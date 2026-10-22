"""2020 Census blocks -> compact population points for proto/resilience.py and proto/risk.py.

    python proto/census_blocks.py --state 25 --out docs/network/census_blocks_ma.npz     # Massachusetts (run in .github/workflows/census.yml)
    python proto/census_blocks.py --state 50 --out docs/network/census_blocks_vt.npz     # Vermont
    python proto/census_blocks.py --selftest

Source: US Census Bureau, 2020 TIGER/Line Shapefiles, tabulation blocks (TABBLOCK20),
https://www2.census.gov/geo/tiger/TIGER2020/TABBLOCK20/tl_2020_<ss>_tabblock20.zip.  The block attribute table carries POP20 and HOUSING20
(2020 Census P.L. 94-171 redistricting counts: total population and housing units) and the internal point INTPTLAT20 / INTPTLON20 (a point
inside the block, the Census Bureau's representative point).  Only the .dbf is read (no geometry, no GIS dependency).

Output (.npz, compressed), blocks with POP20 > 0 only:
  geoid    int64   15-digit block GEOID20
  lat, lon int32   internal point x 1e6 (deg)
  pop      int32   POP20
  housing  int32   HOUSING20
  meta     json string: source URL, counts, totals
"""
import os, sys, io, json, struct, zipfile, argparse, time
import numpy as np

URL = 'https://www2.census.gov/geo/tiger/TIGER2020/TABBLOCK20/tl_2020_{st}_tabblock20.zip'


def read_dbf(fh, fields):
    """Minimal dBASE III reader: yields dicts with the requested fields (strings, stripped)."""
    head = fh.read(32); nrec, hlen, rlen = struct.unpack('<IHH', head[4:12])
    desc = []; off = 1
    while True:
        b = fh.read(1)
        if b == b'\r' or not b: break
        d = b + fh.read(31); name = d[:11].split(b'\0')[0].decode('ascii'); ln = d[16]
        desc.append((name, off, ln)); off += ln
    fh.read(hlen - 32 - 32 * len(desc) - 1)
    want = [(n, o, l) for n, o, l in desc if n in fields]
    missing = set(fields) - {n for n, _, _ in want}
    if missing: raise ValueError(f'dbf lacks fields {sorted(missing)}; has {[n for n, _, _ in desc]}')
    for _ in range(nrec):
        r = fh.read(rlen)
        if len(r) < rlen: break
        if r[:1] == b'*': continue
        yield {n: r[o:o + l].decode('latin-1').strip() for n, o, l in want}


def convert(dbf_bytes, url=''):
    F = ['GEOID20', 'POP20', 'HOUSING20', 'INTPTLAT20', 'INTPTLON20']
    g, la, lo, p, h = [], [], [], [], []; n_all = 0; pop_all = 0
    for r in read_dbf(io.BytesIO(dbf_bytes), F):
        n_all += 1; pp = int(r['POP20'] or 0); pop_all += pp
        if pp <= 0: continue
        g.append(int(r['GEOID20'])); la.append(round(float(r['INTPTLAT20']) * 1e6)); lo.append(round(float(r['INTPTLON20']) * 1e6))
        p.append(pp); h.append(int(r['HOUSING20'] or 0))
    meta = dict(source=url or 'US Census Bureau 2020 TIGER/Line TABBLOCK20', fields='POP20, HOUSING20, INTPTLAT20, INTPTLON20 (2020 Census P.L. 94-171)',
                blocks_all=n_all, blocks_populated=len(p), population=int(sum(p)), population_all_blocks=int(pop_all), housing_units=int(sum(h)),
                made=time.strftime('%Y-%m-%d'))
    return dict(geoid=np.asarray(g, np.int64), lat=np.asarray(la, np.int32), lon=np.asarray(lo, np.int32), pop=np.asarray(p, np.int32),
                housing=np.asarray(h, np.int32), meta=np.asarray(json.dumps(meta))), meta


def load(path):
    """-> dict lat, lon (float deg), pop, housing (float), geoid, meta (dict).  None if the file is missing."""
    if not path or not os.path.exists(path): return None
    z = np.load(path, allow_pickle=False)
    return dict(lat=z['lat'] / 1e6, lon=z['lon'] / 1e6, pop=z['pop'].astype(float), housing=z['housing'].astype(float), geoid=z['geoid'],
                meta=json.loads(str(z['meta'])))


def fetch(st):
    import urllib.request
    url = URL.format(st=st); req = urllib.request.Request(url, headers={'User-Agent': 'mass-flood-watch research (github.com/Horus331/mass-flood-watch)'})
    for k in range(5):
        try: return urllib.request.urlopen(req, timeout=300).read(), url
        except Exception as e:
            print('  retry', k, repr(e)[:120]); time.sleep(10 * (k + 1))
    raise SystemExit('download failed: ' + url)


def main(st, out, zpath=None):
    if zpath: data, url = open(zpath, 'rb').read(), URL.format(st=st)
    else: data, url = fetch(st)
    with zipfile.ZipFile(io.BytesIO(data)) as Z:
        name = [n for n in Z.namelist() if n.lower().endswith('.dbf')][0]; dbf = Z.read(name)
    arr, meta = convert(dbf, url)
    os.makedirs(os.path.dirname(out) or '.', exist_ok=True); np.savez_compressed(out, **arr)
    print(json.dumps(meta), os.path.getsize(out), 'bytes ->', out)


def _dbf(rows, fields):
    """Tiny dBASE III writer for the selftest: fields = [(name, width)], all character fields."""
    rlen = 1 + sum(w for _, w in fields); hlen = 32 + 32 * len(fields) + 1
    b = bytearray(struct.pack('<BBBBIHH20x', 3, 126, 1, 1, len(rows), hlen, rlen))
    for n, w in fields: b += n.encode().ljust(11, b'\0') + b'C' + b'\0' * 4 + bytes([w, 0]) + b'\0' * 14
    b += b'\r'
    for r in rows: b += b' ' + b''.join(str(v).encode().ljust(w)[:w] for v, (_, w) in zip(r, fields))
    return bytes(b + b'\x1a')


def selftest():
    import tempfile
    fields = [('STATEFP20', 2), ('GEOID20', 15), ('POP20', 9), ('HOUSING20', 9), ('INTPTLAT20', 11), ('INTPTLON20', 12)]
    rows = [('25', '250277101001000', 120, 50, '+42.5251000', '-071.7598000'), ('25', '250277101001001', 0, 0, '+42.5300000', '-071.7500000'),
            ('25', '250277101001002', 7, 3, '+42.5000000', '-071.7000000')]
    arr, meta = convert(_dbf(rows, fields)); ok = True
    def check(name, cond, det=''):
        nonlocal ok; ok &= bool(cond); print(('ok   ' if cond else 'FAIL ') + name, '' if cond else det)
    check('only populated blocks kept', meta['blocks_all'] == 3 and meta['blocks_populated'] == 2 and meta['population'] == 127, meta)
    check('coordinates x 1e6', arr['lat'][0] == 42525100 and arr['lon'][0] == -71759800, (arr['lat'], arr['lon']))
    p = os.path.join(tempfile.mkdtemp(), 'b.npz'); np.savez_compressed(p, **arr); L = load(p)
    check('round trip', abs(L['lat'][1] - 42.5) < 1e-9 and L['pop'].sum() == 127 and L['geoid'][0] == 250277101001000, L)
    print('census_blocks selftest', 'OK' if ok else 'FAILED'); return ok


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--state', default='25'); ap.add_argument('--out'); ap.add_argument('--zip', help='local tl_2020_<ss>_tabblock20.zip instead of downloading')
    ap.add_argument('--selftest', action='store_true'); a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    main(a.state, a.out or f'docs/network/census_blocks_{a.state}.npz', a.zip)
