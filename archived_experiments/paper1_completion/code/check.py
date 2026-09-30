from pathlib import Path
import json,sys,hashlib
import pandas as pd,numpy as np
R=Path(__file__).resolve().parents[1];stage=sys.argv[1];log=json.loads((R/'validation'/f'{stage}_run.json').read_text())
checks=dict(complete='end_utc' in log and len(log['runs'])==log['planned'],frozen_hashes=True,population_balance=True,energy_split_norm=True,row_matching=True,unreachable_zero=True,budget_ledger=True,complete_metrics=True,intervention_ledger=True,pre_intervention_prefix=True)
for name,h in log['hashes'].items():checks['frozen_hashes'] &= hashlib.sha256((R/name).read_bytes()).hexdigest()==h
prefixes={}
for j in log['runs']:
 p=R/'raw'/stage/j['prefix'];a=json.loads(Path(str(p)+'_audit.json').read_text());x=pd.read_csv(str(p)+'_metrics.csv');b=pd.read_csv(str(p)+'_updates.csv');life=pd.read_csv(str(p)+'_lifetimes.csv');iv=pd.read_csv(str(p)+'_interventions.csv')
 checks['complete'] &= j['exit_code']==0
 checks['population_balance'] &= np.array_equal(x.population.diff().iloc[1:],(x.births-x.background_deaths-x.energy_deaths).iloc[1:]) and len(life[life.status!='censored'])==x.background_deaths.sum()+x.energy_deaths.sum() and len(life[life.status=='censored'])==x.population.iloc[-1]
 checks['energy_split_norm'] &= max(a['energy_error'],a['split_error'],a['norm_error'])<1e-10
 checks['row_matching'] &= max(a['row_mean_error'],a['row_norm_error'],a['row_contrast_error'],a['empty_support_error'])<1e-12
 checks['unreachable_zero'] &= a['unreachable_sq']==0
 checks['budget_ledger'] &= a['nonzero']<=j['budget'] and len(b)==a['births_total'] and int((b.write_norm>0).sum())==a['nonzero'] and np.isclose(b.write_norm.sum(),a['sum_norm'],rtol=1e-10,atol=1e-10) and np.isclose(a['sum_sq'],a['contrast_sq']+a['common_sq'],rtol=1e-10,atol=1e-10) and np.isclose(a['sum_norm'],a['nonzero']*.1841261006694567,rtol=1e-10,atol=1e-10)
 checks['complete_metrics'] &= x.t.iloc[-1]==20000 and len(x)==101 and np.isfinite(x.drop(columns=['genotype_rms','mean_depth','mean_parent_visits'])).all().all()
 checks['intervention_ledger'] &= len(iv)==a['intervention_births'] and a['phenotype_mean_error']<1e-12 and np.isclose(iv.erased_contrast_sq.sum(),a['erased_sq'],rtol=1e-10,atol=1e-10)
 if j['intervention']==0:checks['intervention_ledger'] &= len(iv)==0
 elif len(iv):
  checks['intervention_ledger'] &= iv.birth_index.iloc[0]>=j['budget'] and iv.t.iloc[0]==a['cap_time'] and len(iv)==a['births_total']-iv.birth_index.iloc[0]+1
  if j['intervention']==1:checks['intervention_ledger'] &= (iv.theta_g_sq==0).all()
 if (stage=='mechanism') or (stage=='development' and j['family']=='mechanism'):
  key=(j['seed'],j['method']);lines=Path(str(p)+'_updates.csv').read_text().splitlines()[:513]
  if key not in prefixes:prefixes[key]=lines
  else:checks['pre_intervention_prefix'] &= prefixes[key]==lines
checks={k:bool(v) for k,v in checks.items()};(R/'validation'/f'{stage}_checks.json').write_text(json.dumps(checks,indent=2));print(stage,checks,flush=True);assert all(checks.values())
