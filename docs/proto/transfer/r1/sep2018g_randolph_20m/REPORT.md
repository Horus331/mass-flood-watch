# Road-closure prototype: sep2018g_transfer_sep2018g_randolph_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2018-09-18T08:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 23,135 |
| Expected closures (sum of probabilities) | 71.3 |
| Segments with closure probability >= 50% | 20 (6.3 km) |
| Further segments that may close (stream reaches the road crest) | 48 (12.7 km) |
| Culverts overtopped / surcharged | 55 / 0 of 707 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 39.5 mm |
| Flood model run time | 1465 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Route 1A | Westwood | 1.57 m of water at peak; over 30 cm for 9.0 h; 30 cm reached 9.5 h into the storm; worst hour 23 mm (41% of the storm); water beside the road 0.45 m below its crest (design freeboard 0.30 m; P 0.16); a culvert within 100 m is overtopped |
| 2 | 1.00 | Ramp | Braintree | 1.30 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 27 mm (45% of the storm); a culvert within 100 m is overtopped |
| 3 | 1.00 | Ramp | Braintree | 1.30 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 27 mm (45% of the storm); a culvert within 100 m is overtopped |
| 4 | 1.00 | Ramp | Braintree | 1.30 m of water at peak; over 30 cm for 7.5 h; 30 cm reached 11.0 h into the storm; worst hour 27 mm (45% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.93 | Blue Hills Parkway | Milton | 0.44 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 14.5 h into the storm; worst hour 21 mm (49% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.93 | Blue Hills Parkway | Milton | 0.44 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 14.5 h into the storm; worst hour 22 mm (49% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.81 | Howard Street | Braintree | 0.39 m of water at peak; over 30 cm for 6.0 h; 30 cm reached 10.0 h into the storm; worst hour 32 mm (48% of the storm); water beside the road 0.34 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.7 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 32 mm; catchment 26.8 ha) (P 0.82) |
| 8 | 0.80 | Common Street | Braintree | 0.38 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 15.5 h into the storm; worst hour 27 mm (45% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.79 | Condlin Drive | Randolph | 0.38 m of water at peak; over 30 cm for 4.0 h; 30 cm reached 11.0 h into the storm; worst hour 26 mm (44% of the storm); water beside the road 0.29 m above its crest (design freeboard 0.30 m; P 1.00); road sag 1.0 m deep (drains sized for the 10-yr hour, 43 mm; peak hour here 26 mm; catchment 17.2 ha) (P 0.82) |
| 10 | 0.77 | Thacher Street | Milton | 0.37 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 16.5 h into the storm; worst hour 20 mm (48% of the storm) |
| 11 | 0.77 | Thacher Street | Milton | 0.37 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 16.5 h into the storm; worst hour 20 mm (48% of the storm) |
| 12 | 0.61 | Southeast Expressway HOV Lane | Quincy | 0.33 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 11.0 h into the storm; worst hour 32 mm (53% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.5 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.28); road sag 1.4 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 31 mm; catchment 20.5 ha) (P 0.62) |
| 13 | 0.61 | Southeast Expressway HOV Lane | Quincy | 0.33 m of water at peak; over 30 cm for 3.5 h; 30 cm reached 11.0 h into the storm; worst hour 31 mm (51% of the storm); water beside the road 0.27 m above its crest (design freeboard 0.30 m; P 1.00); runoff beside / along the road at 1.8 m/s: shoulder / edge may wash out (gravel / loam erodes from ~1 m/s; P 0.43); road sag 1.4 m deep (underpass, drains sized for the 50-yr hour, 58 mm; peak hour here 31 mm; catchment 20.5 ha) (P 0.62) |
| 14 | 0.60 | Newport Avenue | Quincy | 0.33 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 16.5 h into the storm; worst hour 27 mm (48% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.60 | Newport Avenue | Quincy | 0.33 m of water at peak; over 30 cm for 2.0 h; 30 cm reached 16.5 h into the storm; worst hour 27 mm (48% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
