// WPI campus, layer by layer: three slabs of the same real ground (USGS lidar), exploded like a map stack.
//   bottom: what the ground does with rain (soils + land cover -> runoff potential), cut open to show soil layers
//   middle: the place itself (aerial photo on the lidar terrain, buildings from OpenStreetMap)
//   top:    what the model computes (peak water from the flood engine, flow paths on the lidar, roads as the model rated them)
// Data: how-it-works/campus/ (proto/site_layers.py campus). Details panel: window.MFW from scene3d.js (tree.json).
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const DIR = 'how-it-works/campus/';
const S = 100, VE = 2.2, GAP = 34, THICK = 1.4, SOIL = 11;
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const ROAD_C = { closed: '#d93025', risk: '#f29900', wet: '#4285f4' };

const CALL = [
  { id: 'rain', side: 'l', k: 'Rain', t: 'Rain on the hill', s: 'NOAA MRMS radar + gauges · 1 km · hourly', at: 'sky', nodes: ['mrms', 'rain_grid'],
    p: 'Radar rain falls on every square of the ground. On the storm of 19 Aug 2021 most of it fell in two hours.' },
  { id: 'water', side: 'r', k: 'Model output', t: 'Where the water collects', s: 'LISFLOOD-FP 8.2 · peak depth · 20 m grid', at: 'water', nodes: ['lisflood', 'depth', 'velocity'],
    p: 'The flood engine moves the rain across the ground and records the deepest water on every 20 m square. Blue shows where it reached at least 5 cm in the storm of 19 Aug 2021.' },
  { id: 'flow', side: 'r', k: 'Model output', t: 'How the water runs downhill', s: 'Flow paths traced on the 1 m lidar', at: 'flow', nodes: ['breach'],
    p: 'The moving dots follow the paths water takes downhill from the hill, along the streets and into Salisbury Pond, traced on the lidar ground surface. They show the direction of flow; the depths come from the flood engine.' },
  { id: 'roads', side: 'r', k: 'Model output', t: 'Roads the model closed', s: 'Depth every 10 m · 30 cm closes a road', at: 'road', nodes: ['roadpts', 'segdepth', 'onset', 'pclose'],
    p: 'Red roads had about 30 cm of standing water or more in the model run for this storm; orange roads were at risk. This is the same run shown on the map.' },
  { id: 'wpi', side: 'r', k: 'The place', t: 'WPI campus', s: 'Worcester, Massachusetts · 1.8 × 1.8 km', at: 'wpi', nodes: [],
    p: 'The campus sits on a hill. Rain that falls on it and on the slopes around it runs down the streets toward Salisbury Pond and Institute Park.' },
  { id: 'pond', side: 'r', k: 'The place', t: 'Salisbury Pond', s: 'USGS NHDPlus HR · streams carved into the terrain', at: 'pond', nodes: ['nhd', 'channels'],
    p: 'Ponds and streams are part of the ground model. Water that reaches them is carried on downstream.' },
  { id: 'dem', side: 'l', k: 'The place', t: 'Ground height', s: 'USGS 3DEP lidar · 1 m (shown) · 20 m in the model', at: 'peak', nodes: ['lidar', 'dem20', 'crest'],
    p: 'Laser scans give the bare-ground height. Heights here are exaggerated ' + VE + '× so the slopes are easy to see.' },
  { id: 'bld', side: 'l', k: 'The place', t: 'Buildings', s: '© OpenStreetMap contributors · for orientation', at: 'bld', nodes: [],
    p: 'Buildings are drawn so the campus is easy to recognise. The flood engine works on the bare-ground surface; buildings and pavement enter through how fast water moves over each square (Manning roughness from land cover).' },
  { id: 'soil', side: 'l', k: 'Below ground', t: 'Soils and runoff', s: 'USDA SSURGO + NLCD 2021 → curve number', at: 'soilTop', nodes: ['ssurgo', 'nlcd', 'cn'],
    p: 'Darker ground sheds more of the rain: pavement, roofs and tight soils. Lighter ground soaks more of it in. This is the curve number the model uses on every square.' },
  { id: 'layers', side: 'l', k: 'Below ground', t: 'Soil layers', s: 'drawn to show the idea · not measured', at: 'soilWall', nodes: ['wi_amc', 'wi_frozen'],
    p: 'Topsoil, subsoil, glacial till and bedrock. How wet or frozen the upper layers are changes how much rain they can take; the model can run dry, soaked and frozen ground as what-if cases.' },
  { id: 'gw', side: 'l', k: 'Below ground', t: 'Groundwater', s: 'not in the model yet', at: 'gw', nodes: ['cc_gw'], lim: true,
    p: 'Rising groundwater under roads and foundations is part of the cascade this research is building toward. It is not in the current model.' }
];

let HMAX = 0, M, H, G, renderer, scene, camera, controls, slabs = [], particles = null, rain = null, playing = !reduced, wasNarrow = null, narrow = false;
const anchors = {};

function hAt(fx, fy) {
  const g = G, x = Math.min(Math.max(fx, 0), 1) * g, y = Math.min(Math.max(fy, 0), 1) * g;
  const i = Math.min(Math.floor(x), g - 1), j = Math.min(Math.floor(y), g - 1), a = x - i, b = y - j, n = g + 1, v = (r, c) => H[r * n + c];
  return v(j, i) * (1 - a) * (1 - b) + v(j, i + 1) * a * (1 - b) + v(j + 1, i) * (1 - a) * b + v(j + 1, i + 1) * a * b;
}
const toX = (fx) => (fx - 0.5) * S, toZ = (fy) => (fy - 0.5) * S;

function terrainGeometry(step) {
  const g = G / step, n = g + 1, pos = new Float32Array(n * n * 3), uv = new Float32Array(n * n * 2), idx = [];
  for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) {
    const k = r * n + c, fx = c / g, fy = r / g; pos.set([toX(fx), H[(r * step) * (G + 1) + c * step], toZ(fy)], k * 3); uv.set([fx, 1 - fy], k * 2);
  }
  for (let r = 0; r < n - 1; r++) for (let c = 0; c < n - 1; c++) { const a = r * n + c, b = a + 1, d = a + n, e = d + 1; idx.push(a, d, b, b, d, e); }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  geo.setIndex(idx); geo.computeVertexNormals(); return geo;
}

const soilMat = new THREE.ShaderMaterial({
  uniforms: { meanTop: { value: 0 } },
  vertexShader: `attribute float aTop; attribute float aS; varying float vTop; varying float vY; varying float vS; varying vec3 vN;
    void main(){ vTop=aTop; vY=position.y; vS=aS; vN=normal; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
  fragmentShader: `uniform float meanTop; varying float vTop; varying float vY; varying float vS; varying vec3 vN;
    float h(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453); }
    void main(){
      float d=vTop-vY, rock=meanTop-8.2+0.9*sin(vS*0.13)+0.5*sin(vS*0.41+1.3), wt=mix(vTop-2.6,meanTop-3.6,0.6);
      vec3 c;
      if(d<0.7) c=vec3(0.27,0.20,0.15); else if(d<2.4) c=vec3(0.55,0.40,0.27); else if(vY>rock) c=vec3(0.80,0.70,0.53); else c=vec3(0.50,0.51,0.54);
      float g=h(floor(vec2(vS*5.0,vY*5.0))); if(vY>rock && d>=2.4 && g>0.93) c*=0.82;
      if(vY<=rock){ float k=h(floor(vec2(vS*1.2,vY*2.0))); if(k>0.9) c*=0.86; }
      if(vY<wt && vY>rock && d>=0.7) c=mix(c,vec3(0.40,0.62,0.86),0.22);
      if(abs(vY-wt)<0.07 && d>=0.7 && vY>rock && mod(vS,1.4)<0.9) c=vec3(0.13,0.40,0.80);
      gl_FragColor=vec4(c*(0.84+0.16*abs(vN.x)),1.0);
    }`
});
const sideMat = (col) => new THREE.MeshStandardMaterial({ color: col, roughness: 1 });

function wall(fx0, fy0, fx1, fy1, depth) {      // vertical strip under an edge, from the surface down `depth` units
  const n = G, pos = new Float32Array((n + 1) * 6), top = new Float32Array((n + 1) * 2), s = new Float32Array((n + 1) * 2), idx = [];
  for (let i = 0; i <= n; i++) {
    const t = i / n, fx = fx0 + (fx1 - fx0) * t, fy = fy0 + (fy1 - fy0) * t, y = hAt(fx, fy), x = toX(fx), z = toZ(fy);
    pos.set([x, y, z, x, -depth, z], i * 6); top[i * 2] = top[i * 2 + 1] = y; s[i * 2] = s[i * 2 + 1] = (fx + fy) * S;
    if (i < n) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 2, a + 1, a + 3); }
  }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('aTop', new THREE.BufferAttribute(top, 1));
  g.setAttribute('aS', new THREE.BufferAttribute(s, 1)); g.setIndex(idx); g.computeVertexNormals(); return g;
}
function slab(tex, depth, side, y) {
  const grp = new THREE.Group(), top = new THREE.Mesh(terrainGeometry(narrow ? 3 : 2), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.95 }));
  grp.add(top); grp.userData.top = top;
  [[0, 0, 1, 0], [0, 1, 1, 1], [0, 0, 0, 1], [1, 0, 1, 1]].forEach((e) => grp.add(new THREE.Mesh(wall(...e, depth), side)));
  const bottom = new THREE.Mesh(new THREE.PlaneGeometry(S, S), sideMat(0x6e7177)); bottom.rotation.x = Math.PI / 2; bottom.position.y = -depth; grp.add(bottom);
  grp.position.y = y; scene.add(grp); slabs.push(grp); return grp;
}

function loadTex(name) {
  return new Promise((ok) => new THREE.TextureLoader().load(DIR + name, (t) => { t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = renderer.capabilities.getMaxAnisotropy(); ok(t); }));
}
async function modelTexture(R) {     // the model layer: water + flow lines image, with every road and the model's road ratings drawn on top
  const img = await new Promise((ok) => { const i = new Image(); i.onload = () => ok(i); i.src = DIR + 'model.jpg'; });
  const N = 4096, cv = document.createElement('canvas'); cv.width = cv.height = N; const x = cv.getContext('2d');
  x.drawImage(img, 0, 0, N, N); x.lineCap = 'round'; x.lineJoin = 'round';
  const path = (pts) => { x.beginPath(); pts.forEach((p, i) => (i ? x.lineTo(p[0] * N, p[1] * N) : x.moveTo(p[0] * N, p[1] * N))); x.stroke(); };
  x.strokeStyle = 'rgba(255,255,255,.95)'; R.all.forEach((r) => { x.lineWidth = r.c >= 1 ? 16 : 9; path(r.pts); });
  x.strokeStyle = 'rgba(120,124,130,.55)'; R.all.forEach((r) => { x.lineWidth = r.c >= 1 ? 11 : 5; path(r.pts); });
  ['wet', 'risk', 'closed'].forEach((s) => { x.strokeStyle = ROAD_C[s]; R.status.filter((r) => r.s === s).forEach((r) => { x.lineWidth = s === 'closed' ? 20 : 14; path(r.pts); }); });
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = renderer.capabilities.getMaxAnisotropy(); return t;
}

function buildings(B) {
  const geos = [], mpu = M.width_m / S;
  B.buildings.forEach((b) => {
    if (b.p.length < 4) return;
    const sh = new THREE.Shape(b.p.map((p) => new THREE.Vector2(toX(p[0]), -toZ(p[1]))));
    let base = Infinity; b.p.forEach((p) => { base = Math.min(base, hAt(p[0], p[1])); });
    const hgt = Math.max(0.25, b.h * VE / mpu * 0.9);
    const g = new THREE.ExtrudeGeometry(sh, { depth: hgt + 0.3, bevelEnabled: false }); g.rotateX(-Math.PI / 2); g.translate(0, base - 0.3, 0);
    geos.push(g.toNonIndexed ? g.toNonIndexed() : g);
  });
  if (!geos.length) return null;
  const m = new THREE.Mesh(mergeGeometries(geos, false), new THREE.MeshStandardMaterial({ color: 0xf1efe9, roughness: 0.85 }));
  return m;
}

// flow particles on the model layer, moving cell to cell along the D8 directions (how-it-works/campus/flowdir.bin)
function buildParticles(dir, acc) {
  const F = M.flow.grid, N = narrow ? 2200 : 5200, pos = new Float32Array(N * 3), col = new Float32Array(N * 3), st = [];
  const DR = [-1, -1, 0, 1, 1, 1, 0, -1], DC = [0, 1, 1, 1, 0, -1, -1, -1];
  let seed = 11; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const zN = (r, c) => hAt((c + 0.5) / F, (r + 0.5) / F);
  const zmax = HMAX;
  function spawn(p) { for (let k = 0; k < 20; k++) { const r = Math.floor(rnd() * F), c = Math.floor(rnd() * F); if (dir[r * F + c] === 255) continue; if (rnd() < 0.25 + 0.75 * zN(r, c) / zmax) { p.r = r; p.c = c; p.t = rnd(); p.age = 0; return; } } p.r = Math.floor(rnd() * F); p.c = Math.floor(rnd() * F); p.t = 0; p.age = 0; }
  for (let i = 0; i < N; i++) { const p = {}; spawn(p); p.age = Math.floor(rnd() * 400); st.push(p); }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const mat = new THREE.PointsMaterial({ size: narrow ? 0.55 : 0.42, vertexColors: true, transparent: true, opacity: 0.95, depthWrite: false });
  const pts = new THREE.Points(geo, mat); slabs[2].add(pts);
  const cA = new THREE.Color('#9fd0ff'), cB = new THREE.Color('#0b57d0'), tmp = new THREE.Color();
  function step(dt) {
    for (let i = 0; i < N; i++) {
      const p = st[i], k = dir[p.r * F + p.c];
      if (dt) { p.t += dt * (0.22 + 0.5 * Math.min(1, acc[p.r * F + p.c] / 180)); p.age += 1; }
      while (p.t >= 1 && k !== 255) { p.t -= 1; p.r += DR[dir[p.r * F + p.c]]; p.c += DC[dir[p.r * F + p.c]]; if (p.r < 0 || p.c < 0 || p.r >= F || p.c >= F || dir[p.r * F + p.c] === 255) { spawn(p); break; } }
      if (k === 255 || p.age > 900) spawn(p);
      const k2 = dir[p.r * F + p.c], r2 = p.r + (k2 === 255 ? 0 : DR[k2]) * p.t, c2 = p.c + (k2 === 255 ? 0 : DC[k2]) * p.t;
      const fx = (c2 + 0.5) / F, fy = (r2 + 0.5) / F; pos[i * 3] = toX(fx); pos[i * 3 + 1] = hAt(fx, fy) + 0.18; pos[i * 3 + 2] = toZ(fy);
      tmp.copy(cA).lerp(cB, Math.min(1, acc[p.r * F + p.c] / 200)); col[i * 3] = tmp.r; col[i * 3 + 1] = tmp.g; col[i * 3 + 2] = tmp.b;
    }
    geo.attributes.position.needsUpdate = true; geo.attributes.color.needsUpdate = true;
  }
  step(0); particles = { step, pts };
}
function buildRain() {
  const N = narrow ? 700 : 1500, P = new Float32Array(N * 6), top = GAP + HMAX + 16, seeds = [];
  let s = 5; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < N; i++) { const fx = rnd(), fy = rnd(); seeds.push({ x: toX(fx), z: toZ(fy), g: GAP + hAt(fx, fy), o: rnd() }); }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(P, 3));
  const ln = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: 0x5b8fd6, transparent: true, opacity: 0.45 })); scene.add(ln);
  rain = { step(t) { seeds.forEach((d, i) => { const ph = (d.o + t * 0.00012) % 1, y = top - ph * (top - d.g); P.set([d.x, y, d.z, d.x - 0.2, Math.min(y + 1.4, top), d.z], i * 6); }); geo.attributes.position.needsUpdate = true; }, ln, top };
  rain.step(0);
}

// ------------------------------------------------------------------------------------------------ callouts
const NS = 'http://www.w3.org/2000/svg';
let order = { l: [], r: [] };
function buildCallouts() {
  const box = $('ccallouts'), svg = $('cleaders');
  CALL.forEach((c, i) => {
    const b = document.createElement('button'); b.type = 'button'; b.className = 'co ' + c.side + (c.lim ? ' lim' : ''); b.dataset.id = c.id;
    b.innerHTML = `<span class="n">${i + 1}</span><span class="k">${esc(c.k)}</span><b>${esc(c.t)}</b><span class="s">${esc(c.s)}</span>`;
    b.onclick = () => show(c); box.appendChild(b); c.el = b;
    const g = document.createElementNS(NS, 'g'); c.halo = document.createElementNS(NS, 'line'); c.halo.setAttribute('class', 'halo');
    c.ln = document.createElementNS(NS, 'line'); if (c.lim) c.ln.setAttribute('class', 'lim'); c.dot = document.createElementNS(NS, 'circle'); c.dot.setAttribute('r', 4);
    g.append(c.halo, c.ln, c.dot); svg.appendChild(g);
    const bd = document.createElement('div'); bd.className = 'badge'; bd.textContent = i + 1; bd.onclick = () => show(c); $('cstage').appendChild(bd); c.badge = bd;
  });
}
function show(c) { mark(c.id); if (window.MFW) window.MFW.openPanel(c.k, c.t, c.p, c.nodes); }
function mark(id) { CALL.forEach((c) => { const on = c.id === id; c.el.classList.toggle('on', on); c.el.classList.toggle('dim', !!id && !on); c.ln.classList.toggle('on', on); c.dot.classList.toggle('on', on); }); }
document.addEventListener('mfw-panel-close', () => mark(null));
function screen(c) {
  const a = anchors[c.at]; if (!a) return null; const v = a.clone().project(camera), R = renderer.domElement.getBoundingClientRect();
  return { x: (v.x + 1) / 2 * R.width, y: (1 - v.y) / 2 * R.height };
}
function resort() { ['l', 'r'].forEach((sd) => { order[sd] = CALL.filter((c) => c.side === sd).map((c) => ({ c, y: (screen(c) || { y: 0 }).y })).sort((a, b) => a.y - b.y).map((o) => o.c); }); }
function layout() {
  const R = renderer.domElement.getBoundingClientRect(), W = R.width, Hh = R.height;
  if (narrow) { CALL.forEach((c) => { const p = screen(c); if (p) { c.badge.style.left = p.x + 'px'; c.badge.style.top = p.y + 'px'; } }); return; }
  ['l', 'r'].forEach((sd) => {
    const list = order[sd], n = list.length, top = 22, gap = (Hh - top - 30) / n;
    list.forEach((c, i) => {
      const el = c.el, w = el.offsetWidth, h = el.offsetHeight, x = sd === 'l' ? 20 : W - 20 - w, y = top + i * gap + (gap - h) / 2;
      el.style.left = x + 'px'; el.style.top = y + 'px'; const p = screen(c); if (!p) return;
      const lx = sd === 'l' ? x + w + 6 : x - 6, ly = y + h / 2;
      [c.ln, c.halo].forEach((l) => { l.setAttribute('x1', lx); l.setAttribute('y1', ly); l.setAttribute('x2', p.x); l.setAttribute('y2', p.y); });
      c.dot.setAttribute('cx', p.x); c.dot.setAttribute('cy', p.y);
    });
  });
}

function setAnchors(R, B) {
  const P = M.places, at = (f, dy, lift = 0.3) => new THREE.Vector3(toX(f[0]), hAt(f[0], f[1]) + dy + lift, toZ(f[1]));
  let pk = [0.5, 0.5], best = -1; for (let i = 0; i < H.length; i++) if (H[i] > best) { best = H[i]; pk = [(i % (G + 1)) / G, Math.floor(i / (G + 1)) / G]; }
  const closed = R.status.filter((r) => r.s === 'closed').sort((a, b) => b.pts.length - a.pts.length)[0] || R.status[0];
  const cm = closed ? closed.pts[Math.floor(closed.pts.length / 2)] : [0.7, 0.6];
  let big = null; if (B) B.buildings.forEach((b) => { if (!big || b.p.length > big.p.length) big = b; });
  const bc = big ? [big.p.reduce((s, p) => s + p[0], 0) / big.p.length, big.p.reduce((s, p) => s + p[1], 0) / big.p.length] : P.wpi;
  Object.assign(anchors, {
    sky: new THREE.Vector3(-S * 0.25, rain.top, -S * 0.15), water: at(P.pond, GAP), flow: at(P.park_ave, GAP), road: at(cm, GAP),
    wpi: at(P.wpi, 0, 1.2), pond: at(P.institute_park, 0), peak: at(pk, 0), bld: at(bc, 0, 1.5),
    soilTop: at([0.3, 0.4], -GAP), soilWall: new THREE.Vector3(toX(0.35), -GAP + hAt(0.35, 1) - 1.6, toZ(1)), gw: new THREE.Vector3(toX(0.7), -GAP + hAt(0.7, 1) - 3.2, toZ(1))
  });
}

const HOME = { pos: new THREE.Vector3(150, 70, 190), target: new THREE.Vector3(0, -1, 4) }, HOME_N = { pos: new THREE.Vector3(120, 95, 165), target: new THREE.Vector3(0, -2, 0) };
function home() { const h = narrow ? HOME_N : HOME; camera.position.copy(h.pos); controls.target.copy(h.target); controls.update(); resort(); }
function resize() {
  const st = $('cstage'), w = st.clientWidth, h = st.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h;
  narrow = w < 860; const co = $('ccallouts');
  if (narrow && co.parentNode === st) st.after(co); else if (!narrow && co.parentNode !== st) st.insertBefore(co, $('cloading'));
  camera.fov = narrow ? 46 : 32; camera.updateProjectionMatrix(); if (narrow !== wasNarrow) { wasNarrow = narrow; home(); } resort(); layout();
}

async function init() {
  const st = $('cstage'); narrow = st.clientWidth < 860;
  const [meta, hb, R, B, fd, fa] = await Promise.all([fetch(DIR + 'meta.json').then((r) => r.json()), fetch(DIR + 'height.bin').then((r) => r.arrayBuffer()),
    fetch(DIR + 'roads.json').then((r) => r.json()), fetch(DIR + 'buildings.json').then((r) => r.json()).catch(() => null),
    fetch(DIR + 'flowdir.bin').then((r) => r.arrayBuffer()), fetch(DIR + 'flowacc.bin').then((r) => r.arrayBuffer())]);
  M = meta; G = M.grid; const u = new Uint16Array(hb), mpu = M.width_m / S; H = new Float32Array(u.length);
  for (let i = 0; i < u.length; i++) { H[i] = (u[i] / 65535 * (M.zmax - M.zmin)) * VE / mpu; if (H[i] > HMAX) HMAX = H[i]; }
  renderer = new THREE.WebGLRenderer({ canvas: $('cgl'), antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.outputColorSpace = THREE.SRGBColorSpace;
  scene = new THREE.Scene(); camera = new THREE.PerspectiveCamera(32, 1, 1, 2000);
  scene.add(new THREE.HemisphereLight(0xffffff, 0xb9b2a6, 1.7)); const sun = new THREE.DirectionalLight(0xffffff, 1.4); sun.position.set(-70, 120, 50); scene.add(sun);
  const [tRun, tAir, tMod] = await Promise.all([loadTex('runoff.jpg'), loadTex('aerial.jpg'), modelTexture(R)]);
  soilMat.uniforms.meanTop.value = H.reduce((a, b) => a + b, 0) / H.length;
  slab(tRun, SOIL, soilMat, -GAP);
  const mid = slab(tAir, THICK, sideMat(0xd9d5cc), 0); const bm = B && buildings(B); if (bm) mid.add(bm);
  slab(tMod, THICK, sideMat(0xe8eef6), GAP);
  const acc8 = new Uint8Array(fa), acc = new Float32Array(acc8.length); for (let i = 0; i < acc8.length; i++) acc[i] = Math.pow(2, acc8[i] / 16);
  buildRain(); buildParticles(new Uint8Array(fd), acc); setAnchors(R, B);
  controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping = true; controls.dampingFactor = 0.08; controls.enablePan = false;
  controls.minDistance = 60; controls.maxDistance = 380; controls.maxPolarAngle = Math.PI * 0.49; controls.addEventListener('end', resort);
  buildCallouts(); addEventListener('resize', resize); resize(); home();
  const sum = R.status.reduce((o, r) => { o[r.s] = (o[r.s] || 0) + 1; return o; }, {});
  $('clegend').innerHTML = `<span><i class="sw" style="background:${ROAD_C.closed}"></i>Closed in the model run</span><span><i class="sw" style="background:${ROAD_C.risk}"></i>At risk</span>` +
    `<span><i class="sw" style="background:#4a8cd6"></i>Water 5 cm or more (peak)</span><span><i class="sw" style="background:#0b57d0;border-radius:50%"></i>Water running downhill</span>` +
    `<span class="t">Storm of 19 Aug 2021 · heights exaggerated ${VE}×</span>`;
  $('bFlow').onclick = () => { playing = !playing; $('bFlow').querySelector('span').textContent = playing ? 'Pause water' : 'Play water'; };
  if (!playing) $('bFlow').querySelector('span').textContent = 'Play water';
  $('bCHome').onclick = home;
  $('cloading').classList.add('gone');
  let last = 0, lt = 0;
  renderer.setAnimationLoop((t) => {
    if (playing) { particles.step(Math.min(0.12, (t - lt) / 1000 * 2.2)); rain.step(t); }
    lt = t; controls.update(); renderer.render(scene, camera);
    if (t - last > 30) { layout(); last = t; }
  });
}
init().catch((e) => { $('cloading').textContent = 'Could not load the campus view: ' + e.message; console.error(e); });
