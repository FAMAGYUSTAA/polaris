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
    
    // Wait for Cargo Tracking
    await page.waitForSelector('h2');
    
    console.log("Clicking New Shipment...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const newShipment = btns.find(b => b.textContent.includes('New Shipment'));
        if(newShipment) newShipment.click();
    });
    
    await page.waitForSelector('input[placeholder="e.g. IL-76 Flight"]');
    
    // Real valid shipment
    await page.evaluate(() => {
       const setVal = (el, val) => {
           const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
           setter.call(el, val);
           el.dispatchEvent(new Event('input', { bubbles: true }));
           el.dispatchEvent(new Event('change', { bubbles: true }));
       };
       
       const inputs = document.querySelectorAll('input');
       setVal(inputs[0], 'Test Flight 1');
       setVal(inputs[1], 'Test Origin 1');
       setVal(inputs[2], '2026-09-01T10:00');
       setVal(inputs[3], '2026-09-07T12:00');
       setVal(inputs[4], 'FUEL-JA1-001'); // sku
       setVal(inputs[5], 'Jet A1'); // name
       setVal(inputs[6], '1000'); // qty
       setVal(inputs[7], 'L'); // unit
       
       const btns = Array.from(document.querySelectorAll('button'));
       btns.find(b => b.textContent.includes('Create Shipment')).click();
    });
    
    await new Promise(r => setTimeout(r, 2000));
    
    const text = await page.content();
    if(text.includes('Test Flight 1') && text.includes('IN_TRANSIT')) {
       console.log("[UI] Shipment is IN_TRANSIT! (Success)");
    } else {
       console.log("[UI] Shipment not found.");
    }
    
    console.log("Clicking Mark Arrived...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        const ma = btns.find(b => b.textContent.includes('Mark Arrived'));
        if(ma) ma.click();
    });
    
    await new Promise(r => setTimeout(r, 2000));
    const postArrived = await page.content();
    if(postArrived.includes('Shipment marked arrived — inventory updated.')) {
        console.log("[UI] Success notification shown! (Success)");
    }
    if(postArrived.includes('ARRIVED')) {
        console.log("[UI] Shipment status changed to ARRIVED! (Success)");
    }
    
    // Check asset inventory for FUEL-JA1-001
    await new Promise(r => setTimeout(r, 2000));
    console.log("Checking Asset Inventory UI...");
    const assetSection = await page.evaluate(() => {
        const h2 = Array.from(document.querySelectorAll('h2')).find(el => el.textContent.includes('Asset Inventory'));
        return h2 ? h2.parentElement.innerText : 'Not found';
    });
    console.log("Assets text:");
    console.log(assetSection);
    
    await page.waitForSelector('input[placeholder="e.g. IL-76 Flight"]');
    await page.evaluate(() => {
       const setVal = (el, val) => {
           const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
           setter.call(el, val);
           el.dispatchEvent(new Event('input', { bubbles: true }));
           el.dispatchEvent(new Event('change', { bubbles: true }));
       };
       
       const inputs = document.querySelectorAll('input');
       setVal(inputs[0], 'Test Flight FAKE');
       setVal(inputs[1], 'Test Origin 2');
       setVal(inputs[2], '2026-09-01T10:00');
       setVal(inputs[3], '2026-09-07T12:00');
       setVal(inputs[4], 'FAKE-001'); // sku
       setVal(inputs[5], 'Fake Item'); // name
       setVal(inputs[6], '100'); // qty
       setVal(inputs[7], 'kg'); // unit
       
       const btns = Array.from(document.querySelectorAll('button'));
       btns.find(b => b.textContent.includes('Create Shipment')).click();
    });
    
    await new Promise(r => setTimeout(r, 2000));
    console.log("Clicking Mark Arrived (fake)...");
    await page.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('button'));
        // Find the second one if the first one is disappeared
        const ma = btns.filter(b => b.textContent.includes('Mark Arrived'))[0];
        if(ma) ma.click();
    });
    
    await new Promise(r => setTimeout(r, 2000));
    const postFake = await page.content();
    if(postFake.includes('Warning: Some SKUs were unmatched:')) {
        console.log("[UI] Warning notification shown for fake SKU! (Success)");
    }
    
    await browser.close();
  } catch(e) {
    console.error("Error:", e);
    process.exit(1);
  }
})();
