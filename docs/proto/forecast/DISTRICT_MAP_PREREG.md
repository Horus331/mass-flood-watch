# A whole-District 3 forecast map instead of the 20 km boxes: pre-registration (frozen 26 Nov 2026, before any run below)

Mo asked on 26 Nov 2026 (09:12 ET) to drop the dashed 20 km boxes and run all of District 3 at once. The whole-district run over-forecasts
about 3x with the live rain spreading (`DISTRICT.md`: 888 vs 276 segments on 11 Sept 2023), so the boxes stay public until a district
version passes this test. Two candidates (`DISTRICT.md`, "Fix the district map separately"), approved by Mo for testing on 26 Nov:

- **(a) D3, 2 of 8:** the whole district on Turing for each of the 8 ensemble members (`ENSEMBLE.md`), live settings (20,90 spreading);
  a segment is "likely closed" when at least 2 of the 8 member runs close it, the same rule as the boxes.
- **(b) D3, volume-preserving:** one district run from the issue cycle, with each hour's 20,90 field rescaled so that its total over the
  District 3 model domain equals the raw HRRR total over the same domain (spreading keeps the placement, drops the surplus); P ≥ 0.5.

## Storms, labels, set-up (fixed now)
- **Decision pool:** the 7 out-of-sample storms of `ENSEMBLE.md` §4 (jul2021, sep2021, sep2022, jul2023, aug2023, aug2023b, aug2026;
  29 sites), short lead (the issue cycle of `ENSEMBLE.md`). sep2023 and aug2021 are run too but are development storms (reported only).
  The 5 locked storms are not opened.
- **Reference per storm:** the same district domain driven by the observed radar rain (`d3_*_p` set-up of `DISTRICT.md`); flagged =
  P ≥ 0.5.
- **Model:** the live District 3 Turing set-up (`proto/turing/run_forecast.slurm`, T2 terrain, 20 m), labels and strict
  `label_recall` of `ENSEMBLE.md`.
- **Box forecast for comparison:** the published `ENSEMBLE.md` 2-of-8 short-lead result on the same 7 storms (0.276 of 29 sites at
  3.2 % of segments flagged).

## Measures
1. **ratio_n:** flagged segments of the candidate / flagged segments of the radar run, pooled over the 7 storms.
2. **Site recall:** share of the 29 out-of-sample sites on a flagged segment, district-wide (the box forecast can only catch sites inside
   its boxes; the district map is scored on all of them).
3. **Lift:** site recall / share of District 3 segments flagged.
4. **CSI** against the radar run (as in `DISTRICT.md`), for ranking.

## Pass rule (per candidate, all three)
1. 0.7 ≤ ratio_n ≤ 1.5 (pooled).
2. Site recall ≥ 0.276 (the box forecast's).
3. Lift ≥ 2.

If both pass, the higher CSI wins; within 0.01, (b) wins (one run per cycle instead of eight). If neither passes, the boxes stay and the
result goes to `PROJECT_LOG.md` §6. If one passes, the map shows the district forecast in place of the boxes **after Mo sees
screenshots and says yes**; the boxes stay as a fallback when Turing is not available in time.

## Order and cost
Runs on Turing only after Turing's clone is reset to the rewritten history (paused 25 Nov). (b) first: 9 storms × (1 candidate + 1 radar
reference where it does not exist yet) ≈ 18 GPU runs. (a): 9 × 8 = 72 GPU runs (~4 GPU-hours per storm set, `DISTRICT.md`). Nothing is
tuned after the first number is seen; a changed rule is a new pre-registration.

## Execution note (27 Nov 2026, before any district run of this test; rules and pass line unchanged)
- Turing's clone was reset to the rewritten history on 27 Nov 01:50 UTC; the runs go through the job queue (`proto/district_map_eval.py jobs`).
- **Radar references:** all 9 storms are rerun on the radar rain with exactly the candidate's live settings (`forecast_d3.slurm`: CN × 0.88
  AMC II, LF_PARITY=1, 2 mm/h, LF_QOUT=1, notch fix, channel enforcement, T2 terrain), storm windows of w9 `STORMS`, instead of reusing the
  older `d3_*` runs, so candidate and reference differ only in the rain.
- **Candidate (b)** = `LF_HRRR_NBHD=20,90` + `LF_HRRR_VOLPRES=1` (`sim/colab/hrrr_rain.py`: each hour's spread field multiplied by
  raw domain total / spread domain total, the same model cells), HOURS = issue cycle to the ensemble end of `ENSEMBLE.md` (as the box runs).
- **Site recall:** the 29 sites are the strict sites of the `ENSEMBLE.md` short-lead box runs (issue cycle, `forecast/ensemble/<member>/seg.json`),
  each matched district-wide in the candidate run (strict 30 m); a site is hit when any of its matched segments is at P ≥ 0.5.
- Scoring code `proto/district_map_eval.py score` (committed with this note). Candidate (a) (8 members) is queued only after (b) is scored.
