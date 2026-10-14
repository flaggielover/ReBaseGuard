# Cell-308 review 61 continuation implementation plan

**Goal:** Independently validate revision 3, preserve the takeover review, repair demonstrated development defects, and deliver independently reviewed target-free work.

**Architecture:** Review immutable `d423c7aacc4d1cc15f3c7d77aecb5257a0175392` in an isolated worktree. Use a GitHub Linux runner for synthetic validation because both existing SSH workers are unreachable. Keep original evidence and amendment revisions unchanged; bind new evidence to exact inputs.

**Tech stack:** Python standard library, unittest, Git, GitHub Actions Ubuntu runner.

**Spec:** `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R3.md`, brief 61, and the owner's 2026-10-14 authorization. Owner's 2026-10-15 instruction authorizes autonomous continuation of this scope without routine implementation choices.

## Global constraints

- No target, drift, certificate, decoy, science evaluator, formal qualification, freeze, grant, adoption, or protected-ref operation.
- Leave Cell 309 and both historical Cell-308 branches untouched.
- Read only brief-61 allowlisted sources; never scan the entire namespace through the quarantine CLI.
- Preserve reviewed source inputs until independent reviewers finish. Preserve historical documents and evidence; use additive revisions.
- A synthetic Linux test run is not host qualification or proof of VM lifetime/durability.
- Scan the exact changed, target-free artifacts with planted controls before commits and pushes.

## Task 1: independent review and Linux evidence

- [x] Fetch and verify GitHub baseline; create isolated managed worktree.
- [x] Dispatch fresh independent code, amendment, and provenance reviewers against the immutable baseline.
- [x] Add `.github/workflows/cell308-dev-review.yml` and `.github/scripts/cell308_dev_review.py` to run only the isolated development suite on a pinned input revision. The runner records complete per-mutant output, counts, return codes and source/test/harness hashes.
- [x] Establish the unmodified suite passes before mutations. Classify assertion failures, execution errors, survivors and invalid anchors separately; keep an error-classification case for explicit reviewer adjudication.
- [x] Preserve reviewer reports verbatim with disclosures, reviewed SHA, scope and environment limitations; do not impersonate the unavailable Claude reviewer.

## Task 2: bounded repairs from the independent review

- [x] Reproduce each actionable finding before repair. Known code lead: `busy_processes` must not exempt a child merely because its parent PID was once owned; validate the parent identity in the relevant snapshot.
- [x] Validate finite ordered clock observations, recognised process states and valid boot identifiers; malformed observations must remain UNKNOWN/AMBIGUOUS rather than prove ALIVE/DEAD/CLEAN.
- [x] Add isolated regression tests and semantic mutants for each verified repair in `streams/CLOUD_R1_LINUX_DEV/tests/`.
- [x] Correct document claims with an additive amendment/owner-brief revision and update active development documentation accurately (75 baseline tests, not 74). Carry genuinely undecided semantics as conditions.
- [x] Run the baseline and mutation suite on final input hashes. Preserve complete failure evidence; no automatic kill credit for unrelated process errors.

## Task 3: independent follow-up and delivery

- [x] Obtain independent follow-up review of repaired code, relevant document deltas and final evidence.
- [x] Verify historical source/evidence preservation and the changed-path allowlist.
- [x] Record integrity-ledger bindings and additive review/validation artifacts behind the scoped scan gate.
- [x] Commit and push only the continuation branch; prepare a concrete next-step packet without claiming acceptance of proposed governance.

## Task 4: trusted-boundary development prototype

The r4 A1/A2 integration conditions already require a caller boundary deriving root provenance from committed/current-host attestation and restricting favorable reader/checker/observer/decision seams. The later owner authorization permits this target-free development; no new policy choice is needed. This task follows the fresh revision-5 review and its concrete NSpid payload correction.

- [x] Preserve the revision-5 independent reports and exact-commit Linux 111-test/78-mutant record; reproduce and repair the newly demonstrated NSpid delimiter defect with a refusal test and F06 weakening mutant.
- [x] Add an observation-only `lx_verified.py` API accepting only an attestation reference and validated observation mode. Bind repository internally; use canonical current-machine verification and default live readers/observer. Derive root evidence only from a verified record with a strict boolean True.
- [x] Keep decisions empty and the unavailable campaign detector UNKNOWN. Import no science and expose no pin-point completion, campaign launch, caller-supplied readings, checker, observer, repository or root flags.
- [x] Label memory data RAW; withhold unresolved effective-limit/headroom quantities as operational allowances and return development-only / operational-ready False. Keep A5 and all20 policy decisions unmet.
- [x] Add synthetic committed-fixture provenance/refusal and public-seam tests; bind both new files in the full-suite input hashes and trigger exact-source Linux CI.
- [x] Preserve revision-6 independent code/document/evidence review and strict Linux baseline134 PASS /78 valid kills /M25 ERROR; keep the failed aggregate record.
- [x] Repair the demonstrated malformed-path exception boundary and explicitly refuse absent committed blobs before JSON parsing; add two wrapper refusal tests and F07 without relaxing classification.
- [x] Obtain fresh independent code and evidence review of revision 7, verify the final exact-input native run, preserve records and prepare a concrete handoff packet.

## Validation commands

Baseline: `python3 -B -W error::ResourceWarning -m unittest discover -s tests -v` from the development stream in the pinned Linux snapshot.

Current mutation evidence: `python3 -B tests/run_mutants.py <scratch-evidence.json>` from the immutable development snapshot. The separately preserved `.github/scripts/cell308_dev_review.py` supplied the original forensic replay only. No historical result record is overwritten.

Scoped quarantine scan: import `c308_quarantine` and call `scan` on a temporary copy containing only the explicit changed target-free files. Gate on `verdict == PASS`; keep both planted controls enabled and redact literal hit values from display.
