# Catch basins as a capped, clogging-aware sink (`LF_INLETS=1`): status and how to score

**Status (31 Oct 2026): queued on Turing. No verdict yet.** The pre-registration is `INLETS_PREREG.md`, committed before any run. This page
records what was built, what is running, and the exact steps that turn the results into a verdict. When the scores land, the verdict section at
the end is filled in from `inlets_v1/eval.md`, whatever it says.

## What was built

| file | what |
|---|---|
| `sim/colab/lf_inlets.py` | The sink. Each inlet removes water from its 20 m cell at most at the HEC-22 sag-grate capacity at 0.15 m ponding (0.174 m³/s) × (1 − clog). Clog is 0.50, or 0.65 from 15 Oct to 30 Nov. The summed capacity of a pipe network is limited to the full-flow capacity of its largest known pipe. `python sim/colab/lf_inlets.py` runs the selftest. |
| `sim/colab/w9_lisflood.py` | Three blocks, marked `LF_INLETS (begin)` / `(end)`, plus one meta line. They reuse the `mfw-drains` infilfile sink and its probe, and force a CPU build. Off by default; the default path is unchanged (w9 `--selftest` passes). |
| `proto/inlets_table.py`, `.github/workflows/inlets_table.yml` | Compact inlet and conveyance tables from the MassDOT stormwater snapshot on HF, committed to `proto/data/inlets/` (250 kB) so Turing needs no network for them. |
| `proto/turing/run_inlets.slurm` + `plans/inlets_v1.json` (`inlets_plan.py`) | One array task = one storm × one arm, on the CPU, at a pinned commit. Each task gets its own `LF_WORK`, then runs the scorers (`prototype`, `score.py`, `validate_points`, `closure_ml extract`, `score_v2`). Queue kind `run_inlets`. |
| `proto/turing/collect_scores.slurm` | Generic. It waits for a plan's tasks, then pushes only small whitelisted json (each ≤ 400 kB) to the plan's `docs/proto/<area>/<dir>` in one commit. Queue kind `collect_scores`; reusable by any plan in the same format. |
| `proto/inlets_eval.py` | The scorer for this test: `BASE.json` / `CAND.json`, then `score_v2.compare` (PROTOCOL v2 §5a, k = 1). It also runs the DRAINS failure-mode check and reports the sep2023 calibration storm and the clog sensitivity. |

Sources:
- FHWA HEC-22, *Urban Drainage Design Manual*, 3rd ed. (FHWA-NHI-10-009), §4.4.6.
- Poirier, Rahman & van Duin 2025, "The Impact of Leaf Litter on the Performance of Catch Basin Inlets" (ASCE EWRI Congress; https://trid.trb.org/View/2553879).
- Hao, Mu & Shi 2021, *Water* 13(6) 826 (https://www.mdpi.com/2073-4441/13/6/826).
- MassDOT Stormwater Asset Database snapshot 2026-10-29 (`docs/proto/stormwater/SNAPSHOT.md`).
- City of Leominster DPW Drain_Pipe (`proto/data/drains/`).

## Tested so far

- `lf_inlets` selftest:
  - the HEC-22 numbers;
  - type and status mapping;
  - clog season;
  - network cap to the largest known pipe;
  - culverts and abandoned inlets dropped;
  - water cells blocked;
  - DPW nodes counted as inlets.
- The other selftests: `inlets_eval`, `inlets_plan`, `queue_runner`, and w9 `--selftest` (33 checks).
- LISFLOOD-FP 8.2 CPU built locally from `tools/lisflood_src` with the `mfw-drains` patch: sink probe volume ratio **1.00**.
- Preview of the sink on the real data (flat-DEM slopes, so the network caps are approximate):
  - **Leominster sep2023 box:** 14,389 inlets (3,141 MassDOT + 11,248 DPW nodes × 0.587). 847 m³/s after clogging, 495 m³/s after the network limit (865 of 1,312 networks capped), on 9,466 cells. For comparison, the DRAINS pipe sink was 440 m³/s on 13,492 cells.
  - **Worcester sep2021 box:** 4,727 MassDOT inlets, 413 m³/s, 3,822 cells. There are no municipal pipes, so no network limit applies.
- Actions smoke test of the w9 path: sep2023 truncated to 6 h, `LF_INLETS=1`, `parity_test.yml` → `docs/proto/drains/inlets_smoke/`. It is not a scored arm; see the result below.

## What is queued (branch `turing-queue`, `jobs.json`)

| id | kind | env | sbatch |
|---|---|---|---|
| `inl1_runs` | `run_inlets` | `PLAN=proto/turing/plans/inlets_v1.json`, `PIN=<commit>` | array `0-49%10`, partition long, 08:00:00 |
| `inl1_collect` | `collect_scores` | same `PLAN`, `WAIT_H=34` | partition long, 1-12:00:00 |

50 runs:
- sep2023: base, inlets, inlets_clog0, inlets_clog065 (report only);
- held-out 23: base and inlets for each storm.

Each run is about 15–40 min on 16 CPU cores. Watch progress in `STATUS.md` on `turing-queue`. Results arrive in
`docs/proto/drains/inlets_v1/<name>/` plus `manifest.json`.

## How to score (when `inlets_v1/manifest.json` is on main)

```bash
git pull
python proto/inlets_eval.py            # -> docs/proto/drains/inlets_v1/{BASE,CAND,compare,eval}.json + eval.md (2000 bootstrap replicates)
```

- Check `manifest.json` first. Every decision storm needs both arms `done`.
- If some failed (see `FAILED` and `w9_tail.txt`), rerun them **unchanged** under a new queue id. Use a one-off plan holding only the missing
  tasks, with the same names and the same `PIN`, then queue `collect_scores` again with `WAIT_H=0` or more. Do not change any setting.
- When all are there, copy the verdict line, the five conditions, the failure-mode check and the sep2023 table from `eval.md` below.
  Explain any sep2023 loss of more than 2 sites at 3 %.

## Verdict

Pending. Fill in from `inlets_v1/eval.md`.
