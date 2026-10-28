import urllib.request
import urllib.parse
import json

def get_token(username, password):
    login_data = urllib.parse.urlencode({"username": username, "password": password}).encode("utf-8")
    req = urllib.request.Request("http://localhost:8000/api/auth/login", data=login_data)
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())["access_token"]

# 1. Login as HQ
hq_token = get_token("hq_operator", "hq_password")

# 2. List cargo
req = urllib.request.Request("http://localhost:8000/api/cargo?station_id=MAITRI", headers={"Authorization": f"Bearer {hq_token}"})
try:
    with urllib.request.urlopen(req) as res:
        cargo = json.loads(res.read())
        print(f"Cargo count: {len(cargo)}")
        for c in cargo:
            print(c['id'], c.get('hq_approved'), c.get('status'))
except Exception as e:
    print(e.read())

# 3. Approve ship-01
print("\nApproving ship-01")
approve_req = urllib.request.Request(
    "http://localhost:8000/api/cargo/ship-01/approve", 
    data=b"", 
    headers={"Authorization": f"Bearer {hq_token}", "Content-Length": "0"}
)
approve_req.get_method = lambda: "POST"
try:
    with urllib.request.urlopen(approve_req) as res:
        print(json.loads(res.read()))
except Exception as e:
    print("Failed to approve", e)

# 4. List cargo again
req = urllib.request.Request("http://localhost:8000/api/cargo?station_id=MAITRI", headers={"Authorization": f"Bearer {hq_token}"})
try:
    with urllib.request.urlopen(req) as res:
        cargo = json.loads(res.read())
        for c in cargo:
            if c['id'] == 'ship-01':
                print("ship-01 after approval:", c.get('hq_approved'), c.get('status'))
except Exception as e:
    print(e)

