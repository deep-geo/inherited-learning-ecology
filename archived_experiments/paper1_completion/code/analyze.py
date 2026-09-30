from pathlib import Path
import json
import pandas as pd,numpy as np
R=Path(__file__).resolve().parents[1];rows=[];curves=[]
for stage in ['development','representation','mechanism','robustness']:
 p=R/'validation'/f'{stage}_run.json'
 if not p.exists():continue
 log=json.loads(p.read_text())
 if 'end_utc' not in log:continue
 for j in log['runs']:
  pre=R/'raw'/stage/j['prefix'];x=pd.read_csv(str(pre)+'_metrics.csv');a=json.loads(Path(str(pre)+'_audit.json').read_text());occ=x.population/1024
  d={**j,**a,'stage':stage,'extinct':a['extinction_first_sample']>=0,'final_occupancy':occ[x.t>19000].mean(),'auc':np.trapezoid(occ,x.t)/20000,'budget_exhausted':j['budget']>0 and a['nonzero']==j['budget']}
  for threshold in [.9,.95,.99]:
   times=x.loc[occ.ge(threshold).rolling(5).sum().eq(5),'t'];d[f'reached{threshold}']=len(times)>0;d[f'time{threshold}']=int(times.iloc[0]-800) if len(times) else np.nan;d[f'capped{threshold}']=int(times.iloc[0]-800) if len(times) else 20000
  rows.append(d);v=x[['t','population']].copy()
  for key in ['bins','budget','method','setting','intervention','child_eta','seed']:v[key]=j[key]
  v['stage']=stage;curves.append(v)
a=pd.DataFrame(rows);a.to_csv(R/'run_summary.csv',index=False);pd.concat(curves,ignore_index=True).to_csv(R/'curves.csv',index=False)
keys=['stage','bins','setting','budget','intervention','child_eta','method']
s=a.groupby(keys).agg(n=('seed','size'),reached=('reached0.95','sum'),capped_time=('capped0.95','mean'),extinctions=('extinct','sum'),final_occupancy=('final_occupancy','mean'),auc=('auc','mean'),quota_used=('budget_exhausted','sum'),used=('nonzero','mean'),births=('births_total','mean'),sum_norm=('sum_norm','mean'),sum_sq=('sum_sq','mean'),contrast_sq=('contrast_sq','mean'),skips=('fallbacks','sum'),cap_time=('cap_time','mean'),intervened_births=('intervention_births','mean')).reset_index();s.to_csv(R/'summary.csv',index=False)
rng=np.random.default_rng(7192026);effects=[]
def effect(d,**meta):
 d=np.asarray(d,float);b=d[rng.integers(0,len(d),(20000,len(d)))].mean(axis=1);lo,hi=np.quantile(b,[.025,.975]);effects.append(dict(**meta,n=len(d),effect=d.mean(),low=lo,high=hi,positive=int((d>0).sum()),negative=int((d<0).sum())))
for (stage,bins,setting,B,iv,eta),g in a[(a.stage!='development')&(a.method!='none')].groupby(keys[:-1]):
 for metric in ['capped0.95','auc','final_occupancy','reached0.95']:
  p=g.pivot(index='seed',columns='method',values=metric).astype(float);d=p.state_rotated-p.aligned if metric.startswith('capped') else p.aligned-p.state_rotated
  effect(d,kind='direction_advantage',stage=stage,bins=bins,setting=setting,budget=B,intervention=iv,child_eta=eta,metric=metric)
m=a[a.stage=='mechanism']
if len(m):
 for method in ['aligned','state_rotated']:
  for eta in [0,.2,.8]:
   for metric in ['capped0.95','auc']:
    p=m[(m.method==method)&(m.child_eta==eta)].pivot(index='seed',columns='intervention',values=metric);d=p[2]-p[1] if metric.startswith('capped') else p[1]-p[2]
    effect(d,kind='erasure_penalty',stage='mechanism',method=method,child_eta=eta,metric=metric)
  for metric in ['capped0.95','auc']:
   p=m[m.method==method].pivot(index='seed',columns=['intervention','child_eta'],values=metric)
   d=p[(2,.2)]-p[(2,.8)] if metric.startswith('capped') else p[(2,.8)]-p[(2,.2)]
   effect(d,kind='fast_learning_rescue_erased',stage='mechanism',method=method,metric=metric)
   d=(p[(2,.2)]-p[(1,.2)])-(p[(2,.8)]-p[(1,.8)])
   if metric=='auc':d=-d
   effect(d,kind='erasure_penalty_reduction_fast_learning',stage='mechanism',method=method,metric=metric)
 for eta in [0,.2,.8]:
  for metric in ['capped0.95','auc']:
   p=m[m.child_eta==eta].pivot(index='seed',columns=['method','intervention'],values=metric)
   d=(p[('state_rotated',1)]-p[('aligned',1)])-(p[('state_rotated',2)]-p[('aligned',2)])
   if metric=='auc':d=-d
   effect(d,kind='direction_advantage_reduction_erasure',stage='mechanism',child_eta=eta,metric=metric)
e=pd.DataFrame(effects);e.to_csv(R/'paired_effects.csv',index=False)
print(s[s.stage!='development'].to_string(index=False));print(e[e.metric=='capped0.95'].to_string(index=False))
