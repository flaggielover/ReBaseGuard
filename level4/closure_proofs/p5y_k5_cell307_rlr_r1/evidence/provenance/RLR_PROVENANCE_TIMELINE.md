# RLR route: provenance and temporal-integrity timeline (campaign brief §3, §5)

All times are **committer timestamps** of commits on `p5y-k5-tail-overnight-306-309` (base `8b9fc0bb`, handover
`7f45e048`), in +09:00. Commit order is authoritative. The PROGRESS.md "[hh:mm]" stamps are **not** wall-clock
times (REVIEW_RLR_R3_VERIFY N4); they are not used here. Blob ids are at `7f45e048`.

**Result of this reconstruction.**
* No evaluation of Γ(5, 307) exists, under any supply, anywhere in the repository history. See
  `evidence/start/START_STATE.json`: `no_cell307_marker_or_result_ref` and
  `no_cell307_result_artifact_in_any_history`.
* The overnight ledger records **no** computation on cell 307 or on any drift in the quarantined band.
* The only ledger lines naming 307 are the two qualitative `PROXY_EXPOSURE` lines of incident 01 and its residue.
  These are prose co-locations; nothing was computed.
* Every load-bearing RLR design choice precedes the handover, and therefore precedes any possible target execution.

## 1. Timeline

| # | time (+09:00) | commit | event | load-bearing for RLR? |
|---|---|---|---|---|
| 0 | 09-28 02:32 | `6735d945` | Overnight charter, target quarantine and zero-target ledger frozen before any science | governance |
| 1 | 02:49 | `cbff958a` | **First design.** `IDEA_LR_SCORE_CONSTANTS.md` and `pm_probe_synthetic.py`: score representation of A1/A2, synthetic exact probe (8 finite-state seeds, e = 1/8). States its motivation: committed C3 knockout, "cells potentially relevant: 307 … 308 (partial)". No cell data computed | yes (idea) |
| 2 | 03:17 | `4403f86f` | Dependency graph r0. Incident 01 is introduced here (TPT factors next to committed tail shares). The same document's §3 also carries the synthetic probe ratio of row 1 near the committed Dv′ share column (residue, see audit §2.1) | no (graph) |
| 3 | 03:56 | `7e851139` | **First theorem and first implementation.** `THEOREM_LR.md` (LR-1…LR-4, RLR = LR-3, block uniformity) and `lr_fsm.py`. **First non-target validation**: exact finite-state fixtures (`C1LR_FSM_VALIDATION.json`, 24 seeds, e ∈ [0, 1/4]) | yes |
| 4 | 04:09 | `2f0fb5e1` | Incident 01 recorded; TPT tail use BLOCKED | no |
| 5 | 05:13 | `07ab6b94` | Incident 02 recorded (cell 308, A0 channel) | no |
| 6 | 06:06 | `4d64e2b0` | Incident 03 recorded (cell 308, C2b brief) | no |
| 7 | 06:15 | `2b118e62` | **First real-kernel implementation and validation.** C1b `c1b_*.py`: RLR certificate on the real CUSUM kernel at e ∈ {0, 1/4, 1/2, 1, 3} and the block [1/2, 17/32]. Declarations D0–D11 are written before their runs | yes |
| 8 | 06:28–06:39 | `eb55bcab`, `0e081456`, `8531fa57` | Global integrity review repairs. C1a t-flip control withdrawn and re-planted in the solver; RLR G6 set to pending review | validation |
| 9 | 07:30 | `8414614f` | **First review**, REVIEW_RLR_R1. INCOMPLETE: the reviewer stalled; not a verdict | review |
| 10 | 07:48 | `1c4b9fca` | REVIEW_RLR_R2: **ACCEPTED_WITH_CONDITIONS** (C1–C5). Main finding: RLR ≤ Dv′ holds for exact ρ only | review |
| 11 | 07:50 | `2abe29b1` | **Repair.** C1a dominance statements corrected (exact ρ only; certified supply = min) | theory text |
| 12 | 09:14 | `3d13c138` | **Repair (R2 response).** D12 (e-free block family), D13 (coverage), D14 (combined SUPPLY in load-bearing `assemble`), D15 (block controls), D16 (pins + provenance). Code pins r1 written **before** the pinned regeneration: 27 jobs, all rc = 0 | **yes (final load-bearing code)** |
| 13 | 10:33 | `7e35b12c` | REVIEW_RLR_R3_VERIFY: **CONFIRMED_WITH_NOTES** (N2–N8) | review |
| 14 | 10:36 | `9e8ae240` | Protocol draft r0: cell set {307, 308, 309} | draft |
| 15 | 10:45 | `47933904` | **Final C1b fix.** D18: two-sided combined-supply test with six mutants (N5); N3 pre-pin moves; N2 provenance. Pins r3. **Load-bearing set unchanged since r1** | validation (test only) |
| 16 | 10:51 | `d3b60795` | **FREEZE_READY declared** (closure-only). Protocol draft r1: cell set **{307} only**, fixed by the committed C3 knockout scope fact before any result | declaration |
| 17 | 10:52 | `7f45e048` | Morning handover and governance audit | — |

## 2. The object that is frozen, and when it was fixed

| object | fixed at | evidence |
|---|---|---|
| Theorem LR-3 (ratio and non-ratio forms), block uniformity (§6) | `7e851139`; wording corrected at `2abe29b1` (no mathematical change to LR-3 itself; the dominance claim was narrowed) | THEOREM_LR.md blob `6f4f1fbe6b99` |
| Certifier code: load-bearing `c1b_gauss/kernel/pw/certpw/certify` and candidate generator `c1b_float` | `3d13c138` (pins r1). Unchanged in r2 and r3 | C1B_R2_CODE_PINS.json blob `712a9d2d059a`: `load_bearing_unchanged_since_r1 = true` |
| Block family and settings (D11 light, D12 e-free PW_d, D13 coverage, D9 tight C_T) | D11 before the first block run (`2b118e62`); D12/D13 before the R2 regeneration (`3d13c138`) | PROGRESS.md blob `159badb5759c` |
| Combined supply D14: term-level min with the Dv′ factors, then componentwise min with Lemma G (LR-4 form) | `3d13c138` | `c1b_certpw.assemble` (pin `48080dd4…`) |
| Two-sided combined-supply test, six mutants | `47933904` (test file only) | C1B_R2_TEST_COMBINED.json blob `ac696d2be3f4` |
| Cell set {307}; A0 unchanged; S_RLR = componentwise min with the committed supply; the C2 partition rule; the worst-block composition; the frozen C2 consumer; the reproduction gate | `d3b60795` (draft r1) | RLR_FREEZE_PROTOCOL_DRAFT.md blob `1205375c413c` |

**Decisions this formal campaign adds.** None of these existed overnight, so each is new. None depends on any
target quantity. Each is fixed in the frozen protocol before any target execution, and is listed for the reviewers
in `protocol/RLR307_PROTOCOL.md` §3:
1. The outward dyadic hull at 2^-20. It is required because the pinned integer Taylor model accepts only dyadic
   drift centres and radii, while the C2 partition endpoints of cell 307 are decimal.
2. The degree ladder for blocks is the D8 ladder (4, 6, 8), with the pinned CLI's ladder composition. This is how
   C1B_ROUTE_SUMMARY §8 items 2 and 6 bind it.
3. The exception classification and the caps.

## 3. Temporal integrity: result

* All load-bearing design choices (rows 1, 3, 7, 11, 12, 16) precede the handover `7f45e048`.
* This campaign starts from `7f45e048`. It evaluates cell 307 only after its own freeze, its independent
  qualification review and its grant.
* No target execution exists before this campaign. Nothing in rows 0–17 computed on a drift in [6/5, 13/5] or its
  mirror: the overnight guard `ov_quarantine.guard_drift` refused such drifts, and the ledger shows no such line.
* The remaining risk is **motivation provenance**, not temporal order. The route and its cell were chosen with
  knowledge of committed tail facts (row 1: the C3 knockout). This is analysed in `audit/INCIDENT_AUDIT_RLR307.md`.
