"""Direct cyclic-word, physical-rotation and spectrum replay; no model imports."""

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
PREFIX = "research/4ca1557c95957c68512d1bf14dfd865c/pair-pricing-189/"
BASE = "76267c387538b4fb0e802278530b575bab4d1f76"
SEED = "4ca1557c95957c68512d1bf14dfd865c"
M, MASK = (1 << 63) | 1, (1 << 63) - 1


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
    for j in range(a.bit_length() - b.bit_length(), -1, -1):
        if (a >> (j + b.bit_length() - 1)) & 1:
            a ^= b << j
            quotient |= 1 << j
    return quotient, a


def cyclic(a, b):
    value = product(a, b)
    while value > MASK:
        value = (value & MASK) ^ (value >> 63)
    return value


class Oracle:
    def __init__(self):
        remaining, factors = M, []
        for degree in range(1, 7):
            for factor in range((1 << degree) | 1, 1 << (degree+1), 2):
                quotient, remainder = divide(remaining, factor)
                if not remainder:
                    factors.append(factor)
                    remaining = quotient
        require(remaining == 1, "factorization completeness")
        require([p.bit_length()-1 for p in factors] == [1,2,3,3]+[6]*9, "factor degrees")
        self.factors = factors[4:]
        self.pairs = list(itertools.combinations(self.factors, 2))
        self.templates = [(profile, pair) for profile in ("B", "C") for pair in self.pairs]
        self.embedded, self.images, actions = {}, {}, {}
        for factor in self.factors:
            generator, remainder = divide(M, factor)
            require(remainder == 0, "cyclic divisor")
            embedded = [product(generator, a) for a in range(64)]
            require(all(value.bit_count() % 2 == 0 for value in embedded), "even degree-six block")
            inverse = {value: a for a, value in enumerate(embedded)}
            require(len(inverse) == 64, "embedding rank")
            actions[factor] = [inverse[((value << 3) & MASK) | (value >> 60)]
                               for value in embedded]
            self.embedded[factor] = embedded
            self.images[factor] = [[cyclic(value, scalar) for value in embedded]
                                   for scalar in range(64)]
        self.reps = {}
        total = 0
        for p, q in self.pairs:
            unseen = {a | (b << 6) for a in range(1,64) for b in range(1,64)}
            reps, periods = [], []
            while unseen:
                start = min(unseen)
                orbit, value = set(), start
                while value not in orbit:
                    require(value in unseen, "physical orbit collision")
                    orbit.add(value)
                    value = actions[p][value & 63] | (actions[q][value >> 6] << 6)
                require(value == start, "physical orbit closure")
                unseen.difference_update(orbit)
                reps.append(start)
                periods.append(len(orbit))
            expected = 567 if (p,q) == (0x57,0x75) else 189
            require(len(reps) == expected and sum(periods) == 3969, "orbit coverage/short periods")
            require(set(periods) == ({7} if expected == 567 else {21}), "orbit periods")
            self.reps[p,q] = reps
            total += len(reps)**2 * 2
        require(total == 3143448, "normalized domain")
        g1, g2 = divide(M,3)[0], divide(M,7)[0]
        low = {"B": [(g2,0,g2),(g2<<1,0,g2<<1),(0,g2,g2),(0,g2<<1,g2<<1)],
               "C": [(g1,0,g1),(0,g1,g1),(g2,g2,g2),(g2<<1,g2<<1,g2<<1)]}
        self.low = {}
        for profile, rows in low.items():
            words = []
            for message in range(16):
                word = [0,0,0]
                for j, row in enumerate(rows):
                    if (message >> j) & 1:
                        word = [a ^ b for a,b in zip(word,row)]
                require(all(((a << 3) & MASK) | (a >> 60) == a for a in word), "low period three")
                require(sum(a.bit_count() for a in word) % 2 == 0, "even low word")
                words.append(word)
            require(len({tuple(w) for w in words}) == 16, "low rank four")
            self.low[profile] = words

    def word(self, case, f, g, message):
        require(0 <= case < 72 and 0 < message < 65536, "case/nonzero message")
        require(all(1 <= v < 64 for v in (f&63,f>>6,g&63,g>>6)), "unit scalars")
        profile, pair = self.templates[case]
        a,b,c = self.low[profile][message & 15]
        for j, factor in enumerate(pair):
            part = (message >> (4+6*j)) & 63
            a ^= self.embedded[factor][part]
            b ^= self.images[factor][(f >> (6*j)) & 63][part]
            c ^= self.images[factor][(g >> (6*j)) & 63][part]
        return a | (b << 63) | (c << 126)


def spectrum(obj):
    require(obj.get("format") == "binary-generator-v1" and obj.get("q") == 2,
            "certificate format")
    require((obj.get("n"),obj.get("k")) == (189,16), "certificate dimensions")
    strings = obj.get("rows")
    require(isinstance(strings,list) and len(strings) == 16 and
            all(isinstance(row,str) and len(row) == 189 and set(row) <= {"0","1"}
                for row in strings), "certificate rows")
    rows = [sum(int(bit) << j for j,bit in enumerate(row)) for row in strings]
    words = [0]
    for row in rows:
        words += [value ^ row for value in words]
    hist = [0]*190
    for word in words:
        hist[word.bit_count()] += 1
    require(hist[0] == 1 and sum(hist) == 65536, "certificate rank")
    distance = next(i for i in range(1,190) if hist[i])
    require(type(obj.get("d")) is int and obj["d"] == distance >= 74, "certificate threshold/distance")
    require(all(not hist[i] for i in range(1,190,2)), "even code")
    return rows, hist


def replay(output):
    started = time.perf_counter()
    metadata = json.loads((output / "metadata.json").read_text())
    require(metadata.get("schema") == "pair-threshold-pricing-v1" and
            metadata.get("seed") == SEED and metadata.get("base") == BASE, "schema/seed/base")
    require((metadata.get("threshold"),metadata.get("cases"),metadata.get("maximum_domain")) ==
            (74,72,3143448), "fixed threshold/domain")
    paths = {PREFIX+name for name in ("run.py","model.py","threshold.cpp")}
    paths |= {"scripts/codes.py","scripts/large_verify.py"}
    require(set(metadata["source_sha256"]) == paths, "source path set")
    for name, digest in metadata["source_sha256"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, "source hash: "+name)
    compressed = (output / "ledger.csv.gz").read_bytes()
    require(hashlib.sha256(compressed).hexdigest() == metadata["compressed_ledger_sha256"], "compressed hash")
    raw = gzip.decompress(compressed)
    require(hashlib.sha256(raw).hexdigest() == metadata["ledger_sha256"], "ledger hash")
    oracle = Oracle()
    cases = json.loads((output / "cases.json").read_text())
    require(len(cases) == 72, "case coverage")
    for i, case in enumerate(cases):
        profile, pair = oracle.templates[i]
        reps = oracle.reps[pair]
        require(case["case"] == i and case["profile"] == profile and
                case["factors"] == list(pair), "case order/parameters")
        require(type(case["survivor"]) is bool and case["domain"] == len(reps)**2 and
                case["orbit_representatives"] == len(reps), "case domain")
        require(type(case["tested"]) is int and 0 < case["tested"] <= case["domain"], "tested prefix")
        require(case["survivor"] or case["tested"] == case["domain"], "exhausted case coverage")
    counts, finals = [0]*72, {}
    current, total = 0, 0
    reader = csv.DictReader(io.StringIO(raw.decode()))
    require(reader.fieldnames == ["case","index","f_pair","g_pair","exact","d_or_upper",
                                 "minimum_words","message"], "ledger header")
    for record in reader:
        values = {key: int(value) for key,value in record.items()}
        case_id, index = values["case"], values["index"]
        require(current < 72 and case_id == current and index == counts[current], "ordered prefix coverage")
        case = cases[case_id]
        reps = oracle.reps[tuple(case["factors"])]
        require(index < case["tested"], "extra proposal")
        f,g = values["f_pair"],values["g_pair"]
        require((f,g) == (reps[index//len(reps)],reps[index%len(reps)]), "orbit representative choice")
        weight = oracle.word(case_id,f,g,values["message"]).bit_count()
        require(weight == values["d_or_upper"] and weight % 2 == 0, "witness weight")
        require(values["exact"] in (0,1), "exact flag")
        if values["exact"]:
            require(case["survivor"] and index == case["tested"]-1 and weight >= 74 and
                    values["minimum_words"] > 0, "survivor stopping rule")
        else:
            require(weight < 74 and values["minimum_words"] == 0, "rejection upper bound")
        counts[case_id] += 1
        total += 1
        if counts[case_id] == case["tested"]:
            require(bool(values["exact"]) == case["survivor"], "missing/false survivor")
            finals[case_id] = values
            current += 1
    require(current == 72 and total == metadata["tested"] and
            counts == [c["tested"] for c in cases], "complete ledger coverage")
    spectra = json.loads((output / "spectra.json").read_text())
    require(set(spectra) == {str(c["case"]) for c in cases if c["survivor"]}, "spectrum coverage")
    for case in cases:
        if not case["survivor"]:
            continue
        i = case["case"]
        last = finals[i]
        expected_name = f"certificates/{case['profile']}-{case['factors'][0]:x}-{case['factors'][1]:x}.json"
        require(case["certificate"] == expected_name, "certificate path")
        path = output / expected_name
        require(hashlib.sha256(path.read_bytes()).hexdigest() == case["sha256"], "certificate hash")
        obj = json.loads(path.read_text())
        rows,hist = spectrum(obj)
        require(rows == [oracle.word(i,last["f_pair"],last["g_pair"],1 << j) for j in range(16)],
                "certificate construction")
        require(hist == spectra[str(i)] and case["d"] == obj["d"] == last["d_or_upper"] and
                case["minimum_words"] == hist[obj["d"]] == last["minimum_words"], "attaining spectrum/metadata")
        provenance = obj["provenance"]
        require(provenance["profile"] == case["profile"] and provenance["factors"] == case["factors"] and
                provenance["f_pair"] == last["f_pair"] and provenance["g_pair"] == last["g_pair"] and
                provenance["seed"] == SEED and provenance["base"] == BASE, "certificate provenance")
    survivors = sum(c["survivor"] for c in cases)
    require(survivors == metadata["surviving_pairs"] and metadata["coordinate_controls"] == 72,
            "survivor/control count")
    triangles = {}
    for profile in ("B","C"):
        edges = {tuple(c["factors"]) for c in cases if c["profile"] == profile and c["survivor"]}
        triangles[profile] = [list(triple) for triple in itertools.combinations(oracle.factors,3)
                              if all(edge in edges for edge in itertools.combinations(triple,2))]
    return {"status": "PASS", "cases": 72, "tested": total, "surviving_pairs": survivors,
            "excluded_pairs": 72-survivors, "eligible_triples": {p: len(t) for p,t in triangles.items()},
            "seconds": time.perf_counter()-started, "evidence_level": "author-checked"}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: replay.py RUN_DIRECTORY")
    print(json.dumps(replay(Path(sys.argv[1])), sort_keys=True))
