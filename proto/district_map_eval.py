"""Whole-District 3 forecast map test (docs/proto/forecast/DISTRICT_MAP_PREREG.md, frozen 3db11469c). Written before any district run exists.

    python proto/district_map_eval.py jobs --cand vp            # the Turing queue requests (radar reference + candidate (b), solve + post)
    python proto/district_map_eval.py score --cand vp           # -> docs/proto/forecast/district_map_<cand>.json + DISTRICT_MAP_<CAND>.md
    python proto/district_map_eval.py selftest

Runs (proto/turing/run_storm.slurm, SEGDUMP=1, published slim to docs/proto/turing/dm_<storm>_<ref|cand>/seg.json):
  ref   = the District 3 domain on the storm's observed MRMS radar rain (storm window of w9 STORMS), flagged = P >= 0.5;
  vp    = candidate (b): the short-lead issue cycle of ENSEMBLE.md, live settings (20,90 spreading) with each hour's field rescaled to the
          raw HRRR total over the domain (LF_HRRR_VOLPRES=1), P >= 0.5.
Both with the live District 3 Turing settings (forecast_d3.slurm): 20 m, CN x 0.88 AMC II, LF_PARITY=1, 2 mm/h, LF_QOUT=1, T2 terrain.
Measures (prereg): ratio_n pooled over the 7 out-of-sample storms; site recall of the 29 out-of-sample sites (the strict sites of the
ENSEMBLE.md short-lead box runs, matched district-wide); lift = recall / share of District 3 segments flagged; CSI vs the radar run.
Pass: 0.7 <= ratio_n <= 1.5, recall >= 0.276, lift >= 2. sep2023 and aug2021 are run and reported only (development storms).
"""
import argparse
import datetime as dt
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, '..')); sys.path.insert(0, HERE)
TUR = os.path.join(ROOT, 'docs', 'proto', 'turing'); FC = os.path.join(ROOT, 'docs', 'proto', 'forecast')
BOX = '128000,856000,206000,946000'
OOS = ['jul2021', 'sep2021', 'sep2022', 'jul2023', 'aug2023', 'aug2023b', 'aug2026']
DEV = ['sep2023', 'aug2021']
SHORT = {'sep2023': 'sep2023_18z', 'aug2021': 'aug2021_12z', **{s: f'{s}_short' for s in OOS}}
REF_HOURS = {'sep2023': 36, 'aug2021': 18, 'jul2021': 18, 'sep2021': 24, 'sep2022': 18, 'jul2023': 18, 'aug2023': 18, 'aug2023b': 18, 'aug2026': 18}
BOX_RECALL, N_SITES = 0.276, 29
LIVE = dict(BOX=BOX, RES='20', LF_LOSS='cn', LF_CN_AMC='II', LF_CN_SCALE='0.88', LF_PARITY='1', LF_INFIL_MMH='2', LF_QOUT='1', LF_NOTCH_FIX='1',
            LF_CHAN_ENFORCE='1', PROTO_RES_CONSISTENT='1', PROTO_RC_START_H='rain', SEGDUMP='1')
CANDS = {'vp': dict(LF_HRRR_NBHD='20,90', LF_HRRR_VOLPRES='1'), 'a': dict(LF_HRRR_NBHD='20,90')}
K_OF_8 = 2   # candidate (a): likely = at least 2 of the 8 member runs at P >= 0.5 (the box rule)


def mtag(init): return ts(init.replace('Z', '')).strftime('m%d%Hz')


def ts(s): return dt.datetime.strptime(s.replace('Z', ''), '%Y-%m-%dT%H' if len(s.replace('Z', '')) == 13 else '%Y-%m-%dT%H:%M')


def jobs(cand):
    import forecast_ens as F
    out = []
    for s in DEV + OOS:
        E = F.ENSEMBLES[SHORT[s]]; hrs = int((ts(E['end']) - ts(E['issue'])).total_seconds() // 3600)
        runs = [(f'dm_{s}_ref', dict(STORM=s, HOURS=str(REF_HOURS[s])))]
        if cand == 'a':   # one district run per ensemble member, each from its own HRRR cycle to the ensemble end
            for m in E['members']:
                mh = int((ts(E['end']) - ts(m)).total_seconds() // 3600)
                runs.append((f'dm_{s}_a_{mtag(m)}', dict(STORM=s, HOURS=str(mh), LF_RAIN='hrrr', LF_HRRR_INIT=m, LF_ALLOW_DRY='1', **CANDS[cand])))
        else:
            runs.append((f'dm_{s}_{cand}', dict(STORM=s, HOURS=str(hrs), LF_RAIN='hrrr', LF_HRRR_INIT=E['issue'], LF_ALLOW_DRY='1', **CANDS[cand])))
        for name, env in runs:
            if cand != 'vp' and name.endswith('_ref'): continue   # the radar references were run with (b)
            e = dict(LIVE, NAME=name, **env)
            out.append(dict(id=f'{name}_solve', kind='run_storm', env=dict(e, STAGE='solve'),
                            sbatch=dict(partition='short', gres='gpu:1', constraint='A100|H100|H200', time='04:00:00', mem='160G')))
            out.append(dict(id=f'{name}_post', kind='run_storm', env=dict(e, STAGE='post'), after=[f'{name}_solve'],
                            sbatch=dict(partition='short', time='06:00:00', mem='160G')))
    return out


def load(name):
    p = os.path.join(TUR, name, 'seg.json')
    if not os.path.exists(p): return None
    D = json.load(open(p)); P = np.zeros(D['n_segments'], np.float32); inb = np.zeros(D['n_segments'], bool)
    P[D['inbox']] = D['p_depth']; inb[D['inbox']] = True
    return D, P >= 0.5, inb


def load_cand(s, cand):
    if cand != 'a': return load(f'dm_{s}_{cand}')
    import forecast_ens as F
    M = [load(f'dm_{s}_a_{mtag(m)}') for m in F.ENSEMBLES[SHORT[s]]['members']]
    if any(x is None for x in M): return None
    for x in M[1:]: assert (x[2] == M[0][2]).all(), 'members disagree on the domain'
    k = np.sum([x[1] for x in M], axis=0)
    return M[0][0], k >= K_OF_8, M[0][2]


def oos_sites(storm):
    """The strict sites of the ENSEMBLE.md short-lead box run (issue cycle): label id -> None (the 29 sites)."""
    import forecast_ens as F
    E = F.ENSEMBLES[SHORT[storm]]; d = os.path.join(FC, 'ensemble', F.member_name(SHORT[storm], E['issue']), 'seg.json')
    return [m['id'] for m in json.load(open(d))['strict']] if os.path.exists(d) else None


def score(cand):
    rows, pool = [], dict(F=0, R=0, inter=0, union=0, hits=0, sites=0, flagged=0, inb=0)
    for s in DEV + OOS:
        r = dict(storm=s, role='development (reported only)' if s in DEV else 'out-of-sample')
        A, B = load_cand(s, cand), load(f'dm_{s}_ref')
        if A is None or B is None: r['status'] = 'missing ' + ', '.join(n for n, x in ((cand, A), ('ref', B)) if x is None); rows.append(r); continue
        (DA, FA, IA), (_, FB, IB) = A, B
        assert (IA == IB).all(), 'candidate and reference disagree on the domain'
        nF, nR = int(FA.sum()), int(FB.sum()); inter, union = int((FA & FB).sum()), int((FA | FB).sum())
        ids = oos_sites(s) if s in OOS else [m['id'] for m in DA['strict']]
        M = {m['id']: m['segs'] for m in DA['strict']}
        hits = [i for i in (ids or []) if i in M and FA[np.asarray(M[i])].any()]
        r.update(status='ok', flagged=nF, flagged_radar=nR, ratio_n=round(nF / nR, 3) if nR else None, csi=round(inter / union, 3) if union else None,
                 sites=len(ids or []), sites_matched=sum(i in M for i in (ids or [])), hits=len(hits), hit_ids=hits,
                 flagged_share=round(nF / int(IA.sum()), 4))
        rows.append(r)
        if s in OOS:
            pool['F'] += nF; pool['R'] += nR; pool['inter'] += inter; pool['union'] += union; pool['hits'] += len(hits); pool['sites'] += len(ids or [])
            pool['flagged'] += nF; pool['inb'] += int(IA.sum())
    done = [r for r in rows if r['storm'] in OOS and r.get('status') == 'ok']
    res = dict(cand=cand, made=dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), prereg='DISTRICT_MAP_PREREG.md (3db11469c)', storms=rows, complete=len(done) == len(OOS))
    if done:
        ratio = pool['F'] / pool['R'] if pool['R'] else None; rec = pool['hits'] / pool['sites'] if pool['sites'] else None
        share = pool['flagged'] / pool['inb'] if pool['inb'] else None; lift = rec / share if rec is not None and share else None
        res['pooled'] = dict(ratio_n=ratio, site_recall=rec, hits=pool['hits'], sites=pool['sites'], flagged_share=share, lift=lift,
                             csi=pool['inter'] / pool['union'] if pool['union'] else None)
        c = [ratio is not None and 0.7 <= ratio <= 1.5, rec is not None and rec >= BOX_RECALL, lift is not None and lift >= 2]
        res['conditions'] = dict(ratio_n=c[0], site_recall=c[1], lift=c[2])
        res['verdict'] = ('pass' if all(c) else 'fail') if res['complete'] else 'incomplete'
    json.dump(res, open(os.path.join(FC, f'district_map_{cand}.json'), 'w'), indent=1)
    return res


def selftest():
    import forecast_ens as F
    J = jobs('vp'); assert len(J) == 36 and all(j['kind'] == 'run_storm' for j in J)
    assert sum(len(oos_sites(s) or []) for s in OOS) == N_SITES, [len(oos_sites(s) or []) for s in OOS]
    v = [j for j in J if j['id'] == 'dm_jul2021_vp_solve'][0]['env']; assert v['LF_HRRR_INIT'] == '2021-07-09T12Z' and v['HOURS'] == '14' and v['LF_HRRR_VOLPRES'] == '1'
    A = jobs('a'); assert len(A) == 9 * 8 * 2 and not any(j['id'].startswith(tuple(f'dm_{s}_ref' for s in DEV + OOS)) for j in A)
    assert len({j['id'] for j in A}) == len(A)
    print('selftest ok:', len(A), 'requests for (a);', len(J), 'requests;', N_SITES, 'out-of-sample sites')


def main():
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('jobs'); p.add_argument('--cand', default='vp')
    p = sp.add_parser('score'); p.add_argument('--cand', default='vp')
    sp.add_parser('selftest')
    a = ap.parse_args()
    if a.cmd == 'jobs': print(json.dumps(jobs(a.cand), indent=1))
    elif a.cmd == 'score': print(json.dumps(score(a.cand), indent=1)[:4000])
    else: selftest()


if __name__ == '__main__':
    main()
