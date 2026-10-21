# Research agreement and frontier

We study d_max(n,k), the maximum of min_{m!=0} wt(mG) over full-rank k-by-n matrices over GF(2). The primary progress measure is an increased independently verified construction distance above all applicable published and automatically implied lower bounds. Secondary useful outcomes are corrected literature bounds, reproducible constructions, negative results for explicitly bounded search families, and cheaper exact certification.

The evidence profile is exact-certificate. The current scoped frontier is the 16-row table in data/records.csv. Full witnesses are in certificates/. docs/record-table.md makes the gaps readable. A construction establishes existence, not optimality. Literature upper bounds remain separate and their classification proofs were not replayed.

The question and execution scope follow the user's explicit request. Default license is MIT for original work; third-party content retains its rights. The requester has not been assigned as a maintainer. **No consenting maintainer, no review capacity, and no public donor opening.** This is a reviewable local proposal.

## What is known and what not to rediscover

Read docs/literature.md and docs/closure.md. Apply the finite guaranteed-parameter closure before selecting cases or comparing a candidate. Recent results are conservative exclusions even if this pilot cannot certify them. Published classification corrections remove six initially attractive small cases. The independent reconstruction audit marks unsupported recipes rather than dropping their bounds.

Coordinate permutations and basis changes cannot improve distance. Puncturing loses at most one distance per deleted coordinate when dimension is retained. Shortening imposes zero constraints before deletion; it is not ordinary row deletion. Binary parity extension raises odd distance by one automatically. Subcode selection retains or improves distance but does not earn new-parent credit when it is an automatic consequence of a published construction. Newly computed specific transformations get derived-construction credit and provenance, not inflated record counts.

## Practical bottleneck and tracks

For these cases exact verification is cheap; finding a better matrix is hard. Independent literature checking and reviewer capacity matter as much as candidate generation. The saved warm/cold experiments measure only a modest search budget, not the probability that a general volunteer or another search method will succeed. Cases are not statistically independent: several share parent constructions.

Four tracks total 100: independent verification 25, literature and missing constructions 30, structured search 35, stronger certification 10. The refreshed catalogue includes six larger structured-parent cards; see discover/catalog.json. Every card has a positive control, bounded first experiment, success gate, and overlap terms. Use executed randomness through scripts/pick.py; the pick does not reserve anything.

## Submission and review

Submit a local directory with the generator JSON, seed, source and parent hashes, transformation coordinates or selectors, exact command, candidate budget, environment, elapsed time, and both verifier results. Include the complete weight spectrum for proposed record candidates. Check closure and newer sources again. If d reaches a published upper bound, state the dependency on that bound explicitly; a proof of that bound is a different artifact.

A future consenting maintainer checks provenance and duplicate work, asks an independent contributor to replay the exact certificate, and decides whether the contribution is a replication, derived construction, candidate new parent, or certified upper-bound result. External record acceptance requires the relevant authority; it is not implied by this repository.

Credit original literature authors on every derived code. Credit donor construction/search, software and independent verification contributions separately in a contributor record. No automatic authorship promise. Review capacity, not donated compute, sets the pace; verifier and frontier changes deserve the most care.

## Second-cohort preparation (2026-10-21)

For the refreshed task pool, read [the preparation package](research/readiness-20261021/README.md) and `discover/readiness.json`. These versioned portfolios provide the starting witnesses for the new catalogue cards. They do not retroactively change historical experiments or grant public donor intake.
