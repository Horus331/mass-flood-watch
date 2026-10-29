"""Dataset for the LISFLOOD-FP surrogate (docs/proto/surrogate/SURROGATE.md): run outputs -> per-cell input channels + peak depth target.

    python proto/surrogate/dataset.py build --root ~/scratch/surrogate --plans plan_b1.json[,plan_b2.json] --inputs-plan inputs_plan.json --out ~/scratch/surrogate/dataset
    python proto/surrogate/dataset.py selftest

Sources (all written by sim/colab/w9_lisflood.py with LF_SURR_SAVE=1, the frozen baseline physics):
  <root>/run_<id>/out/            surr_inputs.npz + hmax.npy + meta.json of a training-generator scenario (proto/turing/surrogate_gen.slurm)
  <root>/inputs/<name>/           surr_inputs.npz of an inputs-only run (proto/turing/surrogate_inputs.slurm) for a catalogue storm or District 3;
                                  the target is the published LISFLOOD-FP run in the repo (docs/proto/parity/catalog/<name>/hmax_cm.npz,
                                  docs/proto/turing/d3_sep2023_p/hmax_cm.npz), never a new run.
Channels (float16 .npy, one array per box for the static ones, one per scene for the rain ones; 20 m like the run):
  static  STATIC: terrain relative to 1 km / 200 m means, slope, log10 D8 upstream area, HAND, impervious share, curve number, water /
          channel / carved / sea masks, road-crest relief (10 m max - lidar), hydraulic edits (model DEM - lidar)
  rain    RAIN: storm total, max 1 / 3 / 6 h, CN + 2 mm/h effective excess (the exact w9 loss: cumulative SCS-CN on the hourly rain, then
          LF_INFIL_MMH out of each hour), its peak hour, D8-accumulated excess volume and peak-hour volume upstream, wet-hour share, hours
          left after the excess centroid, window length
  target  y.npy = LISFLOOD-FP hmax (m), float16
Splits: from the plan (scenarios.py: train / val / test_box / test_rain), 'catalog' (held-out 23 + dev, role kept) and 'district'.
Normalisation: mean / std of every channel over land cells of the train scenes (norm.json).  Plausibility: the ratio of the peak-depth volume
on land to the effective-excess volume of the box; its 99th percentile over train scenes is kept for the prediction-time check.
"""
import os, sys, json, glob, time, math, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
STATIC = ['zrel_1km', 'zrel_200m', 'slope', 'log_uparea', 'hand', 'imp', 'cn', 'water', 'chan', 'carved', 'crest', 'edit', 'sea']
RAIN = ['p_tot', 'p_max1', 'p_max3', 'p_max6', 'e_tot', 'e_max1', 'up_e', 'up_epk', 'wet_frac', 't_left', 'hours']
CHANNELS = STATIC + RAIN
MASKS = ('water', 'chan', 'carved', 'sea')           # 0 / 1 channels: not normalised
DRAIN_KM2 = 1.0                                     # HAND drainage: channels30 cells or D8 upstream area >= 1 km2
ROW_CHUNK = 512
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)


# ------------------------------------------------------------------ inputs
def load_inputs(path):
    with np.load(path, allow_pickle=False) as q:
        P = {k: q[k] for k in q.files}
    P['meta'] = json.loads(str(P['meta'])); m = P.pop('mask').astype(np.uint8)
    P.update(water=(m & 1) > 0, chan=(m & 2) > 0, carved=(m & 4) > 0, sea=(m & 8) > 0); P['rain_coarsen'] = int(P['rain_coarsen'])
    return P


def watermask(P):
    """w9's watermask.npy: water (incl. sea) | channel | carved."""
    return P['water'] | P['chan'] | P['carved']


def land(P): return ~(watermask(P) | P['sea'])


def rain_rows(P, r0, r1):
    """Hourly rain (T, r1 - r0, nx) float32 mm on the 20 m grid: the coarse blocks repeated (nearest)."""
    k = P['rain_coarsen']; nx = P['z'].shape[1]; R = P['rain']
    a0, a1 = r0 // k, (r1 - 1) // k + 1
    blk = np.repeat(np.repeat(R[:, a0:a1].astype(np.float32), k, axis=1), k, axis=2)
    return blk[:, r0 - a0 * k:r1 - a0 * k, :nx]


# ------------------------------------------------------------------ D8 routing (sim/ml/dataset.py) and level order
def _sim_ml():
    """sim/ml/dataset.py (D8 helpers) loaded under another name: it is also called dataset.py."""
    import importlib.util
    if 'sim_ml_dataset' not in sys.modules:
        spec = importlib.util.spec_from_file_location('sim_ml_dataset', os.path.join(ROOT, 'sim', 'ml', 'dataset.py'))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); sys.modules['sim_ml_dataset'] = m
    return sys.modules['sim_ml_dataset']


def routing(z, sea, res):
    M = _sim_ml(); d8_next, route = M.d8_next, M.route
    nxt, step = d8_next(np.where(sea, -1e6, z).astype(np.float32), sea)
    _, hops, _ = route(nxt, step, res)
    order = np.argsort(-hops, kind='stable'); h = hops[order]
    b = np.flatnonzero(np.diff(h)) + 1; starts = np.r_[0, b]; ends = np.r_[b, len(h)]
    return dict(nxt=nxt, order=order, starts=starts, ends=ends, lev=h[starts])


def accumulate(R, w):
    """Sum of w over every cell draining through each cell (itself included), level by level from the sources down."""
    acc = np.asarray(w, np.float64).ravel().copy(); nxt, order = R['nxt'], R['order']
    for s, e, h in zip(R['starts'], R['ends'], R['lev']):
        if h == 0: break
        idx = order[s:e]; np.add.at(acc, nxt[idx], acc[idx])
    return acc


def hand(R, z, drain):
    """Height above the drainage cell each cell flows to (D8), from the outlets up."""
    zf = z.ravel().astype(np.float64); dz = zf.copy(); dr = drain.ravel(); nxt, order = R['nxt'], R['order']
    for s, e, h in list(zip(R['starts'], R['ends'], R['lev']))[::-1]:
        if h == 0: continue
        idx = order[s:e]; dz[idx] = np.where(dr[idx], zf[idx], dz[nxt[idx]])
    return np.clip(zf - dz, 0, None).reshape(z.shape)


# ------------------------------------------------------------------ channels
def static_layers(P):
    """-> (S float32 (len(STATIC), ny, nx), routing)."""
    from scipy import ndimage
    z = P['z'].astype(np.float32); res = float(P['meta']['res_m']); sea = P['sea']
    zf = np.where(sea, np.nan, z); zfill = np.where(sea, np.nanmean(zf) if np.isfinite(zf).any() else 0.0, z)
    k1 = int(round(1000 / res)) | 1; k2 = int(round(200 / res)) | 1
    gy, gx = np.gradient(zfill, res)
    R = routing(z, sea, res); up = accumulate(R, np.ones(z.size)).reshape(z.shape) * res * res / 1e6
    H = hand(R, z, P['chan'] | (up >= DRAIN_KM2) | P['water'])
    L = dict(zrel_1km=np.clip(zfill - ndimage.uniform_filter(zfill, k1), -60, 60), zrel_200m=np.clip(zfill - ndimage.uniform_filter(zfill, k2), -20, 20),
             slope=np.clip(np.hypot(gx, gy), 0, 1), log_uparea=np.log10(up + 1e-3), hand=np.log1p(np.clip(H, 0, 50)), imp=P['imp'].astype(np.float32) / 100,
             cn=P['cn'].astype(np.float32) / 100, water=P['water'], chan=P['chan'], carved=P['carved'],
             crest=np.clip(P['z_raw_max10'] - P['z_raw'], 0, 5), edit=np.clip(z - P['z_raw'], -5, 2), sea=sea)
    S = np.stack([np.where(sea & (n not in MASKS), 0, L[n]).astype(np.float32) for n in STATIC])
    return S, R


def excess_rows(Pr, cn, infil_mmh):
    """w9's effective rain for rows: cumulative SCS-CN excess per hour (Ia = 0.2 S), then max(e - LF_INFIL_MMH, 0) (LF_INFIL_MODE=rain)."""
    if cn is None or not np.any(cn > 0): E = Pr
    else:
        S = 25400.0 / np.maximum(cn, 1.0) - 254.0; Ia = 0.2 * S; Pc = np.cumsum(Pr, axis=0)
        Q = np.where(Pc > Ia, (Pc - Ia) ** 2 / np.maximum(Pc - Ia + S, 1e-6), 0.0)
        E = np.diff(np.concatenate([np.zeros_like(Q[:1]), Q]), axis=0)
    return np.maximum(E - np.float32(infil_mmh), 0).astype(np.float32) if infil_mmh > 0 else E.astype(np.float32)


def run_infil(P):
    env = P['meta'].get('env', {}); mode = env.get('LF_INFIL_MODE') or ('rain' if env.get('LF_PARITY') == '1' else 'solver')
    return float(env.get('LF_INFIL_MMH', '4')) if mode == 'rain' else 0.0      # solver mode: the CPU solver drains ponded water instead (not modelled here)


def rain_layers(P, R, chunk=ROW_CHUNK):
    """-> float32 (len(RAIN), ny, nx) and box totals (excess volume m3)."""
    ny, nx = P['z'].shape; res = float(P['meta']['res_m']); T = P['rain'].shape[0]; cn = P['cn'].astype(np.float32); infil = run_infil(P)
    out = {n: np.zeros((ny, nx), np.float32) for n in RAIN}; tt = np.arange(T, dtype=np.float32)[:, None, None] + 0.5
    for r0 in range(0, ny, chunk):
        r1 = min(ny, r0 + chunk); Pr = rain_rows(P, r0, r1); cs = np.concatenate([np.zeros_like(Pr[:1]), np.cumsum(Pr, axis=0)])
        def mx(w): w = min(w, T); return (cs[w:] - cs[:-w]).max(axis=0)
        E = excess_rows(Pr, cn[r0:r1], infil); et = E.sum(0)
        out['p_tot'][r0:r1] = Pr.sum(0); out['p_max1'][r0:r1] = Pr.max(0); out['p_max3'][r0:r1] = mx(3); out['p_max6'][r0:r1] = mx(6)
        out['e_tot'][r0:r1] = et; out['e_max1'][r0:r1] = E.max(0); out['wet_frac'][r0:r1] = (Pr >= 1.0).mean(0)
        cen = np.where(et > 0, (E * tt).sum(0) / np.maximum(et, 1e-6), T / 2.0); out['t_left'][r0:r1] = (T - cen) / 24.0
    area = res * res
    up_e = accumulate(R, out['e_tot'].ravel() * area / 1000.0).reshape(ny, nx); up_pk = accumulate(R, out['e_max1'].ravel() * area / 1000.0).reshape(ny, nx)
    vol_e = float(out['e_tot'][~P['sea']].sum() * area / 1000.0)
    for n in ('p_tot', 'p_max1', 'p_max3', 'p_max6', 'e_tot', 'e_max1'): out[n] = np.log1p(out[n])
    out['up_e'] = np.log10(1 + up_e).astype(np.float32); out['up_epk'] = np.log10(1 + up_pk).astype(np.float32); out['hours'][:] = T / 48.0
    X = np.stack([np.where(P['sea'], 0, out[n]).astype(np.float32) for n in RAIN])
    return X, dict(excess_volume_m3=vol_e, rain_max_mm=float(np.expm1(out['p_tot'].max())), hours=int(T))


def features(P):
    """All channels for one inputs file: float32 (len(CHANNELS), ny, nx), plus box stats."""
    S, R = static_layers(P); X, st = rain_layers(P, R); return np.concatenate([S, X]), st


def volume_ratio(h, P, excess_m3):
    """Peak-depth volume on land / effective-excess volume of the box (plausibility; not a mass balance: peaks are not simultaneous)."""
    v = float(np.where(land(P), h, 0).sum() * float(P['meta']['res_m']) ** 2)
    return v / excess_m3 if excess_m3 > 0 else None


# ------------------------------------------------------------------ build
def ref_target(ref, root=ROOT):
    """LISFLOOD-FP hmax (m) and watermask of a published run folder (hmax_cm.npz), or (None, None)."""
    p = os.path.join(root, ref, 'hmax_cm.npz')
    if not os.path.exists(p): return None, None
    with np.load(p) as q: return q['hmax_cm'].astype(np.float32) / 100.0, (q['watermask'].astype(bool) if 'watermask' in q.files else None)


def write_scene(out, sid, X, y, meta):
    d = os.path.join(out, 'scenes', sid); os.makedirs(d, exist_ok=True)
    np.save(os.path.join(d, 'x.npy'), X.astype(np.float16))
    if y is not None: np.save(os.path.join(d, 'y.npy'), y.astype(np.float16))
    json.dump(meta, open(os.path.join(d, 'scene.json'), 'w'), indent=0)
    return os.path.relpath(d, out)


def items(root, plans, inputs_plan):
    """(id, split, extra, inputs path, target loader) for every scene with its files present."""
    out, miss = [], []
    for pp in plans:
        P = json.load(open(pp))
        for s in P['scenarios']:
            d = os.path.join(root, f"run_{s['id']}", 'out')
            if os.path.exists(os.path.join(d, 'surr_inputs.npz')) and os.path.exists(os.path.join(d, 'hmax.npy')):
                out.append(dict(id=s['id'], split=s['split'], kind=s['kind'], box_key=s['box_key'], box_role=s['box_role'], district=s['district'], day=s['day'],
                                scale=s['scale'], inputs=os.path.join(d, 'surr_inputs.npz'), hmax=os.path.join(d, 'hmax.npy'), ref=None))
            else: miss.append(s['id'])
    if inputs_plan:
        for x in json.load(open(inputs_plan))['items']:
            p = os.path.join(root, 'inputs', x['name'], 'surr_inputs.npz')
            if not os.path.exists(p): miss.append(x['name']); continue
            out.append(dict(id=x['name'], split='district' if x['role'].startswith('district') else 'catalog', kind='hrrr' if x['role'] == 'district_hrrr' else 'mrms',
                            box_key=None, box_role=x['role'], district=x['role'].startswith('district'), day=None, scale=1.0, storm=x['storm'], role=x['role'],
                            inputs=p, hmax=None, ref=x['ref']))
    return out, miss


def build(root, plans, inputs_plan, out, repo=ROOT, limit=None):
    os.makedirs(out, exist_ok=True); L, miss = items(root, plans, inputs_plan)
    if limit: L = L[:limit]
    log(f'{len(L)} scenes with files, {len(miss)} missing (not run or failed): {miss[:12]}{" ..." if len(miss) > 12 else ""}')
    index, cache = [], {}
    for it in L:
        t_ = time.time(); P = load_inputs(it['inputs']); key = (tuple(P['meta']['box']), tuple(P['meta']['shape']))
        if key not in cache:
            if len(cache) > 4: cache.clear()
            cache[key] = static_layers(P)
        S, R = cache[key]; X, st = rain_layers(P, R)
        if it['hmax']: y = np.nan_to_num(np.load(it['hmax']).astype(np.float32)); wm_ref = None
        else: y, wm_ref = ref_target(it['ref'], repo)
        chk = None
        if y is not None and y.shape != P['z'].shape: log(f"{it['id']}: target shape {y.shape} != inputs {P['z'].shape}: no target"); y = None
        if wm_ref is not None and wm_ref.shape == P['z'].shape: chk = float((wm_ref == watermask(P)).mean())    # inputs rebuilt now vs the published run
        if y is not None: y = np.where(P['sea'], 0, np.maximum(y, 0))
        ratio = volume_ratio(y, P, st['excess_volume_m3']) if y is not None else None
        meta = dict({k: v for k, v in it.items() if k not in ('inputs', 'hmax')}, shape=list(P['z'].shape), box=P['meta']['box'], res_m=P['meta']['res_m'], t0=P['meta']['t0'],
                    stats=dict(st, volume_ratio=ratio, wet30_land_share=float(((y >= 0.30) & land(P)).mean()) if y is not None else None, watermask_agreement=chk),
                    inputs=os.path.abspath(it['inputs']), has_target=y is not None)
        X = np.concatenate([S, X]); meta['path'] = write_scene(out, it['id'], X, y, meta); index.append(meta)
        log(f"{it['id']:28s} {it['split']:9s} {P['z'].shape} rain max {st['rain_max_mm']:.0f} mm, wet30 {meta['stats']['wet30_land_share']}, "
            f"ratio {None if ratio is None else round(ratio, 3)}, watermask agreement {chk} ({time.time() - t_:.0f} s)")
    norm = norm_stats(out, index)
    json.dump(dict(channels=CHANNELS, static=STATIC, rain=RAIN, masks=list(MASKS), made=time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), scenes=index, missing=miss),
              open(os.path.join(out, 'index.json'), 'w'), indent=0)
    json.dump(norm, open(os.path.join(out, 'norm.json'), 'w'), indent=1)
    log(f"dataset: {len(index)} scenes -> {out}; splits {count(index)}")
    return index, norm


def count(index):
    c = {}
    for m in index: c[m['split']] = c.get(m['split'], 0) + 1
    return c


def norm_stats(out, index, max_cells=400000, seed=0):
    """Channel mean / std over a sample of land cells of the train scenes (masks: mean 0, std 1); 99th percentile of the volume ratio."""
    rng = np.random.default_rng(seed); tr = [m for m in index if m['split'] == 'train' and m['has_target']]
    if not tr: tr = [m for m in index if m['has_target']]
    vals = []
    for m in tr:
        X = np.load(os.path.join(out, m['path'], 'x.npy'), mmap_mode='r'); ny, nx = X.shape[1:]
        r = rng.integers(0, ny, max_cells // max(1, len(tr))); c = rng.integers(0, nx, len(r)); v = np.asarray(X[:, r, c], np.float32).T
        vals.append(v[v[:, CHANNELS.index('sea')] < 0.5])
    V = np.concatenate(vals) if vals else np.zeros((1, len(CHANNELS)), np.float32)
    mean = V.mean(0); std = V.std(0) + 1e-6
    for k in MASKS: i = CHANNELS.index(k); mean[i], std[i] = 0.0, 1.0
    rat = [m['stats']['volume_ratio'] for m in tr if m['stats'].get('volume_ratio') is not None]
    return dict(channels=CHANNELS, mean=[float(v) for v in mean], std=[float(v) for v in std], n_cells=int(len(V)), n_scenes=len(tr),
                volume_ratio_p99=float(np.percentile(rat, 99)) if rat else None)


# ------------------------------------------------------------------ synthetic inputs (selftests of dataset / train / evaluate)
def synth_inputs(path, ny=96, nx=128, res=20.0, box=(150000.0, 905000.0), seed=0, rain_scale=1.0, T=12, coarsen=4, valley_row=None):
    """A valley with a river, a road embankment and a storm; -> (path, a 'LISFLOOD' hmax made from the inputs by a fixed formula)."""
    rng = np.random.default_rng(seed); yy, xx = np.mgrid[0:ny, 0:nx].astype(np.float32)
    vr = valley_row if valley_row is not None else ny / 2 + 6 * np.sin(xx / 17.0 + seed)
    z = 100 + 0.04 * xx + 0.25 * np.abs(yy - vr) + rng.normal(0, 0.05, (ny, nx)).astype(np.float32)
    chan = np.abs(yy - vr) < 0.7; water = chan.copy(); sea = np.zeros((ny, nx), bool); sea[:, :2] = True
    z_raw = z + 0.3 * chan; zmax = z_raw + np.where((xx % 40) < 2, 1.5, 0.1); carved = np.zeros((ny, nx), bool)
    imp = np.clip(60 * np.exp(-((xx - nx * 0.7) ** 2 + (yy - ny * 0.3) ** 2) / 300), 0, 100).astype(np.uint8)
    cn = np.where(water, 100, 70 + 0.25 * imp).astype(np.float16)
    c = (rng.uniform(0.2, 0.8) * nx, rng.uniform(0.2, 0.8) * ny); g = np.exp(-((xx - c[0]) ** 2 + (yy - c[1]) ** 2) / (2 * (nx / 4) ** 2))
    hp = np.exp(-0.5 * ((np.arange(T) - T / 2) / 2.0) ** 2); hp = hp / hp.sum()
    R = (rain_scale * 120 * hp[:, None, None] * g[None]).astype(np.float32)
    py_, px_ = (-ny) % coarsen, (-nx) % coarsen
    Rc = np.pad(R, ((0, 0), (0, py_), (0, px_)), mode='edge').reshape(T, (ny + py_) // coarsen, coarsen, (nx + px_) // coarsen, coarsen).mean(axis=(2, 4))
    mask = water.astype(np.uint8) | (chan.astype(np.uint8) << 1) | (carved.astype(np.uint8) << 2) | (sea.astype(np.uint8) << 3)
    meta = dict(box=[box[0], box[1], box[0] + nx * res, box[1] + ny * res], res_m=res, shape=[ny, nx], t0='2022-06-01T06:00Z', hours=T, rain_src='mrms',
                env=dict(LF_PARITY='1', LF_INFIL_MMH='2', LF_CN_SCALE='0.88', LF_LOSS='cn'))
    np.savez_compressed(path, z=z.astype(np.float32), z_raw=z_raw.astype(np.float32), z_raw_max10=zmax.astype(np.float32), mask=mask, imp=imp, cn=cn,
                        rain=Rc.astype(np.float16), rain_coarsen=np.int32(coarsen), meta=np.array(json.dumps(meta)))
    P = load_inputs(path); F, st = features(P)
    h = 0.15 * (10 ** F[CHANNELS.index('up_e')] / 1e3) ** 0.4 * np.exp(-np.expm1(F[CHANNELS.index('hand')]) / 3.0) + 0.6 * chan
    return path, np.where(sea, 0, h).astype(np.float32)


def synth_root(root, n_train=6, n_val=2, n_test=2, ny=96, nx=128):
    """Synthetic generator outputs + a plan + one catalogue-like inputs item (target written as a fake repo hmax_cm.npz)."""
    S = []
    for k in range(n_train + n_val + n_test):
        sid = f'sg9_{k:04d}'; d = os.path.join(root, f'run_{sid}', 'out'); os.makedirs(d, exist_ok=True)
        _, h = synth_inputs(os.path.join(d, 'surr_inputs.npz'), ny, nx, seed=k, rain_scale=0.5 + 0.25 * (k % 5))
        np.save(os.path.join(d, 'hmax.npy'), h); json.dump(dict(run=sid), open(os.path.join(d, 'meta.json'), 'w'))
        sp = 'train' if k < n_train else 'val' if k < n_train + n_val else 'test_box'
        S.append(dict(id=sid, kind='mrms', split=sp, day=f'2022-06-{k + 1:02d}', box_key='150_905', box_role='train' if sp != 'test_box' else 'hb_west', district=False, scale=1.0))
    pp = os.path.join(root, 'plan.json'); json.dump(dict(scenarios=S), open(pp, 'w'))
    d = os.path.join(root, 'inputs', 'jul2023_worcester_20m'); os.makedirs(d, exist_ok=True)
    _, h = synth_inputs(os.path.join(d, 'surr_inputs.npz'), ny, nx, seed=77)
    rr = os.path.join(root, 'repo', 'docs', 'proto', 'parity', 'catalog', 'jul2023_worcester_20m'); os.makedirs(rr, exist_ok=True)
    P = load_inputs(os.path.join(d, 'surr_inputs.npz'))
    np.savez_compressed(os.path.join(rr, 'hmax_cm.npz'), hmax_cm=np.round(h * 100).astype(np.uint16), watermask=watermask(P).astype(np.uint8))
    ip = os.path.join(root, 'inputs_plan.json')
    json.dump(dict(items=[dict(name='jul2023_worcester_20m', storm='jul2023', role='heldout23', ref='docs/proto/parity/catalog/jul2023_worcester_20m', env={})]), open(ip, 'w'))
    return pp, ip, os.path.join(root, 'repo')


def selftest():
    import tempfile
    ok = []
    # D8 on a tilted plane: everything drains east; upstream count along a row = column index + 1
    z = np.tile(np.arange(10, 0, -1, dtype=np.float32), (5, 1)); R = routing(z, np.zeros(z.shape, bool), 20.0)
    acc = accumulate(R, np.ones(z.size)).reshape(z.shape); assert np.allclose(acc[2], np.arange(1, 11)), acc[2]
    H = hand(R, z, np.zeros(z.shape, bool) | (np.arange(10) == 9)[None, :]); assert np.allclose(H[2], np.arange(9, -1, -1)), H[2]
    ok.append('D8 accumulation and HAND on a tilted plane')
    # effective excess equals w9's CN + rain-mode infiltration
    sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab')); import w9_lisflood as W9
    Pr = np.array([5, 20, 40, 10, 0, 3], np.float32)[:, None, None] * np.ones((1, 2, 2), np.float32); cn = np.array([[70, 98], [100, 55]], np.float32)
    Sx = 25400.0 / cn - 254.0; Pc = np.cumsum(Pr, 0); Q = np.where(Pc > 0.2 * Sx, (Pc - 0.2 * Sx) ** 2 / np.maximum(Pc - 0.2 * Sx + Sx, 1e-6), 0)
    ref = W9.rain_minus_infil(np.diff(np.concatenate([np.zeros_like(Q[:1]), Q]), axis=0), 2.0)[0]
    assert np.allclose(excess_rows(Pr, cn, 2.0), ref, atol=1e-4) and np.allclose(excess_rows(Pr, cn, 2.0)[:, 1, 0], np.maximum(Pr[:, 1, 0] - 2, 0))
    ok.append('effective excess = w9 SCS-CN (cumulative) then LF_INFIL_MMH per hour; water cells (CN 100) keep the rain')
    d = tempfile.mkdtemp(prefix='surr_ds_'); p, h = synth_inputs(os.path.join(d, 'a.npz'), 50, 70, coarsen=3)
    P = load_inputs(p); S, R = static_layers(P); X1, st1 = rain_layers(P, R, chunk=1000); X2, st2 = rain_layers(P, R, chunk=7)
    assert np.allclose(X1, X2, atol=1e-5) and abs(st1['excess_volume_m3'] - st2['excess_volume_m3']) < 1e-3 * max(1, st1['excess_volume_m3'])
    assert S.shape == (len(STATIC), 50, 70) and np.isfinite(S).all() and np.isfinite(X1).all() and rain_rows(P, 0, 50).shape[1:] == (50, 70)
    i = RAIN.index('p_tot'); assert abs(np.expm1(X1[i]).max() - P['rain'].astype(np.float32).sum(0).max()) < 1.0
    ok.append('rain channels identical in row chunks; coarse rain repeated to 20 m; totals preserved')
    root = os.path.join(d, 'root'); pp, ip, repo = synth_root(root)
    idx, norm = build(root, [pp], ip, os.path.join(root, 'ds'), repo=repo)
    c = count(idx); assert c == {'train': 6, 'val': 2, 'test_box': 2, 'catalog': 1}, c
    cat = [m for m in idx if m['split'] == 'catalog'][0]; assert cat['has_target'] and cat['stats']['watermask_agreement'] == 1.0
    assert len(norm['mean']) == len(CHANNELS) and norm['std'][CHANNELS.index('sea')] == 1.0 and norm['volume_ratio_p99'] > 0
    x = np.load(os.path.join(root, 'ds', idx[0]['path'], 'x.npy'), mmap_mode='r'); assert x.dtype == np.float16 and x.shape[0] == len(CHANNELS)
    ok.append(f'build: {len(idx)} scenes, splits {c}, norm stats, catalogue target from the repo hmax_cm.npz, watermask check')
    for o in ok: print('ok  ', o)
    print(f'DATASET SELFTEST PASSED ({len(ok)} checks)'); return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd')
    p = sp.add_parser('build'); p.add_argument('--root', default=os.path.expanduser('~/scratch/surrogate')); p.add_argument('--plans', required=True)
    p.add_argument('--inputs-plan'); p.add_argument('--out', required=True); p.add_argument('--repo', default=ROOT); p.add_argument('--limit', type=int)
    sp.add_parser('selftest')
    a = ap.parse_args()
    if a.cmd == 'selftest': sys.exit(0 if selftest() else 1)
    if a.cmd == 'build': build(a.root, [x for x in a.plans.split(',') if x], a.inputs_plan, a.out, a.repo, a.limit); return
    ap.print_help()


if __name__ == '__main__':
    main()
