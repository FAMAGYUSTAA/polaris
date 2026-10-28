const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  let errors = [];
  page.on('console', msg => {
      if (msg.type() === 'error') {
          errors.push(msg.text());
      }
  });

  const roles = [
    { username: 'maitri_leader', role: 'STATION_LEADER' },
    { username: 'maitri_logistics', role: 'LOGISTICS_ENGINEERING_OFFICER' },
    { username: 'maitri_scientist', role: 'CHIEF_SCIENTIST' },
    { username: 'maitri_medical', role: 'MEDICAL_OFFICER' },
    { username: 'maitri_field', role: 'FIELD_TEAM_MEMBER' }
  ];
  
  const results = [];
  
  for (const r of roles) {
      await page.goto('http://localhost:4173/');
      await page.evaluate(() => { window.sessionStorage.clear(); });
      await page.goto('http://localhost:4173/');
      
      try {
          await page.waitForSelector('#username');
          await page.type('#username', r.username);
          await page.type('#password', 'maitri_password');
          await page.select('#station', 'MAITRI');
          await page.select('#role', r.role);
          await page.click('button[type="submit"]');
          
          await page.waitForSelector('.app-root');
          
          // Wait to see if components mount without error
          await new Promise(r => setTimeout(r, 1000));
          
          const hasSync = await page.evaluate(() => {
              return document.querySelector('.btn-sync-header') !== null;
          });
          
          results.push(`${r.role} -> Force Sync visible: ${hasSync}`);
      } catch (err) {
          results.push(`${r.role} -> Error: ${err.message}`);
      }
  }
  
  console.log(results.join('\n'));
  console.log("Console Errors:", errors);
  fs.writeFileSync('test_ui_redesign.txt', results.join('\n') + "\nErrors:\n" + errors.join('\n'));
  await browser.close();
})();
