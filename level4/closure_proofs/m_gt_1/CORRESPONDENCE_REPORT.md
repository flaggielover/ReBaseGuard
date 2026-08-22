# Independent numerical correspondence report

**Decision:** `FAIL` under the complete frozen numerical gate
**Central derivative criterion:** `PASS`
**Protocol:** `27c3cddad3a09520a562b444e9635a3f4155464ac322f01edc79e0fc74c2d9af`
**Historical Stage D D2.3:** `FAILED` (unchanged)

## 1. Design executed

The run used the frozen grid `m={1,2,5,10,20,50,75,100}`, two independent
seed replications, `1,000,000` paths per Route-A replication, and `500,000`
paths per sign, step, and Route-B replication. Route A and Route B used
disjoint seed prefixes. The actual Stage-D ordinary stopping rule and random
denominator `w=min(m,tau)` were used throughout.

Route A estimated `1-widetilde Gamma_m` from the stopped-score functional at
`e=0`. Route B independently estimated the derivative of the actual induced
map from `F(+h)` and `F(-h)` at the fixed ladder
`h={0.1,0.05,0.025,0.0125}`. The primary step was `0.0125`; Richardson remains
secondary diagnostic evidence only.

The deterministic run took 133.8 seconds. Complete raw estimates are in
`results/correspondence.json` and `results/correspondence.csv`.

## 2. Primary derivative correspondence

Inverse-variance pooled values from the two independent replications:

| `m` | `widetilde Gamma_m` | theorem `1-Gamma` | direct FD at `h=.0125` | discrepancy | abs z |
|---:|---:|---:|---:|---:|---:|
| 1 | 15.88769 ± 0.02850 | -14.88769 | -14.91779 ± 0.11326 | -0.03010 | 0.258 |
| 2 | 13.25814 ± 0.02369 | -12.25814 | -12.26639 ± 0.09445 | -0.00825 | 0.085 |
| 5 | 10.18483 ± 0.01769 | -9.18483 | -9.18062 ± 0.07096 | +0.00421 | 0.058 |
| 10 | 7.08781 ± 0.01165 | -6.08781 | -6.09290 ± 0.04655 | -0.00508 | 0.106 |
| 20 | 4.25381 ± 0.00667 | -3.25381 | -3.25087 ± 0.02662 | +0.00294 | 0.107 |
| 50 | 2.35918 ± 0.00330 | -1.35918 | -1.35454 ± 0.01446 | +0.00463 | 0.312 |
| 75 | 1.96235 ± 0.00257 | -0.96235 | -0.95919 ± 0.01229 | +0.00317 | 0.252 |
| 100 | 1.77555 ± 0.00221 | -0.77555 | -0.77146 ± 0.01139 | +0.00408 | 0.352 |

All pooled discrepancies are below `0.36` combined SE, far inside the frozen
three-SE bound. Across the 16 individual replicate-by-`m` cells, the maximum
discrepancy is `0.99` combined SE, inside the four-SE replication bound. The
two independently seeded direct derivative estimates agree within `1.43`
combined SE at every `m`.

**Central derivative correspondence: PASS.** This is a new result and does not
change historical D2.3.

## 3. Finite-difference convergence

The absolute discrepancy decreased from `h=0.1` to `0.05` for `8/8` window
lengths and from `0.05` to `0.025` for `8/8`. The median observed order over
the first transition was `1.675`, inside the frozen `[1.25,2.75]` interval.
Every raw step is retained. Richardson values were computed but were not used
for the verdict.

**Convergence-order check: PASS.**

## 4. Short-cycle correction

| `m` | pooled `C_m` | observed `P(tau<m)` |
|---:|---:|---:|
| 1 | 0 exactly | 0 exactly |
| 2 | 0 observed | 0 observed |
| 5 | 0.002595 ± 0.000082 | 0.000682 |
| 10 | 0.022805 ± 0.000244 | 0.007447 |
| 20 | 0.078300 ± 0.000462 | 0.027940 |
| 50 | 0.202228 ± 0.000738 | 0.089552 |
| 75 | 0.272728 ± 0.000843 | 0.138093 |
| 100 | 0.328841 ± 0.000911 | 0.183652 |

The pointwise identity
`GammaA integrand = GammaB integrand + short-cycle correction` held to below
`1e-9` on every generated path.

The auxiliary implementation check requiring an observed short cycle at every
`m>1` failed at `m=2`. This is a low-power check, not a contradiction: at
`m=2`, a short cycle means `tau=1`, whose exact frozen-CUSUM probability is
`2 Phi(-5.5)=3.7979e-8`. Across two million Route-A paths, the expected count
is `0.07596` and the probability of observing zero is `0.9269`.

## 5. Rho scaling

Using paired fresh draws only for this explicitly frozen control,

\[
 \widehat D_\rho=\rho\widehat D_1
\]

held with maximum absolute error exactly `0.0` over both replications, all
four rho values, and all eight window lengths.

**Rho scaling: PASS.**

## 6. `m=1` control

The new pooled estimate was `widetilde Gamma_1=15.88769 ± 0.02850`; the
historical independent Stage-D estimate was `15.85436 ± 0.02853`. Their
difference is `0.827` combined SE. The exact structural reduction
`A_1=Z_tau`, `C_1=0` is separately tested.

**m=1 control: PASS.**

## 7. Stage A versus Stage D distinction

The frozen comparison at `e=0.1` gave:

| replicate | `m` | Stage A `F` | Stage D `F` | D − A | abs z | frozen result |
|---:|---:|---:|---:|---:|---:|---|
| 0 | 20 | -0.251180 ± 0.000778 | -0.256519 ± 0.000818 | -0.005338 | 4.730 | FAIL |
| 1 | 20 | -0.250982 ± 0.000779 | -0.254611 ± 0.000822 | -0.003628 | 3.203 | FAIL |
| 0 | 100 | -0.039982 ± 0.000242 | -0.064449 ± 0.000436 | -0.024467 | 49.047 | PASS |
| 1 | 100 | -0.040079 ± 0.000243 | -0.063564 ± 0.000438 | -0.023485 | 46.883 | PASS |

Pooling the two `m=20` replications would give `5.61` SE and pooling `m=100`
gives `67.84` SE, but the implemented pre-exposure rule required every cell to
exceed five SE. The pooled value is not substituted post hoc.

**Stage-A/Stage-D distinction threshold: FAIL (2/4 cells).** The point
estimates have the predicted distinction and `m=100` is decisive, but the
frozen evidentiary strength was not met at `m=20`.

## 8. Overall correspondence decision

The theorem's primary independent numerical correspondence passed by a wide
margin. Nevertheless, the complete frozen numerical gate is `FAIL` because an
explicit auxiliary Stage-A/Stage-D separation threshold failed. The campaign
therefore stopped before Lean. The theorem was not revised, no step or sample
size was changed, and no failed cell was dropped.
