# P5Y GATE 2C — PILOT-M2-ASSEMBLY preregistration

**NON-BINDING.** A single-assembly cost/correspondence pilot. Not a production
cover, not a second-moment campaign, not a binding checkpoint. Frozen before any
result-bearing execution (T2); nothing here changes after T2.

```text
P5_ORIGINAL_VERDICT = PARTIAL   P5X_FINAL_VERDICT = PARTIAL
P5X_CAMPAIGN = ARCHIVALLY_COMPLETE
P5Y_GATE1_DECISION  = GATE1_PASS_ROUTE_B_SUPPORTED   (immutable)
P5Y_GATE2A_DECISION = SR_PRECISION_PASS_256          (immutable)
P5Y_GATE2B_DECISION = SR_COVER_PASS_MEASURED         (immutable)
```

## 0. The single question

For the raw-variable P5Y CUSUM architecture, what is the **actual per-function
cost multiplier for `m > 1` relative to `m = 1`**, and does the assembled
`R_{CUSUM,2}(e)` correspond to an independent estimate of the same object?

Gate-1 MSHARE (function-count multiplier `24.5x`, shared backward-function set)
is **not** revisited. This gate measures assembly cost only.

## 1. Compute cap

```text
GATE2C_CPU_CAP       <= 0.20 CPU-hours   (hard, no extension after results)
GATE2C_CPU_PREFERRED <= 0.10 CPU-hours
```
No full `e`-cover, no other `m`, no second moments, no SR solve, no `H2`/`H3a`.

## 2. Frozen scientific object and drift

```text
detector   CUSUM (k = 1/2, h = 5), inclusive post-update test, Stage-D convention A
m          {1, 2} only
drift      e = 1/4  EXACT RATIONAL  -- one drift only, no second drift may be added
precision  256 bits, Taylor order N = 120, candidate degree 12, quadrature 400
           (the frozen Gate-1 raw-variable configuration, imported unmodified)
```
`e = 1/4` is the drift Gate-1 anchored raw-vs-z behaviour at; it is in the
load-bearing near region and avoids trivial far-field behaviour.

## 3. Frozen raw-variable assembly, derived from `P5X-T1(c)`

`P5X-T1(c)` in raw variables (Gate-1 §6, an exact corollary of `L1`; `Z -> raw`,
`g_r -> F_r`, `S_r -> S_r^raw`, and the external `+ e` deleted):

```text
R_{D,m}(e) = (1/m) sum_{r<m} [ F_r(x0) - sum_{t=r+1}^{m-1} (K_e^{t-r-1} S_r^raw)(x0) ]
             + sum_{t=1}^{m-1} (1/t) sum_{i=1}^{t} (K_e^{i-1} S_{t-i}^raw)(x0)
```

Specialising, with every sum written out:

```text
m = 1:  R_{CUSUM,1}(e) = F_0(x0)
m = 2:  R_{CUSUM,2}(e) = (1/2)[ F_0(x0) - S_0^raw(x0) + F_1(x0) ] + S_0^raw(x0)
                       = (1/2)[ F_0(x0) + F_1(x0) + S_0^raw(x0) ]
```

Objects, and exactly how `m = 2` differs from `m = 1`:

```text
S_0^raw = rho_1^raw = phi(u+e) - phi(l+e)          closed form, SHARED
h_1     = 1 - Phi(u+e) + Phi(l+e)                  CLOSED FORM -- no solve at all
d_e h_1 = -S_0^raw                                 exact
S_1^raw = K_{raw,e} h_1 = K_{z,e} h_1 + e K_e h_1  NEW: 2 kernel applications
F_0     = (I-K_e)^{-1} S_0^raw                     SHARED with m=1
F_1     = (I-K_e)^{-1} S_1^raw                     NEW: 1 resolvent solve
```
`m = 2` adds **one** resolvent solve (`F_1`) plus its `e`-derivative, and the
source machinery for `S_1^raw`. It adds **no** new solve architecture.

Probabilistic identity the formula must reproduce (recorded for the reader):
`R_2 = E[raw_tau; tau=1] + (1/2)E[raw_tau; tau>=2] + (1/2)E[raw_{tau-1}; tau>=2]`,
with `S_0^raw(x0) = E[raw_1; tau=1]`, `F_0(x0) = E[raw_tau]`,
`F_1(x0) = E[raw_{tau-1}; tau>=2]`.

Derivative source, exact, no boundary term because `l`, `u` are `e`-free:

```text
d_e S_1^raw = K_e h_1 + K_{raw,e}(d_e h_1) + [ K_{z,db} h_1 + e K_{db} h_1 ]
```

## 4. Frozen `m`-sharing assertion (checked mechanically BEFORE timing)

```text
unique solved functions for m=1                       : F_0, d_e F_0            = 2
additional unique solved functions needed for m=2      : F_1, d_e F_1            = 2
closed-form (no solve) objects newly needed for m=2    : h_1, S_1^raw, d_e S_1^raw
shared fraction at m=2                                 : 2/4 = 50%
```
A test asserts the `m=1` candidate/residual objects are reused by identity, not
recomputed, and that no duplicate solve is silently created.

## 5. Frozen timing protocol

```text
CERTIFIED_REPEATS = 2      (the certified path dominates; frozen, not reducible)
ASSEMBLY_REPEATS  = 5      (the finite assembly arithmetic is cheap)
```
Report median, min, max and relative spread. Setup is separated from steady
state. **Timing affects the cost model only, never a scientific PASS/FAIL.**

Measured quantities:

```text
T_m1        certified cost of (F_0, d_e F_0)                    -- the denominator
T_incr      certified cost of everything m=2 needs BEYOND m=1
            (h_1, S_1^raw, d_e S_1^raw, F_1, d_e F_1)
T_cold_m1 = T_m1        T_cold_m2 = T_m1 + T_incr
```

## 6. Frozen cost ratios and the production-relevant one

```text
ratio_incremental = T_incr / T_m1
ratio_cold        = T_cold_m2 / T_cold_m1  =  1 + ratio_incremental
units_added_by_m2 = 2      (Gate-1's frozen 4m-2 accounting: m=1 needs 2 functions
                            = 1 unit, m=2 needs 6 = 3 units, so +2 units)
ratio_per_unit    = ratio_incremental / units_added_by_m2      <-- PRODUCTION-RELEVANT
```
`ratio_per_unit` is exactly the quantity the Gate-2B cost model assumed to be
`1.0` and hedged at `1.5x` / `2.0x`. The cost classes are applied to it:

```text
STRONG <= 1.15 ;  MODERATE <= 1.50 ;  WEAK <= 2.00 ;  HIGH > 2.00
```
`ratio_cold` is reported but is **not** production-relevant, because `m`-sharing
is already established and production computes the shared objects once.

## 7. Frozen independent correspondence

Option **A**, the structurally strongest available: a direct Monte Carlo
simulation of the frozen CUSUM detector recursion. It touches no operator, no
candidate, no Fredholm machinery and no line of the assembly code — it simulates
`raw_t`, the two charts, `tau`, `w = min(2,tau)` and `Rbar` exactly as
`FROZEN_SCOPE.md` §1 defines them.

```text
N_CYCLES = 1_000_000     SEED = 20260904     e = 1/4     m = 2
statistic: Rbar = raw_tau if tau = 1 else (raw_tau + raw_{tau-1})/2
SE = sample sd / sqrt(N)   (expected ~9.5e-4)
```

## 8. Frozen correspondence tolerance (may not be widened after results)

```text
PASS iff  (i)  the certified enclosure of R_2 intersects
               [ mc_mean - 4 SE , mc_mean + 4 SE ] ,
     AND  (ii) | center_assembled - mc_mean |  <=  max( 4 SE , 5e-3 ) .
```

## 9. Predeclared algebraic cross-checks (non-decisive)

```text
CHK-A  h_1(x0) as a BiPoly equals 1 - Phi(c+e) + Phi(-c+e)      to < 1e-25
CHK-B  S_0^raw(x0) as a BiPoly equals phi(c+e) - phi(-c+e)      to < 1e-25
CHK-C  the MC estimate of E[raw_1; tau=1] agrees with S_0^raw(x0) within 4 SE
       -- an independent check of one assembly component in isolation
CHK-D  R_1 from this gate's F_0 reproduces Gate-1's certified m=1 enclosure at
       the same drift (overlap required)
```

## 10. STOP rules

```text
S1 cumulative CPU reaches 0.20 CPU-hours                -> INCOMPLETE_EXTERNAL
S2 m=2 needs a fundamentally different solve architecture -> FAIL_ARCHITECTURE
S3 the shared-function claim is false                    -> FAIL_ARCHITECTURE
S4 the raw assembly cannot reproduce the frozen m=2 definition -> FAIL_ARCHITECTURE
S5 correspondence fails the §8 tolerance                 -> FAIL_CORRESPONDENCE
S6 ratio_per_unit > 2.0 with correspondence passing      -> PASS_COST_HIGH
S7 any path outside this namespace is modified           -> STOP the whole gate
S8 a result-bearing semantic bug found after T2 -> STOP that measurement; do not
   patch and continue unless provably reporting-only
```

## 11. Frozen cost-model update rule

Replace the assumed `1.5x` / `2.0x` `m>1` factors by the measured
`ratio_per_unit`. Carry forward Gate-2B's measured SR geometry (322 sub-cells,
3994 live patches, 83,452 panels), degree 8 @ 256 bits, the `24.5x`
function-count multiplier, the free `P1` repair, `+17%` `H2`/`H3a`, `+15%`
overhead. The four bands must differ by **explicit named uncertainties**, not by
arbitrary multipliers, and the Gate-2B defect (`optimistic == central`) is
repaired here by giving `optimistic` a distinct, named assumption.

```text
optimistic   measured ratio_per_unit, and the SR cover walk's LOWER bound (309)
central      measured ratio_per_unit, cover upper bound (322)
conservative central + the residual m>=3 extrapolation risk (ratio_per_unit x 1.25)
worst        conservative + degree-8 SR needing 384 bits (t_panel x 1.164)
```

## 12. Checkpoint readiness

`CHECKPOINT_READY = YES` only if correspondence passes, `m`-sharing holds, the
measured ratio is not `HIGH`, no unresolved architecture defect remains in the
**first-moment** production cost model, and Gates 1/2A/2B are intact. This means
"ready to DESIGN the first binding checkpoint", never that one exists.

**Scientific boundary, restated:** first-moment assembly feasibility is not
closure of `K2` `s_min`, `K3` `M_2`, `K4` `H2` or `K5` `H3a`. Those remain
unresolved after this gate.

## 13. Out of scope — not run

Second moments, `s_min`, `M_2`, SR production, full CUSUM cover, all `m`,
`H2`/`H3a`, Lean, full Arb campaign, any binding checkpoint.

## 14. Repository safety

Branch `p5y-gate1-micropilots` (continued), namespace
`level4/closure_proofs/p5y_gate2c_m2_assembly/`. No merge to main, no push, no
binding checkpoint, no modification of P5, P5X, Gate-1, Gate-2A or Gate-2B.
