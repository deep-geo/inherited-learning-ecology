from pathlib import Path
import pandas as pd,numpy as np,json
R=Path(__file__).resolve().parents[1];rows=[];curves=[]
for stage in ['development','confirmation']:
 p=R/'validation'/f'{stage}_run.json'
 if not p.exists():continue
 log=json.loads(p.read_text())
 if 'end_utc' not in log:continue
 for j in log['runs']:
  pre=R/'raw'/stage/j['prefix'];x=pd.read_csv(str(pre)+'_metrics.csv');b=pd.read_csv(str(pre)+'_updates.csv');z=json.loads(Path(str(pre)+'_audit.json').read_text());occ=x.population/1024
  d={**j,**z,'stage':stage,'extinct':z['extinction_first_sample']>=0,'final_occupancy':occ[x.t>19000].mean(),'auc':np.trapezoid(occ,x.t)/20000,'quota_used':j['cap']>0 and z['nonzero']==j['cap'],'mean_nonzero_norm':z['sum_norm']/z['nonzero'] if z['nonzero'] else np.nan,'max_write_norm':b.write_norm.max() if len(b) else 0}
  for thresh in [.9,.95,.99]:
   t=x.loc[occ.ge(thresh).rolling(5).sum().eq(5),'t'];d[f'reached{thresh}']=len(t)>0;d[f'time{thresh}']=int(t.iloc[0]-800) if len(t) else np.nan;d[f'capped{thresh}']=int(t.iloc[0]-800) if len(t) else 20000
  rows.append(d);c=x[['t','population']].copy()
  for key in ['seed','fraction','cap','lam','method']:c[key]=j[key]
  c['stage']=stage;curves.append(c)
a=pd.DataFrame(rows);a.to_csv(R/'run_summary.csv',index=False);pd.concat(curves,ignore_index=True).to_csv(R/'curves.csv',index=False)
keys=['stage','fraction','cap','lam','method'];s=a.groupby(keys).agg(n=('seed','size'),reached=('reached0.95','sum'),capped_time=('capped0.95','mean'),extinctions=('extinct','sum'),auc=('auc','mean'),late=('final_occupancy','mean'),births=('births_total','mean'),updates=('nonzero','mean'),quota_used=('quota_used','sum'),sum_norm=('sum_norm','mean'),sum_sq=('sum_sq','mean'),mean_nonzero_norm=('mean_nonzero_norm','mean'),max_write_norm=('max_write_norm','max')).reset_index();s.to_csv(R/'summary.csv',index=False)
effects=[];rng=np.random.default_rng(929001)
for (fraction,cap,lam),g in a[(a.stage=='confirmation')&(a.method!='none')].groupby(['fraction','cap','lam']):
 for metric in ['capped0.95','auc','final_occupancy','reached0.95']:
  p=g.pivot(index='seed',columns='method',values=metric).astype(float);d=(p.state_rotated-p.aligned if metric.startswith('capped') else p.aligned-p.state_rotated).to_numpy();b=d[rng.integers(0,len(d),(20000,len(d)))].mean(axis=1);lo,hi=np.quantile(b,[.025,.975]);effects.append(dict(fraction=fraction,cap=cap,lam=lam,metric=metric,effect=d.mean(),low=lo,high=hi,positive=int((d>0).sum()),negative=int((d<0).sum())))
e=pd.DataFrame(effects);e.to_csv(R/'paired_effects.csv',index=False);print(s[s.stage=='confirmation'].to_string(index=False));print(e[e.metric=='capped0.95'].to_string(index=False))
