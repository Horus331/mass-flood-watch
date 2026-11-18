"""Groundwater scouting, proposal A (docs/proto/groundwater/SCOUT.md §5): how much of the District 3 road network sits on a shallow water
table. Water-table depth = the model's own SSURGO grid soils30 'wtd' (cm, annual minimum, 30 m; same grid the curve number uses).
Reads every road segment every 10 m; a segment's value is its shallowest point. Scouting only, no model change."""
import json, os, sys
import numpy as np
from huggingface_hub import hf_hub_download
from pyproj import Transformer
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, f'{ROOT}/sim/infra')
import impacts as IM
REPO = 'mohabeldokla/mass-flood-watch-tiles'; TOK = os.environ.get('HF_TOKEN') or None
OUT = f'{ROOT}/docs/proto/groundwater'


def main():
    S = json.load(open(f'{ROOT}/docs/graph_segments.json')); n = S['n']
    D = np.load(hf_hub_download(REPO, 'data/soils30/soils30.npz', repo_type='dataset', token=TOK))
    M = json.load(open(hf_hub_download(REPO, 'data/soils30/soils30_meta.json', repo_type='dataset', token=TOK)))
    W = D['wtd']; sx0, sy0, sx1, sy1 = M['box']; res = M['res_m']; print('soils30', M.get('crs'), W.shape, W.dtype, 'wtd quantiles', np.percentile(W[W > 0], [1, 10, 50, 90]))
    tr = Transformer.from_crs(4326, 26986, always_xy=True)
    parts = [(i, *tr.transform(lo, la)) for i, lo, la in IM.decode_segments(S)]
    x, y, seg = IM.densify(parts, 10.0)[:3]
    r = np.clip(((sy1 - y) / res).astype(int), 0, W.shape[0] - 1); c = np.clip(((x - sx0) / res).astype(int), 0, W.shape[1] - 1)
    w = W[r, c].astype(float); w[w <= 0] = np.nan                        # 0 = no data
    seg_min = np.full(n, np.nan)
    np.fmin.at(seg_min, seg, w)
    length = np.zeros(n); np.add.at(length, seg, 10.0)
    P = S['props']; towns = P.get('town', [''] * n); cls = P.get('cls', P.get('class', [''] * n))
    out = dict(source='SSURGO via soils30 wtd (cm), road points every 10 m', n_segments=n, km_total=round(length.sum() / 1000, 1))
    for lim in (25, 50, 100):
        m = seg_min <= lim
        out[f'within_{lim}cm'] = dict(segments=int(m.sum()), km=round(length[m].sum() / 1000, 1), share_segments=round(float(m.mean()), 3),
                                       road_km_on_it=round(float(np.nansum(w <= lim)) * 10 / 1000, 1), share_of_road_length=round(float(np.nansum(w <= lim)) / len(w), 3))
        if lim == 50:
            from collections import Counter
            out['towns_within_50cm'] = Counter(towns[i] for i in np.where(m)[0]).most_common(15)
            out['class_within_50cm'] = Counter(str(cls[i]) for i in np.where(m)[0]).most_common(8)
    out['no_data_segments'] = int(np.isnan(seg_min).sum())
    # nearest USGS well (scout.json) for the shallow segments
    sc = json.load(open(f'{OUT}/scout.json'))['wells']; wx, wy = tr.transform([s['lon'] for s in sc], [s['lat'] for s in sc])
    cnt = np.bincount(seg, minlength=n); mx = np.bincount(seg, x, minlength=n) / np.maximum(cnt, 1); my = np.bincount(seg, y, minlength=n) / np.maximum(cnt, 1)
    sh = np.where(seg_min <= 50)[0]; mids = np.c_[mx[sh], my[sh]]
    if len(mids):
        dist = np.min(np.hypot(mids[:, :1] - np.array(wx)[None], mids[:, 1:] - np.array(wy)[None]), axis=1) / 1000
        out['nearest_well_km_shallow_segments'] = dict(median=round(float(np.nanmedian(dist)), 1), within_5km=int((dist <= 5).sum()))
    json.dump(dict(out, seg_wtd_min_cm=[None if np.isnan(v) else int(v) for v in seg_min]), open(f'{OUT}/roads_wtd.json', 'w'))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
