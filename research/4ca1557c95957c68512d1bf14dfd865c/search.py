"""Exhaust the fixed single-factor-swap domain; preserve rejection witnesses."""

import hashlib
import json
import platform
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_structured import div, mul

SEED = "4ca1557c95957c68512d1bf14dfd865c"
BASE = "76267c387538b4fb0e802278530b575bab4d1f76"
MODULUS = (1 << 85) | 1
TAIL_FACTOR = (1 << 5) | 1
OLD = (0x17B, 0x1A3)
FACTORS = (0x139, 0x13F, 0x177, 0x17B, 0x18B,
           0x1A3, 0x1BD, 0x1D7, 0x1DD, 0x1F9)
PAIRS = sorted({tuple(sorted((keep, swap))) for keep in OLD
                for swap in FACTORS if swap not in OLD})
TARGET = 67


def weights(check):
    """Weights of all words (M/check)*message, in message-index order."""
    generator, remainder = div(MODULUS, check)
    assert remainder == 0
    dimension = check.bit_length() - 1
    out = bytearray(1 << dimension)
    word = 0
    for i in range(1, len(out)):
        word ^= generator << ((i & -i).bit_length() - 1)
        out[i ^ (i >> 1)] = word.bit_count()
    return out


def orbits(check, word_weights):
    """Least residue in each orbit under multiplication by x modulo check."""
    limit = 1 << (check.bit_length() - 1)
    seen = bytearray(limit)
    representatives = []
    for message in range(limit):
        if seen[message]:
            continue
        representatives.append(message)
        current, length = message, 0
        while True:
            assert not seen[current]
            assert current >= message
            assert word_weights[current] == word_weights[message]
            seen[current] = 1
            length += 1
            current <<= 1
            if current & limit:
                current ^= check
            if current == message:
                break
        assert 85 % length == 0
    assert all(seen)
    return representatives


def first_rejection(multiplier, check, word_weights, messages, tails):
    """Return a low word, or the exact minimum over the message orbits."""
    best = (173, 0)
    for message in messages:
        product = div(mul(message, multiplier), check)[1]
        weight = word_weights[message] + word_weights[product]
        if tails:
            weight += 2 * (message.bit_count() & 1)
        if weight < best[0]:
            best = weight, message
        if weight < TARGET:
            return best
    return best


def certificate(pair, multiplier, distance):
    check = mul(TAIL_FACTOR, mul(*pair))
    generator, remainder = div(MODULUS, check)
    assert remainder == 0
    rows = []
    for j in range(21):
        left = generator << j
        right = div(mul(left, multiplier), MODULUS)[1]
        row = left | (right << 85) | (3 << 170)
        rows.append("".join(str((row >> i) & 1) for i in range(172)))
    return {
        "format": "binary-generator-v1", "q": 2, "n": 172, "k": 21,
        "d": distance, "rows": rows,
        "provenance": {
            "kind": "coupled-factor-multiplier-search", "seed": SEED,
            "degree_eight_factors": list(pair), "multiplier": multiplier,
            "parent": "research/readiness-20261021/certificates/172_21_66.json",
            "source": "https://arxiv.org/html/2609.37056v1",
        },
    }


def controls():
    assert len(PAIRS) == 16
    product = TAIL_FACTOR
    for factor in FACTORS:
        assert div(MODULUS, factor)[1] == 0
        product = mul(product, factor)
    assert product == MODULUS
    check = mul(*OLD)
    word_weights = weights(check)
    representatives = orbits(check, word_weights)
    messages = sorted(representatives[1:], key=lambda m: (word_weights[m], m))
    assert first_rejection(div(0x2A5F, check)[1], check,
                           word_weights, messages, False)[0] == 68
    assert first_rejection(0, check, word_weights, messages, False)[0] < TARGET


def run(output):
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    controls()
    families = []
    for pair in PAIRS:
        h16 = mul(*pair)
        w16 = weights(h16)
        representatives = orbits(h16, w16)
        messages = sorted(representatives[1:], key=lambda m: (w16[m], m))
        rejected, surviving = [], []
        for multiplier in representatives:
            distance, message = first_rejection(multiplier, h16, w16, messages, False)
            if distance < TARGET:
                rejected.append([multiplier, message, distance])
            else:
                surviving.append(multiplier)
        full_rejected, full_surviving = [], []
        if surviving:
            h21 = mul(TAIL_FACTOR, h16)
            w21 = weights(h21)
            full_representatives = orbits(h21, w21)
            full_messages = sorted(full_representatives[1:], key=lambda m:
                                   (w21[m] + 2 * (m.bit_count() & 1), m))
            for residue in surviving:
                for lift in range(32):
                    multiplier = residue ^ mul(h16, lift)
                    distance, message = first_rejection(
                        multiplier, h21, w21, full_messages, True)
                    if distance < TARGET:
                        full_rejected.append([multiplier, message, distance])
                    else:
                        name = f"candidate-{pair[0]:x}-{pair[1]:x}-{multiplier:x}.json"
                        path = output / name
                        path.write_text(json.dumps(certificate(pair, multiplier, distance), indent=2) + "\n")
                        full_surviving.append([multiplier, distance, name])
        family = {
            "factors": list(pair), "check16": h16,
            "multiplier_orbits16": len(representatives),
            "restricted_rejections": rejected,
            "restricted_survivors": surviving,
            "full_rejections": full_rejected, "full_survivors": full_surviving,
        }
        families.append(family)
        print(json.dumps({
            "pair": [hex(f) for f in pair], "orbits16": len(representatives),
            "restricted_survivors": len(surviving),
            "full_rejections": len(full_rejected),
            "full_survivors": len(full_surviving),
            "elapsed_seconds": round(time.perf_counter() - started, 3),
        }), flush=True)
    sources = [Path(__file__), ROOT / "scripts/prepare_structured.py",
               ROOT / "research/readiness-20261021/certificates/172_21_66.json"]
    result = {
        "schema": "single-factor-swap-witnesses-v1", "seed": SEED, "base": BASE,
        "target_distance": TARGET, "n": 172, "k": 21,
        "factor_pairs": len(PAIRS), "multipliers_per_pair": 1 << 21,
        "domain_size": len(PAIRS) * (1 << 21),
        "families": families,
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sources},
        "python": platform.python_version(),
        "seconds": time.perf_counter() - started,
        "evidence_level": "author-checked",
        "claim": "Finite fixed-tail single-factor-swap domain only; no unrestricted optimality or novelty claim.",
    }
    (output / "result.json").write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(json.dumps({"status": "complete", "domain_size": result["domain_size"],
                      "threshold_survivors": sum(len(f["full_survivors"]) for f in families),
                      "seconds": result["seconds"]}), flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: search.py NEW_OUTPUT_DIRECTORY")
    run(Path(sys.argv[1]))
