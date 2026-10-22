"""Input-uncertainty ensemble for the road-closure prototype: every road segment gets P_ens(close) = share of members in which it closes.

    python proto/ensemble.py design   --n 12 --seed 2023091 --center-env "<proto.yml default env>" --out members.json   # matrix for proto_ens.yml
    python proto/ensemble.py member   --run-dir <w9 out dir> --out <member dir> --member-json '<one design entry>'     # after w9, per member
    python proto/ensemble.py aggregate --members <dir of member dirs> --out docs/proto/ens/<name>                       # after the matrix
    python proto/ensemble.py --selftest                                                                                    # offline, synthetic

Members vary the main uncertain inputs of sim/colab/w9_lisflood.py around the current default (the "center", proto.yml env), by Latin
hypercube sampling (fixed seed) of these spreads.  Each spread is a 1-sigma in log space; samples are truncated at +-2 sigma.

  rain     LF_RAIN_SCALE   lognormal, sigma_ln 0.20 (about +-20 % 1-sigma) on the storm-total MRMS field (one multiplier per member).
           Radar-rain error is multiplicative and shrinks with accumulation and gauge correction (Ciach, Krajewski & Villarini 2007, J. Hydromet.
           8:1325, product-error-driven uncertainty model for NEXRAD QPE; Villarini & Krajewski 2010, Surv. Geophys. 31:107, review of radar-rainfall
           error sources).  MRMS QPE 01H Pass2 is the gauge-corrected multi-sensor product (Zhang et al. 2016, BAMS 97:621, MRMS QPE initial
           operating capabilities); its event-total bias at gauges is of order 10-30 %, so 0.20 is the middle of the range for a 48-h storm total.
           A single storm-wide factor is the mean-field-bias part of the error; sub-storm spatial error is not sampled (caveat).
  CN       LF_CN_SCALE     normal, sd 0.10 about the center CN scale, truncated +-2 sd (CN after scaling clipped to 30-98 by w9).  Event-to-event
           CN scatter: NRCS NEH Part 630 ch. 10 (2004) Table 10-1 gives the AMC I / III (dry / wet) CNs, which Hjelmfelt (1991, J. Hydraul.
           Eng. 117:725) showed bracket roughly the 10 % / 90 % event values of a watershed's CN.  For CN 75 that is 56 / 87 (x0.74 / x1.16).
           The Sept 2023 storm came after the wettest July-August on record in central MA, so the dry tail (AMC I) is not sampled: +-10 % per
           sd reaches AMC III (x1.16) at 1.6 sd.
  n chan   LF_N_CHAN       lognormal about the center (0.035), sigma_ln 0.25.  Chow (1959) Open-Channel Hydraulics Table 5-6 min / normal / max for
           natural main channels (clean, winding with pools and stones: 0.033 / 0.040 / 0.045; sluggish weedy reaches up to 0.08), and the
           base-plus-adjustments method of Arcement & Schneider (1989, USGS Water-Supply Paper 2339) give -20 % / +30-60 % around a normal value.
  n land   LF_N_LAND_SCALE lognormal multiplier of every land Manning n (floodplain 0.08, dense urban 0.10), sigma_ln 0.35.  Chow Table 5-6
           flood plains: brush / trees min-max spans x0.5-x1.6 of normal; Arcement & Schneider (1989) floodplain adjustments (vegetation, obstructions)
           add 0.002-0.10 to a 0.02-0.03 base.  Wider than the channel because land cover is generalised (two classes).
  drain    LF_INFIL_MMH    lognormal about the center (2 mm/h), sigma_ln 0.40: steady drainage of ponded water.  NRCS NEH 630 ch. 7 minimum
           infiltration rates, HSG C 1.3-3.8 mm/h, D 0-1.3, B 3.8-7.6 (Musgrave 1955); x0.45-x2.2 at 2 sd covers C with part of B and D.

Member 'm00' is the center itself (all multipliers 1): the single-run reference the ensemble is compared with.

Per member (member): proto/prototype.py run() on the member's w9 output (no map / frames), capturing every in-box segment's peak depth, P_depth,
overtopping P and freeboard f (second-lowest road point, the prototype's rule), arrival time; label matches; gauges (score.py rise + timing,
w9 xings.json peak flow).  -> member.json (small).
Aggregate: P_ens(close | depth rule) = share of members with peak depth >= 0.30 m; P_ens(close | overtop candidate) = share with depth >= 0.30 m or
f < 0; p_mean = members' physics-prior P averaged; gauge 5/50/95 % bands vs observed; Brier score and reliability bins against the documented
sites (proto/data/labels_sep2023_leominster.csv) for the ensemble and the single run.
"""
import os, sys, json, math, argparse, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)

SEED = 2023091          # Sept 2023 storm
TRUNC = 2.0             # samples truncated at +-2 sigma
# name: (env var, kind, spread, source short)
PARAMS = [
    ('rain', 'LF_RAIN_SCALE', 'lognormal_mult', 0.20, 'Ciach et al. 2007; Villarini & Krajewski 2010; Zhang et al. 2016 (MRMS)'),
    ('cn', 'LF_CN_SCALE', 'normal_mult', 0.10, 'NRCS NEH 630 ch.10 Table 10-1 (AMC I/III); Hjelmfelt 1991'),
    ('n_chan', 'LF_N_CHAN', 'lognormal_mult', 0.25, 'Chow 1959 Table 5-6; Arcement & Schneider 1989 (USGS WSP 2339)'),
    ('n_land', 'LF_N_LAND_SCALE', 'lognormal_mult', 0.35, 'Chow 1959 Table 5-6 (flood plains); Arcement & Schneider 1989'),
    ('drain', 'LF_INFIL_MMH', 'lognormal_mult', 0.40, 'NRCS NEH 630 ch.7 minimum infiltration rates by HSG (Musgrave 1955)'),
]
DEFAULTS = {'LF_RAIN_SCALE': 1.0, 'LF_CN_SCALE': 1.0, 'LF_N_CHAN': 0.035, 'LF_N_LAND_SCALE': 1.0, 'LF_INFIL_MMH': 4.0}   # w9 defaults when unset
FAIL_M = 0.30


def parse_env(s):
    out = {}
    for tok in (s or '').split():
        if '=' in tok: k, v = tok.split('=', 1); out[k] = v
    return out


def norm_ppf(u):
    from scipy.stats import norm
    return norm.ppf(u)


def design(n, seed, center_env):
    """Latin hypercube in len(PARAMS) dimensions (one stratum per member per dimension, random position inside it, independent permutations),
    mapped to truncated normal z, then to each parameter.  Returns [center m00] + n members, each {name, env, mult}."""
    rng = np.random.default_rng(seed); d = len(PARAMS)
    U = np.empty((n, d))
    for j in range(d): U[:, j] = (rng.permutation(n) + rng.random(n)) / n
    from scipy.stats import norm
    lo, hi = norm.cdf(-TRUNC), norm.cdf(TRUNC); Z = norm.ppf(lo + U * (hi - lo))
    C = parse_env(center_env); members = [dict(name='m00', env=' '.join(f'{k}={v}' for k, v in C.items()), z={}, mult={}, center=True)]
    for i in range(n):
        E = dict(C); z = {}; mult = {}
        for j, (nm, var, kind, s, _) in enumerate(PARAMS):
            c = float(C.get(var, DEFAULTS[var])); m = math.exp(s * Z[i, j]) if kind == 'lognormal_mult' else 1.0 + s * Z[i, j]
            E[var] = f'{c * m:.4g}'; z[nm] = round(float(Z[i, j]), 3); mult[nm] = round(m, 4)
            if var == 'LF_N_CHAN' and C.get('LF_SGC') == '1': E['LF_SGCN'] = f"{float(C.get('LF_SGCN', '0.035')) * m:.4g}"   # sub-grid channels take their own n
        members.append(dict(name=f'm{i + 1:02d}', env=' '.join(f'{k}={v}' for k, v in E.items()), z=z, mult=mult, center=False))
    return members


# ------------------------------------------------------------------------------------------------------------------------------- member
def member(run_dir, out, mdef, labels=None):
    """prototype.run() on one member's w9 output with the heavy outputs switched off; capture per-segment rows and label matches."""
    import prototype as PR
    os.makedirs(out, exist_ok=True); cap = dict(rows=[], matches={})
    _reason = PR.reason
    def reason_cap(r):
        cap['rows'].append(r); return _reason(r)
    _ls = PR.label_segments
    def ls_cap(labels_, Q, props, meta, strict=True):
        m = _ls(labels_, Q, props, meta, strict); cap['matches']['strict' if strict else 'loose'] = [(L.get('id'), L.get('type'), [int(s) for s in sg]) for L, sg in m]; return m
    PR.reason = reason_cap; PR.label_segments = ls_cap
    PR.write_map = lambda *a, **k: None; PR.write_figure = lambda *a, **k: None; PR.depth_png = lambda *a, **k: None
    tmp = os.path.join(out, '_proto'); t0 = time.time()
    # no frames in the member run (they only feed the animated map): hide frames_cm.npz from prototype by a load_npz wrapper
    _lnz = PR.load_npz
    PR.load_npz = lambda p: None if os.path.basename(p) == 'frames_cm.npz' else _lnz(p)
    summ = PR.run(run_dir, tmp, os.path.join(ROOT, 'docs', 'graph_segments.json'), os.path.join(ROOT, 'docs', 'network', 'crossings_all.json'),
                  os.path.join(ROOT, 'docs', 'prone', 'flood_reports.json'), os.path.join(ROOT, 'docs', 'network', 'facilities.json'),
                  os.path.join(HERE, 'data', 'massdot_repeat_flood_d3.csv'),
                  labels_csv=labels or os.path.join(HERE, 'data', 'labels_sep2023_leominster.csv'))
    rows = cap['rows']
    seg = dict(id=[r['segment'] for r in rows], depth=[r['peak_depth_m'] for r in rows], p_depth=[r['p_depth'] for r in rows],
               p_ot=[r['p_overtop'] for r in rows], fb=[r['freeboard_m'] for r in rows], arr=[r['arrival_h'] for r in rows],
               h30=[r['hours_over_30cm'] for r in rows])
    gauges = []
    if os.path.exists(os.path.join(run_dir, 'frames_cm.npz')):
        import score as SC
        try:
            os.environ.setdefault('SCORE_WINDOWS', os.path.join(out, '_gw.npz'))
            sc = SC.score(run_dir, os.path.join(ROOT, 'docs', 'proto', 'obs', 'gauges_sep2023.json')); gauges = sc['gauges']
        except Exception as e: print('score failed', repr(e))
    xq = {}
    if os.path.exists(os.path.join(run_dir, 'xings.json')):
        for g in json.load(open(os.path.join(run_dir, 'xings.json'))).get('gauges', []) or []: xq[str(g.get('site'))] = g
    meta = json.load(open(os.path.join(run_dir, 'meta.json')))
    t0m = meta.get('t0')
    for g in gauges:
        q = xq.get(str(g['site']), {}); g['model_peak_q_m3s'] = q.get('q_peak_m3s'); g['model_q_peak_h'] = q.get('q_peak_h')
        g['model_peak_h'] = round((_iso(g['model_peak_utc']) - _iso(t0m)).total_seconds() / 3600, 2)
        g['obs_peak_h'] = round((_iso(g['obs_peak_utc']) - _iso(t0m)).total_seconds() / 3600, 2)
    for s_, g in xq.items():          # gauges with a flow line but no stage series in the box (score.py skips those)
        if not any(str(x['site']) == s_ for x in gauges) and g.get('q_peak_m3s') is not None:
            gauges.append(dict(site=s_, name=g.get('name'), model_peak_q_m3s=g.get('q_peak_m3s'), obs_peak_q_m3s=g.get('obs_peak_q_m3s'), model_q_peak_h=g.get('q_peak_h')))
    M = dict(member=mdef, run=meta.get('run'), t0=t0m, box=meta['box'], res_m=meta['res_m'], hours=len(meta.get('frames', [])) * meta.get('frame_min', 30) / 60,
             env=meta.get('inputs', {}).get('env'), rain_total_mean_mm=meta.get('rain_total_mean_mm'), runtime_s=meta.get('runtime_s'),
             summary={k: summ.get(k) for k in ('segments_in_box', 'segments_p_ge_50', 'segments_may_close', 'closures_expected', 'culverts_overtopped')},
             segments=seg, matches=cap['matches'], gauges=gauges, made=time.strftime('%Y-%m-%d %H:%M'), prototype_s=round(time.time() - t0, 1))
    import gzip
    with gzip.open(os.path.join(out, 'member.json.gz'), 'wt') as f_: json.dump(M, f_, separators=(',', ':'))
    import shutil; shutil.rmtree(tmp, ignore_errors=True)
    print('member', mdef.get('name'), 'segments', len(rows), 'p>=0.5', summ.get('segments_p_ge_50'), 'gauges', len(gauges))
    return M


def _iso(s):
    import datetime as dt
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00')).astimezone(dt.timezone.utc)


# ---------------------------------------------------------------------------------------------------------------------------- aggregate
def brier(p, y):
    p = np.asarray(p, float); y = np.asarray(y, float)
    return float(np.mean((p - y) ** 2)) if len(p) else None


def reliability(p, y, edges=(0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0001)):
    p = np.asarray(p, float); y = np.asarray(y, float); out = []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (p >= a) & (p < b)
        out.append(dict(bin=f'{a:.2f}-{min(b, 1):.2f}', n=int(m.sum()), mean_p=round(float(p[m].mean()), 3) if m.any() else None,
                        obs_freq=round(float(y[m].mean()), 3) if m.any() else None, n_pos=int(y[m].sum())))
    return out


def scores(p, y):
    b = brier(p, y); ybar = float(np.mean(y)); bref = ybar * (1 - ybar)
    # Murphy decomposition on the bins: reliability - resolution + uncertainty
    return dict(brier=round(b, 5), brier_climatology=round(bref, 5), bss=round(1 - b / bref, 4) if bref > 0 else None, n=int(len(y)), n_pos=int(np.sum(y)),
                bins=reliability(p, y))


def pct(v, q):
    v = [x for x in v if x is not None]
    return round(float(np.percentile(v, q)), 3) if v else None


def aggregate(mdir, out, name=None):
    import gzip
    files = sorted(os.path.join(mdir, d, f) for d in os.listdir(mdir) for f in ('member.json', 'member.json.gz') if os.path.exists(os.path.join(mdir, d, f)))
    MS = [json.load(gzip.open(f, 'rt') if f.endswith('.gz') else open(f)) for f in files]
    if not MS: raise SystemExit('no member.json under ' + mdir)
    C = [m for m in MS if m['member'].get('center')]; E = [m for m in MS if not m['member'].get('center')]
    if not E: E = MS
    C = C[0] if C else None
    os.makedirs(out, exist_ok=True)
    S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); props = S['props']
    ids = sorted(set().union(*[set(m['segments']['id']) for m in MS]))
    ix = {s: k for k, s in enumerate(ids)}; ns = len(ids); K = len(E)

    def mat(ms, key, fill=0.0):
        A = np.full((len(ms), ns), fill, float)
        for a, m in enumerate(ms):
            for s, v in zip(m['segments']['id'], m['segments'][key]): A[a, ix[s]] = fill if v is None else v
        return A
    D = mat(E, 'depth'); PD = mat(E, 'p_depth'); POT = mat(E, 'p_ot'); FB = mat(E, 'fb', 99.0); ARR = mat(E, 'arr', np.nan)
    close_d = D >= FAIL_M; close_o = close_d | (FB < 0.0)
    p_ens = close_d.mean(0); p_ens_ot = close_o.mean(0); p_mean = PD.mean(0); p_mean_ot = (1 - (1 - PD) * (1 - POT)).mean(0)
    if C:
        cD = mat([C], 'depth')[0]; cPD = mat([C], 'p_depth')[0]; cPOT = mat([C], 'p_ot')[0]; cFB = mat([C], 'fb', 99.0)[0]
        c_close = cD >= FAIL_M; c_close_o = c_close | (cFB < 0); c_pot = 1 - (1 - cPD) * (1 - cPOT)
    # class changes: center class (closes under the rule) vs ensemble majority (P_ens >= 0.5)
    chg = {}
    if C:
        for nm, cc, pe in (('depth', c_close, p_ens), ('overtop', c_close_o, p_ens_ot)):
            em = pe >= 0.5
            chg[nm] = dict(center_closed=int(cc.sum()), ens_majority_closed=int(em.sum()), closed_to_open=int((cc & ~em).sum()), open_to_closed=int((~cc & em).sum()),
                           uncertain_0_to_1=int(((pe > 0) & (pe < 1)).sum()), uncertain_25_75=int(((pe >= 0.25) & (pe <= 0.75)).sum()),
                           closed_in_any_member=int((pe > 0).sum()), closed_in_all_members=int((pe >= 1).sum()))
    # labels: y = 1 for segments strictly matched to a documented site (any type), 0 for segments not matched even loosely
    ref = C or E[0]; st = ref['matches'].get('strict', []); lo = ref['matches'].get('loose', [])
    pos = {s for _, _, sg in st for s in sg if s in ix}; loose_any = {s for _, _, sg in lo for s in sg if s in ix}
    keep = np.array([(s in pos) or (s not in loose_any) for s in ids]); y = np.array([s in pos for s in ids], float)
    lab = {}
    cands = dict(p_ens_depth=p_ens, p_ens_overtop=p_ens_ot, p_mean_depth=p_mean, p_mean_overtop=p_mean_ot)
    if C: cands.update(single_p_depth=cPD, single_p_overtop=c_pot, single_class_depth=c_close.astype(float), single_class_overtop=c_close_o.astype(float))
    if keep.any() and y.sum() > 0:
        lab['segments'] = {k: scores(v[keep], y[keep]) for k, v in cands.items()}
        # site level: each documented site gets the max P over its strict segments (outcome 1 for every site: these are positives only)
        lab['sites'] = {k: dict(mean_p=round(float(np.mean([max(v[ix[s]] for s in sg if s in ix) for _, _, sg in st if any(s in ix for s in sg)])), 3),
                                recall_p05=round(float(np.mean([max(v[ix[s]] for s in sg if s in ix) >= 0.5 for _, _, sg in st if any(s in ix for s in sg)])), 3),
                                brier_positives=round(float(np.mean([(1 - max(v[ix[s]] for s in sg if s in ix)) ** 2 for _, _, sg in st if any(s in ix for s in sg)])), 4))
                        for k, v in cands.items()}
        lab['site_table'] = [dict(id=i_, type=t_, n_segments=len(sg), p_ens_depth=round(float(max(p_ens[ix[s]] for s in sg if s in ix)), 3),
                                  p_ens_overtop=round(float(max(p_ens_ot[ix[s]] for s in sg if s in ix)), 3),
                                  single_p_depth=round(float(max(cPD[ix[s]] for s in sg if s in ix)), 3) if C else None,
                                  max_depth_range_m=[round(float(D[:, [ix[s] for s in sg if s in ix]].max(1).min()), 2), round(float(D[:, [ix[s] for s in sg if s in ix]].max(1).max()), 2)])
                             for i_, t_, sg in st if any(s in ix for s in sg)]
        lab['note'] = ('y = 1: segments with a road point within 30 m of a documented site (any type); y = 0: in-box segments not within the loose '
                       'match of any site (100-300 m / same-name) -- unreported is not proof of dry, so y = 0 is noisy and Brier is dominated by negatives')
    # gauges
    G = {}
    for m in E:
        for g in m['gauges']: G.setdefault(str(g['site']), []).append(g)
    gauges = []
    for s_, gs in G.items():
        g0 = gs[0]; row = dict(site=s_, name=g0.get('name'), members=len(gs))
        for key, okey in (('model_rise_m', 'obs_rise_m'), ('model_peak_q_m3s', 'obs_peak_q_m3s'), ('model_peak_h', 'obs_peak_h')):
            v = [g.get(key) for g in gs]; ob = g0.get(okey)
            if all(x is None for x in v): continue
            b = dict(p05=pct(v, 5), p50=pct(v, 50), p95=pct(v, 95), min=pct(v, 0), max=pct(v, 100), obs=ob)
            b['obs_inside_5_95'] = None if ob is None else bool(b['p05'] <= ob <= b['p95'])
            if C:
                cg = next((g for g in C['gauges'] if str(g['site']) == s_), {}); b['center'] = cg.get(key)
            row[key.replace('model_', '')] = b
        gauges.append(row)
    # outputs
    S_rows = []
    for s in ids:
        k = ix[s]
        S_rows.append(dict(segment=s, road=props['road'][s] or '', town=props['town'][s] or '', p_ens=round(float(p_ens[k]), 3), p_ens_overtop=round(float(p_ens_ot[k]), 3),
                           p_mean=round(float(p_mean[k]), 3), p_mean_overtop=round(float(p_mean_ot[k]), 3),
                           p_single=round(float(cPD[k]), 3) if C else None, depth_p05=round(float(np.percentile(D[:, k], 5)), 3),
                           depth_p50=round(float(np.percentile(D[:, k], 50)), 3), depth_p95=round(float(np.percentile(D[:, k], 95)), 3),
                           arrival_h_p50=None if np.isnan(ARR[:, k]).all() else round(float(np.nanmedian(ARR[:, k])), 1), label=int(y[k])))
    rows_geo = [r for r in S_rows if r['p_ens'] > 0 or r['p_ens_overtop'] > 0 or r['p_mean'] >= 0.05 or r['depth_p95'] >= 0.05 or r['label']]
    import prototype as PR
    PR.write_geojson(os.path.join(out, 'ens_segments.geojson'), S, rows_geo)
    params = [dict(name=nm, env=var, kind=kind, sigma=s, truncation_sd=TRUNC, sources=src) for nm, var, kind, s, src in PARAMS]
    R = dict(name=name or os.path.basename(out.rstrip('/')), members=len(E), center=C['member'] if C else None, seed=SEED, sampling='Latin hypercube, truncated normal z',
             parameters=params, member_design=[m['member'] for m in E], center_env=' '.join(f'{k}={v}' for k, v in (C['env'] or {}).items()) if C and isinstance(C.get('env'), dict) else (C or {}).get('env'),
             member_summary=[dict(name=m['member']['name'], mult=m['member'].get('mult'), rain_mean_mm=m.get('rain_total_mean_mm'), **(m.get('summary') or {})) for m in MS],
             segments_in_box=ns, closure_rules=dict(depth='peak depth >= 0.30 m (second-highest road point)', overtop='depth rule OR freeboard f < 0 (water beside the road above its lidar crest)'),
             expected_closures=dict(p_ens_depth=round(float(p_ens.sum()), 1), p_ens_overtop=round(float(p_ens_ot.sum()), 1), p_mean_depth=round(float(p_mean.sum()), 1),
                                    single_p_depth=round(float(cPD.sum()), 1) if C else None),
             class_changes=chg, labels=lab, gauges=gauges, made=time.strftime('%Y-%m-%d %H:%M'))
    json.dump(R, open(os.path.join(out, 'ensemble.json'), 'w'), indent=1)
    write_md(os.path.join(out, 'SUMMARY.md'), R)
    print(open(os.path.join(out, 'SUMMARY.md')).read())
    return R


def write_md(path, R):
    L = [f"# Ensemble {R['name']}: {R['members']} members + center", '',
         f"Latin hypercube (seed {R['seed']}), truncated at +-{TRUNC:g} sd, around the center env `{R['center_env']}`.", '',
         '| input | env | spread | sources |', '|---|---|---|---|']
    for p in R['parameters']:
        sp = f"sigma_ln {p['sigma']}" if p['kind'] == 'lognormal_mult' else f"sd {p['sigma']} (x center)"
        L.append(f"| {p['name']} | {p['env']} | {sp} | {p['sources']} |")
    L += ['', '## Members', '', '| member | rain | cn | n_chan | n_land | drain | rain mean mm | segments P>=0.5 |', '|---|---|---|---|---|---|---|---|']
    for m in R['member_summary']:
        mu = m.get('mult') or {}
        L.append(f"| {m['name']} | " + ' | '.join(str(mu.get(k, 1)) for k in ('rain', 'cn', 'n_chan', 'n_land', 'drain')) + f" | {m.get('rain_mean_mm')} | {m.get('segments_p_ge_50')} |")
    L += ['', '## Gauges: ensemble 5-95 % band vs observed', '', '| gauge | quantity | p05 | p50 | p95 | center | observed | inside |', '|---|---|---|---|---|---|---|---|']
    for g in R['gauges']:
        for q in ('rise_m', 'peak_q_m3s', 'peak_h'):
            b = g.get(q)
            if b: L.append(f"| {g['site']} {g.get('name') or ''} | {q} | {b['p05']} | {b['p50']} | {b['p95']} | {b.get('center')} | {b['obs']} | {b['obs_inside_5_95']} |")
    L += ['', '## Segments', '', f"In box: {R['segments_in_box']}. Expected closures: {R['expected_closures']}.", '']
    for k, c in R['class_changes'].items():
        L.append(f"- **{k} rule**: center closes {c['center_closed']}, ensemble majority {c['ens_majority_closed']}; closed->open {c['closed_to_open']}, "
                 f"open->closed {c['open_to_closed']}; closed in some but not all members {c['uncertain_0_to_1']} (P_ens 0.25-0.75: {c['uncertain_25_75']}); "
                 f"closed in every member {c['closed_in_all_members']}, in any {c['closed_in_any_member']}.")
    lab = R['labels']
    if lab.get('segments'):
        L += ['', '## Documented sites (Sept 2023 Leominster labels)', '', lab['note'], '', '| probability | Brier | climatology | BSS | site mean P | site recall P>=0.5 |', '|---|---|---|---|---|---|']
        for k, v in lab['segments'].items():
            s = lab['sites'][k]; L.append(f"| {k} | {v['brier']} | {v['brier_climatology']} | {v['bss']} | {s['mean_p']} | {s['recall_p05']} |")
        L += ['', 'Reliability (segments): bin: n, mean P, observed frequency', '']
        for k in ('p_ens_depth', 'single_p_depth', 'p_ens_overtop', 'single_p_overtop'):
            if k in lab['segments']: L.append(f"- {k}: " + '; '.join(f"{b['bin']}: {b['n']}, {b['mean_p']}, {b['obs_freq']}" for b in lab['segments'][k]['bins'] if b['n']))
    L += ['', 'Files: ensemble.json (everything above + site table), ens_segments.geojson (p_ens, p_ens_overtop, p_mean, p_single, depth 5/50/95 %).', '',
          'Caveats: one storm-wide rain multiplier per member (no spatial rain error); 12 members resolve P_ens in steps of 1/12 and the 5-95 % band '
          'is close to the member min-max; parameters sampled independently; model-structure error (DEM, channel burn, 2-D solver) is not sampled.']
    open(path, 'w').write('\n'.join(L) + '\n')


# ------------------------------------------------------------------------------------------------------------------------------ selftest
def selftest():
    import tempfile
    M = design(12, SEED, 'LF_LOSS=cn LF_CN_AMC=II LF_CN_SCALE=1.0 LF_INFIL_MMH=2 LF_QOUT=1')
    assert len(M) == 13 and M[0]['center'] and M[0]['env'].startswith('LF_LOSS=cn')
    for j, (nm, var, kind, s, _) in enumerate(PARAMS):      # LHS: one sample per stratum in every dimension
        from scipy.stats import norm
        lo, hi = norm.cdf(-TRUNC), norm.cdf(TRUNC); u = (norm.cdf([m['z'][nm] for m in M[1:]]) - lo) / (hi - lo)
        assert sorted((u * 12).astype(int).tolist()) == list(range(12)), nm
    e = parse_env(M[1]['env']); assert abs(float(e['LF_N_CHAN']) / 0.035 - M[1]['mult']['n_chan']) < 1e-3; assert abs(float(e['LF_INFIL_MMH']) / 2 - M[1]['mult']['drain']) < 1e-3
    print('ok   design: 12 LHS members + center, one sample per stratum per input, center env kept')
    d = tempfile.mkdtemp(); S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); n = S['n']
    rng = np.random.default_rng(0); segs = list(range(0, 400)); base = rng.gamma(0.6, 0.25, len(segs))
    for k, m in enumerate(M):
        f = 1.0 if m['center'] else m['mult']['rain']
        dep = (base * f).round(3); pd_ = 0.5 * (1 + np.vectorize(math.erf)((dep - 0.3) / 0.1 / math.sqrt(2)))
        fb = [None if i % 3 else round(0.2 - dep[i], 2) for i in range(len(segs))]
        gauges = [dict(site='01094500', name='N NASHUA', model_rise_m=2.5 * f, obs_rise_m=2.92, model_peak_q_m3s=140 * f, obs_peak_q_m3s=157.4, model_peak_h=8.5 + k * 0.1, obs_peak_h=12.5,
                       model_peak_utc='2023-09-12T00:30Z', obs_peak_utc='2023-09-12T04:30Z')]
        mj = dict(member=m, env=m['env'], rain_total_mean_mm=200 * f, summary=dict(segments_p_ge_50=int((pd_ >= .5).sum())),
                  segments=dict(id=segs, depth=dep.tolist(), p_depth=pd_.round(3).tolist(), p_ot=[0.0] * len(segs), fb=fb, arr=[None] * len(segs), h30=[0] * len(segs)),
                  matches=dict(strict=[('L1', 'flooded', [3, 4]), ('L2', 'closed', [10])], loose=[('L1', 'flooded', [3, 4, 5]), ('L2', 'closed', [10, 11])]), gauges=gauges)
        os.makedirs(os.path.join(d, m['name'])); json.dump(mj, open(os.path.join(d, m['name'], 'member.json'), 'w'))
    R = aggregate(d, os.path.join(d, 'out'), 'selftest')
    assert R['members'] == 12 and R['gauges'][0]['rise_m']['obs_inside_5_95'] in (True, False)
    assert 0 <= R['labels']['segments']['p_ens_depth']['brier'] <= 1 and 'single_p_depth' in R['labels']['segments']
    g = json.load(open(os.path.join(d, 'out', 'ens_segments.geojson'))); assert g['features'] and 'p_ens' in g['features'][0]['properties']
    pe = np.array([f_['properties']['p_ens'] for f_ in g['features']]); assert (np.abs(pe * 12 - np.round(pe * 12)) < 0.02).all()
    print('ok   aggregate: P_ens in steps of 1/12, gauge bands, Brier + reliability, geojson')
    print('SELFTEST PASSED')


if __name__ == '__main__':
    if '--selftest' in sys.argv: selftest(); sys.exit()
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sub = ap.add_subparsers(dest='cmd', required=True)
    a1 = sub.add_parser('design'); a1.add_argument('--n', type=int, default=12); a1.add_argument('--seed', type=int, default=SEED)
    a1.add_argument('--center-env', default=''); a1.add_argument('--out'); a1.add_argument('--only', help='comma-separated member names to keep (tests)')
    a2 = sub.add_parser('member'); a2.add_argument('--run-dir', required=True); a2.add_argument('--out', required=True); a2.add_argument('--member-json', default='{}')
    a2.add_argument('--labels')
    a3 = sub.add_parser('aggregate'); a3.add_argument('--members', required=True); a3.add_argument('--out', required=True); a3.add_argument('--name')
    a = ap.parse_args()
    if a.cmd == 'design':
        M = design(a.n, a.seed, a.center_env)
        if a.only: keep = set(a.only.split(',')); M = [m for m in M if m['name'] in keep]
        s = json.dumps([dict(name=m['name'], env=m['env'], center=m['center'], mult=m['mult']) for m in M], separators=(',', ':'))
        if a.out: open(a.out, 'w').write(s)
        print(s)
    elif a.cmd == 'member': member(a.run_dir, a.out, json.loads(a.member_json), a.labels)
    else: aggregate(a.members, a.out, a.name)
