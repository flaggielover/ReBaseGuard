# Stage D — Phase 0 correspondence audit

Written before the Stage D protocol was frozen and before any confirmatory data
existed. All numbers here come from an **audit-only** seed family
`SeedSequence([20260822, 7, k])`, which is disjoint from the confirmatory family
declared in `STAGE_D_PROTOCOL.md`.

---

## 1. Baseline integrity

Verified, not assumed:

| Suite | Result |
|---|---|
| frozen Level 1–3 (`rebaseguard-proof`) | 90 passed |
| Level 4 Stage A | 290 passed |
| Level 4 Stage B | 46 passed |
| Level 4 Stage C | 48 passed |
| Level 4 Stage C.1 | 36 passed |
| **total** | **510 passed, 0 failed** |

Frozen decisions unchanged: Stage B `STAGE-B-CLOSED-RIGOROUS-PERIOD2`
(root `[1.028724, 1.044724]`, `lambda_2 ∈ [0.108148, 0.832532]`), Stage C
`STAGE-C-PARTIAL` (C6 failed), Stage C.1
`STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY`.

**There is no Stage D simulator in the repository.** The pilot directory
`ReBaseGuard_Level4_StageD_TheoryBlueprint_and_Pilot_2026-08-22/` contains only
a blueprint, CSVs, two `.npy` files and a figure. Stage D production code is
therefore written fresh here, reusing the frozen detector primitives
(`rebaseguard_level4.frozen.cusum_update`) so the CUSUM semantics cannot drift.

---

## 2. THE STOPPED-WINDOW AMBIGUITY — resolved

### 2.1 What the blueprint says

Three statements, which cannot all hold:

| # | Blueprint | Location |
|---|---|---|
| S1 | `zbar_m = (1/w) sum_{i<w} z_{tau-i}`, `w = min(m, tau)`, "the truncated convention is used throughout" | §2.1, line 141–143 |
| S2 | `Gamma_m = E[zbar_m T_tau] = (1/m) sum_{i<m} gamma_i` — presented as an **exact closed form** and listed among the "two structural claims that **are** safe, because they are theorems" | §2.2 line 151; §7 line 477 |
| S3 | `Gamma_m -> Gamma_inf = E[T_tau^2 / tau]` as `m -> inf` | §2.2 line 163 |

Define the two candidate estimands:

```text
A (truncated denominator)   Gamma_m^A = E[ (1/min(m,tau)) sum_{i<min(m,tau)} z_{tau-i} · T_tau ]
B (fixed denominator m)     Gamma_m^B = E[ (1/m)          sum_{i<min(m,tau)} z_{tau-i} · T_tau ]
                                      = (1/m) sum_{i<m} gamma_i,   gamma_i = E[ z_{tau-i} 1{i<tau} T_tau ]
```

`B` equals the closed form **identically, by construction**: the denominator is
non-random, so expectation and the finite sum commute. `A` does not, because
`1/min(m,tau)` is random and correlated with the stopped sum.

Limits: `A -> E[T_tau^2/tau]` (a positive constant); `B -> ARL_0/m -> 0`.

**So S2 is a statement about B, while S1 and S3 are statements about A. S2 is
false under the convention the blueprint itself adopts.**

### 2.2 Measured

400,000 independent cycles, CUSUM `k=1/2, h=5`, `e=0`, audit seed:
`ARL_0 = 465.967`, `E[T_tau^2] = 466.522` (Wald's second identity holds),
`E[T_tau^2/tau] = 1.4048`.

| `m` | `(1/m) sum gamma_i` | conv B | conv A | `A -` closed form | in SE |
|---|---|---|---|---|---|
| 1 | 15.92956 | 15.92956 | 15.92956 | −0.00000 | 0.0 |
| 5 | 10.22888 | 10.22888 | 10.23137 | +0.00249 | 0.1 |
| 10 | 7.09680 | 7.09680 | 7.11946 | +0.02265 | 0.9 |
| 20 | 4.19842 | 4.19842 | 4.27706 | +0.07863 | **5.3** |
| 50 | 2.16376 | 2.16376 | 2.36679 | +0.20303 | **27.4** |
| 75 | 1.69210 | 1.69210 | 1.96601 | +0.27391 | **47.7** |
| 100 | 1.45062 | 1.45062 | 1.78078 | +0.33015 | **66.8** |
| 250 | 0.93731 | 0.93731 | 1.48656 | +0.54924 | **152.1** |

Driver — the probability that a cycle is shorter than the window:

| `m` | 1 | 5 | 10 | 20 | 50 | 75 | 100 | 150 | 250 |
|---|---|---|---|---|---|---|---|---|---|
| `P(tau < m)` | 0.000 | 0.001 | 0.008 | 0.028 | 0.089 | 0.138 | 0.184 | 0.268 | 0.411 |

### 2.3 Which convention did each pilot file use?

| pilot file | matches | evidence |
|---|---|---|
| `gamma_m_direct.csv` | **convention A** | agrees at all 8 shared `m` (1→250), each within ~1.5 SE |
| `rho_c_vs_m.csv` | **not A**; consistent with B at `m = 20, 50`, and with neither cleanly beyond | this is the whole source of the 41σ disagreement between the two files at `m = 100` |

The two pilot files therefore disagree because **they compute different
estimands**, not because of Monte Carlo error.

### 2.4 Frozen production choice

**Convention A: truncated window with denominator `w = min(m, tau)`.**

Chosen because it is what the blueprint's own protocol text adopts (S1), and
because it is what "reuse the last `m` observations of the stopped path" means
operationally: when a cycle supplies only `tau < m` observations, the sample mean
of what is available divides by `tau`, not by `m`. Convention B would divide by
`m` regardless, shrinking the reused statistic toward zero on short cycles — a
different and biased estimator of the same quantity.

The choice was **not** made on which convention gives nicer numbers. For the
record, A gives *larger* `Gamma_m` and therefore a *larger* `m*`, i.e. it is the
less conservative choice for the "instability persists" reading; that did not
enter the decision.

### 2.5 Consequences carried into the protocol

1. `Gamma_m = (1/m) sum_{i<m} gamma_i` is **NOT** a theorem for the adopted
   convention and is removed from the Stage D theory. It is retained only as the
   definition of the *auxiliary* quantity `Gamma_m^B`, reported as a diagnostic.
2. `sum_{i>=0} gamma_i = E[T_tau^2] = ARL_0` **is** convention-independent and
   survives. (A 250-lag partial sum recovers 50.2% of `E[T^2]`, consistent with
   a long lag tail; the identity concerns the full sum.)
3. `Gamma_m -> E[T_tau^2/tau]` survives, as the limit of **A**.
4. The derivative correspondence `F'_{rho,m}(0) = rho(1 - Gamma_m)` **may not be
   assumed** from the `m = 1` result or from the closed form. It must be tested
   against finite differences of the actual induced map under convention A
   (Stage D task D2.3).
5. The headline pilot conclusion `m* ~ 72` (CUSUM) derives from
   `gamma_m_direct.csv`, i.e. convention A, and is **not** overturned: the audit
   run puts the crossing between `m = 50` (2.3668) and `m = 75` (1.9660).

### 2.6 Stop-condition assessment

The Stage D brief requires a halt if the ambiguity *materially changes previous
pilot conclusions*. It does not: the headline `m*` and the existence of a finite
stabilisation window both survive under the adopted convention. What changes is
that **one claimed theorem is falsified** and is removed rather than repaired.
Recorded here, in `FAILURE_DIAGNOSES.md`, and in the Stage D ledger.

---

## 3. Stage D correspondence table

| Concept | Mathematical definition | Implementation | Estimator | Simulation representation | Output artifact | Test |
|---|---|---|---|---|---|---|
| `tau` | `inf{t>=1 : detector_t >= threshold}`, inclusive, tested post-update | `stopped.simulate_stopped` | exact count | lockstep step counter | `arl` in every `*_stats` | `test_frozen_reduction` |
| terminal observation | `z_tau`, the alarm-causing innovation | ring buffer slot `pos-1` | — | `lags[:,0]` | `gamma_lag[0]` | `test_terminal_lag` |
| stopped window | last `w` innovations, `w = min(m,tau)` | `csum[.., min(w,L)-1]` | — | cumulative sum of reversed ring buffer | `gamma_m('A')` | `test_window_truncation` |
| `m` | nominal reuse window length | `m_grid` | — | — | — | `test_m_grid` |
| `w` | `min(m, tau)` — the realised window | `np.minimum(m, tau)` | — | — | — | `test_tau_less_than_m` |
| `Gamma` | `E[z_tau T_tau]` (`m=1`) | `gamma_m('A')[m=1]` | sample mean | — | `gamma_m_*.json` | `test_m1_reduces_to_stage_b` |
| `Gamma_m` | `E[(1/w) sum_{i<w} z_{tau-i} · T_tau]` — **convention A** | `StoppedStats.gamma_m('A')` | sample mean | — | `gamma_m_*.json` | `test_convention_A_vs_B` |
| `Gamma_m^B` (diagnostic) | `(1/m) sum_{i<m} gamma_i` | `gamma_m('B')` | sample mean | — | same file, separate column | `test_convention_B_equals_closed_form` |
| `gamma_i` | `E[z_{tau-i} 1{i<tau} T_tau]` | `StoppedStats.gamma_lag` | sample mean | reversed ring buffer | `gamma_lag_*.json` | `test_wald_sum_rule` |
| `rho` | reuse fraction in `e_{j+1} = rho·zbar + (1-rho)·fresh` | Stage A `frozen.rebaseline` | — | — | — | inherited Stage A tests |
| `rho_c` | `1/(Gamma_m - 1)` where `Gamma_m > 1` | `analysis.rho_c` | plug-in + delta method | — | `gamma_m_*.json` | `test_rho_c` |
| CUSUM reference state | `e = R_j - mu_j`; `z_t = X_t - R_j ~ N(-e,1)` | `simulate_stopped(e=...)` | — | innovation offset | — | inherited Stage A |
| SR reference state | same `e`; detector state is `(R^+,R^-)`, kept **separate** from the reference | `_sr_update` | — | log-domain softplus | `sr_*.json` | `test_sr_reference_separate` |
| `ARL0` | `E_0[tau]` at `e = 0` | `StoppedStats.arl` | sample mean | — | `calibration_*.json` | `test_arl0_calibration` |
| non-Gaussian score | `psi(x) = d/de log p_e(x)|_0` | `scores.py` | closed form per family | — | `nongaus_*.json` | `test_scores` |
| score-weighted stopped functional | `Gamma_psi = E[(1/w) sum psi(z_{tau-i}) · sum_t psi(z_t)]` | `stopped.simulate_stopped(score=...)` | sample mean | — | `nongaus_*.json` | `test_gaussian_score_reduces` |

---

## Addendum A1 — Stage A's minimum dwell vs Stage D's truncation

**Recorded 2026-08-22, after the protocol freeze (`925adecf…`) and BEFORE any
confirmatory D2 data existed.** This addendum changes no criterion, no
tolerance and no convention; it records a code-level fact discovered while
writing the D2 driver and states its consequence.

### The fact

Stage A's cycle simulator applies a **minimum dwell**
([conditional.py:133](level4/src/rebaseguard_level4/conditional.py:133)):

```python
if m > 1 and step < m:
    continue                      # minimum dwell: tau_m = inf{t >= m : ...}
```

so Stage A's stopping time is `tau_m = inf{t >= m : alarm}`, not the frozen
`tau = inf{t >= 1 : alarm}`. Under the dwell `tau_m >= m` always, hence
`w = min(m, tau_m) = m`, the reuse window always holds exactly `m` observations,
and Stage A's `mu_reuse = e + window/m` is unambiguous. **Conventions A and B
coincide under Stage A's rule** — the ambiguity my Phase 0 audit resolved simply
cannot arise there.

### Why Stage D does not inherit it

The Stage D blueprint considered and explicitly rejected the dwell
(`rebaseguard_staged_blueprint.md:142-144`):

> The truncation `w = min(m,tau)` is required: cycles can be shorter than `m`. A
> min-dwell `tau >= tau_m` would remove the truncation but changes the frozen
> stopping rule, so it is NOT adopted; the truncated convention is used
> throughout.

This is correct and Stage D follows it: suppressing alarms before step `m`
changes the law of `tau`, and therefore changes `ARL0` itself, as a function of
`m`. Stage D holds the frozen detector fixed and truncates the window instead.
Convention A, frozen in `STAGE_D_PROTOCOL.md`, is the truncated convention, and
Phase 0 independently confirmed it reproduces the pilot's `gamma_m_direct.csv`
at all 8 shared `m`.

### Consequences, stated so they cannot be blurred later

1. **Stage A and Stage D define different maps for `m > 1`.** Stage A's
   `F_{rho,m}` is the induced map of the *dwell-modified* detector; Stage D's is
   the induced map of the *frozen* detector with a truncated window. Numerical
   values at `m > 1` from the two stages are **not comparable**, and no Stage D
   claim may be supported by a Stage A `m > 1` number, or vice versa.
2. **At `m = 1` they agree exactly.** The dwell is guarded by `m > 1`, so the
   adversarial implementation-equivalence check (`m = 1` reduces to the Stage B
   `Gamma`) is unaffected and remains a valid cross-stage check.
3. **D2.3 must estimate the induced map from the Stage D recursion**, never from
   `conditional.py`. This is what the protocol already requires ("central finite
   difference of the **actual** induced map"); the addendum records *why* the
   requirement has teeth.
4. **The blueprint is internally inconsistent at exactly this point**, which
   corroborates the Phase 0 refutation. It asserts both
   `Gamma_m = (1/m) sum_{i<m} gamma_i` (§2.2) and
   `Gamma_m -> E[T_tau^2/tau] = 1.406` (§2.2(i)) under the *same* truncated
   convention. These cannot both hold: `(1/m) sum_{i<m} gamma_i -> 0` because
   `sum_i gamma_i = E[T_tau^2] = ARL0` is finite. Phase 0 measured the
   divergence at `m = 250` (152 SE) and it is pinned by
   `tests/test_stopped.py::test_convention_A_is_not_the_lag_average`.

### Status

`Gamma_m = (1/m) sum_i gamma_i` under convention A — **FAILED-TO-REPRODUCE**
(refuted, not merely unconfirmed).
`Gamma_m^B = (1/m) sum_i gamma_i` — true **by construction**, an algebraic
restatement of convention B, not an independent result.
`sum_i gamma_i = E[T_tau^2] = ARL0` — **REPRODUCED**.
