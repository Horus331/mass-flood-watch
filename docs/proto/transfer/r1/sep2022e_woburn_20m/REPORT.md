# Road-closure prototype: sep2022e_transfer_sep2022e_woburn_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2022-09-05T01:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 19,722 |
| Expected closures (sum of probabilities) | 37.7 |
| Segments with closure probability >= 50% | 5 (1.2 km) |
| Further segments that may close (stream reaches the road crest) | 9 (4.4 km) |
| Culverts overtopped / surcharged | 20 / 0 of 706 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 38.6 mm |
| Flood model run time | 1272 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 1.00 | Anna Road | Woburn | 0.69 m of water at peak; over 30 cm for 8.0 h; 30 cm reached 10.5 h into the storm; worst hour 24 mm (43% of the storm); a culvert within 100 m is overtopped |
| 2 | 0.74 | Lexington Street | Woburn | 0.37 m of water at peak; over 30 cm for 3.0 h; 30 cm reached 9.5 h into the storm; worst hour 31 mm (55% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.58 | Highland Avenue | Winchester | 0.32 m of water at peak; over 30 cm for 1.5 h; 30 cm reached 17.0 h into the storm; worst hour 12 mm (53% of the storm) |
| 4 | 0.50 | Ramp-US 3 | Burlington | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 13.5 h into the storm; worst hour 15 mm (40% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.50 | Ramp | Burlington | 0.30 m of water at peak; over 30 cm for 0.5 h; 30 cm reached 13.5 h into the storm; worst hour 15 mm (40% of the storm); a culvert within 100 m is overtopped |
| 6 | 0.48 | Mill Street | Reading | 0.30 m of water at peak; worst hour 35 mm (57% of the storm); a culvert within 100 m is overtopped |
| 7 | 0.48 | Mill Street | Reading | 0.30 m of water at peak; worst hour 35 mm (57% of the storm) |
| 8 | 0.41 | Old Cambridge Road | Woburn | 0.28 m of water at peak; worst hour 28 mm (51% of the storm); a culvert within 100 m is overtopped |
| 9 | 0.29 | Sylvester Avenue | Winchester | 0.24 m of water at peak; worst hour 29 mm (69% of the storm); a culvert within 100 m is overtopped |
| 10 | 0.27 | Sylvester Avenue | Winchester | 0.24 m of water at peak; worst hour 30 mm (69% of the storm); a culvert within 100 m is overtopped |
| 11 | 0.14 | Pond Street | Billerica | 0.19 m of water at peak; worst hour 16 mm (23% of the storm) |
| 12 | 0.14 | Presidential Way | Woburn | 0.19 m of water at peak; worst hour 32 mm (51% of the storm) |
| 13 | 0.14 | Presidential Way | Woburn | 0.19 m of water at peak; worst hour 31 mm (50% of the storm) |
| 14 | 0.14 | Presidential Way | Woburn | 0.19 m of water at peak; worst hour 31 mm (51% of the storm); a culvert within 100 m is overtopped |
| 15 | 0.14 | (unnamed) | Woburn | 0.19 m of water at peak; worst hour 31 mm (50% of the storm); a culvert within 100 m is overtopped |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
