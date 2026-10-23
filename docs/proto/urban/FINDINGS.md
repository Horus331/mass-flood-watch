# Why the model misses short, intense urban storms, and a candidate pluvial rule (`PROTO_PLUVIAL`, off by default)

All numbers come from published outputs only (`docs/proto/turing/<storm>_<area>_20m/`). Reproduce with `python proto/pluvial_loso.py` (writes `docs/proto/urban/loso.json`). "Site" = a documented label location with at least one strictly matched segment (30 m), the same unit as `closure_loso.py`. "Flagged" = `p_close >= 0.5`. "Out of sample" (OOS) = the 7 storms not used to build the rules (all but aug2021 and sep2023): 29 sites, of which the default rule catches 5.

## 1. The missed labels

| storm | site | road | depth on segment (m) | max depth within 300 m | nearest flagged segment (m) | peak 1 h (mm) | total (mm) | worst hour % of storm | HAND (m) | upstream area (km2) | road segments within 300 m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| jul2023 | 01 | Main St, Holden | 0.00 | 0.04 | 1042 | 16.0 | 19 | 84 | 0.0 | 0.026 | 17 |
| jul2023 | 02 | S Spencer Rd, E Brookfield | 0.06 | 0.06 | 1190 | 22.0 | 31 | 71 | 1.3 | 0.057 | 1 |
| jul2023 | 03 | Franklin St, Worcester | 0.00 | 0.01 | 1111 | 19.3 | 24 | 82 | 5.0 | 0.041 | 18 |
| jul2023 | 04 | Shrewsbury St, Worcester | 0.02 | 0.10 | 903 | 20.1 | 24 | 82 | 0.0 | 0.304 | 30 |
| jul2023 | 05 | Southbridge St, Worcester | 0.01 | 0.01 | 1180 | 19.0 | 22 | 85 | 0.0 | 0.047 | 10 |
| aug2023b | 01 | Route 146, Millbury | 0.04 | 0.00 | 573 | 34.0 | 49 | 70 | 0.0 | 0.024 | 16 |
| aug2023b | 03 | Providence Rd, Grafton | 0.03 | 0.04 | 1680 | 41.8 | 59 | 70 | 0.0 | 0.088 | 17 |
| sep2022 | 01 | Dresser St, Southbridge | 0.01 | 0.12 | 365 | 35.4 | 49 | 72 | 0.0 | 0.020 | 22 |
| sep2022 | 02 | (unspecified), Oxford | 0.01 | 0.01 | 1583 | 25.2 | 34 | 74 | 0.0 | 0.027 | 10 |
| sep2022 | 03/04 | Worcester Rd, Webster (two labels, one place) | 0.05 | 0.05 | 485 | 74.3 | 98 | 76 | 0.0 | 0.061 | 12 |
| aug2023 | 01 | W Main St, Hopkinton | 0.01 | 0.03 | 4102 | 21.2 | 50 | 42 | 0.0 | 0.047 | 8 |
| aug2023 | 03 | Henry St, Framingham | 0.00 | 0.12 | 644 | 31.4 | 66 | 47 | 1.2 | 0.007 | 16 |
| aug2023 | 04 | Ashland St, Holliston | 0.06 | 0.12 | 596 | 31.5 | 77 | 41 | 0.0 | 0.050 | 10 |
| aug2023 | 02 (hit) | Glen St, Marlborough | 0.39 | 0.39 | 27 | 47.2 | 58 | 81 | 0.0 | 0.025 | 8 |

None of the 13 missed sites is close to a closure: at most 0.06 m of water on the segment and 0.12 m within 300 m; the nearest flagged segment is 0.4–4 km away. `p_sag` is 0 at all 13. The sag layer found 476, 596 and 89 sags in the jul2023, aug2023b and sep2022 boxes, and its rain half fired at none of them in jul2023, aug2023b and aug2023 (`rules.sag.from_rain`).

**Hits in the good storms, for comparison.** Elsa jul2021 (Cambridge St), Ida sep2021 (Southbridge St, Cambridge St) and aug2021 (Route 20, Cambridge St, Southbridge St, Glennie St) are sags the model fills itself: 0.45–1.6 m deep, `p_sag` 0.94–1.0 from model ponding, HAND 0, slope 1.7–5 %. Storm totals were 51–106 mm with the worst hour only 18–48 % of the storm. aug2026 Lancaster St (0.36 m) is an arterial on a stream floor, 77 mm total.

Peak-hour rain at the sites was no higher in the good storms than in the missed ones (Ida 18–19 mm, Elsa 13 mm, aug2021 27–35 mm vs jul2023 16–22 mm). The difference is volume: hits had 50–106 mm totals, misses 19–59 mm (98 mm at Webster) with 70–85 % in one hour.

Across all 9 storms, labelled segments vs all segments in the box: HAND = 0 more often (median share 0.73 vs 0.50), denser street grid (median 16 vs 11 road segments within 300 m), larger upstream area (median 0.02–0.05 vs 0.01 km2).

## 2. Drainage capacity, radar under-catch, or the model's loss?

**(a) The model's runoff loss removes almost all of a short burst on urban ground (main mechanism).** Every run uses `LF_LOSS=cn` with composite CN = IMP·98 + (1−IMP)·CN_pervious, scaled by `LF_CN_SCALE` 0.91 (`w9_lisflood.py`). For HSG C pervious ground (CN 73), AMC II:

| impervious share | CN after ×0.91 | model runoff from 20 / 30 / 45 / 60 / 106 mm | directly connected impervious runoff, IMP·(P − 2 mm) |
|---|---|---|---|
| 0.3 | 73.3 | 0.0 / 1.3 / 5.9 / 12.8 / 42.4 mm | 5.4 / 8.4 / 12.9 / 17.4 / 31.2 mm |
| 0.5 | 77.8 | 0.4 / 2.7 / 9.0 / 17.6 / 51.1 mm | 9.0 / 14.0 / 21.5 / 29.0 / 52.0 mm |
| 0.8 | 84.6 | 2.0 / 6.5 / 15.6 / 26.6 / 65.5 mm | 14.4 / 22.4 / 34.4 / 46.4 / 83.2 mm |

A 20–30 mm storm on a half-paved cell gives 3–20 % of what the pavement alone would shed; a 106 mm storm gives about 100 %. That is why Ida and Elsa sags fill in the model and July 2023 sags do not. The cause is upstream of `prototype.py`.

**(b) Missing storm drains are not why the model misses.** Leaving drains out makes the model too wet. Drain capacity is the real-world mechanism behind these closures.

**(c) Radar under-catch is plausible for jul2023 only.** MRMS peak hour at the sites is 16–22 mm (box maximum 25.6 mm, total ≤ 32 mm): about a 1-year 60-min depth for central MA (NOAA Atlas 14, ~1.0 in) and half the 10-year 43 mm drain design, yet NWS logged 1 ft of water in Holden and a stranded car on Southbridge St. Rain was likely heavier than the 1 km hourly MRMS, or drains were blocked; nothing published separates the two (IEM/ASOS fetches were blocked from the sandbox; the LSRs have no rain reports). The one gauge in the box (Sevenmile River, 22.8 km2) rose 0.24 m observed, 0.00 m modelled. aug2023b (34–42 mm/h, ~2–5-year hour) and sep2022 Webster (74 mm/h, ~100-year hour) are not under-catch: the rain was in the model. aug2023 MetroWest misses are at 21–31 mm/h in suburban settings (8–16 road segments within 300 m).

**Verdict.** The misses come from pluvial runoff the model does not generate (CN loss on mixed cells plus the 20 m grid, in 20–60 mm convective bursts). Overwhelmed drains are the matching real-world mechanism. Radar under-catch adds to it in jul2023.

## 3. Candidate rule: pluvial inflow on low-lying urban streets (`PROTO_PLUVIAL=1`)

Reuses `closure_ml.geo_features` (D8 upstream area, HAND) and the per-segment peak-1 h MRMS rain. Same rational-method idea as the sag layer, but it needs no closed lidar depression and compares inflow with a fixed inlet/pipe capacity rather than a design intensity (which gives 0 below 43 mm/h).

    Q      = 0.6 × i_peak1h × A_upstream
    P_pluv = Phi( ln(Q / 0.5 m3/s) / 0.5 )   on segments with HAND <= 0.5 m and >= 15 road segments within 300 m, else 0
    p_close = max(p_close, P_pluv)            (only with the flag; variant 'pluvial' = max(p_depth, P_pluv))

0.5 m3/s ≈ 3–5 HEC-22 sag grate inlets, or an 18–24 in pipe full at 1 %. Road density stands in for impervious share, which is not stored in the run dir.

**Leave-one-storm-out.** Each fold picked Q_cap from {0.02 … 2} m3/s and the density gate from {0, 10, 15, 20, 25} on the other 8 storms, with a fixed selection rule: maximise mean site recall with mean flagged share within 1 percentage point of the default. All 9 folds picked 0.5 and 15.

| held-out storm | sites caught (default → pluvial) | flagged share | lift (recall / share) |
|---|---|---|---|
| jul2023 | 0/5 → 1/5 (Shrewsbury St, A 0.30 km2, Q 1.0 m3/s) | 0.65 → 1.14 % | 0 → 17.6 |
| aug2023b | 0/2 → 1/2 (Providence Rd, Q 0.61) | 0.51 → 1.29 % | 0 → 38.6 |
| sep2022 | 0/4 → 2/4 (Worcester Rd; one place, two labels) | 1.87 → 2.99 % | 0 → 16.7 |
| aug2023 | 1/4 → 1/4 | 3.58 → 3.67 % | 7.0 → 6.8 |
| jul2021 | 1/5 → 1/5 | 1.22 → 1.32 % | 16.4 → 15.2 |
| sep2021 | 2/5 → 2/5 | 4.07 → 4.55 % | 9.8 → 8.8 |
| aug2026 | 1/4 → 1/4 | 2.20 → 3.29 % | 11.4 → 7.6 |
| aug2021 (in-sample) | 5/12 → 5/12 | 2.24 → 3.20 % | 18.6 → 13.0 |
| sep2023 (in-sample) | 47/127 → 50/127 | 2.80 → 4.50 % | 13.2 → 8.7 |
| **OOS 7 storms** | **5/29 → 9/29** (4 → 7 distinct places) | **2.01 → 2.61 %** | **8.6 → 11.9** |

**False alarms.** +6 to +80 segments per storm (aug2021 +80, sep2023 +76, aug2026 +49, Ida +36); lift falls 10–35 % in the four good storms where nothing is gained.

**Checks that the gain is not chance or terrain alone.** The same number of random extra segments gives an expected +0.3 OOS sites (+0.7 when drawn only from the low-lying dense-grid pool); the rule gives +4. With rain set to a constant 30 mm/h the aug2023b and sep2022 gains vanish. Sensitivity at gate 15 (OOS sites / mean share): Q_cap 0.3 → 10/29 at 3.41 %; 0.5 → 9/29 at 2.61 %; 0.75 → 8/29 at 2.23 %; 1.0 → 6/29 at 2.13 %. At 0.5 m3/s, gate 10 → 10/29 at 3.26 %, gate 20 → 8/29 at 2.32 %.

**Limits.** 4 of the 5 jul2023 misses drain only 0.03–0.05 km2; at 16–22 mm/h the bar would have to drop so far that every Ida and Elsa street would be flagged too. Only better rain or a fix to urban runoff generation can reach them. 29 OOS sites is small: +4 is suggestive, not significant. The rule stays off by default.

## 4. Recommended next steps

1. **Fix runoff generation in the flood model.** In w9, treat directly connected impervious separately (rain minus 1–2 mm) and apply CN to the pervious part only, without ×0.91 on pavement. Re-run the flash storms and the good storms together so false alarms show.
2. **Reprocess with the candidate layer** (no flood re-run; inputs are in each run dir; leave `PUBLISH` unset):

        for r in jul2023:jul2023_worcester_20m aug2023b:aug2023b_millbury_20m sep2022:sep2022_webster_20m aug2023:aug2023_metrowest_20m jul2021:jul2021_worcester_20m sep2021:sep2021_worcester_20m aug2026:aug2026_leominster_20m aug2021:aug2021_worcester_20m sep2023:sep2023_leominster_20m; do STORM=${r%%:*} NAME=${r#*:} PROTO_PLUVIAL=1 sbatch --export=ALL proto/turing/reprocess.slurm; done

   Then check `checks.rules.pluvial` and the 'pluvial' variant in each `summary.json`; they should match the table above.
3. **Get gauge rain for jul2023** (ORH ASOS, CoCoRaHS, 15-min MRMS) to put a number on under-catch before tuning any rain multiplier.
