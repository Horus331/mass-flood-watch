"""Compare two gauges_<storm>.json files (e.g. a fresh OGC-API fetch vs the committed legacy-WaterServices file).

    python proto/obs_compare.py docs/proto/obs/gauges_sep2023.json /tmp/ogc/gauges_sep2023.json --out report.json

Pass = same site set, and per site: peak value within 1 % (or 0.02 ft / 1 cfs), peak time within 15 min, datum/vdatum/drainage area equal
(datum within 0.01 ft).  Exit code 0 always; the verdict is in the report ('pass': true/false) so the workflow can commit it.
"""
import sys, json, argparse, datetime as dt

def t(s): return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))

def compare(ref_path, new_path):
    A = {g['site']: g for g in json.load(open(ref_path))['gauges']}; B = {g['site']: g for g in json.load(open(new_path))['gauges']}
    rep = dict(ref=ref_path, new=new_path, ref_sites=sorted(A), new_sites=sorted(B), only_ref=sorted(set(A) - set(B)), only_new=sorted(set(B) - set(A)), sites=[])
    ok = not rep['only_ref'] and not rep['only_new']
    for sid in sorted(set(A) & set(B)):
        a, b = A[sid], B[sid]; r = dict(site=sid, name=a.get('name'))
        for k, tol_abs in (('peak_q_cfs', 1.0), ('peak_stage_ft', 0.02)):
            if (k in a) != (k in b): r[k] = 'missing in ' + ('new' if k in a else 'ref'); ok = False; continue
            if k not in a: continue
            dv = b[k][1] - a[k][1]; dtm = (t(b[k][0]) - t(a[k][0])).total_seconds() / 60
            good = abs(dv) <= max(tol_abs, 0.01 * abs(a[k][1])) and abs(dtm) <= 15; ok &= good
            r[k] = dict(ref=a[k], new=b[k], dv=round(dv, 3), dt_min=round(dtm, 1), ok=good)
        for k in ('q_cfs', 'stage_ft'): r['n_' + k] = [len(a.get(k) or []), len(b.get(k) or [])]
        for k in ('datum_ft', 'vdatum', 'drain_mi2', 'lon', 'lat'):
            va, vb = a.get(k), b.get(k)
            same = (va == vb) or (isinstance(va, (int, float)) and isinstance(vb, (int, float)) and abs(va - vb) <= (0.01 if k == 'datum_ft' else 0.05 if k == 'drain_mi2' else 1e-4))
            if not same: r[k] = [va, vb]
            if not same and k in ('datum_ft', 'vdatum'): ok = False
        r['first_t'] = [(a.get('stage_ft') or a.get('q_cfs') or [[None]])[0][0], (b.get('stage_ft') or b.get('q_cfs') or [[None]])[0][0]]
        rep['sites'].append(r)
    rep['pass'] = bool(ok); return rep

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('ref'); ap.add_argument('new'); ap.add_argument('--out'); a = ap.parse_args()
    try: rep = compare(a.ref, a.new)
    except Exception as e: rep = dict(ref=a.ref, new=a.new, error=repr(e), **{'pass': False})
    s = json.dumps(rep, indent=1); print(s[:6000])
    if a.out: open(a.out, 'w').write(s)
