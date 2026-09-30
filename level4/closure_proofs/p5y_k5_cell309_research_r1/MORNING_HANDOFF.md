# MORNING HANDOFF: K5 cell-309 research campaign r1 (overnight 2026-09-29 → 30)

**Bottom line.** Cell 309 route **P309 package 1 is FREEZE_READY**, per independent review R2 phases A–D, line 2 of
`reviews/REVIEW_SRK_R2.md`. The prospective formal-campaign package is prepared in `protocol_prep/`: not frozen, not
authorized, never executed. It was reviewed independently by R3: **PACKAGE_REVIEW: COMPLETE**. The campaign stops
at **READY_TO_FREEZE_PENDING_OWNER_AUTHORIZATION**.

## 1–4. Branch and state

| # | item | value |
|---|---|---|
| 1 | branch | `claude/rebaseguard-k5-cell-309-w0jv8m` (the only ref ever pushed; checkpoint pushes only) |
| 2 | local HEAD | the commit that adds this file. Last verified checkpoint before the handoff: `60f0e2c9`. See the final console summary for the exact tip |
| 3 | remote HEAD | equal to the local HEAD after the handoff checkpoint push (verification check 9) |
| 4 | working tree | clean after the handoff commit. No background process is running |

## 5. Overnight commits

Since 17:00Z there are about 150 commits, including checkpoint-record commits. All are inside the research
namespace. Milestones:

| commit | what |
|---|---|
| 23ce9347 | overnight start: self-audit script (PASS) |
| 26d7e781 | evidence manifest builder |
| ce3cbd91 … f6c29f02 | rerun blocks and cell sub-blocks, independently verified as they landed |
| bff271d0 / 581aa729 | A2 cell family complete; A2 end to end PASS |
| 142fe64e | qualification evidence COMPLETE |
| b7f05327 | review R2 phase B preserved (FREEZE_READY_WITH_CONDITIONS) |
| b5ad2372 | C1 adapter geometry fixed; C2 erratum E-15 |
| 27b50777 | interruption record (container restart) |
| b3106070 / 0e4c6cdd | C3 closed by the verifier's author (harness v2; self-tests 21/21); E-16 |
| 426461c8 | review R2 phase C preserved; C4 repaired (verifier executions ledgered; incident 309R1-03; E-17; self-audit A10) |
| f026c80b | review R2 FINAL: FREEZE_READY |
| eb270ced | Phase 3 decision; route matrix update |
| ce829bb4 / 65b64e9e | Phase 4 candidate package; candidate freeze manifest |
| b48a1fa2 | brief for package review R3 |
| 814ff984 → 0a3f1604 | package rev. 2 → 2b per R3 (notes N1–N19, F2, D1–D2, P1–P5); incident 309R1-04; E-18 |
| 60f0e2c9 | R3 FINAL: PACKAGE_REVIEW: COMPLETE; pre-FREEZE_READY drafts preserved verbatim |
| (this commit) | FINAL_REPORT.md and MORNING_HANDOFF.md |

## 6–7. Jobs

* **Completed:**
  * the whole-kernel decoy suite (11/11);
  * the A2 cell family (8/8);
  * independent verification, batch v1 and v2;
  * the MC controls;
  * A2 end to end;
  * the evidence manifest;
  * self-audits;
  * reviews R2 (A–D) and R3 (initial and three follow-ups).
* **Still running:** none. No background process of the campaign is alive.

## 8–11. Evidence

| # | item | status |
|---|---|---|
| 8 | whole-kernel decoy suite | 11/11 declared blocks from ONE code state: lock 2a03e838, producer fingerprint 377057be…. Every rung certified; 55 certificates |
| 9 | A2 cell family | 8/8 sub-blocks (h3 C[1/3, 20/51], h5 C[1/2, 37/72]), hull weight blocks; 32 certificates. End to end PASS on both cells |
| 10 | independent verifier | Verifier `srk_verify_indep.py` a32d5d39… is unchanged. 87/87 rerun certificates ACCEPT (107/107 including the preliminary ones). Harness v2 (3455c141…): 1868/1868 reason-specific mutant expectations. 7q is refused for the band on 41/41 real-kernel certificates. Self-tests 21/21 |
| 11 | MC and controls | MC 55/55 whole-kernel rows plus 8/8 cell-level rows. FSM truth (M1 12/12, M4 6/6, M5 12/12); assembly 10/10; gate 33; adapter 19×20; W-record refusals; certificate battery T1 (refuted), T2, T8, T10. Self-audit A1–A10 PASS |

## 12–13. Review R2

| # | item | status |
|---|---|---|
| 12 | R2 phase A | No science blocker. P-1 (gate/consumer binding) and P-2 (T1 power) repaired before evidence completion, with no producer change |
| 13 | R2 phases B, C, D | B: FREEZE_READY_WITH_CONDITIONS (C1–C3). C: C1–C3 closed, new C4. D: C4 closed, no blocker of any class → **ROUTE_REVIEW: FREEZE_READY** |

## 14–16. Findings, repairs, recomputation

* **14. New findings and incidents.**
  * Masked-reason negative controls in verifier harness v1: 7q, 7f and 7h (E-16).
  * Verifier executions were never ledgered, and their probes reached 37/32, beyond the declared 33/32 decoy envelope
    and still outside the band (E-17).
  * **Incident 309R1-03:** an unsanctioned in-band v1 7h probe on h5 [1, 33/32], refused at parse time, nothing
    evaluated. Liability NONE, and R2 concurs.
  * **Incident 309R1-04:** Phase-4 drafting began in the uncommitted scratchpad at 2026-09-29 14:11Z, before any
    FREEZE_READY. No target information. Liability LOW, and R3 concurs. The drafts are preserved verbatim (E-18).
  * Governance/API hardening: the gate taboo path without D_lo (E-11, before R2); P-1 binding; C1 geometry override.
  * A container restart interrupted the v2 rerun (recorded, then completed from scratch).
  * No soundness finding.
* **15. Repairs.** P-1, P-2, C1, C2 (E-15), C3 (harness v2 plus self-tests, by the verifier's author), C4 (retroactive
  ledger lines, `code/verifier_probe_envelope.py`, A10), E-12..E-18. Package rev. 2/2b settles R3's notes. The checkpoint push was made
  record-first, which removes the unpushed-commit loop.
* **16. Evidence invalidated or recomputed.** No producer evidence was invalidated; no producer file changed after the
  lock. Recomputed:
  * the verifier's mutant batteries (v1 → v2), because the expectations were reason-blind;
  * the 34 batteries interrupted by the restart, rerun from scratch;
  * the verifier self-tests, after their fix.

## 17–22. Route and package

| # | item | status |
|---|---|---|
| 17 | final SRK route status | P309 package 1: frozen direct clause; SRK-0 whole-kernel order-0 min construction; S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)). **FREEZE_READY**, closure-only. SRK-T OUT (C5) |
| 18 | formal package | `protocol_prep/` holds the protocol, the formal package (QC01–QC16, driver, grant schema, recording the result from memory, post-execution checks, the four review briefs, adjudication, failure and recovery, FC1–FC6), the review briefs, the owner decisions and a candidate freeze manifest (48 code pins and 7 data pins). **PACKAGE_REVIEW: COMPLETE** (R3). Candidate rev. 2b |
| 19 | remaining blockers | Science, implementation, evidence and package: **none** (R2, R3). Owner: P0-1/G2, the cell set, G1, G3 (including the Stage-1b fallback), U2, U3, the Stage-1a failure mapping, incident acknowledgements (309R1-01..04, E-3, E-17(a), E-18), efficacy acknowledgement; optional SRK-T; later a separate grant and push/merge. Formal campaign: FC1–FC6, in particular the FC2 grant-scoped guard and verifier variant with QC16 re-qualification |
| 20 | remaining compute (estimate) | Formal campaign only: FC2 re-qualification of the grant-scoped verifier on the decoy battery (a few CPU-hours); Stage 1a SRK (≈ 4 sub-blocks × 3 rungs × 5 certificates, roughly 1–3 CPU-hours at the decoy rates; unknown at 309); Stage 1b RLR (≈ 2–3 CPU-hours, 307 precedent); Stage 2 (minutes). None of it is authorized |
| 21 | FREEZE_READY reached? | **Yes** (R2) |
| 22 | freeze prepared or performed? | **Prepared only (candidate). NOT performed.** The freeze requires owner authorization (P0-1), as confirmed by R2 |

## 23–25. Integrity statements

* **23.** **NEW Γ309 TARGET EVALUATIONS = 0.** NEW Γ308 TARGET EVALUATIONS = 0. No target-equivalent proxy, no band
  quantity. The ledger counters are all 0, and the self-audit A1/A2/A10 PASS.
* **24. Cell-308 noninterference.** No 308 file, ref, marker, worktree or process was touched or read. Everything ran
  in this isolated cloud container. The only branch pushed is the research branch (self-audit A7/A8).
* **25. r5, r6, adoption, K5/P5Y.** r5 is unchanged (blob f978eeb6). No r6 exists. No adoption was performed. No
  K5/P5Y status changed.

## 26. Next action that requires owner authorization

Decide the items in `protocol_prep/P309_OWNER_DECISIONS.md`. Above all, **P0-1/G2** (authorize a separate,
closure-only, exactly-once formal campaign for 309 on P309, including in-band Stage-1 over Ew and a grant), together
with G1, G3, U2 and U3. Only then would a formal campaign perform the incident-independence review, build and
re-qualify the FC2 grant-scoped variants, and freeze the candidate protocol unchanged.
