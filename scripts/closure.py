"""Least fixed point of guaranteed parameter implications, n<=256.
All table bounds, including non-reconstructed ones, are novelty exclusions.
Reported recent paper parameters are conservative exclusions, not verified codes.
"""
import re,json,hashlib
from pathlib import Path
from collections import deque

BOUNDS=Path('data/extracted/codetables-bounds.json');TRIPLES=Path('data/extracted/yu2024-triples.json')

def parse_table(s):
    """Lower/upper bounds from the codetables.de full-table page (used once by extract_sources.py)."""
    out={}
    for n,k,ds in re.findall(r'HREF="BKLC.php\?q=2&n=(\d+)&k=(\d+)">([\d-]+)</A>',s):
        v=list(map(int,ds.split('-')));out[int(n),int(k)]=(v[0],v[-1])
    return out

def parse_triples(s):
    """Explicitly displayed [n,k,d] triples in the Yu et al. page (used once by extract_sources.py)."""
    return sorted(set(tuple(map(int,x)) for x in re.findall(r'\[(\d+),\s*(\d+),\s*(\d+)\]',s)))

def table():
    out={(n,k):(lb,ub) for n,k,lb,ub in json.loads(BOUNDS.read_text())['bounds']}
    if len(out)!=32896:raise ValueError('incomplete table snapshot')
    return out

def implications(n,k,d,limit):
    if k>1:yield (n,k-1,d,'subcode')
    if n>1 and d>1 and k<n:yield (n-1,k,d-1,'puncture')
    if k>1:yield (n-1,k-1,d,'shorten-nonzero-coordinate')
    if n<limit:
        yield (n+1,k,d,'zero-extend')
        yield (n+1,k,d+(d%2),'parity-extend')
    # Permutations preserve parameters and do not create a new node.

def close(seeds,limit=256):
    best={}; trace={};q=deque()
    def put(n,k,d,why):
        if not (1<=k<=n<=limit and 1<=d<=n):return
        if d>best.get((n,k),0):
            best[n,k]=d;trace[n,k]=why;q.append((n,k,d))
    for n,k,d,source in seeds:put(n,k,d,dict(source=source))
    updates=0
    while q:
        n,k,d=q.popleft()
        if best[n,k]!=d:continue
        for nn,kk,dd,op in implications(n,k,d,limit):
            if dd>best.get((nn,kk),0):
                # Store entire derivation tree to avoid mutable predecessor links.
                put(nn,kk,dd,dict(operation=op,parent=[n,k,d],derivation=trace[n,k]));updates+=1
    return best,trace,updates

def run(output='results/closure.json',quiet=False):
    t=table();seeds=[(n,k,lb,f'codetables:{n}:{k}') for (n,k),(lb,ub) in t.items()]
    # Extract explicitly displayed binary triples from recent group-code paper.
    triples=[tuple(x) for x in json.loads(TRIPLES.read_text())['triples']]
    # These include comparison codes: inclusion is conservative for novelty.
    recent=[x for x in triples if 1<=x[1]<=x[0]<=256 and 1<=x[2]<=x[0]]
    seeds += [(*x,'Yu et al. arXiv:2412.15551v1; reported, not locally certified') for x in recent]
    lincode=[(172,21,66),(173,20,68),(176,21,68),(181,21,70),(184,21,72),(189,22,72),(200,21,77)]
    seeds += [(*x,'Seddas et al. arXiv:2609.37056v1 Table 1; reported, not locally certified') for x in lincode]
    b,tr,updates=close(seeds)
    from upper_bounds import audit
    upper,utrace=audit(t)
    conflicts=[(n,k,b[n,k],upper[n,k]) for n,k in t if b[n,k]>upper[n,k]]
    if conflicts:raise ValueError(('literature lower/upper conflict',conflicts))
    rows=[dict(n=n,k=k,table_lower=t[n,k][0],table_upper=t[n,k][1],audited_upper=upper[n,k],upper_derivation=utrace[n,k],exclusion_lower=b[n,k],derivation=tr[n,k]) for n,k in sorted(t)]
    result=dict(scope='Guaranteed parameter closure of frozen complete table and explicit recent reported triples; not equivalence-class closure or all literature',seed_count=len(seeds),recent_triples=recent,lincode2026_parents=lincode,updates=updates,upper_improvements=sum(upper[p]<t[p][1] for p in t),improved_over_table=sum(r['exclusion_lower']>r['table_lower'] for r in rows),rows=rows)
    if output: Path(output).write_text(json.dumps(result,indent=2)+'\n')
    if not quiet: print(json.dumps({k:v for k,v in result.items() if k not in ('rows','recent_triples')}))
    return result
if __name__=='__main__':run()
