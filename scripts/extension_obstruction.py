"""Exact one-column extension feasibility for a FIXED generator matrix.
To increase distance d to d+1, every weight-d message m must satisfy m.x=1.
An inconsistent subsystem gives XOR messages=0 with odd cardinality.
This is not a nonexistence proof for arbitrary [n+1,k,d+1] codes.
"""
import json
from pathlib import Path
import codes

def analyze(rows,n):
    d=codes.distance(rows,n);words=[0]
    for r in rows:words += [v^r for v in words]
    messages=[m for m,w in enumerate(words) if w.bit_count()==d]
    equations={}
    for index,m in enumerate(messages):
        lhs=m;rhs=1;support=1<<index
        while lhs:
            pivot=lhs.bit_length()-1
            if pivot not in equations:equations[pivot]=(lhs,rhs,support);break
            a,b,c=equations[pivot];lhs^=a;rhs^=b;support^=c
        if lhs==0 and rhs:
            proof=[messages[j] for j in range(len(messages)) if support>>j&1]
            assert len(proof)%2==1
            x=0
            for m in proof:x^=m
            assert x==0
            return dict(status='impossible-for-this-matrix',d=d,messages=proof,minimal_words=len(messages))
    x=0
    for pivot,(lhs,rhs,_) in sorted(equations.items()):
        if ((lhs&x).bit_count()%2)!=rhs:x^=1<<pivot
    assert all((m&x).bit_count()%2==1 for m in messages)
    return dict(status='extension-exists',d=d,column=[(x>>i)&1 for i in range(len(rows))],minimal_words=len(messages))

def verify_obstruction(rows,n,proof):
    # Small independent algebraic proof check, exhaustive d handled by other checker.
    if len(proof)%2!=1:raise ValueError('even number of equations')
    total=[0]*len(rows);d=codes.distance(rows,n)
    for m in proof:
        if type(m)!=int or not 1<=m<2**len(rows):raise ValueError('message range')
        word=0
        for i,r in enumerate(rows):
            if (m//2**i)%2:word^=r;total[i]^=1
        if word.bit_count()!=d:raise ValueError('not a minimum word')
    if any(total):raise ValueError('not a dependency')
    return True

def run(output='results/extensions.json'):
    out=[]
    for t in json.loads(Path('data/targets.json').read_text()):
        c,r=codes.read_cert(t['object']);result=analyze(r,c['n'])
        if result['status'].startswith('impossible'):verify_obstruction(r,c['n'],result['messages'])
        else:
            rr,nn=codes.extend(r,c['n'],result['column']);assert codes.distance(rr,nn)==c['d']+1
        out.append(dict(object=t['object'],n=c['n'],k=c['k'],**result))
    Path(output).write_text(json.dumps(out,indent=2)+'\n')
    print('PASS extension feasibility:',{s:sum(x['status']==s for x in out) for s in ('impossible-for-this-matrix','extension-exists')})
if __name__=='__main__':run()
