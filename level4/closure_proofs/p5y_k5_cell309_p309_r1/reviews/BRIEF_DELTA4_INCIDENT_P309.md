# Brief: incident-independence review of the FOURTH rev. 2c delta (conditions C2, D8; delta-3 G8, G9)

This brief is committed before it is issued (condition C5).

**Recipient:** the independent incident-independence reviewer, author of:
* `reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`;
* `reviews/REVIEW_U2_CHECK_P309.md`;
* `reviews/REVIEW_DELTA_INCIDENT_P309.md`;
* `reviews/REVIEW_DELTA2_INCIDENT_P309.md`;
* `reviews/REVIEW_DELTA3_INCIDENT_P309.md`.

## Question

R4's follow-up 2 blocked the freeze: `reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_2_P309.md`, F3, with conditions R4F2-C1 to C4.
The resolution is the commit that adds this brief, recorded in the append-only section "Fourth delta" (A37–A42) of
`governance/P309_REV2C_AMENDMENTS.md`, with an addendum to `governance/D5_SITE_BACKSTOP_REPORT_P309.md`.

Your G8 and G9 make any further rule, parameter or binding change a new delta under C2. The rows marked as such are:
* **A38.** The backstop is pinned by AST hash. Its code is unchanged.
* **A40.** `execute`'s git environment now ignores the host's system and global configuration and uses a fixed commit
  identity. A new pre-marker refusal, `check_host_git`, applies to the repository's own config and hooks.

A37 (scanner schema 5), A39 (validate-grant runs `execute`'s read-only pre-checks; delta-3 G4 already classed this as an
implementation change), A41 (QC flows and checks) and A42 (the verifier helper's `--end-of-options`) are marked as
implementation or controls.

For every row A37–A42: is the change **temporally and parametrically independent** of the exposed information? Could
it move a rule toward closure in a way that reflects target information or result chasing?

## Tasks

1. **Classify each row.** Say whether it is a rule, a parameter, a binding, or implementation/controls. Give its
   direction for closure and its source. Check that its basis is target-free.
2. **Specific attention: A40.**
   * It changes how the post-marker seal commit is made: no signing, and a fixed identity. Could that change any
     outcome of a correct run, or only remove a host-dependent failure?
   * Is the pre-marker refusal outcome-neutral?
3. **New exposures.** Read the execution and exposure ledgers from `77991be1` onwards. That window includes the
   coordinator's pre-freeze dry runs (parts 2 and 3; FE-11), R4 follow-up 2's runs, the verifier author's follow-up
   runs (3, 4 and 5) and the coordinator's dev runs. Did anyone see a 305–309 value?
4. **Liabilities.** Check the two liability items `code/make_freeze_params.py` adds: the R4 follow-up-2 item and the
   A40 finding. Also check the `host_git` and `grant_validation` texts.

## Firewall

The same as your earlier briefs:
* Allowed: FNS, RNS, the overnight incident files, git metadata.
* Never reproduce a 305–309 value.
* Forbidden:
  * THEOREM_TCT lines 12 and 39;
  * any cell-307 or cell-308 campaign file beyond git metadata, masked `code/code_skeleton.py` output, or AST output;
  * any evaluation for cells 305–309;
  * any in-band kernel run;
  * git writes;
  * modifying anything except your output file.
* Ledger your reads and runs to a scratch file, and name it in your output.

## Output

`reviews/REVIEW_DELTA4_INCIDENT_P309.md`.

Line 2 is exactly one of:
* `DELTA4_INDEPENDENCE_ACCEPTED`;
* `DELTA4_INDEPENDENCE_REJECTED`. The campaign then STOPs before the freeze.

It must also contain a section headed exactly `## Conditions`, which the freeze parameters carry verbatim.
