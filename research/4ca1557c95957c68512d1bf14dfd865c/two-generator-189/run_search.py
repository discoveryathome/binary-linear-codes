"""Validate the fresh CPU kernel, run the fixed search, and package exact controls."""

import argparse
import csv
import gzip
import hashlib
import io
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import model

PACKAGE = Path(__file__).parent
sys.path.insert(0, str(model.ROOT / "scripts"))
import codes
import large_verify


def write_certificate(rows, n, path, provenance):
    hist = codes.spectrum(rows, n)
    distance = next(i for i in range(1, n + 1) if hist[i])
    certificate = {"format": "binary-generator-v1", "q": 2, "n": n,
                   "k": len(rows), "d": distance,
                   "rows": ["".join(str((row >> i) & 1) for i in range(n)) for row in rows],
                   "provenance": provenance}
    path.write_text(json.dumps(certificate, indent=2) + "\n")
    if large_verify.check(path)["spectrum"] != hist:
        raise ValueError("full spectrum disagreement")
    return certificate, hist


def controls(binary, output):
    output.mkdir()
    factors = (0x43, 0x49, 0x57)
    for profile in ("B", "C"):
        for i, factor in enumerate(model.FACTORS6):
            triple = (factor, model.FACTORS6[(i + 1) % 9], model.FACTORS6[(i + 2) % 9])
            scalars = (3, 5, 7, 11, 13, 17)
            text = subprocess.check_output([str(binary), "--emit", profile,
                                           *map(str, triple), *map(str, scalars)], text=True)
            actual = [[int(x, 16) for x in line.split()] for line in text.splitlines()]
            expected = [model.chunks(row) for row in model.construct(profile, triple, scalars)]
            if actual != expected:
                raise ValueError("C++/Python coordinate disagreement")
    parent = json.loads((model.ROOT / "research/readiness-20261021/certificates/189_22_72.json").read_text())
    parent_rows = [sum(int(bit) << i for i, bit in enumerate(row)) for row in parent["rows"]]
    cases = [("published-parent", parent_rows)]
    for profile in ("B", "C"):
        cases.append((f"low-{profile}", model.low_rows(profile)))
        rows = model.construct(profile, factors, (3, 5, 7, 11, 13, 17))
        cases.append((f"one-field-{profile}", rows[:10]))
        cases.append((f"full-{profile}", rows))
    results = []
    for name, rows in cases:
        path = output / f"{name}.json"
        certificate, hist = write_certificate(rows, 189, path,
                                               {"kind": "CPU-enumerator-control", "name": name})
        control = output / f"{name}.rows"
        control.write_text(str(len(rows)) + "\n" + "\n".join(
            " ".join(f"{v:x}" for v in model.chunks(row)) for row in rows) + "\n")
        started = time.perf_counter()
        cpp = json.loads(subprocess.check_output([str(binary), "--check", str(control)], text=True))
        if cpp["d"] != certificate["d"] or cpp["minimum_words"] != hist[certificate["d"]]:
            raise ValueError("C++/two-Python-spectrum disagreement")
        word = 0
        for j, row in enumerate(rows):
            if (cpp["message"] >> j) & 1:
                word ^= row
        if word.bit_count() != cpp["d"]:
            raise ValueError("control message disagreement")
        results.append({"name": name, "k": len(rows), "d": cpp["d"],
                        "minimum_words": cpp["minimum_words"],
                        "cpp_seconds": time.perf_counter() - started,
                        "matrix_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({"controls": "PASS", "coordinate_models": 18,
                      "full_spectrum_controls": len(cases)}), flush=True)


def run(binary, output, controls_only=False):
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    controls(binary, output / "controls")
    if controls_only:
        return
    seed_payload = json.dumps([model.SEED, "two-generator-189-round3"], separators=(",", ":"))
    seed64 = int(hashlib.sha256(seed_payload.encode()).hexdigest()[:16], 16)
    subprocess.run([str(binary), "--search", str(output), str(seed64)], check=True)
    summary = json.loads((output / "summary.json").read_text())
    if summary["seed64"] != seed64 or summary["proposals"] > 199296:
        raise ValueError("seed or proposal-cap disagreement")
    certificates = []
    for profile in ("B", "C"):
        candidates = [t for t in summary["templates"] if t["profile"] == profile and t["d"] > 0]
        if not candidates:
            continue
        best = max(candidates, key=lambda t: (t["d"], -t["minimum_words"]))
        certificate = model.certificate(profile, best["factors"], best["scalars"], best["d"])
        name = f"best-{profile}.json"
        path = output / name
        path.write_text(json.dumps(certificate, indent=2) + "\n")
        hist = codes.spectrum(model.construct(profile, best["factors"], best["scalars"]), 189)
        if large_verify.check(path)["spectrum"] != hist or hist[best["d"]] != best["minimum_words"]:
            raise ValueError("best-certificate spectrum disagreement")
        if next(i for i in range(1, 190) if hist[i]) != best["d"]:
            raise ValueError("best distance disagreement")
        (output / f"best-{profile}-spectrum.json").write_text(json.dumps(hist) + "\n")
        certificates.append({"profile": profile, "object": name, "d": best["d"],
                             "minimum_words": best["minimum_words"],
                             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    ledger = (output / "ledger.csv").read_bytes()
    records = list(csv.DictReader(io.StringIO(ledger.decode())))
    if len(records) != summary["proposals"]:
        raise ValueError("ledger count")
    compressed = gzip.compress(ledger, mtime=0)
    if gzip.decompress(compressed) != ledger:
        raise ValueError("ledger compression")
    (output / "ledger.csv.gz").write_bytes(compressed)
    (output / "ledger.csv").unlink()
    sources = [Path(__file__), PACKAGE / "model.py", PACKAGE / "search.cpp", PACKAGE / "price.py",
               model.ROOT / "scripts/codes.py", model.ROOT / "scripts/large_verify.py",
               model.ROOT / "research/readiness-20261021/certificates/189_22_72.json"]
    metadata = {"schema": "two-generator-search-v1", "seed": model.SEED,
                "seed_payload": seed_payload, "seed64": seed64, "base": model.BASE,
                "proposal_cap": 199296, "proposals": summary["proposals"],
                "duplicates": summary["duplicates"], "target": 73,
                "target_found": summary["target_found"], "certificates": certificates,
                "ledger_sha256": hashlib.sha256(ledger).hexdigest(),
                "compressed_ledger_sha256": hashlib.sha256(compressed).hexdigest(),
                "kernel_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                "compiler_flags": "-O3 -std=c++17 -march=native",
                "compiler": subprocess.check_output(["c++", "--version"], text=True).splitlines()[0],
                "source_sha256": {str(p.relative_to(model.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sources},
                "python": platform.python_version(), "seconds": time.perf_counter() - started,
                "evidence_level": "author-checked",
                "claim": "Bounded tested list only; early rejections are upper bounds, and lower multiplicity is not a distance record."}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"status": "packaged", "proposals": metadata["proposals"],
                      "target_found": metadata["target_found"], "certificates": certificates,
                      "seconds": metadata["seconds"]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    run(args.binary.resolve(), args.output, args.controls_only)
