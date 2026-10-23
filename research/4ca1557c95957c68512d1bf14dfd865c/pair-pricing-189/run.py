"""Check coordinates, run fixed threshold pricing, and retain exact controls."""

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

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(model.ROOT / "scripts"))
import codes
import large_verify


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(binary, output):
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    for profile in ("B", "C"):
        for pair in model.PAIRS:
            text = subprocess.check_output([str(binary), "--emit", profile,
                                            *map(str, pair), "193", "709"], text=True)
            actual = [[int(x, 16) for x in row.split()] for row in text.splitlines()]
            expected = [[(row >> (64*j)) & ((1 << 64)-1) for j in range(3)]
                        for row in model.construct(profile, pair, 193, 709)]
            if actual != expected:
                raise ValueError("kernel/model coordinate disagreement")
    kernel = json.loads(subprocess.check_output([str(binary), "--search", str(output)], text=True))
    cases = json.loads((output / "cases.json").read_text())
    raw = (output / "ledger.csv").read_bytes()
    records = list(csv.DictReader(io.StringIO(raw.decode())))
    if kernel["cases"] != 72 or len(records) != kernel["tested"]:
        raise ValueError("kernel count")
    final = {int(record["case"]): record for record in records}
    (output / "certificates").mkdir()
    spectra = {}
    for case in cases:
        if not case["survivor"]:
            continue
        last = final[case["case"]]
        if int(last["exact"]) != 1 or int(last["d_or_upper"]) < 74:
            raise ValueError("survivor record")
        rows = model.construct(case["profile"], tuple(case["factors"]),
                               int(last["f_pair"]), int(last["g_pair"]))
        if len(codes.basis(rows)) != 16:
            raise ValueError("rank")
        hist = codes.spectrum(rows, 189)
        distance = next(i for i in range(1, 190) if hist[i])
        if distance != int(last["d_or_upper"]) or hist[distance] != int(last["minimum_words"]):
            raise ValueError("exact distance/count")
        name = f"{case['profile']}-{case['factors'][0]:x}-{case['factors'][1]:x}.json"
        path = output / "certificates" / name
        obj = model.certificate(case["profile"], tuple(case["factors"]),
                                int(last["f_pair"]), int(last["g_pair"]), distance)
        path.write_text(json.dumps(obj, indent=2) + "\n")
        if large_verify.check(path)["spectrum"] != hist:
            raise ValueError("two full spectra disagree")
        control = output / "kernel-control.rows"
        control.write_text("16\n" + "\n".join(
            " ".join(f"{(row >> (64*j)) & ((1 << 64)-1):x}" for j in range(3))
            for row in rows) + "\n")
        cpp = json.loads(subprocess.check_output([str(binary), "--check", str(control)], text=True))
        control.unlink()
        if cpp != {"d": distance, "minimum_words": hist[distance]}:
            raise ValueError("kernel full control")
        case.update({"certificate": "certificates/" + name, "d": distance,
                     "minimum_words": hist[distance], "sha256": digest(path)})
        spectra[str(case["case"])] = hist
    (output / "cases.json").write_text(json.dumps(cases, indent=2) + "\n")
    (output / "spectra.json").write_text(json.dumps(spectra, sort_keys=True) + "\n")
    compressed = gzip.compress(raw, mtime=0)
    (output / "ledger.csv.gz").write_bytes(compressed)
    (output / "ledger.csv").unlink()
    sources = [Path(__file__).resolve(), PACKAGE / "model.py", PACKAGE / "threshold.cpp",
               model.ROOT / "scripts/codes.py", model.ROOT / "scripts/large_verify.py"]
    metadata = {"schema": "pair-threshold-pricing-v1", "seed": model.SEED, "base": model.BASE,
                "threshold": 74, "cases": 72, "maximum_domain": 3143448,
                "tested": len(records), "surviving_pairs": sum(c["survivor"] for c in cases),
                "coordinate_controls": 72, "ledger_sha256": hashlib.sha256(raw).hexdigest(),
                "compressed_ledger_sha256": hashlib.sha256(compressed).hexdigest(),
                "source_sha256": {str(p.relative_to(model.ROOT)): digest(p) for p in sources},
                "kernel_sha256": digest(binary), "compiler_flags": "-O3 -std=c++17 -march=native",
                "compiler": subprocess.check_output(["c++", "--version"], text=True).splitlines()[0],
                "python": platform.python_version(), "seconds": time.perf_counter()-started,
                "evidence_level": "author-checked",
                "claim": "Threshold result for rank-16 subcodes; no full dimension-22 construction or record."}
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({k: metadata[k] for k in ("cases", "tested", "surviving_pairs", "seconds")}))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: run.py FRESH_BINARY NEW_OUTPUT")
    run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
