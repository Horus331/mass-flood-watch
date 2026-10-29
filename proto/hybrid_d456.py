"""Pre-registered hybrid rule (model rule U FEMA SFHA) on the District 4-6 transfer pool (docs/proto/static/HYBRID.md).

The hybrid was found exploratorily on District 3 (docs/proto/static/STATIC.md section 2.2).  HYBRID.md freezes two variants and the decision
before any FEMA polygon is intersected with a District 4-6 road; this file implements exactly that.

    python proto/hybrid_d456.py fetch --out sfha_d456.json      # GitHub Actions only (hybrid_d456.yml): MassGIS statewide NFHL (FEMA REST
                                                                 #   fallback) -> per OSM segment % of length inside the SFHA, per storm box
    python proto/hybrid_d456.py emit sfha_d456.json --part P     # transport: gzip (mtime 0, so every job emits identical chunks) + base64
                                                                 #   ::notice annotations in the static_maps format
    python proto/static_maps.py decode --run RUN --out docs/proto/static/hybrid_d456_sfha.json
    python proto/hybrid_d456.py score --flags docs/proto/static/hybrid_d456_sfha.json --runs-root DIR --out docs/proto/static/hybrid_d456.json
    python proto/hybrid_d456.py selftest

--runs-root is a folder holding docs/proto/transfer/{r1,roads_osm} as on the work branch transfer-d456 (features_<id>.csv[.gz] per run).
"""
import argparse
import csv
import gzip
import json
import os
import shutil
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))

STRICT = 30.0            # SFHA flag: >= 30 % of the segment's length inside the SFHA (frozen, HYBRID.md H1/H2)
RAIN_GATE_MM = 40.0      # H2: box-mean radar storm total (flood_meta.json rain_total_mean_mm) >= 40 mm (frozen, HYBRID.md)
ALPHA = 0.05; K_VARIANTS = 2; MIN_GAIN = 0.04; BOOT = 2000
CAT_D456 = os.path.join(ROOT, 'docs', 'proto', 'obs', 'catalog_d456.json')


def events():
    return [dict(id=e['id'], name=f"{e['id']}_{e['area']}_20m", box=[float(v) for v in e['box_26986']], district=e.get('district'))
            for e in json.load(open(CAT_D456))['events']]


def graph_lines(path):
    """OSM road graph (graph_segments.json layout) -> list of shapely lines per segment in EPSG:26986."""
    import shapely
    from pyproj import Transformer
    from impacts import decode_segments
    S = json.load(gzip.open(path, 'rt') if path.endswith('.gz') else open(path)); tr = Transformer.from_crs(4326, 26986, always_xy=True); parts = {}
    for s, lon, lat in decode_segments(S):
        x, y = tr.transform(lon, lat)
        if len(x) >= 2: parts.setdefault(s, []).append(np.column_stack([x, y]))
    out = []
    for s in range(S['n']):
        P = parts.get(s, [])
        out.append(shapely.MultiLineString([shapely.LineString(p) for p in P]) if len(P) > 1 else shapely.LineString(P[0]) if P else None)
    return out


# ------------------------------------------------------------------------------------------------ fetch (Actions only)
def fetch(out, roads_dir, log=print):
    import shapely
    import static_maps as SM
    E = events(); M = 3000.0
    allb = (min(e['box'][0] for e in E) - M, min(e['box'][1] for e in E) - M, max(e['box'][2] for e in E) + M, max(e['box'][3] for e in E) + M)
    meta = dict(made=time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), strict_pct=STRICT, storms=len(E), sources={})
    polys = None
    try:
        import geopandas as gpd
        import requests
        import tempfile
        import zipfile
        tmp = os.path.join(tempfile.gettempdir(), 'massgis_nfhl.zip'); hdr = {}
        for i in range(4):
            try:
                with requests.get(SM.MASSGIS_ZIP, stream=True, timeout=600) as r:
                    r.raise_for_status(); hdr = {k: r.headers.get(k) for k in ('Last-Modified', 'Content-Length', 'ETag')}
                    with open(tmp, 'wb') as f:
                        for b in r.iter_content(1 << 20): f.write(b)
                break
            except Exception as e:
                log(f'MassGIS download try {i}: {e}'); time.sleep(20)
        else:
            raise RuntimeError('MassGIS NFHL download failed')
        names = [n for n in zipfile.ZipFile(tmp).namelist() if n.lower().endswith('.shp')]; shp = [n for n in names if 'poly' in n.lower()] or names
        mask = gpd.GeoSeries([shapely.union_all([shapely.box(e['box'][0] - M, e['box'][1] - M, e['box'][2] + M, e['box'][3] + M) for e in E])], crs=26986)
        G = gpd.read_file(f'zip://{tmp}!{shp[0]}', mask=mask).to_crs(26986); polys = []; cnt = {}
        for a, g in zip(G.drop(columns='geometry').to_dict('records'), G.geometry):
            c = SM.fema_class(a); cnt[str(c)] = cnt.get(str(c), 0) + 1
            if c == 'sfha' and g is not None and not g.is_empty: polys.append(shapely.make_valid(g))
        meta['sources']['fema'] = dict(source='MassGIS statewide NFHL (FEMA_NFHL_POLY)', url=SM.MASSGIS_ZIP, http=hdr, shapefile=shp[0],
                                       polygons_in_mask=len(G), by_class=cnt, sfha_polygons=len(polys))
        log(f"MassGIS NFHL {hdr}: {len(G)} polygons in the District 4-6 boxes, SFHA {len(polys)}")
    except Exception as e:
        log(f'MassGIS failed ({e}); FEMA REST fallback'); meta['sources']['massgis_error'] = str(e); polys = []
        srv = None
        for s in SM.FEMA_SERVERS:
            try:
                j = SM._get(s, dict(f='json'), tries=3); ids = [l['id'] for l in j.get('layers', []) if l.get('name', '').strip().lower() == SM.FEMA_LAYER_NAME]
                srv = f'{s}/{ids[0] if ids else SM.FEMA_LAYER_DEFAULT}'; break
            except Exception as ee: log(f'{s}: {ee}')
        if not srv: raise SystemExit('no FEMA source reachable')
        st_all = []
        for e in E:
            b = e['box']; F, st = SM.query_tiles(srv, (b[0] - M, b[1] - M, b[2] + M, b[3] + M), where="SFHA_TF = 'T'", log=log); st_all.append(st)
            for f in F:
                if SM.fema_class(f.get('attributes', {})) == 'sfha':
                    g = SM.esri_polygon((f.get('geometry') or {}).get('rings'))
                    if g is not None: polys.append(g)
        meta['sources']['fema'] = dict(source='FEMA NFHL REST', layer=srv, sfha_polygons=len(polys), requests=sum(s['requests'] for s in st_all))
    P = np.array(polys, dtype=object); tree = shapely.STRtree(P); cats = {}; meta['per_storm'] = {}
    for e in E:
        p = os.path.join(roads_dir, e['name'] + '.json.gz')
        if not os.path.exists(p): log(f"{e['id']}: no road graph {p}"); meta['per_storm'][e['id']] = dict(error='no road graph'); continue
        t = time.time(); lines = graph_lines(p); B = [g for g in lines if g is not None]
        bb = shapely.bounds(np.array(B, dtype=object)); env = shapely.box(bb[:, 0].min(), bb[:, 1].min(), bb[:, 2].max(), bb[:, 3].max())
        sel = list(P[tree.query(env, predicate='intersects')])
        d = SM.overlap_pct(lines, {'sfha': sel}, log=lambda *a: None)['sfha']; cats[f"sfha|{e['id']}"] = d
        meta['per_storm'][e['id']] = dict(n_graph=len(lines), polygons=len(sel), any=len(d), ge30=sum(v >= STRICT for v in d.values()))
        log(f"{e['id']:10s} {len(lines):6d} segments, {len(sel):5d} SFHA polygons, touched {len(d):5d}, >= 30 % {meta['per_storm'][e['id']]['ge30']:5d} ({time.time() - t:.0f} s)")
    res = dict(meta=meta, categories=cats); json.dump(res, open(out, 'w'), separators=(',', ':'))
    return res


# ------------------------------------------------------------------------------------------------ scoring
def stage_runs(runs_root, dest):
    """Copy the r1 run folders score_v2 needs (flood_meta, matches, features as plain csv) and roads_osm next to them -> dest/r1."""
    src = os.path.join(runs_root, 'docs', 'proto', 'transfer') if os.path.isdir(os.path.join(runs_root, 'docs')) else runs_root
    r1 = os.path.join(dest, 'r1'); os.makedirs(r1, exist_ok=True)
    ro = os.path.join(dest, 'roads_osm')
    if not os.path.exists(ro): os.symlink(os.path.abspath(os.path.join(src, 'roads_osm')), ro)
    for e in events():
        s = os.path.join(src, 'r1', e['name']); d = os.path.join(r1, e['name'])
        if not os.path.isdir(s): continue
        os.makedirs(d, exist_ok=True)
        for f in ('flood_meta.json', f"matches_{e['id']}.json"):
            if os.path.exists(os.path.join(s, f)) and not os.path.exists(os.path.join(d, f)): shutil.copy(os.path.join(s, f), d)
        fc = os.path.join(d, f"features_{e['id']}.csv")
        if not os.path.exists(fc):
            g = os.path.join(s, f"features_{e['id']}.csv.gz")
            if os.path.exists(g):
                with gzip.open(g, 'rt') as a, open(fc, 'w') as b: b.write(a.read())
            elif os.path.exists(os.path.join(s, f"features_{e['id']}.csv")): shutil.copy(os.path.join(s, f"features_{e['id']}.csv"), d)
    return r1


def flags_for(flags, storm, segs):
    d = flags['categories'].get(f'sfha|{storm}', {})
    return np.array([d.get(str(int(s)), 0) for s in segs], float)


def _binary(R, flag):
    Q = dict(R); Q['p'] = flag.astype(float); Q['pm'] = Q['p'].copy(); Q['depth'] = np.zeros(len(flag)); return Q


def blk(B):
    return dict(k=B['k'], share=B['share'], hits=B['_hits'], chance=B['_chance'])


def score_storm(R, pct, rain_mean):
    """One storm, box domain: model rule, SFHA>=30 alone, H1, H2, and the model's top-k at each hybrid's own k."""
    import score_v2 as S
    n = len(R['seg']); dm = np.ones(n, bool); rule = R['p'] >= 0.5; sf = pct >= STRICT
    gate = rain_mean is not None and rain_mean >= RAIN_GATE_MM
    masks = dict(sfha30=sf, H1=rule | sf, H2=rule | (sf if gate else np.zeros(n, bool)), sfha_any_hybrid=rule | (pct > 0))
    ks = {v: int(m.sum()) for v, m in masks.items()}
    S.SHARES = tuple(sorted({k / n for k in ks.values()}))
    M = S.score_domain(R, dm, None); S.SHARES = ()
    D = dict(n=n, n_sites=M['n_sites'], sites=[s['id'] for s in M['sites']], rain_mean_mm=rain_mean, gate=bool(gate), model_rule=blk(M['rule']), rows={}, model_k={})
    for v, m in masks.items():
        D['rows'][v] = blk(S.score_domain(_binary(R, m), dm, None)['rule']); D['model_k'][v] = blk(M['shares'][f'{ks[v] / n:g}'])
    return D


def boot_pair(H1, H0, boot=BOOT, seed=0, alpha=ALPHA / K_VARIANTS):
    """Paired two-stage bootstrap (storms, then sites within storm) of pooled recall(H1) - recall(H0); one-sided lower bound at alpha."""
    rng = np.random.default_rng(seed); N = sum(len(h) for h in H1)
    if N == 0: return dict(delta=None)
    d0 = (sum(h.sum() for h in H1) - sum(h.sum() for h in H0)) / N; dd = []
    for _ in range(boot):
        sel = rng.integers(0, len(H1), len(H1)); a = b = n = 0.0
        for i in sel:
            if not len(H1[i]): continue
            j = rng.integers(0, len(H1[i]), len(H1[i])); a += H1[i][j].sum(); b += H0[i][j].sum(); n += len(j)
        dd.append((a - b) / n if n else 0.0)
    dd = np.array(dd)
    return dict(delta=float(d0), lower_one_sided=float(np.percentile(dd, 100 * alpha)), alpha=alpha, ci90=[float(x) for x in np.percentile(dd, [5, 95])],
                p_one_sided=float((dd <= 0).mean()))


def pool(per, get):
    H = C = N = K = Nn = 0.0; shares = []
    for D in per.values():
        B = get(D); H += sum(B['hits']); C += sum(B['chance']); N += len(B['hits']); K += B['k']; Nn += D['n']; shares.append(B['share'])
    return dict(sites=int(N), hits=H, recall=H / N if N else None, chance=C / N if N else None, lift=H / C if C else None,
                pooled_share=K / Nn if Nn else None, mean_share=float(np.mean(shares)) if shares else None, flagged=int(K),
                hits_per_1000_flagged=1000 * H / K if K else None)


def score(flags_path, runs_root, out, boot=BOOT):
    import warnings
    import score_v2 as S
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    S.RADII = (300,); S.FSS_DRAWS = 0
    flags = json.load(open(flags_path)) if flags_path else dict(categories={}, meta={})
    import tempfile
    work = tempfile.mkdtemp(prefix='hyb_'); r1 = stage_runs(runs_root, work); per = {}
    for e in events():
        d = os.path.join(r1, e['name'])
        if not os.path.exists(os.path.join(d, 'flood_meta.json')): print('missing run', e['name']); continue
        t = time.time(); R = S.load_run(d, e['id']); m = json.load(open(os.path.join(d, 'flood_meta.json')))
        D = score_storm(R, flags_for(flags, e['id'], R['seg']), m.get('rain_total_mean_mm')); D['district'] = e['district']; D['run'] = e['name']; per[e['id']] = D
        print(f"{e['id']:9s} D{e['district']} sites {D['n_sites']:3d} rain {D['rain_mean_mm']} gate {int(D['gate'])} rule {sum(D['model_rule']['hits']):.0f} "
              f"H1 {sum(D['rows']['H1']['hits']):.0f}/{D['rows']['H1']['k']} H2 {sum(D['rows']['H2']['hits']):.0f}/{D['rows']['H2']['k']} ({time.time() - t:.0f} s)", flush=True)
    P = {k: v for k, v in per.items() if v['n_sites'] > 0}
    hl = lambda get: [np.asarray(get(D)['hits'], float) for D in P.values()]
    res = dict(made_by='proto/hybrid_d456.py score', flags=os.path.relpath(os.path.abspath(flags_path), ROOT) if flags_path else None,
               frozen=dict(strict_pct=STRICT, rain_gate_mm=RAIN_GATE_MM, alpha=ALPHA, k=K_VARIANTS, min_gain=MIN_GAIN, boot=boot, seed=0),
               storms=len(per), storms_with_sites=len(P), per_storm=per, pooled={}, tests={}, decision={})
    res['pooled']['model_rule'] = pool(P, lambda D: D['model_rule'])
    for v in ('sfha30', 'H1', 'H2', 'sfha_any_hybrid'):
        res['pooled'][v] = pool(P, lambda D, v=v: D['rows'][v]); res['pooled'][f'model_topk_at_{v}'] = pool(P, lambda D, v=v: D['model_k'][v])
        res['tests'][v] = dict(vs_rule=boot_pair(hl(lambda D, v=v: D['rows'][v]), hl(lambda D: D['model_rule']), boot),
                               vs_model_same_share=boot_pair(hl(lambda D, v=v: D['rows'][v]), hl(lambda D, v=v: D['model_k'][v]), boot))
    for v in ('H1', 'H2'):
        a, b = res['tests'][v]['vs_rule'], res['tests'][v]['vs_model_same_share']
        c = dict(gain_vs_rule_ge_0p04=bool(a['delta'] is not None and a['delta'] >= MIN_GAIN), lower_vs_rule_gt_0=bool(a['delta'] is not None and a['lower_one_sided'] > 0),
                 beats_model_same_share=bool(b['delta'] is not None and b['delta'] > 0), lower_vs_same_share_gt_0=bool(b['delta'] is not None and b['lower_one_sided'] > 0))
        res['decision'][v] = dict(checks=c, adopt=all(c.values()))
    passing = [v for v in ('H1', 'H2') if res['decision'][v]['adopt']]
    res['decision']['adopted'] = max(passing, key=lambda v: res['tests'][v]['vs_model_same_share']['lower_one_sided']) if passing else None
    # descriptive: by district
    res['by_district'] = {}
    for dist in sorted({D['district'] for D in P.values()}):
        Q = {k: D for k, D in P.items() if D['district'] == dist}
        res['by_district'][str(dist)] = {v: pool(Q, (lambda D: D['model_rule']) if v == 'model_rule' else (lambda D, v=v: D['rows'][v])) for v in ('model_rule', 'H1', 'H2')}
    res['gate'] = dict(storms_gated=sum(D['gate'] for D in per.values()), storms=len(per))
    json.dump(res, open(out, 'w'), indent=0, default=float); shutil.rmtree(work, ignore_errors=True)
    return res


def emit(path, part, per=10):
    """static_maps.emit with a deterministic gzip header, so chunks printed by different jobs join into one payload."""
    import base64
    import hashlib
    import static_maps as SM
    raw = gzip.compress(json.dumps(SM.compact(json.load(open(path))), separators=(',', ':')).encode(), 9, mtime=0); b = base64.b64encode(raw).decode()
    sha = hashlib.sha256(b.encode()).hexdigest()[:12]; ch = [b[i:i + SM.CHUNK] for i in range(0, len(b), SM.CHUNK)]; n = len(ch)
    if part == 0:
        m = json.load(open(path))['meta']
        print(f"::warning title=hybrid_d456 summary::chunks {n} sha {sha} source {json.dumps({k: {x: v.get(x) for x in ('source', 'http', 'sfha_polygons')} for k, v in m['sources'].items() if isinstance(v, dict)})}")
    for i in range(part * per, min(n, (part + 1) * per)):
        print(f'::notice title=sf {i}/{n} {sha}::{ch[i]}')
    return n


def selftest():
    ok = True

    def check(n, c):
        nonlocal ok; ok &= bool(c); print(('PASS ' if c else 'FAIL ') + n)
    a = [np.array([1., 0, 1]), np.array([0., 1])]; b = [np.zeros(3), np.zeros(2)]
    check('boot identical', boot_pair(a, a, 200)['delta'] == 0)
    r = boot_pair(a, b, 200); check(f'boot better {r}', r['lower_one_sided'] >= 0 and r['delta'] > 0)
    f = dict(categories={'sfha|x': {'3': 30, '5': 29, '7': 100}})
    check('flags >= 30', list(flags_for(f, 'x', [3, 5, 7, 9]) >= STRICT) == [True, False, True, False])
    print('selftest', 'OK' if ok else 'FAILED'); return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('fetch'); p.add_argument('--out', required=True); p.add_argument('--roads', default=os.path.join(ROOT, 'docs', 'proto', 'transfer', 'roads_osm'))
    p = sp.add_parser('emit'); p.add_argument('path'); p.add_argument('--part', type=int, default=0)
    p = sp.add_parser('score'); p.add_argument('--flags'); p.add_argument('--runs-root', required=True); p.add_argument('--out', required=True); p.add_argument('--boot', type=int, default=BOOT)
    sp.add_parser('selftest')
    a = ap.parse_args()
    if a.cmd == 'fetch': fetch(a.out, a.roads)
    elif a.cmd == 'emit': emit(a.path, a.part)
    elif a.cmd == 'score': score(a.flags, a.runs_root, a.out, a.boot)
    else: sys.exit(0 if selftest() else 1)


if __name__ == '__main__':
    main()
