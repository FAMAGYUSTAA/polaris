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
        "event_type": "ASSET_DELTA",
        "payload": {"item_id": "none", "delta_quantity": 0, "reason": "bump"},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }]
})

print("Checking status after sync:")
status_after = request_json("/station-status?station_id=BHARATI", method="GET")
pjson(status_after)


print("\n=== 2. Cargo Approval Workflow ===")
print("Creating cargo shipment:")
cargo = request_json("/cargo", {
    "station_id": "BHARATI",
    "carrier_name": "Test Carrier",
    "origin": "Cape Town",
    "manifest": [],
    "departure_date": datetime.now(timezone.utc).isoformat(),
    "expected_arrival": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
})
pjson(cargo)
shipment_id = cargo["id"]

print("\nAttempting to mark arrived without approval:")
arrived_fail = request_json(f"/cargo/{shipment_id}/mark-arrived")
pjson(arrived_fail)

print("\nApproving cargo shipment:")
approve_res = request_json(f"/cargo/{shipment_id}/approve")
pjson(approve_res)

print("\nAttempting to mark arrived AFTER approval:")
arrived_success = request_json(f"/cargo/{shipment_id}/mark-arrived")
pjson(arrived_success)


print("\n=== 3. Emergency Muster Escalation ===")
print("Triggering MUSTER_TRIGGERED via sync/delta:")
muster_id = str(uuid.uuid4())
request_json("/sync/delta", {
    "events": [{
        "id": muster_id,
        "station_id": "BHARATI",
        "event_type": "MUSTER_TRIGGERED",
        "payload": {"reason": "Test muster from test script"},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }]
})

print("\nFetching muster events:")
musters = request_json("/muster-events?station_id=BHARATI", method="GET")
pjson(musters)


print("\n=== 4. Directive Acknowledgment ===")
print("Creating directive:")
directive = request_json("/directives", {
    "station_id": "BHARATI",
    "message": "Please perform generator maintenance.",
    "issued_by": "HQ Goa"
})
pjson(directive)
dir_id = directive["id"]

print("\nFetching directives (should be unacknowledged):")
dirs_before = request_json("/directives?station_id=BHARATI", method="GET")
pjson(dirs_before)

print("\nAcknowledging directive via sync/delta:")
ack_id = str(uuid.uuid4())
request_json("/sync/delta", {
    "events": [{
        "id": ack_id,
        "station_id": "BHARATI",
        "event_type": "DIRECTIVE_ACKNOWLEDGED",
        "payload": {"directive_id": dir_id},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }]
})

print("\nFetching directives (should be acknowledged):")
dirs_after = request_json("/directives?station_id=BHARATI", method="GET")
pjson(dirs_after)

print("\nResending identical acknowledgment event (testing idempotency):")
dup_ack_res = request_json("/sync/delta", {
    "events": [{
        "id": ack_id,
        "station_id": "BHARATI",
        "event_type": "DIRECTIVE_ACKNOWLEDGED",
        "payload": {"directive_id": dir_id},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }]
})
pjson(dup_ack_res)

print("\nFetching directives (should still be acknowledged):")
dirs_final = request_json("/directives?station_id=BHARATI", method="GET")
pjson(dirs_final)
