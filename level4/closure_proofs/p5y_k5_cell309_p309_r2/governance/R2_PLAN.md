# P309-r2 plan: a fresh successor campaign for cell 309 (qualification infrastructure + execution-host durability)

Status: **PLAN, before independent review.** Nothing below is implemented yet. NEW Γ309 TARGET EVALUATIONS = 0.

## 0. Starting state (verified read-only, 2026-10-01)

**The r1 facts r2 takes over unchanged.**
* `p5y_k5_cell309_p309_r1` ended at **QUALIFICATION_FAILED**.
  * F is `4c754a73767903a5ad5dddff725f1e173a0a6876`.
  * FR is `2f66bc566bcc67402d883513474c1f04acbeb108`.
  * The single attempt failed gate Q11, and a host reboot interrupted it during QC-D5.
  * Postmortem: `p5y_k5_cell309_p309_r1/handoff/QUALIFICATION_FAILURE_POSTMORTEM_P309.md`, reviewed independently
    (POSTMORTEM_DISPUTED on wording only; corrections confirmed).
* A27 binds r1. r1 cannot be repaired, resumed or requalified in place.
* r2 is **not a retry** of r1's qualification. It is a new campaign with its own freeze, its own single qualification
  and its own reviews.
* The r1 failure is a qualification and infrastructure failure. It is **no evidence about Γ309**.

**Integrity at r1's final head `c902fe2f`** (local equals remote):
* 0 campaign or test refs, locally and on the remote;
* no grant anywhere in history;
* the execution ledger has 1421 rows, with 0 target evaluations and 0 proxies;
* the r5 blob is `f978eeb6…` (unchanged), and there is no r6;
* cell 308 is untouched.

## 1. Branch, base and namespace

| item | value |
|---|---|
| branch | `claude/p5y-k5-cell309-p309-r2` (new; the r1 branch is never written again) |
| base | `c902fe2fe33003ac7e4e61f29c10c81682fc940c` (r1's final head) |
| why that base | it holds the reviewed r1 pre-freeze candidate (F's tree), the failed attempt and the postmortem, which r2 cites. `main` (`1cb45382`) holds none of the r1 campaign and is not the base |
| r2 namespace | `level4/closure_proofs/p5y_k5_cell309_p309_r2/` (FNS2). The r2 tooling refuses to change anything outside FNS2 (its checkpoint push checks it). The r1 namespace and the research namespace stay byte-identical |
| remote | `origin` (`flaggielover/rebaseguard`); explicit refspec, never forced |

## 2. Scope (narrow)

r2 changes **only** qualification infrastructure and execution-host durability. The scientific object is inherited
**byte for byte** from r1's reviewed candidate (F's tree):
* the SRK route;
* the supply definitions, the closure criterion and the inequalities;
* the target definition, Γ309, and the cell interval and identity;
* the producer and verifier semantics;
* every research-namespace module and every data pin;
* the budgets, worker counts, the outcome table and the Stage 1a/1b/2 procedures.

**Equivalence proof (mechanical, before the r2 freeze).**
* Every r2 manifest pin outside FNS2 must equal r1's F manifest pin (sha256 and blob).
* For each FNS2 file, the diff against its r1 counterpart is classified (§3) and reviewed.
* A change that could affect any scientific output stops the work and is classified before it is implemented.

## 3. Changes (each classified)

| id | change | class |
|---|---|---|
| **R2-I1** | **Namespace relocation.** Copy r1's candidate files (F's tree: `code/ config/ fc2/ tests/ verify/ start_state/ governance/`) to FNS2, then change only the campaign-path and campaign-name literals: `NS_REL`, `_FNS_REL` (guard, variant), `campaign` (guard, variant, grant schema tests), the manifest generator's `NS_REL`, the scanner and quarantine configs, the checkpoint tool's branch and namespace, and the self-audit lists. The r1 governance documents are copied as the inherited frozen protocol. New r2 text goes in a new append-only `governance/P309_R2_AMENDMENTS.md`. Ledgers start fresh, with a genesis line citing r1's final state | infrastructure (relocation). The AST diff must show changed string constants only. The two site ASTs and the backstop and host-git AST hashes must stay **equal** to the r1 pins |
| **R2-I2** | **Portability.** Five files hard-code this session's scratch path (`p309_qualify.py`, `test_p309_guard.py`, `test_p309_exactly_once.py`, `test_p309_d5_exception.py`, the verifier author's `verify/scoped_sandbox.py`). Replace with one environment variable `P309_SCRATCH_ROOT` and a fixed default (`<repo parent>/p309_r2_scratch`), recorded in every run's evidence | infrastructure |
| **R2-I3** | **QC11 repair: the post-freeze topology** (§4) | infrastructure (test harness) |
| **R2-I4** | **Host provenance and continuity gate** in the QC runner (§6) | infrastructure (runner), plus a new gate Q-HOST: a **rule**, so it is reviewed |
| **R2-I5** | **Post-freeze rehearsal tool** (§5) | infrastructure (development tooling, never qualification evidence) |
| **R2-I6** | **A provider-independent worker package** under FNS2 `host/` (§6, §7) | infrastructure |
| **R2-I7** | **The r2 checkpoint push** (a branch and namespace copy of r1's tool) | infrastructure |
| **R2-B1** | **The production ref namespace** of the inert marker and pending-result names (owner D5) | **binding: owner decision** (§8) |
| **R2-B2** | **D5 ratification for r2:** the two exactly-once sites, with unchanged AST hashes, present in r2's frozen tree | **owner decision** (§8) |
| **R2-B3** | **The execution and qualification host:** the shared AWS worker in an exclusive window (bound by the freeze runtime pins) | **owner decision** (access path and window) (§6, §8) |

The variant's literals (R2-I1) and its sandbox path (R2-I2) are changed **by the verifier author** (role separation),
who reports the AST diff. `verifier_id` changes as a result; the change is classified as infrastructure, by its AST
diff.

## 4. The QC11 repair (R2-I3)

**Root cause (r1 postmortem §3, confirmed independently).**
* `tests/test_p309_exactly_once.py::new_sandbox` sets the sandbox branch to **this repository's HEAD**.
* `build_chain` then adds a synthetic freeze commit and a synthetic freeze-record commit.
* After the real freeze, HEAD's history already holds the real freeze record, so the sandbox has **two**
  freeze-record commits.
* `recorded_freeze` (A24: exactly one) correctly refuses.

The backstop controls reuse that harness. `test_p309_guard.py::new_sandbox` and the verifier's
`scoped_sandbox.Sandbox` also take the live HEAD, but the code under test there never read the freeze record (r1 QC16
passed after the freeze).

**Repair (minimal; the production path unchanged).**
1. A single base rule, `sandbox_base()`, in the QC11 harness:
   * if HEAD holds this namespace's freeze record, the base is `D.recorded_freeze()`, the recorded freeze commit F.
     F's tree carries everything frozen and no freeze record. An invalid record raises, so QC11 fails loudly, as
     QC13 does.
   * otherwise (development) the base is HEAD.
2. The guard harness uses the same rule.
3. The verifier's sandbox is left as is unless the rehearsal (§5) shows sensitivity. Its use is recorded.
4. **Invariant inside `build_chain`:** after building a valid chain, the sandbox has **exactly one** commit touching
   the freeze record. Otherwise the harness raises: fail loud, not refusal-shaped.
5. **Mutant control R2-M01:** a copy of the harness with the old base (`HEAD`) restored, run in the rehearsal's
   post-freeze topology. It **must** fail with the FREEZE_RECORD refusal, which the rehearsal asserts.
6. **Static check:** the QC12 static check gains an assertion that `new_sandbox` takes its base from `sandbox_base()`
   (AST), so the rule cannot silently regress.
7. **Production path:** `recorded_freeze`, `check_grant` and `walk_chain` are unchanged, and their AST hashes are
   pinned and compared.

## 5. The post-freeze rehearsal (R2-I5; development only, never qualification evidence)

**Purpose.** Prevent "pre-freeze tests PASS, but the first real post-freeze topology shows a harness bug".

**Mechanism.**
* A scratch clone of the r2 branch (`git clone --local`, nothing pushed). In it, the tool commits a **synthetic**
  freeze F′ (regenerated manifest and parameters) and its record-only child FR′, exactly as the real freeze will.
* It then runs the QC runner in a `--rehearsal` mode:
  * a scratch attempt directory;
  * every ledger line labelled `REHEARSAL (not qualification)`;
  * the scratch clone's own ledger, never pushed.

**It exercises:**
* freeze-record discovery (`recorded_freeze` on F′/FR′);
* sandbox construction (QC11, QC-D5 backstop, QC16 guard and verifier tests);
* frozen-commit resolution (`mirror(F′)`, QC13 in full);
* checkpoint-record commits after FR′ (the rehearsal makes one, and the chain walk must still accept it);
* QC12 and QC15;
* the host provenance gate (§6).

**Controls:** R2-M01 (§4.5), plus a control that plants a second freeze record and must make QC13 and
`recorded_freeze` fail.

**Two tiers.**
* **(a) Cloud tier**, here: every item except the heavy decoy computations QC06, QC08, QC09 and QC10. About 30–40
  minutes.
* **(b) Worker tier**, on the shared AWS worker in an exclusive window (§6.2): the full item set, as a full-length
  post-freeze dry run. It doubles as the host durability burn-in (§7).

Target integrity: decoys and synthetic state only. The production namespace stays empty, which the rehearsal checks
at the end.

## 6. The compute host: shared AWS worker, exclusive heavy compute (owner instruction, 2026-10-01)

The owner decided that **no new worker is provisioned for now**. P309-r2 may share the existing AWS ReBaseGuard worker
used by cell 308, under strict cross-campaign isolation.

* For r2, and only under these terms, this replaces r1's boundary "do not use the cell-308 machine".
* Cell 308 has priority. P309-r2 never interrupts it and waits for an exclusive heavy-compute window.

**6.1 Isolation (state is never shared, only the physical host).**
* P309-r2 uses its **own full clone** of the repository on the worker, cloned over HTTPS directly from GitHub. It
  never shares an object store with the cell-308 checkout.
* It has its own branch (`claude/p5y-k5-cell309-p309-r2`), its own namespace (FNS2) and its own `P309_SCRATCH_ROOT`.
  Its evidence directories are under FNS2 or that root.
* A separate Unix user is recommended.
* It never switches, reads into, writes or changes the cell-308 checkout, refs, evidence, processes or governance
  files. It reads only process metadata (`/proc`) for the exclusion gate.

**Isolation proof**, recorded by `host/isolation_check.py` before every heavy run:
* the P309 repository's real path, git common dir and `alternates` are disjoint from any cell-308 checkout;
* the scratch and evidence roots are disjoint;
* the P309 repository holds no cell-308 ref and no cell-308 namespace change;
* the cell-308 checkout's HEAD and branch are read-only observed, and identical before and after the run;
* there is no write to any path outside the P309 roots, verified by listing the files the run created.

**6.2 The cross-campaign exclusion gate (`host/exclusion_gate.py`; read-only; before every rehearsal or
qualification-scale run).** It refuses unless:
* **no cell-308 process is active.** No process has a cwd, command line or open file under a cell-308 checkout or
  namespace (`*cell308*`), or matches the cell-308 runner patterns declared in the gate's configuration.
* **no other ReBaseGuard heavy process is active.** No process from any ReBaseGuard checkout other than this P309 one
  is using more than 5 % of one CPU for 60 s.
* **the CPU load is back at baseline.** The 1-minute and 5-minute load averages are ≤ the idle baseline measured at
  audit time plus 0.5, sampled over 3 minutes.
* **resources are available.** Available RAM ≥ 8 GB, and free disk on the P309 roots ≥ 40 GB.
* **no stale P309 worker is left:** no `p309_driver.py _job`, `p309_qualify.py` or rehearsal process.

The gate's JSON output is preserved with the run. While a P309-r2 heavy job runs, a lock file under the P309 roots and
a visible process title (`p309-r2-heavy`) announce it. The cell-308 operator is asked not to start heavy work then;
P309-r2 cannot enforce that on cell 308's side.

## 7. Host provenance and continuity (R2-I4, R2-I6)

**Provenance.** At start, after each QC item and at the end, the runner records:
* `boot_id`;
* sha256 of `/etc/machine-id` and of the hostname;
* the cloud instance identity as a sha256 (read only from the instance metadata service where reachable; never
  stored in clear);
* kernel release, CPU model, vCPU count, total memory;
* the Python executable and version;
* the git version;
* the persistence mechanism (a transient systemd unit, or the setsid session id).

**New gate Q-HOST** (a rule, so it is reviewed). It passes iff:
* every recorded `boot_id`, machine-id hash and instance hash is identical from the start to the summary;
* the runner process is the same;
* the exclusion gate's start state holds: no cell-308 heavy process appeared during the attempt, sampled after each QC
  item.

**Fail-closed.** A reboot or environment replacement kills the runner, so no summary is written. A27-equivalent for
r2: **no retry, no resumption.** A cell-308 heavy process appearing during the attempt fails Q-HOST, and so fails the
attempt. That is why the launch waits for an exclusive window agreed with the cell-308 schedule. **This plan proposes
no retry rule.**

**Preflight (refuses to launch).**
* The exclusion gate (§6.2) and the isolation check (§6.1) pass.
* Automatic reboots are disabled, and no reboot is pending.
* The runtime matches the freeze pins (Python version, platform, `host_id_sha256`).
* `check_host_git` (A40) passes.
* `systemd-run` is available (fallback `setsid` + `nohup`).

**Persistence.**
* `systemd-run --unit=p309-r2-qualification --property=Restart=no --collect`.
* Independent of any interactive connection: the owner's Mac is never in the loop.
* Bulk artifacts stay on the worker and GitHub.

**Durability window.**
* The worker-tier rehearsal (§5b) is the burn-in, on the same `boot_id`.
* The official attempt needs a continuous exclusive window of about 6 h + 50 % ≈ 9 h, agreed against cell 308's
  schedule.

## 8. Worker access, requirements and the read-only audit (R2-B3)

**Access.**
* This cloud session has no SSH client and no keys, and its egress proxy carries HTTPS only. It cannot reach the AWS
  worker directly.
* The access path must not go through cell 308's session or checkout. For example:
  * a **separate** P309 Claude Code session on the worker (`claude remote-control` in the P309 clone, under the P309
    user);
  * or a GitHub-mediated job restricted to the P309 branch.
* The retired Vultr worker is not used, probed or recorded.

`FNS2/host/` holds:
* `HOST_REQUIREMENTS.md`;
* `host_audit.py`: **read-only** JSON; identity values as hashes only, no secrets;
* `BOOTSTRAP.md`: the P309 clone and user on the shared worker; nothing through the owner's Mac;
* `exclusion_gate.py`;
* `isolation_check.py`;
* `durability_preflight.py`;
* `launch_qualification.sh`.

**Requirements** (from r1's measured workload; the r1 attempt's QC01–QC-U2 alone took 5.47 h):

| resource | needed for P309-r2 (exclusive window) | basis |
|---|---|---|
| CPU | ≥ 4 vCPU x86_64 free for the window | frozen worker count ≤ 4; QC08 used 15 461 CPU-s on 4 workers |
| RAM | ≥ 8 GB available | r1 container: about 15 GB of 16 GB stayed available while 4 jobs ran |
| disk | ≥ 40 GB free on the P309 roots | repository about 1.4 GB (482 MB `.git`); attempt about 5 MB; sandboxes, mirror, headroom |
| OS / runtime | Linux with systemd; CPython 3.11.x, the exact patch pinned at the r2 freeze; git ≥ 2.32 | stdlib only; A40 |
| durability | no automatic reboot; not spot or preemptible; an exclusive window of about 9 h | §7 |

**Verdict rule.** The read-only audit of the AWS worker yields **HOST_SUITABLE**, **HOST_NOT_SUITABLE** (with the
minimum practical change) or **HOST_SUITABILITY_PENDING**. It is pending until the audit can run. Because the freeze's
runtime pins bind the host, r2's freeze is generated **on** that worker, in the P309 clone.

## 8A. Owner decisions that r2 needs (stop points)

* **OD-R2-1 (before the r2 freeze; owner D5): the production ref namespace for r2.**
  * **(a) Keep** `refs/p5y-k5-cell309-p309-r1/` (one exactly-once marker for cell 309 across campaigns).
  * **(b) Rename** to `refs/p5y-k5-cell309-p309-r2/`. **Recommended,** with a fail-closed pre-marker rule that the r1
    namespace is also empty (a new, reviewed rule).
* **OD-R2-2 (before the r2 freeze; owner D5): extend D5's ratification** to r2's two sites. Their AST hashes must equal
  `1ee764b7…` and `13ee3ec3…`.
* **OD-R2-3: the access path** to the AWS worker for a separate P309 session, and an exclusive window agreed against
  cell 308's schedule.
* **Not requested:** a grant, any target evaluation, or any change to r5 or r6.

## 9. Review and gate order (as for r1, restarted for r2)

1. Independent review of **this plan** (before implementation).
2. Implementation in the cloud session. Development tests: scan, T1–T10, QC11 (development topology), D5 controls,
   guard, backstop and allowance controls, U2, self-audit.
3. **Cloud-tier post-freeze rehearsal** (§5a), including R2-M01.
4. The verifier author's changes (R2-I1, R2-I2), with their own report.
5. An independent delta review of the r2 changes, an equivalence review, and an R4-style pre-freeze review.
6. Owner decisions OD-R2-1 and OD-R2-2. **Stop.**
7. Access to the shared AWS worker (OD-R2-3): the read-only host audit (§8), then **HOST_SUITABLE** or
   **HOST_NOT_SUITABLE**. In an exclusive window (§6.2), the worker-tier rehearsal and burn-in (§5b).
8. The r2 freeze on the worker, then the single official r2 qualification, the independent qualification review, and
   the proposed authorization.
9. **Stop at READY_FOR_OWNER_GRANT_DECISION.**

**Host status now: HOST_SUITABILITY_PENDING.** The shared AWS worker has not been audited, because this session
cannot reach it. The retired Vultr worker is not used. Steps 1–5 do not need a worker.
