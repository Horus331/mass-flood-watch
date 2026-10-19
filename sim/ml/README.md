# sim/ml — surrogate training data and baseline

Code for the ML side of the Oct 18 plan (`docs/reviews/2026-10-18_ml_cascade_review.md` items 1–3, 6; decisions C and F): turn finished
engine runs into a per-cell training table and score a gradient-boosting baseline with the pre-registered splits in `docs/validation/protocol.md`.
Everything here is CPU-only and reads the same Hugging Face layout the engine writes (`runs/<name>/hmax.npy, z.npy, t_first.npy, dur.npy, vmax.npy, meta.json`).

| file | what |
|---|---|
| `dataset.py` | runs + static grids → Parquet/NPZ shards (`part-*.parquet`, `manifest.json`): statics (z, slope, TPI, HAND to the drained-to channel, Euclidean HAND, distances, D8 upstream area, receiving-channel area/width/depth, pit flag, impervious fraction, SSURGO group / aws / water table / bedrock / storage cap, channel flag), storm features (max 1/3/6/24 h rain and total, antecedent store mm and fraction of capacity, FC_SCALE, run length), targets (`hmax` m, `t_first_h`, `dur_h`, `wet`, `vmax`), split keys (`storm`, `huc10`, `fold`, `split`), `weight`. All wet cells kept, dry cells stratified by HAND with inverse-probability weights, tile by tile. |
| `baseline.py` | LightGBM (if installed) or sklearn HistGradientBoosting: P(wet), depth on wet cells (log1p), arrival time, duration. Leave-one-storm-out and HUC10 block CV; hit / precision / F1 / CSI at P≥0.5, CSI/F1 at 10/30/50 cm, PR-AUC, Brier + Brier skill, depth MAE and within-50 cm, t_first/dur MAE; weighted and unweighted; reliability-diagram CSV per split (bins with < 50 positives flagged); feature importance. |

## Run it

```bash
python sim/ml/dataset.py --selftest          # synthetic state + 6 fake runs -> shards -> consistency checks (1 s)
python sim/ml/baseline.py --selftest         # builds the synthetic dataset, trains, checks the report (~40 s on CPU, sklearn backend)

# real data, on a machine with the HF token (Colab / Kaggle / laptop); inputs are downloaded on demand with --hf
HF_TOKEN=... python sim/ml/dataset.py --hf --runs runs/dec2023_v3_30m runs/sep2023_v3_30m runs/jul2023_v3_30m runs/jan2018_v3_30m \
    --soils data/soils30/soils30.npz --channels data/channels30/channels30.npz --nlcd10 data/nlcd10 \
    --huc10 data/huc10_30/huc10_30.npz --out /content/ds_v3 --upload ml/datasets/v3_30m
python sim/ml/baseline.py --dataset /content/ds_v3 --out /content/ds_v3/baseline --upload ml/datasets/v3_30m/baseline
```

Options worth knowing: `--dry-ratio 2` (dry rows per wet row, per tile), `--tile 1024`, `--rows-per-shard 2000000`, `--folds 5`, `--storm test_leominster=sep2023`
(force a run onto a storm id; by default the storm is the run name up to the first `_`, so `jul2023_southriver_v3` and `jul2023_v3` are held out together),
`--keep-water` (river/lake/sea cells are dropped by default), `--format npz` (no pyarrow), `baseline.py --drop rain_total_mm ...` for ablations, `--max-rows` for a quick look.
Static layers are computed once per (box, resolution) and cached, so a parameter ensemble on one box costs one routing pass. Memory is set by the static arrays
of one grid: a district box (≈4 M cells) needs well under 1 GB, statewide 30 m (44 M cells) several GB (≈ 5 GB peak during D8 routing) → use a High-RAM runtime for statewide.

## Inputs the engine does not write yet (asks for the w4 owner)

`dataset.py` degrades gracefully, but the storm features need two small additions to `w4_flood_gpu.py` (decision C, "outputs the ML needs"):

1. **`rain_hourly.npz`** — the MRMS hours on a coarse grid: `np.savez_compressed(f'{OUT}/rain_hourly.npz', mm=np.stack([RAIN[ts][::10, ::10] for ts in hours]).astype(np.float16), box=np.array(BOX), res_m=RES * 10, hours=np.array([ts.strftime('%Y-%m-%dT%H:%MZ') for ts in hours]))`
   (≈ 5 MB statewide). Without it every cell gets the storm's mean total from `meta.json` and `rain_grid` = 0, which makes the rain features useless for spatial learning.
2. **`imp.npy`** — the paved fraction already in memory: `np.save(f'{OUT}/imp.npy', IMP.astype(np.float16))`. Without it `dataset.py` re-assembles the NLCD 10 m tiles itself (`--nlcd10 data/nlcd10`, slower, same numbers).

Also useful later: per-cell antecedent store (`Finf0`) as `ante.npy`; today the dataset uses the run-mean `physics.antecedent_mm` capped by the cell's storage capacity.

## HUC10 raster

The protocol's spatial split is by HUC10 watershed. There is no HUC10 grid on Hugging Face yet. Expected: `data/huc10_30/huc10_30.npz` (field `huc10`, int64, 0 = outside)
+ `huc10_30_meta.json` with `box`, `res_m`, `shape` on the whole-state 30 m grid (same convention as `soils30` / `channels30`), rasterised from the USGS WBD HU10
polygons (free; a `sim/huc10_grid.py` GitHub-Actions job like `channels_grid.py` would do it). Until it exists `dataset.py` falls back to 20 km grid blocks and
writes `block_src: grid20km` into the manifest; `baseline.py` copies that into the report so a result on the fallback cannot be mistaken for the pre-registered split.

## Queue job (template — not added to `docs/queue/jobs.json`; the worker needs the STEP mapping below first)

```json
{
 "id": "ml_dataset_v3_30m",
 "kind": "ml",
 "env": {
  "ML_RUNS": "runs/dec2023_v3_30m,runs/sep2023_v3_30m,runs/jul2023_v3_30m,runs/jan2018_v3_30m",
  "ML_OUT": "ml/datasets/v3_30m",
  "HUC10": "data/huc10_30/huc10_30.npz",
  "NLCD10": "data/nlcd10",
  "DRY_RATIO": "2",
  "FOLDS": "5"
 },
 "steps": ["dataset", "baseline"],
 "gpu_gb": 0,
 "priority": 4,
 "after": ["dec2023_v3_30m", "sep2023_v3_30m", "jul2023_v3_30m", "jan2018_v3_30m"],
 "note": "per-cell surrogate table from the four v3 storms + GBM baseline with LOSO and HUC10 splits; CPU only, High-RAM for statewide boxes"
}
```

`dataset.py` and `baseline.py` read their settings from the job env when run without arguments (`ML_RUNS`, `ML_OUT`, `HUC10`, `NLCD10`, `SOILS_GRID`, `CHANNELS_GRID`,
`DRY_RATIO`, `FOLDS`, `STORM_OF=run=storm,...`; `ML_DATASET` for the baseline step, which defaults to `ML_OUT` of the same job when the worker passes the job env).
`gpu_gb: 0` lets a CPU-only worker take it.

### Suggested `worker.py` change (owner: queue teammate — not edited here)

```python
# fetch_scripts(): add the two ML scripts to the tuple
for f in ('sim/colab/w4_flood_gpu.py', 'sim/colab/w5_tiles.py', 'sim/colab/w6_validate.py', 'sim/colab/w8_coast_gpu.py', 'sim/solver.py',
          'sim/ml/dataset.py', 'sim/ml/baseline.py'):
# STEP: two new steps
STEP = {'w4': 'w4_flood_gpu.py', 'w5': 'w5_tiles.py', 'w6': 'w6_validate.py', 'w8': 'w8_coast_gpu.py', 'dataset': 'dataset.py', 'baseline': 'baseline.py'}
```

`baseline.py` imports `dataset` from its own directory, so both files must land in `WORK` together (they do with the tuple above). Kind `"ml"` is informational
(the worker dispatches on `steps`); `pick()` needs no change because `gpu_gb: 0` fits every worker.

## Open questions

- Dry-cell sampling: `--dry-ratio 2` per tile with 5 HAND strata is a first guess; the right ratio depends on how the surrogate is used (ranker feature vs map). Weights make the choice recoverable.
- `t_first_h` for dry cells is NaN (never wet) — the baseline regresses arrival time on wet cells only; a hazard-style "time to wet" model would need a censoring treatment.
- Channel cells start a third full in v2 physics, so `wet` on `chan` cells is partly baseflow; they are kept with `chan` as a feature. Drop them with `df[df.chan == 0]` if the target should be overbank water only.
- HAND is computed on the run DEM (`z.npy`, channels already burnt), routed by D8 with pits spilling to their nearest channel cell instead of a priority-flood fill; upstream area therefore stays local to a pit. Good enough for a GBM feature, not a hydrologic product.
