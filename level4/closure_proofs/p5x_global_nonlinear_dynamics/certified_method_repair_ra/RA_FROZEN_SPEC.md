# R-A′ frozen certified-method repair specification

Frozen **before** any R-A′ result exists. Hashed into `RA_PROTOCOL_DIGEST.json`
and committed at the R-A pre-result anchor. No parameter below may be chosen or
changed after observing an R-A′ number.

R-A′ is a **repair of the certified numerical realisation only**. The certified
equation, the reduction `P5X-T1`, the human proofs `L1`, `L2`, `L3`, `L5`, `L6`
and every P5X theorem statement are unchanged. `RA_FEASIBILITY_AUDIT.md` §2
records why R-A's literal form does not compose with this architecture and what
R-A′ substitutes for it.

---

## 1. The certified equation — unchanged

For the frozen CUSUM (`k = 1/2`, `h = 5`, inclusive post-update test), state
`x = (p, m) in [0, 5]^2`, innovation `z`, continuation interval
`(l(x), u(x)) = (m - 11/2, 11/2 - p)`, state map
`q(x, z) = (max(0, p + z - 1/2), max(0, m - z - 1/2))`, reset `x_0 = (0,0)`:

```text
(K_e f)(x) = int_{l(x)}^{u(x)} f(q(x,z)) phi(z + e) dz
rho_{1,e}(x) = phi(u+e) - phi(l+e) - e ( 1 - Phi(u+e) + Phi(l+e) )
g = K_e g + rho_{1,e} ,        R_{CUSUM,1}(e) = e + g(x_0; e)     [PROOF.md L1.7]
```

The **unshifted** innovation variable `z` is used throughout, so `l`, `u`, the
reset kinks `alpha = 1/2 - p`, `beta = m - 1/2` and `q` contain no `e`.

## 2. Representation (Device 1 — recentring)

```text
phi(z + e) = sum_{i=0}^{N} b_i(e) z^i + Rem_N(z; e) ,   b_i(e) = (-1)^i He_i(e) phi(e) / i!
He_0 = 1 ,  He_1 = e ,  He_{i+1}(e) = e He_i(e) - i He_{i-1}(e)          (exact for rational e)
|Rem_N(z;e)| <= eps_rec(N) := 0.4333 * (11/2)^{N+1} / sqrt((N+1)!)       (Cramer; e-free)
```

with the constant `0.4333 >= 1.086 / sqrt(2 pi)` from Cramér's inequality
`|He_n(x)| e^{-x^2/4} <= 1.086 sqrt(n!)`.

Reward arguments are recentred likewise: `phi` and `Phi` at `u + e` are expanded
about `3 + e` in the `e`-free variable `5/2 - p`, and at `l + e` about `-3 + e`
in `m - 5/2`; remainder `<= 0.4333 (5/2)^{N+1} / sqrt((N+1)!)` and its integral.

**Frozen degree:** `N = 120`.

## 3. Derivative equation

```text
d_e g = K_e d_e g + (d_e K_e) g + d_e rho_{1,e}
d_e b_i = (i + 1) b_{i+1}
d_e rho_{1,e}(x) = -(u+e) phi(u+e) + (l+e) phi(l+e) - (1 - Phi(u+e) + Phi(l+e))
                   + e ( phi(u+e) - phi(l+e) )
```

certified by the same residual machinery at the same exact rational `e_0`.

## 4. Candidates (not proof evidence)

Tensor-Chebyshev collocation, **degree 12**, quadrature order **400**,
coefficients rounded to exact dyadic rationals at **`scale_bits = 50`**, for
both `ghat` (value equation) and `ghat'` (derivative equation). The floating
solver leaves the proof path at that point.

## 5. Interval arithmetic policy and precision

python-flint / FLINT-Arb outward-rounded real balls, working precision
**256 bits**, minimum-precision guard active. Every stored quantity serialised
as `ball`, `lower_enclosure`, `upper_enclosure`. All model constants exact
rationals (`k = 1/2`, `h = 5`). Every `e_0` is an exact rational with
denominator `10^7`. **No interval-valued `e` ever enters the symbolic chain.**

## 6. Residual certification rule

Unchanged from the inherited architecture and reused by import: exact dyadic
candidate substituted into `q`, multiplied by the recentred coefficient list,
integrated in `z` symbolically over the three reset panels in both `p+m <= 1`
and `p+m >= 1` regimes, then bounded on the **continuum** of the reachable set
(`p = r t`, `m = r(1-t)`; `r in [0,1]`, `r in [1,4]`, axis tails `r in [4,5]`)
by tensor Bernstein conversion at **subdivision depth 3**. No state is sampled.

```text
delta  = BernsteinResidual(value)      + (11 sup|ghat|  + 2 + 2 e_hi (11/2 + e_hi)) * eps_rec(N)
delta' = BernsteinResidual(derivative) + (11 sup|ghat'| + 11 sup|ghat| + 2 + 2 e_hi (11/2 + e_hi)) * eps_rec(N)
```

(the extra `11 sup|ghat|` in `delta'` covers the `(d_e K_e) ghat` term).

## 7. Resolvent handling

Drift-explicit block forcing, proved from scratch, no imported constant, no
monotonicity in `e` assumed: from any live state `S^+_n >= G_n - n k` and
`S^-_n >= -G_n - n k`, so with `G_n ~ N(-ne, n)`

```text
q_n(e) = Phi( -(h+nk)/sqrt(n) - e sqrt(n) ) + Phi( -(h+nk)/sqrt(n) + e sqrt(n) ) ,
||(I - K_e)^{-1}||_inf <= n / q_n(e) ,     minimised over n in {1..60} ,
```

evaluated on the **gate cell's** `e`-interval and read at its lower endpoint, so
one constant `C` is valid for every sub-cell.

## 8. Sub-cell construction (Device 2)

```text
a := 2 phi(0) = 0.7978845608...            (>= ||d_e K||_inf)
h := 1 / (4 a C)                            (frozen formula; C from section 7)
n_sub := ceil( (e_hi - e_lo) / (2 h) )      sub-cells of equal half-width h' = (e_hi-e_lo)/(2 n_sub) <= h
e_0^{(j)} := the sub-cell midpoint, rounded to an exact rational with denominator 10^7,
             with the sub-cell then *widened* to contain its declared range
```

`C`, `h` and `n_sub` are computed **before any residual is evaluated** and are
recorded in the result artifact.

## 9. Bootstrap and enclosure formulas (frozen)

```text
b2 := 4 phi(1) = 0.9678828981...           (>= ||d_e^2 K||_inf)
c2 := 1.13788 + b2 * e_hi                  (>= sup |d_e^2 rho_1|)
G0 := sup|ghat|  + C delta                 G1 := sup|ghat'| + C delta'
S2 := 2 C ( 2 a G1 + b2 G0 + b2 h' G1 + c2 )         [valid because C(2 a h' + b2 h'^2) <= 1/2]

per sub-cell j:
  g_encl   = ghat(x_0) +/- C delta
  dg_encl  = ghat'(x_0) +/- C delta'
  R_encl_j = [e_lo^j, e_hi^j] + g_encl + [-h', h'] * dg_encl + [-1, 1] * (h'^2 / 2) * S2

gate enclosure = hull over j of R_encl_j
achieved half-width = radius of that hull
```

## 10. Stop-gate cell (unchanged from the failed gate)

```text
detector = CUSUM (k = 1/2, h = 5)
m        = 1
e-cell   = [0.24, 0.26]
```

The **same scientifically binding cell** as the failed gate: it contains
`argmax_e |R_{CUSUM,1}|`, carries the campaign's tightest margin to `2`, sits in
the steepest part of the map and has nearly the worst-case resolvent. It is not
changed, not narrowed and not moved. The internal sub-cell decomposition is an
enclosure device: the certified object is still `R` over the whole cell
`[0.24, 0.26]`, obtained as the hull.

## 11. Threshold and verdict semantics (unchanged)

```text
achieved half-width <= 0.2   ->  RA_STOP_GATE = PASS
achieved half-width >  0.2   ->  RA_STOP_GATE = FAIL
```

Applied mechanically to the hull half-width of §9. Not reinterpretable.

## 12. Mandatory gates before the stop-gate may run

1. **`e = 0` self-test**, five checks, all mandatory:
   * `S1` **coefficient identity** — `phi_taylor_coefficients(N, 0)` must contain
     the plain Maclaurin list `(-1)^n / (sqrt(2 pi) 2^n n!)` at every even index
     and `0` at every odd index (this is `He_i(0)` evaluated exactly);
   * `S2` **reward accuracy** — at a fixed set of exact rational states in the
     reachable set, the recentred reward polynomial must enclose the exact
     `rho_{1,e}` computed directly from Arb `phi`/`erf`, to within the frozen
     reward truncation allowance;
   * `S3` **kernel-weight accuracy** — at fixed exact rational `z` spanning
     `[-11/2, 11/2]` and at `e in {0, 1/4}`, `sum_i b_i(e) z^i` must enclose
     `phi(z+e)` to within `eps_rec(N)`;
   * `S4` **residual containment** — the R-A′ Bernstein residual at `e = 0` must
     lie within the certified `Gamma` `a`-equation residual
     `3.0027342099356678e-6` plus or minus the **sum of the two representations'
     own truncation allowances**. Exact digit agreement is *not* required and
     must not be asserted: the two representations truncate differently, so the
     correct test is interval containment, not equality;
   * `S5` `ghat(0,0)` must enclose `0` with `|ghat(0,0)| < 1e-12` (`P5-T3`).

   **If any of `S1`-`S5` fails, STOP; the stop-gate must not be run.**

2. **Radius-scaling diagnostic.** Re-run the value-equation residual with the
   *old* interval-`e` policy at radii `{0, 1e-8, 1e-6, 1e-4}` under the R-A′
   representation, to measure whether recentring alone changed the dependency
   constant. Reported, never used to choose a parameter.
3. **Far-field truncation diagnostic.** Evaluate `eps_rec(120)` and the R-A′
   truncation allowance at `e in {0, 0.26, 6.5, 12}` and confirm each is finite
   and below `1e-6`, against the failed method's `7.04e44` at `e = 12`.

## 13. Retry ladder and maximum refinement

**There is no retry ladder.** `h` is a closed formula of `C`; there is exactly
one admissible configuration, and it is fully determined before the first
residual. Maximum refinement is therefore `n_sub` as computed in §8, and no
adaptive escalation is authorised.

## 14. Abort rule

The run aborts, and the gate is recorded `FAIL`, if any of the following occurs:
the `e = 0` self-test fails; any Arb positivity or containment check raises; the
bootstrap closure condition `C (2 a h' + b2 h'^2) <= 1/2` is not verified in
interval arithmetic; a sub-cell's declared range is not contained in its `e`
ball; or the sub-cells do not tile `[0.24, 0.26]` exactly. No retry, no
parameter change, no partial-cover substitution.

## 15. R-B fallback semantics (pre-frozen, and deliberately not auto-invoked)

R-B is the Bernstein-variable representation: lift the residual algebra from
`(p, m)` to `(p, m, e)` and take the continuum range bound jointly over the
reachable set times the `e`-cell.

**Pre-frozen semantics:** if R-A′ fails its stop-gate, R-B is **not** invoked in
the same session and **not** improvised. It requires its own pre-result anchor,
its own specification with the same content as this document, and its own
declared stop-gate on the same cell at the same threshold. Invoking R-B without
that is prohibited. This clause exists so that an R-A′ failure produces a stop,
not a scramble.

## 16. Scope carried forward

`errata/D1_SR_DOMAIN_ERRATUM.md` applies: any future SR certified work under
R-A′ must use `b_SR = log(1 + A)` and cite the erratum. **No SR work is
performed under this specification** — R-A′ is CUSUM-only, and the SR code path
is kept separate.
