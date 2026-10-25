"""Label evidence ladder (docs/proto/obs/LABELS_ROUND3.md): an evidence tier and a weight for every label row of every source, written as a
DERIVED file per storm.  The original label files are never rewritten.

    python proto/label_tiers.py build            # -> proto/data/labels_tiered_<storm>.csv for every non-locked catalogue storm with labels
    python proto/label_tiers.py summary          # counts by tier / source family (stdout + docs/proto/obs/round3/tiers_summary.json)
    python proto/label_tiers.py selftest

Sources read per storm (proto/data/): labels_<storm>_*.csv (NWS LSR / Storm Events, news, WX1BOX, Leominster DPW inventory, MA CDBG-DR site
table), crashwater_<storm>.csv (MassDOT water-surface crashes), scf_<storm>.csv (SeeClickFix 311 issues).  Locked storms (PROTOCOL.md §2)
are skipped: nothing is read or written for them.

TIERS AND WEIGHTS (fixed 25 Oct 2026, before any tiered score was computed; changing them is a new pre-registration):
  confirmed_inundation  1.0  photo / field report of water or water damage on the segment: municipal DPW damage inventory, state post-event
                             damage-site table (MA CDBG-DR / disaster recovery plan, MassDOT hearing handout), and NWS / Storm Events / WX1BOX
                             reports that describe an observation on the road (car stuck / stranded, water rescue, a stated depth, under water,
                             impassable, washed out) or physical damage types (washout, culvert_failure, sinkhole, bridge_damage)
  confirmed_closure     1.0  an official closure with a flood cause: type 'closed', or 'closed / closure / shut down' in the text of an NWS,
                             WX1BOX or news row (checked before the text-inundation rule; both weigh 1.0)
  corroborated          1.0  a row that is otherwise 'reported', with a row of a DIFFERENT source family within 150 m in the same storm
                             (town-level coordinates never corroborate; LSR and Storm Events are one family, 'NWS', since Storm Events restate LSRs)
  reported              0.6  a single report: generic 'flooded' NWS / news rows, MassDOT water-surface crashes (surface code 6 also covers rain
                             sheet flow), SeeClickFix issues (unverified public reports, photos not inspected)
  suspected             0.3  indirect signals (speed drops, etc.): none exist yet
Weight of a scored site (score_v2 SCORE_TIERS=1) = max weight of its labels.  Unreported roads stay unknown, never negative: tiers only
down-weight positives; no row of any tier creates a negative.
"""
import csv
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, 'data')
LOCKED = ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016')
TIERS = ('confirmed_inundation', 'confirmed_closure', 'corroborated', 'reported', 'suspected')
WEIGHTS = dict(confirmed_inundation=1.0, confirmed_closure=1.0, corroborated=1.0, reported=0.6, suspected=0.3)
CORROB_M = 150.0
DAMAGE_TYPES = ('washout', 'culvert_failure', 'sinkhole', 'bridge_damage')
WATER_OBS = re.compile(r'stuck|stranded|stall|rescue|\b\d+(\.\d+)?\s*(-\s*\d+\s*)?(inch|inches|in\.|foot|feet|ft)\b|under\s*water|underwater|submerged|'
                       r'impassable|impassible|wash(ed)?\s*out|washout|water (over|across) (the )?(road|street)|over the road', re.I)
CLOSED = re.compile(r'\bclosed\b|\bclosure|shut down', re.I)
OUT_COLS = ['storm', 'file', 'id', 'key', 'source_family', 'tier', 'weight', 'base_tier', 'corroborated_by', 'n_families_150m', 'type', 'town',
            'lon', 'lat', 'coord_quality', 'time_local']


def storms():
    C = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))['events']
    out = [e['id'] for e in C if e['id'] not in LOCKED]
    return [s for s in out if source_files(s)]


def source_files(storm):
    if storm in LOCKED: return []
    F = sorted(glob.glob(os.path.join(DATA, f'labels_{storm}_*.csv')))
    for pat in (f'crashwater_{storm}.csv', f'scf_{storm}.csv'): F += sorted(glob.glob(os.path.join(DATA, pat)))
    return F


def family(r, fname):
    s = (r.get('source') or '').strip(); u = (r.get('source_url') or '')
    if fname.startswith('scf_') or s == 'SeeClickFix': return 'SeeClickFix'
    if fname.startswith('crashwater_') or s == 'MassDOT_crash': return 'MassDOT_crash'
    if 'DPW' in u or fname.endswith('_dpw.csv'): return 'DPW'
    if 'mass.gov/doc' in u: return 'MA_state'
    if s in ('LSR', 'StormEvents') or 'mesonet.agron' in u or 'ncdc.noaa' in u or 'ncei.noaa' in u or 'dem.ri.gov' in u: return 'NWS'
    if s == 'WX1BOX' or 'wx1box' in u: return 'WX1BOX'
    return 'news'


def base_tier(r, fam):
    t = (r.get('type') or '').strip(); txt = f"{r.get('name', '')} {r.get('quote', '')}"
    if fam in ('DPW', 'MA_state'): return 'confirmed_inundation'
    if fam in ('SeeClickFix', 'MassDOT_crash'): return 'reported'
    if fam in ('NWS', 'WX1BOX', 'news') and (t == 'closed' or CLOSED.search(txt)): return 'confirmed_closure'
    if fam in ('NWS', 'WX1BOX') and (t in DAMAGE_TYPES or t == 'impassable' or WATER_OBS.search(txt)): return 'confirmed_inundation'
    return 'reported'


def _xy(lon, lat):
    k = 111320.0; return lon * k * math.cos(math.radians(42.3)), lat * 110540.0


def tier_rows(storm):
    """-> list of tiered rows (dicts with OUT_COLS) for one storm, from every source file."""
    rows = []
    for f in source_files(storm):
        fn = os.path.basename(f)
        for r in csv.DictReader(open(f)):
            try: lon, lat = float(r['lon']), float(r['lat'])
            except (TypeError, ValueError, KeyError): lon = lat = None
            fam = family(r, fn); bt = base_tier(r, fam)
            rows.append(dict(storm=storm, file=fn, id=r['id'], key=f'{fn}:{r["id"]}', source_family=fam, base_tier=bt, tier=bt, type=r.get('type', ''),
                             town=r.get('town', ''), lon=lon, lat=lat, coord_quality=(r.get('coord_quality') or 'approx').strip(), time_local=r.get('time_local', '')))
    pts = [(i, *_xy(r['lon'], r['lat'])) for i, r in enumerate(rows) if r['lon'] is not None and r['coord_quality'] != 'town']
    for r in rows: r['corroborated_by'] = []; r['n_families_150m'] = 1
    for i, xi, yi in pts:
        fams = {rows[i]['source_family']}; by = []
        for j, xj, yj in pts:
            if j != i and math.hypot(xi - xj, yi - yj) <= CORROB_M and rows[j]['source_family'] != rows[i]['source_family']:
                fams.add(rows[j]['source_family']); by.append(rows[j]['key'])
        rows[i]['n_families_150m'] = len(fams); rows[i]['corroborated_by'] = by
        if rows[i]['base_tier'] == 'reported' and by: rows[i]['tier'] = 'corroborated'
    for r in rows:
        r['weight'] = WEIGHTS[r['tier']]; r['corroborated_by'] = ';'.join(r['corroborated_by'])
    return rows


def weights_by_key(storm):
    """{label key 'file:id' -> (tier, weight)} for score_v2 / closure training; computed on the fly (same rules as the derived file)."""
    return {r['key']: (r['tier'], r['weight']) for r in tier_rows(storm)}


def weights_by_id(storm):
    """{label id -> weight} (closure_ml / closure_v2 features carry label ids, not files)."""
    out = {}
    for r in tier_rows(storm): out[r['id']] = max(out.get(r['id'], 0.0), r['weight'])
    return out


def build():
    n = 0
    for s in storms():
        R = tier_rows(s)
        with open(os.path.join(DATA, f'labels_tiered_{s}.csv'), 'w', newline='') as fh:
            w = csv.DictWriter(fh, OUT_COLS); w.writeheader(); w.writerows(R)
        n += len(R)
    print('tiered rows', n)


def summary(out=os.path.join(ROOT, 'docs', 'proto', 'obs', 'round3', 'tiers_summary.json')):
    from collections import Counter
    T = Counter(); FT = Counter(); per = {}
    for s in storms():
        R = tier_rows(s); per[s] = dict(Counter(r['tier'] for r in R))
        for r in R: T[r['tier']] += 1; FT[f"{r['source_family']}|{r['tier']}"] += 1
    res = dict(made_by='proto/label_tiers.py summary', weights=WEIGHTS, corroboration_m=CORROB_M, by_tier=dict(T), by_family_tier=dict(sorted(FT.items())), per_storm=per)
    os.makedirs(os.path.dirname(out), exist_ok=True); json.dump(res, open(out, 'w'), indent=1); print(json.dumps(res['by_tier']), json.dumps(res['by_family_tier'], indent=0))
    return res


def selftest():
    ok = True
    def chk(name, c):
        nonlocal ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + name)
    chk('dpw', base_tier(dict(type='washout'), 'DPW') == 'confirmed_inundation')
    chk('closed', base_tier(dict(type='flooded', quote='road closed due to flooding'), 'NWS') == 'confirmed_closure')
    chk('stuck', base_tier(dict(type='flooded', quote='car stuck in 2 feet of water'), 'NWS') == 'confirmed_inundation')
    chk('generic', base_tier(dict(type='flooded', quote='Main Street flooded'), 'NWS') == 'reported')
    chk('scf', base_tier(dict(type='reported_flooding', quote='car stuck'), 'SeeClickFix') == 'reported')
    chk('news-depth-not-inundation', base_tier(dict(type='flooded', quote='2 feet of water'), 'news') == 'reported')
    chk('weights', WEIGHTS == dict(confirmed_inundation=1.0, confirmed_closure=1.0, corroborated=1.0, reported=0.6, suspected=0.3))
    chk('locked', all(source_files(s) == [] for s in LOCKED))
    return ok


if __name__ == '__main__':
    c = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if c == 'selftest': sys.exit(0 if selftest() else 1)
    build() if c == 'build' else summary()
