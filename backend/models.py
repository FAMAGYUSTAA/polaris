"""
models.py — SQLAlchemy ORM models for the Polar Expedition Logistics system.

These models represent the local, station-side data layer.  Every station
(Bharati / Maitri / Himadri) runs its own SQLite database with the same schema.
Data is synchronised to the central server (and peer stations) via the
event-sourcing mechanism described in SyncLedger; the other tables are
*materialised state* derived from replaying those events.

All primary keys are client-generated UUIDs so that records created while a
station is offline will never collide with records created elsewhere.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy.types import TypeDecorator
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    JSON,
    String,
)

from database import Base


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _generate_uuid() -> str:
    """Return a new UUID4 string suitable for use as a primary key."""
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    """Return the current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)

class AwareDateTime(TypeDecorator):
    """
    A SQLAlchemy TypeDecorator that ensures DateTime objects are timezone-aware.
    SQLite natively strips timezone info on save and returns naive datetimes.
    This intercepts reads/writes and forces timezone.utc.
    """
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CategoryEnum(str, enum.Enum):
    """Allowed inventory categories — kept as a Python enum so that application
    code can validate values even though SQLite stores them as plain strings."""
    FUEL = "Fuel"
    LIFE_SUPPORT = "Life-Support"
    FOOD = "Food"
    SCIENTIFIC = "Scientific"
    MEDICAL = "Medical"


class PersonnelStatus(str, enum.Enum):
    """Tracks a person's current physical location within the station complex."""
    INSIDE_BASE = "INSIDE_BASE"
    FIELD_MISSION = "FIELD_MISSION"
    MEDICAL_BAY = "MEDICAL_BAY"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class InventoryItem(Base):
    """
    Materialised view of the current stock for a single SKU at a station.

    In the event-sourced architecture, every inventory change (receipt,
    consumption, adjustment, transfer) is first recorded as a SyncLedger event.
    This table is then updated by replaying / applying that event — making it
    a projection that can always be rebuilt from the ledger if needed.

    `minimum_threshold` powers the low-stock alerting system: when `quantity`
    drops below this value the PWA will surface a warning, even while offline.
    """
    __tablename__ = "inventory_items"

    id = Column(String, primary_key=True, default=_generate_uuid)
    station_id = Column(String, nullable=False, index=True)
    sku = Column(String, nullable=False)
    name = Column(String, nullable=False)
    category = Column(
        String,
        nullable=False,
        comment="Allowed values: Fuel, Life-Support, Food, Scientific, Medical",
    )
    quantity = Column(Float, nullable=False, default=0.0)
    unit = Column(String, comment='Measurement unit, e.g. "L", "kg", "units"')
    minimum_threshold = Column(Float, default=0.0)
    updated_at = Column(AwareDateTime, default=_utcnow, onupdate=_utcnow)

    # Logical uniqueness: one SKU per station.  Enforced at DB level.
    __table_args__ = (
        Index("ix_inventory_station_sku", "station_id", "sku", unique=True),
    )

    def __repr__(self) -> str:
        return f"<InventoryItem {self.sku} @ {self.station_id} qty={self.quantity}>"


class Personnel(Base):
    """
    Tracks every person currently assigned to a station.

    `status` reflects real-time location so that the base commander can see
    at a glance who is inside the station vs. out on a field mission or in the
    medical bay.  `last_seen` is updated by check-in events (manual or via
    RFID/NFC badges once those are deployed).
    """
    __tablename__ = "personnel"

    id = Column(String, primary_key=True, default=_generate_uuid)
    station_id = Column(String, index=True)
    full_name = Column(String, nullable=False)
    role = Column(String)
    blood_type = Column(String)
    status = Column(String, default=PersonnelStatus.INSIDE_BASE.value)
    last_seen = Column(AwareDateTime, default=_utcnow)

    def __repr__(self) -> str:
        return f"<Personnel {self.full_name} [{self.status}]>"


class FieldMission(Base):
    """
    Represents an active or past field mission (traverse, sampling run, etc.).

    `members` is stored as a JSON list of personnel IDs so that the record
    remains self-contained even when the personnel table has not yet synced.
    `vhf_channel` records the radio channel assigned to the team, which is
    critical safety information displayed on the base operations dashboard.
    """
    __tablename__ = "field_missions"

    id = Column(String, primary_key=True, default=_generate_uuid)
    station_id = Column(String, index=True, nullable=False)
    team_lead = Column(String, primary_key=True, default=_generate_uuid)
    team_lead = Column(String, nullable=False)
    members = Column(JSON, comment="JSON list of personnel names or IDs")
    purpose = Column(String)
    destination_coords = Column(String, comment="Lat/Lon or local grid ref")
    vhf_channel = Column(String)
    departure_time = Column(AwareDateTime)
    expected_return = Column(AwareDateTime)
    is_active = Column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<FieldMission lead={self.team_lead} active={self.is_active}>"


class SyncLedger(Base):
    """
    Append-only event log — the single source of truth in the offline-first
    event-sourcing architecture.

    When a station reconnects after days or weeks offline, it pushes all locally
    queued events to the central server.  `client_event_id` is the idempotency
    key: if the same event arrives twice (e.g. the upload succeeded but the ACK
    was lost over the satellite link), the unique index on this column causes
    the duplicate INSERT to fail harmlessly, preventing double-replay.

    `client_timestamp` preserves *when* the event actually happened at the
    station — which may differ significantly from `server_received_at` due to
    connectivity gaps.  Conflict resolution and ordering logic should use
    `client_timestamp`; `server_received_at` is for audit/debugging only.
    """
    __tablename__ = "sync_ledger"

    id = Column(String, primary_key=True, default=_generate_uuid)
    client_event_id = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        comment="Client-generated UUID — idempotency key to prevent duplicate replay",
    )
    station_id = Column(String, index=True)
    event_type = Column(String, nullable=False)
    payload = Column(JSON)
    client_timestamp = Column(AwareDateTime, comment="Wall-clock time at the originating station")
    server_received_at = Column(AwareDateTime, default=_utcnow)

    def __repr__(self) -> str:
        return f"<SyncLedger {self.event_type} from={self.station_id}>"

class CargoShipment(Base):
    """
    Tracks incoming supply shipments to the polar station.
    Cargo Tracking is online-only in this version; offline sync integration is planned for a future redesign.
    """
    __tablename__ = "cargo_shipments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(String, index=True, nullable=False)
    carrier_name = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    manifest = Column(JSON, nullable=False)
    departure_date = Column(AwareDateTime, nullable=False)
    expected_arrival = Column(AwareDateTime, nullable=False)
    status = Column(String, default="PENDING_APPROVAL", nullable=False)
    hq_approved = Column(Boolean, default=False, nullable=False)
    arrived_at = Column(AwareDateTime, nullable=True)
    created_at = Column(AwareDateTime, default=_utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<CargoShipment {self.carrier_name} to={self.station_id} status={self.status}>"


class PlannedExpedition(Base):
    """
    Future planned expedition scheduling.
    """
    __tablename__ = "planned_expeditions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(String, index=True, nullable=False)
    team_lead = Column(String, nullable=False)
    members = Column(JSON, nullable=False)
    purpose = Column(String, nullable=False)
    destination_coords = Column(String, nullable=False)
    vhf_channel = Column(String, nullable=False)
    planned_departure = Column(AwareDateTime, nullable=False)
    planned_return = Column(AwareDateTime, nullable=False)
    status = Column(String, default="PLANNED", nullable=False)
    created_at = Column(AwareDateTime, default=_utcnow, nullable=False)
    cancelled_at = Column(AwareDateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<PlannedExpedition {self.id} lead={self.team_lead} status={self.status}>"


class Directive(Base):
    __tablename__ = "directives"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    station_id = Column(String, index=True, nullable=False)
    message = Column(String, nullable=False)
    issued_by = Column(String, nullable=False)
    issued_at = Column(AwareDateTime, default=_utcnow, nullable=False)
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_at = Column(AwareDateTime, nullable=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, default=_generate_uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    station_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(AwareDateTime, default=lambda: datetime.now(timezone.utc))
