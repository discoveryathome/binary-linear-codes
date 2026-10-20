"""Regenerate the human record table and measured assessment from saved artifacts."""
import csv,json,statistics,hashlib,re
from pathlib import Path

def main():
    targets=json.loads(Path('data/targets.json').read_text());ex=json.loads(Path('results/experiment/experiment.json').read_text());closure=json.loads(Path('results/closure.json').read_text());info=json.loads(Path('results/information-sets.json').read_text())
    results={(r['n'],r['k']):r for r in ex['rows']}
    fields=['n','k','published_lower','closure_lower','verified_d','upper','experiment_best','goal','object','by','source','updated','evidence','upper_status']
    rows=[]
    for t in targets:
        c=json.loads(Path(t['object']).read_text());m=re.search(r'Code found by ([^\n]+)',json.dumps(c).replace('\\n','\n'));by=m.group(1) if m else 'Published construction; Grassl code table provenance'
        row={k:t[k] for k in ['n','k','published_lower','closure_lower','verified_d','upper','object','source','updated']}
        row.update(by=by,experiment_best=results[t['n'],t['k']]['best_d'],goal=t['improvement_goal'],evidence='two exhaustive implementations; author-checked',upper_status='literature-reported; not locally proved');rows.append(row)
    with Path('data/records.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    text='# Record table — 2026-10-20\n\nLower-bound witnesses are exact constructions; upper bounds are separate literature claims. None of these rows is proved optimal by this pilot. “Closure” is the minimum novelty exclusion threshold, not a pilot discovery.\n\n| n | k | Published lower | Closure | Verified d | Upper | Search best | Codewords/check | Witness |\n|---:|---:|---:|---:|---:|---:|---:|---:|---|\n'
    for r in rows:text+=f"| {r['n']} | {r['k']} | [{r['published_lower']}]({r['source']}) | {r['closure_lower']} | {r['verified_d']} | {r['upper']} | {r['experiment_best']} | {2**r['k']} | [matrix](../{r['object']}) |\n"
    text+='\nExact upper-bound derivations and source pages are retained in `data/targets.json` and `results/closure.json`. Selection: lexicographically first 16 locally reconstructible open pairs among archived n<=70, 9<=k<=12 candidates, **after** complete table/recent-parent closure and literature upper corrections. This favors cheap certification and available parent matrices; it is not a ranking by estimated probability of discovery.\n'
    Path('docs/record-table.md').write_text(text)
    cold=[r['runs'][2]['final_d'] for r in ex['rows']];gaps=[r['closure_lower']-r['runs'][2]['final_d'] for r in ex['rows']]
    report=f'''# Measured assessment

The pilot is technically suitable for short, checkable contributions, but this experiment provides **no evidence of easy fresh-record discovery** in the selected small-dimension cases. Verification and literature repair are immediately useful. A public discovery-focused launch should wait for a consenting maintainer and an independent replay.

## Measurements

- Final targets: {len(targets)}, n=41–62, k=10–12; 1,024–4,096 codewords per exhaustive check.
- Source table: 32,896 cells. Guaranteed transformation closure plus recent reported parents excludes improvements at {closure['improved_over_table']} cells above the frozen table's lower bounds. These are prior-art implications, **zero pilot records**.
- Upper-bound audit: {closure['upper_improvements']} table cells tightened through cited results and propagation. Six initial small-k targets were removed as settled. These are published proofs, not new proofs by the pilot.
- Final research budget: {ex['local_proposals']:,} local proposals = 16 cases × 3 restarts × 1,000 proposals, plus {ex['structured_candidates']} concrete transformations matching final targets. Each case uses two published warm starts and one random systematic cold start.
- Seed: `{ex['seed']}`. Elapsed time: {ex['seconds']:.2f} seconds on Python {ex['environment']['python']}, {ex['environment']['platform']}.
- New distances above the exclusion baseline: {ex['candidate_records']}/16. Structured improvements: {len(ex['structured_improvements'])}. Pure coordinate permutations are negative controls and never discoveries.
- Cold starts matching the baseline: {sum(g==0 for g in gaps)}/16. Median remaining distance deficit: {statistics.median(gaps):g}; range {min(gaps)}–{max(gaps)}. Warm starts preserved the lower bound but did not improve it.
- Extension feasibility: eight fixed generators admit a one-column increase; eight have explicit GF(2) inconsistency witnesses. Neither result proves unrestricted optimality.
- Experimental information-set certification: [32,16,8] used {info[0]['enumerated']:,} visits; [64,16,24] used {info[1]['enumerated']:,}, versus 65,536 messages each for full enumeration. Both agree with both exhaustive implementations. Duplicate visits are counted; this is not a speedup claim.

## Interpretation and limits

The scientific bottleneck here is obtaining a new construction, not checking a submitted small-k matrix. Known parents are valuable starting material, but inherited and equivalent codes inflate apparent progress unless explicitly excluded. A better secondary weight-spectrum objective is useful for search, but fewer minimum-weight words do not improve the primary distance record.

These are correlated cases, one fixed seed stream, modest search budgets and one simple heuristic. No statistical success-rate estimate or impossibility claim is justified. Many warm starts are related by transformations, so 32 warm runs are not 32 independent scientific trials. This was one agent session, not a study of multiple new contributors. A clean local clone tests reproducibility, not reviewer independence.

Other compute-heavy work was visible on the host during the session. Wall times are descriptive and may vary substantially; the fixed evaluation budget and exact output hashes are the reproducible comparison. The preliminary 95.97-second run on superseded targets is archived under `results/preaudit/` and excluded from these final denominators.

The [September 2026 LinCodeEvolve paper](https://arxiv.org/html/2609.37056v1) supplies a reason to explore structured larger-k regimes. Its reported parent records and their cheap descendants are already excluded here. Reproducing one is useful verification, not a new discovery. Its reported resource budget is materially larger than this laptop pilot.

## Donor potential and next decision

Recommended near-term work: independent replay; upper-bound freshness audits; portable reconstruction of Goppa/B2 recipes; structured subspace and coupled-column search; certification hardening. Six draft cards include real positive controls. Rebalance toward discovery only after independently checked experiments show improved distances or a clearly justified new search family.

A practical next assessment is ten independently reviewed sessions, each with a fixed target, seed and budget. Measure accepted useful artifacts per session, new parent constructions versus derived entries, reviewer minutes, verification seconds and duplicated work. Do not assume donation volume compensates for low novelty yield. Current review capacity is zero because no maintainer has agreed.
'''
    benchmark=Path('results/verification-benchmark.json')
    if benchmark.exists():
        values=json.loads(benchmark.read_text())['rows']
        maximum=max(x['gray_seconds_median']+x['column_seconds_median'] for x in values)
        report+=f'\n## Verification cost\n\nThree repeats per final witness gave a maximum median combined cost of {maximum:.4f} seconds for the two exhaustive checks. Full measurements are in `results/verification-benchmark.json`; shared-host timing caveats apply. See `results/clean-checkout.json` for the clean-checkout reproduction measurement.\n'
    Path('docs/assessment.md').write_text(report)
    f=Path('discover/frontier.json');front=json.loads(f.read_text());front['artifacts']=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in map(Path,['data/records.csv','data/targets.json','results/closure.json','results/experiment/experiment.json'])];f.write_text(json.dumps(front,indent=2)+'\n')
    print('PASS record table and assessment generated')
if __name__=='__main__':main()
