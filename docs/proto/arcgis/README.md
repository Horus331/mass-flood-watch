# District 3 road-segment flood vulnerability layer (for ArcGIS)

Prepared for MassDOT Highway District 3 GIS. Research product, not an operational MassDOT dataset.
Contact: **Mohab Eldokla**, PhD student, Civil, Environmental and Architectural Engineering, Worcester Polytechnic Institute
(Mass Flood Watch project; email as given in the hand-off message). Built 2026-10-28 by `proto/arcgis_export.py`.
Method note: [METHOD.md](METHOD.md). Field dictionary: [FIELDS.csv](FIELDS.csv) (also inside the zip).

## Files

| file | CRS | features | size | content |
|---|---|---|---|---|
| `d3_road_flood_vulnerability_shp.zip` | EPSG:26986 (NAD83 / Massachusetts Mainland, m) | 48,945 | 5.7 MB | full layer, polyline shapefile (.shp/.shx/.dbf/.prj/.cpg) + FIELDS.csv |
| `d3_road_flood_vulnerability.csv` | – (no geometry) | 48,945 | 7.2 MB | same attribute table; join on `seg_id` |
| `d3_road_flood_vulnerability.geojson` | EPSG:4326 (WGS 84, RFC 7946) | 7,061 | 7.6 MB | same fields; every High and Medium segment plus every Low segment that carries ≥ 5 cm of modelled water in any run, a cascade value or a scored crossing. The 41,884 Low segments left out are dry (< 5 cm) in all 26 runs; they are in the shapefile and the CSV. |

The layer covers the 48,945 segments of the District 3 road graph that lie in at least one model box or carry a report. The other 3,753
graph segments were never modelled and are not included.

Open in ArcGIS Pro: *Add Data* on the zip's `.shp` (or the GeoJSON via *JSON To Features*). Suggested symbology: unique values on `vuln`.

## Vulnerability class (`vuln`)

Applied in this order; the first rule that matches sets the class, and `vuln_why` records which one.

| class | rule | segments | km |
|---|---|---|---|
| **High** | `n_flag` ≥ 2 (flagged, p_close ≥ 0.5, in two or more of the 25 catalogue storms) | 133 | |
| **High** | flagged by the model (`n_flag` ≥ 1 or `d3_pclose` ≥ 0.5) **and** at least one documented report or MassDOT repeating flood site on the segment | 19 | |
| | *High total* | *152* | *102.2* |
| **Medium** | `n_flag` = 1 | 400 | |
| **Medium** | flagged only in the District 3 Sept 2023 run (`d3_pclose` ≥ 0.5) | 86 | |
| **Medium** | documented report or MassDOT repeating site, never flagged by the model | 220 | |
| **Medium** | in the "may close" layer (stream reaches the road crest) in ≥ 1 catalogue storm, never flagged | 561 | |
| | *Medium total* | *1,267* | *792.6* |
| **Low** | modelled, never flagged, no report | 47,526 | 15,764.1 |

The class is a screening rule, chosen for transparency, not fitted or validated as a class. The crossing damage score and the cascade
(delay) fields are **not** used in the class; they are attached for prioritisation.

## Main fields (full list with units in FIELDS.csv)

| field | unit | meaning |
|---|---|---|
| `seg_id` | | segment id in the Mass Flood Watch road graph (`docs/graph_segments.json`, built from the MassDOT road inventory). **Not** a RoadInventory ID: join to MassDOT layers spatially. |
| `road`, `town`, `rd_class`, `len_m`, `aadt`, `aadt_dflt` | m, veh/day | road-inventory attributes carried by the graph. Class: highway = Interstate, arterial = other numbered US / MA route, local / collector = the rest. `aadt_dflt` = 1 where AADT is the 1,000 veh/day default. |
| `n_cov` | storms | how many of the 25 catalogue storms modelled this segment (their 20 × 20 km-scale boxes overlap; 0–12 per segment) |
| `n_flag`, `flag_rate`, `flag_strm`, `max_pclose` | storms, 0–1 | storms with p_close ≥ 0.5, the share of covering storms, which storms, and the highest p_close |
| `n_may` | storms | storms in the "may close" layer (p_may_close ≥ 0.5) with p_close < 0.5 |
| `cat_dep_m` | m | highest modelled peak depth on the segment over the catalogue storms |
| `d3_dep_m`, `d3_pclose`, `d3_h30` | m, 0–1, h | District 3 Sept 11–13 2023 run: peak depth, p_close, hours over 30 cm (blank = outside its box) |
| `n_rpt`, `rpt_src`, `rpt_ids` | reports | documented flood reports from the 25 storms assigned to the segment (nearest segment within 30 m) and their source families |
| `n_mdot`, `mdot_ids` | sites | MassDOT District 3 repeating flood sites assigned to the segment (nearest within 100 m) |
| `vh_delay`, `vh_detour`, `h_closed`, `det_min` | veh-h, h, min | cascade, Sept 2023 run: vehicle-hours of delay caused by this segment closing or slowing, its detour part, hours closed, largest added detour time |
| `peak_vc`, `h_ovcap` | ratio, h | cascade: peak volume / capacity and hours over capacity when the segment carries other closures' detours |
| `dmg_xid`, `dmg_p`, `dmg_rank`, `dmg_pct` | 0–1, rank, % | highest-scoring road-stream crossing within 30 m: damage score, rank among 4,733 scored crossings, percentile (0 = top) |

Blank (null) means "not computed for this segment" (outside the run, no crossing, never closed), not zero.

## Method (short; details in METHOD.md)

- **Flood model.** LISFLOOD-FP 8.2, local-inertial 2-D shallow water, 20 m grid, MRMS radar rain, NRCS curve-number loss ×0.88 with
  2 mm/h infiltration (the "clean parity baseline", `docs/proto/parity/BASELINE.md`). 25 storms 2018–2026 on their own boxes (catalogue)
  plus one District-wide run of 11–13 Sept 2023 (78 × 90 km box, 45,099 segments, 48 h).
- **p_close** is a physics prior, not fitted to closures: Φ((peak road depth − 0.30 m) / 0.10 m), combined with freeboard, culvert
  (FHWA HDS-5) and fast-water terms. Flagged = p_close ≥ 0.5, i.e. about 30 cm of water at the segment's second-highest point.
- **Reports.** 320 report rows for the 25 storms (NWS LSR / Storm Events, news, WX1BOX SKYWARN, Leominster DPW, MA state, MassDOT
  water-surface crashes, SeeClickFix): 310 assigned, 7 town-level only, 3 with no segment within 30 m.
- **Cascade.** `proto/cascade.py` on the Sept 2023 run: closures ≥ 30 cm, Pregnolato et al. (2017) depth–speed curve for 5–30 cm,
  shortest-path detours capped at 30 min, no traffic assignment. District totals: 166,239 vehicle-hours of delay; peak 51,421 people
  losing hospital, fire or police coverage, 94 % of them on roads that stay dry.
- **Damage.** `proto/damage.py`: specific stream power γQS/w at crossings, logistic fragility from `damage_model.json`, max over the 10
  damage-layer runs (9 storms).

## Caveats (please read)

1. **Model output, not observation.** Classes come from simulated storms. A Low segment can still flood (the model catches about a third
   of documented sites at its default threshold; `BASELINE.md`: 41 of 132 sites over 9 storms), and a High segment may be a modelling
   artefact (for example a depression in the terrain model or a missing culvert or storm drain; storm drains are not modelled).
2. **Coverage bias.** `n_flag` counts storms that modelled the segment. Worcester segments are covered by up to 11–12 storms, many rural
   segments by 1. One storm can never make a segment High without a report. Use `flag_rate` and `n_cov` alongside `vuln`.
3. **Light storms are under-predicted** by this baseline (gauge rise bias negative on 8 of 9 storms; none of 20 documented sites on 5 light
   storms is flagged). The layer mostly reflects the large storms (Sept 2023, Sept 2021, Aug 2021).
4. **MassDOT repeating flood sites.** All 38 sites were assigned to a segment; only 4 of them are on a segment the model flags.
   The model does not reproduce most of MassDOT's known repeating sites (drainage-capacity and sag ponding are not resolved at 20 m).
5. **Cascade numbers** are scenario consequences for one storm, with no traffic assignment and AADT defaults on many local roads
   (`aadt_dflt`); they are lower bounds on delay and are not validated against counts. People losing emergency access are computed for
   the network as a whole, **not attributable to a single segment**, so there is no per-segment access field.
6. **Damage score** is experimental (not adopted in `docs/proto/damage/DAMAGE.md`): a ranking, not a probability, labelled on one storm
   only, and known to over-score large rivers (the top-ranked crossings are I-190 over the Nashua River).
7. **Segment ids** are internal; geometry is the graph's, simplified from the road inventory. Divided roads may be one segment per direction.

## Data sources

MassDOT road inventory (via `docs/graph_segments.json`); MassDOT District 3 repeating flood sites; MassDOT IMPACT crash open data (water
surface); NOAA MRMS radar QPE (AWS); USGS 3DEP-derived 10 m DEM, NHDPlus HR, USGS stream gauges; USDA SSURGO soils; NLCD; MA Stream
Crossings Project / NAACC culverts; FHWA NBI bridges; 2020 Census blocks; OpenStreetMap facilities; NWS Local Storm Reports and NCEI
Storm Events; WX1BOX SKYWARN reports; Leominster DPW; SeeClickFix; news reports. Full list: `docs/proto/advisors/datasets.md`.

## Reproduce

`python proto/arcgis_export.py` (about 1 minute, committed data only; writes this folder and `build_stats.json`, then re-reads all three
files with geopandas and checks feature counts, CRS, field-name length and geometry length).
