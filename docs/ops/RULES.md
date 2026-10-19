# Coordination rules

These rules keep the agents and the GPU machines from stepping on each other. If a rule blocks you, ask the lead; do not work around it.

## 1. File ownership

Each path has one owner, and only the owner edits it. Everyone else reads it and sends changes to the lead.

| Owner | Paths |
|---|---|
| **Lead** | `sim/colab/*.py` (engine, worker, launchers), `sim/solver.py`, `sim/validate.py`, `docs/queue/jobs.json`, `docs/progress.json` (work log), `docs/reviews/`, and any path not listed elsewhere (site HTML, `refresh/`, `tools/`, `.github/workflows/`) |
| **Research scout** | `docs/research/` |
| **Secretary** | `docs/ops/` |
| **Review agents** | nothing. They are read-only and report findings to the lead |
| **Mo** | accounts, tokens and secrets; starting, stopping and restarting GPU sessions; approving decisions |

- Agents never commit, push, send, post or submit anything. The lead commits.
- No agent reads, prints, copies or handles tokens (`HF_TOKEN`, Kaggle or Colab secrets).
- A new agent gets its own directory before it starts. The lead adds it to this table and to the roster.

## 2. The queue (`docs/queue/jobs.json`)

- **Only the lead edits jobs.json.** Other agents propose jobs as a JSON snippet in their report to the lead.
- Workers read jobs.json from GitHub `main` on every poll, so a change takes effect only once it is pushed.
- Job status lives on Hugging Face (`queue/status/<id>.json`). Only workers write it. The lead may write a final `failed`/`superseded` status on a dead claim.
- Every new job must have:
  - `GIT_SHA` pinned (no unpinned jobs)
  - a `note` that matches its env
  - the smallest honest `gpu_gb`
  - `after` for every job whose output or verdict it depends on
- Use `only` for a real hardware reason only. Never use it to "keep a machine free"; use priority for that, and remove the `only` once the reason is gone.
- Prune `done` jobs from the list after their result is in the work log. `after` checks HF status, so pruning never breaks a dependency.
- **Priority bands:**
  - 12: smoke tests and validate checks
  - 10: the experiment that answers the current question, plus its same-commit control
  - 8 to 9: follow-ups
  - 5 to 7: background work (coast, tiles, corpus)
  - A low-value job never sits above a high-value one only because it was added earlier.

## 3. Gating new code (smoke test first)

1. Any commit that changes `w4`/`w8`/`solver.py` (engine), `w6`/`validate.py` (scoring) or `w5` (tiles) gets a **smoke job pinned to that exact sha**. A smoke job is a short `HOURS` window, run end to end through every step the real jobs use, with the same flags (for example `BREACH=1`).
2. Every multi-hour job at that sha lists the smoke in `after`. Re-pinning jobs to a newer sha means re-gating them on a smoke test at the newer sha, or showing that the diff cannot affect their steps.
3. Changes to scoring alone can be gated by a `score` job (w6 only) on an existing run. That takes minutes, not a full smoke run.
4. Experiments that depend on another experiment's verdict wait for it with `after`. Do not queue them in parallel and hope.

## 4. Naming

- **Run dir** (fixed by the worker): `runs/<RUN><TAG>_<RES>m`. For coast runs: `runs/coast_<TILE>_<STORM>[_slr<cm>]_<RES>m`.
- **TAG**: `_v<physics>` plus a short variant code, lower-case with no separators. Examples: `_v3`, `_v3n07` (Manning x0.7), `_v3dryAK`, `_v3brch`. One TAG means one scientific configuration.
- **Job id** = `<RUN><TAG>_<RES>m`. A **retry** of the same configuration adds `b`, `c`, … to the id and keeps the TAG (so it writes the same run dir), for example `sep2023_v3b_30m`. If the earlier attempt reached the upload step, change the TAG instead, so no stale files are mixed in.
- **Smoke jobs**: id `smoke_<sha8>`, `RUN=test_*` (or a `TAG` starting `_smoke_`), so they never mix with real runs in the run picker.
- **Score, tiles and coast jobs**: `score_<rundir-name>_<sha8>`, `tiles_<rundir-name>`, `coast_<tile>_<storm>_<res>m`.
- Never reuse a job id for a different configuration.

## 5. When a job is dead

- A `running` claim with **no heartbeat for more than 40 min is dead**. Any eligible worker may re-claim it, and that claim counts as a new attempt.
- **After 2 attempts** (failed or dead), no worker will touch it again; a human has to look. Before re-queuing, fix the cause, then use a new id (retry suffix) so it gets a fresh budget.
- A `failed` job with 1 attempt **is retried automatically**, and the retry runs **all** steps again, including a 4 h w4. If a job fails in w6 or w5 after w4 uploaded, the lead should replace it with a `score` or `tiles` job, not let the full retry happen.
- **Kaggle sessions die at 12 h, and Colab sessions can drop without warning.** Do not let a worker claim a job that cannot finish before its session ends.
- Superseded or removed jobs whose status still says `running` are harmless to workers, but should get a final status so dashboards stay honest.

## 6. How results flow

1. **Run**: the worker runs w4 (or w8), w5 and w6. w4 uploads `runs/<dir>/`, with `meta.json` last; the presence of `meta.json` means the run is complete.
2. **Score**: w6 writes `validation.json` (and `validation_hsnap.json` when there is an hsnap) into the same run dir. The worker uploads the log to `queue/logs/<id>.log` and sets the status to `done`/`failed`.
3. **Lead**: reads `validation.json` and the log, and checks the provenance in `meta.json` (git_sha, antecedent source, hours) and the upload lines.
4. **Work log**: the lead writes the result and verdict to `docs/progress.json`, then edits the queue (follow-ups, re-pins, pruning).
5. **Secretary**: refreshes `docs/ops/ROSTER.md` (machines, schedule, issues).
6. **Scout**: research that bears on a result goes to `docs/research/` and is flagged to the lead.

Runs on different commits are compared only after both have been scored by the same `validate.py` commit; re-score the older one with a `score` job.
