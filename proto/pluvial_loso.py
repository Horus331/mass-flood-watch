"""Urban / pluvial miss diagnosis and leave-one-storm-out (LOSO) test of the PROTO_PLUVIAL candidate rule, from published data only
(docs/proto/turing/<storm>_<area>_20m/features_<storm>.csv + matches_<storm>.json).  python proto/pluvial_loso.py -> docs/proto/urban/loso.json
Findings: docs/proto/urban/FINDINGS.md.  The rule mirrors prototype.pluvial_probability (same geo features, same per-segment peak-1h rain)."""
import csv, json, itertools, numpy as np
from scipy.spatial import cKDTree
from scipy.stats import norm
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); TUR=ROOT+'/docs/proto/turing'
AREA=dict(aug2021='worcester', aug2023='metrowest', aug2023b='millbury', aug2026='leominster', jul2021='worcester', jul2023='worcester', sep2021='worcester', sep2022='webster', sep2023='leominster')
def F(x):
    try: return float(x)
    except: return np.nan
S={}
for s,a in AREA.items():
    d=f'{TUR}/{s}_{a}_20m'; rows=list(csv.DictReader(open(f'{d}/features_{s}.csv'))); M=json.load(open(f'{d}/matches_{s}.json'))
    A={k:np.nan_to_num(np.array([F(r[k]) for r in rows])) for k in ['hand_m','slope_pct','area_km2','peak1h_mm','storm_total_mm','flashness_pct','cx','cy','p_sag','p_close']}
    t=cKDTree(np.column_stack([A['cx'],A['cy']])); A['dens']=np.array([len(v) for v in t.query_ball_point(np.column_stack([A['cx'],A['cy']]),300)],float)
    A['local']=np.array([r['road_class']=='local / collector' for r in rows])
    idx={int(r['segment']):i for i,r in enumerate(rows)}
    A['sites']=[[idx[g] for g in m['segs'] if g in idx] for m in M['matches'].values()]; A['sites']=[x for x in A['sites'] if x]
    A['y']=np.array([r['y']=='1' for r in rows])
    S[s]=A
def metrics(A, flag):
    rec=np.mean([flag[x].any() for x in A['sites']]); share=flag.mean()
    return rec, share, sum(flag[x].any() for x in A['sites']), len(A['sites'])
C=0.6
def rule(A, kind, par):
    i=A['peak1h_mm']; low=A['hand_m']<=0.5
    if kind=='inflow':   # rational inflow C i A vs inlet/drain capacity Qcap (m3/s) at a low-lying, urban segment
        qcap,D=par; q=C*i/1000/3600*A['area_km2']*1e6
        p=norm.cdf(np.log(np.maximum(q,1e-9)/qcap)/0.5)*(low&(A['dens']>=D))
    elif kind=='excess': # peak-hour intensity vs effective drain capacity icap (mm/h), low-lying urban, flat
        icap,D,sl=par; p=norm.cdf(np.log(np.maximum(i,1e-9)/icap)/0.5)*(low&(A['dens']>=D)&(A['slope_pct']<=sl))
    elif kind=='sagboost': # existing sag layer (p_sag>0 means a mapped sag with some model water) at lower threshold
        thr,=par; p=(A['p_sag']>=thr).astype(float)
    return p
GRID={'inflow':list(itertools.product([0.02,0.05,0.1,0.2,0.3,0.5,1.0,2.0],[0,10,15,20,25])),
      'excess':list(itertools.product([15,20,25,30,35,43,58],[0,15,20,25],[2,3,5,100])),
      'sagboost':[(t,) for t in [0.05,0.1,0.2,0.3]]}
storms=list(S)
base={s:S[s]['p_close']>=0.5 for s in storms}
def evalset(ss, kind, par):
    r=[];sh=[]
    for s in ss:
        fl=base[s]|(rule(S[s],kind,par)>=0.5); a,b,_,_=metrics(S[s],fl); r.append(a); sh.append(b)
    return np.mean(r), np.mean(sh)
res={}
for kind in GRID:
    out={}
    for h in storms:
        tr=[s for s in storms if s!=h]
        r0,sh0=evalset(tr,'sagboost',(2.0,))   # default
        best=None
        for par in GRID[kind]:
            r,sh=evalset(tr,kind,par)
            if sh<=sh0+0.01 and (best is None or r>best[0]+1e-9 or (abs(r-best[0])<1e-9 and sh<best[1])): best=(r,sh,par)
        par=best[2]; fl=base[h]|(rule(S[h],kind,par)>=0.5)
        a,b,k,n=metrics(S[h],fl); a0,b0,k0,_=metrics(S[h],base[h])
        out[h]=dict(par=par, sites=f'{k}/{n}', base_sites=f'{k0}/{n}', rec=round(a,3), rec0=round(a0,3), share=round(b*100,2), share0=round(b0*100,2),
                    lift=round(a/b,1) if b else 0, lift0=round(a0/b0,1) if b0 else 0)
    res[kind]=out
    print('\n##',kind)
    for h,o in out.items(): print(h,o)
    oos=[h for h in storms if h not in('aug2021','sep2023')]
    k=sum(int(out[h]['sites'].split('/')[0]) for h in oos); k0=sum(int(out[h]['base_sites'].split('/')[0]) for h in oos); n=sum(int(out[h]['sites'].split('/')[1]) for h in oos)
    print('OOS 7 storms sites', k,'/',n,'(default',k0,')  mean share %.2f%% (default %.2f%%)'%(np.mean([out[h]['share'] for h in oos]),np.mean([out[h]['share0'] for h in oos])))
json.dump(res,open(ROOT+'/docs/proto/urban/loso.json','w'),indent=1,default=str)

print('\n## gained sites and ablation (inflow 0.5, D15)')
rng=np.random.default_rng(0)
for s in storms:
    A=S[s]; p=rule(A,'inflow',(0.5,15)); fl=base[s]|(p>=0.5); add=fl&~base[s]
    gained=[x for x in A['sites'] if fl[x].any() and not base[s][x].any()]
    # ablation: constant 30 mm/h rain
    A2=dict(A); A2['peak1h_mm']=np.full_like(A['peak1h_mm'],30.0); fl2=base[s]|(rule(A2,'inflow',(0.5,15))>=0.5)
    # chance: same number of added segments drawn at random from non-flagged segments (and from the low+urban pool)
    pool=np.nonzero(~base[s])[0]; pool2=np.nonzero(~base[s]&(A['hand_m']<=0.5)&(A['dens']>=15))[0]; ch=[];ch2=[]
    for _ in range(500):
        f=base[s].copy(); f[rng.choice(pool,add.sum(),replace=False)]=True; ch.append(sum(f[x].any() for x in A['sites']))
        f=base[s].copy(); f[rng.choice(pool2,min(add.sum(),len(pool2)),replace=False)]=True; ch2.append(sum(f[x].any() for x in A['sites']))
    k0=sum(base[s][x].any() for x in A['sites'])
    print(s,'added segs',int(add.sum()),'gained',len(gained),'| const-30mm sites',sum(fl2[x].any() for x in A['sites']),'share %.2f'%(fl2.mean()*100),
          '| chance gain random %.2f, low+urban pool %.2f'%(np.mean(ch)-k0,np.mean(ch2)-k0))

print('\n## sensitivity, fixed params, OOS 7 storms')
oos=[h for h in storms if h not in('aug2021','sep2023')]
for qc in [0.2,0.3,0.5,0.75,1.0]:
  for D in [10,15,20]:
    k=0;n=0;sh=[];kl=[]
    for s in storms:
        fl=base[s]|(rule(S[s],'inflow',(qc,D))>=0.5); hit=sum(fl[x].any() for x in S[s]['sites'])
        if s in oos: k+=hit; n+=len(S[s]['sites']); sh.append(fl.mean()*100)
        else: kl.append(f'{s} {hit}/{len(S[s]["sites"])} {fl.mean()*100:.2f}%')
    print(qc,D,f'OOS {k}/{n} share {np.mean(sh):.2f}%', kl)
print('\n## CN effective runoff, HSG C pervious (CN 73), LF_CN_SCALE 0.91, AMC II')
for imp in [0.3,0.5,0.8]:
    cn=(imp*98+(1-imp)*73)*0.91; Sx=25400/cn-254; Ia=0.2*Sx
    print(imp, 'CN %.1f'%cn, [(P, round((P-Ia)**2/(P-Ia+Sx) if P>Ia else 0,1), round(imp*max(P-2,0),1)) for P in [20,30,45,60,106]])
