# Datasets used by the road-closure prototype

This file lists every dataset the Mass Flood Watch code uses. Each entry was checked against the scripts and workflows on 22 Oct 2026. The same table is in [datasets.csv](datasets.csv), and the pipeline diagram is in [pipeline.html](pipeline.html).

**What the role values mean.**

- *input*: drives the flood model.
- *network*: the road, structure and facility layer that the closure and access rules run on.
- *validation*: the model is scored against it and never fitted to it.
- *label*: ground truth for the closure rules or for the ML model.
- *baseline*: another model we compare against.
- *calibration*: a model value is tuned to match it. No dataset has this role yet. The prototype uses only published values: the NRCS curve number at AMC II, and closure thresholds taken from the literature.

**What the status values mean.** *used: prototype* means the dataset is part of the Sept 2023 Leominster LISFLOOD-FP prototype. That path runs `sim/colab/w9_lisflood.py`, then `proto/prototype.py`, `proto/score.py` and `proto/validate_points.py`. For other datasets, the status says where they are used instead, or *not used yet*.

## Summary

| id | dataset | provider | role | status |
|---|---|---|---|---|
| D01 | USGS 3DEP DEM, 1/3 arc-second (~10 m) | USGS National Map (3DEPElevation ImageServer) | input | used: prototype |
| D02 | NOAA MRMS MultiSensor QPE 01H Pass2 | NOAA NSSL/NCEP, AWS Open Data bucket noaa-mrms-pds | input | used: prototype |
| D03 | NOAA MRMS MultiSensor QPE 24H Pass2 | NOAA, AWS noaa-mrms-pds | input | used: statewide engine only (not in prototype) |
| D04 | NOAA HRRR forecast (surface, wrfsfc) | NOAA NCEP, AWS noaa-hrrr-bdp-pds | input (forecast mode) | used: live graph model; not in prototype |
| D05 | NASA GPM IMERG V07 half-hourly (Final > Late > Early) | NASA GES DISC (found via CMR) | validation (rain check) | used: rain cross-check only |
| D06 | NLCD 2021 percent impervious | USGS/MRLC (WCS NLCD_2021_Impervious_L48) | input | used: prototype |
| D07 | USDA SSURGO (via Soil Data Access) | USDA NRCS | input | used: prototype |
| D08 | NHDPlus High Resolution flowlines + rasters; derived channels30 grid | USGS (NHDPlus_HR MapServer, prd-tnm S3); channels30 built here | input | used: prototype |
| D09 | Watershed Boundary Dataset HU10 | USGS National Map (wbd MapServer layer 5) | validation design | used: ML pilot only; not in prototype |
| D10 | USGS instantaneous values (IV), discharge 00060 + gage height 00065, with site datum | USGS Water Data OGC API (continuous, monitoring-locations); legacy WaterServices as fallback | validation; input (boundary inflow, statewide) | used: prototype (validation) |
| D11 | USGS Short-Term Network (STN) high-water marks | USGS STN services (api.waterdata.usgs.gov/stnservices) | validation | used: statewide runs; not in Sep 2023 prototype |
| D12 | NOAA CO-OPS tide gauges (water level) | NOAA CO-OPS API (tidesandcurrents) | input (coastal boundary) | used: statewide/coastal; not in prototype (inland box) |
| D13 | NOAA National Water Model (operational analysis_assim, analysis_assim_no_da) + OWP HAND | NOAA OWP (Google Cloud / Azure buckets); HAND from CIROH mirror / NFIE | baseline | used: baseline comparison; not in prototype |
| D14 | MassDOT road network graph (graph_segments.json) | MassDOT road inventory (per docs/methods.html) | network | used: prototype. Build script not in repo; 25 % of AADT are 1,000 defaults |
| D15 | FHWA National Bridge Inventory 2024 (MA) | FHWA | network / closure rule | used: prototype |
| D16 | Road-stream crossings: USGS national stream crossings + MA Stream Crossings Project + MassDOT bridges | USGS; USGS/UMass/MassDEP; MassDOT (ArcGIS services) | input; network / closure rule | used: prototype |
| D17 | NAACC culvert surveys (MA): NAACC 2015+, UMass Stream Continuity 2005-2017, Culvert Condition 2018 | North Atlantic Aquatic Connectivity Collaborative (naacc.org Data Center exports) | input; closure rule | used: prototype (sized notch and blockage are opt-in) |
| D18 | OpenStreetMap emergency facilities | OpenStreetMap contributors (Overpass API) | network | used: prototype |
| D19 | MassDOT District 3 repeating flood areas | MassDOT District 3 list | validation | used: prototype (check only) |
| D20 | NWS Local Storm Reports (LSR) | NWS, via Iowa Environmental Mesonet archive | validation | used: prototype |
| D21 | NOAA Storm Events Database | NOAA NCEI | validation; label | used: prototype |
| D22 | Historical road-flood reports (docs/prone/flood_reports.json) | compiled: NWS storm reports, crash records, MassDOT District 3 reports | validation; label | used: prototype (check). Build script not in repo |
| D23 | Documented labels, Sep 2023 Leominster (labels_sep2023_leominster.csv) | compiled here from WX1BOX SKYWARN log, MA CDBG-DR plan, MassDOT reports, news | label; validation | used: prototype |
| D24 | MassDOT roadway events feed (logger) | MassDOT (events.massdot.evbg.net) | label (future) | not used yet (logging only) |
| D25 | Vermont July 2023 road closures (VTrans TMC, digitized) | S. Grant 2025, FEMC / UVM ("RoadClosures2023") | validation (independent storm) | not used yet (file in repo; no code reads it) |
| D26 | PRISM daily rain via ACIS | PRISM Climate Group / NOAA RCC ACIS GridData | input (forecast mode) | used: live graph model; not in prototype |
| D27 | USGS annual peaks + ratings (legacy NWIS archive) | USGS NWIS (legacy /peak, get_ratings) | validation (planned) | not used yet (archived) |

## Details

### D01. USGS 3DEP DEM, 1/3 arc-second (~10 m)

- **Provider:** USGS National Map (3DEPElevation ImageServer)
- **Resolution / coverage:** 10 m tiles (176 x 20 km) over MA; averaged to run res (10-20 m prototype, 30 m statewide)
- **Period used:** static (lidar-era survey)
- **Role:** input
- **How it is used:** Ground elevation for LISFLOOD-FP; raw (unedited) copy z_raw = road crest for the freeboard / overtop rule
- **Where in the code:** `sim/colab/w1_data.py (exportImage) -> HF data/dem10`; `sim/colab/w9_lisflood.py`; `proto/prototype.py (z_raw.npz)`
- **Licence:** Public domain (USGS)
- **Access:** public
- **Status:** used: prototype

### D02. NOAA MRMS MultiSensor QPE 01H Pass2

- **Provider:** NOAA NSSL/NCEP, AWS Open Data bucket noaa-mrms-pds
- **Resolution / coverage:** ~1 km, hourly, CONUS
- **Period used:** storm windows (Sep 2023 Leominster: 2023-09-11 16Z + 36 h); statewide runs Jan 2018 - Jan 2024
- **Role:** input
- **How it is used:** Hourly rain on every cell (TUFLOW-format NetCDF dynamic rain for LISFLOOD-FP); peak-1h and flashness per segment
- **Where in the code:** `sim/colab/w9_lisflood.py`; `sim/colab/w4_flood_gpu.py`; `proto/prototype.py`
- **Licence:** NOAA open data (no restrictions)
- **Access:** public
- **Status:** used: prototype

### D03. NOAA MRMS MultiSensor QPE 24H Pass2

- **Provider:** NOAA, AWS noaa-mrms-pds
- **Resolution / coverage:** ~1 km, daily (00Z), CONUS
- **Period used:** 14 days before each storm
- **Role:** input
- **How it is used:** Antecedent soil wetness (14-day rain minus 3 mm/day ET) in the statewide engine. The LISFLOOD-FP prototype uses fixed NRCS AMC II instead
- **Where in the code:** `sim/colab/w4_flood_gpu.py`
- **Licence:** NOAA open data
- **Access:** public
- **Status:** used: statewide engine only (not in prototype)

### D04. NOAA HRRR forecast (surface, wrfsfc)

- **Provider:** NOAA NCEP, AWS noaa-hrrr-bdp-pds
- **Resolution / coverage:** 3 km, hourly, 0-48 h leads, CONUS
- **Period used:** live (every 6 h) and replayed past storms
- **Role:** input (forecast mode)
- **How it is used:** Forecast rain for the live road-graph model (4 time-lagged runs, 90th percentile); 2 m temperature for frozen-ground / snow spin-up
- **Where in the code:** `refresh/graph_refresh.py`; `refresh/hrrr_replay.py (replay.yml, refresh.yml)`; `sim/colab/snow_inputs.py`
- **Licence:** NOAA open data
- **Access:** public
- **Status:** used: live graph model; not in prototype

### D05. NASA GPM IMERG V07 half-hourly (Final > Late > Early)

- **Provider:** NASA GES DISC (found via CMR)
- **Resolution / coverage:** 0.1 deg, 30 min, global
- **Period used:** 2023-09-11 12Z to 2023-09-13 12Z (Leominster box)
- **Role:** validation (rain check)
- **How it is used:** Independent satellite check on radar rain totals for the prototype storm; not a model input
- **Where in the code:** `proto/imerg_fetch.py (imerg.yml) -> docs/proto/obs/imerg_sep2023.json/.npz`
- **Licence:** NASA open data
- **Access:** needs account (Earthdata login; token held as repo secret)
- **Status:** used: rain cross-check only

### D06. NLCD 2021 percent impervious

- **Provider:** USGS/MRLC (WCS NLCD_2021_Impervious_L48)
- **Resolution / coverage:** 30 m native, resampled onto 10 m tiles; MA
- **Period used:** 2021 (fixed for all storms)
- **Role:** input
- **How it is used:** Manning n (paved > 30 % -> 0.10, else 0.08), impervious part of the NRCS curve number; storm-drain capacity in the statewide engine
- **Where in the code:** `nlcd.yml -> HF data/nlcd10`; `sim/colab/w9_lisflood.py`; `sim/colab/w4_flood_gpu.py`; `sim/ml/dataset.py`
- **Licence:** Public domain (USGS)
- **Access:** public
- **Status:** used: prototype

### D07. USDA SSURGO (via Soil Data Access)

- **Provider:** USDA NRCS
- **Resolution / coverage:** 375,545 map-unit polygons -> 30 m state grid (hydgrp, ksat, wtd, drcl)
- **Period used:** current survey
- **Role:** input
- **How it is used:** Hydrologic soil group A-D (shallow water table counted as D) for the NRCS curve number; Horton rates in the statewide engine
- **Where in the code:** `sim/soils_sda.py (soils.yml) -> HF data/soils30`; `sim/colab/w9_lisflood.py (LF_LOSS=cn)`; `sim/colab/w4_flood_gpu.py`
- **Licence:** Public (USDA NRCS, free use)
- **Access:** public
- **Status:** used: prototype

### D08. NHDPlus High Resolution flowlines + rasters; derived channels30 grid

- **Provider:** USGS (NHDPlus_HR MapServer, prd-tnm S3); channels30 built here
- **Resolution / coverage:** 1:24k flowlines (213,719 lines); 10 m flow dir/accum; channels30 = 30 m state grid
- **Period used:** static
- **Role:** input
- **How it is used:** Channel mask, open-water mask (no losses), drainage area; bankfull width/depth (Bieger 2015: W = 2.70 A^0.352, D = 0.30 A^0.213) burnt into the DEM (volume-equivalent)
- **Where in the code:** `sim/colab/w1_data.py`; `sim/colab/w2_drain10.py`; `sim/channels_grid.py (channels.yml) -> HF data/channels30`; `sim/colab/w9_lisflood.py`; `sim/crossings_capacity.py`
- **Licence:** Public domain (USGS)
- **Access:** public
- **Status:** used: prototype

### D09. Watershed Boundary Dataset HU10

- **Provider:** USGS National Map (wbd MapServer layer 5)
- **Resolution / coverage:** HU10 polygons -> 30 m grid, MA
- **Period used:** static
- **Role:** validation design
- **How it is used:** Spatial-block cross-validation folds for the ML surrogate (no watershed in both train and test)
- **Where in the code:** `sim/huc10_grid.py (huc10.yml) -> HF data/huc10_30`; `sim/ml/dataset.py, sim/ml/baseline.py (ml_pilot.yml)`; `sim/fim_maps.py`
- **Licence:** Public domain (USGS)
- **Access:** public
- **Status:** used: ML pilot only; not in prototype

### D10. USGS instantaneous values (IV), discharge 00060 + gage height 00065, with site datum

- **Provider:** USGS Water Data OGC API (continuous, monitoring-locations); legacy WaterServices as fallback
- **Resolution / coverage:** 15 min; 10 gauges in the Leominster box, ~100-128 statewide
- **Period used:** storm windows (Sep 2023: 2023-09-10 to 09-14)
- **Role:** validation; input (boundary inflow, statewide)
- **How it is used:** Prototype: scored on stage rise, peak timing, peak WSE (NAVD88 datum) and peak flow vs LISFLOOD-FP face fluxes. Statewide engine: discharge injected where rivers enter MA
- **Where in the code:** `proto/obs_fetch.py -> docs/proto/obs/gauges_sep2023.json`; `proto/score.py`; `proto/diag_gauge.py`; `sim/colab/w9_lisflood.py (LF_QOUT)`; `sim/gauges_fetch.py (gauges.yml) -> HF data/gauges_v2`
- **Licence:** Public domain (USGS)
- **Access:** public
- **Status:** used: prototype (validation)

### D11. USGS Short-Term Network (STN) high-water marks

- **Provider:** USGS STN services (api.waterdata.usgs.gov/stnservices)
- **Resolution / coverage:** 1,866 surveyed marks in MA, 9 events
- **Period used:** Irene 2011, Sandy 2012, Jan + Mar 2018, Henri 2021, Jul 2023, 2010, 1978, 1991
- **Role:** validation
- **How it is used:** Peak water-surface elevation (NAVD88) at each mark vs model ground + peak depth. No STN event covers the Sep 2023 Leominster storm
- **Where in the code:** `hwm.yml, hwm_ma.yml -> docs/validation/stn_ma.json`; `sim/validate.py`; `sim/colab/w6_validate.py`
- **Licence:** Public domain (USGS)
- **Access:** public
- **Status:** used: statewide runs; not in Sep 2023 prototype

### D12. NOAA CO-OPS tide gauges (water level)

- **Provider:** NOAA CO-OPS API (tidesandcurrents)
- **Resolution / coverage:** 6-min, coastal stations (Boston, Nantucket, ...)
- **Period used:** live; storm windows for coastal runs
- **Role:** input (coastal boundary)
- **How it is used:** Sea cells held at observed water level (+0.5 / +1 m scenarios) in coastal runs; live page
- **Where in the code:** `refresh/live_refresh.py -> docs/live.json`; `sim/colab/w4_flood_gpu.py`; `sim/colab/w8_coast_gpu.py`
- **Licence:** NOAA open data
- **Access:** public
- **Status:** used: statewide/coastal; not in prototype (inland box)

### D13. NOAA National Water Model (operational analysis_assim, analysis_assim_no_da) + OWP HAND

- **Provider:** NOAA OWP (Google Cloud / Azure buckets); HAND from CIROH mirror / NFIE
- **Resolution / coverage:** NHDPlus v2 reaches, hourly; HAND 10 m
- **Period used:** storm windows
- **Role:** baseline
- **How it is used:** Benchmark: NWM flow vs USGS gauges (NSE, KGE, peak ratio); NWM + HAND inundation map as the "national model" baseline for road impacts
- **Where in the code:** `sim/nwm_compare.py (nwm.yml)`; `sim/fim_maps.py, sim/fim_publish.py (fim.yml)`; `sim/infra/impacts.py --combine`
- **Licence:** NOAA open data
- **Access:** public
- **Status:** used: baseline comparison; not in prototype

### D14. MassDOT road network graph (graph_segments.json)

- **Provider:** MassDOT road inventory (per docs/methods.html)
- **Resolution / coverage:** District 3: 52,698 segments (road, town, class, length, AADT) + 81,519 links
- **Period used:** snapshot Oct 2026
- **Role:** network
- **How it is used:** Segments on which depth/closure is computed; links for cut-off and detour routing; AADT for vehicle-hours at risk
- **Where in the code:** `docs/graph_segments.json`; `proto/prototype.py`; `sim/infra/impacts.py`; `proto/validate_points.py (random road points)`; `refresh/graph_refresh.py`
- **Licence:** MassDOT/MassGIS public data (no explicit licence found)
- **Access:** public
- **Status:** used: prototype. Build script not in repo; 25 % of AADT are 1,000 defaults

### D15. FHWA National Bridge Inventory 2024 (MA)

- **Provider:** FHWA
- **Resolution / coverage:** 5,296 structures (334 culverts) > 20 ft; MA
- **Period used:** 2024 submission
- **Role:** network / closure rule
- **How it is used:** Bridge vs culvert flag at crossings, waterway adequacy and scour-critical ratings; NBI ids on crossings
- **Where in the code:** `sim/nbi_fetch.py (nbi.yml) -> docs/network/nbi_ma.json`; `proto/prototype.py`; `sim/crossings_capacity.py`; `sim/infra/crossings_all.py`
- **Licence:** Public domain (US DOT)
- **Access:** public
- **Status:** used: prototype

### D16. Road-stream crossings: USGS national stream crossings + MA Stream Crossings Project + MassDOT bridges

- **Provider:** USGS; USGS/UMass/MassDEP; MassDOT (ArcGIS services)
- **Resolution / coverage:** 29,205 MA crossings (9,393 in District 3); peak flows pk10-pk500, bankfull, deck, inverts where surveyed
- **Period used:** snapshot 2026-10-20
- **Role:** input; network / closure rule
- **How it is used:** Notch opened through road fill at every crossing in the DEM (culverts are dams in lidar); HDS-5 culvert capacity vs modelled flow (culvert rule)
- **Where in the code:** `sim/infra/crossings_all.py (crossings_all.yml) -> docs/network/crossings_all.json`; `sim/crossings_fetch.py`; `sim/colab/w9_lisflood.py (open_crossings)`; `sim/infra/culvert.py`; `proto/prototype.py`
- **Licence:** Public (federal/state open data)
- **Access:** public
- **Status:** used: prototype

### D17. NAACC culvert surveys (MA): NAACC 2015+, UMass Stream Continuity 2005-2017, Culvert Condition 2018

- **Provider:** North Atlantic Aquatic Connectivity Collaborative (naacc.org Data Center exports)
- **Resolution / coverage:** 11,737 surveys; 7,299 matched within 40 m, 4,438 added
- **Period used:** 2005-2025 field visits
- **Role:** input; closure rule
- **How it is used:** Culvert shape, span, rise, barrels, inlet type, fill height, blockage for HDS-5 capacity and sized notches (LF_BREACH_SIZED)
- **Where in the code:** `proto/naacc_merge.py -> docs/network/crossings_all.json, naacc_ma.json`; `sim/colab/w9_lisflood.py`; `sim/infra/culvert.py`; `proto/prototype.py`
- **Licence:** Not stated on export (verify NAACC terms)
- **Access:** public download (Data Center; account requirement not verified)
- **Status:** used: prototype (sized notch and blockage are opt-in)

### D18. OpenStreetMap emergency facilities

- **Provider:** OpenStreetMap contributors (Overpass API)
- **Resolution / coverage:** hospitals, fire, police, ambulance in and around MA
- **Period used:** snapshot 2026-10-18
- **Role:** network
- **How it is used:** Hospital access: segments cut off from every hospital, added travel minutes
- **Where in the code:** `sim/facilities_osm.py (facilities.yml) -> docs/network/facilities.json`; `proto/prototype.py`
- **Licence:** ODbL 1.0
- **Access:** public
- **Status:** used: prototype

### D19. MassDOT District 3 repeating flood areas

- **Provider:** MassDOT District 3 list
- **Resolution / coverage:** 38 sites, no dates
- **Period used:** multi-year (undated)
- **Role:** validation
- **How it is used:** Check: share of known repeat-flood sites flagged (P >= 0.5) vs share of all segments flagged
- **Where in the code:** `proto/data/massdot_repeat_flood_d3.csv`; `proto/prototype.py (checks.massdot_repeat_sites)`
- **Licence:** Agency document (no licence stated)
- **Access:** obtained from MassDOT material (not a public feed)
- **Status:** used: prototype (check only)

### D20. NWS Local Storm Reports (LSR)

- **Provider:** NWS, via Iowa Environmental Mesonet archive
- **Resolution / coverage:** points rounded to 0.01 deg; MA
- **Period used:** storm window
- **Role:** validation
- **How it is used:** Was there >= 10/30 cm within 300 m when and where flooding was reported (vs 2,000 random road points)
- **Where in the code:** `proto/obs_fetch.py -> docs/proto/obs/lsr_sep2023.csv`; `proto/validate_points.py`
- **Licence:** Public domain (NWS)
- **Access:** public
- **Status:** used: prototype

### D21. NOAA Storm Events Database

- **Provider:** NOAA NCEI
- **Resolution / coverage:** episode/event points with narratives; MA
- **Period used:** storm window (Sep 2023: 11 records)
- **Role:** validation; label
- **How it is used:** Same point check as LSR; narratives for washouts/closures
- **Where in the code:** `proto/obs_fetch.py -> docs/proto/obs/stormevents_sep2023.csv`; `proto/validate_points.py`
- **Licence:** Public domain (NOAA)
- **Access:** public
- **Status:** used: prototype

### D22. Historical road-flood reports (docs/prone/flood_reports.json)

- **Provider:** compiled: NWS storm reports, crash records, MassDOT District 3 reports
- **Resolution / coverage:** 4,551 dated points (crash 2,136; storm_report 1,636; D3 report 779)
- **Period used:** 2002-2026
- **Role:** validation; label
- **How it is used:** Storm-day check of runs (reports inside the run box on the storm days); positives for the graph model
- **Where in the code:** `docs/prone/flood_reports.json`; `proto/prototype.py (--reports)`; `sim/validate.py`; `sim/infra/impacts.py`
- **Licence:** Mixed public sources
- **Access:** public
- **Status:** used: prototype (check). Build script not in repo

### D23. Documented labels, Sep 2023 Leominster (labels_sep2023_leominster.csv)

- **Provider:** compiled here from WX1BOX SKYWARN log, MA CDBG-DR plan, MassDOT reports, news
- **Resolution / coverage:** 93 road sites (29 culvert failures, 11 closed, 8 washouts, ...)
- **Period used:** 2023-09-11/12
- **Role:** label; validation
- **How it is used:** Main ground truth: recall / flagged share / lift of the closure rules; point hit test
- **Where in the code:** `proto/data/labels_sep2023_leominster.csv`; `proto/prototype.py (--labels)`; `proto/validate_points.py`
- **Licence:** Facts from public documents; quotes <= 20 words
- **Access:** public sources
- **Status:** used: prototype

### D24. MassDOT roadway events feed (logger)

- **Provider:** MassDOT (events.massdot.evbg.net)
- **Resolution / coverage:** statewide events (closures, incidents), polled every 15 min
- **Period used:** from 2026-10-21 onward
- **Role:** label (future)
- **How it is used:** Time-stamped history of closures for future storms; not yet joined to any run
- **Where in the code:** `proto/events_logger.py (events_log.yml) -> docs/proto/obs/massdot_events/`
- **Licence:** Public feed (no licence stated)
- **Access:** public
- **Status:** not used yet (logging only)

### D25. Vermont July 2023 road closures (VTrans TMC, digitized)

- **Provider:** S. Grant 2025, FEMC / UVM ("RoadClosures2023")
- **Resolution / coverage:** 63 closed state-highway segments
- **Period used:** 2023-07-11/12 snapshots
- **Role:** validation (independent storm)
- **How it is used:** Planned second, independent test of the closure rules (validation only, not training)
- **Where in the code:** `proto/data/vt_roadclosures_jul2023.geojson (+ README)`
- **Licence:** CC0
- **Access:** public
- **Status:** not used yet (file in repo; no code reads it)

### D26. PRISM daily rain via ACIS

- **Provider:** PRISM Climate Group / NOAA RCC ACIS GridData
- **Resolution / coverage:** ~4 km daily
- **Period used:** 14-30 days before forecast time
- **Role:** input (forecast mode)
- **How it is used:** Antecedent wetness index (k = 0.85) for the live road-graph model
- **Where in the code:** `refresh/graph_refresh.py`
- **Licence:** PRISM terms (free, attribution)
- **Access:** public
- **Status:** used: live graph model; not in prototype

### D27. USGS annual peaks + ratings (legacy NWIS archive)

- **Provider:** USGS NWIS (legacy /peak, get_ratings)
- **Resolution / coverage:** MA stream gauges + boundary gauges
- **Period used:** full record
- **Role:** validation (planned)
- **How it is used:** Archived before the legacy shutdown, for peak-Q / AEP checks and stage-Q rating checks
- **Where in the code:** `tools/usgs_legacy_archive.py (usgs_archive.yml) -> archive/usgs_legacy/`
- **Licence:** Public domain (USGS)
- **Access:** public
- **Status:** not used yet (archived)

## Open points

- **Road graph (D14) and historical road-flood reports (D22).** Both files are in the repo, but the scripts that built them are not. Their provenance comes from `docs/methods.html` and from the file contents.
- **NAACC culvert surveys (D17).** The NAACC ArcGIS service refused our query, so the surveys came from naacc.org Data Center exports instead. I have not verified the licence terms or whether a download needs a login.
- **MRMS 24 h rain (D03).** Only the statewide GPU engine uses it. The LISFLOOD-FP prototype runs with a fixed NRCS AMC II and no antecedent rain.
- **Not used yet.** This covers three datasets: the MassDOT events logger (D24), which has been logging since 21 Oct 2026; the Vermont July 2023 closures (D25), which are the planned independent test storm; and the USGS peaks and ratings archive (D27).
- **USGS endpoints.** USGS will retire the legacy WaterServices service between Nov 2026 and Q1 2027. The gauge fetchers now use the OGC Water Data API and fall back to the legacy service while it still answers. A Sept 2023 fetch through the OGC API reproduced the committed `docs/proto/obs/gauges_sep2023.json` exactly. The comparison is in `docs/proto/obs/_logs/ogc_test_sep2023.json`.
