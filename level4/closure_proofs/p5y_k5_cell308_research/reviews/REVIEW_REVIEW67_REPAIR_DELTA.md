# Review: the coordinator's repairs of review 67's findings (combined Cell-308 development source, Cloud route r1, S4 changed branch)

* Reviewer: **reviewREVIEW67_REPAIR (fresh agent, brief 68)**
* Date: 2026-10-15 (UTC), about 18:10Z to 18:35Z.
* Pinned commit: **`05caa00e19cd71eb1b1ca5f90d02eaab7cf63c44`** (branch `codex/cell308-claude-r5-integration`, draft PR
  flaggielover/ReBaseGuard#3). Detached worktree `scratchpad/review68/tree_05caa00e`. `git status --porcelain` was
  empty after the suites and after the mutant runs. I wrote nothing there.
* Delta: `2f39e9f4..05caa00e`, four commits: 074bb4a0 (brief 67), 73018725 (native run on 2f39e9f4 recorded), ad341014
  (review 67 recorded, repairs), 05caa00e (local full-run record).
* NS = `level4/closure_proofs/p5y_k5_cell308_research/`, DEV = `NS/streams/CLOUD_R1_LINUX_DEV`. Line numbers refer to
  the 05caa00e files.
* Scratch: `/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review68/` ("scratch").
  * Probes ran on `scratch/base/lx_platform.py`, sha256 `fbcf9ef5…`. This equals the 05caa00e blob and ledger 509's
    binding.
  * Comparisons at 2f39e9f4 ran on `scratch/base2f39/lx_platform.py` (`470436ea…`, copied from review 67's original).
  * Scripts are stored as `*.py.txt`.
  * Every git, gpg and Python process I started ran with `HOME=scratch/home` and `GNUPGHOME=scratch/home/.gnupg`
    (`TMPDIR=scratch/tmp`). Both directories are empty at the end.
* Local git: **2.43.0** (Ubuntu). Native runner git: 2.55.0 (job log of run 38756465002).
* `new_target_evaluations = 0`. I ran no cell, drift, certificate, decoy, science module, qualification case or
  candidate code. I installed nothing and changed no setting.

---

## 1. Exposure disclosure

**Opened:**
* Brief 68 in the shared checkout. It is the only file I read there.
* In the pinned tree:
  * the `2f39e9f4..05caa00e` diffs of the five tested inputs and of `BRIEF_INDEX.md`;
  * `lx_platform.py` lines 1130–1640;
  * the review-64/65/67 tests in `tests/test_lx_platform.py` that the delta touches (around lines 1252–1290, 1361–1420 and
    1505–1630);
  * `run_mutants.py` (`MUTANTS` tail, `PROPERTY_WITNESSES`, `classify_mutant`, `apply_mutation`);
  * the workflow;
  * review 67 as recorded, supplement r67, ledger lines 500–510, and the delta's commit messages.
* The compressed record `LOCAL_FULL_HARNESS_PY312_AD341014.json.gz`, decompressed in memory. I read the header, input
  hashes, status counts and every mutant row (edits, witnesses, suite failure names). It holds synthetic test output only.
* `scratchpad/review67/` originals, for the byte comparison. I copied `probes67.py.txt`, `reviewer67_mutants.py.txt`,
  `rerun66/probes66.py.txt` and `rerun66/probes66b.py.txt` to `scratch/rerun67/` and ran them there.
* I did not open `review67/tmp/` or `review67/tree_2f39e9f4/`; I only saw their names in a listing.

**Name-level contact:** the scratchpad root listing (the same names review 67 lists, plus `review68`). Nothing else was
opened. `git diff --name-only 2f39e9f4..05caa00e` contains no audit, interruption, mb_r1, 309 or exposure-disclosure
path.

**Shared object store:** the pinned worktree's git dir lives in the shared repository, so every git read of the pinned
tree went through it (objects only). I ran no `fsck` and no git command in the shared checkout.

**GitHub (read-only, MCP):**
* the branch's run list;
* jobs of runs 38783320859 and 38756465002;
* the artifacts of run 38756465002;
* the last 40 lines of job 116496102737.

The log tail contains an artifact page URL, which I did not record.

**Live calls:** none against the real repository. Every `attestation_valid` and `_history_complete` call passed
`repo_root=<synthetic repository under scratch/tmp>` with `machine_identity` patched. Before running the
`exception_repo_roots` probe, I confirmed that `scratch/tmp` has no enclosing git repository (`rev-parse` rc 128), so no
probe could discover a parent repository.

**Not opened, grepped or read:**
* `NS/audit/EXECUTION_INTERRUPTION_ASSESSMENT*`, `NS/audit/INCIDENT_AUDIT*`, `NS/reviews/REVIEW_EXECUTION_INTERRUPTION*`;
* anything under `p5y_k5_cell308_mb_r1/postexec/`, and any MB r1 target-run or qualification record;
* `NS/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`;
* any Cell-309 branch, file or record;
* candidate source.

**No accidental contact.** No side effect outside scratch: HOME and GNUPGHOME were redirected, and no system `gpg` ran
(every signature program was a scratch script).

---

## 2. Verdicts

REPAIR: REPAIRED_WITH_DEFECTS
HARNESS: SOUND_WITH_DEFECTS
RECORDS: ACCURATE_WITH_CORRECTIONS

**No verdict here accepts any amendment, supplement, addendum, erratum, host or decision.** This is a bounded
development-layer review. Supplements r64–r67, erratum E1, the L-DET addendum and every D-* decision stay PROPOSED or
undecided. Only the formal route review, a fresh S12 re-rating and the owner can accept, reject or put anything into
force.

**REPAIR = REPAIRED_WITH_DEFECTS.**
* Each of N1–N7 is resolved in code or wording as claimed.
* Review 67's two ACCEPTED constructions are now refused: the `fullPathname` tree entry, and the order-rule bypass
  through `gpg.program`. No repository-configured command ran in a sweep of 46 command-bearing keys and 28 hooks.
* **Defect (P1):** supplement r67 declines the pathspec-independent scan because "strict fsck already refuses the
  warning-class names that make the two views differ". That is not true. Symlinks make the checkout view differ from
  git's scan with no fsck message at all. A rejection shown by a checkout at `<review dir>/veto.md` (at HEAD, deleted in
  history, or under a symlinked review or ancestor directory) is **ACCEPTED**, at 05caa00e and at 2f39e9f4. Under the
  rule as written (git tree paths and blob contents) these rejections lie outside the review directory. The defect is
  the stated rationale and the "checkout view" framing, not a regression.
* **Defect (P2):** INFO-class fsck messages pass `--strict`, which contradicts the "any warning refuses" wording.

**HARNESS = SOUND_WITH_DEFECTS.**
* RV49–RV54 are each KILLED by their own witness alone, in the record and in my single runs. RV31 and RV44 are
  re-anchored correctly. 187/188 is right.
* Defects:
  * The N2 witness covers only the `--find-object` call. RA3 moves the signature switch to that call alone and
    **survives**, and a signature program runs again (P3).
  * The `--strict` requirement is pinned only through `fullPathname`: RA2 survives (P4).
  * `GIT_ATTR_NOSYSTEM` is unpinned: RA4 survives, inert (P4).

**RECORDS = ACCURATE_WITH_CORRECTIONS.**
* All 81 sha256 bindings in ledger lines 505–510 recompute at their introducing commit and at 05caa00e.
* The gz record gunzips to the bound digest. Its inputs equal the ad341014 blobs, and all 187 rows re-classify.
* Review 67 and its 27 scratch files are byte-identical to `scratchpad/review67/`.
* The ledger is append-only. No credential or signed URL appears.
* Every native run since 9b6347cb is recorded, except 38783320859, which is in progress on 05caa00e (expected).
* Corrections are wording only: the supplement's N1 rationale (P1), the "any warning" wording (P2), and one unverifiable
  ledger statement (P5).

---

## 3. Review 67's findings (Q1)

"now" = 05caa00e. Evidence files are in scratch:
* `rerun67/`: review 66/67 probes re-run unchanged;
* `probes68*`, `reviewer68_mutants*`, `ra1_reclassify*`;
* `check_records68*`, `reclassify68*`;
* `suites/`.

| finding (review 67) | disposition (supplement r67) | verified at 05caa00e | status |
|---|---|---|---|
| N1 MAJOR: `fullPathname` entry hides a deleted rejection | `--strict` restored; test; RV49 | Code `:1212` is `fsck --full --strict --no-dangling --no-progress`. `rerun67/probes67_at_05caa00e_out.json`: `full_pathname_entry_hides_deleted_rejection` and `…_in_review_dir_tree` are **refused** ("history completeness"; strict rc 1, default rc 0). The `.`/`..`/`.git` variants are refused. New (`probes68 n1_in_alternate_shared_clone`): the same construction placed only in an alternate (`--shared`; 1 local object) is **refused**. It was **ACCEPTED at 2f39e9f4**, so `--full --strict` covers alternates. The construction plus `fsck.fullPathname=ignore` in the local, worktree or included (upper-case `[FSCK]`) scope is refused by the key list. RV49 is killed by its witness alone. **But** the supplement's reason for not adopting the pathspec-independent scan is wrong (P1), and "any warning refuses" is overstated (P2). | **RESOLVED** (rationale defect P1, wording P2) |
| N2 MAJOR: `git log` runs signature programs | `-c log.showSignature=false`; test; RV50 | Code `:1162`. `probes67`: `gpg_program_runs_on_valid_repo` invocations 0, ACCEPTED; `gpg_program_rewrites_quote_order_rule` gpg ran 0, **refused**; `gpg_ssh_program_runs` ran false. `probes68 configured_command_sweep` (46 keys incl. `core.pager`, `pager.*`, `gpg.*program`, `gpg.ssh.defaultKeyCommand`, `diff.external`, textconv / filter / merge drivers via `.gitattributes`, `core.hooksPath` with 28 hooks, `core.fsmonitor`, `core.alternateRefsCommand`, `uploadpack.packObjectsHook`, `ext::` remote, `trace2.*`, `diff.renames=copies`, `diff.relative`, `log.follow`, a signed commit): **no command ran** on a valid repository (still ACCEPTED) or on an order-rule repository (still refused). The same sweep at 2f39e9f4 records one `gpg --verify` call (positive control). The supplement's key audit matches. **But** the witness covers only the `--find-object` call (P3). | **RESOLVED** (pinning gap P3) |
| N3 MINOR: refused-repository list incomplete | dubious ownership added; `safe.directory` not passed | `probes67 dubious_ownership_legit_repo`: refused, reason "attestation not committed at HEAD" (git rc 128). It is listed in §2 with that reason. The `log.showSignature` + signed-commit refusal is gone (N2 sweep: valid repository ACCEPTED). Not passing `safe.directory` is a defensible fail-closed choice and is stated. Remaining wording problem: "any … warning" (P2). | **RESOLVED (STATED)**. Acceptable to carry. |
| N4 NOTE: global attributes read via HOME | `-c core.attributesFile=/dev/null`; test; RV51 | Code `:1163`. `probes67 global_attributes_file_read_via_HOME`: `check-attr -a` under the isolation returns **empty** (2f39e9f4: the global attribute was reported). RV51 is killed alone. The system attributes file (`GIT_ATTR_NOSYSTEM`) is unpinned and untestable here (RA4, P4). | **RESOLVED** |
| N5 MINOR: RZ1, RZ4, RZ5 survive | CDAT test asserts HISTORICAL; two subtests; RV52–RV54 | Test `:1374` asserts HISTORICAL. Subtests `extensions.partialClone` (with `repositoryformatversion=1`) and `remote.upstream.promisor` added (`:1399–1407`). RV52, RV53 and RV54 are each KILLED by the single witness, in the record and singly here. RV52/RV53/RV54 are byte-equal to RZ1/RZ4/RZ5. Registering RZ6 as "outcome-equivalent, not registered" is acceptable. | **RESOLVED** |
| N6 NOTE: wording and records | docstrings; ledger 506 / 508 | `_git_env` docstring `:1170–1172` names 2.43.0 (RV45 is killed locally on 2.43, consistent). The forged-graph docstring no longer says "strict fsck". Ledger 506 records run 38756465002: success, artifact 11986430317, `sha256:9b2c99ae…` (re-verified via API: artifact list and job-log digest line). Ledger 508 states the 3.11 / 3.13 wording. Its claim "the gate ran all three" is **UNVERIFIED**: no 2288bec1 gate output is committed (P5). | **RESOLVED** (one unverifiable statement) |
| N7 NOTE: class cannot be closed in-repository | §2 restated as defence in depth | §2 says "defence in depth, not a closure" and lists what is not established (consistent rewrite, check-to-read race, other repository-configured behaviour, reviewer authority), resting on D-HOST-LIFETIME (i) and (ii). The `_history_complete` docstring says the same. **But** the N1 row still argues that strict fsck makes "the two views" agree (P1). | **RESOLVED** (P1 inconsistency) |

**Supplement r67 §2: mostly accurate. Three corrections.**
* The three conditions exactly describe `_history_complete` (`:1205–1212`). The `config` call also passes `-z`, which is
  immaterial.
* The isolation bullets hold as tested:
  * replace refs and grafts are ignored (probes66 `use_replace_refs_local`, `env_allowlist`);
  * the graph is never read (Bloom and CDAT probes refused HISTORICAL);
  * no fsmonitor, lazy fetch or signature program runs;
  * global configuration and global attributes are not read.
  * The system attributes file is not observable here (UNVERIFIED; RA4).
* **Correction 1 (P2):** "any `git fsck --full --strict` error or warning in any object" is refused. False for
  INFO-class messages. A tree with mode `100664` prints `warning … badFilemode` and fsck exits 0 under `--strict`
  (`probes68 info_class_bad_filemode_legit`: **ACCEPTED**). The same holds for the other INFO ids (e.g.
  `missingTaggerEntry`, `gitattributesSymlink`), by git's design; I tested only `badFilemode`.
* **Correction 2 (P1):** §2 and the N1 row frame the class as git reporting "a history other than the one a checkout
  shows". The N1 row then claims strict fsck refuses what makes "the two views differ". Symlinks are a counterexample
  with no fsck message.
* **Correction 3 (wording):** errors in refs, reflogs or linked-worktree metadata also refuse ("any fsck error"), but
  they are not "in any object". This is minor; the list says "e.g.".
* The refused list is otherwise complete for what I measured. Accepted as legitimate (correctly):
  * sha256 object format;
  * `--separate-git-dir`;
  * a bare clone;
  * a repository after `gc --aggressive` with a changed-paths graph;
  * `.gitmodules`, a real submodule, a sparse index, a read from a linked worktree, notes, an annotated tag and a stash.

  Refused, all stated: `nulInCommit` (WARN), zero-padded modes, `badTimezone`, shallow, partial, `fsck.*`, dubious
  ownership, index naming a missing object, `./att/HOST.json`.

---

## 4. Answers Q2–Q5

### Q2 — Adversarial fail-closed audit

**Suites:** `python3.1x -B -W error::ResourceWarning -m unittest discover -s tests -v` gives **224 tests OK** on 3.11,
3.12 and 3.13 (`suites/suite_python3.1x.txt`). The pinned tree was clean afterwards.

**Review 66/67 probes re-run unchanged** (`rerun67/*_at_05caa00e_out.json`):
* Every construction refused at 2f39e9f4 is refused at 05caa00e.
* N1 (both variants) and the N2 order-rule bypass are now refused.
* Legitimate controls still ACCEPTED: `fsmonitor_valid_repo`, `gpg_program_runs_on_valid_repo` (program not run), the
  owned-by-caller repository and `att/HOST.json`.
* `zero_padded_mode_legit` is refused again, as stated.
* Clone shapes are unchanged: shallow and filter shapes refused for completeness, and every full shape refused as
  HISTORICAL.

**New probes** (`probes68.py.txt`; `probes68_out.json` at 05caa00e, `probes68_at_2f39e9f4_out.json` at 2f39e9f4):

| construction | 05caa00e | 2f39e9f4 | finding |
|---|---|---|---|
| HEAD: `<review dir>/veto.md` is a **symlink** (120000) to `notes/veto.txt` containing `<sha> REJECTED`, plus a valid acceptance | fsck strict rc 0; `ls-tree` shows `120000 blob`; a checkout of HEAD reads `<sha> REJECTED` at the review path; **ACCEPTED** | ACCEPTED | P1 |
| same symlink in history, then removed | fsck rc 0; checkout of C2 shows the rejection; **ACCEPTED** | ACCEPTED | P1 |
| history: the **review directory itself** is a symlink to a sibling `elsewhere/` holding `veto.md`, later removed | `ls-tree -r C2 -- <review dir>` lists only the symlink; checkout of C2 shows the rejection at `<review dir>/veto.md`; **ACCEPTED** | ACCEPTED | P1 |
| history: the top directory `level4` is a symlink to `alt/` holding the rejection at the same relative path | **ACCEPTED** (checkout shows it) | ACCEPTED | P1 |
| legitimate repository with a `100664` tree entry (INFO `badFilemode`) | strict rc 0 with a "warning" line; **ACCEPTED** | ACCEPTED | P2 (wording) |
| N1 construction only in an alternate (`clone --shared`) | refused (strict rc 1) | **ACCEPTED** | N1 fix covers it |
| N1 + `fsck.fullPathname=ignore` in local / worktree / include (`[FSCK] FullPathName`) | refused (key list); plain `git fsck --strict` rc 0 | refused | — |
| configured-command sweep (46 keys, 28 hooks, attributes drivers, signed commit), valid and order-rule repositories | no command ran; outcomes unchanged (ACCEPTED / refused); no trace2 file | `gpg --verify` ran once | N2 fixed |
| quote-before-blob under `* binary`, `* -diff`, `core.bigFileThreshold=1`, `diff.renames=copies` + `findCopiesHarder`, `text eol=crlf` + `autocrlf`; quote moved into the acceptance after the blob | all refused (order rule) | — | supplement's `-S` claim holds |
| legitimate shapes: sha256, separate git dir, bare clone, gc + changed-paths graph, `.gitmodules`, submodule, sparse index, linked worktree, notes / tag / stash | all ACCEPTED | — | — |
| `nulInCommit` in an old commit (WARN) | refused (stated class) | — | — |
| `repo_root` missing, a file, an empty dir, containing a newline, starting with `-` | refused, no exception; `_history_complete(file)` False | — | — |

**Classes:**
* **ACCEPTED where the stated rule refuses:**
  * None, under the rule as written: git tree paths under `ACCEPTANCE_REVIEW_DIR`, read as blobs.
  * Under the "what a checkout shows" standard that the N1 repair and supplement r67 use, the symlink constructions
    are ACCEPTED (P1). They are pre-existing and not a regression.
* **A repository-configured command runs during the check:** none found (sweep above). fsmonitor, lazy fetch and
  signature programs are all off.
* **Exception escaping `attestation_valid` / `preflight`:** none found. The delta adds no new raising path:
  `os.devnull` is formatted at import, and `_git` catches the same exceptions.
* **Legitimate full-clone cases newly refused and not stated:**
  * None. `--strict` re-refuses zero-padded modes and every WARN-class message (stated).
  * INFO-class histories are accepted, which is more permissive than the wording (P2).
* **Regressions from 2f39e9f4:** none found. Every refused construction stays refused. The changed outcomes go toward
  refusal (N1, N2, N1-in-alternate) or are the stated zero-padded change.
* **Native git 2.55:** RV49 and RV50 on 2.55 are pending in run 38783320859, which was **in progress** at 18:28Z
  (step 4). UNVERIFIED.

**Mutants:** 4 new (RA1–RA4): **1 killed** (RA1, after widening its witnesses to the test that fails; see §7) and
**3 survived** (RA3 with a changed outcome; RA2 with a changed outcome in the legitimate direction; RA4 inert).

### Q3 — Harness integrity

* **RV31 (re-anchored)** anchors on the new strict line and keeps the weakening (`return True`). It is KILLED by its
  witness (record and my run). The N1 test also fails, as expected, since the precondition is gone entirely.
* **RV44 (re-anchored)** deletes the whole fsmonitor line, leaving a valid tuple. It is KILLED by its witness alone.
* **RV49:** drops `--strict`; KILLED by the N1 test alone. Direct: a real `fullPathname` tree via `hash-object
  --literally`. The test also asserts the scan's blind spot (`rev-list` lists only HEAD) and that the full listing shows
  the entry.
* **RV50:** drops `log.showSignature=false`; KILLED alone. Direct: a real `gpgsig` header and a marker script.
  * The signed commit is the **attestation** commit, so only `_ordered`'s `--find-object` call is exercised.
  * The `-S` call is not (RA3 survives, P3).
* **RV51:** drops `core.attributesFile`; KILLED alone. Direct for the isolation flag: it calls `L._git(…, "check-attr")`
  under a patched HOME. It does not show any effect on an attestation outcome, which is inert anyway.
* **RV52:** replaces `core.commitGraph=false` with `commitGraph.readChangedPaths=false`; KILLED by the CDAT test's new
  HISTORICAL assertion. The kill comes through fsck's graph verification changing the reason, so it is an outcome
  witness, not a read witness. If a future git stopped verifying CDAT, the forgery would turn ACCEPTED and the test would
  still fail. Adequate.
* **RV53 / RV54:** KILLED by the new subtests alone. Direct (real keys; `repositoryformatversion=1` set for the
  extension).
* **Counts:**
  * `MUTANT_GROUP_SIZES` sums to 32+10+9+14+9+15+11+13+16+4+54 = **187**;
  * `validate_registry()` = 187 is asserted in `test_mutation_harness.py`;
  * the workflow asserts `== 187` and `len(suites) == 188` (baseline + 187), and takes `expected_test_count` (224) from
    the record;
  * the ad341014 record has 187 rows, each suite with `ran` 224.
  * **Right.** The workflow timeout of 90 min is ample: run 38756465002 took 31 min for 182 suites.
* **Gaps:**
  * P3: the N2 property is pinned on one of the two `git log` calls.
  * P4: `--strict` is pinned through one message id; `GIT_ATTR_NOSYSTEM` is unpinned.
  * The fsck-key refusal is pinned through `fsck.missingEmail`, `fsck.skipList` and (in the worktree subtest)
    `fsck.badTimezone`. RA1 is killed only by the last of these.

### Q4 — Records

* **Ledger:**
  * 2f39e9f4 (504 lines) → 074bb4a0 (505) → 73018725 (506) → ad341014 (509) → 05caa00e (510).
  * Each is a byte prefix of the next (append-only verified, `check_records68_out.json`).
* **Bindings:** **81 bindings** recompute at the introducing commit and at 05caa00e, with 0 problems:
  * 505: brief 67 `927ba91c…`;
  * 507: review 67 `eba3fe9d…` and 27 scratch files;
  * 509: 10 inputs and supplement r67 `94c69fd3…`;
  * 510: the gz record `3c5efb69…`.
* **Compressed record:**
  * It gunzips to `bb9cf2dd…` (= ledger 510's `uncompressed_sha256`). Header: mtime 0, flags 0, XFL 2, OS 3, consistent
    with `gzip -9 -n`.
  * All 10 `input_sha256` entries equal `input_sha256_after`, ledger 509, and the blobs at ad341014 and at 05caa00e.
  * Baseline 224 PASS; 187/187 KILLED; `utc` 18:07:54Z, before run 38783320859 was created (18:09:48Z). No run exists for
    ad341014 alone, so "before any push" is consistent.
  * Re-classifying all 187 rows with the pinned `classify_mutant` reproduces every status. The ids and order, edits,
    properties and witnesses equal the registry, every `mutated_lx_platform_sha256` recomputes against ad341014's
    source, and the RV origin is "Claude reviews 63-67" (`reclassify68_out.json`, `problems: []`).
  * `source_commit` is null. The binding rests on the input hashes, which hold.
* **Review 67 and scratch:**
  * `REVIEW_REVIEW66_REPAIR_DELTA.md` and all 27 committed scratch files are byte-identical to the `scratchpad/review67`
    originals (`.py` → `.py.txt` for the two `lx_platform.py` copies).
  * No original outside `tmp/` and `tree_2f39e9f4/` is omitted. Those two are covered by ledger 507's omission
    statement.
  * Every committed scratch file is bound, and every binding is committed.
* **Signed URLs / credentials:** I scanned every file added or modified in the delta (the gz decompressed; only the
  ledger's new lines) for `sig=`, `se=`, `sv=`, `X-Amz-`, GitHub token prefixes, `Authorization:`, `Bearer`,
  `api_key`, `password`, `token=`, blob-storage hosts and any `http(s)://`. The only hits are review 67's own
  description of its scan and `check_records67.py.txt`'s marker list. **No URL and no credential.**
* **Modified files** (`git diff --name-status 2f39e9f4..05caa00e`): 31 A, 7 M. The 7 M are the 5 tested inputs, the
  ledger (append-only) and `BRIEF_INDEX.md` (one appended row for brief 67). No reviewed or historical review,
  governance or audit file changed. Supplement r66 is not edited.
* **Native runs since 9b6347cb:**
  * Recorded: 38689564567, 38692293195 (485), 38694984232 (486/488), 38709761027, 38709764443 (490/496), 38714823675
    (491/493), 38725820509 (496/502), 38739675256 (502), and **38756465002 (506)**. The last matches the API: success,
    artifact 11986430317, `sha256:9b2c99ae…`, the job-log digest line, git 2.55.0.
  * Not recorded: **38783320859** (05caa00e). It was in progress at 18:28Z and cannot be in the commit it tests. Ledger
    510 says PENDING, which is correct.

### Q5 — Overstatement

1. **Supplement r67 N1 row:** "strict fsck already refuses the warning-class names that make the two views differ" is
   offered as the reason not to adopt the pathspec-independent scan. **Overstated.**
   * The views also differ through symlinks, with no fsck message (P1).
   * The pathspec-independent scan would not have caught the symlink cases either. The claim still implies an
     agreement between the two views that is not established.
2. **Supplement §2 refused list, the `_history_complete` docstring (`:1201`) and the N1 test docstring:** "any
   `git fsck --full --strict` error or warning in any object" / "refuses legitimate histories with any warning". INFO-class
   warnings pass (P2).
3. **Ledger 508:** "both describe the same pre-commit gate, which ran all three". UNVERIFIED: no gate output for 2288bec1
   is committed. I did reproduce 221 OK on all three at 2f39e9f4 (review 67) and 224 OK at 05caa00e (P5).
4. **Ledger 509 `repairs[2]`:** "refused-repository list completed". Acceptable for what was measured. It is weakened by
   P2 (the list over-refuses in wording).
5. **Ledger 510 `worktree_clean_after: true`:** UNVERIFIED. It is consistent with the record's `inputs_unchanged`.
6. **Not overstated:**
   * the ad341014 message's "224 tests OK on 3.11/3.12/3.13" (reproduced);
   * "RV23, RV30–RV32, RV39, RV43, RV44, RV48–RV54 KILLED singly" (the record and my runs agree for those I re-ran);
   * "187/187, baseline 224, inputs equal ad341014's blobs, before any push" (verified);
   * ledger 506 (verified via API);
   * the withdrawal in ledger 508;
   * §2's "defence in depth, not a closure";
   * "N1's and N2's behaviour on 2.55 is shown only by the native run of RV49 and RV50" (correctly not claimed yet).

---

## 5. New findings

**P1 — MINOR — Symlinks make the checkout view differ from git's history scan without any fsck message. A rejection
that a checkout shows at `<review dir>/veto.md` is ACCEPTED. The supplement's reason for not adopting a
pathspec-independent scan, and its "checkout view" framing, are therefore wrong.**
* **Location:**
  * `lx_platform.py:1249–1283` (`_historical_review_blobs`: reads symlink entries as their target text);
  * `:1321–1374` (`_acceptances`: HEAD files read via `cat-file blob`, so a symlink is its target text);
  * supplement r67 N1 row and §2 ("a history other than the one a checkout shows");
  * test `:1564` docstring.
* **Evidence** (`probes68_out.json`, same at 2f39e9f4):
  * `symlink_review_file_at_head_to_outside_rejection`: ACCEPTED, while a checkout of HEAD reads `<sha> REJECTED` at
    the review path.
  * `symlink_review_file_deleted_in_history`: ACCEPTED.
  * `symlinked_review_dir_in_history` and `symlinked_ancestor_dir_in_history`: ACCEPTED.
  * Strict fsck rc 0 in all four.
* **Scope:**
  * Pre-existing. Not reachable for a rejection that was ever committed as a regular file under the review directory:
    the history scan finds that blob.
  * Under the rule as written (git paths, blob contents), these rejections are outside the directory and are not
    vetoes. The defect is that the repair's rationale claims a view agreement that does not hold.
* **Correction:** either
  * (a) fail closed: treat any non-regular entry (120000, 160000) under the review directory, at HEAD or in any commit of
    the history, and any symlink at the review directory or one of its ancestors in any commit, as unavailable evidence;
    with a test and a mutant; or
  * (b) state in §2, the docstrings and the N1 row that the rule is defined on git tree paths and blob contents, that
    checkout-view equivalence is **not** established, and that symlinks are a known difference. Withdraw "strict fsck
    already refuses … what makes the two views differ".

**P2 — NOTE — INFO-class fsck messages pass `--strict`; "any warning refuses" is overstated.**
* **Evidence:** `probes68 info_class_bad_filemode_legit`: a `100664` entry prints `warning … badFilemode`, `fsck --full
  --strict` rc 0, ACCEPTED (same at 2f39e9f4).
* **Analysis:** git maps INFO to "warning" in its report and does not promote INFO under `--strict`. I know of no
  INFO-class message that hides a path from the scan (`canon_mode` normalises odd modes), but I tested only
  `badFilemode`.
* **Location:** supplement §2 refused list; `_history_complete` docstring `:1200–1201`.
* **Correction:** wording: "any message fsck reports as an error under `--strict` (WARN-class promoted; INFO-class
  messages such as `badFilemode` pass)". Optionally pin a legitimate INFO-class repository as accepted.

**P3 — MINOR — Harness: the N2 property is pinned on only one of the two `git log` calls (RA3 survives with a changed
outcome).**
* `test_review67_signature_program_never_runs` signs the attestation commit, which only `--find-object` selects.
* RA3 removes `log.showSignature=false` from the isolation and passes `--no-show-signature` to the `--find-object` call
  only. The suite passes (224).
* Outcome: a repository whose **acceptance** commit is signed, with local `log.showSignature=true` and `gpg.program`, runs
  the program under RA3 (`signature_program_ran: true`) and not under base. This is exactly the review-67 N2 attack
  path, on the `-S` call.
* **Correction:** sign the acceptance commit as well (or add a subtest), assert the marker is absent, and register RA3.

**P4 — NOTE — Harness: `--strict` is pinned only through `fullPathname` (RA2 survives), and `GIT_ATTR_NOSYSTEM` is
unpinned (RA4 survives, inert).**
* RA2 replaces `--strict` with `-c fsck.fullPathname=error`. The suite passes.
* Outcome: the zero-padded-mode history goes from refused to ACCEPTED, in the legitimate direction. I know no hiding
  construction for other WARN ids (`.`/`..`/`.git` entries are found by the scan; `emptyName` paths stay under the
  directory).
* The supplement nonetheless states `--strict` as the requirement.
* RA4 drops `GIT_ATTR_NOSYSTEM`. It cannot be observed without writing `/etc/gitattributes`.
* **Correction:** add one legitimate WARN-class subtest asserted refused (e.g. zero-padded mode or `nulInCommit`), so
  `--strict` itself is pinned. State RA4 as unpinned-by-construction, or pin it by fault injection on `_git_env()`.

**P5 — NOTE — Records residue.**
* Ledger 508's "the gate ran all three" (2288bec1) is unverifiable from committed evidence.
* Native run 38783320859 on 05caa00e (RV49–RV54 on git 2.55) was in progress at review time. It must be recorded in a
  later line, with its job-log SUMMARY and artifact digest.
* **Correction:** mark the 508 statement as coordinator-asserted; append the 38783320859 line.

**Counts:** BLOCKING 0 · MAJOR 0 · MINOR 2 (P1, P3) · NOTE 3 (P2, P4, P5); 5 new findings.

---

## 6. Reproduction and scratch files

* Suites: `suites/suite_python3.11.txt`, `suite_python3.12.txt`, `suite_python3.13.txt` (224 OK each).
* Review 66/67 probes re-run: `rerun67/probes67.py.txt`, `probes66.py.txt` and `probes66b.py.txt` (copies), with
  outputs `rerun67/*_at_05caa00e_out.json`.
* New probes: `probes68.py.txt`, with outputs `probes68_out.json` (05caa00e) and `probes68_at_2f39e9f4_out.json`.
* Mutants:
  * `reviewer68_mutants.py.txt` (derived from review 67's script), with `reviewer68_mutants_result.json` and
    `reviewer68_mutants_stdout.txt`;
  * `ra1_reclassify.py.txt` with `ra1_reclassify_out.json`.
* Records: `check_records68.py.txt` with `check_records68_out.json`; `reclassify68.py.txt` with
  `reclassify68_out.json`.

---

## 7. Reviewer mutants (brief 68)

**Method:**
* Each mutant is a copy of the 05caa00e `lx_platform.py` under `scratch/tmp/mut`.
* The pinned 224-test suite runs through the harness's own `run_suite` (`LX_PLATFORM_DIR`, `PYTHONWARNINGS=error`).
* Each mutant is classified with the harness's `classify_mutant` against a fresh PASS baseline (224).
* An outcome check runs base and mutant on one synthetic construction, each in a child interpreter.

**Result: 4 new mutants, 1 killed, 3 survived.**

```
### RA1 KILLED (ERROR under my first witness choice) | fsck-key refusal narrowed to the two keys the review-65 test uses
###   N1 construction + local fsck.fullPathname=ignore: base refused -> mutant ACCEPTED
-_LOCAL_CONFIG_REFUSED = re.compile(r"fsck\.|extensions\.partialclone$|remote\..*\.(promisor|partialclonefilter)$")
+_LOCAL_CONFIG_REFUSED = re.compile(r"fsck\.(skiplist|missingemail)$|extensions\.partialclone$|remote\..*\.(promisor|partialclonefilter)$")
    first run, witness test_review65_local_fsck_or_promisor_configuration_refuses: ERROR (NO_INTENDED_PROPERTY_ASSERTION);
    the only failing method is test_review66_configuration_in_includes_and_worktree_scope_refuses (its worktree subtest
    uses fsck.badTimezone). Re-run with that method added to the witnesses: KILLED (ra1_reclassify_out.json).

### RA2 SURVIVED | strict fsck narrowed to the one tested message
###   zero-padded-mode legitimate history: base refused -> mutant ACCEPTED (no hiding construction known)
-    return _git(repo_root, "fsck", "--full", "--strict", "--no-dangling", "--no-progress") is not None
+    return _git(repo_root, "-c", "fsck.fullPathname=error", "fsck", "--full", "--no-dangling", "--no-progress") is not None
    witnesses: test_review67_warning_class_tree_name_refuses

### RA3 SURVIVED | showSignature off only for the --find-object search; the -S search honours the repository
###   signed ACCEPTANCE commit + local log.showSignature=true + gpg.program marker:
###   base: ACCEPTED, program not run -> mutant: ACCEPTED, program RAN
-                  "-c", "log.showSignature=false",              # review 67 N2: no signature program from `git log`
-    blob_commits = _commits(repo_root, f"--find-object={blob}", "HEAD")
+    blob_commits = _commits(repo_root, "--no-show-signature", f"--find-object={blob}", "HEAD")
    witnesses: test_review67_signature_program_never_runs

### RA4 SURVIVED | system attributes file read (GIT_ATTR_NOSYSTEM dropped)
###   outcome inert here (/etc/gitattributes not writable; no driver configuration reaches git)
-    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM="1",
+    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
    witnesses: test_review67_global_attributes_file_is_not_read, test_review64_order_ignores_reading_configuration
```

For each survivor, the suite returned 0 with 224 tests.

**Registered mutants re-run singly** (not reviewer mutants), each against the same 224-test baseline:
* RV31, RV44 and RV49–RV54: all **KILLED**.
* The failing methods are exactly the registered witness, except RV31 (its witness plus the N1 test, which is expected
  because the whole precondition is removed).
