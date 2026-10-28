"""
schemas.py — Pydantic v2 request/response schemas for the Polar Logistics API.

These schemas serve as the serialisation boundary between the FastAPI routes and
the SQLAlchemy ORM models.  They enforce field-level validation (e.g. allowed
category values, status enums) so that bad data is rejected before it ever
touches the database or the event ledger.

Convention used throughout:
    *Base   — shared fields common to create and read operations.
    *Create — fields required when creating a new record (no id, no auto-timestamps).
    *Read   — full representation returned to clients, with `from_attributes=True`
              so Pydantic can read directly from ORM model instances.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums (mirrors models.py enums for Pydantic-level validation)
# ---------------------------------------------------------------------------

class CategoryEnum(str, Enum):
    """Allowed inventory categories — validated on inbound requests."""
    FUEL = "Fuel"
    LIFE_SUPPORT = "Life-Support"
    FOOD = "Food"
    SCIENTIFIC = "Scientific"
    MEDICAL = "Medical"


class PersonnelStatusEnum(str, Enum):
    """Personnel location states — validated on inbound requests."""
    INSIDE_BASE = "INSIDE_BASE"
    FIELD_MISSION = "FIELD_MISSION"
    MEDICAL_BAY = "MEDICAL_BAY"


# ---------------------------------------------------------------------------
# Inventory schemas
# ---------------------------------------------------------------------------

class InventoryItemBase(BaseModel):
    """Shared fields for inventory items."""
    station_id: str
    sku: str
    name: str
    category: CategoryEnum
    quantity: float = 0.0
    unit: Optional[str] = None
    minimum_threshold: float = 0.0


class InventoryItemCreate(InventoryItemBase):
    """
    Schema for creating a new inventory item.
    Supports a client-provided id for offline creation.
    """
    id: Optional[str] = None


class InventoryItemRead(InventoryItemBase):
    """Full inventory item representation returned from the API."""
    id: str
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Personnel schemas
# ---------------------------------------------------------------------------

class PersonnelBase(BaseModel):
    """Shared fields for personnel records."""
    station_id: Optional[str] = None
    full_name: str
    role: Optional[str] = None
    blood_type: Optional[str] = None
    status: PersonnelStatusEnum = PersonnelStatusEnum.INSIDE_BASE


class PersonnelCreate(PersonnelBase):
    """
    Schema for registering new personnel at a station.

    `id` and `last_seen` are server-generated.
    """
    pass


class PersonnelRead(PersonnelBase):
    """Full personnel representation returned from the API."""
    id: str
    last_seen: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# FieldMission schemas
# ---------------------------------------------------------------------------

class FieldMissionBase(BaseModel):
    """Shared fields for field missions."""
    station_id: Optional[str] = None
    team_lead: str
    members: List[str] = Field(default_factory=list)
    purpose: Optional[str] = None
    destination_coords: Optional[str] = None
    vhf_channel: Optional[str] = None
    departure_time: Optional[datetime] = None
    expected_return: Optional[datetime] = None
    is_active: bool = True


class FieldMissionCreate(FieldMissionBase):
    """
    Schema for creating a new field mission.

    `id` can be client-generated or omitted for server-generated.
    """
    id: Optional[str] = None


class FieldMissionRead(FieldMissionBase):
    """Full field-mission representation returned from the API."""
    id: str

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Sync / Event-sourcing schemas
# ---------------------------------------------------------------------------

class SyncEventIn(BaseModel):
    """
    A single event arriving from a client's offline outbox.

    `id` here is the *client_event_id* — the idempotency key generated on the
    client device.  If the server has already persisted an event with this id,
    the duplicate is rejected (reported in `rejected_ids`) rather than replayed,
    which is essential when a station reconnects after weeks on a flaky sat-link
    and retransmits its entire outbox.

    `event_type` values include:
        ASSET_DELTA, FIELD_CHECKOUT, FIELD_CHECKIN,
        PERSONNEL_STATUS_CHANGE, MUSTER_TRIGGERED, ...

    `payload` is intentionally untyped (dict) because the shape varies by
    event_type; downstream processing (sync_engine.py) will validate it.

    `timestamp` is the *client-side* wall-clock time — which may lag behind
    server time by hours or days due to connectivity gaps.
    """
    id: str = Field(..., description="Client-generated event UUID (idempotency key)")
    event_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    station_id: str
    timestamp: datetime


class SyncDeltaRequest(BaseModel):
    """
    Batch wrapper sent by a client when it flushes its offline outbox.

    Contains one or more SyncEventIn objects that should be processed in order.
    """
    events: List[SyncEventIn]


class SyncDeltaResponse(BaseModel):
    """
    Server response after processing a SyncDeltaRequest.

    `synced_ids` — client_event_ids that were successfully persisted and applied.
    `rejected_ids` — client_event_ids that were skipped (duplicates or failed
                     validation).  The client can safely discard these from its
                     outbox since the server has either already processed them or
                     determined they are invalid.
    """
    status: str
    synced_ids: List[str] = Field(default_factory=list)
    rejected_ids: List[str] = Field(default_factory=list)
    server_time: datetime


class SyncLedgerRead(BaseModel):
    """Full read representation of a persisted SyncLedger row."""
    id: str
    client_event_id: str
    station_id: Optional[str] = None
    event_type: str
    payload: Optional[Dict[str, Any]] = None
    client_timestamp: Optional[datetime] = None
    server_received_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Response schema for the /health endpoint."""
    status: str
    server_time: datetime


# ---------------------------------------------------------------------------
# Sneakernet import
# ---------------------------------------------------------------------------

class SneakernetBundle(BaseModel):
    """
    Represents a JSON file physically carried between stations on a USB drive
    (the "sneakernet" — the original offline data transport).

    The client exports its entire outbox to a JSON file with a SHA-256
    integrity hash.  At the receiving end, the hash is verified before any
    events are processed to guard against file corruption or truncation
    during transport across the Antarctic.

    See ``sync_engine.verify_snapshot_hash()`` for the hashing protocol.
    """
    station_id: str
    exported_at: datetime
    events: List[SyncEventIn]
    hash: str


class ManifestItem(BaseModel):
    sku: str
    name: str
    quantity: float
    unit: str

class CargoShipmentCreate(BaseModel):
    id: Optional[str] = None
    station_id: str
    carrier_name: str
    origin: str
    manifest: List[ManifestItem]
    departure_date: datetime
    expected_arrival: datetime

class CargoShipmentRead(CargoShipmentCreate):
    id: str
    status: str
    arrived_at: Optional[datetime] = None
    created_at: datetime
    hq_approved: bool = False

    model_config = ConfigDict(from_attributes=True)


class PlannedExpeditionCreate(BaseModel):
    id: Optional[str] = None
    station_id: str
    team_lead: str
    members: List[str]
    purpose: str
    destination_coords: str
    vhf_channel: str
    planned_departure: datetime
    planned_return: datetime

class PlannedExpeditionRead(PlannedExpeditionCreate):
    id: str
    status: str
    created_at: datetime
    hq_approved: bool = False
    cancelled_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


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

class UserBase(BaseModel):
    username: str
    role: str
    station_id: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: str
    created_at: datetime
    hq_approved: bool = False
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    station_id: Optional[str] = None
