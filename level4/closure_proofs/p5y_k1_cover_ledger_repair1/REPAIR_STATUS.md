# Repair 1 status

    REPAIR_VERDICT              = REPAIR_READY_FOR_INDEPENDENT_ADJUDICATION
    REPAIRED_COMMIT_BASE        = c0a1f40cff6974899cd44ab424591bb6a819c949
    DERIVATIVE_DEPENDENCY       = repaired (S0 remainder charged exactly once)
    WORK_UNIVERSE / RESUME      = repaired (exact per-obligation identity)
    PRODUCTION_READY            = false
    IMPLEMENTATION_COMPLETE     = false
    COST_CAP_STATUS             = NOT_ESTABLISHED
    SCIENTIFIC_VERDICT_CHANGED  = NO

Scope: the two defects the independent adjudication identified, and nothing
else. Cell 325, SR, the far-field certificates and the cost cap are all
untouched and remain open.

--------------------------------------------------------------------------
## A. Defect 1 reproduced, then repaired

### Reproduction (pre-repair)

Static provenance in the reviewed source:

```text
cusum_layer2.py:379   extra = extra + self.reward_allow[0]     # F_0  local residual
cusum_layer2.py:395   extra = extra + self.reward_allow[1]     # dF_0 local residual
cusum_layer2.py:411   extra = extra + self.reward_allow[2]     # H_0  local residual
cusum_layer2.py:320   allow0 = tight_upper(self.reward_allow[k])   -> Sclosed_k node
propagate.py:39       _source_node(0, k) -> "Sclosed:k"
propagate.py:69       dag.local(nid, d(f"Sclosed_{k}"), ...)       -> the epsS input
propagate.py:87/90/93 resolvent_value/derivative/curvature consume it
```

So `epsF = C*(deltaF + epsS)` counts `reward_allow[k]` twice. The excess is
exactly `C * reward_allow[k]`, demonstrated on the real frozen DAG arithmetic
with a dyadic sentinel in
`tests/test_pre_repair_defects.py::test_remainder_is_charged_exactly_once`.

Measured on CUSUM cell 221 (`diagnostics/before_after_221.json`):

| object | reward_allow (the duplicate) | polynomial residual |
|---|---|---|
| F_0 | 4.309445e-53 | 1.291845e-05 |
| dF_0 | 2.479124e-52 | 3.245517e-05 |
| H_0 | 1.469277e-51 | 1.361805e-04 |

### Repair

Representation **A** of the frozen ERROR_ALGEBRA section 1 is adopted:
residual against the fixed candidate source, error carried once by the epsS
node. `reward_allow[k]` is removed from the three r = 0 local residuals and
left only in `Sclosed:k`. Every other object already used representation A.

`epsF = C*(deltaF + epsS)` and `epsD = C*(deltaD + k1*epsF + epsS')` keep their
frozen shape; STYLE_1, the complete `D_interval` and the single Taylor
derivative charge are untouched; the r >= 1 objects, the kernel-series
truncation and the whole-cell envelopes are unchanged.

### Verification: an invariant, not a number

`repair_check.py` locates the remainder in both places it could appear and
counts them. Across all five regression records:

```text
all_charged_exactly_once = True
representation           = "A: residual against fixed candidate + separate epsS"
F_0/dF_0/H_0: charge_count = 1, local = 0, dependency = reward_allow
```

Tests fail if the remainder is charged **zero** times, **twice**, or through
both paths.

### Numerical effect: none, and that is the correct outcome

The duplicate is ~1e-53 to 1e-51, roughly 48 orders below the certificate
values it sat inside. Every certified quantity is **identical** before and
after, at every cell, m and precision tested:

```text
mag(D_interval) delta = 0     M_R2 delta = 0     B_cover delta = 0
all statuses PASS -> PASS
```

Numerical improvement is explicitly NOT offered as proof of correctness.

### A measurement that constrains how tight the guard can be

`eps_z` (the frozen `taylor_remainder`) carries a relative radius of 2.04e-16,
and Arb stores ball radii with 30-bit precision. Two valid outward bounds of
the same quantity therefore differ by `~2^-30 * rad(A) ~ 4.8e-35`, about 1e18
times `reward_allow`. Exact bit-equality between "reviewed allowance minus
reward" and the recomputed allowance is not an available invariant.
`diagnostics/arb_radius_provenance.json` records the component radii. The
over-removal guard is stated at `2^-40` of the allowance -- comfortably above
the rounding artefact and twelve orders below any real term. The guard also
asserts, separately, that the repaired allowance still dominates its own
certified enclosure and never loosens the reviewed bound.

--------------------------------------------------------------------------
## B. Defect 2 reproduced, then repaired

### Reproduction (pre-repair)

`universe.admit_resume_record(record, *, backend_hash, impl_hash)` takes no
expected unit and validates only global context. Against the reviewed function,
a record for `("CUSUM", 0, "object", "h_1")` is still admitted after mutating
each of `detector`, `cell_index`, `unit_kind`, `function_or_m`, `e0`, `rho`,
`unit_hash` -- all seven accepted. `source_certificate_hashes`, which the frozen
`work.resume_identity` list requires, is absent from the reviewed identity
altogether.

### Repair

`repair_universe.admit_resume_record(record, expected_unit, ...)` rebuilds the
canonical identity and requires a field-for-field match on all 17 identity
fields plus a **recomputed** `unit_hash`:

```text
checkpoint_hash, cells_sha256, error_algebra_sha256, backend_hash,
implementation_hash, obligation_universe_total, detector, cell_index,
unit_kind, function_or_m, left, right, e0, rho, C_upper, precision_bits,
source_certificate_hashes                                (+ unit_hash)
```

`source_certificate_hashes` is derived from the frozen dependency graph;
`dependencies_of` is asserted equal to `algebra.unit_dependencies` on a sample.
Exact quantities use the repository's canonical encodings (affine `[p, s]`
rational-string pairs, reduced rationals); a float in an exact field is a hard
reject, never a tolerance comparison.

### Negative controls (all rejected)

```text
detector  cell  unit_kind  function  m  e0  rho  unit_hash
checkpoint_hash  implementation_hash  precision  cells_sha256
error_algebra_sha256  backend_hash  left  right  C_upper
obligation_universe_total  dependency_hash  source_certificate_hash
missing-any-required-field   forged-but-self-consistent unit_hash
float in an exact field      old 12,255 universe
superseded parent checkpoints
cross-shard identity substitution
leaf obligation admitted; forged leaf dependency rejected
reordered JSON admitted (canonical serialisation is order-independent)
```

--------------------------------------------------------------------------
## C. Regression (Phase 3)

`diagnostics/REGRESSION.md`, records in `diagnostics/regression/`.

```text
re-certified through the repaired path:
  CUSUM cell 221, m = 1,2,3,5, 256 bits          (full)
  CUSUM cell 293, m = 1,2,3,5, 256 bits          (full, the m>1 cross-check)
  CUSUM cell 221, m = 1, at 256 / 384 / 512 bits (precision diagnostic)

CUSUM_M_R2_SOUND candidate          unchanged (M_R2 delta = 0 for every m)
CUSUM_ALL_M_ASSEMBLY_SOUND candidate unchanged (all four m, both cells)
PRECISION_DIAGNOSTIC                 PASS (384/512 nested in 256, ratios 1.000)
17,978 enumeration                   unchanged
shard conservation 1/8/16/32/64      unchanged
DAG audits                           duplicate_edges = 0, all derivative
                                     edges on B_cover, 108 = 108 distinct
```

Frozen CUSUM-kernel correspondence at cell 221 (the `e ~ 1/4` cell the
reference values come from):

```text
h_2:0  = 1.831353e-06   (reference ~1.83e-06)
S_1:0  = 2.764060e-06   (reference ~2.76e-06)
```

Cell 293 sits at a different drift (`e ~ 1`) and legitimately gives different
values (6.62e-06 and 1.14e-05); it is a cross-check of the m>1 path, not of
those two reference constants.

**Cell 325 was not re-run and was not attacked.** `repair_qualify` refuses it
by construction. Its state remains `CURRENT_CERTIFICATE_FAILURE_ONLY`.

--------------------------------------------------------------------------
## D. Tests (Phase 4)

| suite | result |
|---|---|
| repair1 (default) | **52 passed** |
| repair1 pre-repair mode (`PRE_REPAIR_EXPECT_FAILURE=1`) | 4 passed, 2 skipped |
| reviewed implementation | **102 passed** (see note*) |
| CUSUM kernel | 18 passed |
| production driver | 25 passed |
| frozen successor | 24 passed, **2 failed** (known guard conflict) |
| `git diff --check` | clean |

\* While repair1 was still uncommitted,
`test_implementation_writes_only_inside_its_own_namespace` failed: it asserts
`git status --porcelain` shows nothing outside the reviewed namespace, and an
untracked new namespace is exactly that. It cleared on commit, as predicted,
and the suite is 102/102 at the repair commit. The reviewed implementation was
not edited to achieve this.

The 2 frozen-successor failures are the **already-documented guard conflict**
(`p5y_k1_cover_ledger_implementation/IMPLEMENTATION_STATUS.md` section H):
`audit.protected_check()` diffs START_HEAD against the worktree and rejects any
differing path outside its own namespace, so it fails for any commit made
anywhere after the freeze. The frozen tree remains byte-identical to its freeze
manifest. Not a mutation, and not caused by this repair.

--------------------------------------------------------------------------
## E. Self-audit (Phase 5)

`manifests/repair_self_audit.json` -- 16 checks, 0 failed:

```text
frozen_successor_untouched                    reviewed_implementation_commit_preserved
duplicate_S0_charge_absent                    S0_uncertainty_present_exactly_once
exact_resume_identity_enforced                all_single_field_mutations_rejected
source_certificate_hashes_bound               work_universe_17978_unchanged
shard_conservation_unchanged                  cpu_cap_1126_unchanged
precision_256_unchanged                       budgets_unchanged
production_disabled                           SR_still_unimplemented
far_field_still_unimplemented                 cell_325_still_unresolved
```

--------------------------------------------------------------------------
## F. Remaining unresolved

Unchanged by this repair, and still open:

```text
SR raw DAG absent                    (316 of 642 cells, 8,850 of 17,978 obligations)
SR M_R2 absent
SR all-m absent
far-field not implemented            (2 obligations)
cell 325 CURRENT_CERTIFICATE_FAILURE_ONLY   (m = 2, 3, 5)
full cost cap NOT_ESTABLISHED        (1126 CPU-h retained, not increased)
```

This repair does not claim implementation completeness, production readiness,
a cost-cap pass, or any change to P5Y closure.
