# P309-r2 plan, addendum 1 (append-only): resolution of plan-review conditions P1–P5, and the disposition of P6–P23

The plan review `governance/REVIEW_R2_PLAN.md` (sha256 `cddfd0d0…`) returned **R2_PLAN_ACCEPTED** with conditions
P1–P23.
* P1–P5 must be resolved in this committed addendum, which goes to a focused follow-up review **before any
  implementation**.
* Where this addendum differs from `R2_PLAN.md`, the addendum governs.

NEW Γ309 TARGET EVALUATIONS = 0.

## P1: authority

**The owner's words.** `governance/OWNER_INSTRUCTIONS_R2_VERBATIM.md` holds the owner's three 2026-10-01 messages
verbatim, each with the sha256 of its fenced body:
1. the r2 directive;
2. the retired Vultr worker (one disclosed redaction: the retired worker's IP address);
3. the shared AWS worker.

**Carry-over of r1's owner decisions to r2.** r1's decisions are in `p5y_k5_cell309_p309_r1/governance/`. Quotes are
from the 2026-10-01 messages. "Carried" means the owner's 2026-10-01 words cover the item. Everything else becomes the
stop point **OD-R2-0**.

| r1 decision | r2 status | owner's words (2026-10-01) |
|---|---|---|
| **P0-1 / G2**: the authorization naming `p5y_k5_cell309_p309_r1` (freeze, qualification, review, grant package; not the grant) | **not covered as an authorization**. The owner asked r2 to be designed and "where governance permits, prepare[d]", with "eventually the official r2 qualification, but ONLY after the new r2 protocol, reviews, freeze and authorization state permit it". An explicit authorization to **freeze and qualify** r2, analogous to P0-1, is therefore **OD-R2-0** | msg 1 intro and §2 |
| CELL SET {309}; Stage-1 material bound to 309 | carried | msg 1 §1: "target interval/cell identity" |
| EXECUTION HOST: "Do not use the cell-308 machine … while 308 is live" | **superseded for r2, and only by these words** | msg 3: "P309-r2 may share the existing AWS ReBaseGuard worker currently used by cell 308, subject to strict cross-campaign isolation", with its terms 1–10 |
| The eventual target-execution host | **not covered**; **OD-R2-6** (P22) | — |
| G1 (accepted), G3 (RLR confirmed), U2 (not triggered), U3 (CLOSURE_ONLY), EFFICACY, SRK-T (out of package 1) | carried as part of the inherited scientific object; the U2 check re-runs on r2's bytes | msg 1 §1: "preserve the scientific object … SRK route/science; supply definitions; closure criterion; … scientific producer/verifier semantics" |
| STAGE-1a FAILURE SEMANTICS (protocol rev. 2b §2.5; no retry) | carried as producer/verifier semantics; listed in OD-R2-0 for confirmation | msg 1 §1 |
| QUALIFICATION FAILURE (preserve and stop; no silent re-freeze) | carried; P23's text is added (below) | msg 1 §5.B: "Do NOT introduce qualification retry/resume …" |
| SUCCESSFUL QUALIFICATION ENDPOINT | carried | msg 1 §10: "If r2 eventually reaches: READY_FOR_OWNER_GRANT_DECISION stop there" |
| ABSOLUTE BOUNDARY (target counter 0, no marker, no r5/r6 change, cell 308 untouched) | carried | msg 1 §0, §7, §10 |
| GITHUB / HISTORY (additive; no merge to main; no force) | carried | msg 1 §9 |
| Owner rulings 2: U2; FC2; the scanner allowance; the **marker-name allowance** | carried, **except the marker-name allowance**, which is **OD-R2-1/2** (P19) | — |
| D5 ratification: the pending-ref NAME and the two exactly-once sites | **not covered**; **OD-R2-1** and **OD-R2-2** | — |

## P2: literal disposition (replaces R2-I1's list)

**The table.** `governance/R2_LITERAL_DISPOSITION.json` lists every occurrence in F's frozen directories and
`start_state/` (350 rows, generated mechanically by `git show F:`) of:
* `p5y_k5_cell309_p309_r1`, `p5y-k5-cell309-p309-r1` and `p309[_-]r1`;
* the r1 branch name;
* every `P309_*/n` schema name;
* every hex string that resolves to a commit.

Each row has a disposition and a reason:

| disposition | rows | meaning |
|---|---|---|
| `rename` | 42 | namespace or campaign **path or name**: `…_p309_r1` → `…_p309_r2`, or the r1 branch → the r2 branch |
| `keep` | 102 | inherited r1 record or authority text (`governance/`, the `fc2/` specs), schema-format names, verifier history, the research anchor `eb9a9c22`, the producer lock `2a03e838`, inherited step-0 evidence |
| `owner` | 20 | the production ref names and namespace, which follow OD-R2-1 |
| `binding` | 19 | grant `campaign`, result `SCHEMA` (P3) |
| `change` | 3 | the anchor splits below |
| `verifier-author` | 164 | `verify/VERIFY_RESULTS_SCOPED.json`: regenerated at r2 by the verifier author, or marked inherited |

**The cases named in finding 1:**
* `u2_structure_check.py` lines 340 and 435–437: **rename**, so the U2 check reads r2's files.
* driver `SCHEMA` (line 93): **binding**.
* `make_freeze_params.py`:
  * line 26: rename;
  * lines 166–177 (the reviews table): **restructured**. r1's preserved reviews are referenced as inherited by their r1
    paths and the r1 head `c902fe2f`; r2's own reviews are listed beside them;
  * line 218: binding.
* The self-audit: `IMMUTABLE` is restructured the same way (r1's inherited files by r1 path; r2's preserved reviews by
  r2 path); `BASE` is split (below).
* The checkpoint tool, line 79: a change (below).
* `make_proposed_authorization.py` line 79: binding.
* The planted control: owner; it must fire for both the r1 and r2 tokens.
* The variant, `scoped_sandbox` and the allowance names: owner, rename or binding, as listed. The verifier author makes
  the variant and `scoped_sandbox` changes.

**The anchor split:**
* Research, r5 and r6 checks keep `eb9a9c22`: checkpoint line 107, runner line 269, the self-audit's research part.
* Namespace-only checks (every new commit touches only FNS2) use r2's base `c902fe2f`.
* **New check:** r1's tree at HEAD equals `ecd1c359ef0c3e0c9911b014b884376a10f6ed5b`, so r1 is never mutated. It runs
  in the checkpoint tool, the self-audit and QC13.

## P3: classification

**Bindings, reported to the owner with OD-R2-1/2 (OD-R2-1b):**

| binding | r1 | proposed r2 |
|---|---|---|
| grant path | `p5y_k5_cell309_p309_r1/authorization/P309_GRANT.json` | `p5y_k5_cell309_p309_r2/authorization/P309_GRANT.json` |
| grant `campaign` | `p5y_k5_cell309_p309_r1` | `p5y_k5_cell309_p309_r2` (schema `P309_GRANT/1` kept) |
| result path (`EXEC_DIR_REL` under FNS) | `…_r1/evidence/execution/` | `…_r2/evidence/execution/` |
| result `SCHEMA` | `rebaseguard.p5y.k5.cell309-p309-r1.result.v1` | `rebaseguard.p5y.k5.cell309-p309-r2.result.v1` |

**Rules (new, reviewed):**
* the §4.6 static assertion: the sandbox base rule, extended by P6(e);
* the §4.7 pins: the call closure of `recorded_freeze`, `check_grant`, `walk_chain` and `check_not_evaluated`
  (P6(f)).

## P4: where the host package lives

* The tools the runner calls go in **`code/`**, so they are frozen, pinned and scanned:
  * `code/p309_host.py`: provenance, Q-HOST continuity, the exclusion gate, the isolation check and the durability
    preflight, as functions;
  * `code/p309_launch.py`: the launcher, a `.py` with **no** executable bit.
* The documents go in `governance/` (`R2_HOST_REQUIREMENTS.md`, `R2_BOOTSTRAP.md`).
* No `.sh` file and no `host/` directory. `FROZEN_DIRS` is unchanged.
* Each new process-starting or `/proc`-reading function gets a `process_policy.reviewed_functions` entry with its
  reason.
* T7's string scope is extended to `code/p309_host.py` and `code/p309_launch.py`.
* The scratch drafts of the audit, the exclusion gate and the isolation check are **not** the implementation. They
  will be rewritten into `code/p309_host.py` under P9.

## P5: the post-freeze topology drill (replaces the plan's `--rehearsal` mode)

* **No** rehearsal branch is added to `p309_qualify.py`. The runner stays unmodified.
* **The tool: `code/p309_topology_drill.py`** (the name "drill" is distinct from QC14′'s "rehearse"). It:
  1. makes a scratch clone under a dedicated drill root (`<P309_SCRATCH_ROOT>/drill_<utc>/`);
  2. **refuses unless**:
     * the clone's real path is under the drill root;
     * the clone's git common dir differs from the P309 clone's;
     * the clone has **no usable push URL** (origin removed, and `remote.pushDefault` unset);
  3. commits there a synthetic F′, with the manifest and parameters regenerated by the unmodified generators, and its
     record-only child FR′;
  4. then one checkpoint-style record commit, as after a real push;
  5. runs the **unmodified** runner:
     * **cloud tier:** the runner's own item functions for the topology items (QC11, QC-D5, QC12, QC13, QC15, QC16,
       plus `recorded_freeze` and `mirror(F′)`), as the earlier dry runs did, with no change to the runner;
     * **worker tier:** the runner's `main()` in full, through the same launcher and unit properties as the official
       run (P11).
* **After each run** it asserts that the clone's changes after FR′ are confined to `qualification/` and the two
  ledgers.
* **Recording.**
  * It preserves in FNS2 `evidence/drill/`: the drill ledger's rows (as a digest), their sha256, the counters
    (target evaluations 0) and a band check.
  * **No decoy output is copied.**
  * It adds **one** GOVERNANCE row to the official FNS2 ledger.
* Its ref-moving calls (the synthetic commits) are listed in `ref_mutation_functions`, with reasons.
* **Controls.** In the drill topology, all of these must fail as specified:
  * the two R2-M01 mutants (P6(d));
  * a planted second freeze record;
  * an r1-namespace ref;
  * a drill clone that still has a push URL.

## P6–P16: implementation and pre-freeze requirements (accepted)

* P6–P13 are accepted **as written in the review**, as implementation requirements. They are verified at the r2 delta
  review.
* P14–P16 are accepted as pre-freeze requirements.

Points to note:
* **P6(e).** The verifier author applies the base rule to `scoped_sandbox.Sandbox.__init__`.
* **P6(g).** The re-pin list is published with the implementation commit, with every AST hash computed on CPython
  3.11.
* **P9.** The gate records only counts, flags, pids, uids and sha256 values for non-P309 processes. It **never** runs
  git in a cell-308 checkout. It refuses on unreadable `/proc`, `hidepid` or zero visible foreign processes. Its
  negative controls are TEST-named.
* **P10.** Every refusal comes before the attempt directory and the `RUN_START` row (static check). Sampling is
  continuous, every 60 s or less. On detecting cell-308 heavy work, the runner terminates its own heavy tree and records
  Q-HOST FAIL, unless the owner chooses otherwise under OD-R2-5. `argv[0]` is unaltered.
* **P11.** A system transient unit runs as the P309 user, with:
  * `Restart=no`, `KillMode=control-group`;
  * `MemoryMax`, a high `OOMScoreAdjust`, a low CPU and I/O weight;
  * hermetic git variables, `TMPDIR` and `P309_SCRATCH_ROOT`.

  There is no fallback unless it is proven durable.
* **P12.** The separate Unix user is mandatory. Also required: a P309-only credential outside the repository config,
  a single-branch clone with full history, and a quota-limited volume. No self-hosted runner without the owner's
  explicit choice.
* **P14.** The worker-tier drill is mandatory and decides HOST_SUITABLE. QC08's byte identity and QC10 must pass
  there.
* **P15.** CPython **3.11.15** exactly (P309-private). Pinned: glibc and the interpreter's sha256. Upgrades are held,
  AWS scheduled events checked, no burstable instance.
* **P16.** The placeholder allowlist entries are narrowed to the exact hits, or the pre-freeze reviewer confirms every
  allowed hit.

## P17–P23: owner decisions (replaces plan §8A)

* **OD-R2-0 (P17): authority and carry-over.** Confirm the P1 table, and authorize, analogous to r1's P0-1, r2's:
  * freeze, the single qualification and the independent qualification review;
  * grant-package preparation (**not** the grant).

  This is required before the r2 freeze.
* **OD-R2-1 (P18): the production ref namespace.**
  * **(a)** keep r1's names;
  * **(b) recommended:** the `refs/p5y-k5-cell309-p309-r2/` names. No new code is needed: the driver already refuses
    any `refs/p5y-k5-cell309*` ref (driver line 67). r1's namespace stays forbidden in `production_tokens`, the
    `TestContext` refusal, `_FORBIDDEN_REF_PREFIX` and QC13.

  **OD-R2-1b:** the bindings in P3.
* **OD-R2-2 (P19).** Under (b), ratify the new pending-result and marker **names** (D5-1, and the marker-name allowance
  of owner rulings 2). Extend D5-2 to r2's two sites, whose AST hashes equal `1ee764b7…` and `13ee3ec3…`. The A38
  backstop pins are reported as unchanged.
* **OD-R2-3: worker access.** A separate P309 session on the AWS worker (P12), and an exclusive window agreed against
  cell 308's schedule.
* **OD-R2-4 (P20): shared-host changes.** These need the owner's **and** the cell-308 operator's consent:
  * the P309 Unix user, and the permissions on cell 308's checkout;
  * the reboot and upgrade hold;
  * the P309-private Python install;
  * the volume or quota;
  * the unit limits.
* **OD-R2-5 (P21): the interference policy.**
  * **(i)** a cell-308 heavy start fails r2's single attempt;
  * **(ii)** P309 yields by kernel priority (idle CPU weight, OOM preference) and records the event.

  Under (i), a third party can consume r2's only attempt.
* **OD-R2-6 (P22), before the freeze: is the shared worker also the proposed target-execution host?**
  * After the marker, an OOM kill or `kill -9` is `EXECUTION_INDETERMINATE` (A22).
  * Execution may need about 31.5 h.
  * Also decide whether A14's QC10 host re-run is repeated immediately before any grant.

**P23 (governance text, adopted):**
* A failed or interrupted r2 attempt ends r2's qualification, and r2 stops.
* Any successor needs a new owner decision.
* No r2 tool prepares an r3.

## P13: gate order (replaces plan §9)

1. Plan review (**done**: R2_PLAN_ACCEPTED, conditions P1–P23).
2. This addendum and its focused follow-up review. **No implementation before it is accepted.**
3. The verifier author's changes:
   * the variant's literals (rename / owner / binding per P2);
   * `scoped_sandbox`'s base rule (P6(e));
   * `P309_SCRATCH_ROOT` (P7);
   * `VERIFY_RESULTS_SCOPED.json` (P2), with its report.

   These come **before** any development QC16 run and before the drill.
4. Coordinator implementation (R2-I1 to R2-I7, under P2–P12), then the development tests.
5. The cloud-tier topology drill (P5), with every control.
6. The r2 delta review: implementation, equivalence (P8), classification.
7. The owner decisions OD-R2-0 to OD-R2-6. **STOP.**
8. Worker access (OD-R2-3, OD-R2-4):
   * the read-only audit through `code/p309_host.py`;
   * the worker-tier drill as the burn-in (P14);
   * then **HOST_SUITABLE**, **HOST_NOT_SUITABLE** or **HOST_SUITABILITY_PENDING**.
9. A pre-freeze follow-up review after the audit and the worker-tier drill. After any later change: a delta review and
   a re-drill.
10. The r2 freeze **on the worker**:
    * clocks synchronised;
    * a single writer for the branch from F until the Q commit;
    * the frozen-directory tree ids at F equal those reviewed and drilled (`freeze/` excepted).

    Then the single qualification, the independent qualification review and the proposed authorization.
11. **Stop at READY_FOR_OWNER_GRANT_DECISION.**
