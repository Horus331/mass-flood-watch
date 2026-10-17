"""Make small 'overview' copies of water frames so thin streams of water stay visible when the map is zoomed out.

Each block of F x F cells keeps its deepest (most opaque) cell, so a 50 m stream still shows as a 300 m line at state scale
instead of being averaged away. Writes o000.png ... next to f000.png and sets meta['pool'] = F.

Usage: python sim/pool_frames.py fm00 fm01 ...   (or no arguments: every scene whose name starts with fm or cm_)
"""
import os, sys, json, glob
import numpy as np
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'sim')
F = 6


def pool(path_in, path_out):
    a = np.asarray(Image.open(path_in).convert('RGBA'))
    h, w = a.shape[:2]; H, W = -(-h // F), -(-w // F)
    p = np.zeros((H * F, W * F, 4), np.uint8); p[:h, :w] = a
    b = p.reshape(H, F, W, F, 4).transpose(0, 2, 1, 3, 4).reshape(H, W, F * F, 4)
    k = b[..., 3].argmax(-1)
    out = np.take_along_axis(b, k[..., None, None], 2)[:, :, 0].copy()
    frac = (b[..., 3] > 0).mean(-1)                       # share of the block that is wet: one wet cell gives a faint block, a full block a solid one
    out[..., 3] = (out[..., 3] * np.clip(np.sqrt(frac) * 1.6, 0, 1)).astype(np.uint8)
    Image.fromarray(out, 'RGBA').save(path_out, optimize=True)


def run(name):
    d = os.path.join(ROOT, name); mp = os.path.join(d, 'meta.json')
    if not os.path.exists(mp):
        return
    m = json.load(open(mp))
    for f in sorted(glob.glob(os.path.join(d, 'f[0-9][0-9][0-9].png'))):
        pool(f, os.path.join(d, 'o' + os.path.basename(f)[1:]))
    if os.path.exists(os.path.join(d, 'max.png')):
        pool(os.path.join(d, 'max.png'), os.path.join(d, 'omax.png'))
    m['pool'] = F
    json.dump(m, open(mp, 'w'), separators=(',', ':'))
    print(name, 'pooled', m.get('n'))


if __name__ == '__main__':
    names = sys.argv[1:] or sorted(n for n in os.listdir(ROOT) if n.startswith(('fm', 'cm_')))
    for n in names:
        run(n)
