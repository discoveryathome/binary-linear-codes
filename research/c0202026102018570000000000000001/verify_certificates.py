"""Verify all saved trial generator certificates with both original implementations."""
import json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import codes,independent
def run():
    t=time.perf_counter();count=0;by_k={}
    # Materialize structured-run initial/distance witnesses, whose exact matrices
    # were retained in JSONL but not yet wrapped in the standard certificate.
    for phase in ['coset','qc']:
        for row in json.loads((HERE/phase/'manifest.json').read_text())['rows']:
            tag=Path(row['object']).name.removesuffix('.certificate.json')
            log=HERE/phase/f'{tag}.jsonl'
            for idx,event in enumerate(map(json.loads,log.read_text().splitlines())):
                if event['type'] not in ('initial','distance'):continue
                path=HERE/phase/f'{tag}.milestone_{idx}.json'
                if not path.exists():
                    codes.write_cert(path,event['rows'],row['n'],dict(kind='structured-search-milestone',
                        run=tag,phase=phase,step=event['step'],log=str(log.relative_to(ROOT))))
                c,r=codes.read_cert(path)
                assert r==event['rows'] and c['d']==event['d']
    paths=list(HERE.glob('*.json'))
    for phase in ['paired','heldout','coset','qc']:paths+=list((HERE/phase).glob('*.json'))
    for path in sorted(paths):
        c=json.loads(path.read_text())
        if not isinstance(c,dict) or c.get('format')!='binary-generator-v1':continue
        a,b=codes.check(path),independent.check(path);assert a['spectrum']==b['spectrum']
        count+=1;by_k[str(c['k'])]=by_k.get(str(c['k']),0)+1
    result=dict(status='PASS',certificates=count,by_dimension=by_k,seconds=time.perf_counter()-t,
        note='Two independently implemented checkers; same author session, no independent human review.')
    (HERE/'certificate_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':run()
