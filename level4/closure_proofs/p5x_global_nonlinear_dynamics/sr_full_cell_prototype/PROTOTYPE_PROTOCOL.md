# P5X — SR full-cell prototype: FROZEN protocol

**Frozen before any prototype code is written or run.** Authorized by the R5
brief §20 condition, which R6 satisfies (`R6 GATE = PASS`, amplification
`1.0027e2 <= 1e12`, all `G1`-`G10`).

```text
detector   SR (symmetric two-chart Shiryaev-Roberts)
m          1
e cell     [24/100, 26/100]   exact rationals
target     R_{SR,1}(e) = e + g_0(x_0),  (I - K_e) g_0 = rho_{1,e},  x_0 = (0,0)
```

This is the frozen `P5X-T1(c)` selection map at `m = 1`, where the double sum is
empty. `b_SR = log(1+A)` throughout (`D1` erratum), `A` exact rational,
convention A, `[0,12]` and `m in {1,2,3,5}` untouched.

---

## 1. Certified statement to be produced

With `r := ghat - K_e ghat - rho_{1,e}` (the residual of an approximate
candidate) one has `(I - K_e)(ghat - g_0) = r`, hence

```text
| ghat(x_0) - g_0(x_0) |  <=  || (I - K_e)^{-1} ||_inf  *  || r ||_inf  =:  C * delta ,
R_{SR,1}(e)  in  e + ghat(x_0)  +/-  C * delta      for every e in the cell.
```

Three certified inputs are required: `C`, `delta`, and `ghat(x_0)`. The
candidate `ghat` itself is **not** proof evidence — only the residual it
produces is.

## 2. NEW ALGORITHM (frozen here): rigorous SR resolvent bound `C`

P5X has never built a rigorous `sup_x E_{x,e}[tau]` for SR. R1's monotone
Bellman minorant is CUSUM-specific (`k -> k - |e|`) and does not transfer.

**Construction.** Let `V_n(P)` be a rigorous upper bound on
`sup_{x in P} P_x(tau > n)` over a uniform `G x G` grid of cells `P` on
`[0, b_SR]^2` in the `y` coordinate. Set `V_0 = 1`. For the induction, fix a
uniform partition of `z` into `Z` sub-intervals over `[-c_SR, c_SR]`, and for a
cell `P = [yp_lo,yp_hi] x [ym_lo,ym_hi]`:

```text
widest continuation interval over P :  l_P = ym_lo - c_SR ,  u_P = c_SR - yp_lo
   (using the widest interval over the cell is CONSERVATIVE for an upper bound
    on P(tau > n+1), since a larger continuation region can only increase it)

for each z-sub-interval [z_a, z_b] intersected with (l_P, u_P):
    yp' in [ softplus(yp_lo + z_a - 1/2) , softplus(yp_hi + z_b - 1/2) ]
    ym' in [ softplus(ym_lo - z_b - 1/2) , softplus(ym_hi - z_a - 1/2) ]
       (softplus is increasing; yp' is increasing in z, ym' decreasing in z)
    W  = max of V_n over every grid cell meeting that box
    mass = an UPPER bound on int_{z_a}^{z_b} phi(z+e) dz, valid for ALL e in
           the cell (computed once in Arb, rounded outward, at the e in the
           cell maximising the mass)

V_{n+1}(P) = min( V_n(P) ,  sum over sub-intervals of  W * mass )   [*]
```

`[*]` the `min` is valid because `P_x(tau > n)` is non-increasing in `n`.

**Termination and the bound.** Iterate until `q := max_P V_{n_0} <= 1/2`. Then
`P_x(tau > j n_0) <= q^j` for all `x` and all `j`, so

```text
C = sup_x E_x[tau] = sup_x sum_{n>=0} P_x(tau > n)  <=  n_0 / (1 - q) .
```

**Floating-point rigour.** The `mass` values are computed once in Arb and
rounded **up** into float64. The iteration is a non-negative linear map, so each
sweep's float64 rounding is absorbed by multiplying the sweep result by
`(1 + 2^-40)`; over the frozen `n_0 <= 4000` sweeps this inflates `C` by at most
`4000 * 2^-40 < 4e-9` relative, which is recorded and included.

**Frozen parameters.** `G = 64`, `Z = 256`, `n_max = 4000`, `q_target = 1/2`.

## 3. Candidate solve (NOT proof evidence)

Bidegree `(16,16)` polynomial in `zeta = (xi-1)/A` on `[0,1]^2`, obtained by
collocation at the `17 x 17` tensor Chebyshev-Lobatto grid mapped to `[0,1]^2`,
solving the dense linear system `(I - K_{e_0}) ghat = rho_{1,e_0}` at the exact
cell centre `e_0 = 1/4` in float64. Any solver failure is a `FAIL`, not a
retry.

## 4. Residual bound `delta` (proof evidence)

`delta = max over the state grid of  |ghat - K_e ghat - rho_{1,e}|`, each cell
evaluated **as an Arb ball over the whole cell** with the R6 evaluator, at
**interval** `e = [24/100, 26/100]`. Inclusion isotonicity makes the per-cell
ball a valid bound for every state in the cell and every `e` in the cell, so the
maximum over cells bounds `|| r ||_inf` on the whole square. Grid `64 x 64`.

`rho_{1,e}` is evaluated in its stable form, since `1 - Phi(u+e)` cancels:

```text
rho_{1,e} = phi(u+e) - phi(l+e) - e * [ erfc((u+e)/sqrt2)/2 + erfc(-(l+e)/sqrt2)/2 ]
```

valid when `u+e >= 0` and `l+e <= 0`; otherwise the corresponding `Phi` is taken
on its own accurate `erfc` branch, exactly as R6 regime `D` does.

## 5. Frozen e-subdivision ladder

If the certified half-width exceeds the campaign's frozen stop-gate threshold
`0.2`, bisect the `e` cell and take the hull, to a maximum depth `4` (16
sub-cells). Depth is reported. The threshold `0.2` is **not** changed.

## 6. Frozen prototype gate `P1`-`P8`

```text
P1  the candidate solve succeeds and ghat(x_0) is finite
P2  delta is finite and the residual is evaluated on all 64x64 cells
P3  C is finite, with q <= 1/2 reached at some n_0 <= 4000
P4  certified half-width C*delta + (half-width of e + ghat(x_0)) <= 0.2
P5  z_panels = 0 and softplus_approximations = 0 on the certified path
P6  the enclosure is CONSISTENT with prior SR evidence (see section 7)
P7  wall time <= 3600 s and peak RSS <= 8 GiB on this 6-core machine
P8  e remains exact-rational-bounded (cell endpoints exact; no float e)

PROTOTYPE = PASS iff P1..P8.
```

## 7. Correspondence with prior SR evidence

There is no prior *certified* `R_{SR,1}` value in the campaign — SR was never
run to production, which is why this prototype exists. The available
independent checks, both **DIAGNOSTIC ONLY**:

* a Monte-Carlo estimate of `R_{SR,1}(0.25)` from the frozen recurrence;
* `R(e) -> e` as `e -> infinity`, and `R(0) = 0` by symmetry.

`P6` requires the certified interval to **contain** the Monte-Carlo point
estimate within its stated Monte-Carlo standard error. A Monte-Carlo estimate is
not rigorous and can therefore never *establish* the enclosure; it can only
**refute** it, which is the only direction `P6` uses.

## 8. Frozen prediction

```text
C            200 .. 900          (MC scoping gave E_{x_0}[tau] ~ 130 at e=0.25,
                                  ~472 at e=0; the certified sup over x and over
                                  the cell must exceed those)
delta        1e-12 .. 1e-6
C*delta      1e-9  .. 1e-3
half-width   dominated by the genuine variation of R over the cell, ~0.01
R_{SR,1}     around 0.25 .. 0.30
wall         60 .. 900 s
depth        0 (no subdivision needed)
verdict      PASS
```

Named risks: (i) interval-`e` dependency could inflate `delta` — the frozen
ladder of §5 is the only permitted response; (ii) the degree-16 candidate may
not resolve `rho_1` well enough near the reset corner, inflating `delta`;
(iii) the resolvent iteration may not reach `q <= 1/2` within `n_max = 4000`
if the grid is too coarse, which is a `P3` FAIL and stops this route.
