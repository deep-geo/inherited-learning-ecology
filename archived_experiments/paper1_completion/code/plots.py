from pathlib import Path
import os,tempfile
_cache=Path(tempfile.gettempdir())/"paper1_completion_plot_cache"
_cache.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR",str(_cache))
os.environ.setdefault("XDG_CACHE_HOME",str(_cache))
import pandas as pd,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];s=pd.read_csv(R/'summary.csv');e=pd.read_csv(R/'paired_effects.csv');c=pd.read_csv(R/'curves.csv');colors={'aligned':'#168457','state_rotated':'#2369ad','none':'#888888'}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})
a=s[s.stage=='representation'];fig,ax=plt.subplots(1,2,figsize=(11,4),layout='constrained')
labels=[];positions=[]
for i,(bins,B) in enumerate([(8,512),(4,512),(8,1024),(4,1024)]):
 labels.append(f'{bins}x{bins} states\nB={B}');positions.append(i)
 for k,method in enumerate(['aligned','state_rotated']):
  row=a[(a.bins==bins)&(a.budget==B)&(a.method==method)].iloc[0];x=i+(k-.5)*.32
  ax[0].bar(x,row.capped_time,.3,color=colors[method],label=method if i==0 else None)
  ax[1].bar(x,row.reached/row.n,.3,color=colors[method]);ax[1].text(x,row.reached/row.n+.015,f'{int(row.reached)}/20',ha='center',fontsize=8)
for p in ax:p.set_xticks(positions,labels);p.grid(axis='y',alpha=.2);p.set_axisbelow(True)
ax[0].set_ylabel('Capped establishment time (sweeps)');ax[0].legend();ax[1].set_ylabel('Fraction reaching sustained 95% occupancy');ax[1].set_ylim(0,1.12);fig.savefig(R/'plots/representation.png');plt.close(fig)
a=s[s.stage=='mechanism'];fig,axes=plt.subplots(2,3,figsize=(13,7),layout='constrained')
for col,eta in enumerate([0,.2,.8]):
 for k,method in enumerate(['aligned','state_rotated']):
  g=a[(a.child_eta==eta)&(a.method==method)].sort_values('intervention');x=np.arange(2)+(k-.5)*.3
  axes[0,col].bar(x,g.capped_time,.28,color=colors[method],label=method)
  axes[1,col].bar(x,g.auc,.28,color=colors[method])
  for xx,(_,row) in zip(x,g.iterrows()):axes[0,col].text(xx,row.capped_time+200,f'{int(row.reached)}/20',ha='center',fontsize=8)
 axes[0,col].set_title(f'Post-budget offspring learning rate = {eta}')
 for p in axes[:,col]:p.set_xticks([0,1],['Keep preference','Erase preference']);p.grid(axis='y',alpha=.2);p.set_axisbelow(True)
 axes[0,col].set_ylim(0,22500);axes[1,col].set_ylim(0,1.05)
axes[0,0].set_ylabel('Capped establishment time');axes[1,0].set_ylabel('Mean occupancy over full trajectory');axes[0,0].legend(loc='upper left',fontsize=8);fig.savefig(R/'plots/mechanism.png');plt.close(fig)
a=s[(s.stage=='robustness')&(s.method!='none')];order=['baseline','low_death','high_death','low_child_energy','high_child_energy','no_birth_bonus'];labels=['Baseline','Death .0005','Death .01','Child share .35','Child share .65','Birth bonus 0'];fig,axes=plt.subplots(2,1,figsize=(11,7),layout='constrained')
for k,method in enumerate(['aligned','state_rotated']):
 g=a[a.method==method].set_index('setting').loc[order];x=np.arange(6)+(k-.5)*.32
 axes[0].bar(x,g.capped_time,.3,color=colors[method],label=method);axes[1].bar(x,g.auc,.3,color=colors[method])
 for xx,(_,row) in zip(x,g.iterrows()):axes[0].text(xx,row.capped_time+200,f'{int(row.reached)}/20',ha='center',fontsize=8)
for p in axes:p.set_xticks(np.arange(6),labels);p.grid(axis='y',alpha=.2);p.set_axisbelow(True)
axes[0].set_ylim(0,22500);axes[1].set_ylim(0,1.05);axes[0].legend();axes[0].set_ylabel('Capped establishment time');axes[1].set_ylabel('Mean occupancy over full trajectory');fig.savefig(R/'plots/robustness.png');plt.close(fig)
# Full trajectories for the main mechanistic test, with seed-mean standard errors.
v=c[(c.stage=='mechanism')&(c.child_eta==.2)];fig,ax=plt.subplots(figsize=(9,4),layout='constrained')
for (method,iv),g in v.groupby(['method','intervention']):
 z=g.groupby('t').population.agg(['mean','std','count']);x=z.index.to_numpy();y=z['mean'].to_numpy()/1024;se=(z['std']/np.sqrt(z['count'])).to_numpy()/1024
 ax.plot(x,y,color=colors[method],ls='-' if iv==1 else '--',label=f'{method}, '+('keep' if iv==1 else 'erase'));ax.fill_between(x,y-se,y+se,color=colors[method],alpha=.08)
ax.set(xlabel='Sweeps',ylabel='Occupancy',ylim=(0,1.03));ax.legend(fontsize=9);fig.savefig(R/'plots/mechanism_trajectories.png');plt.close(fig)
print('Four figures saved')
