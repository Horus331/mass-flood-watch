/* How it works (docs/model-tree.html): one illustrated landscape; every label opens the full model detail from model-tree/tree.json
   (content and parameter values: proto/model_tree.py, checked against the code in model-tree/CHECK.md). */
(function () {
  'use strict';
  // label: id, n (story order, 0 = limitation), anchor (scene x, y), box (scene x, y, width), nodes (tree.json ids), title, src, plain
  var L = [
    { k: 'obs', n: 1, a: [300, 112], b: [470, 22, 330], nodes: ['mrms', 'rain_grid'], t: 'Rain that fell', src: 'NOAA MRMS radar + rain gauges · 1 km · hourly · mm/h',
      p: 'Radar, corrected with rain gauges, measures the rain on every 1 km square every hour.' },
    { k: 'fc', n: 2, a: [1000, 104], b: [1250, 22, 330], nodes: ['hrrr', 'gate', 'nbhd', 'spinup', 'members'], t: 'Rain that is forecast', src: 'NOAA HRRR · 3 km · hourly · 48 h ahead · 8 forecasts',
      p: 'A weather model forecasts the next two days. We run the flood model with the 8 newest forecasts to see how much they agree.' },
    { k: 'snow', n: 3, a: [1180, 230], b: [1250, 168, 330], nodes: ['phase'], t: 'Rain or snow?', src: 'HRRR 2 m air temperature · °C',
      p: 'Between 0 and 2 °C part of it falls as snow, which does not run off right away.' },
    { k: 'cover', n: 4, a: [760, 505], b: [580, 330, 300], nodes: ['nlcd', 'manning'], t: 'Pavement and land cover', src: 'NLCD 2021 · 30 m · % paved',
      p: 'Paved streets shed almost all the rain; forest slows the water down.' },
    { k: 'soil', n: 5, a: [180, 470], b: [30, 678, 300], nodes: ['ssurgo'], t: 'Soil type', src: 'USDA NRCS SSURGO · soil groups A (sandy) to D (clay)',
      p: 'Sandy soil drinks rain fast, clay slowly.' },
    { k: 'wet', n: 6, a: [260, 590], b: [30, 820, 300], nodes: ['wi_amc', 'wi_frozen'], t: 'How wet, or frozen, the ground is', src: 'NRCS antecedent-moisture classes · frozen-ground rule (Knisel)',
      p: 'Soaked or frozen ground cannot take more water. Live: average wetness; dry, soaked and frozen are what-if runs.' },
    { k: 'runoff', n: 7, a: [470, 408], b: [350, 678, 300], nodes: ['cn'], t: 'How much rain runs off', src: 'NRCS curve number (TR-55) · mm per cell',
      p: 'From soil, pavement and wetness we work out how much of each hour’s rain runs off instead of soaking in.' },
    { k: 'dem', n: 8, a: [560, 470], b: [670, 678, 300], nodes: ['lidar', 'dem20', 'breach', 'crest'], t: 'Ground height', src: 'USGS 3DEP lidar · 10 m → 20 m squares',
      p: 'Laser scans give the height of the ground, so we know which way the water runs and where it pools.' },
    { k: 'stream', n: 9, a: [1300, 556], b: [990, 820, 300], nodes: ['nhd', 'channels'], t: 'Streams and rivers', src: 'USGS NHDPlus HR · carved to bankfull depth',
      p: 'Every mapped stream is dug into the ground grid so it carries water like a real channel.' },
    { k: 'culvert', n: 10, a: [1155, 552], b: [990, 678, 300], nodes: ['crossings', 'notch', 'culvert', 'wi_culvert'], t: 'Culvert under the road', src: 'NAACC / MA Stream Crossings surveys · FHWA HDS-5',
      p: 'Where a stream passes under a road, the pipe’s size decides when water goes over the road. Blocked pipes are a what-if.' },
    { k: 'engine', n: 11, a: [840, 500], b: [470, 172, 330], nodes: ['lisflood', 'depth', 'velocity'], t: 'The flood engine', src: 'LISFLOOD-FP 8.2 · 20 m squares · steps ≤ 1 s · depth every 5 min',
      p: 'Moves the water downhill across every square, step by step, and records how deep and how fast it is everywhere.' },
    { k: 'road', n: 12, a: [1012, 520], b: [1250, 296, 330], nodes: ['roads', 'roadpts', 'segdepth', 'onset', 'pclose'], t: 'Is the road closed?', src: 'MassDOT Road Inventory · depth read every 10 m · closed at 30 cm',
      p: 'We read the water depth along every road. About 30 cm, a car’s door sill, means the road is likely closed.' },
    { k: 'access', n: 13, a: [1440, 450], b: [1310, 678, 280], nodes: ['census', 'facilities', 'dijkstra', 'access'], t: 'Who loses access', src: '2020 Census · hospitals, fire, police (OpenStreetMap)',
      p: 'With closed roads removed, we find who can no longer reach a hospital in 30 min, fire in 8, police in 10.' },
    { k: 'check', n: 14, a: [1300, 506], b: [1310, 820, 280], nodes: ['gauges', 'labels', 'metrics'], t: 'Checked against reality', src: 'USGS river gauges · NWS storm reports · city DPW · MassDOT',
      p: 'Real gauges and flood reports are never fed in; they are only used to check the model afterwards.' },
    { k: 'gw', n: 0, a: [620, 690], b: [350, 820, 300], nodes: ['cc_gw'], t: 'Groundwater (not modelled yet)', src: 'no subsurface flow in the model',
      p: 'Rising groundwater under roads is a named limitation.' },
    { k: 'drain', n: 0, a: [900, 522], b: [670, 820, 300], nodes: ['cc_drains'], t: 'Storm drains (not modelled)', src: 'three ways of adding them were tested and rejected',
      p: 'City pipes are not in the model; adding them removed the water at the very places that flooded.' }
  ];
  var CHAIN = [
    { t: 'Water on each road', p: 'Depth read every 10 m; the second-deepest point counts; only water the storm added.', nodes: ['roadpts', 'segdepth', 'onset'] },
    { t: 'How the road fails', p: 'Ponding (30 cm) closes it; culvert capacity, freeboard, fast water, washout and edge erosion are checked beside it.', nodes: ['pclose', 'culvert', 'freeboard', 'fastwater', 'washout', 'edge'] },
    { t: 'Detours and slower roads', p: 'Closed roads come out of the road network; wet roads are slower; the quickest routes are found again.', nodes: ['graph', 'pregnolato', 'dijkstra'] },
    { t: 'Who loses access', p: 'People who can no longer reach a hospital, fire or police station in time; how well the network still works.', nodes: ['access', 'efficiency'] },
    { t: 'The forecast list', p: 'Roads closed by at least 2 of the 8 forecast runs are "likely"; the list is ordered by the chance of really flooding.', nodes: ['gate', 'members', 'kofn', 'pirank'] },
    { t: 'Checked against reality', p: 'Real reports, matched to roads, scored against random roads and six simple alternatives, on storms never used to set the model.', nodes: ['labels', 'matching', 'metrics', 'baselines', 'split', 'gauges'] }
  ];
  var T, by = {}, simple = true, story = -1;
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var SVGNS = 'http://www.w3.org/2000/svg';
  var ORDER = L.filter(function (l) { return l.n; }).sort(function (a, b) { return a.n - b.n; });

  function fmtVal(p) { var v = p.value; if (typeof v === 'string' && /^[0-9.]+,[0-9.]+$/.test(v)) v = v.replace(',', ', '); if (v === 1 && !p.unit && /parity|fix|switch|enforcement|output|connected/i.test(p.name)) v = 'on'; return v + (p.unit ? ' ' + p.unit : ''); }
  function tex(s, d) { try { return katex.renderToString(s, { displayMode: !!d, throwOnError: false }); } catch (e) { return esc(s); } }
  function stClass(s) { s = s || ''; return /what-if/.test(s) ? 'st-whatif' : /can't/.test(s) ? 'st-limit' : /candidate/.test(s) ? 'st-cand' : 'st-live'; }

  function nodeHtml(n) {
    var h = ['<section class="nd"><h3>' + esc(n.title) + ' <span class="chip ' + stClass(n.status) + '">' + esc(n.status) + '</span></h3><p class="plain">' + esc(n.plain) + '</p><div class="sci">'];
    if (n.what) h.push('<p>' + esc(n.what) + '</p>');
    var meta = [['Units', n.units], ['Resolution', n.resolution], ['Period', n.period], ['How it enters the model', n.how_used], ['What comes out', n.output]].filter(function (r) { return r[1]; });
    if (meta.length) h.push('<table>' + meta.map(function (r) { return '<tr><td>' + r[0] + '</td><td>' + esc(r[1]) + '</td></tr>'; }).join('') + '</table>');
    if (n.formula) { h.push('<div class="formula">' + tex(n.formula, true) + '</div>'); if (n.symbols && n.symbols.length) h.push('<table class="sym">' + n.symbols.map(function (s) { return '<tr><td>' + tex(s[0]) + '</td><td>' + esc(s[1]) + '</td></tr>'; }).join('') + '</table>'); }
    if (n.parameters && n.parameters.length) h.push('<h4>Values used (read from the code)</h4><table>' + n.parameters.map(function (p) { return '<tr><td>' + esc(p.name) + '<div class="where">' + esc(p.origin) + '</div></td><td class="v">' + esc(fmtVal(p)) + '</td></tr>'; }).join('') + '</table>');
    if (n.limits) h.push('<p class="lim"><b>Cannot capture:</b> ' + esc(n.limits) + '</p>');
    if (n.source && n.source.length) h.push('<h4>Sources</h4><ul>' + n.source.map(function (s) { return '<li>' + (s.url ? '<a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.text) + '</a>' : esc(s.text)) + '</li>'; }).join('') + '</ul>');
    if (n.code && n.code.length) h.push('<p class="where">Code: ' + n.code.map(function (c) { return '<a href="' + esc(c.url) + '" target="_blank" rel="noopener">' + esc(c.path) + '</a>' + (c.fn ? ' (' + esc(c.fn) + ')' : ''); }).join(' · ') + '</p>');
    h.push('</div></section>'); return h.join('');
  }

  function openPanel(title, plain, ids, nav) {
    var P = $('panel'), h = ['<button class="btn close" id="pClose" type="button" aria-label="Close">✕</button>'];
    if (nav) h.push('<div class="nav"><button class="btn" id="sPrev" type="button">◀ Back</button><button class="btn on" id="sNext" type="button">Next ▶</button><span class="where">' + nav + '</span></div>');
    h.push('<h2>' + esc(title) + '</h2><p class="lead">' + esc(plain) + '</p>');
    ids.forEach(function (id) { if (by[id]) h.push(nodeHtml(by[id])); });
    P.innerHTML = h.join(''); P.scrollTop = 0; document.body.classList.add('panel-open');
    $('pClose').onclick = closePanel;
    if (nav) { $('sPrev').onclick = function () { step(-1); }; $('sNext').onclick = function () { step(1); }; }
  }
  function closePanel() { document.body.classList.remove('panel-open'); story = -1; mark(null); $('bStory').textContent = '▶ Follow the rain'; history.replaceState(null, '', location.pathname); }
  function mark(k) { Array.prototype.forEach.call(document.querySelectorAll('.lbl,.spot'), function (e) { e.classList.toggle('active', e.dataset.k === k); e.classList.toggle('dim', !!k && e.dataset.k !== k); }); }
  function show(l, nav) { mark(l.k); openPanel(l.t, l.p, l.nodes, nav); history.replaceState(null, '', '#' + l.k); }
  function step(d) { story = Math.max(0, Math.min(ORDER.length - 1, story + d)); show(ORDER[story], 'step ' + (story + 1) + ' of ' + ORDER.length); $('bStory').textContent = 'Next ▶ (' + (story + 1) + '/' + ORDER.length + ')'; }

  function build() {
    var svg = $('scene'), spots = $('spots'), box = $('labels');
    L.forEach(function (l) {
      var lim = !l.n, x = l.b[0], y = l.b[1], w = l.b[2];
      var d = document.createElement('button'); d.type = 'button'; d.className = 'lbl' + (lim ? ' lim' : ''); d.dataset.k = l.k;
      d.style.left = (x / 16) + '%'; d.style.top = (y / 9.6) + '%'; d.style.width = (w / 16) + '%';
      d.innerHTML = (lim ? '' : '<span class="num">' + l.n + '</span>') + '<b>' + esc(l.t) + '</b><span class="src">' + esc(l.src) + '</span><span class="pl">' + esc(l.p) + '</span>';
      d.onclick = function () { story = -1; $('bStory').textContent = '▶ Follow the rain'; show(l); };
      box.appendChild(d); l.el = d;
      var ln = document.createElementNS(SVGNS, 'line'); ln.setAttribute('class', 'lead' + (lim ? ' lim' : '')); ln.dataset.k = l.k; spots.appendChild(ln); l.ln = ln;
      var g = document.createElementNS(SVGNS, 'g'); g.setAttribute('class', 'spot' + (lim ? ' lim' : '')); g.dataset.k = l.k; g.setAttribute('transform', 'translate(' + l.a[0] + ' ' + l.a[1] + ')');
      g.innerHTML = '<circle r="15"/>' + (lim ? '<text y="5">!</text>' : '<text y="5">' + l.n + '</text>');
      g.addEventListener('click', function () { show(l); }); spots.appendChild(g);
    });
    layoutLines(); window.addEventListener('resize', layoutLines);
  }
  function layoutLines() {
    var R = $('scene').getBoundingClientRect(), s = 1600 / R.width;
    document.documentElement.style.setProperty('--sc', (R.width / 1600).toFixed(4));
    L.forEach(function (l) {
      var r = l.el.getBoundingClientRect(), x0 = (r.left - R.left) * s, y0 = (r.top - R.top) * s, x1 = (r.right - R.left) * s, y1 = (r.bottom - R.top) * s;
      var tx = Math.max(x0, Math.min(x1, l.a[0])), ty = l.a[1] < y0 ? y0 : l.a[1] > y1 ? y1 : (l.a[0] < x0 ? 0 : 0);
      if (l.a[1] >= y0 && l.a[1] <= y1) { ty = l.a[1]; tx = l.a[0] < x0 ? x0 : x1; }
      l.ln.setAttribute('x1', l.a[0]); l.ln.setAttribute('y1', l.a[1]); l.ln.setAttribute('x2', tx); l.ln.setAttribute('y2', ty);
    });
  }

  function lists() {
    $('chain').innerHTML = CHAIN.map(function (c, i) { return '<li><button type="button" class="card" data-i="' + i + '"><span class="num">' + (i + 1) + '</span><b>' + esc(c.t) + '</b><span>' + esc(c.p) + '</span></button></li>'; }).join('');
    Array.prototype.forEach.call(document.querySelectorAll('#chain .card'), function (b) { b.onclick = function () { var c = CHAIN[+b.dataset.i]; mark(null); openPanel(c.t, c.p, c.nodes); }; });
    var lim = T.nodes.filter(function (n) { return n.stage === 10; });
    $('limits').innerHTML = lim.map(function (n) { return '<li><button type="button" class="card lim" data-id="' + n.id + '"><b>' + esc(n.title) + '</b><span>' + esc(n.plain) + '</span></button></li>'; }).join('');
    Array.prototype.forEach.call(document.querySelectorAll('#limits .card'), function (b) { b.onclick = function () { var n = by[b.dataset.id]; mark(null); openPanel(n.title, n.plain, [n.id]); }; });
  }

  function init() {
    T.nodes.forEach(function (n) { by[n.id] = n; });
    build(); lists();
    $('bStory').onclick = function () { step(story < 0 ? 0 - (story = -1) + 0 * 0 + 1 - 1 : 1); };
    $('bSimple').onclick = function () { simple = true; document.body.classList.add('simple'); $('bSimple').classList.add('on'); $('bSci').classList.remove('on'); };
    $('bSci').onclick = function () { simple = false; document.body.classList.remove('simple'); $('bSci').classList.add('on'); $('bSimple').classList.remove('on'); };
    document.body.classList.add('simple');
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closePanel(); if (story >= 0 && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')) step(e.key === 'ArrowRight' ? 1 : -1); });
    var h = location.hash.replace('#', '').replace(/^node=/, ''), l = L.filter(function (x) { return x.k === h; })[0];
    if (l) show(l); else if (by[h]) { var m = L.filter(function (x) { return x.nodes.indexOf(h) >= 0; })[0]; if (m) show(m); }
  }
  fetch('model-tree/tree.json?v=' + Date.now()).then(function (r) { return r.json(); }).then(function (j) { T = j; init(); })
    .catch(function (e) { document.querySelector('.intro p').textContent = 'Could not load the model data: ' + e; });
})();
