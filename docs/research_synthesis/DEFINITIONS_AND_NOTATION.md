# Definitions and notation

## Frozen base model

The primary instance uses a reset, symmetric, two-sided Gaussian CUSUM with
allowance `k=1/2`, inclusive threshold `h=5`, alarm testing from time one, and
the terminal observation included. The exact model correspondence is recorded
in `closure/01_FROZEN_MODEL.md` and `closure/03_LEAN_VERIFICATION.md`.

| Symbol | Canonical meaning |
|---|---|
| `mu` | Current in-control location. |
| `R_j` | Reference used during monitoring cycle `j`. |
| `e=R_j-mu` | Current reference error. |
| `X_t=mu+epsilon_t` | Physical observation. |
| `Z_t=X_t-R_j=epsilon_t-e` | Residual seen by the detector in the current cycle. Under the Gaussian base law, `Z_t~N(-e,1)`. |
| `tau` | Inclusive alarm time of the reset detector, starting at `t=1`. |
| `T_tau=sum_{t=1}^tau Z_t` | Stopped residual sum, including the terminal residual. |
| `rho in [0,1]` | Fraction of the next reference supplied by alarm-path reuse. |
| `m` | Nominal reuse-window length. |
| `F_{rho,m}(e)` | Conditional mean of the next reference error given current error `e`; at `m=1`, write `F_rho`. |
| `Gamma_CUSUM` | `E_0[Z_tau T_tau]` for the frozen CUSUM at `m=1`. |
| `A_m` | Stage-D random-window mean: `(1/min(m,tau))*sum_{r=0}^{min(m,tau)-1} Z_{tau-r}`. |
| `GammaTilde_m` | Authoritative Track-1B/D4 quantity `E_0[A_m T_tau]`. The tilde is load-bearing. |
| `B_m` | Fixed-denominator stopped suffix `(1/m)*sum_{r=0}^{m-1}1{tau>r}Z_{tau-r}`. |
| `C_m` | Nonnegative short-cycle correction `E_0[1{tau<m}(1/tau-1/m)T_tau^2]`. |
| `rho_c(m)` | Local multiplier boundary. For `GammaTilde_m>1`, `rho_c(m)=1/(GammaTilde_m-1)`. |
| `Gamma_SR` | `E_0[Z_tau T_tau]` under the authoritative symmetric two-chart SR stopping rule. |
| `psi(z)` | Conventional location score `-f'(z)/f(z)`. The parameter score for `f(z+e)` is `s(z)=-psi(z)`. |
| `Gamma_f` | `E_0[Z_tau sum_{t<=tau}psi(Z_t)]` for a regular location family. |

## The random-window convention is not Stage A

Historical Stage A suppresses alarm eligibility until `m`:

`tau_m=inf{t>=m: alarm at t}`.

It always reuses exactly `m` observations and divides by `m`; its stopping path
therefore depends on `m`. Track 1B and Stage D instead retain the ordinary
`tau=inf{t>=1: alarm at t}` and use `min(m,tau)` observations. On short cycles,
the denominator is `tau`, not `m`. The conventions agree only at `m=1`.

For Track 1B,

`GammaTilde_m=(1/m)sum_{r=0}^{m-1}gamma_r+C_m`,

where `gamma_r=E_0[1{tau>r}Z_{tau-r}T_tau]` and `C_m>=0`. Omitting `C_m`, using
a minimum dwell, or silently writing a Stage-A scalar as `GammaTilde_m` changes
the theorem. See `level4/closure_proofs/d4_phase_map/DEFINITION_AUDIT.md` and
`level4/closure_proofs/m_gt_1_track1b/THEOREM.md`.

Shortened prose may use `Gamma_m` only after declaring it an alias for the
Track-1B random-denominator `GammaTilde_m`. This synthesis otherwise retains
the tilde.

## Policies

| Policy | Definition | Role |
|---|---|---|
| P0 | `rho=0` | Fresh-reference baseline. |
| P1 | `rho=1` | Full alarm-window reuse. |
| P2 | `rho=0.0297958439` | Historical fixed-reuse comparison. |
| P3 | `rho_P3(m)=min(1,0.8*rho_c,L95(m))` | Primary uncertainty-aware stability policy. |

`rho_c,L95(m)` is the lower endpoint of the D4 95% interval for `rho_c(m)`.
The fixed factor `0.8` is a pre-outcome 20% safety margin, not a fitted
performance parameter. Definitions are frozen in
`level4/closure_proofs/l4r06_policy/PROTOCOL.md` and
`level4/closure_proofs/l4r06_policy/POLICY_DEFINITION.md`.

## Map versus stochastic recursion

`F_{rho,m}` is a deterministic conditional-mean map. The observed recursive
reference error has additional cycle noise. A local multiplier or deterministic
period-2 orbit therefore does not by itself characterize the invariant law,
alternation, or operational performance of the noisy chain.
