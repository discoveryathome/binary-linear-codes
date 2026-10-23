# Complete pair tables and a capped [189,22] compatibility prefix

**No target code was found, and the full-code search is incomplete.** The complete
canonical B/C pair filter leaves 499,193,136 root-normalized allowed assignments.
The fixed full-code pass rejected a prefix of 2,000,000, with explicit nonzero
words of weight <=72. **497,193,136 allowed assignments remain unchecked.**

This contribution supplies complete reusable pair tables, an exact compatibility
count map and a verified finite prefix. It does not exclude the full B/C models,
construct a new record or bound unrestricted binary codes. [PROOF.md](PROOF.md)
states the filter, root normalization and exact limits.

## Domain and outcome

- Original seed `4ca1557c95957c68512d1bf14dfd865c`, drawn `structured/structured-189-22`.
- Base `76267c387538b4fb0e802278530b575bab4d1f76`.
- [Claim](https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19144349).
- [TASK.md](TASK.md) fixes all 3,143,448 pair choices and the two-million full-code cap.
- Deterministic continuation of PRs #12/#13; no new random choices.

Every excluded pair choice has a direct low-word certificate. Zero markers are
treated conservatively as allowed by replay, so the filter cannot remove a target
code without a checked witness. The complete tables contain 2,627,208 exclusions
and 516,240 allowed choices. All 240 coordinate controls and five exact spectrum
controls passed, including the inherited [189,22,72] parent.

Independent three-position block rotations give nine normalized root states for
every surviving triple. There are 100 such templates (50 per profile), with
14,177,664,900 assignments before the pair filter. The stored allowed join has
354,086,700 assignments in B and 145,106,436 in C, totaling 499,193,136. All 100
templates remain nonempty. Independent Python and count-only C++ agree on every
template count; neither count alone certifies the untested full-code distances.

The full pass stopped exactly at its cap, within template 7 (B factors
0x43/0x57/0x5b, root 0x43). Its allowed join has 6,414,192 choices; 2,000,000 were
rejected and 4,414,192 remain there. No other template received a full-code check.
Rejection weights are distance upper bounds, not exact minima or a claim that
the tested prefix attains distance 72. No more construction checks followed the cap.

The primary run took 586.170 seconds including controls and packaging. Direct
replay/counting passed in 317.356 seconds. The separate C++ counter matched all
168 counts. These are author-machine timings, not an algorithm-race benchmark.

## Replay and regeneration

From the repository root, Python 3.10+ and only the standard library:

```sh
python3 research/4ca1557c95957c68512d1bf14dfd865c/pair-compatibility-189/replay.py research/4ca1557c95957c68512d1bf14dfd865c/pair-compatibility-189/run
python3 research/4ca1557c95957c68512d1bf14dfd865c/pair-compatibility-189/test_replay.py
```

Expected: PASS, 3,143,448 pair choices, 516,240 allowed, 2,000,000 full words,
499,193,136 allowed join, complete=false, target_found=false,
excludes_full_BC=false; 20 tests pass. Replay emits bounded phase progress and can
take several minutes. The tests exercise corrupt tables, zero/changed full words,
missing assignments, false targets/completeness, wrong seed/source, rank/distance
defects, physical short/root orbits and two tiny independently specified joins.
The full replay is run separately from those small failure controls.

To regenerate, use fresh binaries and new output/report paths:

```sh
mkdir -p ../compatibility-build
c++ -O3 -std=c++17 -march=native research/4ca1557c95957c68512d1bf14dfd865c/pair-compatibility-189/compatibility.cpp -o ../compatibility-build/compatibility
python3 research/4ca1557c95957c68512d1bf14dfd865c/pair-compatibility-189/run.py ../compatibility-build/compatibility ../compatibility-replay
python3 research/4ca1557c95957c68512d1bf14dfd865c/pair-compatibility-189/replay.py ../compatibility-replay --report ../compatibility-join-report.json
```

The optional separate C++ counter accepts the decompressed pair table and a new
report path. It performs no full-code distance evaluations:

```sh
c++ -O3 -std=c++17 -march=native research/4ca1557c95957c68512d1bf14dfd865c/pair-compatibility-189/count_join.cpp -o ../compatibility-build/count-join
python3 -c 'import gzip,pathlib; p=pathlib.Path("../compatibility-replay/pair-witnesses.bin.gz"); pathlib.Path("../pair-input.bin").write_bytes(gzip.decompress(p.read_bytes()))'
../compatibility-build/count-join ../pair-input.bin ../compatibility-cpp-counts.json
```

Pair-table records are three bytes each, little-endian uint16 message followed by
uint8 weight, in the case/representative order of TASK.md and `run/pairs.json`.
Zero/zero means allowed. The full gzip CSV retains every tested assignment, message,
weight and stopping metadata. A complete deterministic parameter list is preserved;
the largest compressed ledger is about 21.1 MB. No executable binary is committed.

Primary sources, compiler flags, parent/checker hashes, binary hash and environment
are pinned in `run/metadata.json`. `audit/join-report.json` records the Python count
map and `audit/cpp-counts.json` its separately implemented cross-check.
[VERIFICATION.md](VERIFICATION.md) records clean-clone checks and artifact hashes.

## Credit, limits, and handoff

Canonical models and primary CRT/Gray mechanics come from this same session's
PRs [#12](https://github.com/discoveryathome/binary-linear-codes/pull/12) and
[#13](https://github.com/discoveryathome/binary-linear-codes/pull/13). The direct
physical-rotation oracle specializes PR #13's separate replay. The new contribution
is the complete conservative tables, full-code root normalization/join, count map
and retained capped prefix. The package is self-contained on main with no changed
paths overlapping the previous contributions.

Seddas, Shashkov, Viazovska and Abbe retain the published parent credit. The project
supplied reconstruction and both spectrum checkers. Standard CRT/Griesmer theory,
@thakrarsagar's sessions `aac390866c59afee7d645224e629b13b` and
`a981e1a3197e2c924de70ed18d8e8ea8`, and PRs #10/#11 informed the witness/orbit methods.
No general-method or literature novelty is claimed.

Not checked: 497,193,136 untested allowed full assignments, profile A, exact minima
of rejected codes, independently certified spectra of every allowed pair, unrestricted
equivalence/optimality, a full fresh literature audit, other platforms and independent
human review. The positive-target output branch was not exercised by a real target.
The wider necessary-profile argument still requires review of PR #12. No accepted
results, frontier, catalogue or global verifier changed.

After independent review, a new bounded session can use the count map. C triples
0x43/0x6d/0x73 and 0x5b/0x61/0x67 each have 201,912 allowed assignments and received
no full distance checks here. Their smaller counts do not imply better distances.
The original prefix can also be resumed at index 2,000,000 in template 7.

```discover
{"v":0,"kind":"finding","task":"structured-189-22-pair-compatibility","scope":"Complete conservative pair tables and 499193136-assignment allowed join, with only a 2000000-choice full-code prefix excluded; no target or family exclusion","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-23T11:23:19Z","evidence_level":"author-checked","artifact":"research/4ca1557c95957c68512d1bf14dfd865c/pair-compatibility-189/README.md","seed":"4ca1557c95957c68512d1bf14dfd865c"}
```
