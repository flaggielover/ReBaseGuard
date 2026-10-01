# P309-r2: owner decision packet (OD-R2-0 … OD-R2-6)

**Why this packet exists.** It is prepared so that the owner can decide. **Nothing in it is decided, and no answer is
inferred from any instruction.** Every option is set out with its consequences.

**Sources:**
* `R2_PLAN.md`;
* addenda 1 and 2;
* reviews P1–P23 and F1–F11;
* the r2 delta review (`REVIEW_R2_DELTA.md`, conditions C1–C15) and `P309_R2_AMENDMENTS.md`;
* `OWNER_INSTRUCTIONS_R2_VERBATIM.md` and `OWNER_INSTRUCTIONS_R2_MSG4_VERBATIM.md`.

**Revision.** This revision applies the delta review's condition C1 (a)–(d). The first version was committed at
`61731123` and is preserved in git history.

**State when written:**
* HOST_SUITABILITY_PENDING;
* NEW Γ309 TARGET EVALUATIONS = 0;
* no production-namespace ref, no grant, no marker and no pending-result ref;
* r1 immutable at `c902fe2f`, tree `ecd1c359`.

---

## OD-R2-0: authority and carry-over (needed before the r2 freeze)

### What is asked of the owner

* **(A) Confirm the record.** Confirm two files:
  * `OWNER_INSTRUCTIONS_R2_VERBATIM.md` records the owner's 2026-10-01 messages 1–3 verbatim, with one disclosed
    redaction (the retired worker's IP);
  * the overnight message 4 is recorded verbatim in its own file, `OWNER_INSTRUCTIONS_R2_MSG4_VERBATIM.md` (sha256
    `de3c8e44…`).

  Message 4 was **not** appended to the first file. That file is immutable under self-audit A3, so appending would have
  broken the check.
* **(B) Confirm the carry-over.** Confirm each row of the carry-over table below.
* **(C) Acknowledge the r1-era events.** Acknowledge the events listed under "Liabilities" for the purpose of proceeding
  with r2.
* **(D) Authorize, or decline, the r2 stage.** The text proposed for authorization, by analogy with r1's P0-1, is:

  > "Authorize, for the successor campaign p5y_k5_cell309_p309_r2:
  > * the formal freeze and the single official qualification (QC01–QC17, QC-U2, QC-D5, Q-HOST; started only through
  >   code/p309_launch.py; no retry, no resumption), both on the **qualification host** approved under OD-R2-3 and
  >   OD-R2-4;
  > * the independent qualification review;
  > * the preparation of the grant package.
  >
  > This names and approves no **target-execution host**; that is OD-R2-6, decided separately. It does NOT issue the
  > target execution grant, does not arm or consume a marker, and does not authorize any Γ309 evaluation."

  The delta review asked for the two hosts to be kept apart (C1 (d)). The first version's wording, "on the host
  approved under OD-R2-3/6", joined them.

### Carry-over table: r1's owner decisions and their r2 status

| r1 owner text | proposed r2 status | asked of the owner |
|---|---|---|
| P0-1 / G2 (authorization for r1's freeze, qualification and package) | **not carried**: r1-specific | (D) |
| CELL SET {309}; 305–308 excluded; Stage-1 material bound to 309 | {309} is carried by msg 1 §1. The exclusions and no-reuse are not covered by msg 1 | confirm |
| EXECUTION HOST: not on the cell-308 machine while 308 is live | for r2's drill, freeze and qualification: **superseded** by msg 3 (shared host, exclusive heavy compute). For **target execution**: not settled here | OD-R2-6 |
| INCIDENT ACKNOWLEDGEMENT (r1 list) | carried for the events it listed | confirm, and (C) for later events |
| EFFICACY: UNKNOWN BY DESIGN; the evaluation may be consumed without closure | carried as part of the inherited scientific object | confirm |
| SRK-T out of package 1 | carried | confirm |
| FORMAL CAMPAIGN PROCEDURE (conservative order; history rules) | r2's order is P13 / addendum 2; the history rules are carried by msg 1 §9 | confirm |
| QUALIFICATION FAILURE: preserve and stop | carried, and strengthened by P23 (a failed r2 ends r2; any r3 is a new owner decision) | confirm |
| SUCCESSFUL QUALIFICATION ENDPOINT | carried (msg 1 §10) | — |
| ABSOLUTE BOUNDARY | carried (msg 1 §0, §7, §10) | — |
| GITHUB / HISTORY | carried (msg 1 §9) | — |
| FINAL HANDOFF list | carried, plus host identity and durability | confirm |
| Owner rulings 2: GRANT ADMISSION CODE (the verifier author's authority; "do not have the coordinator silently implement an independent component") | applied to r2 as a constraint (F11) | confirm |
| Owner rulings 2: U2, FC2, scanner allowance, sandbox marker | carried as inherited rules; the marker-name allowance moves to OD-R2-2 | confirm |
| Owner rulings 2: FORMAL CAMPAIGN CONTINUATION (autonomy through stages) | for r2, autonomy is governed by msgs 1, 3 and 4 | confirm |
| G1: acceptance of the MEDIUM-HIGH liability | an owner acceptance, not part of the scientific object | confirm |
| STAGE-1a FAILURE SEMANTICS (rev. 2b §2.5) | carried as producer semantics | confirm |
| Owner D5: the pending-ref NAME and the two exactly-once sites | **not covered for r2's names** | OD-R2-2 |

### Liabilities for acknowledgement (C)

* **Qualification failure.** r1's single official qualification FAILED: a QC11 harness defect, after which the host
  container rebooted during QC_D5. There was no Q, no review and no grant.
* **Incidents and errata.** The P309F-01 incident, and formal errata FE-1 to FE-11.
* **Unreviewed allowlist entries.** r1's never-reviewed allowlist entries of the unresolved-marker check (D3). For r2, P16 applies:
  every allowed hit is listed for the pre-freeze reviewer.
* **Reboots.** The 22:41:12Z container reboot (at least the third restart in that session).
* **A firewall departure.** r1's postmortem reviewer hashed four pinned cell-307 files, against its brief's limit to
  git metadata.
* **Brief timing.** Briefs were issued by message only and recorded after issue (departures from C5).
* **r2 development history** (preserved in `evidence/drill/`):
  * cloud-tier drill attempts 1–5: attempts 1–3 failed on development defects (all fixed), and attempts 4 and 5 passed.
    The repair round after the delta review adds the attempt(s) that the final overnight report lists;
  * one coordinator write during a drill, which tripped the F2 check;
  * pushes made before the r2 checkpoint tool was relocated.

---

## OD-R2-1 and OD-R2-1b: the r2 production namespace and its bindings

**The names, as currently implemented provisionally:**

| binding | r1 | r2 (provisional, option b) |
|---|---|---|
| ref namespace | `refs/p5y-k5-cell309-p309-r1/` | `refs/p5y-k5-cell309-p309-r2/` |
| grant path | `…_p309_r1/authorization/P309_GRANT.json` | `…_p309_r2/authorization/P309_GRANT.json` |
| grant `campaign` | `p5y_k5_cell309_p309_r1` | `p5y_k5_cell309_p309_r2` (schema `P309_GRANT/1` kept) |
| result path | `…_p309_r1/evidence/execution/P309_RESULT.json` | `…_p309_r2/evidence/execution/P309_RESULT.json` |
| result SCHEMA | `rebaseguard.p5y.k5.cell309-p309-r1.result.v1` | `rebaseguard.p5y.k5.cell309-p309-r2.result.v1` |

**The options:**

* **(b), recommended and implemented provisionally.** Each campaign has its own names. r1's namespace stays forbidden
  everywhere. The driver refuses execution while **any** ref under `refs/p5y-k5-cell309` exists, which is the
  cross-campaign exactly-once rule. This needs no new code beyond what is already implemented.
* **(a) Keep r1's names for r2.** The two campaigns' evidence would then share names, and r1's "forbidden everywhere"
  rule would have to be lifted for r2. **Cost:** re-implementing the owner rows of the literal table, a new delta
  review and a re-drill.
* **(c) Other names named by the owner.** Cost as for (a).

**OD-R2-1b.** Confirm the four bindings above, or name others. A change means the same cost.

---

## OD-R2-2: the pending-result and marker names, and the D5 extension

**What is asked.** Ratify for r2:
* the marker name `refs/p5y-k5-cell309-p309-r2/target-consumed`;
* the pending-result name `refs/p5y-k5-cell309-p309-r2/pending-result`.

Also extend owner D5 (exception 2) to r2's two exactly-once sites, `_arm_marker` and `_persist_pending`. Their AST
sha256 values are unchanged from r1's ratified pins (`1ee764b7…`, `13ee3ec3…`), and the A38 backstop pins are
unchanged (`R2_REPIN_LIST.json`).

**Semantics:**
* The marker is created exactly once, by `_arm_marker`, only inside an execute that a valid owner grant admitted.
* The pending ref is created only by `_persist_pending`, after the marker.
* Neither exists today, and neither is created by any test, drill or sandbox: TEST names are used there (F1).

**Collision checks:**
* no ref under `refs/p5y-k5-cell309` exists, locally or on the remote;
* r1's and r2's names are distinct;
* both start with the driver's `PRIOR_MARKER_PATTERNS[0]`, so the existence of either refuses execution;
* the scanner allows each literal only at its reviewed definition, and QC12 T12 checks all of this statically.

---

## OD-R2-3: the AWS access path, the session and the window

**Required:** a separate P309 session on the shared AWS worker, with:
* its own access path and a P309-only credential;
* never cell 308's session, user, terminal or credential;
* no self-hosted runner unless the owner explicitly chooses one (P12).

**The AWS-side session must:**
* follow `R2_AWS_SESSION_INSTRUCTIONS.md` and `R2_BOOTSTRAP.md` in order: the 8a read-only audit, the 8b verdict,
  then STOP, then 8c bootstrap of consented items only, then the 8d worker-tier drill;
* push evidence only through the r2 checkpoint tool.

**It must not:**
* touch cell 308's checkout, processes, refs or units;
* change the host without OD-R2-4 consent;
* freeze, qualify or grant.

**Exclusive heavy-compute windows:** about **9 h** for the worker-tier drill and about **9 h** for the official
qualification. Each starts with cell 308 idle (exclusion gate). If cell 308 needs the host, P309 waits.

---

## OD-R2-4: host changes requiring consent (the owner's and the cell-308 operator's)

**Read-only, needing no consent beyond OD-R2-3:** the 8a audit, `isolation`, `preflight`, `gate`, and
`systemctl list-units`.

**Host mutations, each needing consent:**
1. creating the P309 Unix user, with no group access to cell 308's checkout;
2. a P309 volume or quota (≥ 40 GB free);
3. a **polkit** rule letting the P309 user start only `p309-r2-*` transient system units. The launcher calls
   `systemd-run` directly; a sudo rule is not used by the code;
4. holding automatic reboots and upgrades for each window (host-wide; it affects cell 308 too);
5. a P309-private CPython 3.11.15 under the P309 home (P309 files only; no system change).

**The unit's limits** (P20). Every P309 unit runs with settings the owner and the cell-308 operator agree to:
* `MemoryMax`: it must leave cell 308 its working memory;
* `OOMScoreAdjust`: P309 is preferred for an OOM kill;
* low `CPUWeight` and `IOWeight`;
* `KillSignal=SIGKILL`, `SendSIGKILL=yes` and `TimeoutStopSec=10s`: a stopped P309 unit dies at once;
* `ProtectSystem=strict`, `PrivateTmp`, `NoNewPrivileges`, and `InaccessiblePaths=` for each cell-308 root.

The values are in the host configuration (`R2_AWS_SESSION_INSTRUCTIONS.md` §3.1). They are recorded in the launch
record, and the runner checks them against `systemctl show` of its own unit.

**The cell-308 identification data** (delta review C2). Two items come from the cell-308 operator:
* the cell-308 campaign's uid or uids (`foreign_uids`);
* its heavy-job command patterns.

Both are read-only facts, but P309's gate and monitor depend on them (see OD-R2-5).

**Isolation without altering cell 308.** `InaccessiblePaths=` on P309 units and a P309 user without group access
leave cell 308's checkout unchanged (message 3 §6). Only if those fail would the owner be asked to amend §6.

**A world-readable cell-308 checkout fails isolation.** The `isolation` check (`foreign_roots_unreadable`) runs as
the P309 user, **outside** the unit, and requires that user to be unable to read the checkout by its permissions. If
the checkout is world-readable (the 8a audit records this as a boolean), the check fails. `InaccessiblePaths=` inside
the unit does not change that result. Proceeding would then need the owner to amend message 3 §6, with the cell-308
operator's consent, for example to restrict the checkout's permissions. The coordinator changes nothing of cell 308.

---

## OD-R2-5: interference policy

**The owner's text.** Message 3 §3: "if a cell-308 heavy job is running, P309-r2 may perform only work that does not
materially affect host resources". Message 3 §8: do not interrupt cell 308; wait.

**The options:**
* **(i)** A cell-308 heavy start during an r2 run makes Q-HOST record FAIL. The single attempt ends (P23) and no retry
  is possible. This matches §3 and §8 as written; it is what the code implements now. **Risk:** a third party can
  consume r2's only attempt, so windows must be agreed with the cell-308 operator.
* **(ii)** r2 continues at idle priority (lowest CPU and IO weight, OOM preference) while cell 308 runs heavy work.
  **This conflicts with the owner's existing strict-isolation instruction (message 3 §3) unless the owner amends
  it.** It would also need a code change and a re-review.

**What "heavy" means in the bytes** (delta review C1 (b)). The start and the run use different definitions:

| | at the start (exclusion gate, 60 s sample) | during the run (Q-HOST monitor, every ≤ 60 s) |
|---|---|---|
| one foreign or unattributable process | blocks if it uses more than **0.05** of a core, matches a heavy pattern, or appeared during the sample | fails if it uses more than **0.5** of a core, or matches a heavy pattern |
| all of them together | the load average must be at most the agreed baseline + 0.5 | fails if they use more than **1.0** core together |
| a process first seen in a sample | blocks | is judged at the next sample (a grace of one sample) |
| other ReBaseGuard processes | block above 0.05 of a core | fail above 0.5 of a core |
| P309's own unit | excluded | excluded |

The thresholds are the host configuration's `heavy_cpu_fraction`, `monitor_heavy_cpu_fraction` and
`monitor_aggregate_cpu_fraction`. Option (i) consumes r2's attempt exactly when the right-hand column fires. Changing
the values is a host-configuration change, recorded in the launch record.

**What the P309 user can see** (delta review C1 (b), C2). P309 runs as a separate Unix user (P12). It cannot read
another user's process working directory, so it recognises a cell-308 process only by:
* its uid, if listed in `foreign_uids`, which the gate requires to be non-empty;
* its command line, by `foreign_patterns` and `foreign_heavy_patterns`;
* or as **unattributable**: a process of another non-root user whose working directory cannot be read. It counts as
  foreign.

If cell 308 runs as root, its uid 0 must be listed, and every root process then counts as foreign. The cell-308
operator must therefore supply the uids and job patterns. Without them, detection depends on the command line alone.

**How fast a run stops** (delta review C1 (b), C5):
* **Detection** takes up to one sampling interval: 60 s, plus up to 20 s of sampling. A newly started cell-308 process
  is judged one sample later, so detection can take up to about 140 s after it starts.
* **Termination after detection** is immediate. The runner SIGKILLs its own process tree, which ignores SIGTERM, and
  records Q-HOST FAIL. The unit's `KillSignal=SIGKILL` stops anything left. In the worker-tier drill, the drill stops
  at once as well.
* While the run is undetected, P309's low CPU and IO weights apply.

**The coordinator does not choose.**

---

## OD-R2-6: the target-execution host (separate from the qualification host)

**The question:** should the shared AWS worker also be the eventual target-execution host? Approving it as the
qualification host does **not** imply approving it for target execution.

**The facts:**
* Execution may take **about 31.5 h** at 4 workers (the A6 bounds: < 96 CPU-h Stage 1a, < 30 CPU-h Stage 1b).
* After the marker is armed, an OOM kill, `kill -9`, reboot or host loss makes the outcome `EXECUTION_INDETERMINATE`
  (A22), and the single evaluation is consumed.
* A 31.5 h exclusive window on a shared host requires cell 308 to stay idle throughout, and reboots and upgrades to be
  held host-wide.

**What the bytes do today** (delta review C1 (a); repaired under C7 and C8):
* **The frozen proposal names no host by default.** The parameter file's `proposed_execution_host` names a host only
  if the owner's own OD-R2-6 answer exists at the freeze, as `governance/OWNER_OD_R2_6_ANSWER.json`. Otherwise it
  states that no host is proposed.
  * The bytes the delta review read (`447e0713`) behaved differently. They would have written "this isolated cloud
    environment (rev. 2c A14)" with the freeze host's id, so a freeze on the AWS worker would have proposed that
    worker without any decision.
  * Also to settle: whether the frozen field may name any host before OD-R2-6 is answered.
* **The QC10 host re-run** is now gated. It runs only through `code/p309_launch.py --mode host-rerun`, under the
  exclusion gate, isolation, the durability preflight and Q-HOST, into `qualification/host_rerun/<host id>/`.
* **`execute` and `seal-only` are not gated** by the launcher, the exclusion gate or Q-HOST. Under
  `P309_R2_AMENDMENTS.md` §C, on a host shared with another campaign, execute may run only after a further reviewed
  amendment (with code, a delta review and a re-drill). The bytes support execute only on a host that runs no other
  campaign's work.
* **The grant-proposal tool** (`make_proposed_authorization.py`) writes the id of the host it runs on into the proposed
  grant's `execution_host`. The owner checks or replaces it in the grant.
* **The runtime is pinned** (delta review C14). The freeze manifest pins the python version, glibc and the sha256 of
  the interpreter binary, and the driver's binding check refuses any difference. So the execution host must run a
  byte-identical interpreter with the same glibc as the freeze host. `validate-grant` shows a mismatch without
  spending anything; an `execute` refusal spends the grant.

**Also to decide:**
* whether QC10's host re-run is repeated immediately before any grant (rev. 2c A14);
* which of these the execution host is:
  * the qualification host;
  * a dedicated host;
  * the shared worker, with the amendment above.

**The coordinator does not choose.**
