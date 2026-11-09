# Radar nowcast in the first hours, and chance of flooding by time window: pre-registration (9 Nov 2026)

Items 3 and 14 of `docs/proto/IMPROVE_20.md`. Committed before any of the runs below. Results go to `NOWCAST_WINDOWS.md` whatever they are.

## A. Radar nowcast blended into the forecast rain (0-3 h)

Why: on the 5-7 Nov storm the HRRR rain was about twice the radar rain in the north and too intense in the south (`prospective/storm_2026-11-06_watch.md`).
The first hours after a cycle are where radar extrapolation is known to beat a model (Germann & Zawadzki 2002; Pulkkinen et al. 2019,
pysteps). `proto/live_feeds.py nowcast` already makes a 0-2 h advection nowcast for display only (0-1 h beat persistence in 3 of 4 cases).

Candidate (fixed now): forecast member rain = MRMS PrecipRate frames advected (pysteps Lucas-Kanade + semi-Lagrangian, no growth/decay) for
lead 0-1 h, linear blend radar -> HRRR over 1-3 h (weight on radar 1 at 1 h, 0 at 3 h), HRRR from 3 h. Same 1 km totals preserved as
the advection gives them; no rescaling.

Hindcast set: every forecast cycle in the storm archive with MRMS truth (`docs/proto/archive`), plus the HRRR cycles of the 9 T2 replay storms
where HRRR is on AWS (cycles every 3 h from 6 h before to 3 h after the storm's peak hour). Locked storms are not used.

Checks (all must pass to adopt for live members):
1. Rain, 0-3 h lead, box-mean hourly mm vs MRMS: mean absolute error of the blend at most 0.85 x HRRR's (pooled over cycles), and not worse
   than HRRR in more than 1/3 of cycles.
2. Rain, 3-6 h lead: within ±5 % of HRRR's error (the blend must not harm what follows).
3. Flood outcome (k-of-8 closures on a box run with each rain) vs the radar-rain run of the same box and window: segment-level F1 of the blend
   ≥ HRRR's - 0.02 pooled.

## B. Chance of flooding within 1 h, 6 h and 24 h

Candidate (fixed now): for a road with calibrated chance π (LIVE_PI.md) and members m = 1..n, P(within W) = π x (members whose closure on
that road starts within W of issue) / (members that close it at all); roads no member closes get π x (share of members whose peak depth on
the road is reached within W). Shown as three numbers on the road row ("1 h · 6 h · 24 h").

Checks (on the archived forecast cycles and the T2 replay storms re-run as hindcasts):
4. Ordering: P(1 h) ≤ P(6 h) ≤ P(24 h) ≤ π for every road (by construction; checked in code).
5. Timing: for report sites with a report time, the share whose report falls inside the window where P(W) first exceeds half of π is at
   least 0.5 pooled. With fewer than 15 timed report sites in the set the result is reported as "too few to judge" and B is not shown.

Adopt A if 1-3 pass; adopt B if 4-5 pass. Either can pass alone.
