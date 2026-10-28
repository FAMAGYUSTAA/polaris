const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  let logs = [];
  page.on('console', msg => {
      logs.push("Console: " + msg.type() + " - " + msg.text());
  });
  page.on('pageerror', err => {
      logs.push("Page Error: " + err.message);
  });
  page.on('requestfailed', request => {
      logs.push("Request Failed: " + request.url() + " - " + request.failure().errorText);
  });

  try {
      await page.goto('http://192.168.21.116:5173');
      await new Promise(r => setTimeout(r, 2000));
      
      console.log("Logs caught:");
      console.log(logs.join('\n'));
      
      const bodyContent = await page.evaluate(() => document.body.innerHTML);
      console.log("Body length:", bodyContent.length);
      
  } catch (err) {
      console.log("Script Error: " + err.message);
  }
  
  await browser.close();
})();
