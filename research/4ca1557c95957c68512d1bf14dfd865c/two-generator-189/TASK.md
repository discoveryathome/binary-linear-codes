# Two-generator CRT families at [189,22]

Seed `4ca1557c95957c68512d1bf14dfd865c`; base
`76267c387538b4fb0e802278530b575bab4d1f76`. The repository picker was executed again
and returned the original `structured/structured-189-22` card. Its inherited
[189,22,72] positive control passed both exhaustive spectra, with 4,194,304 words and
2,394 minimum words. Goal remains distance at least 73, subject to fresh exclusion
reconciliation before any record claim.

The user corrected the total budget to 480 minutes from about 06:00 UTC and permits
multiple focused PRs. This round's new research stops by 11:30 UTC, with a global
research cutoff 12:00 and final verification/handoffs through about 14:00 UTC.
No merges, accepted-result edits, submissions, or direct author outreach.

The canonical integer seed, computed by Python from the hex string, is
`101859021349280159657904260309176911452`. The first starter invocation accidentally
used `101137681567107069320642249479418431004`; its 16 null proposals are preserved
as auxiliary `starter/` data. The correct canonical control is `starter-seeded/`.
Task selection used the original hex seed throughout. The 199,296-proposal cap below
applies to the new model, not these separate starter controls.

A fresh focused table retrieval returned lower 71 and upper 81 (source page's
displayed change date 30 December 2011). Retain the stronger published paper
distance 72 as the exclusion baseline; the table's lower value does not reduce it.

## Fixed question and domain before new computation

Can two-generator CRT profiles, outside the inherited injective one-block
representation, reach [189,22,73]? Establish the necessary high-distance constituent
profiles, price the small invariant subcodes first, then run a bounded seeded
experiment only if the favorable bounds leave room.

Use three cyclic blocks of length 63. The proposed profiles have three distinct
degree-six constituents, each a field line with three nonzero entries, and one of:

- B: no degree-one/three constituent; a degree-two field plane of dimension two,
  normalized to a+b+c=0 over GF(4).
- C: a degree-one binary even-parity plane and a degree-two field line normalized
  to (1,1,1); no degree-three constituent.

Each has binary dimension 4+3*6=22. They have first-block ranks 20 and 21 respectively,
so differ from the inherited one-generator model of block-projection rank 22.
There are 84 degree-six factor triples. For each profile/triple, allow six nonzero
GF(64) scalars f_i,g_i in 1..63. No complete enumeration of 2*84*63^6 is claimed.

Let M=x^63+1, G1=M/(x+1), G2=M/(x^2+x+1), and Gp=M/p for each chosen degree-six p.
Profile B low rows are `(G2*x^j,0,G2*x^j)` and `(0,G2*x^j,G2*x^j)` for j=0,1.
Profile C low rows are `(G1,0,G1)`, `(0,G1,G1)`, and `(G2*x^j,G2*x^j,G2*x^j)` for j=0,1.
For each p add six rows `(Gp*x^j,Gp*f_i*x^j mod M,Gp*g_i*x^j mod M)`, j=0..5.

## Fully charged favorable case and finite pricing

Both rank-four low constituents have distance 84, above target 73. Verify this
with their exact small matrices before a construction search. Check the complete
factorization, binary rank, shift invariance, and constituent dimension profiles.
Price each degree-six constituent over every scalar pair; a maximum below 73
excludes that factor. Price degree-six pairs when useful before full searches.
Stop a line that fails the target even in its favorable constituent bound.

Derived parity observation: both B and C contain only even-weight words. B has no
degree-one constituent, so every block is even; C's degree-one plane imposes even
total block parity. Thus meeting distance >=73 in these profiles requires distance
at least 74. The scientific target is unchanged and the favorable cap 84 still
leaves room; no smaller multiplicity or distance-70/72 result will be called an
improvement over the published parent.

The proposed necessary aggregate profiles for any distance-73 three-block QC code
are A=(e1,e2,t3,t6)=(1,0,1,3), B=(0,2,0,3), C=(2,1,0,3). This is a hypothesis to
verify by the CRT/projection and small-code arguments, not an accepted classification.
The existing parent has profile A. See the session's round3/PLAN.md for the proposed
derivation; publish only arguments and finite checks that survive validation.

## Bounded experiment if pricing leaves room

Retain the card's existing 16-proposal control. Then use an explicitly recorded
PRNG derived from the original seed for a maximum of **199,296 proposals**:
16 initial samples for each of 168 profile/triple templates (2,688), followed by
3 restarts of 4,096 proposals for each of the 16 strongest templates (196,608).
Order equal fitness deterministically. Mutate one to three of the six nonzero
field scalars, recording every proposal, duplicate, rejection witness or exact
fitness, and acceptance. Lexicographic distance then minimum-word count may guide
search; only distance >=73 meets the scientific goal.

An optional freshly compiled C++17 CPU enumerator can accelerate exact enumeration.
Never execute a committed binary or install globally. Its row construction and
enumeration must be compared with Python controls, including the inherited parent.
All final artifacts remain replayable with Python and both existing spectrum
implementations. A nonzero low-word witness may reject an unpromising proposal;
do not label an early rejection's bound as its exact distance.

Stop early on a verified target candidate, a complete invariant-subcode obstruction,
or the fixed research clock. Otherwise the negative result is only about the exact
tested list. Preserve all unsuccessful runs and exact parameters. Any positive
candidate requires fresh closure/literature, equivalence/provenance review, and
expert review before any record claim; accepted results remain untouched.

## Overlap, scope, credit, and falsification

No [189,22] claim or PR was present in the refreshed coordination channel. Open
PRs #7–#11 address other objects or the two-block [172,21] obstruction. This changes
the representation and question within the drawn card, not merely its seed.

Credit Seddas, Shashkov, Viazovska and Abbe for the published control; the repository
for reconstruction and both exhaustive checkers; the cited CRT mathematics; prior
handoffs and PRs #10/#11 for developing the constituent/witness methods. All new work
is author-checked by one AI agent session.

Falsifiers include a missing constituent profile, a rank or invariance failure,
an incorrect favorable bound, disagreement with either full spectrum, a target
candidate already covered by fresh exclusions, or unverifiable search coverage.

## One bounded pivot after the completed B/C experiment

The B/C run completed all 199,296 proposals, covering 163,272 distinct parameter
choices; both best distances were 70. A separate direct replay checked all witnesses
and both attaining sample spectra. This does not rule out the unsearched B/C family.

Pivot to the inherited profile-A parent using field-scalar coordinates. Fix its
degree-three factor, its three degree-six factors, and its all-ones degree-one line.
Normalize its degree-three line to (1,1,1) by independently rotating blocks two and
three, preserving distance and checking row-space equality. The six degree-six
scalars are nonzero GF(64) elements. Exhaust every replacement of zero, one, or two
of those six scalars by any other nonzero value: `1+6*62+15*62^2=58,033` choices.
This is a complete finite neighborhood, not an exhaustive search of profile A.
Target remains distance >=73. Retain an explicit nonzero word for every failed
choice, and verify any survivor by both full spectra. The inherited normalized
parent is the positive control. New research still stops by 11:30 UTC.
