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
