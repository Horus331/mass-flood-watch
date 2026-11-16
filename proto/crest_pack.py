"""Ground grids for the crest-relative road readout (docs/proto/phase1/PARAMETRIC_T2_PREREG.md; same readout as proto/whatif_v3.py).

    python proto/crest_pack.py <w9 out dir> <dest dir>

Writes <dest>/zz_cm.npz: z_cm = the solver's ground (with notches, carved channels), zc_cm = the lidar ground before any carving (the 10 m
maximum when the run kept it, else the raw lidar), both int32 cm on the run grid.  With hmax_cm.npz (proto/parity_pack.py) this gives the
water surface over the road crest: max(z + h - zc, 0).
"""
import os, sys
import numpy as np


def main(o, d):
    os.makedirs(d, exist_ok=True)
    z = np.nan_to_num(np.load(f'{o}/z.npy').astype(np.float32))
    zf = np.load(f'{o}/z_raw.npz')
    zc = (zf['z_raw_max10'] if 'z_raw_max10' in zf else zf['z_raw']).astype(np.float32)
    cm = lambda a: np.round(np.nan_to_num(a) * 100).astype(np.int32)
    np.savez_compressed(f'{d}/zz_cm.npz', z_cm=cm(z), zc_cm=cm(zc))
    print('crest pack:', d, z.shape, 'cells carved below the lidar:', int((z < zc - 0.05).sum()))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
