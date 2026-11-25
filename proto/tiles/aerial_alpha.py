"""Make the no-data part of the self-hosted aerial tiles transparent (25 Nov 2026).

MassGIS fills the area outside Massachusetts and outside its photo coverage with white. In the tiles at the edges of the District 3 box
(proto/tiles/aerial_tiles.py) that white showed as pale blocks on the zoomed-out map. Here near-white pixels (all channels >= 248) that
form large blocks (a 9 x 9 opening, then components of >= 400 pixels) become transparent, so the world photo underneath shows through;
small white things (roofs, snow on a car park) are kept.  Tiles with no such block are left untouched.

    python proto/tiles/aerial_alpha.py AERIAL_DIR      # rewrites the changed tiles in place (WebP with alpha, q72)
"""
import os, sys, glob, concurrent.futures as cf
import numpy as np
from PIL import Image
from scipy import ndimage as nd

ST = np.ones((9, 9), bool)


def fix(p):
    im = Image.open(p).convert('RGB'); a = np.asarray(im)
    w = (a >= 248).all(axis=2)
    if w.sum() < 400: return 0
    m = nd.binary_opening(w, ST)
    if not m.any(): return 0
    lab, n = nd.label(m); size = nd.sum(m, lab, range(1, n + 1)); keep = np.isin(lab, 1 + np.flatnonzero(size >= 400))
    if not keep.any(): return 0
    keep = nd.binary_dilation(keep, np.ones((3, 3), bool)) & w          # back to the block's edge, never into the photo
    rgba = np.dstack([a, np.where(keep, 0, 255).astype(np.uint8)])
    Image.fromarray(rgba, 'RGBA').save(p, 'WEBP', quality=72, method=4, exact=False)
    return 1


if __name__ == '__main__':
    P = sorted(glob.glob(os.path.join(sys.argv[1], '*', '*', '*.webp')))
    with cf.ProcessPoolExecutor() as ex: n = sum(ex.map(fix, P, chunksize=64))
    print('tiles', len(P), 'made transparent at the edges', n)
