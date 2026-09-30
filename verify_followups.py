from pathlib import Path
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parent/'archived_experiments'
count=0
for name,n,keys in [('paper1_writeback_stability',1200,['seed','fraction','lam','rule','cap','mode']),('paper1_cutoff_diagnostic',160,['seed','regime','mode']),('paper1_budget_timing',80,['seed','regime','mode'])]:
 d=R/name;a=pd.read_csv(d/'run_summary.csv');c=pd.read_csv(d/'curves.csv');assert len(a)==n and not a.duplicated(keys).any()
 a=a.set_index(keys);groups=c.groupby(keys,dropna=False);assert len(groups)==n
 for key,x in groups:
  row=a.loc[key];x=x.sort_values('t');t=x.t.to_numpy();occ=x.occupancy.to_numpy() if 'occupancy' in x else x.population.to_numpy()/1024
  assert len(t)==101 and np.array_equal(t,np.arange(0,20001,200))
  hit=[i for i in range(len(t)-4) if (occ[i:i+5]>=.95).all()]
  tm='time0.95' if name=='paper1_writeback_stability' else 'time';rc='reached0.95' if name=='paper1_writeback_stability' else 'reached'
  assert (t[hit[0]] if hit else 20000)==row[tm] and bool(hit)==bool(row[rc])
  assert np.isclose(np.trapezoid(occ,t)/20000,row.auc,atol=1e-12)
  assert np.isclose(occ[-5:].mean(),row.late,atol=1e-12)
  assert bool((occ==0).any())==row.extinct
  if name=='paper1_budget_timing':
   assert row.updates==1024 and np.isclose(row.sum_norm,20.48) and np.isclose(row.sum_sq,.4096)
  count+=1
assert count==1440
print('PASS: 1440 follow-up runs; endpoints and fixed-budget summary ledger checked.')
