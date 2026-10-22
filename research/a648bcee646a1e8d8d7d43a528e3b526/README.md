# Reconstructing the 55-point Goppa parent and two B2 descendants

This is a replication of published lower-bound constructions, not a new code record. The task was drawn from the `literature/goppa` card with seed `a648bcee646a1e8d8d7d43a528e3b526` at base `76267c387538b4fb0e802278530b575bab4d1f76`. The four certificates below were author-checked in this agent session; they have not had an independent reviewer.

## Construction

The [CodeTables recipe for `[51,12,19]`](https://www.codetables.de/BKLC/BKLC.php?q=2&n=51&k=12) starts from Loeloeian and Conan's `[55,16,19]` binary Goppa code over GF(64), with `g(x) = x^9 + 1`. The pinned source snapshot hash in `data/source-index.json` is `7ef83bce045ba4dd48413e8d395ceb72eda570b4a0b3c00f12358b296be32b80`. We use GF(64) defined by `x^6 + x + 1` and take all 55 elements where `g(a) != 0`. This is independent of the choice of field representation up to a permutation of the complete support.

For each support element `a`, the generator script forms the nine GF(64) parity checks `a^j/g(a)` for `j = 0..8`, expands them into 54 binary checks, and takes their GF(2) nullspace. The script checks that the field generator has order 63, the support has 55 elements, the nullspace has rank 16, and every generator row satisfies every check. Exhaustive enumeration gives distance 19. Appending overall parity gives `[56,16,20]`.

Two explicit dual words reproduce the B2 parameter steps in the [`[49,11,19]` table recipe](https://www.codetables.de/BKLC/BKLC.php?q=2&n=49&k=11) and the [`[46,11,17]` recipe](https://www.codetables.de/BKLC/BKLC.php?q=2&n=46&k=11):

| Parent | Zero-based dual support | Operation | Result |
| --- | --- | --- | --- |
| `[55,16,19]` | `5, 33, 35, 39, 40, 41` (weight 6) | Shorten on those six coordinates | `[49,11,19]` |
| `[49,11,19]` | `12, 21, 45` (weight 3) | Puncture those three coordinates | `[46,11,17]` |

Both supports are checked for orthogonality to every parent generator row. In the first step the six coordinates obey one parity relation, so zeroing them imposes at most five independent constraints; the resulting rank is exactly 11. In the second step every codeword has even parity on the three removed coordinates, so puncturing can remove at most two ones. The exact distance is 17. A seeded randomized information-set search found each listed support on its first coordinate permutation, but the saved supports are the witnesses; no exhaustive dual-distance search was performed.

## Replay and evidence

From the repository root, using Python 3.10 or later and the standard library:

```sh
python3 research/a648bcee646a1e8d8d7d43a528e3b526/goppa.py
python3 scripts/verify.py research/a648bcee646a1e8d8d7d43a528e3b526/*.json
```

The construction command deterministically rewrites the four certificates. `scripts/verify.py` checks each with the project's Gray-code and separate column-parity implementations. Its replay took 0.23 seconds on macOS arm64 in this session. The repository's `python3 scripts/reproduce.py` also passed at this base.

| Certificate | Rank | Exact minimum distance | Number of minimum-weight words |
| --- | ---: | ---: | ---: |
| `55_16_19.json` | 16 | 19 | 1,290 |
| `56_16_20.json` | 16 | 20 | 3,612 |
| `49_11_19.json` | 11 | 19 | 177 |
| `46_11_17.json` | 11 | 17 | 99 |

The source pages report these parameters; they do not supply generator matrices for a row-by-row comparison. The derived matrices therefore establish the same parameters and documented construction route, not coordinate equivalence to an unpublished Magma matrix. Neither verifier checks the external upper-bound proofs or proves optimality.

## Open next questions

An independent reviewer can replay the four certificates and inspect the field construction and dual supports. Other deferred Goppa and B2 recipes may need different support choices or later transformations; they were outside this bounded task.
