# Paper outline

## Author metadata

Jingzhe Su<br>
School of Information and Software Engineering<br>
University of Electronic Science and Technology of China<br>
Email: suzhea0226@gmail.com

No advisor, coauthor, ORCID, venue, acceptance, peer-review status, or
institutional endorsement is asserted by this outline.

## 1. Introduction

Frame the overlooked feedback created by reusing alarm-selected observations.
State the derivative mechanism, the deterministic/local scope, the policy
contribution, semi-real support, and the negative operational-crossing result.

## 2. Repeated post-alarm re-baselining problem

Show the cycle: reference error, residual stream, stopping-selected alarm,
reuse update, next-cycle reference. Distinguish this problem from generic drift
detection and one-shot post-change estimation.

## 3. Frozen sequential model

Define the two-sided Gaussian CUSUM, inclusive alarm time, terminal inclusion,
reference map, reuse fraction, and P0--P3 policies. State what remains fixed
across cycles and what changes with `e`.

## 4. Stopping-selected derivative theory

Present Theorem 1, the stopped likelihood, the score covariance, Lean's role,
and the human/Arb interface. Define `Gamma_CUSUM` before using it.

## 5. CUSUM instability and deterministic dynamics

Present the Arb enclosure and local-instability consequence, then the separate
period-2 certificate. Keep the deterministic conditional-mean skeleton in the
section title/captions and state the stochastic scope exclusion beside the
result.

## 6. Finite-window reuse and stability boundary

Define the Track-1B random window, contrast it with Stage A, prove the exact
short-cycle correction, state Theorem 4, derive `rho_c(m)`, and present D4.
Label the map mathematical rather than operational.

## 7. Stability-aware reuse policy

Define P3 from the lower 95% D4 boundary and frozen 20% margin. Report reference
improvement, false-alert consequence, primary non-inferiority, P2 advantages,
secondary unfavorable outcomes, and `m=100` saturation.

## 8. Cross-detector and location-family extensions

Present the SR derivative theorem, the historically later Arb certificate, and
the scoped local-instability consequence as separate proof obligations. Then
state the regular location-family theorem, Gaussian reduction, and concrete
human/Lean boundary. Do not use either cross-detector result or L4R-13 to imply
general non-Gaussian closure.

## 9. Semi-real validation

Give the task-level Stage E/V2/V3 table, the non-pooled aggregation rule, and
the three-success versus two-required closure. Emphasize regime-dependent P2
safety and the absence of a production claim.

## 10. Mathematical boundary without operational transition

Treat the negative result as a main result: consistent crossing location,
adequate frozen design, 0/4 localized peaks, 4/4 monotonicity, and the scoped
negative conclusion.

## 11. Related work

Organize the 33 included works by self-starting/adaptive monitoring,
post-CUSUM estimation bias, repeated/multi-cyclic detection, reset/forgetting
systems, and adaptive windows. Use the N2 claims-narrowed position and the
approved search-scope wording.

## 12. Limitations

Cover L4R-13, the historical/current SR certificate distinction,
deterministic/stochastic separation,
location-family hypotheses, regime dependence, semi-real status, and novelty
coverage.

## 13. Discussion

Explain when stopping-selected reuse can matter, why mathematical stability is
useful even without a sharp operational transition, and how uncertainty-aware
reuse converts theory into a cautious policy.

## 14. Conclusion

Restate the mechanism and scoped contribution. Close with the evidence stack
and negative result, not with a universal safety or novelty claim.

## Appendices

- **A. Lean formalization:** theorem inventory, axiom audit, model
  correspondence, and conditional boundaries.
- **B. Arb certificate:** operator reduction, residual/resolvent bounds, exact
  enclosure, and replay.
- **C. `m>1` proof:** random-window definition, correction, human proof, Lean
  spine, correspondence.
- **D. SR proof and certificate:** forcing tail, stopped change of measure,
  reflection, Lean, historical open attempt, and post-Level-4 Arb closure.
- **E. Location-family proof:** score convention, hypotheses, Gaussian
  specialization, t3 correspondence, remaining obligations.
- **F. Extra simulations:** historical numerical diagnostics and unfavorable
  outcomes; no new runs for the paper-outline phase.
- **G. External-validation protocol:** task definitions, block inference,
  non-pooling, and task-level outcomes.
- **H. Novelty audit/search strategy:** 36 queries, screening, classification,
  unavailable sources, and claim firewall.
- **I. Reproducibility:** final ledger, protected history, protocol hashes,
  exact commands, and terminal reproducer.

The source map for every section is `REPOSITORY_MAP.md`; the safe wording
authority is `CLAIM_CATALOG.md`.
