# Review: the coordinator's repairs of review 66's findings (combined Cell-308 development source, Cloud route r1, S4 changed branch)

* Reviewer: **reviewREVIEW66_REPAIR (fresh agent, brief 67)**
* Date: 2026-10-15 (UTC), about 15:05Z to 16:30Z.
* Pinned commit: **`2f39e9f451955629b72875bd965626a391621f8e`** (branch `codex/cell308-claude-r5-integration`, draft PR
  flaggielover/ReBaseGuard#3). Detached worktree `scratchpad/review67/tree_2f39e9f4`. `git status --porcelain` was
  empty at the end; I wrote nothing there.
* Delta: `774f2183..2f39e9f4`, three commits: 3adeabaa (brief 66), 2288bec1 (review 66 recorded, repairs), 2f39e9f4
  (local full-run record).
* NS = `level4/closure_proofs/p5y_k5_cell308_research/`, DEV = `NS/streams/CLOUD_R1_LINUX_DEV`. Line numbers refer to
  the 2f39e9f4 files.
* Scratch: `/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review67/` ("scratch").
  Probes ran on `scratch/base/lx_platform.py`, sha256 `470436ea…`, equal to the 2f39e9f4 blob and to ledger 503's
  binding. The 774f2183 comparison ran on `scratch/base774/lx_platform.py` (`26aca753…`, extracted from git). Scripts
  are stored as `*.py.txt`.
* Local git: **2.43.0** (Ubuntu build). Native runner git (job logs of runs 38739675256 and 38756465002): **2.55.0**.
* `new_target_evaluations = 0`. I ran no cell, drift, certificate, decoy, science module, qualification case or
  candidate code. I installed nothing and changed no setting (one side effect is disclosed in §1).

---

## 1. Exposure disclosure

**Opened:**
* Brief 67 in the shared checkout (the only file read there).
* In the pinned tree: the `774f2183..2f39e9f4` diffs of `lx_platform.py`, `test_lx_platform.py`, `run_mutants.py`,
  `test_mutation_harness.py`, the workflow and `BRIEF_INDEX.md`; `lx_platform.py` lines 1130–1540; the attestation
  fixtures and the review-65/66 tests in `tests/test_lx_platform.py` (lines 1010–1035, 1240–1260, 1320–1550);
  `run_mutants.py` (`PROPERTY_WITNESSES` tail, `classify_mutant`, `apply_mutation`, `validate_registry`); review 66
  as recorded; supplement r66; ledger lines 500–504; the delta's commit messages.
* The compressed local record `LOCAL_FULL_HARNESS_PY312_2288BEC1.json.gz`: decompressed in memory; header, input
  hashes, status counts and every mutant row (edits, witnesses, suite failure names) read. Synthetic test output only.
* `scratchpad/review66/` originals, for the byte comparison of Q4, and review 66's `probes66*.py.txt` /
  `reviewer66_mutants.py.txt` (copied to `scratch/rerun66/` and executed there). I did not open
  `review66/tree_774f2183/` or `review66/tmp/` (names seen in a listing).
* `scratchpad/review65/job_116337943534.log` (the M6 file): read as bytes for its size, sha256 and the presence of
  URL / signature markers only. The URL was not printed, copied or recorded.

**Name-level contact:** the scratchpad root listing (`MUTANTS_RUN_R*.json`, `fix65`, `fix66`, `fix_shallow`,
`fsck_probe`, `gate.txt`, `gitprobe*`, `inv_check.json`, `lazy_probe`, `ldet`, `mut*.log`, `native-r3`, `r65files.txt`,
`r66files.txt`, `rev5`, `review59`–`review67`, `rv`, `scan*.json`, `shallow_probe`). Nothing else opened. `git diff
--name-only 774f2183..2f39e9f4` contains no audit / interruption / mb_r1 / 309 / exposure-disclosure path.

**Shared object store:** the pinned worktree's git dir lives in the shared repository; every git read of the pinned
tree went through it (objects only), plus one `git rev-parse --is-shallow-repository` on the pinned worktree (answer
`true`, used for the supplement's last sentence). No `fsck`, no `git` command in the shared checkout.

**GitHub (read-only, MCP):** the branch's run list; jobs and artifacts of runs 38739675256, 38725820509 and
38756465002; the last 45–60 lines of jobs 116437795163 and 116496102737 (SUMMARY lines, artifact digests, git version).

**Live calls:** none against the real repository. Every `attestation_valid` / `_history_complete` call passed
`repo_root=<synthetic repository under scratch/tmp>` with `machine_identity` patched. I removed from my probe script,
before running it, a `preflight` call that would have defaulted to `_repository_root()` of the scratch copy.

**Side effect (disclosed):** in one manual shell check (`scratch/tmp/legitsig`, a synthetic repository with a fake
`gpgsig` header and local `log.showSignature=true`, default `gpg.program`), git ran the system `gpg` with
`HOME=/root`, and gpg **created `/root/.gnupg/` (with an empty `pubring.kbx`)**. My attempt to remove it was refused
by the session's permission system, so it remains. It holds no key material from any repository. The same mechanism
is finding N2/N3.

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
development-layer review. Supplement r66, supplement r65, supplement r64, erratum E1, the L-DET addendum and every D-*
decision stay PROPOSED / undecided. Only the formal route review, a fresh S12 re-rating and the owner can accept,
reject or put anything into force.

**REPAIR = REPAIRED_WITH_DEFECTS.**
* Repaired: every construction review 66 reported as ACCEPTED is now refused: forged Bloom filter (local, alternate,
  split chain), fsmonitor rewrite, `fsck.*` key through an include. No fsmonitor command runs. Keys in includes,
  `includeIf` (gitdir, onbranch), nested includes and the worktree scope (main and linked worktree) refuse.
* **N1 (MAJOR, regression):** removing `--strict` re-opens a hiding construction. A deleted rejection stored under a
  tree entry whose *name* is `<review dir>/veto.md` (fsck `fullPathname`, a warning) is invisible to the
  pathspec-limited history scan. A checkout of that commit puts the rejection at `<review dir>/veto.md`. Default fsck
  exits 0, and the attestation is **ACCEPTED** at 2f39e9f4. It was refused at 774f2183 (strict fsck rc 1). This
  contradicts "`--strict` … hides nothing".
* **N2 (MAJOR, pre-existing, same class as M2):** `git log` honours the repository's `log.showSignature`, so a
  repository-configured `gpg.program` (or `gpg.ssh.program`) runs inside `_ordered`, after fsck. Such a command can
  rewrite a verified object and turn an order-rule refusal into **ACCEPTED**. Reproduced at 774f2183 and 2f39e9f4.
  `-c log.showSignature=false` closes it.

**HARNESS = SOUND_WITH_DEFECTS.**
* RV23/RV31/RV33 (re-anchored), RV39 (narrowed) and RV43–RV48 are each KILLED by their own witness alone (RV39 also by
  RV32's witness, as expected). 181/182 is right.
* Defects (N5): 3 of my 6 new mutants survive with a changed or weakened outcome (RZ1, RZ4, RZ5); RZ6 survives
  outcome-equivalent. The CDAT test no longer pins that the graph is unread. Nothing pins N1's or N2's property.

**RECORDS = ACCURATE_WITH_CORRECTIONS.**
* All 56 sha256 bindings in ledger 500–504 recompute. The compressed record, its inputs and all 181 rows
  re-classify. Review 66 and its 42 scratch files are byte-identical to the originals. M6's stated reason is true.
  No committed file in the delta contains a signed URL or credential.
* Corrections: supplement r66 states things the code does not do (N1, N2, N4). One code docstring and one test
  docstring are stale (N6). Native run 38756465002 on 2f39e9f4 finished **success, 181/181** after the commit and is
  not yet in the ledger (expected; N6).

---

## 3. Review 66's findings (Q1)

"now" = 2f39e9f4. Evidence files are in scratch: `rerun66/` (review 66's probes re-run unchanged), `probes67*`,
`reviewer67_mutants*`, `check_records67*`, `reclassify67*`.

| finding (review 66) | disposition (supplement r66) | verified at 2f39e9f4 | status |
|---|---|---|---|
| M1 MAJOR: forged changed-path Bloom filters | `-c core.commitGraph=false` in `_GIT_ISOLATION` (`:1158–1160`); test `test_review66_forged_bloom_filter_is_never_read`; RV43 | Code matches. Every `_git` call and `_strictly_after` (`:1213`) carry it. `rerun66/probes66_at_2f39e9f4_out.json`: `bloom_local`, `bloom_alternate` and `bloom_split_chain` are all **refused (HISTORICAL)**, though fsck and `commit-graph verify` still exit 0 on the forged files. `rev_list_reviews` in the probe's own uncontrolled reader still loses the commit, so the fix is the isolation. The native run on 2f39e9f4 (git 2.55) KILLED RV43, so 2.55 also reads unverified Bloom data when allowed: M1 was relevant natively, and the fix is exercised there. The CDAT case is now refused by HISTORICAL (my RZ1 base outcome), as the supplement says. **But** the CDAT test asserts refusal only: re-enabling the graph's parent data (RZ1) survives (N5). | **RESOLVED** (pinning gap N5) |
| M2 MAJOR: fsck runs `core.fsmonitor` | `-c core.fsmonitor=false`; test; RV44 | Code matches. `fsmonitor_valid_repo`: marker **not written**, valid repository ACCEPTED. `fsmonitor_rewrites_object_during_fsck`: hook ran 0 times, **refused (HISTORICAL)**. RV44 is killed by its witness alone. "Other index-time commands were not found in fsck's path" holds as far as I checked. **But** the class review 66 described (a command configured by the repository runs during the check and rewrites a verified object) is still open through `git log` → `log.showSignature` → `gpg.program` (N2). | **RESOLVED** as reported. The class is open (N2). |
| M3 MINOR: keys in includes / `config.worktree` | `config --includes --name-only --list -z` (`:1201`); test; RV48 | `probes67 config_listing_scopes`: `includeIf.gitdir`, `includeIf.onbranch`, a nested include (promisor), a linked worktree's `config.worktree` (`fsck.*`), `remote.ORIGIN.promisor` and `extensions.partialClone` alone all give `_history_complete` **False**. The main worktree of the linked case stays valid (correct). Review 66's `fsck_key_in_include` and `partial_clone_keys_in_include` / `_in_worktree_config` are now refused, and no configured command ran. System and global configuration are nulled, so "every scope git reads" is accurate for configuration (not for attributes: N4). | **RESOLVED** |
| M4 MINOR: RY1, RY2, RY3, RY5 unpinned | RY1 → RV45, RY3 → RV46, RY5 → RV47 with direct tests; RV39 narrowed; RY2: `--strict` removed | RY1, RY3 and RY5 re-run unchanged now **fail exactly the new witnesses** (RV45 / RV46 / RV47 tests). They classify ERROR in my run only because I passed review 66's old witness names. Their edits are byte-identical to RV45–RV47, which the record and my runs show KILLED by their own witness alone. Outcomes: RY3 still turns a 120000 attestation into ACCEPTED, and RY5 turns refused into ACCEPTED, so the pins are meaningful. RY4 re-anchored (RY4b) is KILLED. **RY2's disposition is wrong:** "`--strict` only promotes warnings … no hiding construction depends on it" is refuted by N1. | **PARTIALLY RESOLVED** (N1) |
| M5 NOTE: newly refused legitimate repositories | supplement §2 list | The items listed reproduce: shallow; partial / promisor; `fsck.*` key; old-history fsck error (`strict_warning_legit`: badTimezone, still refused); index naming a missing object (`index_only_breakage` rc 2, refused); `./att/HOST.json` refused. The zero-padded-mode history is now accepted (`zero_padded_mode_legit` valid). **Missing** from the list (N3): a repository owned by another uid (dubious ownership, refused as "attestation not committed at HEAD", because `safe.directory` is read only from the nulled global / system scopes), and a repository with local `log.showSignature=true` whose searched commits are signed. | **STATED**, incomplete (N3). Acceptable to carry once completed. |
| M6 MINOR: ledger 495 binds an uncommitted file | stays uncommitted; ledger 502 states BOUND_BUT_NOT_COMMITTED | The original `scratchpad/review65/job_116337943534.log` is **522 bytes**, sha256 `fed307d6…` (= binding), not a job log (no runner markers), and contains one https URL carrying `sig=` / `se=` parameters. It is absent at 2f39e9f4. Ledger 502 says exactly this. | **RESOLVED (STATED)**. Acceptable to carry: the binding is verifiable only from the coordinator's scratchpad. |
| M7 NOTE: wording | label, supplement, test docstring, ledger artifact | Fixed: the RV origin label is "Claude reviews 63–66" (record `origins`); the partial-clone test docstring is narrowed; ledger 502 carries run 38725820509's artifact 11969136626 / `3be305c4…` (verified via API). **Not fixed:** the `_git_env` docstring (`:1168`) still says "git >= 2.44 honours it". | **PARTIALLY RESOLVED** (N6) |

**Supplement r66 §2: not accurate as written.**
* The three conditions are an exact description of `_history_complete` (`:1199–1205`).
* "Under the isolation … global and system configuration and **attributes** are not read": **false for attributes.**
  `$HOME/.config/git/attributes` is read (`probes67 global_attributes_file_read_via_HOME`: `check-attr` under `_git_env`
  reports a global `diff=` attribute). This is inert today, but the statement is wrong (N4).
* "**This establishes** that … git's own verification finds the reading repository's object store complete and
  consistent": this holds only at **default** severity. Warning-class malformations such as `fullPathname` pass, and they
  hide history from the pathspec-limited scans (N1).
* "the history the scans walk comes from the commit objects themselves": true for parents (graph, grafts, replace
  are off). It is not true that what the scans see equals what a checkout shows (N1).
* "No fsmonitor command runs" is true, but the list omits that `git log` runs repository-configured signature
  programs (N2). The M2 residual ("any process with write access …") does not cover a command **the check itself
  launches**.
* The refused-repository list is incomplete (N3).

---

## 4. Answers Q2–Q5

### Q2 — Adversarial fail-closed audit

**Suites:** `python3.1x -B -W error::ResourceWarning -m unittest discover -s tests -v` gives **221 tests OK** on 3.11,
3.12 and 3.13 (`suite_python3.1x.txt`).

**Review 66's probes, re-run unchanged** (`rerun66/probes66_at_2f39e9f4_out.json`, `probes66b_at_2f39e9f4_out.json`):
* Every review-66 ACCEPTED row is now refused: `bloom_local`, `bloom_alternate`, `bloom_split_chain`,
  `fsmonitor_rewrites_object_during_fsck` and `fsck_key_in_include`.
* Review 66's configured-command rows: `fsmonitor_valid_repo` marker null; `partial_clone_keys_in_include`
  `_history_complete` False, no command; worktree-config case refused, no command.
* Changes in the legitimate direction: `zero_padded_mode_legit` refused → **valid** (stated). `./att/HOST.json` still
  refused (stated). Index-only breakage still refused (stated).
* `env_allowlist`, `use_replace_refs_local`, `symlink_attestation` and `skiplist_in_include_rewritten_blob`: unchanged,
  refused.

**New probes** (`probes67.py.txt`; outputs `probes67_out.json` at 2f39e9f4, `probes67_at_774f2183_out.json`, and the
control `probes67_out_showsig_off.json`, which adds `-c log.showSignature=false` in memory):

| construction | 2f39e9f4 | 774f2183 | finding |
|---|---|---|---|
| att → C2: root tree entry **named** `<review dir>/veto.md` (blob `<sha> REJECTED`), written with `hash-object --literally` → C3 removes it → acceptance | fsck default rc **0** (warning `fullPathname`); `rev-list --full-history HEAD -- <review dir>` lists only the acceptance commit; `ls-tree -r C2 -- <review dir>` empty; `ls-tree -r C2` (no pathspec) lists `<review dir>/veto.md`; `git worktree add C2` puts the rejection file at `<review dir>/veto.md`; **ACCEPTED** | refused (strict fsck rc 1, "history completeness") | **N1** |
| same with the entry `reviews/veto.md` inside the review directory's parent tree | **ACCEPTED** (fsck rc 0) | refused | **N1** |
| rejection under `reviews/./`, `reviews/../`, `reviews/.git/` (hasDot / hasDotdot / hasDotgit, warnings) | refused (HISTORICAL; the scan finds them) | refused | — |
| valid repository; the attestation commit carries a `gpgsig` header; local `log.showSignature=true`, `gpg.program=<script>` that prints GOODSIG status lines and nothing on stderr | ACCEPTED (correct outcome), but **the script ran** (once, in `_ordered`'s `log --find-object`). Not during `_history_complete`. Clean stdout, so `_commits` parses. | same | **N2** |
| order-rule case: C0 adds `notes/quote.md` containing the accepting line (quote **before** the blob), C1 (signed) adds the attestation, C2 adds the acceptance. Without the gpg config: refused (order rule). With the script also overwriting C0's quote blob with a benign object | **ACCEPTED.** fsck passed before; the rewrite happens inside `log --find-object`; the later `log -S` no longer sees C0. A later fsck gives rc 3 (hash-path mismatch). | **ACCEPTED** (same) | **N2** |
| same two cases with `-c log.showSignature=false` in the isolation (control) | refused; script ran 0 times | — | N2 fix |
| `gpg.format` left default; ssh-signature header; `gpg.ssh.program=<script>` | script **ran** | ran | N2 |
| legitimate repo owned by uid 65534, checked as uid 0 | refused, reason "attestation not committed at HEAD" (git: dubious ownership, rc 128) | same | N3 |
| global attributes file under `$HOME/.config/git/attributes` | read by git under `_git_env` | same | N4 |
| config scopes: `includeIf.gitdir`, `includeIf.onbranch`, nested include, linked worktree `config.worktree`, upper-case subsection, `extensions.partialClone` alone | all refused ("history completeness") | n/a | M3 resolved |
| clone shapes from a rejected-then-deleted source: `--no-local` full, `--depth 2`, depth 2 then `fetch --unshallow`, `--shared`, `--reference --dissociate`, `--filter=tree:0`, `--mirror` (bare), `--single-branch` | shallow and filter: refused (completeness); every full shape: refused (HISTORICAL); no shape accepted | — | — |
| exception inputs: NUL in path, `--output=…` path, lone surrogate, `:(glob)` magic | refused, no exception | — | — |

**Classes:**
* **ACCEPTED where the stated rule refuses:**
  * N1: warning-class tree names that the pathspec walk does not match (regression from removing `--strict`).
  * N2: order-rule bypass through a signature program launched by `git log` (pre-existing).
* **A repository-configured command runs during the check:**
  * N2: `gpg.program` / `gpg.ssh.program` (and by the same code path `gpg.x509.program`) whenever
    `log.showSignature` is set locally and a commit selected by `--find-object` / `-S` carries a `gpgsig` or mergetag.
  * With the default program, the system `gpg` runs and writes into the caller's `$HOME` (§1 side effect).
  * fsmonitor and lazy fetch: none.
* **Exception escaping `attestation_valid` / `preflight`:** none found (malformed refs, `_git` failures, deep JSON,
  unreadable config listing).
* **Legitimate full-clone cases newly refused and not stated:**
  * None new in the delta. The pre-existing unstated ones (dubious ownership; local `log.showSignature` with signed
    commits) are N3.
  * Removing `--strict` and listing the global scope introduced no new refusals that I found. Global and system
    configuration stay nulled.
* **Regression of a property that held at 774f2183:** N1 (warning-class trees refused). No other: every
  probes66/probes67 construction refused at 774f2183 is refused at 2f39e9f4, except N1 and the deliberate
  zero-padded-mode case.
* **Native git 2.55:** N1 and N2 were measured on 2.43.0 only. The fsck message levels and the `log.showSignature`
  behaviour on 2.55 are **UNVERIFIED** (I have no 2.55 here).

**NOTE — can "the reading repository's own files make git report a false history" be closed in-repository? (N7)**
No, in my assessment. The evidence:
1. **Each closure has been one mechanism, and each review finds another.** Review 64 found grafts and replace refs;
   review 65 the CDAT graph and rewritten objects; review 66 Bloom filters, fsmonitor and includes; this review a
   warning-class tree name (N1) and a signature program (N2).
2. **The check runs git, and git reads the repository's configuration.** Any code path that executes a configured
   command, or any process with write access, can change objects after `git fsck`. git does not re-hash objects on
   read (N2's rewritten blob is served by `log -S`; review 66's by `cat-file`).
3. **What git's pathspec walk sees is not what checkout or a human sees** for malformed but warning-only trees (N1).
4. **A consistent rewrite with new commit ids passes every in-repository check by construction.** Nothing in the
   repository pins which history is the reviewed one.

An in-repository check could only shrink this to "consistent rewrite". To do that, the reader would itself need to:
verify every object's hash from a HEAD id recorded **outside** the repository; parse trees and commits without git's
configuration; and run no repository-configured code. The anchor would then be that external id, which is the
ledger binding. The class therefore must rest on D-HOST-LIFETIME item (i) (ledger binding of the reviewed commit and
attestation blob) and item (ii) (a non-coordinator reviewer). The in-repository precondition is defence in depth, not
a closure. The supplement should say so instead of "This establishes …".

**Mutants:** 6 new (RZ1–RZ6), **2 killed, 4 survived** (§7).

### Q3 — Harness integrity

* **RV23 (re-anchored)** drops `"-c", "log.showRoot=true"` and keeps the new lines, so it is the same weakening. It is
  killed by `test_review64_order_ignores_reading_configuration` alone (my run and the record).
* **RV31 (re-anchored, re-described)** turns fsck into `return True`. The witness rewrites a real loose blob and
  asserts the completeness reason, so it is direct. Killed alone.
* **RV33 (re-anchored)** drops `--no-replace-objects` only. Killed alone by
  `test_review65_replace_refs_and_grafts_are_ignored`. Direct (real replace graft).
* **RV39 (narrowed)** is now the key regex only. The witness `test_review65_partial_clone_runs_no_configured_command`
  asserts the "history completeness" reason, so it witnesses the precondition, not the configured command. RV39 is
  also caught by RV32's witness, which is expected because the promisor subtests fail. The description is accurate.
* **RV43–RV48:** each is KILLED in my single runs against a fresh 221-test baseline, and in the record, with **only
  its own witness failing**. Reading the tests:
  * RV43: a real `--changed-paths` graph with the rejection commit's BDAT bytes zeroed and the checksum recomputed;
    asserts HISTORICAL; positive control with an honest Bloom graph. Direct.
  * RV44: a real repository-local `core.fsmonitor` overriding the fixture's `false`; marker asserted absent. Direct.
  * RV45: a real blob:none clone with a configured upload-pack; `_history_complete` patched True (fault injection for
    the precondition only); marker asserted absent. Direct for the lazy-fetch block.
  * RV46: a real 120000 entry whose target text is the attestation. Direct.
  * RV47: fault injection (`_git("config", …)` → None). Stated as such; acceptable.
  * RV48: a real `include.path` and a real `--worktree` key. Direct. RZ2 (`--no-includes`) and RZ3 (no `-z`) are also
    killed by it.
* **Gaps (N5):**
  * The CDAT forged-graph assertion lost its reason check (test file `:1371`). Reading the graph's parent data again (RZ1) is
    not detected, because fsck's `commit-graph verify` then refuses the forgery with a different reason.
  * `extensions.partialClone` alone (RZ4) and promisor keys of a non-`origin` remote (RZ5) are not pinned. RZ4 turns a
    refusal into ACCEPTED.
  * There is no test for a warning-class tree (N1) or for `log.showSignature` (N2). Every fixture repository sets no
    `log.showSignature`, so the suite cannot observe N2.
* **Counts:**
  * `MUTANT_GROUP_SIZES` sums to 181 (RV 48); `validate_registry()` = 181 is asserted in `test_mutation_harness.py`.
  * The workflow asserts `== 181` and `len(suites) == 182` (baseline + 181).
  * The 2288bec1 record has 181 rows and 221-test suites.
  * The native run on 2f39e9f4 printed `SUMMARY … expected_test_count 221, killed 181, total 181, pass true`.
  * **Right.**

### Q4 — Records

* **Ledger:** 774f2183 (499 lines) → 3adeabaa (500) → 2288bec1 (503) → 2f39e9f4 (504). Each is a byte prefix of the
  next (append-only verified).
* **Bindings** (`check_records67.py.txt`, `check_records67_out.json`): **56 bindings** recompute both at the
  introducing commit and at 2f39e9f4, with **0 problems**:
  * 500: brief 66 `001b3280…`;
  * 501: review 66 `8dd1b208…` and 42 scratch files;
  * 503: 10 inputs and supplement r66 `bd13726d…`;
  * 504: the gz record `72903cd8…`.
* **Compressed record:**
  * It gunzips to `b58144be…` (= ledger 504's `uncompressed_sha256`). Header: mtime 0, flags 0, XFL 2 (= `-9 -n`).
  * The 10 `input_sha256` entries equal `input_sha256_after`, ledger 503 and the blobs at 2288bec1 and at 2f39e9f4.
  * Baseline 221 PASS; 181/181 KILLED; `utc` 14:58:26Z, before the 2f39e9f4 run was created (15:00:21Z). No native run
    exists for 2288bec1, so "before any push" is consistent.
  * Re-classifying all 181 rows with the pinned `classify_mutant` reproduces every status. Edits and witnesses equal
    the registry, and every `mutated_lx_platform_sha256` recomputes (`reclassify67_out.json`, `problems: []`).
  * `source_commit` is null; the binding rests on the input hashes, which hold.
* **Review 66 and scratch:**
  * `REVIEW_REVIEW65_REPAIR_DELTA.md` and all 42 committed scratch files are byte-identical to the
    `scratchpad/review66` originals (`.py` → `.py.txt` for the five `lx_platform.py` copies).
  * Not committed: three `__pycache__/*.pyc`, `tmp/` and `tree_774f2183/`, all covered by ledger 501's omission
    statement. The M6 file is handled by ledger 502 (§3).
* **Signed URLs / credentials:** a scan of every file added or modified in the delta (the gz decompressed) for
  `sig=`, `se=`, `sv=`, `X-Amz-`, GitHub token prefixes, `Authorization:`, `Bearer`, `api_key`, `password`, `token=`
  and blob-storage hosts gives **0 hits**. The only URLs are two pre-existing support.claude.com links in old ledger
  lines.
* **Modified files** (`git diff --name-status 774f2183..2f39e9f4`): 46 A, 7 M. The 7 M are the 5 tested inputs, the
  ledger (append-only) and `BRIEF_INDEX.md` (one appended row for brief 66). No reviewed or historical review,
  governance or audit file changed. Supplement r65 is not edited.
* **Native runs since 9b6347cb:**
  * Recorded: 38689564567, 38692293195, 38694984232, 38709764443, 38709761027, 38714823675, 38725820509 (now with
    artifact 11969136626 / `3be305c4…`, verified), and **38739675256** (774f2183) in ledger 502.
  * For 38739675256 I verified: success; job log `SUMMARY … 215, killed 175, total 175, pass true`; workflow `== 175`,
    `176`; artifact 11977920148, digest `sha256:bdb1974b…`. All match ledger 502.
  * **38756465002 (2f39e9f4):** completed **success** at 15:31Z. `SUMMARY … expected_test_count 221, killed 181,
    total 181, pass true`; git 2.55.0; artifact **11986430317**, digest `sha256:9b2c99ae10d30dd260e7a8d1b3bbf49e6a5ed676ed64d0b944387f8827894314`.
    Ledger 504 says PENDING, which is correct for the commit itself. It must be recorded in a later line (N6).

### Q5 — Overstatement

1. **Supplement r66 M4 row, ledger 503 ("`--strict` removed"), the `_history_complete` docstring (`:1198`) and the
   2288bec1 message:** "`--strict` only promotes warnings … no hiding construction depends on it" / "hides nothing".
   **False** (N1).
2. **Supplement §2 "This establishes that … git's own verification finds the object store complete and consistent":**
   true only at default severity; it does not establish that the scans see what a checkout shows (N1). The claim is
   also limited by commands that git itself launches during the reads (N2).
3. **Supplement §2 "global and system configuration and attributes are not read":** global attributes are read (N4).
4. **Supplement M2 row:** "Other index-time commands were not found in fsck's path" is literally true. It reads as a
   completed audit of configured commands, but `git log`'s signature path was not covered (N2). The stated residual
   names only "any process with write access", not a command launched by the check.
5. **2288bec1 message "Local: 221 tests OK on CPython 3.11/3.12/3.13"** vs ledger 503 "221 OK on CPython 3.12 …;
   3.11 / 3.13 in this commit's gate". The two records describe the evidence differently. I reproduced 221 OK on all
   three, so the substance holds (N6).
6. **Not overstated:**
   * "181/181 KILLED", "baseline 221", "inputs equal 2288bec1's blobs", "before any push" (re-classified / verified);
   * ledger 502's M6 description (verified as far as size, hash and URL markers);
   * ledger 502's 774f2183 native-run line (verified via API);
   * "The repository checked out in this session is shallow" (the shared git dir reports `true`).

---

## 5. New findings

**N1 — MAJOR — Removing `--strict` re-opens a hiding construction: a deleted rejection under a `fullPathname` tree
entry is invisible to the history scan and the attestation is ACCEPTED (regression from 774f2183).**
* **Location:**
  * `lx_platform.py:1205` (`fsck --full` without `--strict`) and `:1198` (docstring);
  * `:1247` and `:1252` (`_historical_review_blobs`: `rev-list --full-history HEAD -- <dir>` and
    `ls-tree -r -z <c> -- <dir>`, both pathspec-limited);
  * supplement r66 M4 row and §2; ledger 503; the 2288bec1 message.
* **Evidence** (`probes67_out.json` `full_pathname_entry_hides_deleted_rejection` and
  `full_pathname_entry_in_review_dir_tree`; `probes67_at_774f2183_out.json`):
  * Construction: a root tree with `att/` and a blob entry named
    `level4/closure_proofs/p5y_k5_cell308_research/reviews/veto.md`, then removed, then a valid acceptance.
  * fsck: default rc 0 (`warning … fullPathname`); `--strict` rc 1.
  * The scans miss commit C2. `ls-tree -r C2` without a pathspec, and a checkout of C2, show the rejection at
    `<review dir>/veto.md` with its `REJECTED` text.
  * Result: **ACCEPTED** at 2f39e9f4, **refused** at 774f2183.
  * The variant inside the review directory's parent tree behaves the same.
  * `.` / `..` / `.git` entries are found by the scan (refused).
* **Correction:**
  * Restore `--strict` (stating the zero-padded-mode denial), or at minimum force `-c fsck.fullPathname=error`
    (also `emptyName`, `hasDot*`) in the isolation.
  * Better: make the history scan independent of pathspec matching. List every commit's full tree (`ls-tree -r -z`
    without a pathspec, `rev-list --full-history HEAD` without a path) and select paths by normalised prefix in Python.
  * Add a test and a mutant.
  * Retract "hides nothing" in the docstring, supplement and ledger wording.
  * Measure on git 2.55.

**N2 — MAJOR — `git log` runs repository-configured signature programs (`log.showSignature` + `gpg.program` /
`gpg.ssh.program`) inside the check, after fsck; such a program can rewrite a verified object and the order rule
ACCEPTS a quote-before-blob history.**
* **Location:** `_GIT_ISOLATION` (`:1158–1160`: no `-c log.showSignature=false`); `_commits` (`:1371`, `git log`);
  `_ordered` (`:1398–1399`); supplement r66 M2 row and §2.
* **Evidence** (`probes67_out.json`):
  * `gpg_program_runs_on_valid_repo`: the script ran once, the outcome ACCEPTED (correct), and stdout stayed clean.
  * `gpg_program_rewrites_quote_order_rule`: refused without the config, **ACCEPTED** with it. The rewrite happens
    during `log --find-object`, so the following `log -S` misses C0. A later fsck gives rc 3.
  * `gpg_ssh_program_runs`: the program ran.
  * Identical at 774f2183, so this is pre-existing, not a regression.
  * Control `-c log.showSignature=false`: refused, the program ran 0 times (`probes67_out_showsig_off.json`).
  * Only `_ordered` is affected: `rev-list`, `ls-tree`, `cat-file`, `merge-base` and `fsck` do not read
    `log.showSignature`, so the veto scan is not reachable this way.
* **Severity:** this is the M2 attacker and the M2 effect (a configured command defeats a stated rule after fsck), on a
  path the M2 audit did not cover.
* **Correction:**
  * Add `-c log.showSignature=false` to the isolation (or `--no-show-signature` on every `log` call).
  * Audit every configuration key `git log` reads (`log.*`, `gpg.*`, `mailmap.*`, `notes.*`, `diff.*`).
  * Add a test with a signed commit and a marker-writing `gpg.program`, and a mutant.
  * State in §2 that a command launched by the check is excluded only for the named mechanisms.

**N3 — MINOR — Supplement §2's refused-repository list is incomplete.**
* **Evidence** (`probes67_out.json` `dubious_ownership_legit_repo`; manual check in `scratch/tmp/legitsig`):
  * A legitimate repository owned by another uid is refused (git: "detected dubious ownership", rc 128). The reason
    reported is the misleading "attestation not committed at HEAD". `safe.directory` is honoured only from the global
    and system scopes, which the isolation nulls. This is common for CI and container checkouts.
  * A legitimate repository with local `log.showSignature=true` and a signed attestation or acceptance commit is
    refused, because gpg's output reaches `git log`'s stdout and `_commits` rejects non-hex tokens. The system `gpg`
    also runs and writes into the caller's `$HOME`.
* **Correction:**
  * List both in §2 and in the D-HOST-LIFETIME procedure.
  * Consider passing `-c safe.directory=<repo_root>` explicitly, or reporting an ownership failure distinctly.
  * N2's fix removes the second item.

**N4 — NOTE — Supplement §2 says global attributes are not read; they are.**
* `GIT_ATTR_NOSYSTEM` covers only the system file. `core.attributesFile` defaults to `$XDG_CONFIG_HOME` or
  `$HOME/.config/git/attributes`, and `HOME` is kept.
* `probes67 global_attributes_file_read_via_HOME`: `check-attr` under `_git_env` reports `diff: probe67`.
* It is inert today: driver configuration comes from nulled scopes, and `--no-textconv` / `--no-ext-diff` are passed.
* **Correction:** add `-c core.attributesFile=/dev/null` to the isolation, or restate.

**N5 — MINOR — Harness: three elements of the repaired precondition are unpinned (RZ1, RZ4, RZ5 survive).**
* RZ1: the graph's parent data is read again (`commitGraph.readChangedPaths=false` in place of
  `core.commitGraph=false`). **SURVIVED.** CDAT forgery outcome: refused (HISTORICAL) → refused ("history
  completeness"). The property "the commit-graph is never read" is unpinned because the CDAT test (test file `:1371`) asserts
  refusal only.
* RZ4: `extensions.partialClone` dropped from the regex. **SURVIVED.** A repository whose only promisor key is
  `extensions.partialClone=origin` goes from refused to **ACCEPTED**.
* RZ5: promisor keys refused only for `origin`. **SURVIVED.** A blob:none clone with `-o upstream` passes the
  precondition. The final result is still refused (unreadable history), and no command ran.
* No witness exists for N1 or N2.
* **Correction:** restore the reason assertion on the CDAT case (HISTORICAL). Add subtests for
  `extensions.partialClone` and a non-`origin` remote. Add tests and mutants for N1 and N2. Register them.

**N6 — NOTE — Record and wording residue.**
* `_git_env` docstring (`:1168`) still says "git >= 2.44 honours it" (M7 corrected only the supplement).
* `test_review65_forged_graph_and_rewritten_object_refuse` docstring (test file `:1363`) still says "a full strict
  fsck is a precondition".
* The 2288bec1 message ("221 tests OK on CPython 3.11/3.12/3.13") and ledger 503 ("3.12; 3.11 / 3.13 in this
  commit's gate") describe the local evidence differently.
* Native run 38756465002 (2f39e9f4) finished success, 181/181, artifact 11986430317 / `sha256:9b2c99ae…`. It is not
  yet recorded (it cannot be in the commit it tests).
* **Correction:** wording; append a ledger line for run 38756465002.

**N7 — NOTE — The class "the reading repository's own files make git report a false history" cannot be closed by
in-repository checks** (evidence and reasoning in §4 Q2). It must rest on the carried ledger binding (D-HOST-LIFETIME
item (i)) and a non-coordinator reviewer (item (ii)). **Correction:** state this in supplement §2 in place of
"This establishes …". Treat `_history_complete` as defence in depth.

**Counts:** BLOCKING 0 · MAJOR 2 (N1, N2) · MINOR 2 (N3, N5) · NOTE 3 (N4, N6, N7); 7 new findings.

---

## 6. Reproduction and scratch files

* Suites: `suite_python3.11.txt`, `suite_python3.12.txt`, `suite_python3.13.txt` (221 OK each).
* Review 66's probes re-run: `rerun66/probes66.py.txt`, `rerun66/probes66b.py.txt` (copies), with outputs
  `rerun66/probes66_at_2f39e9f4_out.json` and `rerun66/probes66b_at_2f39e9f4_out.json`.
* New probes: `probes67.py.txt`, with outputs `probes67_out.json` (2f39e9f4), `probes67_at_774f2183_out.json` and
  `probes67_out_showsig_off.json` (control).
* Mutants: `reviewer67_mutants.py.txt` (derived from review 66's script), `reviewer67_mutants_result.json`,
  `reviewer67_mutants_stdout.txt`.
* Records: `check_records67.py.txt` / `check_records67_out.json`; `reclassify67.py.txt` / `reclassify67_out.json`.
* Manual shell checks (no scripts kept): `tmp/sigprobe` (gpg.program runs under the isolation) and `tmp/legitsig` (§1
  side effect).

---

## 7. Reviewer mutants (brief 67)

**Method:**
* Each mutant is a copy of the 2f39e9f4 `lx_platform.py` under `scratch/tmp/mut`.
* The pinned 221-test suite runs through the harness's own `run_suite` (`LX_PLATFORM_DIR`, `PYTHONWARNINGS=error`).
* Each mutant is classified by the harness's `classify_mutant` against a fresh PASS baseline (221), with the
  witnesses named below.
* An outcome check runs base and mutant on one synthetic construction, each in a child interpreter.

**Result: 6 new mutants, 2 killed, 4 survived** (RZ1, RZ4 and RZ5 with a changed or weakened outcome; RZ6
outcome-equivalent on its construction).

```
### RZ1 SURVIVED | the commit-graph's parent data is read again (only Bloom filters off)
###   forged CDAT graph: base refused (HISTORICAL) -> mutant refused ("history completeness", fsck's graph verify)
-                  "-c", "core.commitGraph=false",               # review 66 M1: ...
+                  "-c", "commitGraph.readChangedPaths=false",   # review 66 M1: ...
    witnesses: test_review66_forged_bloom_filter_is_never_read, test_review65_forged_graph_and_rewritten_object_refuse

### RZ2 KILLED | configuration listed in every scope but without includes
###   fsck key via include.path: refused -> ACCEPTED; killed by test_review66_configuration_in_includes_and_worktree_scope_refuses
-    names = _git(repo_root, "config", "--includes", "--name-only", "--list", "-z")
+    names = _git(repo_root, "config", "--no-includes", "--name-only", "--list", "-z")

### RZ3 KILLED | configuration listing without -z (all names matched as one newline-joined string)
###   fsck key via include.path: refused -> ACCEPTED; killed by the RV32, RV39 and RV48 witnesses
-    names = _git(repo_root, "config", "--includes", "--name-only", "--list", "-z")
+    names = _git(repo_root, "config", "--includes", "--name-only", "--list")

### RZ4 SURVIVED | extensions.partialClone no longer refused
###   repository with only core.repositoryformatversion=1 + extensions.partialClone=origin: refused -> ACCEPTED
-_LOCAL_CONFIG_REFUSED = re.compile(r"fsck\.|extensions\.partialclone$|remote\..*\.(promisor|partialclonefilter)$")
+_LOCAL_CONFIG_REFUSED = re.compile(r"fsck\.|remote\..*\.(promisor|partialclonefilter)$")
    witnesses: test_review65_local_fsck_or_promisor_configuration_refuses

### RZ5 SURVIVED | promisor keys refused only for a remote named "origin"
###   blob:none clone with -o upstream: precondition False -> True; final refused (review history unreadable); no command ran
-... remote\..*\.(promisor|partialclonefilter)$")
+... remote\.origin\.(promisor|partialclonefilter)$")
    witnesses: test_review65_local_fsck_or_promisor_configuration_refuses, test_review65_partial_clone_runs_no_configured_command

### RZ6 SURVIVED | fsck --no-full
###   --shared clone whose alternate's rejection blob is rewritten: refused -> refused (outcome-equivalent on git 2.43)
-    return _git(repo_root, "fsck", "--full", "--no-dangling", "--no-progress") is not None
+    return _git(repo_root, "fsck", "--no-full", "--no-dangling", "--no-progress") is not None
    witnesses: test_review65_forged_graph_and_rewritten_object_refuse
```

For each survivor, the suite returned 0 with 221 tests.

**Review 66's mutants re-run (not counted as new):**
* RY1, RY3 and RY5 are byte-identical to RV45, RV46 and RV47. Under the old witness names they classify ERROR
  (`NO_INTENDED_PROPERTY_ASSERTION`), but the only failing method in each is the new registered witness, so they are
  KILLED under the registry.
* RY2 and RY4 are NOT_APPLIED (the `--strict` anchor is gone). RY4 re-anchored (RY4b, `--connectivity-only`) is
  **KILLED** by `test_review65_forged_graph_and_rewritten_object_refuse` (rewritten blob: refused → ACCEPTED under the
  mutant).

**Registered mutants re-run singly in the same session** (not reviewer mutants), each against the same baseline:
* RV23, RV30, RV31, RV32, RV33, RV39, RV43–RV48: all **KILLED**.
* Failing methods are exactly the registered witness, except: RV32 (its witness plus the RV39 and RV48 witnesses) and
  RV39 (its witness plus RV32's). Both are expected overlaps.
