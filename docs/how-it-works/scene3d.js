// How it works: a 3D block of the real ground around WPI (Worcester, MA), built from the model's own input layers
// (proto/site_layers.py). Texture layers, height field and rain grid: how-it-works/data/. Label details: model-tree/tree.json.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const DATA = 'how-it-works/data/';
const S = 100;            // block width in scene units
const VE = 3;             // vertical exaggeration
const BASE = -15;         // block bottom (schematic subsurface)
const CUT = 0.6;          // north-south position of the cut (fraction from north)
const GAP = 15, DROP = 9; // how far the front part slides out and down when the ground is opened
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

const SURF = [
  { k: 'aerial', t: 'Aerial photo', legend: () => '<span class="t">USGS NAIP aerial imagery, about 1 m (resampled)</span>' },
  { k: 'landcover', t: 'Land cover', legend: (m) => (m.layers.landcover.classes || []).map((c) => `<span><i class="sw" style="background:${c[2]}"></i>${esc(c[1])}</span>`).join('') + '<span class="t">NLCD 2021, 30 m</span>' },
  { k: 'runoff', t: 'Runoff potential', legend: (m) => `<span class="t">less runoff</span><i class="bar" style="background:linear-gradient(90deg,#f5f1e6,#e2c896,#c48452,#964e34,#5c2c28)"></i><span class="t">more runoff</span><span class="t">· curve number ${m.layers.runoff.lo}–${m.layers.runoff.hi} (NRCS TR-55), from soils (SSURGO) and land cover</span>` },
  { k: 'terrain', t: 'Terrain and streams', legend: (m) => `<span><i class="sw" style="background:#3a78be"></i>Streams</span><span><i class="sw" style="background:#78a8d6"></i>Ponds and lakes</span><span><i class="sw" style="background:#fff;border:2px solid #194682"></i>Road–stream crossings</span><span class="t">Lidar ground height ${m.layers.terrain.zmin}–${m.layers.terrain.zmax} m, shaded relief</span>` },
  { k: 'roads', t: 'Roads and services', legend: () => '<span><i class="sw" style="background:#fab450"></i>Major roads</span><span><i class="sw" style="background:#969696"></i>Local roads</span><span><i class="sw" style="background:#c82828"></i>Hospital</span><span><i class="sw" style="background:#e66e14"></i>Fire station</span><span><i class="sw" style="background:#2850aa"></i>Police</span>' },
  { k: 'flood', t: 'Flood depth (model)', legend: (m) => `<span class="t">shallow</span><i class="bar" style="background:linear-gradient(90deg,#aacdf0,#3c82d2,#123282)"></i><span class="t">deep</span><span class="t">· peak water depth the model computed for the storm of 19 Aug 2021, shown from ${Math.round(m.layers.flood.min_m * 100)} cm; ${m.layers.flood.res_m} m grid</span>` }
];

// callouts: side (l / r), anchor kind, title, source line, tree.json nodes, plain text for the panel
const CALL = [
  { id: 'obs', side: 'l', k: 'Rain', t: 'Observed rain', s: 'NOAA MRMS radar + gauges · 1 km · hourly', at: 'sky_l', nodes: ['mrms', 'rain_grid'],
    p: 'Radar, corrected with rain gauges, measures the rain on every 1 km square every hour. The squares above the block are the real radar grid for the storm of 19 Aug 2021.' },
  { id: 'fc', side: 'r', k: 'Rain', t: 'Forecast rain', s: 'NOAA HRRR · 3 km · 48 h ahead · 8 runs', at: 'sky_r', nodes: ['hrrr', 'phase', 'members', 'nbhd', 'gate'],
    p: 'For warnings, the newest eight HRRR forecasts replace the radar. Their air temperature splits rain from snow.' },
  { id: 'dem', side: 'l', k: 'Ground', t: 'Ground height', s: 'USGS 3DEP lidar · 10 m → 20 m grid', at: 'peak', nodes: ['lidar', 'dem20', 'breach', 'crest'],
    p: 'Laser scans give the height of the bare ground. Water runs downhill on this surface and pools in its low points.' },
  { id: 'cover', side: 'l', k: 'Surface', t: 'Land cover and pavement', s: 'NLCD 2021 · 30 m · % paved', at: 'downtown', nodes: ['nlcd', 'manning'],
    p: 'Paved surfaces shed almost all the rain; forest and grass slow the water down and soak part of it up.' },
  { id: 'soil', side: 'l', k: 'Below ground', t: 'Soils and runoff', s: 'USDA SSURGO · NRCS curve number (TR-55)', at: 'soil', nodes: ['ssurgo', 'cn', 'wi_amc', 'wi_frozen'],
    p: 'Soil type and land cover set how much of each hour’s rain soaks in and how much runs off.' },
  { id: 'gw', side: 'l', k: 'Below ground', t: 'Groundwater', s: 'not in the model yet', at: 'gw', nodes: ['cc_gw'], lim: true,
    p: 'Rising groundwater under roads and foundations is part of the cascade this research is building toward. It is not in the current model.' },
  { id: 'wpi', side: 'r', k: 'Place', t: 'WPI campus', s: 'Worcester, Massachusetts · 6 × 6 km block', at: 'wpi', nodes: [],
    p: 'The block is centred on the WPI campus. Everything on it is real data for this area.' },
  { id: 'stream', side: 'r', k: 'Water', t: 'Streams and ponds', s: 'USGS NHDPlus HR · carved into the terrain', at: 'pond', nodes: ['nhd', 'channels'],
    p: 'Streams are cut into the ground model to their normal full depth, so they carry water the way the real channels do.' },
  { id: 'culvert', side: 'r', k: 'Water', t: 'Culverts under roads', s: 'NAACC surveys · FHWA HDS-5 capacity', at: 'culvert', nodes: ['crossings', 'notch', 'culvert', 'wi_culvert'],
    p: 'Where a stream passes under a road, the opening lets water through. When more water arrives than the culvert can pass, it backs up and can go over the road.' },
  { id: 'road', side: 'r', k: 'Roads', t: 'Roads', s: 'MassDOT Road Inventory · depth every 10 m', at: 'road', nodes: ['roads', 'roadpts', 'segdepth', 'onset', 'pclose'],
    p: 'The water depth is read every 10 m along every road. About 30 cm of standing water makes a road likely closed.' },
  { id: 'access', side: 'r', k: 'People', t: 'Hospitals, fire and police', s: 'OpenStreetMap · 2020 Census blocks', at: 'hospital', nodes: ['facilities', 'census', 'dijkstra', 'access'],
    p: 'With closed roads taken out of the network, the model finds who can no longer reach a hospital, fire station or police station in time.' },
  { id: 'engine', side: 'r', k: 'Engine', t: 'Flood engine', s: 'LISFLOOD-FP 8.2 · 20 m squares · every 5 min', at: 'engine', nodes: ['lisflood', 'depth', 'velocity'],
    p: 'The engine moves the water across every 20 m square of this block, a second at a time, and records how deep and how fast it is everywhere.' }
];

const CHAIN = [
  { t: 'Water on each road', p: 'Depth is read every 10 m along every road. Only the water the storm added counts, not water already in a stream.', nodes: ['roadpts', 'segdepth', 'onset'] },
  { t: 'How the road fails', p: 'Standing water of about 30 cm closes a road. Culvert capacity, fast water and washout at crossings are checked alongside.', nodes: ['pclose', 'culvert', 'freeboard', 'fastwater', 'washout', 'edge'] },
  { t: 'Detours', p: 'Closed roads come out of the road network, wet roads get slower, and the quickest routes are found again.', nodes: ['graph', 'pregnolato', 'dijkstra'] },
  { t: 'Who loses access', p: 'People who can no longer reach a hospital, fire station or police station within the response standard.', nodes: ['access', 'efficiency'] },
  { t: 'The forecast list', p: 'Before a storm, the model runs on eight weather forecasts. A road closed in at least two of them is listed as likely.', nodes: ['gate', 'members', 'kofn', 'pirank'] },
  { t: 'Checked against reality', p: 'Flood reports and river gauges are used only to check the model afterwards, on storms that were never used to set it.', nodes: ['labels', 'matching', 'metrics', 'baselines', 'split', 'gauges'] }
];

// ------------------------------------------------------------------------------------------------ detail panel (tree.json)
let TREE = {};
const tex = (s, d) => { try { return katex.renderToString(s, { displayMode: !!d, throwOnError: false }); } catch (e) { return esc(s); } };
function fmtVal(p) { let v = p.value; if (typeof v === 'string' && /^[0-9.]+,[0-9.]+$/.test(v)) v = v.replace(',', ', '); if (v === 1 && !p.unit && /parity|fix|switch|enforcement|output|connected/i.test(p.name)) v = 'on'; return v + (p.unit ? ' ' + p.unit : ''); }
function stChip(s) { s = s || ''; return /what-if/.test(s) ? '<span class="st wi">what-if runs</span>' : /can't/.test(s) ? '<span class="st lim">not in the model yet</span>' : /candidate/.test(s) ? '<span class="st wi">extra check</span>' : '<span class="st">in use</span>'; }
function nodeHtml(n) {
  const h = [`<section class="nd"><h3>${esc(n.title)}${stChip(n.status)}</h3><p>${esc(n.plain)}</p>`];
  if (n.what) h.push(`<p>${esc(n.what)}</p>`);
  const meta = [['Units', n.units], ['Resolution', n.resolution], ['Period', n.period], ['How it is used', n.how_used], ['Output', n.output]].filter((r) => r[1] && r[1] !== '—');
  if (meta.length) h.push('<table>' + meta.map((r) => `<tr><td>${r[0]}</td><td>${esc(r[1])}</td></tr>`).join('') + '</table>');
  if (n.formula) { h.push(`<div class="formula">${tex(n.formula, true)}</div>`); if (n.symbols && n.symbols.length) h.push('<table class="sym">' + n.symbols.map((s) => `<tr><td>${tex(s[0])}</td><td>${esc(s[1])}</td></tr>`).join('') + '</table>'); }
  if (n.parameters && n.parameters.length) h.push('<h4>Values used</h4><table>' + n.parameters.map((p) => `<tr><td>${esc(p.name)}<div class="where">${esc(p.origin)}</div></td><td class="v">${esc(fmtVal(p))}</td></tr>`).join('') + '</table>');
  if (n.limits) h.push(`<p class="where"><b>Limits:</b> ${esc(n.limits)}</p>`);
  if (n.source && n.source.length) h.push('<h4>Sources</h4><ul>' + n.source.map((s) => `<li>${s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.text)}</a>` : esc(s.text)}</li>`).join('') + '</ul>');
  h.push('</section>'); return h.join('');
}
function openPanel(kicker, title, plain, ids) {
  const P = $('panel');
  P.innerHTML = `<button class="x" type="button" aria-label="Close">✕</button><p class="k">${esc(kicker)}</p><h2>${esc(title)}</h2><p class="lead">${esc(plain)}</p>` + ids.filter((i) => TREE[i]).map((i) => nodeHtml(TREE[i])).join('');
  P.scrollTop = 0; document.body.classList.add('panel-open'); P.querySelector('.x').onclick = closePanel; P.querySelector('.x').focus({ preventScroll: true });
}
function closePanel() { document.body.classList.remove('panel-open'); mark(null); if (location.hash) history.replaceState(null, '', location.pathname); }
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closePanel(); });

// ------------------------------------------------------------------------------------------------ scene
let M, H, G, renderer, scene, camera, controls, pieces = [], rain = null, rainOn = !reduced, split = 1, splitTarget = 1, sky;
const texCache = {};
const anchors = {};

function hAt(fx, fy) {        // ground height (scene units) at box fractions, bilinear
  const g = G, x = Math.min(Math.max(fx, 0), 1) * g, y = Math.min(Math.max(fy, 0), 1) * g;
  const i = Math.min(Math.floor(x), g - 1), j = Math.min(Math.floor(y), g - 1), a = x - i, b = y - j, n = g + 1;
  const v = (r, c) => H[r * n + c];
  return (v(j, i) * (1 - a) * (1 - b) + v(j, i + 1) * a * (1 - b) + v(j + 1, i) * (1 - a) * b + v(j + 1, i + 1) * a * b);
}
const toX = (fx) => (fx - 0.5) * S, toZ = (fy) => (fy - 0.5) * S;
const ll2f = (lon, lat) => {   // small-area conversion around the block centre (WPI), good to a few metres here
  const c = M.anchors.wpi; return [c[0] + (lon + 71.8085) * Math.cos(42.2746 * Math.PI / 180) * 111320 / M.width_m, c[1] - (lat - 42.2746) * 110574 / M.height_m];
};

function terrainGeometry(r0, r1) {
  const n = G + 1, rows = r1 - r0 + 1, pos = new Float32Array(rows * n * 3), uv = new Float32Array(rows * n * 2), idx = [];
  for (let r = 0; r < rows; r++) for (let c = 0; c < n; c++) {
    const k = r * n + c, fx = c / G, fy = (r0 + r) / G;
    pos[k * 3] = toX(fx); pos[k * 3 + 1] = H[(r0 + r) * n + c]; pos[k * 3 + 2] = toZ(fy);
    uv[k * 2] = fx; uv[k * 2 + 1] = 1 - fy;
  }
  for (let r = 0; r < rows - 1; r++) for (let c = 0; c < n - 1; c++) { const a = r * n + c, b = a + 1, d = a + n, e = d + 1; idx.push(a, d, b, b, d, e); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals(); return g;
}

const wallMat = new THREE.ShaderMaterial({
  uniforms: { meanTop: { value: 0 }, shade: { value: 1 } },
  vertexShader: `attribute float aTop; attribute float aS; varying float vTop; varying float vY; varying float vS; varying vec3 vN;
    void main(){ vTop=aTop; vY=position.y; vS=aS; vN=normal; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader: `uniform float meanTop; varying float vTop; varying float vY; varying float vS; varying vec3 vN;
    float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453); }
    void main(){
      float d=vTop-vY;
      float rock=-7.0+1.4*sin(vS*0.11)+0.8*sin(vS*0.31+1.3);
      float wt=mix(vTop-3.0,meanTop-4.2,0.55);
      vec3 c;
      if(d<0.9) c=vec3(0.27,0.20,0.15);
      else if(d<3.2) c=vec3(0.55,0.40,0.27);
      else if(vY>rock) c=vec3(0.80,0.70,0.53);
      else c=vec3(0.50,0.51,0.54);
      float g=h(floor(vec2(vS*4.0,vY*4.0)));
      if(vY>rock && d>=3.2 && g>0.93) c*=0.82;
      if(vY<=rock){ float k=h(floor(vec2(vS*0.9,vY*1.6))); if(k>0.9) c*=0.86; }
      if(vY<wt && vY>rock && d>=0.9) c=mix(c,vec3(0.40,0.62,0.86),0.22);
      if(abs(vY-wt)<0.09 && d>=0.9 && vY>rock && mod(vS,1.6)<1.0) c=vec3(0.13,0.40,0.80);
      float l=0.82+0.18*abs(vN.x)+0.08*vN.z;
      gl_FragColor=vec4(c*l,1.0);
    }`
});

function wallGeometry(pts) {      // pts: [{x,z,top,s}] along the edge -> vertical strip from top to BASE
  const n = pts.length, pos = new Float32Array(n * 2 * 3), top = new Float32Array(n * 2), s = new Float32Array(n * 2), idx = [];
  pts.forEach((p, i) => {
    pos.set([p.x, p.top, p.z, p.x, BASE, p.z], i * 6); top[i * 2] = top[i * 2 + 1] = p.top; s[i * 2] = s[i * 2 + 1] = p.s;
    if (i < n - 1) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 2, a + 1, a + 3); }
  });
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('aTop', new THREE.BufferAttribute(top, 1)); g.setAttribute('aS', new THREE.BufferAttribute(s, 1)); g.setIndex(idx); g.computeVertexNormals(); return g;
}
function edge(fx0, fy0, fx1, fy1) {
  const pts = [], n = G; for (let i = 0; i <= n; i++) { const t = i / n, fx = fx0 + (fx1 - fx0) * t, fy = fy0 + (fy1 - fy0) * t; pts.push({ x: toX(fx), z: toZ(fy), top: hAt(fx, fy), s: (fx + fy) * S }); }
  return pts;
}

function piece(fy0, fy1) {
  const grp = new THREE.Group(), r0 = Math.round(fy0 * G), r1 = Math.round(fy1 * G);
  const top = new THREE.Mesh(terrainGeometry(r0, r1), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.95, metalness: 0 }));
  grp.add(top); grp.userData.top = top;
  const walls = [edge(0, fy0, 1, fy0), edge(0, fy1, 1, fy1), edge(0, fy0, 0, fy1), edge(1, fy0, 1, fy1)];
  walls.forEach((w) => grp.add(new THREE.Mesh(wallGeometry(w), wallMat)));
  const bottom = new THREE.Mesh(new THREE.PlaneGeometry(S, (fy1 - fy0) * S), new THREE.MeshBasicMaterial({ color: 0x6e7177 }));
  bottom.rotation.x = Math.PI / 2; bottom.position.set(0, BASE, toZ((fy0 + fy1) / 2)); grp.add(bottom);
  scene.add(grp); return grp;
}

function rainCanvas() {
  const R = M.rain_grid, n = R.length, m = R[0].length, cv = document.createElement('canvas'); cv.width = m; cv.height = n;
  const x = cv.getContext('2d'), im = x.createImageData(m, n), lo = M.layers.rain.lo, hi = M.layers.rain.hi;
  const st = [[0, [232, 240, 250]], [0.4, [150, 190, 232]], [0.75, [88, 120, 210]], [1, [96, 60, 170]]];
  for (let j = 0; j < n; j++) for (let i = 0; i < m; i++) {
    const v = Math.min(Math.max((R[j][i] - lo) / Math.max(hi - lo, 1), 0), 1); let k = 0; while (k < st.length - 2 && v > st[k + 1][0]) k++;
    const t = (v - st[k][0]) / (st[k + 1][0] - st[k][0]), c = st[k][1].map((a, q) => a + (st[k + 1][1][q] - a) * t), o = (j * m + i) * 4;
    im.data[o] = c[0]; im.data[o + 1] = c[1]; im.data[o + 2] = c[2]; im.data[o + 3] = 255;
  }
  x.putImageData(im, 0, 0); const t = new THREE.CanvasTexture(cv); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.colorSpace = THREE.SRGBColorSpace; return t;
}

function buildSky() {
  const top = Math.max(...H), y = top + 30, grp = new THREE.Group();
  const plane = new THREE.Mesh(new THREE.PlaneGeometry(S, S), new THREE.MeshBasicMaterial({ map: rainCanvas(), transparent: true, opacity: 0.42, side: THREE.DoubleSide, depthWrite: false }));
  plane.rotation.x = -Math.PI / 2; plane.position.y = y; grp.add(plane);
  const km = 1000 / M.width_m * S, lines = [];               // the 1 km radar grid
  for (let v = -S / 2; v <= S / 2 + 1e-6; v += km) { lines.push(-S / 2, y + 0.02, v, S / 2, y + 0.02, v, v, y + 0.02, -S / 2, v, y + 0.02, S / 2); }
  const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.Float32BufferAttribute(lines, 3));
  grp.add(new THREE.LineSegments(lg, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.55 })));
  const box = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(S, 0.01, S)), new THREE.LineBasicMaterial({ color: 0x5b7fb5 }));
  box.position.y = y; grp.add(box);
  // falling rain
  const N = 1600, P = new Float32Array(N * 6), seed = []; let s = 7; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < N; i++) { const fx = rnd(), fy = rnd(); seed.push({ x: toX(fx), z: toZ(fy), g: hAt(fx, fy), o: rnd() }); }
  const rg = new THREE.BufferGeometry(); rg.setAttribute('position', new THREE.BufferAttribute(P, 3));
  const rl = new THREE.LineSegments(rg, new THREE.LineBasicMaterial({ color: 0x4f86d0, transparent: true, opacity: 0.42 }));
  grp.add(rl); scene.add(grp); rain = { seed, P, rg, y, rl }; sky = y; stepRain(0);
}
function stepRain(t) {
  const { seed, P, rg, y } = rain;
  seed.forEach((d, i) => {
    const span = y - d.g, ph = ((d.o + t * 0.00011) % 1), yy = y - ph * span, z = d.z + (split < 0.5 ? 0 : 0);
    const fr = d.z > toZ(CUT), off = fr ? split * GAP : 0, yy2 = fr ? Math.max(yy - split * DROP * ph, d.g - split * DROP) : yy;
    if (d.z + off > S / 2) { P.fill(0, i * 6, i * 6 + 6); P[i * 6 + 1] = P[i * 6 + 4] = -999; return; }
    P.set([d.x, yy2, d.z + off, d.x - 0.25, Math.min(yy2 + 1.6, y), d.z + off], i * 6);
  });
  rg.attributes.position.needsUpdate = true;
}

function loadTex(k) {
  if (texCache[k]) return Promise.resolve(texCache[k]);
  return new Promise((ok) => new THREE.TextureLoader().load(DATA + k + '.jpg', (t) => { t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = renderer.capabilities.getMaxAnisotropy(); texCache[k] = t; ok(t); }));
}
async function setSurface(k) {
  const t = await loadTex(k);
  pieces.forEach((p) => { p.userData.top.material.map = t; p.userData.top.material.needsUpdate = true; });
  document.querySelectorAll('#surfaces .chip').forEach((b) => b.setAttribute('aria-pressed', b.dataset.k === k));
  const s = SURF.find((x) => x.k === k); $('legend').innerHTML = s.legend(M);
  try { localStorage.setItem('mfw-hiw-surface', k); } catch (e) {}
}

function setAnchors() {
  const yTop = (fx, fy) => hAt(fx, fy);
  const peak = (() => { let b = 0, bi = 0; for (let i = 0; i < H.length; i++) if (H[i] > b) { b = H[i]; bi = i; } const n = G + 1; return [(bi % n) / G, Math.floor(bi / n) / G]; })();
  const pk = peak[1] > CUT ? peak : [peak[0], Math.min(peak[1], CUT - 0.05)];
  const f = {
    wpi: M.anchors.wpi, peak: pk, downtown: ll2f(-71.8023, 42.2626), pond: ll2f(-71.8048, 42.2774),
    culvert: (M.crossings.filter((c) => c.stream).sort((a, b) => Math.hypot(a.at[0] - 0.5, a.at[1] - 0.45) - Math.hypot(b.at[0] - 0.5, b.at[1] - 0.45))[0] || { at: [0.4, 0.4] }).at,
    road: M.road_anchor ? M.road_anchor.at : [0.62, 0.5],
    hospital: ((M.layers.roads.facilities || []).filter((x) => x[0] === 'hospital').sort((a, b) => Math.hypot(a[2] - 0.5, a[3] - 0.5) - Math.hypot(b[2] - 0.5, b[3] - 0.5))[0] || [0, 0, 0.7, 0.3]).slice(2),
    engine: [0.3, 0.82]
  };
  for (const k in f) { const [fx, fy] = f[k]; anchors[k] = { p: new THREE.Vector3(toX(fx), yTop(fx, fy) + 0.3, toZ(fy)), front: fy > CUT }; }
  anchors.sky_l = { p: new THREE.Vector3(-S * 0.32, sky, -S * 0.1) };
  anchors.sky_r = { p: new THREE.Vector3(S * 0.36, sky, -S * 0.3) };
  const fxs = 0.3, ts = hAt(fxs, CUT);
  anchors.soil = { p: new THREE.Vector3(toX(fxs), ts - 1.9, toZ(CUT) + 0.05), front: false };
  const meanTop = H.reduce((a, b) => a + b, 0) / H.length, fxg = 0.62, tg = hAt(fxg, CUT);
  anchors.gw = { p: new THREE.Vector3(toX(fxg), (tg - 3.0) * 0.45 + (meanTop - 4.2) * 0.55, toZ(CUT) + 0.05), front: false };
  wallMat.uniforms.meanTop.value = meanTop;
}

// ------------------------------------------------------------------------------------------------ callouts + leader lines
const NS = 'http://www.w3.org/2000/svg';
let narrow = false, order = { l: [], r: [] };
function buildCallouts() {
  const box = $('callouts'), svg = $('leaders');
  CALL.forEach((c, i) => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'co ' + c.side + (c.lim ? ' lim' : ''); b.dataset.id = c.id;
    b.innerHTML = `<span class="n">${i + 1}</span><span class="k">${esc(c.k)}</span><b>${esc(c.t)}</b><span class="s">${esc(c.s)}</span>`;
    b.onclick = () => show(c); box.appendChild(b); c.el = b;
    const g = document.createElementNS(NS, 'g'); g.dataset.id = c.id;
    c.ln = document.createElementNS(NS, 'line'); if (c.lim) c.ln.setAttribute('class', 'lim'); c.dot = document.createElementNS(NS, 'circle'); c.dot.setAttribute('r', 4);
    g.append(c.ln, c.dot); svg.appendChild(g); c.g = g;
    const bd = document.createElement('div'); bd.className = 'badge'; bd.textContent = i + 1; bd.onclick = () => show(c); $('stage').appendChild(bd); c.badge = bd;
  });
}
function show(c) { mark(c.id); openPanel(c.k, c.t, c.p, c.nodes); history.replaceState(null, '', '#' + c.id); }
function mark(id) { CALL.forEach((c) => { const on = c.id === id; c.el.classList.toggle('on', on); c.el.classList.toggle('dim', !!id && !on); c.ln.classList.toggle('on', on); c.dot.classList.toggle('on', on); }); }
function screen(c) {
  const a = anchors[c.at]; if (!a) return null;
  const v = a.p.clone(); if (a.front) { v.z += split * GAP; v.y -= split * DROP; }
  v.project(camera); const R = renderer.domElement.getBoundingClientRect();
  return { x: (v.x + 1) / 2 * R.width, y: (1 - v.y) / 2 * R.height, behind: v.z > 1 };
}
function resort() {   // order each column by where its anchors are on screen, so leader lines do not cross
  ['l', 'r'].forEach((sd) => { order[sd] = CALL.filter((c) => c.side === sd).map((c) => ({ c, y: (screen(c) || { y: 0 }).y })).sort((a, b) => a.y - b.y).map((o) => o.c); });
}
function layoutCallouts() {
  const R = renderer.domElement.getBoundingClientRect(), W = R.width, Hh = R.height;
  if (narrow) { CALL.forEach((c) => { const p = screen(c); if (p) { c.badge.style.left = p.x + 'px'; c.badge.style.top = p.y + 'px'; } }); return; }
  ['l', 'r'].forEach((sd) => {
    const list = order[sd], n = list.length, top = 22, gap = (Hh - top - 30) / n;
    list.forEach((c, i) => {
      const el = c.el, w = el.offsetWidth, h = el.offsetHeight, x = sd === 'l' ? 20 : W - 20 - w, y = top + i * gap + (gap - h) / 2;
      el.style.left = x + 'px'; el.style.top = y + 'px';
      const p = screen(c); if (!p) return;
      const lx = sd === 'l' ? x + w + 6 : x - 6, ly = y + h / 2;
      c.ln.setAttribute('x1', lx); c.ln.setAttribute('y1', ly); c.ln.setAttribute('x2', p.x); c.ln.setAttribute('y2', p.y);
      c.dot.setAttribute('cx', p.x); c.dot.setAttribute('cy', p.y);
    });
  });
}

// ------------------------------------------------------------------------------------------------ main
function resize() {
  const st = $('stage'), w = st.clientWidth, h = st.clientHeight;
  renderer.setSize(w, h, false); camera.aspect = w / h;
  narrow = w < 860;
  const host = narrow ? $('stage').parentNode : $('stage'), co = $('callouts');
  if (narrow && co.parentNode === $('stage')) $('stage').after(co); else if (!narrow && co.parentNode !== $('stage')) $('stage').insertBefore(co, $('loading'));
  camera.fov = narrow ? 50 : 34; camera.updateProjectionMatrix(); resort(); layoutCallouts();
}
const HOME = { pos: new THREE.Vector3(150, 105, 205), target: new THREE.Vector3(0, 4, 10) };
function home() { camera.position.copy(HOME.pos); controls.target.copy(HOME.target); controls.update(); resort(); }

async function init() {
  const [meta, hb, tree] = await Promise.all([fetch(DATA + 'layers.json').then((r) => r.json()), fetch(DATA + 'height.bin').then((r) => r.arrayBuffer()), fetch('model-tree/tree.json').then((r) => r.json()).catch(() => ({ nodes: [] }))]);
  M = meta; G = M.grid; tree.nodes.forEach((n) => { TREE[n.id] = n; });
  const u = new Uint16Array(hb), mpu = M.width_m / S; H = new Float32Array(u.length);
  for (let i = 0; i < u.length; i++) H[i] = (u[i] / 65535 * (M.zmax - M.zmin)) * VE / mpu;
  renderer = new THREE.WebGLRenderer({ canvas: $('gl'), antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.outputColorSpace = THREE.SRGBColorSpace;
  scene = new THREE.Scene(); camera = new THREE.PerspectiveCamera(34, 1, 1, 2000);
  scene.add(new THREE.HemisphereLight(0xffffff, 0xb9b2a6, 1.6));
  const sun = new THREE.DirectionalLight(0xffffff, 1.5); sun.position.set(-80, 120, 40); scene.add(sun);
  pieces = [piece(0, CUT), piece(CUT, 1)];
  pieces[1].position.set(0, -split * DROP, split * GAP);
  buildSky(); setAnchors();
  controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping = true; controls.dampingFactor = 0.08;
  controls.minDistance = 70; controls.maxDistance = 420; controls.maxPolarAngle = Math.PI * 0.49; controls.enablePan = false;
  controls.addEventListener('end', () => { resort(); });
  home();
  // surface chips
  $('surfaces').innerHTML = SURF.filter((s) => M.layers[s.k]).map((s) => `<button class="chip" type="button" data-k="${s.k}" aria-pressed="false">${esc(s.t)}</button>`).join('');
  document.querySelectorAll('#surfaces .chip').forEach((b) => { b.onclick = () => setSurface(b.dataset.k); });
  let first = 'aerial'; try { first = localStorage.getItem('mfw-hiw-surface') || first; } catch (e) {}
  if (!M.layers[first]) first = Object.keys(M.layers)[0];
  buildCallouts(); await setSurface(first);
  $('figNote').textContent = `Real data for a ${M.width_m / 1000} × ${M.height_m / 1000} km block centred on WPI. Heights are exaggerated ${VE}×. The soil layers and groundwater on the cut faces are drawn to show the idea, not measured. Rain above the block: radar storm total for 19 Aug 2021 on the 1 km radar grid.`;
  $('bSplit').onclick = () => { splitTarget = splitTarget ? 0 : 1; $('bSplit').querySelector('span').textContent = splitTarget ? 'Close the ground' : 'Open the ground'; $('bSplit').setAttribute('aria-pressed', !!splitTarget); };
  $('bRain').onclick = () => { rainOn = !rainOn; $('bRain').querySelector('span').textContent = rainOn ? 'Pause rain' : 'Play rain'; $('bRain').setAttribute('aria-pressed', rainOn); };
  if (!rainOn) $('bRain').querySelector('span').textContent = 'Play rain';
  $('bReset').onclick = home;
  $('chain').innerHTML = CHAIN.map((c, i) => `<li><button type="button" data-i="${i}"><b>${esc(c.t)}</b><span>${esc(c.p)}</span></button></li>`).join('');
  document.querySelectorAll('#chain button').forEach((b) => { b.onclick = () => { const c = CHAIN[+b.dataset.i]; mark(null); openPanel('Step ' + (+b.dataset.i + 1), c.t, c.p, c.nodes); }; });
  addEventListener('resize', resize); resize();
  const h = location.hash.slice(1), c0 = CALL.find((c) => c.id === h); if (c0) show(c0);
  $('loading').classList.add('gone');
  let last = 0;
  renderer.setAnimationLoop((t) => {
    if (Math.abs(split - splitTarget) > 1e-3) { split += (splitTarget - split) * (reduced ? 1 : 0.08); pieces[1].position.set(0, -split * DROP, split * GAP); }
    else if (split !== splitTarget) { split = splitTarget; pieces[1].position.set(0, -split * DROP, split * GAP); }
    if (rainOn) stepRain(t); rain.rl.visible = rainOn || reduced;
    controls.update(); renderer.render(scene, camera);
    if (t - last > 30) { layoutCallouts(); last = t; }
  });
}
init().catch((e) => { $('loading').textContent = 'Could not load the 3D view: ' + e.message; console.error(e); });
