# Label round 2: multi-road split, WX1BOX, MassDOT water-surface crashes, MRMS FLASH check (24 Oct 2026)

Items 1–3 (+9) of `docs/proto/DATA_IDEAS.md`. Locked storms (PROTOCOL.md §2: aug2015, aug2018, aug2020, jul2018, oct2016) were not read or
written by any step below. No model, threshold or run changed: every difference in §4 is a **label** change scored on the same parity runs.

## 1. Closure labels: parser fix + WX1BOX

- **Multi-road split.** `proto/labels_round2.py audit` splits every in-box, in-window LSR / Storm Events text into all the roads it names
  (`roads()`), and lists roads absent from the label files (`round2/split_audit.json`). After removing basements, cross-streets of an existing
  site and spelling variants (Rathbun/Rathburn, Crescent/Cresent), 7 real road reports were missing; they are now `-Snn` rows.
- **WX1BOX** SKYWARN compilations (`round2/wx1box/`): 2 road reports that never reached an NWS product are `-Xnn` rows
  (Mirick Rd, Princeton, aug2026; Main St, Westminster, jul2023b).
- **Removed:** AUG2026-01 (Allen Hill Rd, Leominster) — the LSR is a flooded basement.
- **Geocode:** `label_geocode.yml` run 40104068422 (6 shards, `labels_geocode_osm_{0..5}.json`) placed all 9; `build` wrote them. All 9 are
  `approx` (road centroid / vertex nearest the NWS point; one OSM pair, Speen St at Nottingham Dr); the two intersection pairs that OSM could not
  close (West St at Hillary Rd, West Main St at Mason Rd) fell back to the road vertex and stay `approx`. None is left at a town point.
  Per-row detail: `labels_round2_sites.json`. `labels_expand.py build` now keeps `-S/-X` rows on a rebuild.

| storm | file | rows before → after |
|---|---|---|
| aug2026 | labels_aug2026_leominster.csv | 7 → 11 (−1, +4 S, +1 X) |
| aug2023 | labels_aug2023_metrowest.csv | 5 → 6 |
| sep2022 | labels_sep2022_webster.csv | 4 → 5 |
| sep2021 | labels_sep2021_worcester.csv | 7 → 8 |
| jul2023b | labels_jul2023b_worcester.csv | 4 → 5 (Main St, Westminster is outside the box: not scored) |

## 2. MassDOT water-surface crashes (separate source)

`proto/crashwater.py`: crashes with road surface code 6 "Water (standing, moving)" from IMPACT open data (2021–2026, `MASSDOT_ODP_OPEN_<yr>`)
and the StatewideCrashesDashboard layer (2018–2020), 314 District-3 crashes in all (`round2/crash_water_d3*.csv`). Window t0 − 2 h .. t0 + hours
+ 6 h, inside the storm box. Written to `proto/data/crashwater_<storm>.csv` (never `labels_*.csv`); scored only with `SCORE_CRASHWATER=1`.
All 25 non-locked catalogue storms are now covered (2018–2020 included this round; locked-storm days dropped from discovery).

- **Yield is small: 6 crashes in 4 storms** (aug2021 2, jul2021b 2, sep2023 1, aug2026 1); 21 storms have none. All `exact`, clock-timed.
- **Against the parity runs** (crash rows alone, `round2/crashwater_score.json`): 6 sites, all matched to segments; **4/6 in the top 3 %**
  (chance 0.03), 2/6 at the rule tier, 5/6 in the top 10 %. Too few to pool; useful as an independent, exactly placed check.
- **Storm discovery** (`round2/crashwater_days.json`): 18 non-locked days with ≥ 2 water crashes in one 20 × 20 km window; 5 match catalogue
  storms, **13 are not in the catalogue** (strongest: 2018-03-02 Milford/Uxbridge, 2019-10-17 Auburn/Worcester, 3 each; several are winter
  rain/sleet days and need an NWS check before they become storms).

## 3. MRMS FLASH archive check (item 9)

`round2/mrms_flash_check.json`: on AWS (`noaa-mrms-pds`, from 14 Oct 2020) all 19 FLASH products exist for **all 13 AWS-era storms**, full windows
(CREST 10-min, QPE ARI / FFG ratio 2-min). **The 13 storms of 2018–2020 (and sep2014) have none on AWS**; the IEM mtarchive FLASH folder
(2019 on) is not read. Extractor `proto/mrms_flash.py` (Actions `mrms_flash.yml`) has written `docs/proto/ml/flash/flash_<storm>.csv` for all
13 AWS storms (CREST max unit streamflow, max QPE/FFG ratio, max QPE ARI per segment). Opt-in only: `PROTO_FLASH=1` makes
`closure_v2.load_storm` attach it; no model uses it, and adding it is a pre-registered candidate under PROTOCOL v2.

## 4. Re-score (`python proto/score_v2.py --catalog`, parity runs, box domain)

Before = `scoring/BASELINE_v2_expanded.json`; after = `obs/round2/score_round2.json` (+ `score_round2_table.md`). Same runs, same matching
(new rows matched by the strict 30 m rule; `score_v2.py` now does this for label rows newer than a run's published matches).

| pool | storms | sites | site recall @ rule | lift @ rule | site recall @ 3 % [90 % CI] | lift @ 3 % | @ 10 % | FSS300 @ rule | PR-AUC site |
|---|---|---|---|---|---|---|---|---|---|
| heldout23 before | 23 | 90 | 0.056 | 4.8 | 0.167 [0.080, 0.255] | 2.6 | 0.427 | 0.031 | 0.008 |
| heldout23 after | 23 | **98** | 0.092 | 6.4 | 0.204 [0.104, 0.303] | 3.1 | 0.443 | 0.051 | 0.010 |
| heldout7 (OOS-7) before | 7 | 32 | 0.125 | 5.4 | 0.188 | 2.9 | 0.388 | 0.038 | 0.007 |
| heldout7 (OOS-7) after | 7 | 40 | 0.200 | 7.4 | 0.275 | 4.1 | 0.435 | 0.073 | 0.015 |

Changed storms (sites; rule / 3 % site recall): aug2026 7 → 10 (0.14 → 0.30 / 0.29 → 0.50), sep2022 3 → 4 (0 → 0.25 / 0 → 0.25),
sep2021 6 → 8 (0.33 → 0.38 / 0.50), aug2023 5 → 6 (0.20 → 0.17), aug2023b 2 → 3 (0 → 0). Turing heldout23 (7 storms): 27 → 40 sites,
3 % recall 0.22 → 0.33.

**Reading.** The 8 new sites raise measured skill (heldout23 3 % recall +0.037, rule-tier recall +0.036), mostly from aug2026 and sep2022: the
report-backed roads the old parser dropped were roads the model already ranks high. Caveats: all new rows are `approx` (centroid/vertex,
500 m uncertainty) and matched at 30 m, so individual hits are placement-sensitive; CIs still overlap widely. This is a measurement change, not
a model gain: **any later `--compare` must use a baseline re-scored on these labels** (`score_round2.json`), not `BASELINE_v2_expanded.json`.
