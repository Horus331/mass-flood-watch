"""Benchmark: the same storm run with LISFLOOD-FP 8.x (University of Bristol), the open-source reference local-inertial model.

    RUN_DIR=runs/sep2023_lisflood_20m BOX=150000,905000,170000,925000 RES=20 python w9_lisflood.py
    python w9_lisflood.py --selftest            (offline: checks the input writers on a tiny synthetic grid)

env: HF_TOKEN, RUN_DIR, GIT_SHA, BOX 'x0,y0,x1,y1' (EPSG:26986), RES (m, multiple of 10), STORM (default sep2023), T0, HOURS,
     LF_LOSS none|fc (default none), LF_CHAN vol|none (default vol), LF_BASEFLOW 1|0, LF_ZENODO (record id override),
     LF_SAVEINT (s, default 1800)
Steps:  1. download LISFLOOD-FP from Zenodo (v8.2, record 13121102; concept record 4073010 as fallback) and build it with CMake,
           with CUDA when nvcc and a GPU are present, else the OpenMP CPU build; everything lives under /content/lisflood.
        2. inputs from the same data as w4_flood_gpu.py: 10 m DEM tiles (HF data/dem10) averaged to RES, the channels30 burn
           (volume-equivalent, as w4 with SUBGRID=0), NLCD impervious -> Manning n (0.035 water/channel, 0.10 >30 % paved,
           0.08 other), MRMS hourly QPE (same mrms_hour) -> TUFLOW-format NetCDF dynamic rain, FREE boundaries on all edges.
        3. two tiny probe runs fix the rain-file conventions empirically (y orientation, units, which interval a time stamp
           covers), then the real run with the acceleration (local-inertial) solver, GPU if built.
        4. hmax.npy (float32 m), hsnap.npy (peak of the 30-min snapshots), z.npy, meta.json -> HF RUN_DIR in ONE commit,
           so w6_validate.py scores it unchanged.
"""
import math, os, sys, re, json, time, gzip, glob, shutil, zipfile, subprocess
import numpy as np

WORK = os.environ.get('LF_WORK', '/content/lisflood')
REPO = 'mohabeldokla/mass-flood-watch-tiles'
STORMS = {'sep2023': dict(t0='2023-09-11T16:00Z', hours=36, frame_min=30, title='Sept 11, 2023 flash floods'),
          'test_leominster': dict(t0='2023-09-11T17:00Z', hours=12, frame_min=30, title='Leominster test')}
ZENODO_RECORDS = ['13121102', '4073010']        # LISFLOOD-FP v8.2 (DOI 10.5281/zenodo.13121102); 4073010 = concept record (latest)
NODATA = -9999.0
LOGP = None


def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True)
    if LOGP:
        with open(LOGP, 'a') as f: f.write(s + '\n')


# ======================================================================================================================
# writers / readers (pure numpy + scipy; checked by --selftest)
# ======================================================================================================================
def write_asc(path, a, x0, y0, res, fmt='%.3f'):
    """ESRI ASCII grid.  `a` rows run north -> south (same as our .npy grids); (x0, y0) = lower-left corner of the box."""
    a = np.asarray(a, np.float64); ny, nx = a.shape
    with open(path, 'w') as f:
        f.write(f'ncols {nx}\nnrows {ny}\nxllcorner {x0:.3f}\nyllcorner {y0:.3f}\ncellsize {res:.3f}\nNODATA_value {NODATA:.0f}\n')
        np.savetxt(f, np.where(np.isfinite(a), a, NODATA), fmt=fmt, delimiter=' ')


def read_asc(path):
    """-> (array north->south float32 with NODATA as nan, header dict)."""
    hdr = {}
    with open(path) as f:
        txt = f.read()
    lines = txt.split('\n'); i = 0
    while i < len(lines) and re.match(r'^\s*[A-Za-z_]+\s', lines[i]):
        k, v = lines[i].split()[:2]; hdr[k.lower()] = float(v); i += 1
    ny, nx = int(hdr['nrows']), int(hdr['ncols'])
    a = np.array(' '.join(lines[i:]).split(), dtype=np.float32)
    if a.size != ny * nx: raise ValueError(f'{path}: {a.size} values for {ny}x{nx}')
    a = a.reshape(ny, nx); nd = hdr.get('nodata_value', NODATA)
    a[a == nd] = np.nan
    return a, hdr


def write_rain_nc(path, rain_mm, x0, y0, res, times_h, flip_y=False, flip_x=False):
    """Dynamic rain file in the TUFLOW NetCDF rainfall format that LISFLOOD-FP 8 reads with `dynamicrainfile`.
    rain_mm: (nt, ny, nx) mm in each interval (rows north -> south, like our grids).  With 1-hour intervals mm == mm/h, so the
    depth-vs-rate ambiguity of the format does not matter.  Coordinates are cell centres, x and y ascending (CF), so the file
    origin equals the DEM's xllcorner/yllcorner.  flip_y/flip_x exist only to undo an orientation the probe run detects."""
    # LISFLOOD-FP's reader (lisflood2/file_tool.cpp, read_file_netCDF_start) uses the *variable* id of "time" as a dimension id and the
    # *dimension* ids of x/y as variable ids, so variable ids must equal dimension ids: define time, y, x as dims AND as the first three
    # variables in that order.  scipy.io.netcdf_file reorders variables (record variables last), which breaks this; netCDF4 keeps the order.
    import netCDF4
    r = np.asarray(rain_mm, np.float32); nt, ny, nx = r.shape
    r = r[:, ::-1, :]                                   # north->south rows -> y ascending
    if flip_y: r = r[:, ::-1, :]
    if flip_x: r = r[:, :, ::-1]
    f = netCDF4.Dataset(path, 'w', format='NETCDF3_64BIT_OFFSET')
    f.title = 'Gridded Rainfall'; f.source = 'mass-flood-watch w9_lisflood.py (MRMS QPE 01H Pass2)'
    f.comment = 'Contains time-varying gridded rainfall (mm per interval) for LISFLOOD-FP dynamicrainfile'
    f.createDimension('time', nt); f.createDimension('y', ny); f.createDimension('x', nx)
    t = f.createVariable('time', 'f8', ('time',)); t.standard_name = 'time'; t.long_name = 'time'; t.units = 'hours'; t.axis = 'T'
    y = f.createVariable('y', 'f8', ('y',)); y.standard_name = 'projection_y_coordinate'; y.long_name = 'y-coordinate in cartesian system'; y.units = 'm'; y.axis = 'Y'
    x = f.createVariable('x', 'f8', ('x',)); x.standard_name = 'projection_x_coordinate'; x.long_name = 'x-coordinate in cartesian system'; x.units = 'm'; x.axis = 'X'
    v = f.createVariable('rainfall_depth', 'f4', ('time', 'y', 'x'), fill_value=np.float32(-999.0)); v.units = 'mm'
    tot = f.createVariable('total_rainfall_depth', 'f4', ('y', 'x'), fill_value=np.float32(-999.0))
    y[:] = y0 + (np.arange(ny) + 0.5) * res; x[:] = x0 + (np.arange(nx) + 0.5) * res
    t[:] = np.asarray(times_h, np.float64); v[:] = r; tot[:] = r.sum(axis=0)
    f.close()


def rain_records(rain_hourly, convention='forward'):
    """Hourly MRMS grids (hour h covers sim time [h, h+1) h) -> (records, times_h) for the rain file.
    forward  : LISFLOOD-FP holds a record from its time stamp until the next one   -> stamp at the interval start
    backward : a record covers the interval ending at its stamp                    -> stamp at the interval end
    linear   : records are interpolated linearly                                   -> stamp at interval centres
    A closing zero record ends the rain."""
    H = len(rain_hourly); z = np.zeros_like(rain_hourly[0])
    if convention == 'forward':
        return np.stack(list(rain_hourly) + [z]), np.arange(H + 1, dtype=float)
    if convention == 'backward':
        return np.stack([z] + list(rain_hourly)), np.arange(H + 1, dtype=float)
    if convention == 'linear':
        return np.stack([z] + list(rain_hourly) + [z]), np.r_[0.0, np.arange(H) + 0.5, float(H)]
    raise ValueError(convention)


def write_bci(path, x0, y0, x1, y1):
    """FREE (normal-depth outflow) on all four edges: the open boundary of w4 (edge cells drain out)."""
    with open(path, 'w') as f:
        f.write(f'N {x0:.1f} {x1:.1f} FREE\nS {x0:.1f} {x1:.1f} FREE\nW {y0:.1f} {y1:.1f} FREE\nE {y0:.1f} {y1:.1f} FREE\n')


def write_par(path, resroot, sim_time, saveint=1800, massint=300, cuda=False, dem='dem.asc', manning=None, rain=None,
              bci=None, start=None, dirroot='results', initial_tstep=10.0, infiltration=None, extra=None):
    """LISFLOOD-FP parameter file for the local-inertial ('acceleration') solver; `cuda` selects the GPU version (8.1+)."""
    L = [f'DEMfile {dem}', f'resroot {resroot}', f'dirroot {dirroot}', f'sim_time {int(sim_time)}', f'initial_tstep {initial_tstep:g}',
         f'massint {int(massint)}', f'saveint {int(saveint)}', 'fpfric 0.08', 'acceleration']
    if cuda: L.append('cuda')
    if manning: L.append(f'manningfile {manning}')
    if rain: L.append(f'dynamicrainfile {rain}')
    if bci: L.append(f'bcifile {bci}')
    if start: L.append(f'startfile {start}')
    if infiltration: L.append(f'infiltration {infiltration:.3e}')
    if extra: L += list(extra)     # m/s on wet floodplain cells (infevap.cpp FPInfiltration)
    with open(path, 'w') as f: f.write('\n'.join(L) + '\n')
    return L


def manning_map(water, chan, imp):
    """Same rule as w4 (PHYS 2): channels and open water 0.035, dense urban (>30 % paved) 0.10, everything else 0.08."""
    return np.where(water | chan, 0.035, np.where(imp > 0.3, 0.10, 0.08)).astype(np.float32)


def analyse_probe(hA, hB, expect_A=0.072, expect_B_forward=0.036):
    """Decide the rain-file conventions from the two probe runs on an 8x8 flat closed box (north-up arrays).
    A: 36 mm/h on the NW quadrant for the whole 2 h  -> which quadrant got water (orientation) and how much (units).
    B: 36 mm in the first record only, then zeros    -> forward (0.036 m), linear (~0.018) or backward (0)."""
    n = hA.shape[0] // 2
    q = {'NW': np.nanmean(hA[:n, :n]), 'NE': np.nanmean(hA[:n, n:]), 'SW': np.nanmean(hA[n:, :n]), 'SE': np.nanmean(hA[n:, n:])}
    wet = max(q, key=q.get)
    flip_y, flip_x = wet[0] == 'S', wet[1] == 'E'
    # water spreads across the flat box, so judge units by the volume (sum of the four quadrant means vs 0.072 m on one quadrant), not by NW alone
    vol = float(sum(q.values()))
    scale = vol / expect_A if vol > 0 else float('nan')
    if np.isfinite(scale) and abs(scale - 1) < 0.25: scale = 1.0
    b = float(np.nanmean(hB)) / max(scale, 1e-12) if np.isfinite(scale) else float('nan')
    r = b / expect_B_forward if np.isfinite(b) else float('nan')
    conv = 'forward' if r > 0.75 else ('linear' if r > 0.25 else 'backward')
    return dict(quadrants={k: round(float(v), 5) for k, v in q.items()}, flip_y=bool(flip_y), flip_x=bool(flip_x), scale=round(scale, 4),
                probe_B_ratio=round(r, 3), convention=conv)


# ======================================================================================================================
# LISFLOOD-FP: download + build
# ======================================================================================================================
def sh(cmd, cwd=None, check=True, timeout=None):
    log('$', cmd if isinstance(cmd, str) else ' '.join(cmd))
    p = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True, timeout=timeout)
    out = (p.stdout or '') + (p.stderr or '')
    if p.returncode != 0:
        log(out[-3000:])
        if check: raise RuntimeError(f'command failed ({p.returncode})')
    return p.returncode, out


def zenodo_files(rec):
    import requests
    j = requests.get(f'https://zenodo.org/api/records/{rec}', timeout=60).json()
    ver = j.get('metadata', {}).get('version') or j.get('metadata', {}).get('title', '')
    out = []
    for f in j.get('files', []):
        key = f.get('key') or f.get('filename'); link = (f.get('links') or {}).get('self') or f'https://zenodo.org/records/{rec}/files/{key}?download=1'
        out.append((key, link, f.get('size', 0), f.get('checksum', '')))
    return ver, out


def get_lisflood():
    """-> (path to the zip, version string, source url).  Cached under /content/lisflood."""
    import requests
    os.makedirs(WORK, exist_ok=True)
    recs = [os.environ['LF_ZENODO']] if os.environ.get('LF_ZENODO') else ZENODO_RECORDS
    for rec in recs:
        try:
            ver, files = zenodo_files(rec)
            zips = [f for f in files if f[0].lower().endswith('.zip')]
            if not zips: log(f'zenodo {rec}: no zip in {[f[0] for f in files]}'); continue
            key, link, size, ck = zips[0]; dst = f'{WORK}/{key}'
            if not (os.path.exists(dst) and (not size or os.path.getsize(dst) == size)):
                log(f'downloading LISFLOOD-FP {ver} from zenodo {rec}: {key} ({size / 1e6:.0f} MB)')
                with requests.get(link, stream=True, timeout=600) as r:
                    r.raise_for_status()
                    with open(dst + '.part', 'wb') as f:
                        for chunk in r.iter_content(1 << 22): f.write(chunk)
                os.replace(dst + '.part', dst)
            if ck.startswith('md5:'):
                import hashlib; h = hashlib.md5(open(dst, 'rb').read()).hexdigest()
                if h != ck[4:]: raise RuntimeError(f'md5 mismatch {h} != {ck}')
            return dst, str(ver), f'https://doi.org/10.5281/zenodo.{rec}'
        except Exception as e:
            log(f'zenodo {rec} failed:', repr(e)[:200])
    raise SystemExit('could not download LISFLOOD-FP from Zenodo')


def extract_all(zpath, dst, depth=0):
    """Unzip, and unzip any zip inside (the 8.2 archive bundles source + test cases), at most 2 levels down."""
    with zipfile.ZipFile(zpath) as z:
        for m in z.namelist():                         # no absolute paths / parent escapes
            if m.startswith('/') or '..' in m.split('/'): raise RuntimeError(f'unsafe member {m}')
        z.extractall(dst)
    if depth < 2:
        try: find_source(dst); return                   # source tree already visible
        except SystemExit: pass
        for inner in glob.glob(f'{dst}/**/*.zip', recursive=True):
            if os.path.getsize(inner) < 400e6 and not os.path.isdir(inner[:-4]):
                extract_all(inner, inner[:-4], depth + 1)


def find_source(root):
    cands = []
    for p in glob.glob(f'{root}/**/CMakeLists.txt', recursive=True):
        try: txt = open(p, errors='ignore').read()
        except Exception: continue
        if re.search(r'project\s*\(\s*[^)]*lisflood', txt, re.I) or re.search(r'add_executable\s*\(\s*lisflood', txt, re.I):
            cands.append((p.count('/'), os.path.dirname(p)))
    if not cands: raise SystemExit('no LISFLOOD-FP CMakeLists.txt found in the archive')
    return sorted(cands)[0][1]


def build_lisflood(src, want_cuda):
    """CMake build.  The build switches are read from the source itself (option()/set() names containing CUDA or NETCDF in
    CMakeLists.txt / *.cmake), because the 8.x tree keeps them in a user config.cmake; every name and value is logged."""
    sh('apt-get -qq update && DEBIAN_FRONTEND=noninteractive apt-get -qq install -y cmake libnetcdf-dev netcdf-bin libnuma-dev > /dev/null', check=False)
    cm = glob.glob(f'{src}/*.cmake') + glob.glob(f'{src}/cmake/*.cmake') + [f'{src}/CMakeLists.txt']
    names = set()
    for p in cm:
        txt = open(p, errors='ignore').read()
        names |= set(re.findall(r'option\s*\(\s*(\w+)', txt)) | set(re.findall(r'set\s*\(\s*(\w*(?:CUDA|NETCDF|NetCDF)\w*)\s', txt))
        names |= set(re.findall(r'if\s*\(\s*(\w*(?:CUDA|NETCDF)\w*)\s*\)', txt))
    log('cmake files:', [os.path.relpath(p, src) for p in cm]); log('build switches found:', sorted(names))
    if not os.path.exists(f'{src}/config.cmake'):        # 8.x ships an example config to copy
        ex = [p for p in glob.glob(f'{src}/*config*.cmake') if 'example' in p.lower() or 'default' in p.lower() or 'template' in p.lower()]
        if ex: shutil.copy(ex[0], f'{src}/config.cmake'); log('config.cmake from', os.path.basename(ex[0]))
    cfg_txt = open(f'{src}/config.cmake').read() if os.path.exists(f'{src}/config.cmake') else ''

    def attempt(cuda):
        bld = f'{WORK}/build_{"cuda" if cuda else "cpu"}'; shutil.rmtree(bld, ignore_errors=True); os.makedirs(bld)
        if cfg_txt:
            t = cfg_txt
            for nm in re.findall(r'set\s*\(\s*(\w+)\s+(?:ON|OFF|0|1|TRUE|FALSE)\s*\)', cfg_txt, re.I):
                on = ('NETCDF' in nm.upper()) or ('CUDA' in nm.upper() and cuda)
                if 'CUDA' in nm.upper() or 'NETCDF' in nm.upper():
                    t = re.sub(rf'set\s*\(\s*{nm}\s+\w+\s*\)', f'set({nm} {"ON" if on else "OFF"})', t)
            open(f'{src}/config.cmake', 'w').write(t); log('config.cmake used:\n' + t[-1500:])
        D = ['-DCMAKE_BUILD_TYPE=Release']
        for nm in names:
            if 'NETCDF' in nm.upper(): D.append(f'-D{nm}=ON')
            elif 'CUDA' in nm.upper() and not nm.upper().startswith('CMAKE'): D.append(f'-D{nm}={"ON" if cuda else "OFF"}')
        if cuda:
            try:
                cc = subprocess.run(['nvidia-smi', '--query-gpu=compute_cap', '--format=csv,noheader'], capture_output=True, text=True).stdout.split()[0]
                D.append(f'-DCMAKE_CUDA_ARCHITECTURES={cc.replace(".", "")}')
            except Exception: pass
            D.append('-DCMAKE_CUDA_COMPILER=' + (shutil.which('nvcc') or '/usr/local/cuda/bin/nvcc'))
        sh(['cmake', '-S', src, '-B', bld] + D)
        sh(f'cmake --build {bld} -j {os.cpu_count() or 2}', timeout=3600)
        exes = [p for p in glob.glob(f'{bld}/**/lisflood*', recursive=True) if os.path.isfile(p) and os.access(p, os.X_OK) and not p.endswith(('.so', '.a', '.o'))]
        exes = sorted(exes, key=lambda p: (os.path.basename(p) != 'lisflood', len(p)))
        if not exes: raise RuntimeError('build finished but no lisflood executable')
        _, ld = sh(['ldd', exes[0]], check=False)
        return exes[0], ('cudart' in ld or 'libcuda' in ld or cuda)

    if want_cuda:
        try: return attempt(True)
        except Exception as e: log('CUDA build failed, falling back to the CPU build:', repr(e)[:200])
    return attempt(False)


def run_lisflood(exe, wd, par, timeout=6 * 3600):
    t = time.time()
    p = subprocess.run([exe, '-v', par], cwd=wd, capture_output=True, text=True, timeout=timeout)
    out = (p.stdout or '') + (p.stderr or ''); open(f'{wd}/lisflood_stdout.txt', 'w').write(out)
    if p.returncode != 0: log(out[-3000:]); raise RuntimeError(f'lisflood exited {p.returncode}')
    return time.time() - t, out


def max_depth(wd, resroot, dirroot='results'):
    """Peak depth: the model's own <resroot>.max if written, else the max of the .wd snapshots."""
    d = f'{wd}/{dirroot}'
    p = f'{d}/{resroot}.max'
    if os.path.exists(p): return read_asc(p)[0], 'max file'
    snaps = sorted(glob.glob(f'{d}/{resroot}-*.wd'))
    if not snaps: raise RuntimeError(f'no .max or .wd output in {d}: {os.listdir(d) if os.path.isdir(d) else "missing"}')
    h = None
    for s in snaps: a = read_asc(s)[0]; h = a if h is None else np.fmax(h, a)
    return h, 'max of snapshots'


def probe(exe, cuda):
    """Two 8x8 flat closed-box runs that pin the rain-file conventions (see analyse_probe)."""
    res = {}
    for name in ('A', 'B'):
        wd = f'{WORK}/probe_{name}'; shutil.rmtree(wd, ignore_errors=True); os.makedirs(f'{wd}/results')
        n = 8; write_asc(f'{wd}/dem.asc', np.full((n, n), 10.0), 0.0, 0.0, 100.0)
        r = np.zeros((3, n, n), np.float32)
        if name == 'A': r[:, :n // 2, :n // 2] = 36.0      # NW quadrant (rows north->south) every record
        else: r[0] = 36.0
        write_rain_nc(f'{wd}/rain.nc', r, 0.0, 0.0, 100.0, [0.0, 1.0, 2.0])
        write_par(f'{wd}/p.par', 'p', 7200, saveint=3600, massint=600, cuda=cuda, rain='rain.nc', initial_tstep=5)
        run_lisflood(exe, wd, 'p.par', timeout=600)
        res[name] = max_depth(wd, 'p')[0]
    out = analyse_probe(res['A'], res['B']); log('probe:', out); return out


# ======================================================================================================================
# inputs from Hugging Face / MRMS (copied from w4_flood_gpu.py, which cannot be imported: it runs at top level)
# ======================================================================================================================
def breach_depressions(Z, max_cut=4.0):
    """Least-cost breaching of every closed depression to the box edge (Barnes et al. 2014 priority-flood with carving), applied to all
    cells.  Lidar keeps road, rail and runway fill but not the pipes and culverts under them, so water ponds behind every embankment
    with no surface outlet.  A carved one-cell path stands in for those pipes.  No cell is lowered more than max_cut m (deeper basins
    are kept: real ponds, quarries).  Returns (carved Z, mask of lowered cells, stats)."""
    import heapq
    ny_, nx_ = Z.shape; Zc = Z.astype(np.float64).copy(); seen = np.zeros(Z.size, bool); par = np.full(Z.size, -1, np.int64)
    edge = np.zeros(Z.shape, bool); edge[[0, -1], :] = True; edge[:, [0, -1]] = True
    hq = [(float(Zc.flat[k]), int(k)) for k in np.flatnonzero(edge)]; heapq.heapify(hq); seen[np.flatnonzero(edge)] = True
    nb8 = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)); Zf = Zc.ravel(); Zo = Z.ravel(); skipped = 0
    while hq:
        zc, k = heapq.heappop(hq); r, c = divmod(k, nx_)
        for dr, dc in nb8:
            rr, cc = r + dr, c + dc
            if rr < 0 or cc < 0 or rr >= ny_ or cc >= nx_: continue
            kk = rr * nx_ + cc
            if seen[kk]: continue
            seen[kk] = True; par[kk] = k; zn = Zf[kk]
            if zn < zc:
                path = []; p_ = k; ok = True
                while p_ >= 0 and Zf[p_] > zn:
                    if Zo[p_] - zn > max_cut: ok = False; break
                    path.append(p_); p_ = int(par[p_])
                if ok:
                    for p_ in path: Zf[p_] = zn
                else: skipped += 1
            heapq.heappush(hq, (float(Zf[kk]), kk))
    Zc = Zf.reshape(Z.shape).astype(np.float32); d = Z - Zc; low = d > 0.01
    return Zc, low, dict(cells=int(low.sum()), mean_cut_m=round(float(d[low].mean()), 2) if low.any() else 0.0, max_cut_m=round(float(d.max()), 2), kept_deep=skipped)


def build_inputs(BOX, RES, S, TOK):
    from huggingface_hub import hf_hub_download
    from scipy import ndimage
    import pandas as pd
    x0, y0, x1, y1 = BOX; T = 20000; k = int(round(RES / 10)); assert abs(k * 10 - RES) < 1e-6, 'RES must be a multiple of 10 m'
    idx = json.load(open(hf_hub_download(REPO, 'data/dem10/index.json', repo_type='dataset', token=TOK)))
    nx10, ny10 = int((x1 - x0) / 10), int((y1 - y0) / 10)
    Z10 = np.full((ny10, nx10), np.nan, np.float32)
    need = [(key, v) for key, v in idx.items() if v['valid'] > 0 and v['x'] < x1 and v['x'] + T > x0 and v['y'] < y1 and v['y'] + T > y0]
    log(f'elevation: {len(need)} tiles of 10 m')
    def paste(dst, a, v):
        c0 = int((v['x'] - x0) / 10); r0 = int((y1 - (v['y'] + T)) / 10)
        rs, cs = max(r0, 0), max(c0, 0); re_, ce = min(r0 + a.shape[0], ny10), min(c0 + a.shape[1], nx10)
        dst[rs:re_, cs:ce] = a[rs - r0:re_ - r0, cs - c0:ce - c0]
    for key, v in need: paste(Z10, np.load(hf_hub_download(REPO, f'data/dem10/{key}.npy', repo_type='dataset', token=TOK)), v)
    ny, nx = ny10 // k, nx10 // k
    Z = np.nanmean(Z10[:ny * k, :nx * k].reshape(ny, k, nx, k), axis=(1, 3)).astype(np.float32); del Z10
    nod = np.isnan(Z); low = nod | (Z <= 0.3)
    lab, _ = ndimage.label(low); edge = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]); edge = edge[edge > 0]
    sea = np.isin(lab, edge); del lab
    inland_void = nod & ~sea
    if inland_void.any():
        fill = ndimage.grey_erosion(np.where(nod, 1e4, Z), size=7); Z = np.where(inland_void, fill, Z)
    Z = np.where(np.isnan(Z), -2.0, Z).astype(np.float32)
    log(f'grid {ny} x {nx} = {ny * nx / 1e6:.2f} M cells at {RES:.0f} m; sea {sea.mean() * 100:.1f}%')
    from pyproj import Transformer
    tr = Transformer.from_crs(26986, 4326, always_xy=True)
    xc = x0 + (np.arange(nx) + 0.5) * RES; yc = y1 - (np.arange(ny) + 0.5) * RES
    lon_c, _ = tr.transform(xc, np.full(nx, (y0 + y1) / 2)); _, lat_c = tr.transform(np.full(ny, (x0 + x1) / 2), yc)
    lon_c, lat_c = np.asarray(lon_c), np.asarray(lat_c)
    # NLCD impervious
    IMP = np.zeros((ny, nx), np.float32)
    try:
        from PIL import Image
        I10 = np.zeros((ny10, nx10), np.float32); got = 0
        for key, v in need:
            try: a = np.asarray(Image.open(hf_hub_download(REPO, f'data/nlcd10/{key}.png', repo_type='dataset', token=TOK))).astype(np.float32)
            except Exception: continue
            paste(I10, a, v); got += 1
        IMP = I10[:ny * k, :nx * k].reshape(ny, k, nx, k).mean(axis=(1, 3)).astype(np.float32) / 100; del I10
        log(f'NLCD impervious: {got}/{len(need)} tiles, mean {IMP.mean() * 100:.1f}% paved')
    except Exception as e:
        log('NLCD unavailable:', repr(e)[:120])
    # grids from HF (soils, channels) cut to the box (w4 hf_grid)
    def hf_grid(name, meta_name, fields):
        D = np.load(hf_hub_download(REPO, f'data/{name}', repo_type='dataset', token=TOK)); M = json.load(open(hf_hub_download(REPO, f'data/{meta_name}', repo_type='dataset', token=TOK)))
        sx0, sy0, sx1, sy1 = M['box']; sres = M['res_m']
        if not (x0 >= sx0 - 1 and y0 >= sy0 - 1 and x1 <= sx1 + 1 and y1 <= sy1 + 1): raise RuntimeError(f'{name}: run box outside the grid')
        rr_ = np.clip(((sy1 - (y1 - (np.arange(ny) + 0.5) * RES)) / sres).astype(int), 0, M['shape'][0] - 1)
        cc_ = np.clip(((x0 + (np.arange(nx) + 0.5) * RES - sx0) / sres).astype(int), 0, M['shape'][1] - 1)
        return {f: D[f][rr_][:, cc_] for f in fields}
    water = sea.copy(); chan = np.zeros((ny, nx), bool); burn = np.zeros((ny, nx), np.float32); CW = np.zeros((ny, nx), np.float32); CD = np.zeros((ny, nx), np.float32)
    SGC = os.environ.get('LF_SGC', '0') == '1'
    if os.environ.get('LF_CHAN', 'vol') != 'none':
        try:
            CH = hf_grid('channels30/channels30.npz', 'channels30/channels30_meta.json', ['chan', 'water', 'width', 'depth'])
            water |= CH['water'].astype(bool); chan = CH['chan'].astype(bool) & ~sea
            CW = np.where(chan, CH['width'].astype(np.float32), 0); CD = np.where(chan, CH['depth'].astype(np.float32), 0)
            burn = (CD * np.minimum(CW / RES, 1.0)).astype(np.float32)          # w4 SUBGRID=0: volume-equivalent channel depth
            if not SGC: Z = np.where(chan, Z - burn, Z).astype(np.float32)     # LF_SGC=1: rivers go in LISFLOOD-FP's sub-grid channel model instead
            log(f'channels: {int(chan.sum()):,} cells burnt, mean {float(burn[chan].mean()) if chan.any() else 0:.2f} m (volume-equivalent)')
        except Exception as e:
            log('no channel grid, rivers unburnt:', repr(e)[:120])
    # culverts are not in the lidar DEM: road fill over a culvert is a dam (USGS lidar base spec).  Open a notch at every mapped crossing
    # to the lowest ground within LF_BREACH_M (default 40 m), so water passes under the road as it does through the culvert.
    nb = 0
    if os.environ.get('LF_BREACH_XINGS', '1') == '1':
        try:
            xp = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'network', 'crossings_all.json')
            XJ = json.load(open(xp)); C = XJ['columns']; il, ia = C.index('lon'), C.index('lat')
            from pyproj import Transformer
            tf = Transformer.from_crs(4326, 26986, always_xy=True)
            pts = [(r_[il], r_[ia]) for r_ in XJ['rows'] if r_[il] is not None]
            xx, yy = tf.transform([p[0] for p in pts], [p[1] for p in pts])
            kw = int(math.ceil(float(os.environ.get('LF_BREACH_M', '40')) / RES))
            for xq, yq in zip(xx, yy):
                if not (x0 <= xq < x1 and y0 <= yq < y1): continue
                rq, cq = int((y1 - yq) // RES), int((xq - x0) // RES)
                r0_, r1_, c0_, c1_ = max(0, rq - kw), min(ny, rq + kw + 1), max(0, cq - kw), min(nx, cq + kw + 1)
                zmin = float(Z[r0_:r1_, c0_:c1_].min())
                Z[max(0, rq - 1):rq + 2, max(0, cq - 1):cq + 2] = np.minimum(Z[max(0, rq - 1):rq + 2, max(0, cq - 1):cq + 2], zmin); nb += 1
            log(f'crossings: {nb} road fills opened to the lowest ground within {kw * RES:.0f} m')
        except Exception as e:
            log('crossing breach skipped:', repr(e)[:150])
    carved = np.zeros((ny, nx), bool)
    if os.environ.get('LF_BREACH_DEPRESSIONS', '1') == '1':
        t_ = time.time(); Z, carved, st_ = breach_depressions(Z, float(os.environ.get('LF_BREACH_MAX', '4')))
        log(f'depressions: {st_["cells"]:,} cells carved (mean {st_["mean_cut_m"]} m, max {st_["max_cut_m"]} m), {st_["kept_deep"]} basins deeper than the cap kept, {time.time() - t_:.0f}s')
    loss = None
    if os.environ.get('LF_LOSS', 'none') == 'fc':      # rain-excess approximation of w4's losses: steady soil rate + storm drains
        try:
            SO = hf_grid('soils30/soils30.npz', 'soils30/soils30_meta.json', ['hydgrp', 'wtd'])
            grp = np.where(SO['hydgrp'] >= 5, 4, SO['hydgrp']).astype(np.int64); grp[(SO['wtd'] < 25) & (grp > 0)] = 4
            FC = np.array([3.0, 25.4, 12.7, 6.4, 2.5], np.float32)[grp]
            loss = np.where(water, 0.0, FC * (1.0 - 0.9 * IMP) + np.where(IMP > 0.05, 7.0 * IMP, 0.0)).astype(np.float32)   # mm/h
            log(f'LF_LOSS=fc: mean loss {float(loss.mean()):.1f} mm/h subtracted from each hour of rain')
        except Exception as e:
            raise SystemExit(f'LF_LOSS=fc needs soils30: {e!r}')
    CNG = None
    if os.environ.get('LF_LOSS', 'none') == 'cn':      # NRCS curve number (TR-55): cumulative rain excess per cell, the standard event-loss method
        SO = hf_grid('soils30/soils30.npz', 'soils30/soils30_meta.json', ['hydgrp', 'wtd'])
        grp = np.where(SO['hydgrp'] >= 5, 4, SO['hydgrp']).astype(np.int64); grp[(SO['wtd'] < 25) & (grp > 0)] = 4
        CNP = np.array([77.0, 36.0, 60.0, 73.0, 79.0], np.float32)[grp]        # pervious: woods/grass mix, good condition, HSG A-D (TR-55 table 2-2); 0 = unknown -> C/D
        CNG = IMP * 98.0 + (1.0 - IMP) * CNP
        amc = os.environ.get('LF_CN_AMC', 'II')
        if amc == 'III': CNG = 23.0 * CNG / (10.0 + 0.13 * CNG)                  # wet antecedent conditions (Chow et al. 1988)
        CNG = np.clip(CNG * float(os.environ.get('LF_CN_SCALE', '1')), 30, 98); CNG = np.where(water, 100.0, CNG).astype(np.float32)
        log(f'LF_LOSS=cn: AMC {amc}, mean CN {float(CNG[~water].mean()):.1f} (HSG A-D + NLCD impervious)')
    # MRMS hourly (w4 mrms_hour)
    import requests, pygrib
    from scipy.interpolate import RegularGridInterpolator
    def get(url, tries=4):
        for kk in range(tries):
            try:
                r = requests.get(url, timeout=120)
                if r.status_code == 200: return r
            except Exception: pass
            time.sleep(3 * (kk + 1))
        raise RuntimeError(f'download failed: {url[-60:]}')
    gp = f'{WORK}/q.grib2'
    def mrms_hour(ts):
        d = ts.strftime('%Y%m%d'); f = ts.strftime('%Y%m%d-%H%M%S')
        url = f'https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MultiSensor_QPE_01H_Pass2_00.00/{d}/MRMS_MultiSensor_QPE_01H_Pass2_00.00_{f}.grib2.gz'
        open(gp, 'wb').write(gzip.decompress(get(url).content))
        g = pygrib.open(gp); m = g[1]; la, lo = m.latlons(); v = np.ma.filled(m.values, 0).astype(np.float32); g.close(); v[v < 0] = 0
        lat1d = la[:, 0]; lon1d = lo[0, :]; lon1d = np.where(lon1d > 180, lon1d - 360, lon1d)
        i0 = np.searchsorted(-lat1d, -lat_c.max() - 0.05); i1 = np.searchsorted(-lat1d, -lat_c.min() + 0.05) + 1
        j0 = np.searchsorted(lon1d, lon_c.min() - 0.05); j1 = np.searchsorted(lon1d, lon_c.max() + 0.05) + 1
        fi = RegularGridInterpolator((lat1d[i0:i1][::-1], lon1d[j0:j1]), v[i0:i1, j0:j1][::-1], bounds_error=False, fill_value=0)
        LA, LO = np.meshgrid(lat_c, lon_c, indexing='ij'); return fi((LA, LO)).astype(np.float32)
    t0 = pd.Timestamp(S['t0']); hours = [t0 + pd.Timedelta(hours=h + 1) for h in range(S['hours'])]
    RAIN, MISSING = [], []
    for ts in hours:
        for kk in range(4):
            try: RAIN.append(mrms_hour(ts)); break
            except Exception as e:
                if kk == 3: log('  no MRMS', ts, repr(e)[:80]); RAIN.append(np.zeros((ny, nx), np.float32)); MISSING.append(ts.strftime('%Y-%m-%dT%H:%MZ'))
                else: time.sleep(5 + 10 * kk)
    RAIN = np.stack(RAIN)
    tot = RAIN.sum(0); log(f'rain: max {tot.max():.0f} mm, mean {tot.mean():.0f} mm over {len(hours)} h; missing {MISSING}')
    if tot.max() <= 0: raise SystemExit('no rain data at all; refusing to run a dry storm')
    RAIN_OBS = RAIN.copy()
    if loss is not None: RAIN = np.maximum(RAIN - loss[None], 0).astype(np.float32); log(f'effective rain mean {RAIN.sum(0).mean():.0f} mm')
    if CNG is not None:
        Sx = 25400.0 / np.maximum(CNG, 1.0) - 254.0; Ia = 0.2 * Sx; P = np.cumsum(RAIN, axis=0)
        Q = np.where(P > Ia, (P - Ia) ** 2 / np.maximum(P - Ia + Sx, 1e-6), 0.0)
        RAIN = np.diff(np.concatenate([np.zeros_like(Q[:1]), Q]), axis=0).astype(np.float32)
        log(f'effective rain (CN) mean {RAIN.sum(0).mean():.0f} mm of {RAIN_OBS.sum(0).mean():.0f} mm ({100 * RAIN.sum() / max(RAIN_OBS.sum(), 1):.0f}%)')
    return dict(Z=Z, sea=sea, water=water, chan=chan, burn=burn, IMP=IMP, RAIN=RAIN, rain_total=tot, missing=MISSING, ny=ny, nx=nx, RAIN_OBS=RAIN_OBS, carved=carved, CW=CW, CD=CD, SGC=SGC)


# ======================================================================================================================
def main():
    global LOGP
    import pandas as pd
    t_all = time.time(); os.makedirs(WORK, exist_ok=True); LOGP = f'{WORK}/w9_log.txt'
    BOX = tuple(float(v) for v in os.environ.get('BOX', '150000,905000,170000,925000').split(',')); RES = float(os.environ.get('RES', '20'))
    STORM = os.environ.get('STORM', 'sep2023'); S = dict(STORMS[STORM])
    if os.environ.get('T0'): S['t0'] = os.environ['T0']
    if os.environ.get('HOURS'): S['hours'] = int(os.environ['HOURS'])
    RUN_DIR = os.environ.get('RUN_DIR', f'runs/{STORM}_lisflood_{RES:.0f}m'); TOK = os.environ.get('HF_TOKEN')
    run_name = RUN_DIR.rstrip('/').split('/')[-1]
    if not run_name.startswith(STORM + '_'): run_name = f'{STORM}_{run_name}'        # w6 takes the gauge storm id from run.split('_')[0]
    x0, y0, x1, y1 = BOX; SAVEINT = int(os.environ.get('LF_SAVEINT', '1800'))
    for mod, pkg in (('pygrib', 'pygrib'), ('pyproj', 'pyproj'), ('huggingface_hub', 'huggingface_hub'), ('PIL', 'pillow'), ('requests', 'requests')):
        try: __import__(mod)
        except ImportError: subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', pkg], check=False)
    gpu = shutil.which('nvidia-smi') is not None and subprocess.run(['nvidia-smi'], capture_output=True).returncode == 0
    if not shutil.which('nvcc') and os.path.exists('/usr/local/cuda/bin/nvcc'): os.environ['PATH'] += ':/usr/local/cuda/bin'
    want_cuda = gpu and shutil.which('nvcc') is not None
    log(f'w9 LISFLOOD-FP benchmark: {run_name} box {BOX} res {RES} m, {S["hours"]} h from {S["t0"]}; GPU {gpu}, nvcc {shutil.which("nvcc")}')
    # 1. get + build
    tb = time.time()
    zp, ver, src_url = get_lisflood()
    srcroot = f'{WORK}/src'
    if not os.path.isdir(srcroot): extract_all(zp, srcroot)
    src = find_source(srcroot); log('source tree:', src)
    exe, is_cuda = build_lisflood(src, want_cuda)
    build_s = time.time() - tb; log(f'built {exe} (CUDA {is_cuda}) in {build_s:.0f}s')
    m = re.search(r'(\d+\.\d+(?:\.\d+)?)', ver or '') or re.search(r'v?(\d+\.\d+(?:\.\d+)?)', os.path.basename(zp))
    model = f'LISFLOOD-FP {m.group(1) if m else ver}'
    # 2. conventions probe
    try: P = probe(exe, is_cuda)
    except Exception as e: log('probe failed, assuming forward / y-ascending / mm:', repr(e)[:200]); P = dict(flip_y=False, flip_x=False, scale=1.0, convention='forward', failed=repr(e)[:200])
    scale = P.get('scale') or 1.0
    if not (np.isfinite(scale) and 1e-4 < scale < 1e4): scale = 1.0
    if abs(scale - 1) > 0.2: log(f'WARNING: probe depth {scale:.3f} x expected; rain will be divided by it')
    # 3. inputs
    I = build_inputs(BOX, RES, S, TOK); ny, nx = I['ny'], I['nx']
    wd = f'{WORK}/run_{run_name}'; shutil.rmtree(wd, ignore_errors=True); os.makedirs(f'{wd}/results')
    write_asc(f'{wd}/dem.asc', I['Z'], x0, y0, RES)
    write_asc(f'{wd}/n.asc', manning_map(I['water'], I['chan'], I['IMP']), x0, y0, RES, fmt='%.3f')
    rec, th = rain_records(I['RAIN'] / (scale if abs(scale - 1) > 0.2 else 1.0), P['convention'])
    write_rain_nc(f'{wd}/rain.nc', rec, x0, y0, RES, th, flip_y=P['flip_y'], flip_x=P['flip_x'])
    write_bci(f'{wd}/run.bci', x0, y0, x1, y1)
    start = None
    extra = []; infil_mmh = float(os.environ.get('LF_INFIL_MMH', '4'))
    if I['SGC'] and I['chan'].any():
        # LISFLOOD-FP sub-grid channels (Neal et al. 2012): width raster, bank = DEM, bed = bank - bankfull depth (channels30, Bieger 2015)
        W_ = np.where(I['chan'], np.maximum(I['CW'], 1.0), 0.0); bed = np.where(I['chan'], I['Z'] - np.maximum(I['CD'], 0.3), I['Z'])
        write_asc(f'{wd}/sgc_width.asc', W_, x0, y0, RES, fmt='%.2f'); write_asc(f'{wd}/sgc_bank.asc', I['Z'], x0, y0, RES); write_asc(f'{wd}/sgc_bed.asc', bed, x0, y0, RES)
        extra += ['SGCwidth sgc_width.asc', 'SGCbank sgc_bank.asc', 'SGCbed sgc_bed.asc', f"SGCn {os.environ.get('LF_SGCN', '0.035')}"]
        if infil_mmh > 0:     # the sub-grid solver has no infiltration call; its evaporation term (mm/day, all wet cells) drains ponded water instead
            open(f'{wd}/drain.evap', 'w').write(f'# constant drainage of ponded water as evaporation (mm/day)\n2 hours\n{infil_mmh * 24:.1f} 0\n{infil_mmh * 24:.1f} {S["hours"] + 1}\n')
            extra.append('evaporation drain.evap'); infil_mmh = 0
        log(f'sub-grid channels: {int(I["chan"].sum()):,} cells, width mean {float(W_[I["chan"]].mean()):.1f} m, bankfull depth mean {float((I["Z"] - bed)[I["chan"]].mean()):.2f} m')
    elif os.environ.get('LF_BASEFLOW', '1') == '1' and I['chan'].any():
        write_asc(f'{wd}/start.wd', np.where(I['chan'], 0.3 * I['burn'], 0.0), x0, y0, RES); start = 'start.wd'     # w4: channels start a third full
    par = write_par(f'{wd}/run.par', 'res', S['hours'] * 3600, saveint=SAVEINT, cuda=is_cuda, manning='n.asc', rain='rain.nc', bci='run.bci', start=start,
                    infiltration=infil_mmh / 3.6e6 if infil_mmh > 0 else None, extra=extra)
    log('par:', ' | '.join(par))
    # 4. run
    run_s, out = run_lisflood(exe, wd, 'run.par'); log(f'LISFLOOD-FP run {run_s:.0f}s'); log(out[-1200:])
    hmax, hsrc = max_depth(wd, 'res'); hmax = np.nan_to_num(hmax, nan=0.0)
    if hmax.shape != (ny, nx): raise SystemExit(f'output shape {hmax.shape} != grid {(ny, nx)}')
    land = ~I['chan']; t0 = pd.Timestamp(S['t0']); nfr = int(S['hours'] * 60 / S['frame_min']) + 1
    snaps = {int(re.search(r'-(\d+)\.wd$', p).group(1)): p for p in glob.glob(f'{wd}/results/res-*.wd')}
    frames, hsnap = [], None
    for i in range(nfr):
        j = int(round(i * S['frame_min'] * 60 / SAVEINT)) if SAVEINT else -1
        fr = dict(t=(t0 + pd.Timedelta(minutes=S['frame_min'] * i)).strftime('%Y-%m-%dT%H:%MZ'))
        if j in snaps and abs(j * SAVEINT - i * S['frame_min'] * 60) < 1:
            h = np.nan_to_num(read_asc(snaps[j])[0], nan=0.0); hsnap = h if hsnap is None else np.maximum(hsnap, h)
            fr.update(wet_km2=round(float(((h >= 0.1) & land).sum() * RES * RES / 1e6), 1), deep_km2=round(float(((h >= 0.5) & land).sum() * RES * RES / 1e6), 1))
        frames.append(fr)
    # time above the car-stalling depths (from every snapshot, not only frame times) and first arrival, hours
    tover15 = np.zeros((ny, nx), np.float32); tover30 = np.zeros((ny, nx), np.float32); tarr30 = np.full((ny, nx), np.nan, np.float32)
    FR, FT = [], []
    for j in sorted(snaps):
        h = np.nan_to_num(read_asc(snaps[j])[0], nan=0.0)
        if h.shape != (ny, nx): continue
        FR.append(np.clip(np.round(h * 100), 0, 65000).astype(np.uint16)); FT.append(j * SAVEINT / 3600.0)
        tover15 += (h >= 0.15) * (SAVEINT / 3600.0); tover30 += (h >= 0.30) * (SAVEINT / 3600.0)
        tarr30 = np.where(np.isnan(tarr30) & (h >= 0.30), j * SAVEINT / 3600.0, tarr30)
    peak_wet = round(float(((hmax >= 0.1) & land).sum() * RES * RES / 1e6), 1)
    peak_frame_wet = max([f.get('wet_km2', 0) for f in frames] or [0])
    log(f'peak wet (hmax >= 10 cm, land) {peak_wet} km2; largest snapshot wet area {peak_frame_wet} km2; {len(snaps)} snapshots')
    mass = sorted(glob.glob(f'{wd}/results/res.mass'))
    mass_tail = open(mass[0]).read().strip().split('\n')[-2:] if mass else []
    # 5. run layout + one commit
    OUT = f'{wd}/out'; os.makedirs(OUT, exist_ok=True)
    np.save(f'{OUT}/hmax.npy', hmax.astype(np.float32)); np.save(f'{OUT}/z.npy', I['Z'].astype(np.float32))
    if hsnap is not None: np.save(f'{OUT}/hsnap.npy', hsnap.astype(np.float32))
    if FR: np.savez_compressed(f'{OUT}/frames_cm.npz', depth_cm=np.stack(FR), hours=np.array(FT, np.float32))
    np.save(f'{OUT}/watermask.npy', (I['water'] | I['chan'] | I['carved']).astype(np.uint8))
    np.savez_compressed(f'{OUT}/timing.npz', tover15=tover15, tover30=tover30, tarr30=tarr30, saveint_s=SAVEINT)
    R = I['RAIN_OBS']; r3 = np.stack([R[i:i + 3].sum(0) for i in range(max(1, len(R) - 2))])
    np.savez_compressed(f'{OUT}/rainstats.npz', total=R.sum(0), peak1h=R.max(0), peak3h=r3.max(0), hour_of_peak=R.argmax(0).astype(np.int16),
                        hourly_mean=R.reshape(len(R), -1).mean(1), hourly_max=R.reshape(len(R), -1).max(1))
    for f in ('run.par', 'run.bci', 'lisflood_stdout.txt'): shutil.copy(f'{wd}/{f}', f'{OUT}/{f}')
    if mass: shutil.copy(mass[0], f'{OUT}/lisflood.mass')
    meta = dict(run=run_name, title=S['title'] + ' · LISFLOOD-FP benchmark', box=list(BOX), res_m=RES, shape=[ny, nx], t0=S['t0'], frame_min=S['frame_min'], frames=frames,
                crs='EPSG:26986', model=model, model_source=src_url, model_build=dict(cuda=bool(is_cuda), exe=os.path.basename(exe), build_s=round(build_s)),
                solver='acceleration (local inertial, Bates et al. 2010)' + (' on GPU (cuda)' if is_cuda else ' on CPU (OpenMP)'),
                inputs=dict(dem='HF data/dem10 averaged to RES', channels=os.environ.get('LF_CHAN', 'vol'), manning='0.035 water/channel, 0.10 dense urban, 0.08 other',
                            rain='MRMS MultiSensor QPE 01H Pass2 -> TUFLOW NetCDF dynamicrainfile', loss=os.environ.get('LF_LOSS', 'none'),
                            boundary='FREE on all edges', baseflow=start is not None, inflows='none'),
                rain_probe=P, hmax_source=hsrc, rain_total_max_mm=round(float(I['rain_total'].max())), rain_total_mean_mm=round(float(I['rain_total'].mean())),
                rain_missing_hours=I['missing'], runtime_s=round(run_s), total_s=round(time.time() - t_all), peak_wet_km2=peak_wet, peak_snapshot_wet_km2=peak_frame_wet,
                mass_tail=mass_tail, git_sha=os.environ.get('GIT_SHA', '')[:8])
    json.dump(meta, open(f'{OUT}/meta.json', 'w'))
    shutil.copy(LOGP, f'{OUT}/w9_log.txt')
    if not TOK or os.environ.get('LF_NO_UPLOAD') == '1': log('no upload: outputs left in', OUT); return
    from huggingface_hub import HfApi, CommitOperationAdd
    api = HfApi(token=TOK); files = sorted(os.listdir(OUT))
    ops = [CommitOperationAdd(path_in_repo=f'{RUN_DIR}/{f}', path_or_fileobj=f'{OUT}/{f}') for f in files]
    for k_ in range(5):
        try: api.create_commit(REPO, repo_type='dataset', operations=ops, commit_message=f'{RUN_DIR} LISFLOOD-FP benchmark ({len(ops)} files)'); break
        except Exception as e: log('  retry', k_, repr(e)[:120]); time.sleep(10 + 20 * k_)
    else: log('UPLOAD FAILED'); sys.exit(1)
    log(f'uploaded {len(files)} files to {RUN_DIR} | run {run_s:.0f}s, build {build_s:.0f}s, peak wet {peak_wet} km2 | ALL DONE')


# ======================================================================================================================
def selftest():
    """Offline: writers and readers on a tiny synthetic grid, plus the probe logic on synthetic outputs."""
    import tempfile
    from scipy.io import netcdf_file
    d = tempfile.mkdtemp(prefix='w9st_'); ok = []
    x0, y0, res = 150000.0, 905000.0, 20.0; ny, nx = 5, 7
    z = (np.arange(ny * nx, dtype=np.float32).reshape(ny, nx) * 0.5 + 100).astype(np.float32); z[0, 0] = np.nan
    write_asc(f'{d}/dem.asc', z, x0, y0, res)
    a, h = read_asc(f'{d}/dem.asc')
    assert (int(h['ncols']), int(h['nrows'])) == (nx, ny) and h['xllcorner'] == x0 and h['yllcorner'] == y0 and h['cellsize'] == res
    assert np.isnan(a[0, 0]) and np.allclose(a[1:], z[1:], atol=1e-3) and np.allclose(a[0, 1:], z[0, 1:], atol=1e-3); ok.append('DEM ascii round trip + NODATA')
    water = np.zeros((ny, nx), bool); water[2, :] = True; chan = np.zeros((ny, nx), bool); chan[:, 3] = True
    imp = np.zeros((ny, nx), np.float32); imp[0, :] = 0.5
    n = manning_map(water, chan, imp)
    assert n[2, 0] == np.float32(0.035) and n[4, 3] == np.float32(0.035) and n[0, 0] == np.float32(0.10) and n[4, 0] == np.float32(0.08)
    write_asc(f'{d}/n.asc', n, x0, y0, res); assert np.allclose(read_asc(f'{d}/n.asc')[0], n); ok.append('Manning map (w4 rule) + ascii')
    H = 3; rain = np.zeros((H, ny, nx), np.float32)
    for k in range(H): rain[k, 0, :] = 10.0 * (k + 1)                  # rain only on the northern row, rising each hour
    rec, th = rain_records(rain, 'forward')
    assert rec.shape == (H + 1, ny, nx) and list(th) == [0, 1, 2, 3] and rec[-1].sum() == 0 and rec[0, 0, 0] == 10
    rb, tb = rain_records(rain, 'backward'); assert list(tb) == [0, 1, 2, 3] and rb[0].sum() == 0 and rb[1, 0, 0] == 10
    rl, tl = rain_records(rain, 'linear'); assert list(tl) == [0, 0.5, 1.5, 2.5, 3] and rl.shape[0] == H + 2
    write_rain_nc(f'{d}/rain.nc', rec, x0, y0, res, th)
    f = netcdf_file(f'{d}/rain.nc', 'r', mmap=False)
    v = f.variables['rainfall_depth']; y = f.variables['y'][:].copy(); x = f.variables['x'][:].copy(); t = f.variables['time'][:].copy()
    assert v.dimensions == ('time', 'y', 'x') and v.shape == (H + 1, ny, nx)
    assert f.variables['time'].units in (b'hours', 'hours') and np.all(np.diff(y) > 0) and np.all(np.diff(x) > 0)
    assert abs(y[0] - (y0 + res / 2)) < 1e-6 and abs(x[0] - (x0 + res / 2)) < 1e-6 and abs(y[-1] - (y0 + (ny - 0.5) * res)) < 1e-6
    vv = v[:].copy(); assert vv[0, -1, 0] == 10 and vv[0, 0, :].sum() == 0 and vv[2, -1, 3] == 30   # northern row = largest y
    assert np.allclose(f.variables['total_rainfall_depth'][:][-1, :], 60) and list(t) == [0, 1, 2, 3]
    f.close(); ok.append('rain NetCDF (TUFLOW layout, y ascending, hourly mm, interval-start stamps)')
    write_rain_nc(f'{d}/rain_f.nc', rec, x0, y0, res, th, flip_y=True)
    f = netcdf_file(f'{d}/rain_f.nc', 'r', mmap=False); assert f.variables['rainfall_depth'][:][0, 0, 0] == 10; f.close(); ok.append('rain flip_y option')
    write_bci(f'{d}/run.bci', x0, y0, x0 + nx * res, y0 + ny * res)
    bl = open(f'{d}/run.bci').read().split('\n'); assert bl[0] == f'N {x0:.1f} {x0 + nx * res:.1f} FREE' and bl[2].startswith('W 905000.0') and len([l for l in bl if l]) == 4
    ok.append('boundary file (FREE on 4 edges)')
    write_par(f'{d}/run.par', 'res', 36 * 3600, cuda=True, manning='n.asc', rain='rain.nc', bci='run.bci', start='start.wd')
    txt = open(f'{d}/run.par').read().split('\n')
    for need in ('DEMfile dem.asc', 'sim_time 129600', 'acceleration', 'cuda', 'manningfile n.asc', 'dynamicrainfile rain.nc', 'bcifile run.bci', 'startfile start.wd', 'saveint 1800'):
        assert need in txt, need
    assert 'cuda' not in write_par(f'{d}/cpu.par', 'r', 60)
    ok.append('parameter file (acceleration, cuda, manningfile, dynamicrainfile, bcifile, startfile)')
    # probe logic: synthetic outputs for the four orientations and three time conventions
    def fake(q, depth):
        a = np.zeros((8, 8)); r = slice(0, 4) if q[0] == 'N' else slice(4, 8); c = slice(0, 4) if q[1] == 'W' else slice(4, 8); a[r, c] = depth; return a
    for q, fy, fx in (('NW', False, False), ('SW', True, False), ('NE', False, True), ('SE', True, True)):
        p = analyse_probe(fake(q, 0.072), np.full((8, 8), 0.036)); assert (p['flip_y'], p['flip_x'], p['convention']) == (fy, fx, 'forward') and abs(p['scale'] - 1) < 1e-6
    assert analyse_probe(fake('NW', 0.072), np.full((8, 8), 0.0))['convention'] == 'backward'
    assert analyse_probe(fake('NW', 0.072), np.full((8, 8), 0.018))['convention'] == 'linear'
    p = analyse_probe(fake('NW', 72.0), np.full((8, 8), 36.0)); assert abs(p['scale'] - 1000) < 1e-3 and p['convention'] == 'forward'
    ok.append('probe analysis (orientation, units, time convention)')
    # output reader: a .max file in the layout LISFLOOD-FP writes
    os.makedirs(f'{d}/results'); write_asc(f'{d}/results/res-0000.wd', z * 0, x0, y0, res); write_asc(f'{d}/results/res-0001.wd', np.nan_to_num(z) * 0 + 0.2, x0, y0, res)
    hm, src = max_depth(d, 'res'); assert src == 'max of snapshots' and np.allclose(hm[1:], 0.2)
    write_asc(f'{d}/results/res.max', np.full((ny, nx), 0.3), x0, y0, res); hm, src = max_depth(d, 'res'); assert src == 'max file' and np.allclose(hm, 0.3)
    ok.append('output reader (.max, else max of .wd snapshots)')
    shutil.rmtree(d)
    for o in ok: print('ok  ', o)
    print(f'SELFTEST PASSED ({len(ok)} checks)')


if __name__ == '__main__':
    if '--selftest' in sys.argv: selftest()
    else: main()
