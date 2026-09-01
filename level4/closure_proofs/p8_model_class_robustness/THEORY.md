# P8 theory

Three statements. Two are P8's own (`P8-T1`, `P8-T2`); one is a lemma
(`P8-L1`) that supplies the exact centring used by the empirical window law.
None is formalised: `P8_DEFINITION_AUDIT.md` §4 `O4` records that no repository
statement asks P8 for a formal layer, and P4's Lean was explicitly **NOT
AUTHORIZED** after its numerical gate failed, so starting one here would be out
of order. **No Arb enclosure and no Lean declaration exists in P8, and none is
claimed.**

---

## 0. Setting, exactly as frozen

Physical observations `eps_1, eps_2, ...` are iid with density `f`, `E[eps]=0`.
The reference error entering cycle `j` is `e_j = R_j - mu`. The detector is fed

```text
Z_t = eps_t - e ,        so the residual density is  f_e(z) = f(z + e).
```

Scores (frozen sign convention, `location_family/PROTOCOL.md` §2):

```text
s(z) = f'(z)/f(z) ,   psi(z) = -f'(z)/f(z) = -s(z) ,
S_tau = sum_{t<=tau} s(Z_t) = - sum_{t<=tau} psi(Z_t) .
```

Detector, stopping and window semantics are the frozen ones (`C1`–`C6` of
`PRIORITY_DEPENDENCY_AUDIT.md`): two-sided CUSUM `k = 1/2` or symmetric
two-chart SR, both arms updated before an inclusive alarm test, no minimum
dwell, `tau = inf{t >= 1 : alarm}`, terminal increment included,

```text
w = min(m, tau) ,      zbar^A_m = (1/w) sum_{r=0}^{w-1} Z_{tau-r} ,
e_{j+1} = rho ( e_j + zbar^A_m ) + (1-rho) mu_fresh ,
mu_fresh = (1/m) sum_{r<m} Y_r ,   Y_r iid f, independent of the cycle.
```

**The detector statistic is frozen at its Gaussian design and is never
re-derived per family.** Only the threshold is recalibrated to the frozen
`ARL_0 = 465.50394`. This is the Stage-D D3 convention and the operationally
realistic one: the practitioner deploys the standard chart and tunes its limit.
A family-optimal (score-based) chart is a *different detector* and is out of
P8's scope.

---

## P8-L0. Raw-mean form (algebraic, any innovation law)

Since `Z_t = eps_t - e_j` and the window is a plain average of `w` consecutive
residuals,

```text
e_j + zbar^A_m = (1/w) sum_{r<w} eps_{tau-r} =: Rbar_j ,
e_{j+1} = rho * Rbar_j + (1-rho) * mu_fresh .
```

*Proof.* `zbar^A_m = (1/w) sum_{r<w}(eps_{tau-r} - e_j) = Rbar_j - e_j`. ∎

This is a change of variables and holds for **any** iid innovation law. P5's
`T1` is the same statement for the frozen Gaussian core; `p5/LIMITATIONS.md` §1
fixes T1's scope there, so P8 states `P8-L0` in its own right and records the
correspondence rather than importing T1 (`D1` in the dependency audit).

`P8-L0` is what makes the mechanism distribution-independent *as a mechanism*:
the reused reference is a **stopping-time-selected sample mean of raw
observations** in every family. Nothing in that sentence mentions Gaussianity.
It says nothing about the *size* of the effect, which is what the rest of P8
measures.

---

## P8-T1. Convention-A stopped-selection gain, general location family

**Statement.** Fix a detector family `D`, a window `m >= 1` and an innovation
density `f`. Suppose

* **(A1)** `f` satisfies hypotheses 4–6 of `location_family/THEOREM.md`
  (positive a.e. on a translation-stable support, absolutely continuous, `f'/f`
  measurable, prefix likelihood ratios differentiable at `e = 0`);
* **(A2)** the detector recursion, the stopping boundary, the tie rule and the
  window index set do not depend on `e` **in residual coordinates**;
* **(A3)** `tau < infinity` a.s. for all small `|e|`, and hypotheses 8–9 of
  `location_family/THEOREM.md` hold for `H_tau = zbar^A_m`.

Then `e -> E_e[zbar^A_m]` is differentiable at `0` and, writing

```text
Gamma_A(D,f,m) := E_0[ zbar^A_m * sum_{t<=tau} psi(Z_t) ] ,
```

we have `d/de E_e[zbar^A_m]|_0 = -Gamma_A(D,f,m)`, hence for the reference map
`F_{rho,m}(e) := E_e[e_{j+1} | e_j = e]`

```text
F'_{rho,m}(0) = rho ( 1 - Gamma_A(D,f,m) ) ,
```

and, by P3's boundary theorem `A3` applied with this multiplier,

```text
rho_c(D,f,m) = 1 / | 1 - Gamma_A(D,f,m) | .
```

**Proof.** `zbar^A_m` is a stopped-prefix functional: on `{tau = n}` it equals
`(1/min(m,n)) sum_{r<min(m,n)} z_{n-r}`, a Borel function of the first `n`
residual coordinates, and `{tau = n}` is measurable w.r.t. those coordinates by
`(A2)`. So hypotheses 1–3 of `location_family/THEOREM.md` hold. With `(A1)` and
`(A3)`, that theorem (`B1`) gives
`d/de E_e[zbar^A_m]|_0 = E_0[zbar^A_m S_tau] = -Gamma_A`. By `P8-L0`,
`F_{rho,m}(e) = rho ( e + E_e[zbar^A_m] ) + (1-rho) E[mu_fresh]` and
`E[mu_fresh] = 0`, so `F'_{rho,m}(0) = rho(1 + dE_e[zbar^A_m]/de|_0)`. The
boundary formula is P3 `A3` verbatim. ∎

**Status: CONDITIONAL, and conditional on a `PARTIAL` priority.** The step from
`(A1)`+`(A3)` to the identity is `B1`, which lives in `P4 = PARTIAL`. P4's
overall status is `PARTIAL` because its *numerical* replication gate failed, not
because the human theorem was rejected — `location_family/results/decision.json`
records `"human_theorem": "PROVED UNDER EXPLICIT ANALYTIC HYPOTHESES"` — but P8
does not upgrade it. `P8-T1` is therefore reported at
`THEOREM_CONDITIONAL_ON_PARTIAL_PREMISE` and **never** as closed.

**What is new here relative to P4.** P4's `Gamma_f` is `m = 1` raw reuse:
`H_tau = Z_tau`. `P8-T1` is the same argument for the **convention-A truncated
window for every `m`**, `H_tau = zbar^A_m`. The extension is not automatic:
`H_tau` now depends on `tau` through *both* the index set and the denominator
`w = min(m, tau)`, so hypotheses 1–3 have to be re-checked, which is what the
proof above does. Everything analytic (7–9) is inherited and assumed, not
proved, per family.

**What P8-T1 does NOT say.** It says nothing about any monitoring metric. `X6`
and the rejected candidate `P7-E` (`G5` in the dependency audit) establish that
`d E[e_1]` does **not** determine `d E[M(e_1)]`. Every operational number in P8
is measured, never derived from `Gamma_A` or `rho_c`.

---

## P8-L1. Exact unit diagonal and the lag decomposition

**(a) Unit diagonal.** For any density `f` that is absolutely continuous with
`z f(z) -> 0` as `|z| -> infinity` and `E|eps psi(eps)| < infinity`,

```text
E[ eps psi(eps) ] = integral z (-f'(z)) dz = [-z f(z)] + integral f = 1 ,
```

**exactly, for every family.** (Checked by quadrature for all six P8 families:
`results/family_regularity.json`; the largest deviation is `8e-6`, at `t3`,
where it is quadrature error.)

**(b) Lag decomposition.** Define the *lag selection covariance*

```text
gamma_r(D,f) := E_0[ Z_{tau-r} 1{r < tau} * sum_{t<=tau} psi(Z_t) ] ,  r >= 0 .
```

Then for every `m >= 1`,

```text
Gamma_A(D,f,m) = (1/m) sum_{r<m} gamma_r(D,f)  +  R_m(D,f) ,          (L1.b)
R_m := E[ 1{tau < m} (1/tau - 1/m) T_tau * sum_{t<=tau} psi(Z_t) ] ,
```

with `T_tau = sum_{t<=tau} Z_t` and `R_1 = 0` exactly (because `tau >= 1`, so
`w = min(1,tau) = 1` always).

*Proof.* `(1/m) sum_{r<m} gamma_r = E[(1/m) sum_{r<min(m,tau)} Z_{tau-r} Psi]`.
Split on `{tau >= m}` and `{tau < m}`; on the first event this equals the
convention-A term exactly, and on the second the convention-A denominator is
`tau` rather than `m`, while `sum_{r<tau} Z_{tau-r} = T_tau`. Subtracting gives
`R_m`. ∎

`R_m` is exactly the **convention-A minus convention-B** difference:
`Gamma_B(D,f,m) = (1/m) sum_{r<m} gamma_r`, so

```text
Gamma_A - Gamma_B = R_m ,
```
which turns the "truncated-window semantics" check into an identity P8 can test
numerically rather than assert (gate `G6`).

**(c) Centring.** `gamma_0 = Gamma_A(D,f,1)` exactly. Writing
`d(D,f,m) := Gamma_A(D,f,m) - 1` (so `rho_c = 1/|d|`), (L1.b) gives

```text
d(D,f,m) = (1/m) sum_{r<m} ( gamma_r - 1 )  +  R_m .
```

The `-1` is not cosmetic: by (a) each `gamma_r` contains an exact unit *own*
contribution `E[Z_{tau-r} psi(Z_{tau-r}) 1{r<tau}]`, which is `1` up to the
selection effect of conditioning on `{r < tau}` and on the alarm. `gamma_r - 1`
is therefore the part of the lag-`r` covariance that the **stopping-time
selection** creates, and `d = Gamma_A - 1 = 1/rho_c` is its window average.

---

## P8-T2. Reset decomposition for a general innovation family

**Statement.** In the frozen repeated-cycle model with a full reset of both
detector arms, the lag buffer and the cycle clock at every alarm, and iid
innovations from any law `f`: conditionally on `e_j`, the cycle-`j` run length
is independent of everything before cycle `j`, and

```text
E[tau_j]                 = E[ A_f(e_j) ] ,
E[tau_j | shift Delta]   = E[ A_f(e_j - Delta) ] ,
A_f(x) := E[ tau | reset state, Z_t = eps_t - x, eps ~ f ] .
```

If `f` is even and the detector is reflection-equivariant then `A_f` is even.

**Proof.** Identical to `THEOREM P7-A` (`p7/THEORY_BRIDGE.md`). The argument
uses only (i) the reset, which makes the cycle's initial state deterministic,
and (ii) iid innovations, which makes the cycle's law a function of the
innovation mean offset alone. Gaussianity is used nowhere. ∎

**Status: EXACT, P8's own restatement.** P7 owns the Gaussian case (`G1`) and is
credited; the generalisation is one line and is stated here because P8 needs it
in five families where P7's statement does not reach. It is exact **and
useless on its own**: `A_f` is not available in closed form for any family, and
no P8 result infers a monitoring quantity from `A_f` without measuring it.

**Why P8 needs it.** It is the only bridge that says *what* a robustness result
about the reference-error law implies operationally: every first-moment
monitoring consequence in every family is a functional of the law of `e` alone,
composed with one family-and-detector-specific function `A_f`. It licenses the
experiment design (measure the law of `e`, measure `A_f`, and check the
composition) — nothing more.

---

## The empirical law P8 tests (a hypothesis, NOT a theorem)

From `P8-T1` and P3's `A3`, `rho_c(D,f,m) = 1/|Gamma_A(D,f,m) - 1|` when
`Gamma_A > 1`. Define the **window scaling of the critical reuse fraction**

```text
K(D,f,m) := rho_c(D,f,m) / rho_c(D,f,1)
          = ( Gamma_A(D,f,1) - 1 ) / ( Gamma_A(D,f,m) - 1 ) ,     K(D,f,1) = 1 .
```

> **Hypothesis H1 (window-separability law).** `K(D,f,m)` depends on `m` alone:
> it is invariant across the detector family `D` and the innovation family `f`.
> Equivalently `Gamma_A(D,f,m) - 1 = (Gamma_A(D,f,1) - 1) / K(m)`, i.e. the
> whole `(D, f, m)` stability map factorises into a detector-and-distribution
> amplitude and a universal window profile.

There is **no theorem behind H1**. By `P8-L1(c)` it is equivalent to the
statement that the normalised lag profile
`w_r(D,f) := (gamma_r - 1)/(gamma_0 - 1)` is invariant in `D` and `f`, which is
a statement about how stopping-time selection distributes itself over recent
observations. P8 measures `w_r` directly so that a failure of H1 is diagnosed
rather than merely observed.

**Prior information used to set H1's margin (before any P8 production run).**
P3's `CLOSED` Gaussian boundary table gives, for `m = 2,3,5`, cross-*detector*
`K` agreeing to `0.1%`, `0.8%`, `1.1%`. Stage D's `Gamma_psi` (a *different*
estimand) gives a cross-*family* `c(5)` spread of about `12%` over the five
non-`t3` families. The gate margin in `CLOSURE_GATES.md` `G4` is set from those
two numbers and from nothing P8 measured.
