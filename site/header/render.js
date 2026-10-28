// Renders ink.svg (header) to PNG at 3x (website and README, sharp on phones) and og.svg (preview) at 2x. Usage: node render.js DIR
const {chromium} = require('playwright');
(async () => {
  const dir = process.argv[2], b = await chromium.launch();
  for (const cs of ['light', 'dark']) {
    const p = await b.newPage({viewport: {width: 1280, height: 640}, deviceScaleFactor: 3, colorScheme: cs});
    await p.goto('file://' + dir + '/ink.svg'); await p.screenshot({path: dir + '/out-' + cs + '.png'}); await p.close();
  }
  const p = await b.newPage({viewport: {width: 1200, height: 630}, deviceScaleFactor: 2});
  await p.goto('file://' + dir + '/og.svg'); await p.screenshot({path: dir + '/og-raw.png'});
  await b.close();
})();
