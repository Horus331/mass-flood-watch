"""Evaluate the LISFLOOD-FP surrogate against the physics and the labels, as pre-registered in docs/proto/surrogate/SURROGATE.md, and use it.

    python proto/surrogate/evaluate.py eval --data ~/scratch/surrogate/dataset --model-a A.pt --model-b B.pt --out results/surrogate_eval \
                                            --doc docs/proto/surrogate              # -> RESULTS.md + results.json (the decision)
    python proto/surrogate/evaluate.py predict --inputs surr_inputs.npz --model B.pt --out DIR [--storm forecast] [--threads 4]
                                            # rain over District 3 (w9 LF_INPUTS_ONLY=1 LF_SURR_SAVE=1) -> DIR/run (hmax.npy ...) + DIR/proto/segments.geojson
    python proto/surrogate/evaluate.py selftest

Metrics (SURROGATE.md section 4):
  cells     CSI at 0.30 m on land cells (not water / channel / carved / no data), CSI at 0.10 m, depth MAE and bias on wet cells (either >= 0.10 m)
  segments  CSI of the flagged sets (p_close >= 0.5 from proto/prototype.py with every default) of the surrogate and of LISFLOOD-FP; count ratio
  labels    site recall at the rule and at 3 % flagged (proto/score_v2.py, held-out 23 storms), surrogate minus the LISFLOOD-FP parity catalogue
            (docs/proto/parity/catalog), paired two-stage bootstrap (storms, then sites), 2000 replicates
  district  the same segment metrics on District 3, Sept 2023 radar run (docs/proto/turing/d3_sep2023_p); the HRRR 18z run's count (888) reported
  speed     District 3 inputs -> peak depth on --threads CPU threads (features + network)
Model A (train split, val-picked) gives the generalisation numbers (val, test_rain, test_box); model B (all generated scenes) gives every
number the decision uses.  Nothing here is tuned: one model, one decision.
"""
import os, sys, json, time, glob, shutil, argparse, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'proto'))
import dataset as DS

# the adoption rule (SURROGATE.md section 5), fixed 29 Oct 2026 before any surrogate was trained
ADOPT = dict(seg_csi_min=0.70, count_ratio=(0.80, 1.25), d_recall_point_min=-0.02, d_recall_lower_min=-0.04, levels=('rule', '0.03'), alpha=0.05,
             boot=2000, district_csi_min=0.60, district_ratio=(0.70, 1.30), speed_s_max=300.0, speed_threads=4)
CLOSE_P = 0.5
log = lambda *a: print(time.strftime('%H:%M:%S'), *a, flush=True)


# ------------------------------------------------------------------ inference
def normalise(X, norm):
    m = np.array(norm['mean'], np.float32)[:, None, None]; s = np.array(norm['std'], np.float32)[:, None, None]
    return (np.asarray(X, np.float32) - m) / s


def predict_grid(net, ck, X, tile=512, overlap=64, device='cpu', batch=4):
    """Peak depth (m) and P(h >= 0.30 m) over a whole grid: overlapping tiles, linear blending at the seams."""
    import torch
    C, ny, nx = X.shape; mult = 2 ** ck['cfg']['depth']; t = max(mult, min(tile, ((max(ny, nx) + mult - 1) // mult) * mult))
    step = max(mult, t - overlap); acc = np.zeros((2, ny, nx), np.float32); wsum = np.zeros((ny, nx), np.float32)
    ramp = np.minimum(1.0, (np.arange(t) + 1.0) / max(1, overlap)); w1 = np.minimum(ramp, ramp[::-1]); W = np.outer(w1, w1).astype(np.float32)
    rows = list(range(0, max(1, ny - t) + 1, step)); cols = list(range(0, max(1, nx - t) + 1, step))
    if rows[-1] + t < ny: rows.append(ny - t)
    if cols[-1] + t < nx: cols.append(nx - t)
    jobs = [(max(0, r), max(0, c)) for r in rows for c in cols]
    for k in range(0, len(jobs), batch):
        J = jobs[k:k + batch]; xb = np.zeros((len(J), C, t, t), np.float32)
        for j, (r, c) in enumerate(J):
            x = normalise(X[:, r:r + t, c:c + t], ck['norm']); xb[j, :, :x.shape[1], :x.shape[2]] = x
        with torch.no_grad(): o = net(torch.from_numpy(xb).to(device)).float().cpu().numpy()
        for j, (r, c) in enumerate(J):
            h_, w_ = min(t, ny - r), min(t, nx - c)
            acc[:, r:r + h_, c:c + w_] += o[j, :, :h_, :w_] * W[None, :h_, :w_]; wsum[r:r + h_, c:c + w_] += W[:h_, :w_]
    o = acc / np.maximum(wsum, 1e-6)[None]
    h = DS_from_t(o[0]); pw = 1.0 / (1.0 + np.exp(-o[1]))
    sea = np.asarray(X[DS.CHANNELS.index('sea')]) > 0.5
    return np.where(sea, 0, h).astype(np.float32), np.where(sea, 0, pw).astype(np.float32)


def DS_from_t(t):
    import train as TR
    return TR.from_t(t)


def load_model(path, device='cpu', threads=None):
    import torch, train as TR
    if threads: torch.set_num_threads(int(threads))
    return TR.load(path, device)


# ------------------------------------------------------------------ pseudo run dir -> proto/prototype.py
def pseudo_run(d, P, h, name, storm, model='LISFLOOD-FP surrogate (proto/surrogate)'):
    """A run folder with the files proto/prototype.py reads, from a surr_inputs.npz and a peak-depth grid (no timing, frames or velocity)."""
    os.makedirs(d, exist_ok=True); ny, nx = P['z'].shape
    np.save(os.path.join(d, 'hmax.npy'), np.asarray(h, np.float32)); np.save(os.path.join(d, 'z.npy'), P['z'].astype(np.float32))
    np.save(os.path.join(d, 'watermask.npy'), DS.watermask(P).astype(np.uint8))
    np.savez_compressed(os.path.join(d, 'z_raw.npz'), z_raw=P['z_raw'], z_raw_max10=P['z_raw_max10'])
    T = P['rain'].shape[0]; tot = np.zeros((ny, nx), np.float32); p1 = np.zeros_like(tot); p3 = np.zeros_like(tot); hp = np.zeros((ny, nx), np.int16)
    for r0 in range(0, ny, DS.ROW_CHUNK):
        r1 = min(ny, r0 + DS.ROW_CHUNK); R = DS.rain_rows(P, r0, r1); tot[r0:r1] = R.sum(0); p1[r0:r1] = R.max(0); hp[r0:r1] = R.argmax(0)
        p3[r0:r1] = np.stack([R[i:i + 3].sum(0) for i in range(max(1, T - 2))]).max(0)
    Rc = P['rain'].astype(np.float32)
    np.savez_compressed(os.path.join(d, 'rainstats.npz'), total=tot, peak1h=p1, peak3h=p3, hour_of_peak=hp, hourly_mean=Rc.reshape(T, -1).mean(1), hourly_max=Rc.reshape(T, -1).max(1))
    M = P['meta']; meta = dict(run=name, title=f'{name} (surrogate)', box=M['box'], res_m=M['res_m'], shape=[ny, nx], t0=M['t0'], frame_min=30, frames=[], crs='EPSG:26986',
                               model=model, solver='none (surrogate of LISFLOOD-FP 8.2 at the frozen baseline)', inputs=dict(env=M.get('env', {})),
                               rain_total_max_mm=round(float(tot.max())), rain_total_mean_mm=round(float(tot.mean())), storm=storm)
    json.dump(meta, open(os.path.join(d, 'meta.json'), 'w'))
    return d


def run_proto(run_dir, out, storm, segments=None, full=False):
    """proto/prototype.py at its defaults on run_dir -> out (segments.geojson, summary.json ...).  full: through closure_ml.extract, which also
    writes features_<storm>.csv / matches_<storm>.json (every in-box segment, the score_v2 universe) to out."""
    os.makedirs(out, exist_ok=True); env = dict(os.environ); [env.pop(k, None) for k in list(env) if k.startswith('PROTO_')]
    if full:
        cmd = [sys.executable, os.path.abspath(__file__), '_extract', '--run-dir', run_dir, '--storm', storm, '--out', out]
    else:
        cmd = [sys.executable, os.path.join(ROOT, 'proto', 'prototype.py'), '--run-dir', run_dir, '--out', out, '--storm', storm] + (['--segments', segments] if segments else [])
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=ROOT)
    if r.returncode != 0 or not os.path.exists(os.path.join(out, 'segments.geojson')):
        raise RuntimeError(f'prototype failed on {run_dir}: {r.stdout[-800:]} {r.stderr[-1500:]}')
    return out


def cmd_extract(a):
    import score_v2 as SV, closure_ml as CM
    tmp = os.path.join(a.out, '_proto'); CM.extract(a.run_dir, a.storm, SV.label_files(a.storm), out_dir=a.out, tmp=tmp)
    for f in ('segments.geojson', 'summary.json', 'watchlist.csv', 'REPORT.md'):
        if os.path.exists(os.path.join(tmp, f)): shutil.copy(os.path.join(tmp, f), os.path.join(a.out, f))
    shutil.rmtree(tmp, ignore_errors=True)


def flagged(path):
    """Segment ids with p_close >= 0.5: features_<storm>.csv when the folder has one (every in-box segment), else segments.geojson."""
    import csv
    d = path if os.path.isdir(path) else os.path.dirname(path)
    g = path if path.endswith('.geojson') else os.path.join(d, 'segments.geojson')
    return {int(f['properties']['segment']) for f in json.load(open(g))['features'] if (f['properties'].get('p_close') or 0) >= CLOSE_P}


def seg_csi(F, R):
    i, u = len(F & R), len(F | R); return dict(inter=i, union=u, n_surr=len(F), n_lisflood=len(R), csi=(i / u if u else None))


# ------------------------------------------------------------------ cell metrics
def cell_metrics(hp, hr, landm):
    o = {}
    for th in (0.30, 0.10):
        P = (hp >= th) & landm; R = (hr >= th) & landm; tp = int((P & R).sum()); fp = int((P & ~R).sum()); fn = int((~P & R).sum())
        o[f'tp{int(th * 100)}'], o[f'fp{int(th * 100)}'], o[f'fn{int(th * 100)}'] = tp, fp, fn
        o[f'csi{int(th * 100)}'] = tp / (tp + fp + fn) if tp + fp + fn else None
    wet = landm & ((hr >= 0.10) | (hp >= 0.10)); e = (hp - hr)[wet]
    o.update(n_wet=int(wet.sum()), abs_err_sum=float(np.abs(e).sum()), err_sum=float(e.sum()), mae=float(np.abs(e).mean()) if e.size else None,
             bias=float(e.mean()) if e.size else None)
    return o


def pool_cells(L):
    o = {}
    for th in ('30', '10'):
        tp, fp, fn = (sum(m[f'{k}{th}'] for m in L) for k in ('tp', 'fp', 'fn')); o[f'csi{th}'] = tp / (tp + fp + fn) if tp + fp + fn else None
    n = sum(m['n_wet'] for m in L); o.update(mae=sum(m['abs_err_sum'] for m in L) / n if n else None, bias=sum(m['err_sum'] for m in L) / n if n else None, scenes=len(L))
    return o


def pool_seg(L):
    i = sum(m['inter'] for m in L); u = sum(m['union'] for m in L); ns = sum(m['n_surr'] for m in L); nl = sum(m['n_lisflood'] for m in L)
    v = [m['csi'] for m in L if m['csi'] is not None]
    return dict(csi=i / u if u else None, count_ratio=ns / nl if nl else None, n_surr=ns, n_lisflood=nl, median_scene_csi=float(np.median(v)) if v else None, scenes=len(L))


# ------------------------------------------------------------------ labels: paired non-inferiority
def noninferiority(base, cand, storms, level, boot=2000, seed=0, alpha=0.05):
    """Surrogate minus LISFLOOD site recall at `level` ('rule' or a share '0.03'), box domain; paired two-stage bootstrap (storms, then
    sites in each storm, the same draws for both).  Storms without sites add nothing and are skipped."""
    B = {r['storm']: r for r in base}; C = {r['storm']: r for r in cand}; hb, hc, per = [], [], {}
    blk = (lambda X, s: X[s]['domains']['box']['rule']) if level == 'rule' else (lambda X, s: X[s]['domains']['box']['shares'][level])
    for s in storms:
        if s not in B or s not in C: continue
        sb = [x['id'] for x in B[s]['domains']['box']['sites']]; sc = [x['id'] for x in C[s]['domains']['box']['sites']]
        if sb != sc: raise SystemExit(f'{s}: site lists differ between LISFLOOD-FP and the surrogate (labels or matching changed)')
        if not sb: continue
        hb.append(np.asarray(blk(B, s)['_hits'], float)); hc.append(np.asarray(blk(C, s)['_hits'], float))
        per[s] = dict(sites=len(sb), lisflood=float(hb[-1].sum()), surrogate=float(hc[-1].sum()))
    N = sum(len(h) for h in hb)
    if not N: return dict(level=level, n_sites=0, delta=None, lower=None, upper=None, per_storm=per)
    d0 = (sum(h.sum() for h in hc) - sum(h.sum() for h in hb)) / N; rng = np.random.default_rng(seed); dd = []
    for _ in range(boot):
        sel = rng.integers(0, len(hb), len(hb)); a = b = n = 0.0
        for i in sel:
            j = rng.integers(0, len(hb[i]), len(hb[i])); a += hc[i][j].sum(); b += hb[i][j].sum(); n += len(j)
        dd.append((a - b) / n if n else 0.0)
    return dict(level=level, n_sites=int(N), storms=len(hb), recall_lisflood=float(sum(h.sum() for h in hb) / N), recall_surrogate=float(sum(h.sum() for h in hc) / N),
                delta=float(d0), lower=float(np.percentile(dd, 100 * alpha)), upper=float(np.percentile(dd, 100 * (1 - alpha))), per_storm=per)


def decide(R):
    """The pre-registered adoption rule (SURROGATE.md section 5) on the results dict."""
    A = ADOPT; c = {}; why = []
    seg = R.get('catalog', {}).get('segments_heldout23') or {}
    c['C1_segment_csi'] = seg.get('csi') is not None and seg['csi'] >= A['seg_csi_min']
    c['C2_count_ratio'] = seg.get('count_ratio') is not None and A['count_ratio'][0] <= seg['count_ratio'] <= A['count_ratio'][1]
    for lv in A['levels']:
        ni = (R.get('catalog', {}).get('labels', {}).get('noninferiority') or {}).get(lv) or {}
        c[f'C3_recall_{lv}'] = ni.get('delta') is not None and ni['delta'] >= A['d_recall_point_min'] and ni['lower'] >= A['d_recall_lower_min']
    ds = (R.get('district') or {}).get('d3_sep2023_p') or {}
    c['C4_district'] = ds.get('csi') is not None and ds['csi'] >= A['district_csi_min'] and ds.get('count_ratio') is not None and A['district_ratio'][0] <= ds['count_ratio'] <= A['district_ratio'][1]
    sp = R.get('speed') or {}
    c['C5_speed'] = bool(sp.get('district')) and sp.get('seconds') is not None and sp['seconds'] <= A['speed_s_max']
    for k, v in c.items():
        if not v: why.append(k)
    return dict(checks=c, adopt=all(c.values()), failed=why, rule=A)


# ------------------------------------------------------------------ evaluation
def scene_inputs(m): return DS.load_inputs(m['inputs'])


def eval_scene(net, ck, data, m, device):
    X = np.load(os.path.join(data, m['path'], 'x.npy'), mmap_mode='r'); h, pw = predict_grid(net, ck, X, device=device)
    y = np.load(os.path.join(data, m['path'], 'y.npy')).astype(np.float32) if m['has_target'] else None
    return h, pw, y


def evaluate(data, model_a, model_b, out, doc=None, repo=ROOT, device=None, threads=4, workers=4, boot=None, segments=None, k=1):
    import torch, score_v2 as SV
    from concurrent.futures import ThreadPoolExecutor
    device = device or ('cuda' if torch.cuda.is_available() else 'cpu'); boot = boot or ADOPT['boot']
    os.makedirs(out, exist_ok=True); I = json.load(open(os.path.join(data, 'index.json'))); S = I['scenes']
    R = dict(made=time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), git_sha=os.environ.get('GIT_SHA', ''), data=os.path.abspath(data), device=device,
             models=dict(A=os.path.abspath(model_a) if model_a else None, B=os.path.abspath(model_b)), splits=DS.count(S), adopt_rule=ADOPT,
             k=int(k), alpha=ADOPT['alpha'] / int(k))
    # 1. model A: generalisation (val, test_rain, test_box)
    if model_a and os.path.exists(model_a):
        netA, ckA = load_model(model_a, device); R['model_A'] = dict(step=ckA['step'], best=ckA.get('best'), n_params=ckA['n_params'], scenes=len(ckA['scenes']))
        for sp in ('val', 'test_rain', 'test_box'):
            L = [m for m in S if m['split'] == sp and m['has_target']]; cm, segl, jobs = [], [], []
            for m in L:
                h, _, y = eval_scene(netA, ckA, data, m, device); P = scene_inputs(m); cm.append(dict(cell_metrics(h, y, DS.land(P)), id=m['id']))
                if sp != 'val':
                    base = os.path.join(out, 'scenes', m['id'])
                    pseudo_run(os.path.join(base, 'surr_run'), P, h, f"{m['id']}_surr", 'forecast'); pseudo_run(os.path.join(base, 'lf_run'), P, y, f"{m['id']}_lf", 'forecast')
                    jobs.append((m['id'], base))
            def two(j):
                sid, base = j
                run_proto(os.path.join(base, 'surr_run'), os.path.join(base, 'surr_proto'), 'forecast', segments)
                run_proto(os.path.join(base, 'lf_run'), os.path.join(base, 'lf_proto'), 'forecast', segments)
                return dict(seg_csi(flagged(os.path.join(base, 'surr_proto')), flagged(os.path.join(base, 'lf_proto'))), id=sid)
            if jobs:
                with ThreadPoolExecutor(workers) as ex: segl = list(ex.map(two, jobs))
            R[f'A_{sp}'] = dict(cells=pool_cells(cm) if cm else None, segments=pool_seg(segl) if segl else None, per_scene=dict(cells=cm, segments=segl))
            log(f"model A {sp}: {R[f'A_{sp}']['cells']} {R[f'A_{sp}']['segments']}")
    # 2. model B: catalogue storms (held-out 23 + dev) against the published LISFLOOD-FP parity runs and the labels
    netB, ckB = load_model(model_b, device); R['model_B'] = dict(step=ckB['step'], n_params=ckB['n_params'], scenes=len(ckB['scenes']))
    p99 = ckB['norm'].get('volume_ratio_p99'); cat = [m for m in S if m['split'] == 'catalog']; cm = {}; sg = {}; base_runs, cand_runs = [], []; plaus = {}
    cand_root = os.path.join(out, 'catalog')
    for m in cat:
        h, _, y = eval_scene(netB, ckB, data, m, device); P = scene_inputs(m); storm = m['storm']; ref = os.path.join(repo, m['ref'])
        if y is not None: cm[m['id']] = dict(cell_metrics(h, y, DS.land(P)), role=m['role'])
        rat = DS.volume_ratio(h, P, m['stats']['excess_volume_m3']); plaus[m['id']] = dict(volume_ratio=rat, p99_train=p99, flag=bool(p99 and rat and rat > p99))
        run_d = pseudo_run(os.path.join(out, 'runs', m['id']), P, h, m['id'], storm); cd = os.path.join(cand_root, m['id'])
        run_proto(run_d, cd, storm, full=True)
        rm = os.path.join(ref, f'matches_{storm}.json')
        if os.path.exists(rm): shutil.copy(rm, os.path.join(cd, f'matches_{storm}.json'))       # the published label matches: identical site lists
        json.dump(json.load(open(os.path.join(run_d, 'meta.json'))), open(os.path.join(cd, 'flood_meta.json'), 'w'))
        sg[m['id']] = dict(seg_csi(flagged(cd), flagged(ref)), role=m['role'], storm=storm)
        if os.path.exists(os.path.join(ref, 'flood_meta.json')):
            rb = SV.score_run(SV.load_run(ref, storm)); rc = SV.score_run(SV.load_run(cd, storm))
            rb.update(group='parity', primary=True); rc.update(group='surrogate', primary=True); base_runs.append(rb); cand_runs.append(rc)
        log(f"{m['id']}: cells {cm.get(m['id'], {}).get('csi30')}, segments {sg[m['id']]}, ratio {rat}")
    ho = [k for k, v in sg.items() if v['role'] == 'heldout23']; dv = [k for k, v in sg.items() if v['role'] == 'dev']
    C = dict(cells_heldout23=pool_cells([cm[k] for k in ho if k in cm]) if ho else None, cells_dev=pool_cells([cm[k] for k in dv if k in cm]) if dv else None,
             segments_heldout23=pool_seg([sg[k] for k in ho]) if ho else None, segments_dev=pool_seg([sg[k] for k in dv]) if dv else None,
             per_storm=dict(cells=cm, segments=sg), plausibility=dict(flagged=[k for k, v in plaus.items() if v['flag']], per_storm=plaus))
    held = [s for s in SV.HELDOUT + SV.NEW16]
    if base_runs:
        C['labels'] = dict(noninferiority={lv: noninferiority(base_runs, cand_runs, held, lv, boot, alpha=ADOPT['alpha'] / int(k)) for lv in ADOPT['levels']},
                           pooled=dict(lisflood=SV.pooled([r for r in base_runs if r['storm'] in held], 'box', boot), surrogate=SV.pooled([r for r in cand_runs if r['storm'] in held], 'box', boot)),
                           dev=dict(lisflood=SV.pooled([r for r in base_runs if r['storm'] in SV.DEV], 'box', boot), surrogate=SV.pooled([r for r in cand_runs if r['storm'] in SV.DEV], 'box', boot)))
        json.dump(dict(made_by='proto/surrogate/evaluate.py', runs=base_runs), open(os.path.join(out, 'score_lisflood.json'), 'w'), indent=0)
        json.dump(dict(made_by='proto/surrogate/evaluate.py', runs=cand_runs), open(os.path.join(out, 'score_surrogate.json'), 'w'), indent=0)
    R['catalog'] = C
    # 3. District 3 (domain the forecast needs) and 4. speed on 4 CPU threads
    R['district'] = {}
    for m in [m for m in S if m['split'] == 'district']:
        P = scene_inputs(m); X = np.load(os.path.join(data, m['path'], 'x.npy'), mmap_mode='r'); h, _ = predict_grid(netB, ckB, X, device=device)
        run_d = pseudo_run(os.path.join(out, 'runs', m['id']), P, h, m['id'], 'sep2023' if m['role'] == 'district' else 'forecast')
        pd_ = run_proto(run_d, os.path.join(out, 'district', m['id']), 'sep2023' if m['role'] == 'district' else 'forecast'); ref = os.path.join(repo, m['ref'])
        o = dict(role=m['role'], n_surr=len(flagged(pd_)))
        if os.path.exists(os.path.join(ref, 'segments.geojson')): o.update(seg_csi(flagged(pd_), flagged(ref))); o['count_ratio'] = o['n_surr'] / o['n_lisflood'] if o['n_lisflood'] else None
        elif os.path.exists(os.path.join(ref, 'summary.json')): o['n_lisflood'] = json.load(open(os.path.join(ref, 'summary.json'))).get('segments_p_ge_50'); o['count_ratio'] = o['n_surr'] / o['n_lisflood'] if o['n_lisflood'] else None
        if m['has_target']:
            y = np.load(os.path.join(data, m['path'], 'y.npy')).astype(np.float32); o['cells'] = cell_metrics(h, y, DS.land(P))
        R['district'][m['id']] = o; log(f"district {m['id']}: {o}")
    R['speed'] = speed(model_b, [m for m in S if m['split'] == 'district'] or cat, threads)
    R['decision'] = decide(R)
    json.dump(R, open(os.path.join(out, 'results.json'), 'w'), indent=1, default=float)
    md = results_md(R); open(os.path.join(out, 'RESULTS.md'), 'w').write(md)
    if doc:
        sfx = '' if int(k) == 1 else f'_k{int(k)}'     # a second evaluation (after batch 2) never overwrites the first
        os.makedirs(doc, exist_ok=True); open(os.path.join(doc, f'RESULTS{sfx}.md'), 'w').write(md)
        json.dump({k: v for k, v in R.items() if k not in ('catalog',)} | dict(catalog={k: v for k, v in C.items() if k != 'labels'} | dict(labels=dict(noninferiority=(C.get('labels') or {}).get('noninferiority')))),
                  open(os.path.join(doc, f'results{sfx}.json'), 'w'), indent=1, default=float)
    log(f"decision: adopt {R['decision']['adopt']}, failed {R['decision']['failed']}")
    return R


def speed(model, items, threads):
    """Wall seconds from surr_inputs.npz to peak depth on `threads` CPU threads (features + network), on the District 3 inputs when present."""
    import torch
    if not items: return dict(seconds=None, district=False)
    m = max(items, key=lambda m: m['shape'][0] * m['shape'][1]); old = torch.get_num_threads(); t0 = time.time()
    net, ck = load_model(model, 'cpu', threads); P = DS.load_inputs(m['inputs']); X, _ = DS.features(P); h, _ = predict_grid(net, ck, X, device='cpu')
    s = time.time() - t0; torch.set_num_threads(old)
    return dict(seconds=round(s, 1), threads=threads, scene=m['id'], cells=int(m['shape'][0] * m['shape'][1]), district=m['split'] == 'district')


def fmt(v, nd=3):
    return '–' if v is None else (f'{v:.{nd}f}' if isinstance(v, float) else str(v))


def results_md(R):
    D = R['decision']; C = R.get('catalog', {}); L = [f"# LISFLOOD-FP surrogate: results ({R['made']})", '',
         f"Pre-registration: `SURROGATE.md` (fixed before training). Data `{R['data']}`; scenes per split {R['splits']}; evaluation k = {R.get('k', 1)} (alpha {R.get('alpha', 0.05):g}).", '',
         f"**Decision: {'ADOPTED as the district-wide / ensemble layer only' if D['adopt'] else 'NOT adopted'}.**" + ('' if D['adopt'] else f" Failed: {', '.join(D['failed'])}."), '',
         '## Adoption checks (model B)', '', '| check | result |', '|---|---|']
    for k, v in D['checks'].items(): L.append(f'| {k} | {"pass" if v else "FAIL"} |')
    seg = C.get('segments_heldout23') or {}; cel = C.get('cells_heldout23') or {}
    L += ['', '## Against LISFLOOD-FP on the catalogue storms (model B; rain never trained on)', '',
          '| pool | segment CSI | count ratio (surrogate / LISFLOOD) | median storm CSI | cell CSI 0.30 m | cell CSI 0.10 m | depth MAE wet (m) | bias (m) |', '|---|---|---|---|---|---|---|---|']
    for nm, s_, c_ in (('held-out 23', seg, cel), ('dev (sep2023, aug2021)', C.get('segments_dev') or {}, C.get('cells_dev') or {})):
        L.append(f"| {nm} | {fmt(s_.get('csi'))} | {fmt(s_.get('count_ratio'), 2)} | {fmt(s_.get('median_scene_csi'))} | {fmt(c_.get('csi30'))} | {fmt(c_.get('csi10'))} | {fmt(c_.get('mae'))} | {fmt(c_.get('bias'))} |")
    ni = (C.get('labels') or {}).get('noninferiority') or {}
    L += ['', '## Labels: site recall, held-out 23 (surrogate minus LISFLOOD-FP radar runs)', '', '| level | sites | LISFLOOD | surrogate | difference | 90 % interval |', '|---|---|---|---|---|---|']
    for lv, v in ni.items():
        L.append(f"| {lv} | {v.get('n_sites')} | {fmt(v.get('recall_lisflood'))} | {fmt(v.get('recall_surrogate'))} | {fmt(v.get('delta'))} | [{fmt(v.get('lower'))}, {fmt(v.get('upper'))}] |")
    L += ['', '## District 3', '']
    for k, v in (R.get('district') or {}).items():
        L.append(f"- `{k}` ({v.get('role')}): surrogate flags {v.get('n_surr')}, LISFLOOD-FP {v.get('n_lisflood')}, ratio {fmt(v.get('count_ratio'), 2)}, segment CSI {fmt(v.get('csi'))}.")
    sp = R.get('speed') or {}
    L += [f"- Speed: {fmt(sp.get('seconds'), 1)} s on {sp.get('threads')} CPU threads for `{sp.get('scene')}` ({sp.get('cells')} cells; District 3 inputs: {sp.get('district')})."]
    L += ['', '## Generalisation (model A, trained on the train split only)', '', '| set | cell CSI 0.30 | depth MAE (m) | segment CSI | count ratio | scenes |', '|---|---|---|---|---|---|']
    for sp_ in ('val', 'test_rain', 'test_box'):
        v = R.get(f'A_{sp_}') or {}; c_ = v.get('cells') or {}; s_ = v.get('segments') or {}
        L.append(f"| {sp_} | {fmt(c_.get('csi30'))} | {fmt(c_.get('mae'))} | {fmt(s_.get('csi'))} | {fmt(s_.get('count_ratio'), 2)} | {c_.get('scenes', 0)} |")
    pl = (C.get('plausibility') or {}).get('flagged') or []
    L += ['', f"Plausibility (peak-depth volume / excess volume above the training 99th percentile): {len(pl)} catalogue storm(s) flagged {pl}.", '',
          'What this means: the surrogate may only replace LISFLOOD-FP where every check passes, and only for the district-wide ensemble map. '
          'The box runs, the archive and the forward test stay on the physics.']
    return '\n'.join(L) + '\n'


# ------------------------------------------------------------------ predict (use)
def cmd_predict(a):
    t0 = time.time(); net, ck = load_model(a.model, a.device or 'cpu', a.threads); P = DS.load_inputs(a.inputs); t1 = time.time()
    X, st = DS.features(P); t2 = time.time(); h, pw = predict_grid(net, ck, X, device=a.device or 'cpu'); t3 = time.time()
    name = a.name or os.path.basename(os.path.normpath(a.out)); run_d = pseudo_run(os.path.join(a.out, 'run'), P, h, name, a.storm)
    np.save(os.path.join(run_d, 'pwet30.npy'), pw.astype(np.float16))
    p99 = ck['norm'].get('volume_ratio_p99'); rat = DS.volume_ratio(h, P, st['excess_volume_m3'])
    rep = dict(inputs=os.path.abspath(a.inputs), model=os.path.abspath(a.model), model_step=ck['step'], shape=list(h.shape), seconds=dict(load=round(t1 - t0, 1), features=round(t2 - t1, 1), network=round(t3 - t2, 1)),
               threads=a.threads, rain_max_mm=st['rain_max_mm'], wet30_km2=round(float(((h >= 0.30) & DS.land(P)).sum() * float(P['meta']['res_m']) ** 2 / 1e6), 2),
               volume_ratio=rat, volume_ratio_p99_train=p99, plausibility_flag=bool(p99 and rat and rat > p99))
    if not a.no_proto:
        pd_ = run_proto(run_d, os.path.join(a.out, 'proto'), a.storm, a.segments); rep['segments_p_ge_50'] = len(flagged(pd_)); rep['seconds']['prototype'] = round(time.time() - t3, 1)
    json.dump(rep, open(os.path.join(a.out, 'predict.json'), 'w'), indent=1); print(json.dumps(rep, indent=1))
    return rep


# ------------------------------------------------------------------ selftest
def synth_segments(path, box, n_rows=(20, 48, 70), res=20.0):
    """Three horizontal road segments across a synthetic box (prototype.py selftest layout)."""
    from pyproj import Transformer
    tr = Transformer.from_crs(26986, 4326, always_xy=True); geo = []
    for y in n_rows:
        lo, la = tr.transform([box[0] + 100, box[2] - 100], [box[3] - y * res, box[3] - y * res])
        a = [int(round(v * 1e5)) for v in (lo[0], la[0])]; b = [int(round(v * 1e5)) for v in (lo[1], la[1])]; geo.append([[a[0], a[1], b[0] - a[0], b[1] - a[1]]])
    n = len(geo); json.dump(dict(n=n, geo=geo, props=dict(road=[f'R{i} St' for i in range(n)], town=['T'] * n, cls=[0] * n, low=[0] * n, len=[2000] * n, aadt=[1000] * n),
                                 links=[[i, i + 1] for i in range(n - 1)]), open(path, 'w'))
    return path


def selftest():
    import tempfile, train as TR
    ok = []
    hp = np.array([[0.5, 0.0], [0.35, 0.2]], np.float32); hr = np.array([[0.4, 0.31], [0.0, 0.2]], np.float32); lm = np.ones((2, 2), bool)
    c = cell_metrics(hp, hr, lm); assert c['tp30'] == 1 and c['fp30'] == 1 and c['fn30'] == 1 and abs(c['csi30'] - 1 / 3) < 1e-9 and c['n_wet'] == 4
    assert abs(pool_cells([c, c])['csi30'] - 1 / 3) < 1e-9 and seg_csi({1, 2, 3}, {2, 3, 4})['csi'] == 0.5 and pool_seg([seg_csi({1}, {1, 2}), seg_csi({5}, {5})])['csi'] == 2 / 3
    ok.append('cell CSI / MAE and segment CSI, pooled as sums')
    mk = lambda s, hits, sid: dict(storm=s, domains=dict(box=dict(sites=[dict(id=f'{s}{i}') for i in range(len(hits))], rule=dict(_hits=hits), shares={'0.03': dict(_hits=hits)})))
    base = [mk('jul2023', [1, 0, 0, 1], 0), mk('sep2021', [1, 1, 0], 0), mk('aug2023', [], 0)]; same = [mk('jul2023', [1, 0, 0, 1], 0), mk('sep2021', [1, 1, 0], 0), mk('aug2023', [], 0)]
    worse = [mk('jul2023', [0, 0, 0, 0], 0), mk('sep2021', [1, 0, 0], 0), mk('aug2023', [], 0)]
    n0 = noninferiority(base, same, ['jul2023', 'sep2021', 'aug2023'], 'rule', 300); n1 = noninferiority(base, worse, ['jul2023', 'sep2021', 'aug2023'], '0.03', 300)
    assert n0['delta'] == 0 and n0['lower'] == 0 and n0['n_sites'] == 7 and n1['delta'] < -0.4 and n1['lower'] < n1['delta'] <= n1['upper'] <= 0
    try: noninferiority(base, [mk('jul2023', [1, 0, 0], 0)], ['jul2023'], 'rule', 10); raise AssertionError('site lists must match')
    except SystemExit: pass
    R0 = dict(catalog=dict(segments_heldout23=dict(csi=0.75, count_ratio=1.1), labels=dict(noninferiority={'rule': n0, '0.03': dict(n0, delta=-0.01, lower=-0.04)})),
              district={'d3_sep2023_p': dict(csi=0.65, count_ratio=0.9)}, speed=dict(seconds=120.0, district=True))
    assert decide(R0)['adopt']
    for path, v in ((('catalog', 'segments_heldout23', 'csi'), 0.69), (('catalog', 'segments_heldout23', 'count_ratio'), 1.3), (('district', 'd3_sep2023_p', 'csi'), 0.5), (('speed', 'seconds'), 400.0)):
        R1 = json.loads(json.dumps(R0)); d = R1
        for p in path[:-1]: d = d[p]
        d[path[-1]] = v; assert not decide(R1)['adopt'], path
    R1 = json.loads(json.dumps(R0)); R1['catalog']['labels']['noninferiority']['0.03']['lower'] = -0.06; assert decide(R1)['failed'] == ['C3_recall_0.03']
    ok.append('paired non-inferiority bootstrap (site lists must match) and every adoption condition')
    # end to end on synthetic scenes with the real road graph: dataset -> 2-step models -> evaluation -> RESULTS.md; predict with a synthetic road file
    d = tempfile.mkdtemp(prefix='surr_ev_'); root = os.path.join(d, 'root'); pp, ip, repo = DS.synth_root(root, n_train=4, n_val=1, n_test=2, ny=96, nx=128)
    data = os.path.join(root, 'ds'); idx, _ = DS.build(root, [pp], ip, data, repo=repo)
    cfg = dict(base=8, depth=3, patch=64, batch=2, val_every=1)
    TR.train(data, 'A', os.path.join(d, 'A.pt'), cfg, iters=2, device='cpu', log_every=10); TR.train(data, 'B', os.path.join(d, 'B.pt'), cfg, iters=2, device='cpu', log_every=10)
    net, ck = load_model(os.path.join(d, 'B.pt')); m = idx[0]; X = np.load(os.path.join(data, m['path'], 'x.npy'), mmap_mode='r')
    h1, p1 = predict_grid(net, ck, X, tile=64, overlap=16); h2, _ = predict_grid(net, ck, X, tile=128, overlap=0)
    assert h1.shape == (96, 128) and np.isfinite(h1).all() and (h1 >= 0).all() and ((p1 >= 0) & (p1 <= 1)).all() and h2.shape == h1.shape
    ok.append('tiled prediction (overlapping tiles, blended seams, sea cells zero)')
    segs = synth_segments(os.path.join(d, 'segs.json'), idx[0]['box'])
    cat = [x for x in idx if x['split'] == 'catalog'][0]; P = DS.load_inputs(cat['inputs']); refd = os.path.join(repo, cat['ref'])
    y = np.load(os.path.join(data, cat['path'], 'y.npy')).astype(np.float32)
    lfr = pseudo_run(os.path.join(d, 'ref_run'), P, y, cat['id'], 'jul2023'); run_proto(lfr, refd, 'jul2023', full=True)
    json.dump(json.load(open(os.path.join(lfr, 'meta.json'))), open(os.path.join(refd, 'flood_meta.json'), 'w'))
    assert os.path.exists(os.path.join(refd, 'features_jul2023.csv')) and os.path.exists(os.path.join(refd, 'matches_jul2023.json'))
    R = evaluate(data, os.path.join(d, 'A.pt'), os.path.join(d, 'B.pt'), os.path.join(d, 'eval'), os.path.join(d, 'doc'), repo=repo, device='cpu', boot=50, segments=segs)
    assert os.path.exists(os.path.join(d, 'doc', 'RESULTS.md')) and os.path.exists(os.path.join(d, 'doc', 'results.json'))
    assert R['A_test_box']['cells']['scenes'] == 2 and R['A_test_box']['segments']['scenes'] == 2 and R['catalog']['segments_heldout23']['scenes'] == 1
    assert R['decision']['adopt'] is False and 'C4_district' in R['decision']['failed'] and 'C5_speed' in R['decision']['failed']     # no District 3 inputs here
    assert R['speed']['seconds'] is not None and R['speed']['district'] is False
    ok.append(f"evaluate end to end (model A val/test, model B catalogue via prototype + closure_ml + score_v2, decision {R['decision']['failed']})")
    rep = cmd_predict(argparse.Namespace(inputs=cat['inputs'], model=os.path.join(d, 'B.pt'), out=os.path.join(d, 'pred'), storm='forecast', name='selftest_pred',
                                         threads=2, device='cpu', no_proto=False, segments=segs))
    g = json.load(open(os.path.join(d, 'pred', 'proto', 'segments.geojson'))); assert g['type'] == 'FeatureCollection' and 'segments_p_ge_50' in rep
    assert os.path.exists(os.path.join(d, 'pred', 'run', 'hmax.npy')) and rep['seconds']['network'] >= 0
    ok.append('predict: inputs -> run dir (hmax.npy ...) -> prototype segments.geojson')
    for o in ok: print('ok  ', o)
    print(f'EVALUATE SELFTEST PASSED ({len(ok)} checks)'); return True


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); sp = ap.add_subparsers(dest='cmd')
    p = sp.add_parser('eval'); p.add_argument('--data', required=True); p.add_argument('--model-a'); p.add_argument('--model-b', required=True)
    p.add_argument('--out', required=True); p.add_argument('--doc'); p.add_argument('--repo', default=ROOT); p.add_argument('--device'); p.add_argument('--threads', type=int, default=ADOPT['speed_threads'])
    p.add_argument('--workers', type=int, default=4); p.add_argument('--boot', type=int)
    p.add_argument('--k', type=int, default=1, help='number of surrogate evaluations scored on the held-out 23 under SURROGATE.md (alpha / k): 1, or 2 after batch 2')
    p = sp.add_parser('predict'); p.add_argument('--inputs', required=True); p.add_argument('--model', required=True); p.add_argument('--out', required=True)
    p.add_argument('--storm', default='forecast'); p.add_argument('--name'); p.add_argument('--threads', type=int, default=4); p.add_argument('--device')
    p.add_argument('--no-proto', action='store_true'); p.add_argument('--segments')
    p = sp.add_parser('_extract'); p.add_argument('--run-dir', required=True); p.add_argument('--storm', required=True); p.add_argument('--out', required=True)
    sp.add_parser('selftest')
    a = ap.parse_args()
    if a.cmd == 'selftest': sys.exit(0 if selftest() else 1)
    if a.cmd == 'eval': evaluate(a.data, a.model_a, a.model_b, a.out, a.doc, a.repo, a.device, a.threads, a.workers, a.boot, k=a.k); return
    if a.cmd == 'predict': cmd_predict(a); return
    if a.cmd == '_extract': cmd_extract(a); return
    ap.print_help()


if __name__ == '__main__':
    main()
