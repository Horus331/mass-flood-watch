# Scoring v2 baseline: the published Turing catalogue (23 Oct 2026)

These are the reference numbers for `PROTOCOL.md`.

- Made by `python proto/score_v2.py --catalog --out docs/proto/scoring/BASELINE_v2.json --md docs/proto/scoring/baseline_table.md`, which runs
  in about 3 minutes on 2 CPUs.
- `baseline_table.md` has every run and every pool. `BASELINE_v2.json` keeps the per-site hit vectors that `--compare` needs.
- Runs scored: the 9 LOSO runs `docs/proto/turing/<storm>_<area>_20m` (marked "primary") and 6 extra runs (`leominster_sep2023_gpu/_10m/_dams`,
  `d3_sep2023_20m`, `worcester_aug2021_gpu/_dams`). The extra runs are listed but not pooled.
- `docs/proto/parity/catalog/` does not exist yet. When T0 publishes it, the same command scores it as the group `parity:*`, and that group
  replaces this baseline (PROTOCOL §3).

**Caveat.** These are the pre-parity GPU numbers. PARITY.md found `hmax` spikes, missing infiltration and a wrong gauge start level in them, so
read them as the bar today's published model sets, not as its true skill.

## Headline pools (box-wide; 90 % two-stage cluster-bootstrap CI)

| pool | sites (labels) | metric | rule (p_close ≥ 0.5) | top 1 % | top 2 % | **top 3 %** | top 5 % | top 10 % |
|---|---|---|---|---|---|---|---|---|
| **OOS-7 held-out** | 27 (29) | site recall | 0.185 [0.04, 0.36] | 0.111 | 0.148 | **0.222 [0.07, 0.41]** (6/27) | 0.259 | 0.407 |
| | | chance / lift | 0.042 / 4.4 | 0.020 / 5.7 | 0.039 / 3.8 | 0.058 / 3.9 | 0.095 / 2.7 | 0.184 / 2.2 |
| | | FSS 300 m | 0.020 [0.007, 0.037] | 0.021 | 0.016 | **0.015 [0.006, 0.027]** | 0.017 | 0.013 |
| | | FSS 100 / 1000 m | 0.019 / 0.035 | | | 0.014 / 0.034 | | |
| | | PR-AUC segment / site (storm mean) | 0.007 / 0.008 | | | | | |
| dev-2 (sep2023 + aug2021) | 83 (139) | site recall | 0.373 | 0.217 | 0.349 | 0.398 [0.31, 0.55] | 0.482 | 0.627 |
| | | FSS 300 m | 0.250 | 0.229 | 0.271 | 0.220 | 0.202 | 0.150 |
| all 9 | 110 (168) | site recall | 0.327 [0.15, 0.40] | 0.191 | 0.300 | 0.355 [0.18, 0.43] | 0.427 | 0.573 |
| | | label recall (RECALL.md unit) | 0.339 (57/168) | 0.196 | 0.315 | 0.369 | 0.423 | 0.554 |
| | | FSS 300 m | 0.095 [0.015, 0.20] | 0.102 | 0.096 | 0.074 | 0.064 | 0.047 |
| | | PR-AUC segment / site | 0.022 / 0.028 | | | | | |

"Useful" FSS (0.5 + f₀/2) is about 0.50 for every storm except sep2023, where it is 0.53 box-wide and 0.59 in Leominster city.

## What the baseline says

1. **It reproduces the existing counts.** There are 168 matched labels over the 9 storms and 29 on OOS-7. The rule catches 5 of the 29
   held-out labels (RECALL.md: "5 of 29 for the default").
2. **Held-out skill is concentrated at the very top of the ranking.** The lift is 5.7 at 1 % and falls to 2.2 at 10 %. The adoption operating
   point (3 %) catches 6 of 27 held-out sites; adoption needs at least 8 of 27.
3. **No storm reaches "useful" FSS at any scale except sep2023 inside Leominster.** In Leominster the rule's FSS is 0.49 / 0.56 / 0.64 at
   100 / 300 / 1000 m against a useful level of 0.59. That makes 1000 m useful there and 300 m just short.
   - On OOS-7 the rule's FSS at 300 m is 0.020, barely above random flagging of the same share (per-storm chance at 300 m is 0.010–0.031).
     It beats chance clearly on jul2021 and sep2021 (0.044 and 0.047 against 0.016 and 0.015) and is below chance on aug2023, jul2023 and sep2022.
   - The held-out storms have few, scattered reports (f₀ ≈ 0.2–0.5 % of road length), so FSS stays small there. Its job is to rank variants
     against each other and against chance, not to be read as an absolute grade.
4. **CSI is meaningful only in the complete Leominster DPW domain.** There, site CSI is 0.29 for the 20 m LOSO run and 0.30 for the GPU
   headline run. Everywhere else, unreported floods count as false alarms, so CSI is about 0.01–0.06 and should not be read.
5. **The extra sep2023 runs show why the rule has to use a fixed share.**
   - The 10 m run flags 10.7 % of segments and gets the highest rule recall (0.48), but its lift is only 2.4 and its recall at 3 % is the
     lowest (0.18).
   - The dams run gets 0.38 at 3 % and the GPU run 0.41.

## Method notes

- The FSS window is a square of equal area to a disk of radius *r* on a 20 m road-length raster. It is a Euclidean stand-in for along-road
  distance, so it can count parallel roads and grade-separated crossings within *r*.
- An exact label observes its matched segments. An approximate or town label is spread over the road within 500 m or 1500 m.
- Runs without `features_<storm>.csv` (gpu, 10m and d3) use every segment with a road point in the box. That gives 1–3 % more segments than the
  model's own in-box set, and their matches are recomputed at strict 30 m.
- Ranking is by `p_close`, then depth, with random tie-breaks averaged over 5 seeds. Most segments have `p_close` = 0, so at 10 % the order
  is mostly by depth.
