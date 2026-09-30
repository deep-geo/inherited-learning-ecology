from pathlib import Path
import json,hashlib,os
os.environ['MPLCONFIGDIR']='/tmp/paper1_cutoff_mpl'
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
rec=json.loads((R/'validation/run.json').read_text());assert 'end' in rec and len(rec['runs'])==160
assert all(hashlib.sha256((R/k).read_bytes()).hexdigest()==v for k,v in rec['hashes'].items())
rows=[];curves=[]
for j in rec['runs']:
 p=R/'raw'/j['prefix'];m=pd.read_csv(str(p)+'_metrics.csv');u=pd.read_csv(str(p)+'_updates.csv');s=pd.read_csv(str(p)+'_stability.csv');a=json.loads(Path(str(p)+'_audit.json').read_text())
 assert j['exit_code']==0 and len(m)==101 and len(s)==len(u)==a['births_total']
 assert np.isfinite(u).all().all() and np.isfinite(s).all().all()
 assert (m.population.diff().iloc[1:].values==(m.births-m.background_deaths-m.energy_deaths).iloc[1:].values).all()
 assert np.isclose(u.write_norm.sum(),a['sum_norm']) and np.isclose((u.write_norm**2).sum(),a['sum_sq'])
 assert int((u.write_norm>0).sum())==a['nonzero']
 assert a['energy_error']<1e-10 and a['split_error']<1e-10 and a['unreachable_sq']<1e-10
 assert np.allclose(s.post_a,s.post_r,atol=1e-10,rtol=1e-10)
 assert np.allclose(u.write_norm,np.where(u.allowed,s.post_a,0),atol=1e-10,rtol=1e-10)
 assert s.post_a.max()<=.1841261006694567+1e-10
 assert s.child_min.min()>=-.62-1e-10 and s.child_max.max()<=.42+1e-10
 if j['cap']>0:assert a['nonzero']==1024
 if j['stop']>=0:assert (u.loc[u.t>j['stop'],'write_norm']==0).all() and (u.allowed==(u.t<=j['stop']).astype(int)).all()
 occ=m.population/1024;good=occ>=.95;times=[int(m.t.iloc[k]) for k in range(len(m)-4) if good.iloc[k:k+5].all()]
 row={k:v for k,v in j.items() if k not in ['stderr','exit_code']}
 cutoff=j['stop'] if j['stop']>=0 else a['cap_time']
 before=m[m.t<=cutoff].iloc[-1] if cutoff>=0 else None
 after=m[m.t>=cutoff].iloc[0] if cutoff>=0 else None
 row.update(time=times[0] if times else 20000,reached=bool(times),auc=np.trapezoid(occ,m.t)/20000,late=occ.iloc[-5:].mean(),extinct=bool((m.population==0).any()),births=a['births_total'],updates=a['nonzero'],sum_norm=a['sum_norm'],sum_sq=a['sum_sq'],cutoff=cutoff,last_write=int(u.loc[u.write_norm>0,'t'].max()),cutoff_sample_before_t=before.t if before is not None else np.nan,cutoff_sample_before_occ=before.population/1024 if before is not None else np.nan,cutoff_sample_after_t=after.t if after is not None else np.nan,cutoff_sample_after_occ=after.population/1024 if after is not None else np.nan)
 rows.append(row)
 curves.append(pd.DataFrame(dict(seed=j['seed'],mode=j['mode'],regime=j['regime'],t=m.t,occupancy=occ,resource=m.resource_mean)))
df=pd.DataFrame(rows);df.to_csv(R/'run_summary.csv',index=False)
cv=pd.concat(curves);cv.to_csv(R/'curves.csv',index=False)
su=df.groupby(['regime','mode']).agg(n=('seed','size'),time=('time','mean'),reached=('reached','sum'),extinct=('extinct','sum'),auc=('auc','mean'),late=('late','mean'),updates=('updates','mean'),sum_norm=('sum_norm','mean'),sum_sq=('sum_sq','mean'),births=('births','mean'),cutoff=('cutoff','mean')).reset_index();su.to_csv(R/'summary.csv',index=False)
rg=np.random.default_rng(309301);ix=rg.integers(0,20,(20000,20))
def interval(d):
 return dict(effect=float(np.mean(d)),low=float(np.quantile(d[ix].mean(1),.025)),high=float(np.quantile(d[ix].mean(1),.975)))
effects=[];ds={}
for regime,g in df.groupby('regime'):
 for metric in ['time','auc','reached','late']:
  p=g.pivot(index='seed',columns='mode',values=metric).sort_index().astype(float)
  d=(p[8]-p[7] if metric=='time' else p[7]-p[8]).values;ds[regime,metric]=d
  effects.append(dict(regime=regime,metric=metric,**interval(d)))
ef=pd.DataFrame(effects);ef.to_csv(R/'paired_effects.csv',index=False)
inter=[]
for regime in ['time150','time750','continuous']:
 for metric in ['time','auc','reached','late']:
  inter.append(dict(regime=regime,reference='count1024',metric=metric,**interval(ds[regime,metric]-ds['count1024',metric])))
it=pd.DataFrame(inter);it.to_csv(R/'interaction_effects.csv',index=False)
fig,axs=plt.subplots(2,2,figsize=(11,7),sharex=True,sharey=True)
order=['continuous','count1024','time150','time750']
for ax,regime in zip(axs.flat,order):
 for mode,label,col in [(7,'Directed','#147d92'),(8,'Random','#ca6436')]:
  z=cv[(cv.regime==regime)&(cv['mode']==mode)].pivot(index='seed',columns='t',values='occupancy').sort_index()
  samples=z.values[ix].mean(1);lo,hi=np.quantile(samples,[.025,.975],axis=0)
  ax.plot(z.columns,z.mean(),label=label,color=col);ax.fill_between(z.columns,lo,hi,color=col,alpha=.18)
 ax.axhline(.95,ls=':',color='gray');ax.set_title(regime);ax.set_ylim(0,1.03);ax.set_xlabel('Sweep');ax.set_ylabel('Occupancy');ax.legend()
fig.suptitle('Predefined cutoff diagnostic: 20 paired seeds; pointwise 95% bootstrap bands');fig.tight_layout();fig.savefig(R/'occupancy.png',dpi=180);plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(10,4))
for k,(metric,label) in enumerate([('time','Capped establishment time'),('updates','Nonzero writebacks')]):
 for mode,col,labelmode,offset in [(7,'#147d92','Directed',-.18),(8,'#ca6436','Random',.18)]:
  vals=[su[(su.regime==r)&(su['mode']==mode)][metric].iloc[0] for r in order]
  axs[k].bar(np.arange(4)+offset,vals,.36,label=labelmode,color=col)
 axs[k].set_xticks(range(4),order,rotation=15);axs[k].set_ylabel(label);axs[k].legend()
fig.tight_layout();fig.savefig(R/'outcomes_budget.png',dpi=180);plt.close(fig)
(R/'validation/analysis.json').write_text(json.dumps(dict(runs=160,independent_seeds=20,frozen_hashes=True,ledger=True,bounds=True,geometry=True,cutoff_logic=True,development_note='Initial checks caught integer versus float CSV inference for all-zero columns; comparison changed to ignore dtype but require exact values before formal freeze.'),indent=2))
print(su.to_string(index=False));print(it.to_string(index=False))
