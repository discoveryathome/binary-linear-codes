import json,sys
from pathlib import Path
x,y=[json.loads(Path(p).read_text()) for p in sys.argv[1:]]
for key in ('seed','iterations_per_restart','restarts','local_proposals','structured_candidates','candidate_records','closure_sha256','targets_sha256'):
    if x[key]!=y[key]:raise ValueError(key)
for a,b in zip(x['rows'],y['rows'],strict=True):
    for key in ('n','k','best_d','candidate_record'):
        if a[key]!=b[key]:raise ValueError(key)
    for aa,bb in zip(a['runs'],b['runs'],strict=True):
        for key in ('initial_d','best_d','final_d','accepted','rank_rejects','matrix_sha256'):
            if aa[key]!=bb[key]:raise ValueError((a['n'],a['k'],key))
print('PASS deterministic search scores and exact matrix hashes; elapsed time excluded')
