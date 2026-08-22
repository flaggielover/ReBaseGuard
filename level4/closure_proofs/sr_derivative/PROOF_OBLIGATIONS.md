# SR derivative proof-obligation ledger

**Ledger date:** 2026-08-22  
**Protocol:** `e9b66ff8ffbf0d8138598b1d4dc19dcc1e44d8b4f33f5b462b5b82f341d5f762`

This ledger separates the concrete human probability proof from the
conditional machine-checked spine.  `CLOSED (human)` means that the argument is
given in `THEOREM.md`; it does not mean the concrete infinite process has been
instantiated in Lean.

## 1. Definition and analytic obligations

| ID | Obligation | Evidence | Status |
|---|---|---|---|
| D1 | Authoritative natural-unit threshold, reset, update, inclusive alarm, and terminal inclusion match active Stage D SR code | `DEFINITION_AUDIT.md` Sections 1--2; source-hash tests | CLOSED |
| D2 | Residual convention is `Z=epsilon-e~N(-e,1)` and fixes the likelihood-score sign | `DEFINITION_AUDIT.md` Sections 1 and 4 | CLOSED |
| D3 | After residual parameterization, the detector is a fixed path functional and `e` changes only its law | `DEFINITION_AUDIT.md` Section 3 | CLOSED |
| D4 | Matched `m=1` reuse is exactly `e+Z_tau`; the fresh term is independent and mean zero | `THEOREM.md` Section 5 | CLOSED (human) |
| A1 | Finite-prefix chart states, alarm events, `tau`, `Z_tau`, and `T_tau` are measurable | `THEOREM.md` Section 2 | CLOSED (human) |
| A2 | `tau` is a.s. finite near zero and has a uniform geometric tail | forcing bound and compact Gaussian tail argument, `THEOREM.md` Section 3 | CLOSED (human) |
| A3 | Small exponential moments of `tau` and `T_tau`, plus `Z_tau in L2`, hold | Gaussian MGF and Cauchy--Schwarz summation, `THEOREM.md` Section 4 | CLOSED (human) |
| A4 | `Z_tau`, `T_tau`, and `Z_tau T_tau` are integrable | consequence of A3, `THEOREM.md` Section 4 | CLOSED (human) |
| A5 | The stopped likelihood identity is valid without an unjustified optional-stopping step | event-by-event finite-prefix change of measure, `THEOREM.md` Section 6 | CLOSED (human) |
| A6 | A uniform integrable derivative dominator exists near zero | explicit dominator and A3, `THEOREM.md` Sections 4 and 7 | CLOSED (human) |
| A7 | Differentiation under the stopped expectation gives `-E_0[Z_tau T_tau]` | A5--A6, `THEOREM.md` Section 7 | CLOSED (human) |
| S1 | Reflection swaps charts and preserves the alarm time | recursion induction, `THEOREM.md` Section 8 | CLOSED (human) |
| S2 | Reflection negates terminal residual and stopped sum; `F_1` is odd | `THEOREM.md` Section 8 | CLOSED (human) |
| R1 | `F_rho=rho F_1` and `F'_rho(0)=rho F'_1(0)` | exact affine expectation, `THEOREM.md` Sections 5 and 7 | CLOSED (human) |
| T1 | `F'_rho(0)=rho(1-Gamma_SR)` | `THEOREM.md` Section 7 | CLOSED (human) |
| T2 | `Gamma_SR>2` implies `|F'_1(0)|>1` and local linear repulsion | `THEOREM.md` Section 9 | CLOSED conditionally on the scalar inequality |

## 2. Numerical obligations

| ID | Obligation | Blocking rule | Status |
|---|---|---|---|
| N1 | Fresh calibration candidate reproduces the authoritative threshold | candidate error `0.333%<2%` | PASS |
| N2 | Fixed-threshold SR/CUSUM operating points match | ARL ratio error `0.162%<1%` | PASS |
| N3 | Raw-state Route A corresponds to historical SR Gamma | combined `z=-0.726` | PASS |
| N4 | Route A numerically places Gamma above two | batch 99% lower bound `17.218>2` | PASS — confirmatory only |
| N5 | Independent log-state Route B matches stopped-score prediction | pooled `|z|=2.015`; replication and relative gates pass | PASS |
| N6 | Raw/log reflection, rho, crossing, and tie controls pass | all structural items; zero confirmatory ties | PASS |
| N7 | Seed, batch, CRN, and source separation hold | all integrity guards | PASS |

N1--N7 passed and the numerical decision records exactly
`NUMERICAL GATE CLOSED — LEAN AUTHORIZED`.  Lean is now authorized.

## 3. Lean reuse boundary

The following are already reusable from the Level 1--3 project:

| Component | Existing declaration/file | Role |
|---|---|---|
| stopped integrand | `stoppedIntegrand`, `StoppedLikelihood.lean` | defines `Z exp(-eT-e^2 tau/2)` |
| pointwise derivative | `stoppedIntegrand_hasDerivAt` | supplies score `-(T+e tau)` |
| integral bridge | `hasDerivAt_integral_stoppedIntegrand_zero`, `IntegralBridge.lean` | converts explicit measurability/integrability/domination hypotheses to derivative at zero |
| deterministic dominator | `abs_stoppedIntegrandDeriv_le`, `Domination.lean` | bounds the parameter derivative uniformly |
| moment interface | `hasDerivAt_integral_stoppedIntegrand_zero_of_separate_moments` | accepts separate stopped exponential-moment hypotheses |
| real derivative algebra | Mathlib | identity-plus-expectation and constant scaling |

Track 2 still must formalize after the numerical gate:

| ID | New Lean obligation | Status |
|---|---|---|
| L1 | raw two-chart state, update, and sign/state-swap reflection | PASS |
| L2 | inclusive alarm symmetry | PASS |
| L3 | finite-list first-alarm and terminal-record reflection | PASS |
| L4 | terminal sign negation and product invariance | PASS |
| L5 | exact rho scaling and odd-map algebra | PASS |
| L6 | conditional stopped-score derivative consequence | PASS under explicit analytic hypotheses |
| L7 | `Gamma>2 -> |F'_1(0)|>1` | PASS as a conditional implication |
| L8 | authoritative threshold/convention correspondence theorem | PASS |
| L9 | compilation, forbidden-placeholder scan, and `#print axioms` audit | PASS — standard axioms only |

The following concrete facts are deliberately not claimed as Lean-instantiated:

- the infinite product Gaussian residual construction for SR;
- the filtration and concrete stopping-time measurability proof;
- the SR forcing-tail probability calculation;
- concrete exponential moments and stopped-variable integrability;
- the stopped change-of-measure identification; and
- concrete domination for the infinite SR process.

The final Lean correspondence report must use this wording:

> The Lean theorem formalizes the algebraic/stopped-score consequence under
> explicit analytic hypotheses; the concrete SR tail, measurability,
> integrability, and domination obligations remain human-proved.

## 4. Arb and final obligations

| ID | Obligation | Closure role | Status |
|---|---|---|---|
| C1 | Arb interval proves `Gamma_SR>2` at exact runtime rational for authoritative `A` | non-blocking rigor upgrade | OPEN — global cover/residual/propagation incomplete |
| C2 | independent certificate auditor reconstructs all critical claims | required only for `SR-GAMMA-CERTIFIED` | OPEN — auditor covers the OPEN probe, not a full certificate |
| V1 | Track-2 clean reproduction | required for derivative closure | PASS — 168/168 closure-track checks |
| V2 | full authoritative repository verification | required for derivative closure | PASS — 695/695 |
| V3 | historical manifest unchanged | required for derivative closure | PASS — 139-file manifest |

C1 and C2 remain incomplete.  The final report must say `rigorous SR local-
instability certificate: OPEN`; this does not block `SR-DERIVATIVE-CLOSED`.
