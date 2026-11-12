# Model + stream crossings: pre-registration (11 Nov 2026)

Committed before the candidate is fitted or scored. Results go to `CROSSING_v3.md` whatever they are.

## Why
In Leominster, 17 of 54 DPW damage points are within 30 m of an inventoried stream crossing, against 1.9 % of the city's road length
(`phase1/LEOMINSTER_MISSES.md`, amendment 1; seen before this file, which is why the test is on other storms only).

## Candidate (fixed now)
X = logistic regression on the **Leominster sep2023 complete domain only**, inputs: the model's p_close and a 0/1 flag "an inventoried
stream crossing within 30 m of the segment" (`docs/network/crossings_all.json`: UMass stream crossings, MassDOT, NBI bridges; distance =
nearest crossing to any of the segment's road points). Unregularised (C = 1e6). Frozen. Ranking by X's probability; yes/no flag = top 3 %.
Also reported, not decided on: the crossing flag alone as a baseline (score = flag, ties random).

## Test and decision (as PREREG_HYBRID.md)
`proto/bench_v3.py`, PROTOCOL_v3 rules. Adopt X as the ranking only if on Test 2 (81 District 4–6 storms) the 95 % storm-bootstrap interval
of X − M for site recall at 3 % is above 0, and on Test 1 (23 District 3 storms) the point estimate of X − M is not below −0.03.
