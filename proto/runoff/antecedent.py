"""Antecedent wetness per catalogue storm (ROADMAP_research.md T4; docs/proto/runoff/AMC.md).

    python proto/runoff/antecedent.py [--storms jul2021,sep2021] [--skip-nwm] [--skip-mrms] [--all-eras] [--out antecedent]
        -> docs/proto/runoff/<out>.json + <out>.csv  (--all-eras: include the IEM-era catalogue storms, e.g. for the NEW16 OOS check)

Per storm (docs/proto/obs/catalog.json, the AWS-era events, catalogue box and t0):
  * P5 / P10: box-mean MRMS MultiSensor QPE 24H Pass2 rain over the 5 and 10 days before t0 (sim/colab/lf_antecedent.py, the same
    code LF_CN_AMC=auto runs), and the NEH-4 growing-season AMC class from P5 (< 35 mm I, 35-53 mm II, > 53 mm III).
  * NWM v3 operational analysis (analysis_assim, land, tm00) at the hour t0: box mean of SOILSAT_TOP (saturation of the top soil
    layers, 0-1) and of SOIL_M per layer, from the public NWM archive (Google Cloud, then AWS noaa-nwm-pds).  Diagnostic only:
    the AMC rule uses P5.
Needs network (run on GitHub Actions, .github/workflows/runoff.yml mode=ante).
"""
import os, sys, json, argparse, io, time
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'sim', 'colab'))
import lf_antecedent  # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'proto', 'runoff')
NWM_URLS = ['https://storage.googleapis.com/national-water-model/nwm.{ymd}/analysis_assim/nwm.t{hh}z.analysis_assim.land.tm00.conus.nc',
            'https://noaa-nwm-pds.s3.amazonaws.com/nwm.{ymd}/analysis_assim/nwm.t{hh}z.analysis_assim.land.tm00.conus.nc']
NWM_LCC = '+proj=lcc +lat_1=30 +lat_2=60 +lat_0=40 +lon_0=-97 +x_0=0 +y_0=0 +a=6370000 +b=6370000 +units=m +no_defs'


def box_lonlat(box):
    from pyproj import Transformer
    tr = Transformer.from_crs('EPSG:26986', 'EPSG:4326', always_xy=True)
    x0, y0, x1, y1 = box; xs = np.linspace(x0, x1, 21); ys = np.linspace(y0, y1, 21); X, Y = np.meshgrid(xs, ys)
    lo, la = tr.transform(X.ravel(), Y.ravel()); return (float(min(la)), float(max(la))), (float(min(lo)), float(max(lo))), (X.ravel(), Y.ravel())


def nwm_land(t0, box_xy):
    import requests, netCDF4
    from pyproj import Transformer
    import pandas as pd
    t = pd.Timestamp(t0); ymd = f'{t:%Y%m%d}'; hh = f'{t:%H}'
    for u in NWM_URLS:
        url = u.format(ymd=ymd, hh=hh)
        for k in range(3):
            try:
                r = requests.get(url, timeout=300)
                if r.status_code == 200: break
                if r.status_code == 404: r = None; break
            except Exception as e:
                r = None; print('  nwm', url[-70:], repr(e)[:80]); time.sleep(5)
        if r is None or r.status_code != 200: print('  nwm missing', url); continue
        ds = netCDF4.Dataset('mem.nc', memory=r.content); names = list(ds.variables)
        x = ds['x'][:].astype(np.float64); y = ds['y'][:].astype(np.float64)
        tr = Transformer.from_crs('EPSG:26986', NWM_LCC, always_xy=True); bx, by = tr.transform(*box_xy)
        ix = np.where((x >= min(bx)) & (x <= max(bx)))[0]; iy = np.where((y >= min(by)) & (y <= max(by)))[0]
        res = dict(url=url, variables=names, n_cells=int(len(ix) * len(iy)))
        for v in ('SOILSAT_TOP', 'SOIL_M', 'SOIL_W', 'SOILSAT'):
            if v not in ds.variables: continue
            V = ds[v]; dims = V.dimensions; sl = []
            for d in dims:
                sl.append(slice(iy[0], iy[-1] + 1) if d == 'y' else slice(ix[0], ix[-1] + 1) if d == 'x' else slice(None))
            a = np.ma.filled(V[tuple(sl)].astype(np.float64), np.nan); a[(a < -1) | (a > 1e5)] = np.nan
            sc = 1.0
            # per layer when there is a soil-layer dimension
            ld = [i for i, d in enumerate(dims) if d not in ('time', 'x', 'y')]
            if ld:
                a2 = np.moveaxis(a, ld[0], 0).reshape(a.shape[ld[0]], -1); res[v] = [round(float(np.nanmean(r_) * sc), 4) for r_ in a2]
            else: res[v] = round(float(np.nanmean(a) * sc), 4)
        ds.close(); return res
    return None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--storms', default=''); ap.add_argument('--skip-nwm', action='store_true')
    ap.add_argument('--skip-mrms', action='store_true'); ap.add_argument('--all-eras', action='store_true')
    ap.add_argument('--out', default='antecedent', help='output basename in docs/proto/runoff/ (default antecedent; e.g. antecedent_new16)'); a = ap.parse_args()
    cat = json.load(open(os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog.json')))
    ev = [e for e in cat['events'] if (a.all_eras or e.get('era') == 'aws') and e.get('selected')]
    if a.storms: ev = [e for e in ev if e['id'] in a.storms.split(',')]
    rows = []
    for e in ev:
        print(e['id'], e['t0'], e['box_26986'], flush=True)
        lat_r, lon_r, bxy = box_lonlat(e['box_26986'])
        r = dict(storm=e['id'], t0=e['t0'], box=e['box_26986'], month=int(e['t0'][5:7]))
        try:
            if a.skip_mrms: raise RuntimeError('skipped (--skip-mrms)')
            p10 = lf_antecedent.antecedent(e['t0'], lat_r, lon_r, days=10)
            r.update(p5_mm=round(sum(p10['per_day_mm'][:5]), 1), p10_mm=round(p10['p_mm'], 1), per_day_mm=[round(v, 1) for v in p10['per_day_mm']],
                     sources=p10['sources'], n_pixels=p10['n_pixels'])
            r['amc'] = lf_antecedent.amc_class(r['p5_mm'])
            p5 = lf_antecedent.antecedent(e['t0'], lat_r, lon_r, days=5, log=lambda *x: None)   # pixel range of the 5-day sum
            r.update(p5_max_mm=round(p5['p_max_mm'], 1), p5_min_mm=round(p5['p_min_mm'], 1))
        except Exception as ex:
            r['error'] = repr(ex)[:200]; print('  MRMS failed', ex)
        if not a.skip_nwm:
            try: r['nwm'] = nwm_land(e['t0'], bxy)
            except Exception as ex: r['nwm'] = dict(error=repr(ex)[:200]); print('  NWM failed', ex)
        print('  ', {k: v for k, v in r.items() if k not in ('box', 'per_day_mm', 'sources')}, flush=True); rows.append(r)
    os.makedirs(OUT, exist_ok=True)
    res = dict(made_by='proto/runoff/antecedent.py', thresholds_mm=dict(amc_I_below=lf_antecedent.THRESH_MM[0], amc_III_above=lf_antecedent.THRESH_MM[1],
               source='NEH-4 growing season, 1.4 / 2.1 in. 5-day antecedent rain'),
               p_source='MRMS MultiSensor QPE 24H Pass2 (AWS noaa-mrms-pds), 24 h grids valid at t0 - 24 k h, box mean of native 0.01 deg pixels',
               nwm_source='NWM operational analysis_assim land tm00 at t0 (national-water-model GCS / noaa-nwm-pds); box mean of 1 km cells', storms=rows)
    json.dump(res, open(os.path.join(OUT, a.out + '.json'), 'w'), indent=1)
    with open(os.path.join(OUT, a.out + '.csv'), 'w') as f:
        f.write('storm,t0,p5_mm,p10_mm,p5_min_mm,p5_max_mm,amc,nwm_soilsat_top,nwm_soil_m_layer1\n')
        for r in rows:
            n = r.get('nwm') or {}; sm = n.get('SOIL_M'); sm1 = sm[0] if isinstance(sm, list) else sm
            f.write(f"{r['storm']},{r['t0']},{r.get('p5_mm', '')},{r.get('p10_mm', '')},{r.get('p5_min_mm', '')},{r.get('p5_max_mm', '')},{r.get('amc', '')},"
                    f"{n.get('SOILSAT_TOP', '')},{'' if sm1 is None else sm1}\n")
    print(open(os.path.join(OUT, a.out + '.csv')).read())


if __name__ == '__main__':
    main()
