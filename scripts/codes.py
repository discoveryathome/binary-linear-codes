"""Binary linear code primitives. Coordinate j is bit j (leftmost in JSON)."""
import hashlib,json
from pathlib import Path

def basis(rows):
    piv={}
    for x in rows:
        while x:
            p=x.bit_length()-1
            if p in piv: x ^= piv[p]
            else:
                piv[p]=x; break
    return [piv[p] for p in sorted(piv,reverse=True)]

def spectrum(rows,n):
    hist=[0]*(n+1); hist[0]=1; w=0
    for i in range(1,1<<len(rows)):
        w ^= rows[(i & -i).bit_length()-1]
        hist[w.bit_count()]+=1
    return hist

def distance(rows,n):
    h=spectrum(rows,n)
    return next(i for i in range(1,n+1) if h[i])

def puncture(rows,n,positions):
    pos=set(positions)
    if any(not 0<=j<n for j in pos): raise ValueError('coordinate')
    keep=[j for j in range(n) if j not in pos]
    return basis([sum(((r>>j)&1)<<i for i,j in enumerate(keep)) for r in rows]),len(keep)

def shorten(rows,n,positions):
    pos=sorted(set(positions)); a=basis(rows)
    if any(not 0<=j<n for j in pos): raise ValueError('coordinate')
    for j in pos:
        pivot=next((r for r in a if (r>>j)&1),None)
        if pivot is not None:
            a.remove(pivot); a=[r^pivot if (r>>j)&1 else r for r in a]
    return puncture(a,n,pos)

def extend(rows,n,column=None):
    if column is None: column=[r.bit_count()%2 for r in rows]
    if len(column)!=len(rows) or any(x not in (0,1) for x in column): raise ValueError('column')
    return [r|(v<<n) for r,v in zip(rows,column)],n+1

def subcode(rows,coefficients):
    out=[]
    for m in coefficients:
        if type(m)!=int or not 0<=m<1<<len(rows): raise ValueError('coefficient')
        r=0
        for i,v in enumerate(rows):
            if (m>>i)&1:r^=v
        out.append(r)
    if len(basis(out))!=len(out): raise ValueError('dependent subcode selectors')
    return out

def permute(rows,n,order):
    if sorted(order)!=list(range(n)): raise ValueError('not a permutation')
    return [sum(((r>>j)&1)<<i for i,j in enumerate(order)) for r in rows],n

def certificate(rows,n,provenance):
    if not 1<=len(rows)<=20 or len(basis(rows))!=len(rows): raise ValueError('rank or budget')
    return dict(format='binary-generator-v1',q=2,n=n,k=len(rows),d=distance(rows,n),
                rows=[''.join(str((r>>j)&1) for j in range(n)) for r in rows],provenance=provenance)

def write_cert(path,rows,n,provenance):
    c=certificate(rows,n,provenance); Path(path).write_text(json.dumps(c,indent=2)+'\n'); return c

def read_cert(path):
    c=json.loads(Path(path).read_text())
    if c.get('format')!='binary-generator-v1' or type(c.get('q'))!=int or c['q']!=2: raise ValueError('format')
    if not isinstance(c.get('provenance'),dict):raise ValueError('provenance metadata')
    n,k,d=[c.get(t) for t in ('n','k','d')]
    if any(type(t)!=int for t in (n,k,d)) or not (1<=k<=min(n,20) and k<=n<=512 and 1<=d<=n): raise ValueError('parameters/budget')
    if not isinstance(c.get('rows'),list) or len(c['rows'])!=k: raise ValueError('row count')
    if any(not isinstance(r,str) or len(r)!=n or set(r)-{'0','1'} for r in c['rows']): raise ValueError('binary rows')
    return c,[int(r[::-1],2) for r in c['rows']]

def check(path):
    c,r=read_cert(path)
    if len(basis(r))!=c['k']:raise ValueError('rank mismatch')
    h=spectrum(r,c['n']); d=next(i for i in range(1,len(h)) if h[i])
    if d!=c['d']:raise ValueError('distance mismatch')
    return dict(n=c['n'],k=c['k'],d=d,spectrum=h,sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())

# Primitive narrow-sense BCH; multiply minimal-root factors in GF(2^m).
def bch(m,delta,b=1):
    primitive={3:0b1011,4:0b10011,5:0b100101,6:0b1000011,7:0b10000011,8:0b100011101}[m]
    n=(1<<m)-1
    def mul(a,b):
        v=0
        while b:
            if b&1:v^=a
            b>>=1;a<<=1
            if a>>m:a^=primitive
        return v
    powers=[1]
    for _ in range(1,n):powers.append(mul(powers[-1],2))
    assert len(set(powers))==n
    roots=set()
    for i in range(b,b+delta-1):
        j=i%n
        while j not in roots:roots.add(j);j=(2*j)%n
    p=[1]
    for j in sorted(roots):
        out=[0]*(len(p)+1)
        for t,a in enumerate(p):out[t]^=mul(a,powers[j]);out[t+1]^=a
        p=out
    assert set(p)<={0,1}
    g=sum(a<<i for i,a in enumerate(p)); k=n-len(p)+1
    return [g<<i for i in range(k)],n
