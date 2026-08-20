# Phase-4B Convention Matrix

| Item | Symmetric SR diagnostic | Protected CUSUM control |
|---|---|---|
| Innovation | `Z_t=X_t-e` | `Z_t=X_t-e` |
| In-control law at `e=0` | iid `N(0,1)` | iid `N(0,1)` |
| Update timing | update both arms, then test | update both arms, then test |
| Alarm boundary | inclusive `>=` | inclusive `>=` |
| Terminal observation | current firing increment `Z_tau` | current firing increment `Z_tau` |
| Stopped sum | includes `Z_tau` | includes `Z_tau` |
| Reward | `Z_tau*T_tau` | `Z_tau*T_tau` |
| Direction | larger firing chart; exact tie recorded | firing chart |
| State reset | both charts reset each cycle | both charts reset each cycle |
| Diagnostic seeds | `1729`, `20260818` | `1729` |
| Harness | `StoppingSample.summary` | same `StoppingSample.summary` adapter |
| Proof role | non-rigorous witness only | non-rigorous positive control only |

The CUSUM adapter calls the protected simulator without modifying it. On one
million paths it returns `Gamma=15.8429362`, consistent with the established
`15.87` diagnostic scale. This controls the common reward indexing, stopping
sum, standard-error, seed, and reporting conventions.

The SR scalar log-domain oracle and raw-state replay are independently
structured and agree on all fixed paths, exact/epsilon boundaries, reflection,
overshoot, simultaneous crossing, tie handling, and terminal rewards.
