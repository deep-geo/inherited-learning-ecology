from pathlib import Path
import json,pandas as pd,numpy as np,sys
R=Path(__file__).resolve().parents[1];stage=sys.argv[1];log=json.loads((R/'validation'/f'{stage}_run.json').read_text());checks={'all_runs_complete':True,'population_balance':True,'energy_split_norm':True,'row_matching':True,'zero_unreachable_in_main_pair':True,'budget_ledger':True,'complete_metrics':True}
for job in log['runs']:
 p=R/'raw'/stage/job['prefix'];a=json.loads(Path(str(p)+'_audit.json').read_text());x=pd.read_csv(str(p)+'_metrics.csv');b=pd.read_csv(str(p)+'_updates.csv');life=pd.read_csv(str(p)+'_lifetimes.csv')
 checks['all_runs_complete'] &= job['exit_code']==0
 checks['population_balance'] &= bool(np.array_equal(x.population.diff().iloc[1:],(x.births-x.background_deaths-x.energy_deaths).iloc[1:])) and len(life[life.status!='censored'])==x.background_deaths.sum()+x.energy_deaths.sum()
 checks['energy_split_norm'] &= max(a['energy_error'],a['split_error'],a['norm_error'])<1e-10
 checks['row_matching'] &= max(a['row_mean_error'],a['row_norm_error'],a['row_contrast_error'],a['empty_support_error'])<1e-12
 if job['condition'] in ['aligned_q','state_rotated_q']:checks['zero_unreachable_in_main_pair'] &= a['unreachable_sq']==0
 B=job['budget'];checks['budget_ledger'] &= (B<0 or a['nonzero']<=B) and len(b)==a['births_total'] and int((b.write_norm>0).sum())==a['nonzero'] and np.isclose(b.write_norm.sum(),a['sum_norm'],rtol=1e-10,atol=1e-10) and np.isclose(a['sum_sq'],a['contrast_sq']+a['common_sq'],rtol=1e-10,atol=1e-10)
 if job['condition']!='none':checks['budget_ledger'] &= np.isclose(a['sum_norm'],a['nonzero']*job['q'],rtol=1e-10,atol=1e-10)
 checks['complete_metrics'] &= x.t.iloc[-1]==20000 and len(x)==101 and bool(np.isfinite(x.drop(columns=['genotype_rms','mean_depth','mean_parent_visits'])).all().all())
if stage=='replay':
 checks['exact_replays']=all((R/'raw/replay'/f"b512_{name}_52000_{suffix}").read_bytes()==(R/'raw/budgets'/f"b512_{name}_52000_{suffix}").read_bytes() for name in ['aligned_q','state_rotated_q'] for suffix in ['metrics.csv','lifetimes.csv','learning.csv','updates.csv'])
checks={k:bool(v) for k,v in checks.items()};(R/'validation'/f'{stage}_checks.json').write_text(json.dumps(checks,indent=2));print(checks);assert all(checks.values())
