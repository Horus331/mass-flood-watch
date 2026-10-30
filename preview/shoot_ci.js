// CI screenshots with the real network (tiles, fonts, maplibre); docs/ from the checkout, what-if packs from the local placeholders
const { chromium } = require('playwright'); const fs = require('fs'), path = require('path');
const DOCS = path.resolve('docs'), WIS = path.join(__dirname, 'site_whatif');
const [, , out, ...specs] = process.argv; fs.mkdirSync(out, { recursive: true });
const types = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.svg': 'image/svg+xml' };
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  for (const sp of specs) {
    const [name, url, w, h, wait, nowi, js] = sp.split('|');
    const ctx = await b.newContext({ viewport: { width: +w, height: +h }, deviceScaleFactor: +w < 500 ? 2 : 1 });
    const pg = await ctx.newPage(); const errs = [];
    pg.on('pageerror', e => errs.push('PAGEERR ' + e.message)); pg.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 200)); });
    await pg.route('http://local.test/**', r => {
      const u = new URL(r.request().url()); let f = decodeURIComponent(u.pathname); if (f.endsWith('/')) f += 'index.html';
      const p = f.startsWith('/site/data/whatif/') ? (nowi === '1' ? null : path.join(WIS, f.slice(18))) : path.join(DOCS, f);
      if (f === '/site/data/outlook_sample.json' || (f === '/site/data/outlook.json' && !fs.existsSync(p))) return r.fulfill({ status: 200, body: fs.readFileSync(path.join(__dirname, 'outlook_sample.json')), contentType: 'application/json' });
      if (!p || !fs.existsSync(p)) return r.fulfill({ status: 404, body: 'nf' });
      return r.fulfill({ status: 200, body: fs.readFileSync(p), contentType: types[path.extname(p)] || 'application/octet-stream' });
    });
    await pg.goto('http://local.test/' + url); await pg.waitForTimeout(+wait || 15000);
    if (js) { await pg.evaluate(js); await pg.waitForTimeout(6000); }
    await pg.screenshot({ path: path.join(out, name + '.png') });
    console.log(name, errs.slice(0, 8).join('\n  ')); await ctx.close();
  }
  await b.close();
})();
