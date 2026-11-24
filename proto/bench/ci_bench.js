// CI speed check for the map (map speed plan, 24 Nov 2026): loads each page in headless Chromium and records bytes, requests and
// readiness. Frame rates are not measured here (CI has no graphics card); they are measured on a real laptop with bench.js.
//   node proto/bench/ci_bench.js http://localhost:8080 out.json
const { chromium } = require('playwright'); const fs = require('fs');
const BASE = process.argv[2], OUT = process.argv[3];
const PAGES = [['next_forecast', '/next.html?debug=1'], ['next_replay', '/next.html?run=leominster_sep2023&debug=1'],
               ['live_replay', '/index.html?debug=1'], ['live_forecast', '/index.html?run=forecast&debug=1']];
(async () => {
  const b = await chromium.launch(); const res = {};
  for (const [name, path] of PAGES) {
    const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
    let bytes = 0, reqs = 0, t0 = Date.now(), readyBytes = null, readyReqs = null;
    p.on('response', async r => { reqs++; try { const body = await r.body(); bytes += body.length; } catch (e) {} });
    await p.goto(BASE + path, { waitUntil: 'load' });
    let ready = null;
    for (let i = 0; i < 1200; i++) {
      const ok = await p.evaluate(() => { const m = window.__mfwMap; const pl = document.getElementById('play'), fp = document.getElementById('fplayer');
        return !!(m && m.isStyleLoaded() && ((pl && !pl.disabled) || (fp && !fp.hidden))); }).catch(() => false);
      if (ok) { ready = Date.now() - t0; readyBytes = bytes; readyReqs = reqs; break; }
      await p.waitForTimeout(100);
    }
    await p.waitForTimeout(10000);
    res[name] = { ready_ms: ready, MB_until_ready: readyBytes != null ? +(readyBytes / 1e6).toFixed(2) : null, requests_until_ready: readyReqs,
                  MB_after_10s: +(bytes / 1e6).toFixed(2), requests_after_10s: reqs };
    console.log(name, JSON.stringify(res[name])); await p.close();
  }
  await b.close(); fs.writeFileSync(OUT, JSON.stringify({ at: new Date().toISOString(), pages: res }, null, 1));
})();
