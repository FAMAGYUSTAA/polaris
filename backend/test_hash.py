import json
import hashlib
from schemas import SneakernetBundle

# This mimics exactly what the JS will send
js_payload = {
    "station_id": "BHARATI",
    "exported_at": "2026-09-05T10:17:52.249Z",
    "events": [
        {
            "id": "1234",
            "event_type": "MUSTER_TRIGGERED",
            "payload": {"initiated_by": "field_ui"},
            "timestamp": "2026-09-05T10:17:52.249Z",
            "station_id": "BHARATI"
        }
    ]
}

# The bundle needs a hash, but we compute it first
bundle_dict = js_payload.copy()
canonical_json = json.dumps(
    bundle_dict,
    sort_keys=True,
    separators=(',', ':'),
    default=str
)
calculated_hash = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

js_payload["hash"] = calculated_hash

with open("test_sn_payload.json", "w") as f:
    json.dump(js_payload, f)

print(calculated_hash)
