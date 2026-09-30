from pathlib import Path
import json,subprocess
R=Path(__file__).resolve().parents[1]
checks={k:all(json.loads((R/'validation'/f'{k}.json').read_text()).values()) for k in ['implementation_checks','development_checks','confirmation_checks']}
a=json.loads((R/'validation/development_run.json').read_text());b=json.loads((R/'validation/confirmation_run.json').read_text());checks['same_frozen_hashes']=a['hashes']==b['hashes']
folder=R/'raw/replay';folder.mkdir(exist_ok=True);records=[]
for method,fraction,lam,cap in [('aligned',.5,1,-1),('state_rotated',.65,.5,1024)]:
 j=next(x for x in b['runs'] if x['seed']==81000 and (x['method'],x['fraction'],x['lam'],x['cap'])==(method,fraction,lam,cap));out=folder/j['prefix']
 subprocess.run([str(R/'code/sim'),str(out),'32','20000',str(j['seed']),'.2',str(lam),'0',str(8 if method=='state_rotated' else 7),'1','.06','.002','.1841261006694567',str(cap),str(fraction),'.2','0','.2'],check=True)
 exact={suffix:Path(str(out)+'_'+suffix).read_bytes()==(R/'raw/confirmation'/f'{j["prefix"]}_{suffix}').read_bytes() for suffix in ['metrics.csv','updates.csv','lifetimes.csv','learning.csv','audit.json','interventions.csv','birth_probes.csv']};records.append(dict(job=j,exact=exact))
checks['two_exact_replays']=all(all(r['exact'].values()) for r in records)
import pandas as pd
a=pd.read_csv(R/'run_summary.csv');prefix_checks={}
for (seed,fraction,lam,method),g in a[(a.stage=='confirmation')&(a.method!='none')].groupby(['seed','fraction','lam','method']):
 def prefix(path):
  lines=[];count=0
  with path.open() as f:
   lines.append(next(f))
   for line in f:
    lines.append(line);count+=float(line.split(',')[3])>0
    if count==1024:break
  return lines
 paths=[R/'raw/confirmation'/f'{j.prefix}_updates.csv' for _,j in g.sort_values('cap').iterrows()]
 prefix_checks[f'{seed}_{fraction}_{lam}_{method}']=prefix(paths[0])==prefix(paths[1])
checks['same_pre_cap_update_histories']=all(prefix_checks.values());(R/'validation/cap_prefix_checks.json').write_text(json.dumps(prefix_checks,indent=2))
(R/'validation/replays.json').write_text(json.dumps(records,indent=2));(R/'validation/final_checks.json').write_text(json.dumps(checks,indent=2));print(checks);assert all(checks.values())
