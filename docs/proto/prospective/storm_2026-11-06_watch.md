# Storm watch: 6–7 Nov 2026 (archive `20261105_arc20261105`)

The first storm of the forward test (`PROSPECTIVE.md`). Running log: what each forecast cycle said, then what happened. Times UTC
unless marked EST. Automatic scoring follows from `archive_followup.yml` 24–36 h after the storm; this file is the hand-made companion.

## Forecast cycles

| cycle | model | heaviest rain (6 h / 24 h, mm) | 6 h window | headline | likely closures (k of 8) |
|---|---|---|---|---|---|
| 5 Nov 00Z | v1 | 33.8 / 52.9 | 6 Nov 17Z–23Z | 0 likely, 5 possible | – |
| 5 Nov 06Z | v1 | 27.2 / 44.8 | 6 Nov 18Z–7 Nov 00Z | 22 likely, 7 possible | MLK Jr Blvd ×2, Foster St ×2 (Worcester), 10 Berlin / Northborough / Clinton segments: all 8/8, all start-state water (see CHANGE_2026-11-05.md) |
| 5 Nov 12Z | v1 | 39.1 / 47.6 | 6 Nov 19Z–7 Nov 01Z | 10 likely, 5 possible | Route 2 Leominster (51395, known terrain artefact), Sanborn St Fitchburg, Water St / Depot Sq Leominster, Town Farm Rd Westford, Lackey Ln Barre, Oakmont Ave Westminster, 3 unnamed (Leominster, Lunenburg, Winchendon): all 2/8 |
| 5 Nov 18Z | **v2** (first) | 60.2 / **110.2** (Franklin) | 6 Nov 18Z–7 Nov 00Z | 3 likely, 66 possible | not published (see Operations). The 18Z HRRR moved the core south to Franklin / Bellingham / Milford and doubled the 24 h maximum; it is the only member that wet; its closures are the 66 'possible' (1 of 8). Not an artefact of the start-state rule: b2–b4 had 0 likely, 0–1 standing. NWS Flood Watch for Friday in effect. |
| 6 Nov 00Z | v2 | 50.2 / 96.7 (Bellingham) | 6 Nov 11Z–17Z | 25 likely, 44 possible | Bellingham: Paine St, Pine Grove Ave (4/8), Wrentham Rd (3/8), Railroad St, Beech St; Rogerson Crossing Uxbridge (4/8); Mendon: Cemetery St, Bellingham St; Mellen St Milford / Hopedale; Hopping Brook Rd Holliston. All storm-driven (v2 counts only water added after the rain begins). The 00Z HRRR kept the southern core (97 mm / 24 h) and moved the peak earlier, to Friday 6 AM – noon EST. b2 = b3 = b4 (duplicate-box bug, fixed below), so the north got no box. |
| 6 Nov 06Z | v2 | 37.0 / 41.8 (Pepperell) | 6 Nov 17Z–23Z | 22 likely, 6 possible | First cycle with four distinct boxes (north: Pepperell–Fitchburg, Westminster–Gardner, Hubbardston; plus Worcester). North boxes: 0 likely (24 h maximum back down to 42 mm). All 22 likely are in the Worcester box: East Park Terrace 8/8, Hudson St Northborough 6/8, Shrewsbury St and Cambridge St 5/8, Millbury St Grafton, Fantasia Dr, Coolidge Rd 3/8, MLK Jr Blvd, Wellington St, Murray Ave, Kansas St, Crowningshield Rd, Kinnicutt Rd 2/8. Southern core of 00Z (97 mm Bellingham) gone: the 06Z HRRR keeps the heaviest rain north. Several Worcester streets are closed depressions where the city's storm drains (not modelled) would carry water away: East Park Terrace rises to 42 cm by hour 24 and 50 cm at hour 50 in the latest member. |

Reading so far: the rain forecast is stable (24 h maximum 45–53 mm, heaviest 6 h on Friday afternoon–evening), but the core has moved
north between cycles (Blackstone valley at 00Z → central at 06Z → Fitchburg / Leominster / Westford at 12Z), so the roads change from
cycle to cycle. No road was named by two cycles. Model v2 (terrain fix T2 + depth above the rain-onset state) starts with the next cycle.

## Operations

- 5 Nov: the site served the 06Z forecast until about 21Z because the Pages deploy was queued behind the 32 flood-model jobs of the 12Z
  cycle. Fixed: the flood matrix now runs at most 14 jobs at once.
- 5 Nov 18Z (v2): computed twice and lost twice at the publish step. Both runs had been started from commits older than a data commit on
  main (a hand-added `forecast_history.json`, then the 12Z data), their `git pull --rebase` hit conflicts and the old loop retried on
  unmerged files until it gave up, while the job still reported success. Fixed for all six data-publishing workflows: `-X theirs`
  (the job's own data wins) and `git rebase --abort` on failure. A fresh forecast was dispatched at 02:30Z on the fixed workflow.
- 6 Nov 00Z: first v2 cycle on the site (published 06:38Z). The duplicate-box bug above was found in it and fixed (CHANGE_2026-11-05.md, operational fix). The forecast-history card now reads each cycle's model version after the ledger is written.
- 6 Nov 06–08Z, Forecast-tab review (screenshots from `ui_check.yml`): closure times now carry the weekday in 48 h runs; the visible key
  explains the wide forecast lines (likely 2+ of 8 / possible 1 of 8); the timeline's 'Now' is refreshed hourly by the live-feeds job
  (it was the forecast-cycle time, 5 h old); live data and forecast packs bypass the 10-min Pages cache; the live refresh / live feeds /
  events log workflows no longer drop a push on a race. Map check, 00Z: closed stretches follow low ground (Paine St along the Peters
  River, Wrentham Rd at Bungay Brook, Pulaski Blvd by Jenks Pond).

## During the storm (6 Nov 23:30Z = 6:30 PM EST)

| | forecast (latest on the site: 12Z cycle, published 22:09Z) | observed so far |
|---|---|---|
| rain | 6 h maximum 61 mm near Groton / Pepperell, 11 AM–5 PM EST; 24 h up to 89 mm | MRMS 3 h maximum 19.6 mm (to 23Z), district mean 4.8 mm in 3 h; peak rate 40 mm/h in a cell |
| rivers | – | North Nashua near Leominster 143 → 325 cfs, Nashua at East Pepperell 377 cfs: rising, well inside the banks |
| roads | 6 likely (West Brookfield Rd New Braintree 3/8; Depot Sq, Water St, Kingman Dr Leominster, 1 Leominster and 1 Groton unnamed 2/8), 10 possible | MassDOT feed: no flood events; no news reports of flooded roads found |

Reading: the HRRR was too wet for this storm so far (about a third of the forecast 6 h maximum fell). The 2-of-8 Leominster calls have not
verified as of 6:30 PM. Operations: the 12Z cycle reached the site 10 h after its issue time; fixed by reusing older members' runs
(only new members run) and by giving the live timeline the wall-clock 'now' (it was frozen at 12Z because the cycle was over 8 h old).

## After the storm (7 Nov 09Z, preliminary; automatic scoring follows from archive_followup.yml)

- Where the rain fell: the heavy core was south-east of District 3: NWS flood / flash-flood warnings on 6 Nov were for Barnstable
  (2–3 in by 1:53 PM), Bristol MA / RI and Plymouth (1.5–2.5 in, road closures in Acushnet and New Bedford by 9 PM); Brockton
  (Westgate Dr) and Falmouth flooded. District 3: MRMS district mean about 31 mm over 48 h, 3 h maxima about 20 mm; gauges rose but
  stayed in their banks (North Nashua near Leominster 143 → 325 cfs, Blackstone at Woonsocket 941 cfs).
- Flood reports in District 3: none found (MassDOT roadway-events feed: no flooding entries 6–7 Nov; news; NWS warnings did not
  cover the district). Absence of reports is not proof of dry roads; the automatic follow-up checks the remaining sources.
- Forecast: every cycle from 5 Nov 06Z to 6 Nov 12Z named likely closures in District 3 (22, 10, 25, 22, 6), in a different part of the
  district each time, following the HRRR core (Worcester / Berlin → Leominster–Westford → Franklin–Bellingham (110 mm) →
  Bellingham (97 mm) → Pepperell (42 mm) → Groton (89 mm)). The HRRR placed the storm 50–100 km too far west and north and too wet
  over the district; the flood model inherited it. Provisional verdict: false alarms in District 3, caused by the rain forecast.
- Operations lost the 6 Nov 18Z – 7 Nov 06Z cycles (cache-key error in the member-reuse change, fixed 09Z) and delayed others by up to
  10 h; the forward-test ledger has no rows for them.
- Lessons for the model (to be pre-registered before any change): (1) the k-of-8 rule kept 2-of-8 calls although the members disagreed
  on where the storm would be; a location-agreement check (do the members put heavy rain in the same box?) could have lowered these to
  'possible'. (2) Cycle-to-cycle stability: no road was named by two cycles, which the forecast-history card now shows to users.

### 7 Nov, 10:50Z: would a stricter "likely" rule have helped?

- In this storm's forecasts most "likely" roads were closed by exactly 2 of the 8 members (archive `kofn.csv`):
  5 Nov 06Z 3 of 22 likely at k = 2; 5 Nov 12Z 10 of 10; 6 Nov 00Z 21 of 25; 6 Nov 06Z 14 of 22; 6 Nov 12Z 5 of 6.
  A "3 of 8" rule would have cut the likely list to 0 to 8 roads per cycle.
- But on the 7 out-of-sample past storms (`docs/proto/forecast/ensemble.json`, `by_threshold`) a higher k loses real flood sites:

  | rule | long lead: recall / mean flagged | short lead: recall / mean flagged |
  | --- | --- | --- |
  | 2 of 8 (live) | 0.345 / 3.1 % | 0.276 / 2.3 % |
  | 3 of 8 | 0.276 / 2.5 % | 0.241 / 2.0 % |
  | 4 of 8 | 0.172 / 1.9 % | 0.207 / 1.7 % |

  3 of 8 drops 2 of the 29 sites at long lead (Sep 2021, Jul 2023) and 1 at short lead (Aug 2026) for a small cut in flagged roads.
  So raising k is not the fix; the live rule stays.
- The better test is the location-agreement check (do the members put the heavy rain in the same place?). It needs each member's rain field
  per cycle, which the archive does not keep yet (only `gate.json` of the issue cycle and `kofn.csv`). Not tested; nothing changed in the model.
- Two cycles (6 Nov 18Z, 7 Nov 00Z) show n = 1 in the archive: those are the cycles lost to the cache-key bug (only the issue member ran).

### 7 Nov, 12:30Z: operations

- Member cache tested (prefix `test_cache`, init 6 Nov 18Z, 1 box): first pass 8 members 55 to 110 min; second pass the 7 older members
  restored from the cache in about 35 s each, only the issue-cycle member reruns. A forecast update during a storm is now one flood run per box.
- Storm replays repacked from their terrain-fix (T2) runs, with rivers and ponds drawn where they rise >= 20 cm above their lowest level
  (`RISE_MIN_M`). Segments at P >= 0.5, old -> T2: Leominster Sep 2023 102 -> 73, Worcester Aug 2021 98 -> 73, Sep 2021 Worcester 187 -> 104,
  Aug 2023 MetroWest 108 -> 96, Jun 2020 Northbridge 22 -> 20, Sep 2022 Webster 15 -> 11, Jul 2023 Worcester 6 -> 0.
  Aug 2026 Leominster, Sep 2018 Fitchburg and Sep 2018 Milford failed on Turing on the first try and were requeued.

### 7 Nov, 12:40Z: second rain band; flash-flood panel bug

- Radar at 12:34Z: rain rates up to 25 to 28 mm/h in the south of the district (Bellingham, Blackstone, Franklin, Mendon), but short:
  most in one hour 8 mm, in 3 h 17 mm (Millis / Blackstone). Under the flood-model trigger (25 mm in 6 h).
- Bug found and fixed: the live FLASH feed compared MRMS QPE/FFG ratios, which MRMS stores in percent, with 1.0, so every District 3 town
  showed as "at or over flash-flood guidance" from 6 Nov 05Z to 7 Nov 12Z. Real maximum ratio through the storm was 0.75 (3 h, 7 Nov 09Z).
  After the fix: 0 towns flagged; district maximum 0.2 (1 h), 0.3 (3 h), 0.6 (6 h).

### 7 Nov, 17:00Z: forecast vs outcome (correction and radar-driven reruns)

**Correction.** The "about 31 mm 48 h mean" above was the District 3 mean. The south of the district was much wetter: the radar-driven
model input (MRMS, gauge-corrected) gives box b1 (Bellingham, Mendon, Milford, Uxbridge) 96 mm max and 72 mm mean over 48 h, with
two bursts of about 40 mm in 6 h (6 Nov 05-11Z, 7 Nov 00-06Z). The north was drier than forecast. So "the rain went elsewhere" is only
true for the north and west of the district.

**Reports in District 3 (6 to 7 Nov):** none. NWS LSRs 0 of 210 Massachusetts rows, MassDOT events 0 of 23, SeeClickFix 0, news none
found; NCEI Storm Events not yet published. Rivers rose a lot but stayed below flood stage (Blackstone at Millbury 119 -> 928 cfs,
Woonsocket 1330 cfs at 3.6 ft).

**Forecast rain vs radar, 48 h totals (forecast = the cycle's town value, mm):**

| cycle | Bellingham | Milford | Worcester | Leominster | Fitchburg | likely / possible |
| --- | --- | --- | --- | --- | --- | --- |
| 5 Nov 00Z | 50 | 36 | 30 | 21 | 27 | 0 / 5 |
| 5 Nov 06Z | 38 | 28 | 44 | 45 | 31 | 22 / 7 |
| 5 Nov 12Z | 30 | 22 | 20 | 41 | 49 | 10 / 5 |
| 6 Nov 00Z | 104 | 65 | 36 | 36 | 34 | 25 / 44 |
| 6 Nov 06Z | 43 | 42 | 39 | 39 | 53 | 22 / 6 |
| 6 Nov 12Z | 44 | 53 | 54 | 71 | 63 | 6 / 10 |
| radar (box) | b1 max 96, mean 72 | in b1 | b8 pending | b4 max 52, mean 40 | b3 max 30, mean 20 | |

**Flood model on the radar rain (model v2 = live settings: T2 terrain, depth from rain onset), segments at P >= 0.5:**
b1 Bellingham–Milford 0 (expected closures 6.2), b2 Holden–Spencer 0, b3 Fitchburg–Gardner 0, b4 Berlin–Leominster–Northborough 11
(P >= 0.9: 5). The 6 Nov 00Z forecast had 22 likely closures in the Bellingham–Mendon area; with the rain that fell, the same model
closes none there, matching the reports.

**What this says so far.**
- South (b1): forecast totals were about right (104 vs 96 mm) but the forecast put 50 mm in 6 h on Bellingham, and the members with
  closures were wetter still; observed 6 h bursts were about 40 mm and the model closes nothing. Error source: rain intensity of the
  forecast members, amplified by a closure response that is steep near the threshold.
- North (b3, b4, Leominster/Fitchburg): forecast about twice too wet. Error source: rain forecast.
- b4: 11 closures from the radar rain with 0 reports: a possible flood-model false positive (road list pending, rerun with names).
- The archive's radar boxes were first-come (cap 4), so the boxes of the later, wettest forecasts (incl. 6 Nov 06Z Worcester, 22 likely,
  East Park Terrace 8 of 8) had no radar run. Cap raised to 8 and the 4 later boxes added; rerun pending.

### 7 Nov, 19:00Z: all 8 boxes on the radar rain; main error sources

Radar-driven reruns (archive_followup, publish=false, window 5 Nov 20Z + 48 h; last 2 h not yet on radar). Segments at P >= 0.5:

| box | area | radar rain max / mean (mm) | baseline model | v2 (live settings) | reports |
| --- | --- | --- | --- | --- | --- |
| b1 | Bellingham, Mendon, Milford, Uxbridge | 96 / 72 | 2 | 0 | 0 |
| b2 | Holden, Spencer, Rutland | 50 / 28 | 1 | 0 | 0 |
| b3 | Fitchburg, Gardner | 30 / 20 | 0 | 0 | 0 |
| b4 | Clinton, Berlin, Lancaster, Northborough | 56 / 43 | 22 | 11 | 0 |
| b5 | Groton, Pepperell, Dunstable | 43 / 33 | – | 0 | 0 |
| b6 | Holden, Princeton, Hubbardston | 38 / 25 | – | 0 | 0 |
| b7 | Franklin, Grafton, Holliston | 84 / 61 | – | 0 | 0 |
| b8 | Worcester, Northborough, Grafton | 66 / 48 | – | 7 | 0 |

v2 roads closed by the radar rain:
- b8: East Park Terrace (0.75 m, 11.5 h over 30 cm), Shrewsbury Street x2, Cambridge Street, Fantasia Drive, Hudson Street (Northborough),
  Martin Luther King Jr Blvd. All reach 30 cm 37 to 41 h into the run (7 Nov 09Z to 13Z, the second rain band). These are the same roads
  the 6 Nov 06Z forecast listed as likely (East Park Terrace 8 of 8 members, Hudson Street 6 of 8, Shrewsbury and Cambridge Street 5 of 8).
- b4: Ash Street (Clinton) x2, Water Street (Clinton), Route 62 and South Street (Berlin), the Route 290 / Solomon Pond Road ramps
  (Northborough), Route 117 (Lancaster). Most reach 30 cm 0.5 h into the run, before the storm's rain, so the depth comes from water
  already next to the road at the start (streams, ponds), not from this storm.

**Main error sources, by area.**
1. North and west (Leominster, Fitchburg, Gardner, Pepperell, Holden): the rain forecast, about twice too wet. With the real rain the
   model closes nothing, matching the reports.
2. South (Bellingham to Franklin): the forecast storm total was about right but the members put too much of it into one 6 h burst. With
   the real rain the model closes nothing (v2), matching the reports. Error source: rain intensity of the forecast members.
3. Worcester (b8): not the rain forecast. The model closes the same 7 roads with the observed rain; no one reported them. Either these
   are real, unreported street-flooding spots (East Park Terrace / Shrewsbury Street / Cambridge Street are low streets under or next to
   rail lines), or the model floods them because it has no storm drains. Storm-drain experiments were already rejected twice
   (docs/proto/drains), so this needs evidence first (city 311 records, cameras), not a model change.
4. b4: start-state water on roads next to streams and ponds (depth at the start of the run). The closure rule should only count water
   that the storm adds.

**Proposed changes, pre-registered in `CHANGE_PROPOSAL_2026-11-07.md`, not adopted.**
P1 rise rule for closures (start-state water), P2 rain-location agreement for "likely", P3 radar boxes follow the forecasts (cap raised
to 8: done), P4 evidence for the Worcester hot spots before any model change.
