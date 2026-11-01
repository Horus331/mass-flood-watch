# District 3 forecast map: percentile chosen for rain volume — result (1 Nov 2026)

Pre-registration: `DISTRICT_VOLCAL_PREREG.md` (commit 440c4ad4, before the diagnostic ran). Run: GitHub Actions `probe.yml` on branch
`terrain-fix`, run 41319326871; files `district/volcal_rain.json`, `district/volcal_decision.json`. All 18 cycles complete, no missing HRRR or
MRMS hours. Reproduce: `python proto/forecast_volcal.py decide --rain docs/proto/forecast/district/volcal_rain.json`.

## Verdict: not adopted. The District 3 map keeps `LF_HRRR_NBHD=20,90` and stays a shadow run.

**Choice on the development cycles (pooled District 3 volume / MRMS):**

| P | 50 | 60 | 70 | 75 | **80** | 85 | 90 (live) | raw |
|---|---|---|---|---|---|---|---|---|
| dev ratio | 0.39 | 0.52 | 0.73 | 0.87 | **1.08** | 1.36 | 1.85 | 0.74 |

P\* = 80.

**Held-out check (14 issue cycles of the 7 OOS storms, District 3 domain):**

| setting | median \|ln volume ratio\| | median \|ln area ≥ 25 mm ratio\| | pooled volume ratio | pooled CSI ≥ 25 mm | pooled CSI ≥ 50 mm | volume ratio inside the storm's own box |
|---|---|---|---|---|---|---|
| 20,90 (live) | 0.716 | **0.150** | 1.80 | 0.650 | 0.496 | 1.23 |
| **20,80 (P\*)** | **0.481** | 0.362 | 1.39 | 0.640 | 0.574 | 0.95 |
| 20,75 | 0.493 | 0.864 | 1.25 | 0.631 | 0.583 | 0.86 |
| 20,70 | 0.372 | 0.784 | 1.15 | 0.626 | 0.601 | 0.79 |
| raw | 0.343 | 0.598 | 0.99 | 0.593 | 0.572 | 0.70 |

Conditions: (1) volume closer — **yes** (0.48 vs 0.72); (2) area ≥ 25 mm closer — **no** (0.36 vs 0.15); (3) CSI ≥ 25 mm not lower by more
than 0.02 — yes (0.640 vs 0.650). One condition fails, so P\* is not adopted.

## What this says

- **The volume bias of 20,90 is real out of sample**, not a sep2023 quirk: on the 14 held-out cycles the district forecast carries 1.8 × the
  radar's rain (per cycle 0.11–3.2 ×; 12 of 14 cycles above 1.2 ×). Halving the radius never fixed this (`DISTRICT.md` §C).
- **But 20,90 gets the extent of moderate rain (≥ 25 mm) about right** (median area ratio within ±16 %); lowering the percentile shrinks
  that area too much. Caveat on the pre-registered area metric: in 4 of the 14 cycles both the radar and 20,90 cover (almost) the whole
  district with ≥ 25 mm (sep2021, aug2026), where the ratio is ~1 by saturation; in jul2023 long, aug2023 short and both aug2023b cycles
  20,90 covers 2.8–4.5 × the radar's ≥ 25 mm area. The excess is in how much rain falls inside the right area — the high end — so a single percentile cannot fix volume
  and extent together. P80 does improve the ≥ 50 mm placement (CSI 0.57 vs 0.50), which the decision rule did not use.
- **Inside each storm's own 20 × 20 km box** 20,90 is 1.23 × the radar and P80 0.95 ×: the box forecasts live on that surplus, consistent
  with `DISTRICT.md` §B (less spreading loses box sites).

## Next step (not run; would need a new pre-registration)

Fix intensity without shrinking extent: keep the 20,90 footprint (where it rains) and rescale amounts to the raw HRRR's domain volume each
hour (a volume-preserving neighbourhood, `DISTRICT.md` option b), or probability-matched mean of the 8 lagged members. Either is checked the
same way (`forecast_volcal.py` with an extra variant), then by one District 3 GPU hindcast against the radar run. Until then the District 3
map is not shown as a warning map (unchanged).
