# P6R theorem scope

```text
T6-B = EXACT_VALID                          (unchanged; policy-class scope clarified)
T6-C = VALID_WITH_NARROWER_ASSUMPTIONS      (exact for FIXED k; restated below)
```

Premises used, and only these: **T1** (raw-mean identity), **T2** (conditional
mean/variance factorisation), **T3** (symmetry), **T4/T5** (state-independent
stopping and moment bounds) — all adjudicated `EXACT` for the frozen
constant-policy Gaussian convention-A model and licensed to P6. P5's **T7 is
not used**.

---

## 1. T6-B — unchanged, with its policy class stated explicitly

> **Theorem T6-B (EXACT).** Fix a frozen detector and a decision box
> `Ucal = [0, rho_max] x {1..M} x {k_min..k_max}` with `rho_max < 1`,
> `k_min >= 1`. Let `u : O -> Ucal` be a **memoryless** admissible policy. Then
> `(e_j)` is a time-homogeneous Markov chain on `R`, its kernel `P_u` satisfies a
> whole-space two-step minorisation `P_u^2(x,A) >= epsilon nu_*(A)` with
> `epsilon > 0` and `nu_*` independent of `x`, and consequently `P_u` admits a
> **unique** invariant probability `pi_u`, converges to it **uniformly
> geometrically** in total variation from every initial state, and satisfies
> `E_{pi_u} |e|^q < infinity` for every real `q > 0`. If `u` is sign-equivariant,
> `pi_u` is symmetric.

The proof is unchanged from `p6_safe_rebaselining/THEORY.md` section 4 and is
not restated here. The adjudication returned `EXACT_VALID`; P6R adds only the
**policy-class clarification** that the proof's step (c) requires, and which is
the single place the theorem could be misapplied:

> **Scope of "memoryless".** `O` carries **only the cycle that has just ended**.
> `u` may read `tau`, the alarm arm, the overshoot, the post-update detector
> statistics and the terminal `z` window. It may **not** read `cycle`,
> `prev_tau`, `prev_zbar`, `prev_rho`, `prev_m`, `prev_k`, `displacement` or
> `last_move`. Those eight fields are legally *observable*
> (`OBSERVABILITY_AUDIT.md` F09-F13) and a policy using them is perfectly
> implementable — it is simply **outside T6-B**, because reading them makes the
> transition kernel depend on more than `e_j` and the Markov state must be
> augmented.
>
> Why this is exactly where the theorem lives: step (c) minorises on the event
> `{z_1 in J}`, where `tau = 1` forces `w = min(m,1) = 1` for every `m`, so
> `U_x = x + z_1` and the cycle observation is a function of **`z_1` alone**.
> A policy that read any of the eight excluded fields would make `u` depend on
> the history as well, the minorising measure would depend on that history, and
> the Doeblin construction would fail.

**SAW-M is inside the scope**, and this is asserted mechanically rather than
argued: `tests/test_p6r_method_identity.py` perturbs each of the eight excluded
fields and asserts no SAW-M decision moves, and asserts `rho_j < rho_max`
strictly in every measured cell. Policies **outside** the scope include
`CappedReusePolicy` (B10), any EWMA-carrying rule, and the Family-E filter; for
those the closed-loop stationarity question remains **open**.

## 2. T6-C — the strongest surviving exact statement, for fixed `k`

Fix `k`, hence `nu = 1/k`. Let `F` be a sigma-field with
`sigma(zbar_j, tau_j, w_j) subset F subset H_j` and let
`V = E[U_j^2 | F]` be the **selection intensity**, where `U_j = e_j + zbar_j` is
the realized raw terminal-window mean (exact, by T1).

> **Theorem T6-C (EXACT, fixed `k`).** With `nu = 1/k` **constant**:
>
> **(a) One-step decomposition.** For any `F`-measurable `rho in [0,1]`,
> ```text
> E[e_{j+1}^2 | F] = h(rho; V) = rho^2 V + (1-rho)^2 nu ,
> ```
> strictly convex, minimised pointwise at
> ```text
> rho*(V) = nu / (V + nu)  in (0,1) ,      h(rho*; V) = Q(V) := nu V / (V + nu) ,
> ```
> with the exact excess-risk identity `h(rho; V) - Q(V) = (V + nu)(rho - rho*)^2`.
>
> **(b) The constant-policy optimum depends on `V` only through `E[V]`.** For a
> **constant** `rho_0`, `E[h(rho_0; V)] = h(rho_0; E[V])`, so
> ```text
> min over CONSTANT rho_0 of  E[e_{j+1}^2]  =  Q(E[V]) .
> ```
>
> **(c) The adaptive advantage is a strict Jensen gap.** `Q` is strictly concave
> on `(0, infinity)` (`Q'' = -2 nu^2 / (V + nu)^3`), so whenever `V` is
> non-degenerate,
> ```text
> Gap := Q(E[V]) - E[Q(V)]  >  0 ,       Gap  ~  nu^2 Var(V) / (E[V] + nu)^3 .
> ```
> **Fixed-`rho` tuning is exactly the `V = const` member of this family.**
>
> **(d) Plug-in criterion.** For an `F`-measurable estimate `rho_hat`,
> `E[h(rho_hat; V)] < Q(E[V])` **iff** `E[(V + nu)(rho_hat - rho*(V))^2] < Gap`.

### 2.1 What is explicitly NOT claimed

* **The scalar Jensen formula is not claimed unchanged for adaptive `k`.** With
  `k_j` chosen from observables, `nu_j = 1/k_j` is random, `Q` becomes a
  function of two arguments, step (b) fails as written — `E[h(rho_0; V, nu)]` is
  no longer `h(rho_0; E V, E nu)` — and the single-variable concavity argument
  of step (c) does not apply. **No theorem for adaptive `k` is asserted here,
  and none is manufactured.** The adaptive-`k` case is an open question.
* **All headline SAW-M cells use fixed `k`.** Every cell in the P6R confirmation
  plan fixes `k` in advance (`k = m` at the primary cell and throughout the
  precommitted robustness set). T6-C is therefore **exact for the actual P6/P6R
  headline setting**, and the narrower scope costs the campaign nothing it
  claims.
* T6-C is a **one-step** statement from a **common entering law**, about a
  **latent-layer** quantity. It does not assert that the stationary second
  moment falls, and `S18`/`X6` forbid inferring any monitoring consequence from
  it. Both are measured instead.
* The implementable rule substitutes a design-time plug-in for `V`, so the
  realized method is governed by (d), not by (c). **The plug-in is not the
  oracle `F`-measurable optimizer** and is nowhere claimed to be.

### 2.2 How T6-C is evidenced in P6R

Two statistics, both precommitted before execution:

1. **the restricted diagnostic** — the original `sigma(V_hat)`-restricted
   measurement, retained and **labelled restricted** wherever it appears. It
   estimates `E[U^2 | V_hat]`, i.e. the plug-in's *calibration*, so both its gap
   and its plug-in error are `sigma(V_hat)`-restricted;
2. **the direct realized one-step risk** (`onestep.py`) — no binning, no
   conditional-expectation estimate, no plug-in reference. On the same cycles,
   `R_star = min over constant rho_0` of the realized risk and `R_adapt` the
   realized risk of the weights SAW-M actually chose, giving
   `G = 1 - R_adapt / R_star` with a replicate-cluster BCa interval. Because
   `R_adapt` uses the plug-in, `G` is a **lower bound** on the achievable gap.

## 3. What P6R does not touch

`T6-A` (uniform one-step bound), `T6-D` (one-step tail control: the Chebyshev
route is exact and never binds; the sharp route is open; the implementable rule
is an approximation) and `T6-E` (Pareto endpoints) are unchanged from
`p6_safe_rebaselining/THEORY.md` and carry their original status. `T6-D`'s
consequence stands: **P6 has no theorem-backed safety guarantee**, and P6R does
not create one.
