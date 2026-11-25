// Screenshots of the test page (map speed plan, 24-25 Nov 2026) for a visual check: desktop at a zoomed-out, a town and a street view,
// and a phone view.   node proto/bench/ci_shots.js http://localhost:8080 OUTDIR
const { chromium, devices } = require('playwright'); const fs = require('fs');
const BASE = process.argv[2], OUT = process.argv[3]; fs.mkdirSync(OUT, { recursive: true });
async function settle(p) {
  await p.waitForFunction(() => !!window.__mfwMap, null, { timeout: 120000 });
  await p.evaluate(() => new Promise(r => { const m = window.__mfwMap; m.once('idle', r); m.triggerRepaint(); setTimeout(r, 30000); }));
  await p.waitForTimeout(2000);
}
(async () => {
  const b = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const views = [['desk_z9', 9.3, -71.75, 42.35], ['desk_z12', 12, -71.76, 42.53], ['desk_z15', 15, -71.765, 42.527]];
  for (const [name, z, lon, lat] of views) {
    const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
    await p.goto(BASE + '/next.html?run=leominster_sep2023&debug=1', { waitUntil: 'load' }); await settle(p);
    await p.evaluate(([z, lon, lat]) => window.__mfwMap.jumpTo({ zoom: z, center: [lon, lat] }), [z, lon, lat]); await settle(p);
    await p.screenshot({ path: `${OUT}/${name}.png` }); await p.close(); console.log('shot', name);
  }
  const ctx = await b.newContext({ ...devices['iPhone 13'] }); const p = await ctx.newPage();
  await p.goto(BASE + '/next.html?run=leominster_sep2023&debug=1', { waitUntil: 'load' }); await settle(p);
  await p.screenshot({ path: `${OUT}/phone.png` }); console.log('shot phone');
  await b.close();
})();
