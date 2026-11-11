# Runbook: Mass Flood Watch

What runs, where, and how to fix or restart each piece. Repository: Horus331/mass-flood-watch. Site: https://horus331.github.io/mass-flood-watch/

## What runs

| piece | where | schedule | output |
|---|---|---|---|
| Sentinel (storm state) | `sentinel.yml` | every ~10 min | `docs/site/data/status.json`, `/status/` |
| Live feeds (radar rain, nowcast, FLASH, NWM, snow, reports) | `live_feeds.yml` | hourly | `docs/site/data/live/` |
| Forecast (HRRR × 8 members → LISFLOOD-FP → closures) | `forecast.yml` | 4 × a day | `docs/site/data/forecast_latest/`, frames branch |
| Keeper (re-runs whatever GitHub's schedule skipped) | `keeper.yml` | chain, restarted every 3 h | — |
| MassDOT events log | `events_log.yml` | every 15 min | events archive |
| Storm archive follow-up | `archive_followup.yml` | twice a day | `docs/proto/archive/` |
| Failure Issues | `failure_issue.yml` | on each live run | GitHub Issue "Failing: <workflow>" |
| Golden storm | `golden.yml` | on model code changes | pass / fail |
| Turing queue | `proto/turing/queue_runner.slurm` on Turing | every 30 min | jobs from `turing-queue` branch |

## When something fails
1. An Issue "Failing: <workflow>" opens (GitHub emails the owner). Open the linked run, read the failed step's log.
2. A network source down (NOAA, USGS, NWS): nothing to do; the next run retries. `/status/` shows the source red / amber.
3. A code error: fix, push; the next scheduled run (or a manual "Run workflow") closes the Issue.
4. A run stuck: cancel it in Actions; concurrency groups prevent overlaps, so the next one starts cleanly.

## Restart each piece
- **Any workflow:** Actions → the workflow → Run workflow (main).
- **Keeper chain broken:** run `keeper.yml` by hand.
- **Turing queue:** on a login node, `cd ~/mass-flood-watch && sbatch proto/turing/queue_runner.slurm`. Stop it: `touch ~/scratch/queue/STOP`
  (remove the file and submit once to restart). Pause new submissions only: `"paused": true` in `jobs.json` on `turing-queue`.
- **Site not updating:** check the Pages deployment in Actions; the site is `docs/` on `main`.

## Container
`ghcr.io/horus331/mass-flood-watch:latest` (and `:<sha>`), rebuilt by `container.yml` when `container/` changes; pushed only if the golden
storm passes inside it. On Turing: `apptainer build mfw.sif docker://ghcr.io/horus331/mass-flood-watch:latest`. If the pull asks for a login,
set the package to public (GitHub → Packages → mass-flood-watch → Package settings → Change visibility). New Python package: add it to
`container/requirements.in`, run `container.yml` with `lock = true`.

## Re-run a storm
- Replay on the CPU set-up: `parity_test.yml` with a case `{name, storm, box, hours, env}` (catalogue storms: `docs/proto/obs/catalog.json`).
- On Turing (GPU solve + CPU post): add a job to `jobs.json` on `turing-queue` (kinds in `proto/turing/queue_kinds.json`).

## Rotate a token
Tokens live only as GitHub Actions secrets (Settings → Secrets and variables → Actions): `HF_TOKEN`, `HF_ARCHIVE_TOKEN` (planned),
`API_USGS_PAT`, `EARTHDATA_TOKEN`. To rotate: create the new token at the provider, paste it into the secret, revoke the old one. Never put a
token in a file. `secret_scan.yml` scans the full git history for leaked tokens.

## Roll back a release
`git revert <commit>` on `main` and push (never force-push `main`). If the model changed on purpose, rerun `golden.yml` with `update = true`
and add a line to `docs/CHANGELOG.md`.
