"""Geocode road-level flood labels with OpenStreetMap (run on GitHub Actions: .github/workflows/label_geocode.yml; the sandbox cannot reach OSM).

Input: a JSON list of queries (docs/proto/obs/labels_geocode_queries.json), one per label site:
    {"key": "...", "town": "Gardner", "towns": [...optional neighbours], "a": "Walnut Street", "b": "John Street" | null,
     "near": [lon, lat] | null, "addr": "86 Southwest Cutoff, Worcester, MA" | null}
  a / b feature specs:  "Walnut Street"            highway way with that name (case-insensitive)
                        "ref:MA 12"                highway way whose ref list holds MA 12 (or US 20, I 290 ...)
                        "water:West Branch Ware River"   waterway way with that name
                        "rail"                     any railway=rail way
                        "A|B"                      either spec
Output (docs/proto/obs/labels_geocode_osm.json): per key
  pair (a and b):  closest approach of the two features inside the town(s): lon/lat, distance (0 = shared node), and up to 5 candidate
                   crossings (distinct places, ordered by distance to `near` when given, else by gap)
  single (a only): the vertex of a nearest to `near` (when given) and the vertex nearest the feature centroid, with the feature length
  addr:            Nominatim result (lon/lat, display name, class/type)
Coordinates are OSM (ODbL); the label files cite the report as the source and say the point was placed with OSM.

    python proto/label_geocode.py --queries docs/proto/obs/labels_geocode_queries.json --out docs/proto/obs/labels_geocode_osm.json
"""
import json, time, argparse, re
import numpy as np
import requests
from pyproj import Transformer

OVERPASS = ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter', 'https://overpass.private.coffee/api/interpreter']
UA = {'User-Agent': 'mass-flood-watch label geocoder (github.com/Horus331/mass-flood-watch)'}
T = Transformer.from_crs(4326, 26986, always_xy=True); TI = Transformer.from_crs(26986, 4326, always_xy=True)


LOG = []


def overpass(q):
    for k in range(3):
        u = OVERPASS[k % len(OVERPASS)]
        try:
            r = requests.post(u, data={'data': q}, headers=UA, timeout=60)
            if r.status_code == 200: return r.json()
            LOG.append(f'{u} {r.status_code}'); print('  overpass', u, r.status_code, r.text[:120], flush=True)
        except Exception as e: LOG.append(f'{u} {repr(e)[:80]}'); print('  overpass', u, repr(e)[:120], flush=True)
        time.sleep(5 + 5 * k)
    return None


def esc(s): return re.sub(r'([\\"^$.|?*+()\[\]{}])', r'\\\1', s)


def filt(spec):
    out = []
    for s in spec.split('|'):
        s = s.strip()
        if s == 'rail': out.append('["railway"="rail"]')
        elif s.startswith('ref:'): out.append('["highway"]["ref"~"(^|;) *%s *(;|$)",i]' % esc(s[4:].strip()))
        elif s.startswith('water:'): out.append('["waterway"]["name"~"^%s$",i]' % esc(s[6:].strip()))
        else: out.append('["highway"]["name"~"^%s$",i]' % esc(s))
    return out


def fetch(spec, towns, near):
    """Ways matching spec within 4 km of the NWS point (fast), else inside the towns (MA admin_level 8)."""
    F = filt(spec)
    if near:
        J = overpass('[out:json][timeout:90];(%s);out geom;' % ''.join('way(around:4000,%f,%f)%s;' % (near[1], near[0], f) for f in F))
        if J and J.get('elements'): return J['elements']
    if towns:
        tq = ''.join('rel(area.ma)["boundary"="administrative"]["admin_level"="8"]["name"="%s"];' % t for t in towns)
        J = overpass('[out:json][timeout:120];area["ISO3166-2"="US-MA"]->.ma;(%s)->.r;.r map_to_area->.t;(%s);out geom;' % (tq, ''.join('way(area.t)%s;' % f for f in F)))
        if J: return J['elements']
    return []


def lines(els):
    L = []
    for e in els:
        g = e.get('geometry') or []
        if len(g) < 2: continue
        x, y = T.transform([p['lon'] for p in g], [p['lat'] for p in g])
        L.append(dict(id=e['id'], name=(e.get('tags') or {}).get('name'), ref=(e.get('tags') or {}).get('ref'), xy=np.column_stack([x, y]), nodes=e.get('nodes') or []))
    return L


def densify(xy, step=5.0):
    P = [xy[0]]
    for a, b in zip(xy[:-1], xy[1:]):
        n = max(1, int(np.hypot(*(b - a)) / step))
        for k in range(1, n + 1): P.append(a + (b - a) * k / n)
    return np.array(P)


def lonlat(p): lo, la = TI.transform(p[0], p[1]); return [round(lo, 6), round(la, 6)]


def pair(A, B, near):
    from scipy.spatial import cKDTree
    PA = np.vstack([densify(l['xy']) for l in A]); PB = np.vstack([densify(l['xy']) for l in B])
    d, j = cKDTree(PB).query(PA); C = []
    for k in np.argsort(d):
        if d[k] > 400 or len(C) >= 5: break
        p = (PA[k] + PB[j[k]]) / 2
        if all(np.hypot(*(p - np.array(c['xy']))) > 150 for c in C): C.append(dict(xy=p.tolist(), gap_m=round(float(d[k]), 1)))
    if near is not None:
        nx, ny = T.transform(*near)
        for c in C: c['to_near_m'] = round(float(np.hypot(c['xy'][0] - nx, c['xy'][1] - ny)))
    for c in C: c['lonlat'] = lonlat(c['xy']); del c['xy']
    shared = set(n for l in A for n in l['nodes']) & set(n for l in B for n in l['nodes'])
    return dict(candidates=C, shared_nodes=len(shared), best_gap_m=round(float(d.min()), 1))


def single(A, near):
    P = np.vstack([l['xy'] for l in A]); L = sum(float(np.hypot(*np.diff(l['xy'], axis=0).T).sum()) for l in A)
    c = P.mean(0); k = np.hypot(*(P - c).T).argmin(); r = dict(length_m=round(L), centroid_vertex=lonlat(P[k]), names=sorted({str(l['name']) for l in A})[:5])
    if near is not None:
        nx, ny = T.transform(*near); d = np.hypot(P[:, 0] - nx, P[:, 1] - ny); k = d.argmin()
        r.update(nearest_vertex=lonlat(P[k]), nearest_m=round(float(d[k])))
    return r


def nominatim(q):
    try:
        r = requests.get('https://nominatim.openstreetmap.org/search', params=dict(q=q, format='json', limit=3, countrycodes='us'), headers=UA, timeout=60)
        time.sleep(1.2)
        return [dict(lonlat=[float(x['lon']), float(x['lat'])], name=x.get('display_name'), cls=x.get('class'), type=x.get('type')) for x in r.json()]
    except Exception as e: return dict(error=repr(e)[:200])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--queries', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--addr-only', action='store_true', help='Nominatim only (no Overpass): queries need "addr"')
    ap.add_argument('--shard', default='0/1', help='i/n: this job does queries i, i+n, ... (parallel Actions jobs, one output file each)')
    ap.add_argument('--seed', default='', help='earlier output file: keys already resolved there are skipped')
    ap.add_argument('--seed2', default='', help='another earlier output file (merged shards)')
    a = ap.parse_args(); Q = json.load(open(a.queries)); R = {}
    i, n = (int(v) for v in a.shard.split('/')); Q = Q[i::n]
    done = {}
    for f in [a.seed, a.seed2, a.out]:
        try: done.update({k: v for k, v in json.load(open(f)).items() if v.get('pair') or v.get('single') or v.get('addr')})
        except Exception: pass
    Q = [q for q in Q if q['key'] not in done]; print(len(Q), 'queries to do', flush=True)
    try: R = json.load(open(a.out))
    except Exception: pass
    for q in Q:
        k = q['key']
        if k in R and not R[k].get('error'): continue
        towns = q.get('towns') or ([q['town']] if q.get('town') else []); near = q.get('near'); r = dict(q=q)
        try:
            if q.get('addr'): r['addr'] = nominatim(q['addr'])
            if q.get('a') and not a.addr_only:
                A = lines(fetch(q['a'], towns, near)); r['a_ways'] = len(A)
                if q.get('b'):
                    B = lines(fetch(q['b'], towns, near)); r['b_ways'] = len(B)
                    if A and B: r['pair'] = pair(A, B, near)
                if A: r['single'] = single(A, near)
        except Exception as e: r['error'] = repr(e)[:300]
        if LOG: r['overpass_log'] = LOG[:]; LOG.clear()
        R[k] = r; print(k, {x: r.get(x) for x in ('a_ways', 'b_ways')}, (r.get('pair') or {}).get('candidates', [None])[:1], flush=True)
        json.dump(R, open(a.out, 'w'), indent=1); time.sleep(2)


if __name__ == '__main__':
    main()
