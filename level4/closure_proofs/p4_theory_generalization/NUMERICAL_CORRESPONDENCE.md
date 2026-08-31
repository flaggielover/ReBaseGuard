# Numerical correspondence

Four independent routes.  Route Q and Route N have known or deterministically computed answers and therefore *test* the implementation; Routes A and B are two Monte Carlo estimates of the same quantity under the frozen detector recursions and therefore test the theorem.  Every table states its own evidence class.

## 1. Route Q -- deterministic quadrature, memoryless detector

No sampling error.  Both sides of Theorem G1 are evaluated by adaptive quadrature for the detector `tau = inf{t : |Z_t| >= c}` with `c = 2.0`, including the truncated window, the random denominator and the `tau < m` branch.  This is **not** the frozen operating point and is never reported as evidence about it.

| family | m | `Gamma` (score side) | `-g_m'(0)` (map side) | relative | result |
|---|---|---|---|---|---|
| gaussian | 1 | 5.7464310656 | 5.7464310657 | 3.37e-12 | PASS |
| gaussian | 2 | 3.3732155328 | 3.3732155328 | 3.03e-12 | PASS |
| gaussian | 3 | 2.6181376662 | 2.6181376662 | 2.79e-12 | PASS |
| gaussian | 5 | 2.0513982739 | 2.0513982739 | 2.49e-12 | PASS |
| laplace | 1 | 3.8284271247 | 3.8284271248 | 2.94e-12 | PASS |
| laplace | 2 | 2.4142135624 | 2.4142135624 | 2.69e-12 | PASS |
| laplace | 3 | 1.9706717577 | 1.9706717577 | 2.54e-12 | PASS |
| laplace | 5 | 1.6442109179 | 1.6442109179 | 2.38e-12 | PASS |
| logistic | 1 | 4.5336739110 | 4.5336739110 | 2.94e-12 | PASS |
| logistic | 2 | 2.7668369555 | 2.7668369555 | 2.63e-12 | PASS |
| logistic | 3 | 2.2083889507 | 2.2083889507 | 2.43e-12 | PASS |
| logistic | 5 | 1.7929915094 | 1.7929915094 | 2.19e-12 | PASS |
| t3 | 1 | 3.5138179502 | 3.5138179503 | 2.67e-11 | PASS |
| t3 | 2 | 2.2569059252 | 2.2569059252 | 2.56e-11 | PASS |
| t3 | 3 | 1.8549108367 | 1.8549108368 | 2.63e-11 | PASS |
| t3 | 5 | 1.5510333432 | 1.5510333433 | 2.90e-11 | PASS |
| t1p5 | 1 | 2.1959897408 | 2.1959897445 | 1.68e-09 | PASS |
| t1p5 | 2 | 1.5964976021 | 1.5964976064 | 2.72e-09 | PASS |
| t1p5 | 3 | 1.4411424068 | 1.4411424119 | 3.50e-09 | PASS |
| t1p5 | 5 | 1.3525840248 | 1.3525840307 | 4.33e-09 | PASS |
| skewnormal4 | 1 | 1.5232905828 | 1.5232905828 | 3.17e-11 | PASS |
| skewnormal4 | 2 | 1.2616452914 | 1.2616452914 | 2.53e-12 | PASS |
| skewnormal4 | 3 | 1.1990918600 | 1.1990918600 | 5.83e-12 | PASS |
| skewnormal4 | 5 | 1.1734772946 | 1.1734772946 | 4.18e-12 | PASS |

All Route-Q cells pass: **True**.

The uniform family is the deliberate negative control.  Its a.e. interior score is identically zero, so the score side is exactly `0.0`, while the exact map slope is `-2.366025` (quadrature: `-2.366025`).  The identity is **false** there, as `PROOF.md` Section 9 proves.

The Laplace cell additionally has a closed form with an unbounded horizon: `Gamma_1 = (c+b)/b = 3.8284271247` and `g_1(e) = -(c+b) tanh(e/b)`.  It is interval-certified in `certificates/certificate.json`.

## 2. Route N -- neutrality control

Corollary G2 says a deterministic stopping rule has gain exactly one for **every** regular location family and every window length.  This exercises the score, the window average and the random denominator against a known answer, and it is the control that a sign or normalisation error in any family would break.

All 72 cells pass (`all_pass = True`); the largest deviation from one is `t1p5`, `tau = 2`, `m = 2`: `Gamma = 1.00605 +- 0.00229`, `|z| = 2.64`.

## 3. Routes A and B under the frozen detector recursions

Route A evaluates `Gamma = E_0[A_m sum psi(Z_t)]`.  Route B is a common-random-number central difference of the conditional-mean map with per-batch Richardson extrapolation; it uses no likelihood, no score and no change of measure.  The frozen gate is the 3% relative discrepancy limit inherited from the Track-3 location-family campaign, with `|z| <= 4` as the secondary criterion.

### 3.1 `reduced` layer (cusum@2, sr@20)

| detector | family | class | m | ARL | Route A | Route B | relative | \|z\| | verdict |
|---|---|---|---|---|---|---|---|---|---|
| cusum@2 | gaussian | TS | 1 | 19.3 | 6.1982 ± 0.0026 | 6.1946 ± 0.0154 | 0.057% | 0.23 | PASS |
| cusum@2 | gaussian | TS | 2 | 19.3 | 4.7251 ± 0.0020 | 4.7199 ± 0.0114 | 0.110% | 0.45 | PASS |
| cusum@2 | gaussian | TS | 3 | 19.3 | 3.7611 ± 0.0015 | 3.7571 ± 0.0092 | 0.106% | 0.43 | PASS |
| cusum@2 | gaussian | TS | 5 | 19.3 | 2.7542 ± 0.0012 | 2.7558 ± 0.0059 | 0.057% | 0.26 | PASS |
| cusum@2 | laplace | TS | 1 | 19.5 | 4.9834 ± 0.0050 | 5.0174 ± 0.0138 | 0.678% | 2.31 | PASS |
| cusum@2 | laplace | TS | 2 | 19.5 | 3.5407 ± 0.0030 | 3.5653 ± 0.0087 | 0.691% | 2.68 | PASS |
| cusum@2 | laplace | TS | 3 | 19.5 | 2.8781 ± 0.0022 | 2.8939 ± 0.0069 | 0.547% | 2.19 | PASS |
| cusum@2 | laplace | TS | 5 | 19.5 | 2.2249 ± 0.0014 | 2.2363 ± 0.0049 | 0.512% | 2.24 | PASS |
| cusum@2 | logistic | TS | 1 | 19.5 | 5.6204 ± 0.0044 | 5.6105 ± 0.0124 | 0.176% | 0.76 | PASS |
| cusum@2 | logistic | TS | 2 | 19.5 | 4.1603 ± 0.0028 | 4.1526 ± 0.0086 | 0.184% | 0.85 | PASS |
| cusum@2 | logistic | TS | 3 | 19.5 | 3.3536 ± 0.0020 | 3.3461 ± 0.0070 | 0.225% | 1.04 | PASS |
| cusum@2 | logistic | TS | 5 | 19.5 | 2.5176 ± 0.0015 | 2.5135 ± 0.0055 | 0.163% | 0.72 | PASS |
| cusum@2 | t3 | TS | 1 | 29.1 | 4.7856 ± 0.0093 | 4.7855 ± 0.0154 | 0.003% | 0.01 | PASS |
| cusum@2 | t3 | TS | 2 | 29.1 | 3.4814 ± 0.0056 | 3.4902 ± 0.0098 | 0.251% | 0.78 | PASS |
| cusum@2 | t3 | TS | 3 | 29.1 | 2.8655 ± 0.0038 | 2.8759 ± 0.0066 | 0.361% | 1.36 | PASS |
| cusum@2 | t3 | TS | 5 | 29.1 | 2.2285 ± 0.0025 | 2.2351 ± 0.0042 | 0.296% | 1.35 | PASS |
| cusum@2 | t1p5 | TS | 1 | 4.8 | 2.5657 ± 0.0544 | 2.4957 ± 0.1217 | 2.727% | 0.52 | PASS |
| cusum@2 | t1p5 | TS | 2 | 4.8 | 1.8961 ± 0.0271 | 1.8618 ± 0.0613 | 1.806% | 0.51 | PASS |
| cusum@2 | t1p5 | TS | 3 | 4.8 | 1.6512 ± 0.0252 | 1.6197 ± 0.0408 | 1.907% | 0.66 | PASS |
| cusum@2 | t1p5 | TS | 5 | 4.8 | 1.4804 ± 0.0242 | 1.4517 ± 0.0249 | 1.936% | 0.83 | PASS |
| cusum@2 | skewnormal4 | TS | 1 | 20.1 | 6.1563 ± 0.0046 | 6.1450 ± 0.0149 | 0.184% | 0.73 | PASS |
| cusum@2 | skewnormal4 | TS | 2 | 20.1 | 4.6974 ± 0.0030 | 4.6919 ± 0.0106 | 0.118% | 0.50 | PASS |
| cusum@2 | skewnormal4 | TS | 3 | 20.1 | 3.8373 ± 0.0025 | 3.8318 ± 0.0078 | 0.143% | 0.67 | PASS |
| cusum@2 | skewnormal4 | TS | 5 | 20.1 | 2.8224 ± 0.0017 | 2.8194 ± 0.0052 | 0.105% | 0.54 | PASS |
| cusum@2 | uniform | OA | 1 | 19.9 | 0.0000 ± 0.0000 | 6.9944 ± 0.0103 | 100.000% | 680.25 | COUNTEREXAMPLE-CONFIRMED |
| cusum@2 | uniform | OA | 2 | 19.9 | 0.0000 ± 0.0000 | 6.3258 ± 0.0095 | 100.000% | 664.61 | COUNTEREXAMPLE-CONFIRMED |
| cusum@2 | uniform | OA | 3 | 19.9 | 0.0000 ± 0.0000 | 4.8368 ± 0.0072 | 100.000% | 674.63 | COUNTEREXAMPLE-CONFIRMED |
| cusum@2 | uniform | OA | 5 | 19.9 | 0.0000 ± 0.0000 | 3.3123 ± 0.0049 | 100.000% | 676.80 | COUNTEREXAMPLE-CONFIRMED |
| cusum@2 | cauchy | OA | 1 | 3.7 | -2.9967 ± 6.8209 | 14.1811 ± 8.2607 | 121.132% | 1.60 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| cusum@2 | cauchy | OA | 2 | 3.7 | -0.9407 ± 3.4104 | 7.6428 ± 4.1295 | 112.309% | 1.60 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| cusum@2 | cauchy | OA | 3 | 3.7 | -0.3458 ± 2.2764 | 5.4304 ± 2.7548 | 106.368% | 1.62 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| cusum@2 | cauchy | OA | 5 | 3.7 | 0.2915 ± 1.3964 | 3.7025 ± 1.6525 | 92.127% | 1.58 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| sr@20 | gaussian | TS | 1 | 18.3 | 6.4278 ± 0.0022 | 6.4329 ± 0.0129 | 0.080% | 0.39 | PASS |
| sr@20 | gaussian | TS | 2 | 18.3 | 4.8205 ± 0.0016 | 4.8201 ± 0.0103 | 0.009% | 0.04 | PASS |
| sr@20 | gaussian | TS | 3 | 18.3 | 3.8502 ± 0.0013 | 3.8500 ± 0.0079 | 0.005% | 0.02 | PASS |
| sr@20 | gaussian | TS | 5 | 18.3 | 2.7834 ± 0.0010 | 2.7800 ± 0.0053 | 0.119% | 0.62 | PASS |
| sr@20 | laplace | TS | 1 | 19.3 | 6.0968 ± 0.0054 | 6.1245 ± 0.0163 | 0.453% | 1.61 | PASS |
| sr@20 | laplace | TS | 2 | 19.3 | 4.1602 ± 0.0034 | 4.1798 ± 0.0114 | 0.468% | 1.65 | PASS |
| sr@20 | laplace | TS | 3 | 19.3 | 3.3143 ± 0.0025 | 3.3286 ± 0.0089 | 0.429% | 1.55 | PASS |
| sr@20 | laplace | TS | 5 | 19.3 | 2.4819 ± 0.0016 | 2.4919 ± 0.0061 | 0.402% | 1.60 | PASS |
| sr@20 | logistic | TS | 1 | 18.8 | 6.2692 ± 0.0020 | 6.2612 ± 0.0159 | 0.128% | 0.50 | PASS |
| sr@20 | logistic | TS | 2 | 18.8 | 4.5210 ± 0.0013 | 4.5208 ± 0.0125 | 0.005% | 0.02 | PASS |
| sr@20 | logistic | TS | 3 | 18.8 | 3.6222 ± 0.0011 | 3.6245 ± 0.0092 | 0.063% | 0.25 | PASS |
| sr@20 | logistic | TS | 5 | 18.8 | 2.6680 ± 0.0008 | 2.6694 ± 0.0062 | 0.053% | 0.23 | PASS |
| sr@20 | t3 | TS | 1 | 27.1 | 6.2614 ± 0.0096 | 6.2559 ± 0.0221 | 0.088% | 0.23 | PASS |
| sr@20 | t3 | TS | 2 | 27.1 | 4.3435 ± 0.0052 | 4.3414 ± 0.0123 | 0.048% | 0.16 | PASS |
| sr@20 | t3 | TS | 3 | 27.1 | 3.5035 ± 0.0033 | 3.5063 ± 0.0086 | 0.080% | 0.31 | PASS |
| sr@20 | t3 | TS | 5 | 27.1 | 2.6508 ± 0.0021 | 2.6532 ± 0.0057 | 0.087% | 0.38 | PASS |
| sr@20 | t1p5 | TS | 1 | 5.5 | 2.6818 ± 0.0475 | 2.8311 ± 0.1053 | 5.276% | 1.29 | FAIL |
| sr@20 | t1p5 | TS | 2 | 5.5 | 1.9488 ± 0.0238 | 2.0274 ± 0.0533 | 3.874% | 1.35 | FAIL |
| sr@20 | t1p5 | TS | 3 | 5.5 | 1.6531 ± 0.0229 | 1.7157 ± 0.0358 | 3.645% | 1.47 | FAIL |
| sr@20 | t1p5 | TS | 5 | 5.5 | 1.4344 ± 0.0230 | 1.4807 ± 0.0226 | 3.132% | 1.44 | FAIL |
| sr@20 | skewnormal4 | TS | 1 | 18.9 | 6.7582 ± 0.0035 | 6.7589 ± 0.0161 | 0.011% | 0.04 | PASS |
| sr@20 | skewnormal4 | TS | 2 | 18.9 | 5.0247 ± 0.0023 | 5.0168 ± 0.0107 | 0.157% | 0.72 | PASS |
| sr@20 | skewnormal4 | TS | 3 | 18.9 | 4.0683 ± 0.0017 | 4.0644 ± 0.0085 | 0.094% | 0.44 | PASS |
| sr@20 | skewnormal4 | TS | 5 | 18.9 | 2.9475 ± 0.0012 | 2.9434 ± 0.0065 | 0.141% | 0.63 | PASS |
| sr@20 | uniform | OA | 1 | 18.2 | 0.0000 ± 0.0000 | 6.2899 ± 0.0097 | 100.000% | 650.72 | COUNTEREXAMPLE-CONFIRMED |
| sr@20 | uniform | OA | 2 | 18.2 | 0.0000 ± 0.0000 | 5.4369 ± 0.0077 | 100.000% | 709.22 | COUNTEREXAMPLE-CONFIRMED |
| sr@20 | uniform | OA | 3 | 18.2 | 0.0000 ± 0.0000 | 4.4102 ± 0.0062 | 100.000% | 713.69 | COUNTEREXAMPLE-CONFIRMED |
| sr@20 | uniform | OA | 5 | 18.2 | 0.0000 ± 0.0000 | 3.0366 ± 0.0047 | 100.000% | 641.94 | COUNTEREXAMPLE-CONFIRMED |
| sr@20 | cauchy | OA | 1 | 4.1 | 4.7714 ± 3.0856 | 4.8750 ± 2.2622 | 2.125% | 0.03 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| sr@20 | cauchy | OA | 2 | 4.1 | 2.9329 ± 1.5429 | 2.9836 ± 1.1311 | 1.699% | 0.03 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| sr@20 | cauchy | OA | 3 | 4.1 | 2.2515 ± 1.0837 | 2.3444 ± 0.7547 | 3.959% | 0.07 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| sr@20 | cauchy | OA | 5 | 4.1 | 1.7235 ± 0.7554 | 1.8650 ± 0.4686 | 7.589% | 0.16 | COUNTEREXAMPLE-NOT-DEMONSTRATED |

### 3.2 `frozen` layer (cusum@5, sr@520.886)

| detector | family | class | m | ARL | Route A | Route B | relative | \|z\| | verdict |
|---|---|---|---|---|---|---|---|---|---|
| cusum@5 | gaussian | TS | 1 | 465.5 | 15.8773 ± 0.0168 | 15.8572 ± 0.0466 | 0.127% | 0.41 | PASS |
| cusum@5 | gaussian | TS | 2 | 465.5 | 13.2475 ± 0.0151 | 13.2302 ± 0.0364 | 0.130% | 0.44 | PASS |
| cusum@5 | gaussian | TS | 3 | 465.5 | 11.9147 ± 0.0137 | 11.9109 ± 0.0312 | 0.032% | 0.11 | PASS |
| cusum@5 | gaussian | TS | 5 | 465.5 | 10.1842 ± 0.0121 | 10.1814 ± 0.0260 | 0.028% | 0.10 | PASS |
| cusum@5 | laplace | TS | 1 | 276.4 | 13.0220 ± 0.0501 | 12.9869 ± 0.0472 | 0.269% | 0.51 | PASS |
| cusum@5 | laplace | TS | 2 | 276.4 | 9.5496 ± 0.0305 | 9.5312 ± 0.0299 | 0.193% | 0.43 | PASS |
| cusum@5 | laplace | TS | 3 | 276.4 | 8.0495 ± 0.0238 | 8.0313 ± 0.0248 | 0.227% | 0.53 | PASS |
| cusum@5 | laplace | TS | 5 | 276.4 | 6.3917 ± 0.0193 | 6.3724 ± 0.0184 | 0.301% | 0.72 | PASS |
| cusum@5 | logistic | TS | 1 | 359.4 | 14.5743 ± 0.0217 | 14.5928 ± 0.0508 | 0.126% | 0.33 | PASS |
| cusum@5 | logistic | TS | 2 | 359.4 | 11.4154 ± 0.0151 | 11.3976 ± 0.0353 | 0.156% | 0.46 | PASS |
| cusum@5 | logistic | TS | 3 | 359.4 | 9.9297 ± 0.0124 | 9.9143 ± 0.0290 | 0.155% | 0.49 | PASS |
| cusum@5 | logistic | TS | 5 | 359.4 | 8.1379 ± 0.0087 | 8.1297 ± 0.0239 | 0.101% | 0.32 | PASS |
| cusum@5 | t3 | TS | 1 | 237.1 | 8.0054 ± 0.0712 | 8.0175 ± 0.0625 | 0.151% | 0.13 | PASS |
| cusum@5 | t3 | TS | 2 | 237.1 | 5.5397 ± 0.0348 | 5.5648 ± 0.0315 | 0.451% | 0.54 | PASS |
| cusum@5 | t3 | TS | 3 | 237.1 | 4.5604 ± 0.0258 | 4.5959 ± 0.0235 | 0.772% | 1.02 | PASS |
| cusum@5 | t3 | TS | 5 | 237.1 | 3.5995 ± 0.0147 | 3.6203 ± 0.0159 | 0.575% | 0.96 | PASS |
| cusum@5 | t1p5 | TS | 1 | 11.7 | 3.4825 ± 0.1403 | 3.5959 ± 0.2914 | 3.155% | 0.35 | FAIL |
| cusum@5 | t1p5 | TS | 2 | 11.7 | 2.5210 ± 0.0703 | 2.5834 ± 0.1488 | 2.413% | 0.38 | PASS |
| cusum@5 | t1p5 | TS | 3 | 11.7 | 2.1376 ± 0.0473 | 2.1852 ± 0.0997 | 2.179% | 0.43 | PASS |
| cusum@5 | t1p5 | TS | 5 | 11.7 | 1.7751 ± 0.0291 | 1.8049 ± 0.0600 | 1.653% | 0.45 | PASS |
| cusum@5 | skewnormal4 | TS | 1 | 365.1 | 5.4213 ± 0.0413 | 5.4037 ± 0.0275 | 0.325% | 0.36 | PASS |
| cusum@5 | skewnormal4 | TS | 2 | 365.1 | 4.3086 ± 0.0308 | 4.3314 ± 0.0225 | 0.525% | 0.60 | PASS |
| cusum@5 | skewnormal4 | TS | 3 | 365.1 | 3.8606 ± 0.0269 | 3.8634 ± 0.0171 | 0.074% | 0.09 | PASS |
| cusum@5 | skewnormal4 | TS | 5 | 365.1 | 3.4946 ± 0.0223 | 3.4930 ± 0.0140 | 0.048% | 0.06 | PASS |
| cusum@5 | uniform | OA | 1 | 672.3 | 0.0000 ± 0.0000 | 16.7089 ± 0.0323 | 100.000% | 516.65 | COUNTEREXAMPLE-CONFIRMED |
| cusum@5 | uniform | OA | 2 | 672.3 | 0.0000 ± 0.0000 | 15.2523 ± 0.0326 | 100.000% | 468.04 | COUNTEREXAMPLE-CONFIRMED |
| cusum@5 | uniform | OA | 3 | 672.3 | 0.0000 ± 0.0000 | 14.2878 ± 0.0298 | 100.000% | 478.77 | COUNTEREXAMPLE-CONFIRMED |
| cusum@5 | uniform | OA | 5 | 672.3 | 0.0000 ± 0.0000 | 13.0976 ± 0.0279 | 100.000% | 470.01 | COUNTEREXAMPLE-CONFIRMED |
| cusum@5 | cauchy | OA | 1 | 6.9 | 29.9280 ± 22.3223 | 8.8524 ± 10.3439 | 70.421% | 0.86 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| cusum@5 | cauchy | OA | 2 | 6.9 | 15.5904 ± 11.1614 | 5.0454 ± 5.1721 | 67.638% | 0.86 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| cusum@5 | cauchy | OA | 3 | 6.9 | 10.6653 ± 7.4748 | 3.7577 ± 3.4472 | 64.767% | 0.84 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| cusum@5 | cauchy | OA | 5 | 6.9 | 6.4822 ± 4.6007 | 2.7083 ± 2.0684 | 58.219% | 0.75 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| sr@520.886 | gaussian | TS | 1 | 465.2 | 17.2589 ± 0.0203 | 17.2385 ± 0.0341 | 0.118% | 0.51 | PASS |
| sr@520.886 | gaussian | TS | 2 | 465.2 | 14.3586 ± 0.0161 | 14.3243 ± 0.0284 | 0.239% | 1.05 | PASS |
| sr@520.886 | gaussian | TS | 3 | 465.2 | 12.8313 ± 0.0130 | 12.8006 ± 0.0258 | 0.239% | 1.06 | PASS |
| sr@520.886 | gaussian | TS | 5 | 465.2 | 10.9230 ± 0.0097 | 10.9118 ± 0.0221 | 0.102% | 0.46 | PASS |
| sr@520.886 | laplace | TS | 1 | 297.5 | 16.0790 ± 0.0493 | 16.0747 ± 0.0601 | 0.027% | 0.06 | PASS |
| sr@520.886 | laplace | TS | 2 | 297.5 | 11.5902 ± 0.0360 | 11.6026 ± 0.0361 | 0.107% | 0.24 | PASS |
| sr@520.886 | laplace | TS | 3 | 297.5 | 9.6624 ± 0.0263 | 9.6793 ± 0.0285 | 0.175% | 0.44 | PASS |
| sr@520.886 | laplace | TS | 5 | 297.5 | 7.6115 ± 0.0178 | 7.6258 ± 0.0201 | 0.188% | 0.53 | PASS |
| sr@520.886 | logistic | TS | 1 | 374.6 | 16.8196 ± 0.0193 | 16.8879 ± 0.0543 | 0.405% | 1.19 | PASS |
| sr@520.886 | logistic | TS | 2 | 374.6 | 13.0425 ± 0.0133 | 13.0660 ± 0.0398 | 0.180% | 0.56 | PASS |
| sr@520.886 | logistic | TS | 3 | 374.6 | 11.2627 ± 0.0105 | 11.2933 ± 0.0324 | 0.272% | 0.90 | PASS |
| sr@520.886 | logistic | TS | 5 | 374.6 | 9.2044 ± 0.0083 | 9.2333 ± 0.0261 | 0.313% | 1.05 | PASS |
| sr@520.886 | t3 | TS | 1 | 257.2 | 11.2480 ± 0.0973 | 11.0345 ± 0.0654 | 1.898% | 1.82 | PASS |
| sr@520.886 | t3 | TS | 2 | 257.2 | 7.4351 ± 0.0513 | 7.3287 ± 0.0397 | 1.432% | 1.64 | PASS |
| sr@520.886 | t3 | TS | 3 | 257.2 | 5.9639 ± 0.0334 | 5.8962 ± 0.0289 | 1.135% | 1.53 | PASS |
| sr@520.886 | t3 | TS | 5 | 257.2 | 4.5623 ± 0.0230 | 4.5307 ± 0.0194 | 0.691% | 1.05 | PASS |
| sr@520.886 | t1p5 | TS | 1 | 13.1 | 4.1276 ± 0.0956 | 3.0694 ± 0.7160 | 25.637% | 1.47 | FAIL |
| sr@520.886 | t1p5 | TS | 2 | 13.1 | 2.8573 ± 0.0477 | 2.3225 ± 0.3567 | 18.717% | 1.49 | FAIL |
| sr@520.886 | t1p5 | TS | 3 | 13.1 | 2.3668 ± 0.0321 | 2.0187 ± 0.2390 | 14.706% | 1.44 | FAIL |
| sr@520.886 | t1p5 | TS | 5 | 13.1 | 1.9109 ± 0.0204 | 1.6998 ± 0.1438 | 11.044% | 1.45 | FAIL |
| sr@520.886 | skewnormal4 | TS | 1 | 396.0 | 7.9390 ± 0.0387 | 8.1256 ± 0.0366 | 2.296% | 3.50 | PASS |
| sr@520.886 | skewnormal4 | TS | 2 | 396.0 | 6.3875 ± 0.0284 | 6.5561 ± 0.0270 | 2.571% | 4.29 | FAIL |
| sr@520.886 | skewnormal4 | TS | 3 | 396.0 | 5.6509 ± 0.0254 | 5.7814 ± 0.0242 | 2.257% | 3.72 | PASS |
| sr@520.886 | skewnormal4 | TS | 5 | 396.0 | 4.8861 ± 0.0209 | 4.9869 ± 0.0211 | 2.020% | 3.39 | PASS |
| sr@520.886 | uniform | OA | 1 | 627.3 | 0.0000 ± 0.0000 | 17.0069 ± 0.0331 | 100.000% | 514.00 | COUNTEREXAMPLE-CONFIRMED |
| sr@520.886 | uniform | OA | 2 | 627.3 | 0.0000 ± 0.0000 | 15.5241 ± 0.0304 | 100.000% | 510.27 | COUNTEREXAMPLE-CONFIRMED |
| sr@520.886 | uniform | OA | 3 | 627.3 | 0.0000 ± 0.0000 | 14.5009 ± 0.0282 | 100.000% | 513.72 | COUNTEREXAMPLE-CONFIRMED |
| sr@520.886 | uniform | OA | 5 | 627.3 | 0.0000 ± 0.0000 | 13.1326 ± 0.0270 | 100.000% | 486.41 | COUNTEREXAMPLE-CONFIRMED |
| sr@520.886 | cauchy | OA | 1 | 7.6 | -15.0396 ± 20.1168 | 69.8539 ± 53.5710 | 121.530% | 1.48 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| sr@520.886 | cauchy | OA | 2 | 7.6 | -6.8993 ± 10.0585 | 35.5489 ± 26.7846 | 119.408% | 1.48 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| sr@520.886 | cauchy | OA | 3 | 7.6 | -4.1230 ± 6.7446 | 24.0908 ± 17.8569 | 117.114% | 1.48 | COUNTEREXAMPLE-NOT-DEMONSTRATED |
| sr@520.886 | cauchy | OA | 5 | 7.6 | -1.8151 ± 4.1426 | 14.9644 ± 10.7123 | 112.129% | 1.46 | COUNTEREXAMPLE-NOT-DEMONSTRATED |

## 4. Finite-difference step diagnostic

A central difference is `O(h^2)` accurate.  Route B therefore runs two steps on the same batches and reports the Richardson combination; this table adds an independent finer pair on the pre-named cells so the `O(h^2)` law is checked rather than assumed.

| layer | detector | family | m | coarse step | fine step | Richardson |
|---|---|---|---|---|---|---|
| reduced | cusum@2 | gaussian | 1 | 6.1729 | 6.1841 | 6.1878 ± 0.0170 |
| reduced | cusum@2 | gaussian | 2 | 4.7104 | 4.7153 | 4.7169 ± 0.0135 |
| reduced | cusum@2 | gaussian | 3 | 3.7523 | 3.7595 | 3.7619 ± 0.0114 |
| reduced | cusum@2 | gaussian | 5 | 2.7527 | 2.7561 | 2.7572 ± 0.0074 |
| reduced | cusum@2 | t3 | 1 | 4.7631 | 4.7745 | 4.7783 ± 0.0276 |
| reduced | cusum@2 | t3 | 2 | 3.4682 | 3.4753 | 3.4777 ± 0.0154 |
| reduced | cusum@2 | t3 | 3 | 2.8579 | 2.8602 | 2.8609 ± 0.0112 |
| reduced | cusum@2 | t3 | 5 | 2.2242 | 2.2257 | 2.2262 ± 0.0074 |

### 4.1 Independent skew-normal SR ladder

Independent adjudication added the finer steps that the original frozen
protocol did not include.  These runs do not replace the frozen cell or alter
its gate.

| run | m | Richardson | combined `|z|` versus original Route A |
|---|---:|---:|---:|
| `.025/.0125`, 960k paths | 2 | `6.5170 ± 0.0391` | 2.68 |
| `.0125/.00625`, 480k paths | 1 | `7.9768 ± 0.0921` | 0.38 |
| `.0125/.00625`, 480k paths | 2 | `6.4342 ± 0.0785` | 0.56 |
| `.0125/.00625`, 480k paths | 3 | `5.6772 ± 0.0661` | 0.37 |
| `.0125/.00625`, 480k paths | 5 | `4.8912 ± 0.0527` | 0.09 |

A fresh 1.6M-path score replay gave `6.4549 ± 0.0452` at `m=2`, only
`0.23` combined standard errors from the smallest-step direct result.  The
original discrepancy is finite-step bias plus Monte Carlo scatter, not a
detector or theorem failure.  The rising small-`h` variance is why the last
line of attack is less precise despite its lower bias.

## 5. Consistency with the closed Gaussian gains

Priority 4 re-implements the frozen CUSUM and SR from scratch.  Its Gaussian cells are therefore an independent check on the closed Priority-1 and Priority-2 Monte Carlo values.  They are a consistency check only: Priority 4 does **not** re-derive, replace or update any frozen number.

| detector | m | closed P1/P2 gain | P4 independent Route A | \|z\| |
|---|---|---|---|---|
| cusum@5 | 1 | 15.9165 | 15.8773 ± 0.0168 | 2.33 |
| cusum@5 | 2 | 13.2648 | 13.2475 ± 0.0151 | 1.15 |
| cusum@5 | 3 | 11.9571 | 11.9147 ± 0.0137 | 3.08 |
| cusum@5 | 5 | 10.2264 | 10.1842 ± 0.0121 | 3.49 |
| sr@520.886 | 1 | 17.4536 | 17.2589 ± 0.0203 | 9.61 |
| sr@520.886 | 2 | 14.5005 | 14.3586 ± 0.0161 | 8.81 |
| sr@520.886 | 3 | 12.9727 | 12.8313 ± 0.0130 | 10.83 |
| sr@520.886 | 5 | 11.0485 | 10.9230 ± 0.0097 | 12.91 |

### 5.1 Independent frozen-P2 implementation replay

The table above uses the original gate statistic, which treats the old P2
Monte Carlo point as exact.  A fresh 1.6M-path replay through the frozen P2
score implementation resolves the implementation question directly:

| m | fresh frozen-P2 implementation | P4 Route A | combined `|z|` |
|---:|---:|---:|---:|
| 1 | `17.3132 ± 0.0363` | `17.2589 ± 0.0203` | 1.31 |
| 2 | `14.4055 ± 0.0309` | `14.3586 ± 0.0161` | 1.35 |
| 3 | `12.8688 ± 0.0268` | `12.8313 ± 0.0130` | 1.26 |
| 5 | `10.9575 ± 0.0210` | `10.9230 ± 0.0097` | 1.49 |

The new run agrees with P4 at every window.  The older 240k-path P2 vector was
a correlated high Monte Carlo realization across `m`; no implementation
mismatch was found.  Its historical point estimates and the literal gate are
not changed.

## 6. Structural diagnostics

The expected short-window correction `E_0[Q_m]` is the quantity Priority 1 proves nonnegative for the Gaussian score.  Theorem G3 shows the pathwise sign is exactly the sign of `T_tau S_tau`, so for a bounded score it need not be nonnegative.  The `m = 1` column is structurally zero (the short event is empty).

| layer | detector | family | `E[Q_5]` | `E[A_5 S]` | `E[B_5 S]` | Gaussian form `E[A_5 T]` |
|---|---|---|---|---|---|---|
| reduced | cusum@2 | gaussian | 0.29395 ± 0.00032 | 2.7542 | 2.4602 | 2.7542 |
| reduced | cusum@2 | laplace | 0.26320 ± 0.00038 | 2.2249 | 1.9617 | 3.0792 |
| reduced | cusum@2 | logistic | 0.27601 ± 0.00028 | 2.5176 | 2.2416 | 2.8948 |
| reduced | cusum@2 | t3 | 0.16803 ± 0.00031 | 2.2285 | 2.0605 | 4.4641 |
| reduced | cusum@2 | t1p5 | 0.61902 ± 0.01402 | 1.4804 | 0.8614 | 9544.4931 |
| reduced | cusum@2 | skewnormal4 | 0.25449 ± 0.00039 | 2.8224 | 2.5679 | 2.5010 |
| reduced | sr@20 | gaussian | 0.14262 ± 0.00028 | 2.7834 | 2.6407 | 2.7834 |
| reduced | sr@20 | laplace | 0.15964 ± 0.00029 | 2.4819 | 2.3222 | 3.1017 |
| reduced | sr@20 | logistic | 0.15148 ± 0.00023 | 2.6680 | 2.5165 | 2.9177 |
| reduced | sr@20 | t3 | 0.10672 ± 0.00026 | 2.6508 | 2.5441 | 4.4060 |
| reduced | sr@20 | t1p5 | 0.48509 ± 0.01460 | 1.4344 | 0.9493 | 9663.0624 |
| reduced | sr@20 | skewnormal4 | 0.13477 ± 0.00033 | 2.9475 | 2.8127 | 2.7514 |
| frozen | cusum@5 | gaussian | 0.00285 ± 0.00010 | 10.1842 | 10.1814 | 10.1842 |
| frozen | cusum@5 | laplace | 0.01513 ± 0.00013 | 6.3917 | 6.3766 | 9.8048 |
| frozen | cusum@5 | logistic | 0.00809 ± 0.00011 | 8.1379 | 8.1298 | 9.9637 |
| frozen | cusum@5 | t3 | 0.02069 ± 0.00019 | 3.5995 | 3.5788 | 15.4995 |
| frozen | cusum@5 | t1p5 | 0.28354 ± 0.00307 | 1.7751 | 1.4915 | 2226.2190 |
| frozen | cusum@5 | skewnormal4 | 0.00757 ± 0.00013 | 3.4946 | 3.4871 | 2.8162 |
| frozen | sr@520.886 | gaussian | 0.00043 ± 0.00003 | 10.9230 | 10.9225 | 10.9230 |
| frozen | sr@520.886 | laplace | 0.00587 ± 0.00012 | 7.6115 | 7.6056 | 10.8207 |
| frozen | sr@520.886 | logistic | 0.00228 ± 0.00005 | 9.2044 | 9.2022 | 10.8707 |
| frozen | sr@520.886 | t3 | 0.01296 ± 0.00014 | 4.5623 | 4.5493 | 16.7802 |
| frozen | sr@520.886 | t1p5 | 0.23261 ± 0.00350 | 1.9109 | 1.6783 | 2752.1007 |
| frozen | sr@520.886 | skewnormal4 | 0.00223 ± 0.00007 | 4.8861 | 4.8839 | 4.1422 |

The last column is what the *Gaussian* formula would report if it were applied unchanged to a non-Gaussian family.  Where it differs from `E[A_m S]`, using the closed Gaussian estimand off its model would give the wrong gain and hence the wrong critical reuse fraction.

## 7. Origin as a fixed point

Theorem G4 needs an even density and a reflection-equivariant detector, and then *proves* `E_0[A_m] = 0`.  The numbers below are a falsification check, not an estimate of something unknown: a symmetric cell should sit within a few standard errors of zero, and a family that violates the hypothesis should miss by orders of magnitude.  The classifier refuses to classify any cell beyond 6 standard errors.

| detector | family | `E_0[A_1]` | \|z\| |
|---|---|---|---|
| cusum@5 | gaussian | -0.00152 ± 0.00138 | 1.1 |
| cusum@5 | laplace | +0.00097 ± 0.00186 | 0.5 |
| cusum@5 | logistic | +0.00054 ± 0.00143 | 0.4 |
| cusum@5 | t3 | +0.00987 ± 0.00310 | 3.2 |
| cusum@5 | t1p5 | +0.01158 ± 0.05575 | 0.2 |
| cusum@5 | skewnormal4 | +2.17287 ± 0.00069 | 3142.9 |
| sr@520.886 | gaussian | -0.00157 ± 0.00118 | 1.3 |
| sr@520.886 | laplace | -0.00157 ± 0.00185 | 0.8 |
| sr@520.886 | logistic | +0.00209 ± 0.00118 | 1.8 |
| sr@520.886 | t3 | +0.00828 ± 0.00296 | 2.8 |
| sr@520.886 | t1p5 | -0.02800 ± 0.06346 | 0.4 |
| sr@520.886 | skewnormal4 | +2.03349 ± 0.00109 | 1870.4 |
