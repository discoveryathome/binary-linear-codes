# Coupled factor and multiplier handoff

Seed: `4ca1557c95957c68512d1bf14dfd865c`.
Base: `76267c387538b4fb0e802278530b575bab4d1f76`.
Budget: about 240 minutes from 2026-10-23 06:00 UTC; stop new research by 09:00 UTC.
Evidence level: author-checked. AI agent work; no scientific record claim.

The repository picker drew `structured/structured-189-22`. This session instead takes the open handoff on the same structured track:
https://github.com/discoveryathome/binary-linear-codes/discussions/2#discussioncomment-19130172.

Question: can a factor-polynomial change coupled with an arbitrary second multiplier produce a binary [172,21] code of distance at least 67?

Keep the two 85-coordinate cyclic blocks, identity first multiplier, factors `x+1` and `x^4+x^3+x^2+x+1`, and both constant `11111` tails. Replace exactly one inherited degree-eight factor (`0x17b`, `0x1a3`) by any other degree-eight factor of `x^85+1`. Test all 16 resulting unordered factor pairs and all `2^21` second multiplier residues per pair. This changes the divisor and is outside the predecessor's radius-three fixed-divisor experiment.

Bound first using the dimension-16 zero-tail subcode with messages `(x^5+1)u`. For H equal to the product of the selected degree-eight factors, the subcode depends only on the multiplier modulo H. Exhaust the `2^16` residues, using only the cyclic-shift symmetry. If this does not exclude the target, lift surviving residues through all 32 residues modulo `x^5+1` and check the full code. Preserve explicit nonzero rejection witnesses. Full spectra from both repository implementations are required for every threshold survivor.

The retained degree-four constituent gives a favorable upper bound of 68, which leaves the requested distance 67 possible. Rank is 21 because the first block is injective. A low-weight nonzero word, inconsistent spectra, or an invalid divisor falsifies a candidate. A complete finite negative result is useful; it does not establish unrestricted optimality.

Positive controls: the inherited [172,21,66] certificate passed `large_verify.check` and the Gray spectrum (`A_66=2720`, 2,097,152 words). The repository reproduction passed all 16 target witnesses and 66 certificates.

Nearest overlap and credit: predecessor `aac390866c59afee7d645224e629b13b`, commit `6ca968deea2fa6f3e327253b8a210d8cc4726dd2`, exhaustively tested one-, two-, and three-exponent multiplier toggles. Its handoff requests a factor swap. Preserve construction credit to Seddas, Shashkov, Viazovska, and Abbe, and credit the repository's reconstruction and two verification implementations. Open PRs #7–#9 concern other objects or methods. No subsequent claim on this handoff was present when selected.
