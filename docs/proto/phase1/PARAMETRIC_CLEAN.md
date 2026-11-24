# Leominster parametric study, clean rerun on the deployed model: results (24 Nov 2026)

Pre-registration `PARAMETRIC_CLEAN_PREREG.md`, commit **a1c36ad9e** (before any run); readout script `proto/parametric_clean_eval.py`
(commit 4bc10d5cc, before any result). Runs: GitHub Actions 45443747446, 9 of 9 succeeded. Storm: Leominster, 11 September 2023,
MRMS rain, catalogue box, deployed model settings and closure rule. In-sample by design: a sensitivity study, not a skill test. Data:
`parametric_clean.json`, `parametric_clean.csv`. Figures: `fig/parametric_clean_bars.png`, `fig/parametric_clean_culverts.png`.

## Plain-language summary (5 lines)
1. **Ground condition before the storm matters most.** Frozen ground almost triples the closed road length; wet soil adds two thirds;
   dry soil removes about two fifths. Residents losing timely emergency access move the same way (+47 %, +25 %, −32 %).
2. **A fully blocked culvert raises the water at the crossing by about 2 m (median)** and puts water over the road at 24 crossings
   that stay dry when open; across the area, closed road length rises 12–14 % and network delay 51–79 %.
3. **Partial blockage (20–50 %) changes little on its own**, but 50 % blockage on wet soil is close to wet soil alone: the soil drives it.
4. **Inspection list:** ten culverts where blockage puts the most water over the road (Fig. 2), led by Dewey Street (Fitchburg) and
   Meadow Pond Drive (Leominster); the list holds across scenarios (6 of 10 confirmed).
5. In every scenario 90–98 % of the residents who lose timely access live on roads that stay dry: they are cut off by closures elsewhere.

## Readout table
Closed = deployed rule (any time); peak = half-hourly series. Access: hospital 30 / fire 8 / police 4 min (report-only). Delay = added
vehicle-hours over the storm. Change vs base in brackets.

| Scenario | Closed segments | Closed km | Closed at peak | Residents losing access (peak) | Cut off from all services | Lost access on dry roads (person-h) | Delay (veh-h) |
|---|---|---|---|---|---|---|---|
| Base (deployed) | 70 | 49.0 | 49 | 43,620 | 7,514 | 97 % | 41,544 |
| Culverts 20 % blocked | 80 | 52.4 (+7 %) | 51 | 43,054 (−1 %) | 5,691 | 97 % | 50,623 (+22 %) |
| Culverts 50 % blocked | 79 | 51.1 (+4 %) | 52 | 41,045 (−6 %) | 5,783 | 93 % | 56,232 (+35 %) |
| Culverts 100 % blocked | 92 | 55.9 (+14 %) | 63 | 40,398 (−7 %) | 6,813 | 90 % | 62,907 (+51 %) |
| Smallest third 100 % blocked | 82 | 55.1 (+12 %) | 58 | 43,768 (+0 %) | 7,543 | 95 % | 74,527 (+79 %) |
| Dry soil (ARC I) | 41 | 29.2 (−40 %) | 30 | 29,541 (−32 %) | 5,403 | 98 % | 18,495 (−55 %) |
| Wet soil (ARC III) | 118 | 82.0 (+67 %) | 77 | 54,620 (+25 %) | 10,161 | 97 % | 53,721 (+29 %) |
| Frozen ground | 207 | 134.4 (+174 %) | 140 | 63,927 (+47 %) | 17,471 | 96 % | 79,275 (+91 %) |
| 50 % blocked + wet soil | 114 | 73.7 (+50 %) | 78 | 53,842 (+23 %) | 6,997 | 93 % | 70,433 (+70 %) |

**Crossings (crest-relative readout; 470 culverts in the box, 37 in the smallest third):**

| Scenario | Segments near crossings closed (open → blocked) | Crossings overtopped (open → blocked) | Median pool rise |
|---|---|---|---|
| 20 % | 2 → 2 | 0 → 0 | +0.6 m |
| 50 % | 2 → 10 | 0 → 5 | +1.6 m |
| 100 % | 2 → 81 | 0 → 24 | +2.3 m |
| Smallest third | 0 → 7 | 0 → 0 | +1.7 m |
| 50 % + wet soil | 2 → 11 | 0 → 5 | +1.7 m |

## Reading rules (as pre-registered)
- **Matters for roads** (closed length ±10 % or more): 100 % blockage, smallest third, dry soil, wet soil, frozen ground, 50 % + wet.
  Little effect: 20 % and 50 % blockage.
- **Matters for access** (±10 % or more): dry soil, wet soil, frozen ground, 50 % + wet. Little effect: all blockage scenarios.
- **Robust:** soil and frozen ground (peak and any-time closures move the same way, all well over 3 segments); blockage for roads at
  50 % and above (crest readout and any-time closures both up). **Not robust:** the small *decrease* in access under 20–100 % blockage.
  It comes from the known notch-water effect in the deployed readout near crossings (21 base closures near crossings disappear at
  100 % blockage; PROJECT_LOG §6), not from a real improvement. Report blockage through the crest readout and delay, not access.
- **Inspection list robust:** 6 of the top 10 under 100 % blockage are also in the top 10 under the smallest third, 50 % + wet soil, or
  the 16 Nov T2 list (rule ≥ 6).

## Culvert inspection list (top 10 under 100 % blockage)
Ranked by added water above the road crest when blocked (ties: pool rise). NAACC condition from the field assessments.

| # | Road, town | Added over road | Pool rise | NAACC condition | Also top 10 under 50 % + wet | In 16 Nov list |
|---|---|---|---|---|---|---|
| 1 | Dewey Street, Fitchburg | +1.0 m | +2.5 m | OK | | yes |
| 2 | Meadow Pond Drive, Leominster | +0.7 m | +2.9 m | not assessed | yes | |
| 3 | Commercial St, Fitchburg | +0.4 m | +1.8 m | not assessed | | yes |
| 4 | Tisdale St / Manchester St, Leominster | +0.4 m | +1.4 m | OK | yes | |
| 5 | Manchester St, Leominster | +0.3 m | +1.1 m | not assessed | yes | |
| 6 | Ball Hill Road, Princeton | +0.2 m | +0.3 m | Poor | | |
| 7 | unnamed road, Fitchburg | +0.2 m | +2.5 m | not assessed | | yes |
| 8 | Pratt St, Fitchburg | +0.2 m | +4.7 m | not assessed | | |
| 9 | Lakeview Dr, Leominster | +0.2 m | +1.2 m | not assessed | | |
| 10 | Theresa Ave, Leominster | +0.1 m | +1.8 m | not assessed | | |

Town = town of the nearest road segment. Seven of the ten have no NAACC condition record: the list doubles as where an assessment is
missing. Only #6 carries a Poor rating.

## Unexpected, recorded honestly (not for the slide)
- Blockage lowers the storm-report and DPW matches (DPW 20 → 8 of 54 at 50 % and 100 %) for the same notch-water reason as above;
  soil and frozen ground change them little (DPW 20–22). Internal check only.
- Under 50 % + wet soil, the largest pool rises (8–11 m) are at the Route 2 / I-190 interchange: the chained-notch pit already found in
  the terrain study (TERRAIN.md). They add no water over the road crest, so they do not enter the inspection list.
- The smallest-third scenario overtops no crossing yet gives the largest delay increase (+79 %): blocked small culverts close a few
  well-used local roads early in the storm. Worth a closer look before it is presented.
- Base here (70 segments, 49 km) is lower than the 16 Nov T2 base (85) because the deployed closure rule now subtracts start-up water.
