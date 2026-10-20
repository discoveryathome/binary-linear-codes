"""Offline public demonstration using a real verified generator certificate.
No simulated research progress: the selected code and its provenance are printed.
"""
import argparse,random,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import codes,independent
def demo(path,message,errors,seed):
    c,r=codes.read_cert(path);a,b=codes.check(path),independent.check(path)
    assert a['spectrum']==b['spectrum']
    if len(message)!=c['k'] or set(message)-{'0','1'}:raise ValueError(f"message needs {c['k']} binary digits")
    if not 0<=errors<=c['n']:raise ValueError('error count')
    m=int(message[::-1],2);word=0
    for i,row in enumerate(r):
        if (m>>i)&1:word^=row
    positions=sorted(random.Random(seed).sample(range(c['n']),errors))
    noisy=word
    for j in positions:noisy^=1<<j
    allwords=[0]
    for row in r:allwords += [w^row for w in allwords]
    distances=[(w^noisy).bit_count() for w in allwords]
    nearest=min(distances);decoded=[i for i,x in enumerate(distances) if x==nearest]
    def bits(x):return ''.join(str((x>>j)&1) for j in range(c['n']))
    print(f"Real code [{c['n']},{c['k']},{c['d']}], checked by both exhaustive verifiers")
    print(f"Certificate: {path}")
    print("Source category:",c['provenance'].get('kind','unspecified'))
    print("Message:  ",message)
    print("Encoded:  ",bits(word))
    print("Corrupted:",bits(noisy))
    print("Changes:  ",''.join('^' if j in positions else ' ' for j in range(c['n'])))
    print(f"Changed {errors} bits. Guaranteed correction radius: {(c['d']-1)//2}.")
    if decoded==[m]:print("Recovered the original message uniquely.")
    elif len(decoded)>1:print(f"Ambiguous: {len(decoded)} closest messages.")
    else:print("Closest-message decoding chose a different message.")
    print("A successful example outside the radius is not a stronger guarantee.")
    print("These are known-distance constructions; this demo is not evidence of a new record.")
    return decoded==[m]
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--certificate',type=Path,default=ROOT/'certificates/baseline_45_11.json')
    p.add_argument('--message',default='10110100101')
    p.add_argument('--errors',type=int,default=7);p.add_argument('--seed',type=int,default=20261020)
    a=p.parse_args();demo(a.certificate,a.message,a.errors,a.seed)
