# P6 robustness

```text
SEED FAMILY = EVAL (blocks 1-4);  REPLAY reported in section 6
```

Five axes, all preregistered: fresh budget `k`, window `m`, detector, shift
`Delta`, and reference initialisation `e_0`. Plus the two internal
approximations the method actually rests on.

---

## 1. The fresh-budget frontier — `k` swept, SAW recalibrated at every point

Under the approved cost model the sample-cost axis is `k`, so the frontier is
traced by sweeping it. **SAW is recalibrated from scratch at each `k`** (a fresh
fixed point on `TUNE`), and compared against the whole fixed-`rho` grid at the
**same `k`**, so every comparison below is exactly cost-matched.

| cell | `k` | Jensen gap | `B2*` | `Arl0` `B2*` -> SAW | `Rms` `B2*` -> SAW | `Dtail100` `B2*` -> SAW |
|---|---|---|---|---|---|---|
| CUSUM m=1 | 1 | 10.04% | 0.25 | 95.3 -> 106.0 **+11.2%** | 0.8413 -> 0.7783 -7.5% | 0.1120 -> 0.1079 -3.7% |
| | 2 | 7.16% | 0.15 | 120.3 -> 127.8 +6.2% | 0.6455 -> 0.6118 -5.2% | 0.0943 -> 0.0877 -6.9% |
| | 4 | 4.43% | 0.05 | 152.9 -> 158.3 +3.5% | 0.4809 -> 0.4629 -3.8% | 0.0605 -> 0.0547 -9.6% |
| CUSUM m=3 | 3 | 5.77% | 0.20 | 145.1 -> 152.0 +4.7% | 0.5121 -> 0.4894 -4.4% | 0.0677 -> 0.0624 -7.8% |
| | 6 | 3.42% | 0.10 | 181.5 -> 184.9 +1.9% | 0.3852 -> 0.3755 -2.5% | 0.0340 -> 0.0310 -8.6% |
| | 12 | 1.78% | 0.05 | 226.9 -> 228.0 +0.5% | 0.2806 -> 0.2770 -1.3% | 0.0100 -> 0.0079 -21.1% |
| CUSUM m=5 | 5 | 3.50% | 0.20 | 174.0 -> 179.1 +2.9% | 0.4059 -> 0.3928 -3.2% | 0.0369 -> 0.0360 -2.2% |
| | 10 | 1.87% | 0.10 | 215.8 -> 219.1 +1.5% | 0.3018 -> 0.2966 -1.7% | 0.0130 -> 0.0110 -15.2% |
| | 20 | 0.92% | 0.05 | 264.6 -> 266.3 +0.6% | 0.2185 -> 0.2169 -0.7% | 0.0024 -> 0.0020 -16.5% |
| SR m=1 | 1 | 10.16% | 0.20 | 90.0 -> 101.5 **+12.9%** | 0.8544 -> 0.7770 -9.1% | 0.1052 -> 0.1022 -2.9% |
| | 2 | 7.39% | 0.15 | 115.0 -> 121.8 +5.9% | 0.6466 -> 0.6115 -5.4% | 0.0894 -> 0.0805 -9.9% |
| | 4 | 4.50% | 0.10 | 145.6 -> 151.7 +4.2% | 0.4797 -> 0.4627 -3.6% | 0.0551 -> 0.0517 -6.3% |
| SR m=3 | 3 | 5.97% | 0.20 | 139.0 -> 145.0 +4.3% | 0.5118 -> 0.4888 -4.5% | 0.0623 -> 0.0569 -8.6% |
| | 6 | 3.46% | 0.10 | 174.0 -> 177.7 +2.2% | 0.3854 -> 0.3739 -3.0% | 0.0291 -> 0.0278 -4.4% |
| | 12 | 1.82% | 0.10 | 213.1 -> 219.1 +2.8% | 0.2877 -> 0.2762 -4.0% | 0.0082 -> 0.0077 -6.1% |
| SR m=5 | 5 | 3.86% | 0.20 | 166.4 -> 171.7 +3.2% | 0.4038 -> 0.3908 -3.2% | 0.0335 -> 0.0311 -7.1% |
| | 10 | 2.00% | 0.10 | 208.0 -> 210.6 +1.2% | 0.3000 -> 0.2957 -1.4% | 0.0112 -> 0.0110 -2.0% |
| | 20 | 0.97% | 0.05 | 254.3 -> 256.0 +0.7% | 0.2180 -> 0.2167 -0.6% | 0.0017 -> 0.0016 -5.8% |

**SAW is ahead of the matched-`k` best fixed reuse weight in 18 of 18 cells on
`Arl0`, `Rms` and `Dtail(100)` simultaneously.**

Two caveats on the `Dtail(100)` column. Sixteen of the eighteen cells clear the
preregistered tail-event floor of 200 (the smallest is `308`); the two `m=5,
k=20` cells deliver only `65`-`81` events for the low-`rho` arms and their
`Dtail(100)` entries are therefore labelled **`INSUFFICIENT_TAIL_EVENTS`** — the
`-16.5%` and `-5.8%` there are point estimates on tens of events and carry no
weight. The `Arl0` and `Rms` columns, which are the low-variance coordinates,
are unaffected and are 18 of 18.

Two things the frontier says that the headline cell cannot.

* **The advantage decays with the fresh budget, exactly as the theory
  predicts.** The `Arl0` gain tracks the Jensen gap almost monotonically —
  `10.0% -> 11.2%`, `1.8% -> 0.5%`, `0.9% -> 0.6%` — because a larger `k` means
  a smaller `nu`, a smaller optimal `rho`, less weight on the selected window,
  and therefore less selection intensity to be adaptive about. **SAW matters most
  where fresh data is expensive**, which is the regime re-baselining exists for.
* **Buying safety with data always works, and never reaches nominal.** Going
  from `k = m` to `k = 4m` at CUSUM `m = 3` raises `Arl0` from `152` to `228`
  and cuts `Dtail(100)` from `0.062` to `0.0079`. It also costs four times the
  fresh observations. Even at `k = 20`, `Arl0 = 266` against a nominal `465`:
  `S20` holds throughout.

## 2. Window `m` and detector transfer

Both detectors, `m in {1, 2, 3, 5}`, eight families, canonical `e_0 = 0`
(`RESULTS.md` section 2): **8 of 8 improve on `Arl0`, `Rms`, `Dtail(100)`,
`Dq95` and `Rdelta` at matched `Fresh`.**

* **Detector transfer.** CUSUM and SR agree closely: the `Arl0` gain is
  `+14.4%` / `+12.0%` at `m=1`, `+5.1%` / `+5.0%` at `m=3`, `+2.4%` / `+5.6%` at
  `m=5`. The calibration constants differ systematically (`g1 = -1.02..-1.07`
  CUSUM vs `-1.17..-1.25` SR), which is why **each detector is calibrated
  separately** — `P14` (detector-agnosticism of the map) is `EMPIRICAL_ONLY` and
  no transfer is assumed anywhere.
* **`m` dependence.** The gain shrinks monotonically with `m` in the CUSUM
  column (`+14.4%, +7.2%, +5.1%, +2.4%`) and near-monotonically in SR
  (`+12.0%, +6.5%, +5.0%, +5.6%`). The theory explains it: averaging more
  observations reduces the dispersion of the selection intensity, hence the
  Jensen gap (`15.9% -> 6.9%` over `m = 1..5`).
* **`m = 1`, which `S14` calls unusable at any `rho`, is where SAW helps most**
  in relative terms and where it still leaves the worst absolute state
  (`Arl0 = 106` against nominal `465`). Improving the worst case is not the same
  as fixing it.

## 3. Shift regimes

Measured at `Delta in {0.5, 1.0, 2.0}` and, for the in-control coordinate,
`Delta = 0`. The full table is `RESULTS.md` section 4. The finding that matters:

**SAW's delay-tail advantage over `B2*` is material at `Delta = 1`, present but
under-powered at `Delta = 2` (the tail-event floor of 200 is not met there, so
`Dq95` is reported instead and `Dtail(100)` is labelled
`INSUFFICIENT_TAIL_EVENTS`), and absent at `Delta = 0.5`.** At `Delta = 0.5` full reuse has the
*smallest* delay tail of any policy — an artefact of its ruined in-control ARL
(`Rdelta = 1.074 > 1`: the shifted cycle is *longer* than the in-control one,
the pathological regime `S6` names), not a detection advantage. On `Rdelta`,
which is not confounded by the alarm rate, SAW is best at all three shifts.

The calibration never saw a shift (`Delta = 0` only), so this is out-of-sample
behaviour for the method in the strongest sense available.

## 4. Finite-reference initialisation (secondary evidence)

The canonical experiment fixes `e_0 = 0`. As a **secondary** regime the whole
comparison was re-run with `e_0 ~ N(0, 1/m_0)`, `m_0 in {20, 50, 100}`, on both
detectors at `m in {1, 3, 5}` — 18 cells.

**SAW_M beats `B2*` in 18 of 18 on `Arl0`, `Rms`, `Dmean`, `Dq95` and
`Dtail(100)`.** Representative (CUSUM `m = 3`):

| `m_0` | `B2*` `Arl0` | SAW `Arl0` | `B2*` `Rms` | SAW `Rms` | `B2*` `Dtail100` | SAW `Dtail100` |
|---|---|---|---|---|---|---|
| 20 | 144.2 | 152.2 | 0.5174 | 0.4902 | 0.0671 | 0.0623 |
| 50 | 144.0 | 151.8 | 0.5181 | 0.4894 | 0.0708 | 0.0624 |
| 100 | 144.3 | 151.1 | 0.5176 | 0.4907 | 0.0701 | 0.0598 |
| (canonical `e_0=0`) | 144.1 | 151.5 | 0.5177 | 0.4909 | 0.0677 | 0.0607 |

The late-cycle numbers are essentially unchanged from the canonical regime,
which is what T6-B's uniform geometric ergodicity would predict: the initial
condition is forgotten.

**One number does move, and it is a definitional artefact worth flagging.**
`Coll = E[tau_2]/E[tau_1]` rises sharply (e.g. `0.293 -> 0.562` at `m_0 = 20`)
because its *denominator* changes: cycle 1 now starts from a random `e_0` rather
than from `e_0 = 0`, so `E[tau_1]` falls from `~465` to `~250-385`. `Coll` is a
convention-dependent diagnostic and its two regimes must not be compared
directly. The ordering *within* a regime is preserved: full reuse remains at
`0.02-0.06` in every cell.

## 5. The method's two internal approximations, measured

| approximation | how it was checked | result |
|---|---|---|
| the plug-in `V_hat` for `V = E[U^2 \| F]` | binned estimate of the true conditional second moment on 4000 x 120 cycles | `corr(V_hat, V) = 0.997`-`0.999`; plug-in error is **7.4%-13.9% of the Jensen gap** in all 8 cells, so `THEORY.md` T6-C(iii)'s criterion is satisfied everywhere |
| SAW-T's Gaussian step for the law of `U \| F` | Monte Carlo evaluation of the realised exceedance against the Gaussian prediction, by decile of `\|mu_hat\|` | overall predicted vs empirical agree to `0.0005`-`0.003`; worst decile-bin gap `0.013`-`0.020`. The approximation is good but not free, and it is why SAW-T is consistently slightly worse than SAW-M (`ABLATION.md` (e)) |

## 6. Independent seed family (`REPLAY`)

`REPLAY` is a third disjoint seed family, asserted disjoint by test and untouched
during calibration, screening and confirmation. The confirmation stage was
re-run on it end to end, including re-selection of `B2*` on `REPLAY` itself so
that the grid-selection bias of `S1` in `LIMITATIONS.md` is exposed rather than
inherited.

<!-- P6-REPLAY-START -->
| cell | `B2*` on EVAL | `B2*` on REPLAY | `Arl0` rel (EVAL / REPLAY) | `Rms` rel | `Dtail100` rel | `z` | resolved |
|---|---|---|---|---|---|---|---|
| CUSUM m=1 | 0.15 | **0.20** | +14.4% / +11.3% | -11.4% / -9.0% | -6.0% / -6.0% | -3.75 | yes |
| CUSUM m=2 | 0.25 | **0.20** | +7.2% / +6.5% | -5.6% / -5.6% | -10.1% / -10.9% | -6.13 | yes |
| CUSUM m=3 | 0.15 | **0.20** | +5.1% / +4.8% | -5.2% / -4.4% | -10.4% / -8.9% | -4.25 | yes |
| CUSUM m=5 | 0.15 | **0.20** | +2.4% / +2.7% | -3.1% / -2.9% | -10.9% / -7.5% | -2.64 | yes |
| SR m=1 | 0.20 | 0.20 | +12.0% / +12.4% | -9.0% / -9.4% | -4.7% / -6.2% | -3.70 | yes |
| SR m=2 | 0.20 | 0.20 | +6.5% / +7.0% | -5.8% / -5.9% | -11.3% / -9.1% | -4.91 | yes |
| SR m=3 | 0.20 | **0.15** | +5.0% / +5.6% | -4.4% / -5.6% | -8.6% / -10.0% | -4.60 | yes |
| SR m=5 | 0.25 | **0.15** | +5.6% / +3.1% | -4.3% / -3.4% | -9.6% / -6.7% | -2.26 | yes |

**8 of 8 families reproduce on the independent seed family**, with the effect
resolved in each and the effect sizes agreeing to within a few percentage
points. At the primary cell the paired comparison is `Dtail(100)`
**-8.9%** `[-12.8%, -4.9%]` on `REPLAY` against `-10.4%` `[-14.3%, -6.4%]` on
`EVAL`; `Arl0` `+4.8%` against `+5.1%`; `Rms` `-4.4%` against `-5.2%`.

**The grid-selection sensitivity is visible and is worth naming.** `B2*` moves
between seed families in **5 of 8** cells — always to an adjacent grid point,
because the fixed-`rho` objective is flat near its optimum and the grid members
at `0.15`, `0.20` and `0.25` are statistically near-tied. That is exactly the
optimistic bias `LIMITATIONS.md` `S1` warns about, and it is the reason `B2*` is
re-selected on `REPLAY` rather than carried over: had the `EVAL` choice been
imposed on `REPLAY`, SAW's margin would have been reported against a control
chosen to be favourable to it. The measured effect survives re-selection.
<!-- P6-REPLAY-END -->

## 7. Difficult regimes, not cherry-picked

The design deliberately includes the cells where P7 found the worst behaviour:

| regime | what P7 found | what P6 measures |
|---|---|---|
| `m = 1`, any `rho` | "unusable" (`S14`) | still the worst absolute state under every policy; SAW's *relative* gain is largest here and its absolute `Arl0` is still `106` against `465` |
| `rho = 1`, cycle 2 | 98% collapse (`S8`) | reproduced: `Coll = 0.012`-`0.020` for full reuse in all 8 families. SAW's `Coll` is `0.19`-`0.37`, statistically indistinguishable from `B2*`'s |
| `Delta = 1`, upper-tail delay | `q95 = 275`, `P(delay>100) = 11.4%` at CUSUM `m=1, rho=1` (`S9`) | reproduced (`q95 = 276`, `Dtail100 = 0.1136`); SAW at the same cell gives `q95 = 252`, `Dtail100 = 0.1057` — an improvement, but a small one. **`m = 1` is not repaired by SAW** |
| discrimination ratio `>= 1` | `R_Delta = 1.06` at `m=1, rho=1` (`S6`) | reproduced (`1.047`); SAW gives `0.473` at the same cell |
