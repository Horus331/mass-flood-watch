# Network resilience, warning priority and risk matrix (Sept 2023 Leominster storm)

These three outputs answer three questions the advisors asked. How much of the road network's function was lost, and for how long (a quantitative version of Bruneau's 4R)? Which closures give the least warning? What would the damage cost, and which segments and crossings carry the most risk? All three run after `proto/prototype.py` on its outputs. None of them changes `p_close`.

| file in `docs/proto/leominster_sep2023/` | made by | what it holds |
|---|---|---|
| `resilience.json`, `resilience.png`, `resilience_segments.csv` | `proto/resilience.py` | Q(t) per variant, resilience metrics, access, vehicle-hours of delay |
| `warning_priority.csv`, `rating.json` | `proto/rating.py` | flash-flood index, warning priority and tier per segment, gauge flashiness |
| `risk_matrix.csv`, `risk_matrix.png`, `risk.json` | `proto/risk.py` | top 50 items in the likelihood × consequence matrix, unit costs, totals |

The workflow `.github/workflows/proto.yml` runs all three after every prototype run. The Leominster numbers below were computed offline from the committed outputs (made 22 Oct 2026). Crossing status came from `docs/proto/exp/fb_base/rundir`. That run has the same hydraulics and the same 168 overtopped and 20 surcharged crossings.

## 1. Quantitative resilience

**Network state every 30 min.** A segment is closed at 30 cm or more of water, the prototype's closure depth. Between 5 and 30 cm it is slowed by the Pregnolato et al. (2017) depth-disruption curve. Travel time is the free-flow time by road class. As a sensitivity check, the efficiency curve is repeated with segments closed at 15 cm, the network cut used in `sim/infra/impacts.py`.

**Functionality Q(t), as % of the dry network. Three variants:**

| variant | definition | why |
|---|---|---|
| Q_eff | global efficiency E(t) / E_dry. E = mean of 1 / (shortest travel time) over all pairs of the 5,183 segments in the box | Latora & Marchiori (2001); used for road networks by Ganin et al. (2017). Measures how well the whole network still moves traffic |
| Q_access | residents within the response standard of an open facility, now / dry, averaged over three services: hospital 30 min (Carr et al. 2009), fire station 8 min (NFPA 1710, full first alarm 480 s), police 10 min (assumption). Residents are 2020 Census block counts (see below) | Critical access, weighted by the people who need it |
| Q_access_km | the same with in-box road-km in place of residents | The earlier proxy, kept for comparison (and the fallback when the census file is missing) |
| Q_traffic | Σ AADT·L·f(t) / Σ AADT·L, where f is the Pregnolato speed ratio (0 when closed) | Serviceability weighted by use (Sun, Bocchini & Davison 2020) |

**Metrics over the 48 h window:**

- RL = ∫(100 − Q) dt: Bruneau et al. (2003) resilience loss, the area of the resilience triangle.
- R = ∫Q dt / (100 T): the normalised index of Cimellaro et al. (2010) and Ouyang et al. (2012).
- Robustness = min Q.
- Rapidity: hours from the minimum back to 90 % and to 95 %, and the mean recovery rate.

| | Q_eff | Q_access (residents) | Q_access_km | Q_traffic | Q_eff, 15 cm cut |
|---|---|---|---|---|---|
| robustness (min Q) | **59.0 %** at 7.0 h | **66.8 %** at 7.0 h | 68.4 % at 7.0 h | **68.3 %** at 9.0 h | 48.5 % at 8.5 h |
| resilience loss RL (%·h, 48 h) | 1,284 | 876 | 937 | 1,061 | 1,520 |
| resilience index R | 0.73 | 0.82 | 0.80 | 0.78 | 0.68 |
| recovery to 90 % / 95 % | not within 48 h | not within 48 h | not within 48 h | not within 48 h | not within 48 h |
| Q at 48 h | 71.9 % | 80.8 % | 79.9 % | 76.4 % | 69.4 % |

**Population.** The box's residents come from the 2020 Census: TIGER/Line tabulation blocks (TABBLOCK20) for Massachusetts, whose attribute table carries POP20 and HOUSING20 (P.L. 94-171 counts) and an internal point per block. The `census` workflow downloads the file and `proto/census_blocks.py` keeps the 88,207 populated MA blocks (7,029,917 people, the 2020 count) in `docs/network/census_blocks_ma.npz` (1.1 MB; Vermont, 17,976 blocks, in `census_blocks_vt.npz`). Each block whose internal point lies in the box is put on the in-box road segment with the nearest road point. The Leominster box holds **120,789 residents** (49,634 housing units) in 1,663 blocks. The median block point is 44 m from its road (90th percentile 176 m). 19 blocks (2,015 people) are more than 500 m from any road and are still assigned to the nearest one. Residents of a segment that is closed count as without coverage.

The three services, by residents (the road-km share in brackets):

| service | within the standard, dry | min share | people losing it at the worst time | person-hours of lost coverage (48 h) | back to 90 % |
|---|---|---|---|---|---|
| hospital, 30 min | 118,684 (98.3 %) | 77.2 % (79.2 %) | **27,037** at 7.5 h | **620,000** | after 33 h |
| fire station, 8 min | 113,543 (94.0 %) | 56.6 % (57.0 %) | **49,317** at 7.0 h | **1,297,000** | not within 48 h |
| police, 10 min | 116,533 (96.5 %) | 66.2 % (67.2 %) | **39,366** at 7.0 h | **1,123,000** | not within 48 h |
| at least one of the three | | | **55,244** at 7.0 h | 1,465,000 | |

Person-hours = ∫ (residents within the standard dry but not now) dt, trapezoid over the 48 h window. At 48 h, 13,000 / 28,000 / 25,000 residents are still outside the hospital / fire / police standard, because ponded depressions keep roads closed.

**Isolated residents** (no route at all to any open hospital, fire station or police station: their own segment is closed, or the part of the open network they are on holds no facility): **22,559 at 7.5 h**, of whom 4,754 live on a flooded segment and the rest are cut off on dry roads; 631,000 person-hours over 48 h. 2,105 of them are already "isolated" on the dry network (blocks on road pieces that the graph does not connect to the rest), so the storm adds about 20,500. 13,224 are still isolated at 48 h.

The population weighting changes Q_access little (min 66.8 % against 68.4 % by road-km): the flooded roads in this box are spread over both dense and sparse areas, so road-km was a fair proxy here. The people numbers are new information: tens of thousands of residents lose fire and police coverage for many hours.

**Delay.** Total delay is about **510,000 vehicle-hours**:

- 368,000 vehicle-hours from detours around closed stretches.
- 143,000 vehicle-hours from slow driving through shallow water.
- About 358,000 vehicle-trips had no detour within 30 min. Each is counted at the 30-min cap.

Closed segments that touch count as one closed stretch, so through traffic is counted once. The largest AADT in a stretch detours from the busiest open entry to the busiest open exit, and the extra time is the wet shortest time minus the dry one on the whole MA graph. There is no traffic assignment (detour roads do not congest) and the daily profile is flat, so this is a lower bound for the closed roads. The I-190 and Route 2 segments in Lancaster and Leominster carry the largest shares.

**Caveat.** About 115 segments are still closed at 48 h. Water ponds in closed depressions of the lidar DEM, and the model has no storm drains beyond 2 mm/h. This is why no variant recovers to 90 %. The recovery times are therefore upper bounds on what the model can show, and RL depends on the window length.

## 2. Warning priority (flash-flood index)

`p_close` stays as it is. A separate score ranks closures by how little warning they give:

- **onset**: the first hour with box-mean MRMS rain ≥ 7.6 mm/h, the AMS Glossary "heavy rain" rate. Here that is hour 4.
- **lead_h**: the time 30 cm arrives on the segment, minus the onset.
- **rise_h**: the time from the first 5 cm to the first 30 cm.
- **flashness_pct**: the share of the storm's rain in its worst hour.
- **intensity_ratio**: peak 1 h / (peak 3 h / 3).
- **Flash-flood index** FFI = mean of three scores: (1 − lead/6 h), (1 − rise/6 h) and flashness/100. The 6 h scale is the NWS flash-flood time scale: flooding within 6 h of the causative rain.
- **warning_priority** = p_close × (0.5 + 0.5 FFI).
- **Tiers**:
  - *warn now*: p ≥ 0.5 and lead ≤ 3 h.
  - *warn*: p ≥ 0.5 and lead ≤ 6 h.
  - *advisory (slow)*: p ≥ 0.5 and lead > 6 h.
  - *watch*: 0.1 ≤ p < 0.5.
  - *wet before heavy rain (check)*: 30 cm before the onset (standing water at t0 or a DEM pit). These segments get lead and rise scores of 0.

**Leominster.** Of the 233 likely closures with a lead time, the median lead is **2.5 h** (10th–90th percentile 1.5–4.5 h), and 97 % close within 6 h of the onset: this is a flash flood. Tiers: 173 warn now, 54 warn, 7 advisory, 158 watch, and 3 wet before the rain. The warning ranking correlates 0.93 with the p_close ranking. It moves fast-onset local streets up. For example, Woodside Avenue in Leominster is 137th by p_close and 1st by warning priority (lead 1.0 h, rise under 30 min).

**Gauges, for context.** These are event Richards-Baker flashiness values, Σ|Δq| / Σq (Baker et al. 2004), on the observed 15-min flow for 10–14 Sep 2023. They are not comparable with the annual daily-mean values in Baker et al. (2004).

| gauge | event RBI, hourly | event RBI, daily | peak / base flow | hours from rain onset to peak |
|---|---|---|---|---|
| 01094500 North Nashua near Leominster | 0.083 | 0.81 | 26.9 | 8.5 |
| 01094400 North Nashua at Fitchburg | 0.062 | 0.68 | 15.2 | 5.25 |

## 3. Repair cost and risk matrix

All numbers are order-of-magnitude, in 2023 US$, given as low–high ranges. The midpoint is the geometric mean. They are not engineer's estimates.

**Pavement, per lane-km, 2 lanes:**

| condition | cost per lane-km | basis |
|---|---|---|
| inundated less than 24 h | $3k–15k | clean-up and inspection (assumption) |
| inundated 24 h or more | $60k–150k | mill and 50 mm overlay. After Katrina, submerged asphalt roads lost strength equal to about 2 in (50 mm) of new asphalt, and rehabilitation was costed at $250k per mile for a 4 in mill and overlay (Gaspard et al. 2007). That study found no significant effect of flood duration, so the 24 h split here is our own assumption. Hot-mix asphalt priced against the MassDOT 2023 liquid-asphalt index of $625–665/t |
| washout | $0.5M–1.4M | applied over 50 m. Triggered within 30 m of an overtopped crossing with p_close ≥ 0.5, or when p_washout ≥ 0.5. Upper end = VTrans 2014 post-Irene armoring, $1.7M per mile, in 2023 $ |

**Crossings.** Replacement is costed at the size the Massachusetts Stream Crossing Standards require (span ≥ 1.2 × bankfull width), from the VTrans 2014 Irene unmet-needs table × CPI-U 2023/2014 = 1.287:

| required span | cost (2023 $) |
|---|---|
| pipe < 1.2 m | $19k–109k |
| box 1.2–1.8 m | $264k–360k |
| box 1.8–3.7 m | $360k–521k |
| short bridge 3.7–7 m | $553k–1.29M |
| bridge > 7 m | $1.29M–2.6M |
| size unknown | $19k–521k |

**User delay.** Vehicle-hours from section 1 × 1.67 persons per vehicle (2017 NHTS) × $18.13 per person-hour. That is the USDOT 2016 VOT for local travel, all purposes, $14.10 in 2015 $, × CPI-U 2023/2015.

**Critical access** (not in $). Residents of the box who lose access within the standard to a hospital, fire station or police (at least one) when the segment alone is closed on the dry network. This is link importance as in Jenelius et al. (2006). The segment's own residents are not counted (they are in `residents_on_segment`); a crossing takes the value of the segment it carries. Road-km lost stays in the CSV for comparison.

**Matrix.** Likelihood is p_close for segments and P(overtop) for crossings, in five bands: L1 < 0.1, L2 0.1–0.3, L3 0.3–0.5, L4 0.5–0.9, L5 ≥ 0.9. Consequence is the higher of two classes:

- the $ class: < 50k, < 250k, < 1M, < 5M, ≥ 5M;
- the access class, by residents losing access: C1 0, C2 1–50, C3 51–500, C4 501–5,000, C5 > 5,000. One decade per class, as for the $ classes, anchored on census geography: 50 is one or two blocks (MA averages 80 residents per populated block), 500 is below a block group (600–3,000 people), 5,000 is about a census tract (1,200–8,000, optimum 4,000). The earlier road-km bands (0, ≤ 2, ≤ 10, ≤ 40, > 40 km) are kept as the fallback and for comparison (`risk_with_km_bands`).

Risk = L × C: Low 1–4, Medium 5–9, High 10–16, Extreme 20–25.

**Leominster.** 658 items were scored: 395 segments with p_close ≥ 0.1 and 263 crossings (overtopped, surcharged, or NAACC culverts with P ≥ 0.1).

| class | segments | crossings | (road-km bands: segments / crossings) |
|---|---|---|---|
| Extreme | 17 | 15 | 12 / 10 |
| High | 146 | 146 | 145 / 157 |
| Medium | 75 | 82 | 92 / 79 |
| Low | 157 | 20 | 146 / 17 |

Moving from road-km to residents changes the class of 85 of the 658 items: 19 High → Extreme, 9 Extreme → High, 11 Medium → High, 10 High → Medium, 11 Low → Medium, 24 Medium → Low, 1 High → Low. Short urban segments that cut off dense blocks move up (Litchfield Street, Union Street and the Decicco Drive crossing in Leominster: under 2.5 km of road but 500–870 residents); long rural roads with few residents move down. 217 items cut someone off; the largest is 1,810 residents.

| total | amount |
|---|---|
| repair, segments | $18M–50M |
| repair, crossings | $15M–104M |
| user delay | $15M (504,000 vehicle-hours) |
| expected cost (Σ p × consequence) | about $68M |

Top of `risk_matrix.csv`:

| # | item | p | consequence (mid, range) | driver |
|---|---|---|---|---|
| 1 | I-190, Lancaster | 1.00 | $1.6M ($1.5–1.8M), 44,000 vehicle-hours | cost (delay) |
| 2 | I-190, Lancaster | 1.00 | $1.1M ($1.05–1.24M) | cost (delay) |
| 3 | I-190, Lancaster | 1.00 | $1.0M ($0.9–1.16M) | cost |
| 4 | Route 12, Leominster | 1.00 | $0.56M; 1,428 residents lose access (13 km) | access |
| 5 | Decicco Drive crossing, Leominster | 1.00 | $0.43M; 623 residents (0.9 km) | access |
| 6–7 | Litchfield Street, Union Street, Leominster | 1.00 | $0.36–0.42M; 515–865 residents (1–2.4 km) | access |
| 8–10 | Lancaster Ave (Lunenburg), Leominster Rd and Catacunemaug Rd (Shirley) | 1.00 | $0.27–0.31M; 524–1,217 residents (14–27 km) | access |

## Caveats

- Likelihood is the physics prior `p_close`, not a calibrated failure probability. Overtopping a crossing does not mean the crossing fails. Its replacement cost is the consequence if it does fail.
- 75 % of local-road AADT values are the 1,000 vpd default. There is no lane count, so 2 lanes are assumed.
- Population is the 2020 Census night-time (residential) count at block internal points, each block on its nearest road segment only. A block with several access roads loses coverage when that one segment closes, and residents of a closed segment count as isolated even if they could stay home safely. Daytime population (workplaces, schools) is not included. Coverage counts residents, not calls for service.
- The 6 h scale, the equal weights in the flash-flood index, and the class bands are transparent choices. None was fitted.

## Sources

- Bruneau M. et al. (2003) Earthquake Spectra 19(4) 733–752.
- Cimellaro, Reinhorn & Bruneau (2010) Engineering Structures 32(11) 3639–3649.
- Ouyang, Dueñas-Osorio & Min (2012) Structural Safety 36–37 23–31.
- Latora & Marchiori (2001) Physical Review Letters 87 198701.
- Ganin et al. (2017) Science Advances 3 e1701079.
- Sun, Bocchini & Davison (2020) Sustainable and Resilient Infrastructure 5(3) 168–199.
- Pregnolato et al. (2017) Transportation Research Part D 55 67–81.
- NFPA 1710 (2020).
- Carr et al. (2009) Annals of Emergency Medicine 54(2) 261–269.
- Baker, Richards, Loftus & Kramer (2004) JAWRA 40(2) 503–522.
- NWS Directive 10-950 and the NWS Glossary (flash flood).
- AMS Glossary of Meteorology (heavy rain).
- USDOT (2016) Revised Departmental Guidance on Valuation of Travel Time, Table 4.
- BLS CPI-U.
- FHWA 2017 NHTS Summary of Travel Trends.
- VTrans (2014) State and Local Highway Unmet Needs (Irene).
- Massachusetts River and Stream Crossing Standards (2011).
- MassDOT 2023 period prices.
- Gaspard et al. (2007) LTRC Technical Assistance Report 07-2TA.
- US Census Bureau (2021) 2020 TIGER/Line Shapefiles, TABBLOCK20 (POP20, HOUSING20, internal points); Census Bureau block group and tract population criteria.
- Jenelius, Petersen & Mattsson (2006) Transportation Research Part A 40(7) 537–560.
