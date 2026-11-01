# Turing job queue (no login needed)

Turing jobs used to need Mo at the laptop: VPN, OnDemand, an Authenticator approval, then typing. The queue removes that for routine work.
Turing has no `scrontab` (checked 29 Oct 2026: "scrontab is disabled on this cluster"), so a tiny CPU job re-submits itself every 30 min
(`proto/turing/queue_runner.slurm`, partition `short`, 1 core, 2 GB, under a minute of work). Each tick:

1. submits the next tick first (`--dependency=singleton`, so there is never more than one waiting);
2. pulls `main` (the code) and the branch **`turing-queue`** (the requests, `jobs.json`);
3. submits every new request whose `kind` is in `proto/turing/queue_kinds.json` (`proto/turing/queue_runner.py`);
4. polls Slurm (`sacct`) for the jobs it started and writes `status.json` + `STATUS.md` back to `turing-queue`, only when something changed.

`main` is never pushed by the queue, so requests and status do not redeploy the public site.

## Safety

- Only the Slurm scripts listed in `queue_kinds.json` can run, and each kind lists the env keys and sbatch options it accepts.
- Values may contain only `[A-Za-z0-9_.,:=/@+%~-]`: no spaces, quotes, `;`, `$` or backticks, so a request cannot carry shell code.
- Keys like `PATH`, `LD_*`, `PYTHON*`, `BASH_ENV`, `SLURM_*` are refused.
- Anyone who can push to this GitHub repository can still change those scripts on `main`. Keep write access to the repository limited to Mo.
- Stop everything: `touch ~/scratch/queue/STOP` on Turing (the chain ends at the next tick), or `"paused": true` in `jobs.json` (no new
  submissions, status keeps updating).

## Requests

`jobs.json` on `turing-queue`:

```json
{"paused": false,
 "jobs": [
  {"id": "surr_gen_b1", "kind": "surrogate_gen", "env": {"PLAN": "~/scratch/surrogate/plan_b1.json", "PER_TASK": "8"}, "sbatch": {"array": "0-23%4"}},
  {"id": "surr_inputs", "kind": "surrogate_inputs"},
  {"id": "surr_train_b1", "kind": "surrogate_train", "env": {"PLANS": "~/scratch/surrogate/plan_b1.json"}, "after": ["surr_gen_b1", "surr_inputs"]},
  {"id": "bk_surr_b1", "kind": "backup_hf", "env": {"RUNS_ROOT": "~/scratch/surrogate", "PREFIX": "runs/surrogate"}, "after": ["surr_gen_b1"]}
 ]}
```

An id is submitted once; to rerun, add a new id. `after` becomes Slurm `afterok` on those requests' jobs.

What-if explorer (docs/proto/whatif/WHATIF.md), one request runs all 32 scenarios and publishes once:
`{"id": "whatif_v1", "kind": "whatif_pipeline", "env": {"CONC": "8", "PART": "short"}}`

**GPU jobs run the solver only** (WPI HPC flagged a GPU left idle for an hour on 1 Nov 2026 while w9's CPU post-processing ran). Split each
run into `"STAGE": "solve"` with `"gres": "gpu:1"` and a CPU-only `"STAGE": "post"` request with the same env, no gres and `"after"` the solve
request (run_storm and run_plan_display; w9 `LF_STAGE`). `"cancel": ["<id>@4-11"]` cancels only those array tasks of a request (e.g. its
pending ones) and leaves the running tasks alone.

Diagnostics without a login (disk/quota, the Slurm submit limits, sacct of named jobs, sizes of run folders, tails of named logs) come back to
this branch as `diag/<id>.md` (`proto/turing/diag.slurm`):
`{"id": "diag_1", "kind": "diag", "env": {"JOBS": "2442643", "LOGS": "roadflood_2442643.out", "WORKDIRS": "run_sep2023_proto_site_d3_sep2023"}}`

Display runs from a plan, no scoring (`proto/turing/run_plan_display.slurm`; e.g. all of District 3 for every catalogue storm,
`proto/turing/plans/d3all_v1.json`); array task j runs PER plan entries in a row, `{"id": "d3all_v1_a", "kind": "run_plan_display", "env": {"PLAN": "proto/turing/plans/d3all_v1.json", "PIN": "<sha>", "IDXS": "0-23", "PER": "1"}, "sbatch": {"array": "0-23%3", "partition": "short", "gres": "gpu:A100:1", "time": "10:00:00", "mem": "160G"}}`

Turing limits per user (sacctmgr, `diag/d3all_diag1.md`, 1 Nov 2026), **every array task counts as one submitted job**:

| QOS / partition | max submitted (pending + running) | GPUs at once | time limit | GPU types |
| --- | --- | --- | --- | --- |
| quick | 20 | **1** | 12 h | A100, H100, H200, L40S, RTX Pro 6000 |
| short (default) | 100 | 12 | 1 day | same as quick |
| long | 100 | 4 | 7 days | A100, L40S, RTX Pro 6000 (no H100/H200) |

A quick array with more than ~18 tasks can never be submitted (the runner keeps deferring it, and the runner stops at the first
deferred request, so everything after it waits too). For FP64 runs ask for any fast-FP64 node by feature, not one gres type:
`"sbatch": {"gres": "gpu:1", "constraint": "A100|H100|H200"}` (run_storm, run_forecast, run_plan_gpu, run_plan_display, forecast_d3).
On 1 Nov 2026 three of the four A100-80G nodes and both H100 nodes were down: an A100-only request waits for 1 node (4 GPUs) plus the
2 × A100-40G on whitehill-0-02, while the H200 node (8 GPUs) is reachable only through the constraint.

## Where results go (no Google Drive)

- Small results (scores, site packs, RESULTS.md): the job scripts push them to `main` through the deploy key (`proto/turing/publish.sh`).
- Large files (runs, model weights): `backup_hf` uploads them to the Hugging Face dataset `mohabeldokla/mass-flood-watch-tiles`, using the
  token saved on Turing (`~/.cache/huggingface/token`).

## Start once

```bash
cd ~/mass-flood-watch && git pull && sbatch proto/turing/queue_runner.slurm
tail ~/scratch/queue/runner.log
```
