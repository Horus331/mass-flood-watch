"""Real data layers for the site's "How it works" figure (one 20 x 20 km box, the Leominster catalogue box).

    python proto/site_layers.py fetch --surr surr.npz --out drafts/layers/data     # on a GitHub runner (needs the network)

Inputs: the model's own input pack (sim/colab/w9_lisflood.py with LF_SURR_SAVE=1: lidar DEM, curve number, impervious share,
water / channel masks, hourly MRMS rain), plus NLCD 2021 land-cover classes (MRLC WCS) and a USGS NAIP aerial image
(USGS The National Map image service). Writes small files only (float16 / uint8, compressed).
"""
import argparse, io, json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = (162000, 908000, 182000, 928000)     # EPSG:26986, the Leominster catalogue box


def naip(box, px, out):
    import requests
    x0, y0, x1, y1 = box
    for u in ('https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPImagery/ImageServer/exportImage',
              'https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer/exportImage'):
        q = dict(bbox=f'{x0},{y0},{x1},{y1}', bboxSR=26986, imageSR=26986, size=f'{px},{px}', format='jpg', f='image')
        try:
            r = requests.get(u, params=q, timeout=300)
            if r.status_code == 200 and r.content[:3] == b'\xff\xd8\xff':
                open(out, 'wb').write(r.content); return u
            print('naip: bad response', u, r.status_code, r.content[:120])
        except Exception as e:
            print('naip: failed', u, repr(e)[:120])
    return None


def fetch(a):
    sys.path.insert(0, f'{ROOT}/sim/colab')
    import w9_lisflood as W
    os.makedirs(a.out, exist_ok=True)
    S = np.load(a.surr); meta = json.loads(str(S['meta']))
    ny, nx = meta['shape']; box = tuple(meta['box']); res = meta['res_m']
    rain = S['rain'].astype(np.float32)                    # hourly mm, block means of `rain_coarsen` cells
    lc, cov = W.nlcd_landcover(box, res, ny, nx)
    np.savez_compressed(f'{a.out}/layers.npz', z_raw=S['z_raw'].astype(np.float16), z=S['z'].astype(np.float16), cn=S['cn'],
                        imp=S['imp'], mask=S['mask'], rain_total=rain.sum(0).astype(np.float16), rain_hourly_mean=rain.mean(axis=(1, 2)).astype(np.float32),
                        nlcd=(lc if lc is not None else np.zeros((ny, nx), np.uint8)))
    src = naip(box, a.px, f'{a.out}/naip.jpg')
    info = dict(box=list(box), crs='EPSG:26986', res_m=res, shape=[ny, nx], t0=meta['t0'], hours=meta['hours'], rain_src=meta.get('rain_src'),
                rain_coarsen=int(S['rain_coarsen']), nlcd=cov, naip=src, env=meta.get('env'), git_sha=meta.get('git_sha'),
                made_by='proto/site_layers.py fetch')
    json.dump(info, open(f'{a.out}/layers.json', 'w'), indent=1); print(json.dumps(info, indent=1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    f = sp.add_parser('fetch'); f.add_argument('--surr', required=True); f.add_argument('--out', default='drafts/layers/data'); f.add_argument('--px', type=int, default=2000)
    a = ap.parse_args()
    if a.cmd == 'fetch': fetch(a)
