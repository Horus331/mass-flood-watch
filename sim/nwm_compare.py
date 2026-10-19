"""How good is the NOAA National Water Model (NWM) as our hydrology input?  NWM hourly streamflow vs observed USGS discharge.

    python sim/nwm_compare.py              -> out/nwm_compare.json + out/nwm_compare.md (uploaded to HF validation/nwm/ if HF_TOKEN)
    python sim/nwm_compare.py --selftest   -> offline check of the metric / matching code on synthetic data (no network)
    python sim/nwm_compare.py --storms jul2023 --products analysis_assim   (optional subsets)

Steps
  1. Observed hourly flow (cfs, hourly max, UTC hour strings) per storm from HF data/gauges_v2/gauges_<storm>.json.
  2. Gauge -> NWM reach: USGS NLDI linked-data (nwissite/USGS-<site>) gives the NHDPlus v2 COMID, which is the NWM CONUS
     channel feature_id.  The mapping is cached in the output JSON.
  3. NWM operational hourly analysis, CONUS channel_rt, tm00 (valid at HH:00 UTC), from the public Google Cloud bucket
     (Azure mirror as fallback).  Two products:
        analysis_assim        - nudged toward USGS gauges (data assimilation).  At an assimilated gauge this is close to
                                the observation by construction, so it is NOT an independent test of the model.
        analysis_assim_no_da  - same forcing, no streamflow nudging.  This is the fair "how good is the model" test and
                                the right proxy for ungauged reaches / forecasts.
     Each file (~10-15 MB) is read in memory, only the gauge reaches are kept, the bytes are dropped.
  4. Metrics per gauge x storm x product: observed and NWM peak (m3/s), peak ratio, peak timing error (h, NWM - obs),
     NSE and KGE over the storm window (hourly, paired hours only), plus a per-storm summary.
Note: observed values are hourly maxima of 15-min data; NWM values are instantaneous at the top of the hour.  This biases
the peak ratio slightly low (a few %), which is small next to the differences we are looking for.
"""
import os, sys, json, time, argparse, datetime as dt
from concurrent.futures import ThreadPoolExecutor
import numpy as np

HF_REPO = 'mohabeldokla/mass-flood-watch-tiles'
OBS_URL = f'https://huggingface.co/datasets/{HF_REPO}/resolve/main/data/gauges_v2/gauges_{{storm}}.json'
NLDI = ['https://api.water.usgs.gov/nldi/linked-data/nwissite/USGS-{site}',
        'https://labs.waterdata.usgs.gov/api/nldi/linked-data/nwissite/USGS-{site}']
NWM = ['https://storage.googleapis.com/national-water-model/nwm.{ymd}/{prod}/nwm.t{hh}z.{prod}.channel_rt.tm00.conus.nc',
       'https://noaanwm.blob.core.windows.net/nwm/nwm.{ymd}/{prod}/nwm.t{hh}z.{prod}.channel_rt.tm00.conus.nc']
STORMS = {'jul2023': ('2023-07-09T12', '2023-07-12T00'), 'sep2023': ('2023-09-11T12', '2023-09-13T12'),
          'dec2023': ('2023-12-17T18', '2023-12-20T00'), 'jan2024': ('2024-01-09T06', '2024-01-11T12')}
PRODUCTS = ['analysis_assim', 'analysis_assim_no_da']
HIGHLIGHT = {'01169900': 'South River near Conway', '01170000': 'Deerfield River near West Deerfield', '01171000': 'Mill River'}
CFS = 0.0283168466
H = {'User-Agent': 'mass-flood-watch research (NWM vs USGS comparison)'}
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)


# ----------------------------------------------------------------------------------------------- metrics (pure numpy)
def hours(t0, t1):
    a, b = dt.datetime.strptime(t0, '%Y-%m-%dT%H'), dt.datetime.strptime(t1, '%Y-%m-%dT%H')
    return [(a + dt.timedelta(hours=i)).strftime('%Y-%m-%dT%H') for i in range(int((b - a).total_seconds() // 3600) + 1)]

def nse(o, s):
    d = np.sum((o - o.mean()) ** 2)
    return None if d <= 0 else float(1 - np.sum((s - o) ** 2) / d)

def kge(o, s):
    if o.std() < 1e-9 or s.std() < 1e-9 or o.mean() <= 0: return None
    r = np.corrcoef(o, s)[0, 1]
    return float(1 - np.sqrt((r - 1) ** 2 + (s.std() / o.std() - 1) ** 2 + (s.mean() / o.mean() - 1) ** 2))

def compare(win, obs, sim, min_cover=0.5):
    """obs/sim: {hour: m3/s}.  Metrics over the window hours where both exist; None if too little overlap."""
    hs = [h for h in win if obs.get(h) is not None and sim.get(h) is not None and np.isfinite(obs[h]) and np.isfinite(sim[h])]
    if len(hs) < max(6, min_cover * len(win)): return dict(n_hours=len(hs), ok=False)
    o, s = np.array([obs[h] for h in hs], float), np.array([sim[h] for h in hs], float)
    io, is_ = int(np.argmax(o)), int(np.argmax(s))
    t = lambda h: dt.datetime.strptime(h, '%Y-%m-%dT%H')
    r = lambda x, n=3: None if x is None else round(x, n)
    return dict(ok=True, n_hours=len(hs), obs_peak=r(float(o[io])), nwm_peak=r(float(s[is_])), obs_peak_time=hs[io], nwm_peak_time=hs[is_],
                peak_ratio=r(float(s[is_] / o[io])) if o[io] > 0 else None, timing_err_h=(t(hs[is_]) - t(hs[io])).total_seconds() / 3600,
                nse=r(nse(o, s)), kge=r(kge(o, s)))

def summarize(rows):
    rows = [m for m in rows if m.get('ok')]
    pr = np.array([m['peak_ratio'] for m in rows if m['peak_ratio'] is not None], float)
    te = np.array([abs(m['timing_err_h']) for m in rows], float)
    md = lambda a: None if len(a) == 0 else round(float(np.median(a)), 3)
    return dict(n_gauges=len(rows), median_peak_ratio=md(pr), share_peak_within_25pct=None if len(pr) == 0 else round(float(np.mean(np.abs(pr - 1) <= 0.25)), 3),
                median_abs_timing_h=md(te), median_nse=md(np.array([m['nse'] for m in rows if m['nse'] is not None])),
                median_kge=md(np.array([m['kge'] for m in rows if m['kge'] is not None])))


# ----------------------------------------------------------------------------------------------- network pieces
def get(url, tries=4, timeout=120, ok404=False):
    import requests
    for k in range(tries):
        try:
            r = requests.get(url, headers=H, timeout=timeout)
            if r.status_code == 404 and ok404: return None
            if r.status_code in (429, 500, 502, 503, 504): raise RuntimeError(f'HTTP {r.status_code}')
            r.raise_for_status(); return r
        except Exception as e:
            if k == tries - 1: log('  give up', url[-90:], repr(e)[:120]); return None
            time.sleep(5 * (k + 1))

def comid_for(site):
    for u in NLDI:
        r = get(u.format(site=site), tries=3, timeout=60, ok404=True)
        if r is None: continue
        try:
            f = r.json()['features'][0]['properties']; c = f.get('comid')
            if c not in (None, ''): return int(c), u.split('/linked-data')[0]
        except Exception as e: log('  NLDI parse', site, repr(e)[:80])
    return None, None

import threading
_NC_LOCK = threading.Lock()      # HDF5/netCDF4 is not thread-safe: downloads run in threads, parsing one at a time (a parallel parse segfaulted on the runner)

def read_channel(blob, ids):
    """NWM channel_rt netCDF bytes -> {feature_id: streamflow m3/s} for the wanted ids."""
    import netCDF4
    with _NC_LOCK, netCDF4.Dataset('mem.nc', memory=blob) as ds:
        fid = ds.variables['feature_id'][:].astype(np.int64)
        q = np.ma.filled(ds.variables['streamflow'][:].astype(float), np.nan).ravel()   # auto scale_factor / missing
    pos = {int(f): i for i, f in enumerate(fid)}
    return {c: (float(q[pos[c]]) if c in pos and np.isfinite(q[pos[c]]) and q[pos[c]] >= 0 else None) for c in ids}

def fetch_hour(prod, hour, ids):
    ymd, hh = hour[:10].replace('-', ''), hour[11:13]
    for u in NWM:
        r = get(u.format(ymd=ymd, hh=hh, prod=prod), tries=3, timeout=180, ok404=True)
        if r is None: continue
        try: vals = read_channel(r.content, ids); del r; return hour, vals, u.split('/nwm.')[0]
        except Exception as e: log('  read fail', prod, hour, repr(e)[:100])
    return hour, None, None


# ----------------------------------------------------------------------------------------------- report
def fmt(x, p='{:.2f}'):
    return '-' if x is None else p.format(x)

def write_md(res, path):
    L = ['# NWM vs USGS observed discharge, Massachusetts storms', '',
         f"Generated {res['generated']}. NWM operational hourly analysis (CONUS channel_rt, tm00) vs USGS hourly-max discharge. "
         'Peak ratio = NWM peak / observed peak; timing error = NWM peak hour - observed peak hour (h, + = NWM late).', '',
         '**Which product is fair?** `analysis_assim` is nudged toward USGS gauge observations, so at assimilated gauges it '
         'matches the observation partly by construction - it overstates skill and is only a check that the data plumbing '
         'works. `analysis_assim_no_da` uses the same forcing without streamflow nudging; it is the fair test of what NWM '
         'gives at reaches with no gauge (most of our network) and the closer analogue of a forecast.', '']
    for prod in res['products']:
        L += [f'## Summary - {prod}', '', '| storm | gauges | median peak ratio | share peak within ±25% | median abs timing (h) | median NSE | median KGE |', '|---|---|---|---|---|---|---|']
        for st, s in res['summary'].get(prod, {}).items():
            L.append(f"| {st} | {s['n_gauges']} | {fmt(s['median_peak_ratio'])} | {fmt(s['share_peak_within_25pct'], '{:.0%}')} | {fmt(s['median_abs_timing_h'], '{:.0f}')} | {fmt(s['median_nse'])} | {fmt(s['median_kge'])} |")
        L.append('')
    L += ['## Highlighted gauges', '', '| gauge | storm | product | obs peak (m3/s) | NWM peak | ratio | timing (h) | NSE | KGE |', '|---|---|---|---|---|---|---|---|---|']
    for site, nm in HIGHLIGHT.items():
        for st in res['storms']:
            for prod in res['products']:
                m = res['metrics'].get(prod, {}).get(st, {}).get(site)
                if not m: L.append(f'| {site} {nm} | {st} | {prod} | no data | | | | | |'); continue
                if not m.get('ok'): L.append(f"| {site} {nm} | {st} | {prod} | too few hours ({m.get('n_hours')}) | | | | | |"); continue
                L.append(f"| {site} {nm} | {st} | {prod} | {fmt(m['obs_peak'], '{:.1f}')} | {fmt(m['nwm_peak'], '{:.1f}')} | {fmt(m['peak_ratio'])} | {m['timing_err_h']:+.0f} | {fmt(m['nse'])} | {fmt(m['kge'])} |")
    for prod in res['products']:
        L += ['', f'## All gauges - {prod}', '', '| storm | gauge | name | COMID | obs peak | NWM peak | ratio | timing (h) | NSE | KGE |', '|---|---|---|---|---|---|---|---|---|---|']
        for st in res['storms']:
            for site, m in sorted(res['metrics'].get(prod, {}).get(st, {}).items()):
                if not m.get('ok'): continue
                L.append(f"| {st} | {site} | {res['sites'].get(site, {}).get('name', '')} | {res['comids'].get(site, {}).get('comid')} | {fmt(m['obs_peak'], '{:.1f}')} | {fmt(m['nwm_peak'], '{:.1f}')} | {fmt(m['peak_ratio'])} | {m['timing_err_h']:+.0f} | {fmt(m['nse'])} | {fmt(m['kge'])} |")
    if res.get('notes'): L += ['', '## Notes', ''] + ['- ' + n for n in res['notes']]
    open(path, 'w').write('\n'.join(L) + '\n')


# ----------------------------------------------------------------------------------------------- main
def run(storms, products, workers):
    os.makedirs('out', exist_ok=True)
    res = dict(generated=dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), storms={s: STORMS[s] for s in storms}, products=products,
               sources=dict(observed=OBS_URL, nldi=NLDI, nwm=NWM), sites={}, comids={}, metrics={}, summary={}, coverage={}, notes=[])
    obs = {}
    for st in storms:
        r = get(OBS_URL.format(storm=st)); j = r.json() if r else {}
        obs[st] = {s: {h: v * CFS for h, v in d.get('values', []) if v is not None} for s, d in j.get('flow', {}).items()}
        for s, d in j.get('flow', {}).items():
            info = j.get('sites', {}).get(s, {})
            res['sites'].setdefault(s, dict(name=info.get('name') or d.get('name'), lat=d.get('lat'), lon=d.get('lon'), drain_mi2=info.get('drain_mi2')))
        log(st, len(obs[st]), 'flow gauges')
    sites = sorted(res['sites'])
    with ThreadPoolExecutor(8) as ex:
        for s, (c, src) in zip(sites, ex.map(comid_for, sites)): res['comids'][s] = dict(comid=c, source=src)
    ids = sorted({v['comid'] for v in res['comids'].values() if v['comid']})
    log(len(ids), 'of', len(sites), 'gauges linked to an NWM reach')
    for s in HIGHLIGHT: log('  highlight', s, res['comids'].get(s))
    for prod in products:
        for st in storms:
            win = hours(*STORMS[st]); sim_by_comid = {c: {} for c in ids}; missing = []; srcs = set()
            with ThreadPoolExecutor(workers) as ex:
                for hour, vals, src in ex.map(lambda h: fetch_hour(prod, h, ids), win):
                    if vals is None: missing.append(hour); continue
                    srcs.add(src)
                    for c, v in vals.items(): sim_by_comid[c][hour] = v
            res['coverage'].setdefault(prod, {})[st] = dict(hours=len(win), missing=missing, source=sorted(srcs))
            log(prod, st, f'{len(win) - len(missing)}/{len(win)} hourly files', sorted(srcs))
            if len(missing) == len(win): res['notes'].append(f'{prod} {st}: no files found - product not available for these dates'); continue
            ms = {}
            for s in sites:
                c = res['comids'][s]['comid']
                if not c or s not in obs[st]: continue
                ms[s] = compare(win, obs[st][s], sim_by_comid.get(c, {}))
            res['metrics'].setdefault(prod, {})[st] = ms
            res['summary'].setdefault(prod, {})[st] = summarize(ms.values())
            log('  summary', res['summary'][prod][st])
    unl = [s for s, v in res['comids'].items() if not v['comid']]
    if unl: res['notes'].append(f'{len(unl)} gauges had no NLDI COMID and were skipped: ' + ', '.join(unl))
    res['notes'].append('NWM v2.1 was operational until 2023-09-19 and v3.0 after; feature_id = NHDPlus v2 COMID in both. jul2023/sep2023 are v2.1, dec2023/jan2024 v3.0.')
    res['notes'].append('Observed = hourly max of 15-min USGS data; NWM = instantaneous at HH:00 UTC (tm00). Small low bias in NWM peak ratio expected from this alone.')
    json.dump(res, open('out/nwm_compare.json', 'w'), indent=1)
    write_md(res, 'out/nwm_compare.md'); log('wrote out/nwm_compare.json, out/nwm_compare.md')
    if os.environ.get('HF_TOKEN'):
        from huggingface_hub import HfApi
        api = HfApi(token=os.environ['HF_TOKEN'])
        for f in ('nwm_compare.json', 'nwm_compare.md'):
            api.upload_file(path_or_fileobj=f'out/{f}', path_in_repo=f'validation/nwm/{f}', repo_id=HF_REPO, repo_type='dataset')
        log('uploaded to HF validation/nwm/')


def selftest():
    ok = True
    def check(name, cond):
        nonlocal ok; ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name)
    win = hours('2023-07-09T12', '2023-07-12T00'); check('window length 61 h', len(win) == 61)
    t = np.arange(len(win)); o = 5 + 100 * np.exp(-((t - 30) / 6.0) ** 2)
    obs = dict(zip(win, o))
    m = compare(win, obs, dict(zip(win, o))); check('perfect: NSE=1 KGE=1 ratio=1 timing=0', m['nse'] == 1 and m['kge'] == 1 and m['peak_ratio'] == 1 and m['timing_err_h'] == 0)
    s = 5 + 80 * np.exp(-((t - 34) / 6.0) ** 2); m = compare(win, obs, dict(zip(win, s)))
    check(f"shifted+low: ratio={m['peak_ratio']} timing={m['timing_err_h']:+.0f} NSE={m['nse']} KGE={m['kge']}", abs(m['peak_ratio'] - 85 / 105) < 1e-3 and m['timing_err_h'] == 4 and m['nse'] < 1 and m['kge'] < 1)
    m = compare(win, obs, dict(zip(win, np.full(len(win), o.mean())))); check(f"mean-only sim: NSE={m['nse']} (~0)", abs(m['nse']) < 1e-9 and m['kge'] is None)
    m = compare(win, obs, {h: v for h, v in zip(win[:20], o[:20])}); check('too little overlap -> ok=False', m['ok'] is False)
    gap = dict(zip(win, s)); gap.pop(win[10]); gap[win[11]] = float('nan'); m = compare(win, obs, gap); check('gaps/NaN skipped', m['ok'] and m['n_hours'] == 59)
    rows = [dict(ok=True, peak_ratio=r, timing_err_h=e, nse=0.5, kge=0.4) for r, e in [(1.0, 0), (0.8, -2), (1.3, 3), (0.5, 6)]] + [dict(ok=False)]
    S = summarize(rows); check(f'summary {S}', S['n_gauges'] == 4 and S['median_peak_ratio'] == 0.9 and S['share_peak_within_25pct'] == 0.5 and S['median_abs_timing_h'] == 2.5)
    try:
        import netCDF4
        p = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'nwm_selftest.nc')
        with netCDF4.Dataset(p, 'w') as ds:      # mimic NWM layout: int streamflow with scale_factor and _FillValue
            ds.createDimension('feature_id', 4); f = ds.createVariable('feature_id', 'i4', ('feature_id',)); f[:] = [101, 6076229, 303, 404]
            q = ds.createVariable('streamflow', 'i4', ('feature_id',), fill_value=-999900); q.scale_factor = 0.01; q.add_offset = 0.0
            q[:] = np.ma.masked_array([1.23, 45.67, 0, 0], mask=[False, False, True, False])
        v = read_channel(open(p, 'rb').read(), [6076229, 101, 303, 999]); os.remove(p)
        check(f'netCDF read {v}', abs(v[6076229] - 45.67) < 1e-6 and abs(v[101] - 1.23) < 1e-6 and v[303] is None and v[999] is None)
    except ImportError: print('SKIP netCDF read (netCDF4 not installed)')
    res = dict(generated='selftest', storms={'jul2023': STORMS['jul2023']}, products=['analysis_assim_no_da'], sites={'01170000': {'name': 'test'}},
               comids={'01170000': {'comid': 6076229}}, metrics={'analysis_assim_no_da': {'jul2023': {'01170000': compare(win, obs, dict(zip(win, s)))}}},
               summary={'analysis_assim_no_da': {'jul2023': summarize([compare(win, obs, dict(zip(win, s)))])}}, notes=['synthetic'])
    p = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'nwm_selftest.md'); write_md(res, p); md = open(p).read(); os.remove(p)
    check('markdown report renders', '| 01170000 Deerfield River near West Deerfield | jul2023 | analysis_assim_no_da | 105.0 | 85.0 | 0.81 | +4 |' in md)
    print('SELFTEST', 'OK' if ok else 'FAILED'); return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--storms', default=','.join(STORMS)); ap.add_argument('--products', default=','.join(PRODUCTS))
    ap.add_argument('--workers', type=int, default=8)
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    run(a.storms.split(','), a.products.split(','), a.workers)
