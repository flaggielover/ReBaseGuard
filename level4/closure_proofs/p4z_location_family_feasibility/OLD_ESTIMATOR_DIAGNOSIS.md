# P4Z Phase 4 — why the historical estimator failed, quantified

"Too noisy" is not a diagnosis.  This is the decomposition.

## 1. The historical Route A

```text
Xi_A = A_m * S_tau^psi,     Gamma_hat = (1/N) sum over paths of Xi_A
```

**Expectation.**  `E[Xi_A] = Gamma_{D,m,f}` exactly, by G1a.  Unbiased.  No
part of the P4 or P4X record shows otherwise, and P4X's anchor phase reproduced
48 frozen comparisons at `1e-12` with 0 mismatches.  **The old estimator is
correct.  It is only unusable.**

**Variance.**  Split the summand at the alarm step.  On `{tau = n}`,

```text
A_m = (Z_n + B_{n,m}) / w,       B_{n,m} = sum_{r=1}^{w-1} Z_{n-r}
S_tau^psi = P_{n-1} + psi(Z_n),  P_{n-1} = sum_{t<n} psi(Z_t)
```

By the bounded-survival lemma every `Z_{n-r}` with `r >= 1` obeys
`|Z_{n-r}| < c_D`, so `|B_{n,m}| < (m-1) c_D`.  For a bounded-score family
`|psi| <= M`, so `|P_{n-1}| <= M(n-1)` and `|psi(Z_n)| <= M`.  Therefore

```text
Xi_A = (Z_n / w) * P_{n-1}          <- the only unbounded term
     + (Z_n / w) * psi(Z_n)         <- bounded: |z psi(z)| is bounded for t
     + (B_{n,m} / w) * S_tau^psi    <- bounded by (m-1) c_D M n / w
```

The first term is the whole problem.  `Z_tau` is the alarm-causing increment;
for large `|z|` every state alarms, so `Z_tau` inherits the base law's tail
exactly.  For `t1p5`, `P(|Z| > x) ~ C x^{-1.5}`, hence

```text
E[Xi_A^2] >= E[(Z_tau P_{tau-1} / w)^2] = infinity
```

and no batching repairs it: block means of tail-index-`alpha` summands keep
tail index `alpha`.  The dominant term is *one coordinate of one step of the
path*.

**Measured, on 200 000 paths (`micropilots/diagnostics/micropilot.json`).**

| cell | Hill index of `Xi_A` | top-1 share of squared deviation | per-path sd |
|---|---|---|---|
| `t1p5/cusum@5`, m=1 | 1.5–1.6 | 0.297 | 105.5 |
| `t1p5/sr@520.886`, m=1 | 1.5–1.6 | **0.975** | 518.1 |
| `t1p5/sr@20`, m=1 | 1.5–1.6 | 0.436 | 33.5 |
| `t3/cusum@5`, m=1 | ~3.1 | 0.010 | 156.1 |
| `gaussian/cusum@2`, m=1 | ~6.4 | 0.003 | 6.2 |

The measured Hill index reproduces the theoretical `alpha = 1.5`.  On the
frozen SR operating point a **single path out of 200 000 carries 97.5 % of the
sample variance** — the sample standard deviation there is essentially the
largest observation, which is the definition of an unusable scale estimate.

**Scaling.**  For `alpha < 2` the sample mean of `N` draws converges at
`N^{-(1-1/alpha)} = N^{-0.32}` in distribution to an `alpha`-stable law, not at
`N^{-1/2}` to a normal.  P4X's heavy-tail policy patched the exponent
(`kappa = 1 - 1/alpha`) correctly but kept a *standard error* as the
uncertainty, and an `alpha`-stable limit has no standard error.  That is why
buying more paths kept failing: the target `r*` is a property of a distribution
that does not exist for this summand.

**Scaling with the detector.**  The dependence on the operating point is not
through `alpha` but through the *frequency* of a large `Z_tau`.  A high
threshold means a long `tau`, hence a larger `P_{tau-1}`, hence a larger
multiplier on the heavy increment — which is exactly the ordering observed:
`sr@520.886` is worse than `cusum@5`, which is worse than `sr@20`.

**Scaling with `m`.**  Mild.  Larger `m` divides the heavy increment by a
larger `w`, so the per-path sd falls roughly like `1/m` while the tail index is
unchanged.  Measured: 105.5, 52.9, 35.4, 21.7 for `m = 1,2,3,5` on
`t1p5/cusum@5`.  This is why the `m=1` cells dominate the unresolved set.

## 2. The historical Route B

```text
Xi_B = -(A_m^{(+h)} - A_m^{(-h)}) / (2h),   Richardson-combined over h, h/2
```

Under common random numbers the two shifted runs share `eps`.  Since
`Z = eps - e`, on any path where the two runs stop at the same time **and** the
window indices coincide, `A_m^{(+h)} - A_m^{(-h)} = -2h` exactly and the path
contributes exactly `1`.

So `Xi_B = 1 + D`, where `D` is supported on the rare set where the two runs
disagree, and on that set `D = O(Z_tau / 2h)`: the family's full tail, amplified
by `1/(2h) ∈ {10, 20}`.  Route B is a rare-event estimator of a heavy-tailed
jump.  Its measured cost is the signature: **2 255 250 000 paths and 66 759
CPU-seconds** for `frozen/cusum@5/t1p5` to reach relSE `0.0062`, against 93 500 000
paths and 198 CPU-seconds for Route A on the same cell.

Measured per-path sd of `Xi_B` on 60 000 paths for that cell: **138.5**, with a
Hill index of `1.46` and a top-1 share of `0.195`.  Reconstructing the scale
implied by P4X's own 2.255e9-path result gives ≈ **1044** — a factor of 7.5
larger than the 60 000-path estimate, which is itself a direct measurement of
F-03: at these tail indices the sample sd systematically under-reports.

## 3. Covariance structure, and why the obvious fixes died

The two routes share nothing (different seeds, different modes), so
`cov(Xi_A, Xi_B) = 0` by construction and the combined-error statistic is
correct as written.

Within a route, P4X's R0 pilot measured four variance-reduction candidates and
rejected all four.  The reasons are structural, not incidental:

* **reflection-antithetic**: pathwise exact and distributionally valid for
  symmetric families, but VRF `0.001–0.003` — a 300–1000x variance *increase*,
  because substituting the mirror for the `-h` run destroys the CRN
  cancellation that supplies Route B's exact `1`.
* **Corollary-G2 control variate**: per-path variance `6e-29` to `9e-31`, i.e.
  identically zero.  That is Corollary G2's own content — the control has no
  variance to lend.
* **coarse FD step**: inadmissibly biased for `skewnormal4`.
* **fine FD step**: variance *increase* by a factor 0.32–0.55, the classic
  CRN-difference blow-up as `h` shrinks.

P4Z's own FD ladder reproduces the last point independently: on
`t1p5/sr@520.886`, the central-difference standard error roughly doubles from
`h = 0.05` to `h = 0.0125`, while the `O(h^2)` truncation offset shrinks by the
expected factor of four from `h = 0.2` to `h = 0.1` (`-0.0918` to `-0.0211`,
ratio 4.36).  The frozen pair `(0.05, 0.025)` sits where truncation is already
below Monte Carlo noise.  **The frozen finite-difference convention is sound and
P4Z keeps it unchanged.**

## 4. The answer

The old estimator failed because a single coordinate of the path — the
alarm-causing increment `Z_tau` — carries the innovation law's tail into the
per-path summand, multiplied by a factor (`P_{tau-1}` in Route A, `1/2h` in
Route B) that grows with the operating point.  Everything else in both summands
is bounded by the detector's own forcing increment.

The dominant term is therefore not diffuse.  It is one term, and it is
integrable in closed form.
