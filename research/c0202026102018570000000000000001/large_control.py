"""Replicate the published [173,20,68] construction in Appendix A of
Seddas et al., arXiv:2609.37056v1. Already in our exclusion closure.
This is a home-PC verification control, not a new record."""
import hashlib,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import codes,independent
def mul(a,b):
    out=0
    while b:
        if b&1:out^=a
        a<<=1;b>>=1
    return out
def divmod2(a,b):
    q=0
    while a.bit_length()>=b.bit_length():
        shift=a.bit_length()-b.bit_length();q^=1<<shift;a^=b<<shift
    return q,a
def poly(exponents):return sum(1<<i for i in exponents)
def run():
    start=time.perf_counter();cpu=time.process_time()
    factors=[poly([4,3,2,1,0]),poly([8,5,4,3,2,1,0]),poly([8,7,6,5,4,3,0])]
    h=1
    for factor in factors:h=mul(h,factor)
    modulus=(1<<85)|1;g,remainder=divmod2(modulus,h);assert remainder==0 and h.bit_length()==21
    f2=poly([15,11,6,3,2,0]);tail=['01001','10100','01010'];rows=[]
    for j in range(20):
        left=divmod2(g<<j,modulus)[1];right=divmod2(mul(g,f2)<<j,modulus)[1]
        rows.append(left|(right<<85)|sum(int(c[j%5])<<(170+i) for i,c in enumerate(tail)))
    cert=HERE/'published_173_20_68.json'
    codes.write_cert(cert,rows,173,dict(kind='published-recent-record-replication',
        source='https://arxiv.org/html/2609.37056v1#A1',
        authors='Amal Seddas, Vladyslav Shashkov, Maryna Viazovska, Emmanuel Abbe',
        snapshot='data/sources/lincode2026.html',
        snapshot_sha256=next(x['sha256'] for x in json.loads((ROOT/'data/source-index.json').read_text()) if x['path']=='data/sources/lincode2026.html'),
        construction='Appendix A: block85 index2, h degree20, three five-periodic tail coordinates',
        polynomial_factors=factors,f2=f2,tail=tail,
        credit='Known published construction; already excluded from discovery credit before this trial.'))
    t=time.perf_counter();ct=time.process_time();a=codes.check(cert)
    first=dict(wall=time.perf_counter()-t,cpu=time.process_time()-ct)
    t=time.perf_counter();ct=time.process_time();b=independent.check(cert)
    second=dict(wall=time.perf_counter()-t,cpu=time.process_time()-ct)
    assert a['spectrum']==b['spectrum'] and a['d']==68
    result=dict(n=173,k=20,d=68,codewords=1<<20,minimum_words=a['spectrum'][68],
        object=str(cert.relative_to(ROOT)),sha256=a['sha256'],spectrum=a['spectrum'],
        verifier_gray=first,verifier_column_parity=second,
        total_wall=time.perf_counter()-start,total_cpu=time.process_time()-cpu,
        claim='Replication of known 2026 construction, not a pilot discovery or optimality proof.',
        independent_human_review=False)
    (HERE/'large_control.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='spectrum'}),flush=True)
if __name__=='__main__':run()
