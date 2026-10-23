/* Mass Flood Watch storm replay.
   GPU layers (custom WebGL, one draw each per animation frame):
     depth  all frames decoded once into textures (9 frames per texture, depth class packed base 5 in RGB), interpolated in time
            and, after decoding, bilinearly in space with a soft edge at the wet/dry cell boundary
     rain   MRMS radar rain, every frame in one atlas texture (3 frames per cell, log-scaled mm/h), filtered in space and time
     flow   (5-min runs only) moving water surface: a ripple texture advected along the modelled velocity field (flow-map),
            masked to wet cells and faded by depth and speed; frozen still when the replay is paused
   Roads: depth on each segment per frame (cm) is interpolated in time and written to feature-state only when it changes,
   so a road turns grey -> amber -> red as the water rises and fades back as it drains.
   Framing: the camera opens on where roads close, with one-click hotspot views and an optional 'follow the storm'. */
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
    },
    forecast: { title: 'Live forecast, MassDOT District 3', kind: '' }
  };
  var D3_BOUNDS = [[-72.38, 41.95], [-71.43, 42.765]];
  var params = new URLSearchParams(location.search);
  var runKey = RUNS[params.get('run')] ? params.get('run') : /^[a-z0-9_]{3,60}$/.test(params.get('run') || '') ? params.get('run') : 'leominster_sep2023';
  if (!RUNS[runKey]) RUNS[runKey] = { title: runKey.replace(/_/g, ' '), kind: '' }; // any other published run folder, e.g. a 5-minute rerun
  var base = 'site/data/' + runKey + '/';
  var $ = function (id) { return document.getElementById(id); };
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var small = function () { return window.innerWidth < 720; };

  document.querySelectorAll('.runs a').forEach(function (a) {
    var on = a.dataset.run === runKey;
    a.setAttribute('aria-selected', on ? 'true' : 'false');
    var q = new URLSearchParams(location.search); q.set('run', a.dataset.run);
    a.href = '?' + q.toString();
  });
  $('runTitle').textContent = RUNS[runKey].title;
  $('runKind').textContent = RUNS[runKey].kind;

  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; } }

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

  // ---------- basemaps and the palette that reads on each ----------
  var CARTO = function (style) {
    return { type: 'raster', tileSize: 256, maxzoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/attributions">CARTO</a>',
      tiles: ['a', 'b', 'c', 'd'].map(function (s) { return 'https://' + s + '.basemaps.cartocdn.com/rastertiles/' + style + '/{z}/{x}/{y}@2x.png'; }) };
  };
  var ESRI = function (path, mz, attr) {
    return { type: 'raster', tileSize: 256, maxzoom: mz, attribution: attr, tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/' + path + '/MapServer/tile/{z}/{y}/{x}'] };
  };
  var BASEMAPS = {
    streets: { layers: { 'b-voy': 1 } },
    terrain: { layers: { 'b-hill': 1, 'b-voy': 0.62 } },
    satellite: { layers: { 'b-sat': 1, 'l-dark': 1 } },
    dark: { layers: { 'b-dark': 1, 'l-dark': 1 } }
  };
  // depth ramp (5, 15, 30, 100 cm), roads: wet (amber) -> closed (red), casing under them, footprint of closures, may close
  var PAL = {
    light: { d: ['rgba(120,196,240,.55)', 'rgba(52,148,226,.72)', 'rgba(18,96,196,.85)', 'rgba(8,46,138,.93)'],
      grey: '#7f8b95', amber: '#f0a020', orange: '#ec6a12', closed: '#d4142a', cas: 'rgba(255,255,255,.95)', peak: '#b4182c', peakOp: 0.5, may: '#e06a00', halo: '#ff3048' },
    satellite: { d: ['rgba(110,226,255,.5)', 'rgba(44,186,255,.7)', 'rgba(24,136,255,.82)', 'rgba(40,84,240,.92)'],
      grey: '#c9d1d6', amber: '#ffc21a', orange: '#ff7a1a', closed: '#ff2448', cas: 'rgba(20,20,20,.85)', peak: '#ff8fa0', peakOp: 0.8, may: '#ffb020', halo: '#ff4060' },
    dark: { d: ['rgba(40,104,176,.6)', 'rgba(52,142,222,.76)', 'rgba(96,184,246,.86)', 'rgba(186,228,255,.95)'],
      grey: '#8796a3', amber: '#ffb52e', orange: '#ff7d2e', closed: '#ff4058', cas: 'rgba(8,14,20,.9)', peak: '#ff7d8c', peakOp: 0.55, may: '#ffa24a', halo: '#ff4a5e' }
  };
  var bm = store('mfw-basemap');
  function basemap() { return BASEMAPS[bm] ? bm : (isDark() ? 'dark' : 'streets'); }
  function pal() { var b = basemap(); return b === 'satellite' ? PAL.satellite : b === 'dark' ? PAL.dark : PAL.light; }

  // ---------- state ----------
  var meta, map, nf = 1, t = 0, playing = false, played = false, speed = 2, last = 0;
  var flowRGB = { hi: [1, 1, 1], dk: 0.2 }; // flow layer: glint colour and trough shading, per basemap
  var segs = [], ready = false, popup = null, hover = null, refs = null, rain = null, flowInfo = null;
  var fmtClock = new Intl.DateTimeFormat('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York', timeZoneName: 'short' });
  var fmtShort = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York' });
  var t0;
  function timeAt(f) { return new Date(t0.getTime() + f * meta.frame_min * 60000); }
  function n(v) { return Math.round(v).toLocaleString('en-US'); }
  function usd(v) { return v >= 1e6 ? '$' + (v / 1e6).toFixed(1) + 'M' : '$' + Math.round(v / 1e3) + 'k'; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function title(s) { return String(s || '').toLowerCase().replace(/\b[a-z]/g, function (c) { return c.toUpperCase(); }); }

  // ---------- WebGL helpers ----------
  function program(gl, vs, fs) {
    var p = gl.createProgram();
    [[gl.VERTEX_SHADER, vs], [gl.FRAGMENT_SHADER, fs]].forEach(function (s) {
      var sh = gl.createShader(s[0]); gl.shaderSource(sh, s[1]); gl.compileShader(sh);
      if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) console.error(gl.getShaderInfoLog(sh));
      gl.attachShader(p, sh);
    });
    gl.linkProgram(p);
    return p;
  }
  function texture(gl, img, filter, fmt) {
    var tx = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tx);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
    gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, gl.NONE);
    if (img instanceof Uint8Array) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, img.length / 4, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, img);
    else gl.texImage2D(gl.TEXTURE_2D, 0, fmt || gl.RGB, fmt || gl.RGB, gl.UNSIGNED_BYTE, img);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, filter);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, filter);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    return tx;
  }
  function quad(corners) { // [TL, TR, BR, BL] lon/lat -> triangle strip x, y, u, v
    var c = corners.map(function (p) { return maplibregl.MercatorCoordinate.fromLngLat(p); });
    return new Float32Array([c[0].x, c[0].y, 0, 0, c[1].x, c[1].y, 1, 0, c[3].x, c[3].y, 0, 1, c[2].x, c[2].y, 1, 1]);
  }

  // ---------- depth layer ----------
  var depth = (function () {
    var gl, prog, buf, loc = {}, tex = [], queue = [], ramp = null;
    var VS = 'attribute vec2 aPos;attribute vec2 aUv;uniform mat4 uM;varying vec2 vUv;' +
      'void main(){vUv=aUv;gl_Position=uM*vec4(aPos,0.0,1.0);}';
    var FS = 'precision highp float;varying vec2 vUv;uniform sampler2D uA;uniform sampler2D uB;' +
      'uniform vec3 uMa;uniform vec3 uMb;uniform float uDa;uniform float uDb;uniform float uT;uniform vec4 uC[4];' +
      'uniform vec2 uS;' +
      // classes are decoded per cell first (base-5 digits cannot be filtered), then interpolated: bilinear between the
      // four nearest cell centres. A wet cell next to a dry one reads 0.5 exactly on their shared edge, so the soft
      // threshold at 0.5 keeps the water edge on the cell boundary (never more than half a cell onto dry ground)
      'float code(sampler2D s,vec3 m,float d,vec2 uv){float x=floor(dot(texture2D(s,uv).rgb,m)*255.0+0.5);return mod(floor(x/d+0.001),5.0);}' +
      'float cls(sampler2D s,vec3 m,float d){vec2 p=vUv*uS-0.5;vec2 i=floor(p);vec2 f=p-i;vec2 c=(i+0.5)/uS;vec2 dx=vec2(1.0/uS.x,0.0);vec2 dy=vec2(0.0,1.0/uS.y);' +
      'return mix(mix(code(s,m,d,c),code(s,m,d,c+dx),f.x),mix(code(s,m,d,c+dy),code(s,m,d,c+dx+dy),f.x),f.y);}' +
      'vec4 ramp(float L){if(L<=2.0)return mix(uC[0],uC[1],L-1.0);' +
      'if(L<=3.0)return mix(uC[1],uC[2],L-2.0);return mix(uC[2],uC[3],L-3.0);}' +
      'void main(){float L=mix(cls(uA,uMa,uDa),cls(uB,uMb,uDb),uT);float e=smoothstep(0.38,0.62,L);if(e<0.004)discard;' +
      'vec4 c=ramp(max(L,1.0));c.a*=e;gl_FragColor=vec4(c.rgb*c.a,c.a);}';
    function slot(f) {
      var k = f % 9, m = [0, 0, 0]; m[Math.floor(k / 3)] = 1;
      return { tex: tex[Math.floor(f / 9)], m: m, d: [1, 5, 25][k % 3] };
    }
    return {
      layer: {
        id: 'depth', type: 'custom', renderingMode: '2d',
        onAdd: function (m, g) {
          gl = g; prog = program(gl, VS, FS);
          ['aPos', 'aUv'].forEach(function (k) { loc[k] = gl.getAttribLocation(prog, k); });
          ['uM', 'uA', 'uB', 'uMa', 'uMb', 'uDa', 'uDb', 'uT', 'uC', 'uS'].forEach(function (k) { loc[k] = gl.getUniformLocation(prog, k); });
          buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, quad(meta.corners), gl.STATIC_DRAW);
        },
        render: function (g, matrix) {
          while (queue.length) { var q = queue.shift(); tex[q.i] = texture(gl, q.img, gl.NEAREST); if (q.img.close) q.img.close(); }
          var fa = Math.min(Math.floor(t), nf - 1), fb = Math.min(fa + 1, nf - 1);
          var A = slot(fa), B = slot(fb);
          if (!A.tex || !B.tex || !ramp) return;
          gl.useProgram(prog);
          gl.uniformMatrix4fv(loc.uM, false, matrix);
          gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, A.tex); gl.uniform1i(loc.uA, 0);
          gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, B.tex); gl.uniform1i(loc.uB, 1);
          gl.uniform3fv(loc.uMa, A.m); gl.uniform3fv(loc.uMb, B.m); gl.uniform2f(loc.uS, meta.w, meta.h);
          gl.uniform1f(loc.uDa, A.d); gl.uniform1f(loc.uDb, B.d);
          gl.uniform1f(loc.uT, fb === fa ? 0 : t - fa);
          gl.uniform4fv(loc.uC, ramp);
          gl.bindBuffer(gl.ARRAY_BUFFER, buf);
          gl.enableVertexAttribArray(loc.aPos); gl.vertexAttribPointer(loc.aPos, 2, gl.FLOAT, false, 16, 0);
          gl.enableVertexAttribArray(loc.aUv); gl.vertexAttribPointer(loc.aUv, 2, gl.FLOAT, false, 16, 8);
          gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
          gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
          gl.disableVertexAttribArray(loc.aPos); gl.disableVertexAttribArray(loc.aUv);
          gl.activeTexture(gl.TEXTURE0);
        }
      },
      add: function (i, img) { queue.push({ i: i, img: img }); },
      setRamp: function (cols) { ramp = new Float32Array([].concat.apply([], cols)); },
      // the two depth frames around t, for the flow layer's wet mask (null until both are on the GPU)
      frames: function () {
        var fa = Math.min(Math.floor(t), nf - 1), fb = Math.min(fa + 1, nf - 1), A = slot(fa), B = slot(fb);
        return A.tex && B.tex ? { A: A, B: B, ft: fb === fa ? 0 : t - fa } : null;
      }
    };
  })();

  // ---------- rain layer (radar loop) ----------
  // mm/h stops: colour and opacity, classic radar greens -> yellow -> red -> magenta, kept clear of the blue depth ramp
  var RAIN_STOPS = [[0.4, [120, 210, 110, 0]], [1, [96, 196, 92, 0.1]], [3, [46, 168, 66, 0.17]], [8, [22, 128, 46, 0.24]], [15, [238, 222, 40, 0.3]],
    [30, [248, 150, 24, 0.36]], [50, [226, 36, 36, 0.41]], [80, [204, 34, 168, 0.45]], [150, [150, 70, 236, 0.5]]];
  function rainColor(mm) {
    if (mm <= RAIN_STOPS[0][0]) return [0, 0, 0, 0];
    for (var i = 1; i < RAIN_STOPS.length; i++) {
      if (mm <= RAIN_STOPS[i][0]) {
        var a = RAIN_STOPS[i - 1], b = RAIN_STOPS[i], k = (Math.log(mm) - Math.log(a[0])) / (Math.log(b[0]) - Math.log(a[0]));
        return a[1].map(function (v, j) { return v + (b[1][j] - v) * k; });
      }
    }
    return RAIN_STOPS[RAIN_STOPS.length - 1][1];
  }
  var rainLayer = (function () {
    var gl, prog, buf, loc = {}, tex = null, lut = null, pending = null;
    var VS = 'attribute vec2 aPos;uniform mat4 uM;varying vec2 vM;void main(){vM=aPos;gl_Position=uM*vec4(aPos,0.0,1.0);}';
    // vM is Web Mercator (0..1); the radar grid is regular in lat/lon, so the row is found from latitude, not mercator y
    var FS = 'precision highp float;varying vec2 vM;uniform sampler2D uS;uniform sampler2D uL;uniform vec4 uB;' +
      'uniform vec2 uCa;uniform vec2 uCb;uniform vec3 uMa;uniform vec3 uMb;uniform vec2 uCell;uniform vec2 uHalf;uniform float uT;uniform float uOp;' +
      'void main(){float lon=vM.x*360.0-180.0;float yy=3.14159265*(1.0-2.0*vM.y);float lat=degrees(atan((exp(yy)-exp(-yy))*0.5));' +
      'vec2 uv=vec2((lon-uB.x)/(uB.z-uB.x),(uB.w-lat)/(uB.w-uB.y));if(uv.x<0.0||uv.x>1.0||uv.y<0.0||uv.y>1.0)discard;' +
      'vec2 c=clamp(uv*uCell,uHalf,uCell-uHalf);float a=dot(texture2D(uS,uCa+c).rgb,uMa);float b=dot(texture2D(uS,uCb+c).rgb,uMb);' +
      'float v=mix(a,b,uT);if(v<0.03)discard;vec4 k=texture2D(uL,vec2(v,0.5));float al=k.a*uOp;' +
      'float e=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));al*=smoothstep(0.0,0.06,e);gl_FragColor=vec4(k.rgb*al,al);}';
    return {
      layer: {
        id: 'rain', type: 'custom', renderingMode: '2d',
        onAdd: function (m, g) {
          gl = g; prog = program(gl, VS, FS);
          loc.aPos = gl.getAttribLocation(prog, 'aPos');
          ['uM', 'uS', 'uL', 'uB', 'uCa', 'uCb', 'uMa', 'uMb', 'uCell', 'uHalf', 'uT', 'uOp'].forEach(function (k) { loc[k] = gl.getUniformLocation(prog, k); });
          var b = rain.bounds, p = [[b[0][0], b[1][1]], [b[1][0], b[1][1]], [b[1][0], b[0][1]], [b[0][0], b[0][1]]].map(function (q) { return maplibregl.MercatorCoordinate.fromLngLat(q); });
          buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
          gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([p[0].x, p[0].y, p[1].x, p[1].y, p[3].x, p[3].y, p[2].x, p[2].y]), gl.STATIC_DRAW);
          var L = new Uint8Array(256 * 4);
          for (var i = 0; i < 256; i++) {
            var mm = Math.expm1(i / 255 * Math.log1p(rain.max_mmh)), c = rainColor(mm);
            L[i * 4] = c[0]; L[i * 4 + 1] = c[1]; L[i * 4 + 2] = c[2]; L[i * 4 + 3] = Math.round(c[3] * 255);
          }
          lut = texture(gl, L, gl.LINEAR);
        },
        render: function (g, matrix) {
          if (pending) { tex = texture(gl, pending, gl.LINEAR); if (pending.close) pending.close(); pending = null; }
          if (!tex) return;
          var R = rain, pos = Math.max(0, Math.min(R.n - 1, (t * meta.frame_min - R.off) / R.step_min));
          var fa = Math.floor(pos), fb = Math.min(fa + 1, R.n - 1);
          function cell(f) { var c = Math.floor(f / 3), cy = Math.floor(c / R.cols), cx = c % R.cols, m = [0, 0, 0]; m[f % 3] = 1; return { o: [cx / R.cols, cy / R.rows], m: m }; }
          var A = cell(fa), B = cell(fb);
          gl.useProgram(prog);
          gl.uniformMatrix4fv(loc.uM, false, matrix);
          gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tex); gl.uniform1i(loc.uS, 0);
          gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, lut); gl.uniform1i(loc.uL, 1);
          gl.uniform4f(loc.uB, R.bounds[0][0], R.bounds[0][1], R.bounds[1][0], R.bounds[1][1]);
          gl.uniform2fv(loc.uCa, A.o); gl.uniform2fv(loc.uCb, B.o); gl.uniform3fv(loc.uMa, A.m); gl.uniform3fv(loc.uMb, B.m);
          gl.uniform2f(loc.uCell, 1 / R.cols, 1 / R.rows); gl.uniform2f(loc.uHalf, 0.5 / (R.cols * R.w), 0.5 / (R.rows * R.h));
          gl.uniform1f(loc.uT, pos - fa); gl.uniform1f(loc.uOp, 1);
          gl.bindBuffer(gl.ARRAY_BUFFER, buf);
          gl.enableVertexAttribArray(loc.aPos); gl.vertexAttribPointer(loc.aPos, 2, gl.FLOAT, false, 8, 0);
          gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
          gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
          gl.disableVertexAttribArray(loc.aPos);
          gl.activeTexture(gl.TEXTURE0);
        }
      },
      set: function (img) { pending = img; }
    };
  })();

  // ---------- flow layer (moving water surface along the modelled velocity field) ----------
  // One quad over the model box, all on the GPU. Per pixel: the depth frames around t give a smooth wet mask (bilinear
  // on the 20 m depth classes, so nothing moves on dry land); the 100 m velocity field is read bilinearly, weighted by
  // each block's wet share, and interpolated between its 15-min frames; a tiling ripple texture is then advected
  // along that velocity with the flow-map technique (two layers half a cycle apart, cross-faded so the resets never
  // show), smeared a little along the current so fast water reads as streaks, and lit with a soft glint.
  // The animation clock only runs while the replay plays and eases to a stop on pause: a paused picture is still.
  var flowLayer = (function () {
    var gl, prog, buf, loc = {}, F = null, img = null, ftex = null, ntex = null, clock = 0, rate = 0, lastT = 0;
    var Q = 160, T = 1.6; // ripple tile (px at the zoom level it belongs to; wavelengths Q/7..Q/2.5), flow-map cycle (s)
    var VS = 'attribute vec2 aPos;attribute vec2 aUv;uniform mat4 uM;varying vec2 vUv;' +
      'void main(){vUv=aUv;gl_Position=uM*vec4(aPos,0.0,1.0);}';
    var FS = [
      'precision highp float;varying vec2 vUv;',
      'uniform sampler2D uDa;uniform sampler2D uDb;uniform vec3 uMa;uniform vec3 uMb;uniform float uKa;uniform float uKb;uniform float uDt;uniform vec2 uDs;',
      'uniform sampler2D uF;uniform vec4 uFa;uniform vec4 uFb;uniform vec2 uFn;uniform float uFt;uniform float uVmax;',
      'uniform sampler2D uN;uniform vec2 uBox;uniform vec4 uLod;uniform float uPh;uniform float uT;uniform vec3 uHi;uniform float uDk;uniform float uOp;',
      'float code(sampler2D s,vec3 m,float d,vec2 uv){float x=floor(dot(texture2D(s,uv).rgb,m)*255.0+0.5);return mod(floor(x/d+0.001),5.0);}',
      'float depthAt(sampler2D s,vec3 m,float d,vec2 uv){vec2 p=uv*uDs-0.5;vec2 i=floor(p);vec2 f=p-i;vec2 c=(i+0.5)/uDs;vec2 dx=vec2(1.0/uDs.x,0.0);vec2 dy=vec2(0.0,1.0/uDs.y);',
      ' return mix(mix(code(s,m,d,c),code(s,m,d,c+dx),f.x),mix(code(s,m,d,c+dy),code(s,m,d,c+dx+dy),f.x),f.y);}',
      // velocity (m/s, x east, y north) from one atlas cell: bilinear, each block weighted by its wet share
      'vec3 tap(vec4 cell,vec2 c,float w){c=clamp(c,vec2(0.0),uFn-1.0);vec3 s=texture2D(uF,cell.xy+(c+0.5)/uFn*cell.zw).rgb;float k=w*s.b;',
      ' return vec3((s.rg*255.0-128.0)/127.0*uVmax*k,k);}',
      'vec2 vel(vec4 cell,vec2 uv){vec2 p=uv*uFn-0.5;vec2 i=floor(p);vec2 f=p-i;',
      ' vec3 a=tap(cell,i,(1.0-f.x)*(1.0-f.y))+tap(cell,i+vec2(1.0,0.0),f.x*(1.0-f.y))+tap(cell,i+vec2(0.0,1.0),(1.0-f.x)*f.y)+tap(cell,i+vec2(1.0,1.0),f.x*f.y);',
      ' return a.xy/max(a.z,0.004);}',
      'vec3 nz(vec2 x){return texture2D(uN,x/' + Q.toFixed(1) + ').rgb*2.0-1.0;}', // value, slope x, slope y; x in level px
      // one advected layer: the ripple texture at x (level px), smeared over L px along the current d (line-integral style)
      'vec3 lay(vec2 x,vec2 d,float L){vec2 o=d*(L*0.25);return (nz(x-2.0*o)+nz(x-o)+nz(x)+nz(x+o)+nz(x+2.0*o))*0.2;}',
      // flow-map at one zoom level: s = level px per metre, v = velocity in level px per s
      'vec3 surf(float s,vec2 v,vec2 d,float L,float pn){vec2 x=vUv*uBox*s;',
      ' float p0=fract(uPh+pn);float p1=fract(p0+0.5);float w0=1.0-abs(2.0*p0-1.0);float w1=1.0-w0;',
      ' vec3 a=lay(x-v*(p0*uT),d,L);vec3 b=lay(x-v*(p1*uT)+vec2(53.0,91.0),d,L);',
      ' return (a*w0+b*w1)/sqrt(w0*w0+w1*w1);}',
      'void main(){',
      // only inside the depth layer's water edge (>= 5 cm, same bilinear class field), faded towards the edge
      ' float L=mix(depthAt(uDa,uMa,uKa,vUv),depthAt(uDb,uMb,uKb,vUv),uDt);if(L<0.5)discard;',
      ' vec2 u=mix(vel(uFa,vUv),vel(uFb,vUv),uFt);float sp=length(u);',
      ' float amp=smoothstep(0.5,1.2,L)*mix(0.35,1.0,smoothstep(1.2,3.2,L))*smoothstep(0.03,0.25,sp)*mix(0.45,1.0,smoothstep(0.25,1.5,sp))*uOp;',
      ' if(amp<0.004)discard;',
      ' vec2 d=vec2(u.x,-u.y)/max(sp,1e-4);', // uv y runs south
      ' float vis=30.0*sp/(1.0+0.6*sp);', // screen px per s: 1 m/s ~ 19 px/s, compressive so floods in rivers do not smear
      ' float st=mix(4.0,110.0,smoothstep(0.1,1.8,sp));', // streak length, px
      ' float pn=texture2D(uN,vUv*uBox/700.0).r;', // per-place phase (fixed on the ground), so cycles never pulse in step
      // two zoom levels cross-faded, so ripples keep their on-screen size while zooming; a level at weight ~0 is skipped
      ' float w=uLod.w;vec3 h=vec3(0.0);',
      ' if(w<0.99)h=surf(uLod.x,d*vis*uLod.z,d,st,pn);',
      ' if(w>0.01){vec3 h1=surf(uLod.y,d*vis*uLod.z*2.0,d,st,pn);h=(h*(1.0-w)+h1*w)/sqrt((1.0-w)*(1.0-w)+w*w);}',
      ' vec3 n=normalize(vec3(-h.yz*1.6,1.0));vec3 H=normalize(vec3(-0.35,-0.45,1.0)+vec3(0.0,0.0,1.0));',
      ' float spec=pow(max(dot(n,normalize(H)),0.0),36.0);',
      ' float lit=dot(n,normalize(vec3(-0.45,-0.55,0.7)))-0.7;',
      ' float aHi=amp*clamp(0.55*spec+0.6*max(lit,0.0)+0.14*smoothstep(0.3,0.9,h.x),0.0,0.62);',
      ' float aDk=amp*uDk*clamp(smoothstep(0.0,0.8,-h.x)+2.0*max(-lit,0.0),0.0,1.0);',
      ' gl_FragColor=vec4(uHi*aHi,min(1.0,aHi+aDk));}'
    ].join('\n');
    // tiling ripple texture: a sum of waves with whole-number wavenumbers (so it wraps), value in R, slope in G, B
    function ripples() {
      var S = 128, W = [], r = 0.5, rnd = function () { r = (r * 9301 + 49297) % 233280; return r / 233280; };
      for (var k = 0; k < 36; k++) {
        var kx, ky, m;
        do { kx = Math.round((rnd() * 2 - 1) * 7); ky = Math.round((rnd() * 2 - 1) * 7); m = Math.hypot(kx, ky); } while (m < 2.5 || m > 7.5);
        W.push([kx * 2 * Math.PI / S, ky * 2 * Math.PI / S, rnd() * 6.2832, 1 / m]);
      }
      var V = new Float32Array(S * S * 3), mx = [0, 0, 0];
      for (var y = 0; y < S; y++) for (var x = 0; x < S; x++) {
        var v = 0, gx = 0, gy = 0;
        for (var j = 0; j < W.length; j++) { var w = W[j], a = w[0] * x + w[1] * y + w[2], c = Math.cos(a) * w[3]; v += Math.sin(a) * w[3]; gx += c * w[0] * S / 8; gy += c * w[1] * S / 8; }
        var i = (y * S + x) * 3; V[i] = v; V[i + 1] = gx; V[i + 2] = gy;
        mx[0] = Math.max(mx[0], Math.abs(v)); mx[1] = Math.max(mx[1], Math.abs(gx), Math.abs(gy));
      }
      var D = new Uint8Array(S * S * 4);
      for (var q = 0; q < S * S; q++) {
        D[q * 4] = Math.round(127.5 + 127.5 * V[q * 3] / mx[0]);
        D[q * 4 + 1] = Math.round(127.5 + 127.5 * V[q * 3 + 1] / mx[1]);
        D[q * 4 + 2] = Math.round(127.5 + 127.5 * V[q * 3 + 2] / mx[1]);
        D[q * 4 + 3] = 255;
      }
      var tx = gl.createTexture();
      gl.bindTexture(gl.TEXTURE_2D, tx);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false); gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, S, S, 0, gl.RGBA, gl.UNSIGNED_BYTE, D);
      gl.generateMipmap(gl.TEXTURE_2D);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.REPEAT);
      return tx;
    }
    function cell(f) { return [(f % F.cols) / F.cols, Math.floor(f / F.cols) / F.rows, 1 / F.cols, 1 / F.rows]; } // atlas cell of flow frame f, in uv
    return {
      layer: {
        id: 'flow', type: 'custom', renderingMode: '2d',
        onAdd: function (m, g) {
          gl = g; prog = program(gl, VS, FS);
          ['aPos', 'aUv'].forEach(function (k) { loc[k] = gl.getAttribLocation(prog, k); });
          ['uM', 'uDa', 'uDb', 'uMa', 'uMb', 'uKa', 'uKb', 'uDt', 'uDs', 'uF', 'uFa', 'uFb', 'uFn', 'uFt', 'uVmax', 'uN', 'uBox', 'uLod', 'uPh', 'uT', 'uHi', 'uDk', 'uOp']
            .forEach(function (k) { loc[k] = gl.getUniformLocation(prog, k); });
          buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, quad(F.corners), gl.STATIC_DRAW);
          ntex = ripples();
          lastT = performance.now();
        },
        render: function (g, matrix) {
          if (img) { ftex = texture(gl, img, gl.NEAREST); if (img.close) img.close(); img = null; }
          var D = depth.frames();
          if (!F || !ftex || !D) return;
          // animation clock: runs with the replay, eases to a stop in about half a second when paused
          var now = performance.now(), real = (now - lastT) / 1000, dt = Math.min(0.1, real); lastT = now;
          var target = playing && !reduced ? 1 : 0;
          rate += (target - rate) * Math.min(1, real * 6);
          if (target === 0 && rate < 0.003) rate = 0;
          clock = (clock + dt * rate) % (T * 1000);
          var fi = Math.max(0, Math.min(F.n - 1, t * meta.frame_min / F.frame_min)), f0 = Math.floor(fi), f1 = Math.min(f0 + 1, F.n - 1);
          var z = map.getZoom(), zl = Math.floor(z), lat = map.getCenter().lat;
          var mppL = function (zz) { return 40075016.7 * Math.cos(lat * Math.PI / 180) / (512 * Math.pow(2, zz)); };
          var fr = z - zl, w1 = Math.min(1, Math.max(0, (fr - 0.15) / 0.7)); w1 = w1 * w1 * (3 - 2 * w1); // mostly one level, blended over the middle of each zoom step
          gl.useProgram(prog);
          gl.uniformMatrix4fv(loc.uM, false, matrix);
          gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, D.A.tex); gl.uniform1i(loc.uDa, 0);
          gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, D.B.tex); gl.uniform1i(loc.uDb, 1);
          gl.activeTexture(gl.TEXTURE2); gl.bindTexture(gl.TEXTURE_2D, ftex); gl.uniform1i(loc.uF, 2);
          gl.activeTexture(gl.TEXTURE3); gl.bindTexture(gl.TEXTURE_2D, ntex); gl.uniform1i(loc.uN, 3);
          gl.uniform3fv(loc.uMa, D.A.m); gl.uniform3fv(loc.uMb, D.B.m); gl.uniform1f(loc.uKa, D.A.d); gl.uniform1f(loc.uKb, D.B.d);
          gl.uniform1f(loc.uDt, D.ft); gl.uniform2f(loc.uDs, meta.w, meta.h);
          gl.uniform4fv(loc.uFa, cell(f0)); gl.uniform4fv(loc.uFb, cell(f1)); gl.uniform2f(loc.uFn, F.w, F.h);
          gl.uniform1f(loc.uFt, fi - f0); gl.uniform1f(loc.uVmax, F.vmax_ms);
          gl.uniform2f(loc.uBox, F.w * F.cell_m, F.h * F.cell_m);
          // level px per metre at the two zoom levels around z, the level-to-screen scale, and the cross-fade weight
          gl.uniform4f(loc.uLod, 1 / mppL(zl), 1 / mppL(zl + 1), Math.pow(2, zl - z), w1);
          gl.uniform1f(loc.uPh, (clock / T) % 1); gl.uniform1f(loc.uT, T);
          gl.uniform3fv(loc.uHi, flowRGB.hi); gl.uniform1f(loc.uDk, flowRGB.dk); gl.uniform1f(loc.uOp, 1);
          gl.bindBuffer(gl.ARRAY_BUFFER, buf);
          gl.enableVertexAttribArray(loc.aPos); gl.vertexAttribPointer(loc.aPos, 2, gl.FLOAT, false, 16, 0);
          gl.enableVertexAttribArray(loc.aUv); gl.vertexAttribPointer(loc.aUv, 2, gl.FLOAT, false, 16, 8);
          gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
          gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
          gl.disableVertexAttribArray(loc.aPos); gl.disableVertexAttribArray(loc.aUv);
          gl.activeTexture(gl.TEXTURE0);
          if (rate > 0) map.triggerRepaint(); // only animate while the water is moving; a paused map is not redrawn
        }
      },
      set: function (info, image) {
        F = info; img = image; F.frame_min = info.frame_min || (meta.nf - 1) * meta.frame_min / Math.max(1, info.n - 1);
      }
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
  function getJson(url) { return fetch(url).then(function (r) { if (!r.ok) throw new Error(url + ' ' + r.status); return r.json(); }); }
  var done = 0, total = 1;
  function progress(label) {
    done++;
    var p = Math.min(1, done / total);
    $('loadBar').style.width = (p * 100).toFixed(0) + '%';
    $('loadText').textContent = label || ('Loading storm frames… ' + Math.round(p * 100) + '%');
  }

  // ---------- forecast tab ----------
  if (runKey === 'forecast') {
    getJson('site/data/forecast_status.json').then(function (s) {
      var run0 = s && s.runs && s.runs[0], dir = s && (s.dir || (run0 && run0.viewer) || (s.state === 'run' && s.run));
      if (s && s.state === 'quiet') { forecastQuiet(s); return; }
      var ok = s && (s.ready === true || s.status === 'ok' || s.state === 'run') && dir;
      if (!ok) throw new Error('forecast not ready');
      base = 'site/data/' + String(dir).replace(/^(site\/)?data\//, '').replace(/\/?$/, '/');
      if (!s.title && s.headline) s.title = s.headline;
      if (s.title) $('runTitle').textContent = s.title;
      $('runKind').textContent = s.kind || ('Forecast issued ' + (s.issued ? fmtShort.format(new Date(s.issued)) : '') + ' from the NOAA HRRR rain forecast.');
      start();
    }).catch(function () { forecastPlaceholder(); });
  } else start();

  // forecast issued, but rain below the gate: a live 'quiet' card with the forecast rain, no replay
  function forecastQuiet(s) {
    forecastPlaceholder();
    var R = (s.rain && s.rain.district) || {}, v = s.valid || [], f = function (x) { return x ? fmtShort.format(new Date(x)) : ''; };
    var towns = ((s.rain && s.rain.towns) || []).slice().sort(function (a, b) { return (b.max24h_mm || 0) - (a.max24h_mm || 0); }).slice(0, 3)
      .filter(function (t) { return t.max24h_mm > 0; });
    var g = (s.gate && s.gate.thresholds) || {};
    $('runStats').innerHTML = '<span class="tag-live">Live</span> ' + esc(s.headline || 'No road closures expected');
    var c = $('forecastCard');
    c.innerHTML = '<span class="tag-live">Live · updated every 6 h</span><h2 id="fcTitle">' + esc(s.headline || 'No road closures expected') + '</h2>' +
      '<p>NOAA HRRR forecast issued ' + esc(f(s.issued)) + ', valid to ' + esc(f(v[1])) + '. Heaviest forecast rain anywhere in District 3: <b>' +
      (R.max6h_mm || 0).toFixed(0) + ' mm in 6 h</b>, <b>' + (R.max24h_mm || 0).toFixed(0) + ' mm in 24 h</b>' +
      (towns.length ? ' (wettest: ' + towns.map(function (t) { return esc(t.town) + ' ' + t.max24h_mm.toFixed(0) + ' mm'; }).join(', ') + ')' : '') + '.</p>' +
      '<p class="muted">The flood model runs on the road network when a town is forecast ' + (g.max6h_mm || 25) + ' mm in 6 h or ' + (g.max24h_mm || 40) +
      ' mm in 24 h. Below that, no closures are expected.</p><a href="?run=leominster_sep2023">See what the model shows for a real storm: Leominster 2023</a>';
  }
  function forecastPlaceholder() {
    document.documentElement.classList.add('no-replay');
    $('runKind').textContent = 'Road-by-road closure forecast for the next 48 hours.';
    $('runStats').innerHTML = '<span class="tag-dev">In development</span>';
    $('forecastCard').hidden = false;
    $('legend').hidden = true;
    map = new maplibregl.Map({ container: 'map', bounds: D3_BOUNDS, fitBoundsOptions: { padding: framePadding() }, attributionControl: false, dragRotate: false, style: baseStyle() });
    map.addControl(new maplibregl.AttributionControl({ compact: true }));
    map.once('style.load', applyTheme);
  }

  function start() {
    getJson(base + 'meta.json').then(function (m) {
      meta = m; nf = m.nf;
      t0 = new Date(m.storm_start.replace(/Z$/, ':00Z'));
      $('scrub').max = nf - 1;
      $('runStats').innerHTML = m.kofn ? '<b>' + n(m.kofn.likely) + '</b> road segments likely closed (2 or more of ' + m.kofn.n + ' forecast runs agree), <b>' +
        n(m.kofn.possible) + '</b> possible (1 of ' + m.kofn.n + '), out of ' + n(m.segments_in_box) + ' segments in the area.' :
        '<b>' + n(m.segments_p_ge_50) + '</b> road segments likely closed (' + m.km_p_ge_50 + ' km), <b>' +
        n(m.segments_may_close) + '</b> more may close, <b>' + n(m.culverts_overtopped) + '</b> culverts overtopped, out of ' +
        n(m.segments_in_box) + ' segments in the area.';
      var peak = 0, cp = m.closed_per_frame || [];
      cp.forEach(function (v, i) { if (v > cp[peak]) peak = i; });
      t = peak;
      drawChart();
      initMap();
    }).catch(function (e) { $('loadText').textContent = 'The storm data did not load. Reload the page to try again.'; console.error(e); });
  }

  // ---------- map ----------
  function baseStyle() {
    return {
      version: 8,
      sources: {
        // CARTO raster tiles now ask for an API key on this domain: Esri basemaps (no key)
        voy: ESRI('World_Street_Map', 19, 'Esri, HERE, Garmin, © OpenStreetMap contributors, and the GIS User Community'),
        voyl: ESRI('Canvas/World_Light_Gray_Reference', 16, 'Esri'),
        drk: ESRI('Canvas/World_Dark_Gray_Base', 16, 'Esri, HERE, Garmin, © OpenStreetMap contributors'),
        drkl: ESRI('Canvas/World_Dark_Gray_Reference', 16, 'Esri'),
        sat: ESRI('World_Imagery', 18, 'Imagery © Esri, Maxar, Earthstar Geographics, USDA, USGS, AeroGRID, IGN, and the GIS User Community'),
        hill: ESRI('Elevation/World_Hillshade', 16, 'Hillshade © Esri, USGS, NGA, NASA, CGIAR, N Robinson, NCEAS, NLS, OS, NMA, Geodatastyrelsen, Rijkswaterstaat, GSA, Geoland, FEMA, Intermap')
      },
      layers: [
        { id: 'b-hill', type: 'raster', source: 'hill', layout: { visibility: 'none' }, paint: { 'raster-fade-duration': 150 } },
        { id: 'b-voy', type: 'raster', source: 'voy', layout: { visibility: 'none' }, paint: { 'raster-fade-duration': 150 } },
        { id: 'b-sat', type: 'raster', source: 'sat', layout: { visibility: 'none' }, paint: { 'raster-fade-duration': 150, 'raster-saturation': -0.25, 'raster-brightness-max': 0.82, 'raster-contrast': 0.05 } },
        { id: 'b-dark', type: 'raster', source: 'drk', layout: { visibility: 'none' }, paint: { 'raster-fade-duration': 150, 'raster-brightness-min': 0.04 } },
        { id: 'l-voy', type: 'raster', source: 'voyl', layout: { visibility: 'none' }, paint: { 'raster-fade-duration': 150 } },
        { id: 'l-dark', type: 'raster', source: 'drkl', layout: { visibility: 'none' }, paint: { 'raster-fade-duration': 150 } }
      ]
    };
  }
  function boxBounds() {
    var lons = meta.corners.map(function (c) { return c[0]; }), lats = meta.corners.map(function (c) { return c[1]; });
    return [[Math.min.apply(0, lons), Math.min.apply(0, lats)], [Math.max.apply(0, lons), Math.max.apply(0, lats)]];
  }
  // padding that keeps the framed area clear of the panels, measured from the panels themselves
  function framePadding() {
    var W = window.innerWidth, H = window.innerHeight, g = 14;
    var card = $('card').getBoundingClientRect(), lg = $('legend').getBoundingClientRect(), pl = document.querySelector('.player').getBoundingClientRect();
    var fc = $('forecastCard'); var p;
    if (!small()) {
      p = { top: g + 8, bottom: H - (pl.height ? pl.top : H) + g, left: card.right + g, right: (lg.width && !$('legend').hidden ? W - lg.left : 0) + g + 40 };
      if (!fc.hidden) { var r = fc.getBoundingClientRect(); p.bottom = Math.max(p.bottom, H - r.top + g); }
    } else {
      var lgTop = lg.width && !$('legend').hidden ? lg.top : H;
      p = { top: card.bottom + g, bottom: H - Math.min(pl.height ? pl.top : H, lgTop) + g, left: g, right: g };
      if (!fc.hidden) { var r2 = fc.getBoundingClientRect(); p.bottom = Math.max(p.bottom, H - r2.top + g); }
    }
    // never leave less than 40% of the map free: shrink padding proportionally if the panels are huge
    var fw = W - p.left - p.right, fh = H - p.top - p.bottom;
    if (fw < W * 0.4) { var k = (W * 0.6) / (p.left + p.right); p.left *= k; p.right *= k; }
    if (fh < H * 0.3) { var k2 = (H * 0.7) / (p.top + p.bottom); p.top *= k2; p.bottom *= k2; }
    return p;
  }

  function initMap() {
    map = new maplibregl.Map({
      container: 'map', bounds: boxBounds(), maxZoom: 17, minZoom: 6, dragRotate: false, pitchWithRotate: false,
      fitBoundsOptions: { padding: framePadding() }, attributionControl: false, fadeDuration: 0, style: baseStyle()
    });
    map.addControl(new maplibregl.AttributionControl({ compact: true, customAttribution: 'Flood model: LISFLOOD-FP 8.2 · Rain: NOAA MRMS · Roads: MassDOT' }));
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    map.touchZoomRotate.disableRotation();
    map.once('style.load', function () {
      map.addLayer(depth.layer, 'l-voy');
      applyTheme();
      styleReady();
    });
    map.on('movestart', function (e) { if (e.originalEvent) { userMoved = true; if (follow) setFollow(false); } });
    var at = document.querySelector('.maplibregl-ctrl-attrib');
    if (at && small()) at.classList.remove('maplibregl-compact-show');
    loadData();
  }
  var styleWaiters = [], styleOk = false;
  function styleReady() { styleOk = true; styleWaiters.splice(0).forEach(function (f) { f(); }); }
  function whenStyle(f) { if (styleOk) f(); else styleWaiters.push(f); }

  function loadData() {
    total = meta.sheets.length + 2;
    var jobs = meta.sheets.map(function (s, i) {
      return getBitmap(base + s).then(function (img) { depth.add(i, img); progress(); if (styleOk) map.triggerRepaint(); });
    });
    jobs.push(getJson(base + 'roads.json').then(function (g) {
      return new Promise(function (res) { whenStyle(function () { addRoads(g); progress(); res(); }); });
    }));
    // optional layers: a missing file only hides that layer
    jobs.push(getJson(base + 'rain.json').then(function (r) {
      return getBitmap(base + r.sheet).then(function (img) {
        r.off = (new Date(r.start.replace(/Z$/, ':00Z')) - t0) / 60000;
        rain = r; rainLayer.set(img);
        whenStyle(function () { map.addLayer(rainLayer.layer, 'l-voy'); vis('rain', $('lyRain').checked); });
        $('rainRow').hidden = $('rainRamp').hidden = $('rainLabels').hidden = false;
        progress();
      });
    }).catch(function () { progress(); }));
    jobs.push(getJson(base + 'refs.json').then(function (r) { refs = r; whenStyle(function () { try { addRefs(); } catch (e) { console.error('refs', e); } }); }).catch(function (e) { console.warn('refs', e); }));
    if (meta.flow) {
      jobs.push(getJson(base + meta.flow).then(function (fi) {
        return getBitmap(base + fi.sheet).then(function (img) {
          flowLayer.set(fi, img);
          whenStyle(function () { map.addLayer(flowLayer.layer, map.getLayer('rain') ? 'rain' : 'l-voy'); vis('flow', $('lyFlow').checked); });
          $('flowRow').hidden = $('flowKey').hidden = false;
        });
      }).catch(function (e) { console.warn('flow', e); }));
    } else $('flowSoon').hidden = false;
    Promise.all(jobs).then(function () {
      ready = true;
      $('loading').classList.add('done');
      $('play').disabled = false;
      setTime(t);
      fitView(currentView, false);
    }).catch(function (e) { $('loadText').textContent = 'Some storm data did not load. Reload the page to try again.'; console.error(e); });
  }

  // ---------- roads ----------
  function addRoads(g) {
    g.features.forEach(function (f) {
      var p = f.properties;
      if (p.d || p.iv) segs.push({ id: f.id, d: p.d || null, iv: p.iv || null, v: -1, f: f });
    });
    map.addSource('roads', { type: 'geojson', data: g, tolerance: 0.2 });
    var w = function (a, b) { return ['interpolate', ['linear'], ['zoom'], 9, a, 15, b]; };
    var D = ['coalesce', ['feature-state', 'd'], 0];
    var byD = function (z9, z15) { // width grows with water on the road, scaled by zoom
      return ['interpolate', ['linear'], ['zoom'], 9, ['interpolate', ['linear'], D, 0, z9[0], 30, z9[1], 100, z9[2]], 15, ['interpolate', ['linear'], D, 0, z15[0], 30, z15[1], 100, z15[2]]];
    };
    map.addLayer({ id: 'peak', type: 'line', source: 'roads', filter: ['>=', ['get', 'p'], 0.5], layout: { 'line-cap': 'round' }, paint: { 'line-width': w(1, 2.5) } });
    if (meta.kofn) { // forecast ensemble: how many of the time-lagged forecast runs close the road (likely >= 2, possible 1)
      map.addLayer({ id: 'agree', type: 'line', source: 'roads', filter: ['has', 'k'], layout: { 'line-cap': 'round' }, paint: { 'line-width': w(2, 5), 'line-opacity': 0.9 } });
      kofnLegend();
    }
    map.addLayer({ id: 'may', type: 'line', source: 'roads', filter: ['==', ['get', 'm'], 1], paint: { 'line-width': w(1.5, 3.5), 'line-dasharray': [2, 1.2] } });
    map.addLayer({ id: 'risk', type: 'line', source: 'roads', filter: ['has', 'rk'], layout: { visibility: 'none', 'line-cap': 'round' }, paint: { 'line-width': w(2.5, 6) } });
    map.addLayer({ id: 'halo', type: 'line', source: 'roads', filter: ['has', 'd'], layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: { 'line-width': byD([0, 9, 12], [0, 20, 26]), 'line-blur': w(4, 9), 'line-opacity': ['interpolate', ['linear'], D, 22, 0, 40, 0.42] } });
    map.addLayer({ id: 'wetcase', type: 'line', source: 'roads', filter: ['has', 'd'], layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: { 'line-width': byD([2.5, 5, 6], [4.5, 9.5, 11]), 'line-opacity': ['interpolate', ['linear'], D, 5, 0, 12, 1] } });
    map.addLayer({ id: 'wet', type: 'line', source: 'roads', filter: ['has', 'd'], layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: { 'line-width': byD([1.2, 3, 3.8], [2.5, 6.5, 7.5]), 'line-opacity': ['interpolate', ['linear'], D, 5, 0, 10, 1] } });
    map.addLayer({ id: 'hit', type: 'line', source: 'roads', paint: { 'line-width': 16, 'line-opacity': 0 } });
    applyTheme();
    if (g.features.some(function (f) { return f.properties.rk; })) { $('riskRow').hidden = false; }
    map.on('mouseenter', 'hit', function () { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', 'hit', function () { map.getCanvas().style.cursor = ''; });
    map.on('click', 'hit', function (e) {
      if (map.queryRenderedFeatures(e.point, { layers: refLayers.filter(function (l) { return map.getLayer(l); }) }).length) return;
      var vis_ = e.features.filter(function (f) {
        var p = f.properties; return p.p >= 0.5 || p.m === 1 || (p.rk && $('lyRisk').checked) || p.d || p.k;
      });
      var f = (vis_.length ? vis_ : e.features).sort(function (a, b) { return b.properties.p - a.properties.p; })[0];
      showPopup(e.lngLat, popupHtml(f));
    });
    computeViews(g);
  }
  function kofnLegend() {
    var lb = $('legendBody'); if (!lb || $('kofnKey')) return;
    var k = document.createElement('div'); k.id = 'kofnKey'; k.className = 'kofn';
    k.innerHTML = '<h2>Forecast agreement</h2><label class="row"><input type="checkbox" id="lyAgree" checked><span>Roads closed in the ' + meta.kofn.n + ' forecast runs</span></label>' +
      '<p class="note"><i style="display:inline-block;width:18px;height:4px;border-radius:2px;vertical-align:middle;background:var(--closed)"></i> likely closed: 2 or more of ' + meta.kofn.n + ' agree<br>' +
      '<i style="display:inline-block;width:18px;height:4px;border-radius:2px;vertical-align:middle;background:var(--amber)"></i> possible: 1 of ' + meta.kofn.n +
      '<br>Runs from this and the 7 previous HRRR forecasts; the replay shows this forecast\'s run.</p>';
    var h2 = lb.querySelectorAll('h2'); lb.insertBefore(k, h2.length > 1 ? h2[1] : null);
    $('lyAgree').addEventListener('change', function () { vis('agree', this.checked); });
  }
  function showPopup(ll, html) {
    if (popup) popup.remove();
    if (hover) hover.remove();
    popup = new maplibregl.Popup({ maxWidth: '300px' }).setLngLat(ll).setHTML(html).addTo(map);
  }

  var CLS = ['Local or collector road', 'Arterial', 'Highway'];
  function arr(v) { return v ? (typeof v === 'string' ? JSON.parse(v) : v) : null; }
  function popupHtml(f) {
    var p = f.properties, iv = arr(p.iv), a = arr(p.a), rc = arr(p.rc), d = arr(p.d);
    var h = '<div class="pp"><h3>' + esc(p.n || 'Unnamed road') + '</h3><p class="sub">' + esc(p.t ? p.t + ', ' : '') + CLS[p.c || 0] + '</p><dl>';
    if (p.k) h += '<dt>Forecast runs closing it</dt><dd><b>' + p.k + ' of ' + meta.kofn.n + '</b> (' + (p.k >= 2 ? 'likely closed' : 'possible') + ')</dd>';
    h += '<dt>' + (p.k ? 'Chance of closing in the run shown' : 'Chance of closing') + '</dt><dd><b>' + Math.round(p.p * 100) + '%</b></dd>';
    if (d) {
      var fa = Math.min(Math.floor(t), nf - 1), now = Math.round(((d[fa] || 0) * (1 - (t - fa)) + (d[fa + 1] || 0) * (t - fa)));
      h += '<dt>Water on it now</dt><dd>' + (now >= 3 ? now + ' cm' : 'dry') + '</dd>';
    }
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

  // ---------- reference layers ----------
  var refLayers = ['r-crossings', 'r-bridges', 'r-dams', 'r-facilities', 'r-reports', 'r-gauges'];
  var ICONS = {
    gauge: function (c, s) { c.fillStyle = '#0b7a75'; c.beginPath(); c.moveTo(s / 2, 2); c.lineTo(s - 2, s - 3); c.lineTo(2, s - 3); c.closePath(); c.fill(); c.stroke(); },
    culvert: function (c, s) { c.fillStyle = '#8a5a2b'; c.beginPath(); c.arc(s / 2, s / 2, s / 2 - 3, 0, 7); c.fill(); c.stroke(); c.fillStyle = '#fff'; c.beginPath(); c.arc(s / 2, s / 2, s / 5, 0, 7); c.fill(); },
    culvertRisk: function (c, s) { c.fillStyle = '#c0392b'; c.beginPath(); c.arc(s / 2, s / 2, s / 2 - 2, 0, 7); c.fill(); c.stroke(); c.fillStyle = '#fff'; c.beginPath(); c.arc(s / 2, s / 2, s / 5, 0, 7); c.fill(); },
    bridge: function (c, s) { c.fillStyle = '#4b5966'; rr(c, 2, s * 0.3, s - 4, s * 0.4, 3); c.fill(); c.stroke(); },
    dam: function (c, s) { c.fillStyle = '#3d5a80'; c.beginPath(); c.moveTo(3, s - 3); c.lineTo(s * 0.38, 3); c.lineTo(s * 0.62, 3); c.lineTo(s - 3, s - 3); c.closePath(); c.fill(); c.stroke(); },
    hospital: function (c, s) { c.fillStyle = '#d6223a'; rr(c, 2, 2, s - 4, s - 4, 4); c.fill(); c.stroke(); cross(c, s); },
    fire: function (c, s) { c.fillStyle = '#e8590c'; rr(c, 2, 2, s - 4, s - 4, 4); c.fill(); c.stroke(); letter(c, s, 'F'); },
    police: function (c, s) { c.fillStyle = '#1c4e9c'; rr(c, 2, 2, s - 4, s - 4, 4); c.fill(); c.stroke(); letter(c, s, 'P'); },
    report: function (c, s) { c.fillStyle = '#6f2dbd'; c.beginPath(); c.moveTo(s / 2, s - 2); c.arc(s / 2, s * 0.4, s * 0.34, Math.PI * 0.8, Math.PI * 2.2); c.closePath(); c.fill(); c.stroke(); c.fillStyle = '#fff'; c.beginPath(); c.arc(s / 2, s * 0.4, s * 0.13, 0, 7); c.fill(); }
  };
  function rr(c, x, y, w, h, r) { c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
  function cross(c, s) { c.fillStyle = '#fff'; var a = s * 0.18, b = s * 0.56; c.fillRect(s / 2 - a / 2, s / 2 - b / 2, a, b); c.fillRect(s / 2 - b / 2, s / 2 - a / 2, b, a); }
  function letter(c, s, L) { c.fillStyle = '#fff'; c.font = '800 ' + Math.round(s * 0.62) + 'px Overpass, system-ui, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(L, s / 2, s / 2 + 1); }
  function iconCanvas(name, s) {
    var cv = document.createElement('canvas'); cv.width = cv.height = s; var c = cv.getContext('2d');
    c.strokeStyle = 'rgba(255,255,255,.95)'; c.lineWidth = Math.max(1.5, s / 14); c.lineJoin = 'round'; ICONS[name](c, s); return cv;
  }
  document.querySelectorAll('.ico').forEach(function (el) { var cv = iconCanvas(el.dataset.ico, 32); cv.setAttribute('aria-hidden', 'true'); el.appendChild(cv); });

  function fc(rows, fn) { return { type: 'FeatureCollection', features: rows.map(function (r, i) { var p = fn(r); return { type: 'Feature', id: i, properties: p, geometry: { type: 'Point', coordinates: [r[0], r[1]] } }; }) }; }
  function addRefs() {
    var R = refs;
    Object.keys(ICONS).forEach(function (k) { var cv = iconCanvas(k, 40); map.addImage('i-' + k, cv.getContext('2d').getImageData(0, 0, 40, 40), { pixelRatio: 2 }); });
    var sets = {
      gauges: R.gauges && R.gauges.length ? { type: 'FeatureCollection', features: R.gauges.map(function (g, i) { return { type: 'Feature', id: i, properties: { k: 'gauge', i: i }, geometry: { type: 'Point', coordinates: [g.lon, g.lat] } }; }) } : null,
      crossings: R.crossings && R.crossings.rows.length ? fc(R.crossings.rows, function (r) { return { k: r[8] === 'Extreme' || r[8] === 'High' ? 'culvertRisk' : 'culvert', road: r[2], stream: r[3], kind: r[4], shape: r[5], span: r[6], cond: r[7], risk: r[8] || '', pov: r[9] }; }) : null,
      bridges: R.bridges && R.bridges.length ? fc(R.bridges, function (r) { return { k: 'bridge', id: r[2], year: r[3], culv: r[4], scour: r[5], adt: r[6] }; }) : null,
      dams: R.dams && R.dams.length ? fc(R.dams, function (r) { return { k: 'dam', name: r[2], river: r[3], hazard: r[4], h: r[5], cond: r[6] }; }) : null,
      facilities: R.facilities ? fc([].concat(
        (R.facilities.hospital || []).map(function (r) { return r.concat('hospital'); }),
        (R.facilities.fire_station || []).map(function (r) { return r.concat('fire'); }),
        (R.facilities.police || []).map(function (r) { return r.concat('police'); })), function (r) { return { k: r[3], name: r[2] }; }) : null,
      reports: R.reports && R.reports.length ? fc(R.reports, function (r) { return { k: 'report', src: r[2], text: r[3], t: r[4], m: r[5], hit: r[6] }; }) : null
    };
    var minz = { crossings: 11, bridges: 11.5, dams: 9, facilities: 10, reports: 8, gauges: 6 };
    ['crossings', 'bridges', 'dams', 'facilities', 'reports', 'gauges'].forEach(function (key) {
      if (!sets[key]) return;
      document.querySelector('label[data-ref="' + key + '"]').hidden = false;
      map.addSource('s-' + key, { type: 'geojson', data: sets[key] });
      map.addLayer({ id: 'r-' + key, type: 'symbol', source: 's-' + key, minzoom: runKey === 'd3_sep2023' ? minz[key] + 1 : minz[key] - 1,
        layout: { 'icon-image': ['concat', 'i-', ['get', 'k']], 'icon-size': key === 'gauges' ? 1.15 : key === 'crossings' ? ['case', ['==', ['get', 'k'], 'culvertRisk'], 0.85, 0.65] : 0.8,
          'icon-allow-overlap': key === 'gauges' || key === 'reports', 'icon-ignore-placement': key !== 'crossings', 'symbol-sort-key': key === 'crossings' ? ['case', ['==', ['get', 'k'], 'culvertRisk'], 0, 1] : 0,
          visibility: document.querySelector('input[data-ref="' + key + '"]').checked ? 'visible' : 'none' } });
      map.on('mouseenter', 'r-' + key, function (e) {
        map.getCanvas().style.cursor = 'pointer';
        if (small()) return;
        if (hover) hover.remove();
        hover = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 12, className: 'tip' }).setLngLat(e.features[0].geometry.coordinates).setHTML(refTip(key, e.features[0].properties)).addTo(map);
      });
      map.on('mouseleave', 'r-' + key, function () { map.getCanvas().style.cursor = ''; if (hover) { hover.remove(); hover = null; } });
      map.on('click', 'r-' + key, function (e) {
        var f = e.features[0];
        showPopup(f.geometry.coordinates, refHtml(key, f.properties));
        if (key === 'gauges') { $('gaugeSel').value = f.properties.i; drawChart(); }
      });
    });
    if (R.gauges && R.gauges.some(function (g) { return g.obs_q; })) {
      var sel = $('gaugeSel'), best = 0, bv = -1;
      R.gauges.forEach(function (g, i) {
        if (!g.obs_q) return;
        var o = document.createElement('option'); o.value = i; o.textContent = g.name.replace(/, MA$/, ''); sel.appendChild(o);
        var mx = Math.max.apply(0, g.obs_q.filter(function (v) { return v != null; }));
        if (mx > bv) { bv = mx; best = i; }
      });
      sel.value = best;
      $('gaugeBand').hidden = false;
      drawChart();
    }
  }
  var KIND = { report: { LSR: 'NWS storm report', StormEvents: 'NOAA Storm Events', culvert_failure: 'Culvert failure', other_damage: 'Damage', flooded: 'Flooding', closed: 'Road closed', impassable: 'Road impassable', washout: 'Washout', sinkhole: 'Sinkhole', bridge_damage: 'Bridge damage' } };
  function gaugeName(g) { return esc(g.name.replace(/, MA$/, '')); }
  function refTip(key, p) {
    if (key === 'gauges') return '<b>' + gaugeName(refs.gauges[p.i]) + '</b><br>USGS river gauge';
    if (key === 'crossings') return '<b>' + esc(p.road || 'Stream crossing') + '</b>' + (p.stream ? ' over ' + esc(p.stream) : '') + (p.risk ? '<br>Risk: ' + esc(p.risk) : '');
    if (key === 'bridges') return '<b>Bridge ' + esc(p.id) + '</b>' + (p.year ? ', built ' + p.year : '');
    if (key === 'dams') return '<b>' + esc(title(p.name)) + '</b><br>Dam' + (p.hazard ? ', ' + esc(p.hazard.toLowerCase()) + ' hazard' : '');
    if (key === 'facilities') return '<b>' + esc(p.name || { hospital: 'Hospital', fire: 'Fire station', police: 'Police station' }[p.k]) + '</b>';
    return '<b>' + esc(KIND.report[p.src] || p.src) + '</b><br>' + esc((p.text || '').slice(0, 80));
  }
  function refHtml(key, p) {
    var h = '<div class="pp">';
    if (key === 'gauges') {
      var g = refs.gauges[p.i];
      h += '<h3>' + gaugeName(g) + '</h3><p class="sub">USGS gauge ' + esc(g.site) + (g.km2 ? ', ' + n(g.km2) + ' km² upstream' : '') + '</p><dl>';
      if (g.obs_rise_m != null) h += '<dt>River rise</dt><dd>observed <b>' + g.obs_rise_m.toFixed(2) + ' m</b>, modelled <b>' + (g.model_rise_m != null ? g.model_rise_m.toFixed(2) + ' m' : '–') + '</b></dd>';
      if (g.obs_peak_utc) h += '<dt>Peak</dt><dd>observed ' + fmtShort.format(new Date(g.obs_peak_utc.replace(/Z$/, ':00Z'))) + (g.model_peak_utc ? ', modelled ' + fmtShort.format(new Date(g.model_peak_utc.replace(/Z$/, ':00Z'))) : '') + '</dd>';
      if (g.obs_peak_q_m3s) h += '<dt>Observed peak flow</dt><dd>' + g.obs_peak_q_m3s.toFixed(1) + ' m³/s</dd>';
      h += '</dl><p class="why">The model is scored against this gauge: the timeline below shows its observed flow through the storm.</p>';
    } else if (key === 'crossings') {
      h += '<h3>' + esc(p.road || 'Stream crossing') + '</h3><p class="sub">' + esc(p.kind === 'culvert' ? 'Culvert' : p.kind === 'bridge' ? 'Bridge crossing' : 'Road–stream crossing') + (p.stream ? ' over ' + esc(p.stream) : '') + '</p><dl>';
      if (p.shape || p.span) h += '<dt>Opening</dt><dd>' + esc(p.shape || '') + (p.span ? (p.shape ? ', ' : '') + (+p.span).toFixed(1) + ' m span' : '') + '</dd>';
      if (p.cond) h += '<dt>Condition</dt><dd>' + esc(p.cond) + ' (NAACC survey)</dd>';
      if (p.risk) h += '<dt>Risk class</dt><dd><b>' + esc(p.risk) + '</b>' + (p.pov != null ? ', ' + Math.round(p.pov * 100) + '% chance the road over it is overtopped' : '') + '</dd>';
      h += '</dl>';
    } else if (key === 'bridges') {
      h += '<h3>Bridge ' + esc(p.id) + '</h3><p class="sub">FHWA National Bridge Inventory' + (p.culv ? ', culvert' : '') + '</p><dl>';
      if (p.year) h += '<dt>Built</dt><dd>' + p.year + '</dd>';
      if (p.adt && +p.adt) h += '<dt>Daily traffic</dt><dd>' + n(+p.adt) + '</dd>';
      if (p.scour && p.scour !== 'N') h += '<dt>Scour rating</dt><dd>' + esc(p.scour) + ' (item 113)</dd>';
      h += '</dl>';
    } else if (key === 'dams') {
      h += '<h3>' + esc(title(p.name)) + '</h3><p class="sub">Dam' + (p.river ? ' on ' + esc(title(p.river)) : '') + ', National Inventory of Dams</p><dl>';
      if (p.hazard) h += '<dt>Hazard potential</dt><dd>' + esc(p.hazard) + '</dd>';
      if (p.h) h += '<dt>Height</dt><dd>' + (p.h * 0.3048).toFixed(1) + ' m</dd>';
      if (p.cond) h += '<dt>Condition</dt><dd>' + esc(p.cond) + '</dd>';
      h += '</dl>';
    } else if (key === 'facilities') {
      h += '<h3>' + esc(p.name || 'Unnamed') + '</h3><p class="sub">' + { hospital: 'Hospital', fire: 'Fire station', police: 'Police station' }[p.k] + '</p><p class="why">Used to count residents who lose access when roads close (OpenStreetMap).</p>';
    } else {
      h += '<h3>' + esc(KIND.report[p.src] || p.src) + '</h3><p class="sub">' + (p.t ? fmtShort.format(new Date(String(p.t).replace(/Z$/, ':00Z'))) : '') + '</p><p>' + esc(p.text) + '</p><dl>';
      if (p.m != null) h += '<dt>Modelled water nearby</dt><dd>' + Math.round(p.m * 100) + ' cm at peak' + (p.hit ? ' (30 cm or more: caught)' : '') + '</dd>';
      h += '</dl>';
    }
    return h + '</div>';
  }

  // ---------- views: overview, hotspots, whole area, follow the storm ----------
  var views = [], currentView = 0, userMoved = false, follow = false, followAt = -1, followLast = 0;
  function computeViews(g) {
    var lat0 = (meta.corners[0][1] + meta.corners[2][1]) / 2, kx = 111.32 * Math.cos(lat0 * Math.PI / 180), ky = 110.57;
    var pts = [];
    g.features.forEach(function (f, i) {
      var p = f.properties; if (!(p.iv || p.p >= 0.5)) return;
      var cs = f.geometry.type === 'LineString' ? f.geometry.coordinates : [].concat.apply([], f.geometry.coordinates);
      var mid = cs[Math.floor(cs.length / 2)];
      var b = [Infinity, Infinity, -Infinity, -Infinity];
      cs.forEach(function (c) { b[0] = Math.min(b[0], c[0]); b[1] = Math.min(b[1], c[1]); b[2] = Math.max(b[2], c[0]); b[3] = Math.max(b[3], c[1]); });
      pts.push({ x: mid[0] * kx, y: mid[1] * ky, b: b, t: p.t, n: p.n, id: f.id, used: false });
    });
    var bb = boxBounds(), diag = Math.hypot((bb[1][0] - bb[0][0]) * kx, (bb[1][1] - bb[0][1]) * ky);
    var R = Math.max(0.9, Math.min(6, diag / 20)), minSize = Math.max(3, Math.round(pts.length * 0.04)), clusters = [];
    function near(p, x, y, r) { return Math.hypot(p.x - x, p.y - y) <= r; }
    while (clusters.length < 5) {
      var free = pts.filter(function (p) { return !p.used; }); if (!free.length) break;
      var best = null, bd = 0;
      free.forEach(function (p) { var d = 0; free.forEach(function (q) { if (near(q, p.x, p.y, R)) d++; }); if (d > bd) { bd = d; best = p; } });
      if (bd < minSize) break;
      var mem = free.filter(function (q) { return near(q, best.x, best.y, 2 * R); });
      var cx = mem.reduce(function (s, q) { return s + q.x; }, 0) / mem.length, cy = mem.reduce(function (s, q) { return s + q.y; }, 0) / mem.length;
      mem = free.filter(function (q) { return near(q, cx, cy, 2 * R); });
      mem.forEach(function (q) { q.used = true; });
      clusters.push(mem);
    }
    function mode(a) { var c = {}, b = '', bn = 0; a.forEach(function (v) { if (!v) return; c[v] = (c[v] || 0) + 1; if (c[v] > bn) { bn = c[v]; b = v; } }); return b; }
    function bounds(mem) {
      var b = [Infinity, Infinity, -Infinity, -Infinity];
      mem.forEach(function (q) { b[0] = Math.min(b[0], q.b[0]); b[1] = Math.min(b[1], q.b[1]); b[2] = Math.max(b[2], q.b[2]); b[3] = Math.max(b[3], q.b[3]); });
      var mw = R * 1.4 / kx, mh = R * 1.4 / ky, cxx = (b[0] + b[2]) / 2, cyy = (b[1] + b[3]) / 2; // never zoom in past a few blocks
      return [[Math.min(b[0], cxx - mw / 2), Math.min(b[1], cyy - mh / 2)], [Math.max(b[2], cxx + mw / 2), Math.max(b[3], cyy + mh / 2)]];
    }
    var hs = clusters.map(function (mem) {
      var town = mode(mem.map(function (q) { return q.t; })) || mode(mem.map(function (q) { return q.n; })) || 'Hotspot';
      return { name: town, road: mode(mem.map(function (q) { return q.n; })), count: mem.length, bounds: bounds(mem), ids: mem.map(function (q) { return q.id; }) };
    });
    hs.forEach(function (h) { if (hs.filter(function (o) { return o.name === h.name; }).length > 1 && h.road) h.name = h.name + ', ' + h.road; });
    // overview: the largest clusters until about two thirds of the closing roads are in view, without zooming far out for stragglers
    var ov = null, cum = 0, area = function (b) { return (b[1][0] - b[0][0]) * (b[1][1] - b[0][1]); };
    hs.slice().sort(function (a, b) { return b.count - a.count; }).forEach(function (h) {
      if (cum >= pts.length * 0.66 && ov) return;
      var u = ov ? [[Math.min(ov[0][0], h.bounds[0][0]), Math.min(ov[0][1], h.bounds[0][1])], [Math.max(ov[1][0], h.bounds[1][0]), Math.max(ov[1][1], h.bounds[1][1])]] : h.bounds;
      if (ov && area(u) > area(ov) * 3 && cum >= pts.length * 0.4) return;
      ov = u; cum += h.count;
    });
    views = [{ name: 'Overview', bounds: ov || bb, hint: 'where most roads close' }].concat(hs.map(function (h) { return { name: h.name, bounds: h.bounds, count: h.count, ids: h.ids }; }));
    views.push({ name: 'Whole area', bounds: bb, hint: 'the full model box' });
    var idToView = {}; views.forEach(function (v, i) { (v.ids || []).forEach(function (id) { idToView[id] = i; }); });
    segs.forEach(function (s) { s.view = idToView[s.id]; });
    var el = $('views'); el.innerHTML = '';
    views.forEach(function (v, i) {
      var b = document.createElement('button'); b.type = 'button'; b.dataset.view = i;
      b.innerHTML = esc(v.name) + (v.count ? ' <span>' + v.count + '</span>' : '');
      b.title = v.count ? v.count + ' roads close here' : v.hint;
      b.setAttribute('aria-pressed', i === currentView ? 'true' : 'false');
      b.addEventListener('click', function () { setFollow(false); fitView(i, true); });
      el.appendChild(b);
    });
    var lab = document.createElement('label'); lab.className = 'follow';
    lab.innerHTML = '<input type="checkbox" id="follow"><span>Follow the storm</span>';
    el.appendChild(lab);
    $('follow').addEventListener('change', function (e) { setFollow(e.target.checked); });
    fitView(0, false);
  }
  function fitView(i, animate) {
    if (!map || !views[i]) return;
    currentView = i; userMoved = false;
    document.querySelectorAll('#views button').forEach(function (b) { b.setAttribute('aria-pressed', +b.dataset.view === i ? 'true' : 'false'); });
    map.fitBounds(views[i].bounds, { padding: framePadding(), maxZoom: 15.5, duration: animate && !reduced ? 1400 : 0, essential: true });
  }
  function setFollow(on) {
    follow = on; followAt = -1; if ($('follow')) $('follow').checked = on;
    if (on) { followLast = 0; followTick(true); }
  }
  // the hotspot with the most roads closing in the last two hours of storm time; moves at most every 4 s, with a slow ease
  function followTick(force) {
    if (!follow || views.length < 3) return;
    var now = performance.now();
    if (!force && now - followLast < 4000) return;
    var win = 120 / meta.frame_min, score = {};
    segs.forEach(function (s) {
      if (s.view == null || !s.iv) return;
      s.iv.forEach(function (iv) { if (iv[0] <= t && iv[0] > t - win) score[s.view] = (score[s.view] || 0) + 1; });
    });
    var best = -1, bs = 0;
    Object.keys(score).forEach(function (k) { if (score[k] > bs) { bs = score[k]; best = +k; } });
    if (best < 0) { if (force && followAt < 0) { followAt = 0; } return; }
    if (best === followAt || (followAt >= 0 && (score[followAt] || 0) * 1.5 >= bs)) return;
    followAt = best; followLast = now; currentView = best;
    document.querySelectorAll('#views button').forEach(function (b) { b.setAttribute('aria-pressed', +b.dataset.view === best ? 'true' : 'false'); });
    var cam = map.cameraForBounds(views[best].bounds, { padding: framePadding(), maxZoom: 15.5 });
    if (cam) map.easeTo({ center: cam.center, zoom: cam.zoom, duration: reduced ? 0 : 2600, easing: function (x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; } });
  }

  // ---------- theme and basemap ----------
  function applyTheme() {
    if (!map || !map.getLayer('b-voy')) return;
    var b = basemap(), L = BASEMAPS[b].layers, P = pal();
    ['b-hill', 'b-voy', 'b-sat', 'b-dark', 'l-voy', 'l-dark'].forEach(function (id) {
      map.setLayoutProperty(id, 'visibility', L[id] ? 'visible' : 'none');
      if (L[id]) map.setPaintProperty(id, 'raster-opacity', L[id]);
    });
    document.querySelectorAll('#basemaps button').forEach(function (x) { x.setAttribute('aria-pressed', x.dataset.bm === b ? 'true' : 'false'); });
    var root = document.documentElement.style;
    ['d1', 'd2', 'd3', 'd4'].forEach(function (k, i) { root.setProperty('--' + k, P.d[i]); });
    root.setProperty('--closed', P.closed); root.setProperty('--amber', P.amber); root.setProperty('--orange', P.orange); root.setProperty('--grey', P.grey);
    root.setProperty('--peak', P.peak); root.setProperty('--peak-op', P.peakOp); root.setProperty('--may', P.may);
    flowRGB = b === 'dark' ? { hi: [0.9, 0.97, 1], dk: 0.24 } : b === 'satellite' ? { hi: [0.92, 0.98, 1], dk: 0.26 } : { hi: [1, 1, 1], dk: 0.2 };
    depth.setRamp(P.d.map(rgba));
    if (map.getLayer('wet')) {
      var D = ['coalesce', ['feature-state', 'd'], 0];
      map.setPaintProperty('wet', 'line-color', ['interpolate', ['linear'], D, 3, P.grey, 10, P.amber, 22, P.orange, 30, P.closed]);
      map.setPaintProperty('wetcase', 'line-color', P.cas);
      map.setPaintProperty('halo', 'line-color', P.halo);
      map.setPaintProperty('peak', 'line-color', P.peak); map.setPaintProperty('peak', 'line-opacity', P.peakOp);
      map.setPaintProperty('may', 'line-color', P.may);
      if (map.getLayer('agree')) map.setPaintProperty('agree', 'line-color', ['case', ['>=', ['get', 'k'], 2], P.closed, P.amber]);
      map.setPaintProperty('risk', 'line-color', ['match', ['get', 'rk'], 'Extreme', css('--rx'), 'High', css('--rh'), 'Medium', css('--rm'), css('--rl')]);
    }
    map.triggerRepaint();
    drawChart();
  }
  document.querySelectorAll('#basemaps button').forEach(function (x) {
    x.addEventListener('click', function () { bm = x.dataset.bm; store('mfw-basemap', bm); applyTheme(); });
  });
  (function () { // legend ramps that do not depend on the basemap
    var stops = [1, 3, 8, 15, 30, 50, 80, 120].map(function (mm, i, a) { var c = rainColor(mm); return 'rgba(' + c.slice(0, 3).map(Math.round).join(',') + ',' + Math.min(1, c[3] + 0.2) + ') ' + Math.round(100 * i / (a.length - 1)) + '%'; });
    $('rainRamp').style.background = 'linear-gradient(90deg,' + stops.join(',') + ')';
  })();
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

  // ---------- timeline: input rain, output closures, check against a river gauge ----------
  function drawChart() {
    if (!meta) return;
    var svg = $('chart'), W = nf - 1, r = meta.rain_hourly_mean_mm || [], cp = meta.closed_per_frame || [];
    var bands = Array.prototype.filter.call(document.querySelectorAll('#timeline .band'), function (b) { return !b.hidden; });
    var BH = (bands[0] && bands[0].offsetHeight) || 30, H = BH * bands.length, s = '', per = 60 / meta.frame_min, y0;
    bands.forEach(function (b, k) {
      y0 = k * BH;
      var kind = b.dataset.band;
      if (k) s += '<line x1="0" x2="' + W + '" y1="' + y0 + '" y2="' + y0 + '" stroke="' + css('--rule') + '" stroke-width="1" vector-effect="non-scaling-stroke"/>';
      if (kind === 'rain') {
        var rmax = Math.max.apply(0, r.concat([1])), hours = Math.floor(W / per);
        for (var i = 0; i < Math.min(r.length, hours); i++) {
          var bh = (BH - 12) * r[i] / rmax;
          s += '<rect x="' + (i * per + 0.06 * per) + '" y="' + (y0 + BH - bh) + '" width="' + (per * 0.88) + '" height="' + bh + '" fill="' + css('--rain') + '"/>';
        }
      } else if (kind === 'closed') {
        var cmax = Math.max.apply(0, cp.concat([1]));
        var pts = cp.map(function (v, i) { return i + ',' + (y0 + BH - 1 - (BH - 13) * v / cmax).toFixed(2); });
        s += '<polygon points="0,' + (y0 + BH) + ' ' + pts.join(' ') + ' ' + (cp.length - 1) + ',' + (y0 + BH) + '" fill="' + css('--closed') + '" fill-opacity=".16"/>';
        s += '<polyline points="' + pts.join(' ') + '" fill="none" stroke="' + css('--closed') + '" stroke-width="1.6" vector-effect="non-scaling-stroke" stroke-linejoin="round"/>';
      } else if (kind === 'gauge' && refs) {
        var g = refs.gauges[+$('gaugeSel').value]; if (!g) return;
        var vals = (g.obs_q || []).concat(g.model_q || []).filter(function (v) { return v != null; }), gm = Math.max.apply(0, vals.concat([1]));
        var line = function (a, col, dash) {
          var seg = [], out = '';
          a.forEach(function (v, i) { if (v == null) { if (seg.length) { out += pl(seg); seg = []; } return; } seg.push(i + ',' + (y0 + BH - 1 - (BH - 13) * v / gm).toFixed(2)); });
          if (seg.length) out += pl(seg);
          function pl(sg) { return '<polyline points="' + sg.join(' ') + '" fill="none" stroke="' + col + '" stroke-width="1.6" ' + (dash ? 'stroke-dasharray="4 3" ' : '') + 'vector-effect="non-scaling-stroke"/>'; }
          return out;
        };
        if (g.obs_q) s += line(g.obs_q, css('--obs'), false);
        if (g.model_q) s += line(g.model_q, css('--mod'), true);
        $('modKey').hidden = $('modLabel').hidden = !g.model_q;
        if (!g.model_q && g.model_peak_utc) { // the modelled peak time, when the flow series is not published
          var fx = (new Date(g.model_peak_utc.replace(/Z$/, ':00Z')) - t0) / 60000 / meta.frame_min;
          if (fx >= 0 && fx <= W) s += '<line x1="' + fx + '" x2="' + fx + '" y1="' + (y0 + 10) + '" y2="' + (y0 + BH) + '" stroke="' + css('--mod') + '" stroke-width="2" stroke-dasharray="3 2" vector-effect="non-scaling-stroke"/>';
          $('modKey').hidden = $('modLabel').hidden = false; $('modLabel').textContent = 'modelled peak';
        } else $('modLabel').textContent = 'modelled';
      }
    });
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.style.height = H + 'px';
    svg.innerHTML = s;
    setCursor();
  }
  $('gaugeSel').addEventListener('change', drawChart);
  function setCursor() { var c = $('cursor'); if (c && nf > 1) c.style.left = (100 * t / (nf - 1)) + '%'; }

  var lastClock = '';
  function setTime(v) {
    t = Math.max(0, Math.min(nf - 1, v));
    var fa = Math.min(Math.floor(t), nf - 1), fr = t - fa, closed = 0;
    for (var i = 0; i < segs.length; i++) {
      var s = segs[i], d = s.d, val;
      if (d) {
        var a = d[fa] || 0, b = d[fa + 1] || 0;
        val = a + (b - a) * fr;
      } else { // no depth series: ramp up over the hour before each closure and drain over the hour after
        val = 0;
        for (var j = 0; j < s.iv.length; j++) {
          var lead = 60 / meta.frame_min, x0 = s.iv[j][0], x1 = s.iv[j][1];
          var u = t < x0 ? 1 - (x0 - t) / lead : t > x1 ? 1 - (t - x1) / lead : 1;
          val = Math.max(val, u > 0 ? (t >= x0 && t <= x1 ? 40 : 30 * u) : 0);
        }
      }
      if (val >= 30) closed++;
      var q = val < 2 ? 0 : 2 * Math.round(val / 2);
      if (q !== s.v) { s.v = q; map.setFeatureState({ source: 'roads', id: s.id }, { d: q }); }
    }
    var mins = Math.round(t * meta.frame_min / 5) * 5, label = fmtClock.format(new Date(t0.getTime() + mins * 60000));
    if (label !== lastClock) {
      lastClock = label;
      $('clock').textContent = label;
      $('since').textContent = (mins / 60).toFixed(1) + ' h after the replay starts';
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
    followTick(false);
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
      if (follow) followTick(true);
      requestAnimationFrame(tick);
    }
  }
  $('play').addEventListener('click', function () { if (ready) setPlaying(!playing); });
  document.querySelectorAll('.speeds button').forEach(function (b0) {
    b0.addEventListener('click', function () {
      var b = b0;
      if (small() && b.getAttribute('aria-pressed') === 'true') { // phones show one speed button that cycles
        var all = Array.prototype.slice.call(document.querySelectorAll('.speeds button')); b = all[(all.indexOf(b) + 1) % all.length];
      }
      speed = +b.dataset.speed;
      document.querySelectorAll('.speeds button').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    });
  });
  $('scrub').addEventListener('input', function (e) { if (!ready) return; if (playing) setPlaying(false); played = true; setTime(+e.target.value); });
  document.addEventListener('keydown', function (e) {
    if (e.key === ' ' && e.target === document.body && ready) { e.preventDefault(); setPlaying(!playing); }
  });

  // ---------- layer toggles ----------
  function vis(id, on) { if (map && map.getLayer(id)) map.setLayoutProperty(id, 'visibility', on ? 'visible' : 'none'); }
  $('lyRain').addEventListener('change', function (e) { vis('rain', e.target.checked); });
  $('lyDepth').addEventListener('change', function (e) { vis('depth', e.target.checked); });
  $('lyFlow').addEventListener('change', function (e) { vis('flow', e.target.checked); $('flowKey').hidden = !e.target.checked; });
  $('lyClosed').addEventListener('change', function (e) { ['wet', 'wetcase', 'halo'].forEach(function (l) { vis(l, e.target.checked); }); });
  $('lyPeak').addEventListener('change', function (e) { vis('peak', e.target.checked); });
  $('lyMay').addEventListener('change', function (e) { vis('may', e.target.checked); });
  $('lyRisk').addEventListener('change', function (e) {
    var on = e.target.checked;
    vis('risk', on); $('riskKey').hidden = !on;
    $('lyPeak').checked = !on; vis('peak', !on);
    $('lyMay').checked = !on; vis('may', !on);
  });
  document.querySelectorAll('input[data-ref]').forEach(function (x) { x.addEventListener('change', function () { vis('r-' + x.dataset.ref, x.checked); }); });
  var pl = document.querySelector('.player');
  function ph() { document.documentElement.style.setProperty('--player-h', pl.offsetHeight + 'px'); }
  if (window.ResizeObserver) new ResizeObserver(ph).observe(pl); ph();
  var lg = $('legend');
  if (small()) { lg.dataset.collapsed = 'true'; $('legendToggle').setAttribute('aria-expanded', 'false'); }
  $('legendToggle').addEventListener('click', function () {
    var c = lg.dataset.collapsed === 'true';
    lg.dataset.collapsed = c ? 'false' : 'true';
    this.setAttribute('aria-expanded', c ? 'true' : 'false');
  });
  var rz = 0;
  window.addEventListener('resize', function () { clearTimeout(rz); rz = setTimeout(function () { if (!userMoved && !follow && views.length) fitView(currentView, false); }, 200); });
})();
