# SR full-cover cost feasibility against the frozen 1126 CPU-hour cap

Overnight campaign finding. Derived from adjudicated measurements only; no new
numerics were invented and no frozen quantity was altered.

---

## 1. Inputs, all from adjudicated or frozen artifacts

| quantity | value | source |
|---|---|---|
| frozen cap | **1126 CPU-h** | `spec.HARD_CAP_CPU_H` |
| cap may be raised | **False** | `p5y_k1_sr_backend_cost_audit/config/frozen_audit.json` |
| CUSUM measured | **206.086 CPU-h** | Aux4 full cover, commit `ea2ce6b` |
| SR sub-cells | 322 | frozen `work_model.SR_subcells` |
| panels per sub-cell-function | 83,452 | frozen `work_model` (= Gate-2B live-patch panel census) |
| work-model functions/detector | **19** | frozen `work_model.functions_per_detector` |
| overhead factor | 1.15 | frozen `work_model.overhead_factor` |
| cost formula | `K1 = 1.15 * (t_panel * EVALS / 3600 + CUSUM)` | frozen `work_model.formula` |
| optimized amortized `t_panel` | **2.5019e-3 s** | `sr_backend_cost_audit/results/benchmark.json`, ADJUDICATED (27/27 checks) |
| optimization speedup | 194.05x | same, adjudicated |

## 2. The empirical calibration the completed CUSUM campaign now provides

The same frozen work model projected the CUSUM side, and CUSUM has now actually
been measured:

```text
    work-model CUSUM projection   126.024 CPU-h
    CUSUM measured (326 cells)    206.086 CPU-h
    calibration factor            1.6353x      (the work model UNDER-projects)
```

This is new information that did not exist before the Aux4 campaign completed.
It is the only empirical check available on the work model's accuracy, and it
shows the model is optimistic by a factor of ~1.64 on the detector we can check.

## 3. The decisive discrepancy: functions per cell

The frozen work model takes `functions_per_detector = 19`. That is the count of
top-level OBJECT CLASSES (`h_1..h_4, S_0..S_4, F_0..F_4, dF_0..dF_4`).

It is **not** the number of panel-resolved candidate functions a cell must
certify. The validated CUSUM analogue (`cusum_layer2._candidates`) builds a
candidate for each object at each derivative order plus each finite kernel
power. Counting the SR DAG (`config/sr_dag.json`) the same way:

```text
    reward_chain  h_j        orders 0,1,2      4 x 3 = 12
    source_chain  S_r        orders 0,1,2      5 x 3 = 15
    finite_power  W_(r,j)    orders 0,1,2     10 x 3 = 30
    resolvent     F/D/H_r    orders 0,1,2      5 x 3 = 15
                                              --------
    SR candidate functions per cell                72
```

**72, not 19 — a factor of 3.79.** SR carries 10 finite-power indices where
CUSUM carries 6, so SR is heavier than CUSUM here, not lighter.

Consequently the frozen `SR_panel_evaluations = 510,559,336` is an
under-count by the same factor; the architecture actually implies ~1.94e9
panel evaluations.

## 4. Result

Applying the frozen formula with the adjudicated `t_panel`:

| functions/cell | SR raw | SR calibrated | K1 total | vs 1126 cap |
|---|---|---|---|---|
| 19 (work-model assumption) | 354.8 | 580.3 | **904.3** | 80% — fits |
| 48 (CUSUM-analogue census) | 896.4 | 1465.9 | 1922.8 | 171% — exceeds |
| **72 (actual SR DAG census)** | **1344.6** | **2198.9** | **2765.7** | **246% — exceeds** |

Even with **no** calibration applied, the SR DAG census gives
`K1_total = 1783.3 CPU-h = 158%` of the cap.

Residual SR allowance after CUSUM and overhead: **773.0 CPU-h**.
Required `t_panel` to fit at 72 functions: **1.438e-3 s**.
Measured amortized `t_panel`: **2.502e-3 s**.

> A further **1.74x** speedup would be needed on top of the already-adjudicated
> 194x optimization merely to fit the uncalibrated case; **3.6x** to fit the
> calibrated one.

## 5. Verdict

```text
    SR_FULL_COVER_COST = NOT_ESTABLISHED
    COST_CAP           = NOT_ESTABLISHED   (neither PASS nor FAIL)
```

The 1126 cap lies strictly **inside** the interval of defensible projections
(645 – 2766 CPU-h). It cannot be adjudicated in either direction from
projections. Two things would settle it, and neither is available tonight:

1. the **actual SR candidate census** — whether every one of the 72 DAG nodes
   truly needs an independent panel-resolved candidate, or whether closed forms
   and m-sharing reduce it materially (the honest bound is 19 <= n <= 72);
2. a **measured SR cell**, which requires the patch-resolved candidate solver
   that does not yet exist (`sr_patch.build_candidate` raises
   `CandidateSolveDeferred`).

## 6. What this does NOT establish

This is a projection, not a measurement, and it is **not** a finding that SR is
infeasible. It is a finding that SR feasibility is unresolved and that the
optimistic reading rests on a work-model assumption (19 functions) that the
frozen SR DAG contradicts (72).

Nothing here licenses raising the cap: `cap_may_be_raised = False`, and the
historical `HARD_CPU_CAP_historical = 1848` belongs to a superseded campaign and
is not the governing constraint for this one.
