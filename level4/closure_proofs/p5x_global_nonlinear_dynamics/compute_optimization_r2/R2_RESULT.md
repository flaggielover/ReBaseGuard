# P5X Compute Optimization R2 — result

```text
R2_SELFTEST         = PASS (S1-S8, 9/9)
B1                  = PASS,  half-width 0.008664502830320444  (threshold 0.2, unchanged)
MEASURED_SPEEDUP    = 14.448401737437928 (CPU)  ->  R2_BREAKTHROUGH
CERTIFIED_CORRESPONDENCE = PASS (overlaps R1)
R2_CAMPAIGN_CLASS   = R2_USEFUL_BUT_MORE_OPT_REQUIRED
FULL_COVER          = NOT AUTHORIZED, NOT LAUNCHED
```

---

## 1. Self-test, before the benchmark

All nine checks passed. The decisive one:

| check | result |
|---|---|
| `S1` coefficient agreement with the reference on the **real production polynomials** | exact overlap, all coefficients |
| `S2` resulting Bernstein bound, reference vs optimized | **ratio `1.0000`** — bit-identical bound |
| `S2` cost, reference vs optimized | `81.3 s` vs `6.8 s` — **`12.04x` on the primitive** |
| `S3` same equation assembly (`ra_certifier` imported unmodified) | yes |
| `S4` `e = 0` consistency, `ghat(0,0)` | `< 1e-12` |
| `S5` exact rational drift, exact tiling | yes |
| `S6` no empirical monotonicity | yes |
| `S7` depth ladder deterministic and bounded | `(0,1,2,3)` |
| `S8` derivative equation certified identically | yes |

`S2` is the important one: candidate C2 returns the **same bound**, not merely a
comparable one, at one twelfth of the cost.

## 2. Benchmark B1

CUSUM, `m = 1`, first moment with the derivative equation, `e in [0.24, 0.26]`,
8 sub-cells, 5 workers — the same cell and worker count as R1.

| quantity | R1 | R2 |
|---|---|---|
| enclosure | `[-1.5843524238144047, -1.5682610865345454]` | `[-1.584973380499857, -1.5676443748392161]` |
| half-width | `0.008045668639929672` | `0.008664502830320444` |
| subdivision depth | `3` (fixed) | `0` (ladder accepted at the first rung) |
| CPU | `1.1727245380555558` h | **`0.081166385` h** |
| wall | `1262.9 s` | **`90.5 s`** |
| peak RSS per worker | `218.1 MiB` | `76.2 MiB` |
| sub-cells / solves / Bernstein bounds / refinements | `8 / 24 / 16 / 0` | `8 / 24 / 16 / 0` |
| per sub-cell CPU | `527.73 s` | **`36.52 s`** |

**`SPEEDUP = 1.1727245380555558 / 0.081166385 = 14.4484`**, wall speedup `13.95x`.
Band: `>= 8x` → **`R2_BREAKTHROUGH`**.

The enclosure is `7.7%` wider — exactly the depth-0 looseness the ladder
accepted — and remains `23x` inside the frozen `0.2`.

## 3. B2, B3, B4

`B2` (primitive attribution) is reported as `S2` above: `12.04x` from C2 alone,
with C1 supplying the rest by removing the `256`-patch subdivision.

**`B3` (SR) and `B4` (`m = 5`) were NOT RUN because they are NOT RUNNABLE**: no
SR certifier and no `m > 1` certifier exist anywhere in P5X. This was declared in
`R2_FROZEN_SPEC.md` §3 before the benchmark, not discovered after it, and easier
cells were deliberately not substituted.

## 4. Certified correspondence

The R2 enclosure overlaps R1's and in fact **contains** it — the expected
relation for a valid but slightly looser bound of the same object. Both contain
the true `R_{CUSUM,1}(e)` on the cell. No contradictory certified interval.
`CERTIFIED_CORRESPONDENCE = PASS`.

## 5. The pre-registered prediction

Predicted before the run: `0.13` CPU-hours (band `0.08-0.30`), speedup `9.0`
(band `4-15`), total `~3.4e3` CPU-hours. Measured: `0.0812` CPU-hours (at the
optimistic edge of the band), speedup `14.45` (inside the band). The prediction
**held on speedup**; the CPU-hours came in at the band edge. The projected total
did **not** hold — see §6, and the reason is instructive.

## 6. Cost re-projection — and why the campaign total barely moves

| scope | pre-R2 | post-R2 |
|---|---|---|
| CUSUM `m = 1`, `[0, 12]` | `49.0` CPU-h | **`3.4` CPU-h** |
| CUSUM all `m`, both moments (`x36`) | `1,764` CPU-h | **`122` CPU-h** |
| SR all `m`, both moments | `~28,665` CPU-h | **`~28,665` CPU-h — UNCHANGED** |
| **total P5X** | `~30,500` | **`~28,787` CPU-h** |

**R2 is a `14.45x` breakthrough on CUSUM and only `~1.06x` on the campaign.**
The reason is the §9 finding of `R2_PROFILE_AND_AUDIT.md`: SR is `~94%` of the
projected cost, and SR **cannot use the optimized path at all**. C2 accelerates
the affine substitution inside the symbolic `z`-integration pipeline, and that
pipeline exists only because CUSUM's `q(x,z) = max(0, p + z - k)` is piecewise
affine in `z`. SR's `q(x,z) = log(1 + exp(y + z - 1/2))` is transcendental in
`z`; SR must use adaptive innovation partitioning instead, which inherits
nothing from R2.

**Counterfactual, recorded to size the prize:** if an SR certifier could use the
symbolic pipeline and inherit R2's `14.45x`, the total would be
**`~2,106` CPU-hours** — `R2_READY_FOR_FULL_COVER`. Making SR symbolic is
therefore worth roughly `13x` on the whole campaign, far more than any further
CUSUM optimization.

| effective cores | wall-clock, `~28,787` CPU-h |
|---|---|
| 8 | `3,598 h` (150 d) |
| 16 | `1,799 h` (75 d) |
| 32 | `900 h` (37 d) |
| 64 | `450 h` (19 d) |
| 128 | `225 h` (9.4 d) |

**RAM** `76.2 MiB` per worker (down from `218.1`), so `~10 GiB` at 128 cores.
**Storage** `~1.5 KiB` per sub-cell record, `~63 MiB` total. **Refinement rate**
`0`.

## 7. Bottleneck migration

Before R2: `_affine_to_unit_square`, `~80%` of a CUSUM certification.
After R2, within CUSUM: `_power_to_bernstein` and `_kernel_polynomials` now
share the load with the reduced affine step; per-sub-cell cost is `36.5 CPU-s`,
and no single routine dominates the way the affine substitution did.

**But the campaign-level bottleneck has migrated somewhere else entirely: to the
SR certifier that does not exist.** Its cost driver is mathematical (softplus is
not polynomial in the innovation), not implementational. No amount of further
CUSUM optimization can move the campaign total by more than `~0.4%`.

`NEW_DOMINANT_BOTTLENECK = SR certifier architecture (unbuilt; softplus
transcendence blocks the symbolic pipeline)`.

## 8. Campaign classification

Projected total `~28,787` CPU-hours `> 10,000` →
**`R2_CAMPAIGN_CLASS = R2_USEFUL_BUT_MORE_OPT_REQUIRED`**, applied mechanically
to the frozen bands. R2 succeeded at what it targeted and did not make the
campaign practically executable, because the target was not where the campaign's
cost lives.

## 9. Lean and scope

`LEAN_INTERFACE_CHANGED = NO` — C1 and C2 change only the range-bound
arithmetic; the certified scalars `R_max`, `s_min`, `M_2` and the `X1`-`X6`
assumptions are untouched. `SCIENTIFIC_SCOPE_CHANGED = NO`,
`SCIENTIFIC_TARGET_CHANGED = NO`; `e in [0, 12]` and the `0.2` threshold are
unchanged.
