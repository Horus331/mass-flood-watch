# Catch basins as a capped, clogging-aware sink (`LF_INLETS=1`): result

**Verdict: not adopted.** This is the pre-registered rule (`INLETS_PREREG.md`, PROTOCOL v2 §5a, k = 1, all 23 held-out storms scored).

- **Ranking is unchanged.** Pooled site recall at the 3 % flag budget is 0.194 with and without inlets: 19 of 98 sites on 98 sites. The gain is
  +0.000, against the required +0.04. Its lower bound is −0.033. FSS at 300 m drops by 0.0009.
- **Per storm, the sink swaps one site for another and nothing more.** sep2018w gains 1 site and jul2023c loses 1. No other held-out storm
  changes at 3 %.
- **At the rule (`p_close ≥ 0.5`), the sink trims flags.**
  - Mean flagged share falls from 0.43 % to 0.36 %.
  - Lift rises from 6.27 to 6.62.
  - Site recall falls from 0.082 to 0.071 (8 rule-hit sites → 7).
- **The failure mode from DRAINS.md is weaker but not gone.** Pooled over the held-out storms, flags drop 18 % and rule-hit sites drop 12.5 %,
  a ratio of 0.68. The pre-registered "in proportion" threshold is 0.8, so the check is negative.
- **On sep2023 in Leominster city the failure mode is clearer.** City flags fall from 58 to 37 (−36 %) and the city's rule-hit sites from 29 to
  26 (−10 %), a ratio of 0.29.
  - At an equal 3 % budget, sep2023 goes from 30 to 29 sites. That is within the 2-site limit, so no explanation is required.
  - The Leominster gauges get worse: mean absolute rise error goes from 0.23 m to 0.49 m. As in DRAINS, drained water is not returned at
    the outfalls.

**What this means.** A physically capped inlet sink still behaves like a slightly higher depth threshold. It removes flags (and with them a
smaller share of documented sites), and it does not reorder segments. Most documented sites are not served by MassDOT inlets: those inlets sit
on state highways, and municipal inlets are known only in Leominster. Where a site did flood, the real inlets were overwhelmed or blocked anyway.

`LF_INLETS` stays **opt-in and off by default**. It is a "drains working" sensitivity layer that is more physical than `LF_DRAINS`. The leaf-season
clog value (0.65) was not tested, because no catalogue storm falls in 15 Oct – 30 Nov.

## Numbers (`inlets_v1a/eval.md`, `compare.json`, `eval.json`)

| PROTOCOL v2 §5a | value | pass |
|---|---|---|
| 1. 3 % site recall gain ≥ +0.04 | +0.000 (98 sites) | no |
| 2. one-sided 5 % lower bound > 0 | −0.033 | no |
| 3. FSS 300 m at 3 % not lower | −0.0009 | no |
| 4. no ≥ 3-site storm loses > 1 site | worst −1 (jul2023c) | yes |
| 5. rule lift ≥ 0.8 × base | 6.62 vs 6.27 | yes |

| sep2023 (calibration, report only) | box 3 % hits / 79 | box rule hits / share | Leominster city rule hits / flagged segments | sink m³/s | gauge mean abs rise error (m) |
|---|---|---|---|---|---|
| base | 30 | 29 / 2.16 % | 29 / 58 | – | 0.23 |
| inlets (clog 0.50) | 29 | 26 / 1.65 % | 26 / 37 | 582 | 0.49 |
| clog 0 (sensitivity) | 27 | 25 / 1.56 % | 25 / 34 | 919 | 0.53 |
| clog 0.65 (sensitivity) | 29 | 26 / 1.67 % | 26 / 38 | 447 | 0.47 |

Sink size on the held-out boxes:
- MassDOT inlets only: 1,386–5,607 inlets, 111–434 m³/s, on 1,085–4,049 cells;
- Leominster and Fitchburg boxes, with the DPW network: 13,800–14,400 inlet points, 526–582 m³/s.

The base arm agrees with the published parity catalogue; for example, sep2021's rule share is 2.41 % in both.

Reproduce: `python proto/inlets_eval.py --dir docs/proto/drains/inlets_v1a`.

## What was built

| file | what |
|---|---|
| `sim/colab/lf_inlets.py` | The sink. Each inlet removes water from its 20 m cell at most at the HEC-22 sag-grate capacity at 0.15 m ponding (0.174 m³/s) × (1 − clog). Clog is 0.50, or 0.65 from 15 Oct to 30 Nov. A pipe network's summed capacity is limited to the full-flow capacity of its largest known pipe. Inlets are MassDOT inventory inlets plus Leominster DPW pipe nodes × 0.587. Selftest included. |
| `sim/colab/w9_lisflood.py` | Blocks marked `LF_INLETS (begin)` / `(end)`, plus one meta line. They reuse the `mfw-drains` infilfile sink and its probe (volume ratio 1.00 in every run), on the CPU. The default path is unchanged. |
| `proto/inlets_table.py`, `.github/workflows/inlets_table.yml` | Compact MassDOT inlet and conveyance tables in `proto/data/inlets/` (250 kB, `inventory.json` = counts). |
| `.github/workflows/inlets_test.yml` | The plan's tasks on Actions CPU at a pinned commit. Each job uploads an artifact, and one collect job makes a single commit to main. |
| `proto/turing/run_inlets.slurm`, `collect_scores.slurm`, `inlets_plan.py`, `plans/inlets_v1.json` | The Turing path, with queue kinds `run_inlets` and `collect_scores`. `collect_scores` is generic and also used by the NWM AMC test. |
| `proto/inlets_eval.py` | The pre-registered scorer. |

**Turing.**
- The `inl1_runs` array ran every w9 (LISFLOOD-FP CPU), but 49 of 50 tasks then failed at the `score_v2` step, and one failed in w9 (see
  `inlets_v1/manifest.json` and the `w9_tail.txt` files).
- The Slurm stdout with the `score_v2` error stays on Turing (`~/mass-flood-watch/inlets_*.out`). The same step passes on Actions, so the
  cause is in the Turing environment, not the scorer.
- Per amendment A1, the decision runs are the Actions runs in `inlets_v1a/`. `inlets_v1/` holds only the failure markers.

Sources:
- FHWA HEC-22, *Urban Drainage Design Manual*, 3rd ed. (FHWA-NHI-10-009), §4.4.6.
- [Poirier, Rahman & van Duin 2025](https://trid.trb.org/View/2553879) (leaf litter: 35 % of the clean-inlet conveyance).
- [Hao, Mu & Shi 2021, *Water* 13(6) 826](https://www.mdpi.com/2073-4441/13/6/826).
- MassDOT Stormwater Asset Database snapshot 2026-10-29 (`docs/proto/stormwater/SNAPSHOT.md`).
- City of Leominster DPW Drain_Pipe.
