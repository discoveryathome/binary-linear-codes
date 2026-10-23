"""Exact small constituent controls and favorable bounds before full search."""

import collections
import itertools
import json
import sys
from pathlib import Path

import model

sys.path.insert(0, str(model.ROOT / "scripts"))
import codes
import large_verify


def gf4(a, b):
    return model.div(model.mul(a, b), 7)[1]


def projective_vectors(q):
    values = set()
    for vector in itertools.product(range(q), repeat=3):
        first = next((a for a in vector if a), None)
        if first is None:
            continue
        inverse = next(i for i in range(1, q) if (gf4(first, i) if q == 4 else first * i) == 1)
        values.add(tuple(gf4(a, inverse) if q == 4 else a * inverse for a in vector))
    return sorted(values)


def plane_basis(normal, q):
    pivot = next(i for i, a in enumerate(normal) if a)
    inverse = next(i for i in range(1, q) if (gf4(normal[pivot], i) if q == 4 else normal[pivot] * i) == 1)
    rows = []
    for other in range(3):
        if other == pivot:
            continue
        row = [0, 0, 0]
        row[other] = 1
        row[pivot] = gf4(normal[other], inverse) if q == 4 else normal[other] * inverse
        rows.append(row)
    return rows


def minimum(rows, n):
    hist = codes.spectrum(rows, n)
    distance = next(i for i in range(1, n + 1) if hist[i])
    return distance, hist[distance], hist


def write_control(rows, n, distance, path, provenance):
    certificate = {"format": "binary-generator-v1", "q": 2, "n": n, "k": len(rows),
                   "d": distance,
                   "rows": ["".join(str((row >> i) & 1) for i in range(n)) for row in rows],
                   "provenance": provenance}
    path.write_text(json.dumps(certificate, indent=2) + "\n")
    hist = codes.spectrum(rows, n)
    if large_verify.check(path)["spectrum"] != hist:
        raise ValueError("small-control spectrum disagreement")


def run(output):
    output.mkdir(parents=True, exist_ok=False)
    complete = model.mul(model.mul(model.mul(3, 7), 0xB), 0xD)
    for factor in model.FACTORS6:
        complete = model.mul(complete, factor)
    assert complete == model.M and len(model.TRIPLES) == 84
    patterns = [(a, b, c, d) for a in range(3) for b in range(3)
                for c in range(2) for d in range(10) if a + 2*b + 3*c + 6*d == 22]
    assert patterns == [(0, 2, 0, 3), (1, 0, 1, 3), (2, 1, 0, 3)]
    low_b, low_c = [], []
    vectors4 = projective_vectors(4)
    vectors2 = projective_vectors(2)
    assert len(vectors4) == 21 and len(vectors2) == 7
    for normal in vectors4:
        rows = []
        for vector in plane_basis(normal, 4):
            for scalar in (1, 2):
                blocks = [model.mul(3, gf4(a, scalar)) for a in vector]
                rows.append(model.block_word(*blocks, length=3))
        distance, count, hist = minimum(rows, 9)
        assert distance == (4 if all(normal) else 2)
        low_b.append({"normal": normal, "d": distance, "minimum_words": count,
                      "rows": rows, "spectrum": hist})
    for normal in vectors2:
        for line in vectors4:
            rows = [model.block_word(*(7*a for a in vector), length=3)
                    for vector in plane_basis(normal, 2)]
            rows += [model.block_word(*(model.mul(3, gf4(a, scalar)) for a in line), length=3)
                     for scalar in (1, 2)]
            distance, count, hist = minimum(rows, 9)
            if all(normal):
                assert distance == (4 if all(line) else 2)
            else:
                assert distance <= 3
            low_c.append({"normal": normal, "line": line, "d": distance,
                          "minimum_words": count, "rows": rows, "spectrum": hist})
    for profile in ("B", "C"):
        rows = model.low_rows(profile)
        distance, count, _ = minimum(rows, 189)
        assert distance == 84 and count == 9
        write_control(rows, 189, 84, output / f"low-{profile}.json",
                      {"kind": "canonical-low-constituent-control", "profile": profile})
    pair_cases, best = [], (0, None)
    for f in range(64):
        for g in range(64):
            rows = [model.block_word(3 << j, model.div(model.mul(3 << j, f), 129)[1],
                                     model.div(model.mul(3 << j, g), 129)[1], length=7)
                    for j in range(6)]
            distance, count, hist = minimum(rows, 21)
            assert distance <= 8 and all(hist[i] == 0 for i in range(1, 22, 2))
            pair_cases.append([f, g, distance, count])
            if distance > best[0]:
                best = distance, (f, g, rows)
    assert best[0] == 8
    f, g, rows = best[1]
    write_control(rows, 21, 8, output / "two-degree3-control.json",
                  {"kind": "two-degree-three-constituent-control", "f": f, "g": g,
                   "note": "Repeated nine times in length 189; upper bound 72 follows from evenness and Griesmer."})
    field_prices = []
    for factor in model.FACTORS6:
        generator, remainder = model.div(model.M, factor)
        assert remainder == 0
        weight = [model.mul(generator, a).bit_count() for a in range(64)]
        table = [[model.div(model.mul(a, b), factor)[1] for b in range(64)] for a in range(64)]
        distances = [min(weight[a] + weight[table[a][f]] + weight[table[a][g]]
                         for a in range(1, 64)) for f in range(1, 64) for g in range(1, 64)]
        best_distance = max(distances)
        order = next(i for i in range(1, 64) if model.div((1 << i) | 1, factor)[1] == 0)
        field_prices.append({"factor": factor, "order": order, "maximum_line_d": best_distance,
                             "distance_histogram": dict(sorted(collections.Counter(distances).items())),
                             "unit_pair_distances": distances})
        print(json.dumps({"factor": hex(factor), "order": order,
                          "favorable_line_d": best_distance,
                          "unit_pairs_meeting_73": sum(d >= 73 for d in distances)}), flush=True)
    result = {"schema": "three-block-constituent-pricing-v1", "seed": model.SEED,
              "base": model.BASE, "dimension_patterns": patterns,
              "low_B": low_b, "low_C": low_c, "two_degree3_cases": pair_cases,
              "degree6": field_prices, "evidence_level": "author-checked",
              "claim": "Exact small-model pricing and necessary-profile checks; not a full construction search or unrestricted bound."}
    (output / "pricing.json").write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(json.dumps({"status": "PASS", "planes_B": len(low_b), "planes_and_lines_C": len(low_c),
                      "two_degree3_cases": len(pair_cases), "favorable_low_d": 84}), flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: price.py NEW_OUTPUT_DIRECTORY")
    run(Path(sys.argv[1]))
