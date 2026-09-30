# Postmortem: the official qualification of p5y_k5_cell309_p309_r1 FAILED

**Verdict.** The single qualification attempt (`qualification/attempt_1/`) failed:
* gate **Q11 is FAIL**;
* a host reboot then **interrupted** the run during QC-D5, so the runner never wrote `QC_D5.json` or the summary
  `qualification/P309_QUALIFICATION.json`.

Under A27 ("no retry, no resumption; a failed or interrupted attempt is preserved, and the campaign stops") and the
owner's rule "QUALIFICATION FAILURE", the campaign stops at this formal state. There is:
* no grant;
* no marker;
* no pending ref;
* no qualification review for acceptance;
* no proposed authorization.

**NEW Γ309 TARGET EVALUATIONS = 0.**

The attempt is preserved as the runner left it, in commit `f433d490` (pushed; remote verified at `61952023`).

## 1. The freeze (valid)

| object | commit / hash |
|---|---|
| pre-freeze brief addenda 7, 8 and the placeholder allowlist fix | `ab1dcf26`, `cffef234` |
| **F** (parameters + manifest) | `4c754a73767903a5ad5dddff725f1e173a0a6876` |
| parameters `freeze/P309_FREEZE.json` | sha256 `b9b0f510d2bde2c4ba2147284790120f4bcd824a65ad612df45c22284c77fa5e` |
| manifest `freeze/P309_FREEZE_MANIFEST.json` | sha256 `728fbf10608b1357e14b1a0f6147d9b4bbc3719a94c0d94ef2243c3fe7733c6c` (114 code pins, 10 data pins) |
| **FR** (freeze record only) | `2f66bc566bcc67402d883513474c1f04acbeb108` |

Placeholder check: PASS (0 unallowed hits, 0 nulls). The first run at the freeze failed on six rule quotations in the
generated parameter file; its output is preserved as `evidence/freeze/PLACEHOLDER_CHECK_AT_FREEZE_FAIL_1.json`. That
was fixed before F with two reviewed allowlist entries (brief addendum 8).

## 2. The attempt

Launched 2026-09-30T17:07:03Z, detached (`setsid`), at F. The ledger has exactly one `QUALIFICATION RUN START` line.

| gate | result | wall s |
|---|---|---|
| QC01–QC05 | PASS | 1.0 / 1.3 / 7.3 / 0.2 / 0.6 |
| QC06 | PASS | 831.1 |
| QC07 | PASS | 143.4 |
| QC08 | PASS | 4309.8 |
| QC09 | PASS | 9768.7 |
| QC10 | PASS (48 certificates byte-identical) | 3863.8 |
| **QC11** | **FAIL** | 36.1 |
| QC12 | PASS | 7.1 |
| QC13 | PASS (all its checks, now that the freeze exists) | 0.7 |
| QC14 | PASS | 60.7 |
| QC15 | PASS | 10.7 |
| QC16 | PASS | 653.7 |
| QC17 | PASS | 0.1 |
| QC-U2 | PASS | 1.9 |
| **QC-D5** | **not completed**: the runner was killed by the host reboot | — |

The runner's last write was `QC_U2.json` at 22:35:21Z. The last ledger line is QC-D5's D5-controls start. The host
booted at 22:41:12Z (`/proc/stat` btime).

## 3. Root cause of Q11 (reproduced)

`tests/test_p309_exactly_once.py`, `validate_flows`, flow V01: `D.validate_grant` → `recorded_freeze(sandbox)`
raised `Refusal FREEZE_RECORD: the freeze record was changed after it was made`. The traceback is recorded in
`qualification/attempt_1/QC11.json`.

Why:
* Every QC11 sandbox (`new_sandbox`) is built on this repository's HEAD.
* `build_chain` then adds a synthetic freeze commit and a synthetic freeze-record commit.
* After the real freeze, HEAD's history already contains the real FR, so each sandbox chain has **two** commits
  touching `ledger/FREEZE_RECORD.json`.
* `recorded_freeze` requires exactly one, and correctly refuses.

Post-qualification diagnostic (`scratchpad/postmortem_qc11.py`, ledgered, not qualification evidence):
* the real repository has 1 freeze-record commit (`2f66bc56`);
* a sandbox built by the frozen harness has 2;
* `recorded_freeze` on it gives Refusal FREEZE_RECORD.

**Classification.** A deterministic, target-free, decision-independent defect in the frozen **test harness** that
only shows after a real freeze.
* Every pre-freeze dry run had no freeze record in its history, so none could show it.
* The production path is unaffected: the real history has exactly one freeze-record commit, and `execute`'s
  `check_grant` reads it.
* Any post-freeze run of this frozen harness fails the same way, so the frozen r1 package cannot pass QC11. A retry
  is forbidden by A27, and it would also fail.

**QC-D5.** Its backstop controls (`tests/test_p309_site_backstop.py`) use the same `new_sandbox` and `build_chain`, so
they were probably exposed to the same defect. This was not run. Its D5 mutant controls copy files and do not depend
on git history.

## 4. The reboot (an infrastructure incident, independently disqualifying)

The cloud container restarted at 22:41:12Z. That was the second restart in this session; the first, around 15:19Z,
restarted only the harness and left processes alive. No host control could prevent it.

On its own, the interruption would also end the attempt under A27. It did not cause the Q11 failure, which was
recorded 18 minutes earlier.

## 5. Target integrity (verified after the reboot)

* Production-namespace refs:
  * 0 in this repository;
  * 0 in all 100 QC11 sandboxes;
  * no `refs/p309-test/` in the repository.
* No `authorization/` directory, and no grant file in history.
* Execution ledger: every row has `new_target_evaluations` 0.
* r5 unchanged; no r6.
* Every change since the formal campaign's first commit is inside this namespace. No path mentions 308.

## 6. What a successor would need (for the owner's decision only; nothing applied)

1. **An owner decision.** The frozen governance provides no in-place repair route after a failed qualification.
2. **A new campaign namespace** (for example `…_p309_r2`), not a re-freeze of r1. `recorded_freeze` requires that the
   freeze record is never changed, so r1 cannot be re-frozen in place without changing a reviewed rule.
3. **A harness fix.** QC11 and the backstop controls must build sandboxes whose history holds no real freeze record.
   For example, base the sandbox on the recorded freeze commit F rather than HEAD, or on a base tree without the
   record.
4. **A post-freeze rehearsal.** Before any official attempt, rehearse QC11 and QC-D5 in a scratch clone that carries a
   synthetic freeze and freeze record, so that post-freeze-only defects show up in development.
5. **Host durability.** The attempt takes about 5.5 hours and cannot resume (A27). Choose the host with that in mind.
6. **Reviews.** As before: a delta review of the fix, R4-style re-confirmation, then freeze, qualification and
   review.

## 7. Corrections from the independent postmortem review (additive; the text above stays as first written)

`reviews/REVIEW_QUALIFICATION_POSTMORTEM_P309.md` (sha256 `00531409…`) returned **POSTMORTEM_DISPUTED**. It confirmed
every conclusion above:
* the freeze;
* the single attempt;
* Q11's root cause, including a counterfactual (the same synthetic chain placed on the real F passes);
* the classification;
* the interruption;
* that the governance requires stopping (in-place repair is also impossible: `tests/` is frozen, and A24 allows only
  one freeze record);
* target integrity;
* the successor notes.

It disputed five statements as overstated or unverified. They are corrected here in the reviewer's words:
* **D1 (§3, QC-D5).** Instead of "so they were probably exposed to the same defect", read: they share `new_sandbox`
  and `build_chain`, so their sandboxes also carry two freeze-record commits. However, no backstop control reads the
  freeze record (the sites, `_site_backstop` and the guard's `premarker_check` never call `recorded_freeze`,
  `check_grant` or `freeze_commit`), so this defect gives no reason to expect them to fail. They were never run, and
  their outcome is unknown.
* **D2 (§5).** Instead of "0 in all 100 QC11 sandboxes", read: 0 in all 100 sandbox directories under
  `scratchpad/qc11_sandboxes/`: 57 from the attempt's QC11, 42 from pre-freeze development and 1 from the postmortem
  diagnostic.
* **D3 (§1).** Instead of "two reviewed allowlist entries", read: two allowlist entries, with reasons, whose check
  was assigned to the qualification review (brief addendum 8), which has not taken place. The postmortem review's
  item 1 finds the six hits to be rule statements.
* **D4 (§4).** The first restart (about 15:19Z, "restarted only the harness and left processes alive") and "No host
  control could prevent it" are the coordinator's unverified account; neither is recorded in the repository. The
  coordinator's basis was its own session observations: a restart notice, then `uptime` showing 12 h 57 min and the
  detached dry run still alive.
* **D5 (§6.5).** Instead of "about 5.5 hours", read: about 5.5 hours for QC01–QC-U2 alone; a complete attempt takes
  about 5.7–5.9 hours.

None of D1–D5 changes the verdict, the stop, the target counter or the successor route.

**The reviewer's firewall disclosure.** The reviewer's first pin check hashed every pinned blob. That piped the bytes
of four pinned cell-307 campaign files through sha256:
* `p5y_k5_cell307_rlr_r1/protocol/RLR307_FREEZE.json`;
* `code/rlr307_stage1.py`;
* `code/rlr307_independent.py`;
* `code/rlr307_pinned.py`.

Their content was never displayed; only hash equality was printed. The reviewer then switched to comparing blob IDs
(metadata only). This departs from the brief's "no cell-307 … campaign file beyond git metadata". The reads are the
same class as the freeze-manifest generator's pin hashing of those same files. No cell 305–309 value was read.
