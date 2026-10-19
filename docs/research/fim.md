# NOAA OWP HAND-FIM flood-depth maps from NWM flows (`sim/fim_maps.py`)

A second, independent flood map for each storm, built with NOAA's own national method rather than our hydraulic engine. It gives a baseline to compare the engine against, and a statewide map we can produce in one night.

Run: `.github/workflows/fim.yml` (workflow_dispatch: `storms`, `hucs`, `extra`) or `python sim/fim_maps.py --storms jul2023 --hucs west,east`. The offline check is `python sim/fim_maps.py --selftest`.

## Method (FIM4, github.com/NOAA-OWP/inundation-mapping)
HAND ("Height Above Nearest Drainage") is the height of each 10 m DEM cell above the stream cell it drains to. OWP precomputes it for each HUC8, together with a synthetic rating curve for each reach segment (HydroID). The curve comes from Manning's equation over the HAND-derived channel and floodplain geometry, and OWP calibrates it to USGS gauges and rating curves where it can.
1. **Flow.** We take the peak NWM `analysis_assim` streamflow for each `feature_id` (NHDPlus v2 COMID) over the storm window, as the max of the hourly `channel_rt` tm00 files. The URLs are the same Google and Azure ones as `sim/nwm_compare.py`. `analysis_assim` is nudged toward USGS gauges, so it is NOAA's best estimate of what happened. Windows (UTC) are jul2023 07-09T12→07-12T00, sep2023 09-11T12→09-13T12, dec2023 12-17T18→12-20T00 and jan2024 01-09T06→01-11T12.
2. **Stage.** For each branch, `hydroTable_<b>.csv` maps HydroID ↔ feature_id and holds stage (m) against `discharge_cms`. Stage per HydroID = `np.interp(Q_peak, discharge_cms, stage)`, clamped at both ends of the table. Lake rows (`LakeID != -999`) are dropped, and a feature with no flow gets no water, as in OWP `inundate`.
3. **Depth.** depth = stage(HydroID of the cell) − HAND(cell), only inside that HydroID's catchment, and depth ≥ 0. The catchment comes from `gw_catchments_reaches_filtered_addedAttributes_<b>.tif` and HAND from `rem_zeroed_masked_<b>.tif`.
4. **Mosaic.** Branches combine into a HUC8 by max. Branch 0 covers all streams; the other branches are level paths, which handle the larger rivers. HUC8s then combine into the statewide map by max, built block by block.

Outputs go to HF `mohabeldokla/mass-flood-watch-tiles` under `runs/fim_<storm>/`:
- `depth.tif`: int16 cm (GDAL scale 0.01 → m), EPSG:5070, 10 m, DEFLATE, with overviews
- `summary.json`: flooded km² and max depth per HUC8, wet HydroIDs, failed branches, NWM file coverage and validation scores
- `huc/<HUC8>.tif`: uploaded as each HUC8 finishes
- `validation.json`

The western mosaic is published once the western HUC8s are done (`partial: true`), and again when the run finishes.

## Data paths
| what | path | status |
|---|---|---|
| OWP HAND, CIROH mirror (primary) | `s3://ciroh-owp-hand-fim/hand_fim_<ver>/<HUC8>/`. Versions `hand_fim_4_9_9_0` (FIMserv default), `hand_fim_4_8_7_2` and `hand_fim_4_5_2_11`. Per HUC8: `branch_ids.csv`, `hydrotable.csv`, `branches/<b>/…` | **Anonymous** (`--no-sign-request`), according to the source of CIROH FIMserv 0.2.13 (`fimserve/datadownload.py`, read from the PyPI wheel). The script picks the newest `hand_fim_*` it can list. |
| branch files | `branches/<b>/rem_zeroed_masked_<b>.tif`, `gw_catchments_reaches_filtered_addedAttributes_<b>.tif`, `hydroTable_<b>.csv` | OWP naming convention. FIMserv confirms `branches/0/gw_catchments_reaches_filtered_addedAttributes_0.gpkg`. The script finds files by listing and falls back to the HUC `hydrotable.csv` filtered by `branch_id`. |
| OWP HAND, ESIP | `s3://noaa-nws-owp-fim/hand_fim/` | The OWP README says ESIP AWS credentials are needed, so it is **not anonymous**. The script tries it second and logs the result. |
| NFIE/CFIM HAND (fallback) | `https://web.corral.tacc.utexas.edu/nfiedata/HAND/<HUC6>/` (`<HUC6>hand.tif`, `*catchmask.tif`, `hydroprop-fulltable*.csv`). MA HUC6s are 010700, 010802, 010900, 011000 and 020200. | This is an older HAND (v0.1, superseded by v0.2 at ORNL). Catchments are COMIDs. File names are found from the directory index. Used only if no OWP bucket answers (`--source nfie` forces it). |
| NWM | `storage.googleapis.com/national-water-model/nwm.<ymd>/analysis_assim/nwm.t<hh>z.analysis_assim.channel_rt.tm00.conus.nc` (Azure `noaanwm` mirror) | Already used by `sim/nwm_compare.py`. |

The anonymous S3 listing could not be run from the agent sandbox, which has no general internet, so the first Actions log is the real check. It prints `HAND source s3://…: N prefixes, picked …` and the number of branches and GB for each HUC8.

### Massachusetts HUC8s
- **West** (run first): 01080203 Deerfield, 01080206 Westfield, 01080202 Millers, 01080204 Chicopee, 01080201 Middle Connecticut, 01080205 Lower Connecticut, 01100005 Housatonic, 02020003 Hudson-Hoosic, 01080207 Farmington (small MA part), 02020006 Middle Hudson (small MA part).
- **East**: 01070004 Nashua, 01070005 Concord (Sudbury-Assabet-Concord), 01070006 Merrimack, 01090001 Charles (incl. Boston Harbor, Mystic, Neponset, North Shore), 01090003 Blackstone, 01090004 Narragansett (Taunton), 01090002 Cape Cod, 01100001 Quinebaug.
- Path pattern: `s3://ciroh-owp-hand-fim/hand_fim_4_9_9_0/<HUC8>/branches/<branch>/…`. For example, the Deerfield branch 0 HAND is `…/01080203/branches/0/rem_zeroed_masked_0.tif`.

The HUC list was checked against the USGS HUC name table. Two edges are not checked: the 01070006 split, which came after 1997, and which coastal basins sit inside 01090001.

## Known limits (read before comparing with the engine)
- **Flat, urban and coastal areas.** HAND underestimates flooding there. Near-zero HAND relief makes depths very sensitive to the rating curve, storm drains and pluvial ponding off the network are invisible, and there is **no tide or surge**. Boston Harbor, North Shore and Cape Cod maps are not meaningful for coastal flooding.
- **No backwater.** Each catchment is flat-pooled at its own stage, so there is no backwater from a main stem into tributaries and no confluence effect. Water also cannot cross a catchment divide.
- **No structures.** There are no culverts, bridges, dams or levees, apart from the levee-protected masks OWP applies elsewhere, which we do not apply. A crossing that blocks and floods a road does not show up. This is exactly where our engine and `crossings_capacity.py` add value.
- **Only as good as NWM.** Steep, small basins like the Deerfield in July 2023 depend on NWM peak magnitude. `nwm_compare.py` measures that, and `analysis_assim` is close to gauges only at assimilated gauges. Peaks are hourly snapshots, so they run slightly low.
- **Synthetic rating curves** come from a 10 m DEM without bathymetry, so the channel itself always shows as "flooded". `flooded_km2` therefore includes normal river area and the parts of each HUC8 outside MA.
- **Steady state.** This is the peak flow placed everywhere at once, not a timed flood wave.

## Validation with our existing tools
`fim_maps.py` resamples the mosaic by **max** to the EPSG:26986 30 m grid that `sim/validate.py` reads (`validate/meta.json` + `hmax.npy`, in metres). It then calls `validate.main` and stores the scores in `summary.json` and `runs/fim_<storm>/validation.json`.
- **USGS STN high-water marks** (`docs/validation/stn_ma.json`):
  - depth above ground at the mark (`bias_m`, `mae_m`, `within_50cm`)
  - `wet_within_30m`
  - per-reach and coastal splits
  - The `wse_*` metrics need a `z.npy` DEM, which HAND outputs do not include. They will read `wse_found: 0`, so ignore them or add a 30 m DEM `z.npy` on the same grid.
- **Road flood reports** (`docs/prone/flood_reports.json`): storm-day hit rate within 100 m against the random-road rate. Expect HAND to score low on reports caused by pluvial flooding or culverts, which is the point of the comparison.
- **Gauges**: `validate.py`'s gauge WSE check also needs `z.npy`. The direct check is the HAND stage at the gauge's HydroID against the observed peak stage. That is not implemented yet; the planned route is to take `stage` from the branch hydroTable at the gauge COMID that `nwm_compare.py` already resolves.
- **Fair comparison with the engine**: score both maps on the same 30 m grid and the same marks. Report each separately by reach type (steep western reaches against flat urban and coastal ones), because HAND's known biases differ by setting.

## Changelog
- **2026-10-19**: first version (research scout): script, workflow and this note. The selftest passes locally. It covers stage interpolation, depth, branch and HUC max mosaics, the NWM peak reader, S3 key discovery and the `validate.py` export. The anonymous bucket listing is not yet confirmed from a networked machine.
