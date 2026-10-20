import unittest,random,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import codes
from information_sets import certified
from extension_obstruction import analyze,verify_obstruction
from upper_bounds import griesmer
class CertificationTests(unittest.TestCase):
    def test_certified_vs_exhaustive(self):
        rng=random.Random(13)
        for _ in range(40):
            k=rng.randrange(2,7);n=rng.randrange(k,20)
            rows=[(1<<i)|(rng.getrandbits(n-k)<<k) for i in range(k)]
            self.assertEqual(certified(rows,n)['d'],codes.distance(rows,n))
            p=analyze(rows,n)
            if p['status'].startswith('impossible'):self.assertTrue(verify_obstruction(rows,n,p['messages']))
            else:
                rr,nn=codes.extend(rows,n,p['column']);self.assertEqual(codes.distance(rr,nn),p['d']+1)
    def test_bad_sets(self):
        with self.assertRaises(ValueError):certified([1,2],4,[[0,1],[1,2]])
        with self.assertRaises(ValueError):certified([1,2],4,[[2,3]])
        with self.assertRaises(ValueError):certified([1,2],4,[[0,99]])
    def test_griesmer(self):
        self.assertEqual(griesmer(7,3),4)
        self.assertEqual(griesmer(8,4),4)
        self.assertEqual(griesmer(41,12),16)
