# Proposed changes after the 6 Nov 2026 storm (pre-registered, not adopted)

Written 7 Nov 2026 before any of these were tested. None changes the live forecast until it passes the tests below and Mo and the
advisors approve it. Evidence: `storm_2026-11-06_watch.md`, sections of 7 Nov.

## P1. Closure needs water the storm added ("rise rule")

**Problem.** In the radar-driven rerun of box b4, 8 of the 11 closed segments reach 30 cm within 0.5 h, before the storm's rain: the water
was already beside the road at the start of the run (streams, ponds). The same roads appear in the forecasts (for example the Route 290 /
Solomon Pond Road ramps, "up to 27 cm at Fri 5:00 AM", the first frame).

**Change.** A segment counts as closed only where depth >= 30 cm AND depth minus its depth at rain onset >= 30 cm, at the same frame.
(v2 already measures depth from rain onset in the probability; this applies the same to the closure rule and to the k-of-8 count.)

**Test.** All archived storms with labels (`docs/proto/forecast/ensemble.json` storms and the 23 district T2 storms): site recall (score_v2)
and flagged share, current rule vs rise rule. Adopt only if pooled recall does not drop by more than 1 site and flagged share falls.

## P2. Rain agreement before "likely" (location-agreement check)

**Problem.** Most "likely" roads in this storm were closed by exactly 2 of 8 members, and the place of the heavy rain moved every cycle.
A stricter k (3 of 8) costs 2 of 29 past sites at long lead (7 Nov analysis), so k alone is not the fix.

**Change.** "Likely" requires k >= 2 AND at least 3 of the 8 members put >= 70 % of the box's heaviest 6 h rain within 10 km of the road.
Otherwise the road is shown as "possible".

**Test.** Needs each member's 6 h rain maximum per cycle. Step 1 (safe, no model change): archive per-member 6 h rain fields (coarse,
1 km) with each cycle. Step 2: evaluate on this storm and on hindcasts of the 7 out-of-sample storms. Adopt only if no past site is lost.

## P3. Radar boxes follow the forecasts (done, operations only)

The storm archive's radar reruns used the first 4 forecast boxes; the Worcester box of the 6 Nov 06Z forecast (22 likely) had no rerun.
Cap raised to 8 on 7 Nov. Further proposal: choose boxes by the number of likely closures they held in any cycle, not first come.

## P4. Worcester hot spots: get evidence before changing the model

East Park Terrace, Shrewsbury Street, Cambridge Street and Fantasia Drive close in the model with 66 mm over 48 h and 16 mm in the worst
hour. No report this storm. Before any model change: request Worcester DPW / 311 street-flooding records for these streets, and check
MassDOT cameras near Shrewsbury Street during the next storm. If they do flood, keep them; if not, they become the test set for a
drainage term (the earlier drain experiments are in `docs/proto/drains`).
