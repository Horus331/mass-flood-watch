"""Evidence layer for a replay pack (docs/site/data/<run>/evidence.json): resident flood reports from the MRPC / BSC Leominster
crowdsource map (proto/data/crowd_sep2023.csv, docs/proto/obs/CROWD.md) checked against the pack's modelled water, plus the honest
headline numbers the viewer quotes (docs/proto/STATUS.md section 2, docs/proto/obs/CROWD.md).

    python3 docs/site/build_evidence.py leominster_sep2023

A point counts as 'water modelled' when the replay has 30 cm or more of water on land within RADIUS_M of the pin at any time (the
depth sheets, 20 m cells; permanent water and channels are not in the sheets). Pins are approximate (placed by residents), and this is a
point check, not the segment scoring of proto/score_v2.py; the scored numbers are quoted from CROWD.md.
"""
import csv
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RADIUS_M = 50.0


def max_class(od, meta):
    mx = None
    for i, s in enumerate(meta['sheets']):
        a = np.asarray(Image.open(os.path.join(od, s)))
        for j in range(9):
            if i * 9 + j >= meta['nf']: break
            c = (a[..., j // 3] // (1, 5, 25)[j % 3]) % 5
            mx = c.astype(np.uint8) if mx is None else np.maximum(mx, c.astype(np.uint8))
    return mx


def main(key):
    od = os.path.join(ROOT, 'docs', 'site', 'data', key); meta = json.load(open(os.path.join(od, 'meta.json')))
    M = max_class(od, meta); h, w = M.shape
    (lon0, lat0), (lon1, _), _, (_, lat3) = meta['corners']     # TL, TR, BR, BL (a near-rectangle at this size)
    rpx = int(np.ceil(RADIUS_M / meta['pixel_m']))
    pts = []
    for r in csv.DictReader(open(os.path.join(ROOT, 'proto', 'data', 'crowd_sep2023.csv'))):
        lon, lat = float(r['lon']), float(r['lat'])
        x = (lon - lon0) / (lon1 - lon0) * w; y = (lat0 - lat) / (lat0 - lat3) * h
        if not (0 <= x < w and 0 <= y < h): continue
        xi, yi = int(x), int(y)
        c = int(M[max(0, yi - rpx):yi + rpx + 1, max(0, xi - rpx):xi + rpx + 1].max())
        pts.append([round(lon, 5), round(lat, 5), r['type'], r['quote'][:160], r['road'] or '', r['town'], c])
    n30 = sum(1 for p in pts if p[6] >= 3)
    out = dict(made_by='docs/site/build_evidence.py', radius_m=RADIUS_M,
               crowd=dict(columns=['lon', 'lat', 'type', 'text', 'road', 'town', 'max_class (0 dry, 1 5 cm, 2 15 cm, 3 30 cm, 4 100 cm+)'], rows=pts,
                          source='MRPC / BSC Group Leominster crowdsource map, 70 road-related resident pins (docs/proto/obs/CROWD.md)',
                          water30=n30),
               numbers=dict(
                   heldout=dict(text='Across 23 storms the model was never tuned on, the closure rule catches 9 of 98 documented flood sites (6.4 times chance); ranking the riskiest 3 % of roads catches 20 of 98 (20 %, 3.1 times chance).',
                                src='docs/proto/STATUS.md section 2; docs/proto/obs/LABELS_ROUND2.md section 4'),
                   tuned=dict(text='This storm is the one the settings were checked against, so it is not a fair test: here the closure rule catches 35 of 89 documented '
                              'closure and damage sites while flagging 1.97 % of road segments (12.8 times random), and 6 of the 27 new sites on the residents’ map '
                              '(22 %), which were never used to build it.',
                              src='docs/proto/parity/BASELINE.md, docs/proto/obs/CROWD.md')))
    json.dump(out, open(os.path.join(od, 'evidence.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
    print(key, len(pts), 'crowd pins,', n30, 'with >= 30 cm modelled within', RADIUS_M, 'm')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'leominster_sep2023')
