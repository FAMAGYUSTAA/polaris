import puppeteer from 'puppeteer';
import fs from 'fs';

async function runTests() {
  console.log("Starting End-to-End Test...");
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));

  await page.goto('http://127.0.0.1:4173', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 2000)); // wait for initial syncs

  const getDexieDump = async () => {
    return await page.evaluate(async () => {
      return new Promise((resolve, reject) => {
        const request = indexedDB.open('PolarLogisticsDB');
        request.onerror = (e) => reject(e);
        request.onsuccess = (e) => {
          const db = e.target.result;
          const getStore = (name) => new Promise(res => {
            const trans = db.transaction(name, 'readonly');
            const store = trans.objectStore(name);
            const req = store.getAll();
            req.onsuccess = () => res(req.result);
          });
          Promise.all([
            getStore('inventory'),
            getStore('personnel'),
            getStore('fieldMissions'),
            getStore('outboxEvents')
          ]).then(([items, personnel, missions, outbox]) => {
            resolve({ items, personnel, missions, outbox });
          });
        };
      });
    });
  };

  console.log("\n--- TEST 1: Initial Load ---");
  const initDexie = await getDexieDump();
  console.log(`Inventory Items in Dexie: ${initDexie.items.length}`);
  console.log(`Personnel in Dexie: ${initDexie.personnel.length}`);
  fs.writeFileSync('test1_dexie.json', JSON.stringify(initDexie, null, 2));

  console.log("\n--- TEST 2: Offline Consumption Flow ---");
  await page.setOfflineMode(true);
  console.log("Went offline.");

  await page.evaluate(() => {
    const cards = Array.from(document.querySelectorAll('.inventory-card'));
    const jetA1Card = cards.find(c => c.textContent.includes('Jet-A1 Fuel'));
    const consumeBtn = jetA1Card.querySelector('.btn-consume');
    consumeBtn.click();
  });

  await page.waitForSelector('.modal-content input[type="number"]');
  await page.type('.modal-content input[type="number"]', '200');
  const textInputs = await page.$$('.modal-content input[type="text"]');
  await textInputs[0].type('Generator Run - Test');
  await page.click('.modal-content .btn-confirm');
  await new Promise(r => setTimeout(r, 500));
  
  const offlineDexie = await getDexieDump();
  const jeta1 = offlineDexie.items.find(i => i.name === 'Jet-A1 Fuel');
  console.log(`Local Jet-A1 Fuel Quantity: ${jeta1.quantity} (Expected 49800)`);
  
  const newOutbox = offlineDexie.outbox.find(e => e.event_type === 'ASSET_DELTA');
  console.log(`Outbox Event Payload:`, JSON.stringify(newOutbox.payload));
  fs.writeFileSync('test2_dexie.json', JSON.stringify(offlineDexie, null, 2));
  
  const fetch = (await import('node-fetch')).default || globalThis.fetch;
  const backendInvResp = await fetch('http://127.0.0.1:8000/api/inventory?station_id=BHARATI');
  const backendInv = await backendInvResp.json();
  const backendJetA1 = backendInv.find(i => i.name === 'Jet-A1 Fuel');
  console.log(`Backend Jet-A1 Fuel Quantity: ${backendJetA1.quantity} (Expected 50000)`);

  console.log("\n--- TEST 3: Reconnection / Auto-sync ---");
  await page.setOfflineMode(false);
  console.log("Went online.");
  
  await page.evaluate(() => document.querySelector('.btn-sync').click());
  await new Promise(r => setTimeout(r, 1000));
  
  const syncDexie = await getDexieDump();
  const syncedEvent = syncDexie.outbox.find(e => e.id === newOutbox.id);
  console.log(`Outbox Event Status: ${syncedEvent.sync_status} (Expected SYNCED)`);

  const backendInvResp2 = await fetch('http://127.0.0.1:8000/api/inventory?station_id=BHARATI');
  const backendInv2 = await backendInvResp2.json();
  const backendJetA1_2 = backendInv2.find(i => i.name === 'Jet-A1 Fuel');
  console.log(`Backend Jet-A1 Fuel Quantity: ${backendJetA1_2.quantity} (Expected 49800)`);
  fs.writeFileSync('test3_dexie.json', JSON.stringify(syncDexie, null, 2));

  console.log("\n--- TEST 4: Field checkout/check-in ---");
  await page.evaluate(() => {
    document.evaluate("//button[contains(., 'New Field Checkout')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();
  });
  await new Promise(r => setTimeout(r, 500));
  
  await page.evaluate(() => {
    const checkboxes = document.querySelectorAll('.personnel-item input[type="checkbox"]');
    checkboxes[0].click();
    checkboxes[1].click();
    document.querySelector('.checkout-form input[type="datetime-local"]').value = '2026-09-06T10:00';
    document.querySelector('.checkout-form button[type="submit"]').click();
  });
  await new Promise(r => setTimeout(r, 500));
  
  const checkoutDexie = await getDexieDump();
  console.log(`Active Missions: ${checkoutDexie.missions.length}`);
  console.log(`Personnel on FIELD_MISSION: ${checkoutDexie.personnel.filter(p => p.status === 'FIELD_MISSION').length}`);
  
  await page.evaluate(() => document.querySelector('.btn-sync').click());
  await new Promise(r => setTimeout(r, 1000));
  
  const backendPersonnelResp = await fetch('http://127.0.0.1:8000/api/personnel?station_id=BHARATI');
  const backendPersonnelData = await backendPersonnelResp.json();
  console.log(`Backend Active Missions: ${backendPersonnelData.active_missions.length}`);
  console.log(`Backend Personnel on FIELD_MISSION: ${backendPersonnelData.personnel.filter(p => p.status === 'FIELD_MISSION').length}`);
  fs.writeFileSync('test4_checkout_dexie.json', JSON.stringify(checkoutDexie, null, 2));

  page.on('dialog', async dialog => {
    await dialog.accept();
  });

  await page.evaluate(() => document.querySelector('.btn-checkin').click());
  await new Promise(r => setTimeout(r, 500));

  const checkinDexie = await getDexieDump();
  console.log(`Active Missions after checkin: ${checkinDexie.missions.length}`);
  
  await page.evaluate(() => document.querySelector('.btn-sync').click());
  await new Promise(r => setTimeout(r, 1000));
  
  const backendPersonnelResp2 = await fetch('http://127.0.0.1:8000/api/personnel?station_id=BHARATI');
  const backendPersonnelData2 = await backendPersonnelResp2.json();
  console.log(`Backend Active Missions after checkin: ${backendPersonnelData2.active_missions.length}`);

  console.log("\n--- TEST 5: Sneakernet ---");
  await page.setOfflineMode(true);
  
  await page.evaluate(() => document.querySelector('.btn-muster').click());
  await new Promise(r => setTimeout(r, 200));
  await page.evaluate(() => document.querySelector('.btn-muster-confirm').click());
  await new Promise(r => setTimeout(r, 500));
  
  const finalDexie = await getDexieDump();
  const pendingEvents = finalDexie.outbox.filter(e => e.sync_status === 'PENDING');
  fs.writeFileSync('sneakernet_pending.json', JSON.stringify(pendingEvents));

  console.log("Done frontend puppeteer tasks.");
  await browser.close();
}
runTests().catch(console.error);
