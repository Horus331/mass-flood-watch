"""Dams in Massachusetts from the USACE National Inventory of Dams (NID, https://nid.sec.usace.army.mil), free, no key.
Writes docs/network/dams_ma.json: columns/rows like crossings_all.json, one row per dam with location, heights (ft), storages (acre-ft),
surface area (acres), drainage area (mi2), spillway type / width (ft), purposes, hazard class.  Also docs/network/dams_ma_fetch_log.json
(which endpoint answered, which source column fed each field) so a run in Actions can be checked without its log.  Run by dams.yml.
"""
import csv, io, json, os, re, time, requests

os.makedirs('docs/network', exist_ok=True)
LOG = dict(started=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), tries=[])
H = {'User-Agent': 'mass-flood-watch research (dams for flood model)'}
URLS = ['https://nid.sec.usace.army.mil/api/nation/csv',
        'https://nid.sec.usace.army.mil/api/states/MA/csv',
        'https://nid.sec.usace.army.mil/api/nation/csv?state=MA']


def fetch():
    for u in URLS:
        try:
            r = requests.get(u, timeout=600, headers=H)
            LOG['tries'].append(dict(url=u, status=r.status_code, bytes=len(r.content), ctype=r.headers.get('content-type'), head=r.text[:300]))
            if r.status_code == 200 and len(r.content) > 10000: return u, r.content.decode('utf-8-sig', errors='replace')
        except Exception as e:
            LOG['tries'].append(dict(url=u, error=repr(e)[:300]))
    return None, None


# field -> regexes tried in order against the header (case-insensitive); the first header that matches is used
FIELDS = dict(name=[r'^dam name$', r'dam.?name'], nid=[r'^nid id$', r'nidid', r'nid.?id'], lat=[r'^latitude$', r'lat'], lon=[r'^longitude$', r'lon'],
              state=[r'^state$', r'^state.?name'], county=[r'county'], river=[r'river'], owner_type=[r'primary owner type', r'owner.?type'],
              purposes=[r'^purposes?$', r'purpose'], year=[r'year completed$', r'year.?completed'], dam_type=[r'^primary dam type$', r'dam.?type'],
              nid_height_ft=[r'^nid height', r'nid.?height'], dam_height_ft=[r'^dam height', r'dam.?height'], hydraulic_height_ft=[r'hydraulic height'],
              structural_height_ft=[r'structural height'], dam_length_ft=[r'^dam length', r'dam.?length'],
              nid_storage_acft=[r'^nid storage', r'nid.?storage'], max_storage_acft=[r'^max(imum)? storage', r'max.?storage'],
              normal_storage_acft=[r'^normal storage', r'normal.?storage'], surface_area_acres=[r'surface area'], drainage_area_mi2=[r'drainage area'],
              spillway_type=[r'^spillway type', r'spillway.?type'], spillway_width_ft=[r'^spillway width', r'spillway.?width'],
              max_discharge_cfs=[r'max(imum)? discharge'], outlet_gates=[r'outlet gate'], hazard=[r'hazard potential', r'hazard'],
              condition=[r'condition assessment$', r'condition'])
NUM = {k for k in FIELDS if k.endswith(('_ft', '_acft', '_acres', '_mi2', '_cfs')) or k in ('lat', 'lon', 'year')}


def main():
    url, txt = fetch()
    if not txt:
        LOG['result'] = 'no endpoint answered'; json.dump(LOG, open('docs/network/dams_ma_fetch_log.json', 'w'), indent=1); raise SystemExit('NID not reachable')
    LOG['text_head'] = txt[:1500]; lines = txt.splitlines(); LOG['n_lines'] = len(lines)
    hi = next(i for i, l in enumerate(lines[:50]) if re.search(r'latitude', l, re.I))     # the export starts with a 'last updated' line
    rd = csv.reader(io.StringIO('\n'.join(lines[hi:]))); hdr = next(rd)
    col = {}
    for f, pats in FIELDS.items():
        for p in pats:
            m = [i for i, h in enumerate(hdr) if re.search(p, h.strip(), re.I)]
            if m: col[f] = m[0]; break
    LOG.update(url=url, header=hdr, columns_used={f: hdr[i] for f, i in col.items()})
    rows = []; cols = list(FIELDS)
    for r in rd:
        if len(r) < len(hdr) // 2: continue
        g = lambda f: r[col[f]].strip() if f in col and col[f] < len(r) else ''
        st = g('state')
        try: lat, lon = float(g('lat')), float(g('lon'))
        except ValueError: continue
        if not (st.upper() in ('MA', 'MASSACHUSETTS') or (not st and 41.2 < lat < 42.9 and -73.6 < lon < -69.9)): continue
        if not (41.0 < lat < 43.1 and -73.7 < lon < -69.8): continue
        out = []
        for f in cols:
            v = g(f)
            if f in NUM:
                try: v = round(float(v.replace(',', '')), 5 if f in ('lat', 'lon') else 2)
                except ValueError: v = None
            out.append(v if v != '' else None)
        rows.append(out)
    fill = {f: sum(1 for x in rows if x[cols.index(f)] is not None) for f in cols}
    LOG.update(result='ok', n=len(rows), filled=fill)
    json.dump(dict(source='USACE National Inventory of Dams (nid.sec.usace.army.mil), Massachusetts', url=url, fetched=time.strftime('%Y-%m-%d'),
                   units='heights/lengths/widths ft, storage acre-ft, surface area acres, drainage area mi2, discharge cfs (NID units)',
                   n=len(rows), columns=cols, rows=rows), open('docs/network/dams_ma.json', 'w'), separators=(',', ':'))
    json.dump(LOG, open('docs/network/dams_ma_fetch_log.json', 'w'), indent=1)
    print(len(rows), 'MA dams;', 'spillway width given for', fill.get('spillway_width_ft'), '; surface area for', fill.get('surface_area_acres'))


if __name__ == '__main__':
    try: main()
    except BaseException as e:
        import traceback; LOG['error'] = traceback.format_exc()[-3000:]
        json.dump(LOG, open('docs/network/dams_ma_fetch_log.json', 'w'), indent=1); raise
