from pathlib import Path
import subprocess,json,hashlib,datetime,time,concurrent.futures,sys
R=Path(__file__).resolve().parents[1];stage=sys.argv[1];first,n={'development':(80000,2),'confirmation':(81000,20)}[stage];jobs=[]
for seed in range(first,first+n):
 for fraction in [.5,.65]:
  for cap in [-1,1024]:
   for lam in [.25,.5,1]:
    for method in ['aligned','state_rotated']:jobs.append(dict(seed=seed,fraction=fraction,cap=cap,lam=lam,method=method))
  jobs.append(dict(seed=seed,fraction=fraction,cap=-1,lam=0,method='none'))
folder=R/'raw'/stage;folder.mkdir(exist_ok=True);path=R/'validation'/f'{stage}_run.json';assert not path.exists()
record=dict(start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),planned=len(jobs),hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'PROTOCOL.md',*sorted((R/'code').glob('*.cpp')),*sorted((R/'code').glob('*.hpp')),R/'code/run.py']},runs=[])
for i,j in enumerate(jobs):j['prefix']=f'{i:04d}_{j["method"]}_{j["seed"]}'
def one(j):
 cmd=[str(R/'code/sim'),str(folder/j['prefix']),'32','20000',str(j['seed']),'.2',str(j['lam']),'0',str(8 if j['method']=='state_rotated' else 7),'1','.06','.002','.1841261006694567',str(j['cap']),str(j['fraction']),'.2','0','.2'];t=time.monotonic();z=subprocess.run(cmd,capture_output=True,text=True,timeout=1800);return dict(**j,exit_code=z.returncode,seconds=time.monotonic()-t,stderr=z.stderr)
t=time.monotonic();path.write_text(json.dumps(record,indent=2))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for j in pool.map(one,jobs):
  record['runs'].append(j);path.write_text(json.dumps(record,indent=2));assert j['exit_code']==0,j
  if len(record['runs'])%40==0:print(stage,len(record['runs']),len(jobs),flush=True)
record.update(end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),seconds=time.monotonic()-t);path.write_text(json.dumps(record,indent=2));print(stage,'DONE',len(jobs),flush=True)
