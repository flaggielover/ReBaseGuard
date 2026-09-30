# Independent pre-freeze review R4 (FC2 code/spec review + FC1/FC3–FC6 + QC design), formal campaign p5y_k5_cell309_p309_r1
FREEZE_BLOCKED

**Reviewer.** Independent reviewer R4, a subagent that wrote none of the reviewed code or documents. It is not R1, R2,
R3, the incident-independence reviewer, the delta reviewer or the verifier's author. Brief:
`reviews/BRIEF_PREFREEZE_R4_P309.md` (committed before issue, 08acd6a2).

**State reviewed.** Branch `claude/p5y-k5-cell309-p309-r1` at HEAD 7fe020c8. The review began at 4f51a2df and followed
the coordinator's two addenda:
* the delta review e53a678c;
* the verifier author's E1-1/E1-5 change 4286c527;
* FE-8 and the fixtures f3bc541b;
* D3 and D5, 8fbb982e and 88195515, which do not touch the reviewed code.

File sha256 prefixes at HEAD:

| file | sha256 prefix |
|---|---|
| `code/p309_driver.py` | `2e0739e94f89` |
| `code/p309_guard.py` | `676568482a8f` |
| `verify/srk_verify_indep_scoped.py` | `9d9f8cec52cf` |
| `verify/run_verify_all_scoped.py` | `2dc92f5697a5` |
| `code/p309_postexec.py` | `caf829b4a1a5` |
| `code/p309_qualify.py` | `1f9ea5f05030` |
| `code/p309_static_check.py` | `1de47aa8600c` |
| `code/p309_scan.py` | `01993d13af03` |
| `config/SCANNER_ALLOWANCE_P309.json` | `0415fa366441` |
| `tests/test_p309_exactly_once.py` | `1b08bf5233ef` |
| `tests/test_p309_guard.py` | `7d6d9bbfa10a` |
| `tests/test_verify_scoped.py` | `1483d6c2f5c9` |

Line numbers below refer to these versions.

**Standard.** The standard is the owner's two authority documents, protocol and package rev. 2b, the rev. 2c amendments
(including the appended D2 correction), `fc2/FC2_SPEC_R2.md` with erratum 1 (E1-1 to E1-6), and the U2 documents.

---

## 1. Verdict in brief

**FREEZE_BLOCKED.** The admission mechanism (guard and variant) meets the owner's list on its own terms: it fails
closed, it contains no grant, it creates no marker, and it keeps test and production structurally separate. The variant's
E1-1/E1-5 change is exactly what it claims (D8 confirmed, §3).

The driver and the QC design around the mechanism are not ready to freeze. There are eight blocking findings, B1–B8:
* **One threatens validity.** The cell is taken from the grant, and is never checked against the pinned `cells.json`
  (B1).
* **Two would turn a correct execution into EXECUTION_INDETERMINATE.**
  * The post-seal re-verification cannot parse the driver's sealed record, and postexec cannot run seal-only in
    production (B2).
  * The grant fields that admission needs are checked only after the marker (B3).
* **One contradicts the owner's failure semantics.** A worker killed by SIGKILL becomes a fallback (B4).
* **One makes the grant window procedurally impossible.** The handoff, ledger lines and host re-run cannot be committed
  between the review commit Rv and the grant commit G, and cannot be left uncommitted either (B5).
* **One is a recording gap.** Verdict reasons are not sealed (B6).
* **Two are QC design defects.**
  * The QC suite never runs the post-marker evaluation path. QC13's temporal checks are tautological. The guard lacks
    the production-critical E1-1 positive test (B7).
  * The QC runner allows a failed gate to be re-run with its evidence overwritten (B8).

Each finding has a small, concrete fix. None needs a new scientific parameter. B3 needs one new frozen rule (a minimum
grant horizon), B5 needs an A8 amendment, and both are deltas under C2.

The coordinator found and fixed FE-8 (f3bc541b). R4 had independently reproduced it at 03:57Z, before being told
(ledger line R4-7): Stage 1b could not load its certifier after the SRK imports in `execute`. The fix is correct (§3.3).
FE-8 is the pattern behind B7(a): the post-marker code path has never run as a whole.

---

## 2. Blocking findings

### B1. The target cell comes from the grant, not from the pinned `cells.json` (validity)

* **Where.**
  * `code/p309_driver.py:1032`: `cell = tuple(F(x) for x in grant["cell_interval"])`.
  * That value feeds the historical control (1042), Stage 1a (`stage1a("target", cell, …)`), Stage 1b
    (`S1.blocks_for(cell…)`) and Stage 2 (`evaluate_srk(…, cell, gate_result, …)`).
  * The only cross-checks are:
    * Ew equals the hull of the grant's own `cell_interval` (1033–1037);
    * `srk_adapter._bound_gamma` checks `rho == (c1 − c0)/2`, which compares the **width** only.
* **Failure scenario.** A grant whose `cell_interval` has the right width but the wrong centre passes every check. The
  neighbouring cell's interval, copied by mistake, is an example; in a regular cover it has the same width.
  * Stage 1a certifies Ew′ and Stage 1b certifies the wrong blocks. Both are in-band, and possibly on cell 308's drift
    range, which the owner put out of bounds.
  * The gate and the adapter accept the GateResult, because it is bound to the same wrong cell.
  * Stage 2 then combines cell 309's measurement with certificates that do not cover cell 309's drift range. A sealed
    CELL309_CLOSED_UNDER_P309 could rest on an invalid enclosure.
* **What it contradicts.**
  * Protocol §2.1 ("C … from the pinned `cells.json`").
  * Package §A and FC4 ("the cell from the pinned cells.json as exact rationals").
  * The freeze's own `post_grant_derivations.cell_interval` rule.
  * `NO_PLACEHOLDER_STATEMENT_P309.md` §2, which claims the derivation is enforced.
* **Fix I would accept.**
  * In `run_execute`, before the historical control and in the PRODUCTION context, derive C from the pinned
    `cells.json`. Use the CUSUM filter and index 309, as exact rationals: the same rule as
    `make_proposed_authorization.py:63–65`, or `con["cover"][309]`.
  * Refuse with exit 2 and no marker unless `grant.cell_interval` equals C exactly and `grant.drift_hull_Ew` equals
    `cell_blocks(C)[0]`.
  * Use the `cells.json` value of C everywhere afterwards.
  * Add a QC11 flow in which a same-width, shifted `cell_interval` is refused before the marker.

### B2. The post-execution checks fail on a correct production run (P10 and P5 → EXECUTION_INDETERMINATE)

* **(a) P10: the review mode cannot find the sealed certificates.**
  * The variant's review mode reads `json.loads(result)['stage1a']['certificates']` at the **top level**
    (`verify/srk_verify_indep_scoped.py:604`), as spec §3 says.
  * The driver seals Stage 1a under **`target.stage1a`** (`p309_driver.py:947` inside `evaluate_target`, then
    `common["target"] = tgt` at 978).
  * **Demonstrated.** `scratchpad/r4/review_mode_shape.py` used a light sandbox, TEST names and the descriptor of a
    committed h3 decoy certificate, with admission only:
    * a top-level `stage1a` gives ADMIT;
    * the driver's shape gives `REFUSE … the sealed result does not parse (stage1a.certificates)`.
  * **Consequence.** In production every sealed certificate re-verifies as REFUSE, so `p309_postexec.reverify_production`
    returns False. By protocol §5 (post-seal row) the outcome is EXECUTION_INDETERMINATE for **every run in which SRK
    admitted a certificate**, which includes every run that could close through SRK.
* **(b) P5: seal-only refuses without the interpreter flags.** `p309_postexec.checks` calls `D.run_seal_only(ctx)`
  (postexec 67). In production that calls `check_flags()` (driver 1077, 234–236), which requires `python3 -I -S -B`.
  * The documented invocation is `python3 code/p309_postexec.py`, so the result is Refusal INTERPRETER_FLAGS, then
    P5 = False, then `outcome_if_failed = "EXECUTION_INDETERMINATE"`.
  * Since f3bc541b the refusal is caught and turned into a failed check, so the checker no longer crashes; the failure
    stays.
* **Why QC11 misses both.** F27 calls `PX.checks` with `reverify=None`, and SANDBOX contexts skip `check_flags`.
* **Fix I would accept.**
  * The driver seals a **top-level** `"stage1a": {"certificates": [...]}`, as spec §3 requires. This is a driver-side
    change. A spec erratum plus a variant change would be a larger delta.
  * Postexec gets a frozen invocation, `python3 -I -S -B code/p309_postexec.py`, and refuses to start without those
    flags (rather than recording P5 = False).
  * Add a QC11 flow covering the driver-to-variant integration:
    * the driver's SANDBOX context takes the result path from the test context (`TEST_ONLY/P309_TEST_RESULT.json`);
    * a stub evaluator returns the 16 committed TEST-band h3 certificates as Stage-1a certificates, with verdicts;
    * P10 runs the real variant in review mode through `reverify`, and must equal the sealed verdicts;
    * P5 runs through the production flag path.

### B3. The admission preconditions are checked only after the marker (avoidable post-marker failures)

* **Where.** Admission checks 2, 4, 5, 6, 8 and 9, and the parts of check 7 that do not depend on the marker, run only
  inside `admission_decision`:
  * the guard, `code/p309_guard.py:249–309`;
  * the variant, 530–569.

  Both are called only after `_arm_marker` (driver 1069). `check_grant` (312–387) validates only:
  * `schema`;
  * `cell`, by `!=` (309.0 passes);
  * `closure_only` and `executions_authorized`;
  * the driver sha and the manifest sha;
  * the chain.
* **Not checked before the marker:**
  * `campaign`;
  * `geometry` as the exact strings (E1-3: the variant refuses "5/1");
  * `cell` as the exact int type (both implementations refuse 309.0);
  * `verifier_id` = `sha256:` + pin(variant), and `guard_id` = `sha256:` + pin(guard);
  * `marker_ref`;
  * `execution_host.host_id_sha256`, which includes the hostname and so may change if the container is re-provisioned;
  * `execution_host.worktree` (A9);
  * `runtime.python` and the platform string (package §C step 2);
  * `not_after_utc`, both its format and its remaining validity. The committed proposal tool emits
    `"<SET BY THE OWNER, ISO-8601 UTC, …>"` (`make_proposed_authorization.py:120`);
  * that exactly one commit adds the grant path (guard check 4);
  * that HEAD is attached to a branch. The guard raises on a detached HEAD at `p309_guard.py:287`, so every guard call
    refuses, and the seal fails at driver 875;
  * that no ref other than the current branch points at a strict descendant of G. For example, a pushed
    checkpoint-record commit on top of G, with the local branch reset to G;
  * that a git committer identity exists for the seal.
* **Failure scenario.** Any one of these is wrong or missing, and `execute` arms the marker. Then:
  1. The guard refuses inside the producer.
  2. QuarantineRefusal becomes JOB_EXCEPTION, and the result is EXECUTION_INDETERMINATE: the single evaluation is spent.
  3. Variant refusals alone would give an all-REFUSE fallback: SRK silently contributes nothing.

  In addition, expiry is re-checked on **every** guard and verifier call during the run, while rev. 2c A6 (corrected)
  leaves wall time unbounded. A grant that expires mid-run therefore turns a slow host into EXECUTION_INDETERMINATE,
  which is the host-speed route that A6 set out to remove.
* **Fix I would accept.**
  * Add a pre-marker "dry admission" step to `run_execute`, after `check_grant` and before `_arm_marker`. It verifies
    every item above against the frozen and pinned values, and the live host, runtime, refs and HEAD. It refuses with
    exit 2 and no marker. (Optionally both implementations expose a pre-marker admission mode covering checks 1–6,
    8–10 and the marker-independent part of 7; the driver-side check suffices.)
  * Freeze a **minimum remaining validity** at arming, for example `not_after_utc ≥ now + 14 days`, as a stated
    grant-preparation rule. This is a new rule and a delta under C2.
  * Add one QC11 flow per condition, each asserting exit 2 and no marker.

### B4. A SIGKILL below the CPU limit is treated as budget exhaustion (a runtime failure becomes a fallback)

* **Where.** `p309_driver.py:608`:
  `if sig in (signal.SIGXCPU, signal.SIGKILL) or cpu >= job_limit_s: done[idx] = {"kind": "TERMINATED_JOB_LIMIT", …}`.
  It applies to Stage 1a and to Stage 1b.
* **Failure scenario.** An OOM kill, or any `kill -9` of a worker, at a CPU time far below the 12 CPU-h (or 21 600 s)
  limit is classified as a budget termination. The outputs are discarded, and the result is a fallback (Stage 1a) or a
  missing rung (Stage 1b), not a post-marker failure.
  * The owner's STAGE-1a FAILURE SEMANTICS say "an actual software/runtime exception after the exactly-once marker has
    been consumed -> EXECUTION_INDETERMINATE … Do not convert a post-marker software exception into a fallback".
  * Protocol §2.5 lists only "stopped by the budget mechanics" as a fallback, and protocol §3 makes Stage-1b exceptions
    INDETERMINATE.
  * It also hands the operator a post-marker lever: kill a chosen worker, and get a fallback for that job.
* **Fix I would accept.**
  * `TERMINATED_JOB_LIMIT` only when the kernel's CPU-limit enforcement ended the job: SIGXCPU, or SIGKILL with
    `cpu ≥ job_limit_s`.
  * Every other abnormal end gives `JOB_EXCEPTION`, so the stage raises.
  * Add a QC11 flow in which a stub child SIGKILLs itself at low CPU and the stage must raise.
  * Also set `RLIMIT_CORE = 0` in the job's `preexec_fn`, because SIGXCPU's default action dumps core into the cwd.

### B5. The window from Rv through G to `execute` cannot be kept consistent (A8 as coded)

* **Where.**
  * `check_grant` (driver 342–369) allows only checkpoint-record commits (`ledger/CHECKPOINT_PUSHES.jsonl`) between
    Q, Rv and G.
  * Rv may touch only `reviews/REVIEW_QUALIFICATION_P309*`.
  * HEAD must equal G.
  * `check_clean` (281–285) requires a clean tree, including ignored files in the namespace.
* **What must happen in that window under the committed procedures:**
  * `make_proposed_authorization.py` writes an EXPOSURE_LEDGER line (line 60) and `handoff/PROPOSED_…json` (124–127);
  * the qualification reviewer's executions are "transcribed by the coordinator" into the ledger
    (`RNS/protocol_prep/P309_REVIEW_BRIEFS.md:20`);
  * A14 requires QC10 to be re-run on a different named host, and its evidence has no place to go;
  * any ledgered action after G (for example preflight or the self-audit) dirties the tree.
* **Failure scenario.**
  * **Committing** any of these between Rv and G makes `check_grant` refuse permanently. The chain cannot be repaired
    without rewriting history, which the owner forbids.
  * **Leaving them uncommitted** gives DIRTY_TREE at `execute`.
  * **Deleting them** violates "every execution is ledgered" and incident review C4.
* **Fix I would accept.** Before the freeze:
  * amend A8 and `check_grant` so that, between Rv and G, commits are allowed that touch only an enumerated set, checked
    path by path: the three ledger files, `handoff/…`, and the qualification review's own execution ledger;
  * state that nothing ledgered may run between G and `execute`, or say where such lines go;
  * say where A14's host re-run evidence is committed (before G);
  * add QC11 flows for allowed and forbidden interleavings.

  This is a delta under C2.

### B6. Stage-1a verdict reasons are not sealed

* **Where.**
  * `srk_gate.verdicts_from_verifier` keeps only `["verdict"]` (`RNS/impl/srk_gate.py:106`).
  * The job returns those strings (`p309_driver.py:667–672`), and they are all that is sealed.
* **What it contradicts.** Protocol §2.6 and package §E require "all verdicts (with reasons)".
* **Consequence.** The sealed record cannot tell an admission REFUSE (expiry, host, …) from a mathematical REJECT. The
  execution review needs that distinction, especially together with B3.
* **Fix I would accept.**
  * Pass `verdicts_from_verifier` a recording proxy of the pinned variant. It has the same `__file__`, so
    `verifier_identity` is unchanged, and it delegates `verify_cert` while keeping each full result (verdict, reason,
    admission, boxes, maxdepth).
  * Seal these as `stage1a.verdict_details`.
  * QC08 and QC11 assert that they are present.

### B7. QC blind spots: the post-marker path, production-only branches, the tautological QC13, and the guard's E1-1 path

* **(a) `evaluate_target` (driver 937–949) has never run as a whole, not even on decoys.**
  * The decoy modes run Stage 1a and Stage 1b in separate fresh processes.
  * QC11 stubs the whole evaluator, and QC14′ does not load the RLR307 certifier.
  * FE-8 was found only because S10 happened to run after S01–S08 imported the SRK side. B2(a) was not found.
  * **Fix.** Parameterize the evaluation by mode and cell, so that one function body serves `execute` and QC. Add a QC
    flow that runs it in one process, in `execute`'s import order, on the declared decoys:
    * stub job runners return committed decoy certificates and records;
    * then `compose_S`, the independent S check, `evaluate_srk` on manufactured inputs, `decide`, and `serialize()`
      (without `default=str`);
    * then the sandbox seal and P1–P10 with B2's integration.
* **(b) The production-only pre-marker branches are never exercised.** In SANDBOX contexts these are skipped:
  * `check_grant`'s field checks (335–337);
  * the Ew check (1033–1037);
  * `check_flags`;
  * the new B1 and B3 checks.

  **Fix.** Parameterize them by context, so that the sandbox runs them on test values, and add one refusal flow each.
* **(c) QC13's temporal checks are tautological** (`p309_qualify.py:216–224, 269`).
  * `freeze` is `D.freeze_commit()`, the last commit that touches the frozen directories. So
    "freeze_is_last_frozen_change", "frozen_dirs_unchanged_since_freeze" and "qualification_after_freeze" hold by
    construction.
  * An accidental change to a frozen directory after the reviewed freeze would silently become "the freeze".
  * **Fix.** Record the freeze commit independently at the freeze (for example a freeze record committed in the next
    commit). Have QC13, the QC runner, the proposal tool and `check_grant` compare against it.
* **(d) The guard's tests never exercise E1-1's positive case: a non-current ref exactly at G must ADMIT.**
  * In production the remote-tracking ref will be exactly that.
  * `N7h` covers only a strict descendant.
  * **Fix.** Add the positive case. Add a detached-HEAD case once B3 has settled the rule.

### B8. The QC runner allows retry-until-pass with the failed evidence overwritten

* **Where.** `p309_qualify.py:307–319`.
  * `--only` re-runs selected items.
  * `qualification/QCxx.json` is overwritten.
  * The summary passes if the latest files pass.
* **What it contradicts.** The owner's instructions "Preserve the complete qualification evidence" and "Do not silently …
  weaken a failed qualification gate". A re-run after seeing a failure is a post-result choice built into the frozen
  tool.
* **Fix I would accept.**
  * Write each attempt with O_EXCL under an attempt number, and never overwrite.
  * `P309_QUALIFICATION.json` passes only if a single complete run passes every gate, or else under a frozen, reviewed
    retry rule. My recommendation is no retry.

---

## 3. The coordinator's addenda: D8, D2, D5, FE-8

### 3.1 D8: confirmed

`git diff 6522db10 4286c527` over `verify/` and `tests/test_verify_scoped.py` changes only E1-1 and E1-5:

| file | change |
|---|---|
| **variant** | two lines, `srk_verify_indep_scoped.py:562–563`: `c != G and _is_ancestor(repo, G, c)`, plus the message. sha256 `9d9f8cec…` (verified) |
| **harness** | `--out` added, default unchanged. `out_path` is used in `flush`, in the I1-end ledger note and in the `--skip-i1` merge. sha `2dc92f56…` |
| **tests** | N7 only. A ref at G must ADMIT, and a ref at a child of G must REFUSE "strict descendant". sha `1483d6c2…` |
| **README** | identities and erratum text only |
| **`VERIFY_RESULTS_SCOPED.json`** | apart from `i1_sec`, every difference is a permutation of the `differences` lists (parallel completion order). The multisets and all counts are identical: production 87/87 genuine, 1914/1914 mutants; test_context 16/16 and 352/352. Unit tests 37/37 |

No other point changed.

### 3.2 D2: my view

**No change to the Stage-1b per-job limit is required.** Keep 21 600 s.
* Rev. 2b §3, which the owner authorized, states no per-job limit.
* A per-job limit equal to the start threshold is the minimal addition: no binding constraint below the budget.
* A smaller value, such as 5 400 s, is efficacy-relevant in both directions. Without a target-free cost basis there is
  no principled reason to prefer it.

The appended A5/A6 correction (f3bc541b) is necessary and sufficient, with one precision: the hard limit is the soft limit
plus 5 s (`resource.setrlimit(RLIMIT_CPU, (lim, lim + 5))`), so the bound is < threshold + 4 × (limit + 5 s).

S14 checks the frozen order and values as the runner receives them. S06 and S07 cover the mechanics. That satisfies D2's
QC11 clause.

### 3.3 FE-8: the fix is correct

`_load_certifier_isolated` (driver 735–749):
1. It pops `LOAD_ORDER` and `ov_quarantine`.
2. It calls the unchanged pinned loader.
3. It restores the table in `finally`.

I checked two things:
* The pinned C1B modules make no function-level imports of the `LOAD_ORDER` names (masked skeletons; only `c1b_gauss`
  imports `math` locally). So after the restore, the certifier's module-level bindings stay self-consistent.
* A probe (`scratchpad/r4/fe8_probe.py`, ledgered) imported `srk_certify` and `srk_gate` first, then:
  * the load succeeded, with the identity check true;
  * the module table was unchanged;
  * `certpw.Q` is the adapter;
  * the certifier holds its own pinned `c1b_gauss`;
  * `kappa_check` was true.

S13 is a sufficient regression test for this defect. B7(a) remains for the class of defect.

### 3.4 D5

On the technical question, the pending-ref NAME extension (A10) and the two sanctioned sites (A10/A19) are as narrow as
the owner's scanner ruling can reasonably be extended:
* a single file, under the same conditions (a)–(e);
* the sites are bound by file, function name and `ast.dump` sha;
* each site begins with `_assert_execute_context`;
* their callers are restricted by QC12 T4.

They remain an extension of an owner ruling, so D5's owner ratification is required, and it is not something R4 can
supply. The `ast.dump` hashes depend on the Python version (3.13 changed `ast.dump`'s output). That is fine under the
pinned 3.11 runtime.

---

## 4. Section A: FC2 code and spec review (owner rulings 2)

| owner requirement | guard (`code/p309_guard.py`) | variant (`verify/srk_verify_indep_scoped.py`) |
|---|---|---|
| fail closed by default | every check sits inside one `try`; any exception gives REFUSE (312–336); `guard_interval` raises | `admission_decision` catches everything and returns REFUSE (491–499); `verify_cert` refuses at parse time |
| no embedded valid production grant | none | none |
| no implicit grant, no default admission | none; NOT_BANDED is not an admission (E1-2) | "meets no band" is not a band admission (E1-2) |
| no production marker creation | read-only git verbs only (show, log, diff-tree, rev-parse, merge-base, for-each-ref, symbolic-ref) | read-only git verbs only (verified by grep) |
| no real in-band computation | the D1 items are dry | dry; the harness tripwire refuses evaluation |
| no target-derived constants | only the inherited band, the synthetic TEST band and the cell id | the same |
| no test-only bypass reachable from production | REAL band needs `ctx is PRODUCTION`; TEST band needs exactly `TestContext` | the same (518–529); the CLI `--test-sandbox` can only admit the TEST band |
| grant bound to protocol/hash, 309, Ew, verifier, host, marker | checks 2–10 | checks 2–10, plus review mode |

The binding holds only once the marker exists (B3), and the cell is never bound to `cells.json` (B1).

**Remaining items of the owner's list:**
* **Malformed, missing or mismatched grants are refused:** yes. Guard N1–N8 (52/52 in the committed `evidence/fc2/GUARD_TESTS.json`, guard sha `676568482a8f`); variant
  N01–N13 (37/37).
* **Synthetic artifacts cannot authorize production:** yes, through the structural separation and N9–N11.
* **Production admission before the owner's grant is impossible mechanically.** It needs a grant file added by one commit
  that is G = HEAD, plus the frozen chain and the marker. Code cannot authenticate the owner (see NB8); that stays a
  governance matter.

**Test power.**
* **Variant tests:** strong. They assert reason fragments, carry positive controls within the negatives (N02, N09), and
  use a prepare-tripwire.
* **Guard tests:**
  * They assert only `REFUSE`, never the reason (NB2).
  * They lack the E1-1 positive case (B7(d)).
* **Harness I1:** its expectation rule was recorded before the run, and it predicts independently from its own band
  table. However, its tripwire classifies with the variant's `cert.bands`, not with its own table (NB3).
* **Scanner controls C1–C15:** they are sound for what they test. I showed that the formal rules miss local aliasing (NB1).

**Is the scanner allowance as narrow as the ruling requires?** Yes:
* exact files;
* one module-level assignment to one constant;
* no rebinding;
* no mutating call naming it;
* listed in the config;
* allowed findings are listed, never dropped.

It does not bind file hashes. The manifest pins them at the freeze, which is acceptable.

**Independence of authorship (spec §9).**
* The README records the author session as `session_01RiV5bfPm5GJ4GcvoBrCC3p`. That is the **same top-level session**
  that signs the coordinator's commits.
* Independence therefore rests on:
  * subagent separation;
  * the declared list of sources read, with no guard or producer code;
  * the independent divergences found (E1-1 to E1-4).
* That is procedurally acceptable. The README should say so plainly and record the author agent's own identifier (NB9).

---

## 5. Section B: the driver and the qualification machinery

**Stage 1a.** These are correct:
* 12 jobs, rung-major (`stage1a_jobs`);
* the start-threshold accounting with live CPU;
* the 12 CPU-h RLIMIT_CPU limit;
* no raising for budget reasons;
* per-rung serialization: `run_block` with `ladder=(d,)`, then `certificate_json` of a single-rung record;
* in-process verdicts at N = 8 and max_depth = 24, statically enforced by QC12 T2;
* the `verdict_source` check;
* the pinned gate;
* job exceptions give EXECUTION_INDETERMINATE.

Defects: B1 (the cell), B4 (SIGKILL) and B6 (reasons).

**Stage 1b.** These are correct:
* the RLR307 helpers at their pinned bytes;
* the degree-descending order;
* per-rung and per-block independent reconstruction, and the cell composition cross-check;
* the fallback to S_I1;
* the adapter injected as `ov_quarantine`, through `c1b_certpw`'s `Q.guard_drift` and `Q.log_execution`, whose
  signatures are compatible;
* FE-8, now fixed.

A4's text says "execute mode only", but the code injects the adapter in every mode. That is harmless, but the text or the
code should change (NB7).

**Stage 2.** These are correct:
* `compose_S`, with A0 from I1 and the independent `consumed` check;
* the TC-T crosscheck, then the adapter, then the pinned `direct` through the argument-checked shim (A11);
* the two-part historical control (A12);
* the A13 record binding.

Pre-marker exceptions in the control are not sealed as CONTROL_FAILED (NB5).

**Exactly-once.** These are sound:
* the CAS from the zero OID for the marker and the pending ref;
* the O_EXCL|O_NOFOLLOW emergency file;
* the private-index seal with the branch CAS;
* O_EXCL materialization through a dirfd chain, with read-back;
* seal-only;
* exit codes 0, 2–7;
* signals ignored after the marker.

Gaps:
* the pre-marker completeness (B3);
* the grant window (B5);
* the postexec invocation (B2(b));
* test hooks are honoured in production (NB4);
* `_job` target mode can be started outside `execute` (NB6).

**The QC suite, item by item (as implemented):**

| QC | as implemented | status |
|---|---|---|
| QC01–QC04 | research tests in a `git archive` mirror of the freeze commit; QC04 also under -O | as specified |
| QC05 | the adapter test, and pinned re-assembly equality on 12 manufactured seeds | as specified |
| QC06 | research verifier v2 battery against the committed results; 21 self-tests | as specified |
| QC07 | MC control | as specified |
| QC08 | driver decoy Stage 1a (a2_h5): 12 jobs, all ACCEPT, byte identity with the research best rung, gate/W-record/mutant/e2e batteries | adequate, except B6 |
| QC09 | decoy Stage 1b on 297 and 316, with the independent checks | adequate; the `execute` import order is now covered by S13 |
| QC10 | QC08 against QC10 on this host | adequate; the owner-named host re-run has no recording path (B5) |
| QC11 | 54 flows (dev, per the coordinator) | gaps B2, B3, B4, B7(a)(b); code-only assertions (NB2) |
| QC12 | T1–T5 | pass (R4 re-run at c58c66b2). A16's consumer-call ban lives in QC-U2, not QC12; fix the text (NB10) |
| QC13 | governance checks | partly tautological (B7(c)) |
| QC14′ | R1–R5 | as specified |
| QC15 | self-audit | ok (R4 re-run, label R4b); its immutable list is incomplete (NB11) |
| QC16 | variant I1 and tests, guard tests, scanner controls | see §4; B7(d) |
| QC17 | 2 000 manufactured cases against the independent reconstruction | as specified |
| QC-U2 | U2 checker and controls | pass (R4 re-run) |

---

## 6. Section C: readiness to freeze

**Must change before the freeze:** B1–B8.

**What the freeze would otherwise carry:**

| category | open item |
|---|---|
| unresolved placeholder | none in the frozen directories (the proposal's owner fields live in `handoff/`, outside them). B3 requires that the driver refuse placeholder or short-horizon values |
| mutable scientific decision | D2 is settled (unchanged). The minimum grant horizon (B3) must be frozen |
| post-result choice | the QC runner's re-runs (B8); the operator's kill lever (B4); `_job` target mode outside `execute` (NB6) |
| rule ambiguous in code | the cell source (B1); SIGKILL (B4); the grant window (B5); the freeze identity (B7(c)); CONTROL_FAILED raised as an exception (NB5) |

### Non-blocking notes

* **NB1. The scanner's formal rules miss local aliasing** (demonstrated on in-memory snippets, static):
  * `r = ctx.marker_ref; git("update-ref", r, …)` gives no finding;
  * `p = ctx.pending_ref; git("update-ref", "-d", p)` gives no finding;
  * `p = ctx.guard_ctx.grant_path; Path(p).write_text(…)` gives no finding.

  Recommendations:
  * every mutating git call in FNS should be a reviewed site, or carry only literal non-production refs or
    `ctx.branch_ref`;
  * GRANT_WRITE should track `grant_path`.

  The current code has no such evasion.
* **NB2.** The guard's negative tests, and the QC11 refusal flows, should assert the reason or detail, not only the code.
* **NB3.** The harness tripwire should classify with the harness's own table (`own_bands`), for strict §7(c)
  independence.
* **NB4.** `run_execute`'s hooks (`prepare`, `evaluator`, `persist`, `sealer`, `materializer`, `control`) should be
  refused unless `ctx.kind == "SANDBOX"`.
* **NB5. Pre-marker exceptions.**
  * Any exception in the historical control should be sealed as CONTROL_FAILED (exit 3). Examples: the adapter's
    REPRODUCTION_FAILED in part (b), and IndependentCheckFailed. Protocol §4 says "any mismatch … STOP".
  * Every other pre-marker exception should give exit 2, not a traceback with exit 1.
* **NB6. The `_job` CLI accepts `"mode": "target"` with no link to a running `execute`.** While the marker is the only ref
  in its namespace and HEAD = G, an in-band job started separately would be admitted. That holds during `execute`, and
  indefinitely after CONSUMED_UNRECORDED. Recommendations:
  * bind target jobs to the run: a nonce created with O_EXCL in the git dir before arming, and removed once the pending
    ref exists;
  * have the guard refuse while an emergency file exists.
* **NB7.** Two text fixes:
  * the A4 and spec §5 wording ("execute mode only") against the code;
  * target-mode adapter records carry the producer's labels (NONTARGET_DECOY / NONTARGET_DRIFT_VALIDATION); label them
    in the sealed record.
* **NB8.** No code checks the grant's `authority` or `issued_utc`. Require non-placeholder values before the marker
  (with B3). Owner authenticity itself stays procedural.
* **NB9.** The variant's README should state that the author and the coordinator share one top-level session, and give
  the author agent's identifier.
* **NB10.** Fix the text that places A16's items in QC12; they live in QC-U2.
* **NB11.** The self-audit's A3 IMMUTABLE list should add the committed briefs, the delta review and its ledger, this
  review, and (after the freeze) the FC2 spec and its erratum.
* **NB12.** The variant tests still use `git clone --shared` sandboxes, about 445 MB each and sequential. Use E1-6 light
  sandboxes for QC16, given about 28 GB free.
* **NB13.** `make_freeze_params.py` carries no conditions for `prefreeze_r4` (heading `None`). Use this review's heading
  "## 7. Conditions".
* **NB14.** Job children run without `-I -S` (driver 635), while the parent insists on `-I -S -B`. Use the same flags.
* **NB15.** The execution procedure should say three things:
  * remove `__pycache__` from the namespace (`check_clean --ignored` refuses otherwise);
  * run on the named branch, in the named worktree;
  * use postexec's flags (B2(b)).

---

## 7. Conditions

* **R4-C1.** B1–B8 are fixed, with the accepted fixes or equivalents that close the same failure scenarios. B3's
  minimum-horizon rule and B5's A8 amendment are new deltas under C2, and go to the delta reviewer before the freeze.
* **R4-C2.** A focused re-review of the fixes, by R4 or another independent reviewer, before the freeze. It covers:
  * the new QC11 flows (B2, B3, B4, B7);
  * one full dev run of `test_p309_exactly_once.py`, guard tests and variant tests at the candidate freeze tree.
* **R4-C3.** D5, the owner's ratification of the A10 and A19 extensions, is obtained before the freeze. R4 finds the
  extensions technically narrow.
* **R4-C4.** D2 stays as appended: 21 600 s, with the bound precision noted in §3.2.
* **R4-C5.** The non-blocking notes NB1–NB15 are either applied before the freeze or recorded as accepted residuals, each
  with a reason.

---

## 8. Reviewer disclosures, executions and firewall

**Reads.**
* FNS and RNS files, and git metadata.
* The pinned RLR307 helpers and the C1B modules, **only** through `code/code_skeleton.py`, with numbers masked. The C1B
  modules were read for import structure only.
* No consumer code (`tct_rule`, `tc_rule`, `c2_d5_forecast`, `tail_forecast_r2`, `deflated_consume`) was opened.
* `THEOREM_TCT.md` was not opened.
* No target input file was read.
* No 305–309 value was seen.
* Seen:
  * decoy and test-band values (h3 decoy mutant reasons in the I1 diff);
  * band literals;
  * the coordinator's scratch dev-run outputs (pass/fail lines and a traceback);
  * the file names (not contents) in the mirrored C1B directory.

**Executions.** All were target-free. There were 18 ledger lines through `code/p309_env.py`, each note prefixed
"R4 reviewer:".

| # | ledger line (UTC) | class | what |
|---|---|---|---|
| 1 | 03:51:04 | SYNTHETIC | rev-list and blob-ref check in a throwaway `git init` repo |
| 2 | 03:51:42 | SYNTHETIC | `review_mode_shape.py` (B2(a) demonstration) |
| 3 | 03:53:45 | GOVERNANCE | RLR307 skeletons |
| 4–5 | 03:55:34, 03:55:43 | SYNTHETIC | `f27_probe.py`, QC11 F27 alone, run twice |
| 6 | 03:56:03 | SYNTHETIC | `chain_probe.py` (the empty sandbox freeze commit, since fixed by the nonce) |
| 7 | 03:57:03 | SYNTHETIC | `pinerror_probe.py` (FE-8 reproduced) |
| 8–13 | 03:58:16 | GOVERNANCE | the scan, static check, U2 checker, U2 controls, scanner-allowance controls, self-audit |
| 14 | 04:04:46 | GOVERNANCE | scanner aliasing snippets |
| 15 | 04:05:04 | GOVERNANCE | C1B skeletons |
| 16 | 04:05:47 | SYNTHETIC | `fe8_probe.py` |
| 17 | 04:06:36 | GOVERNANCE | scan re-run at c58c66b2 |
| 18 | 04:07:35 | GOVERNANCE | static check and self-audit re-run |

**How the executions were contained.**
* Evidence went to `scratchpad/r4/evidence` (`P309_EVIDENCE_DIR`).
* The sandboxes were light repositories (`git init` plus alternates plus the copied `shallow` file) under `scratchpad/r4`,
  with TEST names only. All were deleted.

**What was never done.**
* `execute` and `seal-only` were never run.
* No evaluation was made for cells 305–309, and no kernel ran in the band.
* No ref was created under `refs/p5y-k5-cell309-p309-r1/`, anywhere. Checked: 0 in this repository, and 0 `refs/p309-test/`
  refs in this repository.
* The production grant path was never written.
* No git write was made in this repository.

**Writes.** This file only. The ledger lines went through `p309_env`, as the brief instructs; the coordinator has
already committed 16 of the 18 lines.

NEW Γ309 TARGET EVALUATIONS = 0.
