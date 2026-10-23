"""Exhaust the fixed one/two field-scalar neighborhood of the published parent."""

import argparse
import gzip
import hashlib
import json
import subprocess
import time
from pathlib import Path

import model
import pivot_model
from run_search import write_certificate, codes

PACKAGE = Path(__file__).parent


def run(binary, output):
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    p = pivot_model.parameters()
    rows = pivot_model.construct(p["degree_three"], p["factors"], p["scalars"])
    parent_rows = [sum(int(bit) << j for j, bit in enumerate(row)) for row in p["parent"]["rows"]]
    def rotate(word, shift):
        return ((word << shift) & model.MASK) | (word >> (63-shift)) if shift else word
    rotated = [model.block_word(*(rotate((row >> (63*j)) & model.MASK,
                                        p["block_rotations"][j]) for j in range(3)))
               for row in parent_rows]
    if len(codes.basis(rows)) != 22 or len(codes.basis(rows + rotated)) != 22:
        raise ValueError("normalization row-space equality")
    arguments = [str(p["degree_three"]), *map(str, p["factors"])]
    for scalars in (p["scalars"], [3,5,7,11,13,17]):
        raw = subprocess.check_output([str(binary), "--emit", *arguments,
                                       str(pivot_model.packed(scalars))], text=True)
        actual = [[int(v, 16) for v in line.split()] for line in raw.splitlines()]
        expected = [model.chunks(row) for row in pivot_model.construct(
            p["degree_three"], p["factors"], scalars)]
        if actual != expected:
            raise ValueError("pivot C++/Python coordinate mismatch")
    certificate, hist = write_certificate(rows, 189, output / "normalized-parent.json",
        {"kind": "coordinate-rotated-published-parent", "source": "research/readiness-20261021/certificates/189_22_72.json",
         "block_rotations": p["block_rotations"], "degree_three": p["degree_three"],
         "degree_six_factors": p["factors"], "scalars": p["scalars"], "seed": model.SEED,
         "credit": "Seddas, Shashkov, Viazovska, Abbe; a normalized replication, not a new code"})
    if certificate["d"] != 72 or hist[72] != 2394:
        raise ValueError("published parent control")
    (output / "normalized-parent-spectrum.json").write_text(json.dumps(hist) + "\n")
    subprocess.run([str(binary), str(output), *arguments, str(pivot_model.packed(p["scalars"]))], check=True)
    summary = json.loads((output / "summary.json").read_text())
    if summary["domain_size"] != 58033 or summary["evaluated"] > 58033:
        raise ValueError("neighborhood cardinality")
    candidate = None
    if summary["target_found"]:
        packed = summary["candidate_genome"]
        scalars = [(packed >> (6*j)) & 63 for j in range(6)]
        candidate_rows = pivot_model.construct(p["degree_three"], p["factors"], scalars)
        candidate, spectrum = write_certificate(candidate_rows, 189, output / "candidate.json",
            {"kind": "field-scalar-neighborhood-candidate", "seed": model.SEED,
             "degree_three": p["degree_three"], "degree_six_factors": p["factors"],
             "scalars": scalars, "parent_scalars": p["scalars"],
             "claim": "Author-checked candidate; fresh literature, closure, equivalence and expert review required."})
        if candidate["d"] < 73 or candidate["d"] != summary["maximum_witness"]:
            raise ValueError("candidate exact distance")
        (output / "candidate-spectrum.json").write_text(json.dumps(spectrum) + "\n")
    raw = (output / "ledger.csv").read_bytes()
    compressed = gzip.compress(raw, mtime=0)
    if gzip.decompress(compressed) != raw:
        raise ValueError("pivot compression")
    (output / "ledger.csv.gz").write_bytes(compressed)
    (output / "ledger.csv").unlink()
    sources = [Path(__file__), PACKAGE / "pivot_model.py", PACKAGE / "pivot-search.cpp",
               PACKAGE / "model.py", PACKAGE / "run_search.py", model.ROOT / "scripts/codes.py",
               model.ROOT / "scripts/large_verify.py",
               model.ROOT / "research/readiness-20261021/certificates/189_22_72.json"]
    metadata = {"schema": "field-neighborhood-v1", "seed": model.SEED, "base": model.BASE,
                "degree_three": p["degree_three"], "factors": p["factors"], "parent_scalars": p["scalars"],
                "block_rotations": p["block_rotations"], "domain_size": 58033,
                "evaluated": summary["evaluated"], "target_found": summary["target_found"],
                "ledger_sha256": hashlib.sha256(raw).hexdigest(),
                "compressed_ledger_sha256": hashlib.sha256(compressed).hexdigest(),
                "source_sha256": {str(s.relative_to(model.ROOT)): hashlib.sha256(s.read_bytes()).hexdigest()
                                  for s in sources},
                "seconds": time.perf_counter() - started, "evidence_level": "author-checked",
                "claim": "Complete zero/one/two field-scalar replacement neighborhood only; not unrestricted optimality."}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"status": "packaged", "evaluated": metadata["evaluated"],
                      "target_found": metadata["target_found"],
                      "maximum_witness": summary["maximum_witness"], "seconds": metadata["seconds"]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    run(args.binary.resolve(), args.output)
