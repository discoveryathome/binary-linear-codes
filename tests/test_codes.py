import sys,json,tempfile,unittest,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import codes,independent

def words(rows):
    s={0}
    for r in rows:s|={x^r for x in list(s)}
    return s

def delete(x,n,pos):
    return sum(((x>>j)&1)<<i for i,j in enumerate(j for j in range(n) if j not in pos))

class Tests(unittest.TestCase):
    def test_transformations_against_sets(self):
        rng=random.Random(871)
        for _ in range(100):
            n=rng.randrange(3,10);r=codes.basis([rng.randrange(1<<n) for _ in range(rng.randrange(1,n))]);s=words(r)
            pos=set(rng.sample(range(n),rng.randrange(n)))
            p,m=codes.puncture(r,n,pos);self.assertEqual(words(p),{delete(x,n,pos) for x in s})
            p,m=codes.shorten(r,n,pos);self.assertEqual(words(p),{delete(x,n,pos) for x in s if all(not (x>>j)&1 for j in pos)})
            p,m=codes.extend(r,n);self.assertEqual(words(p),{x|((x.bit_count()%2)<<n) for x in s})
            order=rng.sample(range(n),n);p,m=codes.permute(r,n,order)
            self.assertEqual(sorted(x.bit_count() for x in words(p)),sorted(x.bit_count() for x in s))
            if len(r)>1:self.assertTrue(words(codes.subcode(r,[1,3]))<=s)
    def test_checkers_and_rejections(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'results') as tmp:
            p=Path(tmp)/'code.json';r,n=codes.bch(3,3)
            c=codes.write_cert(p,r,n,{'source':'Hamming BCH(7,3)'})
            self.assertEqual((len(r),c['d']),(4,3))
            self.assertEqual(codes.check(p)['spectrum'],independent.check(p)['spectrum'])
            bad=[]
            for key,val in [('provenance',None),('d',4),('d',2),('n',8),('k',True),('q',3),('rows',c['rows'][:-1]),('rows',[c['rows'][0]]*4),('rows',['2'*7]*4)]:
                bad.append({**c,key:val})
            for b in bad:
                p.write_text(json.dumps(b))
                for check in (codes.check,independent.check):
                    with self.assertRaises(ValueError):check(p)
    def test_rank_and_enumeration(self):
        rng=random.Random(19)
        for _ in range(100):
            r=[rng.randrange(64) for _ in range(4)]
            self.assertEqual(1<<len(codes.basis(r)),len(words(r)))
            h=codes.spectrum(r,6); brute=[0]*7
            for m in range(16):
                x=0
                for i in range(4):
                    if m>>i&1:x^=r[i]
                brute[x.bit_count()]+=1
            self.assertEqual(h,brute)
    def test_closure(self):
        from closure import close,implications
        seeds=[(7,4,3,'hamming')];b,_,_=close(seeds,10)
        self.assertEqual(b[8,4],4);self.assertGreaterEqual(b[7,3],4)
        b2,_,_=close([(n,k,d,'rerun') for (n,k),d in b.items()],10)
        self.assertEqual(b,b2)
        for (n,k),d in b.items():
            for nn,kk,dd,_ in implications(n,k,d,10):
                if 1<=kk<=nn<=10:self.assertGreaterEqual(b[nn,kk],dd)
if __name__=='__main__':unittest.main()
