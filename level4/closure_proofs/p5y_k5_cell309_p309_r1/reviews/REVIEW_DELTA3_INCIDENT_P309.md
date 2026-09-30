# Incident-independence review of the THIRD rev. 2c delta (A31–A36; conditions C2, D8, delta-2 E10), formal campaign p5y_k5_cell309_p309_r1
DELTA3_INDEPENDENCE_ACCEPTED

**Standard.** As before, temporal and parametric independence only. The conditions are G1–G9, in the section headed
"Conditions" below. I use G, not F, so they are not confused with R4's F1 and F2. G2–G5 must be met before the freeze.

**Reviewer.** I am the independent incident-independence reviewer. I wrote:
* `reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`;
* `reviews/REVIEW_U2_CHECK_P309.md`;
* `reviews/REVIEW_DELTA_INCIDENT_P309.md`;
* `reviews/REVIEW_DELTA2_INCIDENT_P309.md`, including its follow-up 1.

I did not produce or coordinate the campaign.

**Brief.** `reviews/BRIEF_DELTA3_INCIDENT_P309.md`, committed at 7884122d before it was issued (C5 respected).

**Reviewed state.**
* HEAD is 77991be1. It adds only a checkpoint record to 7884122d.
* The delta is 3cb5d513, plus 147ba3a2 and 7884122d. I diffed it against a873ca83.
* I read committed bytes only. The working tree carries uncommitted ledger lines written by others after 77991be1 (§3).

**Written.** 2026-09-30, 06:53–07:03Z.

**Ledger** (reads and runs):
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/delta3review/D3_LEDGER.jsonl`.

---

## 0. Verdict in brief

**ACCEPTED, on temporal and parametric independence.**

* All six rows come from R4's follow-up findings: F1, F2, NF1 and NF2, with conditions R4F-C1 and R4F-C3. R4 is an
  independent reviewer, and it wrote those findings before this delta.
* The rows concern two things only:
  * which code paths may move a ref;
  * how a grant is admitted.
* None touches:
  * Stage 1a, Stage 1b or Stage 2;
  * a budget, a gate, a decoy, the band or the outcome table;
  * any quantity computed from the kernel.
* **The two new rules are outcome-neutral.**
  * A31, the runtime backstop, only refuses. In a correct run it changes no outcome.
  * A34 admits a genuine grant regardless of its wording, and requires the worktree field. It acts before the marker
    and before any result exists.
  * Neither rule can encode or respond to target information.
* **The one new target-carrying read is validate-grant's.**
  * It reads the target's pinned `cells.json` entry.
  * It is the same read as the proposal tool's, in the same slot: after the freeze, the qualification run and the
    qualification review.
  * At that point every parameter is fixed, so the read is parametrically inert.
  * It is ledgered as carrying 309 numbers.
* **Exposures.** No 305–309 value appears in the ledgers from a873ca83 onwards.
* **Result-chasing component: LOW.**
* **What must happen before the freeze.**
  * The grant must carry this review's conditions verbatim, and R4 follow-up 2's (G2).
  * The liabilities must list the third delta's rule choices, the validate-grant read and the E6 labelling departure
    (G3, G5).
  * The `grant_validation` text must stop claiming "the same checks as execute's" (G4).

---

## 1. Task 1: each row

| row | kind | source | direction for closure | basis target-free? |
|---|---|---|---|---|
| **A31** site backstop | **rule**: a strengthened precondition at the two exactly-once sites | R4F F1(a), R4F-C1 | none on efficacy; fail-closed. In one edge case (the grant expiring between admission and arming) it refuses before the marker instead of arming, so the evaluation is not consumed (§2.1) | yes: R4's code reading of `_assert_execute_context`; no quantity |
| **A32** scanner schema 4, plus the addendum and 147ba3a2 | mechanism: static rejection of code paths | R4F F1(b); the owner's D5 classes | none. It can fail qualification on code **shape** only | yes: R4's mutants M01–M15, and the coordinator's M07 re-run |
| **A33** T7 hardened, new T8 | mechanism: static rejection of code paths | R4F F1(c) | none | yes |
| **A34** authority narrowed; `execution_host.worktree` required; validate-grant; handoff | **rule** (authority, worktree), plus a mechanism (validate-grant) | R4F F2, NF1 | authority and validate-grant: toward a conclusive outcome, but not toward any particular outcome. Worktree: against malformed grants, before the marker | yes: R4's failure scenario for a genuine owner quote with "->", and NF1 |
| **A35** controls (backstop B-controls, M01–M15 and the D5 controls, QC11 A27, A28, V01–V09, the I03 adapter) | controls only | R4F-C1, R4F-C3 | none. The I03 adapter is a TEST-context one, which is stricter | yes. TEST contexts only; validate-grant flows use the TEST cell and write no exposure row |
| **A36** the qualification reviewer checks the ledger and the attempt tree together | controls only | R4F NF2 | none. It makes a hidden second attempt harder | yes |

**Parameters.** The delta changes no parameter.
* **Driver.** The diff touches only:
  * `PLACEHOLDER_MARKS`;
  * `_assert_execute_context` and the new `_site_backstop` and `_require_own_run_nonce`;
  * `_SITE_CODES`;
  * the `check_grant` refactor that factors out `walk_chain`;
  * `grant_content_checks`, `premarker_admission` and `validate_grant`;
  * `main`'s new mode.
* **Other code.** The changes to `p309_qualify.py`, `p309_self_audit.py` and `checkpoint_push_p309.py` rewrite
  subprocess call forms for the scanner. They run the same commands.
* **Unchanged.** The site ASTs are unchanged: `_arm_marker` `1ee764b7…` and `_persist_pending` `13ee3ec3…` in the
  allowance, and `p309_scan_pins.py --list` reports "all current".

**`check_grant` refactor.** The refactored function applies the same set of conditions as before:
* the chain walked from the grant commit's parent to the recorded freeze;
* the chain-commit equality;
* the `_only` checks;
* the review verdict;
* the frozen-directory check.

Only the order of the refusals changed, and all of them come before the marker.

**Duplicate keys in the dry admission.** `grant_content_checks` adds keys that duplicate checks `check_grant` or the
guard already makes: `schema_cell_scope`, `driver_sha256`, `frozen_manifest_sha256`, `host_id` and
`guard_field_parse`. A grant that passes `check_grant` and `premarker_check` passes them too, so the execute outcome is
unchanged.

---

## 2. Task 2: specific attention

### 2.1 A31

**In a correct run, do the conditions already hold at each site?** Yes. I checked each condition against
`run_execute`'s order.

* **Arming.**
  * `_MODE` is set to `execute` first.
  * `premarker_check` is the same function the dry admission has just passed. Between the admission and
    `_arm_marker`, the driver:
    * loads the consumer and the RLR307 code;
    * runs the historical control;
    * writes ledger lines;
    * creates the nonce file in the git directory.

    None of these creates a ref or a commit. `premarker_check` inspects the grant commit, the marker namespace, strict
    descendants, expiry, host and runtime; it does not inspect the worktree.
  * The nonce is created immediately before `_arm_marker`, with this process's pid.

  The only input that can change in between is the clock (check 8). A21 requires `not_after_utc` to be at least
  14 days ahead at admission, so check 8 flips only if the historical control ran for longer than that. In that edge
  case the backstop refuses **before** the marker, where the old path would have armed and then ended
  EXECUTION_INDETERMINATE. That is not a move toward closure.
* **Pending, in execute mode.**
  * The marker was armed moments earlier, at the grant commit, which carries the grant.
  * The nonce is removed only in the `finally` after `after_marker` returns.
  * If the pending backstop nevertheless refused, `after_marker` catches it and writes the emergency file. The
    seal-only path then requires only a marker whose commit carries the grant, and `run_seal_only` already checked
    that. So A31 adds no silent-loss path.
* **Pending, in seal-only mode.** These are exactly the D5 seal-only gate conditions, re-checked. Recovery is not
  narrowed.

**Test evidence.** The development evidence is at the committed driver (sha256 `c9da2b28…`) and QC11 (`3cc7b882…`):
* QC11: 103/103, including the full sandbox flows through both sites;
* backstop controls: 27/27;
* D5 controls: 101/101.

R4 follow-up 2 confirms these; I did not re-run them.

**D5.** A31 narrows the sites to "only with a valid grant, now, from this process". That is the owner's own wording made
operative: "fail-closed CODE CAPABLE of performing those operations after a valid future execution grant". It widens
nothing, and the ratified hashes are unchanged. The report to the owner is accurate, and it is a report, not a request.

**Target information.** None can bear on A31. Its inputs are:
* the grant commit;
* the ref namespace;
* the nonce;
* the mode.

### 2.2 A34

**Direction of the authority change.**
* Before, `authority` was refused if it contained `<`, `>`, "SET BY THE OWNER", "TBD" or "TODO".
* Now only the proposal's own placeholders are refused: `<THE OWNER'S GRANT INSTRUCTION` and `<SET BY THE OWNER`.
* So a grant whose authority quotes the owner with `<`, `>` or `->` is now admitted, and so is one containing "TBD",
  "TODO", or "SET BY THE OWNER" without the `<`.

That is toward a conclusive outcome, in the sense that an execution happens. It does not favour closure over
non-closure.

**Could the target bear on it?** No.
* `authority` is free text, supplied by the owner.
* The test runs before the marker, when no result exists.
* No target-dependent field enters it. `cell_interval` and `drift_hull_Ew` are compared against execute's own
  derivation, not against the authority text.
* The motivation liability (the coordinator's interest in running; MEDIUM-HIGH for the route) is not increased. R4
  identified the trap and proposed exactly this fix. Without it, a genuine grant commit could be irreparable, which the
  owner's no-history-rewrite rule turns into a dead campaign.

**The worktree requirement** is against malformed grants, before the marker.

**validate-grant.** It runs:
* the shared content checks;
* the chain walk;
* the guard's field parser;
* `G.candidate_check`: checks 2, 3 and 5–9, and check 7 in its pre-marker form.

It runs nothing of Stage 1 or 2. `S.cell_blocks` is the geometric outward dyadic hull; I read it in RNS. It creates no
commit and no ref. It writes only ledger lines, and only in the production context.

**Is the `cells.json` read necessary and correctly classified?**
* **Necessary.** Yes, for its purpose. The candidate's `cell_interval` must equal execute's derivation. Without the
  comparison, a mismatch (for example an owner edit) is found only by `execute`, after the grant commit, when it is
  terminal. Reading the proposal's copy instead would be the same exposure class.
* **Correctly classified.** Yes. It is:
  * the same function (`expected_cell` and `cover_interval`, the canonical sum form);
  * the same content as the proposal tool's C4 read;
  * in the same slot, after the qualification review.

  It is ledgered by an exposure row with `carried_309_numbers: true`, "compared, not displayed". The printed output is
  booleans plus fixed reason texts.
* **Parametric effect.** None. By then the freeze, the qualification and its review are all committed.
* **Equality oracle.** Repeated runs can only confirm a value the proposal already contains, and each run leaves an
  exposure row.

**Observations (not conditions).**
* A malformed rational in a candidate field can reach `main`'s exception print, or the guard's reason text, and echo
  that field's own text. That text is the candidate's, already in the file being validated. It is not the
  `cells.json` read, so this is not a new exposure. Printing only the exception type would remove it.
* `expected_cell`'s docstring still says "read in execute only".

### 2.3 A32 and A33

**Confirmed: no rule on the evaluation.** The changes are to:
* the scanner and its pins tool;
* the static check (T7 hardened, T8 added);
* the allowance (schema 4: `process_policy`, `t7_exemptions`, the `ref_mutation_functions` edits);
* tests;
* scanner-driven rewrites of call forms.

Each change either rejects code paths or lists reviewed code by its AST hash. None changes a computed quantity, a
budget, a gate or a decision.

Removing entries from `ref_mutation_functions` and the `q309_guard.py` name exemption only tightens the scan. The
removed entries are those whose only ref-looking call is the read-only form `symbolic-ref -q HEAD`.

Their only route to the outcome is through qualification. A code-shape finding fails QC12 or Q-D5, whatever the target.

---

## 3. Task 3: new exposures (from a873ca83 on)

**Exposure ledger.** There are no new rows from a873ca83 to 77991be1. The last row is the delta-2 E4 retrospective row.

**Execution ledger, 30 rows committed in 3cb5d513 (05:34:46–06:36:07Z).**

| class | rows | what |
|---|---|---|
| GOVERNANCE | 18 | QC12 static checks, D5 controls with M01–M15, backstop controls, scanner allowance controls, the owner step-11 placeholder scan |
| NONTARGET_DECOY | 10 | the coordinator's pre-freeze dry run of the QC runner (research tests, decoy Stage 1a on the declared a2_h5, QC09 decoy Stage 1b on cover cells 297 and 316), and two QC11 runs |
| SYNTHETIC | 2 | guard tests |

Every row has:
* `new_target_evaluations` 0;
* `target_informed_optimisation` 0;
* `target_equivalent_proxies` 0;
* no drift interval meeting the band or its mirror (checked mechanically; no interval printed);
* no cell 305–309 touched.

**Who ran what.**
* There are no R4 rows in this window. R4's follow-up runs were committed before a873ca83, and R4 follow-up 2 had not
  run by 77991be1.
* No production validate-grant has run. The V-flows use the TEST cell and write no exposure row.

**Continuity check, not asked.** The 82 rows committed between 70927a08 and a873ca83 carry the same flags, all clean:
* 45 NONTARGET_DECOY;
* 33 SYNTHETIC;
* 4 GOVERNANCE, including 4 R4-reviewer rows.

**After 77991be1.** Uncommitted lines are in the working tree: the coordinator's "PRE-FREEZE dry run part 2" and one
R4 follow-up 2 row. I saw only their class, script and purpose text. The purpose texts carry declared-decoy drift
intervals, out of band. These lines fall to the next review (G6).

**Answer.** On the ledgers' evidence, nobody saw a 305–309 value in this window.

The QC09 decoy outputs remain latent-proxy class (E5). I did not read them.

**E6 labelling.** The dry-run lines at 05:34–05:40Z, after delta-2 E6, read "qualification:", not "dry run". The QC
runner has no path that sets the "dry run" label (follow-up 1 observed this). They are distinguishable only by date:
they come before any freeze record. That is a departure from E6's letter, recorded in G5.

---

## 4. Task 4: liabilities

**The new item in `code/make_freeze_params.py`** (the R4 follow-up: FREEZE_BLOCKED, `D5_...: NO`, F1, F2, the third
delta, reported to the owner, "re-confirmed (R4F-C3)") is accurate, with one proviso. "Re-confirmed" must be true at the
freeze, with R4 follow-up 2's verdict cited. The build refuses to run without that review file (G7).

**`grant_rules` texts.**
* `premarker_admission`: accurate.
* `site_backstop`: accurate.
* `grant_validation`: **overstated.** It says "the same checks as execute's". validate-grant does **not** run:
  * check 4 (the grant commit);
  * the flags, branch, not-evaluated and result-path checks;
  * `check_bindings` and `check_governance_state`;
  * the consumer-cover agreement;
  * the historical control.

  An owner who reads PASS as a guarantee of admission could make a terminal grant commit on a false belief. The
  proposal tool's own procedure text ("execute's own content checks, chain walk and the guard's checks") is accurate
  (G4).

**Missing from `DISCLOSED_LIABILITIES`** (G3):
* the third delta's rule choices, with direction;
* validate-grant's read of the target's `cells.json` entry;
* the E6 labelling departure (G5);
* "third delta result-chasing component LOW".

**Missing from the grant.**
* `incident_review_conditions_verbatim` carries C, D and E, but not this review's conditions.
* `prefreeze_review_conditions_verbatim` does not carry R4 follow-up 2's conditions.

The freeze parameters already list both reviews (`REVIEWS`), but the proposal tool does not carry them into the grant
(G2).

---

## Conditions

* **G1 (wording).** The third delta is accepted on **temporal and parametric independence only**. C1–C8, D1–D8 and
  E1–E10 continue.
* **G2 (grant; before the freeze).**
  * The grant's `incident_review_conditions_verbatim` also carries this file's conditions, verbatim.
  * `prefreeze_review_conditions_verbatim` also carries `REVIEW_PREFREEZE_R4_FOLLOWUP_2_P309.md`'s conditions,
    verbatim.
* **G3 (liabilities; before the freeze).** Add to `DISCLOSED_LIABILITIES`:
  * **(a) the third-delta rule choices, with direction:**
    * A31: fail-closed, with no effect on efficacy. If the grant expires between admission and arming, it refuses
      before the marker.
    * A34 authority: toward a conclusive outcome. It now admits `<`, `>`, `->`, "TBD" and "TODO" in a quote of the
      owner.
    * A34 worktree: against malformed grants, before the marker.
    * validate-grant: toward a conclusive outcome.
  * **(b)** validate-grant's read of the target's pinned `cells.json` entry. It is taken after the qualification
    review, is of the same class as the proposal tool's C4 read, is compared but not displayed, and gets one exposure
    row per run.
  * **(c)** "third delta result-chasing component LOW".
* **G4 (`grant_validation` text; before the freeze).** Correct `grant_rules.grant_validation` to name what
  validate-grant checks and what only `execute` checks. Only `execute` checks:
  * check 4;
  * the flags, branch, not-evaluated and result-path checks;
  * the bindings;
  * the governance state;
  * the consumer-cover agreement;
  * the historical control.

  Say plainly that a PASS does not guarantee admission. Whether validate-grant should also run the read-only
  bindings and governance-state checks is R4's call; if it is added, it is an implementation change, not a new delta.
* **G5 (E6 labelling; before the freeze).**
  * Record in the formal errata or amendments that E6's "dry run" label clause is met by dating instead of by label:
    every "qualification:" line dated before the freeze record is development.
  * Record this as a departure from E6's letter.
  * After the freeze record, the QC runner is invoked once only, for the single run. QC13 and the qualification review
    enforce this.
* **G6 (later ledger lines).** The next independence or qualification review covers the execution-ledger rows after
  77991be1. That includes the part-2 dry run and R4 follow-up 2's runs.
* **G7 (standing).** At the freeze:
  * the liability item's "re-confirmed (R4F-C3)" is true, and cites R4 follow-up 2's verdict;
  * the two sites keep the owner-ratified AST hashes.
* **G8 (the backstop is binding).** `_assert_execute_context`, `_site_backstop`, `_require_own_run_nonce` and
  `_SITE_CODES` are frozen as R4 follow-up 2 confirms them. Any change after that confirmation is a new delta under C2.
* **G9 (later changes).** Any further rule, parameter or binding change after this review is a new delta under C2.

---

## 5. Reviewer disclosures

**Exposures.** None to any 305–309 value. I saw:
* code and governance text of the formal namespace;
* R4's follow-up review;
* the RNS `cell_blocks` source;
* ledger rows, summarised mechanically by class and flags;
* in uncommitted rows' purpose text, declared-decoy drift intervals, out of band, which I do not reproduce;
* top-level pass counts of the development evidence files, but not the I03 or QC09 decoy outputs.

I opened no cell-307 or cell-308 campaign file. THEOREM_TCT was not opened.

**Executions.**
* Read-only `git` and `grep`.
* `PYTHONDONTWRITEBYTECODE=1 python3 code/p309_scan_pins.py --list`. It is read-only and wrote nothing; the tool writes
  only with `--refresh`.
* Small read-only Python summaries, in scratch, of the ledger rows and the evidence counts.
* An in-memory band-intersection test that printed flags only.

I ran no evaluation, no kernel run and no git write.

**Writes.** This file only.

---
