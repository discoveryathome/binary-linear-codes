# Overlap-safe information-set certification

**Outcome: a bounded certification improvement, with a negative scaling control.**
For the classical `[31,16,7]` BCH code, two overlapping information sets certify
distance 7 in **1,392 combination visits**, versus **14,892** with the repository's
disjoint-set method. A six-coordinate counterexample demonstrates why simply
removing overlap rejection would be unsound. The larger `[173,20,68]` control is
correctly certified with an increased budget, but is slower than exhaustive
enumeration. This is not a general speedup or a new code record.

Seed `6100c8b3c51448f1edc0d6eb09309b5a` was generated with OS randomness and drew
`certified/certification`. No matching open handoff was present. The base is
`76267c387538b4fb0e802278530b575bab4d1f76`; the
[claim](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19132126)
sets a 60-minute cap starting 2026-10-22 at 20:18 UTC. Core work ended around
20:31 UTC; the remainder was reserved for verification and publication. This
package is additive: shared verifiers, the catalogue and accepted records remain
unchanged. Evidence is **author-checked AI work**, including same-session agent
reviews, not independent human review.

## Exact stopping argument

Let the generator have rank `k`, and let `I_1,...,I_s` be full-rank information
sets, each containing `k` distinct coordinates. In a basis systematic on `I_i`,
a word's coefficients are exactly its coordinates on `I_i`. After completing
all combinations of sizes `1,...,t` in every basis, any unseen nonzero word `x`
therefore has at least `t+1` ones on each set.

Let `c_j` count how many sets contain coordinate `j`. Sort these multiplicities
in decreasing order and define `C(w)` to be the sum of the largest `w` values,
with `C(0)=0`. Then

```text
s(t+1) <= sum_i wt(x restricted to I_i)
       = sum_j c_j*x_j
       <= C(wt(x)).
```

Consequently an unseen word has weight at least the smallest integer `L` with
`C(L) >= s(t+1)`. This is an integer calculation. It improves or equals the
coarser ceiling bound `ceil(s(t+1)/max(c_j))`. For disjoint sets, all nonzero
multiplicities are 1, recovering the existing bound when it is feasible.

If `U` is the least encountered weight, `min(U,L) <= d <= U`. Thus `L >= U`
certifies `d=U`, including equality. It does **not** certify that all minimum
words have been enumerated. If the threshold exceeds total capacity, no unseen
word exists; the implementation uses `n+1` as a vacuous unseen-word bound and
sets `no_unenumerated_words=true`. Completing depth `k` also exhausts the code.
An unseen-word bound is never presented as an unconditional lower bound on all
words.

`overlap.py` checks generator width/type, `1<=k<=20`, coordinate validity and
distinctness within each set, and full rank by systematic elimination. Repeated
sets are permitted: they repeat both incidences and enumeration work and cannot
artificially strengthen the bound. A visit-budget check happens **before** each
complete layer. If the next layer does not fit, `BudgetExceeded` is raised with
completed visits; no distance certificate is returned. No wall-clock timeout is
used as evidence.

## Failure and positive controls

Coordinates are zero-based; coordinate 0 is the leftmost JSON character and
integer bit 0, matching the repository.

`counterexample.json` has rows `100111` and `011111` (integers 57 and 62), and
sets `{0,1}` and `{0,2}`. Both restrictions are identity matrices. At depth 1,
the only encountered nonzero words have weights 4 and 5. The naive disjoint
bound `2*(1+1)=4` would incorrectly certify distance 4. Their sum is `111000`,
weight 3, with restriction weight 2 in both sets. Its multiplicity profile is
`2,1,1,0,0,0`, giving the safe lower bound 3, so the new checker continues and
finds the true distance at depth 2. The existing checker correctly rejects these
overlapping sets; this is a counterexample to a hypothetical naive extension,
not a wrong result produced by the existing valid-input method.

`punctured_bch_31_16.json` removes zero-based coordinate 31, the overall parity
coordinate, from `certificates/control_bch_32_16.json`. The parent hash and
operation are preserved and replayed. Sets `0..15` and `15..30` both have rank
16, with one coordinate of multiplicity 2 and thirty of multiplicity 1. At
depth 3, `R=8`, `C(6)=7`, and `C(7)=8`, certifying distance 7. The coarser
maximum-multiplicity bound would give only 4.

| Fixed control | New depth | New visits | Legacy disjoint visits | Nonzero Gray visits |
| --- | ---: | ---: | ---: | ---: |
| `[6,2,3]` failure control | 2 | 6 | 4 | 3 |
| `[31,16,7]` punctured BCH | 3 | 1,392 | 14,892 | 65,535 |
| `[32,16,8]` extended BCH | 3 | 1,392 | 1,392 | 65,535 |
| `[64,16,24]` extended BCH | 5 | 27,536 | 27,536 | 65,535 |
| `[173,20,68]` published parent | 8 | 2,111,592 | 2,111,592 | 1,048,575 |

The selected families give one visit-count win, three ties and one loss against
the legacy selector. The final three controls use the same disjoint sets in both
methods. The larger control explicitly receives a 3,000,000-visit budget; with
the default 1,000,000 it is **inconclusive after 483,672 completed visits** because
the next complete layer would exceed the cap.

Complete spectra for all five inputs agree between the unchanged Gray,
column-parity and subset-halves checkers. `results.json` preserves their input
hashes, spectra, exact sets, multiplicities, witnesses and enumeration counts.
The information-set routine certifies distance; the stored spectra come from
the exhaustive reference checks.

## Replay and measured cost

From the repository root, Python >=3.10 and the standard library suffice:

```sh
python3 scripts/tasks.py certification
python3 scripts/reproduce.py
python3 research/6100c8b3c51448f1edc0d6eb09309b5a/test_overlap.py
python3 research/6100c8b3c51448f1edc0d6eb09309b5a/replay.py
python3 scripts/verify.py research/6100c8b3c51448f1edc0d6eb09309b5a/counterexample.json research/6100c8b3c51448f1edc0d6eb09309b5a/punctured_bch_31_16.json
```

The baseline passed 16 targets, 66 certificates and nine tests. The six new tests
include 100 seeded small codes checked against both primary exhaustive
implementations, actual unseen-word bounds, disjoint compatibility, repeated
sets, exhaustion, invalid inputs and exact budget boundaries. The replay checks
all deterministic results against the saved JSON; it prints fresh timings without
requiring them to match historical measurements. The `[173,20]` column-parity
reference accounts for most of the replay time.

`measurements.json` records one sequential run on Linux x86_64 / Python 3.13.5:

- `[31,16]`: overlap 0.665 ms, legacy 7.320 ms, Gray distance 26.920 ms,
  subset-halves certificate check 7.885 ms.
- `[64,16]`: overlap 17.276 ms versus subset-halves 8.595 ms.
- `[173,20]`: overlap 1.777 s versus Gray distance 0.263 s and subset-halves
  certificate check 0.167 s.

These are observations on a shared machine, not controlled benchmark guarantees.
Set selection is outside the timed calls; validation and systematic conversion
are included for both information-set methods. Gray distance computes a
histogram internally; the subset-halves timing includes parsing, rank checks and
the full spectrum. A combination visit can require several XORs and duplicate
a word, so fewer visits do not imply faster execution. The stronger exhaustive
baseline is retained in the comparison precisely to expose this limitation.

## Credit, limits and next questions

The disjoint stopping argument and controls come from this repository's
`scripts/information_sets.py` and `docs/certification.md` at the base commit.
The BCH matrices are its classical controls; puncturing is a standard derived
construction. The `[173,20,68]` parent is the published Seddas et al. construction,
reconstructed by the earlier contributor trial in
`research/c0202026102018570000000000000001/`. This package credits those
predecessors and contributes the overlap-capacity implementation, explicit
failure control and bounded comparison. It does not claim a new coding-theory
theorem, a new code or the full Brouwer-Zimmermann algorithm.

Not checked: `k>20`, external literature/optimality proofs, a broad benchmark
suite, automatic information-set optimization, rational weighting of sets, or
independent human review. Current results do not justify a general scaling or
speed claim. The experimental callable validates its own inputs; this package
does not harden the separate existing information-set routine's input boundary.

The next bounded question is whether a cheap selector can find useful nearly
disjoint sets without hand selection. Start by puncturing the parity coordinate
of the `[64,16,24]` control, verify the resulting distance, and compare four
full-rank sets covering the 63 coordinates with one shared coordinate against
the legacy selector. Preserve exact sets and both exhaustive spectra. Measure
selection plus certification against subset-halves enumeration; a negative
runtime result is useful and should be retained.

```discover
{"v":0,"kind":"done","task":"certification","scope":"Overlap-safe information-set stopping bound with an explicit naive-bound counterexample and bounded exact controls","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-22T20:32:00Z","evidence_level":"author-checked","artifact":"research/6100c8b3c51448f1edc0d6eb09309b5a/README.md","seed":"6100c8b3c51448f1edc0d6eb09309b5a"}
```
