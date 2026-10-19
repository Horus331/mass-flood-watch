"""Put a NOAA HAND-FIM storm map (runs/fim_<storm>/depth.tif from sim/fim_maps.py) on the v2 site.

    STORMS=jul2023,sep2023 HF_TOKEN=... python sim/fim_publish.py

For each storm: depth.tif (EPSG:5070, 10 m, cm) -> peak-depth grid on the site's EPSG:26986 grid at 30 m (max resampling) ->
one depth-class frame f000.png (same classes as the engine: 5-10 cm, 10-30, 30-100, 1-2.5 m, > 2.5 m) + meta.json + hmax.npy,
uploaded to runs/fim_<storm>/, then sim/colab/w5_tiles.py builds the map tiles and samples the road segments (flooded roads,
cut-off and detour layers on the site work from those).
"""
import os, sys, json, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fim_maps import validate_export
from nwm_compare import STORMS
from huggingface_hub import HfApi, hf_hub_download

REPO = 'mohabeldokla/mass-flood-watch-tiles'; TOK = os.environ.get('HF_TOKEN')
TITLES = dict(jul2023='July 9-11, 2023 western Mass. rain', sep2023='Sept 11, 2023 flash floods', dec2023='Dec 18, 2023 statewide rain',
              jan2024='Jan 9-10, 2024 rain on snow')
api = HfApi(token=TOK)
for storm in [s.strip() for s in os.environ.get('STORMS', 'jul2023').split(',') if s.strip()]:
    d = f'/tmp/fimpub/{storm}'; os.makedirs(d, exist_ok=True)
    tif = hf_hub_download(REPO, f'runs/fim_{storm}/depth.tif', repo_type='dataset', token=TOK)
    validate_export(tif, d, storm, 30.0)
    hm = np.load(f'{d}/hmax.npy'); meta = json.load(open(f'{d}/meta.json'))
    cls = np.zeros(hm.shape, np.uint8)
    for i, th in enumerate((0.05, 0.10, 0.30, 1.0, 2.5)): cls[hm >= th] = i + 1
    Image.fromarray(cls, 'L').save(f'{d}/f000.png', optimize=True)
    a, b = STORMS[storm]
    wet = float((hm >= 0.1).sum() * 900 / 1e6); deep = float((hm >= 0.5).sum() * 900 / 1e6)
    meta.update(run=f'fim_{storm}', title=f'{TITLES.get(storm, storm)} · NOAA National Water Model + HAND flood map (peak)', shape=list(hm.shape),
                t0=a + ':00Z' if not a.endswith('Z') else a, frame_min=60, frames=[dict(t=b + ':00Z', wet_km2=round(wet, 1), deep_km2=round(deep, 1))],
                peak_wet_km2=round(wet, 1), model='NOAA NWM analysis_assim peak flows -> OWP HAND-FIM (FIM4) rating curves; riverine flooding only')
    json.dump(meta, open(f'{d}/meta.json', 'w'))
    np.save(f'{d}/hmax.npy', hm.astype(np.float16))
    from huggingface_hub import CommitOperationAdd       # one commit per storm (HF allows 128 commits per hour per repo)
    api.create_commit(REPO, repo_type='dataset', commit_message=f'runs/fim_{storm}: site frame + meta',
                      operations=[CommitOperationAdd(path_in_repo=f'runs/fim_{storm}/{f}', path_or_fileobj=f'{d}/{f}') for f in ('f000.png', 'hmax.npy', 'meta.json')])
    print(storm, 'uploaded', hm.shape, f'{wet:.0f} km2 wet', flush=True)
    w5 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'colab', 'w5_tiles.py')
    subprocess.run([sys.executable, w5], env=dict(os.environ, RUN_DIR=f'runs/fim_{storm}'), check=True)
