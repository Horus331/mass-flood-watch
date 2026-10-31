"""Compact MassDOT inlet / conveyance tables for the LF_INLETS sink (sim/colab/lf_inlets.py; docs/proto/drains/INLETS_PREREG.md).

    python proto/inlets_table.py fetch [--date 2026-10-29]     # Actions (HF reachable): HF snapshot -> proto/data/inlets/*.csv.gz + inventory.json
    python proto/inlets_table.py selftest

Source: the MassDOT Stormwater Asset Database snapshot of 2026-10-29 on HF (`mohabeldokla/mass-flood-watch-tiles`,
`massdot_stormwater/<date>/`, docs/proto/stormwater/SNAPSHOT.md; public domain per the layers' copyrightText). MassDOT-owned assets only.
Kept: every Inlet point with District 3 OR inside any storm-catalogue box (docs/proto/parity/catalog/*/config.json, the drains box) + 2 km;
every Conveyance polyline that touches one of those boxes (+ 2 km) (Conveyance has almost no District values, SNAPSHOT.md).
Written (small, offline-readable on Turing and Actions; no network needed at run time):
  proto/data/inlets/massdot_inlets.csv.gz       lon, lat (EPSG:4326, 6 dp), type (InletType as published, decoded through the layer's coded
                                                 domain when there is one), cover (CoverType, decoded), status (ServiceStatus, decoded), district
  proto/data/inlets/massdot_conveyance.csv.gz   size (PIPESIZE), material, culvert, linetype, status, xy ('x y;x y;...' EPSG:26986, 0.1 m)
  proto/data/inlets/inventory.json              counts by type / cover / status, per catalogue box, conveyance size coverage
"""
import argparse, csv, glob, gzip, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'data', 'inlets')
REPO = 'mohabeldokla/mass-flood-watch-tiles'
MARGIN = 2000.0
DRAINS_BOX = (168000.0, 908000.0, 188000.0, 928000.0)


def boxes():
    B = {}
    for p in sorted(glob.glob(os.path.join(ROOT, 'docs', 'proto', 'parity', 'catalog', '*', 'config.json'))):
        c = json.load(open(p)); B[c['name']] = tuple(float(v) for v in c['box'].split(','))
    B['drains_leominster'] = DRAINS_BOX
    return B


def domains(layer_json):
    """field name -> {code: name} from the layer's coded-value domains."""
    out = {}
    for f in layer_json.get('fields', []):
        d = f.get('domain') or {}
        if d.get('type') == 'codedValue': out[f['name']] = {str(c['code']): c['name'] for c in d.get('codedValues', [])}
    for t in layer_json.get('types', []) or []:      # subtype domains
        for k, d in (t.get('domains') or {}).items():
            if d.get('type') == 'codedValue': out.setdefault(k, {}).update({str(c['code']): c['name'] for c in d.get('codedValues', [])})
    return out


def in_any(x, y, B, m=MARGIN):
    return [n for n, (x0, y0, x1, y1) in B.items() if x0 - m <= x <= x1 + m and y0 - m <= y <= y1 + m]


def fetch(date):
    from huggingface_hub import hf_hub_download
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 26986, always_xy=True); B = boxes(); os.makedirs(OUT, exist_ok=True)
    get = lambda f: hf_hub_download(REPO, f'massdot_stormwater/{date}/{f}', repo_type='dataset')
    # --- inlets
    lj = json.load(open(get('02_Inlet.layer.json'))); D = domains(lj)
    dec = lambda k, v: D.get(k, {}).get(str(v), v) if v not in (None, '') else ''
    rows = list(csv.DictReader(io.TextIOWrapper(gzip.open(get('02_Inlet.csv.gz')), encoding='utf-8')))
    out = []; cnt = dict(type={}, cover={}, status={}, owned={}, per_box={n: 0 for n in B}, read=len(rows), no_xy=0)
    for r in rows:
        try: lon, lat = float(r['lon']), float(r['lat'])
        except (TypeError, ValueError): cnt['no_xy'] += 1; continue
        x, y = tr.transform(lon, lat); hit = in_any(x, y, B); d = str(r.get('District') or '')
        if d != '3' and not hit: continue
        t, cv, st = dec('InletType', r.get('InletType')), dec('CoverType', r.get('CoverType')), dec('ServiceStatus', r.get('ServiceStatus'))
        out.append([f'{lon:.6f}', f'{lat:.6f}', t, cv, st, d])
        for k, v in (('type', t), ('cover', cv), ('status', st), ('owned', dec('OwnedBy', r.get('OwnedBy')))): cnt[k][str(v)] = cnt[k].get(str(v), 0) + 1
        for n in in_any(x, y, B, 0.0): cnt['per_box'][n] += 1
    sio = io.StringIO(); w = csv.writer(sio); w.writerow(['lon', 'lat', 'type', 'cover', 'status', 'district']); w.writerows(out)
    open(os.path.join(OUT, 'massdot_inlets.csv.gz'), 'wb').write(gzip.compress(sio.getvalue().encode(), 9, mtime=0))
    cnt['kept'] = len(out)
    # --- conveyance
    cj = json.load(open(get('05_Conveyance.layer.json'))); DC = domains(cj)
    decc = lambda k, v: DC.get(k, {}).get(str(v), v) if v not in (None, '') else ''
    G = json.load(gzip.open(get('05_Conveyance.geojson.gz')))
    cv_out = []; cc = dict(read=len(G['features']), kept=0, size_known=0, culvert={}, per_box={n: 0 for n in B}, sizes={})
    for f in G['features']:
        g = f.get('geometry') or {}; a = f.get('properties') or {}
        lines = g.get('coordinates') or []
        if g.get('type') == 'LineString': lines = [lines]
        pts = [p for L in lines for p in L]
        if not pts: continue
        X, Y = tr.transform([p[0] for p in pts], [p[1] for p in pts])
        if not any(in_any(x, y, B) for x, y in zip(X[::max(1, len(X) // 20)], Y[::max(1, len(Y) // 20)])) and not in_any(X[-1], Y[-1], B): continue
        size = decc('PIPESIZE', a.get('PIPESIZE')); cul = decc('CULVERT', a.get('CULVERT'))
        cv_out.append([size, decc('MATERIAL', a.get('MATERIAL')), cul, decc('LINETYPE', a.get('LINETYPE')), decc('ServiceStatus', a.get('ServiceStatus')),
                       ';'.join(f'{x:.1f} {y:.1f}' for x, y in zip(X, Y))])
        cc['kept'] += 1; cc['size_known'] += bool(str(size).strip()); cc['culvert'][str(cul)] = cc['culvert'].get(str(cul), 0) + 1
        cc['sizes'][str(size)] = cc['sizes'].get(str(size), 0) + 1
        for n in B:
            if any(in_any(x, y, {n: B[n]}, 0.0) for x, y in zip(X, Y)): cc['per_box'][n] += 1
    sio = io.StringIO(); w = csv.writer(sio); w.writerow(['size', 'material', 'culvert', 'linetype', 'status', 'xy']); w.writerows(cv_out)
    open(os.path.join(OUT, 'massdot_conveyance.csv.gz'), 'wb').write(gzip.compress(sio.getvalue().encode(), 9, mtime=0))
    inv = dict(source=f'HF {REPO} massdot_stormwater/{date}/ (02_Inlet, 05_Conveyance); MassDOT Stormwater Asset Database, public domain',
               boxes={n: list(b) for n, b in B.items()}, margin_m=MARGIN, inlets=cnt, conveyance=cc,
               inlet_domains={k: v for k, v in D.items() if k in ('InletType', 'CoverType', 'ServiceStatus')},
               conveyance_domains={k: v for k, v in DC.items() if k in ('PIPESIZE', 'MATERIAL', 'CULVERT', 'LINETYPE')})
    json.dump(inv, open(os.path.join(OUT, 'inventory.json'), 'w'), indent=1)
    print(json.dumps(dict(inlets_kept=len(out), types=cnt['type'], status=cnt['status'], conveyance_kept=cc['kept'], conveyance_size_known=cc['size_known']), indent=1))


def selftest():
    B = boxes(); assert 'sep2023_leominster_20m' in B and len(B) >= 25, len(B)
    assert in_any(170000.0, 910000.0, B) and not in_any(0.0, 0.0, B)
    assert domains(dict(fields=[dict(name='InletType', domain=dict(type='codedValue', codedValues=[dict(code='CB', name='Catch Basin')]))]))['InletType']['CB'] == 'Catch Basin'
    print('inlets_table selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('fetch'); p.add_argument('--date', default='2026-10-29'); sp.add_parser('selftest')
    a = ap.parse_args()
    fetch(a.date) if a.cmd == 'fetch' else selftest()
