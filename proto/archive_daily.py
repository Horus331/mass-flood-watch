"""Daily archive of District 3 forecast data that the providers delete after a few days (replaces the Colab 'daily saver' that needed
Google Drive). Runs on GitHub Actions (.github/workflows/archive_daily.yml); the Hugging Face dataset is the archive and the state, so a
re-run only adds what is missing.
  ecmwf  ECMWF open data, IFS and AIFS precipitation forecasts (0.25 deg), the two latest 00Z/12Z cycles, cropped to New England
         -> archive/ecmwf/<model>_<YYYYMMDDHH>_tp_NE.nc ; plus the IFS ensemble heavy-rain probabilities -> archive/ecmwf/ifs_ep_<..>.grib2
  nwm    National Water Model short-range streamflow (f001-f018) at the culvert crossings' reaches (docs/proto/live/crossing_comids.json),
         every 00Z/06Z/12Z/18Z cycle of the last 2 days still on AWS -> archive/nwm/<YYYYMMDD>_t<HH>z_short_range_crossings.csv.gz
The MassDOT roadway-events log (events_log.yml) and REFS / SPoRT-LIS (archive_feeds.yml) already run on GitHub; the REFS check of the old
saver is covered there.
"""
import argparse, datetime as dt, gzip, io, json, os, sys, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from archive_feeds import log, hf_ls, hf_put   # same dataset and helpers as the other archive
import live_feeds as LF

NE = dict(lat=(43.5, 41.0), lon=(-74.0, -69.5))


def ecmwf(dry=False):
    from ecmwf.opendata import Client
    import xarray as xr
    have = {os.path.basename(p) for p in hf_ls('archive/ecmwf')}
    put, msgs = {}, []
    tmpd = tempfile.mkdtemp()
    for model, steps in (('ifs', list(range(0, 75, 3))), ('aifs-single', list(range(0, 78, 6)))):
        c = Client(source='aws', model=model)
        try: last = c.latest(type='fc', step=24, param='tp')
        except Exception as e: log(f'{model}: no latest cycle ({repr(e)[:120]})'); continue
        for back in (0, 1):
            d0 = last - dt.timedelta(hours=12 * back)
            name = f'{model}_{d0:%Y%m%d%H}_tp_NE.nc'
            if name in have: log('have', name); continue
            g = os.path.join(tmpd, f'{model}_{d0:%Y%m%d%H}.grib2')
            try:
                c.retrieve(date=d0.strftime('%Y%m%d'), time=d0.hour, type='fc', step=steps, param='tp', target=g)
                ds = xr.open_dataset(g, engine='cfgrib').sel(latitude=slice(*NE['lat']), longitude=slice(*NE['lon']))
                out = os.path.join(tmpd, name); ds.to_netcdf(out); os.remove(g)
                put[f'archive/ecmwf/{name}'] = out; msgs.append(name); log('saved', name, f'{os.path.getsize(out) / 1e6:.2f} MB')
            except Exception as e: log(f'{name}: {repr(e)[:200]}')
    try:   # ensemble heavy-rain probabilities (10/25/50 mm in 24 h), when offered
        c = Client(source='aws', model='ifs'); d0 = c.latest(type='ep', step='0-24', param='tpg25')
        name = f'ifs_ep_{d0:%Y%m%d%H}.grib2'
        if name not in have:
            g = os.path.join(tmpd, name)
            c.retrieve(date=d0.strftime('%Y%m%d'), time=d0.hour, type='ep', step=['0-24', '24-48'], param=['tpg10', 'tpg25', 'tpg50'], target=g)
            put[f'archive/ecmwf/{name}'] = g; msgs.append(name); log('saved', name)
    except Exception as e: log(f'ECMWF probabilities skipped: {repr(e)[:150]}')
    hf_put(put, 'ECMWF open data: ' + ', '.join(msgs), dry=dry)
    return len(put)


def nwm(dry=False, days=2):
    M = json.load(open(LF.COMID_MAP))['map']
    pairs = sorted({int(v['comid']) if isinstance(v, dict) else int(v) for v in M.values() if (v.get('comid') if isinstance(v, dict) else v)})
    comids = np.array(pairs, np.int64)
    have = {os.path.basename(p) for p in hf_ls('archive/nwm')}
    now = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None); put, msgs = {}, []
    for d in range(days, -1, -1):
        for hh in (0, 6, 12, 18):
            c = (now - dt.timedelta(days=d)).replace(hour=hh, minute=0, second=0, microsecond=0)
            if c > now - dt.timedelta(hours=3): continue
            name = f'{c:%Y%m%d}_t{hh:02d}z_short_range_crossings.csv.gz'
            if name in have: continue
            pre = f'nwm.{c:%Y%m%d}/short_range/nwm.t{hh:02d}z.short_range.channel_rt.f'
            K = sorted(k for k in LF.s3_list(LF.NWM_S3, pre) if k.endswith('.conus.nc'))[:18]
            if len(K) < 18: log(f'{name}: only {len(K)} files on AWS, skipped'); continue
            cols, rows = [], []
            try:
                for k in K:
                    raw = LF.http_get(f'{LF.NWM_S3}/{k}', timeout=180, tries=3).content
                    tv, v, _ = LF.nwm_read(raw, comids); cols.append(tv.strftime('%Y-%m-%dT%H:%MZ')); rows.append(v)
            except Exception as e: log(f'{name}: {repr(e)[:200]}'); continue
            Q = np.array(rows).T   # reaches x hours
            buf = io.StringIO(); buf.write('feature_id,' + ','.join(cols) + '\n')
            for fid, r in zip(comids, Q): buf.write(f'{fid},' + ','.join('' if np.isnan(x) else f'{x:.3f}' for x in r) + '\n')
            put[f'archive/nwm/{name}'] = gzip.compress(buf.getvalue().encode()); msgs.append(name); log('saved', name, len(comids), 'reaches')
    hf_put(put, 'NWM short range at the crossings: ' + ', '.join(msgs), dry=dry)
    return len(put)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('what', choices=['ecmwf', 'nwm', 'all'])
    ap.add_argument('--dry', action='store_true'); a = ap.parse_args()
    n = 0
    if a.what in ('ecmwf', 'all'): n += ecmwf(a.dry)
    if a.what in ('nwm', 'all'): n += nwm(a.dry)
    log('files added:', n)


if __name__ == '__main__':
    main()
