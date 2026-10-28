import urllib.request
import urllib.error
import json
import uuid
import sys
from datetime import datetime, timedelta, timezone

base_url = "http://127.0.0.1:8000/api"

def request_json(endpoint, data=None, method="POST"):
    req = urllib.request.Request(
        f"{base_url}{endpoint}",
        data=json.dumps(data).encode('utf-8') if data else None,
        headers={"Content-Type": "application/json"} if data else {},
        method=method
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())

def pjson(data):
    print(json.dumps(data, indent=2))

print("=== 1. Freshness Indicator ===")
print("Checking status before sync:")
status_before = request_json("/station-status?station_id=BHARATI", method="GET")
pjson(status_before)

print("\nCreating a dummy sync event (to update freshness):")
sync_res = request_json("/sync/delta", {
    "events": [{
        "id": str(uuid.uuid4()),
        "station_id": "BHARATI",
        "event_type": "MUSTER_TRIGGERED",
        "payload": {"reason": "Test freshness"},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }]
})
pjson(sync_res)

print("Checking status after sync:")
status_after = request_json("/station-status?station_id=BHARATI", method="GET")
pjson(status_after)
