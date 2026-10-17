# Review: the coordinator's repairs of review 70's findings (combined Cell-308 development source, Cloud route r1, S4 changed branch)

* Reviewer: **reviewREVIEW70_REPAIR (fresh agent, brief 71)**
* Date: 2026-10-16 (UTC), about 03:00Z to 03:25Z.
* Pinned commit: **`cc02b9b7d5cb0564bbbf7c67e15e8d4c818908b0`** (branch `codex/cell308-claude-r5-integration`, draft PR
  flaggielover/ReBaseGuard#3). Detached worktree `scratchpad/review71/tree_cc02b9b7`. `git status --porcelain` was
  empty after the suites, probes and mutant runs. I wrote nothing there.
* Delta: `9f223c91..cc02b9b7`, three commits:
  * 218e478a: brief 70;
  * 74badebc: review 70 recorded, repairs;
  * cc02b9b7: sharded local run on 74badebc and native run 38826606180 recorded.
* NS = `level4/closure_proofs/p5y_k5_cell308_research/`, DEV = `NS/streams/CLOUD_R1_LINUX_DEV`. Line numbers refer to
  the cc02b9b7 files.
* Scratch: `/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review71/` ("scratch").
  * Probes and mutants ran on `scratch/base/lx_platform.py`, sha256 `da32ce8c…`. This equals the cc02b9b7 / 74badebc
    blob and the binding in ledger line 528.
  * Scripts are stored as `*.py.txt`.
* Environment of my processes:
  * Every git, gpg and Python process I started ran with `HOME=scratch/home` and `GNUPGHOME=scratch/home/.gnupg`.
    `scratch/home` holds only the empty `.gnupg` directory.
  * Disclosure: the first suite run (`run_suites.sh`) did not set `TMPDIR`. Its self-cleaning `TemporaryDirectory`
    fixtures were therefore created and removed under `/tmp`. Every later run set `TMPDIR=scratch/tmp`, which I
    emptied at the end.
* Local git: **2.43.0** (Ubuntu). Native runner git: 2.55.0 (job log of run 38826606180).
* `new_target_evaluations = 0`. I ran nothing that evaluates a target: no cell, drift, certificate, decoy, science
  module, qualification case or candidate code. I installed nothing and changed no setting. I did not run the
  optional full `run_mutants.py`.

---

## 1. Exposure disclosure

**What I opened:**
* Brief 71 in the shared checkout. It is the only file I read there.
* In the pinned tree:
  * the `9f223c91..cc02b9b7` diffs of the five tested inputs, `BRIEF_INDEX.md` and the ledger;
  * `lx_platform.py` lines 1140–1635: git helpers, completeness, `_cat_file_batch`, `_tree_entry`, the walk, the
    history scan, `_acceptances`, `_ordered`, `attestation_valid` and `preflight`;
  * the review-70, review-69 and review-65 environment tests and the fixture helpers in `tests/test_lx_platform.py`;
  * from `run_mutants.py`: the new `MUTANTS` entries, `MUTANT_GROUP_SIZES`, `PROPERTY_WITNESSES`, `run_suite`,
    `classify_mutant`, `apply_mutation`, `validate_registry` and `main`;
  * the workflow diff and the workflow's count and timeout lines;
  * review 70 as recorded, supplements r69 and r70, and ledger lines 525–531;
  * the commit messages of the delta;
  * these committed review-70 scratch scripts, copied to `scratch/rerun/`: `cons70`, `forge_mid70`,
    `evil_merge_view70`, `probes69` and `probes68`. I also read their committed outputs, for comparison only;
  * `sharded_run.py.txt`;
  * `BRIEF_CHECK.json`: its keys, and whether it mentions briefs 17, 20, 69 and 70.
* The compressed record `LOCAL_SHARDED_HARNESS_PY312_74BADEBC.json.gz`, decompressed in memory: summary keys and all
  203 rows. It holds synthetic test output only.
* 74badebc's `run_mutants.py` and `lx_platform.py` (git objects), extracted under scratch tmp, to recompute the
  sharded rows.
* `scratchpad/review70/` originals: file names and bytes, for the byte comparison only.

**Name-level contact:**
* The scratchpad root listing shows sibling directory names such as `review59`…`review70`, `fix70`, `fix70_check`,
  `sharded` and `rv`. I opened none of them except `review70/` (Q4).
* `git diff --name-status 9f223c91..cc02b9b7` contains no audit, interruption, mb_r1, 309 or exposure-disclosure path.
* The `ledger/briefs/` file listing shows brief names (01–70). I opened only `BRIEF_INDEX.md` and the
  `BRIEF_CHECK.json` keys.

**Shared object store:** the pinned worktree's git directory lives in the shared repository, so every git read of the
pinned tree went through it (objects only):
* `git show <c>:<path>` of the bound files at 218e478a, 74badebc and cc02b9b7;
* `git log -1` of 9b6347cb;
* `git merge-base --is-ancestor` between run-era commits;
* `git log -- BRIEF_CHECK.json`.

All of these are HEAD-reachable (no `--all`). I ran no `fsck` and no git command in the shared checkout.

**GitHub (read-only, MCP):**
* the branch's run list (15 runs);
* the jobs and artifacts of run 38826606180;
* the last 45 lines of job 116735414165;
* the status of run 38843066536.

The log tail contains an artifact page URL, which I did not copy into any file.

**Live calls:** none against the real repository. Every one of these calls passed a synthetic repository under
`scratch/tmp` (or literal bytes), with `machine_identity` patched: `attestation_valid`, `_review_dir_is_a_directory`,
`_cat_file_batch` and `_tree_entry`.

**Not opened, grepped or read:**
* `NS/audit/EXECUTION_INTERRUPTION_ASSESSMENT*`, `NS/audit/INCIDENT_AUDIT*` and `NS/reviews/REVIEW_EXECUTION_INTERRUPTION*`;
* anything under `p5y_k5_cell308_mb_r1/postexec/`, and any MB r1 target-run or qualification record;
* `NS/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`;
* any Cell-309 branch, file or record;
* candidate source;
* the tail-figure pattern source named in `BRIEF_CHECK.json`.

My credential scan (Q4) read only files added or modified in the delta.

**No accidental contact.** The only side effect outside scratch is the `/tmp` fixture directories of the first suite
run, which the suite itself created and removed.

---

## 2. Verdicts

REPAIR: REPAIRED
HARNESS: SOUND_WITH_DEFECTS
RECORDS: ACCURATE_WITH_CORRECTIONS

**No verdict here accepts any amendment, supplement, addendum, erratum, host or decision.** This is a bounded
development-layer review. Supplements r64–r70, erratum E1, the L-DET addendum and every D-* decision stay PROPOSED or
undecided. Only the formal route review, a fresh S12 re-rating and the owner can accept, reject or put anything into
force.

* **REPAIR = REPAIRED.**
  * Each of T1–T7 is disposed as the supplement says, and the code at cc02b9b7 matches: the duplicate refusal in
    `_tree_entry`, the docstrings, the six new mutants, and the subtests that kill them.
  * No review-68, review-69 or review-70 probe regressed. The only outcome-level change is the intended one (T5).
  * The defects I found are in the harness (U1–U3), not in the repairs' claims.
* **HARNESS = SOUND_WITH_DEFECTS.**
  * RV64 and RV66–RV70 are genuine direct witnesses: each is killed only by its own subtest or assertion, and each
    changes the outcome on a synthetic repository. RV65 is killed indirectly, as stated.
  * The counts 203/204 are right. The sharded run is a faithful use of the 74badebc registry and `classify_mutant`.
  * Gaps:
    * a root commit's own tree is unpinned, a fail-open survivor (U1);
    * same-mode duplicates and the walk's use of a malformed answer are unpinned (U2);
    * there is no positive control for prefix-sharing siblings (U3);
    * the sharded record is weaker evidence than the harness's own record (U4).
* **RECORDS = ACCURATE_WITH_CORRECTIONS.**
  * All 108 binding checks of ledger lines 525–531 recompute. The gz record gunzips to its digest. Review 70 and its
    38 scratch files are byte-identical to the originals. No credential or signed URL.
  * Every native run since 9b6347cb on the branch is recorded, except the in-progress run on cc02b9b7 itself.
  * Corrections:
    * the sharded record's interpreter is asserted, and whether the run was resumed is not recorded (U4);
    * the native run on cc02b9b7 is pending, and no native run exists on 74badebc (U5);
    * the brief-index "0 hits" claim is unrecorded (U6).

---

## 3. Review 70's findings (Q1)

| finding (review 70) | disposition (supplement r70) | verified at cc02b9b7 | status |
|---|---|---|---|
| T1 MINOR: RB5 / RB6 stated equivalent; neither is | Withdrawn. RC1 = RV64 (`review_dir_regular_file` subtest); RC2 = RV65, killed indirectly; no direct forged-object witness | Withdrawn in three places: supplement r70 header and §1, ledger 527 `withdrawn[0]`, and the review-69 test docstring (`:1682`). Ledger 522 and supplement r69 are not edited (append-only). **RV64** KILLED singly, failing only `test_review70_… (case='review_dir_regular_file')`. Outcome (cons70 `leaf_regular_file`): base refused, RV64 **ACCEPTED**. **RV65** KILLED singly, failing only `test_review65_caller_git_environment_is_ignored` (reason text: UNAVAILABLE instead of HISTORICAL). Outcome (re-run of `forge_mid70`, which forges a non-root tree via a caller `GIT_OBJECT_DIRECTORY` plus alternates): base refused, RV65 **ACCEPTED** (`diag/forge_mid_*_out.txt`). The indirect kill is stated. It is fragile: an edit of that test's reason assertion would lose it. | **RESOLVED** (RV65 indirect: STATED, acceptable to carry) |
| T2 MINOR: merge commits' own trees unpinned | `evil_merge` subtest; RC3 = RV66 | **RV66** KILLED singly, failing only `(case='evil_merge')`. Outcome (cons70 `evil_merge_ancestor_symlink`): base refused, RV66 ACCEPTED. The subtest's merge carries `level4 -> alt` only in its own tree, and the history scan does not list it. Only the walk refuses it, and RV66 survives every other test. | **RESOLVED** |
| T3 NOTE: sha256 width and odd directory modes unpinned | sha256 positive control (RC5 = RV67); `odd_dir_mode` 40755 subtest (RC4 = RV68) | **RV67** KILLED by the sha256 test only. Outcome (`sha256_control`): base ACCEPTED, RV67 refused. **RV68** KILLED, failing only `(case='odd_dir_mode')`. Outcome (`40755`): base refused, RV68 ACCEPTED. The subtest's `40755` tree is written `--literally`; strict fsck reports INFO only, so the walk is what refuses it. | **RESOLVED** |
| T4 NOTE: S4 and the walk's integrity assumptions unpinned and unstated | direct `_cat_file_batch` missing test (RC7 = RV70); reliance on fsck and isolation stated; helper exception clause unmutated (stated) | `:1786–1788` asserts None for a missing id (64 zeros, sha256 repository), with and without contents, and a `tree` answer for `HEAD^{tree}`. **RV70** KILLED by that test only. Docstring `:1283–1284` and r70 §2 "Integrity" state the reliance. The helper's own exception clause has no mutant; this is stated in the r70 §1 T4 row only. | **RESOLVED** (exception clause: STATED) |
| T5 NOTE: `_tree_entry` takes the last of duplicate entries | refuse on a second match; direct byte test; RV69 | `:1269–1271`: a second entry with the same name returns False. **RV69** KILLED by the direct assertion `:1790`. Re-run of cons70 `duplicate_entry_symlink_then_dir`: `dir_check` True → **False**, `_tree_entry` → `False`; strict fsck still refuses first (`duplicateEntries`, error class). Pinned only for a duplicate whose two modes differ, and only on raw bytes (U2). | **RESOLVED** (pinning gap: U2) |
| T6 NOTE: §2's checkout alternative incomplete | alternative withdrawn; tree paths and blob contents only | r70 §2 "Checkout" replaces the sentence. The procedure must read git tree paths and blob contents only, never a checkout. The listed differences are illustrative, and no longer a sufficiency condition, so their completeness no longer matters. | **RESOLVED** |
| T7 NOTE: native run on 9f223c91 pending | recorded by its own ledger line | Ledger 529 matches the API and job log: run 38826606180, head 9f223c91, success; SUMMARY `PASS / 227 / 196 / 196 / pass / inputs_unchanged / full_registry_completed`; artifact 12016729252; digest `sha256:434a5da9…`; runner git 2.55.0. | **RESOLVED** (same residue recurs at cc02b9b7: U5) |

**Supplement r70 §2, with the standing parts of r69 §2: accurate. One wording nuance.**
* "Walk scope" is true:
  * `rev-list HEAD` lists merges and roots;
  * the loop covers the review directory's own name (`enumerate(parts)`);
  * RV64 and RV66 show both properties change outcomes.
* "Integrity" is true, and also covers the history scan: `ls-tree` and `cat-file blob` do not verify hashes either.
* "Duplicate tree entries … `_tree_entry` also treats them as malformed" is true only for the walk's looked-up
  component names. A duplicate of any other name is refused by fsck alone; my probe `duplicate_unrelated_name` gives
  `dir_check` True and fsck rc 1. This is a wording nuance, not a defect.
* "Performance" matches review 70's figures.
* r69 §2's standing parts are unchanged and still describe the code:
  * the completeness items 1–3;
  * the scan bullets;
  * the isolation list;
  * the not-refused case/Unicode list;
  * the list of legitimate repositories that are refused.
* Two cases that are not named but are correct: a `--depth N` clone whose N covers the whole history is not shallow
  (git writes no `shallow` file) and is ACCEPTED; a full `--no-local` or `--bare` clone is ACCEPTED (§4 Q2).

---

## 4. Answers Q2–Q5

### Q2 — Adversarial fail-closed audit

**Suites:** `python3.1x -B -m unittest discover -s tests -v` → **229 tests OK** on 3.11, 3.12 and 3.13 (`suites/`,
`rc.txt` all 0). The harness baseline (`run_suite`, `PYTHONWARNINGS=error`) is 229 PASS and equals the static count.

**Review 68, 69 and 70 probes re-run unchanged** (`rerun/`; comparison `rerun/cmp_out.txt`, script `cmp_probes71.py.txt`):
* All three stdouts are byte-identical to review 70's committed stdouts.
* After normalising object ids and temp names:
  * probes68: identical.
  * probes69: one key differs only in the interleaving of fsck's stderr (hint lines vs the `badFilemode` warning);
    outcomes are identical.
  * cons70: only `duplicate_entry_symlink_then_dir` changed (`dir_check` True→False, `_tree_entry` direct → False),
    which is the T5 repair. The attestation outcome is unchanged.
* So every construction review 70 listed is unchanged at cc02b9b7, including the 30 000 / 150 000-commit timings and
  the configured-command sweep (no command ran).

**New probes** (`probes71.py.txt` → `probes71/`):

| construction | walk | outcome | note |
|---|---|---|---|
| **root commit** holds `level4 -> alt` and `alt/…/reviews/veto.md` (`<sha> REJECTED`); next commit removes both and adds the attestation | False | refused | fsck rc 0; the history scan lists 1 commit (the acceptance); a checkout of the root shows `veto.md` at the review path. Only the walk refuses it, and that is unpinned (U1, RD1) |
| same, as an **orphan root** merged `-s ours --allow-unrelated-histories` | False | refused | the checkout of the orphan root shows the veto; same reliance |
| duplicate `40000 level4` twice (bad tree first, good last) | False | refused by fsck (`duplicateEntries`) | under RD2 / RD3 the walk returns True; fsck still refuses |
| duplicate at the review directory name (`100644` blob + `40000` tree) | False | refused by fsck | |
| duplicate of an unrelated name (`zz` twice) | True | refused by fsck | `_tree_entry` only refuses the looked-up name |
| siblings `level4x`, `level4.orig`, `level4/closure_proofs-old` (symlinks), `<review dir>-archive` (file); the review directory removed and re-created | True | ACCEPTED | not over-refused; no such control in the suite (U3, RD5) |
| merge history: origin; `clone` (local); `--no-local`; `--bare`; `--depth 100` (covers the whole history); sha256 merge origin | True | ACCEPTED (all) | legitimate full clones are not newly refused |
| `--depth 1` clone | — | refused (shallow) | stated |
| `_tree_entry` edges: empty, single, same-mode duplicate, duplicate followed by a truncated entry, duplicate of another name, prefix names, name with a space, empty name, no space, NUL in mode | — | None / entry / **False** / False / entry / exact match / exact match / None / False / entry with odd mode (the walk then refuses) | no exception |
| `_cat_file_batch` edges: the same name twice; a commit name; a name containing a newline; 5000 names | — | 2 answers / `commit` / **None** / 5000 | no exception; the newline case relies on the final `pos == len(out)` check (RD7) |

**Classes:**
* **ACCEPTED where the stated rule refuses:** none in the base. Every construction stated as refused is refused.
  * The duplicate refusal is now in `_tree_entry` as well as fsck.
  * The root-commit case is refused, but no test pins it (U1).
* **Repository-configured command run:** none (review 70's sweep re-run unchanged).
* **Exception escaping `attestation_valid` / preflight:** none found.
  * The new branch in `_tree_entry` returns before any slice is used.
  * `ids[0]` in the walk is reached only when `rev-list HEAD` printed at least one id; git does not print a
    whitespace-only answer with exit 0. Unchanged from 9f223c91.
* **Legitimate full-clone case newly refused and not stated:** none. A repository with a duplicate name is already
  refused by strict fsck, so the T5 change refuses nothing new.
* **Regression from 9f223c91:** none.

**Mutants:** 7 new (RD1–RD7): **2 KILLED** (RD4, RD6), **5 SURVIVED**:
* RD1 with a fail-open outcome change;
* RD5 with a fail-closed (over-refusal) outcome change;
* RD2, RD3 and RD7 equivalent under strict fsck or hex-only names.

Details in §7.

### Q3 — Harness integrity

* **RV64–RV70 re-run singly** (`mut71/`), against a fresh 229 PASS baseline under the harness's `run_suite` /
  `classify_mutant`. Each row: KILLED, 229 ran, rc 1, no errors, failed methods ⊆ its registered witnesses.
  * The shared method `test_review70_review_dir_file_evil_merge_and_odd_mode_refuse` witnesses three mutants. At
    **subtest** level each one fails exactly its intended case: RV64 → `review_dir_regular_file`, RV66 →
    `evil_merge`, RV68 → `odd_dir_mode`. `classify_mutant` checks methods only, so the shared method alone would not
    show this; the subtest split confirms it.
  * RV67, RV69 and RV70 fail only `test_review70_sha256_repository_and_walk_parsing`. Each is pinned by a distinct
    assertion (`:1785`, `:1790`, `:1786`).
  * Outcome changes on synthetic repositories: RV64, RV66, RV68 refused → ACCEPTED; RV67 ACCEPTED → refused; RV69
    `dir_check` False → True (fsck still refuses); RV65 refused → ACCEPTED under a caller object directory. RV70 is
    equivalent under fsck and the isolation, pinned directly on the helper.
  * **Genuine: yes.** RV65 is indirect, as stated (see T1).
* **Previously registered, re-run singly:** RV40, RV60, RV61, RV62, RV63 and CDEX15 are all KILLED.
  * RV61, RV62 and RV63 fail only their own subtests.
  * RV60 also fails all three review-70 subtests.
  * RV40 also fails `caller_git_dir`.
* **Counts:**
  * `MUTANT_GROUP_SIZES` sums to 32+10+9+14+9+15+11+13+16+4+70 = **203**.
  * `validate_registry()` returns 203, and `test_mutation_harness` asserts 203.
  * The workflow asserts `== 203` and `len(suites) == 204` (203 + baseline), and takes `expected_test_count` (229)
    from the record.
  * All new anchors occur exactly once. **Right.**
  * The workflow's `timeout-minutes: 90` leaves margin: run 38826606180 took 44 min for 196 mutants.
* **Sharded run** (`q3/check_sharded71.py.txt` → `q3/check_sharded71_out.json`, 0 problems):
  * It uses the harness's own module (`import run_mutants as R`), with `R.MUTANTS`, `R.apply_mutation`,
    `R.run_suite`, `R.classify_mutant` and `R.PROPERTY_WITNESSES`, against a persisted baseline. Its environment
    matches `main()` (`LX_PLATFORM_DIR` popped; `PYTHONDONTWRITEBYTECODE`, `PYTHONWARNINGS=error`, `PYTHONHASHSEED=0`).
  * **Consistent with 74badebc:**
    * 203 rows in registry order;
    * every `mutated_lx_platform_sha256` recomputes from 74badebc's `lx_platform.py` plus that row's edits;
    * every property text and witness list equals the 74badebc registry;
    * anchor counts are all 1;
    * every row is KILLED with `reasons` [], `ran` 229 and rc 1, and has a witness among its failed methods;
    * `inputs_before` = `inputs_after` = the 74badebc blobs = the cc02b9b7 blobs (10 inputs);
    * baseline 229 = static 229.
  * **Differences from `main()`, not all stated (U4):**
    * There is no `BASELINE_COUNT_DIFFERS_FROM_STATIC_TEST_METHODS` check; I verified baseline = static here.
    * There is no source-hash-vs-snapshot check; the mutated-hash recomputation covers it.
    * Rows keep only `failed_methods`: no raw stdout/stderr, failure names or executed ids. A row cannot be
      re-classified from the record.
    * No interpreter or kernel is recorded.
    * The baseline's own timestamp is not copied into the summary.
    * Three suites run concurrently (thread pool).
    * A resumed run reuses `_baseline.json` and finished rows. Whether this run was resumed is not recorded.
  * **Faithful use of the classification: yes.** It is evidence of a lower grade than the harness's record; ledger
    531 states that it is "NOT the harness's single-process evidence run".

### Q4 — Records

* **Ledger:** 9f223c91 (524 lines) → 218e478a (525) → 74badebc (528) → cc02b9b7 (531). Each is a byte prefix of the
  next (checked for 524 → 531).
* **Bindings** (`records/check_records71.py.txt` → `records/check_records71_out.json`): **108 checks, 0 problems.**
  Each binding was checked at its introducing commit and at cc02b9b7:
  * brief 70 `1716c91a…`;
  * review 70 `72269778…` and its 38 scratch files;
  * the 10 inputs of 74badebc (`lx_platform.py` `da32ce8c…`, …);
  * supplement r70 `4e0bde22…`;
  * the gz `8bae4162…`, which gunzips to `d85b52c8…` = `uncompressed_sha256`;
  * the runner `dbd40466…`.

  The gz header has mtime 0, flags 0, XFL 2, OS 3, consistent with `gzip -9 -n`. Commit blobs: see Q3.
* **Review 70 and scratch:** `REVIEW_REVIEW69_REPAIR_DELTA.md` and all 38 committed scratch files are
  **byte-identical** to the `scratchpad/review70` originals. Two of them are `.py` originals committed as `.py.txt`:
  `base/lx_platform.py` and `q3/old/lx_platform.py`, identical in bytes. The only original files not committed are
  under `tree_9f223c91/` (the worktree). `home/` and `tmp/` hold no files. This is consistent with ledger 526's
  omission statement.
* **Signed URLs / credentials** (`records/scan71.py.txt` → `scan71_out.json`): I scanned all 50 added or modified
  files, with the gz decompressed and the ledger's new lines only.
  * Pattern hits are only the scanner pattern text inside the review-69/70 record checkers and their output.
  * The URLs are the `https://example.invalid/s` placeholder (8) and the `Claude-Session` URL (2).
  * **No signed URL, no credential.**
* **Modified files:** 43 A, 7 M. The 7 M are:
  * the 5 tested inputs;
  * the ledger (append-only);
  * `BRIEF_INDEX.md` (one row added at the end of the table).

  No reviewed or historical review, governance, audit or brief file changed. Supplement r69 is not edited.
* **Native runs since 9b6347cb** (API, 15 branch runs): every run from 38680983939 to 38826606180 appears in the
  ledger (lines 480–529).
  * **38843066536** (cc02b9b7, created 02:57:23Z) was `in_progress` at 03:16Z. It cannot be in the commit it tests
    (U5).
  * No run exists on 218e478a or 74badebc: both were pushed together with cc02b9b7. This is consistent with ledger
    528's "native_validation: after push" and ledger 531's "PENDING (this push)".
* **Interrupted local runs** (ledger 530): stated as two single-process runs with no output and no result, "neither a
  pass nor a failure". Accurate as a statement of non-evidence. Their timing (~00:32–02:00Z and ~02:06–02:26Z) is
  coordinator-asserted; I found no artifact of them and did not open the coordinator's scratch.

### Q5 — Overstatement

1. **Ledger 531 `"python": "CPython 3.12.3"` and the record name `…_PY312_…`.** The sharded runner records no
   interpreter or kernel (unlike `main()`), so this is coordinator-asserted, not evidenced (U4).
2. **cc02b9b7 message and ledger 531, "203 KILLED … inputs equal to 74badebc's blobs and unchanged".** Verified; this
   is not overstated. But "203/203" in the commit title rests on a record without raw reports, and the resumed or
   uninterrupted status of the sharded run is unstated (U4).
3. **Ledger 528 `local_full_harness`: "to run on these committed inputs before push".** This did not happen as a
   single-process full run (ledger 530). The successor line 531 states the substitute, so this is not misleading
   after 531.
4. **BRIEF_INDEX row 70, "tail-figure scan: 0 hits".** The index says the check is recorded in `BRIEF_CHECK.json`,
   which has not changed since 8da57f89 and names no brief after 17. Unrecorded; UNVERIFIED here (U6). This is a
   pre-existing pattern for rows after 17.
5. **Supplement r70 §2, "`_tree_entry` also treats them as malformed".** True only for the walk's component names
   (see §3). A nuance.
6. **Not overstated:**
   * the T1–T7 code claims (74badebc message, ledger 528 `repairs`, docstrings);
   * "229 OK on 3.11/3.12/3.13" (reproduced);
   * "CDEX15, RV40, RV60–RV70 KILLED under classify_mutant" (reproduced singly);
   * "RV65 killed indirectly" (reproduced);
   * ledger 529's run facts (API and log).

---

## 5. New findings

**U1 — MINOR — Harness: a root commit's own tree is not pinned. The walk's refusal of a root-only ancestor symlink
survives its removal.**
* **Location:** `_review_dir_is_a_directory` `:1287` (`rev-list HEAD`); `tests/test_lx_platform.py`, review-68/69/70
  walk tests. Every fixture's root commit holds only `att/HOST.json`.
* **Evidence:**
  * RD1 (`rev-list --min-parents=1 HEAD`: the root commit is skipped) **SURVIVES**: 229 pass, rc 0.
  * Construction `root_commit_ancestor_symlink`. The root commit holds `level4 -> alt` and `alt/…/reviews/veto.md`
    containing `<sha> REJECTED`. The next commit deletes both and adds the attestation, then the acceptance follows.
  * fsck rc 0. The history scan lists only the acceptance commit. A checkout of the root shows `veto.md` (vetoing) at
    the review path.
  * Base refuses (walk False); RD1 **ACCEPTS**. The orphan-root variant (an unrelated root merged `-s ours`) is the
    same.
  * RD6 (walk limited to the history scan's commits) is KILLED, but only through non-root cases.
* **Scope:** not a base fail-open. It is the same class as review 70 T2 (merges): a stated walk scope ("every commit
  of HEAD's history") with no witness for one of its commit classes.
* **Correction:** add a `root_commit` subtest (and an orphan-root subtest) to
  `test_review70_review_dir_file_evil_merge_and_odd_mode_refuse` or a new test. Register RD1.

**U2 — NOTE — The T5 repair is pinned only on raw bytes, for a duplicate whose modes differ. The walk's use of a
malformed answer is unpinned.**
* **Evidence:** both of these SURVIVE, and are equivalent while strict fsck (`duplicateEntries`, error class) runs
  first:
  * RD2: a duplicate is refused only when the two modes differ, so for same-mode duplicates the last one wins.
    Probe: walk True instead of False.
  * RD3: the walk reads `_tree_entry`'s False as "absent".
* RD4 (keep the first occurrence) is KILLED.
* **Correction:** add a same-mode duplicate to the direct `_tree_entry` assertion. Add a direct
  `_review_dir_is_a_directory` call on a duplicate-tree repository (fsck is not consulted by the walk itself), or
  state RD2 / RD3 as equivalent under fsck.

**U3 — NOTE — No positive control for siblings that share a prefix with a component. Over-refusal would go
unnoticed.**
* **Evidence:**
  * RD5 (`_tree_entry` matches any name that starts with the component) SURVIVES.
  * It refuses a legitimate repository with `level4x` / `level4.orig` symlinks beside the real `level4` directory:
    base ACCEPTED, RD5 refused. The T5 duplicate check turns every such prefix match into a refusal.
  * Review 70's `sibling_gitlinks_control` and `names_with_spaces_control` are probes, not tests.
* **Correction:** add a sibling-name positive control (`level4x` symlink, `<review dir>-archive` file,
  `<review dir> old`) and register RD5.

**U4 — NOTE — The sharded record is weaker evidence than the harness's record, and two of its facts are asserted.**
* **Location:** ledger 531; `reviews/scratch_REVIEW63_REPAIR_20261015/sharded_run.py.txt` and its record.
* **Evidence:**
  * Rows keep `failed_methods` only: no raw stdout/stderr, failure names, executed ids or invalid-reason detail. The
    harness module itself says "Every complete raw report … is retained".
  * The record has no interpreter, kernel or baseline timestamp. Ledger 531's `CPython 3.12.3` and the `PY312` name
    are asserted.
  * The runner is resumable (persisted baseline and rows). Whether this run was resumed across a restart is not
    recorded.
  * Three suites ran concurrently.
  * The classification itself is faithful (Q3).
* **Correction:** state these limits in a successor ledger line. Do not treat the sharded record as the single-process
  evidence; the native run 38843066536, or a later complete local `main()` run, is that evidence.

**U5 — NOTE — Records residue.**
* Native run **38843066536** on cc02b9b7 was `in_progress` at review time (UNVERIFIED). It is the first native run on
  the review-70 repairs: no run exists on 74badebc or 218e478a.
* **Correction:** append its line with the job-log SUMMARY (expected `229 / 203 / 203 / pass`), the artifact id and
  digest, and the runner git.

**U6 — NOTE — BRIEF_INDEX row 70's "tail-figure scan: 0 hits" is not recorded where the index says.**
* `BRIEF_CHECK.json` is unchanged since 8da57f89 and names no brief after 17. Rows after 17 share this pattern
  (pre-existing).
* UNVERIFIED: I did not open the pattern source.
* **Correction:** record the per-brief scan result in `BRIEF_CHECK.json` or a successor file, or reword the index
  column as coordinator-asserted.

**Counts:** BLOCKING 0 · MAJOR 0 · MINOR 1 (U1) · NOTE 5 (U2–U6); 6 new findings.

---

## 6. Reproduction and scratch files

* Suites: `run_suites.sh`, `suites/suite_python3.11.txt`, `suite_python3.12.txt`, `suite_python3.13.txt`,
  `suites/rc.txt`.
* Re-runs:
  * `rerun/` holds copies of `probes68.py.txt`, `probes69.py.txt`, `cons70.py.txt`, `forge_mid70.py.txt` and
    `evil_merge_view70.py.txt`;
  * outputs `rerun/*_at_cc02b9b7_out.json`, `*_stdout.txt` and `*_err.txt` (empty);
  * the comparison script `cmp_probes71.py.txt` and its output `rerun/cmp_out.txt`.
* New probes: `probes71.py.txt` → `probes71/probes71_out.json`, `probes71_stdout.txt`, `probes71_err.txt` (empty).
* Mutants: `reviewer71_mutants.py.txt` → `mut71/reviewer71_mutants_result.json`, `_stdout.txt`, `_err.txt` (empty).
* RV65 outcome: `diag/forge_mid_base_out.txt`, `diag/forge_mid_RV65_out.txt` and `diag/RV65_lx_platform.py.txt`.
* Harness record check: `q3/check_sharded71.py.txt` → `q3/check_sharded71_out.json`.
* Records: `records/check_records71.py.txt` → `records/check_records71_out.json`; `records/scan71.py.txt` →
  `records/scan71_out.json`.
* Base copy: `base/lx_platform.py` (`da32ce8c…`).

---

## 7. Reviewer mutants (brief 71)

**Method:**
* Each mutant is a copy of the cc02b9b7 `lx_platform.py` under `scratch/tmp`.
* The pinned 229-test suite runs through the harness's own `run_suite` (`LX_PLATFORM_DIR`, `PYTHONWARNINGS=error`).
* Each mutant is classified with the harness's `classify_mutant` against a fresh PASS baseline (229).
* Witnesses are the review-68/69/70 walk tests, or the review-70 parsing test for parser-only mutants.
* The outcome check runs base and mutant on one `probes71` construction, each in a child interpreter.
* Every row ran 229 tests with the baseline's executed ids and no errors.

**Result: 7 new mutants, 2 killed, 5 survived.** RD1 survives with a fail-open outcome change and RD5 with an
over-refusal; RD2, RD3 and RD7 are equivalent under strict fsck or hex-only names.

```
### RD1 SURVIVED | root commits' own trees are skipped by the walk
###   root_commit_ancestor_symlink: base refused (walk False) -> mutant ACCEPTED (walk True)        [U1]
-    commits = _git(repo_root, "rev-list", "HEAD")
+    commits = _git(repo_root, "rev-list", "--min-parents=1", "HEAD")

### RD2 SURVIVED (equivalent under strict fsck) | duplicates refused only when the modes differ
###   duplicate_same_mode_bad_first: walk False -> True; attestation refused by fsck in both          [U2]
-            if found is not None:
+            if found is not None and found[0] != data[pos:sp]:
                 return False

### RD3 SURVIVED (equivalent under strict fsck) | the walk reads a malformed tree as "entry absent"
###   duplicate_same_mode_bad_first: walk False -> True; attestation refused by fsck in both          [U2]
-            if entry is False:
-                return False
-            if entry is None:
+            if entry is False or entry is None:
                 continue

### RD4 KILLED | _tree_entry keeps the FIRST of duplicate entries
###   failed only test_review70_sha256_repository_and_walk_parsing
             if found is not None:
-                return False
+                pos = nul + 1 + width
+                continue

### RD5 SURVIVED (over-refusal) | _tree_entry matches names that START WITH the component
###   prefix_sibling_controls (level4x, level4.orig symlinks): base ACCEPTED -> mutant refused        [U3]
-        if data[sp + 1:nul] == name:
+        if data[sp + 1:nul].startswith(name):

### RD6 KILLED | the walk covers only the commits the path-limited history scan lists
###   failed: review68 ancestor_symlink; review69 all six subtests; review70 evil_merge, odd_dir_mode
###   (root_commit_ancestor_symlink: base refused -> mutant ACCEPTED)
-    commits = _git(repo_root, "rev-list", "HEAD")
+    commits = _git(repo_root, "rev-list", "--full-history", "HEAD", "--", ACCEPTANCE_REVIEW_DIR)

### RD7 SURVIVED (equivalent: the walk's names are hex ids) | _cat_file_batch ignores trailing output
###   batch with a newline inside a name: base None -> mutant [1 answer, "commit"]
-    return answers if pos == len(out) else None
+    return answers
```

**Registered mutants re-run singly** (against the same baseline): RV64–RV70, RV40, RV60–RV63 and CDEX15 are all
**KILLED**. Subtest-level failures are in §4 Q3. Outcome checks: RV64, RV66, RV68 and RV65 (forged non-root tree)
change refused → ACCEPTED; RV67 changes ACCEPTED → refused; RV69 changes the walk from False to True under fsck.
