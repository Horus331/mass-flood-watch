"""Warning priority: rank likely closures by how little warning they give (flash-flood index), without touching p_close.

    python proto/rating.py --out docs/proto/leominster_sep2023 [--gauges docs/proto/obs/gauges_sep2023.json]
    python proto/rating.py --selftest

Post-step on a proto/prototype.py output folder (segments.geojson with p_close, arrival_h, peak1h_mm, peak3h_mm, flashness_pct and the
30-min depth series 'd'; summary.json with the box-mean hourly rain).  Writes warning_priority.csv and rating.json there.

Per segment (all segments with p_close >= 0.1):
  onset_h        start of the first hour whose box-mean MRMS rain reaches 7.6 mm/h, the 'heavy rain' rate of the AMS Glossary of Meteorology
                 (rain intensity: heavy > 7.6 mm/h = 0.30 in/h).  Box-wide (per-cell rain timing is not stored by w9).
  lead_h         arrival_h (30 cm first reached on the segment) - onset_h, >= 0: the time a radar-triggered warning could have.
  rise_h         time from the first 5 cm to the first 30 cm in the 30-min series (0 = within one snapshot).
  intensity_ratio peak 1-h rain / mean hourly rain of the peak 3 h (1 = steady over 3 h, 3 = all in one hour).
  flashness_pct  share of the storm's rain in its worst hour (already in the prototype).
  Flash-flood index FFI = mean of three scores in [0, 1]:
      lead   1 - min(lead_h, 6) / 6     6 h = the NWS flash-flood time scale (flooding within 6 h of the causative rain;
                                        NWS Directive 10-950 / NWS Glossary 'flash flood')
      rise   1 - min(rise_h, 6) / 6     same time scale for depth 5 -> 30 cm
      rain   flashness_pct / 100        rain concentrated in one hour
  warning_priority = p_close x (0.5 + 0.5 FFI): a slow, certain closure keeps half its weight, a sudden one keeps all of it.  p_close is
  unchanged; this is a separate ranking for who gets warned first.
  Segments with 30 cm before the onset (water standing at t0, e.g. a DEM pit) get lead/rise scores 0 and tier 'wet before heavy rain (check)'.
  tier: 'warn now' p >= 0.5 and lead <= 3 h; 'warn' p >= 0.5 and lead <= 6 h; 'advisory (slow)' p >= 0.5 and lead > 6 h; 'watch' 0.1 <= p < 0.5.

Context at USGS gauges (observed 15-min discharge from proto/obs_fetch.py): Richards-Baker flashiness index RBI = sum |q_i - q_(i-1)| / sum q_i
(Baker, Richards, Loftus & Kramer 2004), here on hourly means over the storm window (an event RBI; Baker et al. use daily means over a
year, so the numbers are not comparable with their tables), the daily-mean RBI over the same window, peak / pre-storm base flow, and hours
from rain onset to the peak.
"""
import os, sys, json, csv, math, argparse, time, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..'))
HEAVY_MMH = 7.6        # AMS Glossary of Meteorology: heavy rain > 7.6 mm/h (0.30 in/h)
FLASH_H = 6.0          # NWS: flash flood = flooding within 6 h of the causative event
WARN_NOW_H = 3.0
SOURCES = dict(
    baker='Baker D.B., Richards R.P., Loftus T.T., Kramer J.W. (2004) A new flashiness index: characteristics and applications to midwestern rivers and streams. '
          'Journal of the American Water Resources Association 40(2), 503-522',
    nws='NOAA NWS Directive 10-950 (Hydrologic Services Program) and NWS Glossary: flash flood = rapid rise of water, flooding within 6 hours (often within 3 h) of the causative event',
    ams='American Meteorological Society Glossary of Meteorology, "rain": heavy rain > 7.6 mm/h (0.30 in/h)',
    pclose='p_close from proto/prototype.py (unchanged): Phi((peak depth - 0.30 m) / 0.10 m)')


def onset_hour(hourly):
    for k, v in enumerate(hourly or []):
        if v is not None and v >= HEAVY_MMH: return float(k)
    return None


def rise_hours(d, hours, lo=5, hi=30):
    d = np.asarray(d, float); h = np.asarray(hours, float)
    i5 = np.nonzero(d >= lo)[0]; i30 = np.nonzero(d >= hi)[0]
    if not len(i30): return None
    return float(h[i30[0]] - h[i5[0]]) if len(i5) else 0.0


def score_row(p, onset, hours):
    pc = float(p.get('p_close') or 0); arr = p.get('arrival_h'); d = p.get('d')
    pre = arr is not None and onset is not None and float(arr) < onset      # 30 cm before the heavy rain: standing water at t0 / DEM pit, not a flash closure
    lead = None if arr is None or onset is None or pre else float(arr) - onset
    rise = rise_hours(d, hours) if d is not None and len(d) == len(hours) and not pre else None
    p1 = float(p.get('peak1h_mm') or 0); p3 = float(p.get('peak3h_mm') or 0); fl = float(p.get('flashness_pct') or 0)
    ir = p1 / (p3 / 3.0) if p3 > 0 else None
    s_lead = 0.0 if lead is None else 1.0 - min(lead, FLASH_H) / FLASH_H
    s_rise = 0.0 if rise is None else 1.0 - min(rise, FLASH_H) / FLASH_H
    s_rain = min(max(fl / 100.0, 0.0), 1.0)
    ffi = (s_lead + s_rise + s_rain) / 3.0
    wp = pc * (0.5 + 0.5 * ffi)
    tier = 'wet before heavy rain (check)' if pre and pc >= 0.1 else ('warn now' if lead is not None and lead <= WARN_NOW_H else 'warn' if lead is not None and lead <= FLASH_H else 'advisory (slow)') if pc >= 0.5 else 'watch' if pc >= 0.1 else ''
    return dict(segment=int(p['segment']), road=p.get('road') or '', town=p.get('town') or '', road_class=p.get('road_class'), aadt=p.get('aadt'),
                p_close=round(pc, 3), arrival_h=arr, lead_h=None if lead is None else round(lead, 2), rise_h=None if rise is None else round(rise, 2),
                peak1h_mm=p1, intensity_ratio=None if ir is None else round(ir, 2), flashness_pct=fl,
                s_lead=round(s_lead, 3), s_rise=round(s_rise, 3), s_rain=round(s_rain, 3), flash_index=round(ffi, 3), warning_priority=round(wp, 4), tier=tier)


def _t(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))


def gauge_flashiness(path, storm_start, onset_h, box=None):
    """Event flashiness at the gauges of proto/obs_fetch.py (15-min q_cfs series)."""
    if not path or not os.path.exists(path): return None
    G = json.load(open(path)); out = []
    t0 = _t(storm_start) if storm_start else None
    tr = None
    if box:
        from pyproj import Transformer
        tr = Transformer.from_crs(4326, 26986, always_xy=True)
    for g in G.get('gauges', []):
        q = [(_t(t), v) for t, v in (g.get('q_cfs') or []) if v is not None and v >= 0]
        if len(q) < 8: continue
        T = np.array([(a - q[0][0]).total_seconds() / 3600.0 for a, _ in q]); Q = np.array([v for _, v in q], float) * 0.0283168
        hb = np.floor(T).astype(int); hq = np.bincount(hb, weights=Q) / np.maximum(np.bincount(hb), 1); hq = hq[np.bincount(hb) > 0]
        db = np.floor(T / 24).astype(int); dq = np.bincount(db, weights=Q) / np.maximum(np.bincount(db), 1); dq = dq[np.bincount(db) > 0]
        rbi = lambda x: float(np.abs(np.diff(x)).sum() / x[1:].sum()) if len(x) > 1 and x[1:].sum() > 0 else None
        k = int(np.argmax(Q)); tpk = q[k][0]
        base = None
        if t0 is not None:
            pre = Q[[a < t0 for a, _ in q]]; base = float(np.median(pre)) if len(pre) else None
        inb = None
        if tr and g.get('lon') is not None:
            x, y = tr.transform(g['lon'], g['lat']); inb = bool(box[0] <= x < box[2] and box[1] <= y < box[3])
        out.append(dict(site=g.get('site'), name=g.get('name'), in_box=inb, drain_km2=None if g.get('drain_mi2') is None else round(g['drain_mi2'] * 2.58999, 1),
                        rbi_event_hourly=None if rbi(hq) is None else round(rbi(hq), 3), rbi_event_daily=None if rbi(dq) is None else round(rbi(dq), 3),
                        peak_m3s=round(float(Q[k]), 2), base_m3s=None if base is None else round(base, 2),
                        peak_over_base=None if not base else round(float(Q[k]) / base, 1),
                        hours_onset_to_peak=None if t0 is None or onset_h is None else round((tpk - t0).total_seconds() / 3600.0 - onset_h, 2),
                        window=[q[0][0].isoformat(), q[-1][0].isoformat()]))
    out.sort(key=lambda r: (not r['in_box'], -(r['rbi_event_hourly'] or 0)))
    return out


def run(out, gauges=None):
    summ = json.load(open(os.path.join(out, 'summary.json'))); G = json.load(open(os.path.join(out, 'segments.geojson')))
    hours = summ.get('frame_hours') or []; onset = onset_hour(summ.get('rain_hourly_mean_mm'))
    rows = [score_row(f['properties'], onset, hours) for f in G['features'] if float(f['properties'].get('p_close') or 0) >= 0.1]
    rows.sort(key=lambda r: (-r['warning_priority'], -r['p_close']))
    for k, r in enumerate(rows): r['rank_warning'] = k + 1
    byp = sorted(rows, key=lambda r: (-r['p_close'], -(r['aadt'] or 0)))
    for k, r in enumerate(byp): r['rank_p_close'] = k + 1
    cols = ['rank_warning', 'rank_p_close', 'tier', 'warning_priority', 'p_close', 'flash_index', 'lead_h', 'rise_h', 'arrival_h', 'flashness_pct',
            'intensity_ratio', 'peak1h_mm', 's_lead', 's_rise', 's_rain', 'road', 'town', 'road_class', 'aadt', 'segment']
    with open(os.path.join(out, 'warning_priority.csv'), 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(cols)
        for r in rows: w.writerow([r[c] for c in cols])
    tiers = {t: sum(1 for r in rows if r['tier'] == t) for t in ('warn now', 'warn', 'advisory (slow)', 'watch', 'wet before heavy rain (check)')}
    flagged = [r for r in rows if r['p_close'] >= 0.5]
    rho = None
    if len(rows) > 2:
        a = np.array([r['rank_warning'] for r in rows], float); b = np.array([r['rank_p_close'] for r in rows], float); rho = float(np.corrcoef(a, b)[0, 1])
    lead = np.array([r['lead_h'] for r in flagged if r['lead_h'] is not None], float)
    lead = lead if len(lead) else np.zeros(0)
    res = dict(run=summ.get('run'), made=time.strftime('%Y-%m-%d %H:%M'), onset_h=onset, onset_rule=f'first hour with box-mean rain >= {HEAVY_MMH} mm/h',
               segments_scored=len(rows), tiers=tiers,
               lead_h_flagged=dict(n=int(len(lead)), median=None if not len(lead) else round(float(np.median(lead)), 2),
                                   p10=None if not len(lead) else round(float(np.percentile(lead, 10)), 2), p90=None if not len(lead) else round(float(np.percentile(lead, 90)), 2),
                                   share_within_6h=None if not len(lead) else round(float((lead <= FLASH_H).mean()), 3)),
               spearman_warning_vs_p_close_rank=None if rho is None else round(rho, 3),
               top10=[{k: r[k] for k in ('rank_warning', 'rank_p_close', 'tier', 'warning_priority', 'p_close', 'flash_index', 'lead_h', 'rise_h', 'flashness_pct', 'road', 'town')} for r in rows[:10]],
               gauges=gauge_flashiness(gauges, summ.get('storm_start'), onset, summ.get('box_epsg26986')),
               definitions=dict(flash_index='mean of s_lead = 1 - min(lead_h, 6)/6, s_rise = 1 - min(rise_h, 6)/6, s_rain = flashness_pct/100',
                                warning_priority='p_close x (0.5 + 0.5 x flash_index); p_close itself is not changed',
                                lead_h='arrival of 30 cm on the segment - onset of heavy rain (box mean >= 7.6 mm/h)', rise_h='first 5 cm -> first 30 cm, 30-min snapshots',
                                intensity_ratio='peak1h / (peak3h / 3)', rbi='sum |dq| / sum q (Baker et al. 2004), hourly and daily means over the observed window'),
               caveats=['Rain onset is box-wide; per-cell rain timing would sharpen lead_h.', 'The 6 h scale and equal weights are transparent choices, not fitted.',
                        'Event RBI on a 5-day window is context only; annual daily-mean RBI needs a year of USGS daily values.'],
               sources=SOURCES)
    json.dump(res, open(os.path.join(out, 'rating.json'), 'w'), indent=1)
    print(json.dumps({k: res[k] for k in ('onset_h', 'tiers', 'lead_h_flagged', 'spearman_warning_vs_p_close_rank', 'top10')}, indent=1)[:2500])
    return res


def selftest():
    import tempfile
    d = tempfile.mkdtemp(); hrs = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    fast = dict(segment=1, road='Fast', p_close=0.9, arrival_h=1.0, d=[0, 10, 40, 40, 40, 40, 40, 40, 40], peak1h_mm=60, peak3h_mm=90, flashness_pct=50)
    slow = dict(segment=2, road='Slow', p_close=0.95, arrival_h=8.0, d=[0, 6, 8, 10, 12, 14, 16, 20, 31], peak1h_mm=20, peak3h_mm=50, flashness_pct=15)
    low = dict(segment=3, road='Low', p_close=0.2, arrival_h=None, d=[0] * 9, peak1h_mm=10, peak3h_mm=20, flashness_pct=10)
    json.dump(dict(type='FeatureCollection', features=[dict(type='Feature', geometry=None, properties=p) for p in (fast, slow, low)]), open(os.path.join(d, 'segments.geojson'), 'w'))
    json.dump(dict(run='t', frame_hours=hrs, rain_hourly_mean_mm=[1, 20, 5, 0]), open(os.path.join(d, 'summary.json'), 'w'))
    r = run(d); rows = list(csv.DictReader(open(os.path.join(d, 'warning_priority.csv')))); ok = True
    def check(name, cond, det=''):
        nonlocal ok; ok &= bool(cond); print(('ok   ' if cond else 'FAIL ') + name, '' if cond else det)
    check('onset = first hour >= 7.6 mm/h', r['onset_h'] == 1.0, r['onset_h'])
    check('fast closure ranks first for warning though p_close is lower', rows[0]['road'] == 'Fast' and rows[1]['road'] == 'Slow', [x['road'] for x in rows])
    f = rows[0]; exp = 0.9 * (0.5 + 0.5 * ((1 - 0 / 6) + (1 - 0.5 / 6) + 0.5) / 3)
    check('fast: lead 0 h, rise 0.5 h, priority formula', float(f['lead_h']) == 0.0 and float(f['rise_h']) == 0.5 and abs(float(f['warning_priority']) - round(exp, 4)) < 1e-4, f)
    check('tiers', f['tier'] == 'warn now' and rows[1]['tier'] == 'advisory (slow)' and rows[2]['tier'] == 'watch', [x['tier'] for x in rows])
    check('p_close unchanged', float(rows[1]['p_close']) == 0.95)
    print('rating selftest', 'OK' if ok else 'FAILED', d); return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out'); ap.add_argument('--gauges', default=None, help='gauges_<storm>.json from proto/obs_fetch.py (default docs/proto/obs/gauges_sep2023.json if present)')
    ap.add_argument('--storm', help='storm id for the gauge file (default $STORM)'); ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    g = a.gauges
    if not g:      # the observed-gauge file of the same storm: docs/proto/obs/gauges_<storm>.json (--storm / $STORM; 2023-09 runs -> sep2023)
        st = a.storm or os.environ.get('STORM') or ('sep2023' if (json.load(open(os.path.join(a.out, 'summary.json'))).get('storm_start') or '')[:7] == '2023-09' else None)
        g = os.path.join(ROOT, 'docs', 'proto', 'obs', f'gauges_{st}.json') if st else None
    run(a.out, g)
