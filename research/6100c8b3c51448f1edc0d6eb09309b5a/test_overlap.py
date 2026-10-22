"""Bounded exhaustive and adversarial tests; baseline checkers stay separate."""
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import codes
import independent
import information_sets
from overlap import BudgetExceeded, certified, systematic_on


class OverlapTests(unittest.TestCase):
    def test_naive_overlap_counterexample(self):
        c, rows = codes.read_cert(HERE / "counterexample.json")
        info = c["provenance"]["information_sets_zero_based"]
        naive_upper = min(row.bit_count() for columns in info for row in systematic_on(rows, columns))
        self.assertEqual(naive_upper, 4)
        self.assertGreaterEqual(len(info) * 2, naive_upper)
        self.assertEqual(codes.check(HERE / "counterexample.json")["d"], 3)
        self.assertEqual(independent.check(HERE / "counterexample.json")["d"], 3)
        with self.assertRaises(ValueError):
            information_sets.certified(rows, c["n"], info)
        result = certified(rows, c["n"], info)
        self.assertEqual((result["d"], result["enumeration_depth"], result["minimum_word"]),
                         (3, 2, "111000"))

    def test_punctured_control_and_budget_boundary(self):
        c, rows = codes.read_cert(HERE / "punctured_bch_31_16.json")
        info = [list(range(16)), list(range(15, 31))]
        result = certified(rows, c["n"], info, max_visits=1392)
        self.assertEqual((result["d"], result["enumerated"], result["enumeration_depth"]), (7, 1392, 3))
        self.assertEqual(result["unenumerated_lower_bound"], 7)
        with self.assertRaises(BudgetExceeded) as caught:
            certified(rows, c["n"], info, max_visits=1391)
        self.assertEqual(caught.exception.enumerated, 272)
        self.assertIn("no distance certified", str(caught.exception))

    def test_disjoint_compatibility(self):
        for n in (32, 64):
            _, rows = codes.read_cert(ROOT / f"certificates/control_bch_{n}_16.json")
            info = information_sets.sets(rows, n)
            result, old = certified(rows, n, info), information_sets.certified(rows, n, info)
            for key in ("d", "minimum_word", "enumeration_depth", "enumerated", "unenumerated_lower_bound"):
                self.assertEqual(result[key], old[key])

    def test_small_codes_against_two_checkers_and_unseen_words(self):
        rng = random.Random(int("6100c8b3c51448f1edc0d6eb09309b5a", 16))
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            path = Path(tmp) / "control.json"
            for trial in range(100):
                k = rng.randrange(2, 7)
                n = rng.randrange(k, 15)
                rows = [(1 << i) | (rng.getrandbits(n - k) << k) for i in range(k)]
                info = [list(range(k))]
                for _ in range(12):
                    columns = rng.sample(range(n), k)
                    try:
                        systematic_on(rows, columns)
                    except ValueError:
                        continue
                    info.append(columns)
                    if len(info) == 5:
                        break
                codes.write_cert(path, rows, n, {"kind": "seeded test", "trial": trial})
                result = certified(rows, n, info)
                with self.subTest(trial=trial, n=n, k=k):
                    for checker in (codes.check, independent.check):
                        self.assertEqual(result["d"], checker(path)["d"])
                    words = {0}
                    for row in rows:
                        words |= {word ^ row for word in words}
                    witness = int(result["minimum_word"][::-1], 2)
                    self.assertIn(witness, words - {0})
                    self.assertEqual(witness.bit_count(), result["d"])
                    masks = [sum(1 << j for j in columns) for columns in info]
                    unseen = [word for word in words - {0}
                              if all((word & mask).bit_count() > result["enumeration_depth"] for mask in masks)]
                    if unseen:
                        self.assertFalse(result["no_unenumerated_words"])
                        self.assertLessEqual(result["unenumerated_lower_bound"],
                                             min(word.bit_count() for word in unseen))

    def test_duplicate_sets_and_exhaustion(self):
        rows = [57, 62]
        result = certified(rows, 6, [[0, 1]] * 3)
        self.assertEqual(result["d"], 3)
        self.assertEqual(result["enumeration_depth"], 2)
        self.assertTrue(result["no_unenumerated_words"])

    def test_reject_invalid_inputs(self):
        cases = [
            ([], 2, [[0, 1]]), ([1, 1], 2, [[0, 1]]),
            ([5, 6], 2, [[0, 1]]), ([-1, 2], 2, [[0, 1]]),
            ([True, 2], 2, [[0, 1]]), ([1, 2], True, [[0, 1]]),
            ([1, 2], 513, [[0, 1]]), ([1, 2], 2, []),
            ([1, 2], 2, [[0, 0]]), ([1, 2], 2, [[0]]),
            ([1, 2], 4, [[2, 3]]), ([1, 2], 2, [[0, True]]),
            ([1, 2], 2, [[0, -1]]), ([1, 2], 2, [[0, 2]]),
            ([1 << i for i in range(21)], 21, [list(range(21))]),
        ]
        for rows, n, info in cases:
            with self.subTest(rows=rows, n=n, info=info):
                with self.assertRaises(ValueError):
                    certified(rows, n, info)
        for budget in (0, -1, True, 1.5):
            with self.assertRaises(ValueError):
                certified([1], 1, [[0]], max_visits=budget)
        with self.assertRaises(BudgetExceeded):
            certified([1, 2], 2, [[0, 1]], max_visits=1)


if __name__ == "__main__":
    unittest.main()
