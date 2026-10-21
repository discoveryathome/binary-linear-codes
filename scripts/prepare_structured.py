"""Reconstruct six Appendix A parents, cross-check spectra, and propose bounded tasks.
Never replaces the frozen 16-case frontier or labels a replication a new record.
"""
import hashlib,json,time,importlib.util
from pathlib import Path
import codes,large_verify,closure
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/readiness-20261021'
SOURCE='https://arxiv.org/html/2609.37056v1'
F21=[[1,0],[4,3,2,1,0],[8,6,5,4,3,1,0],[8,7,5,1,0]]
SPECS=[
(172,21,66,85,F21,[[0],[13,11,9,6,4,3,2,1,0]],['11111']*2),
(173,20,68,85,[[4,3,2,1,0],[8,5,4,3,2,1,0],[8,7,6,5,4,3,0]],[[0],[15,11,6,3,2,0]],['01001','10100','01010']),
(176,21,68,85,F21,[[0],[13,11,9,6,4,3,2,1,0]],['01111','11111','11111','10010','11011','00101']),
(181,21,70,85,[[1,0],[4,3,2,1,0],[8,5,4,3,2,1,0],[8,7,3,1,0]],[[0],[13,10,7,6,4,3,0]],['11000','10100','11100','01010','01110','10001','11101','00011','10011','00111','01111']),
(184,21,72,85,[[1,0],[4,3,2,1,0],[8,6,5,4,2,1,0],[8,7,5,4,3,2,0]],[[0],[13,9,8,7,6,5,3,1,0]],['11001','01001','00101','11101','11110','00111','11100','01010','10010','10001','11111','01110','10011','00110']),
(189,22,72,63,[[1,0],[3,2,0],[6,5,0],[6,5,3,2,0],[6,5,4,2,0]],[[0],[14,13,12,9,7,5,3,2,0],[16,14,13,10,7,1,0]],[])]
def poly(xs):return sum(1<<i for i in xs)
def mul(a,b):
    out=0
    while b:
        if b&1:out^=a
        a<<=1;b>>=1
    return out
def div(a,b):
    q=0
    while a.bit_length()>=b.bit_length():
        shift=a.bit_length()-b.bit_length();q^=1<<shift;a^=b<<shift
    return q,a

def construct(spec):
    n,k,d,m,factors,fs,tails=spec;h=1
    for f in factors:h=mul(h,poly(f))
    modulus=(1<<m)|1;g,rem=div(modulus,h)
    if rem or h.bit_length()!=k+1:raise ValueError('invalid divisor/dimension')
    rows=[]
    for j in range(k):
        r=sum(div(mul(g,poly(f))<<j,modulus)[1]<<(i*m) for i,f in enumerate(fs))
        r|=sum(int(c[j%5])<<(len(fs)*m+i) for i,c in enumerate(tails));rows.append(r)
    if len(codes.basis(rows))!=k or max(rows).bit_length()>n:raise ValueError('rank/length')
    return rows

def main():
    (OUT/'certificates').mkdir(parents=True,exist_ok=True);records=[]
    bounds={(r['n'],r['k']):r for r in closure.run(output=None,quiet=True)['rows']}
    for spec in SPECS:
        n,k,d,*_=spec;start=time.perf_counter();rows=construct(spec);hist=codes.spectrum(rows,n)
        if next(i for i in range(1,n+1) if hist[i])!=d:raise ValueError('published distance mismatch')
        obj=OUT/f'certificates/{n}_{k}_{d}.json'
        cert=dict(format='binary-generator-v1',q=2,n=n,k=k,d=d,rows=[''.join(str((r>>j)&1) for j in range(n)) for r in rows],
          provenance=dict(source=SOURCE,authors='Seddas, Shashkov, Viazovska, Abbe',kind='published-parent-replication',construction=spec,
            source_snapshot_sha256=hashlib.sha256((ROOT/'data/sources/lincode2026.html').read_bytes()).hexdigest()))
        obj.write_text(json.dumps(cert,indent=2)+'\n');gray=time.perf_counter()-start;t=time.perf_counter();other=large_verify.check(obj)
        if hist!=other['spectrum']:raise ValueError('checker disagreement')
        b=bounds[n,k];records.append(dict(n=n,k=k,d=d,object=str(obj.relative_to(ROOT)),sha256=hashlib.sha256(obj.read_bytes()).hexdigest(),
          spectrum=hist,gray_seconds=gray,subset_seconds=time.perf_counter()-t,exclusion_lower=b['exclusion_lower'],upper=b['audited_upper'],
          target_distance=b['exclusion_lower']+1,status='replicated parent; successor task needs coding-theorist review'))
        print(n,k,d,round(gray,3),round(records[-1]['subset_seconds'],3),flush=True)
    # Replay the existing local-neighborhood obstructions before using them to retire tasks.
    folder=ROOT/'research/c0202026102018570000000000000001';import sys;sys.path.insert(0,str(folder))
    import obstruction
    ob=json.loads((folder/'obstructions.json').read_text())['rows']
    for r in ob:obstruction.verify(r)
    result=dict(parents=records,obstruction_pairs=sum(r['proved'] for r in ob),
        unsupported=[{'n':200,'k':21,'d':77,'reason':'Appendix HTML has no explicit generator; retain exclusion, request accompanying artifact.'}],
        status='author-checked; review pending',novel_records=0,
        task_scope='Search must change the structured core/family, not repeat certified blocked local neighborhoods. All proposed targets require current-record reconciliation.')
    (OUT/'structured.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
