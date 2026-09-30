# Postmortem review follow-up 2: does the report's section 8 apply F1 and F2? (formal campaign p5y_k5_cell309_p309_r1)
CORRECTIONS_CONFIRMED

**Reviewer.** The independent postmortem reviewer ("PM reviewer"), author of
`reviews/REVIEW_QUALIFICATION_POSTMORTEM_P309.md` and `reviews/REVIEW_QUALIFICATION_POSTMORTEM_FOLLOWUP_P309.md`. I
wrote none of the campaign's code and I am not its coordinator.

**Instruction.** The coordinator's message for this second follow-up. The boundaries are unchanged: no git writes;
blob IDs only for cell-307 and cell-308 files; write only this file.

**State reviewed.**
* HEAD `988199b7`, linear on top of `9fefd218` through `5f76c1bf`.
* The report is `handoff/QUALIFICATION_FAILURE_POSTMORTEM_P309.md` at `5f76c1bf`: blob `a96a5f21`, the same at HEAD
  and in the working tree.
* **HEAD moved while I was writing.** It is now `6fafd568`, after two further commits:
  * `0a515d4c` adds only `handoff/OVERNIGHT_REPORT_P309.md`, a draft;
  * `6fafd568` changes only `ledger/CHECKPOINT_PUSHES.jsonl`.

  I re-checked at `6fafd568`. The report and my six files are unchanged since `5f76c1bf`, and every statement below
  still holds. The overnight report is outside this follow-up's scope and I have not reviewed it.

**NEW Γ309 TARGET EVALUATIONS = 0.** This follow-up ran no campaign code and created no ref.

## Findings

### 1. Section 8 applies F1 and F2 accurately: confirmed

I compared the texts after normalising whitespace.

**F1.** The quoted sentence added to section 7's D4 is identical to my F1 text. It reads: "The count 'That was the
second restart in this session' is also withdrawn. … The 22:41:12Z reboot is therefore at least the third restart in
this session."
* The withdrawn phrase still stands, verbatim, in section 4, which is what F1 addresses.
* I re-checked F1's premise at its source, `governance/briefs_recovered/AGENT_BRIEFS_TRANSCRIPT.jsonl`, items 7 and 14.
  Item 7 (2026-09-29T15:10Z) says "the container restarted and your process was killed". Item 14 says "A container
  restart (about 23:3xZ) interrupted … Your process was killed".
* The README says these are instructions "in this session". F1 therefore stands, and "at least the third" is the
  conservative count.

**F2.** Both the replaced phrase and the replacement are identical to my F2 text.
* The replaced phrase, "(the same synthetic chain placed on the real F passes)", occurs in section 7's introduction.
  It occurs once more in the whole report, as the quotation inside section 8.
* The replacement is "(a synthetic freeze and freeze record placed on the real F pass `recorded_freeze`; no QC11 flow
  was run)".

**Section 8's summary is accurate.** It says my follow-up confirmed D1, D2, D3 and D5 as applied, the disclosure as
recorded, and that nothing else changed. It also says "Neither changes the verdict, the stop, the target counter or
the successor route". That is a faithful paraphrase of my wording.

### 2. Nothing before section 8 changed: confirmed

* The report is touched only by `2b149412`, `c7e0ff51` and `5f76c1bf`.
* The `c7e0ff51` version (9 280 bytes) is a byte prefix of the `5f76c1bf` version (10 382 bytes), by `cmp -n`. So
  sections 1–7 are unchanged. The `2b149412` version (6 278 bytes) is also a byte prefix.
* The only diff hunk is `@@ -166,0 +167,17 @@`: 17 appended lines, which are section 8.

### 3. My follow-up files were committed unchanged: confirmed

* **`REVIEW_QUALIFICATION_POSTMORTEM_FOLLOWUP_P309.md`:** blob `3cc55381` in the working tree, at `5f76c1bf` and at
  HEAD. Its sha256 `0edf3686…c41021e` matches the committed `.sha256` file.
* **`REVIEW_QUALIFICATION_POSTMORTEM_FOLLOWUP_P309_EXEC_LEDGER.jsonl`:** sha256 `2bceef71…23fee7`, matching the
  `.sha256` file.
  * It is a byte prefix of my scratch ledger, lines 1–30.
  * Line 30 is my last follow-up-1 entry (23:06:47Z), before the commit time of `5f76c1bf` (23:07:21Z). The copy was
    therefore complete when it was committed.
  * Lines 31 onward are this follow-up's.

**The rest of the tree is unchanged.**
* `5f76c1bf` touches only the report and those three files. `988199b7` touches only `ledger/CHECKPOINT_PUSHES.jsonl`.
* My first review's three files are unchanged since `c7e0ff51`.
* Since `9fefd218`: the execution ledger is unchanged (1421 rows) and no path outside the namespace changed.
* No frozen-directory change since F.
* No ref under `refs/p5y-k5-cell309-p309-r1/` or `refs/p309-test/`.

## Observation (process; not a dispute of the corrections)

This second follow-up was issued by message only. No `BRIEF_QUALIFICATION_POSTMORTEM_FOLLOWUP_2*` exists in any
commit. The first two briefs were committed before issue (condition C5).
`governance/briefs_recovered/README.md` says "From now on every brief is committed before it is issued".

For the record, the coordinator may commit the message verbatim as a brief and disclose that it was committed after
issue.

## Disclosure (reads, runs, writes)

**Reads.** Paths relative to the formal namespace:
* the report at `5f76c1bf`: lines 145–184, plus prefix and diff checks against `c7e0ff51` and `2b149412`;
* the name-status of `5f76c1bf` and `988199b7`;
* my committed follow-up review, its `.sha256` and its EXEC_LEDGER, compared with my own files;
* `governance/briefs_recovered/AGENT_BRIEFS_TRANSCRIPT.jsonl`, items 7 and 14 (the first 330 characters).

**Runs.**
* Read-only git: `rev-parse`, `log`, `diff`, `show`, `hash-object`, `for-each-ref`, `status`.
* `cmp`, `sha256sum`.
* One Python text comparison over those files.
* No campaign code was run, so this follow-up adds no execution-ledger row.

**Writes.**
* This file.
* Scratch entries appended to
  `/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/pm_review/PM_LEDGER.jsonl`,
  from line 31 on.
* No git write.

**Firewall.** No cell-307 or cell-308 file was read or hashed, no value for cells 305–309 was read, and no QC09 decoy
output was opened.
