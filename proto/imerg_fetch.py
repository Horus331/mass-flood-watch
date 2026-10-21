"""NASA GPM IMERG half-hourly satellite rainfall (V07, 0.1 deg) for a storm window and box, as an independent check on radar (MRMS).

    EARTHDATA_TOKEN=... python proto/imerg_fetch.py --storm sep2023 --bbox -72.15,42.40,-71.55,42.75 \
        --start 2023-09-11T12:00Z --end 2023-09-13T12:00Z --out docs/proto/obs [--compare docs/proto/leominster_sep2023/flood_meta.json]

Granules found via NASA CMR, downloaded from GES DISC with the Earthdata bearer token (needs the "NASA GESDISC DATA ARCHIVE" app
authorized in the Earthdata profile).  Writes imerg_<storm>.npz (precip mm/h per half hour, lon, lat, times) and imerg_<storm>.json
(box-mean and max storm total, peak 1-h, hourly box-mean series) and, with --compare, the same against the radar totals of a run.
Product order: Final run (research grade, ~3.5 month lag) -> Late -> Early.
"""
import os, sys, io, json, argparse, datetime as dt, time
import numpy as np, requests

CMR = 'https://cmr.earthdata.nasa.gov/search/granules.json'
PRODUCTS = ['GPM_3IMERGHH', 'GPM_3IMERGHHL', 'GPM_3IMERGHHE']

class AuthSession(requests.Session):
    """Keep the bearer header across NASA redirects (requests drops it on a host change)."""
    def rebuild_auth(self, prep, resp):
        h = requests.utils.urlparse(prep.url).hostname or ''
        if not (h.endswith('nasa.gov') or h.endswith('earthdata.nasa.gov')): prep.headers.pop('Authorization', None)

def granules(short, start, end, bbox):
    out, page = [], 1
    while True:
        r = requests.get(CMR, params=dict(short_name=short, version='07', temporal=f'{start},{end}', bounding_box=','.join(map(str, bbox)),
                                          page_size=200, page_num=page), timeout=60)
        r.raise_for_status(); E = r.json()['feed']['entry']
        for e in E:
            L = [l['href'] for l in e.get('links', []) if l['href'].startswith('https') and l['href'].endswith(('.HDF5', '.h5')) and 'opendap' not in l['href']]
            if L: out.append((e['time_start'], L[0]))
        if len(E) < 200: break
        page += 1
    return sorted(set(out))

def read_box(blob, bbox):
    import h5py
    with h5py.File(io.BytesIO(blob), 'r') as f:
        g = f['Grid']; lon = g['lon'][:]; lat = g['lat'][:]
        i = np.nonzero((lon >= bbox[0] - 0.05) & (lon <= bbox[2] + 0.05))[0]; j = np.nonzero((lat >= bbox[1] - 0.05) & (lat <= bbox[3] + 0.05))[0]
        p = g['precipitation'][0, i[0]:i[-1] + 1, j[0]:j[-1] + 1].astype(np.float32)   # (lon, lat) mm/h
    p[p < 0] = np.nan
    return p.T[::-1], lon[i], lat[j][::-1]          # rows north -> south

def main(a):
    tok = os.environ.get('EARTHDATA_TOKEN')
    if not tok: sys.exit('EARTHDATA_TOKEN not set')
    bbox = [float(v) for v in a.bbox.split(',')]
    S = AuthSession(); S.headers['Authorization'] = 'Bearer ' + tok
    for short in PRODUCTS:
        G = granules(short, a.start, a.end, bbox)
        if G: break
    if not G: sys.exit('no IMERG granules found')
    print(short, len(G), 'granules')
    P, T = [], []
    for k, (t, url) in enumerate(G):
        for tries in range(4):
            try:
                r = S.get(url, timeout=180)
                if r.status_code == 200 and r.content[:4] == b'\x89HDF': break
                print('  http', r.status_code, r.headers.get('content-type'), url[-60:]); time.sleep(5 * (tries + 1))
            except Exception as e: print('  err', repr(e)[:120]); time.sleep(5)
        else: sys.exit('download failed (is the GESDISC app authorized in the Earthdata profile?)')
        p, lon, lat = read_box(r.content, bbox); P.append(p); T.append(t[:16] + 'Z')
        if k % 12 == 0: print(' ', t, f'{np.nanmean(p):.2f} mm/h')
    P = np.stack(P); tot = np.nansum(P, axis=0) * 0.5
    hourly = (P[0::2][:len(P) // 2] + P[1::2][:len(P) // 2]) * 0.5          # mm in each hour
    os.makedirs(a.out, exist_ok=True)
    np.savez_compressed(f'{a.out}/imerg_{a.storm}.npz', precip_mmh=P, lon=lon, lat=lat, times=np.array(T))
    s = dict(product=short + ' V07', granules=len(G), start=T[0], end=T[-1], bbox=bbox, grid_deg=0.1,
             total_box_mean_mm=round(float(np.nanmean(tot)), 1), total_max_mm=round(float(np.nanmax(tot)), 1),
             peak1h_max_mm=round(float(np.nanmax(hourly)), 1) if len(hourly) else None,
             hourly_box_mean_mm=[round(float(v), 2) for v in np.nanmean(hourly, axis=(1, 2))])
    if a.compare and os.path.exists(a.compare):
        m = json.load(open(a.compare))
        s['radar_run'] = dict(file=a.compare, total_box_mean_mm=m.get('rain_total_mean_mm'), total_max_mm=m.get('rain_total_max_mm'), t0=m.get('t0'),
                              note='radar box is the run box (EPSG:26986); IMERG box is the --bbox above, so compare means as a sanity check only')
    json.dump(s, open(f'{a.out}/imerg_{a.storm}.json', 'w'), indent=1)
    print(json.dumps({k: v for k, v in s.items() if k != 'hourly_box_mean_mm'}, indent=1))

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--storm', default='sep2023'); ap.add_argument('--bbox', default='-72.15,42.40,-71.55,42.75')
    ap.add_argument('--start', default='2023-09-11T12:00:00Z'); ap.add_argument('--end', default='2023-09-13T12:00:00Z')
    ap.add_argument('--out', default='docs/proto/obs'); ap.add_argument('--compare')
    main(ap.parse_args())
