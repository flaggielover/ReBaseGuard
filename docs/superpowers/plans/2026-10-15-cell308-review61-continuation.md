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
- [ ] Add `.github/workflows/cell308-dev-review.yml` and `.github/scripts/cell308_dev_review.py` to run only the isolated development suite on a pinned input revision. The runner records complete per-mutant output, counts, return codes and source/test/harness hashes.
- [ ] Establish the unmodified suite passes before mutations. Classify assertion failures, execution errors, survivors and invalid anchors separately; keep an error-classification case for explicit reviewer adjudication.
- [ ] Preserve reviewer reports verbatim with disclosures, reviewed SHA, scope and environment limitations; do not impersonate the unavailable Claude reviewer.

## Task 2: bounded repairs from the independent review

- [ ] Reproduce each actionable finding before repair. Known code lead: `busy_processes` must not exempt a child merely because its parent PID was once owned; validate the parent identity in the relevant snapshot.
- [ ] Validate finite ordered clock observations, recognised process states and valid boot identifiers; malformed observations must remain UNKNOWN/AMBIGUOUS rather than prove ALIVE/DEAD/CLEAN.
- [ ] Add isolated regression tests and semantic mutants for each verified repair in `streams/CLOUD_R1_LINUX_DEV/tests/`.
- [ ] Correct document claims with an additive amendment/owner-brief revision and update active development documentation accurately (75 baseline tests, not 74). Carry genuinely undecided semantics as conditions.
- [ ] Run the baseline and mutation suite on final input hashes. Preserve complete failure evidence; no automatic kill credit for unrelated process errors.

## Task 3: independent follow-up and delivery

- [ ] Obtain independent follow-up review of repaired code, relevant document deltas and final evidence.
- [ ] Verify historical source/evidence preservation and the changed-path allowlist.
- [ ] Record integrity-ledger bindings and additive review/validation artifacts behind the scoped scan gate.
- [ ] Commit and push only the continuation branch; prepare a concrete next-step packet without claiming acceptance of proposed governance.

## Validation commands

Baseline: `python3 -B -W error::ResourceWarning -m unittest discover -s tests -v` from the development stream in the pinned Linux snapshot.

Independent mutation evidence: `python3 .github/scripts/cell308_dev_review.py --repo <snapshot> --output <scratch-evidence>` from the control checkout. No output is written to historical `results/` records.

Scoped quarantine scan: import `c308_quarantine` and call `scan` on a temporary copy containing only the explicit changed target-free files. Gate on `verdict == PASS`; keep both planted controls enabled and redact literal hit values from display.
