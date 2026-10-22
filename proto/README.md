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

**Calibration and checks (Sept 2023):** rain losses use the standard NRCS curve number (TR-55, HSG + NLCD impervious, AMC II, no
adjustment factor). Modelled peak river flow matches both in-box USGS gauges: 41 vs 44 m³/s observed at 01094400 (North Nashua at
Fitchburg) and 167 vs 157 m³/s at 01094500 (North Nashua near Leominster); stage rise 1.29 vs 1.00 m and 3.26 vs 2.92 m. Peaks come
0.8 h and 4 h early. Absolute water levels sit 1.1–1.3 m below the gauge datum, because the lidar DEM holds the river surface at survey
time and the channel bed is burnt approximately, so rise and flow are the scored quantities. Every run is also scored against 13 NWS storm
reports, 11 NOAA Storm Events records and 93 documented road flood/closure/damage sites (`proto/data/`), next to random road points.

*Fixed 21 Oct 2026:* the rain NetCDF was written with y ascending, which LISFLOOD-FP's `DynamicRain` reads one row off, with the north
row reading past the buffer (spurious inflow of ~3×10⁹ m³). Runs before commit "Fix rain file row mapping" (including the earlier ×0.9
calibration) are superseded.

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
Peak speeds have numerical spikes (max 96 m/s in a few cells; p95 on wet land 3.2 m/s), so read single-cell speeds with care.

## Run it

Small case (any laptop or the GitHub workflow `.github/workflows/proto.yml`):
```
BOX=168000,908000,188000,928000 RES=20 STORM=sep2023 HOURS=48 LF_LOSS=cn LF_CN_SCALE=1.0 LF_INFIL_MMH=2 LF_QOUT=1 LF_NO_UPLOAD=1 LF_WORK=$PWD/lf python sim/colab/w9_lisflood.py
python proto/prototype.py --run-dir lf/run_sep2023_*/out --out results/leominster
python proto/prototype.py --selftest        # offline check of step 2-5
```

On WPI Turing (GPU): `bash proto/turing/setup_lisflood.sh` once, then `sbatch proto/turing/run_storm.slurm`.

## Why it needs the cluster

See `proto/turing/COMPUTE.md`.
