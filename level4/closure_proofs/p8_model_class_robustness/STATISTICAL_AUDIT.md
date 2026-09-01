# P8 statistical audit

Methodology first, then the numbers. Every number quoted below is printed by
`experiments/make_tables.py` from `results/*.json`; none is typed by hand.

---

## 1. Statistical units and uncertainty

| experiment | unit | n units | uncertainty |
|---|---|---:|---|
| `E1` `Gamma` matrix | the **batch** (204,800 cycles) | 20 per cell | batch-means SE = `sd/sqrt(20)`; 95% interval `+- 1.96 SE` |
| `E5` seed replication | the batch, at an independent batch family (100..119) | 20 per cell | as `E1` |
| `E2` SR calibration | the cycle, in blocks of 4096 | 61 blocks per evaluation, 500 per verification | block-means SE |
| `E3` chain ladder | the **replicate** | 4,000 per cell | replicate-level SE |
| `E4` drift | the **replicate** | 8,000 per cell | replicate-level SE; delay tails additionally reported as `q50`, `q95`, `P(>100)` |
| `E6` P4 replication diagnostic | the **replication** (409,600 cycles) | 12 per family | across-replication sd vs mean nominal within-replication SE |

Batch means, not pooled cycle means, are used for `E1` because they are robust
to within-batch dependence (there is none by construction, but the estimator
does not rely on that) and because they are the unit at which the primitive
field is addressed.

**`K`'s standard error is computed on the batch ratios**, `K_b = (Gamma_b(1)-1)/(Gamma_b(m)-1)`,
not by an independence-assuming delta method. `Gamma(1)` and `Gamma(m)` are
measured on the *same* cycles and are strongly positively correlated, so an
independent-error propagation would badly overstate `K`'s uncertainty.

## 2. Seed derivation

Every draw is a pure function of its address (`primitives.py`); no seed is
derived from a live-set size, a loop counter, an execution order, or a `hash()`
of a string. Addresses use fixed integer namespaces and SHA-256 tags of fixed
literals. The P8 namespace `0x50385F4D_43520001` is disjoint from Stage D
(`20261001`), P7 (`20260831`) and P6R2b (`0x50365232_42435250`).

CRN pairing is declared in `EXPERIMENT_PROTOCOL.md` §4: paired across detector,
window, window convention and `rho`; **unpaired across innovation family**.
Family comparisons therefore carry the full independent variance, which is the
conservative direction.

## 3. Multiple comparisons

* **One** primary hypothesis (`H1`) at **one** primary statistic (the spread of
  `K` over the eligible cells) at **three** windows `m in {2,3,5}`. The gate
  requires all three, which is a conjunction and needs no adjustment.
* Secondary metric families (chain `arl` / `ref_mse` / `fap100` / `e_acf1`;
  drift `mean` / `q50` / `q95` / `P(>100)`) use Benjamini–Hochberg at
  `q = 0.10` **within** the family where a `p`-value is reported.
* P7's boundary criterion (`G7`) is a **count** criterion over pre-specified
  metrics and brackets and is applied verbatim; it has no `p`-value and needs no
  adjustment.
* The real protection is reproduction: two detectors, six families, six windows,
  two conventions and an independent seed family (`E5`, gate `G10`).

## 4. The large-`n` trap, and how P8 avoids it

At `4,096,000` cycles per cell the SE of `Gamma_A(1)` is of order `0.01`–`0.14`,
i.e. `0.1%`–`1.6%` relative. A homogeneity test on `K` across ten cells will
therefore reject at any conventional level for a heterogeneity of `1%`, which is
scientifically irrelevant.

P8's response, declared before production:

* every invariance gate is a **practical-equivalence** gate with a pre-declared
  margin (`10%` for `G4`/`G4-F`, `3%` for `G4-D`);
* Cochran's `Q`, its `df`, `p` and `I^2` are computed and reported, and are
  labelled `DESCRIPTIVE_ONLY` in the artifact key itself
  (`homogeneity_DESCRIPTIVE_ONLY`);
* no gate anywhere in `CLOSURE_GATES.md` is a null-hypothesis test.

A reader who reads the `p`-values as the result will draw the wrong conclusion.

## 5. Moment conditions — why `t3` is treated apart

The `Gamma_A` estimand is a mean of `zbar^A_m * sum_{t<=tau} psi(Z_t)`.

* For unit-variance `t_nu`, `psi(z) = (nu+1) a^2 z / (nu + a^2 z^2)` with
  `a^2 = nu/(nu-2)` is **bounded**, and `tau` has geometric-type tails, so the
  score-sum factor has all moments.
* `zbar^A_m` is an average of at most `m` innovations, so the integrand inherits
  the innovation tail index `nu`: `E|integrand|^p < infinity` iff `p < nu`.

Hence

| family | `E[X^2]` (CLT) | `E|X|^3` (Berry–Esseen) | `E[X^4]` (SE of the SE) |
|---|---|---|---|
| `gaussian`, `contam0.05`, `contam0.1` | finite | finite | finite |
| `t10` | finite | finite | finite |
| `t5` | finite | finite | finite (`nu = 5 > 4`) |
| **`t3`** | finite | **divergent** | **divergent** |

`t3` therefore has a valid CLT but **no Berry–Esseen rate**, and its sample
variance has infinite variance, so its reported SE is not trustworthy at any
sample size that P8 can afford. This is derived from the tail index, not from
any P8 measurement, and is asserted in `config.MOMENT_MARGINAL` and enforced by
`tests/test_families.py::test_declared_moment_marginal_family_is_exactly_t3`,
which re-derives the set from `tail_moment_order` rather than trusting the
literal.

`E6` measures the consequence directly (§7 below).

## 6. Grid-selection discipline

* The `m` grid is `{1,2,3,5}` (P3-supported) plus `{10,20}` labelled
  `EXTRAPOLATION_BEYOND_P3` in the artifact for every row.
* The `rho` grid is P7's ladder verbatim. Any "best" `rho` reported anywhere in
  P8 is **the best grid point**, is reported with its neighbours and their
  intervals, and is never called an optimum.
* No co-optimality claim of any kind is made. The distance between two grid
  argmaxes, when reported, is reported in grid units with the neighbouring
  values, exactly because a single grid point winning once is not evidence of
  co-optimality.
* `rho_c` intervals use the **exact monotone image** of the `Gamma` interval
  under `rho_c = 1/|1-Gamma|` (P3's own rule), not a linearisation, and return
  an unbounded upper end whenever the `Gamma` interval contains `1`.

---

## 7. Measured uncertainty, effect sizes and sample sizes

### 7.1 `Gamma_A` precision, per family

Relative standard error of `Gamma_A(1)` at `4,096,000` cycles (batch means over
20 batches), CUSUM / SR:

| family | rel. SE, CUSUM | rel. SE, SR | inflation vs `gaussian` |
|---|---:|---:|---:|
| `gaussian` | 0.081% | 0.085% | 1.0x |
| `t10` | 0.212% | 0.211% | 2.5x |
| `t5` | 0.394% | 0.287% | 4.1x |
| `contam0.05` | 0.378% | 0.295% | 4.0x |
| `contam0.1` | 0.235% | 0.267% | 3.0x |
| **`t3`** | **1.588%** | **1.162%** | **16.5x** |

(inflation is the two-detector mean relative SE divided by the Gaussian's.)

The `t3` inflation is the finite-sample signature of the divergent third
absolute moment (§5), visible at the same sample size as every other family. It
was predicted from the tail index before production, and it is why `t3` is
`MOMENT_MARGINAL`.

### 7.2 Effect sizes against the gate margins

| comparison | measured | margin | ratio |
|---|---:|---:|---:|
| cross-family spread of `K`, `m = 5` | 49.29% | 10% | **4.9x the margin** |
| cross-family spread of `K`, `m = 2` | 22.67% | 10% | 2.3x the margin |
| cross-detector residual of `K`, worst cell | 3.63% | 3% | 1.21x the margin |
| `rho_c(D,f,1)` range across the 12 cells | factor 2.54 | — | — |
| wrong-score inflation, `t3`, `m = 1` | 11.66x | — | — |
| `Gamma_A` relative SE inflation at `t3` | 16.5x | — | — |

The `G4` rejection is a large effect against its margin; the `G4-D` failure is a
marginal one, and is reported as such rather than as a clean rejection.

### 7.3 The `E6` replication diagnostic

P4's frozen gate failed because two independent Route-B replications of `t3`
differed by `4.605%` against a `3%` limit. `E6` runs 12 independent
`409,600`-cycle replications of the same estimand per family on P8's own field
and reports, for each, the across-replication scatter against the mean nominal
within-replication standard error. The prediction from §5 is that the ratio is
near `1` for the families with finite fourth moment and materially above `1`
for `t3`, and that a `>= 3%` pairwise gap is common at `t3` and rare elsewhere.
See `results/p4_replication_diagnostic.json` and `RESULTS.md` §11.

**P8 does not adjudicate P4.** It measures what an estimator with this moment
structure does at this sample size, and reports it.

### 7.4 Calibration residuals

The five `NEW_P8_CALIBRATION` SR thresholds verify at `1,024,000` cycles with
relative `ARL_0` errors of `0.10%` (`t10`), `0.07%` (`t5`), `0.44%` (`t3`),
`0.01%` (`contam0.05`), `0.15%` (`contam0.1`) — all inside gate `G2`'s `0.5%`.
The frozen Gaussian SR threshold, which is **not** recalibrated, verifies at
`0.23%`.

`t3`'s `0.44%` is the one worth watching: the refinement phase stopped when its
own `614,400`-cycle sample read inside `0.25%`, and the independent
`1,024,000`-cycle verification then read `0.44%`. That is ordinary Monte Carlo
disagreement between two samples of a quantity whose relative SE is about
`0.10%`–`0.15%`, but it means `t3`'s SR operating point is the least well
matched in the matrix, and `LIMITATIONS.md` `S9` applies to it most.

### 7.5 Where the intervals are, and are not, trustworthy

* `Gamma_A`, `Gamma_B`, `gamma_r`, `R_m`: batch-means SEs over 20 independent
  batch addresses. Trustworthy for all families except `t3` (§5).
* `rho_c`: exact monotone image, no linearisation. Trustworthy wherever
  `Gamma_A`'s interval is.
* `K`: batch-ratio SE, which absorbs the strong positive correlation between
  `Gamma(1)` and `Gamma(m)`. Trustworthy, and materially tighter than a
  delta-method SE would be.
* Chain and drift metrics: replicate-level SEs. Finite-horizon quantities, never
  stationary ones (`LIMITATIONS.md` `L7`).
* Delay tails: reported with `q50`, `q95` and `P(>100)`, and labelled
  `INSUFFICIENT_TAIL_EVENTS` wherever fewer than 200 tail events occurred. That
  label is not decoration.


### 7.6 The `E6` outcome, and what it does and does not license

Measured: the relative across-replication spread of the `m = 1` CUSUM gain is
`0.36%` (`gaussian`), `0.71%`–`1.15%` (`t10`, `t5`, both contaminated families)
and **`6.53%` at `t3`** — an 18-fold inflation. The variance-inflation ratios
(observed sd over mean nominal SE) are `0.83x`–`1.27x` in every family, so the
nominal standard errors are roughly the right *size*; `t3` is understated by
about `25%`, consistent with but much milder than the worst case the moment
argument allows.

The P4-comparable statistic — the probability that **one random pair** of
replications differs by more than `3%` — is `80.3%` at `t3` and `<= 7.6%`
everywhere else, with a **median** `t3` pairwise difference of `7.60%`, larger
than the `4.605%` P4 observed.

**This licenses one narrow statement**: a `3%` two-replication agreement
criterion applied to this estimand at this sample size fails at `t3` most of the
time, so that gate outcome carries little information about the estimand. **It
does not license** any statement about P4's status, about whether P4's theorem
holds, or about what P4 should have done. P8 owns neither the artifact nor the
adjudication.

### 7.7 A residual anomaly in the seed replication

Gate `G10` passes at `95.8%` overall and at exactly `95.0%` on the non-`t3`
cells, its required threshold. All three failures are the same cell, SR /
`gaussian`, offset by `+0.30%` to `+0.51%` between the two seed families at
**every** window — one discrepancy at `z ~ 3`–`4`, not six, since all windows
share the same cycles.

Across the 72 comparisons the `z` values have mean `0.08` and sd `1.26`. An sd
above `1` means the batch-means standard error slightly **understates** true
cell-to-cell variability, most visibly where the SE is smallest. The practical
consequence is that P8's tightest intervals — the Gaussian cells, at `0.08%`
relative — should be read as slightly optimistic. Nothing P8 concludes depends
on precision at that level: the reported effects are `22%`–`49%`.

The anomaly is **not explained**. It is a specific, cheap target for independent
attack: re-run `E1`/`E5` for SR `gaussian` at a third experiment tag and see
which of the two it agrees with.
