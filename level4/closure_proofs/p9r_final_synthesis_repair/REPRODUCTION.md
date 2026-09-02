# P9R reproduction — corrected SR recurrence against authoritative P7 cells

Generator: `experiments/run_reproduction.py`. Targets are read at run time from
`level4/closure_proofs/p7_statistical_consequences/results/consequences.json`;
nothing is transcribed by hand, and `n_rep = 5000`, `n_cycles = 50`,
`burn_in = 12` are taken from the matching P7 cell. The implementation shares
no code with P1-P9. Comparison is by the combined-SE `z` statistic; the word
"exact agreement" is not used anywhere in this document.

## 1. The recurrence repair (deterministic, no Monte Carlo)

`results/sr_recurrence_check.json`, six checks, `all_pass = true`.

| check | result |
|---|---|
| `C1` first step from the reset state | `log R_1 = Z_1 - 1/2`, matching the direct recurrence with `abs_diff = 0` exactly |
| `C2` first two steps | max abs difference from `R_t = (1+R_{t-1})exp(Z_t-1/2)` below `1e-12` |
| `C3` first step after a cycle reset | identical to `C1`; a reset restores `y = 0` |
| `C4` eight-step path | max abs difference `< 1e-12`; every alarm decision matches the non-log recurrence |
| `C5` the P9 form | first-step statistic exceeds the frozen one by **exactly** `log 2 = 0.6931471805599453` (bitwise equality, not a tolerance) |
| `C6` alarm witness | at `Z = log A + 1/2 - (log 2)/2` the frozen recurrence does **not** alarm at `t = 1` and the P9 form does |

The defect was structural, not a constant: P9 stored the alarm statistic
`ell = log R` in the slot that must hold the state `y = log(1 + R)`, and started
it at `0`, which encodes `R_0 = 1` — a headstart the frozen model does not have.
P9R's module names the two quantities separately so the confusion cannot recur
silently, and keeps the defective update as an explicitly non-scientific
function so its effect can be measured.

## 2. Corrected reproduction — CUSUM

| `m` | `rho` | P9R ARL | P7 ARL | combined SE | `z` | verdict |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 0 | 83.699 ± 0.458 | 83.223 ± 0.435 | 0.632 | +0.75 | `MC_CONSISTENT` |
| 1 | 1 | 50.109 ± 0.317 | 49.910 ± 0.317 | 0.448 | +0.44 | `MC_CONSISTENT` |
| 2 | 0 | 112.362 ± 0.515 | 112.497 ± 0.512 | 0.726 | −0.19 | `MC_CONSISTENT` |
| 2 | 1 | 61.146 ± 0.346 | 61.719 ± 0.352 | 0.493 | −1.16 | `MC_CONSISTENT` |
| 3 | 0 | 132.775 ± 0.538 | 132.983 ± 0.549 | 0.769 | −0.27 | `MC_CONSISTENT` |
| 3 | 1 | 69.938 ± 0.378 | 69.266 ± 0.366 | 0.526 | +1.28 | `MC_CONSISTENT` |
| 5 | 0 | 164.070 ± 0.616 | 162.033 ± 0.603 | 0.862 | +2.36 | `MC_CONSISTENT` |
| 5 | 1 | 80.553 ± 0.404 | 80.047 ± 0.399 | 0.568 | +0.89 | `MC_CONSISTENT` |

`8/8 MC_CONSISTENT`, max `|z| = 2.36`. Fresh (`rho=0`) range `83.70–164.07`
against P7's `83.22–162.03`; full-reuse range `50.11–80.55` against `49.91–80.05`.

## 3. Corrected reproduction — SR

| `m` | `rho` | P9R ARL | P7 ARL | combined SE | `z` | verdict |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 0 | 79.183 ± 0.429 | 79.913 ± 0.428 | 0.606 | −1.20 | `MC_CONSISTENT` |
| 1 | 1 | 48.313 ± 0.305 | 48.364 ± 0.310 | 0.435 | −0.12 | `MC_CONSISTENT` |
| 2 | 0 | 107.208 ± 0.494 | 106.542 ± 0.482 | 0.690 | +0.96 | `MC_CONSISTENT` |
| 2 | 1 | 58.963 ± 0.335 | 59.788 ± 0.340 | 0.478 | −1.73 | `MC_CONSISTENT` |
| 3 | 0 | 127.647 ± 0.531 | 126.885 ± 0.539 | 0.757 | +1.01 | `MC_CONSISTENT` |
| 3 | 1 | 67.282 ± 0.356 | 67.356 ± 0.362 | 0.508 | −0.14 | `MC_CONSISTENT` |
| 5 | 0 | 155.417 ± 0.593 | 156.220 ± 0.574 | 0.825 | −0.97 | `MC_CONSISTENT` |
| 5 | 1 | 77.679 ± 0.377 | 77.707 ± 0.387 | 0.540 | −0.05 | `MC_CONSISTENT` |

`8/8 MC_CONSISTENT`, max `|z| = 1.73`. This is the first SR reproduction in the
Priority-9 lineage run on the frozen no-headstart recurrence.

## 4. Cycle-1 (nominal `A(0)`) and cycle-2 controls

Cycle 1 starts from the perfect reference `e_0 = 0`, so its mean is the nominal
`A(0)` control and must be kept separate from the `rho = 0` mixture.

| detector | P9R cycle-1 range | P7 cycle-1 range | P9R cycle-2 (`rho=1`) | P7 cycle-2 (`rho=1`) |
|---|---|---|---|---|
| CUSUM | 458.6–474.8 | 463.1–473.6 | 5.82–8.70 | 5.60–8.52 |
| SR | 457.6–467.7 | 456.7–471.5 | 6.08–9.35 | 6.28–9.35 |

The cycle-2 collapse — from roughly `460` to under `10` in a single cycle under
full reuse — reproduces closely for both detectors.

## 5. The `log 2` defect, measured

Every SR cell was replayed a second time with the defective P9 update on the
**same seed**, so the comparison is paired.

| `m` | `rho` | corrected | defective | paired difference | paired `z` | defective vs P7 |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 0 | 79.183 | 79.535 | −0.353 ± 0.599 | −0.59 | `MC_CONSISTENT` |
| 1 | 1 | 48.313 | 47.528 | +0.785 ± 0.428 | +1.84 | `MC_CONSISTENT` |
| 2 | 0 | 107.208 | 106.800 | +0.408 ± 0.705 | +0.58 | `MC_CONSISTENT` |
| 2 | 1 | 58.963 | 59.117 | −0.154 ± 0.479 | −0.32 | `MC_CONSISTENT` |
| 3 | 0 | 127.647 | 126.479 | +1.168 ± 0.759 | +1.54 | `MC_CONSISTENT` |
| 3 | 1 | 67.282 | 66.872 | +0.410 ± 0.515 | +0.80 | `MC_CONSISTENT` |
| 5 | 0 | 155.417 | 155.105 | +0.312 ± 0.816 | +0.38 | `MC_CONSISTENT` |
| 5 | 1 | 77.679 | 76.923 | +0.756 ± 0.543 | +1.39 | `MC_CONSISTENT` |

Inverse-variance pooled paired difference **`+0.402 ± 0.200`, `z = +2.01`**;
6 of 8 cells positive.

**Reading this honestly.** The defect is a real correctness defect — it is a
headstart the frozen model does not have, it shifts the whole trajectory upward,
and it demonstrably changes alarm decisions (`C6`). Its measured effect on the
*ARL estimand* is a downward bias of about `0.4` cycles, roughly `0.5%`, in a
systematic direction, which does not reach the campaign's own `3`-SE materiality
threshold in any single cell nor in the pooled statistic. Under the frozen gate
convention:

```text
S5 = IMMATERIAL      for the post-burn-in ARL estimand at n_rep = 5000
                     (pooled |z| = 2.01 < 3)
```

with the explicit caveat that this is **not** a licence to keep the defective
recurrence: the sign is systematic, the effect grows with the frequency of
early alarms (it is largest at `rho = 1`, where entering errors are larger), and
it is unbounded for any per-path, first-step, or short-horizon quantity. The
correct conclusion is that the corrected recurrence should be used, and that
P9's SR *numbers* were not badly wrong even though its SR *implementation* was.

## 6. Burn-in convention (A5)

`results/burnin_sensitivity.json`, `rho = 1`, `n_rep = 5000`, `n_cycles = 50`.

| cell | discard 0 | 1 | 3 | 6 | 10 | **12 (P7)** | 20 |
|---|---:|---:|---:|---:|---:|---:|---:|
| CUSUM `m=1` | 57.34 | 48.96 | 49.33 | 49.56 | 49.57 | **49.58** | 49.95 |
| CUSUM `m=5` | 88.40 | 80.86 | 80.79 | 81.46 | 81.26 | **81.35** | 81.31 |
| SR `m=1` | 55.81 | 47.72 | 48.10 | 48.31 | 48.17 | **48.15** | 48.11 |
| SR `m=5` | 86.05 | 78.14 | 77.89 | 78.57 | 78.37 | **78.39** | 78.29 |

Pooling all cycles inflates the estimate by `8–16%` because the perfect first
cycle is included; beyond a discard of about `3` the estimate is stable to well
under one cycle. P9 reported a `45.21` vs `48.36` gap and explained it as a
burn-in convention effect *after* seeing it. P9R removes the question by
adopting P7's authoritative `burn_in = 12` from the P7 cell itself, and reports
the sensitivity as a diagnostic rather than as an explanation.

## 7. Mixture correspondence (A6)

`results/response_grid.json`. Two independent estimators of the same quantity:
the `rho = 0` chain ARL of §2/§3, and the quadrature mixture
`E_{e~N(0,1/m)}[A(e)]` built from the response grid.

| cell | `A(0)` | mixture `E[A]` ± budget | `rho=0` chain ARL | difference |
|---|---:|---:|---:|---:|
| CUSUM `m=1` | 473.12 | 82.772 ± 0.160 | 83.699 ± 0.458 | −0.93 |
| CUSUM `m=2` | 473.12 | 111.759 ± 0.224 | 112.362 ± 0.515 | −0.60 |
| CUSUM `m=3` | 473.12 | 132.351 ± 0.272 | 132.775 ± 0.538 | −0.42 |
| CUSUM `m=5` | 473.12 | 162.261 ± 0.347 | 164.070 ± 0.616 | −1.81 |
| SR `m=1` | 466.10 | 79.334 ± 0.163 | 79.183 ± 0.429 | +0.15 |
| SR `m=2` | 466.10 | 106.850 ± 0.229 | 107.208 ± 0.494 | −0.36 |
| SR `m=3` | 466.10 | 126.435 ± 0.279 | 127.647 ± 0.531 | −1.21 |
| SR `m=5` | 466.10 | 154.986 ± 0.356 | 155.417 ± 0.593 | −0.43 |

This is **agreement between two estimators**, not an identity check: the
quadrature carries its own error budget, reported in three parts.

| component | CUSUM `m=1` | SR `m=1` | how it is obtained |
|---|---:|---:|---|
| Monte Carlo | 0.1519 | 0.1448 | node SEs propagated through the Simpson weights |
| discretisation | 0.0076 | 0.0185 | Richardson `\|I_h − I_2h\|/15` from the half-resolution grid |
| truncation | 1.2e−06 | 1.8e−04 | **rigorous**: `C_D · P(\|e\| > 8)` from Lemma L2, with `C_CUSUM = 9.9e8`, `C_SR = 1.4e11` |

P9 left this "unquantified". Here every component is reported, and the
truncation term is a genuine upper bound rather than an estimate, because
Lemma L2 bounds `A` uniformly.
