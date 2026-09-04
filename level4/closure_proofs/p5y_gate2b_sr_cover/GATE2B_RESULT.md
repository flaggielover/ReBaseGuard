# P5Y GATE 2B — PILOT-SR-COVER result

```text
P5Y_GATE2B_DECISION = SR_COVER_PASS_MEASURED
SR sub-cells over [0, e_star_SR]  = 322   (lower bound 309)   vs inherited 835
SR live patches                   = 3994 / 4096              vs inherited 1210
SR panels over live patches       = 83,452                   vs inherited 1210 x 28 = 33,880
COVER FEASIBILITY = STRONG        central P5Y CPU = 3,092 h
CPU USED = 0.0201 CPU-hours against a 0.10 cap (20% of cap, 40% of preference)
STOP_FIRED = NO ; BINDING = NO ; PRODUCTION RUN = NO ; NO SOLVE INVOKED
```

---

## 1. `C_SR(e)` reconstructed — and validated to 17 significant figures

R1 made the **CUSUM** minorant drift-explicit and recorded that the SR extension
"is not implemented and not claimed here". This gate implements it on the
**authoritative softplus chart** rather than on a CUSUM surrogate: state grid on
`[0, b_SR]` with left endpoints (`M1`), alarm on the pre-update quantity at
`log A`, continuation cells addressed through `softplus^{-1}`, `cells = 200`,
`n_max = 250`, `192` bits — the parameters of the certified SR component.

**Mandatory pre-declared cross-check, passed:**

| quantity | this reconstruction | certified `sr_monotone_contraction.json` |
|---|---|---|
| `H_250(0)` | `0.20271993143543465` | `0.20271993143543464049780…` |
| `C_SR(0)` | `1205.937` (`t* = 139`) | `25000/19 = 1315.789` |

The hit probability agrees to **17 significant figures** with a certificate
produced by different code in a different campaign. `C_SR(0)` is tighter because
the reconstruction minimises `t / H_t` over `t` rather than fixing `t = 250` with
a floored `q`. Row mass balance holds in every row.

**A correction to an inherited assumption.** R1 estimated
`C_SR / C_CUSUM = 3.86x` at `e = 0` from softplus domination by a CUSUM chart
with barrier `log A`. Measured directly: `C_SR(0) = 1205.9` against R1's
`C_CUSUM(0) = 1232.8`, a ratio of **0.978** — the SR chart is marginally
*easier*, not 3.9x harder. The domination bound was simply loose.

## 2. Representative `C_SR(e)` and `h(e) = 1/(4 a C_SR(e))`

| `e` | `C_SR(e)` | `t*` | `h(e)` | sub-cells per unit `e` |
|---|---|---|---|---|
| 0 | 1205.937 | 139 | `2.598e-04` | 1924.4 |
| 1/4 | 187.747 | 55 | `1.669e-03` | 299.6 |
| 1/2 | 57.751 | 29 | `5.425e-03` | 92.2 |
| 1 | 17.586 | 13 | `1.782e-02` | 28.1 |
| 2 | 6.428 | 5 | `4.875e-02` | 10.3 |
| `e_star` | 2.000 | 1 | `1.567e-01` | 3.2 |

Explanatory only; the counts below come from the full walk.

## 3. The measured cover

Full deterministic greedy walk over `[0, e_star_SR]`, `e_star_SR = c_SR =
6.755531464321473…`, under a monotone step envelope (upper bound by `M2`).

```text
sub-cells      322   (upper bound)     309   (lower bound)   -- brackets the truth
outer cells      9   (bookkeeping only; 11 to 117 sub-cells each)
widths        min 5.196e-04   median 1.551e-03   max 3.133e-01
densest       [0, 5.196e-04] -- the origin itself
distribution  79.5% of sub-cells in [0, 0.5] ; 13.4% in (0.5, 2] ; 7.1% in (2, e_star]
tiling        exact: starts at 0, ends at e_star, every boundary shared
```

Predeclared `+/-5%` envelope sensitivity: `338 / 306` against a baseline of `322`
— exactly linear, as `h ~ 1/C` requires. Diagnostic only.

**Against the inherited `835`: ratio `0.386`, classification `LOWER` (2.59x
fewer).** Two inherited assumptions caused the gap: (i) the `2.5x` SR-vs-CUSUM
cover inflation, which §1 shows should be `~1.0x`; and (ii) the `[0,12]` domain,
which the proved `P5X-T3` compression replaces by `[0, 6.7555]`.

## 4. The measured patch geometry — and an exact new invariant

The SR two-chart recursion has an **exact invariant** in the multiplicative
variable, derived here from the frozen recursion:

```text
xi^+' - 1 = xi^+ e^{z-1/2} ,  xi^-' - 1 = xi^- e^{-z-1/2}
=>  (xi^+' - 1)(xi^-' - 1) = xi^+ xi^- / e         -- the innovation z CANCELS
```

With `xi >= 1` always and `xi < 1+A` pre-alarm, every state reachable at `t >= 1`
lies in `R = { 1/e <= (e^{y+}-1)(e^{y-}-1) <= (1+A)^2/e }`. This is an
*algebraic* exclusion, never a numerical-smallness one, and `{x_0} u R` is
mechanically verified forward-invariant (image product ranges over
`[0.36787944…, 82401.06]` inside the constraint `[0.36787944…, 100197.53]`).

```text
nominal patches                      4096   (grid 64 x 64 on [0, b_SR]^2)
live                                 3994   (97.5%)
excluded, product below 1/e            57   (states too near the origin corner)
excluded, product above (1+A)^2/e      45   (unreachable far corner)
patch (0,0) kept                      yes   -- it holds the reset state x_0
geometry depends on e                  NO   -- l, u, q_SR and the invariant are e-free
```

Unlike CUSUM, whose reachable mass collapses onto the axes, softplus keeps both
SR charts strictly positive, so SR's exclusion is the *opposite* corner and is
small: **97.5% of patches are live**. The inherited `1210` is therefore **3.3x
too low** — it was the incumbent `Gamma_SR` certificate's symmetry-reduced live
cell count, not this architecture's.

## 5. `n_z` is per patch, not a global 28

```text
core_len(i,j) = 2 c_SR - y+_hi - y-_hi        n_z(i,j) = ceil(core_len / (2 h_z))
n_z: min 5, max 35, mean 18.89               at Gate-1's patch (17,11): 28  (reproduced)
panels(i,j) = n_z + 2   (core + two boundary strips)
sum over live patches   = 83,452
naive 3994 x 28         = 111,832            -> per-patch counting saves 1.34x
```

Gate-1's `n_z = 28` was the value at one patch and is **not** a global constant.

## 6. Sharing audit — three distinct multipliers, none double-counted

```text
GEOMETRIC cover   322 sub-cells x 83,452 panels    SHARED across all m, both
                  moments and value/derivative. NOT multiplied by m, NOT by 24.5.
FUNCTION count    49 = 24.5 units x 2 (value + derivative), Gate-1 PILOT-MSHARE
PANEL/integration already inside the geometric cover

CPU_SR = 322 x 49 x 83,452 x 6.091 ms = 2,227.8 CPU-hours
```

**The two inherited errors nearly cancelled.**

```text
inherited ops per certified function  835 x 1210 x 28 = 28,289,800
measured  ops per certified function  322 x 83,452    = 26,871,544
ratio 0.9499 -- only 5% lower, from a 2.59x over-count of sub-cells meeting a
2.46x under-count of patch-panels.
```

That the inherited total was accidentally close to right is not a reason to have
trusted it: both inputs were wrong by a factor of ~2.5 in opposite directions.

## 7. `P1` headroom repair — estimated, not applied

Geometry was **not** changed. Targeting `E_d <= (1 - 1e-3) 1e-9` scales `H_max`
by `(1-eps)^{1/9}`, moving `h_z` from `0.19386660811` to `0.19383962357`
(relative `1.39e-4`). Recomputing `n_z` over every live patch gives **83,452
panels — identical**: the change is absorbed by the ceiling on every patch.
**The `P1` headroom repair is free.**

## 8. Updated cost

| band | assumption | CPU-h | 16 cores | 64 cores | 128 cores |
|---|---|---|---|---|---|
| optimistic | *(see defect note)* | 3,092 | 203 h | 54 h | 30 h |
| **central** | measured geometry, degree 8 @ 256 bits | **3,092** | 203 h | 54 h | 30 h |
| conservative | `m>1` per-function cost 1.5x | 4,638 | 305 h | 81 h | 45 h |
| worst plausible | `P1` repair applied and `m>1` 2x | 6,184 | 407 h | 107 h | 60 h |

`CPU_SR = 2,227.8` h, CUSUM `70.1` h, `+17%` `H2`/`H3a` rung, `+15%` overhead.

**Defect recorded, not patched.** The `optimistic` band was frozen with no
assumption distinguishing it from `central`, so the two are numerically equal.
This is a preregistration weakness in the band construction, not a measurement
error; it changes no decision (`central` drives the classification). Patching it
after T2 would be a post-result amendment, so it is reported instead.

Feasibility: `central 3,092 <= 5,000` → **STRONG**.

## 9. What this gate did NOT establish

No cover was certified, no function was solved, no second moment, no `s_min`,
`M_2`, `m>1`, `H2`/`H3a`, no Lean, no degree-10 geometry. The `835` and `1210`
are replaced by measurements; the SR *cover-cost* model is now measured
end-to-end except for the `m>1` per-function cost, which remains assumed equal
to `m=1`. P5, P5X, Gate-1 and Gate-2A are untouched.
