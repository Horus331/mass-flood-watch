"""Longer-lead forecast experiments: time-lagged HRRR ensemble and HRRR -> MRMS quantile mapping (docs/proto/forecast/ENSEMBLE.md).

    python proto/forecast_ens.py proto  --run-dir <flood out> --out <dir> --storm sep2023 --dump seg.json
                                        prototype.py with its defaults, plus seg.json: P_depth of every in-box segment and the label-site matches
    python proto/forecast_ens.py qmfit  --out docs/proto/forecast/qmap.json [--only ids]
                                        hourly HRRR vs MRMS histograms on the AWS catalogue storms -> leave-one-storm-out quantile maps
    python proto/forecast_ens.py report [--md docs/proto/forecast/ENSEMBLE.md]
                                        members -> P(close) = share of members with P_depth >= 0.5; recall / flagged share / lift per threshold
    python proto/forecast_ens.py selftest

The scoring is prototype.py's own label_recall (strict 30 m and loose matches, chance-corrected lift), applied to the ensemble probability.
Nothing here is used by the live forecast.
"""
import os, sys, json, argparse, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))
OUT = os.path.join(ROOT, 'docs', 'proto', 'forecast')
ENS_DIR = os.path.join(OUT, 'ensemble')

# time-lagged ensembles: the cycles that were on the web at the time of the evaluated cycle, valid for the same storm window.
# hourly cycles (18 h horizon) only back to the one whose horizon still covers the storm's main rain; the synoptic cycles (48 h) further back.
ENSEMBLES = {
    'sep2023_12z': dict(storm='sep2023', issue='2023-09-11T12Z', first_report='2023-09-11T21:10Z', end='2023-09-13T04:00Z',
                        members=['2023-09-11T12Z', '2023-09-11T11Z', '2023-09-11T10Z', '2023-09-11T09Z', '2023-09-11T08Z',
                                 '2023-09-11T06Z', '2023-09-11T00Z', '2023-09-10T18Z']),
    'aug2021_06z': dict(storm='aug2021', issue='2021-08-19T06Z', first_report='2021-08-19T15:38Z', end='2021-08-20T03:00Z',
                        members=['2021-08-19T06Z', '2021-08-19T05Z', '2021-08-19T04Z', '2021-08-19T03Z', '2021-08-19T02Z',
                                 '2021-08-19T00Z', '2021-08-18T18Z', '2021-08-18T12Z']),
    # the same at the short lead (the cycles the deterministic hindcast already handles well), to check the ensemble does not lose skill there
    'sep2023_18z': dict(storm='sep2023', issue='2023-09-11T18Z', first_report='2023-09-11T21:10Z', end='2023-09-13T04:00Z',
                        members=['2023-09-11T18Z', '2023-09-11T17Z', '2023-09-11T16Z', '2023-09-11T15Z', '2023-09-11T14Z',
                                 '2023-09-11T12Z', '2023-09-11T06Z', '2023-09-11T00Z']),
    'aug2021_12z': dict(storm='aug2021', issue='2021-08-19T12Z', first_report='2021-08-19T15:38Z', end='2021-08-20T03:00Z',
                        members=['2021-08-19T12Z', '2021-08-19T11Z', '2021-08-19T10Z', '2021-08-19T09Z', '2021-08-19T08Z',
                                 '2021-08-19T06Z', '2021-08-19T00Z', '2021-08-18T18Z']),
}

# out-of-sample storms (rules fixed in advance, ENSEMBLE.md section 4): long lead = the newest 00/06/12/18z cycle issued >= 8 h before the first
# report, short lead = the next one (6 h later); members = that cycle, the 3 synoptic cycles before it and the 4 hourly cycles before it.
OOS_STORMS = ['jul2021', 'sep2021', 'sep2022', 'jul2023', 'aug2023', 'aug2023b', 'aug2026']
BOXES = {'sep2023': '168000,908000,188000,928000', 'aug2021': '168000,875000,188000,895000'}     # the HINDCAST.md boxes; others: catalogue box


def _oos():
    import pandas as pd
    C = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']}
    out = {}
    for sid in OOS_STORMS:
        e = C[sid]; f = pd.Timestamp(e['first_report_utc']).tz_convert(None); end = pd.Timestamp(e['t0']).tz_convert(None) + pd.Timedelta(hours=e['hours'])
        BOXES[sid] = ','.join(str(int(v)) for v in e['box_26986'])
        TL = (f - pd.Timedelta(hours=8)).floor('6h')
        for lead, T in (('long', TL), ('short', TL + pd.Timedelta(hours=6))):
            mem = [T] + [T - pd.Timedelta(hours=h) for h in (1, 2, 3, 4)] + [T - pd.Timedelta(hours=h) for h in (6, 12, 18)]
            out[f'{sid}_{lead}'] = dict(storm=sid, issue=f'{T:%Y-%m-%dT%H}Z', first_report=f'{f:%Y-%m-%dT%H:%M}Z', end=f'{end:%Y-%m-%dT%H:%M}Z',
                                        members=[f'{m:%Y-%m-%dT%H}Z' for m in mem], oos=True, lead=lead,
                                        mrms=dict(t0=e['t0'], hours=e['hours']))
    return out


for _k, _v in (('sep2023_12z', 'long'), ('aug2021_06z', 'long'), ('sep2023_18z', 'short'), ('aug2021_12z', 'short')): ENSEMBLES[_k]['lead'] = _v
ENSEMBLES.update(_oos())


def log(*a): print(*a, flush=True)


def ts(s):
    import hrrr_rain; return hrrr_rain.parse_init(s)


def member_name(ens, init, tag='nb'):
    t = ts(init); return f"{ENSEMBLES[ens]['storm']}_m{t:%d%H}z_{tag}"


def matrix(which='members', ens=None):
    """GitHub Actions matrix JSON for the member runs (each: storm, box, init, hours, env, name)."""
    import pandas as pd
    BOX = BOXES; out = []
    for k, E in ENSEMBLES.items():
        if ens and k not in ens.split(','): continue
        end = ts(E['end'])
        for m in E['members']:
            if any(o['name'] == member_name(k, m) for o in out): continue
            hrs = int((end - ts(m)).total_seconds() // 3600)
            out.append(dict(name=member_name(k, m), storm=E['storm'], box=BOX[E['storm']], init=m, hours=str(hrs), env='LF_HRRR_NBHD=20,90'))
        if which == 'all' and E.get('mrms') and not any(o['name'] == f"{E['storm']}_mrms" for o in out):
            out.append(dict(name=f"{E['storm']}_mrms", storm=E['storm'], box=BOX[E['storm']], init='mrms', hours=str(E['mrms']['hours']), env=''))
    return out


# ------------------------------------------------------------------ prototype with a per-segment dump
def cmd_proto(a):
    import prototype as PT
    rec = []
    orig = PT.label_recall
    def spy(matches, P, inbox, thr=0.5):
        rec.append((matches, P, inbox)); return orig(matches, P, inbox, thr)
    PT.label_recall = spy
    labels = (sorted(glob.glob(os.path.join(HERE, 'data', f'labels_{a.storm}_*.csv'))) + sorted(glob.glob(os.path.join(HERE, 'data', f'labels_{a.storm}_*.geojson'))) or [None])[0]
    PT.run(a.run_dir, a.out, os.path.join(ROOT, 'docs', 'graph_segments.json'), os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'),
           os.path.join(ROOT, 'docs', 'prone', 'flood_reports.json'), os.path.join(ROOT, 'docs', 'network', 'facilities.json'),
           os.path.join(HERE, 'data', 'massdot_repeat_flood_d3.csv'), 30, os.environ.get('PROTO_CULVERT_RULE', '0') == '1', labels, True,
           os.environ.get('PROTO_FREEBOARD', '0') == '1', os.environ.get('PROTO_FASTWATER', '0') == '1', os.environ.get('PROTO_EDGE', '0') == '1')
    # call order in prototype.run: depth_rule(LM, p_depth), with_culverts(LM, p_comb), loose depth_rule(LL, p_depth), ...
    (LM, Pd, inbox), (LL, Pd2, _) = rec[0], rec[2]
    assert Pd2 is Pd, 'prototype.label_recall call order changed'
    idx = np.nonzero(inbox)[0]
    def mm(M): return [dict(id=L.get('id'), type=L.get('type'), segs=[int(s) for s in segs]) for L, segs in M]
    json.dump(dict(labels=os.path.basename(labels or ''), n_segments=int(len(Pd)), inbox=idx.tolist(), p_depth=[round(float(v), 3) for v in Pd[idx]],
                   strict=mm(LM), loose=mm(LL)), open(a.dump, 'w'))
    log('dump', a.dump, len(idx), 'in-box segments,', int((Pd[idx] >= 0.5).sum()), 'at P >= 0.5')


# ------------------------------------------------------------------ scoring of a probability over the in-box segments
def recall(matches, P, inb, thr):
    """prototype.label_recall, group 'all': P and inb are full-length arrays."""
    fl = (P >= thr) & inb; f = float(fl[inb].mean()) if inb.any() else 0.0
    if not matches: return dict(flagged_share=round(f, 4), n_flagged=int(fl.sum()))
    hit = np.array([fl[np.asarray(m['segs'])].any() for m in matches]); exp_ = np.array([1 - (1 - f) ** len(m['segs']) for m in matches])
    return dict(flagged_share=round(f, 4), n_flagged=int(fl.sum()), n=len(matches), recall=round(float(hit.mean()), 3), random_recall=round(float(exp_.mean()), 3),
                lift=round(float(hit.mean() / exp_.mean()), 2) if exp_.mean() > 0 else None)


def load_dump(path):
    D = json.load(open(path)); P = np.zeros(D['n_segments'], np.float32); inb = np.zeros(D['n_segments'], bool)
    P[D['inbox']] = D['p_depth']; inb[D['inbox']] = True; return D, P, inb


def ensemble_scores(dumps):
    """dumps: list of seg.json paths (one per member) -> P_ens = share of members with P_depth >= 0.5, scored at every k / N."""
    Ds = [load_dump(p) for p in dumps]; D0, _, inb = Ds[0]
    for D, _, i2 in Ds[1:]: assert (i2 == inb).all(), 'members disagree on the in-box segments'
    hits = np.stack([(P >= 0.5) for _, P, _ in Ds]).astype(np.float32); N = len(Ds); Pe = hits.mean(0); Pm = np.stack([P for _, P, _ in Ds]).mean(0)
    rows = []
    for k in range(1, N + 1):
        thr = (k - 0.5) / N
        rows.append(dict(k=k, n=N, p_ens_ge=round(k / N, 3), strict=recall(D0['strict'], Pe, inb, thr), loose=recall(D0['loose'], Pe, inb, thr)))
    meanP = {f'{t:.2f}': dict(strict=recall(D0['strict'], Pm, inb, t), loose=recall(D0['loose'], Pm, inb, t)) for t in (0.1, 0.25, 0.5)}
    # reliability against the label sites: per P_ens level, how many strict label sites have their best segment at that level
    best = [float(Pe[np.asarray(m['segs'])].max()) for m in D0['strict']]
    lev = {f'{k}/{N}': sum(1 for b in best if abs(b - k / N) < 1e-6) for k in range(N + 1)}
    seg_lev = {f'{k}/{N}': int(((np.abs(Pe - k / N) < 1e-6) & inb).sum()) for k in range(N + 1)}
    return dict(members=N, by_threshold=rows, mean_p_depth=meanP, label_sites_by_level=lev, segments_by_level=seg_lev)


# ------------------------------------------------------------------ quantile-mapping fit
EDGES = np.concatenate([[0.0, 0.05], np.geomspace(0.1, 400.0, 240), [1e6]])


def cmd_qmfit(a):
    import pandas as pd, gzip, tempfile, pygrib, hrrr_rain
    from forecast import cycles_before
    from pyproj import Transformer
    C = [e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events'] if e.get('era') == 'aws']
    if a.only: C = [e for e in C if e['id'] in a.only.split(',')]
    tr = Transformer.from_crs(26986, 4326, always_xy=True); res = {}
    for ev in C:
        bx = ev['box_26986']; m = a.margin_km * 1000.0
        xs = np.arange(bx[0] - m + 500, bx[2] + m, 1000.0); ys = np.arange(bx[1] - m + 500, bx[3] + m, 1000.0); XX, YY = np.meshgrid(xs, ys)
        LO, LA = tr.transform(XX.ravel(), YY.ravel()); t0 = ts(ev['t0']); hours = [t0 + pd.Timedelta(hours=h + 1) for h in range(ev['hours'])]
        # MRMS Pass2 1 km, nearest cell
        mr = []
        for t in hours:
            u = (f'https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MultiSensor_QPE_01H_Pass2_00.00/{t:%Y%m%d}/'
                 f'MRMS_MultiSensor_QPE_01H_Pass2_00.00_{t:%Y%m%d-%H%M%S}.grib2.gz')
            r = hrrr_rain._get(u, timeout=120)
            if r is None: log(ev['id'], 'no MRMS', t); continue
            with tempfile.NamedTemporaryFile(suffix='.grib2') as f:
                f.write(gzip.decompress(r.content)); f.flush(); g = pygrib.open(f.name); msg = g[1]
                la, lo = msg.latlons(); v = np.maximum(np.ma.filled(msg.values, 0), 0); g.close()
            lat1 = la[:, 0]; lon1 = np.where(lo[0] > 180, lo[0] - 360, lo[0])
            ii = np.clip(np.rint((LA - lat1[0]) / (lat1[1] - lat1[0])).astype(int), 0, len(lat1) - 1)
            jj = np.clip(np.rint((LO - lon1[0]) / (lon1[1] - lon1[0])).astype(int), 0, len(lon1) - 1)
            mr.append(v[ii, jj].astype(np.float32))
        R = dict(points=int(LA.size), hours=len(mr), mrms=np.histogram(np.concatenate(mr), EDGES)[0].tolist() if mr else None,
                 mrms_max1h=round(float(np.max(mr)), 1) if mr else None, cycles={})
        first = ev.get('first_report_utc') or ev['t0']
        for init in cycles_before(first, n=3):
            H = hrrr_rain.horizon(init); m1 = hrrr_rain.apcp(init, 1)
            if m1 is None: continue
            G = hrrr_rain.LccGrid(m1); smp = {}
            for var, nb in (('raw', ''), ('nb20p90', '20,90')):
                os.environ['LF_HRRR_NBHD'] = nb; smp[var] = G.bilinear(XX, YY)
            os.environ.pop('LF_HRRR_NBHD', None)
            vals = {k: [] for k in smp}
            for t in hours:
                fh = int((t - init).total_seconds() // 3600)
                if not 1 <= fh <= H: continue
                msg = hrrr_rain.apcp(init, fh)
                if msg is None: continue
                for k, s in smp.items(): vals[k].append(s(msg).ravel())
            lead = round((ts(first) - init).total_seconds() / 3600, 1)
            R['cycles'][f'{init:%Y-%m-%dT%H}Z'] = dict(lead_h=lead, hours=len(vals['raw']),
                                                       **{k: np.histogram(np.concatenate(v), EDGES)[0].tolist() for k, v in vals.items() if v},
                                                       **{k + '_max1h': round(float(np.max(v)), 1) for k, v in vals.items() if v})
            log(ev['id'], f'{init:%Y-%m-%d %H}z', 'lead', lead, 'hours', len(vals['raw']), 'max1h raw / nb', R['cycles'][f'{init:%Y-%m-%dT%H}Z'].get('raw_max1h'),
                R['cycles'][f'{init:%Y-%m-%dT%H}Z'].get('nb20p90_max1h'), 'MRMS', R['mrms_max1h'])
        res[ev['id']] = R
    out = dict(edges=EDGES.tolist(), margin_km=a.margin_km,
               note='per AWS catalogue storm: hourly accumulations at 1 km points over the storm box + margin, over the catalogue MRMS window; MRMS Pass2 '
                    '(nearest 1 km cell) and the HRRR cycles before the first report (bilinear, raw and 20 km / 90th pct neighbourhood) as histograms',
               storms=res)
    out['maps'] = fit_maps(out)
    json.dump(out, open(a.out, 'w'))


def quantiles(counts, probs):
    c = np.asarray(counts, np.float64); cdf = np.concatenate([[0], np.cumsum(c)]) / max(c.sum(), 1)
    return np.interp(probs, cdf, EDGES[:len(cdf)].clip(max=400.0))


def fit_maps(Q, probs=None):
    """Leave-one-storm-out (and all-storm) quantile maps HRRR -> MRMS from the stored histograms.  Every storm gets equal weight: its MRMS and
    pooled-cycle HRRR histograms are normalised before summing."""
    probs = probs if probs is not None else np.concatenate([np.linspace(0.5, 0.99, 50), 1 - np.geomspace(0.01, 1e-4, 30)])
    S = Q['storms']; maps = {}
    for out_id in [None] + list(S):
        for var in ('raw', 'nb20p90'):
            mh = np.zeros(len(EDGES) - 1); hh = np.zeros(len(EDGES) - 1); used = []
            for sid, R in S.items():
                if sid == out_id or not R.get('mrms'): continue
                hc = [np.asarray(c[var], float) for c in R['cycles'].values() if c.get(var)]
                if not hc: continue
                m_ = np.asarray(R['mrms'], float); h_ = sum(hc)
                mh += m_ / m_.sum(); hh += h_ / h_.sum(); used.append(sid)
            if not used: continue
            x = quantiles(hh, probs); y = quantiles(mh, probs); ok = x > 0.1
            x, y = x[ok], y[ok]
            if len(x) < 3: continue
            x = np.maximum.accumulate(x + np.arange(len(x)) * 1e-6); y = np.maximum.accumulate(y)
            maps[f"{'loso_' + out_id if out_id else 'all'}/{var}"] = dict(x=[round(float(v), 3) for v in x], y=[round(float(v), 3) for v in y], storms=used,
                                                                          probs=[round(float(p), 5) for p, k in zip(probs, ok) if k])
    return maps


# ------------------------------------------------------------------ report
def cmd_report(a):
    from forecast import metrics
    import pandas as pd
    rows = dict(made=pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%dT%H:%MZ'), ensembles={}, runs={})
    T = []
    for k, E in ENSEMBLES.items():
        dumps = [os.path.join(ENS_DIR, member_name(k, m), 'seg.json') for m in E['members']]
        have = [p for p in dumps if os.path.exists(p)]
        mem = []
        for m, p in zip(E['members'], dumps):
            d = os.path.dirname(p)
            if os.path.exists(os.path.join(d, 'summary.json')):
                mt = metrics(d); mem.append(dict(init=m, lead_h=round((ts(E['first_report']) - ts(m)).total_seconds() / 3600, 1), **{q: mt[q] for q in ('rain_max_mm', 'rain_peak1h_mm', 'flagged_share', 'recall', 'lift', 'loose_recall')}))
        r = dict(storm=E['storm'], issue=E['issue'], members_expected=len(dumps), members_found=len(have), members=mem)
        if len(have) >= 2: r['ensemble'] = ensemble_scores(have)
        syn = [p for m, p in zip(E['members'], dumps) if ts(m).hour % 6 == 0 and os.path.exists(p)]
        hrl = [p for i, (m, p) in enumerate(zip(E['members'], dumps)) if (i == 0 or ts(m).hour % 6) and os.path.exists(p)]
        if len(syn) >= 2: r['ensemble_synoptic'] = ensemble_scores(syn)
        if len(hrl) >= 2: r['ensemble_hourly'] = ensemble_scores(hrl)
        rows['ensembles'][k] = r
    for d in sorted(glob.glob(os.path.join(ENS_DIR, '*'))):
        if os.path.exists(os.path.join(d, 'summary.json')) and '_m' not in os.path.basename(d):
            rows['runs'][os.path.basename(d)] = metrics(d)
    json.dump(rows, open(os.path.join(OUT, 'ensemble.json'), 'w'), indent=1)
    print(json.dumps(rows, indent=1)[:6000])


def selftest():
    D = dict(n_segments=6, inbox=[0, 1, 2, 3, 4], p_depth=[0.9, 0.1, 0.6, 0.0, 0.0], strict=[dict(id='L1', type='flooded', segs=[0]), dict(id='L2', type='flooded', segs=[1, 3])],
             loose=[dict(id='L1', type='flooded', segs=[0, 1])])
    import tempfile
    d = tempfile.mkdtemp(); p1 = os.path.join(d, 'a.json'); p2 = os.path.join(d, 'b.json'); json.dump(D, open(p1, 'w'))
    D2 = dict(D, p_depth=[0.2, 0.7, 0.6, 0.0, 0.0]); json.dump(D2, open(p2, 'w'))
    E = ensemble_scores([p1, p2]); r1 = E['by_threshold'][0]['strict']; r2 = E['by_threshold'][1]['strict']
    assert r1['recall'] == 1.0 and abs(r1['flagged_share'] - 0.6) < 1e-6, r1      # any member: segs 0, 1, 2
    assert r2['recall'] == 0.0 and abs(r2['flagged_share'] - 0.2) < 1e-6, r2      # both members: seg 2 only
    import hrrr_ens
    qm = (np.array([1.0, 10.0]), np.array([2.0, 30.0])); v = hrrr_ens.apply_qmap(np.array([0, 0.5, 1, 5.5, 10, 20], np.float32), qm)
    assert np.allclose(v, [0, 1, 2, 16, 30, 60]), v
    h = np.zeros(len(EDGES) - 1); h[0] = 50; h[100] = 50; q = quantiles(h, [0.25, 0.75]); assert q[0] < 0.05 and EDGES[100] <= q[1] <= EDGES[101], q
    print('selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('proto'); p.add_argument('--run-dir', required=True); p.add_argument('--out', required=True); p.add_argument('--storm', required=True); p.add_argument('--dump', required=True)
    p = sp.add_parser('qmfit'); p.add_argument('--out', required=True); p.add_argument('--only'); p.add_argument('--margin-km', type=float, default=20.0)
    p = sp.add_parser('refit'); p.add_argument('--qmap', default=os.path.join(OUT, 'qmap.json'))
    p = sp.add_parser('matrix'); p.add_argument('--ens'); p.add_argument('--which', default='members'); p.add_argument('--skip-existing', action='store_true')
    sp.add_parser('report'); sp.add_parser('selftest')
    a = ap.parse_args()
    if a.cmd == 'proto': cmd_proto(a)
    elif a.cmd == 'qmfit': cmd_qmfit(a)
    elif a.cmd == 'refit': Q = json.load(open(a.qmap)); Q['maps'] = fit_maps(Q); json.dump(Q, open(a.qmap, 'w'))
    elif a.cmd == 'matrix': print(json.dumps([c for c in matrix(a.which, a.ens) if not (a.skip_existing and os.path.exists(os.path.join(ENS_DIR, c['name'], 'summary.json')))]))
    elif a.cmd == 'report': cmd_report(a)
    else: selftest()
