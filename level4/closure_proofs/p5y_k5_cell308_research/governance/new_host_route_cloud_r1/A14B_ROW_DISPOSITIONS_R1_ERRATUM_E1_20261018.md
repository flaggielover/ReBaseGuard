# Erratum E1 to the A14b row dispositions r1 (Cell-308 Cloud route r1): chronology limit, a further contact class, and the R6b wording

**Status: ADDITIVE FACTUAL DISCLOSURE AND ADMINISTRATIVE CORRECTION (coordinator, under owner statement 5 §2).**
This erratum amends `A14B_ROW_DISPOSITIONS_R1_20261017.md` (`9aebe666…8b04`), which is preserved unchanged. Its §1
disclosure stands as written. No contact event is cleared. `new_target_evaluations = 0` · `cell309_activity = none`.

## E1.1 — The limit of the chronology argument (attached to r1 §1, "Timing")

The sentence "C-1 and C-2 therefore cannot have influenced them" is limited as follows.

* It concerns only the identified text versions committed before the identified events C-1 and C-2.
* It does **not** establish any of the following:
  * that no earlier contact occurred;
  * general historical cleanliness;
  * the independence of later drafting;
  * that there is no influence on future reuse or interpretation of those texts.

## E1.2 — A further contact class: the pre-commit quarantine scan (C-5)

**What the check does.** The required pre-commit check `python3 -B code/c308_quarantine.py --scan` calls
`scan(root=NS)`. That runs `_scan_tree`, which walks the whole research namespace with `rglob`. It reads every `*.py`
file and every `.md`, `.json`, `.txt` and `.jsonl` file (`code/c308_quarantine.py` lines 326–330 and 376–377). That
set includes the excluded files:
* `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`;
* `audit/*`;
* `reviews/REVIEW_EXECUTION_INTERRUPTION*`;
* `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`.

Each run is therefore a **process content scan of excluded files**. The scanner matches them against the tail-figure
patterns. It reports findings outside `history/` and `ledger/` as failures, and records matches inside them as
sanctioned.

**Runs known within my available context.** I ran it once before each of commits `b9860515` and `412214d8`. Each run
printed only its last lines, or its `"verdict"` line, which read **PASS**. No finding line was displayed.

**Earlier runs.** According to the compaction summaries, running this scan before commits was standing practice for
this coordinator throughout the session. The **number of earlier runs, and what each displayed, are UNKNOWN** in my
available context.

**Saved outputs.** The scanner's full JSON output contains a `sanctioned_text` list. That list records every tail-figure
match found in `history/` and `ledger/` files, together with the matched text. `ledger/` contains the register.
* The coordinator's scratchpad holds files named `scan.json` through `scan6.json` from earlier in this session. Their
  names were seen in a listing of the scratchpad root during this conversation.
* Within my available context they have **not been opened**. Whether they hold sanctioned-text matches from excluded
  `ledger/` files is UNKNOWN.
* They are **left unopened and undeleted**. Deleting them would destroy possible evidence. What to do with them is the
  owner's decision.

**State under MA1.** C-5 is a contact event. Its display of PASS only, or of nothing, does **not** clear it.

**Conflict reported, not repeated (statement 5 §2).** The full-namespace `--scan` was **not** run for this commit.
* In its place, the scanner's own `_scan_tree` function was run on a scratch copy containing **only the files staged
  for this commit**, with its planted controls. The scope is explicit and every file in it is permitted.
* The `"verdict"` is reported below.
* **This substitute is not an approved replacement.**

Whether the pre-commit check should be scoped this way is the owner's decision. Changing the scanner's code would be
a change to a quarantine tool, and that is outside the coordinator's current limits. Until the owner decides:
* the coordinator runs only the scoped form;
* the coordinator does not run `--scan`;
* the coordinator makes no change to the scanner.

## E1.3 — R6b wording (r1 §2, row R6b; r1 §5, item 5)

**Withdrawn:** the references to B3's advisory use as adopted "in statement 1B item 1". **Statement 1B has not been
issued.**

**Replaced by the state the owner issued in statement 5 §5: ADVISORY_USE_ACCEPTED_WITH_LIMITATIONS.**
* This is kept apart from any formal eligibility dimension.
* Every use that needs standing or separation the evidence does not establish stays **UNRESOLVED**.
* r1's proposed "ESTABLISHED_ELIGIBLE" for R6b is superseded by this owner-issued state.

## E1.4 — States now in force (owner statement 5 §1, §5)

| rows | state |
|---|---|
| R1a, R1b, R2, R3a–R3c, R6a | **UNRESOLVED** (material dimensions as in r1 §2) |
| R4-59…R4-71, R5a–R5c | excluded **only** for uses that need a reviewer outside the coordinator's reach. Exposure states are kept separately, as r1 §2 records them |
| owner-assistance Codex `01a13b76…` | excluded from the fresh A6b tracer role |
| R6b | **ADVISORY_USE_ACCEPTED_WITH_LIMITATIONS**; UNRESOLVED for other uses |
| every ER-T6 result | CANNOT_TELL |
