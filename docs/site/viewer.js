/* Mass Flood Watch storm replay.
   GPU layers (custom WebGL, one draw each per animation frame):
     depth  all frames decoded once into textures (9 frames per texture, depth class packed base 5 in RGB), interpolated in time
            and, after decoding, bilinearly in space with a soft edge at the wet/dry cell boundary
     rain   MRMS radar rain, every frame in one atlas texture (3 frames per cell, log-scaled mm/h), filtered in space and time
     flow   (5-min runs only) moving water surface: a ripple texture advected along the modelled velocity field (flow-map),
            masked to wet cells and faded by depth and speed; frozen still when the replay is paused
   Roads: depth on each segment per frame (cm) is interpolated in time and written to feature-state only when it changes,
   so a road turns grey -> amber -> red as the water rises and fades back as it drains.
   Base roads: the whole street network from OpenStreetMap vector tiles (OpenFreeMap, no key), drawn over a muted
   grey basemap and under the water, widths by road class and zoom, so streets read from district to street zoom.
   Story: opening a replay plays six short scenes on the real timeline (storm arrives, rain intensifies, water
   collects, streets flood, streets close, knock-on effects), then hands the map over for free exploration.
   Framing: the camera opens on where roads close, with one-click hotspot views and an optional 'follow the storm'. */
(function () {
  'use strict';
  var RUNS = {
    leominster_sep2023: {
      title: 'Leominster · Sept 11, 2023',
      kind: 'Tuned case. 20 × 20 km box at 20 m, the storm the model settings were checked against.'
    },
    worcester_aug2021: {
      title: 'Worcester · Aug 19, 2021',
      kind: 'Blind test. Same model settings as Leominster, run on a storm it was not tuned on.'
    },
    d3_sep2023: {
      title: 'District 3 · Sept 11, 2023',
      kind: 'One GPU run on WPI’s Turing cluster: 17.6 million cells at 20 m (shown here at 80 m).'
    },
    whatif: {
      title: 'What if? · Leominster storm',
      kind: 'The real storm, rerun by the flood model with heavier or lighter rain, wetter or frozen ground, and blocked culverts.'
    },
    forecast: { title: 'Live forecast · District 3', kind: '' }
  };
  var D3_BOUNDS = [[-72.38, 41.95], [-71.43, 42.765]];
  var params = new URLSearchParams(location.search);
  var runKey = RUNS[params.get('run')] ? params.get('run') : /^[a-z0-9_]{3,60}$/.test(params.get('run') || '') ? params.get('run') : 'leominster_sep2023';
  if (!RUNS[runKey]) RUNS[runKey] = { title: runKey.replace(/_/g, ' '), kind: '' }; // any other published run folder, e.g. a 5-minute rerun
  var base = 'site/data/' + runKey + '/';
  var WHATIF = runKey === 'whatif', WI = 'site/data/whatif/', wi = null, WION = false; // WION: the scenario runs are published
  if (WHATIF) {
    base = 'site/data/leominster_sep2023/'; // rain, gauges, dams and facilities of the same box
    document.documentElement.classList.add('whatif');
  }
  var REPLAY = runKey !== 'forecast'; // replays (and what-if) get the night water basemap: hillshade, vector water, streets and names
  // light by default (dark maps read worst in daylight); the dark theme follows the system setting or the stored choice
  var $ = function (id) { return document.getElementById(id); };
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var small = function () { return window.innerWidth < 720; };

  document.querySelectorAll('.runs a').forEach(function (a) {
    var on = a.dataset.run === runKey;
    a.setAttribute('aria-current', on ? 'true' : 'false');
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
  var BASEMAPS = REPLAY ? { // replays: a vector basemap (OpenFreeMap / OpenMapTiles) drawn by this page: muted land, every street with its
    // name, water in pale grey-blue; 'night' is kept as an alias of dark for stored choices and links
    streets: { layers: {} },
    terrain: { layers: { 'b-hill': 0.5 } },
    satellite: { layers: { 'b-sat': 1 } },
    dark: { layers: { 'b-hshade': 1 } },
    night: { layers: { 'b-hshade': 1 } }
  } : {
    streets: { layers: { 'b-lgt': 1, 'l-voy': 1 } },
    terrain: { layers: { 'b-hill': 1, 'b-lgt': 0.5, 'l-voy': 1 } },
    satellite: { layers: { 'b-sat': 1, 'l-dark': 1 } },
    dark: { layers: { 'b-dark': 1, 'l-dark': 1 } },
    night: { layers: { 'b-dark': 1, 'l-dark': 1 } }
  };
  // depth ramp (5, 15, 30, 100 cm), roads: wet (amber) -> closed (red), casing under them, footprint of closures, may close
  // base road network (net): line colour per class [highway, arterial, collector, local], the white street fill at
  // street zoom, and how strongly it shows. Blue water / amber-red roads stay distinguishable with red-green colour
  // blindness: water and road status sit on the blue-yellow axis, and closed roads add stripes, not just hue.
  var PAL = {
    light: { d: ['rgba(158,202,225,.78)', 'rgba(107,174,214,.82)', 'rgba(33,113,181,.86)', 'rgba(8,48,107,.9)'], // ColorBrewer Blues, single hue: lighter = shallower
      grey: '#8a959e', amber: '#E69F00', orange: '#D55E00', closed: '#7A0019', cas: '#FFFFFF', casDark: '#1F2328', peak: '#7A0019', peakOp: 0.45, may: '#D55E00', halo: '#7A0019',
      net: ['#7C7C77', '#878782', '#9A9A95', '#A4A49F'], fill: '#ffffff', netOp: 1, box: '#5F6368' }, // streets readable from z11
    satellite: { d: ['rgba(198,219,239,.82)', 'rgba(107,174,214,.86)', 'rgba(33,113,181,.9)', 'rgba(8,48,107,.92)'],
      grey: '#c9d1d6', amber: '#F5B400', orange: '#FF8A3D', closed: '#FF5C6C', cas: 'rgba(20,20,20,.85)', casDark: 'rgba(20,20,20,.85)', peak: '#ff8fa0', peakOp: 0.8, may: '#ffb020', halo: '#ff4060',
      net: ['rgba(255,255,255,.9)', 'rgba(255,255,255,.75)', 'rgba(255,255,255,.55)', 'rgba(255,255,255,.45)'], fill: 'rgba(30,30,30,.35)', netOp: 0.85, box: '#ffffff' },
    dark: { d: ['rgba(212,236,244,.85)', 'rgba(151,203,228,.85)', 'rgba(100,166,214,.85)', 'rgba(69,128,194,.85)'],
      grey: '#8796a3', amber: '#F5B400', orange: '#FF8A3D', closed: '#FF5C6C', cas: '#1E2124', casDark: '#1E2124', peak: '#FF5C6C', peakOp: 0.55, may: '#FF8A3D', halo: '#FF5C6C',
      net: ['#7d848c', '#646a72', '#50565d', '#474c53'], fill: '#2f3439', netOp: 1, box: '#9AA0A6' }
  };
  var BMKEY = WHATIF ? 'mfw-basemap-wi' : 'mfw-basemap', bm = store(BMKEY);
  function basemap() { return BASEMAPS[bm] ? (bm === 'night' ? 'dark' : bm) : (isDark() ? 'dark' : 'streets'); }
  function pal() { var b = basemap(); return b === 'satellite' ? PAL.satellite : b === 'dark' || b === 'night' ? PAL.dark : PAL.light; }

  // ---------- state ----------
  var meta, map, nf = 1, t = 0, playing = false, played = false, speed = 2, last = 0;
  var flowRGB = { hi: [0.216, 0.278, 0.31], dk: 0.2 }; // flow lines: blue-grey #37474F on light maps, pale on dark and satellite
  var segs = [], segById = {}, ready = false, popup = null, hover = null, refs = null, rain = null, flowInfo = null, cascade = null;
  var nWet = 0, nClosedNow = 0, sparkRange = [0, 1], rtip = null, rtipId = null, rtipLL = null;
  var fmtClock = new Intl.DateTimeFormat('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York', timeZoneName: 'short' });
  var fmtCap = new Intl.DateTimeFormat('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York' });
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
    var gl, prog, buf, loc = {}, tex = [], queue = [], ramp = null, drnCol = new Float32Array([0.48, 0.54, 0.6, 0.7]);
    var VS = 'attribute vec2 aPos;attribute vec2 aUv;uniform mat4 uM;varying vec2 vUv;' +
      'void main(){vUv=aUv;gl_Position=uM*vec4(aPos,0.0,1.0);}';
    var FS = 'precision highp float;varying vec2 vUv;uniform sampler2D uA;uniform sampler2D uB;' +
      'uniform vec3 uMa;uniform vec3 uMb;uniform float uDa;uniform float uDb;uniform float uT;uniform vec4 uC[4];' +
      'uniform vec2 uS;uniform sampler2D uR;uniform vec3 uMr;uniform float uDr;uniform float uHasR;uniform vec4 uDrn;' +
      // classes are decoded per cell first (base-5 digits cannot be filtered), then interpolated: bilinear between the
      // four nearest cell centres. A wet cell next to a dry one reads 0.5 exactly on their shared edge, so the soft
      // threshold at 0.5 keeps the water edge on the cell boundary (never more than half a cell onto dry ground)
      'float code(sampler2D s,vec3 m,float d,vec2 uv){float x=floor(dot(texture2D(s,uv).rgb,m)*255.0+0.5);return mod(floor(x/d+0.001),5.0);}' +
      // classes decoded per cell, then bilinear between cell centres with a soft threshold at 0.5: smooth water edges that stay on
      // the cell boundary (never more than half a cell onto dry ground); isolated shallow cells are removed in the pack (despeckle)
      'float cls(sampler2D s,vec3 m,float d){vec2 p=vUv*uS-0.5;vec2 i=floor(p);vec2 f=p-i;vec2 c=(i+0.5)/uS;vec2 dx=vec2(1.0/uS.x,0.0);vec2 dy=vec2(0.0,1.0/uS.y);' +
      'return mix(mix(code(s,m,d,c),code(s,m,d,c+dx),f.x),mix(code(s,m,d,c+dy),code(s,m,d,c+dx+dy),f.x),f.y);}' +
      'vec4 ramp(float L){if(L<=2.0)return mix(uC[0],uC[1],L-1.0);' +
      'if(L<=3.0)return mix(uC[1],uC[2],L-2.0);return mix(uC[2],uC[3],L-3.0);}' +
      'void main(){float L=mix(cls(uA,uMa,uDa),cls(uB,uMb,uDb),uT);float e=smoothstep(0.38,0.62,L);if(e<0.004)discard;' +
      // drying: where the depth class an hour earlier was higher the water is going down (draining or soaking in): it cools to
      // slate and thins out, so receding water reads as receding
      'vec4 c=ramp(max(L,1.0));if(uHasR>0.5){float dr=smoothstep(0.35,1.2,cls(uR,uMr,uDr)-L);c=vec4(mix(c.rgb,uDrn.rgb,dr*0.7),c.a*mix(1.0,uDrn.a,dr));}' +
      'c.a*=e;gl_FragColor=vec4(c.rgb*c.a,c.a);}';
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
          ['uM', 'uA', 'uB', 'uMa', 'uMb', 'uDa', 'uDb', 'uT', 'uC', 'uS', 'uR', 'uMr', 'uDr', 'uHasR', 'uDrn'].forEach(function (k) { loc[k] = gl.getUniformLocation(prog, k); });
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
          var R = slot(Math.max(0, fa - Math.round(60 / meta.frame_min))); // an hour earlier
          if (R.tex && fa > 0) { gl.activeTexture(gl.TEXTURE2); gl.bindTexture(gl.TEXTURE_2D, R.tex); gl.uniform1i(loc.uR, 2); gl.uniform3fv(loc.uMr, R.m); gl.uniform1f(loc.uDr, R.d); gl.uniform1f(loc.uHasR, 1); }
          else gl.uniform1f(loc.uHasR, 0);
          gl.uniform4fv(loc.uDrn, drnCol);
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
      setDrain: function (c) { drnCol = new Float32Array(c); },
      // the two depth frames around t, for the flow layer's wet mask (null until both are on the GPU)
      frames: function () {
        var fa = Math.min(Math.floor(t), nf - 1), fb = Math.min(fa + 1, nf - 1), A = slot(fa), B = slot(fb);
        return A.tex && B.tex ? { A: A, B: B, ft: fb === fa ? 0 : t - fa } : null;
      }
    };
  })();

  // ---------- rain layer (radar loop) ----------
  // Radar rain rate, MRMS. Stepped classes at standard rain-intensity breaks (light < 2.5 mm/h, moderate 2.5-10, heavy 10-25,
  // very heavy 25-50, violent 50+; AMS / MANOBS / ICAO), single-hue ColorBrewer Purples: a lightness ramp that is colour-blind safe and
  // stays clear of the blue water and the amber-red roads. The 1 km field is interpolated in space and between radar frames, then classed,
  // so class edges are smooth contours rather than 1 km blocks. Below 0.5 mm/h nothing is drawn.
  var RAIN_CLASSES = [[0.5, [188, 189, 220], 'light'], [2.5, [158, 154, 200], 'moderate'], [10, [128, 125, 186], 'heavy'],
    [25, [106, 81, 163], 'very heavy'], [50, [63, 0, 125], 'violent']];
  var RAIN_ALPHA = 0.5;
  function rainColor(mm) {
    var c = null; for (var i = 0; i < RAIN_CLASSES.length; i++) if (mm >= RAIN_CLASSES[i][0]) c = RAIN_CLASSES[i];
    return c ? c[1].concat([RAIN_ALPHA]) : [0, 0, 0, 0];
  }
  var rainOp = 1; // story fades the radar back once the rain has done its work
  var rainLayer = (function () {
    var gl, prog, buf, loc = {}, tex = null, lut = null, pending = null, K = 1;
    var VS = 'attribute vec2 aPos;uniform mat4 uM;varying vec2 vM;void main(){vM=aPos;gl_Position=uM*vec4(aPos,0.0,1.0);}';
    // vM is Web Mercator (0..1); the radar grid is regular in lat/lon, so the row is found from latitude, not mercator y
    var FS = 'precision highp float;varying vec2 vM;uniform sampler2D uS;uniform sampler2D uL;uniform vec4 uB;' +
      'uniform vec2 uCa;uniform vec2 uCb;uniform vec3 uMa;uniform vec3 uMb;uniform vec2 uCell;uniform vec2 uHalf;uniform float uT;uniform float uOp;uniform float uK;uniform float uLm;' +
      'void main(){float lon=vM.x*360.0-180.0;float yy=3.14159265*(1.0-2.0*vM.y);float lat=degrees(atan((exp(yy)-exp(-yy))*0.5));' +
      'vec2 uv=vec2((lon-uB.x)/(uB.z-uB.x),(uB.w-lat)/(uB.w-uB.y));if(uv.x<0.0||uv.x>1.0||uv.y<0.0||uv.y>1.0)discard;' +
      'vec2 c=clamp(uv*uCell,uHalf,uCell-uHalf);float a=dot(texture2D(uS,uCa+c).rgb,uMa);float b=dot(texture2D(uS,uCb+c).rgb,uMb);' +
      'float v=mix(a,b,uT);if(uK!=1.0){v=min(1.0,log(1.0+(exp(v*uLm)-1.0)*uK)/uLm);}if(v<0.03)discard;vec4 k=texture2D(uL,vec2(v,0.5));float al=k.a*uOp;' +
      'float e=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));al*=smoothstep(0.0,0.06,e);gl_FragColor=vec4(k.rgb*al,al);}';
    return {
      layer: {
        id: 'rain', type: 'custom', renderingMode: '2d',
        onAdd: function (m, g) {
          gl = g; prog = program(gl, VS, FS);
          loc.aPos = gl.getAttribLocation(prog, 'aPos');
          ['uM', 'uS', 'uL', 'uB', 'uCa', 'uCb', 'uMa', 'uMb', 'uCell', 'uHalf', 'uT', 'uOp', 'uK', 'uLm'].forEach(function (k) { loc[k] = gl.getUniformLocation(prog, k); });
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
          gl.uniform1f(loc.uT, pos - fa); gl.uniform1f(loc.uOp, rainOp); gl.uniform1f(loc.uK, K); gl.uniform1f(loc.uLm, Math.log1p(R.max_mmh));
          gl.bindBuffer(gl.ARRAY_BUFFER, buf);
          gl.enableVertexAttribArray(loc.aPos); gl.vertexAttribPointer(loc.aPos, 2, gl.FLOAT, false, 8, 0);
          gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
          gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
          gl.disableVertexAttribArray(loc.aPos);
          gl.activeTexture(gl.TEXTURE0);
        }
      },
      set: function (img) { pending = img; },
      scale: function (k) { K = k; if (map) map.triggerRepaint(); } // what-if: the radar rain as scaled in the run
    };
  })();

  // ---------- flow layer: the modelled current as evenly spaced streamlines ----------
  // flow.json + flow sheet(s): the water velocity of each block (60 m from the solver's own .Vx/.Vy, or 100 m from the water-surface slope
  // on older runs) per frame: east / north speed and the wet share of the block.
  // Drawing (Jobard & Lefer 1997 evenly spaced streamlines; Laidlaw et al. 2005 found streamlines read direction better than arrows or LIC):
  //   street zoom (15+): thin blue-grey streamlines about 24 px apart, traced through the field in both directions from seeds, only on water
  //     the map shows (5 cm+), where the current is at least 0.1 m/s. Opacity steps with speed (0.25 / 0.5 / 1 / 2 m/s, EA speed bands).
  //     A short dash slides along each line at 30 px per second per m/s: direction and relative speed, not to time scale.
  //   closer than town zoom (13.4-15): a static arrow at block centres, length proportional to speed (capped at 2 m/s), so the
  //     coarseness of the field is visible.
  // Recomputed when the view settles or the field moves on by half a frame; nothing moves with prefers-reduced-motion.
  var mapMoving = false;
  var flowLayer = (function () {
    var gl, prog, buf, loc = {}, F = null, DIR = '', SH = {}, SHL = {}, n_ = 0, verts = null, nv = 0, built = null, t0 = performance.now(), mode = 0;
    var VS = 'attribute vec2 aPos;attribute vec2 aD;uniform mat4 uM;varying vec2 vD;void main(){vD=aD;gl_Position=uM*vec4(aPos,0.0,1.0);}';
    // aD = (alpha, tau). tau < 0: no dash (arrows). Dash: 25 % of a 1.6 s period, smooth edges; the line itself at 45 % of the dash.
    var FS = 'precision mediump float;varying vec2 vD;uniform vec3 uC;uniform float uT;uniform float uF;void main(){float a=vD.x*uF;' +
      'if(vD.y>=0.0){float d=fract((vD.y-uT)/1.6);float k=smoothstep(0.0,0.05,d)*(1.0-smoothstep(0.2,0.3,d));a*=0.55+0.45*k;}' +
      'gl_FragColor=vec4(uC*a,a);}';
    var SPEED_A = [[0.1, 0.35], [0.25, 0.5], [0.5, 0.65], [1, 0.8], [2, 0.95]];
    function alphaFor(v) { var a = 0; for (var i = 0; i < SPEED_A.length; i++) if (v >= SPEED_A[i][0]) a = SPEED_A[i][1]; return a; }
    function sheetOf(f) { var per = F.per_sheet || F.n; return Math.floor(f / per); }
    function need(si) {
      if (SH[si] || SHL[si] || !F.sheets || si >= F.sheets.length) return;
      SHL[si] = 1;
      getBitmap(DIR + F.sheets[si]).then(function (img) { SH[si] = pix(img); delete SHL[si]; built = null; if (map) map.triggerRepaint(); })
        .catch(function () { delete SHL[si]; });
    }
    function pix(img) {
      var cv = document.createElement('canvas'); cv.width = img.width; cv.height = img.height;
      var cx = cv.getContext('2d', { willReadFrequently: true }); cx.drawImage(img, 0, 0); if (img.close) img.close();
      return { d: cx.getImageData(0, 0, cv.width, cv.height).data, w: cv.width };
    }
    function texel(f, x, y, o, wt) { // one block of frame f, decoded to m/s, added into o with weight wt x wet share
      var S = SH[sheetOf(f)]; if (!S) return;
      var li = f % (F.per_sheet || F.n), cx = li % F.cols, cy = Math.floor(li / F.cols);
      x = Math.max(0, Math.min(F.w - 1, x)); y = Math.max(0, Math.min(F.h - 1, y));
      var i = ((cy * F.h + y) * S.w + cx * F.w + x) * 4, w = S.d[i + 2] / 255 * wt;
      var ex = (S.d[i] - 128) / 127, ny = (S.d[i + 1] - 128) / 127, ue, vn;
      if (F.enc === 'sqrt') { var m = Math.hypot(ex, ny), sp = m * m * F.vmax_ms; ue = m > 0 ? ex / m * sp : 0; vn = m > 0 ? ny / m * sp : 0; }
      else { ue = ex * F.vmax_ms; vn = ny * F.vmax_ms; }
      o[0] += ue * w; o[1] += vn * w; o[2] += w;
    }
    var acc = [0, 0, 0];
    function vel(f, u, v, out) { // bilinear in space, weighted by wet share -> [east m/s, north m/s, wet share]
      var px = u * F.w - 0.5, py = v * F.h - 0.5, x = Math.floor(px), y = Math.floor(py), fx = px - x, fy = py - y;
      acc[0] = acc[1] = acc[2] = 0;
      texel(f, x, y, acc, (1 - fx) * (1 - fy)); texel(f, x + 1, y, acc, fx * (1 - fy)); texel(f, x, y + 1, acc, (1 - fx) * fy); texel(f, x + 1, y + 1, acc, fx * fy);
      var w = Math.max(acc[2], 1e-3); out[0] = acc[0] / w; out[1] = acc[1] / w; out[2] = acc[2];
    }
    var va = [0, 0, 0], vb = [0, 0, 0], FI = 0;
    function field(u, v, out) { // linear in time between the two flow frames around the replay time
      var f0 = Math.floor(FI), f1 = Math.min(f0 + 1, F.n - 1), k = FI - f0;
      vel(f0, u, v, va); if (!SH[sheetOf(f1)]) { out[0] = va[0]; out[1] = va[1]; out[2] = va[2]; return; }
      vel(f1, u, v, vb);
      out[0] = va[0] + (vb[0] - va[0]) * k; out[1] = va[1] + (vb[1] - va[1]) * k; out[2] = va[2] + (vb[2] - va[2]) * k;
    }
    // drawn-water mask: the depth sheet of the current frame, so lines run only on water the map shows (5 cm and more)
    var SD = null, sdIdx = -1, sdLoading = -1;
    function maskSheet() {
      var k = Math.max(0, Math.min(nf - 1, Math.round(t))), si = Math.floor(k / 9);
      if (si === sdIdx || si === sdLoading || !meta.sheets) return;
      sdLoading = si;
      var url = (WION && wi ? WI + wi.key + '/' : base) + meta.sheets[si];
      getBitmap(url).then(function (img) { var P = pix(img); SD = { d: P.d, w: P.w, h: img.height || (P.d.length / 4 / P.w) }; sdIdx = si; sdLoading = -1; built = null; map.triggerRepaint(); })
        .catch(function () { sdLoading = -1; });
    }
    var CH = null; // mapped streams, rivers and ponds of the box (terrain.png G): the current runs there too, though the depth layer shows the rise
    function chan(u, v) { if (!CH) return false; var x = Math.min(CH.w - 1, Math.max(0, Math.floor(u * CH.w))), y = Math.min(CH.h - 1, Math.max(0, Math.floor(v * CH.h))); return CH.d[(y * CH.w + x) * 4 + 1] > 128; }
    function drawn(u, v) {
      if (chan(u, v)) return true;
      if (!SD) return false;
      var k = Math.max(0, Math.min(nf - 1, Math.round(t))); if (Math.floor(k / 9) !== sdIdx) return true;
      var j = k % 9, x = Math.min(SD.w - 1, Math.max(0, Math.floor(u * SD.w))), y = Math.min(SD.h - 1, Math.max(0, Math.floor(v * SD.h)));
      return Math.floor(SD.d[(y * SD.w + x) * 4 + Math.floor(j / 3)] / [1, 5, 25][j % 3]) % 5 >= 1;
    }
    // screen <-> box uv: the box is a near-parallelogram on screen (20 km of Web Mercator), so an affine map from three corners is exact to
    // well under a pixel; east and north on screen come from the same corners, so a rotated map stays right
    var Ax = null;
    function frame() {
      var P = F.corners.map(function (c) { return map.project(c); });
      var ux = P[1].x - P[0].x, uy = P[1].y - P[0].y, vx = P[3].x - P[0].x, vy = P[3].y - P[0].y, det = ux * vy - uy * vx;
      var lu = Math.hypot(ux, uy), lv = Math.hypot(vx, vy);
      Ax = { ox: P[0].x, oy: P[0].y, ux: ux, uy: uy, vx: vx, vy: vy, det: det, ex: [ux / lu, uy / lu], nx: [-vx / lv, -vy / lv],
             mpp: F.w * F.cell_m / lu };   // metres per screen px
    }
    function toUV(x, y, o) { var dx = x - Ax.ox, dy = y - Ax.oy; o[0] = (dx * Ax.vy - dy * Ax.vx) / Ax.det; o[1] = (Ax.ux * dy - Ax.uy * dx) / Ax.det; }
    var uv = [0, 0], fv = [0, 0, 0];
    function sv(x, y, out) { // screen velocity (px direction, unit) and speed m/s at screen point; false where no moving drawn water
      toUV(x, y, uv); if (uv[0] < 0 || uv[0] > 1 || uv[1] < 0 || uv[1] > 1) return false;
      field(uv[0], uv[1], fv); var s = Math.hypot(fv[0], fv[1]);
      if (fv[2] < 0.3 || s < 0.1 || !drawn(uv[0], uv[1])) return false;
      var dx = fv[0] * Ax.ex[0] + fv[1] * Ax.nx[0], dy = fv[0] * Ax.ex[1] + fv[1] * Ax.nx[1], L = Math.hypot(dx, dy) || 1;
      out[0] = dx / L; out[1] = dy / L; out[2] = s; return true;
    }
    function streamlines(W, H) {
      var dsep = small() ? 28 : 24, dtest = dsep * 0.5, cs = dtest, gw = Math.ceil(W / cs) + 1, gh = Math.ceil(H / cs) + 1;
      var occ = new Int32Array(gw * gh).fill(-1), lines = [], step = 2.5, maxPts = 260, o = [0, 0, 0], o2 = [0, 0, 0];
      function free(x, y, id, r) {
        var gx = Math.floor(x / cs), gy = Math.floor(y / cs);
        for (var j = gy - r; j <= gy + r; j++) for (var i = gx - r; i <= gx + r; i++) {
          if (i < 0 || j < 0 || i >= gw || j >= gh) continue; var q = occ[j * gw + i]; if (q >= 0 && q !== id) return false;
        }
        return true;
      }
      function trace(x, y, dir, id) { // RK2 (midpoint) in screen px
        var pts = [];
        for (var k = 0; k < maxPts; k++) {
          if (!sv(x, y, o)) break;
          var mx = x + dir * o[0] * step * 0.5, my = y + dir * o[1] * step * 0.5;
          if (!sv(mx, my, o2)) break;
          var nx = x + dir * o2[0] * step, ny = y + dir * o2[1] * step;
          if (nx < -20 || ny < -20 || nx > W + 20 || ny > H + 20 || !free(nx, ny, id, 0)) break;
          // stop at a sharp turn (a stagnation point or a flip between frames)
          if (k > 0 && o[0] * o2[0] + o[1] * o2[1] < 0.5) break;
          pts.push([nx, ny, o2[2]]); x = nx; y = ny;
        }
        return pts;
      }
      for (var sy = dsep * 0.5; sy < H; sy += dsep) for (var sx = dsep * 0.5 + ((sy / dsep) % 2) * dsep * 0.5; sx < W; sx += dsep) {
        if (!free(sx, sy, -2, 1) || !sv(sx, sy, o)) continue;
        var id = lines.length, s0 = o[2];
        var fw = trace(sx, sy, 1, id), bw = trace(sx, sy, -1, id);
        var pts = bw.reverse().concat([[sx, sy, s0]], fw);
        if (pts.length < 6) continue;
        pts.forEach(function (p) { var gx = Math.floor(p[0] / cs), gy = Math.floor(p[1] / cs); if (gx >= 0 && gy >= 0 && gx < gw && gy < gh) occ[gy * gw + gx] = id; });
        lines.push(pts);
      }
      return lines;
    }
    function arrows(W, H) { // one arrow per block centre (thinned to >= 30 px apart): [x0, y0, x1, y1, speed]
      var out = [], bpx = F.cell_m / Ax.mpp, k = Math.max(1, Math.ceil(30 / bpx)), o = [0, 0, 0], P = [0, 0];
      for (var by = Math.floor(k / 2); by < F.h; by += k) for (var bx = Math.floor(k / 2); bx < F.w; bx += k) {
        var u = (bx + 0.5) / F.w, v = (by + 0.5) / F.h, x = Ax.ox + u * Ax.ux + v * Ax.vx, y = Ax.oy + u * Ax.uy + v * Ax.vy;
        if (x < -10 || y < -10 || x > W + 10 || y > H + 10 || !sv(x, y, o)) continue;
        var L = Math.max(7, Math.min(o[2], 2) / 2 * Math.min(26, bpx * k * 0.85));
        out.push([x - o[0] * L / 2, y - o[1] * L / 2, x + o[0] * L / 2, y + o[1] * L / 2, o[2]]);
      }
      return out;
    }
    function build() {
      var cv = map.getCanvas(), W = cv.clientWidth, H = cv.clientHeight, z = map.getZoom();
      frame(); mode = z >= 15 ? 1 : 2;
      var segs = [], hw = 0.65; // half width in css px (1.3 px line)
      if (mode === 1) {
        streamlines(W, H).forEach(function (L) {
          var tau = 0, n = L.length;
          for (var i = 0; i < n - 1; i++) {
            var a = L[i], b = L[i + 1], ds = Math.hypot(b[0] - a[0], b[1] - a[1]), ta = tau; tau += ds / (30 * Math.max(0.1, (a[2] + b[2]) / 2));
            var e = Math.min(1, Math.min(i, n - 2 - i) / 5 + 0.15);   // ends fade in and out
            segs.push([a[0], a[1], b[0], b[1], alphaFor(a[2]) * e, alphaFor(b[2]) * e, ta, tau]);
          }
        });
      } else {
        arrows(W, H).forEach(function (A) {
          var al = alphaFor(A[4]), dx = A[2] - A[0], dy = A[3] - A[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L, hl = Math.min(6, L * 0.45);
          segs.push([A[0], A[1], A[2], A[3], al, al, -1, -1]);
          segs.push([A[2], A[3], A[2] - ux * hl - uy * hl * 0.6, A[3] - uy * hl + ux * hl * 0.6, al, al, -1, -1]);
          segs.push([A[2], A[3], A[2] - ux * hl + uy * hl * 0.6, A[3] - uy * hl - ux * hl * 0.6, al, al, -1, -1]);
        });
      }
      var need_ = segs.length * 6 * 4; if (!verts || verts.length < need_) verts = new Float32Array(Math.max(need_, 4096));
      nv = 0;
      // screen -> Web Mercator is affine for a flat (unpitched) map: three reference points give it exactly
      var m0 = maplibregl.MercatorCoordinate.fromLngLat(map.unproject([0, 0])), m1 = maplibregl.MercatorCoordinate.fromLngLat(map.unproject([1000, 0])),
        m2 = maplibregl.MercatorCoordinate.fromLngLat(map.unproject([0, 1000]));
      var ax = (m1.x - m0.x) / 1000, ay = (m1.y - m0.y) / 1000, bx = (m2.x - m0.x) / 1000, by = (m2.y - m0.y) / 1000;
      var M = function (x, y) { return { x: m0.x + ax * x + bx * y, y: m0.y + ay * x + by * y }; };
      segs.forEach(function (s) {
        var dx = s[2] - s[0], dy = s[3] - s[1], L = Math.hypot(dx, dy); if (L < 1e-6) return;
        var nx = -dy / L * hw, ny = dx / L * hw;
        var p = [M(s[0] + nx, s[1] + ny), M(s[0] - nx, s[1] - ny), M(s[2] + nx, s[3] + ny), M(s[2] - nx, s[3] - ny)];
        var q = [[p[0], s[4], s[6]], [p[1], s[4], s[6]], [p[2], s[5], s[7]], [p[1], s[4], s[6]], [p[3], s[5], s[7]], [p[2], s[5], s[7]]];
        q.forEach(function (r) { var o = nv * 4; verts[o] = r[0].x; verts[o + 1] = r[0].y; verts[o + 2] = r[1]; verts[o + 3] = r[2]; nv++; });
      });
      built = { fi: FI, z: z };
    }
    return {
      layer: {
        id: 'flow', type: 'custom', renderingMode: '2d',
        onAdd: function (m, g) {
          gl = g; prog = program(gl, VS, FS);
          loc.aPos = gl.getAttribLocation(prog, 'aPos'); loc.aD = gl.getAttribLocation(prog, 'aD');
          loc.uM = gl.getUniformLocation(prog, 'uM'); loc.uC = gl.getUniformLocation(prog, 'uC'); loc.uT = gl.getUniformLocation(prog, 'uT'); loc.uF = gl.getUniformLocation(prog, 'uF');
          buf = gl.createBuffer();
        },
        render: function (g, matrix) {
          if (!F) return;
          var z = map.getZoom(); if (z < 13.4) return;
          maskSheet(); if (!SD) return;
          FI = Math.max(0, Math.min(F.n - 1, t * meta.frame_min / F.frame_min));
          var f0 = Math.floor(FI); need(sheetOf(f0)); need(sheetOf(Math.min(f0 + 1, F.n - 1))); need(sheetOf(Math.min(f0 + (F.per_sheet || 1), F.n - 1)));
          if (!SH[sheetOf(f0)]) return;
          if (!mapMoving && (!built || Math.abs(built.fi - FI) > 0.5 || (built.z >= 15) !== (z >= 15))) build();
          if (!nv) return;
          var fade = Math.min(1, (z - 13.4) / 0.6);
          gl.useProgram(prog); gl.uniformMatrix4fv(loc.uM, false, matrix);
          gl.uniform3fv(loc.uC, flowRGB.hi);
          gl.uniform1f(loc.uT, reduced ? 0 : (performance.now() - t0) / 1000);
          gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, verts.subarray(0, nv * 4), gl.DYNAMIC_DRAW);
          gl.enableVertexAttribArray(loc.aPos); gl.vertexAttribPointer(loc.aPos, 2, gl.FLOAT, false, 16, 0);
          gl.enableVertexAttribArray(loc.aD); gl.vertexAttribPointer(loc.aD, 2, gl.FLOAT, false, 16, 8);
          gl.uniform1f(loc.uF, fade); gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
          gl.drawArrays(gl.TRIANGLES, 0, nv);
          gl.disableVertexAttribArray(loc.aPos); gl.disableVertexAttribArray(loc.aD);
          if (mode === 1 && !reduced && !document.hidden) map.triggerRepaint();
        }
      },
      stat: function () { return { F: !!F, nv: nv, mode: mode, sheets: Object.keys(SH).length, sd: sdIdx }; },
      set: function (info, image, dir) {
        F = info; F.frame_min = info.frame_min || (meta.nf - 1) * meta.frame_min / Math.max(1, info.n - 1);
        if (!F.sheets) F.sheets = [F.sheet];
        DIR = dir || ''; SH = {}; SHL = {}; built = null; nv = 0;
        if (image) SH[0] = pix(image);
        var k = $('flowKey'); if (k) k.innerHTML = '<div class="fkey"><svg width="34" height="12" viewBox="0 0 34 12" aria-hidden="true"><path d="M1 9 C10 2 22 2 33 6" fill="none" stroke="currentColor" stroke-width="1.3" opacity=".45"/><path d="M14 4.2 L22 3.6" stroke="currentColor" stroke-width="1.6"/></svg>' +
          '<span>Lines follow the modelled current; darker is faster (0.25, 0.5, 1, 2 m/s). Dashes move 30 px a second per m/s: direction and relative speed, not to time scale. ' +
          'Arrows when zoomed out. Source: ' + (/solver/.test(F.method || '') ? 'the flood solver’s own velocity' : 'the modelled water-surface slope') + ', ' + Math.round(F.cell_m) + ' m blocks.</span></div>';
        if (map) map.triggerRepaint();
      },
      reset: function () { built = null; },
      setChannels: function (img) { var P = pix(img); CH = { d: P.d, w: P.w, h: P.d.length / 4 / P.w }; built = null; if (map) map.triggerRepaint(); }
    };
  })();

  // ---------- what-if explorer (?run=whatif): one real storm, rerun with other inputs; every combination a full physics run ----------
  /* docs/site/data/whatif/ (proto/whatif.py pack, from WHATIF runs on Turing):
       index.json   axes, per-scenario numbers and status;  roads.json  every road segment that gets water in any scenario;
       terrain.png  R hillshade of the lidar DEM, G mapped water / channel cells, B elevation;  culverts.json  crossings in the box
       <id>/d.json  depth on each road per 15-min frame, closures, culverts overtopped, numbers;  <id>/depth_NN.png  9 frames per image
                    (base-5 classes; on channels and ponds the class is the rise above the starting level);  <id>/flow.*  30-min velocity
     Until those runs land, the tab shows the live replay of the actual storm (same physics) and marks the other settings as queued. */
  var wdepth = (function () {
    var gl, prog, buf, loc = {}, sets = {}, queue = [], cur = null, prev = null, X = 1, mask = null, maskImg = null;
    var VS = 'attribute vec2 aPos;attribute vec2 aUv;uniform mat4 uM;varying vec2 vUv;void main(){vUv=aUv;gl_Position=uM*vec4(aPos,0.0,1.0);}';
    var FS = 'precision highp float;varying vec2 vUv;uniform sampler2D uA;uniform sampler2D uB;uniform sampler2D uPA;uniform sampler2D uPB;uniform sampler2D uR;uniform sampler2D uK;' +
      'uniform vec3 uMa;uniform vec3 uMb;uniform vec3 uMpa;uniform vec3 uMpb;uniform vec3 uMr;uniform float uDa;uniform float uDb;uniform float uDpa;uniform float uDpb;uniform float uDr;' +
      'uniform float uT;uniform float uX;uniform float uHasK;uniform vec2 uS;uniform vec4 uL[4];uniform vec4 uC[4];uniform vec4 uDrn;' +
      'float code(sampler2D s,vec3 m,float d,vec2 uv){float x=floor(dot(texture2D(s,uv).rgb,m)*255.0+0.5);return mod(floor(x/d+0.001),5.0);}' +
      'float cls(sampler2D s,vec3 m,float d){vec2 p=vUv*uS-0.5;vec2 i=floor(p);vec2 f=p-i;vec2 c=(i+0.5)/uS;vec2 dx=vec2(1.0/uS.x,0.0);vec2 dy=vec2(0.0,1.0/uS.y);' +
      'return mix(mix(code(s,m,d,c),code(s,m,d,c+dx),f.x),mix(code(s,m,d,c+dy),code(s,m,d,c+dx+dy),f.x),f.y);}' +
      'vec4 rmp(vec4 c[4],float L){if(L<=2.0)return mix(c[0],c[1],L-1.0);if(L<=3.0)return mix(c[1],c[2],L-2.0);return mix(c[2],c[3],L-3.0);}' +
      'void main(){float Lc=mix(cls(uA,uMa,uDa),cls(uB,uMb,uDb),uT);float Lp=uX<0.999?mix(cls(uPA,uMpa,uDpa),cls(uPB,uMpb,uDpb),uT):Lc;' +
      'float L=mix(Lp,Lc,uX);float e=smoothstep(0.38,0.62,L);if(e<0.004)discard;' +
      'float k=uHasK>0.5?smoothstep(0.3,0.7,texture2D(uK,vUv).g):0.0;' +
      'vec4 c=mix(rmp(uL,max(L,1.0)),rmp(uC,max(L,1.0)),k);' +
      // draining: the class an hour earlier was higher -> the water is going down: cooler, greyer, a little fainter
      'float dr=smoothstep(0.35,1.2,cls(uR,uMr,uDr)-Lc)*(1.0-k*0.6);c=vec4(mix(c.rgb,uDrn.rgb,dr*0.75),c.a*mix(1.0,uDrn.a,dr));' +
      'c.a*=e;gl_FragColor=vec4(c.rgb*c.a,c.a);}';
    function slot(key, f) {
      var S = sets[key]; if (!S) return null; f = Math.max(0, Math.min(nf - 1, f));
      var k = f % 9, m = [0, 0, 0]; m[Math.floor(k / 3)] = 1;
      return { tex: S.tex[Math.floor(f / 9)], m: m, d: [1, 5, 25][k % 3] };
    }
    function bind(unit, name, s) { gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, s.tex); gl.uniform1i(loc[name], unit); }
    var api = {
      layer: {
        id: 'depth', type: 'custom', renderingMode: '2d',
        onAdd: function (m, g) {
          gl = g; prog = program(gl, VS, FS);
          ['aPos', 'aUv'].forEach(function (k) { loc[k] = gl.getAttribLocation(prog, k); });
          ['uM', 'uA', 'uB', 'uPA', 'uPB', 'uR', 'uK', 'uMa', 'uMb', 'uMpa', 'uMpb', 'uMr', 'uDa', 'uDb', 'uDpa', 'uDpb', 'uDr', 'uT', 'uX', 'uHasK', 'uS', 'uL', 'uC', 'uDrn']
            .forEach(function (k) { loc[k] = gl.getUniformLocation(prog, k); });
          buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, quad(meta.corners), gl.STATIC_DRAW);
        },
        render: function (g, matrix) {
          while (queue.length) { var q = queue.shift(); if (sets[q.key]) sets[q.key].tex[q.i] = texture(gl, q.img, gl.NEAREST); if (q.img.close) q.img.close(); }
          if (maskImg) { mask = texture(gl, maskImg, gl.LINEAR); if (maskImg.close) maskImg.close(); maskImg = null; }
          Object.keys(sets).forEach(function (k) { var S = sets[k]; if (S.drop) { S.tex.forEach(function (tx) { if (tx) gl.deleteTexture(tx); }); delete sets[k]; } });
          var fa = Math.min(Math.floor(t), nf - 1), fb = Math.min(fa + 1, nf - 1), per = 60 / meta.frame_min;
          var A = slot(cur, fa), B = slot(cur, fb), R = slot(cur, Math.round(t - per));
          if (!A || !A.tex || !B.tex || !R.tex) return;
          var useP = X < 0.999 && prev && sets[prev], PA = useP ? slot(prev, fa) : A, PB = useP ? slot(prev, fb) : B;
          if (!PA.tex || !PB.tex) { PA = A; PB = B; }
          gl.useProgram(prog); gl.uniformMatrix4fv(loc.uM, false, matrix);
          bind(0, 'uA', A); bind(1, 'uB', B); bind(2, 'uPA', PA); bind(3, 'uPB', PB); bind(4, 'uR', R);
          gl.activeTexture(gl.TEXTURE5); gl.bindTexture(gl.TEXTURE_2D, mask || A.tex); gl.uniform1i(loc.uK, 5); gl.uniform1f(loc.uHasK, mask ? 1 : 0);
          gl.uniform3fv(loc.uMa, A.m); gl.uniform3fv(loc.uMb, B.m); gl.uniform3fv(loc.uMpa, PA.m); gl.uniform3fv(loc.uMpb, PB.m); gl.uniform3fv(loc.uMr, R.m);
          gl.uniform1f(loc.uDa, A.d); gl.uniform1f(loc.uDb, B.d); gl.uniform1f(loc.uDpa, PA.d); gl.uniform1f(loc.uDpb, PB.d); gl.uniform1f(loc.uDr, R.d);
          gl.uniform1f(loc.uT, fb === fa ? 0 : t - fa); gl.uniform1f(loc.uX, useP ? X : 1); gl.uniform2f(loc.uS, meta.w, meta.h);
          gl.uniform4fv(loc.uL, WPAL.land); gl.uniform4fv(loc.uC, WPAL.chan); gl.uniform4fv(loc.uDrn, WPAL.drain);
          gl.bindBuffer(gl.ARRAY_BUFFER, buf);
          gl.enableVertexAttribArray(loc.aPos); gl.vertexAttribPointer(loc.aPos, 2, gl.FLOAT, false, 16, 0);
          gl.enableVertexAttribArray(loc.aUv); gl.vertexAttribPointer(loc.aUv, 2, gl.FLOAT, false, 16, 8);
          gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
          gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
          gl.disableVertexAttribArray(loc.aPos); gl.disableVertexAttribArray(loc.aUv); gl.activeTexture(gl.TEXTURE0);
        }
      },
      open: function (key, n) { if (!sets[key]) sets[key] = { tex: new Array(n), n: n, used: performance.now() }; sets[key].used = performance.now(); },
      alive: function (key) { return !!sets[key] && !sets[key].drop; },
      has: function (key) { var S = sets[key]; if (!S) return false; for (var i = 0; i < S.n; i++) if (!S.tex[i]) return false; return true; },
      add: function (key, i, img) { queue.push({ key: key, i: i, img: img }); },
      setMask: function (img) { maskImg = img; },
      show: function (key) { if (key === cur) return; prev = cur; cur = key; X = prev ? 0 : 1; api.trim(); },
      fade: function (x) { X = x; },
      trim: function () { // keep at most a few scenarios on the GPU (each is ~22 textures of 1000 x 1000)
        var keep = small() ? 2 : 4, ks = Object.keys(sets).filter(function (k) { return k !== cur && k !== prev && !sets[k].drop; });
        ks.sort(function (a, b) { return sets[a].used - sets[b].used; });
        while (ks.length + 2 > keep && ks.length) sets[ks.shift()].drop = true;
      },
      frames: function () {
        var fa = Math.min(Math.floor(t), nf - 1), fb = Math.min(fa + 1, nf - 1), A = slot(cur, fa), B = slot(cur, fb);
        return A && B && A.tex && B.tex ? { A: A, B: B, ft: fb === fa ? 0 : t - fa } : null;
      }
    };
    return api;
  })();

  // the model's own terrain inside the box: lidar hillshade, slate-toned, under the water (terrain.png from the baseline run)
  var terrainLayer = (function () {
    var gl, prog, buf, loc = {}, tex = null, img = null, corners = null, op = 0;
    var VS = 'attribute vec2 aPos;attribute vec2 aUv;uniform mat4 uM;varying vec2 vUv;void main(){vUv=aUv;gl_Position=uM*vec4(aPos,0.0,1.0);}';
    var FS = 'precision mediump float;varying vec2 vUv;uniform sampler2D uT;uniform vec3 uLo;uniform vec3 uHi;uniform vec3 uW;uniform float uOp;' +
      'void main(){vec3 s=texture2D(uT,vUv).rgb;float h=pow(s.r,1.15);vec3 c=mix(uLo,uHi,h)*(0.92+0.16*s.b);c=mix(c,uW,smoothstep(0.35,0.8,s.g)*0.55);' +
      'float e=min(min(vUv.x,1.0-vUv.x),min(vUv.y,1.0-vUv.y));float a=uOp*smoothstep(0.0,0.025,e);gl_FragColor=vec4(c*a,a);}';
    return {
      layer: {
        id: 'terrain', type: 'custom', renderingMode: '2d',
        onAdd: function (m, g) {
          gl = g; prog = program(gl, VS, FS); loc.aPos = gl.getAttribLocation(prog, 'aPos'); loc.aUv = gl.getAttribLocation(prog, 'aUv');
          ['uM', 'uT', 'uLo', 'uHi', 'uW', 'uOp'].forEach(function (k) { loc[k] = gl.getUniformLocation(prog, k); });
          buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, quad(corners), gl.STATIC_DRAW);
        },
        render: function (g, matrix) {
          if (img) { tex = texture(gl, img, gl.LINEAR); if (img.close) img.close(); img = null; }
          if (!tex || op <= 0) return;
          var P = WPAL.terrain;
          gl.useProgram(prog); gl.uniformMatrix4fv(loc.uM, false, matrix);
          gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tex); gl.uniform1i(loc.uT, 0);
          gl.uniform3fv(loc.uLo, P[0]); gl.uniform3fv(loc.uHi, P[1]); gl.uniform3fv(loc.uW, P[2]); gl.uniform1f(loc.uOp, op);
          gl.bindBuffer(gl.ARRAY_BUFFER, buf);
          gl.enableVertexAttribArray(loc.aPos); gl.vertexAttribPointer(loc.aPos, 2, gl.FLOAT, false, 16, 0);
          gl.enableVertexAttribArray(loc.aUv); gl.vertexAttribPointer(loc.aUv, 2, gl.FLOAT, false, 16, 8);
          gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
          gl.disableVertexAttribArray(loc.aPos); gl.disableVertexAttribArray(loc.aUv);
        }
      },
      set: function (c, image) { corners = c; img = image; },
      opacity: function (v) { op = v; }
    };
  })();

  // water-journey palette (what-if tab): overland water pale aqua -> blue as it deepens; streams, rivers and ponds rising in teal;
  // draining water cools to slate. Roads keep the amber -> red closure ramp, so the four stages never share a hue.
  var WPAL = {
    land: [].concat([0.36, 0.78, 0.86, 0.5], [0.22, 0.6, 0.92, 0.7], [0.2, 0.42, 0.95, 0.84], [0.42, 0.36, 1.0, 0.93]),
    chan: [].concat([0.16, 0.86, 0.76, 0.55], [0.22, 0.95, 0.8, 0.72], [0.55, 1.0, 0.88, 0.86], [0.85, 1.0, 0.95, 0.95]),
    drain: [0.5, 0.58, 0.68, 0.72],
    terrain: [[0.05, 0.08, 0.11], [0.36, 0.42, 0.47], [0.1, 0.32, 0.4]]
  };
  function wpalFor(b) {
    if (b === 'night' || b === 'dark') {
      WPAL.land = [].concat([0.831, 0.925, 0.957, 0.85], [0.592, 0.796, 0.894, 0.85], [0.392, 0.651, 0.839, 0.85], [0.271, 0.502, 0.761, 0.85]);
      WPAL.chan = [].concat([0.16, 0.86, 0.76, 0.55], [0.22, 0.95, 0.8, 0.72], [0.55, 1.0, 0.88, 0.86], [0.85, 1.0, 0.95, 0.95]);
      WPAL.drain = [0.5, 0.58, 0.68, 0.72];
    } else { // light / terrain / satellite
      WPAL.land = [].concat([0.62, 0.792, 0.882, 0.8], [0.42, 0.682, 0.839, 0.84], [0.129, 0.443, 0.71, 0.88], [0.031, 0.188, 0.42, 0.92]);
      WPAL.chan = [].concat([0.0, 0.66, 0.62, 0.55], [0.0, 0.58, 0.55, 0.72], [0.0, 0.48, 0.46, 0.85], [0.0, 0.34, 0.33, 0.94]);
      WPAL.drain = [0.48, 0.54, 0.6, 0.7];
    }
  }

  var WI_TEXT = {
    rain: ['Half the radar rain', 'Three quarters of the radar rain', 'The storm as the radar measured it', 'A quarter more rain than measured'],
    soil: ['Dry ground soaks up more of the rain (the driest soil class)', 'Ground as it was: the model’s calibrated setting',
      'Soaked ground from earlier rain sheds more of it (the wettest soil class)', 'Frozen ground sheds rain like pavement: nothing soaks in (an upper bound)'],
    culv: ['Water passes under roads through culverts and pipes', 'Culverts are full or blocked: road embankments hold water back like dams (bridges stay open)']
  };
  var wiCtl = { rain: ['r050', 'r075', 'r100', 'r125'], soil: ['dry', 'normal', 'wet', 'frozen'], culv: ['open', 'blocked'] };
  function wiKey() { return wiCtl.rain[+$('wiRain').value] + '_' + wiCtl.soil[+$('wiSoil').value] + '_' + wiCtl.culv[+$('wiCulv').value]; }
  function wiScale() { return [0.5, 0.75, 1, 1.25][+$('wiRain').value]; }

  // load one scenario (d.json, depth sheets, flow) -> resolves with its data once every texture is queued
  function wiLoad(key) {
    var dir = WI + key + '/';
    if (wi.cache[key] && wdepth.alive(key)) return wi.cache[key];
    var p = getJson(dir + 'd.json').then(function (dj) {
      wdepth.open(key, dj.sheets.length);
      return Promise.all(dj.sheets.map(function (s, i) { return getBitmap(dir + s).then(function (img) { wdepth.add(key, i, img); if (map) map.triggerRepaint(); }); }))
        .then(function () { return dj; });
    });
    wi.cache[key] = p; p.catch(function () { delete wi.cache[key]; });
    return p;
  }
  function wiIntervals(d) { // closed stretches (>= 30 cm) in frame units, as build_data.intervals
    var out = [], st = null;
    for (var i = 0; i < d.length; i++) {
      var v = d[i];
      if (v >= 30 && st === null) st = i === 0 ? 0 : i - 1 + (30 - d[i - 1]) / Math.max(v - d[i - 1], 1e-6);
      if (v < 30 && st !== null) { out.push([st, i - 1 + (d[i - 1] - 30) / Math.max(d[i - 1] - v, 1e-6)]); st = null; }
    }
    if (st !== null) out.push([st, nf - 0.5]);
    return out;
  }
  // apply a loaded scenario: roads (depth series cross-fade), numbers, chart, flow, culverts, then fade the water
  function wiApply(key, dj, first) {
    wi.key = key; wi.dj = dj; store('mfw-whatif', key);
    meta.closed_per_frame = dj.closed_per_frame; meta.rain_hourly_mean_mm = dj.rain_hourly_mean_mm;
    var N = dj.numbers || {};
    ['segments_closed', 'km_closed', 'segments_may_close', 'culverts_overtopped', 'rain_peak1h_mm', 'rain_max_total_mm', 'segments_in_box'].forEach(function (k) {
      var mk = { segments_closed: 'segments_p_ge_50', km_closed: 'km_p_ge_50', rain_peak1h_mm: 'rain_peak1h_max_mm' }[k] || k; meta[mk] = N[k];
    });
    var may = {}; (dj.may || []).forEach(function (id) { may[id] = 1; });
    segs.forEach(function (s) {
      var d = dj.seg[s.id] || null;
      s.dp = first ? null : (s.d || []); s.d = d || []; s.iv = d ? wiIntervals(d) : []; s.e = (dj.edge && dj.edge[s.id]) || null;
      var pr = s.f.properties; pr.p = dj.p[s.id] || 0; pr.m = may[s.id] ? 1 : 0; pr.d = d; if (s.iv.length) pr.iv = s.iv; else delete pr.iv;
    });
    if (map.getSource('roads')) map.getSource('roads').setData(wi.roads);
    wdepth.show(key);
    if (dj._flow) { flowLayer.set(dj._flow.info, dj._flow.img, WI + key + '/'); dj._flow = null; }
    rainLayer.scale(wiScale());
    wiCulverts();
    wiNumbers(); wiPhases(); drawChart(); if (ready) { instInit(); rankBuild(); }
    if (first) { wdepth.fade(1); wi.x = 1; setTime(t); return; }
    var t0_ = performance.now(), D = reduced ? 1 : 650;
    (function step(now) {
      var x = Math.min(1, (now - t0_) / D); x = x * x * (3 - 2 * x); wi.x = x; wdepth.fade(x); setTime(t);
      if (x < 1) requestAnimationFrame(step); else segs.forEach(function (s) { s.dp = null; });
    })(t0_);
    wiPulse();
  }
  function wiSelect() {
    var key = wiKey(), st = wi.index && wi.index.scenarios[key];
    wiLabels();
    if (!WION) { // before the runs land: the actual storm is the live replay; the rest are queued
      if (key === 'r100_normal_open') { $('wi').classList.remove('pending'); $('wiNote').innerHTML = 'The actual storm, from the live replay. <b>The other combinations are queued on WPI’s Turing GPU cluster</b>: each is a full flood-model run of this storm with one input changed.'; }
      else wiPending(key);
      return;
    }
    if (!st || st.status !== 'ok') { wiPending(key); return; }
    $('wi').classList.remove('pending'); $('wi').classList.add('busy'); $('wiNote').textContent = 'Loading this run…';
    var want = key;
    wiLoad(key).then(function (dj) {
      return getJson(WI + key + '/flow.json').then(function (fi) {   // the bitmap is consumed by the GPU upload: fetch again (HTTP cache) on every switch
        return getBitmap(WI + key + '/' + (fi.sheets ? fi.sheets[0] : fi.sheet)).then(function (img) { dj._flow = { info: fi, img: img }; return dj; });
      }).catch(function () { return dj; });
    }).then(function (dj) {
      if (wiKey() !== want) return;
      // wait until every sheet is on the GPU, so the cross-fade never shows a half-loaded run
      (function wait() { map.triggerRepaint(); if (wdepth.has(want) || !dj.sheets.length) { $('wi').classList.remove('busy'); wiApply(want, dj, false); } else setTimeout(wait, 40); })();
    }).catch(function (e) { console.error('whatif', e); $('wi').classList.remove('busy'); $('wiNote').textContent = 'This run did not load. Try again.'; });
  }
  function wiPending(key) {
    $('wi').classList.add('pending');
    var done = wi.index ? wi.index.n_ok || 0 : 1;
    $('wiNote').innerHTML = '<b>This combination is queued on WPI’s Turing GPU cluster.</b> ' + (wi.index ? done + ' of ' + (wi.index.n || 32) + ' runs are in so far; ' : '') +
      'the map keeps showing the last run that has landed.';
  }
  function wiLabels() {
    $('wiRainV').textContent = ['×0.5', '×0.75', 'actual', '×1.25'][+$('wiRain').value];
    $('wiSoilV').textContent = ['dry', 'normal', 'soaked', 'frozen'][+$('wiSoil').value];
    $('wiCulvV').textContent = ['clear', 'blocked'][+$('wiCulv').value];
    $('wiRainH').textContent = WI_TEXT.rain[+$('wiRain').value];
    $('wiSoilH').textContent = WI_TEXT.soil[+$('wiSoil').value];
    $('wiCulvH').textContent = WI_TEXT.culv[+$('wiCulv').value];
    ['wiRain', 'wiSoil', 'wiCulv'].forEach(function (id) { var e = $(id); e.style.setProperty('--v', (+e.value / +e.max * 100) + '%'); e.setAttribute('aria-valuetext', $(id + 'V').textContent); });
    $('wiCulv').style.setProperty('--b', +$('wiCulv').value ? '#ff5a6e' : '#2fdcc2');
    ['wiSoil', 'wiCulv'].forEach(function (id) {
      var box = $(id).parentNode, tk = box.querySelectorAll('.ticks span');
      Array.prototype.forEach.call(box.querySelectorAll('.seg button'), function (b, i) { b.setAttribute('aria-checked', +b.dataset.v === +$(id).value ? 'true' : 'false'); b.classList.toggle('q', !!(tk[i] && tk[i].classList.contains('q'))); });
    });
    $('wiSoil').style.setProperty('--b', ['#c8a46b', '#8d7a5c', '#4f6b7a', '#bfe6ff'][+$('wiSoil').value]);
    { // ticks whose run is not in yet are marked queued
      var r = +$('wiRain').value, s = +$('wiSoil').value, c = +$('wiCulv').value, S = wi.index ? wi.index.scenarios : { r100_normal_open: { status: 'ok' } };
      var okAt = function (rr, ss, cc) { var v = S[wiCtl.rain[rr] + '_' + wiCtl.soil[ss] + '_' + wiCtl.culv[cc]]; return v && v.status === 'ok'; };
      [['wiRainBox', 4, function (i) { return okAt(i, s, c); }], ['wiSoilBox', 4, function (i) { return okAt(r, i, c); }], ['wiCulvBox', 2, function (i) { return okAt(r, s, i); }]].forEach(function (a) {
        var tk = $(a[0]).querySelectorAll('.ticks span'); for (var i = 0; i < a[1]; i++) tk[i].classList.toggle('q', !a[2](i));
      });
    }
  }
  function wiNumbers() {
    var N = (wi.dj && wi.dj.numbers) || {}, B = wi.index && wi.index.scenarios[wi.index.baseline], base_ = wi.key !== (wi.index && wi.index.baseline) && B && B.status === 'ok' ? B : null;
    var delta = function (v, b) { if (!base_ || v == null || b == null) return ''; var d = v - b; return d === 0 ? ' <i>same as the actual storm</i>' : ' <i>' + (d > 0 ? '+' : '−') + n(Math.abs(d)) + ' vs actual</i>'; };
    $('wiNRain').innerHTML = N.rain_total_mm != null ? Math.round(N.rain_total_mm) + ' mm' + (N.rain_peak1h_mm ? '<i>up to ' + Math.round(N.rain_peak1h_mm) + ' mm in one hour</i>' : '') : '–';
    $('wiNClosed').innerHTML = N.segments_closed != null ? n(N.segments_closed) + (N.pct_closed != null ? '<small>' + N.pct_closed.toFixed(1) + '% of roads</small>' : '') + delta(N.segments_closed, base_ && base_.segments_closed) : '–';
    $('wiNPeople').innerHTML = N.people_cut_off != null ? n(N.people_cut_off) + delta(N.people_cut_off, base_ && base_.people_cut_off) : '–';
    $('wiNCulv').innerHTML = N.culverts_overtopped != null ? n(N.culverts_overtopped) + delta(N.culverts_overtopped, base_ && base_.culverts_overtopped) : '–';
    $('wiNote').innerHTML = 'Each setting is a full LISFLOOD-FP flood-model run of the real storm with that one input changed: ' +
      (wi.index ? wi.index.n_ok + ' runs' : 'runs') + ' on WPI’s Turing GPU cluster, not an extrapolation. People cut off: residents with no route to a hospital, fire or police station.';
    $('runStats').innerHTML = '<b>' + n(N.segments_closed || 0) + '</b> road segments close (' + (N.km_closed || 0) + ' km), <b>' + n(N.culverts_overtopped || 0) +
      '</b> culverts overtopped, out of ' + n(N.segments_in_box || 0) + ' segments in the area.';
  }

  // phases of the water's journey, from the run's own series: rain -> runoff -> streams rise -> streets flood -> draining
  var PH = [], phNow = -1;
  var PHASES = [
    { k: 'rain', name: 'Rain falls', s: 'Radar rain sweeps over the hills' },
    { k: 'runoff', name: 'Runoff', s: 'Rain the ground cannot take runs off over the land' },
    { k: 'chan', name: 'Streams rise', s: 'Brooks, rivers and ponds collect it and swell' },
    { k: 'over', name: 'Streets flood', s: 'Water overflows onto roads; 30 cm closes them' },
    { k: 'drain', name: 'Draining', s: 'Water drains downstream and roads reopen' }
  ];
  function wiPhases() {
    var r = meta.rain_hourly_mean_mm || [], cp = meta.closed_per_frame || [], per = 60 / meta.frame_min, N = nf - 1, dj = wi && wi.dj;
    var rmax = Math.max.apply(0, r.concat([0.001])), cmax = Math.max.apply(0, cp.concat([0])), i;
    var first = function (a, th, from) { for (var k = from || 0; k < a.length; k++) if (a[k] >= th) return k; return -1; };
    var hS = first(r, 0.12 * rmax); var a0 = Math.max(0, (hS < 0 ? 0 : hS) * per - per);
    var wk = dj && dj.wet_km2, ck = dj && dj.channel_rise_km;
    var fRun = wk ? first(wk, 0.12 * Math.max.apply(0, wk)) : -1; if (fRun < 0) fRun = a0 + per;
    var fCh = ck ? first(ck, 0.2 * Math.max.apply(0, ck)) : -1;
    var fOv = first(cp, Math.max(2, 0.1 * cmax), Math.floor(a0)); if (fOv < 0) fOv = Math.min(N, fRun + 2 * per);
    if (fCh < 0) fCh = (fRun + fOv) / 2;
    var fPk = 0; for (i = 0; i < cp.length; i++) if (cp[i] > cp[fPk]) fPk = i;
    var fDr = fPk; while (fDr < N && cp[fDr] >= 0.85 * cmax) fDr++;   // draining: once closures are clearly past their peak
    var b = [a0, Math.max(a0 + 0.4 * per, fRun), 0, 0, 0, N];
    b[2] = Math.max(b[1] + 0.4 * per, fCh); b[3] = Math.max(b[2] + 0.4 * per, Math.min(fOv, fPk)); b[4] = Math.max(b[3] + 0.6 * per, fDr);
    for (i = 1; i < b.length; i++) b[i] = Math.min(N, Math.max(b[i], b[i - 1]));
    PH = PHASES.map(function (p, k) { return { k: p.k, name: p.name, s: p.s, a: b[k], b: b[k + 1] }; });
    var el = $('phases'); el.hidden = false; el.innerHTML = '';
    PH.forEach(function (p, k) {
      var d = document.createElement('button'); d.type = 'button'; d.className = 'ph ph-' + p.k; d.dataset.i = k;
      d.style.left = (100 * p.a / N) + '%'; d.style.width = Math.max(0, 100 * (p.b - p.a) / N) + '%';
      d.innerHTML = '<span>' + esc(p.name) + '</span>'; d.title = p.name + ': ' + p.s + ' (' + fmtShort.format(timeAt(p.a)) + ')';
      d.setAttribute('aria-label', d.title);
      d.addEventListener('click', function () { if (playing) setPlaying(false); played = true; setTime(p.a + 0.01); phaseCaption(true); });
      el.appendChild(d);
    });
    Array.prototype.forEach.call(el.children, function (d) { var sp = d.firstChild; if (sp.scrollWidth > sp.clientWidth + 1) d.classList.add('nl'); });
    var ol = $('phsteps'); ol.hidden = false; ol.innerHTML = '';
    PH.forEach(function (p, k) {
      var li = document.createElement('li'); li.className = 'ps ph-' + p.k;
      li.innerHTML = '<button type="button"><i></i><b>' + esc(p.name) + '</b><span>' + esc(fmtShort.format(timeAt(p.a)).replace(/^[A-Z][a-z]{2} \d+, /, '')) + '</span></button>';
      li.firstChild.addEventListener('click', function () { if (playing) setPlaying(false); played = true; setTime(p.a + 0.01); phaseCaption(true); });
      ol.appendChild(li);
    });
    phNow = -1; phaseCaption();
  }
  function phaseAt(f) { for (var k = PH.length - 1; k >= 0; k--) if (f >= PH[k].a) return k; return -1; }
  var capTimer = 0;
  function phaseCaption(force) {
    if (!PH.length) return;
    var k = phaseAt(t);
    if (k === phNow && !force) return;
    phNow = k;
    [$('phases'), $('phsteps')].forEach(function (el) { Array.prototype.forEach.call(el.children, function (c, j) { c.classList.toggle('on', j === k); c.classList.toggle('past', j < k); }); });
    // the time pill over the map: clock and the phase of the water's journey, with one line of explanation when the phase changes
    var cap = $('caption'); if (story.on) { cap.hidden = true; return; }
    var p = PH[Math.max(0, k)], live = '';
    if (p.k === 'rain' && meta.rain_peak1h_max_mm) live = ' (up to ' + Math.round(meta.rain_peak1h_max_mm) + ' mm in one hour at the wettest spot)';
    $('capT').textContent = k < 0 ? 'Before the storm' : p.name; $('capS').textContent = k < 0 ? '' : p.s + live;
    cap.className = 'caption cap-' + (k < 0 ? 'pre' : p.k); cap.hidden = false; capClock(true);
    cap.classList.toggle('long', playing || !!force);
    clearTimeout(capTimer); capTimer = setTimeout(function () { cap.classList.remove('long'); }, 5200);
  }
  var capLast = '';
  function capClock(force) {
    if (!meta || !t0) return;
    var mins = Math.round(t * meta.frame_min / 5) * 5, s = fmtCap.format(new Date(t0.getTime() + mins * 60000));
    if (s !== capLast || force) { capLast = s; $('capC').textContent = s; }
  }

  // culverts: open (pale ring), overtopped (amber, from the moment the run overtops it), blocked in this scenario (red bar)
  var wiCx = null, wiCxOn = -1;
  function wiCulvertsInit(rows) {
    wiCx = rows.map(function (r, i) { return { type: 'Feature', id: i, properties: { road: r[2], stream: r[3], br: r[4], b: 0 }, geometry: { type: 'Point', coordinates: [r[0], r[1]] } }; });
    map.addSource('wcx', { type: 'geojson', data: { type: 'FeatureCollection', features: wiCx } });
    var st = ['coalesce', ['feature-state', 'o'], 0];
    // culverts from street zoom (z14.5): open white with a grey ring, overtopped dark red, blocked in this run charcoal with a cross
    map.addLayer({ id: 'wcx', type: 'circle', source: 'wcx', filter: ['==', ['get', 'br'], 0], minzoom: 14.5,
      paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 14.5, 5, 16, 7],
        'circle-color': ['case', ['==', ['get', 'b'], 1], '#1F2328', ['==', st, 1], '#7A0019', '#FFFFFF'],
        'circle-stroke-color': ['case', ['==', ['get', 'b'], 1], '#FFFFFF', ['==', st, 1], '#FFFFFF', '#5F6368'],
        'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 11, 1, 15, 1.8], 'circle-opacity': 0.95 } });
    map.addLayer({ id: 'wcx-x', type: 'symbol', source: 'wcx', filter: ['all', ['==', ['get', 'br'], 0], ['==', ['get', 'b'], 1]], minzoom: 14.5,
      layout: { 'text-field': '×', 'text-font': ['Noto Sans Bold'], 'text-size': ['interpolate', ['linear'], ['zoom'], 12.5, 9, 15, 13], 'text-allow-overlap': true, 'text-ignore-placement': true },
      paint: { 'text-color': '#fff' } });
    map.addLayer({ id: 'wcx-lb', type: 'symbol', source: 'wcx', filter: ['all', ['==', ['get', 'br'], 0], ['!=', ['get', 'stream'], '']], minzoom: 14.5,
      layout: { 'text-field': ['concat', 'culvert, ', ['get', 'stream']], 'text-font': ['Noto Sans Italic'], 'text-size': 10.5, 'text-offset': [0, 1.1], 'text-anchor': 'top', 'text-optional': true },
      paint: { 'text-color': '#2F5C80', 'text-halo-color': '#FFFFFF', 'text-halo-width': 1.4 } });
    map.on('mouseenter', 'wcx', function (e) {
      map.getCanvas().style.cursor = 'pointer'; if (small()) return; var p = e.features[0].properties, o = (map.getFeatureState({ source: 'wcx', id: e.features[0].id }) || {}).o;
      if (hover) hover.remove();
      hover = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 10, className: 'tip' }).setLngLat(e.features[0].geometry.coordinates)
        .setHTML('<b>' + esc(p.road || 'Road–stream crossing') + '</b>' + (p.stream ? ' over ' + esc(p.stream) : '') + '<br>' +
          (p.b ? 'Blocked in this run: the road fill holds water back' : o ? 'Overtopped: 15 cm or more of water on the road here' : 'Culvert passing water')).addTo(map);
    });
    map.on('mouseleave', 'wcx', function () { map.getCanvas().style.cursor = ''; if (hover) { hover.remove(); hover = null; } });
    if (wi && wi.dj) wiCulverts();
  }
  function wiCulverts() {
    if (!wiCx || !wi.dj) return;
    var blk = wiCtl.culv[+$('wiCulv').value] === 'blocked' && /_blocked$/.test(wi.key);
    wiCx.forEach(function (f) { f.properties.b = blk ? 1 : 0; });
    map.getSource('wcx').setData({ type: 'FeatureCollection', features: wiCx });
    wi.cxT = {}; (wi.dj.culverts || []).forEach(function (c) { wi.cxT[c[0]] = c[1]; });
    wiCxOn = -1; wiCulvertTime();
  }
  function wiCulvertTime() {
    if (!wiCx || !wi.cxT) return;
    var f = Math.floor(t); if (f === wiCxOn) return; wiCxOn = f;
    wiCx.forEach(function (x, i) { var a = wi.cxT[i], o = a != null && a <= t ? 1 : 0; if (x._o !== o) { x._o = o; map.setFeatureState({ source: 'wcx', id: i }, { o: o }); } });
  }

  // streams and rivers: dashes travel downstream (OpenStreetMap waterways are drawn in the direction of flow) and swell with the run
  var DASH = [[0, 4, 3], [0.5, 4, 2.5], [1, 4, 2], [1.5, 4, 1.5], [2, 4, 1], [2.5, 4, 0.5], [3, 4, 0], [0, 0.5, 3, 3.5], [0, 1, 3, 3], [0, 1.5, 3, 2.5], [0, 2, 3, 2], [0, 2.5, 3, 1.5], [0, 3, 3, 1], [0, 3.5, 3, 0.5]];
  var dashI = 0, dashLast = 0, dashUntil = 0, swellLast = -1;
  function wiPulse() { dashUntil = performance.now() + 6000; requestAnimationFrame(dashTick); }
  function dashTick(now) {
    if (!map || !map.getLayer('h-flow') || reduced) return;
    if (now - dashLast > 85) { dashLast = now; dashI = (dashI + 1) % DASH.length; map.setPaintProperty('h-flow', 'line-dasharray', DASH[dashI]); }
    if (playing || now < dashUntil) requestAnimationFrame(dashTick);
  }
  function wiSwell() { // stream glow follows the run's channel rise (or, before the runs land, the closures) through the storm
    if (!map || !map.getLayer('h-flow')) return;
    var a = (wi && wi.dj && wi.dj.channel_rise_km) || (stageAt() != null && stageSer) || meta.closed_per_frame || [], mx = Math.max.apply(0, a.concat([1e-6]));
    var f = Math.max(0, Math.min(nf - 1, t)), i = Math.floor(f), v = ((a[i] || 0) + ((a[i + 1] || a[i] || 0) - (a[i] || 0)) * (f - i)) / mx;
    v = Math.round(v * 20) / 20; if (v === swellLast) return; swellLast = v;
    map.setPaintProperty('h-flow', 'line-opacity', 0.25 + 0.7 * v);
    map.setPaintProperty('h-river', 'line-width', ['interpolate', ['exponential', 1.5], ['zoom'], 9, 1 + v, 13, 2.2 + 2 * v, 16, 5 + 4 * v]);
  }


  // ---------- what-if: loading, controls, labels ----------
  function pieceOrd(seg) { var c = {}; return seg.map(function (s) { c[s] = (c[s] || 0) + 1; return c[s] - 1; }); }
  function wiLoadJobs() {
    var k0 = wi.first, dj = wi.dj, ix = wi.index, jobs = [];
    total = 4;
    jobs.push(Promise.all([getJson(WI + 'roads.json'), getJson(WI + 'pieces.json').catch(function () { return null; })]).then(function (a) {
      var g = a[0]; if (a[1] && a[1].seg) { PCS = a[1]; PCS.k = pieceOrd(PCS.seg); }
      var may = {}; (dj.may || []).forEach(function (id) { may[id] = 1; });
      g.features.forEach(function (f) { var p = f.properties; p.d = dj.seg[f.id] || null; p.e = (dj.edge && dj.edge[f.id]) || null; p.p = dj.p[f.id] || 0; p.m = may[f.id] ? 1 : 0; if (p.d) { var iv = wiIntervals(p.d); if (iv.length) p.iv = iv; } });
      wi.roads = g;
      return new Promise(function (res) { whenStyle(function () { addRoads(g); progress(); res(); }); });
    }));
    jobs.push(getBitmap(WI + ix.terrain.sheet).then(function (img) {
      terrainLayer.set(ix.corners, img);
      whenStyle(function () { map.addLayer(terrainLayer.layer, map.getLayer('h-water') ? 'h-water' : 'l-voy'); applyTheme(); });
      return getBitmap(WI + ix.terrain.sheet).then(function (im2) { wdepth.setMask(im2); progress(); return getBitmap(WI + ix.terrain.sheet); }).then(function (im3) { flowLayer.setChannels(im3); });
    }).catch(function (e) { console.warn('terrain', e); progress(); }));
    jobs.push(getJson(WI + 'culverts.json').then(function (c) { whenStyle(function () { try { wiCulvertsInit(c.rows); } catch (e) { console.error('culverts', e); } }); progress(); }).catch(function (e) { console.warn('culverts', e); progress(); }));
    jobs.push(getJson(WI + k0 + '/flow.json').then(function (fi) {
      return getBitmap(WI + k0 + '/' + (fi.sheets ? fi.sheets[0] : fi.sheet)).then(function (img) {
        flowLayer.set(fi, img, WI + k0 + '/');
        whenStyle(function () { map.addLayer(flowLayer.layer, 'l-voy'); vis('flow', $('lyFlow').checked); });
        $('flowRow').hidden = $('flowKey').hidden = false; progress();
      });
    }).catch(function (e) { console.warn('flow', e); progress(); }));
    return jobs;
  }
  // the live replay's reference layers, on the scenario clock (15-min frames): observed gauge flow only, no single-run model numbers
  function wiRefs(r) {
    if (!WION) return r;
    var k = Math.round(meta.frame_min / 5);
    (r.gauges || []).forEach(function (g) {
      if (g.obs_q) g.obs_q = g.obs_q.filter(function (v, i) { return i % k === 0; });
      ['model_q', 'model_rise_m', 'model_peak_utc', 'timing_error_h'].forEach(function (x) { delete g[x]; });
    });
    r.reports = []; r.crossings = { columns: [], rows: [] }; // culverts come from the scenario (wiCulverts)
    return r;
  }
  function segmented(id, names) { // native-style segmented control driving a hidden range input
    var inp = $(id), box = inp.parentNode, g = document.createElement('div'); g.className = 'seg'; g.setAttribute('role', 'radiogroup');
    g.setAttribute('aria-label', box.querySelector('label b').textContent);
    names.forEach(function (nm, i) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = nm; b.dataset.v = i; b.setAttribute('role', 'radio');
      b.addEventListener('click', function () { inp.value = i; inp.dispatchEvent(new Event('input')); });
      g.appendChild(b);
    });
    inp.insertAdjacentElement('afterend', g); box.classList.add('has-seg');
  }
  function wiInitUi() {
    $('wi').hidden = false; document.documentElement.classList.add('wi-on');
    segmented('wiSoil', ['Dry', 'Normal', 'Soaked', 'Frozen']); segmented('wiCulv', ['Clear', 'Blocked']);
    if (WION && $('drnKey')) $('drnKey').remove();
    if (WION) { // the key names the stages of the water's journey
      var k = document.querySelector('#key .kramp.depth'); if (k) k.closest('.k').outerHTML =
        '<div class="k"><span class="kl">Water</span><span class="kr"><i class="kramp wl"></i><span class="kt kt5"><span>5</span><span>15</span><span>30</span><span>100 cm</span><span></span></span></span></div>' +
        '<div class="k kdrn"><span class="kl">Draining</span><span class="kr kroads"><span><i class="kw drn"></i>water going down</span></span></div>';
    }
    $('replayStory').hidden = true;
    ['wiRain', 'wiSoil', 'wiCulv'].forEach(function (id) {
      $(id).addEventListener('input', function () { wiLabels(); clearTimeout(wi.deb); wi.deb = setTimeout(wiSelect, 120); });
    });
    $('wiPlay').addEventListener('click', function () { if (!ready) return; played = false; setPlaying(true); });
    wiLabels();
    if (WION) wiNumbers();
    else {
      $('wiNRain').textContent = Math.round(sum(meta.rain_hourly_mean_mm || [], 99)) + ' mm';
      $('wiNClosed').innerHTML = n(meta.segments_p_ge_50 || 0) + (meta.segments_in_box ? '<small>' + (100 * meta.segments_p_ge_50 / meta.segments_in_box).toFixed(1) + '% of roads</small>' : '');
      $('wiNPeople').textContent = '–'; $('wiNCulv').textContent = n(meta.culverts_overtopped || 0);
      fetch(base + 'cascade.json').then(function (r) { return r.text(); }).then(function (x) { return JSON.parse(x.replace(/\bNaN\b/g, 'null')); }).then(function (c) { var pk = c && c.totals && c.totals.peak; if (pk && pk.pop_isolated != null) $('wiNPeople').textContent = n(pk.pop_isolated); }).catch(function () {});
    }
  }
  function wiLive() { // the live part of the numbers: roads closed right now
    var el = $('wiNClosedL'); if (!el) return;
    var txt = playing || played ? 'roads close (' + n(nClosedNow) + ' closed now)' : 'roads close during the storm';
    if (el.textContent !== txt) el.textContent = txt;
  }
  // labels: rivers, brooks, lakes and ponds, towns, route numbers, hospitals, schools, fire and police (OpenStreetMap via OpenFreeMap
  // vector tiles), dams (National Inventory of Dams); collision-aware, by zoom, most important first
  function addLabels() {
    if (!map.getSource('omt')) return;
    var halo = 'rgba(9,17,23,.9)', F = { r: ['Noto Sans Regular'], b: ['Noto Sans Bold'], i: ['Noto Sans Italic'] };
    var pill = document.createElement('canvas'); pill.width = pill.height = 24; var c = pill.getContext('2d');
    c.fillStyle = '#e9eef1'; c.strokeStyle = '#3c4852'; c.lineWidth = 2; rr(c, 1.5, 3.5, 21, 17, 4); c.fill(); c.stroke();
    if (!map.hasImage('shield')) map.addImage('shield', c.getImageData(0, 0, 24, 24), { pixelRatio: 2, stretchX: [[7, 17]], stretchY: [[8, 16]], content: [5, 5, 19, 19] });
    var L = [
      { id: 'lb-place', type: 'symbol', source: 'omt', 'source-layer': 'place', minzoom: 8, filter: ['match', ['get', 'class'], ['city', 'town', 'village', 'suburb', 'hamlet', 'neighbourhood'], true, false],
        layout: { 'text-field': ['get', 'name'], 'text-font': F.b, 'text-size': ['interpolate', ['linear'], ['zoom'], 9, ['match', ['get', 'class'], ['city', 'town'], 13, 10], 14, ['match', ['get', 'class'], ['city', 'town'], 17, 12.5]],
          'text-letter-spacing': 0.04, 'symbol-sort-key': ['match', ['get', 'class'], 'city', 0, 'town', 1, 'village', 2, 3], 'text-padding': 6 },
        paint: { 'text-color': '#e8eef2', 'text-halo-color': halo, 'text-halo-width': 1.6, 'text-opacity': ['interpolate', ['linear'], ['zoom'], 8, 0.9, 15, 0.55] } },
      { id: 'lb-water', type: 'symbol', source: 'omt', 'source-layer': 'water_name', minzoom: 11, filter: ['==', ['geometry-type'], 'Point'],
        layout: { 'text-field': ['get', 'name'], 'text-font': F.i, 'text-size': ['interpolate', ['linear'], ['zoom'], 11, 10.5, 15, 13.5], 'text-max-width': 7, 'text-padding': 4 },
        paint: { 'text-color': '#8fd8f2', 'text-halo-color': halo, 'text-halo-width': 1.4 } },
      { id: 'lb-waterl', type: 'symbol', source: 'omt', 'source-layer': 'water_name', minzoom: 11, filter: ['==', ['geometry-type'], 'LineString'],
        layout: { 'text-field': ['get', 'name'], 'text-font': F.i, 'text-size': ['interpolate', ['linear'], ['zoom'], 11, 10.5, 15, 13.5], 'symbol-placement': 'line', 'text-padding': 4 },
        paint: { 'text-color': '#8fd8f2', 'text-halo-color': halo, 'text-halo-width': 1.4 } },
      { id: 'lb-river', type: 'symbol', source: 'omt', 'source-layer': 'waterway', minzoom: 11.5, filter: ['all', ['has', 'name'], ['!=', ['get', 'brunnel'], 'tunnel']],
        layout: { 'text-field': ['get', 'name'], 'text-font': F.i, 'text-size': ['interpolate', ['linear'], ['zoom'], 12, ['match', ['get', 'class'], 'river', 11.5, 10], 16, ['match', ['get', 'class'], 'river', 14, 12]],
          'symbol-placement': 'line', 'symbol-spacing': 320, 'text-letter-spacing': 0.06, 'symbol-sort-key': ['match', ['get', 'class'], 'river', 0, 1] },
        paint: { 'text-color': '#7fe0e8', 'text-halo-color': halo, 'text-halo-width': 1.4 } },
      { id: 'lb-shield', type: 'symbol', source: 'omt', 'source-layer': 'transportation_name', minzoom: 9.5,
        filter: ['all', ['has', 'ref'], ['<=', ['length', ['to-string', ['get', 'ref']]], 5], ['match', ['get', 'class'], ['motorway', 'trunk', 'primary', 'secondary'], true, false]],
        layout: { 'text-field': ['get', 'ref'], 'text-font': F.b, 'text-size': 10.5, 'icon-image': 'shield', 'icon-text-fit': 'both', 'icon-text-fit-padding': [1, 4, 1, 4],
          'symbol-placement': 'line', 'symbol-spacing': 420, 'text-rotation-alignment': 'viewport', 'icon-rotation-alignment': 'viewport', 'symbol-sort-key': ['match', ['get', 'class'], 'motorway', 0, 'trunk', 1, 2] },
        paint: { 'text-color': '#17222c' } },
      { id: 'lb-road', type: 'symbol', source: 'omt', 'source-layer': 'transportation_name', minzoom: 13.5, filter: ['has', 'name'],
        layout: { 'text-field': ['get', 'name'], 'text-font': F.r, 'text-size': ['interpolate', ['linear'], ['zoom'], 14, 10, 17, 13], 'symbol-placement': 'line', 'symbol-spacing': 260, 'text-padding': 3 },
        paint: { 'text-color': '#c3ccd3', 'text-halo-color': halo, 'text-halo-width': 1.3 } },
      { id: 'lb-poi', type: 'symbol', source: 'omt', 'source-layer': 'poi', minzoom: 13,
        filter: ['any', ['match', ['get', 'class'], ['hospital', 'school', 'college', 'police', 'fire_station', 'town_hall'], true, false], ['match', ['get', 'subclass'], ['hospital', 'fire_station', 'police', 'school'], true, false]],
        layout: { 'text-field': ['get', 'name'], 'text-font': F.r, 'text-size': 10.5, 'text-max-width': 9, 'text-padding': 4, 'text-optional': true,
          'symbol-sort-key': ['match', ['get', 'class'], 'hospital', 0, 'fire_station', 1, 'police', 1, 2] },
        paint: { 'text-color': ['match', ['get', 'class'], 'hospital', '#ff9aa8', ['fire_station', 'police'], '#ffc28a', '#d7dde2'], 'text-halo-color': halo, 'text-halo-width': 1.3 } }
    ];
    // dams and the region's hospitals / stations from the replay's reference files (names from NID and OpenStreetMap)
    var R = refs || {}, pts = [];
    (R.dams || []).forEach(function (d) { if (d[2]) pts.push({ type: 'Feature', properties: { name: title(d[2]).replace(/\bDam\b/, 'dam'), k: 'dam' }, geometry: { type: 'Point', coordinates: [d[0], d[1]] } }); });
    var FAC = R.facilities || {};
    [['hospital', 'hospital'], ['fire_station', 'fire'], ['police', 'police']].forEach(function (a) {
      (FAC[a[0]] || []).forEach(function (f) { if (f[2]) pts.push({ type: 'Feature', properties: { name: f[2], k: a[1] }, geometry: { type: 'Point', coordinates: [f[0], f[1]] } }); });
    });
    map.addSource('lbp', { type: 'geojson', data: { type: 'FeatureCollection', features: pts } });
    L.push({ id: 'lb-pts', type: 'symbol', source: 'lbp', minzoom: 11.5,
      layout: { 'text-field': ['get', 'name'], 'text-font': ['match', ['get', 'k'], 'dam', ['literal', F.i], ['literal', F.r]], 'text-size': ['match', ['get', 'k'], 'hospital', 11.5, 10.5],
        'text-max-width': 9, 'text-variable-anchor': ['top', 'bottom', 'right', 'left'], 'text-radial-offset': 0.9, 'text-padding': 3, 'symbol-sort-key': ['match', ['get', 'k'], 'hospital', 0, 'dam', 1, 2] },
      paint: { 'text-color': ['match', ['get', 'k'], 'dam', '#9cc8ff', 'hospital', '#ff9aa8', '#ffc28a'], 'text-halo-color': halo, 'text-halo-width': 1.4 } });
    // streets for 'this closed road runs between X and Y': an invisible query layer and a highlight of the two cross streets
    map.addLayer({ id: 'net-q', type: 'line', source: 'omt', 'source-layer': 'transportation_name', minzoom: 10, filter: ['has', 'name'], paint: { 'line-width': 10, 'line-opacity': 0 } }, 'edge');
    map.addLayer({ id: 'net-hl', type: 'line', source: 'omt', 'source-layer': 'transportation_name', filter: ['in', ['get', 'name'], ['literal', []]],
      layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-width': ['interpolate', ['linear'], ['zoom'], 11, 2, 16, 6], 'line-opacity': 0.55, 'line-dasharray': [1.5, 1] } }, 'edge');
    map.addLayer({ id: 'net-alt', type: 'line', source: 'omt', 'source-layer': 'transportation_name', filter: ['in', ['get', 'name'], ['literal', []]],
      layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': css('--alt') || '#1E8E3E', 'line-width': ['interpolate', ['linear'], ['zoom'], 11, 2.5, 16, 7], 'line-opacity': 0.55 } }, 'edge');
    L.forEach(function (l) { if (!map.getLayer(l.id)) map.addLayer(l, map.getLayer('rlab-w') ? 'rlab-w' : undefined); });
    applyTheme();
  }
  // vector water and hillshade for the what-if basemap (OpenFreeMap / OpenMapTiles, AWS Terrain Tiles)
  function hydroLayers() {
    if (!REPLAY) return [];
    var Z = ['zoom'];
    return [
      { id: 'b-hshade', type: 'hillshade', source: 'dem', layout: { visibility: 'none' },
        paint: { 'hillshade-exaggeration': 0.4, 'hillshade-shadow-color': '#121417', 'hillshade-highlight-color': '#3a4047', 'hillshade-accent-color': '#1a1d20', 'hillshade-illumination-direction': 315 } },
      { id: 'v-park', type: 'fill', source: 'omt', 'source-layer': 'park', paint: { 'fill-color': '#E8EBE4', 'fill-opacity': 0.9 } },
      { id: 'v-bldg', type: 'fill', source: 'omt', 'source-layer': 'building', minzoom: 14, paint: { 'fill-color': '#E4E4E0', 'fill-opacity': ['interpolate', ['linear'], ['zoom'], 14, 0, 15, 1] } },
      { id: 'h-water', type: 'fill', source: 'omt', 'source-layer': 'water', paint: { 'fill-color': '#D5DDE3', 'fill-opacity': 1 } },
      // ponds and lakes rise with the river: the outline thickens and brightens with the stage (pondSwell)
      { id: 'h-water-ol', type: 'line', source: 'omt', 'source-layer': 'water', minzoom: 11, paint: { 'line-color': '#3586C4', 'line-width': 0.6, 'line-opacity': 0.15 } },
      { id: 'h-stream', type: 'line', source: 'omt', 'source-layer': 'waterway', minzoom: 10, filter: ['match', ['get', 'class'], ['stream', 'drain', 'ditch'], true, false],
        layout: { 'line-cap': 'round', 'line-join': 'round' },
        paint: { 'line-color': '#2b8db5', 'line-width': ['interpolate', ['exponential', 1.5], Z, 11, 0.6, 14, 1.6, 17, 3.5], 'line-opacity': ['interpolate', ['linear'], Z, 10, 0.4, 13, 0.85] } },
      { id: 'h-river', type: 'line', source: 'omt', 'source-layer': 'waterway', filter: ['match', ['get', 'class'], ['river', 'canal'], true, false],
        layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#3aa7d6', 'line-width': ['interpolate', ['exponential', 1.5], Z, 9, 1, 13, 2.2, 16, 5] } },
      { id: 'h-flow', type: 'line', source: 'omt', 'source-layer': 'waterway', minzoom: 11, filter: ['all', ['match', ['get', 'class'], ['river', 'canal', 'stream'], true, false], ['!=', ['get', 'brunnel'], 'tunnel']],
        layout: { 'line-cap': 'butt', 'line-join': 'round' },
        paint: { 'line-color': '#b9f3ff', 'line-width': ['interpolate', ['exponential', 1.5], Z, 11, 0.8, 14, ['match', ['get', 'class'], 'stream', 1.2, 2], 17, ['match', ['get', 'class'], 'stream', 2.6, 4]],
          'line-opacity': 0.35, 'line-dasharray': DASH[0] } }
    ];
  }
  function labelTheme(b) { // vector labels (every tab): colours per basemap
    var night = b === 'night' || b === 'dark', sat = b === 'satellite', dk = night || sat;
    var halo = dk ? 'rgba(30,33,36,.92)' : '#FFFFFF';
    var col = { 'lb-place': dk ? '#E8EAED' : '#1F2328', 'lb-water': dk ? '#9cc3dc' : '#2F5C80', 'lb-waterl': dk ? '#9cc3dc' : '#2F5C80', 'lb-river': dk ? '#9cc3dc' : '#2F5C80', 'lb-road': dk ? '#C3C7CC' : '#3C4043' };
    Object.keys(col).forEach(function (id) { if (map.getLayer(id)) { map.setPaintProperty(id, 'text-color', col[id]); map.setPaintProperty(id, 'text-halo-color', halo); } });
    if (map.getLayer('lb-poi')) map.setPaintProperty('lb-poi', 'text-color', ['match', ['get', 'class'], 'hospital', dk ? '#ff9aa8' : '#b4122c', ['fire_station', 'police'], dk ? '#ffc28a' : '#9a4a00', dk ? '#d7dde2' : '#4b5864']);
    if (map.getLayer('lb-pts')) map.setPaintProperty('lb-pts', 'text-color', ['match', ['get', 'k'], 'dam', dk ? '#9cc8ff' : '#1f5fa8', 'hospital', dk ? '#ff9aa8' : '#b4122c', dk ? '#ffc28a' : '#9a4a00']);
    ['lb-poi', 'lb-pts'].forEach(function (id) { if (map.getLayer(id)) map.setPaintProperty(id, 'text-halo-color', halo); });
    if (map.getLayer('net-hl')) map.setPaintProperty('net-hl', 'line-color', dk ? '#ffffff' : '#17222c');
  }
  function wiTheme(b) { // colours of the vector water per basemap (what-if tab)
    labelTheme(b);
    if (!map.getLayer('h-water')) return;
    var night = b === 'night' || b === 'dark', sat = b === 'satellite';
    ['h-water', 'v-park', 'v-bldg'].forEach(function (id) { if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', sat ? 'none' : 'visible'); });
    map.setPaintProperty('h-water', 'fill-color', night ? '#2B3A45' : '#D5DDE3');
    map.setPaintProperty('v-park', 'fill-color', night ? '#252a26' : '#E8EBE4'); map.setPaintProperty('v-bldg', 'fill-color', night ? '#2a2e33' : '#E4E4E0');
    map.setPaintProperty('h-stream', 'line-color', night ? '#3f6178' : sat ? '#7fd4ff' : '#A9BFCF');
    map.setPaintProperty('h-river', 'line-color', night ? '#4a6f88' : sat ? '#8adcff' : '#9DB6C8');
    map.setPaintProperty('h-flow', 'line-color', night || sat ? '#b9e6f5' : '#ffffff');
    wpalFor(b); WPAL.chan = WPAL.land; // rising streams stay in the one blue depth family
    WPAL.terrain = night ? [[0.09, 0.1, 0.11], [0.24, 0.26, 0.28], [0.17, 0.23, 0.27]] : [[0.8, 0.8, 0.78], [0.97, 0.97, 0.95], [0.84, 0.87, 0.89]];
    terrainLayer.opacity(sat || !WHATIF ? 0 : night ? 0.5 : 0.28);
  }


  // ---------- instruments: the inputs and the state of the system at the current moment, for the whole replay ----------
  var instCx = null, instSer = {};
  function instInit() {
    var g = instGauge();
    $('inRiverBox').hidden = !g;
    if (WHATIF) { var sv = +$('wiSoil').value; $('inGround').textContent = ['dry', 'as it was', 'soaked', 'frozen'][sv]; $('inGroundS').textContent = ['driest soil class', 'normal wetness', 'wettest soil class', 'sheds rain like pavement'][sv]; }
    instSpark('inRoadsSp', meta.closed_per_frame || [], 'roads');
    if (g) instSpark('inRiverSp', g.obs_q || [], 'river');
    instNow();
  }
  function instGauge() { if (!refs || !refs.gauges || !refs.gauges.length) return null; var g = refs.gauges[+$('gaugeSel').value] || refs.gauges[0]; return g && g.obs_q ? g : null; }
  function instSpark(id, a, key) {
    var el = $(id); if (!el) return;
    var mx = 0, k; for (k = 0; k < a.length; k++) if (a[k] != null && a[k] > mx) mx = a[k];
    var N = Math.max(1, nf - 1), pts = [];
    for (k = 0; k < a.length; k += Math.max(1, Math.floor(a.length / 120))) if (a[k] != null) pts.push((100 * k / N).toFixed(1) + ',' + (23 - 21 * a[k] / (mx || 1)).toFixed(1));
    el.innerHTML = '<polyline points="' + pts.join(' ') + '" fill="none" stroke="currentColor" stroke-width="1.4" vector-effect="non-scaling-stroke"/><line class="cur" x1="0" x2="0" y1="0" y2="24" vector-effect="non-scaling-stroke"/>';
    instSer[key] = el.querySelector('.cur');
  }
  function instNow() {
    if (!meta) return;
    var per = 60 / meta.frame_min, h = t / per, r = meta.rain_hourly_mean_mm || [], hr = r[Math.floor(h)] || 0, tot = sum(r, h);
    $('inRain').textContent = (hr >= 10 ? Math.round(hr) : hr.toFixed(1)) + ' mm/h';
    $('inRainS').textContent = (tot >= 10 ? Math.round(tot) : tot.toFixed(1)) + ' mm so far (area average)';
    var x = (100 * t / Math.max(1, nf - 1)).toFixed(2);
    Object.keys(instSer).forEach(function (k) { var c = instSer[k]; if (c) { c.setAttribute('x1', x); c.setAttribute('x2', x); } });
    var g = instGauge();
    if (g) { var q = g.obs_q[Math.round(t)]; $('inRiver').textContent = q != null ? (q >= 10 ? Math.round(q) : q.toFixed(1)) + ' m³/s' : '–'; $('inRiverL').textContent = 'River, observed: ' + g.name.replace(/, MA$/, '').replace(/ (at|near) .*/, ''); }
    var cx = WION && wi && wi.cxT ? Object.keys(wi.cxT).map(function (k) { return wi.cxT[k]; }) : instCx, nc = 0;
    if (cx) { for (var i = 0; i < cx.length; i++) if (cx[i] <= t) nc++; $('inCulv').textContent = n(nc); $('inCulvS').textContent = 'of ' + n(cx.length) + ' that overtop in this run'; }
    else { $('inCulv').textContent = meta.culverts_overtopped != null ? n(meta.culverts_overtopped) : '–'; $('inCulvS').textContent = 'over the whole storm'; }
    $('inRoads').textContent = n(nClosedNow);
  }
  // knock-on numbers from the replay's cascade file (tolerates NaN in it): culvert overtopping times and people cut off
  function loadCascadeNumbers() {
    return fetch(base + 'cascade.json').then(function (r) { if (!r.ok) throw 0; return r.text(); }).then(function (x) {
      var c = JSON.parse(x.replace(/\bNaN\b/g, 'null')), fpm = meta.frame_min;
      if (!WION) instCx = (c.culverts || []).filter(function (u) { return u.first_h != null; }).map(function (u) { return u.first_h * 60 / fpm; });
      return c;
    }).catch(function () { return null; });
  }

  // ---------- evidence: real reports, which the model caught, gauges, the honest headline ----------
  function loadEvidence(casc) {
    return getJson(base + 'evidence.json').then(function (E) {
      if (refs) { refs.crowd = (E.crowd && E.crowd.rows) || []; }
      var R = refs || {}, rep_ = R.reports || [], hit = rep_.filter(function (x) { return x[6]; }).length, cr = refs.crowd, c30 = cr.filter(function (x) { return x[6] >= 3; }).length;
      var gs = (R.gauges || []).filter(function (g) { return g.obs_rise_m != null; });
      var pk = casc && casc.totals && casc.totals.peak;
      var h = '<p class="ev-head">' + esc(E.numbers.heldout.text) + '</p>';
      if (!WHATIF) {
        h += '<ul class="ev">';
        if (rep_.length) h += '<li><b>' + hit + ' of ' + rep_.length + '</b> storm reports (NWS, NOAA, news, city public works) have 30 cm or more of modelled water nearby <span class="ok">▲</span> caught, <span class="ok">△</span> not</li>';
        if (cr.length) h += '<li><b>' + c30 + ' of ' + cr.length + '</b> residents’ pins (MRPC / BSC map) have 30 cm or more modelled within ' + Math.round(E.radius_m) + ' m</li>';
        gs.forEach(function (g) { h += '<li>' + gaugeName(g) + ': river rose <b>' + g.obs_rise_m.toFixed(2) + ' m</b> observed, <b>' + (g.model_rise_m != null ? g.model_rise_m.toFixed(2) + ' m' : '–') + '</b> modelled</li>'; });
        if (pk && pk.pop_isolated != null) h += '<li><b>' + n(pk.pop_isolated) + '</b> residents cut off from any hospital, fire or police station at the worst moment (' + n(pk.pop_lost_any) + ' lose at least one)</li>';
        h += '</ul>';
      } else h += '<p class="ev-note">Markers: the residents’ flood reports from this storm. Which ones the model catches is shown on the Leominster tab (the actual storm).</p>';
      h += '<p class="ev-small">' + esc(E.numbers.tuned.text) + ' Sources: docs/proto/STATUS.md, docs/proto/obs/CROWD.md.</p>';
      $('evidBody').innerHTML = h; $('evid').hidden = false;
      if (!WHATIF) { var rp = document.querySelector('input[data-ref="reports"]'); if (rp) rp.checked = true; }
    }).catch(function () { /* no evidence file for this run */ });
  }

  // ---------- phones: the panels live in a bottom sheet; the map is full screen until the sheet is opened ----------
  var homes = {};
  function sheetPlace() {
    var pl = document.querySelector('.player'), body = $('sheetBody'), card = $('card');
    ['rank', 'evid', 'legend', 'tabs', 'live', 'inst'].forEach(function (id) {
      var el = $(id); if (!el) return;
      if (!homes[id]) homes[id] = { parent: el.parentNode, next: el.nextSibling };
      if (id === 'legend') { if (el.parentNode !== homes[id].parent) homes[id].parent.insertBefore(el, homes[id].next); return; }
      if (id === 'tabs') { if (small()) { if (el.parentNode !== document.body) document.body.appendChild(el); } else if (el.parentNode !== homes[id].parent) homes[id].parent.insertBefore(el, homes[id].next); return; }
      if (id === 'inst') { if (small()) { if (el.previousElementSibling !== $('timeline')) $('timeline').insertAdjacentElement('afterend', el); } else if (el.parentNode !== card) { var after = $('live'); after.insertAdjacentElement('afterend', el); } return; }
      if (id === 'live') { if (small()) { if (el.parentNode !== pl) $('grab').insertAdjacentElement('afterend', el); } else if (el.parentNode !== homes[id].parent) homes[id].parent.insertBefore(el, homes[id].next); return; }
      if (small()) { if (el.parentNode !== body) body.appendChild(el); }
      else if (el.parentNode !== homes[id].parent) homes[id].parent.insertBefore(el, homes[id].next);
    });
    // phones: the status line heads the sheet; desktop: it sits in the card, and the what-if controls move into the card too
    var sl = $('statusLine'), w = $('wi');
    if (small()) { if (sl.parentNode !== pl) $('grab').insertAdjacentElement('afterend', sl); if (w.parentNode !== pl || w.previousElementSibling !== $('inst')) $('inst').insertAdjacentElement('afterend', w); }
    else { if (sl.parentNode !== card) card.querySelector('.pick').insertAdjacentElement('afterend', sl); if (WHATIF && w.parentNode !== card) sl.insertAdjacentElement('afterend', w); }
    pl.dataset.sheet = small() ? 'on' : 'off';
    document.documentElement.style.setProperty('--card-b', Math.round(card.getBoundingClientRect().bottom) + 'px');
    if (small()) sheetDetent(detent || 'peek'); else { pl.style.removeProperty('--sheet-off'); pl.style.removeProperty('--sheet-h'); pl.style.transform = ''; delete pl.dataset.detent; }
  }
  function sheetToggle(open) {
    if (small()) { sheetDetent(open === undefined ? (detent === 'peek' ? 'half' : 'peek') : open ? 'half' : 'peek'); return; }
    var pl = document.querySelector('.player'); if (open === undefined) open = pl.dataset.open !== 'true';
    pl.dataset.open = open ? 'true' : 'false'; $('grab').setAttribute('aria-expanded', open ? 'true' : 'false');
    document.documentElement.classList.toggle('sheet-open', open);
    $('grabL').textContent = open ? 'Show more map' : (WHATIF ? 'Set up the storm, layers, timeline' : 'Timeline, layers, evidence');
    drawChart();
  }

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
      if (s && s.state === 'quiet') { forecastQuiet(s); liveInit(s); return; }
      var ok = s && (s.ready === true || s.status === 'ok' || s.state === 'run') && dir;
      if (!ok) throw new Error('forecast not ready');
      base = 'site/data/' + String(dir).replace(/^(site\/)?data\//, '').replace(/\/?$/, '/');
      if (!s.title && s.headline) s.title = s.headline;
      if (s.title) $('runTitle').textContent = s.title;
      $('runKind').textContent = s.kind || ('Forecast issued ' + (s.issued ? fmtShort.format(new Date(s.issued)) : '') + ' from the NOAA HRRR rain forecast.');
      start(); liveInit(s);
    }).catch(function () { forecastPlaceholder(); liveInit(null); });
  } else if (WHATIF) {
    getJson(WI + 'index.json').then(function (ix) {
      var b = ix.scenarios && ix.scenarios[ix.baseline];
      if (!b || b.status !== 'ok' || !ix.terrain) throw new Error('what-if runs not published yet');
      wi = { index: ix, cache: {}, x: 1 }; WION = true;
      var k0 = params.get('s') || store('mfw-whatif'); if (!(k0 && ix.scenarios[k0] && ix.scenarios[k0].status === 'ok')) k0 = ix.baseline;
      wiSetCtl(k0);
      return wiLoad(k0).then(function (dj) {
        wi.first = k0; wi.dj = dj; wi.key = k0;
        begin({ corners: ix.corners, storm_start: ix.storm_start || dj.storm_start, frame_min: dj.frame_min, nf: dj.nf, w: ix.terrain.w, h: ix.terrain.h, sheets: dj.sheets,
          rain_hourly_mean_mm: dj.rain_hourly_mean_mm, closed_per_frame: dj.closed_per_frame, segments_in_box: dj.numbers.segments_in_box,
          segments_p_ge_50: dj.numbers.segments_closed, km_p_ge_50: dj.numbers.km_closed, segments_may_close: dj.numbers.segments_may_close,
          culverts_overtopped: dj.numbers.culverts_overtopped, rain_peak1h_max_mm: dj.numbers.rain_peak1h_mm, rain_max_total_mm: dj.numbers.rain_max_total_mm });
      });
    }).catch(function (e) { console.info('what-if:', e && e.message); wi = { index: null, cache: {}, x: 1 }; WION = false; start(); });
  } else start();
  function wiSetCtl(key) {
    var p = String(key).split('_');
    $('wiRain').value = Math.max(0, wiCtl.rain.indexOf(p[0])); $('wiSoil').value = Math.max(0, wiCtl.soil.indexOf(p[1])); $('wiCulv').value = Math.max(0, wiCtl.culv.indexOf(p[2]));
  }

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
    getJson(base + 'meta.json').then(begin).catch(function (e) { $('loadText').textContent = 'The storm data did not load. Reload the page to try again.'; console.error(e); });
  }
  function begin(m) {
    {
      meta = m; nf = m.nf;
      if (m.kofn) { var bl = document.querySelector('[data-band=rain] .blabel'); if (bl) bl.innerHTML = '<b>Input</b> forecast rain, NOAA HRRR (box mean, mm/h)'; }
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
      if (params.get('t') != null && !isNaN(+params.get('t'))) t = Math.max(0, Math.min(nf - 1, +params.get('t')));
      if (WHATIF) wiInitUi();
      drawChart();
      initMap();
    }
  }

  // ---------- map ----------
  function baseStyle() {
    var st = {
      version: 8,
      glyphs: 'https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf',
      sources: {
        // CARTO raster tiles now ask for an API key on this domain: Esri basemaps (no key)
        lgt: ESRI('Canvas/World_Light_Gray_Base', 16, 'Esri, HERE, Garmin, © OpenStreetMap contributors'),
        omt: { type: 'vector', url: 'https://tiles.openfreemap.org/planet', attribution: '<a href="https://openfreemap.org">OpenFreeMap</a> © <a href="https://www.openmaptiles.org/">OpenMapTiles</a>' },
        voyl: ESRI('Canvas/World_Light_Gray_Reference', 16, 'Esri'),
        drk: ESRI('Canvas/World_Dark_Gray_Base', 16, 'Esri, HERE, Garmin, © OpenStreetMap contributors'),
        drkl: ESRI('Canvas/World_Dark_Gray_Reference', 16, 'Esri'),
        sat: ESRI('World_Imagery', 18, 'Imagery © Esri, Maxar, Earthstar Geographics, USDA, USGS, AeroGRID, IGN, and the GIS User Community'),
        hill: ESRI('Elevation/World_Hillshade', 16, 'Hillshade © Esri, USGS, NGA, NASA, CGIAR, N Robinson, NCEAS, NLS, OS, NMA, Geodatastyrelsen, Rijkswaterstaat, GSA, Geoland, FEMA, Intermap')
      },
      layers: [
        { id: 'b-hill', type: 'raster', source: 'hill', layout: { visibility: 'none' }, paint: { 'raster-fade-duration': 150 } },
        { id: 'b-lgt', type: 'raster', source: 'lgt', layout: { visibility: 'none' }, paint: { 'raster-fade-duration': 150 } },
        { id: 'b-sat', type: 'raster', source: 'sat', layout: { visibility: 'none' }, paint: { 'raster-fade-duration': 150, 'raster-saturation': -0.25, 'raster-brightness-max': 0.82, 'raster-contrast': 0.05 } },
        { id: 'b-dark', type: 'raster', source: 'drk', layout: { visibility: 'none' }, paint: { 'raster-fade-duration': 150, 'raster-brightness-min': 0.04 } }
      ].concat(hydroLayers(), netLayers(), [
        { id: 'l-voy', type: 'raster', source: 'voyl', layout: { visibility: 'none' }, paint: { 'raster-fade-duration': 150 } },
        { id: 'l-dark', type: 'raster', source: 'drkl', layout: { visibility: 'none' }, paint: { 'raster-fade-duration': 150 } }
      ])
    };
    if (REPLAY) {
      st.sources.dem = { type: 'raster-dem', encoding: 'terrarium', tileSize: 256, maxzoom: 14, tiles: ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'],
        attribution: 'Terrain: <a href="https://registry.opendata.aws/terrain-tiles/">AWS Terrain Tiles</a> (USGS 3DEP)' };
      st.layers.unshift({ id: 'bg', type: 'background', paint: { 'background-color': '#F2F2EF' } });
    }
    return st;
  }
  // the street network: OpenMapTiles 'transportation' classes grouped into highway (0), arterial (1), collector (2),
  // local (3); highways from district zoom, locals fade in by street zoom; a white fill appears inside the casing at
  // street zoom so streets read as streets. Drawn under the water, so flooded streets disappear under the blue.
  var NET_RANK = ['match', ['get', 'class'], ['motorway', 'trunk'], 0, ['primary', 'secondary'], 1, 'tertiary', 2, 'minor', 3, 4];
  function netLayers() {
    var Z = ['zoom'], R = NET_RANK;
    var cw = ['interpolate', ['exponential', 1.5], Z,
      8, ['match', R, 0, 1.1, 1, 0.6, 0.3],
      10, ['match', R, 0, 2.2, 1, 1.4, 2, 0.8, 0.5],
      11, ['match', R, 0, 2.8, 1, 2, 2, 1.3, 3, 0.9, 0.6],
      12, ['match', R, 0, 3.8, 1, 2.8, 2, 1.8, 3, 1.3, 0.9],
      14, ['match', R, 0, 7, 1, 5.4, 2, 4, 2.8],
      17, ['match', R, 0, 18, 1, 14, 2, 11, 8]];
    var fw = ['interpolate', ['exponential', 1.5], Z, 11.5, 0, 13, ['match', R, 0, 2.2, 1, 1.4, 2, 0.8, 0.4],
      14, ['match', R, 0, 4.6, 1, 3.4, 2, 2.4, 1.4], 17, ['match', R, 0, 15, 1, 11.5, 2, 9, 6]];
    // minor / residential streets are drawn from z11 so a flooded street reads as one street among its neighbours
    var op = ['interpolate', ['linear'], Z, 10.3, ['match', R, [3, 4], 0, 1], 11, ['match', R, 4, 0, 1], 13, ['match', R, 4, 0.6, 1], 14.5, 1];
    var filt = ['all', ['match', ['get', 'class'], ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'minor', 'service'], true, false],
      ['!=', ['get', 'brunnel'], 'tunnel']];
    return [
      { id: 'net-case', type: 'line', source: 'omt', 'source-layer': 'transportation', filter: filt, minzoom: 7,
        layout: { 'line-cap': 'round', 'line-join': 'round', 'line-sort-key': ['-', 3, R] }, paint: { 'line-width': cw, 'line-opacity': op, 'line-color': '#76818b' } },
      { id: 'net-fill', type: 'line', source: 'omt', 'source-layer': 'transportation', filter: filt, minzoom: 11.5,
        layout: { 'line-cap': 'round', 'line-join': 'round', 'line-sort-key': ['-', 3, R] }, paint: { 'line-width': fw, 'line-opacity': op, 'line-color': '#ffffff' } }
    ];
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
      var lgTop = lg.width && !$('legend').hidden ? lg.top : H, st = $('story');
      if (!st.hidden) lgTop = Math.min(lgTop, st.getBoundingClientRect().top);
      p = { top: card.bottom + g, bottom: H - Math.min(pl.height ? pl.top : H, lgTop) + g, left: g, right: g };
      if (!fc.hidden) { var r2 = fc.getBoundingClientRect(); p.bottom = Math.max(p.bottom, H - r2.top + g); }
    }
    // never leave less than 40% of the map free: shrink padding proportionally if the panels are huge
    var fw = W - p.left - p.right, fh = H - p.top - p.bottom;
    if (fw < W * 0.4) { var k = (W * 0.6) / (p.left + p.right); p.left *= k; p.right *= k; }
    if (fh < H * 0.3) { var k2 = (H * 0.7) / (p.top + p.bottom); p.top *= k2; p.bottom *= k2; }
    return p;
  }

  // ---------- model coverage: where the live forecast runs (MassDOT District 3) and where the model was only tested on past storms
  // (the District 4-6 storm boxes); everything else is greyed out (docs/site/data/coverage.json, proto/build_coverage.py)
  function addCoverage() {
    getJson('site/data/coverage.json').then(function (C) {
      var fc = C.features.filter(function (f) { return f.properties.k === 'forecast'; })[0], ts = C.features.filter(function (f) { return f.properties.k === 'tested'; })[0];
      var outers = function (g) { return !g ? [] : g.type === 'Polygon' ? [g.coordinates[0]] : g.coordinates.map(function (p) { return p[0]; }); };
      var mask = { type: 'Feature', properties: {}, geometry: { type: 'Polygon', coordinates: [[[-179, -85], [179, -85], [179, 85], [-179, 85], [-179, -85]]].concat(outers(fc.geometry), outers(ts && ts.geometry)) } };
      map.addSource('cov', { type: 'geojson', data: C }); map.addSource('cov-mask', { type: 'geojson', data: mask });
      var before = map.getLayer('depth') ? 'depth' : 'l-voy';
      map.addLayer({ id: 'cov-out', type: 'fill', source: 'cov-mask', paint: { 'fill-color': '#5F6368', 'fill-opacity': 0.34 } }, before);
      map.addLayer({ id: 'cov-test', type: 'fill', source: 'cov', filter: ['==', ['get', 'k'], 'tested'], paint: { 'fill-color': '#5F6368', 'fill-opacity': 0.2 } }, before);
      map.addLayer({ id: 'cov-test-ol', type: 'line', source: 'cov', filter: ['==', ['get', 'k'], 'tested'], paint: { 'line-color': '#5F6368', 'line-width': 1, 'line-dasharray': [3, 2] } }, before);
      map.addLayer({ id: 'cov-d3', type: 'line', source: 'cov', filter: ['==', ['get', 'k'], 'forecast'], paint: { 'line-color': '#1F2328', 'line-width': ['interpolate', ['linear'], ['zoom'], 7, 1.2, 12, 2], 'line-opacity': 0.8 } }, before);
      $('covKey').hidden = false;
    }).catch(function (e) { console.warn('coverage', e); });
  }

  function initMap() {
    map = new maplibregl.Map({
      container: 'map', bounds: boxBounds(), maxZoom: 16, minZoom: 6, dragRotate: false, pitchWithRotate: false,
      fitBoundsOptions: { padding: framePadding() }, attributionControl: false, fadeDuration: 0, style: baseStyle()
    });
    map.addControl(new maplibregl.AttributionControl({ compact: true, customAttribution: 'Flood model: LISFLOOD-FP 8.2 · Rain: ' + (meta && meta.kofn ? 'NOAA HRRR forecast' : 'NOAA MRMS') + ' · Roads: MassDOT' }));
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    map.touchZoomRotate.disableRotation();
    if (params.get('debug') === '1') { window.__mfwZoom = function (c, z) { map.jumpTo({ center: c, zoom: z }); }; window.__mfwState = function () { return { wi: wi && { key: wi.key, cxT: wi.cxT && Object.keys(wi.cxT).length, hasDj: !!wi.dj }, wcx: !!map.getLayer('wcx'), flow: flowLayer.stat(), flowVis: map.getLayer('flow') && map.getLayoutProperty('flow', 'visibility') }; }; } // screenshot checks
    map.once('style.load', function () {
      map.addLayer(WION ? wdepth.layer : depth.layer, 'l-voy');
      addCoverage();
      applyTheme();
      styleReady();
    });
    map.on('movestart', function () { mapMoving = true; });
    map.on('moveend', function () { mapMoving = false; flowLayer.reset(); map.triggerRepaint(); });
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
    var jobs = WION ? wiLoadJobs() : meta.sheets.map(function (s, i) {
      return getBitmap(base + s).then(function (img) { depth.add(i, img); progress(); if (styleOk) map.triggerRepaint(); });
    });
    if (!WION) jobs.push(Promise.all([getJson(base + 'roads.json'), getJson(base + 'pieces.json').catch(function () { return null; })]).then(function (a) {
      if (a[1] && a[1].seg) { PCS = a[1]; PCS.k = pieceOrd(PCS.seg); }
      return new Promise(function (res) { whenStyle(function () { addRoads(a[0]); progress(); res(); }); });
    }));
    // optional layers: a missing file only hides that layer
    jobs.push(getJson(base + 'rain.json').then(function (r) {
      return getBitmap(base + r.sheet).then(function (img) {
        r.off = (new Date(r.start.replace(/Z$/, ':00Z')) - t0) / 60000;
        rain = r; rainLayer.set(img);
        whenStyle(function () { map.addLayer(rainLayer.layer, map.getLayer('depth') ? 'depth' : 'l-voy'); vis('rain', $('lyRain').checked); });
        $('rainRow').hidden = false; $('rainKey').hidden = !$('lyRain').checked;
        progress();
      });
    }).catch(function () { progress(); }));
    jobs.push(getJson(base + 'refs.json').then(function (r) { refs = WHATIF ? wiRefs(r) : r; whenStyle(function () { try { addRefs(); raiseLabels(); } catch (e) { console.error('refs', e); } }); }).catch(function (e) { console.warn('refs', e); }));
    // optional knock-on dataset from the cascade model (spec in the story section); absent today on most runs
    if (!WHATIF) jobs.push(getJson(base + 'cascade.json').then(function (c) { cascade = c; }).catch(function () { cascade = null; }));
    if (!WHATIF && runKey === 'leominster_sep2023') jobs.push(getJson(WI + 'index.json').then(function (ix) {   // same 20 km box as the what-if runs
      return getBitmap(WI + ix.terrain.sheet).then(function (im) { flowLayer.setChannels(im); });
    }).catch(function () {}));
    if (WION) { /* flow comes with each scenario (wiLoadJobs) */ } else if (meta.flow) {
      jobs.push(getJson(base + meta.flow).then(function (fi) {
        return getBitmap(base + (fi.sheets ? fi.sheets[0] : fi.sheet)).then(function (img) {
          flowLayer.set(fi, img, base);
          whenStyle(function () { map.addLayer(flowLayer.layer, 'l-voy'); vis('flow', $('lyFlow').checked); });
          $('flowRow').hidden = $('flowKey').hidden = false;
        });
      }).catch(function (e) { console.warn('flow', e); }));
    } else $('flowSoon').hidden = false;
    Promise.all(jobs).then(function () {
      ready = true;
      $('loading').classList.add('done');
      $('play').disabled = false;
      if (!WHATIF) { try { addKnock(); } catch (e) { console.error('knock-on', e); } }
      try { addLabels(); } catch (e) { console.error('labels', e); }
      $('slMode').textContent = WHATIF ? 'What-if · not a forecast · ' : runKey === 'forecast' ? 'Forecast · ' : '';
      loadCascadeNumbers().then(function (c) { instInit(); return loadEvidence(c); }).then(function () { if (refs && refs.crowd && refs.crowd.length) { try { addCrowd(); raiseLabels(); } catch (e) { console.error('crowd', e); } } });
      if (WION) wiApply(wi.first, wi.dj, true); else if (WHATIF) { wiPhases(); wiSelect(); } else wiPhases();
      try { rankBuild(); } catch (e) { console.error('rank', e); }
      setTime(t);
      if (storyWanted()) storyStart(0); else refit();
      if (!WHATIF && runKey !== 'forecast' && $('tourLink')) { $('tourLink').href = '?run=' + runKey + '&tour=1'; $('tourLink').hidden = false; }
    }).catch(function (e) { $('loadText').textContent = 'Some storm data did not load. Reload the page to try again.'; console.error(e); });
  }

  // ---------- roads ----------
  function addRoads(g) {
    g.features.forEach(function (f) {
      var p = f.properties;
      if (p.d || p.iv || p.e || WION) { var sg = { id: f.id, d: p.d || (WION ? [] : null), iv: p.iv || [], e: p.e || null, v: -1, f: f }; segs.push(sg); segById[f.id] = sg; }
    });
    map.addSource('roads', { type: 'geojson', data: g, tolerance: 0.2 });
    var RS = 'roads';
    if (PCS) { // road state drawn per ~40 m piece, only where the map shows water on the piece (pieces.json)
      map.addSource('pieces', { type: 'geojson', data: { type: 'FeatureCollection', features: PCS.seg.map(function (sid, i) { return { type: 'Feature', id: i, properties: { s: sid }, geometry: { type: 'LineString', coordinates: PCS.lines[i] } }; }) }, tolerance: 0.2 });
      RS = 'pieces'; PCS.v = new Int16Array(PCS.seg.length).fill(-1); PCS.e = new Int8Array(PCS.seg.length).fill(-1);
      PCS.bySeg = {}; PCS.seg.forEach(function (sid, i) { (PCS.bySeg[sid] = PCS.bySeg[sid] || []).push(i); });
    }
    // the model box, a quiet dashed outline so the replayed area reads at regional zoom
    map.addSource('boxsrc', { type: 'geojson', data: { type: 'Feature', properties: {}, geometry: { type: 'LineString', coordinates: meta.corners.concat([meta.corners[0]]) } } });
    map.addLayer({ id: 'box', type: 'line', source: 'boxsrc', paint: { 'line-width': 1.4, 'line-dasharray': [3, 2], 'line-opacity': ['interpolate', ['linear'], ['zoom'], 9, 0.75, 13, 0.25] } });
    var w = function (a, b) { return ['interpolate', ['linear'], ['zoom'], 9, a, 15, b]; };
    var D = PCS ? ['coalesce', ['get', 'd'], 0] : ['coalesce', ['feature-state', 'd'], 0]; RD = D;
    var RR = RS; // the road-state lines: with pieces, merged runs of the painted pieces of each segment (one continuous line per run)
    if (PCS) {
      map.addSource('runs', { type: 'geojson', data: { type: 'FeatureCollection', features: [] }, tolerance: 0.2 }); RR = 'runs';
      map.addSource('rlab', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
    }
    var byD = function (z9, z15) { // width grows with water on the road, scaled by zoom
      return ['interpolate', ['linear'], ['zoom'], 9, ['interpolate', ['linear'], D, 0, z9[0], 30, z9[1], 100, z9[2]], 15, ['interpolate', ['linear'], D, 0, z15[0], 30, z15[1], 100, z15[2]]];
    };
    var HASW = ['any', ['has', 'd'], ['has', 'iv']];
    // overview zooms show closed roads only; at-risk (15-30 cm) appears from z13, water on the road from z14
    var ZOP = ['interpolate', ['linear'], ['zoom'], 12.6, ['case', ['>=', D, 30], 1, 0], 13.2, ['case', ['>=', D, 15], 1, 0], 13.8, ['case', ['>=', D, 15], 1, 0], 14.3, ['case', ['>=', D, 4], 1, 0]];
    // water at the road edge: a soft water-blue band along the road, under the road-state lines
    // water at the road edge: a thin dashed amber line (the road surface stays above the water), from street zoom
    map.addLayer({ id: 'edge', type: 'line', source: RS, minzoom: 13.5, layout: { 'line-cap': 'butt', 'line-join': 'round' },
      paint: { 'line-width': w(1.2, 2.6), 'line-color': '#E69F00', 'line-dasharray': [1.2, 1.6], 'line-opacity': ['case', ['==', ['coalesce', ['feature-state', 'e'], 0], 1], 0.95, 0] } });
    map.addLayer({ id: 'peak', type: 'line', source: 'roads', filter: ['>=', ['get', 'p'], 0.5], layout: { 'line-cap': 'round' }, paint: { 'line-width': w(1, 2.5) } });
    if (meta.kofn) { // forecast ensemble: how many of the time-lagged forecast runs close the road (likely >= 2, possible 1)
      map.addLayer({ id: 'agree', type: 'line', source: 'roads', filter: ['has', 'k'], layout: { 'line-cap': 'round' }, paint: { 'line-width': w(2, 5), 'line-opacity': 0.9 } });
      kofnLegend();
    }
    map.addLayer({ id: 'may', type: 'line', source: 'roads', filter: ['==', ['get', 'm'], 1], paint: { 'line-width': w(1.5, 3.5), 'line-dasharray': [2, 1.2] } });
    map.addLayer({ id: 'risk', type: 'line', source: 'roads', filter: ['has', 'rk'], layout: { visibility: 'none', 'line-cap': 'round' }, paint: { 'line-width': w(2.5, 6) } });
    map.addLayer({ id: 'halo', type: 'line', source: RR, filter: PCS ? ['has', 'd'] : HASW, layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: { 'line-width': byD([0, 7, 9], [0, 18, 22]), 'line-blur': w(3, 8), 'line-opacity': ['interpolate', ['linear'], D, 22, 0, 40, 0.28] } });
    map.addLayer({ id: 'wetcase', type: 'line', source: RR, filter: PCS ? ['has', 'd'] : HASW, layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: { 'line-width': byD([2.8, 3.8, 4.6], [7.4, 10.4, 11.8]), 'line-opacity': ZOP } });
    map.addLayer({ id: 'wet', type: 'line', source: RR, filter: PCS ? ['has', 'd'] : HASW, layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: { 'line-width': byD([1.6, 2.4, 3], [4.4, 7.2, 8.2]), 'line-opacity': ZOP } });
    // closed: white barricade stripes inside the red line, only where the water is 30 cm or more
    map.addLayer({ id: 'bar', type: 'line', source: RR, filter: PCS ? ['has', 'd'] : HASW, layout: { 'line-cap': 'butt', 'line-join': 'round' },
      paint: { 'line-width': byD([0, 0.9, 1.1], [0, 2.7, 3.1]), 'line-dasharray': [1.4, 1.6], 'line-opacity': ['case', ['>=', D, 30], 0.95, 0] } });
    // the selected road: an ink outline under the road-state lines at every zoom, so the selection never disappears when zooming out
    map.addLayer({ id: 'sel', type: 'line', source: 'roads', filter: ['==', ['id'], -1], layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: { 'line-width': w(6, 14), 'line-color': '#1F2328', 'line-opacity': 0.85 } }, 'halo');
    map.addLayer({ id: 'hit', type: 'line', source: 'roads', paint: { 'line-width': 16, 'line-opacity': 0 } });
    if (PCS) { // the flooded street's own name (MassDOT inventory) beside it, from z12: closed first, at risk from z13, water on road from z14
      [['rlab-w', ['all', ['>=', ['get', 'd'], 5], ['<', ['get', 'd'], 15]], 14], ['rlab-r', ['all', ['>=', ['get', 'd'], 15], ['<', ['get', 'd'], 30]], 13], ['rlab-c', ['>=', ['get', 'd'], 30], 12]].forEach(function (a) {
        map.addLayer({ id: a[0], type: 'symbol', source: 'rlab', filter: a[1], minzoom: a[2],
          layout: { 'text-field': ['get', 't'], 'text-font': ['Noto Sans Bold'], 'text-size': ['interpolate', ['linear'], ['zoom'], 12, 11, 16, 13], 'text-allow-overlap': false,
            'text-variable-anchor': ['top', 'bottom', 'left', 'right'], 'text-radial-offset': 0.7, 'text-padding': 3, 'text-max-width': 14, 'symbol-sort-key': ['-', 0, ['get', 'd']] },
          paint: { 'text-halo-width': 2 } });
      });
    }
    vis('peak', $('lyPeak').checked); vis('may', $('lyMay').checked); // static peak-based layers: off by default, they mark roads that may be dry now
    applyTheme();
    if (g.features.some(function (f) { return f.properties.rk; })) { $('riskRow').hidden = false; }
    map.on('mouseenter', 'hit', function () { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', 'hit', function () { map.getCanvas().style.cursor = ''; hideTip(); });
    map.on('mousemove', 'hit', function (e) {
      if (small() || !e.features.length) return;
      var f = pickRoad(e.features);
      rtipId = f.id; rtipLL = e.lngLat;
      if (!rtip) rtip = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 14, className: 'tip', maxWidth: '240px' });
      rtip.setLngLat(e.lngLat).setHTML(roadTip(f)).addTo(map);
    });
    map.on('click', 'hit', function (e) {
      if (map.queryRenderedFeatures(e.point, { layers: refLayers.filter(function (l) { return map.getLayer(l); }) }).length) return;
      hideTip();
      openPlace(pickRoad(e.features), e.lngLat);
    });
    computeViews(g);
  }
  function pickRoad(fs) {
    var vis_ = fs.filter(function (f) {
      var p = f.properties; return p.p >= 0.5 || p.m === 1 || (p.rk && $('lyRisk').checked) || p.d || p.k;
    });
    return (vis_.length ? vis_ : fs).slice().sort(function (a, b) { return (segDepth(b.id) - segDepth(a.id)) || (b.properties.p - a.properties.p); })[0];
  }
  function hideTip() { if (rtip) rtip.remove(); rtipId = null; }
  function segDepth(id) { var s = segById[id]; return s ? Math.max(0, s.v) : 0; }
  function status(cm, id) { var s = segById[id]; return cm >= 30 ? ['shut', 'Closed'] : cm >= 3 ? ['wet', 'Water on road'] : s && s.eg ? ['edge', 'Water at the road edge; the road surface is above it'] : ['dry', 'Dry']; }
  function roadTip(f) {
    var p = f.properties, cm = segDepth(f.id), st = status(cm, f.id);
    return '<b>' + esc(p.n || 'Unnamed road') + '</b>' + (p.t ? '<br>' + esc(p.t) : '') +
      '<br>Water now: <b>' + (cm >= 3 ? cm + ' cm' : 'none') + '</b><br><span class="st ' + st[0] + '">' + st[1] + '</span>' +
      (small() ? '' : '<br><span style="color:var(--muted)">Click for depth over time</span>');
  }
  // depth on the road over the whole replay: blue area, red where 30 cm or more, dashed closure line, live cursor
  function spark(d) {
    if (!d || !d.length) return '';
    // x range: the wet part of the storm for this road (2 h either side, at least 8 h), so the rise and fall are legible
    var per = 60 / meta.frame_min, N = nf - 1, i0 = 0, i1 = d.length - 1;
    while (i0 < i1 && d[i0] < 3) i0++;
    var x0 = Math.max(0, i0 - 2 * per), x1 = Math.min(N, Math.max(i1 + 2 * per, x0 + 8 * per)); x0 = Math.max(0, Math.min(x0, x1 - 8 * per));
    var W = 260, H = 60, pk = Math.max.apply(0, d), mx = Math.max(45, pk);
    var x = function (i) { return ((i - x0) / (x1 - x0) * W).toFixed(1); }, y = function (v) { return (H - v / mx * (H - 4)).toFixed(1); };
    var idx = []; for (var k = Math.floor(x0); k <= Math.min(d.length - 1, Math.ceil(x1)); k++) idx.push(k);
    var pts = idx.map(function (i) { return x(i) + ',' + y(d[i] || 0); }).join(' ');
    var red = '', run = [], flush = function () { if (run.length) red += '<polyline points="' + run.join(' ') + '" fill="none" stroke="' + css('--closed') + '" stroke-width="2.4"/>'; run = []; };
    idx.forEach(function (i) { if (d[i] >= 30) run.push(x(i) + ',' + y(d[i])); else flush(); }); flush();
    var last = x(idx[idx.length - 1]);
    sparkRange = [x0, x1];
    return '<div class="spk"><svg viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" role="img" aria-label="Water depth on this road through the storm">' +
      '<polygon points="' + x(idx[0]) + ',' + H + ' ' + pts + ' ' + last + ',' + H + '" fill="' + css('--mod') + '" fill-opacity=".22"/>' +
      '<polyline points="' + pts + '" fill="none" stroke="' + css('--mod') + '" stroke-width="1.6"/>' + red +
      '<line x1="0" x2="' + W + '" y1="' + y(30) + '" y2="' + y(30) + '" stroke="' + css('--closed') + '" stroke-dasharray="3 3" stroke-width="1"/>' +
      '<text x="' + (W - 2) + '" y="' + (+y(30) - 3) + '" text-anchor="end" font-size="9.5" fill="' + css('--closed') + '">closed at 30 cm</text>' +
      '<line id="spkCur" x1="' + x(t) + '" x2="' + x(t) + '" y1="0" y2="' + H + '" stroke="' + css('--ink') + '" stroke-width="1.5"' + (t < x0 || t > x1 ? ' visibility="hidden"' : '') + '/></svg>' +
      '<div class="cap"><span>' + fmtShort.format(timeAt(x0)) + '</span><span>peak ' + pk + (pk >= 255 ? '+' : '') + ' cm</span><span>' + fmtShort.format(timeAt(x1)) + '</span></div></div>';
  }

  function kofnLegend() {
    var lb = $('legendBody'); if (!lb || $('kofnKey')) return;
    var k = document.createElement('div'); k.id = 'kofnKey'; k.className = 'grp kofn';
    k.innerHTML = '<h2>Forecast agreement</h2><label class="row"><input type="checkbox" id="lyAgree" checked><span>Roads closed in the ' + meta.kofn.n + ' forecast runs</span></label>' +
      '<p class="note"><i style="display:inline-block;width:18px;height:4px;border-radius:2px;vertical-align:middle;background:var(--closed)"></i> likely closed: 2 or more of ' + meta.kofn.n + ' agree<br>' +
      '<i style="display:inline-block;width:18px;height:4px;border-radius:2px;vertical-align:middle;background:var(--amber)"></i> possible: 1 of ' + meta.kofn.n +
      '<br>Runs from this and the 7 previous HRRR forecasts; the replay shows this forecast\'s run.</p>';
    var gs = lb.querySelectorAll('.grp'); lb.insertBefore(k, gs.length > 2 ? gs[2] : null);
    $('lyAgree').addEventListener('change', function () { vis('agree', this.checked); });
  }
  function showPopup(ll, html) {
    if (popup) popup.remove();
    if (hover) hover.remove();
    popup = new maplibregl.Popup({ maxWidth: '300px' }).setLngLat(ll).setHTML(html).addTo(map);
  }

  var CLS = ['Local or collector road', 'Arterial', 'Highway'];
  function likely(p) { var v = Math.round(p * 100); return (p >= 0.7 ? 'Likely' : p >= 0.3 ? 'Possible' : 'Unlikely') + ' · ' + v + '%'; }
  function arr(v) { return v ? (typeof v === 'string' ? JSON.parse(v) : v) : null; }
  // the named streets at the two ends of a road segment (OpenStreetMap names in the vector tiles), excluding the road itself
  function crossStreets(f) {
    if (!map.getLayer('net-q')) return [];
    var g = f.geometry, cs = g.type === 'LineString' ? g.coordinates : [].concat.apply([], g.coordinates), own = String(f.properties.n || '').toLowerCase(), out = [];
    [cs[0], cs[cs.length - 1]].forEach(function (c) {
      var p = map.project(c), hits = map.queryRenderedFeatures([[p.x - 14, p.y - 14], [p.x + 14, p.y + 14]], { layers: ['net-q'] });
      for (var i = 0; i < hits.length; i++) {
        var nm = hits[i].properties.name; if (!nm) continue;
        var l = nm.toLowerCase(); if (l === own || own.indexOf(l) >= 0 || l.indexOf(own) >= 0 && own) continue;
        if (out.indexOf(nm) < 0) { out.push(nm); break; }
      }
    });
    return out;
  }
  function segLen(f) { // metres along the drawn geometry
    var g = f.geometry; if (!g) return 0; var L = g.type === 'LineString' ? [g.coordinates] : g.coordinates, m = 0;
    L.forEach(function (cs) { for (var i = 1; i < cs.length; i++) { var a = cs[i - 1], b = cs[i], k = Math.cos((a[1] + b[1]) / 2 * Math.PI / 180);
      m += Math.hypot((b[0] - a[0]) * 111320 * k, (b[1] - a[1]) * 110540); } });
    return m;
  }
  function popupHtml(f, ends) {
    var p = f.properties, iv = arr(p.iv), a = arr(p.a), rc = arr(p.rc), d = arr(p.d);
    var h = '<div class="pp"><h3>' + esc(p.n || 'Unnamed road') + '</h3><p class="sub">' + esc(p.t ? p.t + ', ' : '') + CLS[p.c || 0] +
      (ends && ends.length ? (ends.length > 1 ? ', between ' + esc(ends[0]) + ' and ' + esc(ends[1]) : ', at ' + esc(ends[0])) : '') + '</p>' + spark(d) + '<dl>';
    if (p.k) h += '<dt>Forecast runs closing it</dt><dd><b>' + p.k + ' of ' + meta.kofn.n + '</b> (' + (p.k >= 2 ? 'likely closed' : 'possible') + ')</dd>';
    h += '<dt>' + (p.k ? 'Chance of closing, run shown' : 'Chance of closing') + '</dt><dd><b>' + likely(p.p) + '</b></dd>';
    if (d) {
      var fa = Math.min(Math.floor(t), nf - 1), now = Math.round(((d[fa] || 0) * (1 - (t - fa)) + (d[fa + 1] || 0) * (t - fa)));
      h += '<dt>Water on it now</dt><dd id="ppNow" data-id="' + f.id + '">' + (now >= 3 ? now + ' cm' : 'dry') + '</dd>';
    }
    if (d && d.length) {
      var pk = 0; for (var q = 1; q < d.length; q++) if ((d[q] || 0) > (d[pk] || 0)) pk = q;
      var pm = (d[pk] || 0) / 100;
      if (pm >= 0.03) h += '<dt>Peak depth</dt><dd><b>' + (d[pk] >= 255 ? '2.5 m+' : pm.toFixed(2) + ' m') + '</b> (' + (d[pk] >= 255 ? '8 ft+' : (pm * 3.281).toFixed(1) + ' ft') + ') at ' + fmtShort.format(timeAt(pk)) + '</dd>';
    }
    if (iv && iv.length) {
      var s = iv[0][0], e = iv[iv.length - 1][1], dur = 0; iv.forEach(function (x) { dur += x[1] - x[0]; });
      var hm = function (fr) { var m = Math.round(fr * meta.frame_min); return Math.floor(m / 60) + ' h ' + String(m % 60).padStart(2, '0') + ' min'; };
      h += '<dt>Closed</dt><dd>' + fmtShort.format(timeAt(s)) + '</dd>';
      h += '<dt>Reopens</dt><dd>' + (e >= nf - 1 ? 'still closed at the end of the ' + Math.round((nf - 1) * meta.frame_min / 60) + ' h run' : fmtShort.format(timeAt(e))) + '</dd>';
      h += '<dt>Time closed</dt><dd>' + hm(dur) + (e >= nf - 1 ? '+' : '') + '</dd>';
    }
    var len = segLen(f); if (len) h += '<dt>Segment</dt><dd>' + (len / 1609.34).toFixed(2) + ' mi (' + Math.round(len) + ' m) · id ' + f.id + '</dd>';
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
  var refLayers = ['r-crossings', 'r-bridges', 'r-dams', 'r-facilities', 'r-reports', 'r-crowd', 'r-gauges'];
  var ICONS = {
    gauge: function (c, s) { c.fillStyle = '#0b7a75'; c.beginPath(); c.moveTo(s / 2, 2); c.lineTo(s - 2, s - 3); c.lineTo(2, s - 3); c.closePath(); c.fill(); c.stroke(); },
    culvert: function (c, s) { c.fillStyle = '#8a5a2b'; c.beginPath(); c.arc(s / 2, s / 2, s / 2 - 3, 0, 7); c.fill(); c.stroke(); c.fillStyle = '#fff'; c.beginPath(); c.arc(s / 2, s / 2, s / 5, 0, 7); c.fill(); },
    culvertRisk: function (c, s) { c.fillStyle = '#c0392b'; c.beginPath(); c.arc(s / 2, s / 2, s / 2 - 2, 0, 7); c.fill(); c.stroke(); c.fillStyle = '#fff'; c.beginPath(); c.arc(s / 2, s / 2, s / 5, 0, 7); c.fill(); },
    bridge: function (c, s) { c.fillStyle = '#4b5966'; rr(c, 2, s * 0.3, s - 4, s * 0.4, 3); c.fill(); c.stroke(); },
    dam: function (c, s) { c.fillStyle = '#3d5a80'; c.beginPath(); c.moveTo(3, s - 3); c.lineTo(s * 0.38, 3); c.lineTo(s * 0.62, 3); c.lineTo(s - 3, s - 3); c.closePath(); c.fill(); c.stroke(); },
    hospital: function (c, s) { c.fillStyle = '#d6223a'; rr(c, 2, 2, s - 4, s - 4, 4); c.fill(); c.stroke(); cross(c, s); },
    fire: function (c, s) { c.fillStyle = '#e8590c'; rr(c, 2, 2, s - 4, s - 4, 4); c.fill(); c.stroke(); letter(c, s, 'F'); },
    police: function (c, s) { c.fillStyle = '#1c4e9c'; rr(c, 2, 2, s - 4, s - 4, 4); c.fill(); c.stroke(); letter(c, s, 'P'); },
    ring: function (c, s) { c.fillStyle = 'rgba(200,16,46,.16)'; c.strokeStyle = '#c8102e'; c.lineWidth = s / 9; c.beginPath(); c.arc(s / 2, s / 2, s / 2 - 3, 0, 7); c.fill(); c.stroke(); },
    repHit: function (c, s) { c.fillStyle = '#1F2328'; tri(c, s); c.fill(); c.stroke(); },
    repMiss: function (c, s) { c.fillStyle = '#FFFFFF'; tri(c, s); c.fill(); c.strokeStyle = '#1F2328'; c.lineWidth = s / 8; c.stroke(); },
    pin: function (c, s) { c.fillStyle = '#1F2328'; dia(c, s); c.fill(); c.stroke(); },
    pinHit: function (c, s) { c.fillStyle = '#1F2328'; dia(c, s); c.fill(); c.stroke(); },
    pinMiss: function (c, s) { c.fillStyle = '#FFFFFF'; dia(c, s); c.fill(); c.strokeStyle = '#1F2328'; c.lineWidth = s / 8; c.stroke(); },
    report: function (c, s) { c.fillStyle = '#6f2dbd'; c.beginPath(); c.moveTo(s / 2, s - 2); c.arc(s / 2, s * 0.4, s * 0.34, Math.PI * 0.8, Math.PI * 2.2); c.closePath(); c.fill(); c.stroke(); c.fillStyle = '#fff'; c.beginPath(); c.arc(s / 2, s * 0.4, s * 0.13, 0, 7); c.fill(); }
  };
  function tri(c, s) { c.beginPath(); c.moveTo(s / 2, 3); c.lineTo(s - 3, s - 4); c.lineTo(3, s - 4); c.closePath(); }
  function dia(c, s) { c.beginPath(); c.moveTo(s / 2, 3); c.lineTo(s - 4, s / 2); c.lineTo(s / 2, s - 3); c.lineTo(4, s / 2); c.closePath(); }
  function rr(c, x, y, w, h, r) { c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
  function cross(c, s) { c.fillStyle = '#fff'; var a = s * 0.18, b = s * 0.56; c.fillRect(s / 2 - a / 2, s / 2 - b / 2, a, b); c.fillRect(s / 2 - b / 2, s / 2 - a / 2, b, a); }
  function letter(c, s, L) { c.fillStyle = '#fff'; c.font = '800 ' + Math.round(s * 0.62) + 'px -apple-system, BlinkMacSystemFont, Roboto, system-ui, sans-serif'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(L, s / 2, s / 2 + 1); }
  function iconCanvas(name, s) {
    var cv = document.createElement('canvas'); cv.width = cv.height = s; var c = cv.getContext('2d');
    c.strokeStyle = 'rgba(255,255,255,.95)'; c.lineWidth = Math.max(1.5, s / 14); c.lineJoin = 'round'; ICONS[name](c, s); return cv;
  }
  document.querySelectorAll('.ico').forEach(function (el) { var cv = iconCanvas(el.dataset.ico, 32); cv.setAttribute('aria-hidden', 'true'); el.appendChild(cv); });

  function fc(rows, fn) { return { type: 'FeatureCollection', features: rows.map(function (r, i) { var p = fn(r); return { type: 'Feature', id: i, properties: p, geometry: { type: 'Point', coordinates: [r[0], r[1]] } }; }) }; }
  // reports cluster (40 px) until street zoom: a purple bubble with the count; tap to zoom in
  function addClusters(key) {
    var on = document.querySelector('input[data-ref="' + key + '"]').checked ? 'visible' : 'none';
    map.addLayer({ id: 'c-' + key, type: 'circle', source: 's-' + key, filter: ['has', 'point_count'], minzoom: 11, layout: { visibility: on },
      paint: { 'circle-color': '#1F2328', 'circle-radius': ['interpolate', ['linear'], ['get', 'point_count'], 2, 8, 30, 13], 'circle-stroke-color': '#fff', 'circle-stroke-width': 1.5, 'circle-opacity': 0.8 } });
    map.addLayer({ id: 'c-' + key + '-n', type: 'symbol', source: 's-' + key, filter: ['has', 'point_count'], minzoom: 11,
      layout: { visibility: on, 'text-field': ['to-string', ['get', 'point_count']], 'text-font': ['Noto Sans Bold'], 'text-size': 10.5, 'text-allow-overlap': true }, paint: { 'text-color': '#fff' } });
    map.on('click', 'c-' + key, function (e) { map.easeTo({ center: e.features[0].geometry.coordinates, zoom: Math.min(15.5, map.getZoom() + 2) }); });
    map.on('mouseenter', 'c-' + key, function () { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', 'c-' + key, function () { map.getCanvas().style.cursor = ''; });
  }
  function addCrowd() {
    if (map.getSource('s-crowd')) return;
    var data = fc(refs.crowd, function (r) { return { k: WHATIF ? 'pin' : r[6] >= 3 ? 'pinHit' : 'pinMiss', type: r[2], text: r[3], road: r[4], town: r[5], c: r[6] }; });
    if (!map.hasImage('i-pin')) Object.keys(ICONS).forEach(function (k) { if (!map.hasImage('i-' + k)) { var cv = iconCanvas(k, 40); map.addImage('i-' + k, cv.getContext('2d').getImageData(0, 0, 40, 40), { pixelRatio: 2 }); } });
    map.addSource('s-crowd', { type: 'geojson', data: data, cluster: true, clusterRadius: 40, clusterMaxZoom: 14 });
    addClusters('crowd');
    var on = document.querySelector('input[data-ref="crowd"]').checked;
    map.addLayer({ id: 'r-crowd', type: 'symbol', source: 's-crowd', minzoom: 11, filter: ['!', ['has', 'point_count']], layout: { 'icon-image': ['concat', 'i-', ['get', 'k']], 'icon-size': 0.62, 'icon-allow-overlap': true, visibility: on ? 'visible' : 'none' } });
    document.querySelector('label[data-ref="crowd"]').hidden = false;
    map.on('mouseenter', 'r-crowd', function (e) {
      map.getCanvas().style.cursor = 'pointer'; if (small()) return; if (hover) hover.remove();
      hover = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 10, className: 'tip' }).setLngLat(e.features[0].geometry.coordinates).setHTML(refTip('crowd', e.features[0].properties)).addTo(map);
    });
    map.on('mouseleave', 'r-crowd', function () { map.getCanvas().style.cursor = ''; if (hover) { hover.remove(); hover = null; } });
    map.on('click', 'r-crowd', function (e) { showPopup(e.features[0].geometry.coordinates, refHtml('crowd', e.features[0].properties)); });
    if (!WHATIF) refVis('reports', true);
  }
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
      reports: R.reports && R.reports.length ? fc(R.reports, function (r) { return { k: r[6] ? 'repHit' : 'repMiss', src: r[2], text: r[3], t: r[4], m: r[5], hit: r[6] }; }) : null,
      crowd: null // added later with the evidence file (addCrowd)
    };
    var minz = { crossings: 11, bridges: 11.5, dams: 9, facilities: 10, reports: 12, crowd: 12, gauges: 6 };
    ['crossings', 'bridges', 'dams', 'facilities', 'crowd', 'reports', 'gauges'].forEach(function (key) {
      if (!sets[key]) return;
      document.querySelector('label[data-ref="' + key + '"]').hidden = false;
      var clu = key === 'reports';
      map.addSource('s-' + key, clu ? { type: 'geojson', data: sets[key], cluster: true, clusterRadius: 40, clusterMaxZoom: 14 } : { type: 'geojson', data: sets[key] });
      if (clu) addClusters(key);
      map.addLayer({ id: 'r-' + key, type: 'symbol', source: 's-' + key, filter: clu ? ['!', ['has', 'point_count']] : ['==', 1, 1], minzoom: runKey === 'd3_sep2023' ? minz[key] + 1 : minz[key] - 1,
        layout: { 'icon-image': ['concat', 'i-', ['get', 'k']], 'icon-size': key === 'gauges' ? 1.15 : key === 'crossings' ? ['case', ['==', ['get', 'k'], 'culvertRisk'], 0.85, 0.65] : 0.8,
          'icon-allow-overlap': key === 'gauges' || key === 'reports' || key === 'crowd', 'icon-ignore-placement': key !== 'crossings', 'symbol-sort-key': key === 'crossings' ? ['case', ['==', ['get', 'k'], 'culvertRisk'], 0, 1] : 0,
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
      $('gaugeBand').hidden = WHATIF && small(); // phones: the what-if panel needs the room
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
    if (key === 'crowd') return '<b>Resident report: ' + esc(CROWD[p.type] || p.type) + '</b><br>' + esc((p.text || '').slice(0, 90)) + (WHATIF ? '' : '<br>' + crowdVerdict(p.c));
    return '<b>' + esc(KIND.report[p.src] || p.src) + '</b><br>' + esc((p.text || '').slice(0, 80)) + (WHATIF ? '' : '<br>' + (p.hit ? '<span class="ok">Model: 30 cm or more nearby</span>' : '<span class="miss">Model: under 30 cm here</span>'));
  }
  var CROWD = { washout: 'washout or roadway damage', flooded: 'high or deep water', impassable: 'road impassable', swift: 'swift water', closed: 'road closed', other_damage: 'damage' };
  function crowdVerdict(c) { return c >= 3 ? '<span class="ok">Model: 30 cm or more within 50 m</span>' : c >= 1 ? '<span class="miss">Model: some water nearby, under 30 cm</span>' : '<span class="miss">Model: dry here</span>'; }
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
    } else if (key === 'crowd') {
      h += '<h3>' + esc(p.road || p.town || 'Resident report') + '</h3><p class="sub">Resident report, ' + esc(CROWD[p.type] || p.type) + ', Sept 11, 2023</p><p>' + esc(p.text) + '</p>' +
        (WHATIF ? '' : '<p>' + crowdVerdict(p.c) + '</p>') + '<p class="why">MRPC / BSC Group Leominster crowdsource map. Pins are placed by residents, so positions are approximate.</p>';
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
    if (map && !map.getSource('hot')) { // overview zooms: one quiet label per hotspot instead of every road
      map.addSource('hot', { type: 'geojson', data: { type: 'FeatureCollection', features: hs.map(function (h) {
        // one line, placed just above the hotspot (not on its roads); it gives way to place labels and other hotspots instead of overlapping
        return { type: 'Feature', properties: { t: h.name + ' · ' + h.count + ' roads close', k: -h.count }, geometry: { type: 'Point', coordinates: [(h.bounds[0][0] + h.bounds[1][0]) / 2, Math.max(h.bounds[0][1], h.bounds[1][1])] } }; }) } });
      map.addLayer({ id: 'hot', type: 'symbol', source: 'hot', maxzoom: 12.8, layout: { 'text-field': ['get', 't'], 'text-font': ['Noto Sans Bold'], 'text-size': 12, 'text-allow-overlap': false, 'text-ignore-placement': false,
        'symbol-sort-key': ['get', 'k'], 'text-variable-anchor': ['bottom', 'top', 'left', 'right'], 'text-radial-offset': 0.5, 'text-padding': 4 },
        paint: { 'text-color': css('--ink') || '#1F2328', 'text-halo-color': css('--solid') || '#fff', 'text-halo-width': 2, 'text-opacity': ['interpolate', ['linear'], ['zoom'], 12.2, 1, 12.8, 0] } });
    }
    var el = $('views'); el.innerHTML = '';
    views.forEach(function (v, i) {
      var b = document.createElement('button'); b.type = 'button'; b.dataset.view = i;
      b.innerHTML = esc(v.name) + (v.count ? ' <span>' + v.count + '</span>' : '');
      b.title = v.count ? v.count + ' roads close here' : v.hint;
      b.setAttribute('aria-pressed', i === currentView ? 'true' : 'false');
      b.addEventListener('click', function () { if (story.on) storyEnd(); setFollow(false); fitView(i, true); });
      el.appendChild(b);
    });
    var lab = document.createElement('label'); lab.className = 'follow';
    lab.innerHTML = '<input type="checkbox" id="follow"><span>Follow the storm</span>';
    el.appendChild(lab);
    $('follow').addEventListener('change', function (e) { if (story.on) storyEnd(); setFollow(e.target.checked); });
    if (!story.on) workView();
  }
  // the opening camera: a working zoom (about z13.8 desktop, z13.4 phone) on the hotspot where most roads close, so the streets and
  // the flooded streets among them read at once; 'Overview' (one tap, or zoom out) frames the whole story
  var workOn = false;
  var linkView = false;
  function refit() { if (linkView) return; if (workOn) workView(); else fitView(currentView, false); }
  function workView() {
    var lc = (params.get('c') || '').split(',').map(Number), lz = +params.get('z');
    if (lc.length === 2 && isFinite(lc[0]) && isFinite(lc[1]) && lz > 3 && !linkView) { // a shared link: its own view
      linkView = true; userMoved = true; map.jumpTo({ center: lc, zoom: lz });
      var rid = params.get('road'); if (rid && segById[rid]) setTimeout(function () { openPlace(segById[rid].f); }, 400);
      return;
    }
    if (linkView) return;
    workOn = true;
    var bi = -1; views.forEach(function (v, i) { if (v.count && (bi < 0 || v.count > views[bi].count)) bi = i; });
    if (!map || bi < 0) { fitView(0, false); return; }
    currentView = bi; userMoved = false;
    document.querySelectorAll('#views button').forEach(function (b) { b.setAttribute('aria-pressed', +b.dataset.view === bi ? 'true' : 'false'); });
    var ids = {}; (views[bi].ids || []).forEach(function (id) { ids[id] = 1; });
    var sx = 0, sy = 0, sn = 0; // centre on the closing roads themselves, not the middle of the cluster box
    segs.forEach(function (s) { if (!ids[s.id]) return; var g = s.f.geometry, c = g.type === 'LineString' ? g.coordinates : g.coordinates[0]; var m = c[Math.floor(c.length / 2)]; sx += m[0]; sy += m[1]; sn++; });
    var b = views[bi].bounds, ctr = sn ? [sx / sn, sy / sn] : [(b[0][0] + b[1][0]) / 2, (b[0][1] + b[1][1]) / 2];
    var p = framePadding(); // centre the roads in the part of the map the panels leave clear (without leaving a persistent map padding)
    map.jumpTo({ center: ctr, zoom: small() ? 13.4 : 13.8 }); map.panBy([-(p.left - p.right) / 2, -(p.top - p.bottom) / 2], { duration: 0 });
  }
  if (params.get('debug') === '1') window.__mfwView = function (i) { if (i === 'work') workView(); else fitView(i, false); };
  function fitView(i, animate) {
    if (!map || !views[i]) return;
    workOn = false;
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

  // ---------- knock-on effects: places near closing roads, overtopped culverts, and the optional cascade dataset ----------
  /* cascade.json (optional: docs/site/data/<run>/cascade.json, written by the cascade model). Times are replay frame
     indices (float; frame k = meta.storm_start + k * meta.frame_min minutes). Every key is optional.
     {
       "version": 1,
       "summary":    { "headline": "one sentence", "people_cut_off": int, "facilities_affected": int,
                       "max_added_min": number, "detour_km": number, "culverts_failed": int },
       "events":     [ { "t": frame, "lon": x, "lat": y, "kind": "closure|culvert|washout|bridge|cutoff|facility|other",
                         "label": "what happens", "cause": "what set it off" } ],
       "detours":    [ { "t0": frame, "t1": frame, "for": road segment id, "added_min": number, "coords": [[lon, lat], ...] } ],
       "cutoff":     [ { "t0": frame, "t1": frame, "label": "area", "people": int, "ring": [[lon, lat], ...] } ],
       "facilities": [ { "name": "..", "kind": "hospital|fire|police|school|shelter", "lon": x, "lat": y, "t0": frame,
                         "added_min": number, "cut_off": true } ]
     }
     Drawn as: cut-off areas a grey hatch with an ink outline, detours dashed ink lines, events dots that appear at
     their time, facilities circled icons; the summary feeds the last story scene. Without it, the last scene uses the
     run's own numbers (culverts overtopped, roads that may close) and the stations within 500 m of a closing road. */
  var knock = { fac: 0, hosp: 0, fire: 0, police: 0, xing: 0 }, cxFrame = -1;
  function addKnock() {
    var lat0 = (meta.corners[0][1] + meta.corners[2][1]) / 2, kx = 111.32 * Math.cos(lat0 * Math.PI / 180), ky = 110.57;
    var lines = [];
    segs.concat([]).forEach(function (s) {
      var p = s.f.properties; if (!(p.p >= 0.5 || s.iv)) return;
      var g = s.f.geometry, parts = g.type === 'LineString' ? [g.coordinates] : g.coordinates;
      parts.forEach(function (cs) { for (var i = 1; i < cs.length; i++) lines.push([cs[i - 1][0] * kx, cs[i - 1][1] * ky, cs[i][0] * kx, cs[i][1] * ky]); });
    });
    function dist(lon, lat) {
      var px = lon * kx, py = lat * ky, best = 1e9;
      for (var i = 0; i < lines.length; i++) {
        var L = lines[i], dx = L[2] - L[0], dy = L[3] - L[1], q = dx * dx + dy * dy, u = q ? Math.max(0, Math.min(1, ((px - L[0]) * dx + (py - L[1]) * dy) / q)) : 0;
        var ex = L[0] + u * dx - px, ey = L[1] + u * dy - py, d = ex * ex + ey * ey; if (d < best) best = d;
      }
      return Math.sqrt(best);
    }
    var feats = [], R = refs || {}, bb = boxBounds();
    var inBox = function (lon, lat) { return lon >= bb[0][0] && lon <= bb[1][0] && lat >= bb[0][1] && lat <= bb[1][1]; };
    if (cascade && cascade.facilities && cascade.facilities.length) {
      cascade.facilities.forEach(function (f) {
        var k = { hospital: 'hospital', fire: 'fire', police: 'police' }[f.kind] || 'report';
        feats.push({ type: 'Feature', properties: { k: k, name: f.name || '', note: (f.cut_off ? 'Cut off' : '') + (f.added_min ? (f.cut_off ? ', ' : '') + '+' + Math.round(f.added_min) + ' min to reach' : '') }, geometry: { type: 'Point', coordinates: [f.lon, f.lat] } });
        knock.fac++;
      });
    } else if (R.facilities && lines.length) {
      [['hospital', 'hospital'], ['fire_station', 'fire'], ['police', 'police']].forEach(function (kk) {
        (R.facilities[kk[0]] || []).forEach(function (r) {
          if (!inBox(r[0], r[1])) return;
          var d = dist(r[0], r[1]); if (d > 0.5) return;
          feats.push({ type: 'Feature', properties: { k: kk[1], name: r[2] || '', note: Math.round(d * 1000 / 10) * 10 + ' m from a road that closes' }, geometry: { type: 'Point', coordinates: [r[0], r[1]] } });
          knock.fac++; knock[kk[1] === 'fire' ? 'fire' : kk[1] === 'police' ? 'police' : 'hosp']++;
        });
      });
    }
    if (R.crossings && R.crossings.rows) R.crossings.rows.forEach(function (r) {
      if (r[9] != null && r[9] >= 0.5 && inBox(r[0], r[1])) {
        feats.push({ type: 'Feature', properties: { k: 'culvertRisk', name: r[2] || 'Stream crossing', note: Math.round(r[9] * 100) + '% chance the road over it is overtopped' + (r[3] ? ' (' + r[3] + ')' : '') }, geometry: { type: 'Point', coordinates: [r[0], r[1]] } });
        knock.xing++;
      }
    });
    if (!feats.length && !cascade) return;
    if (!map.hasImage('i-hospital')) Object.keys(ICONS).forEach(function (k) { var cv = iconCanvas(k, 40); if (!map.hasImage('i-' + k)) map.addImage('i-' + k, cv.getContext('2d').getImageData(0, 0, 40, 40), { pixelRatio: 2 }); });
    map.addSource('knock', { type: 'geojson', data: { type: 'FeatureCollection', features: feats } });
    var vk = document.querySelector('input[data-ref="knock"]').checked ? 'visible' : 'none';
    map.addLayer({ id: 'knock-ring', type: 'circle', source: 'knock', filter: ['!=', ['get', 'k'], 'culvertRisk'], layout: { visibility: vk },
      paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 9, 9, 14, 16], 'circle-color': css('--closed'), 'circle-opacity': 0.12, 'circle-stroke-color': css('--closed'), 'circle-stroke-width': 1.6 } });
    map.addLayer({ id: 'knock', type: 'symbol', source: 'knock', layout: { visibility: vk, 'icon-image': ['concat', 'i-', ['get', 'k']], 'icon-size': ['case', ['==', ['get', 'k'], 'culvertRisk'], 0.62, 0.85], 'icon-allow-overlap': true, 'symbol-sort-key': ['case', ['==', ['get', 'k'], 'culvertRisk'], 1, 0] } });
    map.on('mouseenter', 'knock', function (e) {
      map.getCanvas().style.cursor = 'pointer'; if (small()) return;
      var p = e.features[0].properties;
      if (hover) hover.remove();
      hover = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 12, className: 'tip' }).setLngLat(e.features[0].geometry.coordinates)
        .setHTML('<b>' + esc(p.name || { hospital: 'Hospital', fire: 'Fire station', police: 'Police station', culvertRisk: 'Culvert' }[p.k]) + '</b><br>' + esc(p.note)).addTo(map);
    });
    map.on('mouseleave', 'knock', function () { map.getCanvas().style.cursor = ''; if (hover) { hover.remove(); hover = null; } });
    document.querySelector('label[data-ref="knock"]').hidden = false;
    if (cascade) addCascade();
  }
  function addCascade() {
    var C = cascade, ink = css('--ink');
    var fcx = function (rows, geom) { return { type: 'FeatureCollection', features: (rows || []).map(function (r, i) { return { type: 'Feature', id: i, properties: { t0: r.t0 != null ? r.t0 : (r.t != null ? r.t : 0), t1: r.t1 != null ? r.t1 : 1e9, label: r.label || r.kind || '', people: r.people || 0, added: r.added_min || 0 }, geometry: geom(r) }; }) }; };
    map.addSource('cx-cut', { type: 'geojson', data: fcx(C.cutoff, function (r) { return { type: 'Polygon', coordinates: [r.ring] }; }) });
    map.addSource('cx-det', { type: 'geojson', data: fcx(C.detours, function (r) { return { type: 'LineString', coordinates: r.coords }; }) });
    map.addSource('cx-ev', { type: 'geojson', data: fcx(C.events, function (r) { return { type: 'Point', coordinates: [r.lon, r.lat] }; }) });
    var before = map.getLayer('peak') ? 'peak' : undefined;
    map.addLayer({ id: 'cx-cut', type: 'fill', source: 'cx-cut', paint: { 'fill-color': ink, 'fill-opacity': 0.1 } }, before);
    map.addLayer({ id: 'cx-cut-line', type: 'line', source: 'cx-cut', paint: { 'line-color': ink, 'line-width': 1.2, 'line-dasharray': [1, 1.5] } }, before);
    map.addLayer({ id: 'cx-det', type: 'line', source: 'cx-det', paint: { 'line-color': ink, 'line-width': ['interpolate', ['linear'], ['zoom'], 9, 1.5, 15, 3.5], 'line-dasharray': [2, 1.5] } });
    map.addLayer({ id: 'cx-ev', type: 'circle', source: 'cx-ev', paint: { 'circle-radius': 5, 'circle-color': css('--closed'), 'circle-stroke-color': '#fff', 'circle-stroke-width': 1.5 } });
    CX_LAYERS.forEach(function (l) { vis(l, document.querySelector('input[data-ref="knock"]').checked); });
    cascadeTime(true);
  }
  var CX_LAYERS = ['cx-cut', 'cx-cut-line', 'cx-det', 'cx-ev'];
  function cascadeTime(force) { // filters change only when the replay crosses a frame, never per animation frame
    if (!map || !map.getLayer('cx-ev')) return;
    var f = Math.floor(t); if (f === cxFrame && !force) return; cxFrame = f;
    var on = ['all', ['<=', ['get', 't0'], t], ['>=', ['get', 't1'], t]];
    CX_LAYERS.forEach(function (l) { map.setFilter(l, l === 'cx-ev' ? ['<=', ['get', 't0'], t] : on); });
  }

  // ---------- story mode ----------
  // six scenes on the real timeline; each plays a stretch of storm time, moves the camera, and sets which layers speak
  var story = { on: false, i: 0, sc: [], start: 0, paused: false, pausedAt: 0, hold: 0, raf: 0 };
  function storyWanted() { return !WHATIF && (params.get('tour') === '1' || params.get('story') === '1') && !document.documentElement.classList.contains('embed'); }
  function sum(a, n) { var s0 = 0; for (var i = 0; i < Math.min(a.length, Math.floor(n)); i++) s0 += a[i] || 0; if (n % 1 && a[Math.floor(n)]) s0 += a[Math.floor(n)] * (n % 1); return s0; }
  function buildScenes() {
    var M = meta, per = 60 / M.frame_min, N = nf - 1, r = M.rain_hourly_mean_mm || [], cp = M.closed_per_frame || [];
    var cl = function (v) { return Math.max(0, Math.min(N, v)); };
    var rmax = Math.max.apply(0, r.concat([0.001])), hS = 0, hP = 0, i;
    for (i = 0; i < r.length; i++) if (r[i] >= 0.15 * rmax) { hS = i; break; }
    for (i = 0; i < r.length; i++) if (r[i] > r[hP]) hP = i;
    var cmax = Math.max.apply(0, cp.concat([0])), fP = 0;
    for (i = 0; i < cp.length; i++) if (cp[i] > cp[fP]) fP = i;
    // first frame at which q of the peak closures are in, searched from the steady rise (not a lone early river crossing)
    var fq = function (q) { for (var k = 0; k <= fP; k++) if (cp[k] >= Math.max(2, q * cmax)) return k; return fP; };
    // flash floods close roads while it is still pouring, so each scene ends on a closure milestone, not on the rain
    var s1a = cl(hS * per - 1.5 * per), s1b = cl(hS * per + 0.5 * per);
    var s2b = cl(Math.max(s1b + 0.5 * per, Math.min((hP + 0.5) * per, fq(0.06))));
    var s3b = cl(Math.max(s2b + 0.25 * per, fq(0.15))), s4b = cl(Math.max(s3b + 0.25 * per, fq(0.55))), s5b = cl(Math.max(s4b + 0.25 * per, fP));
    var place = RUNS[runKey].title.split(' · ')[0].replace(/^What if\? ?/, 'Leominster'), hot = views[1] && views[1].count ? views[1] : null;
    var big = function (v) { return '<b>' + n(v) + '</b>'; };
    var rep_ = (refs && refs.reports) || [], hits = rep_.filter(function (x) { return x[6]; }).length;
    var C = cascade && cascade.summary;
    function rainLive() { var h = t / per, s0 = sum(r, h); return '<b class="rainv">' + s0.toFixed(s0 < 10 ? 1 : 0) + ' mm</b><span>rain so far, averaged over the model area</span>'; }
    var S = [
      { title: 'The storm arrives', a: s1a, b: s1b, dur: 6500, rain: 1, cam: rain ? rain.bounds : null, zoomOut: !rain,
        text: function () { return '<b>' + fmtShort.format(timeAt(s1b)) + '.</b> Radar rain from NOAA MRMS sweeps across central Massachusetts toward ' + esc(place) + '. The dashed outline is the area the flood model covers.'; }, live: rainLive },
      { title: 'Rain intensifies', a: s1b, b: s2b, dur: 7500, rain: 1, cam: 'box',
        text: function () { return 'Up to ' + (M.rain_peak1h_max_mm != null ? '<b>' + M.rain_peak1h_max_mm + ' mm</b>' : 'a month’s rain') + ' falls on one spot in a single hour' + (M.rain_max_total_mm != null ? ', and the wettest place in the area collects <b>' + M.rain_max_total_mm + ' mm</b> over the storm.' : '.'); }, live: rainLive },
      { title: 'Runoff and rising brooks', a: s2b, b: s3b, dur: 8000, rain: 0.55, cam: hot ? 1 : 0,
        text: function () { return 'Rain the ground cannot take runs off down streets and slopes into the brooks' + (meta.flow ? ' (the moving particles follow the modelled current)' : '') + '. Brooks and rivers swell and ponds fill: their outlines thicken as the river rises. Blue is water at least 5 cm deep, darker is deeper.'; },
        live: function () { return '<b class="blue">' + n(nWet + nClosedNow) + '</b><span>road segments with water on them</span>'; } },
      { title: 'Streets flood', a: s3b, b: s4b, dur: 7500, rain: 0.3, cam: hot ? 1 : 0,
        text: function () { return 'Where water reaches a road it turns <b>amber</b>: water on the road, still under 30 cm.' + (hot ? ' Around ' + esc(hot.name) + ', ' + big(hot.count) + ' road segments flood during the storm.' : ''); },
        live: function () { return '<b class="wet">' + n(nWet) + '</b><span>roads with water</span><b class="shut">' + n(nClosedNow) + '</b><span>closed</span>'; } },
      { title: 'Streets close', a: s4b, b: s5b, dur: 7000, rain: 0.2, cam: 0,
        text: function () {
          return 'At 30 cm a road counts as closed: <b>red with white stripes</b>. At the peak, ' + big(cp[fP] || 0) + ' segments are closed at once' +
            (M.segments_p_ge_50 != null ? ', and ' + big(M.segments_p_ge_50) + ' (' + M.km_p_ge_50 + ' km) close at some point, out of ' + n(M.segments_in_box) + ' in the area.' : '.') +
            (rep_.length ? ' Check: ' + hits + ' of ' + rep_.length + ' storm reports fall where the model has 30 cm or more.' : '');
        },
        live: function () { return '<b class="shut">' + n(nClosedNow) + '</b><span>roads closed now</span>'; } },
      { title: 'Knock-on effects', a: s5b, b: s5b, dur: 0, rain: 0.15, cam: 0, peak: true, may: true, knock: true,
        text: function () {
          if (C) return esc(C.headline || '') + (C.people_cut_off ? ' ' + big(C.people_cut_off) + ' people cut off.' : '') + (C.facilities_affected ? ' ' + big(C.facilities_affected) + ' facilities affected.' : '') +
            (C.max_added_min ? ' Detours add up to <b>' + Math.round(C.max_added_min) + ' min</b>.' : '');
          var bits = [];
          if (M.culverts_overtopped) bits.push(big(M.culverts_overtopped) + ' culverts are overtopped');
          if (M.segments_may_close) bits.push(big(M.segments_may_close) + ' more segments may close where streams reach road level (dashed)');
          if (knock.fac) bits.push(big(knock.fac) + (knock.fac > 1 ? ' hospitals, fire and police stations sit' : ' emergency station sits') + ' within 500 m of a closing road (circled)');
          var list = bits.length > 1 ? bits.slice(0, -1).join('; ') + '; and ' + bits[bits.length - 1] : bits.join('');
          return 'Closed roads cut routes around them. ' + (list ? list + '.' : '') + ' Faint red lines mark every road that closes at some point.';
        },
        live: function () { return M.segments_p_ge_50 != null ? '<b class="shut">' + n(M.segments_p_ge_50) + '</b><span>roads close at some point</span>' + (knock.fac ? '<b class="shut">' + knock.fac + '</b><span>stations near them</span>' : '') : ''; } },
      { title: 'Draining and soaking in', a: s5b, b: cl(s5b + 8 * per), dur: 9000, rain: 0, cam: hot ? 1 : 0,
        text: function () { return 'The rain stops. Water runs down the brooks to the river and soaks into the ground; <b>slate-grey</b> water is going down, and roads reopen as it drops below 26 cm.' +
          (meta.surface_mm ? ' Of the rain that fell, most has soaked in or drained away (estimate: rain fallen minus the water still drawn on the land).' : ''); },
        live: function () { var per_ = 60 / meta.frame_min, tot = sum(r, t / per_), sf = meta.surface_mm ? meta.surface_mm[Math.round(t)] || 0 : null;
          return sf != null ? '<b class="blue">' + Math.max(0, tot - sf).toFixed(0) + ' mm</b><span>of ' + tot.toFixed(0) + ' mm soaked in or drained</span><b class="shut">' + n(nClosedNow) + '</b><span>still closed</span>' : '<b class="shut">' + n(nClosedNow) + '</b><span>still closed</span>'; } }
    ];
    return S;
  }
  function storyLayers(sc) {
    if (!map) return;
    vis('peak', !!sc.peak); vis('may', !!sc.may); vis('risk', false);
    ['knock', 'knock-ring'].concat(CX_LAYERS).forEach(function (l) { vis(l, !!sc.knock); });
    vis('depth', true); vis('flow', true); vis('rain', true);
    ['wet', 'wetcase', 'halo', 'bar'].forEach(function (l) { vis(l, true); });
  }
  function applyToggles() {
    vis('rain', $('lyRain').checked); vis('depth', $('lyDepth').checked); vis('flow', $('lyFlow').checked);
    ['wet', 'wetcase', 'halo', 'bar'].forEach(function (l) { vis(l, $('lyClosed').checked); });
    vis('peak', $('lyPeak').checked); vis('may', $('lyMay').checked); vis('risk', $('lyRisk').checked);
    document.querySelectorAll('input[data-ref]').forEach(function (x) { refVis(x.dataset.ref, x.checked); });
  }
  function storyCam(sc, first) {
    var dur = first || reduced ? 0 : 2600, opt = { padding: framePadding(), duration: dur, essential: true, maxZoom: 14.5, curve: 1.3 };
    if (sc.cam === 'box') map.fitBounds(boxBounds(), opt);
    else if (Array.isArray(sc.cam)) map.fitBounds(sc.cam, opt);
    else if (sc.zoomOut) { var b = boxBounds(), dx = b[1][0] - b[0][0], dy = b[1][1] - b[0][1]; map.fitBounds([[b[0][0] - dx, b[0][1] - dy], [b[1][0] + dx, b[1][1] + dy]], opt); }
    else if (views[sc.cam]) { map.fitBounds(views[sc.cam].bounds, opt); currentView = sc.cam; }
  }
  function storyStart(i) {
    if (!ready) return;
    if (!story.sc.length) story.sc = buildScenes();
    if (playing) setPlaying(false);
    if (popup) popup.remove(); hideTip();
    if (follow) setFollow(false);
    story.on = true; document.documentElement.classList.add('story-on'); $('caption').hidden = true;
    $('story').hidden = false; $('replayStory').hidden = true;
    var ol = $('stSteps'); ol.innerHTML = ''; ol.style.setProperty('--n', story.sc.length);
    story.sc.forEach(function (sc, k) {
      var li = document.createElement('li'); li.innerHTML = '<i></i>'; li.title = (k + 1) + '. ' + sc.title;
      li.addEventListener('click', function () { storyGo(k); }); ol.appendChild(li);
    });
    placeStory();
    storyGo(i || 0, true);
    if (!story.raf) story.raf = requestAnimationFrame(storyTick);
  }
  function storyGo(i, first) {
    i = Math.max(0, Math.min(story.sc.length - 1, i));
    var sc = story.sc[i]; story.i = i; story.hold = 0; story.start = performance.now(); setStoryPaused(false);
    $('stTitle').innerHTML = '<span class="n">' + (i + 1) + ' of ' + story.sc.length + '</span>' + esc(sc.title);
    setTime(sc.a);
    $('stText').innerHTML = sc.text();
    $('story').classList.toggle('fin', i === story.sc.length - 1);
    $('stPrev').disabled = i === 0;
    Array.prototype.forEach.call($('stSteps').children, function (li, k) { li.className = k < i ? 'done' : ''; li.firstChild.style.width = k < i ? '100%' : '0'; });
    storyLayers(sc); storyCam(sc, first); storyLive();
    if (i === story.sc.length - 1) setTimeout(function () { if (story.on && story.i === i) $('stSkip').focus({ preventScroll: true }); }, 50);
  }
  function storyLive() { var sc = story.sc[story.i]; if (sc) $('stLive').innerHTML = sc.live(); }
  function storyTick(now) {
    story.raf = 0;
    if (!story.on) return;
    var sc = story.sc[story.i], p = sc.dur ? (story.paused ? story.pausedAt - story.start : now - story.start) / sc.dur : 1;
    p = Math.max(0, Math.min(1, p));
    if (!story.paused) setTime(sc.a + (sc.b - sc.a) * p);
    var li = $('stSteps').children[story.i]; if (li) li.firstChild.style.width = (p * 100).toFixed(1) + '%';
    var dt = Math.min(0.25, (now - (story.last || now)) / 1000); story.last = now;
    var dr = sc.rain - rainOp; if (Math.abs(dr) > 0.005) { rainOp += dr * Math.min(1, dt * 2.5); map.triggerRepaint(); }
    if (p >= 1 && !story.paused && story.i < story.sc.length - 1) {
      if (!story.hold) story.hold = now;
      else if (now - story.hold > 1800) storyGo(story.i + 1);
    }
    story.raf = requestAnimationFrame(storyTick);
  }
  function setStoryPaused(on) {
    if (on === story.paused) return;
    story.paused = on;
    if (on) story.pausedAt = performance.now(); else story.start += performance.now() - story.pausedAt;
    $('stPauseIcon').setAttribute('d', on ? 'M6 4l10 6-10 6z' : 'M6 4h3v12H6zM11 4h3v12h-3z');
    $('stPause').setAttribute('aria-label', on ? 'Resume story' : 'Pause story');
  }
  function storyEnd() {
    if (!story.on) return;
    story.on = false; document.documentElement.classList.remove('story-on');
    phNow = -9; setTimeout(function () { phaseCaption(); }, 0);
    $('story').hidden = true;
    rainOp = 1; applyToggles(); map.triggerRepaint();
    document.querySelectorAll('#views button').forEach(function (b) { b.setAttribute('aria-pressed', +b.dataset.view === currentView ? 'true' : 'false'); });
  }
  function placeStory() { // desktop: under the identity card, in the same left column the framing already keeps clear
    var c = $('card').getBoundingClientRect();
    document.documentElement.style.setProperty('--story-top', Math.round(c.bottom + 10) + 'px');
    document.documentElement.style.setProperty('--cap-top', Math.round(c.bottom + 8) + 'px');
  }
  $('stNext').addEventListener('click', function () { storyGo(story.i + 1); });
  $('stPrev').addEventListener('click', function () { storyGo(story.i - 1); });
  $('stPause').addEventListener('click', function () { setStoryPaused(!story.paused); });
  $('stSkip').addEventListener('click', function () { storyEnd(); });
  $('replayStory').addEventListener('click', function () { storyStart(0); });
  // timeline jumps: the start of the run and the moment the most roads are closed
  $('jStart').addEventListener('click', function () { if (!meta) return; if (playing) setPlaying(false); played = true; setTime(0); });
  $('jPeak').addEventListener('click', function () {
    if (!meta) return; var cp = meta.closed_per_frame || [], k = 0; for (var i = 1; i < cp.length; i++) if (cp[i] > cp[k]) k = i;
    if (playing) setPlaying(false); played = true; setTime(Math.min(k, nf - 1));
  });

  // ---------- theme and basemap ----------
  function applyTheme() {
    if (!map || !map.getLayer('b-lgt')) return;
    var b = basemap(), L = BASEMAPS[b].layers, P = pal();
    ['b-hill', 'b-lgt', 'b-sat', 'b-dark', 'l-voy', 'l-dark', 'b-hshade'].forEach(function (id) {
      if (!map.getLayer(id)) return;
      var on = L[id] && !(/^l-/.test(id) && map.getLayer('lb-place')); // vector street, water and place labels replace the raster ones
      map.setLayoutProperty(id, 'visibility', on ? 'visible' : 'none');
      if (on && id !== 'b-hshade') map.setPaintProperty(id, 'raster-opacity', L[id]);
    });
    if (map.getLayer('bg')) map.setPaintProperty('bg', 'background-color', b === 'night' || b === 'dark' ? '#1E2124' : '#F2F2EF');
    wiTheme(b);
    document.querySelectorAll('#basemaps button').forEach(function (x) { x.setAttribute('aria-pressed', x.dataset.bm === b ? 'true' : 'false'); });
    var root = document.documentElement.style;
    ['d1', 'd2', 'd3', 'd4'].forEach(function (k, i) { root.setProperty('--' + k, P.d[i]); });
    root.setProperty('--closed', P.closed); root.setProperty('--amber', P.amber); root.setProperty('--orange', P.orange); root.setProperty('--grey', P.grey);
    root.setProperty('--peak', P.peak); root.setProperty('--peak-op', P.peakOp); root.setProperty('--may', P.may);
    flowRGB = b === 'dark' || b === 'night' ? { hi: [0.86, 0.91, 0.93], dk: 0.24 } : b === 'satellite' ? { hi: [0.93, 0.95, 0.96], dk: 0.26 } : { hi: [0.216, 0.278, 0.31], dk: 0.2 };
    depth.setRamp(P.d.map(rgba)); depth.setDrain(b === 'dark' || b === 'night' ? [0.5, 0.58, 0.68, 0.72] : [0.48, 0.54, 0.6, 0.62]);
    if (map.getLayer('net-case')) {
      map.setPaintProperty('net-case', 'line-color', ['match', NET_RANK, 0, P.net[0], 1, P.net[1], 2, P.net[2], P.net[3]]);
      map.setPaintProperty('net-fill', 'line-color', P.fill);
    }
    if (map.getLayer('box')) map.setPaintProperty('box', 'line-color', P.box);
    if (map.getLayer('wet')) {
      var D = RD || ['coalesce', ['feature-state', 'd'], 0];
      // under 15 cm water on road (amber, dark casing), 15-30 cm at risk (vermillion), 30 cm and more closed (dark red, white stripes)
      map.setPaintProperty('wet', 'line-color', ['step', D, P.amber, 15, P.orange, 30, P.closed]);
      map.setPaintProperty('wetcase', 'line-color', P.cas); // a casing in the background colour: 'this street, flooded'
      var dkT = b === 'dark' || b === 'night';
      ['rlab-w', 'rlab-r', 'rlab-c'].forEach(function (id) { if (!map.getLayer(id)) return;
        map.setPaintProperty(id, 'text-color', ['step', ['get', 'd'], dkT ? '#F2F2EF' : '#1F2328', 15, dkT ? P.orange : '#A33F00', 30, P.closed]);
        map.setPaintProperty(id, 'text-halo-color', dkT ? '#1E2124' : '#FFFFFF'); });
      map.setPaintProperty('bar', 'line-color', '#ffffff');
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
    x.addEventListener('click', function () { bm = x.dataset.bm; store(BMKEY, bm); applyTheme(); });
  });
  (function () { // legend ramps that do not depend on the basemap
    var n = RAIN_CLASSES.length, stops = RAIN_CLASSES.map(function (c, i) { var col = 'rgb(' + c[1].join(',') + ')'; return col + ' ' + (100 * i / n).toFixed(1) + '% ' + (100 * (i + 1) / n).toFixed(1) + '%'; });
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
    var bands = Array.prototype.filter.call(document.querySelectorAll('#timeline .band'), function (b) { return !b.hidden && b.offsetParent !== null; });
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
  $('gaugeSel').addEventListener('change', function () { drawChart(); instInit(); });
  function setCursor() { var c = $('cursor'); if (c && nf > 1) c.style.left = (100 * t / (nf - 1)) + '%'; }

  // pieces: a piece shows its segment's state while the map draws water on it
  var PCS = null;
  function inIv(w) { for (var j = 0; j < w.length; j++) if (t >= w[j][0] - 0.5 && t <= w[j][1] + 0.5) return true; return false; }
  function pieceWet(i) {
    return inIv(WION && wi && wi.dj && wi.dj.pw ? ((wi.dj.pw[PCS.seg[i]] || [])[PCS.k[i]] || []) : PCS.w[i]);
  }
  function pieceNear(i) { // drawn water in the cell beside the piece (published packs only)
    return !WION && PCS.n && PCS.n[i] ? inIv(PCS.n[i]) : false;
  }
  // merged runs: consecutive painted pieces of a segment joined into one line (a single unpainted piece between two painted ones is
  // bridged), so a flooded street reads as one continuous line, plus one name label per segment at the middle of its longest run
  var RD = null, runsKey = '', runsAt = 0, runsT = 0;
  var ABBR = [[/\bStreet\b/g, 'St'], [/\bAvenue\b/g, 'Ave'], [/\bRoad\b/g, 'Rd'], [/\bDrive\b/g, 'Dr'], [/\bBoulevard\b/g, 'Blvd'], [/\bLane\b/g, 'Ln'], [/\bPlace\b/g, 'Pl'], [/\bParkway\b/g, 'Pkwy'], [/\bHighway\b/g, 'Hwy']];
  function shortName(nm) { ABBR.forEach(function (a) { nm = nm.replace(a[0], a[1]); }); return nm; }
  // street labels sit above the report and culvert markers: drawn over them, and placed first so a marker never pushes a name off
  function raiseLabels() { ['hot', 'rlab-w', 'rlab-r', 'rlab-c'].forEach(function (id) { if (map.getLayer(id)) map.moveLayer(id); }); }
  function runsBuild() {
    runsAt = Date.now(); runsT = 0;
    var feats = [], labs = [], same = function (a, b) { return Math.abs(a[0] - b[0]) < 2e-5 && Math.abs(a[1] - b[1]) < 2e-5; };
    Object.keys(PCS.bySeg).forEach(function (sid) {
      var ix = PCS.bySeg[sid], d = 0, k, runs = [], cur = null;
      for (k = 0; k < ix.length; k++) if (PCS.v[ix[k]] > 0) { d = PCS.v[ix[k]]; break; }
      if (!d) return;
      for (k = 0; k < ix.length; k++) {
        var i = ix[k], on = PCS.v[i] > 0 || (k > 0 && k < ix.length - 1 && PCS.v[ix[k - 1]] > 0 && PCS.v[ix[k + 1]] > 0), ln = PCS.lines[i];
        if (!on) { cur = null; continue; }
        if (cur && same(cur[cur.length - 1], ln[0])) { for (var j = 1; j < ln.length; j++) cur.push(ln[j]); } else { cur = ln.slice(); runs.push(cur); }
      }
      if (!runs.length) return;
      feats.push({ type: 'Feature', properties: { d: d }, geometry: { type: 'MultiLineString', coordinates: runs } });
      var sg = segById[sid], nm = sg && sg.f && sg.f.properties.n;
      if (!nm) return;
      var best = runs[0], bl = -1;
      runs.forEach(function (r) { var L = 0; for (var q = 1; q < r.length; q++) L += Math.hypot(r[q][0] - r[q - 1][0], r[q][1] - r[q - 1][1]); if (L > bl) { bl = L; best = r; } });
      var mid = best[Math.floor((best.length - 1) / 2)], mid2 = best[Math.ceil((best.length - 1) / 2)];
      var kk = meta.kofn && sg.f.properties.k, lt = kk ? (kk >= 2 ? 'Likely' : 'Possible') + ' · ' + kk + ' of ' + meta.kofn.n + ' runs' : d >= 30 ? 'closed' : Math.round(d) + ' cm';
      labs.push({ type: 'Feature', properties: { d: d, nm: nm, t: shortName(nm) + ' · ' + lt }, geometry: { type: 'Point', coordinates: [(mid[0] + mid2[0]) / 2, (mid[1] + mid2[1]) / 2] } });
    });
    // one label per street name within about 800 m, keeping the most severe (several segments of one street flood together)
    labs.sort(function (a, b) { return b.properties.d - a.properties.d; });
    var kept = [], kx = 1 / (111320 * Math.cos(meta.corners[0][1] * Math.PI / 180)), ky = 1 / 110540;
    labs.forEach(function (f) {
      var nm = f.properties.nm, c = f.geometry.coordinates;
      if (kept.some(function (o) { return o.properties.nm === nm && Math.hypot((o.geometry.coordinates[0] - c[0]) / kx, (o.geometry.coordinates[1] - c[1]) / ky) < 800; })) return;
      kept.push(f);
    });
    map.getSource('runs').setData({ type: 'FeatureCollection', features: feats });
    map.getSource('rlab').setData({ type: 'FeatureCollection', features: kept });
  }
  function runsUpdate() {
    var k = []; for (var i = 0; i < PCS.seg.length; i++) if (PCS.v[i] > 0) k.push(i + ':' + PCS.v[i]);
    k = k.join(','); if (k === runsKey) return; runsKey = k;
    if (runsT) return; var dt = Date.now() - runsAt; // at most four rebuilds a second while the storm plays
    if (dt >= 250) runsBuild(); else runsT = setTimeout(runsBuild, 250 - dt);
  }
  function piecesTime() {
    var any = {}, i, wet = new Uint8Array(PCS.seg.length), anyN = {};
    for (i = 0; i < PCS.seg.length; i++) if (pieceWet(i)) { wet[i] = 1; any[PCS.seg[i]] = 1; }
    for (i = 0; i < PCS.seg.length; i++) if (!any[PCS.seg[i]] && pieceNear(i)) { var sq = segById[PCS.seg[i]]; if (sq && sq.v >= 30) { wet[i] = 2; anyN[PCS.seg[i]] = 1; } }
    for (i = 0; i < PCS.seg.length; i++) {
      var sg = segById[PCS.seg[i]], q = sg ? Math.max(0, sg.v) : 0, d, e;
      // the depth layer starts at 5 cm, so road states do too: water on road = 5-15 cm, and only on pieces where the map draws water.
      // A wet piece whose road water is under 5 cm shows 'water at the edge'. A closure is never hidden (whole-segment fallback).
      // a closed segment with no water on its own pieces is drawn on the pieces with water beside them (wet = 2), and only failing
      // that along the whole segment.
      if (wet[i]) { d = q >= 5 ? q : 0; e = q < 5 ? 1 : 0; } else { d = q >= 30 && !any[PCS.seg[i]] && !anyN[PCS.seg[i]] ? q : 0; e = 0; }
      if (d !== PCS.v[i] || e !== PCS.e[i]) { PCS.v[i] = d; PCS.e[i] = e; map.setFeatureState({ source: 'pieces', id: i }, { d: d, e: e }); }
    }
    if (map.getSource('runs')) runsUpdate();
    var r = 0, w = 0; // counts as drawn: segments with water on the road where the map shows it
    Object.keys(any).forEach(function (sid) { var sg = segById[sid], q = sg ? sg.v : 0; if (q >= 30) return; if (q >= 15) r++; else if (q >= 5) w++; });
    return [r, w];
  }
  // status line: what the map shows right now, in words, and which kind of run it is
  var slLast = '';
  function statusLine(c, r, w) {
    var cp = meta.closed_per_frame || [], pk = 0; for (var i = 0; i < cp.length; i++) if (cp[i] > cp[pk]) pk = i;
    var txt = n(c) + ' closed · ' + n(r) + ' at risk' + (small() ? '' : ' · ' + n(w) + ' with water on the road') + (cp.length ? ' · peak ' + fmtCap.format(timeAt(pk)).replace(/^\w+ /, '') : '');
    if (txt === slLast) return; slLast = txt;
    $('slNow').textContent = txt;
  }
  function rankBuild() {
    var rows = [];
    segs.forEach(function (s) {
      var d = s.d || [], mx = 0, pk = 0; for (var i = 0; i < d.length; i++) if (d[i] > mx) { mx = d[i]; pk = i; }
      if (mx < 3) return;
      var iv = s.iv || [], sev = iv.length ? 3 : mx >= 15 ? 2 : 1, st = iv.length ? iv[0][0] : d.findIndex(function (v) { return v >= 3; });
      rows.push({ s: s, mx: mx, pk: pk, sev: sev, st: st, end: iv.length ? iv[iv.length - 1][1] : null });
    });
    rows.sort(function (a, b) { return b.sev - a.sev || a.st - b.st; });
    rankRows = rows;
    var ol = $('rankList'); ol.innerHTML = '';
    rows.slice(0, 40).forEach(function (r) {
      var p = r.s.f.properties, li = document.createElement('li'), b = document.createElement('button'); b.type = 'button';
      var chip = r.sev === 3 ? '<span class="chip-st shut">Closed</span>' : r.sev === 2 ? '<span class="chip-st risk">At risk</span>' : '<span class="chip-st wet">Water on road</span>';
      b.innerHTML = '<span class="rn"><b>' + esc(p.n || 'Unnamed road') + '</b>' + (p.t ? ' <span>' + esc(p.t) + '</span>' : '') + '</span>' + chip +
        '<span class="rt">' + (r.sev === 3 ? 'Closes ' + fmtCap.format(timeAt(r.st)).replace(/^\w+ /, '') + ' · ' : 'From ' + fmtCap.format(timeAt(r.st)).replace(/^\w+ /, '') + ' · ') +
        'Peak ' + fmtCap.format(timeAt(r.pk)).replace(/^\w+ /, '') + (r.end != null ? ' · Reopens ' + (r.end >= nf - 1 ? 'after the run' : fmtCap.format(timeAt(r.end)).replace(/^\w+ /, '')) : '') +
        ' · up to ' + (r.mx >= 255 ? '2.5 m+' : r.mx + ' cm') + '</span>';
      b.addEventListener('click', function () {
        var g = r.s.f.geometry, cs = g.type === 'LineString' ? g.coordinates : [].concat.apply([], g.coordinates), bb = [[180, 90], [-180, -90]];
        cs.forEach(function (c) { bb[0][0] = Math.min(bb[0][0], c[0]); bb[0][1] = Math.min(bb[0][1], c[1]); bb[1][0] = Math.max(bb[1][0], c[0]); bb[1][1] = Math.max(bb[1][1], c[1]); });
        if (playing) setPlaying(false); played = true; setTime(r.pk);
        map.fitBounds(bb, { padding: framePadding(), maxZoom: 14.5, duration: reduced ? 0 : 900 });
        if (small()) sheetDetent('peek');
        map.once('moveend', function () { openPlace(r.s.f, cs[Math.floor(cs.length / 2)]); });
      });
      li.appendChild(b); ol.appendChild(li);
    });
    $('rank').hidden = !rows.length;
    $('rank').querySelector('summary').textContent = 'Roads, most severe first (' + rows.length + ')';
  }
  var lastClock = '';
  function setTime(v) {
    t = Math.max(0, Math.min(nf - 1, v));
    var fa = Math.min(Math.floor(t), nf - 1), fr = t - fa, closed = 0, wet = 0, risk = 0;
    for (var i = 0; i < segs.length; i++) {
      var s = segs[i], d = s.d, val;
      if (d) {
        var a = d[fa] || 0, b = d[fa + 1] || 0;
        val = a + (b - a) * fr;
        if (s.dp && wi && wi.x < 1) { var pa = s.dp[fa] || 0, pb = s.dp[fa + 1] || 0; val = (pa + (pb - pa) * fr) * (1 - wi.x) + val * wi.x; }
      } else { // no depth series: ramp up over the hour before each closure and drain over the hour after
        val = 0;
        for (var j = 0; j < s.iv.length; j++) {
          var lead = 60 / meta.frame_min, x0 = s.iv[j][0], x1 = s.iv[j][1];
          var u = t < x0 ? 1 - (x0 - t) / lead : t > x1 ? 1 - (t - x1) / lead : 1;
          val = Math.max(val, u > 0 ? (t >= x0 && t <= x1 ? 40 : 30 * u) : 0);
        }
      }
      // a closed road reopens below 26 cm, not 30, so a depth hovering at the threshold does not flicker between states
      if (s.cl) { if (val < 26) s.cl = false; } else if (val >= 30) s.cl = true;
      if (s.cl) { closed++; val = Math.max(val, 30); } else { val = Math.min(val, 29); if (val >= 3) wet++; if (val >= 15) risk++; }
      var q = val < 2 ? 0 : 2 * Math.round(val / 2);
      // water drawn across the road while the road surface stays above it (embankments, crowned roads): 'water at the road edge'
      var eg = 0;
      if (q < 3 && s.e) for (var k = 0; k < s.e.length; k++) if (t >= s.e[k][0] - 0.5 && t <= s.e[k][1] + 0.5) { eg = 1; break; }
      if (q !== s.v || eg !== s.eg) { s.v = q; s.eg = eg; if (!PCS) map.setFeatureState({ source: 'roads', id: s.id }, { d: q, e: eg }); else s.v2 = 1; }
    }
    if (PCS && PCS.v) { var cnt = piecesTime(); statusLine(closed, cnt[0], cnt[1]); } else statusLine(closed, risk, wet - risk);
    var mins = Math.round(t * meta.frame_min / 5) * 5, label = fmtClock.format(new Date(t0.getTime() + mins * 60000));
    if (label !== lastClock) {
      lastClock = label;
      $('clock').textContent = label;
      $('since').textContent = (mins / 60).toFixed(1) + ' h after the replay starts';
    }
    $('nClosed').textContent = closed;
    nWet = wet; nClosedNow = closed;
    $('scrub').value = t;
    setCursor();
    // live bits of open tooltips and popups (a few DOM writes, no feature loops)
    if (rtipId != null && rtip) { var hf = segById[rtipId]; if (hf) rtip.setHTML(roadTip(hf.f)); }
    var sc = document.getElementById('spkCur');
    if (sc) { var xx = ((t - sparkRange[0]) / (sparkRange[1] - sparkRange[0]) * 260).toFixed(1); sc.setAttribute('x1', xx); sc.setAttribute('x2', xx); sc.setAttribute('visibility', t < sparkRange[0] || t > sparkRange[1] ? 'hidden' : 'visible'); }
    var pn = document.getElementById('ppNow');
    if (pn) { var cm = segDepth(+pn.dataset.id); pn.textContent = cm >= 3 ? cm + ' cm' : 'dry'; }
    if (story.on) storyLive();
    if (cascade) cascadeTime();
    if (WHATIF) { wiCulvertTime(); wiLive(); }
    phaseCaption(); wiSwell(); capClock();
    instNow(); appTick();
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
      if (!played || t >= nf - 1.01) t = WHATIF && PH.length ? Math.max(0, PH[0].a - 60 / meta.frame_min) : 0;
      played = true;
      last = performance.now();
      if (follow) followTick(true);
      requestAnimationFrame(tick);
      requestAnimationFrame(dashTick); phNow = -1; phaseCaption();
    }
  }
  $('play').addEventListener('click', function () { if (!ready) return; if (story.on) { storyEnd(); played = true; } setPlaying(!playing); });
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
  $('scrub').addEventListener('input', function (e) { if (!ready) return; if (story.on) storyEnd(); if (playing) setPlaying(false); played = true; setTime(+e.target.value); });
  document.addEventListener('keydown', function (e) {
    if (!ready || e.altKey || e.ctrlKey || e.metaKey) return;
    var tg = e.target, free = tg === document.body || tg === map.getCanvas() || (tg.closest && tg.closest('#story'));
    if (/^(INPUT|SELECT|TEXTAREA)$/.test(tg.tagName) && tg.id !== 'scrub') return;
    if (story.on) {
      if (e.key === 'ArrowRight') { e.preventDefault(); if (story.i < story.sc.length - 1) storyGo(story.i + 1); else storyEnd(); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); storyGo(story.i - 1); }
      else if (e.key === 'Escape') { e.preventDefault(); storyEnd(); }
      else if (e.key === ' ' && free && tg.tagName !== 'BUTTON') { e.preventDefault(); setStoryPaused(!story.paused); }
      return;
    }
    if (e.key === ' ' && free && tg.tagName !== 'BUTTON') { e.preventDefault(); setPlaying(!playing); }
    else if ((e.key === 'ArrowRight' || e.key === 'ArrowLeft') && free) {
      e.preventDefault(); if (playing) setPlaying(false); played = true;
      setTime(Math.round(t) + (e.key === 'ArrowRight' ? 1 : -1) * (e.shiftKey ? 60 / meta.frame_min : 1));
    }
  });

  // ---------- layer toggles ----------
  function vis(id, on) { if (map && map.getLayer(id)) map.setLayoutProperty(id, 'visibility', on ? 'visible' : 'none'); }
  $('lyRain').addEventListener('change', function (e) { vis('rain', e.target.checked); });
  $('lyDepth').addEventListener('change', function (e) { vis('depth', e.target.checked); });
  $('lyFlow').addEventListener('change', function (e) { vis('flow', e.target.checked); $('flowKey').hidden = !e.target.checked; });
  $('lyClosed').addEventListener('change', function (e) { ['wet', 'wetcase', 'halo', 'bar'].forEach(function (l) { vis(l, e.target.checked); }); });
  $('lyPeak').addEventListener('change', function (e) { vis('peak', e.target.checked); });
  $('lyMay').addEventListener('change', function (e) { vis('may', e.target.checked); });
  $('lyRisk').addEventListener('change', function (e) {
    var on = e.target.checked;
    vis('risk', on); $('riskKey').hidden = !on;
    $('lyPeak').checked = !on; vis('peak', !on);
    $('lyMay').checked = !on; vis('may', !on);
  });
  function refVis(key, on) { if (key === 'knock') ['knock', 'knock-ring'].concat(CX_LAYERS).forEach(function (l) { vis(l, on); }); else { vis('r-' + key, on); vis('c-' + key, on); vis('c-' + key + '-n', on); } }
  document.querySelectorAll('input[data-ref]').forEach(function (x) { x.addEventListener('change', function () { refVis(x.dataset.ref, x.checked); }); });
  sheetPlace(); sheetToggle(false);
  var pl = document.querySelector('.player');
  function ph() { if (small()) return; document.documentElement.style.setProperty('--player-h', pl.offsetHeight + 'px'); }
  if (window.ResizeObserver) new ResizeObserver(ph).observe(pl); ph();
  // the key is always on screen; the layer panel opens on demand (remembered on desktop)
  var lg = $('legend'), lgOpen = !small() && store('mfw-layers') === '1';
  lg.dataset.collapsed = lgOpen ? 'false' : 'true'; $('legendToggle').setAttribute('aria-expanded', lgOpen ? 'true' : 'false');
  $('legendToggle').addEventListener('click', function () {
    var c = lg.dataset.collapsed === 'true';
    lg.dataset.collapsed = c ? 'false' : 'true';
    this.setAttribute('aria-expanded', c ? 'true' : 'false');
    if (!small()) store('mfw-layers', c ? '1' : '0');
  });
  var rz = 0;
  window.addEventListener('resize', function () {
    clearTimeout(rz);
    rz = setTimeout(function () { sheetPlace(); placeStory(); if (story.on) storyCam(story.sc[story.i], true); else if (!userMoved && !follow && views.length) refit(); }, 200);
  });

  // ======================================================================================================================
  // Round 4: app shell. Tabs (Map · Roads · What-if · Live · About), phone sheet detents, floating buttons, place card,
  // share links and CSV, the Live tab, and the water journey on the map (rain, runoff particles, swelling streams, drying).
  // ======================================================================================================================
  var TAB_OF = { whatif: 'whatif', forecast: 'live' }, curTab = TAB_OF[runKey] || 'map';
  function setTabOn(k) { document.querySelectorAll('#tabs a').forEach(function (a) { if (a.dataset.tab === k) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); }); }
  (function tabsInit() {
    var lastMap = store('mfw-lastmap') || 'leominster_sep2023';
    if (curTab === 'map') store('mfw-lastmap', runKey);
    document.querySelectorAll('#tabs a').forEach(function (a) {
      var k = a.dataset.tab;
      if (k === 'map') a.href = '?run=' + (curTab === 'map' ? runKey : lastMap);
      if (k === 'roads') {
        a.href = curTab === 'live' ? '?run=' + lastMap + '#roads' : '#roads';
        if (curTab !== 'live') a.addEventListener('click', function (e) { e.preventDefault(); openRoads(); });
      }
      if (k === 'map' && curTab === 'map') a.addEventListener('click', function (e) {
        e.preventDefault(); closePlace(); setTabOn('map');
        if (small()) sheetDetent('peek'); else { $('rank').open = false; if (document.documentElement.classList.contains('side-off')) sideSet(true); }
      });
    });
    setTabOn(curTab);
    if (location.hash === '#roads') { var tries = 0, iv = setInterval(function () { if (ready && rankRows.length || ++tries > 60) { clearInterval(iv); if (rankRows.length) openRoads(); } }, 250); }
  })();
  function openRoads() {
    if ($('rank').hidden) { toast('No road gets water in this run'); return; }
    closePlace(); setTabOn('roads'); $('rank').open = true;
    if (small()) { sheetDetent('full'); setTimeout(function () { var pl = document.querySelector('.player'); pl.scrollTo({ top: $('rank').offsetTop - 44, behavior: reduced ? 'auto' : 'smooth' }); }, 60); }
    else { sideSet(true); $('rank').scrollIntoView({ block: 'start', behavior: reduced ? 'auto' : 'smooth' }); }
  }

  // ---------- desktop sidebar: collapsible ----------
  function sideSet(on) {
    document.documentElement.classList.toggle('side-off', !on);
    $('sideToggle').setAttribute('aria-expanded', on ? 'true' : 'false'); $('sideToggle').setAttribute('aria-label', on ? 'Hide the side panel' : 'Show the side panel');
    store('mfw-side', on ? '1' : '0');
    setTimeout(function () { drawChart(); if (map) map.resize(); }, 420);
  }
  $('sideToggle').addEventListener('click', function () { sideSet(document.documentElement.classList.contains('side-off')); });
  if (!small() && store('mfw-side') === '0') sideSet(false);

  // ---------- phone: bottom sheet with three detents ----------
  var detent = 'peek', dragged = false;
  function sheetMetrics() {
    var pl = document.querySelector('.player'), vh = window.innerHeight, tabs = $('tabs'), tab = tabs && tabs.parentNode === document.body ? tabs.offsetHeight : 0;
    var top = $('card').getBoundingClientRect().bottom + 8, full = Math.max(200, vh - tab - top);
    var tl = $('timeline'), peek;
    if (document.documentElement.classList.contains('no-replay')) peek = Math.min(full, Math.round(vh * 0.2));
    else peek = Math.min(full, (tl && tl.offsetParent ? tl.offsetTop : 120) + 48);
    var half = Math.max(peek + 90, Math.min(full, Math.round(vh * 0.52)));
    return { full: full, peek: Math.max(96, peek), half: half };
  }
  function sheetDetent(d) {
    if (!small()) return;
    var pl = document.querySelector('.player'); detent = d;
    pl.dataset.detent = d; pl.dataset.open = d === 'peek' ? 'false' : 'true';
    $('grab').setAttribute('aria-expanded', d === 'peek' ? 'false' : 'true');
    document.documentElement.classList.toggle('sheet-open', d !== 'peek');
    var m = sheetMetrics(), vis_ = m[d];
    pl.style.setProperty('--sheet-h', m.full + 'px'); pl.style.setProperty('--sheet-off', (m.full - vis_) + 'px'); pl.style.transform = '';
    if (d !== 'full') pl.scrollTop = 0;
    document.documentElement.style.setProperty('--player-h', vis_ + 'px');
    $('grabL').textContent = d === 'peek' ? 'More' : 'Less';
    drawChart();
  }
  (function sheetDrag() {
    var pl = document.querySelector('.player'), y0 = null, off0 = 0, ly = 0, lt = 0, v = 0, id = null;
    function down(e) {
      if (!small() || (e.pointerType === 'mouse' && e.button !== 0)) return;
      if (detent === 'full' && pl.scrollTop > 0 && e.currentTarget !== $('grab')) return;
      var m = sheetMetrics(); y0 = e.clientY; off0 = m.full - m[detent]; ly = y0; lt = performance.now(); v = 0; id = e.pointerId; dragged = false;
    }
    function move(e) {
      if (y0 === null || e.pointerId !== id) return;
      var dy = e.clientY - y0; if (!dragged && Math.abs(dy) < 6) return;
      if (!dragged) { dragged = true; pl.classList.add('dragging'); try { e.currentTarget.setPointerCapture(id); } catch (x) { } }
      var m = sheetMetrics(), off = Math.max(-12, Math.min(m.full - m.peek + 24, off0 + dy));
      pl.style.transform = 'translateY(' + off + 'px)';
      var now = performance.now(); v = (e.clientY - ly) / Math.max(1, now - lt); ly = e.clientY; lt = now;
    }
    function up(e) {
      if (y0 === null) return;
      var dy = e.clientY - y0; y0 = null; pl.classList.remove('dragging');
      if (!dragged) return;
      var m = sheetMetrics(), vis_ = m.full - (off0 + dy) - v * 220, best = 'peek', bd = 1e9;
      ['peek', 'half', 'full'].forEach(function (k) { var dd = Math.abs(m[k] - vis_); if (dd < bd) { bd = dd; best = k; } });
      sheetDetent(best);
      setTimeout(function () { dragged = false; }, 50);
    }
    ['grab', 'statusLine'].forEach(function (k) {
      var el = $(k); el.addEventListener('pointerdown', down); el.addEventListener('pointermove', move); el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
    });
    $('grab').addEventListener('click', function () { if (dragged) return; sheetDetent(detent === 'peek' ? 'half' : detent === 'half' ? 'full' : 'peek'); });
    $('statusLine').addEventListener('click', function () { if (small() && !dragged && detent === 'peek') sheetDetent('half'); });
  })();

  // ---------- floating buttons ----------
  $('fbIn').addEventListener('click', function () { if (map) map.zoomIn({ duration: reduced ? 0 : 300 }); });
  $('fbOut').addEventListener('click', function () { if (map) map.zoomOut({ duration: reduced ? 0 : 300 }); });
  $('fbShare').addEventListener('click', function () { shareView(); });
  $('shareBtn2').addEventListener('click', function () { shareView(); });
  $('csvBtn').addEventListener('click', function () { rankCsv(); });
  $('fbLayers').addEventListener('click', function () {
    var lg = $('legend');
    if (small()) { var on = lg.dataset.pop !== 'on'; lg.dataset.pop = on ? 'on' : 'off'; this.setAttribute('aria-expanded', on ? 'true' : 'false'); if (on) closePlace(); }
    else $('legendToggle').click();
  });
  var meMark = null;
  $('fbLocate').addEventListener('click', function () {
    if (!navigator.geolocation || !map) { toast('Location is not available in this browser'); return; }
    var btn = this; btn.setAttribute('aria-pressed', 'true');
    navigator.geolocation.getCurrentPosition(function (p) {
      var ll = [p.coords.longitude, p.coords.latitude];
      if (!meMark) { var el = document.createElement('div'); el.className = 'me'; meMark = new maplibregl.Marker({ element: el }); }
      meMark.setLngLat(ll).addTo(map);
      map.flyTo({ center: ll, zoom: Math.max(map.getZoom(), 14), duration: reduced ? 0 : 900 });
      var b = meta && meta.corners ? boxBounds() : null;
      if (b && (ll[0] < b[0][0] || ll[0] > b[1][0] || ll[1] < b[0][1] || ll[1] > b[1][1])) toast('You are outside the area this storm was modelled for');
    }, function () { btn.removeAttribute('aria-pressed'); toast('Location permission was not given'); }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 });
  });

  // ---------- toast ----------
  var toastT = 0;
  function toast(msg) { var el = $('toast'); el.textContent = msg; el.hidden = false; clearTimeout(toastT); toastT = setTimeout(function () { el.hidden = true; }, 2600); }

  // ---------- share links (storm, time, view, open road) and CSV ----------
  function viewUrl() {
    var u = new URL(location.href), q = u.searchParams;
    ['debug', 'story', 'embed', 'c', 'z', 't', 'road', 's'].forEach(function (k) { q.delete(k); });
    q.set('run', runKey);
    if (map) { var c = map.getCenter(); q.set('c', c.lng.toFixed(5) + ',' + c.lat.toFixed(5)); q.set('z', map.getZoom().toFixed(2)); }
    if (meta && curTab !== 'live') q.set('t', String(Math.round(t)));
    if (placeId != null) q.set('road', String(placeId));
    if (WION && wi && wi.key) q.set('s', wi.key);
    u.hash = ''; return u.toString();
  }
  function shareView() {
    var url = viewUrl(), title = document.title;
    if (navigator.share && small()) { navigator.share({ title: title, url: url }).catch(function () { }); return; }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(function () { toast('Link copied: this storm, time and view'); }, function () { window.prompt('Copy this link', url); });
    else window.prompt('Copy this link', url);
  }
  var rankRows = [];
  function rankCsv() {
    var q = function (v) { v = v == null ? '' : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
    var iso = function (f) { return f == null || f < 0 ? '' : new Date(timeAt(f).getTime()).toISOString().replace(/\.\d+Z$/, 'Z'); };
    var L = [['segment_id', 'road', 'town', 'road_class', 'state', 'first_water_utc', 'closes_utc', 'peak_utc', 'peak_depth_cm', 'reopens_utc', 'chance_of_closing'].join(',')];
    rankRows.forEach(function (r) {
      var p = r.s.f.properties;
      L.push([r.s.id, p.n || '', p.t || '', CLS[p.c || 0], r.sev === 3 ? 'closed' : r.sev === 2 ? 'at risk (15-30 cm)' : 'water on road (5-15 cm)', iso(r.st), r.sev === 3 ? iso(r.st) : '',
        iso(r.pk), r.mx, r.end != null ? (r.end >= nf - 1 ? 'after the run' : iso(r.end)) : '', p.p != null ? p.p : ''].map(q).join(','));
    });
    var blob = new Blob([L.join('\n') + '\n'], { type: 'text/csv' }), a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = 'mass-flood-watch_' + runKey + '_roads.csv'; document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
    toast(rankRows.length + ' roads saved as CSV');
  }

  // ---------- place card: a tapped road, with its cross streets and nearby open streets ----------
  var placeId = null;
  function midOf(f) { var g = f.geometry, cs = g.type === 'LineString' ? g.coordinates : [].concat.apply([], g.coordinates); return cs[Math.floor(cs.length / 2)]; }
  function altStreets(f, ends) {
    if (!map.getLayer('net-q')) return [];
    var g = f.geometry, cs = g.type === 'LineString' ? g.coordinates : [].concat.apply([], g.coordinates), own = String(f.properties.n || '').toLowerCase();
    var pts = cs.map(function (c) { return map.project(c); }), x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    pts.forEach(function (p) { x0 = Math.min(x0, p.x); y0 = Math.min(y0, p.y); x1 = Math.max(x1, p.x); y1 = Math.max(y1, p.y); });
    var M = 170, hits = map.queryRenderedFeatures([[x0 - M, y0 - M], [x1 + M, y1 + M]], { layers: ['net-q'] });
    var wetNames = {}; segs.forEach(function (s) { if (s.v >= 15 && s.f.properties.n) wetNames[String(s.f.properties.n).toLowerCase().replace(/\bstreet\b/, 'st')] = 1; });
    var mid = map.project(midOf(f)), best = {};
    hits.forEach(function (h) {
      var nm = h.properties.name; if (!nm) return;
      var l = nm.toLowerCase(); if (l === own || (own && (own.indexOf(l) >= 0 || l.indexOf(own) >= 0)) || ends.indexOf(nm) >= 0) return;
      if (wetNames[l.replace(/\bstreet\b/, 'st')]) return;
      var gg = h.geometry, cc = gg.type === 'LineString' ? gg.coordinates : gg.type === 'MultiLineString' ? [].concat.apply([], gg.coordinates) : [];
      cc.forEach(function (c) { var p = map.project(c), d = Math.hypot(p.x - mid.x, p.y - mid.y); if (best[nm] == null || d < best[nm]) best[nm] = d; });
    });
    return Object.keys(best).sort(function (a, b) { return best[a] - best[b]; }).slice(0, 3);
  }
  function openPlace(f, ll) {
    if (!f || !map) return;
    hideTip(); if (popup) popup.remove();
    placeId = f.id;
    var ends = crossStreets(f), cm = segDepth(f.id), st = status(cm, f.id);
    var stc = cm >= 30 ? 'shut' : cm >= 15 ? 'risk' : cm >= 5 ? 'wet' : '';
    var h = popupHtml(f, ends).replace(/<dt>Water on it now<\/dt><dd id="ppNow"[^<]*<\/dd>/, '');
    h = h.replace('</p>', '</p><div class="pl-state"><b id="plNow" data-id="' + f.id + '">' + (cm >= 5 ? cm + ' cm' : 'Dry') + '</b>' +
      (stc ? '<span class="chip-st ' + stc + '" id="plChip">' + (stc === 'shut' ? 'Closed' : stc === 'risk' ? 'At risk' : 'Water on road') + '</span>' : '<span class="chip-st" id="plChip" style="background:var(--surface-2);color:var(--muted)">' + esc(st[1].split(';')[0]) + '</span>') + '</div>');
    var dt = ends.length ? '<p class="pl-btw">Between <b>' + ends.map(esc).join('</b> and <b>') + '</b></p>' : '';
    var act = '<div class="pl-act"><button type="button" class="primary" id="plZoom">Zoom to road</button><button type="button" id="plShare">Share</button></div>';
    $('placeBody').innerHTML = h + dt + act;
    $('place').hidden = false; $('place').classList.remove('tall'); document.documentElement.classList.add('place-on');
    if (small()) { var lg = $('legend'); lg.dataset.pop = 'off'; $('fbLayers').setAttribute('aria-expanded', 'false'); }
    if (map.getLayer('net-hl')) map.setFilter('net-hl', ['in', ['get', 'name'], ['literal', ends]]);
    if (map.getLayer('sel')) map.setFilter('sel', ['==', ['id'], f.id]);
    $('plZoom').addEventListener('click', function () {
      var g = f.geometry, cs = g.type === 'LineString' ? g.coordinates : [].concat.apply([], g.coordinates), bb = [[180, 90], [-180, -90]];
      cs.forEach(function (c) { bb[0][0] = Math.min(bb[0][0], c[0]); bb[0][1] = Math.min(bb[0][1], c[1]); bb[1][0] = Math.max(bb[1][0], c[0]); bb[1][1] = Math.max(bb[1][1], c[1]); });
      var p = framePadding(); if (small()) p.bottom = Math.round($('place').getBoundingClientRect().height) + 20 + (p.bottom > 0 ? 0 : 0);
      map.fitBounds(bb, { padding: p, maxZoom: 15, duration: reduced ? 0 : 800 });
    });
    $('plShare').addEventListener('click', shareView);
    if (small()) { // keep the road above the card
      var pt = map.project(ll || midOf(f)), lim = window.innerHeight - $('place').getBoundingClientRect().height - 40;
      if (pt.y > lim) map.panBy([0, pt.y - lim + 60], { duration: reduced ? 0 : 400 });
    }
  }
  function closePlace() {
    if ($('place').hidden) return;
    $('place').hidden = true; placeId = null; document.documentElement.classList.remove('place-on');
    if (map && map.getLayer('net-hl')) map.setFilter('net-hl', ['in', ['get', 'name'], ['literal', []]]);
    if (map && map.getLayer('sel')) map.setFilter('sel', ['==', ['id'], -1]);
  }
  $('placeX').addEventListener('click', closePlace);
  $('placeGrab').addEventListener('click', function () { $('place').classList.toggle('tall'); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { closePlace(); $('hsheet').hidden = true; } });
  function placeTime() { // live depth on the open card
    var el = document.getElementById('plNow'); if (!el) return;
    var cm = segDepth(+el.dataset.id); el.textContent = cm >= 5 ? cm + ' cm' : 'Dry';
    var c = document.getElementById('plChip'), k = cm >= 30 ? 'shut' : cm >= 15 ? 'risk' : cm >= 5 ? 'wet' : '';
    if (c) { c.className = 'chip-st ' + k; c.textContent = k === 'shut' ? 'Closed' : k === 'risk' ? 'At risk' : k === 'wet' ? 'Water on road' : 'Dry'; c.style.cssText = k ? '' : 'background:var(--surface-2);color:var(--muted)'; }
  }

  // ---------- the water journey on the map ----------
  // runoff: moving-water particles switch on by themselves at street zoom during runoff, rising streams and street flooding,
  // unless the reader has set the layer by hand
  var rainUser = false, rainAutoOn = null;
  $('lyRain').addEventListener('change', function (e) { rainUser = true; rainOp = 0.9; $('rainKey').hidden = !e.target.checked; if (map) map.triggerRepaint(); });
  function rainAuto(mmh) {
    if (!story.on) return; // outside the guided tour the map opens on water and roads only; radar rain is one tick away in Layers
    if (rainUser || story.on || !map || !map.getLayer('rain') || $('rainRow').hidden) return;
    var want = mmh >= 0.5; if (want === rainAutoOn) return; rainAutoOn = want;
    $('lyRain').checked = want; vis('rain', want); $('rainKey').hidden = !want;
    rainOp = 0.9; // shown by itself: about 45 % opacity, the streets stay readable
  }
  var flowUser = false, flowAutoOn = false;
  $('lyFlow').addEventListener('change', function () { flowUser = true; });
  function flowAuto() {
    if (!story.on) return; // moving water is opt-in (Layers) outside the guided tour
    if (flowUser || !map || !map.getLayer('flow') || $('flowRow').hidden) return;
    var k = PH.length ? phaseAt(t) : -1, want = k >= 1 && k <= 3 && map.getZoom() >= 13.4;
    if (want === flowAutoOn) return; flowAutoOn = want;
    $('lyFlow').checked = want; vis('flow', want); $('flowKey').hidden = !want;
  }
  // streams and ponds swell with the river: the gauge's modelled flow (or the observed one) scaled to its storm peak
  var stageSer = null;
  function stageAt() {
    if (stageSer === null) {
      stageSer = false;
      var g = refs && refs.gauges && refs.gauges.filter(function (x) { return (x.model_q && x.model_q.length) || (x.obs_q && x.obs_q.length); })
        .sort(function (a, b) { return (b.km2 || 0) - (a.km2 || 0); })[0];
      if (g) { var a = (g.model_q && g.model_q.length ? g.model_q : g.obs_q).map(function (v) { return v == null ? 0 : v; }), mn = Math.min.apply(0, a), mx = Math.max.apply(0, a); if (mx > mn) stageSer = a.map(function (v) { return (v - mn) / (mx - mn); }); }
    }
    if (!stageSer) return null;
    var i = Math.max(0, Math.min(stageSer.length - 1, Math.round(t))); return stageSer[i];
  }
  var pondLast = -1;
  function pondSwell(v) {
    if (!map || !map.getLayer('h-water')) return;
    v = Math.round(v * 20) / 20; if (v === pondLast) return; pondLast = v;
    var dk = basemap() === 'dark' || basemap() === 'night';
    map.setPaintProperty('h-water', 'fill-color', dk ? 'rgb(' + Math.round(40 + 20 * v) + ',' + Math.round(62 + 40 * v) + ',' + Math.round(82 + 60 * v) + ')'
      : 'rgb(' + Math.round(213 - 60 * v) + ',' + Math.round(221 - 30 * v) + ',' + Math.round(227 - 5 * v) + ')');
    if (map.getLayer('h-water-ol')) { map.setPaintProperty('h-water-ol', 'line-opacity', 0.15 + 0.75 * v); map.setPaintProperty('h-water-ol', 'line-width', 0.6 + 1.8 * v); }
  }
  // soaked in or drained: rain fallen so far (area mean) minus the water still drawn on the land (area mean)
  function soakNow() {
    if (!meta || !meta.surface_mm || !meta.rain_hourly_mean_mm) return;
    var per = 60 / meta.frame_min, tot = sum(meta.rain_hourly_mean_mm, t / per), s = meta.surface_mm[Math.max(0, Math.min(meta.surface_mm.length - 1, Math.round(t)))] || 0;
    var g = Math.max(0, tot - s);
    $('inSoakBox').hidden = false;
    $('inSoak').textContent = (g >= 10 ? Math.round(g) : g.toFixed(1)) + ' mm';
    $('inSoakS').textContent = (s >= 1 ? s.toFixed(1) : s.toFixed(2)) + ' mm still on the land (area average)';
  }
  function appTick() {
    if (!meta) return;
    var per = 60 / meta.frame_min, r = meta.rain_hourly_mean_mm || [], hr = r[Math.floor(t / per)] || 0;
    rainAuto(hr);
    flowAuto();
    var v = stageAt(); if (v != null) pondSwell(v);
    soakNow(); placeTime();
  }

  // ---------- the Live tab: the week ahead, storms coming, forecast health ----------
  var REPO = 'https://github.com/Horus331/mass-flood-watch/blob/main/';
  var fmtDay = new Intl.DateTimeFormat('en-US', { weekday: 'short', timeZone: 'America/New_York' }), fmtMD = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', timeZone: 'America/New_York' });
  var fmtHM = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit', timeZone: 'America/New_York' });
  function ago(d) { var m = Math.round((Date.now() - d.getTime()) / 60000); return m < 2 ? 'just now' : m < 90 ? m + ' min ago' : Math.round(m / 60) + ' h ago'; }
  function zt(x) { return x ? new Date(String(x).replace(/Z?$/, 'Z').replace(/:00ZZ$/, ':00Z')) : null; }
  var ERO = ['none', 'marginal', 'slight', 'moderate', 'high'], ERO_L = { none: 'No risk area', marginal: 'Marginal', slight: 'Slight', moderate: 'Moderate', high: 'High' };
  function liveInit(s) {
    if (curTab !== 'live') return;
    document.documentElement.classList.add('live-mode');
    $('forecastCard').hidden = true; $('live').hidden = false;
    if (small()) { sheetPlace(); setTimeout(function () { sheetDetent('half'); }, 50); }
    var oc = getJson('site/data/' + (params.get('outlook') === 'sample' ? 'outlook_sample.json' : 'outlook.json')).catch(function () { return null; });
    oc.then(function (o) { liveRender(s, o); });
  }
  // docs/proto/forecast/OUTLOOK.md (schema outlook/1): health chip rule, day levels and verdicts come from the feed itself
  function health(s, o) {
    var h = (o && o.health) || {}, issued = zt(h.issued || (o && o.issued)) || zt(s && s.built), next = zt(h.next_update);
    var staleH = h.stale_after_h || 7, cyc = h.forecast_cycle || {};
    var st = !o && !s ? 'fail' : issued && Date.now() - issued.getTime() > staleH * 3600e3 ? 'stale' : h.status === 'failed' ? 'fail' : h.status === 'partial' ? 'partial' : 'ok';
    if (!next && issued) { next = new Date(issued.getTime() + 6 * 3600e3); }
    var running = (cyc.state || (s && s.state)) === 'run';
    return { st: st, issued: issued, next: next, cyc: cyc, h: h, label: { ok: running ? 'OK · flood model running' : 'OK', partial: 'Partial', stale: 'Stale', fail: 'Broken' }[st] };
  }
  function liveRender(s, o) {
    var H = health(s, o), O = o && o.health && o.health.status === 'failed' && o.previous ? o.previous : o;
    $('hdot').className = 'dot ' + (H.st === 'partial' ? 'stale' : H.st);
    $('hchipT').textContent = (H.issued ? 'Updated ' + ago(H.issued) : 'Not updated yet') + (H.next ? ' · next ' + fmtHM.format(H.next) : '') + ' · ' + H.label;
    var days = (O && O.days) || [];
    $('lvTitle').textContent = 'Next 7 days' + (O && O.headline ? '' : '');
    var mx = Math.max.apply(0, days.map(function (d) { return (d.rain && d.rain.town_max_mm) || 0; }).concat([25]));
    var ol = $('week'); ol.innerHTML = '';
    if (O && O.headline) { var hl = document.createElement('li'); hl.className = 'wk-head'; hl.textContent = O.headline; ol.appendChild(hl); }
    for (var i = 0; i < 7; i++) {
      var d = days[i] || null, dd = d && d.date ? new Date(d.date + 'T12:00:00Z') : new Date(Date.now() + i * 864e5);
      var R = d && d.rain, mean = R ? R.d3_mean_mm : null, mxv = R ? R.town_max_mm : null;
      var ero = d && d.ero && ERO.indexOf(d.ero.category) >= 0 ? d.ero.category : null, lv = d ? d.level : null;
      var vc = lv === 4 ? 'run' : lv === 3 ? 'hot' : '', txt = d ? d.verdict || '' : 'Week-ahead feed not published yet';
      var det = d && d.detail && lv != null && lv >= 1 ? d.detail : '';
      var li = document.createElement('li'); li.className = 'day' + (mean == null ? ' na' : '');
      li.innerHTML = '<span class="dn">' + (i === 0 ? 'Today' : d ? esc(d.label.split(' ')[0]) : fmtDay.format(dd)) + '<small>' + (d ? esc(d.label.split(' ').slice(1).join(' ')) : fmtMD.format(dd)) + (d && d.partial ? ' (rest)' : '') + '</small></span>' +
        '<i class="ero ' + (ero || 'na') + '" title="NOAA WPC excessive rainfall risk: ' + (ero ? ERO_L[ero] : 'no outlook for this day') + '"></i>' +
        '<span class="rbar" role="img" aria-label="' + (mean != null ? 'district mean ' + mean.toFixed(1) + ' mm, wettest town ' + (mxv || 0).toFixed(0) + ' mm' : 'no rain figure') + '">' +
        (mean != null ? '<i style="width:' + Math.min(100, 100 * mean / mx).toFixed(1) + '%"></i><u style="left:' + Math.min(99, 100 * (mxv || 0) / mx).toFixed(1) + '%"></u>' : '') + '</span>' +
        '<span class="mm">' + (mean != null ? (mean < 10 ? mean.toFixed(1) : Math.round(mean)) + ' mm' : '–') + (mxv != null ? '<small title="wettest town">max ' + Math.round(mxv) + '</small>' : '') + '</span>' +
        '<span class="vd ' + vc + '">' + esc(txt) + (det ? ' <span class="tw">· ' + esc(det) + '</span>' : '') + (d && d.alerts && d.alerts.length ? ' <span class="al">' + esc(d.alerts.join(', ')) + '</span>' : '') + '</span>';
      ol.appendChild(li);
    }
    var key = document.createElement('li'); key.className = 'ero-key';
    key.innerHTML = '<span><i class="rbar" style="width:16px;display:inline-block"><i style="width:100%"></i></i>district mean</span><span><i style="display:inline-block;width:2px;height:10px;background:var(--ink)"></i>wettest town</span>' +
      '<span>WPC excessive rain risk:</span>' + ERO.slice(1).map(function (e) { return '<span><i class="ero ' + e + '"></i>' + ERO_L[e] + '</span>'; }).join('');
    ol.appendChild(key);
    // storms coming (runs of days at level 2 or more)
    var sb = $('storms'), list = (O && O.storms) || [];
    sb.innerHTML = list.length ? '<h2>Storms coming</h2>' : '';
    list.forEach(function (x) {
      var a = zt(x.start), b = zt(x.end), tw = x.towns_over || [];
      var c = document.createElement('div'); c.className = 'storm lv' + (x.level || 0);
      c.innerHTML = '<h3>' + esc(x.verdict || 'Rain') + '</h3>' +
        '<p>' + (a ? fmtShort.format(a) : esc(x.start_date || '')) + ' – ' + (b ? fmtShort.format(b) : esc(x.end_date || '')) + (x.peak_date ? ' · peak day ' + esc(x.peak_date) : '') + '</p>' +
        '<p><b>' + (x.d3_mean_mm != null ? Math.round(x.d3_mean_mm) + ' mm' : '–') + '</b> district average, <b>' + (x.town_max_mm != null ? Math.round(x.town_max_mm) + ' mm' : '–') + '</b> in ' + esc(x.town_max || 'the wettest town') +
        (x.max6h_mm != null ? ' (' + Math.round(x.max6h_mm) + ' mm in 6 h)' : '') + '</p>' +
        (tw.length ? '<p class="tw">Over the flood-model threshold: ' + tw.map(function (t_) { return esc(t_.town || t_); }).join(', ') + '</p>' : '') +
        (x.ero_max && x.ero_max !== 'none' ? '<p class="tw">WPC excessive rain: ' + esc(ERO_L[x.ero_max] || x.ero_max) + '</p>' : '') +
        (x.alerts && x.alerts.length ? '<p class="tw">NWS: ' + esc(x.alerts.join(', ')) + '</p>' : '');
      sb.appendChild(c);
    });
    var fc = (s && s.headline) || (H.cyc && H.cyc.headline);
    if (fc) sb.insertAdjacentHTML('beforeend', '<h2>Next 48 hours</h2><div class="storm"><h3>' + esc(fc) + '</h3><p>Road closures are modelled only here: the flood model runs when a town is forecast ' +
      (((s && s.gate && s.gate.thresholds) || {}).max6h_mm || 25) + ' mm in 6 h or ' + (((s && s.gate && s.gate.thresholds) || {}).max24h_mm || 40) + ' mm in 24 h (NOAA HRRR).</p></div>');
    // health sheet
    var src = (o && o.sources) || {}, rows = [
      ['Week outlook', H.issued ? 'built ' + fmtShort.format(H.issued) + ' (' + ago(H.issued) + ')' : '–'],
      ['Next update', H.next ? fmtShort.format(H.next) + ' (results usually 10–60 min later)' : '–'],
      ['Rain, days 1–7', src.rain ? (src.rain.ok ? 'NOAA ' + (src.rain.model || '') + ' run ' + (zt(src.rain.run) ? fmtShort.format(zt(src.rain.run)) : src.rain.run || '') : 'missing: ' + (src.rain.error || '')) : '–'],
      ['Excessive rain outlook', src.ero ? (src.ero.ok ? 'NWS WPC, days 1–5' + (src.ero.partial ? ' (some days missing)' : '') : 'missing') : '–'],
      ['NWS alerts', src.alerts ? (src.alerts.ok ? 'fetched ' + (zt(src.alerts.fetched) ? fmtShort.format(zt(src.alerts.fetched)) : '') : 'missing') : '–'],
      ['Flood forecast (HRRR, 48 h)', H.cyc && H.cyc.issued ? 'cycle ' + fmtShort.format(zt(H.cyc.issued)) + ', built ' + (zt(H.cyc.built) ? fmtShort.format(zt(H.cyc.built)) : '–') : (s && s.issued ? 'cycle ' + fmtShort.format(zt(s.issued)) : '–')],
      ['Flood model', (H.cyc.state || (s && s.state)) === 'run' ? 'ran for this cycle: the map shows its closures' : (H.cyc.state || (s && s.state)) === 'error' ? 'run failed' : 'not needed: no town over the rain gate']];
    $('hsBody').innerHTML = '<p><i class="dot ' + (H.st === 'partial' ? 'stale' : H.st) + '" style="display:inline-block;vertical-align:1px;margin-right:6px"></i><b>' + esc(H.label) + '</b>: ' +
      ({ ok: 'every source answered and the six-hourly update is on time.', partial: 'the rain forecast is in; the excessive-rain outlook or the alerts are missing.', stale: 'the last update is more than ' + ((H.h && H.h.stale_after_h) || 7) + ' hours old.', fail: 'the last update has no rain forecast; the previous outlook is shown.' }[H.st]) + '</p>' +
      ((H.h.problems || []).length ? '<p class="tw">' + H.h.problems.map(esc).join('<br>') + '</p>' : '') +
      '<table class="hs-t">' + rows.map(function (r) { return '<tr><td>' + esc(r[0]) + '</td><td>' + esc(r[1]) + '</td></tr>'; }).join('') + '</table>' +
      '<p>' + (H.h.run_url ? '<a href="' + esc(H.h.run_url) + '" target="_blank" rel="noopener">The run that built it</a> · ' : '') + '<a href="' + REPO + 'docs/proto/forecast/HINDCAST.md" target="_blank" rel="noopener">How the forecast scores on past storms</a> · <a href="' + REPO + 'docs/proto/forecast/OUTLOOK.md" target="_blank" rel="noopener">How the week view works</a></p>';
  }
  $('hchip').addEventListener('click', function () { $('hsheet').hidden = !$('hsheet').hidden; });
  $('hsX').addEventListener('click', function () { $('hsheet').hidden = true; });
  if (params.get('debug') === '1') window.__mfwApp = { openPlace: function (id) { var s = segById[id]; if (s) openPlace(s.f); }, closedIds: function () { return segs.filter(function (s) { return s.v >= 30; }).map(function (s) { return s.id; }); },
    detent: function (d) { sheetDetent(d); }, health: function () { $('hsheet').hidden = false; }, roads: function () { openRoads(); } };

})();
