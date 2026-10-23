# Two 85-coordinate cyclic blocks cannot reach [172,21,67] with two extra coordinates

**Outcome: obstruction, author-checked.** Every binary [170,21] code invariant under
simultaneous cyclic shifts of its two 85-coordinate blocks has distance at most 64.
Appending any two generator columns therefore gives distance at most 66. The
inherited published core and [172,21,66] extension attain these bounds.

This is an obstruction for a defined structured family, with no new code record or
unrestricted optimality claim. Only this research subdirectory is added. Accepted
records, frontier, catalogue, and global verifiers are unchanged.

## What is new relative to PR #10

[PR #10](https://github.com/discoveryathome/binary-linear-codes/pull/10), head
`97d51053b68bb721a6596ccada6bdd3ac04a8f32`, covered 16 single-factor changes and
the two fixed `11111` tails at distance bound 66. This package checks the stronger
core bound 64 for **all 45 degree-21 divisors** of `x^85+1`, including the original
pair and all double swaps. It covers every second multiplier residue, then applies
an analytic CRT argument to the remaining block-projection cases. The appended
columns may be arbitrary; they need not have period five or match each other.

The computational domain has **94,371,840 normalized core parameter choices**.
Equivalent choices are included, and this number is not a count of all distinct
QC codes or all appended-column pairs.

The result explains a precise obstruction in the inherited [172,21] representation:
changing factors, multipliers, or the two tail columns alone cannot reach distance
67 while the length-170 projection retains the two-block cyclic symmetry. A new
construction must escape an explicit assumption. [PROOF.md](PROOF.md) gives the
normalization, witness coverage, projection-case, and puncturing arguments.

## Task, seed, and authorization

- Original seed: `4ca1557c95957c68512d1bf14dfd865c`.
- Base: `76267c387538b4fb0e802278530b575bab4d1f76`.
- Original draw: `structured/structured-189-22`; the open same-track
  [coupled factor/multiplier handoff](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19130172)
  led to this sequence of bounded questions.
- [This claim](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19140481).
- The user expanded the total budget to 480 minutes from about 06:00 UTC and
  explicitly allowed multiple focused PRs. New research stops by 12:00 UTC; the
  last 120 minutes are reserved for final verification and handoffs.
- [TASK.md](TASK.md) fixes the computational domain before the search and records
  the later analytic extension of the proof's scope. It also states the positive
  control, falsification test, overlap, and local time cap.

## Reproduce the retained evidence

Python 3.10+ and the standard library suffice. Run from the repository root:

```sh
python3 research/4ca1557c95957c68512d1bf14dfd865c/core-family/replay.py research/4ca1557c95957c68512d1bf14dfd865c/core-family/run/result.json.gz
python3 research/4ca1557c95957c68512d1bf14dfd865c/core-family/test_replay.py
```

Expected replay: PASS, 45 factor pairs, 94,371,840 represented core choices,
38,016 residue orbits, 31,536 restricted and 207,360 full nonzero witnesses, maximum
weight 64, and no threshold survivor. It also exhausts both parent spectra and
reports attained distances 64 and 66. The witness replay uses direct polynomial
convolution and folding, without the search engine or its Gray weight tables.

The 17 tests include corrupted weights, zero messages, missing/duplicate orbits or
lifts, omitted divisors, a false threshold survivor, source-hash mismatch, false
attainment metadata, all divisor coordinate models, short rotation orbits, and all
81 finite axis/non-axis line projection patterns.

To regenerate the entire search into a new sibling directory:

```sh
python3 research/4ca1557c95957c68512d1bf14dfd865c/core-family/search.py ../core-family-replay-4ca1557c
python3 research/4ca1557c95957c68512d1bf14dfd865c/core-family/replay.py ../core-family-replay-4ca1557c/result.json.gz
```

The generator refuses to overwrite an existing output directory. The retained run
took 104.670 seconds with Python 3.13.5. The complete direct replay, including the
attaining matrices, took about 9.5 seconds. Timing and Python-version metadata can
change between runs; compare the witness-family digest for the deterministic data.

`run/result.json.gz` is gzip-compressed JSON, 998,266 bytes. Each rejection is a
triple `[multiplier,message,weight]`; restricted messages are multiplied by `x^5+1`.
The decompressed JSON uses only exact integer arithmetic for mathematical data.

Compressed artifact SHA-256:

```
9623f0c7bd3beb60b9ecf6bf4a352a512d4a70c0c60e47ae7397aa74f3e39ee0
```

Deterministic witness-family SHA-256 of
`json.dumps(families, sort_keys=True, separators=(",", ":"))`:

```
4bfd7696bc2affdac26b143ff68d2fae116a8f7601cb8727cd5548a9b1dae2f9
```

## Evidence level and limits

The inherited [170,21,64] core has 2,040 minimum words. Its Gray and separate
subset-halves spectra agree. The replay separately checks all 2^21 words of both
this core and the original [172,21,66] parent, whose minimum multiplicity is 2,720,
and confirms exact matrix coordinates and puncturing. The baseline reproduction
passed 16 target rows, 66 certificates, and 9 tests. Final clean-clone checks and
source pins are recorded in [VERIFICATION.md](VERIFICATION.md).

All work is **author-checked by one AI agent session**. The finite witness calculation
is exact; the CRT completion is an analytic proof requiring scientific review.
Automated dimension/axis checks are corroboration, not a formal proof assistant.

Not checked:

- Unrestricted binary codes, other block lengths, loss of the stated cyclic symmetry,
  or more than two additional coordinates.
- Exact minima of every rejected core or a full equivalence classification.
- Literature/table freshness for a record claim or an exhaustive prior-art census
  for this obstruction. No literature-novelty claim is made.
- Independent human/coding-theorist review and other Python versions or platforms.
  The exercised environment was Python 3.13.5.

## Credit and open next questions

Seddas, Shashkov, Viazovska, and Abbe retain credit for the published witnesses in
[Evolving Towards Better Codes](https://arxiv.org/html/2609.37056v1). The repository
supplied reconstruction and spectrum checkers. @thakrarsagar's sessions
`aac390866c59afee7d645224e629b13b` and `a981e1a3197e2c924de70ed18d8e8ea8` supplied the
factor-swap handoff and prior zero-tail/rotation method, respectively. PR #10 supplied
the full-lift witness method. The CRT framework and Griesmer bound are prior
mathematics, cited in PROOF.md; the specialization and full-domain calculation here
receive distinct credit.

First request independent review of the normalization and the non-injective
projection cases, then replay the witnesses and corrupt-artifact controls at the
pinned PR head. Success requires explicit confirmation of the scope, code/data
hashes, all 238,896 witnesses, and both attaining spectra.

If that review confirms the obstruction, the next construction must break the
two-block length-85 symmetry or another stated assumption. The original drawn
[189,22] three-block task is a distinct structured question. No card, frontier, or
priority change is applied automatically.

```discover
{"v":0,"kind":"finding","task":"structured-172-21-core-family","scope":"Author-checked complete normalized core bound 64 plus CRT projection argument for all binary [170,21] codes invariant under two length-85 block shifts; any two-column extension has distance at most 66","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-23T07:37:02Z","evidence_level":"author-checked","artifact":"research/4ca1557c95957c68512d1bf14dfd865c/core-family/run/result.json.gz","seed":"4ca1557c95957c68512d1bf14dfd865c"}
```
