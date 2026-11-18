# Gauge-rise bias against storm size (18 Nov 2026; descriptive, Paper 1 review M8)

All 25 non-locked District 3 catalogue storms, parity runs at the operational physics (`parity/catalog/*/score.json`); rain from each
run's own features (99th percentile of segment storm totals in the box; maximum segment peak-hour rain); top-3 % site recall from
`obs/round2/score_round2.json`. Script `proto/bias_by_storm.py`, numbers `bias_by_storm.json`. Nothing fitted, no model change.

- **The model under-predicts river rises on almost every storm:** mean signed rise error negative on 22 of the 24 storms with a gauge.
- **The shortfall is largest on small storms.** Median ratio of modelled to observed rise: **0.15** on the 9 storms with a box 99th-percentile
  storm total below 60 mm, **0.56** on the 15 above (0.35 without the two development storms). Rank correlation of the ratio with storm
  total 0.41, with peak-hour rain 0.35 (n = 24).
- **Site recall follows the same pattern.** Top-3 % recall pooled: **0.06** (2 of 34 sites) on the small storms vs **0.33** (50 of 150) on the
  large ones (0.29, 17 of 59, without the development storms). Rank correlation of per-storm recall with storm total 0.53 (n = 25).

The 60 mm split was chosen after looking at the table and is for reading only; the rank correlations use no split. With 1–3 gauges per
storm, the ratios are noisy (four storms have a modelled rise of 0).

**Reading.** The light-storm bias is systematic, not a few outliers, and it is where the model's skill is lost: on storms below ~60 mm the
model barely raises the rivers and finds almost no reported sites. That fits the calibration (one curve-number scale chosen on the largest
storm, Sept 2023) and points to rain excess on small storms (initial abstraction, antecedent wetness, urban runoff) as the next physics
item. Any fix must go through the protocol (pre-registered, held-out); the soil-wetness test T4 C stays stopped as Mo asked.
