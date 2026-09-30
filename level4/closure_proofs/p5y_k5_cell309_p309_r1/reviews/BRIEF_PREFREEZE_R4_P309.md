# Brief: independent pre-freeze review R4 (FC2 code/spec review + FC1/FC3–FC6 + QC design; formal campaign p5y_k5_cell309_p309_r1)

This brief is committed before it is issued (condition C5). **The reviewer must not have produced any of the reviewed
code**, and must not be R1, R2, R3, the incident-independence reviewer or the verifier's author. The owner's rulings 2
require an "independent code/spec review" of the grant-admission mechanism before FC2 re-qualification and before FC1 and
FC3–FC6. This review provides it, together with the pre-freeze review of the rest of the package.

## Authority and boundaries (read first)

* `governance/OWNER_DECISIONS_P309_VERBATIM.md` and `governance/OWNER_RULINGS_2_P309_VERBATIM.md`. No grant exists.
  **NEW Γ309 TARGET EVALUATIONS must stay 0.**
* Package rev. 2b: `RNS/protocol_prep/P309_PROTOCOL.md`, `P309_FORMAL_PACKAGE.md`, `P309_REVIEW_BRIEFS.md`.
* Rev. 2c: `governance/P309_REV2C_AMENDMENTS.md`, which governs where it differs from rev. 2b.
* `fc2/FC2_SPEC_R2.md` and `fc2/FC2_SPEC_R2_ERRATUM_1.md`.
* The U2 documents: `governance/U2_CORRECTED_PROPOSITION_R2.md`, `reviews/REVIEW_U2_CHECK_P309.md`.

## A. FC2 code and spec review (the owner's grant-admission ruling)

Review `code/p309_guard.py` (coordinator) and `verify/srk_verify_indep_scoped.py` (verifier's author), each against the
spec, the erratum and the owner's list:
* fail closed by default;
* no embedded or hard-coded valid production grant;
* no implicit grant; no default admission;
* no production marker creation;
* no real in-band computation;
* no target-derived constants;
* no test-only bypass reachable from the production path;
* the grant bound to the frozen protocol and hash, cell 309, Ew, the verifier identity, the execution identity and host,
  and the marker identity;
* malformed, missing or mismatched grants refused;
* synthetic qualification artifacts cannot authorize production;
* production admission cannot occur until the later explicit owner grant exists.

Assess the power of the tests: `tests/test_p309_guard.py`, `tests/test_verify_scoped.py`, the verifier harness I1, and
the scanner allowance (`code/p309_scan.py`, `config/SCANNER_ALLOWANCE_P309.json`, `tests/test_p309_scan_allowance.py`).
Is the allowance as narrow as the owner's scanner ruling requires? Are the pending-ref NAME extension and the reviewed
exactly-once sites (rev. 2c A10) acceptable? Assess independence of authorship procedurally (spec §9; the variant's
README).

## B. The driver and the qualification machinery

Review these files against protocol rev. 2b plus rev. 2c:
* `code/p309_driver.py`, `code/p309_rehearse.py`, `code/p309_postexec.py`;
* `code/p309_static_check.py`, `code/p309_self_audit.py`, `code/p309_qualify.py`, `code/make_freeze_manifest.py`;
* `tests/test_p309_exactly_once.py`.

Check in particular:
* **Stage 1a:**
  * jobs, rung-major order, the start-threshold budget, the per-job CPU limit, and "never raises" for budget reasons;
  * per-rung serialization, in-process verdicts at N = 8 and max_depth = 24, and the gate;
  * the §2.5 failure mapping.
* **Stage 1b:** the RLR307 rules verbatim, the fallback to S_I1, the independent reconstruction, and the guard injection
  (rev. 2c A4).
* **Stage 2:** the S composition; the pinned `direct()` called unchanged through the shim (A11); the two-part historical
  control (A12); the record binding (A13).
* **Exactly-once:**
  * the marker CAS and the pending ref;
  * the emergency file;
  * seal, materialize and seal-only;
  * the exit codes;
  * check_grant (the A8 chain);
  * pins.
* **The QC suite:** does each of QC01–QC17 and QC-U2, as implemented, test what package §B and rev. 2c say it tests?
  Is anything missing or trivially passable?

## C. Readiness to freeze

List everything that must change before the freeze. Include:
* any unresolved placeholder;
* any mutable scientific decision;
* any post-result choice;
* any rule that is ambiguous in code.

Separate blocking findings from non-blocking notes.

## Allowed and forbidden

* **Allowed:**
  * reading all of FNS and RNS, and git metadata;
  * reading consumer code only through `python3 code/code_skeleton.py py <file>`;
  * running target-free tools and tests: the guard and variant tests, the scanner and its controls, the static check,
    the U2 checker and its controls, the QC11 flows, `p309_driver.py rehearse`, `code/p309_self_audit.py`;
  * sandboxes under the scratchpad (never pushed).
* **Forbidden:**
  * `execute` or `seal-only` in this repository;
  * any evaluation for cells 305–309;
  * any in-band kernel run;
  * reading any value in the target inputs;
  * creating any ref under `refs/p5y-k5-cell309-p309-r1/` anywhere;
  * writing the production grant path anywhere;
  * git writes in this repository;
  * modifying any file except your output file.
* **Ledger** every execution through `code/p309_env.py`, and name your ledger lines.

## Output

`reviews/REVIEW_PREFREEZE_R4_P309.md`, with line 2 exactly one of:
* `FREEZE_APPROVED`, followed by any non-blocking notes and conditions;
* `FREEZE_BLOCKED`, followed by the blocking findings B1…, each with the fix you would accept.
