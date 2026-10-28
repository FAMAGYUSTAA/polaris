import puppeteer from 'puppeteer';

(async () => {
  try {
    const browser = await puppeteer.launch({
      headless: "new",
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    // Setup test data
    console.log("Setting up Cargo test data...");
    await fetch("http://127.0.0.1:8000/api/cargo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            station_id: "BHARATI",
            carrier_name: "Test Icebreaker",
            origin: "Cape Town",
            departure_date: new Date().toISOString(),
            expected_arrival: new Date(Date.now() + 86400000 * 5).toISOString(),
            manifest: []
        })
    });
    
    console.log("Setting up Muster test data (via sync)...");
    const uuid = crypto.randomUUID();
    await fetch("http://127.0.0.1:8000/api/sync/delta", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            events: [{
                id: uuid,
                station_id: "BHARATI",
                event_type: "MUSTER_TRIGGERED",
                payload: { reason: "HQ Dashboard Muster Test" },
                timestamp: new Date().toISOString()
            }]
        })
    });

    const page = await browser.newPage();
    console.log("Loading HQ Dashboard...");
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle0' });
    
    // Wait for the components to fetch and render
    await new Promise(r => setTimeout(r, 2000));
    
    console.log("\n=== 1. FreshnessIndicator ===");
    let content = await page.content();
    if (content.includes("Bharati Station Connection") && (content.includes("STALE") || content.includes("ONLINE"))) {
        console.log("✔ FreshnessIndicator loaded successfully.");
    } else {
        console.log("❌ FreshnessIndicator missing or malformed.");
    }
    
    console.log("\n=== 2. CargoApprovalPanel ===");
    if (content.includes("Test Icebreaker") && content.includes("PENDING")) {
        console.log("✔ Cargo pending shipment found.");
    } else {
        console.log("❌ Cargo pending shipment NOT found.");
    }
    
    console.log("Clicking Approve Shipment...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const ackBtn = btns.find(b => b.textContent.includes('Approve Shipment') && b.closest('.panel').textContent.includes('Test Icebreaker'));
        if(ackBtn) ackBtn.click();
    });
    await new Promise(r => setTimeout(r, 2000));
    content = await page.content();
    if (!content.includes("Approve Shipment") && content.includes("Test Icebreaker") && !content.includes("PENDING")) {
        console.log("✔ Cargo shipment successfully approved (moved out of pending list).");
    } else {
        console.log("❌ Cargo shipment still in pending list or approval failed.");
    }
    
    console.log("\n=== 3. MusterAlerts ===");
    if (content.includes("EMERGENCY MUSTER TRIGGERED") && content.includes("HQ Dashboard Muster Test")) {
        console.log("✔ Muster Alert displayed correctly with red alarming banner.");
    } else {
        console.log("❌ Muster Alert missing.");
    }

    console.log("\n=== 4. DirectiveComposer ===");
    console.log("Typing and submitting a new directive...");
    
    // Use page.type for React
    await page.type('textarea', 'Automated Test Directive from Puppeteer');
    await new Promise(r => setTimeout(r, 500));
    
    await page.evaluate(() => {
        const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Send Directive'));
        if(btn) btn.click();
    });
    
    await new Promise(r => setTimeout(r, 2000));
    content = await page.content();
    if (content.includes("Automated Test Directive from Puppeteer") && content.includes("Awaiting Acknowledgment")) {
        console.log("✔ Directive successfully sent and appears in the sent list.");
    } else {
        console.log("❌ Directive did not appear in sent list.");
    }

    await browser.close();
  } catch(e) {
    console.error("Error:", e);
    process.exit(1);
  }
})();
