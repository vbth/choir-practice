// Render test of the website: both languages at the four device classes (mobile, tablet portrait, tablet landscape, desktop).
//   node site/render_test.js [out_dir]      (needs playwright with chromium)
// Writes a full-page screenshot per language and size to out_dir (default: a temp folder) and reports horizontal overflow
// (page wider than the viewport) with the elements that stick out. Exit code 1 if a page overflows.
const { chromium } = require('playwright');
const fs = require('fs'), os = require('os'), path = require('path');
const DOCS = path.resolve(__dirname, '..', 'docs');
const SIZES = { mobile: [390, 844], tablet_portrait: [820, 1180], tablet_landscape: [1180, 820], desktop: [1440, 900] };
(async () => {
  const out = process.argv[2] || fs.mkdtempSync(path.join(os.tmpdir(), 'render-'));
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch(); let bad = 0;
  for (const lang of ['de', 'en']) for (const [name, [w, h]] of Object.entries(SIZES)) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto('file://' + path.join(DOCS, lang === 'de' ? '' : 'en', 'index.html'));
    await p.evaluate(() => document.querySelectorAll('img[loading=lazy]').forEach(i => { i.loading = 'eager'; }));
    await p.waitForTimeout(600);
    const r = await p.evaluate(() => {
      const W = innerWidth, over = document.documentElement.scrollWidth - W, els = [];
      if (over > 0) document.querySelectorAll('body *').forEach(e => { const x = e.getBoundingClientRect().right; if (x > W + 1 && els.length < 3) els.push(e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ')[0] : '')); });
      return { over, els };
    });
    const file = path.join(out, `${lang}-${name}.png`);
    await p.screenshot({ path: file, fullPage: true });
    console.log(`${r.over > 0 ? 'OVERFLOW' : 'ok      '} ${lang} ${name} ${w}x${h}` + (r.over > 0 ? ` +${r.over}px: ${r.els.join(', ')}` : ''));
    if (r.over > 0) bad++;
    await p.close();
  }
  await b.close(); console.log('screenshots:', out); process.exit(bad ? 1 : 0);
})();
