from pathlib import Path
import subprocess,json,hashlib,datetime,time,concurrent.futures,sys
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1]
def command(prefix,seed=100000,fraction=.65,lam=1,mode=8,rule=2,cap=-1,T=20000,eta=.2):
 return [str(R/'code/sim'),str(prefix),'32',str(T),str(seed),str(eta),str(lam),'0',str(mode),'0','.06','.002','.1841261006694567',str(cap),str(fraction),'.2','0',str(eta),str(rule)]
def check():
 checks={};w=R/'validation/development';w.mkdir(exist_ok=True)
 for rule in range(4):
  for mode in [7,8]:
   p=w/f'r{rule}m{mode}';subprocess.run(command(p,rule=rule,mode=mode,T=1200),check=True,capture_output=True)
   s=pd.read_csv(str(p)+'_stability.csv');u=pd.read_csv(str(p)+'_updates.csv')
   assert np.isfinite(s).all().all() and np.allclose(u.write_norm,np.where(u.allowed,s.post_a,0),rtol=1e-9,atol=1e-10)
   if rule:
    assert np.allclose(s.post_a,s.post_r,rtol=1e-9,atol=1e-10)
    assert s.post_a.max()<=.1841261006694567+1e-10
   if rule>=2:
    lo,hi=(-.62,.42) if rule==2 else (-1,1)
    assert s.child_min.min()>=lo-1e-10 and s.child_max.max()<=hi+1e-10
   if rule==0:
    old=w/f'old{mode}';cmd=command(old,rule=rule,mode=mode,T=1200)[:-1];cmd[0]=str(R.parent/'paper1_native_writeback/code/sim');subprocess.run(cmd,check=True,capture_output=True)
    for suffix in ['metrics.csv','updates.csv','audit.json','lifetimes.csv','learning.csv','interventions.csv','birth_probes.csv']:
     assert Path(str(p)+'_'+suffix).read_bytes()==Path(str(old)+'_'+suffix).read_bytes()
 checks['native_seven_outputs_exact']=True;checks['development_bounds_and_geometry']=True
 for eta,lam,name in [(.2,0,'lambda0'),(0,1,'eta0')]:
  paths=[]
  for rule in [0,2]:
   for mode in [7,8]:
    p=w/f'{name}_{rule}_{mode}';subprocess.run(command(p,eta=eta,lam=lam,rule=rule,mode=mode,T=1200),check=True,capture_output=True);paths.append(Path(str(p)+'_metrics.csv').read_bytes())
  assert all(x==paths[0] for x in paths);checks[name+'_exact']=True
 (R/'validation/development_checks.json').write_text(json.dumps(checks,indent=2));print(checks,flush=True)
def formal():
 assert (R/'validation/development_checks.json').exists()
 jobs=[]
 for seed in range(101000,101020):
  for fraction in [.5,.65]:
   for lam in [.25,.5,1]:
    for rule in range(4):
     for cap in ([-1,1024] if rule==2 else [-1]):
      for mode in [7,8]:jobs.append(dict(seed=seed,fraction=fraction,lam=lam,rule=rule,cap=cap,mode=mode))
 for i,j in enumerate(jobs):j['prefix']=f'{i:04d}'
 p=R/'validation/run.json';assert not p.exists()
 rec=dict(start=datetime.datetime.now(datetime.timezone.utc).isoformat(),planned=len(jobs),runs=[],hashes={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [R/'PROTOCOL.md',*sorted((R/'code').glob('*.cpp')),*sorted((R/'code').glob('*.hpp')),Path(__file__)]})
 def one(j):
  args={k:v for k,v in j.items() if k!='prefix'};t=time.monotonic();z=subprocess.run(command(R/'raw'/j['prefix'],**args),capture_output=True,text=True,timeout=1800)
  return dict(**j,seconds=time.monotonic()-t,exit_code=z.returncode,stderr=z.stderr)
 p.write_text(json.dumps(rec,indent=2))
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for result in pool.map(one,jobs):
   rec['runs'].append(result);p.write_text(json.dumps(rec,indent=2))
   assert result['exit_code']==0,result
   if len(rec['runs'])%40==0:print(len(rec['runs']),len(jobs),flush=True)
 rec['end']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(rec,indent=2));print('COMPLETE',flush=True)
if __name__=='__main__':{'check':check,'formal':formal}[sys.argv[1]]()
