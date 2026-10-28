import urllib.request
import urllib.error
import json

base_url = "http://127.0.0.1:8000/api"

def login(username, password):
    data = f"username={username}&password={password}&grant_type=password".encode()
    req = urllib.request.Request(f"{base_url}/auth/login", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())["access_token"]
    except urllib.error.HTTPError as e:
        print(f"Login failed for {username}: {e.code}")
        return None

def fetch(endpoint, token=None):
    req = urllib.request.Request(f"{base_url}{endpoint}")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

hq_token = login("hq_operator", "hq_password")
bh_token = login("bharati_operator", "bharati_password")
ma_token = login("maitri_operator", "maitri_password")
hi_token = login("himadri_operator", "himadri_password")

print(f"Tokens obtained: HQ={'YES' if hq_token else 'NO'}, BHARATI={'YES' if bh_token else 'NO'}, MAITRI={'YES' if ma_token else 'NO'}, HIMADRI={'YES' if hi_token else 'NO'}")

# Test Read endpoint isolation
status, res = fetch("/inventory?station_id=BHARATI", bh_token)
print(f"Bharati fetching BHARATI: {status}")

status, res = fetch("/inventory?station_id=MAITRI", bh_token)
print(f"Bharati fetching MAITRI: {status}")

status, res = fetch("/inventory?station_id=MAITRI", ma_token)
print(f"Maitri fetching MAITRI: {status}")

status, res = fetch("/inventory?station_id=HIMADRI", hq_token)
print(f"HQ fetching HIMADRI: {status}")

# Test invalid station
status, res = fetch("/inventory?station_id=DELHI", hq_token)
print(f"HQ fetching DELHI: {status}")

# Seed Maitri and test again
print("Done")
