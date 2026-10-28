import urllib.request
import urllib.error
import json
import uuid
from datetime import datetime, timezone

base_url = "http://127.0.0.1:8000/api"

def login(username, password):
    data = f"username={username}&password={password}&grant_type=password".encode()
    req = urllib.request.Request(f"{base_url}/auth/login", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())["access_token"]

def post_sync(token, events):
    req = urllib.request.Request(f"{base_url}/sync/delta")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, data=json.dumps({"events": events}).encode()) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

bh_token = login("bharati_operator", "bharati_password")
ma_token = login("maitri_operator", "maitri_password")

def make_event(station_id):
    return {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "INVENTORY_CONSUMED",
        "station_id": station_id,
        "payload": {"sku": "MED-KIT-001", "quantity": 1}
    }


# Maitri trying to submit Bharati event
status, res = post_sync(ma_token, [make_event("BHARATI")])
print(f"Maitri submitting BHARATI event: {status}")

# Maitri submitting Maitri event
status, res = post_sync(ma_token, [make_event("MAITRI")])
print(f"Maitri submitting MAITRI event: {status}")

# Maitri submitting DELHI event
status, res = post_sync(ma_token, [make_event("DELHI")])
print(f"Maitri submitting DELHI event: {status}")

