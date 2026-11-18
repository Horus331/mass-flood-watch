# District 3 run of the September 2021 storm (Ida remnants) on the T2 terrain: result (18 Nov 2026)

Plan fixed before the run: `d3_sep2021_t2_PLAN.md`. Turing queue `d3t2_sep2021_solve` (Slurm 2535698, 30 min on GPU) and
`d3t2_sep2021_post` (2535699, CPU). Output `docs/proto/turing/d3_sep2021_t2/` (`cascade.json`, `summary.json`, `REPORT.md`). Settings
identical to `d3_sep2023_t2`. Reporting only; no setting changed.

| Plan item | Sept 2021 (held-out) | Sept 2023 (calibration storm, for comparison) |
|---|---|---|
| 1. Segments closed at some time (half-hourly series / own peak) | 372 / 371 | 127 / 134 |
| 1. Closed at the peak, and when | 252 at 14.5 h | 70 at 8.0 h |
| 2. Delay at the peak (vehicle-hours per hour) | 35,708 | 7,379 |
| 2. Delay over 48 h (vehicle-hours; detours / slowed) | 383,477 (128,648 / 254,830) | 119,739 (63,160 / 56,579) |
| 3. Residents losing timely access at the peak (any service) | 355,938 | 76,450 |
| 3. … hospital / fire station / police | 69,971 / 233,689 / 221,041 | 26,518 / 45,686 / 38,617 |
| 3. Residents cut off from every service at the peak | 27,216 | 7,886 |
| 3. Of those losing access, on roads that stay dry | 347,181 (97.5 %) | 75,700 (99.0 %) |
| 3. Share of lost-access person-hours on dry roads | 97.4 % | 97.7 % |
| 4. Segments closed before the rain starts | 0 (first closure at 2.0 h) | 1 (at 0.5 h) |
| 5. Storm labels (Worcester catalogue list, 8 matched): hit by the rule / in the top 3 % | 5 / 5 (rule flags 0.82 % of segments) | — |

**Reading (rule fixed in the plan):** the dry-road share is 97.5 % (≥ 80 %), so the claim that consequences fall mostly on people whose own
road stays dry **holds on a second, held-out storm**. Both storms go in the paper.

**Caveats.** The Sept 2021 storm is less intense than Sept 2023 (heaviest hour in the run report 24.5 mm vs 102 mm) but closes 3× as many
segments and cuts off 4.7× as many residents, so its rain fell over much more of the District's road network. As for Sept 2023: no storm drains (long
closures are an upper bound), single shortest-path detours, flat daily traffic, night-time population, nothing to validate the
consequences against. The model under-predicts this storm at the gauges (e.g. Quinapoxet River rise 0.72 m vs 1.55 m observed; Gates Brook
0 vs 0.77 m), consistent with the paper's light-storm bias. Labels for this storm cover only the Worcester catalogue box (8 matched), so
item 5 is indicative only.
