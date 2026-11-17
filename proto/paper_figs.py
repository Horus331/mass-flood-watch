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


def fig1():
    from matplotlib.patches import Rectangle
    LOCKED = ('aug2015', 'aug2018', 'aug2020', 'jul2018', 'oct2016'); DEV = ('sep2023', 'aug2021')
    G = json.load(open(f'{ROOT}/docs/graph_segments.json'))
    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=200)
    for seg in G['geo']:
        for part in seg:
            a = np.array(part, float); xy = np.cumsum(a.reshape(-1, 2), axis=0) / 1e5
            ax.plot(xy[:, 0], xy[:, 1], color='#cfcfcf', lw=0.25, zorder=1)
    n = {'dev': 0, 'held': 0, 'd456': 0}
    for e in json.load(open(f'{P}/obs/catalog_d456.json'))['events']:
        x0, y0, x1, y1 = e['bbox_lonlat']; ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc='none', ec='#8c6bb1', lw=0.6, alpha=0.7, zorder=2)); n['d456'] += 1
    for e in json.load(open(f'{P}/obs/catalog.json'))['events']:
        if e['id'] in LOCKED or e['id'] == 'sep2014': continue
        k = 'dev' if e['id'] in DEV else 'held'; n[k] += 1
        x0, y0, x1, y1 = e['bbox_lonlat']
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc='none', ec=C_MODEL if k == 'held' else C_CHANCE, lw=1.3 if k == 'dev' else 0.9, zorder=3))
    ax.set_aspect(1 / np.cos(np.radians(42.3))); ax.set_xlim(-72.5, -69.75); ax.set_ylim(41.3, 42.95)
    ax.set_xlabel('longitude'); ax.set_ylabel('latitude'); ax.spines[['top', 'right']].set_visible(False)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], color='#cfcfcf', lw=1.5, label='MassDOT District 3 road graph (52,698 segments)'),
                       Line2D([], [], color=C_CHANCE, lw=1.3, label=f"development storms ({n['dev']})"),
                       Line2D([], [], color=C_MODEL, lw=1, label=f"held-out District 3 storms ({n['held']})"),
                       Line2D([], [], color='#8c6bb1', lw=0.8, label=f"Districts 4–6 transfer storms ({n['d456']})")],
              frameon=False, fontsize=7.5, loc='lower left')
    ax.set_title('Study area and storm boxes (20 × 20 km each; 5 locked storms not shown)', fontsize=9, loc='left')
    fig.tight_layout(); fig.savefig(f'{OUT}/fig1_study_area.png'); plt.close(fig); NUM['fig1'] = n


def fig3():
    import pandas as pd
    t0 = pd.Timestamp('2023-09-11T16:00Z'); GJ = {g['site']: g for g in json.load(open(f'{P}/obs/gauges_sep2023.json'))['gauges']}
    V = [('sep2023_rain', 'default step (≤ 10 s)', '#c0392b', '-'), ('sep2023_rain_dt1', 'step ≤ 1 s (LF_PARITY)', C_MODEL, '-'),
         ('sep2023_rain_dt05', 'step ≤ 0.5 s', INK, ':')]
    fig, axs = plt.subplots(1, 2, figsize=(9.4, 3.4), dpi=200); NUM['fig3'] = {}
    for ax, site in zip(axs, ('01094400', '01094500')):
        g = GJ[site]; st = [(pd.Timestamp(t).tz_convert('UTC'), v * 0.3048) for t, v in g['stage_ft']]
        pre = np.median([v for t, v in st if t0 - pd.Timedelta(hours=12) <= t <= t0])
        oh = [((t - t0).total_seconds() / 3600, v - pre) for t, v in st if t0 <= t <= t0 + pd.Timedelta(hours=36)]
        ox, oy = [], []
        for (a, b), (c, d) in zip(oh[:-1], oh[1:]):
            ox.append(a); oy.append(b)
            if c - a > 1.0: ox.append(np.nan); oy.append(np.nan)          # gauge record gap: leave it open
        ox.append(oh[-1][0]); oy.append(oh[-1][1])
        ax.plot(ox, oy, color='#999', lw=2.2, label='observed (USGS stage; gaps left open)'); NUM['fig3'][site] = {}
        for v, lab, col, ls in V:
            Z = np.load(f'{P}/parity/{v}/gauge_windows.npz'); D = Z[f'{site}_depth_cm'].astype(float) / 100; wm = Z[f'{site}_wm']; h = Z['hours']
            c = D.shape[1] // 2; k = 3; sub = wm[c - k:c + k + 1, c - k:c + k + 1]
            if sub.any():
                rr, cc = np.nonzero(sub); j = np.argmin((rr - k) ** 2 + (cc - k) ** 2); r_, c_ = rr[j] + c - k, cc[j] + c - k
            else: r_, c_ = np.unravel_index(np.argmax(D.max(0)[c - k:c + k + 1, c - k:c + k + 1]), (2 * k + 1, 2 * k + 1)); r_ += c - k; c_ += c - k
            ms = D[:, r_, c_]; ax.plot(h, ms - ms[0], ls, color=col, lw=1.4, label=lab)
            NUM['fig3'][site][v] = dict(rise_m=float(ms.max() - ms[0]), peak_h=float(h[int(np.argmax(ms))]))
        ax.set_title(g['name'].title().replace(', Ma', ''), fontsize=9, loc='left'); ax.set_xlabel('hours after 16:00 UTC, 11 Sep 2023')
        ax.set_ylabel('stage rise (m)'); ax.grid(color=GRID, lw=0.6); ax.spines[['top', 'right']].set_visible(False); ax.set_xlim(0, 36)
    axs[0].legend(frameon=False, fontsize=7.5)
    fig.tight_layout(); fig.savefig(f'{OUT}/fig3_timestep.png'); plt.close(fig)


def fig7():
    """Sept 2023 District run: peak depth with closed segments, and the cascade over time (turing/d3_sep2023_p/, paper/data/d3_sep2023_cascade.json
    written by `proto/cascade.py pack d3_sep2023`, then moved out of the site folder)."""
    from pyproj import Transformer
    D = f'{P}/turing/d3_sep2023_t2'; meta = json.load(open(f'{D}/flood_meta.json')); S = json.load(open(f'{D}/summary.json'))
    C = json.load(open(f'{P}/paper/data/d3_sep2023_t2_cascade.json')); s = C['series']; t = np.array(C['t_h'])
    h = np.load(f'{D}/hmax_cm.npz')['hmax_cm']; k = 5; ny, nx = h.shape
    hm = h[:ny // k * k, :nx // k * k].reshape(ny // k, k, nx // k, k).max((1, 3)).astype(float) / 100
    x0, y0, x1, y1 = meta['box']
    fig = plt.figure(figsize=(10.4, 5.6), dpi=200); gs = fig.add_gridspec(4, 2, width_ratios=[1.0, 1.15], wspace=0.18, hspace=0.35)
    ax = fig.add_subplot(gs[:, 0])
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cm_ = ListedColormap(['#f4f4f4', '#c6dbef', '#6baed6', '#2171b5', '#08306b']); nm = BoundaryNorm([0, 0.1, 0.3, 0.6, 1.0, 1e3], cm_.N)
    ax.imshow(hm, extent=(x0 / 1e3, x1 / 1e3, y0 / 1e3, y1 / 1e3), cmap=cm_, norm=nm, interpolation='nearest')
    tr = Transformer.from_crs(4326, 26986, always_xy=True); nclosed = 0
    for f in json.load(open(f'{D}/segments.geojson'))['features']:
        if (f['properties'].get('p_close') or 0) < 0.5: continue
        nclosed += 1
        g = f['geometry']; parts = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
        for part in parts:
            xs, ys = tr.transform(*zip(*part)); ax.plot(np.array(xs) / 1e3, np.array(ys) / 1e3, color=C_CHANCE, lw=1.6, solid_capstyle='round')
    ax.set_xlabel('x (km, EPSG:26986)'); ax.set_ylabel('y (km)'); ax.spines[['top', 'right']].set_visible(False)
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    ax.legend(handles=[Patch(color='#c6dbef', label='peak depth 0.1–0.3 m'), Patch(color='#6baed6', label='0.3–0.6 m'), Patch(color='#2171b5', label='0.6–1 m'),
                       Patch(color='#08306b', label='> 1 m'), Line2D([], [], color=C_CHANCE, lw=1.6, label=f'road segment closed at some time (p ≥ 0.5): {nclosed}')],
              frameon=True, framealpha=0.9, fontsize=7, loc='lower left')
    ax.set_title(f"(a) District run, Sept 2023, 20 m ({meta['shape'][0] * meta['shape'][1] / 1e6:.1f} M cells)", fontsize=9, loc='left')
    rain = np.array(S['rain_hourly_mean_mm'], float)
    panels = [('rain (box mean, mm/h)', None), ('road segments closed', [('closed_n', C_CHANCE, 'closed')]),
              ('vehicle-hours lost per hour', [('delay_vehh_per_h', C_MODEL, 'delay (detours + slowed traffic)')]),
              ('residents', [('pop_lost_any', INK, 'losing a hospital, fire or police station in time'), ('pop_lost_dry_segment', MUTED, '… whose own road is dry'),
                             ('pop_isolated', C_PI, 'cut off from every service')])]
    NUM['fig7'] = dict(source='turing/d3_sep2023_t2 + paper/data/d3_sep2023_t2_cascade.json (T2 terrain, deployed readout)', closed_segments_map=nclosed, peak=C['totals']['peak'])
    for i, (yl, ser) in enumerate(panels):
        a = fig.add_subplot(gs[i, 1])
        if ser is None: a.bar(np.arange(len(rain)) + 0.5, rain, width=0.9, color='#9ecae1')
        else:
            for key, col, lab in ser: a.plot(t, s[key], color=col, lw=1.4, label=lab)
            if len(ser) > 1: a.legend(frameon=False, fontsize=6.5, loc='upper right')
        a.set_xlim(0, max(t.max(), len(rain))); a.grid(color=GRID, lw=0.5); a.spines[['top', 'right']].set_visible(False)
        a.set_ylabel(yl, fontsize=7.5); a.tick_params(labelsize=7)
        if i < 3: a.set_xticklabels([])
        if i == 0: a.set_title('(b) what follows, hours after ' + C['storm_start'].replace('T', ' '), fontsize=9, loc='left')
    a.set_xlabel('hours')
    fig.savefig(f'{OUT}/fig7_district_cascade.png', bbox_inches='tight'); plt.close(fig)


def fig8():
    """Forecast lead time: the four pre-registered ensemble rules, 7 out-of-sample storms, deployed (parity) physics
    (forecast/ensemble_parity.json pooled; forecast/ENSEMBLE_PARITY.md §1-2)."""
    E = json.load(open(f'{P}/forecast/ensemble_parity.json'))['pooled']
    rules = [('single', 'single cycle'), ('any_of_4', 'any of 4'), ('two_of_4', '2 of 4'), ('two_of_8', '2 of 8 (live)')]
    leads = [('oos_long', 'long lead (8–14 h)'), ('oos_short', 'short lead (2–8 h)')]
    fig, axs = plt.subplots(1, 2, figsize=(9.8, 3.6), dpi=200, sharey=True); NUM['fig8'] = dict(source='forecast/ensemble_parity.json pooled')
    for ax, (lk, lt) in zip(axs, leads):
        R = E[lk]['rules']; x = np.arange(len(rules))
        rec = [R[k]['recall'] for k, _ in rules]; fl = [100 * R[k]['mean_flagged_share'] for k, _ in rules]; mx = [100 * R[k]['max_flagged_share'] for k, _ in rules]
        cols = [C_MODEL if k == 'two_of_8' else C_BASE for k, _ in rules]
        ax.bar(x, rec, color=cols, width=0.6)
        for xi, r, f, m, (k, _) in zip(x, rec, fl, mx, rules):
            ax.text(xi, r + 0.01, f"{r:.2f}", ha='center', va='bottom', fontsize=8, color=INK)
        ax.set_xticks(x); ax.set_xticklabels([f"{t}\n{f:.1f} % flagged\n(max {m:.1f} %)" for (_, t), f, m in zip(rules, fl, mx)], fontsize=7.5)
        ax.set_ylim(0, 0.5); ax.grid(axis='y', color=GRID, lw=0.6); ax.spines[['top', 'right']].set_visible(False)
        ax.set_title(f"{lt}: {R['single']['sites']} sites, {R['single']['storms']} storms", fontsize=9, loc='left')
        NUM['fig8'][lk] = {k: dict(recall=R[k]['recall'], mean_flagged_pct=round(100 * R[k]['mean_flagged_share'], 2),
                                   max_flagged_pct=round(100 * R[k]['max_flagged_share'], 2), lift=R[k]['lift']) for k, _ in rules}
    axs[0].set_ylabel('share of documented sites caught')
    fig.tight_layout(); fig.savefig(f'{OUT}/fig8_forecast_rules.png'); plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in (fig1, fig3, fig5, fig6, fig4, fig7, fig8):
        try: f()
        except Exception as e: print(f.__name__, 'failed:', repr(e)[:300])
    subprocess.run([sys.executable, f'{ROOT}/proto/phase1_figure.py'], check=False)
    json.dump(NUM, open(f'{OUT}/figures.json', 'w'), indent=1, default=float); print('figures in', OUT, sorted(os.listdir(OUT)))


if __name__ == '__main__':
    main()
