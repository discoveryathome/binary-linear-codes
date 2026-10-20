import argparse,json,time
from pathlib import Path
import codes,independent
p=argparse.ArgumentParser();p.add_argument('paths',nargs='*');p.add_argument('--all',action='store_true');a=p.parse_args()
paths=sorted(Path('certificates').glob('*.json')) if a.all else map(Path,a.paths)
t=time.perf_counter();count=0
for path in paths:
    x=codes.check(path);y=independent.check(path)
    if any(x[k]!=y[k] for k in y):raise ValueError('checker disagreement')
    count+=1;print(f'PASS {path} [{x["n"]},{x["k"]},{x["d"]}]')
if not count:raise SystemExit('No certificates selected')
print(json.dumps(dict(verified=count,seconds=time.perf_counter()-t)))
