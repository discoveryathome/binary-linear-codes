"""Exploratory secondary metric, explicitly outside the minimum-distance
record question. Exact undetected-error probability for a binary symmetric
channel and code-membership error detection, NOT decoder block-error rate."""
import fractions,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import codes
def run():
    manifest=json.loads((HERE/'paired/manifest.json').read_text())
    best=min((r for r in manifest['rows'] if r['n']==45 and r['start']=='warm' and r['method']=='walsh'),
             key=lambda r:r['minimum_words'])
    paths=[ROOT/'certificates/baseline_45_11.json',ROOT/best['object']]
    result=dict(scope='Exploratory secondary metric; no new distance record or best-known spectrum claim.',
        interpretation='A transmitted codeword suffers independent bit flips with probability p. The receiver only tests code membership; a nonzero error equal to a codeword goes undetected. This is not an error-correcting decoder comparison.',
        formula='sum_{w=1}^n A_w p^w (1-p)^(n-w)',rows=[])
    for path in paths:
        c,r=codes.read_cert(path);hist=codes.spectrum(r,c['n']);metrics=[]
        for a,b in [(1,20),(1,10),(3,20)]:
            probability=fractions.Fraction(sum(hist[w]*a**w*(b-a)**(c['n']-w) for w in range(1,c['n']+1)),b**c['n'])
            metrics.append(dict(p=f'{a}/{b}',numerator=probability.numerator,denominator=probability.denominator,approximation=float(probability)))
        result['rows'].append(dict(object=str(path.relative_to(ROOT)),d=c['d'],minimum_words=hist[c['d']],metrics=metrics))
    (HERE/'channel_metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Exact secondary undetected-error probabilities written; no decoder-performance or novelty claim.')
if __name__=='__main__':run()
