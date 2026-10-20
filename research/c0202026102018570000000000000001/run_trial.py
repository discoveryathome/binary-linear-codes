"""One worker, randomized paired ordering, wall-bounded search; deterministic
replay uses each final step count. Run from repository root."""
import argparse,hashlib,json,platform,random,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import codes,independent

def utc():return datetime.now(timezone.utc).isoformat()
def run(seconds,seeds,phase,budget='wall',starts=('cold','warm')):
    out=HERE/phase;out.mkdir(exist_ok=True)
    targets={(t['n'],t['k']):t for t in json.loads((ROOT/'data/targets.json').read_text())}
    jobs=[(n,k,start,seed,method) for n,k in [(52,10),(45,11),(42,12),(62,11)]
          for start in starts for seed in seeds for method in ['blind','walsh']]
    random.Random(20261020).shuffle(jobs)
    binary='search' if budget=='wall' else 'search_cpu'
    meta=dict(started_at=utc(),phase=phase,seconds_per_run=seconds,budget=budget,seeds=seeds,
              source_sha256=hashlib.sha256((HERE/f'{binary}.cpp').read_bytes()).hexdigest(),
              python=platform.python_version(),platform=platform.platform(),
              cpu='Apple M2; 8 logical cores; 24 GiB RAM; shared loaded host',
              search_workers=1,accelerator=None,job_order=jobs,rows=[])
    (out/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
    for n,k,start,seed,method in jobs:
        tag=f'{n}_{k}_{start}_{seed}_{method}'
        c,r=codes.read_cert(ROOT/f'certificates/baseline_{n}_{k}.json')
        inp=out/f'{n}_{k}.txt'
        inp.write_text(f'{n} {k}\n'+' '.join(map(str,r))+'\n')
        log=out/f'{tag}.jsonl';resource=out/f'{tag}.resource.txt'
        command=[str(HERE/binary),str(inp),method,str(seed),str(seconds),
                 '1000000000000',str(log),start,str(targets[n,k]['closure_lower']+1)]
        with resource.open('w') as stderr:
            subprocess.run(['/usr/bin/time','-l' if platform.system()=='Darwin' else '-v',*command],stderr=stderr,check=True,cwd=ROOT)
        events=[json.loads(x) for x in log.read_text().splitlines()]
        last=events[-1];r=last['rows'];h=codes.spectrum(r,n)
        assert codes.distance(r,n)==last['d'] and h[last['d']]==last['minimum_words']
        cert=out/f'{tag}.certificate.json'
        codes.write_cert(cert,r,n,dict(kind='timed-contributor-search',method=method,
             seed=seed,start=start,iterations=last['step'],parent=f'certificates/baseline_{n}_{k}.json' if start=='warm' else 'random systematic',
             log=str(log.relative_to(ROOT)),source_sha256=meta['source_sha256'],
             credit='Published baseline retained as provenance; no novelty inferred from matrix hash.'))
        a,b=codes.check(cert),independent.check(cert)
        assert a['spectrum']==b['spectrum']
        milestones=[]
        for idx,event in enumerate(events):
            if event['type'] not in ('initial','distance'):continue
            f=out/f'{tag}.milestone_{idx}.json'
            codes.write_cert(f,event['rows'],n,dict(kind='search-milestone',run=tag,step=event['step']))
            aa,bb=codes.check(f),independent.check(f)
            assert aa['spectrum']==bb['spectrum'] and aa['d']==event['d']
            milestones.append(dict(step=event['step'],seconds=event['seconds'],d=event['d'],object=str(f.relative_to(ROOT))))
        row=dict(n=n,k=k,start=start,seed=seed,method=method,initial_d=events[0]['d'],
                 final_d=a['d'],minimum_words=h[a['d']],published_lower=targets[n,k]['published_lower'],
                 exclusion_lower=targets[n,k]['closure_lower'],upper=targets[n,k]['upper'],
                 candidate_record=a['d']>targets[n,k]['closure_lower'],
                 seconds=last['seconds'],cpu_seconds=last['cpu_seconds'],steps=last['step'],
                 alternatives=last['alternatives'],accepted=last['accepted'],shakes=last['shakes'],
                 object=str(cert.relative_to(ROOT)),sha256=a['sha256'],milestones=milestones,
                 command=command,resource=str(resource.relative_to(ROOT)))
        meta['rows'].append(row);meta['updated_at']=utc()
        (out/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
        print(f"{len(meta['rows'])}/{len(jobs)} {tag}: {row['initial_d']} -> {a['d']} (known {row['exclusion_lower']}); minwords {row['minimum_words']}; CPU {row['cpu_seconds']:.2f}s",flush=True)
    meta['finished_at']=utc();(out/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=15)
    p.add_argument('--seeds',default='101,102,103');p.add_argument('--phase',default='paired')
    p.add_argument('--budget',choices=['wall','cpu'],default='wall')
    p.add_argument('--starts',default='cold,warm')
    a=p.parse_args();run(a.seconds,list(map(int,a.seeds.split(','))),a.phase,a.budget,a.starts.split(','))
