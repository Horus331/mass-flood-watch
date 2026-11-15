"""Slide figure for the Leominster deep dive (docs/proto/phase1/LEOMINSTER_MISSES.md): DPW damage points hit / missed on the model's
flagged roads, and the peak depth the model put at each.   python proto/phase1_figure.py"""
import csv, json, os
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = json.load(open(f'{ROOT}/docs/proto/phase1/leominster_misses.json'))
LL = {r['id']: (float(r['lon']), float(r['lat'])) for r in csv.DictReader(open(f'{ROOT}/proto/data/labels_sep2023_leominster_dpw.csv'))}
G = json.load(open(f'{ROOT}/docs/proto/parity/catalog/sep2023_leominster_20m/segments.geojson'))
P = J['points']; lon = np.array([LL[p['id']][0] for p in P]); lat = np.array([LL[p['id']][1] for p in P])
pad = 0.008; bx = (lon.min() - pad, lon.max() + pad, lat.min() - pad, lat.max() + pad)
def cat(p):
    if p['cls_amended'] == 'hit': return 'hit'
    return 'crossing' if p['cls_amended'] == 'culvert' else 'edge'
C = {'hit': '#1b7837', 'edge': '#d6604d', 'crossing': '#4393c3'}
L = {'hit': 'found (flagged road within 30 m)', 'edge': 'missed: little water, not at a crossing (edge erosion)', 'crossing': 'missed: at a stream crossing'}
fig = plt.figure(figsize=(13.33, 6.4), dpi=150)
ax = fig.add_axes([0.02, 0.25, 0.50, 0.67]); ax2 = fig.add_axes([0.60, 0.16, 0.37, 0.72])
for f in G['features']:
    g = f['geometry']; parts = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
    flag = (f['properties'].get('p_close') or 0) >= 0.5
    for line in parts:
        a = np.array(line)
        if a[:, 0].max() < bx[0] or a[:, 0].min() > bx[1] or a[:, 1].max() < bx[2] or a[:, 1].min() > bx[3]: continue
        ax.plot(a[:, 0], a[:, 1], color='#222' if flag else '#c8c8c8', lw=1.6 if flag else 0.5, zorder=2 if flag else 1)
for k in ('hit', 'crossing', 'edge'):
    m = np.array([cat(p) == k for p in P])
    ax.scatter(lon[m], lat[m], s=46, c=C[k], edgecolor='white', lw=0.8, zorder=5)
ax.set_xlim(bx[0], bx[1]); ax.set_ylim(bx[2], bx[3]); ax.set_aspect(1 / np.cos(np.radians(lat.mean()))); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_color('#999')
n = {k: sum(cat(p) == k for p in P) for k in C}
h = [Line2D([], [], color='#222', lw=1.6, label='road flagged by the model (≥ 30 cm)'), Line2D([], [], color='#c8c8c8', lw=1, label='other roads')]
h += [Line2D([], [], marker='o', ls='', mfc=C[k], mec='white', ms=8, label=f'{L[k]}: {n[k]}') for k in ('hit', 'crossing', 'edge')]
ax.legend(handles=h, loc='upper left', bbox_to_anchor=(0.0, -0.01), fontsize=8.5, frameon=False, ncol=1)
ax.set_title('City of Leominster DPW damage points, 11 Sep 2023 (54)', fontsize=12, loc='left')
ax.annotate('Wachusett St: 32 points\n(25 of the 27 non-crossing misses)', xy=(-71.796, 42.4985), xytext=(-71.787, 42.4885), fontsize=8.5, arrowprops=dict(arrowstyle='-', color='#666', lw=0.8), color='#333', bbox=dict(fc='white', ec='none', alpha=0.85, pad=1.5))
d = {k: [100 * (p['peak_depth_m'] or 0) for p in P if cat(p) == k] for k in C}
rng = np.random.default_rng(0)
for i, k in enumerate(('hit', 'crossing', 'edge')):
    y = np.array(d[k]); x = i + rng.uniform(-0.18, 0.18, len(y))
    ax2.scatter(x, np.maximum(y, 0.5), s=30, c=C[k], alpha=0.85, edgecolor='white', lw=0.5)
    ax2.plot([i - 0.28, i + 0.28], [max(np.median(y), 0.5)] * 2, color='#222', lw=2)
    ax2.text(i, 400, f'median {np.median(y):.0f} cm' if np.median(y) >= 1 else f'median {np.median(y):.1f} cm', ha='center', fontsize=9)
ax2.axhline(30, color='#888', ls='--', lw=1); ax2.text(2.45, 33, '30 cm closure depth', ha='right', fontsize=8, color='#555')
ax2.set_yscale('log'); ax2.set_ylim(0.4, 700); ax2.set_xticks([0, 1, 2]); ax2.set_xticklabels(['found', 'missed:\nat a crossing', 'missed:\nedge erosion'])
ax2.set_ylabel('peak water depth the model put there (cm, log)'); ax2.spines[['top', 'right']].set_visible(False)
ax2.set_title('The misses had almost no modelled water', fontsize=12, loc='left')
fig.text(0.60, 0.02, 'LISFLOOD-FP 20 m on radar rain; calibration storm (in-sample).\nSource: docs/proto/phase1/LEOMINSTER_MISSES.md', fontsize=7.5, color='#555')
out = f'{ROOT}/docs/proto/phase1/fig/leominster_deep_dive.png'; fig.savefig(out); print(out, n)
