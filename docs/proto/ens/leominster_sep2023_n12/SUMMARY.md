# Ensemble leominster_sep2023_n12: 3 members + center

Latin hypercube (seed 2023091), truncated at +-2 sd, around the center env `None`.

| input | env | spread | sources |
|---|---|---|---|
| rain | LF_RAIN_SCALE | sigma_ln 0.2 | Ciach et al. 2007; Villarini & Krajewski 2010; Zhang et al. 2016 (MRMS) |
| cn | LF_CN_SCALE | sd 0.1 (x center) | NRCS NEH 630 ch.10 Table 10-1 (AMC I/III); Hjelmfelt 1991 |
| n_chan | LF_N_CHAN | sigma_ln 0.25 | Chow 1959 Table 5-6; Arcement & Schneider 1989 (USGS WSP 2339) |
| n_land | LF_N_FP | sigma_ln 0.35 | Chow 1959 Table 5-6 (flood plains); Arcement & Schneider 1989 |
| drain | LF_INFIL_MMH | sigma_ln 0.4 | NRCS NEH 630 ch.7 minimum infiltration rates by HSG (Musgrave 1955) |

## Members

| member | rain | cn | n_chan | n_land | drain | rain mean mm | segments P>=0.5 |
|---|---|---|---|---|---|---|---|
| m01 | 0.9731 | 0.8429 | 0.7901 | 1.0064 | 0.5954 | 104 | 168 |
| m02 | 0.9285 | 0.9338 | 0.7145 | 0.753 | 0.7287 | 100 | 188 |
| m04 | 1.0235 | 0.9915 | 1.4353 | 0.9218 | 1.276 | 110 | 240 |

## Gauges: ensemble 5-95 % band vs observed

| gauge | quantity | p05 | p50 | p95 | center | observed | inside |
|---|---|---|---|---|---|---|---|
| 01094400 NORTH NASHUA RIVER AT FITCHBURG, MA | rise_m | 0.948 | 1.02 | 1.353 | None | 1.0 | True |
| 01094400 NORTH NASHUA RIVER AT FITCHBURG, MA | peak_q_m3s | 20.446 | 29.275 | 34.016 | None | 43.6 | False |
| 01094400 NORTH NASHUA RIVER AT FITCHBURG, MA | peak_h | 8.55 | 9.0 | 9.45 | None | 9.25 | True |
| 01094500 NORTH NASHUA RIVER NEAR LEOMINSTER, MA | rise_m | 2.649 | 2.82 | 3.306 | None | 2.92 | True |
| 01094500 NORTH NASHUA RIVER NEAR LEOMINSTER, MA | peak_q_m3s | 97.67 | 132.827 | 133.878 | None | 157.4 | False |
| 01094500 NORTH NASHUA RIVER NEAR LEOMINSTER, MA | peak_h | 8.1 | 9.0 | 9.45 | None | 12.5 | False |

## Segments

In box: 5100. Expected closures: {'p_ens_depth': 198.7, 'p_ens_overtop': 395.7, 'p_mean_depth': 227.7, 'single_p_depth': None}.


## Documented sites (Sept 2023 Leominster labels)

y = 1: segments with a road point within 30 m of a documented site (any type); y = 0: in-box segments not within the loose match of any site (100-300 m / same-name) -- unreported is not proof of dry, so y = 0 is noisy and Brier is dominated by negatives

| probability | Brier | climatology | BSS | site mean P | site recall P>=0.5 |
|---|---|---|---|---|---|
| p_ens_depth | 0.03988 | 0.01809 | -1.204 | 0.38 | 0.359 |
| p_ens_overtop | 0.0635 | 0.01809 | -2.5091 | 0.662 | 0.654 |
| p_mean_depth | 0.03734 | 0.01809 | -1.0634 | 0.404 | 0.359 |
| p_mean_overtop | 0.05887 | 0.01809 | -2.2536 | 0.645 | 0.654 |

Reliability (segments): bin: n, mean P, observed frequency

- p_ens_depth: 0.00-0.05: 4426, 0.0, 0.014; 0.25-0.50: 42, 0.333, 0.119; 0.50-0.75: 17, 0.667, 0.0; 0.95-1.00: 126, 1.0, 0.143
- p_ens_overtop: 0.00-0.05: 4231, 0.0, 0.009; 0.25-0.50: 80, 0.333, 0.087; 0.50-0.75: 38, 0.667, 0.026; 0.95-1.00: 262, 1.0, 0.141

Files: ensemble.json (everything above + site table), ens_segments.geojson (p_ens, p_ens_overtop, p_mean, p_single, depth 5/50/95 %).

Caveats: one storm-wide rain multiplier per member (no spatial rain error); 12 members resolve P_ens in steps of 1/12 and the 5-95 % band is close to the member min-max; parameters sampled independently; model-structure error (DEM, channel burn, 2-D solver) is not sampled.
