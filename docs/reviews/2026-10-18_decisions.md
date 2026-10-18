# Decision sheet — 18 Oct 2026

Three internal reviews (hydrology, ML/cascade, geotechnical/groundwater) are in `docs/reviews/`. Below: what I recommend doing, in order, with the reason. Mo decides; items are marked ✅ once approved.

## A. Fix the engine's water balance first (this week, ~2 days) — recommended YES
The July 2023 miss is explained: the model loses ~80 % of the rain. Three concrete defects:
1. **Storm-drain loss of 2 mm/h applied to every cell in the state** (forest, fields) and **infiltration taken from river and lake cells** — a bug. Fix: drains only on paved cells, no infiltration on water.
2. **Infiltration never saturates** — Horton's curve keeps drinking at 7–15 mm/h forever on B/C soils; `WET_START` has no effect above 120 mm (the "250 mm" experiment running now only differs by FC_SCALE). Fix: storage-limited infiltration (soil water capacity from SSURGO `aws0100`, depth to bedrock), antecedent wetness from the previous 14 days of MRMS rain instead of a hand-set number.
3. **Validation metric wrong for river marks**: 89 of 105 July marks are edge-of-water points (height above ground = 0) in 5 survey reaches. Fix: compare water-surface elevation (mark elevation vs model Z + depth), score per reach, and check modelled discharge against the two USGS gauges inside the reaches.
Then re-run July 2023 and Dec/Sept 2023 → honest numbers.

## B. Rivers (next, ~3 days) — recommended YES
4. Sub-grid channels along NHDPlus flowlines (bankfull width/depth from drainage area; MA regressions).
5. Baseflow: start rivers at their pre-storm flow; inject only the excess at the state line, spread along the first km; add the missing NH tributaries (West, Ashuelot, Souhegan, Nashua).
6. Manning n by land cover (NLCD) instead of 0.06 everywhere; q-centred numerics; sea cells held at the tide-gauge level in rain runs (compound flooding); inland DEM voids no longer swallow streams; simple level-pool for the big reservoirs.

## C. Outputs the ML needs (1 day, do alongside A) — recommended YES
7. Save velocity, arrival time, duration, h·v per cell and per road segment (mean and p90 along the segment, not just max); run manifest per run.

## D. Replace the cascade heuristic (1 week) — recommended YES, after A–C
8. Passability from depth × velocity (Pregnolato speed–depth curve), accessibility to hospitals/fire/EMS by travel time, detour by actual rerouting with volume/capacity and vehicle-hours, imputed AADT flagged. Validate on MassDOT count stations.

## E. Culverts and crossings (1.5 weeks) — recommended YES; needs Mo to create a free NAACC account
9. NAACC + MassDOT + NBI inventory → per-crossing capacity vs modelled flow → overtopping probability from the ensemble. First infrastructure failure mode with real ground truth (repeating flood points).

## F. Compute (recommended YES; needs Mo)
10. Second Colab GPU session + Kaggle account with the HF_TOKEN secret → 2–3× more experiments per day. All jobs already read/write Hugging Face so nothing changes in the code.
11. Build the training corpus: 20 highest-report storm days 2015–2026 on district-size boxes + a parameter ensemble; queue file on HF, launchers on Colab/Kaggle.

## G. Later (weeks 3–6) — recommended, in this order
12. Groundwater layer (150–300 m Boussinesq, continuous since 2015, validated on USGS wells) → replaces the antecedent number for good and is the "flooding → groundwater" link.
13. Segment-level spatio-temporal GNN surrogate (seconds instead of hours; physics features for the ranker).
14. Shallow-landslide factor of safety (Berkshires; validated on the MGS inventory).
15. Boston groundwater / timber-pile exposure (BGwT wells).
16. Evaluation protocol written down (LOSO + spatial-block CV, baselines, reliability diagrams) before any paper.
17. Failure-probability hierarchy L1 (validated) → L2 (computed) → L3 (assumed fragility), tagged honestly.

## Not recommended / drop
- 10 m statewide runs (GPU hours better spent on physics and the corpus); 10 m only for case-study boxes.
- Boston Blue Clay consolidation, retaining walls (no data), dam breach as a result (demo only).
