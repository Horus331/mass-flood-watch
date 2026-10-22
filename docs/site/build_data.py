"""Build the web-friendly replay data for the public site (docs/site/data/<run>/).

Reads only committed run outputs under docs/proto/ and writes:
  meta.json   corners, clock, timeline series, headline numbers (copied, not recomputed)
  depth_NN.png  flood-depth classes for 9 frames per image, packed base 5 into RGB
  roads.json  flagged road segments (simplified) with closure intervals and popup facts
Run from the repo root:  python3 docs/site/build_data.py
"""
import json, os, re
import numpy as np
from PIL import Image
from shapely.geometry import shape, mapping
from shapely.ops import linemerge

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'docs', 'proto')
OUT = os.path.join(ROOT, 'docs', 'site', 'data')
RUNS = {  # site key: (source folder, spatial max-pool factor)
    'leominster_sep2023': ('leominster_sep2023', 1),
    'worcester_aug2021': ('worcester_aug2021', 1),
    'd3_sep2023': ('turing/d3_sep2023_20m', 4),
}
# frame colours written by proto/prototype.py (cols at 5 / 15 / 30 / 100 cm)
CLASS_RGB = {(198, 219, 239): 1, (107, 174, 214): 2, (33, 113, 181): 3, (8, 48, 107): 4}
CLS = {'local / collector': 0, 'arterial': 1, 'highway': 2}


def corners(src):
    html = open(os.path.join(P, src, 'map.html')).read()
    return json.loads(re.search(r'C=(\[\[.*?\]\])', html).group(1))


def classes(png, f):
    a = np.asarray(Image.open(png).convert('RGBA'))
    c = np.zeros(a.shape[:2], np.uint8)
    for rgb, k in CLASS_RGB.items():
        c[(a[..., 0] == rgb[0]) & (a[..., 1] == rgb[1]) & (a[..., 2] == rgb[2]) & (a[..., 3] > 0)] = k
    if f > 1:  # keep the deepest class of each block so thin streams stay visible
        h, w = (c.shape[0] // f) * f, (c.shape[1] // f) * f
        c = c[:h, :w].reshape(h // f, f, w // f, f).max(axis=(1, 3))
    return c


def intervals(d):
    """closed stretches (depth >= 30 cm) in fractional frame units"""
    out, start = [], None
    for i, v in enumerate(d):
        if v >= 30 and start is None:
            start = i if i == 0 else i - 1 + (30 - d[i - 1]) / max(v - d[i - 1], 1e-6)
        if v < 30 and start is not None:
            out.append([round(start, 2), round(i - 1 + (d[i - 1] - 30) / max(d[i - 1] - v, 1e-6), 2)])
            start = None
    if start is not None:
        out.append([round(start, 2), len(d) - 1 + 0.5])
    return out


def build(key, src, f):
    od = os.path.join(OUT, key)
    os.makedirs(od, exist_ok=True)
    S = json.load(open(os.path.join(P, src, 'summary.json')))
    nf = len(S['frame_hours'])
    frames = [classes(os.path.join(P, src, 'frames', 'f%03d.png' % i), f) for i in range(nf)]
    h, w = frames[0].shape
    sheets = []
    for s in range(0, nf, 9):
        rgb = np.zeros((h, w, 3), np.uint8)
        for j in range(9):
            if s + j < nf:
                rgb[..., j // 3] += frames[s + j] * (1, 5, 25)[j % 3]
        name = 'depth_%02d.png' % (s // 9)
        Image.fromarray(rgb, 'RGB').save(os.path.join(od, name), optimize=True)
        sheets.append(name)

    risk = {}
    rp = os.path.join(P, src, 'risk_segments.json')
    if os.path.exists(rp):
        risk = json.load(open(rp))['segments']
    g = json.load(open(os.path.join(P, src, 'segments.geojson')))
    feats = []
    for ft in g['features']:
        q = ft['properties']
        d = q.get('d') or []
        iv = intervals(d)
        sid = str(q['segment'])
        e = risk.get(sid, {})
        may = (q.get('p_may_close') or 0) >= 0.5 and q['p_close'] < 0.5
        if not (q['p_close'] >= 0.5 or may or iv or 'r' in e):
            continue
        geom = shape(ft['geometry'])
        if geom.geom_type == 'MultiLineString':
            geom = linemerge(geom)
        geom = geom.simplify(0.00003, preserve_topology=False)
        gm = mapping(geom)

        def rnd(x):
            return [round(x[0], 5), round(x[1], 5)]
        if gm['type'] == 'LineString':
            gm = {'type': 'LineString', 'coordinates': [rnd(c) for c in gm['coordinates']]}
        elif gm['type'] == 'MultiLineString':
            gm = {'type': 'MultiLineString', 'coordinates': [[rnd(c) for c in l] for l in gm['coordinates']]}
        else:
            continue
        pr = {'n': q.get('road') or '', 't': q.get('town') or '', 'c': CLS.get(q.get('road_class'), 0),
              'p': round(q['p_close'], 2), 'm': 1 if may else 0, 'w': q.get('why') or ''}
        if iv:
            pr['iv'] = iv
        a = e.get('a')
        if a and (a.get('h') or a.get('f') or a.get('p')):
            pr['a'] = [a.get('h', 0), a.get('f', 0), a.get('p', 0), a.get('iso', 0)]
        r = e.get('r')
        if r:
            pr['rk'] = r['risk']
            pr['rc'] = [r['repair'][0], r['repair'][1], r.get('delay', 0)]
        feats.append({'type': 'Feature', 'id': int(q['segment']), 'properties': pr, 'geometry': gm})
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(od, 'roads.json'), 'w'),
              separators=(',', ':'))

    keep = ['segments_in_box', 'segments_p_ge_50', 'km_p_ge_50', 'segments_may_close', 'km_may_close',
            'culverts_overtopped', 'crossings_assessed', 'flood_model_runtime_s', 'resolution_m',
            'rain_max_total_mm', 'rain_peak1h_max_mm', 'solver', 'storm_start']
    meta = {k: S[k] for k in keep if k in S}
    meta.update({'key': key, 'source': 'docs/proto/' + src, 'corners': corners(src), 'frame_min': 30, 'nf': nf,
                 'w': w, 'h': h, 'pixel_m': S['resolution_m'] * f, 'sheets': sheets,
                 'rain_hourly_mean_mm': S.get('rain_hourly_mean_mm', []),
                 'closed_per_frame': S.get('closed_per_frame', [])})
    json.dump(meta, open(os.path.join(od, 'meta.json'), 'w'), separators=(',', ':'))
    print(key, 'frames', nf, '%dx%d' % (w, h), 'roads', len(feats))


if __name__ == '__main__':
    for k, (src, f) in RUNS.items():
        build(k, src, f)
