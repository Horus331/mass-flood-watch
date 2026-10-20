# Infrastructure impact layer: roads and stream crossings (Team 4, 19 Oct 2026)

What happens to roads and culverts in a flood run. The layer works on District 3 first and is written to run statewide. Code: `sim/infra/crossings_all.py` (inventory), `sim/infra/culvert.py` (HDS-5 hydraulics), `sim/infra/impacts.py` (per-run impacts and upload). Each script has an offline `--selftest`, and all three pass locally.

Claim level (docs/validation/protocol.md): **L2**. The layer reports hydraulic and traffic states computed from the modelled peak depth and the inventory: overtopped, surcharged, impassable, cut off. It does not predict structural failure (L3 would need fragility curves).

## 1. Data sources (REST pages and field lists checked 19 Oct 2026)

| id | source | what it gives | count | access |
|---|---|---|---|---|
| U | **USGS Database of Stream Crossings in the United States** (Wieferich 2022, [doi:10.5066/P9YX6KTB](https://doi.org/10.5066/P9YX6KTB)); service [`stream_crossings/FeatureServer`](https://services.arcgis.com/v01gqwM5QqNysAAi/ArcGIS/rest/services/stream_crossings/FeatureServer) | Layer 0 holds the modelled crossings (TIGER 2020 roads × NHDPlus HR flowlines): `stream_crossing_id`, `nhdhr_gnis_stream_name`, `tiger2020_feature_names`, `tiger2020_mtfcc_feature_class`, `crossing_type`. Layer 1 holds NBI 2019 observations linked to them: `structure_id`, `crossing_type`, `crossing_subtype`, evaluations. | 6,608,268 nationwide. The MA count is computed at run time (not counted here, see §6). | public, CC0, maxRecordCount 2000 |
| N | **NAACC culvert assessments**: [`NAACC_Culvert_Assessment_2/FeatureServer/0`](https://services.arcgis.com/cJ9YHowT8TU7DUyn/ArcGIS/rest/services/NAACC_Culvert_Assessment_2/FeatureServer/0), covering 14 NE/Mid-Atlantic states | Surveyed structures. Shape and inlet type are among `Inlet_Type`/`Inlet_Ty_1`/`Inlet_Stru` (truncated names). Also `Material`, `Inlet_Widt`/`Inlet_Heig` (ft), `Number_Of_` (culverts), `Road_Fill_` (ft), `Crossing_C` (NAACC code), `Crossing_T`, `Evaluation`, `State`. | MassDEP says about 22 % of MA culverts are surveyed. | public, maxRecordCount 2000 |
| P | **MA Stream Crossings Project** (USGS/UMass/MassDEP, Sturtevant & McCarthy, [doi:10.5066/P9BL9CW4](https://doi.org/10.5066/P9BL9CW4)), layer 0 | `DRNAREA` (mi²), `PK10AEP…PK02AEP` (ft³/s), `BFWDTH`/`BFDPTH` (ft). Per design flood (10/25/50/100-yr, SCS) and per type (BC box / AC arch / PC pipe): `*ORDE*` original road deck, `*USIE*`/`*DSIE*` channel inverts, `*LCE*` low chord, all ft NAVD88. Spans and heights are for the **proposed** standard-compliant designs, not the existing culverts. | 365 crossings (Oct 2026). Phases 2A–4 add more, and the service also feeds StreamStats. | public, CC0 |
| B | **MassDOT bridges & culverts** (BIMS): `Roads/Bridges/MapServer/0`. Tried on `gis.massdot.state.ma.us` first, then on the `gisstg` host (the only one confirmed so far) | `structureCategory`, `structureMaterial`, `culvertCondition`, `structureLength`, `bridgeDepartmentNumber`, lat/lon. Covers NBI bridges, short spans 10–20 ft and culverts 4–10 ft; the service itself says its culvert inventory is incomplete. | n/a | public. Optional: the run skips it if the host can't be reached. |
| — | **TIGERweb** `State_County/MapServer` (Census) | MA county polygons, used for the in-state filter and the county column | 14 | public |

Not used: the NAACC Stream Crossing Explorer download at naacc.org has the full NAACC record, including outlet dimensions, but needs a free account (data_sources.md 5.1, decision E). OSM `culvert=yes` is ODbL share-alike.

**Merge** (`crossings_all.py`):
1. U is the backbone.
2. N, P and B attach to the nearest U point within 50 m (B within 30 m). P matches by NAACC code through N first.
3. N and P records with no U match become rows of their own.
4. Points outside MA are dropped by point-in-polygon against the county polygons.
5. `d3 = 1` inside the District 3 box (EPSG:26986 128000, 856000, 206000, 946000).

Output: `docs/network/crossings_all.json` with columns `lon lat id src road stream county mtfcc xtype naacc n_barrels shape material inlet span_m rise_m fill_m drn_km2 pk10..pk500 bf_w bf_d deck_m usie_m dsie_m nbi_id mdot_cat mdot_mat mdot_cond naacc_eval d3`. Values are SI, and `None` means unknown.

The NAACC export uses truncated names, so `pick_fields` finds the shape, inlet and material columns from their values ("Round Culvert…", "Projecting/Headwall/Wingwalls/Mitered", "Metal/Concrete/Plastic…"). The mapping it chose is stored in `field_map`, and the lead should check it after the first run.

## 2. Culvert hydraulics (`culvert.py`)

Inlet control follows FHWA HDS-5, 3rd ed. (Schall et al. 2012, FHWA-HIF-12-026), Appendix A. It is computed in US units with K_u = 1; Q is flow per barrel, A the full barrel area and D the rise:

- unsubmerged, form 1: HW_i/D = H_c/D + K (Q/AD^0.5)^M + K_s S, where H_c = d_c + V_c²/2g
- unsubmerged, form 2: HW_i/D = K (Q/AD^0.5)^M
- submerged: HW_i/D = c (Q/AD^0.5)² + Y + K_s S
- K_s = −0.5 (+0.7 for mitered inlets)
- The unsubmerged forms apply for Q/AD^0.5 ≤ 3.5 and the submerged form for ≥ 4.0. In between the two are blended linearly; HDS-5 draws a tangent curve there.

Constants (K, M, c, Y) come from HDS-5 Tables A.1/A.2/A.4. They cover:
- circular concrete: square edge with headwall, groove end with headwall, groove end projecting
- circular CMP: headwall, mitered, projecting
- concrete box: wingwall flares of 30–75°, 90/15° and 0°, plus a 90° headwall with chamfers
- elliptical concrete
- CM pipe-arch and closed arch
- concrete open-bottom arch (2:1)

Fallbacks are flagged `coef_exact = False`:
- plastic with a projecting or mitered end uses the CMP constants, as HY-8 does
- plastic with a headwall uses the concrete constants
- stone and wood boxes use the concrete box constants
- a projecting concrete pipe uses the groove-end projecting constants

Outlet control uses HDS-5 eq. 4 for a full barrel: H = [1 + k_e + 2g n² L / R^{4/3}] V²/2g, and HW_o = H + h_o − S L.
- h_o = max(TW, (d_c + D)/2) when the barrel is full (inlet submerged or TW ≥ D). Otherwise h_o = max(TW, d_c), so a trickle does not read as HW = D/2.
- k_e comes from HDS-5 Table C.2, and n from typical values (concrete 0.012, CMP 0.024).
- The governing headwater is max(HW_i, HW_o). `q_at_headwater` inverts it by bisection.

**Status** at headwater HW above the invert:
- crest = deck − invert, else rise + fill, else rise + 0.6 m (cover assumed; flagged `crest_assumed`)
- *overtopped*: HW ≥ crest
- *surcharged*: HW/D > 1.0
- *ok*: otherwise

Selftest checks against published values:

| check | published | computed |
|---|---|---|
| HDS-5 Chart 1 example: 42-in concrete pipe, Q = 120 cfs, HW/D for scales 1/2/3 | 2.5 / 2.1 / 2.2 | 2.44 / 2.04 / 2.10 |
| HDS-5 Chart 2 example: 36-in CMP, Q = 66 cfs, HW/D for headwall / mitered / projecting | 1.8 / 2.1 / 2.2 | 1.79 / 2.10 / 2.15 |
| Critical-depth chart: D = 66 in, Q = 100 cfs | d_c/D 0.50 | 0.503 |
| Outlet control, hand calculation | HW_o 0.933 m | 0.932 m |

The chart readings are nomograph values, so the tolerance is ±0.12. The selftest also checks the box critical depth closed form, monotonic headwater, the inversion round trip and the number of barrels.

## 3. Roads (`impacts.py`)

- **Geometry.** `docs/graph_segments.json` (52,698 segments) is decoded exactly as in `w4_flood_gpu.py`. Each part is then densified to a point every res/2. w4 samples vertices only and misses cells on long edges.
- **Junction trimming.** Points within one cell of a segment's end vertices are left out when the segment has interior points, so one flooded junction does not flag every road that meets there.
- **Per segment:** max and mean depth, and max h·v when `vmax.npy` exists.
- **Classes:**

| class | rule | source |
|---|---|---|
| passable | < 15 cm | NWS *Turn Around Don't Drown*: "Six inches of water will reach the bottom of most passenger cars causing loss of control and possible stalling" ([weather.gov/tsa/hydro_tadd](https://weather.gov/tsa/hydro_tadd)) |
| impassable for cars | 15–30 cm | NWS (as above); Pregnolato et al. 2017, *Transp. Res. D* 55:67–81 (speed falls to 0 at 300 mm) |
| dangerous | ≥ 30 cm, or h·v ≥ 0.3 m²/s | Pregnolato 2017; Shand et al. 2011, ARR Project 10 Stage 2 (small passenger car: 0.3 m still water, DV 0.3 m²/s) |

The extracted DV value in the Shand report was garbled, so check it in the PDF.

**Knock-on effects.** This ports the site's own logic from `docs/v2/index.html` (consequence model, Oct 18 review):
- Segments of class ≥ 1 are removed.
- Partly wet segments are slowed by the Pregnolato speed curve.
- Minutes from the nearest hospital are computed by multi-source Dijkstra on the segment adjacency (`links`), with free-flow speeds of 45/65/95 km/h by class. Hospitals are snapped to segment midpoints within 3 km.
- *Cut off*: reachable when dry, unreachable now.
- *Isolated*: the trip takes 30+ minutes longer.
- Separately, connected components give the site's `reach()`: dry segments no longer connected to any open major road (cls ≥ 1).
- Everything is also reported with the site's 30 cm cut.

**Crossing headwater.** The channel cell is the one with the largest channels30 drainage area within 60 m, else the deepest cell (as in `crossings_capacity.py`).
- Rain-on-grid runs burn the channel to the bankfull bed, so HW = h. When z.npy and a surveyed invert both exist, HW = z + h − invert.
- HAND-FIM runs measure depth above the lidar water surface, so HW = h + bankfull depth. Bankfull depth comes from the record, else channels30, else Bieger 2015 (0.30 A^0.213).
- `--combine` takes the cell-wise max of the depth grids (nearest resampling onto the first run's grid) and, for each crossing, the larger of the per-run headwaters.
- When a deck elevation and z.npy exist, the deck freeboard (deck − WSE) also decides overtopping.
- Crossings with no geometry and no crest are *overtopped* when the road within 30 m carries ≥ 15 cm, and *unknown* otherwise.

**Reports.** Scoring uses the storm days from meta, exactly as `validate.py` does:
- point hit rate: ≥ 10 cm within 100 m
- segment hit rate: the nearest segment within 100 m is impassable
- lift: the share of flagged segments with a storm-day report within 200 m, divided by the same share for all segments in the box

**Outputs** go to `runs/<run>/` in one HF commit:
- `impacts.json`: summary, thresholds, citations, `seg_rows` for affected segments, and crossing rows
- `impacts_seg.bin`: uint8 `[code, max_cm]` per segment. Codes: 0 dry, 1 wet < 15 cm, 2 impassable, 3 dangerous, 4 dry but cut off, 5 isolated, 255 outside the run.
- With `--combine` the files are `impacts_combined.*`.

A smoke test on the real 52,698 segments with a synthetic 20 m District 3 grid (3,900 × 4,500) ran in 12 s on a CPU.

## 4. Limits

- The flood grids give peak depth, not simultaneous depth. A road can be "cut" by water that was never there at the same time as water on its detour, so cut-offs are an upper bound.
- About 78 % of MA culverts have no NAACC survey, so geometry is missing for most U crossings. Those crossings get a status from the deck or road depth, or stay *unknown*.
- P dimensions describe proposed designs and are never used as existing geometry. Only P's deck and inverts are used.
- NAACC dimensions are inlet dimensions in feet, sometimes estimated ("EST."). The NAACC record has no barrel length or slope, so length defaults to 2 × crest + 8 m and slope to 1 %. Outlet control is therefore indicative only.
- At 20–30 m cells the channel cell may not be the stream under the road (`crossings_capacity.py` has the same QC issue). HW then includes valley-floor ponding.
- HAND-FIM depth plus bankfull depth assumes the FIM DEM surface sits at bankfull. In reality it sits at the lidar-date water surface, so HW is overestimated by about the base-flow depth.
- Road class codes (`cls`) only distinguish 3 speeds, and AADT is imputed for many segments, so delay minutes are coarse.
- The h·v criterion needs `vmax.npy`, which only engine runs have. HAND-FIM runs are classified by depth only.

## 5. From District 3 to the state

Nothing in the code is District 3-specific except the `d3` flag:
- `crossings_all.py` already fetches the whole state.
- `impacts.py` works on whatever box the run has, including statewide 30 m runs and `fim_*` maps, because roads, crossings and facilities are all statewide files.
- The Dijkstra and connected-component analysis already runs on the full 52,698-segment graph, so cut-offs that cross a box edge are counted.

Next steps for statewide coverage:
1. Run `crossings_all.py` on the runner and commit `crossings_all.json`. Expected size: a few MB.
2. Use the NAACC full download (account) for outlet dimensions and slope.
3. Pull P phases as USGS publishes them (decks and inverts for thousands more crossings).
4. For coastal runs, add tailwater from the tide/surge grid to `hw_outlet` (`tw` argument).
5. Add the hmax time series per frame (w4 already writes `roads_cm.npy`) to get time-consistent cut-offs instead of peak-based ones.

## 6. Open items for the lead

- The real MA counts from U and N are not yet known: the agent shell has no internet. Run `python sim/infra/crossings_all.py` on the runner and read the `counts` it prints.
- The NAACC `field_map` chosen from the data needs a check. The likely mapping is `Inlet_Ty_1` or `Inlet_Stru` = shape and `Inlet_Type` = inlet edge.
- `gis.massdot.state.ma.us` was unconfirmed; only the staging host (`gisstg`) answered the agent.
