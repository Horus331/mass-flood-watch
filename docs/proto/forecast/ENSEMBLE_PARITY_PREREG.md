# Forecast ensemble at the parity physics: pre-registration of the rerun (15 Nov 2026)

Committed before any run. Results go to `ENSEMBLE_PARITY.md` and `ensemble_parity.json` whatever they are.

## Why
The out-of-sample ensemble test (`ENSEMBLE.md` §4, the basis of the live "2 of 8" rule) was run at CN × 0.91 and the default time step,
before the parity baseline (`parity/BASELINE.md`: `LF_PARITY=1`, CN × 0.88). The paper cannot quote it as the deployed model
(`paper/OUTLINE.md` §8–9, item 3). This reruns it at the parity physics. Nothing else changes.

## What is run
Exactly the cases of `ENSEMBLE.md` (`python proto/forecast_ens.py matrix --which all`: the 4 development ensembles, the 7 out-of-sample
storms at long and short lead, the same members, boxes, hours and `LF_HRRR_NBHD=20,90`, plus the MRMS controls), on GitHub Actions
(`forecast_ens.yml`, `physics=parity`, `which=all`): `LF_PARITY=1`, `LF_CN_SCALE=0.88`, AMC II, `LF_INFIL_MMH=2`, `LF_QOUT=1`, 20 m CPU.
Outputs to `docs/proto/forecast/ensemble_parity/`; report by `FENS_DIR=ensemble_parity FENS_REPORT=ensemble_parity.json python
proto/forecast_ens.py report`. The terrain edits (T2), the 12 h spin-up, the radar nowcast and the rise rule of the live forecast are
**not** added: this measures the physics change alone, against the same rules. A technical failure is rerun unchanged; no storm or
member is dropped after a result is seen.

## What is reported (no new decision)
The tables of `ENSEMBLE.md` §4 at the parity physics, next to the legacy numbers: per storm and lead, single cycle / any of 4 / 2 of 4 /
2 of 8 / MRMS control; pooled over the 7 out-of-sample storms and over all 9.
**Check (stated now):** "2 of 8" keeps the §4 verdict if, pooled over the 7 out-of-sample storms, its site recall is ≥ the single cycle's at
both leads and its mean flagged share is ≤ 2 × the single cycle's + 1 point. If it fails, the live rule is not changed by this file;
the failure is reported to the advisors and a change would need its own pre-registration.

Cost: 124 matrix jobs, about 1 h each (about 120 runner-hours, at most 12 at a time so the live forecast keeps runners).
