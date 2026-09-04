### Design phase — 20 replicates × 6 cells

| rule | third state possible | attained | funded | `PRECISION_LIMITED` | `UNRESOLVED` | p_attain (funded) | 95% CP lower | p_attain (uncond.) | mean × | max × |
|---|---|---|---|---|---|---|---|---|---|---|
| `A_oneshot_one_topup` | YES | 105 | 105 | 15 | **0** | 1.0000 | 0.9719 | 0.875 | 1.28 | 5.96 |
| `B_oneshot_safety_1.15` | YES | 95 | 97 | 23 | **2** | 0.9794 | 0.9365 | 0.792 | 1.39 | 5.46 |
| `B_oneshot_safety_1.30` | YES | 94 | 94 | 26 | **0** | 1.0000 | 0.9686 | 0.783 | 1.60 | 5.67 |
| `B_oneshot_safety_1.50` | YES | 87 | 87 | 33 | **0** | 1.0000 | 0.9662 | 0.725 | 1.79 | 5.96 |
| `C_staged_safety_1.00` | no | 105 | 105 | 15 | **0** | 1.0000 | 0.9719 | 0.875 | 1.28 | 5.96 |
| `C_staged_safety_1.15` | no | 97 | 97 | 23 | **0** | 1.0000 | 0.9696 | 0.808 | 1.42 | 5.58 |
| `C_staged_safety_1.30` | no | 94 | 94 | 26 | **0** | 1.0000 | 0.9686 | 0.783 | 1.60 | 5.67 |
| `D_staged_quantile_0.95` | no | 95 | 95 | 25 | **0** | 1.0000 | 0.9690 | 0.792 | 1.62 | 6.00 |
| `D_staged_quantile_0.99` | no | 91 | 91 | 29 | **0** | 1.0000 | 0.9676 | 0.758 | 1.84 | 5.96 |

### Validation phase — 59 replicates × 6 cells

| rule | third state possible | attained | funded | `PRECISION_LIMITED` | `UNRESOLVED` | p_attain (funded) | 95% CP lower | p_attain (uncond.) | mean × | max × |
|---|---|---|---|---|---|---|---|---|---|---|
| `A_oneshot_one_topup` | YES | 273 | 282 | 72 | **9** | 0.9681 | 0.9450 | 0.771 | 1.13 | 5.67 |
| `B_oneshot_safety_1.15` | YES | 262 | 264 | 90 | **2** | 0.9924 | 0.9763 | 0.740 | 1.40 | 5.96 |
| `B_oneshot_safety_1.30` | YES | 247 | 248 | 106 | **1** | 0.9960 | 0.9810 | 0.698 | 1.58 | 6.00 |
| `B_oneshot_safety_1.50` | YES | 231 | 231 | 123 | **0** | 1.0000 | 0.9871 | 0.653 | 1.68 | 5.96 |
| `C_staged_safety_1.00` | no | 282 | 282 | 72 | **0** | 1.0000 | 0.9894 | 0.797 | 1.14 | 5.67 |
| `C_staged_safety_1.15` | no | 264 | 264 | 90 | **0** | 1.0000 | 0.9887 | 0.746 | 1.41 | 5.96 |
| `C_staged_safety_1.30` | no | 248 | 248 | 106 | **0** | 1.0000 | 0.9880 | 0.701 | 1.59 | 6.00 |
| `D_staged_quantile_0.95` | no | 261 | 261 | 93 | **0** | 1.0000 | 0.9886 | 0.737 | 1.68 | 5.96 |
| `D_staged_quantile_0.99` | no | 248 | 248 | 106 | **0** | 1.0000 | 0.9880 | 0.701 | 1.83 | 5.96 |

### Unbiased nominal-attainment check

| cell | configuration | route | realised ≤ true at B = 12 | fraction |
|---|---|---|---|---|
| `C1` | `reduced/cusum@2/t1p5` | A | 54 / 79 | 0.684 |
| `C2` | `reduced/cusum@2/t1p5` | B | 54 / 79 | 0.684 |
| `C3` | `reduced/sr@20/t1p5` | A | 60 / 79 | 0.759 |
| `C4` | `reduced/sr@20/t1p5` | B | 71 / 79 | 0.899 |
| `C5` | `reduced/cusum@2/gaussian` | B | 35 / 79 | 0.443 |
| `C6` | `reduced/cusum@2/t1p5` | A | 61 / 79 | 0.772 |
| **pooled** | | | **335 / 474** | **0.707** |

### Cost tail (AMENDMENT 1, 16× cap)

| cell | route | rule | attained / 24 | mean × | q50 × | q90 × | q95 × | max × | oracle q90 × | oracle max × |
|---|---|---|---|---|---|---|---|---|---|---|
| `C1` | A | `A_oneshot_one_topup` | 18 / 24 | 3.11 | 2.29 | 7.75 | 9.25 | 13.04 | 1.54 | 2.83 |
| `C1` | A | `C_staged_safety_1.00` | 19 / 24 | 3.11 | 2.29 | 7.75 | 9.25 | 13.04 | 1.54 | 2.83 |
| `C1` | A | `D_staged_quantile_0.95` | 19 / 24 | 3.21 | 2.00 | 7.83 | 8.83 | 11.12 | 1.54 | 2.83 |
| `C3` | A | `A_oneshot_one_topup` | 19 / 24 | 2.09 | 0.83 | 5.08 | 6.42 | 13.42 | 1.25 | 3.46 |
| `C3` | A | `C_staged_safety_1.00` | 19 / 24 | 2.09 | 0.83 | 5.08 | 6.42 | 13.42 | 1.25 | 3.46 |
| `C3` | A | `D_staged_quantile_0.95` | 19 / 24 | 3.29 | 1.25 | 10.79 | 11.00 | 15.88 | 1.25 | 3.46 |
| `C2` | B | `A_oneshot_one_topup` | 19 / 24 | 1.87 | 1.21 | 5.04 | 6.17 | 6.46 | 0.92 | 3.21 |
| `C2` | B | `C_staged_safety_1.00` | 22 / 24 | 2.05 | 1.54 | 5.04 | 6.17 | 6.46 | 0.92 | 3.21 |
| `C2` | B | `D_staged_quantile_0.95` | 22 / 24 | 4.26 | 2.50 | 8.17 | 15.25 | 16.00 | 0.92 | 3.21 |
| `C4` | B | `A_oneshot_one_topup` | 22 / 24 | 2.48 | 0.50 | 6.79 | 11.08 | 15.62 | 1.21 | 1.67 |
| `C4` | B | `C_staged_safety_1.00` | 22 / 24 | 2.48 | 0.50 | 6.79 | 11.08 | 15.62 | 1.21 | 1.67 |
| `C4` | B | `D_staged_quantile_0.95` | 21 / 24 | 1.92 | 0.50 | 5.92 | 6.38 | 13.46 | 1.21 | 1.67 |
| `C6` | A | `A_oneshot_one_topup` | 20 / 24 | 1.85 | 0.54 | 4.96 | 8.33 | 10.38 | 0.88 | 1.46 |
| `C6` | A | `C_staged_safety_1.00` | 21 / 24 | 2.19 | 0.54 | 8.33 | 9.17 | 10.38 | 0.88 | 1.46 |
| `C6` | A | `D_staged_quantile_0.95` | 19 / 24 | 2.39 | 0.75 | 8.62 | 9.42 | 12.33 | 0.88 | 1.46 |
| `C5` | B | `A_oneshot_one_topup` | 24 / 24 | 1.40 | 1.42 | 1.88 | 2.04 | 2.67 | 1.42 | 1.83 |
| `C5` | B | `C_staged_safety_1.00` | 24 / 24 | 1.40 | 1.42 | 1.88 | 2.04 | 2.67 | 1.42 | 1.83 |
| `C5` | B | `D_staged_quantile_0.95` | 24 / 24 | 2.39 | 2.46 | 3.08 | 3.67 | 4.79 | 1.42 | 1.83 |

### Cost tail pooled

| rule | attained / n | 95% CP lower | mean × | q95 × | max × |
|---|---|---|---|---|---|
| `A_oneshot_one_topup` | 122 / 144 | 0.7891 | 2.13 | 7.75 | 15.62 |
| `C_staged_safety_1.00` | 127 / 144 | 0.8282 | 2.22 | 8.33 | 15.62 |
| `D_staged_quantile_0.95` | 124 / 144 | 0.8046 | 2.91 | 10.79 | 16.00 |
