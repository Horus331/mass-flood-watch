// Screenshots of the test page for a visual check (25 Nov 2026). One page at a time, each in its own try, so one crash does not lose
// the rest.   node proto/bench/ci_shots.js http://localhost:8080 OUTDIR
const { chromium } = require('playwright'); const fs = require('fs');
const BASE = process.argv[2], OUT = process.argv[3]; fs.mkdirSync(OUT, { recursive: true });
const SHOTS = [
  ['desk_forecast', { width: 1440, height: 900 }, false, 'fc'],
  ['phone_forecast', { width: 390, height: 844 }, true, 'fc'],
  ['desk_town', { width: 1440, height: 900 }, false, [12.5, -71.76, 42.53]],
  ['desk_district', { width: 1440, height: 900 }, false, [9.3, -71.75, 42.35]],
  ['phone', { width: 390, height: 844 }, true, null],
];
(async () => {
  for (const [name, vp, mobile, view] of SHOTS) {
    const b = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
    try {
      const ctx = await b.newContext({ viewport: vp, deviceScaleFactor: 1, isMobile: mobile, hasTouch: mobile });
      const p = await ctx.newPage(); p.on('crash', () => console.log('page crashed', name));
      await p.goto(BASE + (view === 'fc' ? '/next.html?debug=1' : '/next.html?run=leominster_sep2023&debug=1'), { waitUntil: 'load', timeout: 120000 });
      await p.waitForFunction(() => !!window.__mfwMap, null, { timeout: 120000 });
      await p.waitForTimeout(15000);
      if (view && view !== 'fc') { await p.evaluate(([z, lon, lat]) => window.__mfwMap.jumpTo({ zoom: z, center: [lon, lat] }), view); await p.waitForTimeout(15000); }
      await p.screenshot({ path: `${OUT}/${name}.png`, timeout: 60000 }); console.log('shot', name);
    } catch (e) { console.log('failed', name, String(e).slice(0, 300)); }
    await b.close();
  }
})();
