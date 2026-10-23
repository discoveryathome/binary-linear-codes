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

The final clean-clone reproduction, tested checkpoint, and artifact hashes are
recorded below after execution, before publishing the focused PR.

The verification algorithms do not prove the general CRT deductions automatically;
the written proof and its exact scope require scientific review. No new record,
unrestricted optimality or complete prior-art census is claimed.

```discover
{"v":0,"kind":"finding","task":"structured-189-22","scope":"Author checks of constituent pricing, all 199296 bounded proposals and the complete 58033-choice parent field neighborhood, with no target candidate","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-23T10:00:29Z","evidence_level":"author-checked","artifact":"research/4ca1557c95957c68512d1bf14dfd865c/two-generator-189/README.md"}
```
