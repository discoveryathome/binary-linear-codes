# Full normalized two-block core family

Seed: `4ca1557c95957c68512d1bf14dfd865c`.
Base: `76267c387538b4fb0e802278530b575bab4d1f76`.
Parent session: about 06:00 UTC, 2026-10-23; revised total budget 480 minutes.
This task starts about 07:18 UTC, with a 90-minute research cap and 30 minutes for
verification/publication. Global new-research stop: 12:00 UTC; session cap: 14:00 UTC.
The user explicitly permits multiple focused PRs, superseding the playbook default.

## Question and scope fixed before the search

Does any normalized length-170, dimension-21 two-block cyclic core with block
length 85 have distance at least 65? If all such cores have a nonzero word of
weight at most 64, any two appended binary columns can raise that word's weight by
at most two and cannot yield distance 67 at [172,21].

For M=x^85+1, consider every monic degree-21 divisor h of M, g=M/h, every second
multiplier f modulo h, and messages m of degree below 21. The core is
`(g m, g f m mod M)`. Its first projection is injective. This excludes two-block
cyclic codes whose first projection has rank below 21 and excludes other block
lengths and multi-generator representations.

The complete factorization has one degree-one factor, one degree-four factor,
and ten degree-eight factors. Thus h must be `(x^5+1) A B`, with A and B any distinct
degree-eight factors: all 45 pairs, all 2^21 multiplier residues per pair, or
94,371,840 core parameter choices. Arbitrary appended columns are handled by the
weight-increase inequality, not by claiming to enumerate their 2^42 choices.

First screen the dimension-16 subcode m=(x^5+1)u through residues modulo A B, with
explicit rotation-orbit coverage. Lift every unresolved residue through all 32
full multipliers and screen the complete core. Retain a nonzero message and exact
weight for each rejection. Any threshold survivor falsifies the proposed universal
64 bound: save its parameters and exact matrix, run both exhaustive spectra, then
assess two-column extension constraints as one bounded pivot. Never silently
replace a failed universal claim by a weaker assertion.

## Favorable bound, positive control, and falsification

The degree-four constituent has period five and rank four. Its two blocks give
a binary [10,4] code repeated 17 times; the Griesmer bound gives constituent
distance at most 68. With two additional coordinates the favorable full-code
bound is 70, so distance 67 is not excluded before searching.

Positive control: strip the two retained tails from the inherited [172,21,66]
matrix, verify its [170,21,64] core with Gray and separate subset-halves spectra,
and preserve the exact matrix and source hash. Reproduce the repository baseline.

Failure controls: missing/duplicate multiplier orbits or lifts, zero/wrong
witnesses, altered divisor/domain metadata, and a claimed universal bound in the
presence of a threshold survivor must be rejected by a separate replay.

## Distinction from prior work and credit

The original seed drew `structured/structured-189-22`; the open same-track
[coupled factor/multiplier handoff](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19130172)
led to [PR #10](https://github.com/discoveryathome/binary-linear-codes/pull/10),
head `97d51053b68bb721a6596ccada6bdd3ac04a8f32`. That PR covers 16 single-factor
swaps and fixed tails at bound 66. This task tests a stronger core bound 64,
the original divisor and all 28 double swaps, and arbitrary two-column extensions.
It is a changed bounded question, not an improvement claimed on the original code.

Credit Seddas, Shashkov, Viazovska, and Abbe for the published construction, the
repository for reconstruction and exact checkers, @thakrarsagar's session
`aac390866c59afee7d645224e629b13b` for the original handoff, the fixed-core
[184,21] obstruction (session `a981e1a3197e2c924de70ed18d8e8ea8`) for the quotient/
rotation strategy, and PR #10 for the full-lift witness method. All new work remains
author-checked by one AI agent session; independent scientific review is open.

Overlap check at 07:11 UTC found open PRs #7–#10 only; none investigates the full
core family and arbitrary two-column extensions. No other later structured claim
was present in Handoffs. No accepted record, catalogue, or frontier will be edited.

## Dated analytic extension after the fixed search

At about 07:35 UTC the complete normalized-domain search and separate witness replay
had no threshold survivor. The computational domain remains unchanged. Extend the
conclusion analytically to codes with neither block projection injective, using the
standard squarefree CRT decomposition and the constituent dimension equation
`e1 + 4 e4 + 8 sum(e8) = 21`. The only possible aggregate pattern is `(1,1,2)`.
If a degree-eight constituent has field-dimension two, an axis subcode has binary
dimension eight and effective length 85. Otherwise all active constituents are
lines; two non-injective block projections force an axis constituent of degree four
or eight. The binary Griesmer bound then gives a word of weight at most 44 or 40.

This is a stated enlargement of the proof's scope, not an extra computational
search: all binary [170,21] codes invariant under simultaneous shifts of the two
85-coordinate blocks are covered. Add the trivial rank-drop case when puncturing
two coordinates from a [172,21] code: a lost dimension gives a nonzero word supported
on those two positions. Otherwise the core bound plus two applies. Exact scope and
the normalization argument must be explicit in PROOF.md; independent review remains
required before any scientific acceptance.
