# Paper 2, RQ1: data check for a road-edge flow index (19 Nov 2026; groundwork only, no labels used, no model change)

## Elevation
- **USGS 3DEP image service** (`elevation.nationalmap.gov/.../3DEPElevation/ImageServer`), already used by `proto/site_layers.py`
  (`fetch_dem`): returns the best available bare-earth surface resampled to the requested cell size. It gave 1 m lidar for the WPI campus.
- **MassGIS statewide lidar mosaic:** 0.5 m DEM built from regional projects (MassGIS "Lidar Terrain Data"). For central Massachusetts the
  candidate sources are the 2021 USGS Central-Eastern project (QL1, 0.5 m DEM) and the 2013–14 Sandy project (QL2, 1 m, western third
  of Worcester County). **Which project covers Leominster must be checked on the MassGIS "Latest and Best" tile index** before relying on
  it; the shell here cannot reach those servers, so the fetch would run in a GitHub workflow like `site_layers.yml`.
- Acquisition dates matter: a 2021 surface predates the Sept 2023 storm, so washouts are not in it (good for a predictor).

## Size and cost (Leominster part of the Sept 2023 model box)
- 716 road segments, 277 km of road. A ±30 m corridor at 1 m is ~17 million cells; the whole 20 × 20 km box at 1 m would be 400 million.
- Plan: fetch tiles for the box at 1 m (tiled requests, as for the NAIP fix), hydrologically condition (priority-flood with breaching, the
  same method as the model's terrain), then compute flow on the full tile set but **sample only the road corridors**. Flow accumulation on
  400 M cells needs ~10–20 GB RAM: fine on a Turing CPU node, too big for a free GitHub runner (7 GB). On a runner, process in
  overlapping 5 × 5 km tiles with a 1 km buffer (upslope areas on road edges rarely exceed that in Leominster's catchments; to be checked).

## The index (proposal; fixed in a pre-registration before any label is looked at)
For each road segment, along both edges (the cells 2–6 m from the centreline, where curb lines and shoulders sit):
1. **Upslope area draining along the edge** A (m²), D-infinity or MFD flow on the 1 m surface, with the road surface itself included.
2. **Edge slope** S along the flow path (m/m).
3. **Stream-power index** SPI = A·S (and a rain-scaled version: A × storm rain excess from the model × S, in units of unit discharge × slope).
4. Summary per segment: maximum and 90th percentile along the length; length of edge above a threshold.
A known limit: the lidar surface does not see storm drains, so A is the area that would drain along the curb if the inlets are full or
absent. That is the case the washouts suggest.

## How it would be tested (later, needs Mo's go)
- In-sample, Leominster (Sept 2023 DPW points, unit = segment): does SPI separate damaged from undamaged segments beyond what modelled
  depth and traffic already do (AUC 0.87 and 0.85)? Descriptive only, because the storm is the calibration storm.
- Out-of-sample: only with a second damage inventory (MEMA / FEMA PA Category C request, Mo to send).
- Not reused: the old edge-erosion layer and the ≥ 0.5 m/s flow test (PROJECT_LOG §6).
