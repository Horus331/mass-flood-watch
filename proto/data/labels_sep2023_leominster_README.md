# Ground-truth labels: 11–12 Sept 2023 flash flood, Leominster area

File: `labels_sep2023_leominster.csv` (93 rows). Study box: lon -72.0 to -71.6, lat 42.42 to 42.68. All rows fall inside it.
Columns: `id,name,road,town,type,time_local,time_quality,lon,lat,coord_quality,source_url,quote`.

## Counts

| type | n |
|---|---|
| culvert_failure | 29 |
| other_damage (dams, drainage systems, retaining wall, buckled pavement, lane loss) | 18 |
| flooded | 14 |
| closed | 11 |
| washout | 8 |
| impassable | 7 |
| sinkhole | 3 |
| bridge_damage | 3 |

By town: Leominster 84, Fitchburg 3, Princeton 3, Shirley 2, Sterling 1. No usable road reports were found for Lunenburg, Westminster or Lancaster. The only Lunenburg report is house and garage flooding at 59 Goodrich St and 81 Turkey Hill Rd at 21:02; it is left out because it is not a road.

coord_quality: exact 27, approx 64, town 2. time_quality: exact 26, approx 14, day 53.

## How fields were filled

- **time_local** (EDT). `exact` is a time-stamped spotter or emergency report from the WX1BOX SKYWARN log, which matches the NWS storm-report table in the state Disaster Recovery Action Plan. `approx` is the time a news update or the mayor's list reported the condition. Those reports came on the morning of 12 Sept, so the condition started earlier, on the evening of the 11th. `day` means only the date is known. All CDBG-DR damage sites are dated 2023-09-11, and the city puts the main inundation between 16:30 and 22:30 on 11 Sept.
- **lon/lat**. No geocoder could be reached: Nominatim, ArcGIS and Photon are blocked by the sandbox proxy. Coordinates come from repository data instead.
  - Street intersections: closest approach of the two named streets in `docs/graph_segments.json`. Most are within 50 m, so they are marked `exact`.
  - Bridges and stream culverts: NBI and stream-crossing points in `docs/network/crossings_all.json`. Examples are the Route 13 Main St bridge over the North Nashua (L080021LMDOTNBI), the Mechanic St bridge, and the Fall Brook crossings at Pleasant, Decicco, Grant, Hardy and Wachusett.
  - `approx`: the road is right but the position along it is uncertain. In these cases the coordinate is either the road vertex nearest the road's centroid, or a nearby proxy structure. **Road-centroid points can be 0.5–1.5 km off on long roads** (Pleasant St, Elm St, Litchfield St, Main St, Willard St, Granite St), so match them by road name and town, not by distance.
  - `town`: town-centre coordinate. This applies to Shirley Hill Road and the Distributing Reservoir Dam.
- **quote**: up to 20 words copied from the source. For CDBG-DR rows the quote is the site name exactly as it appears in the plan's Leominster project table.

## Sources

- WX1BOX SKYWARN report log, 9/11/23 (times): https://wx1box.org/wp-content/uploads/2023/09/reports_9_11_23.pdf
- MA CDBG-DR Action Plan, DR-4780 (Leominster table of 62 sites): https://www.mass.gov/doc/cdbg-dr-action-plan/download
- MA Disaster Recovery Action Plan: narrative, NWS storm-report table and photo captions: https://www.mass.gov/doc/disaster-recovery-action-plan/download
- MassDOT Leominster Emergency Recovery hearing handout, 1 Apr 2025: https://www.mass.gov/doc/massdot-hearing-handout-leominster-4125/download
- MassDOT District 3 report, 20 Sep 2023: https://www.mass.gov/doc/highway-administrators-report-presented-to-the-board-on-september-20-2023/download
- CBS Boston, mayor's road-closure list (updated 12 Sep, 10:49): https://www.cbsnews.com/amp/boston/news/leominster-flooding-road-closures/
- Boston Globe live updates, 12 Sep: https://www.bostonglobe.com/2023/09/12/metro/mass-flooding-leominster-live-updates/
- WHDH (11 and 12 Sep), WBUR (12 Sep), Boston 25 (articles and photo gallery), AP via Yahoo, CBS, Patch, NBC Boston and Fox Weather. The URLs are in the CSV.

## Caveats

- **Duplicates were removed.** One location with the same failure type is kept once, using the best-timed source. These were dropped:
  - CDBG rows for Lancaster St (Malburn–Sage), the Pleasant St culvert at Colburn and the Mechanic St Bridge. The timed or more specific rows are kept.
  - The AP report of a Route 13 rail-underpass closure. It is covered by L033 (Main St & Hamilton St).
  - Extra Route 2 reports and the MassDOT notes on Union St and the Lancaster St retaining wall.

  The same location can still appear under two types, such as `closed` and `washout` at Pleasant & Pond.
- **Route 2 timing conflicts.** WHDH says state roads were closed by about 19:50 and that westbound stayed closed into 12 Sep. Boston 25, quoting MassDOT, says all lanes reopened just before 06:30 on 12 Sep. Patch says both sides reopened late Monday night. "Exit 99" is taken to be the Route 12 interchange: the 20:00 report says "near Route 12", and MassDOT pumped water at the Route 2 / Route 12 interchange. This is an inference, so the point is marked approx.
- The Globe's "Route 3 bridge over the North Nashua River" (12:28, 12 Sep) is read as a typo for Route 13. CBS and the MassDOT District 3 report both name the Route 13 bridge.
- **The CDBG-DR table gives no damage mechanism.** Type comes from the site name: "Culvert" becomes culvert_failure, and "Drainage"/"Dam" become other_damage. Some of these sites may have been damaged without being closed. Sewer trunklines, brook bank projects, the parking area at 188-210 Central St, "Behind Doyle Field" and the West St water-tank access road are left out because they are not public-road locations.
- "Imperial Drive" from the CDBG table is placed on Imperial Avenue, the only similar name in the road network. Wilder Brook and the railroad crossing on Litchfield St have no crossing record, so they sit at road centroids.
- Barrett Park Pond Dam is placed at Colburn St (approx), on the basis of the plan's "Barrett Park/Colburn Pond" wording. Brooks Pond Dam is placed on Brooks Pond Rd, west of Route 12. Both are dams, not roads.
- **Fitchburg rain totals disagree.** NWS reported 5.10 in and the WX1BOX log 2.95 in. Fitchburg also had a separate flash flood in Aug 2023, so August Fitchburg articles were excluded.
- **Not reachable from here:** the IEM/NWS LSR archive and Sentinel & Enterprise or Telegram article pages. The CBS "brooks-pond-dam" and Washington Post pages could only be partly read. More Fitchburg, Lunenburg or Westminster road reports may exist in those sources.
