# P6 theory

```text
T6-A  one-step reference-risk bound, uniform over the decision box   EXACT THEOREM
T6-B  closed-loop invariant law + uniform geometric ergodicity       EXACT THEOREM (memoryless policies, rho_max < 1)
T6-C  exact conditional dominance and the Jensen-gap identity        EXACT THEOREM
T6-D  one-step tail control                                          EXACT (oracle form) / APPROXIMATE (implementable form)
T6-E  Pareto endpoints                                               EXACT (endpoint non-comparability) + EMPIRICAL (frontier)
```

Premises used, and only these: **T1** (raw-mean identity), **T2** (conditional
mean/variance factorisation), **T3** (symmetry), **T4/T5** (state-independent
stopping and moment bounds). All four are adjudicated `EXACT THEOREM` for the
frozen constant-policy Gaussian convention-A model and are explicitly licensed
to P6 (`P5_TO_P6_DEPENDENCY_AUDIT.md` section 1). **P5's T7 is not used**: it is
proved for a *fixed* `(D, m, rho)` and does not transfer to a policy-dependent
kernel. T6-B reproves the analogue from scratch and section 4.3 names exactly
where the new argument differs.

---

## 1. Setting

Fix a frozen detector `D` (CUSUM `k=1/2, h=5`, or SR `A = 520.886133602749`),
with its frozen reset, two-sided recurrence and inclusive post-update alarm
test. Fix a **decision box**

```text
Ucal = [0, rho_max] x {1,...,M} x {k_min,...,k_max} ,     rho_max < 1 ,  k_min >= 1 .
```

A cycle entered with reference error `e_j = x` runs on iid raw draws
`X_1, X_2, ... ~ N(0,1)`, which the detector sees as `z_t = X_t - x`. Let
`tau_x` be the inclusive alarm time from the reset state, `o_x` the **cycle
observation** -- the tuple `(tau, arm, overshoot, plus, minus, window, valid)`
of `OBSERVABILITY_AUDIT.md` F01-F07, which is a measurable function of
`(z_1, ..., z_tau)` and hence of `(x, X_1, ..., X_{tau})`.

A **memoryless policy** is a measurable `u : O -> Ucal`, `(rho, m, k) = u(o)`,
where `O` carries **only the cycle that has just ended**. Explicitly, `u` may
read `tau`, the alarm arm, the overshoot, the post-update detector statistics
and the terminal `z` window, and it may **not** read the cycle index, the
policy's own previous decisions, the previous cycle's `tau` or `zbar`, or the
reference displacement -- i.e. none of `cycle`, `prev_tau`, `prev_zbar`,
`prev_rho`, `prev_m`, `prev_k`, `displacement`, `last_move` of the harness's
`CycleObservation`. Those fields are legally observable
(`OBSERVABILITY_AUDIT.md` F09-F13) and a policy using them is perfectly
implementable; it is simply outside T6-B, because reading them makes the kernel
depend on more than `e_j` and the Markov state must be augmented. SAW reads
`tau` and the window and nothing else, which
`tests/test_observability.py::test_saw_decision_depends_only_on_the_audited_observables`
asserts directly by perturbing each of the nine excluded fields and checking
that no decision moves.
With `w = min(m, tau_x)`, `zbar = (1/w) sum_{r<w} z_{tau-r}` and an independent
`G ~ N(0,1)`, the reference update -- the **only** line P6 changes -- is

```text
e_{j+1} = rho (x + zbar) + (1 - rho) G / sqrt(k) .
```

**The raw-mean identity (T1)** rewrites this without the entering error:

```text
x + zbar = (1/w) sum_{r<w} X_{tau-r}  =:  U_x         (the RAW terminal-window mean)
e_{j+1}  = rho U_x + (1 - rho) G / sqrt(k) .                                    (1)
```

`x` survives only inside the *selection* of the window -- which observations are
in it and when the cycle stopped -- and not in the algebra. This is the single
structural fact every result below rests on.

Throughout, `H_j` is the sigma-field of everything known at the alarm ending
cycle `j` **including** `e_j`; `F_j subset H_j` is the *observable* sigma-field
of F01-F13. A policy is admissible iff `(rho_j, m_j, k_j)` is `F_j`-measurable
with values in `Ucal`.

---

## 2. T6-A. One-step reference-risk bound, uniform over the decision box

> **Theorem T6-A (EXACT).** Let `C_D := sup_x E_x[tau_x]`, finite by T4/T5.
> Then for **every** admissible policy -- adaptive, randomised or fixed --
>
> ```text
> sup_x  E[ e_{j+1}^2 | e_j = x ]  <=  rho_max^2 C_D  +  1 / k_min  =:  B .
> ```

*Proof.* `G` is independent of `(X_t)` and of `(rho, m, k)`, which are
functions of the `X_t`, and `E G = 0`, so the cross term in the square of (1)
vanishes:

```text
E[e_{j+1}^2 | x] = E[ rho^2 U_x^2 | x ] + E[ (1-rho)^2 / k | x ]
                 <= rho_max^2 E[U_x^2 | x] + 1/k_min .
```

By convexity of `t -> t^2` and non-negativity,
`U_x^2 <= (1/w) sum_{r<w} X_{tau-r}^2 <= sum_{t=1}^{tau_x} X_t^2`. Since
`{tau_x >= t}` is measurable w.r.t. `sigma(X_1,...,X_{t-1})` and `X_t` is
independent of it, Wald/Tonelli gives
`E_x sum_{t<=tau} X_t^2 = E_x[tau] E[X^2] = E_x[tau] <= C_D`. ∎

**Two remarks, both required for honesty.**

* The bound is *uniform over the policy*, not merely over the state. That is the
  property that makes an adaptive rule tractable here at all, and it is a
  consequence of (1): the policy's `rho` multiplies a quantity whose second
  moment is bounded independently of `x` **and** of the policy's own choices.
* The constant is loose. P5's admissible values for `C_D` (`9.9e8` CUSUM,
  `1.4e11` SR) are, in its own adjudication's words, "extremely loose"; they are
  qualitative. The **measured** `sup_x E_x[tau_x]` is `A(0) ~ 465` (attained at
  `x = 0`; the monotonicity of `A` in `|x|` is `S2`, measured, not proved). P6
  reports both and uses neither as a rate.

---

## 3. T6-C. Exact conditional dominance, and why this is not fixed-`rho` tuning

This is the campaign's central theorem: it says precisely what adaptivity can
buy, and it identifies fixed-`rho` tuning as the degenerate member of the same
family.

Fix a sigma-field `F` with `sigma(zbar_j, tau_j, w_j) subset F subset H_j`, and
let `k` be `F`-measurable with `nu := 1/k`. Define the **selection intensity**

```text
V := E[ U_j^2 | F ]           (the conditional second moment of the RAW window mean).
```

> **Lemma 3.1 (EXACT).** For any `F`-measurable `rho in [0,1]`,
> ```text
> E[ e_{j+1}^2 | F ] = h(rho; V) := rho^2 V + (1-rho)^2 nu ,
> ```
> `h` is strictly convex, minimised at `rho*(V) = nu / (V + nu) in (0,1)`, and
> ```text
> h(rho*; V) = Q*(V) := nu V / (V + nu) ,      h(rho; V) - h(rho*; V) = (V + nu)(rho - rho*)^2 .
> ```

*Proof.* (1) plus `G ⟂ F`, `E G = 0`, `E G^2 = 1`; then elementary calculus.
`rho* in (0,1)` strictly because `V > 0` and `nu > 0`. ∎

`rho*` is an **inverse-variance weight** between the reused window mean and the
fresh baseline: `rho* = (1/k) / (V + 1/k)`. This is the Family-F rule of the
pre-design, restated against the *observable* sigma-field instead of against the
latent `e_j` -- which is exactly what makes it implementable.

> **Theorem T6-C (EXACT).** Let `V` be non-degenerate, i.e. `P(V != E V) > 0`.
> Then, from a common entering law,
>
> **(i) Dominance.** For any constant `rho_0 in [0,1]`,
> ```text
> E[e_{j+1}^2 ; rho_0]  -  E[e_{j+1}^2 ; rho*]  =  E[ (V + nu)(rho_0 - rho*(V))^2 ]  >  0 .
> ```
>
> **(ii) The gain is exactly a Jensen gap.** The best *constant* reuse weight
> attains `min_{rho} E[h(rho; V)] = Q*(E V)`, while the `F`-measurable rule
> attains `E[Q*(V)]`. `Q*` is strictly concave on `(0, infinity)`
> (`Q*'' = -2 nu^2/(V+nu)^3`), so
> ```text
> Gap  :=  Q*(E V)  -  E[Q*(V)]  >  0 ,        Gap  ~  nu^2 Var(V) / (E V + nu)^3 .
> ```
>
> **(iii) When a plug-in still wins.** For an `F`-measurable estimate `rho_hat`,
> ```text
> E[h(rho_hat; V)]  <  Q*(E V)     <=>     E[ (V + nu) (rho_hat - rho*(V))^2 ]  <  Gap .
> ```

*Proof.* (i) and (iii) are Lemma 3.1's exact excess-risk identity, integrated.
(ii): `E[h(rho; V)] = rho^2 E V + (1-rho)^2 nu = h(rho; E V)` for constant
`rho`, so minimising over constants gives `Q*(E V)`; Jensen's inequality for the
strictly concave `Q*` gives the strict gap; the second-order form is Taylor's
theorem. ∎

**What (ii) means, in words.** *Fixed-`rho` tuning is exactly the `V = const`
member of this family.* Whatever the best fixed `rho` is, its risk is `Q*` of
the **average** selection intensity; the adaptive rule's risk is the **average**
of `Q*` of the selection intensity. The entire difference is the curvature of
`Q*` against the *dispersion* of `V` -- the cycle-to-cycle variability in how
hard this particular alarm selected its window. A campaign that only tunes
`rho` cannot access that variability by construction, no matter how fine its
grid.

**(iii) is the campaign's falsifiable design criterion**, and it is checkable
without ever running the policy: measure `Var(V)`, measure the plug-in error,
compare. `RESULTS.md` section 3 reports both sides of that inequality per cell.

**Three limits, stated because they matter.**

1. T6-C is **one step**, from a **common entering law**. It does not assert that
   the *stationary* second moment falls, because the two policies induce
   different stationary laws. That is measured, not proved.
2. `E[e^2]` is a **latent-layer** quantity. `S18` (P7-E rejected) forbids
   concluding any monitoring improvement from it. Every monitoring claim in
   `RESULTS.md` is a measurement.
3. `V` is latent. The implementable rule substitutes a design-time plug-in, so
   the *realised* method is governed by (iii), not by (ii).

---

## 4. T6-B. Closed-loop invariant law under a memoryless adaptive policy

`D9` (time-homogeneity) and P5's T7 are statements about a **fixed**
`(D, m, rho)`. Under an adaptive policy the kernel depends on the decision rule,
and the P5 adjudication's own "P6 must not" list forbids transferring T7. This
section supplies the replacement.

> **Theorem T6-B (EXACT).** Let `u` be a memoryless admissible policy with
> `rho_max < 1` and `1 <= k_min <= k(.) <= k_max`. Then `(e_j)` is a
> time-homogeneous Markov chain on `R` whose kernel `P_u` satisfies a
> **whole-space two-step minorisation**
> ```text
> P_u^2(x, A)  >=  epsilon nu_*(A)      for all x in R and Borel A ,
> ```
> with `epsilon > 0` and `nu_*` a probability measure, both independent of `x`.
> Consequently `P_u` admits a **unique** invariant probability `pi_u`, converges
> to it **uniformly geometrically** in total variation from every initial state,
> and `E_{pi_u}|e|^q < infinity` for every real `q > 0`. If in addition `u` is
> sign-equivariant, `pi_u` is symmetric.

### 4.1 Proof

**(a) Time-homogeneity.** By (1), `e_{j+1} = Psi(x, X_1, X_2, ..., G)` for a
fixed measurable `Psi` determined by `u`, and the innovation block
`(X_., G)` is iid across cycles and independent of the past, because the
detector is reset at each cycle start (`D1`) and the fresh draw is independent
of the cycle (`D6`). Memorylessness is essential: a policy carrying internal
state makes `Psi` depend on that state, and the Markov state must be augmented.

**(b) Uniform return to a compact set.** T6-A gives
`sup_x E[e_{j+1}^2 | x] <= B`. With `R* := sqrt(2B)` and `C := [-R*, R*]`,
Markov's inequality gives `inf_{x in R} P_u(x, C) >= 1/2`.

**(c) Minorisation on `C`.** Let `c_D` be the frozen detector's **one-step alarm
margin**: the least `c` such that a single innovation `z_1 >= c` forces an
inclusive alarm from the reset state. For CUSUM, `plus_1 = max(0, z_1 - 1/2)`
crosses `h = 5` iff `z_1 >= 5.5`, so `c_CUSUM = 11/2`. For SR,
`log r_plus,1 = z_1 - 1/2` crosses `log A` iff `z_1 >= log A + 1/2`, so
`c_SR = log(520.886133602749) + 1/2 ~ 6.7555`. Put `J := [c_D, c_D + 1]`.

On the event `{z_1 in J}` we have `tau_x = 1`, hence `w = min(m, 1) = 1` **for
every `m` the policy could choose**, hence `zbar = z_1` and `U_x = x + z_1`.
Crucially, the cycle observation on this event is
`o = (tau=1, arm=+1, overshoot = f_D(z_1), plus = g_D(z_1), minus = 0,
window = (z_1))`, **a function of `z_1` alone**. Therefore
`(rho, m, k) = u(o) = (rho(z_1), m(z_1), k(z_1))` does not depend on `x`, and

```text
e_{j+1} = rho(z_1) (x + z_1) + (1 - rho(z_1)) G / sqrt(k(z_1)) .              (2)
```

Given `e_j = x`, `z_1 = X_1 - x ~ N(-x, 1)`, so for `x in C` and `z in J` the
density of `z_1` is at least `p_J := phi(c_D + 1 + R*) > 0`, uniformly in `x`.
Given `z_1 = z`, (2) is Gaussian with mean `mu = rho(z)(x+z)`, `|mu| <= M := R* + c_D + 1`,
and standard deviation `s = (1 - rho(z))/sqrt(k(z)) in [s_min, s_max]`,
`s_min := (1 - rho_max)/sqrt(k_max) > 0`, `s_max := 1/sqrt(k_min) <= 1`. Hence for
every `y in [-1, 1]` the conditional density of `e_{j+1}` is at least

```text
q := (1/s_max) (2 pi)^{-1/2} exp( -(1 + M)^2 / (2 s_min^2) )  >  0 ,
```

again uniformly in `x in C` and `z in J`. Integrating `z` over `J` (length 1),

```text
P_u(x, A)  >=  p_J q  Leb(A n [-1,1])  =  epsilon_1 nu_*(A) ,   x in C ,
```

with `nu_*` uniform on `[-1,1]` and `epsilon_1 := 2 p_J q`.

**`rho_max < 1` is used exactly here**, to keep `s_min > 0` so the fresh draw
smooths the (`x`-dependent) location. The alternative hypothesis
"`rho(z) = 1` for all `z in J`" also works, because then `e_{j+1} = X_1` whose
raw density on `x + J` is bounded below independently of `x`; what the proof
cannot tolerate is a policy that takes `rho` arbitrarily close to `1` on that
event without reaching it. SAW satisfies the stated hypothesis structurally:
`rho_j = nu/(V_hat_j + nu) <= nu/(s_floor + nu) < 1` and is additionally capped
at `rho_max`.

**(d) Two-step whole-space minorisation.** For any `x in R`,
`P_u^2(x, A) >= int_C P_u(x, dy) P_u(y, A) >= (1/2) epsilon_1 nu_*(A)`. Set
`epsilon := epsilon_1 / 2`.

**(e) Doeblin.** A whole-space minorisation for `P_u^2` makes `P_u^2` a uniform
(Doeblin) kernel: there is a unique `P_u^2`-invariant probability `pi`, and
`|| P_u^{2n}(x, .) - pi ||_TV <= 2 (1 - epsilon)^n` for all `x` (Meyn & Tweedie,
*Markov Chains and Stochastic Stability*, 2nd ed., Thm 16.0.2; equivalently, by
the Dobrushin contraction implied by the minorisation decomposition). `pi P_u`
is also `P_u^2`-invariant, so `pi P_u = pi` by uniqueness, so `pi` is
`P_u`-invariant; any `P_u`-invariant law is `P_u^2`-invariant and hence equals
`pi`. Geometric TV convergence for `P_u` follows with rate
`2(1-epsilon)^{floor(n/2)}`.

**(f) Moments.** For integer `p >= 1`, convexity gives
`|U_x|^{2p} <= sum_{t<=tau} |X_t|^{2p}`, so by the same Wald/Tonelli step
`E[|U_x|^{2p} | x] <= C_D E|X|^{2p} = C_D (2p-1)!!`. With
`|a+b|^{2p} <= 2^{2p-1}(|a|^{2p}+|b|^{2p})` and `E|G/sqrt k|^{2p} <= (2p-1)!!`,

```text
sup_x E[ |e_{j+1}|^{2p} | x ]  <=  2^{2p-1} (2p-1)!! ( C_D + 1 )  =:  B_p  <  infinity .
```

Integrating against the invariant `pi` gives `E_pi |e|^{2p} <= B_p`; every real
`q > 0` follows by Lyapunov's inequality from a larger even integer.

**(g) Symmetry.** The frozen two-sided detector is sign-symmetric: under
`x -> -x`, `X_t -> -X_t` we get `z_t -> -z_t`, the two arms swap, `tau` is
unchanged, and `U_{-x} = -U_x`. If `u` is sign-equivariant -- `rho, m, k`
unchanged when the observation is negated and the arm flipped, which SAW is
because it depends on `zbar` only through `zbar^2` -- then
`P_u(-x, -A) = P_u(x, A)`, so `pi` is symmetric by uniqueness. ∎

### 4.2 What T6-B does and does not give

* It gives well-posedness: the stationary objectives of
  `OPTIMIZATION_FORMULATIONS.md` are meaningful for SAW.
* It gives uniform-in-time tightness from any start, and rules out divergence.
* It does **not** give a usable mixing rate. `epsilon` involves
  `exp(-(1+M)^2 / (2 s_min^2))` with `M ~ 30` on the measured constant, i.e. it
  is astronomically small. It must never be compared with a measured IACT. This
  is the same qualitative/quantitative gap the P5 adjudication recorded for T7.
* It does **not** bound sample paths. An invariant law with unbounded support
  still has arbitrarily large excursions (the P5 adjudication rejects the
  "exact finite-`e` reset" reading, and P6 keeps its guards accordingly).
* It applies to **memoryless** policies only. `CappedReusePolicy` (B10), the
  Family-E filter and any EWMA-carrying rule fall outside it; for those the
  campaign runs in finite-horizon language and says so.

### 4.3 Exactly where this differs from P5's T7

Three places, and they are the reason the theorem needed proving rather than
citing.

| # | in T7 | in T6-B |
|---|---|---|
| 1 | the kernel is indexed by a fixed `(m, rho)`; homogeneity is immediate | the kernel is induced by a decision rule; homogeneity has to be established, and **fails** if the policy carries memory |
| 2 | the one-step moment bound holds for the fixed `rho` | the bound must hold **uniformly over the decision box**; it does, because (1) puts `rho` outside the selected mean, so the policy cannot inflate `E[U_x^2]` |
| 3 | the minorising event `{tau=1}` gives `w = 1` for every `m` | additionally the **decision itself** must not depend on `x` on that event -- true because a memoryless policy reads only the cycle's own innovations -- and the fresh component must survive, which is the new hypothesis `rho_max < 1` |

---

## 5. T6-D. One-step tail control

The campaign's primary objective is a delay **tail** (`S9`), so the natural
control target is `P(|e_{j+1}| > c | .)` at the ARL-calibrated radius `c_beta`.

**(a) The oracle form is exact.** Given `H_j` -- i.e. given the realised raw
window mean `U_j` -- the only remaining randomness is the fresh draw, so

```text
P( |e_{j+1}| > c | H_j )
    =  Phibar( (c - rho U_j) sqrt(k) / (1-rho) )  +  Phi( (-c - rho U_j) sqrt(k) / (1-rho) )
```

**exactly**, for every `rho < 1`. Minimising this over `rho in [0, rho_max]` is
a one-dimensional smooth problem and defines oracle `Z2`. This is an exact
theorem, and it is not implementable: `U_j` is latent.

**(b) The Chebyshev route is exact and useless.** `P(|e_{j+1}| > c | F_j) <=
h(rho; V)/c^2`, minimised by the same `rho*` at `Q*(V)/c^2`. At the radius that
matters (`c_{0.25} ~ 0.28`) and the measured `Q* ~ 0.15..0.7`, the bound exceeds
`1` in every cell of the design grid: **it never binds.** This is recorded as a
*failed* route rather than omitted, because `METHOD_NOVELTY_SEPARATION.md` N2
warns precisely against presenting a never-binding bound as a safety guarantee.

**(c) The implementable form is an approximation.** Substituting the design-time
plug-in `(mu_hat, s_hat)` for the conditional law of `U_j` given `F_j` and
treating that law as Gaussian gives

```text
rho_j  =  argmin_{rho in [0, rho_max]}  P( |N( rho mu_hat , rho^2 s_hat + (1-rho)^2/k )| > c ) ,
```

which is `SAW-T`. The Gaussian step is an approximation -- `U_j | F_j` is a
*selected* raw-window mean, not a normal variate -- and its size is measured
directly against a Monte Carlo evaluation of the true conditional tail
(`RESULTS.md` section 6). SAW-T is therefore reported as an **approximate
one-step tail rule**, never as a guarantee.

**No route to a genuine enforceable tail bound at the `c ~ 0.28` scale was
found.** The pre-design's route 2 (a sharp sub-Gaussian bound on a
stopping-time-selected mean) remains open and is listed in `LIMITATIONS.md`.

---

## 6. T6-E. Pareto endpoints

Under the primary cost model `C_fresh = k_j 1{rho_j < 1}` (the number of newly
collected observations):

> **Proposition T6-E (EXACT, given the cost model).** `rho_j == 1` is the unique
> policy in `Ucal'` (the box widened to include `rho = 1`) with zero fresh-sample
> cost; every policy with `P(rho_j < 1) > 0` costs at least
> `k_min P(rho_j < 1) > 0`. Hence the cost coordinate has a single degenerate
> minimiser, and it is full reuse.

Combined with two *closed* P7 measurements -- full reuse is the monitoring-worst
case (`S3`, `S5`, `S8`), and fresh-only still loses `65%-83%` of nominal ARL
(`S4`) -- the two endpoints of the frontier are **not comparable**: neither
dominates. That is the non-degeneracy statement the pre-design anticipated, and
it is as far as the theory goes; the frontier itself is measured
(`RESULTS.md` section 5).

---

## 7. Status table

| statement | status | premises | where it is used |
|---|---|---|---|
| (1) raw-mean identity restated for `F_j`-measurable decisions | **EXACT** | T1 | everywhere |
| T6-A uniform one-step bound | **EXACT** | T1, T4/T5 | T6-B(b); feasibility |
| T6-A's constants | `EMPIRICAL_ONLY` (loose theorem constant reported beside the measured one) | P5 §T5, `S2` | reporting only |
| Lemma 3.1 one-step quadratic and `rho*` | **EXACT** | T1, T2 | the method's derivation |
| T6-C(i) dominance | **EXACT** | T1, T2 | mechanism claim |
| T6-C(ii) Jensen-gap identity | **EXACT** | T1, T2 | *the* separation from fixed-`rho` |
| T6-C(iii) plug-in criterion | **EXACT** | T1, T2 | falsifiable design criterion, measured |
| T6-B closed-loop ergodicity | **EXACT**, memoryless + `rho_max < 1` | T1, T4/T5, Doeblin | well-posedness of stationary language for SAW |
| T6-B for policies with memory | **OPEN** | — | `LIMITATIONS.md` |
| T6-D(a) oracle tail form | **EXACT** | T1 | oracle `Z2` |
| T6-D(b) Chebyshev bound | **EXACT but never binding** | T1, T2 | reported as a failed route |
| T6-D(c) implementable tail rule | **APPROXIMATION**, error measured | T1, T2 + a Gaussian step | SAW-T |
| T6-E endpoint non-comparability | **EXACT** given the cost model, plus closed `S3`/`S4` | cost model, `S3`, `S4` | frontier framing |
| stationary second moment of SAW below best fixed `rho` | **NOT PROVED** — measured | — | `RESULTS.md` |
| any monitoring consequence of a reference-state gain | **FORBIDDEN** (`S18`, `X6`) | — | measured, never inferred |
