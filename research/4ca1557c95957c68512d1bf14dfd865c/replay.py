"""Check the finite obstruction directly, without importing the search engine.

Every claimed low word is reconstructed by polynomial convolution and folding at
coordinate 85. No weight tables, Gray enumeration, or search ordering are used.
"""

import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
M = (1 << 85) | 1
P = (1 << 5) | 1
MASK = (1 << 85) - 1


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def bounded(value, lower, upper, label):
    require(type(value) is int and lower <= value < upper, label)
    return value


def product(a, b):
    result = 0
    for i in range(a.bit_length()):
        if (a >> i) & 1:
            result ^= b << i
    return result


def quotient_remainder(numerator, denominator):
    quotient = 0
    for i in range(numerator.bit_length() - denominator.bit_length(), -1, -1):
        if (numerator >> (i + denominator.bit_length() - 1)) & 1:
            numerator ^= denominator << i
            quotient |= 1 << i
    return quotient, numerator


def word_weight(generator, multiplier, message):
    left = product(generator, message)
    require(left <= MASK, "first block exceeds 85 coordinates")
    right = product(left, multiplier)
    while right > MASK:
        right = (right & MASK) ^ (right >> 85)
    return left.bit_count() + right.bit_count() + 2 * (message.bit_count() % 2)


def domain_pairs():
    factors = [f for f in range(257, 512, 2) if quotient_remainder(M, f)[1] == 0]
    require(len(factors) == 10, "factor catalogue")
    complete = P
    for factor in factors:
        for degree in range(1, 5):
            for divisor in range((1 << degree) | 1, 1 << (degree + 1), 2):
                require(quotient_remainder(factor, divisor)[1] != 0,
                        "degree-eight factor is reducible")
        complete = product(complete, factor)
    require(complete == M, "incomplete factorization")
    old = {0x17B, 0x1A3}
    return {tuple(sorted((keep, other))) for keep in old
            for other in factors if other not in old}


def check(result):
    require(result.get("schema") == "single-factor-swap-witnesses-v1", "schema")
    for key, expected in {
        "seed": "4ca1557c95957c68512d1bf14dfd865c",
        "base": "76267c387538b4fb0e802278530b575bab4d1f76",
        "target_distance": 67, "n": 172, "k": 21, "factor_pairs": 16,
        "multipliers_per_pair": 1 << 21, "domain_size": 16 * (1 << 21),
    }.items():
        require(type(result.get(key)) is type(expected) and result[key] == expected,
                "header: " + key)
    families = result.get("families")
    require(isinstance(families, list) and len(families) == 16, "family count")
    expected_pairs = domain_pairs()
    actual_pairs = [tuple(family["factors"]) for family in families]
    require(len(set(actual_pairs)) == 16 and set(actual_pairs) == expected_pairs,
            "factor-pair coverage")
    restricted_total = full_total = represented_total = 0
    maximum_witness = 0
    for family, pair in zip(families, actual_pairs):
        h = product(*pair)
        require(family["check16"] == h, "degree-16 check polynomial")
        generator, remainder = quotient_remainder(M, product(P, h))
        require(remainder == 0 and generator.bit_length() == 65, "full generator")
        rejected = family["restricted_rejections"]
        survivors = family["restricted_survivors"]
        representatives = []
        for entry in rejected:
            require(isinstance(entry, list) and len(entry) == 3, "restricted entry")
            multiplier, message, claimed = entry
            bounded(multiplier, 0, 1 << 16, "restricted multiplier")
            bounded(message, 1, 1 << 16, "restricted nonzero message")
            bounded(claimed, 1, 67, "restricted rejection threshold")
            actual = word_weight(generator, multiplier, product(P, message))
            require(actual == claimed, "restricted witness weight")
            representatives.append(multiplier)
            maximum_witness = max(maximum_witness, actual)
        for multiplier in survivors:
            bounded(multiplier, 0, 1 << 16, "surviving restricted multiplier")
            representatives.append(multiplier)
        require(len(representatives) == family["multiplier_orbits16"], "orbit count")
        require(len(set(representatives)) == len(representatives), "duplicate orbit")
        covered = bytearray(1 << 16)
        for multiplier in representatives:
            orbit = set()
            current = multiplier
            for _ in range(85):
                orbit.add(current)
                current = quotient_remainder(current << 1, h)[1]
            require(current == multiplier and min(orbit) == multiplier,
                    "noncanonical or invalid rotation orbit")
            for residue in orbit:
                require(not covered[residue], "overlapping rotation orbits")
                covered[residue] = 1
        require(all(covered), "missing rotation orbit")
        require(not family["full_survivors"], "threshold survivor: no obstruction")
        lifts = {multiplier: set() for multiplier in survivors}
        for entry in family["full_rejections"]:
            require(isinstance(entry, list) and len(entry) == 3, "full entry")
            multiplier, message, claimed = entry
            bounded(multiplier, 0, 1 << 21, "full multiplier")
            bounded(message, 1, 1 << 21, "full nonzero message")
            bounded(claimed, 1, 67, "full rejection threshold")
            lift, residue = quotient_remainder(multiplier, h)
            require(residue in lifts and lift not in lifts[residue],
                    "unexpected or duplicate lift")
            lifts[residue].add(lift)
            actual = word_weight(generator, multiplier, message)
            require(actual == claimed, "full witness weight")
            maximum_witness = max(maximum_witness, actual)
        require(all(values == set(range(32)) for values in lifts.values()),
                "missing multiplier lift")
        restricted_total += len(rejected)
        full_total += len(family["full_rejections"])
        represented_total += sum(covered) * 32
    require(represented_total == result["domain_size"], "total domain coverage")
    return {
        "status": "PASS", "factor_pairs": 16,
        "represented_parameter_choices": represented_total,
        "restricted_witnesses": restricted_total, "full_witnesses": full_total,
        "maximum_witness_weight": maximum_witness,
        "family_distance_upper_bound": 66, "evidence_level": "author-checked",
        "scope": "Fixed two-block, fixed-tail, single-degree-eight-factor swaps only",
    }


def source_hashes(result):
    expected = {
        "research/4ca1557c95957c68512d1bf14dfd865c/search.py",
        "scripts/prepare_structured.py",
        "research/readiness-20261021/certificates/172_21_66.json",
    }
    require(set(result["source_sha256"]) == expected, "source path set")
    for name, digest in result["source_sha256"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                "source hash: " + name)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: replay.py RESULT_JSON")
    started = time.perf_counter()
    path = Path(sys.argv[1])
    result = json.loads(path.read_text())
    source_hashes(result)
    report = check(result)
    report["artifact_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    report["seconds"] = time.perf_counter() - started
    print(json.dumps(report, sort_keys=True))
