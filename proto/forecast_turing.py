"""Live forecast: Turing first, GitHub boxes as the backup (docs/proto/forecast/GATE.md, "Turing first").

    python proto/forecast_turing.py request --gate gate/gate.json --prefix forecast_latest [--force] [--hours 48] [--repo .]
        (forecast.yml gate job, when the gate fires) queue one whole-District-3 array job on Turing: a request at the FRONT of jobs.json on
        the turing-queue branch (the queue runner submits in jobs.json order and stops at the first refusal of the per-user submit cap, so
        a storm cycle is never stuck behind research requests). Kind forecast_d3 (proto/turing/forecast_d3.slurm), one array task per
        ensemble member, same HRRR members and hours as the box jobs.
    python proto/forecast_turing.py prefer --status docs/site/data/forecast_status.json --turing docs/site/data/forecast_d3_status.json
        (forecast.yml publish job, after forecast.py status) the boxes' status was just written: if Turing already published THIS cycle,
        put the Turing status back (the boxes' one is kept as <status>_boxes.json); otherwise label the boxes as the backup.
    python proto/forecast_turing.py selftest
"""
import argparse, datetime as dt, json, os, re, subprocess, sys, tempfile, time

D3_BOX = [128000.0, 856000.0, 206000.0, 946000.0]


def turing_prefix(prefix):
    return 'forecast_d3' if prefix == 'forecast_latest' else re.sub(r'[^a-z0-9_]', '', prefix.lower())[:36] + '_d3'


def make_request(G, prefix, force=False, hours=None, now=None):
    mem = (G.get('ensemble') or {}).get('members') or [G['issued'][:13] + 'Z']
    mem = [m if re.match(r'^\d{4}-\d\d-\d\dT\d\dZ$', m) else m[:13] + 'Z' for m in mem]
    cyc = mem[0]; tag = re.sub(r'\D', '', cyc); pfx = turing_prefix(prefix)
    env = dict(CYCLE=cyc, MEMBERS=','.join(mem), HOURS=str(int(hours or G.get('horizon_h') or 48)), PFX=pfx,
               REQ_AT=(now or dt.datetime.now(dt.timezone.utc)).strftime('%Y-%m-%dT%H:%M:%SZ'))
    if force: env['FORCE'] = '1'
    return dict(id=f'fcd3_{pfx}_{tag}'[:60], kind='forecast_d3', env=env,
                sbatch=dict(array=f'0-{len(mem) - 1}', partition='quick', time='06:00:00'))


def insert_front(J, req):
    ids = {j.get('id') for j in J.get('jobs', [])}
    if req['id'] in ids: return False
    J.setdefault('jobs', []).insert(0, req); return True


def git(*a, cwd=None):
    r = subprocess.run(['git', *a], cwd=cwd, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(f"git {' '.join(a)}: {r.stderr.strip()[:300]}")
    return r.stdout.strip()


def cmd_request(a):
    G = json.load(open(a.gate))
    if not G.get('trigger'): print('gate quiet: no Turing request'); return
    req = make_request(G, a.prefix, a.force, a.hours)
    d = tempfile.mkdtemp()
    for i in range(5):
        try:
            git('fetch', '-q', 'origin', '+refs/heads/turing-queue:refs/remotes/origin/turing-queue', cwd=a.repo)
            wt = os.path.join(d, f'tq{i}'); git('worktree', 'add', '-q', '--detach', wt, 'origin/turing-queue', cwd=a.repo)
            p = os.path.join(wt, 'jobs.json'); J = json.load(open(p))
            if not insert_front(J, req): print('already queued:', req['id']); return
            open(p, 'w').write(json.dumps(J, indent=1) + '\n')
            git('add', 'jobs.json', cwd=wt)
            git('-c', 'user.name=flood-watch-bot', '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com', 'commit', '-qm',
                f"Queue: forecast {req['env']['CYCLE']} whole District 3 on Turing ({len(req['env']['MEMBERS'].split(','))} members, {req['env']['PFX']})", cwd=wt)
            git('push', '-q', 'origin', 'HEAD:refs/heads/turing-queue', cwd=wt)
            print('queued', json.dumps(req)); return
        except Exception as e:
            print('retry:', repr(e)[:300]); time.sleep(5 + 5 * i)
    raise SystemExit('could not queue the Turing request')


def prefer(status, turing):
    """-> (status to publish, boxes status to keep aside or None)"""
    if status.get('state') != 'run':
        return status, None
    if turing and turing.get('display') == 'turing' and turing.get('issued') == status.get('issued'):
        return turing, dict(status, display='boxes', superseded_by='turing')
    nb = len(status.get('runs') or status.get('boxes') or [])
    s = dict(status, display='boxes', coverage=f"Backup: {nb} box{'es' if nb != 1 else ''} of 20 × 20 km on the heaviest rain (Turing run not ready)")
    s['kind'] = ("The flood model ran only in these boxes (GitHub Actions); the whole-district run on WPI’s Turing cluster was not ready, "
                 "so roads outside the boxes were not modelled.")
    return s, None


def cmd_prefer(a):
    S = json.load(open(a.status)); T = json.load(open(a.turing)) if a.turing and os.path.exists(a.turing) else None
    out, aside = prefer(S, T)
    if aside is not None: json.dump(aside, open(re.sub(r'\.json$', '_boxes.json', a.status), 'w'), separators=(',', ':'))
    json.dump(out, open(a.status, 'w'), separators=(',', ':'))
    print('status:', out.get('display'), out.get('issued'), out.get('coverage', ''))


def selftest():
    G = dict(trigger=True, issued='2026-11-01T12:00Z', horizon_h=48, ensemble=dict(members=['2026-11-01T12Z', '2026-11-01T06Z', '2026-11-01T11Z']))
    r = make_request(G, 'forecast_latest', now=dt.datetime(2026, 11, 1, 13, 50, tzinfo=dt.timezone.utc))
    assert r['id'] == 'fcd3_forecast_d3_2026110112' and r['sbatch']['array'] == '0-2' and r['env']['PFX'] == 'forecast_d3', r
    assert make_request(G, 'test1')['env']['PFX'] == 'test1_d3'
    V = re.compile(r'^[A-Za-z0-9_.,:=/@+%~-]{0,300}$'); assert all(V.match(v) for v in r['env'].values()), r
    J = dict(jobs=[dict(id='research')]); assert insert_front(J, r) and J['jobs'][0]['id'] == r['id'] and not insert_front(J, r)
    B = dict(state='run', issued='2026-11-01T12:00Z', runs=[1, 2])
    s, x = prefer(B, None); assert s['display'] == 'boxes' and 'Backup: 2 boxes' in s['coverage'] and x is None
    T = dict(state='run', issued='2026-11-01T12:00Z', display='turing')
    s, x = prefer(B, T); assert s is T and x['superseded_by'] == 'turing'
    s, x = prefer(dict(B, issued='2026-11-01T18:00Z'), T); assert s['display'] == 'boxes'       # a stale Turing cycle never wins
    s, x = prefer(dict(state='quiet', issued='2026-11-01T18:00Z'), T); assert s['state'] == 'quiet'
    print('selftest ok')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd')
    p = sp.add_parser('request'); p.add_argument('--gate', required=True); p.add_argument('--prefix', default='forecast_latest')
    p.add_argument('--force', action='store_true'); p.add_argument('--hours', type=int); p.add_argument('--repo', default='.')
    p = sp.add_parser('prefer'); p.add_argument('--status', required=True); p.add_argument('--turing')
    sp.add_parser('selftest')
    a = ap.parse_args()
    {'request': cmd_request, 'prefer': cmd_prefer, 'selftest': lambda a: selftest()}.get(a.cmd, lambda a: ap.print_help())(a)
