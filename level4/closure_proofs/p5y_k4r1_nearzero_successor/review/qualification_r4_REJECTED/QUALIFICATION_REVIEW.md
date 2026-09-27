# P5Y-K4R1 pre-result qualification review, round r4

**Verdict: QUALIFICATION_REJECTED**

| Item | Value |
|---|---|
| Candidate | `5d33363cbffc03d9a6f961d67e9d97ba6333becd` on `p5y-k4r1-nearzero-successor` |
| Predecessors | r1 `81f5195a`, r2 `179d5aae`, r3 `cb5b6c61`, all QUALIFICATION_REJECTED |
| Reviewer | Independent and adversarial, in a fresh context. Not the designer, and not the r1, r2 or r3 reviewer. |
| Machine-readable review | `QUALIFICATION_REVIEW.json` (same content, with the evidence) |

## Summary

**Q3 is repaired against every accidental or plausible operator action I tried.**

- `make_freeze` refuses:
  - edited, staged, deleted or untracked files, inside or outside the namespace;
  - ignored files inside the namespace (`.DS_Store`, `__pycache__`, stray `.pyc`, `tmp/`, files hidden through `info/exclude`);
  - extra files in the review directory;
  - a moved HEAD;
  - a review that is not ACCEPTED.
- `ready` and `execute` refuse:
  - post-freeze commits that change files;
  - amended or rebased freeze commits;
  - orphan commits;
  - tampering with FREEZE_HASH or the FREEZE verdict;
  - plain widening of the delta;
  - unbinding of a tracked namespace file.

**The literal flow works.** I ran `freeze_procedure` followed by the `execution` runbook on exported synthetic copies:
- The three real value sources (K1 cell 0, slot-1 and T-EXT) were replaced by the candidate's own synthetic sources before any run.
- The real historical K4 report was kept.
- The flow succeeds under Python 3.9 and 3.14, from a fresh clone, and inside a linked git worktree.

**Other results.**
- Tests pass 78/78 on Python 3.9 and 3.14.
- The harness reproduces 92/92, outcome for outcome.
- Everything from r1 to r3 still holds:
  - mathematics;
  - universe;
  - inheritance;
  - provenance (16/16);
  - adoption;
  - endpoint semantics;
  - leakage.
- No target value was computed.

**Candidate r4 is still rejected, on a new blocking defect, Q4.** The launch-time composition check, which was added to close the second half of Q3, is self-referential.

## Checks

| # | Check | Result |
|---|---|---|
| 1a | Q3: the literal freeze and execution runbook works (3.9 and 3.14, fresh clone, linked worktree, other cwd) | PASS |
| 1b | `make_freeze` attacks: edited, staged, untracked and ignored files; extra review files; moved HEAD; verdicts | PASS (index-flag caveat: N19) |
| 1c | Post-freeze attacks: commits, amend, rebase, orphan, FREEZE tampering | **FAIL** (Q4) |
| 1d | Risk that the real planned flow is spuriously refused or crashes | PASS |
| 2a | Tests 78/78 (3.9 and 3.14); harness 92/92, identical to the committed report | PASS |
| 2b | r3 survivors X3, X15, MF4 and MF5 are killed; MF10 is moot; X14 and MF11 are equivalent | PASS |
| 2c | 29 new mutants of my own | NOTE: 18 killed. The 11 survivors are all masked, equivalent, or untested (V14, V4). |
| 3a | No target computed (blind scan) | PASS |
| 3b | Universe equals the historical residual (report `83cabce2`) | PASS |
| 3c | Inheritance, assembly and handoff at a | PASS |
| 3d | Mathematical soundness against the source semantics | PASS |
| 3e | L5 qualitative only; endpoints; no tunable parameter | PASS |
| 3f | Provenance 16/16 at `5d33363c`; slot-1 and T-EXT ADOPTED | PASS |
| 4 | Stop conditions and runbook | NOTE (N24) |
| 5 | Leakage and governance disclosures | PASS |
| 6 | Other freeze blockers | **FAIL** (Q4) |

## Blocking defect

### Q4. The freeze-composition check at launch is self-referential

**What the gate says.**
- `GATE.execution`: `ready` and `execute` refuse unless `git diff --name-only <candidate> HEAD` equals `allowed_freeze_delta`, "which must be exactly FREEZE.json, FREEZE_HASH and the review files".
- `GATE.freeze_procedure` defines the review files as exactly `QUALIFICATION_REVIEW.json` and `QUALIFICATION_REVIEW.md`, in a new directory `review/qualification_rN/`.

**What `verify_freeze` checks.**
- It requires `set(allowed_freeze_delta) == {FREEZE.json, FREEZE_HASH} | set(review_files)`.
- It reads `review_files` from the same FREEZE.json it is verifying.
- It never constrains `review_files`: not their number, their names, their directory, or their absence at the candidate.
- It never reads the bound review.

The r4 test "a freeze widening its own delta" widens `allowed_freeze_delta` alone. Widening `review_files` at the same time is not tested, and it passes.

**Demonstrations** (synthetic copies only):

| Case | What happens |
|---|---|
| `spec_smuggled` | After `make_freeze`, I edited SPECIFICATION.md and added its path to both `review_files` and `allowed_freeze_delta` with its new hash, then committed. `ready` passes. |
| `code_smuggled` | The same, with `code/k4r1_certificate.py` edited to add a marker field to the result. `git status` is empty and `ready` passes. `execute` returns EXECUTED, and the result carries the marker, so the unqualified code ran. `ready` also passes in a fresh clone of the freeze commit. |

**Why this blocks the freeze.**
- The freeze is the only machine-checked link between the qualified candidate and the code that runs exactly once.
- r4 had to close the second half of Q3: `ready` and `execute` must verify that the freeze commit is the candidate plus the review and FREEZE files.
- As implemented, that verification relies on a premise supplied by the object being verified. It detects internally inconsistent freezes, but not freezes that change the candidate.
- The natural "make it pass" reaction to the refusal `freeze delta / review files malformed` after a post-freeze edit is exactly this edit. The result would then survive both a fresh-clone `ready` and a fresh-clone re-execution.
- The code also falls short of the gate text it would be frozen with, and it cannot be repaired after the freeze.

**Repair** (small, confined to `verify_freeze`):
1. **Pin the review files.** Require `review_files` to be exactly `<ns>/review/<d>/QUALIFICATION_REVIEW.json` and `.md`, for one directory name `d`. Both must be absent at `qualified_candidate_commit` and present at HEAD. `qualification_review` must be the `.json` file.
2. **Read the bound review.** Parse the bound review JSON and require:
   - `verdict == QUALIFICATION_ACCEPTED`;
   - `candidate_commit == qualified_candidate_commit`.
3. **Recommended in the same change:**
   - compare every bound tracked file's hash with its HEAD blob (N19);
   - use `git diff --no-renames` (N22);
   - either refuse ignored entries in the namespace at launch, or run with `python3 -I -B` in both runbooks (N20).
4. **Add tests, each refused:**
   - `review_files` widened with a modified code, spec or gate file, in the same checkout and in a fresh clone;
   - three review files;
   - a wrong file name;
   - a directory outside `review/`;
   - a path already tracked at the candidate;
   - a REJECTED review, or a review naming another candidate.

   Add a positive fresh-clone control and the matching harness mutants.

## Non-blocking notes

All of these require deliberate action, except N23 to N26.

- **N19 (index flags).** With `git update-index --assume-unchanged` or `--skip-worktree`, an edited tracked file does not appear in `git status`.
  - `make_freeze` then binds the edited bytes.
  - `ready` and `execute` run the unqualified code in that checkout (demonstrated).
  - A fresh clone refuses with bound-file drift.
- **N20 (shadow modules).** `code/` is `sys.path[0]`, and `.gitignore` ignores `*.py[cod]`.
  - An ignored sourceless `code/fractions.pyc` shadows the stdlib module. It ran arbitrary code through `ready` and `execute`, with `git status` empty and no committed trace (demonstrated).
  - `make_freeze` imports `json` and `hashlib` before its own ignored check; a garbage `code/json.pyc` crashed it.
  - `python3 -I` removes the script directory from `sys.path` (verified on 3.9 and 3.14).
- **N21.** `verify_freeze` trusts `FREEZE.qualification_verdict`. A hand-written FREEZE that binds a REJECTED review, or a review naming another candidate, passes (demonstrated). This is folded into the Q4 repair.
- **N22.** `git diff --name-only` detects renames. A freeze commit can delete an unbound file outside the namespace, and the deletion is hidden if a new review file is similar to it (demonstrated). Use `--no-renames`.
- **N23.** An empty commit on top of the freeze passes `ready`. The adjudicator should check that `executed_at_head` is the freeze commit, or has an identical tree.
- **N24 (stop conditions).**
  1. **The fresh-clone clause can be read as allowing a second execution.** The clause covers a refusal "caused by local checkout state only (an untracked/ignored stray file ...)". Literally, that includes the EXACT_ONCE refusal of a second `execute`, whose cause is the untracked output of the first run. A fresh clone does execute again (demonstrated on a synthetic copy). `GATE.execution`'s "exactly once" forbids this, but the precedence is not stated. The fix:
     - state that any reservation or result in any checkout ends the lineage;
     - require it to be committed immediately, whatever it contains (N9 carried).
  2. The code never lets an ignored stray file or a "missing ignored cache" cause a `ready` refusal, so those listed causes cannot occur.
  3. "`git status --porcelain` must be empty afterwards" is literally false after `git add`; it holds only after the commit.
  4. "Freeze lineage" is undefined.
- **N25.** Two weakenings among my mutants are untested: V14 (`ready` without the value-blind preflight) and V4 (unbinding a non-mandatory tracked namespace file).
- **N26.** Minor items:
  - The T-EXT scope reads "cells 0-10" in the adjudication, but "1-10" in `GATE.input_scope_note`.
  - Files are read and written without an explicit encoding.
  - Carried over: N3 (T-EXT majorant scope) and N17 (D0 values in `RESIDUAL_TABLE.json`).

## What still holds (evidence in the JSON)

**Mathematics.** I re-derived the certificate:
1. Oddness gives R(0) = R''(0) = R''''(0) = 0.
2. R'(0) <= D0.hi - L1*e0^2/2 = G. This uses the slot-1 bound R''' >= L1 on [0, x1] with e0 <= x1, and D_interval, the K1 enclosure of R'(e0).
3. On [0, a], R''' <= min(M3, U0 + a^2/2*M5) = T. This uses the TEXT_SPEC Conclusion (sup over the prefix hull [0, eta]) and the eta check a <= eta.
4. By Taylor-Lagrange, R(e) <= e*B. So B < 0 gives R < 0 on (0, a].

The formula block and all GATE rule fields are byte-identical from r1 to r4.

**Universe.** It matches report `83cabce2` exactly:
- CUSUM m = 2, cells [0, 1], a = 10187/10^7;
- CUSUM m = 3 and m = 5, cells [0, 1, 2], a = 957/625000;
- no counterexamples.

**Assembly.**
- The covers are contiguous to at least 2.
- In each residual (D,m), the first inherited cell starts exactly at a, and every non-residual cell is DIRECT_R_NEGATIVE.

**Provenance and adoption.** All 16 sources match at the commit, in the worktree and in PROVENANCE. Slot-1 and T-EXT are both ADOPTED, and both adoptions are ancestors of the candidate.

**Real worktree.** It is ready for a future freeze:
- `git status --ignored` is empty;
- no index flags, hooks or attributes are set;
- the preflight is identical to the committed one.

**For r5:** a small delta, confined to `verify_freeze` plus tests and mutants. The requalification must repeat the Q4 attack in the same checkout and in a fresh clone.

## Reviewer disclosures

- **No target value computed.**
  - I never computed G, T, B, or any combination of real K1, slot-1 or T-EXT values.
  - I never printed a real slot-1 per-m value, a T-EXT M value or a Lambda value.
  - All flows used the candidate's synthetic K1, slot-1 and T-EXT sources, written into the scratch copy before any run.
  - I used the real historical K4 report only structurally.
- **Actions in the real worktree:**
  - read-only git commands, plus `git archive` into scratch;
  - the permitted value-blind `preflight` on Python 3.14 and 3.9. Its output is identical to the committed one, and `git status --porcelain --ignored --untracked-files=all` was empty before and after.
  - a blind leakage scan. It loaded the real sources in memory and printed only labels and counts.
  - label-only inspection of the source structure and the adjudications;
  - hashing the 16 sources.
- **Not run in the real worktree:** `ready`, `execute` or `make_freeze`.
- **No repository changes.** I modified no file and made no commit, checkout, switch or reset in `/Users/suzhe/ReBaseGuard-k4r1` or `/Users/suzhe/ReBaseGuard`.
- **Copy warning.** Copy ONLY this file and `QUALIFICATION_REVIEW.json` into the namespace. The scratch directory also holds material that must never be copied:
  - `flows/`, which contains nested git repositories;
  - `base/`, `suite/`, `venv314/` and `evilsrc/`.
