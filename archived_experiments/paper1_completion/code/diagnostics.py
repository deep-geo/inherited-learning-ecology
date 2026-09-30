from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];a=pd.read_csv(R/'run_summary.csv');rows=[]
for _,j in a[(a.stage=='robustness')&a.setting.isin(['baseline','low_child_energy','high_child_energy'])&a.method.ne('none')].iterrows():
 z=pd.read_csv(R/'raw/robustness'/f'{j.prefix}_metrics.csv');rows.append(dict(seed=j.seed,setting=j.setting,method=j.method,births=z.births.sum(),energy_deaths=z.energy_deaths.sum(),background_deaths=z.background_deaths.sum(),visits=z.visits.sum(),harvest=z.harvest.sum()))
pd.DataFrame(rows).to_csv(R/'ecology_diagnostics.csv',index=False)
