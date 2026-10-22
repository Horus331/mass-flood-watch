# Ensemble ens_test: 1 members + center

Latin hypercube (seed 2023091), truncated at +-2 sd, around the center env `LF_CN_AMC=II LF_CN_SCALE=1.0 LF_INFIL_MMH=2 LF_LOSS=cn LF_NO_UPLOAD=1 LF_QOUT=1`.

| input | env | spread | sources |
|---|---|---|---|
| rain | LF_RAIN_SCALE | sigma_ln 0.2 | Ciach et al. 2007; Villarini & Krajewski 2010; Zhang et al. 2016 (MRMS) |
| cn | LF_CN_SCALE | sd 0.1 (x center) | NRCS NEH 630 ch.10 Table 10-1 (AMC I/III); Hjelmfelt 1991 |
| n_chan | LF_N_CHAN | sigma_ln 0.25 | Chow 1959 Table 5-6; Arcement & Schneider 1989 (USGS WSP 2339) |
| n_land | LF_N_LAND_SCALE | sigma_ln 0.35 | Chow 1959 Table 5-6 (flood plains); Arcement & Schneider 1989 |
| drain | LF_INFIL_MMH | sigma_ln 0.4 | NRCS NEH 630 ch.7 minimum infiltration rates by HSG (Musgrave 1955) |

## Members

| member | rain | cn | n_chan | n_land | drain | rain mean mm | segments P>=0.5 |
|---|---|---|---|---|---|---|---|
| m00 | 1 | 1 | 1 | 1 | 1 | 50 | 97 |
| m01 | 0.9731 | 0.8429 | 0.7901 | 1.0064 | 0.5954 | 49 | 42 |

## Gauges: ensemble 5-95 % band vs observed

| gauge | quantity | p05 | p50 | p95 | center | observed | inside |
|---|---|---|---|---|---|---|---|
| 01094400 NORTH NASHUA RIVER AT FITCHBURG, MA | rise_m | 0.42 | 0.42 | 0.42 | 0.55 | 0.68 | False |
| 01094400 NORTH NASHUA RIVER AT FITCHBURG, MA | peak_q_m3s | 1.419 | 1.419 | 1.419 | 1.419 | 43.6 | False |
| 01094400 NORTH NASHUA RIVER AT FITCHBURG, MA | peak_h | 6.0 | 6.0 | 6.0 | 6.0 | 6.0 | True |
| 01094500 NORTH NASHUA RIVER NEAR LEOMINSTER, MA | rise_m | 0.0 | 0.0 | 0.0 | 0.0 | 0.43 | False |
| 01094500 NORTH NASHUA RIVER NEAR LEOMINSTER, MA | peak_q_m3s | 4.796 | 4.796 | 4.796 | 4.796 | 157.4 | False |
| 01094500 NORTH NASHUA RIVER NEAR LEOMINSTER, MA | peak_h | 0.0 | 0.0 | 0.0 | 0.0 | 6.0 | False |

## Segments

In box: 5100. Expected closures: {'p_ens_depth': 42.0, 'p_ens_overtop': 116.0, 'p_mean_depth': 62.2, 'single_p_depth': 123.4}.

- **depth rule**: center closes 97, ensemble majority 42; closed->open 55, open->closed 0; closed in some but not all members 0 (P_ens 0.25-0.75: 0); closed in every member 42, in any 42.
- **overtop rule**: center closes 260, ensemble majority 116; closed->open 144, open->closed 0; closed in some but not all members 0 (P_ens 0.25-0.75: 0); closed in every member 116, in any 116.

## Documented sites (Sept 2023 Leominster labels)

y = 1: segments with a road point within 30 m of a documented site (any type); y = 0: in-box segments not within the loose match of any site (100-300 m / same-name) -- unreported is not proof of dry, so y = 0 is noisy and Brier is dominated by negatives

| probability | Brier | climatology | BSS | site mean P | site recall P>=0.5 |
|---|---|---|---|---|---|
| p_ens_depth | 0.01974 | 0.01809 | -0.0907 | 0.231 | 0.231 |
| p_ens_overtop | 0.02602 | 0.01809 | -0.4383 | 0.423 | 0.423 |
| p_mean_depth | 0.01883 | 0.01809 | -0.0407 | 0.247 | 0.231 |
| p_mean_overtop | 0.02299 | 0.01809 | -0.2705 | 0.414 | 0.449 |
| single_p_depth | 0.02356 | 0.01809 | -0.3018 | 0.328 | 0.282 |
| single_p_overtop | 0.04019 | 0.01809 | -1.221 | 0.524 | 0.526 |
| single_class_depth | 0.02668 | 0.01809 | -0.4742 | 0.282 | 0.282 |
| single_class_overtop | 0.04771 | 0.01809 | -1.6368 | 0.513 | 0.513 |

Reliability (segments): bin: n, mean P, observed frequency

- p_ens_depth: 0.00-0.05: 4585, 0.0, 0.016; 0.95-1.00: 26, 1.0, 0.385
- single_p_depth: 0.00-0.05: 4440, 0.003, 0.013; 0.05-0.25: 84, 0.116, 0.143; 0.25-0.50: 21, 0.354, 0.143; 0.50-0.75: 16, 0.615, 0.0; 0.75-0.95: 8, 0.862, 0.25; 0.95-1.00: 42, 0.988, 0.286
- p_ens_overtop: 0.00-0.05: 4532, 0.0, 0.014; 0.95-1.00: 79, 1.0, 0.278
- single_p_overtop: 0.00-0.05: 4276, 0.003, 0.01; 0.05-0.25: 87, 0.128, 0.092; 0.25-0.50: 46, 0.365, 0.087; 0.50-0.75: 55, 0.638, 0.091; 0.75-0.95: 51, 0.853, 0.118; 0.95-1.00: 96, 0.991, 0.208

Files: ensemble.json (everything above + site table), ens_segments.geojson (p_ens, p_ens_overtop, p_mean, p_single, depth 5/50/95 %).

Caveats: one storm-wide rain multiplier per member (no spatial rain error); 12 members resolve P_ens in steps of 1/12 and the 5-95 % band is close to the member min-max; parameters sampled independently; model-structure error (DEM, channel burn, 2-D solver) is not sampled.
