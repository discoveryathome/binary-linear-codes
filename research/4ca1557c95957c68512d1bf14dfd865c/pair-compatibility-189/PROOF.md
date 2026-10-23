# Conservative pair constraints and the scope of the capped full-code result

All evidence is author-checked by one AI session. The exact finite statements
below do not constitute a full B/C exclusion, a new code record or an unrestricted
bound. Independent mathematical review of the normalization remains open.

## Explicit models and the necessary filter

Use the canonical B/C low constituents of PRs #12/#13, three cyclic blocks of
length 63, and three distinct degree-six field lines (1,f_i,g_i), with every scalar
nonzero. The low part has binary dimension four and each field line adds six,
giving rank 22. Every codeword has even total weight, so distance >=73 requires
distance >=74. Row formulas are retained in model.py and the earlier fixed tasks.

Any two field lines plus the low part give a rank-16 subcode. If it has a nonzero
word of weight <=72, the full code is excluded from the threshold. Conversely,
passing every pair test does not prove the full code reaches 74: words using all
three fields may be lighter.

The first stage exhausts all 3,143,448 rotation-normalized pair choices. Its binary
table stores a nonzero 16-bit message and weight for each exclusion, or zero/zero
for an allowed choice. Independent replay verifies every excluded word directly.
It deliberately treats every zero marker as allowed, without relying on the
primary kernel's full enumeration to certify a lower bound. Thus the replayed
filter has no false negatives: any actual target code must survive every edge.
Extra allowed edges can only enlarge the subsequent join.

The completed tables contain 2,627,208 exclusions and 516,240 allowed entries.
The field-unit rotation actions are checked from physical coordinate rotations
in the direct replay; every orbit and all short periods are included. Three-step
block rotations fix the period-three low words, so quotienting each pair by
independent rotations of blocks two and three preserves distance. Orbit counts
189/567 and the full Cartesian domains are the same fixed domains as PR #13.

## Full-code normalization

A full assignment can be written as three vertex states (f_i,g_i), each in
GF(64)* squared, with state index (f_i-1)*63+(g_i-1). Expand every allowed pair
representative through its two independent physical rotation orbits to obtain a
relation on its two vertex states. A full target must be a triangle in all three
relations, since each of its pair subcodes must avoid the certified low words.

The new tables independently have empty relations on the nine pairs excluded in
PR #13 for each profile. Any triple containing one of these edges is excluded.
The remaining 50 triples per profile each contain a degree-six factor of order 63.
Indeed the only nonprimitive factors are 0x49 (order nine) and 0x57/0x75 (order 21);
triples without a primitive factor contain an empty pair relation.

Choose the smallest order-63 factor in a remaining triple as root. Multiplication
by x^3 has order 21 on every nonzero scalar of that field. Independent rotations
of blocks two and three act freely on the root's f and g scalars. Normalize each
to the least value in its 21-element orbit, leaving three possibilities each,
or nine root states. The two other vertex states remain arbitrary units.

Every global rotation orbit has exactly one representative with those normalized
root scalars: the required shifts are unique modulo 21, and 21 three-step shifts
are a full 63-step rotation on every block. No other code equivalence is used.
Without pair filtering, each surviving triple therefore has 9*63^4=141,776,649
root-normalized assignments, 14,177,664,900 over the 100 templates. These are
parameter counts, not inequivalent-code counts.

## Exact allowed join and the capped prefix

For each root state, take its allowed neighbors in the other two fields and
intersect their pair relation. The primary kernel enumerates assignments in the
fixed order of TASK.md. A separate Python implementation reconstructs relations
from physical rotations, enumerates the tested prefix and counts the full join
using bitset population counts. A separate C++ count-only program, importing no
primary source, uses repeated GF(64) shifts and agrees on all 168 template counts.

The complete conservative allowed join contains 499,193,136 root-normalized
assignments: 354,086,700 in B and 145,106,436 in C. All 100 nonexcluded factor
triples have nonempty joins; pair compatibility eliminates no additional factor
triple. This count is exact for the stored allowed relations. The replay's sound
use of those relations does not require independently certifying every allowed
pair's distance.

The full-code pass stopped at the fixed 2,000,000-check cap. It tested only a
prefix of template 7: B, factors 0x43/0x57/0x5b, root 0x43. This template has
6,414,192 allowed assignments. Every tested full assignment has a separately
replayed nonzero word of weight <=72. Their exact minimum distances were not
enumerated. The 2,000,000 rejections therefore certify only this prefix, leaving
497,193,136 allowed assignments unchecked overall (4,414,192 in template 7).

The retained summary correctly says complete=false, target_found=false. The
replay rejects false completeness flags, missing/extra/changed assignments, false
target flags, incorrect word weights or zero messages, and wrong source/seed pins.
No extra full-code evaluations were performed during the count-only audit.

## What remains and credit

No whole B/C distance bound follows from this capped prefix. Profile A, the
untested allowed assignments, exact minima/multiplicities of rejections,
unrestricted code equivalence/optimality and literature novelty remain open.
The general statement that eligible three-block codes reduce to A/B/C still
depends on PR #12's author-checked argument; this package directly concerns the
explicit canonical B/C models. No accepted result or frontier is changed.

A useful next session can first review/replay the tables and normalization, then
choose a fixed domain using the count map. The smallest untested allowed joins
are C factors 0x43/0x6d/0x73 and 0x5b/0x61/0x67, each 201,912 choices. These counts
do not predict their distances. Any resumed construction requires its own bounded
claim and must retain explicit words or both full target spectra.

Credit the canonical models and primary mechanics from this same session's
PRs #12/#13, the earlier handoffs and explicit-witness methods of PRs #10/#11,
standard CRT theory, the project reconstruction/checkers, and Seddas, Shashkov,
Viazovska and Abbe for the published parent. Separate implementations and fresh
clones are author checks, not independent human review or a formal proof.
