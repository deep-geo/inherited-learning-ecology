from pathlib import Path
import pandas as pd,numpy as np,json
R=Path(__file__).resolve().parents[1];rows=[];curves=[]
for stage in ['development','confirmation','budgets','replay']:
 p=R/'validation'/f'{stage}_run.json'
 if not p.exists():continue
 log=json.loads(p.read_text())
 if 'end_utc' not in log:continue
 for job in log['runs']:
  pre=R/'raw'/stage/job['prefix'];x=pd.read_csv(str(pre)+'_metrics.csv');a=json.loads(Path(str(pre)+'_audit.json').read_text());occ=x.population/1024
  d=dict(stage=stage,seed=job['seed'],condition=job['condition'],budget=job['budget'],births=a['births_total'],used=a['nonzero'],budget_exhausted=job['budget']>0 and a['nonzero']==job['budget'],sum_norm=a['sum_norm'],sum_sq=a['sum_sq'],contrast_sq=a['contrast_sq'],common_sq=a['common_sq'],unreachable_sq=a['unreachable_sq'],zero_signal_skips=a['fallbacks'],extinct=a['extinction_first_sample']>=0,final_occupancy=occ[x.t>19000].mean(),auc=np.trapezoid(occ,x.t)/20000,row_mean_error=a['row_mean_error'],row_norm_error=a['row_norm_error'],row_contrast_error=a['row_contrast_error'],support_error=a['empty_support_error'])
  for thresh in [.9,.95,.99]:
   times=x.loc[occ.ge(thresh).rolling(5).sum().eq(5),'t'];d[f'reached{thresh}']=len(times)>0;d[f'time{thresh}']=int(times.iloc[0]-800) if len(times) else np.nan;d[f'capped{thresh}']=int(times.iloc[0]-800) if len(times) else 20000
  rows.append(d);z=x[['t','population']].copy();z['stage']=stage;z['seed']=job['seed'];z['condition']=job['condition'];z['budget']=job['budget'];curves.append(z)
a=pd.DataFrame(rows);a.to_csv(R/'run_summary.csv',index=False);pd.concat(curves,ignore_index=True).to_csv(R/'curves.csv',index=False)
s=a.groupby(['stage','budget','condition']).agg(n=('seed','size'),reached=('reached0.95','sum'),capped_time=('capped0.95','mean'),extinctions=('extinct','sum'),final_occupancy=('final_occupancy','mean'),auc=('auc','mean'),budget_exhausted=('budget_exhausted','sum'),used=('used','mean'),births=('births','mean'),sum_norm=('sum_norm','mean'),sum_sq=('sum_sq','mean'),contrast_sq=('contrast_sq','mean'),unreachable_sq=('unreachable_sq','mean'),skips=('zero_signal_skips','sum')).reset_index();s.to_csv(R/'summary.csv',index=False)
effects=[];rng=np.random.default_rng(81831)
for (stage,B),g in a[a.stage.isin(['confirmation','budgets'])&a.condition.ne('none')].groupby(['stage','budget']):
 for metric in ['capped0.95','auc','final_occupancy','reached0.95']:
  p=g.pivot(index='seed',columns='condition',values=metric).astype(float)
  for other in ['state_rotated_q','global_scrambled_q','isotropic_q']:
   d=(p[other]-p.aligned_q if metric=='capped0.95' else p.aligned_q-p[other]).to_numpy();b=d[rng.integers(0,len(d),(20000,len(d)))].mean(axis=1);lo,hi=np.quantile(b,[.025,.975]);effects.append(dict(stage=stage,budget=B,metric=metric,comparison='aligned_q vs '+other,n=len(d),advantage=d.mean(),low=lo,high=hi,positive=int((d>0).sum()),negative=int((d<0).sum())))
e=pd.DataFrame(effects);e.to_csv(R/'paired_effects.csv',index=False)
print(s[s.stage!='development'].to_string(index=False));print(e[(e.metric=='capped0.95')&(e.comparison=='aligned_q vs state_rotated_q')].to_string(index=False))
