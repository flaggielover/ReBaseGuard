# Level-4 Priority 3 independent closure adjudication

## Independent verdict

```text
Level-4 Priority 3 -- CLOSED
```

The original candidate's `CLOSED` verdict was **modified, then independently
accepted**. It was not inherited. The scientific map survived independent
recomputation, but the candidate's post-result gate widening was rejected and
replaced by a stronger literal-pass contract. Under the intended current
environment, every named environment-sensitive suite passes, so closure does
not depend on excusing those failures.

This verdict means only that the theorem-supported, first-order local
`m`--`rho` stability map over the two closed detector campaigns and their exact
finite-support witnesses is closed at `m in {1,2,3,5}`. It does not establish
global or nonlinear stability, a stationary-law result, detector universality,
or any non-Gaussian extension.

Most importantly:

```text
frozen infinite-horizon Gaussian gains interval certified: NO
```

The Gaussian rows remain theorem-supported Monte Carlo estimates. Rigorous
Arb/exact certification covers only the finite-support witness rows.

## 1. Frozen intake and review independence

Before any reviewer modification:

```text
HEAD: 987056ec32bcc5e437e4731dd22e0a88fb1119c0
branch: main, aligned with origin/main
tracked/staged changes: none
candidate files: 49 untracked files under this namespace
candidate aggregate SHA-256:
  41f82b34481bc2427d16a9534affb9fdd0c6efa328db4467d96f0f8f193bc319
```

The reviewer stored a path-level manifest independently of the candidate's own
manifest and verified it remained byte-identical throughout Phase 1. Fifteen
ignored `__pycache__/*.pyc` files were separately identified and removed as
regenerable runtime debris. The temporary adjudication design scaffold was
also removed before verification and staging; it was review workflow, not a
durable scientific artifact.

Candidate generators, reports, tests, and `derive_closure.py` were treated as
objects of review. The theorem consequences, all boundaries and intervals,
every uncertainty-sensitive cell, both exact witnesses, upstream hashes, the
Lean source, the Arb certificate, and the three environment diagnoses were
recomputed or replayed independently before corrections began.

## 2. Exact theorem and regime audit

The imported closed P1/P2 derivative statements give, per detector `D` and
supported window `m`,

```text
lambda_{D,m}(rho) = F'_{rho,m}(0)
                  = rho (1-GammaTilde_{D,m}),
|lambda_{D,m}(rho)| = rho |1-GammaTilde_{D,m}|,  rho in [0,1].
```

When `GammaTilde != 1`, the algebraic boundary is

```text
rho_c = 1 / |1-GammaTilde|.
```

Below it the origin is locally attracting, above it locally repelling, and at
it first-order linearization is inconclusive. The simplified expression
`1/(GammaTilde-1)` is used only for `GammaTilde>1`.

The reviewer corrected an incomplete endpoint description in the candidate:

- `GammaTilde>2`: an interior boundary;
- `GammaTilde=2`: attraction on `[0,1)`, boundary at full reuse;
- `1<GammaTilde<2`: attraction throughout `[0,1]`;
- `GammaTilde=1`: multiplier identically zero; no boundary;
- `0<GammaTilde<1`: attraction throughout `[0,1]`;
- `GammaTilde=0`: attraction on `[0,1)`, boundary at full reuse;
- `GammaTilde<0`: an interior boundary from the absolute-value form.

`rho=0` has multiplier zero by the same formula. All claims remain strictly
first-order and local.

## 3. Independently recomputed Gaussian boundaries

The authoritative gains and across-batch standard errors were read directly
from the immutable P1/P2 numerical JSON, without importing Priority-3 code.
With `z95=1.959963984540054`, the reviewer recomputed the point boundary, delta
SE, and exact monotone transform of the gain interval.

| detector | m | gain | gain SE | `rho_c` | delta SE | transformed 95% interval |
|---|---:|---:|---:|---:|---:|---|
| CUSUM | 1 | 15.916540430 | 0.059905189 | 0.067039673 | 0.000269233 | [0.066516108, 0.067571547] |
| CUSUM | 2 | 13.264824962 | 0.050152156 | 0.081533981 | 0.000333401 | [0.080885722, 0.082192714] |
| CUSUM | 3 | 11.957078195 | 0.043161330 | 0.091265206 | 0.000359505 | [0.090565987, 0.091975306] |
| CUSUM | 5 | 10.226363970 | 0.035237075 | 0.108385059 | 0.000413941 | [0.107579777, 0.109202487] |
| SR | 1 | 17.453570692 | 0.065880691 | 0.060777081 | 0.000243354 | [0.060303831, 0.061257818] |
| SR | 2 | 14.500509744 | 0.056724862 | 0.074071277 | 0.000311224 | [0.073466272, 0.074686330] |
| SR | 3 | 12.972654634 | 0.049010543 | 0.083523665 | 0.000341907 | [0.082858873, 0.084199212] |
| SR | 5 | 11.048526073 | 0.041046532 | 0.099517083 | 0.000406510 | [0.098726665, 0.100320259] |

These values exactly match the candidate machine artifacts to floating-point
precision. They are empirical Gaussian correspondence, not rigorous gain
enclosures.

## 4. Uncertainty and cross-detector audit

All 304 declared grid cells were independently reconstructed from
`rho|1-GammaTilde|`. Exactly one candidate-grid cell crosses unit magnitude
under the transformed 95% gain interval:

```text
Gaussian SR, m=5, rho=0.10:
|lambda| interval = [0.9968076348404744, 1.0128975798590936]
classification = INCONCLUSIVE
```

No other grid cell crosses. All eight empirical cells evaluated at their
point-estimate boundaries are also uncertainty-sensitive by construction; the
eight exact witness boundaries are exact.

For every supported `m`, the frozen Gaussian SR point boundary is below the
CUSUM boundary and the transformed intervals are disjoint. The positive gaps
between the SR upper endpoint and CUSUM lower endpoint are approximately
`0.0052583, 0.0061994, 0.0063668, 0.0072595`. This is an empirical ordering of
the two frozen specializations only—not a detector-universal theorem.

The candidate labels its grid as preregistered, but all 49 files arrived in one
uncommitted intake, so temporal preregistration cannot be independently
authenticated. Reports now call it the candidate-declared fixed grid. This
does not change the scientific result: the boundary is analytic and continuous
in `rho`; grid cells are descriptive evaluations, not fitted thresholds.

## 5. Exact witnesses and Arb audit

Independent `Fraction` arithmetic on the immutable witness paths gives:

| witness | m=1 | m=2 | m=3 | m=5 |
|---|---:|---:|---:|---:|
| P1 CUSUM-compatible gain | 15/2 | 15/2 | 15/2 | 15/2 |
| exact `rho_c` | 2/13 | 2/13 | 2/13 | 2/13 |
| P2 SR-compatible gain | 4 | 3 | 8/3 | 12/5 |
| exact `rho_c` | 1/3 | 1/2 | 3/5 | 5/7 |

Every rational boundary satisfies `|rho_c(1-GammaTilde)|=1` exactly. The SR
witness recurrence was independently replayed with Arb at 128 bits and stops
at `tau=1,1,6,6`. The stored certificate matches the exact replay, resolves all
152 witness-grid cells, and records SR witness `m=3, rho=3/5` as the sole exact
boundary on the declared grid.

An Arb ball enclosing one is used only as a consistency enclosure; exact
boundary equality comes from rational arithmetic. The certificate contains no
Gaussian gain, states `gaussian_layers_certified=false`, and uses
`python-flint 0.9.0 / Arb` at 128 bits.

## 6. P1/P2 provenance and immutability

All ten consumed P1/P2 artifacts match the SHA-256 values pinned in
`manifest.json`. Both upstream decision files say `CLOSED`. The P1/P2 trees,
historical SR, Track 1A/1B, D4, the earlier `m_gt_1` tree, and Stage D have zero
tracked modifications and zero untracked additions from Priority 3.

The Gaussian inputs are loaded through the authoritative pointers
`score.gamma_mean`, `score.slope_se`, `final.gamma`, and `final.gamma_se`.
Witness values are recomputed from path data with the random denominator and
terminal increment retained. No value is interpolated across `m`.

## 7. Lean source review and axiom audit

The corrected Priority-3 spine and both protected dependencies compile from
source under pinned Lean `v4.34.0-rc1`. Four `Iff.rfl` lemmas merely prove that
the Priority-3 predicates are definitionally identical to the closed P1/P2
predicates; they are not presented as the substantive proof. The substantive
declarations prove magnitude factorization, strict monotonicity, boundary and
attraction/repulsion criteria, domain intersection, moderate-gain endpoints,
interval robustness, trichotomy, and both detector bridges.

Reviewer corrections renamed the misleading SR bridge from an “attracting”
name to `sr_repelling_of_criticalRho_lt` and added explicit full-reuse endpoint
theorems. Fourteen declarations are axiom-audited:

```text
abs_multiplier
abs_multiplier_strictMonoOn
boundary_at_criticalRho
attracting_iff_lt_criticalRho
repelling_iff_criticalRho_lt
criticalRho_le_one_iff
attracting_of_gain_le_two
full_reuse_attracting_of_gain_between_zero_two
full_reuse_boundary_of_gain_eq_zero_or_two
attracting_of_interval
repelling_of_interval
trichotomy
cusum_attracting_of_lt_criticalRho
sr_repelling_of_criticalRho_lt
```

Every declaration uses only `propext`, `Classical.choice`, and `Quot.sound`.
There is no `sorry`, `sorryAx`, project-specific scientific axiom, or numerical
Gaussian claim in Lean.

## 8. Figures and cross-representation correspondence

The three figures regenerate from the final JSON, their input/output hashes
match `figure_index.json`, and all 304 plotted cells reclassify correctly.
The reviewer removed lines joining distinct `m` values from the critical reuse
plot so a discrete supported grid cannot be visually mistaken for an
interpolated curve. The main stability figure uses separated categorical
columns, and empirical/certified layers remain visually and textually distinct.

JSON, CSV, report tables, figures, exact certificate, and Lean share the same
multiplier and evidence boundary. Gaussian rows are never labelled certified.

## 9. Circularity and gate-contract adjudication

The candidate had changed two self-referential tests and explicitly disclosed:
“I widened the gate definition after seeing these results.” The original
candidate verifier then excluded Priority 1, historical SR, and Track 1B from
the literal required-pass set and accepted matching pristine failures instead.

That post-hoc widening is **not accepted**. The frozen Priority-3 protocol did
not preregister it, and pristine failure equivalence is diagnostic evidence,
not a passing test. The reviewer restored all three suites to the literal
required set and removed the focused test's hardcoded assertion that `rg` must
be absent. `derive_closure.py` now requires verification schema v3, the literal
suite set, and the controlled causal matrix.

The candidate's map checks are not accepted solely because generated JSON says
`valid=true`: focused tests and reviewer scratch calculations independently
recompute the formulas, intervals, exact values, source hashes, and figure
cells. The final closure verdict is regenerated only after those gates.

## 10. Environment diagnostics

All three disputed suites pass literally in the current intended environment:

| suite | current result |
|---|---:|
| Priority 1 | 13 passed |
| historical SR | 94 passed |
| Track 1B | 32 passed |

Controlled worktree and pristine-HEAD tests positively establish causality:

- Priority-1's exact integrity node passes under `en_US.UTF-8` and fails under
  `C`, both with `rg` available;
- the historical-SR and Track-1B seed nodes pass with `rg` and fail when `rg`
  is deliberately removed from `PATH`;
- all twelve controlled outcomes match in both scopes.

The Track-1B content set is identical under both collations. Only ordering
changes: `C` gives hash `196e9780...`, while `en_US.UTF-8` gives the recorded
`e28930fe...`. The current `rg` is the VS Code extension binary recorded in
`results/verification.json`.

The pristine full historical-SR suite has one archive-layout completeness
failure not present in the worktree; it is not one of the disputed current
failures, and the exact controlled seed node passes with `rg`. No protected
test or manifest was edited.

## 11. Historical diagnostics

The following remain visible and non-passing exactly as established before
Priority 3:

- the old 52-file guard rejects the later 92-file additive SR tree, appearing
  in the Level-4 aggregate, external-validation-v2, final global re-audit, and
  terminal Level-4 closure suites;
- the post-Level-4 archive verifier reports the later root `README.md` drift.

Priority 2 separately froze and adjudicated both SR snapshots and the README
drift. Priority 3 changes none of the responsible paths. These are
`HISTORICAL_DIAGNOSTICS`, not Priority-3 gate passes or failures.

## 12. Verification matrix

Literal required gates:

| gate | result |
|---|---|
| Priority-3 focused | 85 passed |
| Level 1--3 full verifier | PASS; terminal regression suite 90 passed |
| Priority 1 | 13 passed |
| Priority 2 | 19 passed |
| historical SR | 94 passed |
| Track 1B | 32 passed |
| D4 phase map | 18 passed |
| external validation v3 | 75 passed |
| L4R-06 | 28 passed |
| L4R-12 | 26 passed |
| Lean source compile / axiom audit | PASS, 14 declarations |
| Arb/exact replay | PASS, both witness layers |
| controlled environment matrix | PASS, 12/12 expected outcomes |
| mechanical closure derivation | `CLOSED`, all ten categories true |

Diagnostic suites retain the expected historical failures: Level-4 aggregate
ends with `1 failed, 17 passed`; external validation v2 with `2 failed, 43
passed`; final global re-audit with `3 failed, 33 passed`; terminal Level-4
closure with `4 failed, 32 passed`; and post-archive verification with the
known `README.md` mismatch.

## 13. Package-bloat and reviewer-change audit

The 49 Git-visible candidate artifacts are justified by the requested package:
human theorem/proof/evidence reports, frozen configuration and manifest,
machine JSON/CSV, three publication figures, Python source/drivers, Lean,
Arb, and focused tests. No duplicate clean-room implementation was added.
Fifteen ignored `.pyc` files and their two empty cache directories were removed.

Material reviewer corrections are confined to this namespace and cover:

- exact gain-regime prose and focused endpoint tests;
- two additional Lean endpoint theorems and the SR bridge rename;
- literal environment-sensitive required gates plus controlled diagnostics;
- removal of the hardcoded “`rg` absent” test assumption;
- independent intake/adjudication metadata and closure semantics;
- honest temporal wording for the candidate-declared grid;
- discrete-marker figure rendering; and
- regenerated Lean, verification, figure, report, and closure artifacts.

Exactly 28 of the 49 Git-visible intake files changed:

```text
CLOSURE_REPORT.md
EVIDENCE_BOUNDARY.md
LEAN_CORRESPONDENCE.md
PROOF.md
PROVENANCE.md
README.md
STABILITY_MAP_REPORT.md
THEOREM.md
derive_closure.py
figures/figure_index.json
figures/p3_critical_reuse_by_detector.png
figures/p3_evidence_grid.png
lean/AxiomAudit.lean
lean/StabilityMapP3.lean
manifest.json
results/axiom_audit.txt
results/closure_decision.json
results/lean_compile.json
results/stability_map.csv
results/verification.json
run_lean.py
run_repository_verification.py
src/rebaseguard_p3_map/figures.py
src/rebaseguard_p3_map/mapbuild.py
src/rebaseguard_p3_map/reports.py
tests/test_classifier.py
tests/test_integrity.py
tests/test_lean.py
```

No Git-visible intake path was added or removed; the other 21 are byte-identical
to intake. Removed non-Git debris consists only of the 15 listed `.pyc` files
and two now-empty `__pycache__` directories.

The final intake-versus-review path/hash ledger is recorded in the independent
review handoff and contains no path outside this namespace. Protected-history
hashes remain unchanged.

## 14. Remaining limitations and strengthening opportunities

- Rigorous infinite-horizon Gaussian CUSUM/SR gain certification remains the
  principal strengthening opportunity; it is not part of this closure.
- Only `m in {1,2,3,5}` is supported. New `m` values require new upstream gain
  evidence, not interpolation.
- The result is first-order and local. Basins, nonlinear convergence, and the
  stochastic repeated-monitoring chain require separate analysis.
- The empirical cross-detector ordering is specific to the two frozen Gaussian
  configurations.
- The candidate protocol's temporal preregistration cannot be authenticated
  from the uncommitted intake. Reviewer-time immutability is authenticated.
- Historical tests remain locale/tool dependent; no protected file was changed
  to make those tests hermetic.
