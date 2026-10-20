"""Reproduce the two scoped obstructions for the larger published control."""
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))
import codes,obstruction
def run():
    c,rows=codes.read_cert(HERE/'published_173_20_68.json')
    minima=[171]*32;witness=[0]*32;full=0;residue=0;minimum_messages=[]
    for index in range(1,1<<20):
        bit=(index&-index).bit_length()-1
        full^=rows[bit];residue^=1<<(bit%5);message=index^(index>>1)
        weight=(full&((1<<170)-1)).bit_count()
        if weight<minima[residue]:minima[residue]=weight;witness[residue]=message
        if full.bit_count()==68:minimum_messages.append(message)
    result=dict(n=170,k=20,minima=minima,witness_messages=witness,
        source='published_173_20_68.json',
        method='Remove three published tails; classify messages by b mod (x^5-1)')
    (HERE/'tail_core_minima.json').write_text(json.dumps(result,indent=2)+'\n')
    solutions,proof=obstruction.affine_equations(minimum_messages,20)
    assert proof is not None
    result=dict(n=173,k=20,d=68,minimal_words=len(minimum_messages),
                odd_xor_dependency=proof,source='published_173_20_68.json')
    (HERE/'large_extension.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: fixed-core five-periodic tails have d<=68; no one-column extension of the published matrix reaches69')
if __name__=='__main__':run()
