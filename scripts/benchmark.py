import json,time,statistics,platform
from pathlib import Path
import codes,independent
out=[]
for target in json.loads(Path('data/targets.json').read_text()):
    r={'n':target['n'],'k':target['k'],'object':target['object']}
    for name,check in [('gray',codes.check),('column',independent.check)]:
        times=[]
        for _ in range(3):
            t=time.perf_counter();check(target['object']);times.append(time.perf_counter()-t)
        r[name+'_seconds_median']=statistics.median(times)
    out.append(r)
Path('results/verification-benchmark.json').write_text(json.dumps(dict(python=platform.python_version(),repetitions=3,warning='Shared host; descriptive timing, not controlled speedup experiment',rows=out),indent=2)+'\n')
print('PASS verification benchmark; max median combined seconds',max(r['gray_seconds_median']+r['column_seconds_median'] for r in out))
