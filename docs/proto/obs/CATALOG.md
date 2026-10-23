# District 3 flash-flood storm catalogue

Historical flash-flood storms in MassDOT Highway District 3 (central MA) for training and testing the learned road-closure model.
Machine-readable copy: [`catalog.json`](catalog.json). Built 2026-10-22 by `proto/obs_catalog.py`, run on GitHub Actions through `.github/workflows/obs_catalog.yml`, in two runs:

1. `discover`: every Massachusetts NWS Local Storm Report of type FLOOD, FLASH FLOOD or HEAVY RAIN for 2014–2026 (IEM), plus every NOAA Storm Events row of type Flash Flood, Flood or Heavy Rain. The output is in `catalog/` (`lsr_ma_flood_2014_2026.csv`, 2,677 LSRs; `stormevents_ma_flood_2014_2026.csv`, 958 rows).
2. `fetch`: the per-storm observations, written in the same form as `obs.yml` makes them (`gauges_<id>.json`, `lsr_<id>.csv`, `stormevents_<id>.csv`), plus an MRMS archive check (`catalog/mrms_check.json`).

How storms were picked: I projected the flood reports to EPSG:26986 and kept those within 10 km of the District 3 extent (`sim/colab/lf_domain.py` `D3_BOX`). Reports were grouped into storms, with a new storm starting after a gap of more than 18 h. For each storm I searched for the 20 × 20 km box, with corners on a 1 km grid, that holds the most road-related flood reports. A storm was selected if its box lies in District 3 towns and has at least 5 road-related reports or named road sites.

## A. Storms in the MRMS Pass2 era: AWS `noaa-mrms-pds` `MultiSensor_QPE_01H_Pass2`, first day 2020-10-14 (w9 can run these as is)

| id | date (local) | towns with road reports | box EPSG:26986 | t0 UTC / hours | LSR / StormEvents rows | road reports (dedup) / named road sites | USGS gauges in box, peak Q | max LSR rain total | labels |
|---|---|---|---|---|---|---|---|---|---|
| jul2021 | 2021-07-09 | Worcester, Millbury | 159000,872000,179000,892000 | 2021-07-09T08:00Z / 18 h | 7 / 3 | 6 / 11 | 01109730 Blackstone River 2930 cfs; 01175670 Sevenmile River Near Spencer 62.8 cfs | — | `labels_jul2021_worcester.csv` |
| aug2021 | 2021-08-19 | Worcester | 168000,875000,188000,895000 | 2021-08-19T09:00Z / 18 h | 2 / 2 | 2 / 14 | 01109730 Blackstone River 2420 cfs; 01110000 Quinsigamond River At North Gr 145 cfs | — | existing labels |
| sep2021 | 2021-09-01/02 | Worcester, Millbury, West Boylston | 160000,882000,180000,902000 | 2021-09-01T18:00Z / 24 h | 5 / 3 | 7 / 9 | 01095375 Quinapoxet River At Canada Mil 1250 cfs; 01095434 Gates Brook Near West Boylston 111 cfs; 01109730 Blackstone River 3680 cfs | 5.08 in (Auburn) | `labels_sep2021_worcester.csv` |
| sep2022 | 2022-09-05 | Webster, Southbridge, Oxford | 151000,855000,171000,875000 | 2022-09-05T06:00Z / 18 h | 7 / 3 | 4 / 8 | 01123600 Quinebaug R Bl Westville Dam N 161 cfs | — | `labels_sep2022_webster.csv` |
| jul2023 | 2023-07-14 | Worcester, Holden, East Brookfield | 157000,882000,177000,902000 | 2023-07-14T08:00Z / 18 h | 5 / 3 | 5 / 5 | 01095375 Quinapoxet River At Canada Mil 256 cfs; 01095434 Gates Brook Near West Boylston 52.1 cfs; 01175670 Sevenmile River Near Spencer 95 cfs | — | `labels_jul2023_worcester.csv` |
| aug2023 | 2023-08-08 | Hopkinton, Marlborough, Framingham, Holliston, Natick | 193000,879000,213000,899000 | 2023-08-08T07:00Z / 18 h | 5 / 4 | 5 / 10 | 01098500 Cochituate Bk Bl Lake Cochitua 123 cfs; 01098530 Sudbury River At Saxonville 802 cfs | — | `labels_aug2023_metrowest.csv` |
| aug2023b | 2023-08-18 | Millbury, Oxford, Grafton, Shrewsbury | 165000,874000,185000,894000 | 2023-08-18T05:00Z / 18 h | 4 / 3 | 4 / 6 | 01109730 Blackstone River 1370 cfs; 01110000 Quinsigamond River At North Gr 139 cfs | — | `labels_aug2023b_millbury.csv` |
| sep2023 | 2023-09-11 | Leominster, Fitchburg | 162000,908000,182000,928000 | 2023-09-11T16:00Z / 36 h | 13 / 11 | 14 / 15 | 01094400 North Nashua River At Fitchbur 1540 cfs; 01094500 North Nashua River Near Leomin 5560 cfs; 01095220 Stillwater River Near Sterling 1610 cfs; 01095503 Nashua River 575 cfs; 01096000 Squannacook River Near West Gr 629 cfs; 01096500 Nashua River At East Pepperell 3750 cfs; 01162000 Millers River Near Winchendon 323 cfs; 01162500 Priest Brook Near Winchendon 97.9 cfs; 01163200 Otter River At Otter River 460 cfs; 01172500 Ware River Near Barre 219 cfs | — | existing labels |
| aug2026 | 2026-08-03 | Princeton, Leominster, Lunenburg, Fitchburg | 162000,908000,182000,928000 | 2026-08-03T04:00Z / 18 h | 4 / 0 | 4 / 15 | 01094400 North Nashua River At Fitchbur 1450 cfs; 01094500 North Nashua River Near Leomin 2810 cfs | — | `labels_aug2026_leominster.csv` |

`aug2021` and `sep2023` are the existing test and tuning storms. Their obs files and labels were left unchanged. For `sep2023`, the gauges come from the existing `gauges_sep2023.json`, which covers a larger lon/lat box. One of its Storm Events rows (1121791) is placed in Leominster but its text says Agawam, which looks like an NWS entry error. The box shown is the one with the most reports. Earlier runs used other boxes, for example `150000,905000,170000,925000`.

## B. Storms before October 2020: MRMS only from IEM (`mtarchive.geol.iastate.edu/YYYY/MM/DD/mrms/ncep/GaugeCorr_QPE_01H/`)

`MultiSensor_QPE_01H_Pass2` began with MRMS v12 in October 2020. For these dates IEM has the v11 `GaugeCorr_QPE_01H` (gauge-corrected hourly) and `RadarOnly_QPE_01H`. The check found 48 GaugeCorr files per day. w9 reads only AWS Pass2, so these storms need an IEM GaugeCorr reader before they can run, and they have no `STORMS` entry yet.

| id | date (local) | towns with road reports | box EPSG:26986 | t0 UTC / hours | LSR / StormEvents rows | road reports (dedup) / named road sites | USGS gauges in box, peak Q | max LSR rain total | labels |
|---|---|---|---|---|---|---|---|---|---|
| aug2015 | 2015-08-15 | Natick, Framingham | 193000,873000,213000,893000 | 2015-08-15T16:00Z / 18 h | 14 / 2 | 11 / 17 | 01103280 Charles River At Medway 9.53 cfs | — | `labels_aug2015_natick.csv` |
| oct2016 | 2016-10-21 | Worcester, Clinton, Shrewsbury, Westborough | 171000,888000,191000,908000 | 2016-10-21T15:00Z / 18 h | 43 / 0 | 29 / 35 | 01095220 Stillwater River Near Sterling 90.1 cfs; 01095375 Quinapoxet River At Canada Mil 155 cfs; 01095434 Gates Brook Near West Boylston 86 cfs; 01095503 Nashua River 180 cfs | — | `labels_oct2016_worcester.csv` |
| jul2018 | 2018-07-17 | Auburn, Worcester, West Auburn, Oxford | 155000,872000,175000,892000 | 2018-07-17T12:00Z / 18 h | 10 / 3 | 7 / 10 | 01175670 Sevenmile River Near Spencer 42.5 cfs | — | `labels_jul2018_worcester.csv` |
| aug2018 | 2018-08-08 | Natick, Hudson, Maynard, Stow, Minute Man Arpt | 194000,892000,214000,912000 | 2018-08-08T16:00Z / 18 h | 21 / 3 | 22 / 26 | 01097000 Assabet River At Maynard 321 cfs; 01098500 Cochituate Bk Bl Lake Cochitua 55.2 cfs; 01098530 Sudbury River At Saxonville 436 cfs | 3.58 in (Maynard) | `labels_aug2018_natick.csv` |
| aug2020 | 2020-08-23 | Worcester | 157000,872000,177000,892000 | 2020-08-23T14:00Z / 18 h | 9 / 5 | 6 / 10 | 01175670 Sevenmile River Near Spencer 21.1 cfs | — | `labels_aug2020_worcester.csv` |


## C. Storms added by the label expansion (2026-10-23)

These were added from the same NWS LSR and Storm Events pull plus news reports, with a lower bar: at least 2 road-level sites in the box.
The method, sources, per-storm counts, geocoding and caveats are in [`LABELS_EXPANSION.md`](LABELS_EXPANSION.md). Storms with 2–3 sites are marked "Small" in `catalog.json` `note`.
`era: aws` storms run as is through `proto/turing/submit_catalog.sh`. `era: iem` storms need the IEM GaugeCorr reader, like group B.
Their `counts` hold `road_sites_named`, which counts in-box sites that are not town-level, and the raw in-box LSR and Storm Events flood rows. They have no `reports_dedup`.
Gauges appear once `obs_catalog.yml` with `mode=fetch` and `only=<ids>` has run.

| id | date (local) | era | towns with road sites in box | box EPSG:26986 | t0 UTC / hours | road sites in box / label rows | labels |
|---|---|---|---|---|---|---|---|
| may2018 | 2018-05-15 | iem | Shrewsbury, Worcester | 169000,881000,189000,901000 | 2018-05-15T14:00Z / 18 h | 3 / 5 | `labels_may2018_shrewsbury.csv` |
| aug2018b | 2018-08-11 | iem | Holden, Lancaster, West Boylston | 167000,894000,187000,914000 | 2018-08-11T08:00Z / 22 h | 3 / 4 | `labels_aug2018b_holden.csv` |
| sep2018 | 2018-09-18 | iem | Ashburnham, Fitchburg, Gardner, Hubbardston | 156000,913000,176000,933000 | 2018-09-18T06:00Z / 18 h | 5 / 5 | `labels_sep2018_fitchburg.csv` |
| sep2018w | 2018-09-18 | iem | Marlborough, Shrewsbury, Worcester | 179000,883000,199000,903000 | 2018-09-18T07:00Z / 18 h | 4 / 4 | `labels_sep2018w_shrewsbury.csv` |
| sep2018m | 2018-09-18 | iem | Bellingham, Milford, Uxbridge | 188000,863000,208000,883000 | 2018-09-18T08:00Z / 18 h | 4 / 4 | `labels_sep2018m_milford.csv` |
| sep2018b | 2018-09-26 | iem | Gardner, Templeton, Westminster | 149000,914000,169000,934000 | 2018-09-26T18:00Z / 18 h | 6 / 7 | `labels_sep2018b_gardner.csv` |
| jul2019 | 2019-07-06 | iem | Oxford, Spencer, Worcester | 157000,874000,177000,894000 | 2019-07-06T14:00Z / 18 h | 5 / 5 | `labels_jul2019_spencer.csv` |
| aug2019 | 2019-08-07 | iem | Oxford, Worcester | 162000,871000,182000,891000 | 2019-08-07T19:00Z / 18 h | 2 / 2 | `labels_aug2019_oxford.csv` |
| sep2019 | 2019-09-02 | iem | Milford, Northbridge | 183000,865000,203000,885000 | 2019-09-02T14:00Z / 18 h | 2 / 4 | `labels_sep2019_northbridge.csv` |
| jun2020 | 2020-06-28 | iem | Blackstone, Franklin, Hopedale, Uxbridge | 190000,859000,210000,879000 | 2020-06-28T14:00Z / 18 h | 6 / 8 | `labels_jun2020_northbridge.csv` |
| jun2020b | 2020-06-28 | iem | Fitchburg, Gardner | 154000,914000,174000,934000 | 2020-06-28T16:00Z / 18 h | 3 / 6 | `labels_jun2020b_gardner.csv` |
| aug2020b | 2020-08-27 | iem | Worcester | 166000,877000,186000,897000 | 2020-08-27T11:00Z / 18 h | 3 / 3 | `labels_aug2020b_worcester.csv` |
| jul2021b | 2021-07-17 | aws | Leicester, Worcester | 163000,880000,183000,900000 | 2021-07-17T14:00Z / 24 h | 4 / 4 | `labels_jul2021b_worcester.csv` |
| jul2023b | 2023-07-10 | aws | Rutland, Worcester | 161000,886000,181000,906000 | 2023-07-10T08:00Z / 18 h | 2 / 4 | `labels_jul2023b_worcester.csv` |
| jul2023c | 2023-07-16 | aws | Fitchburg | 166000,915000,186000,935000 | 2023-07-16T07:00Z / 18 h | 4 / 5 | `labels_jul2023c_fitchburg.csv` |
| jul2023d | 2023-07-21 | aws | Hubbardston | 148000,904000,168000,924000 | 2023-07-21T15:00Z / 18 h | 2 / 3 | `labels_jul2023d_hubbardston.csv` |

The expansion also appended news-sourced rows to `jul2018`, `aug2021` and `aug2026`, plus a missed Storm Events row to `aug2020`. Their ids have the prefixes `JUL2018-N`, `W1`, `AUG2026-N` and `AUG2020-N`.
It also fixed coordinates and names in several earlier label files. The changelog is in `LABELS_EXPANSION.md` and `labels_fix_changelog.json`.

## Excluded candidates

This list predates section C. With the lower bar, some of these storms were added later: 2023-07-16 Fitchburg (`jul2023c`), 2023-07-10 Worcester/Rutland (`jul2023b`), 2018-09-27 Gardner/Templeton (`sep2018b`) and 2019-07-06 Spencer/Worcester (`jul2019`). The 2018-04-16 and 2017 events and the 2020-12-25 Oxford/Sutton rain-on-snow event stay excluded.

| candidate | reason |
|---|---|
| 2014-08-31/09-01 Worcester (`sep2014`, 9 road reports) | No MRMS QPE of any product in the IEM archive for that day, and none on AWS. Its obs files are kept in `docs/proto/obs/*_sep2014.*`. |
| 2021-07-18 Belchertown, Warren, Ware (16 reports) | Most reports are in Belchertown and Ware (District 2). The box would sit west of the District 3 extent. Only Warren and West Warren are in District 3. |
| 2023-07-16 Fitchburg | 3 sites (Franklin Rd at Royalston St, Birch St washout, Merriam Ave basements). Below 5. |
| 2023-07-10 Worcester and Rutland | 2 sites (Southwest Cutoff with 4 cars stuck, Route 56). Below 5. Same day as the Vermont flood. |
| 2023-09-10 Wayland and Acton | 2 sites, the day before `sep2023`. |
| 2020-12-25 Oxford and Sutton | 2 sites, from rain on snowmelt. |
| 2025-06-06 Orange, Warwick, Athol | 3 sites, mostly in District 2. |
| 2023-09-09 North Attleboro and Wrentham; 2020-06-28 Franklin and Wrentham | District 5 / Norfolk–Bristol, outside District 3. |
| 2023-07-21 and 2017-07-18 Chelmsford, Westford, Lowell | District 4. |
| 2024 | No District 3 storm with 3 or more flood reports in the LSR or Storm Events data. |
| Other events before 2020 with 5 to 9 reports | Not added yet, but usable through IEM GaugeCorr: 2014-07-27 Worcester (9 LSR), 2019-07-06 Spencer and Worcester (10), 2018-09-27 Gardner and Templeton (9), 2017-10-24 Worcester and Shrewsbury (8), 2014-10-23 Natick (7), 2016-08-14 Leominster (7), 2017-06-27 Shrewsbury (7), 2018-04-16 Shrewsbury and Westborough (7). See `catalog/` to add them. |

## Label files (`proto/data/labels_<id>_<area>.csv`)

The columns are the same as in the existing label files, plus a final `source` column (`LSR` or `StormEvents`): `id,name,road,town,type,time_local,time_quality,lon,lat,coord_quality,source_url,quote,source`. Each label file has one row per road-related report after deduplication.

- **time_local** is EDT/EST, converted from LSR `VALID` (UTC) or from Storm Events `BEGIN_DATE_TIME` with `CZ_TIMEZONE`. `time_quality` is `report`: the road was flooded by that time, and possibly earlier.
- **Deduplication.** An LSR and a Storm Events row from the same town within 3 minutes are one report. The row keeps the Storm Events 4-decimal point and URL, plus the longer text. LSR corrections, which have the same minute, town and text, are dropped.
- **Road names** are taken from the report text: street suffixes, `Route N`, `I-N` and `146 southbound`. Positions are snapped to `docs/graph_segments.json` by road name within 6 km of an LSR town point, or 3 km of a Storm Events point.
  - When two named roads come within 80 m of each other, the point is their closest approach and `coord_quality` is `exact`. Within 400 m it is `approx`.
  - When only one road is found, the point is that road's vertex nearest the report point, with `approx`. **For a long road and a town-centroid LSR, this can be several hundred metres off, so match those by road name.**
  - When no road matches, the source point is kept: `town` for an LSR with a 0.01° town point, `approx` for a Storm Events point.
- **type** comes from keywords: `closed` for closed/closure/shut, `impassable` for impassable/stuck/stranded/submerged, `washout` for washout/asphalt, and `flooded` otherwise. **quote** is the first 24 words of the report.
- A single report can name several streets, as in a list from an emergency manager. These stay as one row, and `name` lists up to three roads. Splitting them is a possible later improvement.

## Sources

- NWS Local Storm Reports (WFO BOX) through the IEM LSR service: `https://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py`. That service does not apply `states=MA`, so rows are filtered by `STATE`.
- NOAA NCEI Storm Events Database detail files (`StormEvents_details-ftp_v1.0_dYYYY`). 2026 has no rows yet, so `aug2026` is LSR-only.
- USGS gauges from the Water Data OGC API (`proto/obs_fetch.py`). Peaks are the maximum 15-min discharge in the fetch window, which runs from the day before the first report to the day after the last.
- MRMS QPE archive check on AWS `noaa-mrms-pds` (Pass2 listing starts at `20201014`) and IEM mtarchive.
