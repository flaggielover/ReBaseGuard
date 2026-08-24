# Final global Level-4 re-audit

## A. Final global verdict

> **`LEVEL-4-PARTIAL`**

The later D4, external-validation, and novelty campaigns close the previous
FAIL/OPEN blockers, but the original fallback taxonomy requires every mandatory
row to be PASS. L4R-06 and L4R-12 remain mandatory non-PASS rows, so CLOSED is
not available. `LEVEL-4-CLOSED-WITH-LIMITATIONS` remains unauthorized.

## B. Historical Stage-F verdict

`LEVEL-4-PARTIAL` — unchanged historical fact.

## C. Previous post-closure verdict

`LEVEL-4-PARTIAL` — unchanged historical fact.

## D. Current requirement counts

15 PASS · 3 PARTIAL/NEGATIVE · 0 FAIL · 0 OPEN.

## E. Mandatory requirement counts

14 PASS · 2 PARTIAL/NEGATIVE · 0 FAIL · 0 OPEN, of 16.

## F. Requirement-by-requirement table

| ID | Requirement | Class | Stage F | Previous re-audit | Current | Changed now | Blocks closure |
|---|---|---|---|---|---|---|---|
| L4R-01 | Level 1-3 closure foundation | MANDATORY | PASS | PASS | **PASS** | NO | NO |
| L4R-02 | Multi-cycle oracle, reproducible | MANDATORY | PASS | PASS | **PASS** | NO | NO |
| L4R-03 | Conditional map and derivative correspondence at m=1 | MANDATORY | PASS | PASS | **PASS** | NO | NO |
| L4R-04 | Gamma_CUSUM > 2 rigorously | MANDATORY | PASS | PASS | **PASS** | NO | NO |
| L4R-05 | Rigorous period-2 for the deterministic skeleton | MANDATORY | PASS | PASS | **PASS** | NO | NO |
| L4R-06 | Stability-aware reuse policy with monitoring consequences | MANDATORY | PARTIAL | PARTIAL | **PARTIAL** | NO | YES |
| L4R-07 | Confirmatory sensitivity of the stability-aware policy | MANDATORY | PASS (narrow scope) | PASS | **PASS** | NO | NO |
| L4R-08 | SR Monte Carlo derivative | MANDATORY | PASS | PASS | **PASS** | NO | NO |
| L4R-09 | m>1 derivative theorem | MANDATORY | FAIL | PASS | **PASS** | NO | NO |
| L4R-10 | SR derivative theorem (proved) | MANDATORY | OPEN | PASS | **PASS** | NO | NO |
| L4R-11 | m-rho phase map (D4) | MANDATORY | FAIL (not run) | FAIL | **PASS** | YES | NO |
| L4R-12 | Operational consequence of the Gamma_m crossing | MANDATORY | NEGATIVE RESULT | PARTIAL | **PARTIAL** | NO | YES |
| L4R-13 | Non-Gaussian robustness | STRONG_EXTENSION | PARTIAL | PARTIAL | **PARTIAL** | NO | NO |
| L4R-14 | General location-family theorem | STRETCH | OPEN | PASS | **PASS** | NO | NO |
| L4R-15 | Semi-real external validation | MANDATORY | FAIL vs its own rule | FAIL | **PASS** | YES | NO |
| L4R-16 | Prior-art and novelty verification | MANDATORY | OPEN / provenance gap | OPEN | **PASS** | YES | NO |
| L4R-17 | Reproducibility of every stage | MANDATORY | PASS | PASS | **PASS** | NO | NO |
| L4R-18 | Protocol integrity | MANDATORY | PASS | PASS | **PASS** | NO | NO |

## G. Rows changed since the previous re-audit

- L4R-11 — m-rho phase map (D4): PASS via `D4-PHASE-MAP-CLOSED`.
- L4R-15 — Semi-real external validation: PASS via `EXTERNAL-VALIDATION-V3-CLOSED`.
- L4R-16 — Prior-art and novelty verification: PASS via `NOVELTY-VERIFICATION-CLOSED`.

## H. Remaining partial/negative rows

- **L4R-06 — Stability-aware reuse policy with monitoring consequences**: PARTIAL. Stage C remains partial and C6 remains failed; no later campaign explicitly closed this same policy requirement.
- **L4R-12 — Operational consequence of the Gamma_m crossing**: PARTIAL. The frozen experiment produced a scientifically valid negative result, but Stage F normalized the mandatory row as non-PASS and no later same-requirement closure exists.

- **L4R-13** is a nonmandatory STRONG_EXTENSION partial and does not block
  closure. The exact provenance analysis is in `REQUIREMENT_LEDGER.md`.

## I–J. Remaining OPEN items and SR Arb status

No original ledger row is currently OPEN. The rigorous SR local-instability
Arb certificate remains an explicit OPEN optional rigor upgrade outside L4R-10.
Level 4 closure would not imply `SR-GAMMA-CERTIFIED`.

## K. D4 interpretation

D4 closes L4R-11 with `F'_{rho,m}(0)=rho(1-GammaTilde_m)`. This is a
protocol-specific deterministic local-stability map, not proof of an abrupt
stochastic operational transition. Historical D2.5 remains `MATHEMATICAL, NOT
OPERATIONAL`.

## L. External-validation synthesis

L4R-15 is closed by three independent successful tasks against a frozen
requirement of two: V2 Household plus V3 MetroPT-3 and Online Retail II. Stage E
remains 0/3, V2 remains 1/3, V3 Route B remains unfavorable, and P2 remains
regime-dependent.

## M. Novelty positioning

Novelty verification closes L4R-16 at N2: partial overlap found and claims
narrowed. Within the documented search scope, no work was identified that
combines the same alarm-stopped next-reference mechanism with the reported
derivative and stability results. This is not absolute novelty or priority.

## N–Q. Scientific extrema

- **Strongest rigorous result:** The Lean-checked stopped-likelihood differentiation spine, outward-rounded Gamma_CUSUM enclosure above two, and certified deterministic-skeleton period-2 orbit.
- **Strongest general theorem:** For regular one-dimensional location families under explicit stopped change-of-measure, tail, integrability, and domination hypotheses, F'_rho(0)=rho(1-Gamma_f).
- **Strongest cross-detector result:** CUSUM and the authoritative symmetric two-chart SR detector both support the stopped-score derivative identity; Gamma_SR > 2 remains confirmatory numerical evidence.
- **Most important negative result:** The Gamma_m crossing is mathematical, not operational: zero of four monitoring metrics peaked at m* and all four were monotone in log m.

## R. Publication-safe claim

ReBaseGuard has a rigorous CUSUM core and independently verified scoped derivative, phase-map, regular-location-family, novelty-hygiene, and semi-real-validation closure campaigns. The current global Level-4 status remains partial because two original mandatory rows retain non-PASS partial/negative outcomes.

## S. Resume-safe claim

Built and verified a reproducible sequential-monitoring research stack spanning Lean-checked theorem spines, Arb-certified CUSUM bounds, deterministic stability analysis, scoped cross-detector and location-family results, and outcome-blind semi-real validation; a terminal audit preserved historical failures and identified two remaining mandatory limitations.

## T. Prohibited claims

See `CLAIM_FIREWALL.md`. Absolute novelty, priority, universal safety,
production readiness, detector independence, SR certification, and an
operational phase transition are not supported.

## U–W. Verification, adversarial, and reproduction

- distinct authoritative checks: 1139/1139
- focused final-audit tests: 36/36
- adversarial: first 24/26 preserved; final 26/26
- reproduction: PASS, offline and byte-stable
- command: `bash level4/final_global_reaudit/reproduce.sh`

## X. Protected-history confirmation

`INTACT`: 23 trees and 23 historical files verified.

## Y–Z. Project state and exact next action

The current Level-4 research campaign remains open/partial. Resolve only the frozen L4R-06 and L4R-12 mandatory non-PASS blockers in a separately authorized future campaign; do not start that work in this audit.
