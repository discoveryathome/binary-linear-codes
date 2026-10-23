"""Published profile A, normalized to degree-three line (1,1,1)."""

import json
import model


def parameters():
    path = model.ROOT / "research/readiness-20261021/certificates/189_22_72.json"
    parent = json.loads(path.read_text())
    spec = parent["provenance"]["construction"]
    factors = [sum(1 << j for j in f) for f in spec[4]]
    three = next(f for f in factors if f.bit_length() == 4)
    six = [f for f in factors if f.bit_length() == 7]
    f = sum(1 << j for j in spec[5][1])
    g = sum(1 << j for j in spec[5][2])
    rotations = [next(r for r in range(7) if model.div(model.mul(value, 1 << r), three)[1] == 1)
                 for value in (f, g)]
    scalars = []
    for factor in six:
        scalars += [model.div(model.mul(value, 1 << rotation), factor)[1]
                    for value, rotation in zip((f, g), rotations)]
    if len(six) != 3 or any(not 1 <= value < 64 for value in scalars):
        raise ValueError("parent field coordinates")
    return {"degree_three": three, "factors": six, "scalars": scalars,
            "block_rotations": [0] + rotations, "parent": parent}


def construct(three, factors, scalars):
    if three not in (0xB, 0xD) or len(factors) != 3 or len(set(factors)) != 3:
        raise ValueError("profile-A factors")
    if not set(factors) <= set(model.FACTORS6) or len(scalars) != 6 or any(not 1 <= x < 64 for x in scalars):
        raise ValueError("field scalar domain")
    g1, _ = model.div(model.M, 3)
    g3, remainder = model.div(model.M, three)
    if remainder:
        raise ValueError("degree-three divisor")
    rows = [model.block_word(g1, g1, g1)]
    rows += [model.block_word(g3 << j, g3 << j, g3 << j) for j in range(3)]
    for i, factor in enumerate(factors):
        generator, _ = model.div(model.M, factor)
        for j in range(6):
            left = generator << j
            rows.append(model.block_word(left, model.div(model.mul(left, scalars[2*i]), model.M)[1],
                                         model.div(model.mul(left, scalars[2*i+1]), model.M)[1]))
    return rows


def packed(scalars):
    return sum(value << (6*i) for i,value in enumerate(scalars))
