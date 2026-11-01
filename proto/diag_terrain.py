"""Terrain-conditioning diagnostics (docs/proto/terrain/): build the model DEM of a box with sim/colab/w9_lisflood.build_inputs under several
env settings (default, LF_NOTCH_FIX=1, LF_NOTCH_FIX=1 LF_CHAN_ENFORCE=1, ...) and report the closed depressions the solver will see:
cells, and road points (docs/graph_segments.json) that sit in a closed basin more than 1 / 3 m deep, crossing notches cut far below the raw
lidar, and named check points.  No flood run, no rain beyond one hour (build_inputs needs it).

    BOX=157000,882000,177000,902000 STORM=jul2023 HF_TOKEN=... python proto/diag_terrain.py --out DIR \
        --cfg base= --cfg notch=LF_NOTCH_FIX=1 --cfg notch_enf="LF_NOTCH_FIX=1 LF_CHAN_ENFORCE=1" --pt 12771:176050,891561

Writes DIR/terrain_<cfg>.json, DIR/pits_<cfg>.npz (crop arrays around the check points) and DIR/summary.json."""
import os, sys, json, time, argparse, heapq
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab')); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))


def fill_depth(Z):
    """Depth of every cell below its D4 spill level (priority flood from the box edge, face neighbours only, as LISFLOOD-FP exchanges water)."""
    ny, nx = Z.shape; F = Z.astype(np.float64).ravel().copy(); seen = np.zeros(F.size, bool); h = []
    edge = np.zeros(Z.shape, bool); edge[[0, -1], :] = True; edge[:, [0, -1]] = True
    for k in np.flatnonzero(edge): h.append((F[k], int(k))); seen[k] = True
    heapq.heapify(h)
    while h:
        z, k = heapq.heappop(h); r, c = divmod(k, nx)
        for kk in ((k - nx) if r else -1, (k + nx) if r < ny - 1 else -1, (k - 1) if c else -1, (k + 1) if c < nx - 1 else -1):
            if kk >= 0 and not seen[kk]:
                seen[kk] = True
                if F[kk] < z: F[kk] = z
                heapq.heappush(h, (F[kk], kk))
    return (F.reshape(Z.shape) - Z).astype(np.float32)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--cfg', action='append', default=[])
    ap.add_argument('--pt', action='append', default=[], help='name:x,y (EPSG:26986)'); ap.add_argument('--crop', type=int, default=40)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    import w9_lisflood as W9, impacts as IM
    BOX = tuple(float(v) for v in os.environ['BOX'].split(',')); RES = float(os.environ.get('RES', '20')); STORM = os.environ.get('STORM', 'sep2023')
    S = W9.storm_cfg(STORM); S['hours'] = 1; TOK = os.environ.get('HF_TOKEN'); os.makedirs(W9.WORK, exist_ok=True); W9.LOGP = os.path.join(W9.WORK, 'w9_log.txt')
    x0, y0, x1, y1 = BOX
    meta = dict(box=list(BOX), res_m=RES, shape=[int((y1 - y0) / RES), int((x1 - x0) / RES)])
    SG = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); P = IM.road_points(SG, meta)
    pts = [(p.split(':')[0], *[float(v) for v in p.split(':')[1].split(',')]) for p in a.pt]
    base_env = dict(os.environ); summ = {}
    for cfg in a.cfg:
        name, _, envs = cfg.partition('='); t = time.time()
        os.environ.clear(); os.environ.update(base_env)
        for kv in envs.split():
            k, _, v = kv.partition('='); os.environ[k] = v
        I = W9.build_inputs(BOX, RES, S, TOK); Z = I['Z']; ZR = I['Z_RAW']
        D = fill_depth(Z); pd = D[P['r'], P['c']]; low = ZR - Z
        segs1 = np.unique(P['seg'][pd > 1.0]); segs3 = np.unique(P['seg'][pd > 3.0])
        XG = I.get('XG') or []
        res = dict(cfg=name, env=envs, box=list(BOX), storm=STORM, cells_pit_gt1m=int((D > 1).sum()), cells_pit_gt3m=int((D > 3).sum()),
                   pit_volume_m3=round(float(D.sum() * RES * RES)), road_points=int(len(pd)), road_points_pit_gt1m=int((pd > 1).sum()),
                   road_points_pit_gt3m=int((pd > 3).sum()), segments_pit_gt1m=segs1.tolist(), segments_pit_gt3m=segs3.tolist(),
                   cells_lowered_gt5m=int((low > 5).sum()), road_points_lowered_gt3m=int((low[P['r'], P['c']] > 3).sum()),
                   crossings=len(XG), notches_cut_gt5m=sum(1 for g in XG if g['zcrest'] - g['zcut'] > 5),
                   seg_names={int(s): [SG['props']['road'][s], SG['props']['town'][s]] for s in segs1}, points={}, seconds=round(time.time() - t))
        crops = {}
        for nm, x, y in pts:
            r, c = int((y1 - y) // RES), int((x - x0) // RES); w = np.s_[max(0, r - a.crop):r + a.crop + 1, max(0, c - a.crop):c + a.crop + 1]
            res['points'][nm] = dict(r=r, c=c, z=round(float(Z[r, c]), 2), z_raw=round(float(ZR[r, c]), 2), pit_depth=round(float(D[r, c]), 2),
                                     pit_depth_3x3_max=round(float(D[max(0, r - 1):r + 2, max(0, c - 1):c + 2].max()), 2), chan_3x3=bool(I['chan'][max(0, r - 1):r + 2, max(0, c - 1):c + 2].any()))
            crops[f'{nm}_z'] = Z[w]; crops[f'{nm}_zraw'] = ZR[w]; crops[f'{nm}_pit'] = D[w]; crops[f'{nm}_chan'] = I['chan'][w]
        np.savez_compressed(os.path.join(a.out, f'pits_{name}.npz'), **crops)
        json.dump(res, open(os.path.join(a.out, f'terrain_{name}.json'), 'w'), indent=1)
        summ[name] = {k: v for k, v in res.items() if k not in ('seg_names', 'segments_pit_gt1m')}
        print(json.dumps(summ[name]), flush=True)
    json.dump(summ, open(os.path.join(a.out, 'summary.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
