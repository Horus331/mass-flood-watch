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

## Where results go (no Google Drive)

- Small results (scores, site packs, RESULTS.md): the job scripts push them to `main` through the deploy key (`proto/turing/publish.sh`).
- Large files (runs, model weights): `backup_hf` uploads them to the Hugging Face dataset `mohabeldokla/mass-flood-watch-tiles`, using the
  token saved on Turing (`~/.cache/huggingface/token`).

## Start once

```bash
cd ~/mass-flood-watch && git pull && sbatch proto/turing/queue_runner.slurm
tail ~/scratch/queue/runner.log
```
