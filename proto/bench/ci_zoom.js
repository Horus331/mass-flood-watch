// Wait after a zoom (map speed plan, 24 Nov 2026): for each page, after it is ready, zoom in and out in steps and record how long
// until the map is complete again ('idle'), and which sources were the last to finish. Headless Chromium on CI (software GL), so
// draw times are pessimistic; network and worker (tile building) times are real.
//   node proto/bench/ci_zoom.js http://localhost:8080 out.json
const { chromium } = require('playwright'); const fs = require('fs');
const BASE = process.argv[2], OUT = process.argv[3];
const PAGES = [['live_replay', '/index.html?run=leominster_sep2023&debug=1'], ['next_replay', '/next.html?run=leominster_sep2023&debug=1']];
(async () => {
  const b = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] }); const res = {};
  for (const [name, path] of PAGES) {
    const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
    await p.goto(BASE + path, { waitUntil: 'load' });
    await p.waitForFunction(() => window.__mfwMap && window.__mfwMap.loaded(), null, { timeout: 120000 });
    await p.waitForTimeout(8000);
    res[name] = await p.evaluate(async () => {
      const m = window.__mfwMap, sleep = ms => new Promise(r => setTimeout(r, ms)), out = [];
      const steps = [1, 1, 1, -1, -1, -1, 2, -2];
      for (const dz of steps) {
        const last = {}; const t0 = performance.now();
        const onData = e => { if (e.sourceId && e.dataType === 'source') last[e.sourceId] = Math.round(performance.now() - t0); };
        m.on('sourcedata', onData);
        m.zoomTo(m.getZoom() + dz, { duration: 0 });
        let idle = null; await new Promise(r => { m.once('idle', () => { idle = Math.round(performance.now() - t0); r(); }); setTimeout(r, 30000); });
        m.off('sourcedata', onData);
        out.push({ dz, z: +m.getZoom().toFixed(1), idle_ms: idle, slowest: Object.entries(last).sort((a, b) => b[1] - a[1]).slice(0, 4) });
        await sleep(500);
      }
      return out;
    });
    console.log(name, JSON.stringify(res[name])); await p.close();
  }
  await b.close(); fs.writeFileSync(OUT, JSON.stringify({ at: new Date().toISOString(), pages: res }, null, 1));
})();
