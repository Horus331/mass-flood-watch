# C2: storm-drain sink on built-up road cells: pre-registration (13 Nov 2026)

Candidate C2 of `docs/proto/prospective/storm_2026-11-13_watch.md` (fixed 12 Nov, before the storm), made precise here **before any
run**. Nothing below changes after a score has been seen; results go to `C2_ROADS.md` whatever they are. Mo OK'd the run 13 Nov.

## The candidate
The model has no storm drains, so water that inlets take away stands on curbed city streets (first storm: East Park Terrace, Worcester,
in the likely list). C2 removes it at a fixed rate where inlets exist:
- **Where:** road cells (MassDOT segments of `docs/graph_segments.json`, points every 10 m, the same road points the closure scoring
  uses) whose surroundings are built up: **mean NLCD impervious fraction within a 300 m square (150 m each side) ≥ 0.5**. This fixes
  "areas ≥ 50 % impervious" of the watch plan; rural roads (ditches, no inlets) get no sink. Water and channel cells never.
- **Rate:** **25 mm/h** on each such cell, constant, through the patched `infilfile` sink (removed only where water ponds, never below
  zero), the inlet rate of a system sized for about a 2–10-year 1-h storm in central Massachusetts (NOAA Atlas 14: 2-yr ≈ 30 mm,
  10-yr ≈ 45 mm in 1 h). Not scaled by imperviousness or an efficiency.
- Code: `sim/colab/lf_drains.road_design_sink`, env `LF_DRAIN_DESIGN=1 LF_DRAIN_DESIGN_ROADS=1 LF_DRAIN_DESIGN_MMH=25
  LF_DRAIN_IMP_MIN=0.5 LF_DRAIN_IMP_RADIUS_M=150`. One arm, no variants: **k = 1**.

## Runs
Plan `proto/turing/plans/c2_roads_v1.json`: 48 tasks = sep2023 (calibration, report only) + the 23 held-out storms × {base, c2}, the
same storm boxes and hours as the inlet test, with the live physics (CN AMC II × 0.88, parity, infiltration 2 mm/h, notch fix, channel
enforcement). Both arms at one pinned commit on GitHub Actions CPU (`.github/workflows/inlets_test.yml`, the route that worked for the
inlet test; about 26 runner-hours). A technical failure is rerun unchanged; no storm is dropped or re-boxed after a result is seen.

## Decision
Exactly the inlet test's rule (`INLETS_PREREG.md` §5), scored by the same code (`proto/inlets_eval.py --dir docs/proto/drains/c2_roads_v1`,
C2 read as the candidate arm): PROTOCOL v2 §5a ranking route, held-out 23, box-wide, k = 1, 2000 bootstrap replicates; all five hold:
1. pooled site recall at 3 % flagged gains ≥ +0.04; 2. one-sided 5 % lower bound of the gain > 0; 3. FSS at 300 m at 3 % does not drop;
4. no held-out storm with ≥ 3 sites loses > 1 site at 3 %; 5. pooled rule lift ≥ 0.8 × base.
Reported with it: the failure-mode check of `DRAINS.md` (sites removed in proportion to flags), the sink totals, and the 13 Nov storm:
the forecast box replayed on radar rain with and without C2 (closures; nothing flooded that day, so only the false-alarm side).

Known before running: two related sinks were not adopted (generic design drains, `DRAINS.md`; the inlet sink, `INLETS.md`). C2 differs in
placement (built-up road cells only) and rate (constant 25 mm/h).
