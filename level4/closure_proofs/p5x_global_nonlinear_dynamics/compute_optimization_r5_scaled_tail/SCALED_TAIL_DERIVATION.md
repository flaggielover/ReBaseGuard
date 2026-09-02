# P5X R5 — Stable Tail-Scaled SR Kernel Evaluation

`CERTIFIED_NUMERICAL_REPRESENTATION_REPAIR`.
Not a theorem revision, not a detector revision, not a scope revision, not a
scientific method change. The `xi`/`zeta` transformation of R4 is **not**
reopened; the SR recurrence, `[0,12]`, convention A and `m in {1,2,3,5}` are
untouched. R4's frozen gate remains **FAIL** and is not reinterpreted.

---

## 1. What actually causes the `2^58`, measured before designing anything

The R4 brief attributed the conditioning to explicitly forming
`exp(k^2/2-ke) x [Phi(u+e-k) - Phi(l+e-k)]` as `~1e55 x ~1e-55`. A term-by-term
audit of the exact R4 gate configuration (patch `(17,11)` centre, `e = 1/4`,
`n = 16`, 192 bits) shows that is **not** the mechanism:

| observation | value |
|---|---|
| cancellation across `k`: `max_k |G_k I_k| / |sum|` | **`0.9933` = `2^-0.0`** — no cross-`k` cancellation at all; `k = 0` dominates |
| relative radius of `I_k` at `k = 0` | `1.59e-58` (full working precision) |
| relative radius of `I_k` at `k = +16` | **`1.68e-32`** |
| relative radius of `I_k` at `k = -16` | **`6.63e-33`** |
| `|G_k I_k|` at `k = +-16` | `1.79e-9`, `5.85e-10` |
| predicted `rad(sum)` from those two terms alone | `3.0e-41 + 3.9e-42 = 3.4e-41` |
| **measured** `rad(sum)` | **`3.4022e-41`** |

The amplification is produced **entirely inside a single `I_k`, in the deep-tail
`Phi` evaluation**, and is then carried by terms of magnitude `~1e-9`. The
mechanism is the `Phi` *branch*:

```text
gaussian_cdf(x) = (1 + erf(x/sqrt2)) / 2 .
```

At `x = -10.707` (which is `u+e-k` at `k = 16`), `erf -> -1 + 9.4e-27`, so
`1 + erf` cancels `26` decimal digits against the absolute precision of `erf`.
Measured directly:

```text
(1 + erf(x/sqrt2))/2   ->  relative radius 1.690e-32      <-- matches the k=16 row
erfc(-x/sqrt2)/2       ->  relative radius 4.575e-56
```

Arb's `erfc` is relatively accurate at large argument (`2.2e-58` at `t = 7.571`,
`7.8e-60` at `t = 30`). **The repair is a representation change, not a precision
change** — exactly as the flat 192-512-bit sweep predicted.

The `huge x tiny` product is nevertheless real and is a separate obligation
(`Q4`), addressed in §4.

## 2. The exact identity, re-derived independently

```text
I_k(l,u,e) = int_l^u e^{kz} phi(z+e) dz .
```

Substitute `zeta = z + e` (`dz = dzeta`, limits `l+e .. u+e`):

```text
I_k = e^{-ke} int_{l+e}^{u+e} e^{k zeta} (2pi)^{-1/2} e^{-zeta^2/2} dzeta
    = e^{-ke} (2pi)^{-1/2} int e^{-(zeta^2 - 2k zeta)/2} dzeta
    = e^{-ke} (2pi)^{-1/2} int e^{-((zeta-k)^2 - k^2)/2} dzeta
    = e^{k^2/2 - ke} int_{l+e}^{u+e} phi(zeta - k) dzeta
    = e^{k^2/2 - ke} [ Phi(u+e-k) - Phi(l+e-k) ] .            (R4 identity)
```

Write throughout

```text
a = l + e - k ,   b = u + e - k ,   a < b ,   I_k = e^{k^2/2-ke} [Phi(b) - Phi(a)] .
```

## 3. The exponent-cancellation identity (the load-bearing algebra)

**Lemma.** For every real `x`, `e` and every `k`:

```text
k^2/2 - k e - (x + e - k)^2 / 2  =  k x - (x + e)^2 / 2  =:  E(x) .
```

*Proof.* `(x+e-k)^2/2 = ((x+e)^2 - 2k(x+e) + k^2)/2`. Hence the left side is
`k^2/2 - ke - (x+e)^2/2 + k(x+e) - k^2/2 = -ke - (x+e)^2/2 + kx + ke
= kx - (x+e)^2/2`. The `k^2` terms cancel **exactly**. ∎

Verified as balls at `(k,x,e) = (16, 5.0433, 1/4)`, `(-16, -5.6299, 1/4)` and
`(7, -2, 12)`: both sides agree to full precision.

This is the whole repair. `E(x)` is the exponent that survives after the
Gaussian tail's own `e^{-(x+e-k)^2/2}` has cancelled the `e^{k^2/2}` prefactor
**symbolically, before any numerical evaluation**.

## 4. The scaled tail function

For `t >= 0` define the scaled complementary error function
`erfcx(t) = e^{t^2} erfc(t)`, which satisfies `erfcx(0) = 1`, is decreasing, and
obeys `1/(t sqrt(pi) + sqrt(t^2 pi + 2)) <= erfcx(t) <= 1`. **`erfcx` is `O(1)`
on the whole production range** — it is never astronomically small, which is
precisely why it removes the `huge x tiny` product.

Define

```text
T(x) := exp( E(x) ) * erfcx( |x + e - k| / sqrt(2) ) ,   E(x) = k x - (x+e)^2/2 .
```

Using `Phi(w) = erfc(-w/sqrt2)/2` for `w <= 0` and `erfc(t) = e^{-t^2} erfcx(t)`
with `t = -w/sqrt2`, `t^2 = w^2/2`:

```text
e^{k^2/2-ke} Phi(w)  =  e^{k^2/2-ke} e^{-w^2/2} erfcx(|w|/sqrt2) / 2
                     =  e^{E(x)} erfcx(|w|/sqrt2) / 2  =  T(x)/2 ,      w = x+e-k ,
```

by §3. The same computation with `Phi(w) = 1 - erfc(w/sqrt2)/2` for `w >= 0`
gives `e^{k^2/2-ke} (1 - Phi(w)) = T(x)/2`.

## 5. Regime decomposition and the stable formulas

| regime | condition | formula | why stable |
|---|---|---|---|
| **B** deep negative tail (both args `<= 0`) | `b <= 0`, i.e. `k >= u+e` | `I_k = [ T(u) - T(l) ] / 2` | no `1+erf`; no `e^{k^2/2}` formed; `T(u)/T(l) >= 3.13` (§6) |
| **C** deep positive tail (both args `>= 0`) | `a >= 0`, i.e. `k <= l+e` | `I_k = [ T(l) - T(u) ] / 2` | same, by symmetry `Phi(x)=1-Phi(-x)` |
| **D** crossing / central | `a < 0 < b` | `I_k = e^{k^2/2-ke} [ Phi(b) - Phi(a) ]`, with `Phi(b) = 1 - erfc(b/sqrt2)/2` and `Phi(a) = erfc(-a/sqrt2)/2` | `Phi(b)-Phi(a) >= 0.19` (§6); `|k|` is bounded in this regime so the prefactor is not extreme |

Regimes **A** (both moderate) and **F** (near-equal tails) are subsumed: A is D
with small `|k|`; F is proved **impossible** in §6. Regime **E** (one tail vastly
smaller) is exactly regimes B/C, where it is the *favourable* case — the
subtraction is dominated by its larger term.

Note `T` is a single function serving B and C, differing only in sign:
`I_k = sigma [T(u) - T(l)]/2` with `sigma = +1` in B and `sigma = -1` in C.

### Deterministic, pre-result regime selector

`k` is an exact integer; `l`, `u` are balls; `e` is an exact rational.

```text
if  (u + e - k).upper() <= 0 :   regime B
elif (l + e - k).lower() >= 0 :   regime C
else :                            regime D
```

B and C are entered only when the sign is **proved** by the enclosure;
otherwise D, which is mathematically valid for all arguments. The rule is
total, deterministic, and fixed before any result.

### `erfcx` sub-branch (frozen)

`erfcx` is not exposed by python-flint 0.9.0. Two rigorous branches:

```text
t <= 2 :  erfcx(t) = exp(t^2) * erfc(t)          max intermediate e^4 = 54.6
t >  2 :  erfcx(t) = U(1/2, 1/2, t^2) / sqrt(pi)  Arb's rigorous Tricomi U
```

The identity `erfcx(t) = U(1/2,1/2,t^2)/sqrt(pi)` was verified against
`exp(t^2) erfc(t)` at `t = 0.5, 1, 3, 7.571, 15.115, 30, 120, 500`: all overlap,
relative radius `5e-60` throughout. The `t <= 2` branch keeps `U` away from its
`z -> 0` limit, where `t = 0` occurs exactly at a regime boundary.

## 6. The two non-cancellation bounds

Both rest on a lower bound for the live-region width. From
`u - l = (c_SR - y^+) - (y^- - c_SR) = 2c_SR - y^+ - y^-` and `y^{+/-} <= b_SR`:

```text
W := u - l  >=  2(c_SR - b_SR)  =  1 - 2 log(1 + 1/A)
              =  0.9961640701886751383284382...        (exact, D1-corrected)
```

**(i) Regimes B/C do not cancel.** In B, `a < b <= 0` and `T(u)/T(l) =
Phi(b)/Phi(a)`. `Phi` is increasing, so the ratio exceeds 1; and for left tails
the ratio `Phi(b)/Phi(b-W)` is *decreasing in `b`*, so it is minimised at the
largest admissible `b`, namely `b = 0`:

```text
Phi(b)/Phi(a)  >=  Phi(0)/Phi(-W)  =  3.13312228929...      (checked: 3.133 at
   b=0, 4.584 at b=-0.5, 6.911 at b=-1, 41.94 at b=-3, 5323 at b=-8)
```

so the subtraction `T(u) - T(l)` loses at most `log2(1/(1 - 1/3.133)) = 0.556`
bits. Regime C is identical under `x -> -x`.

**(ii) Regime D does not cancel.** Let `r` be the maximum ball radius of `a`, `b`.
Suppose `r <= 0.4` (asserted by the gate; production patch half-widths are
`~0.05`). Regime D is entered only when `a.lower() < 0` and `b.upper() > 0`.

* If the true `a <= 0`: since `b = a + W >= a + 0.996`, either `a >= -W/2` and
  then `b >= W/2`, giving `Phi(b) - Phi(a) >= Phi(W/2) - Phi(0)`; or `a < -W/2`
  and then `Phi(b) - Phi(a) >= Phi(min(b,0)) - Phi(-W/2) >= Phi(-r) - Phi(-W/2)`.
* If the true `a > 0`: then `a < r` (else `a.lower() >= 0` and regime C would
  have been selected), so `b >= W`, and `Phi(b) - Phi(a) >= Phi(W) - Phi(r)`.

In every branch, with `r <= 0.4`,

```text
Phi(b) - Phi(a)  >=  Phi(W/2) - Phi(0)  =  0.19078688886760390794... > 0.19 ,
```

so the subtraction loses at most `log2(1/0.19) = 2.40` bits. **Regime F
(near-equal tail probabilities) is therefore impossible**, in every regime.

## 7. No `huge x tiny` intermediate

In regime B at the worst production point (`k = 16`, patch `(17,11)` centre):

```text
R4 direct :  exp(k^2/2-ke) = 7.121e53   x   [Phi(b)-Phi(a)] = 4.735e-27   -> HUGE x TINY
R5 scaled :  exp(E(u))     = e^{66.683} = 9.1e28   x   erfcx(7.571) = 0.0739   -> no tiny factor
```

`erfcx` is bounded in `(0,1]` and, on the production range, bounded **below** by
`~1/(t sqrt(pi))`; the smallest value the production domain can reach is
`erfcx(t_max)` with `t_max = (|k| + e + c_SR)/sqrt2 <= (16+12+6.756)/sqrt2 =
24.58`, giving `erfcx >= 0.0229`. So no factor smaller than `~2e-2` is ever
formed. Instrumented, not asserted: the gate records the maximum intermediate
`|log10|`, the minimum tail factor, and a boolean for whether any product of a
`|log10| > 20` factor with a `|log10| < -20` factor was constructed.

## 8. Second-moment extension (analytic only; not implemented)

Differentiating the exact identity in `k`, with `da/dk = db/dk = -1`:

```text
d/dk I_k = (k - e) I_k - e^{k^2/2-ke} [ phi(b) - phi(a) ] .
```

By §3, `e^{k^2/2-ke} phi(x+e-k) = e^{k^2/2-ke} e^{-(x+e-k)^2/2}/sqrt(2pi)
= e^{E(x)}/sqrt(2pi)`. Hence

```text
int_l^u z e^{kz} phi(z+e) dz  =  (k-e) I_k  -  [ e^{E(u)} - e^{E(l)} ] / sqrt(2pi) ,
```

which needs **no `erfcx` and no tail difference at all** — the new term is a bare
exponential. Differentiating once more, using `d E(x)/dk = x`:

```text
int_l^u z^2 e^{kz} phi(z+e) dz
   = I_k + (k-e) d/dk I_k  -  [ u e^{E(u)} - l e^{E(l)} ] / sqrt(2pi) .
```

So the same scaling carries the `z` and `z^2` weights directly.

**`R5_SECOND_MOMENT_STABILITY = DIRECT_WITH_DERIVATIVE_SCALING`.**

## 9. Proof obligations

| lemma | statement | status |
|---|---|---|
| `L-R5.1` | each scaled formula is algebraically identical to R4's exact `I_k` | **PROVED** — §3 exponent identity plus `erfc(t) = e^{-t^2} erfcx(t)` and `Phi(w) = erfc(-w/sqrt2)/2`; each step an identity, no approximation |
| `L-R5.2` | the regime partition covers all production arguments | **PROVED** — the selector's three branches are exhaustive by trichotomy on the ball bounds; `l < u` always, and D is valid unconditionally |
| `L-R5.3` | regime boundaries agree / overlap safely | **PROVED** — B and C are entered only on a *proved* sign, so on any argument where two regimes are both admissible the formulas are equal by `L-R5.1`; at `t = 0` exactly, `erfcx(0) = 1` and B/C reduce to D's value |
| `L-R5.4` | interval evaluation preserves containment | **PROVED** — every operation is an Arb ball operation (`exp`, `erfc`, `hypgeom_u`, `+`, `-`, `*`, `/`) and inclusion isotonicity gives a valid enclosure for every state in the patch; no step divides by a ball containing zero (`erfcx > 0`, `sqrt(pi) > 0`) |
| `L-R5.5` | no subtraction of nearly equal raw tail probabilities where a scaled form exists | **PROVED** — §6(i) ratio `>= 3.133` in B/C, §6(ii) difference `>= 0.19078...` in D, both from `W >= 0.99616...` |
| `L-R5.6` | no empirical monotonicity is used | **PROVED** — the only monotonicity invoked is that `Phi` and `exp` are increasing and `erfcx` is decreasing, all classical |
| `L-R5.7` | `z`-panel count remains zero | **PROVED** — R5 changes only the evaluation of `I_k`; the `k`-sum structure of R4 §14 is untouched, and no `z` discretisation is introduced. Instrumented |
| `L-R5.8` | softplus approximation count remains zero | **PROVED** — `softplus` does not appear in the R5 path at all. Instrumented |
| `L-R5.9` | the R4 `xi` target and theorem interface are unchanged | **PROVED** — `I_k` is a *scalar quantity* consumed by R4's `sum_k G_k I_k`; `L-R4.1`..`L-R4.10` concern the coordinate change and are untouched; `R_max`, `s_min`, `M_2` and Lean `X1`-`X6` sit strictly above this layer |
