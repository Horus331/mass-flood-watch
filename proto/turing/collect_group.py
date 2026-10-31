"""Score finished run_storm results of one group and write SMALL json summaries for the repo (queue kind collect_group;
proto/turing/collect_group.slurm; first used by docs/proto/runoff/NWM_AMC_PREREG.md).

    python proto/turing/collect_group.py --group amcnwm --dest docs/proto/runoff/nwm_amc/runs [--force]

For every folder results/<group>_<arm>_<storm>/ that run_storm.slurm left with flood_meta.json + segments.geojson (prototype.py output):
  <dest>/<name>.score_v2.json   proto/score_v2.py score_run on a private copy of flood_meta.json + segments.geojson ONLY, so the segment
                                universe is segments.geojson and labels are matched by score_v2's own strict 30 m rule.  (features_<storm>.csv
                                and matches_<storm>.json in results/ are deliberately not used: run_storm writes them through the shared
                                docs/proto/ml/ path, which concurrent jobs on the same storm can overwrite.)  Same for every arm -> paired.
  <dest>/<name>.gauges.json     results/<name>/score.json (proto/score.py, USGS stage rise / timing), copied when present and < 1 MB.
  <dest>/<name>.meta.json       t0, box, hours, solver, git sha, LF_* env (incl. LF_CN_AMC_RESOLVED), rain totals, runtime.
Nothing else is written; names and paths are checked against strict patterns; a name already in <dest> is skipped unless --force.
"""
import os, re, sys, json, glob, shutil, argparse, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
GROUP_RE = re.compile(r'^[a-z0-9]{3,20}$'); DEST_RE = re.compile(r'^docs/proto/[a-z0-9_]+(/[a-z0-9_]+){0,4}$')
NAME_RE = re.compile(r'^[a-z0-9]{3,20}_[a-z0-9]{1,12}_[a-z]{3}20[0-9]{2}[a-z]?$')
MAX_BYTES = 1_000_000


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--group', required=True); ap.add_argument('--dest', required=True)
    ap.add_argument('--force', action='store_true'); a = ap.parse_args()
    if not GROUP_RE.match(a.group) or not DEST_RE.match(a.dest) or '..' in a.dest: raise SystemExit('bad --group / --dest')
    sys.path.insert(0, os.path.join(REPO, 'proto')); import score_v2 as SV
    dest = os.path.join(REPO, a.dest); os.makedirs(dest, exist_ok=True); done = []
    for d in sorted(glob.glob(os.path.join(REPO, 'results', a.group + '_*'))):
        name = os.path.basename(d)
        if not NAME_RE.match(name): print('skip (name pattern)', name); continue
        if not (os.path.exists(os.path.join(d, 'flood_meta.json')) and os.path.exists(os.path.join(d, 'segments.geojson'))): print('skip (incomplete)', name); continue
        out = os.path.join(dest, name + '.score_v2.json')
        if os.path.exists(out) and not a.force: print('skip (collected)', name); continue
        storm = SV.storm_of(name)
        if not storm or storm in SV.LOCKED: print('skip (storm)', name, storm); continue
        tmp = tempfile.mkdtemp()
        try:
            for f in ('flood_meta.json', 'segments.geojson'): shutil.copy(os.path.join(d, f), tmp)
            r = SV.score_run(SV.load_run(tmp, storm)); r['primary'] = True; r['run'] = name
        except Exception as e:
            print('score failed', name, repr(e)[:200]); continue
        finally: shutil.rmtree(tmp, ignore_errors=True)
        s = json.dumps(r)
        if len(s) > MAX_BYTES: print('too big', name, len(s)); continue
        open(out, 'w').write(s)
        g = os.path.join(d, 'score.json')
        if os.path.exists(g) and os.path.getsize(g) < MAX_BYTES:
            json.dump(json.load(open(g)), open(os.path.join(dest, name + '.gauges.json'), 'w'))
        m = json.load(open(os.path.join(d, 'flood_meta.json'))); inp = m.get('inputs') or {}
        meta = dict(name=name, storm=storm, t0=m.get('t0'), box=m.get('box'), res_m=m.get('res_m'), solver=m.get('solver'), git_sha=m.get('git_sha'),
                    env=inp.get('env'), infiltration=inp.get('infiltration'), rain_total_mean_mm=m.get('rain_total_mean_mm'),
                    rain_total_max_mm=m.get('rain_total_max_mm'), rain_missing_hours=m.get('rain_missing_hours'), runtime_s=m.get('runtime_s'),
                    peak_wet_km2=m.get('peak_wet_km2'))
        json.dump(meta, open(os.path.join(dest, name + '.meta.json'), 'w'), indent=1)
        b = r['domains']['box']; done.append(name)
        print(f"{name}: sites {b['n_sites']} hits@3% {b['shares']['0.03']['site_hits']} rule {b['rule']['site_hits']}")
    print('collected', len(done), done)


if __name__ == '__main__':
    main()
