# Road-closure prototype: sep2026g_transfer_sep2026g_brockton_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2026-09-27T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 14,166 |
| Expected closures (sum of probabilities) | 159.3 |
| Segments with closure probability >= 50% | 107 (20.1 km) |
| Further segments that may close (stream reaches the road crest) | 103 (18.8 km) |
| Culverts overtopped / surcharged | 184 / 0 of 824 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 30.1 mm |
| Flood model run time | 2250 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 28 | Brockton | 1.00 m of water at peak; over 30 cm for 11.0 h; 30 cm reached 8.5 h into the storm; worst hour 15 mm (14% of the storm); water beside the road 0.86 m above its crest (design freeboard 0.30 m; P 1.00); road sag 2.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 15 mm; catchment 67.9 ha) (P 1.00) |
| 2 | 1.00 | Route 123 | Easton | 0.74 m of water at peak; over 30 cm for 10.5 h; 30 cm reached 9.0 h into the storm; worst hour 14 mm (12% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Route 123 | Easton | 0.75 m of water at peak; over 30 cm for 10.0 h; 30 cm reached 9.5 h into the storm; worst hour 14 mm (12% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | North Central Street | East Bridgewater | 1.16 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 5.5 h into the storm; worst hour 15 mm (15% of the storm) |
| 5 | 1.00 | Pleasant Street | East Bridgewater | 1.16 m of water at peak; over 30 cm for 14.0 h; 30 cm reached 5.5 h into the storm; worst hour 15 mm (15% of the storm) |
| 6 | 1.00 | Ellsworth Street | Brockton | 0.96 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 6.5 h into the storm; worst hour 15 mm (14% of the storm); water beside the road 0.32 m below its crest (design freeboard 0.30 m; P 0.43); a culvert within 100 m is overtopped |
| 7 | 1.00 | Ellsworth Street | Brockton | 0.96 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 6.5 h into the storm; worst hour 15 mm (14% of the storm) |
| 8 | 1.00 | Ellsworth Street | Brockton | 0.95 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 6.5 h into the storm; worst hour 15 mm (14% of the storm); water beside the road 0.12 m below its crest (design freeboard 0.30 m; P 0.88); a culvert within 100 m is overtopped |
| 9 | 1.00 | Carleton Street | Brockton | 0.95 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 6.5 h into the storm; worst hour 15 mm (14% of the storm); water beside the road 0.12 m below its crest (design freeboard 0.30 m; P 0.88); a culvert within 100 m is overtopped |
| 10 | 1.00 | Carleton Street | Brockton | 0.95 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 6.5 h into the storm; worst hour 15 mm (14% of the storm); water beside the road 0.12 m below its crest (design freeboard 0.30 m; P 0.88); a culvert within 100 m is overtopped |
| 11 | 1.00 | Poplar Road | Brockton | 0.89 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 6.5 h into the storm; worst hour 15 mm (14% of the storm); a culvert within 100 m is overtopped |
| 12 | 1.00 | Spring Street | Brockton | 0.89 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 6.5 h into the storm; worst hour 15 mm (14% of the storm); water beside the road 0.32 m below its crest (design freeboard 0.30 m; P 0.44); a culvert within 100 m is overtopped |
| 13 | 1.00 | Spring Street | Brockton | 0.89 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 6.5 h into the storm; worst hour 15 mm (13% of the storm); water beside the road 0.32 m below its crest (design freeboard 0.30 m; P 0.44); a culvert within 100 m is overtopped |
| 14 | 1.00 | Condlin Drive | Randolph | 0.83 m of water at peak; over 30 cm for 13.0 h; 30 cm reached 6.5 h into the storm; worst hour 23 mm (23% of the storm); water beside the road 0.74 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 23 mm; catchment 17.2 ha) (P 1.00) |
| 15 | 1.00 | Newbury Street | Brockton | 0.69 m of water at peak; over 30 cm for 12.0 h; 30 cm reached 7.5 h into the storm; worst hour 15 mm (14% of the storm); water beside the road 0.44 m below its crest (design freeboard 0.30 m; P 0.17); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
