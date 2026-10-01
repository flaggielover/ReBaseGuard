# Independent review of the P309-r2 plan (before implementation)
R2_PLAN_ACCEPTED

**Reviewer.** I am a new independent reviewer. I wrote none of the P309 code and none of the r2 plan, and I am not the
coordinator.

**Brief.** `governance/BRIEF_R2_PLAN_REVIEW.md` (blob `ef3d1a79`, sha256 `b2085c48…`). It was committed before issue,
in `da754b8f`.

**State reviewed.**
* Branch `claude/p5y-k5-cell309-p309-r2`, HEAD `da754b8fec608a16e8972a106579c49e300e104d`, working tree clean.
* The plan is `governance/R2_PLAN.md` (blob `8e6a66ec`, sha256 `eff4f80a…`).
* r1 is `p5y_k5_cell309_p309_r1`, at the same tree as its final head `c902fe2f` (r1 tree `ecd1c359` at both).

**NEW Γ309 TARGET EVALUATIONS = 0.** This review evaluated nothing, ran no campaign code and created no ref.

Unless stated otherwise, paths below are relative to `level4/closure_proofs/p5y_k5_cell309_p309_r1/` ("r1"). "FNS2" is
the r2 namespace.

## Verdict in brief

**Accepted, with binding conditions.** The direction of the plan is right:
* r2 is a new campaign, not a retry. A27, A24 and the runner's attempt refusal leave no other route that keeps r1's
  frozen rules.
* The scientific object is untouched.
* Basing the QC11 sandboxes on the recorded freeze commit F is the correct and minimal fix.
* A post-freeze rehearsal is the right control for the r1 class of defect.
* Host continuity and cross-campaign exclusion are handled as rules, and the stop points are owner decisions.

**But the plan cannot be implemented as written.** Concretely:
1. **R2-I1's relocation list is incomplete and its method is unsafe.** One missed literal makes QC-U2 analyse r1's
   files instead of r2's, and pass without ever reading r2's driver, guard or variant. Other literals cannot simply be
   renamed: renaming them breaks QC15, QC13's parameter regeneration, freeze generation and the first checkpoint push
   (P2).
2. **The equivalence proof in §2 cannot detect a missed rename.** A stale r1 literal is byte-identical to r1, so the
   proof passes it (P8).
3. **The planned `host/` package sits on the qualification path, but is neither frozen nor pinned.** Its shell
   launcher is also a finding for the frozen scanner (P4).
4. **The `--rehearsal` runner mode either fails QC13 or gives QC13 a code path the official run never takes** (P5).
5. **The verifier author's relocation is scheduled after the rehearsal that is meant to test it** (P13).
6. **The shared-host isolation fails open in places, and it has a path that leaks cell-308 data.** Under a separate
   Unix user the exclusion gate cannot see another user's cwd and open files, so it would pass. The gate's committed JSON
   could carry cell-308 command lines (P9–P12).
7. **The authority for r2, and for using the cell-308 machine, is not preserved verbatim.** Several owner-reserved
   items are missing from §8A (P1, P17–P23).

**Blocking.**
* Conditions **P1–P5** must be met in a committed, append-only plan addendum before any implementation starts. That
  addendum goes to a focused follow-up of this review.
* **P6–P13** are verified at the r2 delta review.
* **P14–P16** must be met before the r2 freeze.
* **P17–P23** are owner decisions.

## Findings

### 1. Scope and the equivalence proof

**Confirmed.**
* No change in §3 touches the SRK route, supplies, the closure criterion, Γ309, the cell interval, the budgets, worker
  counts, the outcome table or the Stage 1a/1b/2 procedures.
* The two exactly-once sites and the A38 backstop are unaffected by relocation. I parsed the AST statically (nothing
  imported or executed) on CPython 3.11.15, which is r1's pinned runtime:
  * `_arm_marker` `1ee764b7…` and `_persist_pending` `13ee3ec3…` equal the allowance pins now;
  * `_assert_execute_context` `c8a2fb51…`, `_site_backstop` `80d206ad…` and `_require_own_run_nonce` `23f3021d…` also
    equal their pins;
  * all five hashes are unchanged after an in-memory `p309_r1→p309_r2` substitution.
* `recorded_freeze`, `check_grant` and `walk_chain` read only module constants (driver lines 327–547), so their ASTs
  are unchanged too.

**R2-I1 is not "change only the campaign-path and campaign-name literals".** F's tree holds `p309_r1` or `p309-r1` in
19 code, config, test and verify files, four of them only in docstrings. The plan's list omits several of them. Some
cannot be renamed:
* **`code/u2_structure_check.py` lines 340 and 435–437.** `GUARD_MODULES`, `DRIVER` and `VARIANT` are hard-coded r1
  paths.
  * Left unrenamed, QC-U2's U4 part analyses r1's driver, guard and variant. Those files are present in the tree and
    differ from r2's only by literals, so QC-U2 passes without examining r2.
  * This is a silent wrong-target pass. No test would show it.
* **`code/p309_self_audit.py` (QC15).**
  * `IMMUTABLE` (line 44) lists 42 paths, 32 of them under `reviews/`. Each is read through `FNS / rel` (line 111).
    R2-I1 copies no `reviews/`, so in FNS2 this raises `FileNotFoundError`.
  * `BASE = eb9a9c22…` (line 37) feeds A7 (lines 131–134). The r2 branch carries all of r1's paths since `eb9a9c22`,
    so with a renamed `NS_PREFIX` every r1 path counts as "outside", and A7 fails.
* **`code/make_freeze_params.py`.**
  * Its review table (lines 166–177) reads conditions from `NS + "reviews/…"`. With `NS` renamed (line 26), freeze
    generation fails, and so does QC13's `--check`.
  * These entries must keep pointing at r1's reviews, as inherited authority, and gain r2's own.
  * Line 218 also sets `campaign`.
* **`code/checkpoint_push_p309.py` line 79.** When the remote ref is absent, the base is `eb9a9c22…`. Check 6
  (line 84) then counts r1's paths as outside.
* **Not in the plan's list at all:**
  * `code/p309_driver.py` line 93: `SCHEMA = "rebaseguard.p5y.k5.cell309-p309-r1.result.v1"`, the sealed result's
    schema;
  * `code/make_proposed_authorization.py` line 79;
  * `tests/planted_control_p309_formal.py` line 28.
* **Depend on OD-R2-1 but are not named under R2-B1:**
  * the variant's own `PRODUCTION_MARKER` (`verify/srk_verify_indep_scoped.py` line 163);
  * `verify/scoped_sandbox.py` line 31 `_FORBIDDEN_REF_PREFIX`;
  * the allowance's `names`, `production_ref_namespace` and `production_tokens`.
* **`verify/VERIFY_RESULTS_SCOPED.json`.** It is pinned evidence and records r1's variant sha256 `9d9f8cec…`. Copied
  as is, it misstates r2's variant.

**Classification.** Several R2-I1 items are **bindings**, not infrastructure, because the owner's grant must name them:
* the production grant path (`_PROD_GRANT_PATH`, which moves to FNS2);
* the grant's `campaign` value (guard `_parse_grant` line 225);
* the production result path (`EXEC_DIR_REL`);
* the result `SCHEMA`.

The new QC12 assertion (§4.6) and the new AST pins on `recorded_freeze`, `check_grant` and `walk_chain` (§4.7) are
**rules**. The plan should flag them as such.

**Scientific outputs.** No change to the scientific semantics is planned, but **the host change can change outcomes**:
* The producer's float layer uses libm: `impl/srk_float.py` calls `math.exp`, `math.erfc` and `math.cos` (lines 17,
  21, 27).
* On a different glibc or interpreter, Stage-1a certificates can differ. Validity does not depend on this, because
  verification is rigorous, but the outcome can (certify versus fall back).
* QC08 (byte-identity to the research-committed certificates) and QC10 are the guard against this. They must therefore
  be a hard host-suitability criterion, met before the freeze (P14), and the runtime pin must cover libc (P15).

**The equivalence proof (§2) is necessary but not sufficient.**
* "Every pin outside FNS2 equals r1's" checks values, not the set of pins.
* "Each FNS2 diff is classified" cannot see a literal that was never renamed. The U2 case above shows no diff at all and
  passes.
* The regenerated `P309_FREEZE.json` is not compared key by key.
* See P8.

### 2. The QC11 repair (§4)

**Root cause: right.** I re-read the code:
* `new_sandbox` takes the real HEAD (test line 79);
* `build_chain` adds a synthetic record (line 122);
* `recorded_freeze` requires exactly one record commit (driver lines 344–346).

The postmortem review reproduced the failure with a counterfactual, and its follow-up corrected the counterfactual's
wording (F2).

**Basing the sandbox on F: correct and minimal.**
* F's tree holds every frozen directory and no record, and F's history has no record commit.
* F is in the object store that the alternates link points to.
* The QC11 flows never needed the real FR. Nothing is lost.

Two refinements:
* The decision should depend on history (`git log HEAD -- FREEZE_RECORD_REL` is non-empty), not on whether HEAD's tree
  holds the record.
* The harness reads the manifest bytes from the working tree (lines 114 and 570). In post-freeze mode it should read
  them from `F:` instead.

**The invariant (§4.4) is not implementable as worded.** "After building a valid chain … exactly one" cannot work as
stated, because A23–A25 deliberately build chains with 0, 1 and 2 record commits (lines 364–366). It must be:
* a **precondition**: the base's history has 0 record commits;
* plus a **per-mode postcondition**: ok/wrong → 1, missing → 0, late_change → 2.

The flows that expect `FREEZE_RECORD` must also assert the refusal detail: F14, F16 (lines 262–266) and A23–A25. The
postmortem review showed that in r1 these flows "passed for the wrong reason".

**R2-M01 is mis-specified.** If the mutant restores the old base but keeps the new invariant, the invariant raises
first, and the mutant can never show the `FREEZE_RECORD` refusal the plan requires. It needs two mutants:
* old base without the invariant, which must reproduce r1's uncaught V01 refusal;
* old base with the invariant, which must raise the invariant's own error.

Mutant copies must live outside FNS2. The scanner walks all of FNS (`p309_scan.py` line 1433), and an unlisted
ref-moving copy is a finding.

**The static assertion (§4.6) is too narrow.** It covers `new_sandbox` only. The real-repository HEAD reads that serve
as sandbox bases are three:
* `tests/test_p309_exactly_once.py` line 79;
* `tests/test_p309_guard.py` line 70;
* `verify/scoped_sandbox.py` line 85.

**Production path: unchanged.** The three functions keep their ASTs. Pinning them is good, but the pin must cover their
call closure: `freeze_commit`, `_only`, `_chain_kind` and `verdict_ok`, and also `check_not_evaluated` (see §6).
Otherwise a change to `_only` alters `recorded_freeze` while its pin still holds.

**Should the guard and verifier sandboxes follow the same rule now? Yes.**
* The criterion "unless the rehearsal shows sensitivity" only covers the paths that get executed. The r1 defect was
  exactly a latent sensitivity.
* `scoped_sandbox.py` changes anyway for R2-I2, so including the base rule adds no review round.
* `scoped_sandbox.py` is not the variant, so `verifier_id` is unaffected.
* A single rule lets one static check cover all three harnesses.
* The verifier author makes the change (P6e).

### 3. The post-freeze rehearsal (§5)

**Sound idea, and the tier split is sound.** The cloud tier is cheap and covers the r1 class (QC11, QC-D5, QC13, QC16).
The worker tier covers host, runtime, environment and timing. Three defects need fixing.

**A `--rehearsal` mode in the frozen runner lowers fidelity.**
* QC13's `single_run_since_freeze` counts ledger rows whose `purpose` starts with `QUALIFICATION RUN START`
  (`p309_qualify.py` line 296). If the rehearsal label is put into that `purpose`, QC13 fails in the rehearsal.
* If the label goes elsewhere, the official run takes a branch the rehearsal never takes, and the runner gains a mode
  the official attempt must provably never enter.
* Better: run the **unmodified** runner in the scratch clone, which has its own `qualification/attempt_1` and its own
  ledger. Keep the "REHEARSAL" label in the tool's own report.

**The rehearsal tool is dangerous if misdirected.**
* It commits a synthetic freeze record. In the real P309 clone, that would add a second record commit to r2's history
  (A24), and r2 could never qualify.
* After the freeze, the unmodified runner would also create the real `attempt_1`, burning r2's single attempt.
* So it needs hard target guards (P5).
* Its ref-moving git calls must be listed in `ref_mutation_functions` (owner D5, schema 3).
* Its name collides with QC14′ "rehearse" (`code/p309_rehearse.py`, driver mode `rehearse`), which name-based checks
  use (`p309_static_check.py` line 62; `u2_structure_check.py` line 436).

**Rehearsal ledgers that are "never pushed" leave a gap in the record.** Hours of decoy Stage-1 computation on the
shared host would leave no committed trace. Self-audit A2 (no band drift) could not cover them.

**What could still slip through:**
* **Steps that use the network.** QC15's `ls-remote origin` goes to a local origin in a clone, but to GitHub in the
  official run.
* **The user's git configuration.** `p309_qualify.git()` and `single_run_since_freeze` are not hermetic. A global
  `log.showSignature` breaks the parse of `%H %cI` at line 288, the same class as R4's A45 finding.
* **Clock skew.** QC13 compares FR's commit time with the ledger's UTC strings, so skew between the machine that
  commits FR and the runner host matters.
* **Pushes to the branch while the attempt runs.** A merge inside F←FR←…←Q breaks `walk_chain` (line 512), and a
  force push is forbidden.
* **What the Q commit may touch.** A8 lets the Q commit touch only `qualification/` and the two ledgers. The rehearsal
  should assert that `git status` in the clone shows nothing else.
* **Environment differences** between an interactive shell and a systemd unit. The worker tier catches these only if it
  uses the identical launcher.

A side note: `git clone --local` is ignored for a shallow source, such as this cloud repository, and git falls back to
a full object copy.

### 4. Shared host, isolation, Q-HOST, no retry (§6–§7)

**Not yet sufficient, and not fully read-only towards cell 308.**
* **Fail-open visibility.** Under the recommended separate user, `/proc/<pid>/cwd` and `/proc/<pid>/fd` of another
  user's process are unreadable without privilege. A `hidepid` /proc mount hides those processes entirely. The gate
  would then see no cell-308 process and pass. Unreadable means refuse.
* **Firewall leak.** The gate's JSON is "preserved with the run", that is, committed. Cell-308 command lines, cwds and
  open-file paths can carry cell-308 parameters. Only counts, flags, pids, uids and hashes may be recorded.
* **A self-match.** P309's own mirror reads `…/streams/C_308/…` (`p309_qualify.py` line 45). Any pattern containing
  `308` matches P309 itself unless P309's own unit and cgroup are excluded.
* **The plan contradicts itself, and observing cell 308 can write to it.**
  * §6.1 says the P309 side "never … reads into" the cell-308 checkout, yet observes that checkout's HEAD.
  * A git process run there under the P309 user hits `safe.directory`.
  * `status` and `diff` refresh, and so write, the cell-308 checkout's index.
  * The before/after HEAD equality detects cell 308's own commits, not P309 writes. It must not be a gate.
* **"Verified by listing the files the run created."** This needs a filesystem walk that reads into cell 308's tree.
  Kernel enforcement replaces it (P9).
* **Shared resources.**
  * r1 had a disk-exhaustion incident: execution-ledger row 2026-09-30T03:42:08Z, "DISK EXHAUSTION: the coordinator
    dev sandboxes …".
  * On a shared disk, P309 can fill cell 308's filesystem.
  * The OOM killer may pick a cell-308 process.
* **Cell-308 refs.** "Holds no cell-308 ref" fails for a default clone, which fetches every branch.
* **The load baseline.** If it is "measured at audit time" while cell 308 runs, it includes cell 308's load.

**Q-HOST: partly sound.**
* **Boot and instance continuity: correct but mostly redundant.** A reboot already leaves no summary. "The runner
  process is the same" is self-attested.
* **Sampling.** Sampling "after each QC item" is not continuous: QC09 alone ran 9 768 s.
* **On detection the run continues.** The runner keeps competing with cell 308 for hours and fails only at the end.
  That contradicts "never interrupts it".
* **A third party can end r2.** The rule lets cell-308 activity consume r2's single attempt. That is an owner trade-off
  (P21).
* **Ordering is critical.** The preflight, gate and isolation refusals must run before `os.mkdir(attempt_1)` and before
  the `RUN_START` line (`p309_qualify.py` lines 403–406). Otherwise a preflight refusal itself creates a failed attempt.
* **No visible process title from Python.** The scanner forbids `ctypes` (A37), and renaming `argv[0]` in a shell
  breaks `PY = sys.executable` (line 52), which is used to spawn every child. Use the unit name.

**Persistence.**
* Without `--user`, `systemd-run` creates a system unit (needs root) that runs as root unless `--uid` is given.
* With `--user`, the unit dies when the P309 user's last session ends unless lingering is enabled.
* The `setsid` and `nohup` fallback dies at logout under `KillUserProcesses=yes`.
* The preflight says that `systemd-run` "is available (fallback …)", so it is unclear whether a unit is required.

**No retry: correctly kept.** A27 is inherited, and the plan proposes no retry rule. Three clarifications are needed:
* preflight refusals come before the attempt exists;
* the rehearsal can never run in the real clone;
* a failed r2 does not open a routine "r3" route (P23).

### 5. Requirements (§8)

**Mostly justified by r1's evidence, with gaps.**
* **Time.** 5.47 h for QC01–QC-U2 and about 5.7–5.9 h complete (postmortem D5) supports the plan's window of about
  6 h + 50 %. But that was r1's container. The window must come from the worker-tier timing.
* **RAM.** "About 15 GB available" is a session observation (`handoff/OVERNIGHT_REPORT_P309.md` §10). Nothing measured
  it. The burn-in should measure peak memory.
* **Disk.** The 40 GB figure is plausible now that sandboxes are light. Given r1's incident, it must also be a quota or
  a separate volume.
* **Missing:**
  * exact CPython 3.11.15, r1's pin. `ast.dump` differs from 3.12 on, so on another minor version the owner's site
    pins are not reproducible, and the freeze is generated on the worker.
  * the glibc version;
  * a hold on package upgrades: unattended-upgrades and needrestart can kill a long-running process or change libm
    under an unchanged `host_id`;
  * AWS scheduled maintenance events;
  * a non-burstable instance;
  * clock synchronisation;
  * a stable hostname and `machine-id`, both of which `host_id` binds.
* **Execution-phase requirements are absent, although the freeze binds the host.**
  * The A6 bounds, as corrected (< 96 CPU-h for Stage 1a, < 30 CPU-h for Stage 1b), mean up to about 31.5 h at 4
    workers on an idle host, and unbounded wall time on a contended host.
  * After the marker, an OOM kill is `JOB_EXCEPTION` → `EXECUTION_INDETERMINATE` (A22).

### 6. Owner decisions (§8A)

**OD-R2-1.**
* **(b) is the right recommendation.** (a) would create refs in r1's namespace, which conflicts with "r1 is never
  mutated".
* **The "new, reviewed rule" already exists.** `check_not_evaluated` refuses any ref that starts with
  `refs/p5y-k5-cell309`. That covers both namespaces: driver lines 67 and 356–359, run in `execute` and in
  `validate-grant` (A39).
* **No new code is needed**, and none should go into the sites or the pinned backstop.
* **Under (b), r1's namespace must stay "production" for r2's tooling:**
  * the scanner's `production_tokens`;
  * the guard's `TestContext` refusal (line 173);
  * `_FORBIDDEN_REF_PREFIX`;
  * QC13's `no_exactly_once_ref` (`p309_qualify.py` line 268).
  * Otherwise r2's code could create r1-namespace refs with no finding. Owner rulings 2 treats the real marker name as
    forbidden everywhere.

**OD-R2-2.** Under (b), D5-1 ratified the exact name `refs/p5y-k5-cell309-p309-r1/pending-result`. The new
pending-result name, and the scanner's marker-name allowance (owner rulings 2), need ratification. Extending D5-2 to
the sites alone is not enough.

**OD-R2-3.** It is right but too narrow. These items are missing: P17, P20, P21 and P22.

### 7. Gate order (§9)

Missing before the r2 freeze:
* **The owner's verbatim instruction**, before step 2.
* **Order of steps 3 and 4.** The verifier author's relocation (step 4) must precede the development runs of QC16 and
  the cloud-tier rehearsal (step 3).
  * Until then, the variant in FNS2 still names r1's manifest, grant and result paths, and those files exist.
  * QC16 would then validate against r1's paths.
* **A pre-freeze follow-up review** after the host audit and the worker-tier rehearsal. The R4-style review in step 5
  comes before both.
* **A rule for changes made after a rehearsal**: delta review and re-rehearsal.
* **A mechanical binding** of the reviewed tree, the rehearsed tree and the frozen tree.
* **A single-writer rule** for the r2 branch from F to Q, because two sessions will exist.
* **The freeze commits made on the worker**, with clocks synchronised.

### 8. Facts in §0 (checked locally; the remote was not queried)

* The r1 ledger has 1421 rows, 0 nonzero target evaluations, 0 proxies and exactly 1 `QUALIFICATION RUN START` row.
* No ref exists under `refs/p5y-k5-cell309-p309-r1/`, `refs/p5y-k5-cell309-p309-r2/` or `refs/p309-test/`, and no
  non-ordinary ref exists.
* The r5 blob is `f978eeb6…`, and no path matches `COVERAGE_MAP_R6`.
* No frozen directory changed between F and HEAD.
* r1's tree is identical at `c902fe2f` and at HEAD.
* `eb9a9c22` is an ancestor of HEAD.
* The tree has no cell-308 namespace directory (names only).

## Conditions

**A. Before any implementation.** These go into a committed, append-only plan addendum, which receives a focused
follow-up review.

* **P1 — Authority.**
  * Commit the owner's 2026-10-01 instruction(s) verbatim in FNS2 `governance/`: the fenced body, its sha256, and the
    transcript timestamp or uuid.
  * Quoting the owner's words, map which r1 decisions carry over to r2:
    * P0-1/G2, which names `p5y_k5_cell309_p309_r1`;
    * G1, G3, U2 and U3;
    * the Stage-1a failure semantics;
    * the cell set;
    * QUALIFICATION FAILURE;
    * the endpoint and the absolute boundary;
    * owner rulings 2 and D5.
  * Any decision the owner's words do not cover becomes a stop point.
  * r1's "Do not use the cell-308 machine … while 308 is live" is superseded only by those verbatim words.
* **P2 — Literal disposition table** (replaces R2-I1's list).
  * For every occurrence in F's frozen directories and `start_state/`, state rename, keep (inherited r1 authority) or
    owner (R2-B1), with a reason. Cover:
    * `p309_r1`, `p309-r1` and `cell309-p309-r1`;
    * the r1 branch name;
    * `eb9a9c22` and the other commit anchors.
  * Resolve at least the cases in finding 1: `u2_structure_check.py` 340/435–437, driver `SCHEMA`,
    `make_freeze_params.py` 26/166–177/218, the self-audit's `IMMUTABLE` and `BASE`, checkpoint push line 79,
    `make_proposed_authorization.py` 79, the planted control, and the variant, `scoped_sandbox` and allowance names.
  * Split the anchors:
    * research, r5 and r6 checks keep `eb9a9c22`;
    * namespace-only checks use `c902fe2f`;
    * add a check that r1's tree at HEAD equals `ecd1c359` (r1 never mutated).
  * The verifier author regenerates `verify/VERIFY_RESULTS_SCOPED.json`, or marks it as inherited.
* **P3 — Classification.**
  * Reclassify the grant path, the grant `campaign`, the result path and the result `SCHEMA` as **bindings**. Report
    them to the owner with OD-R2-1 and OD-R2-2.
  * Flag the §4.6 static assertion and the §4.7 pins as **rules**.
* **P4 — Host package location.**
  * Put the tools the runner calls in `code/`: provenance, the exclusion gate, the isolation check and the durability
    preflight. There they are frozen, pinned and scanned.
  * Write the launcher as `.py`, with no executable bit. A `.sh` file is a `NONPY_FILE` finding, and an executable bit
    is an `EXEC_BIT` finding (`p309_scan.py` lines 1268–1275).
  * Put the documents in `governance/`.
  * List each new process-starting function in `process_policy.reviewed_functions`, and extend T7's string scope.
  * The alternative, adding `host` to `FROZEN_DIRS` in the driver, the generator and the runner, is a binding change.
* **P5 — Rehearsal tool.**
  * Add no rehearsal branch to `p309_qualify.py`. The tool runs the unmodified runner in a scratch clone.
  * The tool refuses unless all of these hold:
    * the target's real path is under a dedicated rehearsal root;
    * the target's git common dir differs from the P309 clone's;
    * the target has no usable push URL.
  * Give it a name distinct from QC14′'s "rehearse".
  * List its ref-moving calls in `ref_mutation_functions`, with reasons.
  * After each run, assert that the clone's changes are confined to `qualification/` and the two ledgers.
  * Preserve each rehearsal's ledger in FNS2 evidence (rows, sha256, counters, band check), and add one GOVERNANCE row
    to the official ledger. Copy no decoy outputs.

**B. During implementation; verified at the r2 delta review.**

* **P6 — QC11 repair details.**
  * (a) `sandbox_base()` decides by history. In post-freeze mode, it takes the manifest from `F:`.
  * (b) The invariant is a 0-record precondition on the base, plus a per-mode postcondition.
  * (c) Flows that expect `FREEZE_RECORD` assert the refusal detail.
  * (d) R2-M01 is split into the two mutants above, kept outside FNS2.
  * (e) The guard harness, and `scoped_sandbox.Sandbox.__init__` (changed by the verifier author), use the same rule.
    The static check forbids any other real-repository HEAD read used as a sandbox base in `tests/` and `verify/`.
  * (f) Pin the call closure of `recorded_freeze`, `check_grant` and `walk_chain`, and also `check_not_evaluated`.
  * (g) Publish the re-pin list, and compute every AST hash on CPython 3.11.
    * Relocation alone changes `ref_mutation` `tests/test_p309_guard.py::run` and the reviewed
      `TestFC2Scoped.test_N10_production_cannot_be_synthesized`.
    * It also changes the module hashes of the `t7_exemptions` for `test_p309_guard.py`, `p309_env.py`,
      `p309_scan.py`, `checkpoint_push_p309.py` and `test_verify_scoped.py`, and the variant's `multiprocessing`
      exemption.
    * R2-I2 and R2-I3 add further re-pins.
* **P7 — `P309_SCRATCH_ROOT`.**
  * It must be absolute and resolved, outside REPO and outside every configured cell-308 path.
  * It must differ for each rehearsal and for the official run, and must be empty at the official preflight.
  * `TMPDIR` points to it.
  * A violation fails loudly in every consumer.
* **P8 — Equivalence proof.** It must include all of these:
  * (a) the set of pins outside FNS2 equals r1's set;
  * (b) for relocation-only files, the bytes after reverse substitution of the declared map equal F's bytes;
  * (c) a completeness scan of FNS2 for r1 literals returns only P2's "keep" entries;
  * (d) a key-by-key diff of `P309_FREEZE.json` against r1's, with the expected differences listed beforehand;
  * (e) the runtime-pin difference is classified under R2-B3.
* **P9 — Exclusion gate and isolation.**
  * Refuse on any of these:
    * an unreadable `/proc` entry of a foreign process;
    * a `hidepid` mount;
    * zero visible foreign processes.
  * Exclude P309's own cgroup before matching.
  * Record only counts, flags, pids, uids and sha256 values. Never record command-line text, cwds or paths of non-P309
    processes.
  * Never run git in a cell-308 checkout. Its HEAD may be read from `.git/HEAD` and the one named ref, and the
    observation is informational only.
  * Replace "listing the files the run created" with unit sandboxing, evidenced by `systemctl show`:
    * `ProtectSystem=strict`;
    * `ReadWritePaths=` limited to the P309 roots;
    * `PrivateTmp=yes`;
    * `InaccessiblePaths=` covering the cell-308 checkout(s).
  * Measure the baseline load while the cell-308 operator confirms the host is idle.
  * Add controls. Each of these must refuse, and there must be one positive control:
    * a TEST-named fake heavy process;
    * an unreadable `/proc`;
    * a `hidepid` mount;
    * a simulated `boot_id` change;
    * a stale P309 job;
    * low disk or low RAM.
* **P10 — Q-HOST and preflight.**
  * All refusals come before the attempt directory and the `RUN_START` row, and a static check asserts this order.
  * Sampling is continuous, at most every 60 s.
  * On detecting cell-308 heavy work, the runner at once terminates its own heavy process tree and records a Q-HOST
    FAIL, unless the owner chooses otherwise under P21.
  * Record at start and end:
    * the interpreter binary's sha256;
    * the glibc version;
    * `CLOCK_BOOTTIME − CLOCK_MONOTONIC`, which shows suspension;
    * the NTP status.
  * Do not alter `argv[0]`.
* **P11 — Persistence.**
  * Run as a system transient unit with `--uid`/`--gid` set to the P309 user. Remove the fallback unless it is proven
    durable.
  * Unit properties:
    * `Restart=no` and `KillMode=control-group`;
    * `MemoryMax`, a high `OOMScoreAdjust`, and a low CPU and I/O weight, so that P309 yields to cell 308;
    * `Environment=` setting `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_TERMINAL_PROMPT=0`, plus
      `TMPDIR` and `P309_SCRATCH_ROOT`.
  * The worker-tier rehearsal uses the identical launcher and properties.
* **P12 — Separation on the worker.**
  * A separate Unix user is **mandatory**.
  * The cell-308 checkout and evidence are unreadable by that user, and the P309 session runs as that user.
  * Use a P309-only GitHub credential, not in the repository's local config. `credential.helper` is not in
    `REPO_CONFIG_ALLOWED`, so a local helper makes `check_host_git` refuse.
  * Clone with `git clone --single-branch --branch claude/p5y-k5-cell309-p309-r2` and full history (`eb9a9c22` must be
    reachable).
  * Put the P309 roots on a quota-limited or separate volume.
  * Do not use a self-hosted GitHub runner on the shared host without the owner's explicit choice.
* **P13 — Gate order.** Add the missing items from finding 7:
  * P1 before step 2;
  * the verifier author's changes before the development runs of QC16 and before step 3;
  * a pre-freeze follow-up review after the host audit and the worker-tier rehearsal;
  * after any later change: a delta review and a re-rehearsal;
  * the frozen-directory tree ids at F equal those reviewed and rehearsed (`freeze/` excepted);
  * a single writer for the branch from F until the Q commit;
  * the freeze committed on the worker, with clocks synchronised.

**C. Before the r2 freeze.**

* **P14 — Worker-tier rehearsal: mandatory, and decisive for HOST_SUITABLE.**
  * It runs on the same host and interpreter binary, through the same unit, with the full item set.
  * QC08's byte-identity to the research certificates, and QC10, must pass there.
  * The measured wall time × 1.5 sets the window.
  * The measured peak memory sets the RAM requirement.
  * State exactly what "on the same `boot_id`" requires.
* **P15 — Runtime and host.**
  * Use exactly CPython 3.11.15, as a P309-private interpreter.
  * Pin the glibc version and the interpreter's sha256 at the freeze.
  * Hold package upgrades (unattended-upgrades and needrestart) from the worker-tier rehearsal through qualification.
    If P22 says yes, the hold extends through execution.
  * The preflight checks AWS scheduled events.
  * The instance is x86_64 and not burstable.
  * The hostname and `machine-id` stay stable.
* **P16 — Placeholder allowlist.** r1's two entries are scoped by file and pattern, and the qualification review never
  checked them (D3). r2's regenerated parameters will contain new text. Either narrow the entries to the exact hits, or
  have the pre-freeze reviewer confirm every allowed hit.

**D. Owner decisions (add to §8A).**

* **P17 — OD-R2-0: authority and carry-over.** This is P1, put to the owner.
* **P18 — OD-R2-1, amended.**
  * Under (b), add no new code. The r1-namespace refusal already exists (driver line 67).
  * Keep r1's namespace in `production_tokens`, the `TestContext` refusal, `_FORBIDDEN_REF_PREFIX` and QC13.
* **P19 — OD-R2-2, amended.** Under (b), ratify the new pending-result and marker names (D5-1, and the marker-name
  allowance of owner rulings 2). Report the A38 backstop pins as unchanged.
* **P20 — New: changes to the shared host.** These need the owner's and the cell-308 operator's consent:
  * the Unix user and the permissions on cell 308's checkout;
  * the reboot and upgrade hold;
  * the Python install;
  * the volume or quota;
  * the unit limits.
* **P21 — New: interference policy.**
  * Choose one:
    * (i) fail r2's single attempt on a cell-308 start, as the plan does;
    * (ii) yield by kernel priority (idle CPU weight, OOM preference) and only record the event.
  * Under (i), a third party can consume r2's only attempt.
* **P22 — New, before the freeze: is the shared worker the proposed target-execution host?**
  * After the marker, an OOM kill or `kill -9` is `EXECUTION_INDETERMINATE` (A22).
  * A reboot leaves the evidence to `seal-only`.
  * Even on an idle host, execution may need about 31.5 h.
  * Decide whether A14's QC10 host re-run is repeated immediately before the grant in any case.
* **P23 — Governance text.**
  * A failed or interrupted r2 attempt ends r2.
  * Any successor needs a new owner decision.
  * No r2 tool prepares an r3.

## Disclosure (reads, runs, writes)

**Scratch ledger.** Every read and run is logged in
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r2_plan_review/LEDGER.jsonl`.

**Reads.** All r1 reads are in r1's own namespace.
* The brief and the plan.
* r1 governance:
  * `P309_REV2C_AMENDMENTS.md` (in full);
  * `OWNER_DECISIONS_P309_VERBATIM.md` and `OWNER_D5_RATIFICATION_P309_VERBATIM.md` (in full);
  * `OWNER_RULINGS_2_P309_VERBATIM.md` (lines 85–164 and a grep).
* The postmortem, the three postmortem reviews, and `handoff/OVERNIGHT_REPORT_P309.md` §§9–11.
* r1 code, in part:
  * the driver, guard and runner;
  * `test_p309_exactly_once.py`, `test_p309_guard.py` and `test_p309_site_backstop.py`;
  * `scoped_sandbox.py`, the self-audit and the checkpoint push;
  * the static check, the scanner, `u2_structure_check.py` and `make_freeze_manifest.py`;
  * greps of the variant and `make_freeze_params.py`.
* The structure of the allowance config.
* The manifest's runtime and the namespaces of its pins (metadata).
* `verify/VERIFY_RESULTS_SCOPED.json`: top-level keys and harness/variant metadata only.
* The r1 execution ledger: counters only, plus the utc, class and opening `purpose` text of one row found by grep (the
  disk-exhaustion row).
* The import lines and `math.` call lines of the research producer modules `impl/srk_float.py` and
  `impl/srk_kernel.py`.

**Runs.**
* Read-only git: `rev-parse`, `log`, `show --stat`, `diff --stat`/`--name-only`/`--quiet`, `ls-tree`, `for-each-ref`,
  `branch -a`, `merge-base --is-ancestor`, `cat-file -t`, `count-objects`, `status`.
* `sha256sum` of the plan and the brief.
* One in-memory Python AST analysis: `ast.parse` only; nothing imported or executed; no file written; **not
  evidence**.
* No `ls-remote` or other network call. No scratch diagnostic. No campaign code. No `execute`, `seal-only` or
  `validate-grant`, and no QC item.

**Writes.** This file and my scratch ledger only. No git write of any kind.

**Firewall.**
* No value for cells 305–309 was read.
* No cell-307 or cell-308 file was read or hashed. I saw only directory names from `ls-tree`, and the namespace names
  of the manifest's pins.
* No QC09 decoy output (cover cells 297 and 316) was opened, and no decoy result is quoted.
* No ref under `refs/p5y-k5-cell309-p309-r1/` or `refs/p5y-k5-cell309-p309-r2/` was created, armed or consumed.
