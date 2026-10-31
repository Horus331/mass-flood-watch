"""Upstream inflow at the box edge for w9_lisflood.py (opt-in: LF_INFLOW=usgs; nothing here runs otherwise).

Why: w9 runs a 20 x 20 km box with FREE edges and no inflow, so a gauge whose watershed reaches outside the box only sees the rain
that falls inside it.  This module
  1. delineates each scored gauge's watershed (USGS NLDI basin, NHDPlus V2) and reports the share inside the box (diagnosis),
  2. finds where the upstream NHDPlus flowlines enter the box (outside -> inside), keeps the outermost entries (an entry whose point lies
     in another entry's upstream basin is nested in it and dropped), and the upstream basin area of each (NLDI comid basin),
  3. gives each entry a discharge hydrograph by drainage-area ratio from a donor USGS gauge (OGC API 'continuous' 00060, 15 min):
     the gauge upstream of the entry with the largest drainage area, else the first gauge downstream of it on the main stem
     (flagged donor_scored when that gauge is one the run is scored on: then the run is a sensitivity bound, not a validation),
  4. returns LISFLOOD-FP point sources 'P x y QVAR name' (bci) and the .bdy time series.  LISFLOOD-FP point-source QVAR values are flow
     per unit width (m2/s): UpdateH adds value * dx * dt / dA (iterateq.cpp), so the file holds Q / RES.  Sources sit 3 cells inside the
     edge on the lowest (channel) cell near the entry so the FREE edge does not take the water straight back out.

env: LF_INFLOW=usgs, LF_INFLOW_MIN_KM2 (default 2: smaller entries ignored), LF_INFLOW_DONOR any|external (external: never use a gauge
     the run is scored on; default any), LF_INFLOW_SCALE (multiplier on every inflow, default 1).
    python lf_inflow.py --selftest      (offline geometry / file-format checks)
"""
import os, json, math, time
import numpy as np

NLDI = ['https://api.water.usgs.gov/nldi/linked-data', 'https://labs.waterdata.usgs.gov/api/nldi/linked-data']
OGC = 'https://api.waterdata.usgs.gov/ogcapi/v0/collections'
HDR = {'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'}
CFS = 0.0283168


# ---------------------------------------------------------------- geometry (no shapely on the runners)
def ring_area(xy):
    x, y = np.asarray(xy, float).T
    return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def clip_ring(xy, box):
    """Sutherland-Hodgman clip of a polygon ring to the rectangle box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    def clip(P, inside, cut):
        out = []
        for i in range(len(P)):
            a, b = P[i - 1], P[i]
            if inside(b):
                if not inside(a): out.append(cut(a, b))
                out.append(b)
            elif inside(a): out.append(cut(a, b))
        return out
    def cx(v):
        return lambda a, b: (v, a[1] + (b[1] - a[1]) * (v - a[0]) / (b[0] - a[0]))
    def cy(v):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (v - a[1]) / (b[1] - a[1]), v)
    P = [tuple(p) for p in xy]
    if len(P) > 1 and P[0] == P[-1]: P = P[:-1]
    for inside, cut in ((lambda p: p[0] >= x0, cx(x0)), (lambda p: p[0] <= x1, cx(x1)), (lambda p: p[1] >= y0, cy(y0)), (lambda p: p[1] <= y1, cy(y1))):
        if not P: break
        P = clip(P, inside, cut)
    return P


def poly_rings(geom):
    """[(outer, [holes])] from a GeoJSON Polygon / MultiPolygon (lon/lat)."""
    if geom['type'] == 'Polygon': return [(geom['coordinates'][0], geom['coordinates'][1:])]
    if geom['type'] == 'MultiPolygon': return [(p[0], p[1:]) for p in geom['coordinates']]
    return []


def poly_area_in_box(rings_xy, box):
    """(total km2, inside-box km2) of projected [(outer, holes)]."""
    tot = ins = 0.0
    for outer, holes in rings_xy:
        tot += ring_area(outer) - sum(ring_area(h) for h in holes)
        co = clip_ring(outer, box); ins += ring_area(co) if len(co) >= 3 else 0.0
        for h in holes:
            ch = clip_ring(h, box); ins -= ring_area(ch) if len(ch) >= 3 else 0.0
    return tot / 1e6, ins / 1e6


def point_in_ring(x, y, ring):
    r = np.asarray(ring, float); xs, ys = r[:, 0], r[:, 1]; xj, yj = np.roll(xs, 1), np.roll(ys, 1)
    m = ((ys > y) != (yj > y)) & (x < (xj - xs) * (y - ys) / np.where(yj - ys == 0, 1e-12, yj - ys) + xs)
    return bool(m.sum() % 2)


def in_poly(x, y, rings_xy):
    return any(point_in_ring(x, y, o) and not any(point_in_ring(x, y, h) for h in hs) for o, hs in rings_xy)


def entries(lines_xy, box):
    """Points where a polyline goes from outside the box to inside: [(line index, x, y, edge)].  Direction-free: a segment crossing the
    edge counts once whichever way it was digitised (the caller checks which side the upstream basin lies on)."""
    x0, y0, x1, y1 = box; out = []
    ins = lambda p: x0 < p[0] < x1 and y0 < p[1] < y1
    for k, L in enumerate(lines_xy):
        for a, b in zip(L[:-1], L[1:]):
            ia, ib = ins(a), ins(b)
            if ia == ib: continue
            o, i = (a, b) if ib else (b, a)
            best = None
            for edge, v, ax in (('W', x0, 0), ('E', x1, 0), ('S', y0, 1), ('N', y1, 1)):
                if (o[ax] - v) * (i[ax] - v) > 0 or o[ax] == i[ax]: continue
                t = (v - o[ax]) / (i[ax] - o[ax]); p = (o[0] + t * (i[0] - o[0]), o[1] + t * (i[1] - o[1]))
                if x0 - 1 <= p[0] <= x1 + 1 and y0 - 1 <= p[1] <= y1 + 1 and (best is None or t > best[0]): best = (t, p, edge)
            if best: out.append((k, best[1][0], best[1][1], best[2]))
    return out


def source_cell(x, y, edge, Z, chan, box, res, inset=3, search=4):
    """Cell (row, col) for a point source near the edge crossing (x, y): `inset` cells inside the edge, then the lowest cell (channel cells
    first) within `search` cells, never on the outer ring."""
    x0, y0, x1, y1 = box; ny, nx = Z.shape
    r = int((y1 - y) // res); c = int((x - x0) // res)
    if edge == 'W': c = inset
    elif edge == 'E': c = nx - 1 - inset
    elif edge == 'N': r = inset
    else: r = ny - 1 - inset
    r = min(max(r, 1), ny - 2); c = min(max(c, 1), nx - 2)
    ra, rb, ca, cb = max(1, r - search), min(ny - 1, r + search + 1), max(1, c - search), min(nx - 1, c + search + 1)
    if edge in 'WE': ca, cb = (c, c + 2) if edge == 'W' else (c - 1, c + 1)
    else: ra, rb = (r, r + 2) if edge == 'N' else (r - 1, r + 1)
    w = Z[ra:rb, ca:cb].astype(float) - 100.0 * (chan[ra:rb, ca:cb] if chan is not None else 0)
    i = np.unravel_index(int(np.argmin(w)), w.shape)
    return ra + i[0], ca + i[1]


def bdy_text(series, title='w9 LF_INFLOW point-source inflows (m2/s = Q / RES)'):
    """LISFLOOD-FP .bdy: header line, then per boundary: name, '<n> seconds', '<value> <time>' rows."""
    L = [f'# {title}']
    for name, t_s, v in series:
        L += [name, f'{len(t_s)} seconds'] + [f'{float(a):.5f} {float(b):.0f}' for b, a in zip(t_s, v)]
    return '\n'.join(L) + '\n'


# ---------------------------------------------------------------- web (Actions only)
def _get(url, params=None, tries=4, timeout=180):
    import requests
    for k in range(tries):
        try:
            r = requests.get(url, params=params, headers=HDR, timeout=timeout)
            if r.status_code == 404: return None
            if r.status_code in (429, 500, 502, 503, 504): raise RuntimeError(f'HTTP {r.status_code}')
            r.raise_for_status(); return r.json()
        except Exception as e:
            if k == tries - 1: raise
            time.sleep(5 * (k + 1))


def nldi(path, params=None):
    err = None
    for base in NLDI:
        try:
            j = _get(f'{base}/{path}', params)
            if j is not None: return j
        except Exception as e: err = e
    if err: raise err
    return None


def gauge_q(site, t0, t1):
    """15-min discharge (UTC pandas Series, m3/s) and drainage area (km2) from the OGC API; (None, area) if no data.
    Through proto/usgs_api.py when the repo's proto/ is next to sim/ (legacy WaterServices fallback until 22 Feb 2027, env USGS_SOURCE);
    the inline OGC query below otherwise."""
    import pandas as pd, sys
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'proto')); import usgs_api as U
    except ImportError: U = None
    if U is not None:
        G, used = U.iv(sites=[site], start=t0, end=t1, params=('00060',))
        g = G.get(site) or {}; area = g['drain_mi2'] * 2.58999 if g.get('drain_mi2') is not None else None
        q = U.to_pandas(G, site, '00060')
        return (None, area) if q is None else (q * CFS, area)
    area = None
    try:
        m = _get(f'{OGC}/monitoring-locations/items', dict(id=f'USGS-{site}', f='json'))
        p = (m or {}).get('features', [{}])[0].get('properties', {}) if (m or {}).get('features') else {}
        area = float(p['drainage_area']) * 2.58999 if p.get('drainage_area') is not None else None
    except Exception: pass
    j = _get(f'{OGC}/continuous/items', dict(monitoring_location_id=f'USGS-{site}', parameter_code='00060', f='json', limit=10000,
                                             time=f"{t0.strftime('%Y-%m-%dT%H:%M:%SZ')}/{t1.strftime('%Y-%m-%dT%H:%M:%SZ')}"))
    rows = {}
    for f in (j or {}).get('features', []):
        q = f['properties']
        try: v = float(q['value'])
        except (TypeError, ValueError): continue
        if v > -999: rows.setdefault(q.get('time_series_id') or '', []).append((q['time'], v))
    if not rows: return None, area
    t, v = zip(*sorted(max(rows.values(), key=len)))
    return pd.Series(np.array(v) * CFS, index=pd.to_datetime(list(t), utc=True)).sort_index(), area


def project(tf, coords):
    a = np.asarray(coords, float)[:, :2]; x, y = tf.transform(a[:, 0], a[:, 1]); return list(zip(x, y))


def build_inflows(BOX, RES, Z, chan, t0, hours, gauges, log=print, env=os.environ):
    """gauges: [{site, name, lon, lat, drain_mi2}] in the box (the scored ones).  Returns dict(report, bci_lines, bdy, n)."""
    import pandas as pd
    from pyproj import Transformer
    tf = Transformer.from_crs(4326, 26986, always_xy=True)
    min_km2 = float(env.get('LF_INFLOW_MIN_KM2', '2')); donor_mode = env.get('LF_INFLOW_DONOR', 'any'); scale = float(env.get('LF_INFLOW_SCALE', '1'))
    t0 = pd.Timestamp(t0); t0 = t0.tz_localize('UTC') if t0.tzinfo is None else t0.tz_convert('UTC'); t1 = t0 + pd.Timedelta(hours=hours)
    scored = {g['site'] for g in gauges}
    rep = dict(gauges=[], entries=[], note='NLDI (NHDPlus V2) basins; areas km2; share_in_box = basin area inside the model box / basin area')
    # 1. gauge basins
    lines, comids = [], []
    for g in gauges:
        s = g['site']; row = dict(site=s, name=g.get('name'), drain_km2_usgs=round((g.get('drain_mi2') or 0) * 2.58999, 1))
        try:
            B = None
            for split in ('true', 'false'):
                try: B = nldi(f'nwissite/USGS-{s}/basin', dict(splitCatchment=split, simplified='false'));
                except Exception as e: log(f'  NLDI basin {s} split={split}: {repr(e)[:100]}')
                if B and B.get('features'): break
            R = [(project(tf, o), [project(tf, h) for h in hs]) for f in B['features'] for o, hs in poly_rings(f['geometry'])]
            tot, ins = poly_area_in_box(R, BOX)
            allxy = np.concatenate([np.asarray(o) for o, _ in R])
            row.update(basin_km2=round(tot, 1), in_box_km2=round(ins, 1), share_in_box=round(ins / tot, 3) if tot else None,
                       basin_bbox=[round(float(v)) for v in (*allxy.min(0), *allxy.max(0))])
            F = nldi(f'nwissite/USGS-{s}/navigation/UT/flowlines', dict(distance='300'))
            n0 = len(lines)
            for f in (F or {}).get('features', []):
                c = f['properties'].get('nhdplus_comid'); gm = f['geometry']
                parts = gm['coordinates'] if gm['type'] == 'MultiLineString' else [gm['coordinates']]
                for p in parts:
                    lines.append(project(tf, p)); comids.append(str(c))
            row['upstream_flowlines'] = len(lines) - n0
        except Exception as e:
            row['error'] = repr(e)[:200]
        rep['gauges'].append(row)
        log(f"inflow: basin {s} {(row.get('name') or '')[:40]}: NLDI {row.get('basin_km2')} km2 (USGS {row['drain_km2_usgs']}), "
            f"{row.get('in_box_km2')} km2 in the box = {100 * (row.get('share_in_box') or 0):.0f}%, basin bbox {row.get('basin_bbox')}" + (f" ERROR {row['error']}" if 'error' in row else ''))
    # 2. entries, deduplicated by comid, with each one's upstream basin
    E, seen = [], set()
    for k, x, y, edge in entries(lines, BOX):
        c = comids[k]
        if c in seen: continue
        seen.add(c); E.append(dict(comid=c, x=int(round(float(x))), y=int(round(float(y))), edge=edge))
    log(f'inflow: {len(E)} flowline crossings of the box edge')
    for e in E:
        try:
            B = nldi(f"comid/{e['comid']}/basin", dict(simplified='false'))
            R = [(project(tf, o), [project(tf, h) for h in hs]) for f in B['features'] for o, hs in poly_rings(f['geometry'])]
            tot, ins = poly_area_in_box(R, BOX); e.update(up_km2=round(tot, 2), up_in_box_km2=round(ins, 2), _R=R)
        except Exception as ex: e.update(up_km2=None, error=repr(ex)[:120])
    E = [e for e in E if e.get('up_km2') and e['up_km2'] - e['up_in_box_km2'] >= min_km2 and e['up_in_box_km2'] < 0.5 * e['up_km2']]
    E.sort(key=lambda e: -e['up_km2'])
    keep = []
    for e in E:      # nested: this entry's point lies inside a bigger kept entry's basin (river leaves and re-enters the box)
        if any(in_poly(e['x'] + 0.0, e['y'] + 0.0, k['_R']) for k in keep): e['nested'] = True; continue
        keep.append(e)
    # 3. donors
    qcache = {}
    def q_of(site):
        if site not in qcache:
            try: qcache[site] = gauge_q(site, t0 - pd.Timedelta(hours=6), t1 + pd.Timedelta(hours=6))
            except Exception as ex: log(f'  OGC {site}: {repr(ex)[:100]}'); qcache[site] = (None, None)
        return qcache[site]
    series, bci = [], []
    for i, e in enumerate(keep):
        cand = []
        for nav, dist in (('UT', '300'), ('DM', '80')):
            try:
                S = nldi(f"comid/{e['comid']}/navigation/{nav}/nwissite", dict(distance=dist))
                for f in (S or {}).get('features', []):
                    sid = f['properties']['identifier'].replace('USGS-', '')
                    if len(sid) <= 10: cand.append((nav, sid))
            except Exception as ex: log(f"  NLDI sites {e['comid']} {nav}: {repr(ex)[:100]}")
        donor = None
        for nav in ('UT', 'DM'):
            best = None
            for nv, sid in cand:
                if nv != nav or (donor_mode == 'external' and sid in scored): continue
                q, a = q_of(sid)
                if q is None or not a or len(q) < 8: continue
                if nav == 'UT' and (best is None or a > best[2]): best = (sid, q, a)
                if nav == 'DM' and best is None: best = (sid, q, a)       # NLDI lists downstream sites nearest first
            if best: donor = (nav,) + best; break
        if donor is None: e.update(donor=None); log(f"inflow: entry {e['comid']} {e['edge']} ({e['up_km2']} km2): no donor gauge with discharge, skipped"); continue
        nav, sid, q, a = donor; ratio = e['up_km2'] / a
        tt = pd.date_range(t0, t1, freq='15min'); qq = np.interp(tt.asi8, q.index.asi8, q.values) * ratio * scale
        r, c = source_cell(e['x'], e['y'], e['edge'], Z, chan, BOX, RES)
        xc, yc = BOX[0] + (c + 0.5) * RES, BOX[3] - (r + 0.5) * RES; name = f'IN{i:02d}'
        series.append((name, (tt - t0).total_seconds().values, qq / RES)); bci.append(f'P {xc:.1f} {yc:.1f} QVAR {name}')
        e.update(donor=sid, donor_dir='upstream' if nav == 'UT' else 'downstream', donor_km2=round(a, 1), ratio=round(ratio, 3),
                 donor_scored=sid in scored, cell=[int(r), int(c)], q_peak_m3s=round(float(qq.max()), 2), q_t0_m3s=round(float(qq[0]), 2),
                 q_peak_utc=tt[int(np.argmax(qq))].strftime('%Y-%m-%dT%H:%MZ'), volume_m3=round(float(qq.sum()) * 900.0))
        log(f"inflow: {name} {e['edge']} edge at ({e['x']}, {e['y']}) comid {e['comid']}: {e['up_km2']} km2 upstream; donor {sid} ({e['donor_dir']}, "
            f"{a:.1f} km2{', SCORED gauge' if sid in scored else ''}) x {ratio:.3f}: Q {e['q_t0_m3s']} -> peak {e['q_peak_m3s']} m3/s at {e['q_peak_utc']}")
    for e in E: e.pop('_R', None)
    rep['entries'] = E; rep['n_sources'] = len(series); rep['scale'] = scale; rep['donor_mode'] = donor_mode
    return dict(report=rep, bci_lines=bci, bdy=bdy_text(series) if series else None, n=len(series))


def selftest():
    box = (0.0, 0.0, 1000.0, 1000.0)
    sq = [(-500, -500), (500, -500), (500, 500), (-500, 500), (-500, -500)]
    tot, ins = poly_area_in_box([(sq, [])], box); assert abs(tot - 1.0) < 1e-9 and abs(ins - 0.25) < 1e-9, (tot, ins)
    hole = [(100, 100), (200, 100), (200, 200), (100, 200)]
    tot, ins = poly_area_in_box([(sq, [hole])], box); assert abs(ins - 0.24) < 1e-9
    assert in_poly(0, 0, [(sq, [])]) and in_poly(300, 300, [(sq, [hole])]) and not in_poly(150, 150, [(sq, [hole])]) and not in_poly(900, 900, [(sq, [])])
    E = entries([[(-100, 500), (100, 500), (300, 500)], [(500, 1200), (500, 900)], [(500, 500), (500, -10)]], box)
    assert [(k, round(x), round(y), ed) for k, x, y, ed in E] == [(0, 0, 500, 'W'), (1, 500, 1000, 'N'), (2, 500, 0, 'S')], E
    Z = np.full((50, 50), 10.0); Z[:, 20] = 5.0; ch = np.zeros(Z.shape, bool); ch[:, 22] = True
    r, c = source_cell(435.0, 1000.0, 'N', Z, ch, box, 20.0); assert (r, c) == (3, 22), (r, c)
    t = bdy_text([('IN00', np.array([0, 900.0]), np.array([0.5, 1.25]))]).split('\n')
    assert t[1] == 'IN00' and t[2] == '2 seconds' and t[3] == '0.50000 0' and t[4] == '1.25000 900'
    print('lf_inflow selftest OK: clip area, holes, point-in-polygon, edge entries, source cell, .bdy format')


if __name__ == '__main__':
    import sys
    if '--selftest' in sys.argv: selftest()
