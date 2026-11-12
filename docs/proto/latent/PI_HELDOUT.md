# Held-out calibration of the chance of flooding (π): result (12 Nov 2026)

Pre-registration: `PREREG_PI_HELDOUT.md`. Turing CPU job 2511076 (`pitest.slurm`, CMD=heldout), 9 T2 replay runs, each storm's fit made
without that storm. Raw: `pi_heldout_t2.json`.

| check | threshold | result | |
|---|---|---|---|
| 1 calibration in the large (reported segments / expected) | pooled 0.67–1.5, every storm 1/3–3 | pooled **0.56**; storms 0.36–2.88 | **fail** (pooled) |
| 2 Leominster sep2023, DPW domain, sep2023 held out | Brier skill > 0; top fifth within ±0.10 | Brier skill **+0.13**; top fifth 0.27 predicted vs 0.24 observed | pass |
| ranking (report sites hit at the deployed share) | reported only | depth rule 0.22 → held-out π **0.35** (147 sites) | |

Per storm, reported segments vs expected: sep2023 119 / 327 (0.36), aug2023 1.40, aug2026 1.93, sep2021 1.36, sep2018 2.88, jul2023 0.85,
jun2020 0.76, sep2022 0.67, sep2018m 0.54.

**Decision (as pre-registered): not adopted. The site keeps "k of 8 forecast runs"; no percentage is shown.**

What it means:
- Fitted without Leominster, the model expects about 2.7 times more *reported* flooded roads in Sept 2023 than were reported; that one
  storm pulls the pooled ratio below the threshold. Without sep2023 the other eight pool to 122 / 107 (1.14), inside the band, but the
  rule was fixed before the run and Leominster is the storm that matters most.
- Against the DPW's complete list for Leominster the held-out π is still well calibrated where it counts (top fifth 27 % predicted vs
  24 % observed) and has positive skill. The miss is in the detection part (how many floods get reported), not in where it floods.
- Held out, π still ranks report sites much better than the depth rule (0.35 vs 0.22). A ranking can use it; a percentage cannot yet.

Next: the forward test keeps archiving π with every forecast; the detection model needs more storms with complete inventories (DPW-type
lists) before a percentage can be shown.
