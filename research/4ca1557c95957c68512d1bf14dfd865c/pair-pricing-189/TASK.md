# Fixed question: can pair subcodes exclude a B/C template?

Seed `4ca1557c95957c68512d1bf14dfd865c`, drawn card structured-189-22.
Base `76267c387538b4fb0e802278530b575bab4d1f76`.
[Claim](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19143956).
User grant: 480 minutes total, multiple focused PRs and coordination posts allowed.
New research cutoff 12:00 UTC; final 120 minutes reserved for verification/handoffs.

PR #12 gives canonical low constituents B/C of binary rank four, at three cyclic
blocks of length 63. Add two distinct degree-six field lines, with nonzero entries
normalized to (1,f_p,g_p) and (1,f_q,g_q). This gives binary rank 16. Each full
dimension-22 B/C code contains the three subcodes obtained by omitting one field.
Consequently an upper bound <=72 for any selected pair excludes a full code with
that pair from distance >=74. Both profiles have even total weights.

For every profile and every unordered pair of the nine degree-six factors, decide
whether any such rank-16 subcode has distance >=74. Stop a case at the first exact
threshold survivor, keeping its matrix and both full spectra. If none survives,
exhaust its entire domain and retain a nonzero word of weight <=72 for each choice.
This is threshold pricing, not maximization of pair distance or a construction
search at dimension 22. No additional heuristic or full-code pivot is included.

## Domain and symmetry

Let M=x^63+1 and G_p=M/p. The low rows are:

- B: (G_7*x^j,0,G_7*x^j), (0,G_7*x^j,G_7*x^j), j=0,1.
- C: (G_3,0,G_3), (0,G_3,G_3), (G_7*x^j,G_7*x^j,G_7*x^j), j=0,1.

Here subscripts 3/7 encode x+1 and x^2+x+1. For each p add the six rows
(G_p*x^j,G_p*f_p*x^j mod M,G_p*g_p*x^j mod M), j=0..5.

Independent rotations of blocks two and three by three positions fix every low
row, since their periods divide three. They multiply (f_p,f_q), respectively
(g_p,g_q), by (x^3 mod p,x^3 mod q). Represent each orbit of the 63^2 nonzero
symbol pairs by its smallest packed integer a+64*b. Sort representatives and
enumerate their Cartesian square in that order. Short orbits are included exactly.

There are 189 representatives except for the pair 0x57/0x75 (both order 21),
which has 567. Thus the maximum domain across both profiles is
2*(35*189^2+567^2)=3,143,448 normalized choices. These are parameter choices,
not inequivalent-code counts. The order and cap are fixed before computation.

## Evidence and stopping rules

Freshly compile a C++17 Gray enumerator as an accelerator. Every early rejection
must retain a nonzero message and exact word weight <74; these are upper bounds,
not exact distances. A survivor requires all 65,535 nonzero words, then separate
Python checks and both repository full-spectrum implementations. Keep exact
parameters, source/compiler hashes, all tested prefix choices and elapsed times.
Use no randomness; the original seed identifies this deterministic continuation.

Separate replay must reconstruct cyclic words without importing the primary
model, verify all orbit coverage/short periods, check each rejected word, ensure
each case stops only at its first survivor or exhausts all representatives, and
match survivor spectra and ranks. Failure controls must catch zero messages,
changed weights, omitted choices/cases, invalid orbit representatives, false
survivor claims and source/provenance mismatch.

If a pair is excluded, compute the remaining eligible triangles of the nine-factor
graph for each profile. If all pairs have threshold survivors, report explicitly
that pair-based threshold bounds eliminate no triple. Individual pair survivors
need not be mutually compatible in a three-field code. Do not infer existence of
a [189,22,74] code, general impossibility, a new record or literature novelty.

Credit PR #12's specialized models and canonical low constituents, standard CRT
theory, the repository's checkers, Seddas/Shashkov/Viazovska/Abbe's published parent,
and preceding structured handoffs/PRs #10/#11. All current evidence is author-checked
by one AI session. Independent mathematical review remains open.

```discover
{"v":0,"kind":"claim","task":"structured-189-22-pair-pricing","scope":"Threshold pricing of 72 rank-16 B/C low-plus-two-degree-six cases, at most 3143448 rotation-normalized choices, stopping each case at its first distance-74 survivor","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-23T10:39:06Z","evidence_level":"author-checked","seed":"4ca1557c95957c68512d1bf14dfd865c","expires_at":"2026-10-23T12:15:00Z","artifact":"research/4ca1557c95957c68512d1bf14dfd865c/pair-pricing-189/TASK.md"}
```
