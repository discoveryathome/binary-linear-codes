# Generator certificate v1

A UTF-8 JSON object has `format: "binary-generator-v1"`, `q: 2`, integer `n`, `k`, `d`, `rows`, and descriptive `provenance`. There are exactly k binary strings of exactly n characters. Character j is coordinate j, from the left, and corresponds to bit j internally. No numeric floating-point entries are accepted. The operational limit is k<=20 and n<=512. Pilot targets use k=10–12; larger checks require an explicit resource budget.

`d` means the **exact** minimum nonzero weight. Both understated and overstated values fail. Rank must be k. The JSON and source files have SHA-256 receipts. Provenance is an audit trail, not trusted mathematical input. Published recipes sometimes leave the choice of subcode unspecified: the importer chooses the first k independent basis rows, records this convention, and verifies the result. This reconstructs a qualifying code, not necessarily the identical Magma representative.

`codes.py` uses integer XOR elimination and a Gray-code walk over all 2^k messages. `independent.py` imports none of that module: it parses independently, performs list-valued GF(2) elimination, transposes the matrix, and computes each coordinate from message/column parity. Their full weight histograms must agree. These are independent implementations written in the same session, **not an independent human review**.

For a full-rank generator, linearity gives d(C)=min_{m!=0} wt(mG). Exhaustively evaluating all nonzero messages therefore proves this matrix's exact minimum distance. It does not prove that another [n,k] code cannot do better. `upper` in the record table is a separate literature/analytic bound, with its derivation retained.

All transformations return an independent basis. Puncturing may lower dimension; shortening first intersects with the zero constraints, then removes coordinates. Tests compare them to explicit codeword-set operations. Subcode selection uses full-rank message selectors. A permutation must be a bijection and cannot improve distance. Parity extension appends the row parity; arbitrary binary columns are also supported.
