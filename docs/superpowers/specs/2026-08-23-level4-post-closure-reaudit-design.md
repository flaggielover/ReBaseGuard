# Level-4 post-closure re-audit design

## Purpose

Create an isolated, current-state Level-4 re-audit without modifying Stage F
or performing new science. The re-audit maps later proof-track closures onto
the 18 requirements reconstructed by Stage F, preserves every historical
decision, and derives the current verdict mechanically.

## Architecture

The namespace is `level4/re_audit_post_closure/`. Its canonical input is
`requirements.json`, containing exactly the 18 Stage-F requirements, their
Stage-F statuses, classifications, post-Stage-F evidence, and any scoped
status update. Counts and the current verdict are not authored separately.

`src/generate_audit.py` validates the canonical table, resolves each current
status, derives all counts and blocker lists, applies the frozen fallback
taxonomy, and renders the decision JSON and mirrored Markdown artifacts.
`historical_artifact_hashes.json` independently protects the complete tracked
Stage-F namespace, the two historical Stage-F reports, and the critical
protocol and decision artifacts used by the mapping.

## Decision mechanics

The generator normalizes current statuses to `PASS`, `PARTIAL`, `FAIL`, or
`OPEN`. A later status overrides the Stage-F normalized status only when the
row explicitly identifies a scoped closure artifact. Mandatory `FAIL` and
`OPEN` rows form `mandatory_unmet`; mandatory `PARTIAL` rows are reported
separately. Integrity loss or a contradicted central claim would yield
`LEVEL-4-FAILED`. Any mandatory non-pass yields `LEVEL-4-PARTIAL`. Otherwise,
all mandatory requirements pass and the result is `LEVEL-4-CLOSED`; the
fallback architecture does not independently authorize
`LEVEL-4-CLOSED-WITH-LIMITATIONS`.

The approved expected result is 12 pass, 3 partial/negative, 2 fail, and 1
open. The three mandatory fail/open blockers are D4, semi-real external
validation, and novelty verification. The generator must fail rather than
coerce the data if the table does not derive those values.

## Historical boundary

Stage F remains a historical `LEVEL-4-PARTIAL` audit. Its files and reports
are read-only inputs protected by exact SHA-256 values. Stage-D D2.3, Track
1A, historical Track 3, Stage E 0/3, D2.5, and the t3 ambiguity remain
unchanged. Track 1B, Track 2, and Track 3A/3B update only the corresponding
requirement rows.

## Verification

The isolated pytest suite has exactly 18 parameterized adversarial cases,
R1--R18. `scripts/verify_level_4.sh` runs it after the unchanged Stage-F
suite. The re-audit reproducer checks generated artifacts byte-for-byte,
executes the adversarial evaluator and isolated suite, runs the two full
repository verifiers, confirms protected hashes, and proves that it introduced
no additional tracked-file changes.

The final unique check accounting is 713 authoritative repository tests, 205
historical closure tests, and 29 Track-3A/3B tests: 947 total.

## Commit policy

All implementation and generated artifacts are committed together only after
the isolated suite, 18/18 adversarial checks, full verification, byte-stable
reproduction, and protected-hash checks pass. Push is fast-forward only.
