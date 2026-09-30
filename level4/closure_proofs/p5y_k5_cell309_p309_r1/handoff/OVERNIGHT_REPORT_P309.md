# Overnight report (final): cell 309, formal campaign p5y_k5_cell309_p309_r1 (2026-09-30)

## 1. Final state

**QUALIFICATION FAILED. The campaign has stopped at its failure boundary** (A27, and the owner's rule "QUALIFICATION
FAILURE"). **READY_FOR_OWNER_GRANT_DECISION was NOT reached.**

| item | state |
|---|---|
| Freeze F | exists: `4c754a73767903a5ad5dddff725f1e173a0a6876` |
| Freeze record FR | exists: `2f66bc566bcc67402d883513474c1f04acbeb108` (F's only child) |
| Official qualification (the single attempt) | **FAILED**: gate Q11 FAIL; interrupted by a host reboot during QC-D5; no summary |
| Qualification review for acceptance | not held (nothing to accept) |
| Independent postmortem review | POSTMORTEM_DISPUTED on wording only; every conclusion confirmed; corrections applied (§5) |
| Proposed authorization | **not prepared**; not permitted after a failed qualification |

## 2. QC09 and dry run 5 (development, before the freeze)

* QC09: PASS (9886.5 s); both declared cover cells completed, rc 0, independent checks all equal.
* QC13: EXPECTED_PRE_FREEZE_PENDING. Only its four freeze-dependent checks failed; its other eight passed.
* Dry run 5 overall:
  * PASS: QC01–QC10, QC12, QC14–QC17 and QC-U2;
  * QC11 (112/112) and QC-D5 (D5 166/166, backstop 27/27, pins current) were run separately at the same code;
  * FAIL: none.
* Pre-freeze integrity audit: 25/25 at `f9a53745`. It covered:
  * the 16 R4 AST hashes and the A38 backstop pins;
  * the allowance unchanged since `fd7da22f`;
  * the scan PASS with exactly two sites;
  * the T10 protections;
  * the refs, the grant, the ledger and the namespace.

## 3. The freeze

* Final brief addenda before F: addendum 7 `ab1dcf26`; the placeholder fix and addendum 8 `cffef234`.
* Parameters `freeze/P309_FREEZE.json`: sha256 `b9b0f510d2bde2c4ba2147284790120f4bcd824a65ad612df45c22284c77fa5e`.
* Manifest `freeze/P309_FREEZE_MANIFEST.json`: sha256 `728fbf10608b1357e14b1a0f6147d9b4bbc3719a94c0d94ef2243c3fe7733c6c`,
  with 114 code pins and 10 data pins.
* Placeholder check:
  * the first run at the freeze failed on six rule quotations in the generated parameter file (preserved);
  * two allowlist entries were added before F;
  * the re-run passed (0 unallowed, 0 nulls).
* F and FR were pushed, and the remote was verified at `c950054a` (FR's checkpoint record).

## 4. The qualification

* Launched 2026-09-30T17:07:03Z, detached, at F. One `QUALIFICATION RUN START` line.
* PASS: QC01–QC10, QC12–QC17 and QC-U2.
  * QC08 4309.8 s, QC09 9768.7 s, QC10 3863.8 s.
  * QC10's certificates are byte-identical.
  * QC13 passed all its checks.
* **QC11 FAIL** (36.1 s). A deterministic defect in the frozen test harness that shows only after a real freeze:
  * QC11's sandboxes are built on HEAD, which after the freeze already carries the real freeze record;
  * `recorded_freeze` therefore sees two freeze-record commits and refuses;
  * this was reproduced in a TEST-only diagnostic sandbox.
  * The production path is unaffected.
  * Every post-freeze run of this frozen harness would fail the same way.
* **Interrupted.** The host rebooted at 22:41:12Z while QC-D5 ran; the runner's last write was at 22:35:21Z. So no
  `QC_D5.json` and no summary exist, and none was fabricated.
* **No Q.** The attempt was preserved as the runner left it in `f433d490` (pushed).

## 5. Reviews

* **Postmortem review** (a fresh independent reviewer): POSTMORTEM_DISPUTED on five overstated or unverified
  statements, D1–D5. It confirmed every conclusion:
  * the freeze;
  * one attempt;
  * Q11's root cause;
  * that stopping is required and in-place repair is impossible;
  * target integrity.

  D1–D5 are applied in the report's section 7.
* **Follow-up 1:** CORRECTIONS_DISPUTED on F1 (the restart count) and F2 (the counterfactual's scope). Both are
  applied in section 8.
* **Follow-up 2:** CORRECTIONS_CONFIRMED. Section 8 applies F1 and F2 exactly, and nothing before it changed. The
  follow-up-2 brief was issued by message only. It is committed verbatim afterwards, disclosing the departure
  from C5.
* **Firewall disclosure by the reviewer:** hash-only reads of four pinned cell-307 files. No content was displayed,
  and no cell 305–309 value was read.

## 6. Authorization

None was prepared, proposed, issued or consumed. No `authorization/` directory exists, and no grant appears in
history.

## 7. Target integrity

* NEW Γ309 TARGET EVALUATIONS = **0**. The execution ledger has 1421 rows, all with 0 target evaluations and 0
  proxies.
* Production marker: absent.
* Pending-result ref: absent.
* Campaign namespace refs: 0 locally, 0 on the remote, and 0 in all 100 scratch sandboxes.
* Grant: none.

## 8. Governance

* r5 unchanged (blob `f978eeb6…`); no r6.
* Cell 309 status: unchanged, still open. The formal campaign r1 has stopped after a failed qualification.
* Cell 308: untouched. No commit since the formal campaign began touches a path outside this namespace or a path
  naming 308.

## 9. Commits and refs (this night, in order)

`ab1dcf26` addendum 7 · `f9a53745` record · `cffef234` placeholder fix + addendum 8 · **`4c754a73` F** · **`2f66bc56`
FR** · `c950054a` record · `f433d490` failed attempt preserved · `61952023` record · `2b149412` postmortem + brief ·
`91a5747f` record · `c7e0ff51` postmortem review + section 7 · `a491a453` record · `a5f5cb09` follow-up brief ·
`9fefd218` record · `5f76c1bf` follow-up + section 8 · `988199b7` record · `0a515d4c` draft of this report · `6fafd568` record · the final commit (follow-up 2, its brief
and this final report) and its record.

Every push was made with `code/checkpoint_push_p309.py`, and each one verified remote == local.

## 10. Host

* A cloud Linux container; there is no AC power, sleep, macOS update or thermal state to manage.
* Disk: 25 GB free throughout.
* Memory: about 15 GB available throughout; no OOM event.
* Restarts:
  * at about 15:19Z the harness restarted and the detached dry run survived (the coordinator's session observation,
    not recorded in the repository; postmortem D4);
  * **at 22:41:12Z the host rebooted, which killed the official runner during QC-D5.**
  * The 22:41Z reboot is at least the third restart in this session (postmortem follow-up, F1).

## 11. What the owner needs to decide next

The r1 campaign cannot be requalified or repaired in place: A27 forbids it, `tests/` is frozen, and A24 allows only
one freeze record. The smallest decision needed:

**Decide whether to open a successor formal campaign for cell 309** (a new namespace, for example `…_p309_r2`). It
would carry:
* the harness fix: QC11 and backstop sandboxes whose history holds no real freeze record;
* a post-freeze rehearsal of QC11 and QC-D5 before any official attempt;
* host-durability planning for an attempt of about 5.7–5.9 hours that cannot resume;
* the usual delta review, R4-style re-confirmation, freeze, single qualification and independent qualification
  review.

Alternatively, leave cell 309 open. Nothing here authorizes, or needs, a target evaluation.
