import sys

dexie_file = 'src/db/dexie.js'
with open(dexie_file, 'r', encoding='utf-8') as f:
    content = f.read()

new_stores = """db.version(2).stores({
  inventory: "id, sku, name, category, quantity, unit, minimum_threshold",
  personnel: "id, full_name, role, status, last_seen",
  fieldMissions: "id, team_lead, destination_coords, departure_time, expected_return, is_active",
  outboxEvents: "++local_id, id, event_type, payload, timestamp, sync_status",
  plannedExpeditions: "id, team_lead, purpose, destination_coords, vhf_channel, planned_departure, planned_return, status",
});

db.version(3).stores({
  inventory: "id, sku, name, category, quantity, unit, minimum_threshold",
  personnel: "id, full_name, role, status, last_seen",
  fieldMissions: "id, team_lead, destination_coords, departure_time, expected_return, is_active",
  outboxEvents: "++local_id, id, event_type, payload, timestamp, sync_status",
  plannedExpeditions: "id, team_lead, purpose, destination_coords, vhf_channel, planned_departure, planned_return, status",
  directives: "id, message, issued_by, issued_at, acknowledged",
});
"""

content = content.replace("db.version(2).stores({\n  inventory: \"id, sku, name, category, quantity, unit, minimum_threshold\",\n  personnel: \"id, full_name, role, status, last_seen\",\n  fieldMissions: \"id, team_lead, destination_coords, departure_time, expected_return, is_active\",\n  outboxEvents: \"++local_id, id, event_type, payload, timestamp, sync_status\",\n  plannedExpeditions: \"id, team_lead, purpose, destination_coords, vhf_channel, planned_departure, planned_return, status\",\n});", new_stores)

with open(dexie_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated dexie.js successfully.")
