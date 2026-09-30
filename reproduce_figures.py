from pathlib import Path
import os, sys
R=Path(__file__).resolve().parent
O=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else R
(O/'figures').mkdir(parents=True,exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR',str(O/'mpl_cache'))
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
s=pd.read_csv(R/'data/state_matched_summary.csv')
c=pd.read_csv(R/'data/completion_summary.csv')
e=pd.read_csv(R/'data/native_writeback_paired_effects.csv')
rows=s[(s.stage=='budgets')&(s.budget==512)].set_index('condition').loc[['aligned_q','state_rotated_q','global_scrambled_q','isotropic_q']]
mm=c[(c.stage=='mechanism')&c.child_eta.isin([.2,.8])]
vals=[]
for method in ['aligned','state_rotated']:
 vals.append([mm[(mm.method==method)&(mm.child_eta==eta)&(mm.intervention==iv)].iloc[0].capped_time for eta,iv in [(.2,1),(.2,2),(.8,1),(.8,2)]])
g=e[e.metric=='capped0.95'].sort_values(['fraction','lam'])
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(7,4));ax.bar(range(4),rows.capped_time,color=['#235f95','#d07a21','#8e99a4','#abb3bc']);ax.set_xticks(range(4),['Directed','State rotation','Global shuffle','Isotropic']);ax.set_ylabel('Capped establishment time (sweeps)');ax.set_ylim(0,22000)
for i,(_,r) in enumerate(rows.iterrows()):ax.text(i,r.capped_time+300,f'{int(r.reached)}/20',ha='center')
fig.tight_layout();fig.savefig(O/'figures/control.pdf');fig.savefig(O/'figures/control.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4));xx=np.arange(4)
for v,off,col,label in zip(vals,[-.18,.18],['#235f95','#d07a21'],['Directed','State rotation']):ax.bar(xx+off,v,.36,color=col,label=label)
ax.set_xticks(xx,['Keep .2','Erase .2','Keep .8','Erase .8']);ax.set_ylabel('Capped establishment time (sweeps)');ax.legend();fig.tight_layout();fig.savefig(O/'figures/mechanism.pdf');fig.savefig(O/'figures/mechanism.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4.5))
for cap,col,shift,label in [(-1,'#235f95',.1,'Continuous'),(1024,'#d07a21',-.1,'1024 updates')]:
 gg=g[g.cap==cap];v=gg.effect.to_numpy();ax.errorbar(v,np.arange(6)+shift,xerr=np.array([v-gg.low.to_numpy(),gg.high.to_numpy()-v]),fmt='o',color=col,label=label)
ax.axvline(0,color='gray',ls='--');ax.set_yticks(range(6),['.50 / .25','.50 / .50','.50 / 1.0','.65 / .25','.65 / .50','.65 / 1.0']);ax.set_ylabel('Offspring energy share / writeback strength');ax.set_xlabel('Random minus directed capped time (sweeps)');ax.legend();fig.tight_layout();fig.savefig(O/'figures/native.pdf');fig.savefig(O/'figures/native.png',dpi=180);plt.close(fig)
