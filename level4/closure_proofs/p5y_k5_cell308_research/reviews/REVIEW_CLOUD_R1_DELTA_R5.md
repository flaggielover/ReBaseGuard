# Review — DELTA of revision 5 and amendment r5 after review 62 (Cell 308, MB-S successor, S4 changed branch, Cloud route r1)

* Reviewer: **reviewCLOUD_R1_DELTA4 (fresh agent, brief 63)**
* Date: 2026-10-15 (UTC). Work ran from about 01:25Z to about 01:45Z, was interrupted by a usage limit, and resumed at
  about 05:17Z after a coordinator message.
* Delta reviewed: **cd86c326..37c62102** (HEAD under review = `37c62102c0e2e22563760173fb04a1fcf66d5e2f`, branch
  `claude/cell-308-github-state-skb1g0` as it stood when I started).
  * Four commits: dd5f3901 (review 62 recorded), 18d8e93d (revision 5, amendment r5, owner brief r5, brief 63;
    intermediate), 29fbe6c9 (tests killing Z07 / Q13; intermediate), 37c62102 (TEST_RUN, MUTANTS_RUN, ledger line 473).
  * **Location change.** At 05:16:47Z the shared checkout `/home/user/ReBaseGuard` was switched to another branch. On
    the coordinator's instruction, "the checkout" for this review is now the detached worktree
    `scratchpad/review63/tree_37c62102` (HEAD = 37c62102). Every result I produced before 05:16Z was produced before
    the switch, so none read the switched tree. To be safe I **redid** from the pinned tree: the three suite runs, the
    probe script (`probes63.py`, output identical key by key to the earlier run, kept as `probes63_out_prepin.json`),
    the quotation check (byte-identical output), and every record check of Q5 (identical results). The committed
    harness run (finished 01:42Z, before the switch) was **not** redone: its recorded hashes equal the pinned tree's
    bytes (`lx_platform.py` 8ccddf85…, tests 2002dc8d…). My own mutants ran only against the pinned tree's suite.
    `git -C tree_37c62102 status --porcelain` was empty at every check; I wrote nothing there.
* NS = `level4/closure_proofs/p5y_k5_cell308_research/` in the pinned tree. Line numbers refer to the 37c62102 files.
* `new_target_evaluations = 0`. I ran no cell, drift, certificate, decoy, science module, qualification case, candidate
  code or quarantine guard. I installed nothing, changed no setting, and wrote no repository file.
* Scratch: `/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review63/`
  ("scratch"). Probes ran on `scratch/base/lx_platform.py`, sha256 `8ccddf85…`, which equals 37c62102.

---

## 1. Exposure disclosure

**Opened in full:** review 62 (`reviews/REVIEW_CLOUD_R1_DELTA_R4.md`); `lx_platform.py` at 37c62102; the
cd86c326..37c62102 diffs of `lx_platform.py`, `tests/test_lx_platform.py`, `tests/run_mutants.py` and
`README_DEV_ONLY.md`; amendment r5; owner brief r5, and its diff against r4; ledger lines 472–473; the new
BRIEF_INDEX row; `ledger/briefs/63_reviewCLOUD_R1_DELTA4.txt`; `results/TEST_RUN.json`; the summary keys of
`results/MUTANTS_RUN.json`. From review 62's scratch: `probes62`, `ns_probe62`, `ns_probe62b`, `quotecheck62`, the
head and tail of `reviewer62_mutants`, and the head of `probe_zombie_leader`.

**Read programmatically only:** `quotecheck63.py` (review 62's checker pointed at r5, with review 60's list `q60.txt`)
read the accepted sources it names: `governance/SUCCESSOR_GOVERNANCE_308*.md`, `USER_DECISION_BRIEF_308_SUCCESSOR_R2.md`,
`CONSTANTS_RATIFICATION_MBS308.md`, `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1*.md`,
`reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`, `ROUTE_PREPARATION.md`. I grepped `q60.txt` for the source file names.

**Candidate:** `git show 142d97a9:…/mbs308_host.py`, lines 575–605 only (`preflight_gates`).

**Host (read-only):** `/proc/1/comm` (`process_api`), `systemctl --version` (255), `git --version`, the boot id,
`--is-shallow-repository` (true), namespace inodes and cgroup files via the probes. `unshare` ran three times (no flags,
`--cgroup`, `--pid --fork --mount-proc`), each reading only the scratch copy.

**Not opened, grepped or read:** `audit/EXECUTION_INTERRUPTION_ASSESSMENT*`, `audit/INCIDENT_AUDIT*`,
`reviews/REVIEW_EXECUTION_INTERRUPTION*`, anything under `p5y_k5_cell308_mb_r1/postexec/` or any MB r1 target-run record,
`ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`, any Cell-309 branch, file or record. I ran no `git branch -a`.

**Name-level contact only:**
* The scratchpad root listing showed `MUTANTS_RUN_R3.json`, `MUTANTS_RUN_R4.json`, `MUTANTS_RUN_R4b.json`, `gate.txt`,
  `inv_check.json`, `mut2.log`, `mut3.log`, `scan*.json`, and the directories `rev5`, `review59`–`review62`. I opened
  none of them. I **hashed** `review62/REVIEW_CLOUD_R1_DELTA_R4.md` and review 62's original scratch files to compare
  them with the recorded copies; I did not read them.
* `ls /tmp/tmp*` showed temporary-directory names created by harness runs.
* At 05:18Z, before I knew of the switch, I ran `git -C /home/user/ReBaseGuard rev-parse HEAD` and `reflog -5`. These
  showed commit `9b6347cb` and a branch name `codex/cell308-claude-r5-integration`. I read no file, diff or log message
  of that branch, and nothing here depends on it.

I hold no E1″ material and no MB r1 target-run runtime or host observation.

---

## 2. Verdicts

DELTA: DELTA_ACCEPTED_WITH_CONDITIONS
AMENDMENT_DRAFT_R5: FIT_WITH_CONDITIONS
DEV_CODE_R5: FAIL_CLOSED_WITH_DEFECTS

**No verdict here accepts the amendment.** Only three things can accept, reject or put it into force: a formal
independent route / governance review, a fresh S12 incident-independence re-rating, and the owner's decisions (OD-1 to
OD-3 and the [OPEN] items). This is a delta review of a draft and of a development layer.

**DEV_CODE_R5 = FAIL_CLOSED_WITH_DEFECTS.**
* Closed: every probe of review 62 (G1–G15) that showed a defect is now refused or fails closed (§4 Q2). The
  `readings`, `view_complete` and `pin_point(modules)` parameters are gone. In a nested PID namespace, `busy_processes`
  returns None live. `OPEN_DECISIONS` holds 21 ids.
* Defects:
  * With D-HOST-LIFETIME patched into `DECIDED`, an attestation is **accepted** by four constructions that the stated
    L-LIFE rule forbids (H1):
    * a *directory* named `REVIEW_HOST_ATTESTATION_1.md` committed together with the blob;
    * an acceptance introduced by a merge commit together with the blob;
    * an acceptance written on a branch that never contained the blob;
    * an acceptance written before the blob and dated later.
  * A rejection is removed by `git rm`, and many rejection forms are not seen (H3).
  * A failed `is-active` query plus `disabled` gives "not enabled" (H4).
  * **7 of my 8 new mutants survive** with a demonstrated change of outcome, including a malformed identity record
    proving **DEAD** (H2).
* Why not NOT_FAIL_CLOSED: in the shipped state `DECIDED` is empty, so `host_lifetime_attested`, the provider-image
  half of the update gate and root attestation stay OPEN_DECISION or None. Five gates are hard-wired OPEN_DECISION. No
  failed reading gives PASS, AC, CLEAN or a number.

**AMENDMENT_DRAFT_R5 = FIT_WITH_CONDITIONS.**
* Done: L-PIN, L-EXCL and H6 now state what the code does. §4 has 21 rows, equal to `OPEN_DECISIONS`. The acceptance
  mechanism's independence is carried as explicit items (i)–(iii) of D-HOST-LIFETIME. Every [ACCEPTED] quotation is
  unchanged and verbatim.
* Still not exact:
  * L-LIFE says "files", "the commit that first introduced the accepting line … is a strict descendant", and "a
    rejection is permanent" (H1, H3).
  * L-UPD says "a failed query ⇒ unknown" (H4).
  * The "Caller inputs" paragraph is incomplete (H5).

**DELTA = DELTA_ACCEPTED_WITH_CONDITIONS.**
* G4–G10 and E1, E3 and E4 are resolved; G11 is resolved for its listed items; G1–G3 are partly resolved; E2 is partly
  resolved (§3).
* Records recompute: every binding of line 473; review 62 is verbatim; review 62's scratch is byte-identical to the
  originals; ledger lines 1–472 are unchanged.
* A fresh run reproduces TEST_RUN (87 OK on 3.11, 3.12, 3.13) and MUTANTS_RUN (113/113, every (id, status) pair).
* Conditions are in §6 (C1–C4).

---

## 3. Status of review 62's findings and conditions

| item | sev (r62) | status | evidence |
|---|---|---|---|
| G1 | MAJOR | **PARTIALLY RESOLVED**; ledger binding **CARRIED-AS-CONDITION** (acceptable) | **Resolved:** <br>• `_acceptances` (`:1062–1086`) lists only direct children (`ls-tree --name-only HEAD reviews/`) and requires the `.md` suffix. <br>• Review 62's G1 probe and an `.md` file in a scratch subdirectory are both refused (`G1_*`, `G1b_*`). <br>• Test cases "subdirectory of the review dir" and "wrong suffix"; Q02 and Q05 are killed. <br>**Not resolved:** a **tree** entry at top level is accepted (H1a). A directory `reviews/REVIEW_HOST_ATTESTATION_1.md/` whose two empty member files are named as the acceptance line and the verdict line is accepted. `git show HEAD:<tree>` prints the member names one per line (`H1_git_show_tree`). Given one later quote of the line anywhere, the attestation is **valid** (`H1b`). That is subdirectory content, the G1 class. <br>**Carried:** the ledger REVIEW binding is carried as D-HOST-LIFETIME item (i) (amendment line 175). This is acceptable to carry. |
| G2 | MINOR | **PARTIALLY RESOLVED** | **Resolved:** <br>• `_ordered` (`:1089–1100`) compares the first `--find-object` commit of the blob with the first `-S` commit of the line, by ancestry. <br>• Review 62's G2, G3, G4 and the rename case are all refused. <br>• Test `test_accepting_line_must_post_date_the_attested_blob`. <br>**Not resolved (H1):** <br>• "First" is the oldest **by log date** among the `-S` hits, repository-wide, and `acc_path` is never used. <br>• Merge commits are invisible to `-S` and `--find-object` (verified on git 2.43). <br>• **Valid** results: <br>&nbsp;&nbsp;– an evil merge introducing blob and acceptance together, then a copy of the blob and a quote of the line (`H2c`); <br>&nbsp;&nbsp;– an acceptance committed on a branch forked before the blob, whose commit is **not** a descendant of the blob commit, merged after a quote on main (`H3`); <br>&nbsp;&nbsp;– the same with the acceptance actually made first and dated later (`H3b`). <br>• Control without the quote: refused (`H3c`). |
| G3 | MINOR | **RESOLVED** (as specified) | **Resolved:** <br>• `_NEGATIVE` is case-insensitive; the scan is recursive over every committed file under `reviews/`; one verdict line is required. <br>• Review 62's G5 (lower-case, NOT_ACCEPTED, WITHDRAWN) and G6 (a non-prefix review) are refused. <br>• Q01, Q03, Q04 and Z01 are killed. <br>**Residual gaps are new findings:** <br>• H3: the rejecting review is deleted or moved; a quoted path; UTF-16; an abbreviated or upper-case sha; unlisted words; the ledger. <br>• H7: a formatted second verdict. |
| G4 | MAJOR | **RESOLVED** (for Z02–Z04, Z07, Z11) | Z01–Z11 are in the harness (`run_mutants.py:224–261`). My fresh run killed **all 113**, with every (id, status) pair equal to `MUTANTS_RUN.json`. Z05 and Z06 now weaken `_ordered` (path-limited `-S`; equal commit counts as later). These are new weakenings, not "the same" ones (§13 wording, H8). New survivors: H2. |
| G5 | MINOR | **RESOLVED** | `preflight` parameters are `repo_path, mode, other_job_running, launched, attestation_ref` (`B2c`), and `readings=` raises TypeError (`G8_readings_kw`). Live `ac_power` = OPEN_DECISION (power `ABSENT`). Q10 and Q11 are killed. Residual enumeration gaps: H5. |
| G6 | MINOR | **RESOLVED** | `busy_processes` calls `proc_view_complete()` itself (`:662`), and `view_complete=` raises TypeError. Live under `unshare --pid --fork --mount-proc`, `busy_processes` returns **None** (`ns_probe63_out.txt`); a patched False or None view gives None. Test `test_view_is_read_not_assumed`; M31 and Z10 are killed. |
| G7 | MINOR | **RESOLVED** (the three cases); a new defect in the repair (H4) | **Fixed:** <br>• disabled-but-active gives True (`G12`); <br>• a dangling `.wants` link gives True (`G10`); <br>• all 13 roots of systemd.unit(5) are searched (`G11_UNIT_ROOTS`). <br>Q07, Q09 and Q12 are killed. <br>**New:** if `is-active` fails (None) and `is-enabled` says `disabled`, the result is **False** (`H12['']`), contrary to L-UPD "a failed query ⇒ unknown" (H4). File-mode residuals are in H6. |
| G8 | NOTE | **RESOLVED** | `pin_point()` takes no argument; `pin_point(("sys",))` raises TypeError. The test asserts `co_argcount == 0`. |
| G9 | NOTE | **RESOLVED** | not-found with no unit file in any root gives False (`G9b_not_found_no_files`); with a file present it gives None. Q08 is killed. The new branch is weakly pinned: W04, W05 and W07 survive (H2). |
| G10 | NOTE | **RESOLVED** (the listed items) | Ledger 473 `g10_record_corrections_E3` lists every review-62 G10 item: <br>• §11 notes each stale r4 citation; <br>• H6 is restated; <br>• the §3 preamble carries the qualifier; <br>• the harness docstring reads P01–P15; <br>• owner brief r5 is accurate. <br>Two new inaccuracies of the same kind: <br>• "a rejection is permanent" (L-LIFE and ledger 473) is false (H3); <br>• "Trust-relevant test seams are module attributes" is still not wholly true (H5). |
| G11 | NOTE | **RESOLVED** (the listed items) | `OPEN_DECISIONS` has 21 ids, equal to the §4 ids (checked programmatically). `_GATE_DECISION["host_exclusive"]` names three decisions, and live `open_decisions` reports all three. Q13 is killed. The four reader seams that G11 named are listed in §3 "Caller inputs". Other seams are missing from that list (H5). |
| E1 | condition | **RESOLVED** (honoured) | §3 "Citation status" (amendment lines 92–104), the README and ledger 473 cite revision 5 for nothing before this review. |
| E2 | condition | **PARTIALLY RESOLVED**; independence **CARRIED-AS-CONDITION** (acceptable) | **Done:** <br>• L-EXCL, L-PIN and H6 are exact. <br>• D-HOST-LIFETIME carries (i) a ledger REVIEW binding, (ii) a non-coordinator reviewer identity and (iii) blob-level order, and says "The code implements (iii) only". <br>**Not exact:** <br>• L-LIFE (H1, H3); <br>• L-UPD's failed-query clause (H4); <br>• the "Caller inputs" paragraph (H5). <br>Item (iii) is itself only partly implemented (H1). |
| E3 | condition | **RESOLVED** | Ledger line 473 is new. Lines 470–471 are unedited, and 1–472 are a byte prefix of the 37c62102 ledger. |
| E4 | condition | **RESOLVED** | Owner brief r5 lines 27–30: reviews are recorded up to 62, and revision 5's delta review is "not yet recorded". That is true at 37c62102. |

---

## 4. Answers Q2–Q5

### Q2 — Fail-closed audit of revision 5

**Re-run of review 62's probes.** Script `probes63.py`, output `probes63_out.json`. Trust inputs are changed only by
patching module attributes of the scratch copy.

* **Part A:**
  * Power: an unreadable battery type gives None; a UPS discharging gives BATTERY; `Unknown`, garbage, lower case,
    `"Discharging \x00"`, `""` and a status directory give None; `Not charging` and `Full` give AC.
  * The update gate is UNKNOWN for `{}`, `None`, `"true"` and a None reading.
  * A committed attestation with `"REJECTED"`, strings or truthy ints is refused. A forged dict reference and README
    as a reference are both refused.
  * The boot-id gate is UNKNOWN for six bad values. `launched=True` in launcher mode gives FAIL.
  * `attestation_ref` = True, "yes", 1 or a dict gives no number. `root_attested=` raises TypeError.
  * A newborn hog is reported; `own ∋ 1` gives None; a hog that exits is reported; an unreadable pid makes
    `cpu_ticks` None.
  * ESRCH with an unrecorded namespace gives UNKNOWN; a zombie with a full record gives UNKNOWN; a `(deleted)` libm
    mapping gives None.
* **B1–B10:** all refused or fail closed.
  * B1: all three self-acceptance cases are refused.
  * B2: a str, set, list or unknown id raises ValueError. With all 21 ids decided, five gates stay OPEN_DECISION.
  * B3: a forged record gives FAIL in execute and in launcher mode; a float MainPID is refused.
  * B4: all ten malformed records give UNKNOWN, including bool starttime, pidns and timens.
  * B5: AMBIGUOUS.
  * B6: a timer in a second root is not shown disabled.
  * B8: undefined or empty lists raise.
  * B10: a bool or str key is not exempted.
* **G1–G15:** see the table in §3. G13 (caller texts give a complete view) and G14 (a caller MemTotal becomes the
  allowance once the root is attested) are unchanged seams, now named in §3 as never passed by a reviewed caller.
* **Zombie probe (review 59 P6), re-run unchanged** (`probe_zombie_leader_rev5_out.json`): the leader is in Z with
  `Threads: 2`, ticks rise 86→136→186→235, and `identity_state` is **UNKNOWN** on all four readings.
* **`unshare`** (`ns_probe63_out.txt`), with `DECIDED ∋ D-HOST-LIFETIME` and a favourable attestation injected:
  * initial namespaces: `effective_limit` = 14 343 688 192;
  * `--cgroup`: `root_attestation` = false, with a null limit and headroom;
  * `--pid --fork --mount-proc`: `proc_view_complete` = false, `cpu_ticks` sees 1 process, and `busy_processes` returns
    **None**.

**New probes (part H).** All synthetic git repositories are under `scratch/tmp`.

| # | construction | result | finding |
|---|---|---|---|
| H1a/b | directory `reviews/REVIEW_HOST_ATTESTATION_1.md/` holding empty files named `HOST_ATTESTATION_ACCEPTED sha256=<sha>` and `VERDICT: HOST_ATTESTATION_ACCEPTED`, committed **with** the blob; later, any file quoting the line | a: refused (no `-S` hit); b: **valid** | H1 |
| H2a–c | an evil merge adds blob and acceptance together; then a copy of the blob; then a quote of the line | a, b: refused; c: **valid** | H1 |
| H3 | acceptance committed on a branch forked before the blob (not a descendant of it: `H3_acc_commit_descends_from_blob_commit` = false); a quote on main; merge | **valid** | H1 |
| H3b | as H3, but the acceptance was made **before** the blob and dated later | **valid** | H1 |
| H3c | control: H3 without the quote | refused | — |
| H4a–c | a rejecting review is committed, then removed with `git rm`, or moved out of `reviews/` | a: refused; b, c: **valid** | H3 |
| H5 | rejection under a non-ASCII path or a path containing `"` (git quotes it, so `git show` fails); UTF-16; abbreviated, upper-case or path-only sha; "REFUSED", "UNACCEPTED", `VERDICT: …DECLINED`, `NEEDS_REVISION`; rejection in `ledger/` | **valid** in all 11 | H3 |
| H6 | the accepting file also carries `**Verdict:** NEEDS_REVISION`, `## Verdict - DECLINED`, `* VERDICT: …DECLINED` or `DEV_CODE: NOT_FAIL_CLOSED` | **valid** in all 4 | H7 |
| H7 | `attestation_valid(ref, repo_root=<synthetic repo>)` | **valid** (a caller-chosen location) | H5 |
| H8 | `identity_state` with the caller callables `exists`, `stat`, `cmd`, `current_boot` and `current_ns` | **ALIVE** or **DEAD** from callables, with no reading taken | H5 |
| H9 | `busy_processes` with a 100 % hog and `hz=10**9`, `dt_s=1e9` or `threshold_pct=1e9`; empty snapshots; `cpu_ticks(<empty dir>)` | `[]` (no busy process) in each; `{}` | H5 |
| H10 | `preflight(repo_path="/")` vs a nonexistent path | `free_disk_ge_2GiB` PASS vs UNKNOWN (the caller picks the filesystem; the candidate does the same) | H5 |
| H11 | file mode: a `multi-user.target.upholds/` link; a `/run` mask shadowed by an `/etc` unit file with a vendor `.wants` link | both False ("not enabled") | H6 |
| H12 | systemd PID 1, `is-enabled` = `disabled`, `is-active` = None / `refreshing` / `deactivating` / `maintenance` | **False** in each | H4, H6 |
| H13 | a quote of the line committed **before** the blob | refused permanently | H8 |

**Classes not found:**
* No path to **AC** from an unrecognised supply.
* No **CLEAN** (L′ is hard-wired).
* No **numeric allowance** in the shipped state, or in a non-initial cgroup namespace.
* No **PASS** in `preflight` from a failed reading.
* **ALIVE** and a **complete /proc view** arise only through reader seams (H5, G13).
* An **accepted attestation** and **"not enabled"** arise as listed in H1, H3, H4 and H6. Each acceptance path needs
  `DECIDED ∋ D-HOST-LIFETIME`, which is empty as shipped.

**Mutants:** 8 written (§7): **1 killed, 7 survived**. Each survivor changes an outcome on a synthetic input
(`equiv63_out.json`).

### Q3 — Regressions and strictness

**No regression found:**
* **Zombie rule:** `identity_state` is absent from the diff. The P6 probe gives UNKNOWN. M04 and R07 are killed.
* **Pins:** `PIN_KEYS`, `pin_mismatches`, `mapped_objects` and `platform_readings` are unchanged. `pin_point` is
  stricter. M17, M30, R06, Y06 and P15 are killed.
* **durable_write:** absent from the diff. M16, R03, R08 and X05 are killed.
* **R01–R10, X01–X09, Y01–Y09, N01–N14, P01–P15:** all killed in my fresh run. The re-anchored M31, N02, Y03 and
  P01–P04 were checked by eye; each keeps a weakening of the same property.
* **`busy_processes`:** `TestBusy.setUp` now patches `proc_view_complete` to True for the synthetic cases, and the
  live test patches it to the real reading. No synthetic case lost coverage.

**One relaxation, deliberate and correct:** G9's `not-found` → False (with no unit file) replaces revision 4's None. It
needs no file in any of the 13 roots, but that branch is weakly pinned (W04, W05, W07 survive; H2).

**NOTES — stricter, possibly unattainable, stated or not:**
* A quote of the acceptance line anywhere in history **before** the blob refuses the attestation forever (H13). This is
  not stated in L-LIFE (H8).
* A negative word anywhere in an accepting review, or in any file under `reviews/` that names the sha, vetoes
  acceptance. This is stated. The real `reviews/` tree holds many reviews that use "REJECTED" in verdict vocabularies,
  so a review that quotes the full sha with such text vetoes it.
* Acceptance depends on clone depth; this checkout is shallow. This is stated.
* `_strictly_after` (`:1053`) runs `subprocess.run` without a try. A git timeout raises out of `preflight` instead of
  giving UNKNOWN. This fails closed, but by exception (H8).

### Q4 — Amendment r5

* **§3 rows against the code.**
  * Exact: L-PIN, L-EXCL (no argument, no default), H6, L-LAUNCH, L-ID (the Z11 shape is covered by
    `_ident_shape_ok`), L-FREE.
  * Not exact:
    * **L-LIFE:**
      * "the files … named `REVIEW_HOST_ATTESTATION_*.md`": a tree entry is accepted (H1a/b).
      * "the commit that first introduced the accepting line … is a strict descendant of the commit that first
        introduced the attested blob": the code takes the oldest-dated `-S` hit anywhere, never the accepting file's
        own commit, and cannot see merges (H2c, H3, H3b).
      * "a rejection is permanent": a `git rm` lifts it (H4b/c).
      * "any committed file anywhere under `reviews/`": files with quoted names are skipped (H5).
    * **L-UPD:** "any other output, a failed query … ⇒ unknown": a failed `is-active` query with `disabled` gives "not
      enabled" (H12, H4). `.upholds` links and precedence shadowing of masks are not stated (H6).
    * **"Caller inputs":** it omits:
      * `preflight`'s `repo_path`, which decides the free-disk gate (H10);
      * `busy_processes`' `dt_s`, `threshold_pct` and `hz` (H9);
      * `attestation_valid(repo_root=…)` (H7);
      * `identity_state`'s five injectables (H8);
      * `launched_by_systemd(env, proc_cgroup_text, show, pid1, prefix)`, `cpu_ticks(proc_root)`, `boot_id(text)`,
        `systemd_is_pid1(...)`, `mapped_objects` / `platform_readings(maps_text)`, `dpkg_versions(query)` and
        `machine_identity(paths)`.

      The module docstring (`:35–36`) again says "Trust-relevant test seams are module attributes" (H5).
* **§4:** 21 rows, ids equal to `OPEN_DECISIONS` (set equality checked programmatically), and every "amends which
  accepted text / new number" cell is non-empty.
* **E2 carry:** D-HOST-LIFETIME (line 175) lists (i) the ledger REVIEW line, (ii) a reviewer identity that is not the
  coordinator, and (iii) blob-level order, "to be fixed by the formal review before this can be decided". Explicit, and
  acceptable to carry. (iii) is claimed as implemented but is only partly so (H1).
* **[ACCEPTED] quotations:** `quotecheck63` against r5 gives the same 32 results as review 62's run against r4. The
  r4→r5 diff adds no `[ACCEPTED]` line. **None is non-verbatim.** The 4 flagged entries are the same alternate-source
  variants as before.
* **Owner brief r5:**
  * E4 is accurate (see §3).
  * OD-2's "Today's code checks only the commit order" is accurate as a statement about independence. The code also
    checks the set, the verdict and a negative scan.
  * The V-A text is unchanged from r4.

### Q5 — Records

All checks below were redone on the pinned tree.

* **Ledger:** two lines were added after cd86c326, 472 (dd5f3901) and 473 (37c62102), numstat +2/−0.
  * The cd86c326 ledger is a byte prefix of the 37c62102 ledger (lines 1–471), and so is the dd5f3901 ledger
    (lines 1–472).
  * Every one of the 9 bindings in line 473 recomputes from the 37c62102 bytes: amendment r5 `d0963b11…`, owner brief
    r5 `a0142eb0…`, lx_platform `8ccddf85…`, tests `2002dc8d…`, run_mutants `8fc73e9c…`, TEST_RUN `23b350a8…`,
    MUTANTS_RUN `fd5396b3…`, README `239bc085…`, brief 63 `d4f49029…`.
  * Line 472's `review_sha256` `0a54a549…` equals the file and the original
    `scratchpad/review62/REVIEW_CLOUD_R1_DELTA_R4.md`, so review 62 was recorded verbatim.
  * `lx_inventory.py` is unchanged (`8ea74ed3…`, equal to line 469).
* **Review 62's scratch:** all 23 files under `reviews/scratch_CLOUD_R1_DELTA3/` are byte-identical to the originals in
  `scratchpad/review62/`; the scripts were renamed to `*.py.txt` only.
* **TEST_RUN.json:** both hashes equal the committed files, and its boot id equals this boot. My runs on the pinned tree
  (`-B -W error::ResourceWarning`) give **87 OK** on 3.11, 3.12 and 3.13, with no skips (`suite_pinned_python3.1x.txt`).
* **MUTANTS_RUN.json:** my `python3 -B tests/run_mutants.py` (no output argument; stdout in
  `committed_mutants_stdout.json`; empty stderr) equals it in:
  * both hashes;
  * the unmutated PASS;
  * 113/113 killed (R 10, X 9, Y 9, Z 11);
  * every (id, status) pair, in order.

  No mutant was NOT_APPLIED.
* **Byte-unchanged:** `git diff cd86c326..37c62102` is empty for:
  * amendment r1–r4 (r4 `42114202…`, equal to ledger 471) and owner briefs r1–r4 (r4 `1da77fb7…`);
  * reviews 59–61 and their scratch directories;
  * `lx_inventory.py`, `lx_portmap.py` and `PORT_MAP_142D97A9.json`.

  `git diff dd5f3901..37c62102 -- reviews/` is empty, so review 62 and its scratch are unchanged since they were
  recorded. The modified files are the 6 dev-layer files and 2 ledger files; nothing is deleted and nothing outside NS
  is touched.
* **Brief 63:** the recorded file matches the brief I received (visual comparison). Its hash matches line 473.
* **Ledger 473 accuracy:**
  * The counts are correct.
  * Its `process_notes` disclose the 111/113 intermediate run, and Z07 and Q13.
  * Its G10 item "a rejection is permanent" repeats a false statement (H3).
  * "Z05/Z06 … the same weakenings" is loose: they are analogous, not identical (H8).

---

## 5. New findings

**H1 — MAJOR — The acceptance set and the order rule are not what L-LIFE states. Four constructions accept an
attestation whose acceptance was written together with, before, or without the attested blob.**
* **Location:** `lx_platform.py:1069–1086` (`_acceptances` lists tree entries too), `:1043–1046` (`_first_commit` takes
  the oldest-dated hit) and `:1089–1100` (`_ordered`: `acc_path` unused, `-S` repository-wide, merges invisible).
  Amendment L-LIFE (line 146) and D-HOST-LIFETIME item (iii).
* **Evidence** (each with `machine_identity` patched; each needs `DECIDED ∋ D-HOST-LIFETIME` in the gate path):
  * H1b: a directory named as an accepting review, committed **with** the blob; valid once any later commit quotes the
    line.
  * H2c: blob and acceptance introduced together by an evil merge.
  * H3: the accepting commit is not a descendant of the blob commit.
  * H3b: the acceptance was made before the blob.

  The quote that unlocks H1b, H3 and H3b is exactly what carried item (i), a ledger line quoting the acceptance, or any
  later review, would produce.
* **Correction:**
  * Accept only **blob** entries (`ls-tree` type `blob`, mode 100644) in the set.
  * Determine the commit that introduced the accepting line **in the accepting file itself**. Use
    `git log --first-parent -m -S… -- <acc_path>` with `--follow` limits, or `git blame` on the line with `-M -C` on
    the accepting blob. Require that commit to be a strict descendant of the blob's first commit, with merges included
    (`-m` / `--diff-merges=separate` for both searches).
  * Refuse when any `-S` hit for the line or the blob is not ordered (rather than taking the oldest by date).
  * Add tests for the tree entry, evil merge and side-branch cases.
  * Restate L-LIFE.

**H2 — MAJOR — The suite again does not pin several fail-closed properties: 7 of 8 new mutants survive with a
demonstrated change of outcome.**
* **Location:** `tests/test_lx_platform.py` (`test_malformed_records_prove_nothing`,
  `test_accepting_line_must_post_date_the_attested_blob`, `test_acceptance_is_found_not_named`,
  `test_systemctl_path_when_systemd_is_pid1`); `tests/run_mutants.py`.
* **Evidence** (§7, `equiv63_out.json`):
  * W02 and W03: an upper-case cmdline digest or boot id passes the shape check, and the record then proves **DEAD**
    (revision 5: UNKNOWN). This is a malformed record giving death evidence: the P9 / Z11 class.
  * W01: an acceptance written before the blob and quoted later is **accepted**.
  * W06: "revoked" no longer rejects.
  * W04, W05 and W07: not-found with a dangling root link, a non-directory root, or a unit file only in an earlier root
    gives **not enabled** (revision 5: unknown).
* **Correction:** add tests that kill W01–W07 (upper-case digest and boot id; an earlier-root file with a later root;
  a dangling root link; a file as a root; "revoke"; multiple `-S` hits). Add W01–W07 to the harness.

**H3 — MINOR — A rejection is neither permanent nor reliably seen. L-LIFE and ledger 473 state that it is permanent.**
* **Location:** `lx_platform.py:1069–1076`; amendment L-LIFE ("a rejection is permanent", "any committed file anywhere
  under `reviews/`"); ledger 473 G10 item 7.
* **Evidence:**
  * H4b/c: after `git rm` of the rejecting review, or `git mv` out of `reviews/`, the attestation is **valid**. Only
    HEAD is scanned.
  * H5: these are not seen:
    * paths that git quotes (non-ASCII, `"`): the quoted name makes `git show` fail, and the failure reads as an empty
      file;
    * UTF-16 text;
    * abbreviated, upper-case or path-only references to the attestation;
    * the words refused, unaccepted, declined, NEEDS_REVISION;
    * a rejection recorded in the ledger.
* **Correction:**
  * Use `ls-tree -z` and treat a failed `git show` as a rejection (fail closed).
  * Scan the whole history (`git log -p` / `-S<sha>` across `reviews/` and `ledger/`), or bind rejection to the ledger
    (carried item (i)).
  * Match the sha case-insensitively and by any 8+-hex prefix.
  * Treat any verdict other than the accepting one as negative.
  * Correct L-LIFE and record the correction in a ledger line.

**H4 — MINOR — A failed `systemctl is-active` query followed by `is-enabled` = `disabled` gives "not enabled".**
* **Location:** `lx_platform.py:744–752`; amendment L-UPD ("a failed query … ⇒ unknown").
* **Evidence:** H12 with `is-active` = None gives **False**. A disabled unit can be running (the G7 rationale), so
  without an `is-active` reading "disabled" does not show it is off.
* **Correction:** `if act is None: return None`. Add a test (an `is-active` failure combined with each is-enabled
  state).

**H5 — MINOR — The caller-input and seam enumeration is incomplete, and the docstring repeats an overstatement.**
* **Location:** amendment §3 "Caller inputs" (lines 108–121); `lx_platform.py:35–39` and `:1110`
  ("`repo_root` is a location … not an assertion").
* **Evidence:**
  * H7: a caller `repo_root` accepts an attestation.
  * H8: `identity_state` callables give ALIVE or DEAD.
  * H9: `hz`, `dt_s` and `threshold_pct` turn a 100 % hog into `[]`, and `cpu_ticks(proc_root=<empty>)` gives `{}`.
  * H10: `repo_path` decides `free_disk_ge_2GiB` (as in the candidate's `preflight_gates`).

  None of these reaches a `preflight` PASS except H10 (by design).
* **Correction:** list every such parameter in §3 as a test seam a reviewed caller never passes, or as a caller input
  with its required source (`dt_s` from CLOCK_MONOTONIC, `threshold_pct` = the decided R-EXCL-PCT number, `repo_path` =
  the campaign store). Better, move `repo_root`, `hz` and the `identity_state` injectables to module attributes.
  Correct the docstring.

**H6 — NOTE — Update-unit detection: residual gaps.**
* **File mode** (used only when systemd is not PID 1, where units do not run in this namespace):
  * `*.upholds` links are ignored (H11a);
  * a mask is honoured even when a higher-precedence root holds a real unit file (H11b).
* **systemd mode:** `is-active` states `deactivating`, `refreshing` (systemd ≥ 257) and `maintenance` with `disabled`
  give False (H12). `unattended-upgrades.service` performs its install in ExecStop, that is, while deactivating.
* **Correction:** state these in L-UPD, or treat any `is-active` state other than `inactive` / `failed` as True and
  count `.upholds`.

**H7 — NOTE — The single-verdict rule only recognises lines that start with `verdict:`.**
* **Location:** `lx_platform.py:1058`, `:1083`.
* **Evidence:** H6 probes: `**Verdict:**`, `## Verdict -`, `* VERDICT:` and `DEV_CODE: NOT_FAIL_CLOSED` in the
  accepting file are each accepted. This repository's reviews state verdicts as `KEY: VALUE` lines.
* **Correction:** refuse an accepting file that contains any verdict-like token other than the accepting line, for
  example any `\bVERDICT\b`, or any line `^[A-Z0-9_]+: [A-Z_]+$` other than the accepting one. Or rely on the ledger
  binding.

**H8 — NOTE — Record and wording items.** Correct these in a new ledger line or the next revision, never by editing
recorded lines.
* L-LIFE does not state that a quote of the line before the blob blocks acceptance forever (H13).
* `_strictly_after` (`:1053`) has no try around `subprocess.run`, so a timeout raises out of `preflight`.
* `_ordered(..., acc_path, ...)` declares a parameter it never uses, which hides H1.
* Amendment §13 (G4) and ledger 473 call the harness Z05 / Z06 "the same two weakenings"; they are new weakenings of
  `_ordered`.
* Ledger 473 G10 item 7 records "a rejection is permanent" as a stated side effect; it is false (H3).

**Counts:** BLOCKING 0 · MAJOR 2 (H1, H2) · MINOR 3 (H3, H4, H5) · NOTE 3 (H6, H7, H8); 8 new findings in total.

---

## 6. Conditions

* **C1 (citation).** Revision 5 (sha256 `8ccddf85…`) may be referenced as the DEV_ONLY implementation of:
  * L-ID (with W02 and W03 open), L-BOOT, L-POWER, L-SLEEP, L-LAUNCH;
  * L-FREE (a gated reader);
  * L-DISK (with `repo_path` named as a caller input) and L-FSYNC;
  * L-EXCL as a reader (the view is now read inside);
  * the L-PIN pin point (no override; the list is undefined).

  It may **not** be cited for L-LIFE (H1, H3) or L-UPD (H4; W04, W05 and W07 open) before a revision that fixes them
  and kills W01–W07, and a fresh delta review that confirms both.
* **C2 (amendment).** r6, or explicit conditions carried into the formal route review, must:
  * restate L-LIFE (tree entries, how "first" is determined, merges, rejection permanence and visibility, the H13 side
    effect);
  * restate L-UPD's failed-query clause;
  * complete "Caller inputs" (H5).

  The independence items (i)–(iii) stay carried. Item (iii) must not be described as implemented until H1 is fixed.
* **C3 (records).** Add a ledger line correcting ledger 473's "a rejection is permanent" and the Z05 / Z06 wording.
  Do not edit lines 472–473.
* **C4 (owner brief).** The next owner brief must not say that the code implements blob-level commit order (item
  (iii)) without H1's qualification, and must not say that revision 5's delta review is recorded until it is.

---

## 7. Reviewer mutants (brief 63)

**Method:**
* Each mutant was applied to the scratch copy of `lx_platform.py` (sha256 `8ccddf85…`, equal to 37c62102) in a
  temporary directory under scratch.
* The **unchanged** suite of the pinned tree was run against it with `LX_PLATFORM_DIR=<copy>`, `-B` and
  `PYTHONDONTWRITEBYTECODE=1`.
* The base copy passes (`OK`).
* Script `reviewer63_mutants.py`, results `reviewer63_mutants_result.json`, outcome checks `equiv63.py` and
  `equiv63_out.json`.

**Result: 8 written, 1 killed, 7 survived.** Every survivor changes an outcome in the weakening direction.

```
### W01 SURVIVED | the LATEST commit touching the accepting line is taken as 'first'
###     (acceptance committed before the blob, quoted later: refused -> ACCEPTED)
@@ -1046 +1046 @@
-    return lines[0] if lines else None
+    return lines[-1] if lines else None

### W02 SURVIVED | upper-case cmdline digest passes the record shape check   (UNKNOWN -> DEAD)
@@ -214 +214 @@
-    return c is None or (isinstance(c, str) and re.fullmatch(r"[0-9a-f]{64}", c) is not None)
+    return c is None or (isinstance(c, str) and re.fullmatch(r"[0-9a-fA-F]{64}", c) is not None)

### W03 SURVIVED | upper-case boot id passes the record shape check   (UNKNOWN -> DEAD)
@@ -207 +207 @@
-    if b is not None and (not isinstance(b, str) or not _BOOT_ID.match(b)):
+    if b is not None and (not isinstance(b, str) or not _BOOT_ID.match(b.lower())):

### W04 SURVIVED | not-found: a dangling unit link in a root is not a unit file   (None -> False)
@@ -730 +730 @@
-        found |= f.is_symlink() or f.exists()
+        found |= f.exists()

### W05 SURVIVED | not-found: a unit root that is not a directory is skipped   (None -> False)
@@ -728 +728 @@
-            return None
+            continue

### W06 SURVIVED | 'revoke' is not a negative word   (a revoking review: refused -> ACCEPTED)
@@ -1059 +1059 @@
-_NEGATIVE = re.compile(r"reject|withdraw|not[ _-]?accepted|revoke", re.I)
+_NEGATIVE = re.compile(r"reject|withdraw|not[ _-]?accepted", re.I)

### W07 SURVIVED | not-found: only the last root decides whether a unit file exists   (None -> False)
@@ -730 +730 @@
-        found |= f.is_symlink() or f.exists()
+        found = f.is_symlink() or f.exists()

### W08 KILLED (test_failed_systemctl_query_is_no_reading, test_systemctl_path_when_systemd_is_pid1)
###     a failed is-enabled query treated like not-found
@@ -753 +753 @@
-        if st == "not-found":
+        if st in ("not-found", None):
```

**Committed harness, re-run by this reviewer** (no output file; run before the checkout switch, on bytes equal to the
pinned tree):
* unmutated suite PASS;
* **113/113 killed**: R 10/10, X 9/9, Y 9/9, Z 11/11, Q 13/13, plus M, N and P;
* both sha256 values equal `MUTANTS_RUN.json`, and every (id, status) pair is identical.
