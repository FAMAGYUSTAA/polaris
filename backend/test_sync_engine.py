import traceback
from sqlalchemy.orm import Session
from database import SessionLocal
import sync_engine
from schemas import SyncEventIn
import uuid
import datetime

db = SessionLocal()

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
    result = sync_engine.process_event(db, event)
    print(result)
except Exception as e:
    traceback.print_exc()
