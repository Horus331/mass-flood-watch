/* How it works: labels, numbers and the model tree. Every number is read from how-it-works/sketch/anchors.json
   (proto/howit_sketch_render.py) or model-tree/tree.json (proto/model_tree.py); nothing is typed here. */
(function () {
  'use strict';
  var BASE = 'how-it-works/sketch/';
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var NICE = { 'Umass Memorial-HealthAlliance Hospital': 'HealthAlliance Hospital', 'Sp Leominster': 'State Police, Leominster',
    'Massachusetts State Police - Leominster': 'State Police, Leominster' };
  var nice = function (n) { return NICE[n] || n; };
  var A = null;

  function get(path) { return path.split('.').reduce(function (o, k) { return o == null ? o : o[k]; }, A); }
  function fmt(v) { if (typeof v !== 'number') return v; return v >= 100 ? Math.round(v).toLocaleString('en-US') : (Math.round(v * 10) / 10).toString(); }

  // ---------- flat maps ----------
  function mapImg(fig) {
    if (fig.querySelector('img')) return;
    var im = new Image(); im.src = BASE + fig.dataset.img; im.alt = fig.dataset.alt || ''; im.decoding = 'async'; im.loading = 'lazy'; fig.prepend(im);
  }
  function label(fig, pos, html, cls) {
    var d = document.createElement('div'); d.className = 'ml ' + (cls || ''); d.style.left = pos[0] + '%'; d.style.top = pos[1] + '%'; d.innerHTML = html; fig.appendChild(d); return d;
  }
  function dot(fig, pos, color) { var d = document.createElement('div'); d.className = 'dot'; d.style.left = pos[0] + '%'; d.style.top = pos[1] + '%'; d.style.setProperty('--c', color); fig.appendChild(d); }
  function side(pos) { return pos[1] < 14 ? 'below' : ''; }
  function spread(items, minDist) {   // drop labels that would sit on top of a stronger one (items are in priority order)
    var out = []; items.forEach(function (it) { if (out.every(function (o) { return Math.hypot(o.pos[0] - it.pos[0], (o.pos[1] - it.pos[1]) * 1.4) > minDist; })) out.push(it); }); return out;
  }
  var FAC = { hospital: ['#c52233', 'H'], fire: ['#e8590c', 'F'], police: ['#1a5fb4', 'P'] };
  function facMarker(fig, f) { var m = document.createElement('div'); m.className = 'mk ' + f.kind; m.textContent = FAC[f.kind][1]; m.style.left = f.pos[0] + '%'; m.style.top = f.pos[1] + '%'; m.title = nice(f.name); fig.appendChild(m); }

  function buildMaps() {
    document.querySelectorAll('.mapfig').forEach(mapImg);
    var f;
    // 1 rain
    f = $('#s-rain .mapfig'); label(f, A.rain.pos, A.rain.max_mmh + ' mm/h<small>wettest radar square, 6:48 PM</small>', side(A.rain.pos) || 'below');
    // 2 ground
    f = $('#s-ground .mapfig');
    A.ground.streams.forEach(function (s) { label(f, s.pos, esc(s.name), 'stream'); });
    label(f, [Math.max(A.ground.high_pos[0], 7), A.ground.high_pos[1]], A.ground.high_m + ' m<small>highest ground</small>', 'right');
    label(f, [Math.min(A.ground.low_pos[0], 93), Math.min(A.ground.low_pos[1], 95)], A.ground.low_m + ' m<small>lowest point</small>', 'left');
    // 3 water
    f = $('#s-water .mapfig');
    var ds = A.roads.streets[0]; dot(f, ds.pos, '#08306b');
    label(f, ds.pos, esc(ds.name) + '<small>' + (ds.d / 100).toFixed(2) + ' m of water</small>');
    A.ground.streams.forEach(function (s) { if (/Nashua|Monoosnoc/.test(s.name)) label(f, s.pos, esc(s.name), 'stream'); });
    // 4 close-up
    f = $('#s-road .mapfig'); var C = A.closeup;
    label(f, C.top[1], 'Second-deepest dot<small>the road\'s depth: ' + C.d + ' cm</small>');
    label(f, [C.pos[0], C.pos[1] + 4], esc(C.name), 'below');
    // 5 roads
    f = $('#s-closed .mapfig');
    spread(A.roads.streets, innerWidth < 700 ? 16 : 9).slice(0, innerWidth < 700 ? 4 : 6).forEach(function (s) { dot(f, s.pos, '#e8590c'); label(f, s.pos, esc(s.name) + '<small>' + s.d + ' cm · closed</small>', side(s.pos)); });
    // 6 access
    f = $('#accfig'); A.access.facilities.forEach(function (x) { facMarker(f, x); });
    spread(A.access.facilities.filter(function (x) { return x.kind !== 'police'; }), 10).forEach(function (x) { label(f, x.pos, esc(nice(x.name)), side(x.pos)); });
    // 7 reports
    f = $('#s-check .mapfig'); var tip = null;
    A.check.reports.forEach(function (r) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'rep'; b.style.left = r.pos[0] + '%'; b.style.top = r.pos[1] + '%';
      var t = new Date(r.t); var when = t.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York' });
      b.setAttribute('aria-label', 'Report, ' + when + ': ' + r.text);
      b.addEventListener('click', function (e) {
        e.stopPropagation(); if (tip) tip.remove();
        tip = document.createElement('div'); tip.className = 'reptip'; tip.innerHTML = '<b>' + esc(when) + ' · ' + (r.src === 'LSR' ? 'NWS storm report' : 'NOAA Storm Events') + '</b>' + esc(r.text);
        tip.style.left = Math.min(r.pos[0], 62) + '%'; tip.style.top = (r.pos[1] + 3) + '%'; f.appendChild(tip);
      });
      f.appendChild(b);
    });
    document.addEventListener('click', function () { if (tip) { tip.remove(); tip = null; } });
  }


  // ---------- zoom and pan inside a step picture (buttons, double-click, drag, pinch; the wheel once zoomed or with Ctrl) ----------
  function zoomify(fig) {
    var img = fig.querySelector('img'); if (!img || fig._z) return;
    var Z = fig._z = { s: 1, x: 0, y: 0 }, items = [];
    function collect() { items = Array.prototype.filter.call(fig.children, function (e) { return e !== img && !e.classList.contains('zbar') && e.style.left; })
      .map(function (e) { if (e.dataset.bx == null) { e.dataset.bx = parseFloat(e.style.left); e.dataset.by = parseFloat(e.style.top); } return e; }); }
    function clamp() { Z.s = Math.max(1, Math.min(6, Z.s)); var lo = 100 - 100 * Z.s; Z.x = Math.min(0, Math.max(lo, Z.x)); Z.y = Math.min(0, Math.max(lo, Z.y)); }
    function apply() {
      clamp(); img.style.transformOrigin = '0 0'; img.style.transform = 'translate(' + Z.x + '%,' + Z.y + '%) scale(' + Z.s + ')';
      if (!items.length) collect();
      items.forEach(function (e) { var x = +e.dataset.bx * Z.s + Z.x, y = +e.dataset.by * Z.s + Z.y; e.style.left = x + '%'; e.style.top = y + '%'; e.style.display = (x < -2 || x > 102 || y < -2 || y > 102) ? 'none' : ''; });
      fig.classList.toggle('zoomed', Z.s > 1.01); rs.disabled = Z.s <= 1.01;
    }
    function zoomAt(f, px, py) { var r = fig.getBoundingClientRect(), u = (px - r.left) / r.width * 100, v = (py - r.top) / r.height * 100, s0 = Z.s; Z.s *= f; clamp(); var k = Z.s / s0; Z.x = u - (u - Z.x) * k; Z.y = v - (v - Z.y) * k; apply(); }
    var bar = document.createElement('div'); bar.className = 'zbar';
    bar.innerHTML = '<button type="button" aria-label="Zoom in">+</button><button type="button" aria-label="Zoom out">−</button><button type="button" aria-label="Reset zoom">⤢</button>';
    fig.appendChild(bar); var bs = bar.querySelectorAll('button'), rs = bs[2];
    var mid = function () { var r = fig.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; };
    bs[0].onclick = function (e) { e.stopPropagation(); var m = mid(); zoomAt(1.6, m[0], m[1]); };
    bs[1].onclick = function (e) { e.stopPropagation(); var m = mid(); zoomAt(1 / 1.6, m[0], m[1]); };
    rs.onclick = function (e) { e.stopPropagation(); Z.s = 1; Z.x = Z.y = 0; apply(); };
    fig.addEventListener('dblclick', function (e) { if (e.target.closest('.zbar,.rep')) return; zoomAt(e.shiftKey ? 1 / 2 : 2, e.clientX, e.clientY); });
    fig.addEventListener('wheel', function (e) { if (Z.s <= 1.01 && !e.ctrlKey) return; e.preventDefault(); zoomAt(Math.exp(-e.deltaY * 0.0022), e.clientX, e.clientY); }, { passive: false });
    var drag = null, pts = {};
    fig.addEventListener('pointerdown', function (e) { if (e.target.closest('.zbar,.rep')) return; pts[e.pointerId] = [e.clientX, e.clientY];
      if (Object.keys(pts).length === 1 && Z.s > 1.01) { drag = [e.clientX, e.clientY, Z.x, Z.y]; fig.setPointerCapture(e.pointerId); } });
    fig.addEventListener('pointermove', function (e) {
      if (!pts[e.pointerId]) return; var prev = pts[e.pointerId]; pts[e.pointerId] = [e.clientX, e.clientY]; var ks = Object.keys(pts);
      if (ks.length === 2) { var a = pts[ks[0]], b = pts[ks[1]], pa = ks[0] == e.pointerId ? prev : a, pb = ks[1] == e.pointerId ? prev : b;
        var d0 = Math.hypot(pa[0] - pb[0], pa[1] - pb[1]), d1 = Math.hypot(a[0] - b[0], a[1] - b[1]); if (d0 > 0) zoomAt(d1 / d0, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2); drag = null; return; }
      if (drag) { var r = fig.getBoundingClientRect(); Z.x = drag[2] + (e.clientX - drag[0]) / r.width * 100; Z.y = drag[3] + (e.clientY - drag[1]) / r.height * 100; apply(); } });
    var up = function (e) { delete pts[e.pointerId]; drag = null; };
    fig.addEventListener('pointerup', up); fig.addEventListener('pointercancel', up);
    var hint = document.createElement('p'); hint.className = 'zhint'; hint.textContent = 'Double-click or press + to zoom in; drag to move around.'; fig.after(hint);
    fig._zreset = function () { items = []; Z.s = 1; Z.x = Z.y = 0; apply(); };
    apply();
  }

  // ---------- legends and numbers ----------
  function legends() {
    $('#lg-rain').innerHTML = [['#9ee08c', '0.5'], ['#3eb34e', '2.5'], ['#f7d320', '10'], ['#ff8c00', '25'], ['#de1e2d', '50+']].map(function (c) { return '<span><i class="sw" style="background:' + c[0] + '"></i>' + c[1] + '</span>'; }).join('') + '<span style="color:var(--s-mut)">mm per hour</span>';
    $('#lg-depth').innerHTML = '<div class="ramp"><small>1 cm</small><i style="background:linear-gradient(90deg,#c6dbef,#9ecae1 20%,#6baed6 40%,#2171b5 65%,#08306b)"></i><small>1 m +</small></div><span style="color:var(--s-mut)">water depth · 5, 15 and 30 cm are the road thresholds</span>';
    $('#lg-roads').innerHTML = '<span><i class="ln" style="background:#f2c14e"></i>5–15 cm, slower</span><span><i class="ln" style="background:#f0a202"></i>15–30 cm, at risk</span><span><i class="ln" style="background:#e8590c"></i>30 cm +, closed</span>';
    $('#lg-access').innerHTML = '<span><i class="ln" style="background:#7c5cc4"></i>no longer reached in time</span><span><i class="ln" style="background:#e8590c"></i>closed</span><span><i class="mk hospital" style="position:static;display:inline-grid;margin:0 6px 0 0;width:14px;height:14px">H</i>hospital</span><span><i class="mk fire" style="position:static;display:inline-grid;margin:0 6px 0 0;width:14px;height:14px">F</i>fire</span><span><i class="mk police" style="position:static;display:inline-grid;margin:0 6px 0 0;width:14px;height:14px">P</i>police</span>';
    $('#lg-check').innerHTML = '<span><i class="ln" style="background:#e8590c"></i>closed by the model</span><span><i class="sw" style="background:#6d28d9;border-radius:50%;width:12px;height:12px"></i>flood report</span>';
    // rain per hour (model-area mean), noon to 1 AM
    var H = A.rain.hourly_mm, mx = Math.max.apply(null, H);
    $('#hourly').innerHTML = H.map(function (v, i) { var hr = (12 + i) % 12 || 12, ap = (12 + i) % 24 < 12 ? 'AM' : 'PM';
      return '<i class="' + (i === 6 ? 'now' : '') + '" style="height:' + Math.max(2, 100 * v / mx) + '%" title="' + hr + ' ' + ap + ': ' + v + ' mm"><em>' + (i % 3 === 0 || i === 6 ? hr + (i === 6 ? ' ' + ap : '') : '') + '</em></i>'; }).join('');
  }
  var ACC = { fire_station: 'a fire truck can no longer reach within 8 minutes', hospital: 'no longer within 30 minutes of a hospital', police: 'police can no longer reach within 10 minutes' };
  function numbers(service) {
    A.acc = { km: A.access.lost_km[service || 'fire_station'] }; A.check.n = A.check.reports.length;
    document.querySelectorAll('[data-k]').forEach(function (e) { var v = get(e.dataset.k); if (v != null) e.textContent = fmt(v); });
  }
  function accessToggle() {
    document.querySelectorAll('#accseg button').forEach(function (b) {
      b.addEventListener('click', function () {
        document.querySelectorAll('#accseg button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        var s = b.dataset.s; $('#accfig img').src = BASE + 'L_access_' + s + '.jpg'; $('#accwhat').textContent = ACC[s]; numbers(s);
      });
    });
    ['hospital', 'police'].forEach(function (s) { var i = new Image(); i.src = BASE + 'L_access_' + s + '.jpg'; });   // ready before the click
  }

  // ---------- the stack ----------
  function stack() {
    var S = A.stack, fig = $('#stackfig'), ar = S.size[0] / S.size[1], IW = 0.5, ar2 = ar / IW;
    fig.style.setProperty('--ard', ar2.toFixed(4));
    var X = function (p) { return 50 - IW * 50 + p[0] * IW; };
    var proj = function (k, pos) { var c = S.corners[k], u = pos[0] / 100, v = pos[1] / 100;
      return [c[0][0] + u * (c[1][0] - c[0][0]) + v * (c[3][0] - c[0][0]), c[0][1] + u * (c[1][1] - c[0][1]) + v * (c[3][1] - c[0][1])]; };
    var svg = $('#stackLines'), L = $('#stackLabels'), lines = '', html = '';
    var LAY = [['Rain', 'radar, every few minutes'], ['Ground', 'lidar heights in 20 m squares'], ['Water', 'flood engine, depth every 5 min'],
      ['Roads', 'open, at risk or closed'], ['Access', 'purple: help can\'t arrive in time']];
    LAY.forEach(function (t, k) {
      var c = S.corners[k], p = [c[0][0] + 0.72 * (c[3][0] - c[0][0]), c[0][1] + 0.72 * (c[3][1] - c[0][1])], ax = X(p), lx = 22;
      lines += '<line x1="' + (lx + 1) + '" y1="' + p[1] + '" x2="' + ax + '" y2="' + p[1] + '"/><circle cx="' + ax + '" cy="' + p[1] + '" r=".35"/>';
      html += '<div class="sl left" style="right:' + (100 - lx) + '%;top:' + p[1] + '%"><b><span class="n">' + (k + 1) + '</span>' + t[0] + '</b>' + t[1] + '</div>';
    });
    var ds = A.roads.streets, R = [
      [0, A.rain.pos, A.rain.max_mmh + ' mm/h', 'heaviest rain at 6:48 PM', '#3eb34e'],
      [1, (A.ground.streams.filter(function (s) { return /Monoosnoc/.test(s.name); })[0] || A.ground.streams[0]).pos, 'Monoosnoc Brook', 'runs through downtown', '#0b4f8a'],
      [2, ds[0].pos, (ds[0].d / 100).toFixed(2) + ' m of water', 'on ' + ds[0].name, '#08306b'],
      [3, (ds[4] || ds[1]).pos, (ds[4] || ds[1]).name + ' closed', (ds[4] || ds[1]).d + ' cm deep', '#e8590c'],
      [4, (A.access.facilities.filter(function (f) { return f.kind === 'hospital'; })[0] || A.access.facilities[0]).pos, 'HealthAlliance Hospital', A.access.lost_km.hospital + ' km of streets beyond 30 min', '#c52233']];
    var ys = [];
    R.forEach(function (r) {
      var p = proj(r[0], r[1]), ax = X(p), y = p[1];
      ys.forEach(function (q) { if (Math.abs(q - y) < 7.5) y = q + 7.5; }); ys.push(y);
      var lx = 78;
      lines += '<line x1="' + ax + '" y1="' + p[1] + '" x2="' + (lx - 1) + '" y2="' + y + '"/><circle cx="' + ax + '" cy="' + p[1] + '" r=".35"/>';
      html += '<div class="sl right" style="left:' + lx + '%;top:' + y + '%;--c:' + r[4] + '"><b>' + esc(r[2]) + '</b>' + esc(r[3]) + '</div>';
    });
    A.stack.facilities.forEach(function (f) { var p = [X(f.p), f.p[1]]; html += '<div class="mk ' + f.kind + '" style="left:' + p[0] + '%;top:' + p[1] + '%;width:14px;height:14px;margin:-7px 0 0 -7px;font-size:8px" title="' + esc(nice(f.name)) + '">' + FAC[f.kind][1] + '</div>'; });
    svg.innerHTML = lines; L.innerHTML = html;
    svg.querySelectorAll('circle').forEach(function (c) {   // end points as HTML dots: they stay round when the figure is stretched
      var m = document.createElement('div'); m.className = 'dot'; m.style.left = c.getAttribute('cx') + '%'; m.style.top = c.getAttribute('cy') + '%';
      m.style.width = m.style.height = '9px'; m.style.margin = '-4.5px 0 0 -4.5px'; m.style.borderWidth = '2px'; L.appendChild(m); c.remove();
    });
  }

  // ---------- step bar ----------
  function stepbar() {
    var links = document.querySelectorAll('#stepbar a'), secs = Array.prototype.map.call(links, function (a) { return document.getElementById(a.dataset.s); });
    var io = new IntersectionObserver(function (ent) {
      ent.forEach(function (e) { if (e.isIntersecting) links.forEach(function (a) { a.classList.toggle('on', a.dataset.s === e.target.id); }); });
    }, { rootMargin: '-45% 0px -50% 0px' });
    secs.forEach(function (s) { if (s) io.observe(s); });
  }

  // ---------- the tree ----------
  function tree(T) {
    var COLS = [1, 2, 3, 4, 5, 6, 8], byId = {}, el = {}, main = new Set(T.follow || []), sel = null, showAll = false, stepIx = -1;
    T.nodes.forEach(function (n) { byId[n.id] = n; });
    var stage = {}; T.stages.forEach(function (s) { stage[s.id] = s; });
    var root = $('#tree'), svg = $('#tlines');
    COLS.forEach(function (sid, ci) {
      var col = document.createElement('div'); col.className = 'tcol'; col.dataset.c = ci;
      col.innerHTML = '<h3>' + (ci + 1) + '. ' + esc(stage[sid].title) + '<span>' + esc(stage[sid].sub) + '</span></h3>';
      T.nodes.filter(function (n) { return n.stage === sid; }).sort(function (a, b) { return (a.type === 'engine' ? -9 : a.row) - (b.type === 'engine' ? -9 : b.row); }).forEach(function (n) {
        var b = document.createElement('button'); b.type = 'button'; b.className = 'tnode' + (main.has(n.id) ? ' main' : '') + (/candidate|opt-in|not in p_close/.test(n.status) ? ' opt' : '');
        b.textContent = n.title; b.dataset.id = n.id; b.addEventListener('click', function (e) { e.stopPropagation(); pick(n.id); });
        el[n.id] = b; col.appendChild(b);
      });
      root.appendChild(col);
    });
    var bands = [[7, 'Before the storm (forecast)', ''], [9, 'What-if only (not live)', 'whatif'], [10, 'Can\'t capture yet', 'limit']];
    $('#tbands').innerHTML = bands.map(function (b) {
      return '<div class="band ' + b[2] + '"><h4>' + b[1] + '</h4><div class="chips">' + T.nodes.filter(function (n) { return n.stage === b[0]; }).map(function (n) { return '<button type="button" data-id="' + n.id + '">' + esc(n.title) + '</button>'; }).join('') + '</div></div>';
    }).join('');
    $('#tbands').addEventListener('click', function (e) { var b = e.target.closest('button[data-id]'); if (b) { e.stopPropagation(); pick(b.dataset.id); } });
    function draw() {
      var r0 = root.getBoundingClientRect(); svg.setAttribute('width', r0.width); svg.setAttribute('height', r0.height); svg.setAttribute('viewBox', '0 0 ' + r0.width + ' ' + r0.height);
      var rel = new Set(), out = '';
      T.edges.forEach(function (e) {
        var a = el[e.source], b = el[e.target]; if (!a || !b) return;
        var isMain = main.has(e.source) && main.has(e.target) && (T.follow.indexOf(e.target) === T.follow.indexOf(e.source) + 1);
        var isRel = sel && (e.source === sel || e.target === sel);
        if (!isMain && !isRel && !showAll) return;
        if (isRel) { rel.add(e.source); rel.add(e.target); }
        var ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        var x1 = ra.right - r0.left, y1 = ra.top + ra.height / 2 - r0.top, x2 = rb.left - r0.left, y2 = rb.top + rb.height / 2 - r0.top;
        if (x2 < x1) { x1 = ra.left - r0.left; x2 = rb.right - r0.left; }
        if (Math.abs(x2 - x1) < 5) { x1 = ra.left - r0.left; x2 = rb.left - r0.left; var k = -22;
          out += '<path class="' + (isRel ? 'rel' : isMain ? 'main' : '') + '" d="M' + x1 + ' ' + y1 + ' C' + (x1 + k) + ' ' + y1 + ',' + (x2 + k) + ' ' + y2 + ',' + x2 + ' ' + y2 + '"/>'; return; }
        var dx = Math.max(24, Math.abs(x2 - x1) * 0.45) * (x2 > x1 ? 1 : -1);
        out += '<path class="' + (isRel ? 'rel' : isMain ? 'main' : '') + '" d="M' + x1 + ' ' + y1 + ' C' + (x1 + dx) + ' ' + y1 + ',' + (x2 - dx) + ' ' + y2 + ',' + x2 + ' ' + y2 + '"/>';
      });
      svg.innerHTML = out;
      Object.keys(el).forEach(function (id) { el[id].classList.toggle('sel', id === sel); el[id].classList.toggle('rel', rel.has(id) && id !== sel); });
    }
    var card = $('#tcard');
    function showCard(html) { card.innerHTML = '<button class="x" type="button" aria-label="Close">×</button>' + html; card.hidden = false; card.querySelector('.x').onclick = function () { card.hidden = true; sel = null; draw(); }; }
    function pick(id) {
      sel = id; var n = byId[id]; draw();
      var pm = (n.parameters || []).filter(function (p) { return p.value != null && p.value !== ''; }).map(function (p) { return '<span>' + esc(p.name) + '</span><span>' + esc(p.value) + (p.unit ? ' ' + esc(p.unit) : '') + '</span>'; }).join('');
      var src = (n.source || []).map(function (s) { return '<li>' + (s.url ? '<a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.text) + '</a>' : esc(s.text)) + '</li>'; }).join('');
      var nx = (n.next || []).map(function (x) { return byId[x.to] ? '<li><b>' + esc(byId[x.to].title) + '</b>: ' + esc(x.what) + '</li>' : ''; }).join('');
      showCard('<p class="k">' + esc(stage[n.stage].title) + ' · ' + esc(n.status) + '</p><h3>' + esc(n.title) + '</h3><p class="pl">' + esc(n.plain) + '</p>' +
        (n.what ? '<h4>How it works</h4><p>' + esc(n.what) + '</p>' : '') + (n.output && n.output !== '—' ? '<h4>What it gives</h4><p>' + esc(n.output) + '</p>' : '') +
        (nx ? '<h4>Feeds into</h4><ul>' + nx + '</ul>' : '') + (pm ? '<h4>Values used</h4><div class="pm">' + pm + '</div>' : '') +
        (n.limits && n.limits !== '—' ? '<h4>Limits</h4><p>' + esc(n.limits) + '</p>' : '') + (src ? '<h4>Sources</h4><ul>' + src + '</ul>' : ''));
    }
    function step(d) {
      stepIx = Math.max(0, Math.min(COLS.length - 1, stepIx + d)); sel = null;
      root.querySelectorAll('.tcol').forEach(function (c) { var on = +c.dataset.c === stepIx; c.classList.toggle('dim', !on); c.classList.toggle('on', on); });
      var sid = COLS[stepIx], ns = T.nodes.filter(function (n) { return n.stage === sid; }).sort(function (a, b) { return a.row - b.row; });
      showCard('<p class="k">Step ' + (stepIx + 1) + ' of ' + COLS.length + '</p><h3>' + esc(stage[sid].title) + '</h3><p class="pl">' + esc(stage[sid].sub) + '</p><ul class="stg">' +
        ns.map(function (n) { return '<li><b>' + esc(n.title) + '.</b> ' + esc(n.plain) + '</li>'; }).join('') + '</ul>');
      $('#tNext').textContent = stepIx === COLS.length - 1 ? 'Done' : 'Next'; draw();
      var c = root.querySelector('.tcol[data-c="' + stepIx + '"]'); if (c) c.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' });
    }
    $('#tNext').onclick = function () { if (stepIx === COLS.length - 1) { stepIx = -1; root.querySelectorAll('.tcol').forEach(function (c) { c.classList.remove('dim', 'on'); }); card.hidden = true; $('#tNext').textContent = 'Start'; return; } step(1); };
    $('#tPrev').onclick = function () { if (stepIx > 0) step(-1); };
    $('#tAll').onclick = function () { showAll = !showAll; this.textContent = showAll ? 'Main path only' : 'Show everything'; draw(); };
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { card.hidden = true; sel = null; draw(); } });
    window.addEventListener('resize', draw); draw();
    if (document.fonts) document.fonts.ready.then(draw);
  }

  fetch(BASE + 'anchors.json').then(function (r) { return r.json(); }).then(function (j) {
    A = j; buildMaps(); document.querySelectorAll('.mapfig').forEach(zoomify); legends(); numbers('fire_station'); accessToggle(); stack(); stepbar();
  }).catch(function (e) { console.error('how it works', e); });
  fetch('model-tree/tree.json').then(function (r) { return r.json(); }).then(tree).catch(function (e) { console.error('tree', e); });
})();
