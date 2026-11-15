/* How it works: one illustrated landscape; every label opens the full model detail from tree.json
   (content and parameter values: proto/model_tree.py, checked against the code in docs/model-tree/CHECK.md). */
(function () {
  'use strict';
  var C = { sky: '#3b82d6', fc: '#7b6fd0', ground: '#9c7350', water: '#1f6fc2', road: '#e2554a', people: '#c26401', lim: '#9aa0a6' };
  // k, n (story order; 0 = limitation), a = anchor in the picture, b = card [x, y, width] (picture units 1600 x 900), c = colour, nodes = tree.json ids
  var L = [
    { k: 'obs', n: 1, c: C.sky, a: [372, 104], b: [420, 26, 300], nodes: ['mrms', 'rain_grid'], t: 'Rain that fell', src: 'NOAA MRMS radar + gauges · 1 km · every hour',
      p: 'Radar, corrected with rain gauges, measures the rain on every 1 km square every hour.' },
    { k: 'fc', n: 2, c: C.fc, a: [1176, 92], b: [1250, 26, 320], nodes: ['hrrr', 'gate', 'nbhd', 'spinup', 'members'], t: 'Rain that is forecast', src: 'NOAA HRRR · 3 km · 48 h ahead · newest 8 forecasts',
      p: 'A weather model forecasts the next two days. We run the flood model on the 8 newest forecasts to see how much they agree.' },
    { k: 'snow', n: 3, c: C.fc, a: [1192, 214], b: [1250, 146, 320], nodes: ['phase'], t: 'Rain or snow?', src: 'HRRR air temperature at 2 m · °C',
      p: 'Between 0 and 2 °C part of it falls as snow, which does not run off right away.' },
    { k: 'cover', n: 4, c: C.ground, a: [800, 470], b: [790, 312, 270], nodes: ['nlcd', 'manning'], t: 'Pavement and land cover', src: 'NLCD 2021 · 30 m · % paved',
      p: 'Paved streets shed almost all the rain; forest slows the water down.' },
    { k: 'soil', n: 5, c: C.ground, a: [190, 520], b: [24, 628, 290], nodes: ['ssurgo'], t: 'Soil type', src: 'USDA SSURGO · sandy (A) to clay (D)',
      p: 'Sandy soil drinks rain fast, clay slowly.' },
    { k: 'wet', n: 6, c: C.ground, a: [168, 756], b: [24, 786, 290], nodes: ['wi_amc', 'wi_frozen'], t: 'Wet, dry or frozen ground', src: 'NRCS moisture classes · frozen-ground rule',
      p: 'Soaked or frozen ground cannot take more water. Live runs use average wetness; dry, soaked and frozen are what-if runs.' },
    { k: 'runoff', n: 7, c: C.water, a: [452, 408], b: [334, 628, 290], nodes: ['cn'], t: 'How much rain runs off', src: 'NRCS curve number (TR-55) · mm',
      p: 'From soil, pavement and wetness we work out how much of each hour’s rain runs off instead of soaking in.' },
    { k: 'dem', n: 8, c: C.ground, a: [604, 478], b: [420, 266, 300], nodes: ['lidar', 'dem20', 'breach', 'crest'], t: 'Ground height', src: 'USGS 3DEP lidar · 10 m, used as 20 m squares',
      p: 'Laser scans give the height of the ground, so we know which way the water runs and where it pools.' },
    { k: 'engine', n: 9, c: C.water, a: null, b: [420, 146, 300], nodes: ['lisflood', 'depth', 'velocity'], t: 'The flood engine', src: 'LISFLOOD-FP 8.2 · moves all the water in this picture, on 20 m squares',
      p: 'Moves the water downhill across every square, a second at a time, and records how deep and how fast it is everywhere.' },
    { k: 'culvert', n: 10, c: C.water, a: [1158, 502], b: [964, 628, 290], nodes: ['nhd', 'channels', 'crossings', 'notch', 'culvert', 'wi_culvert'], t: 'Streams and the culvert', src: 'USGS NHDPlus HR · NAACC surveys · FHWA HDS-5',
      p: 'Streams are carved into the ground; where one passes under a road, the pipe size decides when water goes over the road.' },
    { k: 'road', n: 11, c: C.road, a: [1020, 478], b: [1250, 266, 320], nodes: ['roads', 'roadpts', 'segdepth', 'onset', 'pclose'], t: 'Is the road closed?', src: 'MassDOT roads · depth every 10 m · closed at 30 cm',
      p: 'We read the water depth along every road. About 30 cm, a car’s door sill, means the road is likely closed.' },
    { k: 'access', n: 12, c: C.people, a: [1452, 410], b: [1284, 628, 290], nodes: ['census', 'facilities', 'dijkstra', 'access'], t: 'Who loses access', src: 'Census 2020 · hospitals, fire, police (OSM)',
      p: 'With closed roads taken out, we find who can no longer reach a hospital in 30 min, fire in 8, police in 10.' },
    { k: 'gw', n: 0, c: C.lim, a: [500, 760], b: [334, 786, 290], nodes: ['cc_gw'], t: 'Groundwater', src: 'not in the model yet',
      p: 'Rising groundwater under roads is not modelled.' },
    { k: 'drain', n: 0, c: C.lim, a: [880, 505], b: [654, 628, 290], nodes: ['cc_drains'], t: 'Storm drains', src: 'not in the model: 3 versions tested, none helped',
      p: 'City pipes are not in the model; adding them removed water at the very places that flooded.' },
    { k: 'check', n: 13, c: '#5f6870', a: [1316, 462], b: [964, 786, 290], nodes: ['gauges', 'labels', 'metrics', 'split'], t: 'Checked against reality', src: 'USGS river gauges · flood reports · never fed in',
      p: 'Real gauges and flood reports are only used to check the model afterwards, never as inputs.' }
  ];
  var CHAIN = [
    { t: 'Water on each road', p: 'Depth read every 10 m along every road; only the water the storm added counts.', nodes: ['roadpts', 'segdepth', 'onset'] },
    { t: 'How the road fails', p: 'Standing water of about 30 cm closes it. Culvert capacity, fast water and washout are checked alongside.', nodes: ['pclose', 'culvert', 'freeboard', 'fastwater', 'washout', 'edge'] },
    { t: 'Detours', p: 'Closed roads come out of the road network, wet ones get slower, and the quickest routes are found again.', nodes: ['graph', 'pregnolato', 'dijkstra'] },
    { t: 'Who loses access', p: 'People who can no longer reach a hospital, fire or police station in time.', nodes: ['access', 'efficiency'] },
    { t: 'The forecast list', p: 'Roads closed by at least 2 of the 8 forecast runs are "likely"; the list is ordered by the chance of really flooding.', nodes: ['gate', 'members', 'kofn', 'pirank'] },
    { t: 'Checked against reality', p: 'Real reports, matched to roads, compared with random roads and simple alternatives, on storms never used to set the model.', nodes: ['labels', 'matching', 'metrics', 'baselines', 'split', 'gauges'] }
  ];
  var T, by = {}, story = -1;
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var NS = 'http://www.w3.org/2000/svg';
  var ORDER = L.filter(function (l) { return l.n; }).sort(function (a, b) { return a.n - b.n; });
  function el(tag, attrs, parent) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; }

  // ---------------------------------------------------------------- drawing details (deterministic, so the picture is the same every time)
  function rnd(s) { return function () { s = (s * 16807) % 2147483647; return s / 2147483647; }; }
  function decorate() {
    var r = rnd(7), g = $('rainObs');
    for (var i = 0; i < 46; i++) { var x = 150 + r() * 230, y = 150 + r() * 150; el('line', { x1: x, y1: y, x2: x - 6, y2: y + 22 }, g); }
    g = $('rainFc');
    for (i = 0; i < 34; i++) { x = 960 + r() * 200, y = 146 + r() * 170; el('line', { x1: x, y1: y, x2: x - 6, y2: y + 20 }, g); }
    g = $('flakes');
    [[1150, 180], [1192, 236], [1124, 250], [1176, 296]].forEach(function (p) { el('path', { d: 'M0 -8V8M-7 -4L7 4M-7 4L7 -4', transform: 'translate(' + p[0] + ' ' + p[1] + ')' }, g); });
    g = $('trees');
    [[96, 392, 1.0], [140, 360, 1.15], [188, 334, 1.05], [234, 322, 1.2], [352, 330, 1.0], [398, 356, 1.1], [446, 392, 0.95], [1380, 476, 0.9], [1580, 396, 0.9]].forEach(function (t, i) {
      var x = t[0], y = t[1], s = t[2];
      el('rect', { x: x - 3 * s, y: y - 6 * s, width: 6 * s, height: 16 * s, fill: '#7a5a3c' }, g);
      el('circle', { cx: x, cy: y - 22 * s, r: 18 * s, fill: i % 2 ? 'var(--tree1)' : 'var(--tree2)' }, g);
      el('circle', { cx: x - 10 * s, cy: y - 12 * s, r: 12 * s, fill: i % 2 ? 'var(--tree2)' : 'var(--tree1)' }, g);
    });
    g = $('houses');
    [[700, 494, 44, 34], [770, 494, 52, 46], [856, 494, 40, 30]].forEach(function (h) {
      var x = h[0], y = h[1], w = h[2], hh = h[3];
      el('rect', { x: x, y: y - hh, width: w, height: hh, fill: 'var(--house)', stroke: '#8a8f96', 'stroke-width': 1.5 }, g);
      el('path', { d: 'M' + (x - 6) + ' ' + (y - hh) + 'L' + (x + w / 2) + ' ' + (y - hh - w * 0.45) + 'L' + (x + w + 6) + ' ' + (y - hh) + 'Z', fill: 'var(--roof)' }, g);
      el('rect', { x: x + w / 2 - 6, y: y - 16, width: 12, height: 16, fill: '#8a8f96' }, g);
    });
  }

  // ---------------------------------------------------------------- panel
  function fmtVal(p) { var v = p.value; if (typeof v === 'string' && /^[0-9.]+,[0-9.]+$/.test(v)) v = v.replace(',', ', '); if (v === 1 && !p.unit && /parity|fix|switch|enforcement|output|connected/i.test(p.name)) v = 'on'; return v + (p.unit ? ' ' + p.unit : ''); }
  function tex(s, d) { try { return katex.renderToString(s, { displayMode: !!d, throwOnError: false }); } catch (e) { return esc(s); } }
  function stClass(s) { s = s || ''; return /what-if/.test(s) ? 'st-whatif' : /can't/.test(s) ? 'st-limit' : /candidate/.test(s) ? 'st-cand' : 'st-live'; }
  function stText(s) { s = s || ''; return /what-if/.test(s) ? 'what-if only' : /can't/.test(s) ? 'not modelled yet' : /candidate/.test(s) ? 'extra check, not in the closure rule' : 'in use'; }
  function nodeHtml(n) {
    var h = ['<section class="nd"><h3>' + esc(n.title) + '<span class="chip ' + stClass(n.status) + '">' + stText(n.status) + '</span></h3><p class="plain">' + esc(n.plain) + '</p>'];
    if (n.what) h.push('<p>' + esc(n.what) + '</p>');
    var meta = [['Units', n.units], ['Detail', n.resolution], ['Period', n.period], ['How it is used', n.how_used], ['What comes out', n.output]].filter(function (r) { return r[1]; });
    if (meta.length) h.push('<table>' + meta.map(function (r) { return '<tr><td>' + r[0] + '</td><td>' + esc(r[1]) + '</td></tr>'; }).join('') + '</table>');
    if (n.formula) { h.push('<div class="formula">' + tex(n.formula, true) + '</div>'); if (n.symbols && n.symbols.length) h.push('<table class="sym">' + n.symbols.map(function (s) { return '<tr><td>' + tex(s[0]) + '</td><td>' + esc(s[1]) + '</td></tr>'; }).join('') + '</table>'); }
    if (n.parameters && n.parameters.length) h.push('<h4>Values used</h4><table>' + n.parameters.map(function (p) { return '<tr><td>' + esc(p.name) + '<div class="where">' + esc(p.origin) + '</div></td><td class="v">' + esc(fmtVal(p)) + '</td></tr>'; }).join('') + '</table>');
    if (n.limits) h.push('<p class="lim"><b>Can’t capture:</b> ' + esc(n.limits) + '</p>');
    if (n.source && n.source.length) h.push('<h4>Sources</h4><ul>' + n.source.map(function (s) { return '<li>' + (s.url ? '<a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.text) + '</a>' : esc(s.text)) + '</li>'; }).join('') + '</ul>');
    h.push('</section>'); return h.join('');
  }
  function openPanel(title, plain, ids, nav) {
    var P = $('panel'), h = ['<button class="close" id="pClose" type="button" aria-label="Close">✕</button>'];
    if (nav) h.push('<div class="nav"><button class="pill" id="sPrev" type="button">Back</button><button class="pill pill-on" id="sNext" type="button">Next</button><span class="where">' + nav + '</span></div>');
    h.push('<h2>' + esc(title) + '</h2><p class="lead">' + esc(plain) + '</p>');
    ids.forEach(function (id) { if (by[id]) h.push(nodeHtml(by[id])); });
    P.innerHTML = h.join(''); P.scrollTop = 0; document.body.classList.add('panel-open');
    $('pClose').onclick = closePanel;
    if (nav) { $('sPrev').onclick = function () { step(-1); }; $('sNext').onclick = function () { step(1); }; }
  }
  function closePanel() { document.body.classList.remove('panel-open'); story = -1; mark(null); $('bStory').textContent = 'Follow the rain, step by step'; history.replaceState(null, '', location.pathname); }
  function mark(k) { Array.prototype.forEach.call(document.querySelectorAll('.lbl,#spots .spot,#spots line'), function (e) { e.classList.toggle('active', e.dataset.k === k); e.classList.toggle('dim', !!k && e.dataset.k !== k); }); }
  function show(l, nav) { mark(l.k); openPanel(l.t, l.p, l.nodes, nav); history.replaceState(null, '', '#' + l.k); }
  function step(d) {
    story = Math.max(0, Math.min(ORDER.length - 1, story + d)); show(ORDER[story], 'Step ' + (story + 1) + ' of ' + ORDER.length);
    $('bStory').textContent = 'Next step (' + (story + 1) + ' of ' + ORDER.length + ')';
    var r = ORDER[story].el.getBoundingClientRect(); if (r.top < 70 || r.bottom > innerHeight) ORDER[story].el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  // ---------------------------------------------------------------- labels and leaders
  function build() {
    var spots = $('spots'), box = $('labels');
    L.forEach(function (l) {
      var lim = !l.n, d = document.createElement('button');
      d.type = 'button'; d.className = 'lbl' + (lim ? ' lim' : ''); d.dataset.k = l.k; d.style.setProperty('--c', l.c);
      d.style.left = (l.b[0] / 16) + '%'; d.style.top = (l.b[1] / 9) + '%'; d.style.width = (l.b[2] / 16) + '%';
      d.innerHTML = (lim ? '' : '<span class="num">' + l.n + '</span>') + '<b>' + esc(l.t) + '</b><span class="src">' + esc(l.src) + '</span><span class="pl">' + esc(l.p) + '</span>';
      d.onclick = function () { story = -1; $('bStory').textContent = 'Follow the rain, step by step'; show(l); };
      box.appendChild(d); l.el = d;
      if (!l.a) return;
      l.ln = el('line', { 'class': lim ? 'lim' : '' }, spots); l.ln.dataset.k = l.k;
      var g = el('g', { 'class': 'spot', transform: 'translate(' + l.a[0] + ' ' + l.a[1] + ')' }, spots); g.dataset.k = l.k; g.style.setProperty('--c', l.c);
      el('circle', { 'class': 'dot', r: lim ? 7 : 8 }, g);
      g.addEventListener('click', function () { show(l); });
    });
    lines(); window.addEventListener('resize', lines);
  }
  function lines() {
    var R = $('scene').getBoundingClientRect(), s = 1600 / R.width;
    document.documentElement.style.setProperty('--sc', (R.width / 1600).toFixed(4));
    L.forEach(function (l) {
      if (!l.a) return;
      var r = l.el.getBoundingClientRect(), x0 = (r.left - R.left) * s, y0 = (r.top - R.top) * s, x1 = (r.right - R.left) * s, y1 = (r.bottom - R.top) * s;
      var ax = l.a[0], ay = l.a[1], tx, ty;
      if (ay < y0) { ty = y0; tx = Math.max(x0 + 14, Math.min(x1 - 14, ax)); }
      else if (ay > y1) { ty = y1; tx = Math.max(x0 + 14, Math.min(x1 - 14, ax)); }
      else { ty = Math.max(y0 + 10, Math.min(y1 - 10, ay)); tx = ax < x0 ? x0 : x1; }
      l.ln.setAttribute('x1', ax); l.ln.setAttribute('y1', ay); l.ln.setAttribute('x2', tx); l.ln.setAttribute('y2', ty);
    });
  }
  function lists() {
    $('chain').innerHTML = CHAIN.map(function (c, i) { return '<li><button type="button" class="card" data-i="' + i + '"><span class="num">' + (i + 1) + '</span><b>' + esc(c.t) + '</b><span>' + esc(c.p) + '</span></button></li>'; }).join('');
    Array.prototype.forEach.call(document.querySelectorAll('#chain .card'), function (b) { b.onclick = function () { var c = CHAIN[+b.dataset.i]; mark(null); openPanel(c.t, c.p, c.nodes); }; });
    var lim = T.nodes.filter(function (n) { return n.stage === 10; });
    $('limits').innerHTML = lim.map(function (n) { return '<li><button type="button" class="card" data-id="' + n.id + '"><b>' + esc(n.title) + '</b><span>' + esc(n.plain) + '</span></button></li>'; }).join('');
    Array.prototype.forEach.call(document.querySelectorAll('#limits .card'), function (b) { b.onclick = function () { var n = by[b.dataset.id]; mark(null); openPanel(n.title, n.plain, [n.id]); }; });
  }
  function init() {
    T.nodes.forEach(function (n) { by[n.id] = n; });
    decorate(); build(); lists();
    $('bStory').onclick = function () { if (story < 0) story = -1; step(1); };
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closePanel(); if (story >= 0 && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')) step(e.key === 'ArrowRight' ? 1 : -1); });
    var h = location.hash.replace('#', ''), l = L.filter(function (x) { return x.k === h; })[0]; if (l) show(l);
  }
  fetch(document.body.dataset.tree || 'model-tree/tree.json').then(function (r) { return r.json(); }).then(function (j) { T = j; init(); })
    .catch(function (e) { document.querySelector('.lede').textContent = 'Could not load the model data: ' + e; });
})();
