# Evaluation protocol (pre-registered 18 Oct 2026)

Written before any calibration or surrogate training so metric choices cannot be post-hoc.

## Observations used
1. **USGS STN high-water marks** (`stn_ma.json`, 1,866 in MA). Primary metric: water-surface elevation (WSE) error = model (ground + peak depth at the deepest cell within 60 m) − surveyed elevation (NAVD88). *Amendment 19 Oct 2026, before any calibration:* the first version took the highest water surface among all wet cells within 60 m; in steep valleys (July 2023 reaches) a hillside cell with a few cm of sheet flow sat 5–7 m above the river and won, so the metric is now read at the deepest cell. Coastal scores were re-run under the amended rule. Secondary: depth above ground at the mark cell (marks with height above ground > 0 only); "water within 30 m". Scores reported per survey reach (marks cluster) and, for the coast, still-water marks separately from wave/debris lines.
2. **MassDOT dated road-flood reports** (`flood_reports.json`, 4,551). Hit rate = share of reports on the storm's days with modelled peak depth ≥ 10 cm within 100 m; always shown next to the rate at the same test applied to all report locations on any day (a hard baseline: these are flood-prone roads). Also: ≥ 30 cm threshold.
3. **USGS gauge peak stage and timing** (`data/gauges/`), for every storm including Dec 2023 and Sept 2023 which have no surveyed marks: peak-stage error above the DEM at the gauge cell, first-rise and peak timing error (to be added).

## Thresholds (fixed)
Wet 10 cm. Impassable road 30 cm, or depth × speed ≥ 0.5 m²/s. "Within" tolerance 50 cm for WSE.

## Baselines every result is compared with
HAND static inundation at the storm's return-period depth (NOAA Atlas 14); FEMA Special Flood Hazard Area membership; the existing GBM/GNN road-segment ranker (AUC 0.93–0.94 on reports); "lowest roads first".

## Splits for anything learned (surrogate, calibration)
Leave-one-storm-out across storms (all parameter variants of a storm held out together) and spatial block cross-validation by HUC10 watershed. Report both.

## Uncertainty
Physics ensemble (rain ×0.8/1.0/1.2, antecedent ±1σ, infiltration scale 0.7–1.3, Manning ±30 %), rain-forecast ensemble (HRRR members) in forecast mode, deep ensemble (5 seeds) for surrogates. Spread–skill and PIT histograms; reliability diagrams and Brier skill vs climatology for every published probability (only where ≥ 50 positives per bin).

## Claims hierarchy
L1 road impassable — validated and calibrated against reports. L2 hydraulic exceedance (culvert HW/D > 1, overtopping, freeboard < 0) — computed from physics + inventory, uncertainty from the ensemble, indirectly validated (repeating flood points, NBI waterway adequacy). L3 structural failure — literature fragility conditioned on L2 and inventory condition, labelled "assumed", never presented as calibrated.

## Versioning
Every run's `meta.json` records physics version, parameters and inputs; scores are published next to the run as `validation.json`; the scoreboard on the methods page reads them live. Runs are never overwritten: new physics = new tag (`_v3` …).
