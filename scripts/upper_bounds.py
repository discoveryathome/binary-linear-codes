"""Close upper bounds by contrapositives of standard operations."""
import json
from pathlib import Path
from collections import deque

def griesmer(n,k):
    lo,hi=0,n+1
    while hi-lo>1:
        d=(lo+hi)//2
        if sum((d+(1<<i)-1)//(1<<i) for i in range(k))<=n:lo=d
        else:hi=d
    return lo

def audit(table,limit=256):
    u={p:v[1] for p,v in table.items()};trace={p:dict(source=f'codetables:{p[0]}:{p[1]}') for p in u};q=deque(u)
    for r in json.loads(Path('data/upper-overrides.json').read_text()):
        p=(r['n'],r['k']);u[p]=min(u[p],r['upper']);trace[p]=dict(source=r['source'],claim=r['claim'])
    for (n,k) in u:
        g=griesmer(n,k)
        if g<u[n,k]:u[n,k]=g;trace[n,k]=dict(source='Griesmer integer sum',n=n,k=k)
    while q:
        n,k=q.popleft();v=u[n,k]
        candidates=[(n,k+1,v,'subcode-contrapositive'),(n+1,k,v+1,'puncture-contrapositive'),(n+1,k+1,v,'shorten-contrapositive'),(n-1,k,v-v%2,'parity-extension-contrapositive')]
        for nn,kk,vv,op in candidates:
            if (nn,kk) in u and vv<u[nn,kk]:
                u[nn,kk]=vv;trace[nn,kk]=dict(operation=op,parent=[n,k,v],derivation=trace[n,k]);q.append((nn,kk))
    return u,trace
