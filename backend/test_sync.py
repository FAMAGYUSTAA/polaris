import urllib.request
import urllib.parse
import json
import uuid
import datetime

# 1. Login
login_data = urllib.parse.urlencode({
    "username": "maitri_logistics",
    "password": "maitri_password"
}).encode("utf-8")

req = urllib.request.Request("http://localhost:8000/api/auth/login", data=login_data)
try:
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read())
        token = res["access_token"]
except urllib.error.HTTPError as e:
    print("Login failed", e.code, e.read())
    exit(1)

# 2. Sync
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

event_id = str(uuid.uuid4())
sync_data = json.dumps({
    "events": [
        {
            "id": event_id,
            "event_type": "CARGO_CREATED",
            "station_id": "MAITRI",
            "timestamp": now,
            "payload": payload
        }
    ]
}).encode("utf-8")

req2 = urllib.request.Request("http://localhost:8000/api/sync/delta", data=sync_data, headers={
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
})
try:
    with urllib.request.urlopen(req2) as response:
        print(response.getcode())
        print(json.loads(response.read()))
except urllib.error.HTTPError as e:
    print("Sync failed", e.code, e.read())
