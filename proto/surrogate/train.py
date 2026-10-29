"""Train the LISFLOOD-FP surrogate: a U-Net from the input channels (dataset.py) to peak depth hmax, pre-registered in
docs/proto/surrogate/SURROGATE.md.

    python proto/surrogate/train.py --data ~/scratch/surrogate/dataset --model A --out ~/scratch/surrogate/models/A.pt     # train split; val picks the step
    python proto/surrogate/train.py --data ... --model B --iters-from ~/scratch/surrogate/models/A.pt --out .../B.pt         # every generated scene, fixed steps
    python proto/surrogate/train.py --selftest

Model A trains on the 'train' scenes and keeps the checkpoint with the lowest validation loss (the 'val' rain days; checked every --val-every
steps).  Model B is the same recipe on every generated scene (train + val + test_box + test_rain) for exactly A's best step count, with no
look at any evaluation scene.  Catalogue storms and District 3 inputs are never read here.
Loss per cell: Huber on t = log1p(h / 0.1 m) + 0.5 x BCE of the wet head (h >= 0.30 m), weights 1 on land, 0.3 on water / channel cells,
0 on sea / no-data; land cells near the closure depth (0.15-0.60 m) weigh 2.  Patches 256 x 256 (5.1 km at 20 m), half of them centred on a
cell >= 0.30 m; random flips and 90-degree turns (every channel is a scalar field, so the physics is unchanged).
"""
import os, sys, json, time, math, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import dataset as DS

T_SCALE = 0.1          # m: t = log1p(h / T_SCALE)
WET_M = 0.30
CFG = dict(base=24, depth=4, patch=256, batch=12, lr=1e-3, wd=1e-4, iters=20000, val_every=500, wet_frac=0.5, seed=0)
B_SPLITS = ('train', 'val', 'test_box', 'test_rain')


def to_t(h): return np.log1p(np.maximum(h, 0) / T_SCALE)


def from_t(t): return T_SCALE * np.expm1(np.maximum(t, 0))


def build_model(cin, base=24, depth=4):
    import torch.nn as nn
    def block(a, b): return nn.Sequential(nn.Conv2d(a, b, 3, padding=1), nn.GroupNorm(min(8, b), b), nn.SiLU(), nn.Conv2d(b, b, 3, padding=1), nn.GroupNorm(min(8, b), b), nn.SiLU())

    class UNet(nn.Module):
        """Plain U-Net (Ronneberger et al. 2015) with GroupNorm; outputs t = log1p(h / 0.1) and the wet logit (h >= 0.30 m)."""
        def __init__(self):
            super().__init__(); ch = [base * 2 ** i for i in range(depth + 1)]
            self.down = nn.ModuleList([block(cin if i == 0 else ch[i - 1], ch[i]) for i in range(depth)]); self.mid = block(ch[depth - 1], ch[depth])
            self.up = nn.ModuleList([nn.ConvTranspose2d(ch[i + 1], ch[i], 2, stride=2) for i in reversed(range(depth))])
            self.dec = nn.ModuleList([block(2 * ch[i], ch[i]) for i in reversed(range(depth))]); self.head = nn.Conv2d(ch[0], 2, 1); self.pool = nn.MaxPool2d(2)

        def forward(self, x):
            sk = []
            for d in self.down: x = d(x); sk.append(x); x = self.pool(x)
            x = self.mid(x)
            for u, d, s in zip(self.up, self.dec, reversed(sk)): x = d(__import__('torch').cat([u(x), s], 1))
            return self.head(x)
    return UNet()


class Scenes:
    """Memory-mapped scenes of one split set; normalised random patches with targets and loss weights."""
    def __init__(self, data, splits, norm=None, seed=0):
        I = json.load(open(os.path.join(data, 'index.json'))); self.ch = I['channels']; self.data = data
        self.norm = norm or json.load(open(os.path.join(data, 'norm.json')))
        self.mean = np.array(self.norm['mean'], np.float32)[:, None, None]; self.std = np.array(self.norm['std'], np.float32)[:, None, None]
        self.meta = [m for m in I['scenes'] if m['split'] in splits and m['has_target']]
        if not self.meta: raise SystemExit(f'no scenes with targets in splits {splits}')
        self.X = [np.load(os.path.join(data, m['path'], 'x.npy'), mmap_mode='r') for m in self.meta]
        self.Y = [np.load(os.path.join(data, m['path'], 'y.npy'), mmap_mode='r') for m in self.meta]
        self.wet = []
        rng = np.random.default_rng(seed)
        for y in self.Y:       # a sample of wet cells per scene (patch centres)
            r, c = np.nonzero(np.asarray(y) >= WET_M)
            k = rng.choice(len(r), min(len(r), 5000), replace=False) if len(r) else []
            self.wet.append((r[k], c[k]) if len(r) else None)
        self.iw, self.ic, self.isea = self.ch.index('water'), self.ch.index('chan'), self.ch.index('sea')

    def weights(self, X, y):
        sea = X[self.isea] > 0.5; wat = (X[self.iw] > 0.5) | (X[self.ic] > 0.5)
        w = np.where(sea, 0.0, np.where(wat, 0.3, 1.0)).astype(np.float32)
        return np.where(~wat & ~sea & (y >= 0.15) & (y <= 0.60), 2.0 * w, w)

    def patch(self, rng, size, wet_frac=0.5, i=None, r0=None, c0=None, aug=True):
        i = int(rng.integers(len(self.meta))) if i is None else i; X, Y = self.X[i], self.Y[i]; ny, nx = Y.shape; s = min(size, ny, nx)
        if r0 is None:
            W = self.wet[i]
            if W is not None and rng.uniform() < wet_frac:
                k = int(rng.integers(len(W[0]))); r0 = int(np.clip(W[0][k] - s // 2 + rng.integers(-s // 4, s // 4 + 1), 0, ny - s)); c0 = int(np.clip(W[1][k] - s // 2 + rng.integers(-s // 4, s // 4 + 1), 0, nx - s))
            else: r0, c0 = int(rng.integers(0, ny - s + 1)), int(rng.integers(0, nx - s + 1))
        x = np.asarray(X[:, r0:r0 + s, c0:c0 + s], np.float32); y = np.asarray(Y[r0:r0 + s, c0:c0 + s], np.float32)
        w = self.weights(x, y); x = (x - self.mean) / self.std
        if aug:
            k = int(rng.integers(4)); x, y, w = np.rot90(x, k, (1, 2)), np.rot90(y, k), np.rot90(w, k)
            if rng.uniform() < 0.5: x, y, w = x[:, :, ::-1], y[:, ::-1], w[:, ::-1]
        if s < size:     # small scenes (selftest): pad to the patch size with zero weight
            pad = ((0, 0), (0, size - s), (0, size - s)); x = np.pad(x, pad); y = np.pad(y, pad[1:]); w = np.pad(w, pad[1:])
        return np.ascontiguousarray(x), np.ascontiguousarray(y), np.ascontiguousarray(w)

    def batch(self, rng, n, size, wet_frac=0.5, aug=True):
        P = [self.patch(rng, size, wet_frac, aug=aug) for _ in range(n)]
        return np.stack([p[0] for p in P]), np.stack([p[1] for p in P]), np.stack([p[2] for p in P])


def loss_fn(out, y, w):
    import torch, torch.nn.functional as F
    t = torch.log1p(torch.clamp(y, min=0) / T_SCALE); wet = (y >= WET_M).float()
    reg = F.smooth_l1_loss(out[:, 0], t, reduction='none', beta=0.1); bce = F.binary_cross_entropy_with_logits(out[:, 1], wet, reduction='none')
    ws = w.sum().clamp(min=1.0)
    return ((reg + 0.5 * bce) * w).sum() / ws, (reg * w).sum() / ws, (bce * w).sum() / ws


def train(data, model_name, out, cfg=None, iters=None, device=None, log_every=100):
    import torch
    cfg = dict(CFG, **(cfg or {})); torch.manual_seed(cfg['seed']); rng = np.random.default_rng(cfg['seed'])
    dev = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    splits = ('train',) if model_name == 'A' else B_SPLITS
    D = Scenes(data, splits, seed=cfg['seed']); V = Scenes(data, ('val',), norm=D.norm, seed=1) if model_name == 'A' else None
    if model_name == 'A' and V is not None:      # a fixed validation set: 4 patches per val scene, same every check
        vr = np.random.default_rng(123); VB = [V.patch(vr, cfg['patch'], 0.5, i=i, aug=False) for i in range(len(V.meta)) for _ in range(4)]
    net = build_model(len(D.ch), cfg['base'], cfg['depth']).to(dev); n_par = sum(p.numel() for p in net.parameters())
    n_it = int(iters or cfg['iters'])
    opt = torch.optim.AdamW(net.parameters(), lr=cfg['lr'], weight_decay=cfg['wd']); sch = torch.optim.lr_scheduler.OneCycleLR(opt, cfg['lr'], total_steps=max(2, n_it), pct_start=0.05)
    print(f'model {model_name}: {len(D.meta)} scenes {sorted({m["split"] for m in D.meta})}, {n_par / 1e6:.2f} M parameters, {n_it} steps on {dev}', flush=True)
    best = dict(val=float('inf'), step=n_it); hist = []; t0 = time.time()
    def save(path, step, extra):
        torch.save(dict(state=net.state_dict(), cfg=cfg, channels=D.ch, norm=D.norm, model=model_name, step=step, n_params=n_par, splits=list(splits),
                        scenes=[m['id'] for m in D.meta], **extra), path)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    for it in range(1, n_it + 1):
        net.train(); x, y, w = (torch.from_numpy(a).to(dev) for a in D.batch(rng, cfg['batch'], cfg['patch'], cfg['wet_frac']))
        L, Lr, Lb = loss_fn(net(x), y, w); opt.zero_grad(); L.backward(); torch.nn.utils.clip_grad_norm_(net.parameters(), 1.0); opt.step(); sch.step()
        if it % log_every == 0 or it == 1: print(f'step {it} loss {L.item():.4f} (reg {Lr.item():.4f}, wet {Lb.item():.4f}) {time.time() - t0:.0f} s', flush=True)
        if model_name == 'A' and V is not None and (it % cfg['val_every'] == 0 or it == n_it):
            net.eval(); vl = []
            with torch.no_grad():
                for k in range(0, len(VB), cfg['batch']):
                    ch = VB[k:k + cfg['batch']]; xb, yb, wb = (torch.from_numpy(np.stack([c[j] for c in ch])).to(dev) for j in range(3))
                    vl.append(loss_fn(net(xb), yb, wb)[0].item() * len(ch))
            v = sum(vl) / len(VB); hist.append(dict(step=it, val=v, train=L.item())); print(f'  val {v:.4f} at step {it}', flush=True)
            if v < best['val']: best = dict(val=v, step=it); save(out, it, dict(best=best, history=hist))
    if model_name != 'A' or V is None: best = dict(val=None, step=n_it); save(out, n_it, dict(best=best, history=hist))
    else:
        ck = torch.load(out, map_location='cpu', weights_only=False); ck['history'] = hist; ck['best'] = best; torch.save(ck, out)
    print(f'model {model_name} -> {out}; best {best}; {time.time() - t0:.0f} s', flush=True)
    return best


def load(path, device='cpu'):
    import torch
    ck = torch.load(path, map_location=device, weights_only=False)
    net = build_model(len(ck['channels']), ck['cfg']['base'], ck['cfg']['depth']); net.load_state_dict(ck['state']); net.eval().to(device)
    return net, ck


def selftest():
    import tempfile
    import torch
    d = tempfile.mkdtemp(prefix='surr_tr_'); root = os.path.join(d, 'root'); pp, ip, repo = DS.synth_root(root)
    DS.build(root, [pp], ip, os.path.join(root, 'ds'), repo=repo)
    net = build_model(len(DS.CHANNELS), 8, 3); o = net(torch.zeros(1, len(DS.CHANNELS), 64, 64)); assert tuple(o.shape) == (1, 2, 64, 64)
    S = Scenes(os.path.join(root, 'ds'), ('train',)); x, y, w = S.batch(np.random.default_rng(0), 2, 64)
    assert x.shape == (2, len(DS.CHANNELS), 64, 64) and np.isfinite(x).all() and (w >= 0).all()
    assert np.allclose(from_t(to_t(np.array([0, 0.3, 2.0]))), [0, 0.3, 2.0], atol=1e-6)
    cfg = dict(base=8, depth=3, patch=64, batch=2, val_every=2)
    bA = train(os.path.join(root, 'ds'), 'A', os.path.join(d, 'A.pt'), cfg, iters=2, device='cpu', log_every=1)
    bB = train(os.path.join(root, 'ds'), 'B', os.path.join(d, 'B.pt'), cfg, iters=bA['step'], device='cpu', log_every=1)
    netA, ckA = load(os.path.join(d, 'A.pt')); _, ckB = load(os.path.join(d, 'B.pt'))
    assert ckA['splits'] == ['train'] and set(ckB['splits']) == set(B_SPLITS) and not any(s.startswith('jul2023') for s in ckA['scenes'] + ckB['scenes'])
    assert ckA['best']['step'] in (1, 2) and len(ckA['channels']) == len(DS.CHANNELS)
    print('ok   U-Net shapes, patches, t transform, 2 training steps for A (val-picked) and B (fixed steps); no catalogue scene in either')
    print('TRAIN SELFTEST PASSED'); return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--data'); ap.add_argument('--model', choices=['A', 'B'], default='A'); ap.add_argument('--out')
    ap.add_argument('--iters', type=int); ap.add_argument('--iters-from', help='B: take the step count of this model A checkpoint'); ap.add_argument('--device')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    if not (a.data and a.out): ap.error('--data and --out (or --selftest)')
    it = a.iters
    if a.iters_from:
        import torch; it = torch.load(a.iters_from, map_location='cpu', weights_only=False)['best']['step']; print(f'B: {it} steps (best step of {a.iters_from})')
    train(a.data, a.model, a.out, iters=it, device=a.device)


if __name__ == '__main__':
    main()
