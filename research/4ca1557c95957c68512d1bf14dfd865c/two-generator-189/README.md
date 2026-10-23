# Three-block [189,22] CRT profiles: target not reached

**Outcome: structural reduction and bounded negative results, author-checked.**
No distance-73 candidate was found. The new two-generator sample has maximum
distance 70 over 163,272 distinct tested parameter choices. A complete 58,033-choice
field-scalar neighborhood of the published parent has maximum distance 72. The
published [189,22,72] parent remains the baseline; a smaller minimum-word count
would not constitute a distance improvement.

The useful structural result is a necessary reduction to three CRT constituent
profiles for possible distance at least 73. Two profiles require two R-generators
and escape the inherited full-block-projection representation. Their low constituents
leave a favorable bound 84, but both profiles are even, so they need distance at
least 74 to meet the card's threshold. [PROOF.md](PROOF.md) gives the assumptions,
normalizations, finite bounds, and exact limits of the null results.

## Task, provenance, and fixed domains

- Original seed: `4ca1557c95957c68512d1bf14dfd865c`.
- Base: `76267c387538b4fb0e802278530b575bab4d1f76`.
- Executed repository draw: `structured/structured-189-22`, the original drawn card.
- [Claim](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19141787).
- User grant: corrected total 480 minutes, multiple focused PRs allowed; no merges,
  accepted-result edits, record submissions, or direct author outreach.
- [TASK.md](TASK.md) fixes the two-generator proposal cap and records the single
  bounded pivot. The global last 120 minutes remain for verification/handoffs.

The parent first step passed both full spectra: 4,194,304 words, distance 72,
2,394 minimum words. The card's 16-proposal starter with the exact code-converted
seed found no improvement and is retained in `starter-seeded/`. An earlier starter
invocation used a mistyped decimal seed; its separate 16 null proposals remain in
`starter/`. Task selection always used the original hex seed. The canonical integer
seed and this correction are explicit in TASK.md; neither auxiliary run is counted
as part of the new-model search.

## New models and constituent pricing

Three length-63 cyclic blocks have irreducible factor degrees 1,2,3,3 and nine sixes.
For a possible distance-73 binary dimension-22 code, the necessary aggregate profiles
`(degree-one dimension, degree-two dimension, active degree-three lines, active degree-six lines)` are

```
A = (1,0,1,3), B = (0,2,0,3), C = (2,1,0,3).
```

A is the inherited one-generator form after normalization. B and C use a canonical
rank-four low constituent and three degree-six field lines, for binary rank 22.
Each has 84 factor triples and six nonzero GF(64) multipliers. Their block projection
ranks are 20 and 21; they are not just a binary basis change of the inherited
one-R-generator model under the same shift. Unrestricted coordinate equivalence
between codes is not classified.

The exact small-code pricing retains all 21 GF(4) planes, 147 binary-plane/GF(4)-line
pairs, 4,096 two-degree-three multiplier pairs, and 35,721 degree-six scalar pairs.
It confirms the low bound 84 and the degree-three-pair obstruction 72. All nine
degree-six factors have favorable line distance at least 84, so that screen does
not eliminate the proposed construction families. Canonical controls passed both
existing exhaustive spectrum implementations. A separate arithmetic implementation
checks all small pricing tables.

## Complete retained search list

The deterministic seeded run used 16 initial samples for each of 168 profile/factor
templates, then three bounded restarts of 4,096 proposals for each of sixteen selected
templates. All 199,296 proposals are retained, including 36,024 duplicates. There are
163,272 distinct parameter choices; this is not a count of inequivalent codes.

- B best: distance 70, 252 minimum words.
- C best: distance 70, 315 minimum words.
- Exact fitness enumeration records: 9,722. Other records are explicit low-word
  rejections; their values are distance upper bounds, not exact minima.
- Every proposal has a nonzero word of weight at most 70. Together with both full
  best spectra, this proves the tested list's exact maximum 70.
- CPU kernel and Python models agreed on 18 coordinate models and seven full
  spectrum controls, including the published parent.

The freshly compiled C++17 search is an accelerator; no executable binary is
committed. Verification uses only Python's standard library. The full run took
179.559 seconds on the author machine. This is not a held-out benchmark, a fair
algorithm-race result, or evidence of an improved code construction.

## One complete bounded pivot

The published parent was normalized by cyclic rotations `[0,6,5]` of its blocks.
The normalized degree-three factor is d, degree-six factors 61,6d,75 (hex), and
six scalar values `[15,14,8,34,6,60]` (decimal). Exact row-space equality confirms
the coordinate-equivalent parent.

All zero-, one-, and two-scalar replacements by nonzero GF(64) elements were checked:
`1+6*62+15*62^2=58,033`. Every choice has a saved nonzero word of weight at most 72.
The parent attains 72, so this finite neighborhood's maximum is exactly 72. No
target candidate survived. The final source-pinned replay took 9.464 seconds, including controls
and both full parent spectra.

## Replay and regeneration

From the repository root, with Python 3.10+:

```sh
python3 research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/verify_pricing.py research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/pricing/pricing.json
python3 research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/replay.py research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/run
python3 research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/replay_pivot.py research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/pivot
python3 research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/test_replay.py
```

Expected: pricing PASS, all 199,296 proposal witnesses PASS with exact tested-list
maximum 70, all 58,033 neighborhood choices PASS with attained parent distance 72,
and 15 tests pass. The tests include altered weights, zero messages, false duplicate
or acceptance flags, a missing final proposal, incorrect derived seed, false best
distance, source mismatch, a missing low generator, corrupt small models, and a changed pivot basepoint.

To regenerate, build fresh binaries in a new sibling folder and use new output
directories (existing outputs are refused):

```sh
mkdir -p ../two-generator-build
c++ -O3 -std=c++17 -march=native research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/search.cpp -o ../two-generator-build/search
c++ -O3 -std=c++17 -march=native research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/pivot-search.cpp -o ../two-generator-build/pivot
python3 research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/run_search.py ../two-generator-build/search ../two-generator-replay
python3 research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/run_pivot.py ../two-generator-build/pivot ../field-neighborhood-replay
```

The seed-to-64-bit-PRNG derivation, source and binary hashes, flags, exact tested
parameters, witnesses, duplicate counts and timings are retained in the metadata
and gzip CSV ledgers. Timing and compiler-specific binary bytes may differ on
another machine; the deterministic proposal ledger is the comparison artifact.
The final clean-clone checks and hashes are in [VERIFICATION.md](VERIFICATION.md).

## Source baseline, credit, and open work

A focused live table page returned 71–81; its URL, retrieval date and hash are in
`current-source.json`. The published paper's stronger distance 72 remains the
exclusion baseline. This focused retrieval is not a full record/literature audit.

Seddas, Shashkov, Viazovska and Abbe retain credit for the parent in
[Evolving Towards Better Codes](https://arxiv.org/html/2609.37056v1). The project
supplied reconstruction, starter search and both exhaustive checkers. The standard
CRT framework, Griesmer inequality and prior handoffs/PRs #10/#11 informed the
methods. This AI agent session contributes the specialized profile reduction,
alternative-model experiments and finite-neighborhood witnesses. Evidence remains
author-checked, with independent scientific review open.

Not checked: the unsearched B/C family, changes to three or more parent scalars,
different parent factors or low-degree patterns in the pivot, unrestricted code
equivalence or optimality, full prior-art/freshness reconciliation, and other Python
versions/platforms. Only the two best sample matrices and named controls received
full independent-algorithm spectra; every remaining tested choice has a direct low
word, not a separately checked exact minimum/multiplicity.

Open next question: can an invariant-subcode or higher-order move explain the
remaining gap? First independently review the necessary-profile argument and replay
both finite datasets. A useful next construction must escape the completed pivot
neighborhood or improve a different verified template; source lower bounds and
maintainer acceptance remain separate.

```discover
{"v":0,"kind":"finding","task":"structured-189-22","scope":"Author-checked necessary CRT profiles, bounded two-generator null experiment (sample maximum 70), and complete 58033-choice parent field-scalar neighborhood of maximum 72; target 73 not reached","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-23T10:00:29Z","evidence_level":"author-checked","artifact":"research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/README.md","seed":"4ca1557c95957c68512d1bf14dfd865c"}
```
