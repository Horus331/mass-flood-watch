"""Every road the model evaluates in District 3 (docs/graph_segments.json, MassDOT road inventory) as one light file for the map, so the
smallest street is drawn at every zoom on every tab (the basemap tiles drop minor streets below street zoom): docs/site/data/streets_d3.json.
Geometry simplified to ~7 m and delta-encoded (lon/lat x 1e5, first point absolute); c = class (0 local/collector, 1 arterial, 2 highway).
Usage: python proto/build_streets_d3.py"""
import json, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
import impacts as IM


def simplify(x, y, tol):
    """Douglas-Peucker on integer coordinates (1e-5 deg ~ 1 m)."""
    if len(x) < 3: return list(range(len(x)))
    keep = np.zeros(len(x), bool); keep[0] = keep[-1] = True; st = [(0, len(x) - 1)]
    while st:
        a, b = st.pop()
        if b - a < 2: continue
        dx, dy = x[b] - x[a], y[b] - y[a]; L = np.hypot(dx, dy) or 1.0
        d = np.abs(dy * (x[a + 1:b] - x[a]) - dx * (y[a + 1:b] - y[a])) / L
        k = int(np.argmax(d)) + a + 1
        if d[k - a - 1] > tol: keep[k] = True; st += [(a, k), (k, b)]
    return list(np.nonzero(keep)[0])


S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); P = S['props']
G, C, I = [], [], []
for seg, lo, la in IM.decode_segments(S):
    if len(lo) < 2: continue
    x = np.round(np.asarray(lo) * 1e5).astype(np.int64); y = np.round(np.asarray(la) * 1e5).astype(np.int64)
    k = simplify(x.astype(float), y.astype(float), 7.0); x, y = x[k], y[k]
    g = [int(x[0]), int(y[0])]
    for j in range(1, len(x)): g += [int(x[j] - x[j - 1]), int(y[j] - y[j - 1])]
    G.append(g); C.append(int(P['cls'][seg])); I.append(int(seg))
out = dict(made_by='proto/build_streets_d3.py', enc='lon/lat x 1e5, first point absolute then deltas', c=C, g=G)
p = os.path.join(ROOT, 'docs', 'site', 'data', 'streets_d3.json'); json.dump(out, open(p, 'w'), separators=(',', ':'))
print(len(G), 'lines', os.path.getsize(p) // 1024, 'KB')
