"""Per-cell training table for the flood-depth surrogate, built from finished engine runs (w4_flood_gpu.py outputs).

    python dataset.py --runs /path/run_dec2023_v3_30m /path/run_sep2023_v3_30m --soils data/soils30/soils30.npz \
                      --channels data/channels30/channels30.npz --huc10 data/huc10_30/huc10_30.npz --nlcd10 data/nlcd10 --out ml/ds_v3
    python dataset.py --selftest                     (synthetic box, runs, soils, channels, HUC10 -> builds shards in a temp dir and checks them)
    ML_RUNS=runs/dec2023_v3_30m,runs/sep2023_v3_30m ML_OUT=ml/datasets/v3_30m HF_TOKEN=... python dataset.py     (queue step "dataset", see README.md)

One row per sampled cell:  static features (terrain, drainage, soils, pavement, channel) + storm features (rain windows, antecedent
store, experiment knobs) + targets (hmax m, t_first h, dur h, wet) + split keys (storm id, HUC10 id, spatial fold).  All wet cells
(hmax >= WET_M) are kept; dry cells are a stratified sample (by height above the drained-to channel, HAND bins) with `weight` =
1 / sampling probability so population rates can be recovered.  Work is done tile by tile (TILE x TILE cells) and flushed to
Parquet (or NPZ when pyarrow is missing) every ROWS_PER_SHARD rows, so memory is bounded by the static layers of one run grid
(~10 float32 arrays; 4 M cells for a district box = 160 MB, 44 M cells statewide = 1.8 GB -> use High-RAM for statewide).

Inputs per run directory (local, or runs/<name> on Hugging Face with --hf):  meta.json, hmax.npy, z.npy, t_first.npy, dur.npy,
    vmax.npy (optional), rain_hourly.npz (optional: mm[hours, ry, rx] float16 + box + res_m, a coarse copy of the MRMS hours; without it
    the rain windows fall back to the meta totals and `rain_grid` = 0), imp.npy (optional paved fraction on the run grid).
Static whole-state grids (npz + sibling *_meta.json with box, res_m, shape, same convention as hf_grid in w4):  --soils (hydgrp, wtd,
    aws, brock), --channels (chan, water, area, width, depth), --huc10 (huc10 int64, 0 = outside).  --nlcd10 is a dir of 10 m PNG
    tiles with index.json (the HF data/nlcd10 layout) used when a run has no imp.npy.  --imp is an alternative whole-state grid (imp).
Splits (docs/validation/protocol.md):  `storm` = run name up to the first '_' (all parameter variants of a storm share it, for
    leave-one-storm-out) and `fold` = deterministic hash of the HUC10 id into --folds spatial blocks; `split` = "<storm>/h<fold>".
    Without a HUC10 raster the fold comes from 20 km grid blocks and `block_src` says so (loud warning; not the pre-registered split).
"""
import os, sys, json, time, math, argparse, hashlib, tempfile
import numpy as np
from scipy import ndimage

WET_M = 0.10                                      # protocol: wet = 10 cm
HAND_BINS = np.array([1.0, 3.0, 10.0, 30.0])     # dry-cell strata: height above the drained-to channel (m); 5 bins incl. above 30 and NaN merged into last
STATIC_FEATURES = ['z', 'slope', 'tpi150', 'hand', 'hand_eucl', 'dist_chan_m', 'flow_dist_m', 'uparea_km2', 'chan_area_km2', 'chan_width_m', 'chan_depth_m',
                   'pit', 'imp', 'hydgrp', 'aws_mm', 'wtd_cm', 'brock_cm', 'scap_mm', 'chan']
STORM_FEATURES = ['rain_1h_mm', 'rain_3h_mm', 'rain_6h_mm', 'rain_24h_mm', 'rain_total_mm', 'rain_grid', 'ante_mm', 'ante_frac', 'fc_scale', 'hours']
TARGETS = ['hmax', 't_first_h', 'dur_h', 'wet', 'vmax']
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)

# ---------------------------------------------------------------- file access (local dir, or Hugging Face when --hf) ----
REPO = 'mohabeldokla/mass-flood-watch-tiles'
class Files:
    """fetch('runs/x/hmax.npy') -> local path.  Local paths are returned as they are; with hf=True missing paths are downloaded."""
    def __init__(self, hf=False, cache=None):
        self.hf = hf; self.cache = cache or os.path.join(tempfile.gettempdir(), 'mfw_ml_cache'); self.tok = os.environ.get('HF_TOKEN')
    def fetch(self, path, required=True):
        if os.path.exists(path): return path
        if self.hf:
            try:
                from huggingface_hub import hf_hub_download
                return hf_hub_download(REPO, path, repo_type='dataset', token=self.tok, cache_dir=self.cache)
            except Exception as e:
                if required: raise FileNotFoundError(f'{path}: {e!r}')
                return None
        if required: raise FileNotFoundError(path)
        return None

def state_grid(F, npz_path, fields, box, res, shape):
    """Cut a whole-state grid (npz + *_meta.json with box/res_m/shape) to a run box by nearest neighbour, like hf_grid in w4_flood_gpu.py."""
    meta_path = npz_path.replace('.npz', '_meta.json').replace('.npy', '_meta.json')
    D = np.load(F.fetch(npz_path)); M = json.load(open(F.fetch(meta_path)))
    sx0, sy0, sx1, sy1 = M['box']; sres = M['res_m']; ny, nx = shape; x0, y0, x1, y1 = box
    rr = np.clip(((sy1 - (y1 - (np.arange(ny) + 0.5) * res)) / sres).astype(int), 0, M['shape'][0] - 1)
    cc = np.clip(((x0 + (np.arange(nx) + 0.5) * res - sx0) / sres).astype(int), 0, M['shape'][1] - 1)
    out = {}
    for f in fields:
        a = D[f] if hasattr(D, 'files') else D                                   # .npy holds a single array
        out[f] = a[rr][:, cc]
    # cells outside the state grid get NaN-able sentinels: mark them so callers can mask
    outside = ((y1 - (np.arange(ny) + 0.5) * res) > sy1) | ((y1 - (np.arange(ny) + 0.5) * res) < sy0)
    outside = outside[:, None] | (((x0 + (np.arange(nx) + 0.5) * res) < sx0) | ((x0 + (np.arange(nx) + 0.5) * res) > sx1))[None, :]
    out['_outside'] = outside
    return out

def tiles10(F, tdir, box, res, shape, kind='png'):
    """Assemble 10 m tiles (index.json: key -> {x, y, valid}, tiles of T m) over the run box and average to the run resolution (w4 logic, local dir)."""
    idx = json.load(open(F.fetch(f'{tdir}/index.json'))); T = float(idx.pop('_tile_m', 20000))                       # HF tiles are 20 km; the selftest writes smaller ones
    x0, y0, x1, y1 = box; k = int(round(res / 10)); ny, nx = shape; nx10, ny10 = nx * k, ny * k
    A = np.full((ny10, nx10), np.nan, np.float32); got = 0
    for key, v in idx.items():
        if not isinstance(v, dict) or v.get('valid', 1) <= 0 or not (v['x'] < x1 and v['x'] + T > x0 and v['y'] < y1 and v['y'] + T > y0): continue
        p = F.fetch(f'{tdir}/{key}.{kind}', required=False)
        if p is None: continue
        if kind == 'png':
            from PIL import Image
            a = np.asarray(Image.open(p)).astype(np.float32)
        else: a = np.load(p).astype(np.float32)
        c0 = int((v['x'] - x0) / 10); r0 = int((y1 - (v['y'] + T)) / 10)
        rs, cs = max(r0, 0), max(c0, 0); re_, ce = min(r0 + a.shape[0], ny10), min(c0 + a.shape[1], nx10)
        if re_ > rs and ce > cs: A[rs:re_, cs:ce] = a[rs - r0:re_ - r0, cs - c0:ce - c0]; got += 1
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning); out = np.nanmean(A.reshape(ny, k, nx, k), axis=(1, 3)).astype(np.float32)   # all-NaN blocks (no tile) stay NaN
    return out, got

# ---------------------------------------------------------------- static features on one run grid ----
def d8_next(Z, terminal):
    """Index of the steepest downhill neighbour for every cell (flattened), self for terminals, pits and cells draining off the grid."""
    ny, nx = Z.shape; n = ny * nx; Zp = np.pad(Z, 1, constant_values=-1e9)                 # -1e9 outside: border cells drain off the grid (open boundary in w4)
    best = np.zeros((ny, nx), np.float32); nxt = np.arange(n, dtype=np.int64).reshape(ny, nx); step = np.zeros((ny, nx), np.float32)
    for dr, dc in ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)):
        d = math.hypot(dr, dc); drop = (Z - Zp[1 + dr:1 + dr + ny, 1 + dc:1 + dc + nx]) / d
        better = drop > best
        rr = np.clip(np.arange(ny)[:, None] + dr, -1, ny); cc = np.clip(np.arange(nx)[None, :] + dc, -1, nx)
        off = (rr < 0) | (rr >= ny) | (cc < 0) | (cc >= nx)                                 # flows off the grid -> terminal (self)
        tgt = np.where(off, nxt, np.clip(rr, 0, ny - 1) * nx + np.clip(cc, 0, nx - 1))
        nxt = np.where(better, tgt, nxt); step = np.where(better, np.where(off, 0, d), step); best = np.where(better, drop, best)
    nxt = nxt.ravel(); step = step.ravel()
    t = terminal.ravel(); nxt[t] = np.arange(n)[t]; step[t] = 0
    return nxt, step

def route(nxt, step, res):
    """Pointer jumping: root (terminal reached), hops and flow-path length for every cell in O(n log L)."""
    root = nxt.copy(); hops = (nxt != np.arange(len(nxt))).astype(np.int32); dist = step.astype(np.float32) * res
    for _ in range(64):
        nr = root[root]
        if np.array_equal(nr, root): break
        hops = hops + hops[root]; dist = dist + dist[root]; root = nr
    return root, hops, dist

def accumulate(nxt, hops):
    """D8 upstream cell count: cells ordered by hops to the terminal (a cell always drains to one with fewer hops), added level by level."""
    n = len(nxt); acc = np.ones(n, np.float32); order = np.argsort(-hops, kind='stable'); h = hops[order]
    bounds = np.flatnonzero(np.diff(h)) + 1; starts = np.r_[0, bounds]; ends = np.r_[bounds, n]
    for s, e in zip(starts, ends):
        if h[s] == 0: break
        idx = order[s:e]; np.add.at(acc, nxt[idx], acc[idx])
    return acc

def static_features(F, run, args):
    """All static layers for one run grid as a dict of (ny, nx) float32 arrays; cached per (box, res) because parameter variants share the grid."""
    meta = run['meta']; box = tuple(meta['box']); res = float(meta['res_m']); shape = tuple(meta['shape'])
    key = hashlib.md5(json.dumps([box, res, shape, args.soils, args.channels, args.imp, args.nlcd10]).encode()).hexdigest()[:10]
    cpath = os.path.join(args.cache, f'static_{key}.npz')
    if os.path.exists(cpath) and not args.no_cache:
        D = np.load(cpath); log(f'   statics from cache {cpath}'); return {k: D[k] for k in D.files}
    Z = np.load(F.fetch(f"{run['dir']}/z.npy")).astype(np.float32); ny, nx = Z.shape; assert (ny, nx) == shape, f'z.npy {Z.shape} vs meta shape {shape}'
    S = {'z': Z}
    gy, gx = np.gradient(Z, res); S['slope'] = np.hypot(gy, gx).astype(np.float32)                                  # m/m (channels are burnt in z: slope is steep at banks)
    S['tpi150'] = (Z - ndimage.uniform_filter(Z, size=max(3, int(round(150 / res)) | 1), mode='nearest')).astype(np.float32)
    # sea as in w4: low ground (<= 0.3 m, or the -2 m void fill) connected to the box edge
    low = Z <= 0.3; lab, _ = ndimage.label(low); edge = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]); edge = edge[edge > 0]; sea = np.isin(lab, edge); del lab
    # channels / open water
    if args.channels:
        CH = state_grid(F, args.channels, ['chan', 'water', 'area', 'width', 'depth'], box, res, shape)
        chan = CH['chan'].astype(bool) & ~sea; water = CH['water'].astype(bool) | sea
        carea = np.where(chan, CH['area'].astype(np.float32), 0); cw = np.where(chan, CH['width'].astype(np.float32), 0); cd = np.where(chan, CH['depth'].astype(np.float32), 0)
    else:
        log('   WARNING no channel grid: channels = local drainage minima (upstream >= 1 km2 after routing); widths/depths NaN')
        chan = np.zeros(shape, bool); water = sea.copy(); carea = np.zeros(shape, np.float32); cw = np.full(shape, np.nan, np.float32); cd = np.full(shape, np.nan, np.float32)
    # routing: D8 on the run DEM, stop at channels / sea / pits / off-grid
    nxt, step = d8_next(Z, chan | sea); root, hops, fdist = route(nxt, step, res); acc = accumulate(nxt, hops)
    if not args.channels:                                                                                             # fallback channels: cells with >= 1 km2 upstream
        chan = (acc.reshape(shape) * res * res / 1e6 >= 1.0) & ~sea; nxt, step = d8_next(Z, chan | sea); root, hops, fdist = route(nxt, step, res); acc = accumulate(nxt, hops)
    S['uparea_km2'] = np.maximum(acc.reshape(shape) * res * res / 1e6, carea).astype(np.float32); del acc
    # Euclidean distance to the nearest channel cell and HAND against that cell
    if (chan | sea).any():
        ed, (ir, ic) = ndimage.distance_transform_edt(~(chan | sea), return_indices=True); S['dist_chan_m'] = (ed * res).astype(np.float32); S['hand_eucl'] = (Z - Z[ir, ic]).astype(np.float32)
        # flow paths that end in a pit (lidar DEMs are full of them) or leave the grid: spill the pit to its nearest channel cell, so HAND, the
        # drained-to channel and the path length are defined everywhere (no priority-flood fill needed; upstream area stays local to the pit)
        near = (ir * nx + ic).ravel(); pit = ~(chan | sea).ravel()[root]; root2 = np.where(pit, near[root], root); fdist = fdist + np.where(pit, ed.ravel()[root] * res, 0); del ed, ir, ic, near
    else:
        S['dist_chan_m'] = np.full(shape, np.nan, np.float32); S['hand_eucl'] = np.full(shape, np.nan, np.float32); root2 = root; pit = np.ones(len(root), bool)
    S['hand'] = (Z - Z.ravel()[root2].reshape(shape)).astype(np.float32); S['flow_dist_m'] = fdist.reshape(shape).astype(np.float32); S['pit'] = pit.reshape(shape).astype(np.float32)
    S['chan_area_km2'] = carea.ravel()[root2].reshape(shape).astype(np.float32); S['chan_width_m'] = cw.ravel()[root2].reshape(shape).astype(np.float32); S['chan_depth_m'] = cd.ravel()[root2].reshape(shape).astype(np.float32)
    if not args.channels:
        for k in ('chan_area_km2', 'chan_width_m', 'chan_depth_m'): S[k] = np.where(S[k] > 0, S[k], np.nan).astype(np.float32)
    del nxt, step, root, root2, hops, fdist, pit
    S['chan'] = chan.astype(np.float32); S['water'] = water.astype(np.float32); S['sea'] = sea.astype(np.float32)
    # soils (SSURGO 30 m): same decoding as w4 (dual groups and shallow water table -> D; storage cap from aws cut by water table / bedrock)
    if args.soils:
        SO = state_grid(F, args.soils, ['hydgrp', 'wtd', 'aws', 'brock'], box, res, shape); hg = SO['hydgrp'].astype(np.int64); wt = SO['wtd'].astype(np.float32); br = SO['brock'].astype(np.float32)
        grp = np.where(hg >= 5, 4, hg); grp[(wt < 25) & (grp > 0)] = 4
        aws = SO['aws'].astype(np.float32) * 10.0; aws = np.where(aws > 0, aws, 120.0)
        dlim = np.minimum(np.where(wt < 255, wt * 2.0, 200.0), np.where(br < 255, br * 2.0, 200.0))
        S['scap_mm'] = np.maximum(aws * np.clip(dlim / 100.0, 0.1, 1.0), 20.0).astype(np.float32)
        S['hydgrp'] = np.where(SO['_outside'], np.nan, grp).astype(np.float32); S['aws_mm'] = np.where(SO['aws'] > 0, aws, np.nan).astype(np.float32)
        S['wtd_cm'] = np.where(wt < 255, wt * 2.0, np.nan).astype(np.float32); S['brock_cm'] = np.where(br < 255, br * 2.0, np.nan).astype(np.float32)
    else:
        log('   WARNING no soils grid: soil features NaN, storage cap 120 mm (w4 default)')
        for k in ('hydgrp', 'aws_mm', 'wtd_cm', 'brock_cm'): S[k] = np.full(shape, np.nan, np.float32)
        S['scap_mm'] = np.full(shape, 120.0, np.float32)
    # impervious fraction: per-run imp.npy > whole-state grid > 10 m NLCD tiles > NaN
    p = F.fetch(f"{run['dir']}/imp.npy", required=False)
    if p is not None: S['imp'] = np.load(p).astype(np.float32)
    elif args.imp: G = state_grid(F, args.imp, ['imp'], box, res, shape); S['imp'] = (G['imp'].astype(np.float32) / (100.0 if G['imp'].max() > 1.5 else 1.0))
    elif args.nlcd10:
        a, got = tiles10(F, args.nlcd10, box, res, shape, kind='png'); S['imp'] = (a / 100.0).astype(np.float32); log(f'   NLCD impervious from {got} tiles')
    else: log('   WARNING no impervious source: imp NaN'); S['imp'] = np.full(shape, np.nan, np.float32)
    S['imp'] = np.where(np.isfinite(S['imp']), np.clip(S['imp'], 0, 1), np.nan).astype(np.float32)
    os.makedirs(args.cache, exist_ok=True); np.savez(cpath, **S); log(f'   statics cached -> {cpath}')
    return S

# ---------------------------------------------------------------- storm features ----
def rain_windows(F, run, shape):
    """Max rolling 1/3/6/24 h rain and the storm total on the run grid (from rain_hourly.npz, nearest neighbour); meta totals as the fallback."""
    meta = run['meta']; p = F.fetch(f"{run['dir']}/rain_hourly.npz", required=False)
    if p is None:
        tot = float(meta.get('rain_total_mean_mm', np.nan)); log(f'   WARNING no rain_hourly.npz: rain windows = meta mean total {tot} mm everywhere (rain_grid 0)')
        W = {k: np.full(shape, tot, np.float32) for k in ('rain_1h_mm', 'rain_3h_mm', 'rain_6h_mm', 'rain_24h_mm', 'rain_total_mm')}; W['rain_grid'] = np.zeros(shape, np.float32); return W
    R = np.load(p); mm = R['mm'].astype(np.float32); rbox = tuple(float(v) for v in R['box']); rres = float(R['res_m']); nh, ry, rx = mm.shape
    cs = np.cumsum(np.concatenate([np.zeros((1, ry, rx), np.float32), mm]), axis=0)
    def maxwin(w): w = min(w, nh); return (cs[w:] - cs[:-w]).max(axis=0)
    C = {'rain_1h_mm': maxwin(1), 'rain_3h_mm': maxwin(3), 'rain_6h_mm': maxwin(6), 'rain_24h_mm': maxwin(24), 'rain_total_mm': cs[-1]}
    x0, y0, x1, y1 = meta['box']; res = float(meta['res_m']); ny, nx = shape
    rr = np.clip(((rbox[3] - (y1 - (np.arange(ny) + 0.5) * res)) / rres).astype(int), 0, ry - 1); cc = np.clip((((x0 + (np.arange(nx) + 0.5) * res) - rbox[0]) / rres).astype(int), 0, rx - 1)
    W = {k: v[rr][:, cc].astype(np.float32) for k, v in C.items()}; W['rain_grid'] = np.ones(shape, np.float32); return W

def storm_id(run_name, override):
    """'jul2023_southriver_v3' -> 'jul2023'; parameter variants and sub-boxes of a storm are held out together in leave-one-storm-out."""
    return override.get(run_name) or run_name.split('_')[0]

# ---------------------------------------------------------------- splits ----
def huc_fold(F, args, box, res, shape):
    """HUC10 id per cell + spatial fold (stable hash of the id); 20 km grid blocks when no HUC10 raster is given."""
    x0, y0, x1, y1 = box; ny, nx = shape
    if args.huc10:
        H = state_grid(F, args.huc10, ['huc10'], box, res, shape); huc = H['huc10'].astype(np.int64); src = 'huc10'
    else:
        log('   WARNING no HUC10 raster: spatial folds from 20 km grid blocks (NOT the pre-registered split)')
        bx = np.floor((x0 + (np.arange(nx) + 0.5) * res) / 20000).astype(np.int64); by = np.floor((y1 - (np.arange(ny) + 0.5) * res) / 20000).astype(np.int64)
        huc = (by[:, None] * 100000 + bx[None, :]).astype(np.int64) + 1; src = 'grid20km'
    fold = ((huc * np.int64(2654435761)) >> np.int64(13)) % np.int64(args.folds); fold = np.where(huc > 0, fold, -1).astype(np.int8)
    return huc, fold, src

# ---------------------------------------------------------------- sampling and shards ----
class Writer:
    def __init__(self, out, fmt, rows_per_shard):
        self.out = out; self.fmt = fmt; self.cap = rows_per_shard; self.buf = []; self.n = 0; self.shards = []; os.makedirs(out, exist_ok=True)
        if fmt == 'parquet':
            try: import pyarrow  # noqa
            except ImportError: log('pyarrow missing -> NPZ shards'); self.fmt = 'npz'
    def add(self, df):
        self.buf.append(df); self.n += len(df)
        if self.n >= self.cap: self.flush()
    def flush(self):
        if not self.buf: return
        import pandas as pd
        df = pd.concat(self.buf, ignore_index=True); k = len(self.shards); self.buf = []; self.n = 0
        if self.fmt == 'parquet': p = os.path.join(self.out, f'part-{k:04d}.parquet'); df.to_parquet(p, index=False)
        else: p = os.path.join(self.out, f'part-{k:04d}.npz'); np.savez_compressed(p, **{c: (df[c].astype(str).values.astype('U') if (pd.api.types.is_string_dtype(df[c]) or pd.api.types.is_object_dtype(df[c])) else df[c].values) for c in df.columns})
        self.shards.append(dict(file=os.path.basename(p), rows=int(len(df)))); log(f'   shard {os.path.basename(p)}: {len(df):,} rows')

def sample_tile(rng, hmax_t, hand_t, valid_t, dry_ratio, dry_min):
    """Indices (flat, within the tile) of all wet cells + a HAND-stratified sample of dry cells, and the sampling weight of each row."""
    wet = (hmax_t >= WET_M) & valid_t; dry = (hmax_t < WET_M) & valid_t
    iw = np.flatnonzero(wet); n_target = max(int(dry_ratio * len(iw)), dry_min if dry.any() else 0)
    if n_target == 0 or not dry.any(): return iw, np.ones(len(iw), np.float32)
    strata = np.digitize(np.nan_to_num(hand_t, nan=1e9), HAND_BINS)                       # 0..4 by HAND; NaN -> last stratum
    cands = [np.flatnonzero(dry & (strata == s)) for s in range(len(HAND_BINS) + 1)]; avail = np.array([len(c) for c in cands])
    take = np.minimum(avail, n_target // max((avail > 0).sum(), 1))                                                   # equal share per stratum ...
    for _ in range(len(cands)):                                                                                       # ... and the shortfall of thin strata handed to the others
        short = n_target - take.sum(); room = avail - take
        if short <= 0 or room.sum() == 0: break
        take = take + np.minimum(room, np.ceil(short * room / room.sum()).astype(int)); take = np.minimum(take, avail)
    idx, wts = [iw], [np.ones(len(iw), np.float32)]
    for cand, t in zip(cands, take):
        if t == 0: continue
        pick = rng.choice(cand, size=int(t), replace=False) if t < len(cand) else cand
        idx.append(pick); wts.append(np.full(len(pick), len(cand) / len(pick), np.float32))
    return np.concatenate(idx), np.concatenate(wts)

def build(args):
    import pandas as pd
    F = Files(hf=args.hf, cache=args.cache); os.makedirs(args.cache, exist_ok=True)
    override = dict(kv.split('=') for kv in (args.storm or [])); W = Writer(args.out, args.format, args.rows_per_shard)
    manifest = dict(created=time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), wet_m=WET_M, dry_ratio=args.dry_ratio, folds=args.folds, tile=args.tile, runs=[], features=STATIC_FEATURES + STORM_FEATURES, targets=TARGETS, shards=[])
    for rdir in args.runs:
        rdir = rdir.rstrip('/'); meta = json.load(open(F.fetch(f'{rdir}/meta.json'))); run = dict(dir=rdir, meta=meta, name=meta.get('run') or os.path.basename(rdir))
        shape = tuple(meta['shape']); res = float(meta['res_m']); box = tuple(meta['box']); x0, y0, x1, y1 = box; fm = float(meta.get('frame_min', 30)) / 60.0
        storm = storm_id(run['name'], override); log(f"run {run['name']} ({storm}): {shape[0]} x {shape[1]} at {res:.0f} m")
        S = static_features(F, run, args); R = rain_windows(F, run, shape); huc, fold, bsrc = huc_fold(F, args, box, res, shape)
        hmax = np.load(F.fetch(f'{rdir}/hmax.npy')).astype(np.float32); tf = np.load(F.fetch(f'{rdir}/t_first.npy')); du = np.load(F.fetch(f'{rdir}/dur.npy'))
        pv = F.fetch(f'{rdir}/vmax.npy', required=False); vmax = np.load(pv).astype(np.float32) if pv else np.full(shape, np.nan, np.float32)
        ante = float(meta.get('physics', {}).get('antecedent_mm', meta.get('infiltration', {}).get('wet_start_mm', np.nan))); fc = float(meta.get('experiment', {}).get('fc_scale', 1.0)); hours = float(meta.get('frame_min', 30)) * (len(meta.get('frames', [])) - 1) / 60.0 if meta.get('frames') else np.nan
        rng = np.random.default_rng(int(hashlib.md5(run['name'].encode()).hexdigest()[:8], 16) ^ args.seed)
        valid = (S['water'] == 0) & (S['sea'] == 0) & (fold >= 0) & np.isfinite(hmax) if not args.keep_water else (fold >= 0) & np.isfinite(hmax)
        n_rows = n_wet = 0; T = args.tile
        for r0 in range(0, shape[0], T):
            for c0 in range(0, shape[1], T):
                sl = (slice(r0, min(r0 + T, shape[0])), slice(c0, min(c0 + T, shape[1]))); h_t = hmax[sl]
                idx, wts = sample_tile(rng, h_t, S['hand'][sl], valid[sl], args.dry_ratio, args.dry_min)
                if len(idx) == 0: continue
                rr, cc = np.unravel_index(idx, h_t.shape); rr = rr + r0; cc = cc + c0
                d = dict(run=run['name'], storm=storm, row=rr.astype(np.int32), col=cc.astype(np.int32), x=(x0 + (cc + 0.5) * res).astype(np.float32), y=(y1 - (rr + 0.5) * res).astype(np.float32),
                         huc10=huc[rr, cc], fold=fold[rr, cc], weight=wts)
                d['split'] = [f'{storm}/h{f}' for f in d['fold']]
                for k in STATIC_FEATURES: d[k] = S[k][rr, cc]
                for k in ('rain_1h_mm', 'rain_3h_mm', 'rain_6h_mm', 'rain_24h_mm', 'rain_total_mm', 'rain_grid'): d[k] = R[k][rr, cc]
                d['ante_mm'] = np.full(len(rr), ante, np.float32); d['ante_frac'] = (np.minimum(ante, 0.9 * S['scap_mm'][rr, cc]) / S['scap_mm'][rr, cc]).astype(np.float32)
                d['fc_scale'] = np.full(len(rr), fc, np.float32); d['hours'] = np.full(len(rr), hours, np.float32)
                d['hmax'] = h_t[rr - r0, cc - c0]; t_ = tf[rr, cc].astype(np.float32); d['t_first_h'] = np.where(tf[rr, cc] == 255, np.nan, t_ * fm).astype(np.float32)
                d['dur_h'] = (du[rr, cc].astype(np.float32) * fm); d['wet'] = (d['hmax'] >= WET_M).astype(np.int8); d['vmax'] = vmax[rr, cc]
                W.add(pd.DataFrame(d)); n_rows += len(rr); n_wet += int(d['wet'].sum())
        manifest['runs'].append(dict(run=run['name'], dir=rdir, storm=storm, box=list(box), res_m=res, shape=list(shape), rows=n_rows, wet=n_wet, wet_cells_total=int(((hmax >= WET_M) & valid).sum()),
                                     valid_cells=int(valid.sum()), rain_grid=bool(R['rain_grid'].max() > 0), antecedent_mm=ante, fc_scale=fc, block_src=bsrc))
        log(f'   {n_rows:,} rows ({n_wet:,} wet of {int(((hmax >= WET_M) & valid).sum()):,} wet cells; {int(valid.sum()):,} valid cells)')
        del S, R, hmax, tf, du, vmax, huc, fold, valid
    W.flush(); manifest['shards'] = W.shards; manifest['format'] = W.fmt; manifest['rows'] = int(sum(s['rows'] for s in W.shards))
    json.dump(manifest, open(os.path.join(args.out, 'manifest.json'), 'w'), indent=1); log(f"dataset: {manifest['rows']:,} rows in {len(W.shards)} shards -> {args.out}")
    if args.upload and os.environ.get('HF_TOKEN'):
        from huggingface_hub import HfApi
        api = HfApi(token=os.environ['HF_TOKEN'])
        for f in sorted(os.listdir(args.out)): api.upload_file(path_or_fileobj=os.path.join(args.out, f), path_in_repo=f'{args.upload}/{f}', repo_id=REPO, repo_type='dataset', commit_message=f'ml dataset {args.upload}: {f}')
        log('uploaded to', args.upload)
    return manifest

def load_dataset(out):
    """Read every shard back into one pandas frame (used by baseline.py and the selftest)."""
    import pandas as pd
    man = json.load(open(os.path.join(out, 'manifest.json'))); parts = []
    for s in man['shards']:
        p = os.path.join(out, s['file'])
        if p.endswith('.parquet'): parts.append(pd.read_parquet(p))
        else:
            D = np.load(p, allow_pickle=False); parts.append(pd.DataFrame({k: D[k] for k in D.files}))
    return pd.concat(parts, ignore_index=True), man

# ---------------------------------------------------------------- synthetic world for the selftest ----
def make_synthetic(root, n_storms=3, variants=2, ny=120, nx=160, res=30.0, seed=0):
    """A small 'state' (soils, channels, HUC10, nlcd10 tiles) and n_storms x variants fake runs whose depths follow HAND and rain, written in the real file layouts."""
    rng = np.random.default_rng(seed); x0, y0 = 200000.0, 880000.0; x1, y1 = x0 + nx * res, y0 + ny * res; box = [x0, y0, x1, y1]
    yy, xx = np.mgrid[0:ny, 0:nx]
    Z = 60 + 0.25 * (nx - xx) + 8 * np.sin(yy / 9.0) + 15 * np.abs(yy - ny / 2) / (ny / 2) + rng.normal(0, 0.4, (ny, nx)); Z = Z.astype(np.float32)   # valley along the middle row, sloping east
    chan = np.abs(yy - ny / 2 - 4 * np.sin(xx / 15.0)) < 1.2; area = np.where(chan, 5 + 0.6 * xx, 0).astype(np.float32)
    Z[chan] -= 2.0; water = ndimage.binary_dilation(chan, iterations=1)
    os.makedirs(f'{root}/data/channels30', exist_ok=True); os.makedirs(f'{root}/data/soils30', exist_ok=True); os.makedirs(f'{root}/data/huc10_30', exist_ok=True); os.makedirs(f'{root}/data/nlcd10', exist_ok=True)
    smeta = dict(box=box, res_m=res, shape=[ny, nx], crs='EPSG:26986')
    np.savez_compressed(f'{root}/data/channels30/channels30.npz', chan=chan, water=water, area=area, width=(2.7 * area ** 0.352).astype(np.float16), depth=(0.3 * area ** 0.213).astype(np.float16))
    json.dump(smeta, open(f'{root}/data/channels30/channels30_meta.json', 'w'))
    hg = rng.integers(1, 5, (ny, nx)).astype(np.uint8); hg[rng.random((ny, nx)) < 0.05] = 0
    np.savez_compressed(f'{root}/data/soils30/soils30.npz', hydgrp=hg, wtd=np.where(rng.random((ny, nx)) < 0.3, rng.integers(10, 90, (ny, nx)), 255).astype(np.uint8),
                        aws=rng.integers(5, 25, (ny, nx)).astype(np.uint8), brock=np.where(rng.random((ny, nx)) < 0.2, rng.integers(20, 100, (ny, nx)), 255).astype(np.uint8), ksat=hg, drcl=hg)
    json.dump(smeta, open(f'{root}/data/soils30/soils30_meta.json', 'w'))
    huc = (1900000000 + (yy // 40) * 10 + (xx // 40)).astype(np.int64)                                      # 12 fake HUC10 blocks of 40 x 40 cells
    np.savez_compressed(f'{root}/data/huc10_30/huc10_30.npz', huc10=huc); json.dump(smeta, open(f'{root}/data/huc10_30/huc10_30_meta.json', 'w'))
    # 10 m NLCD tiles: 2 tiles of 2400 m (240 cells of 10 m) covering the west part only, so the east gets NaN -> tests the missing-tile path
    from PIL import Image
    T = 2400; idx = {'_tile_m': T}; imp_true = np.clip(rng.random((ny, nx)) ** 4 * 100 + 40 * (np.abs(yy - 20) < 6), 0, 100).astype(np.float32)
    for i, (tx, ty) in enumerate(((x0, y1 - T), (x0, y1 - 2 * T))):
        key = f't{i}'; idx[key] = dict(x=tx, y=ty, valid=1); r0 = int((y1 - (ty + T)) / 10); c0 = int((tx - x0) / 10)
        a = np.repeat(np.repeat(imp_true, 3, axis=0), 3, axis=1)[r0:r0 + T // 10, c0:c0 + T // 10]; full = np.zeros((T // 10, T // 10), np.uint8); full[:a.shape[0], :a.shape[1]] = a.astype(np.uint8)
        Image.fromarray(full, 'L').save(f'{root}/data/nlcd10/{key}.png')
    json.dump(idx, open(f'{root}/data/nlcd10/index.json', 'w'))
    # a quick HAND for the fake depths (Euclidean nearest channel)
    _, (ir, ic) = ndimage.distance_transform_edt(~chan, return_indices=True); hand = Z - Z[ir, ic]
    runs = []
    for s in range(n_storms):
        base = [25, 60, 110][s % 3]; t0 = f'2023-0{s + 6}-10T12:00Z'
        for v in range(variants):
            name = f'storm{s}' + ('' if v == 0 else f'_v{v}'); rdir = f'{root}/runs/{name}_30m'; os.makedirs(rdir, exist_ok=True)
            fc = [1.0, 0.5][v % 2]; rain = base * (1 + 0.5 * np.exp(-((xx - 40 * s - 30) ** 2 + (yy - 60) ** 2) / 1200.0)) * rng.uniform(0.9, 1.1)
            hours = 24; mm = np.zeros((hours, ny // 4, nx // 4), np.float32); prof = np.exp(-((np.arange(hours) - 8) ** 2) / 12.0); prof /= prof.sum()
            for h in range(hours): mm[h] = (rain[::4, ::4] * prof[h])
            depth = np.clip(0.9 * rain / 60 / fc - 0.6 * np.maximum(hand, 0) + 0.3 * imp_true / 100 + rng.normal(0, 0.08, (ny, nx)), 0, None).astype(np.float32); depth[water] += 0.5
            wet = depth >= WET_M; tf = np.where(wet, np.clip(16 - 20 * depth, 2, 40), 255).astype(np.uint8); du = np.where(wet, np.clip(4 + 30 * depth, 1, 48), 0).astype(np.uint8)
            np.save(f'{rdir}/hmax.npy', depth.astype(np.float16)); np.save(f'{rdir}/z.npy', Z); np.save(f'{rdir}/t_first.npy', tf); np.save(f'{rdir}/dur.npy', du); np.save(f'{rdir}/vmax.npy', (depth * 0.5).astype(np.float16))
            np.savez_compressed(f'{rdir}/rain_hourly.npz', mm=mm.astype(np.float16), box=np.array(box), res_m=res * 4, hours=np.array([f'{t0[:11]}{h:02d}:00Z' for h in range(hours)]))
            meta = dict(run=name, title='synthetic', experiment=dict(fc_scale=fc, wet_start_mm=0.0), res_m=res, box=box, crs='EPSG:26986', shape=[ny, nx], t0=t0, frame_min=30,
                        frames=[dict(t='', wet_km2=0) for _ in range(49)], rain_total_max_mm=float(rain.max()), rain_total_mean_mm=float(rain.mean()), infiltration=dict(wet_start_mm=0.0),
                        physics=dict(version=2, antecedent_mm=[20.0, 55.0, 90.0][s % 3]), cell_outputs=dict(hmax='peak depth m (float16)', t_first='frame index when depth first >= 10 cm (255 = never)', dur='number of frames >= 10 cm'))
            json.dump(meta, open(f'{rdir}/meta.json', 'w')); runs.append(rdir)
    return runs

def selftest():
    import pandas as pd
    root = tempfile.mkdtemp(prefix='mfw_ds_'); log('selftest in', root); runs = make_synthetic(root)
    args = parse([*sum((['--runs', r] for r in runs), []), '--soils', f'{root}/data/soils30/soils30.npz', '--channels', f'{root}/data/channels30/channels30.npz', '--huc10', f'{root}/data/huc10_30/huc10_30.npz',
                  '--nlcd10', f'{root}/data/nlcd10', '--out', f'{root}/ds', '--cache', f'{root}/cache', '--tile', '64', '--rows-per-shard', '20000', '--dry-ratio', '1.0'])
    args.runs = runs; man = build(args); df, _ = load_dataset(args.out)
    assert man['rows'] == len(df) > 0, 'no rows'
    assert set(STATIC_FEATURES + STORM_FEATURES + TARGETS + ['run', 'storm', 'huc10', 'fold', 'split', 'weight']) <= set(df.columns), 'missing columns'
    assert df['storm'].nunique() == 3 and df['run'].nunique() == 6, 'storm / run ids'
    assert (df.groupby('storm')['run'].nunique() == 2).all(), 'variants must share the storm id'
    assert df['fold'].between(0, args.folds - 1).all() and df['fold'].nunique() >= 3, 'spatial folds'
    for r in man['runs']: assert r['wet'] == r['wet_cells_total'], 'every wet cell must be kept'
    assert ((df['hmax'] >= WET_M) == (df['wet'] == 1)).all() and df.loc[df.wet == 1, 't_first_h'].notna().all() and df.loc[df.wet == 0, 't_first_h'].isna().all(), 'targets'
    assert (df.loc[df.wet == 1, 'weight'] == 1).all() and (df.loc[df.wet == 0, 'weight'] >= 1).all(), 'weights'
    assert df['rain_grid'].eq(1).all() and df['rain_1h_mm'].le(df['rain_3h_mm'] + 1e-4).all() and df['rain_24h_mm'].le(df['rain_total_mm'] + 1e-3).all(), 'rain windows'
    assert df['imp'].notna().mean() > 0.3 and df['imp'].isna().mean() > 0.05, 'nlcd10 tile assembly (west covered, east NaN)'
    assert df['hand'].notna().all() and df['uparea_km2'].gt(0).all() and df['chan_area_km2'].notna().mean() > 0.5, 'routing features'
    # the fake depths fall with HAND: the surrogate signal must be in the table
    wet_rate = df.groupby(pd.cut(df['hand'], [-99, 1, 3, 10, 1e9]), observed=True)['wet'].mean().values; assert wet_rate[0] > wet_rate[-1], f'wet rate vs HAND {wet_rate}'
    log('selftest OK:', f"{len(df):,} rows, wet {df.wet.mean():.2f}, folds {sorted(df.fold.unique().tolist())}, shards {len(man['shards'])} ({man['format']}), columns {len(df.columns)}")
    return root

def parse(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--runs', nargs='+', default=None, help='run directories (local) or runs/<name> on HF with --hf')
    ap.add_argument('--soils', default=None); ap.add_argument('--channels', default=None); ap.add_argument('--huc10', default=None, help='HUC10 id raster (npz field huc10 + *_meta.json)')
    ap.add_argument('--imp', default=None, help='whole-state impervious grid (npz field imp)'); ap.add_argument('--nlcd10', default=None, help='dir of 10 m NLCD tiles + index.json')
    ap.add_argument('--out', default='ml_dataset'); ap.add_argument('--format', default='parquet', choices=['parquet', 'npz']); ap.add_argument('--rows-per-shard', type=int, default=2_000_000)
    ap.add_argument('--tile', type=int, default=1024); ap.add_argument('--dry-ratio', type=float, default=2.0, help='dry rows per wet row (per tile)'); ap.add_argument('--dry-min', type=int, default=50, help='dry rows from an all-dry tile')
    ap.add_argument('--folds', type=int, default=5); ap.add_argument('--seed', type=int, default=0); ap.add_argument('--storm', nargs='*', default=None, help='run=storm overrides, e.g. test_leominster=sep2023')
    ap.add_argument('--keep-water', action='store_true', help='keep river / lake / sea cells (dropped by default)')
    ap.add_argument('--hf', action='store_true', help='download missing inputs from Hugging Face'); ap.add_argument('--cache', default=os.path.join(tempfile.gettempdir(), 'mfw_ml_cache')); ap.add_argument('--no-cache', action='store_true')
    ap.add_argument('--upload', default=None, help='HF path (e.g. ml/datasets/v3_30m) to upload the shards to after the build')
    ap.add_argument('--selftest', action='store_true')
    return ap.parse_args(argv)

if __name__ == '__main__':
    a = parse()
    if a.selftest: selftest(); sys.exit(0)
    if a.runs is None and os.environ.get('ML_RUNS'):          # queue step: everything from the job env (worker.py passes the job's env)
        E = os.environ; a.runs = E['ML_RUNS'].split(','); a.hf = True; a.out = E.get('ML_LOCAL', f"{E.get('WORK', '/content')}/ml_dataset"); a.upload = E.get('ML_OUT')
        a.soils = E.get('SOILS_GRID', 'data/soils30/soils30.npz'); a.channels = E.get('CHANNELS_GRID', 'data/channels30/channels30.npz'); a.huc10 = E.get('HUC10') or None; a.nlcd10 = E.get('NLCD10', 'data/nlcd10')
        a.dry_ratio = float(E.get('DRY_RATIO', a.dry_ratio)); a.folds = int(E.get('FOLDS', a.folds)); a.storm = E['STORM_OF'].split(',') if E.get('STORM_OF') else None
    if not a.runs: sys.exit('no runs given (--runs ... or ML_RUNS=...)')
    build(a)
