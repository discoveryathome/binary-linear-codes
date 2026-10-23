"""Exact polynomial model for two-generator CRT profiles B and C."""

import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
M = (1 << 63) | 1
MASK = (1 << 63) - 1
SEED = "4ca1557c95957c68512d1bf14dfd865c"
BASE = "76267c387538b4fb0e802278530b575bab4d1f76"
FACTORS6 = (0x43, 0x49, 0x57, 0x5B, 0x61, 0x67, 0x6D, 0x73, 0x75)
TRIPLES = tuple(itertools.combinations(FACTORS6, 3))


def mul(a, b):
    value = 0
    while b:
        if b & 1:
            value ^= a
        a <<= 1
        b >>= 1
    return value


def div(a, b):
    quotient = 0
    while a.bit_length() >= b.bit_length():
        shift = a.bit_length() - b.bit_length()
        quotient ^= 1 << shift
        a ^= b << shift
    return quotient, a


def block_word(a, b, c, length=63):
    if min(a, b, c) < 0 or max(a, b, c).bit_length() > length:
        raise ValueError("block length")
    return a | (b << length) | (c << (2 * length))


def low_rows(profile, length=63):
    modulus = (1 << length) | 1
    g1, r1 = div(modulus, 3)
    g2, r2 = div(modulus, 7)
    if r1 or r2:
        raise ValueError("low-factor divisor")
    if profile == "B":
        return [block_word(g2 << j, 0, g2 << j, length) for j in range(2)] + [
            block_word(0, g2 << j, g2 << j, length) for j in range(2)]
    if profile == "C":
        return [block_word(g1, 0, g1, length), block_word(0, g1, g1, length)] + [
            block_word(g2 << j, g2 << j, g2 << j, length) for j in range(2)]
    raise ValueError("profile")


def construct(profile, factors, scalars):
    if len(factors) != 3 or len(set(factors)) != 3 or not set(factors) <= set(FACTORS6):
        raise ValueError("three distinct degree-six factors")
    if len(scalars) != 6 or any(type(x) is not int or not 1 <= x < 64 for x in scalars):
        raise ValueError("six nonzero field scalars")
    rows = low_rows(profile)
    for i, factor in enumerate(factors):
        generator, remainder = div(M, factor)
        if remainder:
            raise ValueError("degree-six divisor")
        f, g = scalars[2 * i:2 * i + 2]
        for j in range(6):
            left = generator << j
            rows.append(block_word(left, div(mul(left, f), M)[1],
                                   div(mul(left, g), M)[1]))
    return rows


def certificate(profile, factors, scalars, distance):
    return {
        "format": "binary-generator-v1", "q": 2, "n": 189, "k": 22,
        "d": distance,
        "rows": ["".join(str((row >> i) & 1) for i in range(189))
                 for row in construct(profile, factors, scalars)],
        "provenance": {
            "kind": "two-generator-crt-experiment", "profile": profile,
            "degree_six_factors": list(factors), "scalars": list(scalars),
            "seed": SEED, "base": BASE, "block_length": 63,
            "parent_control": "research/readiness-20261021/certificates/189_22_72.json",
            "inherited_control_credit": "Seddas, Shashkov, Viazovska, Abbe",
            "claim": "Changed CRT representation; exact certificate is author-checked, with no record or independent-review claim.",
        },
    }


def chunks(row):
    return [(row >> (64 * j)) & ((1 << 64) - 1) for j in range(3)]
