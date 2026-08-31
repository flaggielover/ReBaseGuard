# Provenance

## 1. Starting point

```text
commit  68bc23d2bc90c33bcc638bbedf90b2a855e6480d
subject close Level-4 Priority 3 m-rho stability map
tree    clean
```

`m_gt_1_priority1`, `sr_derivative_priority2`, `m_rho_stability_priority3`,
`location_family` and `location_family_track3ab` are read-only scientific
dependencies for this campaign.  `tests/test_integrity.py` asserts on every run
that `git diff HEAD` is empty for each of them.

## 2. Honest account of the freeze

**This protocol was frozen after an exploratory pilot, not before it.**  Saying
otherwise would be false, so the pilot is recorded here in full.

The pilot did three things.

1. **It built the Route-Q reference.**  The realisation that the memoryless
   detector `tau = inf{t : |Z_t| >= c}` collapses every stopped quantity to
   one-dimensional integrals came from the pilot, and it is why the campaign
   has an evidence route with no sampling error at all.

2. **It found and fixed a real defect in this campaign's own code.**  The
   common-random-number stream keyed Philox on
   `counter = (batch << 32) | step`.  Philox emits four 64-bit words per
   counter increment, so a draw of `n_paths` doubles advances the counter by
   about `n_paths/4`, and consecutive steps' "independent" innovations were
   overlapping shifted copies of each other.  The symptom was a stable ~14%
   disagreement between Route A and Route B for Student-`t` under the CUSUM,
   while the memoryless detector — where paths stop after one or two steps and
   the overlap barely matters — looked almost fine.  Route Q is what settled
   which side was wrong: it reproduced Route A to twelve digits.  The stream
   now reserves `2^64` counter values per `(batch, step)`, and
   `tests/test_detectors_and_simulation.py::test_aligned_streams_do_not_overlap_between_steps`
   is a permanent regression guard.

3. **It sized the campaign and chose the Route-B estimator.**  A central
   difference is `O(h^2)` accurate, and at the frozen operating point the pilot
   measured `D(0.05) = 15.016`, `D(0.025) = 15.687`, `D(0.0125) = 15.882`
   against a Route-A value of `15.896` — a clean `h^2` law with a resolvable
   bias.  Route B therefore reports the per-batch Richardson combination, and
   the `O(h^2)` law is re-tested rather than assumed by the independent finer
   ladder in `results/correspondence.json`.

Nothing about the *scientific outcome* — which families pass, whether the
identity holds, whether the correction sign generalises — was known when the
protocol was frozen.  The pilot Gaussian and `t3` cells at the reduced
operating point were seen; every other cell was not.

## 3. Frozen inputs

| file | sha256 recorded in |
|---|---|
| `configs/P4_PROTOCOL.json` | `manifest.json` → `frozen_new_inputs.protocol_sha256` |
| `certificates/WITNESS.json` | `manifest.json` → `frozen_new_inputs.finite_support_witness_sha256` |
| `lean/GeneralLocationFamilyP4.lean` | `manifest.json` → `lean.source_sha256` |

`tests/test_integrity.py` recomputes all three.

## 4. Inherited conventions, unchanged

* residual convention `Z_t = eps_t - e`, `f_e(z) = f(z+e)`, parameter score
  `s = f'/f = -psi` — from `location_family` / `location_family_track3ab`;
* window `w = min(m, tau)`, denominator `w`, terminal increment included —
  from `m_gt_1_priority1`;
* inclusive post-update alarm; ordinary `tau` from `t = 1`;
* frozen CUSUM `k = 1/2`, `h = 5`; frozen SR `A = 520.886133602749`;
* `m` grid `[1, 2, 3, 5]` — from `m_rho_stability_priority3`;
* admissible `rho` domain `[0, 1]`;
* the 3% relative correspondence limit — from the frozen Track-3 gate;
* Priority-3's classification rule and its `INCONCLUSIVE` downgrade.

## 5. New inputs introduced by Priority 4, and why

| input | value | why it is new |
|---|---|---|
| innovation families | gaussian, laplace, logistic, t3, t1p5, skewnormal4, uniform, cauchy | the whole point of the campaign; chosen to span bounded/unbounded score, finite/infinite variance, symmetric/asymmetric, and the two proved failure modes |
| reduced operating points | `h = 2`, `A = 20` | the frozen points have ARL ≈ 465, and a cross-family grid at that ARL with usable precision is not reachable in the time available; the reduced points share the recursion exactly and are labelled as a separate layer everywhere |
| Route-Q threshold | `c = 2` (`c = 1` for uniform, whose support is `±sqrt 3`) | a memoryless detector with a moderate alarm probability |
| Richardson step pair | `(0.05, 0.025)` | see Section 2.3 |
| master seeds | `4010001`-`4010006` | `tests/test_integrity.py::test_master_seeds_are_confined_to_this_namespace` |

## 6. Environment

```text
python      3.14.5 (level4/.venv)
numpy       2.5.2
scipy       1.18.0
pytest      9.1.1
python-flint 0.9.0   (Arb)
lean        leanprover/lean4:v4.34.0-rc1
mathlib     v4.34.0-rc1
```

## 6.1 Run record, including two things that went wrong

**The correspondence campaign was launched twice by accident**, with the same
protocol and the same seeds.  The two runs are therefore bit-identical by
construction and are not independent evidence.  The trailing process was
terminated before it wrote anything; `results/correspondence.json` comes from a
single complete execution (6604 s).

**One tool call patched a file from the wrong working directory.**  Its cwd was
`level4/closure_proofs/sr_derivative_priority2`, which also contains a
`derive_closure.py`, and the script rewrote that file.  The rewrite was
byte-identical -- the search patterns did not match, so `str.replace` was a
no-op -- and the file hashes identically to `HEAD`.  All twelve protected trees
are clean against `HEAD` and `tests/test_integrity.py` asserts this on every
run.  No frozen artifact was changed.  It is recorded here because an auditor
should know that a write touched a frozen tree at all, not because anything
came of it.

**The repository-wide verification was stopped before completion.**
`run_repository_verification.py` was terminated mid-run and
`results/verification.json` was never written.  `derive_closure.py` records the
corresponding gate as *not passing* rather than skipping it, so the verdict is
not derived from an unfinished check.  `CLOSURE_REPORT.md` §9.2 lists exactly
what was run manually and what was not run at all.

**Independent adjudication subsequently completed that verification.**  The
new `results/verification.json` records `all_gates_pass=true`; required suites
pass, controlled environment and freeze-scoped replays behave as expected,
and grandfathered diagnostics remain unchanged.  The original interruption is
kept above as provenance rather than rewritten out of the history.

## 7. What was NOT done

* No frozen artifact was edited, repaired or relabelled.  The two findings in
  `ASSUMPTION_AUDIT.md` Section 4 about P1/P2's own hypotheses are recorded
  here, not applied there.
* No literature search was performed; see `NOVELTY_AUDIT.md`.
* At the time of the original handoff, no commit and no push had occurred.
  Independent adjudication and checkpoint integration are recorded separately.
