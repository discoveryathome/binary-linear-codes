"""Direct oracle for the complete fixed parent field-scalar neighborhood."""

import csv
import gzip
import hashlib
import io
import itertools
import json
import sys
import time
from pathlib import Path

from replay import Oracle, ROOT, PREFIX, SEED, M, MASK, divide, product, require, exact_spectrum


def pack(values):
    return sum(value << (6*i) for i,value in enumerate(values))


def expected_choices(parent):
    choices=[pack(parent)]
    for i in range(6):
        for a in range(1,64):
            if a != parent[i]:
                values=parent.copy();values[i]=a;choices.append(pack(values))
    for i,j in itertools.combinations(range(6),2):
        for a in range(1,64):
            if a==parent[i]:continue
            for b in range(1,64):
                if b==parent[j]:continue
                values=parent.copy();values[i]=a;values[j]=b;choices.append(pack(values))
    require(len(choices)==len(set(choices))==58033,"complete neighborhood generation")
    return choices


def rank(rows):
    pivots={}
    for row in rows:
        while row:
            bit=row.bit_length()-1
            if bit not in pivots:pivots[bit]=row;break
            row ^= pivots[bit]
    return len(pivots)


def check(output):
    started=time.perf_counter()
    meta=json.loads((output/"metadata.json").read_text());summary=json.loads((output/"summary.json").read_text())
    require(meta.get("schema")=="field-neighborhood-v1" and meta.get("seed")==SEED and
            meta.get("base")=="76267c387538b4fb0e802278530b575bab4d1f76" and meta.get("domain_size")==58033,
            "pivot scope")
    expected={PREFIX+n for n in ("run_pivot.py","pivot_model.py","pivot-search.cpp","model.py","run_search.py")}
    expected|={"scripts/codes.py","scripts/large_verify.py","research/readiness-20261021/certificates/189_22_72.json"}
    require(set(meta["source_sha256"])==expected,"pivot source set")
    for name,digest in meta["source_sha256"].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,"source hash: "+name)
    parent=json.loads((ROOT/"research/readiness-20261021/certificates/189_22_72.json").read_text())
    original_factors=[sum(1<<i for i in f) for f in parent["provenance"]["construction"][4]]
    require(meta["degree_three"]==next(f for f in original_factors if f.bit_length()==4) and
            meta["factors"]==[f for f in original_factors if f.bit_length()==7],"fixed parent factors")
    parent_scalars=meta["parent_scalars"]
    require(len(parent_scalars)==6 and all(type(v) is int and 1<=v<64 for v in parent_scalars),"parent unit coordinates")
    oracle=Oracle();g1,_=divide(M,3);g3,r=divide(M,meta["degree_three"]);require(r==0,"degree-three divisor")
    low=[]
    for message in range(16):
        value=g1 if message&1 else 0
        value ^= product(g3,message>>1)
        low.append((value,value,value))
    def word(scalars,message):
        require(type(message) is int and 0<message<(1<<22),"nonzero pivot message")
        a,b,c=low[message&15]
        for j,factor in enumerate(meta["factors"]):
            part=(message>>(4+6*j))&63
            a^=oracle.embedded[factor][part]
            b^=oracle.images[factor][scalars[2*j]][part]
            c^=oracle.images[factor][scalars[2*j+1]][part]
        return a|(b<<63)|(c<<126)
    normalized=json.loads((output/"normalized-parent.json").read_text())
    normalized_rows=[sum(int(v)<<j for j,v in enumerate(row)) for row in normalized["rows"]]
    require(normalized_rows==[word(parent_scalars,1<<j) for j in range(22)],"normalized model rows")
    hist=exact_spectrum(normalized)
    require(normalized["d"]==72 and hist[72]==2394 and
            hist==json.loads((output/"normalized-parent-spectrum.json").read_text()),"normalized spectrum")
    def rotate(value,r):return ((value<<r)&MASK)|(value>>(63-r)) if r else value
    original_rows=[sum(int(v)<<j for j,v in enumerate(row)) for row in parent["rows"]]
    rotations=meta["block_rotations"]
    require(len(rotations)==3 and rotations[0]==0 and all(0<=r<7 for r in rotations),"block rotations")
    transformed=[]
    for row in original_rows:
        blocks=[rotate((row>>(63*j))&MASK,rotations[j]) for j in range(3)]
        transformed.append(blocks[0]|(blocks[1]<<63)|(blocks[2]<<126))
    require(rank(normalized_rows+transformed)==22,"published-parent row-space equivalence")
    compressed=(output/"ledger.csv.gz").read_bytes();raw=gzip.decompress(compressed)
    require(hashlib.sha256(compressed).hexdigest()==meta["compressed_ledger_sha256"] and
            hashlib.sha256(raw).hexdigest()==meta["ledger_sha256"],"pivot ledger hashes")
    choices=expected_choices(parent_scalars);count=0;maximum=0
    for item in csv.DictReader(io.StringIO(raw.decode())):
        row={k:int(v) for k,v in item.items()}
        require(row["index"]==count and count<58033 and row["genome"]==choices[count],"neighborhood coverage/order")
        scalars=[(row["genome"]>>(6*j))&63 for j in range(6)]
        require(all(1<=v<64 for v in scalars) and
                row["changes"]==sum(a!=b for a,b in zip(scalars,parent_scalars))<=2,"one/two replacements")
        weight=word(scalars,row["message"]).bit_count()
        require(weight==row["weight"] and 0<weight<=summary["maximum_witness"],"pivot witness")
        require(row["exact"] in (0,1) and (row["exact"]==1 or row["minimum_words"]==0),"pivot exactness flag")
        if not summary["target_found"]:require(weight<=72 and row["exact"]==0,"null threshold witness")
        maximum=max(maximum,weight);count+=1
    require(count==meta["evaluated"]==summary["evaluated"] and maximum==summary["maximum_witness"],"pivot final counts")
    require(meta["target_found"]==summary["target_found"],"pivot target status")
    if not summary["target_found"]:require(count==58033 and maximum<=72,"complete finite neighborhood bound")
    else:
        candidate=json.loads((output/"candidate.json").read_text());candidate_hist=exact_spectrum(candidate)
        require(candidate["d"]>=73 and candidate_hist==json.loads((output/"candidate-spectrum.json").read_text()),"target candidate spectrum")
    return {"status":"PASS","evaluated":count,"domain_size":58033,"maximum_witness":maximum,
            "attained_parent_distance":72,"target_found":summary["target_found"],
            "evidence_level":"author-checked","seconds":time.perf_counter()-started}


if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: replay_pivot.py PIVOT_DIRECTORY")
    print(json.dumps(check(Path(sys.argv[1])),sort_keys=True))
