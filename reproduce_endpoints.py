from pathlib import Path
import pandas as pd
import numpy as np
R=Path(__file__).resolve().parent
specs={
'state_matched':['stage','seed','condition','budget'],
'completion':['stage','seed','bins','setting','budget','intervention','child_eta','method'],
'native_writeback':['stage','seed','fraction','cap','lam','method']}
count=0
for name,keys in specs.items():
 a=pd.read_csv(R/'data'/f'{name}_runs.csv')
 c=pd.read_csv(R/'data'/f'{name}_curves.csv')
 keys=[k for k in keys if k in c.columns]
 assert not a.duplicated(keys).any(),(name,keys)
 a=a.set_index(keys)
 groups=c.groupby(keys,dropna=False)
 assert len(groups)==len(a)
 for key,x in groups:
  row=a.loc[key];x=x.sort_values('t');t=x.t.to_numpy();occ=x.population.to_numpy()/1024
  assert len(t)==101 and len(set(t))==101 and t[0]==0 and t[-1]==20000
  for h in [.9,.95,.99]:
   hit=[i for i in range(len(t)-4) if np.all(occ[i:i+5]>=h)]
   assert bool(hit)==bool(row[f'reached{h}'])
   assert (t[hit[0]] if hit else 20000)==row[f'capped{h}']
  assert np.isclose(np.trapezoid(occ,t)/20000,row.auc,atol=1e-12)
  assert np.isclose(occ[t>19000].mean(),row.final_occupancy,atol=1e-12)
  assert bool(np.any(occ==0))==row.extinct
  count+=1
assert count==1840
print(f'PASS: {count} formal runs; attainment, capped times, AUC, late occupancy and extinction reproduced.')
