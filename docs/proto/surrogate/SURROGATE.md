# A fast surrogate of the flood model: pre-registration (29 Oct 2026)

This file was written and committed **before any surrogate was trained or scored**. No training run exists yet. If anything below changes,
it gets a new dated section, and the change applies only to evaluations made after that date.

Code: `proto/surrogate/` (`scenarios.py`, `dataset.py`, `train.py`, `evaluate.py`). Turing jobs: `proto/turing/surrogate_gen.slurm`,
`surrogate_inputs.slurm`, `surrogate_train.slurm`. Results will go to `RESULTS.md` and `results.json` in this folder.

## 1. Why

- The deployed model is pure physics: LISFLOOD-FP 8.2 at 20 m (`parity/BASELINE.md`) plus the depth rule P = Φ((d − 0.30 m) / 0.10 m).
- Direct machine learning on flood reports lost to the physics. There are too few labels (98 held-out sites).
- A surrogate learns from the physics itself. Every training example is a LISFLOOD-FP run, so labels are not the limit.
- The concrete need is the District 3 map. `forecast/DISTRICT.md` showed that one HRRR run over-forecasts the district about 3 times.
  The fix it names is the 2-of-8 ensemble district-wide. That costs 8 × ~17 GPU-minutes per cycle on Turing (about 50 minutes of node time
  each, with inputs), and Turing is not on a 6-hourly schedule.
- A surrogate that turns static terrain plus a rain field into peak depth in seconds on a CPU would let GitHub Actions run 8 or more
  members over the whole district every 6 hours. It would also allow larger ensembles and probabilistic maps.

**Scope.** If adopted, the surrogate is used **only** as the district-wide / ensemble layer. It never replaces the physics in the box
forecast runs, the storm archive, the forward test (`prospective/PROSPECTIVE.md`) or any baseline. Showing a District 3 warning map built
from it still needs its own pre-registered test (`forecast/DISTRICT.md`, options a–c).

## 2. What is predicted

- **Target.** Peak depth `hmax` (m) in every 20 m cell, exactly as LISFLOOD-FP writes it (`hmax.npy`). A second head predicts
  P(hmax ≥ 0.30 m). It is reported, but the decision uses the depth.
- **Physics it imitates.** The frozen baseline: `LF_PARITY=1`, `LF_LOSS=cn`, AMC II, `LF_CN_SCALE=0.88`, `LF_INFIL_MMH=2`, 20 m, free
  boundaries, no dams, no drains (`parity/BASELINE.md`; the same settings as `proto/storm_archive.py` `BASELINE_ENV`).
- **Inputs** (`dataset.py`, 24 channels at 20 m):
  - Static (13): terrain relative to its 1 km and 200 m means; slope; log D8 upstream area; HAND; impervious share; curve number; water,
    channel, breached-depression and no-data masks; road-crest relief (highest 10 m cell minus the lidar cell); hydraulic edits (model
    DEM minus lidar: channel burn, culvert notches, breaching). All come from the model's own inputs (`w9_lisflood.py`, `LF_SURR_SAVE=1`).
  - Rain (11): storm total; maximum 1, 3 and 6 h; the effective excess after the model's own losses (cumulative SCS-CN, then 2 mm/h out of
    each hour, exactly as `w9`); its peak hour; the D8-accumulated excess volume and peak-hour volume from upstream; share of wet hours;
    hours left after the excess centroid; window length.
- **Model** (`train.py`). A plain U-Net, 4 levels, 24 base channels, GroupNorm, 4.4 M parameters. Loss: Huber on log1p(h / 0.1 m) plus
  0.5 × the wet-head cross-entropy. Weights: land 1, water and channel 0.3, no-data 0, land cells at 0.15–0.60 m × 2. Patches 256 × 256,
  half centred on a cell ≥ 0.30 m, random flips and 90° turns. AdamW, one-cycle learning rate 1e-3, batch 12, 20 000 steps. These
  settings are fixed now (`train.py` `CFG`). They may only change by looking at the **val** rain days, before any evaluation below is run.

## 3. Training data

**Generator** (`scenarios.py`, `surrogate_gen.slurm`): LISFLOOD-FP runs at the frozen baseline on 20 × 20 km boxes covering District 3.

- **Boxes.** A 10 km grid of 20 km boxes inside the District 3 box (`D3_BOX`, EPSG:26986): 56 boxes. Two boxes are held out for
  terrain: `hb_west` 136000,876000,156000,896000 (Brookfields, Spencer, Warren) and `hb_north` 186000,916000,206000,936000 (Groton,
  Westford, Littleton). No training box touches them, which leaves 38 training boxes.
- **Rain days.** The 24 h ending 12 UTC, from the MRMS `MultiSensor_QPE_24H_Pass2` scan (Oct 2020 – 27 Oct 2026, central and eastern
  Massachusetts and the edges of the neighbouring states). Days with a maximum ≥ 40 mm are taken wettest first. The model window is 36 h:
  6 h before, the 24 h, and 6 h of drain-down.
- **Protected rain (never used).** Every storm in `obs/catalog.json` (the 2 dev storms, the held-out 23, the 5 locked storms and sep2014),
  every storm in `obs/catalog_d456.json` (the District 4–6 transfer test), and the Vermont July 2023 storm. Each is protected from 24 h
  before its window to 24 h after it. No rain after 27 Oct 2026 is used (the forward test starts 3 Nov 2026). Their rain is **not**
  transplanted either, because a transplanted storm still carries its own intensity and timing. `check_plan` refuses any plan that breaks
  these rules.
- **Dev storms are excluded too.** sep2023 and aug2021 may be used for tuning under PROTOCOL v2, but here they are kept out. This makes
  the District 3 Sept 2023 run an independent district-scale check.
- **Placements per rain day** (1 MRMS run in place, 2 moved, 1 HRRR):
  - Train and val days: the observed storm on the training box nearest its core (moved into the box centre if needed); twice moved
    (`LF_RAIN_SHIFT_M`) onto a random training box and scaled (`LF_RAIN_SCALE` 0.5, 1, 1, 1.5 or 2); and the HRRR forecast from the 06 UTC
    cycle at the start of the window (24 forecast hours) on the nearest training box. Two thirds of the HRRR runs use the live 20 km / 90th-percentile
    neighbourhood, one third the raw field.
  - Test days: moved onto each held-out box (scale 1 on `hb_west`, random on `hb_north`), once onto a training box, and the HRRR forecast
    on a held-out box.
- **Day split.** A hash of the date: about 70 % train, 15 % val, 15 % test. A day keeps its split in every batch.

| | rain days | box runs | district runs | GPU-node-hours (estimate) |
|---|---|---|---|---|
| Batch 1 | 48 | 192 (4 per day; the split follows the day hash, about 70 / 15 / 15) | 0 | ~16 (4 GPUs at once: ~4 h, one night) |
| Batch 2 | next 144 | 576 | 16 (8 lagged HRRR members on the 2 wettest train days, whole District 3) | ~63 |

Estimate per box run: ~5 minutes of a GPU node. The parity GPU box runs took 2.5–5 minutes in all, of which the solver took 20–150 s
(`docs/proto/turing/*/flood_meta.json`). A District 3 run takes ~50 minutes (`d3_sep2023_p`: 52 min, `hindcast_d3_sep2023_18z`: 46 min).

**Existing runs.** The parity catalogue (`parity/catalog/`) and the District 3 runs (`turing/d3_sep2023_p`, `hindcast_d3_sep2023_18z`)
are catalogue storms, so they are used **only for evaluation**. The ensemble and hindcast box runs (`forecast/ensemble`, `forecast/district`)
used CN × 0.91 at the default step, not the baseline physics, so they are not used for training. The old HF runs (`runs/<name>`) came from
earlier engines and are not used.

**Training sets.** Model A trains on the train split and keeps the step with the lowest val loss. Model B uses the same recipe on every
generated run (train + val + test_rain + test_box) for exactly A's step count. Model B is the candidate. No catalogue or District 3 input
is ever read during training.

## 4. Metrics

All are computed by `evaluate.py eval`. "Flagged" means p_close ≥ 0.5 from `proto/prototype.py` at its defaults, run on the surrogate's
depth exactly as on LISFLOOD-FP's.

**Against LISFLOOD-FP** (model B; catalogue storms on their catalogue boxes and windows; the reference is the published parity run):

1. **Segment CSI**: |F ∩ R| / |F ∪ R|, pooled as sums over the held-out 23 storms. F is the surrogate's flagged set, R is LISFLOOD-FP's.
2. **Count ratio**: Σ|F| / Σ|R| over the held-out 23 storms.
3. **Cell CSI** at 0.30 m (and at 0.10 m) on land cells (not water, channel, breached or no data), pooled.
4. **Depth MAE and bias** on wet land cells (either model ≥ 0.10 m).

The dev storms (sep2023, aug2021) are reported separately.

**Against the labels** (model B; `score_v2.py` machinery, PROTOCOL §1 matching, the published `matches_<storm>.json`): site recall at the
rule and at 3 % flagged on the held-out 23 storms (98 sites after label round 2). Each is compared with the LISFLOOD-FP radar-driven parity
catalogue, scored by the same run with the same label files. The difference (surrogate minus physics) comes with a paired two-stage
bootstrap (storms, then sites; 2000 replicates; the same draws for both).

**District 3** (model B): the segment CSI and count ratio against `turing/d3_sep2023_p` (the Sept 2023 radar run, 276 flagged). The
HRRR 18z hindcast count is set against its 888 flagged and reported only.

**Speed**: wall time from `surr_inputs.npz` to peak depth for the District 3 inputs (features plus network) on 4 CPU threads.

**Plausibility** (after the mass-error check of Bentivoglio et al. 2026, `../research/sota_2026-10-19.md` (b)): the peak-depth volume on land
divided by the effective-excess volume of the box. A prediction is flagged when this ratio is above the 99th percentile of the LISFLOOD-FP
training runs. This is reported, not a gate. Peaks are not simultaneous, so this is not a mass balance.

**Generalisation** (model A, reported only): cell and segment metrics on the val days, on test days over training boxes (`test_rain`), and
on test days over the held-out boxes (`test_box`: new terrain and new rain).

## 5. Adoption rule

The surrogate is adopted **as the district-wide / ensemble layer only** if all five conditions hold for model B:

| | condition | threshold | why this number |
|---|---|---|---|
| C1 | segment CSI vs LISFLOOD-FP, held-out 23 pooled | **≥ 0.70** | The surrogate's error must be smaller than the spread it is meant to sample. Across the 13 lagged HRRR runs of each of the 9 ensemble storms (`forecast/ensemble/*_m*_nb/seg.json`, flags only, no labels), the pairwise CSI of the flagged sets has median 0.50 and upper quartile 0.71 (702 pairs). 0.70 means the surrogate agrees with the physics about as well as the closest quarter of member pairs agree with each other. Published CNN / GNN surrogates report 0.71–0.80 CSI at 30 cm (Asif et al. 2026; Bentivoglio et al. 2026). |
| C2 | count ratio, held-out 23 | **0.80–1.25** | No systematic over- or under-flagging (±22 %, symmetric in log). This is tighter than DISTRICT.md's ±30 % gate, because it pools 23 storms. |
| C3 | site recall vs physics, held-out 23, at the rule **and** at 3 % | difference **≥ −0.02** and one-sided 95 % lower bound **≥ −0.04** | −0.04 is PROTOCOL v2's smallest meaningful change (+0.04 to adopt a gain). The surrogate must not be shown to lose that much. −0.02 is about 2 of 98 sites. |
| C4 | District 3 Sept 2023 (radar) | segment CSI **≥ 0.60** and count ratio **0.7–1.3** | This is the use case and it lies outside the box training domain. It is one storm, so the bar is lower than C1. The ratio band is DISTRICT.md's gate. |
| C5 | speed, District 3, 4 CPU threads | **≤ 300 s** per member | 8 members fit in about 40 minutes of one GitHub Actions job. |

- **One candidate.** This pre-registration scores exactly one model (B, the settings of section 2) on the held-out 23, so k = 1 and
  α = 0.05 in C3.
- **One more chance.** If batch 1 fails, one more evaluation is allowed after batch 2, with the same recipe and only more data (k = 2,
  α = 0.025 in C3, `K=2`). Both results are reported. There is no third try under this file.
- **Locked storms** are never run, read or scored (`scenarios.py inputs` refuses them). District 4–6 storms are never used.
- **If adopted**, nothing live changes in this step. The next step is a new pre-registration that tests the District 3 forecast map
  (2-of-8 from surrogate members) against the labels.

## 6. Commands (Turing, owner)

```
cd ~/mass-flood-watch && git pull
conda activate ~/envs/roadflood && pip install torch --index-url https://download.pytorch.org/whl/cu126     # once
python proto/surrogate/scenarios.py scan --out ~/scratch/surrogate/scan.json                                # login node, ~1 h
python proto/surrogate/scenarios.py plan --scan ~/scratch/surrogate/scan.json --batch 1 --out ~/scratch/surrogate/plan_b1.json
sbatch --array=0-23%4 --export=ALL,PLAN=$HOME/scratch/surrogate/plan_b1.json,PER_TASK=8 proto/turing/surrogate_gen.slurm   # ~16 GPU-h
sbatch proto/turing/surrogate_inputs.slurm                                                                   # CPU, ~2-3 h
# when both have finished:
sbatch --export=ALL,PLANS=$HOME/scratch/surrogate/plan_b1.json proto/turing/surrogate_train.slurm           # ~3 GPU-h; one push
bash proto/turing/backup_hf.sh --runs-root ~/scratch/surrogate --results-root /nonexistent --prefix runs/surrogate
```

- The plan step prints the exact `--array` range.
- Only `surrogate_train.slurm` pushes to GitHub, once: `docs/proto/turing/surrogate_eval/` (results, scores, plans, dataset index, models)
  and this folder's `RESULTS.md` / `results.json`, through `publish.sh`.
- The runs stay in `~/scratch/surrogate/run_<id>/out/`. `backup_hf.sh` copies them to `runs/surrogate/` on the Hugging Face dataset.

## 7. Known limits (stated now)

- **Peak depth only.** The surrogate gives no timing, velocity or crossing flow. Prototype layers that need them (hours over 30 cm,
  arrival time, fast water, edge washout, culvert flow) are empty on surrogate runs. None of them is part of the deployed `p_close`.
- **Box training, district use.** Batch 1 has no District 3 runs. Rivers entering from beyond 20 km are deeper district-wide than in any
  training box. C4 tests exactly this. Batch 2 adds 16 District 3 runs.
- **Rain eras.** Training rain is AWS Pass2 (from Oct 2020). The 16 held-out storms before Oct 2020 used the IEM GaugeCorr product. Both
  are hourly gauge-corrected MRMS, so the shift should be small. It is reported per storm.
- **Static inputs are rebuilt.** The catalogue inputs come from an inputs-only `w9` run at today's commit. The watermask of each is
  compared with the published run's (`watermask_agreement` in the dataset index).
