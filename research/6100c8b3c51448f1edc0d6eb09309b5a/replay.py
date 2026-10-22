"""Replay fixed certification controls and compare with exhaustive implementations."""
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import codes
import independent
import information_sets
import large_verify
from overlap import BudgetExceeded, certified


def require(condition, message):
    if not condition:
        raise ValueError(message)


def timed(function, *args, **kwargs):
    start = time.perf_counter()
    value = function(*args, **kwargs)
    return value, time.perf_counter() - start


def run():
    cases = [
        ("overlap_counterexample", HERE / "counterexample.json", [[0, 1], [0, 2]]),
        ("punctured_bch_31_16", HERE / "punctured_bch_31_16.json", [list(range(16)), list(range(15, 31))]),
        ("extended_bch_32_16", ROOT / "certificates/control_bch_32_16.json", None),
        ("extended_bch_64_16", ROOT / "certificates/control_bch_64_16.json", None),
        ("published_173_20", ROOT / "research/c0202026102018570000000000000001/published_173_20_68.json", None),
    ]
    results = {}
    measurements = dict(python=sys.version.split()[0], platform=platform.platform(),
                        note="One sequential run on a shared machine; timings are not benchmark guarantees.",
                        seconds={})
    for name, path, selected_sets in cases:
        c, rows = codes.read_cert(path)
        reference, gray_check_time = timed(codes.check, path)
        other, column_time = timed(independent.check, path)
        halves, halves_time = timed(large_verify.check, path)
        require(all(reference[key] == other[key] == halves[key] for key in other), "checker disagreement")
        legacy_sets = information_sets.sets(rows, c["n"])
        selected_sets = legacy_sets if selected_sets is None else selected_sets
        budget = 3_000_000 if c["k"] == 20 else 1_000_000
        result, new_time = timed(certified, rows, c["n"], selected_sets, max_visits=budget)
        legacy, old_time = timed(information_sets.certified, rows, c["n"], legacy_sets)
        gray_distance, gray_distance_time = timed(codes.distance, rows, c["n"])
        require(result["d"] == legacy["d"] == gray_distance == reference["d"], "distance mismatch")
        require(sum(reference["spectrum"]) == 2 ** c["k"], "spectrum size")
        results[name] = dict(
            path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            spectrum=reference["spectrum"], max_visits=budget, overlap=result,
            legacy={key: legacy[key] for key in ("d", "enumerated", "enumeration_depth", "sets")},
            gray_nonzero_visits=2 ** c["k"] - 1,
        )
        measurements["seconds"][name] = dict(overlap=new_time, legacy_disjoint=old_time,
                                               gray_distance=gray_distance_time,
                                               gray_check=gray_check_time,
                                               column_parity_check=column_time,
                                               subset_halves_check=halves_time)

    parent_path = ROOT / "certificates/control_bch_32_16.json"
    _, parent_rows = codes.read_cert(parent_path)
    derived, n = codes.puncture(parent_rows, 32, [31])
    c, saved_rows = codes.read_cert(HERE / "punctured_bch_31_16.json")
    require(n == c["n"] and derived == saved_rows, "puncturing replay mismatch")
    require(c["provenance"]["parent_sha256"] == hashlib.sha256(parent_path.read_bytes()).hexdigest(), "parent hash")

    c, rows = codes.read_cert(cases[-1][1])
    try:
        certified(rows, c["n"], information_sets.sets(rows, c["n"]))
    except BudgetExceeded as error:
        results["default_budget_control"] = dict(status="inconclusive", limit=error.limit,
                                                  completed_visits=error.enumerated)
    else:
        raise ValueError("million-visit control should be inconclusive")
    return results, measurements


if __name__ == "__main__":
    result, measurements = run()
    require(result == json.loads((HERE / "results.json").read_text()), "saved result mismatch")
    print(json.dumps(dict(status="PASS", controls=5, measurements=measurements), indent=2))
