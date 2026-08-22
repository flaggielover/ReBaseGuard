# Frozen protocol — Proof Track 1A

**Campaign:** Stage-A / Stage-D Distinction Replication + Lean Completion  
**Freeze date:** 2026-08-22  
**Status at writing:** no Track 1A confirmatory data generated  
**Historical Stage-D D2.3:** `FAILED` and immutable  
**Previous proof track:** `MGT1-THEOREM-PARTIAL` and immutable

This protocol is hashed and committed before confirmatory numerics. It does
not alter or reinterpret the previous track's five-SE-per-cell auxiliary gate.

## 1. Frozen detector and probability convention

Under the in-control law, `Z_t` are iid `N(0,1)`. The two-sided CUSUM has
allowance `k=1/2`, threshold `h=5`, initial states zero, update

`S_t^+ = max(0, S_{t-1}^+ + Z_t - k)` and
`S_t^- = max(0, S_{t-1}^- - Z_t - k)`.

The alarm boundary is inclusive and tested after the update. The terminal
observation is included in every stopped sum.

## 2. Exact estimands

For the ordinary Stage-D stop, define

`tau = inf {t >= 1 : max(S_t^+,S_t^-) >= 5}`,

`T_tau = sum_{t=1}^tau Z_t`, `w_m = min(m,tau)`, and

`S_m^D = sum_{r=0}^{w_m-1} Z_{tau-r}`.

The Stage-D truncated statistic and gain are

`A_m^D = S_m^D / w_m`,

`Gamma_D(m) = E_0[A_m^D T_tau]`.

The ordinary-stop, fixed-denominator intermediate statistic and gain are

`B_m^D = S_m^D / m`,

`Gamma_B(m) = E_0[B_m^D T_tau]`.

The short-cycle correction is

`C_m = E_0[1{tau<m}(1/tau - 1/m)T_tau^2]`.

For Stage A, define the dwell stop

`tau_m = inf {t >= m : max(S_t^+,S_t^-) >= 5}`,

where crossings before `m` do not terminate the path. Define

`A_m^A = (1/m) sum_{r=0}^{m-1} Z_{tau_m-r}`,

`Gamma_A(m) = E_0[A_m^A T_{tau_m}]`.

The gain distinction is

`Delta_Gamma(m) = Gamma_D(m) - Gamma_A(m)`.

At full reuse (`rho=1`), the corresponding derivatives are

`d_A(m)=1-Gamma_A(m)` and `d_D(m)=1-Gamma_D(m)`, so

`Delta_d(m)=d_D(m)-d_A(m)=-Delta_Gamma(m)`.

For general `rho`, both derivatives are multiplied exactly by `rho`.

## 3. Separation of the two mechanisms

The stopping-time contribution is

`S_stop(m) = Gamma_B(m) - Gamma_A(m)`.

The denominator/window contribution is `C_m`. The exact reconstruction is

`Delta_Gamma(m) = S_stop(m) + C_m`.

This prevents two mechanisms from being collapsed into a single convention
label:

1. `Gamma_B-Gamma_A` changes `tau_m` to `tau` while retaining denominator
   `m`; and
2. `C_m` changes the ordinary-stop denominator from `m` to `min(m,tau)`.

No sign theorem is assumed for `S_stop`. The correction integrand is
nonnegative pathwise.

## 4. Confirmatory grid and seed families

The frozen grid is `m={1,2,5,10,20,50}`. The `m=1` cell is the equality
control; the five `m>1` cells are reported without omission.

The master seed is `2026082211`, absent from every prior repository science
run at protocol freeze. NumPy `SeedSequence` with PCG64 maps each tuple below
to a deterministic stream:

- Stage A direct: `[2026082211, 1, replicate, m_index, batch]`;
- Stage D direct: `[2026082211, 2, replicate, batch]`;
- Stage D independent reconstruction: `[2026082211, 3, replicate, batch]`;
- test/smoke streams use route identifiers at least `90` and never enter the
  confirmatory result.

There are two independent confirmatory replications, indexed 0 and 1. Route
identifiers and all tuple components are part of the recorded result.

## 5. Sample sizes, batching, and CRN policy

For each replication:

- each Stage-A `m` cell uses `1,000,000` paths;
- the Stage-D direct route uses `1,000,000` ordinary-stop paths and evaluates
  all `m` on each path;
- the Stage-D reconstruction route uses a separate `1,000,000` ordinary-stop
  paths and evaluates all `m` on each path;
- batch size is `50,000` paths.

There are no common random numbers between Stage A and Stage D, between the
two replications, or between direct and reconstruction routes. Within one
Stage-D route, the same ordinary stopped path is intentionally evaluated at
all `m`; this is cross-`m` reuse, not CRN between the primary objects. Every
Stage-A `m` has a distinct stream.

No fresh-reference random draws are needed because the zero-mean fresh term
does not affect a gain or derivative expectation. Rho scaling is checked
algebraically and with deterministic transformed sample estimates.

## 6. Estimation and uncertainty

For every estimand, retain count, sum, and sum of squares of the pathwise
integrand. The reported Monte Carlo SE is the sample standard deviation divided
by `sqrt(n)`. Per-replication 95% confidence intervals use estimate
`±1.96*SE`.

Independent replications are combined by inverse-variance weighting. Pooled
SE is `1/sqrt(sum 1/SE_r^2)`. If a structural zero gives zero SE, it is reported
as exact and is not inverse-variance pooled.

For the direct Stage-A/Stage-D difference, independence gives

`SE_Delta = sqrt(SE_A^2 + SE_D^2)`.

The effect-size panel must include:

- raw gain difference `Delta_Gamma`;
- raw derivative difference `-Delta_Gamma`;
- 95% CI;
- standardized difference
  `Delta_Gamma/sqrt((Var(A_m^A T_tau_m)+Var(A_m^D T_tau))/2)`;
- the z statistic `Delta_Gamma/SE_Delta` as a diagnostic only.

The standardized difference is a path-integrand-scale effect size and is not a
hypothesis-test threshold.

`P(tau<m)` is the direct Stage-D short-cycle count divided by `n` with a
Wilson 95% interval. At `m=2`, zero observed events are permitted and must not
be treated as a failed implementation check; the exact event is extremely
rare.

## 7. Independent decomposition correspondence

The direct Stage-D route estimates `Gamma_D`. The disjoint reconstruction
route jointly estimates `Gamma_B`, `C_m`, and `Gamma_B+C_m`. Its within-path
sum is used so covariance is retained in the reconstruction SE.

For every replication and `m`, report

`epsilon_m = Gamma_D,direct - (Gamma_B,recon + C_m,recon)`,

`SE_epsilon = sqrt(SE_D,direct^2 + SE_(B+C),recon^2)`,

absolute discrepancy, absolute z, and relative discrepancy
`|epsilon_m|/|Gamma_D,direct|` when the denominator is nonzero.

Also verify independently in both ordinary-stop routes that

`A_m^D T_tau = B_m^D T_tau +
 1{tau<m}(1/tau-1/m)T_tau^2`

holds pathwise to maximum absolute floating-point error `<=1e-10`.

The decomposition criterion passes only if:

- every pooled absolute z is at most 3;
- every per-replication absolute z is at most 4;
- every pathwise maximum error is at most `1e-10`; and
- every correction sample is nonnegative to tolerance `-1e-14`.

## 8. Distinction criterion

The previous five-SE-per-cell rule is not reused. The confirmatory distinction
criterion is outcome-blind and combines statistical and scientific checks:

1. `m=1` passes the exact equality controls in Section 9;
2. at the preselected effect-bearing cells `m=20` and `m=50`, the pooled 95%
   CI for `Delta_Gamma` has lower endpoint strictly above zero and both
   independent replication point estimates are positive;
3. all `m>1` point estimates, CIs, standardized effects, stopping components,
   corrections, and short-cycle probabilities are reported, whether or not
   individually significant;
4. the direct effect and the two-component reconstruction agree at the sample
   level to `1e-10` when formed from the same direct-route moments; and
5. the independent decomposition criterion in Section 7 passes.

This criterion does not require significance at `m=2`, `m=5`, or `m=10`,
where the actual effect may be small. It does not use a z-score alone.

## 9. Mandatory `m=1` control

At `m=1`, verify:

- `tau_1=tau` in the implementation;
- `w_1=1`;
- `A_1^A=A_1^D=Z_tau` pathwise under a shared test stream;
- `C_1=0` exactly;
- the new independent Stage-A and Stage-D gain estimates agree within four
  combined SE;
- the pooled new gain agrees with the prior independent `m=1` gain within four
  combined SE; and
- the theorem reduces to the established identity
  `F'_{rho,1}(0)=rho(1-E[Z_tau T_tau])`.

## 10. Lean targets and soundness rule

Lean is authorized independently of the numerical distinction outcome. The
proof file must compile against the pinned Mathlib project and cover:

1. `w=min m tau` and the short/long partition;
2. the `tau<m` whole-path statistic identity;
3. pointwise and expectation-level decomposition;
4. correction nonnegativity;
5. `m=1` reduction;
6. exact rho scaling;
7. derivative-map algebra using the existing abstract differentiation-under-
   stopping interface where valid; and
8. derivative-plus-gain bounds implying the stated local slope condition.

The formalization must not introduce a scientific axiom. Explicit theorem
hypotheses are allowed and must be listed. The axiom audit must distinguish
Lean-checked algebra, the reused analytic interface and its hypotheses, and
numerical evidence. No claim of a fully instantiated frozen-CUSUM `A_m`
formalization may be made unless all corresponding measurability and moment
hypotheses are actually discharged.

## 11. Rho check

For `rho={0,0.25,0.5,0.75,1}`, verify in code that transforming the full-reuse
sample derivative as `rho*(1-Gamma)` equals the separately evaluated affine
formula to absolute error at most `1e-14`. This is an implementation control,
not new stochastic evidence.

## 12. Overall Track 1A decision

The exact allowed verdicts are `MGT1-TRACK1A-CLOSED`,
`MGT1-TRACK1A-PARTIAL`, and `MGT1-TRACK1A-FAILED`.

`CLOSED` requires all of the following:

1. previous theorem artifacts and expected partial result reproduce;
2. this independent distinction criterion passes;
3. the independent decomposition criterion passes;
4. the mandatory `m=1` control passes;
5. the Lean proof spine compiles;
6. assumptions and axioms are transparently documented;
7. the Track 1A tests and authoritative repository suite pass;
8. every frozen historical artifact remains unchanged.

A theorem contradiction, decomposition failure, correction-sign failure,
`m=1` failure, or Lean-discovered algebra error yields `FAILED` and stops the
campaign. A sound theorem spine with an evidentiary or instantiation obligation
remaining yields `PARTIAL`. No outcome may change this protocol retroactively.

If `CLOSED`, the scoped answer to the previously unmet `m>1 derivative
theorem` requirement is `YES — CLOSED`. This makes no overall Level-4 decision.

## 13. Arb and scope guards

Arb is `NOT REQUIRED`: this track claims a structural identity and a compiled
proof spine, not a new rigorously certified scalar inequality.

The track must not start an SR theorem, `m-rho` phase map, general location
family, external validation, or global Stage-F re-audit.

