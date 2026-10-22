"""Integration checks kept separate from the independently implemented replay."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
import codes
import independent


class ReplayTests(unittest.TestCase):
    def test_complete_spectra_agree(self):
        saved = json.loads((HERE / "results.json").read_text())
        for name, expected in saved["certificates"].items():
            for check in (codes.check, independent.check):
                with self.subTest(certificate=name, checker=check.__module__):
                    actual = check(HERE / "inputs" / name)
                    for key in ("n", "k", "d", "spectrum"):
                        self.assertEqual(actual[key], expected[key])

    def test_coordinate_reversal_and_unicode_digit(self):
        parent = json.loads((HERE / "inputs/55_16_19.json").read_text())
        expected = json.loads((HERE / "results.json").read_text())["certificates"]["55_16_19.json"]
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            path = Path(tmp) / "control.json"
            reversed_code = copy.deepcopy(parent)
            reversed_code["rows"] = [row[::-1] for row in parent["rows"]]
            path.write_text(json.dumps(reversed_code))
            for check in (codes.check, independent.check):
                self.assertEqual(check(path)["spectrum"], expected["spectrum"])

            malformed = copy.deepcopy(parent)
            malformed["rows"][0] = malformed["rows"][0].replace("1", "\u0661", 1)
            path.write_text(json.dumps(malformed))
            for check in (codes.check, independent.check):
                with self.subTest(checker=check.__module__):
                    with self.assertRaises(ValueError):
                        check(path)


if __name__ == "__main__":
    unittest.main()
