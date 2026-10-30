"""LOCAL TEST ONLY: fake what-if scenario packs derived from the live baseline pack (never committed)."""
import json, os, sys, numpy as np
from PIL import Image
REPO = os.getcwd(); SCR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, 'proto')); import whatif as W
W.SITE = os.path.join(SCR, 'site_whatif'); os.environ['LF_WORK'] = os.path.join(SCR, 'work')
P = os.path.join(REPO, 'docs/site/data/leominster_sep2023'); meta = json.load(open(P + '/meta.json'))
cls = []
for i, s in enumerate(meta['sheets']):
    a = np.asarray(Image.open(os.path.join(P, s)))
    for j in range(9):
        k = i * 9 + j
        if k < meta['nf'] and k % 3 == 0: cls.append(((a[..., j // 3] // (1, 5, 25)[j % 3]) % 5).astype(np.uint8))
cls = np.stack(cls); print('frames', cls.shape)
CM = np.array([0, 8, 20, 50, 130], np.float32)
mask = (cls[-1] >= 3)
ny, nx = cls.shape[1:]
yy, xx = np.mgrid[0:ny, 0:nx]
z = (120 + 40 * np.sin(xx / 70.0) * np.cos(yy / 90.0) + 25 * np.sin((xx + yy) / 23.0) + 8 * np.cos(xx / 9.0 + yy / 13.0)).astype(np.float32)
SRC = os.path.join(REPO, 'docs/proto/turing/leominster_sep2023_p')
S0 = json.load(open(SRC + '/summary.json')); G = json.load(open(SRC + '/segments.geojson'))
SF = {'dry': 0.75, 'normal': 1.0, 'wet': 1.25, 'frozen': 1.45}; CF = {'open': 1.0, 'blocked': 1.15}
only = sys.argv[1].split(',') if len(sys.argv) > 1 else None
for sc in W.matrix():
    if only and sc['id'] not in only: continue
    f = sc['rain'] * SF[sc['soil']] * CF[sc['culverts']]
    out = W.run_out(sc); rd = os.path.join(SCR, 'results', sc['env']['NAME']); os.makedirs(out, exist_ok=True); os.makedirs(rd, exist_ok=True)
    D = (CM[cls] * f).astype(np.uint16)
    D[:, mask] = (40 + 140 * np.clip(np.sin(np.linspace(0, 3.2, D.shape[0])), 0, 1) * f)[:, None].astype(np.uint16)
    np.savez_compressed(out + '/frames_cm.npz', depth_cm=D, hours=np.arange(D.shape[0]) * 0.25)
    np.save(out + '/watermask.npy', mask.astype(np.uint8)); np.savez_compressed(out + '/z_raw.npz', z_raw=z, z_raw_max10=z); np.save(out + '/z.npy', z)
    S = dict(S0); S['frame_hours'] = [round(i * 0.25, 2) for i in range(D.shape[0])]
    S['rain_hourly_mean_mm'] = [round(v * sc['rain'], 1) for v in S0['rain_hourly_mean_mm']]
    feats = []
    for ft in G['features']:
        q = dict(ft['properties']); d = json.loads(q['d']) if isinstance(q.get('d'), str) else q.get('d') or []
        d = [int(min(255, v * f)) for v in d[::3]]; q['d'] = d
        pk = max(d) if d else 0; q['p_close'] = 1.0 if pk >= 30 else 0.0
        feats.append(dict(type='Feature', properties=q, geometry=ft['geometry']))
    S['segments_p_ge_50'] = sum(1 for x in feats if x['properties']['p_close'] >= 0.5)
    S['culverts_overtopped'] = int(S0['culverts_overtopped'] * f)
    json.dump(S, open(rd + '/summary.json', 'w')); json.dump(dict(type='FeatureCollection', features=feats), open(rd + '/segments.geojson', 'w'))
    import shutil; shutil.copy(SRC + '/map.html', rd + '/map.html')
    C = json.load(open(os.path.join(P, 'cascade.json')))
    C['totals']['peak']['pop_isolated'] = int(C['totals']['peak']['pop_isolated'] * f ** 2)
    C['culverts'] = [dict(c, first_h=c['first_h'] / f) for c in C['culverts'][:int(60 * f)]]
    json.dump(C, open(rd + '/cascade.json', 'w'))
W.pack(os.path.join(SCR, 'results'), only)
