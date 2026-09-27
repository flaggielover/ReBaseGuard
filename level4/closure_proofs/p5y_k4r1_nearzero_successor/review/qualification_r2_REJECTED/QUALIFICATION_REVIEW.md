# P5Y-K4R1 pre-result qualification review, round r2

**Verdict: QUALIFICATION_REJECTED**

| Item | Value |
|---|---|
| Candidate | `179d5aae` on `p5y-k4r1-nearzero-successor` (code `a0f21672`, tests `d3c15ea2`) |
| Predecessor | `81f5195a`, QUALIFICATION_REJECTED |
| Reviewer | Independent, adversarial, fresh context. Neither the designer nor the r1 reviewer. |
| Machine-readable review | `QUALIFICATION_REVIEW.json` |

## Summary

r2 repairs the r1 blocking defect Q1:
- The value-wiring path is now covered by exact-value tests.
- The r1 reviewer's 12 mutants are all killed.
- The committed harness reproduces 51/51 byte-identically.

The mathematics, residual universe, provenance, assembly and endpoint semantics all still hold, and no target value exists anywhere.

The candidate cannot be frozen, however. **Following the prescribed exactly-once execution from a clean checkout, the run crashes after it has computed the target, and no result is recorded.** The new end-to-end harness hides this because it pre-creates the output directory.

## Checks

| # | Check | Result |
|---|---|---|
| 1 | Q1 repaired: value wiring and the execute composition | PASS |
| 1b | 38 new mutants of my own | NOTE: 18 killed, 20 survived. No survivor changes G, T, B or the verdicts on inputs that pass the checks. |
| 2 | N1: freeze bindings, clean checkout, FREEZE.json at HEAD | PASS |
| 2 | N2: exact-once | NOTE: still per output path (carried over) |
| 2 | N3: T-EXT scope | PASS |
| 2 | N4: disclosure | PASS |
| 2 | N5: K1 metadata and slot-1 transport consistency | PASS. Semantics are correct; it is not over-strict, since the real preflight passes. |
| 2 | N6: typed refusals in tests | PASS |
| 3 | No target computed | PASS: blind scan found 0 hits, no FREEZE or execution in history |
| 3 | Universe equals the historical residual (report `83cabce2`) | PASS |
| 3 | Inheritance, assembly and handoff at a | PASS |
| 3 | Mathematical soundness against the source semantics | PASS |
| 3 | Endpoint semantics, no narrowing, no tuning | PASS |
| 3 | Provenance (16/16 at `179d5aae`) and adoption status | PASS |
| 4 | End-to-end harness fidelity to the planned freeze and execute flow | **FAIL** |
| 5 | Leakage | PASS, with a note |
| 6 | Other freeze blockers | **FAIL** (Q2) |

### Check 1: Q1 repair evidence

- **Test suite:** pytest passes 52/52 on an exported copy.
- **Committed harness:** 51/51 mutants killed, and the null mutant passes. My re-run report is byte-identical to `evidence/qualification_r2/MUTATION_REPORT.json`.
- **r1 extra mutants:** all 12 of the r1 reviewer's mutants are killed.
- **Wiring test:** `test_extract_values_are_wired_to_the_right_fields` uses a distinct constant for every field.
- **End-to-end value test:** `test_execute_end_to_end_exact_values` asserts the exact G, T, B and a for each m, through `main()`, on the copy under test.

### Check 1b: my own 38 mutants

Every mutant is a single edit. The full list is in the JSON. The 20 survivors fall into three groups.

**Unsound in principle (5).** The checks are correct by inspection, and the real inputs pass them, so these survivors cannot change the real outcome:
- **W1:** x1 is not required to equal the hull's right end.
- **W2:** e0 ≤ x1 is not checked.
- **W7:** the hull's left end is not required to be 0.
- **A1:** an inherited cover is not required to start at 0.
- **A6:** a non-certified (D, m) outside the universe would be marked PASS.

**Record fidelity (4).** No test asserts these result fields:
- **R1:** `executed_at_head`
- **R2:** `freeze_sha256`
- **R3:** the per-m `inputs` block (a label swap survives)
- **R4:** `T_branch`

**Sound weakenings or equivalents (11):**
- **W3, W4, W11:** these fields are not used by the certificate.
- **W5:** the per-entry detector and the producer identity are still checked.
- **W6:** the record hash binding subsumes this check.
- **W8:** the residual keys are compared with the historical report.
- **W9:** this is a cross-check only.
- **R7:** already documented as equivalent in the harness.
- **F2:** a modified FREEZE.json makes the checkout dirty.
- **F4:** the mandatory-binding list contains the same path.
- **A3:** `check_universe` refuses this case first.
- **A4:** this mutant is sound.

### Check 2: N5 semantics

The source is `p5y_k5_cusum_real_point_executor/code/executor_core.py`, `enclosure_stages`. It defines:
- tf = x1²/2 exactly;
- L1 = L0 − tf·M5 and U1 = U0 + tf·M5;
- [L0, U0] as the R3_mid point enclosure of R'''(0);
- M5 ≥ sup over [0, x1] of |R⁽⁵⁾|.

K4R1 checks the sound one-sided form of this definition. It is not over-strict: the real preflight passes. For soundness it is not under-strict either, because L1 and U0 are used exactly as recorded.

### Check 3: the mathematics, re-derived

1. Oddness gives R(0) = R''(0) = R''''(0) = 0.
2. On [0, e0] ⊂ [0, x1], R''(t) ≥ t·L1. Therefore R'(0) ≤ G = D0.hi − L1·e0²/2, whatever the sign of L1.
3. R'''(e) = R'''(0) + ∫₀ᵉ (e − t) R⁽⁵⁾(t) dt ≤ U0 + a²/2·M5(a), and also R''' ≤ M3(a). Hence R''' ≤ T.
4. By Taylor–Lagrange, R(e) ≤ e·(G + a²/6·max(T, 0)) = e·B. Since e > 0, B < 0 implies R(e) < 0, strictly.

Source semantics:
- D_interval encloses R'(e0), per the K4 checkpoint.
- The T-EXT Conclusion gives M_n(η) ≥ sup over [0, η] of |R⁽ⁿ⁾|, and η ≥ a is enforced.
- L5 is used qualitatively only.

The GATE changes from r1 to r2 are procedural and descriptive only.

## Blocking defect

### Q2. The prescribed exactly-once execution cannot write its result, and crashes after computing the target

**What goes wrong:**
- `evidence/execution_r1/` does not exist at `179d5aae`. Git does not track empty directories, so a clean checkout of any freeze commit cannot contain it unless a file is committed there.
- `main()` neither creates nor checks `out.parent`.
- `out.write_text` runs only after every other step: `verify_freeze`, `git_state`, `load_sources`, `extract_inputs`, the G, T and B computation for every m, and `assemble`.
- The write therefore raises an uncaught `FileNotFoundError`, not a `K4R1Refusal`. The target has been computed in memory, but nothing is recorded or printed, and the exactly-once run is spent. Any retry would be a second execution.

**The GATE command has no working directory it succeeds from.** `GATE.execution` combines a namespace-relative script path (`code/k4r1_certificate.py`) with a repo-relative `--out` (`level4/...`):
- From the repo root, the script is not found.
- From the namespace directory, `--out` resolves to a doubly nested path. The run then crashes after computing, even when the output directory was pre-created.

**Why the tests miss it.** `build_repo` pre-creates `evidence/execution_r1`, and `run_execute` calls `main()` in-process with an absolute path.

**Evidence** (synthetic sources only, in the scratch directory):

| Simulation | Setup | Result |
|---|---|---|
| `sim/sim_flow.py`, dir_absent | clean checkout, output directory absent | `rc=1`, `FileNotFoundError`, no output |
| `sim/sim_flow.py`, dir_precreated | output directory created | `rc=0` |
| `sim/sim_literal.py`, repo root | literal GATE command | `rc=2`, script not found |
| `sim/sim_literal.py`, namespace dir | literal GATE command | `rc=1`, `FileNotFoundError` after compute |

**Repair:**
1. Before any source is read, resolve and validate `--out`: resolve it against REPO, or require it to be absolute under the namespace `evidence/`. Either create its parent or refuse with a typed refusal, and require that the output does not exist.
2. Give one unambiguous command and working directory in `GATE.execution`.
3. Add a CLI subprocess test of the literal command from the prescribed working directory, without pre-creating the output directory.
4. Add a test that a bad output location is refused before `load_sources`.

This needs a new candidate, r3, and a fresh qualification. r2 must not be frozen.

## Non-blocking notes

- **N7. Coverage gaps (check 1b).** Add targeted tests for W1, W2, W7, A1 and A6, and assert the result fields `executed_at_head`, `freeze_sha256`, `inputs` and `T_branch`.
- **N8. The end-to-end tests depend on the host.**
  - On a standard CPython that writes bytecode caches into the source tree, the 3 positive end-to-end tests fail. The cause is an untracked `__pycache__` in the synthetic repo.
  - The negative end-to-end tests then pass for the wrong reason.
  - They pass on this machine only because Xcode's python keeps its bytecode cache outside the tree.
  - **Fix:** in `build_repo`, add a `.gitignore` or set `sys.dont_write_bytecode`, and assert refusal reasons with `pytest.raises(..., match=...)`.
- **N9. Exact-once is still per output path.** There is no ledger (r1 note N2, carried over). The clean-checkout check partly mitigates this.
- **N10. The stop rule makes any untracked file fatal.** Under `stop_conditions`, one untracked file in the frozen checkout refuses execution and ends the lineage. The runbook must require an empty `git status --porcelain` immediately before execution, and must forbid writing reverification output into the checkout. `__pycache__` and `.pytest_cache` are gitignored, and the real worktree is clean at `179d5aae`.
- **N11. HEAD is recorded but not pinned to the freeze commit.** This is acceptable.

## Reviewer disclosures

- **No target value computed.**
  - I never ran `execute` on the real worktree.
  - I never computed G, T, B or any combination of real values.
  - I never printed a real slot-1 per_m value, or a T-EXT rows 1–2 M or Lambda value.
- **Blind leakage scan.** The scan loaded those real values into memory as search strings only. It printed only file names and hit counts, and found 0 hits.
- **Prior exposure.** My system-provided memory contains slot-1 L1 decimals for m = 1, 2, 3 and 5. I did not use them.
- **Real-worktree actions**, all read-only:
  - git inspection;
  - reading schemas and keys;
  - the value-blind preflight, which passed and was identical to the committed one (the checkout was still clean afterwards);
  - reading the slot-1 adjudication's `adoption_status` (ADOPTED) and its aggregate label and route.
- **No repository changes.** I modified no file in any worktree. All tests, mutants and simulations ran on `git archive` exports and synthetic repositories in the scratch directory.
