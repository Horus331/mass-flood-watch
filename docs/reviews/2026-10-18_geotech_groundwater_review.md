# Groundwater / geotechnical review — 18 Oct 2026 (internal reviewer)

Two framing points: (1) a statewide "70 % probability this culvert fails in 24 h" cannot be validated as a calibrated probability (no public failure database); what can be validated are the intermediate hazard states (water table, overtopping/closure, landslide occurrence). Produce failure probability as **validated hazard × literature fragility** and say so. (2) Strength parameters are not in SSURGO; c′, φ′ come from USCS-class ranges and every factor of safety carries ±30 % from that alone.

| # | Item | Output | Validatable against | Value | Days |
|---|------|--------|---------------------|-------|------|
| 1 | Continuous water-table / soil-water state (2-D Dupuit–Boussinesq layer at 150–300 m, recharge = Horton loss − root-zone bucket with GridMET PET; saturation-excess coupling back to the surface; continuous spin-up 2015→ on daily MRMS) | WTD grid, antecedent-wetness map replacing wet_start_mm | USGS NWIS wells (~100–150 MA, a dozen continuous); improvement of existing HWM scores without retuning | High | 12–15 |
| 2 | Culvert / small-crossing capacity and overtopping (NAACC + DER crossings + NBI; HDS-5 inlet control; pond storage from 1 m LiDAR; Monte Carlo over blockage Beta(2,5), n, rain ±25 %) | P(overtop), head over road, hours | MassDOT repeating flood points, 4,551 road reports, Leominster 2023, Irene 2011 (Stage IV rain) | Very high | 10–12 |
| 3 | Embankment washout / outlet scour (shear-stress erosion index with τc by USCS/vegetation; HEC-14 scour) | P(washout) | a few dozen documented washouts (ranking only) | Med-high | 5–7 |
| 4 | Shallow landslides / road cut-fill slopes: infinite-slope FS with pore pressure (SINMAP-style steady + Iverson transient), LiDAR 10 m slopes, soil depth bounded by SSURGO brockdepmin | P(FS<1) per cell and segment, static susceptibility | MGS landslide inventory (mostly Irene 2011) AUC 0.75–0.85 | High | 8–10 |
| 5 | Boston urban groundwater: local Boussinesq fill-aquifer model with sewer-leakage sink, recharge from ponded flood depth, tidal boundary; timber-pile exposure index vs cut-off elevation; P(basement inundation) | WT elevation, exposure-days, basement risk | Boston Groundwater Trust ~800 wells (WT only; pile condition not validatable) | Med-high | 8–10 |
| 6 | Flooded pavement / saturated subgrade (hours inundated × AADT × AASHTO subgrade class; MEPDG moisture-modulus; FR-615, Chen 2024 thresholds) | damage index, P(damage) | MassDOT PCI before/after differencing (weak) | Medium | 4–5 |
| 7 | Levee freeboard (National Levee Database) and bridge scour screen (NBI items 71/113, HEC-18 relative index) | P(overtop), scour exposure | river stage at gauges only | Low-med | 4–5 |
| 8 | Dam overtopping screen (NID, LiDAR storage, Froehlich breach cascade demo) | P(overtop) | none in MRMS era | Low | 4 |
| 9 | Retaining walls | FS sensitivity | none (no public inventory; request MassDOT's) | Low | 3 |
| 10 | Ensemble + fragility framework: 8–16 members (rain ±25 %, antecedent ±1σ, FC_SCALE 0.7–1.3) → hazard distributions → P(hazard > resistance) with validated/assumed tags; reliability diagrams for the validatable intermediates | labelled P(failure) per asset | ensemble reliability on HWMs | Very high | 6–8 |

Recommended sequence: 1 → 2 → 10 (minimal) → 4 → 3 → 5 → 6; 7–9 filler. Total 65–80 days.

Say no to / say plainly: no Boston Blue Clay consolidation modelling; FS as distributions, never site values; groundwater layer not at 30 m statewide; pre-2015 storms need NCEP Stage IV rain; culvert dimensions will be imputed for most state highways — report coverage and send the MassDOT culvert-inventory request early.
