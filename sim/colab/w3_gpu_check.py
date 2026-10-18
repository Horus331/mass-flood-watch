"""Week plan, day 2: GPU check. Runs sim/solver.py's self-test on CuPy and times a 16 M-cell step."""
import subprocess, sys, time, urllib.request, os
LOGP = '/content/drive/MyDrive/flood_atlas_state/log_gpu.txt'
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True); open(LOGP, 'a').write(s + '\n')
r = subprocess.run('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader', shell=True, capture_output=True, text=True); log('GPU:', r.stdout.strip() or r.stderr.strip()[:200])
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'cupy-cuda12x'], check=False)
urllib.request.urlretrieve('https://raw.githubusercontent.com/Horus331/mass-flood-watch/main/sim/solver.py', '/content/solver.py')
sys.path.insert(0, '/content'); import numpy as np, solver
try:
    import cupy as cp
    t0 = time.time(); d, hmax = solver.selftest(cp); log(f'self-test: max |CPU - GPU| = {d:.2e} m (peak depth {hmax:.2f} m) in {time.time() - t0:.1f}s')
    for n in (2000, 4000, 8000):
        z = cp.random.random((n, n), dtype=cp.float32) * 10; s = solver.LocalInertial(z, 20.0, 0.05, xp=cp); src = cp.full((n, n), 1e-5, cp.float32)
        for _ in range(3): s.step(1.0, source=src)
        cp.cuda.Device().synchronize(); t0 = time.time()
        for _ in range(20): s.step(1.0, source=src)
        cp.cuda.Device().synchronize(); ms = (time.time() - t0) / 20 * 1000; log(f'GPU: {n}x{n} = {n * n / 1e6:.0f} M cells, {ms:.0f} ms per step, {cp.get_default_memory_pool().used_bytes() / 2**30:.1f} GB used')
        del s, z, src; cp.get_default_memory_pool().free_all_blocks()
except Exception as e:
    log('GPU FAILED', repr(e)[:300])
log('ALL DONE')
