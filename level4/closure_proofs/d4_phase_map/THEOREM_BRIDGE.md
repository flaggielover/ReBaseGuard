# Track-1B theorem to the D4 stability boundary

## Imported theorem

For the exact Stage-D convention-A statistic audited in
`DEFINITION_AUDIT.md`, Track 1B closes

`F'_{rho,m}(0) = rho(1-GammaTilde_m)`.

D4 defines the local multiplier

`lambda(m,rho) = rho(1-GammaTilde_m)`.

The fixed point `e=0` of the deterministic conditional-mean reference map is
locally stable when `|lambda|<1`, on the boundary when `|lambda|=1`, and
locally unstable when `|lambda|>1`.

## Exact boundary algebra

For `rho>=0`, put `d_m=|1-GammaTilde_m|`. Then

`|lambda(m,rho)| = rho d_m`.

If `d_m>0`, the unconstrained critical fraction is

`rho_c(m) = 1/d_m = 1/|1-GammaTilde_m|`.

On the protocol domain `0<=rho<=1`:

- if `d_m>1`, then `rho_c in (0,1)`, points below it are stable, the point at
  it is boundary, and points above it are unstable;
- if `d_m=1`, all `rho<1` are stable and `rho=1` is boundary;
- if `d_m<1`, every admissible `rho` is stable and the unconstrained boundary
  lies above one (or is infinite when `d_m=0`).

In the scientifically relevant observed regime `GammaTilde_m>1`, this becomes

`rho_c(m) = 1/(GammaTilde_m-1)`.

Thus:

- `GammaTilde_m>2`: an accessible boundary lies strictly below one;
- `GammaTilde_m=2`: full reuse, `rho=1`, is the boundary;
- `1<GammaTilde_m<2`: the algebraic `rho_c` exceeds one, so every admissible
  reuse fraction is locally stable.

For completeness, `GammaTilde_m<=1` is not forced into that sign convention.
The absolute-value formula is used. In particular, `0<GammaTilde_m<=1` gives
local stability throughout `rho in [0,1]`; `GammaTilde_m=0` gives a boundary
at full reuse; and `GammaTilde_m<0` would again admit an accessible positive
boundary. No such regime is assumed before measurement.

## Mechanical classification

Every final JSON cell stores `lambda` and exactly one of:

- `LOCALLY-STABLE` when `abs(lambda) < 1` outside numerical equality tolerance;
- `BOUNDARY` when `abs(abs(lambda)-1) <= 1e-12`;
- `LOCALLY-UNSTABLE` when `abs(lambda) > 1` outside that tolerance.

Point classification uses the point estimate of `GammaTilde_m`. Confidence
interval endpoints are propagated separately and may flag that a cell's class
is uncertainty-sensitive; they do not silently replace or smooth the point
estimate.

For `GammaTilde_m>1`, delta-method uncertainty is

`SE(rho_c) = SE(GammaTilde_m)/(GammaTilde_m-1)^2`.

When the 95% Gamma interval lies entirely above one, its monotone transformed
interval is

`[1/(Gamma_hi-1), 1/(Gamma_lo-1)]`.

If the interval reaches one, D4 reports the transformed interval as unbounded
rather than inventing a finite endpoint.

## Claim boundary

The boundary belongs to the local deterministic conditional-mean skeleton. It
is not an operational phase transition, detector-wide bifurcation statement,
distribution-free law, or assertion of a discontinuity in the stochastic
repeated-monitoring chain. Stage-D D2.5 remains the controlling operational
negative result.
