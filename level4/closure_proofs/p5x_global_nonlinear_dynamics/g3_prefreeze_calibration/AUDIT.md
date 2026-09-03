# P5X — G3 Pre-Freeze Cost and Scaling Calibration

`PRE_FREEZE_COST_AND_SCALING_CALIBRATION`. Not R9, not a binding checkpoint, not
a scientific result, not a new certifier. **Nothing historical changed.**
`R8 F3 = FAIL`, `R8 prototype = FAIL`, `G3 consumer = strict |R| < 2`.

```text
RESULT   PREFREEZE_READY = NO.
         Caveat II is retired with a NEGATIVE answer: delta is NOT
         e-independent -- k = G*delta varies 2388x across the cover.
         The G3 audit's 54.95 CPU-h projection is SUPERSEDED: it priced the
         far field at grid 9, and the far field actually needs grid 5000-8400.
BLOCKER  PF-E (cells need G > 1536), carrying PF-D and PF-F.
```

---

## 1. Caveat II — `1/G` scaling holds, `e`-independence does not

`delta(e,G)` measured with the R8 certifier, worst over a 12x12 cell sample:

| `e` | `delta(512)` | `delta(1024)` | `delta(512)/delta(1024)` | `k = G delta` |
|---|---|---|---|---|
| 0.05 | `1.058022e-02` | `5.292144e-03` | `1.9992` | `5.42` |
| 0.10 | `1.055396e-02` | `5.282261e-03` | `1.9980` | `5.41` |
| 0.15 | `1.022257e-02` | `5.116197e-03` | `1.9981` | `5.24` |
| 0.25 | `1.001946e-02` | `5.008547e-03` | `2.0005` | `5.13` |
| 0.35 | `9.889220e-03` | `4.941030e-03` | `2.0014` | `5.06` |
| 0.50 | `1.018050e-02` | `5.086885e-03` | `2.0013` | `5.21` |
| 1.00 | `1.353057e-02` | `6.753018e-03` | `2.0036` | `6.92` |

**`1/G` scaling is confirmed exact** (ratios `1.998`-`2.004`, within `0.2%`).

**`e`-independence is refuted.** The direct-residual variant the G3 cost model
actually assumed has gradient-bound sum `W(e) = w_+ + w_-` (`k_direct = W`):

```text
e:      0.00   0.02   0.05   0.10   0.15   0.25   0.35   0.50   1.00
W:      2.035  2.082  2.156  2.096  2.001  1.810  1.688  1.702  2.883
e:      2.00      4.00       6.00       8.00
W:     88.53   4031.37    3572.43*   3113.48        (*interpolated)
```

`W` spans `1.688` to `4031.37` — a factor **`2388`**. The G3 audit used a single
constant `k = 1.637` taken from one cell at `e = 1/4`. Two errors compound: that
single-cell value understates even the `e = 0.25` worst-over-cells `W = 1.8098`
by `11.4%`, and it is applied where the true `W` is three orders larger.

**Mechanism, not noise.** `w_-` contains `int E^- phi dz = e^{e}[Phi(u+e+1) -
Phi(l+e+1)]`, which grows like `e^{e}`. At `e = 4` that weight is `~52`; at
`e = 8`, `e^8 ~ 2981`.

## 2. The far field is genuinely harder, and the bound is also loose

| `e` | true `max|dr/dz+|` | true `max|dr/dz-|` | true sum | `W` bound | looseness |
|---|---|---|---|---|---|
| 0.25 | `7.57e-03` | `1.05e-02` | `0.0181` | `1.81` | `100x` |
| 1.00 | `3.15e-05` | `4.93e-02` | `0.0494` | `2.88` | `58x` |
| 2.00 | `3.84e-04` | `2.92e-01` | `0.2927` | `88.53` | `302x` |
| 4.00 | `8.26e-04` | `4.58e+01` | `45.81` | `4031.37` | `88x` |
| 8.00 | `2.73e-10` | `8.86e+01` | `88.59` | `3113.48` | `35x` |

Both statements are true: the **true** gradient grows to `~89` at `e = 8`, and
the **bound** is still `35`-`302x` loose. If the bound were tight the far field
would be cheap (`G ~ 56`-`77`); making it tight is a new architecture and is out
of scope here.

## 3. Caveat I — the actual adaptive cover under the `G3` rule

Deterministic rule modelled: accept a cell when the certified enclosure fits in
`(-1.95, 1.95)` at some `G <= 1536` from the ladder, else bisect;
`delta_needed = (1.95 - max|R| - halfwidth_e)/max C_SR`, `G = 1.25 W/delta`.

```text
accepted cells                16, spanning e in [0.2285, 2.0654]
accepted widths               min 0.00146  median 0.02344  max 0.37500
OVERFLOW (require G > 1536)   84.7% of [0,12] by measure (10.16 of 12)
worst required G              8432
```

| `e` range | status | worst required `G` |
|---|---|---|
| `[0, 0.072]` | OVERFLOW | `2219` |
| `[0.072, 0.20]` | OVERFLOW | `2362` |
| `[0.20, 0.35]` | OVERFLOW | `1841` |
| `[1, 2]` | accepted (3 cells) | `1396` (`7.15` CPU-h) |
| `[2, 3]` | OVERFLOW | `6574` |
| `[3, 6]` | OVERFLOW | **`8432`** |
| `[6, 10]` | OVERFLOW | `5419` |
| `[10, 12]` | OVERFLOW | `2096` |

**Bisection does not rescue an overflow cell.** `delta_needed` is dominated by
`C_SR`, which is a property of the drift, not the cell width; halving a cell
only halves the `~0.007` `e`-contribution. The reconstruction confirms this: it
bisected to width `1e-3` and produced `13876` unaccepted cells.

Two overflow regions have non-certifier routes already available: `[0, 0.072]`
is covered by the exact `R(0) = 0` (`P5-T3`) plus the certified `Gamma_SR`
derivative bound, and `[~6.9, 12]` is plausibly closed by the `P5X-T3`
far-field majorant. The residual genuine blockers are therefore
**`[0.072, 0.35]`** and **`[2, ~6.9]`**, the latter dominant.

## 4. Cost

```text
optimistic (G3 audit assumption, e-independent delta)   54.95 CPU-h  -- INVALID
central    (accepted cells only, e in [0.2285,2.0654])   7.2  CPU-h
conservative (whole cover at the required G)             INFEASIBLE
```

At `e in [3,6]` a single `e`-cell at `G = 8432` costs `8432^2 x 6 ms = 118.5`
CPU-hours. Even a few dozen cells there run to thousands of CPU-hours.

## 5. Pre-freeze conditions

| | condition | verdict |
|---|---|---|
| `PF-A` | adaptive cover reconstructed | **PASS** |
| `PF-B` | `delta` drift-dependence measured | **PASS** — and it refutes the assumption |
| `PF-C` | conservative scaling envelope | **PASS** — `delta <= 1.25 W(e)/G`, `W` measured at 12 drifts |
| `PF-D` | every cell has a planned rigorous route | **FAIL** |
| `PF-E` | every direct-certified cell needs `G <= 1536` | **FAIL** — `84.7%` of the cover overflows |
| `PF-F` | conservative total `<= 500` CPU-h | **FAIL** |
| `PF-G` | protected tree | **PASS** |
| `PF-H` | no new candidate/approximation | **PASS** |

`PF1`/`PF2`/`PF3` all **FAIL** on the conservative number.
**`PREFREEZE_READY = NO`.** No successor specification is drafted: `PF-D` and
`PF-E` fail, so there is no complete method assignment to freeze.

## 6. What this changes

The G3 audit's headline — `~55` CPU-hours, `COST_STRONG` — does not survive
measurement. Its error was precisely the caveat it flagged: it took `delta` from
one cell at one drift and applied it across `[0,12]`, and the region it assumed
cheapest (large `e`, where `|R| -> 0` and `C_SR -> 1`) is where `delta` is worst
by three orders of magnitude, because the `e^{e}` weight in the minus-chart
derivative had never been measured outside `e ~ 0.25`.

The consumer-margin insight from that audit still stands and is still valuable:
`|R| < 2` really is the load-bearing criterion, and it really does make
`e >= 0.35` cheap *in margin terms*. What it does not do is make the far field
cheap in *certifier* terms.

## 7. Recorded for whoever picks this up

The far-field blocker has a clear shape. `w_-` bounds `int ghat_y(q) E^- phi dz`
by `(global range of ghat_y) x int E^- phi`, and `int E^- phi ~ e^{e}`. But
`E^- phi` concentrates near `z = l`, where `zeta'^- = 1` exactly — the alarm
edge. A bound that used `ghat_y` restricted to a neighbourhood of that edge,
rather than its global range, would attack the `35`-`302x` looseness directly.
That is a new construction and needs its own audit; nothing here establishes it.
