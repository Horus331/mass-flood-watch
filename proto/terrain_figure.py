"""Before / after peak-depth maps for the terrain-conditioning candidates (docs/proto/terrain/TERRAIN.md).

    python proto/terrain_figure.py --run aug2021_worcester_20m --arms base t1 t2 --window 174300,177300,888800,892600 --title "..." --out fig.png
Reads docs/proto/terrain/runs/<arm>/<run>/hmax_cm.npz + flood_meta.json; road centrelines from docs/graph_segments.json."""
import os, sys, json, argparse
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'sim', 'infra'))
LABEL = {'base': 'deployed (before)', 't1': 'T1 notch fix', 't2': 'T2 notch fix + buried-stream conveyance', 'b0': 'B0'}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--run', required=True); ap.add_argument('--arms', nargs='+', default=['base', 't1', 't2'])
    ap.add_argument('--window', required=True); ap.add_argument('--title', default=''); ap.add_argument('--out', required=True)
    ap.add_argument('--vmax', type=float, default=2.0)
    a = ap.parse_args(); X0, X1, Y0, Y1 = (float(v) for v in a.window.split(','))
    import impacts as IM
    SG = json.load(open(os.path.join(ROOT, 'docs', 'graph_segments.json')))
    fig, axs = plt.subplots(1, len(a.arms), figsize=(5.2 * len(a.arms), 5.4), squeeze=False)
    for ax, arm in zip(axs[0], a.arms):
        d = os.path.join(ROOT, 'docs', 'proto', 'terrain', 'runs', arm, a.run)
        meta = json.load(open(os.path.join(d, 'flood_meta.json'))); x0, y0, x1, y1 = meta['box']; R = meta['res_m']
        H = np.load(os.path.join(d, 'hmax_cm.npz'))['hmax_cm'].astype(np.float32) / 100.0
        r0, r1, c0, c1 = int((y1 - Y1) // R), int((y1 - Y0) // R), int((X0 - x0) // R), int((X1 - x0) // R)
        im = ax.imshow(np.where(H[r0:r1, c0:c1] > 0.05, H[r0:r1, c0:c1], np.nan), extent=[x0 + c0 * R, x0 + c1 * R, y1 - r1 * R, y1 - r0 * R],
                       cmap='Blues', vmin=0, vmax=a.vmax)
        P = IM.road_points(SG, meta); m = (P['x'] > X0) & (P['x'] < X1) & (P['y'] > Y0) & (P['y'] < Y1)
        ax.scatter(P['x'][m], P['y'][m], s=0.15, c='0.4')
        ax.set_title(f"{LABEL.get(arm, arm)}\nwater > 1 m: {int((H[r0:r1, c0:c1] > 1).sum())} cells, max {H[r0:r1, c0:c1].max():.1f} m", fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(im, ax=axs[0].tolist(), shrink=0.8, label='peak water depth (m)')
    fig.suptitle(a.title, fontsize=10); plt.savefig(a.out, dpi=90, bbox_inches='tight')


if __name__ == '__main__':
    main()
