# Review — repairs of review 63's findings on the combined Cell-308 development source (Cloud route r1, S4 changed branch)

* Reviewer: **reviewREVIEW63_REPAIR (fresh agent, brief 64)**
* Date: 2026-10-15 (UTC), about 07:40Z to 08:45Z (full harness run 07:59Z–08:42Z).
* Pinned commit: **`5e8e3d9c68786f3624c84a9a8f885ff5b499e370`** (branch `codex/cell308-claude-r5-integration`, draft PR
  flaggielover/ReBaseGuard#3). Detached worktree `scratchpad/review64/tree_5e8e3d9c`. `git status --porcelain` was
  empty at every check; I wrote nothing there.
* Delta: `9b6347cb..5e8e3d9c`, four commits: 03107fe3 (L-DET addendum), 670ec7a4 (review 63 recorded and the repairs),
  a16d2d99 (value-free job-log summary), 5e8e3d9c (Q01 / Q04 / R5SYNC02 extended, ledger line 485).
* NS = `level4/closure_proofs/p5y_k5_cell308_research/`, DEV = `NS/streams/CLOUD_R1_LINUX_DEV`. Line numbers refer to
  the 5e8e3d9c files.
* Scratch: `/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review64/` ("scratch").
  Probes ran on `scratch/base/lx_platform.py` (sha256 `6d114218…`, equal to 5e8e3d9c) and, for the 9b6347cb state, on
  `scratch/base_9b6347cb/lx_platform.py` (sha256 `2f0489d3…`, equal to 9b6347cb). Scripts are stored as `*.py.txt`.
* `new_target_evaluations = 0`. I ran no cell, drift, certificate, decoy, science module, qualification case or
  candidate code. I installed nothing and changed no setting.

---

## 1. Exposure disclosure

**Opened in full:** brief 64 (the only file read in the shared checkout); in the pinned tree: the 9b6347cb..5e8e3d9c
diffs of `lx_platform.py`, `tests/test_lx_platform.py`, `tests/run_mutants.py`, `tests/test_mutation_harness.py` and the
workflow; `lx_platform.py` lines 195–300, 800–955, 1120–1457; parts of `tests/test_lx_platform.py`,
`tests/test_sync_boundaries.py` (lines 385–427) and `tests/test_lx_verified.py` (setup lines); review 63 as recorded;
the disposition supplement; the L-DET addendum; `fn_digests.py.txt` and the head of `FUNCTION_DIGESTS_142D97A9.json`;
ledger lines 482–485.

**Candidate source (parse / read only, nothing executed):** `git show 142d97a9:…/mbs308_qualify.py` lines 94, 1109–1114,
1820–1860 and 2409–2580; `mbs308_driver.py` lines 317–319, 345–352, 1879, 1895; a grep for `json.loads` in
`mbs308_qualify.py`. Both files parsed with `ast` to recompute digests.

**MB r1 qualification records:** the five blobs named by the addendum were hashed in memory
(`git cat-file blob <id>` → sha256) and never printed, parsed or opened. To check the addendum's claims I resolved
`<commit>:<path>` blob ids (tree traversal only) at `7eb057bb`, `142d97a9`, `c46434a3`, `88a16f74`, `5e8e3d9c` and
**`21e99cf0`** (the commit the addendum describes as an MB r1 postexec commit). I listed no tree, diff, file or message
of `21e99cf0`; only `cat-file -e` and `rev-parse 21e99cf0:<qualification path>` touched it. I printed only the
committer date of `7eb057bb`.

**Shared object store:** the pinned worktree's git common directory is `/home/user/ReBaseGuard/.git`; every git read
above went through that object store (objects only, no working-tree file of the shared checkout).

**Name-level contact:** the scratchpad root listing (`MUTANTS_RUN_R*.json`, `gate.txt`, `gitprobe`, `inv_check.json`,
`ldet`, `mut2.log`, `mut3.log`, `native-r3`, `rev5`, `review59`–`review63`, `rv`, `scan*.json`); I opened none of
them except `rv/local_full.json` (named by the brief; `rv/local_full.stdout` only compared by `cmp`). Inside
`review63/` I hashed the originals to compare them with the recorded copies, and listed the names in `scripts/`,
`mut_tmp/`, `tmp/` and `gitexp/` (harness temp copies; nothing read).

**GitHub (read-only API):** run 38694984232 metadata, its job's step list and the last 60 log lines; the last 75 log
lines of the failed job of run 38692293195. Both logs print only counts, ids, statuses, test ids and exception types.

**Live calls:** none against the real repository. Every `attestation_valid` call I made passed `repo_root=<synthetic
repository under scratch/tmp>`. The unit suite (as the brief permits) runs `attestation_valid` only on synthetic
repositories or with `_git` patched (`test_lx_platform.py:1258` uses `repo_root="."` with `_git` patched to return
None). `unshare --user` ran once per interpreter, reading only scratch directories.

**Not opened, grepped or read:** `NS/audit/EXECUTION_INTERRUPTION_ASSESSMENT*`, `NS/audit/INCIDENT_AUDIT*`,
`NS/reviews/REVIEW_EXECUTION_INTERRUPTION*`, anything under `p5y_k5_cell308_mb_r1/postexec/` or any MB r1 target-run
record, `NS/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`, any Cell-309 branch, file or record. I ran no `git branch -a`
and no `--all` log (the addendum's `git log --all --find-object` claim was checked on the candidate's history only).

I hold no E1″ material and no MB r1 target-run runtime or host observation.

---

## 2. Verdicts

REPAIR: REPAIRED_WITH_DEFECTS
HARNESS: SOUND_WITH_DEFECTS
RECORDS: ACCURATE_WITH_CORRECTIONS

**No verdict here accepts any amendment, supplement, addendum, host or decision.** This is a bounded development-layer
review. The supplement, the L-DET addendum and every D-* decision stay PROPOSED / undecided; only the formal route
review, a fresh S12 re-rating and the owner can accept, reject or put anything into force.

* **REPAIR = REPAIRED_WITH_DEFECTS.** Every construction of review 63 that accepted an attestation (H1b, H2c, H3,
  H3b), lifted a rejection (H4b/c) or missed one of the listed forms (H5: 9 of 11) is now refused on 5e8e3d9c, and
  the verdict-format probes (H6 of review 63) refuse. The file-mode H6 repair works. But:
  * an acceptance written **before** the blob is still **accepted** when the repository's git configuration hides the
    commit that introduced it (`log.showRoot=false` with a shallow boundary or root commit; an uncommitted textconv
    attribute) (K1, MAJOR);
  * 5 of my 6 new mutants survive with a demonstrated outcome change, three of them turning a refusal into ACCEPTED
    (K3, MAJOR);
  * one regression: a full sha preceded by a hex character no longer names the attestation (K4);
  * the "complete" caller-input enumeration is not complete (K6).
* **HARNESS = SOUND_WITH_DEFECTS.** P11, Z01, Z02, Z05 and Q06 keep their weakening. RV01–RV17 are genuine direct
  witnesses. The Q01 and R5SYNC02 extensions are justified. The Q04 extension is **not**: the single-site Q04 changes
  an outcome (a duplicated accepting verdict line goes from refused to ACCEPTED), and extending it hid a test gap (K2).
  The workflow change is sound and value-free.
* **RECORDS = ACCURATE_WITH_CORRECTIONS.** Every sha256 bound in ledger lines 482–485 recomputes at its introducing
  commit. Ledger lines 1–481 are a byte prefix. Review 63 and its 27 scratch files are byte-identical to the originals.
  Only delta inputs and the ledger were modified. The local full-run record matches the 5e8e3d9c blobs and
  re-classifies identically. The native run's SUMMARY is **verified** from the GitHub job log. Corrections: ledger
  485's root-cause wording (K2), and unbound or late items (K10).

---

## 3. Review 63's findings and conditions

"9b" = the PR3 head 9b6347cb (`lx_platform.py` 2f0489d3…), "5e" = 5e8e3d9c. Probe ids refer to
`probes64_out.json` (5e) and `probes64_at_9b6347cb_out.json` (9b), both from one script (`probes64.py.txt`).

| item | supplement's claim about 9b | verified at 9b | state at 5e | status |
|---|---|---|---|---|
| H1 MAJOR | tree entry already refused; merges, oldest-dated hit, side branch and acceptance-before-blob open | **Correct.** H1b refused (UNAVAILABLE). H2c (evil merge) and H3b (acceptance first, dated later) **valid**. My H3 variant was refused at 9b (date order differed from review 63's); this does not contradict the claim. | H1b, H2c, H3 and H3b all **refused**. `_first_commit` is gone. `_commits` uses `--diff-merges=separate`; every blob commit must be a strict ancestor of every line commit. Merges, side branches and dates are covered by `test_review63_order_every_commit_merges_and_side_branches` (RV01 and RV08 killed). | **RESOLVED** for the listed constructions. New: K1 (config-hidden introducing commit, MAJOR), K5 (later merges refuse), K7 (symlink entry). |
| H2 MAJOR | W01–W07 not in harness; W03 **equivalent** | **Correct.** W03 is equivalent: an upper-case recorded boot id gives UNKNOWN at 9b and 5e, because `identity_state` calls `boot_id(recorded_boot)` (`:241`), which applies `_BOOT_ID.match` without lower-casing. | RV01–RV07 carry W01–W07; all KILLED in the local record (re-classified by me) and in the native run (SUMMARY 150/150, verified). My re-run of W03 alone (`W03r`) **survives** the suite, and its outcome equals the base (UNKNOWN). That confirms the equivalence and justifies RV03's double edit. W08 re-run: KILLED. | **RESOLVED.** New survivors: K3. |
| H3 MINOR | quoted paths and non-UTF-8 already refuse; HEAD-only scan, case or abbreviation, words and verdicts open | **Correct.** At 9b: non-ASCII path, `"` path and UTF-16 refused; `git rm`, `git mv`, abbreviated, upper-case, REFUSED, UNACCEPTED, `…DECLINED` verdict and NEEDS_REVISION all **valid**. | All of those are **refused** at 5e. A rejection survives `git rm`, `git mv` out of the directory and side branches (`_historical_review_blobs`, `rev-list --full-history`). A non-UTF-8 *historical path* refuses (N8). Still valid, and not claimed: a path-only reference and a ledger rejection. These are acceptable to carry under D-HOST-LIFETIME item (i). | **RESOLVED** as restated in §2. One **regression** (K4). Vocabulary residuals: K8. |
| H4 MINOR | already repaired (CDEX16) | **Correct.** At 9b, `is-active` = None, refreshing, deactivating or maintenance, each with `disabled`, gives None (H12). | unchanged | **RESOLVED** (at PR3) |
| H5 MINOR | partly addressed; §2 lists caller inputs "complete for the public functions" | — | The docstring now calls `repo_root` a test seam (`:1339–1341`). The enumeration is **not complete** (K6). | **PARTIALLY RESOLVED** |
| H6 NOTE | systemd mode already repaired | **Correct** (see H4). In file mode at 9b: an `.upholds` link gives False, and a shadowed lower mask gives False. | `.upholds` counts (H11a True). Only the highest-precedence entry can mask (H11b True). RV16 and RV17 killed. `Wants=` inside unit files is carried, which is acceptable. | **RESOLVED** (residual carried). Note: an empty unit file, which systemd treats as masked, still reads as "wanted" (U3, conservative). |
| H7 NOTE | open | open at 9b (all four formatted verdicts valid) | All four refused. The rule refuses a line containing the word "verdict" (`\bverdict\b`) or a bare capitalised `KEY: VALUE` line. RV15 killed. | **RESOLVED** as restated. Residuals: K8 |
| H8 NOTE | `_strictly_after` timeout already repaired | **Correct** (try/except present at 9b). | `acc_path` is documented as unused on purpose. Ledger 483 `c3_record_corrections` corrects "a rejection is permanent" and the Z05/Z06 wording. The H13 side effect ("a quote before or beside the blob refuses forever") is now stated in §2. | **RESOLVED** |
| C1 | no citation before native run, independent check and fresh review | — | Honoured: the supplement cites nothing as accepted. The native run exists, and its SUMMARY is verified here. This review is the fresh review; it does **not** clear L-LIFE (K1, K3) or L-UPD (K3/RW2) for citation. | **RESOLVED (honoured)**; the condition stays in force for L-LIFE and L-UPD. |
| C2 | §2 restates L-LIFE, L-UPD and caller inputs | — | L-UPD's failed-query clause is exact (H12). L-LIFE omits its dependence on git configuration and clone (K1), the later-merge refusal (K5) and the symlink case (K7). The caller-input list is incomplete (K6). Independence items (i) and (ii) are carried. | **PARTIALLY RESOLVED** |
| C3 | ledger corrects 473 and r5 §13 without editing 472–473 | — | Ledger 483 carries both corrections. The 9b6347cb ledger (481 lines) is a byte prefix of the 5e ledger. | **RESOLVED** |
| C4 | no new owner brief | — | No owner brief in the delta (`git diff --name-status`: 32 added files, none an owner brief). | **CARRIED** (acceptable) |

---

## 4. Answers Q2–Q5

### Q2 — Adversarial fail-closed audit

**Suites.** `python3.1x -B -W error::ResourceWarning -m unittest discover -s tests -v` gives **198 tests OK** on 3.11,
3.12 and 3.13 (`suite_python3.1x.txt`).

**Review 63's probes, re-run** (`probes64.py.txt`, same script against 9b and 5e; table in §3). At 5e: H1b, H2c, H3,
H3b, H4b, H4c, H6×4 and H13 are refused. In H5, 9 of 11 are refused; path-only and ledger are still valid (not
claimed). In H12, all non-inactive activity readings with `disabled` give None, and an unknown PID-1 state gives None.
The control is valid.

**New probes.** All on synthetic repositories under `scratch/tmp`, with `machine_identity` patched; each acceptance
needs `DECIDED ∋ D-HOST-LIFETIME` in the gate path.

| # | construction | 9b | 5e | finding |
|---|---|---|---|---|
| N5 | acceptance in the **root** commit, blob later, quote later; repository config `log.showRoot=false` | valid | **valid** | K1 |
| N5′ | real-history form: acceptance → blob → quote; `git clone --depth 3` so the acceptance commit is the shallow boundary; `log.showRoot=false` set **locally**, or only in a **global** config file (`probes64b_out.json`) | — | **valid** (depth 2 and 4, and default config: refused) | K1 |
| P-c | acceptance in an ordinary (non-root) commit **before** the blob, then quote; full clone; **uncommitted** `.git/info/attributes` `reviews/** diff=hide` plus local `diff.hide.textconv=true` (`probes64c_out.json`) | valid | **valid** (refused without the attribute) | K1 |
| N1 | accepting entry is a **symlink** (mode 120000, a blob) whose target text is the two accepting lines | valid | **valid** | K7 |
| N7 | blob → acceptance → `--no-ff` merge of an unrelated branch forked **before** the blob | valid | **refused, permanently** (the merge "adds" blob and line against its second parent) | K5 |
| N7′ | same, branch forked after the blob, before the acceptance | valid | valid | — |
| N4 | separate rejecting review `blob:a<sha> REJECTED` (full sha preceded by a hex character) | refused | **valid** | K4 (regression) |
| N4 | `<sha> is invalid; do not use it`, `Decision: denied <sha>`, `<sha> not  accepted` (two spaces), `not yet accepted`, a zero-width space inside the first 8 hex digits, the git blob id only | valid | valid | K8 |
| N3 | accepting file also holds `Verdicts: NOT_FIT`, `DEV_CODE: NOT_FIT (see H1)`, `Status: HOLD`, `- DEV_CODE: NOT_FIT`, `**DEV_CODE**: NOT_FIT`, `Vеrdict` with a Cyrillic е, or `Outcome: DENIED` | valid | valid | K8 |
| N10 | the accepting verdict line twice | refused | refused (unpinned by the suite: K2) | K2 |
| N8 | rejecting review under a non-UTF-8 path, later removed | valid | refused (UNAVAILABLE) | — |
| N9 | review files `x` and `x..HEAD` under `reviews/` | valid | **refused: UNAVAILABLE** (`rev-parse HEAD:…/x..HEAD` is parsed as a range and prints two ids) | K9 |
| N9 | `y^@`, `-n.md`, `a..b.md`, `z^!` | — | valid (no effect) | — |
| N2 | gitlink named `REVIEW_HOST_ATTESTATION_2.md` | refused | refused (UNAVAILABLE) | — |
| N6 | accepting file classified binary by git (a NUL byte), written before the blob | refused | refused (`-S` searches binary blobs) | — |
| N9 | `ref.path` = NUL-containing, lone surrogate, 5000 characters, `""`, `:`, `HEAD`, `../x` | no exception | no exception (refused) | — |
| U1 | file mode: dangling link as highest entry, lower mask, `.wants` link | False | True (conservative) | (K3/RW2) |
| U3 | empty unit file as highest entry plus `.wants` (systemd: masked) | True | True (conservative) | — |
| E1 | file mode, a unit root that can be listed but not searched (`unshare --user`, mode 0644 directory) | **PermissionError raised** | **PermissionError raised** out of `unit_enabled` and `auto_update_settings` (therefore out of `preflight`) on 3.11, 3.12 and 3.13 | K9 (pre-existing) |

**Classes:**
* **ACCEPTED where L-LIFE refuses:**
  * K1 (configuration and attributes of the reading repository; three constructions, one a full clone with no
    committed trace);
  * K4 (a rejection not seen that 9b saw).
* **Wrongly "not enabled":** none found in shipped code. RW2 shows the dangling-entry branch is unpinned.
* **Crash:**
  * `attestation_valid`: none found. Every failed listing, blob, decode or rev-parse refuses.
  * `preflight`: can raise `PermissionError` via `unit_enabled` (pre-existing; it fails closed by exception).
* **Regression of a 9b property:** K4. The supplement does not list K5's new refusal among the stated side effects;
  it is fail-closed.

**Mutants:** 6 new (RW1–RW6) plus re-runs of W03 and W08 and the single-site Q04 (§7). 1 of 6 new killed; 5 survived,
each with a demonstrated outcome change (`equiv64_out.json`).

### Q3 — Harness integrity

* **Re-anchored mutants (same weakening):**
  * **P11:** the mask check is removed (now the post-loop check). Same property.
  * **Z01:** a veto counts only when the reference and the negative or verdict signal are on the **same line**. It is
    the same weakening, applied to the widened veto vocabulary.
  * **Z02:** `.requires` is dropped while `.wants` (and the new `.upholds`) are kept. Same.
  * **Z05:** line commits are looked up path-limited to `acc_path`. The old version did this for the oldest line
    commit, the new one for all. It is the same class (path limit), applied to the new set semantics.
  * **Q06:** the oldest commit touching `att_path` by path. `[-1:]` of log order equals the old `--reverse` `[0]`.
    Same.
* **Extended mutants:**
  * **Q01** (plus a non-recursive history listing): justified. The single site is outcome-equivalent for vetoes,
    because the history scan reads the subdirectory blob, since `current` then holds only top-level ids. Native run
    38692293195 shows the single site was detected only by non-witness tests.
  * **R5SYNC02** (plus RV10's edit): justified. The test's fault injection (`ls-tree` with `-r`) fails both listings,
    and with the history scan intact a HEAD-only listing failure cannot hide a veto. The kill proves detection of the
    joint removal only. RV10 alone is separately pinned.
  * **Q04** (plus RV14's edit): **over-weakened** (K2). The single-site Q04 (`ACCEPTANCE_VERDICT_LINE in verdicts`) is
    **not** equivalent. With the accepting verdict line twice, base refuses and single-site Q04 **accepts**
    (`equiv64_out.json`, Q04s; `reviewer64_mutants_result.json`: Q04s SURVIVED). The extended Q04 ⊃ RV14, so its kill
    no longer shows that "exactly one verdict-like line" is pinned. Ledger 485's statement that the three single-site
    mutants "no longer change the outcome" is false for Q04. For Q01 and R5SYNC02 it is loose: they did change test
    outcomes (non-witness assertions).
  * **RV03:** justified (W03 is equivalent, shown above).
* **RV01–RV17:** each witness is a direct assertion of the stated property. I traced each mutant to the failing case:
  * RV01: the `first` case. Under RV01 only the newest line commit is ordered, so the earlier acceptance escapes.
  * RV08: the evil merge.
  * RV09, RV10, RV11: `removed`, `non-UTF-8 history` and `side branch`. Without `--full-history` the merge is
    TREESAME to its first parent and the side branch is never walked.
  * RV12: `upper-case abbreviated` and `declined` (`sha[:8]`).
  * RV13: `refused`, `veto` and `needs revision`.
  * RV14: `other verdict`.
  * RV15: `* VERDICT: ok`.
  * RV16 and RV17: the upholds and mask-precedence cases.
  * RV02–RV07: the W tests.

  The local record shows each RV kill coming from its own witness alone.
* **Workflow:**
  * The asserts were raised to 150 mutants and 151 suites. `MUTANT_GROUP_SIZES` sums to 150, and
    `test_registry_witnesses_and_complete_input_hashes` asserts 150.
  * Timeout 90 min (the native run took 17 min 32 s).
  * `git --version` is written to the artifact only.
  * The SUMMARY prints 7 keys: counts, booleans and PASS/ERROR. NOT_KILLED prints ids, statuses, reason codes, counts,
    test ids and exception types; test ids carry only synthetic subTest parameters. **Value-free.**
  * Both are printed before the asserts, so a failing run is diagnosable (run 38692293195 shows this works).
  * A malformed `controlled_runner_metadata_raw` would raise before the asserts; that fails the step, so it is
    fail-closed.
* **Native evidence, verified via the GitHub API:**
  * Run 38694984232: head_sha 5e8e3d9c, conclusion success, step "Full baseline and strict property mutations"
    06:52:04–07:09:36Z. The log prints exactly the transcribed SUMMARY, with artifact digest `d3c0a509…` and artifact
    id 11954406071. The runner's git is 2.55.0.
  * Run 38692293195 (a16d2d99) printed 147/150 with exactly the three NOT_KILLED rows transcribed in ledger 485.
  * The artifact contents remain **UNVERIFIED** (not downloadable).

### Q4 — Records

* **Ledger.** Lines 482 (03107fe3), 483–484 (670ec7a4) and 485 (5e8e3d9c) were added; lines 1–481 are a byte prefix.
  * All 3 bindings of 482, the 27 `scratch_sha256` entries and `review_sha256` `107305de…` of 483, and the 11 hashes
    of 484 recompute **at the introducing commit**.
  * Two entries of 484 are superseded by 5e8e3d9c (workflow → `7a9ee1dd…` since a16d2d99; `run_mutants.py` →
    `e7697f35…`). Ledger 485 rebinds them, and all 10 of its hashes recompute at 5e8e3d9c.
  * a16d2d99's own inputs (workflow `7a9ee1dd…`, an intermediate `run_mutants.py`) are bound by no ledger line (K10).
* **Local full-run record** (`rv/local_full.json`, byte-equal to `rv/local_full.stdout`; not committed at 5e8e3d9c,
  as the brief states):
  * all 10 `input_sha256` values equal the 5e8e3d9c blobs, and before equals after;
  * all 150 rows' edits and `mutated_lx_platform_sha256` recompute from the 5e8e3d9c source;
  * re-running the harness's own `classify_mutant` on every stored suite against the stored baseline reproduces all
    150 statuses (150 KILLED, 198 tests each, baseline valid).
  * It finished at 07:35:22Z, after the native run (K10).
* **Review 63 and scratch:**
  * `REVIEW_CLOUD_R1_DELTA_R5.md` is byte-identical to `scratchpad/review63/REVIEW_CLOUD_R1_DELTA_R5.md` (`107305de…`).
  * All 27 files under `reviews/scratch_CLOUD_R1_DELTA4/` are byte-identical to their originals; only `.py` was
    renamed to `.py.txt`.
  * Not copied: `gitexp/`, `tmp/` (harness copies), `tree_37c62102/`, and the empty `scripts/` and `mut_tmp/`. This
    matches ledger 483's stated omissions; the two empty directories are not named there, but are empty.
* **Modified files:** `git diff --name-status 9b6347cb..5e8e3d9c` shows 6 M, namely the workflow, the ledger,
  `lx_platform.py`, `run_mutants.py`, `test_lx_platform.py` and `test_mutation_harness.py`, plus 32 A. No other file
  that existed at 9b6347cb changed; nothing was deleted.
* **Supplement facts:**
  * The PR3 `lx_platform.py` is `2f0489d3…` (verified).
  * "198 tests OK locally on 3.11–3.13" reproduced.
  * "22/22 selected" cannot be re-derived, but is consistent with the full record.

### Q5 — L-DET reference addendum (git objects only; `ldet_check64.py.txt`, `ldet_check64_out.json`)

* **Hashes:**
  * For all 5 records: the git blob ids at `7eb057bb`, `142d97a9` and `21e99cf0` equal the table, and sha256 of each
    blob equals the table.
  * `MBR1_RECORD_PINS` (lines 1823–1839) contains every sha256 and the blob prefix.
* **Ancestry:**
  * `c46434a3` ⊂ `7eb057bb` ⊂ `142d97a9` (both `--is-ancestor` true).
  * None of the five paths exists at `c46434a3`, at `7eb057bb~1` (present in this shallow clone), at `88a16f74` or at
    5e8e3d9c.
  * No commit in `7eb057bb..142d97a9` touches them.
  * In the candidate's history, `--find-object` finds only `7eb057bb` for each blob.
  * Committer date 2026-09-29T19:22:35+09:00.
  * The `--all` form and full-history confirmation are **UNVERIFIED** by me (shallow clone; I did not run `--all`).
* **Function digests:**
  * Both file blobs and file sha256 values match.
  * All 16 definitions: lines, `source_sha256` and `ast_sha256` match, the AST under CPython 3.13.16 (same as stated).
  * No decorators, no duplicate top-level definitions, no other bindings of these names.
  * The serializer lines 1879 and 1895 and the `jsonable` / `fs` behaviour are as described.
* **Gap statements:** accurate as far as they go. Gap 1 (structural comparison after `json.loads`, no byte equality)
  and gap 2 (the serial record) are verified from source. They are incomplete (K11):
  * Python equality also conflates JSON `true` / `1`, `false` / `0` and `0` / `-0.0`, not only `1` / `1.0`;
  * `pinned_bytes` reads the **working tree** (`(repo / rel).read_bytes()`) and checks `HEAD:rel`. The paths are
    absent on this branch, so the candidate's loader cannot serve §1's "read by blob id, never from a working tree".
    This is not listed as a gap.
  * §1 cites `MBR1_RECORD_PINS` as "lines 1822–1839" while the table says 1823–1839 (1822 is the comment line).

---

## 5. New findings

**K1 — MAJOR — The order rule depends on the reading repository's git configuration and attributes. An acceptance
written BEFORE the attested blob is ACCEPTED when that configuration hides its introducing commit.**
* **Location:** `lx_platform.py:1150–1156` (`_git`: no config isolation), `:1290–1303` (`_commits`: `git log` with
  default config, textconv allowed), `:1306–1327` (`_ordered`); supplement §2 L-LIFE ("every commit … that adds or
  removes the accepting line"; "any git failure … refuses").
* **Evidence** (`probes64_out.json` N5, `probes64b_out.json`, `probes64c_out.json`; each refused under default
  config):
  * `log.showRoot=false` in local **or global** scope hides the root or **shallow-boundary** commit from `-S` and
    `--find-object`. A depth-3 clone whose boundary is the acceptance commit then accepts. This checkout is shallow.
  * An uncommitted `.git/info/attributes` `diff=hide` plus local `diff.hide.textconv=true` hides an ordinary
    pre-blob acceptance commit in a full clone. This also means the check **executes** a configured textconv command.

  The same holds at 9b6347cb (pre-existing). It is not stated in §2, and it defeats item (iii) without any committed
  trace.
* **Correction:**
  * Run every git call with `--no-replace-objects`, `-c log.showRoot=true` (or `--root`) and `--no-textconv`.
    Pass `--no-ext-diff`.
  * Set `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=/dev/null`, and ignore repository-local config, or refuse when
    it sets any key outside an allow-list. Refuse if `.git/info/attributes` or `.git/info/grafts` exists or
    `refs/replace/` is non-empty.
  * Refuse in a shallow repository (`rev-parse --is-shallow-repository`).
  * Add tests with `log.showRoot=false`, a shallow clone and a textconv attribute.
  * State the dependency in L-LIFE.

**K2 — MINOR — Harness Q04 was extended instead of adding a test. The single-site weakening is not equivalent, and
ledger 485's root cause is wrong for Q04.**
* **Location:** `tests/run_mutants.py` Q04 (two edits); ledger line 485 `root_cause`.
* **Evidence:**
  * Q04s (single site, as at 670ec7a4) **SURVIVED** the 198-test suite under `classify_mutant`.
  * Base refuses an accepting file holding `VERDICT: HOST_ATTESTATION_ACCEPTED` twice; Q04s accepts it.
  * RW4 (`set(verdicts) == {…}`) is the same gap.
  * Extended Q04 ⊃ RV14, so its kill shows only that removing both enforcement sites is detected.
* **Correction:**
  * Add a duplicate-accepting-verdict case to `test_review63_verdict_like_lines_refuse_acceptance` (or to
    `test_acceptance_is_found_not_named`).
  * Restore Q04 to its single site, or keep both and register the single site as its own mutant.
  * Correct ledger 485 in a new line: Q04 was a test gap; Q01 and R5SYNC02 were detected by non-witness tests.

**K3 — MAJOR — The new code is again under-pinned: 5 of 6 reviewer mutants survive, each with a demonstrated outcome
change. Three of them turn a refusal into ACCEPTED.** (§7; `reviewer64_mutants_result.json`, `equiv64_out.json`)
* **RW1:** the `not blob_commits` guard is removed. With the blob and the acceptance in the same (root) commit and
  `log.showRoot=false`, refused → **ACCEPTED** (`all()` over no blob commits).
* **RW3:** a non-UTF-8 historical review path is skipped. A removed rejection under such a path: UNAVAILABLE →
  **ACCEPTED**.
* **RW6:** line commits are searched on the first parent only. An acceptance written on a side branch before the blob
  existed there, synced with main and merged `--no-ff`: refused → **ACCEPTED**. The existing side-branch test cannot
  see it, because its merge is also a blob commit (K5).
* **RW2:** a dangling highest-precedence unit link no longer shadows a lower mask: True → **False** ("not enabled",
  the unsafe direction).
* **RW4:** the duplicate accepting verdict (K2).

**Correction:** add tests that kill RW1–RW4 and RW6, and add them to the registry.

**K4 — MINOR (regression) — A full sha preceded by a hex character no longer names the attestation.**
* **Location:** `lx_platform.py:1171–1177` (`_HEX_TOKEN`, `_names_sha`).
* **Evidence:** N4 `blob:a<sha> REJECTED`: refused at 9b6347cb (`sha in ln`), **valid** at 5e8e3d9c. `findall`
  starts the token at the extra hex character, so neither token is a prefix of the sha.
* **Correction:** keep the substring test as well (`sha in ln.lower()`), and match prefixes at hex-run starts **or**
  anywhere a full sha occurs. Add a test.

**K5 — MINOR — Any later merge of a branch forked before the blob permanently refuses a valid acceptance. §2 does not
state this.**
* **Location:** `_commits` (`--diff-merges=separate`), `_ordered`; supplement §2 side effects.
* **Evidence:** N7: blob, then acceptance, then a `--no-ff` merge of an unrelated branch forked before the blob. Valid
  at 9b, **refused** at 5e: against its second parent the merge "adds" the blob and the line. In a merge-based
  repository (this one uses PR merges), routine merges revoke acceptance. This fails closed but is unstated and
  practically decisive.
* **Correction:** either count a merge as introducing the blob or line only if it is absent from **every** parent
  (combined-diff semantics; keep the evil-merge test), or state the side effect in L-LIFE.

**K6 — MINOR — The caller-input enumeration called "complete for the public functions" is not complete.**
* **Location:** supplement §2 "Caller inputs".
* **Evidence** (AST enumeration of public signatures), omitted:
  * `machine_identity(machine_id_path, dmi_path)`: the F20 hardware binding; review 63 named it;
  * `dpkg_versions(packages, query)`: review 63 named it;
  * `cmdline_sha256(pid, data)`;
  * `snapshot(power_root=, suspend_text=)`;
  * `assess(start, end, samples, journal_suspend_events)`;
  * `durable_write(path, data, fault=)`;
  * `root_attestation(attestation_ref)` and `memory_readings(…, attestation_ref=)`;
  * `free_disk_bytes(path)`, `identity(pid)`, `proc_stat(pid, text)`, `ns_inode(kind, pid)`.

  "the `text=`, `root=` and `maps_text=` arguments of the other readers" does not cover these.
* **Correction:** complete the list, or drop "complete".

**K7 — MINOR — A symlink is accepted as an accepting review.**
* **Location:** `_acceptances` (`:1243–1287`); supplement §2 ("blob files").
* **Evidence:** N1: a mode-120000 entry whose target text holds the two lines is **valid** (9b and 5e). It is a git
  blob, but not a review file: a checkout makes it a dangling link. Review 63 asked for mode 100644.
* **Correction:** require mode `100644` (or `100755`) via `ls-tree` for accepting entries, refuse 120000. State it.

**K8 — NOTE — Verdict and veto vocabulary residuals** (within the stated rule, but the rule is enumerative).
* N3: `Verdicts:` (the plural is not `\bverdict\b`), annotated, bulleted or bold `KEY: VALUE`, homoglyphs and
  `Outcome: DENIED` pass in the accepting file.
* N4: free-text denials, `not  accepted`, `not yet accepted`, a zero-width space and blob-id-only references are not
  vetoes.
* **Correction:** state the enumeration as such in L-LIFE, or rely on the ledger binding (carried item (i)).

**K9 — NOTE — Fail-closed denial and crash paths.**
* **(a)** Review files `x` and `x..HEAD` under `reviews/` make every attestation UNAVAILABLE (rev-parse range parsing
  at `:1270`). Fix: resolve blob ids from the `ls-tree -r -z` listing instead of `rev-parse HEAD:<path>`.
* **(b)** `unit_enabled` (file mode) raises `PermissionError` when a root is listable but not searchable
  (`Path.exists` / `is_symlink`). It propagates out of `auto_update_settings` and `preflight` on 3.11–3.13. This is
  pre-existing (9b6347cb too). Fix: catch `OSError` per entry and return None.

**K10 — NOTE — Records.**
* a16d2d99's inputs (workflow `7a9ee1dd…`, intermediate `run_mutants.py`) are bound by no ledger line.
* The local full-run record is uncommitted and unbound. It finished at 07:35:22Z, 26 minutes after the native success,
  whereas ledger 485's `process_change` says "before relying on the native run".
* The two empty review-63 scratch directories are not in ledger 483's omission list.
* Correct these in a new ledger line.

**K11 — NOTE — L-DET addendum gap statements are incomplete.**
* Add: `true` / `1`, `false` / `0` and `0` / `-0.0` also compare equal.
* Add: the candidate's `pinned_bytes` reads the working tree and `HEAD`, so it cannot be L-DET's loader on a branch
  where the paths are absent.
* Fix the 1822 / 1823 line citation.

**Counts:** BLOCKING 0 · MAJOR 2 (K1, K3) · MINOR 5 (K2, K4, K5, K6, K7) · NOTE 4 (K8, K9, K10, K11); 11 new findings.

---

## 6. Independent full harness run

`python3.12 -B tests/run_mutants.py scratch/full_harness_py312.json` (TMPDIR in scratch; the pinned tree was not
written; `git status --porcelain` empty afterwards).
* Result, finished 08:42:05Z (CPython 3.12.3, git 2.43.0, exit 0, empty stderr): unmutated suite **PASS** (198),
  **150/150 KILLED**, `pass` true, `inputs_unchanged` true, `full_registry_completed` true.
* Its `input_sha256` equals the coordinator's local record, and every (id, status) pair is identical.
* This independently reproduces the native SUMMARY (whose artifact I could not read). It does not change K2 or K3:
  the registry passes, but the suite leaves the RW1–RW4, RW6 and single-site Q04 weakenings undetected.

---

## 7. Reviewer mutants (brief 64)

**Method:**
* Each mutant is a copy of the 5e8e3d9c `lx_platform.py` in a scratch temporary directory.
* The pinned 198-test suite runs through the harness's own `run_suite` (`LX_PLATFORM_DIR`, `PYTHONWARNINGS=error`).
* Each result is classified by the harness's `classify_mutant` against a fresh baseline (PASS, 198), with the witnesses
  named per mutant.
* Script `reviewer64_mutants.py.txt`, result `reviewer64_mutants_result.json`; outcome checks `equiv64.py.txt` and
  `equiv64_out.json`.

**Result: 6 new mutants, 1 killed, 5 survived.** Every survivor changes an outcome in the weakening direction. Re-runs:
W03 survives as an equivalent (UNKNOWN both ways); W08 is killed; the single-site Q04 survives with an outcome change.

```
### RW1 SURVIVED | empty blob-commit set no longer refuses   (same-commit acceptance, log.showRoot=false: refused -> ACCEPTED)
@@ _ordered @@
-    if not blob_commits or not line_commits:
+    if not line_commits:

### RW2 SURVIVED | dangling highest-precedence unit link no longer shadows a lower mask   (True -> False)
@@ unit_enabled @@
-        if first is None and (f.is_symlink() or f.exists()):
+        if first is None and f.exists():

### RW3 SURVIVED | a non-UTF-8 historical review path is skipped   (UNAVAILABLE -> ACCEPTED)
@@ _historical_review_blobs @@
             except UnicodeDecodeError:
-                return None
+                continue

### RW4 SURVIVED | the accepting verdict line may repeat   (refused -> ACCEPTED)
@@ _acceptances @@
-        if f"{ACCEPTANCE_LINE}{sha}" in lines and verdicts == [ACCEPTANCE_VERDICT_LINE]:
+        if f"{ACCEPTANCE_LINE}{sha}" in lines and set(verdicts) == {ACCEPTANCE_VERDICT_LINE}:

### RW5 KILLED (test_review63_veto_words_and_references) | an 8-hex prefix no longer names the sha
@@ _HEX_TOKEN @@
-_HEX_TOKEN = re.compile(r"[0-9A-Fa-f]{8,64}")
+_HEX_TOKEN = re.compile(r"[0-9A-Fa-f]{9,64}")

### RW6 SURVIVED | accepting-line commits on the first-parent chain only   (side-branch pre-blob acceptance: refused -> ACCEPTED)
@@ _ordered @@
-    line_commits = _commits(repo_root, pick, "HEAD")
+    line_commits = _commits(repo_root, pick, "--first-parent", "HEAD")

### W03r SURVIVED (equivalent: UNKNOWN in base and mutant) | review 63 W03 alone
-    if b is not None and (not isinstance(b, str) or not _BOOT_ID.fullmatch(b)):
+    if b is not None and (not isinstance(b, str) or not _BOOT_ID.fullmatch(b.lower())):

### W08r KILLED (test_systemctl_path_when_systemd_is_pid1) | failed is-enabled treated like not-found
-        if st == "not-found":
+        if st in ("not-found", None):

### Q04s SURVIVED | harness Q04 single site (as at 670ec7a4)   (duplicated accepting verdict: refused -> ACCEPTED)
-and verdicts == [ACCEPTANCE_VERDICT_LINE]:
+and ACCEPTANCE_VERDICT_LINE in verdicts:
```

**Scratch files:**
* `probes64.py.txt`, `probes64_out.json`, `probes64_at_9b6347cb_out.json`;
* `probes64b.py.txt`, `probes64b_out.json`;
* `probes64c.py.txt`, `probes64c_out.json`, `probes64c_at_9b6347cb_out.json`;
* `eacces64.py.txt`;
* `check_ledger.py.txt`;
* `ldet_check64.py.txt`, `ldet_check64_out.json`;
* `reviewer64_mutants.py.txt`, `reviewer64_mutants_result.json`;
* `equiv64.py.txt`, `equiv64_out.json`;
* `suite_python3.1x.txt`;
* `full_harness_py312.*`.
