"""Rank-16 pair models, specialized from this session's PR #12."""

import itertools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "76267c387538b4fb0e802278530b575bab4d1f76"
SEED = "4ca1557c95957c68512d1bf14dfd865c"
M = (1 << 63) | 1
FACTORS = (0x43, 0x49, 0x57, 0x5B, 0x61, 0x67, 0x6D, 0x73, 0x75)
PAIRS = tuple(itertools.combinations(FACTORS, 2))


def multiply(a, b):
    value = 0
    while b:
        if b & 1:
            value ^= a
        a <<= 1
        b >>= 1
    return value


def divide(a, b):
    quotient = 0
    while a.bit_length() >= b.bit_length():
        shift = a.bit_length() - b.bit_length()
        quotient ^= 1 << shift
        a ^= b << shift
    return quotient, a


def representatives(p, q):
    unseen = {a | (b << 6) for a in range(1, 64) for b in range(1, 64)}
    result = []
    while unseen:
        start = min(unseen)
        value = start
        while value in unseen:
            unseen.remove(value)
            a, b = value & 63, value >> 6
            value = divide(a << 3, p)[1] | (divide(b << 3, q)[1] << 6)
        if value != start:
            raise ValueError("orbit did not close")
        result.append(start)
    return result


def construct(profile, pair, f, g):
    if profile not in ("B", "C") or pair not in PAIRS:
        raise ValueError("profile/factor pair")
    if any(type(v) is not int or not 1 <= v < 64 for v in (f & 63, f >> 6, g & 63, g >> 6)):
        raise ValueError("four nonzero scalars")
    def word(a, b, c):
        if min(a, b, c) < 0 or max(a, b, c).bit_length() > 63:
            raise ValueError("block size")
        return a | (b << 63) | (c << 126)
    g1, g2 = divide(M, 3)[0], divide(M, 7)[0]
    if profile == "B":
        rows = [word(g2 << j, 0, g2 << j) for j in range(2)]
        rows += [word(0, g2 << j, g2 << j) for j in range(2)]
    else:
        rows = [word(g1, 0, g1), word(0, g1, g1)]
        rows += [word(g2 << j, g2 << j, g2 << j) for j in range(2)]
    for i, factor in enumerate(pair):
        generator, remainder = divide(M, factor)
        if remainder:
            raise ValueError("factor divisor")
        for j in range(6):
            a = generator << j
            rows.append(word(a, divide(multiply(a, (f >> (6*i)) & 63), M)[1],
                             divide(multiply(a, (g >> (6*i)) & 63), M)[1]))
    return rows


def certificate(profile, pair, f, g, distance):
    return {"format": "binary-generator-v1", "q": 2, "n": 189, "k": 16,
            "d": distance,
            "rows": ["".join(str((row >> i) & 1) for i in range(189))
                     for row in construct(profile, pair, f, g)],
            "provenance": {"kind": "pair-threshold-pricing", "profile": profile,
                           "factors": list(pair), "f_pair": f, "g_pair": g,
                           "seed": SEED, "base": BASE,
                           "model_credit": "PR #12, same author session; canonical B/C low constituents",
                           "claim": "Rank-16 subcode only; not a full dimension-22 construction or record."}}
