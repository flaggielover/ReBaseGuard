# P5X R8 — result: local certification PASSES, SR prototype FAILS

```text
R8_LOCAL_CERTIFICATION_GATE  = PASS     (B1_GATE AND B2_GATE)
SR FULL-CELL PROTOTYPE       = FAIL     failed F3 (half-width), F7 (CPU)
BLOCKER                      = RESIDUAL_STILL_TOO_WIDE  (+ COST_FAIL on F7)
CLASSIFICATION               = R8_LOCAL_CERTIFICATION_PASS
```

Anchor: Checkpoint J `55c5f1de9eb07a855948f92215b38a24b8321c5d`, pushed before
any binding gate ran. **The `F3` failure was predicted in that anchor, with the
numbers, before the run.**

---

## 1. B1 — one-sided resolvent: PASS

| criterion | result |
|---|---|
| `B1-Q1` domination proof | PASS — `B1-L1`..`B1-L5` |
| `B1-Q2` one-sided kernel correspondence | PASS |
| `B1-Q3` finite rigorous `C_SR` | PASS |
| `B1-Q4` `C_SR(e=1/4) <= 1000` | **`203.067`** (`n_0 = 102`, `q = 0.497702`) PASS |
| `B1-Q5` `C_SR(e=0) <= 3000` | **`1505.821`** (`n_0 = 753`, `q = 0.499940`) PASS |
| `B1-Q6` runtime `<= 30 min` | `3.2 s` and `23.4 s` PASS |
| `B1-Q7` no empirical monotonicity | PASS |
| `B1-Q8` semantics unchanged | PASS |

`C_SR` for the whole `e`-cell `[0.24, 0.26]` is **`216.963`** (computed at
`e = 0.24`, valid across the cell by lemma `B1-L6`, added post-anchor and
disclosed in `POST_ANCHOR_ADDENDUM.md`).

**Recorded negative result inside B1.** The frozen cell-mass construction —
maximising each `z`-sub-interval's Gaussian mass at its own worst `e*` — does
**not** converge on an `e`-cell: `q` stays at exactly `1.0` for all `4000`
sweeps, because the per-sub-interval maxima sum to more than `1`. It converges
immediately at point drifts. `B1-L6` supplies a different, proved route to the
cell scalar; it does not rescue that construction.

## 2. B2 — stable-basis range bound: PASS

Full frozen `1024 x 1024` sweep, `1048576` cells, 6 workers, `2260.97 s` wall.

| criterion | result |
|---|---|
| `B2-Q1` exact monomial/Bernstein equality | PASS |
| `B2-Q2` exact degree elevation `16 -> 32` | PASS |
| `B2-Q3` rigorous de Casteljau restriction | PASS (overshoot `1.000x`) |
| `B2-Q4` rigorous `ghat` hull | PASS |
| `B2-Q5` rigorous derivative hulls | PASS (`Mx = 1.2046`, `My = 0.5217`) |
| `B2-Q6` rigorous `K_e ghat` range, corrected `w^-` | PASS (`<= 6.5e-13` vs finite differences) |
| `B2-Q7` worst enclosure `<= 1e-2` | **`5.0108623e-03`** at cell `(385, 382)` PASS |
| `B2-Q8` improvement `>= 1e6` | **`1.344e7 x`** over `6.736713e4` PASS |
| `B2-Q9` grid `1024 x 1024` | PASS (disclosed deviation, §0 of the spec) |
| `B2-Q10` mean `<= 10 ms/cell` | **see disclosure below** |
| `B2-Q11` `z_panels = 0` | PASS |
| `B2-Q12` `softplus = 0` | PASS |
| `B2-Q13` R6 fast kernel unchanged | PASS |
| `B2-Q14` no empirical monotonicity | PASS |

Mean bound over all cells `4.142e-03`; worst `5.0108623e-03`, within `0.03%` of
the pre-freeze dense-scan prediction `5.009432e-03`.

**`B2-Q10` disclosure.** Single-threaded per-cell cost, the basis on which the
criterion was written and on which the audit reported `5.13 ms`, is **`4.85
ms/cell`** (measured on `1600` cells) — PASS. The 6-worker sweep's
CPU-per-cell is **`12.94 ms`**, inflated by memory/allocator contention; read
that way `B2-Q10` would FAIL. `B2-Q10` is bound here on the single-threaded
figure, and both numbers are reported. Wall-clock per cell was `2.16 ms`.

## 3. R8 local certification gate: **PASS**

`B1_GATE AND B2_GATE = PASS`. This is the first time SR certification machinery
has passed end to end in this campaign.

## 4. SR full-cell prototype: FAIL

```text
R_{SR,1}(e)  in  e + ghat(x_0)  +/-  C_SR * delta ,   e in [24/100, 26/100]

C_SR   = 216.963          (binding B1, cell-valid by B1-L6)
delta  = 5.0108623e-03    (binding B2, 1024x1024 sweep)
ghat(x_0) = -1.8403422831
midpoint  = -1.5903422831
half-width = 1.097172  =  C*delta 1.087172  +  e-cell 0.01
```

| criterion | result |
|---|---|
| `F1` finite | PASS |
| `F2` MC-consistent | **PASS** — contains `-1.593369`, `-1.592117`, `-1.589105` within `3` s.e. |
| `F3` half-width `<= 0.2` | **FAIL — `1.097172`** |
| `F4` `z_panels = 0` | PASS |
| `F5` `softplus = 0` | PASS |
| `F6` no empirical monotonicity | PASS |
| `F7` CPU `<= 2 h` | **FAIL — `3.77` CPU-hours** (sweep `2261 s` x 6 workers) |
| `F8` protected tree | PASS |
| `F9` candidate unchanged | PASS |
| `F10` traceable to binding outputs | PASS |

**Blocker: `RESIDUAL_STILL_TOO_WIDE`**, with `COST_FAIL` on `F7` as a secondary.

The diagnosis was fixed before the run and is confirmed: the certified `delta`
is `202.6x` looser than the true `sup |r| = 2.472122e-05` (46x46 point sample).
`C_SR * sup|r|_true = 0.0049` would pass `F3` with `40x` margin; `C_SR * delta =
1.087` fails it by `5.4x`. The looseness is structural — the frozen §6 recipe
bounds `osc(ghat)` and `osc(K_e ghat)` separately and so discards the
cancellation between two quantities of size `~1.84` that agree to `~2e-5`.
Grid refinement cannot close it inside `F7`: `delta ~ 5.13/G`, so `delta <=
1e-3` needs `G ~ 5130`, i.e. `~35` CPU-hours single-core.

## 5. Measured production projection — `NOT_READY`

The certification, not the kernel, now dominates by five orders of magnitude:
per `e`-cell the R6 kernel work is `1210` patches x `0.3757 ms = 0.45 s`, while
the certification is `1048576` cells x `12.94 ms = 13570 s`.

```text
SR, m = 1, first moment   835 e-cells x 3.77 CPU-h  =  3148 CPU-hours
```

That single lane already exceeds the `2000` CPU-hour ceiling, before `m = 2,3,5`
and before any second moment. **`R8_PRODUCTION_READINESS = NOT_READY`.** No
`m > 1` or second-moment probe was run (§18 requires STOP on a prototype FAIL).

## 6. What R8 establishes

**Established.** A rigorous `C_SR` for the two-chart SR process exists and is
cheap (`203.067` at `e = 1/4`, `1505.821` at `e = 0`, seconds to compute) — the
`B1` blocker open since Phase 2 is **closed**. A rigorous residual enclosure at
`5.01e-3`, a `1.34e7 x` improvement on the historical `6.736713e4`, with zero
`z`-panels, zero softplus approximations and the R6 kernel untouched — the `B2`
blocker is **closed as a range-certification problem**. The certified enclosure
is consistent with Monte Carlo.

**Not established.** The product `C_SR * delta` is `5.4x` too large for a
usable `0.2` half-width, and the certification cost is `~1600x` the kernel cost,
putting even the `m = 1` SR first-moment lane at `3148` CPU-hours. Both trace to
the same root: the residual bound discards the `ghat` / `K_e ghat` cancellation.
Closing it requires bounding `osc(r)` directly, which is a new B2 refinement and
needs its own pre-result audit.
