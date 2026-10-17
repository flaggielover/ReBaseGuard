# Review: the coordinator's repairs of review 68's findings (combined Cell-308 development source, Cloud route r1, S4 changed branch)

* Reviewer: **reviewREVIEW68_REPAIR (fresh agent, brief 69)**
* Date: 2026-10-15 (UTC), about 21:50Z to 22:20Z.
* Pinned commit: **`dad3c94876826b7e80975ea5083be91e81ba36a2`** (branch `codex/cell308-claude-r5-integration`, draft PR
  flaggielover/ReBaseGuard#3). Detached worktree `scratchpad/review69/tree_dad3c948`. `git status --porcelain` was
  empty after the suites and after the mutant runs. I wrote nothing there.
* Delta: `05caa00e..dad3c948`, four commits: 9250f473 (brief 68), 336bb0cb (review 68 recorded, repairs), bf5987a5
  (Q01 third edit; failed local run and native run 38783320859 recorded), dad3c948 (local full-run record on bf5987a5).
* NS = `level4/closure_proofs/p5y_k5_cell308_research/`, DEV = `NS/streams/CLOUD_R1_LINUX_DEV`. Line numbers refer to
  the dad3c948 files.
* Scratch: `/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review69/` ("scratch").
  * Probes and mutants ran on `scratch/base/lx_platform.py`, sha256 `bdca4aa0…`. This equals the dad3c948 blob and the
    bindings in ledger 514 and 517.
  * Scripts are stored as `*.py.txt`.
  * Every git, gpg and Python process I started ran with `HOME=scratch/home`, `GNUPGHOME=scratch/home/.gnupg` and
    `TMPDIR=scratch/tmp`. `scratch/home` holds only the empty `.gnupg` directory. `scratch/tmp` was emptied at the end;
    it had held 330 leftover `snapd/` and `units/` fixture directories from the suite's unit-file tests (inside scratch).
* Local git: **2.43.0** (Ubuntu). Native runner git: 2.55.0 (job log of run 38783320859).
* `new_target_evaluations = 0`. I ran no cell, drift, certificate, decoy, science module, qualification case or
  candidate code. I installed nothing and changed no setting.

---

## 1. Exposure disclosure

**Opened:**
* Brief 69 in the shared checkout. It is the only file I read there.
* In the pinned tree:
  * the `05caa00e..dad3c948` diffs of the five tested inputs, `BRIEF_INDEX.md` and the ledger;
  * `lx_platform.py` lines 1155–1500;
  * the changed tests and the K7 test in `tests/test_lx_platform.py`;
  * `run_mutants.py` (the changed `MUTANTS` entries, `PROPERTY_WITNESSES`, `classify_mutant`, `apply_mutation`);
  * the workflow (counts, timeout);
  * review 68 as recorded, supplement r68, ledger lines 511–518, and the delta's commit messages.
* Both compressed records, decompressed in memory: header, input hashes, counts, and every mutant row (edits,
  witnesses, suite failure names). They hold synthetic test output only.
* `scratchpad/review68/` originals, for the byte comparison, plus `probes68.py.txt` and `reviewer68_mutants.py.txt`. I
  copied both to `scratch/rerun68/`.

**Name-level contact:**
* the scratchpad root listing;
* the first eight entry names of `scratchpad/review68/tmp/` (temporary directory names). I opened nothing there.
* `git diff --name-only 05caa00e..dad3c948` contains no audit, interruption, mb_r1, 309 or exposure-disclosure path.

**Shared object store:** the pinned worktree's git dir lives in the shared repository, so every git read of the pinned
tree went through it (objects only). Beyond the diffs, I ran these git reads there:
* `git log HEAD --raw -- <review dir>` (modes only);
* `ls-tree -r <c> -- <review dir>` entry counts at the five delta commits;
* `rev-parse --is-shallow-repository`.

All are HEAD-reachable only (no `--all`, so no other branch). I ran no `fsck` and no git command in the shared checkout.

**GitHub (read-only, MCP):**
* the branch's run list;
* jobs and artifacts of run 38783320859;
* the last 45 lines of job 116588858110;
* the status of run 38812337420.

The log tail contains an artifact page URL, which I did not record.

**Live calls:** none against the real repository. Every `attestation_valid`, `_history_complete` and
`_review_dir_is_a_directory` call passed `repo_root=<synthetic repository under scratch/tmp>` with `machine_identity`
patched. `scratch/tmp` has no enclosing repository (`rev-parse` rc 128).

**Not opened, grepped or read:**
* `NS/audit/EXECUTION_INTERRUPTION_ASSESSMENT*`, `NS/audit/INCIDENT_AUDIT*`, `NS/reviews/REVIEW_EXECUTION_INTERRUPTION*`;
* anything under `p5y_k5_cell308_mb_r1/postexec/`, and any MB r1 target-run or qualification record;
* `NS/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`;
* any Cell-309 branch, file or record;
* candidate source.

**No accidental contact** beyond the name-level contact listed above. No side effect outside scratch: HOME and
GNUPGHOME were redirected, and every signature program was a scratch script.

---

## 2. Verdicts

REPAIR: REPAIRED_WITH_DEFECTS
HARNESS: SOUND_WITH_DEFECTS
RECORDS: ACCURATE_WITH_CORRECTIONS

**No verdict here accepts any amendment, supplement, addendum, erratum, host or decision.** This is a bounded
development-layer review. Supplements r64–r68, erratum E1, the L-DET addendum and every D-* decision stay PROPOSED or
undecided. Only the formal route review, a fresh S12 re-rating and the owner can accept, reject or put anything into
force.

**REPAIR = REPAIRED_WITH_DEFECTS.**
* All four symlink constructions of review 68 are now refused. So are:
  * a symlink or a file at every ancestor level;
  * an ancestor symlink on a side branch merged with `-s ours`;
  * a gitlink under the review directory;
  * the same constructions in a sha256 repository.
* No regression: every other review-68 probe outcome is unchanged.
* **Defect (S1):** a **gitlink at an ancestor** of the review directory is ACCEPTED when its commit object is absent,
  which is the normal case for a submodule. `cat-file --batch-check` then answers `<commit>:<path> missing`, which the
  parser accepts as "absent". A recursive checkout of that commit shows `<sha> REJECTED` at `<review dir>/veto.md`.
  The supplement, the docstring, the 336bb0cb message and ledger 514 all state that this case is refused.

**HARNESS = SOUND_WITH_DEFECTS.**
* RV55–RV60 are each KILLED in both records and in my single runs. Q01 (three edits) is KILLED, and its two-edit shape
  reproduces the recorded ERROR.
* The counts 193/194 are right.
* Defects:
  * The new ancestor check is pinned only through a symlink at `level4` on a linear history. RB1, RB2, RB4 and RB6
    survive with changed outcomes (S2).
  * The widened RV26 is killed by its review-68 edit alone. Its K7 edit alone survives, and the K7 check is now
    unreachable (S3).

**RECORDS = ACCURATE_WITH_CORRECTIONS.**
* All 58 file bindings in ledger lines 511–518 recompute (93 checks: at the introducing commit and, except for inputs
  changed later by design, at dad3c948). Both gz records gunzip to their bound digests.
* Review 68 and its 32 scratch files are byte-identical to the originals.
* The ledger is append-only. No credential or signed URL appears. The failed local run is recorded accurately.
* Corrections are wording only (S5, S6):
  * the gitlink claim (S1);
  * "refuses the known ways a checkout differs";
  * the stale 1420-entry count;
  * the pending native run on dad3c948.

---

## 3. Review 68's findings (Q1)

Evidence files are in scratch:
* `probes69*`: new probes;
* `rerun68/probes68*`: review-68 probes re-run unchanged;
* `reviewer69_mutants*` and `reviewer69b_mutants*`;
* `check_records69*`;
* `suites/`.

| finding (review 68) | disposition (supplement r68) | verified at dad3c948 | status |
|---|---|---|---|
| P1 MINOR: symlinks make a checkout show a rejection that git's scan never lists; r67 rationale wrong | (a) fail closed: non-regular entries under the directory in any commit; non-directory review dir / ancestor in any commit; test with 5 subtests; RV59, RV60; RV26 widened; checkout-view equivalence not claimed | `_historical_review_blobs` `:1292–1293` refuses any `ls-tree -r` entry whose mode is not 100644/100755 (git canonicalises odd modes first: 100664 → 100644; 140000 → 160000, refused). `_review_dir_is_a_directory` `:1229–1248` is called after it (`:1383`). Re-run of review 68's probes: all four symlink constructions are now **refused**. New probes: symlink or file at each of `level4`, `level4/closure_proofs` and `…/p5y_k5_cell308_research` refused; side-branch (`-s ours`) ancestor symlink refused; sha256 repository refused; gitlink under the directory refused; gitlink at an ancestor whose commit is **present** refused. **But a gitlink at an ancestor whose commit is absent (a real submodule) is ACCEPTED** (S1). The r67 rationale is withdrawn (ledger 513), and the docstrings say the rule is on tree paths and blob contents. | **PARTIALLY RESOLVED** (S1) |
| P2 NOTE: INFO-class messages pass `--strict` | wording | `_history_complete` docstring `:1200–1202` and supplement §2 item 3 say WARN refuses and INFO passes. Re-run `info_class_bad_filemode_legit`: ACCEPTED, as now stated. No INFO case is pinned (stated). | **RESOLVED** |
| P3 MINOR: N2 witness covers only `--find-object` | sign the acceptance commit too; RA3 = RV55 | Test `:1592–1622` signs both commits (`sign_head` after each). RV55 is byte-equal to RA3 and is KILLED by that test alone, in both records and singly here. | **RESOLVED** |
| P4 NOTE: `--strict` pinned via one id; `GIT_ATTR_NOSYSTEM` unpinned | zero-padded subtest (RV56 = RA2); static env check (RV57 = RA4); RA1 = RV58 with a `fsck.fullPathname` subtest | RV56: zero-padded `040000` tree in history refuses with "history completeness"; KILLED alone. RV57: killed by the direct `_git_env()` dictionary check. This pins the dictionary, not its use (S2/RB6). It is stated as a non-observation. RV58: KILLED (its witness plus the review-66 test). | **RESOLVED** (RV57 is a static pin, as stated) |
| P5 NOTE: records residue | ledger 513 marks 508 coordinator-asserted; 38783320859 recorded | Ledger 513 says it. Ledger 515 matches the API: success; job-log SUMMARY 224 / 187 / 187 / pass; artifact 11999725415; `sha256:43039c43…`; git 2.55.0. The RV49/RV50-on-2.55 statement is inferred from `killed == total == 187`, which is valid. | **RESOLVED** |

**Supplement r68 §2: mostly accurate. Three corrections.**
* Items 1–3 exactly describe `_history_complete` `:1208–1214`. The isolation bullets hold as tested. The system
  attributes file is pinned statically only (RV57, as stated).
* **Correction 1 (S1).** The text says the review directory and each ancestor in any commit is refused if it "was ever
  a symlink, gitlink or file", and that the scan refuses "a non-directory review directory or ancestor". This is false
  for an ancestor gitlink whose commit is not in the object store. The repository is ACCEPTED, so the case is
  over-stated as refused. In the legitimate direction, such a repository is not refused either.
* **Correction 2 (S5).** "It refuses the known ways a checkout differs" is overstated:
  * ancestor gitlinks or submodules (S1);
  * directory names that differ only by case or Unicode normalisation/ignorables (`Level4/…`, `…/Reviews`,
    `…/rev‌iews`, `…/reviewś`), which are ACCEPTED. On a case-insensitive or normalising file system (macOS,
    Windows, ext4 casefold), a checkout of these would place a rejection at the review path.

  The rule as written does not cover these (distinct tree paths), so the fix is wording.
* **Correction 3 (S6).** "At HEAD in this session, the real review directory holds 1420 entries" is the count at
  05caa00e/9250f473. The commit that carries the supplement (336bb0cb) has 1453 entries; dad3c948 has 1455. All are
  `100644`.

  The clone is shallow (`--is-shallow-repository` true; 662 commits visible). In the visible history, all 1456 raw
  entries under the directory are `100644`, so no `120000` or `160000` entry was ever committed.
* The rest of the refused list matches what I measured:
  * shallow clones, partial clones and promisor keys, `fsck.*` keys;
  * WARN-class messages (zero-padded mode, `nulInCommit`, `badTimezone`);
  * the index naming missing objects, dubious ownership, a 60 s timeout, and `./att/HOST.json`;
  * symlinks and gitlinks (commit present) under or at the directory or an ancestor.

---

## 4. Answers Q2–Q5

### Q2 — Adversarial fail-closed audit

**Suites:** `python3.1x -B -W error::ResourceWarning -m unittest discover -s tests -v` gives **226 tests OK** on 3.11,
3.12 and 3.13 (`suites/`). The pinned tree was clean afterwards.

**Review 68's probes re-run unchanged** (`rerun68/probes68_at_dad3c948_out.json`, same script sha `fbf11770…`):
* Every outcome is identical to `probes68_out.json` at 05caa00e, except the four symlink constructions, which went from
  ACCEPTED to **refused**.
* Still ACCEPTED: the legitimate controls (sha256, separate git dir, bare clone, gc + changed-paths graph,
  `.gitmodules`, a submodule at `s`, sparse index, linked worktree, notes / tag / stash, and the INFO-class
  `badFilemode`).
* The configured-command sweep runs no command, as before. The order-rule diff-configuration cases stay refused.
* Exception roots still give no exception.
* No regression from 05caa00e.

**New probes** (`probes69.py.txt`, `probes69_out.json`):

| construction (history commit, removed later; HEAD carries a valid acceptance) | `_review_dir_is_a_directory` | outcome | finding |
|---|---|---|---|
| gitlink (absent commit) at `level4`, `level4/closure_proofs` or `…/p5y_k5_cell308_research` | True (all four answers `… missing`) | **ACCEPTED** | S1 |
| real submodule at `level4` (`.gitmodules`; its commit lives only in the submodule repository) | True | **ACCEPTED**; strict fsck rc 0. A recursive clone checked out at that commit shows `<sha> REJECTED` at `<review dir>/veto.md` | S1 |
| `160000` entry at `level4` whose oid is a **tree** present in the store | True (`<oid> tree 41`, deeper paths `missing`) | **ACCEPTED** | S1 (entry mode is not read) |
| odd mode `140000` at `level4` (canonicalised to gitlink) → tree | True; strict fsck rc 0 (INFO `badFilemode`) | **ACCEPTED** | S1 |
| gitlink (absent commit) at the review directory itself | True (the check alone would pass) | refused by the history scan (160000 listed) | RB5: the leaf check is redundant |
| gitlink with present commit at `level4` | False | refused | — |
| `140000` → blob under the review directory | — | refused (history scan) | — |
| symlink at `level4` pointing at a tree oid | — | refused (fsck: "is a tree, not a blob") | — |
| symlink or file at each of the three ancestors | False | refused | — |
| ancestor symlink on a side branch merged `-s ours` | False | refused | — |
| sha256 repository, ancestor symlink | False | refused | — |
| case / Unicode variants of the directory holding a deleted rejection | — | ACCEPTED (distinct tree paths) | S5 wording |
| 30 000-commit linear history (fast-import) | True in 1.81 s | ACCEPTED in 3.4 s | margin about 30× under the 60 s timeout |
| unborn repository, a file, a missing path as `repo_root` | False, no exception | — | — |

**Classes:**
* **ACCEPTED where the stated rule refuses:**
  * Under the rule as written (git tree paths and blob contents), none: a submodule's content is never a tree path of
    this repository.
  * Under the stated refusal list (an ancestor "ever a … gitlink"): the absent-commit gitlink and the gitlink-mode → tree
    entries are ACCEPTED (S1).
  * The batch parser also accepts `<c>:<path> missing` when the commit `c` itself is unreadable. Under the isolated
    environment fsck guarantees readability, but RB6 shows the property is fail-open if isolation is lost (S4).
* **A repository-configured command runs during the check:** none.
  * The new call carries `_GIT_ISOLATION` and `_git_env()`.
  * `cat-file --batch-check` runs no textconv, filter or pager. The review-68 command sweep still runs nothing.
  * Every fsck in a probe prints a `graftFileDeprecated` hint, because of `GIT_GRAFT_FILE=/dev/null`. It is harmless.
* **Exceptions escaping `attestation_valid` / preflight:** none found.
  * `_review_dir_is_a_directory` catches the same exception classes as `_git`.
  * Unborn, file and missing roots return False.
  * Only an out-of-memory condition on a pathological history is uncaught. That is pre-existing in kind.
* **Legitimate full-clone cases newly refused and not stated:** none found.
  * Every refusal I produced is in the new list.
  * The list over-states one refusal (absent-commit ancestor gitlinks are accepted).
* **Regressions from 05caa00e:** none.
* **Native git 2.55:** RV55–RV60 and Q01 on 2.55 are pending in run **38812337420**, which was in progress at 22:04Z.
  UNVERIFIED.

**Mutants:** 6 new (RB1–RB6): **1 killed** (RB3) and **5 survived**:
* RB1, RB2, RB4 and RB6 survive with outcome changes toward ACCEPTED;
* RB5 is equivalent, with no outcome change.

### Q3 — Harness integrity

* **RV55 (= RA3):** byte-equal edits; KILLED by `test_review67_signature_program_never_runs` alone. Direct: the signed
  acceptance commit is selected only by `-S`.
* **RV56 (= RA2):** KILLED by the new zero-padded subtest alone. Direct: zero-padded mode is WARN-class, and only
  `--strict` refuses it.
* **RV57 (= RA4):** KILLED by the static `_git_env()` dictionary assertion.
  * It is a direct pin of the dictionary, not of an effect. This is stated, and acceptable.
  * It does not pin that each git call uses `_git_env()`. RB6 drops it from the new batch-check call, survives, and
    turns an ancestor-symlink repository ACCEPTED when the caller's environment carries a `GIT_DIR` (S2).
* **RV58 (= RA1):** KILLED; the new `fsck.fullPathname` subtest fails, as does the review-66 worktree subtest. Genuine.
* **RV59:** restores the 05caa00e line (`if parts[1] != b"blob": continue`); KILLED by the new test (and the K7 test).
  Direct.
* **RV60:** `if False:`; KILLED only through the `ancestor_symlink` subtest (`level4`, linear history). The
  `review_dir_symlink` subtest is already refused by the history scan (RB5 equivalent). The witness is genuine but
  narrow (S2).
* **RV26 (widened):** KILLED. But **the K7 edit alone SURVIVES** and **the review-68 edit alone is KILLED** by the same
  witness, failing the same two methods (`RV26_edit1_only_K7`, `RV26_edit2_only_history_symlinks`).
  * Reason: any symlink at HEAD under the directory was introduced by a commit that the history scan lists, so the K7
    mode check at `:1393` is unreachable.
  * The widened RV26 is a witness of the P1 symlink refusal (as RV59 already is), not of K7.
  * The K7 test's remaining "symlink is not an accepting review" assertion (`:1858`) holds by the P1 refusal (S3).
* **Q01 (three edits):** a faithful single-property weakening.
  * The non-recursive history listing shows `040000 tree` entries, which the base's recursive listing never shows.
    Skipping them restores the mutant's intent. Direct-child symlinks and gitlinks still refuse.
  * KILLED, including its witness `test_acceptance_is_found_not_named`.
  * Its two-edit (336bb0cb) shape reproduces **ERROR NO_INTENDED_PROPERTY_ASSERTION**. The two failing methods are the
    same as in the failed record.
  * Not masked, not over-weakened: the third edit only removes entries the base never sees.
* **Counts:**
  * `MUTANT_GROUP_SIZES` sums to 32+10+9+14+9+15+11+13+16+4+60 = **193**;
  * `test_mutation_harness` asserts 193;
  * the workflow asserts `== 193` and `len(suites) == 194` and takes the test count (226) from the record;
  * both records have 193 rows with `ran` 226.
  * **Right.** A 90 min timeout is ample: 188 suites took 39 min on run 38783320859.
* **Re-classification:**
  * All 193 rows of each record re-classify with the harness of the commit they ran on (336bb0cb's / bf5987a5's
    `run_mutants.py`). Ids, order, edits, properties, witnesses and every `mutated_lx_platform_sha256` match.
  * `problems: []` in both.

### Q4 — Records

* **Ledger:**
  * 05caa00e (510 lines) → 9250f473 (511) → 336bb0cb (514) → bf5987a5 (517) → dad3c948 (518).
  * Each is a byte prefix of the next (`check_records69_out.json`, `prefix_chain: true`).
* **Bindings:** 58 file bindings, 93 checks, 0 problems:
  * 511: brief 68 `0654a6b0…`;
  * 512: review 68 `381ff283…` and 32 scratch files;
  * 514: 10 inputs (at 336bb0cb) and supplement r68 `714890f5…`;
  * 516: the 336bb0cb gz `f6545685…`;
  * 517: 10 inputs (at bf5987a5);
  * 518: the bf5987a5 gz `6ad9f9f3…`.
  * The only input that differs between 514 and dad3c948 is `run_mutants.py`, changed by bf5987a5 by design.
* **Compressed records:**
  * `…_336BB0CB.json.gz` gunzips to `8d5fb006…` and `…_BF5987A5.json.gz` to `e72e152e…`, equal to the ledger. Both
    headers have mtime 0, flags 0, XFL 2 and OS 3 (`gzip -9 -n`).
  * Input hashes (before = after) equal the 336bb0cb and bf5987a5 blobs respectively.
  * 336bb0cb: baseline 226 PASS; 192 KILLED + **Q01 ERROR NO_INTENDED_PROPERTY_ASSERTION** (failed
    `test_ascii_acceptance_control_and_nonascii_tab_newline_veto_paths` and
    `test_malformed_listing_and_nonutf8_review_blob_refuse_verification`; the witness passed); `pass: false`;
    `utc 20:10:27Z` = ledger 516 `finished_utc`. **Ledger 516 records it accurately.**
  * bf5987a5: 193/193, baseline 226, `utc 21:44:10Z`, before run 38812337420 was created (21:46:01Z). No run exists for
    336bb0cb or bf5987a5, so "not pushed" / "before any push" is consistent.
  * `source_commit` is null in both. The binding rests on the input hashes, which hold.
* **Review 68 and scratch:**
  * `REVIEW_REVIEW67_REPAIR_DELTA.md` and all 32 committed scratch files are byte-identical to the `scratchpad/review68`
    originals (`.py` → `.py.txt` for the two `lx_platform.py` copies).
  * No original outside `tmp/`, `tree_05caa00e/` and `home/` is omitted, which matches ledger 512's omission statement.
  * Every committed scratch file is bound, and every binding is committed.
* **Signed URLs / credentials:** I scanned every file added or modified in the delta (gz decompressed; only the ledger's
  new lines).
  * Hits are only review 68's description of its own scan, `check_records68.py.txt`'s marker list and its output.
  * One placeholder `https://example.invalid/s` appears in `probes68.py.txt`.
  * **No signed URL and no credential.**
* **Modified files:** 37 A and 7 M.
  * The 7 M are the 5 tested inputs, the ledger (append-only) and `BRIEF_INDEX.md` (one appended row for brief 68).
  * No reviewed or historical review, governance or audit file changed. Supplement r67 is not edited.
* **Native runs since 9b6347cb:**
  * All runs up to **38783320859** are recorded. 38783320859 is in ledger 515, which matches the API.
  * **38812337420** (dad3c948) was `in_progress` at 22:04Z and cannot be in the commit it tests. Ledger 518 says
    PENDING, which is correct; it must be recorded later.

### Q5 — Overstatement

1. **Gitlinks at ancestors.** These sources state that an ancestor ever a "gitlink" is refused:
   * the 336bb0cb message ("fail closed … on a review directory or ancestor that is not a directory in any commit");
   * ledger 514 `repairs[0]`;
   * supplement r68 P1 row and §2 ("ancestors was ever a symlink, gitlink or file");
   * the `_review_dir_is_a_directory` docstring ("A symlink (or gitlink, or file) there").

   **Overstated:** this holds only when the gitlink's commit object is in the repository (S1).
2. **Supplement §2: "It refuses the known ways a checkout differs".** Overstated: ancestor submodules, and case- or
   normalisation-variant directories on case-insensitive or normalising file systems, are known and not refused (S5).
3. **Supplement P1 row: "RV26 … is widened to a combined weakening, because the new scan would otherwise mask it".**
   Accurate as far as it goes, but it omits that the K7 check is now unreachable and RV26 no longer witnesses it (S3).
4. **Supplement §2: "1420 entries at HEAD"** is stale for the commit that carries it (S6).
5. **Ledger 518 `worktree_clean_after: true`:** UNVERIFIED. It is consistent with `inputs_unchanged`.
6. **Not overstated:**
   * 336bb0cb's "226 tests OK on 3.11/3.12/3.13" (reproduced);
   * "R5SYNC02, RV09–RV11, RV26, RV31, RV49, RV50, RV55–RV60 KILLED singly" (the record and my runs agree for those I
     re-ran);
   * ledger 516's account of the failed run and its cause (reproduced);
   * bf5987a5's "same single property weakened" for Q01 (verified);
   * ledger 515 (verified via API);
   * ledger 513's withdrawals;
   * §2's "defence in depth, not a closure" and "checkout-view equivalence is not claimed".

---

## 5. New findings

**S1 — MINOR — A gitlink (submodule) at an ancestor of the review directory is ACCEPTED. The repair and every
description of it state that it is refused.**
* **Location:**
  * `lx_platform.py:1229–1248` (`_review_dir_is_a_directory`): `missing` is accepted for any name.
  * Supplement r68 P1 row and §2; the 336bb0cb message; ledger 514 `repairs[0]`.
* **Mechanism:**
  * For `<c>:level4` where `level4` is a `160000` entry whose commit is not in the store (normal for a submodule),
    `cat-file --batch-check` resolves the path and fails the object lookup. It prints `<c>:level4 missing`, which is
    the same text as an absent path.
  * The deeper names also print `missing`.
  * `_historical_review_blobs` never lists the entry: `ls-tree -r <c> -- <review dir>` does not match a non-directory
    ancestor, and `rev-list -- <review dir>` may not list the commit at all.
  * Related: a `160000` (or odd-mode `140000`) entry whose oid is a tree prints `tree` and is accepted. The check reads
    the object type, not the entry mode.
* **Evidence** (`probes69_out.json`):
  * `gitlink_absent_commit_at::level4` (also `…/closure_proofs` and `…/p5y_k5_cell308_research`): ACCEPTED.
  * `gitlink_ancestor_real_submodule_checkout_shows_rejection`: ACCEPTED, strict fsck rc 0. A
    `clone` + `checkout <c>` + `submodule update --init` shows `<sha> REJECTED` at `<review dir>/veto.md`.
  * `gitlink_mode_entry_pointing_at_tree_at_ancestor` and `socket_mode_entry_at_ancestor…`: ACCEPTED.
* **Scope:** this is the review-68 P1 class (checkout view). The rule as written (this repository's tree paths) does
  not cover submodule content. The defect is that the fail-closed repair claims this case and does not implement it.
* **Correction:** either
  * (a) fail closed on the entry mode: read the ancestors' modes, for example
    `ls-tree -z <c> -- <ancestor paths>` per commit, or one `log --raw`-style pass. Alternatively, accept `missing` for
    `<c>:<p>` only when `<c>:<parent>` is a tree with no entry named `<p>`. Add an ancestor-gitlink subtest
    (absent commit) and a mutant; or
  * (b) withdraw "gitlink" (ancestor) from the docstring, the supplement and the ledger statements and list it as
    accepted.

**S2 — MINOR — Harness: the ancestor check is pinned only through a symlink at the top component on a linear
history.**
* **Evidence** (`reviewer69_mutants_result.json`, `reviewer69b_mutants_result.json`). Each mutant below survives with
  226 tests passing, and base refuses where the mutant ACCEPTS:
  * RB1: intermediate ancestors skipped; `level4/closure_proofs` symlink.
  * RB2: `--first-parent`; ancestor symlink on a side branch merged `-s ours`.
  * RB4: `commit` read as a directory; gitlink with present commit at `level4`.
  * RB6: the batch-check call drops `env=_git_env()`; ancestor symlink with a caller `GIT_DIR` pointing at an empty
    repository. Every answer becomes `missing`.
* RB5 (leaf omitted) is equivalent: the history scan already refuses a non-directory review directory.
* **Correction:**
  * Add subtests for a symlink at a middle ancestor, an ancestor symlink on an `-s ours` side branch, and a gitlink with
    present commit at an ancestor.
  * Add the S1 case once fixed.
  * Add a caller-`GIT_DIR` subtest to the new test, or extend `test_review65_caller_git_environment_is_ignored` to an
    ancestor construction.
  * Register RB1, RB2, RB4 and RB6 (RB5 as equivalent, not registered).

**S3 — NOTE — Harness: the widened RV26 no longer witnesses K7, and the K7 mode check is unreachable.**
* `RV26_edit1_only_K7` SURVIVES (the suite passes).
* `RV26_edit2_only_history_symlinks` is KILLED by the same two methods as the widened RV26.
* Any HEAD symlink under the directory is refused earlier by the history scan, so `:1393–1394` is now defence in depth
  that no test can reach.
* **Correction:**
  * State that K7 is subsumed by P1 and that the K7 check is unreachable.
  * Re-describe RV26 as a P1 (symlink) witness, or retire it as duplicating RV59.
  * Change the K7 test docstring accordingly.

**S4 — NOTE — The batch-check parser accepts `<commit>:<path> missing` when the commit itself is unreadable.**
* Under the isolated environment, strict fsck guarantees every listed commit is readable, so this is not reachable in
  the base.
* It is the mechanism behind RB6's outcome and part of S1's.
* **Correction:** also query `<commit>^{tree}` (or `<commit>`) and require a `tree` (or `commit`) answer for each
  commit, so that `missing` can only mean an absent path.

**S5 — NOTE — Supplement §2 over-states "refuses the known ways a checkout differs".**
* Ancestor gitlinks or submodules (S1) are not refused.
* Directory names differing by case or Unicode normalisation/ignorables (`Level4/…`, `…/Reviews`, `…/rev‌iews`,
  `…/reviewś`) are ACCEPTED (`probes69 variant_dir_rejection::*`), with strict fsck rc 0. A checkout on a
  case-insensitive or normalising file system would show their rejection at the review path.
* **Correction:** say "refuses these known differences: …" and list case-insensitive and normalising file systems as
  not covered (the D-HOST-LIFETIME procedure must use a case-sensitive, non-normalising checkout or rely on tree paths
  only).

**S6 — NOTE — Records residue.**
* Supplement §2's "1420 entries at HEAD" is the 05caa00e/9250f473 count. The supplement's own commit has 1453 entries,
  and dad3c948 has 1455, all `100644`.
* Native run 38812337420 (dad3c948; RV55–RV60 and Q01 on git 2.55) was in progress at review time.
* Ledger 518 `worktree_clean_after` is unverifiable.
* **Correction:** name the commit for the 1420 count. Append the 38812337420 line with its job-log SUMMARY and artifact
  digest. Mark `worktree_clean_after` as coordinator-asserted.

**Counts:** BLOCKING 0 · MAJOR 0 · MINOR 2 (S1, S2) · NOTE 4 (S3–S6); 6 new findings.

---

## 6. Reproduction and scratch files

* **Suites:** `suites/suite_python3.11.txt`, `suite_python3.12.txt`, `suite_python3.13.txt` (226 OK each).
* **Review-68 probes re-run:** `rerun68/probes68.py.txt` (copy, sha `fbf11770…`), with
  `rerun68/probes68_at_dad3c948_out.json`, `probes68_stdout.txt` and `probes68_err.txt` (empty).
* `rerun68/reviewer68_mutants.py.txt` is a copy and was not run unchanged. Its RA1–RA4 are now RV55–RV58 and were re-run
  singly through `reviewer69_mutants.py.txt`, which derives from it.
* **New probes:** `probes69.py.txt` (sha `cc128948…`), with `probes69_out.json` and `probes69_err.txt`.
* **Mutants:**
  * `reviewer69_mutants.py.txt` (`c111cbe3…`): registered RV26, RV55–RV60 and Q01 singly; the RV26 and Q01 splits;
    RB1–RB5. Outputs: `reviewer69_mutants_result.json`, `reviewer69_mutants_stdout.txt`.
  * `reviewer69b_mutants.py.txt` (`8e1648cd…`): RB6. Outputs: `reviewer69b_mutants_result.json`,
    `reviewer69b_mutants_stdout.txt`.
* **Records:** `check_records69.py.txt` (`2b9618f7…`), with `check_records69_out.json` and `check_records69_stdout.txt`.
* **Base copy:** `base/lx_platform.py` (`bdca4aa0…`).

---

## 7. Reviewer mutants (brief 69)

**Method:**
* Each mutant is a copy of the dad3c948 `lx_platform.py` under `scratch/tmp`.
* The pinned 226-test suite runs through the harness's own `run_suite` (`LX_PLATFORM_DIR`, `PYTHONWARNINGS=error`).
* Each mutant is classified with the harness's `classify_mutant` against a fresh PASS baseline (226). Witness for RB1–RB5:
  `test_review68_non_directory_review_paths_refuse`. RB6 also uses `test_review65_caller_git_environment_is_ignored`.
* An outcome check runs base and mutant on one synthetic construction, each in a child interpreter.

**Result: 6 new mutants, 1 killed, 5 survived** (4 with an outcome change toward ACCEPTED; 1 equivalent).

```
### RB1 SURVIVED | ancestor check reads only the top component and the review directory
###   symlink at level4/closure_proofs in history: base refused -> mutant ACCEPTED
-             for i in range(1, len(parts) + 1)]
+             for i in (1, len(parts))]

### RB2 SURVIVED | ancestor check walks only the first-parent chain
###   level4 symlink on a side branch merged with -s ours: base refused -> mutant ACCEPTED
-    commits = _git(repo_root, "rev-list", "HEAD")
+    commits = _git(repo_root, "rev-list", "--first-parent", "HEAD")

### RB3 KILLED | history scan skips gitlinks (only symlinks refuse)
###   gitlink under the review directory in history: base refused -> mutant ACCEPTED
+            if parts[1] == b"commit":
+                continue
             if parts[0] not in (b"100644", b"100755"):          # review 68 P1
    failed: test_review68_non_directory_review_paths_refuse (history_gitlink subtest)

### RB4 SURVIVED | a `commit` answer is read as a directory
###   gitlink (commit present) at level4 in history: base refused -> mutant ACCEPTED
-re.fullmatch(r"[0-9a-f]{40,64} tree [0-9]+", a)
+re.fullmatch(r"[0-9a-f]{40,64} (tree|commit) [0-9]+", a)

### RB5 SURVIVED (equivalent) | ancestor check omits the review directory itself
###   review directory a symlink in history: base refused -> mutant refused (history scan)
-             for i in range(1, len(parts) + 1)]
+             for i in range(1, len(parts))]

### RB6 SURVIVED | the batch-check call runs with the caller's environment
###   level4 symlink in history, caller GIT_DIR=<empty repo>: base refused -> mutant ACCEPTED
###   (without the caller GIT_DIR both refuse)
-                           input=("\n".join(names) + "\n").encode(), capture_output=True, timeout=60, env=_git_env())
+                           input=("\n".join(names) + "\n").encode(), capture_output=True, timeout=60)
```

For each survivor, the suite returned 0 with 226 tests.

**Registered mutants re-run singly** (not reviewer mutants), each against the same 226-test baseline:
* RV26, RV55–RV60 and Q01: all **KILLED**.
* RV55, RV56, RV57 and RV60 fail only their own witness.
* RV26, RV58, RV59 and Q01 also fail other related tests, as expected.

**Diagnostic splits** (not registered):

| split | status | failing methods |
|---|---|---|
| `RV26_edit1_only_K7` | **SURVIVED** | none |
| `RV26_edit2_only_history_symlinks` | KILLED | the K7 test and the review-68 test |
| `Q01_first_two_edits_336bb0cb_shape` | **ERROR NO_INTENDED_PROPERTY_ASSERTION** | the same two methods as the failed 336bb0cb record |
