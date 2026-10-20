# Timed contributor trial

Started 2026-10-20 18:57:48 UTC. Budget: 30–60 minutes wall time, including orientation,
implementation, experiments and validation. LOCAL; no external submissions.
Base commit: f7e33cc1680b7e31f5f167f8320bab535d2c0515.

Question: can a fresh, agent-assisted contributor make worthwhile progress on this
frontier within one sitting, and would that progress support a public flagship?
This is one assisted contributor session, not an estimate of a population success rate.

The protocol task draw with seed c0202026102018570000000000000001 selected replay.
Replay passed: 66 certificates, 16 targets, seven test groups, 65.26 seconds.
We deliberately continue with structured search (columns and QC cards), as required
by the user's explicit request to test discovery and hill climbing.

Initial scope: [52,10], [45,11], [42,12], [62,11], all already audited against
published bounds and transformation closure. Retain the other twelve targets as
structural negative controls. Do not change the published frontier.

Planned comparisons:

1. Ordinary bit/column mutation hill climbing from random and published matrices.
2. An agent-designed search using weakest-word constraints and fast Walsh
   transforms to optimize a replacement column, plus controlled perturbations.
3. Structured subspace selection inside the published [45,14,16] QC parent.
4. Exact obstructions to improving fixed witnesses by replacing at most two columns.

Record proposal/work counts as well as wall and CPU time: shared host load is
substantial. A Walsh sweep considers many column alternatives, so a sweep is
not one ordinary proposal. Use matched search time/work where feasible, and
label unequal/adaptive comparisons as exploratory.

Progress categories, never combined:

- new construction exceeding the literature/closure exclusion;
- rediscovery or replication of a known distance;
- improved secondary search objective (not a distance record);
- new reusable algorithm, certificate, or bounded negative result.

All reported final/milestone matrices must pass both existing exhaustive checkers.
No failed search establishes global optimality. A transformation of a published
parent retains that provenance, even if its distance is useful.

Public demo should show guaranteed correctable bit errors floor((d-1)/2), a
visible published frontier, and the actual run trajectory. It must not relabel
training gains or fewer minimum words as scientific discoveries.
