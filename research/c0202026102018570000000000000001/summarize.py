import json,re,statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def run():
    phases={phase:json.loads((HERE/phase/'manifest.json').read_text()) for phase in ['paired','heldout','coset','qc']}
    assert [len(phases[p]['rows']) for p in phases]==[48,16,18,9]
    targets={(x['n'],x['k']):x for x in json.loads((ROOT/'data/targets.json').read_text())}
    out=dict(phases={},candidate_distance_records=[],heldout_pairs=[])
    for phase,data in phases.items():
        rows=data['rows'];peak=[]
        for r in rows:
            if r['final_d']>targets[r['n'],r['k']]['closure_lower']:out['candidate_distance_records'].append(r['object'])
            resource=(ROOT/r['resource']).read_text();m=re.search(r'(\d+)\s+maximum resident set size',resource)
            if m:peak.append(int(m.group(1)))
        out['phases'][phase]=dict(runs=len(rows),search_steps=sum(r['steps'] for r in rows),
              cpu_seconds=sum(r['cpu_seconds'] for r in rows),search_wall_seconds=sum(r['seconds'] for r in rows),
              max_search_RSS_bytes=max(peak) if peak else None)
    ratios=[]
    for n,k in [(42,12),(45,11),(52,10),(62,11)]:
        for seed in [901,902]:
            pair={r['method']:r for r in phases['heldout']['rows'] if r['n']==n and r['seed']==seed}
            a,b=pair['blind'],pair['walsh'];ratio=a['minimum_words']/b['minimum_words'];ratios.append(ratio)
            out['heldout_pairs'].append(dict(n=n,k=k,seed=seed,blind_d=a['final_d'],guided_d=b['final_d'],
                blind_minimum_words=a['minimum_words'],guided_minimum_words=b['minimum_words'],multiplicity_ratio=ratio))
    out['heldout_distance_wins']=sum(x['guided_d']>x['blind_d'] for x in out['heldout_pairs'])
    out['heldout_distance_ties']=sum(x['guided_d']==x['blind_d'] for x in out['heldout_pairs'])
    out['heldout_multiplicity_wins']=sum(x['multiplicity_ratio']>1 for x in out['heldout_pairs'])
    out['heldout_median_multiplicity_ratio']=statistics.median(ratios)
    out['paired_cold']={}
    for method in ['blind','walsh']:
        rows=[r for r in phases['paired']['rows'] if r['method']==method and r['start']=='cold']
        out['paired_cold'][method]=dict(runs=len(rows),known_distance_matches=sum(r['final_d']==r['exclusion_lower'] for r in rows),
            median_distance_gain=statistics.median(r['final_d']-r['initial_d'] for r in rows),
            median_remaining_gap=statistics.median(r['exclusion_lower']-r['final_d'] for r in rows))
    out['target_results']=[]
    for n,k in [(42,12),(44,11),(45,11),(52,10),(62,11)]:
        rows=[r for phase in phases.values() for r in phase['rows'] if (r['n'],r['k'])==(n,k)]
        t=targets[n,k]
        out['target_results'].append(dict(n=n,k=k,published_lower=t['published_lower'],closure_lower=t['closure_lower'],
            upper=t['upper'],best_observed=max(r['final_d'] for r in rows),search_runs=len(rows)))
    out['total_runs']=sum(x['runs'] for x in out['phases'].values())
    out['total_cpu_seconds']=sum(x['cpu_seconds'] for x in out['phases'].values())
    out['total_search_wall_seconds']=sum(x['search_wall_seconds'] for x in out['phases'].values())
    (HERE/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':run()
