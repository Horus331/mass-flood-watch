#!/bin/bash
# What-if explorer as one queueable job (docs/proto/whatif/WHATIF.md): submits the GPU scenario array, then ONE pack + publish job
# with afterany (the site redeploys once, with every scenario that finished).
#   [IDX=0-31] [CONC=8] [PART=short] [RERUN=0] [ONLY=<ids for the pack>]   sbatch proto/turing/whatif_pipeline.slurm
#SBATCH -J whatif_pipe
#SBATCH -p short
#SBATCH -N 1
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -t 00:10:00
#SBATCH -o whatif_pipe_%j.out
set -uo pipefail
cd ~/mass-flood-watch
export RERUN=${RERUN:-0}
IDX=${IDX:-0-31}; CONC=${CONC:-8}; PART=${PART:-short}
A=$(sbatch --parsable -p $PART --array=$IDX%$CONC --export=ALL proto/turing/whatif_runs.slurm) || exit 1
P=$(sbatch --parsable --dependency=afterany:$A --export=ALL proto/turing/whatif_pack.slurm) || exit 1
echo "whatif runs $A (array $IDX, $CONC at a time, partition $PART), pack + publish $P"
