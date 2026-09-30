# Brief: independent confirmation of the qualification-failure postmortem (formal campaign p5y_k5_cell309_p309_r1)

This brief is committed before it is issued (condition C5).

**Reviewer.** A new independent reviewer who wrote none of the campaign's code and is not the coordinator.

## Authority and boundaries (read first)

No grant exists. **NEW Γ309 TARGET EVALUATIONS must stay 0.**
* Never create, arm or consume any ref under `refs/p5y-k5-cell309-p309-r1/`.
* Never run `execute`, `seal-only` or `validate-grant` against this repository.
* Do not rerun the qualification or any part of it as evidence (A27).
* The common firewall applies:
  * no value for cells 305–309;
  * no cell-307 or cell-308 campaign file beyond git metadata;
  * no git writes;
  * write only your output file.
* The QC09 decoy outputs (cover cells 297 and 316) are latent-proxy class (delta-2 E5): never quote their per-cell
  results.
* Ledger any run through `code/p309_env.py`, with notes prefixed "PM reviewer:". Send evidence to a scratch
  `P309_EVIDENCE_DIR`.

## What to check

The coordinator's report is `handoff/QUALIFICATION_FAILURE_POSTMORTEM_P309.md`. The preserved attempt is in commit
`f433d490`. Check each item independently, with evidence:
1. **The freeze.** F `4c754a73…` and FR `2f66bc56…`:
   * FR is F's only child and changes only `ledger/FREEZE_RECORD.json`;
   * the manifest and parameters hashes are as stated;
   * the placeholder-check history (the preserved failure, and the fix before F) is as described.
2. **One attempt.** Exactly one `QUALIFICATION RUN START` line after the freeze record. `attempt_1` is unaltered
   relative to the runner's writes, and no summary was fabricated.
3. **Q11's root cause.** Confirm or refute from the code and git history: the QC11 sandboxes inherit the real freeze
   record, so `recorded_freeze` sees two commits. You may make one TEST-only scratch sandbox as a diagnostic; label
   it as not qualification evidence.
4. **The classification.** A deterministic, target-free harness defect that only shows after a real freeze, with the
   production path unaffected. Also check the claim that the QC-D5 backstop controls share the harness.
5. **The interruption.** The host reboot time against the runner's last write.
6. **Governance.** Does A27, together with the owner's "QUALIFICATION FAILURE" rule, require stopping here? Is any
   in-place repair permitted?
7. **Target integrity.** No production ref anywhere, no grant, ledger target evaluations 0, r5 unchanged, no r6,
   cell 308 untouched.
8. **The successor notes (§6).** Are they accurate and bounded? They are advice for an owner decision, not actions.

## Output

`reviews/REVIEW_QUALIFICATION_POSTMORTEM_P309.md`, with line 2 exactly one of:
* `POSTMORTEM_CONFIRMED`;
* `POSTMORTEM_DISPUTED`, with reasons.

Include a section headed exactly `## Findings`, and a disclosure section listing your reads and runs.
