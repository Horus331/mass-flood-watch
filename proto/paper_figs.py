"""Paper 1 figures from committed JSON only (docs/proto/paper/OUTLINE.md §6, item 5 of §9).

    python proto/paper_figs.py            # writes docs/proto/paper/fig/*.png and fig/figures.json (the numbers plotted)

Fig. 5  held-out District 3: site recall against flagged share, with 90 % CI and chance (obs/round2/score_round2.json, parity:heldout23)
Fig. 6  benchmark v3: top-3 % site recall of the model, the π ranking and six baselines, District 3 held-out 23 and Districts 4-6 (81)
        (scoring/benchmark_v3.json), with the paired-bootstrap verdict of model minus each baseline
Fig. 4  CN-scale calibration (scoring/leo48_cn0*/score.json if present, else parity/BASELINE.md table)
Fig. 11 Leominster deep dive (re-uses proto/phase1_figure.py)
"""
import glob, json, os, subprocess, sys
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P = f'{ROOT}/docs/proto'; OUT = f'{P}/paper/fig'
INK, MUTED, GRID = '#222222', '#6b6b6b', '#e4e4e4'
C_MODEL, C_PI, C_BASE, C_CHANCE = '#1f5f99', '#0b8a6f', '#a9a9a9', '#c0392b'
plt.rcParams.update({'font.size': 9, 'axes.edgecolor': '#999', 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED})
NUM = {}


def fig5():
    d = json.load(open(f'{P}/obs/round2/score_round2.json'))['pools']['parity:heldout23']['box']
    sh = [0.01, 0.02, 0.03, 0.05, 0.10]; k = [f'share_{s:g}' if f'share_{s:g}' in d['point'] else f'share_{s}' for s in sh]
    y = [d['point'][x]['site_recall'] for x in k]; ch = [d['point'][x]['chance'] for x in k]
    lo = [d['ci90'][x]['site_recall'][0] for x in k]; hi = [d['ci90'][x]['site_recall'][1] for x in k]
    r = d['point']['rule']; rlo, rhi = d['ci90']['rule']['site_recall']
    fig, ax = plt.subplots(figsize=(5.2, 3.6), dpi=200)
    x = [100 * s for s in sh]
    ax.fill_between(x, lo, hi, color=C_MODEL, alpha=0.15, lw=0)
    ax.plot(x, y, '-o', color=C_MODEL, ms=4, lw=1.8, label='model, ranked by peak depth')
    ax.plot(x, ch, '--', color=C_CHANCE, lw=1.2, label='chance (random flagging)')
    RR = [u for u in json.load(open(f'{P}/obs/round2/score_round2.json'))['runs'] if u['storm'] in d['storms'] and '/parity/' in u['run']]
    nseg = sum(u['domains']['box']['n_segments'] for u in RR)
    share_rule = 100 * float(np.mean([u['domains']['box']['f0'] for u in RR]))      # storm mean, as in LABELS_ROUND2 / OUTLINE
    ax.errorbar([share_rule], [r['site_recall']], yerr=[[r['site_recall'] - rlo], [rhi - r['site_recall']]], fmt='D', color=INK, ms=5, capsize=3,
                label=f"30 cm rule ({share_rule:.2f} % flagged)")
    ax.set_xlabel('share of road segments flagged (%)'); ax.set_ylabel('share of documented sites caught')
    ax.set_xlim(0, 10.5); ax.set_ylim(0, max(hi) * 1.1); ax.grid(color=GRID, lw=0.6); ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc='upper left')
    ax.set_title(f"Held-out District 3: 23 storms, {d['n_sites']} sites (90 % CI, storm-clustered bootstrap)", fontsize=9, loc='left')
    fig.tight_layout(); fig.savefig(f'{OUT}/fig5_heldout_recall.png'); plt.close(fig)
    NUM['fig5'] = dict(source='obs/round2/score_round2.json pools.parity:heldout23.box', shares=sh, recall=y, ci90=list(zip(lo, hi)), chance=ch,
                       rule=dict(recall=r['site_recall'], ci90=[rlo, rhi], share_pct=share_rule, lift=r['lift']))


def fig6():
    B = json.load(open(f'{P}/scoring/benchmark_v3.json'))
    order = ['P', 'M', 'B6', 'B3', 'B5', 'B2', 'B1', 'B4']
    lab = {'P': 'model, ranked by chance of flooding π', 'M': 'model, ranked by peak depth', 'B6': 'static hazard × vulnerability × consequence',
           'B3': 'MassDOT repeat flood points', 'B5': 'terrain only (HAND)', 'B2': 'FEMA 100-yr zone', 'B1': 'NWS flash-flood warnings',
           'B4': 'radar rain threshold'}
    sets = [('test1_d3_heldout23', 'District 3, 23 held-out storms'), ('test2_d456_81', 'Districts 4–6, 81 storms (never tuned on)')]
    fig, axs = plt.subplots(1, 2, figsize=(9.8, 3.9), dpi=200); NUM['fig6'] = {}
    for ax, (sk, title) in zip(axs, sets):
        S = B['sets'][sk]; M = S['methods']; MB = S.get('model_minus_baseline', {}); rows = order
        v = [M[m]['site_recall_3pct'] if m in M else 0.0 for m in rows]; chance = M['M']['chance_3pct']
        cols = [C_PI if m == 'P' else C_MODEL if m == 'M' else C_BASE for m in rows]
        yy = np.arange(len(rows))[::-1]
        ax.barh(yy, v, color=cols, height=0.62)
        ax.axvline(chance, color=C_CHANCE, ls='--', lw=1.1); ax.text(chance, -0.75, f' chance {chance:.2f}', color=C_CHANCE, fontsize=7.5, va='center')
        for yi, m, vi in zip(yy, rows, v):
            if m not in M: ax.text(0.005, yi, 'not available (District 3 list only)', va='center', fontsize=7.5, color=MUTED); continue
            tag = ''
            if m not in ('M', 'P') and m in MB and 'recall_3pct' in MB[m]:
                t = MB[m]['recall_3pct']; tag = ('  model better' if t['model_better'] else '  baseline better') if t['significant'] else '  n.s.'
            ax.text(vi + 0.005, yi, f'{vi:.2f}{tag}', va='center', fontsize=7.5, color=INK if m in ('M', 'P') else MUTED)
        ax.set_yticks(yy); ax.set_yticklabels([lab[m] for m in rows] if ax is axs[0] else []); ax.set_xlim(0, 0.42); ax.set_ylim(-1.1, len(rows) - 0.5)
        ax.set_title(f"{title}: {M['M']['sites']} sites", fontsize=9, loc='left'); ax.set_xlabel('share of sites caught in the top 3 % of segments')
        ax.grid(axis='x', color=GRID, lw=0.6); ax.spines[['top', 'right']].set_visible(False); ax.set_axisbelow(True)
        NUM['fig6'][sk] = dict(recall_3pct={m: M[m]['site_recall_3pct'] for m in rows if m in M}, chance=chance,
                               model_minus_baseline={m: MB[m].get('recall_3pct') for m in MB if 'recall_3pct' in MB[m]})
    fig.text(0.01, 0.01, 'Verdicts: 95 % paired bootstrap over storms of model (depth) minus baseline (benchmark v3, PROTOCOL v3). '
             'π ranking adopted after this benchmark (PI_RANK_v3).', fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(f'{OUT}/fig6_benchmark.png'); plt.close(fig)


def fig4():
    rows = []
    for f in sorted(glob.glob(f'{P}/scoring/leo48_cn0*/score.json')) + sorted(glob.glob(f'{P}/parity/calib/leo48_cn0*/score.json')):
        s = json.load(open(f)); cn = int(f.split('leo48_cn')[1][:3]) / 100
        G = {g['name'].split(' AT ')[-1].split(',')[0].title(): g['rise_error_m'] for g in s['gauges']}
        rows.append((cn, s['mean_abs_rise_error_m'], tuple(sorted(G.items()))))
    if not rows: print('fig4: no calibration score files with gauges; skipped'); return
    rows = sorted(dict((r[0], r) for r in rows).values()); cn, err, G = zip(*rows)
    fig, ax = plt.subplots(figsize=(4.8, 3.3), dpi=200)
    ax.plot(cn, err, '-o', color=C_MODEL, ms=4, lw=1.8, label='mean |error|')
    for nm, ls in zip(sorted(dict(G[0])), (':', '--', '-.')):
        ax.plot(cn, [dict(g)[nm] for g in G], ls, color=MUTED, lw=1, label=f'{nm} (signed)')
    ax.axhline(0, color='#bbb', lw=0.6); ax.axvline(0.88, color=INK, lw=0.8, ls=':'); ax.text(0.882, max(err) * 0.95, 'chosen 0.88', fontsize=7.5)
    ax.legend(frameon=False, fontsize=7.5)
    ax.set_xlabel('pervious curve-number scale'); ax.set_ylabel('gauge rise error (m)'); ax.grid(color=GRID, lw=0.6)
    ax.spines[['top', 'right']].set_visible(False); ax.set_title('CN-scale calibration, Leominster box, Sept 2023', fontsize=9, loc='left')
    fig.tight_layout(); fig.savefig(f'{OUT}/fig4_cn_scale.png'); plt.close(fig)
    NUM['fig4'] = dict(source='parity/calib/leo48_cn0*/score.json', cn=cn, mean_abs_rise_error_m=err, signed_by_gauge=[dict(g) for g in G])


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in (fig5, fig6, fig4):
        try: f()
        except Exception as e: print(f.__name__, 'failed:', repr(e)[:300])
    subprocess.run([sys.executable, f'{ROOT}/proto/phase1_figure.py'], check=False)
    json.dump(NUM, open(f'{OUT}/figures.json', 'w'), indent=1, default=float); print('figures in', OUT, sorted(os.listdir(OUT)))


if __name__ == '__main__':
    main()
