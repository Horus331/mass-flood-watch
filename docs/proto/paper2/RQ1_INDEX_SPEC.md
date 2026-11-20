# Paper 2, RQ1: road-edge stream-power index, definition fixed before computing it (20 Nov 2026)

Fixed now, before the index exists and before any comparison with damage. Code: `proto/edge_spi.py`; workflow `edge_spi.yml`.

**Inputs.** USGS 3DEP bare earth at 1 m (image service, best available), Leominster road segments of the Sept 2023 model run
(`phase1/parametric_t2/t2_base/segments.geojson`, 716 segments). No damage labels, no model depths.

**Terrain processing.** Core tiles of 4 km with a 1 km buffer; pits filled, depressions filled, flats resolved (pysheds 0.5); D8 flow
directions; accumulation in cells (= m² of upslope area at 1 m); slope = magnitude of the 3 × 3 gradient (m/m).

**Road edges.** Points every 2 m along each segment, 3 m and 5 m to each side of the centreline (curb line and shoulder for typical
two-lane roads); at each point the maximum accumulation and the slope in a 3 × 3 window.

**Index.** SPI = A × S (m²) per edge point. Per segment: maximum, 90th percentile, maximum A, and the equivalent edge length above the
95th percentile of all edge points in the area.

**Known limits, stated now.** D8 on a filled surface; storm drains not represented (the index is the curb flow if inlets are full or absent);
bilinear resampling by the service; the lidar date is whatever 3DEP serves as best available (to be recorded from the service metadata).

**How it will be used (needs Mo's go; separate pre-registration).** In-sample in Leominster: does SPI separate damaged from undamaged
segments beyond modelled depth (AUC 0.87) and traffic (0.85)? Descriptive only (calibration storm). Out-of-sample only with a second damage
inventory. Nothing here changes the live model.
