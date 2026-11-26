# After-storm check from the MassDOT events record: pre-registration (frozen 26 Nov 2026, before any storm is scored with it)

Requested by Mo on the tab board, 26 Nov 2026: match flood-related MassDOT roadway events (closures, high water, washouts) to road segments
after each storm and score them against the forecast's flags, as an extra label source. **Reporting only.** Nothing in the live model, the
forecast, the forward-test rules (`PROSPECTIVE.md`) or `RESULTS.md` changes. The first storm it will score is `arc20261126` (27 Nov 2026).

Why a separate check: the forward test already counts MassDOT flood events among its labels, but it scores them only through the
radar-run verification inside the forecast boxes. This check scores the MassDOT record on its own, district-wide, so that it also shows
the flood events that fell **outside** the boxes the model ran on.

## 1. Which events count (fixed now)

Source: the MassDOT roadway-events archive `docs/proto/obs/massdot_events/YYYY-MM.jsonl` (logged every 10 min by `proto/events_logger.py`).
Text searched = `EventType`, `EventSubType`, `LocationDescription`, `LaneBlockageDescription` and any description/cause field.

- **Class F, flood-related (scored).** The text matches the existing label rule `FLOOD_RE` of `proto/storm_archive.py` (flood, washout,
  washed out, ponding, standing water, high water, water on/in/across/over/covering the road, impassable, sinkhole, culvert, storm drain,
  catch basin, stormwater, road closed due to water, submerged) and does **not** match `NOT_FLOOD` (water main, hydrant, sewer odor, ice,
  icing, frozen). Winter-treatment events ("Crews Treating Roadway") never count. This is the same rule the forward test uses, so the two
  label sets agree on what a MassDOT flood event is.
- **Class C, closure without a stated cause (reported only, never scored).** A full or partial road closure (`CLOSE_RE` of
  `proto/live_feeds.py`) created in the storm window that is not class F and whose type is not a crash, disabled vehicle, fire, police
  activity, planned work / construction, special event or bridge lift. Listed in the report for a person to read; not a label.
- One event counts once (`EventId`); updates of the same event are not new events.

## 2. Time and place (fixed now)

- **Time:** `EventCreatedDate`, which the feed gives as America/New_York wall-clock time without an offset; converted to UTC.
- **Storm window:** from the storm's evidence start − 6 h to its evidence end + 12 h (`storm.json`, `evidence`). The 12 h tail allows for
  closures logged after the rain.
- **District 3 only:** the event point (`PrimaryLatitude`, `PrimaryLongitude`) must fall in a District 3 town (`town_of`).
- **Segment match (primary):** every segment of `docs/graph_segments.json` with a road vertex within **30 m** of the event point, the strict
  match of `score_v2` / `prototype.label_segments`.
- **Segment match (fallback, reported separately):** if nothing is within 30 m, the nearest vertex within **100 m** of a segment whose
  normalised name (`prototype.norm_road`) equals the event's `RoadwayName`. Events matched only this way are scored in a second line, not in
  the primary numbers.
- **Unmatched:** events with neither match are listed with their coordinates and counted as unmatched.
- **Sites:** matched events are clustered single-link within **150 m**; a site counts once (as in `score_v2`).

## 3. Which forecast is scored (fixed now)

- The forecast cycles archived for the storm (`forecast/<cycle>/kofn.csv`), using only cycles issued **at least 1 h before the storm's first
  class-F event** (the forward-test rule).
- **Primary:** the **latest** such cycle (what a user would have had in hand). **Secondary:** the union of all such cycles (any warning
  issued in time). No "best cycle" choice.
- Flags: **likely** (k ≥ 2 of 8, `cls = likely`) and **likely or possible** (`cls` in likely / possible), as published.

## 4. Measures (all reported, no pass/fail line)

Per storm and pooled over storms (sums of counts):
1. Class-F events, matched / fallback / unmatched; class-C events.
2. **Sites inside the forecast boxes** of the scored cycle versus outside (coverage).
3. **Site recall:** sites on a likely segment / all sites (district-wide), and / sites inside the boxes; the same for likely-or-possible.
4. **Lift:** site recall / share of District 3 segments flagged (district-wide denominator `graph_segments.json` `n`).
5. **Lead:** issue time of the earliest in-time cycle that flags a site, to that site's first event (hours), median.

## 5. Output and use

Code `proto/massdot_check.py` (written after this file is committed); run by the storm follow-up (`archive_followup.yml`) after the labels
step, and by hand. Output per storm `docs/proto/archive/<storm>/massdot_check.json` and a pooled `docs/proto/prospective/MASSDOT_CHECK.md`.
The numbers are not used to tune anything. A change to any rule above is a new pre-registration, dated, before the next storm is scored.

Limits, stated now: the MassDOT feed covers state-maintained roads and the events its staff enter, so most local flooding never appears in
it; an empty record is not evidence that nothing flooded. Since the archive began (Oct 2026), no class-F event has been logged in District 3.

Execution note (26 Nov 2026, before any class-F event was scored): "road vertex" in §2 is implemented as the road points of
`graph_segments.json` densified every 10 m (`massdot_import.road_points`), the points `score_v2`'s strict match uses; raw polyline
vertices can be far apart on straight roads. Rules and radii unchanged.
