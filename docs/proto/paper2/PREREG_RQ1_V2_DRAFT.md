# DRAFT: RQ1 v2, road-edge stream-power index with length and crossings handled (20 Nov 2026)

**Status: DRAFT.** Written after RQ1 v1 (`RQ1_RESULT.md`), whose post-hoc checks showed that segment length (AUC 0.87 alone) and stream
crossings (18 of 21 damaged segments within 60 m of one) carry much of v1's signal. v2 fixes both in the index itself. It is to be
**frozen before any out-of-sample data are seen** (a second damage inventory: MEMA / FEMA Public Assistance Category C, or another town's
list), and is not to be tuned on Leominster beyond what v1 already showed.

## Index v2 (changes from `RQ1_INDEX_SPEC.md` only)
1. **Crossing cells removed.** Edge points within 30 m of a mapped road–stream crossing (`docs/network/crossings_all.json`, bridges
   included) or on a cell whose upslope area exceeds 0.5 km² (a channel, not a curb line) are dropped from the edge index. Crossings are
   scored separately by the existing culvert readouts (RQ3).
2. **Length handled.** Per segment the index is computed on fixed 50 m road windows (points every 2 m, both sides, 3 and 5 m offsets), and
   the segment value is the **share of its 50 m windows** whose maximum SPI exceeds the area-wide 95th percentile of window maxima
   (`spi_window_share`), together with the single highest window (`spi_window_max`, which no longer grows with length because every window
   has the same number of points).
3. **Rain-scaled version** (secondary): SPI × the model's storm rain excess at the segment (mm), so storms with little rain score low.

## Test (out-of-sample only)
- Population: segments of the towns covered by the new inventory, model run of that storm at the deployed settings.
- Unit = segment; outcome = ≥ 1 damage point within 30 m; road-edge damage types only (washout, shoulder, pavement edge), crossing damage
  excluded (it belongs to RQ3).
- Main: AUC of `spi_window_share`, and its added value over log depth + log traffic + log length (likelihood-ratio test).
- Reading rule (to be fixed at freezing): AUC ≥ 0.70 with the 95 % interval above 0.5 and LR p < 0.05 → "confirmed out of sample";
  interval including 0.5 → "not confirmed".

## Before freezing
- Recompute v2 on Leominster only to check that it runs (values reported, no comparison with damage beyond what v1 already reported).
- Fix the reading rule numbers; record the commit.
