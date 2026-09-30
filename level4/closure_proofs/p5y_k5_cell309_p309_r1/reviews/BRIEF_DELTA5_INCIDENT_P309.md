# Brief: incident-independence review of the FIFTH rev. 2c delta (conditions C2, D8; delta-3 G8, G9; delta-4 H7, H8)

This brief is committed before it is issued (condition C5).

**Recipient:** the independent incident-independence reviewer, author of:
* `reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`;
* `reviews/REVIEW_U2_CHECK_P309.md`;
* `reviews/REVIEW_DELTA_INCIDENT_P309.md`;
* `reviews/REVIEW_DELTA2_INCIDENT_P309.md`;
* `reviews/REVIEW_DELTA3_INCIDENT_P309.md`;
* `reviews/REVIEW_DELTA4_INCIDENT_P309.md`.

## Question

R4's follow-up 3 blocked the freeze on one finding: `reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_3_P309.md`, F4, condition
R4F3-C1. It found `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES`.

The resolution is the commit that adds this brief. It is recorded in:
* the append-only section "Fifth delta" (A43–A47) of `governance/P309_REV2C_AMENDMENTS.md`;
* addendum 2 of `governance/D5_SITE_BACKSTOP_REPORT_P309.md`.

Your H7 and H8 make any further rule, parameter or binding change a new delta under C2. The rows marked as such are:
* **A43.** `seal-only` runs `check_host_git` before its first git call.
* **A44.** `execute` repeats `check_host_git` in two places:
  * after the historical control, just before its first git write. A refusal there is before the marker.
  * after the marker, just before the evidence persist. A refusal there sends the evidence to the emergency file, for
    `seal-only`.
* **A45.** The guard's git ignores the host's system and global configuration.

A46 (controls: QC11 H01–H07 and V11, QC12 T10, D5 X01–X11) and A47 (five unused allowlist entries removed) are marked as
controls and implementation.

For every row A43–A47: is the change **temporally and parametrically independent** of the exposed information? Could
it move a rule toward closure in a way that reflects target information or result chasing?

## Tasks

1. **Classify each row.** Say whether it is a rule, a parameter, a binding, or implementation/controls. Give its
   direction for closure and its source. Check that its basis is target-free.
2. **Specific attention: A44.**
   * After the marker, a refusal changes the channel of the evidence (emergency file instead of the pending ref) and
     the exit code (4 instead of 0 or 5). Can that change any mechanical outcome or its record? Or does it only delay
     the seal until the host is clean?
   * Is the pre-marker re-check outcome-neutral? Note that it can hide a CONTROL_FAILED seal behind a HOST_GIT refusal.
3. **Specific attention: A45.** Does leaving the verifier variant unchanged fit its role separation? (Inside `execute`
   it inherits the driver's hermetic `ENV` in the Stage-1 jobs.)
4. **New exposures.** Read the execution and exposure ledgers from `bfa18252` onwards. That window includes:
   * the coordinator's pre-freeze dry run part 4 (FE-11);
   * R4 follow-up 3's runs;
   * your delta-4 review;
   * the coordinator's development runs of this delta, in a scratch clone of the repository, whose ledger lines are
     copied into the ledger in this commit.

   Did anyone see a 305–309 value?
5. **Liabilities.** Check:
   * the R4 follow-up-3 liability item that `code/make_freeze_params.py` adds;
   * the `host_git` texts of the grant rules and of `code/make_proposed_authorization.py`.

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

`reviews/REVIEW_DELTA5_INCIDENT_P309.md`.

Line 2 is exactly one of:
* `DELTA5_INDEPENDENCE_ACCEPTED`;
* `DELTA5_INDEPENDENCE_REJECTED`. The campaign then STOPs before the freeze.

It must also contain a section headed exactly `## Conditions`, which the freeze parameters carry verbatim.
