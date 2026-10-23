"""Failure controls for finite coverage, provenance and threshold certificates."""

import copy
import csv
import gzip
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import model
import replay

PACKAGE = Path(__file__).resolve().parent
RUN = PACKAGE / "run"


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata = json.loads((RUN / "metadata.json").read_text())
        cls.cases = json.loads((RUN / "cases.json").read_text())
        with gzip.open(RUN / "ledger.csv.gz", "rt") as stream:
            cls.header = stream.readline()
            cls.first = list(csv.DictReader([cls.header, stream.readline()]))[0]
        path = next((RUN / "certificates").glob("*.json"))
        cls.certificate = json.loads(path.read_text())

    def bad(self, metadata=None, cases=None, first=None, reason=None):
        with tempfile.TemporaryDirectory(dir=PACKAGE) as folder:
            output = Path(folder)
            for name in ("ledger.csv.gz","spectra.json","certificates"):
                (output / name).symlink_to(RUN / name, target_is_directory=name=="certificates")
            obj = copy.deepcopy(self.metadata if metadata is None else metadata)
            if first is not None:
                text = io.StringIO()
                writer = csv.DictWriter(text, fieldnames=self.first.keys(), lineterminator="\n")
                writer.writeheader()
                writer.writerow(first)
                raw = text.getvalue().encode()
                compressed = gzip.compress(raw, mtime=0)
                (output / "ledger.csv.gz").unlink()
                (output / "ledger.csv.gz").write_bytes(compressed)
                obj["ledger_sha256"] = hashlib.sha256(raw).hexdigest()
                obj["compressed_ledger_sha256"] = hashlib.sha256(compressed).hexdigest()
            (output / "metadata.json").write_text(json.dumps(obj))
            (output / "cases.json").write_text(json.dumps(self.cases if cases is None else cases))
            with self.assertRaisesRegex(ValueError, reason or "."):
                replay.replay(output)

    def test_complete_data(self):
        result = replay.replay(RUN)
        self.assertEqual(result["tested"], 1335021)
        self.assertEqual(result["excluded_pairs"], 18)
        self.assertEqual(result["eligible_triples"], {"B":50,"C":50})

    def test_seed(self):
        metadata = copy.deepcopy(self.metadata)
        metadata["seed"] = "0"*32
        self.bad(metadata=metadata, reason="seed")

    def test_source_pin(self):
        metadata = copy.deepcopy(self.metadata)
        metadata["source_sha256"][next(iter(metadata["source_sha256"]))] = "0"*64
        self.bad(metadata=metadata, reason="source hash")

    def test_missing_case(self):
        self.bad(cases=self.cases[:-1], reason="case coverage")

    def test_incomplete_exclusion(self):
        cases = copy.deepcopy(self.cases)
        cases[0]["tested"] -= 1
        self.bad(cases=cases, reason="exhausted case coverage")

    def test_wrong_orbit_count(self):
        cases = copy.deepcopy(self.cases)
        next(c for c in cases if c["factors"] == [0x57,0x75])["orbit_representatives"] = 189
        self.bad(cases=cases, reason="case domain")

    def test_omitted_first_choice(self):
        first = dict(self.first, index="1")
        self.bad(first=first, reason="ordered prefix coverage")

    def test_wrong_representative(self):
        first = dict(self.first, f_pair="0")
        self.bad(first=first, reason="orbit representative choice")

    def test_zero_message(self):
        self.bad(first=dict(self.first, message="0"), reason="nonzero message")

    def test_false_weight(self):
        self.bad(first=dict(self.first, d_or_upper=str(int(self.first["d_or_upper"])+2)),
                 reason="witness weight")

    def test_false_exact_flag(self):
        self.bad(first=dict(self.first, exact="1"), reason="survivor stopping rule")

    def test_truncated_ledger(self):
        self.bad(first=self.first, reason="complete ledger coverage")

    def test_false_survivor_distance(self):
        cases = copy.deepcopy(self.cases)
        next(c for c in cases if c["survivor"])["d"] += 2
        self.bad(cases=cases, reason="attaining spectrum/metadata")

    def test_wrong_certificate_distance(self):
        obj = copy.deepcopy(self.certificate)
        obj["d"] -= 2
        with self.assertRaisesRegex(ValueError, "threshold/distance"):
            replay.spectrum(obj)

    def test_rank_defect(self):
        obj = copy.deepcopy(self.certificate)
        obj["rows"][1] = obj["rows"][0]
        with self.assertRaisesRegex(ValueError, "rank"):
            replay.spectrum(obj)

    def test_order_nine_shortening(self):
        for profile in ("B","C"):
            rows = model.construct(profile, (0x43,0x49), 193, 709)
            short = rows[:4] + rows[10:]
            decoded = []
            for row in short:
                value = 0
                for block in range(3):
                    bits = (row >> (63*block)) & ((1 << 63)-1)
                    small = bits & 511
                    self.assertEqual(bits, sum(small << (9*j) for j in range(7)))
                    value |= small << (9*block)
                decoded.append(value)
            words = [0]
            for row in decoded:
                words += [word ^ row for word in words]
            self.assertEqual(len(set(words)), 1024)
            self.assertLessEqual(min(word.bit_count() for word in words if word), 10)
        self.assertEqual(sum((11+(1 << j)-1)//(1 << j) for j in range(10)), 28)


if __name__ == "__main__":
    unittest.main()
