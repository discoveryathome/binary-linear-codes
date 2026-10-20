"""Positive controls for bounded donor cards. Never posts or modifies frontier."""
import argparse,json
from pathlib import Path
import codes,independent
p=argparse.ArgumentParser();p.add_argument('task',choices=['replay','literature','qc','columns','certification','goppa']);a=p.parse_args()
targets=json.loads(Path('data/targets.json').read_text())
if a.task=='literature':
    r=json.loads(Path('results/closure.json').read_text());d={(x['n'],x['k']):x for x in r['rows']}
    excluded=[(35,10),(36,10),(36,11),(37,11),(37,12),(38,12)]
    assert all(d[x]['exclusion_lower']==d[x]['audited_upper'] for x in excluded)
    print('PASS six stale gaps excluded; audit final target upper-bound references next')
elif a.task=='certification':
    from information_sets import certified
    c,r=codes.read_cert('certificates/control_bch_32_16.json');proof=certified(r,c['n']);assert proof['d']==8
    print('PASS certified [32,16,8]; visits',proof['enumerated'])
elif a.task=='goppa':
    r=json.loads(Path('results/reconstruction-audit.json').read_text());items=[x for x in r if x['status']=='deferred' and 'Goppa' in x.get('reason','')]
    assert items;print('PASS deferred Goppa recipes identified:',json.dumps(items[:2]))
else:
    key={'replay':(41,12),'qc':(45,11),'columns':(52,10)}[a.task]
    t=next(x for x in targets if (x['n'],x['k'])==key);x=codes.check(t['object']);y=independent.check(t['object']);assert x['spectrum']==y['spectrum']
    print(f'PASS {a.task} baseline [{x["n"]},{x["k"]},{x["d"]}]; goal={t["improvement_goal"]}; upper={t["upper"]}')
