# Formal delta follow-up review 5 of r2: governance record

**Final disposition: FORMAL_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS**

This record wraps the formal review for r2's governance trail. The review itself is
`REVIEW_FORMAL_DELTA_FOLLOWUP_5.md` (verbatim, sha256 in `REVIEW_FORMAL_DELTA_FOLLOWUP_5.sha256`). It was written by a
fresh independent reviewer that wrote none of the code, corrections, tooling or earlier reviews. Its brief,
`BRIEF_FORMAL_DELTA_REVIEW_FOLLOWUP_5.md`, was committed and pushed before it was issued (`5a0d444a`, sha256
`63282870…95a0`, which the reviewer verified). Everything below quotes or points to the review; the record's author
(the candidate's author) has added only the integrity check of §7 and the erratum of §8.

**Where the record is kept.** The candidate and r2 may not be modified in this task, so the record lives on
`claude/p309-r2-hardening-20261005` under `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/formal_review_followup_5/`.
When the owner incorporates the candidate (C1), these files can be copied into r2's `governance/` as
`BRIEF_R2_DELTA_FOLLOWUP_5.md`, `REVIEW_R2_DELTA_FOLLOWUP_5.md` (+ `.sha256`, exec ledger) by a separate
governance-only commit, after the fast-forward, so the reviewed four paths stay exactly as reviewed.

## 1. Exact commits

| | commit | verified by |
|---|---|---|
| base | r2 `101ef2cb17e5eab2892212178278da45b98004ed` (`origin/claude/p5y-k5-cell309-p309-r2`, unchanged) | reviewer; §7 |
| candidate | `a119e9789e2a1d42b584fff8a2301946a37f1bcb` (`origin/claude/p309-r2-adoption-candidate-20261005`) | reviewer; §7 |
| ancestry | `101ef2cb` is an ancestor of `a119e978` through 2 commits (`93d55063`, `a119e978`). The candidate is **not** an ancestor of r2 (not merged) | reviewer (`git merge-base`); §7 |
| last formally accepted r2 state | follow-up 4 (`R2_DELTA_FOLLOWUP_4_ACCEPTED`). It reviewed `e96ed380`; `38842550` adds the files preserving that review, and `101ef2cb` adds one `CHECKPOINT_PUSHES.jsonl` row | reviewer |

## 2. Exact diff scope

`git diff --name-only 101ef2cb a119e978`: exactly 4 paths, all in `level4/closure_proofs/p5y_k5_cell309_p309_r2/`:

| path | in-scope item |
|---|---|
| `code/p309_qualify.py` | (1) durability / exactly-once hardening H1–H5; (2) T14a `# exclusive` anchor; (5) filesystem pre-launch probe |
| `code/p309_topology_drill.py` | (3) F-DRILL-ORDER (`make_topology` only) |
| `config/SCANNER_ALLOWANCE_P309.json` | (4) the one re-pin (`ref_mutation_functions[20].ast_sha256`) |
| `governance/R2_REPIN_LIST_SUPPLEMENT_5.json` | (4) its additive governance record |

Since `c902fe2f`: 0 paths outside r2's namespace. The r1 tree is `ecd1c359` and research is unchanged since `eb9a9c22`.

## 3. Evidence reviewed

- **Hardening branch at `4b3baebd`:**
  - `r2_candidate_followup/` (S1–S3 follow-up; `EVIDENCE_INDEX.json`, 58/58 sha256 matched);
  - `r2_candidate/` (task 3; manifest 64/64 matched);
  - `R2_FAILURE_MATRIX.json` (7/7 evidence references matched);
  - `R2_QUALIFICATION_HARDENING_REVIEW.md`, `OWNER_DECISIONS_OD_R2.md`.
- **The two earlier independent reviews.** Read as guides only.
- **The reviewer's own recomputation in a fresh clone of `a119e978`:**
  - `code/p309_static_check.py` (T1–T14 PASS);
  - `tests/test_p309_static_controls.py` (22/22, T14a PASS);
  - `tests/test_p309_scan_allowance.py` (19/0);
  - `code/p309_scan_pins.py --list` (all current);
  - AST comparisons;
  - allowance leaf diff;
  - recomputed `make_topology` hashes;
  - re-pin file blob ids at `38842550`, `101ef2cb`, `a119e978`;
  - result-to-bytes bindings (runner sha256, rehearsal commit and tree).
- **Expensive suites not re-run.** The committed evidence was sufficient and consistent.
- **Execution ledger:** `REVIEW_FORMAL_DELTA_FOLLOWUP_5_EXEC_LEDGER.jsonl` (16 rows). The reviewer's helper scripts
  and outputs are under `reviewer/`.

## 4. Review findings: the fourteen required answers

| # | question | answer |
|---|---|---|
| 1 | scientific logic unchanged | **YES** |
| 2 | target logic unchanged | **YES** |
| 3 | gate semantics unchanged except fail-fast / durability / exactly-once | **YES** |
| 4 | runtime hardening justified by reproduced baseline defects | **YES** |
| 5 | filesystem pre-launch probe correctly scoped and fail-closed | **YES** (it does not cover the exclusive mkdir or ledger appendability: SF1, SF2) |
| 6 | F-DRILL-ORDER corrected to the intended freeze sequence | **YES** |
| 7 | `make_topology` re-pin correctly and additively governed | **YES** |
| 8 | T14a and all static controls pass | **YES** |
| 9 | QC11, QC12, QC-D5, host tests and QC15 / A7 pass | **YES** (by content, bound to `a119e978`'s bytes) |
| 10 | crash matrix still discriminates baseline r2 from the candidate | **YES** |
| 11 | all scanner pins current | **YES** |
| 12 | unauthorized namespace changes | **NO** (none) |
| 13 | SF1 | **NON_BLOCKING** |
| 14 | acceptable for incorporation into r2 | **YES** |

Evidence for each answer is in the review, under Q1–Q14.

## 5. Blockers, should-fix items and rulings

- **Blockers: none.**
- **Should-fix:**
  - **SF1 (non-blocking).** Ledger appendability is not probed.
    - An unwritable ledger is discovered only at RUN START, after `attempt_1/` exists.
    - The remedy is either the about-3-line probe extension (under its own delta review) or a recorded
      host-preparation check. Condition C2.
  - **SF2 (non-blocking).**
    - The `fs_probe` docstring overstates its coverage (the exclusive mkdir is not exercised).
    - Two pre-launch faults raise tracebacks instead of formatted refusals: an unreadable `qualification/`, and a
      non-object or timezone-less ledger row. Both are still fail-closed.
- **SF1 ruling: `SF1: NON_BLOCKING`.**
  - The RUN START append is r2's own, accepted by follow-up 4, and the candidate does not add or widen it.
  - Every failure point the candidate adds is probed first.
  - The failure is fail-closed (no target evaluation, no PASS, no retry).
  - Exposure is narrow: the unit may write the whole repository.
  - It must be resolved **before the freeze** (C2).
- **Re-pin ruling: `RE-PIN: ACCEPTED`.**
  - Exactly one allowance leaf changed (1 228 / 1 228 leaves).
  - Both hashes were recomputed: `9b59c12f…` → `8af1bb78…`.
  - The change is intended (F-DRILL-ORDER).
  - It is recorded additively in supplement 5. `R2_REPIN_LIST.json` and supplements 1–4 are byte-identical across
    `38842550`, `101ef2cb` and `a119e978`.

**Conditions:**

| id | class | condition |
|---|---|---|
| C1 | **blocking-before-incorporation** | Incorporate exactly the two reviewed commits, as a fast-forward of r2 `101ef2cb` → `a119e978` (or the same 4-path bytes). No hardening-branch file, tool or test may enter in that step (R18; QC15 A7). The adoption itself is the owner's step under the proposed OD-R2-H, which has no recorded answer; this review gives only the technical acceptance |
| C2 | **before-freeze** | Resolve SF1 (the probe extension under its own delta review, or a recorded host-preparation check). The review does not choose between them |
| C3 | **before-freeze** | Run the worker-tier drill (8d) on the incorporated bytes, so F-DRILL-ORDER is exercised end to end. It regenerates the drill and P8 records that predate the fix |
| C4 | advisory | SF2; report-wording corrections (A1); lenient `utc` skip in H3 (A4); untested probe branches (A5); subprocess-output fsync, the refusal text naming an out-of-r2 validator, the unchanged schema label (A6); moving the hardening's tests into r2 by a later reviewed delta (A7) |
| C5 | advisory | Power-loss durability remains SAFE_BUT_UNPROVEN and depends on the host filesystem (ext4 / xfs) |

## 6. Final disposition and what it permits

**FORMAL_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS**

**May the candidate be incorporated into r2?** Yes, technically. It must be done as the fast-forward described in C1,
with nothing else in the same step. The incorporation itself is the **owner's act** (proposed OD-R2-H). It was not
performed here.

**Non-blocking follow-ups that remain:**
- SF1 (before the freeze, C2);
- SF2;
- the A1 report-wording corrections (see §8);
- A4 (H3's lenient `utc` skip);
- A5 (untested probe branches);
- A6 (subprocess-output fsync, refusal text, schema label);
- A7 (hardening tests outside r2; drill / P8 records predating the fix, regenerated by C3);
- the power-loss caveat (C5).

**Owner decisions that still gate the official qualification.** These are named, not decided;
`OWNER_DECISIONS_OD_R2.md` records no answers.

| decision | subject |
|---|---|
| OD-R2-0 (A)–(C) | the record, carry-over and liabilities |
| OD-R2-0 (D) | authorization of r2's freeze, its single official qualification, the qualification review and the grant-package preparation |
| OD-R2-1 / OD-R2-1b | the production namespace and its four bindings |
| OD-R2-2 | the marker and pending-result names; the D5 extension to r2's two exactly-once sites |
| OD-R2-3 | the qualification host's access path, session and windows (8a audit / 8b verdict) |
| OD-R2-4 | host mutations 1–5 and the unit limits; the cell-308 operator's consent for mutation 4 |
| OD-R2-5 | the interference policy during the single attempt |
| OD-R2-6 | the target-execution host, the QC10 host re-run before any grant, whether the freeze may name a host |
| OD-R2-H (proposed) | adoption of this runtime hardening into r2 |
| F-DRILL-ORDER owner action (proposed) | technically addressed by the candidate; its adoption follows OD-R2-H |

The pre-freeze technical conditions C2 and C3 also apply before the official qualification.

## 7. Integrity check (independent of the reviewer; `integrity/`)

| item | result |
|---|---|
| target evaluations added | **0**: 325 repositories and 16 234 ledger rows scanned (session repository and all scratch replicas), 0 nonzero or unreadable counters (`integrity/INTEGRITY_COUNT.json`); session audit 0 (`integrity/SESSION_AUDIT_SNAPSHOT.json`) |
| grants added | **0**: no grant or result file added or changed by the session; 0 grant files even in TEST sandboxes; 0 protected refs on origin (`integrity/LS_REMOTE.txt`) |
| r5 | unchanged: `f978eeb6b41188eabaf3c6d590c9178d711f1ce6` at r2 `101ef2cb`, the candidate `a119e978` and the hardening head |
| r6 | none, at any of those commits |
| Cell 309 | **OPEN**. The candidate delta touches no grant, authorization, adoption, status, ledger, evidence or qualification path; r5, which carries coverage status, is unchanged |
| r1 | unchanged: `origin/claude/p5y-k5-cell309-p309-r1` = `c902fe2f` |
| r2 | unchanged: `origin/claude/p5y-k5-cell309-p309-r2` = `101ef2cb` |
| main | unchanged: `origin/main` = `1cb45382` |
| candidate merged? | **no**: `a119e978` is not an ancestor of r2 `101ef2cb`; the candidate branch is at `a119e978`, unchanged by this task |
| this task's writes | the brief (`5a0d444a`) and this record, both on the hardening branch, inside the hardening namespace only |

## 8. Erratum (additive; earlier reports are not edited)

The reviewer found (A1) one inaccuracy in `r2_candidate_followup/FINAL_R2_CANDIDATE_REVIEW.md`. Its crash-matrix row
says "every restart refused with bytes unchanged". That does not hold for every case:
- **C01:** after a crash before the first write, a fresh start is correctly **allowed**.
- **S05 / S06:** `unchanged=false` is an artefact of the matrix tool (`QDIR.mkdir(exist_ok=True)` precedes the refusal,
  as in r2); the ledger is unchanged.

The accurate statement is: "no crash point ends CORRUPT; every restart after a started attempt is refused; S01–S08 are
refused". Task 3's validation report already carried these caveats.

---

**Stop.** Nothing was adopted, merged into r2, frozen or qualified, and no grant was issued or consumed. Γ(309) was not
evaluated. Cell 309 remains OPEN.
