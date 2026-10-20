"""Bounded deterministic research. No network. Never updates published frontier.
All wins are retained as certificates; beating exclusions is only a candidate record.
"""
import argparse,json,random,time,platform,hashlib
from pathlib import Path
import codes,independent

def digest(rows,n):
    return hashlib.sha256(json.dumps([n,rows]).encode()).hexdigest()

def run(seed,iterations,output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    targets=json.loads(Path('data/targets.json').read_text());rng=random.Random(int(seed,16))
    best={};summary=[];attempts=[];t0=time.perf_counter();structured=0
    for t in targets:
        c,r=codes.read_cert(t['object']);best[t['n'],t['k']]=(r,c['d'],t['object'])
    def consider(r,n,method,provenance):
        nonlocal structured
        key=(n,len(r))
        if key not in best or len(codes.basis(r))!=len(r):return
        structured+=1;d=codes.distance(r,n)
        if d>best[key][1]:
            fn=out/f'structured_{n}_{len(r)}_{d}.json';codes.write_cert(fn,r,n,dict(method=method,**provenance));independent.check(fn)
            best[key]=(r,d,str(fn));attempts.append(dict(n=n,k=len(r),d=d,method=method,object=str(fn)))
    # Every eligible source coordinate; one parity extension; 128 hyperplanes per compatible parent.
    for t in targets:
        c,r=codes.read_cert(t['object']);n=c['n'];k=c['k'];prov=dict(parent=t['object'])
        for j in range(n):
            rr,nn=codes.puncture(r,n,[j]);consider(rr,nn,'puncture',dict(**prov,coordinate=j))
            rr,nn=codes.shorten(r,n,[j]);consider(rr,nn,'shorten',dict(**prov,coordinate=j))
        rr,nn=codes.extend(r,n);consider(rr,nn,'parity-extension',prov)
        if (n,k-1) in best:
            for mask in rng.sample(range(1,1<<k),min(128,(1<<k)-1)):
                pivot=(mask&-mask).bit_length()-1
                selectors=[(1<<i)^((1<<pivot) if (mask>>i)&1 else 0) for i in range(k) if i!=pivot]
                consider(codes.subcode(r,selectors),n,'hyperplane-subcode',dict(**prov,mask=mask,selectors=selectors))
        # An explicitly verified permutation negative control.
        order=list(range(n));rng.shuffle(order);rr,nn=codes.permute(r,n,order)
        if codes.spectrum(r,n)!=codes.spectrum(rr,nn):raise ValueError('permutation control')
    for target in targets:
        n,k=target['n'],target['k'];base,bd,origin=best[n,k];started=time.perf_counter()
        per=[]
        for restart in range(3):
            # Two warm starts and one cold systematic start quantify frontier access.
            r=list(base) if restart<2 else [(1<<i)|(rng.getrandbits(n-k)<<k) for i in range(k)]
            h=codes.spectrum(r,n);score=tuple(-x for x in h[1:]);initial=codes.distance(r,n);bestd=initial;accepted=0;rank_rejects=0
            for step in range(iterations):
                rr=list(r)
                if step%3==0: # replace one generator column by a random k-vector
                    j=rng.randrange(n);col=rng.randrange(1<<k)
                    for i in range(k):rr[i]=(rr[i]&~(1<<j))|(((col>>i)&1)<<j)
                else:
                    # single or double bit moves with integer exact objective
                    for _ in range(1+(step%7==0)):
                        i=rng.randrange(k);rr[i]^=1<<rng.randrange(n)
                if len(codes.basis(rr))!=k:rank_rejects+=1;continue
                hh=codes.spectrum(rr,n);ss=tuple(-x for x in hh[1:])
                if ss>=score:r,h,score=rr,hh,ss;accepted+=1
                d=next(i for i in range(1,n+1) if h[i]);bestd=max(bestd,d)
            fn=out/f'local_{n}_{k}_r{restart}.json'
            codes.write_cert(fn,r,n,dict(kind='local-search',seed=seed,restart=restart,iterations=iterations,initial=origin if restart<2 else 'random systematic',method='lexicographic weight-spectrum hill climb; column and bit mutations'))
            check=independent.check(fn)
            per.append(dict(restart=restart,initial_d=initial,best_d=bestd,final_d=check['d'],accepted=accepted,rank_rejects=rank_rejects,object=str(fn),matrix_sha256=digest(r,n)))
            if check['d']>best[n,k][1]:best[n,k]=(r,check['d'],str(fn))
        achieved=best[n,k][1]
        summary.append(dict(n=n,k=k,published_lower=target['published_lower'],closure_lower=target['closure_lower'],upper=target['upper'],best_d=achieved,improvement_over_published=achieved-target['published_lower'],candidate_record=achieved>target['closure_lower'],seconds=time.perf_counter()-started,runs=per))
        print(f'[{n},{k}] best={achieved}, exclusion={target["closure_lower"]}, cold={per[2]["final_d"]}',flush=True)
    result=dict(seed=seed,iterations_per_restart=iterations,restarts=3,local_proposals=iterations*3*len(targets),structured_candidates=structured,structured_improvements=attempts,seconds=time.perf_counter()-t0,environment=dict(python=platform.python_version(),platform=platform.platform(),processor=platform.processor()),closure_sha256=hashlib.sha256(Path('results/closure.json').read_bytes()).hexdigest(),targets_sha256=hashlib.sha256(Path('data/targets.json').read_bytes()).hexdigest(),rows=summary,candidate_records=sum(x['candidate_record'] for x in summary))
    (out/'experiment.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('rows','structured_improvements')}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',default='b17a20261020c0de0000000000000001');p.add_argument('--iterations',type=int,default=1000);p.add_argument('--output',default='results/experiment');a=p.parse_args()
    if len(a.seed)!=32 or any(x not in '0123456789abcdefABCDEF' for x in a.seed) or not 1<=a.iterations<=100000:raise SystemExit('32 hex seed and 1..100000 iterations required')
    run(a.seed,a.iterations,a.output)
