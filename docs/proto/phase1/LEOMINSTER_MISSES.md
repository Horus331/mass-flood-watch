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

## Results
(below, added after the run)
