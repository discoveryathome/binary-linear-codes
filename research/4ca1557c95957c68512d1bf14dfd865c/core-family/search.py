"""Screen every normalized length-170, dimension-21 two-block cyclic core."""

import gzip
import hashlib
import itertools
import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import codes
import large_verify
from prepare_structured import div, mul

M = (1 << 85) | 1
P = (1 << 5) | 1
FACTORS = (0x139, 0x13F, 0x177, 0x17B, 0x18B,
           0x1A3, 0x1BD, 0x1D7, 0x1DD, 0x1F9)
PAIRS = list(itertools.combinations(FACTORS, 2))
SEED = "4ca1557c95957c68512d1bf14dfd865c"
BASE = "76267c387538b4fb0e802278530b575bab4d1f76"
THRESHOLD = 65
PARENT = ROOT / "research/readiness-20261021/certificates/172_21_66.json"


def weights(check):
    generator, remainder = div(M, check)
    assert remainder == 0
    dimension = check.bit_length() - 1
    values = bytearray(1 << dimension)
    word = 0
    for i in range(1, len(values)):
        word ^= generator << ((i & -i).bit_length() - 1)
        values[i ^ (i >> 1)] = word.bit_count()
    return values


def representatives(check, values):
    limit = len(values)
    assert limit == 1 << (check.bit_length() - 1)
    seen = bytearray(limit)
    result = []
    for message in range(limit):
        if seen[message]:
            continue
        result.append(message)
        current, length = message, 0
        while True:
            assert not seen[current] and current >= message
            assert values[current] == values[message]
            seen[current] = 1
            length += 1
            current <<= 1
            if current & limit:
                current ^= check
            if current == message:
                break
        assert 85 % length == 0
    assert all(seen)
    return result


def screen(multiplier, check, values, messages):
    best = (171, 0)
    for message in messages:
        image = div(mul(message, multiplier), check)[1]
        weight = values[message] + values[image]
        if weight < best[0]:
            best = weight, message
        if weight < THRESHOLD:
            break
    return best


def core_certificate(pair, multiplier, distance):
    generator, remainder = div(M, mul(P, mul(*pair)))
    assert remainder == 0
    rows = []
    for j in range(21):
        left = generator << j
        right = div(mul(left, multiplier), M)[1]
        row = left | (right << 85)
        rows.append("".join(str((row >> i) & 1) for i in range(170)))
    return {
        "format": "binary-generator-v1", "q": 2, "n": 170, "k": 21,
        "d": distance, "rows": rows,
        "provenance": {
            "kind": "normalized-two-block-cyclic-core", "block_length": 85,
            "degree_eight_factors": list(pair), "second_multiplier": multiplier,
            "seed": SEED, "base": BASE,
            "source": "https://arxiv.org/html/2609.37056v1",
            "construction_credit": "Seddas, Shashkov, Viazovska, Abbe; inherited two-block recipe",
        },
    }


def save_and_verify(certificate, path):
    path.write_text(json.dumps(certificate, indent=2) + "\n")
    rows = [sum(int(bit) << i for i, bit in enumerate(row))
            for row in certificate["rows"]]
    spectrum = codes.spectrum(rows, certificate["n"])
    actual = next(i for i in range(1, len(spectrum)) if spectrum[i])
    if actual != certificate["d"] or large_verify.check(path)["spectrum"] != spectrum:
        raise ValueError("exhaustive spectrum disagreement")
    return spectrum


def controls(output):
    complete = P
    for factor in FACTORS:
        complete = mul(complete, factor)
    assert complete == M and len(PAIRS) == 45
    parent = json.loads(PARENT.read_text())
    certificate = core_certificate((0x17B, 0x1A3), 0x2A5F, 64)
    assert certificate["rows"] == [row[:170] for row in parent["rows"]]
    certificate["provenance"]["parent_sha256"] = hashlib.sha256(PARENT.read_bytes()).hexdigest()
    spectrum = save_and_verify(certificate, output / "parent-core-170-21-64.json")
    (output / "parent-core-spectrum.json").write_text(json.dumps(spectrum) + "\n")


def run(output):
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    controls(output)
    families = []
    for pair in PAIRS:
        h16 = mul(*pair)
        w16 = weights(h16)
        residues = representatives(h16, w16)
        messages = sorted(residues[1:], key=lambda m: (w16[m], m))
        rejected, unresolved = [], []
        for multiplier in residues:
            distance, message = screen(multiplier, h16, w16, messages)
            if distance < THRESHOLD:
                rejected.append([multiplier, message, distance])
            else:
                unresolved.append(multiplier)
        full_rejected, survivors = [], []
        if unresolved:
            h21 = mul(P, h16)
            w21 = weights(h21)
            full_messages = sorted(representatives(h21, w21)[1:],
                                   key=lambda m: (w21[m], m))
            for residue in unresolved:
                for lift in range(32):
                    multiplier = residue ^ mul(h16, lift)
                    distance, message = screen(multiplier, h21, w21, full_messages)
                    if distance < THRESHOLD:
                        full_rejected.append([multiplier, message, distance])
                    else:
                        survivors.append([multiplier, distance, message])
        best_certificate = None
        if survivors:
            multiplier, distance, _ = max(survivors, key=lambda entry: entry[1])
            best_certificate = f"survivor-{pair[0]:x}-{pair[1]:x}.json"
            spectrum = save_and_verify(core_certificate(pair, multiplier, distance),
                                       output / best_certificate)
            (output / f"survivor-spectrum-{pair[0]:x}-{pair[1]:x}.json").write_text(
                json.dumps(spectrum) + "\n")
        families.append({
            "factors": list(pair), "check16": h16,
            "multiplier_orbits16": len(residues),
            "restricted_rejections": rejected, "restricted_survivors": unresolved,
            "full_rejections": full_rejected, "full_survivors": survivors,
            "best_certificate": best_certificate,
        })
        if len(families) % 5 == 0:
            print(json.dumps({"families_complete": len(families),
                              "surviving_cores": sum(len(f["full_survivors"]) for f in families),
                              "seconds": round(time.perf_counter() - started, 3)}), flush=True)
    sources = [Path(__file__), ROOT / "scripts/prepare_structured.py",
               ROOT / "scripts/codes.py", ROOT / "scripts/large_verify.py", PARENT]
    result = {
        "schema": "normalized-qc-core-witnesses-v1", "seed": SEED, "base": BASE,
        "n": 170, "k": 21, "block_length": 85, "core_threshold": THRESHOLD,
        "factor_pairs": 45, "multipliers_per_pair": 1 << 21,
        "domain_size": 45 * (1 << 21), "families": families,
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sources},
        "python": platform.python_version(), "seconds": time.perf_counter() - started,
        "evidence_level": "author-checked",
        "claim": "A universal core bound 64 requires no full survivor; then any two appended columns have distance at most 66.",
    }
    payload = (json.dumps(result, separators=(",", ":")) + "\n").encode()
    (output / "result.json.gz").write_bytes(gzip.compress(payload, mtime=0))
    print(json.dumps({"status": "complete", "core_parameter_choices": result["domain_size"],
                      "surviving_cores": sum(len(f["full_survivors"]) for f in families),
                      "seconds": result["seconds"]}), flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: search.py NEW_OUTPUT_DIRECTORY")
    run(Path(sys.argv[1]))
