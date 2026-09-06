# SR <-> CUSUM Aux4 integration plan (Phase 14)

No evidence is merged now. This records HOW the SR ledger will later join the
completed CUSUM Aux4 ledger, so the join is designed rather than improvised.

## 1. Producer separation

The two detectors have DIFFERENT execution-derived TCBs and must keep them.

| | CUSUM Aux4 | SR qualification |
|---|---|---|
| namespace | `p5y_k1_cusum_aux4_fullcover` | `p5y_k1_sr_qualification` |
| producer | `code/qualify4.py` | `code/sr_pilot.py` |
| science modules | `cusum_layer1/2`, `_kernel_polynomials` | `sr_sources`, `sr_operators`, `sr_propagate` |
| panel primitives | recentred Hermite on the CUSUM state square | softplus / Taylor models on two charts |
| TCB | Aux4 manifest V2 | derived at run time by `sr_provenance.tcb_from_execution` |

The SR TCB is NOT a copy of the Aux4 manifest. Copying it would bind SR records
to modules SR never executes and leave the modules it does execute unbound.

## 2. Shared frozen K1 checkpoint

Both bind the SAME frozen artifacts, and this is the join key:

```text
config/checkpoint.json  1c2a6825f19e19de6fb588647ca3fc4618068087ef0976292ca7bbeca701f13f
cells.json / cover_witnesses.json / cost_model.json / record_schema.json
ERROR_ALGEBRA.md        4f32df0273d05b1b4e0136e2a901adec9979e158b5decd8c9bf3cce0e35b9ffa
```

`spec.verify_frozen_spec()` must return `spec.FROZEN_HASHES` in BOTH producers at
adjudication time. A mismatch invalidates the join, not just one side.

## 3. Detector-specific ledgers, then one aggregate

```text
   CUSUM ledger : 326 cells x 28 + 1 far-field = 9,129 obligations
   SR    ledger : 316 cells x 28 + 1 far-field = 8,849 obligations
                                                 ------
   aggregate K1 :                                17,978   == spec.TOTAL_UNITS
```

The aggregate is a UNION over disjoint work-ID sets, never a re-computation.
`universe.work_ids()` is the ordering authority for both. The aggregator must
assert disjointness and exact totality (9,129 + 8,849 == 17,978) before emitting.

## 4. Cost aggregation

```text
   K1_total_cpu_hours = CUSUM_measured + SR_measured
```

Both sides measured, never modeled, at adjudication. The 1126 CPU-hour cap is
adjudicated ONCE, on the sum, and only after both sides are complete. Neither
side may claim the cap alone, and the historical SR extrapolation is excluded
(`config/excluded_routes.json#historical_sr_cost_extrapolation`).

## 5. Final K1 adjudication sequence

```text
1. CUSUM 326-cell full-cover campaign completes; Aux4 audit PASS
2. CPU idle verified; SR pilots run (Phase 12), then SR full cover
3. SR audit PASS under its own execution-derived TCB
4. frozen-spec hash equality checked across both producers
5. ledgers unioned; disjointness + totality (17,978) asserted
6. far-field: CUSUM PASS and SR PASS both inherited, not recomputed
7. cost summed and adjudicated against the 1126 cap
8. K1 verdict issued
```

Steps 2-8 are all BLOCKED until step 1 completes naturally. Nothing in this lane
advances past step 2's precondition.

## 6. What must NOT happen at merge time

* no merge of `p5y-k1-sr-parallel` into `p5y-gate1-micropilots` while the CUSUM
  campaign is running -- the branch checkout would move the running worktree;
* no SR file written inside `p5y_k1_cusum_aux4_fullcover`, and no SR file written
  anywhere in the authoritative worktree while it runs: `audit4.audit_governance`
  fails closed on ANY dirty path outside the Aux4 namespace, so a stray SR file
  would invalidate the CUSUM certification;
* no re-run of CUSUM cells under SR code, and no composition of a CUSUM cell
  record into the SR ledger.
