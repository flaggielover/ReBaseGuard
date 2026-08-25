# L4R-12 requirement-semantics audit

## Result

The exact original row is **“Operational consequence of the Gamma_m crossing”**
and its class is **MANDATORY**. Its controlling source is the frozen Stage-D
protocol D2.5 (`925adecf…`), not a later global-audit paraphrase.

The requirement is **INVESTIGATIONAL**. D2.5 asks whether the crossing predicts
an operational change, requires frozen monitoring measurements on both sides,
and explicitly says that if none changes materially the boundary is reported as
**MATHEMATICAL, NOT OPERATIONAL**. The D2.5 precommit (`fb6272ef…`) was written
before outcomes and explicitly commits smooth monotone curves with no feature
near the crossing to that negative conclusion.

Therefore negative evidence was explicitly allowed. No pre-outcome repository
artifact requires a positive operational transition. Adding that condition now
would rewrite the rubric after the outcome.

## Taxonomy

The pre-outcome sources do not define a special global “negative pass” category.
They define a two-sided investigation and prescribe how to report its negative
answer. `PASS` is the available requirement-completion state. Stage F later
recorded the observational label `NEGATIVE RESULT` and normalized the mandatory
row to `PARTIAL`; those historical fields remain unchanged, but that later
normalization does not alter the earlier acceptance semantics.

The structured source extraction and mechanical classification are in
`results/source_extraction.json` and `results/semantic_classification.json`.

