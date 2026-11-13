# Blocked culverts, version 3: pre-registration (13 Nov 2026)

Committed before any version-3 number is computed. Results go to `BLOCKED_V3.md` whatever they are.

## What the diagnostic showed (already seen; disclosed here)
`diag_r100_normal.json`, `diag_r075_wet.json`, `diag_r125_dry.json` (`proto/whatif_diag.py`, Turing): of the road segments within 60 m
of a blocked crossing that close in one run and not the other, **27 of 30 close only in the open run, and in all 27 the deepest road cell
is an edited cell** (the notch cut through the road for the stream; median 2.3 m below the lidar road). In the blocked runs the notch is
gone, so those segments read 0.2–0.3 m instead of 0.5 m. In all 30, the highest water surface within 40 m is the same or higher in
the blocked run (the pool behind the road). So the version-2 comparison measured the notch, not the flood: in the open run, stream water
standing in the notch is counted as water on the road. (In the live model this cell depth is deliberate: at local crossings it is the
proxy that finds the documented culvert failures, Leominster recall 0.385 vs 0.08 crest-relative, `proto/prototype.py`. It is not changed
here.) Because these 30 were seen, the checks below use **all** blocked crossings and all segments near them, not the 30.

## Version 3 (post-processing only, the existing solves, nothing re-run on GPU)
`proto/whatif_v3.py`, the same readout for the open and the blocked run of a pair:
- **Road depth near crossings, crest-relative.** For each road segment whose mean point is within 60 m of a blocked (non-bridge)
  crossing of `docs/site/data/whatif/culverts.json`: depth at each of its 20 m road cells = max(0, Z + H − crest), crest = lidar
  `z_raw_max10` (else `z_raw`) of the cell; segment depth = second-highest cell (highest if one cell). **Closed: segment depth ≥ 0.30 m.**
- **Pool at each blocked crossing:** highest water surface Z + H (cells with H ≥ 0.05 m) within 40 m whose ground Z is below the crossing
  crest (crest = highest lidar cell within 20 m of the crossing point), i.e. the water on the low side of the road, not hillside runoff.
  **Overtopped:** pool > crest.

## Checks (12 complete pairs of `blocked_v2.json`)
1. **Direction.** Segments closed near blocked crossings: blocked ≥ open in at least 9 of 12 pairs.
2. **Pool (replaces version 2's box-wide wet area).** Per pair, the median over crossings wet in either run of (pool blocked − pool
   open) ≥ 0, in at least 9 of 12 pairs; a crossing wet in only one run counts as a rise (wet only blocked) or a fall (wet only
   open). Replaced because box-wide wet area moves with terrain changes far from the crossings (paired
   closure overlap Jaccard 0.0–0.45); the version-2 wet-area result (4 of 12) stands as reported.
3. Reported, not a check: crossings overtopped, open vs blocked.

## Decision
Both pass → the explorer's culvert switch uses the version-3 readout near crossings, and the value of maintenance is reported as segments
near crossings closed blocked − open, per scenario, with the open-vs-open churn stated. Either fails → the switch stays "not reliable yet".
The live forecast is not touched by this test either way.
