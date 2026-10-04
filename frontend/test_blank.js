import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  page.on('requestfailed', request => console.log('REQUEST FAILED:', request.url(), request.failure().errorText));

  await page.goto('http://localhost:5173/cases/new', { waitUntil: 'networkidle0' });
  console.log('Navigated to NewCase');
  
  // Fill the form
  await page.type('input[placeholder="e.g. 0x... or T..."]', 'test_address');
  await page.click('button[type="submit"]');
  console.log('Clicked submit');
  
  await new Promise(r => setTimeout(r, 2000));
  console.log('Done waiting. Current URL:', page.url());
  
  await browser.close();
})();
