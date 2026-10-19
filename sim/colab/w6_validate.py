"""Score a published run against surveyed high-water marks and road flood reports (Stage 4), on Colab or anywhere.

    RUN_DIR=runs/dec2023_30m python w6_validate.py
Downloads meta.json + hmax.npy from Hugging Face, the validation data from the site repo, runs sim/validate.py and uploads
validation.json next to the run (and prints the summary).
"""
import os, sys, json, subprocess, urllib.request, time
for mod, pkg in (('pyproj', 'pyproj'), ('huggingface_hub', 'huggingface_hub')):
    try: __import__(mod)
    except ImportError: subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', pkg], check=False)
from huggingface_hub import HfApi, hf_hub_download
RUN_DIR = os.environ.get('RUN_DIR', 'runs/dec2023_30m'); REPO = 'mohabeldokla/mass-flood-watch-tiles'; TOK = os.environ.get('HF_TOKEN')
RAW = 'https://raw.githubusercontent.com/Horus331/mass-flood-watch/' + os.environ.get('GIT_SHA', 'main') + '/'
d = f'/content/{RUN_DIR.replace("/", "_")}'; os.makedirs(d, exist_ok=True)
for f in ('meta.json', 'hmax.npy', 'z.npy', 'hsnap.npy'):
    try: p = hf_hub_download(REPO, f'{RUN_DIR}/{f}', repo_type='dataset', token=TOK); subprocess.run(['cp', p, f'{d}/{f}'])
    except Exception as e: print('no', f, '(older run):', repr(e)[:80])
for f in ('sim/validate.py', 'docs/validation/stn_ma.json', 'docs/prone/flood_reports.json'):
    os.makedirs(os.path.dirname(f'/content/repo/{f}'), exist_ok=True); urllib.request.urlretrieve(RAW + f + '?x=' + str(int(time.time())), f'/content/repo/{f}')
sys.path.insert(0, '/content/repo/sim'); import validate
out = validate.main(d, hwm_path='/content/repo/docs/validation/stn_ma.json', reports_path='/content/repo/docs/prone/flood_reports.json')
if TOK:
    HfApi(token=TOK).upload_file(path_or_fileobj=f'{d}/validation.json', path_in_repo=f'{RUN_DIR}/validation.json', repo_id=REPO, repo_type='dataset')
    print('uploaded', f'{RUN_DIR}/validation.json')
