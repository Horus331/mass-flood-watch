# Terrain conditioning: results (1 Nov 2026)

Pre-registration: `PREREG.md` (commit cee7c90b, before any run). Runs: GitHub Actions `parity_test.yml`, branch `terrain-fix`, run
41319171613, 100 CPU runs at one commit (in-run baseline, T1, T2 and the B0 arm of `runoff/B0_V2.md`), all 25 non-locked storms, all
succeeded. Run folders `runs/<arm>/<storm>_<area>_20m/` (230 MB) are kept on branch `terrain-fix` only, not on main; scores `score_<arm>.json`; verdicts `compare_t1.json`, `compare_t2.json`;
artefact counts and every changed segment `depths.json`.

## Verdict: neither candidate is adopted (PROTOCOL v2 §5a, k = 2). Both stay opt-in. The displayed replays do not change.

| held-out 23 (98 sites) | in-run baseline | T1 notch fix | T2 notch fix + buried-stream conveyance |
|---|---|---|---|
| site recall at 3 % [90 % CI] | 0.194 [0.10, 0.29] | 0.200 [0.11, 0.29] | 0.194 [0.10, 0.29] |
| Δ vs baseline (lower bound at α/2) | – | +0.006 (−0.033) | 0.000 (−0.053) |
| FSS@300 at 3 % | 0.0223 | 0.0232 | 0.0222 (Δ −0.0001) |
| alert tier (P ≥ 0.5): sites, lift | 8 / 98, 6.27 | 7 / 98, 5.86 | 7 / 98, **7.19** |
| §5a checks failed | – | gain, significance | gain, significance, FSS (by 0.0001) |
| dev storms 3 % (sep2023 / aug2021) | 30 / 3 | 30 / 3 | 29 / 5 |
| USGS gauges: mean per-storm rise error, bias | 0.371 m, −0.35 m | 0.371 m, −0.35 m | **0.359 m, −0.33 m** |

`python proto/score_v2.py --compare docs/proto/terrain/score_base.json docs/proto/terrain/score_t2.json --protocol v2 --k 2` reproduces the T2 row.

**Reading.** The fixes do what they were built to do and are skill-neutral: they neither find nor lose documented sites beyond ±1 per storm
(T2 at 3 %: aug2021 +2 and sep2023 −1 on the dev storms; held-out sep2021 +1, jul2021 +1, aug2026 −1, sep2019 −1; at the rule jul2021 +1,
aug2021 +1, aug2026 −1, sep2022 −1). They remove spurious deep
water that was never matched to a report, so the alert tier flags fewer roads (779 → 586 flagged segments over 25 storms) at the same
recall per flag (lift 6.3 → 7.2). Under the protocol that is not an adoption: the rule needs +0.04 recall at 3 %.

**In-run baseline vs the published catalogue.** Identical on 24 of 25 storms. aug2026 differs by one site (rule 3 → 2, 3 % 5 → 4), so the
in-run baseline is 0.194 at 3 % against 0.204 in `obs/round2/score_round2.json`. Not investigated further (aug2026 is the newest storm; an
input on Hugging Face or the MRMS fetch has probably changed since 23 Oct). The pre-registered reference is the in-run baseline.

## The artefacts, before / after (all 25 storms)

| | baseline | T1 | T2 |
|---|---|---|---|
| segments with peak depth > 1 m (storm × segment) | 72 | 70 | **21** |
| > 2 m | 12 | 13 | **1** |
| > 3 m | 5 | 3 | **0** |
| flagged at P ≥ 0.5 | 779 | 724 | 586 |

Named problems (peak road depth, m):

| segment | storm | baseline | T1 | T2 |
|---|---|---|---|---|
| 51395 Route 2, Leominster (cause: chained culvert notches at the I-190 interchange, not a bridge) | sep2023 | **8.49** | 0.13 | 0.13 |
| 12771 (unnamed, Worcester, near Lincoln Sq.) | sep2021 | 5.60 | 0.24 | 0.20 |
| 45260 MLK Jr Blvd | sep2021 / aug2021 | 4.54 / 3.57 | – / 3.70 | 1.45 / 0.63 |
| 45256 MLK Jr Blvd | sep2021 / aug2021 | 3.83 / 2.87 | – / 3.00 | 0.54 / 0.09 |
| 45281 / 45277 Foster St | sep2021 / aug2021 | 2.79 / 1.85 | 1.79 / 0.94 | 0.04 / 0.02 |

Figures: `fig_worcester_sep2021.png` (downtown Worcester; cells > 1 m deep go from a closed pond along MLK Jr Blvd to the conduit line
only), `fig_route2_sep2023.png` (the 8.5 m pit on Route 2 disappears; the river and its real floodplain are unchanged).

**Other segments affected (problem 2, "list other segments").** Depth drops of ≥ 1 m: T1 5 segments (51395 Route 2; 12771; 50650
Route 122, Northbridge, aug2021 1.82 → 0.02; 50710 Providence St, Millbury, aug2021 1.20 → 0.01; 45281 Foster St); T2 15 segments (the
above plus MLK Jr Blvd 45255/45256/45260, Foster St 45277, Bridge St 38477, Major Taylor Blvd 45280/45283, Commercial St 34683, Thomas St
47031/47749 — all downtown Worcester on the Mill Brook conduit line). Every segment whose depth changes by ≥ 0.5 m or whose flag flips is
in `depths.json` (`affected`): T1 135 storm-segments (89 flags off, 34 on, mostly small changes at notched crossings around 0.30 m), T2 343
(258 off, 65 on).

## What the bridge question turned out to be

Route 2 at 42.5269 N, 71.7309 W runs on an embankment over culverts at the Route 2 / I-190 interchange (NAACC `xy4252683071730952`, "Culvert
on I190"; TIGER road-stream crossings). The lidar crest along it is continuous (no deck gap) and the nearest NBI structure carrying Route 2 is
341 m away, so the bridge rule correctly did not drop these points. The 8.5 m was water in a 3 × 3 notch cut 25 m below the road by the
notch chaining described in `PREREG.md` §1(a). The general rule fixed is the notch (T1), not the bridge mask. The bridge mask itself was not
changed.

## What it means for the site

- No setting changes in the display runs (rule: only adopted settings). The whole-district / box reruns keep the deployed env.
- The artefacts stay visible in the published replays and are named in `about.html` (Limitations), now with their cause and the tested,
  skill-neutral opt-in fix: `LF_NOTCH_FIX=1 LF_CHAN_ENFORCE=1`.
- **Decision for the owner (not taken here):** T2 is a pure artefact fix with no measurable skill change (Δ 0.000, FSS −0.0001, lift up,
  gauges slightly better). PROTOCOL v2 has no route for "skill-neutral, physically correct" changes; if the advisor agrees to one (e.g. a
  non-inferiority rule: Δ lower bound > −0.05, FSS within −0.001, gauges not worse), it would have to be written as PROTOCOL v3 *before*
  being applied, and then the display reruns would use `LF_NOTCH_FIX=1 LF_CHAN_ENFORCE=1`.
