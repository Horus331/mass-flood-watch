"""Turing job queue: lets work be started on Turing without anyone logging in (docs/proto/turing/QUEUE.md).

Turing has no scrontab, so a tiny Slurm job (proto/turing/queue_runner.slurm) re-submits itself every TICK minutes. Each tick:
  1. pulls main (the code) and the branch `turing-queue` (the requests: jobs.json),
  2. submits every new request whose kind is in proto/turing/queue_kinds.json, after checking every value against a strict pattern,
  3. polls Slurm for the jobs it submitted, and
  4. writes status.json + STATUS.md back to `turing-queue` (only when something changed; main is never touched, so the public site is not
     redeployed).
Only the whitelisted Slurm scripts in this repository can run. Requests cannot pass shell code: values may only contain [A-Za-z0-9_.,:=/@+%-].

    python proto/turing/queue_runner.py tick  [--qdir ~/scratch/queue] [--dry-run]
    python proto/turing/queue_runner.py selftest

jobs.json on `turing-queue`:
    {"jobs": [ {"id": "surr_gen_b1", "kind": "surrogate_gen", "env": {"PLAN": "~/scratch/surrogate/plan_b1.json", "PER_TASK": "8"},
                "sbatch": {"array": "0-23%4"}, "after": []},
               {"id": "surr_train_b1", "kind": "surrogate_train", "env": {"PLANS": "~/scratch/surrogate/plan_b1.json"},
                "after": ["surr_gen_b1", "surr_inputs"]} ],
     "paused": false}
A request is submitted once (its id is remembered); to rerun, add a new id.  "after" = Slurm afterok on those requests' jobs.
"""
import os, re, sys, json, time, shlex, argparse, subprocess, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
VAL = re.compile(r'^[A-Za-z0-9_.,:=/@+%~-]{0,300}$')
KEY = re.compile(r'^[A-Z][A-Z0-9_]{0,40}$')
ID = re.compile(r'^[A-Za-z0-9_.-]{1,60}$')
BAD_KEYS = {'PATH', 'HOME', 'SHELL', 'BASH_ENV', 'ENV', 'IFS', 'PS4', 'PROMPT_COMMAND', 'PYTHONPATH', 'PYTHONSTARTUP', 'PYTHONHOME',
            'LD_PRELOAD', 'LD_LIBRARY_PATH', 'CONDA_PREFIX', 'GIT_SSH', 'GIT_SSH_COMMAND', 'GIT_DIR', 'SLURM_CONF'}
SBATCH_OK = {'array': re.compile(r'^[0-9][0-9,%-]{0,40}$'), 'partition': re.compile(r'^(short|long|quick|academic)$'),
             'time': re.compile(r'^[0-9]{1,2}(-[0-9]{1,2})?(:[0-9]{2}){0,2}$'), 'gres': re.compile(r'^gpu(:[A-Za-z0-9_]+)?:[1-4]$'),
             'mem': re.compile(r'^[0-9]{1,4}G$')}
DONE = {'COMPLETED'}; FAILED = {'FAILED', 'CANCELLED', 'TIMEOUT', 'OUT_OF_MEMORY', 'NODE_FAIL', 'PREEMPTED', 'BOOT_FAIL', 'DEADLINE'}


def now(): return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def log(*a): print(now(), *a, flush=True)


def jload(p, d=None):
    try: return json.load(open(p))
    except Exception: return d


def validate(req, kinds):
    """-> (sbatch argv list, problems)."""
    bad = []
    if not ID.match(str(req.get('id', ''))): bad.append('bad id')
    K = kinds.get(req.get('kind'))
    if not K: return None, bad + [f"kind {req.get('kind')!r} not in queue_kinds.json"]
    env = {}
    for k, v in (req.get('env') or {}).items():
        v = str(v)
        if not KEY.match(k) or k in BAD_KEYS or k.startswith(('LD_', 'BASH_FUNC', 'SLURM_')): bad.append(f'env key {k!r} not allowed'); continue
        if K.get('env') is not None and k not in K['env']: bad.append(f'env key {k!r} not listed for kind'); continue
        if not VAL.match(v): bad.append(f'env value of {k} has characters outside [A-Za-z0-9_.,:=/@+%~-]'); continue
        env[k] = v.replace('~', os.path.expanduser('~'), 1) if v.startswith('~') else v
    for k in K.get('required', []):
        if k not in env: bad.append(f'missing env {k}')
    sb = ['sbatch', '--parsable', f"--job-name=q_{req['id']}"[:60]]
    for k, v in (req.get('sbatch') or {}).items():
        if k not in SBATCH_OK or k not in K.get('sbatch', list(SBATCH_OK)) or not SBATCH_OK[k].match(str(v)): bad.append(f'sbatch {k}={v!r} not allowed'); continue
        sb.append(f'--{k}={v}')
    # Slurm's --export splits on commas, so values with commas go through the environment of sbatch itself (--export=ALL picks them up)
    sb.append('--export=ALL')
    script = K['script']
    if not re.match(r'^proto/turing/[A-Za-z0-9_]+\.slurm$', script) or not os.path.exists(os.path.join(REPO, script)): bad.append(f'script {script} missing')
    if K.get('kind_args'): sb += list(K['kind_args'])
    return dict(argv=sb + [script], env=env), bad


def sh(cmd, env=None, timeout=300):
    try: r = subprocess.run(cmd, cwd=REPO, env=env, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e: return 127, '', repr(e)[:200]
    return r.returncode, (r.stdout or '').strip(), (r.stderr or '').strip()


def slurm_state(jid):
    rc, out, _ = sh(['sacct', '-n', '-X', '-P', '-j', str(jid), '--format=JobID,State,ExitCode,Elapsed'])
    if rc != 0 or not out: return None
    states = [l.split('|') for l in out.splitlines() if l]
    S = [s[1].split()[0] for s in states]
    if any(s in ('RUNNING', 'PENDING', 'REQUEUED', 'SUSPENDED', 'CONFIGURING', 'COMPLETING') for s in S): st = 'RUNNING' if 'RUNNING' in S else 'PENDING'
    elif all(s in DONE for s in S): st = 'COMPLETED'
    elif any(s in FAILED for s in S): st = 'FAILED'
    else: st = S[0] if S else None
    return dict(state=st, tasks=len(S), done=sum(s in DONE for s in S), failed=sum(s in FAILED for s in S),
                elapsed=max((s[3] for s in states), default=''))


def tick(qdir, dry=False, kinds_path=None, jobs_path=None, state_path=None):
    kinds = jload(kinds_path or os.path.join(HERE, 'queue_kinds.json'), {}).get('kinds', {})
    J = jload(jobs_path or os.path.join(qdir, 'repo', 'jobs.json'), {}) or {}
    sp = state_path or os.path.join(qdir, 'repo', 'status.json'); S = jload(sp, {}) or {}
    St = S.setdefault('jobs', {}); before = json.dumps(St, sort_keys=True)
    # 1. poll what is in flight
    for rid, s in St.items():
        if s.get('status') in ('submitted', 'pending', 'running') and s.get('slurm_id') and s['slurm_id'] != 'DRY':
            q = slurm_state(s['slurm_id'])
            if q and q['state']:
                s.update(slurm=q); s['status'] = {'PENDING': 'pending', 'RUNNING': 'running', 'COMPLETED': 'completed', 'FAILED': 'failed'}.get(q['state'], s['status'])
                if s['status'] in ('completed', 'failed'): s['finished'] = s.get('finished') or now()
    # 2. submit new requests
    if not J.get('paused'):
        for req in J.get('jobs', []):
            rid = str(req.get('id', ''))
            if not rid or (rid in St and St[rid].get('status') != 'deferred'): continue    # 'deferred' = refused by the per-user job cap: retried
            spec, bad = validate(req, kinds)
            if bad: St[rid] = dict(status='rejected', why=bad[:5], at=now()); log('rejected', rid, bad); continue
            deps = []
            for a in req.get('after') or []:
                d = St.get(a)
                if not d or d.get('status') in ('rejected', 'failed') or not d.get('slurm_id'): deps = None; break
                if d.get('status') != 'completed': deps.append(str(d['slurm_id']))
            if deps is None:
                waiting = [a for a in req.get('after') or [] if a not in St or St[a].get('status') == 'deferred']
                if waiting: continue                                   # a dependency is not submitted yet: try next tick
                St[rid] = dict(status='rejected', why=['a dependency failed or was rejected'], at=now()); continue
            argv = list(spec['argv'])
            if deps: argv.insert(2, '--dependency=afterok:' + ':'.join(deps))
            env = dict(os.environ, **spec['env'])
            if dry: St[rid] = dict(status='submitted', slurm_id='DRY', argv=argv, env=spec['env'], at=now()); continue
            rc, out, err = sh(argv, env=env)
            jid = out.split(';')[0] if rc == 0 else None
            if not jid and 'QOSMaxSubmitJobPerUserLimit' in (err or out):     # the cluster's cap on submitted jobs per user: not a failure,
                St[rid] = dict(status='deferred', kind=req['kind'], at=now(), tries=(St.get(rid) or {}).get('tries', 0) + 1,   # retry next tick,
                               error='QOSMaxSubmitJobPerUserLimit: waiting for a free submit slot')                          # in jobs.json order
                log('deferred', rid); break
            St[rid] = dict(status='submitted' if jid else 'failed', slurm_id=jid, kind=req['kind'], env=spec['env'], sbatch=req.get('sbatch') or {},
                           after=req.get('after') or [], at=now(), error=None if jid else (err or out)[:300])
            log('submit', rid, jid, err[:200])
    S['updated'] = now(); S['paused'] = bool(J.get('paused'))
    changed = json.dumps(St, sort_keys=True) != before
    if changed or not os.path.exists(sp):
        json.dump(S, open(sp, 'w'), indent=1)
        lines = ['# Turing queue status', '', f"Updated {S['updated']} by `proto/turing/queue_runner.py` on Turing. Requests: `jobs.json` on this branch.", '',
                 '| request | kind | status | Slurm job | tasks done / failed | submitted | finished | note |', '|' + ' --- |' * 8]
        for rid, s in St.items():
            q = s.get('slurm') or {}
            lines.append(f"| {rid} | {s.get('kind', '')} | {s['status']} | {s.get('slurm_id') or ''} | {q.get('done', '')} / {q.get('failed', '')} | {s.get('at', '')} | "
                         f"{s.get('finished', '')} | {'; '.join(s.get('why') or []) or (s.get('error') or '')[:120]} |")
        open(os.path.join(os.path.dirname(sp), 'STATUS.md'), 'w').write('\n'.join(lines) + '\n')
    return changed


def selftest():
    import tempfile
    d = tempfile.mkdtemp()
    kinds = dict(kinds=dict(surrogate_gen=dict(script='proto/turing/surrogate_gen.slurm', env=['PLAN', 'PER_TASK'], required=['PLAN'], sbatch=['array', 'partition'])))
    kp, jp, sp = (os.path.join(d, n) for n in ('k.json', 'j.json', 's.json')); json.dump(kinds, open(kp, 'w'))
    jobs = dict(jobs=[dict(id='g1', kind='surrogate_gen', env=dict(PLAN='~/x.json', PER_TASK='8'), sbatch=dict(array='0-23%4')),
                      dict(id='evil', kind='surrogate_gen', env=dict(PLAN='x; rm -rf ~')),
                      dict(id='evil2', kind='surrogate_gen', env=dict(PLAN='x', LD_PRELOAD='/tmp/a.so')),
                      dict(id='evil3', kind='bash', env=dict(PLAN='x')),
                      dict(id='evil4', kind='surrogate_gen', env=dict(PLAN='x'), sbatch=dict(wrap='rm')),
                      dict(id='t1', kind='surrogate_gen', env=dict(PLAN='y'), after=['g1']),
                      dict(id='t2', kind='surrogate_gen', env=dict(PLAN='y'), after=['later'])])
    json.dump(jobs, open(jp, 'w'))
    tick(d, dry=True, kinds_path=kp, jobs_path=jp, state_path=sp); S = json.load(open(sp))['jobs']
    assert S['g1']['status'] == 'submitted' and '--array=0-23%4' in S['g1']['argv'] and S['g1']['env']['PLAN'].startswith('/'), S['g1']
    for e in ('evil', 'evil2', 'evil3', 'evil4'): assert S[e]['status'] == 'rejected', (e, S[e])
    assert S['t1']['status'] == 'submitted' and any(a.startswith('--dependency=afterok:DRY') for a in S['t1']['argv']), S['t1']
    assert 't2' not in S
    assert not tick(d, dry=True, kinds_path=kp, jobs_path=jp, state_path=sp)          # nothing new -> unchanged
    # the per-user submit cap defers (and retries) instead of failing; dependants wait
    d2 = tempfile.mkdtemp(); kp2, jp2, sp2 = (os.path.join(d2, n) for n in ('k.json', 'j.json', 's.json')); json.dump(kinds, open(kp2, 'w'))
    json.dump(dict(jobs=[dict(id='a', kind='surrogate_gen', env=dict(PLAN='x')), dict(id='b', kind='surrogate_gen', env=dict(PLAN='y'), after=['a'])]), open(jp2, 'w'))
    global sh
    real = sh; cap = [True]
    sh = lambda argv, env=None, timeout=300: (1, '', 'sbatch: error: QOSMaxSubmitJobPerUserLimit') if cap[0] else (0, '123', '')
    try:
        tick(d2, kinds_path=kp2, jobs_path=jp2, state_path=sp2); S2 = json.load(open(sp2))['jobs']
        assert S2['a']['status'] == 'deferred' and 'b' not in S2, S2
        cap[0] = False; tick(d2, kinds_path=kp2, jobs_path=jp2, state_path=sp2); S2 = json.load(open(sp2))['jobs']
        assert S2['a']['status'] == 'submitted' and S2['b']['status'] == 'submitted', S2
    finally: sh = real
    print('queue_runner selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('tick'); p.add_argument('--qdir', default=os.path.expanduser('~/scratch/queue')); p.add_argument('--dry-run', action='store_true')
    sp.add_parser('selftest')
    a = ap.parse_args()
    if a.cmd == 'selftest': selftest()
    else: sys.exit(0 if tick(a.qdir, a.dry_run) is not None else 1)
