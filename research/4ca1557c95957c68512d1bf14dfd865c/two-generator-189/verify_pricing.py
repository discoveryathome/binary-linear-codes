"""Independent finite checks of the small constituent and field-pricing tables."""

import collections
import itertools
import json
import sys
from pathlib import Path

from replay import Oracle, divide, product, require


def histogram(rows, n):
    words=[0]
    for row in rows:words += [word^row for word in words]
    require(len(set(words))==len(words),"small-model rank")
    hist=[0]*(n+1)
    for word in words:
        require(0<=word<(1<<n),"small-model length")
        hist[word.bit_count()]+=1
    return hist


def gf4(a,b):return divide(product(a,b),7)[1]


def check(data):
    require(data.get("schema")=="three-block-constituent-pricing-v1","pricing schema")
    require(data.get("seed")=="4ca1557c95957c68512d1bf14dfd865c" and
            data.get("base")=="76267c387538b4fb0e802278530b575bab4d1f76","pricing provenance")
    patterns=[(a,b,c,d) for a in range(3) for b in range(3) for c in range(2) for d in range(10)
              if a+2*b+3*c+6*d==22]
    require(data["dimension_patterns"]==[list(x) for x in patterns] and
            patterns==[(0,2,0,3),(1,0,1,3),(2,1,0,3)],"high-distance dimension patterns")
    # Every three-bit vector has a unique degree-one plus degree-two CRT split.
    split={((7*t)^product(3,s)):(t,s) for t in range(2) for s in range(4)}
    require(len(split)==8,"low CRT split")
    normal4=set()
    for case in data["low_B"]:
        require(len(case["rows"])==4,"rank-four low model")
        normal=tuple(case["normal"])
        require(len(normal)==3 and next((v for v in normal if v),None)==1 and
                all(0<=v<4 for v in normal),"normalized GF4 plane")
        require(normal not in normal4,"duplicate GF4 plane");normal4.add(normal)
        for row in case["rows"]:
            values=[split[(row>>(3*j))&7] for j in range(3)]
            require(all(t==0 for t,s in values),"B degree-one absence")
            total=0
            for coefficient,(_,symbol) in zip(normal,values):total ^= gf4(coefficient,symbol)
            require(total==0,"B plane equation")
        hist=histogram(case["rows"],9);distance=next(i for i in range(1,10) if hist[i])
        require(hist==case["spectrum"] and distance==case["d"] and hist[distance]==case["minimum_words"],"B spectrum")
        require(distance==(4 if all(normal) else 2),"B MDS distinction")
    require(len(normal4)==21 and len(data["low_B"])==21,"all GF4 planes")
    seen=set();normals2=set()
    for case in data["low_C"]:
        require(len(case["rows"])==4,"rank-four low model")
        normal=tuple(case["normal"]);line=tuple(case["line"])
        require(len(normal)==3 and any(normal) and all(v in (0,1) for v in normal),"binary plane")
        require(line in normal4 and (normal,line) not in seen,"C line and pair coverage")
        seen.add((normal,line));normals2.add(normal)
        pivot=next(j for j,v in enumerate(line) if v)
        inverse=next(v for v in range(1,4) if gf4(line[pivot],v)==1)
        for row in case["rows"]:
            values=[split[(row>>(3*j))&7] for j in range(3)]
            require(sum(a*t for a,(t,s) in zip(normal,values))%2==0,"C binary plane equation")
            scalar=gf4(values[pivot][1],inverse)
            require(all(s==gf4(scalar,v) for (_,s),v in zip(values,line)),"C GF4 line equation")
        hist=histogram(case["rows"],9);distance=next(i for i in range(1,10) if hist[i])
        require(hist==case["spectrum"] and distance==case["d"] and hist[distance]==case["minimum_words"],"C spectrum")
        require(distance==(4 if all(line) else 2) if all(normal) else distance<=3,"C necessary support")
    require(len(normals2)==7 and len(seen)==147 and len(data["low_C"])==147,"all C plane/line pairs")
    # The two degree-three constituents reduce to three even length-seven blocks.
    image=[]
    for scalar in range(64):
        weights=[]
        for message in range(64):
            value=product(product(3,message),scalar)
            while value>=128:value=(value&127)^(value>>7)
            require(value.bit_count()%2==0,"even length-seven block")
            weights.append(value.bit_count())
        image.append(weights)
    first=[product(3,m).bit_count() for m in range(64)]
    require(len(data["two_degree3_cases"])==4096,"degree-three pair count")
    for index,entry in enumerate(data["two_degree3_cases"]):
        f,g=divmod(index,64)
        require(entry[:2]==[f,g],"degree-three pair coverage")
        weights=[first[m]+image[f][m]+image[g][m] for m in range(1,64)]
        d=min(weights)
        require(entry[2:]==[d,weights.count(d)] and d<=8,"degree-three exact bound")
    oracle=Oracle();require(len(data["degree6"])==9,"all degree-six factors")
    modulus=(1<<63)|1
    require(divide(modulus,3)[0].bit_count()==63,"degree-one block weight")
    g2,_=divide(modulus,7)
    require(all(product(g2,a).bit_count()==42 for a in range(1,4)),"degree-two symbol weights")
    for factor in (0xB,0xD):
        generator,remainder=divide(modulus,factor)
        require(remainder==0 and all(product(generator,a).bit_count()==36 for a in range(1,8)),
                "degree-three symbol weights")
    for record,factor in zip(data["degree6"],oracle.factors):
        require(record["factor"]==factor,"degree-six order")
        weights=[v.bit_count() for v in oracle.embedded[factor]]
        images=[[v.bit_count() for v in row] for row in oracle.images[factor]]
        distances=[min(weights[m]+images[f][m]+images[g][m] for m in range(1,64))
                   for f in range(1,64) for g in range(1,64)]
        require(distances==record["unit_pair_distances"] and max(distances)==record["maximum_line_d"],
                "all degree-six scalar-pair bounds")
        require({str(k):v for k,v in collections.Counter(distances).items()}==record["distance_histogram"],"field histogram")
    # Integer bounds used to eliminate higher constituent multiplicities.
    require(sum((73+(1<<i)-1)//(1<<i) for i in range(3))>126,"rank-three support bound")
    require(sum((65+(1<<i)-1)//(1<<i) for i in range(6))>126,"rank-six support bound")
    require(sum((10+(1<<i)-1)//(1<<i) for i in range(6))>21,"even rank-six bound")
    return {"status":"PASS","GF4_planes":21,"binary_plane_GF4_line_pairs":147,
            "degree_three_pair_cases":4096,"degree_six_scalar_pairs":9*63*63,
            "necessary_profiles":patterns,"evidence_level":"author-checked"}


if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: verify_pricing.py PRICING_JSON")
    print(json.dumps(check(json.loads(Path(sys.argv[1]).read_text())),sort_keys=True))
