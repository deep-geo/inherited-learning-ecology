from pathlib import Path
import subprocess,tempfile,json,pandas as pd,numpy as np
R=Path(__file__).resolve().parents[1];checks={}
with tempfile.TemporaryDirectory(prefix='native-check-') as w:
 w=Path(w)
 def run(label,mode,lam=1,eta=.2,q=.1841261006694567):
  prefix=w/label;subprocess.run([str(R/'code/sim'),str(prefix),'16','2000','79999',str(eta),str(lam),'0',str(mode),'1','.06','.002',str(q),'-1','.5','.2','0','.2'],check=True);return prefix
 old=run('old',0);new=run('new',7);differentq=run('new_q',7,q=99);rand=run('rand',8);randq=run('rand_q',8,q=99)
 for suffix in ['metrics.csv','lifetimes.csv','learning.csv']:
  checks['original_'+suffix]=Path(str(old)+'_'+suffix).read_bytes()==Path(str(new)+'_'+suffix).read_bytes()
 for p,pq in [(new,differentq),(rand,randq)]:
  for suffix in ['metrics.csv','updates.csv','lifetimes.csv','learning.csv']:checks[p.name+'_q_invariant_'+suffix]=Path(str(p)+'_'+suffix).read_bytes()==Path(str(pq)+'_'+suffix).read_bytes()
 zeroa=run('zeroa',7,lam=0);zeror=run('zeror',8,lam=0);noa=run('noa',7,eta=0);nor=run('nor',8,eta=0)
 checks['negative_lambda0']=Path(str(zeror)+'_metrics.csv').read_bytes()==Path(str(zeroa)+'_metrics.csv').read_bytes()
 nozero=run('nozero',7,lam=0,eta=0)
 for p in [noa,nor]:checks['negative_eta0_'+p.name]=Path(str(p)+'_metrics.csv').read_bytes()==Path(str(nozero)+'_metrics.csv').read_bytes()
 for p in [new,rand]:
  z=json.loads(Path(str(p)+'_audit.json').read_text());u=pd.read_csv(str(p)+'_updates.csv');checks[p.name+'_geometry']=max(z['norm_error'],z['row_mean_error'],z['row_norm_error'],z['row_contrast_error'],z['formula_error'])<1e-10;checks[p.name+'_native_norm']=np.allclose(u.write_norm,u.candidate_norm,rtol=1e-10,atol=1e-12)
(R/'validation/implementation_checks.json').write_text(json.dumps({k:bool(v) for k,v in checks.items()},indent=2));print(checks);assert all(checks.values())
