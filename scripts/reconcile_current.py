"""Reconcile fresh table bounds with historical exclusions without altering the old suite."""
import hashlib,json,re
from pathlib import Path
import closure
from upper_bounds import audit
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'research/readiness-20261021'
def main():
 snapshot=OUT/'table2-current.html';s=snapshot.read_text();current={}
 for n,k,ds in re.findall(r'HREF="BKLC.php\?q=2&n=(\d+)&k=(\d+)">([\d-]+)</A>',s):
  d=list(map(int,ds.split('-')));current[int(n),int(k)]=(d[0],d[-1])
 old=closure.table()
 if set(current)!=set(old):raise ValueError('incomplete or changed source layout')
 # Never discard an old applicable lower bound if a newer table page regresses.
 merged={p:(max(old[p][0],current[p][0]),min(old[p][1],current[p][1])) for p in old}
 historical=json.loads((ROOT/'results/closure.json').read_text())
 seeds=[(n,k,lo,f'old/current codetables {n},{k}') for (n,k),(lo,_) in merged.items()]
 seeds += [(*r,'historical recent-paper exclusion') for r in historical['recent_triples']+historical['lincode2026_parents']]
 lower,trace,_=closure.close(seeds);upper,utrace=audit(merged)
 conflicts=[(n,k,lower[n,k],upper[n,k]) for n,k in merged if lower[n,k]>upper[n,k]]
 if conflicts:raise ValueError(('conflicting bounds',conflicts))
 parents=json.loads((OUT/'structured.json').read_text())['parents'];rows=[]
 for p in parents:
  nk=p['n'],p['k'];rows.append(dict(n=nk[0],k=nk[1],verified_d=p['d'],exclusion_lower=lower[nk],upper=upper[nk],
       improvement_threshold=lower[nk]+1,lower_derivation=trace[nk],upper_derivation=utrace[nk],
       open_within_sources=lower[nk]<upper[nk],status='source-scoped bound audit; coding-theorist and full literature review pending'))
 result=dict(retrieved_on='2026-10-21',source='https://www.codetables.de/BKLC/Tables.php?q=2&n0=1&n1=256&k0=1&k1=256',
  sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(),cells=len(current),changed_cells=sum(current[x]!=old[x] for x in old),parents=rows,
  scope='Fresh full-table plus retained historical paper exclusions and nonexistence corrections; not an exhaustive current-literature census.')
 (OUT/'current-bounds.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='parents'}))
if __name__=='__main__':main()
