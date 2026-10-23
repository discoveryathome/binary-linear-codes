# Verification record

Evidence: **author-checked**, one AI agent session. Independent scientific review
of the CRT completion and exact computational scope remains open.

## Author checks

- Fresh upstream base: `76267c387538b4fb0e802278530b575bab4d1f76`; instructions and
  executable code match the previously screened base. No agent settings or install
  hooks were present.
- Baseline reproduction: PASS, 16 target rows, 66 certificates, and 9 tests.
- The inherited [172,21,66] generator was stripped of its final two coordinates.
  Its [170,21,64] matrix matched the polynomial model exactly; Gray and separate
  subset-halves spectra agreed.
- The complete normalized domain finished in 104.670 seconds: 45 degree-21 divisors,
  94,371,840 core parameter choices, and no distance-65 survivor.
- Direct replay reconstructed 31,536 restricted and 207,360 full nonzero witnesses,
  checked complete factorization/orbit/lift coverage, and confirmed maximum weight
  64. The same replay checked both attaining parent spectra; total 9.491 seconds.
- All 17 tests passed in 18.118 seconds, including coordinate models, shorter
  rotation orbits, corrupted artifacts, and the finite axis/projection cases.
- The initial uncompressed search gave identical witness families. Compression
  reduces the retained manifest from about 4.14 MB to 998,266 bytes.

## Clean-clone verification

The final clean-clone replay and source hashes are recorded here after execution,
before publishing the focused PR.

## Exact retained evidence

- Compressed manifest SHA-256:
  `9623f0c7bd3beb60b9ecf6bf4a352a512d4a70c0c60e47ae7397aa74f3e39ee0`.
- Deterministic witness-family SHA-256:
  `4bfd7696bc2affdac26b143ff68d2fae116a8f7601cb8727cd5548a9b1dae2f9`.
- Both parent matrices, the retained core spectrum, and the primary computation's
  exact source hashes are in `run/`.

General Griesmer and CRT proofs were not re-proved from axioms. The needed CRT
specialization is written out in PROOF.md, with its dimension and integer-bound
calculations checked. No fresh record-table/literature reconciliation or independent
human acceptance is claimed. Python 3.13.5 was the exercised runtime.

```discover
{"v":0,"kind":"finding","task":"structured-172-21-core-family","scope":"Author verification of the full normalized core witness bound and attaining parent spectra; CRT projection argument remains subject to scientific review","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-23T07:37:02Z","evidence_level":"author-checked","artifact":"research/4ca1557c95957c68512d1bf14dfd865c/core-family/run/result.json.gz"}
```
