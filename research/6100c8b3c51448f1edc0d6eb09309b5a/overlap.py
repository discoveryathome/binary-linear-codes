"""Experimental exact distance with an incidence bound for overlapping information sets."""
from bisect import bisect_left
from itertools import accumulate, combinations
from math import comb


class BudgetExceeded(RuntimeError):
    def __init__(self, enumerated, limit):
        self.enumerated = enumerated
        self.limit = limit
        super().__init__(f"visit budget {limit}: stopped after {enumerated}; no distance certified")


def systematic_on(rows, columns):
    basis = list(rows)
    for i, column in enumerate(columns):
        pivot = next((j for j in range(i, len(basis)) if (basis[j] >> column) & 1), None)
        if pivot is None:
            raise ValueError("dependent information set or generator")
        basis[i], basis[pivot] = basis[pivot], basis[i]
        for j in range(len(basis)):
            if j != i and (basis[j] >> column) & 1:
                basis[j] ^= basis[i]
    return basis


def certified(rows, n, information_sets, max_visits=1_000_000):
    """Certify a fixed full-rank generator; an incomplete layer raises, never certifies.

    Coordinate j is integer bit j, matching the repository's JSON convention.
    Duplicate sets are safe but waste visits. Coordinates within a set must be distinct.
    """
    if type(n) is not int or not 1 <= n <= 512:
        raise ValueError("length must be an integer in 1..512")
    rows = list(rows)
    k = len(rows)
    if not 1 <= k <= min(n, 20):
        raise ValueError("dimension budget is 1..20")
    if any(type(row) is not int or not 0 <= row < 1 << n for row in rows):
        raise ValueError("generator row outside its declared binary width")
    if type(max_visits) is not int or max_visits < 1:
        raise ValueError("positive integer visit budget required")
    info = [list(columns) for columns in information_sets]
    if not info:
        raise ValueError("at least one information set required")
    for columns in info:
        if len(columns) != k or any(type(j) is not int or not 0 <= j < n for j in columns):
            raise ValueError("invalid information-set coordinates")
        if len(set(columns)) != k:
            raise ValueError("repeated coordinate within an information set")
    bases = [systematic_on(rows, columns) for columns in info]
    multiplicities = [0] * n
    for columns in info:
        for j in columns:
            multiplicities[j] += 1
    capacity = [0] + list(accumulate(sorted(multiplicities, reverse=True)))
    upper, witness, visits = n + 1, None, 0
    for depth in range(1, k + 1):
        layer_visits = len(info) * comb(k, depth)
        if visits + layer_visits > max_visits:
            raise BudgetExceeded(visits, max_visits)
        for basis in bases:
            for support in combinations(range(k), depth):
                word = 0
                for i in support:
                    word ^= basis[i]
                visits += 1
                if word.bit_count() < upper:
                    upper, witness = word.bit_count(), word
        required = len(info) * (depth + 1)
        # A weight-w support meets the sets at most capacity[w] times in total.
        lower = bisect_left(capacity, required)
        if depth == k or lower >= upper:
            return dict(n=n, k=k, d=upper, exact=True,
                        minimum_word="".join(str((witness >> j) & 1) for j in range(n)),
                        sets=info, coordinate_multiplicities=multiplicities,
                        enumeration_depth=depth, enumerated=visits,
                        required_incidences=required, unenumerated_lower_bound=lower,
                        no_unenumerated_words=(depth == k or required > capacity[-1]))
    raise AssertionError("full enumeration must terminate")
