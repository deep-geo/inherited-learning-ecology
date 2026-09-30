from pathlib import Path
import json,subprocess
import pandas as pd
from run import command
R=Path(__file__).resolve().parents[1];rec=json.loads((R/'validation/run.json').read_text());assert 'end' in rec
replays=[]
for rule,mode in [(0,8),(1,8),(2,7),(2,8),(3,8)]:
 j=next(j for j in rec['runs'] if j['seed']==101000 and j['fraction']==.65 and j['lam']==1 and j['rule']==rule and j['mode']==mode and j['cap']==-1)
 out=R/'validation'/f'replay_{rule}_{mode}'
 subprocess.run(command(out,**{k:j[k] for k in ['seed','fraction','lam','rule','mode','cap']}),check=True,capture_output=True)
 for suffix in ['metrics.csv','updates.csv','audit.json','lifetimes.csv','learning.csv','interventions.csv','birth_probes.csv','stability.csv']:
  assert Path(str(out)+'_'+suffix).read_bytes()==Path(str(R/'raw'/j['prefix'])+'_'+suffix).read_bytes()
 replays.append(j['prefix'])
prefix_pairs=0
for j in rec['runs']:
 if j['cap']!=1024:continue
 other=next(x for x in rec['runs'] if x['cap']==-1 and all(x[k]==j[k] for k in ['seed','fraction','lam','rule','mode']))
 a=pd.read_csv(str(R/'raw'/j['prefix'])+'_updates.csv');b=pd.read_csv(str(R/'raw'/other['prefix'])+'_updates.csv')
 stop=(a.write_norm>0).cumsum();eligible=a[stop<=1024]
 hits=a.index[stop==1024];end=int(hits[0])+1 if len(hits) else len(a)
 assert a.iloc[:end].equals(b.iloc[:end]);prefix_pairs+=1
(R/'validation/final_checks.json').write_text(json.dumps(dict(exact_eight_file_replays=replays,matched_cap_prefix_pairs=prefix_pairs),indent=2));print('Passed',replays,prefix_pairs)
