# Frozen P3 policy definition

The sole confirmatory policy is

`rho_P3(m) = min(1, 0.8 * rho_c,L95(m))`.

`rho_c,L95(m)` is read from the lower endpoint of the protected D4 95%
confidence interval. The fixed `0.8` factor is an uncertainty-aware 20% safety
margin and is not a performance parameter. It was frozen before any
confirmatory monitoring outcome and cannot be tuned afterward.

| m | rho_c,L95 | 0.8 rho_c,L95 | P3 action |
|---:|---:|---:|---:|
| 1 | 0.06705273502486477 | 0.05364218801989182 | 0.05364218801989182 |
| 20 | 0.3067722549504311 | 0.24541780396034488 | 0.24541780396034488 |
| 70 | 0.9774919431834009 | 0.7819935545467208 | 0.7819935545467208 |
| 100 | 1.2827906445813966 | 1.0262325156651174 | 1.0 |

The `m=100` unit action is produced by the common clipping rule. It is not an
override. D4 point estimates are descriptive only and are not evaluated as a
policy. There is no P4 and no semi-real task.
