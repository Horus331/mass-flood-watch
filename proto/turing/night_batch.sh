#!/bin/bash
# Tonight's GPU batch (23 Oct 2026). Run from ~/mass-flood-watch on the login node: bash proto/turing/night_batch.sh
# 1) parity confirmation (docs/proto/parity/PARITY.md), 2) clean-baseline GPU reruns of the public replays (LF_PARITY=1, CN x0.88,
# 5-min frames, velocity) + District 3, packed for the site after each run, 3) District 3 forecast hindcast (Sept 11 2023, 18z HRRR).
set -e
git pull -q --rebase --autostash
L=~/night_batch.log; date > $L
sub() { local id; id=$(sbatch --parsable "$@"); echo "$id $*" >> $L; echo $id; }
P="--export=ALL"
# 1) parity confirmation (PUBLISH=1 so the small result files reach GitHub); SKIP_PARITY=1 skips it
export PUBLISH=1
if [ "${SKIP_PARITY:-0}" != 1 ]; then
BOX=157000,882000,177000,902000 STORM=jul2023 HOURS=18 NAME=parity_jul2023_gpu_rain_dt1 LF_PARITY=1 sub $P proto/turing/run_storm.slurm >/dev/null
BOX=162000,908000,182000,928000 STORM=sep2023 HOURS=36 NAME=parity_sep2023_gpu_rain_dt1 LF_PARITY=1 sub $P proto/turing/run_storm.slurm >/dev/null
BOX=157000,882000,177000,902000 STORM=jul2023 HOURS=18 NAME=parity_jul2023_gpu_rain LF_INFIL_MODE=rain sub $P proto/turing/run_storm.slurm >/dev/null
BOX=162000,908000,182000,928000 STORM=sep2023 HOURS=36 NAME=parity_sep2023_gpu_rain LF_INFIL_MODE=rain sub $P proto/turing/run_storm.slurm >/dev/null
fi
# 2) clean baseline replays on GPU, then pack each for the site under a preview key (promoted after a check)
C="LF_PARITY=1 LF_CN_SCALE=0.88 LF_SAVEINT=300 LF_VOUT=1"
j=$(export $C; BOX=168000,908000,188000,928000 STORM=sep2023 HOURS=48 NAME=leominster_sep2023_p sub $P proto/turing/run_storm.slurm)
NAME=leominster_sep2023_p STORM=sep2023 SITE=leominster_p LIVE=leominster_sep2023 sub $P --dependency=afterok:$j proto/turing/pack_site.slurm >/dev/null
j=$(export $C; BOX=168000,875000,188000,895000 STORM=aug2021 HOURS=48 NAME=worcester_aug2021_p sub $P proto/turing/run_storm.slurm)
NAME=worcester_aug2021_p STORM=aug2021 SITE=worcester_p LIVE=worcester_aug2021 sub $P --dependency=afterok:$j proto/turing/pack_site.slurm >/dev/null
j=$(export LF_PARITY=1 LF_CN_SCALE=0.88 LF_SAVEINT=1800; BOX=128000,856000,206000,946000 STORM=sep2023 HOURS=48 NAME=d3_sep2023_p sub $P proto/turing/run_storm.slurm)
POOL=4 FLOW=0 NAME=d3_sep2023_p STORM=sep2023 SITE=d3_p LIVE=d3_sep2023 sub $P --dependency=afterok:$j proto/turing/pack_site.slurm >/dev/null
# 3) District 3 forecast hindcast from the HRRR cycle issued ~4 h before the Sept 2023 storm
LF_PARITY=1 LF_CN_SCALE=0.88 FORCE=1 INIT=2023-09-11T18Z PUBLISH=0 NAME=hindcast_d3_sep2023_18z KEY=hindcast_d3 sub $P proto/turing/run_forecast.slurm >/dev/null
squeue -u $USER >> $L; echo SUBMITTED >> $L; cat $L
