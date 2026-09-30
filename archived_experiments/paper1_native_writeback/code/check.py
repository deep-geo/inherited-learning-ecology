from pathlib import Path
import sys,json,hashlib,subprocess
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];stage=sys.argv[1];log=json.loads((R/'validation'/f'{stage}_run.json').read_text())
checks=dict(complete=len(log['runs'])==log['planned'] and 'end_utc' in log,frozen_hashes=True,population_balance=True,energy_split=True,native_norm=True,row_geometry=True,budget_ledger=True,complete_metrics=True,formula=True)
for name,h in log['hashes'].items():checks['frozen_hashes'] &= hashlib.sha256((R/name).read_bytes()).hexdigest()==h
flagged=[]
for j in log['runs']:
 p=R/'raw'/stage/j['prefix'];x=pd.read_csv(str(p)+'_metrics.csv');b=pd.read_csv(str(p)+'_updates.csv');l=pd.read_csv(str(p)+'_lifetimes.csv');a=json.loads(Path(str(p)+'_audit.json').read_text())
 checks['complete'] &= j['exit_code']==0
 checks['population_balance'] &= np.array_equal(x.population.diff().iloc[1:],(x.births-x.background_deaths-x.energy_deaths).iloc[1:]) and len(l[l.status!='censored'])==x.background_deaths.sum()+x.energy_deaths.sum() and len(l[l.status=='censored'])==x.population.iloc[-1]
 checks['energy_split'] &= max(a['energy_error'],a['split_error'])<1e-10
 checks['native_norm'] &= np.allclose(b.write_norm,np.where(b.allowed,b.candidate_norm,0),rtol=1e-10,atol=1e-12)
 checks['row_geometry'] &= a['empty_support_error']==0 and a['unreachable_sq']==0
 if max(a['row_mean_error'],a['row_norm_error'],a['row_contrast_error'])>=1e-10:flagged.append({**j,'max_norm':b.write_norm.max(),'row_norm_error':a['row_norm_error']})
 checks['formula'] &= a['formula_error']<1e-10
 checks['budget_ledger'] &= (j['cap']<0 or a['nonzero']<=j['cap']) and len(b)==a['births_total'] and int((b.write_norm>0).sum())==a['nonzero'] and np.isclose(b.write_norm.sum(),a['sum_norm'],rtol=1e-10,atol=1e-10) and np.isclose((b.write_norm**2).sum(),a['sum_sq'],rtol=1e-10,atol=1e-10) and np.isclose(a['sum_sq'],a['contrast_sq']+a['common_sq'],rtol=1e-10,atol=1e-10)
 checks['complete_metrics'] &= len(x)==101 and x.t.iloc[-1]==20000 and np.isfinite(x.drop(columns=['genotype_rms','mean_depth','mean_parent_visits'])).all().all()
if flagged:
 assert stage=='confirmation'
 pd.DataFrame(flagged).to_csv(R/'validation/geometry_absolute_flags.csv',index=False)
 gp=R/'validation/geometry_replay.json'
 if not gp.exists():subprocess.run([sys.executable,str(R/'code/geometry_replay.py')],check=True)
 result=json.loads(gp.read_text());checks['row_geometry'] &= all(result['checks'].get(j['prefix'],False) for j in flagged)
checks={k:bool(v) for k,v in checks.items()};(R/'validation'/f'{stage}_checks.json').write_text(json.dumps(checks,indent=2));print(checks);assert all(checks.values())
