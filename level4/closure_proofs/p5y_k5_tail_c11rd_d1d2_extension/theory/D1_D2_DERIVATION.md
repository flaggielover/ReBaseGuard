# C11RD — independent derivation of the D1 / D2 certificate (cell 306)

Derived from the operator statement (docs/D1_D2_STATEMENT_AUDIT.md sections 2–4), NOT from the
original derivative code. Every step the certificate relies on is stated here as a lemma with its
proof; the implementation (`code/`) is a direct transcription and each module names the lemma it
implements.

## 0. Setting

* `K = 1/2`, `C = 11/2`, `R = {(p, m) in [0, 5]^2 : p + m <= 4 or p = 0 or m = 0}`, atom `a = (0, 0)`,
  `s = p + m`. `B(R)`: bounded measurable functions on R with the sup norm `||.||`.
* For `x in R` and drift `e`: window `[l, u] = [m - C, C - p]`, map `x'(z) = (max(0, p + z - K),
  max(0, m - z - K))`, atom window `A(x) = [m - K, K - p]` if `s < 1`, else empty.
* `Khat_e f(x) = int_{[l,u] \ A(x)} f(x'(z)) phi(z + e) dz`;
  `Khat_e^(i) f(x) = int_{[l,u] \ A(x)} f(x'(z)) phi^(i)(z + e) dz`, where
  `phi^(i)(y) = d^i phi / dy^i = (-1)^i He_i(y) phi(y)` (probabilists' Hermite polynomials).
* `h_1(x; e) = 1 - Phi(u + e) + Phi(l + e)`, `h_1^(j) = d^j h_1 / de^j = -phi^(j-1)(u + e) +
  phi^(j-1)(l + e)` for `j >= 1`.
* `E = [680769/400000, 17885921/10000000]` (cell 306), tiled by sub-blocks `E_j`.

## 1. Invariance and piece structure

**Lemma 0 (R is invariant).** For `x in R` and `z in [l, u]`, `x'(z) in R`.
*Proof.* `p' = p + z - K <= p + (C - p) - K = 5` and likewise `m' <= 5`. If exactly one of `p', m'` is
positive, `x'` lies on an axis. If both are positive, `z in (K - p, m - K)` (requiring `s > 1`) and
`p' + m' = s - 1 <= 4` because `s <= 5` on R. ∎

**Lemma 1 (pieces).** Let `x in R` with `s in [k, k + 1]`, `k in {0, .., 4}` (`k = 4` only on the axes).
Put `l0 = 0` if `k = 0` and `l0 = s - 1` otherwise. Then `[l, u] \ A(x)` is the union of
* the LEFT ARM `z in [l, z_L]`, `z_L = m - K` (`k = 0`) or `K - p` (`k >= 1`), with image `(0, m')`,
  `m' = m - K - z` decreasing from 5 to `l0`;
* the RIGHT ARM `z in [z_R, u]`, `z_R = K - p` (`k = 0`) or `m - K` (`k >= 1`), with image `(p', 0)`,
  `p' = p + z - K` increasing from `l0` to 5;
* for `k >= 1`, the MIDDLE `z in [K - p, m - K]`, image `(p + z - K, m - z - K)` on the line
  `s' = s - 1` (so in band `k - 1`).
Splitting each arm where its image crosses an integer `j` (`m' = j` at `z = m - K - j`; `p' = j` at
`z = j + K - p`) makes the image of every piece lie in ONE band `j` (`j = k - 1` for the partial
piece starting at `l0`, then `j = k, .., 4`). On every piece the image is affine in `z`.
*Proof.* `p' > 0` iff `z > K - p`, `m' > 0` iff `z < m - K`; `K - p <= m - K` iff `s >= 1`. The three
ranges follow; the endpoint values of `m'`, `p'` are direct substitution (`m - K - l = C - K = 5`,
`m - K - (K - p) = s - 1`). ∎

Consequence: for a band-piecewise polynomial `f` (one polynomial per band; band `j`'s polynomial
restricted to an axis on the arms), `Khat^(i)_e f(x)` is a finite sum of integrals
`int_alpha^beta Q(y) phi(y) dy` with `y = z + e`, `Q` a polynomial whose coefficients are polynomials
in `(p, m, e)`, and `alpha, beta` affine in `(p, m, e)`. The piece structure is the same for all
`x` in a closed band, so these formulas are analytic in `(p, m, e)` on each closed band.

**Upper-closed convention (C11RD-R1; replaces the lower-closed "half-open convention" of the
predecessor freeze, review B-1).** The candidate is ONE function on R. Its value at a state
`x = (p, m)` of R is the polynomial of the band that OWNS `x`:

    own(x) = 0  if s in [0, 1];     own(x) = k  if s in (k, k + 1], k = 1, 2, 3 (axis points included);
    own(x) = 4  if x is an axis point with s in (4, 5].

Interior points (`p, m > 0`) of R have `s <= 4`, so band 4 is owned only on the axes; the axis
polynomial of band `j <= 3` is band `j`'s polynomial restricted to the axis. (`code/c11rd_certify.py:
owner_band`.)

**Proposition 1 (the closed-box cover evaluates exactly this candidate).** Let the cover consist of
closed boxes, each inside ONE closed band: for `k = 0..3`, `{s in [s0, s1] subset [k, k + 1],
theta in [t0, t1] subset [-1, 1]}` with `p = s (1 + theta)/2`, `m = s (1 - theta)/2`; for band 4,
axis segments `s in [s0, s1] subset [4, 5]`. On a box of band `k` the certifier evaluates (Lemma 1)
the state value with band `k`'s polynomial, the MIDDLE piece with band `k - 1`'s polynomial, and
the arm piece of image band `j` with band `j`'s axis polynomial. Suppose that for each `k = 0..3` the
band-`k` boxes partition the closed strip `[k, k + 1] x [-1, 1]` in `(s, theta)`, and for each axis
the band-4 boxes partition `[4, 5]`. Then:
(a) every `x in R` lies in a box of band `own(x)` (no gap, band lines included);
(b) on every box of band `own(x)` that contains `x`, the certifier's residual formula at `x` is
    EXACTLY the residual of the single-valued candidate at `x`;
(c) a box of any other band that contains `x` (necessarily at its lower edge `s = own(x) + 1`, or a
    band-4 box at `s = 4` on an axis) computes a quantity that is not the candidate's residual; its
    bound only enlarges `lam_k = max over boxes`, so it can never make a certified bound smaller.
Hence `sup_R |r_k| <= lam_k`, as Theorem 5 requires. Refinement bisects a box into boxes of the SAME
band that partition it (validation V22), so the leaves satisfy the partition hypothesis whenever the
initial boxes do.
*Proof.* (a) If `own(x) = k <= 3`, then `s in [0, 1]` or `s in (k, k + 1]`, so `(s, theta)` lies
in the closed strip `[k, k + 1] x [-1, 1]` (theta is arbitrary at the atom `s = 0`), which band
`k`'s boxes partition; if `own(x) = 4`, `x` is an axis point with `s in (4, 5] subset [4, 5]`. (b)
The state value is band `own(x)`'s polynomial, which is the candidate's value. The middle image
lies on `s' = s - 1`: for `s in (k, k + 1]` it lies in `(k - 1, k]` (off the axes), which band
`k - 1` owns: the certifier's choice. For `own(x) = 0` there is no middle (`s <= 1`; at `s = 1` it
has length zero). An arm piece of image band `j` has image `m'` (or `p'`) in `[j, j + 1]` on an axis;
`own` gives band `j` on `(j, j + 1]`, and the single point `m' = j` has measure zero for the
integral. The partial piece `[s - 1, k]` is band `k - 1`'s for the same reason, and the band-4 arm
pieces use the band-4 axis polynomial on `(4, 5]`. So every integrand coincides with the
candidate's almost everywhere on its piece. (c) is immediate. ∎

The predecessor's lower-closed reading (`s = k + 1` owned by band `k + 1`) fails exactly on the
INTERIOR line `s = 4`: those points would be owned by a band 4 that has no interior boxes, and the
only boxes containing them (band 3) use band 2 on the middle (review B-1). Under the upper-closed
convention the same cover and the same code are complete. Mechanical checks:
`c11rd_certify.verify_cover` proves the partition hypothesis EXACTLY for the frozen cover (and the
runner refuses to start without it, guard R6); `c11rd_certify.owning_boxes` / `verify_ownership`
implement (a); validation V24 evaluates a candidate with deliberate jumps at `s = 1, 2, 3, 4` just
below, on, and just above every line (interior and axes) through the production owner, cover and
kernel code, and shows the reversed convention failing.

## 2. Drift derivatives of the kernel

**Lemma 2.** For `f in B(R)`, `e -> Khat_e f` is infinitely differentiable in `B(R)` with
`d^i/de^i Khat_e f = Khat_e^(i) f`, and `||Khat_e^(i)|| <= kappa_i := int_R |phi^(i)(y)| dy`.
Moreover `kappa_1 = 2 phi(0)` and `kappa_2 = 4 phi(1)`.
*Proof.* The windows do not depend on `e` in the `z` variable; differentiate under the integral
(dominated convergence, `|phi^(i)|` integrable), and `|Khat^(i) f| <= ||f|| int |phi^(i)|`. `phi'`
changes sign only at 0: `int |phi'| = 2 phi(0)`. `phi'' = (y^2 - 1) phi = -(y phi)'` changes sign at
`+-1`: `int |phi''| = 2 [y phi]` evaluated to give `4 phi(1)`. ∎

## 3. The premise and the resolvent (C11R F_H)

**Lemma 3.** Suppose `w in B(R)`, `w >= 0`, and `w >= 1 + Khat_e w` on R for every `e in E` (C11R's
ACCEPTED certificate F_H: `w = 3429/500 - (1113/1000) m`). Then for `e in E`:
(i) `sum_{n < N} Khat_e^n 1 <= w - Khat_e^N w <= w`, so `Ghat_e f := sum_n Khat_e^n f` converges for
every `f in B(R)` and `|Ghat_e f| <= ||f|| Ghat_e 1 <= ||f|| w`;
(ii) `||Ghat_e|| <= C_T := sup_R w = 3429/500` and `|(Ghat_e f)(a)| <= ||f|| tau`, `tau := w(a) =
3429/500`;
(iii) for `g, f in B(R)`: `g = f + Khat_e g` iff `g = Ghat_e f`.
*Proof.* (i) induction on `N` using positivity of `Khat_e`; (ii) `sup_R w = 3429/500` because the
m-coefficient is negative and `m >= 0` on R; (iii) iterate: `g = sum_{n<N} Khat^n f + Khat^N g`, and
`|Khat^N g| <= ||g|| Khat^N 1 -> 0` because `sum Khat^n 1` converges. ∎

## 4. Differentiability of d and the derivative equations

**Lemma 4.** Let `d_e = Ghat_e h_1(.; e)`. On E, `e -> d_e` is twice differentiable in `B(R)` and
`d' = Ghat(Khat' d + h_1')`, `d'' = Ghat(Khat'' d + 2 Khat' d' + h_1'')`; equivalently
`d = Khat d + h_1`, `d' = Khat d' + Khat' d + h_1'`, `d'' = Khat d'' + 2 Khat' d' + Khat'' d + h_1''`.
*Proof (C11RD-R1: explicit at the endpoints of E and of every sub-block; review N-1).* Four steps,
no appeal to "continuity".

(a) *A geometric rate on E.* For `e in E`, `w >= 1 + Khat_e w` with `Khat_e w >= 0` gives `w >= 1`,
and `w <= C_T := sup_R w`. Hence `1 >= w / C_T` and `w >= w / C_T + Khat_e w`, i.e.
`Khat_e w <= q w` with `q := 1 - 1/C_T < 1`. Positivity gives `Khat_e^N w <= q^N w`, and since
`1 <= w`: `||Khat_e^N|| = ||Khat_e^N 1|| <= ||Khat_e^N w|| <= q^N C_T`.

(b) *An open neighbourhood U of E on which the SAME Neumann series converges.* `||Khat_f|| <= 1`
for every drift `f` (`Khat_f 1 <= 1`), and `||Khat_f - Khat_e|| <= kappa_1 |f - e|` (Lemma 2, mean
value). Fix `N` with `q^N C_T <= 1/2`. For `e_0 in E` and `|f - e_0| <= rho := 1/(4 N kappa_1)`,
`||Khat_f^N - Khat_{e_0}^N|| <= sum_{i<N} ||Khat_f||^i ||Khat_f - Khat_{e_0}|| ||Khat_{e_0}||^(N-1-i)
<= N kappa_1 rho = 1/4`, so `||Khat_f^N|| <= 3/4`. Then `Ghat_f := sum_n Khat_f^n` converges in
operator norm with `||Ghat_f|| <= 4 N`, equals `(I - Khat_f)^(-1)`, and is the same probabilistic
object that defines `d` (the Neumann series), on `U := E + (-rho, rho)`.

(c) *Differentiability on U.* For `e, f in U` the resolvent identity `Ghat_f - Ghat_e = Ghat_f
(Khat_f - Khat_e) Ghat_e` holds (both are genuine inverses) with the uniform bound `4 N`. By Lemma 2,
`||Khat_f - Khat_e - (f - e) Khat'_e|| <= kappa_2 (f - e)^2 / 2`, so `e -> Ghat_e` is differentiable
in operator norm on U with `Ghat' = Ghat Khat' Ghat`, and twice by the product rule; `e -> h_1(.; e)`
is smooth. The derivative formulas and equations above hold at every `e in U`. Because E is a
closed subset of the OPEN set U, the derivatives at `e_lo` and `e_hi` are ordinary TWO-SIDED
derivatives: the statement "for every e in the block: |D_e'| <= D1" involves no one-sided
convention at the endpoints.

(d) *The certificate at the endpoints of E and of every sub-block.* The sub-blocks `E_j` are CLOSED
and tile E exactly (neighbours share their endpoint; `c11rd_certify.sub_blocks`, exact rationals).
Each residual Taylor model is a polynomial in `u_e in [-1, 1]` plus a remainder valid for every
`u_e` in the closed interval, so it encloses the residual at `e = e_c +- de` (`u_e = +-1`), both
endpoints of `E_j`. F_H is certified for every `e` of the CLOSED block E (C11R's statement), so
Lemma 3 holds at the endpoints too. Theorem 5 is pointwise in `e`: at every `e in E_j`, endpoints
included, all its hypotheses are verified directly; at a shared endpoint the bounds of both
neighbouring sub-blocks hold, and the cell bound (their maximum) holds there. Validation V25 checks
the endpoint enclosures (`u_e = +-1`) against an independent evaluation at the exact endpoints. ∎

## 5. Candidates, residuals and error propagation (the certificate)

**Theorem 5.** Fix a sub-block `E_j`. Let `D0(e), D1(e), D2(e) in B(R)` for `e in E_j` and put
`r0 = D0 - Khat D0 - h_1`, `r1 = D1 - Khat D1 - Khat' D0 - h_1'`,
`r2 = D2 - Khat D2 - 2 Khat' D1 - Khat'' D0 - h_1''` (all at the same `e`), with
`||r_k|| <= lam_k` for every `e in E_j`. Then for every `e in E_j`, with
`n0 = C_T lam0` and `n1 = C_T (lam1 + kappa_1 n0)`:

    |d'_e(a) - D1(e)(a)|  <= tau (lam1 + kappa_1 n0),
    |d''_e(a) - D2(e)(a)| <= tau (lam2 + 2 kappa_1 n1 + kappa_2 n0).

*Proof.* Put `e0 = d - D0`. Subtracting `D0 = Khat D0 + h_1 + r0` from `d = Khat d + h_1` gives
`e0 = Khat e0 - r0`, so `e0 = -Ghat r0` (Lemma 3(iii)): `||e0|| <= n0`. With `e1 = d' - D1`, Lemma 4
gives `e1 = Khat e1 + Khat' e0 - r1`, so `e1 = Ghat(Khat' e0 - r1)`, `|e1(a)| <= tau (kappa_1 n0 +
lam1)` and `||e1|| <= n1`. With `e2 = d'' - D2`, `e2 = Ghat(2 Khat' e1 + Khat'' e0 - r2)`, so
`|e2(a)| <= tau (2 kappa_1 n1 + kappa_2 n0 + lam2)` (Lemmas 2, 3(ii)). ∎

**Corollary (the statements D1\*, D2\*).** With `D1_j := sup_{e in E_j} |D1(e)(a)| + tau (lam1 +
kappa_1 n0)` and `D2_j := sup_{e in E_j} |D2(e)(a)| + tau (lam2 + 2 kappa_1 n1 + kappa_2 n0)`:
for every `e in E`, `|d'_e(a)| <= max_j D1_j` and `|d''_e(a)| <= max_j D2_j`, because the `E_j` tile E.
The premise enters only through `C_T` and `tau` (Lemma 3); no original constant is used.

**Choice of candidates (does not affect soundness).** C11RD uses `e`-Taylor candidates about the
sub-block centre `e_c`, `h = e - e_c`: `D0(e) = D0 + h D1 + h^2/2 D2 + h^3/6 D3`,
`D1(e) = D1 + h D2 + h^2/2 D3`, `D2(e) = D2 + h D3`, with `D_k` band-piecewise polynomials
approximating the solutions of the chain at `e_c` (including `d''' = Ghat(Khat''' d + 3 Khat'' d' +
3 Khat' d'' + h_1''')`). Formally, the residuals then vanish through order 3 (resp. 2, 1) in `h`, so
the sub-block width costs little; whatever does not cancel is simply part of the rigorously enclosed
residual. `sup |D1(e)(a)|` and `sup |D2(e)(a)|` are bounded exactly: `D_k(a)` is the constant
coefficient of band 0's polynomial, and `|c0 + c1 h + c2 h^2| <= |c0| + |c1| de + |c2| de^2`.

## 6. The integrals: centred Gaussian moment series

**Lemma 6.** For `yc` and `A, B` with `|v| <= rho` on `[A, B]`,
`I_k := int_A^B v^k phi(yc + v) dv = sum_{j <= J} c_j (B^(k+j+1) - A^(k+j+1)) / (k + j + 1) + E_k`,
`c_j = phi^(j)(yc) / j! = (-1)^j He_j(yc) phi(yc) / j!`, and
`|E_k| <= sup_{|xi - yc| <= rho} |He_(J+1)(xi)| phi(xi) / (J + 1)! * |B - A| * rho^(k+J+1)`.
*Proof.* Taylor's theorem for `phi(yc + v)` with Lagrange remainder, integrated term by term. The
supremum is bounded by `sum |He coefficients| (|yc| + rho)^n` times `sup phi` on the interval
(`phi` is unimodal at 0). ∎

A piece integral `int_alpha^beta Q(y) (-1)^i He_i(y) phi(y) dy` is evaluated with `y = yc + v`,
`yc` a dyadic near the piece midpoint (so `|v|` stays below about 1: arm pieces have width 1 and the
middle is cut into `k` pieces of width at most 1), by expanding `Q(yc + v) (-1)^i He_i(yc + v)` in
powers of `v` EXACTLY (Taylor shift of the candidate polynomial about the image of `yc`) and using
Lemma 6. This is stable for every `yc`, including tail pieces where `phi(yc)` is tiny (no forward
moment recurrence is used).

## 7. Taylor models (the enclosure arithmetic)

A Taylor model `(P, R)` of order N in `u in [-1, 1]^3` encloses `f` if `|f(u) - P(u)| <= R` on the box.
* Sum: `(P1 + P2, R1 + R2)`.
* Product: `P1 P2` truncated at order N, the dropped terms bounded by `sum |coefficients|` (every
  monomial is at most 1 in absolute value), plus `B(P1) R2 + R1 B(P2) + R1 R2`.
* Composition with an analytic `g` about the exact constant `x0`: `sum_{j<=N} g^(j)(x0)/j! dX^j` plus
  the Lagrange term `sup |g^(N+1)| r^(N+1) / (N+1)!` with `r` a bound of `|dX|`; for `g = phi, Phi`
  the derivatives are `(-1)^j He_j phi` and `phi^(j-1)`.
* Coefficients are integers scaled by `2^-160`; every rounding is floor-with-recorded-error and the
  error is added to R.
Point values `phi(x0)`, `Phi(x0)` are rigorous rational enclosures (C7's `c7_gaussian`: proved
series remainders, 2^-320 outward rounding). Hence each residual Taylor model encloses the residual
at every `(x, e)` of its box, and `lam_k = max over boxes of (|c_0| + sum |c_a| + R)`.

## 8. Boxes and boundaries

* Bands 0–3: `s in [s0, s1] subset [k, k + 1]`, `theta in [t0, t1] subset [-1, 1]`,
  `p = s (1 + theta)/2`, `m = s (1 - theta)/2` — the closed strip `{k <= s <= k + 1, p, m >= 0}` is
  covered exactly, with no point outside R. Band 4: the two axis segments `s in [4, 5]`.
* Every box lies in one closed band, so one piece structure (Lemma 1) holds on the whole box; no
  box straddles a kink line. The arm pieces' images end exactly at the kink/band points, so no kink
  lies inside a piece. Zero-length pieces (at band edges) integrate to zero.
* The cover is refined by bisection in `(s, theta)` until each box meets the frozen tolerance or the
  frozen depth; the maximum over the leaves is used either way (tightness only).
* The drift variable is the third Taylor-model coordinate, so each box's enclosure holds uniformly
  in `e in E_j` ("block-uniform"; no scalar-drift collapse).
* Boxes are NEVER split in `e`: every box of sub-block `E_j` (and every descendant under bisection)
  carries the whole interval `E_j` and the same Taylor centre `e_c`, so all residual enclosures are
  of ONE candidate function `(x, e) -> D_k(e)(x)` on `R x E_j`, as Theorem 5 requires (were the
  centre to differ between boxes, the boxes would bound residuals of different functions and the
  maximum would prove nothing). Validation V22 checks this invariant and that the initial boxes tile
  `R` exactly. The width of `E_j` enters only through `h = e - e_c`, which is why the number of
  sub-blocks (not the state refinement) controls the `e`-truncation part of the residuals.

## 9. Assumptions and what is not claimed

* R as the state set (C11 / C11R specification; Lemma 0 shows invariance).
* The ACCEPTED C11R F_H certificate as the only premise (Lemma 3); nothing about `Abar` or `D_lo`
  is used.
* Positivity of `Khat_e` and `w >= 0`; unimodality of `phi`; exact Hermite polynomials. No
  monotonicity or sign of `d`, `d'`, `d''` is assumed.
* The float proposal is untrusted and only affects tightness.
* C7's point enclosures of `phi`, `Phi` (accepted in the C11 lineage) are trusted as rigorous.
