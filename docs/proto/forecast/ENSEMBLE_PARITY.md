# Forecast ensemble at the parity physics: results (16 Nov 2026)

Pre-registration: `ENSEMBLE_PARITY_PREREG.md` (15 Nov, committed before any run). Run: GitHub Actions 43719106258, 124 of 124 jobs
succeeded (13:27–18:44 UTC, 15 Nov). Report: `FENS_DIR=ensemble_parity FENS_REPORT=ensemble_parity.json python proto/forecast_ens.py report`.
Nothing was rerun, dropped or tuned after a result was seen.

## 1. Pre-registered check: PASS

"2 of 8" keeps the `ENSEMBLE.md` §4 verdict if, pooled over the 7 out-of-sample storms, its site recall is ≥ the single cycle's at both
leads and its mean flagged share is ≤ 2 × the single cycle's + 1 point.

| 7 out-of-sample storms | single cycle recall / mean flagged | 2 of 8 recall / mean flagged | limit on flagged | result |
| --- | --- | --- | --- | --- |
| long lead (43 sites) | 0.256 / 1.57 % | 0.326 / 2.75 % | 4.14 % | pass |
| short lead (43 sites) | 0.140 / 1.02 % | 0.302 / 1.91 % | 3.04 % | pass |

The live rule stays as it is. The paper can now quote the ensemble result at the deployed physics.

## 2. Pooled tables as produced (`ensemble_parity.json`)

Site-weighted recall / mean flagged share / max flagged share / lift.

| pooled | single cycle | any of 4 | 2 of 4 | 2 of 8 |
| --- | --- | --- | --- | --- |
| 7 out-of-sample, long (43 sites) | 0.256 / 1.6 % / 3.6 % / 6.10 | 0.372 / 3.7 % / 5.6 % / 4.65 | 0.279 / 2.0 % / 4.5 % / 5.75 | 0.326 / 2.8 % / 5.4 % / 5.53 |
| 7 out-of-sample, short (43 sites) | 0.140 / 1.0 % / 4.5 % / 5.28 | 0.326 / 2.7 % / 5.4 % / 5.06 | 0.233 / 1.7 % / 4.7 % / 5.67 | 0.302 / 1.9 % / 4.8 % / 6.40 |
| all 9, long (145 sites) | 0.104 / 1.2 % / 3.6 % / 7.52 | 0.386 / 3.7 % / 5.6 % / 6.14 | 0.221 / 1.8 % / 4.5 % / 9.63 | 0.248 / 2.5 % / 5.4 % / 8.21 |
| all 9, short (145 sites) | 0.255 / 1.2 % / 4.5 % / 8.92 | 0.310 / 2.6 % / 5.4 % / 7.59 | 0.207 / 1.5 % / 4.7 % / 10.19 | 0.297 / 1.9 % / 4.8 % / 9.43 |

**These numbers are not directly comparable with `ENSEMBLE.md` §4.** The scoring code (`proto/prototype.py`) now matches more of the
reports to a road segment than it did on 23 Oct (same label files): 43 out-of-sample sites instead of 29, 145 instead of 119 in all.
Most of the new matches are reports with approximate locations (`-S`, `-N` ids in Sep 2021 and Aug 2026, and Leominster `L` ids), not
segments newly inside the box. The pre-registration did not foresee this, so section 3 adds a like-for-like comparison.

## 3. Like-for-like: the physics change alone (added after the run, not a decision rule)

Both runs re-scored on the same label sites (those matched in both) and the same in-box segments, with `forecast_ens.py`'s own rules
(`python proto/ensemble_common_rescore.py` → `ensemble_common_ensemble.json`, `ensemble_common_ensemble_parity.json`).

| 7 out-of-sample storms (28 sites) | single cycle | any of 4 | 2 of 4 | 2 of 8 |
| --- | --- | --- | --- | --- |
| long lead, legacy (CN × 0.91) | 0.214 / 1.8 % / L 5.44 | 0.357 / 4.2 % / L 4.09 | 0.214 / 2.3 % / L 4.33 | 0.357 / 3.1 % / L 5.52 |
| long lead, parity (CN × 0.88) | 0.214 / 1.6 % / L 6.46 | 0.321 / 3.7 % / L 4.13 | 0.214 / 2.0 % / L 5.03 | 0.286 / 2.7 % / L 5.03 |
| short lead, legacy | 0.071 / 1.1 % / L 2.75 | 0.286 / 3.2 % / L 4.30 | 0.214 / 1.9 % / L 5.04 | 0.286 / 2.3 % / L 5.80 |
| short lead, parity | 0.071 / 1.0 % / L 3.03 | 0.250 / 2.7 % / L 4.39 | 0.214 / 1.7 % / L 5.89 | 0.250 / 1.9 % / L 6.06 |

The check of section 1 also passes on these numbers (long 0.286 ≥ 0.214, 2.7 % ≤ 4.1 %; short 0.250 ≥ 0.071, 1.9 % ≤ 3.0 %).

Per storm (same labels, 2 of 8, recall / flagged): the parity physics loses one site in Sep 2021 (0.6 → 0.4, both leads) and one in
Jul 2023 at long lead (0.4 → 0.2); everything else is equal. In-sample: Aug 2021 0.583 → 0.5 (one of 12 sites); Sep 2023 unchanged at 12z
(0.141), 0.244 → 0.231 at 18z.

## 4. Plain reading

1. **"2 of 8" still beats the single cycle out of sample at the deployed physics.** The pre-registered check passes on the numbers as
   produced and on the like-for-like numbers.
2. **The parity physics is slightly drier.** It flags 10–20 % fewer segments in every rule. On the same sites it finds 2 fewer
   out-of-sample sites at long lead and 1 fewer at short lead with 2 of 8 (8 vs 10 and 7 vs 8 of 28). Lift is about the same (5.0 vs 5.5
   long, 6.1 vs 5.8 short). With 28 sites, one site moves recall by 0.036, so this is within what small samples allow, but the
   direction is consistent: the 0.88 scaling trades a little recall for fewer flags.
3. **No change to the live forecast.** It already runs the parity physics with 2 of 8.

## 5. Open
- `paper/OUTLINE.md` item 3 can now cite section 1 (as produced) with section 3 as the like-for-like note.
- The growth in matched label sites since October also affects any earlier recall quoted from that time; worth one consistency pass over
  `ENSEMBLE.md`, `HINDCAST.md` and the paper numbers before submission.
