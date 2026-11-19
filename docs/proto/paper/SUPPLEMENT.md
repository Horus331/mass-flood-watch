# Paper 1: supplementary material index (draft, 19 Nov 2026)

Proposed contents of the supplement. Nothing here is published beyond the repository. "Fixed" = the date the document states it was
fixed (before any run it governs); "commit" = the first commit containing it in this working copy. This working copy is a shallow clone
whose history starts on 7 Nov 2026, so for documents fixed earlier the commit column shows the import commit `a6d0d4f3f`; the original
commit hashes must be taken from a full clone (`git log --diff-filter=A -- <file>`) before submission.

## S1. Pre-registration documents cited in the paper

| Document | What it fixes | Fixed | Commit |
|---|---|---|---|
| `PROTOCOL.md` (v2) | decision set (23 held-out storms), adoption rule, locked storms | 23 Oct 2026 (v2 revision later) | a6d0d4f3f* |
| `PROTOCOL_v3.md` | protocol revision | 9 Nov 2026 | c91b05879 |
| `transfer/TRANSFER.md` (§1, rules) | Districts 4–6 transfer test, settings frozen | 25 Oct 2026 | a6d0d4f3f* |
| `latent/PREREG.md` | latent-label model (π) | 28 Oct 2026 | a6d0d4f3f* |
| `scoring/PREREG_PI_RANK.md` | ranking by π on Districts 4–6 | 12 Nov 2026 | 4152a2565 |
| `latent/PREREG_PI_HELDOUT.md` | π shown as a percentage (not adopted) | 11 Nov 2026 | 75d482c45 |
| `scoring/PREREG_HYBRID.md`, `PREREG_CROSSING.md` | model + traffic, model + crossing flag (not adopted) | 11 Nov 2026 | 22380e383, fef1af597 |
| `runoff/B0_V2_PREREG.md`, `runoff/NWM_AMC_PREREG.md` | rain-excess variants (not adopted) | 1 Nov, 31 Oct 2026 | a6d0d4f3f* |
| `terrain/PREREG.md` | terrain conditioning T1 / T2 (T2 adopted) | 1 Nov 2026 | a6d0d4f3f* |
| `drains/INLETS_PREREG.md`, `drains/PREREG_C2_ROADS.md` | drain sinks (not adopted) | 31 Oct, 13 Nov 2026 | a6d0d4f3f*, 5963d0bdc |
| `forecast/ENSEMBLE_PARITY_PREREG.md` | forecast ensemble re-test at the deployed physics | 15 Nov 2026 | dcbaac86b |
| `forecast/NOWCAST_WINDOWS_PREREG.md`, `BOX_PERCENTILE_PREREG.md`, `DISTRICT_VOLCAL_PREREG.md` | forecast rain handling | 9 Nov, 9 Nov, 1 Nov 2026 | 6d4bb44b3, 79c4ed649, a6d0d4f3f* |
| `prospective/PREREG_PHASE_LIVE.md` | rain/snow split (artifact fix) | 12 Nov 2026 | b43d0b6e3 |
| `whatif/PREREG_BLOCKED_V2.md`, `PREREG_BLOCKED_V3.md` | blocked-culvert readouts | 12 Nov 2026 | 006f88b8e, 90256d990 |
| `phase1/PARAMETRIC_PREREG.md`, `PARAMETRIC_T2_PREREG.md` | Leominster parametric study | 15, 16 Nov 2026 | ad87c86a9, 585373891 |
| `turing/d3_sep2021_t2_PLAN.md` | held-out District consequence run, reading rule | 18 Nov 2026 | 27078b1c3 |

\* import commit of the shallow clone; replace with the original hash.

## S2. Per-storm tables
- District 3 held-out storms (23 storms, 98 sites): per-storm sites, hits at 1 / 2 / 3 / 5 / 10 %, rule hits, chance
  (`obs/round2/score_round2.json`, runs with group `parity`).
- Districts 4–6 (81 storms, 498 sites): same columns (`transfer/r1/score_d456.json` on branch `transfer-d456`).
- Gauge-rise bias and rain per storm (`parity/bias_by_storm.json`).
- Forecast ensemble per storm and lead (`forecast/ensemble_parity.json`, `ensemble_ci.json`).

## S3. Extra figures and tables
- Fig. S1 (planned as Fig. 9 in the outline, not drawn yet): static vulnerability layer.
- Leominster damage classification (`phase1/LEOMINSTER_MISSES.md`, without the withdrawn stream-distance clause).
- Culvert priority list on the T2 terrain (`phase1/PARAMETRIC_T2.md` §3).
- District consequence runs, both storms (`turing/d3_sep2023_t2/`, `turing/d3_sep2021_t2/`).

## To do before submission
1. Original commit hashes for the starred rows (full clone).
2. Convert the JSON tables to CSV / Excel tables with a column guide.
3. Draw Fig. S1 or drop it.
