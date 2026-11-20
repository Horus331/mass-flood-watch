# Culvert inspection list, Leominster (Paper 2 RQ3; 20 Nov 2026)

**What this is.** Road–stream crossings where the flood model, rerun for the 11 Sept 2023 storm with the culvert blocked, closes roads
that stay open when the culvert is clear. Built only from existing runs (`phase1/PARAMETRIC_T2.md`, `parametric_t2.json`; T2 terrain,
crest readout). Two blockage scenarios: every culvert fully blocked ("all culverts") and only the smallest third blocked
("smallest-third"). "Robust" = also in the top 10 on the earlier terrain (`phase1/PARAMETRIC.md`). NAACC = North Atlantic Aquatic
Connectivity Collaborative stream-crossing surveys (condition of the structure / of its inlet).

**How to read it.** A high rank means: *if this culvert is blocked during a storm like Sept 2023, these roads are the ones that flood
because of it.* It is not a statement that the culvert is in bad condition: condition data are only partly available, and none of these
scenarios explained the damage the City recorded in 2023 (that was mostly edge washout). Use it to decide where to look first, then
confirm with an inspection.

| # | Crossing (road) | Stream | NAACC condition / inlet | Opening (m) | Roads that close only when blocked (segments within 300 m) | Pool rise if fully blocked | Scenario | Robust to terrain |
|---|---|---|---|---|---|---|---|---|
| 1 | Route 2 (42.5510, -71.7856) | Unknown | OK / Poor | 0.61 × 0.61 | Dewey Street, Ramp-South St To Rt 2 Wb, Route 2 (8) | +0.4 m | smallest-third | yes |
| 2 | Dewey Street (42.5520, -71.7861) | Unknown | OK / Adequate | 0.46 × 0.46 | Dewey Street, Ramp-South St To Rt 2 Wb, Route 2 (8) | +0.4 m | smallest-third, all culverts | yes |
| 3 | Meadow Pond Drive (42.5090, -71.7483) | Unknown | No data / — | — | Meadowbrook Acres (4) | +2.6 m | all culverts | yes |
| 4 | Commercial Street (42.5810, -71.7977) | North Nashua River | Poor / — | — | Boulder Drive, Putnam Street (3) | +4.0 m | all culverts | yes |
| 5 | Commercial St (42.5817, -71.7982) | North Nashua River | None / None | — | Boulder Drive, Putnam Street (3) | +4.0 m | all culverts | yes |
| 6 | Railroad Northwest of Laurel Street (42.5810, -71.7972) | North Nashua River | Unknown / — | — | Boulder Drive, Putnam Street (3) | +3.7 m | all culverts | yes |
| 7 | Putnam Street (42.5810, -71.8000) | North Nashua River | OK / — | — | Boulder Drive, Putnam Street (3) | +2.1 m | all culverts | yes |
| 8 |  (42.5516, -71.7861) |  | None / None | — | Columbia Avenue, Dewey Street, Minneapolis Avenue (3) | +2.0 m | all culverts | yes |
| 9 | Columbia Ave (42.5517, -71.7866) |  | None / None | — | Columbia Avenue, Dewey Street, Minneapolis Avenue (3) | +1.6 m | all culverts | yes |
| 10 | Bathrick Road (42.5580, -71.8846) | unnamed | OK / None | 0.46 × 0.46 | Bathrick Road (1) | +2.1 m | smallest-third | yes |
| 11 | Justice Hill Rd (42.4703, -71.8048) | Rocky Brook | OK / None | 1.07 × 0.64 | Justice Hill Road (1) | +1.1 m | smallest-third | yes |
| 12 |  (42.4712, -71.8049) | Rocky Brook | OK / Adequate | 1.07 × 0.64 | Justice Hill Road (1) | +0.8 m | smallest-third | yes |
| 13 | Beaman Rd (42.4477, -71.7941) | Wilder Brook | Poor / Critical | 0.94 × 0.52 | Tanglewood Road (1) | +0.7 m | smallest-third | yes |
| 14 | Pierce Ave (42.5568, -71.7826) | Unknown | OK / Adequate | 0.61 × 0.61 | Harvard Avenue (1) | +0.6 m | smallest-third | yes |
| 15 | Olin Ave (42.5540, -71.7899) | Unknown | OK / Poor | 1.01 × 0.67 | Route 2 (1) | +0.5 m | smallest-third | yes |
| 16 | Justice Hill Rd (42.4670, -71.7995) | Rocky Brook | OK / Adequate | 0.64 × 0.64 | Justice Hill Road (1) | +0.3 m | smallest-third | yes |
| 17 | State Rte 2, Mass State Hwy, George W Stanton Hwy (42.5513, -71.7853) | Unknown | No data / — | — | Columbia Avenue, Dewey Street, Minneapolis Avenue (3) | +2.0 m | all culverts | no |
| 18 | George W Stanton Hwy, Mass State Hwy, State Rte 2 (42.5514, -71.7856) |  | None / None | — | Columbia Avenue, Dewey Street, Minneapolis Avenue (3) | +2.0 m | all culverts | no |
| 19 | Bathrick Road (42.5550, -71.8945) | Unnamed Trib to Round Meadow Pond | Poor / None | 0.61 × 0.61 | Bathrick Road (1) | +0.1 m | smallest-third | no |

Several rows are neighbouring structures at the same place (rows 1–2 and 8–9, 17–18 at Route 2 / Dewey St / Columbia Ave; rows 4–7 at
Commercial St / Putnam St on the North Nashua River; rows 11, 12, 16 on Rocky Brook at Justice Hill Rd), so the list comes down to
**seven locations**:

1. **Route 2 / Dewey St / Columbia Ave** (small 0.46–0.61 m culverts; inlet rated Poor at one) — up to 8 segments incl. Route 2 and its ramp.
2. **Commercial St / Putnam St / railroad on the North Nashua River** (Commercial St structure rated **Poor**) — pool up to +4 m; Boulder Dr, Putnam St.
3. **Meadow Pond Dr** (no survey) — +2.6 m; Meadowbrook Acres.
4. **Bathrick Rd** (0.46–0.61 m; one structure rated Poor) — Bathrick Rd.
5. **Justice Hill Rd on Rocky Brook** — Justice Hill Rd.
6. **Beaman Rd on Wilder Brook** (structure **Poor**, inlet **Critical**) — Tanglewood Rd.
7. **Pierce Ave / Olin Ave** (inlet Poor at Olin Ave) — Harvard Ave, Route 2.

**Inspection priority suggestion:** first the locations where the model effect and a poor NAACC rating coincide (Beaman Rd, Commercial
St, Route 2 / Dewey St), then the unsurveyed Meadow Pond Dr crossing, then the rest. Condition data from MassDOT / the City would
replace the NAACC ratings where newer.
