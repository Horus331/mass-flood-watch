# Cycle 1 results (9–11 Nov 2026): the model benchmarked against six named baselines, and the live skeleton

## One-page summary

**What was done**
- Wrote and committed the evaluation rules *before* scoring anything new (`docs/proto/PROTOCOL_v3.md`, with one dated amendment).
- Built six baselines on the same road segments and storms: NWS flash-flood warnings, FEMA 100-yr zone, MassDOT repeat flood points, a
  radar rain threshold, terrain only (height above nearest drainage, HAND), and a static hazard × vulnerability × consequence score.
- Scored the current, frozen model against all six on 23 held-out District 3 storms and 81 District 4–6 storms (`docs/proto/scoring/BENCHMARK_v3.md`).
- Live system: storm state QUIET / WATCH / ACTIVE every ~10 min with a public `/status/` page, automatic GitHub Issues on failures, a
  golden-storm regression test in CI (repeat run identical), a pinned container, ADRs, runbook and changelog.
- Two model-input tests closed by their pre-registered rules: radar nowcast in the first forecast hours **adopted** (rain error × 0.83);
  lower rain percentile **rejected** (F1 0.442 vs 0.504 for the live setting).

**Key numbers** (share of report sites found when each method flags its top 3 % of road segments; 95 % interval of model minus baseline,
bootstrapped over storms)

| method | District 3, 23 storms | model − method | Districts 4–6, 81 storms | model − method |
|---|---|---|---|---|
| **Model** | **0.20** | | **0.21** | |
| NWS flash-flood warnings | 0.05 | [+0.04, +0.25] | 0.09 | [+0.08, +0.16] |
| FEMA 100-yr zone | 0.12 | [−0.02, +0.19] | 0.07 | [+0.09, +0.18] |
| MassDOT repeat points | 0.14 | [−0.04, +0.15] | (District 3 only) | |
| Rain threshold (Leominster-tuned) | 0.05 | [+0.05, +0.25] | 0.06 | [+0.10, +0.19] |
| Terrain only (HAND) | 0.08 | [+0.02, +0.21] | 0.10 | [+0.07, +0.15] |
| Static H×V×C | **0.32** | [−0.23, 0.00] | 0.10 | [+0.06, +0.16] |
| chance | 0.07 | | 0.09 | |

**What it means for a MassDOT engineer**
- On storms the model never saw (Districts 4–6), it ranks roads clearly better than any map or rule an office could use today; those maps are
  at chance there. Checking the model's top 3 % of roads would have found about 1 in 5 reported problem sites.
- It is a ranking aid, not yet a warning: at its own yes/no rule it catches 3–5 % of reported segments.
- In District 3 a simple score that favours busy roads finds more *reported* sites than the model. Reports there come mostly from MassDOT
  and the news, so busy roads dominate them (reported segments: 25 % arterials vs 4 % of all roads). That is a label bias to fix and a hint
  that traffic belongs in a consequence-weighted product.

**Named limitations**
1. Labels are sparse and positive-unlabeled; outside Leominster most flooded roads are never reported.
2. Probabilities fitted on Leominster do not transfer (roads given ~60 % flood ~3 % of the time elsewhere), so the site shows "k of 8".
3. The model was tuned on one storm; the D3 test set is small (222 reported segments), so D3 intervals are wide.
4. The rain-threshold baseline, tuned on Leominster, almost never fires elsewhere (85 mm/h).
5. The MassDOT repeat-flood list is undated (used for every storm), and NWS warnings count for the whole storm window: both favour the baselines.

**What is next (cycle 2)**
- Phase 1: the Leominster deep dive (why each missed site was missed: culvert, debris, soil, drainage, terrain or label).
- A pre-registered test of model + traffic (consequence) ranking, tuned on Leominster only, tested on D4–6.
- Held-out calibration of the chance of flooding (leave one storm out) before any percentage is shown.
- The forecast archive on Hugging Face (waits for the scoped token).

## Slide bullets (complete story)
- **Last time → this update:** we said the model beats random by ~3×; now it is benchmarked against six named methods with pre-registered rules.
- **Inputs → simulation → outputs:** radar/HRRR rain → LISFLOOD-FP 20 m → depth on every road segment → ranking of roads likely to close.
- **Compared with records (81 storms in Districts 4–6, never used for tuning):** model finds 21 % of reported sites in its top 3 % of roads;
  NWS warnings 9 %, FEMA zone 7 %, terrain 10 %, chance 9 %; every difference significant.
- **Honest caveat:** in District 3 a traffic-weighted static score finds more reported sites (32 % vs 20 %), because reports there favour busy roads.
- **Live system:** storm state every 10 min on a public status page, automatic failure alerts, and a regression test that blocks unintended model changes.
