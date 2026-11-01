# District 3 forecast map: a neighbourhood percentile chosen for rain volume on the development storms (pre-registered 1 Nov 2026)

Fixed and committed **before the rain diagnostic below was run**. Scope: **the District 3 (whole-district, Turing) forecast map only** — the
shadow run that `DISTRICT.md` found over-flags 3.2× (888 vs 276 segments at P ≥ 0.5 on 11 Sept 2023, 18z cycle). The public box forecasts keep
`LF_HRRR_NBHD=20,90` and 2 of 8: `DISTRICT.md` §B already showed that every setting with less spreading loses 2–3 of 29 held-out box sites,
and nothing here changes that decision.

## 1. Idea

`DISTRICT.md` §C traced the district excess to rain volume: the 90th percentile over a 20 km disk lifts every cell near a convective core to
near-core totals, which nearly doubles the district rain (1.91 × MRMS) and gives 6 × the radar's area above 100 mm. Over a 20 × 20 km box
sitting on the core that surplus compensates for a displaced core; over a 78 × 90 km district it is a false alarm. So the district map
should use the percentile that makes the **district-wide** forecast rain volume match the radar, keeping the 20 km footprint, with the
percentile chosen on the development storms only and checked on held-out storms.

## 2. Settings and choice (development storms only)

- Grid: `LF_HRRR_NBHD = 20,P` for P ∈ {50, 60, 70, 75, 80, 85, 90}; the raw field (0,50) is reported for reference.
- Domain: the District 3 run box `128000,856000,206000,946000` (EPSG:26986), 0.01° points, storm totals from the HRRR issue cycle to the
  ensemble end time of `proto/forecast_ens.ENSEMBLES` (capped at the cycle horizon), against MRMS Pass2 over the same hours.
- **P\*** = the P whose pooled District 3 volume ratio (Σ HRRR / Σ MRMS) over the 4 development cycles (sep2023 12z and 18z, aug2021 06z
  and 12z) is closest to 1 in |ln ratio|; a tie goes to the higher P. (`proto/forecast_volcal.py choose`.)

## 3. Held-out check and decision (`proto/forecast_volcal.py decide`)

Held-out cycles: the long- and short-lead issue cycles of the 7 out-of-sample storms of `ENSEMBLE.md` §4 (jul2021, sep2021, sep2022, jul2023,
aug2023, aug2023b, aug2026): 14 cycles, District 3 domain. P\* replaces 20,90 **for the District 3 map** only if all three hold:

1. **Volume.** The median over the held-out cycles of |ln(District 3 volume ratio)| is lower for P\* than for 20,90.
2. **Area.** The median of |ln(area ≥ 25 mm ratio)| (forecast area / radar area, +0.5 cells each) is lower for P\* than for 20,90.
3. **Placement.** The pooled CSI of the ≥ 25 mm area (Σ intersections / Σ unions) is not lower than 20,90's by more than 0.02.

If P\* = 90 the item stays open. Reported whatever the verdict: every setting's held-out numbers, the volume ratio inside each storm's own
box (which explains why the boxes need the surplus), and the dev numbers.

## 4. Flood-level confirmation (planned; not part of the decision above)

If P\* passes, one District 3 GPU hindcast from the sep2023 18z cycle with `LF_HRRR_NBHD=20,P*` (Turing, the `hindcast_d3_sep2023_18z`
set-up of `DISTRICT.md`) is compared with the radar run `turing/d3_sep2023_p` with the `DISTRICT.md` §1 metrics (ratio_n, ratio_km within
0.7–1.3, CSI). sep2023 is a development storm, so this checks the flagged-segment count, it is not held-out skill. Held-out flood-level
checks need District 3 radar runs of the held-out storms (the `d3all_v1` display runs) and 2 × 7 District 3 forecast runs; they are left
for after 3 Nov. Until then the District 3 map stays a shadow run, labelled as such.

Results go to `docs/proto/forecast/DISTRICT_VOLCAL.md` and `docs/proto/forecast/district/volcal_*.json`.
