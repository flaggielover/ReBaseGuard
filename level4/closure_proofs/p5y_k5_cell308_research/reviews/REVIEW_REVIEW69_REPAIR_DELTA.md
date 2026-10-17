# Review: the coordinator's repairs of review 69's findings (combined Cell-308 development source, Cloud route r1, S4 changed branch)

* Reviewer: **reviewREVIEW69_REPAIR (fresh agent, brief 70)**
* Date: 2026-10-15/16 (UTC), about 23:57Z to 00:20Z.
* Pinned commit: **`9f223c91afdc8f3db5fe786b11ddee581e7fb2e1`** (branch `codex/cell308-claude-r5-integration`, draft PR
  flaggielover/ReBaseGuard#3). Detached worktree `scratchpad/review70/tree_9f223c91`. `git status --porcelain` was
  empty after the suites, the probes and the mutant runs. I wrote nothing there.
* Delta: `dad3c948..9f223c91`, three commits: f52e123f (brief 69), 73760d9e (review 69 recorded, repairs), 9f223c91
  (local full-run record on 73760d9e; native run 38812337420 recorded).
* NS = `level4/closure_proofs/p5y_k5_cell308_research/`, DEV = `NS/streams/CLOUD_R1_LINUX_DEV`. Line numbers refer to
  the 9f223c91 files.
* Scratch: `/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review70/` ("scratch").
  * Probes and mutants ran on `scratch/base/lx_platform.py`, sha256 `cddfd4a2…`. This equals the 9f223c91 blob and the
    binding in ledger line 522 (`input_sha256`).
  * Scripts are stored as `*.py.txt`.
  * Every git, gpg and Python process I started ran with `HOME=scratch/home`, `GNUPGHOME=scratch/home/.gnupg` and
    `TMPDIR` under `scratch/tmp`. `scratch/home` holds only the empty `.gnupg` directory. `scratch/tmp` was emptied
    at the end (it held 52 suite fixture directories and the probe temporaries, all inside scratch).
* Local git: **2.43.0** (Ubuntu). Native runner git: 2.55.0 (job log of run 38812337420).
* `new_target_evaluations = 0`. I ran no cell, drift, certificate, decoy, science module, qualification case or
  candidate code. I installed nothing and changed no setting. I did not run the optional full `run_mutants.py`.

---

## 1. Exposure disclosure

**Opened:**
* Brief 70 in the shared checkout. It is the only file I read there.
* In the pinned tree:
  * the `dad3c948..9f223c91` diffs of the five tested inputs, `BRIEF_INDEX.md` and the ledger;
  * `lx_platform.py` lines 1155–1630 (git helpers, completeness, history scan, the new walk, `_acceptances`,
    `_ordered`, `attestation_valid`, `preflight`);
  * the new and the review-68 / review-65 / K7 tests in `tests/test_lx_platform.py`;
  * `run_mutants.py` (the changed `MUTANTS` entries, `MUTANT_GROUP_SIZES`, `PROPERTY_WITNESSES`, `classify_mutant`,
    `apply_mutation`); dad3c948's `run_mutants.py` and `lx_platform.py` (git objects) for the CDEX15 comparison;
  * the workflow diff;
  * review 69 as recorded, supplement r69, the six ledger lines appended after dad3c948, and the delta's commit
    messages;
  * the committed review-69 scratch scripts (`probes69.py.txt`, `reviewer69_mutants.py.txt`, `rerun68/probes68.py.txt`),
    copied to `scratch/rerun69/` and `scratch/rerun68/`.
* The compressed record `LOCAL_FULL_HARNESS_PY312_73760D9E.json.gz`, decompressed in memory: header, input hashes,
  counts, every mutant row (ids, status, ran, failure names). It holds synthetic test output only.
* `scratchpad/review69/` originals, for the byte comparison only (file names and bytes).

**Name-level contact:**
* the scratchpad root listing (it shows sibling directory names such as `review59`…`review69`, `fix69`, `rev5`; I
  opened none of them except `review69/` for Q4);
* `git diff --name-status dad3c948..9f223c91` contains no audit, interruption, mb_r1, 309 or exposure-disclosure path.

**Shared object store:** the pinned worktree's git dir lives in the shared repository, so every git read of the pinned
tree went through it (objects only). Beyond the diffs I ran: `ls-tree -r <c> -- <review dir>` entry counts and modes at
9250f473, f52e123f and 9f223c91; `rev-parse --is-shallow-repository` (true); `rev-list --count HEAD` (665);
`merge-base --is-ancestor` between delta-era commits; `git show <c>:<path>` of the bound files. All HEAD-reachable
(no `--all`). I ran no `fsck` and no git command in the shared checkout.

**GitHub (read-only, MCP):** the branch's run list; jobs and artifacts of run 38812337420; the last 60 lines of job
116688373242; the status of run 38826606180. The log tail contains an artifact page URL, which I did not record here.

**Live calls:** none against the real repository. Every `attestation_valid`, `_history_complete`,
`_review_dir_is_a_directory`, `_cat_file_batch` and `_tree_entry` call passed a synthetic repository under
`scratch/tmp` (or literal bytes) with `machine_identity` patched.

**Not opened, grepped or read:** `NS/audit/EXECUTION_INTERRUPTION_ASSESSMENT*`, `NS/audit/INCIDENT_AUDIT*`,
`NS/reviews/REVIEW_EXECUTION_INTERRUPTION*`; anything under `p5y_k5_cell308_mb_r1/postexec/` and any MB r1 target-run
or qualification record; `NS/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`; any Cell-309 branch, file or record;
candidate source. My credential scan (Q4) read only files added or modified in the delta.

**No accidental contact.** No side effect outside scratch.

---

## 2. Verdicts

REPAIR: REPAIRED_WITH_DEFECTS
HARNESS: SOUND_WITH_DEFECTS
RECORDS: ACCURATE_WITH_CORRECTIONS

**No verdict here accepts any amendment, supplement, addendum, erratum, host or decision.** This is a bounded
development-layer review. Supplements r64–r69, erratum E1, the L-DET addendum and every D-* decision stay PROPOSED or
undecided. Only the formal route review, a fresh S12 re-rating and the owner can accept, reject or put anything into
force.

* **REPAIR = REPAIRED_WITH_DEFECTS.** The code repair of S1/S4 is correct: every review-69 gitlink construction
  (absent commit at each ancestor, a real submodule, present commit, gitlink-mode → tree, odd `140000` → tree) is now
  refused, in sha1 and sha256 repositories; no regression in any review-68 or review-69 probe. Defects are in what the
  repair claims about itself: RB5 and RB6 are stated "equivalent" and are not (T1), and §2's checkout guidance is
  incomplete (T6).
* **HARNESS = SOUND_WITH_DEFECTS.** RV61–RV63 are genuine direct witnesses, CDEX15 is the same weakening, 196/197 is
  right. Gaps: a regular-file review directory, merge commits' own trees, odd directory-like modes, sha256 width and
  S4 itself are unpinned (T1–T4; RC1, RC3, RC4, RC5, RC7 survive).
* **RECORDS = ACCURATE_WITH_CORRECTIONS.** All 75 binding checks of the six new ledger lines recompute; the gz record
  gunzips to its digest and its inputs equal the 73760d9e blobs; review 69 and its 24 scratch files are byte-identical
  to the originals; no credential or signed URL. Corrections: the equivalence wording (T1) and the pending native run
  on 9f223c91 (T7).

---

## 3. Review 69's findings (Q1)

| finding (review 69) | disposition (supplement r69) | verified at 9f223c91 | status |
|---|---|---|---|
| S1 MINOR: ancestor gitlink (absent commit) ACCEPTED; gitlink-mode → tree passes | walk by MODE from every root tree; non-`40000` refuses; 3 gitlink subtests; RV63 | `_review_dir_is_a_directory` `:1274–1306` peels `<c>^{tree}` (must answer `tree`), then per depth one `cat-file --batch` over the distinct trees; `_tree_entry` `:1260–1271` reads `(mode, oid)`; any mode ≠ `b"40000"` returns False. Re-run of `probes69`: all seven gitlink/odd-mode constructions that were ACCEPTED at dad3c948 are now **refused** (`dir_check` False), including the real-submodule case whose checkout shows `<sha> REJECTED`. My probes: sha256 absent-commit gitlink at `level4/closure_proofs` refused; 40755 / 41000 directory-like modes refused (fsck rc 0, INFO `badFilemode`); sibling gitlinks (`vendor/x`, `level4/other`, `…/reviews2`, `…/reviews.bak`) ACCEPTED (not over-refused). | **RESOLVED** |
| S2 MINOR: ancestor check pinned only via a top-level symlink | 6 subtests; RV61–RV63 = RB1, RB2, RB4; RB5, RB6 "equivalent" | RV61, RV62, RV63 each KILLED singly, each failing only `test_review69_ancestor_entries_are_read_by_mode` (middle_symlink / side_branch_symlink / the three gitlink subtests), and in the gz record. **But** RB5 is not equivalent: the history scan does **not** refuse a regular-file review directory (`ls-tree -r` lists `100644 blob <review dir>`); RC1 (leaf omitted on the new walk) SURVIVES and turns that history ACCEPTED. RB6 is not equivalent either: with a caller `GIT_OBJECT_DIRECTORY` + alternates forging a **non-root** tree (`cat-file --batch` does not verify hashes; only the `^{tree}` peel does), RC2 ACCEPTS what base refuses. RC2 happens to be KILLED by `test_review65_caller_git_environment_is_ignored`, through a reason-text change (UNAVAILABLE instead of HISTORICAL), not by the `caller_git_dir` subtest. | **PARTIALLY RESOLVED** (T1) |
| S3 NOTE: widened RV26 no longer witnesses K7 | stated; comment; RV26 re-described; K7 docstring | Comment at `:1452`, RV26 description and the K7 test docstring say so. Reasoning holds: any HEAD entry under the directory is in the tree of some commit that `rev-list --full-history -- <dir>` lists (or of a root commit), so the history scan sees a HEAD symlink first. RV26 KILLED singly (K7 test + review-68 test). | **RESOLVED (STATED; acceptable to carry)** |
| S4 NOTE: `missing` accepted when the commit is unreadable | `_cat_file_batch` refuses any `missing` | `_cat_file_batch` `:1229–1257` requires exactly three header fields and a hex id; `missing` / `ambiguous` (two fields) → None. Direct call: `[c, "0"*40]` → None. Paths are no longer looked up by name. Not pinned (RC7 survives; equivalent under isolation + fsck, T4). | **RESOLVED** (unpinned, T4) |
| S5 NOTE: "refuses the known ways a checkout differs" | withdrawn; §2 lists refused / not refused | Withdrawn in the supplement header. Re-run: the four case/Unicode variants are still ACCEPTED, as now stated. But §2's guidance "or use a case-sensitive, non-normalising checkout" omits other known checkout differences (T6). | **PARTIALLY RESOLVED** (T6, wording) |
| S6 NOTE: records residue | 1420 attributed; 1455 at f52e123f; 38812337420 recorded; 518 coordinator-asserted | `ls-tree -r`: 1420 at 9250f473, 1455 at f52e123f (1481 at 9f223c91), all `100644`. Ledger 523 matches the API and log: success, SUMMARY 226 / 193 / 193 / pass, artifact 12010862383, digest `sha256:24a88da3…`, runner git 2.55.0. Ledger 521 marks 518 coordinator-asserted. | **RESOLVED** |

**Supplement r69 §2: accurate as a description of the code; incomplete in two places.**
* Items 1–3 exactly describe `_history_complete` `:1208–1214`. The two scan bullets describe `_historical_review_blobs`
  and the new walk. "Any failure, timeout (60 s per git call), missing object or other answer refuses" holds for the
  walk.
* The refused list matches what I measured: symlink / file / gitlink / submodule / odd mode (40755, 41000, 140000) at
  an ancestor or the directory; zero-padded `040000` (strict fsck); duplicate and unsorted trees (strict fsck).
* The not-refused list (case / Unicode / ignorable variants) is right but not the whole set relevant to a checkout
  reader (T6). Also unstated: the walk's integrity rests on strict fsck plus the environment isolation, because
  `cat-file --batch` returns object contents without verifying their hashes (T4), and duplicate entries are refused
  only by fsck (T5).
* Performance: "1.8 s on a 30 000-commit linear history" — UNVERIFIED as such; I measured 1.58 s with review 69's
  construction, 2.43 s with a distinct tree at every depth in every commit, and 12.87 s at 150 000 commits (≈ linear;
  the 60 s limit would be reached around 700 000 such commits). Covered by the stated timeout refusal.

---

## 4. Answers Q2–Q5

### Q2 — Adversarial fail-closed audit

**Suites:** `python3.1x -B -W error::ResourceWarning -m unittest discover -s tests -v` → **227 tests OK** on 3.11, 3.12
and 3.13 (`scratch/suites/`). Pinned tree clean afterwards.

**Review 68's probes re-run unchanged** (`scratch/rerun68/probes68_at_9f223c91_out.json`): all 16 keys identical to
`probes68_at_dad3c948_out.json` after normalising object ids and temporary names. Summary stdout byte-identical.

**Review 69's probes re-run unchanged** (`scratch/rerun69/probes69_at_9f223c91_out.json`): the only outcome changes from
dad3c948 are the intended ones (gitlink absent ×4, real submodule, gitlink-mode → tree, odd `140000` → tree at
`level4`: ACCEPTED → refused; `ancestor_symlink_mode_pointing_at_tree` and the review-dir gitlink now also fail the
walk, previously only fsck / the history scan). Case/Unicode variants and the 30 000-commit control stay ACCEPTED.

**New probes** (`scratch/cons70.py.txt`, `scratch/probes70/`):

| construction | walk | outcome | note |
|---|---|---|---|
| review directory itself a regular file (100644 / 100755) in history | False | refused | only the walk refuses it (RC1) |
| evil merge: ancestor symlink only in the merge commit's own tree | False | refused | a checkout of the merge shows `<sha> REJECTED` at `<review dir>/veto.md`; the history scan does not list the merge (RC3) |
| caller `GIT_OBJECT_DIRECTORY` + alternates forging the bad commit's **root** tree | False | refused | the `^{tree}` peel verifies the hash: `missing` |
| same, forging a **non-root** tree (`level4`) | False | refused | under RC2 (no `_git_env()` in the helper): ACCEPTED |
| sha256: forged root tree via caller env | False | refused | |
| duplicate entries `level4` (symlink, then directory) | **True** | refused by strict fsck (`duplicateEntries`) | `_tree_entry` returns the last match (T5) |
| unsorted root tree | False | refused (fsck `treeNotSorted`) | |
| `level4` symlink beside `level4 x` / `a level4` directories | False | refused | names with spaces parsed correctly |
| control: `level4 copy` symlink, `level4.x`, `level4/closure_proofs x` symlink, `<review dir> old` file | True | ACCEPTED | |
| empty tree at `level4` / at the review directory | True | ACCEPTED | nothing to show; not a refusal case |
| directory-like odd modes 40755, 41000 at `level4` | False | refused; fsck rc 0 (INFO) | git and `ls-tree` canonicalise them to `040000 tree`, a checkout shows a directory: legitimate-looking but stated as refused ("odd mode") |
| zero-padded `040000` | False | refused (strict fsck) | stated |
| sha256: gitlink (absent) at `level4/closure_proofs` | False | refused | width 32 handled |
| sha256 control | True | ACCEPTED | |
| unrelated root merged `--allow-unrelated-histories`, its history with an ancestor symlink | False | refused | |
| two unrelated roots, clean | True | ACCEPTED | |
| symlink only on an unmerged branch | True | ACCEPTED | HEAD's history only (stated scope) |
| sibling gitlinks (`vendor/x`, `level4/other`, `…/reviews2`, `…/reviews.bak`) | True | ACCEPTED | not newly refused |
| HEAD file naming a tree; NUL in `repo_root`; bare clone | False / False / True | refused / "not committed" / ACCEPTED | no exception |
| `_tree_entry` on truncated / NUL-less / empty / sha256 data; `_cat_file_batch` on missing, prefix, empty, a name with a space | — | False / False / None / correct; None / commit / [] / None | no exception |
| repository-configured sweep (`pager.cat-file`, `core.pager`, filter smudge/clean/process, textconv, `gpg.program`, `core.sshCommand`, `credential.helper`, `core.askPass`, `uploadpack.packObjectsHook`, `core.alternateRefsCommand`, hooks dir, `core.fsmonitor`, `log.showSignature`) | True | ACCEPTED | **no command ran** |
| 30 000 / 150 000 commits, a distinct tree at every depth in every commit | True in 2.43 s / 12.87 s | — | |

**Classes:**
* **ACCEPTED where the stated rule refuses:** none in the base. Every construction the supplement lists as refused is
  refused. The refusals rely on strict fsck for duplicates and unsorted trees (T5) and on `_git_env()` for forged
  objects (T1/T4).
* **Repository-configured command run:** none (sweep above; review 68's sweep unchanged).
* **Exception escaping `attestation_valid` / preflight:** none found. `_tree_entry` bounds every slice; `_cat_file_batch`
  catches the same classes as `_git`; `ids[0]` is reached only after a non-empty `rev-list` answer.
* **Legitimate full-clone case newly refused and not stated:** none. Directory-like odd modes are refused although git
  treats them as directories; this is stated ("odd-mode entry"). Very long histories hit the stated 60 s limit.
* **Regression from dad3c948:** none.

**Mutants:** 7 new (RC1–RC7): **2 KILLED** (RC2, RC6), **5 SURVIVED** (RC1, RC3, RC4, RC5 with outcome changes; RC7
equivalent under isolation). Details in §7.

### Q3 — Harness integrity

* **RV61** (RB1 on the new walk: a non-directory at a middle depth is skipped, top and leaf still refuse): KILLED singly;
  fails only `middle_symlink`. Direct. Faithful to RB1.
* **RV62** (`--first-parent`): KILLED singly; fails only `side_branch_symlink`. Direct; byte-equal to RB2's edit
  (re-applying RB2 with review 69's witness list gives ERROR `NO_INTENDED_PROPERTY_ASSERTION` only because the
  witness is now the review-69 test).
* **RV63** (`160000` read as a directory, not descended): KILLED singly; fails exactly the three gitlink subtests.
  Direct. Note it skips the gitlink instead of descending, which is the realistic weakening (RB4's analogue).
* **CDEX15 re-anchored:** the dad3c948 anchor now occurs twice (`_git` and `_cat_file_batch`), so re-anchoring was
  required. Applying the old edit to dad3c948 and the new edit to 9f223c91 gives the **identical** hunk in `_git`
  (`scratch/q3/cdex15.py.txt`). Same weakening. The new helper's identical exception clause is weakened by no mutant
  (T4; its `ValueError` / `UnicodeError` paths are not reachable from `_review_dir_is_a_directory`, whose names are
  hex and whose `repo_root` already passed `_git`).
* **RB5 / RB6 "equivalent":** **wrong** (T1). RC1 = RB5 on the new walk SURVIVES with an outcome change (regular-file
  review directory). RC2 = RB6 on the new helper changes the outcome (forged non-root tree) and is KILLED, but only
  indirectly by `test_review65_caller_git_environment_is_ignored`.
* **Review 69's other edits:** RB1, RB4, RB5, RB6 anchors no longer exist (NOT_APPLIED). RB3 still applies and is
  KILLED by `history_gitlink`.
* **Counts:** `MUTANT_GROUP_SIZES` sums to 32+10+9+14+9+15+11+13+16+4+63 = **196**; `validate_registry()` returns 196;
  `test_mutation_harness` asserts 196; the workflow asserts `== 196` and `len(suites) == 197` (196 mutants + baseline)
  and takes `expected_test_count` (227) from the record. All other registered anchors still occur exactly once. The gz
  record has 196 rows, every suite `ran` 227, errors 0, skipped 0. **Right.**

### Q4 — Records

* **Ledger:** dad3c948 (518 lines) → f52e123f (519) → 73760d9e (522) → 9f223c91 (524); each a byte prefix of the next.
* **Bindings** (`scratch/records/check_records70_out.json`): 75 checks, 0 problems — brief 69 `c6606725…`; review 69
  `6ad15c5f…` and 24 scratch files; the 10 inputs of 73760d9e and supplement r69 `93d254b7…`; the gz `0e123232…`; each
  at its introducing commit and at 9f223c91.
* **Compressed record:** gunzips to `9743486…` = `uncompressed_sha256`; header mtime 0, flags 0, XFL 2, OS 3
  (`gzip -9 -n`). `input_sha256` = `input_sha256_after` = the 73760d9e blob for all 10 inputs. Baseline 227 PASS,
  196 KILLED, `utc 23:55:05Z` = ledger `finished_utc`, before run 38826606180 was created (23:56:58Z). No native run
  exists on 73760d9e, so "before any push" is consistent. `source_commit` null (binding rests on the input hashes).
* **Review 69 and scratch:** `REVIEW_REVIEW68_REPAIR_DELTA.md` and all committed scratch files are byte-identical to the
  `scratchpad/review69` originals (`.py` → `.py.txt` for `base/lx_platform.py`). The only uncommitted originals are under
  `tree_dad3c948/` (the worktree), consistent with ledger 520's omission statement (`tmp/` was empty, `home/` holds an
  empty directory).
* **Signed URLs / credentials:** scanned every added or modified file (gz decompressed; ledger new lines only). Hits are
  `log.showSignature` (false positives), the `https://example.invalid/s` placeholder, and the `Claude-Session` URL quoted
  from commit messages inside `check_records69_out.json`. **No signed URL, no credential.**
* **Modified files:** 28 A, 7 M. The 7 M are the 5 tested inputs, the ledger (append-only) and `BRIEF_INDEX.md` (one
  row inserted at the end of the table). No reviewed or historical review, governance or audit file changed;
  supplement r68 is not edited.
* **Native runs since 9b6347cb:** every run from 38689564567 to 38812337420 appears in the ledger (38812337420 in
  ledger 523, matching the API). **38826606180** (9f223c91) was `in_progress` at review time; it cannot be in the commit
  it tests and must be recorded later (T7).

### Q5 — Overstatement

1. **"RB5 and RB6 equivalent"** — supplement r69 S2 row, ledger 522 `repairs[1]` ("RB5 and RB6 equivalent (stated)"),
   and the review-69 test docstring ("RB6, equivalent since S4"). False (T1). The S2 row's reason for RB5 ("the history
   scan refuses a non-directory review directory") is false for a regular file.
2. **§2 "The D-HOST-LIFETIME procedure must read tree paths only, or use a case-sensitive, non-normalising checkout"** —
   the second alternative is not sufficient (T6).
3. **Ledger 522 / 73760d9e message "every missing batch answer refuses" (S4)** — accurate in code, unpinned (T4).
4. **Ledger 523 `git_2_55`** ("RV55–RV60 and Q01 KILLED on git 2.55.0") and `gate` ("every suite ran 226 with 0
   errors/skips") are inferred from the passing workflow assertions and `killed == total`; valid inferences, not
   artifact reads (stated as such: `artifact_audit: UNVERIFIED`).
5. **Not overstated:** the S1 code claims (73760d9e message, ledger 522 `repairs[0]`, docstring); "227 OK on
   3.11/3.12/3.13" (reproduced); the selected strict checks for RV61–RV63, CDEX15, RV26 (reproduced); 9f223c91's
   "196/196, inputs equal to 73760d9e's blobs" (verified); S6's counts; §3's CDEX15 sentence.

---

## 5. New findings

**T1 — MINOR — RB5 and RB6 are stated equivalent; neither is.**
* **Location:** supplement r69 §1 S2 row; ledger 522 `repairs[1]`; `test_review69_ancestor_entries_are_read_by_mode`
  docstring.
* **Evidence:**
  * RC1 (RB5 on the new walk, `enumerate(parts[:-1])`) **SURVIVES** (227 pass). Construction `leaf_regular_file`: the
    review directory is a regular file in one commit, later removed. Base: walk False, refused. Mutant: ACCEPTED.
    `ls-tree -r <c> -- <review dir>` lists `100644 blob …\t<review dir>`, which the history scan accepts as a regular
    file, so only the walk refuses it.
  * RC2 (RB6 on `_cat_file_batch`, no `env=_git_env()`): with a caller `GIT_OBJECT_DIRECTORY` holding a forged loose
    object for the `level4` tree of a commit whose `level4/closure_proofs` is a symlink, and
    `GIT_ALTERNATE_OBJECT_DIRECTORIES` at the real store, base refuses and the mutant ACCEPTS
    (`scratch/probes70/forge_mid70_out.txt`). `cat-file --batch` does not verify object hashes. RC2 is KILLED under the
    strict criteria, but only because `test_review65_caller_git_environment_is_ignored` expects a HISTORICAL reason and
    now gets UNAVAILABLE; the `caller_git_dir` subtest does not fail.
* **Scope:** neither is a base fail-open (a regular-file review directory shows no review path in a checkout; the env
  is isolated). The defect is a false harness claim and two unpinned stated refusals.
* **Correction:** withdraw both equivalence statements. Add a `review_dir_regular_file` subtest and register RC1; add
  a forged-object-directory subtest (non-root tree) as a direct witness and register RC2 (or state that
  `test_review65_…` kills it indirectly).

**T2 — MINOR — Harness: merge commits' own trees are not pinned.**
* **Evidence:** RC3 (`rev-list --no-merges HEAD` in the walk) SURVIVES. Construction `evil_merge_ancestor_symlink`: a
  merge whose own tree (in no parent) has `level4 -> alt` and `alt/…/reviews/veto.md`. A checkout of the merge shows
  `<sha> REJECTED` at `<review dir>/veto.md`; the history scan does not list the merge. Base refuses; mutant ACCEPTS.
* **Correction:** add an evil-merge subtest and register RC3.

**T3 — NOTE — Harness: sha256 width and directory-like odd modes are not pinned.**
* RC5 (`width = 20`) SURVIVES and refuses every legitimate sha256 repository (`sha256_control`: base ACCEPTED, mutant
  refused). No test in the suite uses `--object-format=sha256`.
* RC4 (`not mode.startswith(b"4")`) SURVIVES and ACCEPTS a 40755 directory at `level4`, which §2 lists as refused. Not a
  fail-open (git canonicalises it, so the history scan sees its files).
* **Correction:** add a sha256 positive control and an odd-directory-mode subtest, or state both as unpinned.

**T4 — NOTE — S4 and the helper's integrity assumptions are unpinned and unstated.**
* RC7 (a `missing` answer read as an empty tree) SURVIVES; equivalent while the environment is isolated and strict fsck
  has run, because nothing is then missing.
* The helper's own exception clause has no mutant (CDEX15 covers `_git` only).
* `cat-file --batch` returns contents without hash verification. The walk is therefore only as good as the strict
  fsck that ran earlier over the same object store plus `_git_env()`. §2 does not say this.
* **Correction:** state in §2 and the docstring that the walk relies on the fsck precondition and the isolation; pin
  S4 or state it as defence in depth.

**T5 — NOTE — `_tree_entry` takes the last of duplicate entries.**
* For a root tree `[120000 level4, 40000 level4]`, `_review_dir_is_a_directory` alone returns **True**. Only strict
  fsck (`duplicateEntries`, an error class) refuses the repository, and `_acceptances` always runs it first.
* **Correction:** return False on a second match (a two-line change), or state the reliance on fsck.

**T6 — NOTE — Supplement §2's checkout alternative is incomplete.**
* "Or use a case-sensitive, non-normalising checkout" leaves out other ways a checkout differs from tree paths and
  blob contents:
  * smudge/clean filters, `eol` / `core.autocrlf`, `ident` and `working-tree-encoding` attributes;
  * sparse checkout / skip-worktree, which can hide a committed rejection;
  * untracked or modified working-tree files;
  * a checkout of a commit other than HEAD.
* **Correction:** require the D-HOST-LIFETIME procedure to read git tree paths and blob contents only, or list these
  conditions too.

**T7 — NOTE — Records residue.**
* Native run 38826606180 on 9f223c91 was `in_progress` at review time, so it is UNVERIFIED here. It is the first native
  run on the review-69 repairs (no run exists on 73760d9e).
* **Correction:** append its line with the job-log SUMMARY and artifact digest.

**Counts:** BLOCKING 0 · MAJOR 0 · MINOR 2 (T1, T2) · NOTE 5 (T3–T7); 7 new findings.

---

## 6. Reproduction and scratch files

* Suites: `suites/suite_python3.11.txt`, `suite_python3.12.txt`, `suite_python3.13.txt`, `suites/rc.txt` (227 OK each).
* Re-runs: `rerun68/probes68.py.txt` (copy) → `rerun68/probes68_at_9f223c91_out.json`, `probes68_stdout.txt`,
  `probes68_err.txt` (empty); `rerun69/probes69.py.txt` (copy) → `rerun69/probes69_at_9f223c91_out.json`,
  `probes69_stdout.txt`, `probes69_err.txt` (empty). `rerun69/` also holds copies of `reviewer69_mutants.py.txt`,
  `reviewer69b_mutants.py.txt`, `check_records69.py.txt` (not run unchanged; their RB edits are re-applied by
  `reviewer70_mutants.py.txt`).
* New probes: `cons70.py.txt` → `probes70/probes70_out.json`, `probes70_stdout.txt`, `probes70_err.txt`;
  `forge_mid70.py.txt` → `probes70/forge_mid70_out.txt` (base, then RC2); `evil_merge_view70.py.txt` →
  `probes70/evil_merge_view70_out.txt`.
* Mutants: `reviewer70_mutants.py.txt` → `mut70/reviewer70_mutants_result.json`, `_stdout.txt`, `_err.txt`.
* Harness comparison: `q3/cdex15.py.txt` with `q3/old/` (dad3c948 `lx_platform.py`, `run_mutants.py.txt`).
* Records: `check_records70.py.txt` → `records/check_records70_out.json`, `check_records70_stdout.txt`.
* Diagnostics: `diag/dbg70a.py.txt`, `diag/dbg70b.py.txt` (root-tree forgery shows `hash mismatch` at the peel),
  `diag/RC2_lx_platform.py.txt`.
* Base copy: `base/lx_platform.py` (`cddfd4a2…`).

---

## 7. Reviewer mutants (brief 70)

**Method:**
* Each mutant is a copy of the 9f223c91 `lx_platform.py` under `scratch/tmp`.
* The pinned 227-test suite runs through the harness's own `run_suite` (`LX_PLATFORM_DIR`, `PYTHONWARNINGS=error`).
* Each mutant is classified with the harness's `classify_mutant` against a fresh PASS baseline (227). The witnesses
  are listed per mutant.
* The outcome check runs base and mutant on one `cons70` construction, each in a child interpreter.

**Result: 7 new mutants, 2 killed, 5 survived** (4 with an outcome change, 1 equivalent under isolation).

```
### RC1 SURVIVED | the review directory's own entry is not read by mode (RB5 on the new walk)
###   regular file at <review dir> in history: base refused -> mutant ACCEPTED   (witnesses: review69 + review68 tests)
-    for depth, name in enumerate(parts):
+    for depth, name in enumerate(parts[:-1]):

### RC2 KILLED | _cat_file_batch runs with the caller's environment (RB6 on the new helper)
###   caller GIT_OBJECT_DIRECTORY forging the level4 tree (non-root): base refused -> mutant ACCEPTED
###   killed only by test_review65_caller_git_environment_is_ignored (reason text: UNAVAILABLE, not HISTORICAL)
-                           capture_output=True, timeout=60, env=_git_env())
+                           capture_output=True, timeout=60)

### RC3 SURVIVED | merge commits' own trees are skipped
###   evil merge carrying level4 -> alt only in its own tree: base refused -> mutant ACCEPTED
-    commits = _git(repo_root, "rev-list", "HEAD")
+    commits = _git(repo_root, "rev-list", "--no-merges", "HEAD")

### RC4 SURVIVED | directory-like odd modes are read as directories
###   40755 at level4: base refused -> mutant ACCEPTED (git canonicalises it to a tree; stated as refused)
-            if mode != b"40000":
+            if not mode.startswith(b"4"):
                 return False

### RC5 SURVIVED | raw trees parsed with a fixed 20-byte id
###   sha256 control: base ACCEPTED -> mutant refused (no sha256 test in the suite)
-    level, width = {oid for oid, _, _ in roots}, len(ids[0]) // 2
+    level, width = {oid for oid, _, _ in roots}, 20

### RC6 KILLED | only HEAD's root tree is walked
###   failed: review68 ancestor_symlink; review69 all six subtests
-    level, width = {oid for oid, _, _ in roots}, len(ids[0]) // 2
+    level, width = {roots[0][0]}, len(ids[0]) // 2

### RC7 SURVIVED (equivalent under isolation + strict fsck) | a `missing` answer is read as an empty tree
+        if len(head) == 2 and head[1] == b"missing":
+            pos = nl + 1
+            answers.append(("0" * 40, "tree", b"" if contents else None))
+            continue
         if len(head) != 3 or not re.fullmatch
```

For each survivor the suite returned 0 with 227 tests. Every killed mutant ran 227 tests with the baseline's executed
test ids.

**Registered mutants re-run singly** (against the same baseline): RV26, RV60, RV61, RV62, RV63 and CDEX15 are all
**KILLED**. RV61, RV62 and RV63 fail only their own witness. RV26 fails the K7 test and the review-68 test. RV60 fails
the review-68 `ancestor_symlink` subtest and all six review-69 subtests. CDEX15 fails its two witnesses.

**Review 69's edits re-applied:** RB1, RB4, RB5 and RB6 are NOT_APPLIED (their anchors are gone). RB2 (= RV62) is
ERROR `NO_INTENDED_PROPERTY_ASSERTION` with review 69's witness list; it fails `side_branch_symlink` of the review-69
test. RB3 is KILLED by `history_gitlink`.
