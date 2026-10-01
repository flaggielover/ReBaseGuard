# Brief: focused follow-up of the r2 delta review (repair round 1)

This brief is committed before it is issued (C5 of the r1 governance, kept for r2).

## Who and what

**Recipient.** A **fresh** independent reviewer. You wrote none of these:
* the r2 code or its repairs;
* the verifier author's changes;
* the r2 plan or its addenda;
* any earlier r2 review, including the delta review (`governance/REVIEW_R2_DELTA.md`).

**Boundaries:**
* no git write of any kind (no commit, ref, stash, config, fetch or push);
* NEW Γ309 TARGET EVALUATIONS = 0: never run `p309_driver.py execute`, `seal-only` or `validate-grant`, and never
  anything that could read a target input;
* no cell-305–309 values;
* no cell-307/308 file contents and no hashes of them;
* no decoy outputs opened;
* no network;
* scratch runs only under your own scratchpad, with `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and `TMPDIR` pointed
  there;
* if you start TEST processes (as the delta review did), kill them yourself, and signal nothing else.

**What you review.** The **committed bytes and evidence** on branch `claude/p5y-k5-cell309-p309-r2`, at the commit
that adds this brief, over the range `47d2819a..` (the delta review's preservation commit to now). Two documents are
guides only, never evidence:
* `governance/R2_DELTA_RESPONSE_1.md`, the coordinator's account, condition by condition;
* `governance/REVIEW_R2_DELTA.md`, the conditions you check against.

Verify from git and from the preserved evidence.

## What to assess (every item)

1. **Each condition C1–C15 and advisory A1–A16.** For each, say whether it is met in the bytes, deferred by the plan
   (owner decisions, or worker steps such as the C5 worker-tier evidence and P8(e)), or not met. C1 is
   blocking-before-owner-decisions: check `governance/OWNER_DECISION_PACKET_R2.md` against C1 (a)–(d) word by word, and
   check that it still decides nothing.
2. **The new host semantics.** `code/p309_host.py`:
   * `classify`: `foreign_uids`, `unattributable`, kernel threads;
   * `gate_checks`: `foreign_uids_configured`;
   * `monitor_verdict`: the aggregate rule;
   * `monitor_liveness`;
   * the symmetric `continuity`;
   * `kill_own_descendants`: it must signal only the caller's own descendants;
   * `unit_properties` and its redaction;
   * `redacted_config`, `config_sha256`, `load_launch_config`;
   * the `isolation` order.

   Look for fail-open cases, and for false positives that would consume r2's single attempt in the shared-host
   setting (message 3; OD-R2-5 (i)).
3. **The launcher and the runner.**
   * `code/p309_launch.py`: the modes, including `host-rerun`; the kill properties; the A16 refusals; the redacted
     record and argv; `P309_HOST_CONFIG`.
   * `code/p309_qualify.py`: `qhost_preflight(modes)` (file sha binding, configuration binding, unit properties, the
     instance-id rule); the attempt's start evidence; `_qhost_abort`; `stop_qhost_monitor` (liveness, final sample,
     SIGTERM ignored during the stop); `host_rerun` under Q-HOST.
   * Is every refusal still before the attempt directory and the start line?
4. **QC12.** T13's constant pins (recompute them against r1's F), T14, and the negative controls in
   `tests/test_p309_static_controls.py`: does each mutant really exercise the check it names?
5. **The scanner's signal rule (A7).** Its coverage, its self-signal exception, the planted control, and every new
   `signal`, `proc_read` and `process` registration with its reason. Is anything that sends a signal unregistered?
6. **The committed controls** (`tests/test_p309_host_controls.py`, `tests/test_p309_host.py`). Do P02, S01, K01 and N04
   show what the response claims? Re-run them in your own scratch clone if you can (P02 needs root and `setpriv`).
7. **C14.** `runtime_identity` in the driver and the manifest generator, and `check_bindings`. Confirm that nothing else
   in the driver changed, and that the T13 closure and the exactly-once sites are unchanged.
8. **C8.** `make_freeze_params.py`: `qualification_rule`, `proposed_execution_host`, the execution-host derivation.
9. **The re-drill and P8.**
   * The cloud-tier drill attempt named below. Check its report, its ledger rows in full (F4, the completeness
     check), the controls, and F2.
   * `governance/R2_EQUIVALENCE_P8_ROUND2.json`: recompute (a)–(d) as the delta review did (the F′ bytes can be
     regenerated from the committed tree with the unmodified generators in your scratch clone), and check every new
     difference's classification.
   * `governance/R2_REPIN_LIST_SUPPLEMENT_1.json`, row by row.
10. **No scientific change.** Confirm that nothing changed in any of these:
    * the SRK route, the supplies and the closure criterion;
    * Γ309 and the cell interval;
    * the budgets, the workers and the outcome table;
    * Stage 1a, 1b and 2;
    * the exactly-once sites and the A38 backstop.
11. **The new governance texts.**
    * `governance/P309_R2_AMENDMENTS.md` (C7, C12, C13): are the rules mechanical and correct, and does any of them
      decide an owner question?
    * The AWS instructions and the bootstrap (C15; §8, the launch record).
12. **Disclosures.** The development runs in a scratch clone, the two bugs found while building the controls, and any
    further departure you find.

## The re-drill

* **Evidence:** `evidence/drill/20261001T202159Z/` (attempt 6; PASS).
* **Code commit:** `38089a64`, the drill clone's base (the repairs are `4e6a6901`, plus the checkpoint record).
* **The coordinator's independent validation:** `governance/R2_DRILL_ATTEMPT6_VALIDATION.json` (43/43).
* **The kept drill clone** (F′ `ffee89ab`, FR′ `19cdcbf7`) stays at
  `/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r2_drill_cloud_6/drill_20261001T202159Z/clone`
  until your review ends. You may read it with read-only git. Never write to it.
* **P8 round 2:** `governance/R2_EQUIVALENCE_P8_ROUND2.json`, computed from that clone.

## Output

**`governance/REVIEW_R2_DELTA_FOLLOWUP_1.md`.** Line 2 is exactly one of:
* `R2_DELTA_FOLLOWUP_1_ACCEPTED`, with a section headed exactly `## Conditions` (it may be empty);
* `R2_DELTA_FOLLOWUP_1_REJECTED`, with reasons.

Mark each condition **blocking-before-owner-decisions**, **before-freeze**, or **advisory**. Avoid the words that
`code/p309_placeholder_check.py` flags.

**Your execution ledger** goes in your scratchpad. Do not commit.
