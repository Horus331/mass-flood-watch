# Ground-truth labels: 19 Aug 2021 flash flood (remnants of Fred), Worcester area

File: `labels_aug2021_worcester.csv` (14 rows). This is the second test storm for the closure model. The model was tuned on Leominster (Sept 2023, Nashua basin). This storm is in MassDOT District 3, in a different basin: the upper Blackstone (Middle River, Kettle Brook and Beaver Brook through Worcester), plus one French River site in Oxford and one site in Westborough, about 17 km east.
Columns are the same as `labels_sep2023_leominster.csv`: `id,name,road,town,type,time_local,time_quality,lon,lat,coord_quality,source_url,quote`.

## Storm

- **When.** Thursday 19 Aug 2021, roughly 06:00 to 12:00 EDT (10–16 UTC). Patch: "An estimated 3 inches of rain fell in Worcester between about 6 a.m. and noon". The Globe quotes forecasters: "Between 3 and 4 inches of rain had fallen there by about 10:30 a.m." The city issued its flash-flood alert at about 10:40.
- **How much rain.** Worcester 3.18 in (Boston Globe). NWS BOX: "Higher totals of 3 to 4 inches were more common from the Hartford area northeast to Worcester." Worcester firefighters took about 120 emergency calls in six hours (Boston 25).
- **Suggested model run.** EPSG:26986 box `168000,875000,188000,895000` (20 × 20 km). It holds 13 of the 14 labels; Westborough W014 (x ≈ 192100) is outside. Start `2021-08-19T09:00Z`, run 18 h. MRMS `MultiSensor_QPE_01H_Pass2` is on AWS for this date, since the archive starts Oct 2020.
- **USGS gauges in the box:** 01109730 Blackstone R at Millbury, 01110000 Quinsigamond R at North Grafton, 01124294 French R at North Oxford. Fred was a short urban storm. The water-year-2021 annual peak at 01109730 (3,680 cfs) and at 01110000 came two weeks later, from Ida on 2 Sept 2021, so the river gauges show only a modest Fred response.

## Counts

| type | n |
|---|---|
| flooded | 9 |
| impassable | 3 |
| closed | 2 |

By town: Worcester 11, Auburn 1, Oxford 1, Westborough 1.
coord_quality: exact 8, approx 5, town 1. time_quality: approx 1, day 13.

## How fields were filled

- **time_local** (EDT). Only W001 has a clock time: 11:59, the time of the Turn to 10 report, so it is `approx`. The rain fell between 06:00 and 12:00, and every source places the flooding on Thursday morning. All other rows are `day`. I could not reach the NWS Local Storm Reports for this date (IEM, kamala.cod.edu and wx1box report PDFs were blocked from this sandbox), and they would give exact times.
- **lon/lat** come from `docs/graph_segments.json`, the same way as for Leominster. No external geocoder could be reached.
  - Intersections and bridges use the closest approach of the two named roads: Route 20 × Route 122 (Grafton St) 17 m, Cambridge × Kansas 24 m, Quinsigamond × Lamartine 41 m, William × Somerset 10 m, East Central × I-290 40 m, Millbrook × I-190 30 m, Route 30 × Route 9 (Westborough) 39 m. Those are `exact`. Enid × Commonwealth is 80 m, so it is `approx`.
  - Southbridge St, McKeon Rd and Glennie St sit at the road vertex nearest the road centroid, so they are `approx`. **Southbridge St (about 1.7 km of segments) and McKeon Rd (about 0.9 km) can be several hundred metres off**, so match those by road name.
  - Auburn W012 is "in front of the Auburn Police Station", which is 416 Oxford St North. The point is the Oxford St North centroid (`approx`, could be up to about 1 km off).
  - Oxford W013 is "the area of the police station" (503 Main St / Route 12). It uses the town-centre point (`town`).
- **quote**: 25 words or fewer, copied from the source. For the NWS monthly report rows, the quote is the street entry as listed.

## Sources

- NWS Boston/Norton monthly hydrologic summary, Aug 2021 (Fred street list and rainfall), hosted by RI DEM: https://dem.ri.gov/climate/documents/monthly-conditions-2108.pdf
- Patch Worcester, 19 Aug 2021, 15:40: https://patch.com/massachusetts/worcester/photos-fred-floods-worcester-shutting-down-streets-buildings
- Turn to 10, 19 Aug 2021, 11:59: https://turnto10.com/news/local/floodwater-submerges-4-cars-on-route-20-in-worcester
- Boston 25, 19 Aug 2021, 18:37: https://www.boston25news.com/news/local/father-carries-daughter-safety-after-worcester-flash-flooding/RLJEBQSXNVCA7NVWKZA5KCXCZY
- NBC Boston, 19 Aug 2021: https://www.nbcboston.com/news/local/4-people-rescued-from-cars-submerged-under-water-on-rt-20-in-worcester/2470848/
- CBS Boston photo gallery, 19 Aug 2021: https://cbsnews.com/boston/pictures/august-19-flooding-across-central-eastern-massachusetts
- CBS Boston, 19 Aug 2021: https://www.cbsnews.com/boston/news/worcester-thunderstorms-flood-water-route-20-cars-submerged/
- Boston Globe, 19 Aug 2021 (rain totals, court and pool closures): https://www.bostonglobe.com/2021/08/19/metro/after-wild-weather-day-caused-by-fred-region-braces-tropical-storm-henri and https://www.bostonglobe.com/2021/08/19/metro/remnants-fred-sweep-into-mass-thursday-bringing-rain-chance-thunderstorms
- Context on the Route 20 / Grafton St underpass: MassDOT District 3 calls it the "worst location" for flooding in the district, flooding 5–6 times a year (via Yahoo News): https://news.yahoo.com/5-5m-fix-worcester-route-154837094.html

## Caveats

- **Mostly urban drainage flooding, unlike Leominster.** Leominster's labels are dominated by culvert failures and washouts. These sites are underpasses and low streets where storm drains were overwhelmed. Rows W001/W002, W003, W008 and W010 are all rail or highway underpasses. A flood-depth model with no storm-sewer term may score these differently. That difference is part of what this test should show.
- **Route 20 / Grafton St is a known repeat site.** It floods 5–6 times a year, so a model can get it right from terrain alone. Report recall with and without W001/W002.
- **Left out:**
  - The Cambridge St minivan (Boston 25, NBC). It is most likely the same spot as W003 (Cambridge × Kansas railroad bridge).
  - The Big Y parking lot (store not identified), the Main St court complex and Crompton Park pool, which are not roads.
  - Canton St × Quinsigamond Ave (Globe photo of police inspecting). It is weak evidence and lies about 400 m from W004.
  - Clinton "streets flooded" (no street named, and mixed with tornado damage).
  - Sudbury, Newton, Somerville and Peabody, which are outside District 3 or the box.
- **The NWS street list** (W004–W011) comes from the NWS monthly summary, so it has no times and no detail on depth or closure. These rows are typed `flooded`.
