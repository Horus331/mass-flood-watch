#!/bin/bash
# Read-only diagnostics written back to the `turing-queue` branch as diag/<request id>.md (never to main), for when nobody can log in:
# scratch space and quota, the Slurm limits that refuse submissions (QOSMaxSubmitJobPerUserLimit), sacct of named jobs (elapsed, peak memory),
# sizes of named run folders under $LF_WORK, and the tails of named log files.  Nothing is changed on Turing.
#   queue: {"id": "diag_1", "kind": "diag", "env": {"JOBS": "2442643,2442677", "LOGS": "roadflood_2442643.out",
#           "WORKDIRS": "run_sep2023_proto_site_d3_sep2023", "WLOGS": "d3all_v1/d3all_aug2021/w9_tail.txt"}, "sbatch": {"partition": "short", "time": "00:30:00"}}
#   JOBS     Slurm job ids (comma list)                         -> sacct (state, elapsed, MaxRSS, ...)
#   LOGS     Slurm output files in the repo folder on Turing (comma list of plain file names, e.g. roadflood_2442643.out, plan_display_2443000_1.out)
#   WORKDIRS folders under $LF_WORK (comma list, a or a/b)       -> du of the folder, its out/ and results/ (count + size of each snapshot kind)
#   WLOGS    files under $LF_WORK (comma list, a/b/file)          -> tail
#   TAIL     lines per tail (default 60, max 400)
#SBATCH -J diag
#SBATCH -p short
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -t 00:30:00
#SBATCH -o /dev/null
set -o pipefail
source proto/turing/env.sh >/dev/null 2>&1 || true
REPO=$PWD
RID=${SLURM_JOB_NAME#q_}; [[ "$RID" =~ ^[A-Za-z0-9_.-]{1,60}$ ]] || RID=diag_${SLURM_JOB_ID:-local}
TAIL=${TAIL:-60}; [[ "$TAIL" =~ ^[0-9]{1,3}$ ]] && [ "$TAIL" -le 400 ] || TAIL=60
OUTF=$(mktemp); W=${LF_WORK:-$HOME/scratch/lisflood}
sec() { echo; echo "## $1"; echo; echo '```'; }
end() { echo '```'; }
run() { echo "\$ $*"; timeout ${TO:-60} "$@" 2>&1 | cut -c1-400 | head -n ${MAXL:-200}; }
okname() { [[ "$1" =~ ^[A-Za-z0-9_][A-Za-z0-9_.-]{0,120}$ ]] && [[ "$1" != *..* ]]; }
okpath() { [[ "$1" =~ ^[A-Za-z0-9_][A-Za-z0-9_.-]*(/[A-Za-z0-9_][A-Za-z0-9_.-]*){0,3}$ ]] && [[ "$1" != *..* ]]; }
{
  echo "# Turing diagnostics: $RID"; echo; echo "$(date -u +%FT%TZ) on $(hostname), job ${SLURM_JOB_ID:-}, repo $(git -C $REPO rev-parse --short HEAD 2>/dev/null)"
  sec "disk and quota"
  run df -h $HOME $HOME/scratch $W
  run readlink -f $HOME/scratch
  run quota -s
  MNT=$(df --output=target $W 2>/dev/null | tail -1)
  command -v lfs >/dev/null && run lfs quota -h -u $USER "$MNT"
  command -v beegfs-ctl >/dev/null && run beegfs-ctl --getquota --uid $USER
  command -v mmlsquota >/dev/null && run mmlsquota --block-size auto
  ls /etc/motd >/dev/null 2>&1 && grep -i -m5 -E "scratch|quota|purge" /etc/motd 2>/dev/null
  TO=900 MAXL=60 run bash -c "du -sh $W/* 2>/dev/null | sort -h | tail -n 50"
  TO=600 run du -sh $W
  end
  sec "Slurm limits (submit cap)"
  run sacctmgr -n -P show assoc user=$USER format=cluster,account,partition,qos,maxsubmit,maxjobs,grptres,maxwall
  run sacctmgr -n -P show qos format=name,maxsubmitpu,maxjobspu,maxtrespu,maxwall,grpjobs,grpsubmit,flags
  run sinfo -o '%P %a %l %D %G %c %m'
  MAXL=120 run scontrol show partition
  run squeue -u $USER -o '%i %j %P %T %M %l %R %b'
  echo "array tasks expanded: $(squeue -u $USER -r -h 2>/dev/null | wc -l), job records: $(squeue -u $USER -h 2>/dev/null | wc -l)"
  end
  sec "GPU queue position (short / quick)"
  run sprio -u $USER
  run sinfo -N -p short -o '%N %f %G %T' --noheader | sort -k2 | uniq -f1 -c
  MAXL=60 run squeue -p short -t PD --sort=-p -o '%i %u %Q %b %r'
  MAXL=40 run squeue -p quick -t PD --sort=-p -o '%i %u %Q %b %r'
  run bash -c "squeue -p short -t R -h -o '%b %N' | sort | uniq -c | sort -rn | head -30"
  run sinfo -p short -N -o '%N %G %C %T' --noheader
  end
  if [ -n "${JOBS:-}" ]; then
    sec "sacct $JOBS"
    if [[ "$JOBS" =~ ^[0-9]{1,12}(_[0-9]{1,5})?(,[0-9]{1,12}(_[0-9]{1,5})?){0,40}$ ]]; then
      MAXL=300 run sacct -P -j "$JOBS" --format=JobID,JobName%30,Partition,State,ExitCode,Submit,Start,End,Elapsed,MaxRSS,ReqMem,AllocTRES%60,NodeList
    else echo "JOBS refused (digits, commas, _task only)"; fi
    end
  fi
  for D in ${WORKDIRS//,/ }; do
    sec "work folder $D"
    if okpath "$D" && [ -d "$W/$D" ]; then
      TO=600 run du -sh "$W/$D"
      [ -d "$W/$D/out" ] && run ls -la "$W/$D/out"
      if [ -d "$W/$D/results" ]; then
        TO=600 run du -sh "$W/$D/results"
        for x in wd elev Vx Vy Qx Qy; do
          n=$(ls "$W/$D/results/" 2>/dev/null | grep -c "\.$x$"); f=$(ls "$W/$D/results/"*.$x 2>/dev/null | tail -1)
          echo "$x: $n files, last $(basename "${f:-none}") $( [ -n "$f" ] && stat -c %s "$f") bytes"
        done
        run ls -la "$W/$D/results" | tail -n 12
      fi
    else echo "not a folder (or name refused): $D"; fi
    end
  done
  for L in ${LOGS//,/ }; do
    sec "tail $L"
    if okname "$L" && [ -f "$REPO/$L" ]; then run ls -la "$REPO/$L"; MAXL=$TAIL run tail -n $TAIL "$REPO/$L"; else echo "missing (or name refused): $L"; fi
    end
  done
  for L in ${WLOGS//,/ }; do
    sec "tail \$LF_WORK/$L"
    if okpath "$L" && [ -f "$W/$L" ]; then MAXL=$TAIL run tail -n $TAIL "$W/$L"; else echo "missing (or name refused): $L"; fi
    end
  done
} > $OUTF 2>&1
# scrub anything token-like before it leaves Turing (the repo is public)
sed -i -E 's/(hf_|ghp_|github_pat_)[A-Za-z0-9_]{10,}/\1<redacted>/g' $OUTF
R=$(git -C $REPO remote get-url --push origin); T=$(mktemp -d)
git clone -q --depth 3 -b turing-queue --single-branch "$R" $T || { echo "clone failed"; exit 1; }
mkdir -p $T/diag; cp $OUTF $T/diag/$RID.md; rm -f $OUTF
cd $T && git add diag/$RID.md && git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "diag $RID" || exit 0
for i in 1 2 3 4 5; do git pull -q --rebase "$R" turing-queue && git push -q "$R" HEAD:turing-queue && break; sleep $((RANDOM % 20 + 10)); done
cd /; rm -rf $T
