# Road-closure prototype: aug2023g_transfer_aug2023g_newbedford_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-08-08T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 10,300 |
| Expected closures (sum of probabilities) | 33.0 |
| Segments with closure probability >= 50% | 5 (1.7 km) |
| Further segments that may close (stream reaches the road crest) | 54 (11.1 km) |
| Culverts overtopped / surcharged | 37 / 0 of 474 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 68.3 mm |
| Flood model run time | 1899 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.89 | Reed Road | Westport | 0.42 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 63 mm (98% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.83 | River Road | Mattapoisett | 0.40 m of water at peak; over 30 cm for 16.0 h; 30 cm reached 2.5 h into the storm; worst hour 19 mm (71% of the storm) |
| 3 | 0.53 | Route 6 | Dartmouth | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.0 h into the storm; worst hour 54 mm (94% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.52 | Route 6 | Dartmouth | 0.31 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.0 h into the storm; worst hour 53 mm (92% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.51 | (unnamed) | Rochester | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 10.5 h into the storm; worst hour 34 mm (91% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.48 | Chase Road | Dartmouth | 0.29 m of water at peak; worst hour 59 mm (88% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.41 | Union Avenue | Westport | 0.28 m of water at peak; worst hour 59 mm (97% of the storm); a culvert within 100 m is overtopped |
| 8 | 0.35 | New Bedford Road | Rochester | 0.26 m of water at peak; worst hour 35 mm (84% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.33 | Mosher Street | New Bedford | 0.26 m of water at peak; worst hour 33 mm (64% of the storm); water beside the road 0.19 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 32 mm; catchment 6.6 ha) (P 0.34) |
| 10 | 0.27 | Russells Mills Road | Dartmouth | 0.24 m of water at peak; worst hour 49 mm (81% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.26 | Purchase Street | New Bedford | 0.24 m of water at peak; worst hour 25 mm (51% of the storm); water beside the road 0.50 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.16); road sag 0.5 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 25 mm; catchment 4.3 ha) (P 0.98) |
| 12 | 0.26 | Glen Road | Westport | 0.24 m of water at peak; worst hour 46 mm (99% of the storm); runoff beside / along the road at 0.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.33); a culvert within 100 m is overtopped |
| 13 | 0.24 | Route 6 | Dartmouth | 0.23 m of water at peak; worst hour 52 mm (80% of the storm); a culvert within 100 m is overtopped |
| 14 | 0.21 | Elm Street | Dartmouth | 0.22 m of water at peak; worst hour 48 mm (80% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.21 | Pine Hill Road | Westport | 0.22 m of water at peak; worst hour 59 mm (99% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
