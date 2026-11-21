# RQ1 v2 index: run check on Leominster (20 Nov 2026; values only, not compared with damage)

GitHub run 44742669478, `proto/edge_spi.py` with the v2 fields of `PREREG_RQ1_V2_DRAFT.md`; output `edge_spi_leominster_v2.json` (v1
fields recomputed identically). 710 of 712 segments have at least one 50 m window after dropping edge points within 30 m of a crossing
or on channel cells (upslope area > 0.5 km²). Area-wide 95th percentile of window maxima: 11,895 m².

**Length dependence (the point of v2):** rank correlation with segment length is 0.65 for v1 `spi_max`, 0.63 for v2 `spi_window_max`
(a segment with more windows still has more chances to hold a high one) and **0.36 for `spi_window_share`** (share of windows above the
95th percentile). So `spi_window_share` is the length-neutral main measure, as the draft says; `spi_window_max` should be read with length
in the model. 16.8 % of segments have at least one window above the threshold.

No damage labels were read. The v2 test waits for a second damage inventory (MEMA / FEMA PA Cat C request, Mo to send).

## Full road graph, four towns (21 Nov 2026; values only, no labels)
`edge_spi.yml` with `segments=graph` (all District road-graph segments of the town inside its box), GitHub runs 44843535809–44843554476:

| Town | Segments with an index | Tiles | Missing elevation | Area 95th percentile of 50 m window maxima (m²) | Segments with ≥ 1 window above it |
|---|---|---|---|---|---|
| Leominster (full) | 1,534 | 9 | 0 % | 9,477 | 11.9 % |
| Fitchburg | 1,491 | 9 | 0 % | 17,498 | 12.8 % |
| Worcester | 4,374 | 16 | 0 % | 10,941 | 12.5 % |
| Northbridge | 595 | 9 | 0 % | 11,126 | 17.1 % |

**Note for freezing v2:** the 95th-percentile threshold is computed per area, so it differs between towns (9,500–17,500 m²). For an
out-of-sample test across towns the threshold must be one fixed number, set before the new inventory is opened: proposed **10,000 m²**
(the rounded median of the four), or per-town percentiles if the test stays within one town. To be decided when v2 is frozen.
