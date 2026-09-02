# P5X single-cell certified stop-gate — result

```text
STOP_GATE            = FAIL
FROZEN_THRESHOLD     = 0.2            (Checkpoint A; not reinterpreted)
ACHIEVED_HALF_WIDTH  = 6.417027657738675e+42
CAUSE                = interval dependency blow-up in the continuum-in-e step
FULL_COVER_LAUNCHED  = NO
```

The cell, the detector, the window, every numerical parameter and the decision
rule were declared in `STOP_GATE_SPEC.md` **before** the computation was run.
None was changed afterwards.

---

## 1. The exact cell that was run

| field | value |
|---|---|
| target | `R_{CUSUM, m=1}(e)`, certified over the **closed cell**, not at a point |
| detector | CUSUM `k = 1/2`, `h = 5`, inclusive post-update test |
| `m` | `1` |
| `e`-interval | `[0.24, 0.26]`, carried as the Arb ball `1/4 +/- 1/100` |
| why this cell | the cell that binds `P5X-T4` (it contains `argmax_e |R|`), the steepest part of the map, and the smallest drift among cells — the least favourable available choice |
| precision | `256` bits, python-flint `0.9.0` / FLINT-Arb, outward-rounded real balls |
| method | exact-dyadic degree-12 tensor-Chebyshev candidate; symbolic Arb residual with the `phi` Maclaurin truncation of order `50` and its uniform Lagrange remainder; Bernstein continuum range bound over the reachable set (`p = r t`, `m = r(1-t)`; `r in [0,1]`, `r in [1,4]`, axis tails `r in [4,5]`), subdivision depth `3`, `64` patches per piece; drift-explicit block-forcing resolvent bound |
| sampled states | **none** — the range bound is a continuum bound |

## 2. Recorded numbers

| quantity | value | artifact |
|---|---|---|
| Chebyshev candidate `ghat(0,0)` | `-1.826579987` | `results/stop_gate_cell.json` |
| candidate `R(0.25) = e + ghat(0,0)` | `-1.57658` | agrees with the Checkpoint-A probe `-1.57611` |
| `sup` of candidate Chebyshev coefficients | `2.5373354` | |
| Bernstein continuum residual | `5.178061157506072e+39` | |
| `phi` uniform truncation error, order 50 | included in `delta` | |
| `delta` | `5.178061157506072e+39` | |
| resolvent bound `‖(I-K_e)^{-1}‖_inf` | `1239.2722762545090`, block length `n = 10`, `q_n >= 0.00806925176` | proved from scratch at the cell's drift; **no constant imported from `e = 0`**, so `DEFECT_REGISTER.md` `D3` does not bite |
| propagated error `C · delta` | `6.417e+42` | |
| `R` enclosure over the cell | `[-6.417e+42, +6.417e+42]` | |
| **achieved half-width** | **`6.417027657738675e+42`** | |
| required `delta` for a pass | `1.533158e-04` | `(0.2 - 0.01) / 1239.27` |
| overshoot factor | `3.377e+43` | |
| wall time | `99.3 s` | |
| CPU time | `96.8 s` | |
| peak RSS | `178.2 MiB` | |
| Fredholm/interval solves | 1 candidate solve (float, non-proof) + 1 symbolic residual certification + 60 resolvent block evaluations | |
| subdivisions / refinements | Bernstein subdivision depth `3` → `64` patches per reachable piece, `256` patches total; no adaptive `e`-bisection was attempted (see §5) | |
| numerical warnings | none; no exception, no precision guard triggered, every Arb ball finite and every declared positivity check passed |

## 3. The implementation is correct — checked before the verdict was believed

At `e = 0` the P5X equation `g = K_0 g + rho_{1,0}` is **literally** the `a`
equation of the certified `Gamma` chain (`closure/04_ARB_CERTIFICATE.md` §3:
`a = K a + r_a`, `r_a = phi(u) - phi(l)`), because `rho_{1,0} = phi(u) - phi(l)`.
`certificate/selftest_e0.py` checks this and records
(`results/selftest_e0.json`):

| check | result |
|---|---|
| P5X reward `rho_{1,0}` vs the certified `r_a` | identical, coefficient by coefficient |
| certified `Gamma` `a`-residual at `e = 0`, recomputed here | `3.0027342099356678e-6` |
| P5X residual at `e = 0` | `3.0027342104432955e-6` — agrees to 9 significant digits |
| P5X `ghat(0,0)` at `e = 0` | `8.88e-16`, i.e. `R(0) = 0` as `P5-T3` requires |
| P5X candidate `R(0.25)` | `-1.57658`, against the Checkpoint-A probe's `-1.57611` |

So the reduction, the reward, the panel splitting, the reachable-set cover and
the resolvent are all sound. The failure is in how the **drift** is carried.

## 4. Cause: two independent mechanisms, both from one design choice

### 4.1 The `phi` truncation error is exquisitely sensitive to the drift

The inherited architecture replaces `phi` by a **single global Maclaurin
polynomial of degree 100** (order `50`) with a uniform Lagrange remainder valid
on `|zeta| <= 11/2`. The remainder is
`(zeta_max^2/2)^{51} / (51! sqrt(2 pi))`, so it depends on the expansion radius
through a 51st power. Adding a drift widens the integration limits from
`|zeta| <= 11/2` to `|zeta| <= 11/2 + |e|`:

| drift bound | `phi` truncation error | ratio to `e = 0` |
|---|---|---|
| `e = 0` | `3.75603e-7` | `1` |
| `|e| <= 0.26` (this cell) | `4.17665e-5` | `111` |
| `|e| <= 12` (`e_far`) | `7.04071e+44` | `1.9e+51` |

The truncation allowance therefore **dominates** `delta` at the very first cell
with a drift: at the cell midpoint `delta = 1.4077e-3`, of which only
`3.3355e-5` is the Bernstein polynomial residual and `1.374e-3` is `phi`
truncation. And at `e_far = 12` the scheme is not merely loose but meaningless.
This alone defeats the planned cover, independently of anything else.

### 4.2 An interval-valued `e` is amplified by `~5e41`

`certificate/radius_scan.py` re-runs the identical pipeline varying only the
`e`-ball radius (`results/radius_scan.json`):

| `e`-ball radius `r` | Bernstein continuum residual | residual / `r` |
|---|---|---|
| `0` (point) | `3.335520e-05` | — |
| `1e-8` | `4.960840e+33` | `4.9608e+41` |
| `1e-6` | `4.960860e+35` | `4.9609e+41` |
| `1e-5` | `4.961050e+36` | `4.9610e+41` |
| `1e-4` | `4.962950e+37` | `4.9630e+41` |
| `1e-3` | `4.982020e+38` | `4.9820e+41` |
| `1e-2` (the declared cell) | `5.178061e+39` | `5.1781e+41` |

Exactly linear in the radius, stable across every radius tested. The amplifier
is the same design choice: a degree-100 expansion forces `_integrate_z` to raise
the affine integration limits — which carry `e` — to powers up to `~102`, on a
range where `|limit|` reaches `5.76`; the power-basis to triangle-parameterisation
to Bernstein chain then converts a polynomial of total degree `~200`.

**Two consequences.** More Arb precision does not help: the midpoint is accurate
to `1e-38`; this is radius propagation of a genuine input interval through an
ill-conditioned exact chain. And adaptive bisection does not help: linearity
means the cell must shrink to
`r <= (1.533e-4 - 3.34e-5)/4.961e41 = 2.42e-46`, i.e. `2.48e46` cells to cover
`[0, 12]` for one `(D, m)` — `5.65e44` CPU-hours at the measured `82 s` per
cell, about `4.7e30` times the age of the universe. `FROZEN_SCOPE.md` §4's
adaptive-bisection rule is not a rescue; it is what this measurement rules out.

### 4.3 The three regimes, side by side

| configuration | `delta` | resolvent `C` | half-width | vs threshold `0.2` |
|---|---|---|---|---|
| `e = 0` (the certified `Gamma` configuration) | `7.63302e-6` | `1315.789` (certified, imported for this line only) | `0.0100` | passes |
| `e = 1/4`, **point** (diagnostic, not a cell) | `1.40772e-3` | `1124.651` | `1.5832` | **fails** |
| `e in [0.24, 0.26]`, **the declared cell** | `5.178061e+39` | `1239.272` | `6.417e+42` | **fails** |

The `e = 0` line is the inherited certificate reproduced; every departure from it
is caused by the drift, not by the P5X reduction.

### 4.4 What is *not* the problem

The resolvent, which `CERTIFICATE_PLAN.md` flagged as the main risk, is fine and
**improves** with drift: the from-scratch block-forcing bound gives `5323.4` at
`e = 0` (`n = 7`), `1124.7` at `e = 1/4` (`n = 10`), and exactly `1.000` at
`e = 12` (`n = 1`, since one innovation alarms almost surely there). No constant
was imported and no monotonicity in `e` was assumed, so `DEFECT_REGISTER.md`
`D3` never bites.

**Why the inherited architecture never showed either mechanism.** The `Gamma`
certificates have no interval-valued parameter and no drift: `k`, `h`, `A` are
exact rationals and `e = 0` exactly, so the expansion radius is exactly `11/2`
and every input radius is zero. Both mechanisms are invisible at `e = 0` and
appear the moment a drift is introduced.

## 5. Classification of the failure

| candidate cause | ruled in / out |
|---|---|
| **`phi`-truncation blow-up with drift** (global degree-100 Maclaurin) | **RULED IN** — dominates `delta` already at `|e| <= 0.26`; meaningless at `e_far` |
| **interval dependency blow-up** | **RULED IN** — measured, linear, `4.96e41` per unit radius |
| ill-conditioning of the high-degree power/Bernstein chain | **RULED IN** — the shared amplifier behind both |
| numerical tractability (cost per cell) | ruled out — `99 s`, `178 MiB`, single-threaded |
| Fredholm solve instability | ruled out — the candidate reproduces the audited `a` at `e = 0` to 9 digits |
| resolvent bound too weak | ruled out — better than the certified `e = 0` constant, and improves with drift |
| wrong reduction (`L1`) | ruled out by the `e = 0` self-test and `ghat(0,0) = 8.9e-16` |
| the theorem being false | **not implicated** — the candidate still gives `R(0.25) = -1.5766` against a target of `2` |

## 6. Verdict, applied without reinterpretation

```text
achieved half-width 6.417027657738675e+42  >  0.2   ->   STOP_GATE = FAIL
```

Per `CODEX_HANDOFF.md` §3 step 3 and the Phase-4 rule: the full certified cover
is **aborted**, no scaling is attempted, and no production campaign is launched.
The stop-gate did its job — it cost `~20` minutes of compute and it caught a
defect that would otherwise have consumed the projected `300–800` CPU-hours and
produced nothing.

## 7. What survives

| statement | status after this stage |
|---|---|
| `L1`, `L2`, `L3`, `L5`, `L6` | **PROVED**, exact, unaffected by the certified-layer failure |
| `P5X-T1` (two-dimensional reduction, all `m`, all `e`) | **EXACT_THEOREM**, established |
| `P5X-T2` (second-moment reduction) | **EXACT_THEOREM**, established (needs `K_{z2,e}`, `D2`) |
| `P5X-T3` (far-field forgetting) | **EXACT_THEOREM** with the explicit majorant `B_D`; `B_CUSUM(12) = 5.37e-10`, `B_SR(12) = 8.57e-7`, so the frozen `e_far = 12` closes the tail with enormous margin. Only three outward-rounded Gaussian tail evaluations remain |
| fixed-drift certified enclosure | **works**: half-width `0.0413` at `e = 1/4`, `4.8x` inside the threshold |
| `P5X-T4` (`sup_e |R| <= R_max < 2`) | **NOT ESTABLISHED** — blocked on the continuum-in-`e` step |
| `P5X-T6`, `P5X-T9` | **NOT ESTABLISHED** — they consume the same cover |
| `P5X-T7`, `P5X-T8` | untouched; still `OPTIONAL` |
| original P5 | unchanged, `PARTIAL` |

## 8. Identified repairs — documented, **not executed**

Neither is run here. Re-running a stop-gate whose verdict is recorded would be
gate-shopping; a repaired method needs its own declared, adjudicated stop-gate.

**`R-A` — panel-local Taylor expansion of `phi` (recommended; fixes both
mechanisms).** Replace the single order-50 Maclaurin expansion about `0` on
`|zeta| <= 11/2 + |e|` by **panel-local Taylor expansions** on a subdivision of
the innovation range that follows the shifted limits — say unit-width panels,
degree `~10` each, each with its own uniform Lagrange remainder. Then:

* the truncation error becomes `~(1/8)^{11}/(11! sqrt(2 pi)) ~ 1e-18` per panel
  and, decisively, **stops depending on the drift**, because the panels move
  with the limits instead of the expansion radius growing with `|e|`. Mechanism
  §4.1 disappears;
* integration limits are raised to powers `~11` instead of `~102`, removing the
  `5.76^101` amplifier and with it the bulk of mechanism §4.2.

This changes the *implementation* of an inherited step, not any frozen
statement, and it makes each cell cheaper rather than dearer.

**`R-B` — carry `e` as a Bernstein variable.** Extend the residual polynomial
algebra from `(p, m)` to `(p, m, e)` and take the continuum range bound jointly
over the reachable set times the `e`-cell. Dependency then vanishes by
construction, exactly as it already does for `p` and `m`. Costs one more tensor
dimension in the Bernstein step and a real implementation effort.

`R-A` and `R-B` are complementary; `R-A` addresses both measured mechanisms and
is far cheaper, so it should be tried first and alone. A repaired attempt must re-declare its cell and parameters in a new
spec before running, and must re-run the `e = 0` self-test against the certified
`a` equation first.

## 9. Cost, for the record

Projections were requested only on a PASS; on this FAIL the honest numbers are:

| quantity | value |
|---|---|
| observed cost per cell | `99 s` wall, `97 s` CPU, `178 MiB` peak RSS, single-threaded |
| cover size at the declared granularity (`r = 0.01`) | `600` cells per `(D, m)` → `16.4` CPU-hours per `(D, m)`, `~131` CPU-hours for `8` cells — inside the `CERTIFICATE_PLAN.md` budget |
| cover size actually required by the measured amplification | `2.48e46` cells per `(D, m)` → `5.65e44` CPU-hours |
| conclusion | the budget was never the binding constraint; conditioning is |
