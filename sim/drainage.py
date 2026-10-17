"""Where rain goes: a statewide drainage picture from USGS 3DEP elevation.

Every cell gets its steepest downhill neighbour (D8 flow direction, after filling pits and resolving flats so water always
finds a way out), and the number of upstream cells that drain through it (flow accumulation). Water that reaches the sea or
leaves the state stops there. The browser animates particles along these directions, so you can watch water run downhill,
gather into streams and rivers, and reach the ocean.

Writes docs/drain/flow.png  (one byte per cell: direction code 1..8 (N NE E SE S SW W NW) + 9 x upstream-area class 0..27; 0 = sea)
       docs/drain/streams.json  (polylines of streams draining 5 km2 or more, with upstream area)
       docs/drain/meta.json
"""
import io, os, json, math, time
import numpy as np, requests, tifffile
if not hasattr(np, 'in1d'): np.in1d = np.isin          # pysheds still calls the old name

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'docs', 'drain'); os.makedirs(OUT, exist_ok=True)
BBOX = (-73.55, 41.20, -69.90, 42.92)
RES = float(os.environ.get('DRAIN_RES', '50'))
R_EARTH = 6378137.0
merc = lambda lon, lat: (np.radians(lon) * R_EARTH, np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)) * R_EARTH)


def get(url, tries=5):
    for k in range(tries):
        try:
            r = requests.get(url, timeout=180)
            if r.status_code == 200: return r
        except Exception as e:
            print('  retry', k, e)
        time.sleep(3 + 5 * k)
    raise RuntimeError(url)


def dem():
    lon0, lat0, lon1, lat1 = BBOX
    x0, y0 = merc(lon0, lat0); x1, y1 = merc(lon1, lat1)
    k = 1 / math.cos(math.radians((lat0 + lat1) / 2))
    nx = int(round((x1 - x0) / (RES * k))); ny = int(round((y1 - y0) / (RES * k)))
    Z = np.full((ny, nx), np.nan, np.float32); step = 1500
    for r0 in range(0, ny, step):
        for c0 in range(0, nx, step):
            r1, c1 = min(ny, r0 + step), min(nx, c0 + step)
            bx0 = x0 + (x1 - x0) * c0 / nx; bx1 = x0 + (x1 - x0) * c1 / nx
            by1 = y1 - (y1 - y0) * r0 / ny; by0 = y1 - (y1 - y0) * r1 / ny
            url = ('https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage'
                   f'?bbox={bx0},{by0},{bx1},{by1}&bboxSR=3857&imageSR=3857&size={c1 - c0},{r1 - r0}'
                   '&format=tiff&pixelType=F32&noDataInterpretation=esriNoDataMatchAny&interpolation=RSP_BilinearInterpolation&f=image')
            t = tifffile.imread(io.BytesIO(get(url).content)).astype(np.float32)
            if t.ndim == 3: t = t[..., 0]
            Z[r0:r1, c0:c1] = t[: r1 - r0, : c1 - c0]
    Z[(Z < -500) | (Z > 3000)] = np.nan
    print(f'DEM {ny}x{nx}, {np.isnan(Z).mean() * 100:.1f}% no data')
    return Z


def main():
    t0 = time.time()
    Z = dem(); ny, nx = Z.shape
    from scipy import ndimage
    sea0 = np.isnan(Z) | (Z < -1.0) | (np.abs(Z) < 0.005)
    lab, _ = ndimage.label(sea0); edge = np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]); edge = edge[edge > 0]
    sea = np.isin(lab, edge)
    from pysheds.sview import Raster, ViewFinder
    from pysheds.grid import Grid
    from affine import Affine
    Zs = np.where(sea, -10.0, np.where(np.isnan(Z), -10.0, Z)).astype(np.float64)
    vf = ViewFinder(affine=Affine(1, 0, 0, 0, -1, ny), shape=Zs.shape, nodata=np.float64(-9999))
    d = Raster(Zs, viewfinder=vf); g = Grid.from_raster(d)
    fl = g.resolve_flats(g.fill_depressions(g.fill_pits(d)))
    dirmap = (64, 128, 1, 2, 4, 8, 16, 32)                       # N NE E SE S SW W NW
    fdr = g.flowdir(fl, dirmap=dirmap); fd = np.asarray(fdr).astype(np.int32)
    acc = np.asarray(g.accumulation(fdr, dirmap=dirmap)).astype(np.float64)
    code = np.zeros((ny, nx), np.uint8)
    for i, v in enumerate(dirmap): code[fd == v] = i + 1
    code[sea] = 0
    cell_km2 = (RES / 1000) ** 2
    area = acc * cell_km2
    lvl = np.clip(np.floor(np.log2(np.maximum(area / cell_km2, 1)) ), 0, 27).astype(np.uint8)   # upstream area class: doubling steps
    byte = np.where(code > 0, code + 9 * lvl, 0).astype(np.uint8)
    from PIL import Image
    Image.fromarray(byte, 'L').save(os.path.join(OUT, 'flow.png'), optimize=True)
    print('flow.png', os.path.getsize(os.path.join(OUT, 'flow.png')) // 1024, 'KB')
    # streams: trace downstream from each stream cell; group into polylines per run between junctions
    DR = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
    st = (area >= float(os.environ.get('STREAM_KM2', '4'))) & (code > 0)
    lon0, lat0, lon1, lat1 = BBOX; X0, Y0 = merc(lon0, lat0); X1, Y1 = merc(lon1, lat1)
    def ll(r, c):
        x = X0 + (c + 0.5) / nx * (X1 - X0); y = Y1 - (r + 0.5) / ny * (Y1 - Y0)
        return round(math.degrees(x / R_EARTH), 4), round(math.degrees(2 * math.atan(math.exp(y / R_EARTH)) - math.pi / 2), 4)
    indeg = np.zeros((ny, nx), np.int16)
    rr, cc = np.nonzero(st)
    for r, c in zip(rr, cc):
        dr, dc = DR[code[r, c] - 1]; r2, c2 = r + dr, c + dc
        if 0 <= r2 < ny and 0 <= c2 < nx and st[r2, c2]: indeg[r2, c2] += 1
    lines = []
    starts = [(r, c) for r, c in zip(rr, cc) if indeg[r, c] != 1]
    done = np.zeros((ny, nx), bool)
    for r, c in starts:
        pts = [ll(r, c)]; a_max = area[r, c]; done[r, c] = True
        while True:
            dr, dc = DR[code[r, c] - 1]; r2, c2 = r + dr, c + dc
            if not (0 <= r2 < ny and 0 <= c2 < nx): break
            pts.append(ll(r2, c2))
            if not st[r2, c2] or indeg[r2, c2] != 1 or done[r2, c2]: break
            r, c = r2, c2; done[r, c] = True; a_max = max(a_max, area[r, c])
        if len(pts) >= 2: lines.append([round(float(a_max), 1), [v for p in pts[::2] + ([pts[-1]] if len(pts) % 2 == 0 else []) for v in p]])
    json.dump(dict(lines=lines), open(os.path.join(OUT, 'streams.json'), 'w'), separators=(',', ':'))
    json.dump(dict(bounds=list(BBOX), shape=[ny, nx], cell_m=RES, dirs='1..8 = N NE E SE S SW W NW (R channel / 30)', g_max_km2=round(float(area[~sea].max()), 1),
                   streams=len(lines), built=time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), source=f'USGS 3DEP 1/3 arc-second, resampled to {RES:.0f} m; D8 directions after pit filling (pysheds)'),
              open(os.path.join(OUT, 'meta.json'), 'w'))
    print(f'streams {len(lines)}, largest drains {area[~sea].max():.0f} km2 | {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
