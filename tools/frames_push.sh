#!/bin/bash
# Move the image sheets of forecast replay packs off the main site to a frames branch of this repository, served by raw.githubusercontent.com
# (CORS *, image/png, 5-min cache).  5-minute frames make every fired forecast cycle 3x bigger; on main that would add tens of MB to the
# repository history per cycle.  The branch holds ONE orphan commit (the current cycle and the one before it), force-pushed every cycle, so
# nothing accumulates.  The packs on main keep their JSON (meta, roads, pieces, refs, network, flow.json) and rain.* ; meta.data_base points
# the viewer at the sheets (viewer.js dbase()).  Same split as tools/district_stub.py for the whole-district replays.
#
#   bash tools/frames_push.sh <branch> <cycle tag> <pack dir> [<pack dir> ...]
#   e.g. bash tools/frames_push.sh frames-forecast_latest 2026110706 docs/site/data/forecast_latest_b1 docs/site/data/forecast_latest_b2
#   FRAMES_META=- : packs without a meta.json (the what-if scenarios): nothing is rewritten; the caller points its index at
#                   https://raw.githubusercontent.com/<repo>/<branch>/{key}/<tag>/ itself (index.json data_base).
#
# Run from the repository root (uses its git credentials: GITHUB_TOKEN in Actions, the deploy key on Turing).  A failed push leaves the
# packs untouched (sheets still in the pack, no data_base): the cycle still publishes, only from main.
set -eo pipefail
BR=$1; TAG=$2; shift 2
[[ "$BR" =~ ^frames-[a-z0-9_]{3,40}$ ]] || { echo "branch must be frames-<prefix>"; exit 2; }
[[ "$TAG" =~ ^[0-9]{8,12}$ ]] || { echo "tag must be digits (cycle yyyymmddhh)"; exit 2; }
REPO=${GITHUB_REPOSITORY:-Horus331/mass-flood-watch}
RM=${FRAMES_REMOTE:-$(git remote get-url --push origin)}
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
mkdir -p "$W/tree"
# what the branch holds now (the previous cycle stays one more cycle: a page opened just before this push still finds its sheets)
# (a private ref, not FETCH_HEAD: other jobs fetch in the same repository on Turing)
if git fetch -q --depth 1 "$RM" "+refs/heads/$BR:refs/frames-tmp/$BR" 2>/dev/null; then git archive "refs/frames-tmp/$BR" | tar -x -C "$W/tree"; fi
python3 - "$W/tree" "$TAG" "https://raw.githubusercontent.com/$REPO/$BR" "$@" <<'PY'
import json, os, shutil, sys
tree, tag, url = sys.argv[1:4]; packs = sys.argv[4:]
keys = [os.path.basename(p.rstrip('/')) for p in packs]
# keep only the previous cycle (the newest tag before this one, over all keys) beside this one; everything older goes
dirs = [(k, t) for k in os.listdir(tree) if os.path.isdir(os.path.join(tree, k)) for t in os.listdir(os.path.join(tree, k))]
prev = max([t for _, t in dirs if t < tag], default=None)
for k, t in dirs:
    if t != prev: shutil.rmtree(os.path.join(tree, k, t))
for k in os.listdir(tree):
    if os.path.isdir(os.path.join(tree, k)) and not os.listdir(os.path.join(tree, k)): os.rmdir(os.path.join(tree, k))
tot = 0; man = []; bases = {}
for p, k in zip(packs, keys):
    mf = os.environ.get('FRAMES_META', 'meta.json'); m = os.path.join(p, mf)
    if mf != '-' and not os.path.exists(m): print('skip (no %s):' % mf, p); continue
    dst = os.path.join(tree, k, tag); os.makedirs(dst, exist_ok=True); n = 0
    for r_, _, fs_ in os.walk(p):   # sub-folders too (tiles/ of a tiled pack)
        for f0 in sorted(fs_):
            f = os.path.relpath(os.path.join(r_, f0), p); s = os.path.join(p, f)
            if f0.endswith('.json') or f.startswith('rain.'):
                if f.startswith('rain.'): shutil.copy(s, dst)
                continue
            os.makedirs(os.path.dirname(os.path.join(dst, f)), exist_ok=True)
            shutil.copy(s, os.path.join(dst, f)); n += 1; man.append(dict(pack=p, file=f))
    sz = sum(os.path.getsize(os.path.join(r, x)) for r, _, fs in os.walk(dst) for x in fs); tot += sz
    bases[p] = f'{url}/{k}/{tag}/'
    print(f'{k}: {n} files, {sz / 1e6:.1f} MB -> {bases[p]}')
open(os.path.join(tree, 'README.md'), 'w').write('Image sheets of the live forecast replays (tools/frames_push.sh). One commit, replaced every cycle; '
                                                  'the viewer reads them through meta.data_base of the packs on main.\n')
print(f'branch total this cycle {tot / 1e6:.1f} MB')
json.dump(dict(files=man, bases=bases), open(os.path.join(os.path.dirname(tree), 'manifest.json'), 'w'))
PY
# one orphan commit with exactly this tree, through the repository's own git (credentials), without touching its index or work tree
export GIT_INDEX_FILE="$W/index"
git --work-tree="$W/tree" add -A .
T=$(git write-tree)
C=$(git -c user.name="${GIT_AUTHOR_NAME:-flood-watch-bot}" -c user.email="${GIT_AUTHOR_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}" commit-tree "$T" -m "frames $TAG")
unset GIT_INDEX_FILE
OK=0; for i in 1 2 3; do git push -q --force "$RM" "$C:refs/heads/$BR" && { OK=1; break; }; sleep $((5 * i)); done
[ $OK = 1 ] || { echo "frames push failed: packs left as they were (sheets on main)"; exit 1; }
# pushed: now (only now) the packs on main drop their sheets and point at the branch
python3 - "$W/manifest.json" <<'PY'
import json, os, sys
M = json.load(open(sys.argv[1]))
for e in M['files']: os.remove(os.path.join(e['pack'], e['file']))
for p in M['bases']:   # sub-folders left empty
    for r_, ds_, fs_ in os.walk(p, topdown=False):
        if r_ != p and not os.listdir(r_): os.rmdir(r_)
mf = os.environ.get('FRAMES_META', 'meta.json')
for p, b in M['bases'].items():
    if mf == '-': continue
    m = os.path.join(p, mf); J = json.load(open(m)); J['data_base'] = b; json.dump(J, open(m, 'w'), separators=(',', ':'))
print('packs on main now JSON only:', ', '.join(sorted(M['bases'])))
PY
echo "pushed $BR ($TAG)"
