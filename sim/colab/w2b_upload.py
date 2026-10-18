"""Week plan: copy the 10 m foundation data from Drive to the public Hugging Face dataset, so GPU runtimes (which have no
Drive mount) can read it, and so nothing depends on a browser-authorised Drive session.

Layout on Hugging Face (dataset mohabeldokla/mass-flood-watch-tiles):
    data/dem10/<x>_<y>.npy        3DEP 10 m elevation, EPSG:26986, 20 km tiles (float32, NaN = no data)
    data/dem10/index.json
    data/drain10/d_<r>_<c>.png    10 m flow directions + upstream-area class (one byte per cell), EPSG:5070
    data/drain10/index.json
    data/nhdplushr_flowlines.geojson, data/stn_hwms_ma.json
Runs in the background; log in W/log_upload.txt.  Safe to re-run: skips files already present.
"""
import os, time, json
from google.colab import userdata
from huggingface_hub import HfApi, CommitOperationAdd
W = '/content/drive/MyDrive/flood_atlas_state'
LOG = open(f'{W}/log_upload.txt', 'a')
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n'); LOG.flush()
api = HfApi(token=userdata.get('HF_TOKEN')); REPO = 'mohabeldokla/mass-flood-watch-tiles'
have = set(api.list_repo_files(REPO, repo_type='dataset'))
log('files already on HF:', len(have))
def upload_dir(local, remote, exts, batch=25):
    files = sorted(f for f in os.listdir(local) if f.endswith(exts))
    todo = [f for f in files if f'{remote}/{f}' not in have]
    log(f'{remote}: {len(files)} files, {len(todo)} to upload')
    for i in range(0, len(todo), batch):
        ops = [CommitOperationAdd(path_in_repo=f'{remote}/{f}', path_or_fileobj=f'{local}/{f}') for f in todo[i:i + batch]]
        for k in range(5):
            try:
                api.create_commit(REPO, repo_type='dataset', operations=ops, commit_message=f'{remote} {i + 1}-{i + len(ops)} of {len(todo)}'); break
            except Exception as e:
                log('  retry', k, repr(e)[:160]); time.sleep(10 + 20 * k)
        log(f'  {remote}: {min(i + batch, len(todo))}/{len(todo)}')
for d, exts in (('dem10', ('.npy', '.json')), ('drain10', ('.png', '.json'))):
    if os.path.isdir(f'{W}/{d}') and os.path.exists(f'{W}/{d}/index.json'):
        upload_dir(f'{W}/{d}', f'data/{d}', exts)
    else:
        log(d, 'not finished yet, skipped')
for f in ('nhdplushr_flowlines.geojson', 'stn_hwms_ma.json'):
    if os.path.exists(f'{W}/{f}') and f'data/{f}' not in have:
        api.upload_file(path_or_fileobj=f'{W}/{f}', path_in_repo=f'data/{f}', repo_id=REPO, repo_type='dataset'); log('uploaded', f)
log('ALL DONE')
