"""Vermont July 2023 test storm: one table of the closure rules scored against the VTrans closures, plus the gauge checks.

    python proto/vt_report.py --dir docs/proto/vermont_jul2023 [--run-dir <w9 out dir>]

Reads <dir>/summary.json (proto/prototype.py with --labels proto/data/vt_roadclosures_jul2023.geojson), <dir>/score.json (proto/score.py),
<dir>/xings.json (w9 LF_QOUT: modelled peak flow at gauges) and <dir>/inputs/manifest.json; writes <dir>/vt_scores.json and <dir>/RESULTS.md.
Nothing here is tuned: the rules and thresholds are the ones fixed on Leominster (Sept 2023) before this storm was run.
"""
import os, json, argparse

RULES = [('depth', 'depth rule (default p_close)'), ('overtop', 'overtop candidate (water beside the road reaches the crest)'),
         ('freeboard', 'freeboard (water within 0.30 m of the crest)'), ('depth+culvert', 'culvert (depth + HDS-5 culvert overtopping)'),
         ('overtop+culvert', 'overtop + culvert')]
LEOMINSTER = dict(depth=dict(recall=0.385, flagged_share=0.0465, lift=5.83), overtop=dict(recall=0.744, flagged_share=0.098, lift=5.45),
                  freeboard=dict(recall=0.756, flagged_share=0.1425, lift=3.89))


def main(d, run_dir=None):
    S = json.load(open(os.path.join(d, 'summary.json'))); L = (S.get('checks') or {}).get('labels_segments') or {}
    V = L.get('variants') or {}; rows = []
    for k, nm in RULES:
        v = V.get(k)
        if not v: continue
        st, lo = v['strict'], v['loose']; a = st.get('all') or {}; al = lo.get('all') or {}
        rows.append(dict(rule=k, name=nm, closures_matched=a.get('n'), recall=a.get('recall'), flagged_share=st.get('flagged_share'), n_flagged=st.get('n_flagged'),
                         random_recall=a.get('random_recall'), lift=a.get('lift'), lift_naive=a.get('lift_naive'), loose_recall=al.get('recall'), loose_lift=al.get('lift'),
                         flood_only=(st.get('flood_closure') or {}).get('recall'), split=v.get('split_strict'), leominster=LEOMINSTER.get(k)))
    G = json.load(open(os.path.join(d, 'score.json'))) if os.path.exists(os.path.join(d, 'score.json')) else {}
    X = json.load(open(os.path.join(d, 'xings.json'))) if os.path.exists(os.path.join(d, 'xings.json')) else {}
    gq = {g['site']: g for g in X.get('gauges', [])}; gauges = []
    for g in G.get('gauges', []):
        q = gq.get(g['site'], {})
        gauges.append(dict(g, model_peak_q_m3s=q.get('q_peak_m3s'), model_peak_q_h=q.get('q_peak_h')))
    for sid, q in gq.items():
        if sid not in {g['site'] for g in gauges}: gauges.append(dict(site=sid, name=q.get('name'), obs_peak_q_m3s=q.get('obs_peak_q_m3s'), model_peak_q_m3s=q.get('q_peak_m3s')))
    C = json.load(open(os.path.join(d, 'coarse', 'xings.json'))) if os.path.exists(os.path.join(d, 'coarse', 'xings.json')) else {}
    coarse = [dict(site=g['site'], name=g.get('name'), obs_peak_q_m3s=g.get('obs_peak_q_m3s'), model_peak_q_m3s=g.get('q_peak_m3s'), model_peak_h=g.get('q_peak_h'))
              for g in C.get('gauges', []) if not str(g['site']).startswith('IN')]
    IF = json.load(open(os.path.join(d, 'inputs', 'inflows.json'))) if os.path.exists(os.path.join(d, 'inputs', 'inflows.json')) else {}
    inflows = [dict(name=p['name'], area_km2=p.get('area_km2'), edge=p.get('edge'), peak_m3s=p.get('peak_m3s')) for p in IF.get('points', [])]
    M = json.load(open(os.path.join(d, 'inputs', 'manifest.json'))) if os.path.exists(os.path.join(d, 'inputs', 'manifest.json')) else {}
    dep = next((r for r in rows if r['rule'] == 'depth'), None); ot = next((r for r in rows if r['rule'] == 'overtop'), None)
    verdict = None
    if dep and ot and ot['recall'] is not None:
        better = (ot['recall'] or 0) > (dep['recall'] or 0); ok_share = (ot['flagged_share'] or 0) <= 0.10
        verdict = dict(overtop_recall_higher=better, overtop_flags_le_10pct=ok_share, overtop_lift_vs_depth=[ot['lift'], dep['lift']],
                       holds=bool(better and ok_share and (ot['lift'] or 0) >= (dep['lift'] or 0) * 0.8))
    out = dict(storm='July 10-11, 2023 Vermont flood', box_epsg26986=S.get('box_epsg26986'), segments_in_box=S.get('segments_in_box'),
               closures_in_file=L.get('labels_in_file'), closures_matched_strict=L.get('sites_matched'), closures_matched_loose=(L.get('loose') or {}).get('sites_matched'),
               rules=rows, overtop_verdict=verdict, gauges=gauges, coarse_run_gauges=coarse, inflows=inflows, inflow_source=IF.get('source'), rain_max_total_mm=S.get('rain_max_total_mm'), rain_peak1h_max_mm=S.get('rain_peak1h_max_mm'),
               flood_model_runtime_s=S.get('flood_model_runtime_s'), sites=L.get('sites'), inputs=M.get('steps'))
    json.dump(out, open(os.path.join(d, 'vt_scores.json'), 'w'), indent=1)
    T = [f"# Vermont, July 10-11 2023: closure rules vs VTrans closures", '',
         f"Box (EPSG:26986) {S.get('box_epsg26986')}, {S.get('segments_in_box')} OSM road segments; {L.get('sites_matched')} of the closed stretches in the box matched "
         f"to road segments (strict, 30 m); storm rain max {S.get('rain_max_total_mm')} mm, worst hour {S.get('rain_peak1h_max_mm')} mm.", '',
         '| rule | recall (strict) | flagged share | lift (chance-corrected) | loose recall | Leominster (recall / flagged / lift) |', '| --- | --- | --- | --- | --- | --- |']
    for r in rows:
        le = r['leominster']; les = f"{le['recall']} / {100 * le['flagged_share']:.1f} % / {le['lift']}" if le else ''
        T.append(f"| {r['name']} | {r['recall']} ({r['closures_matched']}) | {100 * (r['flagged_share'] or 0):.2f} % | {r['lift']} | {r['loose_recall']} | {les} |")
    if verdict: T += ['', f"Overtop vs depth: recall higher {verdict['overtop_recall_higher']}, flags <= 10 % {verdict['overtop_flags_le_10pct']}, lift {verdict['overtop_lift_vs_depth']}."]
    if gauges:
        T += ['', '| gauge | obs rise m | model rise m | obs peak (UTC) | model peak | obs peak Q m3/s | model peak Q m3/s |', '| --- | --- | --- | --- | --- | --- | --- |']
        for g in gauges:
            T.append(f"| {g['site']} {g.get('name') or ''} | {g.get('obs_rise_m')} | {g.get('model_rise_m')} | {g.get('obs_peak_utc')} | {g.get('model_peak_utc')} | {g.get('obs_peak_q_m3s')} | {g.get('model_peak_q_m3s')} |")
    if coarse:
        T += ['', 'Coarse (60 m, 60 x 60 km) run that feeds the edge inflows, at the same gauges:', '', '| gauge | obs peak Q m3/s | model peak Q m3/s | model peak (h from t0) |', '| --- | --- | --- | --- |']
        T += [f"| {g['site']} {g['name'] or ''} | {g['obs_peak_q_m3s']} | {g['model_peak_q_m3s']} | {g['model_peak_h']} |" for g in coarse]
    if inflows:
        T += ['', f"Edge inflows ({len(inflows)}): " + ', '.join(f"{p['name']} {p['area_km2']:.0f} km2 peak {p['peak_m3s']} m3/s" for p in sorted(inflows, key=lambda p: -(p['peak_m3s'] or 0))[:8])]
    open(os.path.join(d, 'RESULTS.md'), 'w').write('\n'.join(T) + '\n'); print('\n'.join(T))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--dir', default='docs/proto/vermont_jul2023'); ap.add_argument('--run-dir')
    a = ap.parse_args(); main(a.dir, a.run_dir)
