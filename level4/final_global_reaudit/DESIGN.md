# Final global Level-4 re-audit design

The user-supplied terminal-audit brief is the approved specification. This
namespace performs derivation only: it reads the protected 18-row ledger and
committed closure decisions, validates their evidence chains, and maps only
campaigns that explicitly closed the same original requirement.

## Architecture

1. `requirements.json` preserves the original IDs, descriptions,
   classifications, Stage-F statuses, and previous-re-audit statuses. It adds
   only authorized transition records and surviving limitations.
2. `protected_hashes.json` freezes all historical trees at audit start commit
   `ba9f49d202b8feb71fb4923929b506f8e9b88a40`.
3. `src/audit.py` validates the original-source fingerprints, evidence paths,
   campaign-to-requirement mapping, and later campaign decisions, then derives
   every row, count, blocker, and verdict.
4. `src/adversarial.py` implements the requested claim, history, taxonomy,
   mapping, integrity, offline-reproduction, and synthetic-blocker attacks.
5. `src/reproduction.py` rebuilds the audit-only artifacts twice and compares
   their bytes. It does not launch simulation, data acquisition, literature
   search, theorem development, or network access.
6. `src/finalize.py` combines the derived scientific decision with the final
   adversarial, reproduction, verification, and integrity gates, then renders
   the machine decision and human reports.

## Decision rule

The Stage-F fallback is preserved exactly: `LEVEL-4-CLOSED` requires every
mandatory row to be `PASS`. Mandatory `PARTIAL` and `NEGATIVE` rows are
non-PASS and therefore block closure. `LEVEL-4-CLOSED-WITH-LIMITATIONS` is not
independently authorized. A contradicted core or broken integrity yields
`LEVEL-4-FAILED`; otherwise any mandatory non-PASS row yields
`LEVEL-4-PARTIAL`.

## Scope and error handling

Any source-fingerprint mismatch, historical-tree change, missing evidence,
wrong campaign mapping, failed campaign gate, count mismatch, or stale
generated artifact is a hard failure. Historical reports are read-only. The
only repository-wide edit outside this namespace is additive verifier
integration plus two new current-report filenames.

## Test and reproduction design

Thirty-six focused tests cover source identity, evidence mapping, counts,
verdict logic, claim boundaries, report derivation, and synthetic failure
cases. Twenty-six adversarial checks include every attack required by the
brief. The preserved first run occurs before reproduction and full-verifier
records exist; the final run occurs only after both gates pass.

## Self-review

- No placeholder, TODO, or undecided threshold remains.
- The audit contains no new scientific computation or network dependency.
- The result is not selected in advance; it follows the frozen all-mandatory-
  PASS rule.
- The SR Arb OPEN item remains visible but is outside the original 18-row
  derivative-theorem requirement.
