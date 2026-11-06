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
