# P309-r2 plan, addendum 2 (append-only): the follow-up conditions F1–F11

**What triggered it.** The focused follow-up review of addendum 1, `governance/REVIEW_R2_PLAN_FOLLOWUP_1.md`, returned
**ADDENDUM_1_ACCEPTED** with conditions F1–F11.

**What it does.** It records how each condition is met, and it is committed before gate step 3 starts. Per that review:
* no further follow-up review is needed;
* the r2 delta review (step 6) verifies F1–F11 before the owner decisions (step 7) and before any worker access
  (step 8).

**Precedence.** This addendum governs over addendum 1, and addendum 1 governs over `R2_PLAN.md`.

NEW Γ309 TARGET EVALUATIONS = 0.

## F1: no ref in either production namespace, anywhere

**Withdrawn.** Addendum 1's drill control "an r1-namespace ref" is withdrawn. No r2 tool, test, drill or sandbox ever
creates a ref under `refs/p5y-k5-cell309-p309-r1/` or `refs/p5y-k5-cell309-p309-r2/`.

**The dynamic control.** The prefix refusal in `check_not_evaluated`, whose first pattern `PRIOR_MARKER_PATTERNS[0]` is
`"refs/p5y-k5-cell309"` (driver line 67), is tested with one TEST-only ref:
`refs/p5y-k5-cell309-TEST-ONLY-prior/x`.
* It matches the prefix and lies in neither campaign namespace.
* It is created only inside a sandbox or the drill clone.

**Static checks (AST or literal).**
* `refs/p5y-k5-cell309-p309-r1/` and `refs/p5y-k5-cell309-p309-r2/` both start with `PRIOR_MARKER_PATTERNS[0]`.
* Both namespaces appear in each of these:
  * the `TestContext` refusal, in the guard and in the verifier variant;
  * `_FORBIDDEN_REF_PREFIX` in `verify/scoped_sandbox.py` (a tuple of both);
  * QC13's `no_exactly_once_ref`, which today tests only `D.G._PROD_NAMESPACE` and will test both namespaces;
  * `production_tokens`.

**The planted control** fires on literal tokens in a planted file that never runs. It never fires on a created ref.

## F2: the drill runs only the clone's own copies

**Subprocesses only.** `code/p309_topology_drill.py` imports **nothing** from the runner, driver, guard, generators or
tests. It runs every script as a subprocess:
* the manifest and parameter generators, the runner's individual items, and each control;
* invoked as `<drill clone>/…/code/<script>.py`, with `cwd` under the drill root;
* with an environment that has **no** P309-clone path on `PYTHONPATH`;
* with `PYTHONDONTWRITEBYTECODE=1`, and `P309_SCRATCH_ROOT` set under the drill root.

**Item selection.** The runner's command line has no item selection: `main()` takes only `--workers` and
`--host-rerun`, and none is added.
* **Cloud tier.** For each item, the drill starts a separate `python -c` subprocess whose `sys.path` holds only the
  clone's own `code/` directory. The runner computes `REPO` and `FNS` from its own `__file__`, so they resolve to the
  clone. Before calling the item, the subprocess asserts that `REPO` is the clone root.
* **Worker tier.** The drill runs the clone's `p309_qualify.py` `main()` through the launcher.

**A topology witness per drill run,** written to the drill ledger:
* `recorded_freeze` in the clone returned F′;
* `git rev-list` shows FR′ is F′'s only record child;
* for one QC11 sandbox:
  * the base history holds **0** freeze-record commits;
  * the sandbox holds exactly the number the flow expects;
* the sandbox base commit equals F′.

**The P309 clone is unchanged.** Before and after each drill run, the drill records the P309 clone's HEAD, its
`for-each-ref` output (sha256), and `git status --porcelain=v2 --untracked-files=all` (sha256). They must be identical,
or the drill fails.

## F3: cloud-tier scope

The cloud tier runs every QC item **except QC06, QC08, QC09 and QC10**, as in plan §5:
* QC01–QC05, QC07, QC11–QC17, QC-D5 and QC-U2;
* plus `recorded_freeze`, `mirror(F′)`, and the r1-tree check (`ecd1c359`);
* plus `code/p309_host.py`'s provenance and continuity functions, run on the drill host. The cloud container fails the
  durability preflight, as expected, and that failure is recorded as a control.

## F4: drill ledger rows in full

The following are committed under FNS2 `evidence/drill/<utc>/`:
* the drill ledger's rows, **in full**;
* their sha256;
* the counters (target evaluations 0);
* the band check;
* the topology witnesses (F2);
* the control outcomes.

No decoy output and no qualification output file is committed.

## F5: wording and small items

**Replacing addendum 1's "the runner stays unmodified":** *the runner gains no drill mode; each drill runs the runner
bytes that are later frozen.* (P2's QC13 check and P10's Q-HOST do change the runner.)

**Confinement.** After each runner invocation, the drill asserts that the uncommitted changes the runner leaves,
measured against the drill clone's HEAD at the moment of the call, are confined to:
* the clone's `qualification/`;
* the execution and exposure ledgers.

**Unit names.**
* drill: `p309-r2-drill-<utc>`;
* official: `p309-r2-qualify-<utc>`.

The launcher refuses a drill invocation that carries the official name, and the reverse.

**T7 scope.** Both `code/p309_topology_drill.py` and `code/p309_host.py` / `code/p309_launch.py` (addendum 1, P4) are
added to T7's string scope.

## F6: the carry-over table, completed

These rows complete addendum 1's P1 table. Each row's r1 source is in `p5y_k5_cell309_p309_r1/governance/`. **OD-R2-0
asks the owner to confirm every row marked "OD-R2-0".**

**Rows added:**

| r1 owner text | r2 status |
|---|---|
| OWNER_DECISIONS, **INCIDENT ACKNOWLEDGEMENT** (line 189): "Their existing classifications are accepted for purposes of proceeding to the formal campaign." | **OD-R2-0.** It covers only the events it lists. The r1-era events below were never acknowledged for a successor, and the owner is asked to acknowledge them for r2 |
| OWNER_DECISIONS, **FORMAL CAMPAIGN PROCEDURE** (line 236): "Proceed conservatively in the order required by the reviewed package", plus its history rules | **OD-R2-0.** r2's order is P13 / §9 as amended here. The history rules are also carried by message 1 §9 |
| OWNER_DECISIONS, **FINAL HANDOFF FOR THIS STAGE** (line 371): the report list before the grant decision | **OD-R2-0.** r2's final handoff uses the same list, plus host identity and durability (message 1 §5.B) |
| OWNER_RULINGS_2, **GRANT ADMISSION CODE** (line 141): the verifier/admission author is authorized to write and test the mechanism, and "Do not have the coordinator silently implement an independent component merely because another author is unavailable" | **OD-R2-0.** In the meantime, F11 applies it to r2 as a constraint, not as an authorization |
| OWNER_RULINGS_2, **FORMAL CAMPAIGN CONTINUATION** (line 182): continue autonomously through the stages, under the hard boundary | **OD-R2-0.** For r2, message 1 and message 3 govern autonomy, and message 1 §10 says "do not infer authorization" |
| OWNER_RULINGS_2, the remaining rulings: U2, FC2, scanner allowance, sandbox marker | **OD-R2-0.** Addendum 1 marked this row "carried" with no owner quotation, so it moves here |
| G1 (acceptance of the MEDIUM-HIGH liability) | **OD-R2-0.** It is an owner acceptance, not part of "the scientific object" |
| CELL SET, the exclusions: "Cells 305, 306, 307 and 308 are excluded", and Stage-1 material "permanently bound to cell 309" | **OD-R2-0.** Message 1 §1 ("target interval/cell identity") covers {309} only |

**r1-era events for the owner to acknowledge under OD-R2-0:**
* **Qualification failure.** The r1 qualification FAILED: a QC11 harness defect, followed by the reboot during QC_D5.
  This is recorded in the postmortem.
* **The P309F-01 incident** and the formal errata FE-1 to FE-11 (`ERRATA_FORMAL_P309.md`).
* **The placeholder allowlist entries** that no reviewer reviewed (D3). P16 narrows them for r2.
* **The container reboot at 22:41:12Z** on 2026-09-30, at least the third restart in that session.
* **The postmortem reviewer's disclosure** that it hashed four pinned cell-307 campaign files, beyond the brief's git
  metadata limit.
* **Briefs issued by message only** and recorded after issue: the disclosed departures from C5.

**The verbatim record itself.** OD-R2-0 also asks the owner to confirm that `OWNER_INSTRUCTIONS_R2_VERBATIM.md`
records messages 1–3 verbatim, with the one disclosed redaction. No transcript uuid is available to check that from
here.

## F7: the owner-decision texts, corrected

### OD-R2-4: shared-host changes

The owner's message 3 §6 reads: *"Do not alter the cell-308 campaign, its checkout, refs, evidence, processes or
governance state merely to prepare P309-r2."*

Addendum 1's item "the permissions on cell 308's checkout" is therefore **withdrawn as a default**. To keep cell 308's
checkout unreadable to P309 without altering it, r2 uses only:
* `InaccessiblePaths=` on the P309 unit, naming cell 308's checkout path;
* a P309 Unix user with no group membership that grants access to that checkout;
* a read-only `stat` of the checkout's top directory, which records its mode and owner as hashes and counts, and
  touches nothing.

Only if these fail to make the checkout unreadable will the owner be asked to amend §6, and the cell-308 operator to
consent.

OD-R2-4 also lists **the launch privilege**: starting a system transient unit with `--uid` needs root, or a sudo or
polkit rule limited to exactly the `p309-r2-*` units. That privilege is a shared-host change and needs the owner's and
the cell-308 operator's consent.

### OD-R2-5: the interference policy

The owner's message 3 §3 reads: *"if a cell-308 heavy job is running, P309-r2 may perform only work that does not
materially affect host resources"*. §8 adds the rule "do not interrupt [cell 308]; wait".
* **Option (i)**, where a cell-308 heavy start fails r2's single attempt, matches §3 and §8 as written.
* **Option (ii)**, where P309 yields at idle priority and continues, conflicts with §3. It is available **only if the
  owner amends §3**.

### OD-R2-1: the production ref namespace

**The provisional choice.** At steps 3–4, option **(b)** (`refs/p5y-k5-cell309-p309-r2/`) is implemented
**provisionally**. If the owner chooses otherwise at step 7, the cost is:
* re-implementing the affected literals (the `owner` rows of the P2 table);
* a fresh delta review;
* a re-drill.

**Asking earlier.** The owner may instead answer OD-R2-1 and OD-R2-1b at any time before step 7. The coordinator
does not wait for that answer.

**Under (b), r2 adds rather than replaces.** r2's amendments **add** r2's namespace to FC2_SPEC_R2's forbidden-names
rule. They do not replace r1's: after (b), both namespaces are forbidden everywhere (F1).

## F8: gate step 8, in the owner's order

Addendum 1's step 8 is replaced by four steps:

**8a. A read-only audit of the AWS worker,** before any clone, user, install or file is created there.
* The committed audit function (`code/p309_host.py`, function `audit`) is fed to the worker's **system** Python on
  standard input. Nothing is written on the worker; the output returns on standard output.
* Identities (instance id, machine-id, hostname) are recorded as sha256 values only.
* Nothing inside cell 308's checkout is read. Process data about cell 308 is recorded only as counts, pids and uids.
* The audit is carried by whatever access the owner provides under OD-R2-3. The cell-308 session is never used.

**8b.** The HOST verdict, from 8a. Then OD-R2-3 and OD-R2-4 consent, informed by that verdict.

**8c. Bootstrap,** only after 8b:
* the P309 user;
* the single-branch full clone;
* the P309-private CPython 3.11.15;
* the unit privilege;
* the scratch volume or quota.

**8d.** The worker-tier drill (P14), which is the burn-in.

## F9: table accuracy

`governance/R2_LITERAL_DISPOSITION_SUPPLEMENT_1.json` supplements `R2_LITERAL_DISPOSITION.json` and binds to it by
sha256. Generated mechanically from `git show F:`, it adds:
* **The commit references the table missed:** 72 distinct (file, line, literal) tuples, all "keep" (historical record):
  * 70 in `governance/`;
  * `fc2/FC2_SPEC_R2.md` line 3;
  * `start_state/RESEARCH_SELF_AUDIT_at_eb9a9c22.json` line 51.

  This matches the reviewer's count.
* **The rule for `freeze/`:** it is **not copied**. It is regenerated at r2's freeze by the unmodified generators, and
  P8(d) governs. Its r1-bound matches are listed for completeness: 180 by the supplement generator's counting, which
  includes commit references.
* **The corrected reasons** for `p309_self_audit.py:36` (branch name).
* **Cross-references** for the rename rows that carry P3 bindings:
  * driver 48 → result path;
  * guard 42 → grant path;
  * variant 170 → grant and result paths;
  * `make_freeze_params.py` 26 → derived `result_path` (line 279) and `freeze_record` (line 327).

## F10: the hash convention

**The convention.** Each sha256 in `OWNER_INSTRUCTIONS_R2_VERBATIM.md` is computed over *the body without the newline
that precedes the closing fence*: the bytes after the opening fence line's newline, up to but excluding the newline
before the closing fence line.

**How it differs from r1.** r1's records hash the body "with a final newline added", so this is a different convention.

**No hash of the unredacted body** is or will be recorded.

## F11: the verifier author (step 3)

**Who.** r1's independent verifier author makes the verifier-side changes:
* the variant's literals;
* `scoped_sandbox`'s base rule and `_FORBIDDEN_REF_PREFIX`;
* `P309_SCRATCH_ROOT`;
* `VERIFY_RESULTS_SCOPED.json`;
* the verifier README.

The author is briefed by a brief committed **before** it is issued (C5). If that author cannot act, a new independent
author is briefed the same way.

**The coordinator never makes these changes itself** (owner rulings 2, GRANT ADMISSION CODE, applied here as a
constraint).

## Step 3a: the relocation baseline (a mechanical precondition of step 3)

**Why.** The verifier author edits r2's `verify/` in place, so the baseline must exist first. Before the verifier
author's brief is issued, the coordinator commits a **byte-identical copy** of r1's operative directories as they are
at F:
* `code/`, `config/`, `fc2/`, `tests/`, `verify/` and `start_state/` → the same paths under FNS2;
* r1's 15 `governance/` files at F → FNS2 `governance/`, as inherited record ("keep"). They sit beside r2's own
  documents; no name collides.

**What it contains.**
* That commit changes **no byte**. The delta review checks it: each copied directory's git tree id must equal F's
  subtree id.
* `freeze/` is not copied (F9).
* `evidence/`, `ledger/`, `reviews/`, `qualification/` and `handoff/` are not copied. r1's reviews are referenced by r1
  path at `c902fe2f`.

**What it is not.** The copy is not runnable as r2 until the relocation (step 4) is done. **No QC item, drill or test
is run on it before then.**

## Gate order (P13, as amended)

| step | content |
|---|---|
| 1 | Plan review (done). |
| 2 | Addendum 1 and its follow-up (done: ADDENDUM_1_ACCEPTED). Then this addendum 2, committed. |
| 3a | The relocation baseline (above). |
| 3 | The verifier author's changes (F11), from a committed brief. |
| 4 | Coordinator implementation, then the development tests. |
| 5 | The cloud-tier drill (F2–F4) with every control. |
| 6 | The r2 delta review, which verifies P6–P12 and F1–F11. |
| 7 | Owner decisions. **STOP.** |
| 8 | The worker steps 8a, 8b, 8c and 8d (F8). |
| 9–11 | Unchanged from addendum 1. |
