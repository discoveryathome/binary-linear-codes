"""Optional figure generation; matplotlib 3.10.7. Core search needs no Python packages."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'paired/manifest.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
for ax,(n,k) in zip(axes.flat,[(42,12),(45,11),(52,10),(62,11)]):
    for method,color,label in [('blind','#64748b','Ordinary mutation'),('walsh','#0891b2','Guided column search')]:
        for seed in [101,102,103]:
            row=next(x for x in data['rows'] if (x['n'],x['k'],x['start'],x['method'],x['seed'])==(n,k,'cold',method,seed))
            m=row['milestones'];xx=[x['seconds'] for x in m]+[row['seconds']];yy=[x['d'] for x in m]+[row['final_d']]
            ax.step(xx,yy,where='post',color=color,alpha=0.7,linewidth=1.5,label=label if seed==101 else None)
    ax.axhline(row['exclusion_lower'],color='#b45309',ls='--',lw=1.7,label='Published / closure frontier')
    ax.set_title(f'{k} message bits encoded into {n} bits')
    ax.set_xlabel('Search wall time (seconds)');ax.set_ylabel('Minimum distance')
    ax.set_xlim(0,15.5);ax.set_ylim(bottom=6 if n<46 else 12,top=row['exclusion_lower']+1.5)
    ax.grid(axis='y',alpha=.2)
axes[0,0].legend(loc='lower right',fontsize=8)
fig.suptitle('Fast early gains, then a gap to research progress\nThree cold starts per method; no new distance record',fontsize=16)
fig.savefig(HERE/'progress.png',dpi=170)
fig.savefig(HERE/'progress.svg')
svg=HERE/'progress.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
plt.close(fig)
