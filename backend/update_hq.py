import sys
import re

# 1. models.py
with open("models.py", "r", encoding="utf-8") as f:
    content = f.read()

# Update CargoShipment
content = content.replace(
    'status = Column(String, default="IN_TRANSIT", nullable=False)',
    'status = Column(String, default="PENDING_APPROVAL", nullable=False)\n    hq_approved = Column(Boolean, default=False, nullable=False)'
)

# Append Directive
directive_model = """
class Directive(Base):
    __tablename__ = "directives"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(String, index=True, nullable=False)
    message = Column(String, nullable=False)
    issued_by = Column(String, nullable=False)
    issued_at = Column(DateTime, default=_utcnow, nullable=False)
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)
"""
if "class Directive" not in content:
    content += directive_model

with open("models.py", "w", encoding="utf-8") as f:
    f.write(content)

# 2. schemas.py
with open("schemas.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'expected_arrival: datetime\n    status: str',
    'expected_arrival: datetime\n    status: str\n    hq_approved: bool'
)

directive_schema = """
class DirectiveCreate(BaseModel):
    station_id: str
    message: str
    issued_by: str

class DirectiveRead(DirectiveCreate):
    id: str
    issued_at: datetime
    acknowledged: bool
    acknowledged_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
"""
if "class DirectiveCreate" not in content:
    content += directive_schema

with open("schemas.py", "w", encoding="utf-8") as f:
    f.write(content)


# 3. crud.py
with open("crud.py", "r", encoding="utf-8") as f:
    content = f.read()

# Modify mark_cargo_arrived
old_mark = """def mark_cargo_arrived(db: Session, shipment_id: str):
    import models
    db_shipment = db.query(models.CargoShipment).filter(models.CargoShipment.id == shipment_id).first()
    if not db_shipment:
        raise ValueError(f"CargoShipment with id {shipment_id} not found")
    
    db_shipment.status = "ARRIVED"
    db_shipment.arrived_at = datetime.now(timezone.utc)
    
    unmatched = []
    # parse manifest which is a list of dicts
    manifest = db_shipment.manifest
    for item in manifest:
        sku = item.get("sku")
        qty = item.get("quantity")
        inv_item = db.query(models.InventoryItem).filter(
            models.InventoryItem.station_id == db_shipment.station_id,
            models.InventoryItem.sku == sku
        ).first()
        if inv_item:
            apply_inventory_delta(db, inv_item.id, float(qty))
        else:
            unmatched.append(sku)
            
    db.commit()
    db.refresh(db_shipment)
    return db_shipment, unmatched"""

new_mark = """def mark_cargo_arrived(db: Session, shipment_id: str):
    import models
    db_shipment = db.query(models.CargoShipment).filter(models.CargoShipment.id == shipment_id).first()
    if not db_shipment:
        raise ValueError(f"CargoShipment with id {shipment_id} not found")
    
    if not db_shipment.hq_approved:
        return db_shipment, [], "Cannot mark arrived: shipment requires HQ approval first."
        
    db_shipment.status = "ARRIVED"
    db_shipment.arrived_at = datetime.now(timezone.utc)
    
    unmatched = []
    # parse manifest which is a list of dicts
    manifest = db_shipment.manifest
    for item in manifest:
        sku = item.get("sku")
        qty = item.get("quantity")
        inv_item = db.query(models.InventoryItem).filter(
            models.InventoryItem.station_id == db_shipment.station_id,
            models.InventoryItem.sku == sku
        ).first()
        if inv_item:
            apply_inventory_delta(db, inv_item.id, float(qty))
        else:
            unmatched.append(sku)
            
    db.commit()
    db.refresh(db_shipment)
    return db_shipment, unmatched, None"""
content = content.replace(old_mark, new_mark)

crud_additions = """
def approve_cargo_shipment(db: Session, shipment_id: str):
    import models
    db_shipment = db.query(models.CargoShipment).filter(models.CargoShipment.id == shipment_id).first()
    if db_shipment:
        db_shipment.hq_approved = True
        db_shipment.status = "IN_TRANSIT"
        db.commit()
        db.refresh(db_shipment)
    return db_shipment

from models import Directive
def create_directive(db: Session, directive):
    db_dir = Directive(**directive.model_dump())
    db.add(db_dir)
    db.commit()
    db.refresh(db_dir)
    return db_dir

def get_directives(db: Session, station_id: Optional[str] = None):
    query = db.query(Directive)
    if station_id:
        query = query.filter(Directive.station_id == station_id)
    return query.order_by(Directive.issued_at.desc()).all()

def acknowledge_directive(db: Session, directive_id: str):
    from datetime import datetime, timezone
    db_dir = db.query(Directive).filter(Directive.id == directive_id).first()
    if db_dir and not db_dir.acknowledged:
        db_dir.acknowledged = True
        db_dir.acknowledged_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_dir)
    return db_dir
"""
if "approve_cargo_shipment" not in content:
    content += crud_additions

with open("crud.py", "w", encoding="utf-8") as f:
    f.write(content)

# 4. main.py
with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

old_main_mark = """@app.post("/api/cargo/{shipment_id}/mark-arrived")
def mark_cargo_arrived(
    shipment_id: str,
    db: Session = Depends(get_db),
):
    import schemas
    try:
        db_shipment, unmatched = crud.mark_cargo_arrived(db, shipment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {
        "shipment": schemas.CargoShipmentRead.model_validate(db_shipment).model_dump(mode="json"),
        "unmatched_skus": unmatched,
        "warning": f"Some SKUs were unmatched: {unmatched}" if unmatched else None
    }"""

new_main_mark = """@app.post("/api/cargo/{shipment_id}/mark-arrived")
def mark_cargo_arrived(
    shipment_id: str,
    db: Session = Depends(get_db),
):
    import schemas
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
    }"""
content = content.replace(old_main_mark, new_main_mark)

main_additions = """
@app.get("/api/station-status")
def get_station_status(
    station_id: str,
    db: Session = Depends(get_db),
):
    import models
    from datetime import datetime, timezone, timedelta
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
):
    import models
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
):
    import schemas
    d_obj = schemas.DirectiveCreate(**directive)
    db_dir = crud.create_directive(db, d_obj)
    return schemas.DirectiveRead.model_validate(db_dir).model_dump(mode="json")

@app.get("/api/directives")
def get_directives(
    station_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    import schemas
    dirs = crud.get_directives(db, station_id=station_id)
    return [schemas.DirectiveRead.model_validate(d).model_dump(mode="json") for d in dirs]
"""
if "/api/station-status" not in content:
    content += main_additions

with open("main.py", "w", encoding="utf-8") as f:
    f.write(content)

# 5. sync_engine.py
with open("sync_engine.py", "r", encoding="utf-8") as f:
    content = f.read()

sync_addition = """
def _handle_directive_acknowledged(db: Session, payload: dict) -> None:
    _require_keys(payload, ["directive_id"])
    crud.acknowledge_directive(db, payload["directive_id"])
"""
if "DIRECTIVE_ACKNOWLEDGED" not in content:
    content = content.replace(
        'def _handle_expedition_cancelled(db: Session, payload: dict) -> None:',
        sync_addition + '\ndef _handle_expedition_cancelled(db: Session, payload: dict) -> None:'
    )
    content = content.replace(
        '"EXPEDITION_CANCELLED": _handle_expedition_cancelled,',
        '"EXPEDITION_CANCELLED": _handle_expedition_cancelled,\n    "DIRECTIVE_ACKNOWLEDGED": _handle_directive_acknowledged,'
    )

with open("sync_engine.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Backend update complete.")
