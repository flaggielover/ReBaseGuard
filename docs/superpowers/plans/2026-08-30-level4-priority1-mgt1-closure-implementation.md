# Level-4 Priority 1 `m > 1` Closure Implementation Plan

**Contract:** `docs/superpowers/specs/2026-08-30-level4-priority1-mgt1-closure-design.md`

**Isolated namespace:** `level4/closure_proofs/m_gt_1_priority1/` (the tracked,
hash-protected historical partial campaign at `m_gt_1/` remains unchanged).

## Phase 1 -- Freeze inputs and definitions

1. Hash immutable Track 1B and historical D2.3 inputs.
2. Create the inheritance manifest and human ledger.
3. Complete the source-level definition audit before proof work.
4. Freeze the numerical protocol, seed families, grids, tolerances, escalation
   schedule, and pass/fail rules.
5. Freeze the finite-support witness and exact rational certificate inputs.

## Phase 2 -- Human mathematics

1. Write the standalone theorem with the semantics of `e`, `P_e`, `E_e`, the
   stopped sigma-field, and the state-to-state map.
2. Prove the short/long random-denominator decomposition.
3. Prove stopped-expectation differentiation under explicit domination.
4. State Gaussian specialization, `m=1` reduction, rho scaling, and local
   attraction/repulsion consequences.
5. Prove analytically that the finite-support normalized tilt is a probability
   family and has score `-T_tau` at zero.

## Phase 3 -- Independent frozen-CUSUM correspondence

1. Implement new stopped-path and map evaluators without importing Stage D or
   Track 1B scientific functions.
2. Add forced-path structural tests for all window branches.
3. Run the frozen pilot escalation and record it without gate retuning.
4. Run the final preregistered experiment.
5. Derive machine-readable numerical decisions and the human correspondence
   report.

## Phase 4 -- Lean proof spine

1. Add an independent Level-4 Lean namespace importing only generic Level 1--3
   infrastructure.
2. Formalize window algebra, correction, expectation decomposition, `m=1`,
   dominated derivative algebra, rho scaling, and stability inequalities.
3. Compile with the pinned toolchain and record an axiom audit.
4. Document abstract Lean assumptions separately from concrete Gaussian-CUSUM
   obligations discharged outside Lean.

## Phase 5 -- Arb witness certificate

1. Implement the frozen finite-support witness with exact rational inputs.
2. Generate rigorous Arb enclosures for normalization, score, decomposition,
   derivative agreement, convergence, attraction, and repulsion.
3. Independently audit the machine-readable certificate.
4. Write the certificate report with the frozen-Gaussian evidence exclusion.

## Phase 6 -- Correspondence, regression, and closure

1. Complete the cross-representation correspondence table.
2. Add artifact, integrity, numerical, Lean, and certificate tests.
3. Add a one-command reproducer and derived closure decision.
4. Run focused tests, the Level 1--3 verifier, relevant Level-4 tests, Lean,
   Arb, and repository verification gates where feasible.
5. Write the five-category closure report and README.
6. Review immutable hashes, the full diff, generated outputs, and git status.
7. Commit one coherent implementation checkpoint and push if existing remote
   authentication succeeds.
