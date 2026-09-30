from pathlib import Path
import subprocess,json,hashlib,datetime,time,concurrent.futures,sys
import pandas as pd
R=Path(__file__).resolve().parents[1]
def command(prefix,seed=103000,mode=7,cap=-1,stop=-1,T=20000):
 return [str(R/'code/sim'),str(prefix),'32',str(T),str(seed),'.2','1','0',str(mode),'0','.06','.002','.1841261006694567',str(cap),'.65','.2','0','.2','2',str(stop)]
def check():
 w=R/'validation/development';w.mkdir(exist_ok=True)
 for mode in [7,8]:
  for cap in [-1,1024]:
   p=w/f'new{mode}_{cap}';old=w/f'old{mode}_{cap}'
   subprocess.run(command(p,mode=mode,cap=cap,T=1000),check=True,capture_output=True)
   c=command(old,mode=mode,cap=cap,T=1000)[:-1];c[0]=str(R.parent/'paper1_writeback_stability/code/sim')
   subprocess.run(c,check=True,capture_output=True)
   for file in w.glob(p.name+'_*'):
    assert file.read_bytes()==(w/file.name.replace(p.name,old.name,1)).read_bytes(),file
  for stop in [0,150,750]:
   p=w/f't{stop}m{mode}';subprocess.run(command(p,mode=mode,stop=stop,T=1000),check=True,capture_output=True)
   u=pd.read_csv(str(p)+'_updates.csv');v=pd.read_csv(str(w/f'new{mode}_-1')+'_updates.csv')
   assert (u.loc[u.t>stop,'write_norm']==0).all()
   pd.testing.assert_frame_equal(u[u.t<=stop].reset_index(drop=True),v[v.t<=stop].reset_index(drop=True),check_dtype=False,check_exact=True)
   m=pd.read_csv(str(p)+'_metrics.csv');n=pd.read_csv(str(w/f'new{mode}_-1')+'_metrics.csv')
   pd.testing.assert_frame_equal(m[m.t<=stop],n[n.t<=stop],check_dtype=False,check_exact=True)
 assert (w/'t0m7_metrics.csv').read_bytes()==(w/'t0m8_metrics.csv').read_bytes()
 (R/'validation/development_checks.json').write_text(json.dumps(dict(backward_exact=True,zero_cutoff_directions_exact=True,prefix_exact=True,post_cutoff_zero=True),indent=2))
 print('CHECKS PASS',flush=True)
def formal():
 assert (R/'validation/development_checks.json').exists()
 jobs=[dict(seed=seed,mode=mode,regime=regime,cap=cap,stop=stop) for seed in range(102000,102020) for regime,cap,stop in [('continuous',-1,-1),('count1024',1024,-1),('time150',-1,150),('time750',-1,750)] for mode in [7,8]]
 for i,j in enumerate(jobs):j['prefix']=f'{i:04d}'
 p=R/'validation/run.json';assert not p.exists()
 files=[R/'PROTOCOL.md',*sorted((R/'code').glob('*.cpp')),*sorted((R/'code').glob('*.hpp')),Path(__file__)]
 rec=dict(start=datetime.datetime.now(datetime.timezone.utc).isoformat(),planned=len(jobs),runs=[],hashes={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files})
 p.write_text(json.dumps(rec,indent=2))
 def one(j):
  t=time.monotonic();args={k:j[k] for k in ['seed','mode','cap','stop']};c=command(R/'raw'/j['prefix'],**args)
  z=subprocess.run(c,capture_output=True,text=True,timeout=1800)
  return dict(**j,seconds=time.monotonic()-t,exit_code=z.returncode,stderr=z.stderr)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for result in pool.map(one,jobs):
   rec['runs'].append(result);p.write_text(json.dumps(rec,indent=2));assert result['exit_code']==0,result
   if len(rec['runs'])%20==0:print(len(rec['runs']),len(jobs),flush=True)
 rec['end']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(rec,indent=2))
 print('COMPLETE',flush=True)
if __name__=='__main__':{'check':check,'formal':formal}[sys.argv[1]]()
