# K5 tail overnight research campaign — cells 306–309 (prospective, target-quarantined)

**Status: RESEARCH ONLY. No target evaluation, no adoption, no coverage change, no freeze activation.**

| item | value |
|---|---|
| base | `8b9fc0bb` (tip of `p5y-k5-tail-c11rd-d1d2-extension`, 2026-09-28 02:13 +0900) |
| branch | `p5y-k5-tail-overnight-306-309` (local only, not pushed) |
| worktree | `/Users/suzhe/ReBaseGuard-k5ov` |
| started | 2026-09-27T17:31Z |
| authority | user instruction, 2026-09-28 overnight session ("Overnight K5 Cells 306–309 Scientific Advancement Campaign") |

## Starting state (verified from the repository, not from the prompt)

| check | value |
|---|---|
| r5 | `p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json`, blob `f978eeb6`, `union_open_ranges [[306, 309]]`, `union_open_count 4` |
| r6 | none, on any ref (`git log --all --name-only`: 0 hits) |
| 306 | OPEN / NOT ADOPTED (C12-R2 `CELL306_NOT_ADOPTED` 9c2cbf21, `ADJUDICATION_ACCEPTED` c5324a78) |
| 307, 308, 309 | OPEN (309 REFUTED WITHIN SCOPE for the uniform-A0 atom-constant family, C4 Condition 1) |
| K1, K2/K3, K4 | CLOSED: tags `p5y-k1-successor-closed` → 7d5cf02b, `p5y-k2-k3-closed` → df703837, `p5y-k4-successor-closed` → e88a2885 |
| K5 | OPEN (PARTIAL); P5Y NOT_YET_CLOSED |
| closeout | three rejected freezes (08e9acd1, dfcd8f79, 9f702acb) and their reviews: **not touched** |
| exactly-once refs | `refs/c12r2/cell306-target-consumed` → dec92e09, `refs/c11rd/r1-execution-consumed` → 4b716d43: **not touched** |

## Quarantine

`config/TARGET_QUARANTINE.json` was written and committed **before any scientific work**.

* **Target:** CUSUM, m = 5, cells 306, 307, 308 and 309.
* **Tail-adjacent:** cell 305 is also quarantined for new-route quantities. This is self-imposed and stricter than the
  prompt, following `ROUTE_AUDIT_R1.md` §8: calibration on a real cell is load-bearing because per-cell ratios
  transfer as estimates.
* **Allowed:** reading committed values.
* **Forbidden:** computing any new quantity on these cells.
* **Enforcement** (`code/ov_quarantine.py`):
  * runtime `guard_cell`;
  * import guard against historical consumers and drivers;
  * static scan with a planted negative control;
  * ledger `ledger/ZERO_TARGET_LEDGER.jsonl`.

## Kill gates (from the instruction, applied per route)

| gate | requirement |
|---|---|
| G1 | prospective motivation, independent of the target sign |
| G2 | the derivation is internally sound |
| G3 | scope is explicit |
| G4 | reproducible implementation |
| G5 | passes non-target validation |
| G6 | independent check |
| G7 | temporal integrity |
| G8 | no target leakage |
| G9 | could be frozen prospectively |
| G10 | a real improvement, not cosmetic |

A route that fails G1, G7 or G8 cannot be rescued tonight.

Route states: THEORY_ONLY, IMPLEMENTED, VALIDATED_NON_TARGET, FREEZE_READY, BLOCKED, REFUTED, DEFERRED,
INVALID_RESULT_CHASING. **CLOSED is never used for a route.**

## Layout

| path | content |
|---|---|
| `graph/` | K5 tail dependency graph (md + json) |
| `streams/A_306/` | I1/I2 disagreement audit, common-theorem route |
| `streams/B_307/` | higher-order looseness inventory, real order-3 theory |
| `streams/C_308/` | operator-level route, exclusion question |
| `streams/D_309/` | sup-norm, cover, residual-specific routes |
| `streams/E_assembly/` | assembly tightening, general operator-tuple strategy |
| `streams/F_indep/` | independent implementation, validation infrastructure |
| `registry/K5_OVERNIGHT_ROUTE_REGISTRY.md` | route registry |
| `validation/` | non-target validation report |
| `reviews/` | independent reviews, preserved verbatim |
| `OVERNIGHT_FINAL_REPORT.md` | morning handover |
