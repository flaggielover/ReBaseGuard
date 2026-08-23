# Post-closure integrity audit

## Repository state at audit start

- Branch: `main`
- HEAD: `c8743cc9c363b7a8a3be6dc51947d9d74f76e2ca`
- `origin/main`: `c8743cc9c363b7a8a3be6dc51947d9d74f76e2ca` after `git fetch origin --prune`
- Ahead/behind: `0 / 0`
- Worktree before implementation: clean
- No frozen post-Stage-F global taxonomy was found; the Stage-F fallback is reused.

The first full Level 1–3 invocation was interrupted by its execution session
during Lean compilation without a verifier failure. The identical command was
rerun from a clean state and completed successfully; the interruption is not
silently treated as a pass.

## Actual verification results

| Command / package | Result |
|---|---|
| `bash scripts/verify_level_1_3.sh` | PASS; zero skips; final Lean source elaborated; Arb replay byte-identical; 90 regression tests passed |
| `bash scripts/verify_level_4.sh` | PASS; 713 authoritative tests after re-audit integration |
| Track 1B reproducer | PASS: MGT1-TRACK1B-CLOSED reproduced |
| Track 2 reproducer | PASS: SR-DERIVATIVE-CLOSED reproduced; rigorous SR certificate OPEN |
| Track 3A/3B reproducer | PASS: LOCATION-FAMILY-TRACK3AB-CLOSED reproduced; historical Track 3 partial |
| Post-closure reproducer | PASS; byte-stable `True` |

## Protected history

- Exact SHA-256 files checked: **38**
- Missing: **0**
- Mismatched: **0**
- Status: **INTACT**

The manifest covers every tracked file in `level4/stage_f/`, both historical
Stage-F final reports, the frozen Stage C/C.1/D/E protocols and precommitments,
the critical historical decisions, and the three later closure protocols and
decisions. Stage F is byte-for-byte unchanged.

## Check accounting

- Authoritative repository tests: **713**
- Historical closure tests: **205**
- Track-3A/3B focused tests: **29**
- Current distinct total: **947 / 947**

No Monte Carlo campaign, semi-real dataset, D4 run, SR certificate campaign,
phase diagram, or new theorem was executed by this re-audit.
