# Paper 2 RQ1: road-edge stream-power index vs Leominster damage, result (20 Nov 2026)

Index computed as fixed in `RQ1_INDEX_SPEC.md` (GitHub run 44734954765: 9 tiles, 1 m 3DEP, no missing elevation after retries of
two 502/504 service errors; 712 of 716 Leominster segments, 540,000 edge points; 16 min). Evaluated once with `proto/rq1_eval.py`, exactly as
frozen in `PREREG_RQ1.md` (frozen before the index existed). Numbers: `edge_spi_leominster.json`, `rq1_eval.json`.

## Pre-registered result
| | AUC of `spi_max` [95 %] | Adding SPI to depth + traffic (LR test p; AUC before → after) |
|---|---|---|
| **Damaged segments (21 of 712)** | **0.85 [0.78, 0.92]** | p = 0.0001; 0.90 → 0.92 |
| Washout segments only (17) | 0.86 [0.77, 0.93] | p = 0.0001; 0.89 → 0.93 |
| Without Wachusett St (17) | 0.84 [0.75, 0.92] | p = 0.0007 |
| `spi_p90` instead of max | 0.80 [0.72, 0.87] | p = 0.0008 |
| Edge length above the 95th percentile | 0.86 [0.77, 0.93] | p = 0.0001 |

Washout segments the deployed closure rule missed: **5 of 8 in the top 10 % by SPI** (chance 10 %).

**Verdict by the frozen rules: promising** (AUC ≥ 0.70 with the interval above 0.5; p < 0.05 over depth + traffic; misses 6× chance).

## Post-hoc checks (not pre-registered; reported because a reviewer would ask)
- **Segment length.** Longer segments have more edge points, so their maximum is higher (rank correlation SPI–length 0.65), and length
  alone separates damaged segments almost as well (AUC 0.87): a long segment is simply more likely to contain one of 54 damage points.
- **Stream crossings.** 18 of the 21 damaged segments are within 60 m of a road–stream crossing, and crossing proximity alone gives AUC
  0.83. The largest SPI values are where an edge point sits on a stream at a crossing (top values ~1 km² of upslope area).
- **Still adds something.** With depth, traffic, log length and distance to the nearest crossing all in the model, adding SPI still improves
  it (LR test p = 0.016; AUC 0.937 → 0.941). Among segments near crossings, SPI separates damaged ones with AUC 0.74 (18 of 155).

## Reading
The index carries real information about where the Sept 2023 damage happened, beyond the flood depth the model already gives, and it
survives the obvious confounds, but much of its raw AUC is length and crossings. This is one storm, in-sample, 21 damaged segments.
A fair next version would (1) be pre-registered with length handled (SPI per segment as a rate, or matched on length) and crossing cells
separated from curb-line cells, and (2) be tested on a second damage inventory (the MEMA / FEMA Public Assistance Category C request).
Nothing changes in the live model.
