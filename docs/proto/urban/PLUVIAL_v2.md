# Pluvial rule v2 (T3): time of concentration, sub-hourly intensity, HEC-22 inlet capacity with clogging

**Verdict: not adopted.** Under the pre-registered rule (`PROTOCOL.md` §5), v2 fails three of five conditions on the 7 held-out storms (OOS-7):

- Gain: +1 site (5 → 6 of 29) at 3 % flagged.
- Lower bound: −0.19.
- Rule lift: 1.70 against the baseline's 4.67. To catch that one site, the rule flags 7.2 % of segments.

`PROTO_PLUVIAL=2` was therefore **not** added to `prototype.py`. The default and `PROTO_PLUVIAL=1` are unchanged, and v2 should not become the default. The pre-registered ablation, v2 fed with hourly rain, does better: 9 of 29 at a 1.5 % rule share. It still fails the significance test, with lower bound 0.000 against a required > 0 at α = 0.025. v1 also fails on the new baseline (8 of 29, lower bound −0.07). **None of the pluvial rules can be adopted on 29 sites.** The roadmap target (OOS-7 ≥ 11 of 29 at a mean share ≤ 3 %) was not reached by any variant.

Code: `proto/pluvial_v2.py` (`--selftest` passes). Reproduce with `python proto/pluvial_v2.py loso` (about 5 min) → `pluvial_v2/loso.json` and `pluvial_v2/score_{base,v1,v2,v2_hourly}.json`. The last four are `score_v2.py` run outputs, so `python proto/score_v2.py --compare pluvial_v2/score_base.json pluvial_v2/score_v2.json` reproduces each verdict.

## 1. Baseline and setup

- **Baseline:** the new parity catalogue, `docs/proto/parity/catalog/<storm>_<area>_20m`. Settings: CPU, `LF_PARITY=1`, CN × 0.88, all 9 storms with `features_<storm>.csv` and `matches_<storm>.json` (`parity/BASELINE.md`).
  - It is not the published Turing set.
  - It has 29 OOS-7 sites (5/2/4/4/5/6/3), not 27, because of the bridge-deck matching.
  - Its mean OOS rule share is 0.91 %, and it catches 5 of 29 sites at 3 %.
- **Candidates:** every candidate is the baseline's `p_close` with `max(p_close, P_pluv)` applied. Each is scored by `score_v2.score_run` on the same features and matches, so the site lists are identical.
- **Pre-registration:** constants, grids, the fold selection rule and k = 2 variants (v2, v2-hourly) were committed in `9574cc39` before any held-out score was computed.

## 2. The rule as implemented (`proto/pluvial_v2.py`)

| piece | v1 | v2 |
|---|---|---|
| intensity | MRMS Pass2 peak clock hour | peak *Tc*-minute intensity: MRMS PrecipRate (2 min), volume-matched hour by hour to Pass2, maxima over 5/10/15/20/30/45/60/90/120 min, log-log interpolated at Tc |
| Tc | – | Kirpich on the longest D8 flow path L and its mean slope (head − segment)/L: 0.0195 L^0.77 S^−0.385 min × (1 − 0.6 TIA_up), clipped to 5–120 min |
| runoff C | 0.6 | 0.90 · DCIA_up + 0.20 · (1 − DCIA_up). DCIA is Sutherland's 0.1 · TIA%^1.5 per 20 m cell from NLCD 2021 impervious, as in `LF_LOSS=cn_dcia` |
| area | published D8 area (model DEM) | D8 area on the priority-filled 20 m lidar DEM (falls back to the published area) |
| capacity | 0.5 m³/s fixed | n_in · Q_inlet · (1 − c_clog). n_in = max(1, upstream road length / 100 m). Q_inlet is a HEC-22 sag grate (0.6 × 0.6 m, curb side) at d = 0.10 m: weir 1.66 · 1.8 · 0.1^1.5 = 0.0945 m³/s. On grade (segment slope > 1 %) it is × 0.5 |
| gate | HAND ≤ 0.5 m, ≥ 15 segments within 300 m | same HAND gate; density D chosen per fold |
| fitted (LOSO) | Q_cap, D (0.5, 15 in every fold) | c_clog ∈ {0.3, 0.5, 0.7}, D ∈ {0, 10, 15, 20} |

**Fold selection rule (fixed in advance):** on the 8 other storms, choose the setting with the most pooled site hits at 3 % flagged, subject to a mean rule share no more than 1 point above the default; ties go to the lower share. If no grid point meets the share limit, the fold falls back to the most conservative setting (0.7, 20).

**Inputs.** Both inputs are committed, so the rule can be evaluated offline.

- **Sub-hourly intensity:** `pluvial_v2/intensity_<storm>.csv`, one row per segment. It is built offline from the MRMS crops that `rain_test.yml mode=fetch` commits (`proto/rain/rain_fetch.py`). This task fetched sep2021 and aug2026; the other 7 storms were already there.
  - The clock-hour Pass2 maximum at the segments matches the run's `peak1h_mm` (median ratio 0.992–0.999).
  - The median i15/i60 is 1.34–2.64 where i60 ≥ 5 mm/h (jul2023 2.64, aug2026 2.12, aug2023 1.90, jul2021 1.34), consistent with RAIN.md.
- **Catchment attributes:** `pluvial_v2/geo_<storm>.csv`, from the Actions job `.github/workflows/pluvial_v2.yml mode=geo`. It uses the 10 m DEM and NLCD tiles from HF. The run directories are not published, and NLCD is not in the run outputs, so this job derives the attributes itself.
  - **Approximation:** the DEM is the 20 m lidar mean, depression-filled. It has no channel burn, crossing notches or breaching.
  - Against the published `area_km2`, the log-area correlation is only 0.52–0.62, and the median ratio is 1.4–1.6. Filling routes water across the pits that the model DEM keeps.
  - L for each segment is the longest upstream D8 path. Upstream road length comes from the densified road points.

## 3. Results (held-out = LOSO fold predictions; 3 % = top 3 % of segments by p_close, then depth)

**Selected parameters.** v2 chose (0.7, 20) in all 9 folds. This is the fallback: no grid point kept the training rule share within 1 point of the default. v2-hourly chose (0.3, 20) in all 9 folds.

| OOS-7 (29 sites) | base (parity) | v1 (0.5 m³/s, D 15) | **v2** | v2-hourly (ablation) |
|---|---|---|---|---|
| site recall @ 3 % | 0.172 (5) [0.00, 0.34] | 0.276 (8) [0.13, 0.42] | **0.207 (6)** [0.07, 0.37] | 0.310 (9) [0.17, 0.47] |
| lift @ 3 % (chance 0.063) | 2.7 | 4.4 | 3.3 | 4.9 |
| FSS 300 m @ 3 % | 0.017 | 0.028 | 0.055 | 0.037 |
| rule (p ≥ 0.5): mean share / site hits / lift | 0.91 % / 3 / 4.67 | 1.53 % / 6 / 6.31 | **7.24 % / 7 / 1.70** | 1.51 % / 5 / 5.40 |
| PR-AUC segment / site | 0.006 / 0.005 | 0.014 / 0.015 | 0.008 / 0.008 | 0.010 / 0.015 |

**Hits at 3 % by storm (sites).** The candidate's change against base is in brackets.

| storm | sites | base | v1 | v2 | v2-hourly | v2 rule share |
|---|---|---|---|---|---|---|
| aug2023 | 5 | 1 | 1 | 0 (−1) | 1 | 7.91 % |
| aug2023b | 2 | 0 | 1 | 1 (+1) | 1 | 8.77 % |
| aug2026 | 4 | 1 | 1 | 0 (−1) | 1 | 10.26 % |
| jul2021 | 4 | 0 | 1 | 1 (+1) | 1 | 3.09 % |
| jul2023 | 5 | 0 | 1 | 1 (+1) | 1 | 7.85 % |
| sep2021 | 6 | 3 | 2 | 2 (−1) | 3 | 7.59 % |
| sep2022 | 3 | 0 | 1 | 1 (+1) | 1 | 5.18 % |
| aug2021 (dev) | 11 | 3 | 3 | 3 | 3 | 10.23 % |
| sep2023 (dev) | 79 | 30 | 30 | **20 (−10)** | 29 | 10.52 % |

**Adoption rule (`score_v2.compare`; α = 0.05 / k with k = 2, so α = 0.025):**

| comparison | Δ recall @ 3 % | 2.5 % lower bound | ΔFSS300 | worst storm | rule lift (base → cand) | verdict |
|---|---|---|---|---|---|---|
| v2 vs base | +0.034 | −0.188 | +0.037 | −1 | 4.67 → 1.70 | **reject**: gain, CI and lift fail |
| v2 vs v1 | −0.069 | −0.267 | +0.027 | −1 | 6.31 → 1.70 | reject |
| v2-hourly vs base | +0.138 | 0.000 | +0.020 | 0 | 4.67 → 5.40 | reject: only the CI fails (at α = 0.05, for information only: lower bound +0.03) |
| v1 vs base (reference) | +0.103 | −0.067 | +0.010 | −1 | 4.67 → 6.31 | reject: CI fails |

**Dev storms.** v2 loses 10 of 79 sites at 3 % on sep2023. That is more than 2, so the protocol requires an explanation. v2 sets p = 1 on 10.5 % of Leominster segments, and these ties crowd the depth-ranked model hits out of the top 3 %. v2-hourly loses 1.

**Null model.** The same number of extra rule-flagged segments as v2 adds, drawn at random from the gate pool (HAND ≤ 0.5, density ≥ 20), gives a net −0.2 sites at 3 % over OOS-7. v2 gives +1. The extra segments are informative, but only marginally.

## 4. Why v2 over-flags

- **Tc sits at its 5-minute floor on most segments** (median 5.0–5.7 min in every storm). There, i(Tc) is the 5-min radar peak, 1.7–3.1 × the hourly rate on low-lying segments (median ratio; jul2023 3.05, aug2023 2.88).
- **Inlet capacity scales with upstream road length, and so does Q.** On a dense grid the ratio Q/Q_cap reduces to an intensity threshold of roughly i ≈ 3.6 · ρ_road · 0.0945 · (1 − c) / (100 · C). With a road density ρ of 15–20 km/km² (written in m/km² in the formula), C 0.35–0.5 and c_clog 0.7, that is about 30–60 mm/h. Every convective storm exceeds it at 5 min across whole neighbourhoods.
- **The cost is too high on the good storms.** No clogging value in the grid kept the training share within 1 point of the default. So v2 buys the flash-storm sites (Shrewsbury St, Webster Rt 12, Rt 146 Millbury, Southbridge St in Ida) with 3–10 % of segments at p ≈ 1. That collapses the rule lift and the 3 % ranking on aug2023, aug2026, sep2021 and sep2023.
- **The physics pieces are not what fails.** The hourly ablation shares Tc, C, HEC-22 capacity and the clogging logic, and with ~1–2 % of segments flagged it catches the same flash sites as v1 and keeps sep2021's 3.

**Why the remaining sites stay missed** (`loso.json` `diag.site_terms`):
- Franklin St (Worcester, jul2023) and Henry St (Framingham, aug2023) have HAND 5.0 and 1.2 m.
- Holden Main St and Hopkinton W Main St have only 4–9 road segments within 300 m.
- These are gate failures, not intensity failures.

## 5. What this means for T3

- **Sub-hourly radar intensity used as i(Tc) at Tc ≈ 5 min hurts.** It is the wrong scale for a 20 m segment-level rule fed by 1 km radar, which smooths nothing at 5 min. If a sub-hourly term is retried, it needs one of:
  - a Tc floor of 10–15 min, the usual design minimum for urban inlets;
  - or capacity sized to a design storm (for example 10-yr i(Tc) from NOAA Atlas 14) rather than to a clogged-inlet count.

  Either would be a new variant, counted in k, and logged here before it is scored.
- **The hourly physics version (v2-hourly, 9/29) is the strongest pluvial candidate so far, but 29 sites cannot separate it from chance at the pre-registered level.** The locked test set (5 pre-2020 storms) is the only remaining way to settle it, and it opens only once T3–T6 are frozen.
- `PROTO_PLUVIAL=1` stays as an opt-in layer, and the default model is unchanged.
