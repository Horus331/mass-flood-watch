# Crossing damage layer (roadmap T7): stream power at road-stream crossings

Reproduce: `python proto/damage.py evaluate` (about 1.5 minutes, committed data only). Numbers: `damage.json`. Layer model: `damage_model.json`.
Runs: `.github/workflows/damage_runs.yml` → `docs/proto/damage/runs/<run>/` (crossing table `crossings_<storm>.csv`, `xings_peak.json.gz`, gauge `score.json`).

## Verdict

- **Not adopted. It stays opt-in (`PROTO_DAMAGE=1`) as a separate, experimental layer.** It never touches `p_close`.
- **It fails the pre-set success test.** The roadmap test was that the damage layer's AUC interval must exclude the HDS-5 overtopping layer's AUC.
  - Stream power ranks reported crossing damage in Leominster better than the overtopping layer: ROC-AUC **0.78 against 0.68**.
  - The paired 2 km block-bootstrap interval of the difference is **[-0.06, +0.19]**, which includes zero.
- **It does help where it counts for a watch list:**
  - PR-AUC is **0.155 against 0.094**, and the paired interval of the gain, [+0.005, +0.16], excludes zero.
  - With 10 % of crossings flagged it catches **11 of 35 damage sites, against 8** for the overtopping layer. Chance is 2.7 sites.
  - That is +3 sites, inside the roadmap's expected +2 to +6.
- **There is no true held-out storm.** Damage labels exist for only one catalogue storm, Leominster in September 2023 (news plus the DPW inventory). The other storms have only closure labels, apart from one approximate washout in September 2021.
  - So "leave-one-storm-out" on Leominster falls back to the **literature prior**, which has no parameter fitted on labels. That is what the Leominster numbers above use.
  - A fitted logistic adds nothing. Fitted in-sample it gives AUC 0.78, the same ranking as ω. Leave-one-4 km-block-out within Leominster gives AUC 0.54.
- **The prior's probability scale is wrong, though its ranking is useful.** P ≥ 0.5 (ω ≥ 300 W/m²) flags 34 % of Leominster crossings and 14–23 % in other storms.
  - The layer therefore publishes `damage_p` from the all-storm fit, calibrated to reported damage. Use `damage_p` as a ranking, not as a probability.
- **Before adoption it needs:**
  1. A second storm with damage labels (Vermont July 2023 or Irene 2011 FEMA Public Assistance sites, MassDOT damage records).
  2. A fix for the stream power at large rivers (see Caveats).

## Method

**Runs.** All 9 AWS-era catalogue storms plus the headline Leominster box (`leo48_cn088`) were rerun on CPU in GitHub Actions with the clean parity baseline (`parity/BASELINE.md`): `LF_PARITY=1`, `LF_CN_SCALE=0.88`, `LF_LOSS=cn`, `LF_INFIL_MMH=2`, `LF_QOUT=1`, `LF_VOUT=1`, 20 m, with the same boxes and hours. All 10 reruns reproduce the baseline's gauge `mean_abs_rise_error_m` exactly (for example, sep2023 0.23 m, aug2021 0.40 m, jul2021 1.32 m).

**Per crossing** (`damage.py extract`, every crossing notch the run opened, 616–1,347 per box):

| field | source |
|---|---|
| Q | peak flow through the notch block from the LF_QOUT face fluxes (`xings.json` `q_peak_m3s`, 30 min snapshots) |
| S | least-squares gradient of the routed DEM (`z.npy`) along the D8 flow path, ±50 m around the channel cell, with notch cells excluded; clipped to 0.0005–0.3 |
| w | surveyed bankfull width (MA Stream Crossings Project) if known; otherwise the channels30 width (NHDPlus HR area, Bieger et al. 2015); otherwise Bieger from the D8 area |
| ω | γ Q S / w (W/m²) |
| overtopping | peak upstream water surface (wet cells within 60 m outside the notch) minus the road crest (highest DEM cell of the block before the cut) |
| HDS-5 | Q / Q_crest and P = Φ(ln(Q / Q_crest) / 0.30) for NAACC-surveyed barrels (`prototype.culvert_probability`) |
| other | peak speed (`vel_max.npz`), drainage area |

**Fragility.** P = logistic(b0 + b1 ln(ω/300) + b2 clip(over, −1, 1)).
- **Prior:** b0 = 0, b1 = 1.5, b2 = 0. P = 0.5 at 300 W/m², the level above which floods do major channel work (Magilligan 1992; Anderson et al. 2017 map Irene bridge damage on stream power).
- **Fitted:** L2 logistic, leave-one-storm-out. The prior is used whenever the training storms hold fewer than 5 positive crossings.

**Labels and matching.**
- **Labels:** damage types only (culvert_failure, washout, sinkhole, bridge_damage, other_damage). Closure types are not used.
- **Strict matching:** exact-coordinate labels, joined single-link within 150 m into sites. A site is reachable when a crossing lies within 50 m. A crossing within 50 m of a site is a positive.
- **Tolerant matching** (context only, because chance recall inflates): approximate labels matched to crossings on the same road name within 1.5 km.

**Metrics.**
- ROC-AUC and PR-AUC over crossings.
- Site recall with the top 2 / 5 / 10 % of crossings flagged. Ties are broken at random (20 seeds), with exact chance recall.
- Uncertainty: a paired 2 km block bootstrap (2,000 replicates) against the HDS-5 / overtopping layer.
- A storm-level bootstrap is impossible with one labelled storm.

## Results: Leominster, 11–12 Sept 2023 (catalogue box, held out: no label-fitted parameter)

616 crossings (615 carry flow), 114 damage labels in the box (69 exact), 35 strict sites. **23 of the 35 sites lie within 50 m of a crossing**; the other 12 are road-edge washouts on streets with no mapped crossing. That gives 27 positive crossings (19 culverts, 8 bridges) and a base rate of 4.4 %.

| score | ROC-AUC [5–95 %] | PR-AUC [5–95 %] | sites at 2 % | at 5 % | at 10 % |
|---|---|---|---|---|---|
| **ω (prior fragility = LOSO fold)** | **0.78** [0.66, 0.85] | **0.155** [0.08, 0.27] | 1.0 | 4.0 | **11.0** |
| HDS-5 / overtopping layer (P(HW > crest) for surveyed barrels, else Φ(over / 0.10)) | 0.68 [0.60, 0.79] | 0.094 [0.05, 0.15] | 1.3 | 3.6 | 8.0 |
| overtopped yes/no | 0.57 | 0.056 | 1.05 | 2.25 | 5.2 |
| upstream drainage area | 0.59 | 0.054 | 0.65 | 1.0 | 1.0 |
| peak Q alone | 0.81 [0.74, 0.86] | 0.122 | 0.0 | 3.0 | 8.0 |
| peak speed | 0.63 | 0.065 | 0.0 | 1.0 | 3.0 |
| chance | 0.50 | 0.044 | 0.7 | 1.4 | 2.7 |

How to read the table:
- **Sites columns:** out of 35, with 12, 31 and 62 crossings flagged.
- **Paired differences, ω minus the HDS-5 layer:** ROC-AUC [−0.06, +0.19], PR-AUC [+0.005, +0.16].
- **At 10 % flagged, by source:**
  - News sites: ω 5 of 14, HDS-5 3.
  - DPW sites: ω 8 of 27, HDS-5 7.
  - Counting only the 23 reachable sites, ω catches 48 %.
- **Tolerant matching** (37 approximate sites): ω 4 / 8 / 9 at 2 / 5 / 10 %, HDS-5 2.4 / 5.4 / 9.0. Chance recall is 0.02 / 0.06 / 0.11.
- **Headline Leominster box** (`leo48_cn088`, 48 h): ω ROC-AUC 0.80 and PR-AUC 0.14, with the same site counts (1 / 4 / 11). The HDS-5 layer gets 0.69 and 0.08.

**Fitted fragility.** The all-storm fit (only Leominster has positives) is b0 = −4.79, b1 = 0.99, b2 = 0.30 (n = 8,768, 27 positives).
- In-sample on Leominster it gives AUC 0.78 and PR-AUC 0.16, no better than ω alone.
- The overtopping term carries little: continuous over_m alone has AUC 0.61.
- Within-storm 4 km block CV gives AUC 0.54 and PR-AUC 0.05. The pooled per-block fits are unstable with 27 positives.
- Post hoc, not used for the verdict: ω on the structure span instead of the bankfull width gives AUC 0.80 and PR-AUC 0.20.

**Other storms.** There are no damage labels, so they have no held-out score. The prior flags (ω ≥ 300) are:

| storm | share flagged |
|---|---|
| aug2021 | 14 % |
| aug2026 | 23 % |
| sep2021 | 19 % |
| sep2022 | 6 % |
| aug2023 | 3 % |
| aug2023b, jul2021, jul2023 | ≤ 1 % |

The intensity order is sensible, but the level is too high. The fitted model gives no crossing p ≥ 0.5 anywhere. Its counts of crossings with p ≥ 0.10 are Leominster 16, aug2026 4, sep2021 1, aug2023 1.

## Layer and cost

`python proto/damage.py layer --crossings <csv> --out damage.geojson [--model damage_model.json]`, or `PROTO_DAMAGE=1` in `proto/prototype.py`, which writes `out/damage.geojson` plus `damage_crossings.csv` and adds `summary.json → damage`.

Each crossing carries:
- `damage_p` (fitted model; a ranking)
- `omega` (W/m²), `q_peak_m3s`, `over_m`
- `p_overtop` (the HDS-5 layer)
- `repair_class` and `repair_low_usd` / `repair_high_usd`
- `expected_cost_usd` = damage_p × the geometric mean of the replacement range
- `why`, for example: "stream power 2,723 W/m2 (… m3/s on a …% slope, … m wide channel) - above the ~300 W/m2 at which floods rework channels and scour fills; water 0.23 m over the road crest"

Replacement costs come from `proto/risk.py culvert_cost`: Massachusetts Stream Crossing Standards span of 1.2 × bankfull, VTrans 2014 Irene unit costs, in 2023 $.

Expected repair cost summed over crossings (2023 $, fitted model):

| storm | expected repair |
|---|---|
| Leominster sep2023 | $11.2M |
| Leominster headline box | $12.3M |
| sep2021 | $6.7M |
| aug2026 | $6.0M |
| aug2021 | $4.9M |
| other storms | ≤ $1.1M |

These are order-of-magnitude figures.

## Caveats

- **The highest ω values are implausible.** Examples are the I-190 crossings of the North Nashua at 15,000–26,000 W/m², and the I-90 crossing in MetroWest.
  - Big rivers have large Q. At 20 m the DEM slope next to a high embankment is too steep, and the Bieger width under-sizes main stems.
  - These crossings sit at the top of the ranking and did not fail.
  - Capping S at the NHDPlus reach slope, or using the structure span, is the obvious fix. It must be chosen before scoring the next storm.
- **"Unknown" crossings are never positive.** These are TIGER/USGS points with no structure record: 225 of the 616 in Leominster, and none of the 27 positives. This was seen after scoring, so it is not used.
- **12 of the 35 strict sites are not at a crossing.** These are road-edge washouts on Wachusett St and similar streets. A crossing layer cannot catch them.
- **Damage labels are incomplete outside the Leominster DPW domain.** The fitted probabilities therefore under-state the true damage rate.

## References

- Anderson, I., Rizzo, D. M., Huston, D. R., Dewoolkar, M. M. (2017). Stream power application for bridge-damage probability mapping based on empirical evidence from Tropical Storm Irene. *J. Bridge Eng.* 22(5).
- Magilligan, F. J. (1992). Thresholds and the spatial variability of flood power during extreme floods. *Geomorphology* 5, 373–390.
- Bieger, K., Rathjens, H., Allen, P. M., Arnold, J. G. (2015). Development and evaluation of bankfull hydraulic geometry relationships for the physiographic regions of the United States. *JAWRA* 51(3), 842–858.
- Schall, J. D. et al. (2012). *Hydraulic Design of Highway Culverts*, HDS-5, 3rd ed., FHWA-HIF-12-026.
