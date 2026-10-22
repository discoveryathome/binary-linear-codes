"""Reconstruct the published 55-point binary Goppa code and its parity extension."""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import codes

HERE = Path(__file__).resolve().parent
SOURCE = "https://www.codetables.de/BKLC/BKLC.php?q=2&n=51&k=12"
SOURCE_SHA256 = "7ef83bce045ba4dd48413e8d395ceb72eda570b4a0b3c00f12358b296be32b80"
B2_SUPPORT = [5, 33, 35, 39, 40, 41]  # Zero-based coordinates of a dual word of weight 6.
B2_PUNCTURE = [12, 21, 45]  # Zero-based coordinates after the first B2 step.


def multiply(a, b):
    product = 0
    while b:
        if b & 1:
            product ^= a
        b >>= 1
        a <<= 1
        if a & 64:
            a ^= 0x43  # x^6 + x + 1
    return product


def power(a, exponent):
    result = 1
    while exponent:
        if exponent & 1:
            result = multiply(result, a)
        a = multiply(a, a)
        exponent >>= 1
    return result


def nullspace(checks, n):
    rows = checks[:]
    pivots = []
    for column in range(n):
        pivot = next((i for i in range(len(pivots), len(rows)) if rows[i] >> column & 1), None)
        if pivot is None:
            continue
        rank = len(pivots)
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i] >> column & 1:
                rows[i] ^= rows[rank]
        pivots.append(column)
    free = [j for j in range(n) if j not in pivots]
    return [1 << j | sum(((rows[i] >> j) & 1) << p for i, p in enumerate(pivots)) for j in free]


def main():
    assert len({power(2, i) for i in range(63)}) == 63
    support = [a for a in range(64) if power(a, 9) ^ 1]
    assert len(support) == 55
    checks = [0] * 54
    for column, a in enumerate(support):
        inverse = power(power(a, 9) ^ 1, 62)
        assert multiply(inverse, power(a, 9) ^ 1) == 1
        for j in range(9):
            entry = multiply(power(a, j), inverse)
            for bit in range(6):
                checks[6 * j + bit] |= ((entry >> bit) & 1) << column
    rows = nullspace(checks, len(support))
    assert len(rows) == 16 and all(not (r & h).bit_count() % 2 for r in rows for h in checks)
    assert codes.distance(rows, 55) == 19
    parent = HERE / "55_16_19.json"
    codes.write_cert(parent, rows, 55, {
        "kind": "published-reconstruction",
        "url": SOURCE,
        "source_sha256": SOURCE_SHA256,
        "credit": "M. Loeloeian and J. Conan, A [55,16,19] binary Goppa code (1984)",
        "recipe": "GF(64), x^9 + 1, all 55 nonroots; alternant parity check a^j/g(a), j=0..8",
        "field_modulus": "x^6 + x + 1",
        "support_order": "integer coefficients 0..63, excluding roots",
    })
    extended, n = codes.extend(rows, 55)
    assert codes.distance(extended, n) == 20
    codes.write_cert(HERE / "56_16_20.json", extended, n, {
        "kind": "derived-construction",
        "parent": str(parent.relative_to(ROOT)),
        "parent_sha256": hashlib.sha256(parent.read_bytes()).hexdigest(),
        "transformation": "overall parity extension at coordinate 56",
        "credit": "M. Loeloeian and J. Conan, parent construction (1984)",
    })
    dual_word = sum(1 << j for j in B2_SUPPORT)
    assert dual_word.bit_count() == 6 and all(not (dual_word & r).bit_count() % 2 for r in rows)
    shortened, n = codes.shorten(rows, 55, B2_SUPPORT)
    assert (n, len(shortened), codes.distance(shortened, n)) == (49, 11, 19)
    first_b2 = HERE / "49_11_19.json"
    codes.write_cert(first_b2, shortened, n, {
        "kind": "published-reconstruction",
        "url": "https://www.codetables.de/BKLC/BKLC.php?q=2&n=49&k=11",
        "source_sha256": "ce877d800ae9c006c3ff01470b816fb99e7350283ad333faebb2a405f35fbd5c",
        "parent": str(parent.relative_to(ROOT)),
        "parent_sha256": hashlib.sha256(parent.read_bytes()).hexdigest(),
        "transformation": "Construction B2 (j=0): shorten on the dual-weight-6 support",
        "shortened_coordinates_zero_based": B2_SUPPORT,
        "credit": "M. Loeloeian and J. Conan, Goppa parent; Brouwer and Verhoeff, B2 table construction",
    })
    dual_word = sum(1 << j for j in B2_PUNCTURE)
    assert dual_word.bit_count() == 3 and all(not (dual_word & r).bit_count() % 2 for r in shortened)
    punctured, n = codes.puncture(shortened, n, B2_PUNCTURE)
    assert (n, len(punctured), codes.distance(punctured, n)) == (46, 11, 17)
    codes.write_cert(HERE / "46_11_17.json", punctured, n, {
        "kind": "published-reconstruction",
        "url": "https://www.codetables.de/BKLC/BKLC.php?q=2&n=46&k=11",
        "source_sha256": "572608ebdf2d084e1ba2575d0fdfa8c4450f533be6ccec36f7cb5620638e9312",
        "parent": str(first_b2.relative_to(ROOT)),
        "parent_sha256": hashlib.sha256(first_b2.read_bytes()).hexdigest(),
        "transformation": "Construction B2 (j=1): puncture a dual-weight-3 support; even parity limits the loss to 2",
        "punctured_coordinates_zero_based": B2_PUNCTURE,
        "credit": "M. Loeloeian and J. Conan, Goppa parent; B. Groneick and S. Grosse, table construction",
    })
    print("PASS [55,16,19], [56,16,20], [49,11,19] and [46,11,17]")


if __name__ == "__main__":
    main()
