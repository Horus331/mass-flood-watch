"""Kaggle launcher for the shared job queue: exec'd from a one-line notebook cell.  Reads HF_TOKEN from Kaggle secrets,
installs what the engine needs, fetches worker.py at the current main and runs it in the background as worker 'kaggle'."""
import os, sys, subprocess, urllib.request, json
from kaggle_secrets import UserSecretsClient
tok = UserSecretsClient().get_secret('HF_TOKEN')
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'huggingface_hub', 'pyproj', 'rasterio', 'pygrib', 'pmtiles', 'mercantile', 'cupy-cuda12x'], check=False)
sha = json.loads(urllib.request.urlopen(urllib.request.Request('https://api.github.com/repos/Horus331/mass-flood-watch/commits/main', headers={'User-Agent': 'mfw'})).read())['sha']
os.makedirs('/content', exist_ok=True); os.makedirs('/kaggle/working', exist_ok=True)
urllib.request.urlretrieve(f'https://raw.githubusercontent.com/Horus331/mass-flood-watch/{sha}/sim/colab/worker.py', '/kaggle/working/worker.py')
env = dict(os.environ, HF_TOKEN=tok, WORKER='kaggle', GPU_GB=os.environ.get('GPU_GB', '14'), WORK='/kaggle/working', GIT_SHA=sha, SESSION_H=os.environ.get('SESSION_H', '11.5'))
subprocess.Popen(f'{sys.executable} /kaggle/working/worker.py > /kaggle/working/worker.out 2>&1', shell=True, env=env)
print('worker started at', sha[:8]); print(subprocess.run('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader', shell=True, capture_output=True, text=True).stdout)
