import sys

# 1. Update dexie.js
dexie_file = 'src/db/dexie.js'
content = open(dexie_file, 'r', encoding='utf-8').read()
old_stores = """db.version(1).stores({
  // -----------------------------------------------------------------
  // Materialised state tables
  //
  // These mirror the backend's SQLAlchemy models.  The first field in
  // each schema string is the primary key; subsequent fields are
  // indexed for query performance.
  // -----------------------------------------------------------------
  inventory:
    "id, sku, name, category, quantity, unit, minimum_threshold",

  personnel:
    "id, full_name, role, status, last_seen",

  fieldMissions:
    "id, team_lead, destination_coords, departure_time, expected_return, is_active",

  // -----------------------------------------------------------------
  // Outbox ?" events created locally, awaiting sync to the backend
  //
  // WHY ++local_id (auto-increment) as the Dexie primary key:
  //
  //   `local_id` is a monotonically increasing integer assigned by
  //   IndexedDB on this specific device.  It has NO meaning outside
  //   this browser/device ?" it's never sent to the server and is not
  //   globally unique.  Its purpose is:
  //     1. To give Dexie a fast, auto-generated primary key for local
  //        CRUD without requiring the caller to supply one.
  //     2. To provide a stable, never-reused handle for
  //        `markEventSynced(local_id)` so we can update exactly the
  //        right row even if the same `id` appears in a retry scenario.
  //
  //   `id` (the second field, indexed but NOT the PK) is the
  //   client-generated UUID that becomes `client_event_id` on the
  //   server ?" the globally unique idempotency key that prevents
  //   duplicate replay when a station reconnects after weeks offline.
  //   It is indexed so the sync service can quickly check for
  //   duplicates before queuing a new event.
  // -----------------------------------------------------------------
  outboxEvents:
    "++local_id, id, event_type, payload, timestamp, sync_status",
});"""
# We must replace db.version(1).stores({...}) with db.version(2).stores({...}) keeping the existing tables and adding plannedExpeditions, or just append version(2).
# Dexie schema changes: we need to chain .version(2).stores({ plannedExpeditions: "..." }). Wait, Dexie allows db.version(2).stores( { ... all tables including new ones ... } ) or just the new ones? 
# Usually, Dexie requires ALL tables in the latest version definition if you want them to remain. 
new_stores = content.replace("db.version(1).stores({", "db.version(1).stores({").replace("});", "});\n\ndb.version(2).stores({\n  inventory: \"id, sku, name, category, quantity, unit, minimum_threshold\",\n  personnel: \"id, full_name, role, status, last_seen\",\n  fieldMissions: \"id, team_lead, destination_coords, departure_time, expected_return, is_active\",\n  outboxEvents: \"++local_id, id, event_type, payload, timestamp, sync_status\",\n  plannedExpeditions: \"id, team_lead, purpose, destination_coords, vhf_channel, planned_departure, planned_return, status\",\n});", 1)
with open(dexie_file, 'w', encoding='utf-8') as f:
    f.write(new_stores)

# 2. Update syncService.js
sync_file = 'src/services/syncService.js'
with open(sync_file, 'a', encoding='utf-8') as f:
    f.write('''
export async function syncExpeditionsFromServer(stationId = "BHARATI") {
  const resp = await fetch(`${API_BASE}/api/expeditions?station_id=${stationId}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch expeditions: HTTP ${resp.status}`);
  }
  const items = await resp.json();
  await db.plannedExpeditions.bulkPut(items);
}
''')

# 3. Update App.jsx
app_file = 'src/App.jsx'
app_content = open(app_file, 'r', encoding='utf-8').read()
app_content = app_content.replace('import PersonnelTracker from "./components/PersonnelTracker.jsx";', 'import PersonnelTracker from "./components/PersonnelTracker.jsx";\nimport ExpeditionPlanning from "./components/ExpeditionPlanning.jsx";')
app_content = app_content.replace('<PersonnelTracker />', '<PersonnelTracker />\n        <ExpeditionPlanning />')
with open(app_file, 'w', encoding='utf-8') as f:
    f.write(app_content)

print("Appended frontend files.")
