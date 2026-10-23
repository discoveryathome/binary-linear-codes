# Fixed-tail single-factor-swap obstruction

This is an exact finite obstruction for the family defined below. The computation
and proof are **author-checked** in one AI agent session. Separate implementations
do not constitute independent scientific review.

## Family and assertion

Work in GF(2)[x]. Write

```
M = x^85 + 1
P = x^5 + 1 = (x + 1)(x^4 + x^3 + x^2 + x + 1)
H = A B
h = P H
g = M / h.
```

The two monic irreducible factors A and B have degree eight and divide M.
Exactly one of the inherited pair `{0x17b, 0x1a3}` is retained, and the other is
replaced by one of the eight remaining degree-eight factors. Hexadecimal integers
encode polynomial coefficients, with bit i the coefficient of x^i.

For every one of these 16 unordered pairs, and every polynomial f of degree less
than 21, consider the binary linear code

```
C_f = { (g m, (g f m mod M), m(1), m(1)) : deg(m) < 21 }.
```

The first two entries are 85-coordinate coefficient vectors, constant term first.
The final two entries are the retained `11111` tails: every generator row has a one
in each tail position. This is precisely the single-factor change to the inherited
two-block [172,21] construction. The first block is injective because a nonzero
product g m has degree at most 84, so every C_f has dimension 21.

**Assertion:** every C_f in this domain has minimum distance at most 66. The domain
contains 16 × 2^21 = **33,554,432 parameter choices**, which need not represent
distinct codes. No assertion is made about other divisors, tails, block structures,
or unrestricted [172,21] codes.

Higher-degree multipliers do not enlarge this fixed family: adding a multiple of h
to f changes the second block by a multiple of M. Thus degree less than 21 covers
all multiplier residues for each selected divisor.

## Favorable bound before search

The retained degree-four factor supplies a dimension-four zero-tail cyclic
constituent of period five. Its two blocks give a binary [10,4] code repeated 17
times. Distance at least five for [10,4] would violate the Griesmer inequality
`5 + 3 + 2 + 1 = 11 > 10`. Hence that constituent bounds distance by 68. This bound
leaves the requested distance 67 possible; it was not a reason to discard the task.

## Reducing the multiplier domain

Restrict messages to `m = P u`, with `deg(u) < 16`. They give a dimension-16
subcode with both tails zero:

```
( (M/H)u, ((M/H) f u mod M), 0, 0 ).
```

Its value depends only on f modulo H. Changing f by Ht adds `M t u` to its second
block, which vanishes modulo M. A saved nonzero u therefore rejects every full
multiplier with that residue, whenever its two-block weight is at most 66.

Multiplication of f by x modulo h rotates only the second 85-coordinate block.
It preserves all codeword weights, including tails. Multiplication by x modulo H
partitions the 65,536 residues into orbits of length dividing 85, since H divides
M. The replay verifies the complete partition, disjointness, and least-residue
representatives. It does not assume that every nonzero orbit has length 85.

Take any full multiplier f and rotate it until its residue modulo H is the chosen
representative r. The resulting full multiplier has a unique form

```
r + Ht,     deg(t) < 5.
```

There are exactly 32 lifts. Consequently, rejecting a representative by a zero-tail
witness, or rejecting all its 32 lifts by full-code witnesses, rejects every original
multiplier. Normalization can create duplicate equivalent parameter choices; it
cannot omit a residue.

## Exhaustive witness certificate

The retained `run/result.json` contains:

- 12,400 dimension-16 multiplier-orbit representatives across the 16 factor pairs.
- 11,000 representatives rejected by explicit nonzero u and two-block weight.
- 1,400 remaining representatives, each discharged by all 32 full multiplier lifts.
- 44,800 full-code rejection witnesses, each with a nonzero degree-below-21 message.
- No unresolved multiplier lift or threshold survivor.

An entry `[f, u, w]` in `restricted_rejections` means the full message is P u.
An entry `[f, m, w]` in `full_rejections` uses m directly. All saved weights satisfy
`1 <= w <= 66`.

The replay factors M afresh, verifies that the catalogue is complete and that the
degree-eight factors are irreducible, derives the 16 pairs, checks the entire orbit
partition and all lifts, and reconstructs every witness by direct polynomial
convolution followed by folding modulo `x^85+1`. It does not import the search
engine, its weight tables, or the repository polynomial helpers.

Every supplied witness is nonzero: its nonzero first block follows from the same
degree argument used for rank. The coverage argument above and these explicit
weights prove the assertion for this fixed family. They do not determine the exact
minimum distance of each candidate or establish unrestricted optimality.

## Search-side message orbits

For finding witnesses, `search.py` also reduces the message space by multiplication
by x modulo the relevant check polynomial. This rotates both cyclic blocks.
For full messages, evaluation at one is invariant because h(1)=0, so the tails are
unchanged. This makes exact threshold screening cheaper. The final obstruction
replay does not rely on this search-side reduction: it checks the explicit messages
and multiplier coverage directly.

## Credit

Seddas, Shashkov, Viazovska, and Abbe retain credit for the published construction
in [Evolving Towards Better Codes](https://arxiv.org/html/2609.37056v1). The project
retains credit for reconstruction and its Gray and subset-halves checkers. The
predecessor session by @thakrarsagar, `aac390866c59afee7d645224e629b13b`, commit
`6ca968deea2fa6f3e327253b8a210d8cc4726dd2`, exhausted radius-three multiplier
edits at the original divisor and requested this factor/multiplier follow-up in
[Handoffs](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19130172).

The zero-tail quotient and multiplier-rotation method was also used in
@thakrarsagar's earlier [fixed-core [184,21] obstruction](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19130481),
session `a981e1a3197e2c924de70ed18d8e8ea8`. The present package applies it to the
16 changed-divisor families and adds full-code lift witnesses when that restricted
subcode does not settle the target.

This session supplies the changed-divisor exhaustive domain, full-lift coverage,
explicit witnesses, and separate direct replay. Coding-theorist review of the
conditional proof remains open.
