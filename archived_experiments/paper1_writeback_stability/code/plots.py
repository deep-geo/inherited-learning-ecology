import os,tempfile
from pathlib import Path
cache=Path(tempfile.gettempdir())/'paper1_stability_plot';cache.mkdir(exist_ok=True)
os.environ['MPLCONFIGDIR']=str(cache);os.environ['XDG_CACHE_HOME']=str(cache)
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];ef=pd.read_csv(R/'paired_effects.csv');s=pd.read_csv(R/'summary.csv');raw=pd.read_csv(R/'run_summary.csv')
names=['Native','Norm cap','Bounded [-.62,.42]','Bounded [-1,1]'];colors=['#8a5baf','#df8a22','#168457','#2370ac']
fig,axes=plt.subplots(1,2,figsize=(12,4.5),sharey=True)
for ax,fraction in zip(axes,[.5,.65]):
 for rule in range(4):
  g=ef[(ef.fraction==fraction)&(ef.rule==rule)&(ef.cap==-1)&(ef.metric=='time0.95')].sort_values('lam');x=np.arange(3)+(rule-1.5)*.16
  ax.errorbar(x,g.effect,yerr=[g.effect-g.low,g.high-g.effect],fmt='o',capsize=3,label=names[rule],color=colors[rule])
 ax.axhline(0,color='black',lw=.8);ax.set_xticks(range(3),['.25','.5','1']);ax.set_xlabel('Writeback coefficient');ax.set_title('Offspring energy share '+str(fraction));ax.grid(alpha=.2)
axes[0].set_ylabel('Random minus directed capped time (sweeps)');axes[1].legend(fontsize=8);fig.tight_layout()
for ext in ['png','pdf']:fig.savefig(R/f'figures/time_effects.{ext}',dpi=170)
plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(12,4.5))
for ax,metric,label in zip(axes,['max_step','max_abs_child'],['Maximum actual update L2','Maximum absolute child coordinate']):
 for mode,offset,color in [(7,-.17,'#168457'),(8,.17,'#2370ac')]:
  values=[raw[(raw['rule']==rule)&(raw['cap']==-1)&(raw['mode']==mode)][metric].max() for rule in range(4)]
  ax.bar(np.arange(4)+offset,values,.32,label='Directed' if mode==7 else 'Random',color=color)
 ax.set_yscale('log');ax.set_xticks(range(4),['Native','Norm','Box','Wide']);ax.set_ylabel(label);ax.legend();ax.grid(axis='y',alpha=.2)
fig.tight_layout();fig.savefig(R/'figures/stability.png',dpi=170);plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(12,4),sharey=True)
for ax,fraction in zip(axes,[.5,.65]):
 for mode,color in [(7,'#168457'),(8,'#2370ac')]:
  g=s[(s.fraction==fraction)&(s.rule==2)&(s.cap==1024)&(s['mode']==mode)].sort_values('lam')
  ax.plot(g.lam,g.time,'o-',color=color,label='Directed' if mode==7 else 'Random')
  for x,y,n in zip(g.lam,g.time,g.reached):ax.annotate(str(n)+'/20',(x,y),xytext=(0,5 if mode==7 else -14),textcoords='offset points',fontsize=8)
 ax.set_xlabel('Writeback coefficient');ax.set_title('Bounded, quota 1024; energy share '+str(fraction));ax.grid(alpha=.2)
axes[0].set_ylabel('Capped establishment time');axes[1].legend();fig.tight_layout();fig.savefig(R/'figures/quota.png',dpi=170);plt.close(fig)
