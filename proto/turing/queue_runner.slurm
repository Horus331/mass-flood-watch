#!/bin/bash
# Turing job queue tick (proto/turing/queue_runner.py, docs/proto/turing/QUEUE.md). Re-submits itself every TICK_MIN minutes (Turing has no
# scrontab), pulls main + the `turing-queue` branch, submits new whitelisted requests, writes status back to `turing-queue`.
#   start once:  cd ~/mass-flood-watch && sbatch proto/turing/queue_runner.slurm
#   stop:        touch ~/scratch/queue/STOP            (or "paused": true in jobs.json stops submissions but keeps polling)
#SBATCH -J flood_queue
#SBATCH -p short
#SBATCH -N 1
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -t 00:20:00
#SBATCH -o /dev/null
QDIR=${QDIR:-$HOME/scratch/queue}; TICK_MIN=${TICK_MIN:-30}; mkdir -p $QDIR
exec >> $QDIR/runner.log 2>&1
echo "== tick $(date -u +%FT%TZ) on $(hostname) job ${SLURM_JOB_ID:-local}"
cd ~/mass-flood-watch || exit 1
# 1. next tick first, so one failure does not end the chain (singleton: never two queued ticks)
if [ ! -f $QDIR/STOP ]; then
  sbatch --parsable --begin=now+${TICK_MIN}minutes --dependency=singleton proto/turing/queue_runner.slurm || echo "resubmit failed"
else echo "STOP file present: not resubmitting"; fi
source proto/turing/env.sh >/dev/null 2>&1
# compute nodes cannot fetch over https here ("could not read Username"); use the deploy-key ssh URL (the pushurl) for every fetch
R=$(git remote get-url --push origin)
git pull -q --rebase --autostash "$R" main || echo "pull main failed"
# 2. the request branch
if [ ! -d $QDIR/repo/.git ]; then git clone -q -b turing-queue --single-branch "$R" $QDIR/repo || { echo "no turing-queue branch"; exit 0; }; fi
git -C $QDIR/repo pull -q --rebase "$R" turing-queue || echo "pull turing-queue failed"
# 3. tick
python proto/turing/queue_runner.py tick --qdir $QDIR || echo "tick failed"
# 4. status back (only if it changed)
cd $QDIR/repo && git add -A status.json STATUS.md 2>/dev/null
if ! git diff --cached --quiet; then
  git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "queue status $(date -u +%FT%TZ)"
  for i in 1 2 3; do git pull -q --rebase "$R" turing-queue && git push -q "$R" HEAD:turing-queue && break; sleep 10; done
fi
# keep the log short
tail -n 2000 $QDIR/runner.log > $QDIR/runner.tmp && mv $QDIR/runner.tmp $QDIR/runner.log
