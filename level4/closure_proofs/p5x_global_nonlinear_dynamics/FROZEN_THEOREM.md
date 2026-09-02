# P5X frozen theorem statements

Frozen at Checkpoint A, hashed into `PROTOCOL_DIGEST.json`, and not editable
after the first production result. Tier vocabulary is the repository's:

```text
EXACT_THEOREM | CERTIFIED_THEOREM | CONDITIONAL_THEOREM
NUMERICAL_EVIDENCE | NOT_ESTABLISHED | REJECTED
```

`CERTIFIED_THEOREM` means: an exact theorem whose hypotheses are discharged by
an outward-rounded interval certificate over a **finite cover that provably
exhausts its domain**. It is never a grid evaluation.

---

## 1. Standing setup (imported, not new)

`D in {CUSUM(k=1/2, h=5), SR(A=520.886133602749)}`; `m in {1,2,3,5}`;
`rho in [0,1]`; `Delta = 0`; Stage-D convention A. `raw_t ~ iid N(0,1)`,
`z_t = raw_t - e`, `tau` the frozen inclusive alarm time, `w = min(m, tau)`,
`Rbar = (1/w) sum_{r<w} raw_{tau-r}`.

Imported without restatement or strengthening:

* `P5-T1` `e_{j+1} = rho Rbar_j + (1-rho) fresh_j`;
* `P5-T2` `E[e_{j+1}|e] = rho R(e)`, `Var(e_{j+1}|e) = rho^2 S(e) + (1-rho)^2/m`;
* `P5-T3` `R` odd, `S` even, `R(0) = 0`;
* `P5-T4`/`P5-T5` uniform finiteness of `E_e[tau]` and of all even moments;
* `P5-T7` unique invariant `pi`, uniform ergodicity, all moments, `pi` symmetric,
  per fixed `(D,m,rho)`;
* `P3` `lambda_{D,m}(rho) = rho (1 - GammaTilde_{D,m})`, `rho_c = 1/|1 - GammaTilde|`;
* `Gamma_CUSUM in [3.9243482005828971282, 27.8493821275467032805]` and
  `Gamma_SR in [5.8003917995084423356, 28.781285803081492059]` (existing Arb
  certificates, `e = 0`, `m = 1`).

Write `phi`, `Phi` for the standard normal density and cdf.

---

## 2. `P5X-T1` — two-dimensional Fredholm reduction of the selection map

> **Tier: EXACT_THEOREM.** New. This is the campaign's structural result.

Let `x = (x^+, x^-)` denote the pre-alarm detector state, living in the compact
square `E_D = [0, b_D)^2` with `b_CUSUM = h = 5`, `b_SR = log A`; let
`c_CUSUM = h + k = 11/2`, `c_SR = log A + 1/2`; let

```text
q_CUSUM(x, z) = ( max(0, x^+ + z - 1/2) , max(0, x^- - z - 1/2) )
q_SR(x, z)    = ( log(1 + exp(x^+ + z - 1/2)) , log(1 + exp(x^- - z - 1/2)) )
```

and let the continuation interval from `x` be
`( l(x), u(x) ) = ( x^- - c_D , c_D - x^+ )`, so that the alarm at the next step
is exactly `{ z <= l(x) } union { z >= u(x) }` for both detectors. Let `x_0 =
(0,0)` be the reset state. For `e in R` define, on bounded Borel functions on
`E_D`,

```text
(K_e f)(x)     = int_{l(x)}^{u(x)} f(q(x,z)) phi(z + e) dz
(K_{z,e} f)(x) = int_{l(x)}^{u(x)} z f(q(x,z)) phi(z + e) dz
rho_{1,e}(x)   = phi(u+e) - phi(l+e) - e ( 1 - Phi(u+e) + Phi(l+e) )
rho_{2,e}(x)   = [ (u+e) phi(u+e) + 1 - Phi(u+e) ] - 2 e phi(u+e) + e^2 ( 1 - Phi(u+e) )
               + [ -(l+e) phi(l+e) + Phi(l+e) ] + 2 e phi(l+e) + e^2 Phi(l+e)
```

(`rho_{1,e}(x) = E[ z ; alarm from x ]`, `rho_{2,e}(x) = E[ z^2 ; alarm from x ]`,
both in closed form). Define

```text
h_1 = 1 - K_e 1 ,           h_j = K_e h_{j-1}   (j >= 2)      [ h_j(x) = P_x(tau = j) ]
S_0 = rho_{1,e} ,           S_j = K_{z,e} h_j   (j >= 1)
g_r = (I - K_e)^{-1} S_r    (r >= 0)
```

Then:

**(a) Invertibility.** `‖(I - K_e)^{-1}‖_inf = sup_{x} E_{x,e}[tau] <= C_D < infinity`
for every `e`, so `g_r` exists, is unique among bounded functions, and is given
by a convergent Neumann series.

**(b) Terminal-innovation identities.** For `1 <= i <= t`,
`E_e[ Z_i ; tau = t ] = ( K_e^{i-1} S_{t-i} )(x_0)`, and for `r >= 0`,
`g_r(x_0) = E_e[ Z_{tau - r} ; tau >= r + 1 ]`.

**(c) Selection map.** For every `m >= 1` and every `e`,

```text
R_{D,m}(e) = e
  + (1/m) sum_{r=0}^{m-1} [  g_r(x_0)
                           - sum_{t=r+1}^{m-1} ( K_e^{t-r-1} S_{r} )(x_0) ]
  + sum_{t=1}^{m-1} (1/t) sum_{i=1}^{t} ( K_e^{i-1} S_{t-i} )(x_0) .
```

The inner subtraction removes the `{ tau < m }` part of `g_r`, and the last sum
restores it with the convention-A denominator `w = tau`. All sums are finite and
involve at most `m - 1` applications of `K_e`.

**Why it matters.** The state space is two-dimensional **for every `m`**: the
last `m-1` innovations never enter the state; linearity moves them into `m-1`
backward functions on the same square. The dependence on `e` is only through
`phi(z + e)`, which is entire, so all displayed quantities are real-analytic in
`e` and an interval-valued `e` is a legitimate argument. At `e = 0`, `K_e` and
`K_{z,e}` are exactly the operators of the existing `Gamma` certificate
(`closure/04_ARB_CERTIFICATE.md` §3).

## 3. `P5X-T2` — second-moment reduction

> **Tier: EXACT_THEOREM.** New.

For `m = 1`, `E_e[Rbar^2] = ((I-K_e)^{-1} rho_{2,e})(x_0) + 2 e g_0(x_0) + e^2`,
hence `S_{D,1}(e) = E_e[Rbar^2] - R_{D,1}(e)^2`.

For `m >= 2`, `E_e[Rbar^2]` is determined by the same square through
`O(m^2)` further backward functions: with
`h_{j}^{(z)} := K_{z,e} h_j` and, for `0 <= r' < r <= m-1`, the pair functions
`p_{r,r'} = (I - K_e)^{-1} K_{z,e} g^{(r,r')}` built from `h` and `K_{z,e}` by
the same first-step conditioning as `P5X-T1(b)`, one obtains
`E_e[ Z_{tau-r} Z_{tau-r'} ; tau >= m ]` for every pair, and hence
`E_e[Rbar^2]` with the same short-`tau` bookkeeping as `P5X-T1(c)`.
The exact pair recursion is a proof obligation (`PROOF_OBLIGATIONS.md` `L2`)
and is written out before any certified solve.

## 4. `P5X-T3` — far-field forgetting, with explicit constants

> **Tier: EXACT_THEOREM.** New (a rigorous version of the audit's `G4` note).

Fix `D`, `m >= 1`, and let `a(e) = c_D - |e|`. On `{ |z_1| >= c_D }` the alarm
fires at `t = 1`, so `w = 1` and `Rbar = raw_1` for every `m`. Hence, with
`q(e) = P_e(tau > 1) <= Phi(a(e))` for `e >= 0`,

```text
| R_{D,m}(e) |  <=  sqrt( q(e) ) * ( 1 + sqrt( E_e[ Rbar^2 | tau > 1 ] ) )
```

and, using `P5-T5`, an explicit closed-form majorant `B_D(e)` decreasing in
`|e|` with `B_D(e) -> 0` super-exponentially. Numerically (audit arithmetic,
`p5_final_disposition_audit/results/g4_far_field_bound_check.json`):
`|R_CUSUM(±10)| <= 3.2e-5`, `|R_SR(±10)| <= 4.2e-3`. The frozen production
statement fixes `e_far` and reports `B_D(e_far)` as a certified scalar.

## 5. `P5X-T4` — global saturation

> **Tier: CERTIFIED_THEOREM.** Target.

For each frozen `(D, m)` there is a certified `R_max(D,m)` with

```text
sup_{e in R} | R_{D,m}(e) |  <=  R_max(D,m)  <  2 ,
```

established by an outward-rounded interval enclosure over a finite cover of
`[0, e_far]` in interval-valued `e` (using `P5X-T1` and oddness `P5-T3`),
together with `P5X-T3` on `[e_far, infinity)`.

## 6. `P5X-T5` — global drift and the trapping interval

> **Tier: EXACT_THEOREM given `P5X-T4`.** Corollary; stated as such.

For every `rho in [0,1]`, every `m`, and every `e` with `|e| > rho R_max`,

```text
sign(e) ( E[ e_{j+1} | e_j = e ] - e )  =  sign(e) rho R(e) - |e|  <=  rho R_max - |e|  <  0 ,
```

so `I_rho = [ -rho R_max, rho R_max ] subset [-2, 2]` is forward invariant for
the conditional-mean map and absorbing for the deterministic skeleton. P5X
records explicitly that the mechanism is **forgetting, not restoring**: by
`P5X-T3`, `E[e_{j+1}|e] -> 0` as `|e| -> infinity`, rather than being pushed
back proportionally to `e`.

## 7. `P5X-T6` — quantitative stationary dispersion

> **Tier: CERTIFIED_THEOREM.** Primary target.

Let `pi` be the invariant law supplied by `P5-T7` for a fixed `(D,m,rho)`.
Then, exactly,

```text
E_pi[e^2] = rho^2 E_pi[ R(e)^2 + S(e) ] + (1-rho)^2 / m ,
```

and with certified `s_min = inf_e S_{D,m}(e) > 0` and
`M_2 = sup_e E_e[Rbar^2] < infinity`,

```text
rho^2 s_min + (1-rho)^2/m   <=   E_pi[e^2]   <=   rho^2 M_2 + (1-rho)^2/m .
```

**Corollary (high dispersion).** `RMS_pi >= sqrt( rho^2 s_min + (1-rho)^2/m )`,
uniformly in `rho in [0,1]`. With the frozen `r_lin = 0.05` of P7 this is a
certified statement that the stationary law lives more than an order of
magnitude outside the linearisation radius, for every `rho`.

**Optional extension (`P5X-T6b`, anti-concentration).** With a certified
`M_4 = sup_e E_e[Rbar^4]`, for every `r > 0`,
`pi( |e| > r ) >= ( E_pi[e^2] - r^2 )_+^2 / E_pi[e^4]` with both moments
bounded by certified constants. Attempted only if `M_4` is affordable.

## 8. `P5X-T7` — global shape of the selection map

> **Tier: CERTIFIED_THEOREM.** Secondary target.

For each frozen `(D,m)`, with `E = 2`:

1. `R_{D,m}(e) < 0` for every `e in (0, E]`;
2. `s(e) = -R(e)/e` is continuous on `(0,E]`, `s(0+) = GammaTilde - 1`, and each
   level `L >= 1` is attained exactly once on `(0,E]`;
3. `sup_e |R| = R_max < E` (this is `P5X-T4`).

Statement 1 is certified on `[e_0, E]` by direct enclosure and on `(0, e_0]` by
a certified `R' < 0` together with the **exact** `R(0) = 0` of `P5-T3`.
Statement 2 is certified by enclosing `s'(e) = ( R(e) - e R'(e) ) / e^2 < 0`
cellwise on `[e_0, E]`, with the behaviour on `(0, e_0]` supplied by the
certified `R'` enclosure and a second-order remainder.

**Consequence, credited to P5.** `P5-T8`, `P5-T9` and `P5-T10` become
unconditional for the frozen cells: their hypotheses `H1`–`H3b` are discharged.
P5X claims only the discharge. It does not restate those theorems as its own.

## 9. `P5X-T8` — global dynamics of the deterministic skeleton (scoped, optional)

> **Tier: CERTIFIED_THEOREM, scoped.** Optional target, explicitly at risk.

There exists `eta > 0`, **reported and not tuned**, such that for every
`rho in [ (1+eta) rho_c(D,m) , 1 ]` the map `f_rho = rho R_{D,m}` on the
absorbing interval `I_rho` of `P5X-T5` has: the unique fixed point `0`, which is
repelling; exactly one 2-cycle, which is the symmetric pair `{ +e*(rho), -e*(rho) }`
and is hyperbolic and attracting; no periodic orbit of period `> 2`; and every
orbit from `I_rho \ {0}` converges to that 2-cycle.

**Scope note, load-bearing.** This is a theorem about the conditional-mean map,
not about the stochastic chain. It does not assert, and must not be quoted as
asserting, that the 2-cycle explains the stationary dispersion or the measured
bimodality (`FAILURE_ANALYSIS.md` §4, gate `G12`).

## 10. `P5X-T9` — mechanism synthesis

> **Tier: EXACT_THEOREM given `P5X-T4`, `P5X-T6` and the P3 import.** Final
> statement of the campaign.

Fix a frozen `(D, m)` and `rho in (rho_c, 1]`. Then simultaneously:

1. **(local repulsion, imported P3 + existing Arb)** the conditional-mean map has
   multiplier `lambda(rho) = rho(1 - GammaTilde)` at `0` with `|lambda| > 1`;
2. **(global saturation, `P5X-T4`)** `sup_e |E[e_{j+1}|e]| <= rho R_max < 2`, so
   the map cannot amplify beyond an explicit constant however large `|e|` is;
3. **(forgetting, `P5X-T3`)** `E[e_{j+1}|e] -> 0` as `|e| -> infinity`, with
   explicit rate;
4. **(bounded stationary law, `P5-T7` + `P5X-T6`)** the invariant law is unique
   with all moments finite and `E_pi[e^2] <= rho^2 M_2 + (1-rho)^2/m`;
5. **(high dispersion, `P5X-T6`)** `E_pi[e^2] >= rho^2 s_min + (1-rho)^2/m`, so
   `RMS_pi` exceeds the linearisation radius `r_lin` by more than an order of
   magnitude.

Consequently the regime is bounded **and** genuinely nonlinear: the stationary
law is supported where the linearisation is invalid, the boundedness mechanism
is certified saturation and far-field forgetting of the stopped-selection map,
and no restoring drift, no bifurcation and no branch is required to explain it.

**Forbidden readings**, enforced by gate `G12`: that the flip bifurcation causes
the dispersion; that the skeleton 2-cycle is the stationary law's bimodality;
that `P5X-T9` supersedes, repairs or recolours original P5; that any certified
enclosure is an exact value.
