# Level-4 Priority 4 — closure report

## 1. Verdict

```text
PARTIAL
```

The verdict is derived mechanically in `derive_closure.py` from artifacts on
disk, not asserted here.  `results/closure_decision.json` is authoritative; if
it disagrees with this document, it wins.

**What is and is not established.**  Independent adjudication accepted the
main derivative theorem after narrowing G3's unproved iff wording.  **Three**
preregistered gates remain failed —
`all_outside_assumption_cells_demonstrate_failure`,
`all_theorem_supported_cells_pass`, and
`gaussian_consistency_with_closed_core` — for the reasons below.  The
repository-wide gate now passes.  No frozen numerical gate or generated cell
was edited after the data were seen.

1. **`t1p5` fails the 3% *accuracy* gate while remaining statistically
   consistent.**  Nine of the ten non-passing theorem-supported cells are the
   single family `t1p5` — Student-`t` with `nu = 1.5`, which has no variance.
   Route B's own relative standard error on those cells runs from 1.5% to
   **23.3%**.  Requiring 3% agreement from an estimator with 23% precision is a
   defect in the gate, not evidence against the identity: those cells have
   `|z|` between **0.35 and 1.49**, i.e. the two routes agree as well as their
   errors permit, and Route Q reproduces the identity for `t1p5` at every
   window length to nine significant figures with no sampling error at all.
2. **Exactly one original cell is statistically inconsistent**: `sr@520.886`,
   `skewnormal4`, `m = 2`, at `|z| = 4.29` and 2.57% relative.  It is not
   isolated noise — the whole skew-normal SR column is one-signed at 2.0-2.6%
   with `|z|` from 3.4 to 4.3 — but it is confined: the same family under CUSUM
   agrees to 0.05-0.53%, and every symmetric family under SR agrees to
   0.03-0.41%.  The most likely cause is a residual finite-difference bias that
   the `h^2` Richardson correction does not remove when the map is not odd; for
   a symmetric family the `+h` and `-h` runs are mirror images and much of the
   error cancels, and for an asymmetric family it does not.  Independent
   adjudication tested rather than assumed that explanation.  A `.025/.0125`
   replay moved the m=2 estimate to `6.5170 +/- 0.0391`; a
   `.0125/.00625` replay moved it to `6.4342 +/- 0.0785`, only `0.56`
   combined standard errors from the original Route A value.  A fresh 1.6M
   path Route-A replay gave `6.4549 +/- 0.0452`.  The anomaly is therefore
   resolved as finite-step bias plus Monte Carlo scatter.  The original cell
   remains frozen and its literal gate remains failed.
3. **The Cauchy cells are recorded `COUNTEREXAMPLE-NOT-DEMONSTRATED`.**  The
   preregistered counterexample gate asks for a large *and statistically sharp*
   disagreement.  That is exactly what the moving-support failure produces —
   uniform reaches 100% relative at 468-517 standard errors, confirmed at both
   frozen detectors and every `m`.  Cauchy fails differently: nothing converges.
   `E_0[A_1] = 10.0 ± 14.6` is not a number, which is precisely the pathology
   `PROOF.md` §10 proves (`E|A_1| = infinity`).  The gate was written to detect
   a deterministic defect and does not register a non-convergence, so all
   sixteen Cauchy cells are honestly recorded as not meeting it.
4. **The Gaussian consistency gate uses a mis-specified statistic.**  As coded
   it divides by Priority 4's own standard error alone, treating the closed
   Monte Carlo value as exact — the wrong test for comparing two Monte Carlo
   estimates.  It was **left unchanged** after the data were seen so that no
   gate outcome could be improved by editing it, and the correctly specified
   combined-error statistic is computed and reported beside it.  Under the
   correct statistic the four CUSUM cells sit at **0.33-1.13** combined standard
   errors and the four SR cells at **2.41-2.98**, one-signed, with Priority 4's
   independent estimate about **1.0-1.1% below** the closed Priority-2 SR value.
   Priority 4's estimate uses 3.2M paths against Priority 2's 240k.  Independent
   adjudication reran the frozen P2 score implementation on 1.6M fresh paths;
   all four windows agree with P4 within `1.26-1.49` combined standard errors.
   The old P2 vector was a correlated high Monte Carlo realization, not an
   implementation mismatch.  The frozen value and literal gate remain
   unchanged.
5. **Repository-wide verification now passes.**  The completed artifact is
   `results/verification.json`.  All named required suites pass, controlled
   locale/PATH and freeze-scoped experiments behave as predicted, and the
   grandfathered Level-4/archive diagnostics are unchanged.  See §9.2.

The disciplined reading is therefore: **the generalization is established as
mathematics after one G3 prose narrowing, both named discrepancies are
reconciled, and repository verification passes; but three frozen numerical
gates remain literally false, so the mechanically consistent verdict is still
PARTIAL.**

## 2. The theorem actually established

For observations `X_t = mu + eps_t` from a regular one-dimensional **location
family** with density `f`, monitored by a fixed residual-path stopping rule
`tau`, re-baselined by

```text
e_{j+1} = rho (e + A_m) + (1 - rho)(U - mu),
A_m = (1/min(m,tau)) sum_{r=0}^{min(m,tau)-1} Z_{tau-r},
```

the conditional-mean reference map `F_{rho,m}(e) = rho(e + E_e[A_m])` satisfies,
under hypotheses (A1)-(A7) of `THEOREM.md` §2,

```text
F'_{rho,m}(0) = rho (1 - Gamma_{D,m,f}),
Gamma_{D,m,f} = E_0[ A_m * sum_{t<=tau} psi(Z_t) ],     psi = -f'/f.
```

Together with a fixed point at the origin (Theorem G4) this gives the
Priority-3 classification verbatim, with `rho_c = 1/|1 - Gamma_{D,m,f}|`.

Four companion results:

* **G1'** — the same identity at any base point `e0`, with the score evaluated
  at the unshifted innovations.  This is what an asymmetric family needs.
* **G2** — for a *deterministic* stopping rule the map is identically zero and
  the gain is exactly `1`, for every regular location family.  Hence
  `Gamma - 1` is exactly the stopping-selection effect.
* **G3** — the random-denominator decomposition holds for any score, and its
  short-cycle correction has the sign of `T_tau S_tau`.  The centred Gaussian
  score makes this a square; explicit non-Gaussian witnesses are negative.
  No unproved iff characterisation is claimed.
* **G4** — symmetry is used for the fixed point and for nothing else.

## 3. Exact assumptions

Verbatim from `THEOREM.md` §2, in the order the proof consumes them.

| | assumption |
|---|---|
| A1 | for every `n`, `{tau = n} ∈ F_n`, and `A_m`, `T_tau` are Borel functions of the first `n` residuals; the detector recursion, threshold, inclusivity and tie rule do not depend on `e` |
| A2 | `tau < infinity` a.s. under every `Q_e` in a neighbourhood |
| A3 | `f > 0` a.e. on a translation-invariant set, `f` locally absolutely continuous, `psi = -f'/f` defined a.e. |
| A4 | `e -> L_tau(e)` differentiable **at zero** a.s., with derivative `-sum psi(Z_t)` |
| A5 | `A_m` and `A_m sum psi(Z_t)` integrable under `Q_0` |
| A6 | `|A_m| |L_tau(e) - L_tau(e')| <= G |e - e'|` on `[-d,d]` with `G` integrable |
| A7 | the fresh reference is independent and unbiased for `mu`, entering affinely with coefficient `1 - rho` |

Discharged, not assumed, by `PROOF.md` §8:

* **L1** geometric stopping tail from a one-step forcing event, for the frozen
  CUSUM (`c_D = h + k`) and the frozen SR (`c_D = 1/2 + log A`), requiring the
  innovation law to reach `c_D`;
* **L2** `E[|A_m|^r] <= E|Z|^r E[tau]`, from `{tau >= n} ∈ F_{n-1}`;
* **L3** bounded score plus a `1 + eta` innovation moment ⟹ (A5), (A6);
* **L4** at-most-linear score plus an exponential innovation moment ⟹ (A5), (A6);
* **L5** (A4) from differentiability of `log f` at the finitely many residuals.

**No finite variance is required.**  L3 needs only `E|eps|^{1+eta} < infinity`.

## 4. What generalized beyond Gaussian

| | |
|---|---|
| the derivative identity | with `T_tau` replaced by `sum psi(Z_t)` |
| every window length `m >= 1` | including the random denominator and the `tau < m` branch |
| both frozen detectors | CUSUM and SR, with their tails discharged by the same lemma |
| exact `rho` scaling | uses no property of `f`, the detector, or `m` |
| the random-denominator **identity** | `A_m S = B_m S + 1{tau<m}(1/tau-1/m) T S` |
| the Priority-3 classification | `rho_c = 1/|1-Gamma|`, unchanged |
| the differentiation hypothesis | *weakened* to a Lipschitz difference quotient, which admits Laplace |
| neutrality of non-selective stopping | new, and family free |

## 5. What did NOT generalize

Three things, each proved rather than conjectured.

1. **The sign of the short-window correction.**  Priority 1's `Q_m >= 0` is
   Gaussian.  In general the correction has the sign of `T_tau S_tau`, and both
   the pathwise correction and its expectation can be strictly negative — the
   Arb witness certifies `E[Q_5] = -1/10` exactly.  Consequently the truncated
   window can make the gain *smaller* than the fixed denominator would, the
   opposite of the Gaussian reading.
2. **The fixed point at the origin.**  Without an even density and a
   reflection-equivariant detector, `E_0[A_m] != 0` and the origin is not a
   fixed point, so the Priority-3 stability map has nothing to classify there.
   Theorem G1' gives the right object; finding the fixed point is a separate
   problem.
3. **The model class itself, in two directions.**  Moving support breaks local
   absolute continuity and the identity is then *false* (uniform, exact defect
   `2`); a missing first moment breaks the map before any derivative is taken
   (Cauchy).  The dividing line is the first moment, not the second.

## 6. Numerical correspondence results

Four routes, kept apart.  `NUMERICAL_CORRESPONDENCE.md` has every cell; this
is the summary.

### 6.1 Route Q — deterministic quadrature, no sampling error

For the memoryless detector `tau = inf{t : |Z_t| >= c}` with `c = 2.0`, both
sides of Theorem G1 were evaluated by adaptive quadrature for six families
and four window lengths, including the random denominator and the `tau < m`
branch.  All 24 cells agree, worst relative discrepancy
**4.3e-09**.

This is the campaign's strongest evidence that the *identity* is correct: it
has no Monte Carlo error and it does not use the simulator at all.  It is not
evidence about the frozen operating point.

The uniform negative control behaves as `PROOF.md` §9 proves it must: the
score side is exactly `0.0` while the exact map slope is
`-2.366025`.

### 6.2 Route N — neutrality control

All 72 cells of the deterministic-stopping control return gain one
(worst `|z| = 2.64` against a threshold of
4.0).  Corollary G2 predicts exactly this for every regular
location family, so a sign, normalisation or window error in any family would
break it.

### 6.3 Routes A and B under the frozen recursions

96 theorem-supported cells and 32 outside-assumption cells across two
operating-point layers, two detectors, eight families and four window
lengths.  Frozen gate: 3% relative (inherited from Track 3) and `|z| <= 4`.

* theorem-supported cells passing: **86 / 96**
* worst relative discrepancy: **25.637%**
* worst `|z|`: **4.29**
* outside-assumption cells demonstrating the predicted failure: **16 / 32**

**Cells that did not pass:**

| layer | detector | family | m | Route A | Route B | relative | \|z\| |
|---|---|---|---|---|---|---|---|
| reduced | sr@20 | t1p5 | 1 | 2.6818 ± 0.0475 | 2.8311 ± 0.1053 | 5.276% | 1.29 |
| reduced | sr@20 | t1p5 | 2 | 1.9488 ± 0.0238 | 2.0274 ± 0.0533 | 3.874% | 1.35 |
| reduced | sr@20 | t1p5 | 3 | 1.6531 ± 0.0229 | 1.7157 ± 0.0358 | 3.645% | 1.47 |
| reduced | sr@20 | t1p5 | 5 | 1.4344 ± 0.0230 | 1.4807 ± 0.0226 | 3.132% | 1.44 |
| frozen | cusum@5 | t1p5 | 1 | 3.4825 ± 0.1403 | 3.5959 ± 0.2914 | 3.155% | 0.35 |
| frozen | sr@520.886 | t1p5 | 1 | 4.1276 ± 0.0956 | 3.0694 ± 0.7160 | 25.637% | 1.47 |
| frozen | sr@520.886 | t1p5 | 2 | 2.8573 ± 0.0477 | 2.3225 ± 0.3567 | 18.717% | 1.49 |
| frozen | sr@520.886 | t1p5 | 3 | 2.3668 ± 0.0321 | 2.0187 ± 0.2390 | 14.706% | 1.44 |
| frozen | sr@520.886 | t1p5 | 5 | 1.9109 ± 0.0204 | 1.6998 ± 0.1438 | 11.044% | 1.45 |
| frozen | sr@520.886 | skewnormal4 | 2 | 6.3875 ± 0.0284 | 6.5561 ± 0.0270 | 2.571% | 4.29 |

### 6.4 The frozen operating points, `m = 1` and `m = 5`

| detector | family | ARL | m | `Gamma` (Route A) | Route B | rel | \|z\| | `E_0[A_1]` |
|---|---|---|---|---|---|---|---|---|
| cusum@5 | gaussian | 465 | 1 | 15.8773 ± 0.0168 | 15.8572 ± 0.0466 | 0.13% | 0.41 | -0.0015 |
| cusum@5 | gaussian | 465 | 5 | 10.1842 ± 0.0121 | 10.1814 ± 0.0260 | 0.03% | 0.10 | -0.0011 |
| cusum@5 | laplace | 276 | 1 | 13.0220 ± 0.0501 | 12.9869 ± 0.0472 | 0.27% | 0.51 | +0.0010 |
| cusum@5 | laplace | 276 | 5 | 6.3917 ± 0.0193 | 6.3724 ± 0.0184 | 0.30% | 0.72 | +0.0004 |
| cusum@5 | logistic | 359 | 1 | 14.5743 ± 0.0217 | 14.5928 ± 0.0508 | 0.13% | 0.33 | +0.0005 |
| cusum@5 | logistic | 359 | 5 | 8.1379 ± 0.0087 | 8.1297 ± 0.0239 | 0.10% | 0.32 | +0.0004 |
| cusum@5 | skewnormal4 | 365 | 1 | 5.4213 ± 0.0413 | 5.4037 ± 0.0275 | 0.33% | 0.36 | +2.1729 |
| cusum@5 | skewnormal4 | 365 | 5 | 3.4946 ± 0.0223 | 3.4930 ± 0.0140 | 0.05% | 0.06 | +1.1188 |
| cusum@5 | t1p5 | 12 | 1 | 3.4825 ± 0.1403 | 3.5959 ± 0.2914 | 3.16% | 0.35 | +0.0116 |
| cusum@5 | t1p5 | 12 | 5 | 1.7751 ± 0.0291 | 1.8049 ± 0.0600 | 1.65% | 0.45 | -0.0138 |
| cusum@5 | t3 | 237 | 1 | 8.0054 ± 0.0712 | 8.0175 ± 0.0625 | 0.15% | 0.13 | +0.0099 |
| cusum@5 | t3 | 237 | 5 | 3.5995 ± 0.0147 | 3.6203 ± 0.0159 | 0.58% | 0.96 | +0.0020 |
| sr@520.886 | gaussian | 465 | 1 | 17.2589 ± 0.0203 | 17.2385 ± 0.0341 | 0.12% | 0.51 | -0.0016 |
| sr@520.886 | gaussian | 465 | 5 | 10.9230 ± 0.0097 | 10.9118 ± 0.0221 | 0.10% | 0.46 | -0.0007 |
| sr@520.886 | laplace | 297 | 1 | 16.0790 ± 0.0493 | 16.0747 ± 0.0601 | 0.03% | 0.06 | -0.0016 |
| sr@520.886 | laplace | 297 | 5 | 7.6115 ± 0.0178 | 7.6258 ± 0.0201 | 0.19% | 0.53 | -0.0013 |
| sr@520.886 | logistic | 375 | 1 | 16.8196 ± 0.0193 | 16.8879 ± 0.0543 | 0.40% | 1.19 | +0.0021 |
| sr@520.886 | logistic | 375 | 5 | 9.2044 ± 0.0083 | 9.2333 ± 0.0261 | 0.31% | 1.05 | +0.0007 |
| sr@520.886 | skewnormal4 | 396 | 1 | 7.9390 ± 0.0387 | 8.1256 ± 0.0366 | 2.30% | 3.50 | +2.0335 |
| sr@520.886 | skewnormal4 | 396 | 5 | 4.8861 ± 0.0209 | 4.9869 ± 0.0211 | 2.02% | 3.39 | +1.0587 |
| sr@520.886 | t1p5 | 13 | 1 | 4.1276 ± 0.0956 | 3.0694 ± 0.7160 | 25.64% | 1.47 | -0.0280 |
| sr@520.886 | t1p5 | 13 | 5 | 1.9109 ± 0.0204 | 1.6998 ± 0.1438 | 11.04% | 1.45 | -0.0222 |
| sr@520.886 | t3 | 257 | 1 | 11.2480 ± 0.0973 | 11.0345 ± 0.0654 | 1.90% | 1.82 | +0.0083 |
| sr@520.886 | t3 | 257 | 5 | 4.5623 ± 0.0230 | 4.5307 ± 0.0194 | 0.69% | 1.05 | +0.0023 |

### 6.5 Consistency with the closed Gaussian gains

Priority 4 re-implements both frozen detectors from scratch.  Agreement with
the closed Priority-1 and Priority-2 Monte Carlo values is the main
cross-implementation control.  It is a check, not a re-derivation: no frozen
number is replaced.

| detector | m | closed P1/P2 | P4 independent | \|z\| |
|---|---|---|---|---|
| cusum@5 | 1 | 15.9165 | 15.8773 ± 0.0168 | 2.33 |
| cusum@5 | 2 | 13.2648 | 13.2475 ± 0.0151 | 1.15 |
| cusum@5 | 3 | 11.9571 | 11.9147 ± 0.0137 | 3.08 |
| cusum@5 | 5 | 10.2264 | 10.1842 ± 0.0121 | 3.49 |
| sr@520.886 | 1 | 17.4536 | 17.2589 ± 0.0203 | 9.61 |
| sr@520.886 | 2 | 14.5005 | 14.3586 ± 0.0161 | 8.81 |
| sr@520.886 | 3 | 12.9727 | 12.8313 ± 0.0130 | 10.83 |
| sr@520.886 | 5 | 11.0485 | 10.9230 ± 0.0097 | 12.91 |

Worst `|z| = 12.91` against a limit of 4.

### 6.6 Structural diagnostics

The expected short-window correction at `m = 5`, which Priority 1 proves
nonnegative for the Gaussian score, and the gain the *Gaussian* formula would
report if applied unchanged off its model:

| detector | family | `E_0[Q_5]` | `E[A_5 S]` | `E[B_5 S]` | Gaussian form `E[A_5 T]` |
|---|---|---|---|---|---|
| cusum@5 | gaussian | +0.00285 ± 0.00010 | 10.1842 | 10.1814 | 10.1842 |
| cusum@5 | laplace | +0.01513 ± 0.00013 | 6.3917 | 6.3766 | 9.8048 |
| cusum@5 | logistic | +0.00809 ± 0.00011 | 8.1379 | 8.1298 | 9.9637 |
| cusum@5 | skewnormal4 | +0.00757 ± 0.00013 | 3.4946 | 3.4871 | 2.8162 |
| cusum@5 | t1p5 | +0.28354 ± 0.00307 | 1.7751 | 1.4915 | 2226.2190 |
| cusum@5 | t3 | +0.02069 ± 0.00019 | 3.5995 | 3.5788 | 15.4995 |
| sr@520.886 | gaussian | +0.00043 ± 0.00003 | 10.9230 | 10.9225 | 10.9230 |
| sr@520.886 | laplace | +0.00587 ± 0.00012 | 7.6115 | 7.6056 | 10.8207 |
| sr@520.886 | logistic | +0.00228 ± 0.00005 | 9.2044 | 9.2022 | 10.8707 |
| sr@520.886 | skewnormal4 | +0.00223 ± 0.00007 | 4.8861 | 4.8839 | 4.1422 |
| sr@520.886 | t1p5 | +0.23261 ± 0.00350 | 1.9109 | 1.6783 | 2752.1007 |
| sr@520.886 | t3 | +0.01296 ± 0.00014 | 4.5623 | 4.5493 | 16.7802 |

## 7. Lean / formal status

```text
compiled:                            yes, 19 theorem declarations
axioms:                              propext, Classical.choice, Quot.sound
sorry / sorryAx / project axioms:     none
imports:                             MGtOneClosure, SRPriority2, StabilityMapP3
```

The load-bearing declaration is `hasDerivAt_stoppedMean`, which **proves** the
stopped derivative bridge for an abstract likelihood family from Mathlib's
`hasDerivAt_integral_of_dominated_loc_of_lip`.  Track 3A/3B's corresponding
declaration takes that bridge as a hypothesis and returns it; Priority 1 and
Priority 2 prove it, but through the pointwise-derivative variant, which the
Laplace family does not satisfy.  `gaussian_reuse_derivative` then derives the
frozen Gaussian statement from the abstract one as an instance, so the closed
result is a corollary of the general one rather than a parallel claim.

Boundary, stated in full in `LEAN_CORRESPONDENCE.md` §3: Lean constructs no
probability space, no stopping time and no density; it does not prove that the
product of density ratios is the Radon-Nikodym derivative on the stopped
sigma-field; it does not discharge L1-L5 for the frozen processes; and it
evaluates no gain.  Those remain human proofs, written out in `PROOF.md`
without appeal to unnamed regularity.

## 8. Arb / certification status

Three objects, at 160 bits, all checks passing:

| object | horizon | content |
|---|---|---|
| unit-variance Laplace, memoryless detector, `m=1` | **unbounded** | `Gamma_1 = 1 + 2√2 = 3.828427124746190...`, origin is fixed, central differences converge to `-Gamma_1`, attraction at `rho = 1/4`, repulsion at `rho = 1/2`, `rho_c = √2/4` |
| uniform innovations, memoryless detector | exact rational | alarm probability constant in `e`, map exactly linear with slope `-2`, identity defect exactly `2` |
| finite-support tilt with a bounded non-affine score | finite support | gain `5/2`, fixed-denominator gain `13/5`, `E[Q_5] = -1/10 < 0`, Gaussian-form gain `7/2 ≠ 5/2`, attraction at `rho=1/2`, repulsion at `rho=1`, exact boundary `rho_c = 2/3` |

The Laplace object is the first **unbounded-horizon, non-Gaussian**
interval-certified instance in this line of work: `tau` is geometric and
unbounded, and the series over `n` is summed exactly by memorylessness rather
than truncated.  Its derivation is human mathematics (`PROOF.md` §11); Arb
removes floating-point doubt, not proof obligations.

**Not certified, and explicitly so:** every `Gamma` under the frozen CUSUM or
SR, Gaussian or not.  Those are Monte Carlo estimates, exactly as they were at
Priorities 1, 2 and 3.  The evidence boundary is unchanged.

## 9. Verification matrix

### 9.1 Priority-4 closure gates

| gate | result |
|---|---|
| `protocol_hash_matches_manifest` | PASS |
| `witness_hash_matches_manifest` | PASS |
| `route_q_analytic_identity_holds` | PASS |
| `route_q_uniform_identity_fails_as_predicted` | PASS |
| `route_n_neutrality_holds` | PASS |
| `all_theorem_supported_cells_pass` | **FAIL** |
| `all_outside_assumption_cells_demonstrate_failure` | **FAIL** |
| `both_frozen_detectors_covered` | PASS |
| `at_least_five_theorem_supported_families` | PASS |
| `asymmetric_family_origin_not_a_fixed_point` | PASS |
| `gaussian_consistency_with_closed_core` | **FAIL** |
| `certificate_all_checks_pass` | PASS |
| `lean_compiles_with_clean_axioms` | PASS |
| `repository_verification_all_gates_pass` | PASS |

| negative claim asserted false | holds |
|---|---|
| `frozen_infinite_horizon_gains_interval_certified` | yes |
| `any_frozen_p1_p2_p3_artifact_modified` | yes |
| `novelty_verdict_claimed` | yes |
| `global_or_nonlinear_stability_claimed` | yes |
| `distribution_free_or_detector_universal_claim` | yes |
| `asymmetric_family_classified_at_the_origin` | yes |

### 9.2 Repository-wide verification

```text
status: COMPLETED
artifact: results/verification.json  PRESENT
gate:     repository_verification_all_gates_pass = True
```

Independent adjudication completed the repository driver under the intended
`en_US.UTF-8` locale with a real `rg` binary.  Every suite named as required by
the driver passed literally.  Non-required historical failures were also run
and classified rather than excused.

| check | result |
|---|---|
| focused P4 tests | 134 passed, 2 skipped |
| `scripts/verify_level_1_3.sh` | PASS; 90 pytest cases in its final stage |
| `sr_derivative_priority2/tests` | 19 passed |
| `external_validation_v3/tests` | 75 passed |
| `d4_phase_map/tests` | 18 passed |
| `l4r06_policy/tests` | 28 passed |
| `l4r12_operational_crossing/tests` | 26 passed |
| `location_family_track3ab/tests` | 29 passed |
| `m_gt_1_priority1/tests` | 13 passed (needs `en_US.UTF-8`) |
| `sr_derivative/tests` | 94 passed (needs a real `rg` binary) |
| `m_gt_1_track1b/tests` | 32 passed (needs a real `rg` binary) |
| `m_rho_stability_priority3/tests` in a clean HEAD worktree | 85 passed |
| `location_family/tests` at its frozen revision `1110065` | 37 passed |
| environment probes (locale collation, ripgrep) | all consistent |
| controlled locale/PATH causality matrix (12 runs, 2 scopes) | all outcomes as expected |
| `level4/closure_proofs/*` protected-tree byte identity to HEAD | 12/12 clean |

The aggregate `scripts/verify_level_4.sh`, `external_validation_v2`,
`final_global_reaudit`, `final_level4_closure`, and
`verify_post_level4_archive.py` were also run.  They reproduce the known
52-file historical guard and README archive-hash diagnostics already recorded
by P1/P2; `external_validation_v3` passes.  Controlled clean-HEAD and
freeze-scoped replays show no P4-introduced scientific regression.

Freeze-scoped replays that *were* completed, with the clean-HEAD
control that separates a pre-existing breakage from one this namespace
causes:

| suite | revision | working tree | frozen tree | clean HEAD | already broken at HEAD |
|---|---|---|---|---|---|
| `priority3` | HEAD | 1 failed, 84 passed | 85 passed | 85 passed | no — later untracked namespaces trip its "nothing outside my own tree changed" assertion |
| `location_family` | `1110065` | 1 failed, 36 passed | 37 passed | 1 failed, 36 passed | **yes** — caused by `location_family_track3ab`, entirely independent of P4 |

### 9.3 Focused Priority-4 suite

```text
137 passed, 2 skipped (final isolated P4 overlay on clean HEAD)
```


## 10. Remaining limitations

1. **Not an ARL-matched comparison.**  Every family runs at the same frozen
   threshold, so in-control ARLs differ.  A difference between two families'
   gains mixes the innovation law with the alarm rate.  No claim is made that
   one family is more or less stable than another.  The fix is a follow-up
   campaign with per-family threshold calibration.
2. **Heavy-tailed standard errors.**  `t3` and `t1p5` have infinite fourth
   moments; their error bars are themselves heavy-tailed and their `|z|`
   columns are indicative.
3. **`t1p5` is at its natural scale**, having no variance to normalise, so its
   gain is not comparable to the unit-variance families'.
4. **Route Q is not the frozen detector.**  It is exact, and it is exact about
   the mathematics, not about `h = 5` or `A = 520.886133602749`.
5. **Route A and Route B share the simulator.**  Mitigated by Route Q and by
   the Gaussian cross-implementation check against P1/P2, not eliminated.
6. **Frozen after a pilot.**  `PROVENANCE.md` §2 records exactly what the pilot
   saw, the defect it found in this campaign's own random-number stream, and
   the permanent regression test that now guards it.
7. **No infinite-horizon interval certification of any frozen gain.**
8. **No novelty verdict** — `NOVELTY-NOT-ADJUDICATED`, see below.
9. **Nothing global or nonlinear.**  Priority 4 is first order and local.  P5
   observations are confined to a handoff note.

## 11. Prior art and novelty

`NOVELTY_AUDIT.md` returns `NOVELTY-NOT-ADJUDICATED`.  No internet access, no
literature search, therefore no novelty verdict.

The in-repository overlap is real and is stated everywhere it matters:
`location_family` (PARTIAL) and `location_family_track3ab` (CLOSED) already
proved the stopped-score identity for a general regular location family with
the **single terminal observation** `H_tau = Z_tau`, i.e. `m = 1`.  Priority 4's
delta is the truncated window at general `m` with the random denominator and
the `tau < m` branch, both frozen detectors in one statement, the weakened
differentiation hypothesis, the neutrality corollary, the sign analysis, the
two proved failure modes, and a Lean proof of the bridge those tracks assumed.

Seven prior-art areas that a real audit must cover — sequential analysis,
score-function sensitivity estimators, self-starting control charts,
post-selection inference, renewal/stopping theory, stochastic approximation,
and classical location-score identities — are listed with candidate references
in `NOVELTY_AUDIT.md`.  Until they are searched, every claim in this namespace
is stated as an extension *relative to the frozen ReBaseGuard core*.

## 12. Adversarial review outcome

`ADVERSARIAL_REVIEW.md` runs fifteen attacks.  Three changed the result:

* **A1/A3** — the correction sign and the differentiation hypothesis were both
  found to be Gaussian-specific, and the claim was narrowed accordingly;
* **A4** — the L4 discharge lemma absorbed a constant without saying how, and
  was rewritten with explicit pathwise bounds and an explicit `C_d`;
* **A7/A9** — the classifier now *refuses* to classify asymmetric cells, and
  the cross-family table is explicitly labelled as not ARL matched.

Nothing was repaired to make the campaign close.

## 13. Files

All new, all under `level4/closure_proofs/p4_theory_generalization/`.  No file
outside that directory was created or modified; twelve protected trees are
asserted byte-identical to `HEAD` on every test run.

## 14. Git status and handoff

```text
HEAD          68bc23d2bc90c33bcc638bbedf90b2a855e6480d
branch        main
committed     nothing
pushed        nothing
```

Integration, independent review and the commit are a separate pass.
Independent review is now recorded in `INDEPENDENT_ADJUDICATION.md`; checkpoint
commit and push status are reported by the integrating agent because a commit
cannot truthfully contain its own final object id.
