"""Run plans for proto/turing/run_inlets.slurm and proto/turing/collect_scores.slurm (docs/proto/drains/INLETS_PREREG.md).

    python proto/turing/inlets_plan.py make            # -> proto/turing/plans/inlets_v1.json (from docs/proto/parity/catalog/*/config.json)
    python proto/turing/inlets_plan.py env PLAN IDX    # 'export K=V' lines for task IDX (values checked; sourced by run_inlets.slurm)
    python proto/turing/inlets_plan.py selftest

Plan json: {"id", "results_root" (under $LF_WORK), "dest" (docs/proto/<area>/<dir> on main), "common": {env}, "tasks": [{"name", "storm",
"arm", "env": {...}}]}.  Every value must match the queue's value pattern; keys must be BOX, HOURS, STORM, RES, NAME or LF_*.
"""
import json, os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
VAL = re.compile(r'^[A-Za-z0-9_.,:=/@+%~-]{0,300}$')
KEY = re.compile(r'^(BOX|HOURS|STORM|RES|NAME|LF_[A-Z0-9_]{1,40})$')
NAME = re.compile(r'^[a-z0-9_]{3,80}$')
DEST = re.compile(r'^docs/proto/[a-z0-9_]+/[A-Za-z0-9_]+$')
ROOTV = re.compile(r'^[A-Za-z0-9_]+$')
DECISION = ('aug2023', 'aug2023b', 'aug2026', 'jul2021', 'jul2023', 'sep2021', 'sep2022', 'may2018', 'aug2018b', 'sep2018', 'sep2018w', 'sep2018m',
            'sep2018b', 'jul2019', 'aug2019', 'sep2019', 'jun2020', 'jun2020b', 'aug2020b', 'jul2021b', 'jul2023b', 'jul2023c', 'jul2023d')   # held-out 23
CALIB = 'sep2023'
COMMON = dict(RES='20', LF_PARITY='1', LF_LOSS='cn', LF_CN_SCALE='0.88', LF_INFIL_MMH='2', LF_QOUT='1', LF_VOUT='1')   # parity/BASELINE.md settings
ARMS = dict(base={}, inlets=dict(LF_INLETS='1'))
SENS = dict(inlets_clog0=dict(LF_INLETS='1', LF_INLETS_CLOG='0'), inlets_clog065=dict(LF_INLETS='1', LF_INLETS_CLOG='0.65'))   # sep2023 only


def make(out=os.path.join(HERE, 'plans', 'inlets_v1.json')):
    cat = {}
    for p in sorted(glob.glob(os.path.join(ROOT, 'docs', 'proto', 'parity', 'catalog', '*_20m', 'config.json'))):
        c = json.load(open(p))
        if re.fullmatch(rf"{c['storm']}_[a-z]+_20m", c['name']): cat[c['storm']] = c
    missing = [s for s in (CALIB,) + DECISION if s not in cat]
    if missing: raise SystemExit(f'not in the catalogue: {missing}')
    T = []
    for s in (CALIB,) + DECISION:
        c = cat[s]
        for arm, e in list(ARMS.items()) + (list(SENS.items()) if s == CALIB else []):
            T.append(dict(name=f"inl1_{c['name']}_{arm}", storm=s, arm=arm, role='calibration (report only)' if s == CALIB else 'held-out 23 (decision)',
                          env=dict(BOX=c['box'], HOURS=str(c['hours']), STORM=s, **e)))
    P = dict(id='inlets_v1', about='LF_INLETS test, docs/proto/drains/INLETS_PREREG.md', results_root='inlets_v1', dest='docs/proto/drains/inlets_v1',
             common=COMMON, tasks=T)
    check(P); os.makedirs(os.path.dirname(out), exist_ok=True); json.dump(P, open(out, 'w'), indent=1); print(out, len(T), 'tasks'); return P


def check(P):
    assert DEST.match(P['dest']) and ROOTV.match(P['results_root']), 'bad dest / results_root'
    names = [t['name'] for t in P['tasks']]; assert len(set(names)) == len(names), 'duplicate names'
    for t in P['tasks']:
        assert NAME.match(t['name']), t['name']
        for k, v in list(P.get('common', {}).items()) + list(t['env'].items()):
            assert KEY.match(k) and VAL.match(str(v)), (k, v)
    return True


def env(plan, idx):
    if not re.fullmatch(r'proto/turing/plans/[A-Za-z0-9_]+\.json', plan): raise SystemExit('PLAN must be proto/turing/plans/<name>.json')
    P = json.load(open(os.path.join(ROOT, plan))); check(P); t = P['tasks'][int(idx)]
    E = dict(P.get('common', {}), **t['env'], NAME=t['name'])
    lines = [f'export {k}={v}' for k, v in E.items()] + [f"export TASK_STORM={t['storm']} TASK_ARM={t['arm']} RESULTS_ROOT={P['results_root']}"]
    print('\n'.join(lines))


def selftest():
    P = make(out='/tmp/inlets_plan_selftest.json')
    assert len(P['tasks']) == 2 * 24 + 2 and P['tasks'][0]['storm'] == CALIB and P['tasks'][1]['env']['LF_INLETS'] == '1'
    assert all('LF_INLETS' not in t['env'] for t in P['tasks'] if t['arm'] == 'base')
    bad = json.loads(json.dumps(P)); bad['tasks'][0]['env']['BOX'] = '1;rm -rf ~'
    try: check(bad); raise AssertionError('bad value accepted')
    except AssertionError as e:
        if 'accepted' in str(e): raise
    print('inlets_plan selftest ok')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['make']: make()
    elif a[:1] == ['env']: env(a[1], a[2])
    else: selftest()
