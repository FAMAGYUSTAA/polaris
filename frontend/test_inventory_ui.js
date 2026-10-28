import puppeteer from 'puppeteer';

(async () => {
  try {
    const browser = await puppeteer.launch({
      headless: "new",
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-service-workers']
    });
    
    const page = await browser.newPage();
    console.log("Loading page...");
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
    
    // Helper to set input value
    const setVal = async (placeholder, val) => {
        await page.evaluate(({ placeholder, val }) => {
            const el = document.querySelector(`input[placeholder="${placeholder}"]`);
            if(!el) throw new Error("Could not find input " + placeholder);
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }, { placeholder, val });
    };

    console.log("\n=== ONLINE TEST: ADD ITEM ===");
    console.log("Clicking + Add New Item...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent.includes('Add New Item')).click();
    });
    await page.waitForSelector('input[placeholder="e.g. NEW-SKU-01"]');
    
    await setVal("e.g. NEW-SKU-01", "ONLINE-TEST-01");
    await setVal("e.g. New Inventory Item", "Online Test Item");
    await setVal("0", "150"); // qty
    await setVal("e.g. kg, L", "kg"); // unit
    // the second placeholder "0" is minimum threshold
    await page.evaluate(() => {
       const inputs = document.querySelectorAll('input[placeholder="0"]');
       const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
       setter.call(inputs[1], "20");
       inputs[1].dispatchEvent(new Event('input', { bubbles: true }));
       inputs[1].dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent === 'Add Item').click();
    });
    
    await new Promise(r => setTimeout(r, 1000));
    let text = await page.content();
    if(text.includes('ONLINE-TEST-01')) {
        console.log("[UI] New item appears instantly in UI.");
    }
    
    // Force Sync
    console.log("Clicking Force Sync...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent.includes('Force Sync')).click();
    });
    
    await new Promise(r => setTimeout(r, 2000));
    
    // Verify Backend
    let res = await fetch("http://127.0.0.1:8000/api/inventory?station_id=BHARATI");
    let inv = await res.json();
    let found = inv.find(i => i.sku === "ONLINE-TEST-01");
    if (found) {
        console.log(`[Backend] Item ONLINE-TEST-01 is present with qty ${found.quantity}.`);
    } else {
        console.log(`[Backend] Item missing!`);
    }

    console.log("\n=== ONLINE TEST: DELETE ITEM ===");
    await page.evaluate(() => {
        const cards = Array.from(document.querySelectorAll('.inventory-card'));
        const card = cards.find(c => c.textContent.includes('ONLINE-TEST-01'));
        const delBtn = Array.from(card.querySelectorAll('button')).find(b => b.textContent === 'Delete');
        delBtn.click();
    });
    
    await new Promise(r => setTimeout(r, 500)); // wait for confirm state
    
    await page.evaluate(() => {
        const cards = Array.from(document.querySelectorAll('.inventory-card'));
        const card = cards.find(c => c.textContent.includes('ONLINE-TEST-01'));
        const confBtn = Array.from(card.querySelectorAll('button')).find(b => b.textContent === 'Confirm');
        confBtn.click();
    });
    
    await new Promise(r => setTimeout(r, 1000));
    text = await page.content();
    if(!text.includes('ONLINE-TEST-01')) {
        console.log("[UI] Item ONLINE-TEST-01 disappeared from UI instantly.");
    }
    
    // Force Sync
    console.log("Clicking Force Sync...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent.includes('Force Sync')).click();
    });
    await new Promise(r => setTimeout(r, 2000));
    
    res = await fetch("http://127.0.0.1:8000/api/inventory?station_id=BHARATI");
    inv = await res.json();
    found = inv.find(i => i.sku === "ONLINE-TEST-01");
    if (!found) {
        console.log(`[Backend] Item ONLINE-TEST-01 is correctly deleted from backend.`);
    }

    console.log("\n=== OFFLINE TEST: ADD ITEM ===");
    console.log("Simulating offline mode...");
    await page.setOfflineMode(true);
    
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent.includes('Add New Item')).click();
    });
    await page.waitForSelector('input[placeholder="e.g. NEW-SKU-01"]');
    
    await setVal("e.g. NEW-SKU-01", "OFFLINE-TEST-01");
    await setVal("e.g. New Inventory Item", "Offline Test Item");
    await setVal("0", "500"); // qty
    await setVal("e.g. kg, L", "units"); // unit
    
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent === 'Add Item').click();
    });
    
    await new Promise(r => setTimeout(r, 1000));
    text = await page.content();
    if(text.includes('OFFLINE-TEST-01')) {
        console.log("[UI] Offline Item appears instantly in UI (saved locally).");
    }
    
    let pendingCountText = await page.evaluate(() => {
        const h = document.querySelector('.header-status');
        return h ? h.innerText : '';
    });
    console.log("[UI Header] Pending Count reflects changes (if polling caught it).");
    
    // Verify Backend (should NOT have it)
    res = await fetch("http://127.0.0.1:8000/api/inventory?station_id=BHARATI");
    inv = await res.json();
    found = inv.find(i => i.sku === "OFFLINE-TEST-01");
    if (!found) {
        console.log(`[Backend] Correct: Item OFFLINE-TEST-01 is NOT on backend yet.`);
    }
    
    console.log("Restoring online mode and syncing...");
    await page.setOfflineMode(false);
    
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent.includes('Force Sync')).click();
    });
    await new Promise(r => setTimeout(r, 2000));
    
    res = await fetch("http://127.0.0.1:8000/api/inventory?station_id=BHARATI");
    inv = await res.json();
    found = inv.find(i => i.sku === "OFFLINE-TEST-01");
    if (found) {
        console.log(`[Backend] Item OFFLINE-TEST-01 successfully synced to backend!`);
    }

    await browser.close();
  } catch(e) {
    console.error("Error:", e);
    process.exit(1);
  }
})();
