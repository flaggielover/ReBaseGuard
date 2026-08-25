# L4R-12 operational-crossing closure audit design

## Objective and authority

Create an isolated same-requirement audit for:

`L4R-12 — Operational consequence of the Gamma_m crossing`.

The repository is the complete authoritative requirement record. No external
condition may be imported after the outcome. Pre-outcome requirement semantics
control later status normalization. Historical Stage D, D2.5, D4, L4R-06,
Stage F, and the Final Global Re-audit remain immutable.

## Semantic source precedence

The audit applies this fixed precedence:

1. the pre-outcome Stage-D protocol;
2. the pre-outcome D2.5 design commitment;
3. the original reconstructed 18-row requirement wording and class;
4. the blueprint/ranking/kill-gate context;
5. later Stage-F and global-audit status normalization.

The first two sources explicitly ask whether the crossing predicts an
operational change and prescribe `MATHEMATICAL, NOT OPERATIONAL` if none of the
frozen metrics changes materially. Therefore the requirement is
investigational, and a scientifically sufficient negative answer is allowed.
Later normalization of `NEGATIVE RESULT` to mandatory `PARTIAL` is preserved as
history but cannot retroactively make the frozen question existential.

## Chosen architecture

Create `level4/closure_proofs/l4r12_operational_crossing/` with:

- human audits and reports requested by the campaign brief;
- a protected-history manifest and source hashes;
- a semantic-classification JSON derived from frozen text and structured data;
- a negative-result assessment covering N12.1–N12.10;
- a generator-owned scoped decision covering C12.1–C12.10;
- focused tests, exactly 19 adversarial checks, verification records, and an
  offline byte-stable reproducer.

No historical file is edited. No new simulation, m grid, metric, crossing
estimate, sample increase, dataset, or network access is used. Recomputing
monotonicity, coverage, standardized separation, and hash consistency from
existing JSON is an audit replay, not new science.

## Evidence flow

1. Verify protected hashes and extract exact wording/classification.
2. Classify semantics from frozen language, including explicit negative-outcome
   authorization and the absence of a positive-transition requirement.
3. Import the historical crossing and D2.5 operational summaries.
4. Verify both-side coverage, four preselected metrics, monotonicity, localized
   peak counts, uncertainty, precommit hashes, independent support, and absence
   of contradictory repository claims.
5. Classify the result as a completed research question with a valid negative
   answer, low-power non-demonstration, contradiction, or ambiguity.
6. Apply C12.1–C12.10 mechanically. Only the exact permitted scoped statuses
   may be emitted.
7. Map to original L4R-12 `PASS` only when negative-result closure is allowed,
   evidence is sufficient, same-requirement mapping is true, and every closure
   criterion passes.

## Evidence-strength rule

Evidence is sufficient only if all N12.1–N12.10 checks pass. The audit must show
that the crossing is real, the monitored curves cover both sides, the metrics
were frozen before outcomes, smooth monotonic behavior is present rather than
merely statistically unresolved, the conclusion is robust to the frozen
interpolation convention, later D4 evidence is consistent, and no repository
artifact establishes a contrary operational transition.

The claim remains scoped to the frozen Gaussian CUSUM, full reuse, Stage-D
window convention, m grid, shifts, and four primary monitoring metrics.

## Decision behavior

- All C12 criteria pass: `L4R12-CLOSED-NEGATIVE-RESULT`, mapping to original
  L4R-12 `PASS`.
- Semantics or source authority genuinely conflicts: `L4R12-SEMANTICS-AMBIGUOUS`
  and original row `PARTIAL`.
- Semantics are resolved but evidence or audit criteria are insufficient:
  `L4R12-PARTIAL` and original row `PARTIAL`.

There is no qualitative override and no new global verdict.

## Adversarial and failure handling

Implement exactly A1–A19 from the campaign brief. Preserve the first run before
verification/reproduction records exist. Missing history, source drift,
unreproducible classification, a universal claim, or a positive-transition
claim is an integrity failure. Weak negative evidence yields PARTIAL; it does
not trigger new science or threshold changes.

## Verification and Git

The reproducer verifies history and source hashes, regenerates classification,
assessment, and decision, runs focused tests and A1–A19, runs
`scripts/verify_level_4.sh`, and confirms historical D2.5 verbatim. It uses no
network.

Commit and fast-forward push two green campaign checkpoints after this design:

1. requirement-semantics and historical-evidence audit;
2. final scoped decision, adversarial/reproduction records, and reports.

Do not start the Final Global Level-4 Re-audit automatically.
