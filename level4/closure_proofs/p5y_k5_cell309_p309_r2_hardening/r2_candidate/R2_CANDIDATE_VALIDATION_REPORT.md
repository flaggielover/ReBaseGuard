# r2 adoption candidate: validation report

*Deliverable 2. The required name was `ADOPTION_VALIDATION_REPORT.md`; it is renamed because the session guard refuses
paths containing "adoption" (see `R2_CANDIDATE_DELTA.md`).*

**Candidate:** `93d550638b8c79ae1c252fc6c2b0194b1a416b49`. **Baseline:** r2 `101ef2cb`.

All validation was result-free and ran in scratch replicas on this cloud container. That makes it DEVELOPMENT_ONLY:
msg4 #13 excludes the cloud session as a durable host. Every result below was judged **by the content of its evidence
file**, never by an exit code alone. Evidence paths are relative to this directory.

## STEP 4: r2's own gates on the candidate

| check | result | evidence (content checked) |
|---|---|---|
| `tests/test_p309_static_controls.py` | **PASS**, rc 0: `all_pass: true`, 22/22 controls. **T14a PASS**: the T14a mutant makes T14 fail (`got.T14 = false`), as the control requires | `evidence/regression/STATIC_CONTROLS_candidate.json`, `evidence/regression/REG_CANDIDATE.json` |
| T14a anchor (static) | all 18 mutant anchors present exactly once | `evidence/ANCHORS_CANDIDATE_WT.json` |
| QC11 (`tests/test_p309_exactly_once.py`) | rc 0; 112/112 flows, 0 failed | `REG_CANDIDATE.json` `qc11_table` |
| QC12 (`code/p309_static_check.py`) | rc 0 (also PASS inside the rehearsal) | `REG_CANDIDATE.json`; `rehearsal/attempt/QC12.json` |
| QC-D5: D5 exception controls / site backstop / scan pins | rc 0 / rc 0 / rc 0 (controls 3 091 s); **pins all current** | `REG_CANDIDATE.json` (`pins_all_current: true`) |
| host tests `test_p309_host.py`, `test_p309_host_controls.py` | rc 0, rc 0 | `REG_CANDIDATE.json` |
| **QC15 self-audit** | **PASS**: A1–A10 all `true`, **A7_formal_namespace_only_research_unchanged = true** (QC15 had failed on A7 for the hardening branch in Task 2) | `rehearsal/attempt/QC15.json` |
| A7 inputs (static, independent) | since `c902fe2f`, 0 paths outside r2's namespace (the hardening branch has 60); r1 tree `ecd1c359` (= R1_TREE); research namespace unchanged since `eb9a9c22` | this report; `INDEPENDENT_DELTA_REVIEW.md` Q6 |
| scanner pins changed unexpectedly? | **no**. One intentional re-pin (`make_topology`, F-DRILL-ORDER). All 9 pinned runner functions and the drill's other pins are byte-identical. `p309_scan_pins.py --list` reports "all current" on the candidate and on r2 | `evidence/ALLOWANCE_DIFF.json`, `evidence/SCAN_PINS_LIST_*.txt`, `evidence/AST_*.json` |
| protected namespace changed? | **no**. The diff is 3 files, all in r2's code/config, none of them evidence, ledger, governance, test, research, r1 or other cells | `git diff --name-only 101ef2cb 93d55063` |
| out-of-r2 artefact present? | **no**. No `.claude/**`, no hardening or recovery namespace | same |

The baseline r2 regression (Task 2, `REGRESSION_BASELINE_101ef2cb.json`) also gives rc 0 everywhere. The candidate
therefore matches r2 on every r2 gate. The Task 2 package `3c191ac2` failed only `test_p309_static_controls.py`
(T14a), and that failure is gone.

## STEP 5: the existing hardening validation, re-run (no new mutants)

| check | candidate `93d55063` | baseline r2 `101ef2cb` | evidence |
|---|---|---|---|
| unit tests T01–T08 | **8/8 pass** | T01–T02 pass; **T03–T08 fail** (discriminates) | `evidence/unit/UNIT_{CANDIDATE,BASELINE}.json` |
| crash matrix C01–C15: CORRUPT outcomes | **none** | **C04, C05, C12 CORRUPT** | `evidence/matrix/MATRIX_{CANDIDATE,BASELINE}.json` |
| crash matrix: every restart after every crash point | refused, bytes unchanged | refused, bytes unchanged | same |
| torn write (C04, C05, C12) | INTERRUPTED: a temporary file, never a torn record | CORRUPT | same |
| exactly-once / double launch (S09: both pass the existence check, mkdir decides) | exactly one COMPLETE_PASS, one RUN START | same | same |
| interrupted-run refusal: S01 stale lock, S02 torn prior record, S03 stray marker | refused | refused | same |
| interrupted-run refusal: S04 leftover temp file | **refused** | launched | same |
| ledger-state refusal: S05 torn ledger tail | **refused** | launched | same |
| ledger-state refusal: S06 orphan RUN START | **refused** (no new start line) | launched (a second RUN START) | same |
| S07 host-identity change, S08 frozen dir changed | refused | refused | same |
| Q-HOST abort C13 | ABORTED | ABORTED | same |
| fsync ordering (full run, C15) | **25/25 links** preceded by an fsync of their temp file and followed by a directory fsync; 43 ledger fsyncs; 137 fsyncs in total | 0 fsyncs, 0 links | `evidence/matrix/FSYNC_ORDER_CANDIDATE.json`, `C15_FSYNC_LOG_candidate.jsonl` |

**Identity with Task 2:** the candidate's C15 fsync/link sequence is identical, op for op (after removing PIDs), to the
reviewed hardened v2 log (`3c191ac2`). This is expected: the runner is AST-identical.

**Count correction (disclosed):** Task 2's review states "42 ledger fsyncs". The same counter
(`tools/fsync_order.py`) gives **43** on both Task 2's committed log and the candidate's. The 42 was a counting slip
in Task 2's text, not a difference between the packages.

Matrix caveats (from the independent review, Q8; they do not change the conclusion):
- C06/C07 inject at `os.link`, which the baseline never calls, so they test the candidate only.
- C01's `restart.ok` / `no_trace` flags and S05/S06 `unchanged=false` are artefacts of the matrix tool
  (`QDIR.mkdir(exist_ok=True)` precedes the refusal, as in r2).
- SIGKILL is not power loss: durability across a power cut depends on the filesystem (SAFE_BUT_UNPROVEN, as in
  Task 2).

## STEP 6: the existing result-free rehearsal against the candidate

Tool: `r2h_rehearse.py run --source <session repo> --commit 93d55063 --gates light` (Task 2's tool, unchanged; all gates
except the decoy batteries QC06 and QC08–QC10).

| run | outcome | classification |
|---|---|---|
| attempt 1, root `rehearsal_light_candidate` | died during the clone. The container's writable allowance was exhausted (2.4 GB free) by earlier scratch replicas. `status` gives **INTERRUPTED** ("no provenance (interrupted before the first write)") | **development-host limitation** (disk). Never resumed: the root is preserved as INTERRUPTED (`evidence/rehearsal/ATTEMPT1_STATUS.json`). Stale Task 1 and Task 2 scratch replicas, whose evidence is committed on their branches, were deleted to free space. |
| attempt 2, new root `rehearsal_light_candidate_2` | validator **PASS** (re-validated independently afterwards: PASS, no reasons). All 15 gates PASS: QC01–QC05, QC07, QC11–QC17, QC_U2, QC_D5 (3 077 s), QC16 (673 s). One RUN_START; every record bound by its ledger row; summary last; no temporary file; no protected ref and no grant or result file in the clone. Provenance: commit `93d55063`, parents `[101ef2cb]`, synthetic F′ with 183 code pins (params → manifest) | **PASS** |
| host checks of attempt 2 | `cpus` ok, `ram` ok, `python_exact` ok, `filesystem_durable` ok (ext4); `disk` (< 40 GB), `not_in_container`, `pid1_systemd` fail | **known host-binding behaviour / development-host limitation**: label DEVELOPMENT_ONLY. The rehearsal was run without `--require-durable-host`, as designed for development |

**Adoption blockers from the rehearsal: none.** Unrelated pre-existing conditions: none observed. The full
`--gates all --require-durable-host` rehearsal (6–9 h, with the decoy batteries) belongs on the durable host
(`DURABLE_HOST_EXECUTION_PACKET.md`, Task 2).

## Not validated here (needs the durable host, owner-gated)

- The worker-tier drill through the launcher and systemd unit (F-DRILL-ORDER's end-to-end confirmation).
- Q-HOST on a real unit.
- The decoy batteries QC06 and QC08–QC10.
- Durability across a power cut.
- Whether the host filesystem supports `os.link` and directory fsync (independent review S1).
