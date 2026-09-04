# P5Y GATE 2D — PILOT-SR-REALCANDIDATE result

```text
P5Y_GATE2D_DECISION = SR_REALCANDIDATE_FAIL_REPRESENTATION
  (the artifact's mechanically-derived field reads FAIL_WITHIN_GRID; the frozen
   section-7 rule, applied to the artifact's own recorded precondition, governs —
   see results/gate2d_adjudication.json)
CPU USED = 4.47 CPU-seconds against a frozen 540 s cap (0.8%)
STOP_FIRED = NO ; BINDING = NO ; PRODUCTION RUN = NO ; CHECKPOINT = NO
```

The genuine candidate was built and rigorously certified. It is **better
conditioned than Gate-2A's stand-in by 20.4 digits**. It nonetheless fails,
and not because of precision: **Gate-2A's `P2` is a relative criterion
calibrated on a stand-in whose value is `O(76)`, and a real backward function's
panel integral here is `3.75e-09`.**

---

## 1. The genuine candidate

```text
represents  h_1^SR = 1 - K_e 1 = 1 - Phi(c_SR - a + e) + Phi(b - c_SR + e)
role        the first backward function of P5X-T1, already charged by Gate-1 MSHARE
bidegree    (16,16), 33 nonzero coefficients (separable), exact-dyadic at 2^-50
fit domain  the FULL state square [0, b_SR]^2 -- stronger than the patch
eps_cand    1.9301e-07   on the whole square
```

| chart | `eps` total | Chebyshev tail | degree-60 interp. error | dyadic rounding |
|---|---|---|---|---|
| `A = Phi(c_SR - a + e)` | `6.8782e-08` | `6.8782e-08` | `1.11e-31` | `3.12e-15` |
| `B = Phi(b - c_SR + e)` | `1.2423e-07` | `1.2423e-07` | `1.11e-31` | `3.65e-15` |

Not `unit_candidate`, not synthetic, not chosen for low condition number.
Build cost `0.004` CPU-s.

## 2. Guards — all passed

```text
complexity guard : bidegree (16,16), composed z-degree 128, score 37,281 of 100,000   PASS
P1 repair        : eps_P1 = 1e-3, h_z 0.19386661 -> 0.19383962, n_z = 28 UNCHANGED   PASS
reproducibility  : 384-bit duplicate run, endpoints and P2 identical                  PASS
no hidden high-degree object in the composed path                                     PASS
```

## 3. The precision grid — and why precision is not the story

| cell | `P2` | `P2` floor | acc radius | `|acc|` | digits lost | pass |
|---|---|---|---|---|---|---|
| genuine @256 | `3.5403e-02` | `3.5403e-02` | `1.11e-55` | `3.7473e-09` | **30.54** | no |
| genuine @384 | `3.5403e-02` | `3.5403e-02` | `2.81e-94` | `3.7473e-09` | 30.47 | no |
| genuine @512 | `3.5403e-02` | `3.5403e-02` | `6.09e-132` | `3.7473e-09` | 31.34 | no |
| control @256 | `7.5325e-10` | `7.5325e-10` | `6.02e-25` | `7.5937e+01` | **50.96** | yes |
| control @384 | `7.5325e-10` | `7.5325e-10` | `1.50e-63` | `7.5937e+01` | 50.89 | yes |
| control @512 | `7.5325e-10` | `7.5325e-10` | `3.41e-101` | `7.5937e+01` | 51.78 | yes |

`P2` equals its **precision-independent floor** at every precision; the
precision-dependent share is `< 3e-9` of `P2` and shrinks with bits. The
interval radius runs from `1.1e-55` to `6.1e-132` and is irrelevant to the
outcome. `failure_class = CANDIDATE_RESIDUAL_DOMINANT`.

## 4. Conditioning — the good news

```text
genuine candidate      30.54 digits lost      sup_g = 0.0270
unit_candidate control 50.96 digits lost      sup_g = 11.6523   (same run, same conditions)
delta_digits vs Gate-2A's 51.8   =   -21.26        vs same-run control = -20.43
```

On the conditioning question this gate was asked, the answer is **strongly
favourable**: a real backward function is `20.4` digits *better* conditioned
than the stand-in, so Gate-2A's 256-bit conclusion is conservative on that axis.

The frozen classification returns `SEVERE` — but only through its **second**
clause ("no safe precision `<= 512`"). On the `delta_digits` clause alone this
is `STABLE` by a wide margin. Both facts are reported because reporting only the
label would be misleading.

## 5. Root cause — scale, not precision and not separability

`P2` is a **relative** half-width. Gate-2A calibrated `P2 <= 1e-8` on
`unit_candidate`, whose panel integral is `|acc| = 75.94`. A genuine backward
function has enormous dynamic range across the SR square: `h_1` runs from
`~1e-9` near `a = 0` to `0.63` at `a = b_SR`, and at patch `(17,11)` its panel
integral is `|acc| = 3.75e-09`. The same *absolute* enclosure error (`~1.3e-10`)
therefore reads as a relative `3.54e-02`.

The dominant term is the candidate residual itself:
`eps_cand * N_0 / |acc| = 7.91`, i.e. a degree-16 uniform-absolute fit that is
excellent in absolute terms (`1.93e-07`) is worthless in relative terms where the
function is `1e-5`. Reaching the relative target would need
`eps_cand ~ 2.4e-16`, i.e. roughly **degree 35–40**. Degree 16 is insufficient
*for a relative criterion on this function*, which is squarely
`FAIL_REPRESENTATION` under the frozen sections 7 and 22.

**It is not separability.** The non-decisive non-separable probe
`hhat_2 = K_e h_1` (289 rigorous `acb.integral` node enclosures) fails by the
same mechanism: `|acc| = 9.04e-06`, `P2 = 6.96e-06 = its own floor`. Function
scale, not structure.

*Probe caveat:* its node values were enclosed at 256 bits, so its coefficient
radii do not shrink with evaluation precision and its 512-bit digit-loss figure
(`86.55`) is a construction artifact. Only its 256-bit figure (`43.18`) is
meaningful, and it is non-decisive either way.

## 6. Recorded implementation defect — not patched

`sr_realcandidate.py` computes the acceptance precondition **after** the
precision cells and never branches on it, so the frozen section-7 gate was not
enforced in code and the decision field fell through to the selection rule.
Blast radius is naming only: both outcomes are failures, the artifact records
the measured precondition (`7.91 > 1e-8`, `P2_target_reachable: false`), and the
frozen rule is applied on top of the artifact. **Not patched** — no post-T2
mutation is permitted, and a test asserts the module is byte-identical to its T1
hash. The successor must evaluate and branch on the precondition *before* the
grid, and assert that ordering in a pre-T2 test.

## 7. Consequence

Gate-2A's SR **precision** conclusion is not invalidated — with a real candidate
the conditioning is better, so 256 bits remains supported on that axis. What is
invalidated is the **`P2` acceptance instrument**: a relative criterion cannot be
applied to real backward functions spanning nine orders of magnitude. That is a
new, named, well-understood gap. The cost model is unchanged; nothing here moves
a CPU band.

```text
P5Y_FIRST_BINDING_CHECKPOINT_READY = NO
```

## 8. Boundary

`K2` `s_min`, `K3` `M_2`, `K4` `H2`, `K5` `H3a` remain unresolved. P5, P5X and
Gates 1/2A/2B/2C/2C-bis are untouched.
