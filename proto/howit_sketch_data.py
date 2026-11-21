"""Data for the How it works sketch: one real storm (Leominster, 11 Sept 2023, replay leominster_sep2023 = the deployed T2 run) at one
moment (the 6:50 PM EDT peak of closures, replay frame 82), over one box of central Leominster. Nothing is computed that the model does
not compute: road depth and status come from the replay's own per-segment series; access uses proto/resilience.py (same graph, speeds,
response-time standards and closure depth) on those depths.
    python proto/howit_sketch_data.py  ->  docs/how-it-works/sketch/sketch.json, depth.npy, rain.npy"""
import json, os, sys, numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import resilience as RS
RUN = f'{ROOT}/docs/site/data/leominster_sep2023'; OUT = f'{ROOT}/docs/how-it-works/sketch'
BOX = (175600, 916400, 181600, 921800)      # drawn area, EPSG:26986 m (6.0 x 5.4 km)
FRAME = 82                                   # 5-min replay frame: 16:00Z + 410 min = 22:50Z = 6:50 PM EDT
RAIN_FRAME = 68                              # 6-min radar frame: 16:00Z + 408 min = 22:48Z
GRID_X0, GRID_Y1, CELL = 168000, 928000, 20  # replay grid (meta: 1000 x 1000 at 20 m, EPSG:26986 box 168-188 km E, 908-928 km N)


def depth_frame(meta, f):
    D = meta['depthc']; im = np.asarray(Image.open(f'{RUN}/{D["sheets"][f // D["per"]]}').convert('RGB'), np.float32)
    v = im[:, :, f % D['per']] / 255.0; return 3.0 * v * v                      # enc: v = 255 sqrt(depth / 3)


def rain_frame(R, f):
    im = np.asarray(Image.open(f'{RUN}/{R["sheet"]}').convert('RGB'), np.float32)
    c = f // 3; cy, cx = divmod(c, R['cols']); t = im[cy * R['h']:(cy + 1) * R['h'], cx * R['w']:(cx + 1) * R['w'], f % 3] / 255.0
    return np.expm1(t * np.log1p(R['max_mmh']))                                  # mm/h on a lat/lon grid (bounds)


def main():
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    meta = json.load(open(f'{RUN}/meta.json')); R = json.load(open(f'{RUN}/rain.json')); refs = json.load(open(f'{RUN}/refs.json'))
    x0, y0, x1, y1 = BOX
    # depth raster crop (m)
    dep = depth_frame(meta, FRAME); c0, c1 = (x0 - GRID_X0) // CELL, (x1 - GRID_X0) // CELL; r0, r1 = (GRID_Y1 - y1) // CELL, (GRID_Y1 - y0) // CELL
    np.save(f'{OUT}/depth.npy', dep[r0:r1, c0:c1].astype(np.float16))
    # rain at the same moment, resampled onto the box at 100 m (radar cells are about 1 km; kept blocky on purpose)
    rr = rain_frame(R, RAIN_FRAME); (lo0, la0), (lo1, la1) = R['bounds']
    xs = np.arange(x0 + 50, x1, 100); ys = np.arange(y1 - 50, y0, -100); X, Y = np.meshgrid(xs, ys)
    lon, lat = Transformer.from_crs(26986, 4326, always_xy=True).transform(X, Y)
    ci = np.clip(((lon - lo0) / (lo1 - lo0) * R['w']).astype(int), 0, R['w'] - 1); ri = np.clip(((la1 - lat) / (la1 - la0) * R['h']).astype(int), 0, R['h'] - 1)
    np.save(f'{OUT}/rain.npy', rr[ri, ci].astype(np.float32))
    # roads in the box: status at the frame from the replay's own depth series (cm)
    roads = []; seg_d = {}
    for f in json.load(open(f'{RUN}/roads.json'))['features']:
        p = f['properties']; d = p.get('d') or []; dc = float(d[FRAME]) if len(d) > FRAME else 0.0; seg_d[int(f['id'])] = dc
    S = json.load(open(f'{ROOT}/docs/graph_segments.json')); net = RS.Net(S); geom = RS.seg_geometry(S)
    import impacts as IM
    from impacts import decode_segments
    Pp = S['props']; keep = {}
    for i, lo, la in decode_segments(S):
        x, y = tr.transform(lo, la)
        if x.max() < x0 or x.min() > x1 or y.max() < y0 or y.min() > y1: continue
        keep.setdefault(i, []).append(np.round(np.column_stack([x - x0, y1 - y]), 1).tolist())
    # access: dry vs this frame (proto/resilience.py rules)
    n = net.n; d_cm = np.zeros(n); 
    for i, v in seg_d.items(): d_cm[i] = v
    fac = json.load(open(f'{ROOT}/docs/network/facilities.json'))['facilities']; FS = RS.snap_facilities(fac, geom)
    m0 = np.ones(n); G0 = net.graph(m0); mult, _ = RS.speed_mult(d_cm, RS.CLOSE_CM); G = net.graph(mult); closed = ~np.isfinite(mult)
    lost = {}
    for s, lim in RS.ACCESS_MIN.items():
        a0 = RS.access_minutes(net, G0, FS[s]); src = [j for j in FS[s] if np.isfinite(mult[j])]; a1 = RS.access_minutes(net, G, src)
        lost[s] = {i for i in keep if a0[i] <= lim and not (a1[i] <= lim and not closed[i])}
    for i, parts in keep.items():
        dc = seg_d.get(i, 0.0)
        st = 'closed' if dc >= 30 else 'risk' if dc >= 15 else 'wet' if dc >= 5 else 'dry'
        roads.append(dict(id=i, name=Pp['road'][i] or '', town=Pp['town'][i], cls=int(Pp['cls'][i]), d=round(dc), st=st,
                          lost=[s for s in lost if i in lost[s]], parts=parts))
    facs = []
    for kind, key in (('hospital', 'hospital'), ('fire_station', 'fire'), ('police', 'police')):
        for r in fac.get(kind, []):
            x, y = tr.transform(r[0], r[1])
            if x0 <= x <= x1 and y0 <= y <= y1: facs.append(dict(kind=key, name=r[2] if len(r) > 2 else '', x=round(x - x0), y=round(y1 - y)))
    reps = []
    for r in refs.get('reports', []):
        x, y = tr.transform(r[0], r[1])
        if x0 <= x <= x1 and y0 <= y <= y1: reps.append(dict(x=round(x - x0), y=round(y1 - y), src=r[2], text=r[3], t=r[4]))
    out = dict(made_by='proto/howit_sketch_data.py', run='leominster_sep2023 (deployed T2 run)', frame=FRAME, time_local='Mon Sep 11 2023, 6:50 PM EDT',
               box_epsg26986=BOX, size_m=[x1 - x0, y1 - y0], depth_grid=dict(cell_m=20, file='depth.npy'), rain_grid=dict(cell_m=100, file='rain.npy',
               source=R['source'], frame=RAIN_FRAME), access_min=RS.ACCESS_MIN, close_cm=RS.CLOSE_CM,
               counts=dict(closed=sum(r['st'] == 'closed' for r in roads), risk=sum(r['st'] == 'risk' for r in roads),
                           lost_any=sum(bool(r['lost']) for r in roads), lost={s: len(v) for s, v in lost.items()}),
               roads=roads, facilities=facs, reports=reps)
    json.dump(out, open(f'{OUT}/sketch.json', 'w'), separators=(',', ':'))
    print(json.dumps(out['counts']), len(roads), 'roads', len(facs), 'facilities', len(reps), 'reports', 'rain max', float(np.load(f'{OUT}/rain.npy').max()))


if __name__ == '__main__':
    main()
