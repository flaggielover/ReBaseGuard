# P5X R3 — frozen feasibility specification

Frozen **before** any R3 implementation or measurement, committed at
Checkpoint E. R2 (`e22cd0e`) and every earlier campaign are untouched. The exact
SR target of `EXACT_SR_TARGET.md`, the scope `e in [0,12]`, the `0.2` gate
threshold and the theorem interface are unchanged.

---

## 1. Selected architecture

**State-patch × innovation-panel local symbolic certifier**, basis **A**
(Taylor about the panel centre with a rigorous Lagrange remainder), fallback
**C** (direct Bernstein/interval enclosure — the incumbent method, so falling
back is a null change). Bases B (minimax) and D (rational) are rejected before
measurement on proof burden and Gaussian-integration incompatibility.

Classes: `CERTIFIED_LOCAL_APPROXIMATION` (softplus enclosure),
`CERTIFIED_KERNEL_REFACTOR` (closed-form centred moments replacing interval
quadrature), `CERTIFIED_TAIL_DECOMPOSITION` (core/strip split),
`CERTIFIED_BOUND_REFACTOR` (resolvent). None is a method or scope change.

## 2. Frozen geometry

```text
b_SR   = log(1+A) = 6.25744942922713562368...        (erratum D1)
c_SR   = log A + 1/2 = 6.75553146432147319284...
grid   = 64          (matches the incumbent certificate, for comparability)
patch width = b_SR/64 = 0.09777264733167399
core   z-region  = [ l_max(Y) , u_min(Y) ]
strips           = [ l_min, l_max ] and [ u_min, u_max ], each of width = patch width
```

Patch and panel geometry are **independent of `e` and of `m`** (the `z`-formulation
puts no `e` in `l`, `u`, `q_SR`), so a layout is reusable across the whole cover.

## 3. Frozen feasibility cell

Deliberately the **worst** patch of the incumbent certificate, not a convenient one:

```text
detector = SR (frozen, A = 4581762885148045/8796093022208)
m        = 1
e        = 1/4 exactly (exact rational)
patch    = p17_m11   -- the recorded `worst_patch` of sr_residual_global_a.json
           y^+ in [1.662135005, 1.759907652]
           y^- in [1.075499121, 1.173271768]
           l   in [-5.680032, -5.582260]      u in [4.995624, 5.093396]
           core = [-5.582260, 4.995624], length 10.577884
z-panel  = the CENTRAL core panel, i.e. the panel of the uniform core
           subdivision containing the core midpoint
degree   = d = 6 for the local softplus Taylor enclosure
precision = 192 bits (matching the incumbent SR certificate)
```

## 4. Frozen PASS criteria

All four required:

```text
P1  local softplus remainder E_d  <=  1e-9
P2  composed kernel enclosure relative half-width  <=  1e-6
P3  dependency amplification (interval vs point evaluation) <= 100x
P4  projected SR total  <=  8000 CPU-hours, evaluated by the frozen formula

      SR_total_CPU_h = 835 * 1210 * n_z * t_panel * 2 * 43 / 3600
      => the criterion is exactly   n_z * t_panel <= 0.3314531805 seconds

      835   = SR e-sub-cells (CUSUM's 334 x the 2.5 resolvent factor of R2)
      1210  = live state patches at grid 64
      2     = value + derivative residual for the m=1 first-moment unit
      43    = m and moment multiplier, DERIVED FROM OPERATOR COUNTS in the CUSUM
              measurement lane (not the previously assumed 36). Per window m the
              first moment needs 4m-2 certified functions (m values g_r, m
              derivatives, 2(m-1) backward h_j and sources S_j) and the second
              moment needs m(m+1) (the m(m+1)/2 pair functions G_{r,r'} and their
              e-derivatives); summing over m in {1,2,3,5} gives 36 + 50 = 86
              functions against a 2-function unit, i.e. 43x. The old 11x
              first-moment figure was an undercount: it counted only the g_r and
              omitted the derivative equations and the backward functions.
```

`n_z` is the number of core panels the frozen rule produces for this patch at
the measured accuracy; `t_panel` is the measured CPU per panel.

## 5. Frozen panel rule

```text
h_z := the largest half-width in { 2^-k * (core length)/2 : k = 0,1,2,... }
       for which the degree-6 softplus remainder E_6 <= 1e-9 on the patch
n_z  := ceil( core length / (2 h_z) )
```

Deterministic, evaluated before any residual, and bounded: if no `k <= 12`
qualifies, **ABORT**.

## 6. Retry ladder

**None.** One configuration, one run. If the gate fails, the second pre-frozen
candidate (basis C) is **not** run in this campaign — falling back to the
incumbent method is a null result and needs no benchmark.

## 7. Abort rule

Abort and record `FAIL` if: any self-test fails; the panel rule finds no
qualifying `k <= 12`; any Arb containment check raises; or the patch/strip
decomposition fails its exhaustiveness assertion.

## 8. Mandatory self-tests (§16)

| id | check |
|---|---|
| `T1` | the softplus enclosure contains high-precision point evaluations at panel endpoints and interior points |
| `T2` | the degree-`d+1` coefficient ball is a valid derivative bound: it contains `sp^{(d+1)}(u)/(d+1)!` at sampled `u`, and the enclosure widens monotonically with `H` |
| `T3` | patch endpoints and the core/strip split are exhaustive: `l_min <= l_max <= u_min <= u_max` and the three regions tile `[l_min, u_max]` |
| `T4` | alarm boundary: for `y` at both corners the live region is exactly `(l(y), u(y))` |
| `T5` | Gaussian moments: `N_0` matches `Phi` differences, `|N_k| <= h^k N_0` |
| `T6` | exact rational `e` retained (`e = 1/4`, denominator exact) |
| `T7` | corrected `b_SR = log(1+A)` honoured, and `log A` is **not** used as the domain |
| `T8` | no empirical monotonicity used |
| `T9` | deterministic output: two runs agree bit-for-bit |

Any failure `->` STOP; no gate.

## 9. Second-stage prototype (§19), only if the gate passes

`SR`, `m = 1`, `e in [0.24, 0.26]` on a small frozen layout. **Not** authorised
in advance: it requires the gate to pass first and is reported as
`NOT_RUN` otherwise.

## 10. Frozen classification bands

```text
projected SR CPU-hours:  >15000 R3_NOT_ENOUGH | 8000-15000 R3_PARTIAL |
                         3000-8000 R3_USEFUL | 1000-3000 R3_STRONG | <=1000 R3_BREAKTHROUGH
projected total P5X:     <=5000 PRACTICALLY_VIABLE | <=2000 STRONGLY_VIABLE
campaign class:          >10000 MORE_OPT_REQUIRED | 5000-10000 borderline |
                         2000-5000 READY_FOR_PRODUCTION_DESIGN | <=2000 BREAKTHROUGH_READY
SR full-cell speedup:    <2 WEAK | 2-4 MODERATE | 4-8 STRONG | >=8 BREAKTHROUGH
```

Not changed after results.

## 11. Pre-registered prediction

```text
predicted E_6 at the frozen panel width : <= 1e-12
predicted n_z                            : 8 - 16
predicted t_panel                        : 5 - 40 ms
predicted projected SR total             : 1000 - 6000 CPU-hours  -> R3_USEFUL or R3_STRONG
predicted campaign class                 : READY_FOR_PRODUCTION_DESIGN (borderline)
```

## 12. What R3 will not do

No full SR cover, no full P5X cover, no large `m`-grid, no production
authorisation, no change to any historical artifact, and no implementation of
the multiplicative-`xi` reformulation identified in
`R3_ARCHITECTURE_AUDIT.md` §4 (recorded as the R4 subject).

## 13. Parallel CUSUM measurement lane (§22)

Lightweight and non-blocking: replace the extrapolated `x11` and `x25/11`
multipliers by **operator counts composed with R2-measured primitive costs**,
rather than by building full `m>1` certifiers (which would not be lightweight).
Deliverable: `cusum_measurement_lane/` with the derived operator counts and the
resulting measured-primitive multipliers.

## 14. Test discipline (§23)

The `D8`/`D9` pattern has repeated four times. **R3 anchor-integrity tests use
git object hashes, committed tree hashes and source manifests only.** No R3 test
asserts transient worktree state. No `D10`.
