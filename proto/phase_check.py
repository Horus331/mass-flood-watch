"""C1 (LF_PHASE) on the held-out storms: does any hour of a storm have 2 m air below 2 C anywhere in its box? (docs/proto/prospective/PREREG_PHASE_LIVE.md)

    python proto/phase_check.py --out docs/proto/prospective/phase_check.json

Per storm (score_v2 held-out 23 + sep2023 + aug2021; catalogue t0, hours, bbox): HRRR analysis (f00) TMP 2 m for every hour of the window,
minimum over the box.  A storm whose box never drops below 2 C is unchanged by LF_PHASE by construction (liquid fraction 1 everywhere).
"""
import argparse, datetime as dt, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); a = ap.parse_args()
    import pandas as pd, score_v2 as SV, lf_phase as LP
    from concurrent.futures import ThreadPoolExecutor
    cat = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']}
    storms = [s for s in list(SV.HELDOUT + SV.NEW16) + ['sep2023', 'aug2021'] if s in cat and s not in SV.LOCKED]
    out = {}; ERR = []
    for s in storms:
        e = cat[s]; t0 = pd.Timestamp(e['t0'].replace('Z', '')); lo0, la0, lo1, la1 = e['bbox_lonlat']; G = {}
        def one(h):
            ts = t0 + pd.Timedelta(hours=h)
            try:
                m = LP.tmp2m(ts, 0)
                if m is None: return h, None
                if 'LL' not in G:
                    la, lo = m.latlons(); lo = np.where(lo > 180, lo - 360, lo)
                    G['LL'] = (la >= la0 - 0.05) & (la <= la1 + 0.05) & (lo >= lo0 - 0.05) & (lo <= lo1 + 0.05)
                return h, float(np.min(m.values[G['LL']])) - 273.15
            except Exception as ex:
                if not ERR: ERR.append(repr(ex)[:300]); print('first error', s, h, ERR[0], flush=True)
                return h, None
        one(0)
        with ThreadPoolExecutor(8) as ex: T = dict(ex.map(one, range(e['hours'] + 1)))
        got = [v for v in T.values() if v is not None]
        out[s] = dict(month=e['t0'][:7], hours=e['hours'] + 1, hours_with_t=len(got), tmin_c=round(min(got), 1) if got else None,
                      hours_below_2c=sum(v < 2 for v in got), affected=bool(got and min(got) < 2.0))
        print(s, out[s], flush=True)
    json.dump(dict(made_by='proto/phase_check.py', storms=out, affected=[s for s, v in out.items() if v['affected']],
                   missing=[s for s, v in out.items() if not v['hours_with_t']]), open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
