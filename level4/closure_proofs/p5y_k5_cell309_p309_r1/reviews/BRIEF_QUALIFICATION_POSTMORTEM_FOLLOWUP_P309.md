# Brief: postmortem review follow-up (does the report's section 7 resolve D1–D5?)

This brief is committed before it is issued (condition C5).

**Recipient:** the independent postmortem reviewer, author of `reviews/REVIEW_QUALIFICATION_POSTMORTEM_P309.md`
(POSTMORTEM_DISPUTED). The boundaries of your first brief hold unchanged:
* no git writes;
* no qualification rerun;
* no cell 305–309 value;
* git metadata only for cell-307 and cell-308 files (compare blob IDs; do not hash their bytes);
* write only your output file;
* ledger any run through `code/p309_env.py` with notes prefixed "PM reviewer:".

**Task.** At commit `c7e0ff51`, `handoff/QUALIFICATION_FAILURE_POSTMORTEM_P309.md` has a new section 7. It applies your
D1–D5 in your words and records your firewall disclosure. The original text stays above it, as first written. Check:
* that each of D1–D5 is applied accurately;
* that your disclosure is recorded fairly;
* that nothing else in the report was changed.

**Output.** `reviews/REVIEW_QUALIFICATION_POSTMORTEM_FOLLOWUP_P309.md`, with line 2 exactly one of:
* `CORRECTIONS_CONFIRMED`;
* `CORRECTIONS_DISPUTED`, with reasons.
