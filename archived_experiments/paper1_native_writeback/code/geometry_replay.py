from pathlib import Path
import json,subprocess,sys,tempfile,hashlib
import pandas as pd
R=Path(__file__).resolve().parents[1];rows=pd.read_csv(R/'validation/geometry_absolute_flags.csv');checks={};records=[]
with tempfile.TemporaryDirectory(prefix='native-geometry-') as wd:
 w=Path(wd)
 for name in ['sim.cpp','local_rule.hpp','rotation.hpp']:(w/name).write_bytes((R/'code'/name).read_bytes())
 p=w/'rotation.hpp';s=p.read_text().replace('#pragma once','#pragma once\n#include <cassert>\n#include <limits>')
 old='if(rn==0)check.support_error=std::max(check.support_error,rb);'
 new=old+' double tol=256*std::numeric_limits<double>::epsilon();assert(std::abs(rb-rn)<=tol*std::max(rn,1e-300));assert(std::abs(cb-cn)<=tol*std::max(rn,1e-300));assert(std::abs(mb-m)<=tol*std::max(std::sqrt(rn),1e-150));'
 assert old in s;s=s.replace(old,new);p.write_text(s)
 subprocess.run(['clang++','-O3','-std=c++17',str(w/'sim.cpp'),'-o',str(w/'sim')],check=True)
 for _,j in rows.iterrows():
  out=w/j.prefix;subprocess.run([str(w/'sim'),str(out),'32','20000',str(int(j.seed)),'.2',str(j.lam),'0','8','1','.06','.002','.1841261006694567',str(int(j.cap)),str(j.fraction),'.2','0','.2'],check=True)
  exact={suffix:Path(str(out)+'_'+suffix).read_bytes()==(R/'raw/confirmation'/f'{j.prefix}_{suffix}').read_bytes() for suffix in ['metrics.csv','updates.csv','lifetimes.csv','learning.csv','audit.json','interventions.csv','birth_probes.csv']}
  checks[j.prefix]=all(exact.values());records.append(dict(prefix=j.prefix,per_row_relative_assertions=True,tolerance_multiple_of_machine_epsilon=256,exact=exact))
(R/'validation/geometry_replay.json').write_text(json.dumps(dict(checks=checks,records=records),indent=2));print(checks);assert all(checks.values())
