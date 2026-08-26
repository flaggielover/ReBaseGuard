# Final research synthesis design

## Objective

Convert the terminal `LEVEL-4-CLOSED` repository into an authoritative,
publication-oriented scientific narrative without reopening Level 4. The
synthesis must make the stopped-selection recursive re-baselining mechanism,
the theorem dependency structure, the evidence boundaries, the policy result,
the negative result, and the remaining limitations understandable without
requiring a reviewer to reconstruct campaign chronology.

The output is a repository-native technical Markdown report set. It is intended
to be the source of truth for a paper outline, preprint drafting, the project
README, presentations, resume wording, and independent review.

## Authority and no-new-science boundary

The terminal authority remains `level4/final_level4_closure/`, including the
current decision, requirement ledger, status transitions, open-items register,
and offline reproducer. The synthesis reads frozen artifacts but does not edit
scientific JSON, protocol files or hashes, theorem statements, datasets,
experiments, historical reports, verdicts, or requirement statuses.

The synthesis preserves all load-bearing boundaries:

- current verdict `LEVEL-4-CLOSED`;
- `17 PASS`, `1 PARTIAL`, `0 FAIL`, `0 OPEN`;
- `16/16` mandatory requirements passing;
- nonmandatory L4R-13 remaining `PARTIAL`;
- SR derivative theorem closed while rigorous SR local-instability Arb
  certification remains `OPEN`;
- historical failures and unfavorable comparisons remain visible;
- no production, detector-independence, distribution-free, universal-safety,
  universal-optimality, absolute-novelty, or operational-transition claim.

## Selected architecture

Create `docs/research_synthesis/` as a hub-and-spoke namespace:

- `README.md` is the reviewer entry point and contains the concise verdict,
  central question, summaries, principal result stack, and navigation.
- `MAIN_THEOREM_ARCHITECTURE.md` is the scientific spine and owns the seven
  principal theorems plus the separate method/policy and negative results.
- `RESULT_DEPENDENCY_GRAPH.md` presents the logical flow and scope boundaries.
- `EVIDENCE_HIERARCHY.md` separates human theorem, Lean-checked,
  Arb-certified, confirmatory numerical, semi-real empirical, negative result,
  interpretation, and open evidence.
- `DEFINITIONS_AND_NOTATION.md` owns canonical notation and explicitly
  distinguishes historical Stage-A and Track-1B/Stage-D conventions.
- `CLAIM_CATALOG.md` is the authoritative safe-wording and forbidden-wording
  registry.
- `LIMITATIONS_AND_OPEN_ITEMS.md` classifies limitations, optional rigor
  upgrades, and Level-4+ future work.
- `PAPER_OUTLINE.md` maps the result architecture into the requested paper and
  appendix structure without drafting the full paper.
- `FIGURE_PLAN.md` selects approximately eight nonredundant main figures and
  records source, purpose, section, placement, cleanup, notation, and caption
  thesis for each.
- `REPOSITORY_MAP.md` routes reviewers directly to frozen evidence by topic.

This structure is preferred over a single monograph because each future output
can reuse one authoritative component without duplicating the whole story. It
is preferred over a generated claim database because a new maintenance system
would exceed the presentation-only scope.

## Scientific narrative

The central question is not generic drift detection. It is how a sequential
monitoring system behaves when an alarm is selected by a stopping time, the
alarm-participating observations are reused to update the next reference, and
that new reference recursively changes the next monitoring cycle.

The theorem spine is:

1. the frozen CUSUM `m=1` stopped-selection derivative identity;
2. Arb-certified `Gamma_CUSUM > 2` combined with the Lean-checked
   differentiation spine to establish local instability;
3. the certified period-2 orbit of the deterministic conditional-mean
   skeleton, explicitly not the noisy stochastic chain;
4. the Track-1B random-window `m>1` derivative theorem with its short-cycle
   correction and convention boundary;
5. the derived `m`-`rho` local-stability boundary and D4 map, labelled
   mathematical rather than operational;
6. the closed symmetric two-chart SR derivative theorem, with numerical
   `Gamma_SR > 2` separated from the open Arb certificate;
7. the regular location-family derivative theorem, with analytic hypotheses
   and human-proved versus Lean-instantiated obligations identified.

Two results remain first-class but separate from the theorem spine. The method
result is the frozen stability-aware P3 reuse policy based on 80% of the lower
95% D4 boundary, clipped at one. The negative result is a mathematical
local-stability boundary without a detected operational transition under the
frozen protocol.

## Evidence and citation model

Every substantive claim will cite one or more repository-relative authoritative
artifacts. Numerical values will be copied from canonical JSON or final reports
and checked against those sources. When a conclusion combines evidence types,
the components will remain separately labelled instead of being presented as a
single stronger proof.

The evidence hierarchy is descriptive, not cumulative: Lean checks the formal
differentiation spine; Arb certifies the CUSUM numerical enclosure; human
theorems carry analytic assumptions not wholly discharged in Lean;
confirmatory numerical results do not become rigorous certificates; semi-real
tasks do not imply production deployment; and negative results answer their
pre-specified scoped questions without becoming general impossibility claims.

The closed N2 novelty position will retain the frozen search counts and the
approved wording: within the documented search scope, no identified work
combines the same alarm-stopped next-reference mechanism with the reported
derivative and stability results. Priority and exhaustive-search claims remain
forbidden.

## Verification and guards

Add a synthesis-only verification script and focused tests under the synthesis
namespace or the repository's existing test conventions. They will:

- confirm every cited repository path exists;
- read the final closure decision and requirement ledger to confirm verdict,
  tally, mandatory count, L4R-13 status, and SR evidence boundary;
- scan synthesis prose for forbidden novelty, universal safety, production,
  detector-independence, distribution-free, and operational-transition
  overclaims;
- confirm no scientific or historical files are modified by this task;
- run the terminal closure reproducer or repository verification required by
  current conventions without invoking simulations, new datasets, or network
  science;
- inspect the final Git diff so only design, synthesis, and presentation-only
  guard artifacts are included.

The checks fail closed on missing evidence, source disagreement, prohibited
wording, or frozen-state drift. They never repair a failure by changing a
scientific artifact or weakening a claim boundary.

## Git and publication handoff

After implementation and verification, create one clean implementation commit
named `Add final ReBaseGuard research synthesis`. Confirm the branch is based on
`origin/main`, fast-forward push without force, and verify local and remote HEAD
equality. The already committed design specification remains a separate
workflow checkpoint.

The final handoff reports the synthesis verdict, central question, theorem
stack, policy contribution, negative result, external validation, novelty-safe
position, evidence hierarchy, paper structure, main figures, open items,
created files, verification, and commit/push state. It names `FIGURE
CONSOLIDATION + README/RELEASE` as the next action but does not start it.
