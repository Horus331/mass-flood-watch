# Road-closure prototype: sep2023h_transfer_sep2023h_neattleborough_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2023-09-11T14:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 7,581 |
| Expected closures (sum of probabilities) | 72.1 |
| Segments with closure probability >= 50% | 42 (12.0 km) |
| Further segments that may close (stream reaches the road crest) | 94 (20.9 km) |
| Culverts overtopped / surcharged | 84 / 0 of 515 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 52.8 mm |
| Flood model run time | 1398 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 1 | North Attleborough | 0.71 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 9.5 h into the storm; worst hour 30 mm (26% of the storm); a culvert within 100 m is overtopped |
| 2 | 1.00 | Route 1 | North Attleborough | 0.69 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 9.5 h into the storm; worst hour 30 mm (26% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Barrows Street | Norton | 0.97 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 27 mm (31% of the storm) |
| 4 | 1.00 | Barrows Street | Norton | 0.97 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 0.5 h into the storm; worst hour 27 mm (31% of the storm); water beside the road 0.26 m below its crest (design freeboard 0.30 m; P 0.60) |
| 5 | 1.00 | Roy Avenue | Attleboro | 1.12 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 7.5 h into the storm; worst hour 41 mm (27% of the storm); runoff beside / along the road at 0.6 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.16); a culvert within 100 m is overtopped |
| 6 | 1.00 | Read Street | Attleboro | 0.66 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.5 h into the storm; worst hour 41 mm (28% of the storm); a culvert within 100 m is overtopped |
| 7 | 1.00 | Riverview Drive | North Attleborough | 0.70 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 9.5 h into the storm; worst hour 30 mm (26% of the storm); a culvert within 100 m is overtopped |
| 8 | 1.00 | Riverview Drive | North Attleborough | 0.70 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 9.5 h into the storm; worst hour 30 mm (26% of the storm) |
| 9 | 1.00 | Liberty Drive | Attleboro | 0.61 m of water at peak; over 30 cm for 6.5 h; 30 cm reached 11.0 h into the storm; worst hour 43 mm (39% of the storm); a culvert within 100 m is overtopped |
| 10 | 1.00 | Ramp | North Attleborough | 0.60 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 9.0 h into the storm; worst hour 35 mm (27% of the storm); runoff beside / along the road at 1.7 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.79); a culvert within 100 m is overtopped |
| 11 | 1.00 | Dexter Street | Attleboro | 0.56 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 8.0 h into the storm; worst hour 45 mm (37% of the storm); a culvert within 100 m is overtopped |
| 12 | 0.99 | Route 152 | Seekonk | 0.56 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 8.0 h into the storm; worst hour 35 mm (46% of the storm); a culvert within 100 m is overtopped |
| 13 | 0.99 | Route 120 | North Attleborough | 0.53 m of water at peak; over 30 cm for 2.5 h; 30 cm reached 9.5 h into the storm; worst hour 30 mm (30% of the storm); runoff beside / along the road at 0.4 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.11); a culvert within 100 m is overtopped |
| 14 | 0.99 | Ramp | North Attleborough | 0.53 m of water at peak; over 30 cm for 4.5 h; 30 cm reached 9.5 h into the storm; worst hour 38 mm (28% of the storm); runoff beside / along the road at 1.3 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.55); a culvert within 100 m is overtopped |
| 15 | 0.98 | Park Drive | Attleboro | 0.50 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 11.0 h into the storm; worst hour 41 mm (30% of the storm); water beside the road 0.25 m above its crest (design freeboard 0.30 m; P 1.00); road sag 0.5 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 40 mm; catchment 401.3 ha) (P 0.98) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
