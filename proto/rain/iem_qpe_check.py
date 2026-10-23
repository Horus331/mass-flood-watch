"""Check the w9 IEM MRMS fallback (sim/colab/w9_lisflood.py mrms_sources / mrms_fetch_raw / mrms_sample) against ASOS gauges.

    python proto/rain/iem_qpe_check.py --storm jul2019 --stations ORH,FIT,BED,OWD,PVD,BDL --out docs/proto/rain/iem_check/jul2019.json

For every hour of the storm window (catalogue t0, hours) the hourly QPE is fetched exactly as w9 fetches it (same source order, same
grid sampling) and read at each ASOS station; the IEM ASOS routine METAR one-hour precipitation (p01i, the hour ending HH:54) is paired
with the MRMS hour ending at the next HH:00. Also lists the IEM GaugeCorr_QPE_01H folder of t0's day (file names, count) and, with
--consistency <UTC hour after Oct 2020>, checks that IEM MultiSensor Pass2 equals AWS Pass2 at the stations (same product, two mirrors).
Needs the network (GitHub Actions: .github/workflows/iem_qpe_check.yml).
"""
import argparse, csv, io, json, os, re, sys, tempfile

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))
import w9_lisflood as W9  # noqa: E402


def asos(stations, a, b):
    u = ('https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?' + '&'.join(f'station={s}' for s in stations) +
         f'&data=p01i&year1={a.year}&month1={a.month}&day1={a.day}&hour1={a.hour}&year2={b.year}&month2={b.month}&day2={b.day}&hour2={b.hour}'
         '&tz=Etc/UTC&format=onlycomma&latlon=yes&missing=M&trace=0.0001&report_type=3')
    r = requests.get(u, timeout=120); r.raise_for_status()
    return list(csv.DictReader(io.StringIO(r.text)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--storm', required=True); ap.add_argument('--stations', default='ORH,FIT,BED,OWD,PVD,BDL')
    ap.add_argument('--consistency', default=''); ap.add_argument('--out', required=True); a = ap.parse_args()
    S = W9.storm_cfg(a.storm); t0 = pd.Timestamp(S['t0']); hours = [t0 + pd.Timedelta(hours=h + 1) for h in range(S['hours'])]
    st = [s.strip() for s in a.stations.split(',') if s.strip()]
    out = dict(storm=a.storm, t0=S['t0'], hours=S['hours'], method=__doc__.split('\n')[0])
    # 1. the IEM folder of t0's day
    lst = {}
    for p in ('GaugeCorr_QPE_01H', 'MultiSensor_QPE_01H_Pass2'):
        u = f'https://mtarchive.geol.iastate.edu/{t0:%Y/%m/%d}/mrms/ncep/{p}/'
        try: names = sorted(set(re.findall(r'href="([^"]+\.grib2\.gz)"', requests.get(u, timeout=60).text)))
        except Exception as e: names = [f'error {e!r}'[:120]]
        lst[p] = dict(url=u, n=len(names), first=names[:4], last=names[-2:])
    out['iem_listing'] = lst
    # 2. ASOS hourly
    R = asos(st, t0 - pd.Timedelta(hours=1), hours[-1] + pd.Timedelta(hours=1))
    loc, obs = {}, {}
    for r in R:
        s = r['station']; loc[s] = (float(r['lat']), float(r['lon']))
        if r['p01i'] in ('M', ''): continue
        tv = pd.Timestamp(r['valid'] + 'Z')
        if tv.minute < 45: continue                       # routine METARs only (HH:51-HH:56); specials carry partial-hour totals
        end = (tv + pd.Timedelta(hours=1)).floor('h')     # METAR at 13:54 -> MRMS hour ending 14:00
        obs.setdefault(s, {})[end] = float(r['p01i']) * 25.4
    # 3. MRMS as w9 reads it
    gp = os.path.join(tempfile.mkdtemp(), 'q.grib2'); per = {s: [] for s in loc}; prods = {}
    for ts in hours:
        try: raw, lab, url = W9.mrms_fetch_raw(ts, W9.mrms_http_fetch)
        except RuntimeError as e: prods[f'{ts:%Y-%m-%dT%H:%MZ}'] = 'missing'; continue
        prods[f'{ts:%Y-%m-%dT%H:%MZ}'] = lab
        for s, (la, lo) in loc.items():
            v = float(W9.mrms_sample(raw, np.array([la]), np.array([lo]), gp)[0, 0])
            per[s].append(dict(hour_end=f'{ts:%Y-%m-%dT%H:%MZ}', mrms_mm=round(v, 2), asos_mm=None if ts not in obs.get(s, {}) else round(obs[s][ts], 2)))
    out['products'] = prods
    summ = {}
    for s, rows in per.items():
        pr = [(r['mrms_mm'], r['asos_mm']) for r in rows if r['asos_mm'] is not None]
        if not pr: summ[s] = dict(lat=loc[s][0], lon=loc[s][1], n_pairs=0); continue
        m_, g_ = np.array(pr).T; k = int(np.argmax(g_))
        summ[s] = dict(lat=loc[s][0], lon=loc[s][1], n_pairs=len(pr), asos_total_mm=round(float(g_.sum()), 1), mrms_total_mm=round(float(m_.sum()), 1),
                       ratio_total=round(float(m_.sum() / g_.sum()), 2) if g_.sum() > 0 else None,
                       corr_hourly=round(float(np.corrcoef(m_, g_)[0, 1]), 2) if g_.std() > 0 and m_.std() > 0 else None,
                       asos_peak_hour=dict(hour_end=[r['hour_end'] for r in rows if r['asos_mm'] is not None][k], asos_mm=round(float(g_[k]), 1), mrms_mm=round(float(m_[k]), 1)),
                       mrms_peak_hour_mm=round(float(m_.max()), 1))
    out['stations'] = summ; out['hourly'] = per
    # 4. AWS vs IEM Pass2 (same product, two mirrors)
    if a.consistency:
        ts = pd.Timestamp(a.consistency); res = {}
        for lab, url in W9.mrms_sources(ts)[:2]:
            raw = W9.mrms_http_fetch(url)
            res[lab] = None if raw is None else {s: round(float(W9.mrms_sample(raw, np.array([la]), np.array([lo]), gp)[0, 0]), 3) for s, (la, lo) in loc.items()}
        out['aws_vs_iem_pass2'] = dict(hour_end=f'{ts:%Y-%m-%dT%H:%MZ}', **res)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True); json.dump(out, open(a.out, 'w'), indent=1)
    print(json.dumps(dict(listing=lst, products=sorted(set(prods.values())), stations=summ, aws_vs_iem=out.get('aws_vs_iem_pass2')), indent=1))


if __name__ == '__main__':
    main()
