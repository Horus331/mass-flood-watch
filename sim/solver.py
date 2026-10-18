"""2-D local-inertial shallow-water solver (Bates et al. 2010, as in LISFLOOD-FP) that runs on numpy or CuPy.

    sim = LocalInertial(z, dx, manning, xp=cupy)      # xp = numpy (CPU) or cupy (GPU); arrays live on that device
    sim.step(dt, source=rain_m_per_s)                 # source: array of water added per second (m/s), or None
    sim.step(dt, level=sea_level_m)                   # coastal: cells in `fixed` are held at this water level
    dt = sim.stable_dt()

Identical maths to the numpy class that produced every scene on the site up to Oct 17, 2026; `selftest()` checks the two
back ends against each other on a synthetic hill (max difference must be below 1e-4 m after 300 steps).

Optional per-cell fields (all arrays on the same device as z):
    sim.n2      Manning n squared per cell (float32), instead of one value        -> land-cover roughness
    sim.sink    boolean: water that reaches these cells leaves the model            -> sea cells in rain scenes
    sim.fixed   boolean: cells held at `level`                                      -> sea boundary in coastal scenes
"""
import math
import numpy as np

G = 9.81


class LocalInertial:
    def __init__(self, z, dx, n, fixed=None, xp=np, theta=1.0, fr_max=1.0):
        self.xp = xp
        self.theta = float(theta)          # 1.0 = Bates 2010 update; 0.7 = q-centred scheme of de Almeida & Bates 2013 (damps checkerboarding on steep ground)
        self.fr_max = float(fr_max)        # Froude cap on face flux (1.0 = original; 2.0 lets steep brooks run supercritical)
        self.z = xp.asarray(z, dtype=xp.float32); self.dx = float(dx)
        self.n2 = xp.asarray(n, dtype=xp.float32) ** 2 if hasattr(n, 'shape') else float(n) ** 2
        ny, nx = self.z.shape
        self.h = xp.zeros_like(self.z); self.qx = xp.zeros((ny, nx - 1), xp.float32); self.qy = xp.zeros((ny - 1, nx), xp.float32)
        self.fixed = None if fixed is None else xp.asarray(fixed, dtype=bool)
        self.sink = None
        self.hmax = xp.zeros_like(self.z)
        if self.fixed is not None:
            self.ffx = self.fixed[:, :-1] & self.fixed[:, 1:]; self.ffy = self.fixed[:-1, :] & self.fixed[1:, :]

    def _n2_face(self, axis):
        n2 = self.n2
        if not hasattr(n2, 'shape'): return n2
        return (n2[:, :-1] + n2[:, 1:]) * 0.5 if axis == 0 else (n2[:-1, :] + n2[1:, :]) * 0.5

    def _face(self, q, eta_a, eta_b, z_a, z_b, dt, n2, axis=0):
        xp = self.xp
        hf = xp.maximum(eta_a, eta_b) - xp.maximum(z_a, z_b)
        wet = hf > 1e-3
        hf = xp.where(wet, hf, xp.float32(1.0)).astype(xp.float32)
        s = (eta_b - eta_a) / self.dx
        if self.theta < 1.0:                                   # q-centred: blend the face flux with its two neighbours along the axis
            if axis == 0:
                qm = xp.concatenate([q[:, :1], q[:, :-1]], axis=1); qp = xp.concatenate([q[:, 1:], q[:, -1:]], axis=1)
            else:
                qm = xp.concatenate([q[:1, :], q[:-1, :]], axis=0); qp = xp.concatenate([q[1:, :], q[-1:, :]], axis=0)
            qc = self.theta * q + 0.5 * (1.0 - self.theta) * (qm + qp)
        else:
            qc = q
        qn = (qc - G * hf * dt * s) / (1 + G * dt * n2 * xp.abs(q) / hf ** (7.0 / 3.0))
        lim = self.fr_max * hf * xp.sqrt(G * hf)
        qn = xp.clip(qn, -lim, lim)
        return xp.where(wet, qn, xp.float32(0)).astype(xp.float32)

    def velocity(self):
        """Cell-centred flow speed (m/s): the largest face speed |q|/hf around each cell."""
        xp = self.xp; z, h = self.z, self.h; eta = z + h
        hfx = xp.maximum(xp.maximum(eta[:, :-1], eta[:, 1:]) - xp.maximum(z[:, :-1], z[:, 1:]), 1e-3)
        hfy = xp.maximum(xp.maximum(eta[:-1, :], eta[1:, :]) - xp.maximum(z[:-1, :], z[1:, :]), 1e-3)
        vx = xp.abs(self.qx) / hfx; vy = xp.abs(self.qy) / hfy
        v = xp.zeros_like(h)
        v[:, :-1] = xp.maximum(v[:, :-1], vx); v[:, 1:] = xp.maximum(v[:, 1:], vx)
        v[:-1, :] = xp.maximum(v[:-1, :], vy); v[1:, :] = xp.maximum(v[1:, :], vy)
        return xp.where(h > 1e-3, v, 0).astype(xp.float32)

    def step(self, dt, source=None, level=None):
        xp = self.xp; z, h = self.z, self.h
        if self.fixed is not None and level is not None:
            h[self.fixed] = xp.maximum(xp.float32(level) - z[self.fixed], 0)
        eta = z + h
        self.qx = self._face(self.qx, eta[:, :-1], eta[:, 1:], z[:, :-1], z[:, 1:], dt, self._n2_face(0), axis=0)
        self.qy = self._face(self.qy, eta[:-1, :], eta[1:, :], z[:-1, :], z[1:, :], dt, self._n2_face(1), axis=1)
        if self.fixed is not None:
            self.qx[self.ffx] = 0; self.qy[self.ffy] = 0
        out = (xp.pad(xp.maximum(self.qx, 0), ((0, 0), (0, 1))) + xp.pad(xp.maximum(-self.qx, 0), ((0, 0), (1, 0)))
               + xp.pad(xp.maximum(self.qy, 0), ((0, 1), (0, 0))) + xp.pad(xp.maximum(-self.qy, 0), ((1, 0), (0, 0)))) * (dt / self.dx)
        f = xp.where(out > h, h / xp.maximum(out, 1e-9), xp.float32(1.0)).astype(xp.float32)
        self.qx = xp.where(self.qx > 0, self.qx * f[:, :-1], self.qx * f[:, 1:])
        self.qy = xp.where(self.qy > 0, self.qy * f[:-1, :], self.qy * f[1:, :])
        div = xp.zeros_like(h)
        div[:, :-1] -= self.qx; div[:, 1:] += self.qx; div[:-1, :] -= self.qy; div[1:, :] += self.qy
        h += div * (dt / self.dx)
        if source is not None:
            h += source * dt
        xp.maximum(h, 0, out=h)
        if self.sink is not None:
            h[self.sink] = 0
        if self.fixed is None:
            h[0, :] = 0; h[-1, :] = 0; h[:, 0] = 0; h[:, -1] = 0
        xp.maximum(self.hmax, h, out=self.hmax)

    def stable_dt(self, cfl=0.7, cap=20.0):
        xp = self.xp
        if self.fixed is None:
            hm = float(self.h.max())
        else:
            hm = float(xp.max(xp.where(self.fixed, 0, self.h)))
            hm = max(hm, float(xp.max(xp.where(self.fixed, xp.minimum(self.h, 6.0), 0))))
        return min(cap, cfl * self.dx / math.sqrt(G * max(hm, 0.05)))


def selftest(xp_gpu, n=400, steps=300, seed=0, theta=1.0, fr_max=1.0):
    """Run the same scene on numpy and on `xp_gpu`; return the largest difference in depth (m)."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:n, 0:n]
    z = (30 - 0.05 * np.hypot(x - n / 2, y - n / 2) + rng.normal(0, 0.3, (n, n))).astype(np.float32)   # a hill with noise
    rain = (np.full((n, n), 40 / 3.6e6, np.float32))                                                     # 40 mm/h everywhere
    a = LocalInertial(z, 20.0, 0.05, xp=np, theta=theta, fr_max=fr_max); b = LocalInertial(z, 20.0, 0.05, xp=xp_gpu, theta=theta, fr_max=fr_max)
    rb = xp_gpu.asarray(rain)
    for k in range(steps):
        dt = min(a.stable_dt(), b.stable_dt())
        a.step(dt, source=rain if k < steps // 2 else None); b.step(dt, source=rb if k < steps // 2 else None)
    hb = xp_gpu.asnumpy(b.h) if hasattr(xp_gpu, 'asnumpy') else np.asarray(b.h)
    return float(np.abs(a.h - hb).max()), float(a.h.max())


if __name__ == '__main__':
    import time
    try:
        import cupy as cp
    except ImportError:
        cp = None
    if cp is None:
        print('cupy not available; numpy-only check');  print('numpy vs numpy:', selftest(np))
    else:
        t0 = time.time(); d, hmax = selftest(cp); print(f'max |CPU - GPU| = {d:.2e} m (peak depth {hmax:.2f} m) in {time.time() - t0:.1f}s')
        n = 4000; z = cp.random.random((n, n), dtype=cp.float32) * 10; s = LocalInertial(z, 20.0, 0.05, xp=cp); src = cp.full((n, n), 1e-5, cp.float32)
        cp.cuda.Device().synchronize(); t0 = time.time()
        for _ in range(20): s.step(1.0, source=src)
        cp.cuda.Device().synchronize(); print(f'GPU: {n * n / 1e6:.0f} M cells, {(time.time() - t0) / 20 * 1000:.0f} ms per step')
