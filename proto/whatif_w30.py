"""Impassable stretches for the Scenarios tab (docs/site/data/whatif): per ~40 m road piece of whatif/pieces.json and per scenario,
the frame intervals with 30 cm or more of modelled water on the piece itself (depth class >= 3 in at least half of the cells under
the piece, mapped rivers and ponds excluded), the same rule as pieces_build w30 in docs/site/build_data.py for the replays.
Written into each scenario's d.json as pw30[segment] = [intervals per piece, in pieces.json order]. Reads only published files.

    python proto/whatif_w30.py
"""
import json, os, sys
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'docs', 'site')); import build_data as BD
from pyproj import Transformer

W = os.path.join(ROOT, 'docs', 'site', 'data', 'whatif')
ix = json.load(open(os.path.join(W, 'index.json'))); P = json.load(open(os.path.join(W, 'pieces.json')))
box = [float(v) for v in ix['box_epsg26986'].split(',')]; RES = 20.0
ter = np.asarray(Image.open(os.path.join(W, ix['terrain']['sheet'])).convert('RGB')); land = ter[..., 1] < 128
shape = land.shape
tf = Transformer.from_crs(4326, 26986, always_xy=True)
samp = []
for line in P['lines']:
    x, y = tf.transform([c[0] for c in line], [c[1] for c in line]); x = np.array(x); y = np.array(y)
    dd = np.r_[0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))]; n = max(2, int(dd[-1] / (RES / 2)))
    t = np.linspace(0, dd[-1], n); sx = np.interp(t, dd, x); sy = np.interp(t, dd, y)
    c = np.clip(((sx - box[0]) // RES).astype(int), 0, shape[1] - 1); r = np.clip(((box[3] - sy) // RES).astype(int), 0, shape[0] - 1)
    samp.append((r, c))
ordk = {}; ordr = []
for s in P['seg']: ordr.append(ordk.get(s, 0)); ordk[s] = ordk.get(s, 0) + 1


def ivs(w):
    iv, st = [], None
    for i, on in enumerate(list(w) + [False]):
        if on and st is None: st = i
        if not on and st is not None: iv.append([st, i - 1]); st = None
    return iv


for key in sorted(ix['scenarios']):
    dp = os.path.join(W, key, 'd.json')
    if not os.path.exists(dp): continue
    dj = json.load(open(dp)); od = os.path.join(W, key)
    meta = dict(sheets=dj['sheets'], nf=int(dj['nf']))
    on = [[] for _ in samp]
    for f in BD.sheet_frames(od, meta):
        m3 = (f >= 3) & land
        for i, (r, c) in enumerate(samp): on[i].append(bool(m3[r, c].mean() >= 0.5))
    out = {}
    for i, s in enumerate(P['seg']):
        iv = ivs(on[i])
        if iv: out.setdefault(str(s), {})[ordr[i]] = iv
    dj['pw30'] = {s: [v.get(k, []) for k in range(ordk[int(s)])] for s, v in out.items()}
    json.dump(dj, open(dp, 'w'), separators=(',', ':'))
    print(key, 'segments with an impassable piece', len(out), 'pieces', sum(len(v) for v in out.values()), flush=True)
