from pathlib import Path
import subprocess,time,json,datetime,hashlib,concurrent.futures,sys
R=Path(__file__).resolve().parents[1];stage=sys.argv[1];q=.1841261006694567
conditions=[('aligned_q',2,1),('state_rotated_q',6,1),('global_scrambled_q',3,1),('isotropic_q',4,1)]
first,n={'development':(50000,5),'confirmation':(51000,20),'budgets':(52000,20),'replay':(52000,1)}[stage]
budgets={'development':[-1,512],'confirmation':[-1],'budgets':[128,256,512,1024,2048],'replay':[512]}[stage]
if stage=='replay':conditions=conditions[:2]
if stage=='development':subprocess.run(['clang++','-O3','-std=c++17',str(R/'code/sim.cpp'),'-o',str(R/'code/sim')],check=True)
folder=R/'raw'/stage;folder.mkdir(exist_ok=True);log=R/'validation'/f'{stage}_run.json';assert not log.exists()
record={'stage':stage,'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'code/sim.cpp',R/'code/rotation.hpp',R/'code/local_rule.hpp',R/'PROTOCOL.md']},'runs':[]};log.write_text(json.dumps(record,indent=2))
def one(job):
 seed,cond,B=job;name,mode,lam=cond;prefix=f'b{B}_{name}_{seed}';t=time.monotonic();cmd=[str(R/'code/sim'),str(folder/prefix),'32','20000',str(seed),'.2',str(lam),'0',str(mode),'1','.06','.002',str(q),str(B),'.5','.2'];p=subprocess.run(cmd,capture_output=True,text=True,timeout=1800);return dict(seed=seed,condition=name,budget=B,prefix=prefix,q=q,exit_code=p.returncode,elapsed_seconds=time.monotonic()-t,stderr=p.stderr)
jobs=[(s,c,b) for s in range(first,first+n) for b in budgets for c in conditions]
if stage!='replay':jobs += [(s,('none',0,0),0) for s in range(first,first+n)]
t=time.monotonic()
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for z in ex.map(one,jobs):record['runs'].append(z);log.write_text(json.dumps(record,indent=2));assert z['exit_code']==0,z
record.update(end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-t);log.write_text(json.dumps(record,indent=2));print(stage,len(record['runs']),record['elapsed_seconds'])
