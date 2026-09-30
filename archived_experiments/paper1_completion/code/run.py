from pathlib import Path
import subprocess,sys,json,hashlib,datetime,time,concurrent.futures
R=Path(__file__).resolve().parents[1]
q=.1841261006694567
settings={'baseline':{},'low_death':{'mortality':.0005},'high_death':{'mortality':.01},'low_child_energy':{'fraction':.35},'high_child_energy':{'fraction':.65},'no_birth_bonus':{'bonus':0}}
def jobs_for(stage,seeds):
 out=[]
 def add(seed,**kw):
  j=dict(seed=seed,bins=8,budget=1024,method='aligned',setting='baseline',mortality=.002,fraction=.5,bonus=.2,intervention=0,child_eta=.2)
  j.update(kw);out.append(j)
 for seed in seeds:
  if stage=='representation':
   for bins in [8,4]:
    for B in [512,1024]:
     for method in ['aligned','state_rotated']:add(seed,bins=bins,budget=B,method=method)
    add(seed,bins=bins,budget=0,method='none')
  elif stage=='mechanism':
   for method in ['aligned','state_rotated']:
    for intervention in [1,2]:
     for eta in [0,.2,.8]:add(seed,budget=512,method=method,intervention=intervention,child_eta=eta)
  elif stage=='robustness':
   for setting,kw in settings.items():
    for method in ['aligned','state_rotated','none']:add(seed,setting=setting,method=method,budget=0 if method=='none' else 1024,**kw)
 return out
stage=sys.argv[1]
if stage=='development':
 jobs=[]
 for st in ['representation','mechanism','robustness']:
  for j in jobs_for(st,range(60000,60002)):j['family']=st;jobs.append(j)
else:
 first={'representation':61000,'mechanism':62000,'robustness':63000}[stage];jobs=jobs_for(stage,range(first,first+20))
folder=R/'raw'/stage;folder.mkdir(exist_ok=True);log=R/'validation'/f'{stage}_run.json';assert not log.exists(),'refuse overwrite'
for i,j in enumerate(jobs):j['prefix']=f'{i:04d}_{j["method"]}_{j["seed"]}'
record=dict(stage=stage,start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),planned=len(jobs),hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'PROTOCOL.md',*sorted((R/'code').glob('*.cpp')),*sorted((R/'code').glob('*.hpp')),R/'code/run.py']},runs=[])
def save():log.write_text(json.dumps(record,indent=2))
save()
def one(j):
 cmd=[str(R/'code'/f'sim{j["bins"]}'),str(folder/j['prefix']),'32','20000',str(j['seed']),'.2','0' if j['method']=='none' else '1','0',str({'aligned':2,'state_rotated':6,'none':0}[j['method']]),'1','.06',str(j['mortality']),str(q),str(j['budget']),str(j['fraction']),str(j['bonus']),str(j['intervention']),str(j['child_eta'])]
 t=time.monotonic();z=subprocess.run(cmd,capture_output=True,text=True,timeout=1800)
 return dict(**j,exit_code=z.returncode,seconds=time.monotonic()-t,stderr=z.stderr)
t=time.monotonic()
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for j in pool.map(one,jobs):
  record['runs'].append(j);save();assert j['exit_code']==0,j
  if len(record['runs'])%40==0:print(stage,len(record['runs']),len(jobs),flush=True)
record.update(end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),seconds=time.monotonic()-t);save();print(stage,'DONE',len(jobs),record['seconds'],flush=True)
