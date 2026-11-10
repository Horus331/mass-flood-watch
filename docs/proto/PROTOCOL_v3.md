# Evaluation protocol v3: benchmark against named baselines (pre-registered 10 Nov 2026)

Master prompt Phase 0, task 0.1. Committed before any of the new baselines below (NWS polygons, rain threshold, HAND, H×V×C) has been
intersected with a road segment or scored. What had been scored before: the model (`scoring/BASELINE_v2_expanded.md`), the FEMA SFHA and
the BSC/MRPC Leominster map (`static/STATIC.md`, District 3; `static/HYBRID.md`, Districts 4–6), and MassDOT repeating flood points only
as a check list, not as a predictor. v3 does not replace `PROTOCOL.md` v2 (the adoption rule for model changes); it is the benchmark.

## 1. Unit, labels, negatives

- **Unit:** (road segment, storm). Segment = MassDOT road-inventory segment of `docs/graph_segments.json` (District 3) or the OSM segment
  of the transfer runs (Districts 4–6), as in score_v2. Storm = the catalogue window (`obs/catalog.json`), the whole event.
- **Positive:** a labelled report site (score_v2 site list: NWS/LSR, Storm Events, MassDOT, town DPW, news) matched to the segment within
  30 m, per score_v2. A site counts once.
- **Positive–unlabeled.** Unreported does not mean dry. Two domains, both always reported:
  - **Complete domain:** Leominster, sep2023, where the DPW logged every damaged street. All other Leominster segments are true negatives.
  - **Reported domain** (all storms): negatives are segments in the storm box at least 500 m from every report and in towns that filed
    at least one report in that storm. Segments 30–500 m from a report and segments in towns with no report are excluded from
    POD/FAR/CSI and Brier. Site recall (§3) keeps the score_v2 universe.

## 2. Methods compared (same segments, same storms)

| id | method | yes/no flag | score for ranking / probability |
|---|---|---|---|
| M | the model, frozen (parity baseline settings of the run scored) | p_close ≥ 0.5 | p_close |
| B1 | NWS flash-flood warning polygons (IEM archive, issued during the storm window, District 3 and 4–6 offices) | segment midpoint inside any FFW polygon valid in the window | hours inside a warning |
| B2 | FEMA NFHL 100-yr zone (SFHA), as STATIC.md | ≥ 30 % of length in the SFHA | share of length in SFHA |
| B3 | MassDOT repeating flood points ("it flooded before") | within 30 m of a point | inverse distance to the nearest point |
| B4 | rain threshold: radar I60 (peak 1 h) or 3 h maximum at the segment, MRMS 1 km | I60 ≥ T60 or R3h ≥ T3 | max(I60/T60, R3h/T3) |
| B5 | terrain only: HAND (height above nearest drainage, from the model's 20 m terrain and stream network) | HAND ≤ H* | −HAND |
| B6 | static H×V×C (Tao & Mallick style): hazard = SFHA share + low HAND; vulnerability = road class; consequence = AADT | top 3 % | product |

Thresholds T60, T3 and H* are tuned on **Leominster sep2023 only**: the values that maximise CSI on the complete domain. They are then
frozen. B3 uses the MassDOT points from before each storm when dated, otherwise all points (stated per storm). B6 is reported only if
all its inputs exist for both district groups; otherwise it is dropped and the drop is written down.

## 3. Metrics

- **Yes/no** (each method's own flag): POD, FAR, CSI on the reported domain and on the complete domain; flagged share of segments.
- **Equal-share ranking:** site recall when each method flags the same share as the model's rule, and at 3 % (with the chance level),
  so a method that flags more cannot win by flagging more.
- **Probabilities.** Every score is turned into a probability by isotonic regression fitted on Leominster sep2023 only, then frozen.
  Report Brier score and BSS of M against each baseline and against climatology (the Leominster base rate), reliability diagrams
  (10 bins), PR-AUC (primary) and ROC-AUC.
- **Uncertainty:** 95 % CIs from 2,000 bootstrap resamples of **storms** (one stage), paired between methods. Differences are called
  significant only if the paired 95 % CI excludes 0.

## 4. Splits

- **Tuning:** Leominster sep2023 only (model settings, B4/B5 thresholds, isotonic maps).
- **Test 1:** the 23 held-out District 3 storms of BASELINE_v2_expanded. Worcester aug2021 is reported separately, because it informed
  development decisions in October.
- **Test 2:** the 81 District 4–6 storms of the transfer pool, with the model frozen.
- **Locked storms** (aug2015, aug2018, aug2020, jul2018, oct2016): not run, not scored, not looked at.
- **Forward test:** every forecast archived before the event (Nov 2026 – Oct 2027), scored with the same metrics.

## 5. Reporting

All rows are reported, including any metric on which a baseline beats the model. No threshold, domain, metric or storm list changes after
results are seen; changes need a dated amendment here with the reason, before re-running. Results go to `scoring/BENCHMARK_v3.md`, with a
one-page plain-language summary first.
