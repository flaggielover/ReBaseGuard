# P6 ablation — establishing *why* SAW works

```text
SEED FAMILY = EVAL          CONTROL = B2*, the cell's best fixed rho at matched Fresh
```

The pre-design's standard is explicit: *if the full policy wins but every
component ablation also wins equally, the claimed mechanism is not
established.* This document tests that.

The ablations are not bolted on. SAW is one rung of an **information ladder**
indexed by what is known about the selection intensity `V_j = E[U_j^2 | F_j]`,
and the bottom rung of that ladder **is** the incumbent method. Removing the
sensor does not produce a crippled SAW; it produces a fixed-`rho` policy,
exactly.

| rung | `V` used | class | what removing it tests |
|---|---|---|---|
| `SAW_A_flat` | the constant `E[V]` | implementable | the sensor entirely — **this is a fixed-`rho` policy**, asserted bit-identical to `ConstantPolicy(rho = nu/(E[V]+nu))` by test |
| `SAW_A_naive` | `zbar_j^2` (raw magnitude) | implementable | the *calibration* — keep the sensor, throw away the fitted gain and the variance offset |
| `SAW_A_no_tau` | `(g0 zbar)^2 + s` | implementable | the *stopping-geometry* feature `g1/sqrt(tau)` (with `g0`, `s0` refitted in its absence, not inherited) |
| **`SAW_M`** | `((g0 + g1/sqrt(tau)) zbar)^2 + s` | implementable | — |
| `SAW_T` | same plug-in, tail objective | implementable | whether targeting the tail directly beats targeting the second moment |
| `Z1` | the realised `U_j^2` | **oracle** | the plug-in itself: how much of the shortfall is estimation, how much is the rule shape |
| `Z2` | realised `U_j`, exact one-step tail | **oracle** | the ceiling for the tail objective |

---

## 1. The ladder, as a fraction of `SAW_M`'s gain over `B2*`

`100%` means "recovers exactly the full SAW gain"; `0%` means "indistinguishable
from the best fixed reuse weight". `A` = `Arl0` gain, `R` = `Rms` reduction
(both low-variance); `D` = `Dtail(100)` reduction (noisier, shown for
completeness).

| cell | `flat` | `naive` | `no_tau` | `SAW_M` | `SAW_T` | `Z1` oracle |
|---|---|---|---|---|---|---|
| CUSUM m=1 | A 21% R 39% | A 67% R 65% | A 77% R 87% | **100%** | A 83% R 85% | A 109% R 120% |
| CUSUM m=2 | A 5% R 1% | A 56% R 40% | A 72% R 79% | **100%** | A 87% R 78% | A 140% R 141% |
| CUSUM m=3 | A 8% R 17% | A 55% R 44% | A 86% R 86% | **100%** | A 93% R 85% | A 168% R 150% |
| CUSUM m=5 | A -6% R 6% | A 40% R 31% | A 91% R 82% | **100%** | A 86% R 86% | A 219% R 174% |
| SR m=1 | A 10% R 20% | A 63% R 54% | A 75% R 85% | **100%** | A 90% R 84% | A 119% R 127% |
| SR m=2 | A -0% R 4% | A 54% R 45% | A 77% R 82% | **100%** | A 87% R 85% | A 145% R 146% |
| SR m=3 | A 3% R -4% | A 52% R 34% | A 76% R 78% | **100%** | A 89% R 83% | A 162% R 154% |
| SR m=5 | A 50% R 32% | A 60% R 48% | A 87% R 87% | **100%** | A 94% R 91% | A 153% R 155% |

At the primary cell, in absolute terms and with intervals against `B2*`:

| policy | `Arl0` | `Rms` | `Dtail(100)` | `Dtail(100)` rel. to `B2*` [95%] |
|---|---|---|---|---|
| `B2*` (`rho = 0.15`) | 144.10 | 0.5177 | 0.0677 | — |
| `SAW_A_flat` | 144.67 | 0.5132 | 0.0686 | `+1.4%` `[-2.7%, +5.7%]` **INCONCLUSIVE** |
| `SAW_A_naive` | 148.18 | 0.5060 | 0.0649 | `-4.1%` `[-8.0%, +0.1%]` **INCONCLUSIVE** |
| `SAW_A_no_tau` | 150.48 | 0.4946 | 0.0614 | `-9.3%` `[-13.1%, -5.4%]` resolved |
| **`SAW_M`** | **151.52** | **0.4909** | **0.0607** | `-10.4%` `[-14.3%, -6.4%]` **material** |
| `SAW_T` | 150.96 | 0.4950 | 0.0611 | `-9.7%` `[-13.4%, -5.7%]` resolved |
| `Z1` oracle | 156.53 | 0.4776 | 0.0572 | `-15.5%` `[-19.2%, -11.8%]` material |

## 2. What this establishes

**(a) The sensor is the mechanism, and removing it removes the effect
entirely.** `SAW_A_flat` recovers a median of about `7%` of the `Arl0` gain and
`19%` of the `Rms` gain across the eight families, and at the primary cell its
`Dtail(100)` difference from `B2*` is `+1.4%` with an interval straddling zero —
**statistically indistinguishable from the incumbent**. This is the strongest
form the ablation could take, because `flat` is not an approximation of a
fixed-`rho` policy: it *is* one, and `tests/test_saw.py` asserts the two chains
are bit-identical.

**(b) No single component reproduces the effect; all three contribute.**
Decomposing the `Arl0` gain at the median cell:

```text
   sensor present at all            flat  ->  naive     ~ +48 pp
   calibrated gain + variance       naive ->  no_tau    ~ +22 pp
   stopping-geometry feature        no_tau -> SAW_M     ~ +23 pp
```

so roughly half the effect is *having* a per-cycle risk sensor, and the other
half is split evenly between *calibrating* it and conditioning it on the
stopping geometry. The naive magnitude proxy — "use `zbar^2` as if it were the
selection intensity" — recovers a bit over half the gain and is **not resolved**
at the primary cell. Using the observable is not enough; using it in the derived
way is what pays.

**(c) It is not enough to threshold the same sensor.** Two heuristic baselines
use `|zbar|` exactly as SAW's sensor does, but as a gate rather than a weight:

| policy | `Arl0` | `Rms` | `Dtail(100)` vs `B2*` |
|---|---|---|---|
| `B6` two-level `rho` on `|zbar|` | 137.52 | 0.5175 | `+3.5%` `[-0.6%, +7.8%]` |
| `B11` confidence gate on `|zbar|` | 135.69 | 0.5294 | `+4.8%` `[+0.6%, +9.2%]` |

Both are **worse than the best fixed reuse weight**, and `B11` — the shape of
the cautious-parameter-learning idea (`NOVELTY_AUDIT.md` section 3) —
is resolved-worse. The continuous inverse-variance weight is doing something a
threshold on the same statistic does not.

**(d) The plug-in, not the rule shape, is what is left on the table.** `Z1`
(the same rule with the realised `U_j^2`) recovers `109%` to `219%` of `SAW_M`'s
`Arl0` gain, i.e. **SAW captures 46%-92% of the achievable ceiling** for this
rule shape — best at `m = 1` (92%), worst at `m = 5` (46%). Since the plug-in
error is measured at only 3%-7% of the Jensen gap
(`RESULTS.md` section 6), the remaining ceiling is not a bad estimator; it is
that `Z1` conditions on a strictly finer sigma-field.

**(e) Targeting the tail directly does not help.** `SAW_T` recovers `83%`-`94%`
of `SAW_M`'s gain, i.e. it is consistently *slightly worse*, including on the
tail objective it was designed for. The reason is visible in `THEORY.md` T6-D:
the tail rule requires an extra Gaussian approximation to the conditional law of
a selected window mean, and the approximation error (worst decile-bin gap
`0.013`-`0.020`) costs more than the change of objective gains. **The
second-moment rule is the one to recommend**, and this is a case where the
simpler derivation is also the better method.

**(f) A perfect trigger is not a good policy.** Oracle `Z3` — reset iff the
*true* `|e_j| > 0.3`, else full reuse — reads the latent state and is still
**far worse than the best implementable policy**: at the primary cell
`Arl0 = 97.8` against `B2*`'s `144.1`, `Dtail(100)` `+62.5%`. An oracle bounds
what its own rule shape can achieve, not what adaptivity can achieve, and a
badly shaped oracle is not a ceiling for a well shaped implementable rule. This
is worth recording because the pre-design offered `Z3` as "the value of a
perfect trigger"; the measured answer is that the trigger shape is the problem.

The same holds for oracle `Z4`, which knows the true `Delta` and refuses any
update landing within `0.3` of it — the pre-design's instrument for pricing
`H8` ("the blind spot has no implementable proxy"). At the primary cell it
records `Dtail(100) = 0.0696`, **worse than `SAW_M`'s `0.0607`** and no better
than `B2*`'s `0.0677`. So the measured price of `H8`, for this guard shape, is
**zero**: knowing the shift exactly and steering away from the blind spot buys
nothing here. That is a useful negative — it says the delay tail at `Delta = 1`
is driven by reference dispersion generally, not by the narrow blind-spot event
`S10` isolates — and it is also a limit of the instrument: a single guard radius
on a fixed `rho` is a weak oracle, so this bounds the value of *that* rule, not
of shift knowledge in general.

## 3. What this does *not* establish

* Nothing here is a monitoring **guarantee**; every row is a measurement
  (`S18`, `X6`).
* The decomposition in (b) is a difference of point estimates on a common seed
  family, not an orthogonal variance decomposition; the components interact.
* `SAW_A_no_tau` refits `g0` and `s0` in the feature's absence, so it is a
  genuine ablation and not a crippled full model — but the refit was done on
  `TUNE` at the same time as the full model, so the two share calibration noise.
* The ladder is measured at `k = m` and `Delta in {0.5, 1, 2}` only.
