# U2 factual reconstruction for P309 package 1 (pre-freeze; for owner confirmation and independent review)

**Owner decision (verbatim excerpt).** "Confirm that U2 is not triggered for P309 package 1 because the authorized
route uses no P3-derived quantity. If the formal-campaign reconstruction discovers that this statement is factually
false, STOP before freeze and report the discrepancy. Do not silently reinterpret U2."

**U2 as defined in the committed governance record** (`research/dossier/sources/READER_B_GOVERNANCE_REPORT.md:43`):
"admissibility of **new** quantities derived from P3 tail records (C6 Condition 10: *No P3 object may be adopted as
new scientific evidence*). A ruling is needed before any Stage-1 freeze (KG-U2)."

The record gives these triggering examples:
* SC is "a **new** scientific quantity derived from P3 records" (`research/dossier/digests/SC_SUPNORM.md:252`);
* RSO regeneration (`RSO.md:229`);
* new K1 records (`COVER.md:226`).

The same record states that the tail records, including 309's K1 Aux5 record, have P3 provenance
(`CELL309_DOSSIER.md:43`; `READER_A_309_HISTORY_REPORT.md:25`).

## Every quantity P309 uses, by provenance

| stage | quantity | provenance | new? | derived from P3 records? |
|---|---|---|---|---|
| 1a | the cell interval C, the hull Ew, the sub-blocks | the cell definition in the pinned `cells.json` | structural | no |
| 1a | W, V certificates; Γ̄_1..Γ̄_4 | the CUSUM kernel operator at drifts in Ew only (THEOREM_SRK), exact | **new** | **no**, operator-only |
| 1b | A1_RLR, A2_RLR | RLR307 Stage-1 rules, C1B_R2 operator certificates over drift blocks of the frozen C2 partition | **new** | **no**, operator-only |
| 2 | S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)) | a min of operator-only supplies (S_I1 = registries C1/C2 and Lemma G) | **new** (composition) | **no** |
| 2 | TC-T scalars (s_F, s_D, s_H, the deviations, eps_src, H_at_a, W2 enclosures, σ3, σ4), `TCT_INPUTS_309`, `ADOPTED_TAIL_INPUTS` | Campaign B measurement of the tail record | not new: committed and consumed by C2 | **P3-provenance, consumed unchanged** by the pinned `tct_rule` in its frozen role |
| 2 | K1 record fields (R2 interval, M_R2, …) | the sealed K1 Aux5 record | not new | **P3-provenance, consumed unchanged** by the pinned C2 clause |
| 2 | rad_r^SRK, 𝓗_SRK, M, Γ | outputs of the frozen consumer with the operator-only substitutions S1 and S2 | new values, frozen formulas | computed from P3-provenance scalars in their frozen roles. This is the same category as C2's own Γ (TC-T with S_I1), and as the cell-307 RLR Γ (TC-T with S_RLR). No new statistic of the P3 records is formed (contrast SC, which recomputes composite sups from the candidate payloads) |

## Finding

1. **Under U2's committed definition, U2 is not triggered.**
   * P309 adopts no new P3 object as evidence.
   * Its only new evidence objects (Γ̄, A1_RLR, A2_RLR) are operator-only certificates that never touch a P3 record.
   * Every P3-provenance input enters only through the pinned frozen consumer path, in exactly the role in which C2
     consumed it.
2. **The owner's stated reason is literally imprecise.** "The authorized route uses no P3-derived quantity" is not true
   word for word. Stage 2 **consumes** P3-provenance scalars (the TC-T inputs and the K1 record fields) through the
   frozen consumer, as every K5 tail consumer does, including C2, which established 309's current OPEN status. The
   accurate statement is: *"the authorized route derives no **new** quantity from P3 records; P3-provenance inputs enter
   only through the frozen consumer path in their frozen roles."*
3. **Handling.** This is surfaced explicitly to the owner (not silently reinterpreted) and submitted to the independent
   incident-independence review. **The freeze is not performed unless one of these holds:**
   * (a) the owner confirms the ruling on the accurate premise; or
   * (b) the independent reviewer confirms that the ruling as worded is satisfied on these facts and that no new P3
     quantity exists.

   Otherwise: STOP before the freeze.
4. **Precedent check (ledgered read).** A search for "U2" in the cell-307 formal campaign's governance files
   (`protocol/`, `README.md`, `FINAL_REPORT.md`, `audit/`) returned nothing. That campaign did not address U2
   explicitly, so it provides no precedent either way.
