# L4R-12 frozen audit decision rule

This rule is frozen before the isolated scoped verdict is generated. It audits
existing repository evidence only and cannot authorize new science.

## Source authority

The repository is the complete requirement record. Apply sources in this order:

1. pre-outcome Stage-D protocol;
2. pre-outcome D2.5 precommit;
3. reconstructed 18-row wording and class;
4. blueprint/ranking/kill-gate context;
5. later Stage-F and global-audit status normalization.

A later status label cannot add a positive-transition condition absent from the
pre-outcome sources.

## Evidence rule

`evidence_sufficient` is true only when N12.1 through N12.10 all pass and the
protected-history check passes. Existing JSON arithmetic, source extraction,
hash verification, and deterministic monotonicity replay are permitted. A new
grid, metric, sample, crossing estimate, detector, dataset, or simulation is not.

## Closure criteria

- C12.1 original wording reconstructed exactly.
- C12.2 semantics classified without post-outcome modification.
- C12.3 historical crossing evidence verified.
- C12.4 operational metrics and negative result verified.
- C12.5 historical D2.5 conclusion preserved.
- C12.6 evidence distinguishes a valid negative answer from low power.
- C12.7 frozen semantics allow negative-result closure.
- C12.8 same-requirement mapping is explicit.
- C12.9 exactly A1–A19 pass.
- C12.10 the authoritative repository verifier passes.

Apply the decision mechanically:

- If source authority or semantics genuinely conflict, emit
  `L4R12-SEMANTICS-AMBIGUOUS` and map the original row to `PARTIAL`.
- Otherwise, if C12.1–C12.10 all pass, emit
  `L4R12-CLOSED-NEGATIVE-RESULT` and map the original row to `PASS`.
- Otherwise emit `L4R12-PARTIAL` and map the original row to `PARTIAL`.

No qualitative override and no other scoped or global status is allowed.

## Claim boundary

Allowed: the frozen metrics and protocol found no crossing-localized operational
transition, so the pre-specified research question has a valid negative answer.

Forbidden: the crossing has no operational consequence in general, operational
effects are impossible, or no real system can show a transition.

