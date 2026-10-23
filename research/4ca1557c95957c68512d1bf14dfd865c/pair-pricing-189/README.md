# B/C invariant-subcode pricing: 34 of 84 factor triples excluded

For each canonical B/C model of PR #12, nine of the 36 degree-six factor pairs
cannot reach distance 74 in their rank-16 low-plus-two-field subcodes. Consequently
34 of the 84 full-code factor triples are excluded per profile. **Fifty triples
per profile remain open.** This is an author-checked structured-family restriction;
no new [189,22] code, record or unrestricted impossibility is claimed.

The excluded pairs are the eight containing factor 0x49 and the pair 0x57/0x75.
A short repetition/Griesmer argument strengthens the first exclusion to distance
at most 70. The second uses complete finite witnesses of weight at most 72.
[PROOF.md](PROOF.md) states the scope, symmetry, threshold implication and limits.

## Fixed experiment and provenance

- Original seed: `4ca1557c95957c68512d1bf14dfd865c`.
- Draw: `structured/structured-189-22`; deterministic diagnostic, no new randomness.
- Base: `76267c387538b4fb0e802278530b575bab4d1f76`.
- [Claim](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19143956).
- [TASK.md](TASK.md) fixes the domain and first-survivor stopping rule before execution.
- Donor grant: corrected 480 minutes, multiple focused PRs and coordination posts.
  New research stops by 12:00 UTC, leaving the last 120 minutes for verification.

There are 72 profile/pair cases. Independent three-position block rotations give
189 representatives of each nonzero two-field scalar pair, except 567 for the
short-orbit pair 0x57/0x75. The maximum domain is 3,143,448 normalized choices.
The search stops each case at its first exact distance-74 survivor, or exhausts
the case if none exists. These counts refer to parameters, not inequivalent codes.

The retained run tested 1,335,021 choices in 22.535 seconds including controls and
both full spectrum checks on every survivor. It completely covered 1,214,514 choices
in 18 excluded cases, and 120,507 prefix choices in 54 surviving cases. The 54
rank-16 survivor matrices have distances 74 (13 cases) or 76 (41 cases). They prove
the pair threshold is attainable for each remaining pair; they are not claimed
as optimal pair codes or as mutually compatible full-code parameters.

Every tested choice has a saved nonzero message and weight. Early-rejection values
are upper bounds, not exact minima. All 18 excluded domains have complete orbit
coverage and weights <=72. Their full Cartesian domains, every prefix, every word
and all 54 attaining spectra are checked by a separate direct-arithmetic replay.

## Replay

From the repository root, Python 3.10+ and only the standard library:

```sh
python3 research/4ca1557c95957c68512d1bf14dfd865c/pair-pricing-189/replay.py research/4ca1557c95957c68512d1bf14dfd865c/pair-pricing-189/run
python3 research/4ca1557c95957c68512d1bf14dfd865c/pair-pricing-189/test_replay.py
```

Expected: PASS, 72 cases, 1,335,021 tested choices, 18 excluded pairs, 54 threshold
survivors, 50 eligible triples in B and C; 16 tests pass. Failure controls include
zero/altered words, omitted choices/cases, false exact flags, incomplete exclusions,
short-orbit counts, source/seed changes, false survivor distance and rank defects.
Separate controls decode the order-nine repetition to rank ten at length 27.

Fresh regeneration requires a C++17 compiler and new output directory:

```sh
mkdir -p ../pair-pricing-build
c++ -O3 -std=c++17 -march=native research/4ca1557c95957c68512d1bf14dfd865c/pair-pricing-189/threshold.cpp -o ../pair-pricing-build/threshold
python3 research/4ca1557c95957c68512d1bf14dfd865c/pair-pricing-189/run.py ../pair-pricing-build/threshold ../pair-pricing-replay
```

The C++ accelerator's coordinates are checked against the primary Python model
for all 72 cases. All surviving matrices receive both repository spectra and
a full C++ check. No binary is committed. Source hashes, flags, environment,
matrix hashes and parameters are in `run/metadata.json`, `run/cases.json` and
the certificates. All ledger bytes are retained in `run/ledger.csv.gz`.

Compressed-ledger SHA-256:
`4704524e1a5d49b7b24885241f93fb6008355db31bfddb95cd53f86ca5afbb64`.
Raw-ledger SHA-256:
`16609242369c991056a87e4fb9e96b6ff4ba8f068c73cb47bfa93f59932ac628`.
Clean-clone evidence and timing are recorded in [VERIFICATION.md](VERIFICATION.md).

## Credit and open work

The canonical B/C constituents, row conventions and primary enumerator mechanics
come from this same author session's [PR #12](https://github.com/discoveryathome/binary-linear-codes/pull/12),
head `67a4fad80c8073222a43dcb85e543640fabc5a66`. This package is self-contained on
main and has no changed-path overlap with PRs #10–#12. The new contribution is
threshold pricing, the stated pair exclusions and the resulting factor graph.

Seddas, Shashkov, Viazovska and Abbe retain credit for the published parent;
the repository supplied reconstruction and both exhaustive spectrum checkers.
Standard CRT theory, Griesmer's inequality and @thakrarsagar's structured sessions
`aac390866c59afee7d645224e629b13b` and `a981e1a3197e2c924de70ed18d8e8ea8`
informed the approach. No general method or literature novelty is claimed.

Not checked: simultaneous compatibility of all three pair constraints, full-code
parameters for the 50 remaining triples per profile, profile A, exact distances
of every rejected pair, optimality of threshold survivors, unrestricted code
equivalence/optimality, fresh full literature/record reconciliation, other platforms,
and independent human review. The general B/C classification still depends on
the author-checked argument in PR #12. No accepted results or frontier are changed.

```discover
{"v":0,"kind":"finding","task":"structured-189-22-pair-pricing","scope":"Author-checked rank-16 pair threshold exclusions eliminate 34 of 84 canonical B/C factor triples per profile, with 50 remaining; no full target code","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-23T10:49:51Z","evidence_level":"author-checked","artifact":"research/4ca1557c95957c68512d1bf14dfd865c/pair-pricing-189/README.md","seed":"4ca1557c95957c68512d1bf14dfd865c"}
```
