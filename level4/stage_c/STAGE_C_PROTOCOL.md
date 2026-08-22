# ReBaseGuard Level 4 — Stage C Protocol

**Frozen before the campaign.** Everything below — endpoints, grids, sample
sizes, tolerances, the policy definition, and the success criteria — was
written and committed before any Stage C production run. Deviations, if any,
are recorded in `notes/PROTOCOL_DEVIATIONS.md` with the reason and the date.

---

## 1. Scientific question

Not "does reuse cause instability?" — Stage A and Stage B answered that. The
Stage C question is:

> Can reuse be controlled using the **local stability boundary** so that
> alarm-triggering data is still reused, while avoiding recursive reference
> instability and preserving monitoring performance?

---

## 2. Frozen inputs (not re-derived, not modified)

| Input | Value | Status |
|---|---|---|
| detector | symmetric two-sided Gaussian CUSUM, `k=1/2`, `h=5`, `m=1`, inclusive post-update alarm, shared innovation | FROZEN |
| `F_rho = rho * F_1` | exact | FROZEN-PROVED (Level 2C) |
| `F_1'(0) = 1 - Gamma` | exact | FROZEN-PROVED (Level 2C) |
| `Gamma` enclosure | `[3.9243482, 27.8493821]` | FROZEN-CERTIFIED (Arb) |
| `Gamma` point estimate | `15.885729 ± 0.020165` | NEW-NUMERICAL (Stage A Gate 4.2) |
| `rho_c = 1/(Gamma-1)` | point `0.067178`; certified enclosure `[0.037245, 0.341957]` | derived |
| Stage B period-2 orbit at `rho=1` | `e* ∈ [1.028724, 1.044724]`, `lambda_2 ∈ [0.1081, 0.8325]` | RIGOROUS-CERTIFIED, **deterministic map only** |

**Stage B's theorem concerns the deterministic conditional-mean map `F_1`, not
the noisy recursion `E_{j+1} = F_1(E_j) + noise`.** Stage C may not upgrade it.

---

## 3. The ReBaseGuard policy (defined here, before evaluation)

Safety margin `delta ∈ (0,1)`; require `|F'_rho(0)| <= 1 - delta`. Since
`|F'_rho(0)| = rho (Gamma - 1)`,

```text
rho_safe(delta) = clip( (1 - delta) / (Gamma - 1), 0, 1 )
```

Two variants, kept strictly apart:

| Variant | `Gamma` used | Guarantee | Evidence class |
|---|---|---|---|
| **POINT** | `Gamma_hat = 15.885729` | holds *if* the Monte Carlo estimate is exact | heuristic, **NOT certified** |
| **CONSERVATIVE** | `Gamma_upper = 27.8493821` | holds for the **true** `Gamma`, since `rho(Gamma-1)` increases in `Gamma` | **certified**, for LOCAL LINEAR stability of the DETERMINISTIC map only |

**Headline configuration, fixed now:** `delta = 0.2`, variant `CONSERVATIVE`.
`delta = 0.2` is chosen as a conventional 20% margin, not because of any
observed performance. Sensitivity is reported over
`delta ∈ {0.05, 0.1, 0.2, 0.5}`.

Resulting reuse fractions (computed before the campaign):

| `delta` | POINT `rho` | CONSERVATIVE `rho` |
|---|---|---|
| 0.05 | 0.063820 | 0.035383 |
| 0.10 | 0.060461 | 0.033520 |
| **0.20** | **0.053743** | **0.029796** |
| 0.50 | 0.033589 | 0.018622 |

The policy uses only `Gamma` and `delta`. It does **not** use the Stage B root
`e*`, any Stage C outcome, or any tuning. A test enforces this.

---

## 4. Baselines

| # | Baseline | Definition |
|---|---|---|
| B1 | fresh-only | `rho = 0` |
| B2 | full reuse | `rho = 1` |
| B3 | fixed partial reuse | every `rho` on the dense grid |
| B4 | **ReBaseGuard** | `rho = rho_safe(0.2, CONSERVATIVE) = 0.029796`; POINT variant reported alongside |
| B5 | **ORACLE (post-hoc, reference only)** | the grid `rho` minimising stationary reference MSE, chosen *after* seeing results |

B5 is a performance yardstick. It is **not** a proposed method and must not
influence B4. A test enforces that the policy module cannot see campaign output.

Pre-allocated thinning and sample splitting are **not** implemented: both change
the frozen re-baselining rule `e_{j+1} = rho*mu_reuse + (1-rho)*mu_fresh`, and
Stage C does not modify frozen semantics. Recorded as `OPEN`.

---

## 5. Dense `rho` grid

Mandated grid (all points retained, none deleted):

```text
0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.065, 0.067, 0.07, 0.075, 0.08,
0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75, 1.00
```

Added points, recorded as additions:

```text
0.029796   (ReBaseGuard CONSERVATIVE, delta = 0.2)
0.053743   (ReBaseGuard POINT,        delta = 0.2)
```

Total 23 cells. Any later adaptive refinement is appended, never substituted.

---

## 6. Experimental design

* **Simulator:** the frozen Stage A `rebaseguard_level4.multicycle` for all
  in-control work — no new code in the critical path. Detection experiments use
  a Stage C simulator that must reproduce Stage A bit-for-bit when the shift is
  zero (enforced by test).
* **Replication:** 100 independent replicates, 10^4 retained cycles per
  replicate, burn-in 1000 cycles. Master seed `20260821`.
* **Statistical unit:** the **replicate**. Cycles within a replicate are a
  serially dependent Markov chain. All intervals are 95% percentile bootstrap
  over replicates; never over cycles.
* **CRN:** the same master seed across `rho`, so replicate `r` shares its
  driving stream across cells. Comparisons *between* `rho` therefore use
  **paired** replicate differences; naive independent-point standard errors are
  not computed for such comparisons.

---

## 7. Primary endpoints (small and fixed)

| ID | Endpoint | Definition |
|---|---|---|
| **A** | stationary reference MSE | `E_pi[e^2]` over retained cycles, per replicate then bootstrapped |
| **B** | in-control cycle ARL | mean `tau` over retained cycles |
| **C** | detection delay | `tau` of the first cycle after a mean shift applied at a cycle boundary |
| **D** | sample reuse efficiency | see §10 |

Secondary diagnostics (reported, never promoted to headline): reference
mean/bias, reference SD, alarm-direction alternation, ACF at lags 1–3,
quantiles of the reference state, central vs off-centre stationary mass,
cycle-length distribution, false-alarm hazard conditional on `e`, effective
fraction of alarm data retained.

---

## 8. ARL mechanism

Estimate `A(e) = E[tau | E_j = e]` with the frozen Stage A conditional
simulator, on a symmetric grid covering essentially all stationary mass
observed in Stage A (`sd(e) <= 1.38` at `rho = 1`, so the grid spans `|e| <= 5`).

Pre-specified tests on `A`:
* **symmetry** `A(-e) = A(e)` — expected from the proved arm-swap involution;
* local behaviour near 0;
* monotonicity in `|e|` **where supported** — global monotonicity is *not*
  assumed and non-monotone regions are reported if found.

**Decomposition check.** With `pi_rho` the stationary law of the reference error
*at the start of a cycle* (`e_prev`),

```text
ARL_decomp(rho) = E_pi[ A(e) ]
```

evaluated by averaging an interpolated `A` over the observed `e_prev` sample
(no binning of `pi`). Compared against the direct long-run `mean(tau)`.

**Pre-specified tolerance (C7):** the two agree if

```text
| ARL_direct - ARL_decomp |  <=  3 * sigma_combined
sigma_combined^2 = SE_direct^2 + SE_decomp^2 + bias_interp^2
```

where `SE_direct` is the replicate bootstrap SE, `SE_decomp` propagates the
Monte Carlo error of `A` at the grid points and of the `e_prev` sample, and
`bias_interp` is estimated by halving the `e`-grid. If the check fails, the
mechanism claim is **stopped and diagnosed**, not widened.

---

## 9. Detection performance

Shifts `Delta ∈ {0.25, 0.5, 1.0, 1.5}`.

Protocol: run in control through burn-in; at a cycle boundary the true mean
jumps to `Delta`. Because `e = R - mu`, the reference error instantaneously
becomes `e - Delta` and monitoring continues with the identical recursion.
**Detection delay** is the stopping time `tau` of that first post-change cycle,
measured in observations. Recovery is the number of subsequent cycles until
`|e|` returns inside the in-control stationary 90% band for that `rho`.

Matched streams across `rho`; paired replicate differences for comparisons.

**A method is not successful merely by raising in-control ARL through
insensitivity.** C6 below makes that explicit.

---

## 10. Sample reuse efficiency

Defined to match the implemented protocol exactly:

| ID | Quantity | Definition |
|---|---|---|
| D1 | retained alarm-data weight | `rho` — the weight the next reference places on the alarm-triggering observation |
| D2 | fresh observations per cycle | measured count: `1` when `rho < 1`, `0` when `rho = 1` |
| D3 | fresh observations per monitored observation | `D2 / ARL` |

**Stated limitation, pre-registered:** at `m = 1` the fresh-sample *count* (D2)
is a step function of `rho`, because the protocol always draws one fresh variate
and weights it by `1-rho`. The continuous efficiency story therefore lives in
the weight D1 and in the amortised D3, not in D2. No percentage will be quoted
that is not one of D1–D3.

---

## 11. Success / failure criteria

| ID | Criterion | Pre-specified threshold |
|---|---|---|
| C1 | policy mathematically well-defined | closed form, deterministic, unit-tested |
| C2 | stability rule follows from frozen theory | derived from `F'_rho(0) = rho(1-Gamma)` alone |
| C3 | full reuse has substantially worse reference stability than the stable policy | `MSE(rho=1) > 1.5 x MSE(ReBaseGuard)`, paired bootstrap CI excludes 1.5x |
| C4 | ReBaseGuard preserves nonzero alarm data | `rho > 0` strictly, and D1 > 0 |
| C5 | ReBaseGuard improves stability over full reuse | paired 95% CI for `MSE(rho=1) - MSE(RBG)` strictly positive |
| C6 | improvement is not bought by destroying detection | for every `Delta`, paired 95% CI for `delay(RBG) - delay(rho=1)` must lie below `+0.25 x delay(rho=1)`; i.e. RBG may not be more than 25% slower |
| C7 | direct vs decomposition ARL agree | §8 tolerance |
| C8 | reproduces under independent seeds | headline endpoints agree within paired 95% CI across two disjoint seed families |
| C9 | no frozen Stage A/B claim regresses | all 426 existing tests green; Stage B certificate byte-identical |
| C10 | negative/null findings retained | every grid point and every failed check appears in the ledger |

**Decision rule, fixed now:**

* `STAGE-C-CLOSED-METHOD` — C1–C10 all pass.
* `STAGE-C-PARTIAL` — C1, C2, C9, C10 pass but at least one of C3–C8 fails.
* `STAGE-C-FAILED` — C1, C2, C9 or C10 fails.

No fourth status.

---

## 12. Pre-registered question that is *reported*, not *gated*

Stage A already shows, at `m = 1`, that `rho = 0.25` has lower reference
dispersion (`sd = 0.845`) and longer in-control ARL (`95.5`) than the fresh
baseline (`1.000`, `82.9`). So the local stability boundary `rho_c ≈ 0.067` is
plainly **not** the performance boundary.

It is therefore likely that a fixed `rho` well above `rho_c` will **dominate**
the ReBaseGuard policy on reference MSE and ARL. That possibility is registered
here in advance. If it occurs it will be reported as a **headline limitation**,
not buried: passing C1–C10 does **not** mean the policy is performance-optimal.
It is deliberately not a gating criterion, because the policy's claim is
*certified local stability*, not optimality — but a reader is entitled to know
the price of that certification.

---

## 13. Adversarial checks (all reported, pass or fail)

independent seeds; CRN on/off; doubled and halved run length; burn-in
sensitivity; stationary-window sensitivity; `e`-grid refinement for `A(e)`;
`rho`-grid refinement near `rho_c`; direct vs decomposition ARL; POINT vs
CONSERVATIVE policy; fresh-baseline sanity (`sd = 1/sqrt(m)`, alternation 0.5,
ACF 0); full-reuse reproduction of Stage A; and an explicit test that no Stage B
root value can reach the policy module.

Tolerances are not widened after the fact. Any widening is recorded in
`notes/PROTOCOL_DEVIATIONS.md` with its reason.

---

## 14. Reproducibility

Deterministic seed manifests, config snapshots, environment metadata, campaign
IDs, output hashes, per-cell checkpointing so an interrupted campaign resumes,
and

```bash
bash level4/stage_c/reproduce.sh
```

which rebuilds every Stage C table and figure from persisted campaign data, or
performs a documented full rerun.
