"""Figures for the parametric clean rerun (docs/proto/phase1/PARAMETRIC_CLEAN_PREREG.md), from parametric_clean.json.

    python proto/parametric_clean_figs.py
    -> docs/proto/phase1/fig/parametric_clean_bars.png   (Fig. 1: change from base, closed road length and residents losing access)
       docs/proto/phase1/fig/parametric_clean_culverts.png (Fig. 2: top-10 inspection culverts on the MassGIS 2023 orthophoto)
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker, matplotlib.transforms
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PH = f'{ROOT}/docs/proto/phase1'; FIG = f'{PH}/fig'
INK, INK2, GRID, SURF = '#0b0b0b', '#52514e', '#d9d8d4', '#ffffff'
UP, DOWN = '#2a78d6', '#eb6834'          # increase / decrease from base (blue / orange); values are also printed
COND = {'Collapsing': '#d03b3b', 'Broken': '#d03b3b', 'Rusted Through': '#d03b3b', 'Critical': '#d03b3b', 'Poor': '#ec835a', 'Eroding': '#ec835a',
        'Fair': '#fab219', 'OK': '#0ca30c', 'Good': '#0ca30c', 'Excellent': '#0ca30c', 'New': '#0ca30c'}
NA = '#9a9993'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.edgecolor': GRID, 'axes.labelcolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK, 'savefig.dpi': 300, 'savefig.bbox': 'tight', 'savefig.facecolor': SURF})


def bars(J):
    R = [r for r in J['rows'] if r['id'] != 'B']; B = next(r for r in J['rows'] if r['id'] == 'B')
    panels = [('closed_any_km', 'Change in closed road length (km)', f"Base: {B['closed_any_km']:.0f} km of road closed at some time", 1),
              ('pop_lost_any', 'Change in residents losing timely access\n(hospital 30 min, fire 8 min, police 4 min)',
               f"Base: {B['pop_lost_any']:,} residents at the peak", 0)]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    for ax, (k, xl, note, dec) in zip(axes, panels):
        d = sorted(((r[k] - B[k], r['scenario']) for r in R if r.get(k) is not None), key=lambda t: t[0])
        v = [a for a, _ in d]; lab = [b for _, b in d]; y = np.arange(len(v))
        ax.barh(y, v, height=0.62, color=[UP if a > 0 else DOWN for a in v], edgecolor=SURF, linewidth=2)
        ax.axvline(0, color=INK2, lw=1); ax.set_yticks(y, lab); ax.set_xlabel(xl)
        span = max(abs(min(v + [0])), abs(max(v + [0]))) or 1
        for yi, a in zip(y, v):
            s = (f'{a:+.1f}' if dec else f'{a:+,.0f}').replace('-', '−')
            if a < 0:   # bars to the left: the value sits just right of the zero line, so it never meets the row label
                ax.text(0.02 * span, yi, s, va='center', ha='left', fontsize=9, color=INK)
            else:
                ax.text(a + (0.02 * span if a >= 0 else -0.02 * span), yi, s, va='center', ha='left' if a >= 0 else 'right', fontsize=9, color=INK)
        ax.set_xlim(min(v + [0]) - 0.12 * span, max(v + [0]) + 0.25 * span)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'.replace('-', '−')))
        ax.grid(axis='x', color=GRID, lw=0.6); ax.set_axisbelow(True)
        for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
        ax.set_title(note, fontsize=9, color=INK2, loc='left')
    fig.suptitle('Leominster, 11 September 2023: effect of each condition compared with the base model', x=0.01, ha='left', fontsize=12, color=INK)
    fig.tight_layout(); fig.savefig(f'{FIG}/parametric_clean_bars.png'); plt.close(fig)


def culverts(J, key='C100'):
    from pyproj import Transformer
    T = J['inspection'][key]['top']; tr = Transformer.from_crs(4326, 26986, always_xy=True)
    xy = np.array([tr.transform(d['lon'], d['lat']) for d in T])
    img = Image.open(f'{FIG}/aerial_leominster_box_5m.jpg'); X0, Y1, PX = 162000, 928000, 5.0
    med = np.median(xy, 0); far = np.hypot(*(xy - med).T) > 10000          # a culvert far from the rest is listed, with an arrow at the edge
    core = xy[~far] if (~far).sum() >= 2 else xy
    pad = 700; x0, x1 = core[:, 0].min() - pad, core[:, 0].max() + pad; y0, y1 = core[:, 1].min() - pad, core[:, 1].max() + pad
    side = max(x1 - x0, y1 - y0); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2   # square crop: the map panel is square
    x0, x1, y0, y1 = cx - side / 2, cx + side / 2, cy - side / 2, cy + side / 2
    XE, YB = X0 + img.width * PX, Y1 - img.height * PX           # keep the square inside the photo (shift, do not shrink)
    sx = max(0, X0 - x0) - max(0, x1 - XE); sy = max(0, YB - y0) - max(0, y1 - Y1)
    x0, x1, y0, y1 = x0 + sx, x1 + sx, y0 + sy, y1 + sy; cx, cy = cx + sx, cy + sy
    crop = img.crop((int((x0 - X0) / PX), int((Y1 - y1) / PX), int((x1 - X0) / PX), int((Y1 - y0) / PX)))
    a = np.asarray(crop).astype(float) / 255; a = 0.55 + 0.45 * a    # lighten so markers read
    fig = plt.figure(figsize=(12, 7.5)); ax = fig.add_axes([0.01, 0.02, 0.6, 0.96])
    ax.imshow(a, extent=(x0, x1, y0, y1), aspect='auto'); ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color(GRID)
    # markers closer than ~250 m are fanned out on short leader lines so every number stays readable
    pos = xy.copy(); R = 0.035 * side
    for i in range(len(pos)):
        for j in range(i):
            if not far[i] and not far[j] and np.hypot(*(pos[i] - pos[j])) < R:
                ang = np.pi / 4 + j * 0.9; pos[i] = xy[i] + 1.1 * R * np.array([np.cos(ang), np.sin(ang)])
    for i, (d, (x, y), (px, py)) in enumerate(zip(T, xy, pos), 1):
        col = COND.get(str(d['naacc_condition']), NA)
        if far[i - 1]:   # off the map: arrow on the edge pointing to it, with its distance
            dx, dy = x - cx, y - cy; k = 0.46 * side / max(abs(dx), abs(dy)); ex, ey = cx + dx * k, cy + dy * k
            ax.annotate('', xy=(cx + dx * k * 1.06, cy + dy * k * 1.06), xytext=(ex, ey), arrowprops=dict(arrowstyle='-|>', color=INK, lw=1.5))
            ax.scatter([ex], [ey], s=330, color=col, edgecolor='white', linewidth=2, zorder=3)
            ax.text(ex, ey, str(i), ha='center', va='center', fontsize=9, color='white', fontweight='bold', zorder=4)
            ax.text(ex, ey + 0.035 * side, f"{np.hypot(dx, dy) / 1000:.0f} km", ha='center', fontsize=8.5, color=INK, zorder=4)
            continue
        if (px, py) != (x, y): ax.plot([x, px], [y, py], color='white', lw=1.6, zorder=2); ax.scatter([x], [y], s=18, color=INK, zorder=2)
        ax.scatter([px], [py], s=330, color=col, edgecolor='white', linewidth=2, zorder=3)
        ax.text(px, py, str(i), ha='center', va='center', fontsize=9, color='white', fontweight='bold', zorder=4)
    sb = 1000; bx, by = x1 - sb - 0.04 * (x1 - x0), y0 + 0.04 * (y1 - y0)
    ax.plot([bx, bx + sb], [by, by], color=INK, lw=3, solid_capstyle='butt'); ax.text(bx + sb / 2, by + 0.015 * (y1 - y0), '1 km', ha='center', fontsize=9)
    ax.text(x1 - 0.03 * (x1 - x0), y1 - 0.05 * (y1 - y0), 'N ↑', ha='right', fontsize=10, color=INK)
    tx = fig.add_axes([0.64, 0.0, 0.36, 1.0]); tx.axis('off')
    fig.text(0.64, 0.965, 'Culverts to inspect first', fontsize=13, color=INK, va='top')
    fig.text(0.64, 0.925, 'Ranked by added water above the road when the culvert\nis fully blocked (Leominster, 11 September 2023 storm)', fontsize=9, color=INK2, va='top')
    yy = 0.84
    for i, d in enumerate(T, 1):
        col = COND.get(str(d['naacc_condition']), NA)
        tx.scatter([0.03], [yy], s=170, color=col, edgecolor='white', linewidth=1.5, transform=tx.transAxes, clip_on=False)
        tx.text(0.03, yy, str(i), ha='center', va='center', fontsize=8, color='white', fontweight='bold', transform=tx.transAxes)
        road = d['road'] if d['road'] and d['road'].lower() != 'unknown' else 'unnamed road'
        tx.text(0.09, yy + 0.012, f"{road}, {d['town']}", fontsize=9.5, color=INK, va='center', transform=tx.transAxes)
        tx.text(0.09, yy - 0.022, f"+{d['added_over_crest_m']:.1f} m over the road · condition: {d['naacc_condition']}", fontsize=8.5, color=INK2,
                va='center', transform=tx.transAxes)
        yy -= 0.074
    leg = [('Broken / collapsing', COND['Critical']), ('Poor / eroding', COND['Poor']), ('Fair', COND['Fair']), ('OK / good', COND['OK']), ('Not assessed', NA)]
    for j, (n, c) in enumerate(leg):
        tx.scatter([0.03 + 0.33 * (j % 3)], [0.075 - 0.03 * (j // 3)], s=60, color=c, transform=tx.transAxes, clip_on=False)
        tx.text(0.06 + 0.33 * (j % 3), 0.075 - 0.03 * (j // 3), n, fontsize=8, va='center', color=INK2, transform=tx.transAxes)
    tx.text(0, 0.015, 'Condition: NAACC field assessment. Photo: MassGIS 2023.', fontsize=7.5, color=INK2, transform=tx.transAxes)
    fig.savefig(f'{FIG}/parametric_clean_culverts.png', bbox_inches=matplotlib.transforms.Bbox([[0, 0], [12, 7.5]])); plt.close(fig)


if __name__ == '__main__':
    J = json.load(open(f'{PH}/parametric_clean.json')); os.makedirs(FIG, exist_ok=True)
    bars(J)
    if os.path.exists(f'{FIG}/aerial_leominster_box_5m.jpg') and 'inspection' in J: culverts(J)
    print('figures written')
