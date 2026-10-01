# Owner instruction for P309-r2, message 4 (VERBATIM; received 2026-10-01 during cloud-tier drill attempt 4)

This record holds the owner's overnight message verbatim, in one fenced block, with its sha256 below it. The hash
follows addendum 2, F10: it covers the body without the newline that precedes the closing fence.

* **Why a separate file.** `OWNER_INSTRUCTIONS_R2_VERBATIM.md` (messages 1–3) is immutable under self-audit A3, so
  this message gets its own immutable file rather than an append.
* **Why it was recorded late.** The message arrived while drill attempt 4 required the repository to stay
  unchanged (F2, and this message's own prohibition 14), so it was recorded after that drill ended.
* **Redaction.** Nothing is redacted.
* **What it authorizes.** It authorizes decision-independent overnight work only. It decides none of OD-R2-0 …
  OD-R2-6, and it authorizes no freeze, qualification, grant or target evaluation (its prohibitions 1–7).

## Message 4

```text
You are authorized to continue working autonomously on P309-r2 for the rest
of this overnight session, subject to the hard boundaries below.

PRIMARY OBJECTIVE
=================

Advance P309-r2 as far as safely and legitimately possible overnight,
starting from the current state at commit 93b41bd9 and the currently running
cloud-tier drill attempt 4.

The desired stopping point is:

    READY_FOR_OWNER_DECISIONS

meaning that all decision-independent implementation, testing, evidence
preservation, independent review, review-driven repairs, and permitted
revalidation that can be completed in this Cloud Session have been completed,
and the remaining blockers genuinely require owner decisions and/or access
to the AWS worker.

Do not stop merely because one intermediate task finishes.
Continue autonomously through the permitted sequence below.

However, do not cross any owner-decision, freeze, qualification, grant,
production-ref, or target-evaluation boundary.


CURRENT FACTS TO PRESERVE
=========================

Treat the following as hard current-state facts unless direct repository
evidence proves otherwise:

- P309-r1 is historical and immutable.
- The r1 branch remains at c902fe2f.
- The r1 operative tree must remain unchanged.
- P309-r2 is on branch:
    claude/p5y-k5-cell309-p309-r2
- Current pushed r2 head before attempt 4:
    93b41bd9
- Attempt 4 is currently running.
- HOST_SUITABILITY_PENDING.
- This Cloud Session is not an acceptable official execution host.
- The AWS worker has not yet been audited from this session.
- Cell 308 must not be modified or interrupted.
- NEW Γ309 TARGET EVALUATIONS = 0.
- No production-namespace ref exists.
- No grant exists.
- No target marker or pending-result ref exists.
- r5 is unchanged and there is no r6.

Preserve these facts unless an explicitly authorized later step changes them.


HARD PROHIBITIONS
=================

Throughout this overnight run:

1. DO NOT perform any Γ309 target evaluation.

2. DO NOT create, update, delete, or otherwise mutate any production
   namespace ref for P309-r1 or P309-r2.

3. DO NOT create a grant, execution authorization, target marker,
   pending-result ref, adoption record, r6, or closure claim.

4. DO NOT freeze P309-r2.

5. DO NOT run the official qualification.

6. DO NOT infer owner authorization from this overnight instruction.

7. DO NOT make any decision reserved for OD-R2-0 through OD-R2-6.

8. DO NOT access, modify, interrupt, kill, pause, reprioritize, checkout,
   reset, clean, or otherwise disturb cell 308 or its repository/worktree,
   evidence, refs, processes, jobs, or campaign state.

9. DO NOT attempt to reach the retired Vultr worker or its former IP.

10. DO NOT weaken a gate, scanner, invariant, mutant, review requirement,
    qualification condition, evidence requirement, or fail-closed rule merely
    to obtain PASS.

11. DO NOT erase or rewrite failed attempts.
    Preserve failures and corrections additively.

12. DO NOT rewrite or retroactively modify r1 history.

13. DO NOT use the Cloud Session itself as an official durable host.

14. DO NOT perform repository writes while a drill whose F2/confinement
    contract requires the repository to remain unchanged is running.

15. DO NOT push with force.

If progress requires crossing any of these boundaries, stop that path and
record the exact blocker instead.


PHASE 1 — FINISH ATTEMPT 4
==========================

Allow cloud-tier drill attempt 4 to finish without changing the repository
while its unchanged-repository invariant is active.

Do not commit, push, edit tracked files, generate tracked reports, or otherwise
change HEAD/refs/status while the drill is running.

Scratchpad work outside the repository is allowed.

When attempt 4 finishes, independently inspect the complete evidence.

Require explicit evidence for at least:

- all expected drill items;
- post-freeze QC11;
- topology witness;
- both R2-M01 mutants;
- all required controls;
- host-function tests;
- QC12 T1-T13 where applicable;
- scanner;
- confinement;
- F2 repository invariance;
- F4 complete ledger preservation/export;
- the new ledger-survival check;
- expected ledger row counts and ordering;
- synthetic F'/FR' topology;
- absence of production-namespace refs;
- r1 tree unchanged;
- NEW Γ309 TARGET EVALUATIONS = 0.

Do not call attempt 4 PASS merely because subprocess exit codes are zero.
Validate the evidence itself.


PHASE 2 — IF ATTEMPT 4 FAILS
============================

If attempt 4 fails:

A. Preserve the failure exactly and additively.

B. Determine whether the failure is:
   - a genuine r2 scientific/qualification defect;
   - a governance/integrity defect;
   - an evidence-preservation defect;
   - a drill-only infrastructure defect;
   - an environmental/cloud-container limitation;
   - or an operator/coordinator mistake.

C. Reproduce and diagnose the defect using the smallest safe non-target test.

D. Fix only what is justified by the diagnosis.

E. Add or strengthen a regression control whenever reasonably possible.

F. Refresh affected pins and scanner registrations mechanically.

G. Run the relevant narrow tests first.

H. If the fix affects the behavior or evidence contract exercised by the full
   cloud-tier drill, run another complete cloud-tier drill.

You are authorized to run additional DEVELOPMENT / CLOUD-TIER drills as needed
overnight, provided they:
- cannot evaluate Γ309;
- cannot mutate production refs;
- cannot touch cell 308;
- remain within the existing r2 governance;
- preserve every failed attempt;
- and do not require an owner decision.

Do not cap the number of development attempts artificially.
But do not rerun blindly: every rerun after a failure must have a documented
reason showing what changed and why another full run is necessary.

If a failure reveals that the accepted plan/addenda are no longer sufficient,
stop implementation on that affected path and obtain the required independent
review rather than silently changing the contract.


PHASE 3 — CLOSE CLOUD-TIER EVIDENCE
===================================

Once a complete cloud-tier attempt passes:

1. Preserve its full evidence.

2. Verify P8(a):
   all non-campaign-namespace pins required to remain equivalent to r1 F.

3. Verify P8(b):
   reverse substitution for relocation-only files reproduces the expected r1
   bytes exactly.

4. Verify P8(c):
   perform the completeness scan for residual r1 tokens/references and classify
   every remaining occurrence.

5. Verify P8(d):
   compare frozen-parameter semantics against r1 F and explicitly classify
   every difference.

6. Confirm that no scientific parameter changed unless such a change was
   explicitly authorized by the accepted r2 plan.

7. Refresh and publish the final re-pin list.

8. Finalize the implementation report.

9. Finalize the delta-review brief.

10. Commit these artifacts only after all checks that require repository
    immutability have finished.

11. Push using an explicit non-force refspec.

12. Verify the remote branch points to the expected commit.

After the push, verify again:
- clean working tree;
- r1 unchanged;
- production namespaces empty;
- NEW Γ309 TARGET EVALUATIONS = 0.


PHASE 4 — INDEPENDENT DELTA REVIEW
==================================

Issue the committed delta-review brief to a fresh independent reviewer.

The reviewer must evaluate the actual committed bytes and evidence, not merely
the coordinator's summary.

Ask it to assess at least:

- all binding P1-P23 conditions;
- F1-F11;
- QC11 post-freeze repair;
- sandbox-base rule;
- both mutants;
- namespace prohibitions;
- r1 immutability;
- scratch-root portability;
- host package and Q-HOST;
- shared-host exclusion semantics;
- isolation semantics;
- launcher behavior;
- drill topology;
- confinement;
- complete ledger preservation;
- F2 and F4;
- scanner coverage;
- QC12 T11-T13;
- pin refresh;
- P8(a)-(d);
- all disclosed failed development attempts;
- whether any scientific behavior changed;
- whether any new owner decision was implicitly made.

Preserve the review verbatim before acting on it.


PHASE 5 — REVIEW-DRIVEN REPAIR LOOP
===================================

If the delta review is ACCEPTED with conditions that do NOT require owner
decisions:

- translate every condition into an explicit checklist;
- implement the minimal justified repairs;
- add regression tests/controls;
- refresh affected pins;
- rerun the smallest sufficient validation first;
- rerun the full cloud-tier drill if the changed bytes affect anything bound
  by the drill;
- preserve all prior evidence;
- commit and push additively;
- obtain a fresh follow-up independent review.

Repeat this review/repair/revalidation loop as necessary overnight.

Do not declare a condition satisfied merely because you believe it is minor.
Provide mechanical evidence wherever possible.


PHASE 6 — AWS PREPARATION WITHOUT AWS ACCESS
============================================

Because this session cannot reach the AWS worker, complete every
decision-independent preparation that can be done locally without pretending
the host has been audited.

Prepare/finalize, as applicable:

- the read-only AWS host-audit invocation;
- bootstrap instructions;
- required CPU/RAM/disk/runtime checks;
- cloud identity and reboot/durability observations;
- systemd requirements;
- scratch-root requirements;
- separate-P309-user requirement;
- isolation checks;
- cell-308 visibility checks;
- heavy-worker exclusion checks;
- stale-worker checks;
- launch-record format;
- Q-HOST continuity checks;
- 60-second monitoring semantics;
- fail-closed behavior;
- evidence export procedure;
- cleanup procedure that does not touch cell 308;
- exact instructions for a future AWS-side P309 session.

Do not fabricate HOST_SUITABLE.

The only valid current host status remains:

    HOST_SUITABILITY_PENDING

until the real AWS worker is actually audited.


OWNER-DECISION BOUNDARY
=======================

After all permitted work above is complete, stop before any action requiring
OD-R2-0 through OD-R2-6.

Prepare a concise OWNER_DECISION_PACKET containing:

OD-R2-0
- the complete carry-over table;
- all historical liabilities requiring acknowledgment;
- the exact requested authorization concerning r2 freeze and its single
  official qualification.

OD-R2-1 / OD-R2-1b
- proposed r2 production ref namespace;
- grant path;
- grant campaign name;
- result path;
- result schema name;
- alternatives, if any;
- exact consequences of each choice.

OD-R2-2
- proposed pending-result and marker names;
- exact semantics and collision checks.

OD-R2-3
- exact AWS access-path requirement;
- what the future AWS-side session must do;
- what it must not do;
- required exclusive heavy-compute window.

OD-R2-4
- every host change, if any, that would require owner consent;
- distinguish read-only audit from host mutation.

OD-R2-5
- clearly present the allowed scheduling choices;
- explicitly note that allowing r2 to continue at low priority while cell 308
  runs heavy work conflicts with the owner's existing strict-isolation
  instruction unless the owner amends it;
- do not choose on the owner's behalf.

OD-R2-6
- separately address whether the shared AWS worker should be used for eventual
  target execution;
- qualification-host approval must NOT automatically imply target-execution
  host approval;
- include the current estimate of approximately 31.5 hours and the durability
  implications;
- do not choose on the owner's behalf.


OVERNIGHT RESOURCE POLICY
=========================

Use this Cloud Session efficiently.

You may:
- run non-target development tests;
- run cloud-tier drills;
- use fresh independent reviewers;
- repair implementation defects;
- regenerate development evidence;
- perform static analysis;
- perform equivalence checks;
- prepare AWS-side tooling and documentation;
- commit and push legitimate additive r2 work.

Prefer productive independent work while long tests run, but never write to
the repository while a running test explicitly requires repository
immutability.

Do not repeatedly poll long jobs at very short intervals.
Use bounded waits/checkpoints.

Do not run expensive work merely to consume the night.
Every expensive rerun must answer a concrete unresolved validation question.


FAIL-CLOSED RULE
================

If you encounter ambiguity involving:
- target exposure;
- owner authorization;
- production refs;
- freeze semantics;
- exactly-once semantics;
- scientific parameter changes;
- r1 immutability;
- cell-308 interference;
- host mutation;
- evidence loss;
- or whether an action would consume an official attempt,

choose the non-consuming, non-mutating interpretation and stop that path.

Continue other independent safe work where possible.


FINAL OVERNIGHT REPORT
======================

Before ending the overnight session, produce and, where permitted by the
accepted governance, commit/push an additive overnight report containing:

1. starting commit;
2. ending commit;
3. every commit created overnight;
4. every push performed;
5. every drill/rehearsal attempted;
6. PASS/FAIL outcome of each;
7. every defect discovered;
8. every repair made;
9. every independent review and verdict;
10. every remaining review condition;
11. P8(a)-(d) status;
12. scanner/QC12/control status;
13. host status;
14. AWS readiness status;
15. r1 immutability check;
16. cell-308 untouched check;
17. production-ref scan;
18. grant/marker/pending-result status;
19. NEW Γ309 TARGET EVALUATIONS count;
20. exact remaining blockers;
21. whether the campaign is READY_FOR_OWNER_DECISIONS.

Use explicit final labels such as:

CLOUD_TIER_VALIDATION = PASS / FAIL / INCOMPLETE
DELTA_REVIEW = ACCEPTED / CONDITIONAL / REJECTED / NOT_RUN
HOST_SUITABILITY = PENDING
R1_IMMUTABLE = YES / NO
CELL308_UNTOUCHED = YES / NO
PRODUCTION_REFS_CREATED = 0
NEW_GAMMA309_TARGET_EVALUATIONS = 0
READY_FOR_OWNER_DECISIONS = YES / NO

Do not use "scientifically closed", "cell 309 closed", "adopted", or equivalent
language unless those conclusions have actually been reached through the
authorized later protocol. They have not been reached merely by completing
this overnight work.

Continue autonomously until:
(a) READY_FOR_OWNER_DECISIONS is legitimately reached;
(b) only AWS access / owner decisions remain;
(c) a governance boundary requires the owner;
(d) an unresolved safety/integrity issue makes further work inappropriate;
or
(e) the session/runtime ends.

Do not stop just to ask whether you should continue with an already-authorized,
decision-independent step.
```

sha256: `de3c8e44351e669471d2fa29499eb70717395a22fafc1bd38d61c4e9c979cc56` (bytes: 14621)
