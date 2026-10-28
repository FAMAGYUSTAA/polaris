"""
main.py — FastAPI application for the Polar Expedition Logistics System.

This is the edge-server process that runs locally at each polar research
station (Bharati, Maitri, Himadri).  It serves the React/Dexie PWA over the
station LAN and provides REST endpoints for:
  • Reading current ground-truth state (inventory, personnel, missions).
  • Health checking (used by the frontend to distinguish "Satellite Linked"
    from "Air-Gapped Mode").
  • Delta-sync ingestion (batch of events from an online client outbox).
  • Sneakernet import (USB-carried JSON bundles with integrity hashing).
  • Seeding baseline data for a fresh station deployment.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

import crud
import sync_engine
from database import Base, engine, get_db, SessionLocal
from fastapi.security import OAuth2PasswordRequestForm
import auth
import schemas
import dependencies
from permissions import Permissions, authorize_sync_event
import crud
import stations
from schemas import (
    FieldMissionRead,
    HealthResponse,
    InventoryItemCreate,
    InventoryItemRead,
    PersonnelCreate,
    PersonnelRead,
    SneakernetBundle,
    SyncDeltaRequest,
    SyncDeltaResponse,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Polar Expedition Logistics System",
    version="0.1.0",
    description=(
        "Offline-first, event-sourced logistics backend for Indian polar "
        "research stations. Runs as a local edge-server at each station."
    ),
)


# ---------------------------------------------------------------------------
# Startup: create tables if they don't already exist
# ---------------------------------------------------------------------------

@app.on_event("startup")
def on_startup() -> None:
    """
    Ensure all ORM tables exist in the SQLite file on first run.

    This means a freshly-deployed station can simply start the server and begin
    operating — no separate ``alembic upgrade`` or migration step is required,
    which is critical when the station may be air-gapped with no way to pull
    migration tooling.
    """
    Base.metadata.create_all(bind=engine)
    
    # Seed Demo Users
    with SessionLocal() as db:
        from schemas import UserCreate
        if not crud.get_user_by_username(db, "hq_operator"):
            crud.create_user(db, UserCreate(username="hq_operator", password="hq_password", role="HQ", is_active=True))
        if not crud.get_user_by_username(db, "bharati_operator"):
            crud.create_user(db, UserCreate(username="bharati_operator", password="bharati_password", role="STATION", station_id="BHARATI", is_active=True))
        if not crud.get_user_by_username(db, "maitri_operator"):
            crud.create_user(db, UserCreate(username="maitri_operator", password="maitri_password", role="STATION", station_id="MAITRI", is_active=True))
        if not crud.get_user_by_username(db, "himadri_operator"):
            crud.create_user(db, UserCreate(username="himadri_operator", password="himadri_password", role="STATION", station_id="HIMADRI", is_active=True))



# ---------------------------------------------------------------------------
# CORS — permissive for local station-LAN development
# ---------------------------------------------------------------------------
# WARNING: allow_origins=["*"] is acceptable ONLY because this server runs on
# an isolated station LAN with no internet exposure.  Before any real
# deployment, restrict this to the known station-LAN origins, e.g.:
#   allow_origins=["http://192.168.1.10:5173", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler that returns a clean JSON error body instead of leaking
    raw stack traces to the client.  Logs the full traceback server-side so
    station operators can diagnose issues from the console.
    """
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error. Check server logs for details.",
            "path": str(request.url.path),
        },
    )


# ---------------------------------------------------------------------------
# Response models (composite schemas specific to route responses)
# ---------------------------------------------------------------------------

class PersonnelStatusResponse(BaseModel):
    """
    Combined response for the personnel overview endpoint.

    Bundles the personnel roster with currently active field missions in a
    single payload so the frontend dashboard can render both the personnel
    table and the mission-tracker map from one API call — important when
    bandwidth is limited to a few kbps over the satellite link.
    """
    personnel: List[PersonnelRead]
    active_missions: List[FieldMissionRead]

    model_config = ConfigDict(from_attributes=True)


class SeedResponse(BaseModel):
    """Response returned by the /api/seed endpoint."""
    message: str
    inventory_count: int = 0
    personnel_count: int = 0


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Lightweight health probe used by the frontend header status bar.

    The React PWA periodically pings this endpoint:
      • If it responds → status bar shows **"Satellite Linked"** (green).
      • If it times out or fails → status bar shows **"Air-Gapped Mode"** (amber)
        and the PWA continues operating against its local Dexie/IndexedDB store.

    Returns the current server UTC time, which the frontend can also use to
    detect clock-skew between the station laptop and the edge-server.
    """
    return HealthResponse(
        status="ONLINE",
        server_time=datetime.now(timezone.utc),
    )


@app.get("/api/inventory", response_model=List[InventoryItemRead])
def list_inventory(
    station_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.get_current_user_optional),
) -> List[InventoryItemRead]:
    """
    Return the current ground-truth inventory for a station (or all stations).

    This is the endpoint a freshly-reconnected station — or a newly-provisioned
    field tablet — calls to pull the authoritative stock levels.  The frontend
    then caches these into Dexie for offline use and only fetches deltas
    afterwards via the sync endpoint.
    """
    if station_id:
        dependencies.enforce_station_access(station_id, current_user)
    items = crud.get_inventory(db, station_id=station_id)
    return [InventoryItemRead.model_validate(item) for item in items]


@app.get("/api/personnel", response_model=PersonnelStatusResponse)
def list_personnel(
    station_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.get_current_user_optional),
) -> PersonnelStatusResponse:
    """
    Return the full personnel roster and active field missions.

    Combined into a single response because the operations dashboard always
    renders both side-by-side: the personnel table (who is where) and the
    mission tracker (which teams are in the field, their VHF channels, and
    expected return times).  A single round-trip matters when latency is
    measured in seconds over the satellite link.
    """
    if station_id:
        dependencies.enforce_station_access(station_id, current_user)
    people = crud.get_personnel(db, station_id=station_id)
    missions = crud.get_active_field_missions(db, station_id=station_id)
    return PersonnelStatusResponse(
        personnel=[PersonnelRead.model_validate(p) for p in people],
        active_missions=[FieldMissionRead.model_validate(m) for m in missions],
    )


@app.post("/api/seed", response_model=SeedResponse)
def seed_station(
    station_id: str = "BHARATI",
    db: Session = Depends(get_db),
) -> SeedResponse:
    """
    Seed baseline inventory and personnel data for a Station.

    Designed to be run once on a fresh deployment to populate the database
    with realistic starting values so the frontend has data to render
    immediately.  **Idempotent**: if data already exists, returns
    early with a descriptive message rather than creating duplicates.
    """
    dependencies.enforce_station_access(station_id, None)

    # ---- Idempotency check ------------------------------------------------
    existing = crud.get_inventory(db, station_id=station_id)
    if existing:
        return SeedResponse(
            message=(
                f"Station {station_id} already seeded ({len(existing)} inventory "
                f"items present). No changes made."
            ),
            inventory_count=0,
            personnel_count=0,
        )

    STATION_ID = station_id


    # ---- Inventory --------------------------------------------------------
    inventory_items = [
        InventoryItemCreate(
            station_id=STATION_ID,
            sku="FUEL-JA1-001",
            name="Jet-A1 Aviation Fuel",
            category="Fuel",
            quantity=50_000.0,
            unit="L",
            minimum_threshold=5_000.0,
        ),
        InventoryItemCreate(
            station_id=STATION_ID,
            sku="MED-KIT-001",
            name="Medical Kits",
            category="Medical",
            quantity=1_200.0,
            unit="units",
            minimum_threshold=100.0,
        ),
        InventoryItemCreate(
            station_id=STATION_ID,
            sku="FOOD-RAT-001",
            name="Rations",
            category="Food",
            quantity=8_000.0,
            unit="units",
            minimum_threshold=500.0,
        ),
        # Oxygen Reserves: Bharati Station maintains ~200 medical/emergency O₂
        # cylinders (Type D, 425 L each).  A typical Antarctic station keeps
        # 150–250 cylinders as safety stock for medical emergencies and
        # habitat pressurisation backup.  Minimum threshold of 30 cylinders
        # ensures at least a week of emergency supply for the full crew.
        InventoryItemCreate(
            station_id=STATION_ID,
            sku="LS-OXY-001",
            name="Oxygen Reserves",
            category="Life-Support",
            quantity=200.0,
            unit="cylinders",
            minimum_threshold=30.0,
        ),
    ]

    for item_schema in inventory_items:
        crud.create_inventory_item(db, item_schema)

    # ---- Personnel --------------------------------------------------------
    personnel_list = [
        PersonnelCreate(
            station_id=STATION_ID,
            full_name="Cmdr. Raghav Menon",
            role="Station Commander",
            blood_type="O+",
            status="INSIDE_BASE",
        ),
        PersonnelCreate(
            station_id=STATION_ID,
            full_name="Dr. Priya Sharma",
            role="Chief Medical Officer",
            blood_type="A+",
            status="INSIDE_BASE",
        ),
        PersonnelCreate(
            station_id=STATION_ID,
            full_name="Dr. Arvind Patel",
            role="Glaciologist",
            blood_type="B+",
            status="INSIDE_BASE",
        ),
        PersonnelCreate(
            station_id=STATION_ID,
            full_name="Sneha Iyer",
            role="Communications Engineer",
            blood_type="AB-",
            status="INSIDE_BASE",
        ),
    ]

    for person_schema in personnel_list:
        crud.create_personnel(db, person_schema)

    return SeedResponse(
        message=f"{station_id} Station seeded successfully.",
        inventory_count=len(inventory_items),
        personnel_count=len(personnel_list),
    )



# ---------------------------------------------------------------------------
# Sync endpoints
# ---------------------------------------------------------------------------

@app.post("/api/sync/delta", response_model=SyncDeltaResponse)
def sync_delta(
    request: SyncDeltaRequest,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_station_user())
) -> SyncDeltaResponse:
    for event in request.events:
        if event.station_id != current_user.station_id:
            raise HTTPException(status_code=403, detail=f"Unauthorized station_id: {event.station_id}")

    """
    Ingest a batch of events from a client's offline outbox.

    This is the primary synchronisation pathway.  When a station's PWA
    regains connectivity (satellite link comes up, or the user walks back
    into LAN range), it flushes its Dexie outbox as a ``SyncDeltaRequest``
    containing every locally-queued event.

    Events are processed **sequentially in the order received** (which should
    be chronological, since the client orders its outbox by creation time).
    Each event is independently committed or rejected — one bad event does
    not block or roll back the rest of the batch.

    Duplicates (events whose ``client_event_id`` is already in the ledger)
    are treated as synced — the data is safely server-side — so the client
    can purge them from its outbox.
    """
    synced_ids: list[str] = []
    rejected_ids: list[str] = []

    for event in request.events:
        try:
            authorize_sync_event(event, current_user)
        except Exception as e:
            rejected_ids.append(event.id)
            continue
            
        result = sync_engine.process_event(db, event)
        # Bucketing rule (each event_id lands in exactly ONE list):
        #   APPLIED          -> synced_ids   (freshly written to ledger)
        #   DUPLICATE_SKIPPED -> synced_ids  (already in ledger; safe to purge from client outbox)
        #   REJECTED         -> rejected_ids (bad payload / unknown type; needs client-side review)
        if result["status"] in ("APPLIED", "DUPLICATE_SKIPPED"):
            synced_ids.append(result["id"])
        else:
            rejected_ids.append(result["id"])

    return SyncDeltaResponse(
        status="OK",
        synced_ids=synced_ids,
        rejected_ids=rejected_ids,
        server_time=datetime.now(timezone.utc),
    )


@app.post("/api/sync/sneakernet-import", response_model=SyncDeltaResponse)
async def sneakernet_import(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.get_current_user)
) -> SyncDeltaResponse:
    """
    Import a JSON bundle physically transported between stations on USB.

    The "sneakernet" is the ultimate offline fallback: when satellite is down
    for weeks and there's no network path at all, a station operator can
    export the local outbox to a JSON file on a USB stick, hand-carry it to
    another station or to a supply ship with connectivity, and upload it here.

    **Integrity verification** is mandatory.  The bundle includes a SHA-256
    hash computed by the exporting client.  If the hash doesn't match (file
    was corrupted or truncated during transport), the entire import is
    rejected with HTTP 400 — we never process partially-corrupt data.

    If the hash is valid, every event in the bundle is processed through the
    same ``sync_engine.process_event`` pipeline as the delta endpoint,
    including idempotency checks, so re-importing the same USB file is safe.
    """
    # ---- Integrity check --------------------------------------------------
    # FIX: We must hash the raw incoming JSON dict exactly as received, before
    # Pydantic parses and re-serializes datetimes. Frontend and backend must
    # agree on the exact string serialization (like 'Z' vs '+00:00' or microsecond padding)
    # for hashing to work. This fragile coupling is preserved by hashing the raw body dict.
    raw_body = await request.json()
    if not sync_engine.verify_snapshot_hash(raw_body):
        raise HTTPException(
            status_code=400,
            detail=(
                "Sneakernet bundle integrity check failed — SHA-256 hash does "
                "not match.  The file may have been corrupted or truncated "
                "during transport.  Please re-export from the originating "
                "station and try again."
            ),
        )

    # Validate against schema AFTER hash passes so we still get field-level validation
    bundle = SneakernetBundle.model_validate(raw_body)

    for event in bundle.events:
        if event.station_id != current_user.station_id:
            raise HTTPException(status_code=403, detail=f"Unauthorized station_id: {event.station_id}")

    # ---- Process events (same logic as delta sync) ------------------------
    synced_ids: list[str] = []
    rejected_ids: list[str] = []


    for event in bundle.events:
        try:
            authorize_sync_event(event, current_user)
        except Exception as e:
            rejected_ids.append(event.id)
            continue
            
        result = sync_engine.process_event(db, event)
        # Same bucketing rule as /api/sync/delta — see comment there.
        if result["status"] in ("APPLIED", "DUPLICATE_SKIPPED"):
            synced_ids.append(result["id"])
        else:
            rejected_ids.append(result["id"])

    return SyncDeltaResponse(
        status="OK",
        synced_ids=synced_ids,
        rejected_ids=rejected_ids,
        server_time=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Cargo Tracking (Online-only)
# ---------------------------------------------------------------------------

@app.get("/api/cargo")
def list_cargo_shipments(
    station_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.get_current_user_optional),
):
    import schemas
    if station_id:
        dependencies.enforce_station_access(station_id, current_user)
    shipments = crud.get_cargo_shipments(db, station_id=station_id)
    return [schemas.CargoShipmentRead.model_validate(s).model_dump(mode="json") for s in shipments]

@app.post("/api/cargo")
def create_cargo_shipment(
    shipment: dict, # Take dict and validate manually to avoid modifying global schemas import at top
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_permission(Permissions.SUPPLY_REQUESTS))
):
    import schemas
    shipment_obj = schemas.CargoShipmentCreate(**shipment)
    dependencies.enforce_station_access(shipment_obj.station_id, current_user)
    db_shipment = crud.create_cargo_shipment(db, shipment_obj)
    return schemas.CargoShipmentRead.model_validate(db_shipment).model_dump(mode="json")

@app.post("/api/cargo/{shipment_id}/mark-arrived")
def mark_cargo_arrived(
    shipment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_permission(Permissions.CARGO_RECEIVE))
):
    import schemas
    # First we need to get the shipment to check its station_id
    shipment = crud.get_cargo_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    dependencies.enforce_station_access(shipment.station_id, current_user)
    
    try:
        db_shipment, unmatched, err = crud.mark_cargo_arrived(db, shipment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    if err:
        return {
            "shipment": schemas.CargoShipmentRead.model_validate(db_shipment).model_dump(mode="json"),
            "unmatched_skus": unmatched,
            "warning": err
        }
        
    return {
        "shipment": schemas.CargoShipmentRead.model_validate(db_shipment).model_dump(mode="json"),
        "unmatched_skus": unmatched,
        "warning": f"Some SKUs were unmatched: {unmatched}" if unmatched else None
    }


@app.get("/api/expeditions")
def get_expeditions(
    station_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.get_current_user_optional),
):
    import schemas
    if station_id:
        dependencies.enforce_station_access(station_id, current_user)
    expeditions = crud.get_planned_expeditions(db, station_id=station_id)
    return [schemas.PlannedExpeditionRead.model_validate(e).model_dump(mode="json") for e in expeditions]


@app.get("/api/station-status")
def get_station_status(
    station_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.get_current_user_optional),
):
    import models
    from datetime import datetime, timezone, timedelta
    dependencies.enforce_station_access(station_id, current_user)
    latest_event = db.query(models.SyncLedger).filter(
        models.SyncLedger.station_id == station_id
    ).order_by(models.SyncLedger.server_received_at.desc()).first()

    if not latest_event:
        return {"station_id": station_id, "last_sync_at": None, "is_stale": True}
    
    last_sync_at = latest_event.server_received_at
    # 24 hours is a configurable arbitrary threshold
    is_stale = datetime.now(timezone.utc) - last_sync_at > timedelta(hours=24)
    return {"station_id": station_id, "last_sync_at": last_sync_at.isoformat(), "is_stale": is_stale}

@app.post("/api/cargo/{shipment_id}/approve")
def approve_cargo_shipment(
    shipment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_hq_user())
):
    import schemas
    db_shipment = crud.approve_cargo_shipment(db, shipment_id)
    if not db_shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return schemas.CargoShipmentRead.model_validate(db_shipment).model_dump(mode="json")

@app.get("/api/muster-events")
def get_muster_events(
    station_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.get_current_user_optional),
):
    import models
    dependencies.enforce_station_access(station_id, current_user)
    events = db.query(models.SyncLedger).filter(
        models.SyncLedger.station_id == station_id,
        models.SyncLedger.event_type == "MUSTER_TRIGGERED"
    ).order_by(models.SyncLedger.client_timestamp.desc()).all()
    
    return [
        {
            "event_id": e.client_event_id,
            "triggered_at": e.client_timestamp.isoformat() if e.client_timestamp else None,
            "payload": e.payload
        }
        for e in events
    ]

@app.post("/api/directives")
def create_directive(
    directive: dict,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.require_hq_user())
):
    import schemas
    d_obj = schemas.DirectiveCreate(**directive)
    db_dir = crud.create_directive(db, d_obj)
    return schemas.DirectiveRead.model_validate(db_dir).model_dump(mode="json")

@app.get("/api/directives")
def get_directives(
    station_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(dependencies.get_current_user_optional),
):
    import schemas
    if station_id:
        dependencies.enforce_station_access(station_id, current_user)
    dirs = crud.get_directives(db, station_id=station_id)
    return [schemas.DirectiveRead.model_validate(d).model_dump(mode="json") for d in dirs]

@app.post("/api/auth/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Verify requested station matches the user's station
    requested_station = form_data.client_id
    if user.role != "HQ" and requested_station and user.station_id != requested_station:
        raise HTTPException(
            status_code=403,
            detail=f"User {user.username} is not authorized for station {requested_station}",
        )
        
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role, "station_id": user.station_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

