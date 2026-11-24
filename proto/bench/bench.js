// Map speed benchmark (map speed plan, 24 Nov 2026). Paste into a page on the same origin as the map (or run via a browser tool):
// await bench('/mass-flood-watch/index.html?debug=1')  -> numbers for one load of the page, measured inside a 1280x800 iframe.
async function bench(url, opts) {
  opts = opts || {};
  const lt = []; const po = new PerformanceObserver(l => { for (const e of l.getEntries()) lt.push([e.startTime, e.duration]); }); po.observe({ type: 'longtask' });
  const f = document.createElement('iframe'); f.style.cssText = 'position:fixed;left:0;top:0;width:1280px;height:800px;z-index:99999;border:0;background:#fff';
  const t0 = performance.now(); f.src = url; document.body.appendChild(f);
  const W = () => f.contentWindow, sleep = ms => new Promise(r => setTimeout(r, ms));
  const until = async (fn, max) => { const s = performance.now(); while (performance.now() - s < max) { try { if (fn()) return performance.now() - t0; } catch (e) {} await sleep(50); } return null; };
  const out = {};
  out.map_ready_ms = await until(() => W().__mfwMap && W().__mfwMap.loaded(), 60000);
  out.play_ready_ms = await until(() => { const b = W().document.getElementById('play'); return b && !b.disabled; }, 90000);
  await sleep(1500);
  const net = W().performance.getEntriesByType('resource'); out.requests = net.length; out.MB = +(net.reduce((a, r) => a + (r.transferSize || r.encodedBodySize || 0), 0) / 1e6).toFixed(1);
  const L = lt.filter(x => x[0] > t0); out.load_longtasks = L.length; out.load_blocked_ms = Math.round(L.reduce((a, x) => a + x[1], 0)); out.load_worst_ms = Math.round(Math.max(0, ...L.map(x => x[1])));
  const frames = async (ms, act) => {   // frame times while act() runs
    const ts = []; let go = true; const w = W(); const tick = t => { ts.push(t); if (go) w.requestAnimationFrame(tick); }; w.requestAnimationFrame(tick);
    const n0 = lt.length; await act(); await sleep(ms); go = false;
    const d = ts.slice(1).map((t, i) => t - ts[i]).sort((a, b) => a - b); const L2 = lt.slice(n0);
    return { fps: +(1000 * d.length / (ts[ts.length - 1] - ts[0])).toFixed(1), p95_frame_ms: Math.round(d[Math.floor(d.length * 0.95)] || 0), worst_frame_ms: Math.round(d[d.length - 1] || 0), longtasks: L2.length, blocked_ms: Math.round(L2.reduce((a, x) => a + x[1], 0)) };
  };
  const m = W().__mfwMap;
  if (m) {
    const c = m.getCenter();
    out.pan = await frames(3000, async () => { m.easeTo({ center: [c.lng + 0.06, c.lat + 0.02], duration: 3000, easing: t => t }); });
    out.zoom = await frames(3000, async () => { m.easeTo({ zoom: m.getZoom() + 2.5, duration: 1500 }); setTimeout(() => m.easeTo({ zoom: m.getZoom() - 2.5, duration: 1500 }), 1500); });
  }
  const pb = W().document.getElementById('play');
  if (pb && !pb.disabled && !opts.noplay) { out.play = await frames(5000, async () => { pb.click(); }); pb.click(); }
  po.disconnect(); f.remove(); return out;
}
