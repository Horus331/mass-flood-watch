#!/bin/bash
# Surrogate batch pipeline (docs/proto/surrogate/SURROGATE.md) as one queueable job: waits until the plan exists (scenarios.py plan, run on
# the login node because it needs the internet), then submits  gen array -> (inputs) -> train -> HF backup  with Slurm dependencies.
#   PLAN=~/scratch/surrogate/plan_b1.json  PER_TASK=8  [WAIT_H=20]  [INPUTS=1]  [K=]  [PLANS=<plan list for train, default PLAN>]
#SBATCH -J surr_pipe
#SBATCH -p short
#SBATCH -N 1
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -t 23:00:00
#SBATCH -o surr_pipe_%j.out
set -uo pipefail
cd ~/mass-flood-watch
: "${PLAN:?set PLAN}"; PER_TASK=${PER_TASK:-8}; WAIT_H=${WAIT_H:-20}; INPUTS=${INPUTS:-1}
t0=$(date +%s)
until [ -s "$PLAN" ] && python3 -c "import json,sys; json.load(open('$PLAN'))" 2>/dev/null; do
  [ $(( $(date +%s) - t0 )) -gt $(( WAIT_H * 3600 )) ] && { echo "plan $PLAN not there after ${WAIT_H} h"; exit 1; }
  sleep 300
done
N=$(python3 -c "import json,math; print(math.ceil(json.load(open('$PLAN'))['n'] / $PER_TASK))")
echo "plan $PLAN: $N array tasks of $PER_TASK"
G=$(sbatch --parsable --array=0-$((N-1))%4 --export=ALL,PLAN=$PLAN,PER_TASK=$PER_TASK proto/turing/surrogate_gen.slurm) || exit 1
DEP=afterok:$G
if [ "$INPUTS" = 1 ]; then I=$(sbatch --parsable proto/turing/surrogate_inputs.slurm) && DEP=$DEP:$I; fi
T=$(sbatch --parsable --dependency=$DEP --export=ALL,PLANS=${PLANS:-$PLAN}${K:+,K=$K} proto/turing/surrogate_train.slurm)
B=$(sbatch --parsable --dependency=afterany:$G --export=ALL,RUNS_ROOT=$HOME/scratch/surrogate,PREFIX=runs/surrogate proto/turing/backup_hf.slurm)
echo "gen $G inputs ${I:-none} train $T backup $B"
