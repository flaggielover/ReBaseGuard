# P5Y GATE 2A — PILOT-SR-PRECISION result

```text
P5Y_GATE2A_DECISION = SR_PRECISION_PASS_256
SELECTED SAFE PRECISION (degree 8) = 256 bits
RECOMMENDED BACKEND (frozen rule)  = DEGREE10_CONTINUOUS @ 256 bits
FAILURE CLASS                      = PRECISION_INSUFFICIENT (both degrees)
CPU USED = 0.000113 CPU-hours   against a 0.10 cap  (0.11% of cap)
STOP_FIRED = NO ; BINDING = NO ; PRODUCTION RUN = NO ; CHECKPOINT = NO
```

Reached mechanically by `GATE2A_PREREGISTRATION.md` §9. No narrative override.

---

## 1. The precision grid

Panel geometry frozen from Gate-1 and **bit-identical across every cell**
(`n_z = 28` at degree 8, `17` at degree 10) so precision is the sole variable.

| cell | `n_z` | `P2` | `P2` floor | `acc` radius | digits lost | precision consumed | `t_panel` | cost | verdict |
|---|---|---|---|---|---|---|---|---|---|
| d8@192 *(control)* | 28 | `7.4487e-07` | `7.538e-10` | `5.65e-05` | 51.7 | 89.4% | 5.897 ms | 0.1651 | **P2 FAIL** |
| **d8@256** | 28 | **`7.5376e-10`** | `7.538e-10` | `4.58e-24` | 51.8 | 67.3% | 6.091 ms | 0.1705 | **PASS**, 13.3x |
| d8@384 | 28 | `7.5376e-10` | `7.538e-10` | `1.41e-62` | 51.9 | 44.9% | 7.087 ms | 0.1984 | PASS, 13.3x |
| d8@512 | 28 | `7.5376e-10` | `7.538e-10` | `3.41e-101` | 51.8 | 33.6% | 8.333 ms | 0.2333 | PASS, 13.3x |
| d10@192 *(control)* | 17 | `9.9187e-01` | `1.618e-10` | `1.40e+12` | 57.8 | 100% | 7.159 ms | 0.1217 | **P2 FAIL** |
| **d10@256** | 17 | `3.6342e-10` | `1.618e-10` | `1.14e-07` | 67.4 | 87.4% | 7.345 ms | 0.1249 | **PASS**, 27.5x |
| d10@384 | 17 | `1.6184e-10` | `1.618e-10` | `3.53e-46` | 67.4 | 58.3% | 8.387 ms | 0.1426 | PASS, 61.8x |
| d10@512 | 17 | `1.6184e-10` | `1.618e-10` | `8.56e-85` | 67.3 | 43.7% | 9.434 ms | 0.1604 | PASS, 61.8x |

Every inherited gate (`P1`, `P3`, `T1`, `T2`, `T3`, `T5`, `T6`, `T7`, `T8`)
passes in **every** cell. `P3` margin at 256 bits is 45.6 orders of magnitude.

## 2. Diagnosis — `PRECISION_INSUFFICIENT`, both degrees

Classified from interval **radii**, never midpoints:

```text
degree 8 : 5.65e-05 -> 4.58e-24 -> 1.41e-62 -> 3.41e-101   monotone, contracting
degree 10: 1.40e+12 -> 1.14e-07 -> 3.53e-46 -> 8.56e-85    monotone, contracting
```

The Gate-1 degree-10 explosion was **purely a 192-bit artefact**, not intrinsic
ill-conditioning: the mathematically identical expression contracts cleanly once
precision is adequate. No `MATHEMATICALLY_FALSE`, no `IMPLEMENTATION_DEFECT`.

**Quantitative law extracted.** `digits_lost` is a *constant* of the
configuration, independent of precision (51.8 at degree 8, 67.4 at degree 10 —
i.e. fixed amplifications of `~1e52` and `~1e67`). Required precision is
therefore predictable:

```text
required decimal digits  ~  digits_lost + log10(1 / P2_floor)
degree 8 :  51.8 + 9.1 = 60.9 digits = 203 bits   -> 256 suffices
degree 10:  67.4 + 9.8 = 77.2 digits = 257 bits   -> 256 is exactly borderline
```

`P2` **floors** at a precision-independent value set by the softplus truncation
remainder (`7.54e-10` degree 8, `1.62e-10` degree 10). Both floors are below the
`1e-8` safety target, so the target is reachable — this was the pre-declared
condition under which the pilot could have failed outright, and it did not.

## 3. Reproducibility

Degree 8 @ 384 bits computed twice in the same run: **ball-identical**, both
endpoints and `P2` bit-for-bit equal. `t_panel` differed (7.087 vs 7.182 ms) as
expected — timing varies, the enclosure does not.

## 4. Selection and the degree-10 replacement

`P2 <= 1e-8` first holds at **256 bits** for degree 8 → `SR_PRECISION_PASS_256`.

Degree 10 satisfies every frozen replacement condition of §10, checked
individually rather than accepted as a bundle:

| condition | value | met |
|---|---|---|
| (a) `P2 <= 1e-8` | `3.634e-10` | yes |
| (b) all inherited gates | all pass | yes |
| (c) margins **not worse** than degree 8 at 256 | `P2` `3.63e-10 <= 7.54e-10`; floor `1.62e-10 <= 7.54e-10` | yes — strictly **better** |
| (d) `>= 20%` cheaper | `0.1249 / 0.1705 = 0.732`, **26.8% cheaper** | yes |

So this is not "faster therefore better": degree 10's safety margin at 256 bits
is 27.5x against degree 8's 13.3x.

**Two risks recorded against that recommendation, neither of which the frozen
rule captures:**

1. **Degree 10 @ 256 is not precision-saturated.** Its `P2` (`3.63e-10`) still
   sits 2.2x above its own floor (`1.62e-10`); degree 8 @ 256 is exactly at its
   floor. Saturation for degree 10 needs 384 bits.
2. **Degree 10 @ 256 consumes 87.4% of the available precision** against degree
   8's 67.3%. The amplification (`1e67` vs `1e52`) was measured with the
   *representative* `unit_candidate`, not a production exact-dyadic candidate.
   If a real candidate raises the amplification by even 10 digits, degree 10 @ 256
   fails while degree 8 @ 256 still has ~10 digits in hand.

The saturated alternative, degree 10 @ 384, is only **16.4% cheaper** than degree
8 @ 256 and therefore does **not** clear the frozen 20% bar. Reported so that a
successor sees the whole trade rather than one cell of it.

## 5. Measured precision scaling — my Gate-1 assumption was wrong

| bits | measured `t_panel` multiplier vs 192 | Gate-1 **assumed** multiplier |
|---|---|---|
| 256 | `1.033` (d8) / `1.026` (d10) | `1.5` (central band) |
| 384 | `1.202` / `1.172` | `3.0` (conservative band) |
| 512 | `1.413` / `1.318` | `5.0` (worst band) |

My pre-registered Gate-2A prediction (`1.2-1.6x` / `1.8-3x` / `2.5-5x`) is
**falsified on the pessimistic side**, as is the Gate-1 cost model's precision
assumption. Precision is nearly free at these polynomial sizes because the cost
is dominated by Python-level object handling, not by Arb limb arithmetic.

The `P1` prediction **held**: its margin is `4.32e-16` (degree 8) and identical
to 18 decimal places across 256/384/512, confirming Gate-1's finding that the
`P1` knife edge is a panel-rule construction defect and **not** a precision
artefact. It remains the one gate without healthy headroom, and it remains free
to fix (target `(1-eps) * 1e-9`).

## 6. Updated P5Y cost model

SR unit (value + derivative) over the full SR cover, from measured timings:

```text
degree 8  @256 = 95.73 CPU-h    @384 = 111.38    @512 = 130.97
degree 10 @256 = 70.09 CPU-h    @384 =  80.03    @512 =  90.02
CUSUM unit = 2.86 CPU-h ;  m-sharing multiplier 24.5x (carried forward)
+17% H2/H3a derivative rung ; +15% assembly/resolvent/audit overhead
```

| band | configuration | CPU-h | 16 cores | 64 cores | 128 cores |
|---|---|---|---|---|---|
| optimistic | degree 10 @ 256 | **2,405** | 158 h | 42 h | 23 h |
| central | degree 8 @ 256 (saturated, safer) | **3,250** | 214 h | 56 h | 32 h |
| conservative | degree 8 @ 256, `m>1` x1.5, cover x1.25 | **6,058** | 399 h | 105 h | 59 h |
| worst plausible | degree 8 @ 384, `m>1` x2, cover x1.5 | **11,204** | 737 h | 195 h | 109 h |

Against Gate-1's `3,258 / 4,840 / 14,377 / 31,823`. The conservative and worst
bands fall by `2.4x` and `2.8x` purely because precision turned out cheap.
The remaining band spread is now driven by the **unmeasured** `m>1` per-function
cost and the **inherited, never-measured** SR cover size (`835` sub-cells x
`1210` patches) — not by precision.

## 7. Feasibility

```text
selected precision 256 <= 256   AND   central 3,250 <= 5,000   ->  STRONG
```

## 8. What this pilot did NOT establish

No cover, no second moment, no `s_min`/`M_2`, no `m>1`, no `H2`/`H3a`, no Lean,
no xi back-end, no degree 12. The `unit_candidate` is a representative stand-in,
not a production exact-dyadic candidate. P5, P5X and Gate-1 are untouched.
`NOVELTY_STATUS = NOT_ESTABLISHED`. `LEVEL4_GLOBAL_CLOSURE = NO`.
