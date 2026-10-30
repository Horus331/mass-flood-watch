"""What-if storm explorer: one real storm (Leominster, 11 Sept 2023, the live `leominster_sep2023` replay box) rerun by LISFLOOD-FP with
modified inputs, every combination a full physics run on Turing, packed light for the public viewer (docs/viewer.html?run=whatif).

    python proto/whatif.py list                      # the scenario matrix (index, id, env)
    python proto/whatif.py env <index>               # 'export K=V' lines for one scenario (proto/turing/whatif_runs.slurm)
    python proto/whatif.py pack [--results results]  # every finished scenario -> docs/site/data/whatif/ (index.json, roads.json, terrain.png, <id>/)
    python proto/whatif.py selftest                  # offline: a synthetic run through the packer

Axes (docs/proto/whatif/WHATIF.md has the reasoning):
  rain      LF_RAIN_SCALE 0.5 / 0.75 / 1 (the MRMS radar storm as observed) / 1.25: every hour of radar rain multiplied, same timing and place
  ground    dry = LF_CN_AMC=I, normal = AMC II (the baseline), saturated = AMC III, frozen = LF_CN_FROZEN=1 + LF_INFIL_MMH=0 (every land cell
            at the paved curve number 98 before the calibration scale, no steady soak-in: an upper bound for concrete frost)
  culverts  open = the baseline (a notch at every mapped crossing, depression breaching), blocked = LF_XINGS_BLOCKED=1 (culverts and small
            crossings pass no water: the road fill is solid and never carved; bridges stay open)
Everything else is the deployed baseline (docs/proto/parity/BASELINE.md): LF_PARITY=1, LF_LOSS=cn, LF_CN_SCALE=0.88, LF_INFIL_MMH=2,
20 m, 48 h, hourly MRMS Pass2 rain, plus LF_SAVEINT=900 (15-minute frames: a lighter pack than the 5-minute live replay).

Pack per scenario (docs/site/data/whatif/<id>/, ~1-2 MB): depth_NN.png (15-min frames, 9 per image, base-5 classes 5 / 15 / 30 / 100 cm;
on rivers, streams and ponds the class is the RISE above the level at the start, so channels light up as they swell), d.json (depth on each
road segment per frame, closures, culverts overtopped, numbers), flow.png + flow.json (30-min water velocity). Shared: roads.json (geometry
of every segment that gets water in any scenario), terrain.png (R = hillshade of the lidar DEM, G = mapped water / channel cells), index.json.
"""
import argparse
import datetime as dt
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
SITE = os.path.join(ROOT, 'docs', 'site', 'data', 'whatif')
sys.path.insert(0, os.path.join(ROOT, 'docs', 'site'))

STORM, BOX, HOURS, RES = 'sep2023', '168000,908000,188000,928000', 48, 20
BASE_ENV = dict(STORM=STORM, BOX=BOX, HOURS=str(HOURS), RES=str(RES), LF_PARITY='1', LF_LOSS='cn', LF_CN_SCALE='0.88', LF_INFIL_MMH='2',
                LF_QOUT='1', LF_VOUT='1', LF_SAVEINT='900', LF_NO_UPLOAD='1')
RAIN = [('r050', 0.5, {'LF_RAIN_SCALE': '0.5'}), ('r075', 0.75, {'LF_RAIN_SCALE': '0.75'}), ('r100', 1.0, {}), ('r125', 1.25, {'LF_RAIN_SCALE': '1.25'})]
SOIL = [('dry', 'Dry', {'LF_CN_AMC': 'I'}), ('normal', 'Normal', {}), ('wet', 'Saturated', {'LF_CN_AMC': 'III'}),
        ('frozen', 'Frozen', {'LF_CN_FROZEN': '1', 'LF_INFIL_MMH': '0'})]
CULV = [('open', 'Open', {}), ('blocked', 'Blocked', {'LF_XINGS_BLOCKED': '1'})]
BASELINE = 'r100_normal_open'
FRAME_MIN = 15
FLOW_MIN = 30


def matrix():
    """baseline first, then the one-axis changes from it, then everything else (so a partial batch is still useful)."""
    S = []
    for r, k, re in RAIN:
        for s, sl, se in SOIL:
            for c, cl, ce in CULV:
                sid = f'{r}_{s}_{c}'
                env = dict(BASE_ENV, **re, **se, **ce, NAME='whatif_' + sid)
                S.append(dict(id=sid, rain=k, soil=s, culverts=c, env=env, changes=sum([r != 'r100', s != 'normal', c != 'open'])))
    S.sort(key=lambda x: (x['changes'], x['id'] != BASELINE, x['id']))
    return S


def run_out(sc):
    work = os.environ.get('LF_WORK', os.path.expanduser('~/scratch/lisflood'))
    return os.path.join(work, f"run_{STORM}_proto_{sc['env']['NAME']}", 'out')


# ---------------------------------------------------------------- packing
def hillshade(z, res, az=315.0, alt=40.0, zf=2.0):
    z = np.where(np.isfinite(z), z, np.nanmean(z)).astype(np.float64)
    gy, gx = np.gradient(z * zf, res)
    slope = np.arctan(np.hypot(gx, gy)); aspect = np.arctan2(-gx, gy)
    a, b = math.radians(360 - az + 90), math.radians(alt)
    hs = np.sin(b) * np.cos(slope) + np.cos(b) * np.sin(slope) * np.cos(a - aspect)
    return np.clip(hs, 0, 1)


def frame_classes(cm, wm, d0):
    """land cells: depth classes; mapped water / channel cells: classes of the rise above the start level (cm)."""
    v = np.where(wm, np.maximum(cm.astype(np.int32) - d0, 0), cm.astype(np.int32))
    c = np.zeros(cm.shape, np.uint8)
    for k, th in enumerate((5, 15, 30, 100)):
        c[v >= th] = k + 1
    import build_data as BD
    return BD.despeckle(c)


def write_sheets(frames, od):
    from PIL import Image
    h, w = frames[0].shape; names = []
    for s in range(0, len(frames), 9):
        rgb = np.zeros((h, w, 3), np.uint8)
        for j in range(9):
            if s + j < len(frames):
                rgb[..., j // 3] += frames[s + j] * (1, 5, 25)[j % 3]
        n = 'depth_%02d.png' % (s // 9); Image.fromarray(rgb, 'RGB').save(os.path.join(od, n), optimize=True); names.append(n)
    return names


def seg_props(q):
    import build_data as BD
    may = (float(q.get('p_may_close') or 0)) >= 0.5 and float(q['p_close']) < 0.5
    return dict(n=q.get('road') or '', t=q.get('town') or '', c=BD.CLS.get(q.get('road_class'), 0)), may


def pack_one(sc, rdir, out, od, keep_every):
    """one scenario -> od (depth sheets, d.json, flow); returns (summary for index.json, {seg id: feature} for the shared roads file)."""
    import build_data as BD
    from shapely.geometry import shape, mapping
    from shapely.ops import linemerge
    os.makedirs(od, exist_ok=True)
    for f in os.listdir(od):
        os.remove(os.path.join(od, f))
    S = json.load(open(os.path.join(rdir, 'summary.json'))); fh = S['frame_hours']
    keep = list(range(0, len(fh), keep_every)); nf = len(keep)
    D = np.load(os.path.join(out, 'frames_cm.npz'))['depth_cm']
    wm = np.load(os.path.join(out, 'watermask.npy')).astype(bool)
    d0 = D[0].astype(np.int32)
    frames = [frame_classes(D[k], wm, d0) for k in keep]
    sheets = write_sheets(frames, od)
    land = ~wm
    wet_km2 = [round(float(((D[k] >= 15) & land).sum()) * RES * RES / 1e6, 2) for k in keep]
    rise_km = [round(float(((D[k].astype(np.int32) - d0 >= 15) & wm).sum()) * RES / 1e3, 1) for k in keep]
    g = json.load(open(os.path.join(rdir, 'segments.geojson')))
    box = [float(v) for v in BOX.split(',')]; cells = {}
    for ft in g['features']:
        rc = BD.road_cells(ft['geometry'], box, RES, frames[0].shape)
        if rc is not None: cells[int(ft['properties']['segment'])] = rc
    edge = BD.edge_intervals(iter(frames), cells, ~wm)      # water drawn across the road line while the road surface stays above it
    segs, feats, closed = {}, {}, np.zeros(nf, int)
    p_close, may_ids = {}, []
    for ft in g['features']:
        q = ft['properties']; d = q.get('d') or []
        if isinstance(d, str): d = json.loads(d)
        d = [d[k] for k in keep if k < len(d)]
        pc = float(q['p_close']); pr, may = seg_props(q)
        if not (pc >= 0.5 or may or (d and max(d) >= 3) or int(q['segment']) in edge):
            continue
        sid = int(q['segment'])
        dd = [int(min(255, v)) for v in d]
        while dd and dd[-1] == 0: dd.pop()
        if dd and max(dd) >= 3: segs[sid] = dd
        if pc >= 0.5: p_close[sid] = round(pc, 2)
        if may: may_ids.append(sid)
        for a, b in BD.intervals(d):
            closed[int(math.ceil(a)):int(min(nf, math.ceil(b)))] += 1
        geom = shape(ft['geometry'])
        if geom.geom_type == 'MultiLineString': geom = linemerge(geom)
        gm = mapping(geom.simplify(0.00003, preserve_topology=False))
        r5 = lambda c: [round(c[0], 5), round(c[1], 5)]
        if gm['type'] == 'LineString': gm = {'type': 'LineString', 'coordinates': [r5(c) for c in gm['coordinates']]}
        elif gm['type'] == 'MultiLineString': gm = {'type': 'MultiLineString', 'coordinates': [[r5(c) for c in l] for l in gm['coordinates']]}
        else: continue
        feats[sid] = {'type': 'Feature', 'id': sid, 'properties': pr, 'geometry': gm}
    # road pieces (docs/site/build_data.py pieces_build): per ~40 m piece, the frames when the map draws water on it
    PC = BD.pieces_build([(k, f_['geometry']) for k, f_ in feats.items()], box, RES, frames[0].shape, iter(frames), ~wm)
    pw = {}
    for sid_, w_ in zip(PC['seg'], PC['w']): pw.setdefault(sid_, []).append(w_)
    # knock-on effects (proto/cascade.py on the prototype output; same model as the live replay's cascade.json)
    C = {}
    cp = os.path.join(rdir, 'cascade.json')
    if not os.path.exists(cp):
        subprocess.run([sys.executable, os.path.join(HERE, 'cascade.py'), 'outdir', rdir], check=False, stdout=subprocess.DEVNULL)
    if os.path.exists(cp):
        C = json.load(open(cp))
    pk = (C.get('totals') or {}).get('peak') or {}
    culv = []
    for x in C.get('culverts') or []:
        if x.get('first_h') is not None:
            culv.append([x.get('id'), round(x['first_h'] * 60 / FRAME_MIN, 2)])
    cser = (C.get('series') or {})
    rain_h = S.get('rain_hourly_mean_mm', [])
    num = dict(rain_total_mm=round(float(sum(rain_h)), 1), rain_peak1h_mm=S.get('rain_peak1h_max_mm'), rain_max_total_mm=S.get('rain_max_total_mm'),
               segments_in_box=S.get('segments_in_box'), segments_closed=S.get('segments_p_ge_50'), km_closed=S.get('km_p_ge_50'),
               segments_may_close=S.get('segments_may_close'), peak_closed=int(closed.max()) if nf else 0, peak_closed_frame=int(closed.argmax()) if nf else 0,
               culverts_overtopped=S.get('culverts_overtopped'), people_cut_off=pk.get('pop_isolated'), people_lost_service=pk.get('pop_lost_any'),
               first_closure_h=(C.get('totals') or {}).get('first_closure_h'), peak_wet_km2=max(wet_km2) if wet_km2 else 0,
               peak_channel_rise_km=max(rise_km) if rise_km else 0, flood_model_runtime_s=S.get('flood_model_runtime_s'))
    if num['segments_in_box']:
        num['pct_closed'] = round(100.0 * (num['segments_closed'] or 0) / num['segments_in_box'], 2)
    dj = dict(id=sc['id'], frame_min=FRAME_MIN, nf=nf, sheets=sheets, storm_start=S.get('storm_start'), numbers=num,
              closed_per_frame=closed.tolist(), wet_km2=wet_km2, channel_rise_km=rise_km, rain_hourly_mean_mm=rain_h,
              people_lost_series=[int(v) for v in (cser.get('pop_lost_any') or [])], cascade_t_h=C.get('t_h'),
              seg=segs, p=p_close, may=may_ids, pw=pw, edge={k: v for k, v in edge.items() if k in feats}, culverts=culv, env={k: v for k, v in sc['env'].items() if k.startswith('LF_')})
    json.dump(BD.clean(dj), open(os.path.join(od, 'd.json'), 'w'), separators=(',', ':'), allow_nan=False)
    try:
        BD.flow(out, keep[::max(1, FLOW_MIN // FRAME_MIN)], max(2, int(round(100 / RES))), od, BD.corners(rdir), FLOW_MIN)
        dj_flow = 'flow.json'
    except Exception as e:
        print('  flow skipped', repr(e)[:120]); dj_flow = None
    size = sum(os.path.getsize(os.path.join(od, x)) for x in os.listdir(od)) / 1e6
    print(f"{sc['id']}: {nf} frames, {len(segs)} wet segments, {num['segments_closed']} closed, {size:.1f} MB")
    return dict(num, status='ok', flow=dj_flow, size_mb=round(size, 2)), feats, wm


def crossing_table(corners):
    sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))
    from w9_lisflood import is_bridge
    import build_data as BD
    B = BD.lonlat_box(corners); X = json.load(open(os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'))); C = X['columns']
    rows, ix = [], {}
    for r in X['rows']:
        q = dict(zip(C, r))
        if not BD.inside(B, q['lon'], q['lat']): continue
        ix[q['id']] = len(rows)
        txt = lambda v: v if isinstance(v, str) and v.lower() not in ('nan', 'unknown') else ''
        rows.append([round(q['lon'], 5), round(q['lat'], 5), txt(q.get('road')), txt(q.get('stream')), int(is_bridge(q))])
    return rows, ix


def pack(results, only=None):
    import build_data as BD
    os.makedirs(SITE, exist_ok=True)
    M = matrix(); idx = dict(made=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'), made_by='proto/whatif.py', storm=STORM, box_epsg26986=BOX,
                            title='Leominster and Fitchburg, Sept 11, 2023', baseline=BASELINE, frame_min=FRAME_MIN,
                            axes=dict(rain=[dict(id=r, x=k) for r, k, _ in RAIN], soil=[dict(id=s, label=l) for s, l, _ in SOIL],
                                      culverts=[dict(id=c, label=l) for c, l, _ in CULV]),
                            settings={k: v for k, v in BASE_ENV.items() if k.startswith('LF_')}, scenarios={})
    allf = {}; wm0 = None; corners = None; t0 = None
    for sc in M:
        if only and sc['id'] not in only: continue
        rdir, out = os.path.join(results, sc['env']['NAME']), run_out(sc)
        if not (os.path.exists(os.path.join(rdir, 'summary.json')) and os.path.exists(os.path.join(out, 'frames_cm.npz'))):
            idx['scenarios'][sc['id']] = dict(status='missing'); print(sc['id'], 'missing'); continue
        try:
            S = json.load(open(os.path.join(rdir, 'summary.json'))); fh = S['frame_hours']
            snap = int(round((fh[1] - fh[0]) * 60)) if len(fh) > 1 else FRAME_MIN
            num, feats, wm = pack_one(sc, rdir, out, os.path.join(SITE, sc['id']), max(1, FRAME_MIN // snap))
        except Exception as e:
            idx['scenarios'][sc['id']] = dict(status='failed', why=repr(e)[:200]); print(sc['id'], 'failed', repr(e)[:300]); continue
        idx['scenarios'][sc['id']] = num
        for k, f in feats.items(): allf.setdefault(k, f)
        if corners is None:
            corners = BD.corners(rdir); XT, XI = crossing_table(corners)
        if sc['id'] == BASELINE or t0 is None:
            t0 = S.get('storm_start')
        if sc['id'] == BASELINE or wm0 is None:
            wm0 = (wm, out)
        dp = os.path.join(SITE, sc['id'], 'd.json'); dj = json.load(open(dp))      # overtopped culverts as rows of culverts.json
        dj['culverts'] = [[XI[c], f] for c, f in dj['culverts'] if c in XI]; json.dump(dj, open(dp, 'w'), separators=(',', ':'))
    if corners is None:
        raise SystemExit('no finished scenario run to pack')
    idx.update(corners=corners, storm_start=t0)
    json.dump(BD.clean({'type': 'FeatureCollection', 'features': list(allf.values())}), open(os.path.join(SITE, 'roads.json'), 'w'), separators=(',', ':'), allow_nan=False)
    PCU = BD.pieces_build([(k, f_['geometry']) for k, f_ in allf.items()], [float(v) for v in BOX.split(',')], RES, (1000, 1000), iter([]))
    PCU.pop('w'); PCU['about'] = 'road pieces of roads.json (geometry only); per-scenario wet intervals are <id>/d.json pw[segment][piece]'
    json.dump(PCU, open(os.path.join(SITE, 'pieces.json'), 'w'), separators=(',', ':'))
    json.dump(BD.clean(dict(columns=['lon', 'lat', 'road', 'stream', 'bridge'], note='mapped road-stream crossings in the box (docs/network/crossings_all.json); '
                   'bridge = 1 stays open when culverts are blocked (sim/colab/w9_lisflood.py is_bridge)', rows=XT)),
              open(os.path.join(SITE, 'culverts.json'), 'w'), separators=(',', ':'), allow_nan=False)
    # terrain: hillshade of the lidar DEM before the model's edits (z_raw.npz) and the mapped water / channel cells
    from PIL import Image
    wm, out = wm0
    zr = os.path.join(out, 'z_raw.npz')
    z = np.load(zr)['z_raw'] if os.path.exists(zr) else np.load(os.path.join(out, 'z.npy'))
    hs = hillshade(z, RES)
    rgb = np.zeros(z.shape + (3,), np.uint8); rgb[..., 0] = np.round(hs * 255); rgb[..., 1] = np.where(wm, 255, 0)
    zn = np.where(np.isfinite(z), z, np.nanmin(z)); lo, hi = np.percentile(zn, 1), np.percentile(zn, 99)
    rgb[..., 2] = np.round(np.clip((zn - lo) / max(hi - lo, 1), 0, 1) * 255)
    Image.fromarray(rgb, 'RGB').save(os.path.join(SITE, 'terrain.png'), optimize=True)
    idx['terrain'] = dict(sheet='terrain.png', w=int(z.shape[1]), h=int(z.shape[0]), elev_m=[round(float(lo), 1), round(float(hi), 1)],
                          note='R hillshade (lidar DEM, sun NW 40 deg), G mapped water / channel cells, B elevation 1st-99th percentile')
    ok = [k for k, v in idx['scenarios'].items() if v.get('status') == 'ok']
    idx['n_ok'] = len(ok); idx['n'] = len(M)
    import build_data as BD2
    json.dump(BD2.clean(idx), open(os.path.join(SITE, 'index.json'), 'w'), indent=0, separators=(',', ':'), allow_nan=False)
    tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(SITE) for f in fs) / 1e6
    print(f'packed {len(ok)} / {len(M)} scenarios, {len(allf)} road segments, {tot:.1f} MB in {SITE}')
    return idx


def selftest():
    """synthetic: a 40 x 50 run with a channel, two frames of rain-driven water, one segment; the packer's outputs and their shapes."""
    import tempfile
    global SITE
    d = tempfile.mkdtemp(prefix='whatif_'); os.environ['LF_WORK'] = os.path.join(d, 'work')
    sc = matrix()[0]; assert sc['id'] == BASELINE and len(matrix()) == 32
    assert all(m['env']['LF_CN_SCALE'] == '0.88' and m['env']['LF_PARITY'] == '1' for m in matrix())
    fz = [m for m in matrix() if m['soil'] == 'frozen'][0]; assert fz['env']['LF_CN_FROZEN'] == '1' and fz['env']['LF_INFIL_MMH'] == '0'
    out = run_out(sc); rdir = os.path.join(d, 'results', sc['env']['NAME']); os.makedirs(out); os.makedirs(rdir)
    ny, nx = 40, 50; z = np.add.outer(np.linspace(50, 40, ny), np.linspace(0, 5, nx)).astype(np.float32)
    wm = np.zeros((ny, nx), np.uint8); wm[:, 20] = 1
    D = np.zeros((5, ny, nx), np.uint16); D[:, :, 20] = 40; D[2, 10:20, 5:15] = 35; D[3, :, 20] = 160; D[3, 10:20, 5:15] = 20
    np.savez_compressed(os.path.join(out, 'frames_cm.npz'), depth_cm=D, hours=np.arange(5) * 0.25)
    np.save(os.path.join(out, 'watermask.npy'), wm); np.save(os.path.join(out, 'z.npy'), z)
    np.savez_compressed(os.path.join(out, 'z_raw.npz'), z_raw=z, z_raw_max10=z)
    cn = [[-71.89, 42.60], [-71.85, 42.60], [-71.85, 42.57], [-71.89, 42.57]]
    open(os.path.join(rdir, 'map.html'), 'w').write('var C=' + json.dumps(cn) + ';')
    json.dump(dict(frame_hours=[0, 0.25, 0.5, 0.75, 1.0], storm_start='2023-09-11T16:00Z', segments_in_box=10, segments_p_ge_50=1, km_p_ge_50=0.4,
                   segments_may_close=0, culverts_overtopped=0, rain_hourly_mean_mm=[5, 10], rain_peak1h_max_mm=20, rain_max_total_mm=30),
              open(os.path.join(rdir, 'summary.json'), 'w'))
    json.dump(dict(type='FeatureCollection', features=[dict(type='Feature', properties=dict(segment='7', road='Main St', town='Leominster', road_class='arterial',
              p_close=0.98, p_may_close=0, d=[0, 10, 45, 20, 0]), geometry=dict(type='LineString', coordinates=[[-71.88, 42.59], [-71.87, 42.58]]))]),
              open(os.path.join(rdir, 'segments.geojson'), 'w'))
    json.dump(dict(totals=dict(peak=dict(pop_isolated=12, pop_lost_any=40), first_closure_h=0.5), culverts=[dict(id='u55199', first_h=0.5)],
                   series=dict(pop_lost_any=[0, 40, 0])), open(os.path.join(rdir, 'cascade.json'), 'w'))
    SITE = os.path.join(d, 'site'); idx = pack(os.path.join(d, 'results'), only=[BASELINE])
    s = idx['scenarios'][BASELINE]; assert s['status'] == 'ok' and s['people_cut_off'] == 12 and s['peak_closed'] == 1, s
    dj = json.load(open(os.path.join(SITE, BASELINE, 'd.json')))
    assert dj['nf'] == 5 and dj['seg']['7'] == [0, 10, 45, 20] and dj['closed_per_frame'][2] == 1, dj
    X = json.load(open(os.path.join(SITE, 'culverts.json'))); assert X['rows'] and all(len(r) == 5 for r in X['rows'])
    from PIL import Image
    a = np.asarray(Image.open(os.path.join(SITE, BASELINE, 'depth_00.png'))).astype(int)
    code = lambda f: (a[..., f // 3] // (1, 5, 25)[f % 3]) % 5
    assert code(2)[15, 10] == 3 and code(0)[5, 20] == 0 and code(3)[5, 20] == 4 and code(3)[15, 10] == 2   # channel: rise 120 cm -> class 4
    T = np.asarray(Image.open(os.path.join(SITE, 'terrain.png'))); assert T.shape == (ny, nx, 3) and T[0, 20, 1] == 255 and T[0, 0, 1] == 0
    R = json.load(open(os.path.join(SITE, 'roads.json'))); assert R['features'][0]['id'] == 7 and R['features'][0]['properties']['n'] == 'Main St'
    shutil.rmtree(d)
    print('whatif selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('list'); e = sp.add_parser('env'); e.add_argument('index', type=int)
    p = sp.add_parser('pack'); p.add_argument('--results', default=os.path.join(ROOT, 'results')); p.add_argument('--only', help='comma-separated scenario ids')
    sp.add_parser('selftest')
    a = ap.parse_args()
    if a.cmd == 'list':
        for i, m in enumerate(matrix()): print(i, m['id'], ' '.join(f'{k}={v}' for k, v in m['env'].items() if k.startswith('LF_') and BASE_ENV.get(k) != v))
    elif a.cmd == 'env':
        m = matrix()[a.index]
        for k, v in m['env'].items(): print(f'export {k}={v}')
        print(f"export WHATIF_ID={m['id']}")
    elif a.cmd == 'pack': pack(a.results, a.only.split(',') if a.only else None)
    else: selftest()
