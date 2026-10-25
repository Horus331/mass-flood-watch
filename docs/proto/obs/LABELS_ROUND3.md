# Label round 3: SeeClickFix 311 issues and the label evidence ladder (25 Oct 2026)

Two additions to the label sources, both **secondary**: the PROTOCOL decision set (closure labels `labels_<storm>_*.csv`, unweighted
site recall) is unchanged, and no model, threshold or run changed. Locked storms (PROTOCOL.md §2: aug2015, aug2018, aug2020, jul2018, oct2016)
were never queried, read, written or scored. Unreported roads stay **unknown**; no step below creates a negative.

## 1. SeeClickFix (separate source `proto/data/scf_<storm>.csv`)

- **Fetch** (`proto/scf_fetch.py`, Actions `scf_fetch.yml`, since the sandbox cannot reach seeclickfix.com): `/api/v2/issues` by bounding box.
  (a) Every issue of every type inside each non-locked catalogue storm box, created t0 .. t0 + hours + 24 h (`round3/scf_window_<storm>.json`).
  (b) Flood-type issues across District 3 for 2018-01 .. 2026-10. These come from 18 flood-like request-type ids (the current ones from a 0.1° grid
  of `/issues/new`, 219 types in all, plus older ids seen in the windows) and the text search "flood". This gives 3,549 issues
  (`round3/scf_flood_d3.csv`, compact). 8 issues dated within ±1 day of a locked window were dropped before anything was committed.
- **Coverage is the limit.** The City of Worcester has been on SeeClickFix only since 2023. Before that, D3 coverage is Fitchburg (2018 on), plus
  Framingham, Natick and Marlborough, and Leominster's 2023 "Flood Damage Reporting" form. So the **2018–2022 storms have no issues at all**
  in their boxes: all 16 Worcester/Webster/Gardner/Northbridge/Milford windows before 2023 are empty.
- **Rows** (`proto/scf_labels.py`): one row per issue in the label schema. Each row carries the exact issue lon/lat, `time_local` = created
  (local), `name` = summary, `quote` = description, type `reported_flooding`, time/coord quality `exact`, `source_url` = the issue page, and
  `source` = SeeClickFix. A row is kept only if its request type names flooding or a washout (Flooding Condition on Street, Storm Water
  Drainage/Flooding, Washout On Street, Catch Basin Not Taking Water) or its text says flood, standing water, ponding, water over the road or
  washed out. Routine drain-clog and sweeping requests are not labels (32 of the 65 in-window drainage issues). Neither are
  basement-only reports. **33 rows in 7 storms**: aug2023 16, jul2023c 6, sep2023 4, aug2023b 3, jul2023 2, aug2026 1, jul2023b 1.
  Scored only with `SCORE_SCF=1`.
- **Candidate storms** (`round3/scf_days.json`): local days with ≥ 5 flooding-type issues (catch-basin-only excluded) in one 20 × 20 km window
  inside the union of the catalogue boxes. There are 15 such days. 2 match catalogue storms (2023-08-08 aug2023, 11 issues; 2023-09-13 sep2023). **13
  are not in the catalogue**:

  | date | issues (window) | area | note |
  |---|---|---|---|
  | 2025-02-16 / 02-17 | 14 / 6 | Worcester | winter rain + snowmelt; check NWS before use |
  | 2025-05-15 | 10 | Worcester | strongest warm-season candidate |
  | 2025-10-20 | 10 | Worcester | |
  | 2023-09-14 | 10 | North Attleborough | real flash flood, but outside D3 (inside the padded catalogue union) |
  | 2025-05-31 | 9 | Fitchburg | mostly "Berm Repair" follow-ups: weak |
  | 2024-04-12 | 8 | Worcester | |
  | 2026-07-29 | 8 | Worcester / Auburn | |
  | 2023-12-18 | 7 | Natick / Sudbury | December rain storm |
  | 2020-11-23, 2024-05-23, 2026-04-15, 2025-12-19 | 5–6 | Framingham-Natick, Worcester | |

  Worcester's post-2023 base rate is high (one 311 report every few days), so a day with 5 reports is a lead, not a storm. Each needs an NWS
  LSR / MRMS check before it can enter the catalogue (the same rule as the crash-water candidates of round 2).

## 2. Evidence ladder (`proto/label_tiers.py` → `proto/data/labels_tiered_<storm>.csv`)

The ladder is derived, one file per storm, over every source: labels_*, crashwater_*, scf_*. The original label files are untouched.
The tiers and weights below were fixed in the script before any tiered score was computed:

| tier | weight | rule |
|---|---|---|
| confirmed_inundation | 1.0 | DPW damage inventory, or the state damage-site tables (CDBG-DR / recovery plan / MassDOT handout). Also NWS / Storm Events / WX1BOX rows that describe an observation on the road (stuck / stranded, rescue, a stated depth, under water, impassable, washed out) or a damage type (washout, culvert_failure, sinkhole, bridge_damage) |
| confirmed_closure | 1.0 | type `closed`, or "closed / closure / shut down" in an NWS, WX1BOX or news row |
| corroborated | 1.0 | a row that would otherwise be `reported`, with a row from a **different** source family within 150 m in the same storm. LSR and Storm Events count as one family (NWS). Town-level points never corroborate |
| reported | 0.6 | a single report: generic "flooded" NWS / news rows, MassDOT water-surface crashes, SeeClickFix |
| suspected | 0.3 | indirect signals (speed drops): none yet |

The weight of a site is the weight of its best label. All 320 rows (25 storms): 170 confirmed_inundation, 35 confirmed_closure, 9 corroborated,
106 reported (`round3/tiers_summary.json`).

**Opt-in uses (defaults unchanged):**
- `SCORE_TIERS=1 python proto/score_v2.py ...` adds `wsite_recall` and `recall_by_tier` to every block. The pooled tables gain `recall_<tier>`.
- `TIER_WEIGHTS=1` makes `closure_ml.train/evaluate` and `closure_v2.load_storm → parts_for / V1` use the weights as positive sample weights.
  Unlabeled rows keep weight 1. `python proto/closure_expanded.py run --tier-weights` writes `*_tiered` outputs; it has not been run.

## 3. Re-score (`python proto/labels_round3.py score`, parity runs, box domain, 2000 bootstrap replicates; `round3/score_round3.json`)

`base` reproduces round 2 exactly (98 sites, 0.204), so every difference below comes from the labels.

| setting | pool | sites | site recall @ 3 % [90 % CI] | lift @ 3 % | weighted recall @ 3 % | rule-tier recall | FSS300 @ 3 % |
|---|---|---|---|---|---|---|---|
| base (decision labels) | held-out 23 | 98 | 0.204 [0.104, 0.303] | 3.1 | – | 0.092 | 0.023 |
| + SeeClickFix | held-out 23 | **122** | 0.205 [0.120, 0.292] | 3.2 | – | 0.082 | 0.028 |
| tiers | held-out 23 | 98 | 0.204 | 3.1 | **0.214** [0.107, 0.321] | 0.092 | 0.023 |
| + SeeClickFix, tiers | held-out 23 | 122 | 0.205 | 3.2 | 0.213 [0.118, 0.309] | 0.082 | 0.028 |
| base | OOS-7 | 40 | 0.275 | 4.1 | – | 0.200 | 0.033 |
| + SeeClickFix | OOS-7 | 57 | 0.263 | 4.1 | – | 0.158 | 0.046 |
| tiers | OOS-7 | 40 | 0.275 | 4.1 | 0.301 | 0.200 | 0.033 |

- **Added:** in held-out 23, 28 SeeClickFix rows matched (strict 30 m), giving **+24 sites (98 → 122, +24 %)**, all SeeClickFix-only.
  By storm: aug2023 +12, jul2023c +6, aug2023b +3, aug2026 / jul2023 / jul2023b +1 each. The dev storm sep2023 gains 3 (79 → 82).
- **Recall by tier at 3 %** (held-out 23, base labels): confirmed_inundation 0.195 (41 sites), confirmed_closure 0.294 (17),
  corroborated 1/1, reported 0.154 (39). With SeeClickFix, reported is 0.175 on 63 sites. The SeeClickFix-only sites alone have 5/24 hit (0.21).
- **Corroborated share is tiny:** 1 of 98 held-out sites (1.0 %), and 1 of 122 with SeeClickFix (0.8 %). Only one SeeClickFix issue lands
  within 150 m of another source (Natick, aug2023). The sources mostly report different roads, so the 24 new sites are new places, not
  confirmations.
- **Effect on held-out recall at 3 %: none that matters.** Adding SeeClickFix gives +0.001 (the new sites are hit at the same rate as the old
  ones). Tier weighting gives +0.010 (0.204 → 0.214), because confirmed-closure sites are hit more than reported ones. Both are far inside
  the CIs (± 0.10). SeeClickFix lowers rule-tier recall (0.092 → 0.082): 311 reports are mostly small local streets that the depth rule rarely
  flags. FSS300 rises slightly (0.023 → 0.028) because the new exact points sit near flagged road.

**Reading.** The SeeClickFix rows are useful as dense, exactly placed and timed points for the 2023+ Worcester / Fitchburg / MetroWest storms
and for storm discovery. They do not change the skill estimate, and they cannot help the 2018–2022 storms. The ladder shows the model ranks
official closures and direct observations at least as well as single reports, so down-weighting reported sites raises measured recall a
little. It does not change any conclusion. Neither setting replaces the decision set. A future `--compare` must state its label setting, and both
baseline and candidate must use the same one (score_v2 refuses mismatched site lists).
