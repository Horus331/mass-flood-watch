# Road-closure prototype: which road segments close in a flash flood

One storm, one area: rain goes in; flood depth, the road segments likely to close, why, and what it costs the network come out.
Tested end to end on the Sept 11, 2023 Leominster flash flood (MassDOT District 3) on a free 4-core GitHub machine.

```
INPUTS                                PROCESS                                          OUTPUTS
radar rain (NOAA MRMS, hourly)  ─┐
lidar terrain (USGS 3DEP 10 m)  ─┼─▶ 1. flood depth every 30 min                 ─┐
land cover, soils, streams      ─┘     LISFLOOD-FP 8.2 (Univ. of Bristol, open)   │
                                                                                  ├─▶ map.html       clickable map, layers by road class
road segments (class, AADT)     ─┐  2. per segment: peak depth, hours > 30 cm,    │   watchlist.csv  top segments + plain-language reason
stream crossings (culverts)     ─┼─▶    rain flashness (worst hour / storm)       │   segments.geojson
hospitals                       ─┘  3. P(closed) = chance depth > 30 cm           │   REPORT.md      summary + checks
                                    4. culverts overtopped (FHWA HDS-5),          │   summary.json
flood reports, MassDOT repeat   ─▶     detours / cut-off from hospitals          ─┘
flood sites (for checking only)     5. checks against what happened
```

| Step | Code | Open-source / public pieces used |
| --- | --- | --- |
| Flood depth | `sim/colab/w9_lisflood.py` | LISFLOOD-FP 8.2 (GPL, doi:10.5281/zenodo.13121102), built from source with CMake; MRMS rain from AWS Open Data |
| Segment hazard, flashness, P(closed) | `proto/prototype.py` | 30 cm = depth at which an ordinary car stops (Pregnolato et al. 2017; Shand et al. 2011) |
| Culverts, network | `sim/infra/impacts.py`, `sim/infra/culvert.py` | FHWA HDS-5 culvert equations; MA road-stream crossings (USGS / NAACC / MassDOT); Dijkstra routing |
| Output map | `proto/prototype.py` | MapLibre GL, Esri topographic basemap |

**Default since 22 Oct 2026 — 4-connected depression breaching + CN × 0.91.** The depression breaching used to carve 8-connected
outlets; LISFLOOD-FP exchanges water across cell faces only, so outlets that step diagonally drained nothing and ~24 Mm³ of rain stayed
trapped in sealed hollows (113 of the 115 segments still closed at 47 h in Leominster; Lake Quinsigamond and the Millbury gauge in
Worcester). `LF_BREACH_D4=1` (now the default) carves face-connected outlets: dead storage 24.5 → 8.2 Mm³, roads reopen (5 segments closed
at 47 h instead of 115). The trapped water had acted as a hidden loss, so the curve number was recalibrated (CN × 0.91): Fitchburg rise
0.97 vs 1.00 m, peak Q 37.6 vs 43.6 m³/s; Leominster rise 3.24 vs 2.92 m, Q 197 vs 157 m³/s (peak inside the gauge's data gap);
rising-limb timing +0.9 / +0.3 h. Label checks with the current prototype (strict, Leominster): depth rule recall 0.36 at 2.2 % flagged
(lift 11; was 0.39 at 4.5 %); 'overtop' 0.51 at 5.3 % (was 0.74 at 9.7 %); on the 54 Leominster DPW damage points depth 0.39 (lift 15),
overtop 0.39. Part of the earlier recall came from false pools in sealed hollows beside roads; the lower numbers are the honest baseline.
Runs before this change (including the paragraph below) used 8-connected breaching and CN × 1.0.

**Calibration and checks (Sept 2023):** rain losses use the standard NRCS curve number (TR-55, HSG + NLCD impervious, AMC II, no
adjustment factor). Modelled peak river flow matches both in-box USGS gauges: 41 vs 44 m³/s observed at 01094400 (North Nashua at
Fitchburg) and 167 vs 157 m³/s at 01094500 (North Nashua near Leominster); stage rise 1.29 vs 1.00 m and 3.26 vs 2.92 m. Timing
(`proto/score.py`, gap-aware): the modelled rising limb reaches half the event rise 1.7 h and 0.7 h *late* (rise50); the hydrograph centroid
over the 48 h window is 0.4 h and 1.9 h late; the modelled crest is 0.8 h before Fitchburg's and at 00:30Z, inside the 00:30–15:00Z window
in which Leominster's true crest must lie (see below), so its peak-time error is 0 h as an interval and the old −4 h is not a model error. Absolute water levels sit 1.1–1.3 m below the gauge datum, because the lidar DEM holds the river surface at survey
time and the channel bed is burnt approximately, so rise and flow are the scored quantities. Every run is also scored against 13 NWS storm
reports, 11 NOAA Storm Events records and 93 documented road flood/closure/damage sites (`proto/data/`), next to random road points.

*Fixed 21 Oct 2026:* the rain NetCDF was written with y ascending, which LISFLOOD-FP's `DynamicRain` reads one row off, with the north
row reading past the buffer (spurious inflow of ~3×10⁹ m³). Runs before commit "Fix rain file row mapping" (including the earlier ×0.9
calibration) are superseded.

*Peak timing at Leominster (22 Oct 2026, not adopted; defaults unchanged):* the −4 h is a gauge artefact. USGS 01094500 has no 15-min
stage from 00:30Z to 04:30Z and from 04:30Z to 15:00Z on 12 Sept 2023; the one value between the two gaps, 12.54 ft at 04:30Z, is the
highest recorded, and the −4 h was measured against it. At 00:30Z the river was still rising (3.59 m, 132 m³/s) and at 15:00Z it was
well down (9.15 ft), so the record only says the crest was at least 12.54 ft and fell somewhere in 00:30–15:00Z (USGS's estimated
30-min discharge through the gap tops out at 04:30Z, 157 m³/s, but that is itself filled in). `proto/score.py` therefore flags gauges
whose recorded maximum sits next to a gap > 1 h (`gap_flag`), reports the peak time as an interval (`obs_peak_interval_utc`,
`peak_timing_error_interval_h`) and ranks runs on timing that does not need the crest: rising-limb 50 % time (`rise50_error_h`, the
`mean_abs_timing_error_h` used for means) and hydrograph centroid (`centroid_error_h`); the raw peak-time error stays in `timing_error_h`.
Worcester (Aug 2021) has no gaps; there the robust mean is 1.4 h against 3.8 h for raw peak times (01110000 peaks −10 h on a long flat
crest but its rising limb is within 0.1 h). What is real is the shape: the
model rises 1–1.5 h *late* (CN initial abstraction) and recedes far too fast (12:00Z: 13 vs 93 m³/s at Leominster, 4 vs 33 at Fitchburg;
24-h event volume 3.3 vs 7.0 and 0.8 vs 2.2 Mm³). Half of each gauge's drainage area is outside the 20 km box (in-box 146 of 285 km² and
68 of 166 km²) and the CN event loss has no delayed (interflow/baseflow) or reservoir component. Experiments (`docs/proto/exp/mn_*`):
channel n 0.05 (`LF_N_CHAN`, Chow 1959 natural channels with pools/stones) moves the peaks 0.5–1 h later (Leominster −3.0 h) and lifts
label recall 0.385→0.423 (lift 5.8→6.1), but cuts peak Q to 134 / 37 m³/s and raises the Fitchburg rise to 1.42 m (+42 %); NLCD
floodplain n (`LF_N_LANDCOVER=1`, forest/woody wetland 0.12) changes nothing at the gauges; the full North Nashua basin
(box 160000,906000,190000,942000) fixes Fitchburg (45 m³/s, +0.2 h, volume 1.4 Mm³) but leaves Leominster peaking at 00:30Z. The early
Leominster peak is driven by the local cloudburst over the city; the missing slow component needs reservoir/pond storage or a subsurface
term, not a rougher surface.

Closure probability in this prototype is a physics prior, `P = Φ((peak depth − 0.30 m) / 0.10 m)`. In the dissertation it is replaced by a
model learned from observed closures (storm reports, MassDOT records, Vermont 2023).

### Extra closure rules (opt-in, not the default)

Two rules in `proto/prototype.py` target sites the depth rule misses: roads beside or over streams, and washouts. Both use published
thresholds only (none tuned on the labels). The prototype scores all eight variants every run (`checks.labels_segments.variants` in
summary.json: depth, +freeboard, +fastwater, +both, each with and without the culvert rule, strict/loose recall, flagged share, lift, odd/even split).

* `--freeboard` (`PROTO_FREEBOARD=1`): f = road crest − highest peak water surface within 30 m. The crest is the lidar DEM *before*
  channel burn, crossing notches and depression breaching (`z_raw.npz` from w9; the highest 10 m cell in each 20 m cell, since a fill's
  crest is narrower than the cell). The water surface is model DEM + peak depth in cells ≥ 10 cm deep, leaving out the road's own unedited
  cells so its water is not counted twice. `P_fb = Φ((0.30 − f)/0.15)`. The 0.30 m margin is the 1 ft design freeboard between design
  water level and road edge (e.g. Oklahoma DOT Roadway Drainage Manual §9.3.3.3: headwater one foot below the shoulder edge, applied with
  FHWA HDS-5 culvert design). σ = 0.15 m combines lidar error (3DEP QL2, RMSEz ≤ 0.10 m) and modelled water-level error (0.10 m).
* `--fastwater` (`PROTO_FASTWATER=1`, needs `LF_VOUT=1`): on unedited road cells `P_dv = Φ(ln(DV/0.3)/0.35)`. DV₀ = 0.3 m²/s is the
  small-car stability limit (Shand et al. 2011, ARR Project 10 Stage 2; ARR 2019 Book 6 ch. 7). σ_ln = ln(0.6/0.3)/2, the spread across
  vehicle classes. The washout term applies within 30 m of a mapped crossing with ≥ 10 cm over the road: `Φ(ln(V/1.5)/0.30)`.
  1.5 m/s is the permissible velocity of grass on easily eroded soil (SCS TP-61 1954; Chow 1959 Table 7-6).
* `LF_VOUT=1` in w9 adds `hazard` to the LISFLOOD-FP .par. This writes `.maxVc` (peak cell speed every step, m/s) and `.Vx/.Vy` per
  snapshot, and w9 saves `vel_max.npz` (peak speed, and peak depth × speed in m²/s). It does not change the hydraulics: gauge scores are identical.

The test run was experiment `fb_base` (default env + `LF_VOUT=1`, 22 Oct 2026; the run dir is kept in `docs/proto/exp/fb_base/rundir`).
Results on the 78 strict-matched sites:

| variant | strict recall | flagged share | lift (chance-corrected) | loose recall |
| --- | --- | --- | --- | --- |
| depth (default) | 0.385 | 4.65 % | 5.83 | 0.756 |
| + freeboard | 0.756 | 14.25 % | 3.89 | 0.944 |
| + fast water | 0.397 | 4.82 % | 5.81 | 0.767 |
| + both | 0.756 | 14.27 % | 3.89 | 0.944 |

Freeboard doubles recall but flags 14 % of segments and lift falls from 5.8 to 3.9, so it is not adopted. Fast water adds one site, which
is within noise. Defaults stay depth-only. A post-hoc sensitivity check with margin 0 (water at the crest, i.e. overtopping) gives recall
0.744 at 9.8 % flagged and lift 5.45. It was chosen after seeing the labels, so it needs a second storm before any use.
The map shows it as a separate **"may close: stream at road level"** layer (orange dotted; `p_overtop`, `p_may_close` in
`segments.geojson`; `segments_may_close` in `summary.json`). It never changes `p_close`; it becomes part of the closure rule only if it holds on
an independent storm (Vermont July 2023 closures, `proto/data/vt_roadclosures_jul2023.geojson`).
Peak speeds have numerical spikes (max 96 m/s in a few cells; p95 on wet land 3.2 m/s), so read single-cell speeds with care.

**Edge washout (`--edge` / `PROTO_EDGE=1`) blind test, Worcester Aug 2021.** The peak-only variant (`PROTO_EDGE_DURATION=0`) was picked
on Leominster after seeing the labels (strict recall 0.359 → 0.462 public, 0.388 → 0.449 DPW, 4.2 % flagged). Pre-declared pass rule: on
Worcester, peak-only depth+edge must raise strict recall vs depth, with lift ≥ 5 and flagged ≤ 8 %. Run `wo_edge` (22 Oct 2026; current
defaults + `LF_VOUT=1 LF_VDUR=0.6,1.0,1.5,1.8`, 18 h, box 168000,875000,188000,895000; run dir kept in `docs/proto/exp/wo_edge/rundir`),
labels `proto/data/labels_aug2021_worcester.csv` (12 of 14 strict-matched; without W001/W002, the Route 20 underpass rows: 10):

| variant | strict recall (12) | flagged | lift | without W001/W002 (10): recall / lift |
| --- | --- | --- | --- | --- |
| depth | 0.333 | 1.45 % | 19.8 | 0.200 / 11.5 |
| depth+edge, peak only | 0.333 | 1.98 % | 14.5 | 0.200 / 8.5 |
| depth+edge, 1 h weight | 0.333 | 1.53 % | 18.7 | 0.200 / 10.9 |
| overtop | 0.583 | 3.79 % | 13.3 | 0.500 / 11.1 |
| overtop+edge, peak only | 0.583 | 4.23 % | 11.9 | 0.500 / 9.9 |
| overtop+edge, 1 h weight | 0.583 | 3.84 % | 13.1 | 0.500 / 10.9 |

**Fails**: the edge layer adds no Worcester site in either mode (it only adds flagged segments, so lift falls). The Worcester labels are
flooded / closed streets (no shoulder-washout reports), so this is a test of generality, not of washouts as such. Edge stays a candidate
outside `p_close`; defaults unchanged.

## Resilience, warning priority and risk matrix (post-steps)

Three modules read a finished run folder and never change `p_close`. The proto workflow runs them after `prototype.py`. Definitions,
sources and the Leominster numbers are in [`docs/proto/advisors/resilience.md`](../docs/proto/advisors/resilience.md).

* `proto/resilience.py` builds functionality curves Q(t) every 30 min, with segments closed at ≥ 30 cm and slowed at 5–30 cm by the
  Pregnolato curve. It has three variants:
  * Q_eff: global efficiency (Latora & Marchiori 2001).
  * Q_access: residents (2020 Census blocks, `docs/network/census_blocks_ma.npz` from `proto/census_blocks.py` / the census
    workflow, each block on its nearest road segment) within 30 min of a hospital, 8 min of a fire station (NFPA 1710) and 10 min
    of police; it also reports people losing each service at the worst time, person-hours of lost coverage and isolated residents.
    Q_access_km, the earlier road-km version, is kept for comparison.
  * Q_traffic: AADT-weighted serviceable km.

  For each variant it reports the Bruneau et al. (2003) resilience loss ∫(100 − Q)dt, robustness (min Q), rapidity (hours back to
  90/95 %) and AADT-weighted vehicle-hours of delay. Outputs: `resilience.json`, `resilience.png`, `resilience_segments.csv`.
  Leominster: min Q is 59 / 67 / 68 % (eff / access by residents / traffic), RL is 1,284 / 876 / 1,061 %·h over 48 h, and delay is
  about 510,000 vehicle-hours. Of 120,789 residents in the box, 27,000 / 49,000 / 39,000 lose hospital / fire / police coverage at
  the worst time (7–7.5 h), 3.0 million person-hours of coverage are lost over 48 h, and 22,600 are isolated at the peak. No variant recovers to 90 % within 48 h, because ponded depressions keep about 115 segments closed.
* `proto/rating.py` computes a flash-flood index from three things: lead time from heavy-rain onset (≥ 7.6 mm/h) to 30 cm, rise time
  from 5 to 30 cm, and `flashness_pct`. It also writes `warning_priority = p_close × (0.5 + 0.5 FFI)` with warning tiers
  (`warning_priority.csv`), and the event Richards-Baker flashiness at gauges (`rating.json`). Leominster: the median lead of likely
  closures is 2.5 h, and 97 % close within 6 h of the onset.
* `proto/risk.py` builds the risk matrix: likelihood (p_close, or P(overtop) for crossings) × consequence. Consequence is pavement
  repair plus culvert replacement at Stream-Crossing-Standard size (VTrans 2014 unit costs, CPI to 2023), plus user delay
  (USDOT 2016 VOT → $18.13 / person-h × 1.67), plus critical access lost (residents losing access when the segment alone is closed; classes 0 / ≤ 50 / ≤ 500 / ≤ 5,000 / more). It writes `risk_matrix.csv` (top 50, Low / Medium / High /
  Extreme), `risk_matrix.png` and `risk.json`. All costs are order-of-magnitude. Leominster: 32 items are Extreme (17 segments,
  15 crossings; 22 with the earlier road-km bands), and the expected cost is about $68M.

```
python proto/resilience.py --out docs/proto/leominster_sep2023          # ~9 min (all-pairs efficiency, 97 frames x 2)
python proto/rating.py --out docs/proto/leominster_sep2023
python proto/risk.py --out docs/proto/leominster_sep2023 --run-dir <run dir>   # run dir only for crossing status
python proto/resilience.py --selftest; python proto/rating.py --selftest; python proto/risk.py --selftest
```

## Second storm: Vermont, July 10-11 2023 (independent test, nothing tuned)

`.github/workflows/proto_vt.yml`, inputs `sim/colab/vt_inputs.py`, table `proto/vt_report.py`, outputs `docs/proto/vermont_jul2023/`
(map.html, summary.json, watchlist.csv, segments.geojson, RESULTS.md, vt_scores.json). Box EPSG:26986 107000,1096000,127000,1116000
(Montpelier-Barre-Berlin-Northfield, the densest 20 km box: 11 of the 63 VTrans closed stretches). EPSG:26986 is kept (scale 1.0006,
0.73 deg rotation at Montpelier). Inputs, all fetched in Actions: 3DEP DEM (ImageServer, 10 m), MRMS QPE 01H Pass2 (July 9 18Z + 60 h),
NLCD 2021 impervious (MRLC WCS), SSURGO HSG (`sim/soils_sda.py`), NHDPlus HR channels, OSM roads (Overpass; AADT = class defaults), USGS
road-stream crossings + VTrans Small Culvert Inventory sizes (NAACC has no records here), USGS gauges. w9 reads them through
`LF_DATA_DIR` / `LF_CROSSINGS` (MA runs unchanged). Closures are scored as lines: a segment matches when >= 50 % of it lies within 30 m of
the closed stretch or it holds >= 50 % of it. Edge inflows: one-way nesting from a 60 m, 60 x 60 km run of the same model (`LF_INFLOW=file`).

| run (folder) | depth: recall / flagged / lift | overtop | freeboard | culvert | Montpelier peak Q (obs 654) |
| --- | --- | --- | --- | --- | --- |
| default, rain on box only (`no_inflow`, re-scored with PROTO_BRIDGES) | 0.27 / 6.8 % / 0.70 | 0.36 / 10.1 % / 0.76 | 0.64 / 14.0 % / 1.15 | 0.55 / 7.5 % / 1.33 | 147 |
| default + nested inflows (`nested_default`, re-scored) | 0.27 / 6.1 % / 0.75 | 0.36 / 9.5 % / 0.78 | 0.64 / 13.6 % / 1.17 | 0.55 / 6.8 % / 1.41 | 125 |
| LF_BREACH_D4=1 + nested inflows (root folder) | 0.45 / 8.4 % / 0.97 | 0.45 / 10.7 % / 0.86 | 0.64 / 12.4 % / 1.13 | 0.73 / 9.1 % / 1.49 | 96 |

The overtop candidate does not hold on Vermont: it never beats the depth rule on lift, and with D4 it adds no closure. No rule is far above
chance here (lift ~1): only 11 closures, several 3-6 km long (VT-62 matches 41 segments), so random flagging already hits many. The flood
is under-simulated: the big rivers run at 15-20 % of the gauged peaks (Winooski at Montpelier 96 vs 654 m3/s, Dog River 42 vs 312) because
most of their basins lie outside the box and the 60 m coarse run that feeds the edges routes poorly (Montpelier 13 m3/s); stage rise with
D4 is 3.5 vs 5.0 m (Montpelier) and 1.8 vs 3.2 m (Dog River). A fair test of the river-driven closures needs gauge-forced inflows or a
finer coarse run.

## Run it

Small case (any laptop or the GitHub workflow `.github/workflows/proto.yml`):
```
BOX=168000,908000,188000,928000 RES=20 STORM=sep2023 HOURS=48 LF_LOSS=cn LF_CN_SCALE=0.91 LF_INFIL_MMH=2 LF_QOUT=1 LF_NO_UPLOAD=1 LF_WORK=$PWD/lf python sim/colab/w9_lisflood.py
python proto/prototype.py --run-dir lf/run_sep2023_*/out --out results/leominster
python proto/prototype.py --selftest        # offline check of step 2-5
```

On WPI Turing (GPU): `bash proto/turing/setup_lisflood.sh` once, then `sbatch proto/turing/run_storm.slurm`.

## Why it needs the cluster

See `proto/turing/COMPUTE.md`.
