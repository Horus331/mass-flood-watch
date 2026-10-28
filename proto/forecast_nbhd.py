"""HRRR neighbourhood-spreading comparison for the District 3 over-forecast (docs/proto/forecast/DISTRICT.md; STATUS.md item 3).

    python proto/forecast_nbhd.py matrix --tier 1|2|3        GitHub Actions cases for the box runs (.github/workflows/forecast_nbhd.yml)
    python proto/forecast_nbhd.py rain --out rain.json       storm-total HRRR rain per spreading setting vs MRMS (District 3 + the box storms)
    python proto/forecast_nbhd.py compact --arts DIR --out docs/proto/forecast/district/boxes.json
                                                             box-run artifacts -> flagged segment ids per run (small, committed)
    python proto/forecast_nbhd.py boxes --runs docs/proto/forecast/district/boxes.json --out docs/proto/forecast/district/box_scores.json
                                                             single cycle / 2 of 8 per setting, scored like ENSEMBLE.md section 4
    python proto/forecast_nbhd.py district --out docs/proto/forecast/district/district.json
                                                             Turing District 3 hindcasts vs the radar run (share, km, CSI) + score_v2 site recall
    python proto/forecast_nbhd.py decide --district ... --boxes ...   the pre-registered rule of DISTRICT.md section 1

Settings (tags): nb20p90 = LF_HRRR_NBHD=20,90 (live; box control = the published ENSEMBLE.md members, tag 'nb'), nb10p90 = 10,90 (less area),
nb20p75 = 20,75 (lower intensity), raw = 0,50 (a 1-cell footprint: the raw HRRR field).  The box runs use exactly the ENSEMBLE.md set-up
(CN x 0.91, default step, CPU) so the 20,90 arm is the already-published members; nothing here changes the live forecast.
"""
import os, sys, json, argparse, glob, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))
OUT = os.path.join(ROOT, 'docs', 'proto', 'forecast', 'district')
VARIANTS = {'nb20p90': '20,90', 'nb10p90': '10,90', 'nb20p75': '20,75', 'raw': '0,50'}
NEW = ('nb10p90', 'nb20p75', 'raw')
TURING = {'nb20p90': 'hindcast_d3_sep2023_18z', 'nb10p90': 'hindcast_d3_18z_nb10p90', 'nb20p75': 'hindcast_d3_18z_nb20p75', 'raw': 'hindcast_d3_18z_raw'}
RADAR = 'd3_sep2023_p'
D3_BOX = '128000,856000,206000,946000'
RECHECK = ('sep2023_18z', 'aug2021_12z', 'jul2021_short', 'sep2021_short')     # 20,90 issue cycles re-run at today's commit (reuse check)


def log(*a): print(*a, flush=True)


def E():
    import forecast_ens as F; return F


def short_keys():
    F = E(); return [k for k, v in F.ENSEMBLES.items() if v['lead'] == 'short']


def long_of(storm):
    F = E(); return [k for k, v in F.ENSEMBLES.items() if v['lead'] == 'long' and v['storm'] == storm][0]


def case(k, init, tag):
    F = E(); En = F.ENSEMBLES[k]; hrs = int((F.ts(En['end']) - F.ts(init)).total_seconds() // 3600)
    return dict(name=F.member_name(k, init, tag), storm=En['storm'], box=F.BOXES[En['storm']], init=init, hours=str(hrs), env=f'LF_HRRR_NBHD={VARIANTS[tag]}')


def matrix(tier):
    """tier 1: the issue cycles (short and long lead) of every storm for the 3 new settings + 4 re-checks of 20,90;
    tier 2: the other 6 short-lead members for 10,90 and 20,75; tier 3: the same for raw.  Short-lead members always include the long-lead issue cycle."""
    F = E(); out = []
    for k in short_keys():
        En = F.ENSEMBLES[k]; issue_s = En['issue']; issue_l = F.ENSEMBLES[long_of(En['storm'])]['issue']
        assert issue_l in En['members'], (k, issue_l)
        rest = [m for m in En['members'] if m not in (issue_s, issue_l)]
        if tier == 1:
            for tag in NEW: out += [case(k, issue_s, tag), case(k, issue_l, tag)]
            if k in RECHECK: out.append(case(k, issue_s, 'nb20p90'))
        elif tier == 2: out += [case(k, m, t) for t in ('nb10p90', 'nb20p75') for m in rest]
        elif tier == 3: out += [case(k, m, 'raw') for m in rest]
    return out


# ------------------------------------------------------------------ rain diagnostic (no flood model)
def rain_cases():
    F = E(); out = [dict(id='d3_18z', box=D3_BOX, init='2023-09-11T18Z', end='2023-09-13T18:00Z', mrms_from='2023-09-11T16:00Z')]
    for k in short_keys() + ['sep2023_12z', 'aug2021_06z']:
        En = F.ENSEMBLES[k]; out.append(dict(id=k, box=F.BOXES[En['storm']], init=En['issue'], end=En['end'], mrms_from=None))
    return out


def field_stats(T, ref=None):
    s = dict(mean=round(float(T.mean()), 1), max=round(float(T.max()), 1), p50=round(float(np.percentile(T, 50)), 1),
             p90=round(float(np.percentile(T, 90)), 1), area_ge25=round(float((T >= 25).mean()), 3), area_ge50=round(float((T >= 50).mean()), 3),
             area_ge100=round(float((T >= 100).mean()), 3))
    if ref is not None:
        s['volume_ratio'] = round(float(T.sum() / max(ref.sum(), 1e-6)), 2)
        for t in (50, 100):     # area of the forecast field above t vs radar: >1 = too much area; mean rain inside that area vs radar = intensity
            a, b = T >= t, ref >= t
            s[f'area_ratio_ge{t}'] = round(float(a.sum() / b.sum()), 2) if b.any() else None
            s[f'csi_ge{t}'] = round(float((a & b).sum() / max((a | b).sum(), 1)), 3)
    return s


def cmd_rain(a):
    import pandas as pd, hrrr_rain, w9_lisflood as W
    from pyproj import Transformer
    cache = os.environ.get('LF_HRRR_DIR') or '/tmp/hrrr_cache'; res = {}
    for c in rain_cases():
        try: res[c['id']] = rain_case(c, cache, W, hrrr_rain, pd, Transformer)
        except Exception as e: log('rain case failed', c['id'], repr(e)[:200]); res[c['id']] = dict(case=c, error=repr(e)[:300])
        json.dump(res, open(a.out, 'w'), indent=1)


def rain_case(c, cache, W, hrrr_rain, pd, Transformer):
    if True:
        x0, y0, x1, y1 = (float(v) for v in c['box'].split(','))
        tr = Transformer.from_crs(26986, 4326, always_xy=True); lo0, la0 = tr.transform(x0, y0); lo1, la1 = tr.transform(x1, y1)
        lat_c = np.arange(max(la0, la1), min(la0, la1), -0.01); lon_c = np.arange(min(lo0, lo1), max(lo0, lo1), 0.01)
        LA, LO = np.meshgrid(lat_c, lon_c, indexing='ij'); XX, YY = Transformer.from_crs(4326, 26986, always_xy=True).transform(LO, LA)
        init = hrrr_rain.parse_init(c['init']); end = pd.Timestamp(c['end']).tz_localize(None) if pd.Timestamp(c['end']).tzinfo is None else pd.Timestamp(c['end']).tz_convert(None)
        nh = min(int((end - init).total_seconds() // 3600), hrrr_rain.horizon(init))
        msgs = [hrrr_rain.apcp(init, fh, cache=cache) for fh in range(1, nh + 1)]
        m1 = next(m for m in msgs if m is not None); G = hrrr_rain.LccGrid(m1); tot = {}; peak = {}
        for tag, spec in VARIANTS.items():
            os.environ['LF_HRRR_NBHD'] = spec; smp = G.bilinear(XX, YY)
            H = np.stack([smp(m) if m is not None else np.zeros(XX.shape, np.float32) for m in msgs]); tot[tag] = H.sum(0); peak[tag] = float(H.max())
        os.environ.pop('LF_HRRR_NBHD', None)
        gp = '/tmp/q_nbhd.grib2'; R = []
        for h in range(nh):
            ts = init + pd.Timedelta(hours=h + 1)
            try: raw_, _, _ = W.mrms_fetch_raw(ts, W.mrms_http_fetch); R.append(W.mrms_sample(raw_, lat_c, lon_c, gp))
            except Exception as e: log('no MRMS', ts, repr(e)[:80]); R.append(np.zeros(XX.shape, np.float32))
        R = np.stack(R); ref = R.sum(0)
        r = dict(case=c, hours=nh, points=int(ref.size), mrms=dict(field_stats(ref), peak1h=round(float(R.max()), 1)),
                 hrrr={t: dict(field_stats(tot[t], ref), peak1h=round(peak[t], 1)) for t in VARIANTS})
        if c.get('mrms_from'):     # the radar flood run starts 2 h before the cycle: its extra rain, for reference
            t0 = pd.Timestamp(c['mrms_from']).tz_convert(None); pre = []
            for h in range(int((init - t0).total_seconds() // 3600)):
                raw_, _, _ = W.mrms_fetch_raw(t0 + pd.Timedelta(hours=h + 1), W.mrms_http_fetch); pre.append(W.mrms_sample(raw_, lat_c, lon_c, gp))
            r['mrms_before_cycle_mean_mm'] = round(float(np.stack(pre).sum(0).mean()), 1) if pre else 0.0
        log(c['id'], json.dumps(dict(mrms=r['mrms'], **{t: r['hrrr'][t] for t in VARIANTS}))[:900])
        return r


# ------------------------------------------------------------------ box runs
def cmd_compact(a):
    """artifacts (one folder per run with seg.json / summary.json / w9_log.txt) -> {name: {flagged ids at P_depth >= 0.5, n_inbox, rain}}"""
    out = {}
    for d in sorted(glob.glob(os.path.join(a.arts, '*'))):
        sj = glob.glob(os.path.join(d, '**', 'seg.json'), recursive=True)
        if not sj: continue
        D = json.load(open(sj[0])); name = os.path.basename(d).replace('nbhd_', '', 1)
        P = np.asarray(D['p_depth']); ids = np.asarray(D['inbox'])
        r = dict(n_segments=D['n_segments'], n_inbox=len(ids), flagged=sorted(int(i) for i in ids[P >= 0.5]))
        wl = glob.glob(os.path.join(d, '**', 'w9_log.txt'), recursive=True)
        for ln in (open(wl[0]).read().splitlines() if wl else []):
            if ' rain: max ' in ln or ln.startswith('rain: max') or 'rain: max' in ln:
                try: r['rain_max_mm'] = float(ln.split('max ')[1].split(' mm')[0]); r['rain_mean_mm'] = float(ln.split('mean ')[1].split(' mm')[0])
                except Exception: pass
        out[name] = r
    json.dump(out, open(a.out, 'w'), indent=0, separators=(',', ':')); log(len(out), 'runs ->', a.out)


def _member_flags(k, init, tag, runs):
    """(flagged bool array or None, inbox) for one member; nb20p90 = the published ENSEMBLE.md member (tag 'nb')."""
    F = E()
    if tag == 'nb20p90':
        p = os.path.join(F.ENS_DIR, F.member_name(k, init, 'nb'), 'seg.json')
        if not os.path.exists(p): return None
        D, P, inb = F.load_dump(p); return (P >= 0.5) & inb
    r = runs.get(F.member_name(k, init, tag))
    if r is None: return None
    fl = np.zeros(r['n_segments'], bool); fl[r['flagged']] = True; return fl


def cmd_boxes(a):
    F = E(); runs = json.load(open(a.runs)) if a.runs and os.path.exists(a.runs) else {}
    res = dict(cases={}, pooled={}, recheck={})
    for k in short_keys():
        En = F.ENSEMBLES[k]; kl = long_of(En['storm'])
        D0, _, inb = F.load_dump(os.path.join(F.ENS_DIR, F.member_name(k, En['issue'], 'nb'), 'seg.json'))
        oos = bool(En.get('oos'))
        for tag in VARIANTS:
            row = dict(storm=En['storm'], oos=oos, sites=len(D0['strict']))
            for lead, kk in (('short', k), ('long', kl)):
                fl = _member_flags(kk, F.ENSEMBLES[kk]['issue'], tag, runs)
                row[f'single_{lead}'] = F.recall(D0['strict'], fl.astype(np.float32), inb, 0.5) if fl is not None else None
            mem = [_member_flags(k, m, tag, runs) for m in En['members']]; got = [m for m in mem if m is not None]
            row['members_done'] = len(got)
            if len(got) == len(mem):
                kc = np.sum(got, axis=0).astype(np.float32); row['kofn_2of8_short'] = F.recall(D0['strict'], kc, inb, 1.5)
                row['any_short'] = F.recall(D0['strict'], kc, inb, 0.5)
            else: row['kofn_2of8_short'] = None
            res['cases'][f'{En["storm"]}|{tag}'] = row
    for grp, sel in (('oos7', lambda r: r['oos']), ('dev', lambda r: not r['oos'])):
        for tag in VARIANTS:
            rows = [r for key, r in res['cases'].items() if key.endswith('|' + tag) and sel(r)]
            P = {}
            for rule in ('single_short', 'single_long', 'kofn_2of8_short'):
                rr = [r[rule] for r in rows]
                if any(x is None for x in rr) or not rr: P[rule] = None; continue
                hits = sum(round(x['recall'] * x['n']) for x in rr); n = sum(x['n'] for x in rr)
                exp_ = sum(x['random_recall'] * x['n'] for x in rr)
                P[rule] = dict(hits=hits, n=n, recall=round(hits / n, 3), mean_flagged=round(float(np.mean([x['flagged_share'] for x in rr])), 4),
                               max_flagged=round(float(np.max([x['flagged_share'] for x in rr])), 4), lift=round(hits / exp_, 2) if exp_ > 0 else None)
            res['pooled'][f'{grp}|{tag}'] = P
    for k in RECHECK:      # today's code vs the published 20,90 member: same flagged set?
        En = F.ENSEMBLES[k]; r = runs.get(F.member_name(k, En['issue'], 'nb20p90'))
        if r is None: continue
        old = set(np.nonzero(_member_flags(k, En['issue'], 'nb20p90', {}))[0].tolist()); new = set(r['flagged'])
        res['recheck'][k] = dict(old=len(old), new=len(new), jaccard=round(len(old & new) / max(len(old | new), 1), 3))
    json.dump(res, open(a.out, 'w'), indent=1); log(json.dumps(res['pooled'], indent=0)[:3000]); log(res['recheck'])


# ------------------------------------------------------------------ District 3 (Turing)
def _segs(run):
    p = os.path.join(ROOT, 'docs', 'proto', 'turing', run, 'segments.geojson')
    if not os.path.exists(p): return None
    G = json.load(open(p)); return {int(f['properties']['segment']): (float(f['properties'].get('p_close') or 0), float(f['properties'].get('length_m') or 0))
                                   for f in G['features']}


def cmd_district(a):
    import subprocess
    R = _segs(RADAR); Rs = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'turing', RADAR, 'summary.json')))
    Rset = {s for s, (p, _) in R.items() if p >= 0.5}; out = dict(radar=dict(run=RADAR, n=Rs['segments_p_ge_50'], km=Rs['km_p_ge_50']), runs={})
    for tag, run in TURING.items():
        d = os.path.join(ROOT, 'docs', 'proto', 'turing', run)
        if not os.path.exists(os.path.join(d, 'summary.json')): out['runs'][tag] = None; continue
        S = json.load(open(os.path.join(d, 'summary.json')))
        r = dict(run=run, n=S['segments_p_ge_50'], km=S['km_p_ge_50'], ratio_n=round(S['segments_p_ge_50'] / Rs['segments_p_ge_50'], 3),
                 ratio_km=round(S['km_p_ge_50'] / Rs['km_p_ge_50'], 3), rain_max=S.get('rain_max_total_mm'), rain_peak1h=S.get('rain_peak1h_max_mm'),
                 rain_mean=json.load(open(os.path.join(d, 'flood_meta.json'))).get('rain_total_mean_mm') if os.path.exists(os.path.join(d, 'flood_meta.json')) else None)
        Sg = _segs(run)
        if Sg is not None:
            Fset = {s for s, (p, _) in Sg.items() if p >= 0.5}; H = len(Fset & Rset)
            r.update(hits=H, misses=len(Rset - Fset), false=len(Fset - Rset), csi=round(H / max(len(Fset | Rset), 1), 3),
                     radar_recall=round(H / max(len(Rset), 1), 3), precision=round(H / max(len(Fset), 1), 3))
            if os.path.exists(os.path.join(d, 'flood_meta.json')):
                tmp = os.path.join(a.tmp, f'v2_{tag}.json')
                subprocess.run([sys.executable, os.path.join(HERE, 'score_v2.py'), '--run', d, '--storm', 'sep2023', '--out', tmp], check=False,
                               stdout=subprocess.DEVNULL)
                if os.path.exists(tmp):
                    b = json.load(open(tmp))['domains']['box']; ru = b['rule']; s3 = b['shares']['0.03']
                    r['v2'] = dict(n_sites=b['n_sites'], rule_site_hits=ru['site_hits'], rule_site_recall=round(ru['site_recall'], 3), rule_lift=round(ru['lift'], 2),
                                   rule_share=round(ru['share'], 4), top3_site_recall=round(s3['site_recall'], 3), top3_lift=round(s3['lift'], 2))
        else: r['csi'] = None
        out['runs'][tag] = r
    rv = os.path.join(a.tmp, 'v2_radar.json')
    subprocess.run([sys.executable, os.path.join(HERE, 'score_v2.py'), '--run', os.path.join(ROOT, 'docs', 'proto', 'turing', RADAR), '--storm', 'sep2023',
                    '--out', rv], check=False, stdout=subprocess.DEVNULL)
    if os.path.exists(rv):
        b = json.load(open(rv))['domains']['box']; ru = b['rule']; s3 = b['shares']['0.03']
        out['radar']['v2'] = dict(n_sites=b['n_sites'], rule_site_hits=ru['site_hits'], rule_site_recall=round(ru['site_recall'], 3), rule_lift=round(ru['lift'], 2),
                                  rule_share=round(ru['share'], 4), top3_site_recall=round(s3['site_recall'], 3), top3_lift=round(s3['lift'], 2))
    json.dump(out, open(a.out, 'w'), indent=1); log(json.dumps(out, indent=1))


# ------------------------------------------------------------------ the pre-registered decision (DISTRICT.md section 1)
def decide(district, boxes):
    runs = {t: r for t, r in district['runs'].items() if r}
    eligible = [t for t, r in runs.items() if 0.7 <= r['ratio_n'] <= 1.3 and 0.7 <= r['ratio_km'] <= 1.3]
    P = boxes['pooled']
    def box_key(t):      # box-level hindcast winner: OOS-7 2-of-8 short-lead hits, then single-cycle short+long hits, then lift
        p = P.get(f'oos7|{t}', {}); k = p.get('kofn_2of8_short') or {}; s = [p.get('single_short') or {}, p.get('single_long') or {}]
        return (k.get('hits', -1), sum(x.get('hits', 0) for x in s), k.get('lift') or 0)
    def veto(t):         # box-level veto: may lose at most 1 OOS-7 site under 2 of 8 (short lead) vs 20,90
        if t == 'nb20p90': return False
        a_, b_ = (P.get(f'oos7|{t}') or {}).get('kofn_2of8_short'), (P.get('oos7|nb20p90') or {}).get('kofn_2of8_short')
        if not a_ or not b_:     # ensemble incomplete: fall back to single cycle, both leads pooled
            a2 = sum(((P.get(f'oos7|{t}') or {}).get(r) or {}).get('hits', 0) for r in ('single_short', 'single_long'))
            b2 = sum(((P.get('oos7|nb20p90') or {}).get(r) or {}).get('hits', 0) for r in ('single_short', 'single_long'))
            return a2 < b2 - 1
        return a_['hits'] < b_['hits'] - 1
    why = []
    if eligible:
        cs = {t: runs[t].get('csi') for t in eligible}
        if any(v is None for v in cs.values()): why.append(f'CSI missing for {[t for t, v in cs.items() if v is None]}: ranked by |ln ratio_n| instead')
        key = lambda t: (cs[t] if cs[t] is not None else -1, -abs(math.log(runs[t]['ratio_n'])))
        best = max(cs[t] if cs[t] is not None else -1 for t in eligible)
        tied = [t for t in eligible if (cs[t] if cs[t] is not None else -1) >= best - 0.01]
        win = max(tied, key=box_key) if len(tied) > 1 else tied[0]
        why.append(f'eligible (share and km within +-30 % of radar): {eligible}; CSI {cs}; tied within 0.01: {tied}; district winner {win}')
    else:
        lr = {t: abs(math.log(r['ratio_n'])) for t, r in runs.items()}; win = min(lr, key=lr.get)
        why.append(f'no setting within +-30 %; closest |ln ratio_n| {lr} -> {win}')
        if win != 'nb20p90' and lr[win] > 0.5 * lr.get('nb20p90', 1e9): why.append('not half-way (in log terms) to the radar share: keep 20,90'); win = 'nb20p90'
    if win != 'nb20p90' and veto(win): why.append(f'{win} vetoed at box level (loses > 1 OOS-7 site vs 20,90): keep 20,90'); win = 'nb20p90'
    return win, why


def cmd_decide(a):
    win, why = decide(json.load(open(a.district)), json.load(open(a.boxes)))
    log('DECISION:', win, VARIANTS[win]); [log(' -', w) for w in why]
    if a.out: json.dump(dict(winner=win, setting=VARIANTS[win], why=why), open(a.out, 'w'), indent=1)


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    m = sp.add_parser('matrix'); m.add_argument('--tier', type=int, required=True)
    r = sp.add_parser('rain'); r.add_argument('--out', required=True)
    c = sp.add_parser('compact'); c.add_argument('--arts', required=True); c.add_argument('--out', required=True)
    b = sp.add_parser('boxes'); b.add_argument('--runs'); b.add_argument('--out', required=True)
    d = sp.add_parser('district'); d.add_argument('--out', required=True); d.add_argument('--tmp', default='/tmp')
    k = sp.add_parser('decide'); k.add_argument('--district', required=True); k.add_argument('--boxes', required=True); k.add_argument('--out')
    a = ap.parse_args()
    if a.cmd == 'matrix': print(json.dumps(matrix(a.tier)))
    elif a.cmd == 'rain': cmd_rain(a)
    elif a.cmd == 'compact': cmd_compact(a)
    elif a.cmd == 'boxes': cmd_boxes(a)
    elif a.cmd == 'district': cmd_district(a)
    elif a.cmd == 'decide': cmd_decide(a)


if __name__ == '__main__':
    main()
