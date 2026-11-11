# Phase 1: why the model missed Leominster's damage sites (11 Sep 2023)

## Rules (fixed 11 Nov 2026, committed before the classification was run)
Script: `proto/leominster_misses.py`. Run: the frozen benchmark run (`parity/catalog/sep2023_leominster_20m`, the model scored in
BENCHMARK_v3). Labels: the 54 DPW damage points (exact surveyed coordinates). Hit = a road segment within 30 m with p_close ≥ 0.5.
Each miss gets one class, the first that applies:

1. **label**: no road segment within 30 m (off the modelled network).
2. **culvert**: DPW type culvert failure, or the note names a headwall or a brook, or a matched segment is ≤ 30 m from a stream.
3. **drainage**: the note names a storm drain or gutter line.
4. **debris**: the note says debris.
5. **flow**: shallow (< 0.30 m) but fast water on the segment, peak speed ≥ 0.5 m/s (bare-soil permissible velocity, FHWA HEC-15):
   erosion by flowing water, which a ponding threshold cannot see.
6. **terrain**: a near miss in depth: 0.15–0.30 m on the segment, or ≥ 0.30 m on a segment 30–60 m away.
7. **unexplained**: little modelled water.

## Results (11 Nov 2026)

Raw: `leominster_misses.json`. 54 damage points: **21 hit, 33 missed**.

**As pre-registered:** 32 misses classed *culvert*, 1 *flow*. **That split is an artefact and should not be quoted.** The culvert class came
almost entirely from the stream-distance clause: every one of the 32 has a "stream" exactly 20 m away, which is the next grid cell. The
model's stream network includes the flow lines water takes along the roads, and 41 % of all Leominster segments are within 30 m of one. The
clause cannot tell a culvert from a gutter. (Rule 2 is withdrawn for future use; the other rules unchanged.)

**What the evidence does show:**
- The model put almost no water on the missed sites: median peak depth **2.4 cm** (90th percentile 15 cm), no time above 15 cm at 28 of
  33. At the hit sites the median is 79 cm.
- 26 of the 33 misses are **edge washouts** (DPW note "edge wash out"); 35 of the 54 points are. 9 of the 35 edge washouts were hit.
- Re-classified without the stream-distance clause (post hoc, for reading only): 31 *flow*, 1 *drainage*, 1 *debris*. But the flow test
  (≥ 0.5 m/s) does not separate either: 63 % of all Leominster segments reach it, because thin sheet flow on a 20 m grid is fast.
- Within Leominster (1,521 segments, 29 with DPW damage), what separates damaged segments from the rest (ROC-AUC): modelled peak depth
  0.87, **traffic (AADT) 0.85**, hours above 15 cm 0.80, peak speed 0.78, edge flag 0.76, unit discharge 0.70; rain 0.60–0.63; the
  model's washout flag 0.50 (no signal).

**Reading.** The dominant missed mechanism is erosion at the road edge by water concentrated in curb lines and gutters. A 20 m grid
cannot hold a gutter (under 1 m wide), and a 30 cm ponding threshold is the wrong failure mode for it: these roads failed by erosion with
little standing water. Busy roads are where curbs, gutters and storm drains concentrate the flow, which is a physical reason (beside
reporting bias) why traffic ranks the damage well even in the DPW's complete inventory.

**Named limitations.** One storm, one city; DPW points are damage, not closures; the city's storm-drain network (provided by the DPW) is
not in the public repository and was not used; classes rest on model output at 20 m.

**Next.** (1) A pre-registered test of model + traffic ranking (`../scoring/PREREG_HYBRID.md`). (2) An edge-erosion indicator from
curb-line flow (drain inlets as sinks, the DPW storm-drain layer) for Phase 2. (3) Fix the culvert evidence: use the MassDOT / UMass
stream-crossing inventory, not the model's flow lines.
