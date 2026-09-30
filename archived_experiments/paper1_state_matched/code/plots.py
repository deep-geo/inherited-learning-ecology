from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/paper1-state-mpl')
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];s=pd.read_csv(R/'summary.csv');cv=pd.read_csv(R/'curves.csv');e=pd.read_csv(R/'paired_effects.csv');colors={'aligned_q':'#168457','state_rotated_q':'#2369ad','global_scrambled_q':'#bb8545','isotropic_q':'#bd4545'}
fig,axes=plt.subplots(1,3,figsize=(14,4.3))
for cond,col in colors.items():
 z=s[(s.stage=='budgets')&(s.condition==cond)].sort_values('budget');axes[0].plot(z.budget,z.reached/z.n,marker='o',color=col,label=cond);axes[1].plot(z.budget,z.capped_time,marker='o',color=col);axes[2].plot(z.budget,z.budget_exhausted/z.n,marker='o',color=col)
for ax in axes:ax.set_xscale('log',base=2);ax.set_xticks([128,256,512,1024,2048],[128,256,512,1024,2048]);ax.set_xlabel('Nonzero-update cap');ax.grid(alpha=.2)
axes[0].set_ylim(0,1.05);axes[2].set_ylim(0,1.05);axes[0].set_ylabel('Fraction reaching sustained 95% occupancy');axes[1].set_ylabel('Capped establishment time');axes[2].set_ylabel('Fraction consuming full quota');fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=4);fig.tight_layout(rect=(0,.10,1,1));fig.savefig(R/'plots/budget_curves.png',dpi=160);plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(11,4.3))
for ax,stage,B in [(axes[0],'confirmation',-1),(axes[1],'budgets',512)]:
 for cond,col in colors.items():
  z=cv[(cv.stage==stage)&(cv.budget==B)&(cv.condition==cond)].groupby('t').population.agg(['mean','std','count']);mean=z['mean']/1024;se=z['std']/np.sqrt(z['count'])/1024;ax.plot(z.index,mean,color=col,label=cond);ax.fill_between(z.index,mean-se,mean+se,color=col,alpha=.15)
 ax.set_title('No quota' if B<0 else f'Quota = {B}');ax.set_xlabel('Sweeps');ax.set_ylabel('Occupied fraction');ax.grid(alpha=.2)
fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=4);fig.tight_layout(rect=(0,.1,1,1));fig.savefig(R/'plots/occupancy_curves.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,4));z=e[(e.comparison=='aligned_q vs state_rotated_q')&(e.metric=='capped0.95')];labels=['No quota' if b<0 else str(b) for b in z.budget];ax.errorbar(z.advantage,np.arange(len(z)),xerr=[z.advantage-z.low,z.high-z.advantage],fmt='o');ax.axvline(0,color='gray',ls='--');ax.set_yticks(range(len(z)),labels);ax.set_xlabel('Capped time advantage of aligned update');ax.set_ylabel('Quota');ax.grid(alpha=.2);fig.tight_layout();fig.savefig(R/'plots/paired_effects.png',dpi=160);plt.close(fig)
