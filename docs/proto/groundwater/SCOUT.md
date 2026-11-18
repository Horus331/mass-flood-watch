# Groundwater response to flash-flood storms near District 3: scouting (18 Nov 2026)

Scouting only: nothing here enters the model. Data: USGS continuous groundwater wells, depth to water (parameter 72019), 15-minute
data from USGS Water Services, box lon −72.35 to −71.30, lat 41.95 to 42.75 (District 3 and a margin). Script `proto/gw_scout.py`,
workflow `gw_scout.yml`, output `scout.json` (per well and storm: pre-storm depth, rise, lag, hourly series).

**Definitions.** Pre-storm depth = mean depth to water over the 3 days before the storm date. Rise (7 d) = pre-storm depth minus the
shallowest depth in the 7 days after the storm date. Lag = hours from the storm date (00 local) to that shallowest depth. A lag close
to 168 h means the water was still rising at the end of the window.

## 1. What exists
23 wells with 15-minute depth-to-water data in the box; 17 cover the Sept 2023 window and 14 the Aug 2021 window. None is inside
Leominster or Fitchburg; the nearest to the Sept 2023 storm are Sterling and West Boylston.

## 2. How the water table responded

| Storm | Wells | Median 7-day rise | Wells rising ≥ 0.3 m | Median lag (wells rising ≥ 0.1 m) |
|---|---|---|---|---|
| Aug 2021 (Henri, 19 Aug) | 14 | 0.09 m | 3 | 150 h (≈ 6 days) |
| Sept 2023 (Leominster, 11 Sep) | 17 | 0.09 m | 2 | 112 h (≈ 5 days) |

Largest responses (7-day rise, pre-storm depth):

| Well | Aug 2021 | Sept 2023 |
|---|---|---|
| Northbridge (MA-NXW 54) | **0.93 m in 11 h** (depth 1.0 m) | −0.01 m |
| West Boylston (MA-WSW 26) | 0.62 m, still rising at 6 days (1.9 m) | 0.17 m |
| Winchendon (MA-XNW 13) | 0.62 m (1.9 m) | 0.54 m (2.4 m) |
| Petersham (MA-PHW 16) | −0.03 m | 0.38 m (4.2 m) |
| Winchendon (MA-XNW 48) | 0.21 m (7.9 m) | 0.21 m (8.1 m) |

## 3. What it means
1. **Groundwater is a slow link in the chain.** Most wells peak 4–7 days after the storm, long after roads reopen (the September 2023
   closures last hours). Groundwater does not change same-storm road closures; it changes the ground the *next* storm falls on, and the
   subgrade under pavements and foundations for days to weeks.
2. **Shallow wells react most** (water table within ~2 m: Northbridge, West Boylston, Winchendon 13): rises of 0.5–0.9 m. Deep wells
   (5–8 m) move 0–0.2 m.
3. **Coverage is thin where the damage was**: no well in Leominster or Fitchburg. Any groundwater layer for District 3 would be
   interpolated from wells 10–30 km apart.

## 4. Proposals for Mo (none started)
- **A. Groundwater as the next cascade link (Paper 2 / dissertation chapter).** Rain → water-table rise → wet subgrade under roads in
  the days after a storm. Data in hand: 23 wells, 15-minute series. Next step would be mapping where the water table is shallow under
  District 3 roads (USGS/MassGIS water-table depth, SSURGO "depth to water table") and which road segments sit on it. This is the
  geotechnical side of the framework (rain → flood → groundwater → soil → structure).
- **B. Antecedent state for the flood model.** A "water table already high" index from these wells before a storm, tested like any other
  model change (pre-registered, held-out storms). *Not started: the related soil-wetness test (T4 C) was stopped at Mo's request.*
- **C. Show it on the site later** as a "Groundwater (wells)" layer, once A or B produces something worth showing (the How it works page
  already lists groundwater as planned).
