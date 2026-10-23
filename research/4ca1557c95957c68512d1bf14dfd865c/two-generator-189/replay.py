"""Directly check every tested genotype's low word and the best full spectra.

No imports from model.py, the C++ search, or its field-multiplication tables.
"""

import csv
import gzip
import hashlib
import io
import itertools
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PREFIX = "research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/"
SEED = "4ca1557c95957c68512d1bf14dfd865c"
M = (1 << 63) | 1
MASK = (1 << 63) - 1


def require(value, reason):
    if not value:
        raise ValueError(reason)


def product(a, b):
    result = 0
    for j in range(a.bit_length()):
        if (a >> j) & 1:
            result ^= b << j
    return result


def divide(a, b):
    q = 0
    for j in range(a.bit_length() - b.bit_length(), -1, -1):
        if (a >> (j + b.bit_length() - 1)) & 1:
            a ^= b << j
            q |= 1 << j
    return q, a


def cyclic(a, b):
    result = product(a, b)
    while result > MASK:
        result = (result & MASK) ^ (result >> 63)
    return result


class Oracle:
    def __init__(self):
        remaining, factors = M, []
        for degree in range(1, 7):
            for factor in range((1 << degree) | 1, 1 << (degree + 1), 2):
                q, r = divide(remaining, factor)
                if r == 0:
                    factors.append(factor)
                    remaining = q
        require(remaining == 1, "complete factorization")
        require([f.bit_length()-1 for f in factors] == [1,2,3,3]+[6]*9,
                "factor degrees")
        self.factors = factors[4:]
        self.triples = list(itertools.combinations(self.factors, 3))
        self.templates = [(profile, triple) for profile in ("B", "C") for triple in self.triples]
        self.embedded, self.images = {}, {}
        for factor in self.factors:
            generator, remainder = divide(M, factor)
            require(remainder == 0, "minimal cyclic divisor")
            embedded = [product(generator, a) for a in range(64)]
            require(all(v.bit_count()%2 == 0 for v in embedded), "even field block")
            self.embedded[factor] = embedded
            self.images[factor] = [[cyclic(value, scalar) for value in embedded]
                                   for scalar in range(64)]
        g1, _ = divide(M, 3)
        g2, _ = divide(M, 7)
        low = {
            "B": [(g2,0,g2),(g2<<1,0,g2<<1),(0,g2,g2),(0,g2<<1,g2<<1)],
            "C": [(g1,0,g1),(0,g1,g1),(g2,g2,g2),(g2<<1,g2<<1,g2<<1)],
        }
        self.low = {}
        for profile, rows in low.items():
            words = []
            for message in range(16):
                word = [0,0,0]
                for j, row in enumerate(rows):
                    if (message>>j)&1:
                        word = [a^b for a,b in zip(word,row)]
                require(sum(v.bit_count() for v in word)%2 == 0, "even low word")
                words.append(word)
            self.low[profile] = words

    def word(self, template, scalars, message):
        require(0 <= template < 168 and 0 < message < (1<<22), "template or nonzero message")
        require(len(scalars)==6 and all(1 <= x < 64 for x in scalars), "unit scalars")
        profile, factors = self.templates[template]
        a,b,c = self.low[profile][message&15]
        for j,factor in enumerate(factors):
            part=(message>>(4+6*j))&63
            a ^= self.embedded[factor][part]
            b ^= self.images[factor][scalars[2*j]][part]
            c ^= self.images[factor][scalars[2*j+1]][part]
        return a | (b<<63) | (c<<126)


def source_hashes(metadata):
    expected = {PREFIX+name for name in ("run_search.py","model.py","search.cpp","price.py")}
    expected |= {"scripts/codes.py","scripts/large_verify.py",
                 "research/readiness-20261021/certificates/189_22_72.json"}
    require(set(metadata["source_sha256"])==expected, "source path set")
    for name,digest in metadata["source_sha256"].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, "source hash: "+name)


def exact_spectrum(certificate):
    require(certificate.get("format")=="binary-generator-v1" and certificate.get("q")==2,
            "certificate format")
    n,k=certificate.get("n"),certificate.get("k")
    require(type(n) is int and type(k) is int and n==189 and k==22, "certificate parameters")
    strings=certificate.get("rows")
    require(isinstance(strings,list) and len(strings)==22 and
            all(isinstance(s,str) and len(s)==189 and not set(s)-{"0","1"} for s in strings),
            "certificate rows")
    rows=[int(s,2) for s in strings]
    pivots={}
    for value in rows:
        while value:
            bit=value.bit_length()-1
            if bit not in pivots:
                pivots[bit]=value
                break
            value ^= pivots[bit]
    require(len(pivots)==22, "certificate rank")
    def subsets(values):
        out=[0]
        for value in values:
            out += [word^value for word in out]
        return out
    hist=[0]*190
    for left in subsets(rows[:11]):
        for right in subsets(rows[11:]):
            hist[(left^right).bit_count()]+=1
    require(hist[0]==1 and sum(hist)==(1<<22), "certificate enumeration")
    distance=next(i for i in range(1,190) if hist[i])
    require(certificate.get("d")==distance, "certificate exact distance")
    return hist


def check_records(records, metadata, summary, oracle):
    require(metadata.get("schema")=="two-generator-search-v1" and metadata.get("seed")==SEED,
            "schema or seed")
    require(metadata.get("base")=="76267c387538b4fb0e802278530b575bab4d1f76" and
            metadata.get("proposal_cap")==199296 and metadata.get("target")==73,
            "scope header")
    payload=json.dumps([SEED,"two-generator-189-round3"],separators=(",",":"))
    seed64=int(hashlib.sha256(payload.encode()).hexdigest()[:16],16)
    require(metadata["seed_payload"]==payload and metadata["seed64"]==seed64==summary["seed64"],
            "executed seed derivation")
    require(len(summary["templates"])==168, "template coverage")
    for actual,(profile,factors) in zip(summary["templates"],oracle.templates):
        require(actual["profile"]==profile and actual["factors"]==list(factors), "template ordering")
    maximum=max(c["d"] for c in metadata["certificates"])
    require(maximum>=1 and maximum<=84, "attained sample bound")
    seen=set();duplicates=0;count=0;exact=0
    for raw in records:
        row={k:int(v) for k,v in raw.items()}
        require(row["index"]==count and count<199296, "proposal sequence/cap")
        t=row["template"];encoded=row["genome"]
        require(0<=t<168 and 0<=encoded<(1<<36), "genotype range")
        scalars=[(encoded>>(6*j))&63 for j in range(6)]
        require(row["stage"] in (0,1) and row["exact"] in (0,1) and
                row["accepted"] in (0,1) and row["duplicate"] in (0,1), "record flags")
        if row["stage"]==0:
            require(row["restart"]==-1 and 0<=row["step"]<16 and row["exact"]==1,
                    "initial control record")
        else:
            require(0<=row["restart"]<3 and 0<=row["step"]<4096, "restart budget")
        duplicate=(t,encoded) in seen
        require(bool(row["duplicate"])==duplicate, "duplicate accounting")
        duplicates += duplicate;seen.add((t,encoded))
        weight=oracle.word(t,scalars,row["message"]).bit_count()
        require(weight==row["d_or_upper"] and 0<weight<=maximum, "proposal witness weight")
        if row["exact"]:
            require(1<=row["minimum_words"]<(1<<22), "measured multiplicity")
            exact+=1
        else:
            require(row["minimum_words"]==0 and row["accepted"]==0, "early rejection semantics")
        count+=1
    require(count==metadata["proposals"]==summary["proposals"] and
            duplicates==metadata["duplicates"]==summary["duplicates"], "final proposal counts")
    require(bool(metadata["target_found"])==bool(summary["target_found"])==(maximum>=73),
            "target status")
    if not metadata["target_found"]:
        require(count==199296 and maximum<=72, "complete bounded null run")
    return {"status":"PASS","proposals":count,"duplicates":duplicates,
            "distinct_parameter_choices":len(seen),"exact_fitness_records":exact,
            "attained_tested_list_maximum":maximum,"target_found":metadata["target_found"],
            "evidence_level":"author-checked"}


def check(output):
    started=time.perf_counter();metadata=json.loads((output/"metadata.json").read_text())
    summary=json.loads((output/"summary.json").read_text());source_hashes(metadata)
    compressed=(output/"ledger.csv.gz").read_bytes();raw=gzip.decompress(compressed)
    require(hashlib.sha256(compressed).hexdigest()==metadata["compressed_ledger_sha256"], "compressed ledger hash")
    require(hashlib.sha256(raw).hexdigest()==metadata["ledger_sha256"], "decoded ledger hash")
    oracle=Oracle()
    report=check_records(csv.DictReader(io.StringIO(raw.decode())),metadata,summary,oracle)
    profiles=[c["profile"] for c in metadata["certificates"]]
    require(len(profiles)==len(set(profiles)) and set(profiles)<={"B","C"}, "best certificate profiles")
    if not metadata["target_found"]:require(set(profiles)=={"B","C"}, "missing best profile")
    for control in metadata["certificates"]:
        name=control["object"]
        require(name in ("best-B.json","best-C.json"), "certificate path")
        path=output/name
        require(hashlib.sha256(path.read_bytes()).hexdigest()==control["sha256"], "certificate hash")
        certificate=json.loads(path.read_text());provenance=certificate["provenance"]
        profile=provenance["profile"];factors=tuple(provenance["degree_six_factors"])
        require(profile==control["profile"] and name==f"best-{profile}.json", "best profile metadata")
        t=oracle.templates.index((profile,factors));scalars=provenance["scalars"]
        rows=[oracle.word(t,scalars,1<<j) for j in range(22)]
        actual=[sum(int(bit)<<j for j,bit in enumerate(row)) for row in certificate["rows"]]
        require(rows==actual, "best matrix model")
        hist=exact_spectrum(certificate);d=control["d"]
        require(d==certificate["d"], "best distance metadata")
        require(hist[d]==control["minimum_words"] and
                hist==json.loads((output/f"best-{profile}-spectrum.json").read_text()), "best full spectrum")
        require(all(hist[i]==0 for i in range(1,190,2)), "even family spectrum")
    report["seconds"]=time.perf_counter()-started
    return report


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: replay.py RUN_DIRECTORY")
    print(json.dumps(check(Path(sys.argv[1])),sort_keys=True))
