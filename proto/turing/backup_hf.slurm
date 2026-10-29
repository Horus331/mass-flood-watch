#!/bin/bash
# Back up Turing outputs to the Hugging Face dataset (proto/turing/backup_hf.sh) as a CPU job, so the queue can run it.
#   ONLY=<name filter>  RUNS_ROOT=<dir with run_*/out>  PREFIX=<path in dataset, default runs/turing>
#SBATCH -J backup_hf
#SBATCH -p short
#SBATCH -N 1
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 08:00:00
#SBATCH -o backup_hf_%j.out
cd ~/mass-flood-watch && source proto/turing/env.sh >/dev/null 2>&1
bash proto/turing/backup_hf.sh ${ONLY:+--only $ONLY} ${RUNS_ROOT:+--runs-root $RUNS_ROOT --results-root /nonexistent} ${PREFIX:+--prefix $PREFIX}
