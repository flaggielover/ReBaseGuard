# Incident-independence review of the SECOND rev. 2c delta (A20–A30, FE-9; condition C2 / R4-C1), formal campaign p5y_k5_cell309_p309_r1
DELTA2_INDEPENDENCE_ACCEPTED

**Standard.** Temporal and parametric independence only, as before. The conditions are in the section headed
"Conditions" below (E1–E10). E2, E3, E4, E8 and E9 must be met before the freeze.

**Reviewer.** I am the independent incident-independence reviewer, the author of
`reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`, `reviews/REVIEW_U2_CHECK_P309.md` and
`reviews/REVIEW_DELTA_INCIDENT_P309.md`. I did not produce or coordinate the campaign.

**Brief.** `reviews/BRIEF_DELTA2_INCIDENT_P309.md`, committed at 4ac99bc1 before issue (C5 respected).

**Reviewed state.**
* HEAD was 77900ac2 when I started. The committed state I rely on is 7c6fa27b.
* Two commits landed during the review: 44b10d63 (FE-10 plus the qualification-review brief) and a6e4108d (ledger
  lines). I cover FE-10 in §1.
* I read committed bytes only (`git show HEAD:…`); the working tree carries others' uncommitted ledger edits.

**Written.** 2026-09-30, 05:00–05:15Z.

**Ledger** (reads and runs):
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/delta2review/DELTA2_LEDGER.jsonl`.
* I ran nothing beyond read-only `git` and `grep`, one `code/code_skeleton.py json` key-types read of a cell-307 file
  (§3), and small read-only Python summaries of the ledgers.
* No evaluation, no kernel run and no git write. The only file written is this one.

---

## 0. Verdict in brief

* **Temporal.** Every row A20–A30, FE-9 and FE-10 postdates the last recorded coordinator exposure to a 305–309 value,
  which is 309R1-02 at 13:06:42Z on 09-29. No 309 Stage-1 quantity exists:
  * 336 execution-ledger lines;
  * 0 target evaluations, 0 proxies, 0 target-informed optimisations;
  * no cell touched and no band drift.

  The sources are the independent pre-freeze review R4 (B1–B8, NB-notes), the owner's D5 decision, and implementation
  defects found in development.
* **Parametric.**
  * No Stage-1 scientific parameter changes.
  * The one new numeric rule is A21's 14-day minimum grant horizon (R4's own example value). The hard CPU limit is set
    at "limit + 5 s" (A22).
  * Neither can discriminate between outcomes: they act before the marker, or on a job's end.
* **Direction:**
  * **Toward a conclusive outcome:** A21 and A25. Both remove routes by which a correct run ends INDETERMINATE or
    silently loses SRK.
  * **Against closure in a failure case:** A22, A26, A28.
  * **Against an invalid closure:** A20.
  * **Neutral or stricter:** A23, A24, A27, A29, A30.

  None is tuned to a target number. **Result-chasing component of this delta: LOW.** The route's overall rating is
  unchanged: MEDIUM-HIGH, upper end.
* **Findings needing conditions** (none shows target dependence):
  * a residual SIGXCPU lever in A22 (E2);
  * FE-9's pre-freeze in-memory parse of the target interval (E3);
  * an unledgered QC11 read of a cell-307 campaign **result** file, outside the formal quarantine's enumerated reads
    (E4);
  * the latent-proxy status of the near-band Stage-1b decoy (E5).

---

## 1. Task 1: each row

| row | class | direction | source | basis target-free? | finding |
|---|---|---|---|---|---|
| **A20** cell from `cells.json` | M (enforces protocol §2.1) | **against an invalid closure** | R4 B1 | yes | Independent. `expected_cell` reads the pinned `cells.json` for the target in `execute` only, after `check_grant`, and cross-checks it against the consumer's cover (`run_execute`). The grant never supplies C |
| **A21** 14-day horizon plus dry admission | **R (new) plus M** | toward a conclusive outcome | R4 B3, NB8 | yes | Independent (§2) |
| **A22** job-end mapping | **R (a precision of §2.5 / §3)** | **against closure in a failure case** | R4 B4; owner STAGE-1a FAILURE SEMANTICS | yes | Independent, with one residual lever (§2; E2) |
| **A23** grant window | **R (A8 amended)** | neutral | R4 B5 | yes | Independent (§2; E6) |
| **A24** freeze record | **R (A8)** | neutral (stricter) | R4 B7(c) | yes | Independent |
| A25 top-level `stage1a`; postexec flags | M (fix) | toward a conclusive outcome: without it every run that could close through SRK would be EXECUTION_INDETERMINATE post-seal (R4 B2) | R4 B2 | yes | Independent |
| A26 verdict reasons sealed | M | neutral; against closure in a failure case (an uncovered reason raises) | R4 B6 | yes | Independent |
| **A27** no retry | **R (new)** | neutral to outcome; stricter (a failed or interrupted single attempt stops the campaign) | R4 B8; owner "do not … weaken a failed qualification gate" | yes | Independent (§2; E6) |
| A28 hooks, control exception, nonce, flags | M | against closure in a failure case: a historical-control exception is now a sealed CONTROL_FAILED (STOP), not a retryable exit 2 | R4 NB4–NB6, NB14 | yes | Independent |
| A29 D5 implementation | M | neutral | owner D5 | yes | Independent (§2; E8) |
| A30 text | — | none | R4 NB7, NB10 | yes | Independent |
| FE-9 endpoint form | M (fix) | none | implementation | yes | Correctly classified as to exposure. The read was not necessary for 305–309 (§2; E3) |
| FE-10 QC03 pins (after the brief) | binding / Q | none | a pre-freeze dry run | yes | Independent. See the "Pre-freeze dry runs" note below |

**Pre-freeze dry runs (FE-10).** The four added pins are overnight D_309 test dependencies (`d309_core`, `d309_rso`,
`ov_fixtures`, `ov_quarantine`); the sanitizer's INDEX classes `d309_core` as carrying no tail value.
* A pre-freeze dry run of the QC items is development, not qualification.
* But its ledger lines say "qualification: research test …", which will confuse A27's single-attempt audit (E6).

---

## 2. Task 2: specific attention

**A21: the 14-day horizon and the pre-marker dry admission.**
* **The horizon cannot favour an outcome.**
  * It is checked once, before arming, against the owner's `not_after_utc`.
  * It depends on no computed quantity, and it gates only whether the marker is armed.
  * Its only effect is to lower the chance that the guard's and the variant's per-call expiry check (FC2 check 8)
    fires mid-run, since wall time is unbounded (A6). A mid-run expiry would turn a slow run into EXECUTION_INDETERMINATE
    (guard refusal inside a producer) or into a silent SRK loss (variant REFUSE, then fallback).
  * That effect is toward a conclusive outcome, symmetric between CLOSED and NOT_CLOSED.
  * Review mode does not check expiry (FC2_SPEC_R2 §3, "replaces 4 and 7–9"), so post-seal re-verification is not
    exposed to the horizon.
  * Residual risk: a run longer than the horizon. At the CPU bounds (< 96 CPU-h for Stage 1a and < 30 CPU-h for
    Stage 1b, on 4 workers) that needs a very slow host. Disclose it (E7).
* **The dry admission is outcome-neutral.**
  * `premarker_admission` compares grant fields against pinned values, the live host, the runtime and the refs, and
    calls the guard's `premarker_check`.
  * It computes no kernel, certificate or consumer quantity.
  * It runs before the historical control, and the only target-cell computation before the marker is still that
    control. The control reproduces C2's **committed** Γ, so a pre-marker refusal and retry teaches nothing new.

**A22: the job-end mapping.**
* **Direction: against closure in a failure case.** It turns a runtime kill below the limit from a fallback (which can
  still close through the remaining terms) into EXECUTION_INDETERMINATE.
* **Basis:** the owner's explicit rule, "Do not convert a post-marker software exception into a fallback merely to
  preserve efficacy", and R4 B4. Target-free.
* **Residual lever.** `run_jobs` classifies **any** SIGXCPU as a budget termination (`p309_driver.py:754`). A manual
  `kill -XCPU <pid>` below the limit ends the child (no handler; `RLIMIT_CORE` = 0) and becomes a fallback. That is the
  same post-marker operator lever R4 B4 set out to remove.
* QC11 S15 covers only SIGKILL.
* A kill can only remove certificates. Γ̄ is a max of mins over admitted rungs, and the Stage-1b ladder takes the best
  over certified rungs. So the lever cannot favour closure. It is still a result-steering lever, and A22's own text
  ("only the kernel's CPU-limit enforcement") excludes it (E2).

**A23: the grant window.**
* Its direction is neutral: window commits may touch only the three ledgers, `handoff/` and
  `qualification/host_rerun/`, and a later check refuses any change to a frozen directory.
* **Two gaps.**
  * **The host re-run evidence is committed after the qualification review Rv,** so no independent reviewer sees it
    before the grant.
  * **The host re-run is exclusive only per host id** (`os.mkdir(<host id>)`). An uncommitted failed attempt could be
    deleted and re-run. The same holds for `qualification/attempt_1/` before it is committed.

  A27's "no retry" is therefore enforced by process and by the ledger, not by code (E6).

**A24: the freeze record.** It is stricter: `recorded_freeze` requires F's record-only child, never changed, and F to
remain the last frozen-directory change. Neutral and independent.

**A27: no retry.** It is stricter and neutral to outcome. It removes the post-result choice R4 B8 found. Two notes:
* An **environmental** interruption, such as the disk exhaustion seen in development (ledger 03:42:08Z), now ends the
  campaign. That is conservative and consistent with the owner's rule.
* See E6 for the ledger-based audit.

**A20 and FE-9's structural read.**
* **A20** closes the invalid-closure route R4 found: a same-width, shifted `cell_interval`.
* **What FE-9's check did.** It parsed the endpoints of all 326 CUSUM cover cells in memory, including 305–309, and
  compared the helper with the canonical loader. Only a boolean and the raw entries of cells 0 and 1 were displayed.
  * **Correctly ledgered:** exposure row 23, with `carried_309_numeric_values: false`. That is accurate for display.
  * **Not an "evaluation" in the quarantine's sense.** It reads a cell definition; no new-route quantity is formed.
* **Not necessary for 305–309.**
  * The representation was established by cells 0/1.
  * Equality on the non-quarantined cells would have shown the two readers agree.
  * `run_execute` re-checks the target's interval against the canonical cover at run time.
* **It departs from the letter of my C4** ("the cells.json read of the 309 interval … happens only after the freeze").
  It also contradicts `make_freeze_params.py`'s `post_grant_derivations.cell_interval` text ("read after the freeze").
  No information resulted: the value was not displayed. LOW. Record it and correct the text (E3).

**A29: the D5 implementation.**
* **It does not widen production-ref authority.**
  * `seal-only` creates the pending ref only through the ratified `_persist_pending`.
  * It does so only for emergency evidence bound to a marker that names a grant commit.

  This is the grant-gated recovery mechanism the owner ratified.
* The other additions are either narrowings or match the owner's reject-list:
  * **Narrowings consistent with "grant-gated, fail-closed":** the three seal-only guards; HEAD attached under
    `refs/heads/`.
  * **Scanner schema 3 implements the owner's reject-list:** value-tracked aliases, token definitions, and
    unique-name sites.
* `ref_mutation_functions` lists **non-production** ref movers: the owner-authorized checkpoint push, the seal's
  branch CAS, read-only `symbolic-ref` forms, and QC11 sandbox helpers. D5 does not decide these either way, and they
  are admissible only as "reviewed" paths.
* **Two points need care (E8):**
  * `p309_scan_pins.py` may refresh their AST hashes before the freeze. The frozen hashes must be exactly those R4-C2
    reviews.
  * The allowance's `authority` text still calls the pending-ref NAME "a proposed extension … for independent review",
    although the owner has ratified it.

---

## 3. Task 3: new exposures (from e53a678c on)

* **Exposure ledger.** Exactly one new row, 23 (FE-9; see §2). R4's reads were masked skeletons of the RLR307 helpers,
  C1B modules and the consumption adapter or loader; R4 §8 states that no 305–309 value was seen.
* **Execution ledger.** Lines 170–336, plus the lines of 44b10d63 and a6e4108d. Classes: NONTARGET_DECOY, SYNTHETIC,
  GOVERNANCE.
  * No cell touched, no band drift, counters 0.
  * The ledgered drifts are decoy and test-band drifts only. They include cover cell 297's interval, which lies
    immediately below the band's lower edge (the maximum ledgered |e| is below 6/5).
* **Unledgered read (new finding).** QC11 integration flow I03 (`tests/test_p309_exactly_once.py:684-686`, added in
  35f3cf34 and run in the dev runs at 04:29Z, 04:36Z and 05:00Z) reads
  `p5y_k5_cell307_rlr_r1/qualification/RLR307_DECOY_STAGE1_297.json`. That is a **cell-307 campaign results file**.
  * By a key-types-only read (`code_skeleton.py json`, ledgered), it holds RLR307's Stage-1 decoy record for cover
    cell 297: per-block and per-rung operator constants (C_T, τ, Λ_lo, D_lo, …) and supplies, and a `latent_proxy` field.
  * These are **latent-proxy-class** validation-drift values (overnight QUARANTINE_AMENDMENT_2 R2.1–R2.4) at a drift
    adjacent to the band.
  * The formal quarantine's enumerated necessary reads allow "RLR307 Stage-1 **code** (not evidence or results)".
  * There is no exposure-ledger row for this read.
  * Nothing was displayed, and it carries no 305–309 value. It is a quarantine-process deviation and a latent-proxy
    handling point, not a target exposure (E4, E5).
* **Conclusion.** No 305–309 value was seen by the coordinator, R4, the verifier author or any tool, on the record.

---

## 4. Task 4: liabilities

The frozen `DISCLOSED_LIABILITIES` (`code/make_freeze_params.py`) now carry:
* R4 FREEZE_BLOCKED (B1–B8) and its resolution;
* FE-9;
* owner D5;
* the first delta's items.

These are necessary but not sufficient. Add (E9):
* **(a) the second-delta rule choices with direction:**
  * A20: against an invalid closure;
  * A21: toward a conclusive outcome, with a 14-day minimum horizon, and a residual mid-run expiry for runs longer
    than the horizon;
  * A22: against closure in a failure case;
  * A25: toward a conclusive outcome;
  * A26 and A28: against closure in a failure case;
  * A27: no retry, so a failed or interrupted single attempt ends the campaign;
  * A23 and A24: neutral.
* **(b)** FE-9's pre-freeze in-memory parse of the target interval, with no value displayed, as a departure from C4's
  letter.
* **(c)** the QC11 I03 read of the cell-307 campaign's decoy record, outside the enumerated reads and unledgered (or
  its removal, E4).
* **(d)** the latent-proxy status of the Stage-1b decoy outputs (E5).
* **(e)** "second delta result-chasing component LOW".

The R4 item says "re-reviewed (R4 follow-up)". That must be true at the freeze, with R4-C2's verdict cited.

---

## Conditions

* **E1 (wording).** The second delta is accepted on **temporal and parametric independence only**. C1–C8 and D1–D8
  continue.
* **E2 (A22 residual lever; before the freeze).** Classify a job end as TERMINATED_JOB_LIMIT only if the kernel's
  enforcement is evidenced by CPU time: SIGXCPU **or** SIGKILL, each with `cpu ≥ job_limit_s` (a documented tolerance
  may apply for SIGXCPU at the soft limit). A SIGXCPU below the limit is JOB_EXCEPTION. Add a QC11 flow in which a stub
  child sends itself SIGXCPU at low CPU, and the stage must raise. This is a precision within A22's stated intent, not a
  new rule. R4-C2 confirms it.
* **E3 (FE-9 / C4; before the freeze).**
  * Record FE-9's pre-freeze in-memory parse of the 305–309 intervals (no value displayed) as a departure from C4's
    letter, in the formal errata.
  * Correct `post_grant_derivations.cell_interval`'s "read after the freeze" statement accordingly.
  * Any further structural check of `cells.json` filters out the 305–309 entries before parsing, unless strictly
    necessary.
* **E4 (the cell-307 results file in QC11 I03; before the freeze).** Either:
  * replace the read of `p5y_k5_cell307_rlr_r1/qualification/RLR307_DECOY_STAGE1_297.json` with a manufactured
    Stage-1b record (the S12-fixture pattern); **or**
  * add that exact file to the formal quarantine's enumerated necessary reads, with its content class (decoy
    cover-cell-297 RLR record; latent-proxy class; never displayed).

  In either case, add an exposure-ledger row, retrospectively, for the development runs that already read it.
* **E5 (latent proxies of the Stage-1b decoys).**
  * QC09's and I03's outputs for cover cells 297 and 316 are latent-proxy class. They are labelled as such, never
    displayed in summaries or handoffs, and never juxtaposed with or interpolated toward any tail-cell quantity
    (R2.1–R2.4).
  * If cell 316 lies above the band, the two Stage-1b decoys bracket the band, which the research decoy rule avoided
    for SRK. That fact is disclosed. It does not change A15 (D6).
* **E6 (single-attempt audit).**
  * QC13 and the qualification review verify, from the committed execution ledger anchored at the freeze record, that
    exactly one qualification run and one host re-run per named host occurred after the freeze.
  * Any extra, deleted or unrecorded attempt means STOP.
  * Pre-freeze dry-run lines must be distinguishable. They are before the freeze record, and future ones are labelled
    "dry run", not "qualification".
  * The host re-run evidence (committed in the grant window after Rv) is cited in the grant by commit, and must be a
    PASS. A failed host re-run blocks the grant; a different host needs the owner's naming.
* **E7 (A21 disclosure).**
  * The 14-day minimum is stated in the grant preparation text: `post_grant_derivations.not_after_utc`.
  * The owner is told that a run longer than the horizon turns the per-call expiry into EXECUTION_INDETERMINATE or a
    silent SRK loss.
* **E8 (A29; before the freeze).**
  * The frozen AST hashes of the listed non-production ref movers are exactly those R4-C2 reviews; no refresh after
    that review.
  * The allowance's `authority` text cites `governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md`.
* **E9 (liabilities; before the freeze).** Add §4 items (a)–(e) to `DISCLOSED_LIABILITIES`, and carry E1–E10 verbatim
  among the conditions in the grant.
* **E10 (later changes).** Any further rule, parameter or binding change after this review, including errata after
  FE-10, is a new delta under C2.

---

## 5. Reviewer disclosures

**Exposures.** None to any 305–309 value. I saw:
* key names and types of a cell-307 decoy record (masked JSON skeleton);
* decoy and test-band drift intervals, including cover cell 297's, which I do not reproduce;
* band literals;
* code of the formal namespace;
* R4's review text.

**Executions.** Read-only `git` and `grep`; one `code_skeleton.py json`; ledger summaries in scratch.

**Writes.** This file only. No git write.
