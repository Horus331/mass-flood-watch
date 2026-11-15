"""Figure for the Leominster parametric study (docs/proto/phase1/parametric.json -> docs/proto/phase1/fig/parametric.png)."""
import json, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(f'{ROOT}/docs/proto/phase1/parametric.json'))
R = {r['id']: r for r in D['rows']}
ORDER = [('pm_base', 'Base (as calibrated)'), ('pm_s1', 'Dry soil (AMC I)'), ('pm_s3', 'Wet soil (AMC III)'), ('pm_s2raw', 'Calibration factor removed'),
         ('pm_f', 'Frozen ground'), ('pm_c20', 'All culverts 20 % blocked'), ('pm_c50', 'All culverts 50 % blocked'), ('pm_c100', 'All culverts 100 % blocked'),
         ('pm_ct', 'Smallest third fully blocked'), ('pm_cs', '50 % blocked + wet soil')]
fig, ax = plt.subplots(1, 3, figsize=(12.5, 4.6), sharey=True, gridspec_kw=dict(wspace=0.08))
y = list(range(len(ORDER)))[::-1]; lab = [o[1] for o in ORDER]
c_base, c_ink = '#9aa0a6', '#1a73e8'
def bars(a, key, title, ref=None, fmt='{:.0f}'):
    v = [R[i][key] for i, _ in ORDER]
    a.barh(y, v, color=[c_base if i == 'pm_base' else c_ink for i, _ in ORDER], height=0.62)
    if ref is not None: a.axvline(ref, color='#5f6368', lw=1, ls=(0, (3, 3)))
    for yy, vv in zip(y, v): a.text(vv, yy, ' ' + fmt.format(vv), va='center', fontsize=9, color='#202124')
    a.set_title(title, fontsize=10.5, loc='left'); a.spines[['top', 'right']].set_visible(False); a.tick_params(labelsize=9)
    a.set_xlim(0, max(v) * 1.22)
bars(ax[0], 'flagged', 'Road segments closed (p ≥ 0.5)', R['pm_base']['flagged'])
bars(ax[1], 'reports_hit', f"Storm reports matched (of {R['pm_base']['reports']})", R['pm_base']['reports_hit'])
bars(ax[2], 'dpw_hit', f"City DPW damage points matched (of {R['pm_base']['dpw']})", R['pm_base']['dpw_hit'])
ax[0].set_yticks(y); ax[0].set_yticklabels(lab)
fig.suptitle('Leominster, 11–12 Sep 2023: one condition changed at a time (in-sample sensitivity, not a skill test)', x=0.01, ha='left', fontsize=11.5)
fig.text(0.01, -0.02, 'Source: LISFLOOD-FP 8.2 runs on the calibration storm, 20 m, MRMS radar rain; pre-registered in docs/proto/phase1/PARAMETRIC_PREREG.md. Dashed line = base.', fontsize=8.5, color='#5f6368')
os.makedirs(f'{ROOT}/docs/proto/phase1/fig', exist_ok=True)
fig.savefig(f'{ROOT}/docs/proto/phase1/fig/parametric.png', dpi=200, bbox_inches='tight'); print('wrote docs/proto/phase1/fig/parametric.png')
