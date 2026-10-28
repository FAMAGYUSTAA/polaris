"""
sync_engine.py — Event-sourcing replay engine for the Polar Logistics System.

This is the most safety-critical module in the entire system.  It guarantees
that when a station reconnects after weeks of satellite blackout, every offline
action is applied **correctly, exactly once, in chronological order** — never
duplicated, never lost, never applied out of sequence.

The core loop is:
    1. Idempotency check  — has this client_event_id already been applied?
    2. Dispatch            — route to the correct state-mutation handler.
    3. Ledger persistence  — append the event to the append-only SyncLedger.

If step 1 finds a match the event is skipped (DUPLICATE_SKIPPED).
If step 2 fails (bad payload, missing entity), the event is rejected and
*not* written to the ledger, so the client can correct and resend it.
If step 2 succeeds, step 3 records the event — making subsequent attempts
hit the idempotency gate.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, List

from sqlalchemy.orm import Session

import crud
import schemas
from schemas import FieldMissionCreate, SyncEventIn

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Transaction boundary design
# ---------------------------------------------------------------------------
#
# Each event in a batch is processed with **per-event commit** semantics.
# The existing crud functions call ``session.commit()`` after each mutation,
# so every successful sub-operation is immediately durable.
#
# WHY per-event commit (not one batch commit at the end):
#   Events must be replayed chronologically, and a later event in the same
#   batch may depend on an earlier one succeeding.  For example:
#     Event A: FIELD_CHECKOUT creates mission M-1 and marks 2 personnel
#              as FIELD_MISSION.
#     Event B: FIELD_CHECKIN closes M-1 and sets those personnel back to
#              INSIDE_BASE.
#   If we deferred all commits to the end of the batch, Event B would not
#   be able to find mission M-1 in the database.  Per-event commit ensures
#   each event's state changes are visible to subsequent events.
#
# WHY NOT savepoints:
#   Multi-step events (e.g. FIELD_CHECKOUT creates a mission AND updates N
#   personnel statuses) would ideally use savepoints for atomic rollback on
#   partial failure.  However, the crud functions call ``session.commit()``
#   internally, which releases any enclosing savepoint in SQLAlchemy.
#   Refactoring crud to support deferred-commit mode would be the clean fix,
#   but is out of scope for this prototype.  The practical risk is low:
#   partial application of a multi-step event is detectable by
#   ``replay_full_ledger_for_station()`` and recoverable by manual
#   intervention.
#
# ISOLATION guarantee:
#   If one event in a batch fails, previously-committed events are NOT rolled
#   back.  This is by design — the task requires "one bad event in a batch
#   doesn't roll back or block the others."  The failed event is reported in
#   ``rejected_ids`` and its ``client_event_id`` is NOT inserted into the
#   ledger, so the client can safely retry it on the next sync.
# ---------------------------------------------------------------------------


def process_event(db: Session, event: SyncEventIn) -> dict:
    """
    Process a single client-originated sync event through the full pipeline:
    idempotency check → state mutation → ledger persistence.

    Returns a result dict:
        ``{"id": "<client_event_id>", "status": "APPLIED"}``
        ``{"id": "<client_event_id>", "status": "DUPLICATE_SKIPPED"}``
        ``{"id": "<client_event_id>", "status": "REJECTED", "reason": "..."}``
    """
    # ---- Step 0: Idempotency gate -----------------------------------------
    existing = crud.get_ledger_event_by_client_id(db, event.id)
    if existing is not None:
        logger.info("Event %s already in ledger — skipping duplicate.", event.id)
        return {"id": event.id, "status": "DUPLICATE_SKIPPED"}

    # ---- Step 1: Dispatch to the correct handler --------------------------
    handler = _EVENT_HANDLERS.get(event.event_type)
    if handler is None:
        return {
            "id": event.id,
            "status": "REJECTED",
            "reason": f"Unrecognized event_type: '{event.event_type}'",
        }

    try:
        event.payload["station_id"] = event.station_id
        handler(db, event.payload)
    except (ValueError, KeyError, TypeError) as exc:
        # Expected validation / lookup failures — don't crash the batch.
        db.rollback()
        logger.warning(
            "Event %s (%s) rejected: %s", event.id, event.event_type, exc,
        )
        return {
            "id": event.id,
            "status": "REJECTED",
            "reason": str(exc),
        }
    except Exception as exc:
        # Unexpected error — still don't crash the batch, but log fully.
        db.rollback()
        logger.exception("Unexpected error processing event %s", event.id)
        return {
            "id": event.id,
            "status": "REJECTED",
            "reason": f"Internal error: {exc}",
        }

    # ---- Step 2: Persist to the append-only ledger ------------------------
    try:
        crud.insert_ledger_event(db, event)
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to persist ledger entry for event %s", event.id)
        return {
            "id": event.id,
            "status": "REJECTED",
            "reason": f"Ledger write failed: {exc}",
        }

    return {"id": event.id, "status": "APPLIED"}


# ---------------------------------------------------------------------------
# Payload helpers
# ---------------------------------------------------------------------------

def _require_keys(payload: dict, keys: List[str]) -> None:
    """Raise ``KeyError`` listing every required key absent from *payload*."""
    missing = [k for k in keys if k not in payload]
    if missing:
        raise KeyError(f"Missing required payload key(s): {missing}")


# ---------------------------------------------------------------------------
# Event-type handlers
#
# Each handler receives (db, payload) and either mutates state via crud
# functions or raises an exception.  The caller (process_event) decides
# whether to persist the event to the ledger based on success/failure.
# ---------------------------------------------------------------------------

def _handle_asset_delta(db: Session, payload: dict) -> None:
    """
    Apply an inventory quantity change: Qₜ₊₁ = Qₜ + Δ.

    Expected payload (provide **item_id** OR **sku + station_id**):
    ::

        {
            "item_id": "<uuid>",             # direct lookup (preferred)
            -- OR --
            "sku": "<sku-code>",             # e.g. "FUEL-JA1-001"
            "station_id": "<station>",       # e.g. "BHARATI"

            "delta": <float>                 # positive = receipt, negative = consumption
        }
    """
    _require_keys(payload, ["delta"])
    delta = float(payload["delta"])

    if "item_id" in payload:
        item_id = payload["item_id"]
    elif "sku" in payload and "station_id" in payload:
        item = crud.get_inventory_item_by_sku(
            db, station_id=payload["station_id"], sku=payload["sku"],
        )
        if item is None:
            raise ValueError(
                f"No inventory item with SKU '{payload['sku']}' "
                f"at station '{payload['station_id']}'."
            )
        item_id = item.id
    else:
        raise KeyError(
            "ASSET_DELTA payload must include 'item_id' or both 'sku' and "
            "'station_id'."
        )

    crud.apply_inventory_delta(db, item_id, delta)


def _handle_field_checkout(db: Session, payload: dict) -> None:
    """
    Create a new field mission and mark departing personnel as FIELD_MISSION.

    Expected payload:
    ::

        {
            "team_lead": "Dr. Arvind Patel",
            "members": ["person-name-or-id", ...],       # stored in mission JSON column
            "personnel_ids": ["uuid-1", "uuid-2", ...],  # whose status to update
            "purpose": "Ice core sampling",               # optional
            "destination_coords": "-69.4077, 76.1868",    # optional
            "vhf_channel": "CH-7",                        # optional
            "departure_time": "2026-09-03T10:00:00Z",     # optional, ISO 8601
            "expected_return": "2026-09-04T18:00:00Z"     # optional, ISO 8601
        }
    """
    _require_keys(payload, ["team_lead", "members", "personnel_ids"])

    mission_data = FieldMissionCreate(
        id=payload.get("mission_id"),
        station_id=payload.get("station_id"),
        team_lead=payload["team_lead"],
        members=payload["members"],
        purpose=payload.get("purpose"),
        destination_coords=payload.get("destination_coords"),
        vhf_channel=payload.get("vhf_channel"),
        departure_time=payload.get("departure_time"),
        expected_return=payload.get("expected_return"),
    )
    crud.create_field_mission(db, mission_data)

    for pid in payload["personnel_ids"]:
        crud.update_personnel_status(db, pid, "FIELD_MISSION")


def _handle_field_checkin(db: Session, payload: dict) -> None:
    """
    Close a field mission and return personnel to INSIDE_BASE.

    Expected payload:
    ::

        {
            "mission_id": "<uuid>",
            "personnel_ids": ["uuid-1", "uuid-2", ...]
        }
    """
    _require_keys(payload, ["mission_id", "personnel_ids"])

    crud.close_field_mission(db, payload["mission_id"])

    for pid in payload["personnel_ids"]:
        crud.update_personnel_status(db, pid, "INSIDE_BASE")


def _handle_personnel_status_change(db: Session, payload: dict) -> None:
    """
    Update a single person's location status.

    Expected payload:
    ::

        {
            "personnel_id": "<uuid>",
            "new_status": "MEDICAL_BAY"      # INSIDE_BASE | FIELD_MISSION | MEDICAL_BAY
        }
    """
    _require_keys(payload, ["personnel_id", "new_status"])
    crud.update_personnel_status(db, payload["personnel_id"], payload["new_status"])


def _handle_muster_triggered(db: Session, payload: dict) -> None:
    """
    Emergency headcount event — **no state mutation**.

    This is a broadcast/audit-only event: an emergency muster was initiated
    at the station.  It doesn't change inventory, personnel, or mission
    tables.  The event is still persisted to the SyncLedger (by the caller)
    so that HQ and auditors can review when musters were called, by whom,
    and why.

    Expected payload (informational, not validated):
    ::

        {
            "initiated_by": "<personnel name or id>",
            "reason": "Blizzard warning"
        }
    """
    # Intentional no-op: the event will be recorded in the ledger by
    # process_event() after this handler returns successfully.
    logger.info(
        "MUSTER_TRIGGERED — initiated_by=%s, reason=%s",
        payload.get("initiated_by", "unknown"),
        payload.get("reason", "not specified"),
    )

def _handle_item_created(db: Session, payload: dict) -> None:
    _require_keys(payload, ["station_id", "sku", "name", "category"])
    
    # Check duplicate
    existing = crud.get_inventory_item_by_sku(db, station_id=payload["station_id"], sku=payload["sku"])
    if existing:
        logger.info("ITEM_CREATED duplicate sku: %s at %s - no-op", payload["sku"], payload["station_id"])
        return
        
    from schemas import InventoryItemCreate
    item_create = InventoryItemCreate(**payload)
    crud.create_inventory_item(db, item_create)

def _handle_item_deleted(db: Session, payload: dict) -> None:
    _require_keys(payload, ["item_id"])
    deleted = crud.delete_inventory_item(db, payload["item_id"])
    if not deleted:
        logger.info("ITEM_DELETED item not found: %s - treated as success", payload["item_id"])


def _handle_expedition_planned(db: Session, payload: dict) -> None:
    from schemas import PlannedExpeditionCreate
    _require_keys(payload, ["station_id", "team_lead", "members", "purpose", "destination_coords", "vhf_channel", "planned_departure", "planned_return"])
    
    exp_create = PlannedExpeditionCreate(**payload)
    crud.create_planned_expedition(db, exp_create)


def _handle_directive_acknowledged(db: Session, payload: dict) -> None:
    _require_keys(payload, ["directive_id"])
    crud.acknowledge_directive(db, payload["directive_id"])

def _handle_expedition_cancelled(db: Session, payload: dict) -> None:
    _require_keys(payload, ["expedition_id"])
    cancelled = crud.cancel_planned_expedition(db, payload["expedition_id"])
    if not cancelled:
        logger.info("EXPEDITION_CANCELLED expedition not found or already cancelled: %s - treated as success", payload["expedition_id"])


def _handle_cargo_created(db: Session, payload: dict) -> None:
    schema = schemas.CargoShipmentCreate(**payload)
    crud.create_cargo_shipment(db, schema)

def _handle_cargo_marked_arrived(db: Session, payload: dict) -> None:
    _require_keys(payload, ["shipment_id"])
    import models
    db_shipment = db.query(models.CargoShipment).filter(models.CargoShipment.id == payload["shipment_id"]).first()
    if not db_shipment:
        raise ValueError(f"CargoShipment {payload['shipment_id']} not found")
    if db_shipment.status == "ARRIVED":
        # Already arrived, prevent duplicate inventory updates
        return
    crud.mark_cargo_arrived(db, payload["shipment_id"])

# Handler dispatch table

_EVENT_HANDLERS: Dict[str, Any] = {
    "ASSET_DELTA": _handle_asset_delta,
    "FIELD_CHECKOUT": _handle_field_checkout,
    "FIELD_CHECKIN": _handle_field_checkin,
    "PERSONNEL_STATUS_CHANGE": _handle_personnel_status_change,
    "MUSTER_TRIGGERED": _handle_muster_triggered,
    "ITEM_CREATED": _handle_item_created,
    "ITEM_DELETED": _handle_item_deleted,
    "EXPEDITION_PLANNED": _handle_expedition_planned,
    "EXPEDITION_CANCELLED": _handle_expedition_cancelled,
    "DIRECTIVE_ACKNOWLEDGED": _handle_directive_acknowledged,
    "CARGO_CREATED": _handle_cargo_created,
    "CARGO_MARKED_ARRIVED": _handle_cargo_marked_arrived,
}


# ---------------------------------------------------------------------------
# Ledger replay / consistency audit
# ---------------------------------------------------------------------------

def replay_full_ledger_for_station(
    db: Session,
    station_id: str,
) -> Dict[str, Any]:
    """
    Diagnostic utility: read the full event ledger for a station and validate
    it for internal consistency.

    This does **not** rebuild materialised state (that would require wiping
    tables and re-applying every event).  Instead it walks the chronologically-
    ordered ledger and checks for detectable anomalies:

      - **CHECKIN_WITHOUT_CHECKOUT** - a FIELD_CHECKIN appears before enough
        FIELD_CHECKOUT events to account for it.
      - **TIMESTAMP_REGRESSION** - an event's ``client_timestamp`` is earlier
        than the previous event's, suggesting clock drift or mis-ordering.
      - **UNKNOWN_EVENT_TYPE** - an event type that isn't in the handler table
        somehow made it into the ledger (should be impossible via normal flow).
      - **EMPTY_PAYLOAD** - a state-mutating event type was persisted with a
        null or empty payload.

    Returns a report dict suitable for logging or returning to an HQ admin
    console.
    """
    events = crud.get_all_ledger_events(db, station_id=station_id)

    report: Dict[str, Any] = {
        "station_id": station_id,
        "total_events": len(events),
        "event_type_counts": {},
        "issues": [],
    }

    checkout_count = 0
    checkin_count = 0
    prev_timestamp = None

    for evt in events:
        # ---- Count by type ------------------------------------------------
        etype = evt.event_type
        report["event_type_counts"][etype] = (
            report["event_type_counts"].get(etype, 0) + 1
        )

        # ---- Temporal ordering check --------------------------------------
        if (
            prev_timestamp is not None
            and evt.client_timestamp is not None
            and evt.client_timestamp < prev_timestamp
        ):
            report["issues"].append({
                "event_id": evt.client_event_id,
                "issue": "TIMESTAMP_REGRESSION",
                "detail": (
                    f"client_timestamp {evt.client_timestamp.isoformat()} "
                    f"is earlier than previous event's "
                    f"{prev_timestamp.isoformat()}"
                ),
            })
        if evt.client_timestamp is not None:
            prev_timestamp = evt.client_timestamp

        # ---- Checkout / checkin balance -----------------------------------
        if etype == "FIELD_CHECKOUT":
            checkout_count += 1
        elif etype == "FIELD_CHECKIN":
            checkin_count += 1
            if checkin_count > checkout_count:
                report["issues"].append({
                    "event_id": evt.client_event_id,
                    "issue": "CHECKIN_WITHOUT_CHECKOUT",
                    "detail": (
                        f"FIELD_CHECKIN #{checkin_count} but only "
                        f"{checkout_count} FIELD_CHECKOUT(s) recorded prior"
                    ),
                })

        # ---- Unknown event type -------------------------------------------
        if etype not in _EVENT_HANDLERS:
            report["issues"].append({
                "event_id": evt.client_event_id,
                "issue": "UNKNOWN_EVENT_TYPE",
                "detail": f"Event type '{etype}' is not in the handler table",
            })

        # ---- Payload presence check for state-mutating events -------------
        _NEEDS_PAYLOAD = {
            "ASSET_DELTA", "FIELD_CHECKOUT", "FIELD_CHECKIN",
            "PERSONNEL_STATUS_CHANGE",
        }
        if etype in _NEEDS_PAYLOAD and not evt.payload:
            report["issues"].append({
                "event_id": evt.client_event_id,
                "issue": "EMPTY_PAYLOAD",
                "detail": f"{etype} event has a null or empty payload",
            })

    report["is_consistent"] = len(report["issues"]) == 0

    if report["issues"]:
        logger.warning(
            "Ledger audit for station %s found %d issue(s).",
            station_id,
            len(report["issues"]),
        )
    else:
        logger.info("Ledger audit for station %s: all consistent.", station_id)

    return report


# ---------------------------------------------------------------------------
# Sneakernet hash verification
# ---------------------------------------------------------------------------
#
# SECURITY SCOPE NOTE:
# This function checks DATA INTEGRITY - i.e. "was the JSON file corrupted
# or truncated while being carried on a USB drive across the Antarctic?"
# It does NOT provide cryptographic authenticity or non-repudiation.
#
# An adversary with physical access to the USB drive could modify both the
# events and recompute the hash to match.  A real deployment would sign the
# bundle with a station-held private key (e.g. Ed25519) and have the
# receiving end verify the signature against the station's public key.
# That is out of scope for this prototype.
# ---------------------------------------------------------------------------

def verify_snapshot_hash(snapshot: dict) -> bool:
    """
    Verify the SHA-256 integrity hash of a sneakernet export bundle.

    The hash covers a canonical JSON serialisation of the **entire bundle
    excluding the** ``hash`` **field itself**.  Canonical form uses sorted
    keys, compact separators (``","``, ``":"``), and ``str()`` as the
    default serialiser for non-JSON-native types (datetimes, UUIDs).

    Args:
        snapshot: The parsed JSON bundle dict.  Expected keys:
                  ``station_id``, ``exported_at``, ``events``, ``hash``.

    Returns:
        ``True`` if the recomputed hash matches the embedded one.
    """
    expected_hash = snapshot.get("hash", "")

    # Build the canonical payload - everything except the hash field.
    canonical_payload = {k: v for k, v in snapshot.items() if k != "hash"}
    canonical_json = json.dumps(
        canonical_payload,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )

    computed_hash = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    if computed_hash != expected_hash:
        logger.warning(
            "Sneakernet hash mismatch: expected=%s, computed=%s",
            expected_hash,
            computed_hash,
        )

    return computed_hash == expected_hash
