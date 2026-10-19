# Colab jobs (GPU runtime: L4 + High-RAM)

All jobs read their inputs from Hugging Face (`mohabeldokla/mass-flood-watch-tiles`) and write results back there, so they
work on any runtime with no Drive mount.  The HF write token lives in the Colab secret `HF_TOKEN`; `userdata.get` only works
in the notebook kernel, so the launcher cell passes it to the background job through the environment.

Launcher cell (one job per cell; `RUN` and `RES` select the storm and the cell size):

```python
import os, subprocess, urllib.request, time
from google.colab import userdata
urllib.request.urlretrieve('https://raw.githubusercontent.com/Horus331/mass-flood-watch/main/sim/colab/w4_flood_gpu.py?x=' + str(int(time.time())), '/content/w4_flood_gpu.py')
env = dict(os.environ, HF_TOKEN=userdata.get('HF_TOKEN'), RUN='dec2023', RES='30', DEVICE='gpu')
subprocess.Popen(['bash', '-c', 'nohup python /content/w4_flood_gpu.py > /content/w4_flood_gpu_dec30.out 2>&1 &'], env=env)
```

Tail the log with `print(open('/content/w4_flood_gpu_dec30.out').read()[-1500:])`.

| job | what | inputs (HF) | outputs (HF) |
|---|---|---|---|
| `w4_flood_gpu.py` | 2-D flood run for a storm (`RUN`=dec2023, sep2023, jul2023, jan2018) | data/dem10, data/nlcd10, data/soils30, data/gauges, MRMS from NOAA | runs/<RUN>_<RES>m/ (frames, hmax.npy, roads_cm.npy, meta.json) |
| `w5_tiles.py` | map tiles (PMTiles per frame) for a run (`RUN_DIR`) | runs/<RUN>_<RES>m/ | runs/<RUN>_<RES>m/tiles/ |
| `w1_data.py`, `w2_drain10.py`, `w2b_upload.py` | one-off data foundation (10 m DEM, 10 m drainage, flowlines) | USGS | data/dem10, data/drain10, data/nhdplushr_flowlines.geojson |
| `w3_gpu_check.py` | CPU vs GPU solver check and speed | – | – |
| `w6_validate.py` | score a published run against surveyed high-water marks and road flood reports (`RUN_DIR`) | runs/<RUN_DIR>/ (meta.json, hmax.npy, z.npy), validation data from the site repo | runs/<RUN_DIR>/validation.json |
| `w8_coast_gpu.py` | coastal flood run at 10 m: the sea held at the tide-gauge level flows over the land (`TILE`, `STORM`, `RES`, `SEA_RISE`) | data/dem10, NOAA CO-OPS water levels | runs/coast_<TILE>_<STORM>[_slr<cm>]_<RES>m/ |
| `worker.py` | shared job-queue worker: claims the next runnable job from `docs/queue/jobs.json` and runs its steps (`WORKER`, `GPU_GB`, `WORK`, `ONCE`, `POLL_S`) | docs/queue/jobs.json (GitHub), queue/status/ | queue/status/<id>.json, queue/logs/<id>.log, plus the job's own outputs |
| `kaggle_launch.py` | Kaggle launcher: reads `HF_TOKEN` from Kaggle secrets, installs the engine's packages, fetches `worker.py` at current main and starts it as worker `kaggle` | – | (whatever the worker runs) |

## Job queue (any GPU machine)

Instead of one launcher cell per job, start a worker and let it pull jobs from the queue (`docs/queue/jobs.json`). On Colab:

```python
import os, subprocess, urllib.request, time
from google.colab import userdata
urllib.request.urlretrieve('https://raw.githubusercontent.com/Horus331/mass-flood-watch/main/sim/colab/worker.py?x=' + str(int(time.time())), '/content/worker.py')
env = dict(os.environ, HF_TOKEN=userdata.get('HF_TOKEN'), WORKER='colab2', GPU_GB='22')
subprocess.Popen(['bash', '-c', 'nohup python /content/worker.py > /content/worker.out 2>&1 &'], env=env)
```

On Kaggle (GPU T4 ×2 notebook, `HF_TOKEN` added as a notebook secret), the whole launch is one cell:

```python
exec(__import__('urllib.request').request.urlopen('https://raw.githubusercontent.com/Horus331/mass-flood-watch/main/sim/colab/kaggle_launch.py').read())
```

It prints the commit it started from and the GPU; tail `/kaggle/working/worker.out` to follow the jobs. Claims and heartbeats are HF commits under `queue/status/`, logs under `queue/logs/`; a job whose worker goes quiet for 40 min is re-queued.

Data jobs that need no GPU run on GitHub Actions instead (`.github/workflows/`: nlcd, soils, gauges, hwm, hwm_ma, drain).
