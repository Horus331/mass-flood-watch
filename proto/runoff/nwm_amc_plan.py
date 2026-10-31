"""Run plan of the NWM antecedent-wetness test (docs/proto/runoff/NWM_AMC_PREREG.md) for proto/turing/run_plan_gpu.slurm and
proto/turing/collect_scores.slurm (plan format and checks: proto/turing/inlets_plan.py).

    python proto/runoff/nwm_amc_plan.py      # -> proto/turing/plans/amcnwm_v1.json

50 tasks = 25 primary catalogue storms (docs/proto/parity/catalog/<storm>_<area>_20m/config.json) x 2 arms, the two arms of a storm next
to each other (task 2i = base, 2i + 1 = nwm), so a batch of consecutive tasks runs both arms of its storms on the same GPU node.
"""
import os, re, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'proto', 'turing')); import inlets_plan as IP  # noqa: E402

COMMON = dict(RES='20', LF_PARITY='1', LF_LOSS='cn', LF_CN_SCALE='0.88', LF_INFIL_MMH='2', LF_QOUT='1', LF_VOUT='1')   # parity catalogue settings
ARMS = dict(base={}, nwm=dict(LF_CN_AMC='nwm', LF_NWM_SOILSAT_JSON='docs/proto/runoff/nwm_soilsat.json'))


def make(out=os.path.join(ROOT, 'proto', 'turing', 'plans', 'amcnwm_v1.json')):
    T = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'docs', 'proto', 'parity', 'catalog', '*_20m', 'config.json'))):
        c = json.load(open(p)); s = c['storm']
        if not re.fullmatch(rf'{s}_[a-z]+_20m', c['name']): continue
        assert c['env'] == 'LF_PARITY=1 LF_CN_SCALE=0.88', c
        for arm, e in ARMS.items():
            T.append(dict(name=f'amcnwm_{arm}_{s}', storm=s, arm=arm, role='dev (report only)' if s in ('sep2023', 'aug2021') else 'held-out 23 (decision)',
                          env=dict(BOX=c['box'], HOURS=str(c['hours']), STORM=s, **e)))
    assert len(T) == 50, len(T)
    P = dict(id='amcnwm_v1', about='LF_CN_AMC=nwm test, docs/proto/runoff/NWM_AMC_PREREG.md (GPU, proto/turing/run_plan_gpu.slurm)',
             results_root='amcnwm_v1', dest='docs/proto/runoff/amcnwm_v1', common=COMMON, tasks=T)
    IP.check(P); json.dump(P, open(out, 'w'), indent=1); print(out, len(T), 'tasks'); return P


if __name__ == '__main__':
    make()
