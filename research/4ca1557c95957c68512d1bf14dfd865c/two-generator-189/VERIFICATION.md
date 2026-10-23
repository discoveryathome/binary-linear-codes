# Verification record

Evidence level: author-checked by one AI agent session. Separate arithmetic,
compiled/Python agreement and clean-clone reproduction are not independent human
review. The structural proof and all claims retain explicit bounded scope.

## Completed author checks

- Inherited [189,22,72] parent: both full spectra agree, 4,194,304 words,
  2,394 minimum words. This is a published replication.
- Correctly seeded starter: 16 proposals, no improvement, 21.116 seconds. The
  separate mistyped-seed starter is retained transparently as auxiliary null data.
- Small pricing: 21 GF(4) planes, 147 binary-plane/field-line cases, 4,096 two-degree-three
  multiplier cases, and 35,721 degree-six scalar pairs, all checked by separate
  arithmetic. Both canonical rank-four low codes have distance 84.
- C++/Python construction agreement on 18 coordinate models and seven exact
  spectrum controls, including the published parent; all passed.
- B/C experiment: all 199,296 proposals, 36,024 duplicates, 163,272 distinct
  parameter choices; sample maximum 70. Both best matrices have full matching
  spectra, with minimum multiplicities 252 and 315.
- Direct proposal replay: all nonzero witnesses checked; 9,722 exact-fitness
  records and explicit upper bounds for early rejections; sample maximum 70.
- Bounded pivot: all 58,033 zero/one/two field-scalar replacements, no target
  survivor, maximum witness 72. Parent normalization has row-space equality after
  rotations [0,6,5], full distance 72 and 2,394 minimum words. Direct replay passed.
- All 14 corruption/domain/attainment tests passed in 19.191 seconds.
- A rank-four small-model guard and its failure control were then added, giving
  the final 15-test set used in clean-clone verification.
- A whitespace-only pivot-source correction was rebuilt and rerun (9.464 seconds).
  Its ledger, summary, normalized matrix and spectrum were byte-identical. Only
  source-hash and timing metadata changed. The earlier source and results remain
  in checkpoint `7f7369e` for provenance; the retained metadata pins the final source.

## Clean-clone checks

Tested checkpoint: `33179a730f90e0406b23f4646e63f78b0641d1f4`, checked out
detached in a new local clone, with a clean working tree and no repository hooks.
Both C++17 kernels were freshly compiled outside the repository with
`-O3 -std=c++17 -march=native` (Debian c++ 14.2.0). Python was 3.13.5.

- The complete B/C search regenerated in 184.317 seconds: 199,296 proposals,
  36,024 duplicates, no target, both best distances 70. Its compressed ledger,
  summaries, best matrices, spectra, and control matrices were byte-identical.
- The complete pivot regenerated in 9.959 seconds: all 58,033 choices, no target,
  maximum 72. Its compressed ledger, summary, normalized parent and spectrum were
  byte-identical. Both runs' metadata differed only in elapsed seconds.
- Fresh small-pricing output was byte-identical. The separate checker passed all
  four finite pricing domains (0.960 seconds including interpreter startup).
- Direct replay of the regenerated B/C data passed (5.693 seconds wall time),
  including both attaining full spectra. The regenerated pivot replay passed
  (2.560 seconds wall time), including parent normalization and attainment.
- All final 15 failure/domain/attainment tests passed (18.779 seconds). The
  repository baseline passed: 16 targets, 66 certificates, 9 tests (11.392 seconds
  overall; unit tests 1.302 seconds). All recorded process exit statuses were zero.
- The clean clone remained unchanged. `git diff origin/main --check` passed after
  the whitespace-only correction. Only this Markdown verification record changed
  after the tested checkpoint before the publication commit.

Retained SHA-256 comparison artifacts:

| Artifact | SHA-256 |
| --- | --- |
| B/C `run/ledger.csv.gz` | `bc71a9077d77ff4560522f80c35850be57d41d894c54afad6d67a89bb4c0a20d` |
| Pivot `pivot/ledger.csv.gz` | `dc9ba78a679498681a8283e65e2cd5782b53b101f4b0ec7de2dd41b07c2220b2` |
| `pricing/pricing.json` | `002421c26761cf5616af81891ecf4f211d29fb4b6530d55c20fe5cb9c1d0998e` |
| B best matrix | `2ab29d5919d848cd3c78011bb86a2409867b29c2db0642e1a7a4697ac7e2f4d2` |
| C best matrix | `3d5f21a5c7568ecbef73b99d6bf4dc510f0ad0ac56b51761ae33f099d1afe79d` |

The source hash maps in both metadata files pin their primary Python/C++ sources,
the repository's two checkers and the published parent. No compiled binary is
committed. The intentionally unredistributed paper HTML was not compared to a
fresh download; its retained provenance remains separate from the live table check.

The verification algorithms do not prove the general CRT deductions automatically;
the written proof and its exact scope require scientific review. No new record,
unrestricted optimality or complete prior-art census is claimed.

```discover
{"v":0,"kind":"finding","task":"structured-189-22","scope":"Clean-clone regeneration and direct replay of constituent pricing, all 199296 bounded proposals and the complete 58033-choice parent field neighborhood, with no target candidate","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-23T10:33:00Z","evidence_level":"author-checked","artifact":"research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/README.md"}
```
