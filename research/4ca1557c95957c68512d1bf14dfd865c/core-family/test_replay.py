"""Failure controls, coordinate checks, and the finite CRT projection cases."""

import copy
import gzip
import itertools
import json
import sys
import unittest
from pathlib import Path

import replay

PACKAGE = Path(__file__).parent
sys.path.insert(0, str(replay.ROOT / "scripts"))
from prepare_structured import construct


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(gzip.decompress((PACKAGE / "run/result.json.gz").read_bytes()))

    def reject(self, change, reason):
        data = copy.deepcopy(self.result)
        change(data)
        with self.assertRaisesRegex(ValueError, reason):
            replay.check(data)

    def test_complete_upper_bound(self):
        result = replay.check(self.result)
        self.assertEqual(result["represented_core_choices"], 94371840)
        self.assertEqual(result["restricted_witnesses"], 31536)
        self.assertEqual(result["full_witnesses"], 207360)
        self.assertEqual(result["maximum_witness_weight"], 64)

    def test_attaining_parent_certificates(self):
        result = replay.attainment(PACKAGE / "run")
        self.assertEqual(result["attained_core_distance"], 64)
        self.assertEqual(result["attained_two_column_distance"], 66)
        self.assertEqual(result["extended_minimum_words"], 2720)

    def test_all_divisor_coordinate_models(self):
        for pair in replay.domain_pairs():
            generator, remainder = replay.divide(replay.M, replay.product(replay.P, replay.product(*pair)))
            self.assertEqual(remainder, 0)
            factors = [[1, 0], [4, 3, 2, 1, 0]] + [
                [i for i in range(9) if (f >> i) & 1] for f in pair]
            for multiplier in (0, 1, 0x2A5F):
                spec = [172, 21, 1, 85, factors,
                        [[0], [i for i in range(21) if (multiplier >> i) & 1]],
                        ["11111", "11111"]]
                rows = [row & ((1 << 170) - 1) for row in construct(spec)]
                for message in (1, 103, 503, (1 << 21) - 1):
                    word = 0
                    for j, row in enumerate(rows):
                        if (message >> j) & 1:
                            word ^= row
                    self.assertEqual(word, replay.core_word(generator, multiplier, message))

    def test_short_rotation_orbits_are_covered(self):
        family = next(f for f in self.result["families"] if f["factors"] == [0x139, 0x1D7])
        self.assertEqual(family["multiplier_orbits16"], 3856)
        self.assertEqual(sum(f["multiplier_orbits16"] for f in self.result["families"]), 38016)

    def test_projection_case_classification(self):
        replay.structural_checks()
        for axes in itertools.product(("left", "right", "both"), repeat=4):
            degrees = (1, 4, 8, 8)
            left = sum(d for d, axis in zip(degrees, axes) if axis != "right")
            right = sum(d for d, axis in zip(degrees, axes) if axis != "left")
            if left < 21 and right < 21:
                self.assertTrue(any(d > 1 and axis != "both" for d, axis in zip(degrees, axes)))

    def test_zero_witness(self):
        self.reject(lambda d: d["families"][0]["restricted_rejections"][0].__setitem__(1, 0),
                    "restricted nonzero message")

    def test_changed_weight(self):
        self.reject(lambda d: d["families"][0]["restricted_rejections"][0].__setitem__(2, 1),
                    "restricted witness weight")

    def test_missing_orbit(self):
        def change(data):
            data["families"][0]["restricted_rejections"].pop()
            data["families"][0]["multiplier_orbits16"] -= 1
        self.reject(change, "missing rotation orbit")

    def test_duplicate_orbit(self):
        def change(data):
            family = data["families"][0]
            family["restricted_rejections"].append(family["restricted_rejections"][0])
            family["multiplier_orbits16"] += 1
        self.reject(change, "duplicate orbit")

    def test_missing_lift(self):
        def change(data):
            next(f for f in data["families"] if f["full_rejections"])["full_rejections"].pop()
        self.reject(change, "missing full lift")

    def test_duplicate_lift(self):
        def change(data):
            entries = next(f for f in data["families"] if f["full_rejections"])["full_rejections"]
            entries.append(entries[0])
        self.reject(change, "unexpected/duplicate lift")

    def test_changed_full_weight(self):
        def change(data):
            entries = next(f for f in data["families"] if f["full_rejections"])["full_rejections"]
            entries[0][2] = 1
        self.reject(change, "full witness weight")

    def test_threshold_survivor(self):
        self.reject(lambda d: d["families"][0]["full_survivors"].append([1, 66, 1]),
                    "threshold survivor")

    def test_wrong_domain(self):
        self.reject(lambda d: d.update(core_threshold=67), "header: core_threshold")

    def test_omitted_divisor(self):
        self.reject(lambda d: d["families"].pop(), "family count")

    def test_source_hash_mismatch(self):
        data = copy.deepcopy(self.result)
        data["source_sha256"]["scripts/codes.py"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source hash: scripts/codes.py"):
            replay.source_hashes(data)

    def test_false_attainment_claim(self):
        control = json.loads((PACKAGE / "run/parent-core-170-21-64.json").read_text())
        control["d"] = 65
        with self.assertRaisesRegex(ValueError, "control parameters"):
            replay.certificate_spectrum(control, 170, 64)


if __name__ == "__main__":
    unittest.main()
