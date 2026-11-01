"""District 3 forecast map: the neighbourhood percentile chosen on the development storms so the district rain volume matches the radar
(docs/proto/forecast/DISTRICT_VOLCAL.md, pre-registered in DISTRICT_VOLCAL_PREREG.md).  Rain fields only, no flood model.

    python proto/forecast_volcal.py rain --out docs/proto/forecast/district/volcal_rain.json      HRRR storm totals per setting vs MRMS
    python proto/forecast_volcal.py choose --rain ...json                                          P* from the dev cycles only
    python proto/forecast_volcal.py decide --rain ...json [--out ...]                              the pre-registered held-out rule

Every case is one HRRR issue cycle of forecast_ens.ENSEMBLES (dev: sep2023_12z/18z, aug2021_06z/12z; held-out: the long- and short-lead
issue cycles of the 7 OOS storms), read over the whole District 3 run domain (forecast_nbhd.D3_BOX) on a 0.01 deg grid, from the cycle to
the ensemble's end time (capped at the cycle's horizon), against MRMS Pass2 over the same hours.  Settings: LF_HRRR_NBHD = 20,P for the
grid P below, and 0,50 (raw)."""
import os, sys, json, argparse, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))
GRID_P = (50, 60, 70, 75, 80, 85, 90)
VARIANTS = {**{f'nb20p{p}': f'20,{p}' for p in GRID_P}, 'raw': '0,50'}
LIVE = 'nb20p90'
DEV_CASES = ('sep2023_12z', 'sep2023_18z', 'aug2021_06z', 'aug2021_12z')


def log(*a): print(*a, flush=True)


def cases():
    import forecast_ens as F, forecast_nbhd as N
    out = []
    for k, E in F.ENSEMBLES.items():
        out.append(dict(id=k, storm=E['storm'], lead=E.get('lead'), dev=k in DEV_CASES, init=E['issue'], end=E['end'], box=N.D3_BOX, storm_box=F.BOXES[E['storm']]))
    return out


def stats(T, ref, mask=None):
    if mask is not None: T, ref = T[mask], ref[mask]
    s = dict(hrrr_mean=round(float(T.mean()), 2), mrms_mean=round(float(ref.mean()), 2), hrrr_vol=float(T.sum()), mrms_vol=float(ref.sum()),
             volume_ratio=round(float(T.sum() / max(ref.sum(), 1e-6)), 3))
    for t in (25, 50):
        a, b = T >= t, ref >= t
        s[f'area_hrrr_ge{t}'] = int(a.sum()); s[f'area_mrms_ge{t}'] = int(b.sum()); s[f'inter_ge{t}'] = int((a & b).sum()); s[f'union_ge{t}'] = int((a | b).sum())
    return s


def cmd_rain(a):
    import pandas as pd, hrrr_rain, w9_lisflood as W
    from pyproj import Transformer
    cache = os.environ.get('LF_HRRR_DIR') or '/tmp/hrrr_cache'; res = json.load(open(a.out)) if os.path.exists(a.out) else {}
    for c in cases():
        if c['id'] in res and 'error' not in res[c['id']]: continue
        try:
            x0, y0, x1, y1 = (float(v) for v in c['box'].split(','))
            tr = Transformer.from_crs(26986, 4326, always_xy=True); lo0, la0 = tr.transform(x0, y0); lo1, la1 = tr.transform(x1, y1)
            lat_c = np.arange(max(la0, la1), min(la0, la1), -0.01); lon_c = np.arange(min(lo0, lo1), max(lo0, lo1), 0.01)
            LA, LO = np.meshgrid(lat_c, lon_c, indexing='ij'); XX, YY = Transformer.from_crs(4326, 26986, always_xy=True).transform(LO, LA)
            bx0, by0, bx1, by1 = (float(v) for v in c['storm_box'].split(',')); inbox = (XX >= bx0) & (XX < bx1) & (YY >= by0) & (YY < by1)
            init = hrrr_rain.parse_init(c['init']); end = pd.Timestamp(c['end']); end = end.tz_convert(None) if end.tzinfo else end
            nh = min(int((end - init).total_seconds() // 3600), hrrr_rain.horizon(init))
            msgs = [hrrr_rain.apcp(init, fh, cache=cache) for fh in range(1, nh + 1)]
            m1 = next(m for m in msgs if m is not None); G = hrrr_rain.LccGrid(m1); tot = {}
            for tag, spec in VARIANTS.items():
                os.environ['LF_HRRR_NBHD'] = spec; smp = G.bilinear(XX, YY)
                tot[tag] = np.stack([smp(m) if m is not None else np.zeros(XX.shape, np.float32) for m in msgs]).sum(0)
            os.environ.pop('LF_HRRR_NBHD', None)
            gp = '/tmp/q_volcal.grib2'; R = np.zeros(XX.shape, np.float32); miss = 0
            for h in range(nh):
                ts = init + pd.Timedelta(hours=h + 1)
                try: raw_, _, _ = W.mrms_fetch_raw(ts, W.mrms_http_fetch); R += W.mrms_sample(raw_, lat_c, lon_c, gp)
                except Exception as e: miss += 1; log('no MRMS', ts, repr(e)[:80])
            res[c['id']] = dict(case=c, hours=nh, mrms_missing_hours=miss, hrrr_missing_hours=sum(m is None for m in msgs), points=int(R.size),
                                d3={t: stats(tot[t], R) for t in VARIANTS}, storm_box={t: stats(tot[t], R, inbox) for t in VARIANTS})
            log(c['id'], {t: res[c['id']]['d3'][t]['volume_ratio'] for t in VARIANTS})
        except Exception as e:
            log('case failed', c['id'], repr(e)[:300]); res[c['id']] = dict(case=c, error=repr(e)[:300])
        json.dump(res, open(a.out, 'w'), indent=1)


def pooled_ratio(R, ids, tag, dom='d3'):
    h = sum(R[i][dom][tag]['hrrr_vol'] for i in ids); m = sum(R[i][dom][tag]['mrms_vol'] for i in ids); return h / max(m, 1e-9)


def choose(R):
    """P*: the grid percentile whose pooled District 3 volume ratio over the 4 dev cycles is closest to 1 (|ln ratio|); ties -> the higher P."""
    ids = [i for i in DEV_CASES if i in R and 'error' not in R[i]]
    if len(ids) < 2: raise SystemExit(f'only {len(ids)} dev cycles available: no choice')
    sc = {f'nb20p{p}': abs(math.log(pooled_ratio(R, ids, f'nb20p{p}'))) for p in GRID_P}
    best = min(sc.values()); star = max((t for t, v in sc.items() if v <= best + 1e-9), key=lambda t: int(t[5:]))
    return star, dict(dev_cycles=ids, abs_ln_ratio={t: round(v, 3) for t, v in sc.items()}, pooled_ratio={t: round(pooled_ratio(R, ids, t), 3) for t in VARIANTS})


def decide(R):
    star, ch = choose(R)
    ho = [i for i, v in R.items() if 'error' not in v and not v['case']['dev']]
    def med_abs_ln(tag, key):
        v = []
        for i in ho:
            s = R[i]['d3'][tag]
            if key == 'volume': r = s['hrrr_vol'] / max(s['mrms_vol'], 1e-9)
            else:
                if s['area_mrms_ge25'] == 0 and s['area_hrrr_ge25'] == 0: continue
                r = (s['area_hrrr_ge25'] + 0.5) / (s['area_mrms_ge25'] + 0.5)
            v.append(abs(math.log(max(r, 1e-6))))
        return float(np.median(v)) if v else float('nan')
    def csi(tag, t=25):
        i_ = sum(R[i]['d3'][tag][f'inter_ge{t}'] for i in ho); u_ = sum(R[i]['d3'][tag][f'union_ge{t}'] for i in ho); return i_ / max(u_, 1)
    rep = {tag: dict(median_abs_ln_volume_ratio=round(med_abs_ln(tag, 'volume'), 3), median_abs_ln_area25_ratio=round(med_abs_ln(tag, 'area'), 3),
                     pooled_volume_ratio=round(pooled_ratio(R, ho, tag), 3), pooled_csi_ge25=round(csi(tag), 3), pooled_csi_ge50=round(csi(tag, 50), 3),
                     storm_box_pooled_volume_ratio=round(pooled_ratio(R, ho, tag, 'storm_box'), 3)) for tag in VARIANTS}
    L, S = rep[LIVE], rep[star]
    checks = dict(volume_closer=S['median_abs_ln_volume_ratio'] < L['median_abs_ln_volume_ratio'], area_closer=S['median_abs_ln_area25_ratio'] < L['median_abs_ln_area25_ratio'],
                  csi25_not_worse=S['pooled_csi_ge25'] >= L['pooled_csi_ge25'] - 0.02)
    return dict(p_star=star, choice=ch, heldout_cycles=ho, heldout=rep, checks=checks, adopt_for_district_map=bool(star != LIVE and all(checks.values())))


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    r = sp.add_parser('rain'); r.add_argument('--out', required=True)
    c = sp.add_parser('choose'); c.add_argument('--rain', required=True)
    d = sp.add_parser('decide'); d.add_argument('--rain', required=True); d.add_argument('--out')
    a = ap.parse_args()
    if a.cmd == 'rain': cmd_rain(a)
    elif a.cmd == 'choose': print(json.dumps(choose(json.load(open(a.rain))), indent=1))
    else:
        v = decide(json.load(open(a.rain))); print(json.dumps(v, indent=1))
        if a.out: json.dump(v, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
