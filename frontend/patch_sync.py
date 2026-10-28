import os

with open('src/services/syncService.js', 'r', encoding='utf-8') as f:
    code = f.read()

old_sync = """export async function syncExpeditionsFromServer(stationId) {
  const resp = await fetch(`${API_BASE}/api/expeditions?station_id=${stationId}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch expeditions: HTTP ${resp.status}`);
  }
  const items = await resp.json();
  await db.plannedExpeditions.bulkPut(items);
}"""

new_sync = """export async function syncExpeditionsFromServer(stationId) {
  const resp = await fetch(`${API_BASE}/api/expeditions?station_id=${stationId}`);
  if (!resp.ok) {
    throw new Error(`Failed to fetch expeditions: HTTP ${resp.status}`);
  }
  const items = await resp.json();
  
  // Re-apply local PENDING cancellations so server data doesn't overwrite un-synced offline actions
  const pendingEvents = await getPendingOutboxEvents(stationId);
  const canceledIds = new Set(
    pendingEvents
      .filter(e => e.event_type === "EXPEDITION_CANCELLED")
      .map(e => e.payload.expedition_id)
  );
  
  for (const item of items) {
    if (canceledIds.has(item.id)) {
      item.status = "CANCELLED";
    }
  }

  await db.plannedExpeditions.bulkPut(items);
}"""

if old_sync in code:
    code = code.replace(old_sync, new_sync)
    with open('src/services/syncService.js', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Patched syncService.js")
else:
    print("Could not find old sync in syncService.js")
