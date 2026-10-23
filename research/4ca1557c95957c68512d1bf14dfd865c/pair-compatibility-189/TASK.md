# Fixed question: complete pair constraints and compatible full codes

Seed `4ca1557c95957c68512d1bf14dfd865c`, drawn structured-189-22 card.
Base `76267c387538b4fb0e802278530b575bab4d1f76`.
Continuation of PR #13's pair-compatibility handoff and PR #12's canonical B/C models.
[Claim](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19144349).
The donor explicitly authorized multiple focused PRs and corrected the total
budget to 480 minutes. New research cutoff 12:00 UTC; verification/handoffs through
about 14:00 UTC. No accepted-result edits, merges, submissions or outreach.

## Fixed domain and evidence

First enumerate all 3,143,448 rotation-normalized rank-16 pair choices (72 cases)
from PR #13's domain. Save each rejection's nonzero 16-bit message and exact weight
<74; save zero message for each unexcluded choice. Independent replay treats all
unexcluded choices as allowed, without needing to prove their exact pair distance.
This makes the filter conservative: every code capable of distance >=74 survives
each edge, while extra allowed edges can only enlarge subsequent work.

For each profile and each sorted triple of distinct degree-six factors, join all
three allowed pair relations on states (f_i,g_i) in GF(64)* squared. A pair with
no allowed choices excludes its triple. All remaining triples have a primitive
order-63 factor: choose the smallest such factor as root. Independent rotations
of blocks two and three by multiples of three act freely on each root multiplier
with period 21. Normalize each root multiplier to the least value in its orbit,
giving 3*3=9 root states. Other multipliers remain arbitrary nonzero scalars.

Order: profile B then C; sorted factor triples; ascending root f then g; ascending
state index (f-1)*63+(g-1) on the other factors in sorted order. For each compatible
assignment, evaluate the full rank-22 code against threshold 74, saving a nonzero
message and exact low-word weight. Stop globally at a target survivor or after
2,000,000 full-code evaluations. If any cap/cutoff is reached, mark incomplete and
report only the tested prefix. Do not infer a complete family bound.

The replay also counts the entire allowed join using bitset population counts,
without evaluating additional full codes. Retain that deterministic count as a
diagnostic of the remaining work. It does not increase the full-code cap and does
not certify the distances of the untested compatible assignments.

Without pair filtering, each of the 100 triples surviving PR #13's edge exclusions
has 9*63^4=141,776,649 root-normalized assignments. That is 14,177,664,900 possible
assignments across these templates, not an inequivalent-code count. This run
does not brute-force that number; it uses exact necessary constraints and verifies
the resulting join coverage. All other triples must be excluded by a recorded
empty pair relation, rather than an assumed result from another PR.

## Verification and stopping

Fresh C++17 accelerator, no committed binary. Primary model and direct replay
use separate arithmetic. Replay all pair low words and physical rotation orbits,
rebuild allowed relations, independently enumerate the normalized join and match
every tested full assignment and its word. Check root normalization, source and
artifact hashes, cap/completeness flags, and corruption/domain controls. A target
survivor requires both existing full-spectrum checkers and fresh source review.
Do not call same-session algorithms independent human review.

If complete and negative, the exact conclusion concerns only the canonical B/C
models. The wider necessary-profile argument remains author-checked in PR #12;
profile A, unrestricted binary codes, coordinate-equivalence classification and
literature novelty are outside this question. No family bound follows from a
partial join, and a pair-table allowed flag is not itself a certified lower bound.

Credit the published parent authors Seddas/Shashkov/Viazovska/Abbe, repository
reconstruction/checkers, standard CRT/Griesmer theory, preceding structured sessions
`aac390866c59afee7d645224e629b13b` and `a981e1a3197e2c924de70ed18d8e8ea8`, and
PRs #10–#13. Reused primary mechanics retain same-session provenance explicitly.

```discover
{"v":0,"kind":"claim","task":"structured-189-22-pair-compatibility","scope":"Complete 3143448-choice pair tables and deterministic compatible full-code join, capped at 2000000 full-code checks; no universal claim if incomplete","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-23T11:00:00Z","evidence_level":"author-checked","seed":"4ca1557c95957c68512d1bf14dfd865c","expires_at":"2026-10-23T12:15:00Z","artifact":"research/4ca1557c95957c68512d1bf14dfd865c/pair-compatibility-189/TASK.md"}
```
