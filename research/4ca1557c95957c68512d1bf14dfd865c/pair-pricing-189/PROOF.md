# Pair exclusions for the canonical B/C models

Evidence is author-checked by one AI agent session. This is a specialized
computer-assisted statement about the models in PR #12; independent mathematical
review is open. It is not an unrestricted bound for [189,22] binary codes.

## Models and the threshold implication

Let R=GF(2)[x]/(x^63+1). Use the canonical low constituent B or C specified in
TASK.md and three distinct degree-six field lines, each with all three entries
nonzero and first entry normalized to one. The low part has binary dimension four;
each field line adds six. This gives a dimension-22 R-submodule of R^3. Every word
has even total weight, so distance >=73 requires distance >=74.

Removing one degree-six line gives an invariant binary dimension-16 subcode.
The full code's distance cannot exceed any such subcode's distance. Thus if all
rank-16 codes for a particular factor pair have distance <=72, every canonical
B/C full code containing that pair is excluded from the target.

The argument that every possible distance-73 three-block code has profile A, B
or C, and that B/C admit these canonical low forms, belongs to PR #12. The present
finite statement applies directly to the explicit canonical models whether or
not a reviewer accepts that wider classification. Profile A is not excluded here.

## Rotation-normalized pair coverage

For factors p,q and nonzero field scalars f_p,f_q,g_p,g_q, write the two normalized
field lines as (1,f_p,g_p) and (1,f_q,g_q). A three-position cyclic rotation of the
second block fixes every low word (period dividing three) and multiplies f_p,f_q
by x^3 in their respective fields. The same independent operation on block three
acts on g_p,g_q. Both preserve Hamming weights.

Each nonzero scalar pair has a unique smallest packed representative a+64*b in
its orbit. The independent replay computes the action from actual 63-coordinate
rotations of embedded field words, rather than the search's field-remainder rule.
It checks all 3,969 scalar pairs, every orbit and all short periods.

The degree-six factors have orders 63 except 0x49 of order nine and 0x57/0x75 of
order 21. Every two-factor action therefore has period 21, except the pair
0x57/0x75 of period seven. There are respectively 189 or 567 representatives.
Their Cartesian square covers every four-scalar choice up to the two stated
rotations. No other code equivalence is used. The maximum domain is
2*(35*189^2+567^2)=3,143,448 across both profiles.

## Completed threshold calculation

Each case is tested in sorted representative order, stopping at its first code
of distance >=74. Cases with no survivor exhaust the full Cartesian square. An
early rejection retains a nonzero message and its exact weight <74; since the
models are even this weight is <=72. Exact minima of rejected cases are not needed.

The retained run tests 1,335,021 normalized choices. Of these, 1,214,514 completely
cover 18 excluded profile/pair cases, and 120,507 form prefixes in 54 surviving
cases. Every excluded case has a nonzero <=72 word for every representative.
Separate direct replay checks the complete excluded domains and all prefixes.
Each survivor has a rank-16 matrix and full agreeing spectra from both repository
implementations: 13 have distance 74 and 41 have distance 76. These are threshold
certificates, not pair-distance maxima.

In each profile the excluded pairs are the eight containing 0x49 and the single
pair (0x57,0x75). Every other pair has a threshold survivor. The finite calculation
for the order-21 pair therefore proves its canonical rank-16 family has distance
at most 72. No attaining maximum is claimed for this excluded family.

## A shorter explanation of the order-nine exclusions

The low constituent plus the single degree-six factor 0x49 already forces a
stronger bound 70. Its rows have period nine in each block: x^9+1 divides x^63+1,
0x49 divides x^9+1, and the low words have period at most three. The binary
rank-ten subcode is a sevenfold repetition of a length-27, dimension-ten code.
Distinct CRT components give dimension 4+6=10, preserved by decoding repetition.

The Griesmer inequality excludes distance 11 for [27,10], since
11+6+3+2+1+1+1+1+1+1=28>27. Its distance is at most ten, and repetition gives at
most 70. This applies to every choice of the nonzero field scalars, even before
adding other degree-six components. The finite pair exclusions are consistent
but redundant for these eight edges. The tests retain period/rank controls.

This use of [Griesmer's inequality](https://doi.org/10.1147/rd.45.0532) is prior
mathematics. Standard CRT background is described by Güneri, Ling and Özkaya,
[Quasi-Cyclic Codes, Sections 2–3](https://arxiv.org/html/2007.16029v2). The present
specialization and finite evidence are author deductions, without a novelty claim.

## Exactly what remains

Removing 0x49 leaves eight factors. Forbidding the additional 0x57/0x75 edge leaves
choose(8,3)-6=50 triples per profile, from the original 84. Thus 34 triples per
profile are excluded. The 50 surviving triples pass this necessary pair test only:
individual pair certificates need not be mutually compatible in a three-field
code, and full dimension-22 distance can be smaller than all pair distances.

The result does not establish the existence of a target code in any remaining
triple, exhaust its six scalars, bound profile A, classify unrestricted coordinate
equivalence or prove an unrestricted optimum. No accepted results are changed.
The next useful question is compatibility of all three pair constraints, followed
by full-code verification only for compatible choices. That is outside this run.

Credit: PR #12's canonical models and specialized profile argument; Seddas,
Shashkov, Viazovska and Abbe for the inherited parent construction; project
reconstruction and both spectrum checkers; standard CRT/Griesmer theory; and the
earlier structured handoffs and PRs #10/#11 for explicit witness/orbit methods.
