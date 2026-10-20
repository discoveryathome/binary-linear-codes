import argparse,json,random,subprocess,sys,hashlib,platform
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import codes,independent
def run(phase,seconds):
    out=HERE/phase;out.mkdir(exist_ok=True);jobs=[]
    if phase=='qc':
        jobs=[(44,11,s,m) for s in [201,202,203] for m in ['random','hill','anneal']]
    elif phase=='coset':
        jobs=[(n,k,s,m) for n,k in [(42,12),(52,10),(62,11)] for s in [401,402,403] for m in ['hill','anneal']]
    else:raise ValueError(phase)
    random.Random(20261021).shuffle(jobs)
    result=dict(phase=phase,started_at=datetime.now(timezone.utc).isoformat(),
                seconds_per_run=seconds,source_sha256=hashlib.sha256((HERE/f'{phase}_search.cpp').read_bytes()).hexdigest(),
                jobs=jobs,rows=[])
    for n,k,seed,method in jobs:
        tag=f'{n}_{k}_{seed}_{method}';log=out/f'{tag}.jsonl'
        if phase=='qc':
            cmd=[str(HERE/'qc_search'),str(seed),str(seconds),'1000000000000',str(log),method]
        else:
            inp=HERE/'paired'/f'{n}_{k}.txt'
            cmd=[str(HERE/'coset_search'),str(inp),str(seed),str(seconds),'1000000000000',str(log),method]
        resource=out/f'{tag}.resource.txt'
        with resource.open('w') as f:subprocess.run(['/usr/bin/time','-l' if platform.system()=='Darwin' else '-v',*cmd],stderr=f,check=True,cwd=ROOT)
        events=[json.loads(x) for x in log.read_text().splitlines()];last=events[-1]
        cert=out/f'{tag}.certificate.json'
        codes.write_cert(cert,last['rows'],n,dict(kind=f'{phase}-structured-search',seed=seed,method=method,
            source_sha256=result['source_sha256'],iterations=last['step'],
            parent=f'certificates/baseline_{n}_{k}.json' if phase=='coset' else 'four binary circulants, first identity, block size11',
            parameters={x:last[x] for x in ('polynomials','selector','shift') if x in last}))
        a,b=codes.check(cert),independent.check(cert);assert a['spectrum']==b['spectrum'] and a['d']==last['d']
        row=dict(n=n,k=k,seed=seed,method=method,initial_d=events[0]['d'],final_d=a['d'],
                 minimum_words=a['spectrum'][a['d']],steps=last['step'],seconds=last['seconds'],
                 cpu_seconds=last['cpu_seconds'],object=str(cert.relative_to(ROOT)),sha256=a['sha256'],
                 command=cmd,resource=str(resource.relative_to(ROOT)))
        if phase=='qc':
            rr,nn=codes.extend(last['rows'],n);ext=out/f'{tag}.extended.json'
            codes.write_cert(ext,rr,nn,dict(kind='parity-extension',parent=str(cert.relative_to(ROOT))))
            aa,bb=codes.check(ext),independent.check(ext);assert aa['spectrum']==bb['spectrum']
            row['extended_d']=aa['d'];row['extended_object']=str(ext.relative_to(ROOT))
        result['rows'].append(row)
        (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
        print(f"{phase} {len(result['rows'])}/{len(jobs)} {tag}: {row['initial_d']} -> {row['final_d']}, A_d={row['minimum_words']}",flush=True)
    result['finished_at']=datetime.now(timezone.utc).isoformat()
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['qc','coset']);p.add_argument('--seconds',type=float,default=20)
    a=p.parse_args();run(a.phase,a.seconds)
