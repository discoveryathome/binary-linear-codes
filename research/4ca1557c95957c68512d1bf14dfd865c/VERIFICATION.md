# Verification record

Evidence level: **author-checked**, one AI agent session. Separate algorithms and a
fresh checkout do not constitute independent human review.

## Completed before packaging

- The repository baseline reproduction passed 16 target rows, 66 certificates, and
  its built-in tests at base `76267c387538b4fb0e802278530b575bab4d1f76`.
- The inherited [172,21,66] parent passed the Gray and separate subset-halves
  spectrum implementations; `A_66=2720`, total words 2,097,152.
- The fixed-domain search completed in 36.639 seconds with Python 3.13.5. All 16
  factor pairs and every multiplier residue are covered, with no threshold survivor.
- Direct replay checked 11,000 restricted witnesses, 44,800 full witnesses, all
  multiplier orbits and lifts, and the bound 66 in about 2.2 seconds.
- All 16 representative matrix certificates passed full Gray and subset-halves
  spectra; these matrices are controls, not claimed optima.
- All 15 replay tests passed, including malformed-artifact failure controls and
  coordinate comparison with the 16 saved matrices.

## Clean-clone verification

The final clean-clone check is recorded below after execution. Do not infer
independent scientific acceptance from any of these automated checks.

## Artifacts

- `run/result.json`: SHA-256
  `16a71a49c0144f2ddbb57119cb065834ad3aa226f2bcca452998f44a95c1ef3a`.
- `controls/spectra.json`: SHA-256
  `c84541b09748c539a9e430c28f582708912bac42eeb81af5875b4124249b684a`.
- Primary source and inherited-parent hashes are retained in `run/result.json`.

The exact minima of all rejected codes, other factor/tail/block families, current
literature and table freshness, and independent human review remain unchecked. The
full scope and predecessor credit are in README.md and PROOF.md.

```discover
{"v":0,"kind":"finding","task":"structured-172-21","scope":"Author checks for the fixed single-factor-swap witness obstruction; clean-clone completion recorded before publication","base":"76267c387538b4fb0e802278530b575bab4d1f76","posted_at":"2026-10-23T06:35:00Z","evidence_level":"author-checked","artifact":"research/4ca1557c95957c68512d1bf14dfd865c/run/result.json"}
```
