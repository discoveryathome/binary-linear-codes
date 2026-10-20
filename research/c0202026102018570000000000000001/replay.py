"""Replay selected (default) or all recorded search runs by fixed iteration count.
Matrices, counters and final objectives must agree; timings need not agree."""
import argparse,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def run(all_runs=False):
    out=HERE/'replay';out.mkdir(exist_ok=True);checked=[]
    for phase in ['paired','heldout','coset','qc']:
        data=json.loads((HERE/phase/'manifest.json').read_text());rows=data['rows']
        if not all_runs:
            if phase in ['paired','heldout']:
                rows=[x for x in rows if x['n']==62 and x['start']=='cold' and x['seed']==(101 if phase=='paired' else 901)]
            else:rows=[rows[0]]
        for j,row in enumerate(rows):
            cmd=list(row['command']);cmd[0]=str(HERE/Path(cmd[0]).name)
            original=Path(row['object']).name.replace('.certificate.json','.jsonl')
            events=[json.loads(x) for x in (HERE/phase/original).read_text().splitlines()]
            last=events[-1];log=out/f'{phase}_{j}.jsonl'
            if phase in ['paired','heldout']:
                cmd[1]=str(HERE/phase/Path(cmd[1]).name);cmd[4]='0';cmd[5]=str(last['step']);cmd[6]=str(log)
            elif phase=='coset':
                cmd[1]=str(HERE/'paired'/Path(cmd[1]).name);cmd[3]='0';cmd[4]=str(last['step']);cmd[5]=str(log)
            else:cmd[2]='0';cmd[3]=str(last['step']);cmd[4]=str(log)
            subprocess.run(cmd,cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
            fresh=json.loads(log.read_text().splitlines()[-1])
            keys=[k for k in last if k not in ('seconds','cpu_seconds')]
            assert {k:last[k] for k in keys}=={k:fresh[k] for k in keys},(phase,j)
            checked.append(dict(phase=phase,object=row['object'],steps=last['step']))
    (out/'receipt.json').write_text(json.dumps(dict(status='PASS',runs=checked),indent=2)+'\n')
    print('PASS deterministic replay:',len(checked),'runs')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--all',action='store_true');a=p.parse_args();run(a.all)
