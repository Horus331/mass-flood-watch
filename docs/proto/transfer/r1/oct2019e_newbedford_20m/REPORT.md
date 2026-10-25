# Road-closure prototype: oct2019e_transfer_oct2019e_newbedford_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2019-10-27T15:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 10,072 |
| Expected closures (sum of probabilities) | 51.1 |
| Segments with closure probability >= 50% | 15 (2.7 km) |
| Further segments that may close (stream reaches the road crest) | 114 (17.5 km) |
| Culverts overtopped / surcharged | 38 / 0 of 442 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 40.0 mm |
| Flood model run time | 2306 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.99 | River Road | Mattapoisett | 0.56 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 2.5 h into the storm; worst hour 22 mm (34% of the storm) |
| 2 | 0.99 | Mosher Street | New Bedford | 0.53 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 7.0 h into the storm; worst hour 39 mm (42% of the storm); water beside the road 0.47 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 39 mm; catchment 6.6 ha) (P 0.99) |
| 3 | 0.94 | Route 6 | Fairhaven | 0.46 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 8.0 h into the storm; worst hour 32 mm (42% of the storm); water beside the road 0.37 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 32 mm; catchment 3.8 ha) (P 0.96) |
| 4 | 0.82 | Green Street | Fairhaven | 0.39 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 8.5 h into the storm; worst hour 32 mm (42% of the storm); water beside the road 0.34 m above its crest (design freeboard 0.30 m; P 1.00) |
| 5 | 0.82 | Elm Street | Dartmouth | 0.39 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 7.0 h into the storm; worst hour 30 mm (36% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.74 | Acushnet Avenue | New Bedford | 0.37 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 7.0 h into the storm; worst hour 36 mm (42% of the storm); water beside the road 0.33 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 36 mm; catchment 10.2 ha) (P 0.80) |
| 7 | 0.70 | Blackmer Street | New Bedford | 0.35 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 7.5 h into the storm; worst hour 38 mm (42% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 38 mm; catchment 4.0 ha) (P 0.79) |
| 8 | 0.70 | Winsor Street | New Bedford | 0.35 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 7.5 h into the storm; worst hour 39 mm (42% of the storm); water beside the road 0.29 m above its crest (design freeboard 0.30 m; P 1.00) |
| 9 | 0.68 | Orchard Street | New Bedford | 0.35 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 7.0 h into the storm; worst hour 37 mm (41% of the storm); water beside the road 0.20 m above its crest (design freeboard 0.30 m; P 1.00) |
| 10 | 0.66 | JFK Boulevard | New Bedford | 0.34 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 7.0 h into the storm; worst hour 37 mm (42% of the storm); water beside the road 0.32 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 37 mm; catchment 7.8 ha) (P 0.68) |
| 11 | 0.66 | South Second Street | New Bedford | 0.34 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 7.5 h into the storm; worst hour 36 mm (42% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.4 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 36 mm; catchment 10.2 ha) (P 0.64) |
| 12 | 0.60 | Russells Mills Road | Dartmouth | 0.33 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 7.5 h into the storm; worst hour 30 mm (35% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.59 | Katherine Street | New Bedford | 0.32 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 8.0 h into the storm; worst hour 38 mm (42% of the storm); water beside the road 0.31 m above its crest (design freeboard 0.30 m; P 1.00) |
| 14 | 0.57 | Russells Mills Road | Dartmouth | 0.32 m of water at peak; over 30 cm for 1.0 h; 30 cm reached 7.5 h into the storm; worst hour 32 mm (37% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.52 | Division Street | New Bedford | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 8.5 h into the storm; worst hour 39 mm (42% of the storm); water beside the road 0.24 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.3 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 39 mm; catchment 6.6 ha) (P 0.56) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
