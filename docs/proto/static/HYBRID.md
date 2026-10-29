# Hybrid rule (model rule ∪ FEMA 100-yr zone): pre-registered test on Districts 4–6

**Why.** `STATIC.md` §2.2 found, on the 23 held-out District 3 storms, that the FEMA 100-yr zones (SFHA) and the model catch mostly
different closure sites, and that an exploratory hybrid, *model rule ∪ SFHA covering ≥ 30 % of the segment*, went from 9 to 16 of 98
sites at 2.6 % of segments flagged. That hybrid was chosen after the District 3 results were seen, so it is a hypothesis, not a result.
This page freezes it (and one variant) and tests it once, on storms that played no part in designing it.

Section 1 is the pre-registration. It is committed on its own, with `proto/hybrid_d456.py` and `.github/workflows/hybrid_d456.yml`,
**before** any FEMA polygon has been intersected with a District 4–6 road. Section 2 holds the results.

## 1. Pre-registration (29 Oct 2026)

### 1.1 What has been seen before writing this

- The District 3 static-map results (`STATIC.md`), including the exploratory hybrid rows.
- The District 4–6 transfer results of the frozen model (`transfer/TRANSFER.md`, run r1): rule 18 / 498 sites at 0.14 % flagged (lift
  6.7); top 1 / 2 / 3 % recall 0.10 / 0.16 / 0.21.
- A dry run of `proto/hybrid_d456.py score` **with no SFHA flags** (so H1 = H2 = the rule), to check that it reproduces the transfer
  score (it does: 18 / 498, lift 6.7, 81 storms). That run also printed the box-mean storm rain of each run, after the H2 gate below had
  been fixed in the code: 40 of the 81 storms pass the 40 mm gate.
- **Not seen:** any FEMA flood zone in a District 4–6 storm box, and any hybrid score on District 4–6.

### 1.2 The two frozen variants (k = 2)

A segment is an OSM road segment of the transfer run (`docs/proto/transfer/roads_osm/<run>.json.gz`, the `score_v2` universe of run r1).
*SFHA ≥ 30 %* means that at least 30 % of the segment's length lies inside the FEMA Special Flood Hazard Area, exactly as defined in
`STATIC.md` §1.1–1.2:

- zones with `SFHA_TF = T` (A, AE incl. floodway, AH, AO, AR, A99, V, VE), coastal zones included;
- source: the MassGIS statewide NFHL copy (`nfhl.zip`, the same file as `STATIC.md`; its HTTP Last-Modified is recorded). FEMA's NFHL
  REST service is used only if the MassGIS download fails;
- polygons unioned first; exact line–polygon intersection in EPSG:26986 on the whole segment; % floored.

| variant | flag a segment when |
|---|---|
| **H1** | `p_close ≥ 0.5` (the deployed rule) **or** SFHA ≥ 30 %. This is the exploratory District 3 rule, unchanged. |
| **H2** | `p_close ≥ 0.5` **or** (SFHA ≥ 30 % **and** the storm box's radar storm total, averaged over the box, is ≥ 40 mm). |

**Why H2's condition (fixed without looking at any District 4–6 SFHA result).** The SFHA is a riverine and coastal 1 % floodplain. Mapped
rivers rise on rain averaged over their catchments, not on a single convective cell, and the District 4–6 record is dominated by short
convective bursts (`TRANSFER.md`). The live forecast already runs the flood model only when its rain gate fires (40 mm / 24 h is the
gate's daily threshold, `forecast/GATE.md`), so a hybrid layer in the forecast would only ever be shown in boxes with heavy rain. H2 uses
that gate number on the box-mean storm total (`rain_total_mean_mm` in each run's `flood_meta.json`, MRMS over the run window), because
riverine response integrates over area. It is the form that could be deployed.

### 1.3 Test set (never used to design either variant)

The **District 4–6 transfer pool**: all 81 storms of run r1, 498 sites (`PROTOCOL.md` "Transfer test", `transfer/TRANSFER.md`). The frozen
model runs are reused as they are (features from the work branch `transfer-d456`, commit 04af8c5c; `flood_meta.json` and matches as on
main). Nothing is rerun. `score_v2` matching (strict 30 m, published matches), 150 m sites, exact chance recall. Box domain is primary.
The District 3 locked storms are not touched; District 4–6 storms still never enter a `--compare`, a fold or a fit.

### 1.4 Metrics and comparisons

For each variant, pooled over the 81 storms:

- **Primary metric:** site recall at the variant's own flagged set, with its pooled and mean flagged share.
- **Lift** = recall / exact chance recall at the same share.
- **Precision proxy:** site hits per 1,000 flagged segments.

Comparisons (paired two-stage cluster bootstrap: storms, then sites within each storm; 2000 replicates, seed 0):

- **(A) vs the model rule** (`p_close ≥ 0.5`): Δ = recall(variant) − recall(rule).
- **(B) vs the model's own ranking at the same share:** in each storm box the model flags its top *k* segments (by `p_close`, then depth;
  ties at random, 5 seeds, as in `score_v2`), with *k* = the number of segments the variant flags in that box. Δ = recall(variant) −
  recall(model top-*k*). Chance recall is then identical, so this is the fair test of whether the FEMA layer adds anything the model's
  own ranking does not.

**Significance:** one-sided, α = 0.05 / k = **0.025** (k = 2 variants, `PROTOCOL.md` v2 §5). The lower bound is the 2.5th percentile of
the bootstrap Δ.

### 1.5 Adoption decision (fixed now)

A variant **passes** only if all four hold:

1. Δ(A) ≥ **+0.04** (the PROTOCOL v2 gain size);
2. the one-sided lower bound of Δ(A) is **> 0**;
3. Δ(B) **> 0**;
4. the one-sided lower bound of Δ(B) is **> 0**.

The hybrid must beat both the rule and the model's own ranking at the hybrid's share. If both variants pass, the one with the higher
lower bound in (B) is adopted. If neither passes, no hybrid is adopted, and the page says so.

"Adopted" means only this: the variant may be proposed as a **second, separately pre-registered forecast layer** in the forward test
(`prospective/PROSPECTIVE.md`). Nothing here changes `p_close`, the deployed rule, the live forecast, the archive or the site defaults.

**Descriptive only (cannot change the decision):** SFHA ≥ 30 % alone (vs the model at the same share); the "rule ∪ SFHA any" hybrid;
per district; the number of storms passing the H2 gate.

**What is expected (written now).** On District 3 the hybrid's share (2.6 %) was where the model's own ranking already reaches about
0.15–0.20 recall, and H1 reached 0.16. Districts 4–6 are coastal and densely mapped, so the SFHA share may be larger and condition (B) is
the hard one. A failure of (B) would mean the FEMA layer is a reasonable alert *budget* but not better than spending the same budget on
the model's ranking.

### 1.6 Mechanics

- `.github/workflows/hybrid_d456.yml` (manual, never commits): checks out `docs/proto/transfer/roads_osm/` from `transfer-d456`, runs
  `python proto/hybrid_d456.py fetch`, and returns the per-segment SFHA percentages through `::notice` annotations
  (`static_maps.py emit/decode`).
- Locally: `python proto/static_maps.py decode --run <id> --out docs/proto/static/hybrid_d456_sfha.json`, then
  `python proto/hybrid_d456.py score --flags docs/proto/static/hybrid_d456_sfha.json --runs-root <checkout of transfer-d456> --out docs/proto/static/hybrid_d456.json`.
- If the fetch fails for a technical reason it is rerun unchanged. No zone, threshold, gate, storm or test changes after a result is seen.

## 2. Results (29 Oct 2026)

*(added after the run; section 1 is unchanged)*

**Verdict: neither hybrid is adopted.** Both add sites over the rule, but both lose clearly to the model's own ranking at the same share.
On Districts 4–6 the FEMA layer is a poor way to spend an alert budget: roads with ≥ 30 % of their length in the SFHA hold fewer closure
sites than random roads would (lift 0.67).

### 2.1 What was run

- SFHA: MassGIS statewide NFHL (`nfhl.zip`, HTTP Last-Modified 24 Jul 2025, the same file as `STATIC.md`). It gave 28,288 polygons in the
  81 boxes (+ 3 km), 14,752 of them SFHA. The FEMA REST fallback was not needed.
- Transport: workflow run 40966174644, 81 storm categories returned in `::notice` annotations (sha 10ddca66d659). The first dispatch
  (run 40956902598) was cancelled after more than 1 h inside the intersection step, before it returned anything. The only change before the
  rerun was cutting the unioned zone into 1 km tiles before the line–polygon intersections (`overlap_tiled`): same lengths, same rule.
  On a synthetic check against the untiled `static_maps.overlap_pct`, the floored % moved by at most 1 point on 2 % of segments, and no
  segment crossed 30 %.
- Scored locally with `proto/hybrid_d456.py score` on the r1 run folders of `transfer-d456` (features read from the `.csv.gz`). The model
  rows reproduce `TRANSFER.md` exactly: rule 18 / 498, lift 6.7. The H2 gate passes in 40 of the 81 storms.
- Results: `hybrid_d456.json` (pooled rows, tests, decision, per-storm sums). The per-segment SFHA file is not committed (1.6 MB); rebuild it
  with `python proto/static_maps.py decode --run 40966174644 --out hybrid_d456_sfha.json`.

### 2.2 Results (81 storms, 498 sites, box domain)

| row | mean (pooled) share flagged | site recall (hits) | chance | lift | hits per 1,000 flagged | model's top-*k* at the same share |
|---|---|---|---|---|---|---|
| model, deployed rule | 0.14 % (0.14 %) | 0.036 (18) | 0.005 | **6.7** | 7.3 | |
| **H1** = rule ∪ SFHA ≥ 30 % | 5.74 % (5.43 %) | 0.137 (68) | 0.162 | 0.84 | 0.71 | **0.292 (145.6)** |
| **H2** = rule ∪ (SFHA ≥ 30 % if box-mean rain ≥ 40 mm) | 2.69 % (2.76 %) | 0.088 (44) | 0.095 | 0.94 | 0.91 | **0.184 (91.4)** |
| *descr.* SFHA ≥ 30 % alone | 5.62 % (5.31 %) | 0.106 (53) | 0.158 | 0.67 | 0.57 | 0.290 (144.2) |
| *descr.* rule ∪ SFHA any | 7.54 % (6.85 %) | 0.167 (83) | 0.201 | 0.83 | 0.69 | 0.335 (166.6) |

Paired two-stage bootstrap, 2000 replicates, seed 0; lower bound = one-sided at α / k = 0.025:

| variant | (A) Δ vs rule [lower bound] | (B) Δ vs model top-*k*, same share [lower bound] | checks 1–4 | decision |
|---|---|---|---|---|
| H1 | **+0.100** [+0.066] | **−0.156** [−0.215] | ✓ ✓ ✗ ✗ | not adopted |
| H2 | **+0.052** [+0.026] | **−0.095** [−0.151] | ✓ ✓ ✗ ✗ | not adopted |

By district (descriptive): H1 recall 0.144 / 0.151 / 0.109 and lift 0.87 / 0.93 / 0.70 in Districts 4 / 5 / 6. H2 reaches lift 0.98 /
0.99 / 0.81. H1 adds at least one site over the rule in 36 of the 81 storms.

### 2.3 What it means

- **The District 3 hybrid does not transfer.** On District 3 (held-out 23) the SFHA layer had lift about 2 and the hybrid lifted recall
  from 9 to 16 of 98 at 2.6 % flagged. On Districts 4–6, SFHA ≥ 30 % flags 5.3 % of the OSM road segments (District 3: 2.1 %), and the roads it
  flags hold *fewer* closure sites than chance. That is likely because of what the zone covers there. The boxes are coastal (Lynn,
  Dedham, Fall River, Hingham, the Cape), so the SFHA includes large coastal AE / VE zones, and the transfer catalogue excludes surge and
  tidal flooding by design. Rain closures in these boxes are mostly convective ponding away from mapped floodplains. The shorter OSM
  segments also make "≥ 30 % inside" easier to reach.
- **The rain gate helps but not enough.** H2 halves the share and brings lift close to 1, but the model's own ranking at the same
  2.7 % still catches about twice as many sites (91 vs 44).
- **Condition (B) was the hard one, as section 1.5 expected, and it failed by a wide margin.** Gains over the rule (A) come only from
  flagging 20–40 times more road. Spent on the model's ranking instead, the same budget does much better.
- **For the forward test from 3 Nov:** nothing is added. No hybrid layer is proposed for the live forecast, and the live defaults are
  unchanged. The District 3 exploratory gain stays exploratory. Any future riverine channel should be built as an input to the model
  (for example a channel- or floodplain-aware feature tested under PROTOCOL v2), not as a union with the FEMA map, and it would need a
  coastal-zone exclusion fixed in advance.
