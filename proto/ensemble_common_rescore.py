"""ENSEMBLE_PARITY.md section 3. Re-score legacy and parity ensemble runs on the SAME labels and SAME in-box segments (intersection), using forecast_ens's own rules."""
import json, os, sys, shutil, glob, subprocess
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F=R+'/docs/proto/forecast/'
for tag in ('ensemble','ensemble_parity'):
    other='ensemble_parity' if tag=='ensemble' else 'ensemble'
    dst=F+f'_common_{tag}'; shutil.rmtree(dst,ignore_errors=True); os.makedirs(dst)
    for d in glob.glob(F+tag+'/*'):
        k=os.path.basename(d); o=F+other+'/'+k
        if not os.path.exists(d+'/seg.json') or not os.path.exists(o+'/seg.json'): continue
        a=json.load(open(d+'/seg.json')); b=json.load(open(o+'/seg.json'))
        ib=set(b['inbox']); keep=[(i,p) for i,p in zip(a['inbox'],a['p_depth']) if i in ib]
        a['inbox']=[i for i,_ in keep]; a['p_depth']=[p for _,p in keep]
        for kind in ('strict','loose'):
            ids={m['id'] for m in b[kind]}
            # both runs must match the label; use segments matched in both
            bm={m['id']:set(m['segs']) for m in b[kind]}
            a[kind]=[dict(m,segs=sorted(set(m['segs'])&bm[m['id']]) or m['segs']) for m in a[kind] if m['id'] in ids]
        os.makedirs(dst+'/'+k); json.dump(a,open(dst+'/'+k+'/seg.json','w'))
    env=dict(os.environ,FENS_DIR=f'_common_{tag}',FENS_REPORT=f'ensemble_common_{tag}.json')
    subprocess.run(['python3','proto/forecast_ens.py','report'],cwd=R,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    shutil.rmtree(dst)
