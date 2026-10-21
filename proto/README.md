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

**Calibration and checks (Sept 2023):** rain losses use the NRCS curve number (TR-55, HSG + NLCD impervious, AMC II, ×0.9), so 36% of
the rain runs off, matching the 30–43% storm runoff measured at the USGS North Nashua gauges. At USGS 01094400 (North Nashua at Fitchburg)
the modelled river rose 1.18 m against 1.00 m observed and peaked within 0.2 h of the observed peak. Every run is also scored against 13
NWS storm reports, 11 NOAA Storm Events records and 93 documented road flood/closure/damage sites (`proto/data/`), next to random road points.

Closure probability in this prototype is a physics prior, `P = Φ((peak depth − 0.30 m) / 0.10 m)`. In the dissertation it is replaced by a
model learned from observed closures (storm reports, MassDOT records, Vermont 2023).

## Run it

Small case (any laptop or the GitHub workflow `.github/workflows/proto.yml`):
```
BOX=168000,908000,188000,928000 RES=20 STORM=sep2023 HOURS=48 LF_LOSS=cn LF_CN_SCALE=0.9 LF_INFIL_MMH=2 LF_NO_UPLOAD=1 LF_WORK=$PWD/lf python sim/colab/w9_lisflood.py
python proto/prototype.py --run-dir lf/run_sep2023_*/out --out results/leominster
python proto/prototype.py --selftest        # offline check of step 2-5
```

On WPI Turing (GPU): `bash proto/turing/setup_lisflood.sh` once, then `sbatch proto/turing/run_storm.slurm`.

## Why it needs the cluster

See `proto/turing/COMPUTE.md`.
