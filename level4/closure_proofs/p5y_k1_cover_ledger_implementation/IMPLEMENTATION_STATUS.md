# Implementation status against the frozen cover-ledger successor

    IMPLEMENTATION_VERDICT           = IMPLEMENTATION_INCOMPLETE
    PRODUCTION_READY                 = false
    SCIENTIFIC_VERDICT_CHANGED       = NO
    LEVEL4_GLOBAL_CLOSURE            = NO       (unchanged)
    FROZEN_SUCCESSOR                 = untouched, byte-identical
    HARD_CPU_CAP                     = 1126 CPU-hours (unchanged, not increased)
    PRODUCTION_PRECISION             = 256 bits (unchanged, not escalated)
    COST_CAP_STATUS                  = FAIL_BUDGET (indicative; see section E)

This namespace implements the frozen specification and qualifies as much of it
as the repository's existing scientific kernels allow. Two frozen implementation
dependencies could not be closed at all, and one detector could not be started.
Nothing below is production and nothing below changes a historical verdict.

--------------------------------------------------------------------------
## A. Per-dependency status

| Frozen implementation dependency | Status |
|---|---|
| complete derivative dependency propagation | **PASS** |
| certified whole-cell curvature `M_R2` | **PASS (CUSUM)** / **NOT_IMPLEMENTED (SR)** |
| exact all-m certified interval assembly | **PASS (CUSUM)** / **NOT_IMPLEMENTED (SR)** |
| the 17,978-obligation work universe | **PASS** |
| sharding, resume identity, replay | **PASS** |
| representative complete cover ledger | **PASS with 3 of 20 obligations FAILING** (CUSUM only) |
| 256 / 384 / 512-bit numerical diagnostic | **PASS** |
| cost and memory model under 1126 CPU-h | **FAIL_BUDGET** (indicative) |
| `complete_SR_raw_DAG` | **NOT_IMPLEMENTED** |
| two detector far-field certificates | **NOT_IMPLEMENTED** |

--------------------------------------------------------------------------
## B. Derivative dependency propagation — PASS

`epsD_r = C * (deltaD_r + k1 * epsF_r + epsS1_r)` is implemented in
`code/depgraph.py` with an auditable edge log keyed by the frozen ownership
4-tuple `(primitive_certificate, propagation_path, destination_quantity,
derivative_order)`. Measured on every representative cell:

```text
duplicate_edges                 0
derivative_edges_all_cover      true      (every order>=1 edge lands on B_cover)
```

Three structural prohibitions are enforced as exceptions, not conventions:

* `ValueStyleDerivativeCharge` — the old campaign's dimensionally wrong
  `C * delta_dF` charge against `B_candidate` is refused outright.
* `DoubleCountingError` — a repeated tagged edge, node or ledger charge raises.
* `SeparateDerivativeCharge` — `cover()` refuses any second `rho*epsD` term.

A primitive reaching both `R(e0)` and `R'(e0)` is two distinct charges, not a
duplicate, and a focused test asserts that distinction survives.

--------------------------------------------------------------------------
## C. Whole-cell curvature — PASS for CUSUM

The construction, its authorisation in the frozen ERROR_ALGEBRA, and the reason
the literal interval-`e` route is unusable are documented in
[diagnostics/METHOD.md](diagnostics/METHOD.md). In summary: whole-cell bounds
come from a certified midpoint residual plus a mean-value envelope built from
whole-line absolute Gaussian moments, then tightened by a monotone Taylor-in-`e`
refinement. Nothing is sampled; no finite difference, Monte-Carlo or dense grid
appears on any certified path.

The refinement matters a great deal. Unrefined, the chain amplifies a
first-level slack by roughly `(C k1)^2`:

```text
CUSUM cell 221   crude epsH_cell 47330.7   refined 340.2   139.1x tighter
CUSUM cell 0     crude epsH_cell 1.0e+06   refined 18098.6  55.4x tighter
```

Every iterate is independently valid (all four maps are monotone in `supH` and
each step takes `min` with the crude value), so no fixed point is asserted and
the old R1 bootstrap condition is NOT invoked. The observed contraction factor
`rho*C*2*k1` is reported per cell as evidence only; it came out at 0.5, which is
what the frozen step rule `rho <= 1/(4 a C)` with `a = 2 phi(0) = k1` forces.

### Two implementation defects this work found and fixed

1. **Double-charged source variation.** The F/D/H residuals are built against
   the FIXED closed-form source, so the source's own `e`-variation belongs to
   the `epsS` node alone. It was also being added to the residual envelope.
2. **Degree-120 series fed to the kernel.** The closed-form `h_1^(k)` (a
   recentred order-120 series) was passed directly to `_kernel_polynomials` as
   the argument of `K_i` in the `h_2` residual and of `J_i` in the `S_1`
   residual — exactly the failure the frozen CUSUM kernel warns about. It
   certified `h_2:0` at `2.3e+35` and `S_1:0` at `3.1e+36`, which poisoned every
   `m >= 2` assembly (`R2_interval ~ 1e42`) and inflated CPU by 3.4x. With
   `h_1^(k)` given a degree-12 candidate and certified against its own closed
   form, the same objects certify at `1.83e-06` and `2.76e-06`, agreeing to
   three significant figures with the frozen CUSUM kernel's independently
   measured `1.829e-06` and `2.786e-06`.

--------------------------------------------------------------------------
## D. Representative scientific results (CUSUM)

Full table: [diagnostics/REPRESENTATIVE_LEDGER.md](diagnostics/REPRESENTATIVE_LEDGER.md).
Five frozen anchor cells (0, 1/10, 1/4, 1, and 27/5 & 11/2 which share cell 325)
x m in {1,2,3,5} = 20 obligations.

```text
17 of 20 obligations PASS every frozen top-level and nested gate
 3 of 20 FAIL, all at cell 325 (m = 2, 3, 5)
20 of 20 pass the (-2,2) target enclosure gate
```

| | cell | m | B_cover | util of .050 |
|---|---:|---:|---|---:|
| worst PASSING | 293 | 5 | 0.0158666 | 31.73% |
| worst overall | 325 | 5 | 0.360478 | **720.96%** |

Worst-cell breakdown (cell 325, m=5, rho = 0.09624, C = 2.001):

```text
nominal drift variation   0.00170443
derivative uncertainty    0.000146189
curvature                 0.358627        <-- the entire failure
cover arithmetic          5.2e-77
total B_cover             0.360478        cap .050    margin -0.310478
every other top-level line passes with < 0.6% utilization
```

### The three failures are certificate looseness, not demonstrated curvature

At cell 325 the curvature enclosure is
`R2_interval = [-77.06, +77.44]` for m=5 — near-symmetric about zero. The
magnitude is *entirely* the certificate radius; the enclosure carries no
information about the true `R''`, which the surrounding data suggests is O(1)
(`R` sits at ~-0.199 and `R'` at ~0.019-0.034 across all m there).

The looseness is localised and understood. Cell 325 is the last CUSUM cell, with
the largest radius in the whole cover (`rho = 0.0962`, 5.3x cell 293, so `rho^2`
is 28x larger) and `e_max = 5.5`, which inflates the raw-kernel norms
`j_i = jz_i + e_max k_i + i k_(i-1)`. Every order-2 `delta_cell` there is ~100%
dominated by its `rho * Env` term (ratio 1.000 to three decimals), because the
Taylor-in-`e` refinement was applied to the resolvent chain (F, D, H) but not to
the order-2 source and finite-power chain (h'', S'', W''), which would need
order-3 jets.

Two identified, unimplemented remedies:

* extend the refinement to the order-2 h/S/W chain (needs an order-3 jet); and/or
* use drift-aware operator norms. ERROR_ALGEBRA calls the whole-line moments
  "admissible", not mandatory, and at `e ~ 5.4` they are pessimistic: the actual
  window gives `||K_e|| <= 0.54` against the whole-line 1.

Neither is done here. **These three obligations are reported FAIL, not
NOT_COMPUTED and certainly not PASS.** The frozen ERROR_ALGEBRA anticipates
exactly this: "A loose bound may fail .050; the geometry rule alone does not
promise a successful certificate."

### Independent cross-checks that the numbers are real

* **Known `e = 0` value.** `R` is odd, so `R(0) = 0`. Cell 0's midpoint is
  `e0 = 2.5415e-04`, and the certified `R_interval = [-0.00833, +0.000766]`
  is centred at `-0.00378`, matching `R'(0) * e0 = -14.887 * 2.5415e-4 =
  -0.003784` from the committed near-zero diagnosis.
* **Frozen kernel agreement.** `h_2` and `S_1` certified defects reproduce the
  frozen CUSUM kernel's values to three significant figures.
* **Frozen constant recovered.** The derived `M_2 = 8 phi(1) - 2 phi(0)`
  evaluates to `1.13788`, the constant independently frozen in the raw-variable
  certifier.
* **Precision invariance** (section F) confirms the bounds are residual-limited.

Point agreement was NOT used as a substitute for interval containment anywhere;
every gate is decided on the certified enclosure.

--------------------------------------------------------------------------
## E. Cost and memory — FAIL_BUDGET (indicative)

Full model: [benchmarks/cost_model.json](benchmarks/cost_model.json). Measured
on the 8-vCPU AWS node, one FLINT thread and one BLAS thread per worker, five
representative cells, the real 17,978-obligation universe.

Per-cell CPU by obligation class (mean over 5 cells, seconds):

| class | units/cell | mean | min | max | share |
|---|---:|---:|---:|---:|---:|
| object | 19 | 342.8 | 260.9 | 467.8 | 30.0% |
| dependency_bundle | 1 | 362.0 | 312.2 | 448.3 | 31.7% |
| curvature | 4 | 434.2 | 371.6 | 533.7 | 38.0% |
| assembly | 4 | <0.1 | | | ~0% |
| cell setup (shared) | - | 3.2 | 2.2 | 4.6 | 0.3% |
| **total per cell** | 28 | **1142.2** | 947.0 | 1420.5 | 100% |

The all-m assembly and ledger cost under 0.1 s per cell — it is exact rational
arithmetic over at most 15 terms. It is still a governed obligation and is still
counted; it is simply not a cost driver. The curvature class, which the frozen
successor could not cost at all, is the single largest one at 38%.

```text
CUSUM, complete, MEASURED        103.4 CPU-h central   128.6 CPU-h conservative
  (frozen base-ONLY estimate was 127.2 CPU-h, so the COMPLETE CUSUM obligation
   set lands at about the frozen base-only figure)
complete / base-object ratio     3.33

SR                               NOT_MEASURABLE - no raw-variable SR DAG exists
SR indicative extrapolation      1618.2 central .. 2532.3 worst plausible CPU-h
  (frozen SR base-only projection x the CUSUM 3.33 ratio; a DIFFERENT backend
   and a DIFFERENT formulation, so this is not a measurement of anything)

CAMPAIGN indicative              1721.6 central .. 2660.9 conservative CPU-h
FROZEN HARD CAP                  1126 CPU-h   (unchanged, not increased)
                                 ------------------------------------------
COST_CAP_STATUS                  FAIL_BUDGET
```

The central indicative projection exceeds the frozen cap by 52.9%, and the
conservative one by 136.3%. The cap is NOT raised here. Per the frozen
CHECKPOINT: "if it cannot fit a separate governed cap successor is required."

Two honest caveats in both directions. The SR half is an extrapolation from a
different backend, so the total is indicative, not established — a real SR
implementation could be cheaper or dearer. And the measured CUSUM half now
carries the complete obligation set, including the curvature and dependency
bundles the frozen base-only model excluded, for roughly the cost the frozen
model allowed for CUSUM base objects alone.

Memory is comfortable and is not the constraint:

```text
measured peak RSS per worker     201.9 MiB      frozen per-worker budget 300 MiB
projected total at 64 workers    12.6 GiB       host has 30 GiB
oversubscription                 not allowed, not used
```

Indicative wall time at the central CPU projection: 215.2 h at 8 workers,
107.6 h at 16, 53.8 h at 32, 26.9 h at 64. The 16/32/64-worker figures are
arithmetic divisions of an already-extrapolated total on a host that has 8
cores; only the 8-worker figure rests on measured concurrency.

--------------------------------------------------------------------------
## F. Precision — PASS

[diagnostics/PRECISION.md](diagnostics/PRECISION.md). At 256 / 384 / 512 bits
the certified `mag(D_interval)`, `M_R2` and `B_cover` are identical and the
higher-precision `R`/`D` enclosures are contained in the 256-bit ones. The local
residuals do move, at relative 1e-45 and 1e-26 — twenty-plus orders below the
certificate values. The certificate is residual-limited, not rounding-limited.
No 256-bit certification failed where a higher precision succeeded. Production
precision remains 256 bits.

--------------------------------------------------------------------------
## G. What is NOT implemented

* **The SR raw-variable DAG.** Task1R certified the `F_0` class only, on one
  patch, at one drift, in a different (softplus Taylor-model) formulation.
  `h_j`, `S_r`, `F_r`, `dF_r` for `r >= 1`, the derivative and curvature chains,
  and the whole-cell envelopes do not exist for SR. `qualify.run_cell("SR", ...)`
  returns `NOT_IMPLEMENTED` with a failure class, never a PASS and never a zero.
  This is 316 of the 642 cells and 8,850 of the 17,978 obligations.
* **The two far-field certificates.** The P5X-T3 far-field obligation and the
  parent splice obligations remain mandatory and are not discharged here.
* **The order-2 refinement for the h/S/W chain**, which is what would decide the
  three failing cell-325 obligations either way.

None of these is reported as zero, small, or passing.

--------------------------------------------------------------------------
## H. A governance conflict inside the frozen artifact — surfaced, not fixed

Committing this namespace makes **2 of the frozen successor's own 26 tests
fail**: `GovernanceTests::test_protected_tree` and
`GovernanceTests::test_read_only_adjudication`. Both come from one predicate,
`p5y_k1_cover_ledger_successor/code/audit.py::protected_check()`, which runs

```text
git diff --name-only <START_HEAD> --
```

against the **worktree** and rejects any differing path outside its own
namespace. That guard therefore fails for *any* commit made anywhere in the
repository after the freeze commit — including the implementation namespace its
own CHECKPOINT explicitly authorises ("Implementations may consume these
immutable contracts in a NEW implementation namespace"). It is a freeze-time
guard, not a mutation detector. Note that it passed while this work was
uncommitted and fails the moment the work is committed, which is the signature
of a one-commit-only condition.

This is **not** a mutation of the frozen namespace. Recomputed independently in
`manifests/self_audit.json`:

```text
frozen tree byte-identical to its own freeze manifest      true
START_HEAD git object manifest unchanged                   true
paths the guard objects to                                 40
all objected paths inside THIS namespace                   true
is_a_frozen_namespace_mutation                             false
```

The frozen namespace is immutable and was **not** edited to satisfy its own
guard, and the guard was not bypassed, whitelisted or reinterpreted. The
conflict is recorded here for the independent adjudicator to dispose of. The
other 24 frozen tests pass, and every substantive frozen check
(`cover_replay`, `cover_hash`, `scope_preserved`, `precision_preserved`,
`numeric_budgets_preserved`, `cap_not_increased`, `production_off`,
`scientific_state_unchanged`, ...) still passes.

--------------------------------------------------------------------------
## I. Environment note

`scipy` is imported at module load by the frozen `ra_certifier`, via
`rebaseguard_certify.spectral_candidate`, purely for the non-rigorous candidate
solver. It was not present in `level4/.venv` and was installed to run the frozen
code. No certified path in this namespace uses it: `cusum_layer1.dyadic_candidate`
is a numpy-only reimplementation of the frozen dyadic rounding, and a focused
test asserts it is byte-identical to the frozen one. This is an environment
change, not a repository change.
