# Cell-308 successor MB-S r1: execution architecture (Phases 4–8; coordinator design; for implementation and review)

**Status.** A design only: no freeze, no grant, no target. New cell-308 target evaluations: 0.

**Scope.** The **science is MB308 r1's, byte-identical**. That is Theorem MB r1 and the modules `mb308_stage1`,
`mb308_supply`, `mb308_consumer`, `mb308_a0core` and `mb308_pinned`, together with every research pin (certifiers,
verifiers, F2, F3, TC-T inputs, the C2 consumer), bound by sha256 and blob at their MB r1 paths.

**What changes.** Only the lifecycle:

* a detached launch;
* durable persistence;
* a durable state machine with frozen recovery semantics;
* governed computational checkpoints;
* a host contract.

## 1. Campaign identity

* **Namespace.** `level4/closure_proofs/p5y_k5_cell308_mbs_r1` (NSS).
* **Branch.** `p5y-k5-cell308-mbs-r1`, branched from MB r1's postexec commit `21e99cf0`, so the MB r1 namespace is
  present and **never modified**.
* **Worktree.** `/Users/suzhe/ReBaseGuard-c308mbs`.
* **Refs.**
  * `refs/p5y-k5-cell308-mbs-r1/target-consumed` (the marker);
  * `…/pending-result`;
  * `…/journal` (the state journal);
  * `…/ckpt` (the checkpoint tree).
* **MB r1 is cited as history only:** consumed, interrupted, INDETERMINATE, not scientifically negative. MB r1's marker
  and refs are never read for arming and never written.

## 2. The durable state machine

**The journal.** The durable state lives in a journal: a JSON blob in the object store, pointed to by
`refs/…/journal` and advanced by compare-and-swap.

* It carries **no target value**.
* It records: the state; the grant; the driver sha; the boot session UUID (`kern.bootsessionuuid`); the process
  identity (pid, process start time, boot UUID); the attempt counter; the ids of the checkpoint tree; and a
  monotonically increasing sequence number.
* Every journal write is written durably first. The update-ref CAS goes against the previous journal id.

| state | defined by | recovery (frozen) |
|---|---|---|
| **NO_TARGET_CONSUMED** | no marker | nothing consumed. `execute` is permitted only at a valid grant |
| **CONSUMED_COMPUTING** | marker; journal = COMPUTING; the recorded process identity is alive under the **same boot UUID** | wait; no action. A second `execute` is refused (CONSUMED) |
| **CONSUMED_INTERRUPTED** | marker; journal = COMPUTING; the recorded process identity is dead **or** the boot UUID changed | `resume`, **mandatory** (§4). The attempt counter increments |
| **RESULT_DURABLE_UNSEALED** | a durable, verified complete-result file in the spool (§3); no pending ref | `seal-only`: object store → pending ref → seal |
| **PENDING_RESULT** | pending ref naming a blob whose bytes verify | `seal-only`: seal → materialize |
| **SEALED** | a seal commit on the branch holding exactly the result path; the pending ref names its blob | materialize if missing; nothing else |
| **CONSUMED_UNRECORDED** | marker; no journal, or a journal whose checkpoints fail verification, or the resume budget is exhausted (§4) | **terminal INDETERMINATE**: `close-indeterminate` seals a value-free INDETERMINATE record |
| **INDETERMINATE** | a sealed value-free INDETERMINATE record, or a sealed record whose status is a post-marker failure | terminal; no rerun |

**Status is read-only and deterministic.** `status` classifies the state from refs, spool, journal, process table and
boot UUID only, and prints the **state name only**.

**Dispatch.** `recover` is the only dispatcher. It performs exactly the frozen action for the classified state. It
never computes in any state other than CONSUMED_INTERRUPTED, and there only through `resume`.

## 3. The crash-safe persistence boundary (the complete result)

The spool directory is `<git dir>/mbs308-spool/`: outside the worktree, never tracked, never under /private/tmp. The
steps:

1. The evaluation completes. The result dict is built (status, mechanical outcome, all records), in memory.
2. Canonical serialization (`serialize`: sorted keys, self sha256).
3. Write `result.json.tmp` with O_CREAT|O_EXCL|O_NOFOLLOW, then `fsync(fd)`.
4. `rename(tmp, result.json)`, then `fsync(dir fd)` (on macOS also `F_FULLFSYNC` via `fcntl` where available).
5. Read back and verify: byte equality and self sha256.
6. The journal CAS → RESULT_DURABLE (it records the result sha256, never the value).
7. `git -c core.fsync=loose-object hash-object -w`, verify the blob id, then update-ref the pending ref (CAS from
   zero). The journal → PENDING_RESULT.
8. Seal: a private-index commit adding only the result path; update-ref the branch (CAS); the journal → SEALED.
9. Materialize with O_EXCL|O_NOFOLLOW.

**Invariants:**

* A file whose self hash, schema, grant or driver binding fails is **never** used. The state classifies as
  CONSUMED_INTERRUPTED if checkpoints permit, else CONSUMED_UNRECORDED.
* `result.json.tmp` is never read as a result.
* Only a file that completed steps 3–5 **and** carries `complete: true` with a terminal status field is a complete
  target result.

## 4. Computational checkpoints (not results) and governed resume

* **What they are.** Each completed Stage-1 job record (the object MB r1 keeps in memory) is written durably when its
  job completes:
  * blob → tree entry under `refs/…/ckpt`;
  * record schema `…ckpt.v1`, carrying: job key (kind, block, rung), its bytes' sha256, the grant, the driver sha,
    and the journal sequence number.
* **A checkpoint is never a result.** It has no Stage-2, no decision and no `complete` flag. `status`, `recover`,
  the adjudication and every reviewer treat it as opaque.
* **No channel prints or materializes checkpoint content.** Only `resume` reads it, with the guard armed.
* **Resume.** `resume`:
  * verifies every checkpoint (hash, schema, binding);
  * recomputes exactly the jobs without a verified checkpoint;
  * rebuilds Stage 1 by MB r1's aggregation over all job records;
  * then runs Stage 2, the decision, and §3.

  The science is deterministic (MB r1 QC04), so an interrupted-then-resumed evaluation yields the same bytes of
  every certified quantity as an uninterrupted one. **It is one evaluation, not a rerun.**
* **Mandatory continuation.** There is no discretionary abandonment. After the marker, the operator's only permitted
  actions are `recover` and `resume`. The frozen terminal rules are:
  * (a) a checkpoint fails verification: resume ignores that checkpoint and recomputes the job. Two consecutive
    verification failures of the same job make the run CONSUMED_UNRECORDED;
  * (b) at most **3** resume attempts;
  * (c) a deadline of **7 days** after the marker.

  Past (b) or (c), `close-indeterminate` applies. Any stop outside these rules is disclosed as a deviation and
  classified INDETERMINATE.
* **Quarantine.** Checkpoint blobs are target intermediates:
  * the research scanner and the leak scans cover the ckpt tree by counts only;
  * no agent reads them;
  * the ledger records their existence, never their content.

## 5. Detached launch (no dependence on the hosting app)

* **Launch through launchd.** `launch` installs a transient LaunchAgent with a unique label
  (`org.rebaseguard.mbs308.<mode>.<utc>`):
  * `ProgramArguments` is the pinned interpreter with `-I -S -B` and the driver with its mode;
  * `RunAtLoad` true, `KeepAlive` false, `AbandonProcessGroup` true;
  * `StandardOutPath` and `StandardErrorPath` point to a durable log dir (`~/Library/Logs/ReBaseGuard/mbs308/`, not
    /private/tmp);
  * `WorkingDirectory` is the worktree.

  It is started with `launchctl bootstrap gui/<uid> <plist>`. The job is then launchd's child, outside the hosting
  app's process tree, session and coalition.
* **The launcher records** the label, the pid (from `launchctl print`), PPID (1), PGID, SID, uid, the process start
  time and the boot UUID. It **proves detachment by test, not by PPID=1**:
  * the pid is not a descendant of the launching shell;
  * the SID differs from the launcher's;
  * `launchctl print` names the job as running;
  * the integration test kills the launcher's entire process group and session and checks that the job survives.
* **Caffeinate is supervised.** The driver runs `caffeinate -i -m -s -w <driver pid>` under a supervisor thread that
  re-spawns it if it dies, recording each death and re-spawn in the host provenance. This closes the 23:29 failure
  mode, in which caffeinate died and the driver survived.
* **Stale pidfile or lock.** The pidfile carries (pid, start time, boot UUID, command sha). It is valid only if all
  four match a live process. A stale pidfile is reported and never trusted.

## 6. The host contract (separate from scientific validity)

* **Preflight gates.** Each fails before the marker, so nothing is consumed:
  * AC power;
  * lowpowermode 0;
  * thermal-pressure level 0;
  * free disk ≥ 2 GiB on the repository volume;
  * memory-pressure level normal;
  * boot UUID recorded;
  * no other campaign job running (no live pidfile);
  * launched by the launchd launcher (`XPC_SERVICE_NAME` / the label is present).
* **Recorded and never gating.** During the run: sleep channels K/S/L; power; thermal; load; memory pressure;
  caffeinate re-spawns; boot UUID. **Host provenance never changes the status, the outcome or exactly-once** (MB r1
  E3).
* **Reboot.** A reboot is detected by the boot UUID change and classified CONSUMED_INTERRUPTED. It is never a result.

## 7. Crash-injection and mutant requirements (tests; target-free)

**The fault points.** A test-only environment hook drives the fault points. The production run refuses when it is
present, and a static check enforces this. Each fault point `F<n>` performs a real `os._exit` or `SIGKILL` of the
driver, or of a worker, at:

1. before the marker;
2. immediately after the marker;
3. during Stage 1, after k checkpoints;
4. before the result write;
5. during the tmp write (a partial file);
6. after the write, before fsync;
7. after fsync, before rename;
8. after rename, before the journal RESULT_DURABLE;
9. after RESULT_DURABLE, before the pending ref;
10. after the pending ref, before the seal;
11. during the seal (a commit object without the ref);
12. after the seal.

**Simulations as well:**

* launcher death;
* killing the launching process group and session (the "hosting app" Force Quit analogue);
* caffeinate death, with the supervisor re-spawning it;
* driver death and worker death;
* a simulated reboot (boot UUID changed in the classifier's input);
* a stale lock, a stale pidfile, a corrupt tmp, a truncated `result.json`, a wrong result hash;
* a stale pending ref naming a missing or wrong blob;
* a duplicate `recover` or `resume` running concurrently (lock by O_EXCL lockfile plus CAS).

**For every case, the test asserts:**

* the classified state;
* the recovery action;
* that no second marker exists, and nothing is computed twice when a verified checkpoint exists;
* the final state (SEALED, or the frozen INDETERMINATE);
* that the resumed result's certified bytes equal an uninterrupted run's bytes (synthetic evaluator, and one decoy
  cell).

**Mutants.** Every gate has a planted mutant that must make its test fail. Examples:

* skip the fsync;
* skip the self-hash check;
* accept a `.tmp` file;
* accept a checkpoint with the wrong grant;
* resume on a live process;
* allow abandonment;
* treat PPID=1 as detachment;
* no caffeinate re-spawn.

## 8. What stays of MB r1

* The criterion, the admission rule D5, the controls (C-A, C-B), the guard semantics and the admitted 37 pairs.
* The caps, EVAL_CAP (a CPU-per-job cap, plus the wall-clock alarm), and the qualification case families (QC01–QC13,
  Q8, Q12 with host provenance).
* Q12 re-derives the cap check from the successor's own official decoy runtimes.
* The MB r1 "decoy / rehearse / preflight" modes carry over with the successor's identity.
* The wall-clock EVAL_CAP applies per attempt, from the marker or from the resume start, and never across a sleep
  classified by K/S/L. This is a new, frozen rule, to be reviewed.
