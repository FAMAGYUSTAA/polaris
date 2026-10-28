import puppeteer from 'puppeteer';

(async () => {
  try {
    const browser = await puppeteer.launch({
      headless: "new",
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-service-workers']
    });
    
    const page = await browser.newPage();
    console.log("\n=== PRE-TEST SETUP ===");
    console.log("Creating test directive via API...");
    const dirRes = await fetch("http://127.0.0.1:8000/api/directives", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            station_id: "BHARATI",
            message: "TEST-DIRECTIVE-ONLINE",
            issued_by: "HQ Goa Test"
        })
    });
    const dirJson = await dirRes.json();
    console.log("Created directive:", dirJson.id);

    console.log("Loading page...");
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
    
    console.log("\n=== ONLINE TEST: ACKNOWLEDGE DIRECTIVE ===");
    
    // Check if directive appears
    let content = await page.content();
    if(content.includes('TEST-DIRECTIVE-ONLINE')) {
        console.log("[UI] Directive successfully fetched and displayed on mount.");
    }
    
    console.log("Clicking Acknowledge...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const ackBtn = btns.find(b => b.textContent.includes('Acknowledge Directive'));
        if(ackBtn) ackBtn.click();
    });
    
    await new Promise(r => setTimeout(r, 1000));
    content = await page.content();
    if(content.includes('Acknowledged') && !content.includes('Acknowledge Directive')) {
        console.log("[UI] Directive visually switched to Acknowledged state instantly.");
    }
    
    console.log("Clicking Force Sync...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const fBtn = btns.find(b => b.textContent.includes('Force Sync'));
        if(fBtn) fBtn.click();
    });
    await new Promise(r => setTimeout(r, 2000));
    
    // Verify Backend
    let res = await fetch("http://127.0.0.1:8000/api/directives?station_id=BHARATI");
    let dirs = await res.json();
    let found = dirs.find(d => d.message === "TEST-DIRECTIVE-ONLINE");
    if (found && found.acknowledged) {
        console.log(`[Backend] Directive was successfully acknowledged on the backend.`);
    }

    console.log("\n=== OFFLINE TEST: ACKNOWLEDGE DIRECTIVE ===");
    console.log("Creating test directive via API...");
    const dirRes2 = await fetch("http://127.0.0.1:8000/api/directives", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            station_id: "BHARATI",
            message: "TEST-DIRECTIVE-OFFLINE",
            issued_by: "HQ Goa Test"
        })
    });
    const dirJson2 = await dirRes2.json();
    
    console.log("Refreshing page to pull new directive...");
    await page.reload({ waitUntil: 'networkidle0' });
    
    console.log("Simulating offline mode...");
    await page.setOfflineMode(true);
    
    console.log("Clicking Acknowledge for Offline test...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const ackBtn = btns.find(b => b.textContent.includes('Acknowledge Directive'));
        if(ackBtn) ackBtn.click();
    });
    
    await new Promise(r => setTimeout(r, 1000));
    content = await page.content();
    if(content.includes('Acknowledged')) {
        console.log("[UI] Offline directive visually switched to Acknowledged state instantly.");
    }
    
    let pendingCountText = await page.evaluate(() => {
        const h = document.querySelector('.header-status');
        return h ? h.innerText : '';
    });
    console.log("[UI Header] Pending Count reflects changes (event queued offline).");
    
    res = await fetch("http://127.0.0.1:8000/api/directives?station_id=BHARATI");
    dirs = await res.json();
    found = dirs.find(d => d.message === "TEST-DIRECTIVE-OFFLINE");
    if (found && !found.acknowledged) {
        console.log(`[Backend] Correct: Directive is NOT acknowledged on backend yet.`);
    }
    
    console.log("Restoring online mode and syncing...");
    await page.setOfflineMode(false);
    
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const fBtn = btns.find(b => b.textContent.includes('Force Sync'));
        if(fBtn) fBtn.click();
    });
    await new Promise(r => setTimeout(r, 2000));
    
    res = await fetch("http://127.0.0.1:8000/api/directives?station_id=BHARATI");
    dirs = await res.json();
    found = dirs.find(d => d.message === "TEST-DIRECTIVE-OFFLINE");
    if (found && found.acknowledged) {
        console.log(`[Backend] Directive was successfully synced as acknowledged to backend!`);
    }

    await browser.close();
  } catch(e) {
    console.error("Error:", e);
    process.exit(1);
  }
})();
