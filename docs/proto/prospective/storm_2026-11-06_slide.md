# The 5–7 Nov 2026 storm: what the live system did (action item 16, Nov 3 minutes)

Sources: `docs/proto/prospective/ledger.csv` (every cycle, as issued), `storm_2026-11-06_watch.md` (running log),
`docs/proto/archive/20261105_arc20261105/` (archived forecasts, radar replays of all 8 boxes, `verify.json`), `RESULTS.md`.
Times ET = UTC − 5. Everything below is what the system issued at the time; the radar runs are **replays**, labelled as such.

## 1. Before the storm: what was issued
- **The live forecast ran, and the rain gate fired on every cycle from 5 Nov 00Z (Wed 4 Nov 7 PM ET) to 7 Nov 00Z (Fri 6 Nov 7 PM ET).**
  The HRRR forecast 24 h maxima of 42–110 mm over District 3, above the 40 mm / 24 h gate; 8 members each cycle.
- Archived: `docs/proto/archive/20261105_arc20261105/forecast/<cycle>/` (one folder per cycle; `kofn.csv` = which members closed which road).

| HRRR cycle (UTC) | on the site (ET) | forecast 24 h max | "likely" (2+ of 8) | "possible" (1 of 8) | where |
|---|---|---|---|---|---|
| 5 Nov 00Z | Wed 4 Nov 11:03 PM | 53 mm | 0 | 5 | Blackstone valley |
| 5 Nov 06Z | Thu 5 Nov 5:10 AM | 45 mm | 22 | 7 | Worcester (MLK Blvd, Foster St), Berlin / Northborough / Clinton: start-state water, fixed the same day (model v2) |
| 5 Nov 12Z | Thu 5 Nov 3:33 PM | 48 mm | 10 | 5 | Leominster (Water St, Depot Sq), Fitchburg (Sanborn St), Westford, Barre, Westminster |
| 5 Nov 18Z | not published | 110 mm (Franklin) | 3 | 66 | lost at the publish step (fixed) |
| 6 Nov 00Z | Fri 6 Nov 1:38 AM | 97 mm | 25 | 44 | Bellingham (Paine St, Pine Grove Ave 4/8), Uxbridge (Rogerson Crossing 4/8), Mendon, Milford |
| 6 Nov 06Z | Fri 6 Nov 11:45 AM | 42 mm | 22 | 6 | Worcester (East Park Terrace 8/8, Shrewsbury St, Cambridge St 5/8), Northborough (Hudson St 6/8) |
| 6 Nov 12Z | Fri 6 Nov 2:25 PM | 89 mm | 6 | 10 | Leominster (Depot Sq, Water St, Kingman Dr), New Braintree, Groton |
| 6 Nov 18Z, 7 Nov 00Z | Fri 9:52 PM, Sat 12:38 AM | 41–48 mm | 0 | 11, 5 | – (ran with the issue member only: cache bug, fixed 7 Nov) |

- **80 distinct segments were called "likely" over the 5 cycles; only 5 were named by more than one cycle** (archive `kofn.csv`). The HRRR moved the storm core around the district from cycle to cycle, and the list followed it.

## 2. What fell (MRMS gauge-corrected radar, 5 Nov 20Z + 48 h, the 8 forecast boxes)
- **District 3 mean ≈ 31 mm in 48 h.** The south was much wetter than the north.
- **Area maximum: 96 mm storm total** (Bellingham–Mendon–Milford–Uxbridge box). The highest 1-h cell was **25 mm** (Franklin–Grafton–Holliston box; 24.5 mm in the Bellingham box), with two bursts of about 40 mm in 6 h.
- **Leominster / Clinton–Berlin–Lancaster box: max 56 mm, mean 43 mm; peak 1-h cell 17 mm.** Fitchburg–Gardner: max 30 mm, peak 1 h 11 mm.
- Rivers rose but stayed in their banks: North Nashua near Leominster 143 → 325 cfs; Blackstone at Millbury 119 → 928 cfs; Woonsocket 1,330 cfs at 3.6 ft.

## 3. What happened
- **No reports of flooded or closed roads in District 3.** Looked in: NWS Local Storm Reports (0 of 210 Massachusetts rows), NWS flood /
  flash-flood warnings (none covered the district; they were for Barnstable, Bristol and Plymouth), the MassDOT roadway-events feed (0 of
  23 entries), NCEI Storm Events (0), news (none found).
- SeeClickFix had 6 reports, all in Worcester (Salisbury St, Guild Rd, Pleasant St, Trinity Ave, Clark St): blocked catch basins / standing
  water at drains, low quality, not closures. None was on a road the model named.

## 4. Scoring (the same way as the 12–13 Nov storm)
| | reported flooded | not reported |
|---|---|---|
| **forecast "likely"** (any cycle) | hits **0** | false alarms: **85 cycle-road calls** in 5 cycles (22 + 10 + 25 + 22 + 6), **80 distinct segments** |
| **not forecast** | misses **0** | correct-quiet: the rest of the district |
| **model on the observed radar rain (replay, live rules)** | hits **0** | **8 segments**: Ash St, Clinton (2); East Park Terrace, Shrewsbury St (2), Cambridge St, Fantasia Dr, MLK Jr Blvd, Worcester |

**Verdict: false alarm, mostly from the rain forecast.** The forward-test ledger records it as "false alarm" (`RESULTS.md`).
- North and west (Leominster, Fitchburg, Pepperell, Holden): the HRRR was about twice too wet. With the radar rain the model closes nothing there.
- South (Bellingham–Franklin): storm totals were about right (104 vs 96 mm), but the members packed the rain into one 50 mm / 6 h burst. With the
  observed bursts (≈ 40 mm / 6 h) the model closes nothing.
- Worcester: **not** the rain. The model floods 6 low streets (under / beside the rail lines) with the observed rain too; nobody reported
  them. Either unreported street ponding or no storm drains in the model; storm-drain sinks were tested twice and rejected, so this needs
  evidence (city 311, cameras) before any change.

## 5. One slide (≤ 5 bullets; figure `fig/storm_2026-11-06_slide.png`)
- **The system ran and warned in advance:** the rain gate fired from Wed 4 Nov evening; 7 forecast cycles were published, 3 of them the day before the rain.
- **It over-called:** 5 cycles listed 6–25 "likely" closures each, in a different part of the district each time; **no road flooding was reported** in District 3.
- **The main cause was the rain forecast:** HRRR put the storm too far north and west and too intense; with the real radar rain the same model closes nothing in Leominster, Fitchburg or Bellingham.
- **What we changed because of it:** start-state water no longer counts as flooding (5 Nov), the rise rule (8 Nov), more robust publishing; with all of them, the replay on real rain closes 8 segments (6 in Worcester), all unreported.
- **The next storm (12–13 Nov, 20 mm) was a correct quiet:** no closures forecast, none reported, radar replay 0.

## 6. Likely advisor questions
1. *"Did you check the critical locations on Friday?"* The forecast lists existed (Leominster Water St / Depot Sq on Thursday 3:33 PM and Friday 2:25 PM ET); no field check is recorded in the log. Next time: a short "check list" export (top roads by k-of-8, with map links) the day before.
2. *"Isn't 80 false-alarm roads a failure?"* For this storm, yes, and it is recorded as one. But the radar replay separates the two error sources: almost all of it was the rain forecast, which no road model can fix; what remains (8 segments, 6 in Worcester) is the model's own over-prediction, and it is small.
3. *"Why didn't the ensemble protect you?"* "2 of 8" kept calls where only 2 members agreed. A stricter "3 of 8" would have cut the lists to 0–8 roads per cycle, but on 7 past storms it loses 2 of 29 real sites, so the rule was not changed. Checking whether members agree on **where** the heavy rain falls is the better fix; it is proposed, not yet tested.
