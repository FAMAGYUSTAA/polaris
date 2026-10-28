import sys

dexie_file = 'src/db/dexie.js'
with open(dexie_file, 'r', encoding='utf-8') as f:
    content = f.read()

# We need to add version 3
new_stores = """});

db.version(3).stores({
  inventory: "id, sku, name, category, quantity, unit, minimum_threshold",
  personnel: "id, full_name, role, status, last_seen",
  fieldMissions: "id, team_lead, destination_coords, departure_time, expected_return, is_active",
  outboxEvents: "++local_id, id, event_type, payload, timestamp, sync_status",
  plannedExpeditions: "id, team_lead, purpose, destination_coords, vhf_channel, planned_departure, planned_return, status",
  directives: "id, message, issued_by, issued_at, acknowledged",
});"""

content = content.replace("});\n\n// ---------------------------------------------------------------------------", new_stores + "\n\n// ---------------------------------------------------------------------------")

with open(dexie_file, 'w', encoding='utf-8') as f:
    f.write(content)

# Update syncService.js
sync_file = 'src/services/syncService.js'
with open(sync_file, 'a', encoding='utf-8') as f:
    f.write('''
export async function syncDirectivesFromServer(stationId = "BHARATI") {
  const resp = await fetch(`${API_BASE}/api/directives?station_id=${stationId}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch directives: HTTP ${resp.status}`);
  }
  const items = await resp.json();
  await db.directives.bulkPut(items);
}
''')

# Update App.jsx
app_file = 'src/App.jsx'
with open(app_file, 'r', encoding='utf-8') as f:
    app_content = f.read()

app_content = app_content.replace('import HeaderStatus from "./components/HeaderStatus.jsx";', 'import HeaderStatus from "./components/HeaderStatus.jsx";\nimport DirectivesPanel from "./components/DirectivesPanel.jsx";')
app_content = app_content.replace('<main className="app-main">', '<main className="app-main">\n        <DirectivesPanel />')

with open(app_file, 'w', encoding='utf-8') as f:
    f.write(app_content)

print("Updated frontend files.")
