// Screenshots of the test page's street layer at a zoomed-out and a street-level view (map speed plan, 24 Nov 2026), for a visual check
// after a tile change.   node proto/bench/ci_shots.js http://localhost:8080 OUTDIR
const { chromium } = require('playwright'); const fs = require('fs');
const BASE = process.argv[2], OUT = process.argv[3]; fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const b = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  for (const [name, z, lon, lat] of [['z9', 9.5, -71.75, 42.35], ['z11', 11.5, -71.80, 42.27], ['z13', 13, -71.80, 42.27]]) {
    const p = await b.newPage({ viewport: { width: 1000, height: 650 } });
    await p.goto(BASE + '/next.html?debug=1', { waitUntil: 'load' });
    await p.waitForFunction(() => window.__mfwMap && window.__mfwMap.loaded(), null, { timeout: 120000 });
    await p.evaluate(([z, lon, lat]) => window.__mfwMap.jumpTo({ zoom: z, center: [lon, lat] }), [z, lon, lat]);
    await p.waitForTimeout(1000);
    await p.evaluate(() => new Promise(r => { const m = window.__mfwMap; m.once('idle', r); m.triggerRepaint(); setTimeout(r, 30000); }));
    await p.waitForTimeout(1500);
    await p.screenshot({ path: `${OUT}/${name}.png` }); await p.close();
  }
  await b.close();
})();
