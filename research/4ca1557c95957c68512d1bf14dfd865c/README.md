# An obstruction for 16 coupled [172,21] factor swaps

**Outcome: obstruction, author-checked.** Every code in the fixed family below has
distance at most 66. No distance-67 survivor remains among **33,554,432 parameter
choices**. This package supplies a conditional finite-family proof, 55,800 explicit
nonzero rejection witnesses, a separate replay, and representative matrix controls.

It changes only this donor package. Frontier, accepted records, global verifiers,
catalogue priorities, and the review ledger are unchanged.

## Question and exact scope

Can a factor-polynomial change coupled with an arbitrary second QC multiplier
improve the inherited [172,21,66] construction to distance at least 67?

Keep both 85-coordinate blocks, the identity first multiplier, the degree-one and
degree-four factors, and both constant `11111` tails. Replace exactly one of the
inherited degree-eight factors `0x17b` and `0x1a3` by any other degree-eight factor
of `x^85+1`. This gives 16 factor pairs. Exhaust every second multiplier modulo the
resulting degree-21 check polynomial, all `2^21` residues per pair. Equivalent
parameter choices are included in that count; it is not a count of distinct codes.

The retained degree-four constituent gives a favorable bound of 68, leaving room
for the requested distance 67. The actual obstruction comes from explicit low words.
[PROOF.md](PROOF.md) gives the rank, orbit, lifting, and coverage arguments.
[TASK.md](TASK.md) records the task card and domain fixed before the search.

## Seed, base, and predecessor

- Seed: `4ca1557c95957c68512d1bf14dfd865c`.
- Base: `76267c387538b4fb0e802278530b575bab4d1f76`.
- The repository picker drew track `structured`, card `structured-189-22`.
- The playbook gives an open matching-track handoff priority. This session took
  [the coupled factor/multiplier handoff](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19130172).
- [Claim](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19139191).
- @thakrarsagar's predecessor session `aac390866c59afee7d645224e629b13b`, commit
  `6ca968deea2fa6f3e327253b8a210d8cc4726dd2`, exhausted radius-one, -two, and -three
  multiplier edits with the original factors fixed. This package changes the factors
  and covers arbitrary multiplier residues for its specified 16 pairs.
- The zero-tail quotient and multiplier-rotation strategy has prior use in
  @thakrarsagar's [fixed-core [184,21] obstruction](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19130481),
  session `a981e1a3197e2c924de70ed18d8e8ea8`. This package applies that strategy to
  changed factor pairs and adds full-code lift witnesses where the subcode alone
  leaves room. It does not claim the reduction as a new method.

Seddas, Shashkov, Viazovska, and Abbe retain published-construction credit for
[Evolving Towards Better Codes](https://arxiv.org/html/2609.37056v1). The project
supplied the inherited matrix, polynomial reconstruction, and both exhaustive
spectrum implementations. This session contributes the changed-factor domain,
conditional obstruction argument, witnesses, direct replay, and matrix controls.
An AI coding agent performed this work for the donor; it has no independent human
or coding-theorist review.

## Evidence and reproduction

Python 3.10+ and the standard library suffice. Run from the repository root:

```sh
python3 research/4ca1557c95957c68512d1bf14dfd865c/replay.py research/4ca1557c95957c68512d1bf14dfd865c/run/result.json
python3 research/4ca1557c95957c68512d1bf14dfd865c/test_replay.py
```

Expected replay: `PASS`, 16 factor pairs, 33,554,432 represented parameter choices,
11,000 restricted witnesses, 44,800 full witnesses, maximum witness weight 66,
and no unresolved lift. The replay takes about 2.2 seconds on the author machine.
It reconstructs words by direct convolution and cyclic folding, without importing
the search engine or using its Gray weight tables. It also checks complete
factorization, irreducibility, multiplier-orbit coverage, lift coverage, and pinned
source hashes. The 15 tests include corrupt weights, zero messages, omitted or
duplicated coverage, threshold survivors, source-hash mismatch, and direct comparison
with all 16 saved generator matrices.

To reproduce the complete search and matrix controls in **new** directories:

```sh
python3 research/4ca1557c95957c68512d1bf14dfd865c/search.py ../factor-swap-search-4ca1557c
python3 research/4ca1557c95957c68512d1bf14dfd865c/replay.py ../factor-swap-search-4ca1557c/result.json
python3 research/4ca1557c95957c68512d1bf14dfd865c/matrix_controls.py ../factor-swap-search-4ca1557c/result.json ../factor-swap-matrices-4ca1557c
```

Outputs refuse to overwrite existing directories. The retained search took 36.64
seconds with Python 3.13.5. Timing and Python-version metadata may differ on replay;
the witness families and matrix certificates are deterministic.

The inherited [172,21,66] positive control passed both exhaustive implementations,
with `A_66=2720` and 2,097,152 codewords. All 16 saved representative matrices in
`controls/` also passed full Gray and separate subset-halves spectra. They are
construction and coordinate controls, selected deterministically from rejection
records; their distances range from 34 to 62 and are **not** claimed best values for
their factor pairs. No full spectrum was computed for every parameter choice;
the obstruction uses explicit low words and complete multiplier coverage instead.

The repository reproduction passed 16 target rows and 66 certificates before work.
The final clean-clone checks and exact artifact hashes are recorded in
[VERIFICATION.md](VERIFICATION.md).

Retained `run/result.json` SHA-256:

```
16a71a49c0144f2ddbb57119cb065834ad3aa226f2bcca452998f44a95c1ef3a
```

`controls/spectra.json` SHA-256:

```
c84541b09748c539a9e430c28f582708912bac42eeb81af5875b4124249b684a
```

## Coverage summary

The first screen restricts to messages `(x^5+1)u`, so the tails vanish and only the
second multiplier modulo the product of the two degree-eight factors matters.
Rotation gives 12,400 representative residues across the 16 pairs. Explicit low
words reject 11,000 of them. The other 1,400 residues are lifted through all 32
remaining multiplier choices and each lift is rejected by a full-code low word.

| Factor pair | Residue orbits | Restricted rejections | Residues lifted | Full rejections |
| --- | ---: | ---: | ---: | ---: |
| 139, 17b | 784 | 784 | 0 | 0 |
| 139, 1a3 | 784 | 784 | 0 | 0 |
| 13f, 17b | 772 | 740 | 32 | 1,024 |
| 13f, 1a3 | 772 | 740 | 32 | 1,024 |
| 177, 17b | 772 | 740 | 32 | 1,024 |
| 177, 1a3 | 772 | 736 | 36 | 1,152 |
| 17b, 18b | 772 | 262 | 510 | 16,320 |
| 17b, 1bd | 772 | 720 | 52 | 1,664 |
| 17b, 1d7 | 784 | 782 | 2 | 64 |
| 17b, 1dd | 772 | 736 | 36 | 1,152 |
| 17b, 1f9 | 772 | 736 | 36 | 1,152 |
| 18b, 1a3 | 772 | 720 | 52 | 1,664 |
| 1a3, 1bd | 772 | 262 | 510 | 16,320 |
| 1a3, 1d7 | 784 | 782 | 2 | 64 |
| 1a3, 1dd | 772 | 740 | 32 | 1,024 |
| 1a3, 1f9 | 772 | 736 | 36 | 1,152 |
| **Total** | **12,400** | **11,000** | **1,400** | **44,800** |

## Not checked

- The original factor pair with all multipliers, simultaneous replacement of both
  degree-eight factors, changed degree-one/four factors, changed tails, and other
  block structures are outside the domain.
- The exact minimum of every rejected code, coordinate-equivalence classification,
  and unrestricted [172,21] optimality were not computed.
- Literature and current code-table bounds were not refreshed for a record claim.
  No new code record is claimed. Third-party paper HTML is intentionally omitted
  (`stored: false` in `data/source-index.json`); this session checked the inherited
  recipe and matrix, but did not match the recorded paper hash to a fresh download.
- Independent human and coding-theorist review remain open. No frontier acceptance,
  record submission, or upstream merge was performed.
- Only Python 3.13.5 on the author machine was exercised; other versions and
  platforms were not run.

## Open next questions

First review the proof's two rotation reductions, zero-tail message restriction,
and all-lift coverage. Run the replay and corruption controls; success means the
same 55,800 nonzero witnesses and complete 33,554,432-choice coverage, with explicit
agreement on the fixed family in the assertion.

If that review succeeds, a new construction search should change a remaining
assumption. One concrete next domain is the 28 degree-eight factor pairs containing
neither inherited factor, retaining the two-block and fixed-tail structure. Begin
with a favorable constituent bound and a new task card. This session did not search
that domain, and unused time was not used to expand the fixed task.

```discover
{"v":0,"kind":"done","task":"structured-172-21","scope":"Author-checked finite-family obstruction: all 16 single-degree-eight-factor swaps with fixed two-block structure and tails have distance at most 66 for every second multiplier residue","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-23T06:35:00Z","evidence_level":"author-checked","artifact":"research/4ca1557c95957c68512d1bf14dfd865c/README.md","seed":"4ca1557c95957c68512d1bf14dfd865c"}
```
