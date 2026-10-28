const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  await page.goto('http://localhost:4173');
  
  // Login as logistics to have DATA_SYNC
  await page.type('#username', 'maitri_logistics');
  await page.type('#password', 'maitri_password');
  await page.select('#station', 'MAITRI');
  await page.select('#role', 'LOGISTICS_ENGINEERING_OFFICER');
  await page.click('button[type="submit"]');
  
  await page.waitForSelector('.header-status');
  
  const html = await page.evaluate(() => document.querySelector('.header-status').innerHTML);
  console.log("HEADER HTML FOR LOGISTICS:");
  console.log(html);
  
  // Wait, logistics can't cancel expeditions!
  // Let's see if we can log in as STATION_LEADER, cancel, then login as LOGISTICS
  await page.evaluate(() => {
     window.sessionStorage.clear();
  });
  
  await page.goto('http://localhost:4173');
  await page.type('#username', 'maitri_leader');
  await page.type('#password', 'maitri_password');
  await page.select('#station', 'MAITRI');
  await page.select('#role', 'STATION_LEADER');
  await page.click('button[type="submit"]');
  
  await page.waitForSelector('.header-status');
  
  const html2 = await page.evaluate(() => document.querySelector('.header-status').innerHTML);
  console.log("HEADER HTML FOR LEADER:");
  console.log(html2);
  
  await browser.close();
})();
