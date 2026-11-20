"""Paper 2, RQ1: road-edge stream-power index from 1 m lidar (definition fixed in docs/proto/paper2/RQ1_INDEX_SPEC.md).

No damage labels are read here. Output per segment: upslope area draining along each road edge and the stream-power index A*S.

    python proto/edge_spi.py --box 171400,913700,183100,925000 --segments docs/proto/phase1/parametric_t2/t2_base/segments.geojson \
        --town LEOMINSTER --out docs/proto/paper2/edge_spi_leominster.json

Method (fixed): 1 m 3DEP bare earth (USGS image service, best available) in core tiles of 4 km with a 1 km buffer; pits filled,
depressions and flats resolved (pysheds), D8 flow directions, flow accumulation in cells (= m2 at 1 m); local slope from the 3x3
gradient (m/m). Road edges: points every 2 m along each segment, offset 3 m and 5 m to both sides of the centreline; at each point the
maximum accumulation and the slope within a 3x3 window. SPI = A * S (m2). Per segment: max and 90th percentile of SPI over its edge
points, max A, and the edge length (m) with SPI above the box-wide 95th percentile of all edge points.
"""
import argparse, io, json, math, os, sys, time
import numpy as np
if not hasattr(np, 'in1d'): np.in1d = lambda a, b, **k: np.isin(np.ravel(a), b, **k)   # pysheds 0.5 on numpy 2

SVC = 'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage'
CORE, BUF, SUB = 4000, 1000, 2000          # m; SUB = pixels per service request (1 m cells)
STEP, OFFS = 2.0, (3.0, 5.0)


def fetch(x0, y0, x1, y1):
    """Mosaic of 1 m DEM requests of SUB x SUB pixels; NaN where the service has no data."""
    import requests, tifffile
    nx, ny = int(x1 - x0), int(y1 - y0); Z = np.full((ny, nx), np.nan, np.float32)
    for yy in range(0, ny, SUB):
        for xx in range(0, nx, SUB):
            w, h = min(SUB, nx - xx), min(SUB, ny - yy); bx0, by1 = x0 + xx, y1 - yy
            q = dict(bbox=f'{bx0},{by1 - h},{bx0 + w},{by1}', bboxSR=26986, imageSR=26986, size=f'{w},{h}', format='tiff',
                     pixelType='F32', interpolation='RSP_BilinearInterpolation', noData=-9999, f='image')
            for k in range(4):
                try:
                    r = requests.get(SVC, params=q, timeout=300)
                    if r.status_code == 200 and r.content[:2] in (b'II', b'MM'):
                        z = tifffile.imread(io.BytesIO(r.content)).astype(np.float32); Z[yy:yy + h, xx:xx + w] = np.where(z < -1000, np.nan, z); break
                    print('dem: bad', r.status_code, r.content[:120], flush=True)
                except Exception as e:
                    print('dem: fail', repr(e)[:160], flush=True)
                time.sleep(5 * (k + 1))
    return Z


def accumulate(Z, x0, y1):
    """Fill, resolve flats, D8 directions, accumulation (cells) and slope (m/m) on a 1 m grid whose upper-left corner is (x0, y1)."""
    from pysheds.grid import Grid
    from pysheds.sview import Raster, ViewFinder
    from affine import Affine
    nod = -9999.0; zz = np.where(np.isnan(Z), nod, Z).astype(np.float64)
    vf = ViewFinder(affine=Affine(1.0, 0, x0, 0, -1.0, y1), shape=Z.shape, nodata=nod)
    dem = Raster(zz, viewfinder=vf); g = Grid.from_raster(dem)
    f = g.resolve_flats(g.fill_depressions(g.fill_pits(dem)))
    fd = g.flowdir(f, routing='d8'); acc = np.asarray(g.accumulation(fd, routing='d8'), np.float32)
    gy, gx = np.gradient(np.where(np.isnan(Z), np.nanmean(Z), Z)); S = np.hypot(gx, gy).astype(np.float32)
    acc[np.isnan(Z)] = np.nan; S[np.isnan(Z)] = np.nan
    return acc, S


def edge_points(xy):
    """Points every STEP m along a polyline, offset by OFFS to both sides; returns (n, 2)."""
    P = []
    for (ax, ay), (bx, by) in zip(xy, xy[1:]):
        L = math.hypot(bx - ax, by - ay)
        if L < 1e-6: continue
        ux, uy = (bx - ax) / L, (by - ay) / L; nx_, ny_ = -uy, ux
        for t in np.arange(0, L, STEP):
            px, py = ax + ux * t, ay + uy * t
            for o in OFFS:
                P.append((px + nx_ * o, py + ny_ * o)); P.append((px - nx_ * o, py - ny_ * o))
    return np.array(P) if P else np.zeros((0, 2))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--box', required=True); ap.add_argument('--segments', required=True)
    ap.add_argument('--town', default=''); ap.add_argument('--out', required=True); ap.add_argument('--cache', default='')
    a = ap.parse_args()
    from pyproj import Transformer
    from scipy.ndimage import maximum_filter
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    X0, Y0, X1, Y1 = map(float, a.box.split(','))
    G = json.load(open(a.segments)); segs = {}
    for f in G['features']:
        p = f['properties']
        if a.town and a.town.upper() not in (p.get('town') or '').upper(): continue
        c = f['geometry']['coordinates']; parts = [c] if f['geometry']['type'] == 'LineString' else c
        pts = np.vstack([edge_points([tr.transform(*q[:2]) for q in part]) for part in parts])
        segs[p['segment']] = dict(pts=pts, road=p.get('road'), length_m=p.get('length_m'))
    print(len(segs), 'segments', sum(len(s['pts']) for s in segs.values()), 'edge points', flush=True)
    vals = {k: [np.full(len(s['pts']), np.nan, np.float32), np.full(len(s['pts']), np.nan, np.float32)] for k, s in segs.items()}
    tiles = [(x, y) for y in np.arange(Y0, Y1, CORE) for x in np.arange(X0, X1, CORE)]; meta = []
    for i, (cx, cy) in enumerate(tiles):
        t0 = time.time(); x0, y0, x1, y1 = cx - BUF, cy - BUF, min(cx + CORE, X1) + BUF, min(cy + CORE, Y1) + BUF
        cf = f'{a.cache}/tile_{int(cx)}_{int(cy)}.npz' if a.cache else ''
        if cf and os.path.exists(cf): Z = np.load(cf)['z']
        else:
            Z = fetch(x0, y0, x1, y1)
            if cf: os.makedirs(a.cache, exist_ok=True); np.savez_compressed(cf, z=Z)
        acc, S = accumulate(Z, x0, y1); A3 = maximum_filter(np.nan_to_num(acc), 3)
        S3 = np.where(np.isnan(S), 0, S)
        n = 0
        for k, s in segs.items():
            P = s['pts']; m = (P[:, 0] >= cx) & (P[:, 0] < min(cx + CORE, X1)) & (P[:, 1] >= cy) & (P[:, 1] < min(cy + CORE, Y1))
            if not m.any(): continue
            c = ((P[m, 0] - x0)).astype(int); r = ((y1 - P[m, 1])).astype(int)
            vals[k][0][m] = A3[r, c]; vals[k][1][m] = S3[r, c]; n += int(m.sum())
        meta.append(dict(tile=[cx, cy], shape=list(Z.shape), nan_share=round(float(np.isnan(Z).mean()), 4), points=n, sec=round(time.time() - t0)))
        print(meta[-1], flush=True)
    allspi = np.concatenate([v[0] * v[1] for v in vals.values()]); T = float(np.nanpercentile(allspi, 95))
    out = {}
    for k, s in segs.items():
        A, S = vals[k]; spi = A * S; ok = ~np.isnan(spi)
        if not ok.any(): continue
        out[str(k)] = dict(road=s['road'], length_m=s['length_m'], points=int(ok.sum()), A_max_m2=round(float(np.nanmax(A)), 1),
                           spi_max=round(float(np.nanmax(spi)), 2), spi_p90=round(float(np.nanpercentile(spi[ok], 90)), 2),
                           edge_len_over_p95_m=round(float((spi[ok] > T).sum() * STEP / (2 * len(OFFS))), 1))
    json.dump(dict(made_by='proto/edge_spi.py', spec='docs/proto/paper2/RQ1_INDEX_SPEC.md', box=[X0, Y0, X1, Y1], town=a.town,
                   step_m=STEP, offsets_m=list(OFFS), spi_p95_all_points=round(T, 2), tiles=meta, segments=out), open(a.out, 'w'), indent=0)
    print('wrote', a.out, len(out), 'segments; p95 SPI', round(T, 2))


if __name__ == '__main__':
    main()
