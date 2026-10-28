import urllib.request
import urllib.error
import json

base_url = "http://127.0.0.1:8000/api"

# 1. Create shipment with real SKU
print("--- Creating Shipment with valid SKU ---")
shipment_data = {
    "station_id": "BHARATI",
    "carrier_name": "IL-76 Flight",
    "origin": "Goa, India",
    "manifest": [
        {
            "sku": "FUEL-JA1-001",
            "name": "Jet-A1 Aviation Fuel",
            "quantity": 5000,
            "unit": "L"
        }
    ],
    "departure_date": "2026-09-01T10:00:00Z",
    "expected_arrival": "2026-09-07T12:00:00Z"
}
req = urllib.request.Request(
    f"{base_url}/cargo",
    data=json.dumps(shipment_data).encode(),
    headers={"Content-Type": "application/json"},
    method="POST"
)
try:
    with urllib.request.urlopen(req) as response:
        create_resp = json.loads(response.read().decode())
        print("Create response:", json.dumps(create_resp, indent=2))
        shipment_id = create_resp["id"]
except urllib.error.HTTPError as e:
    print("Error:", e.read().decode())
    exit(1)

# 2. Mark arrived
print("\n--- Marking valid shipment as arrived ---")
req = urllib.request.Request(
    f"{base_url}/cargo/{shipment_id}/mark-arrived",
    method="POST"
)
try:
    with urllib.request.urlopen(req) as response:
        arrive_resp = json.loads(response.read().decode())
        print("Mark arrived response:", json.dumps(arrive_resp, indent=2))
except urllib.error.HTTPError as e:
    print("Error:", e.read().decode())

# 3. Check inventory
print("\n--- Checking inventory ---")
req = urllib.request.Request(f"{base_url}/inventory?station_id=BHARATI")
with urllib.request.urlopen(req) as response:
    inv = json.loads(response.read().decode())
    fuel = next(i for i in inv if i["sku"] == "FUEL-JA1-001")
    print(f"Fuel quantity: {fuel['quantity']} (Expected: 55000 since seeded with 50000)")


# 4. Create shipment with fake SKU
print("\n--- Creating Shipment with fake SKU ---")
fake_shipment = shipment_data.copy()
fake_shipment["manifest"] = [
    {
        "sku": "FAKE-001",
        "name": "Fake Item",
        "quantity": 10,
        "unit": "kg"
    }
]
req = urllib.request.Request(
    f"{base_url}/cargo",
    data=json.dumps(fake_shipment).encode(),
    headers={"Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req) as response:
    fake_resp = json.loads(response.read().decode())
    fake_id = fake_resp["id"]

print("\n--- Marking fake shipment as arrived ---")
req = urllib.request.Request(
    f"{base_url}/cargo/{fake_id}/mark-arrived",
    method="POST"
)
try:
    with urllib.request.urlopen(req) as response:
        fake_arrive_resp = json.loads(response.read().decode())
        print("Mark arrived response (fake):", json.dumps(fake_arrive_resp, indent=2))
except urllib.error.HTTPError as e:
    print("Error:", e.read().decode())
