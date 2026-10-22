"""Benchmark: the same storm run with LISFLOOD-FP 8.x (University of Bristol), the open-source reference local-inertial model.

    RUN_DIR=runs/sep2023_lisflood_20m BOX=150000,905000,170000,925000 RES=20 python w9_lisflood.py
    python w9_lisflood.py --selftest            (offline: checks the input writers on a tiny synthetic grid)

env: HF_TOKEN, RUN_DIR, GIT_SHA, BOX 'x0,y0,x1,y1' (EPSG:26986), RES (m, multiple of 10), STORM (default sep2023), T0, HOURS,
     LF_LOSS none|fc (default none), LF_CHAN vol|none (default vol), LF_BASEFLOW 1|0, LF_ZENODO (record id override),
     LF_SAVEINT (s, default 1800), LF_QOUT 1 (face fluxes -> flow through crossings and gauges),
     LF_VOUT 1 ('hazard' in the .par -> vel_max.npz: peak cell speed m/s from .maxVc, peak depth x speed m2/s),
     LF_DOMAIN basin + LF_DOMAIN_FILE (watershed-shaped domain, sim/colab/lf_domain.py; default box), LF_EXE / LF_EXE_CUDA (prebuilt LISFLOOD-FP),
     LF_MRMS_DIR (MRMS file cache: stage on a login node, then run offline)
Steps:  1. download LISFLOOD-FP from Zenodo (v8.2, record 13121102; concept record 4073010 as fallback) and build it with CMake,
           with CUDA when nvcc and a GPU are present, else the OpenMP CPU build; everything lives under /content/lisflood.
        2. inputs from the same data as w4_flood_gpu.py: 10 m DEM tiles (HF data/dem10) averaged to RES, the channels30 burn
           (volume-equivalent, as w4 with SUBGRID=0), NLCD impervious -> Manning n (0.035 water/channel, 0.10 >30 % paved,
           0.08 other), MRMS hourly QPE (same mrms_hour) -> TUFLOW-format NetCDF dynamic rain, FREE boundaries on all edges.
        3. two tiny probe runs fix the rain-file conventions empirically (y orientation, units, which interval a time stamp
           covers), then the real run with the acceleration (local-inertial) solver, GPU if built.
        4. hmax.npy (float32 m), hsnap.npy (peak of the 30-min snapshots), z.npy (model DEM: burnt, notched, breached),
           z_raw.npz (lidar DEM before those edits, and the highest 10 m cell per cell: road crests), vel_max.npz (LF_VOUT=1), meta.json -> HF RUN_DIR in ONE commit,
           so w6_validate.py scores it unchanged.
"""
import math, os, sys, re, json, time, gzip, glob, shutil, zipfile, subprocess
import numpy as np

WORK = os.environ.get('LF_WORK', '/content/lisflood')
REPO = 'mohabeldokla/mass-flood-watch-tiles'
STORMS = {'sep2023': dict(t0='2023-09-11T16:00Z', hours=36, frame_min=30, title='Sept 11, 2023 flash floods'),
          'test_leominster': dict(t0='2023-09-11T17:00Z', hours=12, frame_min=30, title='Leominster test'),
          'jul2023vt': dict(t0='2023-07-09T18:00Z', hours=60, frame_min=30, title='July 10-11, 2023 Vermont flood'),
          'aug2021': dict(t0='2021-08-19T09:00Z', hours=18, frame_min=30, title='Aug 19, 2021 flash floods (Fred)')}   # inputs: LF_DATA_DIR (sim/colab/vt_inputs.py)
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
    depth-vs-rate ambiguity of the format does not matter.  Coordinates are cell centres, x ascending and y descending (north row
    first, as LISFLOOD-FP's DynamicRain indexes it), so the grid's lower-left corner equals the DEM's xllcorner/yllcorner.  flip_y/flip_x exist only to undo an orientation the probe run detects."""
    # LISFLOOD-FP's reader (lisflood2/file_tool.cpp, read_file_netCDF_start) uses the *variable* id of "time" as a dimension id and the
    # *dimension* ids of x/y as variable ids, so variable ids must equal dimension ids: define time, y, x as dims AND as the first three
    # variables in that order.  scipy.io.netcdf_file reorders variables (record variables last), which breaks this; netCDF4 keeps the order.
    import netCDF4
    r = np.asarray(rain_mm, np.float32); nt, ny, nx = r.shape
    # y is written DESCENDING (first row = north) with rows north -> south.  LISFLOOD-FP's DynamicRain takes dy = ys[0] - ys[1] and
    # tly = ys[0] + dy/2; with ascending y, dy < 0, every DEM row j reads file row ny - j (one row off) and the north row reads past the
    # end of the buffer (garbage rain, the north-edge water source found 21 Oct 2026).  Descending y gives dy > 0, tly = top, row j -> j.
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
    y[:] = y0 + (ny - np.arange(ny) - 0.5) * res; x[:] = x0 + (np.arange(nx) + 0.5) * res
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


# Floodplain Manning n by NLCD class for the undeveloped classes (Chow 1959 table 5-6 flood plains; Arcement & Schneider 1989 USGS WSP 2339):
# pasture / short grass 0.035, cultivated 0.04, scattered brush 0.05-0.07, heavy stand of timber 0.10-0.12 (0.12-0.16 with flow into the
# branches), wooded swamp ~0.12, emergent marsh 0.07-0.10.  Forest and woody wetland take LF_N_FOREST.  Developed classes keep the paved rule.
NLCD_N = {31: 0.03, 52: 0.07, 71: 0.035, 81: 0.035, 82: 0.04, 95: 0.08}
NLCD_FOREST = (41, 42, 43, 90)


def manning_map(water, chan, imp, lc=None):
    """w4 rule (PHYS 2): channels and open water LF_N_CHAN (0.035), dense urban (>30 % paved) 0.10, everything else LF_N_FP (0.08).
    lc (NLCD class grid, LF_N_LANDCOVER=1): undeveloped land takes the NLCD_N table / LF_N_FOREST (0.12) instead of LF_N_FP."""
    nch = float(os.environ.get('LF_N_CHAN', '0.035')); nfp = float(os.environ.get('LF_N_FP', '0.08'))
    other = np.full(water.shape, nfp, np.float32)
    if lc is not None:
        for cls, v in NLCD_N.items(): other[lc == cls] = v
        other[np.isin(lc, NLCD_FOREST)] = float(os.environ.get('LF_N_FOREST', '0.12'))
    return np.where(water | chan, nch, np.where(imp > 0.3, 0.10, other)).astype(np.float32)


def nlcd_landcover(BOX, RES, ny, nx):
    """NLCD 2021 land cover classes on the run grid from the MRLC WCS (nearest-neighbour resample to RES); None if unavailable."""
    import io, requests
    x0, y0, x1, y1 = BOX
    for cov in ('mrlc_download:NLCD_2021_Land_Cover_L48', 'NLCD_2021_Land_Cover_L48', 'mrlc_download:NLCD_2019_Land_Cover_L48'):
        u = ('https://www.mrlc.gov/geoserver/mrlc_download/wcs?service=WCS&version=1.0.0&request=GetCoverage&coverage=' + cov +
             f'&CRS=EPSG:26986&BBOX={x0},{y0},{x1},{y1}&WIDTH={nx}&HEIGHT={ny}&FORMAT=GeoTIFF')
        for k in range(3):
            try:
                r = requests.get(u, timeout=240)
                if r.status_code == 200 and r.content[:2] in (b'II', b'MM'):
                    try:
                        import tifffile; a = tifffile.imread(io.BytesIO(r.content))
                    except ImportError:
                        from PIL import Image; a = np.asarray(Image.open(io.BytesIO(r.content)))
                    a = a[..., 0] if a.ndim == 3 else a
                    if a.shape == (ny, nx): return a.astype(np.uint8), cov
                    log('land cover: unexpected shape', a.shape, cov); break
                log('land cover: bad response', cov, r.status_code, r.content[:120])
                break
            except Exception as e:
                log('land cover retry', k, cov, repr(e)[:100]); time.sleep(5 + 10 * k)
    return None, None


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


def patch_source(src):
    """Source fixes for newer toolchains (idempotent).  cuda/adaptive/utilities/cuda_utils.cuh declares `cudaError_t sync();`, which
    clashes with glibc's `void sync(void)` from <unistd.h> on Ubuntu 24.04 ("cannot overload functions distinguished by return type
    alone", seen on WPI Turing, 22 Oct 2026): rename the CUDA helper to lfp_cuda_sync in the cuda/ tree."""
    n = 0
    for p in glob.glob(f'{src}/cuda/**/*', recursive=True):
        if not p.endswith(('.cu', '.cuh', '.h', '.hpp', '.cpp')) or not os.path.isfile(p): continue
        t = open(p, errors='replace').read(); t2 = re.sub(r'(?<![\w:.>])sync\s*\(', 'lfp_cuda_sync(', t)
        if t2 != t: open(p, 'w').write(t2); n += 1
    if n: log(f'patched sync() -> lfp_cuda_sync() in {n} CUDA source files')


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
    patch_source(src)
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
            if os.environ.get('LF_CUDA_ARCH'): D.append(f"-DCMAKE_CUDA_ARCHITECTURES={os.environ['LF_CUDA_ARCH']}")   # e.g. '80;89;90;120' for a mixed cluster
            else:
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
def breach_depressions(Z, max_cut=4.0, chan=None, max_cut_chan=None, d4=False, protect=None):
    """Least-cost breaching of every closed depression to the box edge (Barnes et al. 2014 priority-flood with carving), applied to all
    cells.  Lidar keeps road, rail and runway fill but not the pipes and culverts under them, so water ponds behind every embankment
    with no surface outlet.  A carved one-cell path stands in for those pipes.  No cell is lowered more than max_cut m (deeper basins
    are kept: real ponds, quarries).  chan / max_cut_chan (LF_BREACH_CHAN_MAX): a pit whose bottom is a mapped channel cell may be cut
    up to max_cut_chan instead.  A river never runs uphill and a real dam holds a flat pool level with its crest, so a closed pit on a
    mapped river is a DEM artifact (bridge deck or road fill left in the bare earth, culvert fill); the default cap leaves those deeper
    than max_cut as dead storage that never drains.  d4 (LF_BREACH_D4=1): search and carve over the 4 face neighbours only.  LISFLOOD-FP
    exchanges water across cell faces (x and y fluxes, Bates et al. 2010), never corner to corner, so an 8-connected one-cell path that
    steps diagonally is no outlet at all: the pit behind it stays closed and its water can only leave by infiltration.
    protect (LF_DAMS, sim/colab/lf_dams.py): cells never lowered -- a carve whose path crosses one is abandoned (the basin is kept).
    Returns (carved Z, mask of lowered cells, stats)."""
    import heapq
    ny_, nx_ = Z.shape; Zc = Z.astype(np.float64).copy(); seen = np.zeros(Z.size, bool); par = np.full(Z.size, -1, np.int64)
    edge = np.zeros(Z.shape, bool); edge[[0, -1], :] = True; edge[:, [0, -1]] = True
    hq = [(float(Zc.flat[k]), int(k)) for k in np.flatnonzero(edge)]; heapq.heapify(hq); seen[np.flatnonzero(edge)] = True
    nb8 = ((-1, 0), (0, -1), (0, 1), (1, 0)) if d4 else ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    Zf = Zc.ravel(); Zo = Z.ravel(); skipped = 0; prf = protect.ravel() if protect is not None else None
    chf = chan.ravel() if (chan is not None and max_cut_chan is not None) else None; chan_deep = 0
    while hq:
        zc, k = heapq.heappop(hq); r, c = divmod(k, nx_)
        for dr, dc in nb8:
            rr, cc = r + dr, c + dc
            if rr < 0 or cc < 0 or rr >= ny_ or cc >= nx_: continue
            kk = rr * nx_ + cc
            if seen[kk]: continue
            seen[kk] = True; par[kk] = k; zn = Zf[kk]
            if zn < zc:
                path = []; p_ = k; ok = True; cap = max_cut if chf is None or not chf[kk] else max(max_cut, max_cut_chan)
                while p_ >= 0 and Zf[p_] > zn:
                    if Zo[p_] - zn > cap or (prf is not None and prf[p_]): ok = False; break
                    path.append(p_); p_ = int(par[p_])
                if ok:
                    for p_ in path: Zf[p_] = zn
                    if cap > max_cut and path and max(Zo[p_] - zn for p_ in path) > max_cut: chan_deep += 1
                else: skipped += 1
            heapq.heappush(hq, (float(Zf[kk]), kk))
    Zc = Zf.reshape(Z.shape).astype(np.float32); d = Z - Zc; low = d > 0.01
    return Zc, low, dict(cells=int(low.sum()), mean_cut_m=round(float(d[low].mean()), 2) if low.any() else 0.0, max_cut_m=round(float(d.max()), 2), kept_deep=skipped,
                         chan_deep_cut=chan_deep)


CULVERT_SHAPES = ('circular', 'elliptical', 'pipe_arch', 'box', 'arch_open', 'arch_closed')


def sized_notch(row, zmin, zcrest, res, n_min=0.035, n_max=5.0):
    """LF_BREACH_SIZED: (cut level, Manning n) for a crossing with a surveyed culvert, else None (keep the default opening).
    A 20 m grid cannot hold a 1 m barrel, so the 3x3-cell notch (width W = 3 res, length L = 3 res) keeps its place and is (a) cut no lower
    than the culvert invert, estimated as the DEM crest minus NAACC fill + rise (the lowest ground within LF_BREACH_M otherwise), and
    (b) given the Manning n at which it passes the barrel's HDS-5 capacity at headwater = rise (inlet just submerged, the usual design
    limit HW/D = 1): steady local-inertial flux Q = W h^(5/3) S^(1/2) / n with mean depth h = rise / 2 and head drop = rise over L
    -> n = W (D/2)^(5/3) (D/L)^(1/2) / Q_cap(HW = D), clipped to [n_min, n_max].  Above the crown the notch conveys like an open
    channel (more than a pressurised barrel) and the road cells around it overtop as weirs."""
    shape, rise, span = row.get('shape'), row.get('rise_m'), row.get('span_m')
    if shape not in CULVERT_SHAPES or not rise or rise <= 0 or (shape != 'circular' and not span): return None
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'infra'))
    import culvert as CV
    nb_ = int(row.get('n_barrels') or 1); fill = row.get('fill_m'); L_ = row.get('length_m') or None
    S_ = (row.get('slope_pct') or 1.0) / 100.0
    qcap = CV.q_at_headwater(rise, shape, span or rise, rise, row.get('material') or 'concrete', row.get('inlet') or 'headwall', S_, L_ or 20.0, 0.0, nb_)
    W = 3 * res; n_eq = W * (0.5 * rise) ** (5 / 3) * math.sqrt(rise / W) / max(qcap, 1e-3)
    zcut = max(zmin, zcrest - (fill + rise)) if fill is not None else zmin
    return float(min(zcut, zcrest)), float(np.clip(n_eq, n_min, n_max))


def open_crossings(Z, rows_x, xx, yy, BOX, RES, kw, sized=False):
    """Open a 3x3-cell notch at every crossing in the box down to the lowest ground within kw cells (default), or sized to the surveyed culvert
    (sized_notch).  Returns (Z, NOV: Manning n of sized notches else nan, XG: one dict per opened crossing)."""
    x0, y0, x1, y1 = BOX; ny, nx = Z.shape; Z = Z.copy(); NOV = np.full((ny, nx), np.nan, np.float32); XG = []
    for row, xq, yq in zip(rows_x, xx, yy):
        if not (x0 <= xq < x1 and y0 <= yq < y1): continue
        rq, cq = int((y1 - yq) // RES), int((xq - x0) // RES)
        r0_, r1_, c0_, c1_ = max(0, rq - kw), min(ny, rq + kw + 1), max(0, cq - kw), min(nx, cq + kw + 1)
        zmin = float(Z[r0_:r1_, c0_:c1_].min()); blk = (slice(max(0, rq - 1), rq + 2), slice(max(0, cq - 1), cq + 2))
        zcrest = float(Z[blk].max()); zcut, n_eq = zmin, None
        if sized:
            sz = sized_notch(row, zmin, zcrest, RES)
            if sz is not None: zcut, n_eq = sz; NOV[blk] = np.fmax(NOV[blk], n_eq)
        Z[blk] = np.minimum(Z[blk], zcut)
        XG.append(dict(id=row.get('id'), r=rq, c=cq, r0=blk[0].start, r1=min(ny, rq + 2), c0=blk[1].start, c1=min(nx, cq + 2), zmin=round(zmin, 2),
                       zcrest=round(zcrest, 2), zcut=round(float(zcut), 2), n_eq=None if n_eq is None else round(float(n_eq), 3)))
    return Z, NOV, XG


def block_throughflow(Qx, Qy, r0, r1, c0, c1):
    """Flow through a block of cells rows r0..r1-1, cols c0..c1-1 from LISFLOOD-FP flux grids (m3/s per face; Qx (ny, nx+1), column c = face
    between cells c-1 and c, + eastwards; Qy (ny+1, nx), row r = face between rows r-1 and r, + southwards, rows north -> south).
    Returns (inflow, outflow) summed over the block's perimeter faces."""
    inw = np.r_[Qx[r0:r1, c0], -Qx[r0:r1, c1], Qy[r0, c0:c1], -Qy[r1, c0:c1]]
    inw = np.nan_to_num(inw)
    return float(inw[inw > 0].sum()), float(-inw[inw < 0].sum())


def cell_speed(Vx, Vy):
    """Cell-centre speed (m/s) from LISFLOOD-FP face velocities, the way its own UpdateV does it (util.cpp): the larger |V| of the two x faces
    and of the two y faces, combined as a vector.  Vx (ny, nx+1), Vy (ny+1, nx), as the .Vx / .Vy snapshot grids (voutput)."""
    Vx = np.abs(np.nan_to_num(Vx)); Vy = np.abs(np.nan_to_num(Vy))
    xv = np.maximum(Vx[:, :-1], Vx[:, 1:]); yv = np.maximum(Vy[:-1, :], Vy[1:, :])
    return np.sqrt(xv * xv + yv * yv).astype(np.float32)


def velocity_peaks(wd, resroot, shape, dirroot='results', keep=False):
    """LF_VOUT=1 ('hazard' in the .par: voutput + voutput_max + hazard, pars.cpp): peak speed and peak depth x speed per cell.
    vmax  : <resroot>.maxVc, the cell speed maximised every time step (UpdateV), m/s; else the max over the .Vx/.Vy snapshots
    dvmax : max over the saveint snapshots of h x speed (both from the same snapshot), and at least maxVc x maxVcd (depth at the time of peak
            speed), m2/s.  Snapshots are 30 min apart, so dvmax can miss a short spike between them; maxVc x maxVcd is a lower bound at every step.
    Snapshot .Vx/.Vy files are deleted after reading unless keep (each is ~1M cells of ascii).
    LF_VDUR='0.6,1.0,1.5,1.8' (opt-in, m/s): also keep the snapshot-only peaks (vsnap_max, dvsnap_max) and count, per cell, the snapshots whose speed is at or above each listed speed with depth
    >= 0.02 m (time above an erosion threshold; x saveint = hours).  Returned as info['_vdur'] = dict(vdur_thr, vdur_count, vdur_snapshots)."""
    d = f'{wd}/{dirroot}'; ny, nx = shape; info = {}
    vmax = np.zeros(shape, np.float32); dv = np.zeros(shape, np.float32); vsnap = np.zeros(shape, np.float32); n = 0
    vthr = [float(t) for t in os.environ.get('LF_VDUR', '').split(',') if t.strip()]; vcnt = np.zeros((len(vthr), ny, nx), np.uint16); dvs = np.zeros(shape, np.float32)
    for fx in sorted(glob.glob(f'{d}/{resroot}-*.Vx')):
        fy = fx[:-3] + '.Vy'; fh = fx[:-3] + '.wd'
        if not os.path.exists(fy): continue
        try: Vx = read_asc(fx)[0]; Vy = read_asc(fy)[0]
        except Exception as e: log('velocity file unreadable', fx, repr(e)[:80]); continue
        if Vx.shape != (ny, nx + 1) or Vy.shape != (ny + 1, nx): log('unexpected velocity grid shapes', Vx.shape, Vy.shape); break
        v = cell_speed(Vx, Vy); vsnap = np.maximum(vsnap, v); hs = None
        if os.path.exists(fh): hs = np.nan_to_num(read_asc(fh)[0]); dv = np.maximum(dv, hs * v); dvs = np.maximum(dvs, hs * v)
        for k_, t_ in enumerate(vthr): vcnt[k_] += (v >= t_) & ((hs >= 0.02) if hs is not None else True)
        n += 1
        if not keep: os.remove(fx); os.remove(fy)
    info['snapshots'] = n
    if os.path.exists(f'{d}/{resroot}.maxVc'):
        vmax = np.nan_to_num(read_asc(f'{d}/{resroot}.maxVc')[0]).astype(np.float32); info['vmax_source'] = 'maxVc (every time step)'
        if os.path.exists(f'{d}/{resroot}.maxVcd'):
            dv = np.maximum(dv, vmax * np.nan_to_num(read_asc(f'{d}/{resroot}.maxVcd')[0])); info['dv_source'] = 'max(snapshot h x speed, maxVc x maxVcd)'
    else:
        vmax = vsnap; info['vmax_source'] = 'max of snapshots'
    info.setdefault('dv_source', 'snapshot h x speed')
    if vthr: info['_vdur'] = dict(vdur_thr=np.array(vthr, np.float32), vdur_count=vcnt, vdur_snapshots=np.array(n), vsnap_max=vsnap.astype(np.float32),
                                  dvsnap_max=dvs.astype(np.float32))   # snapshot-only peaks: free of the single-time-step spikes in .maxVc
    return vmax.astype(np.float32), dv.astype(np.float32), info


def edge_report(Z, label):
    """One log line per box edge: NaN cells, elevation range, and cells more than 1 m below their inward neighbour (a FREE boundary on such a
    cliff misbehaves)."""
    out = []
    for nm, e, inner in (('N', Z[0], Z[1]), ('S', Z[-1], Z[-2]), ('W', Z[:, 0], Z[:, 1]), ('E', Z[:, -1], Z[:, -2])):
        f = np.isfinite(e)
        out.append(f"{nm}: nan {int((~f).sum())}, z {np.nanmin(e) if f.any() else float('nan'):.1f}..{np.nanmax(e) if f.any() else float('nan'):.1f}, "
                   f"median {np.nanmedian(e) if f.any() else float('nan'):.1f}, >1 m below inner {int(np.sum((inner - e) > 1.0))}")
    log(f'edges ({label}): ' + ' | '.join(out))


def build_inputs(BOX, RES, S, TOK):
    from huggingface_hub import hf_hub_download
    if os.environ.get('LF_DATA_DIR'):    # local mirror of the HF data/ layout (Vermont: sim/colab/vt_inputs.py); nothing else changes
        hf_hub_download = lambda repo, f, **kw: os.path.join(os.environ['LF_DATA_DIR'], f)
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
    Z = np.nanmean(Z10[:ny * k, :nx * k].reshape(ny, k, nx, k), axis=(1, 3)).astype(np.float32)
    # highest 10 m cell in each RES cell: a road crest on fill is narrower than the cell and the mean smears it with the ditches beside it
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning); ZMAX10 = np.nanmax(Z10[:ny * k, :nx * k].reshape(ny, k, nx, k), axis=(1, 3)).astype(np.float32)
    del Z10
    edge_report(Z, 'raw DEM at RES'); log('row 0 (north edge) every 20th cell: ' + ' '.join(f'{v:.1f}' for v in Z[0, ::20]))
    log('row 1 every 20th cell: ' + ' '.join(f'{v:.1f}' for v in Z[1, ::20]))
    nod = np.isnan(Z); low = nod | (Z <= 0.3)
    lab, _ = ndimage.label(low); edge = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]); edge = edge[edge > 0]
    sea = np.isin(lab, edge); del lab
    inland_void = nod & ~sea
    if inland_void.any():
        fill = ndimage.grey_erosion(np.where(nod, 1e4, Z), size=7); Z = np.where(inland_void, fill, Z)
    Z = np.where(np.isnan(Z), -2.0, Z).astype(np.float32)
    # the lidar surface before any hydraulic edit (channel burn, crossing notches, depression breaching): the road crest for the freeboard rule
    # (proto/prototype.py).  Notches lower the road cells at crossings, so the model DEM must never be used for road height.
    Z_RAW = Z.copy(); ZMAX10 = np.where(np.isfinite(ZMAX10), np.maximum(ZMAX10, Z_RAW), Z_RAW).astype(np.float32)
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
    # LF_BREACH_SIZED=1: where the NAACC survey gives the culvert (shape, span, rise), the notch is sized to it (sized_notch): cut no deeper
    # than the surveyed invert (crest - fill - rise) and given the Manning n at which the 3x3-cell notch passes the HDS-5 capacity of the
    # real barrel(s); crossings without a size (and bridges) keep the default full opening.
    nb = 0; NOV = np.full((ny, nx), np.nan, np.float32); XG = []; nsized = 0
    if os.environ.get('LF_BREACH_XINGS', '1') == '1':
        try:
            SIZED = os.environ.get('LF_BREACH_SIZED', '0') == '1'
            xp = os.environ.get('LF_CROSSINGS') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'network', 'crossings_all.json')
            XJ = json.load(open(xp)); C = XJ['columns']; il, ia = C.index('lon'), C.index('lat')
            from pyproj import Transformer
            tf = Transformer.from_crs(4326, 26986, always_xy=True)
            rows_x = [dict(zip(C, r_)) for r_ in XJ['rows'] if r_[il] is not None]
            xx, yy = tf.transform([r_['lon'] for r_ in rows_x], [r_['lat'] for r_ in rows_x])
            kw = int(math.ceil(float(os.environ.get('LF_BREACH_M', '40')) / RES))
            Z, NOV, XG = open_crossings(Z, rows_x, xx, yy, BOX, RES, kw, SIZED); nb = len(XG); nsized = sum(1 for g in XG if g['n_eq'] is not None)
            log(f'crossings: {nb} road fills opened to the lowest ground within {kw * RES:.0f} m' + (f'; {nsized} sized to the NAACC culvert (LF_BREACH_SIZED)' if SIZED else ''))
        except Exception as e:
            log('crossing breach skipped:', repr(e)[:150])
    DAMS = None
    if os.environ.get('LF_DAMS', '0') == '1':      # opt-in: dams / mill ponds / lake outlets hold their pool (sim/colab/lf_dams.py)
        if SGC: log('LF_DAMS skipped: not set up for the sub-grid channel model (LF_SGC=1)')
        else:
            try:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lf_dams
                Z, water, DAMS = lf_dams.apply(Z, Z_RAW, ZMAX10, water, chan, CW, BOX, RES, log=log)
            except Exception as e:
                log('LF_DAMS failed, running without dams:', repr(e)[:300]); DAMS = None
    DOM = None
    if os.environ.get('LF_DOMAIN', 'box') == 'basin':  # opt-in watershed-shaped domain (sim/colab/lf_domain.py): cells outside the basin mask become walls before breaching
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lf_domain
        DOM = lf_domain.prepare(lf_domain.load(os.environ['LF_DOMAIN_FILE']), Z, BOX, RES, d4=os.environ.get('LF_BREACH_D4', '1') == '1', log=log)
        Z = np.where(DOM['mask'], Z, lf_domain.WALL).astype(np.float32)
    carved = np.zeros((ny, nx), bool)
    if os.environ.get('LF_BREACH_DEPRESSIONS', '1') == '1':
        t_ = time.time(); mcc = os.environ.get('LF_BREACH_CHAN_MAX')
        D4 = os.environ.get('LF_BREACH_D4', '1') == '1'     # carve 4-connected outlets (the solver's face fluxes; default since 22 Oct 2026); LF_BREACH_D4=0 restores the old 8-connected carving
        Z, carved, st_ = breach_depressions(Z, float(os.environ.get('LF_BREACH_MAX', '4')), chan if mcc else None, float(mcc) if mcc else None, d4=D4, protect=DAMS['protect'] if DAMS else None)
        log(f'depressions ({"4" if D4 else "8"}-connected): {st_["cells"]:,} cells carved (mean {st_["mean_cut_m"]} m, max {st_["max_cut_m"]} m), {st_["kept_deep"]} basins deeper than the cap kept'
            + (f', {st_["chan_deep_cut"]} channel pits cut deeper than the cap (LF_BREACH_CHAN_MAX={mcc})' if mcc else '') + f', {time.time() - t_:.0f}s')
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
        cp_ = os.path.join(os.environ['LF_MRMS_DIR'], os.path.basename(url)) if os.environ.get('LF_MRMS_DIR') else None   # optional cache (offline compute nodes)
        if cp_ and os.path.exists(cp_): raw_ = open(cp_, 'rb').read()
        else:
            raw_ = get(url).content
            if cp_: os.makedirs(os.environ['LF_MRMS_DIR'], exist_ok=True); open(cp_, 'wb').write(raw_)
        open(gp, 'wb').write(gzip.decompress(raw_))
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
    if os.environ.get('LF_RAIN_SCALE'):     # ensemble hook (proto/ensemble.py): storm-wide multiplicative radar-rain error; unset = MRMS as is
        RAIN = (RAIN * float(os.environ['LF_RAIN_SCALE'])).astype(np.float32); log(f"LF_RAIN_SCALE {os.environ['LF_RAIN_SCALE']}: MRMS rain multiplied")
    tot = RAIN.sum(0); log(f'rain: max {tot.max():.0f} mm, mean {tot.mean():.0f} mm over {len(hours)} h; missing {MISSING}')
    if tot.max() <= 0: raise SystemExit('no rain data at all; refusing to run a dry storm')
    RAIN_OBS = RAIN.copy()
    if loss is not None: RAIN = np.maximum(RAIN - loss[None], 0).astype(np.float32); log(f'effective rain mean {RAIN.sum(0).mean():.0f} mm')
    if CNG is not None:
        Sx = 25400.0 / np.maximum(CNG, 1.0) - 254.0; Ia = 0.2 * Sx; P = np.cumsum(RAIN, axis=0)
        Q = np.where(P > Ia, (P - Ia) ** 2 / np.maximum(P - Ia + Sx, 1e-6), 0.0)
        RAIN = np.diff(np.concatenate([np.zeros_like(Q[:1]), Q]), axis=0).astype(np.float32)
        log(f'effective rain (CN) mean {RAIN.sum(0).mean():.0f} mm of {RAIN_OBS.sum(0).mean():.0f} mm ({100 * RAIN.sum() / max(RAIN_OBS.sum(), 1):.0f}%)')
    return dict(Z=Z, sea=sea, water=water, chan=chan, burn=burn, IMP=IMP, RAIN=RAIN, rain_total=tot, missing=MISSING, ny=ny, nx=nx, RAIN_OBS=RAIN_OBS, carved=carved, CW=CW, CD=CD, SGC=SGC,
                NOV=NOV, XG=XG, Z_RAW=Z_RAW, ZMAX10=ZMAX10, DAMS=DAMS, DOM=DOM)


# ======================================================================================================================
def lf_dams_weirfile(D):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lf_dams; return lf_dams.weirfile(D)


def lf_dams_report(D, Zm, FR, FT):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lf_dams; return lf_dams.report(D, Zm, FR, FT)


def main():
    global LOGP
    import pandas as pd
    t_all = time.time(); os.makedirs(WORK, exist_ok=True); LOGP = f'{WORK}/w9_log.txt'
    BOX = tuple(float(v) for v in os.environ.get('BOX', '150000,905000,170000,925000').split(',')); RES = float(os.environ.get('RES', '20'))
    if os.environ.get('LF_DOMAIN', 'box') == 'basin': BOX = tuple(float(v) for v in json.load(open(os.environ['LF_DOMAIN_FILE']))['box'])   # the domain file sets the box
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
    if os.environ.get('LF_EXE'):      # offline compute nodes (proto/turing): a LISFLOOD-FP 8.2 built beforehand by setup_lisflood.sh; LF_EXE_CUDA=1 if it is the CUDA build
        exe, is_cuda, zp, ver, src_url = os.environ['LF_EXE'], os.environ.get('LF_EXE_CUDA', '0') == '1', os.environ['LF_EXE'], '8.2', 'https://doi.org/10.5281/zenodo.13121102'
    else:
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
    edge_report(I['Z'], 'model DEM'); log('model row 0 every 20th cell: ' + ' '.join(f'{v:.1f}' for v in I['Z'][0, ::20]))
    log(f"edge flags: sea N/S/W/E {int(I['sea'][0].sum())}/{int(I['sea'][-1].sum())}/{int(I['sea'][:, 0].sum())}/{int(I['sea'][:, -1].sum())}, "
        f"chan {int(I['chan'][0].sum())}/{int(I['chan'][-1].sum())}/{int(I['chan'][:, 0].sum())}/{int(I['chan'][:, -1].sum())}, "
        f"water {int(I['water'][0].sum())}/{int(I['water'][-1].sum())}/{int(I['water'][:, 0].sum())}/{int(I['water'][:, -1].sum())}, "
        f"rain total row 0 mean {float(I['RAIN'][:, 0].sum(0).mean()):.0f} mm vs box {float(I['RAIN'].sum(0).mean()):.0f} mm")
    if os.environ.get('LF_INPUTS_ONLY') == '1': log('LF_INPUTS_ONLY: stopping after the inputs'); return
    wd = f'{WORK}/run_{run_name}'; shutil.rmtree(wd, ignore_errors=True); os.makedirs(f'{wd}/results')
    DOM = I.get('DOM'); MSK = DOM['mask'] if DOM else None
    write_asc(f'{wd}/dem.asc', I['Z'] if DOM is None else np.where(MSK, I['Z'], np.nan), x0, y0, RES)     # LF_DOMAIN=basin: NODATA outside the mask (LISFLOOD-FP walls)
    LC = None
    if os.environ.get('LF_N_LANDCOVER', '0') == '1':
        LC, cov = nlcd_landcover(BOX, RES, ny, nx)
        if LC is None: log('LF_N_LANDCOVER=1 but NLCD land cover unavailable: floodplain n stays LF_N_FP')
        else: log(f'land cover {cov}: forest/woody wetland {np.isin(LC, NLCD_FOREST).mean() * 100:.0f}%, '
                  + ', '.join(f'{c} {(LC == c).mean() * 100:.0f}%' for c in (11, 21, 22, 23, 24, 52, 71, 81, 82, 95)))
    NM = manning_map(I['water'], I['chan'], I['IMP'], LC)
    log(f"Manning n: channel/water {os.environ.get('LF_N_CHAN', '0.035')}, land mean {float(NM[~(I['water'] | I['chan'])].mean()):.3f}")
    if np.isfinite(I['NOV']).any(): NM = np.where(np.isfinite(I['NOV']), np.maximum(NM, np.nan_to_num(I['NOV'])), NM).astype(np.float32)   # sized culvert notches
    write_asc(f'{wd}/n.asc', NM, x0, y0, RES, fmt='%.3f')
    rec, th = rain_records(I['RAIN'] / (scale if abs(scale - 1) > 0.2 else 1.0), P['convention'])
    write_rain_nc(f'{wd}/rain.nc', rec, x0, y0, RES, th, flip_y=P['flip_y'], flip_x=P['flip_x'])
    write_bci(f'{wd}/run.bci', x0, y0, x1, y1)
    if DOM: open(f'{wd}/run.bci', 'w').write('\n'.join(DOM['bci']) + '\n')     # FREE only where the outlet corridors reach the box edge; other edges closed
    start = None
    extra = []; infil_mmh = float(os.environ.get('LF_INFIL_MMH', '4'))
    INFLOW = None
    if os.environ.get('LF_INFLOW', 'none') == 'usgs':     # opt-in: upstream inflow point sources from USGS gauges (sim/colab/lf_inflow.py)
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import lf_inflow
            from pyproj import Transformer
            tg_ = Transformer.from_crs(4326, 26986, always_xy=True); gp_ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'proto', 'obs', f'gauges_{STORM}.json')
            gl_ = [g for g in (json.load(open(gp_))['gauges'] if os.path.exists(gp_) else []) if x0 <= tg_.transform(g['lon'], g['lat'])[0] < x1 and y0 <= tg_.transform(g['lon'], g['lat'])[1] < y1]
            INFLOW = lf_inflow.build_inflows(BOX, RES, I['Z'], I['chan'], S['t0'], S['hours'], gl_, log=log)
            if INFLOW['n']:
                with open(f'{wd}/run.bci', 'a') as f_: f_.write('\n'.join(INFLOW['bci_lines']) + '\n')
                open(f'{wd}/run.bdy', 'w').write(INFLOW['bdy']); extra.append('bdyfile run.bdy')
            log(f"LF_INFLOW=usgs: {INFLOW['n']} inflow point sources")
        except Exception as e:
            log('LF_INFLOW failed, running without inflows:', repr(e)[:300])
    elif os.environ.get('LF_INFLOW') == 'file':    # opt-in: edge inflows from a coarse run of this model (one-way nesting, sim/colab/vt_inputs.py)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import vt_inputs
        bl_, bdy_, cells_ = vt_inputs.point_sources(json.load(open(os.environ['LF_INFLOW_FILE'])), I['Z'], I['chan'], BOX, RES)
        if bl_:
            with open(f'{wd}/run.bci', 'a') as f_: f_.write('\n'.join(bl_) + '\n')
            open(f'{wd}/run.bdy', 'w').write(bdy_); extra.append('bdyfile run.bdy')
        INFLOW = dict(n=len(bl_), report=dict(source='file', file=os.environ['LF_INFLOW_FILE'], cells=cells_)); log(f'LF_INFLOW=file: {len(bl_)} inflow point sources at {cells_[:8]}')
    QOUT = os.environ.get('LF_QOUT', '0') == '1'
    if QOUT: extra.append('qoutput')          # .Qx/.Qy face fluxes (m3/s) at every saveint: flow through each crossing notch, river flow at gauges
    VOUT = os.environ.get('LF_VOUT', '0') == '1'
    if VOUT: extra.append('hazard')           # voutput + voutput_max + hazard (pars.cpp): .Vx/.Vy (m/s) per saveint, .maxVc/.maxVcd/.maxHaz at the end
    for k_, kw_ in (('LF_THETA', 'theta'), ('LF_CFL', 'cfl')):     # opt-in solver stability: theta < 1 = q-centred diffusion (de Almeida et al. 2012 suggest 0.7), cfl default 0.7
        if os.environ.get(k_): extra.append(f'{kw_} {float(os.environ[k_]):g}')
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
    if I.get('DAMS'):        # LF_DAMS: lakes start full at their pool level (overrides the channel start depth there); native weirs at the outlets
        D_ = I['DAMS']; st0 = read_asc(f'{wd}/start.wd')[0] if start else np.zeros((ny, nx), np.float32)
        write_asc(f'{wd}/start.wd', np.where(D_['start'] > 0, D_['start'], np.nan_to_num(st0)), x0, y0, RES); start = 'start.wd'
        if D_['weirs']:
            open(f'{wd}/run.weir', 'w').write(lf_dams_weirfile(D_)); extra.append('weirfile run.weir')
            if is_cuda: log('WARNING: LF_DAMS weirs are read by the CPU solver (fp_flow.cpp); the CUDA acceleration solver may ignore them')
        extra += D_.get('par', [])
    for k_ in ('theta', 'cfl'):     # LF_THETA / LF_CFL: solver damping on its own (de Almeida et al. 2012); after LF_DAMS's so an explicit value wins
        if os.environ.get('LF_' + k_.upper()): extra.append(f"{k_} {os.environ['LF_' + k_.upper()]}")
    if DOM and start: write_asc(f'{wd}/start.wd', np.where(MSK, np.nan_to_num(read_asc(f'{wd}/start.wd')[0]), 0.0), x0, y0, RES)   # no water on wall cells
    par = write_par(f'{wd}/run.par', 'res', S['hours'] * 3600, saveint=SAVEINT, cuda=is_cuda, manning='n.asc', rain='rain.nc', bci='run.bci', start=start,
                    infiltration=infil_mmh / 3.6e6 if infil_mmh > 0 else None, extra=extra)
    log('par:', ' | '.join(par))
    # 4. run
    run_s, out = run_lisflood(exe, wd, 'run.par'); log(f'LISFLOOD-FP run {run_s:.0f}s'); log(out[-1200:])
    hmax, hsrc = max_depth(wd, 'res'); hmax = np.nan_to_num(hmax, nan=0.0)
    if DOM and hmax.shape == MSK.shape: hmax = np.where(MSK, hmax, 0.0)
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
    # flow through every crossing notch and past every gauge from the face fluxes (LF_QOUT=1): peak over the snapshots
    XG = I['XG']; GQ = []
    gp_ = os.environ.get('LF_GAUGES') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs', 'proto', 'obs', f'gauges_{STORM}.json')
    if os.path.exists(gp_):
        from pyproj import Transformer
        tg = Transformer.from_crs(4326, 26986, always_xy=True)
        for g in json.load(open(gp_))['gauges']:
            gx, gy = tg.transform(g['lon'], g['lat'])
            if x0 <= gx < x1 and y0 <= gy < y1:
                rg, cg = int((y1 - gy) // RES), int((gx - x0) // RES); kg = max(2, int(math.ceil(100 / RES)))
                GQ.append(dict(site=g['site'], name=g['name'], r0=max(0, rg - kg), r1=min(ny, rg + kg + 1), c0=max(0, cg - kg), c1=min(nx, cg + kg + 1),
                               obs_peak_q_m3s=round(g['peak_q_cfs'][1] * 0.0283168, 1) if g.get('peak_q_cfs') else None))
    qfiles = sorted(glob.glob(f'{wd}/results/res-*.Qx'))
    if QOUT and qfiles:
        t_ = time.time()
        for B in XG: B.update(q_peak_m3s=0.0, q_peak_h=None)
        for B in GQ: B.update(q_peak_m3s=0.0, q_peak_h=None, q_series=[])
        for fq in qfiles:
            j = int(re.search(r'-(\d+)\.Qx$', fq).group(1)); fy = fq[:-3] + '.Qy'
            if not os.path.exists(fy): continue
            try: Qx = np.nan_to_num(read_asc(fq)[0]); Qy = np.nan_to_num(read_asc(fy)[0])
            except Exception as e: log('flux file unreadable', fq, repr(e)[:80]); continue
            if Qx.shape != (ny, nx + 1) or Qy.shape != (ny + 1, nx): log('unexpected flux grid shapes', Qx.shape, Qy.shape); break
            for B in XG + GQ:
                qi, qo = block_throughflow(Qx, Qy, B['r0'], B['r1'], B['c0'], B['c1']); q = 0.5 * (qi + qo)
                if 'q_series' in B: B['q_series'].append(round(qo, 2))
                if j > 0 and q > B['q_peak_m3s']: B['q_peak_m3s'] = round(q, 3); B['q_peak_h'] = round(j * SAVEINT / 3600.0, 2)   # j = 0: start-file transient (channels start a third full), not flow
            os.remove(fq); os.remove(fy)
        log(f'fluxes: {len(qfiles)} snapshots read in {time.time() - t_:.0f}s; gauge peak flow ' + ', '.join(f"{g['site']} {g['q_peak_m3s']:.1f} m3/s (obs {g['obs_peak_q_m3s']})" for g in GQ))
    VEL = None
    if VOUT:
        try:
            t_ = time.time(); vmx, dvmx, vinfo = velocity_peaks(wd, 'res', (ny, nx)); vdur = vinfo.pop('_vdur', {})
            VEL = dict(vmax=vmx, dvmax=dvmx, **{k: str(v) for k, v in vinfo.items()}, **vdur)
            if vdur: VEL['vdur_saveint_s'] = np.array(SAVEINT)
            wetv = hmax >= 0.1
            log(f"velocity ({vinfo}): peak speed on wet land p50/p95/max {np.percentile(vmx[wetv & land], 50) if (wetv & land).any() else 0:.2f}/"
                f"{np.percentile(vmx[wetv & land], 95) if (wetv & land).any() else 0:.2f}/{vmx.max():.2f} m/s, peak dv max {dvmx.max():.2f} m2/s, {time.time() - t_:.0f}s")
        except Exception as e:
            log('velocity output unreadable:', repr(e)[:200])
    mass = sorted(glob.glob(f'{wd}/results/res.mass'))
    mass_tail = open(mass[0]).read().strip().split('\n')[-2:] if mass else []
    # 5. run layout + one commit
    OUT = f'{wd}/out'; os.makedirs(OUT, exist_ok=True)
    np.save(f'{OUT}/hmax.npy', hmax.astype(np.float32)); np.save(f'{OUT}/z.npy', (I['Z'] if DOM is None else np.where(MSK, I['Z'], I['Z_RAW'])).astype(np.float32))
    if hsnap is not None: np.save(f'{OUT}/hsnap.npy', hsnap.astype(np.float32))
    if FR: np.savez_compressed(f'{OUT}/frames_cm.npz', depth_cm=np.stack(FR), hours=np.array(FT, np.float32))
    np.save(f'{OUT}/watermask.npy', (I['water'] | I['chan'] | I['carved']).astype(np.uint8))
    np.savez_compressed(f'{OUT}/z_raw.npz', z_raw=I['Z_RAW'], z_raw_max10=I['ZMAX10'],
                        note='lidar DEM at RES before channel burn / crossing notches / depression breaching (m); z_raw_max10 = highest 10 m cell in each cell')
    if VEL is not None: np.savez_compressed(f'{OUT}/vel_max.npz', **VEL)
    np.savez_compressed(f'{OUT}/timing.npz', tover15=tover15, tover30=tover30, tarr30=tarr30, saveint_s=SAVEINT)
    R = I['RAIN_OBS']; r3 = np.stack([R[i:i + 3].sum(0) for i in range(max(1, len(R) - 2))])
    np.savez_compressed(f'{OUT}/rainstats.npz', total=R.sum(0), peak1h=R.max(0), peak3h=r3.max(0), hour_of_peak=R.argmax(0).astype(np.int16),
                        hourly_mean=R.reshape(len(R), -1).mean(1), hourly_max=R.reshape(len(R), -1).max(1))
    json.dump(dict(note='crossing notches: block rows r0..r1-1, cols c0..c1-1; zmin lowest ground within LF_BREACH_M, zcrest highest DEM cell of the block before the cut, '
                        'zcut notch level, n_eq Manning n of a sized notch (LF_BREACH_SIZED), q_peak_m3s peak flow through the block (LF_QOUT, 30-min snapshots)',
                   sized=os.environ.get('LF_BREACH_SIZED', '0') == '1', qout=QOUT, crossings=XG, gauges=GQ), open(f'{OUT}/xings.json', 'w'))
    for f in ('run.par', 'run.bci', 'lisflood_stdout.txt'): shutil.copy(f'{wd}/{f}', f'{OUT}/{f}')
    if os.path.exists(f'{wd}/run.bdy'): shutil.copy(f'{wd}/run.bdy', f'{OUT}/run.bdy')
    if mass: shutil.copy(mass[0], f'{OUT}/lisflood.mass')
    meta = dict(run=run_name, title=S['title'] + ' · LISFLOOD-FP benchmark', box=list(BOX), res_m=RES, shape=[ny, nx], t0=S['t0'], frame_min=S['frame_min'], frames=frames,
                crs='EPSG:26986', model=model, model_source=src_url, model_build=dict(cuda=bool(is_cuda), exe=os.path.basename(exe), build_s=round(build_s)),
                solver='acceleration (local inertial, Bates et al. 2010)' + (' on GPU (cuda)' if is_cuda else ' on CPU (OpenMP)'),
                inputs=dict(dem='HF data/dem10 averaged to RES', channels=os.environ.get('LF_CHAN', 'vol'), manning=f"{os.environ.get('LF_N_CHAN', '0.035')} water/channel, 0.10 dense urban, " + ('NLCD table (forest ' + os.environ.get('LF_N_FOREST', '0.12') + ')' if LC is not None else os.environ.get('LF_N_FP', '0.08') + ' other'),
                            rain='MRMS MultiSensor QPE 01H Pass2 -> TUFLOW NetCDF dynamicrainfile', loss=os.environ.get('LF_LOSS', 'none'),
                            boundary='FREE on all edges', baseflow=start is not None, inflows=INFLOW['report'] if INFLOW else 'none',
                            env={k: os.environ[k] for k in sorted(os.environ) if k.startswith('LF_') and k not in ('LF_WORK',)}),
                rain_probe=P, hmax_source=hsrc, rain_total_max_mm=round(float(I['rain_total'].max())), rain_total_mean_mm=round(float(I['rain_total'].mean())),
                rain_missing_hours=I['missing'], runtime_s=round(run_s), total_s=round(time.time() - t_all), peak_wet_km2=peak_wet, peak_snapshot_wet_km2=peak_frame_wet,
                mass_tail=mass_tail, git_sha=os.environ.get('GIT_SHA', '')[:8])
    if I.get('DAMS'):
        try: meta['dams'] = lf_dams_report(I['DAMS'], I['Z'], FR, FT)
        except Exception as e: log('dam report failed:', repr(e)[:200])
    if DOM:
        meta['domain'] = DOM['report']; meta['inputs']['boundary'] = 'LF_DOMAIN=basin: NODATA walls outside the mask, FREE on the outlet corridor edge cells, other edges closed'
        np.save(f'{OUT}/domain_mask.npy', MSK.astype(np.uint8))
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
    lc = np.full((ny, nx), 43, np.uint8); lc[:, 0] = 81; nl = manning_map(water, chan, imp, lc)
    assert nl[4, 1] == np.float32(0.12) and nl[4, 0] == np.float32(0.035) and nl[0, 1] == np.float32(0.10) and nl[2, 1] == np.float32(0.035)
    ok.append('Manning map with NLCD land cover (forest 0.12, pasture 0.035, paved and water unchanged)')
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
    assert f.variables['time'].units in (b'hours', 'hours') and np.all(np.diff(y) < 0) and np.all(np.diff(x) > 0)
    assert abs(y[0] - (y0 + (ny - 0.5) * res)) < 1e-6 and abs(x[0] - (x0 + res / 2)) < 1e-6 and abs(y[-1] - (y0 + res / 2)) < 1e-6
    vv = v[:].copy(); assert vv[0, 0, 0] == 10 and vv[0, -1, :].sum() == 0 and vv[2, 0, 3] == 30   # northern row = first row = largest y
    assert np.allclose(f.variables['total_rainfall_depth'][:][0, :], 60) and list(t) == [0, 1, 2, 3]
    # emulate LISFLOOD-FP DynamicRain::rate_at_cell: every DEM row j must map to file row j (in range, same y)
    gdy = y[0] - y[1]; gtly = y[0] + gdy / 2; ptly = y0 + ny * res
    tj = [int((j - (ptly - gtly) / res) * res / gdy) for j in range(ny)]
    assert gdy > 0 and tj == list(range(ny)) and abs((gtly - ny * gdy) - y0) < 1e-6
    f.close(); ok.append('rain NetCDF (y descending, LISFLOOD row mapping j -> j in range, hourly mm, interval-start stamps)')
    write_rain_nc(f'{d}/rain_f.nc', rec, x0, y0, res, th, flip_y=True)
    f = netcdf_file(f'{d}/rain_f.nc', 'r', mmap=False); assert f.variables['rainfall_depth'][:][0, -1, 0] == 10; f.close(); ok.append('rain flip_y option')
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
    # crossing notches sized to the culvert (LF_BREACH_SIZED) and flow through a block from face fluxes (LF_QOUT)
    small = dict(shape='circular', rise_m=0.6, span_m=0.6, fill_m=1.0, material='concrete', inlet='headwall')
    big = dict(shape='box', rise_m=3.0, span_m=6.0, fill_m=1.0, material='concrete', inlet='wingwall')
    zc_s, n_s = sized_notch(small, 100.0, 103.0, 20.0); zc_b, n_b = sized_notch(big, 100.0, 103.0, 20.0)
    assert abs(zc_s - 101.4) < 1e-6 and zc_b == 100.0 and n_s > 1.0 and n_b < n_s and 0.035 <= n_b
    assert sized_notch(dict(shape='bridge', rise_m=2, span_m=10), 100, 103, 20) is None and sized_notch(dict(shape=None), 100, 103, 20) is None
    assert sized_notch(dict(small, fill_m=None), 100.0, 103.0, 20.0)[0] == 100.0
    two = sized_notch(dict(small, n_barrels=2), 100.0, 103.0, 20.0)[1]; assert abs(two - n_s / 2) / n_s < 0.02 or two == 0.035
    ok.append('sized crossing notch (invert cap from fill + rise, HDS-5-equivalent Manning n; bridges / unknown sizes keep the default)')
    Qx = np.zeros((5, 6)); Qy = np.zeros((6, 5)); Qx[2, :] = 3.0          # 3 m3/s eastwards along row 2
    assert block_throughflow(Qx, Qy, 1, 4, 1, 4) == (3.0, 3.0)
    Qy[:, 2] = -2.0; Qx[:] = 0                                              # 2 m3/s northwards along column 2
    assert block_throughflow(Qx, Qy, 1, 4, 1, 4) == (2.0, 2.0); ok.append('flow through a block from LISFLOOD-FP face fluxes')
    Zr = np.full((20, 20), 103.0, np.float32); Zr[:, 10] = 100.0                     # stream along column 10 under a road fill on row 5
    Zr[4:7, :] = 104.0
    rows_x = [dict(id='a', **small), dict(id='b', shape='bridge', rise_m=2.0, span_m=8.0), dict(id='out')]
    xs_ = [150000 + 10.5 * 20, 150000 + 10.5 * 20, 140000]; ys_ = [905400 - 5.5 * 20, 905400 - 5.5 * 20, 905000]
    Zd, Nd, Gd = open_crossings(Zr, rows_x, xs_, ys_, (150000, 905000, 150400, 905400), 20.0, 2, False)
    assert len(Gd) == 2 and Zd[5, 10] == 100.0 and Zd[4:7, 9:12].max() == 100.0 and np.isnan(Nd).all() and Zr[5, 10] == 104.0
    Zs, Ns, Gs = open_crossings(Zr, rows_x, xs_, ys_, (150000, 905000, 150400, 905400), 20.0, 2, True)
    assert Gs[0]['n_eq'] is not None and Gs[1]['n_eq'] is None and abs(Zs[5, 10] - 100.0) < 1e-6         # bridge on top keeps the full opening
    Zs, Ns, Gs = open_crossings(Zr, rows_x[:1], xs_[:1], ys_[:1], (150000, 905000, 150400, 905400), 20.0, 2, True)
    assert abs(Zs[5, 10] - (104.0 - 1.6)) < 1e-5 and np.isfinite(Ns[4:7, 9:12]).all() and Gs[0]['zcut'] == 102.4
    ok.append('crossing notches: default full opening, sized notch only where the survey gives a culvert')
    # channel pits may be cut deeper than the cap (LF_BREACH_CHAN_MAX)
    Zp = np.full((7, 9), 20.0, np.float32); Zp[3, :] = [20, 10, 10, 10, 16, 9, 9, 9, 8]   # river along row 3, a 6 m road fill at column 4
    ch = np.zeros_like(Zp, bool); ch[3, :] = True
    Zk, low_k, st_k = breach_depressions(Zp, 4.0); assert Zk[3, 4] == 16 and st_k['kept_deep'] >= 1
    Zc_, low_c, st_c = breach_depressions(Zp, 4.0, ch, 12.0); assert Zc_[3, 4] <= 10 and st_c['chan_deep_cut'] >= 1
    ok.append('channel pits behind a fill deeper than the cap are carved with LF_BREACH_CHAN_MAX, kept without it')
    # LF_BREACH_D4: a pit whose only low exit is a corner-to-corner step is closed for the face-flux solver; d4 carves a face-connected outlet
    Zq = np.full((5, 5), 7.0, np.float32); Zq[2, 2] = 5.0; Zq[3, 3] = 4.0; Zq[4, 4] = 3.0     # pit (2,2) drains diagonally to the SE corner
    Z8, _, _ = breach_depressions(Zq, 4.0); Z4, low4, _ = breach_depressions(Zq, 4.0, d4=True)
    assert Z8[2, 3] == 7 and Z8[3, 2] == 7                                       # 8-connected: no face-connected outlet carved
    assert min(Z4[2, 3], Z4[3, 2]) <= 5.0 and low4.any()                            # 4-connected: a face neighbour is cut to the pit level
    ok.append('LF_BREACH_D4 carves face-connected (4-neighbour) outlets; 8-connected carving leaves corner-only exits')
    # velocity output (LF_VOUT): cell speed as LISFLOOD-FP's UpdateV, peaks from snapshots and from .maxVc / .maxVcd
    Vx = np.zeros((2, 4)); Vy = np.zeros((3, 3)); Vx[0, 1] = -3.0; Vx[0, 2] = 1.0; Vy[1, 0] = 4.0
    sp = cell_speed(Vx, Vy); assert abs(sp[0, 0] - 5.0) < 1e-6 and abs(sp[0, 1] - 3.0) < 1e-6 and abs(sp[1, 0] - 4.0) < 1e-6 and sp[1, 2] == 0
    vd = f'{d}/vel'; os.makedirs(f'{vd}/results'); g = (2, 3)
    for j, (u, hh) in enumerate(((1.0, 0.2), (2.0, 0.5), (0.5, 1.0))):
        write_asc(f'{vd}/results/res-{j:04d}.Vx', np.full((2, 4), u), x0, y0, res); write_asc(f'{vd}/results/res-{j:04d}.Vy', np.zeros((3, 3)), x0, y0, res)
        write_asc(f'{vd}/results/res-{j:04d}.wd', np.full(g, hh), x0, y0, res)
    vm, dvm, inf_ = velocity_peaks(vd, 'res', g)
    assert np.allclose(vm, 2.0) and np.allclose(dvm, 1.0) and inf_['snapshots'] == 3 and inf_['vmax_source'] == 'max of snapshots' and not glob.glob(f'{vd}/results/*.Vx')
    write_asc(f'{vd}/results/res.maxVc', np.full(g, 2.5), x0, y0, res); write_asc(f'{vd}/results/res.maxVcd', np.full(g, 0.6), x0, y0, res)
    vm, dvm, inf_ = velocity_peaks(vd, 'res', g); assert np.allclose(vm, 2.5) and np.allclose(dvm, 1.5) and inf_['vmax_source'].startswith('maxVc')
    for j, (u, hh) in enumerate(((1.0, 0.2), (2.0, 0.5), (0.5, 1.0))):     # LF_VDUR: snapshots at or above each speed (with depth >= 0.02 m)
        write_asc(f'{vd}/results/res-{j:04d}.Vx', np.full((2, 4), u), x0, y0, res); write_asc(f'{vd}/results/res-{j:04d}.Vy', np.zeros((3, 3)), x0, y0, res)
    os.environ['LF_VDUR'] = '1.0,1.5'; _, _, inf_ = velocity_peaks(vd, 'res', g); del os.environ['LF_VDUR']
    assert inf_['_vdur']['vdur_count'][:, 0, 0].tolist() == [2, 1] and int(inf_['_vdur']['vdur_snapshots']) == 3
    assert 'hazard' in write_par(f'{d}/v.par', 'r', 60, extra=['hazard'])
    ok.append('velocity output: UpdateV cell speed, peak speed (.maxVc else snapshots), peak depth x speed')
    shutil.rmtree(d)
    for o in ok: print('ok  ', o)
    print(f'SELFTEST PASSED ({len(ok)} checks)')


if __name__ == '__main__':
    if '--selftest' in sys.argv: selftest()
    else: main()
