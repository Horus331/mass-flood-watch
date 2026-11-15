# Leominster, 11 Sep 2023: why "35 of 89" and "21 of 54" are both right (15 Nov 2026)

They count two different label sets with two different matching rules. Both use the same frozen model run (sep2023, Leominster box,
20 m, `LF_PARITY=1`, CN × 0.88) and the same closure rule (p_close ≥ 0.5).

| | **35 of 89** | **21 of 54** |
|---|---|---|
| labels | storm reports: news, NWS/spotter reports, agency posts (`proto/data/labels_sep2023_leominster.csv`, 93 rows, 89 matched to a road segment) | the City of Leominster DPW damage list (54 points, surveyed coordinates) |
| area | the whole Leominster model box (also Fitchburg, Shirley, Lancaster …) | City of Leominster only |
| what a label is | a road reported flooded or closed | a damaged site (edge washout, culvert, pavement, drainage) |
| hit | the reported segment is flagged | a flagged segment within 30 m of the point |
| result | recall 0.39 at 2.2–2.6 % of segments flagged (lift ≈ 10–12) | 0.39 (21 / 54) |
| where | `docs/proto/parity/BASELINE.md`, `recall/RECALL.md` | `docs/proto/phase1/LEOMINSTER_MISSES.md` |

How to say it: *"On the storm it was calibrated on, the model flags about 2 % of roads and those contain about 4 in 10 of the reported
flooded roads (35 of 89) and about 4 in 10 of the city's damage sites (21 of 54). Most damage sites it misses are edge washouts with
almost no ponded water."*

Both are **in-sample** (sep2023 is the calibration storm). The numbers to quote for skill are the held-out ones (`scoring/BENCHMARK_v3.md`,
`scoring/PI_RANK_v3.md`).
