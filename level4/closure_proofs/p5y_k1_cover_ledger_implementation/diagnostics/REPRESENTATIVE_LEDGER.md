# Representative complete cover ledger (CUSUM)

NON-RESULT-BEARING. Diagnostic evidence for an implementation
qualification, not a scientific certificate and not a production run.
No cell was subdivided; no threshold, budget, precision or cap was
changed. The anchor SELECTS a frozen cell; the expansion point is
always that cell's exact midpoint.

```text
B_cover_usage = outward_upper( rho * mag(D_interval) + rho^2 * M_R2 / 2 )
STYLE_1: D_interval already contains every derivative uncertainty;
         no separate rho*epsD charge exists.
```

| anchor(s) | cell | rho | C | m | mag D | M_R2 | nominal rho*\|D_c\| | deriv rho*d | curvature | B_cover | util of .050 | worst top-level util | obligation | target (-2,2) |
|---|---:|---|---|---:|---|---|---|---|---|---|---:|---:|---|---|
| 0 | 0 | 0.0002542 | 1232.84 | 1 | 19.4594 | 18099.1 | 0.003783 | 0.001162 | 0.0005845 | 0.00553014 | 11.06% | 11.37% | **PASS** | PASS |
| 0 | 0 | 0.0002542 | 1232.84 | 2 | 20.7906 | 33683.9 | 0.003115 | 0.002169 | 0.001088 | 0.00637178 | 12.74% | 14.12% | **PASS** | PASS |
| 0 | 0 | 0.0002542 | 1232.84 | 3 | 19.3281 | 33165.5 | 0.002777 | 0.002136 | 0.001071 | 0.00598334 | 11.97% | 15.41% | **PASS** | PASS |
| 0 | 0 | 0.0002542 | 1232.84 | 5 | 17.4529 | 32610.6 | 0.002336 | 0.0021 | 0.001053 | 0.00548884 | 10.98% | 16.6% | **PASS** | PASS |
| 1/10 | 136 | 0.0005509 | 568.713 | 1 | 9.43671 | 4213.09 | 0.004023 | 0.001176 | 0.0006393 | 0.005838 | 11.68% | 11.68% | **PASS** | PASS |
| 1/10 | 136 | 0.0005509 | 568.713 | 2 | 8.41757 | 4927.32 | 0.003231 | 0.001407 | 0.0007477 | 0.00538493 | 10.77% | 10.77% | **PASS** | PASS |
| 1/10 | 136 | 0.0005509 | 568.713 | 3 | 7.59015 | 4726.64 | 0.002828 | 0.001353 | 0.0007172 | 0.00489866 | 9.797% | 9.797% | **PASS** | PASS |
| 1/10 | 136 | 0.0005509 | 568.713 | 5 | 6.60362 | 4549.64 | 0.00233 | 0.001308 | 0.0006904 | 0.00432832 | 8.657% | 9.016% | **PASS** | PASS |
| 1/4 | 221 | 0.001506 | 208.057 | 1 | 0.490989 | 354.111 | 5.729e-05 | 0.0006821 | 0.0004015 | 0.00114095 | 2.282% | 6.72% | **PASS** | PASS |
| 1/4 | 221 | 0.001506 | 208.057 | 2 | 0.69879 | 313.088 | 0.0004554 | 0.0005969 | 0.000355 | 0.00140737 | 2.815% | 3.732% | **PASS** | PASS |
| 1/4 | 221 | 0.001506 | 208.057 | 3 | 0.820061 | 304.554 | 0.000657 | 0.0005779 | 0.0003453 | 0.00158032 | 3.161% | 3.161% | **PASS** | PASS |
| 1/4 | 221 | 0.001506 | 208.057 | 5 | 0.912896 | 300.932 | 0.0008147 | 0.00056 | 0.0003412 | 0.00171602 | 3.432% | 3.643% | **PASS** | PASS |
| 1 | 293 | 0.01802 | 17.3891 | 1 | 0.607629 | 7.00476 | 0.01089 | 5.737e-05 | 0.001137 | 0.0120858 | 24.17% | 24.17% | **PASS** | PASS |
| 1 | 293 | 0.01802 | 17.3891 | 2 | 0.588119 | 15.6404 | 0.01047 | 0.0001316 | 0.002539 | 0.0131361 | 26.27% | 26.27% | **PASS** | PASS |
| 1 | 293 | 0.01802 | 17.3891 | 3 | 0.547004 | 24.3275 | 0.009684 | 0.0001722 | 0.003949 | 0.0138055 | 27.61% | 27.61% | **PASS** | PASS |
| 1 | 293 | 0.01802 | 17.3891 | 5 | 0.458391 | 46.8597 | 0.008033 | 0.0002262 | 0.007607 | 0.0158666 | 31.73% | 31.73% | **PASS** | PASS |
| 27/5, 11/2 | 325 | 0.09624 | 2.00117 | 1 | 0.0341296 | 1.84201 | 0.003274 | 1.046e-05 | 0.008531 | 0.0118154 | 23.63% | 23.63% | **PASS** | PASS |
| 27/5, 11/2 | 325 | 0.09624 | 2.00117 | 2 | 0.0174934 | 14.0567 | 0.001637 | 4.648e-05 | 0.0651 | 0.0667831 | 133.6% | 133.6% | **FAIL** | PASS |
| 27/5, 11/2 | 325 | 0.09624 | 2.00117 | 3 | 0.0185947 | 29.874 | 0.001704 | 8.516e-05 | 0.1384 | 0.140143 | 280.3% | 280.3% | **FAIL** | PASS |
| 27/5, 11/2 | 325 | 0.09624 | 2.00117 | 5 | 0.0192289 | 77.4368 | 0.001704 | 0.0001462 | 0.3586 | 0.360478 | 721% | 721% | **FAIL** | PASS |

**17 of 20 representative obligations PASS every frozen gate; 3 FAIL.** The `obligation` column is the verdict; the `target (-2,2)` column is the separate enclosure gate, which passes everywhere.

## Worst representative

```text
worst B_cover utilization   720.955% of .050   (cell 325, m=5)
  nominal drift variation   0.00170443
  derivative uncertainty    0.000146189
  curvature                 0.358627
  cover arithmetic          5.21703e-77
  total B_cover usage       0.360478   cap .050
  margin                    -0.310478

worst TOP-LEVEL utilization 720.955%   (cell 325, m=5)
```

## Per-channel top-level usage at the worst cell

| line | usage | cap | utilization | status |
|---|---|---|---:|---|
| B_candidate | 7.85167e-06 | 1/25 | 0.01963% | PASS |
| B_cover | 0.360478 | 1/20 | 721% | FAIL |
| B_interval | 2.95586e-12 | 1/100 | 2.956e-08% | PASS |
| B_kernel | 0.000210175 | 1/25 | 0.5254% | PASS |
| B_other | 0 | 1/25 | 0% | PASS |
| B_resolvent | 0 | 0/1 | n/a | PASS |
| B_rounding | 0 | 1/100 | 0% | PASS |
| top_reserve | 0 | 1/100 | n/a | - |

## Detector coverage

```text
CUSUM   5 representative cells x m in {1,2,3,5}
SR      NOT_IMPLEMENTED
        no raw-variable SR DAG exists in the repository; Task1R certified the F_0 class only, on one patch at one drift, in a different (softplus Taylor-model) formulation
```

The SR half of the frozen scope is NOT certified here and is NOT
reported as zero, small or passing. It is NOT_IMPLEMENTED.
