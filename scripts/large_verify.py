"""Bounded k<=22 certificate checker using direct subset halves (not Gray order).
Separate parser, list-based rank elimination, and subset enumeration. Standard library only.
This is an additional same-author implementation, not an independent human review.
"""
import json
from pathlib import Path

def check(path):
    c=json.loads(Path(path).read_text()); n,k,d=[c.get(x) for x in ('n','k','d')]
    if c.get('format')!='binary-generator-v1' or c.get('q')!=2 or type(c.get('q'))!=int:raise ValueError('format')
    if any(type(x)!=int for x in (n,k,d)) or not 1<=k<=min(n,22) or not n<=512 or not 1<=d<=n:raise ValueError('budget/parameters')
    r=c.get('rows')
    if not isinstance(c.get('provenance'),dict) or not isinstance(r,list) or len(r)!=k:raise ValueError('metadata/matrix')
    if any(not isinstance(s,str) or len(s)!=n or set(s)-{'0','1'} for s in r):raise ValueError('binary matrix')
    a=[list(map(int,s)) for s in r]; rank=0
    for j in range(n):
        pivot=next((i for i in range(rank,k) if a[i][j]),None)
        if pivot is None:continue
        a[rank],a[pivot]=a[pivot],a[rank]
        for i in range(rank+1,k):
            if a[i][j]:a[i]=[(x+y)%2 for x,y in zip(a[i],a[rank])]
        rank+=1
    if rank!=k:raise ValueError('rank')
    # MSB-first parsing deliberately differs from construction-side coordinates.
    ints=[int(s,2) for s in r]
    def subsets(xs):
        out=[0]
        for x in xs:out += [y^x for y in out]
        return out
    left=subsets(ints[:k//2]);right=subsets(ints[k//2:]);hist=[0]*(n+1)
    for x in left:
        for y in right:hist[(x^y).bit_count()]+=1
    if hist[0]!=1 or sum(hist)!=2**k:raise ValueError('enumeration')
    actual=next(i for i in range(1,n+1) if hist[i])
    if actual!=d:raise ValueError('distance')
    return dict(n=n,k=k,d=d,spectrum=hist)

if __name__=='__main__':
    import sys
    for path in sys.argv[1:]:print(json.dumps(check(path)))
