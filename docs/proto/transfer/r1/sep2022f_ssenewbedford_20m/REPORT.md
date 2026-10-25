# Road-closure prototype: sep2022f_transfer_sep2022f_ssenewbedford_20m

Flood model: LISFLOOD-FP 8.2 (acceleration (local inertial, Bates et al. 2010) on CPU (OpenMP)), 20 m grid, storm from 2022-09-13T07:00Z.

| Result | Value |
| --- | --- |
| Road segments in the area | 9,900 |
| Expected closures (sum of probabilities) | 15.4 |
| Segments with closure probability >= 50% | 1 (0.0 km) |
| Further segments that may close (stream reaches the road crest) | 1 (0.7 km) |
| Culverts overtopped / surcharged | 5 / 0 of 448 |
| Road segments cut off from hospitals | 0 |
| Worst added trip time to a hospital | 0.0 min |
| Heaviest hour of rain | 21.5 mm |
| Flood model run time | 1785 s |


## Top segments

| # | P(close) | Road | Town | Why |
| --- | --- | --- | --- | --- |
| 1 | 0.52 | River Road | Mattapoisett | 0.31 m of water at peak; over 30 cm for 5.5 h; 30 cm reached 2.5 h into the storm; worst hour 13 mm (49% of the storm) |
| 2 | 0.25 | Reed Road | Westport | 0.23 m of water at peak; worst hour 13 mm (43% of the storm); a culvert within 100 m is overtopped |
| 3 | 0.11 | Union Avenue | Westport | 0.18 m of water at peak; worst hour 12 mm (39% of the storm); a culvert within 100 m is overtopped |
| 4 | 0.07 | Route 177 | Westport | 0.15 m of water at peak; worst hour 13 mm (42% of the storm); a culvert within 100 m is overtopped |
| 5 | 0.06 | Route 6 | Dartmouth | 0.15 m of water at peak; worst hour 11 mm (26% of the storm) |
| 6 | 0.04 | Acushnet Road | Mattapoisett | 0.12 m of water at peak; worst hour 10 mm (40% of the storm) |
| 7 | 0.03 | Chase Road | Dartmouth | 0.12 m of water at peak; worst hour 16 mm (37% of the storm) |
| 8 | 0.03 | Glen Road | Westport | 0.12 m of water at peak; worst hour 18 mm (42% of the storm) |
| 9 | 0.03 | Pine Hill Road | Westport | 0.11 m of water at peak; worst hour 19 mm (45% of the storm) |
| 10 | 0.02 | Elm Street | Dartmouth | 0.09 m of water at peak; worst hour 15 mm (36% of the storm) |
| 11 | 0.02 | Route 6 | Dartmouth | 0.09 m of water at peak; worst hour 14 mm (40% of the storm) |
| 12 | 0.02 | Route 6 | Dartmouth | 0.09 m of water at peak; worst hour 14 mm (40% of the storm) |
| 13 | 0.02 | (unnamed) | Dartmouth | 0.09 m of water at peak; worst hour 16 mm (38% of the storm) |
| 14 | 0.02 | Slades Corner Road | Dartmouth | 0.09 m of water at peak; worst hour 16 mm (38% of the storm) |
| 15 | 0.01 | Ramp | Dartmouth | 0.08 m of water at peak; worst hour 9 mm (26% of the storm) |

Closure probability (depth): Phi((peak depth - 0.30) / 0.10), physics prior v0. A physics prior from published thresholds, not calibrated on observed closures.
