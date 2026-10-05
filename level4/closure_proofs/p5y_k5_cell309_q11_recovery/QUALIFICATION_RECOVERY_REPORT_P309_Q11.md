# P309 Cell 309 — Q11 / QC-D5 result-free qualification recovery report

**Verdict: QUALIFICATION_RECOVERY_BLOCKED**

**NEW Γ309 TARGET EVALUATIONS = 0** (and 0 for cells 306–308). No grant was issued, consumed, simulated or
modified. Nothing was adopted and no status changed. r5 is unchanged (blob `f978eeb6`) and there is no r6.

Machine-readable twin: `QUALIFICATION_RECOVERY_AUDIT_P309_Q11.json`. Every evidence path and hash is listed in
`EVIDENCE_MANIFEST.json`.

## 1. Actual starting refs (fetched 2026-10-04; the brief's refs were not assumed authoritative)

| ref | commit |
|---|---|
| `origin/main` | `1cb45382` |
| `origin/claude/p5y-k5-cell309-p309-r1` (the brief's "latest known") | `c902fe2f` (= `8ca441c5` CORRECTIONS_CONFIRMED + one ledger commit) |
| **`origin/claude/p5y-k5-cell309-p309-r2`** (not in the brief) | **`101ef2cb`**: r1 + 45 commits, last 2026-10-02 |
| `origin/claude/rebaseguard-k5-cell-309-w0jv8m` | `eb9a9c22` (research r1) |
| protected refs on origin (`refs/p5y-k5-cell30*`, `refs/p309-cell309*`, `refs/rlr-tail/*`) | none |

**The brief's known state is stale.** r2 is the successor campaign that r1's postmortem called for. It already
implements and has reviewed (four follow-up reviews) the QC11 harness repair. It has run 10 cloud-tier drills,
one of which was INTERRUPTED by a container restart during QC_D5. It stands at HOST_SUITABILITY_PENDING, awaiting
owner decisions OD-R2-0..6. r2 touches only its own namespace; r1's namespace tree `ecd1c359` is identical on r1
and r2.

Nothing was merged, rebased or reset. The isolated branch `claude/p309-q11-recovery-20261005` was created at
`c902fe2f`, as the brief directs, and r2 was used read-only (`git show`, scratch clones).

Host: Ubuntu 24.04.4, CPython 3.11.15, git 2.43.0, 4 vCPU, 15 GB, stdlib-only code. `host_id` is `33010a62…`; r1's
freeze host was `a6744a79…`. Full Phase 0 record: `evidence/phase0/PHASE0_RECON.json` (entry points, read and write
sets, target-evaluator reachability, write-set and command-set forecast).

## 2. Root cause of the r1 failure

r1's postmortem is confirmed independently, with one correction to the brief's framing: **Q11 did not fail because
of the reboot.** Two separate events stopped the attempt.

| question asked by the brief | finding | evidence |
|---|---|---|
| purely an infrastructure interruption? | **No for Q11, yes for QC-D5.** QC11 FAILed 18 min before the 22:41:12Z reboot, deterministically. The reboot then killed QC-D5. | r1 `attempt_1/QC11.json`; Run A / A2 reproduce QC11 FAIL on this host |
| identity / provenance mismatch? | **Yes: this is the Q11 root cause.** The QC11 sandbox builder bases every sandbox on `HEAD`. After the real freeze, HEAD's history already holds the real freeze-record commit, so each sandbox chain holds **two** record commits and `recorded_freeze` correctly refuses (`FREEZE_RECORD: the freeze record was changed after it was made`, flow V01). It is a defect of the frozen **test harness**; the production path is unaffected. | A2 / A `QC11.json` traceback; mutant M1 shows the count is 2 where 1 is expected |
| incomplete restart / resume protocol? | **No.** The runner has no resume by design (A27, R4 B8) and fails closed: every restart over an existing attempt is refused byte-for-byte. | crash matrix R02–R13 |
| stale lock / stale checkpoint? | **No.** There is no lock or checkpoint. The attempt directory is a permanent tombstone, and an empty one blocks restarts (fail closed). | R11 |
| non-atomic evidence write? | **Not the cause.** r1's last record before the reboot (`QC_U2.json`) is complete and valid. But the protocol **is** non-atomic (O_EXCL, no fsync, no temp + link): an interruption can leave an empty or torn record (R04, R05, R09; classified CORRUPT, fail closed). | validator on r1 attempt_1; R04/R05/R09 |
| duplicate execution after resume? | **No.** Exactly one RUN START. Two racing starters produce exactly one attempt (the loser fails on `os.mkdir`). | R14, validator `run_start_lines = 1` |
| another protocol defect? | **Two findings, neither causal:** (a) no ledger-integrity check before RUN START (R15); (b) r1's frozen manifest and parameters are **bound to the freeze host**, so the runner refuses on any other host (R17) and QC13 fails there (Run C). | R15, R17, Run C |

The independent validator classifies r1's committed `attempt_1` from content alone as **INTERRUPTED**: 18
consistent records, **QC11 FAIL**, QC_D5 and the summary missing, one RUN START, and ledger activity (QC-D5's
start line) after the last record (`evidence/r1_attempt_1/R1_ATTEMPT_1_VALIDATION.json`). Crash case R08 replays
exactly this state and receives exactly this classification.

**The never-run QC-D5 is now resolved:** under r1's frozen harness on this host, QC-D5 **PASSES** (Run A2: D5
controls, backstop controls, and scan pins all current). Had the host not rebooted, Q11 would still have been
r1's only failing gate.

## 3. The repair, and why r1 cannot carry it

The repair is r2's reviewed P6 change: the sandbox base becomes the recorded freeze F after a freeze, plus a
postcondition on the record count and a check of each FREEZE_RECORD refusal's detail. It was **not
re-implemented**. `code/make_repaired_harness.py` derives it mechanically from r2's committed blob and refuses
unless every changed line belongs to the reviewed repair. The diff is −8/+64 lines
(`repair/QC11_HARNESS_REPAIR.diff`).

| run (scratch replica of r1 at launch HEAD `c950054a`) | QC11 | QC-D5 |
|---|---|---|
| A2, frozen harness | FAIL (r1's defect reproduced) | **PASS** |
| A3, repaired harness | **PASS, 112/112 flows** | FAIL: r1's frozen scanner pins the harness **by AST hash** (9 pins STALE; P0, P0b and C07b flag the new harness's exempted constructs) |
| M1, base back to HEAD, postcondition kept | FAIL, loudly: `2 freeze-record commits … expected 1` | — |
| M2, base HEAD, no postcondition | FAIL: the r1 refusal | — |
| M3, A24/A25 details swapped | FAIL: exactly A24 and A25 | — |
| M4, manifest always from the working tree | PASS: an **equivalent mutant** in this replica (working-tree manifest = F's); reported as a survivor | — |

The repair is therefore **necessary but not sufficient alone**. It must travel with a reviewed re-pin of the
scanner allowances. r2 does exactly that (`R2_REPIN_LIST*`). This confirms the r1 postmortem: in-place repair of
r1 is impossible, and r2 is the vehicle.

**r2 post-freeze, independently:** in a scratch r2 replica, r2's **unmodified** generators produced a synthetic
freeze F′ `0bf31684` with record-only child FR′ `d5a1787b`. The topology was witnessed by my own git queries: one
record commit at HEAD, its parent is F′, and none in F′'s history.
- `evidence/r2_postfreeze/`: QC11 **112/112**, QC12 PASS, QC-D5 **166/166** D5 controls, **27/27** backstop
  controls, scan pins **all current**. **PASS.**
- `evidence/r2_items/`: r2's own `items_table()` / `run_item()` gave QC01–QC05, QC07, QC11–QC17 and QC-U2, all
  **PASS**. QC-D5 in that run was cut by the container restart (covered by the run above).
- r2's heavy decoy gates share r1's bytes: all 72 non-namespace pins are byte-identical, and the driver differs
  only in the production runtime binding and a seal string. Their r1 rehearsal is below.

## 4. Result-free validation of the remaining gates (scratch replicas; never the official runner)

| gate(s) | run | result |
|---|---|---|
| QC01–QC09 | Run B (r1 bytes, repaired harness) | **all PASS**. Interrupted at QC10 by the container restart (boot `ba1fb020` → `973d41ad`, 23:09:14Z); the atomic protocol left every record consistent (validator: INTERRUPTED, no CORRUPT) |
| QC12, QC14–QC17, QC-U2 | Run C (r1) | **PASS** |
| QC13 | Run C (r1) | FAIL only on `freeze_params_regenerate_identically`, because the parameters name the freeze host (rev. 2c A14). By design; all 11 other checks pass. r2's QC13 passes all checks. |
| **QC10** | Run D + independent validator | **48 certificates byte-identical across four runs on two hosts**: r1 QC08 and QC10 (freeze host, 09-30), Run B QC08 (this host, boot `ba1fb020`), Run D (this host, after the reboot). 0 self-hash mismatches (re-hashed independently), set sha256 `a044291a…`, all CERTIFIED / ACCEPT, gate admitted = certificates, 12/12 jobs; verdict and gate structures identical; frozen driver `8cc96f34…` |

Every verdict comes from `code/attempt_validator.py`, which imports no campaign code and judges content, hashes,
order and provenance, never an exit status. Its own defects found during the session are recorded in the commit
history: the QC11 flow-table schema, the summary-pass logic, and per-path keying.

## 5. Restart, resume and exactly-once (synthetic gates only)

`tests/crash_matrix.py` gives **36/36**. It drives the **real** r1 runner `main()` in a scratch replica with every
gate stubbed. One precondition is replaced by a test double: the host-bound manifest check, shown unstubbed in
R17. It also drives the new atomic protocol through the orchestrator's own functions.
- **r1 protocol:** interruption before the first write (a fresh start is allowed, since nothing was recorded),
  before RUN START, during a gate, on an empty or torn record, after the record before the next ledger update,
  after the ledger update, during QC-D5 (r1's case), and on a torn summary. Also stale lock, pre-existing partial
  artifact, stray summary, a duplicated start race, torn ledger tail, mismatched commit, and mismatched host. In
  every case the validator gives the right classification, and three restart requests (one plus two concurrent)
  are each refused with **byte-identical** attempt and ledger hashes.
- **New protocol** (temp file O_EXCL → fsync → link → dir fsync → ledger row): no interruption point yields a torn
  record (N02–N09 give INTERRUPTED, never CORRUPT); only a power-loss-model torn ledger row gives CORRUPT (N07).
  Mutants (N13–N20) are all detected: mixed provenance, foreign freeze, duplicate row, row without record, a
  second RUN_START, a post-summary edit, a summary claiming a phantom gate, and a nonzero target counter.
- **Observed for real:** Run A was killed by a tool time limit, and Runs B and r2-items by a container restart.
  Each was classified INTERRUPTED and **never resumed**; new runs started into new directories.

## 6. Session safety controls (Phase 1)

These are enforced by hooks, not by CLAUDE.md:
- `.claude/hooks/p309_pretooluse_guard.py` (fail closed on any internal error). It refuses: target-evaluation
  modes and tools; grant, adoption, status, r5, r6 and exactly-once-ref mutation; force pushes and any push but
  `git push -u origin claude/p309-q11-recovery-20261005`; `reset --hard`; destructive clean; rebase, merge,
  filter and amend; AWS, Vultr, SSH and other remote compute; and writes outside the declared write-set. It also
  gates commits by branch and by staged paths.
- `.claude/hooks/p309_posttooluse_tripwire.py` re-checks the repository after every call.
- `.claude/hooks/p309_session_audit.py` runs at SessionEnd (and as `--snapshot`).
- **149/149** negative, positive and fixture tests (`evidence/guard/GUARD_TESTS.json`). The guard was proven live
  in this session by a canary and by a real refused `git push --force`; the canary was re-checked after the
  restart. It refused a legitimate push once (a parser false positive on `2>&1`), was fixed, and gained regression
  vectors.
- **Known limits:** the guard sees command text, not what an allowed program does internally (mitigated by the
  tripwire, the in-process self-guards of the rehearsal tools, and the frozen code's own quarantine guards).
  Project-level hooks can be edited by the session itself (tamper-evident via the hook hashes in every audit
  line); full enforcement would use managed settings.

## 7. Exact changes

All changes are in `level4/closure_proofs/p5y_k5_cell309_q11_recovery/` and `.claude/` on
`claude/p309-q11-recovery-20261005`. **No file of r1, r2, cells 306–308, r5, status documents or any other
namespace changed** (`git diff --name-only c902fe2f HEAD` lies wholly in the write-set; enforced by the guard's
commit gate). Code: `code/{attempt_validator, p309_rehearsal, make_repaired_harness, count_target_evaluations}.py`,
`tests/{crash_matrix, make_harness_mutants, r2_postfreeze_rehearsal, r2_items_rehearsal}.py`,
`tests/run_targeted_rehearsals.sh`; repair data in `repair/`; evidence in `evidence/`.

## 8. Target-evaluation count

`code/count_target_evaluations.py`: **0 new**. It scanned 360 git repositories (the session repo, all replicas,
and every QC11, D5 and guard sandbox), origin, and 312 ledgers (132,009 rows), with r5 unchanged and no r6.
Reported, not hidden:
- 3 `refs/rlr-tail/x` in F23 TEST sandboxes, planted by the frozen harness itself
  (`test_p309_exactly_once.py:276`) to show `execute` refuses.
- 4 pre-existing PROXY_EXPOSURE rows (incidents of 2026-09-27; `new_target_evaluations` 0) in the committed
  overnight-research ledger, appearing in its 8 clones.

**Two counter corrections, disclosed.** Both counters first reported nonzero values, and both were investigated
before any claim was made:
- The scan-wide counter first reported 35: the 3 fixture refs and the 32 pre-existing rows above.
- The SessionEnd audit first reported 7: grant / authorization files of older campaigns (cell-307 RLR, CUSUM
  executor, C2, C3, C11RD, C12R2, tc_r1), all byte-identical at the branch point `c902fe2f` and dated
  2026-09-19..28. The session diff touches no grant or authorization path.

Both counters now count what this session added or changed, list the pre-existing items separately, and are
covered by fixture tests (SA1–SA4), including one proving a newly added grant file is still counted.
`audit/SESSION_AUDIT_SNAPSHOT.json` records 0.

## 9. Remaining blockers (`BLOCKERS.json`)

- **B1. No single uninterrupted end-to-end attempt of one repaired package.** The evidence is assembled from
  separate, never-resumed runs. This container restarted mid-session and is not a durable host for a no-resume
  ~6–8 h attempt, and external compute is prohibited here.
- **B2. Owner decisions OD-R2-0..6** gate r2's freeze and its single official qualification (on an approved host).
- **B3. r1 is bound to its freeze host** by design; its gates cannot be fully re-witnessed elsewhere.
- **B4. Proposed hardening for an r2 delta** (not applied): atomic and fsynced record writes, a ledger-integrity
  check before RUN START, and awareness that QC-D5 is a 60–80 min single window.

## 10. Next permitted action

For the **owner**: decide r2's packet OD-R2-0..6 (`p5y_k5_cell309_p309_r2/governance/OWNER_DECISION_PACKET_R2.md`),
optionally first commissioning an r2 delta for B4. Then follow r2's own route: freeze, then the single official
qualification via `code/p309_launch.py` on the approved durable host, then the independent qualification review.

Nothing in this report authorizes a grant, a marker, or any Γ309 evaluation.

## 11. Verdict

**QUALIFICATION_RECOVERY_BLOCKED.**

The diagnosis is complete, and the repair is verified result-free, by content, with mutants, on both r1's real
post-freeze history and r2's post-freeze package. Nothing contradicts it, so the verdict is not REJECTED. It is
not ACCEPTED because the evidence for the repaired path comes from several interrupted or partial runs, not one
complete attempt, and producing that attempt requires a durable host and owner decisions outside this task's
permissions.
