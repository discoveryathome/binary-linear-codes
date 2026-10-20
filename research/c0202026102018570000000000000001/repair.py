"""Targeted three-column repair of a fixed matrix. Constraints are exact;
wall-budget exhaustion is explicitly incomplete, never a nonexistence proof."""
import argparse,itertools,json,random,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import codes,independent

def affine(messages,k,all_solutions=True):
    piv={}
    for m in messages:
        x=m;b=1
        while x:
            p=x.bit_length()-1
            if p not in piv:piv[p]=(x,b);break
            xx,bb=piv[p];x^=xx;b^=bb
        if x==0 and b:return []
    free=[i for i in range(k) if i not in piv]
    out=[]
    for mask in range((1<<len(free)) if all_solutions else 1):
        x=sum(((mask>>j)&1)<<i for j,i in enumerate(free))
        for p,(row,b) in sorted(piv.items()):
            if (x&row).bit_count()%2!=b:x|=1<<p
        out.append(x)
    return out

def run(path,seconds,seed,output):
    c,rows=codes.read_cert(path);n,k,d=c['n'],c['k'],c['d'];goal=d+1
    w=[0]
    for row in rows:w += [x^row for x in w]
    relevant=[(m,x,x.bit_count()) for m,x in enumerate(w) if m and x.bit_count()<goal+3]
    low=[x for m,x,weight in relevant if weight==d]
    triples=list(itertools.combinations(range(n),3));random.Random(seed).shuffle(triples)
    stats=dict(parent=str(path),n=n,k=k,initial_d=d,goal=goal,seed=seed,
               triples_total=len(triples),visited=0,cover_rejects=0,affine_rejects=0,
               pair_attempts=0,pair_cover_rejects=0,third_affine_rejects=0,
               completed_triples=0,found=False,complete=False)
    t=time.perf_counter()
    for triple in triples:
        if time.perf_counter()-t>=seconds:break
        stats['visited']+=1
        mask=sum(1<<j for j in triple)
        if any(x&mask==mask for x in low):
            stats['cover_rejects']+=1;stats['completed_triples']+=1;continue
        req={q:[] for q in [1,2,3]}
        for m,x,weight in relevant:
            need=goal-weight+(x&mask).bit_count()
            if need>0:req[need].append(m)
        sols=affine(req[3],k)
        if not sols:
            stats['affine_rejects']+=1;stats['completed_triples']+=1;continue
        zeros={a:sum((1<<j) for j,m in enumerate(req[2]) if (a&m).bit_count()%2==0) for a in sols}
        stop=False
        for a,b in itertools.combinations_with_replacement(sols,2):
            if time.perf_counter()-t>=seconds:stop=True;break
            stats['pair_attempts']+=1
            if zeros[a]&zeros[b]:
                stats['pair_cover_rejects']+=1;continue
            third=list(req[3])
            third.extend(m for m in req[2] if (a&m).bit_count()%2==0 or (b&m).bit_count()%2==0)
            third.extend(m for m in req[1] if (a&m).bit_count()%2==0 and (b&m).bit_count()%2==0)
            sol=affine(third,k,False)
            if not sol:stats['third_affine_rejects']+=1;continue
            columns=[a,b,sol[0]];r=list(rows)
            for j,col in zip(triple,columns):
                for i in range(k):r[i]=(r[i]&~(1<<j))|(((col>>i)&1)<<j)
            assert codes.distance(r,n)>=goal
            cert=Path(output).with_suffix('.certificate.json')
            codes.write_cert(cert,r,n,dict(kind='targeted-three-column-repair',
                parent=str(path),coordinates=triple,columns=columns,seed=seed))
            aa,bb=codes.check(cert),independent.check(cert);assert aa['spectrum']==bb['spectrum']
            stats.update(found=True,object=str(cert),d=aa['d'],coordinates=triple,columns=columns)
            stop=True;break
        if stop:break
        stats['completed_triples']+=1
    stats['seconds']=time.perf_counter()-t
    stats['complete']=stats['completed_triples']==stats['triples_total']
    stats['claim']='Exact constraints explored; negative search is not independently proof-certified.'
    Path(output).write_text(json.dumps(stats,indent=2)+'\n')
    print(json.dumps(stats),flush=True)
    return stats

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('parent',type=Path)
    p.add_argument('--seconds',type=float,default=120);p.add_argument('--seed',type=int,default=301)
    p.add_argument('--output',required=True);a=p.parse_args()
    run(a.parent,a.seconds,a.seed,a.output)
