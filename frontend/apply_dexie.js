import fs from "fs";

const filepath = "frontend/src/db/dexie.js";
let content = fs.readFileSync(filepath, "utf8");

const version3 = `db.version(3).stores({
  inventory: "id, sku, name, category, quantity, unit, minimum_threshold",
  personnel: "id, full_name, role, status, last_seen",
  fieldMissions: "id, team_lead, destination_coords, departure_time, expected_return, is_active",
  outboxEvents: "++local_id, id, event_type, payload, timestamp, sync_status",
  plannedExpeditions: "id, team_lead, purpose, destination_coords, vhf_channel, planned_departure, planned_return, status",
  directives: "id, message, issued_by, issued_at, acknowledged",
});`;

const version4 = `db.version(4).stores({
  inventory: "id, sku, name, category, quantity, unit, minimum_threshold",
  personnel: "id, full_name, role, status, last_seen",
  fieldMissions: "id, team_lead, destination_coords, departure_time, expected_return, is_active",
  outboxEvents: "++local_id, id, event_type, payload, timestamp, sync_status",
  plannedExpeditions: "id, team_lead, purpose, destination_coords, vhf_channel, planned_departure, planned_return, status",
  directives: "id, message, issued_by, issued_at, acknowledged",
  cargoShipments: "id, station_id, carrier_name, origin, departure_date, expected_arrival, status, hq_approved, arrived_at, created_at",
});`;

content = content.replace(version3, version3 + "\n\n" + version4);
fs.writeFileSync(filepath, content);
console.log("dexie.js updated with cargoShipments table.");
