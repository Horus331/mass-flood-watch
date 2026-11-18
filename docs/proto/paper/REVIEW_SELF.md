# Paper 1: self-review as a hostile reviewer (18 Nov 2026)

Read of `MANUSCRIPT.md` as a reviewer for a hydrology / natural-hazards journal (e.g. J. Hydrology, NHESS, J. Infrastructure Systems).
"Fixed" = changed in the manuscript the same day using numbers already in the repo (no new runs, no tuning). "Open" = needs work or a decision.

## Major

| # | Reviewer point | Status |
|---|---|---|
| M1 | §5.1 claimed the model beats *every* named alternative in District 3, but Table 4 has the traffic-weighted static score ahead (0.32 vs 0.20). | **Fixed**: "better than all but a traffic-weighted static score in District 3". Abstract no longer says the static score "is not worse"; it gives 32 % and "not significant". |
| M2 | The forecast-ensemble result (abstract, §4.6, Table 8) has no uncertainty, on only 7 storms. | **Fixed**: storm bootstrap added (`proto/ensemble_ci.py`, `forecast/ensemble_ci.json`, `ENSEMBLE_PARITY.md` §4b): gain +0.07 [+0.02, +0.14] long, +0.16 [+0.03, +0.31] short. Also stated that at long lead the gain comes with proportionally more flags (lift 6.1 → 5.5). |
| M3 | §4.4 called the watch-tier model "the best" (26 of 90) but the cascade two-tier model has 33 of 98; different label rounds mixed without saying so. | **Fixed**: both given with their label base (first round 90 sites, rule 15; second round 98 sites, rule 20). |
| M4 | The consequence numbers (abstract, §4.5, §5.4) come from the calibration storm and are not validated. | **Fixed (wording)**: §4.5 now says calibration storm, illustrative, no observations to check against. **Fixed**: held-out Sept 2021 District run (plan fixed first): 97.5 % of the residents losing access are on dry roads (rule ≥ 80 %), so the claim holds on two storms; abstract, §4.5, §5.4, Table 7 updated (`turing/d3_sep2021_t2_RESULT.md`). |
| M5 | The closure threshold 0.30 m and spread 0.10 m are untested. A reviewer will ask how sensitive the results are. | **Answered**: all ranked metrics are invariant to both constants (`proto/score_v2.py` ranks by p_close, ties by peak depth; p_close = Φ((d − T)/σ) only, see M9), so the ranking is the depth order for any T, σ. Only the fixed rule's flags depend on them, and recall at other flag shares (1–10 %) already shows that trade-off. Stated in Limitations. |
| M6 | Spatial skill (FSS 300 m) is at or below chance in Districts 4–6; the reviewer may argue the ranking skill is "which storms/towns", not "which roads". | **Answered from existing results** (no new computation): the protocol already scores a "towns" domain = only the towns with a matched report in each storm (an oracle that knows which towns flooded). Top 3 % inside those towns: Districts 4–6 recall 0.195, lift 2.28 [90 % CI 1.81, 2.77]; District 3 held-out 0.204, lift 3.10 [1.67, 4.52] (`score_d456.json` on `transfer-d456`, `obs/round2/score_round2.json`). So the model picks roads within towns, not only towns. Added to §4.3. |
| M7 | π was adopted after looking at the Districts 4–6 result, and the same 81 storms are then quoted as π's out-of-sample skill. | **Partly answered**: the adoption rule was pre-registered (`PREREG_PI_RANK.md`), and Districts 4–6 were never in π's fit. Wording should say "pre-registered single comparison" in §4.3. **Open**: the five locked storms are the clean test (Mo decides when). |
| M9 | §3.2 said three further terms (freeboard, culvert overtopping, fast water) raise P. In every evaluated run P equals the depth term alone (checked: p_close = p_depth in all 26 District 3 feature files; the switches default off and no workflow sets them). | **Fixed**: §3.2 now says they are computed as separate layers and are not part of P in any reported result. The site model tree already says "candidate layer (opt-in, not in p_close)". |
| M10 | Figures repeated two text errors: Fig 2 showed freeboard / culvert / fast-water terms inside P (as §3.2 did), and Fig 6 showed π at 0.34 in District 3 without saying that π was fitted on those storms. | **Fixed**: Fig 2 redrawn ("separate layers"); Fig 6's District 3 π bar hatched and labelled "in its fit, reported only". Captions for Figs 1–8 written. |
| M8 | Light-storm under-prediction (8 of 9 gauges negative bias) undermines a physics claim. | **Quantified** (`parity/BIAS_BY_STORM.md`): bias negative on 22 of 24 storms; modelled/observed rise 0.15 below 60 mm vs 0.56 above; top-3 % recall 0.06 vs 0.33; added to §5.1 ("a large-storm skill"). A physics fix (rain excess on small storms) would need a pre-registered test; T4 C stays stopped. |

## Minor

| # | Point | Status |
|---|---|---|
| m1 | π gain quoted from 0.206 while the transfer recall is 0.210 (two scorings). | **Fixed**: §4.3 says which scoring gives 0.206. |
| m2 | OSM control "loses 2 of 14 sites" did not say it was two District 3 storms. | **Fixed**, and noted that the Districts 4–6 lift is therefore likely conservative. |
| m3 | Mixed 90 % (protocol, Table 5) and 95 % intervals (benchmark, π, ensemble). | **Fixed**: §3.4 states which metrics carry which level; every interval in the text is labelled. |
| m4 | "Any of 4" has a higher recall than the operational "2 of 8" in Table 8. | **Fixed**: §4.6 says 2 of 8 was chosen in the first out-of-sample test (`ENSEMBLE.md` §4: same recall as any of 4, fewer flags, higher lift) and only re-tested here. |
| m5 | "Tests of antecedent moisture are not finished" (Limitations). | **Fixed**: now "tested only as a sensitivity on the calibration storm". |
| m6 | `<!-- src: -->` comments and `R#` references must become a journal reference list. | Open (before submission). |
| m7 | Figures and tables called out in order? | **Fixed**: only Figs 7–8 and Tables 2, 4, 6 were cited; all 8 figures and 8 tables are now called out, first mentions in order (Fig 1, Table 1, Table 2, Fig 2–4, Table 3, Fig 5, Table 4, Fig 6, Tables 5–6, Fig 7, Table 7, Fig 8, Table 8). Fig 7's map legend says 135 closed vs 134 in the run summary: one segment at 0.2999 m rounds to p = 0.500 in the GeoJSON; harmless, note in the caption. |
| m9 | §4.5 "127 closed" vs the run report's 134 (and groundwater SCOUT §6). | **Fixed**: 127 = half-hourly series used for the cascade; 134 = each segment's own peak depth. Both stated. |
| m8 | 52,698 segments vs "about 49,000" in older documents. | Manuscript is consistent (52,698); older poster not published. |

## Next
All review points that can be fixed from existing numbers are done. Remaining open: M7 (locked storms, Mo), M8 (antecedent moisture; T4 C stopped), m6–m7 (submission formatting).
