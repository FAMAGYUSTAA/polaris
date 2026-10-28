import 'fake-indexeddb/auto';

import crypto from 'crypto';
import Dexie from 'dexie';



// 1. Re-declare Dexie DB to match frontend exactly
const db = new Dexie("PolarLogisticsDB");
db.version(1).stores({
  inventory: "id, sku, name",
  personnel: "id, full_name, status",
  fieldMissions: "id, is_active",
  outboxEvents: "id, timestamp, sync_status"
});

const API_BASE = 'http://127.0.0.1:8000';

async function runTests() {
  console.log("=== STARTING INTEGRATION TESTS ===\n");

  // --- STEP 1: Initial load / ground-truth pull ---
  console.log("1. Ground-Truth Pull");
  const invResp = await fetch(`${API_BASE}/api/inventory?station_id=BHARATI`);
  const inventoryData = await invResp.json();
  await db.inventory.bulkPut(inventoryData);

  const persResp = await fetch(`${API_BASE}/api/personnel?station_id=BHARATI`);
  const { personnel, active_missions } = await persResp.json();
  await db.personnel.bulkPut(personnel);
  await db.fieldMissions.bulkPut(active_missions);

  const initItems = await db.inventory.toArray();
  const initPersonnel = await db.personnel.toArray();
  console.log(`[Dexie] Populated ${initItems.length} inventory items and ${initPersonnel.length} personnel.`);
  console.log(`[Dexie State]:\nInventory:`, JSON.stringify(initItems, null, 2).slice(0, 300) + '...');
  
  // --- STEP 2: Offline consumption flow ---
  console.log("\n2. Offline Consumption Flow");
  const jetA1 = await db.inventory.where('sku').equals('FUEL-JA1-001').first();
  const initialQty = jetA1.quantity;
  const consumeAmount = 200;
  
  // Simulate AssetInventory logic:
  const newQuantity = Math.max(0, jetA1.quantity - consumeAmount);
  await db.inventory.update(jetA1.id, { quantity: newQuantity });
  
  const eventId = crypto.randomUUID();
  await db.outboxEvents.add({
    id: eventId,
    event_type: "ASSET_DELTA",
    payload: {
      item_id: jetA1.id,
      delta: -consumeAmount,
      reason: "Generator Run — Test"
    },
    timestamp: new Date().toISOString(),
    sync_status: "PENDING",
    station_id: "BHARATI"
  });

  const updatedJetA1 = await db.inventory.get(jetA1.id);
  console.log(`[Dexie] Jet-A1 updated optimistically: ${initialQty} -> ${updatedJetA1.quantity}`);
  const outboxContents = await db.outboxEvents.toArray();
  console.log(`[Dexie] Outbox contents:\n`, JSON.stringify(outboxContents, null, 2));

  const backendInvCheck = await fetch(`${API_BASE}/api/inventory?station_id=BHARATI`);
  const backendInvCheckData = await backendInvCheck.json();
  const backendJetA1Check = backendInvCheckData.find(i => i.id === jetA1.id);
  console.log(`[Backend] Jet-A1 quantity UNCHANGED: ${backendJetA1Check.quantity}`);

  // --- STEP 3: Reconnection / auto-sync flow ---
  console.log("\n3. Reconnection / Auto-Sync Flow");
  const batch = await db.outboxEvents.where('sync_status').equals('PENDING').toArray();
  const batchPayload = batch.map(e => ({
    id: e.id,
    event_type: e.event_type,
    payload: e.payload,
    timestamp: e.timestamp,
    station_id: e.station_id
  }));
  
  const syncResp = await fetch(`${API_BASE}/api/sync/delta`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ station_id: 'BHARATI', events: batchPayload })
  });
  const syncResult = await syncResp.json();
  console.log(`[Backend] /api/sync/delta response:\n`, JSON.stringify(syncResult, null, 2));

  for (const id of syncResult.synced_ids) {
    await db.outboxEvents.update(id, { sync_status: 'SYNCED' });
  }

  const backendInvCheck2 = await fetch(`${API_BASE}/api/inventory?station_id=BHARATI`);
  const backendInvCheckData2 = await backendInvCheck2.json();
  const backendJetA1Check2 = backendInvCheckData2.find(i => i.id === jetA1.id);
  console.log(`[Backend] Jet-A1 quantity after sync: ${backendJetA1Check2.quantity}`);
  console.log(`[Check] Match? ${backendJetA1Check2.quantity === updatedJetA1.quantity ? 'YES' : 'NO'}`);

  // --- STEP 4: Field checkout/check-in round trip ---
  console.log("\n4. Field Checkout/Check-in Round Trip");
  const insideBase = initPersonnel.filter(p => p.status === 'INSIDE_BASE');
  const p1 = insideBase[0];
  const p2 = insideBase[1];
  
  // Checkout
  const missionId = crypto.randomUUID();
  await db.personnel.update(p1.id, { status: "FIELD_MISSION" });
  await db.personnel.update(p2.id, { status: "FIELD_MISSION" });
  await db.fieldMissions.add({ id: missionId, team_lead: p1.full_name, is_active: true });
  
  const checkoutEventId = crypto.randomUUID();
  await db.outboxEvents.add({
    id: checkoutEventId,
    event_type: "FIELD_CHECKOUT",
    payload: { 
      mission_id: missionId,
      team_lead: p1.full_name, 
      members: [p1.full_name, p2.full_name], 
      personnel_ids: [p1.id, p2.id] 
    },
    timestamp: new Date().toISOString(),
    sync_status: "PENDING",
    station_id: "BHARATI"
  });
  
  console.log(`[Dexie] Checkout done. Syncing...`);
  const checkoutBatch = await db.outboxEvents.where('sync_status').equals('PENDING').toArray();
  const checkoutSync = await fetch(`${API_BASE}/api/sync/delta`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ station_id: 'BHARATI', events: checkoutBatch.map(e => ({ id: e.id, event_type: e.event_type, payload: e.payload, timestamp: e.timestamp, station_id: e.station_id })) })
  });
  const checkoutRes = await checkoutSync.json();
  console.log(`[Backend] Checkout sync response:`, checkoutRes.synced_ids.length > 0 ? "SUCCESS" : "FAIL");

  const bpResp = await fetch(`${API_BASE}/api/personnel?station_id=BHARATI`);
  const bpData = await bpResp.json();
  console.log(`[Backend] Active missions: ${bpData.active_missions.length}`);
  console.log(`[Backend] Personnel in FIELD_MISSION: ${bpData.personnel.filter(p => p.status === 'FIELD_MISSION').length}`);

  // Checkin
  await db.fieldMissions.update(missionId, { is_active: false });
  await db.personnel.update(p1.id, { status: "INSIDE_BASE" });
  await db.personnel.update(p2.id, { status: "INSIDE_BASE" });
  
  const checkinEventId = crypto.randomUUID();
  await db.outboxEvents.add({
    id: checkinEventId,
    event_type: "FIELD_CHECKIN",
    payload: { mission_id: missionId, personnel_ids: [p1.id, p2.id] },
    timestamp: new Date().toISOString(),
    sync_status: "PENDING",
    station_id: "BHARATI"
  });

  const checkinBatch = await db.outboxEvents.where('sync_status').equals('PENDING').toArray();
  const checkinSync = await fetch(`${API_BASE}/api/sync/delta`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ station_id: 'BHARATI', events: checkinBatch.map(e => ({ id: e.id, event_type: e.event_type, payload: e.payload, timestamp: e.timestamp, station_id: e.station_id })) })
  });
  await checkinSync.json();

  const bpResp2 = await fetch(`${API_BASE}/api/personnel?station_id=BHARATI`);
  const bpData2 = await bpResp2.json();
  console.log(`[Backend] Active missions after checkin: ${bpData2.active_missions.length}`);
  console.log(`[Backend] Personnel in FIELD_MISSION: ${bpData2.personnel.filter(p => p.status === 'FIELD_MISSION').length}`);

  // --- STEP 5: Sneakernet round-trip ---
  console.log("\n5. Sneakernet Round-Trip");
  // Queue 2 events
  const snEvt1 = crypto.randomUUID();
  const snEvt2 = crypto.randomUUID();
  await db.outboxEvents.add({
    id: snEvt1,
    event_type: "MUSTER_TRIGGERED",
    payload: { initiated_by: "field_ui" },
    timestamp: new Date().toISOString(),
    sync_status: "PENDING",
    station_id: "BHARATI"
  });
  await db.outboxEvents.add({
    id: snEvt2,
    event_type: "ASSET_DELTA",
    payload: { item_id: jetA1.id, delta: -50, reason: "Sneakernet test" },
    timestamp: new Date().toISOString(),
    sync_status: "PENDING",
    station_id: "BHARATI"
  });

  const pendingSN = await db.outboxEvents.where('sync_status').equals('PENDING').toArray();
  
  // Replicate exportSneakernetSnapshot logic
  const payloadToHash = {
    station_id: "BHARATI",
    exported_at: new Date().toISOString(),
    events: pendingSN.map(e => ({ id: e.id, event_type: e.event_type, payload: e.payload, timestamp: e.timestamp, station_id: e.station_id }))
  };
  
  const fs = await import('fs');
  const execSync = (await import('child_process')).execSync;
  fs.writeFileSync('temp_sn.json', JSON.stringify(payloadToHash));
  
  const pyScript = `
import json, hashlib
with open('temp_sn.json') as f:
    data = json.load(f)
canonical = json.dumps(data, sort_keys=True, separators=(',', ':'), default=str)
print(hashlib.sha256(canonical.encode('utf-8')).hexdigest(), end='')
  `;
  fs.writeFileSync('hash.py', pyScript);
  const correctHash = execSync('python hash.py').toString();
  
  const bundle = { ...payloadToHash, hash: correctHash };
  
  const snResp = await fetch(`${API_BASE}/api/sync/sneakernet-import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(bundle)
  });
  if(snResp.status !== 200) {
      console.log(`[Backend] Sneakernet valid import ERROR status:`, snResp.status, await snResp.json());
  } else {
      const snData = await snResp.json();
      console.log(`[Backend] Sneakernet valid import response:`, JSON.stringify(snData));
  }

  // Now corrupt the hash
  const badBundle = { ...payloadToHash, hash: correctHash.replace('a', 'b').replace('0', '1').replace('e','f') };
  const snRespBad = await fetch(`${API_BASE}/api/sync/sneakernet-import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(badBundle)
  });
  console.log(`[Backend] Sneakernet invalid hash response status: ${snRespBad.status}`);
  console.log(`[Backend] Message:`, await snRespBad.json());

  // --- STEP 6: Duplicate/idempotency sanity check ---
  console.log("\n6. Duplicate Idempotency Check");
  const dupEvent = {
    station_id: "BHARATI",
    events: [
      {
        id: eventId, // From Step 2, already synced
        event_type: "ASSET_DELTA",
        payload: { item_id: jetA1.id, delta: -consumeAmount, reason: "Duplicate attempt" },
        timestamp: new Date().toISOString(),
        station_id: "BHARATI"
      }
    ]
  };
  
  const dupResp = await fetch(`${API_BASE}/api/sync/delta`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dupEvent)
  });
  const dupData = await dupResp.json();
  console.log(`[Backend] Idempotency response (re-sending event ${eventId}):`);
  console.log(JSON.stringify(dupData, null, 2));

  console.log("\n=== ALL TESTS COMPLETED ===");
}

runTests().catch(console.error);
