# Hydrology / hydraulics review — 18 Oct 2026 (internal reviewer)

Context that frames the whole list: the 105 "July 2023 riverine marks" are **five slope-area survey reaches, not 105 independent points**: South River at the Conway gauge (46 marks within ~100 m), Avery Brook (34), West Brook at the Whately gauge (14), North Branch Deerfield VT (5), Whetstone Brook VT (6). 89 of 105 have `height_above_ground_ft = 0.0` (edge-of-water points). So (a) the 4% is "~4 marks at one reach", (b) `obs_m = 0` makes bias/MAE/within-50cm meaningless for this event, and (c) a dry channel cell at three USGS gauge reaches during a record flood means the model is not delivering runoff to the channel at all → loss terms first, hydraulics second. Dec 2023 (100 m run) lost ~79% of rain to infiltration (runoff coefficient ~0.2) for a storm that put most MA rivers at major flood stage. **The model is volume-starved first, conveyance-wrong second.**

## 1. Infiltration never saturates: add storage-limited (saturation-excess) runoff — HIGHEST IMPACT
Horton `f = fc + (f0-fc)·exp(-F/40)` with Akan ultimate rates that never fall further; New England hilltown soils are 0.5–1 m of till over dense basal till/bedrock (Ksat 0.1–1 mm/h) → runoff is saturation-excess (Dunne). With B/C soils the model absorbs 7–15 mm/h indefinitely. **`WET_START` is dead above ~120 mm (exp(-120/40)=0.0025)** — the "250 mm" variant is identical to 120 mm; its extra flooding comes only from FC_SCALE.
Fix (4 h): storage cap `S_cell = θ_def·min(wtd, resdept)`; after `Finf ≥ S_cell` use `f = K_deep` (0.5–1 mm/h C/D, 2–5 B). SSURGO `aws0100wta`, `brockdepmin`. Antecedent from 14-day MRMS − 3 mm/d ET. Or SCS-CN AMC-III per cell (CN from group × NLCD). Expected: 2–4× event runoff for wet-antecedent storms.

## 2. BUG: 2 mm/h "storm drain" applied to every cell; infiltration applied to rivers
`drain_mmph = 2 + 5·IMP` → every forest cell loses 2 mm/h (48 mm/day) on top of fc. `loss = min(h, fcap)` is taken from channel/lake cells too (Connecticut River loses ~100–200 m³/s). Fix (1–2 h): `drain = where(IMP > 0.05, 7·IMP, 0)`; `fcap[water] = 0` using NHDPlus waterbodies + flowline cells.

## 3. Validate high-water marks by water-surface elevation per reach, not depth-above-ground per point
Use `elev_ft` (NAVD88) vs `max within 60–100 m of (Z + hmax)`; report ΔWSE, share within ±0.5 m, dry-within-R separately; `floor` not `int` for cells; aggregate by waterbody (5 reaches); add a **discharge check** at in-box gauges (01169900 South River nr Conway, 01171100 West Brook nr Whately — already in gauges_jul2023.json) by summing face fluxes across a transect. Coastal: score `stillwater == 1` marks separately (wrack lines include wave run-up). 3–4 h.

## 4. Sub-grid channels for streams narrower than 30 m
Block-averaging the 10 m DEM turns a 10 m × 2 m channel into a 0.7 m dip. Stage A (4 h): along NHDPlus HR flowline cells, bankfull `W = 2.70·A^0.352`, `D = 0.30·A^0.213` (Bieger 2015; MA-specific Bent & Waite 2013), burn volume-equivalent depth `D·W/dx` and set channel n = 0.035. Stage B (12–16 h): Neal, Schumann & Bates (2012) sub-grid channel in the solver.

## 5. Baseflow / initial channel storage and gauge-inflow injection
Channels start dry although hydro-flattened mainstems sit at the lidar water surface → inject `Q_excess = max(Q − Q_lidar, 0)` over 60–100 flowline cells in the first 2–3 km inside the box; 6–12 h spin-up at Q(t0). Deerfield: use 01168500 Charlemont scaled by area at the VT line, not 60% at the mouth. Connecticut: add 01156000 West River + 01161000 Ashuelot; Merrimack: add 01094000 Souhegan + 01096500 Nashua. Removes the 18 m cell artefact and gives 2–4× larger dt. 3–4 h.

## 6. Manning n by land cover instead of 0.06 everywhere
NLCD 2021: 0.035 channel/water, 0.04 developed open, 0.08–0.12 developed, 0.035 crops, 0.15 forest (h > 0.3 m), depth-dependent blend toward sheet-flow values (Kalyanapu 2009) for h < 0.1 m. Do after 1, 2, 4. 3 h.

## 7. Numerics: Froude cap masks oscillation; use the q-centred (θ=0.7) scheme of de Almeida & Bates (2013) and relax the cap to Fr ≤ 2. 3 h.

## 8. Sinks, sea cells, inland nodata
`sea = isnan(Z) | (Z ≤ 0.3)` → inland voids become holes; estuaries held at 0 m while Dec 2023 / Jan 2018 tides were +1.5–2.5 m (no compound flooding); reservoirs have zero attenuation. Fix: edge-connected labelling (as in w8), fill inland NaN with surrounding minimum, sea cells `fixed` at the nearest CO-OPS level, simple level-pool for ~15 large reservoirs. 2–3 h (+2 h).

## 9. Run the mark reaches at 10–15 m (40×40 km box around Conway/Whately) after items 1–2. 1 h + GPU.

## 10. Verify soils loaded for the July box (it did: 95%); make the uniform fallback fatal unless SOILS=0. 0.5 h.

## 11. Rain sanity for the hilltowns: compare MRMS 48 h totals with COOP/CoCoRaHS (Ashfield, Conway, Shelburne Falls). 1 h.

## 12. validate.py details: true distance mask for radius; random baseline is "any report location, any day" (a hard baseline — say so); compute WSE in float32; be sure which resolution each score comes from.

**Suggested order:** 10 → 2 → 1 → 3 (re-score July) → 5 → 4A → 9 → 6 → 7 → 8 → 4B → 11.
