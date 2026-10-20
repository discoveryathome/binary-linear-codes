"""Offline, read-only verification of published baselines and experiment artifacts."""
import json,hashlib,time,subprocess,sys,csv
from pathlib import Path
import codes,independent,closure,reconstruct
from extension_obstruction import verify_obstruction
from information_sets import certified

def require(b,message):
    if not b:raise ValueError(message)

def main():
    start=time.perf_counter();targets=json.loads(Path('data/targets.json').read_text())
    frontier=json.loads(Path('discover/frontier.json').read_text())
    for artifact in frontier['artifacts']:
        require(hashlib.sha256(Path(artifact['path']).read_bytes()).hexdigest()==artifact['sha256'],'frontier artifact hash '+artifact['path'])
    with Path('data/records.csv').open() as f: records=list(csv.DictReader(f))
    require(len(records)==len(targets),'record row count')
    require(len({(r['n'],r['k']) for r in records})==len(records),'duplicate record key')
    for record,target in zip(records,targets):
        for field in ('n','k','published_lower','closure_lower','verified_d','upper'):
            require(int(record[field])==target[field],'CSV/target disagreement '+field)
        require(record['object']==target['object'],'CSV certificate mismatch')
    for source in json.loads(Path('data/source-index.json').read_text()):
        require(hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256'],'source hash '+source['path'])
    saved=json.loads(Path('results/closure.json').read_text());fresh=json.loads(json.dumps(closure.run(output=None,quiet=True)))
    require(saved==fresh,'closure replay mismatch')
    bd={(r['n'],r['k']):r for r in saved['rows']};count=0
    for t in targets:
        x=codes.check(t['object']);y=independent.check(t['object'])
        require(all(x[k]==y[k] for k in y),'checker mismatch')
        require((x['n'],x['k'],x['d'])==(t['n'],t['k'],t['verified_d']),'record mismatch')
        c,rows=codes.read_cert(t['object']);(rr,n),steps=reconstruct.recipe(Path(c['provenance']['snapshot']))
        require(rr==rows and n==c['n'],'recipe mismatch')
        b=bd[t['n'],t['k']]
        require(t['published_lower']==b['table_lower'] and t['closure_lower']==b['exclusion_lower'] and t['upper']==b['audited_upper'],'bound mismatch')
        require(t['published_lower']<=t['verified_d']<=t['closure_lower']<t['upper'],'target is not an open audited gap')
        count+=1
    for t in json.loads(Path('results/extensions.json').read_text()):
        c,r=codes.read_cert(t['object'])
        if t['status']=='impossible-for-this-matrix':verify_obstruction(r,c['n'],t['messages'])
        else:
            rr,n=codes.extend(r,c['n'],t['column']);require(codes.distance(rr,n)==c['d']+1,'extension failure')
    for t in json.loads(Path('results/information-sets.json').read_text()):
        c,r=codes.read_cert(t['object']);result=certified(r,c['n'],t['sets'])
        require(result['d']==independent.check(t['object'])['d']==t['d'],'certified distance mismatch')
        count+=1
    ex=json.loads(Path('results/experiment/experiment.json').read_text())
    require(ex['targets_sha256']==hashlib.sha256(Path('data/targets.json').read_bytes()).hexdigest(),'experiment target version')
    require(ex['closure_sha256']==hashlib.sha256(Path('results/closure.json').read_bytes()).hexdigest(),'experiment closure version')
    for row in ex['rows']:
        for run in row['runs']:
            x=codes.check(run['object']);y=independent.check(run['object']);require(x['spectrum']==y['spectrum'] and x['d']==run['final_d'],'experiment verification')
            count+=1
    subprocess.run([sys.executable,'-m','unittest','discover','-s','tests'],check=True)
    print(json.dumps(dict(status='PASS',targets=len(targets),certificates=count,seconds=time.perf_counter()-start,novel_records=ex['candidate_records'],note='Two implementations; author-checked, no independent reviewer or optimality proof.')))
if __name__=='__main__':main()
