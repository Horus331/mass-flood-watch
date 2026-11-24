// Click cost on the test page's timeline (map speed plan, 24 Nov 2026): taps at 5 places on the replay timeline, records the browser's
// event timing (input delay + handler + next paint) and, with the CPU profiler on, the functions that took the most time.
//   node proto/bench/ci_clicks.js http://localhost:8080 out.json
const { chromium } = require('playwright'); const fs = require('fs');
const BASE = process.argv[2], OUT = process.argv[3];
(async () => {
  const b = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] }); const res = {};
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto(BASE + '/next.html?run=leominster_sep2023&debug=1', { waitUntil: 'load' });
  await p.waitForFunction(() => window.__mfwMap && window.__mfwMap.loaded(), null, { timeout: 120000 });
  await p.waitForTimeout(10000);
  await p.evaluate(() => { window.__ev = []; new PerformanceObserver(l => l.getEntries().forEach(e => window.__ev.push({ n: e.name, d: Math.round(e.duration), p: Math.round(e.processingEnd - e.processingStart) }))).observe({ type: 'event', durationThreshold: 16, buffered: false }); });
  const tl = await p.$('#timeline'); const bb = tl && await tl.boundingBox(); res.timeline = bb;
  const cdp = await p.context().newCDPSession(p); await cdp.send('Profiler.enable'); await cdp.send('Profiler.setSamplingInterval', { interval: 200 }); await cdp.send('Profiler.start');
  if (bb) for (const f of [0.15, 0.5, 0.8, 0.3, 0.95]) { await p.mouse.click(bb.x + bb.width * f, bb.y + bb.height / 2); await p.waitForTimeout(1200); }
  const { profile } = await cdp.send('Profiler.stop');
  const self = {}; const byId = {}; profile.nodes.forEach(n => byId[n.id] = n);
  const dt = profile.timeDeltas; profile.samples.forEach((id, i) => { const n = byId[id]; const k = `${n.callFrame.functionName || '(anon)'} ${(n.callFrame.url || '').split('/').pop()}:${n.callFrame.lineNumber + 1}`; self[k] = (self[k] || 0) + (dt[i] || 0) / 1000; });
  res.top_self_ms = Object.entries(self).filter(([k]) => !/^\((idle|program|garbage collector)\)/.test(k)).sort((a, b) => b[1] - a[1]).slice(0, 25).map(([k, v]) => [k, Math.round(v)]);
  res.events = await p.evaluate(() => window.__ev);
  console.log(JSON.stringify(res, null, 1)); fs.writeFileSync(OUT, JSON.stringify(res, null, 1)); await b.close();
})();
