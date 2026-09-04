# P5Y GATE 2B — PILOT-SR-COVER preregistration

**NON-BINDING.** A cover-geometry / cost-model pilot. Not SR production, not a
certified cover, not a binding checkpoint. Frozen before any result-bearing
execution (T2); nothing here changes after T2.

```text
P5_ORIGINAL_VERDICT = PARTIAL     P5X_FINAL_VERDICT = PARTIAL
P5X_CAMPAIGN = ARCHIVALLY_COMPLETE
P5Y_GATE1_DECISION  = GATE1_PASS_ROUTE_B_SUPPORTED     (immutable)
P5Y_GATE2A_DECISION = SR_PRECISION_PASS_256            (immutable)
```

## 0. The single question

Under the current P5Y SR architecture (**degree 8**, continuous panel rule,
256-bit safe precision), what are the **actual** production sub-cell count and
live patch count over the compact domain after the proved `P5X-T3` far-field
compression? These replace the inherited `835` and `1210`.

**Degree 8 geometry is used throughout. Degree 10 may not be used to shrink
anything.**

## 1. Compute cap

```text
GATE2B_CPU_CAP       <= 0.10 CPU-hours   (hard, no extension after results)
GATE2B_CPU_PREFERRED <= 0.05 CPU-hours
```
Geometry, resolvent minorant evaluations, deterministic counting and scalar
interval arithmetic only. **No certified function solve is invoked.** If any
step turns out to need one: STOP and record `REQUIRES_FUTURE_GATE`.

Calibration performed **before** this preregistration, on the historical R1
CUSUM minorant (not an SR result): `0.397 s` per evaluation at `cells = 200`.
The frozen 200-point drift grid therefore costs `~0.02-0.04` CPU-hours.

## 2. Frozen scientific domain

```text
detector          SR, m = 1 geometry (m-independent, see section 8)
e_star_SR         c_SR = log A + 1/2 = 6.75553146432147308692733728672
                  (the CERTIFIED_E_STAR of P5X-T3 / r1_cover_compression.json)
compact domain    e in [0, e_star_SR]        -- NOT extended to 12
negative e        covered by the exact oddness P5-T3; NOT counted separately
A                 4581762885148045 / 8796093022208
b_SR              log(1+A)   (erratum D1)
```

## 3. Frozen `C_SR(e)` — drift-explicit monotone Bellman minorant

R1 made the **CUSUM** minorant drift-explicit and recorded that the SR
extension "is not implemented and not claimed here". This gate implements it on
the **authoritative SR chart itself** (not a CUSUM surrogate), by the same
method:

```text
one-sided aligned (minus) chart:  y' = softplus(y + inc),  inc ~ N(e - 1/2, 1)
alarm iff the PRE-UPDATE quantity  y + inc >= log A        (EXACT_SR_TARGET.md)
state grid: [0, b_SR] in `cells` equal cells, LEFT endpoints  (M1 monotonicity)
cell j receives  y' in [x_j, x_{j+1})  <=>  y + inc in [u_j, u_{j+1}),
       u_j = softplus^{-1}(x_j) = log(exp(x_j) - 1),  u_0 = -infinity,  u_N = log A
alarm mass from x_i:  1 - Phi(log A - m_i),   m_i = x_i + e - 1/2
H_0 = 0 ;  H_t = alarm + transition * H_{t-1}
C_SR(e) = min_{t <= n_max}  t / H_t(0)      evaluated at the SMALLEST |e| of the
                                            region (M2 drift monotonicity)
cells = 200 ,  n_max = 250 ,  bits = 192    (matching the certified SR reference)
```

Mass balance is asserted per row. `M1` (H_t nondecreasing in the state) and `M2`
(H_t(0;e) nondecreasing in |e| for the aligned one-sided chart) are the same two
facts R1 proved; nothing here uses the unproved `sup_e E[tau|e] = E[tau|0]`.

**Mandatory pre-result cross-check (STOP if it fails).** At `e = 0` the
reconstruction must agree with the already-certified SR component
`sr_derivative/results/sr_monotone_contraction.json`:

```text
H_250(0) >= q_safe = 19/100          and        C_SR(0) <= 25000/19 = 1315.789473...
```

## 4. Frozen sub-cell rule — verified identical to the current architecture

```text
a = 2 phi(0)                       h(e) = 1 / (4 a C_SR(e))
```
This is byte-for-byte the rule in `certified_method_repair_ra/RA_FEASIBILITY_AUDIT.md`
section 5 and `compute_optimization_r1/r1_stop_gate.py` (`h_max = 1/(4*a*C)`);
a test asserts the constant `a` matches.

## 5. Frozen drift-evaluation strategy and cover walk

Not sparse sampling. A **full deterministic geometry walk**:

1. evaluate `C_SR` on a frozen 200-point grid, cubically bunched toward 0:
   `e_i = e_star * (i/199)^3`, `i = 0..199`;
2. build a **monotone step envelope**: on `[e_i, e_{i+1})` use `C_SR(e_i)`.
   Valid as an **upper** bound by `M2` (`C_SR` is non-increasing in `|e|`), so the
   resulting cell count is a certified **upper bound**. Using `C_SR(e_{i+1})`
   instead gives the matching **lower** bound; both are reported;
3. greedy walk, the production semantics exactly:
   ```text
   e = 0
   while e < e_star:  C = envelope(e); h = 1/(4 a C)
                      nxt = min(e + 2h, e_star); emit sub-cell [e, nxt]; e = nxt
   ```
   Each sub-cell has half-width `<= h(its own left endpoint)`, which by `M2` is
   valid across the whole sub-cell. The final sub-cell may be narrower, which is
   conservative. Exact endpoint coverage, no gaps, no overlaps — asserted by test.

**Outer cells** are pure bookkeeping (one resolvent evaluation costs `0.4 s`, so
the grouping has no cost consequence). Frozen definition: maximal runs of
consecutive sub-cells whose widths agree within a factor of 2.

## 6. Frozen patch geometry and the LIVE definition

```text
grid = 64 over [0, b_SR]^2          nominal patches = 4096
```

A patch is **LIVE** iff its closed box intersects `{x_0} union R`, where `R` is
the exact reachable set constraint derived here from the frozen recursion:

```text
xi = exp(y) ,   xi^+' = 1 + xi^+ e^{z-1/2} ,   xi^-' = 1 + xi^- e^{-z-1/2}
=>  (xi^+' - 1)(xi^-' - 1) = xi^+ xi^- e^{-1}        -- z CANCELS EXACTLY
```
Since `xi >= 1` always and `xi < 1 + A` pre-alarm, every state reachable at
`t >= 1` satisfies

```text
R := { (y+,y-) in [0,b_SR]^2 :  1/e <= (e^{y+} - 1)(e^{y-} - 1) <= (1+A)^2/e }
```
and `x_0 = (0,0)` is the reset state. The product is increasing in both
coordinates, so a box `[a1,a2] x [b1,b2]` meets `R` iff
`(e^{a2}-1)(e^{b2}-1) >= 1/e` and `(e^{a1}-1)(e^{b1}-1) <= (1+A)^2/e`.

This is an **exact algebraic exclusion**, never a numerical-smallness one. A
test asserts `{x_0} union R` is forward-invariant under `q_SR`, so no reachable
state is dropped. Patches are excluded only if provably unreachable.

## 7. Frozen panel count per patch

```text
h_z = 0.19386660811172551          (Gate-1 degree-8 continuous rule, frozen)
core_len(i,j) = 2 c_SR - y+_hi - y-_hi
n_z(i,j)      = ceil( core_len(i,j) / (2 h_z) )
panels(i,j)   = n_z(i,j) + 2       (core panels + the two boundary strips)
```
**Declared before T2:** Gate-1's `n_z = 28` is the value for the single patch
`(17,11)`; `n_z` is a *per-patch* quantity, and the production total is
`sum over live patches`, never `live_patches x 28`. This gate measures the sum.

## 8. Frozen sharing audit — three distinct multipliers

```text
GEOMETRIC cover      sub-cells x live patches x panels
                     SHARED across all m, both moments and value/derivative.
                     It is NOT multiplied by 24.5 and NOT multiplied by m.
FUNCTION count       49 certified functions = 24.5 units x 2 (value+derivative),
                     from Gate-1 PILOT-MSHARE (union over m, not sum over m)
PANEL/integration    already inside the geometric cover
CPU_SR = n_subcells x 49 x sum_livepatches(panels) x t_panel
```
`t_panel = 6.091 ms` (Gate-2A, degree 8 @ 256 bits, includes the moment
recursion). Patch-independent because the composed degree `16 d = 128` is.

## 9. `P1` headroom — designed, not applied

Gate-2A recorded the `P1` knife edge (margin `4.3e-16`, precision-independent).
Gate-2B **does not change the geometry**. The future repair is recorded and its
effect estimated analytically only: targeting `E_d <= (1-eps) 1e-9` scales
`H_max` by `(1-eps)^{1/(d+1)}`, so with the recommended `eps = 1e-3` the shift is
`h_z -> h_z - 2.7e-5` (relative `1.4e-4`) and `n_z` rises by at most 1 on the
patches sitting exactly on a ceiling boundary. Computed, reported, **not applied**.

## 10. Predeclared sensitivity (diagnostic only)

`+/- 5%` perturbation of the `C_SR` envelope, re-running the walk. It does not
change the frozen production rule and does not enter any decision.

## 11. Acceptance and decision (mechanical)

```text
geometry sound := e=0 cross-check passes AND the walk tiles [0,e_star] exactly
                  AND the live set is forward-invariant AND no production solve ran
STRONG   central <=  5,000 CPU-h        MODERATE central <= 10,000
WEAK     central <= 30,000              NOT_FEASIBLE central > 30,000

geometry sound AND feasibility in {STRONG, MODERATE} -> SR_COVER_PASS_MEASURED
geometry sound AND feasibility in {WEAK, NOT_FEASIBLE} -> SR_COVER_PASS_BUT_COST_HIGH
geometry NOT sound                                     -> SR_COVER_FAIL_GEOMETRY
external interruption / cap                            -> SR_COVER_INCOMPLETE_EXTERNAL
```

## 12. STOP rules

```text
S1 cumulative CPU reaches 0.10 CPU-hours            -> INCOMPLETE_EXTERNAL
S2 e=0 cross-check against the certified SR component fails -> FAIL_GEOMETRY
S3 generated cells fail exact coverage               -> FAIL_GEOMETRY
S4 the live set is not forward-invariant             -> FAIL_GEOMETRY
S5 counting would require a production solve         -> REQUIRES_FUTURE_GATE, STOP
S6 any path outside this namespace is modified       -> STOP the whole gate
S7 a result-bearing semantic bug found after T2      -> STOP that measurement;
   do not patch and continue unless provably reporting-only
```

## 13. Out of scope — not run

`C1` full cover, `C2` second moments, `s_min`, `M_2`, `m>1` solves, `H2`/`H3a`,
Lean, production Arb, degree 10 geometry, the xi back-end.

## 14. Repository safety

Branch `p5y-gate1-micropilots` (continued), namespace
`level4/closure_proofs/p5y_gate2b_sr_cover/`. No merge to main, no push, no
binding checkpoint, no modification of P5, P5X, Gate-1 or Gate-2A artifacts.
