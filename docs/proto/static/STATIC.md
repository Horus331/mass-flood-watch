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

## 2. Results

*(pending: filled in after the workflow run)*
