# Symmetric two-chart SR derivative theorem: implementation plan

**Design:** `docs/superpowers/specs/2026-08-22-sr-derivative-design.md`

**Constraint:** follow the scientific gate order exactly. No confirmatory
outcome before protocol freeze, no Lean before numerical authorization, and no
Arb before Lean.

## Task 1 — Preserve baseline and historical hashes

Create the isolated namespace and a machine-readable SHA-256 manifest covering
all tracked Stage D and Track 1–1B artifacts. Record baseline commit, current
authoritative 695-test success, protocol hashes, historical decisions, and the
authoritative SR result hashes.

Files:

- `level4/closure_proofs/sr_derivative/README.md`
- `level4/closure_proofs/sr_derivative/PROGRESS_CAPSULE.md`
- `level4/closure_proofs/sr_derivative/results/historical_manifest.json`
- `level4/closure_proofs/sr_derivative/tests/test_integrity.py`

Verification: recompute every manifest hash, assert Track 1B closed, Track 1A
failed, D2.3 failed, and Stage F partial.

## Task 2 — Complete definition/code audit

Reconstruct the active Stage D SR recursion, threshold serialization,
initialization, update/alarm ordering, direction/tie behavior, stopping time,
reference-error sign, reused `m=1` statistic, mixed update, reset semantics, and
ARL calibration paths line by line. Contrast the obsolete `A=520.3125`
feasibility detector with authoritative Stage D `A=520.886133602749`.

Files:

- `level4/closure_proofs/sr_derivative/DEFINITION_AUDIT.md`
- `level4/closure_proofs/sr_derivative/tests/test_definition.py`

Verification: exact decimal/binary64 checks, raw/log algebra checks, forcing
bound checks, and source-path references.

## Task 3 — Freeze and push the protocol

Write the complete pre-outcome protocol from the approved design, including
estimands, seed keys, calibration roles, paired batch SE, sample sizes, `h`
ladder, acceptance criteria, stop rules, Lean gate, conditional formal boundary,
and non-blocking Arb rule. Hash the exact bytes and commit/push this checkpoint.

Files:

- `level4/closure_proofs/sr_derivative/PROTOCOL.md`
- `level4/closure_proofs/sr_derivative/results/protocol_hash.json`

Verification: protocol hash test, seed absence/disjointness, no outcome files,
and clean worktree after push.

## Task 4 — Write the human theorem and obligation ledger

Prove the parameterization, fixed-path-functional/law-change distinction,
forcing/geometric-tail lemma, stopped likelihood, differentiation, Gaussian
score, reflection symmetry, rho scaling, derivative identity, and numerical
instability corollary boundary. Classify every analytic and formal obligation.

Files:

- `level4/closure_proofs/sr_derivative/THEOREM.md`
- `level4/closure_proofs/sr_derivative/PROOF_OBLIGATIONS.md`
- `level4/closure_proofs/sr_derivative/FAILURE_DIAGNOSES.md`

Verification: claim guards require “symmetric two-chart,” `m=1`, explicit
analytic hypotheses, and no rigorous Gamma wording.

## Task 5 — Implement independent SR primitives test-first

Implement a raw-state score route and a separate log-state conditional-map
route. Neither may import the other or a shared theorem-encoding helper.
Implement path/time-addressable normals only in the log route. Add explicit
alarm enums for plus, minus, simultaneous unequal crossing, and exact tie.

Files:

- `level4/closure_proofs/sr_derivative/src/rebaseguard_sr_derivative/raw_score.py`
- `level4/closure_proofs/sr_derivative/src/rebaseguard_sr_derivative/log_map.py`
- `level4/closure_proofs/sr_derivative/src/rebaseguard_sr_derivative/statistics.py`
- focused tests under `tests/`

Verification: deterministic raw/log paths, reflected paths, injected ties,
natural/log threshold guard, source AST guard, and paired-SE unit tests.

## Task 6 — Implement calibration and frozen runner

Implement the calibration sanity bisection, fixed-threshold ARL comparison,
Route A batches, two Route B replications across the complete ladder, checkpoint
resume, decision logic, and report-ready JSON/CSV summaries.

Files:

- `level4/closure_proofs/sr_derivative/numerics/run_correspondence.py`
- `level4/closure_proofs/sr_derivative/results/checkpoint_*.json`
- result tests added only after outcomes are frozen

Verification before full run: smoke-only structural tests and source guards;
remove smoke artifacts before confirmatory execution.

## Task 7 — Execute the frozen numerical campaign once

Run calibration, Route A, and both Route B replications without adapting any
input. Freeze batch summaries, evaluate every gate, preserve all discrepancies,
and write `CORRESPONDENCE_REPORT.md`. If any primary criterion fails, record
`SR-DERIVATIVE-PARTIAL` or `FAILED` and stop before Lean.

If all pass, record exactly:

`NUMERICAL GATE CLOSED — LEAN AUTHORIZED`.

Commit/push the green numerical checkpoint.

## Task 8 — Implement and audit the Lean spine

Only after authorization, formalize SR step/alarm/finite-path reflection,
terminal signs, oddness/rho algebra, the conditional stopped-score derivative
spine through `IntegralBridge`, and the `Gamma>2` instability implication.

Files:

- `level4/closure_proofs/sr_derivative/lean/SRDerivative.lean`
- `level4/closure_proofs/sr_derivative/lean/AxiomAudit.lean`
- `level4/closure_proofs/sr_derivative/LEAN_CORRESPONDENCE.md`

Verification: pinned Lean compile, theorem-by-theorem `#print axioms`, and
scans for `sorry`, `admit`, or project axioms. Report the result as a
conditional formal spine, not a concrete infinite-process formalization.

Commit/push the Lean checkpoint.

## Task 9 — Attempt the non-blocking Arb upgrade

Recompute the Phase 4C/4D operator architecture at the exact authoritative
runtime threshold. First audit feasibility at the new constant. Continue to a
certificate only through sound outward-rounded coverage, residual, resolvent,
and independent-auditor steps. Do not reuse old-threshold bounds.

Files:

- `level4/closure_proofs/sr_derivative/certificate/STATUS.md`
- optional producer/auditor/certificate files only if soundly completed

Verification: success requires independently replayed strict lower bound above
two and all TCB invariants. Otherwise record `OPEN / NOT CLOSED` with the exact
obstruction; this does not change derivative-theorem closure.

## Task 10 — Reproducer, final verification, and decision

Create a one-command reproducer for historical states, manifest/protocol,
scoped tests, retained numerics, Lean, axioms, and Arb status. Run it from a
clean checkpoint. Run `scripts/verify_level_4.sh`. Produce the two final reports
and exactly one allowed track verdict.

Files:

- `level4/closure_proofs/sr_derivative/reproduce.sh`
- `level4/closure_proofs/sr_derivative/FINAL_REPORT.md`
- `level4/closure_proofs/sr_derivative/results/decision.json`
- `level4/reports/SR_DERIVATIVE_THEOREM_REPORT.md`

Verification: clean worktree, no historical hash drift, all scoped and
authoritative tests green, local/remote commit equality. Commit/push the final
green checkpoint and name—but do not start—the next proof track.
