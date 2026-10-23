"""Replay the core bound with direct convolution, without search-side imports."""

import gzip
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
M = (1 << 85) | 1
P = (1 << 5) | 1
MASK = (1 << 85) - 1


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def bounded(value, low, high, reason):
    require(type(value) is int and low <= value < high, reason)
    return value


def product(a, b):
    value = 0
    for i in range(a.bit_length()):
        if (a >> i) & 1:
            value ^= b << i
    return value


def divide(a, b):
    quotient = 0
    for i in range(a.bit_length() - b.bit_length(), -1, -1):
        if (a >> (i + b.bit_length() - 1)) & 1:
            a ^= b << i
            quotient |= 1 << i
    return quotient, a


def core_word(generator, multiplier, message):
    left = product(generator, message)
    require(left <= MASK, "first block exceeds length 85")
    right = product(left, multiplier)
    while right > MASK:
        right = (right & MASK) ^ (right >> 85)
    return left | (right << 85)


def word_weight(generator, multiplier, message):
    return core_word(generator, multiplier, message).bit_count()


def irreducible(factor):
    for degree in range(1, (factor.bit_length() - 1) // 2 + 1):
        for divisor in range((1 << degree) | 1, 1 << (degree + 1), 2):
            if divide(factor, divisor)[1] == 0:
                return False
    return True


def domain_pairs():
    factors8 = [f for f in range(257, 512, 2) if divide(M, f)[1] == 0]
    require(len(factors8) == 10 and product(3, 31) == P, "factor catalogue")
    factors = [3, 31] + factors8
    require(all(irreducible(f) for f in factors), "reducible factor")
    divisors = [1]
    for factor in factors:
        divisors += [product(divisor, factor) for divisor in divisors]
    require(max(divisors) == M and len(set(divisors)) == 4096,
            "complete squarefree factorization")
    pairs = set(itertools.combinations(factors8, 2))
    checks21 = {product(P, product(*pair)) for pair in pairs}
    require(checks21 == {d for d in divisors if d.bit_length() == 22},
            "all degree-21 divisors")
    return pairs


def structural_checks():
    patterns = [(a, b, c) for a in range(3) for b in range(3) for c in range(21)
                if a + 4 * b + 8 * c == 21]
    require(patterns == [(1, 1, 2)], "constituent dimension patterns")
    # An axis constituent of degree four/eight has effective length 85.
    require(sum((45 + (1 << i) - 1) // (1 << i) for i in range(4)) == 86,
            "rank-four Griesmer exclusion")
    require(sum((41 + (1 << i) - 1) // (1 << i) for i in range(8)) == 86,
            "rank-eight Griesmer exclusion")


def check(result):
    require(result.get("schema") == "normalized-qc-core-witnesses-v1", "schema")
    for key, value in {
        "seed": "4ca1557c95957c68512d1bf14dfd865c",
        "base": "76267c387538b4fb0e802278530b575bab4d1f76",
        "n": 170, "k": 21, "block_length": 85, "core_threshold": 65,
        "factor_pairs": 45, "multipliers_per_pair": 1 << 21,
        "domain_size": 45 * (1 << 21),
    }.items():
        require(type(result.get(key)) is type(value) and result[key] == value,
                "header: " + key)
    families = result["families"]
    require(isinstance(families, list) and len(families) == 45, "family count")
    actual_pairs = [tuple(f["factors"]) for f in families]
    require(len(set(actual_pairs)) == 45 and set(actual_pairs) == domain_pairs(),
            "all factor-pair coverage")
    structural_checks()
    restricted_count = full_count = represented_count = maximum_weight = 0
    orbit_count = 0
    for family, pair in zip(families, actual_pairs):
        h = product(*pair)
        require(family["check16"] == h, "degree-16 divisor")
        generator, remainder = divide(M, product(P, h))
        require(remainder == 0 and generator.bit_length() == 65, "core generator")
        representatives = []
        for entry in family["restricted_rejections"]:
            require(isinstance(entry, list) and len(entry) == 3, "restricted entry")
            multiplier, message, weight = entry
            bounded(multiplier, 0, 1 << 16, "restricted multiplier")
            bounded(message, 1, 1 << 16, "restricted nonzero message")
            bounded(weight, 1, 65, "restricted threshold")
            require(word_weight(generator, multiplier, product(P, message)) == weight,
                    "restricted witness weight")
            representatives.append(multiplier)
            maximum_weight = max(maximum_weight, weight)
        survivors = family["restricted_survivors"]
        for multiplier in survivors:
            bounded(multiplier, 0, 1 << 16, "surviving residue")
            representatives.append(multiplier)
        require(len(representatives) == family["multiplier_orbits16"], "orbit count")
        require(len(set(representatives)) == len(representatives), "duplicate orbit")
        covered = bytearray(1 << 16)
        for multiplier in representatives:
            orbit, current = set(), multiplier
            for _ in range(85):
                orbit.add(current)
                current = divide(current << 1, h)[1]
            require(current == multiplier and min(orbit) == multiplier,
                    "noncanonical rotation orbit")
            for residue in orbit:
                require(not covered[residue], "overlapping orbits")
                covered[residue] = 1
        require(all(covered), "missing rotation orbit")
        require(not family["full_survivors"] and family["best_certificate"] is None,
                "threshold survivor: universal bound is false")
        lifts = {residue: set() for residue in survivors}
        for entry in family["full_rejections"]:
            require(isinstance(entry, list) and len(entry) == 3, "full entry")
            multiplier, message, weight = entry
            bounded(multiplier, 0, 1 << 21, "full multiplier")
            bounded(message, 1, 1 << 21, "full nonzero message")
            bounded(weight, 1, 65, "full threshold")
            lift, residue = divide(multiplier, h)
            require(residue in lifts and lift not in lifts[residue], "unexpected/duplicate lift")
            lifts[residue].add(lift)
            require(word_weight(generator, multiplier, message) == weight, "full witness weight")
            maximum_weight = max(maximum_weight, weight)
        require(all(values == set(range(32)) for values in lifts.values()), "missing full lift")
        restricted_count += len(family["restricted_rejections"])
        full_count += len(family["full_rejections"])
        orbit_count += len(representatives)
        represented_count += sum(covered) * 32
    require(represented_count == result["domain_size"], "total domain")
    return {"status": "PASS", "factor_pairs": 45,
            "represented_core_choices": represented_count, "residue_orbits": orbit_count,
            "restricted_witnesses": restricted_count, "full_witnesses": full_count,
            "maximum_witness_weight": maximum_weight, "core_bound": 64,
            "two_appended_columns_bound": 66, "evidence_level": "author-checked"}


def source_hashes(result):
    expected = {
        "research/4ca1557c95957c68512d1bf14dfd865c/core-family/search.py",
        "scripts/prepare_structured.py", "scripts/codes.py", "scripts/large_verify.py",
        "research/readiness-20261021/certificates/172_21_66.json",
    }
    require(set(result["source_sha256"]) == expected, "source path set")
    for name, digest in result["source_sha256"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                "source hash: " + name)


def certificate_spectrum(certificate, n, distance):
    require(certificate.get("format") == "binary-generator-v1" and
            type(certificate.get("q")) is int and certificate["q"] == 2,
            "control format")
    require(all(type(certificate.get(k)) is int and certificate[k] == v
                for k, v in {"n": n, "k": 21, "d": distance}.items()),
            "control parameters")
    rows = certificate.get("rows")
    require(isinstance(rows, list) and len(rows) == 21 and
            all(isinstance(row, str) and len(row) == n and not set(row) - {"0", "1"}
                for row in rows), "control matrix")
    integers = [int(row, 2) for row in rows]
    pivots = {}
    for row in integers:
        while row:
            index = row.bit_length() - 1
            if index not in pivots:
                pivots[index] = row
                break
            row ^= pivots[index]
    require(len(pivots) == 21, "control rank")
    def subsets(values):
        result = [0]
        for value in values:
            result += [word ^ value for word in result]
        return result
    histogram = [0] * (n + 1)
    for left in subsets(integers[:10]):
        for right in subsets(integers[10:]):
            histogram[(left ^ right).bit_count()] += 1
    require(histogram[0] == 1 and sum(histogram) == 1 << 21, "control enumeration")
    require(next(i for i in range(1, n + 1) if histogram[i]) == distance,
            "control exact distance")
    return histogram


def attainment(output):
    parent = json.loads((ROOT / "research/readiness-20261021/certificates/172_21_66.json").read_text())
    core = json.loads((output / "parent-core-170-21-64.json").read_text())
    require(core["rows"] == [row[:170] for row in parent["rows"]], "punctured parent rows")
    generator, remainder = divide(M, product(P, product(0x17B, 0x1A3)))
    require(remainder == 0, "parent divisor")
    for j, row in enumerate(core["rows"]):
        actual = sum(int(bit) << i for i, bit in enumerate(row))
        require(actual == core_word(generator, 0x2A5F, 1 << j), "parent model coordinates")
    core_histogram = certificate_spectrum(core, 170, 64)
    parent_histogram = certificate_spectrum(parent, 172, 66)
    require(core_histogram == json.loads((output / "parent-core-spectrum.json").read_text()),
            "saved control spectrum")
    return {"attained_core_distance": 64, "attained_two_column_distance": 66,
            "core_minimum_words": core_histogram[64],
            "extended_minimum_words": parent_histogram[66]}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: replay.py RESULT_JSON_GZ")
    started = time.perf_counter()
    path = Path(sys.argv[1])
    result = json.loads(gzip.decompress(path.read_bytes()))
    source_hashes(result)
    report = check(result)
    report.update(attainment(path.parent))
    report["artifact_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    report["seconds"] = time.perf_counter() - started
    print(json.dumps(report, sort_keys=True))
