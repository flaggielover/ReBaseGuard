# Focused follow-up review of P309-r2 plan addendum 1 (conditions P1–P5)
ADDENDUM_1_ACCEPTED

**Reviewer.** The independent reviewer of `governance/REVIEW_R2_PLAN.md`. I wrote none of the P309 code, the plan or the
addendum, and I am not the coordinator.

**Brief.** `governance/BRIEF_R2_PLAN_FOLLOWUP_1.md` (blob `e0fb95d8`). It was committed in `e9bc840c` together with the
files it asks me to review, before it was issued.

**State reviewed.**
* HEAD `e9bc840c3bde837d9756150dc43d6046a8d130a7`, linear on `da754b8f`, working tree clean.
* `R2_PLAN_ADDENDUM_1.md`: blob `22e9f892`, sha256 `a9fcbde5…`.
* `OWNER_INSTRUCTIONS_R2_VERBATIM.md`: blob `63e11138`, sha256 `05b88579…`.
* `R2_LITERAL_DISPOSITION.json`: blob `1417fa2b`, sha256 `8c6e1e9a…`.

**My first review was preserved unchanged.** `REVIEW_R2_PLAN.md` is sha256 `cddfd0d0…`, equal to the `.sha256` file
and to the file I wrote. `REVIEW_R2_PLAN_EXEC_LEDGER.jsonl` is byte-identical to my scratch ledger (30 lines, sha256
`a377449f…`).

**Integrity at `e9bc840c`, checked locally; I did not query the remote.**
* r1's tree is `ecd1c359…`, at HEAD and at `c902fe2f`.
* Since `c902fe2f`, no path outside FNS2 has changed.
* There are no `refs/p5y-k5-cell309*` and no `refs/p309-test/*` refs.
* The remote-tracking refs read r2 = `e9bc840c` and r1 = `c902fe2f`.
* No IPv4 address appears in the r2 namespace or in the commit messages since `c902fe2f`.

**NEW Γ309 TARGET EVALUATIONS = 0.** This follow-up ran no campaign code and created no ref.

## Verdict in brief

**Accepted, with conditions F1–F11.** The addendum resolves P1–P5 in substance.

**What holds.**
* The three owner messages are recorded with hashes I could reproduce.
* The operative rows of the literal table (code, config, tests, verify, start_state) are complete. Where I checked them
  row by row, they are correct.
* The bindings and the rules are separated.
* The host tools move into `code/`.
* The runner gets no rehearsal mode.
* P6–P23 and the gate order are carried over faithfully.

**What must change.** The addendum introduces one defect that must not be built:
* **The drill control "an r1-namespace ref" would create a ref under `refs/p5y-k5-cell309-p309-r1/`.** The inherited
  FC2 spec and owner rulings 2 forbid that anywhere, including sandboxes and mock repositories (F1).

Three further gaps would weaken the drill:
* it could be vacuous if the runner's items are called in-process from the real clone (F2);
* its cloud tier is narrower than the plan's (F3);
* its ledger is kept only as a digest (F4).

The owner-facing texts also need fixing:
* the carry-over table omits several r1 owner sections (F6);
* OD-R2-4 and OD-R2-5 do not quote owner words that constrain them (F7);
* gate step 8 runs the "read-only audit" from a clone that the owner's words say may only exist after the audit (F8).

**Timing.**
* Addendum 2 (append-only) records F1–F11. It must be committed before step 3 starts.
* No further follow-up review is needed. The r2 delta review (step 6) verifies all of F1–F11 before the owner decisions
  (step 7) and before any worker access (step 8).

## Findings

### 1. P1: the owner's words and the carry-over

**The verbatim record. Hashes and byte counts confirmed.** I recomputed the three fenced bodies:

| message | sha256 (prefix) | bytes |
|---|---|---|
| 1 | `86065859…` | 12 360 |
| 2 | `77e344d7…` | 1 017 |
| 3 | `78cd27da…` | 2 038 |

* All three match when the body is taken **without** the newline that precedes the closing fence. With that newline
  they do not match.
* This convention differs from r1's records ("with a final newline added"). "The exact bytes between the fence lines"
  is ambiguous on this point (F10).
* Each body is pure UTF-8 with no CR or tab.
* I cannot check that the text is verbatim, because no transcript uuid or timestamp is available. The record says so.
  Only the owner can confirm it (F6).

**The redaction is adequately disclosed.**
* It names what was redacted (the IP in message 2) and why: the owner marked the IP RETIRED/UNTRUSTED, and the
  coordinator had undertaken not to record it.
* It gives the replacement token, states that the hash covers the redacted body, and states that nothing else changed.
* The token occurs once in the body and once in the disclosure. No other IPv4 string is present.
* A hash of the unredacted body must **not** be added: an IPv4 address in a known context can be brute-forced from it.

**The carry-over table.**
* Its rule is sound: "carried" only where the owner's 2026-10-01 words cover the item, and everything else goes to
  OD-R2-0.
* It correctly finds that r1's P0-1/G2 authorization to freeze and qualify does not cover r2, and makes it OD-R2-0.
* Message 1 supports that reading. Its §2 reads "eventually the official r2 qualification, but ONLY after … freeze and
  authorization state permit it", and its §10 reads "Do not infer authorization from this prompt".

**The table is incomplete, and some rows overstate the owner's words** (F6):
* **Rows missing.** These r1 owner sections are absent:
  * INCIDENT ACKNOWLEDGEMENT (owner decisions line 189);
  * FORMAL CAMPAIGN PROCEDURE (236);
  * FINAL HANDOFF FOR THIS STAGE (371);
  * from owner rulings 2: GRANT ADMISSION CODE (141), which holds the verifier/admission author's authorization and
    "Do not have the coordinator silently implement an independent component merely because another author is
    unavailable";
  * also from owner rulings 2: FORMAL CAMPAIGN CONTINUATION (182).
* **The incident acknowledgement matters for r2.** The owner accepted the incidents listed in r1's decisions "for
  purposes of proceeding". Later r1 events have not been acknowledged for a successor:
  * the P309F-01 incident and the formal errata;
  * the unreviewed placeholder allowlist entries (D3);
  * the 22:41Z reboot;
  * the postmortem reviewer's cell-307 hashing disclosure;
  * briefs issued by message only.
* **The owner-rulings-2 row** is marked "carried" with "—" in place of the owner's words. By the addendum's own rule it
  belongs in OD-R2-0.
* **G1** is the owner's acceptance of a MEDIUM-HIGH liability, not part of "the scientific object". Message 1 §1 does
  not cover it.
* **CELL SET.** "Target interval/cell identity" (message 1 §1) covers {309}. It does not cover the exclusion of
  305–308, nor the rule that Stage-1 material bound to 309 is never reused for another cell.

The practical risk is limited, because OD-R2-0 asks the owner to confirm the whole table before the freeze. But the
owner can only confirm rows that are listed.

### 2. P2: the literal table

**Independent inventory (scratch script, NOT EVIDENCE; `git ls-tree`, `git show F:` and `git cat-file --batch-check`
only).**
* **Scope.** I ran it over F's eight directories: the seven frozen directories plus `start_state/`.
* **Patterns.** The same patterns as the table:
  * `p5y_k5_cell309_p309_r1` and `p5y-k5-cell309-p309-r1`;
  * `p309[_-]r1`;
  * the r1 branch name;
  * `P309_*/n` schema names;
  * hex tokens of 7–40 characters that resolve to a commit.
* **Every table row is reproduced.** The table has 350 rows, which are 346 distinct (file, line, kind, literal) tuples;
  four are repeats on one line. All 346 appear in my inventory.
* **code, config, tests, verify: no difference.** Nothing is missing there.
* **What the table misses** (F9):
  * `freeze/` (178 matches). It is a frozen directory, but it is not copied and is regenerated at r2's freeze. The
    table does not say so.
  * 72 commit references: 70 in `governance/`, `fc2/FC2_SPEC_R2.md` line 3, and
    `start_state/RESEARCH_SELF_AUDIT_at_eb9a9c22.json` line 51.
  * All of these are historical record and would be "keep". The table's claim to list "every hex string that resolves
    to a commit" is therefore not met.

**Dispositions, row by row.** I checked all 111 rows in code, config, tests and start_state, and the
`verify/*.py`/`*.md` rows.
* **Correct**, including:
  * `u2_structure_check.py` 340 and 435–437 → rename;
  * driver `SCHEMA` (93) → binding;
  * `make_freeze_params.py` 26 → rename, 218 → binding, 230 (`2a03e838`) → keep;
  * checkpoint 79 → change, 107 → keep;
  * runner 269 → keep;
  * self-audit 37 → change, 38 (`LOCK_COMMIT`) → keep;
  * guard 39–41 → owner, 42 → rename, 126 → binding;
  * allowance 7, 15, 43 and 71 → owner, with both tokens kept forbidden;
  * planted control → owner, firing for both tokens;
  * `scoped_sandbox` 31 → owner, forbidding both;
  * variant 163 → owner, 170 → rename, 175 → binding;
  * the production-shaped campaign values in `test_p309_guard.py` 342 and `test_verify_scoped.py` 791 and 815 →
    binding.
* **Cosmetic.**
  * `p309_self_audit.py:36` gives "namespace path" as the reason for the branch name on its `short_r1` and `branch_r1`
    rows.
  * Rename rows that carry a P3 binding should say so:
    * driver 48 → result path;
    * guard 42 → grant path;
    * variant 170 → grant and result paths;
    * `make_freeze_params.py` 26 → the derived `result_path` (279) and `freeze_record` (327).
* **Literals assembled from pieces.** I searched F for r1 names assembled from pieces. The only assembled names are
  module names in the D5 controls (`'p309_' + 'driver'`). No production name is assembled.

**The non-literal class is handled.** Some breakage comes from a relative path dereferenced through a renamed variable,
which no literal inventory can find. My search found only two such places, the self-audit's `IMMUTABLE` list and
`make_freeze_params.py` 166–177. The addendum restructures both: r1's files by r1 path, with the reviews table pinned
to `c902fe2f`. `evidence/`, `handoff/` and `qualification/` are not read as inputs.

**Anchors: as required.**
* Research, r5 and r6 checks keep `eb9a9c22`.
* Namespace-only checks use `c902fe2f`.
* The new check that r1's tree equals `ecd1c359` runs in the checkpoint tool, the self-audit and QC13.

### 3. P3 and P4: satisfied

**P3.** The table of bindings (grant path, grant `campaign`, result path, result `SCHEMA`) and the two flagged rules
match my condition.

**P4.**
* The tools move into `code/p309_host.py` and `code/p309_launch.py`, the latter with no executable bit. There is no
  `.sh` file, no `host/` directory, and `FROZEN_DIRS` is unchanged.
* The documents go in `governance/`.
* There are reviewed-function entries, and the T7 scope is extended.

One addition: a system unit with `--uid` must be started by root or through a polkit/sudo rule. That privilege is a
shared-host change (F7).

### 4. P5: the drill (accepted, with F1–F5)

**Satisfied.**
* The runner gets no rehearsal branch, and the name is distinct.
* The tool refuses unless all of these hold:
  * the clone lies under the drill root;
  * its common dir differs from the P309 clone's;
  * it has no push URL.
* The synthetic F′ and FR′ are built with the unmodified generators, followed by a record commit.
* The worker tier runs `main()` through the official launcher.
* No decoy output is copied, and one GOVERNANCE row is added.
* The ref-moving calls are listed.
* The R2-M01 pair, the second-record control and the push-URL control are present.

**F1: the r1-namespace control is forbidden.**
* F's `fc2/FC2_SPEC_R2.md` (lines 196–198), kept in r2 as inherited spec text, says: "The production marker name, and
  any ref under `refs/p5y-k5-cell309-p309-r1/`, is never created anywhere, including sandboxes, temporary namespaces
  and mock repositories (owner ruling)".
* Owner rulings 2 (SANDBOX MARKER) says the same of the marker name.
* r1's QC11 deliberately tested the prior-marker refusal with `refs/rlr-tail/x` (flow F23).
* `check_not_evaluated` refuses by plain prefix (`refs/p5y-k5-cell309`, driver line 67). It can therefore be tested
  with a ref that matches that prefix but lies in neither campaign namespace.
* The other r1-namespace refusals can only be shown statically:
  * `TestContext`;
  * `_FORBIDDEN_REF_PREFIX`;
  * QC13;
  * the scanner tokens.

**F2: the drill could be vacuous.**
* The runner, driver and tests take `REPO` and `FNS` from `__file__`. Suppose the drill tool, living in the P309
  clone, imported the runner's item functions in-process ("the runner's own item functions … as the earlier dry runs
  did").
* Its QC11 would then build sandboxes on the P309 clone's pre-freeze HEAD and pass, without testing the post-freeze
  topology at all.
* The same applies to the generators that build F′. Run in-process, they would write `freeze/` into the P309 clone.

**F3: the cloud tier is narrower than the plan.**
* The addendum lists only QC11, QC-D5, QC12, QC13, QC15 and QC16. It drops QC01–QC05, QC07, QC14, QC17 and QC-U2,
  which are cheap and also depend on paths and `mirror(F′)`.
* It also drops the host provenance checks. Message 1 §6 names those as a minimum, and the plan's §5 included them.

**F4: the drill ledger.** My P5 asked for the rows themselves. The addendum keeps them only "as a digest", and a digest
cannot be re-checked once the clone is gone.

**F5: wording.**
* "The runner stays unmodified" is literally false: P2's QC13 check and P10's Q-HOST change the runner.
* The confinement assertion should apply to the changes the runner leaves, not to "changes after FR′", which include
  the drill's own record commit.

### 5. P6–P23 and the gate order (P13): faithful, with three corrections

**Faithful.**
* P6–P13 are accepted "as written in the review". The paraphrases of P9–P12 and P14–P16 are partial but say nothing
  contrary.
* OD-R2-0 to OD-R2-6 carry P17–P22 accurately.
* P23 is adopted.
* The gate order includes each element of my P13, in order:
  * the verifier author first;
  * the pre-freeze follow-up review after the audit and the drill;
  * a re-drill after any change;
  * the tree binding;
  * a single writer;
  * the freeze on the worker.

**Corrections, which only the verbatim text made visible.**
* **OD-R2-4 and message 3 §6.** Message 3 §6 says: "Do not alter the cell-308 campaign, its checkout, refs, evidence,
  processes or governance state merely to prepare P309-r2". "The permissions on cell 308's checkout" (OD-R2-4) would
  alter its checkout (F7).
* **OD-R2-5 and message 3 §3.** Message 3 §3 says: "if a cell-308 heavy job is running, P309-r2 may perform only work
  that does not materially affect host resources". Option (ii), continuing at idle priority, conflicts with that. My
  first review offered (ii) without this text; it needs an explicit amendment by the owner. Option (i) matches §3 and
  §8 (F7).
* **The step-8 audit.** Message 1 §3 says "Before installing, modifying, deleting, cloning … perform a READ-ONLY
  audit", and message 3 §7 says "First audit the current AWS worker read-only". So the audit cannot run "through
  `code/p309_host.py`" in a P309 clone that may only be created after it (F8).
* **OD-R2-1 timing.** The literals that depend on OD-R2-1 are implemented at steps 3–4, but OD-R2-1 is decided at step
  7. The provisional choice and the cost of a different owner choice must be stated (F7).

## Conditions

**Addendum 2 (append-only).** It is committed before step 3 starts, and the r2 delta review verifies F1–F11.

* **F1 — No ref in either production namespace, anywhere.**
  * Remove the drill control "an r1-namespace ref".
  * Test the prefix refusal with a TEST-only ref that starts with `refs/p5y-k5-cell309` but lies in neither campaign
    namespace (for example `refs/p5y-k5-cell309-TEST-ONLY-prior/x`). Add a static assertion that both
    `refs/p5y-k5-cell309-p309-r1/` and `-r2/` start with `PRIOR_MARKER_PATTERNS[0]`.
  * Check statically (AST or literal) that both namespaces appear in:
    * the `TestContext` refusal;
    * `_FORBIDDEN_REF_PREFIX`;
    * QC13's `no_exactly_once_ref`;
    * `production_tokens`.
  * The planted control fires on literal tokens in a never-run planted file, never on a created ref.
* **F2 — The drill runs only the clone's own copies.**
  * Every script runs as a subprocess, with its path and cwd under the drill root and with no P309-clone path on
    `PYTHONPATH`. This includes the generators and each runner item. Nothing is imported in-process.
  * Each drill run records a topology witness:
    * `recorded_freeze` returned F′;
    * one QC11 sandbox's base history holds 0 record commits, and the sandbox holds exactly the expected number.
  * The P309 clone's HEAD, refs and `git status` are identical before and after.
* **F3 — Cloud-tier scope.**
  * Every item except QC06, QC08, QC09 and QC10 (as in plan §5).
  * Plus the host provenance and continuity functions of `code/p309_host.py`, and the r1-tree check.
* **F4 — Drill ledger.** Commit the drill's ledger rows in full under `evidence/drill/`, with their sha256, the
  counters and the band check. Commit no decoy outputs.
* **F5 — Wording and small items.**
  * Say: "the runner gains no drill mode; each drill runs the runner bytes that are later frozen".
  * Assert that the runner's uncommitted changes, relative to the drill's HEAD, are confined to `qualification/` and
    the execution and exposure ledgers.
  * Give the drill unit a name different from the official unit's.
  * Add `code/p309_topology_drill.py` to T7's string scope.
* **F6 — Carry-over table.**
  * Add rows for:
    * INCIDENT ACKNOWLEDGEMENT, listing the r1-era events in finding 1;
    * FORMAL CAMPAIGN PROCEDURE;
    * FINAL HANDOFF FOR THIS STAGE;
    * owner rulings 2's GRANT ADMISSION CODE and FORMAL CAMPAIGN CONTINUATION.
  * Move to OD-R2-0, for confirmation:
    * every row without an owner quotation, including the owner-rulings-2 row;
    * G1;
    * the CELL SET exclusions and the no-reuse rule.
  * OD-R2-0 also asks the owner to confirm the verbatim record itself.
* **F7 — Owner-decision texts.**
  * **OD-R2-4.**
    * Quote message 3 §6.
    * Prefer means that leave cell 308's checkout unaltered:
      * the P309 unit's `InaccessiblePaths=`;
      * a P309 user with no group access;
      * a read-only `stat` of the checkout's top directory.
    * Ask for a §6 amendment only if those fail.
    * Add the launch privilege (sudo or polkit for exactly the P309 units).
  * **OD-R2-5.** Quote message 3 §3 and §8, and state that option (ii) requires the owner to amend §3.
  * **OD-R2-1.**
    * State that (b) is implemented provisionally, and that another choice means re-implementation, a re-drill and a
      delta review. Alternatively, ask OD-R2-1 and OD-R2-1b before step 3.
    * Under (b), r2's amendments **add** r2's namespace to FC2_SPEC_R2's forbidden-names rule. They do not replace r1's.
* **F8 — Step 8, in the owner's order.**
  * **8a: a read-only audit** before any clone, user or install. For example, the committed audit function is fed to
    the system Python on stdin; nothing is written on the worker, identities are recorded as hashes, and nothing is
    read inside cell 308's checkout.
  * **8b:** the HOST verdict, and OD-R2-3 and OD-R2-4 consent informed by it.
  * **8c:** bootstrap: the user, the single-branch clone, the interpreter and the unit privilege.
  * **8d:** the worker-tier drill.
* **F9 — Table accuracy.**
  * Add the 72 commit references as "keep", or narrow the claim.
  * State that `freeze/` is not copied and is regenerated (P8(d) governs).
  * Correct the reasons at `p309_self_audit.py:36`.
  * Cross-reference the rename rows that carry P3 bindings.
* **F10 — Hash convention.** State it exactly: "the body without the newline that precedes the closing fence". Note
  that it differs from r1's. Add no hash of the unredacted body.
* **F11 — Verifier author (step 3).**
  * The brief is committed before issue (C5).
  * If r1's verifier author cannot act, a new independent author is briefed. The coordinator never makes these changes
    itself (owner rulings 2, GRANT ADMISSION CODE).

## Disclosure (reads, runs, writes)

**Scratch ledger.** Every read and run is logged in
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r2_plan_review_fu1/LEDGER.jsonl`.

**Reads.**
* The brief, the addendum, the owner-instructions record and the table, all in full.
* My preserved review files, by comparison.
* r1's `OWNER_RULINGS_2_P309_VERBATIM.md` (lines 1–60 and 160–277) and the section headings of the r1 owner records.
* Through `git show F:`: `fc2/FC2_SPEC_R2.md` lines 192–200, and `tests/test_p309_exactly_once.py` lines 270–278.
* Greps of F's tree for r1 names and for reads of paths relative to the namespace.

**Runs.**
* Read-only git: `rev-parse`, `log`, `show`, `diff`, `grep`, `ls-tree`, `cat-file --batch-check`, `for-each-ref`,
  `merge-base`, `status`.
* `sha256sum` and `cmp`.
* Python hash recomputation of the fenced bodies.
* **One scratch diagnostic, NOT EVIDENCE:** `scratchpad/r2_plan_review_fu1/inventory_check.py`.
  * It scans F's r1 namespace through git only. It prints locations and matched tokens, and no file content.
  * It imports and runs no campaign code, and creates no file other than the script itself.
  * It scanned `verify/VERIFY_RESULTS_SCOPED.json` for literal patterns only. No row of that file was displayed.
* No network call, and no `ls-remote`. No `execute`, `seal-only` or `validate-grant`, and no QC item.

**Writes.** This file, my scratch ledger and the script. No git write of any kind.

**Firewall.**
* No value for cells 305–309 was read.
* No cell-307 or cell-308 file was read or hashed.
* No decoy output was opened, and no decoy result is quoted.
* No ref was created, armed or consumed.
* The retired worker was neither contacted nor looked up.
