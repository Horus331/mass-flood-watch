"""Archive USGS annual peak flows and stage-discharge ratings for Massachusetts (+ boundary) gauges while the legacy NWIS
endpoints still answer.  USGS retires /peaks, /ratings and all WaterServices URLs Nov 2026 - Q1 2027 and has not announced a
replacement for peaks or ratings (docs/research/data_sources.md section 0), so we keep our own copy.

    python tools/usgs_legacy_archive.py --out archive/usgs_legacy

Writes (all gzip RDB exactly as served, public domain):
  sites_ma_expanded.rdb.gz      every MA stream site (siteOutput=expanded: datum, vertical datum, drainage area, HUC)
  peaks/peaks_<site>.rdb.gz     annual peak discharge + gage height (water-year peaks, incl. historic/indirect, with qualifiers)
  ratings/<site>.exsa.rdb.gz    expanded shift-adjusted rating table (stage -> Q at 0.01 ft) in use at fetch time
  ratings/<site>.base.rdb.gz    base rating (breakpoints), smaller, for checking the curve shape
  manifest.json                 what was asked, what came back (bytes, http code), fetch time
Runs in GitHub Actions (the agent sandbox cannot reach USGS).
"""
import os, io, gzip, json, time, argparse, requests
UA = {'User-Agent': 'mass-flood-watch research archive (github.com/Horus331/mass-flood-watch)'}
WS = 'https://waterservices.usgs.gov/nwis/site/'
PEAK = ['https://nwis.waterdata.usgs.gov/nwis/peak', 'https://nwis.waterdata.usgs.gov/ma/nwis/peak']
RAT = ['https://nwis.waterdata.usgs.gov/nwisweb/get_ratings', 'https://waterdata.usgs.gov/nwisweb/get_ratings']
# gauges outside MA that the engine uses as inflow (sim/gauges_fetch.py BOUNDARY) and the NH/VT gauges on rivers entering MA
EXTRA = ['01154500', '01156000', '01161000', '01092000', '01094000', '01096500', '01168500', '01170000', '01333000', '01197500']
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)

def get(urls, params, tries=3):
    for k in range(tries):
        for u in (urls if isinstance(urls, list) else [urls]):
            try:
                r = requests.get(u, params=params, headers=UA, timeout=180)
                if r.status_code == 200 and r.text.strip(): return r, u
                if r.status_code == 404: continue
                log('  http', r.status_code, u, str(params)[:80])
            except Exception as e: log('  err', u, repr(e)[:100])
        time.sleep(5 * (k + 1))
    return None, None

def rdb_rows(text):
    L = [l for l in text.splitlines() if l and not l.startswith('#')]
    if len(L) < 3: return []
    H = L[0].split('\t'); return [dict(zip(H, l.split('\t'))) for l in L[2:]]

def save(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, 'wt', compresslevel=9) as f: f.write(text)
    return os.path.getsize(path)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default='archive/usgs_legacy'); ap.add_argument('--max-ratings', type=int, default=400); a = ap.parse_args()
    M = dict(fetched=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), note='legacy NWIS copies; see tools/usgs_legacy_archive.py', sites={}, peaks={}, ratings={})
    # 1. site lists
    r, _ = get(WS, dict(format='rdb', stateCd='ma', siteType='ST', siteStatus='all', siteOutput='expanded'))
    allsites = rdb_rows(r.text) if r else []
    if r: M['sites']['ma_stream_sites'] = dict(n=len(allsites), bytes=save(f'{a.out}/sites_ma_expanded.rdb.gz', r.text))
    r, _ = get(WS, dict(format='rdb', stateCd='ma', siteType='ST', siteStatus='all', hasDataTypeCd='pk'))
    pk_sites = sorted({x['site_no'] for x in rdb_rows(r.text)}) if r else []
    r, _ = get(WS, dict(format='rdb', stateCd='ma', siteType='ST', siteStatus='active', hasDataTypeCd='iv', parameterCd='00060'))
    q_sites = sorted({x['site_no'] for x in rdb_rows(r.text)}) if r else []
    log('MA stream sites', len(allsites), 'with peaks', len(pk_sites), 'active IV discharge', len(q_sites))
    if not pk_sites: pk_sites = sorted({x['site_no'] for x in allsites})        # hasDataTypeCd=pk refused: try every stream site
    pk_sites = sorted(set(pk_sites) | set(EXTRA)); q_sites = sorted(set(q_sites) | set(EXTRA))
    M['sites'].update(peak_sites=len(pk_sites), rating_sites=len(q_sites))
    # 2. peaks, one file per site
    for i, s in enumerate(pk_sites):
        r, u = get(PEAK, dict(site_no=s, agency_cd='USGS', format='rdb'), tries=2)
        rows = rdb_rows(r.text) if r else []
        if rows: M['peaks'][s] = dict(n=len(rows), bytes=save(f'{a.out}/peaks/peaks_{s}.rdb.gz', r.text), first=rows[0].get('peak_dt'), last=rows[-1].get('peak_dt'))
        else: M['peaks'][s] = dict(n=0)
        if i % 50 == 0: log('peaks', i, '/', len(pk_sites), s, M['peaks'][s])
        time.sleep(0.3)
    # 3. ratings for active discharge gauges
    for i, s in enumerate(q_sites[:a.max_ratings]):
        M['ratings'][s] = {}
        for ft in ('exsa', 'base'):
            r, u = get(RAT, dict(site_no=s, file_type=ft), tries=2)
            ok = r is not None and '\t' in r.text and len(rdb_rows(r.text)) > 0
            M['ratings'][s][ft] = dict(bytes=save(f'{a.out}/ratings/{s}.{ft}.rdb.gz', r.text), rows=len(rdb_rows(r.text))) if ok else None
            time.sleep(0.3)
        if i % 25 == 0: log('ratings', i, '/', len(q_sites), s, M['ratings'][s])
    M['summary'] = dict(peak_files=sum(1 for v in M['peaks'].values() if v.get('n')), rating_exsa=sum(1 for v in M['ratings'].values() if v.get('exsa')),
                        rating_base=sum(1 for v in M['ratings'].values() if v.get('base')),
                        total_mb=round(sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(a.out) for f in fs) / 1e6, 2) if os.path.isdir(a.out) else 0)
    os.makedirs(a.out, exist_ok=True); json.dump(M, open(f'{a.out}/manifest.json', 'w'), indent=1); log('summary', M['summary'])
