from pathlib import Path
import os,tempfile
cache=Path(tempfile.gettempdir())/'paper1-native-cache';cache.mkdir(exist_ok=True);os.environ.setdefault('MPLCONFIGDIR',str(cache));os.environ.setdefault('XDG_CACHE_HOME',str(cache))
import pandas as pd,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];s=pd.read_csv(R/'summary.csv');s=s[(s.stage=='confirmation')&(s.method!='none')];c=pd.read_csv(R/'curves.csv');e=pd.read_csv(R/'paired_effects.csv');colors={'aligned':'#168457','state_rotated':'#2369ad'}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})
for metric,ylabel,name,lim in [('capped_time','Capped establishment time (sweeps)','establishment',(0,22000)),('auc','Mean occupancy over full trajectory','occupancy',(0,1.08)),('sum_norm','Cumulative hereditary L2 displacement','variation_budget',None)]:
 fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
 for row,fraction in enumerate([.5,.65]):
  for col,cap in enumerate([-1,1024]):
   ax=axes[row,col];g=s[(s.fraction==fraction)&(s.cap==cap)]
   for k,method in enumerate(['aligned','state_rotated']):
    z=g[g.method==method].sort_values('lam');pos=np.arange(3)+(k-.5)*.32;ax.bar(pos,z[metric],.3,color=colors[method],label=method)
    if metric=='capped_time':
     for xx,(_,v) in zip(pos,z.iterrows()):ax.text(xx,v[metric]+200,f'{int(v.reached)}/20',ha='center',fontsize=8)
   ax.set_xticks(range(3),['.25','.5','1']);ax.set_xlabel('Writeback coefficient lambda');ax.set_title(f'Child energy share {fraction}; '+('no cap' if cap<0 else 'cap 1024'))
   ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
   if lim:ax.set_ylim(*lim)
   if col==0:ax.set_ylabel(ylabel)
 axes[0,0].legend(fontsize=8);fig.savefig(R/'plots'/f'{name}.png');plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
for ax,fraction in zip(axes,[.5,.65]):
 for method in ['aligned','state_rotated']:
  for lam,ls in [(.25,':'),(.5,'--'),(1,'-')]:
   v=c[(c.stage=='confirmation')&(c.fraction==fraction)&(c.cap==-1)&(c.lam==lam)&(c.method==method)];z=v.groupby('t').population.mean()/1024;ax.plot(z.index,z,color=colors[method],ls=ls,label=f'{method}, lambda={lam}')
 ax.set(title=f'Child energy share {fraction}, no cap',xlabel='Sweeps',ylabel='Occupancy',ylim=(0,1.03));ax.grid(alpha=.15)
axes[1].legend(fontsize=8);fig.savefig(R/'plots/trajectories.png');plt.close(fig)
print('Four figures saved')
