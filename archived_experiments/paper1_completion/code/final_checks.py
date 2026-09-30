from pathlib import Path
import json,subprocess,datetime,hashlib
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[1];checks={}
for stage in ['development','representation','mechanism','robustness']:
 checks[stage]=all(json.loads((R/'validation'/f'{stage}_checks.json').read_text()).values())
logs=[json.loads((R/'validation'/f'{s}_run.json').read_text()) for s in ['development','representation','mechanism','robustness']]
checks['all_execution_hashes_identical']=all(x['hashes']==logs[0]['hashes'] for x in logs)
checks['original_and_sham_exact']=all(json.loads((R/'validation/baseline_equivalence.json').read_text()).values())
checks['local_gates_and_rotation']=all(json.loads((R/'validation'/f'test{b}.json').read_text())['passed'] for b in [4,8])
a=pd.read_csv(R/'run_summary.csv');main=a[(a.stage!='development')&(a.method!='none')]
checks['all_main_budgets_used']=bool((main.nonzero==main.budget).all())
checks['no_zero_signal_skip']=bool((a.fallbacks==0).all())
# Every intervention branch has the same metrics and lifetime histories strictly before its cap trigger.
m=a[a.stage=='mechanism'];checks['same_pre_cap_histories']=True
for (seed,method),g in m.groupby(['seed','method']):
 refs={}
 for _,j in g.iterrows():
  t=j.cap_time
  for suffix in ['metrics','lifetimes','learning']:
   x=pd.read_csv(R/'raw/mechanism'/f'{j.prefix}_{suffix}.csv');v=x[x.t<t].to_csv(index=False)
   if suffix not in refs:refs[suffix]=v
   else:checks['same_pre_cap_histories'] &= v==refs[suffix]
# Fixed replay set selected by protocol factors, independent of outcomes.
replay=R/'raw/replay';replay.mkdir(exist_ok=True);records=[]
choices=[('representation',lambda j:j['seed']==61000 and j['bins']==4 and j['budget']==512 and j['method']=='aligned'),('mechanism',lambda j:j['seed']==62000 and j['method']=='state_rotated' and j['intervention']==2 and j['child_eta']==.2),('robustness',lambda j:j['seed']==63000 and j['method']=='aligned' and j['setting']=='no_birth_bonus')]
for stage,pred in choices:
 j=next(j for j in json.loads((R/'validation'/f'{stage}_run.json').read_text())['runs'] if pred(j));out=replay/f'{stage}_{j["prefix"]}'
 cmd=[str(R/'code'/f'sim{j["bins"]}'),str(out),'32','20000',str(j['seed']),'.2','1','0',str(2 if j['method']=='aligned' else 6),'1','.06',str(j['mortality']),'.1841261006694567',str(j['budget']),str(j['fraction']),str(j['bonus']),str(j['intervention']),str(j['child_eta'])]
 subprocess.run(cmd,check=True,timeout=1800)
 exact={suffix:Path(str(out)+'_'+suffix).read_bytes()==(R/'raw'/stage/f'{j["prefix"]}_{suffix}').read_bytes() for suffix in ['metrics.csv','lifetimes.csv','learning.csv','updates.csv','interventions.csv','audit.json','birth_probes.csv']}
 records.append(dict(stage=stage,job=j,exact=exact))
checks['three_exact_replays']=all(all(x['exact'].values()) for x in records)
(R/'validation/replays.json').write_text(json.dumps(records,indent=2))
observations={k:checks.pop(k) for k in ['all_main_budgets_used','no_zero_signal_skip']}
(R/'validation/final_checks.json').write_text(json.dumps({'checks':checks,'observations':observations},indent=2));print(checks,observations)
assert all(checks.values())
