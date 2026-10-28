import urllib.request
import urllib.error
import json
import uuid
import sys
from datetime import datetime, timedelta, timezone

base_url = "http://127.0.0.1:8000/api"

# Helper to send POST requests
def post_json(endpoint, data):
    req = urllib.request.Request(
        f"{base_url}{endpoint}",
        data=json.dumps(data).encode('utf-8'),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error ({e.code}): {e.read().decode()}")
        sys.exit(1)

# Helper to fetch expeditions
def get_expeditions():
    req = urllib.request.Request(f"{base_url}/expeditions?station_id=BHARATI")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def pjson(data):
    print(json.dumps(data, indent=2))

print("=== Starting Planned Expedition Sync Tests ===\n")

client_generated_id = str(uuid.uuid4())
event_id_create = str(uuid.uuid4())

now = datetime.now(timezone.utc)
planned_dep = (now + timedelta(days=2)).isoformat()
planned_ret = (now + timedelta(days=5)).isoformat()

# 1. POST EXPEDITION_PLANNED
print(f"1. Testing EXPEDITION_PLANNED (UUID: {client_generated_id})")
payload_create = {
    "events": [
        {
            "id": event_id_create,
            "station_id": "BHARATI",
            "event_type": "EXPEDITION_PLANNED",
            "payload": {
                "id": client_generated_id,
                "station_id": "BHARATI",
                "team_lead": "Dr. Sarah Chen",
                "members": ["Jane Doe", "John Smith"],
                "purpose": "Ice core drilling",
                "destination_coords": "-69.41, 76.19",
                "vhf_channel": "CH16",
                "planned_departure": planned_dep,
                "planned_return": planned_ret
            },
            "timestamp": "2026-09-06T00:00:00Z"
        }
    ]
}
resp_create = post_json("/sync/delta", payload_create)
print("Response:")
pjson(resp_create)

exps = get_expeditions()
item = next((e for e in exps if e["id"] == client_generated_id), None)
print(f"Expedition check: Found? {'Yes' if item else 'No'}.")

# 2. Resend exact same EXPEDITION_PLANNED
print(f"\n2. Testing EXPEDITION_PLANNED Idempotency (Event ID: {event_id_create})")
resp_create_dup = post_json("/sync/delta", payload_create)
print("Response:")
pjson(resp_create_dup)
exps = get_expeditions()
count = len([e for e in exps if e["id"] == client_generated_id])
print(f"Count of this expedition in returned list: {count}")

# 3. POST EXPEDITION_CANCELLED
print(f"\n3. Testing EXPEDITION_CANCELLED (Expedition UUID: {client_generated_id})")
event_id_cancel = str(uuid.uuid4())
payload_cancel = {
    "events": [
        {
            "id": event_id_cancel,
            "station_id": "BHARATI",
            "event_type": "EXPEDITION_CANCELLED",
            "payload": {
                "expedition_id": client_generated_id
            },
            "timestamp": "2026-09-06T00:00:01Z"
        }
    ]
}
resp_cancel = post_json("/sync/delta", payload_cancel)
print("Response:")
pjson(resp_cancel)

exps = get_expeditions()
item_after = next((e for e in exps if e["id"] == client_generated_id), None)
print(f"Expedition check after cancel: Found? {'Yes' if item_after else 'No'}")

# 4. Resend same EXPEDITION_CANCELLED
print(f"\n4. Testing EXPEDITION_CANCELLED Idempotency (Event ID: {event_id_cancel})")
resp_cancel_dup = post_json("/sync/delta", payload_cancel)
print("Response:")
pjson(resp_cancel_dup)
