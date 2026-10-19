# Mass Flood Watch

Road flood risk map for Massachusetts (MassDOT Districts 3–6), built for Mo Eldokla's PhD research at WPI.

**Open the map:** https://horus331.github.io/mass-flood-watch/ (add `#graph` to open straight on the District 3 segment graph).

- `docs/` is the web page and its data (served by GitHub Pages). `docs/v2/` is the new MapLibre map that plays the statewide GPU runs; `docs/methods.html` explains the model.
- `sim/` is the flood engine: `solver.py` (2-D local-inertial, numpy/CuPy), `colab/` jobs for Google Colab (see its README), data jobs for GitHub Actions (`soils_sda.py`, `gauges_fetch.py`, `drainage.py`), `validate.py` scoring.
- Large data (10 m elevation, drainage, soils, gauge records, run outputs and map tiles) lives on Hugging Face: https://huggingface.co/datasets/mohabeldokla/mass-flood-watch-tiles
- `refresh/live_refresh.py` pulls NOAA tide gauges, the NOAA STOFS surge forecast, NWS rain forecasts, NDBC buoys and NWS alerts, and writes `docs/live.json`.
- `.github/workflows/refresh.yml` runs it every 6 hours. Run it by hand from the **Actions** tab → *Refresh live data* → **Run workflow**.

## Running jobs on more machines

Flood runs are a shared queue: jobs are listed in `docs/queue/jobs.json` (edit with git), and `sim/colab/worker.py` on any GPU machine
(Colab, Kaggle, a cluster node) pulls the next runnable job, claims it with a Hugging Face commit so no two workers take the same one,
runs the steps (engine → tiles → score) and uploads the log to `queue/logs/` on Hugging Face. To add a machine, start a worker there
with an `HF_TOKEN` secret; see `sim/colab/README.md` for the Colab and Kaggle launcher cells.

All data sources are free public NOAA / NWS / USGS / MassGIS services. Model results are research prototypes, not official warnings.
