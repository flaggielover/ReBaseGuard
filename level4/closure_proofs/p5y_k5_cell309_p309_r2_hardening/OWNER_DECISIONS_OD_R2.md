# Owner decisions OD-R2-0 … OD-R2-6: a decision aid

**Nothing in this document is a decision.** Each "Recommendation" is a recommendation only, labelled as such. Every
OD remains open until the owner answers it in their own words.

## Source

| item | value |
|---|---|
| file | `level4/closure_proofs/p5y_k5_cell309_p309_r2/governance/OWNER_DECISION_PACKET_R2.md` |
| branch / head | `claude/p5y-k5-cell309-p309-r2` @ `101ef2cb17e5eab2892212178278da45b98004ed` |
| last commit touching the file | `2fc6c130` (2026-10-02, repair round 4, 5th revision of the packet) |
| file sha256 at `101ef2cb` | `9be65aa61625525406598a4d987a8cd30bc1fde8dc1f56504a45d4432f2bcaca` |
| owner answers present in r2 | **none**: no `OWNER_OD_R2_*` answer file, including no `governance/OWNER_OD_R2_6_ANSWER.json` |

The owner's binding texts are recorded verbatim in r2: message 1 (§0–§11), message 2 (the Vultr worker retired) and
message 3 (the shared AWS worker) in `governance/OWNER_INSTRUCTIONS_R2_VERBATIM.md`; message 4 in
`governance/OWNER_INSTRUCTIONS_R2_MSG4_VERBATIM.md`. These rules apply to every OD below:
- message 1 §5B: no retry or resume "merely for convenience";
- message 3 §3 and §8: exclusive heavy compute, and never interrupt cell 308;
- message 4 item 7: decisions OD-R2-0..6 are reserved to the owner;
- message 4 item 13: the cloud session is not an official durable host.

## Invariants every option is checked against

- **I1** NEW Γ309 TARGET EVALUATIONS = 0, before and after the decision.
- **I2** No grant, marker or pending-result ref before a passed qualification and its review.
- **I3** Exactly once across campaigns: any ref under `refs/p5y-k5-cell309*` refuses execution, and r1's namespace stays forbidden.
- **I4** No retry or resume of a qualification attempt (A27 / R4 B8 / r2 P23).
- **I5** Cells 306–308 untouched: no checkout, process, ref, evidence or unit of cell 308 is changed.
- **I6** r5 unchanged, no r6, no adoption.

## Evidence produced since the packet was written (relevant to several ODs)

| evidence | where | bears on |
|---|---|---|
| r1 Q11 root cause, independently reproduced; r1 QC-D5 passes under its frozen harness | branch `claude/p309-q11-recovery-20261005` @ `290b6c10` | OD-R2-0 (C) |
| r2's QC11 repair passes post-freeze (112/112), and r2's QC-D5 passes (166 / 27 / pins current) | same branch, `evidence/r2_postfreeze/` | OD-R2-0 (D) |
| 48 QC10 certificates byte-identical across 4 runs on 2 hosts | same branch, `evidence/qc10_reproduction/` | OD-R2-6 (QC10 host re-run) |
| three real interruptions in one cloud session (one tool limit, two container restarts) | same branch, report §5 | OD-R2-3/4/6 (host durability) |
| r2 as shipped: non-atomic, non-fsynced evidence writes; launches over a torn ledger, a temporary file, or an orphan RUN START (a second start) | this branch, `evidence/matrix/MATRIX_BASELINE_r2_101ef2cb.json` | OD-R2-0 (D), proposed OD-R2-H |
| r2's durability preflight requires a cloud metadata service (IMDS); it fails closed on a non-cloud host | `code/p309_host.py` `durability_preflight` | OD-R2-3/6 |
| F-DRILL-ORDER: r2's drill topology writes the manifest before the parameters, so the runner's own precondition would refuse in a worker-tier drill | this branch, `R2_QUALIFICATION_HARDENING_REVIEW.md` §4 | OD-R2-3 (the 8d drill) |

---

## OD-R2-0: authority and carry-over

1. **Source:** packet §OD-R2-0, lines 31–100 (sha above).
2. **Why it exists:** r1's owner decisions were made for r1. r2 is a new campaign, and nothing may be inferred from an
   instruction (message 4 item 6). r2 needs its own record of authority before it can be frozen.
3. **Evidence that exists:** verbatim owner messages 1–4 with sha256 (message 3: `78cd27da…`; message 4: `de3c8e44…`);
   the carry-over table; the liabilities list. Since then: the recovery-session evidence above.
4. **Explicit options**, in four parts:
   - (A) confirm, or correct, that messages 1–4 are recorded verbatim;
   - (B) confirm each carry-over row, or amend rows;
   - (C) acknowledge the listed liabilities, or decline to proceed;
   - (D) authorize r2's freeze, its single official qualification, the independent qualification review and the
     grant-package preparation on the OD-R2-3/4 qualification host (the proposed text), **or** decline.
5. **Consequences:**
   - (A)–(C) confirmed: the record is settled and nothing runs.
   - (D) authorized: the next run is the one official attempt. Under r2 P23, a failed or interrupted r2 ends r2; an r3
     would be a new owner decision.
   - (D) declined: r2 stays pre-freeze, and drills and development may continue.
6. **Invariant-preserving options:** every option. (D) authorizes no grant and no Γ309 evaluation (I1, I2).
7. **Recommendation (only):**
   - Confirm (A) and (B).
   - Acknowledge (C), adding the recovery-session events (r1 Q11 recovery; three cloud-session interruptions; the
     r2 baseline durability defects).
   - **Do not authorize (D) yet.** First decide the proposed OD-R2-H below, then have the chosen package pass r2's
     own delta-review route and a worker-tier drill on the chosen host.
   - Reason: under P23 one interruption, or one torn record, ends r2. The baseline matrix shows r2 as shipped can
     lose an attempt's evidence to a torn write, and can start a second run over an orphan RUN START.
8. **Decide now?** (A)–(C): **yes**. (D): **more evidence first** (OD-R2-H, the delta review, the worker-tier drill).

## OD-R2-1 / OD-R2-1b: the production namespace and its bindings

1. **Source:** packet §OD-R2-1, lines 103–125.
2. **Why it exists:** r2 must not share names with r1's forbidden namespace, and the grant / result / schema
   bindings must be fixed before the freeze.
3. **Evidence:**
   - option (b) is implemented provisionally and reviewed (delta review C1–C15 and four follow-ups);
   - QC12 T12 checks both production namespaces statically;
   - the r2 post-freeze rehearsal passed QC12.
4. **Explicit options:**
   - (b) each campaign has its own names; the r1 namespace stays forbidden; any `refs/p5y-k5-cell309*` ref refuses
     execution;
   - (a) keep r1's names;
   - (c) owner-named names.
   - OD-R2-1b: confirm the four bindings, or name others.
5. **Consequences:**
   - (b): no new code.
   - (a) and (c): re-implementation of the owner rows of the literal table, a new delta review and a re-drill; (a)
     also lifts r1's "forbidden everywhere" rule.
6. **Invariant-preserving:** (b) fully. (a) weakens I3's r1-forbidden rule. (c) depends on the names.
7. **Recommendation (only):** **(b)**, and confirm the four bindings as listed.
8. **Decide now?** **Yes**: no further evidence is needed.

## OD-R2-2: marker and pending-result names; extending D5 to r2's two sites

1. **Source:** packet §OD-R2-2, lines 129–148.
2. **Why it exists:** owner D5 ratified r1's names and r1's two exactly-once sites only.
3. **Evidence:**
   - the sites' AST pins are unchanged from r1's ratified values (`1ee764b7…`, `13ee3ec3…`); A38 backstop pins are
     unchanged (`R2_REPIN_LIST.json`);
   - QC12 T12 passes;
   - r2's QC-D5 passes post-freeze with scan pins **all current** (recovery branch, `evidence/r2_postfreeze/`);
   - the hardening branch keeps every pinned function byte-identical (`evidence/AST_DIFF_RUNNER.json`).
4. **Explicit options:** ratify the two names and the D5 extension as listed, or name other names (and/or decline
   the extension).
5. **Consequences:**
   - ratify: no code change.
   - other names: a code change, a scanner allowance update, a delta review and a re-drill.
   - declining the extension: r2 cannot pass QC-D5 / QC12 T4 as built.
6. **Invariant-preserving:** ratification (I2, I3). Both names begin with `refs/p5y-k5-cell309`, so either refuses execution.
7. **Recommendation (only):** **ratify** both names and the D5 extension.
8. **Decide now?** **Yes.**

## OD-R2-3: the qualification host's access path, session and windows

1. **Source:** packet §OD-R2-3, lines 152–170. Owner message 3 chose the **shared AWS worker**.
2. **Why it exists:** the qualification needs a durable host; message 4 item 13 excludes the cloud session itself.
3. **Evidence:**
   - r2's procedure: 8a read-only audit → 8b verdict → STOP → 8c bootstrap → 8d worker-tier drill;
   - estimated windows: about 9 h for the drill and about 9 h for the qualification;
   - r2's code is built for that worker. Its durability preflight **requires** a cloud metadata service (IMDS),
     not-spot, not-burstable and no scheduled maintenance, and reads the instance id;
   - measured here: a full r1-bytes gate set needs about 4.5–7 h on a contended 4-vCPU host, and QC-D5 alone about
     60–80 min (`DURABLE_HOST_EXECUTION_PACKET.md`).
4. **Explicit options in the packet:** approve the separate P309 session on the shared AWS worker as specified (own
   access path, P309-only credential, never cell 308's session), or decline (P309 waits).
   **Not in the packet but implied** by OD-R2-6 and message 2: a dedicated host. That requires amending message 3,
   and a code change if the host has no IMDS.
5. **Consequences:**
   - approve: the 8a audit may start; nothing is frozen or qualified (the packet forbids freeze, qualify and grant
     in that session).
   - decline: no qualification host, so r2 cannot proceed.
   - a dedicated non-cloud host: `durability_preflight` fails (`cloud_metadata_available`, `not_spot`,
     `not_burstable`, `no_scheduled_maintenance`), so it needs a reviewed host-portability change.
6. **Invariant-preserving:** all options, provided I5 (cell 308 untouched) is enforced as specified.
7. **Recommendation (only):** **approve the access path for the read-only 8a audit and the 8b verdict only**. Decide
   the 9 h windows after the 8b verdict. In parallel, ask whether a **dedicated** host is available: on the shared
   worker every non-root workload can end the single attempt (OD-R2-5 (i)).
8. **Decide now?** Audit access: **yes**. The windows: **after the 8a/8b evidence**.

## OD-R2-4: host changes needing consent (the owner's and the cell-308 operator's)

1. **Source:** packet §OD-R2-4, lines 174–215.
2. **Why it exists:** a durable, isolated P309 run needs host mutations on a host shared with cell 308 (message 3 §6).
3. **Evidence:** the five mutations listed in the packet; the unit's limits (P20); the six unit properties the runner
   checks and the seven it only records; cell-308 identification data (`foreign_uids`, heavy patterns) from the
   cell-308 operator; the isolation rule that a world-readable cell-308 checkout fails.
4. **Explicit options:** consent to each of mutations 1–5 individually, plus the unit limit values, or decline each.
5. **Consequences:**
   - mutation 1 (P309 user), 2 (≥ 40 GB volume or quota), 3 (polkit rule for `p309-r2-*` units) and 5 (private
     CPython 3.11.15) are P309-only;
   - mutation 4 (hold automatic reboots and upgrades per window) is **host-wide** and affects cell 308 too;
   - declining 3 means the launcher cannot start its unit. Declining 4 leaves the r1 failure class (a reboot during
     QC-D5) open;
   - without the cell-308 uids and patterns, detection relies on command lines and the unattributable rule.
6. **Invariant-preserving:** all, if the cell-308 operator consents to 4 and to the limits (I5).
7. **Recommendation (only):** consent to 1, 2, 3 and 5. Consent to 4 **only together with** the cell-308 operator, for
   the agreed windows. Ask the operator for the uids and job patterns before the 8a audit is judged.
8. **Decide now?** **After** the 8a audit shows the host's state (world-readability, updater configuration,
   capacity). The request to the cell-308 operator can be made now.

## OD-R2-5: interference policy

1. **Source:** packet §OD-R2-5, lines 219–291. Owner message 3 §3 and §8.
2. **Why it exists:** what happens when other heavy work appears during the single attempt.
3. **Evidence:**
   - the start and run thresholds table;
   - detection takes up to about 80–90 s, termination after detection is immediate;
   - "unattributable" covers every other non-root uid whose working directory P309 cannot read;
   - the hardening branch makes a Q-HOST abort durable and classifiable (`ABORTED`, crash case C13), and an
     interruption inside the abort is classified INTERRUPTED (C14), never a pass.
4. **Explicit options:**
   - (i) a heavy start during the run ends the attempt, with Q-HOST FAIL (current code);
   - (ii) r2 continues at idle priority. This needs the owner to amend message 3 §3, a code change and a re-review.
5. **Consequences:**
   - (i): matches §3 and §8 as written, but any third party can consume r2's only attempt, so windows must be agreed
     for the whole host;
   - (ii): fewer lost attempts, but it conflicts with the current strict-isolation instruction.
6. **Invariant-preserving:** both preserve I1–I6. (i) also preserves message 3 as written.
7. **Recommendation (only):** **(i)**, with whole-host window agreement and, preferably, a dedicated host (see
   OD-R2-3). This keeps the single attempt clean and needs no amendment.
8. **Decide now?** **Yes** for the policy. The window agreement follows the 8a audit.

## OD-R2-6: the target-execution host (separate from the qualification host)

1. **Source:** packet §OD-R2-6, lines 295–335.
2. **Why it exists:** approving a qualification host must not silently approve a target-execution host.
3. **Evidence:**
   - execution may take about 31.5 h at 4 workers; after the marker, any OOM, kill, reboot or host loss means
     `EXECUTION_INDETERMINATE` and consumes the single evaluation (A22);
   - execute and seal-only are not gated by the launcher, gate or Q-HOST, so the bytes support execute only on a
     host running no other campaign;
   - the runtime is pinned: interpreter sha256 and glibc must match the freeze host;
   - the frozen parameters name no execution host unless an OD-R2-6 answer exists at the freeze;
   - QC10's 48 certificates are reproducible across hosts (recovery evidence).
4. **Explicit options:**
   - the execution host is (a) the qualification host, (b) a dedicated host, or (c) the shared worker with a further
     reviewed amendment;
   - also to decide: whether QC10's host re-run is repeated immediately before any grant;
   - and whether the frozen field may name a host before OD-R2-6 is answered.
5. **Consequences:**
   - (a) on a shared worker needs a 31.5 h exclusive window and host-wide reboot holds;
   - (b) needs a byte-identical interpreter and glibc (or a re-freeze), and a QC10 host re-run there;
   - (c) needs code, a delta review and a re-drill.
6. **Invariant-preserving:** all. None authorizes execution (I1, I2).
7. **Recommendation (only):**
   - **Defer the choice of host** until after a passed qualification. **Freeze with "no host proposed"** (the
     current default).
   - **Require the QC10 host re-run** immediately before any grant, on whichever host is later named.
   - Lean to (b), a dedicated single-tenant host, for the 31.5 h single-shot execution.
8. **Decide now?** The deferral and the QC10 re-run rule: **yes**. The host itself: **later**, with more evidence
   (the host's audit and its runtime match).

## Proposed additional decision (not in the packet): OD-R2-H, adopting the runtime hardening

This decision is a recommendation only.
- **Question:** should the r2 package that is frozen include the qualification-runtime hardening on
  `claude/p309-r2-hardening-20261005` (H1–H5, `R2_QUALIFICATION_HARDENING_REVIEW.md`), after r2's own independent
  delta review of it?
- **Options:** (a) adopt via review; (b) freeze r2 as shipped; (c) commission a different hardening.
- **What the finished runs established:**
  - **Fixes:** the hardening fixes R01, R05, R07 and R09 in `R2_FAILURE_MATRIX.json`. R02–R04 move from UNSAFE to
    SAFE_BUT_UNPROVEN.
  - **Passes:** r2's QC11, QC12, QC-D5 (controls, backstop, pins) and host tests, the same as on r2.
  - **But it is not adoptable as is:**
    - (i) **R17**: it fails r2's own static control T14a. The control's anchor includes the comment `# exclusive` on
      the attempt-`mkdir` line, which the hardening extended. Fix: restore that comment (comment only);
    - (ii) **R18**: it must be adopted as the **single file** `code/p309_qualify.py` applied onto r2, never as a
      merge of the hardening branch. The branch's guard and tools would fail QC15 A7.
- **Consequences:**
  - (a): the hardening changes only `code/p309_qualify.py` (no pinned function, no gate logic). Adoption is that
    file with the T14a comment restored, then r2's delta review, then a re-drill;
  - (b): accepts torn or empty records on a crash (the attempt is lost, fail closed), and a second start over an
    orphan RUN START. In the matrix, S06 shows this as a real exactly-once gap;
  - (c): its own cost.
- **Recommendation (only):** **(a)**, with the T14a comment restored, as a single-file delta onto r2.
- **Decide now?** The owner can commission the delta review now. Adoption itself comes after that review.

## Proposed owner action (not an OD in the packet): F-DRILL-ORDER

r2's drill topology (`code/p309_topology_drill.py`, `make_topology`) generates the freeze manifest before the
parameters. A worker-tier drill (8d) would therefore refuse at the runner's own manifest precondition.
- It is **left for owner action**, and is still blocking for the 8d drill. It lies outside the hardening's write-set
  and does not affect the runtime or a real freeze.
- The one-line fix (swap two generator calls) is in `R2_QUALIFICATION_HARDENING_REVIEW.md` §5.
- **Recommendation (only):** include it in the same r2 delta review as OD-R2-H.

## Consolidated table

| OD | question | options | recommended option (recommendation only) | evidence | consequence | owner action |
|---|---|---|---|---|---|---|
| OD-R2-0 | authority, carry-over, liabilities; authorize r2's freeze + single qualification? | (A) confirm record; (B) confirm carry-over; (C) acknowledge liabilities; (D) authorize / decline | confirm A, B; acknowledge C (+ recovery-session events); **do not authorize D yet** | verbatim msgs 1–4 with sha256; carry-over table; recovery branch `290b6c10`; baseline matrix | D authorizes the one attempt; with r2 as shipped a crash can lose it or allow a second start | answer A–C now; answer D after OD-R2-H, the delta review and the 8d drill |
| OD-R2-1/1b | r2's production names and bindings | (b) own names; (a) r1's names; (c) other | **(b)**, confirm four bindings | implemented; reviewed; QC12 T12 passes | (b) no code; (a)/(c) code + review + re-drill | decide now |
| OD-R2-2 | marker / pending names; D5 extension to r2's two sites | ratify; other names / decline | **ratify** | AST pins unchanged; QC-D5 pins all current post-freeze; hardening keeps pins | ratify: no code; else review + re-drill | decide now |
| OD-R2-3 | qualification host access path, session, windows | approve shared-AWS session as specified; decline; (implied) dedicated host | **approve for the 8a audit + 8b verdict only**; ask about a dedicated host | r2 procedure 8a–8d; IMDS-dependent preflight; measured gate durations | audit may start; nothing frozen; a non-cloud host needs a code change | approve audit access now; windows after 8b |
| OD-R2-4 | host mutations 1–5 and unit limits (owner + cell-308 operator) | consent / decline each | 1, 2, 3, 5 yes; 4 only with the operator, per window | packet list; isolation rule; uids/patterns needed | 4 is host-wide; without 3 no launch; without 4 the reboot class stays open | request the operator's data now; consent after the 8a audit |
| OD-R2-5 | interference during the single attempt | (i) Q-HOST FAIL ends it; (ii) idle priority (needs amendment) | **(i)** + whole-host windows, preferably a dedicated host | thresholds; detection about 80–90 s; abort durable (C13/C14) | (i) a third party can consume the attempt; (ii) conflicts with msg 3 §3 | decide now |
| OD-R2-6 | target-execution host; QC10 re-run before grant; may the freeze name a host | (a) qualification host; (b) dedicated; (c) shared + amendment | **defer the host**; freeze with no host; **require the QC10 re-run** before any grant; lean (b) | 31.5 h single shot; runtime pin; execute ungated; QC10 reproducible | (b) needs an identical runtime + re-run; (c) code + review | decide the deferral now; the host later |
| OD-R2-H (proposed) | adopt the runtime hardening before the freeze? | (a) adopt via review; (b) freeze as shipped; (c) other | **(a)** as the single file, with the T14a comment restored | baseline vs hardened matrix; unit tests; regression (T14a the only difference); AST diff | (a) delta review + re-drill; (b) known evidence-loss and exactly-once gaps | commission the delta review |
| F-DRILL-ORDER (proposed action) | fix the drill's generator order? | fix via review; leave | **fix** in the same delta review | first matrix run; r1 F manifest | until fixed, the 8d worker-tier drill refuses at launch | include in the delta review |
