"""Positive controls and corrupt-artifact controls for the witness checker."""

import copy
import json
import unittest
from pathlib import Path

import replay


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads((Path(__file__).parent / "run/result.json").read_text())

    def reject(self, change, reason):
        changed = copy.deepcopy(self.result)
        change(changed)
        with self.assertRaisesRegex(ValueError, reason):
            replay.check(changed)

    def test_complete_saved_obstruction(self):
        report = replay.check(self.result)
        self.assertEqual(report["represented_parameter_choices"], 33554432)
        self.assertEqual(report["restricted_witnesses"], 11000)
        self.assertEqual(report["full_witnesses"], 44800)
        self.assertEqual(report["maximum_witness_weight"], 66)

    def test_published_parent_even_and_odd_messages(self):
        h = replay.product(0x21, replay.product(0x17B, 0x1A3))
        generator, remainder = replay.quotient_remainder(replay.M, h)
        self.assertEqual(remainder, 0)
        self.assertEqual(replay.word_weight(generator, 0x2A5F, 503), 66)
        self.assertEqual(replay.word_weight(generator, 0x2A5F, 103), 66)
        self.assertEqual((503).bit_count() % 2, 0)
        self.assertEqual((103).bit_count() % 2, 1)

    def test_saved_matrix_coordinates_match_direct_reconstruction(self):
        folder = Path(__file__).parent / "controls"
        controls = json.loads((folder / "spectra.json").read_text())
        self.assertEqual(len(controls), 16)
        for control in controls:
            certificate = json.loads((folder / control["object"]).read_text())
            rows = [sum(int(bit) << j for j, bit in enumerate(row))
                    for row in certificate["rows"]]
            h = replay.product(0x21, replay.product(*control["factors"]))
            generator, remainder = replay.quotient_remainder(replay.M, h)
            self.assertEqual(remainder, 0)
            messages = [1 << j for j in range(21)] + [103, 503, (1 << 21) - 1]
            for message in messages:
                word = 0
                for j, row in enumerate(rows):
                    if (message >> j) & 1:
                        word ^= row
                self.assertEqual(word.bit_count(), replay.word_weight(
                    generator, control["multiplier"], message))

    def test_changed_restricted_weight(self):
        def change(result):
            result["families"][0]["restricted_rejections"][0][2] += 1
        self.reject(change, "restricted witness weight")

    def test_zero_message(self):
        def change(result):
            result["families"][0]["restricted_rejections"][0][1] = 0
        self.reject(change, "restricted nonzero message")

    def test_missing_orbit(self):
        def change(result):
            family = result["families"][0]
            family["restricted_rejections"].pop()
            family["multiplier_orbits16"] -= 1
        self.reject(change, "missing rotation orbit")

    def test_duplicate_orbit(self):
        def change(result):
            family = result["families"][0]
            family["restricted_rejections"].append(family["restricted_rejections"][0])
            family["multiplier_orbits16"] += 1
        self.reject(change, "duplicate orbit")

    def test_noncanonical_orbit(self):
        def change(result):
            family = result["families"][0]
            for entry in family["restricted_rejections"]:
                shifted = replay.quotient_remainder(entry[0] << 1, family["check16"])[1]
                if shifted != entry[0]:
                    entry[0] = shifted
                    return
            self.fail("expected a nontrivial orbit")
        # The shifted multiplier may already invalidate its saved word.
        self.reject(change, "restricted witness weight|noncanonical|duplicate orbit")

    def test_missing_lift(self):
        def change(result):
            next(f for f in result["families"] if f["full_rejections"])["full_rejections"].pop()
        self.reject(change, "missing multiplier lift")

    def test_duplicate_lift(self):
        def change(result):
            entries = next(f for f in result["families"] if f["full_rejections"])["full_rejections"]
            entries.append(entries[0])
        self.reject(change, "unexpected or duplicate lift")

    def test_changed_full_weight(self):
        def change(result):
            entries = next(f for f in result["families"] if f["full_rejections"])["full_rejections"]
            entries[0][2] = 1
        self.reject(change, "full witness weight")

    def test_threshold_survivor(self):
        def change(result):
            result["families"][0]["full_survivors"] = [[1, 68, "unreviewed.json"]]
        self.reject(change, "threshold survivor")

    def test_missing_family(self):
        self.reject(lambda result: result["families"].pop(), "family count")

    def test_changed_target(self):
        self.reject(lambda result: result.update(target_distance=68), "header: target_distance")

    def test_source_hash_mismatch(self):
        changed = copy.deepcopy(self.result)
        name = "scripts/prepare_structured.py"
        changed["source_sha256"][name] = "0" * 64
        with self.assertRaisesRegex(ValueError, "source hash: " + name):
            replay.source_hashes(changed)


if __name__ == "__main__":
    unittest.main()
