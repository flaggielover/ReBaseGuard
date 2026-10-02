# Fourth focused follow-up review of the r2 delta repairs (repair round 4) of P309-r2 at e96ed380
R2_DELTA_FOLLOWUP_4_ACCEPTED

**Reviewer.** I am reviewing the committed bytes and preserved evidence as a fresh reviewer. I did not write the r2
implementation, the verifier-author changes, the r2 plan or addenda, or any earlier r2 review. The coordinator's
`R2_DELTA_RESPONSE_4.md` was used as a guide only.

**Brief.** `governance/BRIEF_R2_DELTA_FOLLOWUP_4.md`, committed before this review. The review covers every item in
that brief and the evidence named there. The verdict is based on git, the committed evidence, the preserved attempt-10
clone, and checks in a separate scratch clone.

## Verdict in brief

**Accepted. The Conditions section is empty.** X1–X7 are met in the committed bytes. No new correctness or governance
condition blocks owner decisions or the worker tier. The cloud repair loop can close after this review; the remaining
work is owner decisions followed by the AWS worker-tier checks described in the packet.

The reviewed state is:

* branch `claude/p5y-k5-cell309-p309-r2`, HEAD `e96ed380f0da29fcbc76e21dd40a3e9b4a1d9628`;
* round-4 code at `2fc6c130`, checkpoint record `cec189d9`, validation and review brief at `19dbf404`, and the final
  checkpoint record at HEAD;
* Attempt 10 at `evidence/drill/20261002T052554Z`, PASS, with coordinator validation 44/44;
* P8 round 5 has no unexpected change; all eight supplement-4 pins match the current ASTs;
* `NEW Γ309 TARGET EVALUATIONS = 0`; no production namespace ref, grant, marker or pending-result ref exists;
* r1 remains unchanged and cell 308 was not read or touched.

## 1. X1–X7

| item | status | finding |
|---|---|---|
| X1 | met | Monitor times are unrounded. The stop time is taken after terminate/wait/kill and reaping. `parse_monitor_rows` tolerates only a torn final line; any other malformed line increments `corrupt_lines`. The stop decision requires a completed passing sample, liveness, final continuity and zero corruption. |
| X2 | met | `kill_own_descendants` traverses through already-seen descendants on every round, waits until all seen descendants are stopped/gone, then starts a confirming walk and stops only when that walk finds no new pid. Start times are checked before every signal, including the final SIGKILL. |
| X3 | met | R01 invokes the runner's own `start_qhost_monitor` and `stop_qhost_monitor` with a real child. The test places the four-second interval in `QHOST["interval"]`; production leaves the value at 60 seconds. It checks at least three samples, cadence, no corruption and no qualification write. |
| X4 | met | A01's forkers stop creating children after 20 seconds. `kill_token` repeats until no process carrying the per-case token remains. |
| X5 | met | U01 uses TEST-only configuration bytes, redacted launch-record copies, a mode-700 directory and removes the directory after the case. No host value is copied. |
| X6 | met | T14 now states its syntactic reach and its exclusions: assignment aliases, `getattr`, `exec*`, `pthread_kill` and `alarm`. |
| X7 | met | AWS instructions say that the 8c quiet check includes the gate, identify the namespace working directory, show timer service accounts and cron account fields, and state that at most 80 process rows are retained while counts cover all rows. |

## 2. X1 in depth

`stop_qhost_monitor` records `alive` before termination, terminates the child, waits up to 30 seconds, kills if needed, waits again,
and only then reads the stop clock. Therefore a monitor row cannot be written after the stop used by
`monitor_liveness`. A monitor that hangs long enough to be killed leaves a gap over the configured tolerance or no completed
sample and fails. An empty file has no completed sample and fails. A malformed non-final line is counted as corruption and fails.
A truncated final line without a trailing newline is set aside; completed rows before it still undergo all checks.

The virtual-clock cases MV06–MV09 cover torn-final, middle-corrupt, exact-stop and after-stop rows. The real R01 control
covers the runner's start/stop path. The packet and amendment I1 list the order rule, the completed-sample requirement,
monitor death/gap, continuity, failed sample and corruption as attempt-ending conditions. There is no remaining rounded-time
false-failure window.

## 3. X2 in depth

The loop's `kids` map is rebuilt each round and the traversal pushes every child, including one already in `seen`, so a
child created below a stopped descendant is discoverable. Newly found pids are SIGSTOPed only after their recorded start
time is re-read. `settled_before` is computed from the observed states; the break test is evaluated only on the next walk.
Final SIGKILL is guarded by the same start-time comparison. A pid outside the caller's descendant tree is never in `seen`.

The response's slow-fork reproduction is disclosed honestly: the previous function left survivors in 7/20 trials in the
coordinator's corrected harness, while the round-4 function left 0/20; the harness's ancestor-filter measurement fix is
explained. K02 is explicitly described as a slower bounded regression and not as a reproduction of the back-to-back fork
race, because the scanner forbids that primitive in committed tests. This is an accurate limitation, not a hidden claim.

## 4. X3 and the host controls

R01's `RUNSTOP` imports the committed qualification module, points `ATT["dir"]` at a TEST directory, sets the label to
`host_rerun`, sets `QHOST["interval"]` to 4, starts the real monitor child, stops it through the committed stop function,
and inspects the monitor rows. It does not mutate `qualification/`. Moving the interval into the existing `QHOST` state is
safe: the production state is initialized with 60 and only the test child replaces it. The drill evidence records 41/41
host controls and the R01 cadence `[4.0, 4.0, 4.003, 4.0]` seconds.

A cloud-tier control failure is fail-closed and confined to the TEST directory. The host-control suite is Linux-specific;
this macOS reviewer did not rerun its `/proc` and uid cases locally. Attempt-10's preserved Linux run and its 44/44
independent validator are the authoritative execution evidence.

## 5. Evidence and re-drill

Attempt 10's report has every required item and every item has `rc: 0`, `pass: true`, `confined: true` and
`head_unchanged: true`. The report records the expected cloud preflight refusal, 77/77 host-package decisions, 41/41
host controls and 22/22 static controls. The two planted freeze-record controls, the TEST-only prior ref, push-url guard,
repository guard, reset-row retention control and no-production-ref control all fire as expected.

The independent validation file reports 44/44 checks, 112 rows, one run-start row, no missing scripts, zero target
counters, no cells, no band hits, ordered UTC rows, equal exported and clone ledgers, and preserved F2 lineage. The report
hash is bound in the drill ledger. The post-completion container restart is recorded as an environment event after the
files were written; it did not alter the kept evidence.

## 6. Re-pins and P8

`R2_REPIN_LIST_SUPPLEMENT_4.json` has eight rows: six re-pins (`kill_own_descendants`, `qhost_monitor`,
`start_qhost_monitor`, `stop_qhost_monitor`, `case_u`, `kill_token`) and two new controls (`case_k02`, `case_r01`).
Using CPython 3.11.15 and the scanner's AST hashing code, all eight current hashes match their `now` values. The exact-
once,
backstop, production-read-path, production-token, planted-control, mutating-git and namespace lists are unchanged.

`R2_EQUIVALENCE_P8_ROUND5.json` recomputes the same result as round 4: 73 outside-namespace pins are identical; all
P8(b) paths are either the relocation map, the declared new files or the already disclosed implementation map; P8(c) has
no new occurrence; and P8(d) has 44 classified differences with zero unexpected differences. No scientific parameter,
worker budget, interval, outcome table or Stage parameter changed.

## 7. Governance and scope

`OWNER_DECISION_PACKET_R2.md` remains an option table and explicitly states that it decides nothing. Amendments §I is
append-only and contains only the X1/X2 corrections. The AWS instructions include the required account, gate, working
directory and row-retention procedure. The third follow-up's execution ledger remains outside the governance scan path,
with its sha256 bound by the preserved review; this is consistent with the stated immutable-record handling.

The round-4 diff touches only the host/Q-HOST and control plumbing, the self-audit, the scanner allowance and the
corresponding governance/evidence. It does not touch the driver, guard, verifier, generators or scanner logic. No target
input, decoy output or cell-305–309 value was opened.

## Conditions

None.

## Disclosure (reads, runs, writes)

**Runs in an isolated scratch clone:** CPython 3.11.15 `p309_static_check.py` (14/14), `p309_scan.py` (PASS),
`p309_scan_pins.py --list` (all current), and pure `parse_monitor_rows` cases for empty, valid, torn-final, and
middle-corrupt input. The unresolved-token scanner's result was not treated as a pass in the scratch clone because that clone
has no synthetic freeze file; the drill's own Attempt-10 evidence shows the generated freeze check passed. No qualification
item, drill, `execute`, `seal-only` or `validate-grant` was run by this review.

The committed Attempt-10 Linux evidence was read as JSON and the named P8, repin and validation records were checked.
The kept clone was not modified. The working repository was not written while inspecting the evidence; this review file
and its ledger/hash are the only preservation writes.

**Firewall.** No production ref was created. No target input or decoy output was opened. No cell-305–309 value, cell-307
file or cell-308 file/hash was read. All TEST processes created by earlier local checks were terminated; no process from
this review remains.

**Result.** `R2_DELTA_FOLLOWUP_4_ACCEPTED`; cloud repair loop closed; owner decisions and worker-tier validation remain
open; `NEW Γ309 TARGET EVALUATIONS = 0`.
