"""Save one deterministic matrix per family and check both exhaustive spectra."""

import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import codes
import large_verify
from prepare_structured import SPECS, construct


def run(result_path, output):
    result = json.loads(result_path.read_text())
    output.mkdir(parents=True, exist_ok=False)
    controls = []
    for family in result["families"]:
        entries = family["full_rejections"] or family["restricted_rejections"]
        multiplier = max(entries, key=lambda entry: entry[2])[0]
        spec = list(copy.deepcopy(next(s for s in SPECS if s[0] == 172)))
        spec[4] = spec[4][:2] + [[i for i in range(9) if (factor >> i) & 1]
                               for factor in family["factors"]]
        spec[5][1] = [i for i in range(21) if (multiplier >> i) & 1]
        rows = construct(spec)
        spectrum = codes.spectrum(rows, 172)
        distance = next(i for i in range(1, 173) if spectrum[i])
        spec[2] = distance
        certificate = {
            "format": "binary-generator-v1", "q": 2, "n": 172, "k": 21,
            "d": distance,
            "rows": ["".join(str((row >> i) & 1) for i in range(172)) for row in rows],
            "provenance": {
                "kind": "single-factor-swap-matrix-control",
                "seed": result["seed"], "base": result["base"],
                "construction": spec,
                "selection": "First rejection with largest saved witness weight; not a claimed best code",
                "parent": "research/readiness-20261021/certificates/172_21_66.json",
                "source": "https://arxiv.org/html/2609.37056v1",
                "authors_of_inherited_construction": "Seddas, Shashkov, Viazovska, Abbe",
            },
        }
        name = "control-" + "-".join(f"{f:x}" for f in family["factors"]) + ".json"
        path = output / name
        path.write_text(json.dumps(certificate, indent=2) + "\n")
        other = large_verify.check(path)
        if other["spectrum"] != spectrum:
            raise ValueError("exhaustive spectrum disagreement")
        control = {"factors": family["factors"], "multiplier": multiplier,
                   "d": distance, "minimum_words": spectrum[distance],
                   "object": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                   "spectrum": spectrum}
        controls.append(control)
        print(json.dumps({k: control[k] for k in ("object", "d", "minimum_words")}), flush=True)
    (output / "spectra.json").write_text(json.dumps(controls, indent=2) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: matrix_controls.py RESULT_JSON NEW_OUTPUT_DIRECTORY")
    run(Path(sys.argv[1]), Path(sys.argv[2]))
