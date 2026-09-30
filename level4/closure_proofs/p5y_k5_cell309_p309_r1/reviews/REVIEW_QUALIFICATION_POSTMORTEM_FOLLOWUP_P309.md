# Postmortem review follow-up: does the report's section 7 resolve D1–D5? (formal campaign p5y_k5_cell309_p309_r1)
CORRECTIONS_DISPUTED

**Reviewer.** The independent postmortem reviewer ("PM reviewer"), author of
`reviews/REVIEW_QUALIFICATION_POSTMORTEM_P309.md`. I wrote none of the campaign's code and I am not its coordinator.

**Brief.** `reviews/BRIEF_QUALIFICATION_POSTMORTEM_FOLLOWUP_P309.md`, committed before issue at `a5f5cb09`.

**State reviewed.**
* HEAD `9fefd218`, which is linear on top of `91a5747f` through `c7e0ff51`, `a491a453` and `a5f5cb09`.
* The report is `handoff/QUALIFICATION_FAILURE_POSTMORTEM_P309.md` at `c7e0ff51`, which is also its blob at HEAD.

**NEW Γ309 TARGET EVALUATIONS = 0.** This follow-up ran no campaign code and created no ref.

## Verdict in brief

The dispute is narrow.
* **D1, D2, D3 and D5** are applied accurately, in my words.
* **My firewall disclosure** is recorded fairly.
* **Nothing above section 7 changed.**

I dispute two points:
* **(F1) D4 does not resolve the restart account, and part of that is my fault.** My first review failed to dispute
  "That was the second restart in this session". The committed record contradicts it. The basis sentence the
  coordinator added to D4 also implies another in-session boot.
* **(F2) Section 7's summary overstates my counterfactual.**

Neither point touches the verdict, the stop, the target counter or the successor route. Exact corrections are at the
end.

## Findings

### 1. Nothing else in the report changed: confirmed

**The report.**
* It is touched only by `2b149412` and `c7e0ff51`.
* All 6 278 bytes of the `2b149412` version are a byte prefix of the `c7e0ff51` version (`cmp -n`).
* The only diff hunk is `@@ -120,0 +121,46 @@`: 46 appended lines, which are section 7.
* The blob `be699328` is the same at `c7e0ff51`, at HEAD and in the working tree.

**The rest of `c7e0ff51`.** Beyond the report, it adds only these:
* my review, blob `e8603004`, identical to the file I wrote; sha256 `00531409…`, matching the committed `.sha256`
  file;
* `REVIEW_QUALIFICATION_POSTMORTEM_P309_EXEC_LEDGER.jsonl`, which is my complete first-review scratch ledger, 26
  lines, a byte prefix of my current scratch ledger;
* one execution-ledger row, 1421: my diagnostic row, unchanged. The ledger stays append-only: `91a5747f` is a prefix
  of `c7e0ff51`, which is a prefix of HEAD, which equals the working tree.

**Later commits.** `a491a453` and `9fefd218` change only `ledger/CHECKPOINT_PUSHES.jsonl`, and `a5f5cb09` adds only
the brief.

**Integrity is unchanged.**
* No frozen-directory change since F.
* No path outside the namespace changed since `91a5747f`.
* No ref under `refs/p5y-k5-cell309-p309-r1/` or `refs/p309-test/`.
* No ledger row with nonzero target evaluations.

### 2. D1–D5 as applied

* **D1 (§3, QC-D5): accurate.** It is my wording verbatim.
* **D2 (§5): accurate.** It is my wording verbatim.
* **D3 (§1): accurate.** It is my wording, with "This review's item 1" changed to "The postmortem review's item 1".
  That change is correct.
* **D5 (§6.5): accurate.** "QC01–QC-U2" versus my "QC01–QC_U2" is immaterial.
* **D4 (§4): accurate to my words, but it does not resolve the account. See F1.**
  * **What D4 now says.** The first sentence is mine. The bullet then adds a sentence that is not mine but is
    explicitly attributed: "The coordinator's basis was its own session observations: a restart notice, then `uptime`
    showing 12 h 57 min and the detached dry run still alive". Given that attribution, putting it under "in the
    reviewer's words" is acceptable.
  * **Checking the added basis.** The host keeps no boot record: `journalctl --list-boots` finds no journal files, and
    `wtmp` is empty. The `uptime` reading therefore cannot be checked.
  * **"The detached dry run still alive" is partly corroborated.** The pre-freeze dry run's two decoy Stage-1b ledger
    rows (1168 at 14:17:34Z and 1169 at 15:20:04Z) are 62.5 min apart. The same step took 61 min in the official run
    (18:35:18Z → 19:36:18Z). This fits a process that continued across about 15:19Z. I use timestamps only; no decoy
    content was read.

### 3. F1: the restart count is contradicted by the record (my omission, now corrected)

**The report's words.** Section 4, which stays in force above section 7, says: "That was the second restart in this
session; the first, around 15:19Z, restarted only the harness". My D4 marked the 15:19Z account as unverified. It did
not dispute the count, although I noted that "The recovered briefs record restarts on 2026-09-29 only".

**The record contradicts the count.**
* `governance/briefs_recovered/README.md` states that it reproduces "every instruction the coordinator gave to another
  agent **in this session**".
* Its items 7 and 14 are labelled "Resume after container restart" (2026-09-29T15:10:32Z) and "Resume C3 v2 rerun
  after container restart" (2026-09-29T23:36:27Z).
* Section 4 itself calls the 22:41:12Z event "The cloud container restarted". By its own vocabulary, then, the
  committed record shows at least two earlier container restarts in this session. The reboot at 22:41:12Z is not the
  second.

**The added basis makes it worse.** Suppose `uptime` read 12 h 57 min shortly after the notice at about 15:19Z.
* The host would then have booted at about 02:22Z on 2026-09-30.
* That is after the campaign's first commit (`47b55d00`, 01:42:12Z) and inside a recorded gap in activity: no commit
  between 01:49:34Z and 02:31:22Z, and no ledger row between 01:42:12Z and 02:35:57Z.
* That would be another in-session boot that the count omits.

I cannot confirm that boot, but the report's own basis implies it.

**Why it matters.** The count is immaterial to the attempt: all of these events predate F. But "second restart" is a
stated fact in a preserved report, the record contradicts it, and my first review should have caught it.

### 4. F2: section 7 overstates my counterfactual

**What section 7 says.** "Q11's root cause, including a counterfactual (the same synthetic chain placed on the real F
passes)".

**What I actually ran.**
* A synthetic freeze `9b06b824` and freeze record `c81393f7` were placed on the real F.
* `recorded_freeze` at `c81393f7` returned `9b06b824`.
* It was not the full `build_chain` chain (Q, Rv, G), and it ran no QC11 flow.
* My review says "it tests only that function, not QC11 as a whole".

**Why it matters.** "The same synthetic chain … passes" can be read as the whole chain, or QC11, passing. That would
matter to a successor's harness fix (§6, note 3).

### 5. The firewall disclosure is recorded fairly: confirmed

**The recorded facts are correct.**
* The four paths are right.
* "content never displayed; only hash equality printed" is right.
* The switch to blob-ID comparison is right.
* "This departs from the brief's 'no cell-307 … campaign file beyond git metadata'" is right.
* "No cell 305–309 value was read" is right.

**The coordinator's added sentence is also accurate.** It reads: "The reads are the same class as the freeze-manifest
generator's pin hashing of those same files".
* `code/make_freeze_manifest.py` (lines 66–68) reads each pinned file's bytes into sha256 and the git blob hash.
* All four files are code pins with sha256 values: `RLR307_FREEZE.json` `bd53e37c…`, `rlr307_stage1.py` `cadb9f83…`,
  `rlr307_independent.py` `85397b55…`, `rlr307_pinned.py` `21ce4c46…`. I compared these by blob ID only.
* The sentence adds context and does not withdraw the stated departure.

The section omits my two affirmative notes: that no QC09 decoy output was opened, and that the diagnostic sandbox's
checkout copies were deleted unread. Neither is a departure, so the omission is not unfair.

## Required corrections (additive; none applied by me)

* **F1 (§4 count; extends D4).** In section 7's D4, add: "The count 'That was the second restart in this session' is
  also withdrawn. `governance/briefs_recovered/README.md` records two container restarts in this session on
  2026-09-29 (items 7 and 14). The coordinator's `uptime` basis would also place a host boot at about 02:22Z on
  2026-09-30. The 22:41:12Z reboot is therefore at least the third restart in this session."
* **F2 (section 7 introduction).** Replace "(the same synthetic chain placed on the real F passes)" with "(a synthetic
  freeze and freeze record placed on the real F pass `recorded_freeze`; no QC11 flow was run)".

## Disclosure (reads, runs, writes)

**Reads.** Paths relative to the formal namespace:
* the follow-up brief;
* the report at `c7e0ff51`: lines 118–167, plus prefix and diff checks against `2b149412`;
* the name-status diffs of `c7e0ff51`, `a491a453`, `a5f5cb09` and `9fefd218`;
* the committed review, `.sha256` and EXEC_LEDGER files, compared with my own;
* the execution ledger: row counts and prefixes; the `utc`, `script` and `class` of rows 1–13 and 1161–1172; the
  target counters;
* `governance/briefs_recovered/README.md`, lines 1–20 and its table rows 7 and 14;
* `code/make_freeze_manifest.py`, by grep;
* the manifest's four cell-307 pins: paths, the presence of sha256, and blob ids. This is metadata only; no cell-307
  or cell-308 bytes were read or hashed.

**Runs.**
* Read-only git: `rev-parse`, `log`, `diff`, `show`, `hash-object` on my own review file, `for-each-ref`, `status`.
* `cmp`, `journalctl --list-boots`, `ls /var/log`.
* No campaign code was run, so this follow-up adds no execution-ledger row.

**Writes.**
* This file.
* Scratch entries appended to
  `/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/pm_review/PM_LEDGER.jsonl`,
  from line 27 on.
* Temporary scratch copies of committed ledger versions, deleted after use.
* No git write.

**Firewall.** No value for cells 305–309 was read. No QC09 decoy output was opened, and no decoy result is quoted;
only the timestamps of two dry-run ledger rows are used.
