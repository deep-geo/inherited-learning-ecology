from pathlib import Path
import subprocess,json,hashlib,datetime,time,concurrent.futures,sys
import pandas as pd
R=Path(__file__).resolve().parents[1]
def command(prefix,seed=105000,mode=7,cap=1024,stop=-1,T=20000,spaced=0):
 return [str(R/'code/sim'),str(prefix),'32',str(T),str(seed),'.2','1','0',str(mode),'0','.06','.002','.02',str(cap),'.65','.2','0','.2','2',str(stop),'1',str(spaced)]
def check():
 w=R/'validation/development';w.mkdir(exist_ok=True)
 for mode in [7,8]:
  for spaced in [0,1]:
   p=w/f'm{mode}s{spaced}';subprocess.run(command(p,mode=mode,spaced=spaced,T=1000),check=True,capture_output=True)
   u=pd.read_csv(str(p)+'_updates.csv');v=pd.read_csv(str(p)+'_stability.csv');cnt=(u.write_norm>0).cumsum()
   released=u.t.map(lambda t:128*sum(t>x for x in [0,107,214,321,429,536,643,750])) if spaced else 1024
   assert (cnt<=released).all()
   assert ((u.loc[u.write_norm>0,'write_norm']-.02).abs()<1e-10).all()
   assert v.child_min.min()>=-.62-1e-10 and v.child_max.max()<=.42+1e-10
  p=w/f'compat{mode}';c=command(p,mode=mode,T=1000);c[-2]='0';subprocess.run(c,check=True,capture_output=True)
  old=w/f'old{mode}';c[0]=str(R.parent/'paper1_cutoff_diagnostic/code/sim');c[1]=str(old);subprocess.run(c[:-2],check=True,capture_output=True)
  for f in w.glob(p.name+'_*'):assert f.read_bytes()==(w/f.name.replace(p.name,old.name,1)).read_bytes()
  p=w/f'eta0{mode}';c=command(p,mode=mode,T=1000);c[5]='0';subprocess.run(c,check=True,capture_output=True)
 assert (w/'eta07_metrics.csv').read_bytes()==(w/'eta08_metrics.csv').read_bytes()
 (R/'validation/development_checks.json').write_text(json.dumps(dict(backward_exact=True,zero_learning_exact=True,release_quota=True,fixed_step=True,bounds=True),indent=2));print('CHECKS PASS',flush=True)
def formal():
 assert (R/'validation/development_checks.json').exists()
 jobs=[dict(seed=seed,mode=mode,regime=regime,cap=1024,stop=-1,spaced=spaced) for seed in range(104000,104020) for regime,spaced in [('earliest',0),('staged',1)] for mode in [7,8]]
 for i,j in enumerate(jobs):j['prefix']=f'{i:04d}'
 p=R/'validation/run.json';assert not p.exists()
 files=[R/'PROTOCOL.md',*sorted((R/'code').glob('*.cpp')),*sorted((R/'code').glob('*.hpp')),Path(__file__)]
 rec=dict(start=datetime.datetime.now(datetime.timezone.utc).isoformat(),planned=len(jobs),runs=[],hashes={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files})
 p.write_text(json.dumps(rec,indent=2))
 def one(j):
  t=time.monotonic();args={k:j[k] for k in ['seed','mode','cap','stop','spaced']};c=command(R/'raw'/j['prefix'],**args)
  z=subprocess.run(c,capture_output=True,text=True,timeout=1800)
  return dict(**j,seconds=time.monotonic()-t,exit_code=z.returncode,stderr=z.stderr)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for result in pool.map(one,jobs):
   rec['runs'].append(result);p.write_text(json.dumps(rec,indent=2));assert result['exit_code']==0,result
   if len(rec['runs'])%20==0:print(len(rec['runs']),len(jobs),flush=True)
 rec['end']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(rec,indent=2))
 print('COMPLETE',flush=True)
if __name__=='__main__':{'check':check,'formal':formal}[sys.argv[1]]()
