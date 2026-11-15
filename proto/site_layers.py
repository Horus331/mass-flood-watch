"""Real data layers for the site's "How it works" figure (one 20 x 20 km box, the Leominster catalogue box).

    python proto/site_layers.py fetch --surr surr.npz --out drafts/layers/data     # on a GitHub runner (needs the network)

Inputs: the model's own input pack (sim/colab/w9_lisflood.py with LF_SURR_SAVE=1: lidar DEM, curve number, impervious share,
water / channel masks, hourly MRMS rain), plus NLCD 2021 land-cover classes (MRLC WCS) and a USGS NAIP aerial image
(USGS The National Map image service). Writes small files only (float16 / uint8, compressed).
"""
import argparse, io, json, os, sys, time
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = (162000, 908000, 182000, 928000)     # EPSG:26986, the Leominster catalogue box


def naip(box, px, out):
    """Aerial image; large requests are fetched as a grid of tiles of at most 2000 px and stitched (the service times out on bigger ones)."""
    if px > 2000:
        from PIL import Image
        n = int(np.ceil(px / 2000)); t = px // n; x0, y0, x1, y1 = box; dx, dy = (x1 - x0) / n, (y1 - y0) / n; canvas = Image.new('RGB', (t * n, t * n)); src = None
        for j in range(n):
            for i in range(n):
                b = (x0 + i * dx, y1 - (j + 1) * dy, x0 + (i + 1) * dx, y1 - j * dy); tmp = out + f'.{i}{j}.jpg'
                src = naip1(b, t, tmp)
                if not src: return None
                canvas.paste(Image.open(tmp).convert('RGB').resize((t, t)), (i * t, j * t)); os.remove(tmp)
        canvas.save(out, quality=92); return src
    return naip1(box, px, out)


def naip1(box, px, out):
    import requests
    x0, y0, x1, y1 = box
    for u in ('https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPImagery/ImageServer/exportImage',
              'https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer/exportImage'):
        q = dict(bbox=f'{x0},{y0},{x1},{y1}', bboxSR=26986, imageSR=26986, size=f'{px},{px}', format='jpg', f='image')
        try:
            r = requests.get(u, params=q, timeout=300)
            if r.status_code != 200: time.sleep(5); r = requests.get(u, params=q, timeout=300)
            if r.status_code == 200 and r.content[:3] == b'\xff\xd8\xff':
                open(out, 'wb').write(r.content); return u
            print('naip: bad response', u, r.status_code, r.content[:120])
        except Exception as e:
            print('naip: failed', u, repr(e)[:120])
    return None


def dem_fine(box, res, out):
    """USGS 3DEP bare-earth elevation (best available, 1 m lidar here) resampled to `res` m by the USGS image service."""
    import requests, tifffile
    x0, y0, x1, y1 = box; nx, ny = int(round((x1 - x0) / res)), int(round((y1 - y0) / res))
    u = 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage'
    q = dict(bbox=f'{x0},{y0},{x1},{y1}', bboxSR=26986, imageSR=26986, size=f'{nx},{ny}', format='tiff', pixelType='F32',
             interpolation='RSP_BilinearInterpolation', noData=-9999, f='image')
    for k in range(3):
        try:
            r = requests.get(u, params=q, timeout=300)
            if r.status_code == 200 and r.content[:2] in (b'II', b'MM'):
                z = tifffile.imread(io.BytesIO(r.content)).astype(np.float32)
                z = np.where(z < -1000, np.nan, z)
                np.savez_compressed(out, z=z.astype(np.float32), res_m=np.float32(res)); return dict(src=u, res_m=res, shape=list(z.shape), nan=int(np.isnan(z).sum()))
            print('dem: bad response', r.status_code, r.content[:200])
        except Exception as e:
            print('dem: failed', repr(e)[:200])
    return None


def osm_buildings(box, out):
    """Building footprints with height (m) from OpenStreetMap (Overpass API): height tag, else building:levels x 3.5 m, else 8 m."""
    import requests
    from pyproj import Transformer
    tr = Transformer.from_crs(26986, 4326, always_xy=True); x0, y0, x1, y1 = box
    lo0, la0 = tr.transform(x0, y0); lo1, la1 = tr.transform(x1, y1)
    q = f'[out:json][timeout:120];(way["building"]({la0},{lo0},{la1},{lo1}););out geom tags;'
    for u in ('https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter'):
        try:
            r = requests.post(u, data=dict(data=q), timeout=200, headers={'User-Agent': 'mass-flood-watch research site (github.com/Horus331/mass-flood-watch)', 'Accept': '*/*'})
            if r.status_code != 200: print('osm: bad response', u, r.status_code); continue
            B = []
            for e in r.json().get('elements', []):
                g = e.get('geometry') or []
                if len(g) < 4: continue
                t = e.get('tags', {}); h = None
                try: h = float(str(t.get('height', '')).replace('m', '').strip())
                except ValueError: h = None
                if not h:
                    try: h = float(t.get('building:levels')) * 3.5
                    except (TypeError, ValueError): h = None
                B.append(dict(h=round(h or 8.0, 1), hs='tag' if t.get('height') else ('levels' if t.get('building:levels') else 'default'),
                              n=t.get('name', ''), p=[[round(p['lon'], 6), round(p['lat'], 6)] for p in g]))
            json.dump(dict(src=u, license='© OpenStreetMap contributors (ODbL)', buildings=B), open(out, 'w'))
            return dict(src=u, n=len(B))
        except Exception as e:
            print('osm: failed', u, repr(e)[:200])
    return None


def fetch(a):
    sys.path.insert(0, f'{ROOT}/sim/colab')
    import w9_lisflood as W
    os.makedirs(a.out, exist_ok=True)
    S = np.load(a.surr); meta = json.loads(str(S['meta']))
    ny, nx = meta['shape']; box = tuple(meta['box']); res = meta['res_m']
    rain = S['rain'].astype(np.float32)                    # hourly mm, block means of `rain_coarsen` cells
    lc, cov = W.nlcd_landcover(box, res, ny, nx)
    np.savez_compressed(f'{a.out}/layers.npz', z_raw=S['z_raw'].astype(np.float16), z=S['z'].astype(np.float16), cn=S['cn'],
                        imp=S['imp'], mask=S['mask'], rain_total=rain.sum(0).astype(np.float16), rain_hourly_mean=rain.mean(axis=(1, 2)).astype(np.float32),
                        nlcd=(lc if lc is not None else np.zeros((ny, nx), np.uint8)))
    src = naip(box, a.px, f'{a.out}/naip.jpg')
    dem = dem_fine(box, a.dem_res, f'{a.out}/dem_fine.npz') if a.dem_res else None
    bld = osm_buildings(box, f'{a.out}/buildings.json') if a.buildings else None
    info = dict(box=list(box), crs='EPSG:26986', res_m=res, shape=[ny, nx], t0=meta['t0'], hours=meta['hours'], rain_src=meta.get('rain_src'),
                rain_coarsen=int(S['rain_coarsen']), nlcd=cov, naip=src, dem_fine=dem, buildings=bld, env=meta.get('env'), git_sha=meta.get('git_sha'),
                made_by='proto/site_layers.py fetch')
    json.dump(info, open(f'{a.out}/layers.json', 'w'), indent=1); print(json.dumps(info, indent=1))


# ------------------------------------------------------------------------------------------------ render (runs anywhere, no network)
NLCD_RGB = {11: (122, 164, 206), 12: (226, 234, 245), 21: (233, 221, 214), 22: (220, 182, 168), 23: (198, 128, 116), 24: (150, 74, 70),
            31: (196, 190, 178), 41: (132, 182, 118), 42: (66, 122, 82), 43: (164, 196, 140), 52: (208, 196, 150), 71: (226, 228, 196),
            81: (222, 218, 128), 82: (196, 150, 96), 90: (170, 206, 214), 95: (132, 178, 196)}   # NLCD legend hues, softened for print
NLCD_NAME = {11: 'Open water', 21: 'Developed, open space', 22: 'Developed, low', 23: 'Developed, medium', 24: 'Developed, high',
             31: 'Barren', 41: 'Deciduous forest', 42: 'Evergreen forest', 43: 'Mixed forest', 52: 'Shrub', 71: 'Grassland',
             81: 'Pasture', 82: 'Crops', 90: 'Woody wetland', 95: 'Herbaceous wetland'}


def hillshade(z, res, az=315.0, alt=40.0, zf=2.0):
    gy, gx = np.gradient(z.astype(np.float32) * zf, res)
    slope = np.pi / 2 - np.arctan(np.hypot(gx, gy)); aspect = np.arctan2(-gx, gy)
    a, b = np.radians(az), np.radians(alt)
    return np.clip(np.sin(b) * np.sin(slope) + np.cos(b) * np.cos(slope) * np.cos(a - np.pi / 2 - aspect), 0, 1)


def ramp(stops, v):
    """stops: [(t, (r,g,b)), ...] with t in 0..1; v array in 0..1 -> uint8 rgb."""
    t = np.array([s[0] for s in stops]); c = np.array([s[1] for s in stops], np.float32)
    out = np.stack([np.interp(v, t, c[:, k]) for k in range(3)], -1)
    return np.clip(out, 0, 255).astype(np.uint8)


def up(a, n, order=1):
    from PIL import Image
    if a.dtype == np.uint8 and a.ndim == 3: return np.asarray(Image.fromarray(a).resize((n, n), Image.LANCZOS))
    im = Image.fromarray(a.astype(np.float32)); return np.asarray(im.resize((n, n), Image.BILINEAR if order else Image.NEAREST))


def render(a):
    from PIL import Image, ImageDraw
    from pyproj import Transformer
    os.makedirs(a.out, exist_ok=True)
    L = np.load(f'{a.data}/layers.npz'); info = json.load(open(f'{a.data}/layers.json'))
    x0, y0, x1, y1 = info['box']; res = info['res_m']; N = a.size
    z = L['z_raw'].astype(np.float32); z = np.where(np.isfinite(z), z, np.nanmin(z))
    hs = hillshade(z, res); hsN = up(hs, N); mask = L['mask']; zN = up(z, N)
    water = up(((mask & 1) > 0).astype(np.float32), N) > 0.5; chan = up(((mask & 2) > 0).astype(np.float32), N) > 0.35
    meta = dict(box=info['box'], size=N, layers={})
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    pix = lambda X, Y: ((np.asarray(X) - x0) / (x1 - x0) * N, (y1 - np.asarray(Y)) / (y1 - y0) * N)

    def save(name, rgb, **m):
        Image.fromarray(rgb).save(f'{a.out}/{name}.jpg', quality=88); meta['layers'][name] = m

    # 1 aerial
    if os.path.exists(f'{a.data}/naip.jpg'):
        im = Image.open(f'{a.data}/naip.jpg').convert('RGB').resize((N, N), Image.LANCZOS); save('aerial', np.asarray(im), src=info.get('naip'))
    # 2 land cover
    lc = L['nlcd']; lcN = np.asarray(Image.fromarray(lc).resize((N, N), Image.NEAREST))
    rgb = np.full((N, N, 3), 240, np.uint8)
    for k, c in NLCD_RGB.items(): rgb[lcN == k] = c
    present = [int(k) for k, n in zip(*np.unique(lc, return_counts=True)) if k in NLCD_NAME and n > 0.004 * lc.size]
    save('landcover', (rgb * (0.82 + 0.18 * hsN[..., None])).astype(np.uint8), classes=[[k, NLCD_NAME[k], '#%02x%02x%02x' % NLCD_RGB[k]] for k in present])
    # 3 runoff potential (curve number)
    cn = L['cn'].astype(np.float32); cnN = up(cn, N)
    lo, hi = 40.0, 98.0
    rgb = ramp([(0, (245, 241, 230)), (0.35, (226, 200, 150)), (0.65, (196, 132, 82)), (0.85, (150, 78, 52)), (1, (92, 44, 40))], np.clip((cnN - lo) / (hi - lo), 0, 1))
    rgb = (rgb * (0.85 + 0.15 * hsN[..., None])).astype(np.uint8); rgb[water | chan] = (150, 184, 216)
    save('runoff', rgb, lo=lo, hi=hi)
    # 4 terrain + streams + water + crossings
    zl, zh = np.percentile(z, 1), np.percentile(z, 99)
    tint = ramp([(0, (196, 214, 186)), (0.4, (222, 220, 190)), (0.75, (214, 196, 166)), (1, (236, 232, 226))], np.clip((zN - zl) / (zh - zl), 0, 1)).astype(np.float32)
    rgb = tint * (0.45 + 0.65 * hsN[..., None]); rgb[water] = (120, 168, 214); rgb[chan & ~water] = (58, 120, 190)
    rgb = np.clip(rgb, 0, 255).astype(np.uint8); im = Image.fromarray(rgb); d = ImageDraw.Draw(im)
    X = json.load(open(f'{ROOT}/docs/network/crossings_all.json')); ci = {c: i for i, c in enumerate(X['columns'])}
    nx_ = 0
    for r in X['rows']:
        if r[ci['lon']] is None: continue
        px, py = pix(*tr.transform(r[ci['lon']], r[ci['lat']]))
        if 0 <= px < N and 0 <= py < N:
            rr = max(3, N // 300); d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(255, 255, 255), outline=(25, 70, 130), width=max(2, N // 600)); nx_ += 1
    save('terrain', np.asarray(im), zmin=round(float(zl)), zmax=round(float(zh)), crossings=nx_)
    # 5 roads + emergency services
    G = json.load(open(f'{ROOT}/docs/graph_segments.json')); cls = G['props']['cls']
    im = Image.new('RGB', (N, N), (246, 244, 239)); d = ImageDraw.Draw(im)
    base = np.clip(246 - 18 * (1 - hsN), 0, 255).astype(np.uint8); im.paste(Image.fromarray(np.stack([base, base - 2, base - 7], -1)))
    d = ImageDraw.Draw(im); lon0, lat0 = -71.95, 42.20; nseg = 0
    lines = []
    for i, g in enumerate(G['geo']):
        for part in g:
            p = np.asarray(part, np.float64)
            lon = np.cumsum(p[0::2]) / 1e5; lat = np.cumsum(p[1::2]) / 1e5
            if lon.size == 0 or abs(lon[0] - lon0) > 0.5 or abs(lat[0] - lat0) > 0.5: continue
            X_, Y_ = tr.transform(lon, lat); px, py = pix(X_, Y_)
            if px.max() < 0 or px.min() > N or py.max() < 0 or py.min() > N: continue
            lines.append((cls[i] if i < len(cls) else 9, list(zip(px.tolist(), py.tolist()))))
    best = None                                   # label anchor: a point on the longest major road near the middle of the block
    for i, g in enumerate(G['geo']):
        if (cls[i] if i < len(cls) else 0) < 1: continue
        for part in g:
            p = np.asarray(part, np.float64); lon = np.cumsum(p[0::2]) / 1e5; lat = np.cumsum(p[1::2]) / 1e5
            if lon.size < 2 or abs(lon[0] + 71.81) > 0.06 or abs(lat[0] - 42.27) > 0.05: continue
            X_, Y_ = tr.transform(lon, lat); fx = (np.asarray(X_) - x0) / (x1 - x0); fy = (y1 - np.asarray(Y_)) / (y1 - y0)
            k = len(fx) // 2; dd = np.hypot(fx[k] - 0.62, fy[k] - 0.42)
            if 0.1 < fx[k] < 0.9 and 0.1 < fy[k] < 0.9 and (best is None or dd < best[0]): best = (dd, [round(float(fx[k]), 4), round(float(fy[k]), 4)], G['props']['road'][i])
    if best: meta['road_anchor'] = dict(at=best[1], name=best[2])
    for c, pts in sorted(lines, key=lambda t: -(t[0] or 9)):
        major = (c or 9) <= 2
        d.line(pts, fill=(250, 180, 80) if major else (150, 150, 150), width=max(2, N // (260 if major else 520)), joint='curve'); nseg += 1
    F = json.load(open(f'{ROOT}/docs/network/facilities.json'))['facilities']; fac = []
    col = {'hospital': (200, 40, 40), 'fire_station': (230, 110, 20), 'police': (40, 80, 170)}
    for kind, rows in F.items():
        if kind not in col: continue
        for lon, lat, nm in rows:
            px, py = pix(*tr.transform(lon, lat))
            if 0 <= px < N and 0 <= py < N:
                s = max(7, N // 120); d.rounded_rectangle([px - s, py - s, px + s, py + s], radius=s // 3, fill=col[kind], outline=(255, 255, 255), width=max(2, N // 500))
                fac.append([kind, nm, round(float(px) / N, 4), round(float(py) / N, 4)])
    save('roads', np.asarray(im), segments=nseg, facilities=fac)
    # 6 rain (radar storm total on its own 1 km grid; the model grid blocks are shown as they are)
    rt = L['rain_total'].astype(np.float32); rN = np.asarray(Image.fromarray(rt).resize((N, N), Image.NEAREST))
    rl, rh = float(np.floor(rt.min() / 10) * 10), float(np.ceil(rt.max() / 10) * 10)
    rgb = ramp([(0, (232, 240, 250)), (0.4, (150, 190, 232)), (0.75, (88, 120, 210)), (1, (96, 60, 170))], np.clip((rN - rl) / max(rh - rl, 1), 0, 1))
    save('rain', (rgb * (0.9 + 0.1 * hsN[..., None])).astype(np.uint8), lo=rl, hi=rh, t0=info['t0'], hours=info['hours'])
    # 7 modelled peak water depth (optional: from a solve on the enclosing catalogue box)
    if a.flood and os.path.exists(f'{a.flood}/hmax_cm.npz'):
        H = np.load(f'{a.flood}/hmax_cm.npz')['hmax_cm'].astype(np.float32) / 100.0; fm = json.load(open(f'{a.flood}/flood_meta.json'))
        fx0, fy0, fx1, fy1 = fm['box']; fr = fm['res_m']
        c0, c1 = int(round((x0 - fx0) / fr)), int(round((x1 - fx0) / fr)); r0, r1 = int(round((fy1 - y1) / fr)), int(round((fy1 - y0) / fr))
        h = H[r0:r1, c0:c1]; hN = up(h, N)
        paper = np.clip(np.stack([hsN * 60 + 190] * 3, -1), 0, 255)
        w = np.clip((hN - 0.10) / 0.9, 0, 1)[..., None]; wet = (hN >= 0.10)[..., None]
        blue = ramp([(0, (170, 205, 240)), (0.5, (60, 130, 210)), (1, (18, 50, 130))], w[..., 0]).astype(np.float32)
        rgb = np.where(wet, blue, paper); rgb[chan & ~wet[..., 0]] = (150, 180, 210)
        save('flood', np.clip(rgb, 0, 255).astype(np.uint8), res_m=fr, storm=fm.get('title'), min_m=0.10)
    # height field for the 3D block: (G+1) x (G+1) samples, uint16 over [zmin, zmax], row 0 = north
    G = a.grid; from scipy.ndimage import zoom
    zz = zoom(z, ((G + 1) / z.shape[0], (G + 1) / z.shape[1]), order=1)[:G + 1, :G + 1]
    zmin, zmax = float(zz.min()), float(zz.max())
    ((zz - zmin) / max(zmax - zmin, 1e-6) * 65535).round().astype('<u2').tofile(f'{a.out}/height.bin')
    meta.update(grid=G, zmin=round(zmin, 2), zmax=round(zmax, 2), width_m=x1 - x0, height_m=y1 - y0)
    # rain on its own grid (for the sky layer): totals per block, row 0 = north
    meta['rain_grid'] = [[round(float(v), 1) for v in row] for row in L['rain_total'].astype(np.float32)]
    meta['rain_hourly_mean'] = [round(float(v), 2) for v in L['rain_hourly_mean']]
    # anchors (fractions of the box, x from west, y from north) for labels
    def frac(lon, lat):
        X_, Y_ = tr.transform(lon, lat); return [round((X_ - x0) / (x1 - x0), 4), round((y1 - Y_) / (y1 - y0), 4)]
    meta['anchors'] = dict(wpi=frac(-71.8085, 42.2746))
    xs = []
    for r in X['rows']:
        if r[ci['lon']] is None: continue
        f_ = frac(r[ci['lon']], r[ci['lat']])
        if 0.08 < f_[0] < 0.92 and 0.08 < f_[1] < 0.92: xs.append(dict(id=r[ci['id']], road=r[ci['road']], stream=r[ci['stream']], xtype=r[ci['xtype']], at=f_))
    meta['crossings'] = xs
    json.dump(meta, open(f'{a.out}/layers.json', 'w'), indent=1); print(json.dumps({k: v for k, v in meta.items() if k != 'south_profile'}, indent=1)[:3000])


# ------------------------------------------------------------------------------------------------ campus close-up (layer stack)
def fill_pits(z):
    """Priority-flood depression filling (Barnes et al. 2014) with a tiny gradient, so every cell drains to the edge."""
    import heapq
    ny, nx = z.shape; f = z.astype(np.float64).copy(); done = np.zeros(z.shape, bool); h = []
    for r in range(ny):
        for c in (0, nx - 1): heapq.heappush(h, (f[r, c], r, c)); done[r, c] = True
    for c in range(1, nx - 1):
        for r in (0, ny - 1): heapq.heappush(h, (f[r, c], r, c)); done[r, c] = True
    eps = 1e-4
    while h:
        v, r, c = heapq.heappop(h)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < ny and 0 <= cc < nx and not done[rr, cc]:
                done[rr, cc] = True
                if f[rr, cc] <= v: f[rr, cc] = v + eps
                heapq.heappush(h, (f[rr, cc], rr, cc))
    return f


def d8(f):
    """D8 steepest-descent direction (0..7, 255 = edge/none) and flow accumulation (cells) on a filled surface."""
    ny, nx = f.shape; D = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]; L = [1, 2 ** .5] * 4
    best = np.zeros(f.shape); dirn = np.full(f.shape, 255, np.uint8)
    P = np.pad(f, 1, mode='edge')
    for k, (dr, dc) in enumerate(D):
        nb = P[1 + dr:1 + dr + ny, 1 + dc:1 + dc + nx]; s = (f - nb) / L[k]
        m = s > best; best[m] = s[m]; dirn[m] = k
    order = np.argsort(-f, axis=None); acc = np.ones(f.size)
    rr, cc = np.divmod(order, nx)
    for i, r, c in zip(order, rr, cc):
        k = dirn[r, c]
        if k == 255: continue
        r2, c2 = r + D[k][0], c + D[k][1]
        if 0 <= r2 < ny and 0 <= c2 < nx: acc[r2 * nx + c2] += acc[i]
    return dirn, acc.reshape(f.shape)


def render_campus(a):
    from PIL import Image
    from pyproj import Transformer
    from scipy.ndimage import zoom
    os.makedirs(a.out, exist_ok=True)
    info = json.load(open(f'{a.data}/layers.json')); x0, y0, x1, y1 = info['box']; W, Hm = x1 - x0, y1 - y0
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    frac = lambda X, Y: ((np.asarray(X) - x0) / W, (y1 - np.asarray(Y)) / Hm)
    meta = dict(box=info['box'], width_m=W, height_m=Hm, storm='19 Aug 2021', layers={})
    # aerial
    im = Image.open(f'{a.data}/naip.jpg').convert('RGB'); N = min(a.size, im.size[0])
    im.resize((N, N), Image.LANCZOS).save(f'{a.out}/aerial.jpg', quality=86); meta['layers']['aerial'] = dict(src=info.get('naip'), px_m=round(W / im.size[0], 2))
    # fine terrain -> height grid + flow
    Z = np.load(f'{a.data}/dem_fine.npz'); z = Z['z']; zres = float(Z['res_m'])
    if np.isnan(z).any():
        from scipy.ndimage import distance_transform_edt
        idx = distance_transform_edt(np.isnan(z), return_distances=False, return_indices=True); z = z[tuple(idx)]
    G = a.grid; zz = zoom(z, ((G + 1) / z.shape[0], (G + 1) / z.shape[1]), order=1)[:G + 1, :G + 1]
    zmin, zmax = float(zz.min()), float(zz.max())
    ((zz - zmin) / max(zmax - zmin, 1e-6) * 65535).round().astype('<u2').tofile(f'{a.out}/height.bin')
    meta.update(grid=G, zmin=round(zmin, 2), zmax=round(zmax, 2), dem=info.get('dem_fine'))
    F = a.flow_grid; zf = zoom(z, (F / z.shape[0], F / z.shape[1]), order=1)[:F, :F]
    filled = fill_pits(zf); dirn, acc = d8(filled)
    dirn.tofile(f'{a.out}/flowdir.bin'); np.clip(np.log2(acc) * 16, 0, 255).astype(np.uint8).tofile(f'{a.out}/flowacc.bin')
    meta['flow'] = dict(grid=F, cell_m=round(W / F, 2), method='D8 steepest descent on the lidar surface after priority-flood pit filling (Barnes et al. 2014)')
    # where water collects (flow lines) as an image for the top layer
    lines_img = np.clip((np.log2(acc) - 6) / 8, 0, 1)
    # peak water depth from the flood model (enclosing catalogue box)
    paper = np.full((N, N, 3), 246, np.uint8)
    hsN = np.asarray(Image.fromarray((hillshade(z, zres, zf=1.5) * 255).astype(np.uint8)).resize((N, N), Image.BILINEAR)).astype(np.float32) / 255
    base = np.stack([236 + 14 * hsN, 233 + 14 * hsN, 226 + 14 * hsN], -1)
    if a.flood and os.path.exists(f'{a.flood}/hmax_cm.npz'):
        Hf = np.load(f'{a.flood}/hmax_cm.npz')['hmax_cm'].astype(np.float32) / 100.0; fm = json.load(open(f'{a.flood}/flood_meta.json'))
        fx0, fy0, fx1, fy1 = fm['box']; fr = fm['res_m']
        c0, c1 = (x0 - fx0) / fr, (x1 - fx0) / fr; r0, r1 = (fy1 - y1) / fr, (fy1 - y0) / fr
        sub = Hf[int(np.floor(r0)):int(np.ceil(r1)) + 1, int(np.floor(c0)):int(np.ceil(c1)) + 1]
        hN = np.asarray(Image.fromarray(sub).resize((N, N), Image.BILINEAR))
        w = np.clip((hN - 0.05) / 0.8, 0, 1)
        wet = hN >= 0.05
        blue = ramp([(0, (190, 220, 246)), (0.5, (72, 140, 214)), (1, (20, 60, 150))], w).astype(np.float32)
        base = np.where(wet[..., None], base * 0.25 + blue * 0.75, base)
        meta['layers']['water'] = dict(model='LISFLOOD-FP 8.2, 20 m, deployed settings', res_m=fr, min_m=0.05, run=fm.get('run'))
    fl = np.asarray(Image.fromarray((lines_img * 255).astype(np.uint8)).resize((N, N), Image.BILINEAR)).astype(np.float32)[..., None] / 255
    base = base * (1 - 0.55 * fl) + np.array([58, 120, 190]) * 0.55 * fl
    Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).save(f'{a.out}/model.jpg', quality=88)
    # roads with the model's status for the storm (the live replay's roads, the same data the map shows)
    R = json.load(open(a.roads)); roads = []
    for ft in R['features']:
        g = ft['geometry']; parts = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]; p = ft['properties']
        for part in parts:
            q = np.asarray(part)[:, :2]; fx, fy = frac(*tr.transform(q[:, 0], q[:, 1]))
            if fx.max() < 0 or fx.min() > 1 or fy.max() < 0 or fy.min() > 1: continue
            st = 'closed' if (p.get('p') or 0) >= 0.5 else ('risk' if p.get('m') else 'wet')
            roads.append(dict(n=p.get('n', ''), s=st, pts=[[round(float(u), 4), round(float(v), 4)] for u, v in zip(fx, fy)]))
    # all roads (grey) from the network, for the top layer
    Gs = json.load(open(f'{ROOT}/docs/graph_segments.json')); allr = []
    for i, g in enumerate(Gs['geo']):
        for part in g:
            pp = np.asarray(part, np.float64); lon = np.cumsum(pp[0::2]) / 1e5; lat = np.cumsum(pp[1::2]) / 1e5
            if lon.size < 2 or abs(lon[0] + 71.81) > 0.04 or abs(lat[0] - 42.27) > 0.03: continue
            fx, fy = frac(*tr.transform(lon, lat))
            if fx.max() < 0 or fx.min() > 1 or fy.max() < 0 or fy.min() > 1: continue
            allr.append(dict(n=Gs['props']['road'][i], c=Gs['props']['cls'][i], pts=[[round(float(u), 4), round(float(v), 4)] for u, v in zip(fx, fy)]))
    meta['roads_src'] = os.path.relpath(a.roads, ROOT)
    json.dump(dict(status=roads, all=allr), open(f'{a.out}/roads.json', 'w'), separators=(',', ':'))
    # buildings
    if os.path.exists(f'{a.data}/buildings.json'):
        B = json.load(open(f'{a.data}/buildings.json')); out = []
        for b in B['buildings']:
            q = np.asarray(b['p']); fx, fy = frac(*tr.transform(q[:, 0], q[:, 1]))
            if fx.max() < 0 or fx.min() > 1 or fy.max() < 0 or fy.min() > 1: continue
            out.append(dict(h=b['h'], n=b.get('n', ''), p=[[round(float(u), 5), round(float(v), 5)] for u, v in zip(fx, fy)]))
        json.dump(dict(license=B.get('license'), buildings=out), open(f'{a.out}/buildings.json', 'w'), separators=(',', ':'))
        meta['buildings'] = dict(n=len(out), src='OpenStreetMap', license=B.get('license'))
    # runoff potential (curve number, the model's 10 m input) for the bottom layer
    Lr = np.load(f'{a.data}/layers.npz'); cn = Lr['cn'].astype(np.float32); mk = Lr['mask']
    cnN = np.asarray(Image.fromarray(cn).resize((2048, 2048), Image.BILINEAR)); wN = np.asarray(Image.fromarray(((mk & 3) > 0).astype(np.uint8) * 255).resize((2048, 2048), Image.NEAREST)) > 127
    rgb = ramp([(0, (245, 241, 230)), (0.35, (226, 200, 150)), (0.65, (196, 132, 82)), (0.85, (150, 78, 52)), (1, (92, 44, 40))], np.clip((cnN - 40) / 58, 0, 1)); rgb[wN] = (150, 184, 216)
    Image.fromarray(rgb).save(f'{a.out}/runoff.jpg', quality=88); meta['layers']['runoff'] = dict(lo=40, hi=98, res_m=info['res_m'])
    # places for labels
    P = dict(kaven=(-71.80577, 42.27514), wpi=(-71.8085, 42.2746), pond=(-71.8048, 42.2774), field=(-71.8113, 42.2741), park_ave=(-71.8138, 42.2752), institute_park=(-71.8030, 42.2760))
    meta['places'] = {k: [round(float(v), 4) for v in frac(*tr.transform(*ll))] for k, ll in P.items()}
    meta['rain_total_mm'] = None
    L = np.load(f'{a.data}/layers.npz'); rt = L['rain_total'].astype(np.float32)
    meta['rain_total_mm'] = [round(float(rt.min()), 1), round(float(rt.max()), 1)]; meta['rain_hourly_mean'] = [round(float(v), 2) for v in L['rain_hourly_mean']]
    json.dump(meta, open(f'{a.out}/meta.json', 'w'), indent=1); print(json.dumps(meta, indent=1)[:2500])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    f = sp.add_parser('fetch'); f.add_argument('--surr', required=True); f.add_argument('--out', default='drafts/layers/data'); f.add_argument('--px', type=int, default=2000)
    f.add_argument('--dem-res', type=float, default=0); f.add_argument('--buildings', action='store_true')
    r = sp.add_parser('render'); r.add_argument('--data', required=True); r.add_argument('--flood'); r.add_argument('--out', required=True); r.add_argument('--size', type=int, default=1400); r.add_argument('--grid', type=int, default=300)
    c = sp.add_parser('campus'); c.add_argument('--data', required=True); c.add_argument('--flood'); c.add_argument('--roads', required=True); c.add_argument('--out', required=True)
    c.add_argument('--size', type=int, default=4096); c.add_argument('--grid', type=int, default=450); c.add_argument('--flow-grid', type=int, default=450)
    a = ap.parse_args()
    if a.cmd == 'fetch': fetch(a)
    elif a.cmd == 'campus': render_campus(a)
    else: render(a)
