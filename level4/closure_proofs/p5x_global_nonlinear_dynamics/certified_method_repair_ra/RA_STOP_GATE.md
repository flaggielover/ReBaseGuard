# R-A′ stop-gate — result

```text
RA_STOP_GATE          = PASS
FROZEN_THRESHOLD      = 0.2                       (unchanged from the failed gate)
ACHIEVED_HALF_WIDTH   = 0.014176477298268092      (14.1x inside the threshold)
CELL                  = CUSUM, m = 1, e in [0.24, 0.26]   (unchanged from the failed gate)
FIRST_METHOD          = FAIL, 6.417e+42, preserved at commit 528908b
FULL_COVER_LAUNCHED   = NO
```

The first certified method failed. R-A′ is a second, different method; it does
not reinterpret, rerun or supersede that result, which stands in the record.

---

## 1. The certified statement

For **every** `e` in the closed cell `[0.24, 0.26]`,

```text
R_{CUSUM, m=1}(e)  in  [ -1.5902505376455707 , -1.5618975830490345 ] ,
```

an interval of width `0.0283529545965362`, half-width
`0.014176477298268092`. In particular `|R| <= 1.59026 < 2` on the cell that
contains `argmax_e |R_{CUSUM,1}|`, i.e. the cell that binds `P5X-T4`, with a
margin of `0.4097` to the `2` of hypothesis `H3b`.

## 2. What was run

| item | value |
|---|---|
| detector / window / cell | CUSUM (`k=1/2`, `h=5`), `m = 1`, `e in [0.24, 0.26]` — the same binding cell as the failed gate |
| representation | recentred Taylor, `N = 120`, Hermite-recurrence coefficients |
| panel centres | `e` (kernel weight); `3 + e` and `-3 + e` (reward `phi`/`Phi` sites) |
| expansion radii | `11/2` (kernel, `e`-free); `5/2` (reward, `e`-free) |
| candidate degree | 12, quadrature 400, exact dyadic at `scale_bits = 50` |
| precision | 256 bits, python-flint 0.9.0 / FLINT-Arb, outward-rounded balls |
| Bernstein subdivision | depth 3, reachable-set continuum cover, no sampled state |
| resolvent | drift-explicit block forcing, `C = 1239.2722762545090` at `n = 10`, `q_n >= 0.00806925176`; no imported constant, no monotonicity in `e` |
| sub-cells | `n_sub = 40`, `h_sub = 2.5e-4 <= h_max = 2.5283268280e-4 = 1/(4 a C)`, tiling exact |
| bootstrap closure | `C(2 a h + b2 h^2) = 0.494473 <= 1/2` — verified in interval arithmetic |
| certified solves | **120** (40 sub-cells x {value, derivative-source, derivative}) |
| Bernstein continuum bounds | **80** |
| adaptive refinements | **0** — the frozen spec authorises no retry ladder |

## 3. Measured quantities

| quantity | value (worst over the 40 sub-cells) |
|---|---|
| `delta` (value equation) | `1.02579e-5` |
| `delta'` (derivative equation) | `2.47642e-5` |
| `C * delta` | `0.0127123` |
| `S_2` (bootstrap bound on `sup |d_e^2 g|`) | `2.23821e+4` |
| second-order Taylor term `(h^2/2) S_2` | `6.99441e-4` |
| `ghat(x_0)` (sub-cell 0) | `-1.8163136381278546` |
| `d_e ghat(x_0)` (sub-cell 0) | `-1.1301181083258172` |

`R(0.24) = 0.24 + ghat(x_0) = -1.57631`, against the Checkpoint-A probe's
`-1.5761` and the failed method's own candidate `-1.57658`. The derivative
`R'(e) = 1 + d_e g = -0.130` is small, as expected for a cell containing the
maximum of `|R|`.

## 4. Runtime

| item | value |
|---|---|
| wall | `5173.3 s` (86 min) |
| CPU (workers) | `22311.2 s` (6.20 CPU-hours) |
| workers | 5 (of 6 cores) |
| peak RSS, parent / worst worker | `66.0 MiB` / `257.2 MiB` |
| mean per sub-cell | `645.8 s` wall-equivalent, i.e. `~215 s` per certified solve |
| numerical warnings | none; every declared positivity, containment and tiling check passed |

## 5. The pre-registered prediction, and how it fared

`RA_FEASIBILITY_AUDIT.md` §6 predicted, before the run,
**`~0.043`, band `0.03`–`0.09`**. The achieved `0.0142` is **below** that band:
the prediction was too pessimistic by a factor of `3`, and is recorded as
falsified on the optimistic side. The two causes, both measurable after the fact:

* `delta` came in at `1.03e-5`, not the assumed `3.34e-5` carried over from the
  failed method's point-`e` diagnostic. Recentring improved the *Bernstein
  polynomial residual itself*, not only the truncation allowance — the old
  figure was contaminated by the global expansion's conditioning;
* `delta'` came in at `2.48e-5`, not the assumed `1e-4`.

Prediction error in the conservative direction is still prediction error, and it
is reported as such.

## 6. Both failure mechanisms, retested

**M1 — truncation blow-up with drift: ELIMINATED, exactly and uniformly.**
`results/ra_diagnostics.json`:

| `e` | R-A′ kernel truncation | R-A′ total allowance | failed method (Maclaurin, order 50) |
|---|---|---|---|
| `0` | `5.84165239780028e-12` | `1.9277452912740920e-10` | `3.75603e-7` |
| `0.26` | `5.84165239780028e-12` | `1.9277452912740920e-10` | `4.17665e-5` |
| `6.5` | `5.84165239780028e-12` | `1.9277452912740920e-10` | `1.36e+28` |
| `12` | `5.84165239780028e-12` | `1.9277452912740920e-10` | `7.04071e+44` |

Identical to every digit at every drift, exactly as Device 1 predicts, because
the expansion variable `z` and its bound `11/2` are `e`-free.

**M2 — interval dependency: NOT fixed by recentring; avoided by construction.**
The frozen diagnostic re-ran the residual with an interval-valued `e` under the
R-A′ representation:

| `e`-ball radius | R-A′ Bernstein residual | amplification |
|---|---|---|
| `0` | `1.00777e-5` | — |
| `1e-8` | `4.63487e+32` | `4.63e+40` |
| `1e-6` | `4.63529e+34` | `4.64e+40` |

So the dependency catastrophe is still present in the representation — only a
factor `~11` better than the failed method's `4.96e41`. **Recentring alone would
not have rescued the campaign.** M2 is defeated only by Device 2: R-A′ certifies
exclusively at exact rational drifts and never hands the symbolic chain an
interval `e`. This is stated plainly because the opposite conclusion — that
recentring fixed everything — would be false and is the natural thing to assume.

## 7. Verdict, applied mechanically

```text
achieved half-width 0.014176477298268092  <=  0.2   ->   RA_STOP_GATE = PASS
```

Per `RA_FROZEN_SPEC.md` §11. The threshold was not touched, the cell was not
changed, no parameter was chosen after seeing a number, and no retry occurred.
