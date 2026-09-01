# Cross-priority reproduction — independent replay of the dependency chain

P9 does **not** rerun any campaign. It reproduces a small set of anchors chosen
so that together they exercise the whole chain: exact algebra (P3) → the exact
structural identity (P5) → the operational consequence (P7). Every anchor is
computed by `experiments/reproduce_anchors.py`, an implementation written from
the published model specification that **imports no P1–P8 module**.

**No P8 anchor is run.** P8 is unadjudicated (`P8_DEPENDENCY_GATE.md`).

| control | value |
|---|---|
| implementation | independent; shares no code with P1–P8 |
| seeds | derived deterministically, `seed = SHA-256(label fields)`; no seed chosen by hand |
| SR numerics | log-domain `logaddexp` recurrence, algebraically identical to the frozen form, chosen for stability at `A ~ 521` |
| censoring | `MAX_STEPS = 200000`; never reached at these operating points |
| replay | `/Users/suzhe/ReBaseGuard/level4/.venv/bin/python experiments/reproduce_anchors.py` |

---

## A1 — P3 exact witnesses · **EXACT · PASS**

Independent `Fraction` arithmetic, no floating point.

| witness | `m=1` | `m=2` | `m=3` | `m=5` |
|---|---|---|---|---|
| CUSUM-compatible gain | `15/2` | `15/2` | `15/2` | `15/2` |
| reproduced `rho_c` | `2/13` | `2/13` | `2/13` | `2/13` |
| SR-compatible gain | `4` | `3` | `8/3` | `12/5` |
| reproduced `rho_c` | `1/3` | `1/2` | `3/5` | `5/7` |

All eight match `P3-X1` exactly, and `|rho_c (1 - GammaTilde)| = 1` holds
**exactly** in rational arithmetic in all eight cases. Expected: exact.
Reproduced: exact. Uncertainty: none. Type: exact.

## A2 — P3 Gaussian `rho_c` from the published P1/P2 gains · **PASS**

Recomputing `rho_c = 1/|1-GammaTilde|` from `P1-N1`/`P2-N1`:

* max absolute difference from the published `P3-N1` boundaries: **`4.882e-10`**
* tolerance `1e-9` (set by the 9-decimal rounding of the published table)
* `P3-N2` ordering check — SR boundary strictly below CUSUM at every supported
  `m`: **reproduced**

Type: exact algebra on published inputs. This validates the P1/P2 → P3 edge.

## A3 — P5 raw-mean identity · **EXACT · PASS**

`P5-T1` states `e_{j+1} = rho * (raw window mean) + (1-rho) * fresh`, i.e. the
entering error cancels from `e + zbar_w`. Checked over 18 cells
(2 detectors × `m in {1,2,5}` × `rho in {0, 0.25, 1}`), 4000 paths each, with
randomly drawn entering errors and randomly drawn `w in {1..m}`:

* max absolute difference between the Stage-D update form and the raw-mean form:
  **`8.882e-16`** (machine epsilon)
* tolerance `1e-12`

Type: algebraic identity confirmed to machine precision. This is the single most
load-bearing exact claim in the project — it is what makes `P5-T7`, `P5-MECH`,
`P7-A` and `P9-T2` possible — and it reproduces exactly.

## A4 — P7 operational degradation · **PASS with a convention finding**

12000 paths, 12 cycles, cycle 1 discarded.

| quantity | P7 published | P7's own replay | P9 independent |
|---|---|---|---|
| nominal `A(0)` CUSUM | `465.12` | `447–492` | `452.55 ± 4.07` (and `467.6` at a second seed) |
| nominal `A(0)` SR | `464.86` | `447–492` | `462.65 ± 4.19` |
| fresh `rho=0` ARL | `79.91–162.03` | `78.92–164.12` | `78.84–162.11` |
| full reuse `rho=1` ARL | `48.36–80.05` | `47.73–80.40` | `45.21–79.25` (discard 1) |
| loss vs nominal | `82.8%–89.6%` | reproduced | `82.5%–90.2%` |
| loss vs fresh | `39.5%–50.6%` | reproduced | `41.6%–51.1%` |
| **cycle-2 collapse** | `5.6–9.4` | — | **`5.63–8.83`** |

The fresh-reference range and the cycle-2 collapse reproduce closely. Two cells
needed investigation rather than assertion:

**The nominal `A(0)` CUSUM cell** came out at `z = -3.09` against the published
point. A second independent seed gave `467.6`, and P7's own replay range is
`447–492`, which contains both P9 values. Diagnosis: Monte Carlo scatter of a
heavy-tailed run-length mean (`D-12`, `CONSISTENT_WITH_MC`). P9 reports both of
its values, not the more favourable one.

**The full-reuse low end** (`45.21` vs `48.36`) is a **burn-in convention
effect**, established below, not a disagreement (`D-11`).

## A5 — burn-in sensitivity · **P9-original finding**

Measuring mean cycle length **by cycle index** under full reuse:

```text
SR,    m=1, rho=1:  460.5,  5.8, 73.7, 38.2, 53.6, 46.0, 48.6, 46.4, ... -> ~48.5
CUSUM, m=1, rho=1:  467.6,  5.6, 74.4, 40.3, 54.0, 46.5, 50.5, 47.7, ... -> ~50.0
```

The approach to stationarity is **slow and oscillatory**, not monotone:

| convention | SR `m=1` | CUSUM `m=1` |
|---|---:|---:|
| discard cycle 1 | `46.96` | `48.34` |
| discard 3 | `47.81` | `49.33` |
| discard 6 | `48.22` | `49.84` |
| discard 10 | `48.49` | `49.97` |
| pool all cycles | `67.64` | `69.31` |

At discard-10 the SR value is `48.49` against P7's `48.36` — agreement to
`0.13`. The apparent `3.15` gap was entirely convention. Pooling all cycles
inflates the estimate by `~40%` because the perfect first cycle is included.

Recorded as claim `P9-N1` and crosswalk row `X-08`. It is consistent with
`P5-T7` (uniform geometric ergodicity holds, but its constants are loose, so the
*rate* is empirical) and it sharpens `P7-E2`: one-cycle calibration is
misleading, and so is few-cycle calibration.

## A6 — `P9-T2` mixture correspondence and `P7-A`'s premise · **PASS**

`A(e)` measured on an 81-point half-grid (even reflection, 2500 paths/node),
mixture formed by quadrature, compared against the *separate* recursive
`rho = 0` simulation:

| cell | `A(0)` | `A(1 sigma)` | `E[A(e)]` quadrature | `rho=0` ARL recursive |
|---|---:|---:|---:|---:|
| CUSUM `m=1` | 468.0 | 10.35 | 83.72 | `82.08 ± 0.52` |
| CUSUM `m=5` | 469.7 | 48.51 | 162.41 | `162.11 ± 0.71` |
| SR `m=1` | 480.7 | 10.49 | 79.93 | `78.84 ± 0.51` |
| SR `m=5` | 471.2 | 42.12 | 154.88 | `155.67 ± 0.70` |

Two independent estimators of the same quantity agree to `0.3–1.6`. The
quadrature carries truncation and grid error, so this is **agreement, not an
identity check** — P9 does not call it an identity.

The same grid tests `P7-A`'s structural premise that `A` is even and
non-increasing in `|e|`: across 4 cells and 320 adjacent-node comparisons there
are **0 violations at 3 standard errors**. `P7-A`'s premise is therefore
independently corroborated rather than assumed.

*(An earlier attempt used 21-node Gauss-Hermite quadrature and gave `134.19`
against a measured `82.08`. That was a quadrature-resolution failure, not a
result: `A(e)` falls from `468` to `10.35` within one standard deviation, and 21
nodes cannot resolve it. The failure is recorded because discarding it silently
would be selective reporting.)*

---

## Anchors deliberately **not** reproduced

| anchor | why not |
|---|---|
| P1/P2 `GammaTilde` derivative estimates | correctly reproducing these needs the score-route machinery at ~10^6 paths; P9 reproduces their *consequence* (A2) instead, which validates the edge without re-running the campaign |
| P4 location-family cells | P4 is `PARTIAL`; re-running its cells would risk being read as re-adjudication (`U3`) |
| P6 policy anchor | P6 is `PARTIAL` with `G6` a statistical `MATERIAL_DEFECT`; a P9 reproduction could not settle that and might be misread as doing so |
| **any P8 anchor** | **P8 is unadjudicated** (`P8_DEPENDENCY_GATE.md`) |

## Summary

| anchor | verdict | type |
|---|---|---|
| A1 P3 exact witnesses | **PASS** | exact |
| A2 P3 Gaussian `rho_c` | **PASS** (`4.9e-10`) | exact algebra |
| A3 P5 raw-mean identity | **PASS** (`8.9e-16`) | exact identity |
| A4 P7 operational | **PASS**, 2 cells explained | numerical |
| A5 burn-in | **finding** (`P9-N1`) | numerical |
| A6 `P9-T2` + `P7-A` premise | **PASS** | numerical |

Every edge in the dependency chain that P9 relies on for its own theorem
(`P5-T1 -> P5-T7 -> P7-A -> P9-T2`) is reproduced by independent code.
