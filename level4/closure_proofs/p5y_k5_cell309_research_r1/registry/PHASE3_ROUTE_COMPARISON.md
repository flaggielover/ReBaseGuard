# Phase 3: route comparison for cell 309 (prospective evidence only)

**Selection rule.** `registry/ROUTE_SELECTION_RULE.md` (rule S, fixed before this comparison). No 309 quantity is
used anywhere. Decoy numbers are latent proxies; they are reported only as dimensionless decoy-only ratios and never
next to a tail number.

## Surviving candidate components (not REJECTED)

### SRK, whole kernel (R16)

* **Theorem readiness:** THEOREM_SRK with Lemmas SK, SV, SV′ and amendment A1. Written and self-checked. The
  exact-truth FSM test passes 12/12 on genuine checks; its mutant controls catch M1 12/12 and M4 6/12, while M2 is not applicable and M3 is caught 0/12 (covered only by the two-sided assembly test) [wording corrected per review R1 B6]. The independent review is pending
  (`reviews/REVIEW_SRK_R1.md`).
* **Implementation readiness:** certifier (port identical to C1b, 84/84), envelopes, assembly (two-sided test, 10/10
  mutants), adapter (6×20 checks).
* **Independent-verifier readiness:** a spec-only verifier is being built by an independent agent (`verify/`).
* **Compute cost for a formal run:** operator-only, about minutes per certificate on the decoy blocks; around an hour
  for a 4-sub-block cell ladder (estimate from the decoy blocks only).
* **Qualification cost:** hours (decoy suite, Monte Carlo, verifier, mutants, sandbox exactly-once flows).
* **Exactly-once compatibility:** yes. Stage 1 is deterministic. Stage 2 is a single exact Γ through the frozen path
  with an injected enclosure, gated by exact reproduction.
* **Temporal-integrity risk:** LOW. Charter and quarantine precede all science, and the decoys are declared before
  runs.
* **Result-chasing risk:** MEDIUM-HIGH (programme-wide dominance knowledge; 309R1-01/02).
* **Liabilities:** 309R1-01/02; the overnight incidents are disclosed.
* **Remaining before FREEZE_READY:** see the end of this document.

### SRK-T, taboo kernel (R17)

* **Theorem readiness:** Lemma SV-T (amendment A2), self-checked; review pending.
* **Implementation readiness:** certifier flag `whole=False`.
* **Independent-verifier readiness:** not covered by the spec yet. The (C2)/(C3) claims need K̂ in place of K.
* **Compute cost:** as SRK.
* **Qualification cost:** as SRK, plus the taboo Monte Carlo.
* **Exactly-once compatibility:** yes. D_lo is pinned from the supply registry.
* **Temporal-integrity risk:** LOW.
* **Result-chasing risk:** as SRK.
* **Liabilities:** as SRK.
* **Remaining before FREEZE_READY:** a taboo verifier mode, the taboo decoy suite, and the review.

### RLR A1/A2 min-component (R4)

* **Theorem readiness:** reviewed (R2, R3; RLR307 qualification).
* **Implementation readiness:** the pinned C1b certifier.
* **Independent-verifier readiness:** RLR307 has an independent reconstruction.
* **Compute cost:** about 2–3 CPU-h per cell (307 precedent).
* **Qualification cost:** reuse the 307 qualification pattern with a new driver.
* **Exactly-once compatibility:** yes (307 precedent).
* **Temporal-integrity risk:** LOW.
* **Result-chasing risk:** MEDIUM. The C3 knockout is known, but inclusion is by rule S, not by need.
* **Liabilities:** the 307 disclosures C1–C6.
* **Remaining before FREEZE_READY:** a 309 block partition by the frozen C2 rule, inside the formal campaign.

## Routes not surviving

For the reasons see `dossier/ROUTE_MATRIX.md`.
* **TPT, TPT∘SRK:** liability-blocked.
* **SC, RSO-P, real Ĝ / O3-X, cover refinement, sup-norm:** data-blocked.
* **Corollary T:** U2.
* **Atom-constant families:** rejected.

## Preferred route (by rule S)

**P309 = frozen direct clause**, with:
* the TC-T enclosure's order-0 channel replaced by the SRK min construction. The taboo form SRK-T is included only
  if it becomes ready in the same package; otherwise it is omitted, which is safe;
* supply S = (A0 from S_I1, A1/A2 = min(I1, RLR)).

Closure-only; one sealed evaluation, in a separately authorized campaign.

## Readiness ledger for P309

To be filled after the decoy suite, the independent verifier and the independent review:

| item | status |
|---|---|
| declared decoy suite (whole kernel) | running |
| independent verifier on the decoy certificates | running |
| Monte Carlo positive control | pending decoys |
| taboo family (SRK-T) | declared, not run |
| independent route review | brief written (`reviews/BRIEF_SRK_ROUTE_REVIEW_R1.md`) |
| consumer adapter against the real pinned `tct_rule` | design plus manufactured-input tests. The real pinned-module qualification belongs to the formal campaign (QC) |

## Rule-S application update: SRK-T (recorded 2026-09-29, before any taboo-family output of the rerun exists)

SRK-T's Γ̂_i = v̂/D_lo needs a certified lower bound D_lo valid on the cell (THEOREM_SRK §12).
* For cell 309, D_lo would be the pinned supply-registry value. That is formal-campaign data and is not read here.
* For decoys, this campaign has **no D_lo certifier**, so the Γ̂ path cannot be qualified end to end on decoys.

Criterion C5 ("qualified on decoys and cross-checked") is therefore **not met** in this package, and **SRK-T is OUT of
package 1**. This is safe: SRK-T is min-composed, and omitting it can never invalidate the route (rule S). The
decision uses only C5. It uses no decoy gain and no 309 quantity.

The taboo decoy family (whole-block v̂ certificates, independent verification, taboo MC) is still run as
**preparatory** evidence for a later package. Its results cannot change package 1: adding a component after any
309-related number is known is forbidden by rule S, and this decision precedes the taboo results.

P309 (package 1) = frozen direct clause, with:
* the SRK-0 whole-kernel B3/B4 min construction in the order-0 channel term;
* S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)).

Closure-only.

## Readiness ledger for P309 (update; replaces the table above when complete)

| item | status |
|---|---|
| R1 blockers B1–B6 | repaired: see `reviews/BRIEF_SRK_ROUTE_REVIEW_R2.md` for the map; ERRATA E-1..E-11 |
| declared decoy suite, whole kernel, single code state | running from 2a03e838 (runner lock) |
| A2 cell family (A3 hull rule, verifier, gate, MC end to end) | running from 2a03e838 |
| independent verifier | built and final (20/20 prelim ACCEPT, 415/415 mutant expectations); the rerun certificates are pending |
| MC positive controls | pending the rerun |
| taboo family | preparatory only (SRK-T OUT of package 1) |
| independent route review R2 | brief written; to launch when the rerun evidence is complete |
| tightness note | the verifier finds certified margins well above μ. Γ is conservative (e.g. V0 × (1 − 2⁻⁴) still valid on one decoy). This is a tightness matter only, and the min with A0 makes it harmless for validity |

## Readiness ledger update (2026-09-29 23:1xZ; evidence complete, before R2 phase B)

| item | status |
|---|---|
| single-code-state rerun | lock 2a03e838, producer 377057be… All 19 declared jobs are present (11 whole-kernel blocks, 8 A2 cell sub-blocks), 87 certificates, and every rung of every block certified (`evidence/SRK_EVIDENCE_MANIFEST.json`, complete = true) |
| independent verifier | 87/87 rerun certificates ACCEPT (107/107 including the preliminary ones). Every mutant expectation is met: 2196/2196 in the batch, and 0 unexpected results. The only mutants the verifier proves TRUE are the known SE-1 cases (V0 × (1−2⁻⁸), and index + 1 at i = 0). Genuine weight_block ⊋ block certificates are verified (32/32) |
| MC positive control | whole-kernel 55/55 PASS (5-se criterion; worst MC excess over Γ 2.23 se). Cell level 8/8 PASS |
| A2 end to end | PASS on both cells: in-process verdicts = batch verdicts; the gate is bound to cell and verifier and equals the max over sub-blocks; all 5 real-certificate negatives refused for their own reasons |
| controls | FSM truth (M1 12/12, M4 6/6, M5 12/12); assembly 10/10 with a live refusal; gate 33; adapter 17 × 20; W-record refusal; certificate battery T1 (refuted), T2, T8, T10 |
| self-audit | `evidence/self_audit/SELF_AUDIT_pre_R2_phaseB.json`: A1–A9 PASS (max ledgered drift 33/32) |
| taboo family | not run: SRK-T is OUT of package 1, so it would add nothing load-bearing |
| tightness (decoy-only; not load-bearing) | Γ/MC 0.99–1.39 on whole blocks. The loosest are the small-drift real-kernel blocks |
| independent route review R2 | phase A: no science blocker, and P-1/P-2 repaired. Phase B is being launched now |
