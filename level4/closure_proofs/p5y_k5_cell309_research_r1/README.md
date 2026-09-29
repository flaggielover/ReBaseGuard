# K5 cell-309 research campaign r1 (prospective, target-quarantined, research only)

**Status: RESEARCH ONLY.** No target evaluation, no adoption, no coverage change, no exactly-once step, no grant,
no marker, no push without explicit authorization.

| item | value |
|---|---|
| base | `b73b9449` (tip of `p5y-k5-cell307-rlr-r1`, the latest committed K5 state on origin) |
| branch | `claude/rebaseguard-k5-cell-309-w0jv8m` (isolated cloud clone; **not pushed** unless the user authorizes) |
| authority | user instruction 2026-09-29, "PARALLEL RESEARCH-ONLY campaign for ReBaseGuard K5 cell 309" |
| started | 2026-09-29T12:57Z |
| namespace | `level4/closure_proofs/p5y_k5_cell309_research_r1/` (every commit of this campaign stays inside it) |

## Isolation (from the instruction; verified, not assumed)

* Cell 308 is under its one-and-only authorized exactly-once execution on another machine. This campaign runs in a
  fresh cloud clone. It never contacts that machine and never reads uncommitted or transient state from it. It never
  creates, moves or deletes any `refs/p5y-*` or `refs/c1*` ref. No branch or ref named for a cell-308 formal campaign
  exists on origin at the start (`git ls-remote`, 2026-09-29T12:50Z).
* r5 (`p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json`, blob `f978eeb6`) is read-only. No r6.
* No K5/P5Y status change. Cell 309 is not adopted.

## Target quarantine

`config/TARGET_QUARANTINE_309.json`, committed before any scientific work.
* **Zero** new Γ(5, 309) evaluations, and none for 305–308.
* No target-equivalent proxies, no hidden reconstruction of the verdict, and no tuning against 309.
* No new quantity at any drift in [6/5, 13/5] or its mirror.
* Enforcement: `code/q309_guard.py`, which provides a runtime guard, an import guard and a static scan with a planted
  control. It feeds two ledgers:
  * `ledger/EXPOSURE_LEDGER.jsonl` records every historical read that exposed a 305–309 number;
  * `ledger/ZERO_TARGET_LEDGER.jsonl` records executions.

## Phases

| phase | output |
|---|---|
| 0 | `dossier/`: authoritative reconstruction of cell 309 and the route matrix |
| 1 | `theory/`: target-independent theorems, each with assumptions, proof, the consumer term it replaces, dominance, degenerate cases and adversarial tests |
| 2 | `impl/`, `verify/`, `tests/`: certifiers on decoys, an independent verifier built from the spec, mutants and controls |
| 3 | `registry/`: route comparison based only on prospective evidence |
| 4 | `protocol_prep/`: prepared only if a route is independently reviewed as FREEZE_READY. Never executed |

Route classes: REJECTED, BLOCKED, INSUFFICIENT_EVIDENCE, RESEARCHABLE, PROMISING, FREEZE_READY.

## Push authorizations (recorded per review R1 G5)

| when (UTC) | authorization (user, verbatim scope) | use |
|---|---|---|
| 2026-09-29 ~15:3x | "I explicitly authorize a checkpoint push of the cell-309 research branch only … solely to preserve the current research-only work against another cloud-container restart" | one push, which created `refs/heads/claude/rebaseguard-k5-cell-309-w0jv8m` at 5e96041f (it did not exist on origin before) |
| 2026-09-29 later | "I grant standing permission for checkpoint pushes of the cell-309 research branch only … for preservation/recovery only", with nine required checks | `code/checkpoint_push.py` enforces the nine checks plus the static quarantine scan. Every push is ledgered in `ledger/CHECKPOINT_PUSHES.jsonl` |

Neither authorization permits any target evaluation, grant, marker, r5/r6 change, adoption, K5/P5Y change, or a push of
any other ref.
