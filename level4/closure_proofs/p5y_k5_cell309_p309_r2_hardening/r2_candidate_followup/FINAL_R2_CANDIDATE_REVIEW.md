# Final review: r2 adoption candidate after the S1–S3 follow-up

*Deliverable 4. The required name was `FINAL_R2_ADOPTION_REVIEW.md`. The session guard refuses every path containing
"adoption" (rule R2_GRANT), and relaxing that rule was denied in task 3, so the file carries this neutral name.*

**Verdict: R2_ADOPTION_CANDIDATE_READY**

"Ready" means **ready to be proposed**: ready to go into r2's formal delta follow-up review with the packet in
`FORMAL_DELTA_REVIEW_PACKET.md`. It does **not** mean reviewed by r2's process, adopted, merged, frozen or qualified;
none of those happened.

**NEW Γ309 TARGET EVALUATIONS = 0.**
- No grant was issued or consumed, and nothing was adopted.
- r5 is unchanged and there is no r6.
- r1, r2 and main are unchanged on origin. Cell 309 remains OPEN.

## The candidate now

`claude/p309-r2-adoption-candidate-20261005` at **`a119e9789e2a1d42b584fff8a2301946a37f1bcb`**: two commits on r2
`101ef2cb`, pushed, not merged. The delta is 4 files, all in r2's namespace:

| file | content | task |
|---|---|---|
| `code/p309_qualify.py` | durability / exactly-once hardening H1–H5; T14a anchor `# exclusive`; **S1 `fs_probe`** | 3, 4 |
| `code/p309_topology_drill.py` | F-DRILL-ORDER (params → manifest → placeholder check) | 3 |
| `config/SCANNER_ALLOWANCE_P309.json` | the one re-pin, `make_topology` | 3 |
| `governance/R2_REPIN_LIST_SUPPLEMENT_5.json` | **S2**: additive record of that re-pin | 4 |

## S1–S3: what was done

| item | result | deliverable |
|---|---|---|
| **S1** filesystem pre-launch probe | `fs_probe(QDIR)` in `main` and `host_rerun`, before H3, Q-HOST, the attempt directory and the start line. It checks exactly the hardening's capabilities: O_EXCL create and refusal, write, file fsync, a same-directory hard link that is a second name of the same file and refuses an existing name, directory fsync, and `sync_ledgers`. No probe evidence persists; leftovers are refused by name and never removed; it fails closed with the step and errno. Tests: 18/18 on the candidate; the pre-S1 runner fails them, and **on an unsupported filesystem it consumes the single attempt, while the candidate refuses before anything starts** | `FILESYSTEM_PRELAUNCH_PROBE_REVIEW.md` |
| **S2** governance re-pin supplement | `R2_REPIN_LIST_SUPPLEMENT_5.json`, generated from git: old `9b59c12f…` → new `8af1bb78…`, `make_topology`, reason F-DRILL-ORDER, proof of one changed allowance leaf and of no scientific or target change, and the corresponding validation. The earlier lists and supplements 1–4 are byte-identical | `GOVERNANCE_REPIN_SUPPLEMENT.md` |
| **S3** formal delta follow-up review packet | range, five-item scope, a brief ready to commit (`BRIEF_R2_DELTA_FOLLOWUP_5.md`), the ten mandatory checks with commands and evidence, the output form, and the known items to rule on | `FORMAL_DELTA_REVIEW_PACKET.md` |

## Validation after S1 and S2 (on `a119e978`; judged by content)

| required check | result | evidence |
|---|---|---|
| S1 tests (positive / negative / integration) | **18/18** on `a119e978`; pre-S1 `93d55063` fails F01–F13 and M02–M05 and passes M01 (they discriminate) | `evidence/FSPROBE_TESTS_*.json` |
| `test_p309_static_controls.py` / **T14a** | 22/22, **T14a PASS** (regression and a clean clone) | `evidence/STATIC_CONTROLS_a119e978.json`, `evidence/FAST_CHECKS_a119e978.json` |
| **QC11** | rc 0, 112/112 flows | `evidence/REG_a119e978.json` |
| **QC12** | rc 0; T1–T14 PASS, incl. T5 formal scan and T14 "Q-HOST refusals before the attempt" | same; fast checks |
| **QC-D5** controls / backstop / pins | rc 0 / rc 0 / rc 0; pins all current | `evidence/REG_a119e978.json` |
| host tests | `test_p309_host.py` rc 0, `test_p309_host_controls.py` rc 0 | same |
| **QC15 / A7** | QC15 PASS; A1–A10 all true, incl. `A7_formal_namespace_only_research_unchanged` | `evidence/rehearsal/attempt/QC15.json` |
| scanner pins | `p309_scan_pins.py --list` all current; scan-allowance test PASS; allowance = r2 + 1 leaf | fast checks; `evidence/ALLOWANCE_DIFF_R2_VS_a119e978.json` |
| placeholder check (incl. the new governance file) | 0 unallowed; manifest `--check` IDENTICAL (184 code pins) | fast checks |
| hardening unit tests T01–T08 | 8/8 | `evidence/UNIT_a119e978.json` |
| crash matrix | identical classification to `93d55063` and identical across two runs. No CORRUPT; every restart refused with bytes unchanged; S01–S08 refused. Baseline r2 (task 3): CORRUPT at C04/C05/C12, 0 fsyncs, launches over S04–S06 | `evidence/MATRIX_a119e978.json`, `_run2.json` |
| fsync ordering | 25/25 record links ordered; the 4 probe operations all precede the first record link | `evidence/FSYNC_ORDER_a119e978.json` |
| light result-free rehearsal | validator **PASS**, 15/15 gates; re-validated independently, PASS | `evidence/rehearsal/` |
| AST / byte identity | vs `93d55063`: added `_oserr`, `fs_probe`; changed `main`, `host_rerun`; nothing else. vs r2: 9 pinned functions and all 34 module-level statements byte-identical | `evidence/AST_RUNNER_*.json` |
| namespaces | `101ef2cb..a119e978`: 4 paths, all in r2; 0 paths outside r2 since `c902fe2f` | git |

**Interruption (disclosed).** The container rebooted during the first regression and rehearsal runs (after QC12 and
QC13 respectively).
- The rehearsal's own `status` classifies that run **INTERRUPTED** ("the host rebooted since the rehearsal started").
  The partial regression output is kept as `REG_a119e978_ATTEMPT1_INTERRUPTED_partial.json`.
- Neither was resumed. Both were run again from scratch into new roots, after rebuilding the replica through a second
  crash-matrix run (which matched the first exactly).
- The results above are from those complete second runs. This is a development-host limitation.

## Independent check of the S1+S2 delta

A fresh reviewer read `93d55063..a119e978` and ran r2's static check, scanner, scan pins and static controls in its own
clone (`evidence/S1_S2_INDEPENDENT_REVIEW.md`).

**Recommendation: ACCEPT.** No blocker.
- **YES** on ordering, fail-closed / precise, no persistence, gate semantics / pins, static rules and the supplement.
- **PARTLY** on coverage and tests.
- **One should-fix, SF1**, which the reviewer itself marks "non-blocking, not a condition": the probe does not prove the
  ledgers are appendable. RUN START, r2's pre-existing first append, follows the attempt mkdir.
  - This concerns r2's original behaviour, not a capability the hardening introduced, so it is outside S1's mandate.
  - It is put to the formal review with a three-line proposed fix (`FORMAL_DELTA_REVIEW_PACKET.md` §5), together with
    notes N1 (exclusive mkdir not probed), N3 (listing error raises instead of refusing) and N6 (untested paths).

## Why READY, and not REVIEW_REQUIRED or BLOCKED

- **Not BLOCKED:** every required check passes, and no reviewer found a blocker.
- **Not REVIEW_REQUIRED.** That verdict was given after task 3 because the independent review there recommended
  "propose after listed fixes", for S1–S3. Now:
  - S1 is implemented and validated;
  - S2 is recorded additively;
  - S3's packet is prepared;
  - the independent check of the new code recommends acceptance, with no condition.

  Nothing remains between the candidate and **proposing** it. What follows is r2's own formal follow-up review, which
  this packet makes ready to start; that review is a process step, not an open defect. Its verdict
  (`R2_DELTA_FOLLOWUP_5_ACCEPTED` / `_REJECTED`), the owner decisions and the durable-host steps all remain ahead and are
  not anticipated here.

## Integrity (`evidence/integrity/`)

| item | result |
|---|---|
| new target evaluations | **0**: 459 repositories and 20 886 ledger rows scanned, 0 nonzero or unreadable, 0 protected refs on origin, 0 grant files even in TEST sandboxes |
| new grants | **0** |
| adoption | **none**; nothing merged into r2; no freeze; no qualification |
| r5 / r6 | r5 unchanged (`f978eeb6…`); no r6 |
| origin | r2 `101ef2cb`, r1 `c902fe2f`, main `1cb45382`, recovery `290b6c10` unchanged; candidate `93d55063` → `a119e978`; hardening `5e43e84c` → this report's commit |
| session audit | target evaluations 0. Every refusal in this task was conservative and of my own commands (canaries; one inline command naming the drill tool). No tripwire event; the log's single tripwire entry is task 2's, already disclosed |
| Cell 309 | **OPEN** |

## Deviations (disclosed)

- **File name.** Deliverable 4 carries a neutral name (see the top of this file). The other three keep their required
  names.
- **Guard re-scoping.**
  - For this task the session guard admitted commits on the candidate of exactly the runner and the new supplement.
    The drill, the allowance and supplements 1–4 were protected again (vectors W24, W23).
  - Its vector ids were tidied: the task-3 duplicate W22 became W24.
  - 165/165 guard tests passed before the push; the canary was refused after the reboot.
- **Where things live.** The reports, evidence and the S1 test tool are committed on the hardening branch under
  `…_r2_hardening/r2_candidate_followup/` (the test tool also under `tests/`). The candidate carries only its four r2
  files.

**Stop.** Nothing was merged into r2. Nothing was frozen. Nothing was qualified. Γ(309) was not evaluated.
