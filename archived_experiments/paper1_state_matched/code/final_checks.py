from pathlib import Path
import json,pandas as pd,numpy as np
R=Path(__file__).resolve().parents[1];checks={}
for stage in ['development','confirmation','budgets','replay']:checks[stage]=all(json.loads((R/'validation'/f'{stage}_checks.json').read_text()).values())
logs=[json.loads((R/'validation'/f'{s}_run.json').read_text()) for s in ['development','confirmation','budgets','replay']];checks['frozen_hashes_unchanged']=all(l['hashes']==logs[0]['hashes'] for l in logs)
checks['budget_shared_prefix']=True
for seed in range(52000,52020):
 for cond in ['aligned_q','state_rotated_q','global_scrambled_q','isotropic_q']:
  ref=pd.read_csv(R/'raw/budgets'/f'b128_{cond}_{seed}_updates.csv',nrows=128)
  for B in [256,512,1024,2048]:
   a=pd.read_csv(R/'raw/budgets'/f'b{B}_{cond}_{seed}_updates.csv',nrows=128);checks['budget_shared_prefix'] &= a.equals(ref)
x=pd.read_csv(R/'run_summary.csv');pair=x[(x.stage=='budgets')&x.condition.isin(['aligned_q','state_rotated_q'])];checks['main_pair_all_quotas_used']=bool(pair.budget_exhausted.all());checks['zero_signal_skips_absent']=bool(x.zero_signal_skips.eq(0).all());checks['main_pair_unreachable_zero']=bool(x[x.condition.isin(['aligned_q','state_rotated_q'])].unreachable_sq.eq(0).all())
(R/'validation/final_checks.json').write_text(json.dumps(checks,indent=2));print(checks);assert all(checks.values())
print('max row errors',x[['row_mean_error','row_norm_error','row_contrast_error','support_error']].max().to_dict())
