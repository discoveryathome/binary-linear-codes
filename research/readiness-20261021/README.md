# Binary linear error-correcting codes: second-cohort preparation

Local preparation authorized by the project coordinator on 2026-10-21. Evidence is
**author-checked**; outside scientific review and public intake approval are pending.
No external contact, hub submission, or new reviewer consent is implied.

## Prepared work

Six published structured parents at k=20..22 are reconstructed and checked by Gray enumeration and a separate subset-halves checker. The 20,854 local two-column obstructions are replayed. The complete current table is retrieved and reconciled with retained paper exclusions and upper-bound corrections. A bounded QC multiplier search changes the core rather than repeating blocked fixed-tail moves.

The machine-readable portfolio is [`structured.json`](structured.json).
Historical experiments retain their original exposure and evidence labels. These
preparation cases are now exposed development material, not a sealed test set.

## First contributor step

Activate the repository's documented Python environment, then run from its root:

```sh
python3 scripts/large_verify.py research/readiness-20261021/certificates/189_22_72.json
```

Minimum distance remains primary. The k<=22 checker is a separate bounded entry point; the original k<=20 verifier stays unchanged. All six starting parents are published replications. A new hash or smaller minimum-word multiplicity is not a distance record. Derived constructions and bounded obstruction proofs receive distinct credit.

Before searching, read the portfolio and select one bounded task. Preserve the
starting witness, source hashes, seed and budget. Reserve time to verify the final
artifact. Record unsuccessful runs. A useful handoff can be a replication, a
reproducible defect, a bounded negative finding, or an improvement under the same
formulation; identify which one it is. Passing a local check does not imply novelty
or independent acceptance.

## Outside review

[REVIEW.md](REVIEW.md) contains concrete questions; [review.json](review.json) is an
unfilled review receipt. Review must identify a commit and exact artifact hashes.
The person reproducing a result should disclose any involvement in its creation.

## Independent contributor trial protocol

Choose a task using the refreshed catalogue and give a new contributor only the
published instructions. Record setup time, time to first valid artifact, total
compute, failed attempts and reviewer minutes. Start from the inherited frontier.
Freeze algorithm submissions before evaluating on a separately prepared unseen
case pool. Author-run smoke checks here do not count as independent trials.

Remaining gates:

- Coding-theorist target review.
- Independent record/novelty reconciliation before a record claim.
- Fresh independent contributor trials.

## Current evidence and next search

All 32,896 table cells were retrieved on 2026-10-21; none changed relative to the
original snapshot. Closure retains recent reported parent constructions even when
a generator is unavailable. See `current-bounds.json` for target-specific thresholds.
This is source-scoped reconciliation, not proof of exhaustive literature coverage.

The six 16-proposal multiplier-search controls found **zero distance improvements**.
Every proposal and final spectrum is retained under `search-*`. These controls make
the donor workflow executable; they do not establish productive target headroom.
Coding-theorist selection and independent donor trials remain material launch gates.
The [source paper](https://arxiv.org/html/2609.37056v1) retains all construction credit.

## Setup audit

All ten catalogue first steps pass with the documented Python 3.10+ requirement
(Python 3.14.6 used here). The first coordinator audit accidentally selected macOS
system Python 3.9 and failed on `int.bit_count`; those are unsupported-environment
setup failures, not failed code certificates. The corrected audit is in
`first-steps.json`. Search outcomes remain all 96 recorded null results.
