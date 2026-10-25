"""Label round 3 secondary re-scores (docs/proto/obs/LABELS_ROUND3.md): the parity runs scored with the same score_v2 code under four label
settings.  These are SECONDARY analyses; the PROTOCOL decision set (closure labels, unweighted) is unchanged and is the 'base' setting.

    python proto/labels_round3.py score [--boot 2000]     # -> docs/proto/obs/round3/score_round3.json (+ score_round3_table.md)

Settings: base (labels_*.csv as committed = round 2), scf (+ proto/data/scf_<storm>.csv, SCORE_SCF=1), tiers (SCORE_TIERS=1: site weight =
best label's evidence weight, proto/label_tiers.py), scf_tiers (both).  Same runs (docs/proto/parity/catalog, primary <storm>_<area>_20m),
same matching (new rows: strict 30 m), locked storms never loaded (score_v2.find_runs).
"""
import argparse, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import score_v2 as SV  # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'proto', 'obs', 'round3')
SETTINGS = dict(base=dict(SCORE_SCF='0', tiers=False), scf=dict(SCORE_SCF='1', tiers=False), tiers=dict(SCORE_SCF='0', tiers=True),
                scf_tiers=dict(SCORE_SCF='1', tiers=True))
POOLS = dict(heldout23=SV.HELDOUT + SV.NEW16, heldout7=SV.HELDOUT, new16=SV.NEW16, dev2=SV.DEV)


def score(boot):
    runs = [(p, s) for p, s, grp, prim in SV.find_runs() if grp == 'parity' and prim]
    res = dict(made_by='proto/labels_round3.py score', boot=boot, settings={}, per_storm={}, pools={})
    for name, cfg in SETTINGS.items():
        os.environ['SCORE_SCF'] = cfg['SCORE_SCF']; SV.TIERED = cfg['tiers']
        R = {}
        for p, s in runs:
            r = SV.score_run(SV.load_run(p, s)); r.update(group='parity', primary=True); R[s] = r
        res['settings'][name] = cfg
        res['per_storm'][name] = {s: dict(sites=r['domains']['box']['n_sites'], labels_in_box=r['labels_in_box'], matched=r['domains']['box']['n_labels_matched'],
                                          hits3=r['domains']['box']['shares']['0.03']['site_hits'], rule_hits=r['domains']['box']['rule']['site_hits'],
                                          site_ids=[x['id'] for x in r['domains']['box']['sites']],
                                          site_tiers=[x.get('tier') for x in r['domains']['box']['sites']],
                                          scf_sites=sum('SCF-' in x['id'] for x in r['domains']['box']['sites']),
                                          scf_only_sites=sum(all(k.startswith('SCF-') for k in x['id'].split('+')) for x in r['domains']['box']['sites']))
                                  for s, r in R.items()}
        res['pools'][name] = {}
        for pn, st in POOLS.items():
            sel = [R[s] for s in st if s in R]
            pl = SV.pooled(sel, 'box', boot=boot) if sel else None
            if not pl: continue
            P, C = pl['point'], pl['ci90']
            o = dict(storms=len(sel), sites=pl['n_sites'])
            for b in ('rule', 'share_0.03', 'share_0.1'):
                o[b] = {k: v for k, v in P[b].items()}; o[b]['site_recall_ci90'] = C[b]['site_recall']
                if 'wsite_recall' in C[b]: o[b]['wsite_recall_ci90'] = C[b]['wsite_recall']
            res['pools'][name][pn] = o
        h = res['pools'][name]['heldout23']
        print(f"{name:10s} heldout23 sites {h['sites']} rec@3% {h['share_0.03']['site_recall']:.3f} "
              f"w {h['share_0.03'].get('wsite_recall')} rule {h['rule']['site_recall']:.3f}", flush=True)
    os.environ.pop('SCORE_SCF', None); SV.TIERED = False
    os.makedirs(OUT, exist_ok=True); json.dump(res, open(os.path.join(OUT, 'score_round3.json'), 'w'), indent=1, default=float)
    return res


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['score']); ap.add_argument('--boot', type=int, default=2000)
    a = ap.parse_args(); score(a.boot)
