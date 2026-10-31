"""Ground state before the next storm, District 3 (docs/site/data/ground.json), refreshed with every forecast cycle.

Two standard, data-driven indices; nothing fitted to our storms:

1. Antecedent wetness: 5-day rain P5 (mm), MRMS MultiSensor QPE 24H Pass2 summed over the 120 h before now, District 3 box mean
   (sim/colab/lf_antecedent.py). Class by NRCS NEH-4 table 4.2 (Chow, Maidment & Mays 1988):
       growing season (May-Oct): P5 < 35 mm dry (AMC I), 35-53 mm normal (II), > 53 mm wet (III)
       dormant season (Nov-Apr):  P5 < 13 mm dry,         13-28 mm normal,      > 28 mm wet
2. Frozen ground: Continuous Frozen Ground Index (CFGI, Molnau & Bissell 1983; NWS; used operationally in LISFLOOD and GSSHA):
       CFGI_d = max(0, A * CFGI_(d-1) - T_d * exp(-0.4 * K * D_d)),  A = 0.97 /day, K = 0.5 /cm,
       T_d daily mean air temperature (deg C), D_d snow depth (cm). Frozen (impermeable) once CFGI >= 83 deg C-days, thawed again below 56.
   Temperature and snow depth: NWS daily climate report for Worcester (KORH, 300 m, the District 3 first-order station), via the Iowa
   Environmental Mesonet JSON service, the last 120 days.

How the model uses it: it does NOT change the live forecast. The 5-day wetness rule was backtested on the held-out storms on 23 Oct 2026
and lowered skill (docs/proto/runoff/AMC.md), so runs stay at the calibrated 'normal' setting. Frozen ground has no backtest yet (the
catalogue is June-September). The state is published so a reader knows when the forecast is likely too low (wet or frozen ground), and the
Scenarios tab shows the same storm with that ground.

    python proto/ground_state.py run  --out docs/site/data/ground.json
    python proto/ground_state.py selftest
"""
import argparse, datetime as dt, json, math, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
D3_LAT, D3_LON = (41.98, 42.75), (-72.25, -71.25)
CFGI_A, CFGI_K, FROZEN, THAWED = 0.97, 0.5, 83.0, 56.0
CLI = 'https://mesonet.agron.iastate.edu/json/cli.py?station={st}&year={y}'


def amc_class(p5, month):
    lo, hi = (35.0, 53.0) if 5 <= month <= 10 else (13.0, 28.0)
    return ('dry', 'I') if p5 < lo else (('wet', 'III') if p5 > hi else ('normal', 'II'))


def num(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    s = str(v).strip()
    if s in ('T', 'Trace'): return 0.0
    try: return float(s)
    except ValueError: return None


def cli_days(station='KORH', now=None, days=120):
    """[(date, mean T degC, snow depth cm)] from the NWS daily climate reports (IEM JSON), oldest first."""
    now = now or dt.datetime.now(dt.timezone.utc)
    rows = {}
    for y in sorted({now.year, (now - dt.timedelta(days=days)).year}):
        with urllib.request.urlopen(CLI.format(st=station, y=y), timeout=60) as r: J = json.load(r)
        for x in J.get('results', []):
            d = x.get('valid'); hi, lo = num(x.get('high')), num(x.get('low'))
            sd = num(x.get('snowdepth', x.get('snowd', x.get('snow_depth'))))
            if d and hi is not None and lo is not None:
                rows[d] = ((hi + lo) / 2 - 32) * 5 / 9, (sd or 0.0) * 2.54
    start = (now - dt.timedelta(days=days)).date().isoformat()
    return [(d,) + rows[d] for d in sorted(rows) if d >= start]


def cfgi(series):
    """Run the index through [(date, T, D)]; returns (final CFGI, frozen flag with 83/56 hysteresis, per-day list)."""
    c, frozen, out = 0.0, False, []
    for d, T, D in series:
        c = max(0.0, CFGI_A * c - T * math.exp(-0.4 * CFGI_K * D))
        frozen = c >= FROZEN or (frozen and c >= THAWED)
        out.append([d, round(T, 1), round(D, 1), round(c, 1), frozen])
    return c, frozen, out


def p5_now(log=print):
    sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab')); import lf_antecedent, pandas as pd
    t0 = pd.Timestamp.now(tz='UTC').floor('D') + pd.Timedelta(hours=12)
    if t0 > pd.Timestamp.now(tz='UTC') - pd.Timedelta(hours=2): t0 -= pd.Timedelta(days=1)   # latest Pass2 24H grid that is surely out
    return lf_antecedent.antecedent(t0.tz_localize(None), D3_LAT, D3_LON, log=log)


def cmd_run(a):
    now = dt.datetime.now(dt.timezone.utc); out = dict(made=now.strftime('%Y-%m-%dT%H:%MZ'), made_by='proto/ground_state.py', area='MassDOT District 3')
    try:
        P = p5_now(); w, amc = amc_class(P['p_mm'], now.month)
        out['wetness'] = dict(state=w, amc=amc, p5_mm=round(P['p_mm'], 1), p5_max_mm=round(P['p_max_mm'], 1), window_utc=P['window_utc'],
                              season='growing' if 5 <= now.month <= 10 else 'dormant',
                              source='NOAA MRMS MultiSensor QPE 24H Pass2, District 3 mean; NRCS NEH-4 table 4.2 classes')
    except Exception as e: out['wetness'] = dict(state='unknown', error=repr(e)[:200])
    try:
        S = cli_days('KORH', now); c, fr, per = cfgi(S)
        out['frost'] = dict(state='frozen' if fr else 'thawed', cfgi=round(c, 1), frozen_at=FROZEN, thawed_below=THAWED, snow_cm=per[-1][2] if per else None,
                            t_mean_c=per[-1][1] if per else None, last_day=per[-1][0] if per else None, last_30=per[-30:],
                            source='NWS daily climate report, Worcester (KORH), via Iowa Environmental Mesonet; CFGI after Molnau & Bissell (1983)')
    except Exception as e: out['frost'] = dict(state='unknown', error=repr(e)[:200])
    fz = out['frost'].get('state') == 'frozen'; wt = out['wetness'].get('state')
    out['ground'] = 'frozen' if fz else (wt if wt in ('dry', 'normal', 'wet') else 'unknown')
    out['model_use'] = ('Shown for context only. The live forecast runs at the calibrated normal ground; the 5-day wetness rule lowered skill '
                        'in the 23 Oct 2026 backtest (docs/proto/runoff/AMC.md) and frozen ground is not yet backtested. Wet or frozen ground '
                        'means the forecast is likely too low.')
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1); print(json.dumps({k: out[k] for k in ('ground',)}), out['wetness'].get('p5_mm'), out['frost'].get('cfgi'))


def selftest():
    assert amc_class(10, 7) == ('dry', 'I') and amc_class(40, 7) == ('normal', 'II') and amc_class(60, 7) == ('wet', 'III')
    assert amc_class(10, 1) == ('dry', 'I') and amc_class(20, 1) == ('normal', 'II') and amc_class(30, 1) == ('wet', 'III')
    cold = [('d%02d' % i, -8.0, 0.0) for i in range(20)]
    c, fr, _ = cfgi(cold); assert fr and c > 83, c                 # 20 bare days at -8 C: frozen
    c2, fr2, _ = cfgi([(d, T, 40.0) for d, T, _ in cold]); assert not fr2 and c2 < 30, c2   # 40 cm of snow insulates
    c3, fr3, _ = cfgi(cold + [('w%02d' % i, 6.0, 0.0) for i in range(12)]); assert not fr3, c3   # a thaw week brings it back below 56
    assert num('T') == 0.0 and num('M') is None and num(3) == 3.0
    print('selftest ok', round(c, 1), round(c2, 1), round(c3, 1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd')
    r = sp.add_parser('run'); r.add_argument('--out', default=os.path.join(ROOT, 'docs', 'site', 'data', 'ground.json'))
    sp.add_parser('selftest'); a = ap.parse_args()
    cmd_run(a) if a.cmd == 'run' else selftest()
