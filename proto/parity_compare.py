"""CPU/GPU parity: compare the infiltration treatments on the catalogue storms (docs/proto/parity/PARITY.md).

    python proto/parity_compare.py          -> docs/proto/parity/parity.json + markdown tables on stdout

Runs (all 20 m, catalogue box and hours, LF_LOSS=cn LF_CN_SCALE=0.91 LF_INFIL_MMH=2):
  gpu       published Turing CUDA run, docs/proto/turing/<id>_<area>_20m (the CUDA solver drops the infiltration keyword)
  cpu_cn    CPU control of the loss test, docs/proto/urban/dcia/<id>_cn
  solver / rain / infil0   .github/workflows/parity_test.yml, docs/proto/parity/<id>_<variant>:
            solver = CPU solver infiltration (as cpu_cn), rain = LF_INFIL_MODE=rain, infil0 = LF_INFIL_MMH=0 (the GPU's physics on the CPU)
Summary metrics as proto/dcia_compare.py; cell by cell from hmax_cm.npz; volumes from the .mass file.
"""
import json, os, sys, glob
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dcia_compare import read  # noqa: E402

STORMS = [('jul2023', 'worcester'), ('aug2023b', 'millbury'), ('sep2023', 'leominster')]
VARIANTS = ['solver', 'rain', 'infil0']
PAIRS = [('rain', 'solver'), ('infil0', 'solver'), ('rain', 'infil0')]
# parity tolerance between two runs of the same storm (what the catalogue reports): same labels caught, flagged share within
# 0.1 percentage point or 10 % of it, every gauge rise within 0.10 m, land area >= 0.3 m within 10 %
TOL = dict(flag_pts=0.10, flag_rel=0.10, rise_m=0.10, wet03_rel=0.10)


def mass(d):
    p = f'{d}/lisflood.mass'
    if not os.path.exists(p): return None
    L = [l.split() for l in open(p) if l.strip()]
    hdr = L[0]; rows = [r for r in L[1:] if len(r) == len(hdr)]
    a = np.array([[float(v) for v in r] for r in rows])
    c = {k: i for i, k in enumerate(hdr)}
    vol = a[:, c['Vol']]
    return dict(vol_start_m3=round(float(vol[0])), vol_peak_m3=round(float(vol.max())), vol_end_m3=round(float(vol[-1])),
                qout_end_m3s=round(float(a[-1, c['Qout']]), 2) if 'Qout' in c else None)


def hmax(d):
    p = f'{d}/hmax_cm.npz'
    if not os.path.exists(p): return None
    z = np.load(p); return z['hmax_cm'].astype(np.float32) / 100.0, z['watermask'].astype(bool)


def cellwise(a, b):
    (ha, wa), (hb, _) = a, b; land = ~wa
    wet = land & ((ha >= 0.1) | (hb >= 0.1)); d = ha - hb
    ca, cb = (ha >= 0.3) & land, (hb >= 0.3) & land
    return dict(wet_cells=int(wet.sum()), mean_abs_diff_wet_m=round(float(np.abs(d[wet]).mean()), 3) if wet.any() else 0.0,
                p95_abs_diff_wet_m=round(float(np.percentile(np.abs(d[wet]), 95)), 3) if wet.any() else 0.0,
                mean_diff_wet_m=round(float(d[wet].mean()), 3) if wet.any() else 0.0,
                deep03_a_km2=round(float(ca.sum()) * 4e-4, 2), deep03_b_km2=round(float(cb.sum()) * 4e-4, 2),
                deep03_jaccard=round(float((ca & cb).sum()) / max(int((ca | cb).sum()), 1), 3))


def within(a, b):
    """Parity verdict for two runs of one storm (summary level)."""
    why = []
    if a['caught'] != b['caught']: why.append(f"labels {a['caught']} vs {b['caught']}")
    fa, fb = 100 * (a['flagged_share'] or 0), 100 * (b['flagged_share'] or 0)
    if abs(fa - fb) > max(TOL['flag_pts'], TOL['flag_rel'] * max(fa, fb)): why.append(f'flagged {fa:.2f}% vs {fb:.2f}%')
    ga = {g['site']: g['model'] for g in a.get('gauges', [])}; gb = {g['site']: g['model'] for g in b.get('gauges', [])}
    for s in ga:
        if s in gb and abs(ga[s] - gb[s]) > TOL['rise_m']: why.append(f'gauge {s} {ga[s]:.2f} vs {gb[s]:.2f} m')
    wa, wb = a.get('wet_land_km2_0p3'), b.get('wet_land_km2_0p3')
    if wa is not None and wb is not None and abs(wa - wb) > TOL['wet03_rel'] * max(wa, wb, 1e-6): why.append(f'land >= 0.3 m {wa:.1f} vs {wb:.1f} km2')
    return dict(match=not why, why=why)


def main():
    out = dict(tolerance=TOL)
    for sid, area in STORMS:
        e = dict(gpu=read(f'{ROOT}/docs/proto/turing/{sid}_{area}_20m'), cpu_cn=read(f'{ROOT}/docs/proto/urban/dcia/{sid}_cn'))
        e['gpu_mass_tail'] = (json.load(open(f'{ROOT}/docs/proto/turing/{sid}_{area}_20m/flood_meta.json')).get('mass_tail') or [None])[-1]
        H = {}
        for v in VARIANTS:
            d = f'{ROOT}/docs/proto/parity/{sid}_{v}'; r = read(d)
            if r is None: continue
            r['mass'] = mass(d)
            mp = f'{d}/flood_meta.json'
            if os.path.exists(mp): r['infiltration'] = json.load(open(mp)).get('inputs', {}).get('infiltration')
            e[v] = r; H[v] = hmax(d)
        e['pairs'] = {}
        for a, b in PAIRS + [('infil0', 'gpu'), ('solver', 'gpu'), ('rain', 'gpu')]:
            if e.get(a) and e.get(b):
                p = within(e[a], e[b])
                if H.get(a) is not None and H.get(b) is not None: p['cells'] = cellwise(H[a], H[b])
                e['pairs'][f'{a}_vs_{b}'] = p
        for r in e.values():
            if isinstance(r, dict): r.pop('sites', None)
        out[sid] = e
    json.dump(out, open(f'{ROOT}/docs/proto/parity/parity.json', 'w'), indent=1)
    cols = ['gpu', 'cpu_cn'] + VARIANTS
    def cell(r):
        if not r: return '–'
        g = ' / '.join(f"{x['model']:.2f}" for x in r.get('gauges', []))
        return f"{r['caught']}/{r['n']} · {100 * (r['flagged_share'] or 0):.2f}% · {r.get('wet_land_km2_0p3', float('nan')):.1f} km² · {g} m"
    print('| storm | ' + ' | '.join(cols) + ' |'); print('|---' * (len(cols) + 1) + '|')
    for sid, _ in STORMS: print(f'| {sid} | ' + ' | '.join(cell(out[sid].get(c)) for c in cols) + ' |')
    print()
    for sid, _ in STORMS:
        for k, p in out[sid]['pairs'].items():
            print(f"{sid} {k}: {'MATCH' if p['match'] else 'differ: ' + '; '.join(p['why'])}" + (f" | cells {p['cells']}" if 'cells' in p else ''))
        for v in VARIANTS:
            if out[sid].get(v): print(f"{sid} {v} mass {out[sid][v].get('mass')} infil {out[sid][v].get('infiltration')}")
        print(f"{sid} gpu mass tail {out[sid]['gpu_mass_tail']}")


if __name__ == '__main__':
    main()
