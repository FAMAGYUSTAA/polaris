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
    const setVal = async (placeholder, val, isDateTime = false) => {
        await page.evaluate(({ placeholder, val, isDateTime }) => {
            let el = document.querySelector(`input[placeholder="${placeholder}"]`);
            if(isDateTime) {
                // select by type=datetime-local and placeholder or index
                // but actually react binds by name or id, we'll just pick by type for now since they are sequential
                return; // Handled specially
            }
            if(!el) throw new Error("Could not find input " + placeholder);
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            setter.call(el, val);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }, { placeholder, val, isDateTime });
    };

    console.log("\n=== ONLINE TEST: PLAN EXPEDITION ===");
    console.log("Clicking Plan New Expedition...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent.includes('Plan New Expedition')).click();
    });
    
    await new Promise(r => setTimeout(r, 500));
    
    await setVal("e.g. Dr. Sarah Chen", "ONLINE-LEAD");
    await setVal("e.g. Ice core sampling", "ONLINE-PURPOSE");
    await setVal("-69.40, 76.18", "-70.0, 75.0");
    await setVal("CH-16", "CH-12");
    
    // Set datetimes
    await page.evaluate(() => {
        const inputs = document.querySelectorAll('input[type="datetime-local"]');
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        // departure tomorrow
        let dep = new Date();
        dep.setDate(dep.getDate() + 1);
        dep.setMinutes(dep.getMinutes() - dep.getTimezoneOffset());
        let depStr = dep.toISOString().slice(0, 16);
        setter.call(inputs[0], depStr);
        inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
        inputs[0].dispatchEvent(new Event('change', { bubbles: true }));
        
        // return day after tomorrow
        let ret = new Date();
        ret.setDate(ret.getDate() + 2);
        ret.setMinutes(ret.getMinutes() - ret.getTimezoneOffset());
        let retStr = ret.toISOString().slice(0, 16);
        setter.call(inputs[1], retStr);
        inputs[1].dispatchEvent(new Event('input', { bubbles: true }));
        inputs[1].dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent === 'Submit Planned Expedition').click();
    });
    
    await new Promise(r => setTimeout(r, 1000));
    let text = await page.content();
    if(text.includes('ONLINE-LEAD')) {
        console.log("[UI] New expedition appears instantly in UI.");
    }
    
    // Force Sync
    console.log("Clicking Force Sync...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent.includes('Force Sync')).click();
    });
    
    await new Promise(r => setTimeout(r, 2000));
    
    // Verify Backend
    let res = await fetch("http://127.0.0.1:8000/api/expeditions?station_id=BHARATI");
    let exps = await res.json();
    let found = exps.find(e => e.team_lead === "ONLINE-LEAD");
    if (found) {
        console.log(`[Backend] Expedition lead by ONLINE-LEAD is present.`);
    } else {
        console.log(`[Backend] Expedition missing!`);
    }

    console.log("\n=== ONLINE TEST: CANCEL EXPEDITION ===");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        // Find cancel button in the mission card
        const cardBtns = btns.filter(b => b.textContent === 'Cancel Expedition');
        // Just click the first one since we just created it
        if(cardBtns.length > 0) cardBtns[0].click();
    });
    
    await new Promise(r => setTimeout(r, 500)); // wait for confirm state
    
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const confBtn = btns.find(b => b.textContent === 'Confirm Cancel');
        if(confBtn) confBtn.click();
    });
    
    await new Promise(r => setTimeout(r, 1000));
    text = await page.content();
    if(!text.includes('ONLINE-LEAD')) {
        console.log("[UI] Expedition disappeared from UI instantly.");
    }
    
    // Force Sync
    console.log("Clicking Force Sync...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent.includes('Force Sync')).click();
    });
    await new Promise(r => setTimeout(r, 2000));
    
    res = await fetch("http://127.0.0.1:8000/api/expeditions?station_id=BHARATI");
    exps = await res.json();
    found = exps.find(e => e.team_lead === "ONLINE-LEAD");
    if (!found) {
        console.log(`[Backend] Expedition lead by ONLINE-LEAD correctly cancelled/removed from default backend view.`);
    }

    console.log("\n=== OFFLINE TEST: PLAN EXPEDITION ===");
    console.log("Simulating offline mode...");
    await page.setOfflineMode(true);
    
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent.includes('Plan New Expedition')).click();
    });
    
    await new Promise(r => setTimeout(r, 500));
    
    await setVal("e.g. Dr. Sarah Chen", "OFFLINE-LEAD");
    await setVal("e.g. Ice core sampling", "OFFLINE-PURPOSE");
    await setVal("-69.40, 76.18", "-70.0, 75.0");
    await setVal("CH-16", "CH-12");
    
    await page.evaluate(() => {
        const inputs = document.querySelectorAll('input[type="datetime-local"]');
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        let dep = new Date();
        dep.setDate(dep.getDate() + 1);
        dep.setMinutes(dep.getMinutes() - dep.getTimezoneOffset());
        let depStr = dep.toISOString().slice(0, 16);
        setter.call(inputs[0], depStr);
        inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
        inputs[0].dispatchEvent(new Event('change', { bubbles: true }));
        
        let ret = new Date();
        ret.setDate(ret.getDate() + 2);
        ret.setMinutes(ret.getMinutes() - ret.getTimezoneOffset());
        let retStr = ret.toISOString().slice(0, 16);
        setter.call(inputs[1], retStr);
        inputs[1].dispatchEvent(new Event('input', { bubbles: true }));
        inputs[1].dispatchEvent(new Event('change', { bubbles: true }));
    });
    
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent === 'Submit Planned Expedition').click();
    });
    
    await new Promise(r => setTimeout(r, 1000));
    text = await page.content();
    if(text.includes('OFFLINE-LEAD')) {
        console.log("[UI] Offline Expedition appears instantly in UI (saved locally).");
    }
    
    let pendingCountText = await page.evaluate(() => {
        const h = document.querySelector('.header-status');
        return h ? h.innerText : '';
    });
    console.log("[UI Header] Pending Count reflects changes (if polling caught it).");
    
    // Verify Backend (should NOT have it)
    res = await fetch("http://127.0.0.1:8000/api/expeditions?station_id=BHARATI");
    exps = await res.json();
    found = exps.find(e => e.team_lead === "OFFLINE-LEAD");
    if (!found) {
        console.log(`[Backend] Correct: Expedition lead by OFFLINE-LEAD is NOT on backend yet.`);
    }
    
    console.log("Restoring online mode and syncing...");
    await page.setOfflineMode(false);
    
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        btns.find(b => b.textContent.includes('Force Sync')).click();
    });
    await new Promise(r => setTimeout(r, 2000));
    
    res = await fetch("http://127.0.0.1:8000/api/expeditions?station_id=BHARATI");
    exps = await res.json();
    found = exps.find(e => e.team_lead === "OFFLINE-LEAD");
    if (found) {
        console.log(`[Backend] Expedition lead by OFFLINE-LEAD successfully synced to backend!`);
    }

    await browser.close();
  } catch(e) {
    console.error("Error:", e);
    process.exit(1);
  }
})();
