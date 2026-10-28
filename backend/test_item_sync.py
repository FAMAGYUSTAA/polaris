import urllib.request
import urllib.error
import json
import uuid
import sys

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

# Helper to fetch inventory
def get_inventory():
    req = urllib.request.Request(f"{base_url}/inventory?station_id=BHARATI")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

# Print JSON helper
def pjson(data):
    print(json.dumps(data, indent=2))

print("=== Starting Event Sourcing Offline Tests ===\n")

client_generated_id = str(uuid.uuid4())
event_id_create = str(uuid.uuid4())

# 1. POST ITEM_CREATED
print(f"1. Testing ITEM_CREATED (UUID: {client_generated_id})")
payload_create = {
    "events": [
        {
            "id": event_id_create,
            "station_id": "BHARATI",
            "event_type": "ITEM_CREATED",
            "payload": {
                "id": client_generated_id,
                "station_id": "BHARATI",
                "sku": "TEST-ITEM-001",
                "name": "Test Offline Item",
                "category": "Scientific",
                "quantity": 100,
                "unit": "kg",
                "minimum_threshold": 10
            },
            "timestamp": "2026-09-06T00:00:00Z"
        }
    ]
}
resp_create = post_json("/sync/delta", payload_create)
print("Response:")
pjson(resp_create)

inv = get_inventory()
item = next((i for i in inv if i["sku"] == "TEST-ITEM-001"), None)
print(f"Inventory check: Found? {'Yes' if item else 'No'}. ID matches? {item['id'] == client_generated_id if item else 'N/A'}")


# 2. Resend exact same ITEM_CREATED
print(f"\n2. Testing ITEM_CREATED Idempotency (Event ID: {event_id_create})")
resp_create_dup = post_json("/sync/delta", payload_create)
print("Response:")
pjson(resp_create_dup)
inv = get_inventory()
test_items = [i for i in inv if i["sku"] == "TEST-ITEM-001"]
print(f"Count of TEST-ITEM-001 in inventory: {len(test_items)}")


# 3. POST ITEM_DELETED
print(f"\n3. Testing ITEM_DELETED (Item UUID: {client_generated_id})")
event_id_delete = str(uuid.uuid4())
payload_delete = {
    "events": [
        {
            "id": event_id_delete,
            "station_id": "BHARATI",
            "event_type": "ITEM_DELETED",
            "payload": {
                "item_id": client_generated_id
            },
            "timestamp": "2026-09-06T00:00:01Z"
        }
    ]
}
resp_delete = post_json("/sync/delta", payload_delete)
print("Response:")
pjson(resp_delete)

inv = get_inventory()
item_after_del = next((i for i in inv if i["sku"] == "TEST-ITEM-001"), None)
print(f"Inventory check after delete: Found? {'Yes' if item_after_del else 'No'}")


# 4. Resend same ITEM_DELETED
print(f"\n4. Testing ITEM_DELETED Idempotency (Event ID: {event_id_delete})")
resp_delete_dup = post_json("/sync/delta", payload_delete)
print("Response:")
pjson(resp_delete_dup)


# 5. POST ITEM_CREATED with existing SKU (Duplicate safe-check)
print(f"\n5. Testing ITEM_CREATED with existing SKU (FUEL-JA1-001)")
event_id_dup_sku = str(uuid.uuid4())
new_uuid_for_fuel = str(uuid.uuid4())
payload_dup_sku = {
    "events": [
        {
            "id": event_id_dup_sku,
            "station_id": "BHARATI",
            "event_type": "ITEM_CREATED",
            "payload": {
                "id": new_uuid_for_fuel,
                "station_id": "BHARATI",
                "sku": "FUEL-JA1-001",
                "name": "Duplicate Jet A1",
                "category": "Fuel"
            },
            "timestamp": "2026-09-06T00:00:02Z"
        }
    ]
}
resp_dup_sku = post_json("/sync/delta", payload_dup_sku)
print("Response:")
pjson(resp_dup_sku)

inv = get_inventory()
fuel_items = [i for i in inv if i["sku"] == "FUEL-JA1-001"]
print(f"Count of FUEL-JA1-001 in inventory: {len(fuel_items)}")

