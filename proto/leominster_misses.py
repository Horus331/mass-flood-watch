"""Phase 1 deep dive: why the model missed Leominster DPW damage sites, 11 Sep 2023 (docs/proto/phase1/LEOMINSTER_MISSES.md).

    python proto/leominster_misses.py [--run docs/proto/parity/catalog/sep2023_leominster_20m] [--out docs/proto/phase1/leominster_misses.json]

For each of the 54 DPW damage points (exact surveyed coordinates): the road segments matched within 30 m (score_v2), and the model's values
on them (run features: peak depth, time over 15 / 30 cm, peak speed, culvert / overtop / edge / washout flags, HAND, stream distance, slope).
Hit = any matched segment with p_close >= 0.5 (the deployed rule).  Every miss gets ONE class, by the first rule that applies (rules fixed
in the doc before this was run):
  label        no road segment within 30 m (the point is off the modelled road network)
  culvert      DPW type culvert_failure, or the DPW note names a headwall or a brook, or a matched segment is <= 30 m from a stream
  drainage     the DPW note names a storm drain or gutter line
  debris       the DPW note says debris
  flow         modelled water on the segment is shallow (< 0.30 m) but fast: peak speed >= 0.5 m/s (bare-soil permissible velocity,
               FHWA HEC-15 range 0.5-0.6 m/s): erosion by flowing water, the soil / edge mechanism a ponding threshold cannot see
  terrain      near miss in depth: peak depth 0.15-0.30 m on a matched segment, or >= 0.30 m on a segment 30-60 m away
  unexplained  little modelled water at all
"""
import argparse, csv, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
FLOW_MS = 0.5


def F(x, d=0.0):
    try: return float(x)
    except (TypeError, ValueError): return d


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--run', default='docs/proto/parity/catalog/sep2023_leominster_20m')
    ap.add_argument('--out', default='docs/proto/phase1/leominster_misses.json'); a = ap.parse_args()
    import score_v2 as S
    from scipy.spatial import cKDTree
    R = S.load_run(a.run, 'sep2023'); seg = list(R['seg'])
    rows = {int(r['segment']): r for r in csv.DictReader(open(os.path.join(a.run, 'features_sep2023.csv')))}
    D = {r['id']: r for r in csv.DictReader(open(os.path.join(HERE, 'data', 'labels_sep2023_leominster_dpw.csv')))}
    T = cKDTree(np.column_stack([R['px'], R['py']]))
    out = []
    for l in R['labels']:
        if not l['key'].startswith('labels_sep2023_leominster_dpw.csv:'): continue
        d = D[l['id']]; q = d['quote'].lower(); m = R['matches'].get(l['key'], [])
        F_ = [rows[int(seg[i])] for i in m]
        near = sorted({int(R['pidx'][k]) for k in T.query_ball_point([l['x'], l['y']], 60.0)} - set(m))
        dep = max([F(r['peak_depth_m']) for r in F_], default=0.0); spd = max([F(r['peak_speed_ms']) for r in F_], default=0.0)
        dep_near = max([F(rows[int(seg[i])]['peak_depth_m']) for i in near], default=0.0)
        hit = any(F(r['p_close']) >= 0.5 for r in F_)
        sd = min([F(r['stream_dist_m'], 1e9) for r in F_], default=1e9)
        if hit: c = 'hit'
        elif not m: c = 'label'
        elif d['type'] == 'culvert_failure' or 'headwall' in q or 'brook' in q or sd <= 30: c = 'culvert'
        elif 'storm drain' in q or 'gutter' in q: c = 'drainage'
        elif 'debris' in q: c = 'debris'
        elif dep < 0.30 and spd >= FLOW_MS: c = 'flow'
        elif 0.15 <= dep < 0.30 or dep_near >= 0.30: c = 'terrain'
        else: c = 'unexplained'
        out.append(dict(id=l['id'], note=d['quote'], dpw_type=d['type'], cls=c, matched=len(m), peak_depth_m=round(dep, 3),
                        peak_speed_ms=round(spd, 2), depth_within_60m=round(dep_near, 3), stream_dist_m=round(sd, 1) if sd < 1e9 else None,
                        hours_over_15cm=max([F(r['hours_over_15cm']) for r in F_], default=0.0),
                        p_edge=max([F(r['p_edge']) for r in F_], default=0.0), p_washout=max([F(r['p_washout']) for r in F_], default=0.0),
                        slope_pct=max([F(r['slope_pct']) for r in F_], default=0.0), hand_m=min([F(r['hand_m'], 99) for r in F_], default=None),
                        road_class=F_[0]['road_class'] if F_ else None))
    from collections import Counter
    C = Counter(r['cls'] for r in out)
    edge = [r for r in out if 'edge' in r['note'].lower()]
    sm = dict(points=len(out), classes=dict(C), edge_notes=len(edge), edge_hits=sum(r['cls'] == 'hit' for r in edge),
              median_speed_missed=float(np.median([r['peak_speed_ms'] for r in out if r['cls'] != 'hit' and r['matched']] or [0])),
              median_depth_missed=float(np.median([r['peak_depth_m'] for r in out if r['cls'] != 'hit' and r['matched']] or [0])),
              p_washout_flag_on_missed=sum(r['p_washout'] >= 0.5 for r in out if r['cls'] != 'hit'),
              p_edge_flag_on_missed=sum(r['p_edge'] >= 0.5 for r in out if r['cls'] != 'hit'))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(dict(made_by='proto/leominster_misses.py', run=a.run, flow_threshold_ms=FLOW_MS, summary=sm, points=out), open(a.out, 'w'), indent=1)
    print(json.dumps(sm, indent=1))


if __name__ == '__main__':
    main()
