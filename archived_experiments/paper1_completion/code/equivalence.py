from pathlib import Path
import tempfile,subprocess,json
R=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='paper1-equivalence-') as temp:
 w=Path(temp);old=w/'old';subprocess.run(['clang++','-O3','-std=c++17',str(R/'code/reference/sim.cpp'),'-o',str(old)],check=True)
 args=['32','20000','52000','.2','1','0','2','1','.06','.002','.1841261006694567','512','.5','.2']
 subprocess.run([str(old),str(w/'old_run'),*args],check=True)
 subprocess.run([str(R/'code/sim8'),str(w/'new_run'),*args,'0','.2'],check=True)
 subprocess.run([str(R/'code/sim8'),str(w/'sham_run'),*args,'1','.2'],check=True)
 checks={}
 for suffix in ['metrics.csv','updates.csv','lifetimes.csv','learning.csv']:
  x=(w/f'new_run_{suffix}').read_bytes();checks['original_'+suffix]=x==(w/f'old_run_{suffix}').read_bytes();checks['sham_'+suffix]=x==(w/f'sham_run_{suffix}').read_bytes()
 (R/'validation/baseline_equivalence.json').write_text(json.dumps(checks,indent=2));print(checks);assert all(checks.values())
