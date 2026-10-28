from main import sync_delta, create_cargo_shipment, get_db
import crud
from database import get_db, SessionLocal
from schemas import SyncDeltaRequest, SyncEventIn, CargoShipmentCreate, UserCreate
import uuid
import permissions

db = SessionLocal()

# Setup users
users = [
    {"username": "hq_test", "role": "HQ", "station_id": None},
    {"username": "sl_test", "role": "STATION_LEADER", "station_id": "BHARATI"},
    {"username": "leo_test", "role": "LOGISTICS_ENGINEERING_OFFICER", "station_id": "BHARATI"},
    {"username": "cs_test", "role": "CHIEF_SCIENTIST", "station_id": "BHARATI"},
    {"username": "mo_test", "role": "MEDICAL_OFFICER", "station_id": "BHARATI"},
    {"username": "ftm_test", "role": "FIELD_TEAM_MEMBER", "station_id": "BHARATI"},
    {"username": "sl_maitri", "role": "STATION_LEADER", "station_id": "MAITRI"},
]

for u in users:
    existing = crud.get_user_by_username(db, u["username"])
    if not existing:
        crud.create_user(db, UserCreate(username=u["username"], password="123", role=u["role"], station_id=u["station_id"], is_active=True))

user_objs = {}
for u in users:
    existing = crud.get_user_by_username(db, u["username"])
    user_objs[u["role"]] = existing

print("Testing direct function calls...")

def test_sync(role, event_type, payload):
    evt = SyncEventIn(
        id=str(uuid.uuid4()),
        station_id=user_objs[role].station_id or "BHARATI",
        event_type=event_type,
        timestamp="2026-09-01T10:00:00Z",
        payload=payload
    )
    req = SyncDeltaRequest(events=[evt])
    res = sync_delta(request=req, db=db, current_user=user_objs[role])
    return res

res = test_sync("STATION_LEADER", "MUSTER_TRIGGERED", {"reason": "Test"})
if len(res.synced_ids) != 1: print(res.rejected_ids); assert False

exp_payload = {
    "station_id": "BHARATI",
    "team_lead": "Dr",
    "purpose": "Test",
    "destination_coords": "1",
    "vhf_channel": "1",
    "planned_departure": "2026-09-01T10:00:00Z",
    "planned_return": "2026-09-01T10:00:00Z",
    "members": []
}
res = test_sync("CHIEF_SCIENTIST", "EXPEDITION_PLANNED", exp_payload)
if len(res.synced_ids) != 1: print(res.rejected_ids); assert False

res = test_sync("CHIEF_SCIENTIST", "EXPEDITION_CANCELLED", {"expedition_id": "123", "reason": "Test"})
assert len(res.rejected_ids) == 1

res = test_sync("MEDICAL_OFFICER", "PERSONNEL_STATUS_CHANGE", {"personnel_id": str(user_objs["STATION_LEADER"].id), "new_status": "MEDICAL_BAY"})
if len(res.synced_ids) != 1: print(res.rejected_ids); assert False

res = test_sync("MEDICAL_OFFICER", "EXPEDITION_PLANNED", exp_payload)
assert len(res.rejected_ids) == 1

res = test_sync("FIELD_TEAM_MEMBER", "FIELD_CHECKOUT", {"personnel_ids": [user_objs["FIELD_TEAM_MEMBER"].id], "team_lead": "Me", "members": []})
if len(res.synced_ids) != 1: print(res.rejected_ids); assert False

res = test_sync("FIELD_TEAM_MEMBER", "FIELD_CHECKOUT", {"personnel_ids": [user_objs["STATION_LEADER"].id], "team_lead": "Him", "members": []})
assert len(res.rejected_ids) == 1

evt_iso = SyncEventIn(id=str(uuid.uuid4()), station_id="MAITRI", event_type="MUSTER_TRIGGERED", timestamp="2026-09-01T10:00:00Z", payload={"reason": "Test"})
req_iso = SyncDeltaRequest(events=[evt_iso])
try:
    sync_delta(request=req_iso, db=db, current_user=user_objs["STATION_LEADER"])
    assert False, "Should have thrown 403"
except Exception as e:
    assert getattr(e, "status_code", 0) == 403

evt_idem = SyncEventIn(id=res.synced_ids[0], station_id="BHARATI", event_type="FIELD_CHECKOUT", timestamp="2026-09-01T10:00:00Z", payload={"personnel_ids": [user_objs["FIELD_TEAM_MEMBER"].id], "team_lead": "Me", "members": []})
req_idem = SyncDeltaRequest(events=[evt_idem])
res_idem = sync_delta(request=req_idem, db=db, current_user=user_objs["FIELD_TEAM_MEMBER"])
assert len(res_idem.synced_ids) == 1 # DUPLICATE_SKIPPED

print("All tests passed!")
