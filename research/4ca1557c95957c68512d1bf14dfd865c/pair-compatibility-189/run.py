"""Run complete conservative pair tables and the capped deterministic full join."""

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


def controls(binary, output):
    output.mkdir()
    coordinate_count = 0
    for profile in ("B","C"):
        for pair in model.PAIRS:
            actual = subprocess.check_output([str(binary),"--emit",profile,*map(str,pair),"193","709"],text=True)
            parsed = [[int(v,16) for v in row.split()] for row in actual.splitlines()]
            expected = [model.chunks(row) for row in model.construct(profile,pair,(1,5,3,11))]
            if parsed != expected:
                raise ValueError("pair coordinate control")
            coordinate_count += 1
        for triple in model.TRIPLES:
            scalars = (3,5,7,11,13,17)
            actual = subprocess.check_output([str(binary),"--emit-full",profile,
                                              *map(str,triple),*map(str,scalars)],text=True)
            parsed = [[int(v,16) for v in row.split()] for row in actual.splitlines()]
            if parsed != [model.chunks(row) for row in model.construct(profile,triple,scalars)]:
                raise ValueError("full coordinate control")
            coordinate_count += 1
    parent_path = model.ROOT / "research/readiness-20261021/certificates/189_22_72.json"
    parent = json.loads(parent_path.read_text())
    parent_rows = [sum(int(bit) << j for j,bit in enumerate(row)) for row in parent["rows"]]
    cases = [("published-parent",parent_rows)]
    for profile in ("B","C"):
        cases += [("pair-"+profile,model.construct(profile,(0x43,0x57),(1,5,3,11))),
                  ("full-"+profile,model.construct(profile,(0x43,0x49,0x57),(3,5,7,11,13,17)))]
    results = []
    for name,rows in cases:
        if len(codes.basis(rows)) != len(rows):
            raise ValueError("control rank")
        hist = codes.spectrum(rows,189)
        d = next(i for i in range(1,190) if hist[i])
        obj = {"format":"binary-generator-v1","q":2,"n":189,"k":len(rows),"d":d,
               "rows":["".join(str((row >> j)&1) for j in range(189)) for row in rows],
               "provenance":{"kind":"compatibility-kernel-control","name":name,
                             "parent_credit":"Seddas, Shashkov, Viazovska, Abbe"}}
        path = output / (name+".json")
        path.write_text(json.dumps(obj,indent=2)+"\n")
        if large_verify.check(path)["spectrum"] != hist:
            raise ValueError("control full spectra")
        control = output / "control.rows"
        control.write_text(str(len(rows))+"\n"+"\n".join(
            " ".join(f"{chunk:x}" for chunk in model.chunks(row)) for row in rows)+"\n")
        cpp = json.loads(subprocess.check_output([str(binary),"--check",str(control)],text=True))
        control.unlink()
        if cpp != {"d":d,"minimum_words":hist[d]}:
            raise ValueError("control C++ spectrum")
        (output / (name+"-spectrum.json")).write_text(json.dumps(hist)+"\n")
        results.append({"name":name,"k":len(rows),"d":d,"minimum_words":hist[d],"sha256":digest(path)})
    (output / "results.json").write_text(json.dumps(results,indent=2)+"\n")
    return coordinate_count


def run(binary, output):
    output.mkdir(parents=True,exist_ok=False)
    started = time.perf_counter()
    coordinate_count = controls(binary,output / "controls")
    subprocess.run([str(binary),"--run",str(output)],check=True)
    summary = json.loads((output / "summary.json").read_text())
    if summary["pair_choices"] != 3143448 or summary["cap"] != 2000000 or summary["full_checked"] > 2000000:
        raise ValueError("fixed domain/cap")
    full_raw = (output / "full-ledger.csv").read_bytes()
    count,last = 0,None
    for row in csv.DictReader(io.StringIO(full_raw.decode())):
        count += 1
        last = row
    if count != summary["full_checked"]:
        raise ValueError("full ledger count")
    if summary["target_found"]:
        if last is None or int(last["exact"]) != 1:
            raise ValueError("target record")
        template = int(last["template"])
        profile,triple = [(p,t) for p in ("B","C") for t in model.TRIPLES][template]
        packed = int(last["scalars"])
        scalars = [(packed >> (6*j)) & 63 for j in range(6)]
        obj = model.certificate(profile,triple,scalars,int(last["d_or_upper"]))
        path = output / "target.json"
        path.write_text(json.dumps(obj,indent=2)+"\n")
        hist = codes.spectrum(model.construct(profile,triple,scalars),189)
        if large_verify.check(path)["spectrum"] != hist or hist[obj["d"]] != int(last["minimum_words"]):
            raise ValueError("target full spectra")
        (output / "target-spectrum.json").write_text(json.dumps(hist)+"\n")
    artifacts = {}
    for name in ("pair-witnesses.bin","full-ledger.csv"):
        raw = (output / name).read_bytes()
        compressed = gzip.compress(raw,mtime=0)
        path = output / (name+".gz")
        path.write_bytes(compressed)
        (output / name).unlink()
        artifacts[name] = {"raw_sha256":hashlib.sha256(raw).hexdigest(),
                           "compressed_sha256":digest(path),"bytes":len(raw)}
    sources = [Path(__file__).resolve(),PACKAGE/"model.py",PACKAGE/"compatibility.cpp",
               model.ROOT/"scripts/codes.py",model.ROOT/"scripts/large_verify.py",
               model.ROOT/"research/readiness-20261021/certificates/189_22_72.json"]
    metadata = {"schema":"pair-compatibility-v1","seed":model.SEED,"base":model.BASE,
                "threshold":74,"pair_choices":3143448,"full_cap":2000000,
                "coordinate_controls":coordinate_count,"spectrum_controls":5,
                "source_sha256":{str(p.relative_to(model.ROOT)):digest(p) for p in sources},
                "artifacts":artifacts,"kernel_sha256":digest(binary),
                "compiler":subprocess.check_output(["c++","--version"],text=True).splitlines()[0],
                "compiler_flags":"-O3 -std=c++17 -march=native","python":platform.python_version(),
                "seconds":time.perf_counter()-started,"evidence_level":"author-checked",
                "claim":"Conservative pair constraints; a full B/C exclusion requires a complete negative join."}
    (output / "metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps({"summary":summary,"seconds":metadata["seconds"]}))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: run.py FRESH_BINARY NEW_OUTPUT")
    run(Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve())
