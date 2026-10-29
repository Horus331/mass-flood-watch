# Resident crowdsource reports: Leominster, Sept 2023

**Source.** "Community Input on Flood Experiences", the public layer behind the Leominster Flood Solutions crowdsource map run by the
Montachusett Regional Planning Commission (MRPC) with BSC Group (ArcGIS Hub `leominsterfloodsolutions-bscgroup.hub.arcgis.com`; feature
service `services7.arcgis.com/vZE8iWev3YlXRRXa/arcgis/rest/services/Flooding/FeatureServer/0`). Residents placed 116 points (pulled
29 Oct 2026) about the 11–12 Sept 2023 flood, each with a category (roadway impassible, high/deep water, swift water, washout, public
infrastructure damage, home damage, trapped, other) and often a comment. A second layer collects 11 proposed solutions.

**Label file.** `proto/data/crowd_sep2023.csv`, catalogue label schema. It keeps the 70 points in road-relevant categories
(impassible, high/deep water, swift water, washout, public infrastructure/roadway damage), dropping exact duplicate points. Day-level
time, `approx` coordinates (resident-placed pins), quote = category or a short road-related paraphrase of the comment. Home-damage,
trapped-in-home and other points, and all personal details in comments, are not stored here.

**Opt-in.** `SCORE_CROWD=1` adds the file to `proto/score_v2.py` (like `SCORE_SCF`). Default off, so no published baseline changes.
sep2023 is a dev storm, not part of the held-out decision set.

## Check against the clean baseline (CPU parity, CN × 0.88, `parity/catalog/sep2023_leominster_20m`)

| labels | sites (150 m) | flagged share | site hits at the rule | recall | chance | lift | recall at 3 % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| catalogue + DPW (default) | 79 | 2.2 % | 29 | 0.367 | 0.037 | 10.0 | 0.380 |
| + crowd (`SCORE_CROWD=1`) | 106 | 2.2 % | 35 | 0.330 | 0.041 | 8.0 | 0.349 |

The crowd map adds **27 new sites** (more than 150 m from any existing label). The unchanged model catches **6 of them (22 %)** at a flagged
share of 2.2 %, about 5× chance. These sites were never used to build or tune the model, so this is an independent check, if a small one.

A looser check (any flagged segment within 50 m of a road-category point, no clustering) gives 22 of 62 points near roads (35 %), and 13 of
39 points more than 150 m from existing labels (33 %), against at most 13 % by chance.

**Also useful beyond scores.** The comments describe cascades in the words of residents and the city: a railroad embankment washed out
under the tracks, culverts on Anthony Road and Arlington Street overtopped and failed, Brooks Pond Dam overtopped and washed out, sinkholes
over a failed culvert on Main Street, a mobile-home park evacuated, the Emergency Management Center flooded, and Route 2 under 4–6 ft of water
with no emergency crossover to reach Leominster Hospital. These are examples for the cascade chapter (`cascade/CASCADE.md`).
