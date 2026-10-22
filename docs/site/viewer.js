/* Mass Flood Watch storm replay.
   Flood depth: all frames are decoded once into GPU textures (9 frames per texture, depth class packed base 5 in RGB)
   and drawn by one custom WebGL layer that interpolates between neighbouring 30-min frames on every animation frame.
   Roads: closure intervals are precomputed per segment; playback only flips feature-state on segments that change. */
(function () {
  'use strict';
  var RUNS = {
    leominster_sep2023: {
      title: 'Leominster and Fitchburg, Sept 11, 2023',
      kind: 'Tuned case. 20 × 20 km box at 20 m, the storm the model settings were checked against.'
    },
    worcester_aug2021: {
      title: 'Worcester, Aug 19, 2021',
      kind: 'Blind test. Same model settings as Leominster, run on a storm it was not tuned on.'
    },
    d3_sep2023: {
      title: 'All of MassDOT District 3, Sept 11, 2023',
      kind: 'One GPU run on WPI’s Turing cluster: 17.6 million cells at 20 m (shown here at 80 m).'
    }
  };
  var params = new URLSearchParams(location.search);
  var runKey = RUNS[params.get('run')] ? params.get('run') : 'leominster_sep2023';
  var base = 'site/data/' + runKey + '/';
  var $ = function (id) { return document.getElementById(id); };

  document.querySelectorAll('.runs a').forEach(function (a) {
    var on = a.dataset.run === runKey;
    a.setAttribute('aria-selected', on ? 'true' : 'false');
    var q = new URLSearchParams(location.search); q.set('run', a.dataset.run);
    a.href = '?' + q.toString();
  });
  $('runTitle').textContent = RUNS[runKey].title;
  $('runKind').textContent = RUNS[runKey].kind;

  // ---------- theme ----------
  function css(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
  function isDark() {
    var t = document.documentElement.dataset.theme;
    if (t) return t === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  function rgba(s) {
    var m = s.match(/[\d.]+/g).map(Number);
    return [m[0] / 255, m[1] / 255, m[2] / 255, m.length > 3 ? m[3] : 1];
  }

  // ---------- state ----------
  var meta, map, nf = 1, t = 0, playing = false, played = false, speed = 2, last = 0;
  var segs = [], ready = false, popup = null;
  var fmtClock = new Intl.DateTimeFormat('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York', timeZoneName: 'short' });
  var fmtShort = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York' });
  var t0;
  function timeAt(f) { return new Date(t0.getTime() + f * meta.frame_min * 60000); }
  function n(v) { return Math.round(v).toLocaleString('en-US'); }
  function usd(v) { return v >= 1e6 ? '$' + (v / 1e6).toFixed(1) + 'M' : '$' + Math.round(v / 1e3) + 'k'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  // ---------- depth layer (custom WebGL) ----------
  var depth = (function () {
    var gl, prog, buf, loc = {}, tex = [], queue = [], ramp = null;
    var VS = 'attribute vec2 aPos;attribute vec2 aUv;uniform mat4 uM;varying vec2 vUv;' +
      'void main(){vUv=aUv;gl_Position=uM*vec4(aPos,0.0,1.0);}';
    var FS = 'precision highp float;varying vec2 vUv;uniform sampler2D uA;uniform sampler2D uB;' +
      'uniform vec3 uMa;uniform vec3 uMb;uniform float uDa;uniform float uDb;uniform float uT;uniform vec4 uC[4];' +
      'float code(sampler2D s,vec3 m,float d){float x=floor(dot(texture2D(s,vUv).rgb,m)*255.0+0.5);return mod(floor(x/d+0.001),5.0);}' +
      'vec4 ramp(float L){if(L<=1.0)return vec4(uC[0].rgb,uC[0].a*L);if(L<=2.0)return mix(uC[0],uC[1],L-1.0);' +
      'if(L<=3.0)return mix(uC[1],uC[2],L-2.0);return mix(uC[2],uC[3],L-3.0);}' +
      'void main(){float L=mix(code(uA,uMa,uDa),code(uB,uMb,uDb),uT);if(L<0.02)discard;vec4 c=ramp(L);gl_FragColor=vec4(c.rgb*c.a,c.a);}';
    function sh(type, src) { var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); return s; }
    function slot(f) {
      var k = f % 9, m = [0, 0, 0]; m[Math.floor(k / 3)] = 1 / 1; // channel mask
      return { tex: tex[Math.floor(f / 9)], m: m, d: [1, 5, 25][k % 3] };
    }
    return {
      layer: {
        id: 'depth', type: 'custom', renderingMode: '2d',
        onAdd: function (m, g) {
          gl = g;
          prog = gl.createProgram();
          gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS));
          gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS));
          gl.linkProgram(prog);
          ['aPos', 'aUv'].forEach(function (k) { loc[k] = gl.getAttribLocation(prog, k); });
          ['uM', 'uA', 'uB', 'uMa', 'uMb', 'uDa', 'uDb', 'uT', 'uC'].forEach(function (k) { loc[k] = gl.getUniformLocation(prog, k); });
          var c = meta.corners.map(function (p) { return maplibregl.MercatorCoordinate.fromLngLat(p); });
          // TL, TR, BL, BR as a triangle strip: x, y, u, v
          var v = new Float32Array([c[0].x, c[0].y, 0, 0, c[1].x, c[1].y, 1, 0, c[3].x, c[3].y, 0, 1, c[2].x, c[2].y, 1, 1]);
          buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, v, gl.STATIC_DRAW);
        },
        render: function (g, matrix) {
          while (queue.length) {
            var q = queue.shift(), tx = gl.createTexture();
            gl.bindTexture(gl.TEXTURE_2D, tx);
            gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
            gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
            gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, gl.NONE);
            gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, q.img);
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
            gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
            tex[q.i] = tx;
            if (q.img.close) q.img.close();
          }
          var fa = Math.min(Math.floor(t), nf - 1), fb = Math.min(fa + 1, nf - 1);
          var A = slot(fa), B = slot(fb);
          if (!A.tex || !B.tex || !ramp) return;
          gl.useProgram(prog);
          gl.uniformMatrix4fv(loc.uM, false, matrix);
          gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, A.tex); gl.uniform1i(loc.uA, 0);
          gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, B.tex); gl.uniform1i(loc.uB, 1);
          gl.uniform3fv(loc.uMa, A.m); gl.uniform3fv(loc.uMb, B.m);
          gl.uniform1f(loc.uDa, A.d); gl.uniform1f(loc.uDb, B.d);
          gl.uniform1f(loc.uT, fb === fa ? 0 : t - fa);
          gl.uniform4fv(loc.uC, ramp);
          gl.bindBuffer(gl.ARRAY_BUFFER, buf);
          gl.enableVertexAttribArray(loc.aPos); gl.vertexAttribPointer(loc.aPos, 2, gl.FLOAT, false, 16, 0);
          gl.enableVertexAttribArray(loc.aUv); gl.vertexAttribPointer(loc.aUv, 2, gl.FLOAT, false, 16, 8);
          gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
          gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
          gl.activeTexture(gl.TEXTURE0);
        }
      },
      add: function (i, img) { queue.push({ i: i, img: img }); },
      setRamp: function (cols) { ramp = new Float32Array([].concat.apply([], cols)); }
    };
  })();

  // ---------- loading ----------
  function getBitmap(url) {
    return fetch(url).then(function (r) { if (!r.ok) throw new Error(url + ' ' + r.status); return r.blob(); })
      .then(function (b) {
        if (window.createImageBitmap) {
          return createImageBitmap(b, { colorSpaceConversion: 'none', premultiplyAlpha: 'none' })
            .catch(function () { return imgFromBlob(b); });
        }
        return imgFromBlob(b);
      });
  }
  function imgFromBlob(b) {
    return new Promise(function (res, rej) { var im = new Image(); im.onload = function () { res(im); }; im.onerror = rej; im.src = URL.createObjectURL(b); });
  }
  var done = 0, total = 1;
  function progress(label) {
    done++;
    var p = Math.min(1, done / total);
    $('loadBar').style.width = (p * 100).toFixed(0) + '%';
    $('loadText').textContent = label || ('Loading storm frames… ' + Math.round(p * 100) + '%');
  }

  fetch(base + 'meta.json').then(function (r) { return r.json(); }).then(function (m) {
    meta = m; nf = m.nf;
    t0 = new Date(m.storm_start.replace(/Z$/, ':00Z'));
    $('scrub').max = nf - 1;
    $('runStats').innerHTML = '<b>' + n(m.segments_p_ge_50) + '</b> road segments likely closed (' + m.km_p_ge_50 + ' km), <b>' +
      n(m.segments_may_close) + '</b> more may close, <b>' + n(m.culverts_overtopped) + '</b> culverts overtopped, out of ' +
      n(m.segments_in_box) + ' segments in the area.';
    var peak = 0, cp = m.closed_per_frame || [];
    cp.forEach(function (v, i) { if (v > cp[peak]) peak = i; });
    t = peak;
    drawChart();
    initMap();
  }).catch(function (e) { $('loadText').textContent = 'The storm data did not load. Reload the page to try again.'; console.error(e); });

  // ---------- map ----------
  var ESRI = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/';
  function esri(name) { return { type: 'raster', tileSize: 256, maxzoom: 16, tiles: [ESRI + name + '/MapServer/tile/{z}/{y}/{x}'] }; }
  function initMap() {
    var lons = meta.corners.map(function (c) { return c[0]; }), lats = meta.corners.map(function (c) { return c[1]; });
    var bounds = [[Math.min.apply(0, lons), Math.min.apply(0, lats)], [Math.max.apply(0, lons), Math.max.apply(0, lats)]];
    var small = window.innerWidth < 720;
    map = new maplibregl.Map({
      container: 'map', bounds: bounds, maxZoom: 16, minZoom: 6, dragRotate: false, pitchWithRotate: false,
      fitBoundsOptions: { padding: small ? { top: 160, bottom: 190, left: 10, right: 10 } : { top: 30, bottom: 150, left: 370, right: 280 } },
      attributionControl: false,
      style: {
        version: 8,
        sources: {
          lb: esri('World_Light_Gray_Base'), lr: esri('World_Light_Gray_Reference'),
          db: esri('World_Dark_Gray_Base'), dr: esri('World_Dark_Gray_Reference')
        },
        layers: [
          { id: 'lb', type: 'raster', source: 'lb' }, { id: 'db', type: 'raster', source: 'db' },
          { id: 'lr', type: 'raster', source: 'lr' }, { id: 'dr', type: 'raster', source: 'dr' }
        ]
      }
    });
    map.addControl(new maplibregl.AttributionControl({ compact: true, customAttribution: 'Basemap: Esri, HERE, Garmin, © OpenStreetMap contributors, and the GIS User Community | Flood model: LISFLOOD-FP 8.2 with NOAA MRMS rain | Roads: MassDOT' }));
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    map.touchZoomRotate.disableRotation();
    map.once('style.load', function () {
      map.addLayer(depth.layer, 'lr');
      applyTheme();
      styleReady();
    });
    var at = document.querySelector('.maplibregl-ctrl-attrib');
    if (at && small) at.classList.remove('maplibregl-compact-show');
    loadData();
  }
  var styleWaiters = [], styleOk = false;
  function styleReady() { styleOk = true; styleWaiters.splice(0).forEach(function (f) { f(); }); }
  function whenStyle(f) { if (styleOk) f(); else styleWaiters.push(f); }

  function loadData() {
    total = meta.sheets.length + 1;
    var jobs = meta.sheets.map(function (s, i) {
      return getBitmap(base + s).then(function (img) { depth.add(i, img); progress(); if (styleOk) map.triggerRepaint(); });
    });
    jobs.push(fetch(base + 'roads.json').then(function (r) { return r.json(); }).then(function (g) {
      return new Promise(function (res) { whenStyle(function () { addRoads(g); progress(); res(); }); });
    }));
    Promise.all(jobs).then(function () {
      ready = true;
      $('loading').classList.add('done');
      $('play').disabled = false;
      setTime(t);
    }).catch(function (e) { $('loadText').textContent = 'Some storm data did not load. Reload the page to try again.'; console.error(e); });
  }

  function addRoads(g) {
    g.features.forEach(function (f) { if (f.properties.iv) segs.push({ id: f.id, iv: f.properties.iv, c: false }); });
    map.addSource('roads', { type: 'geojson', data: g, tolerance: 0.2 });
    var w = function (a, b) { return ['interpolate', ['linear'], ['zoom'], 9, a, 15, b]; };
    map.addLayer({ id: 'peak', type: 'line', source: 'roads', filter: ['>=', ['get', 'p'], 0.5], layout: { 'line-cap': 'round' }, paint: { 'line-width': w(1, 2.5), 'line-opacity': 0.45 } });
    map.addLayer({ id: 'may', type: 'line', source: 'roads', filter: ['==', ['get', 'm'], 1], paint: { 'line-width': w(1.5, 3.5), 'line-dasharray': [2, 1.2] } });
    map.addLayer({ id: 'risk', type: 'line', source: 'roads', filter: ['has', 'rk'], layout: { visibility: 'none', 'line-cap': 'round' }, paint: { 'line-width': w(2.5, 6) } });
    map.addLayer({ id: 'closed', type: 'line', source: 'roads', filter: ['has', 'iv'], layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: { 'line-width': w(2.5, 6.5), 'line-opacity': ['case', ['boolean', ['feature-state', 'c'], false], 1, 0] } });
    map.addLayer({ id: 'hit', type: 'line', source: 'roads', paint: { 'line-width': 16, 'line-opacity': 0 } });
    applyTheme();
    if (g.features.some(function (f) { return f.properties.rk; })) { $('riskRow').hidden = false; }
    map.on('mouseenter', 'hit', function () { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', 'hit', function () { map.getCanvas().style.cursor = ''; });
    map.on('click', 'hit', function (e) {
      var vis = e.features.filter(function (f) {
        var p = f.properties; return p.p >= 0.5 || p.m === 1 || (p.rk && $('lyRisk').checked) || p.iv;
      });
      var f = (vis.length ? vis : e.features).sort(function (a, b) { return b.properties.p - a.properties.p; })[0];
      if (popup) popup.remove();
      popup = new maplibregl.Popup({ maxWidth: '300px' }).setLngLat(e.lngLat).setHTML(popupHtml(f)).addTo(map);
    });
  }

  var CLS = ['Local or collector road', 'Arterial', 'Highway'];
  function popupHtml(f) {
    var p = f.properties, iv = p.iv ? (typeof p.iv === 'string' ? JSON.parse(p.iv) : p.iv) : null;
    var a = p.a ? (typeof p.a === 'string' ? JSON.parse(p.a) : p.a) : null;
    var rc = p.rc ? (typeof p.rc === 'string' ? JSON.parse(p.rc) : p.rc) : null;
    var h = '<div class="pp"><h3>' + esc(p.n || 'Unnamed road') + '</h3><p class="sub">' + esc(p.t ? p.t + ', ' : '') + CLS[p.c || 0] + '</p><dl>';
    h += '<dt>Chance of closing</dt><dd><b>' + Math.round(p.p * 100) + '%</b></dd>';
    if (iv && iv.length) {
      var s = iv[0][0], e = iv[iv.length - 1][1];
      h += '<dt>Closes</dt><dd>' + fmtShort.format(timeAt(s)) + '</dd>';
      h += '<dt>Reopens</dt><dd>' + (e >= nf - 1 ? 'still closed when the modelled ' + Math.round((nf - 1) * meta.frame_min / 60) + ' h end' : fmtShort.format(timeAt(e))) + '</dd>';
    }
    if (p.m === 1) h += '<dt>May close</dt><dd>stream beside the road reaches road level (not counted in the chance of closing)</dd>';
    if (a) h += '<dt>If it closes</dt><dd>residents losing access within the response standard: hospital ' + n(a[0]) + ', fire ' + n(a[1]) + ', police ' + n(a[2]) + (a[3] ? '; ' + n(a[3]) + ' with no route to any of them' : '') + '</dd>';
    if (p.rk) {
      var col = { Extreme: css('--rx'), High: css('--rh'), Medium: css('--rm'), Low: css('--rl') }[p.rk];
      h += '<dt>Risk class</dt><dd><span class="tag" style="background:' + col + ';color:' + (p.rk === 'Medium' || p.rk === 'Low' ? '#15212b' : '#fff') + '">' + p.rk + '</span></dd>';
      if (rc) h += '<dt>Cost if damaged</dt><dd>repair ' + usd(rc[0]) + '–' + usd(rc[1]) + ' plus ' + usd(rc[2]) + ' traffic delay (2023 $)</dd>';
    }
    h += '</dl>';
    if (p.w) h += '<p class="why">Why: ' + esc(p.w) + '</p>';
    return h + '</div>';
  }

  function applyTheme() {
    if (!map || !map.getLayer('lb')) return;
    var dark = isDark();
    ['lb', 'lr'].forEach(function (id) { map.setLayoutProperty(id, 'visibility', dark ? 'none' : 'visible'); });
    ['db', 'dr'].forEach(function (id) { map.setLayoutProperty(id, 'visibility', dark ? 'visible' : 'none'); });
    depth.setRamp(['--d1', '--d2', '--d3', '--d4'].map(function (k) { return rgba(css(k)); }));
    if (map.getLayer('closed')) {
      map.setPaintProperty('closed', 'line-color', css('--closed'));
      map.setPaintProperty('peak', 'line-color', css('--peak'));
      map.setPaintProperty('may', 'line-color', css('--may'));
      map.setPaintProperty('risk', 'line-color', ['match', ['get', 'rk'], 'Extreme', css('--rx'), 'High', css('--rh'), 'Medium', css('--rm'), css('--rl')]);
    }
    map.triggerRepaint();
    drawChart();
  }
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
  window.addEventListener('storage', function (e) {
    if (e.key === 'mfw-theme') { if (e.newValue) document.documentElement.dataset.theme = e.newValue; else delete document.documentElement.dataset.theme; applyTheme(); }
  });
  window.addEventListener('message', function (e) {
    if (e.origin === location.origin && e.data && e.data.mfwTheme !== undefined) {
      if (e.data.mfwTheme) document.documentElement.dataset.theme = e.data.mfwTheme; else delete document.documentElement.dataset.theme;
      applyTheme();
    }
  });

  // ---------- timeline ----------
  var cursor;
  function drawChart() {
    if (!meta) return;
    var svg = $('chart'), H = 46, W = nf - 1, r = meta.rain_hourly_mean_mm || [], cp = meta.closed_per_frame || [];
    var rmax = Math.max.apply(0, r.concat([1])), cmax = Math.max.apply(0, cp.concat([1]));
    var hours = Math.floor(W * meta.frame_min / 60), per = 60 / meta.frame_min;
    var s = '';
    for (var i = 0; i < Math.min(r.length, hours); i++) {
      var bh = (H - 4) * r[i] / rmax;
      s += '<rect x="' + (i * per + 0.1) + '" y="' + (H - bh) + '" width="' + (per - 0.2) + '" height="' + bh + '" fill="' + css('--rain') + '"/>';
    }
    var pts = cp.map(function (v, i) { return i + ',' + (H - 2 - (H - 6) * v / cmax).toFixed(1); }).join(' ');
    s += '<polyline points="' + pts + '" fill="none" stroke="' + css('--line') + '" stroke-width="1.5" vector-effect="non-scaling-stroke" stroke-linejoin="round"/>';
    s += '<line id="cur" x1="0" x2="0" y1="0" y2="' + H + '" stroke="' + css('--accent') + '" stroke-width="2" vector-effect="non-scaling-stroke"/>';
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.innerHTML = s;
    cursor = $('cur');
    setCursor();
  }
  function setCursor() { if (cursor) { cursor.setAttribute('x1', t); cursor.setAttribute('x2', t); } }

  var lastClock = '';
  function setTime(v) {
    t = Math.max(0, Math.min(nf - 1, v));
    var closed = 0;
    for (var i = 0; i < segs.length; i++) {
      var s = segs[i], c = false, iv = s.iv;
      for (var j = 0; j < iv.length; j++) { if (t >= iv[j][0] && t < iv[j][1]) { c = true; break; } }
      if (c) closed++;
      if (c !== s.c) { s.c = c; map.setFeatureState({ source: 'roads', id: s.id }, { c: c }); }
    }
    var mins = Math.round(t * meta.frame_min / 5) * 5, label = fmtClock.format(new Date(t0.getTime() + mins * 60000));
    if (label !== lastClock) {
      lastClock = label;
      $('clock').textContent = label;
      var hh = mins / 60;
      $('since').textContent = hh.toFixed(1) + ' h after the replay starts';
    }
    $('nClosed').textContent = closed;
    $('scrub').value = t;
    setCursor();
    if (map) map.triggerRepaint();
  }

  function tick(now) {
    if (!playing) return;
    var dt = Math.min(0.1, (now - last) / 1000); last = now;
    var v = t + dt * speed * (60 / meta.frame_min);
    if (v >= nf - 1) { setTime(nf - 1); setPlaying(false); return; }
    setTime(v);
    requestAnimationFrame(tick);
  }
  function setPlaying(on) {
    playing = on;
    $('playIcon').setAttribute('d', on ? 'M5 3h3.5v14H5zM11.5 3H15v14h-3.5z' : 'M5 3l12 7-12 7z');
    $('play').setAttribute('aria-label', on ? 'Pause' : 'Play storm');
    if (on) {
      if (!played || t >= nf - 1.01) t = 0;
      played = true;
      last = performance.now();
      requestAnimationFrame(tick);
    }
  }
  $('play').addEventListener('click', function () { if (ready) setPlaying(!playing); });
  document.querySelectorAll('.speeds button').forEach(function (b) {
    b.addEventListener('click', function () {
      speed = +b.dataset.speed;
      document.querySelectorAll('.speeds button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    });
  });
  $('scrub').addEventListener('input', function (e) { if (!ready) return; if (playing) setPlaying(false); played = true; setTime(+e.target.value); });
  document.addEventListener('keydown', function (e) {
    if (e.key === ' ' && e.target === document.body && ready) { e.preventDefault(); setPlaying(!playing); }
  });

  // ---------- layers ----------
  function vis(id, on) { if (map && map.getLayer(id)) map.setLayoutProperty(id, 'visibility', on ? 'visible' : 'none'); }
  $('lyDepth').addEventListener('change', function (e) { vis('depth', e.target.checked); });
  $('lyClosed').addEventListener('change', function (e) { vis('closed', e.target.checked); });
  $('lyPeak').addEventListener('change', function (e) { vis('peak', e.target.checked); });
  $('lyMay').addEventListener('change', function (e) { vis('may', e.target.checked); });
  $('lyRisk').addEventListener('change', function (e) {
    var on = e.target.checked;
    vis('risk', on); $('riskKey').hidden = !on;
    $('lyPeak').checked = !on; vis('peak', !on);
    $('lyMay').checked = !on; vis('may', !on);
  });
  var pl = document.querySelector('.player');
  function ph() { document.documentElement.style.setProperty('--player-h', pl.offsetHeight + 'px'); }
  if (window.ResizeObserver) new ResizeObserver(ph).observe(pl); ph();
  var lg = $('legend');
  if (window.innerWidth < 720) { lg.dataset.collapsed = 'true'; $('legendToggle').setAttribute('aria-expanded', 'false'); }
  $('legendToggle').addEventListener('click', function () {
    var c = lg.dataset.collapsed === 'true';
    lg.dataset.collapsed = c ? 'false' : 'true';
    this.setAttribute('aria-expanded', c ? 'true' : 'false');
  });
})();
