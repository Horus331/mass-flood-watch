"""The model's own road network for each replay box (docs/site/data/<run>/network.json), run from the repo root:
    python3 proto/build_network.py
Every District 3 road segment the model evaluates (docs/graph_segments.json, MassDOT road inventory) inside the run's box, in a compact delta encoding (decoded in viewer.js):
the street layout stays visible at every zoom (the basemap tiles drop minor streets below z13), and the road panel gets length and AADT.
properties: i segment id, c class (0 local/collector, 1 arterial, 2 highway), a AADT (veh/day), l length (m)."""
import json, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
import impacts as IM
S = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json'))); P = S['props']
for run in sys.argv[1:] or ['leominster_sep2023', 'worcester_aug2021']:
    d = os.path.join(ROOT, 'docs', 'site', 'data', run); m = json.load(open(os.path.join(d, 'meta.json')))
    C = np.array(m['corners']); lo0, lo1, la0, la1 = C[:, 0].min(), C[:, 0].max(), C[:, 1].min(), C[:, 1].max()
    I, Cc, A, L, G = [], [], [], [], []
    for seg, lo, la in IM.decode_segments(S):
        if lo.max() < lo0 or lo.min() > lo1 or la.max() < la0 or la.min() > la1 or len(lo) < 2: continue
        x = np.round(np.asarray(lo) * 1e5).astype(np.int64); y = np.round(np.asarray(la) * 1e5).astype(np.int64)
        g = [int(x[0]), int(y[0])]
        for k in range(1, len(x)): g += [int(x[k] - x[k - 1]), int(y[k] - y[k - 1])]
        I.append(int(seg)); Cc.append(int(P['cls'][seg])); A.append(int(P['aadt'][seg] or 0)); L.append(int(P['len'][seg] or 0)); G.append(g)
    out = dict(made_by='proto/build_network.py', enc='lon/lat x 1e5, first point absolute then deltas', id=I, c=Cc, aadt=A, len_m=L, g=G)
    p = os.path.join(d, 'network.json'); json.dump(out, open(p, 'w'), separators=(',', ':'))
    print(run, len(I), 'segments', os.path.getsize(p) // 1024, 'KB')
