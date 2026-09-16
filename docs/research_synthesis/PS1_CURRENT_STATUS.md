# Current scientific status: PS1 successor (updated 2026-09-13)

This additive status note updates the public narrative without changing any frozen historical record.

```text
PS1 / SR  = QUALIFIED_AND_AUTHORIZED_ON_AWS, PRODUCTION_STARTED, CURRENTLY_GRACEFUL_DRAINING, NOT_CLOSED
CUSUM     = AUX5_COMPOSITE_CLOSURE_CLOSED (326-cell composite 0-325: 128 carry-over + 198 successor, K4 attestation PASS)
K1        = NOT_CLOSED
```

## Superseded statement (preserved)

The 2026-09-12 version of this note said:
- "AWS genuine PS1 SR production is authorized to start, but **genuine production has not started**: cells = **0**"
- "Full 369-cell production is **NOT RUN**"
- "The production start command is recorded in the authorization result but is intentionally **not run** by this reconciliation."

**Those statements are superseded.** They were accurate when written, at authorization and before production began. They no longer describe the campaign.

## Historical record (unchanged)

P1, P2, P3, P6, P7, P8R, and P9R retain their recorded adjudications. In particular, P4 = PARTIAL, P5 = PARTIAL, P8 = FAIL, and P9 = PARTIAL remain historical verdicts. The original 316-cell SR lineage and its old cell-313 failure remain historical; P8R and P9R remain separate repair lineages. No successor below recolors those outcomes.

## Research progression and negative results

P5Y/K1 continued the P5X global-dynamics successor with certified computation optimization and an O9 SR architecture. The O9 executor progressed through T1 candidate construction, T2 per-patch certification, T3 whole-cell aggregation, T4 curvature, and T5 one-cell/regional closure. The old cell-313 region exposed a genuine whole-cell curvature obstruction. The curvature successor was **NOT_CLOSING**, oracle-tight operator norms were **INSUFFICIENT**, and the Aux3 third-derivative augmentation was a **FEASIBILITY_FAIL**. These governed negative results are preserved because they explain why the next successor was needed.

Those results motivated the predeclared additive PS1 partition successor. PS1 defines a 369-cell SR universe; it replaces only the old-313 region with four deterministic successor cells and does not rewrite the old 316-cell campaign. The successor region passed 28/28 obligations, as did the certified control cells.

## Current successor state

- **PS1 is the SR side of K1. It is qualified and authorized on AWS** (`PS1_PRODUCTION_AUTHORIZATION_CLOSED`, topology `A_AWS_ONLY`). Vultr is **not eligible** for result-bearing PS1 cells: a predeclared cross-host replay found 0/24 bit-identical patch records against AWS.
- **Production started.**
  - Execution generation 1 (run `20260912T041203Z-962132d3`) halted on `RETRY_LIMIT` after a host/systemd maintenance event, with 0 finalized cells and 92.32 CPU-h. That halt is preserved, not cleared.
  - Execution generation 2 has run on AWS since 2026-09-12T15:46:58Z.
- **Currently graceful draining.**
  - An operator DRAIN has been in force since 2026-09-12T16:04:18Z. No new cell is admitted; in-flight cells finish at their boundary.
  - On 2026-09-13 a read-only check found the unit still active and the DRAIN marker unchanged. This note deliberately reports no finalized-cell counts and no results.
- Campaign cost basis: **4,413–5,694 CPU-h** (5,694 in the per-cell-durable production shape) against the frozen **6,600 CPU-h** global cap.
- A runtime-path defect in the deployed generation-2 operations has a synthetically verified repair that is **not deployed**. Deployment is gated on the current drain settling (`level4/closure_proofs/p5y_k1_ps1_gen2_runtime_isolation/DEPLOYMENT_GATE.md`).
- **CUSUM, the other side of K1, is CLOSED as a governed composite** (updated 2026-09-16). The Aux5 composite covers the full 326-cell universe 0-325 as a disjoint union: cells 0-127 are carried over from the predecessor campaign, which remains historically `HALTED` after a host-drift stop and whose cells were **not** recomputed, and cells 128-325 come from the new-glibc successor campaign, `COMPLETE` with 198/198 sealed, 0 failed and 0 torn. Carry-over was gated on the Q6 bit-identity requalification and an independent countersignature; the composite audit is COMPLETE and the K4 composite attestation covers 326 cells. The earlier statement that CUSUM `REQUIRES_FULL_326_RERUN` is **superseded**: it described the Aux4 producer state before the Aux5 campaign and its governed carry-over. See `level4/closure_proofs/p5y_k1_cusum_aux5_composite_closure/`.
- K1 = NOT CLOSED, P5Y = NOT CLOSED, LEVEL4_GLOBAL_CLOSURE = NO. No K1 closure is claimed: the CUSUM side is closed, the PS1/SR side is not.

Authoritative records:

- [PS1 qualification result](../../level4/closure_proofs/p5y_k1_ps1_production_qualification/RESULT.md)
- [PS1 partition result](../../level4/closure_proofs/p5y_k1_sr_o9_partition_successor/RESULT.md)
- [PS1 production namespace](../../level4/closure_proofs/p5y_k1_ps1_production/README.md)
- [Generation-2 portable recovery (published branch `p5y-k1-ps1-gen2-lineage`)](../../level4/closure_proofs/p5y_k1_ps1_portable_recovery/RESULT.md)
- [Post-K1 status correction](../../level4/closure_proofs/p5y_postk1_frontier/PS1_STATUS_CORRECTION.md), [post-K1 DAG](../../level4/closure_proofs/p5y_postk1_frontier/P5Y_POST_K1_DAG.md), [K2–K5 audit](../../level4/closure_proofs/p5y_k2k5_postk1_audit/RESULT.md)
