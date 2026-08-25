# Final Level-4 closure re-audit design

## Objective

Create a terminal, audit-only global Level-4 re-audit after the authorized
L4R-06 and L4R-12 same-requirement closures. The audit must mechanically derive
the current verdict from the original protected 18-row ledger and all authorized
later decision artifacts. It must not run new science or modify any historical
status artifact.

## Authority and immutability

The authoritative requirement source remains
`level4/final_global_reaudit/requirements.json`, whose IDs, wording,
classifications, Stage-F fields, and previous-final-audit fields are protected.
The historical Stage-F, post-closure, and Final Global Re-audit verdicts remain
`LEVEL-4-PARTIAL` as historical facts.

The new audit reads but never edits historical Stage C, Stage D, Stage E,
Stage F, the post-closure re-audit, the previous Final Global Re-audit, or any
closure campaign. A protected-history manifest pins their trees and load-bearing
decision files at the starting commit.

## Selected architecture

Create `level4/final_level4_closure/` as an isolated generated overlay with:

- a mapping registry that connects each authorized closure campaign to exactly
  one original requirement;
- a generator-owned canonical `requirements.json` with exactly 18 rows and the
  original 16 mandatory classifications;
- an evidence audit that validates every mapped decision and preserves all
  unfavorable and negative findings;
- a pure decision function deriving counts, blockers, and the global verdict;
- Markdown reports generated only from the canonical JSON and final decision;
- exact A1-A32 adversarial checks, focused tests, deterministic verification
  records, and an offline reproducer.

The two newly added mappings are:

- L4R-06: `L4R06-POLICY-CLOSED`, same-requirement mapping true, original row
  `PARTIAL -> PASS`, while Stage C remains `STAGE-C-PARTIAL` and C6 remains
  failed;
- L4R-12: `L4R12-CLOSED-NEGATIVE-RESULT`, same-requirement mapping true,
  original row `PARTIAL/NEGATIVE -> PASS`, while the scientific result remains
  `MATHEMATICAL, NOT OPERATIONAL`.

L4R-13 remains a nonmandatory `STRONG_EXTENSION` with current status `PARTIAL`.

## Canonical data flow

1. Validate the original source hash, row order, wording, classifications, and
   historical statuses.
2. Validate protected historical trees and files.
3. Validate all eight current status-transition campaigns and their evidence
   paths, including L4R-06 and L4R-12.
4. Generate the canonical rows with fields for original/historical/current
   status, evidence, campaign, reason, limitations, mandatory flag, and current
   blocking flag.
5. Count statuses directly from the generated rows.
6. Apply the frozen rule `ALL_MANDATORY_ROWS_PASS`; only `PASS` satisfies a
   mandatory row. Integrity and engineering gates must also pass.
7. Emit only a taxonomy-authorized verdict. No
   `LEVEL-4-CLOSED-WITH-LIMITATIONS` category is available.
8. Generate all reports and synthesis text from the canonical decision.

The expected arithmetic is treated only as a test oracle, never as a hard-coded
decision: 17 PASS, one nonmandatory PARTIAL, and 16/16 mandatory PASS would
derive `LEVEL-4-CLOSED` if every integrity and verification gate also passes.

## Claim firewall and open work

Closure, if mechanically reached, means the internally frozen Level-4 program's
mandatory ledger is satisfied. It does not erase failed experiments, make the
method universal, certify production deployment, establish absolute novelty,
or certify Gamma_SR with Arb.

The optional `SR-ARB-CERTIFICATE` remains `OPEN`. Gamma_SR greater than two
remains confirmatory numerical evidence; the SR derivative theorem remains
closed. D4 remains a local deterministic stability map. D2.5 remains a valid
negative operational-transition result. External safety remains
regime-dependent, and novelty remains the scoped N2 partial-overlap result.

## Adversarial, testing, and reproduction flow

Implement exactly A1-A32 from the terminal brief. The first run is preserved
before final reproduction and verification records exist. Tests cover the
18/16 row counts, both new mappings, nonblocking L4R-13, historical
immutability, pure closure-rule counterfactuals, evidence paths, claim firewall,
report mirroring, and byte stability.

The offline reproducer verifies history and all closure artifacts, regenerates
the canonical ledger twice, runs focused tests and A1-A32, invokes
`scripts/verify_level_1_3.sh` and `scripts/verify_level_4.sh`, checks final
records and reports byte-for-byte, and confirms historical verdicts again. It
does not invoke any scientific simulator or network operation.

## Failure behavior and Git

Any source drift, missing evidence, classification change, invalid mapping,
non-PASS mandatory row, failed adversarial check, failed verifier, or unstable
artifact prevents `LEVEL-4-CLOSED`. No scientific criterion is weakened to
repair an engineering failure.

After all gates pass, create one final closure commit, verify a clean worktree,
verify that `origin/main` is an ancestor, fast-forward push without force, and
confirm HEAD/origin equality and 0/0 divergence. Do not create a release tag.
