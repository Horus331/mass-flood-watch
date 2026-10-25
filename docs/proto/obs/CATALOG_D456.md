# District 4-6 transfer-test storm catalogue (`catalog_d456.json`)

Built by `proto/transfer_d456.py` (`discover` on Actions, `queries`, label geocode on Actions, `build`) under the pre-registered rules of
`docs/proto/PROTOCOL.md` "Transfer test (Districts 4-6)" (T-2). These storms are **test-only**: the frozen District 3 model is run on them
once and nothing is tuned on them. Label files: `proto/data/labels_<id>_<area>.csv` (same columns as District 3).

**81 storms, 510 road-level sites** (150 m clusters of non-`town` rows), 544 road-level rows, 659 label rows in all.
Rows by source: LSR 395, StormEvents 199, SeeClickFix 61, Boston311 4. Coordinates: approx 389, exact 155, town 115.

| id | district | date (local) | era / rain | box EPSG:26986 | t0 UTC / h | sites | rows (road-level) | sources | towns |
|---|---|---|---|---|---|---|---|---|---|
| jan2018e | 5 | 2018-01-12 | iem | 233000,811000,253000,831000 | 2018-01-12T18:00Z / 28 | 4 | 7 (5) | LSR 4, StormEvents 3 | Dartmouth, New Bedford, North Dartmouth, Westport |
| jan2018f | 6 | 2018-01-13 | iem | 216000,893000,236000,913000 | 2018-01-12T21:00Z / 18 | 7 | 9 (7) | LSR 5, StormEvents 3, SeeClickFix 1 | Babson Park, Brookline, Lincoln, Malden, North Waltham, Wellesley |
| apr2018e | 4 | 2018-04-16 | iem | 217000,907000,237000,927000 | 2018-04-16T12:00Z / 18 | 3 | 4 (3) | StormEvents 2, LSR 2 | Bedford Spgs, Farm Hill, Stoneham |
| apr2018f | 6 | 2018-04-16 | iem | 222000,887000,242000,907000 | 2018-04-16T12:00Z / 18 | 5 | 7 (5) | LSR 6, StormEvents 1 | Belmont, Dedham, Newton, Quincy, Stone Haven |
| may2018e | 6 | 2018-05-15 | iem | 224000,887000,244000,907000 | 2018-05-15T15:00Z / 18 | 5 | 6 (6) | SeeClickFix 1, LSR 4, StormEvents 1 | Boston, Boston 311, Somerville |
| jun2018e | 4 | 2018-06-25 | iem | 201000,899000,221000,919000 | 2018-06-24T22:00Z / 18 | 3 | 3 (3) | StormEvents 2, LSR 1 | Concord, Silver Hill |
| jun2018f | 4 | 2018-06-25 | iem | 221000,896000,241000,916000 | 2018-06-24T22:00Z / 18 | 12 | 16 (13) | LSR 9, StormEvents 7 | Belmont, Chelsea, Malden, Medford, Revere, Waltham |
| jul2018e | 6 | 2018-07-17 | iem | 207000,895000,227000,915000 | 2018-07-17T11:00Z / 18 | 3 | 3 (3) | LSR 3 | Lexington, Wellesley |
| jul2018f | 6 | 2018-07-17 | iem | 227000,890000,247000,910000 | 2018-07-17T11:00Z / 18 | 7 | 8 (7) | LSR 5, StormEvents 3 | Boston, Cambridge, Winthrop |
| jul2018g | 4 | 2018-07-26 | iem | 217000,930000,237000,950000 | 2018-07-26T12:00Z / 18 | 6 | 7 (7) | LSR 5, StormEvents 2 | Lawrence, Methuen |
| jul2018h | 4 | 2018-07-26 | iem | 229000,900000,249000,920000 | 2018-07-26T13:00Z / 18 | 4 | 4 (4) | SeeClickFix 1, StormEvents 2, LSR 1 | Boston Naval Shipyar, Cambridge, Carletonville |
| aug2018e | 5 | 2018-08-04 | iem | 219000,818000,239000,838000 | 2018-08-04T09:00Z / 18 | 4 | 9 (4) | LSR 8, StormEvents 1 | Fall River, Swansea |
| aug2018f | 5 | 2018-08-04 | iem | 292000,818000,312000,838000 | 2018-08-04T15:00Z / 18 | 3 | 3 (3) | LSR 3 | Barnstable, West Yarmouth |
| aug2018g | 5 | 2018-08-04 | iem | 314000,839000,334000,859000 | 2018-08-04T16:00Z / 18 | 8 | 10 (8) | LSR 8, StormEvents 2 | Eastham, Silver Spg Beach, Wellfleet |
| aug2018h | 5 | 2018-08-09 | iem | 314000,829000,334000,849000 | 2018-08-09T06:00Z / 18 | 4 | 8 (4) | StormEvents 1, LSR 7 | Eastham, Orleans, South Brewster |
| aug2018k | 4 | 2018-08-11 | iem | 209000,928000,229000,948000 | 2018-08-11T11:00Z / 18 | 3 | 5 (4) | StormEvents 1, LSR 4 | Lawrence, Methuen, North Chelmsford |
| aug2018n | 4 | 2018-08-12 | iem | 232000,901000,252000,921000 | 2018-08-12T03:00Z / 19 | 38 | 54 (42) | StormEvents 28, SeeClickFix 3, LSR 23 | Carletonville, Charlestown, Devereux, East Everett, Everett, Farm Hill … |
| aug2018p | 5 | 2018-08-18 | iem | 299000,858000,319000,878000 | 2018-08-18T14:00Z / 18 | 3 | 3 (3) | StormEvents 2, LSR 1 | Provincetown |
| sep2018e | 6 | 2018-09-18 | iem | 220000,895000,240000,915000 | 2018-09-18T07:00Z / 18 | 16 | 18 (17) | SeeClickFix 3, LSR 12, StormEvents 3 | Arlington, Boston Naval Shipyar, Broadway, Cambridge, Chelsea, Malden … |
| sep2018f | 4 | 2018-09-18 | iem | 226000,922000,246000,942000 | 2018-09-18T07:00Z / 18 | 8 | 13 (11) | StormEvents 4, LSR 9 | Burleys Corner, Danvers, Lawrence, Lynnfield, Middleton, South Lawrence … |
| sep2018g | 6 | 2018-09-18 | iem | 224000,873000,244000,893000 | 2018-09-18T08:00Z / 18 | 6 | 7 (7) | SeeClickFix 1, LSR 4, StormEvents 2 | Braintree, Norwood, Quincy, Randolph |
| oct2018e | 4 | 2018-10-29 | iem | 228000,900000,248000,920000 | 2018-10-29T06:00Z / 18 | 8 | 10 (9) | SeeClickFix 6, LSR 2, StormEvents 2 | Malden, Reading, Salem, Somerville |
| nov2018e | 4 | 2018-11-03 | iem | 222000,922000,242000,942000 | 2018-11-03T04:00Z / 18 | 3 | 3 (3) | SeeClickFix 1, LSR 2 | Lawrence, Middleton, Reading |
| nov2018f | 6 | 2018-11-03 | iem | 232000,870000,252000,890000 | 2018-11-03T05:00Z / 18 | 3 | 5 (3) | SeeClickFix 2, StormEvents 2, LSR 1 | Braintree, Brockton, South Weymouth Nas |
| apr2019e | 5 | 2019-04-15 | iem | 239000,879000,259000,899000 | 2019-04-15T04:00Z / 18 | 3 | 4 (4) | LSR 2, StormEvents 2 | Hingham, West Hingham |
| jun2019e | 6 | 2019-06-29 | iem | 229000,894000,249000,914000 | 2019-06-29T13:00Z / 18 | 4 | 7 (4) | LSR 5, StormEvents 2 | East Boston, Revere |
| jul2019e | 6 | 2019-07-06 | iem | 211000,888000,231000,908000 | 2019-07-06T14:00Z / 18 | 3 | 4 (3) | SeeClickFix 1, LSR 2, StormEvents 1 | Babson Park, Cambridge, Wellesley |
| jul2019f | 5 | 2019-07-12 | iem | 238000,813000,258000,833000 | 2019-07-12T03:00Z / 18 | 4 | 5 (4) | LSR 4, StormEvents 1 | Fairhaven, New Bedford |
| jul2019g | 5 | 2019-07-22 | iem | 241000,814000,261000,834000 | 2019-07-22T18:00Z / 18 | 9 | 11 (10) | StormEvents 2, LSR 9 | Fairhaven, Marion, New Bedford |
| jul2019h | 4 | 2019-07-31 | iem | 231000,896000,251000,916000 | 2019-07-31T12:00Z / 18 | 4 | 5 (5) | SeeClickFix 1, LSR 4 | Boston, Lynn, Malden, Revere |
| aug2019e | 5 | 2019-08-04 | iem | 237000,813000,257000,833000 | 2019-08-04T15:00Z / 18 | 5 | 7 (7) | LSR 4, StormEvents 3 | Fairhaven, New Bedford |
| aug2019f | 4 | 2019-08-08 | iem | 223000,895000,243000,915000 | 2019-08-07T21:00Z / 18 | 5 | 5 (5) | StormEvents 1, SeeClickFix 1, LSR 3 | 1 Ne West Somerville, 1 Se Newton Corner, 1 Wnw Crescent Beach, Malden, Tufts College |
| sep2019e | 4 | 2019-09-02 | iem | 209000,893000,229000,913000 | 2019-09-02T15:00Z / 18 | 3 | 4 (3) | LSR 2, StormEvents 2 | Clematis Brook, Waltham |
| sep2019f | 4 | 2019-09-02 | iem | 229000,902000,249000,922000 | 2019-09-02T15:00Z / 18 | 10 | 12 (10) | StormEvents 3, LSR 8, SeeClickFix 1 | 1 Ne East Lynn, 1 Ne Raddin Station, East Lynn, Lynn, Medford, Oak Grove … |
| sep2019g | 5 | 2019-09-02 | iem | 228000,861000,248000,881000 | 2019-09-02T17:00Z / 18 | 4 | 4 (4) | SeeClickFix 1, LSR 3 | 1 Nne Winters Corner, 1 Sse Montello, Brockton |
| oct2019e | 5 | 2019-10-27 | iem | 238000,811000,258000,831000 | 2019-10-27T15:00Z / 18 | 10 | 15 (13) | StormEvents 6, LSR 9 | Fairhaven, New Bedford |
| may2020e | 5 | 2020-05-23 | iem | 268000,791000,288000,811000 | 2020-05-23T07:00Z / 18 | 6 | 10 (8) | StormEvents 4, LSR 6 | 1 Ne Oak Bluffs, Oak Bluffs, Tisbury |
| jun2020e | 5 | 2020-06-21 | iem | 229000,868000,249000,888000 | 2020-06-21T13:00Z / 18 | 6 | 9 (8) | StormEvents 9 | Holbrook, Randolph |
| jun2020f | 6 | 2020-06-21 | iem | 209000,889000,229000,909000 | 2020-06-21T14:00Z / 18 | 5 | 7 (5) | StormEvents 6, SeeClickFix 1 | Needham, Wellesley, Wellesley Fells, Weston |
| jun2020g | 5 | 2020-06-28 | iem | 223000,865000,243000,885000 | 2020-06-28T13:00Z / 18 | 5 | 9 (6) | StormEvents 3, LSR 6 | Brockton, Brockton Hgts, Norwood, Stoughton |
| jul2020e | 4 | 2020-07-23 | iem | 221000,930000,241000,950000 | 2020-07-23T12:00Z / 18 | 12 | 14 (13) | StormEvents 9, LSR 5 | Ballardvale, Georgetown, Lawrence, Methuen |
| jul2020f | 4 | 2020-07-23 | iem | 243000,940000,263000,960000 | 2020-07-23T12:00Z / 18 | 3 | 3 (3) | LSR 2, StormEvents 1 | Newburyport, Newburyport Plum Arp |
| jul2020g | 4 | 2020-07-23 | iem | 249000,915000,269000,935000 | 2020-07-23T12:00Z / 18 | 4 | 6 (5) | LSR 3, StormEvents 3 | Beverly, Gloucester |
| sep2020e | 4 | 2020-09-10 | iem | 232000,914000,252000,934000 | 2020-09-10T15:00Z / 18 | 3 | 3 (3) | LSR 2, StormEvents 1 | Beverly, Middleton, North Reading |
| jul2021e | 4 | 2021-07-02 | aws | 229000,898000,249000,918000 | 2021-07-01T23:00Z / 18 | 5 | 6 (6) | LSR 6 | Charlestown, Chelsea, Lynn, Revere, Somerville |
| jul2021f | 6 | 2021-07-03 | aws | 226000,886000,246000,906000 | 2021-07-03T15:00Z / 18 | 4 | 5 (4) | SeeClickFix 1, LSR 4 | Braintree, Cambridge, Chelsea, South Boston |
| jul2021g | 6 | 2021-07-09 | aws | 223000,886000,243000,906000 | 2021-07-09T07:00Z / 18 | 5 | 9 (5) | LSR 7, StormEvents 2 | Fairmount, Grove Hall, Hyde Park, Newton, Winthrop |
| jul2021h | 4 | 2021-07-09 | aws | 232000,906000,252000,926000 | 2021-07-09T09:00Z / 18 | 6 | 7 (6) | LSR 5, StormEvents 2 | Danvers, Lynn, Melrose, Oak Grove, Peabody |
| jul2021k | 4 | 2021-07-12 | aws | 236000,909000,256000,929000 | 2021-07-12T05:00Z / 18 | 4 | 6 (6) | LSR 2, SeeClickFix 2, StormEvents 2 | Danvers, Malden, Peabody, Salem Maritime Nhs, Swampscott |
| aug2021e | 4 | 2021-08-19 | aws | 229000,901000,249000,921000 | 2021-08-19T09:00Z / 18 | 10 | 12 (10) | SeeClickFix 7, LSR 2, StormEvents 3 | Malden, Salem Maritime Nhs, Saugus, Somerville |
| sep2021e | 5 | 2021-09-02 | aws | 220000,818000,240000,838000 | 2021-09-01T23:00Z / 18 | 5 | 7 (5) | LSR 2, StormEvents 5 | 2 Sw Fall River, Watuppa |
| sep2021f | 6 | 2021-09-02 | aws | 219000,889000,239000,909000 | 2021-09-02T00:00Z / 18 | 6 | 7 (6) | LSR 2, SeeClickFix 2, StormEvents 3 | 1 Wnw Dorchester, Back Bay Annex, Beaver Brook, Medford, Needham |
| nov2021e | 4 | 2021-11-12 | aws | 224000,926000,244000,946000 | 2021-11-12T14:00Z / 18 | 7 | 8 (7) | SeeClickFix 5, StormEvents 2, LSR 1 | Burleys Corner, Department of Public Works (DPW), Shawsheen Vlg |
| nov2021f | 4 | 2021-11-12 | aws | 231000,904000,251000,924000 | 2021-11-12T14:00Z / 18 | 4 | 6 (4) | SeeClickFix 1, StormEvents 2, LSR 3 | 1 Ene Peabody, Cambridge, Tapleyville |
| apr2022e | 5 | 2022-04-08 | aws | 238000,815000,258000,835000 | 2022-04-08T02:00Z / 18 | 5 | 6 (6) | StormEvents 3, LSR 3 | Acushnet, New Bedford, North Bristol, Westgate Park |
| aug2022e | 5 | 2022-08-09 | aws | 229000,815000,249000,835000 | 2022-08-09T15:00Z / 18 | 6 | 8 (6) | LSR 6, StormEvents 2 | Acushnet, Fall River, New Bedford |
| sep2022e | 4 | 2022-09-05 | aws | 218000,910000,238000,930000 | 2022-09-05T01:00Z / 18 | 4 | 5 (4) | LSR 3, StormEvents 2 | 1 Ssw Wilmington, North Wilmington, Nutting Lake, Woburn |
| sep2022f | 5 | 2022-09-13 | aws | 236000,809000,256000,829000 | 2022-09-13T07:00Z / 18 | 4 | 4 (4) | LSR 2, StormEvents 2 | 2 Sse New Bedford, New Bedford, Westport Factory |
| jul2023e | 5 | 2023-07-04 | aws | 209000,832000,229000,852000 | 2023-07-04T12:00Z / 18 | 5 | 5 (5) | LSR 3, StormEvents 2 | 3 Ne Rehoboth, 3 Wsw Attleborough, Rehoboth, Swansea |
| jul2023f | 4 | 2023-07-16 | aws | 229000,905000,249000,925000 | 2023-07-16T10:00Z / 18 | 4 | 5 (4) | LSR 3, SeeClickFix 1, StormEvents 1 | 1 Ssw Danvers, 1 Wsw Revere, Lynnfield, Reading |
| jul2023g | 5 | 2023-07-16 | aws | 217000,872000,237000,892000 | 2023-07-16T11:00Z / 18 | 4 | 4 (4) | SeeClickFix 1, LSR 2, StormEvents 1 | Morrills, Needham, Norwood, Stoughton |
| jul2023h | 5 | 2023-07-16 | aws | 259000,863000,279000,883000 | 2023-07-16T17:00Z / 18 | 3 | 3 (3) | LSR 2, StormEvents 1 | 2 Ene Marshfield, Kent Park |
| jul2023k | 4 | 2023-07-21 | aws | 206000,920000,226000,940000 | 2023-07-21T15:00Z / 18 | 8 | 10 (8) | LSR 8, StormEvents 2 | 1 Ese Lowell, 1 Ne Chelmsford, Billerica, Chelmsford, Lowell, River Pines |
| jul2023n | 6 | 2023-07-21 | aws | 224000,891000,244000,911000 | 2023-07-21T18:00Z / 18 | 13 | 17 (13) | LSR 14, StormEvents 3 | Belmont, Cambridge, Chelsea, Everett, Franklin Park, Medford … |
| jul2023p | 6 | 2023-07-25 | aws | 224000,882000,244000,902000 | 2023-07-25T12:00Z / 18 | 5 | 6 (5) | LSR 5, StormEvents 1 | 1 Ssw Boston, 1 Sw Boston, 2 Wsw Quincy, Dedham, West Quincy |
| jul2023q | 6 | 2023-07-29 | aws | 222000,889000,242000,909000 | 2023-07-29T10:00Z / 18 | 22 | 27 (22) | LSR 22, StormEvents 4, SeeClickFix 1 | 1 Ese Brookline, 1 Nnw West Roxbury, 1 Nw Revere, 1 Sse Brookline, 1 Ssw Boston Esplanade, 1 Sw Newton … |
| jul2023r | 4 | 2023-07-29 | aws | 234000,909000,254000,929000 | 2023-07-29T17:00Z / 18 | 5 | 5 (5) | SeeClickFix 2, LSR 3 | Lynn, Malden, Salem |
| aug2023e | 4 | 2023-08-08 | aws | 217000,920000,237000,940000 | 2023-08-08T07:00Z / 18 | 12 | 16 (12) | SeeClickFix 1, LSR 10, StormEvents 5 | 2 Sw Tewksbury, 2 Wnw Wilmington, North Andover, North Woburn Jct, Reading |
| aug2023f | 6 | 2023-08-08 | aws | 217000,890000,237000,910000 | 2023-08-08T07:00Z / 18 | 7 | 9 (7) | SeeClickFix 4, LSR 3, StormEvents 2 | Babson Park, Cambridge, Medford, Needham, Wellesley |
| aug2023g | 5 | 2023-08-08 | aws | 237000,812000,257000,832000 | 2023-08-08T07:00Z / 18 | 5 | 6 (5) | StormEvents 3, LSR 3 | New Bedford, Sherwood Forest |
| aug2023h | 4 | 2023-08-18 | aws | 211000,922000,231000,942000 | 2023-08-18T07:00Z / 18 | 5 | 6 (5) | LSR 5, StormEvents 1 | Andover, Chelmsford, Tewksbury, West Chelmsford |
| aug2023k | 6 | 2023-08-18 | aws | 221000,874000,241000,894000 | 2023-08-18T07:00Z / 18 | 3 | 3 (3) | LSR 3 | 1 Nne Dorchester, 1 Wsw Canton |
| sep2023e | 5 | 2023-09-09 | aws | 207000,851000,227000,871000 | 2023-09-09T12:00Z / 18 | 9 | 11 (9) | StormEvents 3, SeeClickFix 1, LSR 7 | 1 Wsw North Attleboroug, 2 Sw North Attleborough, 3 Sw North Attleborough, Adamsdale, Foxborough, North Attleboro … |
| sep2023f | 5 | 2023-09-10 | aws | 240000,869000,260000,889000 | 2023-09-10T10:00Z / 18 | 4 | 5 (4) | SeeClickFix 1, LSR 3, StormEvents 1 | 3 Nne Rockland, Brockton, Cohasset, Hanover Center |
| sep2023g | 5 | 2023-09-11 | aws | 229000,831000,249000,851000 | 2023-09-11T11:00Z / 18 | 6 | 6 (6) | LSR 4, StormEvents 2 | 1 Ese Somerset, 1 Ese Taunton Ap, East Taunton, Taunton Ap, Taunton Arpt |
| sep2023h | 5 | 2023-09-11 | aws | 206000,844000,226000,864000 | 2023-09-11T14:00Z / 18 | 3 | 9 (3) | LSR 6, StormEvents 3 | 1 Ne Attleborough, Attleborough, Dodgeville |
| jul2025e | 6 | 2025-07-10 | aws | 232000,880000,252000,900000 | 2025-07-10T04:00Z / 18 | 13 | 14 (13) | SeeClickFix 2, LSR 7, Boston311 4, StormEvents 1 | 1 Ene Hingham, 1 Se Mattapan, 2 Sw Quincy, Back Bay, Dorchester, Milton … |
| jun2026e | 5 | 2026-06-23 | aws | 228000,815000,248000,835000 | 2026-06-23T02:00Z / 18 | 5 | 5 (5) | LSR 5 | 1 Sse New Bedford, 2 Nw Westport, 3 Wsw Fall River, New Bedford |
| sep2026e | 5 | 2026-09-13 | aws | 219000,817000,239000,837000 | 2026-09-13T08:00Z / 18 | 5 | 7 (5) | LSR 7 | Somerset |
| sep2026f | 5 | 2026-09-26 | aws | 229000,814000,249000,834000 | 2026-09-26T12:00Z / 18 | 6 | 7 (6) | LSR 7 | Acushnet, Fall River, New Bedford |
| sep2026g | 5 | 2026-09-27 | aws | 228000,860000,248000,880000 | 2026-09-27T07:00Z / 19 | 9 | 11 (9) | SeeClickFix 4, LSR 7 | 1 Nnw Avon, Brockton, Easton |

**Considered and not selected: 79 boxes** (reason: < 3 road-level sites 78, coastal 1).
Every candidate day (>= 2 District 4-6 flood reports in LSR + Storm Events since 2018) was searched for up to three non-overlapping 20 x 20 km
boxes; the full list with counts is `docs/proto/transfer/raw/build_audit.json`.

## How the labels were made

- **NWS reports** (IEM LSR archive, NCEI Storm Events; `docs/proto/obs/catalog/*_ma_flood_2014_2026.csv`): every FLOOD / FLASH FLOOD report whose
  point lies in District 4, 5 or 6 (MassGIS `MassDOT_Highway_Districts` polygons) was split into the roads it names (one row per road; "A at B"
  is one intersection row) by `transfer_d456.mentions`. Dropped: tide / surge / coastal / wave and snowmelt / ice-jam texts, basement / building /
  water-main reports without a road impact, texts without a flood word. Draft rows: `raw/nws_drafts.json`; reports without a road: `raw/nws_skipped.json`.
- **Placement** (OSM via `proto/label_geocode.py`, `raw/geocode_osm.json`): intersection within 80 m -> `exact`; the road vertex nearest the NWS
  point (< 1.5 km) or the centroid vertex of a road shorter than 3 km -> `approx`; otherwise the row stays `town` at the NWS point and is not matched.
  Same road named twice in one storm within 1 km (an LSR and its Storm Events copy) -> one row (the better coordinate).
- **Boston 311** (data.boston.gov CKAN, full-text "flood"): requests whose type/title says flooding, at the city-geocoded address (`exact`), opened
  between t0 - 2 h and t0 + hours + 12 h. Basement, property, flood-light and food-establishment requests are excluded.
- **SeeClickFix** (api/v2 issues in the window and box): issues whose text says the street / road flooded or had standing water (not chronic
  drain complaints without a flood word, not private property), at the reporter's pin (`exact`), same time window as 311.
- News was not searched systematically for these districts (time); no news rows.

## Storm windows and boxes

- Box: the 1 km-aligned 20 x 20 km square with the most road-level sites that holds >= 1 NWS road report, centre in Districts 4-6, not overlapping a
  District 3 catalogue box of the same date (+-1 day). t0 = first NWS report in the box - 7 h; hours = max(18, last NWS report - t0 + 5 h).
- Selected when >= 3 road-level sites (150 m clusters), coastal texts <= half of the NWS reports in the box and window, and no snowmelt / ice text.
- Rain: MRMS hourly QPE from AWS Pass2 (from 14 Oct 2020) or the IEM GaugeCorr archive before, exactly as the District 3 2018-2020 storms.

