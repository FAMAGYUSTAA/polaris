"""
test_auth_integration.py -- End-to-end verification for Point 4B authentication.

Tests:
  1. Valid HQ login
  2. Valid Station login
  3. Invalid password -> 401
  4. Role separation: Station token -> HQ-only endpoint -> 403
  5. Station sync/delta with valid token -> 200
  6. HQ sync/delta (wrong role) -> 403
  7. No token -> 401
  8. Read endpoints remain accessible without auth (health, GET cargo, etc.)
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import sys

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0

def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} -- {detail}")

def post_form(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, None

def post_json(url, data, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, None

def get(url, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, None

print("\n=== Point 4B Authentication Integration Tests ===\n")

# TEST 1: Valid HQ login
print("[TEST 1] Valid HQ login")
status, data = post_form(f"{BASE}/api/auth/login", {"username": "hq_operator", "password": "hq_password", "grant_type": "password"})
test("HQ login returns 200", status == 200, f"got {status}")
hq_token = data["access_token"] if data else None
test("HQ token received", hq_token is not None)
if hq_token:
    payload = json.loads(urllib.request.urlopen(urllib.request.Request("https://httpbin.org/base64/" + "unused")).read().decode()) if False else None
    # Decode JWT manually
    import base64
    parts = hq_token.split(".")
    padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
    jwt_payload = json.loads(base64.b64decode(padded))
    test("HQ token has role=HQ", jwt_payload.get("role") == "HQ", f"got {jwt_payload.get('role')}")
    test("HQ token has station_id=None", jwt_payload.get("station_id") is None)

# TEST 2: Valid Station login
print("\n[TEST 2] Valid Station login")
status, data = post_form(f"{BASE}/api/auth/login", {"username": "bharati_operator", "password": "bharati_password", "grant_type": "password"})
test("Station login returns 200", status == 200, f"got {status}")
st_token = data["access_token"] if data else None
test("Station token received", st_token is not None)
if st_token:
    parts = st_token.split(".")
    padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
    jwt_payload = json.loads(base64.b64decode(padded))
    test("Station token has role=STATION", jwt_payload.get("role") == "STATION")
    test("Station token has station_id=BHARATI", jwt_payload.get("station_id") == "BHARATI")

# TEST 3: Invalid password
print("\n[TEST 3] Invalid password")
status, _ = post_form(f"{BASE}/api/auth/login", {"username": "hq_operator", "password": "wrong_password", "grant_type": "password"})
test("Invalid password returns 401", status == 401, f"got {status}")

# TEST 4: Role separation -- Station token on HQ-only endpoint
print("\n[TEST 4] Role separation")
status, _ = post_json(f"{BASE}/api/directives", {"station_id": "BHARATI", "message": "test", "issued_by": "test"}, token=st_token)
test("Station token -> POST /api/directives -> 403", status == 403, f"got {status}")

status, _ = post_json(f"{BASE}/api/directives", {"station_id": "BHARATI", "message": "auth test", "issued_by": "hq"}, token=hq_token)
test("HQ token -> POST /api/directives -> 200", status == 200, f"got {status}")

# TEST 5: Station sync/delta
print("\n[TEST 5] Station sync/delta with valid token")
status, data = post_json(f"{BASE}/api/sync/delta", {"events": []}, token=st_token)
test("Station token -> POST /api/sync/delta -> 200", status == 200, f"got {status}")
test("Sync response has status=OK", data and data.get("status") == "OK")

# TEST 6: HQ on sync/delta (wrong role)
print("\n[TEST 6] HQ token on sync/delta")
status, _ = post_json(f"{BASE}/api/sync/delta", {"events": []}, token=hq_token)
test("HQ token -> POST /api/sync/delta -> 403", status == 403, f"got {status}")

# TEST 7: No token on protected endpoint
print("\n[TEST 7] No token on protected endpoint")
status, _ = post_json(f"{BASE}/api/sync/delta", {"events": []})
test("No token -> POST /api/sync/delta -> 401", status == 401, f"got {status}")

# TEST 8: Read-only endpoints remain open
print("\n[TEST 8] Read-only endpoints remain accessible")
status, _ = get(f"{BASE}/api/health")
test("GET /api/health -> 200 (no auth)", status == 200, f"got {status}")

status, _ = get(f"{BASE}/api/cargo?station_id=BHARATI")
test("GET /api/cargo -> 200 (no auth)", status == 200, f"got {status}")

status, _ = get(f"{BASE}/api/expeditions?station_id=BHARATI")
test("GET /api/expeditions -> 200 (no auth)", status == 200, f"got {status}")

status, _ = get(f"{BASE}/api/directives?station_id=BHARATI")
test("GET /api/directives -> 200 (no auth)", status == 200, f"got {status}")

# TEST 9: Station impersonation check
print("\n[TEST 9] Station impersonation prevention")
fake_event = {
    "events": [{
        "id": "test-fake-123",
        "event_type": "ASSET_DELTA",
        "station_id": "MAITRI",
        "timestamp": "2026-09-09T12:00:00Z",
        "payload": {"item_id": "fake", "delta": 1}
    }]
}
status, _ = post_json(f"{BASE}/api/sync/delta", fake_event, token=st_token)
test("Station BHARATI token -> event claiming MAITRI -> 403", status == 403, f"got {status}")

# Summary
print(f"\n{'='*50}")
print(f"Results: {PASS} passed, {FAIL} failed out of {PASS + FAIL}")
if FAIL > 0:
    sys.exit(1)
print("All tests passed!")
