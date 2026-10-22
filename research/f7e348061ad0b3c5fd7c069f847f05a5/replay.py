"""Offline audit of PR #7; no imports from either construction or code verifier."""
import hashlib
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
HASHES = {
    "55_16_19.json": "b632e81e1909f2d912a4f148e5930c32551720d4fc46de4892a2f81b1062fd5c",
    "56_16_20.json": "f9195c606f420cc69944da74efb0bac0768057f9dfb2ef11eb8360ccda8b8d3c",
    "49_11_19.json": "495f1b3d284525ddb3677ec9204315c0215e28b0a90651c05c1caf2dcfcb2c10",
    "46_11_17.json": "49824435e965ddf27ec16ff75e68c608c308f7ba9b557d1f36526b861e7f52d4",
}
SHORTEN = [5, 33, 35, 39, 40, 41]
PUNCTURE = [12, 21, 45]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def multiply(a, b):
    # Carryless convolution, then polynomial long reduction modulo x^6+x+1.
    product = 0
    for i in range(6):
        for j in range(6):
            product ^= (((a >> i) & 1) * ((b >> j) & 1)) << (i + j)
    for degree in range(10, 5, -1):
        if product & (1 << degree):
            product ^= 0x43 << (degree - 6)
    return product


MUL = [[multiply(a, b) for b in range(64)] for a in range(64)]
INV = [0] + [MUL[a].index(1) for a in range(1, 64)]


def trim(p):
    p = p[:]
    while p and p[-1] == 0:
        p.pop()
    return p


def add(p, q):
    result = [0] * max(len(p), len(q))
    for polynomial in (p, q):
        for i, coefficient in enumerate(polynomial):
            result[i] ^= coefficient
    return trim(result)


def product(p, q):
    if not p or not q:
        return []
    result = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            result[i + j] ^= MUL[a][b]
    return trim(result)


def divide(p, q):
    require(bool(q), "polynomial division by zero")
    remainder = trim(p)
    quotient = [0] * max(0, len(p) - len(q) + 1)
    while remainder and len(remainder) >= len(q):
        shift = len(remainder) - len(q)
        coefficient = MUL[remainder[-1]][INV[q[-1]]]
        quotient[shift] = coefficient
        remainder = add(remainder, [0] * shift + [MUL[coefficient][b] for b in q])
    return trim(quotient), remainder


G = [1] + [0] * 8 + [1]


def inverse_linear(a):
    """Extended Euclid computes 1/(x+a) in GF(64)[x]/(x^9+1)."""
    r0, r1 = G, [a, 1]
    t0, t1 = [], [1]
    while r1:
        quotient, remainder = divide(r0, r1)
        r0, r1 = r1, remainder
        t0, t1 = t1, add(t0, product(quotient, t1))
    require(len(r0) == 1, "support contains a root of the Goppa polynomial")
    return divide([MUL[INV[r0[0]]][b] for b in t0], G)[1]


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            column = row.bit_length()
            if column not in pivots:
                pivots[column] = row
                break
            row ^= pivots[column]
    return len(pivots)


def span(rows):
    words = {0}
    for row in rows:
        words |= {word ^ row for word in words}
    return words


def spectrum(words, n):
    counts = Counter(word.bit_count() for word in words)
    return [counts[w] for w in range(n + 1)]


def mask(n, coordinates):
    # Unlike codes.py, integer bit n-1 is the leftmost JSON coordinate 0.
    return sum(1 << (n - 1 - j) for j in coordinates)


def project(word, n, removed):
    bits = format(word, f"0{n}b")
    return int("".join(b for j, b in enumerate(bits) if j not in removed), 2)


def goppa_members(rows, checks):
    return all((row & check).bit_count() % 2 == 0 for row in rows for check in checks)


def audit():
    certificates, spaces, summaries = {}, {}, {}
    for name, digest in HASHES.items():
        raw = (HERE / "inputs" / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, "input hash: " + name)
        c = json.loads(raw)
        require(c["format"] == "binary-generator-v1" and c["q"] == 2, "format")
        require(len(c["rows"]) == c["k"], "row count")
        require(all(len(row) == c["n"] and set(row) <= {"0", "1"} for row in c["rows"]), "rows")
        words = span([int(row, 2) for row in c["rows"]])
        require(len(words) == 2 ** c["k"], "rank: " + name)
        distance = min(word.bit_count() for word in words if word)
        require(distance == c["d"], "distance: " + name)
        certificates[name], spaces[name] = c, words
        summaries[name] = dict(sha256=digest, n=c["n"], k=c["k"], d=distance,
                               codewords=len(words), spectrum=spectrum(words, c["n"]))

    # These equations use the rational definition of a Goppa code, not a^j/g(a).
    require(all(len(set(MUL[a])) == 64 for a in range(1, 64)), "field multiplication")
    support = [a for a in range(64) if divide(G, [a, 1])[1]]
    require(len(support) == 55, "support size")
    inverses = [inverse_linear(a) for a in support]
    require(all(divide(product([a, 1], inverse), G)[1] == [1]
                for a, inverse in zip(support, inverses)), "polynomial inverse identity")
    checks = [sum((((inverse[degree] if degree < len(inverse) else 0) >> bit) & 1)
                  << (54 - j) for j, inverse in enumerate(inverses))
              for degree in range(9) for bit in range(6)]
    require(binary_rank(checks) == 39, "Goppa check rank")
    parent = certificates["55_16_19.json"]
    rows = [int(row, 2) for row in parent["rows"]]
    require(goppa_members(rows, checks), "Goppa defining equations")

    parent_words = spaces["55_16_19.json"]
    require({(word << 1) | (word.bit_count() % 2) for word in parent_words}
            == spaces["56_16_20.json"], "parity extension code space")
    short_mask = mask(55, SHORTEN)
    require(all((row & short_mask).bit_count() % 2 == 0 for row in rows), "first dual support")
    restriction = {word & short_mask for word in parent_words}
    require(len(restriction) == 32, "shortening imposes exactly five constraints")
    shortened = {project(word, 55, SHORTEN) for word in parent_words if not word & short_mask}
    require(shortened == spaces["49_11_19.json"], "shortening code space")
    puncture_mask = mask(49, PUNCTURE)
    losses = Counter((word & puncture_mask).bit_count() for word in shortened)
    require(set(losses) == {0, 2}, "second dual support: loss is zero or two")
    require({project(word, 49, PUNCTURE) for word in shortened}
            == spaces["46_11_17.json"], "puncturing code space")

    for name, parent_name in [("56_16_20.json", "55_16_19.json"),
                              ("49_11_19.json", "55_16_19.json"),
                              ("46_11_17.json", "49_11_19.json")]:
        provenance = certificates[name]["provenance"]
        require(provenance["parent_sha256"] == HASHES[parent_name], "parent hash")
        require(provenance["parent"] == "research/a648bcee646a1e8d8d7d43a528e3b526/" + parent_name,
                "parent path")
    require(certificates["49_11_19.json"]["provenance"]["shortened_coordinates_zero_based"] == SHORTEN,
            "shortening metadata")
    require(certificates["46_11_17.json"]["provenance"]["punctured_coordinates_zero_based"] == PUNCTURE,
            "puncturing metadata")

    # A spectrum alone cannot certify the asserted support order or transformation.
    reversed_rows = [int(row[::-1], 2) for row in parent["rows"]]
    require(spectrum(span(reversed_rows), 55) == summaries["55_16_19.json"]["spectrum"],
            "coordinate reversal preserves the complete spectrum")
    require(not goppa_members(reversed_rows, checks), "reject reversed support order")
    wrong_mask = mask(55, [j + 1 for j in SHORTEN])
    require(any((row & wrong_mask).bit_count() % 2 for row in rows), "reject off-by-one B2 support")
    changed_basis = [rows[0] ^ rows[1]] + rows[1:]
    require(span(changed_basis) == parent_words and goppa_members(changed_basis, checks),
            "accept equivalent generator basis")
    require(len(span([rows[0]] + rows[:-1])) < 2 ** 16, "detect dependent generator")

    return dict(
        predecessor="d05ac05d8c5ba2215bffaf3cdc2f920b238e9140",
        certificates=summaries,
        goppa=dict(field_modulus="x^6+x+1", polynomial="x^9+1", support=support,
                   binary_check_rank=39, kernel_dimension=16, inverse_identities=55),
        b2=dict(shortened_coordinates=SHORTEN, restriction_image_size=len(restriction),
                zero_fiber_size=len(shortened), punctured_coordinates=PUNCTURE,
                puncture_weight_loss={str(k): v for k, v in sorted(losses.items())}),
        controls=dict(reversed_support_rejected=True, reversed_spectrum_preserved=True,
                      off_by_one_dual_support_rejected=True, equivalent_basis_accepted=True,
                      dependent_generator_detected=True),
    )


if __name__ == "__main__":
    result = audit()
    require(result == json.loads((HERE / "results.json").read_text()), "saved audit result mismatch")
    print("PASS: four complete spectra, Goppa defining equations, exact descendant spaces, five controls")
