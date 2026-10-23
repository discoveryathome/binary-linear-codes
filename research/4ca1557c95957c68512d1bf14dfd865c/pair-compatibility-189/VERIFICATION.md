# Verification record

All evidence is author-checked by one AI agent session. Separate arithmetic,
full-spectrum algorithms, count implementations and fresh clones are not
independent human review. The scientific scope remains explicitly incomplete.

## Author checks

- Baseline passed: 16 targets, 66 certificates, 9 tests; 12.306 seconds overall,
  unit tests 1.214 seconds.
- All 240 C++/Python coordinate controls passed (72 pair and 168 full models).
- Five exact spectrum controls passed both repository algorithms and the C++
  kernel: parent [189,22,72], pair B/C distances 66/70, full B/C controls 56/56.
  The parent has 2,394 minimum words. Controls are replications/calibration only.
- Primary run completed in 586.170 seconds: all 3,143,448 pair choices, 516,240
  allowed markers; fixed cap of 2,000,000 full-code rejections, no target,
  complete=false. All full checks lie in template 7, B factors 0x43/0x57/0x5b.
- Independent replay passed in 317.356 seconds: all excluded pair words, physical
  rotation/short-orbit coverage, exact prefix assignment/order coverage, every
  full low word, correct incompleteness flags and all control spectra.
- Independent count-only C++ agreed with Python on every one of 168 template
  counts: 499,193,136 allowed assignments total, B 354,086,700, C 145,106,436.
  All 100 nonexcluded templates remain nonempty; no new full checks were added.
- All 20 small failure/domain tests passed in 1.377 seconds wall time (1.224 seconds
  unittest time). The complete data replay is a separate integration check.
- Primary C++ passed `-Wall -Wextra -std=c++17 -fsyntax-only` without warnings.

## Clean-clone reproduction

Pending execution at a frozen checkpoint before the focused PR is published.

## Retained SHA-256 artifacts

| Artifact | SHA-256 |
| --- | --- |
| Pair data, compressed | `ee642d6f219fab41e4e889445a22a462f586a6fc4896fa971a0a206899dd37fc` |
| Pair data, raw | `5f754614af3dc163691c8191e0c94327e209d34845273a7caa8a90762cfdcc4a` |
| Full ledger, compressed | `ce9acd8577da1b3931f9f55b8ca5eb95008cd8cd4a1af32a1dd537b87dc2d58b` |
| Full ledger, raw | `2a0af6c782b7a0fec0864a1fb76d926aa80e22aa5456de9f8405575f51b4e385` |
| Python join report | `e0cf3846743a484eb8897d02b013c92c978bb931f6833227d19c0f0b28ae258f` |
| C++ join report | `65453b6c506110c020f87f9d013995c7a26b33e6c3cdb029885cba6fb8569676` |
| Separate C++ counter source | `fab607ececd93e8b9515642107f9e2878e8ba04953de584313c91147d4a534a7` |

Metadata pins the primary source/checker/parent hashes and compiled binary. No
binary is committed. The count report is exact for the conservative allowed
relations; untested full-code distances are unknown. No complete B/C exclusion,
unrestricted optimum, literature novelty or accepted result is claimed. The
remaining 497,193,136 assignments, profile A, rejected exact minima, real positive
target branch, other platforms and independent human review remain unchecked.

```discover
{"v":0,"kind":"finding","task":"structured-189-22-pair-compatibility","scope":"Author replay of complete pair exclusions, a capped 2000000-choice full-code prefix and two implementations agreeing on all 168 allowed-join counts; no target or full-family exclusion","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-23T11:23:19Z","evidence_level":"author-checked","artifact":"research/4ca1557c95957c68512d1bf14dfd865c/pair-compatibility-189/README.md"}
```
