const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  const roles = [
    { username: 'maitri_leader', role: 'STATION_LEADER' },
    { username: 'maitri_logistics', role: 'LOGISTICS_ENGINEERING_OFFICER' },
    { username: 'maitri_scientist', role: 'CHIEF_SCIENTIST' },
    { username: 'maitri_medical', role: 'MEDICAL_OFFICER' },
    { username: 'maitri_field', role: 'FIELD_TEAM_MEMBER' }
  ];
  
  const results = [];
  
  for (const r of roles) {
      await page.goto('http://localhost:4173');
      await page.evaluate(() => { window.sessionStorage.clear(); });
      await page.goto('http://localhost:4173');
      
      try {
          await page.waitForSelector('#username');
          await page.type('#username', r.username);
          await page.type('#password', 'maitri_password');
          await page.select('#station', 'MAITRI');
          await page.select('#role', r.role);
          await page.click('button[type="submit"]');
          
          await page.waitForSelector('.header-status');
          const hasSync = await page.evaluate(() => {
              return document.querySelector('.btn-sync') !== null;
          });
          results.push(`${r.role} -> Force Sync visible: ${hasSync}`);
      } catch (err) {
          results.push(`${r.role} -> Error: ${err.message}`);
      }
  }
  
  console.log(results.join('\n'));
  fs.writeFileSync('test_sync_visibility.txt', results.join('\n'));
  await browser.close();
})();
