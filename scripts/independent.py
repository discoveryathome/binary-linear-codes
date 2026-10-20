"""Independent checker: list GF(2) elimination; column parity enumeration.
Does not import codes.py or share its parsing/rank/enumeration routines.
"""
import json,sys
from pathlib import Path

def check(path):
    c=json.loads(Path(path).read_text())
    if c.get('format')!='binary-generator-v1' or type(c.get('q'))!=int or c['q']!=2:raise ValueError('format')
    if not isinstance(c.get('provenance'),dict):raise ValueError('provenance metadata')
    n,k,d=[c.get(t) for t in ('n','k','d')]
    if any(type(x)!=int for x in (n,k,d)) or not 1<=k<=min(n,20) or not n<=512 or not 1<=d<=n:raise ValueError('parameters/budget')
    r=c.get('rows')
    if not isinstance(r,list) or len(r)!=k or any(not isinstance(s,str) or len(s)!=n or set(s)-{'0','1'} for s in r):raise ValueError('matrix')
    a=[[int(b) for b in s] for s in r]; rank=0
    for j in range(n):
        pivot=next((i for i in range(rank,k) if a[i][j]),None)
        if pivot is None:continue
        a[rank],a[pivot]=a[pivot],a[rank]
        for i in range(rank+1,k):
            if a[i][j]:a[i]=[(x+y)%2 for x,y in zip(a[i],a[rank])]
        rank+=1
    if rank!=k:raise ValueError('rank mismatch')
    columns=[sum(int(r[i][j])*2**i for i in range(k)) for j in range(n)]
    parity=[bin(x).count('1')%2 for x in range(2**k)]
    hist=[0]*(n+1)
    for message in range(2**k):hist[sum(parity[message & col] for col in columns)]+=1
    actual=next(w for w in range(1,n+1) if hist[w])
    if actual!=d:raise ValueError('distance mismatch')
    return dict(n=n,k=k,d=actual,spectrum=hist)
if __name__=='__main__':
    for p in sys.argv[1:]: print(p,json.dumps(check(p)))
