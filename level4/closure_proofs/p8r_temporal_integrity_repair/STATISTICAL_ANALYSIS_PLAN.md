# P8R statistical analysis plan

**Frozen at the temporal anchor.** `experiments/derive_resolution.py` applies
this plan and contains no threshold literal of its own; every number it uses
comes from `config`.

## 1. Estimator and the unit of replication

The statistical unit is the **addressable batch**, not the cycle. A batch is a
disjoint block of addresses, so batches are independent by construction and the
batch-means standard error

```
SE = sd(batch values, ddof=1) / sqrt(n_batches)
```

needs no mixing or stationarity assumption. All 20 `E1` batches and all 20 `E5`
batches enter; none is dropped for any reason.

For the chain and drift experiments the unit is the replicate, and the same
formula applies over replicates.

## 2. Intervals

Two-sided 95%, `Z95 = 1.959963984540054`. Reproduction comparisons use the
combined-SE z statistic

```
z = (a - b) / sqrt(SE_a^2 + SE_b^2)
```

with agreement declared at `|z| <= COMBINED_Z_TOLERANCE = 3`. This is the
tolerance P3, P4, P7 and P8 all used; it is inherited, not chosen here.

`rho_c = 1/|1 - Gamma_A|` is reported with the **exact monotone image** of the
`Gamma_A` interval, not a delta-method approximation, and the interval is
correctly unbounded when the `Gamma_A` interval straddles 1
(`analysis.rho_c_from_gamma`, checked in `tests/test_statistics.py`).

## 3. Pairing — the rule that must not be broken

The stopped-cycle address deliberately omits the detector, the window and the
convention. Therefore `cusum` and `sr` at the same `(family, batch)` are driven
by the **same** innovations, and every cross-detector, cross-window and
cross-convention comparison is a common-random-number comparison.

**A CRN-paired ratio must never be given an independent-SE interval.** The
P8 adjudication had to recompute the detector ratios by hand for exactly this
reason. P8R stores the raw per-batch `Gamma_A` vectors in
`results/gamma_matrix_*.json` (`batch_gamma_A`) so that the pairing is available
downstream, and `derive_resolution.paired_ratio` computes

```
r      = mean(a) / mean(b)
d_i    = a_i - r * b_i
SE(r)  = SE(mean d) / |mean b|
```

which carries the covariance exactly. The naive independent SE is computed too
and stored beside it as `naive_unpaired_se`, so an adjudicator can see the size
of the effect rather than take the claim on trust.

Comparisons that are **not** paired, and are treated as independent:

* `E1` against `E5` — different production tags, disjoint fields;
* P8R against P3, P4 or P7 — different campaigns, different fields;
* P8R production against the `E6` reimplementation — different entropy source
  entirely.

Comparisons across innovation family are **not** paired: `f` is in the address,
different families have different laws, and pairing them would require an
expensive family-asymmetric inverse-CDF layer. This is declared, not discovered.

## 4. Heavy tails

`t3` is `MOMENT_MARGINAL`, declared before any result. The `Gamma` integrand has
a divergent third absolute moment, so:

* no Berry–Esseen rate is available for the batch-mean CLT;
* the sample variance itself has infinite variance, so the estimated SE is
  unstable and convergence is slow;
* normal batch intervals are useful for the large non-heavy-tail margins but are
  **fragile** for `t3` and are labelled as such wherever they appear.

Consequences, all frozen:

* `t3` cells are reported in full in `S6` and **never counted** either way.
* `S13` applies a stricter agreement fraction to the non-`t3` cells
  (`S13_NON_T3_FRACTION`) than to all cells (`S13_CELL_FRACTION`).
* `S15` — the `t3`/`m=20` attraction question — requires the upper 95% bound to
  fall below 2 in `E1`, in `E5` **and** in the independent reimplementation.
  This is deliberately conservative. A point estimate below 2 is not evidence of
  attraction; the theorem hypotheses for `t3` are not established; and `m = 20`
  is outside P3's supported grid in any case. `INCONCLUSIVE` is the expected and
  acceptable answer.

## 5. Multiple comparisons

The gates are **literal**. No gate is corrected for multiplicity, and no
multiplicity correction may rescue a gate.

One descriptive companion exists: `S10` carries a Benjamini–Hochberg analysis at
`BH_Q = 0.10` over the bracket-rate differences, because P7's boundary criterion
is a bare `max` over brackets with no uncertainty margin and can therefore flip
on Monte Carlo noise. It is labelled `DESCRIPTIVE ONLY` in the artifact, it is
reported *beside* `S10` and never inside it, and `tests/test_statistics.py`
asserts that the gate statistic does not reference it.

Cochran's `Q` on the seed families is likewise `DESCRIPTIVE_ONLY`. It is not a
closure test and no resolution depends on it.

## 6. Censoring and insufficient tails

The drift experiment observes the first cycle after the change, so the delay is
observed exactly and is not censored. The tail statistics are.

Wherever fewer than `TAIL_EVENT_FLOOR = 200` tail events occur, the row is
labelled `INSUFFICIENT_TAIL_EVENTS`. **The row is still reported, with its `q50`,
`q95` and `P(delay>100)`.** Labelling is not dropping: `S14` requires that every
declared cell be present *and* labelled, so a silently missing cell fails the
question.

## 7. Exact identities are tested absolutely, not statistically

Two of the questions are exact algebra, not measurements:

* `S9`, the convention identity `Gamma_A - Gamma_B = R_m`, tested at
  `S9_EXACT_TOL = 1e-12`;
* `S8`, the decomposition `Gamma_A(m) = (1/m) sum_r gamma_r + R_m`, tested at
  `S8_ABS_TOL = 1e-9`.

Both sides of each identity are the same expectation summed in a different
order, so the residual is floating-point noise of order `1e-16` — and so is its
batch standard error. A `k x SE` rule would therefore compare noise to noise and
return an arbitrary `O(1)` ratio. The absolute test is both the stricter and the
meaningful one. `S8` is a genuine independent check of the lag decomposition even
though it shares an algebraic identity with `S9`, because the two compute
`Gamma_B` by different summation routes.

## 8. Ratio and window-factor uncertainty

`K(D,f,m) = rho_c(D,f,m)/rho_c(D,f,1)` is a ratio of two quantities estimated on
the **same** batches at two windows, hence paired. `S7`, `S7D` and `S7F` are
literal spread and residual statistics against fixed thresholds, exactly as P8's
`G4` family were; they carry no interval and none is required, because the
frozen rules are stated on the point estimates. The paired batch vectors are
stored, so an adjudicator can attach intervals independently.

## 9. Cross-family comparison

Families are compared only through statistics that are already family-specific
ratios (`K`) or through spreads of such ratios. No estimate is pooled across
families, and no family-level average is reported as if it were a single
population quantity.

## 10. What is never done

* No estimator, interval, tolerance or fraction is chosen after seeing a result.
* No cell is dropped for being inconvenient; exclusions come only from the
  frozen calibration ladder and are recorded as artifacts.
* No naive independent SE is used for a CRN-paired ratio.
* No multiplicity correction is applied to a gate.
* No heavy-tail interval is presented without its fragility label.
* No `INSUFFICIENT_TAIL_EVENTS` row is quietly omitted.
