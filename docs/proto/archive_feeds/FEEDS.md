# Forward-only feed archives (started 29 Oct 2026)

Three sources that no one archives for District 3, and that cannot be recovered later, are copied to the Hugging Face dataset
`mohabeldokla/mass-flood-watch-tiles` from GitHub Actions. Nothing is committed to this repository per run: the dataset is both the archive
and the record of what has already been archived. Code: `proto/archive_feeds.py`. Each run echoes what it did as `::notice` annotations
(`gh api repos/Horus331/mass-flood-watch/check-runs/<job id>/annotations`). Why these three (data research note of 29 Oct, items 1 and
5): REFS goes operational on 3 Nov 2026 and nothing before that day is archived anywhere for District 3; SPoRT-LIS keeps an unknown
amount of history; the stormwater service sits on a staging server.

| feed | workflow | schedule | HF path | contents |
|---|---|---|---|---|
| **NOAA REFS flash-flood probabilities** (`refs.tCCz.ffri.fFF.conus.grib2`: flash-flood and recurrence-interval exceedance probabilities) | `archive_feeds.yml`, job `refs` | every 6 h, `10 4,10,16,22 * * *` UTC (forecast.yml runs at :40 of 02/08/14/20) | `refs/ffri/YYYYMMDD/tCCz/ffri_d3.npz`, `meta.json` | every message of every forecast hour, clipped to District 3 + 15 km |
| **NOAA REFS precipitation** (APCP of the `pmmn`, else `lpmm` / `mean` / `avrg` product) | same job | same | `refs/qpf/YYYYMMDD/tCCz/qpf_d3.npz`, `meta.json` | APCP messages only (byte ranges through the `.idx`), same clip |
| **NASA SPoRT-LIS soil moisture** (`lis_rsm_2m`, `lis_vsm_percentile_40cm` / `_100cm` / `_200cm`, 3 km, 6-hourly) | `archive_feeds.yml`, job `sportlis` | same | `sportlis/YYYYMMDD_HH/<layer>.tif`, `meta_<layer>.json` | `exportImage` over District 3 + 15 km at the service's native grid (nearest neighbour, float32 GeoTIFF), one per time step |
| **MassDOT Stormwater Asset Database** (public FeatureServer on `gisstg`, staging) | `stormwater_snapshot.yml` (manual, one-off) | 29 Oct 2026 | `massdot_stormwater/2026-10-29/` | every layer and table statewide: `NN_<name>.geojson.gz`, `.csv.gz`, `.layer.json`, `summary.json`; summary in `docs/proto/stormwater/SNAPSHOT.md` |

## How each archive works

**REFS.** Each run lists NOMADS `com/refs/prod/` and `com/refs/para/` (HTML directory listings, the last 3 UTC days, crawling below
`refs.YYYYMMDD/`), and the AWS RRFS buckets (`noaa-rrfs-ops`, `noaa-rrfs-pds`) only if NOMADS shows no `ffri` file. A cycle comes wholly
from `prod` when `prod` has it, else from `para`, so the 3 Nov switch needs no change. A cycle is archived once it is at least 6 h old (so
it has finished posting) and only if HF does not already hold it with as many files; at most 4 cycles per run, oldest first. Missing
cycles and missing hours are skipped and listed in `meta.json` (`errors`). The clip window is the bounding index box of the grid cells
whose centres fall in District 3's lon/lat envelope plus 15 km (`D3_BOX` of `proto/forecast.py`, EPSG:26986).

**SPoRT-LIS.** Each run reads each ImageServer's time steps (raster catalogue date field, else the time extent's end) and exports every
step not yet on HF (up to 60 per layer per run), so whatever history the service still offers is caught on the first run. If a service
is not time-enabled, the current image is stored under the 6-hourly slot it was fetched in.

**Stormwater.** Pages every layer and table by object id (≤ 1,000 per request), all fields, geometry in EPSG:4326, statewide (so it covers
Districts 3–6 and has the `District` and `Town` fields).

## Reading back

```python
from huggingface_hub import hf_hub_download, HfApi
import numpy as np, json
R = 'mohabeldokla/mass-flood-watch-tiles'
HfApi().list_repo_tree(R, path_in_repo='refs/ffri/20261029', repo_type='dataset')          # cycles of a day
z = np.load(hf_hub_download(R, 'refs/ffri/20261029/t00z/ffri_d3.npz', repo_type='dataset'))  # lat, lon + one 2-D array per message
m = json.load(open(hf_hub_download(R, 'refs/ffri/20261029/t00z/meta.json', repo_type='dataset')))
# m['messages']: key (f<hour>_m<n>), forecast hour, GRIB fields (parameter, probability type, limits, step range) and the pygrib summary
```

SPoRT-LIS GeoTIFFs open with `rasterio`; their `meta_<layer>.json` holds the time, request and value statistics. The stormwater files open
with `geopandas.read_file` / `pandas.read_csv`.

## First runs (verification, 29 Oct 2026)

- **REFS: working.** Run 40966178033, job `refs`: NOMADS `para` listed `refs.20261028/` and `refs.20261029/`, and `prod` does not
  exist yet (expected before 3 Nov). The four 29 Oct cycles were archived: `refs/ffri/20261029/t00z`, `t06z`, `t12z`, `t18z`. Each has 60
  hourly `ffri` files (f001–f060), 323 GRIB messages and a 49 × 45 subgrid of the 3 km Lambert grid, plus 80 `pmmn` APCP messages.
  Per cycle: 18 MB downloaded, about 135 kB `ffri_d3.npz`, 32 kB `qpf_d3.npz`. The first message reads "Probability of precipitation
  exceeding flash flood guidance values, % (accum), fcst 0–1 h, (> 1.0)", so the product is the expected one. The 28 Oct cycle folders
  had no `ffri` listing left on NOMADS, so the archive starts at **2026-10-29 00z**. NOMADS keeps only about a day of `para`, which is why
  the job runs every 6 h. The first scheduled run is at 04:10 UTC.
- **MassDOT stormwater: done.** Run 40966180828: 31 files in `massdot_stormwater/2026-10-29/`. The service has 6 layers and 6 tables (ids
  0–11, more than the 0–9 the research note listed). Statewide: inlets 134,871 (28,936 in District 3), manholes 142,452 (20,331),
  stormwater control measures 1,546 (490), discharge points 19,390, conveyance 6,940, miscellaneous structures 96, and 678
  inspection forms. Every layer's copyright text says the data is public domain. Summary: `docs/proto/stormwater/SNAPSHOT.md`.
- **SPoRT-LIS: first run failed.** All four services answered `f=json` with a body that was not JSON, so nothing was archived. The
  workspace cannot read Actions logs, so the reply itself is unknown. The next commit adds service discovery and diagnostics: it tries
  the documented `ags03` path, then sibling hosts, then a search of the `NRT` folder for the layer name, and it reports the HTTP status,
  content type and first bytes of every failed reply in the `sportlis <layer>` annotation. Check the next run's annotations. If the
  service is only reachable from a browser session, this feed needs another source, such as NASA SPoRT's own file server. No access
  control will be worked around.
