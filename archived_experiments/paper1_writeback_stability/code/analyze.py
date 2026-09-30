from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1]
rec=json.loads((R/'validation/run.json').read_text());assert 'end' in rec and len(rec['runs'])==1200
assert all(hashlib.sha256((R/k).read_bytes()).hexdigest()==v for k,v in rec['hashes'].items())
rows=[];curves=[];maxgeom=0;maxnorm=0
for j in rec['runs']:
 assert j['exit_code']==0
 p=R/'raw'/j['prefix'];m=pd.read_csv(str(p)+'_metrics.csv');u=pd.read_csv(str(p)+'_updates.csv');s=pd.read_csv(str(p)+'_stability.csv');a=json.loads(Path(str(p)+'_audit.json').read_text())
 assert len(m)==101 and len(s)==len(u)==a['births_total']
 assert (m.population.diff().iloc[1:].values==(m.births-m.background_deaths-m.energy_deaths).iloc[1:].values).all()
 assert np.isfinite(s).all().all() and np.isfinite(u).all().all()
 assert np.isclose(u.write_norm.sum(),a['sum_norm']) and np.isclose((u.write_norm**2).sum(),a['sum_sq'])
 assert int((u.write_norm>0).sum())==a['nonzero']
 assert a['energy_error']<1e-10 and a['split_error']<1e-10 and a['unreachable_sq']<1e-10
 if j['cap']>0:assert a['nonzero']<=j['cap']
 if j['rule']:
  assert np.allclose(s.post_a,s.post_r,atol=1e-10,rtol=1e-10)
  assert np.allclose(u.write_norm,np.where(u.allowed,s.post_a,0),atol=1e-10,rtol=1e-10)
  assert s.post_a.max()<=.1841261006694567+1e-10
  maxgeom=max(maxgeom,s.geometry.max());maxnorm=max(maxnorm,abs(s.post_a-s.post_r).max())
 if j['rule']>=2:
  lo,hi=(-.62,.42) if j['rule']==2 else (-1,1)
  assert s.child_min.min()>=lo-1e-10 and s.child_max.max()<=hi+1e-10
 occ=m.population/1024
 row={k:v for k,v in j.items() if k not in ['stderr','exit_code']}
 row.update(auc=np.trapezoid(occ,m.t)/20000,late=occ[m.t>19000].mean(),extinct=bool((m.population==0).any()),births=a['births_total'],updates=a['nonzero'],sum_norm=a['sum_norm'],sum_sq=a['sum_sq'],max_step=u.write_norm.max(),p99_step=u.write_norm.quantile(.99),median_step=u.write_norm.median(),max_abs_child=max(s.child_max.max(),-s.child_min.min()),norm_hit=s.loc[s.allowed.astype(bool),"norm_hit"].mean(),box_hit=(s.loc[s.allowed.astype(bool),"box_rows"]>0).mean(),min_scale=s.min_scale.min(),mean_tv_a=s.tv_a.mean() if j['rule'] else np.nan,mean_tv_r=s.tv_r.mean() if j['rule'] else np.nan)
 for threshold in [.90,.95,.99]:
  good=occ>=threshold;times=[int(m.t.iloc[k]) for k in range(len(m)-4) if good.iloc[k:k+5].all()]
  row['reached'+str(threshold)]=bool(times);row['time'+str(threshold)]=times[0] if times else 20000
 rows.append(row)
 for k in ['seed','fraction','lam','rule','cap','mode']:m[k]=j[k]
 curves.append(m[['t','population','resource_mean','genotype_rms','seed','fraction','lam','rule','cap','mode']])
df=pd.DataFrame(rows);df.to_csv(R/'run_summary.csv',index=False);pd.concat(curves).to_csv(R/'curves.csv',index=False)
keys=['fraction','lam','rule','cap','mode']
su=df.groupby(keys).agg(n=('seed','size'),time=('time0.95','mean'),reached=('reached0.95','sum'),extinct=('extinct','sum'),auc=('auc','mean'),late=('late','mean'),births=('births','mean'),updates=('updates','mean'),sum_norm=('sum_norm','mean'),sum_sq=('sum_sq','mean'),max_step=('max_step','max'),p99_step=('p99_step','mean'),max_abs_child=('max_abs_child','max'),norm_hit=('norm_hit','mean'),box_hit=('box_hit','mean'),mean_tv_a=('mean_tv_a','mean'),mean_tv_r=('mean_tv_r','mean')).reset_index();su.to_csv(R/'summary.csv',index=False)
rng=np.random.default_rng(9126);ix=rng.integers(0,20,(20000,20));effects=[];contrasts=[]
def interval(d):
 q=np.quantile(d[ix].mean(1),[.025,.975]);return dict(effect=d.mean(),low=q[0],high=q[1],positive=int((d>0).sum()),negative=int((d<0).sum()))
for key,g in df.groupby(['fraction','lam','rule','cap']):
 for metric in ['time0.95','auc','late','reached0.95']:
  p=g.pivot(index='seed',columns='mode',values=metric).astype(float);d=(p[8]-p[7] if metric.startswith('time') else p[7]-p[8]).values
  effects.append(dict(zip(['fraction','lam','rule','cap'],key),metric=metric,**interval(d)))
for (fraction,lam),g in df[df.cap==-1].groupby(['fraction','lam']):
 for metric in ['time0.95','auc']:
  p=g.pivot(index='seed',columns=['rule','mode'],values=metric)
  sign=-1 if metric.startswith('time') else 1
  for rule in [1,2,3]:
   d=sign*((p[(rule,7)]-p[(rule,8)])-(p[(0,7)]-p[(0,8)]))
   contrasts.append(dict(fraction=fraction,lam=lam,rule=rule,metric=metric,**interval(d.values)))
pd.DataFrame(effects).to_csv(R/'paired_effects.csv',index=False);pd.DataFrame(contrasts).to_csv(R/'effect_change.csv',index=False)
(R/'validation/analysis.json').write_text(json.dumps(dict(runs=1200,seed_units=20,frozen=True,population_and_budget_ledger=True,energy=True,zero_unreachable=True,paired_geometry_max=maxgeom,paired_norm_max=maxnorm,bounds=True,finite_updates=True),indent=2))
print(su[['fraction','lam','rule','cap','mode','time','reached','auc','max_step','max_abs_child','norm_hit','box_hit']].to_string(index=False))
