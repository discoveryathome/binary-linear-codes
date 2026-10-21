import copy,json,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import codes,large_verify,independent
class LargeCheckerTests(unittest.TestCase):
 def test_original_witnesses_agree(self):
  for p in Path('certificates').glob('baseline_*.json'):
   self.assertEqual(large_verify.check(p)['spectrum'],independent.check(p)['spectrum'])
 def test_reject_mutations(self):
  c=json.loads(Path('research/readiness-20261021/certificates/189_22_72.json').read_text())
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'candidate.json'
   for kind in ('distance','rank','binary','budget'):
    x=copy.deepcopy(c)
    if kind=='distance':x['d']+=1
    elif kind=='rank':x['rows'][0]=x['rows'][1]
    elif kind=='binary':x['rows'][0]='2'+x['rows'][0][1:]
    else:x['k']=23
    p.write_text(json.dumps(x))
    with self.assertRaises(ValueError):large_verify.check(p)
if __name__=='__main__':unittest.main()
