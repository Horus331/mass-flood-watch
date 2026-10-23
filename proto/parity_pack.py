"""Small per-run files for CPU/GPU parity checks (docs/proto/parity/PARITY.md).

    python proto/parity_pack.py <w9 out dir> <dest dir>

Writes <dest>/hmax_cm.npz (hmax_cm = solver max depth, hsnap_cm = peak of the 30-min snapshots, both uint16 cm; watermask),
<dest>/hmax_stats.json (land area >= 0.1 / 0.3 m from hmax and from the snapshots) and copies lisflood.mass.  A cell where hmax is far
above every snapshot is a short spike (or a solver artefact); proto/parity_compare.py compares runs cell by cell.
"""
import json, os, shutil, sys
import numpy as np


def main(o, d):
    os.makedirs(d, exist_ok=True)
    h = np.nan_to_num(np.load(f'{o}/hmax.npy').astype(np.float32))
    w = np.load(f'{o}/watermask.npy').astype(bool) if os.path.exists(f'{o}/watermask.npy') else np.zeros(h.shape, bool)
    s = np.nan_to_num(np.load(f'{o}/hsnap.npy').astype(np.float32)) if os.path.exists(f'{o}/hsnap.npy') else None
    cm = lambda a: np.clip(np.round(a * 100), 0, 65535).astype(np.uint16)
    np.savez_compressed(f'{d}/hmax_cm.npz', hmax_cm=cm(h), watermask=w.astype(np.uint8), **({'hsnap_cm': cm(s)} if s is not None else {}))
    land = ~w
    meta = json.load(open(f'{o}/meta.json')) if os.path.exists(f'{o}/meta.json') else {}
    a = (meta.get('res_m') or 20.0) ** 2 / 1e6
    st = dict(wet_land_km2_0p1=float(((h >= 0.1) & land).sum() * a), wet_land_km2_0p3=float(((h >= 0.3) & land).sum() * a))
    if s is not None:
        st.update(snap_wet_land_km2_0p3=float(((s >= 0.3) & land).sum() * a),
                  spike_cells_0p3=int(((h >= 0.3) & (s < 0.3) & (h > s + 0.10) & land).sum()))
    json.dump(st, open(f'{d}/hmax_stats.json', 'w'))
    if os.path.exists(f'{o}/lisflood.mass'): shutil.copy(f'{o}/lisflood.mass', f'{d}/lisflood.mass')
    print('parity pack:', d, st)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
