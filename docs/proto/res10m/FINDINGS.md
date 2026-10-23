# Why the 10 m Leominster run flags ~4x more roads than the 20 m run (work in progress)

Preliminary (analysis of the published `docs/proto/turing/leominster_sep2023_{gpu,10m}` outputs):

- 552 segments flagged at 10 m vs 134 at 20 m; 101 in both, 451 new at 10 m, 33 lost.
- 295 of the 552 (271 of the 451 new) never hold >= 30 cm in any 30-min snapshot (`hours_over_30cm` = 0); at 20 m only 5 of 134.
  Median hmax / snapshot-peak ratio on flagged segments: 11.1 at 10 m, 1.0 at 20 m.  The 10 m flags are mostly single-step `hmax` spikes.
- The 10 m run already has 11.7 km2 of wet land (6.5 km2 >= 0.5 m) at the first 30-min snapshot, before the rain; the 20 m run 0.8 / 0.2 km2.

Full write-up and the fix follow.
