"""Self-hosted aerial tiles for the map (map speed plan, Mo approved 24 Nov 2026).

Copies the MassGIS 2023 statewide orthoimagery (public, no restrictions; acknowledgement requested) for the District 3 box, zoom 8-16,
from the MassGIS tile service into plain {z}/{x}/{y}.webp files, so the map's aerial loads from the same fast static host as the rest
of the site instead of the slow ArcGIS server at every zoom. Above zoom 16 the map still asks MassGIS directly (sharper detail).

    python proto/tiles/aerial_tiles.py OUTDIR [--zmax 16] [--workers 12]
"""
import argparse, io, math, os, sys, time, json, concurrent.futures as cf
import urllib.request
from PIL import Image

BOX = (-72.14721, 42.00805, -71.30292, 42.71323)   # District 3 forecast area (docs/site/data/coverage.json, feature 'forecast')
URL = 'https://tiles.arcgis.com/tiles/hGdibHYSPO59RG1h/arcgis/rest/services/orthos2023/MapServer/tile/{z}/{y}/{x}'
UA = {'User-Agent': 'mass-flood-watch research map (WPI); one-time tile copy for the District 3 site'}


def tiles(z):
    w, s, e, n = BOX
    def t(lon, lat):
        x = (lon + 180) / 360 * 2 ** z
        y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * 2 ** z
        return int(x), int(y)
    x0, y0 = t(w, n); x1, y1 = t(e, s)
    return [(z, x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]


def get(zxy, out, q):
    z, x, y = zxy; p = f'{out}/{z}/{x}/{y}.webp'
    if os.path.exists(p): return 'skip', 0
    for a in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request(URL.format(z=z, x=x, y=y), headers=UA), timeout=30)
            b = r.read()
            im = Image.open(io.BytesIO(b)).convert('RGB')
            if im.getextrema() in (((0, 0),) * 3, ((255, 255),) * 3): return 'blank', 0
            os.makedirs(os.path.dirname(p), exist_ok=True)
            im.save(p, 'WEBP', quality=q, method=4)
            return 'ok', os.path.getsize(p)
        except urllib.error.HTTPError as e:
            if e.code in (404, 400): return 'missing', 0
            time.sleep(2 * (a + 1))
        except Exception:
            time.sleep(2 * (a + 1))
    return 'fail', 0


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('out'); ap.add_argument('--zmin', type=int, default=8)
    ap.add_argument('--zmax', type=int, default=16); ap.add_argument('--workers', type=int, default=12); ap.add_argument('--q', type=int, default=72)
    A = ap.parse_args()
    todo = [t for z in range(A.zmin, A.zmax + 1) for t in tiles(z)]
    print(len(todo), 'tiles', flush=True)
    st = {}; size = 0; t0 = time.time()
    with cf.ThreadPoolExecutor(A.workers) as ex:
        for i, (s, b) in enumerate(ex.map(lambda t: get(t, A.out, A.q), todo)):
            st[s] = st.get(s, 0) + 1; size += b
            if i % 2000 == 0: print(i, st, round(size / 1e6, 1), 'MB', round(time.time() - t0), 's', flush=True)
    json.dump({'box': BOX, 'zmin': A.zmin, 'zmax': A.zmax, 'counts': st, 'MB': round(size / 1e6, 1), 'source': URL,
               'credit': 'MassGIS 2023 orthoimagery'}, open(f'{A.out}/meta.json', 'w'), indent=1)
    print('done', st, round(size / 1e6, 1), 'MB'); sys.exit(1 if st.get('fail', 0) > 0.01 * len(todo) else 0)
