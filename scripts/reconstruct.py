"""Reconstruct a deliberately limited, fail-closed subset of published recipes."""
import re,json,hashlib
from pathlib import Path
import codes,independent

def polynomial(s):
    terms=s.strip().split(' + ');g=0
    for term in terms:
        if term=='1':e=0
        elif term=='x':e=1
        elif re.fullmatch(r'x\^\d+',term):e=int(term[2:])
        else:raise ValueError('unsupported polynomial '+term)
        g^=1<<e
    return g

EXTRACTED=Path('data/extracted/codetables-recipes.json')

def page_steps(path):
    """Parse a codetables.de recipe page into its recipe steps (index, parameters, recipe line).
    Used once by scripts/extract_sources.py; the checks read data/extracted/ instead."""
    text=re.findall(r'<PRE>(.*?)</PRE>',Path(path).read_text(),re.S)[0]
    entries=re.split(r'\[(\d+)\]:\s*\[(\d+),\s*(\d+),\s*(\d+)\][^\n]*\n',text)
    return [dict(zip(('index','n','k','d'),map(int,entries[i:i+4])),recipe=entries[i+4].split('last modified:')[0].strip()) for i in range(1,len(entries),5)]

def extracted():
    return json.loads(EXTRACTED.read_text())['recipes']

def steps_for(snapshot,sha256):
    """Recipe steps for a certificate's provenance, matched by snapshot path and page hash."""
    for rec in extracted().values():
        if rec['source']['path']==str(snapshot):
            if rec['source']['sha256']!=sha256:raise ValueError('extracted recipe hash '+str(snapshot))
            return rec['steps']
    raise ValueError('no extracted recipe for '+str(snapshot))

def recipe(published):
    made={};steps=[]
    for e in published:
        idx,n,k,d,s=e['index'],e['n'],e['k'],e['d'],e['recipe']
        if 'stored generator matrix' in s:
            strings=[''.join(re.findall('[01]',r)) for r in re.findall(r'^\[ ([01, ]+) \]',s,re.M)]
            if len(strings)!=k or any(len(x)!=n for x in strings):raise ValueError('stored matrix shape')
            r=[int(x[::-1],2) for x in strings]
        elif s.startswith('CyclicCode'):
            g=polynomial(s.split('generating polynomial ')[1]);r=[g<<j for j in range(k)]
        elif s.startswith('QuasiCyclicCode'):
            if '(in octal)' in s:
                polys=[int(v.strip(),8) for v in re.search(r'\[([^]]+)\]',s).group(1).split(',')]
            else:polys=[polynomial(v) for v in s.split('generating polynomials: ')[1].split(',')]
            ell=len(polys);m=n//ell;mask=(1<<m)-1
            # Interleave coordinates by constituent polynomial, as in Magma.
            r=[]
            for j in range(m):
                rotated=[((g<<j)|(g>>(m-j)))&mask for g in polys]
                r.append(sum(((g>>t)&1)<<(ell*t+a) for a,g in enumerate(rotated) for t in range(m)))
            r=codes.basis(r)
        elif s.startswith(('BCHCode','Extended BCHCode')):
            vals=list(map(int,re.search(r'parameters (\d+) (\d+)(?: (\d+))?',s).groups(default='1')))
            length,delta,b=vals;r,nn=codes.bch((length+1).bit_length()-1,delta,b)
            if s.startswith('Extended'):r,nn=codes.extend(r,nn)
            if nn!=n:raise ValueError('BCH length')
        elif s.startswith(('Puncturing','Shortening')):
            parent=int(re.search(r'of \[(\d+)\]',s).group(1));r,nn=made[parent]
            tail=s.split(' at ')[1].strip().strip('{} ')
            if '..' in tail:
                a,z=map(int,tail.split('..'));pos=list(range(a-1,z))
            else:pos=[int(t.strip())-1 for t in tail.split(',')]
            r,nn=(codes.puncture if s.startswith('Puncturing') else codes.shorten)(r,nn,pos)
            if nn!=n:raise ValueError('transform length')
        elif s.startswith('ExtendCode'):
            parent=int(re.search(r'\[(\d+)\]',s).group(1));r,nn=codes.extend(*made[parent])
            if nn!=n:raise ValueError('extension length')
        elif s.startswith('Subcode of'):
            parent=int(re.search(r'\[(\d+)\]',s).group(1));r,nn=made[parent]
            r=codes.subcode(r,[1<<j for j in range(k)])
        else:raise ValueError('unsupported: '+s[:150])
        if len(codes.basis(r))!=k:raise ValueError(f'step {idx} rank {len(codes.basis(r))}!={k}')
        if k>20:raise ValueError('verification budget')
        actual=codes.distance(r,n)
        if actual<d:raise ValueError(f'step {idx} distance {actual}<{d}; coordinate convention requires audit')
        made[idx]=(r,n);steps.append(dict(index=idx,n=n,k=k,published_d=d,verified_d=actual,recipe=s))
    if not made:raise ValueError('no supported steps')
    return made[max(made)],steps

def run():
    closure=json.loads(Path('results/closure.json').read_text());b={(r['n'],r['k']):r for r in closure['rows']}
    eligible=[];audit=[]
    for key,rec in sorted(extracted().items(),key=lambda x:tuple(map(int,x[0].split('_')))):
        n,k=map(int,key.split('_'));row=b[n,k];path=rec['source']
        try:
            (r,nn),steps=recipe(rec['steps'])
            if nn!=n or len(r)!=k:raise ValueError('final parameters')
            if codes.distance(r,n)<row['table_lower']:raise ValueError('lower bound not reached')
            if row['exclusion_lower']>=row['audited_upper']:raise ValueError('closed by exclusions')
            eligible.append((n,k,r,steps,path));audit.append(dict(n=n,k=k,status='reconstructed'))
        except ValueError as e:audit.append(dict(n=n,k=k,status='deferred',reason=str(e)))
    # Deterministic selection AFTER full parameter closure and recipe verification.
    chosen=eligible[:16];out=[]
    for n,k,r,steps,source in chosen:
        row=b[n,k];url=f'https://www.codetables.de/BKLC/BKLC.php?q=2&n={n}&k={k}'
        name=f'certificates/baseline_{n}_{k}.json'
        c=codes.write_cert(name,r,n,dict(kind='published-reconstruction',url=url,snapshot=source['path'],snapshot_sha256=source['sha256'],steps=steps,credit='Published construction, not a pilot discovery. Named authors retained in recipe text.'))
        y=independent.check(name)
        if y['d']!=c['d']:raise ValueError('independent failure')
        out.append(dict(n=n,k=k,published_lower=row['table_lower'],closure_lower=row['exclusion_lower'],table_upper=row['table_upper'],upper=row['audited_upper'],upper_derivation=row['upper_derivation'],verified_d=c['d'],object=name,source=url,by='Published construction via Grassl code tables',updated='2026-10-20',status='open; construction verified; upper bound literature-reported',codewords=2**k,improvement_goal=row['exclusion_lower']+1))
    if len(out)!=16:raise ValueError(f'Only {len(out)} viable targets')
    Path('data/targets.json').write_text(json.dumps(out,indent=2)+'\n')
    Path('results/reconstruction-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(dict(reconstructed=len(eligible),deferred=len(audit)-len(eligible),targets=[[x['n'],x['k'],x['verified_d'],x['upper']] for x in out])))
if __name__=='__main__':run()
