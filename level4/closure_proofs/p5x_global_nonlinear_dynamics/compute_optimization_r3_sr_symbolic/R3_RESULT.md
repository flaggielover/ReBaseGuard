# P5X R3 — SR symbolic feasibility result

```text
R3_SELFTEST        = PASS  (T1-T8, 8/8)
R3_LOCAL_GATE      = FAIL  (P4 only; P1, P2, P3 pass decisively)
FAILED_CRITERION   = P4 cost, missed by 1.51x
R3_FULL_CELL_PROTOTYPE = NOT_RUN (the frozen spec requires a passing gate first)
PROJECTED_SR       = 12,084 CPU-hours  ->  R3_PARTIAL
PROJECTED_TOTAL    = 12,230 CPU-hours  ->  MORE_OPT_REQUIRED
R3_CAMPAIGN_CLASS  = R3_LOCAL_FEASIBLE_ONLY
FULL_COVER         = NOT AUTHORIZED, NOT LAUNCHED
```

---

## 1. Self-test — all eight passed

| id | check | result |
|---|---|---|
| `T1` | enclosure contains high-precision point evaluations at `-H, -H/2, 0, H/2, H` | pass |
| `T2` | remainder monotone in `H` | pass |
| `T3` | core/strip split exhaustive (`l_min <= l_max <= u_min <= u_max`) | pass, core length `10.577884` |
| `T4` | alarm boundary exact at both corners | pass |
| `T5` | centred Gaussian moments decay as `|N_k| <= h^k N_0` | pass |
| `T6` | exact rational `e = 1/4` retained | pass |
| `T7` | corrected `b_SR = log(1+A)` used and `log A` **not** used | pass |
| `T8` | no empirical monotonicity | pass |

## 2. Gate — the frozen cell

`SR`, `m = 1`, `e = 1/4`, patch `p17_m11` (the **incumbent's worst patch**),
central core panel, degree `6`, `192` bits.

| criterion | measured | threshold | verdict |
|---|---|---|---|
| `P1` softplus remainder `E_6` | `8.320749e-11` | `<= 1e-9` | **PASS**, 12x margin |
| `P2` composed+integrated relative half-width | `2.488e-10` | `<= 1e-6` | **PASS**, 4000x margin |
| `P3` dependency amplification (max coefficient radius) | `3.448e-47` | no catastrophe | **PASS**, none at all |
| `P4` `n_z * t_panel` | `0.500651 s` | `<= 0.3314531805 s` | **FAIL**, over by `1.51x` |

Panel rule output: `k = 7`, `h_z = 0.0413199`, `H_total = 0.0902062`,
`n_z = 128`, derivative bound `M_7 = 8.6286`. Measured `t_panel = 3.911 ms`.

## 3. The mathematics works; the cost rule does not

`P1`–`P3` do not merely pass, they pass by three to four orders of magnitude.
The local softplus enclosure, its composition with a bidegree-`(16,16)`
candidate, and the closed-form centred Gaussian integration are **rigorous,
tight and free of interval dependency** — the coefficient radii after composition
are `~1e-47`, i.e. the catastrophe that killed the first certified method in this
campaign does not occur here at all.

The failure is entirely in the panel **count**, and it is caused by the
interaction of two frozen choices:

* the frozen **degree `d = 6`**, which forces `H <= 0.1287` to reach `E_6 <= 1e-9`;
* the frozen **dyadic** panel rule, which then rounds `h_z` down from the
  continuous solution `0.0798` to `5.2889/2^7 = 0.0413`, **doubling** `n_z` from
  `66` to `128`.

Against a budget of `2.59 ms` per panel the machinery delivers `3.91 ms`. The
gate is missed by `1.51x` — a rounding artefact plus a degree choice, not an
architectural obstruction.

## 4. What the frozen rules forbid, and what they permit

`R3_FROZEN_SPEC.md` §6 froze **no retry ladder**. So the degree is not raised and
the panel rule is not relaxed after seeing this result; the `FAIL` stands and no
prototype is run. The following is recorded as *diagnosis*, not as a re-run:

| degree | `M_{d+1}` | `H` for `E_d <= 1e-9` | continuous `n_z` | dyadic `n_z` |
|---|---|---|---|---|
| 6 (frozen) | `8.63` | `0.1287` | `66` | **`128`** |
| 8 | `124` | `0.2428` | `27` | `32` |
| 10 | `2836` | `0.3622` | `17` | `32` |
| 12 | `9.47e4` | `0.4768` | `12` | `16` |

Higher degree raises `t_panel` (the composed degree is `16 d`), so the product is
what matters and only a fresh pre-registered gate can settle it. The measured
scaling of `t_panel` with composed degree is not known from one data point, and
this document does not extrapolate it into a claimed pass.

## 5. Dominant failure mode

`DOMINANT_FAILURE = panel count, from degree/panel-rule interaction` — explicitly
**not** degree explosion, **not** dependency, **not** tail cost, **not**
composition or integration instability. Each of those was measured and each is
comfortably clear:

* degree explosion: composed degree `96`, handled in `3.9 ms`;
* dependency: coefficient radii `~1e-47`;
* tails: none exist — the alarm truncates `z` exactly (`L-R3.4`);
* composition and integration: stable, `P2` margin `4000x`.

## 6. Projections

Using the gate's own frozen formula and the corrected `43x` multiplier:

```text
SR_total = 835 * 1210 * 128 * 0.003911 * 2 * 43 / 3600 = 12,084 CPU-hours
CUSUM    = 3.389 * 43                                  =    146 CPU-hours
TOTAL                                                   = 12,230 CPU-hours
```

| band | value |
|---|---|
| projected SR `12,084` | `8,000-15,000` → **`R3_PARTIAL`** |
| projected total `12,230` | `> 10,000` → **`MORE_OPT_REQUIRED`** |
| campaign class | **`R3_LOCAL_FEASIBLE_ONLY`** |

Against the pre-R3 SR estimate of `~34,239` CPU-hours (with the corrected
multiplier), the R3 architecture would already be a **`2.8x`** improvement — but
the frozen gate is about viability, not improvement, and `12,230` is not viable.

## 7. Second-moment extensibility (§21)

Audited, not assumed:

| element | extends? |
|---|---|
| `z^2`-weighted operator `K_{z2,e}` | **DIRECT** — the centred moment list `N_k` already supplies every power; only the index shifts |
| pair functions `G_{r,r'}` | needs new plumbing (an extra resolvent solve per pair) but no new mathematics |
| `m > 1` backward functions `h_j`, `S_j` | same machinery, more functions |
| patch/panel geometry | **reusable unchanged** — it is independent of `e`, of `m` and of the moment order |

`SECOND_MOMENT_EXTENSION = MODERATE_ADDITIONAL_WORK`.

## 8. The pre-registered prediction

Predicted: `E_6 <= 1e-12`, `n_z` `8-16`, `t_panel` `5-40 ms`, SR `1000-6000`
CPU-hours, class `READY_FOR_PRODUCTION_DESIGN`. Measured: `E_6 = 8.3e-11`
(**missed**, the prediction was 80x too optimistic), `n_z = 128` (**missed
badly** — I predicted the continuous solve and forgot the frozen dyadic rounding
and the fixed degree `6`), `t_panel = 3.9 ms` (**just below** the predicted
band), SR `12,084` (**missed**), class `MORE_OPT_REQUIRED` (**missed**).

Four of five predictions were wrong, all in the optimistic direction, and the
error traces to a single mistake: predicting from a continuous `H` solve at an
unfrozen degree instead of from the rules I had actually frozen. That is
recorded here rather than smoothed over.

## 9. What survives

The architecture is **mathematically established**: eight lemmas proved, three
of four gate criteria passed by orders of magnitude, and the softplus/Gaussian
machinery demonstrated rigorous and dependency-free on the incumbent's worst
patch. What is not established is that it is *cheap enough*, and the frozen rules
correctly refuse to let that be fixed by tuning after the fact.
