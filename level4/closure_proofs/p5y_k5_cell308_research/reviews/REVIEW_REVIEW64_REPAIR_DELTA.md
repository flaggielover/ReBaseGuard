# Review: the coordinator's repairs of review 64's findings and the restored history-completeness guard (combined Cell-308 development source, Cloud route r1, S4 changed branch)

* Reviewer: **reviewREVIEW64_REPAIR (fresh agent, brief 65)**
* Date: 2026-10-15 (UTC), about 11:13Z to 11:45Z.
* Pinned commit: **`2275b3a0f689fea33dbc82dfaf228bd0a2ea301d`** (branch `codex/cell308-claude-r5-integration`, draft PR
  flaggielover/ReBaseGuard#3). Detached worktree `scratchpad/review65/tree_2275b3a0`. `git status --porcelain` was
  empty after every run; I wrote nothing there.
* Delta: `5e8e3d9c..2275b3a0`, five commits: f23f0032 (native pass of 5e8e3d9c recorded, brief 64), b23ee7dd (review 64
  recorded, repairs), 68a38c64 (Q01 re-anchored), c50e73f8 (completeness guard, erratum E1), 2275b3a0 (local full-run
  records).
* NS = `level4/closure_proofs/p5y_k5_cell308_research/`, DEV = `NS/streams/CLOUD_R1_LINUX_DEV`. Line numbers refer to
  the 2275b3a0 files.
* Scratch: `/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review65/`
  ("scratch"). Probes ran on `scratch/base/lx_platform.py`, sha256 `96eb3a5e…`, which equals the 2275b3a0 blob and
  ledger 492's binding. Scripts are stored as `*.py.txt`.
* `new_target_evaluations = 0`. I ran no cell, drift, certificate, decoy, science module, qualification case or
  candidate code. I installed nothing and changed no setting.

---

## 1. Exposure disclosure

**Opened:**
* brief 65. It is the only file I read in the shared checkout.
* In the pinned tree:
  * the `5e8e3d9c..2275b3a0` diffs of `lx_platform.py`, the three test files, `run_mutants.py` and the workflow;
  * `lx_platform.py` lines 820–935 and 1150–1500;
  * the head of `lx_verified.py` (lines 1–45);
  * test helper and witness methods in `tests/test_lx_platform.py`;
  * `run_mutants.py`: Q01, Q04, R5SYNC02, RV08–RV30, `run_suite` and `classify_mutant`;
  * review 64 as recorded, the supplement r64 and erratum E1;
  * ledger lines 486–493;
  * `reviewer64_mutants.py.txt` and the heads of `probes64*.py.txt`.
* Compressed local records: all three were decompressed in memory, and their mutant rows and suite traces were read.
  They contain synthetic test output only.

**Name-level contact:**
* The scratchpad root listing: `MUTANTS_RUN_R*.json`, `fix_shallow`, `gate.txt`, `gitprobe*`, `inv_check.json`,
  `ldet`, `mut*.log`, `native-r3`, `rev5`, `review59`–`review64`, `rv`, `scan*.json`, `shallow_probe`.
  * I opened nothing in it except `scratchpad/review64/`, whose originals I compared byte-for-byte for Q4.
  * I did not open `review64/tree_5e8e3d9c/` or `review64/tmp/`. Their names were seen only.
* The `git diff --name-only` of the delta, grepped for audit / interruption / MB r1 / 309 / exposure names: no hits.

**Shared object store:**
* The pinned worktree's git dir is `/home/user/ReBaseGuard/.git/worktrees/tree_2275b3a0`. Every git read went through
  the shared object store (objects only).
* I ran `git rev-parse --is-shallow-repository` once in the pinned worktree. It answered `true`: the real repository
  is a shallow clone, so the new guard would refuse any attestation there. This is a git query, not a call of
  `attestation_valid`.

**GitHub (read-only API):**
* the run list of the branch;
* run and job metadata of 38709761027, 38709764443, 38714823675 and 38725820509;
* the last 45–60 lines of the job logs of 38709761027, 38709764443 and 38714823675. They print counts, ids, test ids,
  exception types and artifact digests.

**Live calls:**
* None against the real repository.
* Every `attestation_valid` call I made passed `repo_root=<synthetic repository under scratch/tmp>`, with
  `machine_identity` patched.
* The unit suite runs `attestation_valid` only on synthetic repositories or with `_git` patched.

**Not opened, grepped or read:**
* `NS/audit/EXECUTION_INTERRUPTION_ASSESSMENT*`, `NS/audit/INCIDENT_AUDIT*`, `NS/reviews/REVIEW_EXECUTION_INTERRUPTION*`;
* anything under `p5y_k5_cell308_mb_r1/postexec/`, or any MB r1 target-run or qualification record;
* `NS/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`;
* any Cell-309 branch, file or record;
* candidate source (`mbs308_*`): not read, so the line citations of K11 are not re-verified (see §4).

I hold no E1″ material and no MB r1 target-run runtime or host observation.

---

## 2. Verdicts

REPAIR: REPAIRED_WITH_DEFECTS
HARNESS: SOUND_WITH_DEFECTS
RECORDS: ACCURATE_WITH_CORRECTIONS

**No verdict here accepts any amendment, supplement, addendum, erratum, host or decision.** This is a bounded
development-layer review. The supplement r64, erratum E1, the L-DET addendum and every D-* decision stay PROPOSED /
undecided. Only the formal route review, a fresh S12 re-rating and the owner can accept, reject or put anything into
force.

**REPAIR = REPAIRED_WITH_DEFECTS**
* What is repaired:
  * Every construction review 64 reported as wrongly ACCEPTED is now refused: N5, N5′ in local and global scope, P-c,
    N1 and N4-glued.
  * The owner's shallow bypass is refused, including in a shallow submodule.
  * K9's denial (N9) and crash (E1) paths are gone.
* L1 (MAJOR): the completeness guard reads only the shallow marker. A forged commit-graph, in the repository or in an
  **alternate** object store, or a rewritten loose object, hides the same deleted rejection, and the attestation is
  ACCEPTED:
  * `--is-shallow-repository` prints `false`;
  * HEAD, its commit id and its tree are unchanged;
  * `git fsck` and `commit-graph verify` fail.
* L2 (MAJOR): the new isolation is again under-pinned. 6 of 6 reviewer mutants survive:
  * 4 turn a refusal into ACCEPTED on a real synthetic repository;
  * 1 does so under fault injection;
  * 1 lets an `OSError` escape.

**HARNESS = SOUND_WITH_DEFECTS**
* What is sound:
  * RV18–RV30 are each killed by their own witness alone. I traced each one in the c50e73f8 record.
  * Q04 is back to its single site and is killed by the duplicate-verdict case.
  * The R5SYNC02 third edit is a necessary and faithful weakening.
  * The workflow counts 163/164 are right.
* Defects:
  * The new Q01 filter over-weakens: it also drops direct-child gitlinks from the evidence check, which changes an
    outcome (L4).
  * The isolation, the general `OSError` path and the exact-listing set check are unpinned (L2).

**RECORDS = ACCURATE_WITH_CORRECTIONS**
* What is accurate:
  * All 105 sha256 bindings in ledger lines 486–493 recompute at their introducing commit, and at 2275b3a0 where the
    file still exists.
  * The three compressed records equal their stated uncompressed digests. They are `gzip -n` (mtime 0, no name). Their
    10 inputs equal the claimed commit's blobs.
  * Every row re-classifies identically with that commit's own harness, and every mutated sha recomputes.
  * Review 64 and its 30 scratch files are byte-identical to the `scratchpad/review64` originals.
  * Only delta inputs, the ledger and BRIEF_INDEX (one appended row) were modified.
* Corrections:
  * A second failed native run on b23ee7dd (**38709761027**, the same Q01 ERROR) is unrecorded (L5).
  * E1.3, the commit messages and ledger 489 state the isolation and completeness more strongly than the code (Q5).

---

## 3. Review 64's findings and the completeness guard

"5e" = 5e8e3d9c, "now" = 2275b3a0. Probe re-runs:
* `rerun64/probes64_at_2275b3a0_out.json`, `probes64b_…`, `probes64c_…` (review 64's own scripts, unchanged);
* new probes: `probes65*.py.txt`.

| item | disposition (supplement r64 as corrected by E1) | verified at 2275b3a0 | status |
|---|---|---|---|
| K1 MAJOR: order rule depends on the reading repository's git configuration | isolation (`--no-replace-objects`, `-c log.showRoot=true`, `GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_ATTR_NOSYSTEM`, `GIT_GRAFT_FILE=/dev/null`; `--no-textconv --no-ext-diff` on `log`); tests; RV23/RV24; residual: repository-local config honoured. E1 withdraws the "shallow check equivalent" claim | **Code matches** (`:1158–1172`, `:1187–1189`, `:1345–1346`). N5 with `log.showRoot=false`: valid at 5e, **refused** now. probes64b: all 9 shallow and global-scope shapes refused. probes64c: textconv refused. Replace graft and `info/grafts` cut: refused (probes65). An env `GIT_CONFIG_COUNT` or `GIT_CONFIG_PARAMETERS` setting `log.showRoot=false` is overridden by `-c` (refused). **But:** only RV23 (showRoot) and RV24 (textconv) are pinned. Replace objects, grafts and the `_strictly_after` isolation are unpinned (RX1, RX2, RX5 survive with refused → ACCEPTED; L2). The trusted commit-graph / object store is outside the stated isolation (L1). Lazy fetch still runs repository-configured commands (L6). | **PARTIALLY RESOLVED.** The listed constructions are resolved; the isolation is under-pinned, and the history-truncation class is open (L1, L2). |
| K2 MINOR: Q04 extended instead of a test | single-site Q04; duplicate case in `test_acceptance_is_found_not_named`; RV21; ledger correction | Q04 is single-site (`run_mutants.py` Q04). The c50e73f8 record has Q04 and RV21 each killed by `test_acceptance_is_found_not_named`, and the failing assertion is the "accepting verdict line twice (review 64 K2)" case. Ledger 488 carries the corrected root cause. | **RESOLVED** |
| K3 MAJOR: RW1–RW4, RW6 survive | RV18–RV22 with direct tests | Each is killed in the c50e73f8 record with exactly its own witness as the only failing method (`reclassify65_out.json`). | **RESOLVED** (the new under-pinning is L2) |
| K4 MINOR regression | `sha in line.lower()` added; test; RV25 | `:1200–1203`. N4 glued: valid at 5e, **refused** now. RV25 is killed by its witness alone. Upper-case full sha glued to a hex character: refused in base, but unpinned (RX3 survives with refused → ACCEPTED; L2). | **RESOLVED** (pinning gap in L2) |
| K5 MINOR: later merges refuse | stated, not changed | N7: still refused. N7′: valid. Stated in §2 of the supplement. | **STATED.** Acceptable to carry: fail-closed and explicitly listed. |
| K6 MINOR: caller-input list incomplete | §2 lists every public function's parameters | AST enumeration of 39 public functions (`public_signatures65.json`). Every parameter is in either the caller list or the seam list; `clocks`, `apt_config_dump` and `pin_point` take none. `lx_verified.observe` passes only the canonical root (`lx_verified.py:26–27`). | **RESOLVED** |
| K7 MINOR: symlink accepted | modes 100644/100755 only, exact-path `ls-tree` | `:1333–1334`. N1: valid at 5e, **refused** now. Mode 100755: accepted (probes65). Direct-child gitlink: refused (UNAVAILABLE). RV26 is killed by its witness. | **RESOLVED** |
| K8 NOTE: vocabulary residuals | stated as enumerations | N3/N4 rows unchanged (still valid), as stated. | **STATED.** Acceptable to carry. |
| K9 NOTE (a) range-like names; (b) `PermissionError` crash | `cat-file blob HEAD:<path>`, `_tree_entries`; `OSError` caught in `auto_update_settings` | (a) N9 odd names: UNAVAILABLE at 5e, **valid** now. `x..HEAD`, `y^@`, `-n.md`, `a..b.md`, `z^!`, `*.md`, `[R]x.md` and tab names are all valid. `_ordered` still runs `rev-parse HEAD:<att_path>` (`:1368`). An attestation at `att/x..HEAD` while `att/x` exists refuses (`probes65c`; denial only, L7). (b) `:904–909`. The test only patches a `PermissionError`; RX4 (catch `PermissionError` only) survives, and an `EIO` `OSError` then escapes (L2). | (a) **RESOLVED** for reviews, residual in `_ordered` (L7). (b) **RESOLVED** in code, under-pinned (L2). |
| K10 NOTE: records | a16d2d99 inputs bound; timing; empty dirs | Ledger 488: workflow `7a9ee1dd…` and `run_mutants.py` `55a3e6e2…` recompute at a16d2d99. The timing statement matches the 5E8E3D9C record's `utc` (07:35:22Z). Both empty directories are named. | **RESOLVED** |
| K11 NOTE: L-DET gaps | additions stated in supplement §1 (addendum not edited) | The addendum is unchanged in the delta. The additions exist only in the supplement row. The `true`/`1`, `false`/`0` and `0`/`-0.0` equalities are Python facts. The 1822/1823 line citations are **UNVERIFIED** here (candidate source not read under brief 65); they agree with review 64's verified statement. | **STATED** in the supplement (acceptable while the addendum stays PROPOSED); the addendum itself is not corrected |
| Completeness guard (c50e73f8, E1) | `_history_complete` = `rev-parse --is-shallow-repository` prints exactly `false`; refuse otherwise | `:1175–1179`, `:1300–1301`. Results: owner construction at depth 2 refused; shallow submodule refused; `.git/shallow` deleted refused (UNAVAILABLE from the missing object); `blob:none` and `tree:0` partial clones refused (HISTORICAL when the promisor is reachable, UNAVAILABLE when not); bare, mirror, linked worktree, `--shared` alternates and full submodule refused (HISTORICAL). RV29 and RV30 are killed by their witness alone. **But** a forged commit-graph (local or in an alternate) and a rewritten loose blob object **ACCEPT** with `--is-shallow-repository` = `false` (L1). | **PARTIALLY RESOLVED.** The shallow bypass is closed; the "positive evidence of complete history" claim does not hold (L1). |

---

## 4. Answers Q2–Q5

### Q2 — Adversarial fail-closed audit

**Suites:** `python3.1x -B -W error::ResourceWarning -m unittest discover -s tests -v` gives **208 tests OK** on 3.11,
3.12 and 3.13 (`suite_python3.1x.txt`).

**Review 64's probes, re-run unchanged** (`rerun64/`):
* All 5e refusals stay refused.
* Changes, all intended: N1 symlink, N4 glued and N5 showRoot=false went from valid to **refused**; N9 odd names went
  from UNAVAILABLE to valid.
* The control stays valid.
* H12 and the U-rows are unchanged; W03 stays UNKNOWN.

**New probes** (`probes65.py.txt`, `probes65b.py.txt`, `probes65c.py.txt`; synthetic repositories only):

| construction | result | finding |
|---|---|---|
| att → rejecting review → `git rm` → acceptance; git writes a v1 commit-graph, then one CDAT parent entry (of the deletion commit) is set to "none" and the checksum recomputed | **ACCEPTED**. `--is-shallow-repository`=`false`; `rev-list --count HEAD` = 2 (4 with `-c core.commitGraph=false`); objects, commit ids and the HEAD tree are unchanged; `commit-graph verify` exits 1. The same reading with `-c core.commitGraph=false` added to `_GIT_ISOLATION` is refused (HISTORICAL). | L1 |
| same, but the forged graph lives in the **alternate** object store of a `--shared` clone; the reading repository has no graph | **ACCEPTED** (refused before the graph was forged) | L1 |
| same history; the loose blob of the deleted rejection is rewritten in place (same id, benign text) | **ACCEPTED**; `git fsck --full` exits 3 | L1 |
| same history; the deletion commit's loose object is rewritten without its `parent` line | refused (the order rule failed) | — |
| order rule: acceptance before the blob, blob commit's parent cut in a forged graph | refused (the boundary shows the acceptance as added) | — |
| depth-2 clone; depth-2 clone with `.git/shallow` deleted; shallow submodule | refused (UNAVAILABLE) | — |
| `--filter=blob:none` / `tree:0`, promisor reachable / removed | refused (HISTORICAL / UNAVAILABLE) | — |
| `remote.origin.uploadpack=<script>` in a `blob:none` clone | refused, **but the configured script ran** during the check (lazy fetch) | L6 |
| bare, mirror, linked worktree, `--shared` alternates, full submodule | refused (HISTORICAL) | — |
| `git replace --graft`, `info/grafts` cut | refused (HISTORICAL) | — (unpinned: L2) |
| caller environment `GIT_DIR=<other repository>` with `repo_root=<rejecting repository>` | **ACCEPTED** (reads the other repository) | L6 |
| env `GIT_CONFIG_COUNT` / `GIT_CONFIG_PARAMETERS` with `log.showRoot=false`, root acceptance | refused (`-c` wins) | — |
| local `core.bigFileThreshold=1`, `diff.renames=copies`, `log.follow`, `core.commitGraph=false`, `log.showSignature` with a pre-blob acceptance | refused | — |
| attestation at `att/x..HEAD` while `att/x` exists, otherwise valid | refused (`_ordered` `rev-parse` reads a range) | L7 |
| attestation path `att/a..b.json` | valid | — |
| committed attestation of 100 000 nested JSON arrays, sha matching | **`RecursionError` escapes `attestation_valid`** (therefore `preflight`); pre-existing | L7 |
| `auto_update_settings` with a unit root raising `EIO` | base: unknown (None); RX4: escapes | L2 |

**Classes:**
* **ACCEPTED where the stated rule refuses:** L1 (commit-graph local or alternate, rewritten blob), and L6 (caller
  environment `GIT_DIR`).
* **"Not enabled" wrongly:** none found. `OSError` now gives None (unknown), and `timer` then stays True.
* **Exception escaping:**
  * `attestation_valid` / `preflight`: `RecursionError` from `json.loads` (L7, pre-existing).
  * `auto_update_settings`: none at the base.
* **Regression of a 5e property:** none found. The new shallow refusal is a stated, fail-closed denial. It applies to
  the real repository as checked out (L-note in L1).

**Mutants:** 6 new (RX1–RX6), **0 killed, 6 survived**, each with a demonstrated outcome change (§7).

### Q3 — Harness integrity

* **RV18–RV30 are genuine direct witnesses.**
  * In the c50e73f8 record, each of the 13 is killed with exactly its own registered witness as the only failing
    method (`reclassify65_out.json`).
  * I read the tests:
    * RV18 patches `_commits` to return no blob commits (direct);
    * RV23/RV24 use a real local config / `.git/info/attributes`;
    * RV29 uses a genuine depth-2 clone with an identical HEAD tree, a full-history refusal and a positive control;
    * RV30 uses an unreadable answer.
  * All are direct.
  * Gap: none of them pins replace objects, grafts, global/system config, the `_strictly_after` isolation, the
    general `OSError` path or `_tree_entries`' set equality (L2).
* **Q04** is back to one site (`and ACCEPTANCE_VERDICT_LINE in verdicts:`). It is killed by the duplicate-verdict
  assertion. RV21 is killed by the same assertion.
* **Q01's direct-child-files edit over-weakens** (L4).
  * The filter keeps entries whose `cat-file -t` is exactly `blob`. That drops trees, the intended effect, but also
    direct-child **gitlinks**.
  * Outcome (`q01chk.py.txt`): a valid acceptance plus a direct-child gitlink `reviews/sub` is refused in base
    (UNAVAILABLE), **accepted** under Q01, and refused under a tree-only variant (`!= b"tree\n"`).
  * The tree-only variant is also KILLED under `classify_mutant`, with the same failing methods.
  * The recorded kill comes from the intended "not-accepted verdict in a scratch file" (subdirectory) assertion, so
    the kill evidence stands. Only the mutant's faithfulness is defective.
* **R5SYNC02's third edit** (`if path in entries and …`) is necessary and faithful. With `every` emptied,
  `_tree_entries([])` is `{}`, and the unedited mode check would raise `KeyError` on the accepting path (an exception,
  not an assertion). Under normal listings `every ⊇ tree`, so the edit is inert. It weakens nothing beyond the stated
  fault path.
* **Re-anchored RV08 and RV12:** RV08 drops `--diff-merges=separate`, and RV12 restores the bare `sha in line`. Same
  weakening.
* **Workflow:**
  * `assert … == 163` and `len(suites) == 164`;
  * `MUTANT_GROUP_SIZES` sums to 163 (RV 30);
  * `validate_registry()` == 163 is asserted by `test_mutation_harness.py`;
  * all three local records have 1 + N suites consistent with this. **Right.**
* **Native runs:**
  * 38714823675 (68a38c64): SUMMARY 161/161, digest `54cd1189…`, verified from the job log.
  * 38709764443 (b23ee7dd): digest `60b6cc04…`, verified.
  * 38709761027 (b23ee7dd, the same commit): SUMMARY 160/161, NOT_KILLED Q01 ERROR with 4 `test_sync_boundaries`
    assertions, artifact 11961735614 / `0d296071…`. **Unrecorded** (L5).
  * 38725820509 (2275b3a0): **in progress** at 11:30Z. Its result is **UNVERIFIED**.
  * No native run exists for c50e73f8, consistent with "before any push".
* I did not run the 40–60 minute full harness. The three local records re-classify cleanly, and the selected-mutant
  runs above used the pinned harness.

### Q4 — Records

* **Ledger:**
  * Each commit's ledger is a byte prefix of the next: 485 → 486 → 489 → 490 → 492 → 493 lines.
  * `check_records65.py.txt` recomputed **105 bindings** with 0 mismatches:
    * 486: brief 64 and the 5E8E3D9C record;
    * 487: review 64 and all 30 scratch hashes, at b23ee7dd and at 2275b3a0;
    * 488: the a16d2d99 workflow and `run_mutants.py`;
    * 489 / 490 / 492: all 10 inputs at b23ee7dd / 68a38c64 / c50e73f8, and the supplement and erratum;
    * 493: both gz records.
  * The ten inputs at 2275b3a0 equal those at c50e73f8, as ledger 493 states.
* **Compressed records:**
  * All three gunzip to their stated `uncompressed_sha256`. The headers have mtime 0 and no FNAME (`-n`).
  * `input_sha256` equals `input_sha256_after`, and all 10 entries equal the claimed commit's blobs.
  * Status counts: 150 / 161 / 163 KILLED, baselines 198 / 207 / 208, `utc` 07:35:22Z / 10:34:19Z / 11:11:40Z.
  * Re-classifying every row with that commit's own `run_mutants.py` reproduces every status. Witnesses and edits
    equal the registry, and every `mutated_lx_platform_sha256` recomputes.
  * `source_commit` is `null` inside the records. The commit binding rests on the input hashes, which hold.
* **Review 64 and scratch:**
  * `REVIEW_REVIEW63_REPAIR_DELTA.md` is byte-identical to `scratchpad/review64/…` (`cb776925…` = ledger 487).
  * All 30 scratch files are identical. `.py` became `.py.txt`, and `full_harness_py312.json` became `.json.gz`
    (identical after gunzip).
  * Not copied: `full_harness_py312.stdout`, `tmp/` and `tree_5e8e3d9c/`. These are exactly ledger 487's stated
    omissions.
* **Modified files:** `git diff --name-status 5e8e3d9c..2275b3a0` shows 37 A and 8 M:
  * the 6 tested inputs;
  * the ledger (append-only, verified);
  * `BRIEF_INDEX.md` (one appended row for brief 64).
  No historical review, governance or audit file changed.
* **Failed native runs:** 38709764443 is recorded (ledger 490). **38709761027 is not** (L5). The earlier failures
  (38680983939, 38689564567, 38692293195) are recorded in pre-delta lines.

### Q5 — Overstatement

1. **E1.3:** "Acceptance requires positive evidence that the reading repository's history is complete … Other means
   of truncating … are outside what the code can see: grafts and replace refs are disabled."
   * The evidence is only the absence of a shallow marker.
   * Commit-graph parent data (local or alternate) and loose objects are trusted without verification, and they
     truncate history with identical commit ids (L1).
   * Only "rewritten or force-pushed history" is named as undetected.
2. **b23ee7dd commit message and ledger 489:** "git reads isolated from global/system config, **attributes**, replace
   objects and grafts".
   * Only *system* attributes are excluded (`GIT_ATTR_NOSYSTEM`). The repository's `.gitattributes`,
     `.git/info/attributes` and a local `core.attributesFile` are still read. Textconv is neutralised by
     `--no-textconv`, not by attribute isolation; RV24's own test depends on `.git/info/attributes` being read.
   * The supplement row itself is precise.
3. **Supplement K1 / b23ee7dd:** the isolation is presented as a repair, with "Tests and mutants … for … K1", but only
   two of its six elements are pinned (L2).
4. **Ledger 490 and 68a38c64 commit message** call 38709764443 *the* failed run. Two failed on b23ee7dd (L5).
5. **Supplement K9:** "the attestation [is] read with `cat-file blob`" is true for the content read, but `_ordered`
   still resolves the attestation blob id with `rev-parse HEAD:<path>` (L7).
6. **Ledger 493:** "before any push" is consistent with the GitHub run list (no run on c50e73f8; the 2275b3a0 run was
   created 11:13:36Z, after the record's 11:11:40Z). Not overstated.
7. **"208 OK on 3.11–3.13" and "163/163 KILLED"** reproduce (suites) and re-classify (record). Not overstated.

---

## 5. New findings

**L1 — MAJOR — The history-completeness guard is not evidence of complete history: a forged commit-graph (in the
repository or in an alternate object store) or a rewritten loose object hides a deleted rejection while
`--is-shallow-repository` prints `false`, and the attestation is ACCEPTED.**
* **Location:**
  * `lx_platform.py:1158` (`_GIT_ISOLATION`, no `core.commitGraph=false`) and `:1175–1179` (`_history_complete`);
  * `_historical_review_blobs` (`:1216–1251`; blobs read with `cat-file blob <oid>`, content not re-hashed);
  * erratum E1.3, supplement r64 §2 (L-LIFE isolation).
* **Evidence** (`probes65_out.json`, `probes65b_out.json`): history att → rejecting review → `git rm` → acceptance. The
  full repository refuses (HISTORICAL). Three variants accept:
  * **Forged local commit-graph:** a git-written v1 graph with one parent entry set to "none" and a valid checksum.
    The HEAD commit id and tree are unchanged, `rev-list --count` gives 2 instead of 4, the guard passes, and the
    result is **ACCEPTED**. `git commit-graph verify` exits 1.
  * **Forged graph in an alternate:** the same forged graph placed in the **alternate** of a `--shared` clone is also
    **ACCEPTED**.
  * **Rewritten blob:** the deleted rejection's loose blob rewritten in place gives **ACCEPTED**; `git fsck --full`
    exits 3.
  * **Control:** adding `-c core.commitGraph=false` to `_GIT_ISOLATION` refuses the commit-graph cases.
* **Severity:** this is the class that E1 treated as a bypass (identical HEAD, cut history), reached without a
  shallow marker. Grafts and replace refs are disabled, but the commit-graph, git's other source of parent data, is
  not.
* **Correction:**
  * Add `-c core.commitGraph=false` to `_GIT_ISOLATION`. Optionally also set `GIT_NO_LAZY_FETCH=1` (git ≥ 2.44), or
    otherwise refuse partial clones.
  * Verify every blob read by recomputing its git object id from the returned bytes, or require a clean
    `git fsck --full --strict` (no alternates, or verify them too) as a precondition.
  * Add tests: a forged graph, local and alternate, and a rewritten blob. Add mutants.
  * Restate E1.3: the code trusts the reading repository's object store, commit-graph and alternates, and "positive
    evidence" means only that no shallow marker exists.
* **Side note (not a defect):** the real repository as checked out here is shallow (`true`), so the guard would refuse
  every attestation there. That is fail-closed, but the D-HOST-LIFETIME procedure needs to state that a full clone is
  required.

**L2 — MAJOR — The review-64 isolation and K9 repairs are under-pinned: 6 of 6 reviewer mutants survive, 4 with
refused → ACCEPTED on real synthetic repositories.** (§7; `reviewer65_mutants_result.json`)
* RX1 (`--no-replace-objects` dropped) and RX2 (`GIT_GRAFT_FILE` not redirected): a replace / graft cut of the deletion
  commit gives refused → **ACCEPTED**.
* RX5 (`_strictly_after` without isolation): a replace graft putting the pre-blob acceptance commit on top of the blob
  commit gives refused → **ACCEPTED**.
* RX3 (case-sensitive full-sha substring): `blob:A<SHA in upper case> REJECTED` gives refused → **ACCEPTED**.
* RX6 (`set(entries) != set(every)` dropped): UNAVAILABLE → **ACCEPTED** when the exact listing omits a file (fault
  injection only).
* RX4 (only `PermissionError` caught): an `EIO` `OSError` from `unit_enabled` escapes `auto_update_settings` (base:
  unknown).
* **Correction:** add direct tests for replace refs, `info/grafts`, the ancestry check under a replace graft, an
  upper-case glued sha, a non-`PermissionError` `OSError`, and a short exact listing. Register RX1–RX6 or equivalents.

**L3 — MINOR — The isolation leaves inherited caller-environment git variables in force.**
* **Location:** `_git_env()` (`:1161–1163`: `dict(os.environ, …)`).
* **Evidence:** with `GIT_DIR=<other repository>` in the process environment, `attestation_valid(repo_root=<rejecting
  repository>)` reads the other repository and **ACCEPTS** (`probes65_out.json` `caller_environment`).
  `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_COMMON_DIR`, `GIT_NAMESPACE`, `GIT_INDEX_FILE` and
  `GIT_CONFIG_COUNT` keys other than `log.showRoot` pass through the same way. The default root is canonical, but a
  hook or wrapper environment (git sets `GIT_DIR` in hooks) redirects every read.
* **Correction:** build the environment from an allow-list (`PATH`, `HOME`, `LANG`) and drop every `GIT_*` variable
  before adding the forced ones. Add a test.

**L4 — MINOR — Harness Q01 over-weakens: its filter also drops direct-child gitlinks.**
* **Location:** `run_mutants.py` Q01, first edit (`… == b"blob\\n"`).
* **Evidence:** `q01chk.py.txt`: a direct-child gitlink plus a valid acceptance is refused in base and **accepted** by
  Q01. A tree-only filter (`!= b"tree\n"`) keeps the refusal and is still KILLED with the same failing methods.
* **Correction:** filter out trees only, and state it in Q01's description.

**L5 — MINOR — A failed native run is unrecorded.**
* **Location:** ledger 490; 68a38c64 commit message.
* **Evidence:** run **38709761027** on b23ee7dd (created 09:00:30Z, conclusion failure) printed SUMMARY 160/161 with
  Q01 ERROR `NO_INTENDED_PROPERTY_ASSERTION`. Its artifact is 11961735614, digest
  `sha256:0d29607158a6824e23c0b14270a7d563ff694991b32e7e7324c4b2d5b03bcc99`. Only 38709764443 is recorded.
* **Correction:** add a ledger line recording it and saying why two runs were triggered on one commit.

**L6 — NOTE — Repository-configured commands still run during the check.**
* **Evidence:** in a `blob:none` clone, `remote.origin.uploadpack=<script>` ran during `attestation_valid`
  (`probes65b_out.json` `lazy_fetch_ran_configured_command: true`). The check also makes network or file fetches to
  the configured promisor.
* **Status:** this is within the stated residual ("repository-local configuration … still honoured"). But review 64
  K1 named command execution as part of the problem, and the supplement does not mention it.
* **Correction:** set `GIT_NO_LAZY_FETCH=1` (and `-c protocol.allow=never`), or refuse partial clones. State the
  residual.

**L7 — NOTE — Remaining denial and crash paths.**
* **(a) `_ordered` still resolves the attestation with `rev-parse HEAD:<att_path>` (`:1368`).**
  * An attestation at `att/x..HEAD` while `att/x` exists is refused (denial only; `probes65c_out.json`).
  * Fix: take the blob id from `ls-tree -z HEAD -- <att_path>`.
* **(b) `json.loads` in `attestation_valid` (`:1405–1408`) is not guarded against deep nesting.**
  * A committed attestation of 100 000 nested arrays raises `RecursionError` out of `attestation_valid`, and therefore
    out of `preflight`, on 3.11–3.13. This is pre-existing (5e8e3d9c had the same code) and fails closed by exception.
  * Fix: catch `RecursionError`, or bound the attestation size or depth.

**Counts:** BLOCKING 0 · MAJOR 2 (L1, L2) · MINOR 3 (L3, L4, L5) · NOTE 2 (L6, L7); 7 new findings.

---

## 6. Reproduction and scratch files

* Suites: `suite_python3.11.txt`, `suite_python3.12.txt`, `suite_python3.13.txt`.
* Review 64 probes re-run unchanged: `rerun64/probes64*_at_2275b3a0_out.json`.
* New probes:
  * `probes65.py.txt` / `probes65_out.json`: commit-graph, clone shapes, environment, local config, names;
  * `probes65b.py.txt` / `probes65b_out.json`: object rewrite, lazy fetch;
  * `probes65c.py.txt` / `probes65c_out.json`: `_ordered` range, nested JSON.
* Mutants: `reviewer65_mutants.py.txt` / `reviewer65_mutants_result.json` / `reviewer65_mutants_stdout.txt`.
* Q01 faithfulness check: `q01chk.py.txt`. Public signatures (K6): `public_signatures65.json`.
* Records: `check_records65.py.txt` / `check_records65_out.json`, and `reclassify65.py.txt` /
  `reclassify65_out.json`.

---

## 7. Reviewer mutants (brief 65)

**Method:**
* Each mutant is a copy of the 2275b3a0 `lx_platform.py` under `scratch/tmp/mut`.
* The pinned 208-test suite runs through the harness's own `run_suite` (`LX_PLATFORM_DIR`, `PYTHONWARNINGS=error`).
* Each result is classified by the harness's `classify_mutant` against a fresh baseline (PASS, 208), with the
  witnesses named per mutant.
* An outcome check runs base and mutant on one synthetic construction, each in a child interpreter.

**Result: 6 new mutants, 0 killed, 6 survived.** Every survivor changes an outcome in the weakening direction.

```
### RX1 SURVIVED | replace objects honoured   (replace --graft cut of the deletion commit: HISTORICAL refusal -> ACCEPTED)
-_GIT_ISOLATION = ("--no-replace-objects", "-c", "log.showRoot=true")
+_GIT_ISOLATION = ("-c", "log.showRoot=true")

### RX2 SURVIVED | info/grafts honoured   (.git/info/grafts cut: HISTORICAL refusal -> ACCEPTED)
-    return dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM="1",
-                GIT_GRAFT_FILE=os.devnull)
+    return dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM="1")

### RX3 SURVIVED | glued full sha named only in lower case   (`blob:A<SHA upper> REJECTED`: refused -> ACCEPTED)
-    return sha in line.lower() or any(sha.startswith(t.lower()) for t in _HEX_TOKEN.findall(line))
+    return sha in line or any(sha.startswith(t.lower()) for t in _HEX_TOKEN.findall(line))

### RX4 SURVIVED | only PermissionError from a unit root becomes unknown   (EIO: units None -> OSError escapes)
-        except OSError:                                         # review 64 K9: e.g. a root listable, not searchable
+        except PermissionError:

### RX5 SURVIVED | ancestry check without the isolation   (replace graft of the pre-blob acceptance commit onto the
###              blob commit: refused -> ACCEPTED)
-        r = subprocess.run(["git", "-C", str(repo_root), *_GIT_ISOLATION, "merge-base", "--is-ancestor", earlier,
-                            later], capture_output=True, timeout=60, stdin=subprocess.DEVNULL, env=_git_env())
+        r = subprocess.run(["git", "-C", str(repo_root), "merge-base", "--is-ancestor", earlier,
+                            later], capture_output=True, timeout=60, stdin=subprocess.DEVNULL)

### RX6 SURVIVED | exact-path listing need not cover every reviewed path   (fault-injected short listing:
###              UNAVAILABLE -> ACCEPTED)
-    if entries is None or set(entries) != set(every):
+    if entries is None:
```

Witnesses used:
* RX1, RX2: `test_review64_order_ignores_reading_configuration`, `test_review63_rejection_is_permanent`.
* RX3: `test_review64_sha_inside_longer_hex_run_still_names_it`, `test_review63_veto_words_and_references`.
* RX4: `test_review64_unreadable_unit_root_is_unknown_not_a_crash`.
* RX5: `test_accepting_line_must_post_date_the_attested_blob`, `test_review64_order_ignores_reading_configuration`.
* RX6: `test_review64_range_like_review_names_do_not_block`,
  `test_malformed_listing_and_nonutf8_review_blob_refuse_verification`.

In every case the suite returned 0 with 208 tests, and the status was SURVIVED.

Additional harness check (not a reviewer mutant): **Q01 tree-only variant KILLED** (the same five failing methods as
the registered Q01). It shows that the faithful weakening is still detected (L4).
