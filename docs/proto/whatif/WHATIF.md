# What-if storm explorer (`viewer.html?run=whatif`)

**What it is.** One real storm, the Leominster / Fitchburg flash flood of 11 Sept 2023 on the live replay's box
(`168000,908000,188000,928000`, 20 m, 48 h), rerun by LISFLOOD-FP with one or more inputs changed. Every slider position is a full
physics run on WPI's Turing GPUs; nothing is interpolated or extrapolated. Not a forecast, not a validation: a sensitivity explorer for
showing how rain, antecedent ground and culvert condition shape the flood and the road closures. Nothing here changes the deployed
model, the live replays or the forecast.

## Scenario matrix (32 runs, `proto/whatif.py list`)

| axis | positions | setting |
|---|---|---|
| rain | ×0.5, ×0.75, **×1 (as measured)**, ×1.25 | `LF_RAIN_SCALE`: every hour of the MRMS Pass2 radar rain multiplied; same timing and place (the ensemble hook of `w9_lisflood.py`) |
| ground | dry, **normal**, soaked, frozen | dry `LF_CN_AMC=I`, normal AMC II (baseline), soaked `LF_CN_AMC=III` (Chow et al. 1988 conversions); frozen `LF_CN_FROZEN=1` + `LF_INFIL_MMH=0` |
| culverts | **clear**, blocked | clear = the baseline (a notch to the lowest ground within 40 m at every mapped crossing, plus depression breaching); blocked `LF_XINGS_BLOCKED=1` |

Everything else is the deployed baseline (`parity/BASELINE.md`): `LF_PARITY=1`, `LF_LOSS=cn`, `LF_CN_SCALE=0.88`, `LF_INFIL_MMH=2`,
`LF_QOUT=1`, `LF_VOUT=1`, plus `LF_SAVEINT=900` (15-minute frames, so a scenario pack is ~1.5 MB instead of the live replay's ~5 MB).

**Engine changes (opt-in, default off; the selftest covers them):**
- `LF_CN_AMC=I` is now honoured when set explicitly (before, the AMC I conversion only ran through `LF_CN_AMC=auto`).
- `LF_CN_FROZEN=1`: every land cell gets the paved curve number 98 before the calibration scale (so frozen ground behaves like the
  model's pavement), and the scenario sets `LF_INFIL_MMH=0` (no steady soak-in). This is an upper bound for concrete frost: real frozen
  soil varies with snow cover and frost depth. Labelled as such in the viewer.
- `LF_XINGS_BLOCKED=1`: culverts and small crossings pass no water. At each mapped crossing that is not a bridge (`is_bridge`: in the NBI,
  a MassDOT bridge, NAACC shape "bridge", a non-culvert structure type, or span ≥ 6 m) the 3 × 3 cells are raised to their highest cell
  (solid road fill, no notch) and a 5 × 5 block (`LF_XING_BLOCK_M=40`) is protected from depression breaching, so no carved path stands
  in for the pipe. Water behind the road leaves only over the road. 542 of the 713 mapped crossings in the box are blocked; the 171 bridges stay open.

**What "draining" means in the viewer.** With `LF_PARITY=1` the soil's share is taken out of the rain as it falls (CN excess minus
2 mm/h). Once water is on the ground it leaves by flowing downhill and downstream; the model has no soak-in of standing water. The
viewer therefore calls the last phase "Draining", not "absorbed".

## Turing jobs

- `proto/turing/whatif_runs.slurm`: GPU array, one scenario per task (`--array=0-31%8`), model + `prototype.py` + `cascade.py`, no push.
- `proto/turing/whatif_pack.slurm`: `proto/whatif.py pack` into `docs/site/data/whatif/` and **one** push via `publish.sh`
  (`PUBLISH_EXTRA=docs/site/data/whatif`), plus `docs/proto/turing/whatif_site/RESULTS.md` with the numbers of every scenario.
- `proto/turing/whatif_pipeline.slurm`: queue kind `whatif_pipeline`; submits the array, then the pack with `afterany` (a failed scenario
  does not block the others; the viewer marks missing ones as queued).
- Estimate: ~2.5–5 GPU-min of solver per run plus inputs, prototype and cascade (~8 min per task): ~4 GPU-hours allocated in all, ~40 min
  wall on 8 GPUs, then ~30–40 min of CPU packing.

## Pack (`docs/site/data/whatif/`)

`index.json` (axes, numbers per scenario, status), `roads.json` (every segment with water in any scenario), `terrain.png` (R hillshade
of the lidar DEM, G mapped water / channel cells, B elevation), `culverts.json`, and per scenario `<id>/d.json` (depth on each road per
frame, closures, culverts overtopped with the frame, people cut off), `<id>/depth_NN.png` (9 frames per image, base-5 classes 5 / 15 / 30 /
100 cm; on mapped water and channel cells the class is the **rise** above the level at the start, so streams light up as they swell) and
`<id>/flow.png` (30-min velocity). People cut off = residents with no route to any open hospital, fire or police station at the worst
moment (`proto/cascade.py`, 2020 Census blocks).
