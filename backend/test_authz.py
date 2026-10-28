from database import SessionLocal
import models
from permissions import authorize_sync_event
from schemas import SyncEventIn
import uuid
import datetime

db = SessionLocal()
current_user = db.query(models.User).filter(models.User.username == 'maitri_logistics').first()

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
payload = {
    "id": str(uuid.uuid4()),
    "station_id": "MAITRI",
    "carrier_name": "Test Carrier",
    "origin": "Goa",
    "departure_date": now,
    "expected_arrival": now,
    "manifest": [{"sku": "food-101", "name": "Ration", "quantity": 100, "unit": "kg"}],
    "status": "PENDING_APPROVAL",
    "hq_approved": False,
    "created_at": now
}

event = SyncEventIn(
    id=str(uuid.uuid4()),
    event_type="CARGO_CREATED",
    station_id="MAITRI",
    timestamp=datetime.datetime.now(datetime.timezone.utc),
    payload=payload
)

try:
    authorize_sync_event(event, current_user)
    print("Authorization successful")
except Exception as e:
    import traceback
    traceback.print_exc()
