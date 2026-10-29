# Static flood-hazard maps vs the event model

**Question reviewers ask:** "Does a static flood map, such as the FEMA 100-yr zones or a consultant's 100-yr model, already tell you which
roads close?" This page answers it with a comparison that was fixed before any result was seen. Section 1 is the pre-registration. It was
committed (with `proto/static_maps.py` and `.github/workflows/static_maps.yml`) before the workflow had ever run, so no static-map
flag or score existed when it was written. Section 2 holds the results.

## 1. Pre-registration (29 Oct 2026, before any static map was fetched or scored)

### 1.1 Maps

| map | source | zone used |
|---|---|---|
| **FEMA SFHA** (primary) | FEMA National Flood Hazard Layer, flood hazard zone polygons. Primary copy: the MassGIS statewide NFHL (`FEMA_NFHL_POLY`, `download.massgis.digital.mass.gov/shapefiles/state/nfhl.zip`; the MassGIS page, Jul 2025, says it holds FEMA data published as of 18 Jul 2025, latest study effective 8 Jul 2025, latest LOMR 9 Jul 2025). FEMA's own NFHL MapServer (`hazards.fema.gov`, layer "Flood Hazard Zones") is queried too, as a cross-check, and becomes the source if the MassGIS download fails. Whichever was used, and its date, is recorded in §2. | Special Flood Hazard Area, 1 % annual chance: `SFHA_TF = T` (zones A, AE incl. floodway, AH, AO, AR, A99, V, VE) |
| FEMA 0.2 % zone, reported separately | same | shaded X: `FLD_ZONE = X` with `ZONE_SUBTY` "0.2 PCT ANNUAL CHANCE…" or "…REDUCED FLOOD RISK DUE TO LEVEE". Reported on its own (0.2 % band only), and as the full 500-yr extent (SFHA ∪ 0.2 %) |
| **BSC Group / MRPC Leominster** | BSC Group for the Montachusett RPC, Leominster Flood Solutions (`services7.arcgis.com/vZE8iWev3YlXRRXa/.../LeominsterFlooding_CurrentTimeHorizon/FeatureServer/0`, and any sibling `LeominsterFlooding_*` services of the same organisation). Public layer; the owner approved its use. | each `TimeHorizon` × `ReturnPeriod` group as published. The **current-horizon 100-yr extent** is primary; 2050 and 2070 are secondary. Leominster only. |

### 1.2 What "flagged by a static map" means

A road segment of `docs/graph_segments.json` (the District 3 MassDOT road graph, the same segments the model and `score_v2` use) is
flagged by a map when:

- **intersects** (primary): any length of the segment lies inside the zone, or
- **≥ 30 %** (stricter): at least 30 % of the segment's length lies inside the zone.

Lengths are exact line–polygon intersections in EPSG:26986, computed on the whole segment (all parts, not clipped to a model box). Polygons
are unioned per map first, so overlapping or duplicated polygons are not counted twice. The flag is the same for every storm, because a
static map gives the same answer for every storm.

### 1.3 Scoring

Each static map is scored as a run with `proto/score_v2.py`, on the model's own run boxes and universes: the clean CPU parity catalogue
`docs/proto/parity/catalog/<storm>_<area>_20m` (`parity/BASELINE.md`), its `features_<storm>.csv` universe and its published matches.
So the sites, strict 30 m matching, 150 m site clustering and exact chance recall are identical to the model's. Nothing in the run
folders is changed. The static flag is fed in as `p_close` ∈ {0, 1}, so its rule-level block is "flagged by the map".

- **(a) Held-out 23** (PROTOCOL v2 §2: OOS-7 + NEW16), current default labels (round 2), box domain. **Primary.** The towns domain is
  secondary.
- **(b) Leominster sep2023** (development storm, in-sample for the model): box domain and Leominster city domain (complete DPW
  inventory), with default labels and again with `SCORE_CROWD=1` (the resident crowdsource layer, `obs/CROWD.md`).
- **BSC/MRPC map:** this map covers Leominster only, so it is scored on the **Leominster city domain**. That means sep2023, which is
  primary for this map, plus, as a secondary pool, any held-out storm whose box contains Leominster segments and has sites there.

**Comparisons**, all pooled over storms, with site recall, exact chance recall, lift = recall / chance, and FSS at 300 m:

1. **Static map vs the model at the same flagged share (primary).** A static map flags a fixed set of segments, and so a fixed share
   *s* of each domain. The model is scored at its top *k* = the same number of segments in the same domain (ranked by `p_close`, then
   depth; ties at random, 5 seeds, as in `score_v2`). The two then have equal chance recall, so this is the fair comparison.
2. **Static map vs the model's deployed rule** (`p_close` ≥ 0.5). The shares differ here, so lift is the number to read.
3. **Uncertainty:** a paired two-stage cluster bootstrap (storms, then sites within each storm), 2000 replicates, seed 0. It gives the
   pooled recall difference (static − model), its 90 % CI and a two-sided bootstrap p.

**How the primary result will be read (fixed now).** Primary row: FEMA SFHA, intersects, held-out 23, box domain, vs the model at the same
share.

- **"Static map ≥ model"** if Δ = static − model has a 90 % CI lower bound > 0.
- **"Model > static map"** if the CI upper bound is < 0.
- **"No detectable difference"** otherwise.

The ≥ 30 % variant, the 0.2 % rows, the towns domain, sep2023 and the BSC map are secondary and descriptive. With about 12 secondary rows,
a single one with p < 0.05 is not evidence on its own. This is a benchmark, not a model change: nothing here can alter the deployed
model, the forecast, the site or the default scoring.

**Exploratory only (not a decision):** the obvious hybrids, scored at their own shares against the model rule:

- model rule ∪ static map (flag if either flags),
- model rule restricted to segments **outside** the static zone.

These are shown for FEMA SFHA (intersects and ≥ 30 %) and for the BSC current 100-yr extent. Their shares are larger or smaller than
the rule's, so only lift is comparable. No hybrid is adopted from this page. Adopting one would need its own pre-registration under
PROTOCOL v2 §5.

**What a static map cannot do, by construction (stated before the results):** it carries no timing (no lead time, no "closed from 14:00
to 18:00"). It gives the same answer for every storm, whether 30 mm or 200 mm of rain fell and wherever the rain fell. And it says nothing
about pluvial / urban ponding away from mapped streams, or about culvert-overtopping on small unmapped channels. **What it can do well:**
mark riverine floodplains of mapped streams, where many long-duration closures happen. So the expectation, written down now, is that
it should catch riverine sites at a cost of a large flagged share.

### 1.4 Mechanics

- Runs on GitHub Actions (`.github/workflows/static_maps.yml`, manual dispatch, never commits). The workspace shell cannot reach FEMA,
  MassGIS or ArcGIS Online. The per-segment flags (`{map: {segment: % of length inside}}`, % floored, at least 1 when there is any overlap)
  come back gzip+base64 in `::notice` annotations, read with `gh api …/check-runs/<job>/annotations`. Neutral check runs are the
  fallback channel.
- `python proto/static_maps.py decode --run <run id> --out docs/proto/static/static_flags.json`, then
  `python proto/static_maps.py score --flags docs/proto/static/static_flags.json --out docs/proto/static/results.json --md docs/proto/static/results.md`.
- If a fetch fails for a technical reason, it is rerun unchanged. No map, threshold or storm is changed after a result has been seen.

## 2. Results (29 Oct 2026)

**Short answer.** On the 23 held-out storms, the FEMA 100-yr zone does about as well as the model's own ranking when both flag the same
share of road (32 vs 36 of 98 sites at 7 %; the difference is not significant). It does so by flagging 7 % of all roads in every storm,
at the same places every time. The model's alert tier is about 3 times more concentrated (lift 6.4 vs 2.2). The two catch largely
different sites.

### 2.1 Sources actually used

- **FEMA NFHL: the MassGIS statewide copy** (`nfhl.zip`, HTTP Last-Modified 24 Jul 2025; per the MassGIS page, FEMA data published as
  of 18 Jul 2025, latest study effective 8 Jul 2025, latest LOMR 9 Jul 2025). It gave 40,153 polygons in the District 3 bbox:
  20,715 SFHA and 19,383 shaded-X.
- **Cross-check against FEMA's NFHL MapServer** (`hazards.fema.gov/.../NFHL/MapServer/28`, 495 tiles, 51,130 features). The two give
  the same SFHA segments: 3,848 vs 3,830 intersecting, 3,822 in both, Jaccard **0.99**; at ≥ 30 %, 989 vs 982, Jaccard 0.98.
- **District-wide flag counts** (of 52,698 graph segments):

  | zone | intersects | ≥ 30 % of length |
  |---|---|---|
  | SFHA | 3,848 (7.3 %) | 989 |
  | 0.2 % band only | 2,482 | 624 |
  | 500-yr extent (SFHA ∪ 0.2 %) | 5,096 | 1,660 |

- **Coverage gap:** no segment touches an SFHA in Brookfield, East Brookfield, New Braintree, Oakham, Phillipston, Warren, West
  Brookfield or Winchendon, most likely because those towns have no digital FIRM in the NFHL. The map is scored as published, so roads
  there count as unflagged. The 21 polygons of subtype "X, 1 PCT DEPTH LESS THAN 1 FOOT" fall in neither class.
- **BSC/MRPC Leominster:** one service, `LeominsterFlooding_CurrentTimeHorizon/FeatureServer/0`, 8,817 polygons (all fetched), in three
  groups: current 2,997, 2050 2,934, 2070 2,886, all `ReturnPeriod` 100. It touches **749** Leominster segments now (259 at ≥ 30 %),
  835 in 2050 and 860 in 2070.
- **Transport and a fix:** workflow run 40948284120, flags returned in 9 annotation chunks (`static_flags.json`). The run's own `score`
  step failed on a bookkeeping bug: pooling the Leominster-only map rows over non-Leominster domains raised a KeyError. That was fixed in
  `static_maps.py` after the pre-registration commit (it skips map rows absent from a domain, as §1.3 specifies). Scoring was then run
  locally on the same flags. No method, map, threshold or storm changed.
- **Check:** the model rows reproduce the round-2 baseline exactly (held-out 23: 98 sites, rule 9 / 98 = 0.092, lift 6.4).

### 2.2 Results table (box domain; full table with the towns domain and every row: `results.md`, data `results.json`)

Recall = site recall. Same share = the model's top-*k* segments, with *k* = the static map's flag count in each storm box, so chance
recall is identical. Δ = static − model, paired two-stage bootstrap, 2000 replicates, 90 % CI, two-sided p.

| pool | row | flagged share | recall (hits) | chance | lift | model at the same share | **Δ, same share [90 % CI], p** | Δ vs model rule |
|---|---|---|---|---|---|---|---|---|
| held-out 23 (98 sites) | model, deployed rule | 0.46 % | 0.092 (9) | 0.014 | **6.4** | | | |
| held-out 23 | **FEMA SFHA, intersects (primary)** | 6.96 % | **0.327 (32)** | 0.151 | 2.2 | **0.367 (36)** | **−0.041 [−0.178, +0.105], p 0.70** | +0.235 [+0.116, +0.371] |
| held-out 23 | FEMA SFHA, ≥ 30 % | 2.12 % | 0.092 (9) | 0.044 | 2.1 | 0.135 (13.2) | −0.043 [−0.133, +0.053], p 0.50 | 0.000 [−0.082, +0.090] |
| held-out 23 | FEMA 500-yr extent, intersects | 9.06 % | 0.378 (37) | 0.192 | 2.0 | 0.418 (41) | −0.041 [−0.186, +0.119], p 0.72 | +0.286 |
| held-out 23 | FEMA 500-yr extent, ≥ 30 % | 3.23 % | 0.122 (12) | 0.069 | 1.8 | 0.214 (21) | −0.092 [−0.204, +0.022], p 0.22 | +0.031 |
| held-out 23 | FEMA 0.2 % band only, intersects | 3.93 % | 0.214 (21) | 0.090 | 2.4 | 0.224 (22) | −0.010 [−0.143, +0.130], p 0.97 | +0.122 |
| held-out 23 | FEMA 0.2 % band only, ≥ 30 % | 1.05 % | 0.031 (3) | 0.025 | 1.2 | 0.112 (11) | −0.082 [−0.167, +0.010], p 0.16 | −0.061 |
| sep2023 dev (79 sites) | model, deployed rule | 2.16 % | 0.367 (29) | 0.037 | 10.0 | | | |
| sep2023 dev | FEMA SFHA, intersects | 5.79 % | 0.304 (24) | 0.095 | 3.2 | 0.532 (42) | −0.228 [−0.329, −0.139], p < 0.001 | −0.063 |
| sep2023 dev | FEMA SFHA, ≥ 30 % | 1.43 % | 0.063 (5) | 0.024 | 2.6 | 0.342 (27) | −0.278 [−0.367, −0.203], p < 0.001 | −0.304 |
| sep2023 + crowd (106) | FEMA SFHA, intersects | 5.79 % | 0.274 (29) | 0.106 | 2.6 | 0.509 (54) | −0.236 [−0.312, −0.151], p < 0.001 | −0.057 |
| sep2023, Leominster city (73) | model, deployed rule | 3.81 % | 0.397 (29) | 0.064 | 6.2 | | | |
| sep2023, Leominster city | **BSC current 100-yr, intersects** | **48.1 %** | 0.877 (64) | 0.600 | 1.5 | 0.962 (70.2) | −0.085 [−0.140, −0.033], p 0.001 | +0.479 |
| sep2023, Leominster city | BSC current 100-yr, ≥ 30 % | 16.6 % | 0.247 (18) | 0.251 | 1.0 | 0.753 (55) | −0.507 [−0.603, −0.411], p < 0.001 | −0.151 |
| sep2023, Leominster city | BSC 2050 / 2070 100-yr, intersects | 53.7 / 55.2 % | 0.918 / 0.945 | 0.651 / 0.665 | 1.4 / 1.4 | 0.973 / 0.978 | −0.055 (p 0.03) / −0.033 (p 0.30) | |
| sep2023 + crowd, Leominster (100) | BSC current 100-yr, intersects | 48.1 % | 0.870 (87) | 0.631 | 1.4 | 0.972 (97.2) | −0.102 [−0.150, −0.052], p < 0.001 | |

- **Pre-registered verdict (primary row): "no detectable difference."** At the same flagged share, FEMA SFHA ∩ road is not
  distinguishable from the model's ranking on the held-out 23 storms. The 90 % CI runs from −0.18 to +0.11.
- **Context:** the model's own fixed-share recall (round 2) is 0.153 at 2 %, 0.204 at 3 %, 0.286 at 5 % and 0.443 at 10 %.
- **Complementarity** (held-out 23, SFHA intersects, at the same share): of the 32 sites the map catches and the 36 the model's top-*k*
  catches, only **15 are caught by both**; 17 are caught by the map only and 21 by the model only. 29 of the 32 map-caught sites are not
  in the model's alert tier.
- **FSS at 300 m** (held-out, SFHA intersects): 0.025 for the map vs 0.019 for the model at the same share. Both are low, as expected
  for so large a share. At the rule the model reaches 0.051.
- **BSC Leominster held-out pool** (aug2026 only, 5 sites in the city): too small to read. The current 100-yr map flags 48 % of the
  city's roads, and its sites are caught at about chance.
- **Exploratory hybrids** (not a decision; full rows in `results.md`):

  | hybrid | held-out 23: share | recall (hits) | lift | gain over the model rule [90 % CI] | sep2023 (dev) |
  |---|---|---|---|---|---|
  | model rule ∪ SFHA ≥ 30 % | 2.56 % | 0.163 (16) | 2.8 | +0.071 [+0.020, +0.133] | no gain |
  | model rule ∪ SFHA any | 7.28 % | 0.388 (38) | 2.4 | | |
  | model rule restricted to outside SFHA (any) | 0.32 % | 6 of the rule's 9 sites | 6.3 | | 13 of 29 sites |

  On sep2023 the zone holds most of the rule's hits (18 of 29). For comparison, the model's own top 2–3 % gives 0.15–0.20 (ranking alone).

### 2.3 What a static map cannot do, and what it does well

- **Cannot do:**
  - It has no timing (no lead time, no start or end of a closure).
  - It gives the same answer in every storm: it flags the same 7 % of the district's roads for a 30 mm shower and for 200 mm in Leominster,
    and its "alerts" do not move with the rain.
  - It is blank where no digital FIRM exists (the Brookfields, Oakham, Warren, Winchendon …).
  - It does not see pluvial ponding or culvert overtopping on unmapped small channels, which is where many of the model's hits are: 21 of
    its 36 same-share sites lie outside the map's catch.
  - Its precision is low: lift about 2, against the rule's 6.4 on held-out and 10 on the dev storm.
  - "Intersects" also flags every bridge over a mapped stream. Requiring ≥ 30 % of the length inside removes most of that, but it also
    removes most hits (9 of 98).
  - The BSC/MRPC Leominster 100-yr extents flag half the city's roads and sit at chance at ≥ 30 %. They are a planning map, not a closure
    predictor.
- **Does well:**
  - It marks the riverine floodplains of mapped streams. Long-duration closures happen there, and the model under-predicts them in the
    light held-out storms.
  - In 2 of the held-out storms where the model's rule catches nothing (jul2021: 3 of 4 sites; jul2021b: 3 of 4), the zone catches most
    sites.

### 2.4 Conclusion (plain English)

A static FEMA 100-yr map does tell you something about which roads close: on 23 storms the model was never tuned on, roads that touch a
FEMA zone hold about a third of the reported closures. That is about as many as the model's best-ranked roads hold when the model is
allowed to flag the same 7 % of the network. But the map gets there by marking the same 7 % of roads in every storm, with no timing and
a third of the model's precision, and the two catch mostly different sites. On the Leominster storm the model beats the map clearly at
equal share (in-sample), and the consultant's 100-yr extents, which cover half the city's roads, are no better than chance at a strict
threshold. The honest reviewer answer is: "static maps are a competitive baseline for *where* riverine closures happen, not a substitute
for *which roads close in this storm, and when*." The overlap suggests a hybrid is worth a proper pre-registered test. This page does not
adopt one.
