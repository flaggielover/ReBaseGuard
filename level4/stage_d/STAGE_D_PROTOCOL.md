# ReBaseGuard Level 4 — Stage D Protocol

**Frozen before any confirmatory production data.** SHA-256 recorded in
`results/protocol_hash.json` and re-verified by a test on every run.

Stage D asks whether the stopping-selected reference-feedback mechanism
established for the frozen Gaussian two-sided CUSUM **generalises structurally**
— to a different detector (D1), to stopped windows `m > 1` (D2), and to
non-Gaussian location families (D3) — and whether any resulting stability map
carries operational meaning (D4).

Nothing in Stage D may modify Level 1–3, Stage A, Stage B, Stage C or Stage C.1.

---

## 0. Inherited status (verified, not assumed)

510 tests pass (90 / 290 / 46 / 48 / 36). Stage B
`STAGE-B-CLOSED-RIGOROUS-PERIOD2`; Stage C `STAGE-C-PARTIAL` (C6 failed and
stays failed); Stage C.1 `STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY`.

---

## 1. FROZEN STOPPED-WINDOW CONVENTION

Resolved in `notes/CORRESPONDENCE_AUDIT.md` before this protocol was written.

```text
CONVENTION A (frozen for all Stage D production):
    w        = min(m, tau)
    zbar_m   = (1/w) * sum_{i=0}^{w-1} z_{tau-i}
    Gamma_m  = E[ zbar_m * T_tau ],      T_tau = sum_{t=1}^{tau} z_t
```

The blueprint's "exact closed form" `Gamma_m = (1/m) sum_{i<m} gamma_i` is
**false under convention A** and is **not** carried into Stage D. It is retained
only as a named diagnostic `Gamma_m^B` and reported alongside, never as theory.

Convention-independent and retained: `sum_{i>=0} gamma_i = E[T_tau^2] = ARL_0`.
Retained as the A-limit: `Gamma_m -> E[T_tau^2/tau]` (numerical, not proved).

---

## 2. Detectors and reuse rule

Both detectors are **repeated-cycle** monitors. The detector statistic state is
reset each cycle; the **reference state** `e = R_j - mu_j` is what the
alarm-selected observations update. Changing an SR headstart is not ReBaseGuard.

```text
innovation      z_t = X_t - R_j     (in control at reference error e: z_t ~ F(· + (-e)))
CUSUM (frozen)  S+_t = max(0, S+_{t-1} + z_t - k),  S-_t = max(0, S-_{t-1} - z_t - k)
                k = 1/2, h = 5, alarm max(S+,S-) >= h, inclusive, tested post-update
SR (two-chart)  R+_t = (1 + R+_{t-1}) exp(z_t - 1/2),  R-_t = (1 + R-_{t-1}) exp(-z_t - 1/2)
                alarm max(R+,R-) >= A, inclusive, post-update; log-domain softplus
reuse           e_{j+1} = rho * zbar_m + (1 - rho) * fresh,   fresh ⟂ stopping event
```

---

## 3. Hypotheses, estimands, decision criteria

### D1 — SR structural replication

| ID | Hypothesis | Criterion (fixed now) |
|---|---|---|
| D1.1 | SR can be ARL0-matched to CUSUM(h=5) | bisection on `log A` converges with `\|ARL0_SR/ARL0_CUSUM − 1\| <= 0.01` |
| D1.2 | `Gamma_SR > 2` at `m = 1` | **lower** 95% bound of `Gamma_SR` strictly `> 2` |
| D1.3 | the SR excess survives ARL0 matching | 95% CI for `Gamma_SR − Gamma_CUSUM` at matched ARL0 excludes 0 |
| D1.4 | SR induced map has a nonzero period-2 candidate | run **only if** D1.2 passes with `Gamma_SR > 4`; report candidate root of `H(e)=F(e)+e` with CI, or NO-CANDIDATE |

**Kill rule.** If D1.2 fails, D1 is recorded as failed, D1.4 is not run, and no
rigorous SR certificate branch is opened.

### D2 — stopped window `m > 1`

Grid (all retained, none dropped): `m ∈ {1, 2, 5, 10, 20, 50, 75, 100}` plus
refinement points added only to bracket the crossing, recorded as additions.

| ID | Hypothesis | Criterion |
|---|---|---|
| D2.1 | `gamma_i` decays with lag; the terminal observation dominates | report `gamma_0`, decay, CIs; no criterion — descriptive |
| D2.2 | `Gamma_m` crosses 2 at finite `m*` | a bracket `[m_lo, m_hi]` with `Gamma_{m_lo} − 2 > 0` and `Gamma_{m_hi} − 2 < 0`, both by more than 3 SE |
| D2.3 | `F'_{rho,m}(0) = rho(1 − Gamma_m)` | central finite difference of the **actual** induced map at `rho=1`; agreement within 3 combined SE. **Not assumed from `m=1` or from the closed form.** |
| D2.4 | `Gamma_m -> Gamma_inf < 2` | numerical only; report `E[T^2/tau]` with CI. **Not a theorem.** |
| D2.5 | the `Gamma_m` transition predicts an operational change | measure in-control cycle ARL, reference MSE, alarm-direction ACF and `R_Delta` at `m` on both sides of `m*`; if none changes materially, the boundary is reported as **mathematical, not operational** |

### D3 — non-Gaussian

Families, all pre-specified: Gaussian control; Student-t `nu ∈ {10, 5, 3}`
standardised to unit variance; contaminated Gaussian
`(1-eps) N(0,1) + eps N(0, 3^2)`, `eps ∈ {0.05, 0.10}`.

Score `psi(x) = d/de log p_e(x)|_{e=0}` — the **correct** score for each family:

```text
Gaussian     psi(x) = x
Student-t_nu psi(x) = (nu + 1) x / (nu + x^2)      (unit-variance rescaled)
contaminated psi(x) = -p'(x)/p(x) for the mixture density
Gamma_psi = E[ (1/w) sum_{i<w} psi(z_{tau-i}) · sum_{t<=tau} psi(z_t) ]
```

| ID | Criterion |
|---|---|
| D3.1 | regularity assumptions written down and labelled **before** simulation; unproved ones marked |
| D3.2 | per family, ARL0-matched, **lower** 95% bound of `Gamma_psi` compared with 2 |
| D3.3 | naive Gaussian-form `Gamma_T` reported as a **diagnostic only**, never as evidence |

### D4 — stability map

Run only if D1 and D2 both survive. If the map is a monotone transformation of
`Gamma_m` with no additional operational content, it goes to supplementary
material, not to a headline claim.

---

## 4. Decision rule (fixed now, applied in this order)

1. If any adversarial or reproducibility check fails and is not diagnosed →
   **`STAGE-D-INCONCLUSIVE`**.
2. Else if D1.2 fails → **`STAGE-D-SR-FAILED`**.
3. Else if D1 and D2 pass but at least one D3 family fails →
   **`STAGE-D-NONGAUSSIAN-PARTIAL`**.
4. Else if D1, D2 and D3 all pass → **`STAGE-D-CLOSED-GENERALIZED`**.
5. Else → **`STAGE-D-PARTIAL`**.

No other status may be invented.

---

## 5. Seeds

Prior seeds audited across the whole repository:
`{1234, 1729, 2024, 2026, 4242, 5150, 8080, 31337, 90210, 20260820, 20260821,
20260822, 20260901, 20260902, 20260931}`.

| Purpose | Root entropy | Confirmatory? |
|---|---|---|
| Phase 0 audit (already run) | `[20260822, 7, k]` | **NO** — reuses a prior seed; audit only, excluded from all Stage D results |
| smoke / sizing | `[20261031, ...]` | NO |
| **confirmatory** | `[20261001, ...]` | **YES** |
| adversarial independent rerun | `[20261002, ...]` | NO (replication) |

`20261001`, `20261002`, `20261031` appear nowhere in prior work. Tests assert
disjointness and that the generated streams differ.

---

## 6. Monte Carlo precision and estimators

* **Statistical unit: the independent cycle** for `Gamma`-type estimands (cycles
  are i.i.d. by construction, unlike the multi-cycle chain), and the
  **replicate** for any multi-cycle quantity in D2.5.
* Primary `Gamma_m` / `Gamma_psi`: `N = 2,000,000` cycles (D3: `1,000,000`).
* Induced map `F(e)`: `500,000` cycles per grid point.
* Intervals: normal CI on the sample mean using the sample variance, plus a
  batch bootstrap (`n_batches = 20`) as a cross-check; the two must agree.
* ARL0 matching: bisection on `log A` (SR) / `h` (CUSUM), 30 iterations or
  tolerance `1e-3` in `log`-threshold, calibration run on its own seed and its
  own `N = 400,000`. Calibration uncertainty is propagated and reported.
  **The threshold is never adjusted after seeing any `Gamma`.**
* `m*` interpolation: linear in `log m` between the bracketing grid points;
  uncertainty by propagating the SE at both bracket ends. The bracket itself is
  reported and is the primary object; the interpolated point is secondary.
* `rho_c = 1/(Gamma_m − 1)`, defined only where the lower CI bound of `Gamma_m`
  exceeds 1; delta-method SE.

---

## 7. Adversarial suite (all reported, pass or fail)

independent seed family; CRN on/off; estimator variant (convention A vs B, batch
bootstrap vs normal CI); finite-difference step variation; threshold
recalibration uncertainty; interpolation-method variation; direct vs decomposed
`Gamma_m`; `tau < m` edge cases; larger Monte Carlo subset; implementation
equivalence (`m=1` reduces to the Stage B `Gamma`); outcome-blind code guard;
protocol-hash verification.

Any failure is diagnosed in `notes/FAILURE_DIAGNOSES.md` and left visible.
Tolerances are never widened after the fact.

---

## 8. Forbidden

* converting numerical evidence into a theorem;
* calling any Monte Carlo result "certified";
* "detector-independent", "distribution-free", "universal", "robust in general",
  "first stability boundary", "repeated SR is novel";
* re-tuning a threshold, grid or criterion after seeing a `Gamma`;
* dropping a grid point, family or shift after inspection;
* claiming a rigorous asymptotic result from numerical extrapolation.

---

## 9. Kill / stop conditions

Stop and report rather than continue if: frozen artifacts change; baseline tests
fail for non-Stage-D reasons; confirmatory seeds overlap prior work; an estimator
is found mathematically inconsistent with the protocol; or production contradicts
the pilot in a way that requires protocol redesign.
