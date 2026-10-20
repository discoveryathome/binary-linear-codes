"""Exact fixed-matrix obstruction to a strictly better distance after <=2
column replacements. Results are not unrestricted nonexistence proofs."""
import itertools,json,sys,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import codes

def words(rows):
    w=[0]
    for r in rows:w += [x^r for x in w]
    return w

def affine_equations(messages,k):
    """Solve m.x=1, retaining an odd XOR-zero dependency if inconsistent."""
    piv={}
    for m in messages:
        x=m;b=1;proof={m}
        while x:
            p=x.bit_length()-1
            if p not in piv:piv[p]=(x,b,proof);break
            y,c,q=piv[p];x^=y;b^=c;proof^=q
        if not x and b:return None,sorted(proof)
    solutions=[x for x in range(1<<k) if all((x&m).bit_count()%2 for m in messages)]
    return solutions,None

def analyze(path):
    c,r=codes.read_cert(path);w=words(r);n,k,d=c['n'],c['k'],c['d']
    low=[m for m in range(1,1<<k) if w[m].bit_count()==d]
    proofs=[];unresolved=[]
    for i,j in itertools.combinations(range(n),2):
        mask=(1<<i)|(1<<j)
        witness=next((m for m in low if w[m]&mask==mask),None)
        if witness is not None:
            proofs.append(dict(pair=[i,j],kind='containing-minimum-word',message=witness))
            continue
        residual=[(x&~mask).bit_count() for x in w]
        forced=[m for m in range(1,1<<k) if residual[m]==d-1]
        solutions,dependency=affine_equations(forced,k)
        if dependency is not None:
            proofs.append(dict(pair=[i,j],kind='odd-parity-dependency',messages=dependency))
            continue
        clauses=[m for m in range(1,1<<k) if residual[m]==d]
        feasible=next(((a,b) for a in solutions for b in solutions if a<=b and
                       all(((a&m).bit_count()|(b&m).bit_count())&1 for m in clauses)),None)
        if feasible is None:
            proofs.append(dict(pair=[i,j],kind='exhausted-affine-solutions',
                               solution_count=len(solutions)))
        else:
            unresolved.append(dict(pair=[i,j],replacement_columns=feasible))
    return dict(n=n,k=k,d=d,parent=str(path.relative_to(ROOT)),
                parent_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                total_pairs=n*(n-1)//2,proved=len(proofs),unresolved=unresolved,proofs=proofs)

def verify(result):
    """Check each direct/linear proof against direct codeword reconstruction."""
    path=ROOT/result['parent']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==result['parent_sha256']
    c=json.loads(path.read_text());n,k,d=c['n'],c['k'],c['d']
    # Deliberately use strings and message dot products rather than integer XOR words.
    def word(m):
        return [sum(int(c['rows'][i][j]) for i in range(k) if (m>>i)&1)%2 for j in range(n)]
    seen=set()
    for p in result['proofs']:
        pair=tuple(p['pair']);assert pair not in seen;seen.add(pair)
        i,j=pair;assert 0<=i<j<n
        if p['kind']=='containing-minimum-word':
            m=p['message'];assert 0<m<1<<k
            x=word(m);assert sum(x)==d and x[i]==x[j]==1
        elif p['kind']=='odd-parity-dependency':
            ms=p['messages'];assert len(ms)%2==1 and len(set(ms))==len(ms)
            assert all(0<m<1<<k for m in ms)
            for bit in range(k):assert sum((m>>bit)&1 for m in ms)%2==0
            for m in ms:
                x=word(m);assert sum(x)-x[i]-x[j]==d-1
        elif p['kind']=='exhausted-affine-solutions':
            residual={m:sum(v for z,v in enumerate(word(m)) if z not in pair) for m in range(1,1<<k)}
            forced=[m for m,v in residual.items() if v==d-1]
            sols=[a for a in range(1<<k) if all(sum(((a>>b)&1)*((m>>b)&1) for b in range(k))%2 for m in forced)]
            assert len(sols)==p['solution_count']
            for a in sols:
                for b in sols:
                    assert any(v+sum(((a>>z)&1)*((m>>z)&1) for z in range(k))%2+
                               sum(((b>>z)&1)*((m>>z)&1) for z in range(k))%2<d+1
                               for m,v in residual.items())
        else:raise ValueError('unknown proof')
    assert len(seen)==result['proved']
    if not result['unresolved']:assert len(seen)==n*(n-1)//2
    return True

if __name__=='__main__':
    t=time.perf_counter();out=[]
    for target in json.loads((ROOT/'data/targets.json').read_text()):
        r=analyze(ROOT/target['object']);verify(r);out.append(r)
        counts={kind:sum(p['kind']==kind for p in r['proofs']) for kind in sorted(set(p['kind'] for p in r['proofs']))}
        print(r['n'],r['k'],counts,'unresolved',len(r['unresolved']),flush=True)
    dest=Path(__file__).with_name('obstructions.json')
    dest.write_text(json.dumps(dict(seconds=time.perf_counter()-t,rows=out),indent=2)+'\n')
