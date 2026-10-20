"""A portable certificate that the originally proposed fixed-QC-parent task
cannot improve [45,11,16]. This is a family bound, not a new global optimum."""
import json,sys,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import codes,independent

def run():
    polys=[int(x,8) for x in ['3','4631','11327']]
    rows=[]
    for j in range(15):
        rr=[((g<<j)|(g>>(15-j)))&32767 for g in polys]
        rows.append(sum(((g>>t)&1)<<(3*t+a) for a,g in enumerate(rr) for t in range(15)))
    rows=codes.basis(rows);source=ROOT/'data/sources/45_11.html'
    cert=HERE/'qc_parent_45_14.json'
    codes.write_cert(cert,rows,45,dict(kind='published-QC-parent',
        source='https://www.codetables.de/BKLC/BKLC.php?q=2&n=45&k=11',
        snapshot_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        polynomials_octal=['3','4631','11327'],
        credit='Published QC construction; source table credits Bo0. Replication only.'))
    a,b=codes.check(cert),independent.check(cert)
    assert a['spectrum']==b['spectrum'] and a['k']==14 and a['d']==16
    assert all(w%4==0 for w,count in enumerate(a['spectrum']) if count)
    terms=[(20+(1<<i)-1)//(1<<i) for i in range(11)]
    assert sum(terms)==46>45
    result=dict(parent=str(cert.relative_to(ROOT)),parent_sha256=a['sha256'],
        spectrum=a['spectrum'],dimension=11,next_possible_distance=20,
        griesmer_terms=terms,required_length=sum(terms),available_length=45,
        conclusion='Every 11-dimensional subcode of this fixed parent has distance exactly 16.',
        reasoning='Subcode distance is at least 16. Divisibility by four excludes 17,18,19. The binary Griesmer bound excludes distance >=20 for length45 dimension11.',
        scope='All 11-dimensional subspaces of this published parent, not all binary [45,11] codes.',
        independent_implementations=True,independent_human_review=False)
    (HERE/'qc_family_proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['conclusion'])
if __name__=='__main__':run()
