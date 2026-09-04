# P5Y GATE 2C-bis — PILOT-M2-ASSEMBLY-B result

```text
P5Y_GATE2CBIS_DECISION = M2_ASSEMBLY_B_PASS
ratio_incremental = 1.2577   -> MODERATE      ratio_per_unit = 0.6289
correspondence    = PASS      representation guard = PASS
CPU USED = 81.71 CPU-seconds against a frozen 1260 s cap (6.5%)
STOP_FIRED = NO ; BINDING = NO ; PRODUCTION RUN = NO ; CHECKPOINT = NO
```

The Gate-2C implementation defect is repaired and the measurement Gate-2C could
not finish is now complete. **Gate-2C remains `INCOMPLETE_EXTERNAL`; its failed
run is preserved unchanged**, and a test asserts so.

---

## 1. The one architectural change, and its effect

| | Gate-2C (aborted) | Gate-2C-bis |
|---|---|---|
| `h_1` fed to `_kernel_polynomials` | exact series, bidegree **(121,121)**, 243 terms | `hhat_1`, bidegree **(12,12)**, **25 terms** |
| `d_e h_1` | exact, bidegree (120,120), 241 terms | `dhhat_1`, bidegree (12,12), 25 terms |
| complexity score | **32,669,982** | **222,573** |
| source construction cost | dominated the run | `0.0284 CPU-s` = `0.16%` of the `m=1` baseline |
| outcome | cap fired at 723 s | complete in 81.7 s |

`hhat_1` and `dhhat_1` carry only 25 terms because `h_1` is **separable**:
`h_1(p,m) = 1 - Phi(c-p+e) + Phi(m-c+e)`, so four 1-D degree-12 candidates
suffice. Estimand, assembly, drift, `m` set, resolvent and precision unchanged.

## 2. Representation-complexity guard

```text
static precheck (0.024 CPU-s, before any certification)
  m=2 increment : 9 kernel calls, score 222,573        budget 400,000   PASS
  m=1 baseline  : 3 kernel calls, score  74,022
  max bidegree  : 12                                    limit 12        PASS
runtime observed: max bidegree 12, score 222,573 -- IDENTICAL to the precheck
```

**The guard, evaluated on the Gate-2C defective path, scores `32,669,982` —
`81.7x` over budget.** It would have rejected that path in `0.024` CPU-s,
before spending any of the 723 CPU-s the defect actually consumed. The guard
that was missing is now the cheapest test in the gate.

Per-call table (all nine `m=2` calls):

| tag | bidegree | terms | z-degree after | score |
|---|---|---|---|---|
| `K_z,b hhat` / `K_z,b dhhat` / `K_z,db hhat` | (12,12) | 25 | 146 | 24,843 each |
| `K_0,b hhat` / `K_0,b dhhat` / `K_0,db hhat` | (12,12) | 25 | 145 | 24,674 each |
| `K_0,b F1hat` / `K_0,b dF1hat` / `K_0,db F1hat` | (12,12) | 169 | 145 | 24,674 each |

## 3. Candidate certification — rigorous, three named terms

Degree 12, exact-dyadic at `2^-50`, from degree-120 Chebyshev interpolation
in Arb.

| function | `eps` total | Chebyshev tail | degree-120 interp. error | dyadic rounding |
|---|---|---|---|---|
| `A = Phi(c-p+e)` | `8.9218e-07` | `8.9218e-07` | `1.47e-90` | `1.40e-14` |
| `B = Phi(m-c+e)` | `1.2615e-06` | `1.2615e-06` | `1.47e-90` | `1.38e-14` |
| `P = phi(c-p+e)` | `2.5108e-06` | `2.5108e-06` | `1.62e-89` | `1.48e-14` |
| `Q = phi(m-c+e)` | `3.9754e-06` | `3.9754e-06` | `1.62e-89` | `1.38e-14` |

```text
eps_h  = 2.153711e-06     eps_dh = 6.486285e-06
propagated kernel error   cand_allow   = E|raw| eps_h            = 1.7184e-06
                          cand_allow_d = 2 eps_h + E|raw| eps_dh = 9.4827e-06
propagated resolvent error  C * cand_allow (C = 207.754)         = 3.5701e-04
contribution to the R_2 half-width                                = 1.7850e-04
candidate_residual_share = 1.7850e-04 / 2.4947e-02 = 0.00716      limit 0.50  PASS
```

The error is **entirely** the Chebyshev tail; interpolation error and dyadic
rounding are 84 and 8 orders below it. Degree 12 is adequate with a `70x` margin
against the frozen domination rule, and it was **not** raised after results. The
pre-T0 float calibration predicted `8.9e-7 / 1.3e-6 / 2.5e-6 / 4.0e-6` — the
rigorous values match to three significant figures.

Predeclared exact-candidate inclusion check: at all five fixed states the exact
closed-form `h_1` lies inside `hhat_1 +/- eps_h`. **All included.** (The exact
value was taken in closed form rather than from a degree-121 series — the same
number, evaluated more exactly, and it keeps every high-degree object out of the
kernel path, which a test asserts.)

## 4. The measurement

```text
R_{CUSUM,2}(1/4) in [ -1.28223797 , -1.23234488 ]   half-width 2.4947e-02
  = (1/2)[ F_0(x0) + F_1(x0) + S_0^raw(x0) ]
  F_0(x0) = -1.58 +/- 6.10e-3      C*delta_F0 = 2.678e-03
  F_1(x0) = -0.94 +/- 8.53e-2      C*delta_F1 = 4.722e-02   <- the loose term
  S_0^raw(x0) = -3.8645e-07  (exact scalar; P(tau=1) ~ 8e-8 at this drift)
```

`F_1`'s residual is `17.6x` wider than `F_0`'s, because its source `S_1^raw` is
itself an enclosure produced by two kernel applications rather than a closed
form. That, not the candidate error, dominates the half-width, and it is the
obvious target if a production run ever needs a tighter `m>1` enclosure.

## 5. Independent correspondence — PASS

Monte Carlo of the frozen detector recursion (no operator, no candidate, no line
of assembly code), `N = 1,000,000`, seed `20260904`:

```text
MC mean  -1.25602298      SE 6.3758e-04      4-SE CI [-1.25857, -1.25347]
certified enclosure       [-1.28224, -1.23234]        intersects CI   PASS
centre gap 1.2684e-03  <=  tolerance max(4 SE, 5e-3) = 5.0e-3          PASS
```

The gap is `2.0` MC standard errors. Third-party corroboration: P5's own
independently measured map (different campaign, code and seeds) gives
`sup|R_{CUSUM,2}| = 1.2525` at `e = 0.20`; a value near `-1.256` at `e = 0.25`
is exactly what that map implies.

`m=1` consistency: this gate's point enclosure `[-1.57926, -1.57390]` lies inside
Gate-1's cell hull `[-1.58164, -1.57073]`, as containment requires.

## 6. Sharing audit

```text
resolvent solves, m=1                : F_0, d_e F_0                        = 2
resolvent solves added by m=2        : F_1, d_e F_1                        = 2
candidate/source objects added by m=2: hhat_1, dhhat_1, S_1^raw, d_e S_1^raw
shared resolvent fraction            : 0.50
duplicate m=1 solve created          : NO      new solve architecture: NO
```

## 7. Cost

```text
T_m1   = 17.531 CPU-s   (repeats 16.873, 18.189; spread 7.5%)
T_incr = 22.049 CPU-s   (repeats 21.918, 22.180; spread 1.2%)
  of which candidate construction 0.0284 CPU-s  -> ratio_source_only = 0.0016
T_cold_m2 = 39.580      T_assembly = 1e-6 CPU-s (the finite assembly is free)

ratio_incremental = 22.049 / 17.531 = 1.2577      -> MODERATE
ratio_cold        = 2.2577                        (not the production multiplier)
ratio_per_unit    = 1.2577 / 2 = 0.6289           <- enters the production model
```

`ratio_per_unit` is below 1 because Gate-1's function count charges `hhat_1` and
`S_1^raw` a full unit each while they are a Chebyshev fit and two kernel
applications, not resolvent solves. **The `24.5x` multiplier is therefore
conservative, not optimistic** — the opposite of the direction Gate-2B hedged.

A measurement note: the in-process `m=1` call costs `17.53` CPU-s against
Gate-1's `30.85` CPU-s per sub-cell, which was measured inside a 5-worker pool
and carries per-worker startup. Gate-1's larger figure is **retained** in the
CUSUM unit, since production also runs in a pool.

## 8. Updated P5Y cost model — arbitrary multipliers removed

| band | named assumptions | CPU-h | 16 cores | 64 cores | 128 cores |
|---|---|---|---|---|---|
| optimistic | measured `ratio_per_unit = 0.6289` applied to all `m`; SR cover at the walk's lower bound (309) | **1,868** | 123 h | 32 h | 18 h |
| central | `ratio_per_unit = 1.0` **retained** — the `m=2` datum shows 1.0 is conservative, but one measurement is not extrapolated to `m in {3,5}`, whose solve/source mix differs; cover 322, degree 8 @ 256 bits | **3,092** | 203 h | 54 h | 30 h |
| conservative | + the production SR candidate needing 384 bits (Gate-2A measured `t_panel x1.202`) | **3,697** | 243 h | 64 h | 36 h |
| worst plausible | + SR cover `x1.25` (the walk used a monotone step envelope; production may need finer cells near `e = 0`) | **4,597** | 302 h | 80 h | 45 h |

Against Gate-2B's `3,092 / 3,092 / 4,638 / 6,184`. Gate-2B's degenerate
`optimistic == central` is repaired, the arbitrary `1.5x` / `2.0x` hedges are
gone, and every band now names its source. Feasibility remains **STRONG**.

## 9. Checkpoint readiness — NO, with one named blocker

Seven of the eight frozen conditions hold: Gates 1/2A/2B intact, correspondence
PASS, representation guard PASS, `m`-sharing PASS, `ratio_incremental = 1.258 <= 2.0`.

The eighth does not: **the first-moment production cost model still has one
unmeasured load-bearing input.** Gate-2A's precision selection and Gate-2B's
cover and panel counts were both measured with `unit_candidate`, a
*representative* pseudo-candidate, not a production exact-dyadic candidate.
Gate-2A recorded the conditioning amplification (52 digits lost at degree 8) as
candidate-dependent, and that amplification is what selects the working
precision. Until it is measured on a real candidate, the 256-vs-384-bit choice —
the whole gap between the central and conservative bands — rests on a stand-in.

```text
P5Y_FIRST_BINDING_CHECKPOINT_READY = NO
```

## 10. Scientific boundary

This gate closes a **cost/assembly** uncertainty. It does not close `K2` `s_min`,
`K3` `M_2`, `K4` `H2` or `K5` `H3a`, which remain unresolved. P5, P5X and Gates
1/2A/2B/2C are untouched.
