# Why the 10 m Leominster run flags ~4x more roads than the 20 m run

Runs: `docs/proto/turing/leominster_sep2023_gpu` (20 m) and `docs/proto/turing/leominster_sep2023_10m` (10 m), Sept 11 2023, LISFLOOD-FP 8.2
GPU, same rain, CN loss and closure rules (depth rule P = Phi((d - 0.30) / 0.10), d = second-highest road point per segment). All numbers come
from the published `segments.geojson` (per-segment `p_depth`, `peak_depth_m`, `hours_over_30cm`, `arrival_h` and the 30-min snapshot series
`d`), `flood_meta.json` (frame wet areas, gauges) and `points.json`.

## 1. What differs

| | 20 m | 10 m |
| --- | --- | --- |
| Segments flagged (p_depth >= 0.5) | 134 (2.6 %) | 552 (10.8 %) |
| Flagged at both / new at 10 m / lost at 10 m | 101 | 101 / 451 / 33 |
| Strict recall / lift (published) | 0.359 / 9.45 | 0.531 / 2.85 |
| Median peak depth on flagged segments | 0.57 m | 2.18 m |
| Median `hours_over_30cm` on flagged segments | 4.0 h | **0.0 h** |
| Median `arrival_h` (first snapshot >= 30 cm) | 6.5 h | **0.5 h** |
| Median length, flagged | 756 m | 388 m (new: 298 m) |
| Class of the 451 new | | 390 local/collector, 57 arterial, 4 highway |
| Flagged with a mapped crossing <= 100 m | 0.75 | 0.66 (new 0.64; all wet 10 m segments 0.37) |
| Wet land at the first snapshot (16:30Z, before the rain) | 0.8 km2 (0.2 km2 >= 0.5 m) | **11.7 km2 (6.5 km2 >= 0.5 m)** |
| Report/label points first >= 30 cm at 16:00-16:30Z (`points.json`) | 22 | 72 |
| Random road points with >= 30 cm within the radius | 0.40 | 0.57 |
| Fitchburg gauge: model peak time / WSE error | 01:30Z / -1.15 m | **16:30Z (t0 + 0.5 h) / +2.87 m** |
| Leominster gauge: model peak timing error | -4.0 h | -10.5 h |

At 20 m the frames stay almost dry until the rain (~21:30Z). In the 10 m frame at 16:30Z, ponds and wetlands along the river corridors are
already full (`frames/f001.png`), and the 10 m deep area holds at 5-6 km2 until 03:00Z.

## 2. Cause: two flood-model artifacts at 10 m that the closure rule reads as storm water

**(a) `hmax` spikes.** `hmax` is the maximum over every solver step. On the 10 m flagged segments it is a median **11.1x** the peak of the
30-min snapshots (20 m: **1.0x**). **295 of the 552** 10 m flags (271 of the 451 new ones) never hold >= 30 cm in any snapshot
(`hours_over_30cm` = 0). At 20 m, only 5 of 134 do. These are single-step spikes of the local-inertial scheme on the finer, steeper grid
(open item A6 in docs/research/ideas.md). These spike-only segments sit a median 65 m from a mapped crossing and are a median 248 m long:
short local streets near streams, not crossings.

**(b) Start-up water.** The 10 m run has about 11 km2 of water on land within 30 min, before any rain. The Fitchburg gauge peaks at t0 + 0.5 h
with no storm rise, 2.9 m above the observed peak. Before 21:00Z, 187 of the 552 10 m flags (136 of the new ones) already have >= 30 cm on the
road; at 20 m, 15 of 134 do. The cause is in the initial condition or DEM conditioning in `sim/colab/w9_lisflood.py`, not in the closure rule. The
published outputs cannot show which resolution-dependent step causes it. These are the candidates to check on the run directory:
- Channel burn `burn = CD * min(CW / RES, 1)` and start depth `0.3 * burn`. The 30 m `channels30` raster is nearest-sampled onto 9 cells per pixel
  at 10 m (2.25 at 20 m). Channels narrower than 10 m therefore get up to 2x the burnt volume and 2x the start water.
- At 10 m `ZMAX10 == Z_RAW` (no sub-cell crest), and embankments that 20 m averaging smoothed keep their full height. More closed basins
  deeper than the 4 m breach cap (`LF_BREACH_MAX`) are kept, and they hold water.
- `initial_tstep 10` (the `write_par` default) gives the start-file water twice the Courant number at dx = 10 m that it has at 20 m.

To check: the `kept_deep` and channel-burn log lines of the two runs, and the volume of `start.wd` at each resolution.

**Not the main cause:**
- *More samples make the second-highest more extreme.* Points are spaced res / 2 at both resolutions (two per crossed cell), so the
  second-highest point is about one cell at both. But that means the "one wet pixel cannot close a road" guard covers 10 m of road at 10 m and
  20 m at 20 m; step 3 of the fix makes it consistent. This cannot explain flags where no snapshot reaches 30 cm.
- *Roadside ditches/curbs:* the crest snap (`PROTO_SNAP_CREST`, on by default at 10 m) already moves points to the local lidar high. A larger
  snap neighbourhood would not remove a spike or start-up water on the crest cell itself.
- *CN loss:* identical at both resolutions (same soils grid, `LF_CN_SCALE` 0.91).

## 3. Fix: `PROTO_RES_CONSISTENT=1` in proto/prototype.py (default OFF; default path unchanged, `--selftest` passes)

1. **Snapshot-confirmed depth:** `H' = min(hmax, snapshot peak + 0.10 m)` (`frames_cm.npz` / `hsnap.npy`; `RC_TOL_M`). A flash peak between
   snapshots still counts; a single-step spike does not.
2. **Start-up water removed:** subtract the depth at the first saved snapshot at or after 0.5 h (`RC_START_H`). Runs start before the rain.
   `PROTO_RC_STARTUP=0` keeps this water (spike cap and length rule only).
3. **Fixed physical length:** each segment takes its k-th highest road point, with k = 20 m / point spacing (`RC_MIN_LEN_M`): k = 2 at 20 m
   (today's rule), k = 4 at 10 m. So a segment needs >= 0.30 m over at least 20 m of road at any resolution. This applies to every per-point
   rule (depth, freeboard, fast water, edge, and the `d` series).

`H'` replaces `R['H']`, so the network, crossings, freeboard and timing all read the same storm depth. `summary.json` ->
`checks.rules.res_consistent` records the settings, the number of cells capped and the number of cells wet >= 30 cm at start-up.

## 4. Validation from the published data

This is a per-segment emulation. Steps 1-2 are applied to the per-segment `peak_depth_m` and `d` instead of per cell. Step 3 is left out
because it needs the point grid. The strict labels were re-matched to 89 sites. This re-match gives 20 m recall 0.393 and lift 9.8 for the
published rule, against the published 0.359 / 9.45 on 78 sites, so compare rows inside this table, not with the published numbers.

| Rule | 20 m flagged | 20 m recall / lift | 10 m flagged | 10 m recall / lift |
| --- | --- | --- | --- | --- |
| Published (hmax) | 134 (2.6 %) | 0.393 / 9.8 | 552 (10.7 %) | 0.528 / 2.77 |
| Spike cap only: min(hmax, snap + 0.10) | 133 | 0.393 / 9.9 | 278 (5.4 %) | 0.449 / 4.5 |
| Snapshot peak, all frames | 131 | 0.393 / 10.0 | 247 | 0.438 / 4.9 |
| **Spike cap + start-up removed (fix steps 1-2)** | **115 (2.2 %)** | **0.393 / 11.4** | **116 (2.2 %)** | **0.236 / 5.5** |
| Storm-window snapshots only (frames >= 21:30Z) | 130 | 0.393 / 10.1 | 116 | 0.292 / 6.9 |

- With the fix, both resolutions flag the same share (2.2 % and 2.2 %, was 2.6 % and 10.8 %). At 20 m, recall is unchanged and lift
  rises (9.8 -> 11.4): the 19 segments dropped there were start-up water too. Step 3 can only lower the 10 m count further.
- The 10 m recall falls to 0.24. **Half of the 10 m "hits" on documented sites came from the artifacts**: water already there at 30 min, or
  spikes. Without them, the 10 m run has less skill than the 20 m run, which fits its gauge timing (-10.5 h at Leominster). So the 10 m problem
  is upstream in w9, not in the closure rule. The flag makes the flags honest, but it cannot recover a storm response the 10 m run lacks.

## 5. Next steps

- Re-score per cell with the full fix, including the length rule:
  `NAME=leominster_sep2023_10m STORM=sep2023 PROTO_RES_CONSISTENT=1 sbatch --export=ALL proto/turing/reprocess.slurm`.
  Compare `checks.labels_segments.depth_rule` and `checks.rules.res_consistent` with section 4. The same command with
  `NAME=leominster_sep2023_gpu` checks that the 20 m flags change only by start-up water.
- Fix the 10 m start-up in w9 (section 2b) and re-run the 10 m flood. The suspects are the per-resolution start depth, the breach cap and
  `initial_tstep`. Against the spikes, try `LF_THETA=0.7 LF_CFL=0.5` (already used for the basin runs, COMPUTE.md). The fix works when the
  first-snapshot wet area is about 0.8 km2, as at 20 m, and the Fitchburg gauge rises with the storm.
