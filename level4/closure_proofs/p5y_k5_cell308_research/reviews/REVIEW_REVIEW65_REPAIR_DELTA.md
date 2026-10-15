# Review: the coordinator's repairs of review 65's findings (combined Cell-308 development source, Cloud route r1, S4 changed branch)

* Reviewer: **reviewREVIEW65_REPAIR (fresh agent, brief 66)**
* Date: 2026-10-15 (UTC), about 13:05Z to 13:40Z.
* Pinned commit: **`774f2183667e5e03aa9a9991c2c2c979dc8fa1c9`** (branch `codex/cell308-claude-r5-integration`, draft PR
  flaggielover/ReBaseGuard#3). Detached worktree `scratchpad/review66/tree_774f2183`. `git status --porcelain` was
  empty after every run; I wrote nothing there.
* Delta: `2275b3a0..774f2183`, three commits: a8a407bc (brief 65), b0b73adb (review 65 recorded, repairs), 774f2183
  (local full-run record).
* NS = `level4/closure_proofs/p5y_k5_cell308_research/`, DEV = `NS/streams/CLOUD_R1_LINUX_DEV`. Line numbers refer to
  the 774f2183 files.
* Scratch: `/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review66/` ("scratch").
  Probes ran on `scratch/base/lx_platform.py`, sha256 `26aca753…`, equal to the 774f2183 blob (`06f5599a`) and to
  ledger 498's binding. The 2275b3a0 comparison ran on `scratch/base2275/lx_platform.py` (`96eb3a5e…`). Scripts are
  stored as `*.py.txt`.
* Local git: **2.43.0** (Ubuntu build). Native runner git (from the 2275b3a0 job log): **2.55.0**.
* `new_target_evaluations = 0`. I ran no cell, drift, certificate, decoy, science module, qualification case or
  candidate code. I installed nothing and changed no setting.

---

## 1. Exposure disclosure

**Opened:**
* brief 66 in the shared checkout (the only file read there).
* In the pinned tree: the `2275b3a0..774f2183` diffs of `lx_platform.py`, `test_lx_platform.py`, `run_mutants.py`,
  `test_mutation_harness.py` and the workflow; `lx_platform.py` lines 1150–1520; the attestation test fixtures and
  the review-65 tests in `tests/test_lx_platform.py`; `run_mutants.py` registry tail, `PROPERTY_WITNESSES`,
  `run_suite`, `classify_mutant`, `apply_mutation`, `validate_registry`, `main`; review 65 as recorded; supplement r65;
  ledger lines 494–499; the commit messages of the delta; the heads / bodies of `probes65*.py.txt`, `q01chk.py.txt`,
  `reviewer65_mutants.py.txt` (executed only as described in §4).
* The compressed local record `LOCAL_FULL_HARNESS_PY312_B0B73ADB.json.gz`: decompressed in memory; header fields,
  input hashes, status counts and mutant rows / failure names read. Synthetic test output only.
* `scratchpad/review65/` originals, for the byte comparison of Q4 only. I did not open `review65/tree_2275b3a0/` or
  `review65/tmp/` (names seen in a listing).

**Name-level contact:** the scratchpad root listing (`MUTANTS_RUN_R*.json`, `fix65`, `fix_shallow`, `fsck_probe`,
`gate.txt`, `gitprobe*`, `inv_check.json`, `ldet`, `mut*.log`, `native-r3`, `r65files.txt`, `rev5`, `review59`–`review66`,
`rv`, `scan*.json`, `shallow_probe`). Nothing opened except `review65/` (above) and my own `review66/`. `git diff
--name-only 2275b3a0..774f2183` grepped for audit / interrupt / mb_r1 / 309 / exposure: no hits.

**Shared object store:** the pinned worktree's git dir lives in the shared repository; every git read of the pinned
tree went through it (objects only). I ran no `git` command in the shared checkout and no `fsck` on the real repository.

**GitHub (read-only):** the branch's run list; metadata of runs 38739675256 and 38725820509 and their jobs; the last 75
lines of job 116391283635 (run 38725820509: SUMMARY line, artifact digest, git version). Job logs through `gh` were
refused by the blob host; the GitHub MCP log tool returned them.

**Live calls:** none against the real repository. Every `attestation_valid` / `_history_complete` call passed
`repo_root=<synthetic repository under scratch/tmp>` with `machine_identity` patched. The unit suites call them only
on synthetic repositories or with `_git` patched.

**Not opened, grepped or read:** `NS/audit/EXECUTION_INTERRUPTION_ASSESSMENT*`, `NS/audit/INCIDENT_AUDIT*`,
`NS/reviews/REVIEW_EXECUTION_INTERRUPTION*`, anything under `p5y_k5_cell308_mb_r1/postexec/` or any MB r1 target-run or
qualification record, `NS/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`, any Cell-309 branch, file or record, candidate
source. No accidental contact.

---

## 2. Verdicts

REPAIR: REPAIRED_WITH_DEFECTS
HARNESS: SOUND_WITH_DEFECTS
RECORDS: ACCURATE_WITH_CORRECTIONS

**No verdict here accepts any amendment, supplement, addendum, erratum, host or decision.** This is a bounded
development-layer review. Supplement r65, supplement r64, erratum E1, the L-DET addendum and every D-* decision stay
PROPOSED / undecided. Only the formal route review, a fresh S12 re-rating and the owner can accept, reject or put
anything into force.

**REPAIR = REPAIRED_WITH_DEFECTS.**
* Repaired: every construction review 65 reported as ACCEPTED is now refused (forged CDAT parent graph, local and in
  an alternate; rewritten loose blob; caller `GIT_DIR`). RX1–RX6 equivalents are registered and killed. The
  `x..HEAD` attestation path and the deep-JSON crash are fixed. Q01 is tree-only.
* **M1 (MAJOR):** the commit-graph is still trusted for **changed-path Bloom filters**, which `git fsck` and
  `commit-graph verify` do not check. A forged filter hides the rejection's commit from the history-wide veto scan, and
  the attestation is **ACCEPTED**, with `fsck --full --strict` = 0, `commit-graph verify` = 0, not shallow, no refused key.
* **M2 (MAJOR):** the new `git fsck` reads the index, so a repository-local **`core.fsmonitor` command runs** during the
  check (it did not at 2275b3a0 on a full clone). That command can rewrite the deleted rejection's blob after fsck has
  hashed it: fsck exits 0 and the attestation is **ACCEPTED**.

**HARNESS = SOUND_WITH_DEFECTS.** RV30–RV42 and Q01 are each killed, and RV30–RV38, RV40–RV42 by their own witness
alone. Q01's tree-only filter is faithful. 175/176 is right. Defects: RV39 bundles two independent defences, so
`GIT_NO_LAZY_FETCH` is unpinned. The `_ordered` regular-file check, `--strict` and the config-listing failure path
are unpinned too. 4 of my 5 mutants survive (M4).

**RECORDS = ACCURATE_WITH_CORRECTIONS.** 49 sha256 bindings in ledger 494–499 recompute, with one exception: ledger 495
binds `scratch_REVIEW_REVIEW64_REPAIR/job_116337943534.log`, and **that file is not committed** (M6). The compressed
record, its inputs and every row re-classify. Every native run since 9b6347cb is recorded, except the one on 774f2183
itself (still in progress). Some wording overstates (Q5, M7).

---

## 3. Review 65's findings (Q1)

"now" = 774f2183. Probe files: `probes66*.py.txt` / `*_out*.json`, `rerun65/` (review 65's and 64's probes re-run
unchanged on the new source), `reviewer66_mutants*`, `check_records66*`.

| finding (review 65) | disposition (supplement r65) | verified at 774f2183 | status |
|---|---|---|---|
| L1 MAJOR: forged commit-graph / rewritten loose object hides a deleted rejection | `_history_complete` adds a local-config key check and a clean `git fsck --full --strict --no-dangling`; test `test_review65_forged_graph_and_rewritten_object_refuse`; RV31 | Code matches (`:1185–1200`). Review 65's constructions are now refused (`rerun65/probes65*_at_774f2183_out.json`: `forged_graph`, `alternate_has_forged_graph`, `blob_object_rewritten` valid → refused, reason "history completeness"). I measured fsck rc 3 on the rewritten blob. RV31 is killed by its witness alone. **But:** (i) a forged changed-path **Bloom filter** (local, in an alternate, or in a split chain) passes fsck (rc 0) and `commit-graph verify` (rc 0), and the result is **ACCEPTED** (M1). (ii) A local `core.fsmonitor` hook runs inside that fsck and can rewrite the blob after verification, giving **ACCEPTED** (M2). | **PARTIALLY RESOLVED.** The reported constructions are closed. The class (a forged commit-graph or object store hides a deleted rejection) is still open. |
| L2 MAJOR: isolation / K9 repairs under-pinned (RX1–RX6) | tests for replace graft, `info/grafts`, ancestry under a replace graft, upper-case glued sha, EIO, short listing; RV33–RV38 | RV33, RV34, RV35 are each killed by `test_review65_replace_refs_and_grafts_are_ignored` alone. RV36 is killed by `test_review64_sha_inside_longer_hex_run_still_names_it`, RV37 by `test_review64_unreadable_unit_root_is_unknown_not_a_crash`, and RV38 by `test_review65_short_exact_listing_refuses`, each as the only failing method, both in my single runs and in the b0b73adb record. The edits are the RX1–RX6 edits re-anchored. | **RESOLVED** (new pinning gaps: M4) |
| L3 MINOR: inherited `GIT_*` | allow-list env (`:1161–1170`); test; RV40 | Code matches. `GIT_DIR=<good>`, `GIT_WORK_TREE`, `GIT_CONFIG_COUNT` (`core.commitGraph=false`), `GIT_CEILING_DIRECTORIES` and `GIT_NO_REPLACE_OBJECTS=0` in the caller environment are all refused (HISTORICAL) (`probes66 env_allowlist`). Review 65's `bad_with_GIT_DIR=good`: valid → refused. RV40 is killed by its witness alone. | **RESOLVED** |
| L4 MINOR: Q01 drops gitlinks | `!= b"tree\n"` | Registry edit matches. `q01chk` re-run: a direct-child gitlink with a valid acceptance is refused under base and under Q01 alike (UNAVAILABLE). Q01 is KILLED with the same 5 methods as before. | **RESOLVED** |
| L5 MINOR: run 38709761027 unrecorded | ledger 496 | Line 496 carries the run, the commit, 160/161, Q01 ERROR, artifact 11961735614 / `0d296071…` and the duplicate-push explanation. All agree with review 65's API reading. | **RESOLVED** |
| L6 NOTE: configured commands run during the check | partial-clone / promisor key refusal; `GIT_NO_LAZY_FETCH=1`; test; RV39 | With the keys in `.git/config`, a blob:none clone is refused before any fetch, and the configured upload-pack does not run (review 65's `lazy_fetch_ran_configured_command`: true → false). **But:** (i) the key check reads `.git/config` without includes, so keys moved into an `include.path` file or `config.worktree` pass it (`_history_complete` = True for a partial clone). Only `GIT_NO_LAZY_FETCH` then stops the command, and nothing pins it: RY1 removes it, survives, and the configured command runs (M3, M4). (ii) The new fsck runs `core.fsmonitor` (M2). | **PARTIALLY RESOLVED** |
| L7 NOTE: (a) `rev-parse HEAD:<path>` in `_ordered`; (b) deep JSON | exact-path listing, regular files only; `RecursionError` refused; test; RV41/RV42 | (a) `:1389–1390`. Review 65's `att/x..HEAD`: refused → **valid**. (b) `:1431`. 100 000-deep JSON: `RecursionError` → refused ("nested too deeply") on 3.11–3.13 (suite). RV41/RV42 are killed by their witness alone. Side effect: `./att/HOST.json` was valid at 2275b3a0 and is now refused (denial; M5). The "regular files only" rule is unpinned (RY3; M4). | **RESOLVED** (pinning gap M4) |

**Supplement r65 §2: not accurate as written.**
* The three conditions are an exact description of the code.
* "**Establishes** that the object store … is internally consistent and complete as git verifies it … and that git's
  own parent data (commit-graph, shallow marker) agrees with it" is literally true of parents. But it is offered as the
  basis for trusting the history the check reads, and the check also reads the commit-graph's **changed-path Bloom
  filters**, which no git verification covers (M1).
* fsck's verdict can also be defeated by a command the repository itself configures (M2).
* The condition "names no `fsck.*` key and no partial-clone or promisor key" holds only for `.git/config` read
  without includes (M3).
* The "does not establish" list carries the K1 residual (local configuration honoured "in other ways"). That residual
  is broad enough to cover M2 and M3 in words, but the supplement and the code docstring present the local-config
  refusal and the lazy-fetch block as answering configured-command execution, and neither mentions `include.*`,
  `config.worktree` or `core.fsmonitor`.
* What refuses is incomplete: `--strict` turns every fsck warning into an error, and fsck also reads the index and
  worktree state (M5).

---

## 4. Answers Q2–Q5

### Q2 — Adversarial fail-closed audit

**Suites:** `python3.1x -B -W error::ResourceWarning -m unittest discover -s tests -v` gives **215 tests OK** on 3.11,
3.12 and 3.13 (`suite_python3.1x.txt`).

**Review 65's and 64's probes, re-run unchanged on the new source** (`rerun65/*_at_774f2183_out.json`; compared with
`compare66.py.txt`):
* Now refused: every review-65 ACCEPTED row (`forged_graph`, `alternate_has_forged_graph`, `blob_object_rewritten`,
  `bad_with_GIT_DIR=good`).
* Every refused row stays refused. The reasons of the partial-clone, removed-shallow-file and cut-parent rows moved to
  "history completeness".
* Fixed: `lazy_fetch_ran_configured_command` true → false; `x..HEAD` attestation path refused → valid; deep JSON
  `RecursionError` → refused.
* Review 64's probes: every row is identical to 2275b3a0, including the stated N3/N4/N7/N9 vocabulary residuals and
  the control.

**New probes** (`probes66.py.txt`, `probes66b.py.txt`; synthetic only; controls extend `_GIT_ISOLATION` in memory):

| construction | result | finding |
|---|---|---|
| att → rejecting `reviews/veto.md` → `git rm` → acceptance. `git commit-graph write --reachable --changed-paths`, then the 7 Bloom-filter bytes (BDAT via BIDX) of the rejection-adding commit are zeroed and the checksum recomputed. Parents, OIDs, generations and dates are unchanged. | **ACCEPTED.** `--is-shallow-repository` = false; no refused key; `fsck --full --strict --no-dangling` rc **0**; `commit-graph verify` rc **0**; `_history_complete` True. `rev-list --full-history HEAD -- <review dir>` lists 2 commits (3 with `core.commitGraph=false`), and the rejection's commit is missing. Honest Bloom graph: refused (HISTORICAL). | M1 |
| same forged filter in the **alternate** of a `--shared` clone | **ACCEPTED** (refused before the forgery) | M1 |
| same forged filter in a **split** chain layer (layer renamed to its new checksum, chain file updated) | **ACCEPTED**; fsck rc 0; verify rc 0 | M1 |
| control: the three above with `-c core.commitGraph=false` added to `_GIT_ISOLATION` | all **refused** | M1 |
| valid full repository, local `core.fsmonitor=<script>` | ACCEPTED (correct), but **the script ran twice inside `_history_complete`** (the `git fsck` call). At 2275b3a0 the same repository: ACCEPTED, script **not run**. | M2 |
| rejected-then-deleted repository; local `core.fsmonitor` hook that copies a benign object over the rejection's loose blob | **ACCEPTED**. The hook runs during fsck's index read, after the loose-object scan; fsck rc 0. A later fsck gives rc 3 (hash-path mismatch). | M2 |
| control: the same with `-c core.fsmonitor=false` added | refused (HISTORICAL); hook not run | M2 |
| blob:none clone, keys left in `.git/config` | refused ("history completeness"); upload-pack not run | — |
| blob:none clone; `remote.origin.promisor` / `partialclonefilter` moved to an `include.path` file (2.43 sets no `extensions.partialclone`) | `_history_complete` **True** (fsck rc 0). Final: refused (UNAVAILABLE, unreadable history). The configured upload-pack is not run **only because** this git honours `GIT_NO_LAZY_FETCH` ("warning: lazy fetching disabled"). The same clone under RY1 (`GIT_NO_LAZY_FETCH` removed): the script **runs**. | M3, M4 |
| same with `remote.origin.promisor` in `config.worktree` (`extensions.worktreeConfig=true`) | `--local` listing omits it; refused (UNAVAILABLE); no command | M3 |
| old commit with `badTimezone` (an fsck error) + valid acceptance; `fsck.badTimezone=ignore` directly in `.git/config` | refused (stated rule) | — |
| same key through `include.path` | fsck rc 0, **ACCEPTED** (the stated rule refuses any `fsck.*` key) | M3 |
| rewritten rejection blob + `fsck.skipList` naming it through an include | refused (fsck rc 3: hash mismatches are not skippable) | — |
| legitimate history whose old tree has a zero-padded mode (fsck *warning* `zeroPaddedFilemode`) | fsck rc 0 by default, rc 1 with `--strict` → **refused**. Accepted at 2275b3a0. | M5 |
| valid committed history; only the index names a staged blob whose object was removed | fsck rc 2 → **refused** (working state, not committed evidence). Accepted at 2275b3a0. | M5 |
| attestation spelt `./att/HOST.json` | `cat-file` reads it; `_ordered`'s exact listing does not match → refused. Valid at 2275b3a0. `att//…`, `att/./…`, `:(top)…`: not committed (unchanged). | M5 |
| local `core.useReplaceRefs=true` + replace graft cut | refused (HISTORICAL) | — |
| attestation as a symlink to a regular JSON file | refused (unchanged). A symlink whose **target text is** the attestation JSON: refused in base, **ACCEPTED** under RY3 | M4 |

**Classes:**
* **ACCEPTED where the stated rule refuses:**
  * M1: Bloom-filter forgery (local, alternate, split chain).
  * M2: fsmonitor-driven rewrite.
  * M3: an `fsck.*` key through `include.path`. The repository in that case is benign, but the stated rule refuses it.
* **A configured command runs during the check:**
  * M2: `core.fsmonitor`, in every repository that sets it. This is a regression of 2275b3a0's full-clone behaviour.
  * M3 / M4: a promisor hidden in an include runs upload-pack whenever `GIT_NO_LAZY_FETCH` is absent or ineffective.
    The variable is unpinned (RY1).
* **Exception escaping `attestation_valid` / `preflight`:** none found. Timeouts, `OSError`, `ValueError` and
  `UnicodeError` are caught in `_git`. `RecursionError` is caught. `json.loads` on bytes raises `ValueError` subclasses
  for bad encodings and for the int-digit limit.
* **Legitimate full-clone cases newly refused and not stated:** `--strict` warning promotion, index / worktree state,
  and the `./` path spelling (M5). Also, every fsck error in an old history (e.g. `badTimezone`) refuses. Fail-closed.
* **Regression of a 2275b3a0 property:** M2 (no configured command on a full clone) and the denials in M5. No
  previously refused construction is now accepted, except via M1 / M2, which were already accepted at 2275b3a0 and are
  not fixed (the Bloom construction is also ACCEPTED at 2275b3a0: `probes66_at_2275b3a0_out.json`).
* **Native git 2.55:** M1–M3 were measured on 2.43.0 only. Bloom-filter content verification in newer git is
  **UNVERIFIED** here.

**Mutants:** 5 new (RY1–RY5), **1 killed, 4 survived** (§7).

### Q3 — Harness integrity

* **RV30 (re-anchored)** `!= b"false\n"` → `== b"true\n"`: an unreadable answer passes the shallow test. This is the
  same weakening as before. It is killed by `test_review64_shallow_history_refuses_deleted_preboundary_rejection`
  alone (my run and the b0b73adb record).
* **RV31–RV42:** each is KILLED in my single runs against a fresh 215-test baseline. The failing methods are exactly
  the registered witness for RV31–RV38 and RV40–RV42. RV39 also fails RV32's witness, as expected, because its first
  edit drops the promisor keys. The b0b73adb record gives identical failing sets (`check_records66_out.json`
  `selected_rows`). Reading the tests:
  * RV31 uses review 65's CDAT forgery and a real rewritten loose blob, and asserts the completeness reason. Direct.
  * RV33–RV35 use a real replace graft, real `info/grafts` and a real ancestry graft. Direct.
  * RV40 uses real `GIT_DIR` / `GIT_OBJECT_DIRECTORY`. Direct.
  * RV41 uses a real `x..HEAD` path. Direct.
  * RV38 uses fault injection only, as stated.
* **Gaps:**
  * RV31's positive control writes the graph **without changed paths**, so the Bloom surface is untested (M1).
  * Every fixture repository sets local `core.fsmonitor=false` (`GIT_FIXTURE_CONFIG`, test file `:1015–1016`), so the
    suite cannot observe M2.
* **RV39 (two edits):** it is a faithful weakening of the combined property ("no configured command runs in a partial
  clone"), and with both edits removed the witness catches the marker. But it bundles **two independent defences**:
  * the key refusal alone is pinned by RV32 (any promisor key refuses);
  * `GIT_NO_LAZY_FETCH` alone is pinned by nothing. RY1 (that single edit) **survives**, and with the keys hidden it
    lets the configured upload-pack run (M3/M4).
  RV39 therefore over-states what is witnessed.
* **Q01 tree-only filter:** faithful. A tree is dropped (the intended non-recursion). A gitlink is kept and refuses as
  in base (`rerun65/q01chk_at_774f2183_out.json`: base / Q01 both UNAVAILABLE). It is killed by the same 5 methods.
* **Counts:**
  * `MUTANT_GROUP_SIZES` sums to 175 (RV 42);
  * `validate_registry()` = 175 is asserted in `test_mutation_harness.py`;
  * the workflow asserts `== 175` and `len(suites) == 176` (baseline + 175);
  * the b0b73adb record has 175 rows and 215-test suites.
  **Right.**
* **Labels:** `main()` labels every `RV*` row "Claude review 63" (`run_mutants.py:1132`), including RV31–RV42 from
  review 65 (record: `origin_labels_RV31_42 = ["Claude review 63"]`). Cosmetic (M7).

### Q4 — Records

* **Ledger:**
  * Each commit's ledger is a byte prefix of the next: 493 → 494 → 498 → 499 lines.
  * `check_records66.py.txt` recomputes **49 bindings** at the introducing commit and at 774f2183:
    * 494: brief 65;
    * 495: review 65 `af6ce549…` and 35 scratch hashes (34 committed files plus the job log);
    * 498: 10 inputs and supplement r65 `7855d10b…`;
    * 499: the gz record.
  * Every binding recomputes except **`job_116337943534.log` (ledger 495), which is absent at b0b73adb and at 774f2183**.
    The original in `scratchpad/review65/` has exactly the bound hash `fed307d6…`. Ledger 495's omission statement
    ("bytecode caches, the pinned worktree and temp dirs not copied") does not name it (M6).
* **Compressed record:**
  * The record gunzips to `32a27a83…` (= ledger 499). Header: mtime 0, no FNAME, XFL 2 (= `-9 -n`).
  * The 10 `input_sha256` entries equal `input_sha256_after`, ledger 498 and the blobs at b0b73adb and at 774f2183.
  * Baseline 215 PASS; 175/175 KILLED; `utc` 13:02:48Z, before the 774f2183 run was created (13:04:42Z), so "before any
    push" holds.
  * Re-classifying every row with the pinned harness reproduces every status. Edits and witnesses equal the registry,
    and every `mutated_lx_platform_sha256` recomputes (`row_problems: []`).
  * `source_commit` is null. The commit binding rests on the input hashes, which hold.
* **Review 65 and scratch:**
  * `REVIEW_REVIEW64_REPAIR_DELTA.md` and all 34 committed scratch files are byte-identical to the `scratchpad/review65`
    originals (`.py` → `.py.txt` for the three `lx_platform.py` copies).
  * Not committed: `__pycache__`, `tmp/`, `tree_2275b3a0/` (stated) and `job_116337943534.log` (not stated, yet
    bound; M6).
* **Modified files** (`git diff --name-status 2275b3a0..774f2183`): 38 A, 7 M. The 7 M are the 5 tested inputs, the
  ledger (append-only, verified) and `BRIEF_INDEX.md` (one appended row for brief 65). No historical review, governance
  or audit file changed.
* **Native runs since 9b6347cb:**
  * Recorded: 38689564567 and 38692293195 (485), 38694984232 (486/488), 38709764443 (490/496), 38709761027 (496),
    38714823675 (491/493), 38725820509 (496).
  * 38725820509: the job log SUMMARY reads 163/163, `pass: true`, expected tests 208. **Verified.**
  * Ledger 496 gives no artifact id / digest for it (11969136626, `3be305c4…`), unlike earlier run lines (M7).
  * 38739675256 (774f2183): **in_progress** at 13:25Z; its result is **UNVERIFIED**. It cannot be recorded in the
    commit it tests; ledger 499 says PENDING.

### Q5 — Overstatement

1. **b0b73adb commit message:** "a forged commit-graph or a rewritten object **no longer hides** a deleted rejection".
   A forged commit-graph (Bloom chunk) still does (M1). A rewritten object still does when the repository's own
   fsmonitor performs the rewrite (M2).
2. **`_history_complete` docstring and supplement §1 L1:** "a forged commit-graph … fails it" and "That fsck checks
   every object, alternates included, and the commit-graph". This is true of parents and object hashes only, not of
   changed-path filters (M1).
3. **Supplement §2 "establishes … complete as git verifies it":** see §3 above (M1, M2). The condition "names no
   `fsck.*` key" holds only for `.git/config` without includes (M3).
4. **Supplement L6 / ledger 498 "L6 partial clones refused":** the final outcome is a refusal, but the completeness
   check itself accepts a partial clone whose keys sit in an include, and only the unpinned `GIT_NO_LAZY_FETCH` stops
   the configured command (M3, M4). The test docstring "the check refuses before any fetch and runs nothing" holds only
   for keys written directly in `.git/config`.
5. **Supplement L6:** "`GIT_NO_LAZY_FETCH=1`, which git 2.44 and later honour". The local git 2.43.0 honours it (it
   prints "lazy fetching disabled"), so the local runs did exercise it. The statement is imprecise, not inflated.
6. **Supplement L1:** "an honest commit-graph is accepted (positive control)". The control graph has no changed-path
   filters, so it is not a control for the full commit-graph surface.
7. **Supplement L1 "Measured on git 2.43 … rewritten blob rc 3":** reproduced (rc 3). The forged-graph rc 16 was not
   re-measured, but review 65's graph construction is refused with the completeness reason.
8. **Not overstated:**
   * "215 tests OK on 3.11/3.12/3.13" (reproduced);
   * "175/175 KILLED" (re-classified);
   * "inputs equal to b0b73adb's blobs";
   * "before any push";
   * ledger 497's corrections of E1.3 / ledger 489 wording.

---

## 5. New findings

**M1 — MAJOR — The commit-graph's changed-path Bloom filters are trusted and unverified: a forged filter hides the
rejection's commit from the history-wide veto scan, and the attestation is ACCEPTED with a clean strict fsck.**
* **Location:**
  * `lx_platform.py:1158` (`_GIT_ISOLATION`, no `core.commitGraph=false` or `commitGraph.readChangedPaths=false`);
  * `:1242` (`rev-list --full-history HEAD -- ACCEPTANCE_REVIEW_DIR`, a single-pathspec walk, which uses Bloom
    filters);
  * `:1185–1200` (`_history_complete`);
  * supplement r65 §1 L1 and §2; the b0b73adb message.
* **Evidence** (`probes66_out.json` `bloom_local`, `bloom_alternate`, `bloom_split_chain`):
  * Construction: rejection added (c804e5e0), deleted, acceptance. Zeroing the rejection commit's 7 BDAT bytes and
    re-checksumming gives the results below.
  * Results: not shallow; no refused key; `fsck --full --strict --no-dangling` rc 0; `commit-graph verify` rc 0;
    `_history_complete` True. The `rev-list` loses c804e5e0, and the result is **ACCEPTED**.
  * The same holds in an alternate store and in a split-chain layer.
  * Controls: an honest `--changed-paths` graph gives refused, and `-c core.commitGraph=false` in the isolation gives
    refused in all three cases (`probes66_out_commitgraph_off.json`).
  * Also ACCEPTED at 2275b3a0, so this is the unfixed remainder of review 65 L1, not a regression.
* **Correction:**
  * Add `-c core.commitGraph=false` to `_GIT_ISOLATION`, which disables the whole graph (parents and Bloom), as review
    65 already proposed. At minimum add `-c commitGraph.readChangedPaths=false`.
  * Add a test with a forged changed-path filter (local and alternate) and a mutant that re-enables Bloom reads.
  * Restate supplement §2 and the docstring.
  * Measure on the native git 2.55 too.

**M2 — MAJOR — `git fsck` runs the repository's own `core.fsmonitor` command during the completeness check; that
command can rewrite an object after fsck has verified it, and the attestation is ACCEPTED.**
* **Location:** `lx_platform.py:1200` (fsck without arguments reads the index); `_GIT_ISOLATION` (`:1158`; no
  `core.fsmonitor=false`); test fixtures `GIT_FIXTURE_CONFIG` (test file `:1015–1016`), which set
  `core.fsmonitor=false` in every synthetic repository and so hide the case from the suite.
* **Evidence:**
  * `probes66_out.json` `fsmonitor_valid_repo`: the hook ran twice inside `_history_complete`. At 2275b3a0 the same
    repository did not run it (`probes66_at_2275b3a0_out.json`).
  * `probes66b_out.json` `fsmonitor_rewrites_object_during_fsck`: the hook overwrites the deleted rejection's loose
    blob with a benign object. fsck rc 0, and the result is **ACCEPTED**. A later fsck reports a hash-path mismatch
    (rc 3).
  * With `-c core.fsmonitor=false` the result is refused (HISTORICAL) and the hook does not run
    (`probes66b_out_fsmonitor_off.json`).
* **Severity:** this is the L1 attacker (one who controls the reading repository's files), and it defeats the L1
  repair's main mechanism. It is a new configured-command path that the L6 repair was meant to exclude. The K1 residual
  ("local configuration honoured in other ways") covers it only in the broadest reading, and nothing names it.
* **Correction:**
  * Add `-c core.fsmonitor=false` to the isolation, and audit fsck's other index-time hooks.
  * Add a test with a repository that sets `core.fsmonitor` (not overridden by the fixture) and asserts that no marker
    is written. Add a mutant.
  * State the remaining time-of-check/time-of-use gap: any process with write access can change objects between fsck
    and the reads.

**M3 — MINOR — The local-configuration key check reads `.git/config` only, with includes off, but git honours
`include.path` / `includeIf` and `config.worktree`.**
* **Location:** `lx_platform.py:1182`, `:1196–1199`.
* **Evidence** (`probes66_out.json`):
  * `fsck.badTimezone=ignore`: refused when set directly, **ACCEPTED** through `include.path` (`fsck_key_in_include`).
  * Promisor / partial-clone-filter keys in an include give `_history_complete` = True for a blob:none partial clone
    (`partial_clone_keys_in_include`). The same holds for `config.worktree` with `extensions.worktreeConfig`. Only
    `GIT_NO_LAZY_FETCH` then prevents the configured upload-pack from running (RY1).
  * No route to accepting a *hidden-rejection* construction was found this way: `fsck.skipList` does not mask hash
    mismatches.
* **Correction:** list with includes and all repository scopes (e.g. `config --includes --show-scope --name-only
  --list` under the isolation, plus `--worktree`), or refuse any `include.*`, `includeif.*` or
  `extensions.worktreeconfig` key. Add a test.

**M4 — MINOR — Harness: four claimed elements of the repair are unpinned; RV39's two-edit bundle hides one of them.**
* RY1: `GIT_NO_LAZY_FETCH` removed alone. **SURVIVED**. Outcome: the configured upload-pack ran (false → true).
* RY3: `_ordered`'s regular-file check removed. **SURVIVED**. Outcome: a symlink (mode 120000) whose target text is the
  attestation JSON goes from refused to **ACCEPTED**. The supplement states "only regular files count".
* RY2: `--strict` dropped. **SURVIVED**. A legitimate zero-padded-mode history goes from refused to accepted (benign
  direction).
* RY5: an unreadable config listing counts as clean. **SURVIVED**. Under fault injection (the config read fails),
  refused becomes ACCEPTED.
* **Correction:** split RV39, or add a mutant of `GIT_NO_LAZY_FETCH` alone with a witness whose keys are hidden (M3).
  Add direct tests for a symlink attestation, an unreadable config listing and (if `--strict` is meant) a
  strict-only warning. Register them.

**M5 — NOTE — Legitimate repositories newly refused, not stated in supplement §2.**
* All fail-closed, and all accepted at 2275b3a0:
  * `--strict` promotes every fsck warning to an error (zero-padded tree modes, which old git histories contain);
  * any fsck error in old history (e.g. `badTimezone`) refuses;
  * fsck also checks the index (and other worktrees, reflogs), so uncommitted working state refuses: an index entry
    whose object is missing gave rc 2;
  * the attestation path spelling `./att/HOST.json` now refuses.
* **Correction:** list them in §2 and in the D-HOST-LIFETIME procedure. Consider running fsck on objects only, or in a
  scratch index.

**M6 — MINOR — Ledger 495 binds a scratch file that is not committed.**
* `reviews/scratch_REVIEW_REVIEW64_REPAIR/job_116337943534.log` (`fed307d6…`) is absent at b0b73adb and at 774f2183.
  The `scratchpad/review65` original has exactly that hash. The line's omission statement does not name it.
* **Correction:** commit it (it is a job log of synthetic output), or append a correction line naming it as
  bound-but-omitted and why.

**M7 — NOTE — Minor record and wording imprecisions.**
* Supplement L6 says `GIT_NO_LAZY_FETCH` is honoured by "git 2.44 and later"; the local 2.43.0 (Ubuntu) honours it.
* Ledger 496 omits run 38725820509's artifact id and digest (11969136626, `3be305c4eb97…`).
* `run_mutants.py:1132` labels RV31–RV42 "Claude review 63".
* The test docstring of `test_review65_partial_clone_runs_no_configured_command` overstates (Q5 item 4).
* **Correction:** wording only.

**Counts:** BLOCKING 0 · MAJOR 2 (M1, M2) · MINOR 3 (M3, M4, M6) · NOTE 2 (M5, M7); 7 new findings.

---

## 6. Reproduction and scratch files

* Suites: `suite_python3.11.txt`, `suite_python3.12.txt`, `suite_python3.13.txt` (215 OK each).
* New probes:
  * `probes66.py.txt`, with outputs `probes66_out.json` (base), `probes66_out_commitgraph_off.json` and
    `probes66_out_fsmonitor_off.json` (isolation controls) and `probes66_at_2275b3a0_out.json` (comparison);
  * `probes66b.py.txt`, with outputs `probes66b_out.json`, `probes66b_out_commitgraph_off.json` and
    `probes66b_out_fsmonitor_off.json`.
* Re-runs of review 65's and 64's probes: `rerun65/*_at_774f2183_out.json`, `rerun65/q01chk_at_774f2183_out.json`;
  comparison `compare66.py.txt`.
* Mutants (registered RV30–RV42 and Q01 singly, plus RY1–RY5): `reviewer66_mutants.py.txt`,
  `reviewer66_mutants_result.json`, `reviewer66_mutants_stdout.txt`.
* Records: `check_records66.py.txt`, `check_records66_out.json`; `ledger_new_lines.jsonl` (ledger 494–499 as read).

---

## 7. Reviewer mutants (brief 66)

**Method:**
* Each mutant is a copy of the 774f2183 `lx_platform.py` under `scratch/tmp`.
* The pinned 215-test suite runs through the harness's own `run_suite` (`LX_PLATFORM_DIR`, `PYTHONWARNINGS=error`).
* Each mutant is classified by the harness's `classify_mutant` against a fresh PASS baseline (215 tests), with the
  witnesses named below.
* An outcome check runs base and mutant on one synthetic construction, each in a child interpreter.

**Result: 5 new mutants, 1 killed, 4 survived.**

```
### RY1 SURVIVED | GIT_NO_LAZY_FETCH dropped alone (RV39's second edit by itself)
###   blob:none clone, promisor keys in an include.path file: base refused, upload-pack NOT run ->
###   mutant refused (HISTORICAL), configured upload-pack RAN
-               GIT_GRAFT_FILE=os.devnull, GIT_NO_LAZY_FETCH="1")
+               GIT_GRAFT_FILE=os.devnull)
    witnesses: test_review65_partial_clone_runs_no_configured_command

### RY2 SURVIVED | fsck without --strict
###   legitimate history with a zero-padded tree mode: refused -> ACCEPTED
-    return _git(repo_root, "fsck", "--full", "--strict", "--no-dangling", "--no-progress") is not None
+    return _git(repo_root, "fsck", "--full", "--no-dangling", "--no-progress") is not None
    witnesses: test_review65_forged_graph_and_rewritten_object_refuse

### RY3 SURVIVED | _ordered takes the blob id of any exact-path entry (regular-file check dropped)
###   attestation committed as a symlink (120000) whose target text is the attestation JSON: refused -> ACCEPTED
-    blob = entry[2] if entry and entry[:2] in (("100644", "blob"), ("100755", "blob")) else ""
+    blob = entry[2] if entry else ""
    witnesses: test_review65_range_like_attestation_path_and_deep_json, test_review64_symlink_is_not_an_accepting_review

### RY4 KILLED | fsck --connectivity-only instead of a full strict fsck
###   rewritten rejection blob: refused -> ACCEPTED; killed by test_review65_forged_graph_and_rewritten_object_refuse
-    return _git(repo_root, "fsck", "--full", "--strict", "--no-dangling", "--no-progress") is not None
+    return _git(repo_root, "fsck", "--connectivity-only", "--no-dangling", "--no-progress") is not None

### RY5 SURVIVED | an unreadable local-configuration listing counts as clean
###   fault injection (the config listing fails): refused -> ACCEPTED
-    if names is None or any(_LOCAL_CONFIG_REFUSED.match(n)
+    if names is not None and any(_LOCAL_CONFIG_REFUSED.match(n)
    witnesses: test_review65_local_fsck_or_promisor_configuration_refuses
```

For each survivor, the suite returned 0 with 215 tests. RY4's only failing method was its witness.

Registered mutants re-run singly in the same session (not reviewer mutants), each against the same baseline:
* Q01, RV30–RV42: all **KILLED**.
* RV30–RV38 and RV40–RV42: the only failing method is the registered witness.
* RV39: its witness plus RV32's witness.
* Q01: the five methods recorded before.
