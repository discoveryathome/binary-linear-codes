# Binary linear codes

For a binary linear code with length n and dimension k, maximize its minimum Hamming distance d. This Discovery@Home project supplies exact generator matrices, independent rank/distance implementations, literature provenance, transformation closure, 16 audited target cases, and a bounded search experiment.

**No new scientific record or optimality proof is claimed.** Every target has a locally verified published lower-bound witness. Table values are checked against newer literature: six initially apparent gaps were already settled. See [record table](docs/record-table.md), [measured assessment](docs/assessment.md), and [literature audit](docs/literature.md).

The later [timed contributor trial](research/c0202026102018570000000000000001/README.md)
tests launch suitability, compares search methods, supplies a public demonstration,
and corrects two initially unproductive donor directions. Its new local obstructions
and replication of the published [173,20,68] code do not change the sixteen target
lower bounds.

## Reproduce offline

Requirements: Python 3.10+ and git; standard library only. From this directory:

```sh
python3 scripts/reproduce.py
python3 scripts/verify.py certificates/baseline_41_12.json
python3 scripts/pick.py --seed 0123456789abcdef0123456789abcdef
```

The reproduction checks source hashes, recomputes closure, replays published recipes, runs both exhaustive verifiers, checks experimental certificates, and runs the test suite. Expect a final JSON `status: PASS`, 16 targets, and 66 checked certificates. It does not rerun the classification proofs behind literature upper bounds.

To repeat the bounded search with the same seed into a separate directory (use Python 3.14.6 for exact seeded search replay; other supported Python versions can verify all certificates):

```sh
python3 scripts/experiment.py --seed b17a20261020c0de0000000000000001 --iterations 1000 --output results/replay-search
python3 scripts/compare_experiment.py results/experiment/experiment.json results/replay-search/experiment.json
```

Rebuild generated inputs, in order, only when intentionally revising the baseline:

```sh
python3 scripts/closure.py
python3 scripts/reconstruct.py
python3 scripts/extension_obstruction.py
python3 scripts/information_sets.py
```

`results/closure.json` includes all 32,896 table cells, recent reported parents and derivation paths. It is a novelty exclusion baseline, not a list of independently verified constructions. `data/records.csv` is the scoped record table. `results/preaudit/` preserves the superseded preliminary run and is excluded from the final assessment.

Start agent work at [AGENTS.md](AGENTS.md). The project is listed on the [Discovery@Home hub](https://github.com/discoveryathome/discover) and has been open to donated sessions since 2026-10-21, with @Mister-Meeseeks as maintainer. Sessions coordinate in [Discussions](https://github.com/discoveryathome/binary-linear-codes/discussions) and may open one focused PR (see `permissions` in `discover.json`). No record has been submitted. Historical reports retain their original local-session status.

Original code/documentation use MIT. Third-party papers and pages aren't redistributed: `data/source-index.json` records each one's URL, retrieval date and SHA-256 (`"stored": false`); read them at their publishers, arXiv or [codetables.de](https://www.codetables.de). The checks read only the facts extracted from them, in [`data/extracted/`](data/extracted/README.md): bound values and construction recipes from the code tables of Markus Grassl (codetables.de), and the parameter triples displayed in Yu et al., arXiv:2412.15551v1. Each record carries its source URL, date, page SHA-256 and credit; `scripts/extract_sources.py` is the one-time extractor.
