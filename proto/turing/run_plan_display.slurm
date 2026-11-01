#!/bin/bash
# Display runs of a plan (proto/turing/plans/<plan>.json, format: proto/turing/inlets_plan.py): w9 LISFLOOD-FP on the GPU at a pinned commit with
# the plan's frozen settings, NO scoring (these feed the public replays, not decisions).  First used by proto/turing/plans/d3all_v1.json
# (all of MassDOT District 3 at 20 m for every catalogue storm).
#   * each run works in its own folder ($LF_WORK/<results_root>/work_<NAME>: w9's probe folders and logs are not shared with other jobs), and the
#     finished run folder is then moved to $LF_WORK/run_<STORM>_proto_<NAME>, where proto/turing/pack_site.slurm looks for it (NAME=<NAME>);
#   * the solver's raw ESRI-ASCII snapshots (results/: .wd/.elev/.Vx/.Vy/.Qx/.Qy every LF_SAVEINT) are deleted as soon as w9 has turned them into
#     out/frames_cm.npz (uint16 cm) and out/vel_frames.npz (float16 m/s); input rasters too (copies of the .par/.bci stay in out/);
#   * out/frames_u8.npz: the 10-min depth frames as 1 byte per cell, the tile code of docs/proto/district/ARCHITECTURE.md §4.2
#     (0 = dry < 3 cm, 1-100 = cm, 101-255 = 1 m + 5 cm x (code - 100)); frames_cm.npz (uint16 cm) stays for pack_site / prototype.py;
#   * nothing is pushed anywhere: storm display data stays on Turing scratch;
#   * $LF_WORK/<results_root>/<NAME>/ gets DONE or FAILED, w9_tail.txt and report.json (runtime, peak memory, raw and kept sizes);
#   * a run that is already DONE (with its out/meta.json) is skipped, so a re-queue with a new id resumes where a time-out stopped;
#   * a run does not start when scratch has less than MIN_FREE_GB free (default 300; a 48 h District 3 run writes ~200 GB of ASCII before cleanup).
#   queue: {"id": "d3all_v1_a", "kind": "run_plan_display", "env": {"PLAN": "proto/turing/plans/d3all_v1.json", "PIN": "<sha on main>",
#           "IDXS": "0-23", "PER": "1"}, "sbatch": {"array": "0-23%2", "partition": "short", "gres": "gpu:1", "time": "16:00:00", "mem": "240G"}}
#   -> array task j runs indices j*PER .. j*PER+PER-1 of IDXS one after the other; without an array all of IDXS runs in one job.
#   Turing limits (diag/d3all_diag1.md on turing-queue, 1 Nov 2026): every array task counts against the per-user submit cap (quick 20,
#   short/long 100); quick also allows only ONE GPU per user at a time (the live forecast runs there), short allows 12 and 1 day.  So display
#   batches go to short. Measured 1 Nov 2026 on L40S: District 3, 30 h storm, solver 908 s (dt capped at 1 s by LF_PARITY), w9 total ~1 h, peak RSS 143 GB.
#   GPU etiquette (WPI HPC, 1 Nov 2026: a GPU idle for an hour during w9's CPU post-processing was flagged): split every run in two requests,
#     STAGE=solve  on a GPU ("gres": "gpu:1"): inputs + solver only (w9 LF_STAGE=solve), raw results left in the work folder;
#     STAGE=post   CPU only (no gres, "after" the solve request, same PLAN/PIN/IDXS/PER/array): w9 LF_STAGE=post, cleanup, frames_u8, report.
#   Without STAGE one job does both (only for runs that are not on a GPU).
#SBATCH -J planDisp
#SBATCH -p short
#SBATCH -N 1
#SBATCH -n 8
#SBATCH --mem=160G
#SBATCH -t 10:00:00
# no GPU by default: a run request sets "gres": "gpu:1" (+ "constraint" if wanted); ADOPT_ONLY=1 requests (CPU) only finish runs that a
# GPU job already computed (cleanup, frames_u8, report)
#SBATCH -o plan_display_%A_%a.out
set -eo pipefail
source proto/turing/env.sh
[[ "${PIN:-}" =~ ^[0-9a-f]{7,40}$ ]] || { echo "PIN must be a commit sha"; exit 2; }
[[ "${PLAN:-}" =~ ^proto/turing/plans/[A-Za-z0-9_]+\.json$ ]] || { echo "PLAN must be proto/turing/plans/<name>.json"; exit 2; }
[[ "${IDXS:-}" =~ ^[0-9]{1,3}(-[0-9]{1,3})?(,[0-9]{1,3}(-[0-9]{1,3})?)*$ ]] || { echo "IDXS must look like 0-9 or 0,3,5-7"; exit 2; }
[[ "${PER:-1}" =~ ^[0-9]{1,2}$ ]] && [ "${PER:-1}" -ge 1 ] || { echo "PER must be 1-99"; exit 2; }
[[ "${MIN_FREE_GB:-300}" =~ ^[0-9]{1,5}$ ]] || { echo "MIN_FREE_GB must be a number"; exit 2; }
STAGE=${STAGE:-}; [[ "$STAGE" =~ ^(|solve|post)$ ]] || { echo "STAGE must be solve or post"; exit 2; }
[ -x "${LF_EXE:-}" ] || { echo "no prebuilt GPU LISFLOOD-FP (proto/turing/build.slurm)"; exit 2; }
nvidia-smi || true
BASEWORK=$LF_WORK; REPO=$PWD; CODE=$BASEWORK/code_$PIN; GPU_EXE=$LF_EXE
( flock 9
  if [ ! -e $CODE/.git ]; then git -C $REPO worktree add --detach -f $CODE $PIN || git -C $REPO worktree add --detach -f $CODE $(git -C $REPO rev-parse $PIN); fi
) 9>$BASEWORK/code_$PIN.lock
cd $CODE; echo "code $(git rev-parse HEAD) in $CODE"
LIST=$(python -c "
import sys
out = []
for part in sys.argv[1].split(','):
    a, _, b = part.partition('-'); out += range(int(a), int(b or a) + 1)
print(' '.join(map(str, out)))" "$IDXS")
if [ -n "${SLURM_ARRAY_TASK_ID:-}" ]; then
  LIST=$(echo $LIST | tr ' ' '\n' | sed -n "$((SLURM_ARRAY_TASK_ID * ${PER:-1} + 1)),$(((SLURM_ARRAY_TASK_ID + 1) * ${PER:-1}))p" | tr '\n' ' ')
  [ -n "${LIST// /}" ] || { echo "array task $SLURM_ARRAY_TASK_ID: beyond IDXS"; exit 0; }
fi
echo "plan $PLAN indices: $LIST"
run_task() {   # one run in a subshell: its env cannot leak into the next one
  IDX=$1
  unset $(env | grep -oE '^LF_[A-Z0-9_]+' | grep -vE '^LF_WORK$') 2>/dev/null || true
  source <(python proto/turing/inlets_plan.py env $PLAN $IDX)
  [[ "${NAME:-}" =~ ^[a-z0-9_]{3,80}$ && "${RESULTS_ROOT:-}" =~ ^[A-Za-z0-9_]+$ && "${STORM:-}" =~ ^[a-z0-9_]+$ ]] || { echo "plan task $IDX not readable"; return 2; }
  R=$BASEWORK/$RESULTS_ROOT/$NAME; RUN=run_${STORM}_proto_${NAME}; FINAL=$BASEWORK/$RUN
  if [ -f $R/DONE ] && [ -f $FINAL/out/meta.json ]; then echo "== task $IDX: $NAME already done, skipped"; return 0; fi
  # w9 names the run folder run_<run name> with run name = last part of RUN_DIR, prefixed with <STORM>_ unless it starts with it
  export LF_WORK=$BASEWORK/$RESULTS_ROOT/work_$NAME RUN_DIR=runs/${STORM}_proto_${NAME}
  LEGACY=$LF_WORK/run_${STORM}_run_${STORM}_proto_${NAME}     # where the first version of this script (RUN_DIR=runs/run_...) left finished runs
  SOLVED=$LF_WORK/$RUN/stage_solve.json
  if [ "$STAGE" = solve ] && [ -f $SOLVED ]; then echo "== task $IDX: $NAME solver already done, skipped"; return 0; fi
  [ "$STAGE" = post ] || { rm -rf $R; mkdir -p $R; }
  mkdir -p $R; rm -f $R/FAILED
  fail() { echo "$1" > $R/FAILED; echo "FAILED $NAME: $1"; [ "$STAGE" = solve ] && rm -rf $LF_WORK/$RUN/results; exit 1; }
  FREE=$(df -P -BG $BASEWORK | awk 'NR==2 {gsub("G", "", $4); print $4}')
  [ "$STAGE" = post ] || [ "${FREE:-0}" -ge "${MIN_FREE_GB:-300}" ] || fail "no_space: ${FREE}G free on scratch < MIN_FREE_GB ${MIN_FREE_GB:-300}"
  echo "== task $IDX: $NAME ($TASK_STORM) stage ${STAGE:-all} box $BOX hours $HOURS, ${FREE}G free  $(date -u +%FT%TZ)"; env | grep -E '^(LF_|BOX|HOURS|STORM|RES|NAME)' | sort | grep -v LF_WORK || true
  export LF_EXE=$GPU_EXE LF_EXE_CUDA=1 LF_NO_UPLOAD=1 OMP_NUM_THREADS=${SLURM_NTASKS:-8} GIT_SHA=$(git rev-parse --short HEAD) LF_STAGE=$STAGE
  TV=""; [ -x /usr/bin/time ] && TV="/usr/bin/time -v -o $R/time_v_${STAGE:-all}.txt"
  if [ "$STAGE" != solve ] && [ -f $LEGACY/out/meta.json ] && [ -f $LEGACY/out/frames_cm.npz ]; then     # finished run under the old folder name: adopt it
    echo "adopting the finished run in $LEGACY"; rm -rf $LF_WORK/$RUN; mv $LEGACY $LF_WORK/$RUN
    T0=$(stat -c %Y $LF_WORK/$RUN/out/run.par 2>/dev/null || date +%s); T1=$(stat -c %Y $LF_WORK/$RUN/out/meta.json)
    tail -c 20000 $LF_WORK/$RUN/out/w9_log.txt > $R/w9_tail.txt 2>/dev/null || true
  elif [ "${ADOPT_ONLY:-0}" = 1 ]; then fail "not run (ADOPT_ONLY=1 and no finished run in $LEGACY)"
  elif [ "$STAGE" = post ]; then          # CPU job: post-process what the GPU solve stage left
    [ -f $SOLVED ] || fail "no solve stage ($SOLVED)"
    T0=$(date +%s)
    $TV python sim/colab/w9_lisflood.py > $R/w9_stdout.txt 2>&1 || { tail -40 $R/w9_stdout.txt; tail -c 20000 $R/w9_stdout.txt > $R/w9_tail.txt; fail w9_post; }
    T1=$(date +%s); tail -c 20000 $R/w9_stdout.txt > $R/w9_tail.txt; rm $R/w9_stdout.txt
  else                                    # solve (GPU only for the solver) or the old single-job mode
    nvidia-smi >/dev/null 2>&1 || fail "no GPU in this job (ask for one: sbatch gres)"
    rm -rf $LF_WORK; mkdir -p $LF_WORK
    T0=$(date +%s)
    $TV python sim/colab/w9_lisflood.py > $R/w9_stdout.txt 2>&1 || { tail -40 $R/w9_stdout.txt; tail -c 20000 $R/w9_stdout.txt > $R/w9_tail.txt; fail w9; }
    T1=$(date +%s); tail -c 20000 $R/w9_stdout.txt > $R/w9_tail_${STAGE:-all}.txt; rm $R/w9_stdout.txt
    if [ "$STAGE" = solve ]; then
      [ -f $SOLVED ] || fail "solve stage left no $SOLVED"
      echo $((T1 - T0)) > $R/solve_wall_s; echo "solved $NAME in $((T1 - T0)) s $(date -u +%FT%TZ)"; return 0
    fi
    cp $R/w9_tail_all.txt $R/w9_tail.txt
  fi
  OUT=$LF_WORK/$RUN/out
  for f in meta.json frames_cm.npz hmax.npy z.npy; do [ -f $OUT/$f ] || fail "no $f"; done
  [ "${LF_VFRAMES:-0}" = 1 ] && { [ -f $OUT/vel_frames.npz ] || fail "no vel_frames.npz"; }
  RAWB=$(du -sb $LF_WORK/$RUN/results 2>/dev/null | cut -f1); RAWN=$(ls $LF_WORK/$RUN/results 2>/dev/null | wc -l)
  find $LF_WORK/$RUN -mindepth 1 -maxdepth 1 ! -name out -exec rm -rf {} +       # raw snapshots + input rasters; out/ keeps what the packer reads
  rm -rf $FINAL; mv $LF_WORK/$RUN $FINAL; rm -rf $LF_WORK                       # where pack_site.slurm finds it
  python - $FINAL/out <<'PY' || fail frames_u8
import sys, numpy as np
out = sys.argv[1]; D = np.load(f'{out}/frames_cm.npz'); cm = D['depth_cm']; hours = D['hours']
code = np.empty(cm.shape, np.uint8)
for i in range(cm.shape[0]):          # one frame at a time: no int32 copy of the whole stack
    c = cm[i].astype(np.int32)
    code[i] = np.where(c < 3, 0, np.where(c <= 100, c, np.clip(100 + np.rint((c - 100) / 5.0), 101, 255))).astype(np.uint8)
np.savez_compressed(f'{out}/frames_u8.npz', depth_code=code, hours=hours,
                    note='depth code per cell: 0 dry (< 3 cm), 1-100 depth in cm, 101-255 = 1 m + 5 cm x (code - 100); rows north -> south (docs/proto/district/ARCHITECTURE.md 4.2)')
print('frames_u8', code.shape, 'wet cells at peak frame', int((code > 0).sum(axis=(1, 2)).max()))
PY
  python - $FINAL/out $R $T0 $T1 "${RAWB:-0}" "${RAWN:-0}" <<'PY'
import json, os, sys, re
out, r, t0, t1, rawb, rawn = sys.argv[1:]; m = json.load(open(f'{out}/meta.json'))
sizes = {f: os.path.getsize(os.path.join(out, f)) for f in sorted(os.listdir(out))}
rss = {}
for st in ('all', 'solve', 'post', ''):
    tv = os.path.join(r, f'time_v_{st}.txt' if st else 'time_v.txt')
    if os.path.exists(tv):
        mm = re.search(r'Maximum resident set size \(kbytes\): (\d+)', open(tv).read()); rss[st or 'all'] = round(int(mm.group(1)) / 1e6, 1) if mm else None
sw = os.path.join(r, 'solve_wall_s'); solve_wall = int(open(sw).read()) if os.path.exists(sw) else None
rep = dict(name=os.path.basename(r), storm=os.environ.get('STORM'), box=m.get('box'), shape=m.get('shape'), t0=m.get('t0'), hours=os.environ.get('HOURS'),
           saveint_s=os.environ.get('LF_SAVEINT'), stage=os.environ.get('LF_STAGE') or 'all', gpu_job_wall_s=solve_wall, wall_s=int(t1) - int(t0),
           solver_s=m.get('runtime_s'), w9_total_s=m.get('total_s'), peak_rss_gb=rss,
           raw_results_gb=round(int(rawb) / 1e9, 2), raw_results_files=int(rawn), out_gb=round(sum(sizes.values()) / 1e9, 3),
           out_mb={k: round(v / 1e6, 1) for k, v in sizes.items() if v > 1e6}, peak_wet_km2=m.get('peak_wet_km2'), rain_total_max_mm=m.get('rain_total_max_mm'),
           rain_missing_hours=m.get('rain_missing_hours'), git_sha=m.get('git_sha'), env=m.get('inputs', {}).get('env'), folder=os.path.dirname(out))
json.dump(rep, open(f'{r}/report.json', 'w'), indent=1); m.pop('frames', None); json.dump(m, open(f'{r}/flood_meta.json', 'w'), indent=0)
print('report', json.dumps({k: rep[k] for k in ('wall_s', 'solver_s', 'peak_rss_gb', 'raw_results_gb', 'out_gb')}))
PY
  echo ok > $R/DONE; echo "done $NAME $(date -u +%FT%TZ)"
}
NFAIL=0
for IDX in $LIST; do ( run_task $IDX ) || NFAIL=$((NFAIL + 1)); done
echo "tasks: $(echo $LIST | wc -w), failed: $NFAIL"
[ $NFAIL = 0 ]
