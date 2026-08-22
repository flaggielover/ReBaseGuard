# Historical t3 variance diagnosis

## Scope and conclusion

This diagnosis was completed before any Track-3A confirmatory outcome.  It
replayed only the frozen historical Track-3 seed families and reproduced every
retained t3 batch mean (Route A exactly; Route B to at most
`8.44e-14`).  The replay recovered path-level variance and CRN covariance that
the old retained JSON did not contain.  It did not create a new replication or
alter the historical decision.

The historical `4.605351% > 3%` result is most consistent with **ordinary
sampling variance amplified by the heavy-tailed t3 stopped-gain integrand**.
It is not evidence for an implementation mismatch, unstable denominator, or
detectable finite-difference bias.  The conventional t3 score itself is
bounded, so the mechanism is not accurately described as an unbounded
"score-tail" failure.

The historical Track-3 gate remains failed exactly as frozen.

## Historical discrepancy in uncertainty units

At primary `h=0.0125`, the old independent direct-map replications were

```text
replication 1: -7.4579823232 ± 0.1891541103
replication 2: -7.8095439424 ± 0.1880057009
absolute difference: 0.3515616193
combined SE:         0.2666934964
|z|:                 1.3182234438
symmetric relative:  4.6053514258%
```

At equality, the delta-method SE of the relative replication discrepancy is
`3.4936045534%`.  Thus the observed `4.605351%` discrepancy is exactly
`1.3182` of its null standard errors, while the historical 3% point threshold
was only `0.8587` null standard errors wide.  The failed relative predicate was
therefore low-precision at the old sample size even though it remained a valid
and mandatory frozen gate.

The denominator was stable: the mean absolute derivative magnitude was
`7.6337631`, far from zero.  The failure was not denominator instability.

## Route A: stopped-score estimator

The old Route A used `48 × 10,000 = 480,000` paths.  Historical replay gives:

| Quantity | Value |
|---|---:|
| `Gamma_f` | `8.7100873115` |
| batch-based SE | `0.4631692196` |
| path-level SD of `Z_tau sum psi` | `290.7695853130` |
| path-i.i.d. SE | `0.4196897459` |
| batch SD | `3.2089304836` |
| path skew | `-1.9858` |
| path excess kurtosis | `265.7540` |
| path minimum / maximum | `-25968.13 / 14755.19` |

The empirical between-batch variance of batch means was `10.2972`; the mean
within-batch path variance implies `8.4545`.  Their ratio, `1.218`, is
unexceptional for only 48 batches and does not expose a second batch-level
mechanism.  Batches differ only by seed.

Tail concentration is material:

- the largest 10% of paths by absolute gain contributed 77.61% of variance;
- the largest 1% contributed 39.17%;
- the largest 0.1% contributed 17.93%; and
- the largest 0.01% contributed 8.28%.

The most influential batch changed the full mean by `0.18270`, or `2.098%` of
`Gamma_f`, under leave-one-batch-out deletion.  The batch median (`8.7930`) and
10% trimmed mean (`8.8402`) were close to the ordinary mean (`8.7101`), so no
single batch explains the result.  Robust summaries are diagnostic only.

Across historical families, the t3 Route-A batch SD was `3.2089`, compared
with `1.1001` for t5, `0.4862` for t10, and `0.3980` for Gaussian.  This is the
largest route-specific variance inflation in the grid.

For unit-variance t3,

```text
psi(z) = 4z / (1 + z^2),     |psi(z)| <= 2.
```

Therefore the location score is bounded.  The high variance enters through
the heavy-tailed terminal residual and its product with the stopped score sum,
not through an unbounded single-step score.

## Route B: finite difference and CRN

Each old replication used `48 × 5,000 = 240,000` paired path streams.  At the
primary step, the `+h/-h` path contributions had correlations `0.9680` and
`0.9666`.  Paired-CRN variance was only `3.20%` and `3.34%` of the variance
that would result from incorrectly treating the two sides as independent.
The paired architecture worked as intended.

Primary batch distributions had SDs `1.3105` and `1.3025`, with modest batch
skew (`0.022` and `0.451`).  The largest leave-one-batch-out changes were
`1.009%` and `0.924%` of the replication mean.  There is no concentrated batch
outlier capable of explaining the 4.605% separation.

The h ladder was:

| `h` | pooled derivative | replication relative | replication `|z|` |
|---:|---:|---:|---:|
| `0.05` | `-7.7215602` | `2.277%` | `1.342` |
| `0.025` | `-7.6645163` | `2.605%` | `1.065` |
| `0.0125` | `-7.6337631` | `4.605%` | `1.318` |

There is no stable convergence-order or monotone between-replication pattern.
The primary result is statistically compatible with the coarser results and
with the Route-A prediction.  This does not prove zero finite-difference bias,
but retained data contain no affirmative bias signal.

## Route A versus Route B

The old pooled comparison was

```text
Route A derivative:  -7.7100873115 ± 0.4631692196
Route B derivative:  -7.6337631328 ± 0.1338634924
relative discrepancy: 0.9948504%
|z|:                  0.1583076
```

Its delta-method relative SE at equality was about `6.28%`, dominated by Route
A.  The favorable point comparison supports the theorem but was not precise
enough to rescue the independent-replication predicate.

## Mechanism classification

| Candidate | Diagnosis |
|---|---|
| sampling variance | **PRIMARY — supported quantitatively** |
| heavy-tail score variance | Rejected as phrased: `psi` is bounded; heavy-tail gain variance is real |
| finite-difference bias | No retained affirmative evidence; unresolved only below old precision |
| implementation mismatch | Rejected by exact replay, source separation, ARL, reflection, and tie controls |
| unstable denominator | Rejected; magnitude was about `7.63` |
| unresolved mechanism | Not needed to explain the failed predicate |

The retained-data conclusion is intentionally limited: it justifies a new
precision-sized experiment.  It does not retroactively pass Track 3.

Machine-readable evidence is in
`results/historical_variance_diagnosis.json`; the reproducing script is
`numerics/diagnose_historical_t3.py`.
