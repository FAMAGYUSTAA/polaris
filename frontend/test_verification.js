import puppeteer from 'puppeteer';
import crypto from 'crypto';

(async () => {
  try {
    const browser = await puppeteer.launch({
      headless: "new",
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    console.log("=== API Verification ===");
    // 1. Create a fresh directive
    const postDir = await fetch("http://127.0.0.1:8000/api/directives", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            station_id: "BHARATI",
            message: "Verify timezone fix!",
            issued_by: "HQ"
        })
    });
    const newDir = await postDir.json();
    console.log("Raw POST response issued_at:", newDir.issued_at);
    
    // 2. Fetch Personnel and use first one
    const pRes = await fetch("http://127.0.0.1:8000/api/personnel?station_id=BHARATI");
    const pData = await pRes.json();
    const alice = pData.personnel[0];
    
    const expectedReturn = new Date(Date.now() + 1000 * 60 * 30).toISOString(); // +30 minutes
    const fmUUID = crypto.randomUUID();
    await fetch("http://127.0.0.1:8000/api/sync/delta", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            events: [{
                id: fmUUID,
                station_id: "BHARATI",
                event_type: "FIELD_CHECKOUT",
                payload: {
                    team_lead: alice.id,
                    expected_return: expectedReturn
                },
                timestamp: new Date().toISOString()
            }]
        })
    });
    console.log(`Created FIELD_CHECKOUT with expected_return = ${expectedReturn}`);

    // 3. Trigger a fresh muster event
    const musterUUID = crypto.randomUUID();
    await fetch("http://127.0.0.1:8000/api/sync/delta", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            events: [{
                id: musterUUID,
                station_id: "BHARATI",
                event_type: "MUSTER_TRIGGERED",
                payload: { reason: "Timezone Fix Muster" },
                timestamp: new Date().toISOString()
            }]
        })
    });
    console.log("Triggered fresh muster.");

    // --- FRONTEND VERIFICATION --- //

    console.log("\n=== Station Dashboard (5173) ===");
    const pageStation = await browser.newPage();
    await pageStation.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 2000));
    
    let contentStation = await pageStation.content();
    
    // Acknowledge Directive
    console.log("Acknowledging directive...");
    await pageStation.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const ackBtn = btns.find(b => {
             const parent = b.parentElement.parentElement;
             return b.textContent.includes('Acknowledge') && parent && parent.textContent.includes('Verify timezone fix!');
        });
        if(ackBtn) ackBtn.click();
    });
    await new Promise(r => setTimeout(r, 1000));
    contentStation = await pageStation.content();
    
    if (contentStation.includes("Acknowledged ")) {
        console.log("✔ Directive acknowledged successfully on station.");
        const match = contentStation.match(/Acknowledged\s+([\d]{1,2}\/[\d]{1,2}\/[\d]{4}.*?(?:AM|PM))/s);
        if (match) console.log("Station UI displays acknowledged time:", match[1].trim());
    } else {
        console.log("❌ Failed to acknowledge directive on station.");
    }
    
    // Check PersonnelTracker Overdue logic
    if (contentStation.includes(alice.full_name) && contentStation.includes("OVERDUE")) {
         console.log(`❌ Test mission falsely flagged as OVERDUE for ${alice.full_name}!`);
    } else if (contentStation.includes(alice.full_name)) {
         console.log(`✔ Test mission correctly displays as active, NOT overdue for ${alice.full_name}.`);
    } else {
         console.log(`❌ Test mission not found on UI for ${alice.full_name}.`);
    }

    console.log("\n=== HQ Dashboard (5174) ===");
    const pageHQ = await browser.newPage();
    await pageHQ.goto('http://localhost:5174', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 2000));
    
    let contentHQ = await pageHQ.content();
    
    // Check Muster
    if (contentHQ.includes("Timezone Fix Muster")) {
        console.log("✔ Fresh muster event correctly loaded in HQ.");
        const match = contentHQ.match(/Timezone Fix Muster.*?([\d]{1,2}\/[\d]{1,2}\/[\d]{4}.*?(?:AM|PM))/s);
        if (match) console.log("HQ UI displays muster time:", match[1].trim());
    } else {
        console.log("❌ Muster event missing in HQ.");
    }

    await browser.close();
  } catch(e) {
    console.error("Error:", e);
    process.exit(1);
  }
})();
