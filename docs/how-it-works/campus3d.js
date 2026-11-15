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

// The labels around the block follow the old model-tree style: grouped input cards on the left, the engine and its result on the
// right, the checks underneath. Each card points to where it is in the picture (at), and opens the full detail (nodes, tree.json).
const IC = {
  rain: '<path d="M7 15a4 4 0 1 1 .9-7.9A5 5 0 0 1 17.6 9 3.5 3.5 0 0 1 17 16H7z"/><path d="M9 19l-1 2M13 19l-1 2M17 19l-1 2"/>',
  fc: '<path d="M7 15a4 4 0 1 1 .9-7.9A5 5 0 0 1 17.6 9 3.5 3.5 0 0 1 17 16H7z"/><path d="M12 18v3M10.5 19.5h3"/>',
  terrain: '<path d="M3 19l6-9 4 5 3-4 5 8H3z"/>', soil: '<path d="M3 8h18M3 13h18M3 18h18"/><circle cx="7" cy="10.5" r=".6"/><circle cx="15" cy="15.5" r=".6"/>',
  land: '<rect x="4" y="4" width="7" height="7"/><rect x="13" y="4" width="7" height="7"/><rect x="4" y="13" width="7" height="7"/><path d="M13 13h7v7h-7z"/>',
  drop: '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>', stream: '<path d="M4 6c4 0 4 4 8 4s4-4 8-4M4 13c4 0 4 4 8 4s4-4 8-4"/>',
  culvert: '<path d="M3 12h18"/><circle cx="12" cy="15" r="3"/><path d="M3 9h18"/>', road: '<path d="M8 3 5 21M16 3l3 18M12 5v3M12 11v3M12 17v3"/>',
  people: '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M16 6h4M18 4v4"/>', detour: '<path d="M4 18h6V8h8"/><path d="M15 5l3 3-3 3"/>',
  gw: '<path d="M3 15c3 0 3-2 6-2s3 2 6 2 3-2 6-2M3 19c3 0 3-2 6-2s3 2 6 2 3-2 6-2"/>', gauge: '<path d="M4 20V5M4 5l7 4-7 4"/>', report: '<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v4M12 17v.1"/>',
  list: '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h4"/>'
};
// The story around the cross-section, read in order: what falls on it (top), what the ground does with it (left, pointing at the
// cut face), what the model does and what comes out (right), and how it is checked (under the figure). Plain words first; the
// source line says who made each piece and whether it is public. Pointers only go to things you can see for sure: the rain,
// the ground surface and the layers on the cut face.
const PUB = '<i class="chip-p">public data</i>', OSS = '<i class="chip-o">open source</i>', NOT = '<i class="chip-n">not in the model yet</i>';
const STORY = [
  { zone: 'top', n: 1, id: 'obs', ic: 'rain', t: 'Rain that fell', p: 'Weather radar measures how much rain falls on every square kilometre, every hour, checked against rain gauges on the ground.',
    src: 'NOAA MRMS radar', chip: PUB, at: 'skyL', nodes: ['mrms', 'rain_grid'] },
  { zone: 'top', n: 1, id: 'fc', ic: 'fc', t: 'Rain on the way', p: 'A weather model guesses the rain for the next two days. The model runs on its eight newest guesses to see how much they agree.',
    src: 'NOAA HRRR forecast', chip: PUB, at: 'skyR', nodes: ['hrrr', 'phase', 'members'] },
  { zone: 'left', n: 2, id: 'dem', ic: 'terrain', t: 'The shape of the ground', p: 'Lasers flown from planes measure the height of the ground to within centimetres. Water always runs from high to low.',
    src: 'USGS 3DEP lidar, 1 m', chip: PUB, at: 'surf', nodes: ['lidar', 'dem20', 'breach', 'crest'] },
  { zone: 'left', n: 2, id: 'cover', ic: 'land', t: 'Roofs, roads and grass', p: 'Roofs and pavement send rain straight off; grass and trees hold some back and slow the rest down.',
    src: 'NLCD 2021 land cover', chip: PUB, at: 'surf2', nodes: ['nlcd', 'manning'] },
  { zone: 'left', n: 2, id: 'soil', ic: 'soil', t: 'The soil', p: 'Sandy soil drinks rain fast, clay soil slowly. What the soil cannot drink runs off over the ground.',
    src: 'USDA SSURGO soils, NRCS curve number', chip: PUB, at: 'soilBand', nodes: ['ssurgo', 'cn', 'wi_amc', 'wi_frozen'] },
  { zone: 'left', n: 0, id: 'gw', ic: 'gw', t: 'Water already underground', p: 'Groundwater rising under roads and buildings is the next part of the chain this research will add.',
    src: 'Groundwater', chip: NOT, at: 'gwLine', lim: true, nodes: ['cc_gw'] },
  { zone: 'right', n: 3, id: 'engine', engine: true, t: 'LISFLOOD-FP 8.2', k: 'The flood model',
    p: 'A free, open-source flood model from the University of Bristol, UK. It splits the ground into 20 m squares and, second by second, moves the water from each square to its lower neighbours, the way water really runs downhill. The moving blue dots show that.',
    src: 'University of Bristol', chip: OSS, nodes: ['lisflood', 'depth', 'velocity'] },
  { zone: 'right', n: 3, id: 'drain', ic: 'stream', t: 'Where the water can go', p: 'Streams and ponds carry water away. Where a stream passes under a road, a pipe (a culvert) lets it through until the pipe is full.',
    src: 'USGS streams, NAACC culvert surveys', chip: PUB, nodes: ['nhd', 'channels', 'crossings', 'culvert'] },
  { zone: 'right', n: 4, id: 'roads', result: true, t: 'Water on every road', p: 'Every 10 m along every road, the model reads how deep the water gets and for how long.',
    src: 'MassDOT road inventory', chip: PUB, nodes: ['roadpts', 'segdepth', 'onset', 'pclose'] },
  { zone: 'right', n: 5, id: 'access', ic: 'people', t: 'Who gets cut off', p: 'With the flooded roads closed, the model finds who can no longer reach a hospital, fire station or police station in time.',
    src: 'US Census 2020, OpenStreetMap', chip: PUB, nodes: ['census', 'facilities', 'dijkstra', 'access'] }
];
const CHECKS = [
  { ic: 'gauge', t: 'River gauges', s: 'USGS, every 15 minutes: did the river rise as much as the model said, and when?', nodes: ['gauges'] },
  { ic: 'report', t: 'Storm reports', s: 'National Weather Service and NOAA storm reports, news and agency reports of flooded roads.', nodes: ['labels', 'matching'] },
  { ic: 'list', t: 'City damage records', s: 'Public works lists of the roads and culverts a storm damaged.', nodes: ['labels'] },
  { ic: 'list', t: 'Storms kept aside', s: 'Most past storms were never used to set the model; they are kept to test it fairly.', nodes: ['split', 'metrics', 'baselines'] }
];
const CALL = [];   // flat list of everything that points into the picture (filled in buildCallouts)

let EX = 0, EXT = 0, camAnim = null, lastK = 0, HMAX = 0, M, H, G, renderer, scene, camera, controls, slabs = [], particles = null, rain = null, playing = !reduced, wasNarrow = null, narrow = false;
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
  side: THREE.DoubleSide,
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
const sideMat = (col) => new THREE.MeshStandardMaterial({ color: col, roughness: 1, side: THREE.DoubleSide });

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

async function aerialTexture(R) {   // the aerial photo with street and place names written on it, like a planning map
  const img = await new Promise((ok) => { const i = new Image(); i.onload = () => ok(i); i.src = DIR + 'aerial.jpg'; });
  const N = 4096, cv = document.createElement('canvas'); cv.width = cv.height = N; const x = cv.getContext('2d'); x.drawImage(img, 0, 0, N, N);
  const want = ['Park Avenue', 'Institute Road', 'West Street', 'Salisbury Street', 'Boynton Street', 'Highland Street', 'Dean Street', 'Humboldt Avenue', 'Elbridge Street', 'Lancaster Street', 'Grove Street', 'Wachusett Street', 'Drury Lane', 'Schussler Road', 'Trowbridge Road', 'Einhorn Road', 'Massachusetts Avenue'];
  const short = (n) => n.replace(' Avenue', ' Ave').replace(' Street', ' St').replace(' Road', ' Rd').replace(' Lane', ' Ln');
  x.textAlign = 'center'; x.textBaseline = 'middle'; x.lineJoin = 'round';
  want.forEach((nm) => {
    const segs = R.all.filter((r) => r.n === nm); if (!segs.length) return;
    let best = null, bl = 0; segs.forEach((r) => { let l = 0; for (let i = 1; i < r.pts.length; i++) l += Math.hypot(r.pts[i][0] - r.pts[i - 1][0], r.pts[i][1] - r.pts[i - 1][1]); if (l > bl) { bl = l; best = r; } });
    if (!best || bl < 0.06) return;
    const k = Math.floor(best.pts.length / 2), a = best.pts[Math.max(0, k - 1)], b = best.pts[Math.min(best.pts.length - 1, k + 1)];
    const cx = (a[0] + b[0]) / 2 * N, cy = (a[1] + b[1]) / 2 * N; if (cx < 160 || cy < 160 || cx > N - 160 || cy > N - 160) return;
    let ang = Math.atan2((b[1] - a[1]), (b[0] - a[0])); if (ang > Math.PI / 2) ang -= Math.PI; if (ang < -Math.PI / 2) ang += Math.PI;
    x.save(); x.translate(cx, cy); x.rotate(ang); x.font = '600 44px Roboto, Arial, sans-serif';
    x.strokeStyle = 'rgba(32,33,36,.85)'; x.lineWidth = 9; x.strokeText(short(nm).toUpperCase(), 0, 0); x.fillStyle = '#fff'; x.fillText(short(nm).toUpperCase(), 0, 0); x.restore();
  });
  x.lineCap = 'round'; x.lineJoin = 'round';   // roads as the model rated them in the storm (same colours as the result card)
  ['wet', 'risk', 'closed'].forEach((st) => { x.strokeStyle = st === 'wet' ? '#fbbc04' : ROAD_C[st]; x.globalAlpha = 0.9; x.lineWidth = st === 'closed' ? 16 : 12;
    R.status.filter((r) => r.s === st).forEach((r) => { x.beginPath(); r.pts.forEach((p, i) => (i ? x.lineTo(p[0] * N, p[1] * N) : x.moveTo(p[0] * N, p[1] * N))); x.stroke(); }); });
  x.globalAlpha = 1;
  const place = (f, t, size) => { if (!f) return; x.font = `700 ${size}px Roboto, Arial, sans-serif`; x.strokeStyle = 'rgba(32,33,36,.9)'; x.lineWidth = size / 4.5; x.strokeText(t, f[0] * N, f[1] * N); x.fillStyle = '#fff'; x.fillText(t, f[0] * N, f[1] * N); };
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = renderer.capabilities.getMaxAnisotropy(); return t;
}

function buildings(B, roofTex) {   // walls extruded to the real height; roofs are flat caps that show the aerial photo seen from above
  const walls = [], roofs = [], mpu = M.width_m / S;
  B.buildings.forEach((b) => {
    if (b.p.length < 4) return;
    const sh = new THREE.Shape(b.p.map((p) => new THREE.Vector2(toX(p[0]), -toZ(p[1]))));
    let base = Infinity; b.p.forEach((p) => { base = Math.min(base, hAt(p[0], p[1])); });
    const hgt = Math.max(0.2, b.h / mpu * 1.15);
    const w = new THREE.ExtrudeGeometry(sh, { depth: hgt + 0.3, bevelEnabled: false }); w.rotateX(-Math.PI / 2); w.translate(0, base - 0.3, 0); walls.push(w.index ? w.toNonIndexed() : w);
    const r = new THREE.ShapeGeometry(sh); r.rotateX(-Math.PI / 2); r.translate(0, base + hgt + 0.01, 0); roofs.push(r.index ? r.toNonIndexed() : r);
  });
  if (!walls.length) return null;
  const strip = (g) => { ['uv', 'normal'].forEach((k) => g.deleteAttribute(k)); return g; };
  const W = mergeGeometries(walls.map(strip), false); W.computeVertexNormals();
  const Rg = mergeGeometries(roofs.map(strip), false), pos = Rg.attributes.position, uv = new Float32Array(pos.count * 2);
  for (let i = 0; i < pos.count; i++) { uv[i * 2] = pos.getX(i) / S + 0.5; uv[i * 2 + 1] = 0.5 - pos.getZ(i) / S; }
  Rg.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); Rg.computeVertexNormals();
  const grp = new THREE.Group();
  grp.add(new THREE.Mesh(W, new THREE.MeshStandardMaterial({ color: 0xd9d4c9, roughness: 0.95 })));
  grp.add(new THREE.Mesh(Rg, new THREE.MeshStandardMaterial({ map: roofTex, roughness: 0.9, side: THREE.DoubleSide })));
  return grp;
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
  const mat = new THREE.PointsMaterial({ size: narrow ? 0.7 : 0.62, vertexColors: true, transparent: true, opacity: 0.95, depthWrite: false });
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
  const N = narrow ? 500 : 900, P = new Float32Array(N * 6), seeds = [];
  let s = 5; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < N; i++) { const fx = rnd(), fy = rnd(); seeds.push({ x: toX(fx), z: toZ(fy), g: hAt(fx, fy), o: rnd() }); }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(P, 3));
  const ln = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: 0x5b8fd6, transparent: true, opacity: 0.45 })); scene.add(ln);
  rain = { step(t) { const top = GAP * EX + HMAX + 16; seeds.forEach((d, i) => { const g = d.g + GAP * EX, ph = (d.o + t * 0.00012) % 1, y = top - ph * (top - g); P.set([d.x, y, d.z, d.x - 0.2, Math.min(y + 1.4, top), d.z], i * 6); }); geo.attributes.position.needsUpdate = true; }, ln };
  rain.step(0);
}
function applyEx() {   // 0 = the campus as one block (aerial on lidar); 1 = the three layers pulled apart
  slabs[0].position.y = -GAP * EX; slabs[2].position.y = GAP * EX; slabs[0].visible = EX > 0.02;
  slabs[2].children.forEach((ch) => { if (ch.userData.slabPart) ch.visible = EX > 0.02; });
}

// ------------------------------------------------------------------------------------------------ the story cards
const NS = 'http://www.w3.org/2000/svg';
const svgI = (k) => `<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">${IC[k] || ''}</svg>`;
function card(c) {
  const b = document.createElement('button'); b.type = 'button'; b.dataset.id = c.id;
  if (c.engine) {
    b.className = 'scard engine';
    b.innerHTML = `<span class="step">${c.n}</span><span class="k">${esc(c.k)}</span><b>${esc(c.t)}</b><span class="p">${esc(c.p)}</span><span class="src">${esc(c.src)} ${c.chip}</span>`;
  } else if (c.result) {
    b.className = 'scard result';
    b.innerHTML = `<span class="step">${c.n}</span><b>${esc(c.t)}</b><span class="p">${esc(c.p)}</span>` +
      `<span class="lg"><i style="background:${ROAD_C.closed}"></i><b>Closed</b> 30 cm or more, about where a car stalls</span><span class="lg"><i style="background:${ROAD_C.risk}"></i><b>At risk</b> 15 to 30 cm</span><span class="lg"><i style="background:#fbbc04"></i><b>Wet</b> 5 to 15 cm</span>` +
      `<span class="src">${esc(c.src)} ${c.chip}</span>`;
  } else {
    b.className = 'scard' + (c.lim ? ' lim' : '');
    b.innerHTML = `${c.n ? `<span class="step">${c.n}</span>` : ''}<span class="hd">${svgI(c.ic)}<b>${esc(c.t)}</b></span><span class="p">${esc(c.p)}</span><span class="src">${esc(c.src)} ${c.chip}</span>`;
  }
  b.onclick = (e) => { e.stopPropagation(); show(c); }; c.el = b;
  if (c.at) {
    const g = document.createElementNS(NS, 'g'); c.halo = document.createElementNS(NS, 'path'); c.halo.setAttribute('class', 'halo');
    c.ln = document.createElementNS(NS, 'path'); c.ln.setAttribute('class', 'arrow' + (c.lim ? ' lim' : '')); c.ln.setAttribute('marker-end', 'url(#cArrow)');
    g.append(c.halo, c.ln); $('cleaders').appendChild(g); c.g = g;
    const bd = document.createElement('div'); bd.className = 'badge'; bd.textContent = c.n || '·'; bd.onclick = () => show(c); $('cstage').appendChild(bd); c.badge = bd;
  }
  CALL.push(c); return b;
}
function buildCallouts() {
  $('cleaders').innerHTML = '<defs><marker id="cArrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1L9 5L1 9z" fill="currentColor"/></marker></defs>';
  const box = $('ccallouts');
  const top = document.createElement('div'); top.className = 'szone top';
  top.innerHTML = '<p class="zt"><b>1</b> What falls on it</p>';
  const L = document.createElement('div'); L.className = 'szone left'; L.innerHTML = '<p class="zt"><b>2</b> What the ground does with it</p>';
  const Rr = document.createElement('div'); Rr.className = 'szone right'; Rr.innerHTML = '<p class="zt"><b>3</b> What the model does, and what comes out</p>';
  STORY.forEach((c) => ({ top, left: L, right: Rr }[c.zone]).appendChild(card(c)));
  box.append(top, L, Rr);
  const chk = $('cchecks'); if (chk) chk.innerHTML = '<div class="th"><span><b class="stepi">6</b> Checked against what really happened</span><em>never fed into the model, only used to check it afterwards</em></div><div class="tchecks">' +
    CHECKS.map((c, i) => `<button type="button" class="tcard" data-i="${i}">${svgI(c.ic)}<span class="tx"><b>${esc(c.t)}</b><span class="s">${esc(c.s)}</span></span></button>`).join('') + '</div>';
  if (chk) chk.querySelectorAll('button').forEach((b) => { const c = CHECKS[+b.dataset.i]; b.onclick = () => window.MFW && window.MFW.openPanel('Checked against reality', c.t, c.s, c.nodes); });
}
function show(c) { mark(c.id); if (window.MFW) window.MFW.openPanel(c.engine ? c.k : (c.zone === 'top' ? 'What falls on it' : c.zone === 'left' ? 'What the ground does' : 'What the model does'), c.t, c.p, c.nodes); }
function mark(id) { CALL.forEach((c) => { const on = c.id === id; c.el.classList.toggle('on', on); c.el.classList.toggle('dim', !!id && !on); if (c.ln) c.ln.classList.toggle('on', on); }); }
document.addEventListener('mfw-panel-close', () => mark(null));
function screen(c) {
  const a = anchors[c.at]; if (!a) return null; const v = a.p.clone(); v.y += a.L * GAP * EX; v.project(camera); const R = renderer.domElement.getBoundingClientRect();
  return { x: (v.x + 1) / 2 * R.width, y: (1 - v.y) / 2 * R.height };
}
function resort() {}
function layout() {
  const R = renderer.domElement.getBoundingClientRect();
  if (narrow) { CALL.forEach((c) => { if (!c.badge) return; const p = screen(c); c.badge.style.display = p && EX < 0.5 ? '' : 'none'; if (p) { c.badge.style.left = p.x + 'px'; c.badge.style.top = p.y + 'px'; } }); return; }
  CALL.forEach((c) => {
    if (!c.ln) return; const p = screen(c); const show_ = p && EX < 0.5; c.g.style.display = show_ ? '' : 'none'; if (!show_) return;
    const r = c.el.getBoundingClientRect(); let x0, y0, d;
    if (c.zone === 'top') { x0 = r.left - R.left + r.width / 2; y0 = r.bottom - R.top + 2; d = `M${x0},${y0} C${x0},${(y0 + p.y) / 2} ${p.x},${(y0 + p.y) / 2} ${p.x},${p.y - 4}`; }
    else { x0 = r.right - R.left + 2; y0 = r.top - R.top + r.height / 2; d = `M${x0},${y0} C${(x0 + p.x) / 2},${y0} ${(x0 + p.x) / 2},${p.y} ${p.x - 4},${p.y}`; }
    c.ln.setAttribute('d', d); c.halo.setAttribute('d', d);
  });
}

function setAnchors() {
  // seen from the north: the front face (fy = 0) is the cut through the park; its left end on screen is the east end (fx -> 1)
  const A = (p, L = 0) => ({ p, L }), fy = 0, fx = 0.82, face = (d) => new THREE.Vector3(toX(fx), hAt(fx, fy) - d, toZ(fy) - 0.05);
  const meanTop = H.reduce((a, b) => a + b, 0) / H.length, top = hAt(fx, fy), wt = (top - 2.6) * 0.4 + (meanTop - 3.6) * 0.6;
  Object.assign(anchors, {
    skyL: A(new THREE.Vector3(toX(0.72), HMAX + 9, toZ(0.45)), 1), skyR: A(new THREE.Vector3(toX(0.3), HMAX + 9, toZ(0.45)), 1),
    surf: A(face(-0.1)), surf2: A(new THREE.Vector3(toX(0.7), hAt(0.7, 0.05) + 0.6, toZ(0.05))), soilBand: A(face(1.4)), gwLine: A(face(top - wt))
  });
}

const VIEWS = { campus: null, layers: { pos: new THREE.Vector3(175, 82, 225), target: new THREE.Vector3(0, -4, 4) } };
function fitK() {   // pull the camera back when the space for the block (between the label columns) is narrow, so the whole stack fits
  const st = $("cstage"), w = st.clientWidth - (narrow ? 0 : 640), h = st.clientHeight; return Math.max(1, (narrow ? 1.25 : 1.42) / Math.max(0.2, w / h));
}
function viewOf() {
  if (!VIEWS.campus) { const f = M.places.kaven, t = new THREE.Vector3(toX(f[0]), hAt(f[0], f[1]), toZ(f[1])); VIEWS.campus = { pos: new THREE.Vector3(0, 48, -124), target: new THREE.Vector3(0, -9, 6) }; }
  const h = EXT ? VIEWS.layers : VIEWS.campus, k = fitK() * (narrow ? 0.92 : 1); return { pos: h.pos.clone().sub(h.target).multiplyScalar(k).add(h.target), target: h.target.clone() }; }
function home(animate) {
  const v = viewOf();
  if (animate && !reduced) { camAnim = { p0: camera.position.clone(), t0: controls.target.clone(), p1: v.pos, t1: v.target, k: 0 }; return; }
  camera.position.copy(v.pos); controls.target.copy(v.target); controls.update(); resort();
}
function resize() {
  const st = $('cstage'), w = st.clientWidth, h = st.clientHeight; renderer.setSize(w, h, false); camera.aspect = w / h;
  narrow = w < 860; const co = $('ccallouts');
  if (narrow && co.parentNode === st) st.after(co); else if (!narrow && co.parentNode !== st) st.insertBefore(co, $('cloading'));
  camera.fov = narrow ? 46 : 32; camera.updateProjectionMatrix(); if (narrow !== wasNarrow || Math.abs(fitK() - lastK) > 0.05) { wasNarrow = narrow; lastK = fitK(); home(); } resort(); layout();
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
  const [tRun, tAir, tMod] = await Promise.all([loadTex('runoff.jpg'), aerialTexture(R), modelTexture(R)]);
  soilMat.uniforms.meanTop.value = H.reduce((a, b) => a + b, 0) / H.length;
  slab(tRun, THICK, sideMat(0xd9d5cc), 0);
  const mid = slab(tAir, SOIL, soilMat, 0); const bm = B && buildings(B, tAir); if (bm) mid.add(bm);
  slab(tMod, THICK, sideMat(0xe8eef6), 0);
  slabs[2].children.forEach((ch) => { ch.userData.slabPart = true; });
  const acc8 = new Uint8Array(fa), acc = new Float32Array(acc8.length); for (let i = 0; i < acc8.length; i++) acc[i] = Math.pow(2, acc8[i] / 16);
  buildRain(); buildParticles(new Uint8Array(fd), acc); setAnchors(); applyEx();
  controls = new OrbitControls(camera, renderer.domElement); controls.enableDamping = true; controls.dampingFactor = 0.08; controls.enablePan = false;
  controls.minDistance = 18; controls.maxDistance = 700; controls.maxPolarAngle = Math.PI * 0.49; controls.addEventListener('end', resort);
  buildCallouts(); addEventListener('resize', resize); resize(); home();
  const sum = R.status.reduce((o, r) => { o[r.s] = (o[r.s] || 0) + 1; return o; }, {});
  $('clegend').innerHTML = `<span><i class="sw" style="background:${ROAD_C.closed}"></i>Closed in the model run</span><span><i class="sw" style="background:${ROAD_C.risk}"></i>At risk</span>` +
    `<span><i class="sw" style="background:#4a8cd6"></i>Water 5 cm or more (peak)</span><span><i class="sw" style="background:#0b57d0;border-radius:50%"></i>Water running downhill</span>` +
    `<span class="t">Storm of 19 Aug 2021 · heights exaggerated ${VE}×</span>`;
  $('bFlow').onclick = () => { playing = !playing; $('bFlow').querySelector('span').textContent = playing ? 'Pause water' : 'Play water'; };
  if (!playing) $('bFlow').querySelector('span').textContent = 'Play water';
  $('bCHome').onclick = () => home(true);
  $('bLayers').onclick = () => { EXT = EXT ? 0 : 1; $('bLayers').querySelector('span').textContent = EXT ? 'Back to the campus' : 'Show the layers'; home(true); };
  $('cloading').classList.add('gone');
  let last = 0, lt = 0;
  renderer.setAnimationLoop((t) => {
    if (playing) { particles.step(Math.min(0.12, (t - lt) / 1000 * 2.2)); rain.step(t); }
    if (Math.abs(EX - EXT) > 1e-3) { EX += (EXT - EX) * (reduced ? 1 : 0.07); applyEx(); } else if (EX !== EXT) { EX = EXT; applyEx(); }
    if (camAnim) { camAnim.k = Math.min(1, camAnim.k + 0.035); const e = camAnim.k < 0.5 ? 2 * camAnim.k * camAnim.k : 1 - Math.pow(-2 * camAnim.k + 2, 2) / 2;
      camera.position.lerpVectors(camAnim.p0, camAnim.p1, e); controls.target.lerpVectors(camAnim.t0, camAnim.t1, e); if (camAnim.k >= 1) { camAnim = null; resort(); } }
    lt = t; controls.update(); renderer.render(scene, camera);
    if (t - last > 30) { layout(); last = t; }
  });
}
init().catch((e) => { $('cloading').textContent = 'Could not load the campus view: ' + e.message; console.error(e); });
