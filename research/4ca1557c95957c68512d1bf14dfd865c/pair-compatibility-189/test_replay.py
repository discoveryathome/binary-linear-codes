"""Small failure controls; run replay.py separately for the complete retained data."""

import copy
import csv
import gzip
import io
import json
import struct
import tempfile
import types
import unittest
from pathlib import Path

import replay

PACKAGE = Path(__file__).resolve().parent
RUN = PACKAGE / "run"


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = replay.Oracle()
        cls.cases = json.loads((RUN/"pairs.json").read_text())
        cls.raw = gzip.decompress((RUN/"pair-witnesses.bin.gz").read_bytes())
        cls.metadata = json.loads((RUN/"metadata.json").read_text())
        with gzip.open(RUN/"full-ledger.csv.gz","rt") as stream:
            cls.record = {key:int(value) for key,value in next(csv.DictReader(stream)).items()}
        cls.template = cls.record["template"]
        cls.profile,cls.triple = cls.oracle.templates[cls.template]
        cls.scalars = tuple((cls.record["scalars"] >> (6*j))&63 for j in range(6))
        cls.control = json.loads((RUN/"controls/pair-B.json").read_text())

    def bad_pair(self, raw=None, cases=None, reason="."):
        with self.assertRaisesRegex(ValueError,reason):
            replay.pair_tables(self.oracle,self.cases if cases is None else cases,
                               self.raw if raw is None else raw)

    def bad_full(self, record, reason):
        with self.assertRaisesRegex(ValueError,reason):
            replay.full_record(self.oracle,self.profile,self.triple,self.scalars,
                               self.template,0,record)

    def test_actual_first_full_word(self):
        values = replay.full_record(self.oracle,self.profile,self.triple,self.scalars,
                                    self.template,0,self.record)
        self.assertLess(values["d_or_upper"],74)

    def test_short_pair_orbits(self):
        orbits = self.oracle.orbits[0x57,0x75]
        self.assertEqual(len(orbits),567)
        self.assertEqual({len(orbit) for orbit in orbits.values()},{7})
        self.assertEqual(len({value for orbit in orbits.values() for value in orbit}),3969)

    def test_primitive_root_orbits(self):
        for factor,reps in self.oracle.roots.items():
            self.assertEqual(len(reps),3)
            union = set()
            for start in reps:
                values,value = set(),start
                for _ in range(21):
                    values.add(value)
                    value = self.oracle.actions[factor][value]
                self.assertEqual(len(values),21)
                self.assertEqual(value,start)
                self.assertFalse(union & values)
                union |= values
            self.assertEqual(union,set(range(1,64)))

    def test_missing_pair_case(self):
        self.bad_pair(cases=self.cases[:-1],reason="pair table coverage")

    def test_short_binary_table(self):
        self.bad_pair(raw=self.raw[:-3],reason="pair table coverage")

    def test_wrong_pair_parameters(self):
        cases = copy.deepcopy(self.cases)
        cases[0]["factors"].reverse()
        self.bad_pair(cases=cases,reason="pair case/domain")

    def test_bad_allowed_marker(self):
        raw = bytearray(self.raw)
        struct.pack_into("<HB",raw,0,0,2)
        self.bad_pair(raw=raw,reason="allowed marker weight")

    def test_false_pair_weight(self):
        raw = bytearray(self.raw)
        message,weight = struct.unpack_from("<HB",raw,0)
        self.assertGreater(message,0)
        struct.pack_into("<HB",raw,0,message,weight+2)
        self.bad_pair(raw=raw,reason="pair witness weight")

    def test_zero_full_message(self):
        self.bad_full(dict(self.record,message=0),"nonzero message")

    def test_false_full_weight(self):
        self.bad_full(dict(self.record,d_or_upper=self.record["d_or_upper"]+2),"full witness weight")

    def test_wrong_full_assignment(self):
        self.bad_full(dict(self.record,scalars=self.record["scalars"]^1),"join assignment/order coverage")

    def test_missing_first_assignment(self):
        self.bad_full(dict(self.record,index=1),"join assignment/order coverage")

    def test_false_full_target(self):
        self.bad_full(dict(self.record,exact=1,minimum_words=1),"target stopping rule")

    def test_cap_cannot_be_complete(self):
        with self.assertRaisesRegex(ValueError,"completion"):
            replay.completion({"full_checked":2000000,"complete":True,"target_found":False},
                              2000000,True,False)

    def test_wrong_certificate_distance(self):
        obj = copy.deepcopy(self.control)
        obj["d"] += 2
        with self.assertRaisesRegex(ValueError,"exact distance"):
            replay.check_certificate(obj)

    def test_rank_defect(self):
        obj = copy.deepcopy(self.control)
        obj["rows"][1] = obj["rows"][0]
        with self.assertRaisesRegex(ValueError,"rank"):
            replay.check_certificate(obj)

    def test_source_pin(self):
        metadata = copy.deepcopy(self.metadata)
        metadata["source_sha256"][next(iter(metadata["source_sha256"]))] = "0"*64
        with tempfile.TemporaryDirectory(dir=PACKAGE) as folder:
            path = Path(folder)
            (path/"metadata.json").write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError,"source hash"):
                replay.replay(path)

    def test_seed_pin(self):
        metadata = copy.deepcopy(self.metadata)
        metadata["seed"] = "0"*32
        with tempfile.TemporaryDirectory(dir=PACKAGE) as folder:
            path = Path(folder)
            (path/"metadata.json").write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError,"seed"):
                replay.replay(path)

    def toy(self, root):
        triple = (67,87,91)
        others = [p for p in triple if p != root]
        adjacency = {(a,b):[0]*3969 for a in triple for b in triple if a != b}
        for a,b,x,y in [(root,others[0],0,1),(root,others[0],0,5),
                        (root,others[1],0,2),(root,others[1],0,3),(root,others[1],0,7),
                        (others[0],others[1],1,2),(others[0],others[1],1,8),
                        (others[0],others[1],5,3),(others[0],others[1],5,7)]:
            adjacency[a,b][x] |= 1 << y
            adjacency[b,a][y] |= 1 << x
        oracle = types.SimpleNamespace(roots={root:[1]})
        generated = list(replay.assignments(oracle,adjacency,triple))
        self.assertEqual(len(generated),3)
        self.assertEqual(replay.count_assignments(oracle,adjacency,triple),3)
        for actual_root,scalars in generated:
            self.assertEqual(actual_root,root)
            states = {p:(scalars[2*j]-1)*63+scalars[2*j+1]-1 for j,p in enumerate(triple)}
            self.assertEqual(states[root],0)
            self.assertIn((states[others[0]],states[others[1]]),[(1,2),(5,3),(5,7)])
        del adjacency[67,87]
        self.assertEqual(list(replay.assignments(oracle,adjacency,triple)),[])
        self.assertEqual(replay.count_assignments(oracle,adjacency,triple),0)

    def test_join_and_popcount(self):
        self.toy(67)

    def test_join_root_after_first_factor(self):
        self.toy(87)


if __name__ == "__main__":
    unittest.main()
