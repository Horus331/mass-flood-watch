# Forecast member rain: neighbourhood percentile, judged on road closures: pre-registration (9 Nov 2026)

Item 1 of `docs/proto/IMPROVE_20.md`. Committed before any run of the arms below.

Background: the live members use `LF_HRRR_NBHD=20,90`, which carries about 1.8 x the radar's rain over District 3 (`DISTRICT_VOLCAL.md`,
14 held-out cycles) and 1.23 x inside each storm's own box; P80 was 0.95 x in the box but was not adopted because the decision was made on
district rain maps (area ≥ 25 mm). Rain maps are not what the site warns about: road closures are. On the 5-7 Nov storm the forecast was a
false alarm with the rain about twice the radar's in the north.

Design: the 17 issue times and the radar-rain truth runs of `NOWCAST_WINDOWS.md` check 3 (same boxes, windows, live model settings,
12 h runs, closures = p_close ≥ 0.5 with the P1 rise rule, no nowcast in any arm). Arms: `p90` (live, 20,90), `p80` (20,80), `raw`
(no neighbourhood), plus the radar-rain truth: all four arms run fresh in one workflow run at the same code (so the rain volume of every arm
is recorded), differing only in the percentile.

Measures (pooled over the 17 issue times): F1 of closures against the radar run; false closures (FP); rain volume ratio inside the box
(forecast / radar, 12 h).

Decision: switch the live members to the arm with the highest F1 only if its F1 is at least F1(p90) + 0.02 and its FP is not higher than
p90's. Otherwise 20,90 stays. Ties go to the live setting. Nothing else is tried after seeing the results without a new pre-registration.
