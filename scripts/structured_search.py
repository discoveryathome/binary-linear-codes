"""Bounded polynomial-core search from a checked published construction.
Search changes a QC multiplier, avoiding the fixed-tail neighborhoods already ruled out.
This is a reference method, not a forecast of donor success or a novel algorithm.
"""
import argparse,copy,hashlib,json,random,time
from pathlib import Path
import codes,large_verify
from prepare_structured import SPECS,construct,ROOT,OUT

def run(n,seed,trials,output):
    if not 1<=trials<=256:raise ValueError('trial cap 1..256')
    dest=Path(output)
    if dest.exists():raise ValueError('output exists; preserve experiment')
    dest.mkdir(parents=True)
    spec=copy.deepcopy(next(s for s in SPECS if s[0]==n));k=spec[1];rng=random.Random(seed);start=time.perf_counter()
    bestspec=copy.deepcopy(spec);bestrows=construct(spec);besthist=codes.spectrum(bestrows,n);bestd=spec[2];history=[];seen={tuple(codes.basis(bestrows))}
    for i in range(trials):
        proposed=copy.deepcopy(spec);block=rng.randrange(1,len(proposed[5]));exponents=set(proposed[5][block])
        for bit in rng.sample(range(k),rng.randint(1,3)):
            if bit in exponents:exponents.remove(bit)
            else:exponents.add(bit)
        proposed[5][block]=sorted(exponents,reverse=True);rows=construct(proposed);identity=tuple(codes.basis(rows))
        if identity in seen:history.append(dict(trial=i,duplicate=True));continue
        seen.add(identity);hist=codes.spectrum(rows,n);d=next(j for j in range(1,n+1) if hist[j])
        history.append(dict(trial=i,d=d,minimum_words=hist[d],multiplier=proposed[5],duplicate=False))
        if d>bestd:bestd=d;besthist=hist;bestrows=rows;bestspec=proposed
    cert=dict(format='binary-generator-v1',q=2,n=n,k=k,d=bestd,rows=[''.join(str((r>>j)&1) for j in range(n)) for r in bestrows],
      provenance=dict(kind='bounded-structured-search',seed=seed,trials=trials,parent=f'research/readiness-20261021/certificates/{n}_{k}_{spec[2]}.json',construction=bestspec))
    p=dest/'candidate.json';p.write_text(json.dumps(cert,indent=2)+'\n');v=large_verify.check(p)
    if v['spectrum']!=besthist:raise ValueError('checker disagreement')
    result=dict(n=n,k=k,seed=seed,trials=trials,initial_d=spec[2],final_d=bestd,history=history,seconds=time.perf_counter()-start,
       verified_spectrum=besthist,improved_parent=bestd>spec[2],claim='Candidate record requires fresh closure/literature and external review; matching parent is replication.',
       source_sha256={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in (Path(__file__),ROOT/'scripts/prepare_structured.py',ROOT/'scripts/large_verify.py')})
    (dest/'result.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--parent',type=int,choices=[x[0] for x in SPECS],required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--trials',type=int,default=16);p.add_argument('--output',required=True);a=p.parse_args()
    r=run(a.parent,a.seed,a.trials,a.output);print(json.dumps({k:v for k,v in r.items() if k not in ('history','verified_spectrum')}))
