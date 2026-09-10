# B_int representation successor — BINT_REPRESENTATION_NUMERICALLY_NOT_CLOSING

Predecessor: b48973d6 (p5y-k1-sr-o9-endpoint-strip-micropilot). Nothing adopted; no certifier change.

## Phase 1 — doctrine
The frozen record binds the enclosure, not the storage: L-R3.1 (PROOF.md 14d6f028) proves
sp(u) in sum a_k (u-c)^k + [-E_d, E_d] for ANY ball A_{d+1} containing sp^(d+1)(xi)/(d+1)!;
ERROR_ALGEBRA §1 (4f32df02) permits a tighter proved, dependency-preserving enclosure of the same
expression. Storing the Lagrange ball inside the coefficients is Task1R implementation, not doctrine.
=> not FROZEN_BLOCKED.

## Phase 2 — decomposition (evidence/bint_dependency_trace.json)
Dominant source: sr_local.softplus_local_enclosure evaluates the degree-9 Lagrange coefficient by
arb_series over the whole panel interval, giving a_next radius 15.6-27.1 (mid ~1e-6), so
eps = rad*rho^9 = 1.4e-5..6.6e-5 per map. Chebyshev recursion grows radius mass ~1e3 to T_16;
contraction against small high-order moments cancels it: old int = 0.065 x eps.
Moments (~1e-46), candidates (exact dyadic), rounding: negligible.

## Phase 3/4 — requested representation P_mid + R_sp with the SAME frozen Lagrange ball
Mean-value propagation lower bound (core panels only; strips only add):
cell 0 (51,63) 9.02e-5 = 54.4x allowance (old 4.96x); cell 0 (63,54) 2.11e-5 = 12.7x (old 1.25x);
cell 150 (51,63) 9.54e-5 = 20.6x (old 1.81x). Separate propagation is WORSE than the old
representation (loses the interval cancellation). Hard stop: "separate propagation still fails badly".
Phase 5 not run.

## Diagnostic only — NOT adopted (governance question)
Unchanged representation, Lagrange factor A_9 = [-M/9!, M/9!], M = softplus_derivative_bound_tight(9)
(the frozen P1 bound, same theorem L-R3.1, rigorous): worst int/allowance 6.4e-5, 2.5e-5, 2.3e-5;
control 150 (17,11) 2.8e-5; all F_r:k0 gates pass on all four; endpoint <= 6.2e-11; CPU 2-6 s; RSS 64 MiB.
Adopting it changes the numerical remainder bound used by the certifier (user rule: "same frozen
remainder theorem and numerical bound") and therefore requires an explicit governance decision.
