# Results — CUSUM completion successor

**Verdict: `INCOMPLETE_CERTIFICATE`.**
CUSUM compact-cover status: `INCOMPLETE`.
Not production, not result-bearing, no cell claimed closed beyond its own
certificate.

## Where the block stands

27 of 32 `(cell, m)` obligations over cells 318–325 now certify,
against 12 of 32 before this task. Cell 324 closed completely;
cell 325, the regression control, still passes every `m`
(clean). What remains
open is `m = 5` at cells 319, 320, 321, 322, 323.

Every remaining failure is `CERTIFICATE_TOO_LOOSE`: the certified `R''` interval
straddles zero, so the bound — not the mathematics — is what fails.
No obligation is a SCIENTIFIC_FAILURE and none is an IMPLEMENTATION_DEFECT.

| cell | rho | m | status | classification | cover util | M_R2 | M_R2 needed | still short by |
| ---: | ---: | ---: | :--- | :--- | ---: | ---: | ---: | ---: |
| 318 | 0.10732 | 1 | PASS | CERTIFIED_PASS | 56.08% | 1.4452 | 5.2585 | -- |
| 318 | 0.10732 | 2 | PASS | CERTIFIED_PASS | 43.96% | 2.0813 | 6.9474 | -- |
| 318 | 0.10732 | 3 | PASS | CERTIFIED_PASS | 47.35% | 3.2756 | 7.8471 | -- |
| 318 | 0.10732 | 5 | PASS | CERTIFIED_PASS | 98.29% | 7.8157 | 7.9639 | -- |
| 319 | 0.12280 | 1 | PASS | CERTIFIED_PASS | 57.24% | 1.6081 | 4.4437 | -- |
| 319 | 0.12280 | 2 | PASS | CERTIFIED_PASS | 48.30% | 2.0967 | 5.5251 | -- |
| 319 | 0.12280 | 3 | PASS | CERTIFIED_PASS | 53.34% | 3.1804 | 6.2748 | -- |
| 319 | 0.12280 | 5 | FAIL | CERTIFICATE_TOO_LOOSE | 115.29% | 7.3311 | 6.3171 | 1.161x |
| 320 | 0.13650 | 1 | PASS | CERTIFIED_PASS | 41.08% | 1.5870 | 4.7494 | -- |
| 320 | 0.13650 | 2 | PASS | CERTIFIED_PASS | 42.64% | 1.9730 | 5.0513 | -- |
| 320 | 0.13650 | 3 | PASS | CERTIFIED_PASS | 58.87% | 2.9000 | 5.1076 | -- |
| 320 | 0.13650 | 5 | FAIL | CERTIFICATE_TOO_LOOSE | 125.78% | 6.4771 | 5.0937 | 1.272x |
| 321 | 0.14657 | 1 | PASS | CERTIFIED_PASS | 50.96% | 1.3839 | 3.6667 | -- |
| 321 | 0.14657 | 2 | PASS | CERTIFIED_PASS | 48.53% | 1.7616 | 4.1574 | -- |
| 321 | 0.14657 | 3 | PASS | CERTIFIED_PASS | 72.27% | 2.5152 | 3.8059 | -- |
| 321 | 0.14657 | 5 | FAIL | CERTIFICATE_TOO_LOOSE | 133.53% | 5.3630 | 3.8023 | 1.410x |
| 322 | 0.15250 | 1 | PASS | CERTIFIED_PASS | 71.28% | 0.9809 | 2.2159 | -- |
| 322 | 0.15250 | 2 | PASS | CERTIFIED_PASS | 57.76% | 1.4394 | 3.2556 | -- |
| 322 | 0.15250 | 3 | PASS | CERTIFIED_PASS | 75.87% | 2.0367 | 3.0742 | -- |
| 322 | 0.15250 | 5 | FAIL | CERTIFICATE_TOO_LOOSE | 123.90% | 4.1011 | 3.0734 | 1.334x |
| 323 | 0.15525 | 1 | PASS | CERTIFIED_PASS | 74.78% | 0.8241 | 1.8707 | -- |
| 323 | 0.15525 | 2 | PASS | CERTIFIED_PASS | 57.46% | 1.2424 | 3.0072 | -- |
| 323 | 0.15525 | 3 | PASS | CERTIFIED_PASS | 70.91% | 1.7247 | 2.9317 | -- |
| 323 | 0.15525 | 5 | FAIL | CERTIFICATE_TOO_LOOSE | 104.29% | 3.1094 | 2.9313 | 1.061x |
| 324 | 0.15627 | 1 | PASS | CERTIFIED_PASS | 60.22% | 0.9402 | 2.5694 | -- |
| 324 | 0.15627 | 2 | PASS | CERTIFIED_PASS | 47.24% | 1.1699 | 3.3306 | -- |
| 324 | 0.15627 | 3 | PASS | CERTIFIED_PASS | 55.69% | 1.4906 | 3.3053 | -- |
| 324 | 0.15627 | 5 | PASS | CERTIFIED_PASS | 75.48% | 2.3010 | 3.3052 | -- |
| 325 | 0.09624 | 1 | PASS | CERTIFIED_PASS | 12.81% | 0.6741 | 10.0877 | -- |
| 325 | 0.09624 | 2 | PASS | CERTIFIED_PASS | 9.21% | 0.6384 | 10.4407 | -- |
| 325 | 0.09624 | 3 | PASS | CERTIFIED_PASS | 10.37% | 0.7500 | 10.4262 | -- |
| 325 | 0.09624 | 5 | PASS | CERTIFIED_PASS | 12.71% | 1.0025 | 10.4262 | -- |

## Against the predecessor (`f8e6f75`)

| cell | m | predecessor | this successor | improvement |
| ---: | ---: | :--- | :--- | ---: |
| 318 | 1 | 79.12% PASS | 56.08% PASS | 1.41x |
| 318 | 2 | 84.99% PASS | 43.96% PASS | 1.93x |
| 318 | 3 | 104.76% FAIL | 47.35% PASS | 2.21x |
| 318 | 5 | 182.59% FAIL | 98.29% PASS | 1.86x |
| 319 | 1 | 86.11% PASS | 57.24% PASS | 1.50x |
| 319 | 2 | 99.91% PASS | 48.30% PASS | 2.07x |
| 319 | 3 | 124.56% FAIL | 53.34% PASS | 2.34x |
| 319 | 5 | 218.38% FAIL | 115.29% FAIL | 1.89x |
| 320 | 1 | 75.28% PASS | 41.08% PASS | 1.83x |
| 320 | 2 | 102.93% FAIL | 42.64% PASS | 2.41x |
| 320 | 3 | 140.35% FAIL | 58.87% PASS | 2.38x |
| 320 | 5 | 239.68% FAIL | 125.78% FAIL | 1.91x |
| 321 | 1 | 86.19% PASS | 50.96% PASS | 1.69x |
| 321 | 2 | 110.86% FAIL | 48.53% PASS | 2.28x |
| 321 | 3 | 155.30% FAIL | 72.27% PASS | 2.15x |
| 321 | 5 | 245.11% FAIL | 133.53% FAIL | 1.84x |
| 322 | 1 | 103.97% FAIL | 71.28% PASS | 1.46x |
| 322 | 2 | 114.93% FAIL | 57.76% PASS | 1.99x |
| 322 | 3 | 149.77% FAIL | 75.87% PASS | 1.97x |
| 322 | 5 | 218.92% FAIL | 123.90% FAIL | 1.77x |
| 323 | 1 | 105.49% FAIL | 74.78% PASS | 1.41x |
| 323 | 2 | 108.93% FAIL | 57.46% PASS | 1.90x |
| 323 | 3 | 134.57% FAIL | 70.91% PASS | 1.90x |
| 323 | 5 | 181.39% FAIL | 104.29% FAIL | 1.74x |
| 324 | 1 | 88.20% PASS | 60.22% PASS | 1.46x |
| 324 | 2 | 92.20% PASS | 47.24% PASS | 1.95x |
| 324 | 3 | 108.77% FAIL | 55.69% PASS | 1.95x |
| 324 | 5 | 135.39% FAIL | 75.48% PASS | 1.79x |
| 325 | 1 | 18.04% PASS | 12.81% PASS | 1.41x |
| 325 | 2 | 17.24% PASS | 9.21% PASS | 1.87x |
| 325 | 3 | 19.59% PASS | 10.37% PASS | 1.89x |
| 325 | 5 | 22.75% PASS | 12.71% PASS | 1.79x |

## Provenance

| | |
| --- | --- |
| producer hash | `bda92461332249511b00e676b23d8e448f8b7ad768cddb5616584dac85f97d12` |
| identity kind | `cusum_successor_producer_manifest_v1` |
| manifest files | 47 |
| backend hash | `a556e1ea7d7136382fd0777f3a5d0a56aa7f30e8475925b86bbdad09035da0b8` |
| loaded-module coverage | complete |
| per-cell chains verified | 8 of 8, 28 obligations each |

## Determinism

The adjudicated predecessor defect was that repeated fresh runs under the same
producer identity produced different certificate hashes. Fresh repeats here, in
separate processes and a separate output directory, reproduce the recorded
scientific hash exactly while their runtime fields differ — which is what makes
the comparison meaningful rather than a file copy.

| cell | recorded scientific hash | fresh repeat | identical | CPU seconds (recorded / repeat) |
| ---: | :--- | :--- | :--- | :--- |
| 318 | `a3153b2678357148` | `a3153b2678357148` | yes | 2637 / 1302 |
| 323 | `41b02326a5e63a60` | `41b02326a5e63a60` | yes | 2670 / 1310 |

## Cost

`COST_CAP` remains **NOT_ESTABLISHED**. Measured here, and only here:
5.895 CPU-hours over 8 cells
(mean 2652.8 s, max 2681.5 s per cell,
BLAS and FLINT pinned to one thread, 8 workers on 8 cores).

Those per-cell seconds are **inflated by a factor of
2.03**: the determinism repeats ran
the same cells with 2 workers instead of 8 and cost about half the CPU seconds,
because the counter charges memory-bandwidth stalls. Neither number is a per-cell
cost model, and this is a measurement, not a projection:
only 8 of 326 CUSUM cells were certified in this task, and 0 of 316 SR cells; per-cell cost varies strongly with rho and with how many objects need the order-2 path, so these 8 do not extrapolate.

## What would close the rest

The dominant term is the propagated source error — at cell 321, `r = 4`,
`C * epsS2 = 5.254` of `epsH = 9.145`. It is a pure cascade through the frozen
DAG, multiplying by `k_0 + 2k_1 + k_2 = 2.98` per level from an irreducible
`rho * sup_cell|phi''|` seed. Tightening it needs certified midpoint objects one
derivative order above what the frozen object set carries (`h^(3)`, `S^(3)`).
Adding them changes the frozen obligation universe, which is out of scope for
this task; the norm-only substitute is far weaker and does not help
(`diagnostics/third_order_analysis.py`).
