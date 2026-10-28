import sys

content = open('sync_engine.py', 'r', encoding='utf-8').read()

# We know the file currently has:
# _EVENT_HANDLERS: Dict[str, Any] = {
#     "ASSET_DELTA": _handle_asset_delta,
# ...
#     "EXPEDITION_CANCELLED": _handle_expedition_cancelled,
# }
#     canonical_json = json.dumps(

# We split at _EVENT_HANDLERS
top_part = content.split('_EVENT_HANDLERS: Dict[str, Any] = {')[0]

new_bottom = """_EVENT_HANDLERS: Dict[str, Any] = {
    "ASSET_DELTA": _handle_asset_delta,
    "FIELD_CHECKOUT": _handle_field_checkout,
    "FIELD_CHECKIN": _handle_field_checkin,
    "PERSONNEL_STATUS_CHANGE": _handle_personnel_status_change,
    "MUSTER_TRIGGERED": _handle_muster_triggered,
    "ITEM_CREATED": _handle_item_created,
    "ITEM_DELETED": _handle_item_deleted,
    "EXPEDITION_PLANNED": _handle_expedition_planned,
    "EXPEDITION_CANCELLED": _handle_expedition_cancelled,
}


# ---------------------------------------------------------------------------
# Ledger replay / consistency audit
# ---------------------------------------------------------------------------

def replay_full_ledger_for_station(
    db: Session,
    station_id: str,
) -> Dict[str, Any]:
    \"\"\"
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
    \"\"\"
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
    \"\"\"
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
    \"\"\"
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
"""

with open('sync_engine.py', 'w', encoding='utf-8') as f:
    f.write(top_part + new_bottom)

print("sync_engine.py restored successfully.")
