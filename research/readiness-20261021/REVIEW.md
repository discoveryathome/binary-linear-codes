# Review request: Binary linear error-correcting codes

Status: prepared locally; not sent. No reviewer has signed off.

Baseline commit: `b37e3ea5f85cde1b5bc650729c66d950c8cca84a`. Review the preparation branch commit recorded in the cohort receipt when work is finalized.

Minimum distance remains primary. The k<=22 checker is a separate bounded entry point; the original k<=20 verifier stays unchanged. All six starting parents are published replications. A new hash or smaller minimum-word multiplicity is not a distance record. Derived constructions and bounded obstruction proofs receive distinct credit.

1. Assess whether the six proposed successor families have useful headroom after current literature and closure.
2. Audit large-code certificate checking, reconstruction orientation and the stated scope of local obstructions.
3. Provide the missing explicit [200,21,77] generator artifact and provenance if available; its bound remains an exclusion meanwhile.

Return: the commit reviewed, commands run, exact outputs/artifact hashes, any
counterexamples or limitations, and a decision of revise / approve scoped beta /
defer. Specify the scope of approval and review capacity. Do not infer general
scientific validity from passing the automated suite. No signature is prefilled.
