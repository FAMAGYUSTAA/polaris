import puppeteer from 'puppeteer';

(async () => {
  try {
    const browser = await puppeteer.launch({
      headless: "new",
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    page.on("console", msg => console.log("PAGE LOG:", msg.text()));
    
    async function doLogin(station, user, pass, role) {
      await page.goto('http://localhost:4173', { waitUntil: 'networkidle0' });
      await page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
      await page.goto('http://localhost:4173', { waitUntil: 'networkidle0' });

      const hasLogout = await page.evaluate(() => {
          const l = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Logout'));
          if (l) { l.click(); return true; }
          return false;
      });
      if(hasLogout) await new Promise(r => setTimeout(r, 1000));

      await page.waitForSelector('input[type="text"]');
      
      await page.evaluate((station, user, pass, role) => {
         const setVal = (el, val) => {
             const setter = Object.getOwnPropertyDescriptor(el.constructor.prototype, "value").set;
             setter.call(el, val);
             el.dispatchEvent(new Event('change', { bubbles: true }));
             el.dispatchEvent(new Event('input', { bubbles: true }));
         };
         
         const selects = document.querySelectorAll('select');
         setVal(selects[0], station);
         setVal(selects[1], role);
         
         const inputs = document.querySelectorAll('input');
         setVal(inputs[0], user);
         setVal(inputs[1], pass);
         
         const btns = Array.from(document.querySelectorAll('button'));
         btns.find(b => b.textContent.includes('Sign In')).click();
      }, station, user, pass, role);
      
      await new Promise(r => setTimeout(r, 1500));
      return await page.content();
    }
    
    // warm up run to avoid the initialization glitch
    await doLogin('BHARATI', 'bharati_leader', 'bharati_password', 'STATION_LEADER');
    
    console.log("Test 1: bharati_leader + bharati_password + Bharati + Station Leader -> succeeds");
    let res = await doLogin('BHARATI', 'bharati_leader', 'bharati_password', 'STATION_LEADER');
    if (res.includes('Station Overview') || res.includes('Logout')) console.log("  [PASS]");
    else console.log("  [FAIL] \n" + res.substring(0, 100));
    
    console.log("Test 2: bharati_medical + bharati_password + Bharati + Medical Officer -> succeeds");
    res = await doLogin('BHARATI', 'bharati_medical', 'bharati_password', 'MEDICAL_OFFICER');
    if (res.includes('Logout')) console.log("  [PASS]");
    else console.log("  [FAIL] \n" + res.substring(0, 100));
    
    console.log("Test 3: maitri_scientist + maitri_password + Maitri + Chief Scientist -> succeeds");
    res = await doLogin('MAITRI', 'maitri_scientist', 'maitri_password', 'CHIEF_SCIENTIST');
    if (res.includes('Logout')) console.log("  [PASS]");
    else console.log("  [FAIL] \n" + res.substring(0, 100));
    
    console.log("Test 4: himadri_field + himadri_password + Himadri + Field Team Member -> succeeds");
    res = await doLogin('HIMADRI', 'himadri_field', 'himadri_password', 'FIELD_TEAM_MEMBER');
    if (res.includes('Logout')) console.log("  [PASS]");
    else console.log("  [FAIL] \n" + res.substring(0, 100));
    
    console.log("Test 5: bharati_leader + Bharati + Medical Officer -> rejected");
    res = await doLogin('BHARATI', 'bharati_leader', 'bharati_password', 'MEDICAL_OFFICER');
    if (res.includes('Selected role does not match')) console.log("  [PASS]");
    else console.log("  [FAIL] \n" + res.substring(0, 100));
    
    console.log("Test 6: bharati_leader + Maitri + Station Leader -> rejected");
    res = await doLogin('MAITRI', 'bharati_leader', 'bharati_password', 'STATION_LEADER');
    if (res.includes('is not authorized for station') || res.includes('Incorrect username')) console.log("  [PASS]");
    else console.log("  [FAIL] \n" + res.substring(0, 100));

    await browser.close();
  } catch(e) {
    console.error(e);
    process.exit(1);
  }
})();
