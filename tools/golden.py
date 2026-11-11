"""Golden-storm regression (master prompt Phase 0.6; docs/proto/GOLDEN.md).

    python tools/golden.py fingerprint <w9 out dir> <prototype out dir> <fingerprint.json>
    python tools/golden.py compare docs/proto/golden/reference.json <fingerprint.json>     # exit 1 on a regression
    python tools/golden.py selftest

The golden storm: Leominster, 11 Sep 2023 (the tuning storm), an 8 x 8 km box over the city at 20 m, 12 h of observed MRMS rain from the
catalogue t0, the live model settings (forecast.yml), CPU.  The fingerprint is what a change to the code could silently move: rain in,
water out, flooded area, peak depth, road closures (count and which ones).
"""
import json, os, sys
import numpy as np

TOL = dict(rain_rel=0.001, area_rel=0.02, depth_abs_m=0.05, closures_abs=2, closure_jaccard=0.9)


def fingerprint(o, p, out):
    h = np.nan_to_num(np.load(f'{o}/hmax.npy').astype(np.float32))
    w = np.load(f'{o}/watermask.npy').astype(bool) if os.path.exists(f'{o}/watermask.npy') else np.zeros(h.shape, bool)
    meta = json.load(open(f'{o}/meta.json')); a = (meta.get('res_m') or 20.0) ** 2 / 1e6; land = ~w
    S = json.load(open(f'{p}/summary.json'))
    closed = []
    for f in json.load(open(f'{p}/segments.geojson'))['features']:
        q = f['properties']
        if (q.get('p_close') or 0) >= 0.5: closed.append(int(q['segment']))
    F = dict(rain_max_total_mm=S.get('rain_max_total_mm'), rain_peak1h_max_mm=S.get('rain_peak1h_max_mm'),
             wet_land_km2_0p1=float(((h >= 0.1) & land).sum() * a), wet_land_km2_0p3=float(((h >= 0.3) & land).sum() * a),
             depth_p99_land_m=float(np.percentile(h[land & (h > 0.01)], 99)) if (land & (h > 0.01)).any() else 0.0,
             segments_in_box=S.get('segments_in_box'), closures=len(closed), closed_segments=sorted(closed),
             runtime_s=S.get('flood_model_runtime_s'), git_sha=os.environ.get('GIT_SHA'))
    json.dump(F, open(out, 'w'), indent=1); print(json.dumps({k: v for k, v in F.items() if k != 'closed_segments'})); return F


def compare(R, N):
    """-> list of failures (empty = pass)."""
    bad = []
    rel = lambda a, b: abs(a - b) / max(abs(a), 1e-9)
    for k in ('rain_max_total_mm', 'rain_peak1h_max_mm'):
        if rel(R[k], N[k]) > TOL['rain_rel']: bad.append(f'{k}: {R[k]} -> {N[k]} (rain input changed)')
    for k in ('wet_land_km2_0p1', 'wet_land_km2_0p3'):
        if rel(R[k], N[k]) > TOL['area_rel']: bad.append(f'{k}: {R[k]:.3f} -> {N[k]:.3f} km2 (> {TOL["area_rel"]:.0%})')
    if abs(R['depth_p99_land_m'] - N['depth_p99_land_m']) > TOL['depth_abs_m']: bad.append(f"depth_p99_land_m: {R['depth_p99_land_m']:.3f} -> {N['depth_p99_land_m']:.3f}")
    if R['segments_in_box'] != N['segments_in_box']: bad.append(f"segments_in_box: {R['segments_in_box']} -> {N['segments_in_box']} (road network changed)")
    if abs(R['closures'] - N['closures']) > TOL['closures_abs']: bad.append(f"closures: {R['closures']} -> {N['closures']}")
    A, B = set(R['closed_segments']), set(N['closed_segments'])
    j = len(A & B) / len(A | B) if A | B else 1.0
    if j < TOL['closure_jaccard']: bad.append(f'closed-segment overlap {j:.2f} < {TOL["closure_jaccard"]} (lost {sorted(A - B)[:10]}, new {sorted(B - A)[:10]})')
    return bad


def selftest():
    R = dict(rain_max_total_mm=150.0, rain_peak1h_max_mm=60.0, wet_land_km2_0p1=5.0, wet_land_km2_0p3=1.0, depth_p99_land_m=1.2,
             segments_in_box=900, closures=30, closed_segments=list(range(30)))
    assert compare(R, dict(R)) == []
    N = dict(R, wet_land_km2_0p3=1.05); assert any('wet_land_km2_0p3' in b for b in compare(R, N))
    N = dict(R, closures=27, closed_segments=list(range(27))); assert any('closures' in b for b in compare(R, N))
    N = dict(R, closed_segments=list(range(5, 35))); assert any('overlap' in b for b in compare(R, N))
    print('golden selftest ok')


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'selftest': selftest()
    elif c == 'fingerprint': fingerprint(*sys.argv[2:5])
    elif c == 'compare':
        R, N = json.load(open(sys.argv[2])), json.load(open(sys.argv[3])); bad = compare(R, N)
        print('\n'.join(['GOLDEN STORM REGRESSION:'] + bad) if bad else 'golden storm: pass (all within tolerance)')
        print(f"closures {R['closures']} -> {N['closures']}; flooded >= 0.3 m {R['wet_land_km2_0p3']:.3f} -> {N['wet_land_km2_0p3']:.3f} km2; runtime {N.get('runtime_s')} s")
        sys.exit(1 if bad else 0)
