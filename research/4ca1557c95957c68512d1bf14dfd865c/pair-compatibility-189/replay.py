"""Conservative pair-word and independent bitset-join replay.

Physical-rotation oracle specialized from this session's separate PR #13 replay;
no import of the primary model, driver, C++ kernel or their field tables.
"""

import csv
import gzip
import hashlib
import io
import itertools
import json
import struct
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PREFIX = "research/4ca1557c95957c68512d1bf14dfd865c/pair-compatibility-189/"
BASE = "76267c387538b4fb0e802278530b575bab4d1f76"
SEED = "4ca1557c95957c68512d1bf14dfd865c"
M, MASK = (1 << 63) | 1, (1 << 63)-1
CAP = 2000000


def require(value, reason):
    if not value:
        raise ValueError(reason)


def product(a, b):
    value = 0
    for j in range(a.bit_length()):
        if (a >> j) & 1:
            value ^= b << j
    return value


def divide(a, b):
    quotient = 0
    for j in range(a.bit_length()-b.bit_length(),-1,-1):
        if (a >> (j+b.bit_length()-1)) & 1:
            a ^= b << j
            quotient |= 1 << j
    return quotient,a


def cyclic(a, b):
    value = product(a,b)
    while value > MASK:
        value = (value & MASK) ^ (value >> 63)
    return value


class Oracle:
    def __init__(self):
        remaining,factors = M,[]
        for degree in range(1,7):
            for factor in range((1 << degree)|1,1 << (degree+1),2):
                quotient,remainder = divide(remaining,factor)
                if not remainder:
                    factors.append(factor)
                    remaining = quotient
        require(remaining == 1 and [p.bit_length()-1 for p in factors] == [1,2,3,3]+[6]*9,
                "complete factorization")
        self.factors = factors[4:]
        self.pairs = list(itertools.combinations(self.factors,2))
        self.triples = list(itertools.combinations(self.factors,3))
        self.pair_templates = [(profile,pair) for profile in ("B","C") for pair in self.pairs]
        self.templates = [(profile,triple) for profile in ("B","C") for triple in self.triples]
        self.embedded,self.images,self.actions,self.roots = {},{},{},{}
        for factor in self.factors:
            generator,remainder = divide(M,factor)
            require(not remainder,"cyclic divisor")
            embedded = [product(generator,a) for a in range(64)]
            inverse = {value:a for a,value in enumerate(embedded)}
            require(len(inverse) == 64 and all(value.bit_count()%2 == 0 for value in embedded),
                    "embedding rank/evenness")
            action = [inverse[((value << 3)&MASK) | (value >> 60)] for value in embedded]
            self.actions[factor] = action
            self.embedded[factor] = embedded
            self.images[factor] = [[cyclic(value,scalar) for value in embedded] for scalar in range(64)]
            unseen,reps,periods = set(range(1,64)),[],[]
            while unseen:
                start = min(unseen)
                orbit,value = set(),start
                while value not in orbit:
                    require(value in unseen,"root orbit collision")
                    orbit.add(value)
                    value = action[value]
                require(value == start,"root orbit closure")
                unseen.difference_update(orbit)
                reps.append(start)
                periods.append(len(orbit))
            if set(periods) == {21}:
                require(len(reps) == 3,"primitive root coverage")
                self.roots[factor] = reps
        require(set(self.roots) == set(self.factors)-{0x49,0x57,0x75},"primitive root set")
        self.reps,self.orbits = {},{}
        for p,q in self.pairs:
            unseen = {a | (b << 6) for a in range(1,64) for b in range(1,64)}
            reps,orbits = [],{}
            while unseen:
                start = min(unseen)
                orbit,value = [],start
                while value not in orbit:
                    require(value in unseen,"physical pair orbit collision")
                    orbit.append(value)
                    value = self.actions[p][value&63] | (self.actions[q][value>>6] << 6)
                require(value == start,"physical pair orbit closure")
                unseen.difference_update(orbit)
                reps.append(start)
                orbits[start] = orbit
            expected = 567 if (p,q) == (0x57,0x75) else 189
            require(len(reps) == expected and sum(map(len,orbits.values())) == 3969 and
                    {len(o) for o in orbits.values()} == ({7} if expected == 567 else {21}),
                    "pair orbit coverage/short periods")
            self.reps[p,q],self.orbits[p,q] = reps,orbits
        g1,g2 = divide(M,3)[0],divide(M,7)[0]
        low = {"B":[(g2,0,g2),(g2<<1,0,g2<<1),(0,g2,g2),(0,g2<<1,g2<<1)],
               "C":[(g1,0,g1),(0,g1,g1),(g2,g2,g2),(g2<<1,g2<<1,g2<<1)]}
        self.low = {}
        for profile,rows in low.items():
            words = []
            for message in range(16):
                word = [0,0,0]
                for j,row in enumerate(rows):
                    if (message >> j)&1:
                        word = [a^b for a,b in zip(word,row)]
                require(sum(a.bit_count() for a in word)%2 == 0 and
                        all((((a << 3)&MASK) | (a >> 60)) == a for a in word),"low evenness/period")
                words.append(word)
            require(len({tuple(w) for w in words}) == 16,"low rank")
            self.low[profile] = words

    def word(self, profile, factors, scalars, message):
        require(profile in self.low and len(factors) in (2,3) and len(scalars) == 2*len(factors),
                "word model")
        require(0 < message < (1 << (4+6*len(factors))) and
                all(type(v) is int and 1 <= v < 64 for v in scalars),"nonzero message/unit scalars")
        a,b,c = self.low[profile][message&15]
        for j,factor in enumerate(factors):
            part = (message >> (4+6*j))&63
            a ^= self.embedded[factor][part]
            b ^= self.images[factor][scalars[2*j]][part]
            c ^= self.images[factor][scalars[2*j+1]][part]
        return a | (b << 63) | (c << 126)


def read_artifact(output, metadata, name):
    compressed = (output / (name+".gz")).read_bytes()
    info = metadata["artifacts"][name]
    require(hashlib.sha256(compressed).hexdigest() == info["compressed_sha256"],"compressed hash: "+name)
    raw = gzip.decompress(compressed)
    require(len(raw) == info["bytes"] and hashlib.sha256(raw).hexdigest() == info["raw_sha256"],
            "raw artifact hash/length: "+name)
    return raw


def pair_tables(oracle, cases, raw):
    require(len(cases) == 72 and len(raw) == 3*3143448,"pair table coverage/length")
    allowed,offset,total_allowed = {},0,0
    for case_id,(profile,pair) in enumerate(oracle.pair_templates):
        case = cases[case_id]
        reps = oracle.reps[pair]
        require(case["case"] == case_id and case["profile"] == profile and case["factors"] == list(pair)
                and case["domain"] == len(reps)**2 and case["representatives"] == len(reps),"pair case/domain")
        accepted = []
        for f in reps:
            for g in reps:
                message,weight = struct.unpack_from("<HB",raw,offset)
                offset += 3
                if not message:
                    require(weight == 0,"allowed marker weight")
                    accepted.append((f,g))
                else:
                    scalars = (f&63,g&63,f>>6,g>>6)
                    actual = oracle.word(profile,pair,scalars,message).bit_count()
                    require(actual == weight < 74 and weight%2 == 0,"pair witness weight")
        require(case["allowed"] == len(accepted),"pair allowed count")
        allowed[profile,pair] = accepted
        total_allowed += len(accepted)
    require(offset == len(raw),"pair binary trailing data")
    return allowed,total_allowed


def relations(oracle, allowed, profile):
    adjacency = {}
    bits = [1 << i for i in range(3969)]
    for pair in oracle.pairs:
        accepted = allowed[profile,pair]
        if not accepted:
            continue
        p,q = pair
        forward,backward = [0]*3969,[0]*3969
        for f,g in accepted:
            for fv in oracle.orbits[pair][f]:
                for gv in oracle.orbits[pair][g]:
                    a = ((fv&63)-1)*63+(gv&63)-1
                    b = ((fv>>6)-1)*63+(gv>>6)-1
                    require(not (forward[a]&bits[b]),"expanded edge duplicate")
                    forward[a] |= bits[b]
                    backward[b] |= bits[a]
        adjacency[p,q],adjacency[q,p] = forward,backward
    return adjacency


def assignments(oracle, adjacency, triple):
    if any(pair not in adjacency for pair in itertools.combinations(triple,2)):
        return
    roots = [p for p in triple if p in oracle.roots]
    require(roots,"nonprimitive triple not pair-excluded")
    root = min(roots)
    b,c = [p for p in triple if p != root]
    for rf in oracle.roots[root]:
        for rg in oracle.roots[root]:
            x = (rf-1)*63+rg-1
            bs = adjacency[root,b][x]
            while bs:
                bit = bs & -bs
                y = bit.bit_length()-1
                bs ^= bit
                cs = adjacency[root,c][x] & adjacency[b,c][y]
                while cs:
                    bit = cs & -cs
                    z = bit.bit_length()-1
                    cs ^= bit
                    states = {root:x,b:y,c:z}
                    scalars = tuple(v for p in triple for v in (states[p]//63+1,states[p]%63+1))
                    yield root,scalars


def count_assignments(oracle, adjacency, triple):
    if any(pair not in adjacency for pair in itertools.combinations(triple,2)):
        return 0
    roots = [p for p in triple if p in oracle.roots]
    require(roots,"nonprimitive triple not pair-excluded")
    root = min(roots)
    b,c = [p for p in triple if p != root]
    total = 0
    for rf in oracle.roots[root]:
        for rg in oracle.roots[root]:
            x = (rf-1)*63+rg-1
            bs = adjacency[root,b][x]
            while bs:
                bit = bs & -bs
                y = bit.bit_length()-1
                bs ^= bit
                total += (adjacency[root,c][x] & adjacency[b,c][y]).bit_count()
    return total


def full_record(oracle, profile, triple, scalars, template, index, record):
    values = {key:int(value) for key,value in record.items()}
    packed = sum(v << (6*j) for j,v in enumerate(scalars))
    require((values["template"],values["index"],values["scalars"]) ==
            (template,index,packed),"join assignment/order coverage")
    weight = oracle.word(profile,triple,scalars,values["message"]).bit_count()
    require(weight == values["d_or_upper"] and weight%2 == 0,"full witness weight")
    require(values["exact"] in (0,1),"full exact flag")
    if values["exact"]:
        require(weight >= 74 and values["minimum_words"] > 0,"target stopping rule")
    else:
        require(weight < 74 and values["minimum_words"] == 0,"full rejection upper bound")
    return values


def completion(summary, total, stopped, target):
    require(summary["full_checked"] == total and summary["complete"] == (not stopped) and
            summary["target_found"] == target,"global completion/count flags")
    require(not (target and not stopped),"target requires stopping")


def check_certificate(obj):
    require(obj.get("format") == "binary-generator-v1" and obj.get("q") == 2 and obj.get("n") == 189,
            "certificate format")
    k = obj.get("k")
    rows = obj.get("rows")
    require(k in (16,22) and isinstance(rows,list) and len(rows) == k and
            all(isinstance(row,str) and len(row) == 189 and set(row) <= {"0","1"} for row in rows),
            "certificate rows/dimensions")
    integers = [sum(int(bit) << j for j,bit in enumerate(row)) for row in rows]
    words = [0]
    for row in integers:
        words += [word^row for word in words]
    hist = [0]*190
    for word in words:
        hist[word.bit_count()] += 1
    require(hist[0] == 1 and sum(hist) == 1 << k,"certificate rank")
    d = next(i for i in range(1,190) if hist[i])
    require(type(obj.get("d")) is int and obj["d"] == d,"certificate exact distance")
    return integers,hist


def replay(output, progress=False, report=None):
    started = time.perf_counter()
    metadata = json.loads((output / "metadata.json").read_text())
    require(metadata.get("schema") == "pair-compatibility-v1" and metadata.get("seed") == SEED and
            metadata.get("base") == BASE,"schema/seed/base")
    require((metadata.get("threshold"),metadata.get("pair_choices"),metadata.get("full_cap")) ==
            (74,3143448,CAP),"fixed threshold/domain/cap")
    paths = {PREFIX+name for name in ("run.py","model.py","compatibility.cpp")}
    paths |= {"scripts/codes.py","scripts/large_verify.py",
              "research/readiness-20261021/certificates/189_22_72.json"}
    require(set(metadata["source_sha256"]) == paths,"source path set")
    for name,digest in metadata["source_sha256"].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest,"source hash: "+name)
    oracle = Oracle()
    pair_raw = read_artifact(output,metadata,"pair-witnesses.bin")
    allowed,total_allowed = pair_tables(oracle,json.loads((output/"pairs.json").read_text()),pair_raw)
    if progress:
        print(json.dumps({"pair_replay":"PASS","allowed":total_allowed}),flush=True)
    raw = read_artifact(output,metadata,"full-ledger.csv")
    reader = csv.DictReader(io.StringIO(raw.decode()))
    require(reader.fieldnames == ["template","index","scalars","message","d_or_upper","exact","minimum_words"],
            "full ledger header")
    records = iter(reader)
    cases = json.loads((output/"triples.json").read_text())
    summary = json.loads((output/"summary.json").read_text())
    require(len(cases) == 168 and summary["cap"] == CAP and summary["pair_choices"] == 3143448 and
            summary["pair_allowed"] == total_allowed,"triple/summary domain")
    require(type(summary["complete"]) is bool and type(summary["target_found"]) is bool,
            "summary flags")
    total,stopped,target = 0,False,False
    join_counts = []
    target_parameters = None
    for profile_id,profile in enumerate(("B","C")):
        adjacency = relations(oracle,allowed,profile)
        for triple_id,triple in enumerate(oracle.triples):
            template = profile_id*84+triple_id
            case = cases[template]
            require(case["template"] == template and case["profile"] == profile and case["factors"] == list(triple),
                    "triple order/parameters")
            compatible = count_assignments(oracle,adjacency,triple)
            join_counts.append({"template":template,"profile":profile,"factors":list(triple),
                                "allowed_join":compatible})
            expected_root,local,complete = 0,0,not stopped
            if not stopped:
                if all(pair in adjacency for pair in itertools.combinations(triple,2)):
                    expected_root = min(p for p in triple if p in oracle.roots)
                for root,scalars in assignments(oracle,adjacency,triple):
                    require(root == expected_root,"root normalization")
                    if total == CAP:
                        stopped,complete = True,False
                        break
                    record = next(records,None)
                    require(record is not None,"missing compatible assignment")
                    values = full_record(oracle,profile,triple,scalars,template,local,record)
                    local += 1
                    total += 1
                    if values["exact"]:
                        target_parameters = (profile,triple,scalars,values)
                        target,stopped,complete = True,True,False
                        break
            require(case["root"] == expected_root and case["checked"] == local and
                    type(case["complete"]) is bool and case["complete"] == complete,"triple completion/count/root")
            require(not complete or local == compatible,"complete join count")
        if progress:
            print(json.dumps({"profile":profile,"full_replayed":total}),flush=True)
    require(next(records,None) is None,"extra full assignment")
    completion(summary,total,stopped,target)
    if target:
        obj = json.loads((output/"target.json").read_text())
        rows,hist = check_certificate(obj)
        profile,triple,scalars,last = target_parameters
        require(obj["k"] == 22 and obj["d"] >= 74 and rows ==
                [oracle.word(profile,triple,scalars,1 << j) for j in range(22)],"target construction")
        require(hist == json.loads((output/"target-spectrum.json").read_text()) and
                obj["d"] == last["d_or_upper"] and hist[obj["d"]] == last["minimum_words"],"target spectrum")
    controls = json.loads((output/"controls/results.json").read_text())
    require(len(controls) == 5 and metadata["coordinate_controls"] == 240 and
            metadata["spectrum_controls"] == 5,"control coverage")
    for control in controls:
        path = output/"controls"/(control["name"]+".json")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == control["sha256"],"control hash")
        obj = json.loads(path.read_text())
        rows,hist = check_certificate(obj)
        require(hist == json.loads(path.with_name(control["name"]+"-spectrum.json").read_text()) and
                control["k"] == obj["k"] and control["d"] == obj["d"] and
                control["minimum_words"] == hist[obj["d"]],"control spectrum")
    join_total = sum(c["allowed_join"] for c in join_counts)
    totals = {profile:sum(c["allowed_join"] for c in join_counts if c["profile"] == profile)
              for profile in ("B","C")}
    if report is not None:
        require(not report.exists(),"new report path required")
        report.parent.mkdir(parents=True,exist_ok=True)
        report.write_text(json.dumps({"schema":"allowed-join-counts-v1","seed":SEED,"base":BASE,
                                     "allowed_join":join_total,"by_profile":totals,"templates":join_counts,
                                     "full_checked":total,"complete_distance_check":not stopped,
                                     "claim":"Exact conservative allowed-join count; untested distances are unknown."},
                                    indent=2)+"\n")
    return {"status":"PASS","pair_choices":3143448,"pair_allowed":total_allowed,"full_checked":total,
            "allowed_join":join_total,"allowed_join_by_profile":totals,
            "complete":not stopped,"target_found":target,"excludes_full_BC":not stopped and not target,
            "seconds":time.perf_counter()-started,"evidence_level":"author-checked"}


if __name__ == "__main__":
    if len(sys.argv) not in (2,4) or (len(sys.argv) == 4 and sys.argv[2] != "--report"):
        raise SystemExit("usage: replay.py RUN_DIRECTORY [--report NEW_REPORT_JSON]")
    report = Path(sys.argv[3]) if len(sys.argv) == 4 else None
    print(json.dumps(replay(Path(sys.argv[1]),progress=True,report=report),sort_keys=True))
