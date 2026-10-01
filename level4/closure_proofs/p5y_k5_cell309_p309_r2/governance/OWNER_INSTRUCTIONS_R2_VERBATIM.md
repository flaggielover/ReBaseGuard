# Owner instructions for P309-r2 (VERBATIM; received 2026-10-01 in the coordinating cloud session)

This record satisfies plan-review condition P1. It holds three owner messages, each reproduced verbatim inside a fenced
block. The sha256 of each fenced body, taken over the exact bytes between the fence lines, is listed after it.

**One disclosed redaction.** In message 2 the owner named the retired worker's IP address. The owner marked that
address RETIRED/UNTRUSTED ("Do not connect to, probe, authenticate to, or use that IP"), and the coordinator had said
it would not record the address in r2 material. The address is therefore replaced by
`[RETIRED-WORKER-IP-REDACTED]`, and the sha256 is of the redacted body. Nothing else was changed.

The session does not expose a transcript uuid or timestamp for these messages. They were received in order, on
2026-10-01, after the r1 morning report (r1 head `c902fe2f`).

## Message 1: the r2 directive

```text
Continue autonomously from the final P309-r1 postmortem and overnight report.

The immediate goal is to design and, where governance permits, prepare a fresh successor campaign for cell 309:

    p5y_k5_cell309_p309_r2

The primary operational constraint has changed:

My local Mac/VLESS connection has exhausted its traffic allowance. Minimize all traffic that needs to pass through my local machine. This Claude Cloud Session should remain the control/research environment, while heavy computation should be moved to the existing Vultr server whenever that can be done safely and without weakening the scientific/governance guarantees.

Do NOT treat r2 as a retry or continuation of the failed r1 official qualification.

============================================================
0. NON-NEGOTIABLE SCIENTIFIC / GOVERNANCE STATE
============================================================

Preserve the final r1 facts exactly:

- P309-r1 ended at QUALIFICATION_FAILED.
- F exists at:
  4c754a73767903a5ad5dddff725f1e173a0a6876
- FR exists at:
  2f66bc566bcc67402d883513474c1f04acbeb108
- r1 cannot be repaired, resumed, or requalified in place.
- A27 remains binding for r1.
- NEW Γ309 TARGET EVALUATIONS = 0.
- No production marker exists.
- No pending-result ref exists.
- No grant exists.
- No r6 exists.
- r5 remains unchanged.
- Cell 309 remains OPEN.
- Cell 308 must remain untouched.
- Do not reinterpret the failed qualification as scientific evidence about Γ309.

The r1 failure was qualification/infrastructure failure, not a scientific result.

Do not mutate or rewrite historical r1 evidence, reviews, freeze records, qualification evidence, postmortem records, or adjudications.

============================================================
1. R2 SCOPE
============================================================

Create/design r2 as a fresh successor campaign whose initial scope is narrowly:

    qualification infrastructure + execution-host durability

Do NOT change the P309 scientific route merely because r1 qualification failed.

In particular, unless an independent review establishes that a scientific change is necessary, preserve the scientific object inherited from the accepted r1 pre-freeze candidate:

- SRK route/science;
- supply definitions;
- closure criterion;
- mathematical inequalities;
- target definition;
- Γ309 definition;
- target interval/cell identity;
- scientific producer/verifier semantics.

Any unavoidable byte-level changes caused solely by host portability must be classified explicitly as infrastructure/platform changes and reviewed for scientific equivalence.

If a proposed change affects scientific output, stop and classify it before implementing it.

============================================================
2. CLOUD SESSION / VULTR ARCHITECTURE
============================================================

Use this Claude Cloud Session as the control plane:

- repository inspection;
- protocol/governance drafting;
- code changes;
- reviews;
- Git/GitHub operations;
- evidence inspection;
- orchestration;
- lightweight tests.

Use the existing Vultr server as the candidate compute/execution plane for:

- long decoy computations;
- QC08/QC09/QC10-class workloads;
- post-freeze-topology rehearsals;
- qualification rehearsals;
- eventually the official r2 qualification, but ONLY after the new r2 protocol, reviews, freeze and authorization state permit it.

Do not route bulk experiment artifacts through my Mac.

Prefer:

    Claude Cloud Session <-> GitHub
    Claude Cloud Session <-> Vultr
    Vultr <-> GitHub

rather than:

    Vultr -> Mac -> GitHub
or
    Cloud -> Mac -> Vultr.

My Mac should be treated only as an interactive client and must not be required to remain connected for long computations.

============================================================
3. FIRST TASK: READ-ONLY VULTR AUDIT
============================================================

Before installing, modifying, deleting, cloning, or executing anything substantial on Vultr, perform a READ-ONLY audit.

Determine and report:

- hostname;
- OS/distribution/version;
- architecture;
- CPU model;
- vCPU count;
- total/free memory;
- swap;
- filesystem and free disk;
- Python versions;
- git version;
- relevant compiler/runtime versions;
- current load;
- uptime;
- evidence of recent reboots;
- process/session persistence facilities available:
  - systemd
  - tmux
  - screen
  - setsid/nohup
- kernel/OOM history if readable;
- automatic update/reboot configuration if readable;
- whether the server is a VM/container and any evidence of provider-initiated lifecycle events;
- repository state if ReBaseGuard is already present;
- exact origin URL;
- branches/commits currently present;
- whether any unrelated ReBaseGuard computation is running.

Do not expose credentials, tokens, private keys, or secret values in the report.

Do not change the server during this audit.

============================================================
4. HOST SUITABILITY GATE
============================================================

Compare Vultr against the observed P309 workload.

The previous qualification required approximately 5.7–5.9 hours end-to-end and included multi-worker CPU-heavy decoy stages.

Assess whether Vultr has enough:

- CPU;
- RAM;
- disk;
- runtime stability;
- process persistence;
- thermal/resource stability where applicable;
- lifecycle durability.

Do not merely say "it should work."

Create an explicit host-suitability result:

    HOST_SUITABLE
or
    HOST_NOT_SUITABLE
or
    HOST_SUITABILITY_PENDING

with evidence.

If CPU/RAM are inadequate, stop before expensive work and tell me the minimum practical Vultr configuration you recommend.

Do not silently weaken worker counts, caps, tests, scientific workload, or qualification requirements merely to fit the server.

============================================================
5. R1 FAILURE REPAIR REQUIREMENTS
============================================================

r2 must explicitly address BOTH r1 failure classes.

A. QC11 POST-FREEZE TOPOLOGY BUG

r1 QC11 failed because its sandbox inherited the real freeze record from current HEAD, producing two freeze-record commits and causing the driver to refuse.

For r2:

- identify the exact root cause;
- design the minimal repair;
- ensure test sandboxes are constructed from the intended frozen base rather than accidentally inheriting the live freeze record;
- add a mutant/control that restores the old r1 behavior and MUST be caught;
- prove that exactly one freeze record exists in the intended test topology;
- ensure the production path is not weakened.

B. HOST DURABILITY

r1 was also interrupted by a host reboot during QC_D5.

Before any r2 official qualification:

- define a host-durability gate;
- determine how long the host must remain continuously usable;
- make the official runner independent of my Mac connection;
- use an appropriate detached/persistent execution mechanism;
- record boot identity / uptime / relevant host provenance;
- define fail-closed behavior for a reboot or environment replacement.

Do NOT introduce qualification retry/resume merely for convenience unless a new governance review explicitly permits it.

============================================================
6. POST-FREEZE REHEARSAL REQUIREMENT
============================================================

Before r2 freezes for its official qualification, construct a non-target rehearsal that reproduces the relevant POST-FREEZE repository topology.

It must exercise at minimum:

- QC11;
- QC_D5;
- freeze-record discovery;
- sandbox construction;
- frozen-commit resolution;
- checkpoint/ledger behavior;
- host provenance checks.

The purpose is specifically to prevent another case where:

    pre-freeze tests PASS
    but
    the first real post-freeze topology reveals a harness bug.

Use decoys/synthetic state only.

NEW Γ309 TARGET EVALUATIONS must remain 0.

============================================================
7. TARGET-INTEGRITY RULE
============================================================

Throughout all r2 preparation:

- do not evaluate Γ309;
- do not inspect a target-equivalent proxy;
- do not create a production target marker;
- do not create a pending-result ref;
- do not create a grant;
- do not modify r5/r6;
- do not touch cell 308;
- do not create a path by which a test accidentally reaches the target.

Maintain an explicit running counter:

    NEW Γ309 TARGET EVALUATIONS = 0

and verify it periodically from committed evidence, not merely by assertion.

============================================================
8. TRAFFIC-MINIMIZATION RULE
============================================================

Because local proxy traffic is exhausted:

- do not download large experiment artifacts to my Mac;
- do not require my Mac to proxy SSH, Git, package downloads or experiment data;
- keep bulk artifacts on Vultr and/or GitHub where governance permits;
- transfer summaries, hashes and compact evidence rather than large raw files when sufficient;
- avoid repeatedly recloning large repositories;
- avoid redundant package downloads;
- avoid moving large decoy outputs between Cloud Session and Vultr unless required by the protocol.

Do not sacrifice required evidence or reproducibility just to save bandwidth.

If a required operation would transfer a large amount of data through my local machine, stop and report the expected transfer before doing it.

============================================================
9. GIT / BRANCH SAFETY
============================================================

Do not mutate the historical p309-r1 branch.

Prepare a distinct r2 branch/worktree/namespace.

Before creating it, inspect the authoritative remote state and determine the correct r2 base commit.

Do not assume that main is the correct base.

Record:

- base commit;
- ancestry;
- branch name;
- remote;
- namespace boundaries.

Do not merge r1 history into unrelated branches merely to make histories look synchronized.

============================================================
10. AUTONOMY
============================================================

You may autonomously perform:

- read-only audits;
- drafting;
- non-target code repair;
- non-target tests;
- decoy/synthetic tests;
- independent reviews;
- Git commits/pushes where existing project governance permits them;
- Vultr setup after the read-only audit confirms the intended paths are safe;
- host qualification/rehearsal work that does not cross a governance decision boundary.

STOP and ask me before:

- any Γ309 target evaluation;
- any production target marker;
- any grant;
- any change to r5/r6;
- any scientific-route change that is not demonstrably infrastructure-only;
- any destructive operation whose scope is uncertain;
- any action that existing governance explicitly reserves for owner authorization.

If r2 eventually reaches:

    READY_FOR_OWNER_GRANT_DECISION

stop there and report it.

Do not infer authorization from this prompt.

============================================================
11. IMMEDIATE EXECUTION ORDER
============================================================

Proceed now in this order:

1. Re-read the final r1 overnight report and postmortem.
2. Verify target integrity and authoritative Git state read-only.
3. Perform the read-only Vultr audit.
4. Produce the host-suitability verdict.
5. Define the minimal r2 scope and branch/base.
6. Design the QC11 repair.
7. Design the post-freeze-topology rehearsal.
8. Design the host-durability gate.
9. Obtain fresh independent review of the r2 plan.
10. Only then begin implementation and non-target validation.

Keep going autonomously through all decision-independent work.

At meaningful checkpoints report:

- current phase;
- exact commit/branch;
- Vultr status;
- tests/reviews passed or failed;
- target-integrity counter;
- whether any owner decision is now required;
- next step.

Do not wait for me merely because a long non-target job is running if useful independent work can safely proceed in parallel.

But do not create work simply to stay busy: once the next action depends on a running qualification/rehearsal or an owner decision, wait.

Start with the read-only authoritative-state and Vultr audit.
```

sha256: `86065859d6b7919f86d6032e367d52243d34ba451bd211761a07f5400dfbb27f` (bytes: 12360)

## Message 2: the retired Vultr worker

```text
Update: the previously recorded Vultr instance no longer exists in my Vultr account.

Treat the old Vultr worker and [RETIRED-WORKER-IP-REDACTED] as RETIRED/UNTRUSTED infrastructure. Do not connect to, probe, authenticate to, or use that IP. Do not assume that the current holder of that IP is our server.

Therefore:
- HOST_SUITABILITY_PENDING remains correct.
- Continue all P309-r2 decision-independent work entirely in this Cloud Session.
- Do not block r2 design/review/implementation work on Vultr availability.
- Separate the compute-host interface from any specific provider or IP so a fresh worker can be provisioned later.
- Prepare a reproducible bootstrap + host-audit + durability-gate package for a future fresh worker.
- Do not run heavy qualification-scale jobs merely to stay busy.
- When r2 reaches the point where a durable external compute host is actually needed, stop and report the required CPU/RAM/disk/runtime characteristics before any heavy run.
- Maintain NEW Γ309 TARGET EVALUATIONS = 0.
```

sha256: `77e344d73093855c6f6371d7fcbb9888ce85bc42f8e66c4751485cf4682ef578` (bytes: 1017)

## Message 3: the shared AWS worker

```text
Update the compute-host plan.

Do not provision a new Vultr worker for P309-r2 for now.

P309-r2 may share the existing AWS ReBaseGuard worker currently used by
cell 308, subject to strict cross-campaign isolation.

Treat this as SHARED HOST / EXCLUSIVE HEAVY-COMPUTE scheduling:

1. Cell 308 and P309-r2 must use separate repositories/worktrees,
   branches, namespaces, temporary directories and evidence directories.

2. Never switch the cell-308 checkout to a P309 branch and never write
   P309 artifacts into the cell-308 campaign namespace.

3. Heavy computation must be mutually exclusive:
   - if a cell-308 heavy job is running, P309-r2 may perform only work
     that does not materially affect host resources;
   - if a P309-r2 heavy job is running, do not start a cell-308 heavy job.

4. Before every P309-r2 rehearsal or qualification-scale run, add a
   cross-campaign exclusion gate that verifies:
   - no cell-308 worker/process is active;
   - no unrelated ReBaseGuard heavy process is active;
   - CPU load has returned to the accepted baseline;
   - sufficient RAM/disk are available;
   - no stale worker processes remain.

5. Record the AWS host identity and prove that sharing the physical host
   does not share campaign state.

6. Do not alter the cell-308 campaign, its checkout, refs, evidence,
   processes or governance state merely to prepare P309-r2.

7. First audit the current AWS worker read-only and determine whether its
   CPU/RAM/disk/runtime characteristics are sufficient for the observed
   ~5.7–5.9 hour P309 qualification workload.

8. If cell 308 currently needs the AWS worker, do not interrupt it.
   P309-r2 waits for an exclusive heavy-compute window.

9. Keep bulk computation and artifacts on AWS/GitHub. My Mac/VLESS must
   not be used as a bulk-data relay.

10. Maintain:
    NEW Γ309 TARGET EVALUATIONS = 0.

Continue all decision-independent P309-r2 work while the AWS host is
occupied. Do not run any Γ309 target computation and do not infer
authorization from this instruction.
```

sha256: `78cd27da6b2ce0059d51e3764d79413de8e7b1d9a6c5e3687f808c8192a36d52` (bytes: 2038)
