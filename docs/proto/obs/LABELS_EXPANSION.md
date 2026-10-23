# Label expansion: more District 3 storms and road-level sites (2026-10-23)

The flash-flood road-closure model has been checked on 9 MRMS-Pass2 storms with about 170 labelled sites, and only 29 sites
in the pooled out-of-sample set. That is too few for stable recall or skill numbers. This expansion adds storms and sites from
public, citable records for MassDOT Highway District 3 between 2018 and 2026. It also fixes some coordinates in the existing label files.

Built by `proto/labels_expand.py`, with geocoding by `proto/label_geocode.py` on GitHub Actions (`.github/workflows/label_geocode.yml`).
Re-run with `python proto/labels_expand.py queries | build | catalog | report`.

## Result in one table

| id | date (local) | era | box EPSG:26986 | t0 UTC / h | label rows | in box | exact / approx / town (in box) | types (in box) | sources (all rows) |
|---|---|---|---|---|---|---|---|---|---|
| may2018 | 2018-05-15 | iem | 169000,881000,189000,901000 | 2018-05-15T14:00Z / 18 | 5 | 3 | 2 / 1 / 0 | closed 1, impassable 1, flooded 1 | LSR 3, StormEvents 2 |
| aug2018b | 2018-08-11 | iem | 167000,894000,187000,914000 | 2018-08-11T08:00Z / 22 | 4 | 3 | 0 / 3 / 0 | flooded 2, impassable 1 | LSR 3, StormEvents 1 |
| sep2018 | 2018-09-18 | iem | 156000,913000,176000,933000 | 2018-09-18T06:00Z / 18 | 5 | 5 | 2 / 3 / 0 | flooded 5 | StormEvents 3, LSR 2 |
| sep2018w | 2018-09-18 | iem | 179000,883000,199000,903000 | 2018-09-18T07:00Z / 18 | 4 | 4 | 3 / 1 / 0 | impassable 3, flooded 1 | StormEvents 4 |
| sep2018m | 2018-09-18 | iem | 188000,863000,208000,883000 | 2018-09-18T08:00Z / 18 | 4 | 4 | 1 / 3 / 0 | impassable 3, flooded 1 | StormEvents 3, LSR 1 |
| sep2018b | 2018-09-26 | iem | 149000,914000,169000,934000 | 2018-09-26T18:00Z / 18 | 7 | 7 | 1 / 5 / 1 | flooded 4, impassable 3 | LSR 5, StormEvents 2 |
| jul2019 | 2019-07-06 | iem | 157000,874000,177000,894000 | 2019-07-06T14:00Z / 18 | 5 | 5 | 2 / 3 / 0 | flooded 3, impassable 2 | StormEvents 5 |
| aug2019 | 2019-08-07 | iem | 162000,871000,182000,891000 | 2019-08-07T19:00Z / 18 | 2 | 2 | 1 / 1 / 0 | impassable 1, flooded 1 | StormEvents 2 |
| sep2019 | 2019-09-02 | iem | 183000,865000,203000,885000 | 2019-09-02T14:00Z / 18 | 4 | 2 | 2 / 0 / 0 | impassable 1, closed 1 | StormEvents 4 |
| jun2020 | 2020-06-28 | iem | 190000,859000,210000,879000 | 2020-06-28T14:00Z / 18 | 8 | 6 | 2 / 4 / 0 | flooded 4, impassable 2 | StormEvents 8 |
| jun2020b | 2020-06-28 | iem | 152000,914000,172000,934000 | 2020-06-28T16:00Z / 18 | 6 | 5 | 1 / 3 / 1 | impassable 3, flooded 2 | StormEvents 5, LSR 1 |
| aug2020b | 2020-08-27 | iem | 166000,877000,186000,897000 | 2020-08-27T11:00Z / 18 | 3 | 3 | 2 / 1 / 0 | flooded 2, impassable 1 | StormEvents 3 |
| jul2021b | 2021-07-17 | aws | 163000,880000,183000,900000 | 2021-07-17T14:00Z / 24 | 4 | 4 | 3 / 1 / 0 | impassable 2, flooded 2 | StormEvents 4 |
| jul2023b | 2023-07-10 | aws | 161000,886000,181000,906000 | 2023-07-10T08:00Z / 18 | 4 | 2 | 1 / 1 / 0 | impassable 1, flooded 1 | LSR 3, StormEvents 1 |
| jul2023c | 2023-07-16 | aws | 166000,915000,186000,935000 | 2023-07-16T07:00Z / 18 | 5 | 4 | 0 / 4 / 0 | flooded 2, impassable 1, washout 1 | StormEvents 2, news 2, LSR 1 |
| jul2023d | 2023-07-21 | aws | 148000,904000,168000,924000 | 2023-07-21T15:00Z / 18 | 3 | 2 | 0 / 2 / 0 | impassable 1, flooded 1 | LSR 3 |

**New storms: 16 boxes, from 13 storm days in 2018–2023.** Florence on 18 Sep 2018 hit three separate areas and has three boxes; 28 Jun 2020 has two.
They hold 73 label rows, 61 of them inside the storm's box. **59 of those are road-level** (`exact` or `approx`) and the
other 2 are town-level. 12 of the road-level in-box sites are in the 4 storms on MRMS Pass2/AWS. The other 12 boxes are `era: iem` (before Oct 2020).

**Additions to existing storms:** five news sites, plus one Storm Events row that the first parser missed (aug2020 Washington Square, event 916327).


| existing storm | rows added | added rows inside the catalogue box | exact / approx / town |
|---|---|---|---|
| aug2020 | 1 (Washington Square) | 1 | 0 / 1 / 0 |
| aug2021 | 1 (Sever Street) | 1 | 0 / 1 / 0 |
| aug2026 | 3 (Merriam Avenue, Route 2, Granite Street) | 3 | 0 / 3 / 0 |
| jul2018 | 1 (Quinsigamond Avenue) | 1 | 0 / 1 / 0 |

**Totals.** 59 + 6 = **65 new road-level sites inside model boxes.** Counting only the 5 MRMS-Pass2 (AWS) storms, that is 12 + 5 = 17:
the 4 new storms, plus the additions to `aug2021` and `aug2026`. The other additions, to `jul2018` and `aug2020`, are IEM-era storms.
In the new storms the type mix is 36 `flooded`, 31 `impassable`, 5 `closed` and 1 `washout` (Birch St). The additions to existing storms include 1 `other_damage`. So almost every new site is a `flood_closure`-group label, and `culvert_washout` gains only one.

## How the storms were found

1. **Candidate storms.** I used the statewide pull already in `docs/proto/obs/catalog/`: every IEM Local Storm Report (NWS Boston/Norton)
   of type FLOOD, FLASH FLOOD or HEAVY RAIN for 2014–2026, and every NCEI Storm Events row of type Flash Flood, Flood or Heavy Rain.
   I kept 2018 onward and reports within 5 km of the District 3 extent (`D3_BOX`), and grouped them into storms at gaps longer than 18 h.
   I read every group with 2 or more road-related reports.
2. **Selection.** A storm was added when a 20 × 20 km box holds at least 2 road-level sites, with a named road, in District 3 towns,
   from flash-flood (convective or tropical) rain. This is a lower bar than the first catalogue's 5 sites. The reason is that the model is scored per
   site, and every new box adds positive sites plus thousands of negative road segments. Storms with 2–3 sites are flagged "Small" in
   `catalog.json` `note`, so they can be left out of per-storm statistics.
3. **What was left out**, with the reason:
   - 2020-12-25 Oxford/Sutton: rain on snowpack, not a flash flood.
   - 2024-01-10 Worcester Route 20: winter rain and snowmelt, one site.
   - 2024-06-26 Worcester Route 20 near Grafton St: one site.
   - 2026-07-29 Worcester Grafton St: one site.
   - 2022-08-26 Worcester Greenwood St: one site.
   - 2021-07-18 Warren/West Warren and Belchertown/Ware: Warren has almost no segments in `docs/graph_segments.json`, and the rest is District 2.
   - 2025-06-06 Orange/Athol: District 2.
   - 2018-08-04 Millbury/Oxford: 2 sites, one of them trees and wires down, not flooding.
   - 2018-04-16 and 2018-11-03: long-duration rain on wet ground with widely spread reports.
   - 2019-10-16/17 nor'easter: WHDH names Harding St and Kansas St in Worcester, but there are no NWS reports, so only 2 sites, both news-only.
4. **2024–2026 is thin.** After 2023 the NWS record has no District 3 storm with more than one road report, except the existing `aug2026`.
   I searched the news for 2024–2025 and found nothing that adds a storm. I did not pad the catalogue to reach the target.

## How the sites were labelled

- **One row per road site.** NWS reports often say the same thing twice: an LSR and a Storm Events row a few minutes apart. Those count as
  one site. The row cites the Storm Events event page (the longer text with the precise point) when there is one, and otherwise the IEM LSR
  page for that hour. A report that names several separate places (for example "Quaker Highway ... Also, Route 122") becomes one row per road.
- **News.** These sources add road sites to four storms: CBS Boston for Fitchburg on 16 Jul 2023, CBS Boston and Boston 25 for Leominster/Fitchburg
  on 3 Aug 2026, Boston 25 for Worcester on 17 Jul 2018, and WHDH for Worcester on 19 Aug 2021. News rows have `source=news` and
  `time_quality=day`, with `time_local` set to noon of the storm day, because the stories give no clock time. Of the other stories I read
  (CBS, NBC Boston, WHDH, Boston 25, WWLP, Patch and the Boston Globe, 2016–2026), most repeat the NWS sites or name none. I used no paywalled or social-media-only source.
- **Columns.** The columns are the same as the catalogue label files: `id,name,road,town,type,time_local,time_quality,lon,lat,coord_quality,source_url,quote,source`.
  `time_local` is EDT, because all these storms fall between May and September. It is converted from LSR `VALID` (UTC) or from Storm Events `BEGIN_DATE_TIME`, which is in EST (UTC−5).
  `time_quality=report` means the road was already flooded at that time. `quote` is copied verbatim from the source, typos included.
- **type** comes from the report wording:
  - `closed`: closed or shut.
  - `impassable`: impassable, or cars stuck, stranded or trapped.
  - `washout`: the pavement was destroyed (Birch St, Fitchburg, 2023).
  - `other_damage`: buckled pavement (Granite St / Helena St, Leominster, 2026).
  - `flooded`: everything else.

  Reports about basements, yards, a college lobby or manhole covers with no road named were not used.
- **Out-of-box rows.** Sites from the same storm that fall outside its 20 × 20 km box stay in the file, for example Milford, Marlborough and Franklin.
  `prototype.py` skips them, because it only matches labels inside the run box. `catalog.json` `counts.road_sites_named` counts only the in-box sites.

## Geocoding

The goal was to put each point where the report says. `coord_quality` follows the existing convention:
- `exact`: the named intersection, or a road crossing a railway or river, placed where the two features meet, within 80 m.
- `approx`: on the named road, at the vertex nearest the NWS point. Storm Events points have 4 decimals and are often the reported spot. If the report gives no place along the road, the point is the road's middle vertex.
- `town`: the report's own point, used only when the road could not be found.

There were two geocoders, tried in this order. Every site's method and distance is in `labels_expansion_sites.json`.
1. **OpenStreetMap through Overpass**, run on Actions: highway ways by name or by `ref` (`US 20`, `MA 9`, `I 290`), waterways by name, and `railway=rail`.
   For a pair of features, it uses the closest approach. When there are several crossings, it picks the one nearest the NWS point.
   Overpass was slow from Actions: 502 errors and timeouts on all three public servers. So the job runs as 6 parallel shards, and any query it did not finish falls through to geocoder 2.
2. **`docs/graph_segments.json`**: the repository's MassGIS-derived road network, the same one the model scores. Named routes in it carry
   `Route N` names, and several local streets are missing (for example Royalston St in Fitchburg, Timer St in Natick, and Timpany Blvd in Gardner).

## Fixes to existing labels (changelog)

Machine-readable: `labels_fix_changelog.json` (before / after / moved metres / method). Coordinates moved only where a geocoder placed the
named intersection within 80 m (→ `exact`) or found the named road for a row that was town-level (→ `approx`). Name fixes correct
artefacts of the earlier automatic road-name parser. **Row ids are unchanged, and no row was deleted.**

| file | id | coord_quality | moved (m) | name change | method |
|---|---|---|---|---|---|
| labels_aug2018_natick.csv | AUG2018-05 | town → approx | 527 | Subury Street: flooded → Thompson Street at Sudbury Street: flooded (3 ft) | graph_segments pair gap 213 m |
| labels_aug2018_natick.csv | AUG2018-21 | town → town | 0 | Terrance Avenue, Weathers Field Road: flooded → Terrace Avenue at Wethersfield Road: flooded (3 ft) | names only (OSM did not confirm the point) |
| labels_aug2021_worcester.csv | W011 | approx → exact | 45 |  | OSM intersection, gap 0.0 m, 44 m from the old point |
| labels_aug2023_metrowest.csv | AUG2023-04 | approx → exact | 0 |  | OSM intersection, gap 0.0 m, 3 m from the old point |
| labels_aug2023b_millbury.csv | AUG2023b-04 | approx → approx | 442 | Municiple Drive: flooded → Municipal Drive: flooded | OSM road vertex (road 375 m) |
| labels_jul2018_worcester.csv | JUL2018-01 | approx → approx | 0 | Worcester Brought Street, Chandler Street, Murray Avenue: flooded → Chandler Street at Murray Avenue: flooded (1 ft) | names only (OSM did not confirm the point) |
| labels_jul2018_worcester.csv | JUL2018-02 | town → approx | 1120 | Unnamed road: flooded → Auburn Street: flooded | OSM road vertex (road 1945 m) |
| labels_jul2023_worcester.csv | JUL2023-03 | approx → exact | 17 | Franklin Street: flooded → Franklin Street by the railroad tracks: flooded | OSM intersection, gap 23.1 m, 14 m from the old point |
| labels_oct2016_worcester.csv | OCT2016-08 | town → approx | 1377 | Unnamed road: impassable → Bridge Street: impassable | graph_segments road centroid vertex |
| labels_oct2016_worcester.csv | OCT2016-09 | approx → exact | 2 |  | OSM intersection, gap 0.0 m, 2 m from the old point |
| labels_oct2016_worcester.csv | OCT2016-13 | approx → approx | 0 | Taylor Boulevard, Summer Street: closed → Major Taylor Boulevard, Summer Street: closed | names only (OSM did not confirm the point) |
| labels_oct2016_worcester.csv | OCT2016-17 | approx → exact | 107 |  | OSM intersection, gap 0.0 m, 102 m from the old point |
| labels_oct2016_worcester.csv | OCT2016-20 | approx → exact | 0 |  | OSM intersection, gap 0.0 m, 2 m from the old point |
| labels_oct2016_worcester.csv | OCT2016-29 | town → approx | 824 | Mlk Boulevard: flooded → MLK Boulevard at the railroad underpass: flooded | graph_segments road vertex 1083 m from NWS point |
| labels_sep2021_worcester.csv | SEP2021-05 | approx → exact | 600 | Southwest Cutoff, Grafton Street: impassable → Southwest Cutoff (Route 20) at Grafton Street (Route 122): impassable | OSM intersection, gap 1.8 m, 600 m from the old point |
| labels_sep2021_worcester.csv | SEP2021-07 | approx → approx | 0 | Exact Street: washout → Unknown road: washout (exact street unknown) | name/road corrected only |
| labels_sep2022_webster.csv | SEP2022-03 | approx → approx | 0 | That West Main Street, Mason Lane, Worcester Road: closed → West Main Street (Route 197) at Mason Lane; Worcester Road (Route 12): closed | names only (OSM did not confirm the point) |

Problems found but left alone, so the evaluation sets stay comparable:
- **Duplicate sites.** Each pair below is one site, entered once from the LSR and once from Storm Events:
  - JUL2018-03 and JUL2018-04: Route 20 at Southbridge St, Auburn.
  - JUL2021-01 and JUL2021-06: Southgate St at Southbridge St, Worcester.
  - SEP2022-03 and SEP2022-04: Worcester Rd, Webster.
  - AUG2018-01 and AUG2018-02: Dunster Dr, Stow.

  A per-site recall counts each of these twice. Collapsing them changes the denominators, so that choice is left to the scoring code.
- **List reports.** AUG2015-06, AUG2020-04 and SEP2021-01 are reports that list several streets, each kept as one row.

## Caveats

- **Reporting bias.** Labels exist where someone reported. Worcester city streets, state routes and places with active amateur-radio
  spotters are over-represented. Rural towns (Templeton, Hubbardston, Spencer) appear only when a road was badly affected. An unlabelled
  segment is not a known dry one, so precision against these labels is a lower bound.
- **Time.** The time is when the report was made, not when flooding began. News rows are day-level only.
- **Positions.** `approx` points on long roads (John Fitch Hwy, Lunenburg St, Quinsigamond Ave, Route 2) can be 1 km or more from the actual
  flooded spot. Score those by road name (the loose rule), as the README for aug2021 already says.
- **MRMS.** 12 of the 16 new storm boxes are before 14 Oct 2020, so MRMS `MultiSensor_QPE_01H_Pass2` does not exist for them. They are
  `era: iem` (IEM GaugeCorr) and need the IEM reader before w9 can run them. `submit_catalog.sh` picks up only the `era: aws` storms:
  `jul2021b`, `jul2023b`, `jul2023c` and `jul2023d`.
- **Small storms** (2–3 sites) add little to per-storm metrics. They help pooled site-level recall and the negative set.
- **Observed data for the new storms.** Gauges, LSR and Storm Events files come from `obs_catalog.yml` with `mode=fetch` and `only=<new ids>` (`--only` was added to
  `proto/obs_catalog.py` for this). See the status line at the end.

## Sources

- NWS Local Storm Reports (WFO BOX) through IEM: `https://mesonet.agron.iastate.edu/lsr/` (each row links to its hour window).
- NOAA NCEI Storm Events Database event pages: `https://www.ncdc.noaa.gov/stormevents/eventdetails.jsp?id=<EVENT_ID>`.
- News:
  - CBS Boston, 16 Jul 2023, Fitchburg flash flooding: https://www.cbsnews.com/boston/news/fitchburg-massachusetts-flash-flooding/
  - CBS Boston, 3 Aug 2026: https://www.cbsnews.com/boston/news/leominster-shirley-storm-damage-rain-wind/
  - Boston 25, 3 Aug 2026: https://www.boston25news.com/news/local/flooding-leaves-massachusetts-roads-impassable-severe-storms-move-through/OO2KJN6FTNH6XI7HSTHMGA5AVA/
  - Boston 25, 18 Jul 2018: https://www.boston25news.com/news/severe-weather-leaves-several-roads-flooded-throughout-worcester-county/792274888
  - WHDH, 19 Aug 2021: https://whdh.com/news/flash-flooding-leaves-dozens-of-motorists-stranded-in-submerged-cars-in-worcester/
- Road geometry:
  - OpenStreetMap contributors (ODbL), through Overpass.
  - MassGIS / MassDOT road centrelines, through `docs/graph_segments.json`.

## Status at hand-off (2026-10-23) and how to refresh

- **Geocoding.** Two Overpass passes (6 shards each) placed 82 of 100 queries. The road-network fallback placed most of the rest.
  Four sites are still `town` at the NWS point:
  - in the box: Templeton Boulder Dr (sep2018b) and Gardner Timpany Blvd (jun2020b);
  - outside the box: Gardner Ripley St and Douglas Gilboa Rd (both jul2023b).

  To refresh after another `label_geocode.yml` run, run `python proto/labels_expand.py build && python proto/labels_expand.py catalog && python proto/labels_expand.py report`.
  The build is idempotent. It rewrites the new label files, replaces the rows it appended to existing files (matched by id prefix) and re-applies the fixes.
- **Observed data.** `obs_catalog.yml` ran with `mode=fetch` and `only=<16 new ids>`. It committed `gauges_<id>.json`, `lsr_<id>.csv`, `stormevents_<id>.csv`
  and the MRMS archive check for the new storms, and `catalog` copied the in-box gauges into `catalog.json`.
- **GPU runs.** `bash proto/turing/submit_catalog.sh 20 jul2021b jul2023b jul2023c jul2023d` submits the 4 new storms in the AWS era.
