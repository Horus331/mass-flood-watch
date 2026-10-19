"""Shared job queue worker: lets any GPU machine (Colab 1, Colab 2, Kaggle, a cluster node) pull the next flood job and run it.

How it works
  * Jobs are defined in the repo:  docs/queue/jobs.json  (a list; edited with git, so the queue has history and review).
      {"id": "sep2023_v3_30m", "kind": "storm", "env": {"RUN": "sep2023", "RES": "30", "TAG": "_v3", ...},
       "steps": ["w4", "w5", "w6"], "gpu_gb": 12, "priority": 5, "after": ["other_job_id"]}
    kinds: storm (w4 engine -> w5 tiles -> w6 score), coast (w8), tiles (w5 only), score (w6 only).
  * Claims and results live on Hugging Face next to the data:  queue/status/<id>.json  {state, worker, started, finished, note}.
    A claim is an HF commit made with parent_commit = the revision we read, so two workers cannot both claim the same job:
    the second commit is rejected and that worker moves on to the next job.
  * Each worker loops: read jobs (GitHub API, no CDN cache) + status (HF) -> pick the highest-priority runnable job whose
    dependencies are done and whose gpu_gb fits -> claim -> run the steps with the job's env -> upload the log and the
    final state.  A heartbeat file is refreshed every 5 min so a dead worker's job can be re-queued (stale > 40 min).

Launch (Colab):  env = dict(os.environ, HF_TOKEN=userdata.get('HF_TOKEN'), WORKER='colab2', GPU_GB='22'); subprocess.Popen('python worker.py', env=env)
Launch (Kaggle): HF_TOKEN from kaggle_secrets, WORKER='kaggle', GPU_GB='15' (T4 x2: one 15 GB card is used), WORK='/kaggle/working'.
Env: HF_TOKEN (required), WORKER (name), GPU_GB (memory available), WORK (scratch dir, default /content), GIT_SHA (default: main at start),
     ONCE=1 (run one job and exit), POLL_S (idle poll seconds, default 120).
"""
import os, sys, json, time, subprocess, urllib.request, socket, traceback
from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.utils import HfHubHTTPError

REPO = 'mohabeldokla/mass-flood-watch-tiles'; GH = 'Horus331/mass-flood-watch'
TOK = os.environ['HF_TOKEN']; api = HfApi(token=TOK)
WORKER = os.environ.get('WORKER', socket.gethostname()); GPU_GB = float(os.environ.get('GPU_GB', '22')); WORK = os.environ.get('WORK', '/content')
POLL = int(os.environ.get('POLL_S', '120')); os.makedirs(WORK, exist_ok=True)
try: os.makedirs('/content', exist_ok=True)       # the step scripts still write under /content (true on Colab and Kaggle, which run as root)
except OSError: pass
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)

def gh_json(path, ref='main'):
    req = urllib.request.Request(f'https://api.github.com/repos/{GH}/contents/{path}?ref={ref}', headers={'Accept': 'application/vnd.github.raw', 'User-Agent': 'mfw-worker'})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())
def gh_sha():
    req = urllib.request.Request(f'https://api.github.com/repos/{GH}/commits/main', headers={'Accept': 'application/vnd.github.sha', 'User-Agent': 'mfw-worker'})
    return urllib.request.urlopen(req, timeout=60).read().decode().strip()

def read_status():
    """{job_id: status dict} from queue/status/*.json, plus the dataset revision they were read at."""
    info = api.dataset_info(REPO, files_metadata=False); rev = info.sha
    st = {}
    for s in info.siblings:
        if s.rfilename.startswith('queue/status/') and s.rfilename.endswith('.json'):
            try: st[s.rfilename.split('/')[-1][:-5]] = json.load(open(hf_hub_download(REPO, s.rfilename, repo_type='dataset', token=TOK, revision=rev, force_download=True)))
            except Exception as e: raise RuntimeError(f'status read failed {s.rfilename}: {e!r}'[:160])      # a missing status would make that job look queued: skip this poll instead
    return st, rev

def write_status(jid, d, parent=None):
    api.upload_file(path_or_fileobj=json.dumps(d, indent=1).encode(), path_in_repo=f'queue/status/{jid}.json', repo_id=REPO, repo_type='dataset',
                    commit_message=f'queue: {jid} {d.get("state")} ({WORKER})', parent_commit=parent)

def job_run_dir(j, env=None):
    """Where the job's run lives on HF.  Storm jobs: exactly what w4 uploads to (runs/<RUN><TAG>_<RES:.0f>m), ignoring any run_dir."""
    e = dict(j.get('env', {}), **(env or {}))
    if j.get('kind', 'storm') == 'storm': return f"runs/{e.get('RUN', '')}{e.get('TAG', '')}_{float(e.get('RES', '30')):.0f}m"
    return j.get('run_dir') or e.get('RUN_DIR', '')

def owns(jid, s):
    """True while the status on HF still names this worker and this claim (another worker may have re-queued a job it thought stale)."""
    try:
        cur = json.load(open(hf_hub_download(REPO, f'queue/status/{jid}.json', repo_type='dataset', token=TOK, force_download=True)))
        return cur.get('worker') == WORKER and abs(cur.get('started', 0) - s['started']) < 1
    except Exception as e: log('owner check failed', repr(e)[:80]); return None      # unknown: callers skip the write rather than risk overwriting a newer claim

def run_exists(run_dir):
    try: return api.file_exists(REPO, f'{run_dir}/meta.json', repo_type='dataset', token=TOK)
    except Exception: return False

def pick(jobs, st):
    now = time.time()
    def runnable(j):
        s = st.get(j['id'], {}); state = s.get('state', 'queued')
        if state == 'done': return False
        if state == 'running' and now - s.get('heartbeat', s.get('started', 0)) < 2400: return False      # alive
        if state in ('failed', 'running') and s.get('attempts', 1) >= 2: return False      # a job that killed its runtime twice needs a human look
        if j.get('gpu_gb', 10) > GPU_GB: return False
        if any(st.get(a, {}).get('state') != 'done' for a in j.get('after', [])): return False
        if j.get('only') and WORKER not in j['only']: return False
        if j.get('requires_run_dir') and not run_exists(job_run_dir(j)): return False      # post-processing of a run made outside the queue: wait until its meta.json is on HF
        return True
    c = [j for j in jobs if runnable(j)]
    c.sort(key=lambda j: (-j.get('priority', 5), j['id']))
    return c[0] if c else None

def fetch_scripts(sha):
    for f in ('sim/colab/w4_flood_gpu.py', 'sim/colab/w5_tiles.py', 'sim/colab/w6_validate.py', 'sim/colab/w8_coast_gpu.py', 'sim/solver.py'):
        urllib.request.urlretrieve(f'https://raw.githubusercontent.com/{GH}/{sha}/{f}', f'{WORK}/{f.split("/")[-1]}')

STEP = {'w4': 'w4_flood_gpu.py', 'w5': 'w5_tiles.py', 'w6': 'w6_validate.py', 'w8': 'w8_coast_gpu.py'}
def run_job(j, sha):
    env = dict(os.environ, HF_TOKEN=TOK, GIT_SHA=j.get('env', {}).get('GIT_SHA', sha), WORKER=WORKER); env.update({k: str(v) for k, v in j.get('env', {}).items()})
    fetch_scripts(env['GIT_SHA'])          # step scripts at the same commit as the files they fetch (and pick up fixes pushed since the worker started)
    env['RUN_DIR'] = job_run_dir(j, env)
    logp = f'{WORK}/job_{j["id"]}.out'; lf = open(logp, 'a'); t0 = time.time(); last_hb = 0
    for step in j.get('steps', ['w4', 'w5', 'w6']):
        lf.write(f'\n===== {step} {time.strftime("%Y-%m-%d %H:%M:%S")} =====\n'); lf.flush()
        p = subprocess.Popen([sys.executable, f'{WORK}/{STEP[step]}'], env=env, stdout=lf, stderr=subprocess.STDOUT, cwd=WORK)
        while p.poll() is None:
            time.sleep(30)
            if time.time() - last_hb > 300:
                last_hb = time.time()
                try:
                    st = json.load(open(f'{WORK}/st_{j["id"]}.json')); o = owns(j['id'], st)
                    if o is None: last_hb = time.time() - 240; continue      # could not check: try again in ~1 min, do not write
                    if not o:
                        p.kill(); lf.write('\n===== claim taken over by another worker: stopping =====\n'); lf.close(); return None, 'taken over', logp
                    st.update(heartbeat=time.time(), step=step, elapsed_s=round(time.time() - t0))
                    json.dump(st, open(f'{WORK}/st_{j["id"]}.json', 'w')); write_status(j['id'], st)
                    api.upload_file(path_or_fileobj=logp, path_in_repo=f'queue/logs/{j["id"]}.log', repo_id=REPO, repo_type='dataset', commit_message=f'queue: log {j["id"]}')
                except Exception as e: log('heartbeat failed', repr(e)[:100])
        if p.returncode != 0: lf.close(); return False, f'{step} exited {p.returncode}', logp
    lf.close(); return True, 'ok', logp

def main():
    sha = os.environ.get('GIT_SHA') or gh_sha(); fetch_scripts(sha); log(f'worker {WORKER}: {GPU_GB} GB, scripts at {sha[:8]}')
    while True:
        try:
            jobs = gh_json('docs/queue/jobs.json'); st, rev = read_status(); j = pick(jobs, st)
        except Exception as e:
            log('queue read failed', repr(e)[:120]); time.sleep(POLL); continue
        if j is None:
            if os.environ.get('ONCE'): log('nothing to do'); return
            log('idle'); time.sleep(POLL); continue
        prev = st.get(j['id'], {}); s = dict(state='running', worker=WORKER, started=time.time(), heartbeat=time.time(), attempts=prev.get('attempts', 0) + 1, git=j.get('env', {}).get('GIT_SHA', sha)[:8])
        try: write_status(j['id'], s, parent=rev)
        except Exception as e:      # 412 = someone committed since we read (claim lost or just a busy repo); anything else = network/HF trouble
            code = getattr(getattr(e, 'response', None), 'status_code', None)
            log('claim lost' if code == 412 else 'claim failed', j['id'], code, repr(e)[:80]); time.sleep(5 if code == 412 else POLL); continue
        json.dump(s, open(f'{WORK}/st_{j["id"]}.json', 'w')); log('claimed', j['id'], j.get('env'))
        try: ok, note, logp = run_job(j, sha)
        except Exception: ok, note, logp = False, traceback.format_exc()[-400:], None
        if ok is None: log(j['id'], 'taken over by another worker; not touching its status'); continue
        s.update(state='done' if ok else 'failed', finished=time.time(), note=note, elapsed_s=round(time.time() - s['started']))
        for k in range(5):
            try:
                o = owns(j['id'], s)
                if o is None: raise RuntimeError('owner check failed')
                if not o: log(j['id'], 'finished but the claim moved on; status left alone'); break
                write_status(j['id'], s)
                if logp: api.upload_file(path_or_fileobj=logp, path_in_repo=f'queue/logs/{j["id"]}.log', repo_id=REPO, repo_type='dataset', commit_message=f'queue: log {j["id"]}')
                break
            except Exception as e: log('final status failed', repr(e)[:80]); time.sleep(20)
        log(j['id'], s['state'], note)
        if os.environ.get('ONCE'): return

def forever():
    while True:      # a crash of the loop (network blip, HF 5xx) must not leave the GPU idle
        try: main(); return
        except Exception: log('worker loop crashed, restarting in 60 s:', traceback.format_exc()[-300:]); time.sleep(60)

if __name__ == '__main__': forever()
