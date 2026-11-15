/* Model tree (docs/model-tree.html): built from docs/model-tree/tree.json (proto/model_tree.py). Libraries bundled in model-tree/lib. */
(function () {
  'use strict';
  var CW = 380, RH = 190, W = 300, H = 160, EW = 320, EH = 420;
  var COL = { input: '#2f7d4f', process: '#5b5f97', engine: '#0b5c8a', output: '#0b5c8a', check: '#b5562a', label: '#7a6a1e', limit: '#8a8f96' };
  var T, cy, byId = {}, level = -1, simple = true, follow = -1;
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var dark = function () { var d = document.documentElement.dataset.theme; return d ? d === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; };

  function fmtVal(p) {
    var v = p.value;
    if (typeof v === 'string' && /^[0-9.]+,[0-9.]+$/.test(v)) v = v.replace(',', ', ');
    if (v === 1 && /parity|fix|switch|enforcement|output|4-connected/i.test(p.name) && !p.unit) v = 'on (1)';
    return v + (p.unit ? ' ' + p.unit : '');
  }
  function stName(n) { var s = T.stages.filter(function (x) { return x.id === n.stage; })[0]; return s ? s.title : ''; }
  function stClass(s) { s = s || ''; return /what-if/.test(s) ? 'st-whatif' : /can't/.test(s) ? 'st-limit' : /candidate/.test(s) ? 'st-cand' : 'st-live'; }

  function label(n) {
    if (level === 0) return n.title;
    if (level === 1 || simple) return n.title + '\n\n' + n.plain;
    var L = [n.title];
    var meta = [n.units, n.resolution].filter(Boolean).join(' · ');
    if (meta) L.push(meta);
    if (n.source && n.source.length) L.push('Source: ' + n.source.map(function (s) { return s.text.split(/[,(]/)[0]; }).slice(0, 2).join('; '));
    if (n.formula_text) L.push(n.formula_text);
    (n.parameters || []).slice(0, 3).forEach(function (p) { L.push(p.name + ' = ' + fmtVal(p)); });
    if (n.status && n.status !== 'live') L.push('[' + n.status + ']');
    return L.join('\n');
  }

  function elements() {
    var els = [], bands = {};
    function band(key, txt) { if (!bands[key]) bands[key] = { txt: txt, x0: 1e9, y0: 1e9, x1: -1e9, y1: -1e9 }; return bands[key]; }
    T.nodes.forEach(function (n) {
      byId[n.id] = n;
      var big = n.type === 'engine', w = big ? EW : W, h = big ? EH : H;
      var x = n.col * CW, y = n.row * RH + (big ? RH * 0.5 : 0);
      var b = n.stage === 7 ? band('fc', 'Forecast (before the storm)') : n.stage === 9 ? band('wi', 'What-if only (not live)') : n.stage === 10 ? band('cc', "Can't capture yet (named limitations)") : band('c' + n.col, T.columns[n.col]);
      b.x0 = Math.min(b.x0, x - w / 2); b.x1 = Math.max(b.x1, x + w / 2); b.y0 = Math.min(b.y0, y - h / 2); b.y1 = Math.max(b.y1, y + h / 2);
      els.push({ group: 'nodes', data: { id: n.id, label: n.title, color: n.status === 'what-if only' ? '#7b4fa0' : (COL[n.type] || '#5b5f97'), w: w, h: h },
                 position: { x: x, y: y }, classes: [n.type, n.status === 'what-if only' ? 'whatif' : '', n.type === 'limit' ? 'limit' : '', /candidate/.test(n.status || '') ? 'cand' : ''].join(' ') });
    });
    Object.keys(bands).forEach(function (k) {
      var b = bands[k], pad = 26, top = 58;
      els.push({ group: 'nodes', data: { id: 'band_' + k, label: b.txt, bw: b.x1 - b.x0 + 2 * pad, bh: b.y1 - b.y0 + pad + top },
                 position: { x: (b.x0 + b.x1) / 2, y: (b.y0 + b.y1) / 2 - (top - pad) / 2 }, classes: 'band', selectable: false, grabbable: false });
    });
    T.edges.forEach(function (e, i) { els.push({ group: 'edges', data: { id: 'e' + i, source: e.source, target: e.target, label: e.label }, classes: e.kind }); });
    return els;
  }

  function style() {
    var ink = dark() ? '#e8eaed' : '#1f2328', bg = dark() ? '#1c2026' : '#ffffff', muted = dark() ? '#a3abb4' : '#5d6670', bandc = dark() ? '#78aadc' : '#1f5f99';
    return [
      { selector: 'node', style: { shape: 'round-rectangle', width: 'data(w)', height: 'data(h)', 'background-color': bg, 'border-width': 2.5, 'border-color': 'data(color)',
          label: 'data(label)', 'text-wrap': 'wrap', 'text-max-width': W - 28, 'text-valign': 'center', 'text-halign': 'center', color: ink, 'font-size': 16,
          'font-family': 'system-ui,-apple-system,Segoe UI,Roboto,sans-serif', 'z-index': 10, 'min-zoomed-font-size': 0 } },
      { selector: 'node.engine', style: { 'border-width': 6, 'text-max-width': EW - 30, 'background-color': dark() ? '#10283a' : '#eef5fb' } },
      { selector: 'node.output', style: { 'border-width': 4 } },
      { selector: 'node.whatif', style: { 'border-style': 'dashed' } },
      { selector: 'node.cand', style: { 'border-style': 'dashed', 'border-dash-pattern': [10, 4] } },
      { selector: 'node.limit', style: { 'background-color': dark() ? '#262a30' : '#eeeeec', color: muted } },
      { selector: 'node.band', style: { shape: 'round-rectangle', width: 'data(bw)', height: 'data(bh)', 'background-color': bandc, 'background-opacity': 0.07, 'border-width': 0, label: 'data(label)',
          'text-valign': 'top', 'text-halign': 'center', 'text-margin-y': 44, 'font-size': 26, 'font-weight': 700, color: muted, 'z-index': 0, events: 'no', 'text-max-width': 2000 } },
      { selector: 'node.L0', style: { 'font-size': 27, 'font-weight': 700 } },
      { selector: 'node.L1', style: { 'font-size': 16 } },
      { selector: 'node.L2', style: { 'font-size': 11, 'text-valign': 'center' } },
      { selector: 'edge', style: { width: 2, 'line-color': muted, 'target-arrow-color': muted, 'target-arrow-shape': 'triangle', 'curve-style': 'unbundled-bezier',
          'control-point-distances': [0], 'control-point-weights': [0.5], 'arrow-scale': 1.1, opacity: 0.75, 'z-index': 5, label: '', 'font-size': 10, color: ink,
          'text-background-color': bg, 'text-background-opacity': 0.9, 'text-background-padding': 2, 'text-rotation': 'autorotate' } },
      { selector: 'edge.L1', style: { label: 'data(label)' } },
      { selector: 'edge.label', style: { 'line-style': 'dotted', 'line-color': '#9a8a3e', 'target-arrow-color': '#9a8a3e' } },
      { selector: 'edge.whatif', style: { 'line-style': 'dashed', 'line-color': '#7b4fa0', 'target-arrow-color': '#7b4fa0' } },
      { selector: 'edge.limit', style: { 'line-style': 'dashed', 'line-color': '#8a8f96', 'target-arrow-color': '#8a8f96', 'target-arrow-shape': 'tee' } },
      { selector: '.faded', style: { opacity: 0.12 } },
      { selector: 'edge.hl', style: { width: 4, opacity: 1, 'line-color': '#1f5f99', 'target-arrow-color': '#1f5f99', label: 'data(label)', 'z-index': 20 } },
      { selector: 'node.hl', style: { 'border-width': 5 } },
      { selector: 'node:selected', style: { 'border-width': 7, 'border-color': '#e08a00', 'overlay-opacity': 0 } }
    ];
  }

  function setLevel() {
    var z = cy.zoom(), L = z < 0.55 ? 0 : z < 1.05 ? 1 : 2;
    if (L === level) return; level = L;
    cy.batch(function () {
      cy.nodes().not('.band').forEach(function (e) { e.removeClass('L0 L1 L2').addClass('L' + L); e.data('label', label(byId[e.id()])); });
      cy.edges().toggleClass('L1', L >= 1);
    });
  }
  function relabel() { var l = level; level = -1; setLevel(); if (l === level) {} }

  function highlight(n) {
    cy.elements().removeClass('faded hl');
    if (!n) return;
    var up = n.predecessors(), down = n.successors(), keep = up.union(down).union(n);
    cy.elements().not(keep).not('.band').addClass('faded');
    keep.edges().addClass('hl'); keep.nodes().addClass('hl');
  }

  function listLinks(arr, key) {
    return '<ul>' + arr.map(function (x) { var o = byId[x[key]]; return '<li><span class="jump" data-id="' + esc(x[key]) + '">' + esc(o ? o.title : x[key]) + '</span> — ' + esc(x.what) + '</li>'; }).join('') + '</ul>';
  }
  function tex(s, display) { try { return katex.renderToString(s, { displayMode: !!display, throwOnError: false, output: 'html' }); } catch (e) { return esc(s); } }

  function panel(n) {
    var P = $('panel'), h = [];
    h.push('<button class="btn close" id="pClose" type="button" aria-label="Close">✕</button>');
    if (follow >= 0) h.push('<div class="nav"><button class="btn" id="fPrev" type="button">◀ Back</button><button class="btn on" id="fNext" type="button">Next ▶</button><button class="btn" id="fStop" type="button">Stop</button><span class="where">step ' + (follow + 1) + ' of ' + T.follow.length + '</span></div>');
    h.push('<h2>' + esc(n.title) + '</h2><div class="chips"><span class="chip">' + esc(stName(n)) + '</span><span class="chip">' + esc(n.type) + '</span><span class="chip ' + stClass(n.status) + '">' + esc(n.status) + '</span></div>');
    h.push('<div class="plain">' + esc(n.plain) + '</div>');
    h.push('<div class="sci">');
    if (n.what) h.push('<h3>What it is</h3><p>' + esc(n.what) + '</p>');
    var meta = [['Units', n.units], ['Resolution', n.resolution], ['Period', n.period]].filter(function (r) { return r[1]; });
    if (meta.length) h.push('<table>' + meta.map(function (r) { return '<tr><td>' + r[0] + '</td><td>' + esc(r[1]) + '</td></tr>'; }).join('') + '</table>');
    if (n.how_used) h.push('<h3>How it enters the model</h3><p>' + esc(n.how_used) + '</p>');
    if (n.formula) {
      h.push('<h3>Formula</h3><div class="formula">' + tex(n.formula, true) + '</div>');
      if (n.symbols && n.symbols.length) h.push('<table>' + n.symbols.map(function (s) { return '<tr><td>' + tex(s[0]) + '</td><td>' + esc(s[1]) + '</td></tr>'; }).join('') + '</table>');
    }
    if (n.parameters && n.parameters.length) h.push('<h3>Parameter values (read from the code)</h3><table>' + n.parameters.map(function (p) {
      return '<tr><td>' + esc(p.name) + '<div class="where">' + esc(p.origin) + '<br>in the code: ' + esc(p.where) + '</div></td><td class="v">' + esc(fmtVal(p)) + '</td></tr>'; }).join('') + '</table>');
    if (n.output) h.push('<h3>What comes out</h3><p>' + esc(n.output) + '</p>');
    if (n.limits) h.push('<h3>What it cannot capture</h3><p>' + esc(n.limits) + '</p>');
    if (n.source && n.source.length) h.push('<h3>Sources</h3><ul>' + n.source.map(function (s) { return '<li>' + (s.url ? '<a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.text) + '</a>' : esc(s.text)) + '</li>'; }).join('') + '</ul>');
    if (n.code && n.code.length) h.push('<h3>Code</h3><ul>' + n.code.map(function (c) { return '<li><a href="' + esc(c.url) + '" target="_blank" rel="noopener"><code>' + esc(c.path) + '</code></a>' + (c.fn ? ' · ' + esc(c.fn) : '') + '</li>'; }).join('') + '</ul>');
    h.push('</div>');
    if (n.from && n.from.length) h.push('<h3>Comes from</h3>' + listLinks(n.from, 'frm'));
    if (n.next && n.next.length) h.push('<h3>Goes to</h3>' + listLinks(n.next, 'to'));
    P.innerHTML = h.join(''); P.scrollTop = 0; document.body.classList.add('panel-open'); $('legend').open = false;
    $('pClose').onclick = function () { cy.$(':selected').unselect(); closePanel(); };
    Array.prototype.forEach.call(P.querySelectorAll('.jump'), function (a) { a.onclick = function () { select(a.dataset.id, true); }; });
    if (follow >= 0) { $('fPrev').onclick = function () { step(-1); }; $('fNext').onclick = function () { step(1); }; $('fStop').onclick = stopFollow; }
  }
  function closePanel() { document.body.classList.remove('panel-open'); highlight(null); history.replaceState(null, '', location.pathname + location.search); setTimeout(function () { cy.resize(); }, 50); }

  function select(id, center) {
    var e = cy.getElementById(id); if (!e || !e.length) return;
    cy.$(':selected').unselect(); e.select(); highlight(e); panel(byId[id]);
    history.replaceState(null, '', '#node=' + id);
    setTimeout(function () { cy.resize(); if (center) cy.animate({ center: { eles: e }, zoom: Math.max(cy.zoom(), 0.9) }, { duration: 350 }); }, 60);
  }

  function step(d) {
    follow = Math.max(0, Math.min(T.follow.length - 1, follow + d)); var id = T.follow[follow], e = cy.getElementById(id);
    cy.$(':selected').unselect(); e.select(); highlight(e); panel(byId[id]);
    setTimeout(function () { cy.resize(); cy.animate({ center: { eles: e }, zoom: 1.0 }, { duration: 450 }); }, 60);
    $('bFollow').textContent = 'Next ▶ (' + (follow + 1) + '/' + T.follow.length + ')';
  }
  function stopFollow() { follow = -1; $('bFollow').textContent = 'Follow the rain'; $('bFollow').classList.remove('on'); }

  function fitMain() { cy.fit(cy.nodes('.band').filter(function (b) { return !/band_(wi|cc)/.test(b.id()); }), 20); }

  function download(name, url) { var a = document.createElement('a'); a.href = url; a.download = name; document.body.appendChild(a); a.click(); a.remove(); }

  function init() {
    cy = cytoscape({ container: $('cy'), elements: elements(), style: style(), layout: { name: 'preset' }, wheelSensitivity: 0.25, minZoom: 0.12, maxZoom: 3,
                     boxSelectionEnabled: false, autoungrabify: true });
    cy.on('zoom', setLevel);
    cy.on('tap', 'node', function (ev) { if (ev.target.hasClass('band')) return; if (follow >= 0) stopFollow(); select(ev.target.id(), false); });
    cy.on('tap', function (ev) { if (ev.target === cy) { cy.$(':selected').unselect(); closePanel(); } });
    cy.on('mouseover', 'node', function (ev) { if (!ev.target.hasClass('band') && !cy.$(':selected').length) highlight(ev.target); });
    cy.on('mouseout', 'node', function () { if (!cy.$(':selected').length) highlight(null); });
    fitMain(); setLevel();
    var dl = $('qlist'); T.nodes.forEach(function (n) { var o = document.createElement('option'); o.value = n.title; dl.appendChild(o); });
    $('q').addEventListener('change', search); $('q').addEventListener('keydown', function (e) { if (e.key === 'Enter') search(); });
    $('bSimple').onclick = function () { simple = true; document.body.classList.add('simple'); $('bSimple').classList.add('on'); $('bSci').classList.remove('on'); relabel(); };
    $('bSci').onclick = function () { simple = false; document.body.classList.remove('simple'); $('bSci').classList.add('on'); $('bSimple').classList.remove('on'); relabel(); };
    document.body.classList.add('simple');
    $('bFit').onclick = function () { fitMain(); };
    $('bFollow').onclick = function () { if (follow < 0) { follow = -1; $('bFollow').classList.add('on'); } step(1); };
    $('bPng').onclick = function () { download('mass-flood-watch_model-tree.png', cy.png({ full: false, scale: 2, bg: dark() ? '#14171b' : '#ffffff' })); };
    $('bPdf').onclick = function () {
      var img = cy.png({ full: true, scale: 1.5, bg: '#ffffff' }), w = window.open('', '_blank');
      if (!w) return; w.document.write('<!doctype html><title>Model tree (PDF)</title><style>@page{size:landscape;margin:8mm}body{margin:0}img{width:100%}</style><img src="' + img + '" onload="setTimeout(function(){print()},300)">'); w.document.close();
    };
    var m = /node=([\w-]+)/.exec(location.hash); if (m && byId[m[1]]) select(m[1], true);
    window.addEventListener('hashchange', function () { var m2 = /node=([\w-]+)/.exec(location.hash); if (m2 && byId[m2[1]]) select(m2[1], true); });
    document.addEventListener('keydown', function (e) { if (follow >= 0 && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')) step(e.key === 'ArrowRight' ? 1 : -1); if (e.key === 'Escape') { stopFollow(); cy.$(':selected').unselect(); closePanel(); } });
  }

  function search() {
    var q = $('q').value.trim().toLowerCase(); if (!q) return;
    var best = null, score = 0;
    T.nodes.forEach(function (n) {
      var s = (n.title.toLowerCase() === q ? 100 : 0) + (n.title.toLowerCase().indexOf(q) >= 0 ? 20 : 0) + (n.id.indexOf(q) >= 0 ? 10 : 0) +
              ((n.what || '').toLowerCase().indexOf(q) >= 0 ? 5 : 0) + ((n.plain || '').toLowerCase().indexOf(q) >= 0 ? 3 : 0) +
              (JSON.stringify(n.parameters || []).toLowerCase().indexOf(q) >= 0 ? 2 : 0);
      if (s > score) { score = s; best = n; }
    });
    var h = $('hint'); h.hidden = false; h.textContent = best ? 'Found: ' + best.title : 'Nothing found for "' + q + '"'; setTimeout(function () { h.hidden = true; }, 2500);
    if (best) { stopFollow(); select(best.id, true); }
  }

  fetch('model-tree/tree.json?v=' + Date.now()).then(function (r) { return r.json(); }).then(function (j) { T = j; init(); })
    .catch(function (e) { $('cy').innerHTML = '<p style="padding:20px">Could not load the model tree data: ' + esc(e) + '</p>'; });
})();
