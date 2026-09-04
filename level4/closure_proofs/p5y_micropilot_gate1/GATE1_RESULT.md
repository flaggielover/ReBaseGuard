# P5Y MICRO-PILOT GATE 1 — result

```text
P5Y_GATE1_DECISION = GATE1_PASS_ROUTE_B_SUPPORTED
PILOT_RAW_2CELL    = PASS
PILOT_SR_DEGREE    = PASS   (degree 8 selected)
PILOT_SR_XI        = NOT_RUN (frozen condition: runs iff M2 fails; analytic part reported)
CPU USED           = 0.2114 CPU-hours   against a 5.0 cap and a 3.0 preference
STOP_FIRED         = NO
BINDING            = NO ;  PRODUCTION RUN = NO ;  CHECKPOINT = NO
```

Decision reached mechanically by `GATE1_PREREGISTRATION.md` section 5, CASE A.
No narrative override was applied and none was available.

---

## 1. M1 — PILOT-RAW-2CELL = PASS

Identity `I1` (`rho_{1,e} + e h_1 = phi(u+e) - phi(l+e)`) verified exactly
(`< 1e-12` over 9 drifts x 16 states) **before** execution, together with `I3`.

| | CELL A `e in [0.24,0.26]` | CELL B `e in [10.5441104,12]` |
|---|---|---|
| sub-cells (frozen ladder) | 8, `h = 0.00125` | 4, `h = 0.1819862` |
| **raw enclosure** | `[-1.581636424, -1.570725487]` | `[-0.026426199, +0.026425263]` |
| **z control enclosure** | `[-1.584973380, -1.567644375]` | `[-1.223835279, +1.223835277]` |
| raw half-width | `0.005455468` | **`0.026425731`** |
| z half-width | `0.008664503` | **`1.223835278`** |
| ratio | raw `1.59x` tighter | raw **`46.31x`** tighter |

* `A1` the raw enclosure overlaps the historical R2 anchor
  `[-1.584973380499857, -1.5676443748392161]`; it is in fact **strictly inside**
  it, the expected relation between two valid enclosures of the same number.
* The z control arm reproduced R2's published interval to `1e-12` on the lower
  end and `1e-10` on the upper — so the comparison is genuinely ceteris paribus,
  not a reconstruction.
* `A2` `0.0264 < 1.0`; `A3` `0.0264 < 0.75`; `A4` `0.00546 <= 0.05`. All frozen
  thresholds met, the far-field one by a factor of `37.8`.
* The raw arm is also `1.11x` **cheaper** per sub-cell (`30.85` vs `34.31` CPU-s).

**Honest divergence from the brief's historical record.** The brief reports the
historical failing cell at half-width `2.3368`. The z control arm measured here
gives `1.2238` on the same cell, and it fits inside `(-2,2)`. The difference is
the sub-cell plan: the frozen ladder requires exact tiling, which forced `n = 4`
(`h = 0.182`) rather than the `h = 0.313` that `h = 1/(4aC)` alone would allow.
So this gate did **not** reproduce a z-variable failure on that cell; what it
established is stronger in one way and weaker in another, and both are recorded:
under strictly identical machinery, cover, resolvent and precision, the raw
representation is `46.3x` tighter in the far field — but the specific historical
`2.3368` was not reproduced and the z arm did not fail here.

## 2. M2 — PILOT-SR-DEGREE = PASS, degree 8 selected

Same detector, same `e = 1/4`, same patch `(17,11)`, same candidate, same `192`
bits as R3. Dyadic rounding replaced by the frozen continuous minimal-safe rule.

| degree | `n_z` | `t_panel` (ms) | cost `n_z t_panel` (s) | maths | verdict |
|---|---|---|---|---|---|
| 6 (control, not selectable) | 67 | 3.889 | 0.2606 | **`P1` knife-edge FAIL** | FAIL |
| **8** | **28** | **5.797** | **0.1623** | **all pass** | **PASS** |
| 10 | 17 | 6.776 | 0.1152 | **`P2` FAIL (`0.992`)** | FAIL |
| 12 | 13 | 6.978 | 0.0907 | **`P2` FAIL (`0.999`)** | FAIL |

Budget `0.3314531805`; degree 8 sits `2.04x` inside it (`2.11x` excluding the
moment recursion, `1.94x` including it). Timing spread over 5 frozen repeats:
`9.0%` at degree 8.

**Finding 1 — the dyadic rounding was the whole of R3's cost failure.** At the
frozen degree 6 the continuous rule alone gives `n_z = 67` instead of `128` and
a cost of `0.2606 s`, which is **inside** the R3 budget that historically failed
at `0.5007 s`. The mathematics never needed to change.

**Finding 2 — higher degree is NOT monotonically better, and this falsifies the
extrapolation in R3's own diagnosis table and in the pre-gate architecture
audit.** Degrees 10 and 12 are cheaper *and mathematically dead*: the composed
contraction `sum_k c_k N_k` loses precision catastrophically as the panel widens.

| degree | composed degree | integrated enclosure |
|---|---|---|
| 6 | 96 | `9.89394200581790040712 +/- 2.89e-21` |
| 8 | 128 | `75.972 +/- 3.15e-4`   (**~17 digits lost**) |
| 10 | 160 | `+/- 1.42e+12`  (**destroyed**) |
| 12 | 192 | `+/- 2.33e+26`  (**destroyed**) |

The frozen rule — a faster candidate that fails a mathematical gate is FAIL —
was applied without relaxation, without raising the precision after the fact and
without extending the grid.

**Risk recorded, not resolved: degree 8 passed `P2` with only `1.34x` margin
(`7.45e-7` against `1e-6`) and had already lost 17 digits.** A production SR
certifier will very likely need more than 192 bits, and this gate did not
measure that cost. It is the dominant term in the updated cost bands.

**Defect recorded, not patched (`STOP` rule `S2`).** The continuous rule solves
`E_d = 1e-9` to *equality*, so `P1` is decided in the 17th significant digit by
float rounding: degree 6 landed `6.3e-17` above the threshold and failed, degrees
8/10/12 landed just below and passed. Blast radius is nil — degree 6 is
`control_only_not_selectable` by the preregistration, degree 8 (selected) passed,
and degrees 10/12 failed on `P2` by six orders of magnitude, not on `P1`. The fix
for a successor is to target `(1-eps) * 1e-9` with a declared `eps`, or to carry
`h_z` as an exact rational rounded down. It was **not** applied here because it
would change a reported verdict and is therefore not reporting-only.

## 3. M3 — PILOT-SR-XI = NOT_RUN (back-end), analytic part reported

The frozen condition is "M3 runs iff M2 fails". M2 passed, so no back-end was
built. The predeclared non-decisive analytic part ran:

| check | result |
|---|---|
| `X1` transform `exp(softplus(v)) = 1 + xi e^{z-1/2}` and alarm equivalence | verified, max relative error `1.87e-56` |
| `X3` induced panel count | **exactly 127** = the closed-form bound `2(grid-1)+1`; within the frozen threshold 127, **outside the brief's default 100** (disclosed pre-T2) |
| `X4` panel-centred conditioning | `e^{16 h} = 2.19`, bounded |
| `X2` exponential-Gaussian moment identity | **flagged a real obstacle** |

**New obstacle, previously unrecorded.** `G_c(L,U) = e^{c^2/2 - c(z_c+e)}
[Phi(z_hi+e-c) - Phi(z_lo+e-c)]` is mathematically **correct** — at 512 and 1536
bits it matches the independent series to 15 digits. But at `c = 16` and 192 bits
the closed form evaluates to `[+/- 0.0558]`, i.e. *nothing*: it passes through
`e^{128.7} ~ 1.5e56` multiplied by a Gaussian tail difference `~3e-58`. Required
extra precision scales as `~0.217 c^2` decimal digits, so a candidate of degree
16 needs roughly `400+` bits. This was invisible to the pre-gate architecture
audit, which reasoned correctly that the *integrand* is bounded and wrongly that
the *representation* therefore is. Recorded in
`results/m3_precision_addendum.json`.

Self-criticism carried forward: the frozen `X2` check compared ball **midpoints**,
which is why it reported a 22.7% "disagreement" rather than "the closed form has
no significant digits". A successor's identity checks must compare enclosure
**radii**.

## 4. Optional predeclared checks — all PASS, all non-decisive

| check | result |
|---|---|
| `PILOT-MSHARE` | the `m=2` function set is a subset of the `m=5` set; **no `m`-specific solve exists**. Union `49` functions against the historical lane's `86`: multiplier **`24.5x`, not `43x`** — the historical figure over-counts by `1.76x` because it summed over `m` instead of taking the union |
| `PILOT-FARFIELD2` | outward-rounded `B1` reproduces `PROOF.md` L3.4's published values exactly (`5.369774534e-10` CUSUM, `8.573901857e-07` SR at `e=12`). The proposed `L3'` majorant gives `S >= 0.9998` (CUSUM) and `S >= 0.9848` (SR) at `e = 10` |
| `PILOT-SMIN-ANALYTIC` | minimum conditional variance found `0.0403` at `(e=1, L=-4.5, U=6.5)`, strictly positive. **Explicitly a scoping scan, not a certificate.** It is `12x` looser than the measured `s_min = 0.478` at `m=1` and `45x` looser at `m=5`, so it can support positivity but **not** the quantitative dispersion claim — a downward correction to the pre-gate audit's expectation of `0.2-0.3` |

## 5. Updated cost model — from pilot-measured timings only

Inputs measured here: SR `t_panel = 6.106 ms` (incl. moments) at `n_z = 28`;
CUSUM raw `30.85` CPU-s per sub-cell; multiplier `24.5x`. No optimistic
historical estimate is reused.

```text
SR    per certified function  =  47.98 CPU-hours
SR    per unit (value+deriv)  =  95.97 CPU-hours
CUSUM per unit                =   2.86 CPU-hours
+17% for the H2/H3a derivative rung, +15% assembly/resolvent/audit overhead
```

| band | assumption | CPU-hours | 16 cores | 64 cores | 128 cores |
|---|---|---|---|---|---|
| optimistic | 192 bits suffices; `m>1` per-function cost = `m=1` | **3,258** | 214 h | 57 h | 32 h |
| central | 256 bits on SR to restore the `P2` margin | **4,840** | 318 h | 84 h | 47 h |
| conservative | 384 bits; `m>1` functions `1.5x` | **14,377** | 946 h | 250 h | 140 h |
| worst plausible | 512 bits; `m>1` functions `2x` | **31,823** | 2,094 h | 552 h | 311 h |

Against R3's projected `12,084` SR CPU-hours and the pre-gate audit's `6,000`
central. The dominant uncertainty has **migrated from panel count to working
precision**.

## 6. What this gate did NOT establish

No cover, no `m > 1` certification, no second moment, no `s_min`/`M_2`, no
`H2`/`H3a`, no Lean, no production. `NOVELTY_STATUS = NOT_ESTABLISHED`.
`LEVEL4_GLOBAL_CLOSURE = NO`. P5 and P5X are untouched and remain `PARTIAL`.
