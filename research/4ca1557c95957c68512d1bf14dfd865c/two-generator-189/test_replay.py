"""Positive replays and meaningful false-claim controls for the retained evidence."""

import copy
import csv
import gzip
import io
import itertools
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import replay
import replay_pivot
import verify_pricing

PACKAGE = Path(__file__).parent


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata=json.loads((PACKAGE/"run/metadata.json").read_text())
        cls.summary=json.loads((PACKAGE/"run/summary.json").read_text())
        cls.raw=gzip.decompress((PACKAGE/"run/ledger.csv.gz").read_bytes()).decode()
        cls.oracle=replay.Oracle()
        cls.pricing=json.loads((PACKAGE/"pricing/pricing.json").read_text())

    def records(self):
        return csv.DictReader(io.StringIO(self.raw))

    def check_changed_record(self, change, reason, predicate=lambda row: True):
        def changed():
            done=False
            for row in self.records():
                if not done and predicate(row):
                    row=row.copy();change(row);done=True
                yield row
            self.assertTrue(done)
        with self.assertRaisesRegex(ValueError,reason):
            replay.check_records(changed(),self.metadata,self.summary,self.oracle)

    def test_complete_BC_evidence(self):
        result=replay.check(PACKAGE/"run")
        self.assertEqual(result["proposals"],199296)
        self.assertEqual(result["distinct_parameter_choices"],163272)
        self.assertEqual(result["attained_tested_list_maximum"],70)
        self.assertFalse(result["target_found"])

    def test_complete_small_pricing(self):
        result=verify_pricing.check(self.pricing)
        self.assertEqual(result["degree_three_pair_cases"],4096)
        self.assertEqual(result["degree_six_scalar_pairs"],35721)

    def test_complete_parent_neighborhood(self):
        result=replay_pivot.check(PACKAGE/"pivot")
        self.assertEqual(result["evaluated"],58033)
        self.assertEqual(result["maximum_witness"],72)
        self.assertFalse(result["target_found"])

    def test_zero_message(self):
        self.check_changed_record(lambda r:r.update(message="0"),"nonzero message")

    def test_false_weight(self):
        self.check_changed_record(lambda r:r.update(d_or_upper="1"),"proposal witness weight")

    def test_false_duplicate(self):
        self.check_changed_record(lambda r:r.update(duplicate="1"),"duplicate accounting")

    def test_missing_final_proposal(self):
        with self.assertRaisesRegex(ValueError,"final proposal counts"):
            replay.check_records(itertools.islice(self.records(),199295),self.metadata,self.summary,self.oracle)

    def test_early_rejection_cannot_be_accepted(self):
        self.check_changed_record(lambda r:r.update(accepted="1"),"early rejection semantics",
                                  lambda r:r["exact"]=="0")

    def test_wrong_derived_seed(self):
        metadata=copy.deepcopy(self.metadata);metadata["seed64"]^=1
        with self.assertRaisesRegex(ValueError,"executed seed derivation"):
            replay.check_records(self.records(),metadata,self.summary,self.oracle)

    def test_false_attainment_metadata(self):
        with tempfile.TemporaryDirectory(prefix=".audit-",dir=PACKAGE) as directory:
            path=Path(directory)
            for name in ("summary.json","ledger.csv.gz","best-B.json","best-C.json",
                         "best-B-spectrum.json","best-C-spectrum.json"):
                shutil.copyfile(PACKAGE/"run"/name,path/name)
            metadata=copy.deepcopy(self.metadata);metadata["certificates"][0]["d"]=72
            (path/"metadata.json").write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError,"best distance metadata"):
                replay.check(path)

    def test_source_mismatch(self):
        metadata=copy.deepcopy(self.metadata)
        metadata["source_sha256"]["scripts/codes.py"]="0"*64
        with self.assertRaisesRegex(ValueError,"source hash: scripts/codes.py"):
            replay.source_hashes(metadata)

    def test_wrong_small_plane(self):
        data=copy.deepcopy(self.pricing);data["low_B"][0]["normal"]=[0,1,1]
        with self.assertRaisesRegex(ValueError,"B plane equation"):
            verify_pricing.check(data)

    def test_missing_low_generator(self):
        data=copy.deepcopy(self.pricing);data["low_B"][0]["rows"].pop()
        with self.assertRaisesRegex(ValueError,"rank-four low model"):
            verify_pricing.check(data)

    def test_wrong_field_price(self):
        data=copy.deepcopy(self.pricing);data["degree6"][0]["unit_pair_distances"][0]=1
        with self.assertRaisesRegex(ValueError,"degree-six scalar-pair bounds"):
            verify_pricing.check(data)

    def test_wrong_pivot_basepoint(self):
        with tempfile.TemporaryDirectory(prefix=".audit-",dir=PACKAGE) as directory:
            path=Path(directory)
            for name in ("summary.json","ledger.csv.gz","normalized-parent.json",
                         "normalized-parent-spectrum.json"):
                shutil.copyfile(PACKAGE/"pivot"/name,path/name)
            metadata=json.loads((PACKAGE/"pivot/metadata.json").read_text())
            metadata["parent_scalars"][0]=1
            (path/"metadata.json").write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError,"normalized model rows"):
                replay_pivot.check(path)


if __name__=="__main__":
    unittest.main()
