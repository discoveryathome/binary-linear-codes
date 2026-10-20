# Measured assessment

The pilot is technically suitable for short, checkable contributions, but this experiment provides **no evidence of easy fresh-record discovery** in the selected small-dimension cases. Verification and literature repair are immediately useful. A public discovery-focused launch should wait for a consenting maintainer and an independent replay.

## Measurements

- Final targets: 16, n=41–62, k=10–12; 1,024–4,096 codewords per exhaustive check.
- Source table: 32,896 cells. Guaranteed transformation closure plus recent reported parents excludes improvements at 95 cells above the frozen table's lower bounds. These are prior-art implications, **zero pilot records**.
- Upper-bound audit: 20 table cells tightened through cited results and propagation. Six initial small-k targets were removed as settled. These are published proofs, not new proofs by the pilot.
- Final research budget: 48,000 local proposals = 16 cases × 3 restarts × 1,000 proposals, plus 587 concrete transformations matching final targets. Each case uses two published warm starts and one random systematic cold start.
- Seed: `b17a20261020c0de0000000000000001`. Elapsed time: 101.44 seconds on Python 3.14.6, macOS-26.6.2-arm64-arm-64bit-Mach-O.
- New distances above the exclusion baseline: 0/16. Structured improvements: 0. Pure coordinate permutations are negative controls and never discoveries.
- Cold starts matching the baseline: 0/16. Median remaining distance deficit: 2; range 1–3. Warm starts preserved the lower bound but did not improve it.
- Extension feasibility: eight fixed generators admit a one-column increase; eight have explicit GF(2) inconsistency witnesses. Neither result proves unrestricted optimality.
- Experimental information-set certification: [32,16,8] used 1,392 visits; [64,16,24] used 27,536, versus 65,536 messages each for full enumeration. Both agree with both exhaustive implementations. Duplicate visits are counted; this is not a speedup claim.

## Interpretation and limits

The scientific bottleneck here is obtaining a new construction, not checking a submitted small-k matrix. Known parents are valuable starting material, but inherited and equivalent codes inflate apparent progress unless explicitly excluded. A better secondary weight-spectrum objective is useful for search, but fewer minimum-weight words do not improve the primary distance record.

These are correlated cases, one fixed seed stream, modest search budgets and one simple heuristic. No statistical success-rate estimate or impossibility claim is justified. Many warm starts are related by transformations, so 32 warm runs are not 32 independent scientific trials. This was one agent session, not a study of multiple new contributors. A clean local clone tests reproducibility, not reviewer independence.

Other compute-heavy work was visible on the host during the session. Wall times are descriptive and may vary substantially; the fixed evaluation budget and exact output hashes are the reproducible comparison. The preliminary 95.97-second run on superseded targets is archived under `results/preaudit/` and excluded from these final denominators.

The [September 2026 LinCodeEvolve paper](https://arxiv.org/html/2609.37056v1) supplies a reason to explore structured larger-k regimes. Its reported parent records and their cheap descendants are already excluded here. Reproducing one is useful verification, not a new discovery. Its reported resource budget is materially larger than this laptop pilot.

## Donor potential and next decision

Recommended near-term work: independent replay; upper-bound freshness audits; portable reconstruction of Goppa/B2 recipes; structured subspace and coupled-column search; certification hardening. Six draft cards include real positive controls. Rebalance toward discovery only after independently checked experiments show improved distances or a clearly justified new search family.

A practical next assessment is ten independently reviewed sessions, each with a fixed target, seed and budget. Measure accepted useful artifacts per session, new parent constructions versus derived entries, reviewer minutes, verification seconds and duplicated work. Do not assume donation volume compensates for low novelty yield. Current review capacity is zero because no maintainer has agreed.

## Verification cost

Three repeats per final witness gave a maximum median combined cost of 0.0626 seconds for the two exhaustive checks. Full measurements are in `results/verification-benchmark.json`; shared-host timing caveats apply. See `results/clean-checkout.json` for the clean-checkout reproduction measurement.

## Later contributor trial

See the [timed featured-pilot assessment](../research/c0202026102018570000000000000001/README.md)
for a longer contributor session, additional search methods, and corrected donor
directions. The original short pilot measurements above are retained unchanged.
