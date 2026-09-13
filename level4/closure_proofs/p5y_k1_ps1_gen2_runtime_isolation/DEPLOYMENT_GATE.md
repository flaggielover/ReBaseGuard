# Lane A deployment gate

```
LANE_A_REPAIR                        = PASS_SYNTHETIC_NOT_DEPLOYED
LANE_A_DEPLOYMENT_ALLOWED_ONLY_AFTER = CURRENT_LIVE_DRAIN_SETTLED
```

When this gate was created, the live PS1 generation-2 unit
`rbg-p5y-k1-ps1-recov-aws-20260912T154658Z-2011fded` was active under the operator compatibility DRAIN
(written 2026-09-12T16:04:18Z at the gen1 `work/DRAIN` path the live launcher polls). The live run,
its runtime contract, its DRAIN marker and its evidence were not touched.

## How the gate is enforced

1. **Technical.** `config/OPERATIONAL_CONTRACT_HASH` does not exist. The generated `ops/opscommon.py`
   refuses to load the PRODUCTION contract (`UNFROZEN`); see `tests/test_deployment_gate.py`.
2. **Technical.** The proposed contract's `ops_root` is not deployed on AWS. The live unit runs the
   unrepaired `p5y_k1_ps1_portable_recovery` ops.
3. **Mechanical check.** `code/check_deployment_gate.py` is read-only and exits non-zero unless every
   gate of the requested phase passes. It must never be run against a live campaign.
4. **Record.** `config/DEPLOYMENT_GATE.json` holds the ordered steps. `config/QUALIFIED_SOURCE_HASHES.json`
   holds the 14 source hashes that the final synthetic acceptance actually ran.

## Ordered steps before any future PS1 resume

| # | step | verified by |
|---|---|---|
| 1 | Let the live unit exit through the graceful drain. **Never `prodctl stop` it**: its supervisor reconciliation scans a directory the live launcher never writes (AUDIT M3). | unit inactive |
| 2 | **Verify 16 expected cells sealed** (one in-flight cell per worker when the drain began). Any other count goes to adjudication before freeze. **Reconcile ledger/reservations**: `open_reservations` = {}, no OPEN run. **Verify `torn_attempts` = {}.** **Verify the lock is released** (campaign flock free, frozen ledger lock absent). Continuity chain valid; repair sources equal the qualified hashes. | `check_deployment_gate.py --phase settled --expected-sealed 16 --unit-glob 'rbg-p5y-k1-ps1-*'` → `FREEZE_ALLOWED` |
| 3 | **Freeze the Lane A repair**: commit `OPERATIONAL_CONTRACT_HASH` and an `OPS_SOURCE_MANIFEST` over `ops/` + `driver/`. | commit |
| 4 | **Bind exact repair/runtime-contract hashes**: repair commit, contract hash, ops manifest hash, qualified source hashes. If any ops or driver source differs from `QUALIFIED_SOURCE_HASHES.json`, the step-6 acceptance is mandatory, not merely confirmatory. | record |
| 5 | **Deploy** the frozen commit to the AWS ops worktree. No change to the production tree, ledger or evidence. | `prodctl verify` / `prodctl paths` |
| 6 | **Rerun focused acceptance** on the frozen sources, under a synthetic contract and never the live runtime dir. | `tests/isolation_acceptance.py all negative` |
| 7 | **Clear the stale DRAIN only after verification** (steps 2–6): `prodctl clear-drain` archives the generation flag with a continuity record. The gen1 compatibility flag is legacy, ignored by the repaired launcher, reported at pre-start, and never deleted. | continuity `DRAIN_FLAG_ARCHIVED` |
| 8 | Resume check. | `check_deployment_gate.py --phase pre-resume --acceptance <step-6 ACCEPTANCE.json>` → `RESUME_ALLOWED` |
| 9 | **Then resume production**: `prodctl start --role AWS`. | — |

## Forbidden until the gate passes

Deploying the repair; updating the live runtime contract; clearing the live DRAIN marker;
restarting or stopping the live campaign; modifying live evidence.
