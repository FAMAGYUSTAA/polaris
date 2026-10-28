/**
 * dexie.js — Local-first IndexedDB client database for the Polar Logistics PWA.
 *
 * This is the offline data layer.  Every piece of station data the UI renders
 * comes from this Dexie database, NOT from direct API calls.  The sync service
 * (built in a later task) is responsible for hydrating these tables from the
 * backend and flushing the outbox.
 *
 * Tables:
 *   inventory      — materialised stock levels, mirroring backend InventoryItem.
 *   personnel      — personnel roster, mirroring backend Personnel.
 *   fieldMissions  — active/past field missions, mirroring backend FieldMission.
 *   outboxEvents   — locally-queued events waiting to be synced to the server.
 *
 * The app can operate entirely from this database when the station is air-gapped.
 */

import Dexie from "dexie";

const db = new Dexie("PolarStationDB");

db.version(1).stores({
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
  // Outbox — events created locally, awaiting sync to the backend
  //
  // WHY ++local_id (auto-increment) as the Dexie primary key:
  //
  //   `local_id` is a monotonically increasing integer assigned by
  //   IndexedDB on this specific device.  It has NO meaning outside
  //   this browser/device — it's never sent to the server and is not
  //   globally unique.  Its purpose is:
  //     1. To give Dexie a fast, auto-generated primary key for local
  //        CRUD without requiring the caller to supply one.
  //     2. To provide a stable, never-reused handle for
  //        `markEventSynced(local_id)` so we can update exactly the
  //        right row even if the same `id` appears in a retry scenario.
  //
  //   `id` (the second field, indexed but NOT the PK) is the
  //   client-generated UUID that becomes `client_event_id` on the
  //   server — the globally unique idempotency key that prevents
  //   duplicate replay when a station reconnects after weeks offline.
  //   It is indexed so the sync service can quickly check for
  //   duplicates before queuing a new event.
  // -----------------------------------------------------------------
  outboxEvents:
    "++local_id, id, event_type, payload, timestamp, sync_status",
});

db.version(2).stores({
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



// ---------------------------------------------------------------------------
// Outbox helper functions
// ---------------------------------------------------------------------------

/**
 * Return all outbox events that have not yet been synced, ordered by
 * timestamp ascending (chronological).
 *
 * Chronological ordering is critical: the backend's sync_engine replays
 * events in order, and a FIELD_CHECKIN must arrive after its corresponding
 * FIELD_CHECKOUT.
 */
export async function getPendingOutboxEvents(stationId) {
  const pending = await db.outboxEvents
    .where("sync_status")
    .equals("PENDING")
    .sortBy("timestamp");
  return pending.filter(e => e.station_id === stationId);
}

/**
 * Mark a specific outbox event as successfully synced.
 *
 * Called by the sync service after the backend confirms the event was
 * applied or identified as a duplicate (both mean "safely server-side,
 * purge from outbox").
 *
 * @param {number} localId — the auto-incremented Dexie primary key
 */
export async function markEventSynced(localId) {
  return db.outboxEvents.update(localId, { sync_status: "SYNCED" });
}

/**
 * Return the count of pending (un-synced) outbox events.
 *
 * Used by the UI status bar badge to show how many local changes are
 * waiting to be pushed — e.g. "3 pending" in amber when air-gapped.
 */
export async function getOutboxPendingCount(stationId) {
  const pending = await db.outboxEvents
    .where("sync_status")
    .equals("PENDING")
    .toArray();
  return pending.filter(e => e.station_id === stationId).length;
}

db.version(5).stores({
  inventory: "id, sku, name, category, quantity, unit, minimum_threshold",
  personnel: "id, full_name, role, status, last_seen",
  fieldMissions: "id, team_lead, destination_coords, departure_time, expected_return, is_active",
  outboxEvents: "++local_id, id, event_type, payload, timestamp, sync_status",
  plannedExpeditions: "id, team_lead, purpose, destination_coords, vhf_channel, planned_departure, planned_return, status",
  directives: "id, message, issued_by, issued_at, acknowledged",
  cargoShipments: "id, station_id, carrier_name, origin, manifest, departure_date, expected_arrival, status, hq_approved, arrived_at",
  authSessions: "username, role, station_id, password_verifier, last_authenticated_at",
});

db.version(6).stores({
  inventory: "id, sku, name, category, quantity, unit, minimum_threshold",
  personnel: "id, full_name, role, status, last_seen",
  fieldMissions: "id, team_lead, destination_coords, departure_time, expected_return, is_active",
  outboxEvents: "++local_id, id, event_type, payload, timestamp, sync_status",
  plannedExpeditions: "id, team_lead, purpose, destination_coords, vhf_channel, planned_departure, planned_return, status",
  directives: "id, message, issued_by, issued_at, acknowledged",
  cargoShipments: "id, station_id, carrier_name, origin, manifest, departure_date, expected_arrival, status, hq_approved, arrived_at",
  authSessions: "username, role, station_id, password_verifier, last_authenticated_at",
}).upgrade(async tx => {
  // Wipe old operational test data for BHARATI without touching personnel or authSessions
  await tx.inventory.filter(i => i.station_id === 'BHARATI' || !i.station_id).delete();
  await tx.cargoShipments.filter(c => c.station_id === 'BHARATI' || !c.station_id).delete();
  await tx.plannedExpeditions.filter(p => p.station_id === 'BHARATI' || !p.station_id).delete();
  await tx.directives.filter(d => d.station_id === 'BHARATI' || !d.station_id).delete();
  await tx.outboxEvents.filter(e => e.station_id === 'BHARATI' || !e.station_id).delete();
  await tx.fieldMissions.filter(m => m.station_id === 'BHARATI' || !m.station_id).delete();
});

export default db;
