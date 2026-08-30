# Exact finite-support Arb certificate report

**Evidence class:** rigorous interval certificate for the finite-support
witness only.

## Frozen construction

`certificates/WITNESS.json` was hash-pinned before evaluation. Four baseline
paths have rational mass `1/4` each: a sign-symmetric pair with `tau=1` and
stopped sums `+3,-3`, and a sign-symmetric pair with `tau=6` and stopped sums
`+6,-6`. The long paths consist of six `+1` or six `-1` increments. Thus every
`m` in `{2,3,5}` has both short and full-window paths and a nonzero correction.

The construction principle was fixed before interval output: symmetry forces
`E_0[T_tau]=0`; the chosen path magnitudes give a nontrivial random-denominator
term; and `rho=1/10` and `rho=1/4` lie on opposite sides of the exact boundary
`2/13`. They were not selected after inspecting Arb results.

## Valid probability family and score

For positive rational masses `p(omega)`, define

```text
M(e)=sum p(omega) exp(-e T_tau(omega)),
P_e(omega)=p(omega) exp(-e T_tau(omega))/M(e).
```

Every summand is positive and finite for real `e`, so the finite normalizer is
strictly positive and finite. Division produces positive masses summing
algebraically to one on every real neighborhood of zero. Moreover
`M'(0)/M(0)=-E_0[T_tau]=0` by sign symmetry. Hence the score is analytically
and exactly `-T_tau`, independently of numerical normalization.

## Certified values

At 128-bit Arb precision, for each `m=2,3,5`:

```text
GammaTilde_m = 15/2,
F'_{1/10,m}(0) = -13/20,  abs = 13/20 < 1,
F'_{1/4,m}(0)  = -13/8,   abs = 13/8 > 1.
```

Thus attraction at `rho=1/10` and repulsion at `rho=1/4` are rigorously
certified for this witness. The exact short corrections are `9/4`, `3`, and
`18/5` at `m=2,3,5`. Arb encloses the direct value and fixed-plus-correction
value in the same rigorous ball. Central-difference errors decrease strictly
over dyadic steps `1/4,1/8,1/16,1/32` for every target `m`.

All required normalization, score, decomposition, sign, derivative,
convergence, attraction, and repulsion checks passed. Full balls and directed
lower/upper enclosures are stored in `certificates/certificate.json`.

## Evidence boundary

This certificate is not a multidimensional infinite-horizon interval solution
for the frozen Gaussian CUSUM. It rigorously validates the general theorem
architecture and selected stability inequalities on the exact finite-support
stopped-process instantiation only.
