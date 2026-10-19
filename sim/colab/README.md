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
| `../crossings_capacity.py` | post-processing (CPU, any runtime): per road-stream crossing, modelled channel flow Q = h·v·W as a StreamStats return period, water surface vs road deck → freeboard / overtopping (L2 hydraulic exceedance); NBI culverts: depth at the structure vs waterway adequacy code. `python sim/crossings_capacity.py <run_dir> --out <json> [--channels channels30.npz --channels-meta channels30_meta.json]`; `--selftest` runs offline | runs/<RUN>_<RES>m/ (z, hmax, vmax, meta), docs/network/crossings_ma.json + nbi_ma.json, data/channels30 (optional) | <run_dir>/crossings.json (or `--out`) |

Data jobs that need no GPU run on GitHub Actions instead (`.github/workflows/`: nlcd, soils, gauges, hwm, hwm_ma, drain).
