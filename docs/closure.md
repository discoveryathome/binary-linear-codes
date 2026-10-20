# Closure and novelty policy

Let L(n,k) be a known existence lower bound. The engine saturates a finite domain 1<=k<=n<=256 under:

- subcodes: L(n,k-1)>=L(n,k);
- puncturing (d>1, k<n): L(n-1,k)>=d-1;
- shortening a nonzero coordinate, then selecting a subcode if needed: L(n-1,k-1)>=d;
- zero extension: L(n+1,k)>=d;
- parity extension: L(n+1,k)>=d+(d mod 2).

Permutations preserve the same parameter node. The queue terminates because integer lower bounds only increase in a finite bounded domain. Each improved node retains its source and derivation. Closure is recomputed from all table entries, not just selected targets. Recent reported results are included conservatively in the **exclusion** closure, without being relabelled verified constructions.

This is the complete fixed point of those guaranteed parameter rules in that domain. It is not enumeration of every coordinate subset, subspace, or equivalence class of each source matrix. Such enumeration is generally expensive and can occasionally exceed guaranteed bounds. The experiment explores concrete transformations separately. Any result consisting solely of standard transformations of published codes is reported as a derived construction, even if it exposes a table omission; it is not credited as a fresh scientific parent record.

Upper bounds are tightened by the contrapositives of puncturing, shortening, subcoding, and parity extension, plus the exact integer Griesmer inequality. Published nonexistence overrides are separate, source-linked inputs. Their underlying classification computations have not been replayed. Every final target must satisfy verified_d>=published_lower, verified_d<=exclusion_lower<upper. Contradictory lower and upper data stop the pipeline.

Before claiming novelty, refresh literature, reconstruct any relevant newer parent, recompute closure, check coordinate equivalence and provenance, and seek external expert review. Beating this frozen exclusion closure is only a **candidate** record. No novelty is inferred from a new matrix hash or from a smaller number of minimum words.
