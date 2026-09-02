# Full-cover cost projection from the passing R-A′ stop-gate

Required by the frozen protocol **before** any production launch. Nothing was
launched.

## 1. Measured basis

From `results/ra_stop_gate.json`: `645.75 s` per sub-cell (three certified
solves and two Bernstein continuum bounds each), `~215 s` per certified solve,
peak `257 MiB` per worker, single-threaded per sub-cell and embarrassingly
parallel across them.

## 2. Cell count is set by the resolvent, and the resolvent is set by the drift

`h(e) = 1 / (4 a C(e))`, `a = 2 phi(0)`, so the cover density is
`1/(2h) = 2 a C(e)`:

| `e` | `C(e)` | `h(e)` | sub-cells per unit `e` |
|---|---|---|---|
| `0` | `5323.42` | `5.89e-5` | `8495` |
| `0.25` | `1124.65` | `2.79e-4` | `1795` |
| `0.5` | `150.88` | `2.08e-3` | `241` |
| `1` | `19.56` | `1.60e-2` | `31` |
| `2` | `5.76` | `5.44e-2` | `9.2` |
| `5` | `2.00` | `1.56e-1` | `3.2` |
| `6.5` | `1.19` | `2.64e-1` | `1.9` |
| `12` | `1.00` | `3.13e-1` | `1.6` |

The cover is overwhelmingly concentrated in `|e| < 0.5`; beyond `e ~ 2` it is
almost free. This is the opposite of the failed method, whose cost exploded in
the far field.

## 3. Projections

| scope | sub-cells | CPU-hours |
|---|---|---|
| CUSUM, `m = 1`, `e in [0, 12]` (frozen `e_far`) | `~1565` | **`281`** |
| CUSUM, `m = 1`, `e in [0, 6.5]` (`P5X-T3` takes over — flagged, not adopted) | `~1556` | `279` |

| effective cores | wall-clock for CUSUM `m = 1` |
|---|---|
| 8 | `35.1 h` |
| 16 | `17.5 h` |
| 32 | `8.8 h` |
| 64 | `4.4 h` |

**Peak RAM:** `~257 MiB` per worker, so `~2 GiB` at 8 cores, `~16 GiB` at 64.
**Storage:** `~1.5 KiB` per sub-cell record, `~2.3 MiB` for the CUSUM `m = 1`
cover; negligible.
**Adaptive refinement rate:** zero by construction — `h` is a closed formula of
`C`, so the cover is fixed before the first solve and no cell is ever revisited.
**Far-field certifiability:** confirmed. The truncation is `e`-independent
(`5.84e-12` at `e = 12`) and `C(12) = 1.000`, so far-field cells are the
cheapest in the cover. Confidence high.

## 4. Why the full eight-cell campaign is *not* yet affordable

| extension | cost multiplier | reason |
|---|---|---|
| `m in {1,2,3,5}` | `~11x` | `P5X-T1(c)` needs `g_r` for `r = 0..m-1` plus the `h_j`, so roughly `m` value solves and `m` derivative solves per sub-cell; `1+2+3+5 = 11` |
| second moments (`L2`, needed for `s_min` and `M_2`, hence for `P5X-T6`) | `~O(m^2)` more solves | pair functions `G_{r,r'}` and the `z^2`-weighted operator |
| SR | `~5–8x` on top | measured ratio of the existing `Gamma` certificates; plus the corrected domain of erratum `D1` |

A defensible envelope for the whole of `P5X-T4` + `P5X-T6` across both detectors
and all four windows is therefore **`O(10^4)` CPU-hours**, against the
`300–800` CPU-hours anticipated in `CERTIFICATE_PLAN.md` §6. That estimate was
made before the per-cell cost of a *rigorous* drift treatment was known, and it
was wrong by one to two orders of magnitude.

## 5. Consequence for authorisation

`FULL_COVER_AUTHORIZED = NO`. The stop-gate passed and the method is sound, but
the frozen budget does not cover the frozen scope, and the protocol does not
authorise production that exceeds it. Launching `~10^4` CPU-hours on the current
design would be exactly the kind of unbudgeted scaling the stop-gate exists to
prevent.

## 6. The identified cost reduction, recorded and not applied

The cover is dominated by `e < 0.5`, where `h = 1/(4 a C)` is small purely
because the **block-forcing** resolvent bound is loose there: `C(0) = 5323`
against the already-certified monotone-minorant value `1315.79` at `e = 0` and a
true `sup_x E_x[tau] ~ 465`. Since cell count scales linearly in `C`, replacing
the block-forcing bound by a drift-explicit **monotone one-sided minorant** in
the dominant region would cut the CUSUM `m = 1` cover by roughly `4x`, to
`~70` CPU-hours, and the full campaign proportionally.

This is **not applied here**. It changes a frozen element of
`RA_FROZEN_SPEC.md` §7, so it requires its own pre-result specification and
anchor, exactly as `R-B` does. Applying it now, after seeing the cost, would be
post-hoc tuning.
