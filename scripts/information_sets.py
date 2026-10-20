"""Experimental certified distance using disjoint full-rank information sets.
Independent of Gray enumeration; no heuristic stopping rule. See docs/certification.md.
"""
import itertools,json,time
from pathlib import Path
import codes,independent

def systematic_on(rows,columns):
    a=list(rows)
    for i,j in enumerate(columns):
        pivot=next((p for p in range(i,len(a)) if a[p]>>j&1),None)
        if pivot is None:raise ValueError('dependent information set')
        a[i],a[pivot]=a[pivot],a[i]
        for p in range(len(a)):
            if p!=i and a[p]>>j&1:a[p]^=a[i]
    return a

def sets(rows,n):
    remaining=list(range(n));out=[];k=len(rows)
    while True:
        picked=[];basis=[]
        for j in remaining:
            col=sum(((r>>j)&1)<<i for i,r in enumerate(rows))
            if len(codes.basis(basis+[col]))>len(basis):basis.append(col);picked.append(j)
            if len(picked)==k:break
        if len(picked)<k:break
        out.append(picked);remaining=[j for j in remaining if j not in picked]
    return out

def certified(rows,n,information_sets=None):
    info=sets(rows,n) if information_sets is None else information_sets
    flat=[j for s in info for j in s];k=len(rows)
    if not info or any(len(s)!=k for s in info) or len(set(flat))!=len(flat) or any(type(j)!=int or not 0<=j<n for j in flat):raise ValueError('invalid/disjoint information sets')
    bases=[systematic_on(rows,s) for s in info];upper=n+1;word=None;count=0
    for t in range(1,k+1):
        for a in bases:
            for support in itertools.combinations(range(k),t):
                w=0
                for i in support:w^=a[i]
                count+=1
                if w.bit_count()<upper:upper=w.bit_count();word=w
        lower=len(info)*(t+1)
        # Every unenumerated word has >=t+1 ones in EACH disjoint information set.
        if t==k or lower>=upper:
            return dict(d=upper,minimum_word=''.join(str(word>>j&1) for j in range(n)),sets=info,enumeration_depth=t,enumerated=count,unenumerated_lower_bound=lower,exact=True)
    raise AssertionError('unreachable')

def run(output='results/information-sets.json'):
    reports=[]
    for m,delta in [(5,7),(6,23)]:
        rows,n=codes.bch(m,delta);rows,n=codes.extend(rows,n)
        t=time.perf_counter();r=certified(rows,n);r['seconds']=time.perf_counter()-t
        assert r['d']==codes.distance(rows,n)
        fn=f'certificates/control_bch_{n}_{len(rows)}.json';codes.write_cert(fn,rows,n,dict(kind='classical BCH control',m=m,delta=delta))
        assert independent.check(fn)['d']==r['d']
        reports.append(dict(n=n,k=len(rows),all_codewords=2**len(rows),object=fn,**r))
    Path(output).write_text(json.dumps(reports,indent=2)+'\n')
    print('PASS information-set certification',[(x['n'],x['k'],x['d'],x['enumerated'],x['all_codewords']) for x in reports])
if __name__=='__main__':run()
