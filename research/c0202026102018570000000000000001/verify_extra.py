"""Small independently readable checks for the new scoped obstructions."""
import importlib.util,itertools,json,random,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT/'scripts'))
import codes,obstruction,repair
def direct_word(c,m):
    return [sum(int(c['rows'][i][j]) for i in range(c['k']) if (m>>i)&1)%2 for j in range(c['n'])]
def run():
    rng=random.Random(3301)
    for _ in range(1000):
        k=5;ms=rng.sample(range(1,1<<k),rng.randrange(12))
        expected=[x for x in range(1<<k) if all((m&x).bit_count()%2 for m in ms)]
        assert sorted(repair.affine(ms,k))==expected
        one=repair.affine(ms,k,False)
        assert bool(one)==bool(expected)
        if one:assert one[0] in expected
    # Stored per-pair proofs are checked using string arithmetic and direct parity.
    obs=json.loads((HERE/'obstructions.json').read_text())
    for item in obs['rows']:obstruction.verify(item)
    bad=json.loads(json.dumps(obs['rows'][0]));bad['proofs'][0]['message']=0
    try:obstruction.verify(bad)
    except AssertionError:pass
    else:raise AssertionError('malformed obstruction accepted')
    bad=json.loads(json.dumps(obs['rows'][0]));bad['proofs'].pop()
    try:obstruction.verify(bad)
    except AssertionError:pass
    else:raise AssertionError('missing pair accepted')
    # A zero-residue core word bounds all tails depending only on that residue.
    c=json.loads((HERE/'published_173_20_68.json').read_text())
    minima=json.loads((HERE/'tail_core_minima.json').read_text());m=minima['witness_messages'][0]
    assert 0<m<1<<20
    for residue in range(5):assert sum((m>>i)&1 for i in range(residue,20,5))%2==0
    assert sum(direct_word(c,m)[:170])==68
    # An odd dependency among minimum messages rules out every single added column.
    ext=json.loads((HERE/'large_extension.json').read_text());ms=ext['odd_xor_dependency']
    assert len(ms)%2 and all(0<m<1<<20 for m in ms)
    for i in range(20):assert sum((m>>i)&1 for m in ms)%2==0
    for m in ms:assert sum(direct_word(c,m))==68
    print('PASS: 1000 affine controls, 20854 pair proofs, adversarial rejection, large-code tail and extension obstructions')
if __name__=='__main__':run()
