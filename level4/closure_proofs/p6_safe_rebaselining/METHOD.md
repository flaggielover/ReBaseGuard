# METHOD — Selection-Aware Weighting (SAW)

```text
CANDIDATE_METHOD  = SAW-M  (selection-aware weighting, second-moment form)
VARIANT           = SAW-T  (approximate one-step tail form)
CLASS             = implementable  (memoryless; no latent state, no future, no Delta)
FREE_HYPERPARAMETERS = none.  Four constants, all least-squares; two structural.
```

---

## 1. The problem, stated exactly

After an alarm ending cycle `j`, the operator must choose a new reference. The
frozen model's update (`D6`), generalised in the **one line** P6 is allowed to
change, is

```text
e_{j+1} = rho_j ( e_j + zbar_j ) + (1 - rho_j) fresh_j ,
zbar_j  = (1/w_j) sum_{r<w_j} z_{tau_j - r} ,   w_j = min(m_j, tau_j) ,
fresh_j ~ N(0, 1/k_j) drawn after the alarm, independent of the cycle.
```

Detector recurrences, thresholds, reset, the inclusive stopping rule and the
convention-A truncated denominator are untouched (`D1`-`D7`, `X4`), and a
constant policy reproduces `rebaseguard_p7.chain.simulate_chain` with
**bit-identical `tau`** (`results/correspondence.json`: 24/24 cells identical,
`max |e_start difference| = 0`).

## 2. Why reuse is harmful here — the mechanism P6 attacks

The exact raw-mean identity (**T1**, adjudicated `EXACT`, reproduced
independently to `6.66e-16` in 48 configurations) rewrites the update without
the latent error:

```text
e_j + zbar_j  =  U_j  :=  (1/w_j) sum_{r<w_j} X_{tau_j - r}         (the RAW window mean)
e_{j+1}       =  rho_j U_j + (1 - rho_j) fresh_j .
```

If `U_j` were an ordinary mean of `w_j` iid `N(0,1)` draws it would have
variance `1/w_j` and reuse would be *free information*. It is not: the window is
the one that **triggered the alarm**. The campaign's own calibration measures
`E[U_j^2]` at `2.52` for `m = 1` against the unselected `1.00`, and `0.95` for
`m = 5` against `0.20` — the selection inflates the second moment by `2.5x` to
`4.7x`. That inflation, recursively fed back, *is* the reference-state
distortion P7 documented.

**But the selection intensity is not the same every cycle**, and — this is the
whole idea — **it is largely observable**. Regressing the latent `U_j` on the
observable readout `(zbar_j, tau_j)` gives `R^2 = 0.95` in every one of the
eight `(detector, m)` families. The alarm that damages the reference announces
how badly it is about to damage it.

## 3. Derivation

Fix the observable sigma-field `F_j` (F01-F13) and let `nu = 1/k_j`. Because
`fresh_j` is independent of the cycle with mean `0` and variance `nu`,

```text
E[ e_{j+1}^2 | F_j ]  =  rho_j^2 V_j + (1 - rho_j)^2 nu ,      V_j := E[ U_j^2 | F_j ] ,
```

a strictly convex quadratic in `rho_j`, minimised at the **inverse-variance
weight**

```text
rho*_j  =  nu / ( V_j + nu )   in (0,1)  strictly ,       with value   Q*(V_j) = nu V_j / (V_j + nu) .
```

This is exactly Family F of the pre-design, taken against the **observable**
sigma-field rather than against the latent `e_j` — which is what makes it
implementable. Both steps rest only on T1 and T2, both adjudicated `EXACT`
(`P5_TO_P6_DEPENDENCY_AUDIT.md` section 1), so Family F is a *derivation* here
and not an empirical rule.

`THEORY.md` T6-C turns this into the mechanism claim: `Q*` is strictly concave,
the best constant `rho` attains `Q*(E V)`, the adaptive rule attains `E[Q*(V)]`,
and the entire difference is the **Jensen gap of `Q*` against the dispersion of
the selection intensity**. Fixed-`rho` tuning is precisely the `V_j = const`
member of the same family.

## 4. The implementable rule

`V_j` is latent. SAW substitutes a **design-time plug-in** — legal exactly as
the precomputed `A(.)` and `P(tau | e)` tables of `OBSERVABILITY_AUDIT.md` F21
are legal: it uses a function computed offline, never a latent argument.

```text
input at the alarm:  tau_j ,  the terminal window  ->  zbar_j = zbar_j(m) ,  w_j = min(m, tau_j)

mu_hat_j = ( g0 + g1 / sqrt(tau_j) ) * zbar_j
s_hat_j  = max( s0  if w_j == m  else  s1 ,  1e-2 )
V_hat_j  = mu_hat_j^2 + s_hat_j

rho_j = min(  (1/k) / ( V_hat_j + 1/k ) ,  rho_max )
m_j   = m ,   k_j = k
```

* **`mu_hat`** estimates `E[U_j | F_j]`. Oddness of the frozen model in `e`
  (T3) forces this to be an odd function of the readout, so linear-through-origin
  is the natural first-order form. The `1/sqrt(tau)` interaction is kept because
  the stopping geometry carries real gain information: at `tau = 1` the fitted
  gain `g0 + g1` is near zero (a one-observation alarm says the reference is far
  out, and the raw observation is then nearly unselected), while at large `tau`
  it approaches `g0 ~ 0.92-0.99`. A cubic term was tested and discarded (under
  2% further residual reduction).
* **`s_hat`** estimates the residual conditional variance, split by the
  truncation indicator `w < m` rather than smoothed in `1/w`: truncated windows
  are 0.09%-5.3% of cycles but carry 30x-70x the residual variance, which no
  `m/w` averaging law predicts, so two group means are both exact and stable.
* **`rho_max = 0.95`** and the variance floor `1e-2` are **structural**: they are
  the hypotheses `THEORY.md` T6-B needs for its minorisation, not tuning knobs.
  Both are measured non-binding in every campaign cell.

**Four constants, and how they are obtained.** `(g0, g1)` by ordinary least
squares, `(s0, s1)` as two group means, inside a **fixed-point** loop
(calibrate under the current policy, rebuild the policy, repeat) because the law
of `e` is policy-dependent. All on `TUNE` seeds, all at `Delta = 0`. **No search,
no grid, no tuned hyperparameter.**

### 4.1 SAW-T, the tail variant

Same plug-in, different one-step objective: minimise the approximate one-step
tail risk at the ARL-calibrated radius `c_beta`,

```text
rho_j = argmin_{rho in [0, rho_max]}  P( | N( rho mu_hat_j , rho^2 s_hat_j + (1-rho)^2/k ) | > c_beta ) .
```

`c_beta = sup{c : A(c) >= beta A(0)}` at the preregistered `beta = 0.25`,
derived from P7's *closed* response curve: `0.2816` (CUSUM), `0.2656` (SR).
The Gaussian step is an approximation and is reported as one (`THEORY.md` T6-D).

### 4.2 The information ladder — the ablation structure is built in

SAW is one member of a ladder indexed by how much is known about `V_j`:

| rung | `V` used | class | what it is |
|---|---|---|---|
| `Z1` oracle SAW | the realised `U_j^2` | oracle | ceiling for the rule shape |
| **SAW-M** | the calibrated plug-in `mu_hat^2 + s_hat` | implementable | **the proposed method** |
| SAW `no_tau` | `mu_hat` without the `1/sqrt(tau)` feature | implementable | ablation: remove the stopping-geometry sensor |
| SAW `naive` | `zbar_j^2` (the naive magnitude proxy) | implementable | ablation: replace the calibrated readout with the raw one |
| SAW `flat` | the constant `E[V]` | implementable | ablation: remove the sensor entirely — **and this is exactly a fixed-`rho` policy**, with `rho = nu/(E V + nu)` |

The bottom rung *is* the incumbent method. That is the cleanest possible
statement of what SAW adds, and it makes the sensor ablation exact rather than
approximate.

## 5. Information set, stated as the observability gate requires

| question | answer |
|---|---|
| what is observed at decision time | `tau_j`; the terminal `z` window; hence `zbar_j(m)` and `w_j` (F01, F05, F06) |
| what is estimated | `E[U_j \| F_j]` and `Var(U_j \| F_j)`, through four design-time constants |
| what is latent | `e_j`, `U_j`, `R(e_j)`, `S(e_j)`, `A(e_j)`, `Delta` — **none is read** |
| is the shift direction known | **no**. SAW is calibrated entirely at `Delta = 0` |
| does future information leak in | **no**. The decision uses only the cycle that has just ended |
| does the policy carry memory | **no**. SAW is memoryless — which is what lets `THEORY.md` T6-B apply |
| is `e_0` needed | **no**. SAW never touches `displacement`/`last_move`, so it is legal in both the `e_0 = 0` and `e_0 ~ N(0, 1/m_0)` regimes (the section 4a leak does not reach it) |

## 6. Pseudocode

```text
design time, on TUNE seeds, at Delta = 0 only:
    policy <- ConstantPolicy(rho = 0.2, m, k)
    repeat until (g0, g1, s0) stop moving:
        run the frozen chain under `policy`, collect (zbar, tau, w, U)
        (g0, g1) <- lstsq( U ~ zbar , zbar/sqrt(tau) )
        r        <- U - (g0 + g1/sqrt(tau)) * zbar
        s0       <- mean(r^2 | w == m) ;  s1 <- mean(r^2 | w < m)
        policy   <- SAW(g0, g1, s0, s1, m, k)

deployment, at every alarm:
    zbar <- mean of the last min(m, tau) innovations       # already stored
    mu   <- (g0 + g1/sqrt(tau)) * zbar
    s    <- (w == m) ? s0 : s1
    rho  <- min( (1/k) / (mu*mu + max(s,1e-2) + 1/k) , 0.95 )
    new reference  <-  rho * (old reference + zbar) + (1-rho) * mean(k fresh observations)
```

Cost per alarm: one square root, three multiplications, one division. No table
lookup, no optimisation, no state. Deployable.

## 7. Failure modes this method can have (registered in advance)

| # | failure | detector |
|---|---|---|
| M1 | the plug-in error exceeds the Jensen gap, so SAW loses to the best fixed `rho` despite the theory | `THEORY.md` T6-C(iii) is measured directly, both sides, per cell |
| M2 | the calibration is fitted at `Delta = 0` and misbehaves under a shift, where `zbar` acquires a `-Delta` offset | every SAW result is measured at `Delta in {0.5, 1, 2}`; `ROBUSTNESS.md` |
| M3 | `E[e^2]` improves but monitoring does not (`S18`, `F2`) | every monitoring metric is measured, never inferred |
| M4 | the closed loop is unstable or slow-mixing (`H7`) | `THEORY.md` T6-B plus the R3 curves to cycle 50 |
| M5 | the fixed point of the calibration is not unique, or drifts between `TUNE` and `EVAL` | the fixed-point trace and the `TUNE -> EVAL` drift are reported |
| M6 | SAW is a renamed EWMA / shrinkage estimator with prior art | `NOVELTY_AUDIT.md` |
