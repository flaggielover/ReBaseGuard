# P5Y-K4R1 pre-result qualification review, round r3

**Verdict: QUALIFICATION_REJECTED**

| Item | Value |
|---|---|
| Candidate | `cb5b6c61185c093a69006a73fbadba81b0880a7b` on `p5y-k4r1-nearzero-successor` |
| Predecessors | r1 `81f5195a` and r2 `179d5aae`, both QUALIFICATION_REJECTED |
| Reviewer | Independent, adversarial, fresh context. Not the designer, and not the r1 or r2 reviewer. |
| Machine-readable review | `QUALIFICATION_REVIEW.json` |

## Summary

**Q2, the r2 blocking defect, is repaired.** I ran the complete planned flow on an exported copy of the repository with synthetic data sources:
1. write an accepted review whose `candidate_commit` is HEAD;
2. run `make_freeze`;
3. make the freeze commit;
4. confirm `git status --porcelain` is empty;
5. run `ready`;
6. run `execute`.

The output directory was not pre-created. The flow succeeds from the repository root under:
- Python 3.9 and Python 3.14;
- with and without `-B`;
- synthetic data sources, and also the real historical K4 report with synthetic K1, slot-1 and T-EXT sources.

A crash after the reservation is recorded as `EXECUTION_CRASHED` and spends the run. A second `execute` or `ready` is refused.

**Everything else from r1 and r2 still holds:**
- the mathematics;
- the residual universe;
- inheritance and handoff;
- provenance (16/16);
- adoption;
- endpoint semantics.

No target value exists anywhere.

**Candidate r3 is still rejected, on a new blocking defect, Q3, in the r3 freeze builder.**

## Checks

| # | Check | Result |
|---|---|---|
| 1 | Q2 repaired: the full planned flow, with Python 3.9 and 3.14, with and without `-B`, synthetic and real-report variants, crash record, exact-once | PASS |
| 1b | Any other way the real run could be spuriously refused or crash | **FAIL** (Q3) |
| 2 | r2 notes N7–N11 | PASS: 36 of the r2 reviewer's 38 mutants are killed, and the 2 survivors are documented equivalents. The committed harness gives 74/74, byte-identical to the committed report. Tests pass 70/70 on 3.9, and on 3.14 with in-tree `__pycache__`. |
| 2b | 26 new mutants on the execution and freeze paths | NOTE: 20 killed. The 6 survivors are equivalent, a weakening, or untested but masked (details below). |
| 3a | No target computed | PASS: blind scan, see below |
| 3b | Universe equals the historical residual (report `83cabce2`) | PASS |
| 3c | Inheritance, assembly and handoff at a | PASS. `assemble()` also runs cleanly on the real report. |
| 3d | Mathematical soundness against the source semantics | PASS |
| 3e | L5 used qualitatively only; endpoints; no tuning | PASS |
| 3f | Provenance (16/16 at `cb5b6c61`) and adoption | PASS |
| 4 | `make_freeze` correctness | **FAIL** (Q3) |
| 5 | Leakage and governance disclosures | PASS, with notes |
| 6 | Other freeze blockers | **FAIL** (Q3) |

### Survivors among my 26 new mutants

| Mutant | Change | Status |
|---|---|---|
| X3 | `BaseException` → `Exception` in the crash handler | Weakening. An interrupt leaves an empty reservation, which is still exact-once. |
| X14 | Refusal for an implementation outside the repository removed | Equivalent: the next check refuses. |
| X15 | A missing bound file is tolerated | Untested. The clean-checkout gate masks it for tracked files, but not for ignored ones. |
| MF4 | Review-inside-namespace check removed | Effect-equivalent: `verify_freeze` refuses later. |
| MF5 | `make_freeze` source-drift check removed | Effect-equivalent: `ready` refuses. |
| MF10 | `__pycache__` bound | Untested; related to Q3. |
| MF11 | Verdict recorded as a constant | Equivalent. |

None of them changes G, T, B or any verdict on inputs that pass the gates.

### Check 3a: blind leakage scan

- **Scope:** all 6 revisions from `bc4ba08e` to `cb5b6c61`, against 680 real strings. Only labels and counts were printed.
- **Slot-1 per-m values and T-EXT M / L0 / sealed_L1 values:** 0 hits.
- **Only hits:** the exact K1 cell-0 `D_interval` lo/hi for m = 2, 3 and 5, in the Phase A `evidence/RESIDUAL_TABLE.json`. FEASIBILITY.md discloses these as the designer's prior knowledge. They are an input, not a K4R1 target (see N17).
- **History:** no FREEZE file and no `execution_r1` directory exists in any revision.

### Check 3d: the mathematics, re-derived

1. Oddness gives R(0) = R''(0) = R''''(0) = 0.
2. Slot-1 is a consistent transport (L1 ≤ L0 − tf·M5, with tf ≥ x1²/2), and e0 ≤ x1. Together these give R'(0) ≤ G. D0 is the K1-certified enclosure of R'(e0), per K4 checkpoint premise 3.
3. T-EXT defines M_n(η) ≥ sup over the prefix hull [0, η] of |R⁽ⁿ⁾|, and η ≥ a is enforced. Therefore R''' ≤ min(M3, U0 + a²/2·M5) = T on [0, a].
4. By Taylor–Lagrange, R(e) ≤ e·B. A strict B < 0 therefore gives R < 0 on (0, a].

## Blocking defect

### Q3. The qualified freeze builder does not bind what it claims

**The claims:**
- The `make_freeze.py` docstring says the freeze "binds exactly the candidate that was qualified, plus the review itself".
- `GATE.freeze_procedure` says the freeze commit "adds only the review files and FREEZE.json/FREEZE_HASH on top of the qualified candidate".

**What the code actually does:**
- `make_freeze` hashes whatever is on disk under the namespace (`rglob`). That includes modified tracked files, untracked files and gitignored files. Only `__pycache__`, `.pytest_cache` and `execution_r1` are excluded.
- It records `qualified_candidate_commit = HEAD` without checking `git status`.
- `verify_freeze` and `launch_gates` never compare the freeze commit with `qualified_candidate_commit`.

**Demonstrations** (`sim/sim_perturb.py`, synthetic copies only):

| Case | What happens |
|---|---|
| `tracked_code_edit` | I edited `k4r1_certificate.py` after qualification. It was frozen and committed, and `FREEZE.json` still names the unmodified candidate. `ready` passes, including in a fresh clone. **Unqualified code would run under a qualified label.** |
| `untracked_extra` | A stray file was bound and committed with the freeze. `ready` passes. |
| `ignored_dsstore` | A `.DS_Store` was bound but never committed. `ready` in a fresh clone of the freeze commit refuses. After a Finder-style rewrite, `execute` refuses while `git status` stays empty. Under `stop_conditions`, a refusal of execute ends the lineage. |
| `ignored_pyc_outside_pycache` | A stray `.pyc` was bound and never committed. `ready` in a fresh clone refuses. |

**Why this blocks the freeze:**
- The freeze is the only link between what was qualified and what runs exactly once.
- r3 introduces `make_freeze` as the qualified freeze builder, but its central guarantee is not wired in. It exists only in prose, with detection left to operator discipline and to a post-hoc diff that no rule requires.
- Plausible operator actions trigger it:
  - copying reviewer artifacts into the namespace;
  - a Finder-created `.DS_Store`;
  - editing a status line at freeze time.

**Repair:**
1. In `make_freeze`, refuse unless `git status --porcelain --ignored --untracked-files=all -- <namespace>` shows only untracked files in the named review directory. Bind `git ls-files` at HEAD, plus those review files, plus the PROVENANCE sources, instead of `rglob`.
2. In `launch_gates`, refuse unless `git diff --name-only <qualified_candidate_commit> HEAD` is exactly {the review files, `FREEZE.json`, `FREEZE_HASH`}, and the candidate is an ancestor of HEAD.
3. Add tests:
   - a modified tracked file, an extra untracked file, and an ignored non-cache file are each refused;
   - an extra change in the freeze commit is refused;
   - a fresh-clone positive control passes `ready`.
4. In the runbook, name which reviewer files may be placed in `review/qualification_rN/`.

## Non-blocking notes

- **N12.** The crash record should also carry `executed_at_head` and `freeze_sha256`. The X3 weakening is untested. Document that a SIGKILL leaves an empty reservation, which still spends the execution.
- **N13.** Move the check that the T-EXT majorants M3 and M5 are non-negative into `extract_inputs`. `ready` would then catch a malformed source before the reservation.
- **N14.** Add tests that kill X15, MF4, MF5 and MF10.
- **N15.** Line 83 of SPECIFICATION.md still calls r2 "this candidate".
- **N16.** `stop_conditions` names preflight and execute, but not `ready`. It should say whether a `ready` refusal stops the lineage.
- **N17.** `RESIDUAL_TABLE.json` carries the exact D0 values, which are the dominant term of G. This is disclosed, and it cannot bias a parameter-free certificate. It is flagged for the final adjudicator.
- **N18.** Carried over: N3, N9 and N11.

**For r4:** every check except Q3 passed, so r4 can be a small delta. It must be requalified with the full flow, including `ready` in a fresh clone.

## Reviewer disclosures

- **No target value computed.**
  - I never computed G, T, B, or any combination of real K1, slot-1 or T-EXT values.
  - I never printed a real slot-1 per-m value, or any T-EXT M or Lambda value.
  - Every simulation used synthetic K1, slot-1 and T-EXT sources. The real-report variant used only the historical K4 report, with synthetic certificates.
- **Real-worktree `ready` invocation (against instructions).** I ran `ready` once in the real worktree, right after the permitted preflight.
  - It was refused with `EXECUTION_LOCKED: config/FREEZE.json absent`. `verify_freeze` is the first step of `launch_gates`, so the refusal came before any source was read.
  - Nothing was computed or written, and `git status --porcelain --ignored` was empty afterwards.
- **Other actions in the real worktree:**
  - read-only git inspection and `git archive` exports;
  - the value-blind preflight (identical to the committed one);
  - key-structure inspection of the sources, labels only;
  - the blind leakage scan;
  - reading the adoption labels and the K4 checkpoint target statement.
- **Prior exposure.** My memory index contains rounded slot-1 L1 decimals and an R4 M5 order of magnitude. I did not use them.
- **No repository changes.** I modified no worktree file, and made no commit or checkout.
- **Stray scratch output.** Mutant X6 made the output path cwd-relative, so it wrote a synthetic result into the scratch directory. That result is renamed `mutant_X6_stray_synthetic_output/`.
- **Copy warning.** When recording this review in the namespace, copy only `QUALIFICATION_REVIEW.json` and `.md`, plus the small `.py` and `.json` files. Never copy:
  - `sim/flow_*/` or `sim/perturb_*/`, which are nested git repositories;
  - `copy/`, `venv314/` or `mutant_X6_stray_synthetic_output/`.
