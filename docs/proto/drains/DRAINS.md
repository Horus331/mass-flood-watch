# Storm-drain capacity test: Leominster pipe network vs no drains vs generic design drains

Run 23 Oct 2026 on GitHub Actions (CPU, 4 cores), `.github/workflows/drains_test.yml`, run 39941324115, the Actions version of
`proto/turing/run_drains.slurm`. Box 168000,908000,188000,928000 (EPSG:26986) at 20 m, `LF_LOSS=cn LF_CN_SCALE=0.91 LF_INFIL_MMH=2
LF_INFIL_MODE=solver LF_QOUT=1`, LISFLOOD-FP 8.2 with the `mfw-drains` infilfile patch (sink probe volume ratio 1.00 in every drains / design run).

- **base**: no drains.
- **drains**: `LF_DRAINS` = City of Leominster DPW pipe network (`proto/data/drains/leominster_drain_pipe.zip`). 11,911 pipes, 1,359 networks.
  Full-flow capacity 3,706 m3/s, 1,072 m3/s after the network cap and 440 m3/s after the 0.1 m3/s per-cell inlet cap, on 13,492 cells.
  Zero sink outside the city.
- **design**: `LF_DRAIN_DESIGN=1`, the generic fallback (0.5 x 43 mm/h x impervious fraction) on 241,082 developed cells across the whole box (320 m3/s).

Per-run aggregate json is in `docs/proto/drains/<storm>_<case>/`, and the comparison is in `drains.json` (`python proto/drains_eval.py compare`).
"City" means road segments whose MassDOT town is Leominster (1,544 segments in the box), which is the area the pipe network covers.

## Results inside the City of Leominster (the fair comparison)

| | Sep 2023 base | drains | design | Aug 2026 base | drains | design |
|---|---|---|---|---|---|---|
| segments flagged (p_close >= 0.5) | 62 (4.0 %) | **40 (2.6 %)** | 54 (3.5 %) | 28 (1.8 %) | **19 (1.2 %)** | 14 (0.9 %) |
| may-close segments | 142 | 92 | 132 | 54 | 30 | 24 |
| road points wet >= 10 / 30 cm | 3.3 / 1.05 % | 1.8 / 0.57 % | 2.9 / 0.81 % | 1.06 / 0.37 % | 0.56 / 0.26 % | 0.72 / 0.24 % |
| news/LSR labels caught (strict 30 m) | **35 / 82** | 29 / 82 | 33 / 82 | **1 / 1** | 0 / 1 | 0 / 1 |
| lift (vs random at the same flagged share) | 7.0 | 8.9 | 7.6 | 27.8 | 0 | 0 |
| DPW damage points caught (strict) | 21 / 54 | 21 / 54 | 21 / 54 | n/a | n/a | n/a |
| observed points hit >= 30 cm (city) | 0.86 | 0.79 | 0.85 | 2 pts: 1.0 | 0.5 | 0.5 |
| DPW points hit >= 30 cm | 0.69 | 0.67 | 0.67 | n/a | n/a | n/a |

**Equal flag budget** (city segments ranked by peak road depth, top k flagged; news labels / DPW points caught):

| k | base | drains | design |
|---|---|---|---|
| Sep 2023, k = 62 (base budget) | **37** / 24 | 35 / 24 | **37** / 24 |
| Sep 2023, k = 54 (design budget) | **37** / 24 | 33 / 24 | 35 / 24 |
| Sep 2023, k = 40 (drains budget) | **33** / 24 | 31 / 24 | **33** / 24 |
| Aug 2026, k = 28 / 19 / 14 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 |

## Box-wide numbers

| | Sep 2023 base | drains | design | Aug 2026 base | drains | design |
|---|---|---|---|---|---|---|
| flagged share (box) | 2.22 % | 1.79 % | 1.72 % | 1.54 % | 1.33 % | 0.66 % |
| labels recall / lift (box, strict) | 0.393 / 11.4 | 0.326 / 11.7 | 0.371 / 13.9 | 0.25 / 9.3 | 0 / 0 | 0 / 0 |
| peak wet area km2 | 22.2 | 19.7 | 17.6 | 12.2 | 11.4 | 7.7 |
| gauge rise error 01094400 / 01094500 (m) | -0.03 / +0.32 | -0.03 / -0.21 | -0.27 / +0.08 | -0.06 / +0.14 | -0.06 / -0.13 | -0.38 / -0.66 |
| mean gauge rise bias (m) | +0.15 | -0.12 | -0.10 | +0.04 | -0.10 | -0.52 |
| volume removed vs base (m3) | | 1.63 M | 3.38 M | | 0.45 M | 1.59 M |
| share of box rain excess | | 10.4 % | 21.5 % | | 6.0 % | 21.4 % |
| as depth over the city (77 km2) | | 21 mm | (box-wide) | | 6 mm | (box-wide) |

The volume removed is the base run's net source minus the case's (the last `Rain-(Inf+Evap)` value in `lisflood.mass`). Cells the drains dry out
take in less of the 2 mm/h scalar infiltration, so this is a lower bound on what the pipes took. Box rain excess was 15.7 M m3 (39 mm mean) in
Sep 2023 and 7.4 M m3 (19 mm mean) in Aug 2026.

## What the test shows

1. **Drains do reduce flags in the city, on both storms.** City flags fell 35 % in Sep 2023 and 32 % in Aug 2026, and wet road points fell about
   45 %. The 1:1 pipe sink takes about 10 % of the box rain excess in Sep 2023. That is about 21 mm over the city.
2. **The expectation was only half right.** Drains did not "matter little" in the extreme Sep 2023 storm. They changed the city flags as much
   as on the moderate Aug 2026 storm. With a peak-hour rate of 89 mm/h, the pipes are overwhelmed where it matters, but they still empty
   thousands of street cells that the base run keeps ponded.
3. **The flags that were removed were not mostly false alarms.** In Sep 2023 the drains run lost 6 of 35 caught city labels. All 6 are
   standing-water types (closed, flooded, impassable, sinkhole). In Aug 2026 it lost the only city label, the Lancaster St / West St car
   stuck in street flooding (0.31 m becomes 0.25 m on the road). At an equal flag budget, base catches as many sites as drains or more:
   33 vs 31 at k = 40, and 37 vs 35 at k = 62. Higher lift with drains comes only from flagging fewer segments. The sink acts like a higher
   depth threshold, not a better ranking. Where a street really flooded, the real inlets were overwhelmed (clogging, surcharge, tailwater),
   and the model's capacity is an upper bound: inlet efficiency 1.0, no backwater.
4. **The DPW damage points did not change** (21 / 54 in every case; 19 / 50 edge and road washouts). Those are flowing-water damage, and
   pipes taking ponded water do not change them.
5. **Gauges:** the drained water is not put back at the outfalls. The North Nashua near Leominster (01094500) therefore swings from
   +0.32 m to -0.21 m in Sep 2023, and from +0.14 m to -0.13 m in Aug 2026. Absolute error is similar, but the bias flips to low.
   The design fallback across the whole box removes about 21 % of rain excess and under-predicts the Aug 2026 rises by 0.4 to 0.7 m.
6. **Design fallback:** in Sep 2023 it is closer to base in the city (33 / 82 labels, 54 flags). In Aug 2026 it removes too much water
   box-wide. It is not a substitute for the pipe data, and it should stay off.

## Verdict

**No. Keep storm drains off by default, including inside the network area.** On the two storms tested, the Leominster pipe sink cuts city flags
by about a third. It removes documented flood sites in proportion, does not improve the ranking at an equal flag budget, does not change the DPW
damage hits, and biases the downstream gauge low. Fewer flags with drains on is not the same as fewer false alarms here.

Keep it as an opt-in sensitivity layer: `LF_DRAINS` gives a "drains working" lower bound. The test does not show that the sink is useless.
It shows that the sink as built (full-flow capacity, inlets 100 % efficient, no outfall return) is too generous. Changes worth testing before
revisiting the default:

- inlet efficiency / clogging (`LF_DRAIN_EFF` 0.5 on the pipe sink too);
- returning the drained volume at the outfalls (as point inflows), which fixes the gauge bias;
- a storm with more than one labelled city site that is not an extreme event. Aug 2026 has a single city label, so the moderate-storm side
  of the question rests on n = 1.

Caveats: two storms, one city; labels are documented impacts (no negative labels), so "false alarm" is judged by flag counts and wet road share
and not by confirmed dry roads; segment ranking uses peak depth and not `p_close` (ties).
