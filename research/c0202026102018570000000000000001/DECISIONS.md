# Decisions during the timed run

- 18:57:48 UTC — begin. Preserve the existing frontier and evaluate contributor
  experience, not just search throughput.
- About 19:00 — shortest-word supports immediately eliminate most two-column
  replacements. Complete this audit with independently checked local obstructions.
- About 19:02 — implement Walsh scoring of all possible replacement columns.
  This changes the search method, not the certificate standard. Pair wall budgets
  and starting seeds; retain CPU times because host load varies.
- About 19:03 — the original QC donor card is structurally impossible: its
  [45,14,16] parent is doubly even, so an improved 11-dimensional subcode would
  need d>=20, requiring length>=46 by Griesmer. Retire that specific search.
  Replace it with index-four, block-size-11 QC constructions with odd row weight.
- About 19:05 — an optimized [45,11,16] matrix has 20 minimum words rather than
  247. Try exact three-column repair on this more promising weak-word set.
- About 19:07 — all 14,190 triples processed, 1,046,103 column pairs considered,
  no repair. This negative search is not backed by a separate proof checker.
  The two-column audit, by contrast, has per-pair independently checked artifacts:
  all 20,854 pairs over the sixteen published starting witnesses are blocked.
- About 19:08 — for odd-distance codes, retain the even-weight kernel and search
  its other coset. This preserves useful structure while allowing many coordinates
  to move together. Evaluate this separate intervention alongside QC search.

These are adaptive, exploratory decisions by one agent-assisted contributor.
Paired starts and budgets help compare algorithms; this is not a randomized
experiment establishing that an LLM outperforms human contributors or all solvers.
