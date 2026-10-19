"""Flood-depth maps for Massachusetts storms from NOAA National Water Model flows + NOAA OWP HAND (the FIM4 method of
github.com/NOAA-OWP/inundation-mapping), using OWP's PUBLISHED precomputed HAND outputs - no HAND rebuild, no hydraulics.

    python sim/fim_maps.py --selftest                         offline check (synthetic rasters + hydroTable), no network
    python sim/fim_maps.py                                     jul2023, western MA HUC8s first, then eastern
    python sim/fim_maps.py --storms jul2023,dec2023 --hucs 01080203,01080206
    python sim/fim_maps.py --hucs west --branch0-only          fastest smoke run (only the full-HUC branch 0)

Method (as OWP inundate / inundate_mosaic_wrapper)
  1. NWM peak flow per feature_id (= NHDPlus v2 COMID) over each storm window: max of the hourly analysis_assim
     channel_rt tm00 snapshots (same files/URLs as sim/nwm_compare.py; analysis_assim = NOAA's best estimate of what happened).
  2. Per HUC8, per branch (branch 0 = all streams, other branches = level paths): hydroTable_<b>.csv maps HydroID <->
     feature_id and gives the synthetic rating curve stage(m) vs discharge_cms.  Lake catchments (LakeID != -999) are dropped.
     stage per HydroID = np.interp(Q_peak, discharge_cms, stage) (clamped to the table ends; Q <= 0 -> no water).
  3. depth = stage[HydroID of the cell] - HAND(cell), inside that HydroID's catchment
     (gw_catchments_reaches_filtered_addedAttributes_<b>.tif holds HydroID, rem_zeroed_masked_<b>.tif holds HAND in m); depth >= 0.
  4. Branch depths -> HUC8 depth by max; HUC8 depths -> storm mosaic by max.  int16 centimetres, EPSG:5070, 10 m, DEFLATE.
HAND source (found by listing, version picked automatically): s3://ciroh-owp-hand-fim/hand_fim_<ver>/<HUC8>/branches/<b>/
  (CIROH mirror of OWP HAND, anonymous, the source used by CIROH's FIMserv), then s3://noaa-nws-owp-fim/hand_fim/ (ESIP, may
  need credentials), then NFIE/CFIM HAND by HUC6 (web.corral.tacc.utexas.edu/nfiedata, older HAND, COMID catchments).
Outputs: out/fim/fim_<storm>/depth.tif, summary.json, huc/<HUC8>.tif, validate/{meta.json,hmax.npy,validation.json}
  (EPSG:26986 30 m max-resampled copy scored by sim/validate.py).  Uploaded to HF runs/fim_<storm>/ when HF_TOKEN is set.
Disk stays bounded: one branch's inputs on disk at a time, deleted after use.
"""
import os, re, sys, json, time, math, shutil, argparse, tempfile, datetime as dt
from concurrent.futures import ThreadPoolExecutor
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nwm_compare import NWM, STORMS, HF_REPO, hours, get, log      # reuse the NWM downloader / URLs / storm windows

PRODUCT = 'analysis_assim'
# HUC8s intersecting Massachusetts (WBD names).  'west' = Connecticut / Housatonic / Hudson basins, run first.
HUCS = {'west': {'01080203': 'Deerfield', '01080206': 'Westfield', '01080202': 'Millers', '01080204': 'Chicopee',
                 '01080201': 'Middle Connecticut', '01080205': 'Lower Connecticut', '01100005': 'Housatonic',
                 '02020003': 'Hudson-Hoosic', '01080207': 'Farmington', '02020006': 'Middle Hudson'},
        'east': {'01070004': 'Nashua', '01070005': 'Concord (Sudbury-Assabet-Concord)', '01070006': 'Merrimack',
                 '01090001': 'Charles (Boston Harbor, Mystic, Neponset, North Shore)', '01090003': 'Blackstone',
                 '01090004': 'Narragansett (Taunton)', '01090002': 'Cape Cod', '01100001': 'Quinebaug'}}
HUC_NAMES = {**HUCS['west'], **HUCS['east']}
OWP_SOURCES = [('ciroh-owp-hand-fim', ''), ('noaa-nws-owp-fim', 'hand_fim/')]
NFIE_BASE = 'https://web.corral.tacc.utexas.edu/nfiedata/HAND/{huc6}/'
MA_LONLAT = (-73.52, 41.22, -69.90, 42.90)
GT = dict(driver='GTiff', dtype='int16', count=1, compress='deflate', predictor=2, tiled=True, blockxsize=512, blockysize=512, BIGTIFF='IF_SAFER')


# =============================================================================================== core (pure numpy / pandas)
def load_hydrotable(src, branch=None):
    """hydroTable csv (path or DataFrame) -> DataFrame[HydroID, feature_id, stage, discharge_cms], non-lake rows only."""
    import pandas as pd
    df = src if isinstance(src, pd.DataFrame) else pd.read_csv(src, low_memory=False)
    if branch is not None and 'branch_id' in df.columns: df = df[df['branch_id'].astype(str) == str(branch)]
    if 'LakeID' in df.columns: df = df[pd.to_numeric(df['LakeID'], errors='coerce').fillna(-999) == -999]
    q = 'discharge_cms' if 'discharge_cms' in df.columns else 'default_discharge_cms'
    out = pd.DataFrame({'HydroID': pd.to_numeric(df['HydroID'], errors='coerce'), 'feature_id': pd.to_numeric(df['feature_id'], errors='coerce'),
                        'stage': pd.to_numeric(df['stage'], errors='coerce'), 'discharge_cms': pd.to_numeric(df[q], errors='coerce')}).dropna()
    return out.astype({'HydroID': np.int64, 'feature_id': np.int64})

class Flows:
    """Peak flow lookup: sorted feature_id array + values (m3/s)."""
    def __init__(self, fid, q):
        o = np.argsort(fid); self.fid = np.asarray(fid, np.int64)[o]; self.q = np.asarray(q, np.float64)[o]
    def __call__(self, ids):
        ids = np.asarray(ids, np.int64); i = np.clip(np.searchsorted(self.fid, ids), 0, max(len(self.fid) - 1, 0))
        ok = (len(self.fid) > 0) & (self.fid[i] == ids) if len(self.fid) else np.zeros(len(ids), bool)
        return np.where(ok, self.q[i] if len(self.fid) else np.nan, np.nan)

def stages_for(ht, flows):
    """-> (sorted HydroID array, stage array m).  Interpolates each HydroID's rating curve at its feature_id's peak flow.
    HydroIDs without a finite positive flow are left out (no water), as OWP drops features missing from the forecast."""
    ht = ht.assign(Q=flows(ht['feature_id'].values))
    ht = ht[np.isfinite(ht['Q']) & (ht['Q'] > 0)].sort_values(['HydroID', 'stage'])
    if ht.empty: return np.zeros(0, np.int64), np.zeros(0, np.float32)
    hid = ht['HydroID'].values; s = ht['stage'].values; d = ht['discharge_cms'].values; Q = ht['Q'].values
    cut = np.flatnonzero(np.diff(hid)) + 1; starts = np.r_[0, cut]; ends = np.r_[cut, len(hid)]
    ids, st = np.empty(len(starts), np.int64), np.empty(len(starts), np.float32)
    for k, (a, b) in enumerate(zip(starts, ends)):
        dd = np.maximum.accumulate(d[a:b])          # guard against a non-monotonic table (np.interp needs increasing x)
        ids[k] = hid[a]; st[k] = np.interp(Q[a], dd, s[a:b])
    return ids, st

def depth_block(rem, cat, ids, st, rem_nodata=None, cat_nodata=None):
    """HAND block + catchment (HydroID) block -> depth (m, float32, >= 0)."""
    rem = rem.astype(np.float32); cat = cat.astype(np.int64)
    bad = ~np.isfinite(rem) | (cat <= 0)
    if rem_nodata is not None: bad |= rem == np.float32(rem_nodata)
    if cat_nodata is not None: bad |= cat == int(cat_nodata)
    if len(ids) == 0: return np.zeros(rem.shape, np.float32)
    i = np.clip(np.searchsorted(ids, cat), 0, len(ids) - 1); hit = (ids[i] == cat) & ~bad
    d = np.where(hit, st[i] - rem, 0).astype(np.float32)
    return np.where(d > 0, d, 0).astype(np.float32)

def to_cm(d):
    return np.clip(np.rint(d * 100), 0, 32767).astype(np.int16)

def cell_area_km2(transform, crs, row0, nrows):
    """Per-row cell area (km2): constant for projected CRS, latitude-dependent for geographic (NFIE fallback)."""
    if crs is not None and crs.is_geographic:
        lat = transform.f + transform.e * (np.arange(row0, row0 + nrows) + 0.5)
        return np.abs(transform.a * transform.e) * 111.32 * 110.57 * np.cos(np.radians(lat))
    return np.full(nrows, abs(transform.a * transform.e) / 1e6)

def flooded_km2(path, min_cm=1):
    import rasterio
    tot = 0.0; mx = 0
    with rasterio.open(path) as s:
        for _, w in s.block_windows(1):
            a = s.read(1, window=w); ar = cell_area_km2(s.transform, s.crs, w.row_off, w.height)
            tot += float(((a >= min_cm).sum(axis=1) * ar).sum()); mx = max(mx, int(a.max()) if a.size else 0)
    return round(tot, 3), round(mx / 100, 2)


# =============================================================================================== rasters
def branch_depths(rem_path, cat_path, stage_sets, out_paths, rows=1024):
    """One branch: write a depth tif (int16 cm) per storm. stage_sets: [(ids, st)], out_paths: same order."""
    import rasterio
    from rasterio.vrt import WarpedVRT
    from rasterio.enums import Resampling
    with rasterio.open(rem_path) as R, rasterio.open(cat_path) as C0:
        same = (C0.shape == R.shape and C0.transform.almost_equals(R.transform) and C0.crs == R.crs)
        C = C0 if same else WarpedVRT(C0, crs=R.crs, transform=R.transform, width=R.width, height=R.height, resampling=Resampling.nearest)
        prof = dict(GT, crs=R.crs, transform=R.transform, width=R.width, height=R.height)
        if R.width < 512 or R.height < 512: prof.update(tiled=False); prof.pop('blockxsize'); prof.pop('blockysize')
        outs = [rasterio.open(p, 'w', **prof) for p in out_paths]
        try:
            for r0 in range(0, R.height, rows):
                w = rasterio.windows.Window(0, r0, R.width, min(rows, R.height - r0))
                rem = R.read(1, window=w); cat = C.read(1, window=w)
                for (ids, st), o in zip(stage_sets, outs): o.write(to_cm(depth_block(rem, cat, ids, st, R.nodata, C0.nodata)), 1, window=w)
        finally:
            for o in outs: o.close()
            if not same: C.close()

def merge_max(paths, out_path):
    """Max-mosaic of int16 depth tifs (branches -> HUC8)."""
    import rasterio
    from rasterio.merge import merge
    srcs = [rasterio.open(p) for p in paths]
    try:
        arr, tr = merge(srcs, method='max', nodata=0, dtype='int16')
        prof = dict(GT, crs=srcs[0].crs, transform=tr, width=arr.shape[2], height=arr.shape[1])
        if arr.shape[1] < 512 or arr.shape[2] < 512: prof.update(tiled=False); prof.pop('blockxsize'); prof.pop('blockysize')
        with rasterio.open(out_path, 'w', **prof) as o:
            o.write(arr[0], 1); o.scales = (0.01,); o.units = ('m',); o.update_tags(units='int16 centimetres of water depth; 0 = dry')
    finally:
        for s in srcs: s.close()

def mosaic_blocks(paths, out_path, block=4096, overviews=True):
    """Statewide max-mosaic built block by block so memory stays small even at 10 m."""
    import rasterio
    from rasterio.merge import merge
    from rasterio.enums import Resampling
    from rasterio.transform import from_origin
    srcs = [rasterio.open(p) for p in paths]
    try:
        res = srcs[0].res[0]; L = min(s.bounds.left for s in srcs); B = min(s.bounds.bottom for s in srcs)
        Rr = max(s.bounds.right for s in srcs); T = max(s.bounds.top for s in srcs)
        W, H = int(math.ceil((Rr - L) / res)), int(math.ceil((T - B) / res)); tr = from_origin(L, T, res, res)
        prof = dict(GT, crs=srcs[0].crs, transform=tr, width=W, height=H)
        if W < 512 or H < 512: prof.update(tiled=False); prof.pop('blockxsize'); prof.pop('blockysize')
        with rasterio.open(out_path, 'w', **prof) as o:
            for r0 in range(0, H, block):
                for c0 in range(0, W, block):
                    w = rasterio.windows.Window(c0, r0, min(block, W - c0), min(block, H - r0)); bb = rasterio.windows.bounds(w, tr)
                    use = [s for s in srcs if s.bounds.left < bb[2] and s.bounds.right > bb[0] and s.bounds.bottom < bb[3] and s.bounds.top > bb[1]]
                    out = np.zeros((w.height, w.width), np.int16)
                    if use:
                        a, _ = merge(use, bounds=bb, res=res, method='max', nodata=0, dtype='int16')
                        h_, w_ = min(a.shape[1], w.height), min(a.shape[2], w.width); out[:h_, :w_] = a[0, :h_, :w_]
                    o.write(out, 1, window=w)
            o.scales = (0.01,); o.units = ('m',); o.update_tags(units='int16 centimetres of water depth; 0 = dry')
        if overviews and min(W, H) > 2048:
            with rasterio.open(out_path, 'r+') as o: o.build_overviews([4, 16, 64], Resampling.nearest)
    finally:
        for s in srcs: s.close()

def validate_export(depth_tif, run_dir, storm, res=30.0, lonlat=MA_LONLAT):
    """Max-resampled copy on the EPSG:26986 grid sim/validate.py reads (meta.json + hmax.npy in metres)."""
    import rasterio
    from rasterio.vrt import WarpedVRT
    from rasterio.enums import Resampling
    from rasterio.transform import from_origin
    from rasterio.warp import transform_bounds
    os.makedirs(run_dir, exist_ok=True)
    x0, y0, x1, y1 = transform_bounds('EPSG:4326', 'EPSG:26986', *lonlat)
    x0, y0, x1, y1 = math.floor(x0 / res) * res, math.floor(y0 / res) * res, math.ceil(x1 / res) * res, math.ceil(y1 / res) * res
    W, H = int(round((x1 - x0) / res)), int(round((y1 - y0) / res))
    with rasterio.open(depth_tif) as s, WarpedVRT(s, crs='EPSG:26986', transform=from_origin(x0, y1, res, res), width=W, height=H,
                                                   resampling=Resampling.max, src_nodata=None, nodata=0) as v:
        hm = v.read(1).astype(np.float32) / 100.0
    np.save(os.path.join(run_dir, 'hmax.npy'), hm)
    a, b = STORMS[storm]; n = len(hours(a, b))
    meta = dict(run=f'fim_{storm}', box=[x0, y0, x1, y1], res_m=res, t0=a + ':00', frame_min=60, frames=list(range(n)),
                crs='EPSG:26986', source='NOAA OWP HAND-FIM (FIM4 method) driven by NWM analysis_assim peak flows; resampled by max from 10 m')
    json.dump(meta, open(os.path.join(run_dir, 'meta.json'), 'w'), indent=1)
    return hm.shape


# =============================================================================================== HAND sources
def s3_client(bucket):
    import boto3, requests
    from botocore import UNSIGNED
    from botocore.config import Config
    region = 'us-east-1'
    try: region = requests.head(f'https://{bucket}.s3.amazonaws.com', timeout=30).headers.get('x-amz-bucket-region', region)
    except Exception: pass
    return boto3.client('s3', region_name=region, config=Config(signature_version=UNSIGNED, retries={'max_attempts': 8, 'mode': 'adaptive'}))

def s3_list(cli, bucket, prefix, delimiter=None):
    keys, pre, kw = [], [], dict(Bucket=bucket, Prefix=prefix)
    if delimiter: kw['Delimiter'] = delimiter
    for page in cli.get_paginator('list_objects_v2').paginate(**kw):
        keys += [(o['Key'], o['Size']) for o in page.get('Contents', [])]; pre += [p['Prefix'] for p in page.get('CommonPrefixes', [])]
    return keys, pre

def pick_version(prefixes):
    """['hand_fim_4_8_7_2/', 'hand_fim_4_9_9_0/', ...] -> newest by numeric tuple."""
    best = None
    for p in prefixes:
        m = re.search(r'(?:hand_fim|fim|hand)_(\d+(?:_\d+)+)/?$', p.rstrip('/') + '/') or re.search(r'(\d+(?:_\d+)+)/?$', p)
        if m:
            v = tuple(int(x) for x in m.group(1).split('_'))
            if best is None or v > best[0]: best = (v, p)
    return None if best is None else best[1]

def branch_files(keys, huc):
    """S3 keys under <ver>/<huc>/ -> {branch: {rem, cat, ht}} (ht may be the HUC-level hydrotable.csv)."""
    found, huc_ht = {}, None
    for k in keys:
        if re.search(rf'/{huc}/hydrotable\.csv$', k, re.I): huc_ht = k
        m = re.search(rf'/{huc}/branches/([^/]+)/([^/]+)$', k)
        if not m: continue
        b, f = m.groups(); d = found.setdefault(b, {})
        if f == f'rem_zeroed_masked_{b}.tif': d['rem'] = k
        elif f == f'gw_catchments_reaches_filtered_addedAttributes_{b}.tif': d['cat'] = k
        elif f == f'hydroTable_{b}.csv': d['ht'] = k
    out = {}
    for b, d in found.items():
        if 'ht' not in d and huc_ht: d['ht'] = huc_ht; d['ht_branch'] = b
        if {'rem', 'cat', 'ht'} <= set(d): out[b] = d
    return dict(sorted(out.items(), key=lambda kv: (kv[0] != '0', int(kv[0]) if kv[0].isdigit() else 0, kv[0])))

class OWPSource:
    def __init__(self, version=None, bucket=None):
        self.cli = self.bucket = self.root = None; tried = []
        for b, base in OWP_SOURCES:
            if bucket and b != bucket: continue
            try:
                cli = s3_client(b); _, pre = s3_list(cli, b, base, '/')
                cand = [p for p in pre if re.search(r'\d+_\d+', p)]
                v = (base + version.strip('/') + '/') if version else pick_version(cand)
                tried.append(f's3://{b}/{base}: {len(pre)} prefixes, picked {v}')
                if v: self.cli, self.bucket, self.root = cli, b, v; break
            except Exception as e: tried.append(f's3://{b}/{base}: {repr(e)[:160]}')
        self.tried = tried
        for t in tried: log('  HAND source', t)
    @property
    def ok(self): return self.cli is not None
    def units(self, huc):
        keys, _ = s3_list(self.cli, self.bucket, f'{self.root}{huc}/branches/')
        top, _ = s3_list(self.cli, self.bucket, f'{self.root}{huc}/', '/')
        files = branch_files([k for k, _ in keys] + [k for k, _ in top], huc)
        size = {k: s for k, s in keys}
        return [dict(id=b, size=sum(size.get(d[x], 0) for x in ('rem', 'cat')), **d) for b, d in files.items()]
    def fetch(self, key, path):
        self.cli.download_file(self.bucket, key, path); return path
    def url(self, key): return f's3://{self.bucket}/{key}'

class NFIESource:
    """Fallback: NFIE/CFIM HAND by HUC6.  Catchment raster values are COMIDs (= NWM feature_id), so HydroID == feature_id."""
    def __init__(self): self.ok = True; self.tried = [NFIE_BASE]
    def units(self, huc):
        import requests
        u = NFIE_BASE.format(huc6=huc[:6]); r = requests.get(u, timeout=120); r.raise_for_status()
        names = sorted(set(re.findall(r'href="([^"?/]+)"', r.text)))
        pick = lambda pat: next((u + n for n in names if re.search(pat, n, re.I)), None)
        d = dict(id=f'huc6_{huc[:6]}', rem=pick(r'\d{6}hand\.tif$'), cat=pick(r'catchmask\.tif$'), ht=pick(r'hydroprop-fulltable.*\.csv$'), nfie=True)
        return [d] if d['rem'] and d['cat'] and d['ht'] else []
    def fetch(self, url, path):
        import requests
        with requests.get(url, stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(path, 'wb') as f: shutil.copyfileobj(r.raw, f, 1 << 22)
        return path
    def url(self, key): return key

def nfie_hydrotable(path):
    import pandas as pd
    df = pd.read_csv(path, low_memory=False); cols = {c.lower(): c for c in df.columns}
    q = next(c for c in df.columns if c.lower().startswith('discharge'))
    return pd.DataFrame({'HydroID': df[cols['catchid']], 'feature_id': df[cols['catchid']], 'stage': df[cols['stage']], 'discharge_cms': df[q]}).dropna().astype({'HydroID': np.int64, 'feature_id': np.int64})


# =============================================================================================== NWM peaks
import threading
_H5_LOCK = threading.Lock()
def read_full(blob):
    """NWM channel_rt (netCDF4 = HDF5) bytes -> (feature_id, streamflow m3/s).  h5py, one file at a time: netCDF4 in worker
    threads next to rasterio's GDAL segfaulted on the runner."""
    import h5py, io
    with _H5_LOCK, h5py.File(io.BytesIO(blob), 'r') as f:
        fid = f['feature_id'][:].astype(np.int64); v = f['streamflow']; raw = v[:]
        sf = float(np.ravel(v.attrs.get('scale_factor', [1.0]))[0]); off = float(np.ravel(v.attrs.get('add_offset', [0.0]))[0])
        fill = v.attrs.get('_FillValue', None); miss = v.attrs.get('missing_value', None)
    q = raw.astype(np.float32).ravel() * sf + off
    for bad in (fill, miss):
        if bad is not None: q[raw.ravel() == np.ravel(bad)[0]] = np.nan
    q[q < 0] = np.nan
    return fid, q

def peak_accumulate(acc, fid, q):
    """acc = (fid, peak) or None; nan-aware running max, realigning if the feature order ever differs."""
    if acc is None: return fid, q.copy()
    f0, p0 = acc
    if len(fid) == len(f0) and np.array_equal(fid, f0): return f0, np.fmax(p0, q)
    o = np.argsort(f0); i = np.clip(np.searchsorted(f0[o], fid), 0, len(f0) - 1); hit = f0[o][i] == fid
    p = p0.copy(); j = o[i[hit]]; p[j] = np.fmax(p[j], q[hit]); return f0, p

def fetch_full(hour):
    ymd, hh = hour[:10].replace('-', ''), hour[11:13]
    for u in NWM:
        r = get(u.format(ymd=ymd, hh=hh, prod=PRODUCT), tries=3, timeout=180, ok404=True)
        if r is None: continue
        try: out = read_full(r.content); del r; return hour, out, u.split('/nwm.')[0]
        except Exception as e: log('  read fail', hour, repr(e)[:100])
    return hour, None, None

def storm_peaks(storm, out_dir, workers=8):
    cache = os.path.join(out_dir, f'nwm_peak_{storm}.npz')
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=False); return Flows(z['fid'], z['q']), json.loads(str(z['info']))
    win = hours(*STORMS[storm]); acc = None; missing = []; srcs = set()
    with ThreadPoolExecutor(workers) as ex:
        for hour, fq, src in ex.map(fetch_full, win):
            if fq is None: missing.append(hour); continue
            acc = peak_accumulate(acc, *fq); srcs.add(src)
    if acc is None: raise RuntimeError(f'{storm}: no NWM {PRODUCT} files found')
    info = dict(product=PRODUCT, window=STORMS[storm], hours=len(win), missing=missing, source=sorted(srcs), n_features=int(len(acc[0])))
    log(storm, f'NWM peaks: {len(win) - len(missing)}/{len(win)} hourly files', sorted(srcs))
    np.savez_compressed(cache, fid=acc[0], q=acc[1].astype(np.float32), info=json.dumps(info))
    return Flows(*acc), info


# =============================================================================================== run
def upload(local, remote):
    if not os.environ.get('HF_TOKEN'): return False
    try:
        from huggingface_hub import HfApi
        HfApi(token=os.environ['HF_TOKEN']).upload_file(path_or_fileobj=local, path_in_repo=remote, repo_id=HF_REPO, repo_type='dataset')
        log('  uploaded', remote); return True
    except Exception as e: log('  upload failed', remote, repr(e)[:200]); return False

def process_huc(src, huc, storms, flows, out_dir, work, branch0_only=False, min_cm=1):
    units = src.units(huc)
    if branch0_only: units = [u for u in units if u['id'] in ('0',) or u.get('nfie')]
    st = dict(name=HUC_NAMES.get(huc, ''), n_branches=len(units))
    if not units: log(huc, 'no HAND branches found'); return {s: dict(st, error='no HAND data found') for s in storms}
    log(huc, HUC_NAMES.get(huc, ''), f'{len(units)} branches, {sum(u["size"] for u in units if "size" in u) / 1e9:.2f} GB rasters')
    bdir = {s: os.path.join(work, f'{huc}_{s}') for s in storms}
    for d in bdir.values(): os.makedirs(d, exist_ok=True)
    info = {s: dict(st, hydroids_wet=0, hydroids=0, features_no_flow=0, branches_done=0, branches_failed=[]) for s in storms}
    t0 = time.time()
    for k, u in enumerate(units):
        tmp = os.path.join(work, 'in'); os.makedirs(tmp, exist_ok=True)
        try:
            rem = src.fetch(u['rem'], os.path.join(tmp, 'rem.tif')); cat = src.fetch(u['cat'], os.path.join(tmp, 'cat.tif'))
            htp = src.fetch(u['ht'], os.path.join(tmp, 'ht.csv'))
            ht = nfie_hydrotable(htp) if u.get('nfie') else load_hydrotable(htp, u.get('ht_branch'))
            sets = []
            for s in storms:
                ids, stg = stages_for(ht, flows[s]); sets.append((ids, stg))
                fq = flows[s](ht['feature_id'].unique())
                info[s]['hydroids'] += int(ht['HydroID'].nunique()); info[s]['hydroids_wet'] += int((stg > 0).sum()); info[s]['features_no_flow'] += int((~np.isfinite(fq)).sum())
            branch_depths(rem, cat, sets, [os.path.join(bdir[s], f'b_{u["id"]}.tif') for s in storms])
            for s in storms: info[s]['branches_done'] += 1
        except Exception as e:
            log('  branch fail', huc, u['id'], repr(e)[:200])
            for s in storms: info[s]['branches_failed'].append(u['id'])
        finally: shutil.rmtree(tmp, ignore_errors=True)
        if k % 25 == 0 or k == len(units) - 1: log(f'  {huc} branch {k + 1}/{len(units)} ({u["id"]}) {time.time() - t0:.0f}s')
    for s in storms:
        os.makedirs(os.path.join(out_dir, f'fim_{s}', 'huc'), exist_ok=True)
        bt = sorted(os.path.join(bdir[s], f) for f in os.listdir(bdir[s]))
        if bt:
            hp = os.path.join(out_dir, f'fim_{s}', 'huc', f'{huc}.tif'); merge_max(bt, hp)
            info[s]['flooded_km2'], info[s]['max_depth_m'] = flooded_km2(hp, min_cm)
            upload(hp, f'runs/fim_{s}/huc/{huc}.tif')
        shutil.rmtree(bdir[s], ignore_errors=True)
        log(f'  {huc} {s}: flooded {info[s].get("flooded_km2")} km2, max {info[s].get("max_depth_m")} m, {info[s]["hydroids_wet"]} wet HydroIDs')
    return info

def finish_storm(storm, out_dir, summary, src, peak_info, partial, do_validate=True, vres=30.0):
    sd = os.path.join(out_dir, f'fim_{storm}'); hd = os.path.join(sd, 'huc')
    tifs = sorted(os.path.join(hd, f) for f in os.listdir(hd) if f.endswith('.tif')) if os.path.isdir(hd) else []
    res = dict(storm=storm, window_utc=STORMS[storm], generated=dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), partial=partial,
               method='NOAA OWP HAND-FIM (FIM4, inundation-mapping) method: NWM peak flow -> synthetic rating curve stage per HydroID -> depth = stage - HAND in catchment; branches and HUC8s mosaicked by max',
               hand_source=getattr(src, 'tried', None), hand_root=(f's3://{src.bucket}/{src.root}' if getattr(src, 'bucket', None) else 'NFIE'),
               nwm=peak_info, units='depth.tif int16 cm (scale 0.01 -> m), EPSG:5070 10 m; 0 = dry',
               note='flooded_km2 counts depth >= 1 cm over the whole HUC8 (including NH/CT/RI/NY/VT parts) and includes the normal river channel itself',
               hucs=summary, total_flooded_km2=round(sum(v.get('flooded_km2') or 0 for v in summary.values()), 2))
    if tifs:
        mp = os.path.join(sd, 'depth.tif'); mosaic_blocks(tifs, mp); log(storm, 'mosaic', mp, f'{os.path.getsize(mp) / 1e6:.1f} MB')
        if do_validate:
            try:
                vd = os.path.join(sd, 'validate'); validate_export(mp, vd, storm, vres)
                import validate as V
                base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
                v = V.main(vd, hwm_path=os.path.join(base, 'docs', 'validation', 'stn_ma.json'), reports_path=os.path.join(base, 'docs', 'prone', 'flood_reports.json'))
                res['validation'] = {k: ({kk: vv for kk, vv in x.items() if kk not in ('rows', 'by_reach')} if isinstance(x, dict) else x) for k, x in v.items()}
            except Exception as e: res['validation_error'] = repr(e)[:300]; log('  validate failed', repr(e)[:200])
        upload(mp, f'runs/fim_{storm}/depth.tif')
        if os.path.exists(os.path.join(sd, 'validate', 'validation.json')): upload(os.path.join(sd, 'validate', 'validation.json'), f'runs/fim_{storm}/validation.json')
    json.dump(res, open(os.path.join(sd, 'summary.json'), 'w'), indent=1, default=str)
    upload(os.path.join(sd, 'summary.json'), f'runs/fim_{storm}/summary.json')

def parse_hucs(s):
    out = []
    for t in s.split(','):
        t = t.strip()
        if not t: continue
        if t == 'all': t = 'west,east'
        for x in t.split(','):
            out += list(HUCS[x]) if x in HUCS else [x]
    return list(dict.fromkeys(out))

def run(a):
    storms = [s.strip() for s in a.storms.split(',') if s.strip()]; hucs = parse_hucs(a.hucs)
    for s in storms: assert s in STORMS, f'unknown storm {s}'
    os.makedirs(a.out, exist_ok=True); work = tempfile.mkdtemp(prefix='fim_', dir=a.work or None)
    log('storms', storms, 'hucs', hucs)
    src = OWPSource(a.hand_version, a.bucket) if a.source in ('auto', 'owp') else None
    if src is None or not src.ok:
        if a.source == 'owp': raise SystemExit('OWP HAND not reachable anonymously: ' + '; '.join(src.tried))
        log('OWP HAND not reachable -> NFIE/CFIM HUC6 fallback'); src = NFIESource()
    flows, pinfo = {}, {}
    for s in storms: flows[s], pinfo[s] = storm_peaks(s, a.out, a.workers)
    summ = {s: {} for s in storms}
    west = [h for h in hucs if h in HUCS['west']]; done_nfie = set()
    for i, h in enumerate(hucs):
        if isinstance(src, NFIESource):
            if h[:6] in done_nfie: continue
            done_nfie.add(h[:6])
        try: info = process_huc(src, h, storms, flows, a.out, work, a.branch0_only, a.min_depth_cm)
        except Exception as e: log('HUC fail', h, repr(e)[:200]); info = {s: dict(name=HUC_NAMES.get(h, ''), error=repr(e)[:200]) for s in storms}
        for s in storms: summ[s][h] = info[s]
        if west and h == west[-1] and i < len(hucs) - 1:      # fast win: publish the western mosaic before starting the east
            for s in storms: finish_storm(s, a.out, summ[s], src, pinfo[s], partial=True, do_validate=not a.no_validate, vres=a.validate_res)
    for s in storms: finish_storm(s, a.out, summ[s], src, pinfo[s], partial=False, do_validate=not a.no_validate, vres=a.validate_res)
    shutil.rmtree(work, ignore_errors=True); log('done')


# =============================================================================================== selftest
def selftest():
    import pandas as pd, rasterio
    from rasterio.transform import from_origin
    ok = True
    def check(name, cond):
        nonlocal ok; ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name)
    tmp = tempfile.mkdtemp(prefix='fim_selftest_')
    try:
        # rating curves: HydroID 11 (feature 500) Q = 10 s^2, s = 0..5 m; HydroID 12 (feature 500) Q = 20 s; HydroID 13 lake; 14 no flow
        rows = []
        for s in np.arange(0, 5.01, 0.5):
            rows += [dict(HydroID=11, feature_id=500, stage=s, discharge_cms=10 * s * s, LakeID=-999),
                     dict(HydroID=12, feature_id=500, stage=s, discharge_cms=20 * s, LakeID=-999),
                     dict(HydroID=13, feature_id=600, stage=s, discharge_cms=5 * s, LakeID=77),
                     dict(HydroID=14, feature_id=700, stage=s, discharge_cms=5 * s, LakeID=-999),
                     dict(HydroID=21, feature_id=800, stage=s, discharge_cms=4 * s, LakeID=-999)]
        ht = load_hydrotable(pd.DataFrame(rows)); check('lake rows dropped', 13 not in set(ht['HydroID']))
        fl = Flows([800, 500, 600, 999], [8.0, 40.0, 10.0, 1.0])
        ids, st = stages_for(ht, fl); m = dict(zip(ids.tolist(), st.tolist()))
        # Q=40 on HydroID 11: table points (1.5,22.5),(2,40) -> exactly 2.0; HydroID 12: Q=40 -> 2.0; 21: Q=8 -> 2.0
        check(f'stage interp exact {m}', abs(m[11] - 2.0) < 1e-6 and abs(m[12] - 2.0) < 1e-6 and abs(m[21] - 2.0) < 1e-6 and 14 not in m and 13 not in m)
        ids2, st2 = stages_for(ht, Flows([500], [31.25])); m2 = dict(zip(ids2.tolist(), st2.tolist()))
        check(f'stage interp between table points {m2[11]:.4f} (linear 1.5->2.0: 1.75)', abs(m2[11] - (1.5 + 0.5 * (31.25 - 22.5) / (40 - 22.5))) < 1e-6)
        ids3, st3 = stages_for(ht, Flows([500], [1e6])); check('flow above table clamps to top stage', abs(dict(zip(ids3.tolist(), st3.tolist()))[11] - 5.0) < 1e-6)
        ids4, _ = stages_for(ht, Flows([500], [0.0])); check('zero flow -> no stage', len(ids4) == 0)
        # depth logic
        rem = np.array([[0.0, 0.5, 1.0, 3.0], [0.2, 1.9, 2.5, -9999], [0.0, 0.1, 0.4, 1.5]], np.float32)
        cat = np.array([[11, 11, 11, 11], [12, 12, 14, 12], [21, 0, 13, 21]], np.int32)
        d = depth_block(rem, cat, ids, st, rem_nodata=-9999, cat_nodata=0)
        exp = np.array([[2.0, 1.5, 1.0, 0.0], [1.8, 0.1, 0.0, 0.0], [2.0, 0.0, 0.0, 0.5]], np.float32)
        check(f'depth = stage - HAND in own catchment, >=0, nodata/lake/no-flow dry\n{d}', np.allclose(d, exp, atol=1e-6))
        check('cm rounding', to_cm(np.array([0.004, 0.005, 1.234, 400.0])).tolist() == [0, 0, 123, 32767] or to_cm(np.array([0.004, 0.006, 1.234, 400.0])).tolist() == [0, 1, 123, 32767])
        # two synthetic branches on offset grids (EPSG:5070, 10 m) through the real raster path
        crs = 'EPSG:5070'; x0, y0 = 1950000.0, 2350000.0
        def wr(p, a, x, y, dtype, nodata):
            with rasterio.open(p, 'w', driver='GTiff', width=a.shape[1], height=a.shape[0], count=1, dtype=dtype, crs=crs, transform=from_origin(x, y, 10, 10), nodata=nodata) as o: o.write(a.astype(dtype), 1)
        wr(f'{tmp}/rem0.tif', rem, x0, y0, 'float32', -9999); wr(f'{tmp}/cat0.tif', cat, x0, y0, 'int32', 0)
        rem1 = np.full((3, 4), 0.5, np.float32); cat1 = np.full((3, 4), 21, np.int32)
        wr(f'{tmp}/rem1.tif', rem1, x0 + 20, y0 - 10, 'float32', -9999); wr(f'{tmp}/cat1.tif', cat1, x0 + 20, y0 - 10, 'int32', 0)
        sets = [(ids, st), (ids2, st2)]
        branch_depths(f'{tmp}/rem0.tif', f'{tmp}/cat0.tif', sets, [f'{tmp}/b0_s1.tif', f'{tmp}/b0_s2.tif'], rows=2)
        branch_depths(f'{tmp}/rem1.tif', f'{tmp}/cat1.tif', sets, [f'{tmp}/b1_s1.tif', f'{tmp}/b1_s2.tif'])
        with rasterio.open(f'{tmp}/b0_s1.tif') as s: b0 = s.read(1)
        check('branch tif (row blocks) = depth_block in cm', np.array_equal(b0, to_cm(exp)))
        with rasterio.open(f'{tmp}/b0_s2.tif') as s: b02 = s.read(1)
        check('second storm written from the same inputs', b02[0, 0] == 175 and b02[2, 0] == 0)
        merge_max([f'{tmp}/b0_s1.tif', f'{tmp}/b1_s1.tif'], f'{tmp}/huc.tif')
        with rasterio.open(f'{tmp}/huc.tif') as s: h = s.read(1); sh = s.shape; sc = s.scales
        e = np.zeros((4, 6), np.int16); e[:3, :4] = to_cm(exp); e[1:4, 2:6] = np.maximum(e[1:4, 2:6], 150)
        check(f'branch mosaic by max on union grid {sh}\n{h}', sh == (4, 6) and np.array_equal(h, e) and abs(sc[0] - 0.01) < 1e-9)
        km2, mx = flooded_km2(f'{tmp}/huc.tif'); check(f'flooded km2 {km2} (cells {(e >= 1).sum()} x 100 m2), max {mx} m', abs(km2 - (e >= 1).sum() * 1e-4) < 1e-3 and mx == 2.0)
        # second "HUC" far away + blocked statewide mosaic vs one-shot merge
        wr(f'{tmp}/hucB.tif', np.full((5, 5), 33, np.int16), x0 + 30, y0 - 20, 'int16', None)
        mosaic_blocks([f'{tmp}/huc.tif', f'{tmp}/hucB.tif'], f'{tmp}/mos_blk.tif', block=3)
        mosaic_blocks([f'{tmp}/huc.tif', f'{tmp}/hucB.tif'], f'{tmp}/mos_one.tif', block=4096)
        with rasterio.open(f'{tmp}/mos_blk.tif') as s: A = s.read(1)
        with rasterio.open(f'{tmp}/mos_one.tif') as s: Bm = s.read(1)
        check(f'blocked mosaic == one-shot mosaic {A.shape}, max kept', np.array_equal(A, Bm) and A.shape == (7, 8) and A[0, 0] == 200 and A[2, 3] == 150 and A[6, 7] == 33)
        # NWM full-array reader + running peak
        try:
            import netCDF4
            blobs = []
            for qv in ([1.0, 5.0, 0.0, 2.0], [3.0, 4.0, 0.0, 9.0], [2.0, 6.0, 0.0, 1.0]):
                p = f'{tmp}/n.nc'
                with netCDF4.Dataset(p, 'w') as ds:
                    ds.createDimension('feature_id', 4); f = ds.createVariable('feature_id', 'i4', ('feature_id',)); f[:] = [101, 202, 303, 404]
                    q = ds.createVariable('streamflow', 'i4', ('feature_id',), fill_value=-999900); q.scale_factor = 0.01; q.add_offset = 0.0
                    q[:] = np.ma.masked_array(qv, mask=[False, False, True, False])
                blobs.append(open(p, 'rb').read())
            acc = None
            for b in blobs: acc = peak_accumulate(acc, *read_full(b))
            pk = Flows(*acc)([101, 202, 303, 404, 505])
            check(f'NWM peak over hours {pk}', np.allclose(pk[[0, 1, 3]], [3, 6, 9]) and np.isnan(pk[2]) and np.isnan(pk[4]))
            f2, q2 = read_full(blobs[0]); acc2 = peak_accumulate((f2, q2), f2[::-1].copy(), np.array([7, 7, 7, 7], np.float32))
            check('peak realigns a reordered feature list', np.allclose(acc2[1], [7, 7, 7, 7]))
        except ImportError: print('SKIP NWM netCDF (netCDF4 not installed)')
        # S3 key parsing + version pick
        v = 'hand_fim_4_9_9_0/01080203'
        keys = [f'{v}/branch_ids.csv', f'{v}/hydrotable.csv', f'{v}/branches/0/rem_zeroed_masked_0.tif', f'{v}/branches/0/gw_catchments_reaches_filtered_addedAttributes_0.tif',
                f'{v}/branches/0/hydroTable_0.csv', f'{v}/branches/0/gw_catchments_reaches_filtered_addedAttributes_0.gpkg',
                f'{v}/branches/3246000006/rem_zeroed_masked_3246000006.tif', f'{v}/branches/3246000006/gw_catchments_reaches_filtered_addedAttributes_3246000006.tif',
                f'{v}/branches/3246000009/rem_zeroed_masked_3246000009.tif']
        bf = branch_files(keys, '01080203')
        check(f'branch file discovery {list(bf)}', list(bf) == ['0', '3246000006'] and bf['0']['ht'].endswith('hydroTable_0.csv') and bf['3246000006']['ht'].endswith('/hydrotable.csv') and bf['3246000006']['ht_branch'] == '3246000006')
        check('newest HAND version picked', pick_version(['hand_fim_4_5_2_11/', 'hand_fim_4_9_9_0/', 'hand_fim_4_8_7_2/', 'misc/']) == 'hand_fim_4_9_9_0/')
        check('HUC groups parse, west first', parse_hucs('west,01090001')[:2] == ['01080203', '01080206'] and parse_hucs('west,01090001')[-1] == '01090001' and len(parse_hucs('all')) == 18)
        # export for sim/validate.py and run it
        crs_ok = True
        try:
            from rasterio.warp import transform as wtr
            xs, ys = wtr('EPSG:4326', 'EPSG:5070', [-72.6], [42.55])          # Deerfield area
            big = np.zeros((300, 300), np.int16); big[100:200, 100:200] = 250
            wr(f'{tmp}/ma.tif', big, xs[0] - 1500, ys[0] + 1500, 'int16', None)
            shp = validate_export(f'{tmp}/ma.tif', f'{tmp}/val', 'jul2023', res=30.0)
            meta = json.load(open(f'{tmp}/val/meta.json')); hm = np.load(f'{tmp}/val/hmax.npy')
            check(f'validate export {shp}, max {hm.max():.2f} m, wet cells {(hm > 0).sum()} (~ 1 km2 / 900 m2 = 1111)', abs(hm.max() - 2.5) < 1e-6 and 1000 < (hm > 0).sum() < 1300 and meta['frames'][-1] == 60)
            import validate as V
            import contextlib, io
            with contextlib.redirect_stdout(io.StringIO()): out = V.main(f'{tmp}/val', hwm_path=None, reports_path=None)
            check('sim/validate.py runs on the export', out.get('run') == 'fim_jul2023' and os.path.exists(f'{tmp}/val/validation.json'))
        except ImportError as e: print('SKIP validate export', e); crs_ok = False
    finally: shutil.rmtree(tmp, ignore_errors=True)
    print('SELFTEST', 'OK' if ok else 'FAILED'); return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--storms', default='jul2023', help='comma list of ' + ','.join(STORMS))
    ap.add_argument('--hucs', default='west,east', help="comma list of HUC8 codes and/or groups 'west', 'east', 'all'")
    ap.add_argument('--source', default='auto', choices=['auto', 'owp', 'nfie'])
    ap.add_argument('--bucket', default=None, help='force one OWP bucket (ciroh-owp-hand-fim or noaa-nws-owp-fim)')
    ap.add_argument('--hand-version', default=None, help='e.g. hand_fim_4_9_9_0 (default: newest found)')
    ap.add_argument('--branch0-only', action='store_true', help='only branch 0 (all streams, no level-path branches) - fast smoke run')
    ap.add_argument('--min-depth-cm', type=int, default=1)
    ap.add_argument('--no-validate', action='store_true'); ap.add_argument('--validate-res', type=float, default=30.0)
    ap.add_argument('--workers', type=int, default=8); ap.add_argument('--out', default='out/fim'); ap.add_argument('--work', default=None)
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    if a.source == 'nfie':
        a.source = 'auto'; OWP_SOURCES.clear()
    run(a)
