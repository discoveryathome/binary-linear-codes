# Extracted source data

The checks read these facts instead of the third-party pages they come from. The pages
carry no open license and are not redistributed; `data/source-index.json` cites each one by
URL, retrieval date and SHA-256 (`"stored": false`). Every record here repeats that source
block, and `scripts/reproduce.py` checks it against the index.

| File | Facts | Source and credit |
| --- | --- | --- |
| `codetables-bounds.json` | `[n, k, lower, upper]` for all 32,896 binary cells, n, k ≤ 256 (closure and upper-bound audit) | Full GF(2) table, [codetables.de](https://www.codetables.de), maintained by Markus Grassl |
| `codetables-recipes.json` | Construction steps for the 58 archived cells (n ≤ 70, 9 ≤ k ≤ 12), keyed `n_k`: step index, `[n, k, d]` and the recipe line the importer reads (operation, parameters, stored matrix) | Per-cell codetables.de pages; the original authors of each construction are credited on its page |
| `yu2024-triples.json` | The 68 `[n, k, d]` triples displayed in the paper, used as conservative closure seeds | Cong Yu, Shixin Zhu, Hao Chen, Yang Li and Xiuyu Zhang, "New record-breaking binary linear codes constructed from group codes", [arXiv:2412.15551v1](https://arxiv.org/abs/2412.15551v1) |

`scripts/extract_sources.py` produced these files on 2026-10-21 from the 2026-10-20
snapshots, using the same parsers the checks used before (`closure.parse_table`,
`closure.parse_triples`, `reconstruct.page_steps`). To refresh, fetch the pages to the paths in
the source index and rerun it.

Equivalence check at extraction: the old code path (parsing the HTML) and the new one
(reading these files) gave byte-identical output for the full closure replay, the 32,896
table bounds, and the reconstruction of all 58 recipes (matrices, steps and deferral
reasons). Rerunning `scripts/closure.py`, `scripts/reconstruct.py` and the trial's
`family_proof.py` on the extracted data reproduced `results/closure.json`,
`data/targets.json`, `results/reconstruction-audit.json`, every `certificates/baseline_*.json`
and the trial's QC-parent certificate byte for byte.
