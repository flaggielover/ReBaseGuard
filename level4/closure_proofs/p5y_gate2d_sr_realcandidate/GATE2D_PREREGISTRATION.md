# P5Y GATE 2D — PILOT-SR-REALCANDIDATE preregistration

**NON-BINDING.** A real-candidate conditioning / precision-validation pilot. Not
a production cover, not an SR campaign, not a binding checkpoint. Frozen before
any result-bearing execution (T2).

```text
P5_ORIGINAL_VERDICT = PARTIAL   P5X_FINAL_VERDICT = PARTIAL
P5X_CAMPAIGN = ARCHIVALLY_COMPLETE
P5Y_GATE1_DECISION     = GATE1_PASS_ROUTE_B_SUPPORTED    (immutable)
P5Y_GATE2A_DECISION    = SR_PRECISION_PASS_256           (immutable)
P5Y_GATE2B_DECISION    = SR_COVER_PASS_MEASURED          (immutable)
P5Y_GATE2C_DECISION    = M2_ASSEMBLY_INCOMPLETE_EXTERNAL (immutable)
P5Y_GATE2CBIS_DECISION = M2_ASSEMBLY_B_PASS              (immutable)
```

## 0. The single question

Does **one genuine production exact-dyadic SR backward-function candidate**
preserve the Gate-2A conditioning conclusion and minimum safe working precision
on the already-frozen representative patch?

## 1. Compute cap

```text
GATE2D_CPU_CAP       = 540 CPU-seconds = 0.15 CPU-hours    (hard)
GATE2D_CPU_PREFERRED <= 360 CPU-seconds = 0.10 CPU-hours
```
External CPU watchdog kept; no extension after T2. Pre-T0 calibration measured
one rigorous `acb.integral` at `0.0244` CPU-s, so the 289-node non-separable
probe costs `~7` CPU-s; the precision grid inherits Gate-2A's `~8` ms per
composition. Expected total `~60` CPU-s, leaving a `9x` margin.

## 2. Frozen patch and backend — unchanged from Gate-1 / 2A / 2B

```text
patch (17,11) on grid = 64      e = 1/4 exact       b_SR = log(1+A)
softplus Taylor degree = 8      candidate bidegree = (16,16)
continuous minimal-safe panel rule, same representative patch geometry
```
Degree 10 is **not** used: Gate-2A selected degree 8 as the safe baseline and
this gate isolates *candidate dependence*, not degree selection. No other patch,
no second patch after results.

## 3. The genuine candidate — which scientific function, and why

```text
DECISIVE CANDIDATE:  hhat_1^SR  approximating
    h_1(a,b) = 1 - Phi(c_SR - a + e) + Phi(b - c_SR + e)
```
`h_1 = 1 - K_e 1` is the **first backward function of `P5X-T1`**, a real
production certified function that Gate-1's MSHARE count already charges for,
and it is exactly the object composed with `q_SR` in the kernel path. It is
closed form, so it can be evaluated to arbitrary precision and — decisively —
its whole-domain residual can be certified rigorously within this cap.

It is **not** `unit_candidate`, not synthetic, not a toy, and not selected for
low condition number: it is the function the architecture dictates.

**Declared limitation, before T2.** `h_1` is *separable* (`1 - A(a) + B(b)`),
whereas the resolvent solutions `F_r` and the higher backward functions
`h_j (j>=2)` are not. A rigorous whole-domain enclosure for a non-separable
bidegree-(16,16) object needs a 2-D tail argument that is outside this cap. So
the decisive measurement is on a genuine but separable production object, and
that limitation is stated here rather than discovered later.

```text
NON-DECISIVE CONDITIONING PROBE:  hhat_2^SR  approximating
    h_2 = K_e h_1 ,   h_2(y) = int_{l(y)}^{u(y)} h_1(q_SR(y,z)) phi(z+e) dz
```
`h_2` is the second backward function of `P5X-T1`, genuinely **non-separable**
(the innovation and the integration limits couple both charts). Its 17x17 node
values are obtained by **rigorous `acb.integral` enclosures**, one per node, and
its coefficients are exact-dyadic. **No whole-domain residual certificate is
claimed for it**, so it cannot certify anything; conditioning (digit loss in the
composed contraction) is a property of the coefficient array alone, and that is
the only thing reported from it. It is explicitly NON-DECISIVE and exists to
test whether the separability of `h_1` flatters the decisive result.

## 4. Frozen candidate construction

Fit domain is the **full state square `[0, b_SR]^2`**, not just the patch —
strictly stronger, because `q_SR` may land anywhere in the square.

```text
1. per chart, evaluate at 61 Chebyshev-Lobatto nodes on [0, b_SR] in Arb
2. degree-60 Chebyshev coefficients by direct DCT-I summation in Arb
3. keep coefficients 0..16 ; round each to an exact dyadic multiple of 2^-50
4. convert to the monomial basis by the Chebyshev recurrence and t = (2a-b_SR)/b_SR
hhat_1 = 1 - Ahat(a) + Bhat(b)      bidegree (16,16), 33 nonzero coefficients
```
For the non-decisive `hhat_2`: tensor Chebyshev interpolation at the 17x17
Chebyshev-Lobatto nodes of the square, node values from `acb.integral`,
coefficients rounded to the same exact dyadic grid, converted to monomials —
289 nonzero coefficients, genuinely dense.

## 5. Frozen residual certification (decisive candidate only)

```text
eps_cand = sum_{k=17}^{60} |a_k|                   Chebyshev truncation
         + 2 (b_SR/4)^{61} sup|f^{(61)}| / 61!     degree-60 interpolation error
         + 17 * 2^-50                              exact-dyadic rounding
with sup|f^{(61)}| <= 0.4333 sqrt(60!)   (Cramer; the constant already used by
ra_certifier.taylor_remainder).   eps_cand = eps_A + eps_B, valid on the WHOLE square.
```
Not a pointwise fitting error. Reported split into its three named terms.

## 6. Frozen acceptance precondition (before entering the precision grid)

```text
- eps_cand finite and rigorously certified                    else FAIL_REPRESENTATION
- eps_cand small enough that P2 <= 1e-8 remains reachable:
      eps_cand * N_0 / |acc|  <=  1e-8                        else FAIL_REPRESENTATION
- no malformed coefficient, no interval explosion
- representation-complexity guard passes
```
Degree 16 is mandated and **may not be raised after T2**.

## 7. Standing representation-complexity guard (Gate-2C-bis rule, carried forward)

Every object entering the composed-contraction path is statically inspected
before T2: bidegree, term count, expected composed z-degree, invocation count.

```text
COMPLEXITY_SCORE = sum over compositions of (deg_a+1)(deg_b+1)(composed_z_deg+1)
composed_z_deg = candidate_degree * softplus_degree = 16 * 8 = 128
per composition  = 17 * 17 * 129 = 37,281
MAX_COMPLEXITY_SCORE = 100,000        (frozen)
```
Basis: the Gate-2A-validated path performs one such composition per precision
cell, scoring `37,281`; `100,000` leaves `2.7x` headroom and rejects any
high-degree object (a degree-121 argument would score `>1.9e6`). It is also
asserted that **no exact-series object of degree > 16 enters the path**.

## 8. Frozen precision grid and P1 repair

```text
precisions = {256, 384, 512}     no 640/768/1024, no adaptive point
192 bits is NOT re-run; Gate-2A's value is cited for comparison only
P1 repaired target:  E_d <= (1 - eps_P1) * 1e-9 ,  eps_P1 = 1e-3   (Gate-2B: free)
MUST assert n_z unchanged at 28 relative to Gate-2B/Gate-1              else FAIL
```

## 9. Frozen decisive target and reported diagnostics

```text
P2 <= 1e-8      (identical to Gate-2A; not weakened)
report per precision: P2, precision-independent floor, interval radius,
                      digits_lost, fraction of precision consumed, margin
digits_lost = digits_available - (-log10(radius / |acc|))     [Gate-2A definition]
```
Failure in any cell is classified from **interval radii, floors and certified
residuals only** — never from midpoint disagreement — as exactly one of
`NONE / PRECISION_INSUFFICIENT / CANDIDATE_RESIDUAL_DOMINANT /
REPRESENTATION_ILL_CONDITIONED / MATHEMATICALLY_FALSE / IMPLEMENTATION_DEFECT /
UNKNOWN`.

## 10. Frozen conditioning classification, against Gate-2A's `51.8` digits

```text
delta_digits = real_candidate_digits_lost - 51.8
STABLE <= +5 ; MILDLY_WORSE <= +15 ; MATERIALLY_WORSE <= +30 ; SEVERE > +30
```
Gate-2A's `unit_candidate` is additionally re-measured here under identical
conditions as a control, so the comparison is like-for-like rather than
cross-gate.

## 11. Frozen selection rule

Lowest precision in `{256, 384, 512}` with: `P2 <= 1e-8`; every inherited gate
passing with nonzero margin; no interval explosion; radius monotone in
precision; candidate-residual contribution acceptable; guard PASS.

```text
256 -> SR_REALCANDIDATE_PASS_256 ; else 384 ; else 512 ;
none -> SR_REALCANDIDATE_FAIL_WITHIN_GRID
candidate uncertifiable / degree 16 insufficient / guard fail / hidden
high-degree object -> SR_REALCANDIDATE_FAIL_REPRESENTATION
```
No interpolation to an untested precision.

## 12. Reproducibility and timing

```text
duplicate run frozen at 384 bits: enclosure endpoints and P2 must be IDENTICAL
TIMING_REPEATS = 5 per precision cell    (frozen, not reducible after seeing timings)
```
Timing affects the cost model only, never a mathematical PASS/FAIL.

## 13. Pre-registered predictions (falsifiable)

| quantity | prediction |
|---|---|
| `eps_cand` | `~1.9e-07` (float calibration: chart tails `6.9e-8` and `1.24e-7`) |
| `sup_g` of the genuine candidate | `~3.0`, against `unit_candidate`'s `11.65` |
| `P2` floor | `~4x` **lower** than Gate-2A's `7.54e-10`, i.e. `~2e-10` |
| `digits_lost` | `51.8 +/- 5` -> `STABLE` |
| safe precision | `256` |
| decision | `SR_REALCANDIDATE_PASS_256` |

## 14. STOP rules

```text
S1 worker CPU reaches 540 s -> kill, no completed artifact, STOP_FIRED = YES
S2 candidate cannot be certified / degree 16 insufficient -> FAIL_REPRESENTATION
S3 complexity guard fails or a hidden high-degree object appears -> FAIL_REPRESENTATION,
   and T2 is not entered
S4 no precision in the grid satisfies the frozen gates -> FAIL_WITHIN_GRID
S5 any path outside this namespace modified -> STOP the whole gate
S6 a result-bearing semantic bug found after T2 -> STOP; no adaptive repair
```

## 15. Checkpoint readiness

`YES` only if the genuine candidate is constructed and certified, the guard
passes, the grid completes, safe precision `<= 512`, `P2` PASS, Gates
1/2A/2B/2C-bis intact, **and no remaining unmeasured load-bearing input exists**
in the first-moment production architecture / cost model. The separability
limitation of section 3 is explicitly in scope for that judgement and will be
adjudicated on the evidence, including the non-decisive `hhat_2` probe.

## 16. Out of scope — not run

Another patch, full SR cover, `m>1` production, second moments, `s_min`, `M_2`,
`H2`/`H3a`, Lean, binding checkpoint, production campaign.

## 17. Repository safety

Branch `p5y-gate1-micropilots`, namespace
`level4/closure_proofs/p5y_gate2d_sr_realcandidate/`. No merge to main, no push,
no binding checkpoint, no modification of P5, P5X or Gates 1/2A/2B/2C/2C-bis.
