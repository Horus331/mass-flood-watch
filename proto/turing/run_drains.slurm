#!/bin/bash
# Storm-drain capacity test (sim/colab/lf_drains.py): Leominster, with and without the City of Leominster pipe network, on the CPU solver.
#   1. copy the pipe file to Turing yourself (it is shared for research only: never commit it, never put it under the repo):
#        mkdir -p ~/private && chmod 700 ~/private && scp leominster_drain_pipe.zip turing:~/private/
#   2. cd ~/mass-flood-watch && sbatch proto/turing/run_drains.slurm
#      CASES="base drains design" sbatch --export=ALL proto/turing/run_drains.slurm     # add the generic design-storm fallback case
#      STORMS_RUN=aug2026 sbatch --export=ALL proto/turing/run_drains.slurm            # one storm only
# Why CPU: the sink is a patched LISFLOOD-FP 8.2 'infilfile' (infevap.cpp FPInfiltration), run-tested on the CPU acceleration solver.
#   The CUDA acceleration solver has no infiltration at all; an opt-in CUDA kernel (LF_PATCH_CUDA_SINK=1 at build time, then
#   LF_DRAIN_ALLOW_CUDA=1) exists but is untested, so this job builds and uses $LF_WORK/build_cpu/lisflood (env.sh would pick the GPU build).
# Cost: 1.0 M cells, 20 m; measured 37 min per 48 h of storm on 4 CPU cores (COMPUTE.md), so ~15-25 min per run on 16 cores; 4 runs.
# Outputs (results/drains_<storm>_<case>/): score.json, points.json, flood_meta.json (aggregate drain numbers only), no maps; the per-cell
#   sink raster is deleted by w9 after each run.  Nothing is published unless PUBLISH=1 (then only those aggregate json files).
#SBATCH -J roadflood_drains
#SBATCH -p long
#SBATCH -N 1
#SBATCH -n 16
#SBATCH --mem=64G
#SBATCH -t 12:00:00
#SBATCH -o roadflood_drains_%j.out
set -eo pipefail
source proto/turing/env.sh
export LF_NO_UPLOAD=1 OMP_NUM_THREADS=${SLURM_NTASKS:-16}
export BOX=${BOX:-168000,908000,188000,928000} RES=${RES:-20} LF_LOSS=${LF_LOSS:-cn} LF_CN_SCALE=${LF_CN_SCALE:-0.91} LF_INFIL_MMH=${LF_INFIL_MMH:-2} LF_QOUT=${LF_QOUT:-1}
DRAINS_FILE=${DRAINS_FILE:-$HOME/private/leominster_drain_pipe.zip}
CASES=${CASES:-base drains}; STORMS_RUN=${STORMS_RUN:-sep2023 aug2026}
case "$(realpath -m "$DRAINS_FILE")" in "$(realpath -m .)"/*) echo "DRAINS_FILE is inside the repo: move it to ~/private"; exit 1;; esac
[[ " $CASES " == *" drains "* ]] && [ ! -f "$DRAINS_FILE" ] && { echo "no $DRAINS_FILE (copy the pipe zip there first)"; exit 1; }

# CPU build with the mfw-drains patch (rebuilt only when missing or older than the patched source)
python - <<'PY'
import os, sys; sys.path.insert(0, 'sim/colab'); import w9_lisflood as W
src = f'{W.WORK}/src'
if not os.path.isdir(src): z, ver, url = W.get_lisflood(); W.extract_all(z, src)
s = W.find_source(src); st = W.patch_drain_sink(s); exe = f'{W.WORK}/build_cpu/lisflood'
if not (st['cpu'] and os.path.exists(exe) and os.path.getmtime(exe) > os.path.getmtime(f'{s}/infevap.cpp')):
    exe, cuda = W.build_lisflood(s, want_cuda=False)
print('CPU build', exe); print(W.probe_sink(exe, False))
PY
export LF_EXE=$LF_WORK/build_cpu/lisflood LF_EXE_CUDA=0

for STORM in $STORMS_RUN; do
  case $STORM in
    sep2023) export T0=2023-09-11T16:00Z HOURS=${HOURS_SEP2023:-48};;
    aug2026) export T0=2026-08-03T04:00Z HOURS=18;;
    *) echo "unknown storm $STORM"; continue;;
  esac
  export STORM
  for C in $CASES; do
    unset LF_DRAINS LF_DRAIN_DESIGN
    [ "$C" = drains ] && export LF_DRAINS=$DRAINS_FILE
    [ "$C" = design ] && export LF_DRAIN_DESIGN=1
    NAME=drains_${STORM}_${C}; export RUN_DIR=runs/${STORM}_proto_${NAME}
    echo "== $NAME (LF_DRAINS ${LF_DRAINS:+set} LF_DRAIN_DESIGN ${LF_DRAIN_DESIGN:-0})"
    time python sim/colab/w9_lisflood.py
    OUT=$LF_WORK/run_${STORM}_proto_${NAME}/out; mkdir -p results/$NAME
    python proto/score.py --run-dir "$OUT" --storm $STORM --out results/$NAME/score.json | tail -12 || true
    python proto/validate_points.py --run-dir "$OUT" --storm $STORM --out results/$NAME/points.json | tail -8 || true
    cp $OUT/meta.json results/$NAME/flood_meta.json
  done
done

python - $STORMS_RUN <<'PY'
import json, os, sys
for s in sys.argv[1:]:
    print(f'== {s}: case | LSR+labels hit10 hit30 | random-road hit10 hit30 | peak wet km2 | gauge rise error m | drains m3/s')
    for c in ('base', 'drains', 'design'):
        d = f'results/drains_{s}_{c}'
        if not os.path.exists(f'{d}/flood_meta.json'): continue
        m = json.load(open(f'{d}/flood_meta.json')); p = json.load(open(f'{d}/points.json'))['summary'] if os.path.exists(f'{d}/points.json') else {}
        g = json.load(open(f'{d}/score.json')).get('gauges', []) if os.path.exists(f'{d}/score.json') else []
        a, r = p.get('all', {}), p.get('random_road_points', {}); dr = m['inputs'].get('drains')
        print(f"{c:7s} | {a.get('hit_10')} {a.get('hit_30')} | {r.get('hit_10')} {r.get('hit_30')} | {m.get('peak_wet_km2')} | "
              + ', '.join(f"{x['site']} {x.get('rise_error_m')}" for x in g) + f" | {dr.get('total_q_m3s') if isinstance(dr, dict) else '-'}")
PY
if [ "${PUBLISH:-0}" = "1" ]; then for C in $CASES; do for S in $STORMS_RUN; do bash proto/turing/publish.sh drains_${S}_${C} || true; done; done; fi
