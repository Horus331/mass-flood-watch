"""Slide figure: the 5-7 Nov 2026 storm, forecast 'likely' closures by cycle vs the radar replay and reports.
Data: docs/proto/prospective/ledger.csv (likely / possible per cycle), storm_2026-11-06_watch.md (radar replays, reports)."""
import csv, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = [r for r in csv.DictReader(open(f'{ROOT}/docs/proto/prospective/ledger.csv')) if '2026-11-05T00' <= r['issued'] <= '2026-11-07T00:00Z']
lab = []; L = []; Pz = []; v2 = []
for r in R:
    t = r['issued']; lab.append(f"{t[8:10]} Nov {t[11:13]}Z"); L.append(int(r['likely_closed'] or 0)); Pz.append(int(r['possible'] or 0)); v2.append('T2' in r['settings'])
fig, ax = plt.subplots(figsize=(9.6, 4.0), dpi=200)
x = range(len(R))
ax.bar(x, L, color=['#1f5f99' if v else '#7fa7cc' for v in v2], width=0.6, label='forecast "likely" closures (2+ of 8 members)')
for i, (l, p) in enumerate(zip(L, Pz)): ax.text(i, l + 0.6, f'{l}\n({p} possible)', ha='center', fontsize=7.5, color='#333')
ax.axhline(8, color='#e67e22', ls='--', lw=1.3); ax.axhline(0.15, color='#c0392b', lw=2.2)
ax.set_xticks(list(x)); ax.set_xticklabels(lab, fontsize=8); ax.set_ylabel('road segments'); ax.set_ylim(0, 41)
ax.spines[['top', 'right']].set_visible(False); ax.grid(axis='y', color='#e6e6e6', lw=0.6); ax.set_axisbelow(True)
ax.set_title('Storm of 5–7 Nov 2026: every cycle from 5 Nov 06Z to 6 Nov 12Z forecast closures; none were reported', fontsize=10, loc='left')
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
ax.legend(handles=[Patch(color='#7fa7cc', label='forecast "likely" closures, model v1 (before the 5 Nov start-state fix)'),
                   Patch(color='#1f5f99', label='forecast "likely" closures, model v2 (live from 6 Nov 00Z)'),
                   Line2D([], [], color='#e67e22', ls='--', lw=1.3, label='same model on the observed radar rain, live rules: 8 segments'),
                   Line2D([], [], color='#c0392b', lw=2.2, label='flood / closure reports in District 3: 0')],
          frameon=False, fontsize=8, loc='upper right')
fig.text(0.01, 0.01, 'HRRR cycle (UTC). 5 Nov 18Z was computed but lost at the publish step. Sources: docs/proto/prospective/ledger.csv, storm_2026-11-06_watch.md.', fontsize=7, color='#666')
fig.tight_layout(rect=(0, 0.03, 1, 1)); out = f'{ROOT}/docs/proto/prospective/fig/storm_2026-11-06_slide.png'; fig.savefig(out); print(out, list(zip(lab, L, Pz)))
