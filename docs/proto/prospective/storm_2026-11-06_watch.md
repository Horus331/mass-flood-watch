# Storm watch: 6–7 Nov 2026 (archive `20261105_arc20261105`)

The first storm of the forward test (`PROSPECTIVE.md`). Running log: what each forecast cycle said, then what happened. Times UTC
unless marked EST. Automatic scoring follows from `archive_followup.yml` 24–36 h after the storm; this file is the hand-made companion.

## Forecast cycles

| cycle | model | heaviest rain (6 h / 24 h, mm) | 6 h window | headline | likely closures (k of 8) |
|---|---|---|---|---|---|
| 5 Nov 00Z | v1 | 33.8 / 52.9 | 6 Nov 17Z–23Z | 0 likely, 5 possible | – |
| 5 Nov 06Z | v1 | 27.2 / 44.8 | 6 Nov 18Z–7 Nov 00Z | 22 likely, 7 possible | MLK Jr Blvd ×2, Foster St ×2 (Worcester), 10 Berlin / Northborough / Clinton segments: all 8/8, all start-state water (see CHANGE_2026-11-05.md) |
| 5 Nov 12Z | v1 | 39.1 / 47.6 | 6 Nov 19Z–7 Nov 01Z | 10 likely, 5 possible | Route 2 Leominster (51395, known terrain artefact), Sanborn St Fitchburg, Water St / Depot Sq Leominster, Town Farm Rd Westford, Lackey Ln Barre, Oakmont Ave Westminster, 3 unnamed (Leominster, Lunenburg, Winchendon): all 2/8 |

Reading so far: the rain forecast is stable (24 h maximum 45–53 mm, heaviest 6 h on Friday afternoon–evening), but the core has moved
north between cycles (Blackstone valley at 00Z → central at 06Z → Fitchburg / Leominster / Westford at 12Z), so the roads change from
cycle to cycle. No road was named by two cycles. Model v2 (terrain fix T2 + depth above the rain-onset state) starts with the next cycle.

## Operations

- 5 Nov: the site served the 06Z forecast until about 21Z because the Pages deploy was queued behind the 32 flood-model jobs of the 12Z
  cycle. Fixed: the flood matrix now runs at most 14 jobs at once.
