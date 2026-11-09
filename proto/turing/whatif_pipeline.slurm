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
# solver on GPUs (released as soon as each solve ends), then the post-processing on CPUs, then pack + publish (8 Nov 2026)
A=$(STAGE=solve sbatch --parsable -p $PART --gres=gpu:1 --array=$IDX%$CONC --export=ALL proto/turing/whatif_runs.slurm) || exit 1
B=$(STAGE=post sbatch --parsable -p $PART --dependency=afterany:$A --array=$IDX%16 --export=ALL proto/turing/whatif_runs.slurm) || exit 1
P=$(sbatch --parsable --dependency=afterany:$B --export=ALL proto/turing/whatif_pack.slurm) || exit 1
echo "whatif solves $A on GPUs (array $IDX, $CONC at a time, partition $PART), post-processing $B on CPUs, pack + publish $P"
