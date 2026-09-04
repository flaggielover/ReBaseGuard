# P5Y GATE 2F — PILOT-SR-METRIC-B preregistration

**NON-BINDING.** A one-line repair-validation gate. It does **not** turn Gate-2E
into a PASS: `P5Y_GATE2E_DECISION = SR_METRIC_FAIL_CANDIDATE` stands permanently,
as does `P5Y_GATE2D_DECISION = SR_REALCANDIDATE_FAIL_REPRESENTATION`.

```text
P5Y_GATE1_DECISION     = GATE1_PASS_ROUTE_B_SUPPORTED         (immutable)
P5Y_GATE2A_DECISION    = SR_PRECISION_PASS_256                (immutable)
P5Y_GATE2B_DECISION    = SR_COVER_PASS_MEASURED               (immutable)
P5Y_GATE2C_DECISION    = M2_ASSEMBLY_INCOMPLETE_EXTERNAL      (immutable)
P5Y_GATE2CBIS_DECISION = M2_ASSEMBLY_B_PASS                   (immutable)
P5Y_GATE2D_DECISION    = SR_REALCANDIDATE_FAIL_REPRESENTATION (immutable, FAIL forever)
P5Y_GATE2E_DECISION    = SR_METRIC_FAIL_CANDIDATE             (immutable, FAIL forever)
```

## 0. The question

With the Gate-2E absolute metric kept unchanged, does making the `P1`
construction target and the `P1` acceptance threshold genuinely asymmetric
remove the floating-point knife edge and let the frozen genuine SR candidate
pass at the lowest valid working precision?

## 1. The only allowed change

```text
CONSTRUCTION RULE   E_d <= (1 - eps_P1) * 1e-9      eps_P1 = 1e-3   [used to solve for h_z]
ACCEPTANCE CHECK    E_d <= 1e-9                                     [the scientific requirement]
```
Two **distinct** constants, evaluated on different sides of the pipeline. The
rule creates headroom; the check tests the original requirement. Nothing else —
metric, budget, ledger, candidate, precision, geometry, panels, guards — changes.

## 2. Byte-for-byte inheritance

Gate-2F does **not re-declare** Gate-2E's constants. It imports Gate-2E's frozen
module and references its attributes directly, so equality is structural rather
than transcribed:

```text
inherited by direct reference from p5y_gate2e_sr_metric/sr_metric.py:
  BOUNDARY SLACK_R ALPHA W_TARGET LEDGER RESERVE_FRACTION LOCAL_GATE_COMPONENTS
  B_ABS LOCAL_GATE_BUDGET W_PANEL_MAX DELTA_CANDIDATE_MAX
  C_SR_QUARTER C_SR_ZERO C_SR_CERTIFIED_CAP N_PANELS E_ABS_RAW
  PATCH GRID E_NUM E_DEN DEGREE CAND_DEGREE PRECISIONS
  EPS_P1 P1_TARGET GATE2A_NZ MAX_COMPLEXITY_SCORE TIMING_REPEATS
  direction_audit()  acceptance_precondition()  representation_guard()  run_cell()
```

The **mathematics of every cell is Gate-2E's `run_cell`, called verbatim.** The
new `P1` verdict is computed from that cell's own reported `E_d`, so the absolute
metric, the composed contraction, the moments and the radii are bit-identical to
Gate-2E by construction, not by comparison.

A machine-readable equality manifest is written comparing every inherited
constant against Gate-2E's module and against Gate-2E's result artifact. The
**only** permitted semantic difference is the `P1` threshold pair.

## 3. Compute cap

```text
GATE2F_CPU_CAP = 180 CPU-seconds = 0.05 CPU-hours (hard)   preferred <= 72 s
```
Gate-2E completed in `4.46` CPU-s. External watchdog kept; no extension after T2.

## 4. Frozen metric (carried forward unchanged)

```text
scientific target R_MAX_LT_2      metric type ABSOLUTE
slack_R = 2.0    alpha = 0.1      w_target = 0.2
B_cover .050 | B_candidate .040 | B_kernel .040 | B_other .040
B_rounding .010 | B_interval .010 | B_resolvent 0 (multiplicative)
reserve .010 (non-redistributable)          local-gate budget 0.100
w_panel_max = 3.550874e-05        delta_candidate_max = 5.340433e-04
```
Not recomputed from any Gate-2F result.

## 5. Amplification-bound consistency

`C_SR(1/4) = 187.7472` remains an **UPPER** bound on the resolvent amplification.
Gate-2E's `direction_audit()` is re-invoked as a lightweight consistency
assertion only; the proof is not redesigned. Mismatch ->
`SR_METRIC_B_FAIL_ARCHITECTURE`, before the grid.

## 6. Frozen objects and grid

```text
genuine hhat_1 | non-separable hhat_2 probe | unit_candidate control
patch (17,11)  grid 64  bidegree (16,16)  degree-8 backend
precisions {256, 384, 512}    no 192 rerun, no 640/768/1024, no adaptive point
```
No object is refitted. Candidate identity is asserted against Gate-2D's and
Gate-2E's recorded `eps_cand` to the last digit.

## 7. The decisive `P1` asymmetry

```text
P1_RULE_TARGET     = (1 - eps_P1) * P1_TARGET       (solves for h_z)
P1_CHECK_THRESHOLD = P1_TARGET = 1e-9               (tests E_d)
MIN_HEADROOM_REL   = 1e-6                           (robustness guard, NOT the design target)
HEADROOM_REL       = (P1_CHECK_THRESHOLD - E_d) / P1_CHECK_THRESHOLD
```
The comparison is performed in **Arb**, not on the reported float, and the
recomputed `E_d` is asserted identical to the value Gate-2E's `run_cell`
reports. Expected headroom is `~1e-3`, i.e. `~1000x` above the guard.

## 8. Negative control for the fix (structural, pre-T2, no result artifact)

A deterministic test reproduces the **old symmetric** logic
(`old_rule_target == old_check_threshold`) on the same evaluation path and
asserts it yields knife-edge headroom (`< 1e-6`, in fact negative at `~-4.4e-16`),
then asserts the **new asymmetric** logic yields robust positive headroom
(`>= 1e-6`). This is the test that would have caught Gate-2E.

## 9. Enforced execution order

```text
inheritance equality audit
  -> amplification direction consistency
  -> P1 asymmetric-threshold structural checks
  -> candidate absolute-budget precondition
  -> representation-complexity guard
  -> ONLY THEN the precision grid
```
No cell may run if any preceding stage fails. A pre-T2 test supplies an invalid
precondition and asserts the grid is skipped.

## 10. Acceptance

Gate-2E's absolute metric, unchanged, is primary:
`total_absolute_error <= w_panel_max`. The old relative `P2` is reported for
every cell as a **diagnostic only** and may not decide anything.

Safe precision = the lowest of `{256,384,512}` with: absolute metric PASS, `P1`
acceptance PASS, `HEADROOM_REL >= 1e-6`, guard PASS, radii normal. **`256` is
not encoded as required.**

## 11. Reproducibility

`hhat_1 @ 256` is computed twice; endpoints, absolute metric, `E_d` and
`HEADROOM_REL` must be identical. Timing may differ.

## 12. Failure classification

`NONE / P1_HEADROOM_FAILURE / ABSOLUTE_METRIC_FAILURE / REPRESENTATION_FAILURE /
PRECISION_FAILURE / IMPLEMENTATION_DEFECT / UNKNOWN`. Not relabelled after results.

## 13. STOP rules

```text
S1 worker CPU reaches 180 s -> kill, no completed artifact, STOP_FIRED = YES
S2 asymmetric semantics not enforced, or headroom < 1e-6 everywhere -> FAIL_P1
S3 the absolute metric fails for the genuine candidate -> FAIL_ABSOLUTE
S4 inheritance audit / direction / identity / guard fails -> FAIL_ARCHITECTURE
S5 any path outside this namespace modified -> STOP the whole gate
S6 result-bearing semantic bug after T2 -> STOP; no adaptive repair
```

## 14. Cost model

Carried forward unchanged (`1868 / 3092 / 3697 / 4597` CPU-hours). A PASS does
**not** lower costs; only a change of selected precision would move the central
band, using previously measured scaling.

## 15. Boundary

Even a PASS leaves `K2` `s_min`, `K3` `M_2`, `K4` `H2`, `K5` `H3a` unresolved.
P5 remains `PARTIAL`. No closure is claimed.

## 16. Out of scope

New candidate fit, another patch, full cover, `m = 3` or `5`, second moments,
`s_min`, `M_2`, `H2`/`H3a`, Lean, Arb production, checkpoint creation.

## 17. Repository safety

Branch `p5y-gate1-micropilots`, namespace
`level4/closure_proofs/p5y_gate2f_sr_metric_b/`. No merge to main, no push, no
binding checkpoint, no modification of P5, P5X or any prior gate.
