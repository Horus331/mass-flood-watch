# Paper 1: self-review as a hostile reviewer (18 Nov 2026)

Read of `MANUSCRIPT.md` as a reviewer for a hydrology / natural-hazards journal (e.g. J. Hydrology, NHESS, J. Infrastructure Systems).
"Fixed" = changed in the manuscript the same day using numbers already in the repo (no new runs, no tuning). "Open" = needs work or a decision.

## Major

| # | Reviewer point | Status |
|---|---|---|
| M1 | §5.1 claimed the model beats *every* named alternative in District 3, but Table 4 has the traffic-weighted static score ahead (0.32 vs 0.20). | **Fixed**: "better than all but a traffic-weighted static score in District 3". Abstract no longer says the static score "is not worse"; it gives 32 % and "not significant". |
| M2 | The forecast-ensemble result (abstract, §4.6, Table 8) has no uncertainty, on only 7 storms. | **Fixed**: storm bootstrap added (`proto/ensemble_ci.py`, `forecast/ensemble_ci.json`, `ENSEMBLE_PARITY.md` §4b): gain +0.07 [+0.02, +0.14] long, +0.16 [+0.03, +0.31] short. Also stated that at long lead the gain comes with proportionally more flags (lift 6.1 → 5.5). |
| M3 | §4.4 called the watch-tier model "the best" (26 of 90) but the cascade two-tier model has 33 of 98; different label rounds mixed without saying so. | **Fixed**: both given with their label base (first round 90 sites, rule 15; second round 98 sites, rule 20). |
| M4 | The consequence numbers (abstract, §4.5, §5.4) come from the calibration storm and are not validated. | **Fixed (wording)**: §4.5 now says calibration storm, illustrative, no observations to check against. **Open**: a held-out storm (e.g. Aug 2021 District run) would make §5.4's "dry roads" point stronger; needs one Turing run (free; changes no model). |
| M5 | The closure threshold 0.30 m and spread 0.10 m are untested. A reviewer will ask how sensitive the results are. | **Answered**: all ranked metrics are invariant to both constants (`proto/score_v2.py` ranks by p_close, ties by peak depth; p_close = Φ((d − T)/σ) only, see M9), so the ranking is the depth order for any T, σ. Only the fixed rule's flags depend on them, and recall at other flag shares (1–10 %) already shows that trade-off. Stated in Limitations. |
| M6 | Spatial skill (FSS 300 m) is at or below chance in Districts 4–6; the reviewer may argue the ranking skill is "which storms/towns", not "which roads". | **Open**: a within-storm, within-town shuffle baseline (rank segments randomly inside each town that has any report) would answer it. Reporting only. |
| M7 | π was adopted after looking at the Districts 4–6 result, and the same 81 storms are then quoted as π's out-of-sample skill. | **Partly answered**: the adoption rule was pre-registered (`PREREG_PI_RANK.md`), and Districts 4–6 were never in π's fit. Wording should say "pre-registered single comparison" in §4.3. **Open**: the five locked storms are the clean test (Mo decides when). |
| M9 | §3.2 said three further terms (freeboard, culvert overtopping, fast water) raise P. In every evaluated run P equals the depth term alone (checked: p_close = p_depth in all 26 District 3 feature files; the switches default off and no workflow sets them). | **Fixed**: §3.2 now says they are computed as separate layers and are not part of P in any reported result. The site model tree already says "candidate layer (opt-in, not in p_close)". |
| M8 | Light-storm under-prediction (8 of 9 gauges negative bias) undermines a physics claim. | Already in §5.1 and Limitations. **Open**: nothing more without an antecedent-moisture model (T4 C stopped by Mo). |

## Minor

| # | Point | Status |
|---|---|---|
| m1 | π gain quoted from 0.206 while the transfer recall is 0.210 (two scorings). | **Fixed**: §4.3 says which scoring gives 0.206. |
| m2 | OSM control "loses 2 of 14 sites" did not say it was two District 3 storms. | **Fixed**, and noted that the Districts 4–6 lift is therefore likely conservative. |
| m3 | Mixed 90 % (protocol, Table 5) and 95 % intervals (benchmark, π, ensemble). | **Open**: state the level in every table caption; keep 90 % for protocol metrics as pre-registered. |
| m4 | "Any of 4" has a higher recall than the operational "2 of 8" in Table 8. | **Fixed**: §4.6 says 2 of 8 was chosen in the first out-of-sample test (`ENSEMBLE.md` §4: same recall as any of 4, fewer flags, higher lift) and only re-tested here. |
| m5 | "Tests of antecedent moisture are not finished" (Limitations). | **Fixed**: now "tested only as a sensitivity on the calibration storm". |
| m6 | `<!-- src: -->` comments and `R#` references must become a journal reference list. | Open (before submission). |
| m7 | Figure order: Fig 7 cited in §4.5 before Fig 6 appears in the text? | Open: check the figure call-out order on the final layout. |
| m8 | 52,698 segments vs "about 49,000" in older documents. | Manuscript is consistent (52,698); older poster not published. |

## Next (no model change; reporting only)
1. M6 within-town shuffle baseline.
2. m3 wording (interval levels in captions).
