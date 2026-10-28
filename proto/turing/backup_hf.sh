#!/bin/bash
# Back up the important Turing run outputs to the Hugging Face dataset mohabeldokla/mass-flood-watch-tiles under runs/turing/<name>/.
#   export HF_TOKEN=...            # a write token for the dataset; set it yourself (never stored in the repo, never printed)
#   bash proto/turing/backup_hf.sh --dry-run          # list what would be uploaded, upload nothing
#   bash proto/turing/backup_hf.sh                    # upload (files already on the dataset with the same size are skipped)
#   bash proto/turing/backup_hf.sh --only leominster  # only runs / results whose name contains 'leominster'
# Sources:  ~/scratch/lisflood/run_*/out/   -> runs/turing/<name>/          (<name> = folder name without 'run_')
#           ~/mass-flood-watch/results/*/   -> runs/turing/<name>/results/
# Kept: hmax / hsnap / meta / score / summary / points / features / matches json-csv, the frame packs (frames_cm.npz: the 5-min packs of
# LF_SAVEINT=300 runs, and any *pack* file), vel_max / timing / rainstats npz, gauge windows, lisflood.mass, run.par/.bci, logs.
# Not kept: raw per-step LISFLOOD-FP files (*.wd, *.Vx, *.Vy, *.Qx, *.Qy, *.asc snapshots, res-*), z.npy / z_raw.npz / watermask.npy (rebuilt from the
# tiles; add --include-dem to keep them).  Options: --runs-root DIR, --results-root DIR, --repo ID, --max-mb N (skip larger files, default 4000).
set -eo pipefail
set +x                                    # never trace: the token must not reach the terminal or a job log
cd "$(dirname "$0")/../.."
TOKFILE="${HF_TOKEN_PATH:-$HOME/.cache/huggingface/token}"
if [ -z "${HF_TOKEN:-}" ] && [ ! -s "$TOKFILE" ]; then
  echo "No Hugging Face token: export HF_TOKEN, or save a write token in $TOKFILE (huggingface-cli login does this)." >&2
  exit 2
fi
if ! python -c "import huggingface_hub" 2>/dev/null; then
  [ -f proto/turing/env.sh ] && source proto/turing/env.sh >/dev/null 2>&1 || true
  python -c "import huggingface_hub" 2>/dev/null || { echo "python package huggingface_hub missing (pip install huggingface_hub)" >&2; exit 3; }
fi
exec python - "$@" <<'PY'
import os, sys, re, glob, argparse, fnmatch
from huggingface_hub import HfApi, CommitOperationAdd

ap = argparse.ArgumentParser(prog='backup_hf.sh')
ap.add_argument('--dry-run', action='store_true'); ap.add_argument('--only', default='')
ap.add_argument('--runs-root', default=os.path.expanduser(os.environ.get('LF_WORK', '~/scratch/lisflood')))
ap.add_argument('--results-root', default=os.path.expanduser('~/mass-flood-watch/results'))
ap.add_argument('--repo', default='mohabeldokla/mass-flood-watch-tiles'); ap.add_argument('--prefix', default='runs/turing')
ap.add_argument('--include-dem', action='store_true'); ap.add_argument('--max-mb', type=float, default=4000)
ap.add_argument('--batch', type=int, default=40, help='files per commit')
a = ap.parse_args()

KEEP_OUT = ['hmax.npy', 'hsnap.npy', 'meta.json', '*.json', 'frames_cm.npz', '*pack*', 'vel_max.npz', 'timing.npz', 'rainstats.npz', 'gauge_windows.npz',
            'lisflood.mass', 'run.par', 'run.bci', 'run.bdy', '*_log.txt', '*stdout*.txt', 'domain_mask.npy']
KEEP_RES = ['*.json', '*.csv', '*.md', '*.npz', '*.geojson', '*.geojson.gz', '*.html', '*.txt', '*pack*']
DEM = ['z.npy', 'z_raw.npz', 'watermask.npy']
RAW = re.compile(r'(\.(wd|vx|vy|qx|qy|asc|wdfp|elev|inittm|maxtm|totaltm|max|mxe|Vx|Vy|Qx|Qy)$)|(^res-)|(-\d{4}\.)', re.I)


def want(name, keep):
    if RAW.search(name): return False
    return any(fnmatch.fnmatch(name, k) for k in keep + (DEM if a.include_dem else []))


def files(src, keep):
    out = []
    for dp, dn, fn in os.walk(src):
        for f in fn:
            p = os.path.join(dp, f)
            if want(f, keep) and os.path.getsize(p) <= a.max_mb * 1e6: out.append(p)
    return sorted(out)


plan = []        # (local path, path in repo)
for d in sorted(glob.glob(os.path.join(a.runs_root, 'run_*', 'out'))):
    name = os.path.basename(os.path.dirname(d))[4:]
    if a.only and a.only not in name: continue
    plan += [(p, f'{a.prefix}/{name}/{os.path.relpath(p, d)}') for p in files(d, KEEP_OUT)]
for d in sorted(glob.glob(os.path.join(a.results_root, '*'))):
    if not os.path.isdir(d): continue
    name = os.path.basename(d)
    if a.only and a.only not in name: continue
    plan += [(p, f'{a.prefix}/{name}/results/{os.path.relpath(p, d)}') for p in files(d, KEEP_RES)]

api = HfApi(token=os.environ.get('HF_TOKEN') or None)   # None: huggingface_hub reads the saved token file
have = {}
try:
    for e in api.list_repo_tree(a.repo, path_in_repo=a.prefix, recursive=True, repo_type='dataset'):
        if hasattr(e, 'size') and e.size is not None: have[e.path] = e.size
except Exception as ex:          # prefix not there yet
    if 'not found' not in str(ex).lower() and '404' not in str(ex):
        print('listing the dataset failed:', type(ex).__name__, str(ex)[:200])
        if not a.dry_run: sys.exit(4)
        print('(dry run: treating every file as new)')
todo = [(p, r) for p, r in plan if have.get(r) != os.path.getsize(p)]
gb = sum(os.path.getsize(p) for p, _ in todo) / 1e9
print(f'{len(plan)} file(s) selected, {len(plan) - len(todo)} already on {a.repo} (same size), {len(todo)} to upload ({gb:.2f} GB)')
for p, r in todo[:400]: print(f'  {os.path.getsize(p) / 1e6:9.1f} MB  {r}')
if len(todo) > 400: print(f'  ... and {len(todo) - 400} more')
if a.dry_run or not todo:
    print('dry run: nothing uploaded' if a.dry_run else 'nothing to upload'); sys.exit(0)
for i in range(0, len(todo), a.batch):
    chunk = todo[i:i + a.batch]
    names = sorted({r.split('/')[2] for _, r in chunk})
    api.create_commit(a.repo, repo_type='dataset', operations=[CommitOperationAdd(path_in_repo=r, path_or_fileobj=p) for p, r in chunk],
                      commit_message=f"Turing backup: {', '.join(names)[:120]} ({len(chunk)} files)")
    print(f'uploaded {min(i + a.batch, len(todo))}/{len(todo)}')
print('done: https://huggingface.co/datasets/' + a.repo + '/tree/main/' + a.prefix)
PY
