# U2 corrected proposition for P309 package 1 (owner rulings 2, 2026-09-30; pre-freeze)

**Status.** This document is required by the owner's U2 ruling (`governance/OWNER_RULINGS_2_P309_VERBATIM.md`,
section "OWNER RULING — U2"). The owner confirmed U2 = NOT_TRIGGERED **only** on the corrected premise, and only if
that premise is established from committed evidence. If it cannot be established, the campaign STOPs before the freeze
with **U2_UNRESOLVED**. This document states the premise, lists every potentially P3-derived quantity, and gives the
mechanical evidence. It is submitted for independent check before it is relied on.

## 1. Preserved verbatim

The independent incident-independence review (`reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`, sha256
f5ff1d68d8749935ac9f89da62231ae266a41e85cfb237e542bb10356e14d85c, committed 39ed662c), line 3:

    U2_FINDING: NOT_TRIGGERED_WORDING_DISCREPANCY

That finding stands and is not overwritten. Its §8 and condition C7 are the basis of this document.

## 2. Withdrawn wording

The research package's statement "P309 uses no P3-derived quantity" (`P309_OWNER_DECISIONS.md:21`, relayed in
`REVIEW_SRK_R2.md:44` and in `U2_FACTUAL_RECONSTRUCTION.md`) is **withdrawn as false**. It originated in the research
package, not with the owner. Stage 2 consumes P3-provenance inputs, and SRK's radius formula (S2) recombines several
of them in a new formula. The formal campaign will not repeat that wording in any freeze document, grant or handoff.
`U2_FACTUAL_RECONSTRUCTION.md` is left unchanged as a record. Its rad_r^SRK row ("frozen formulas") is superseded by §5
below, as the review found.

## 3. What requires U2 authorization (committed evidence only)

* **Definition** (`research/dossier/sources/READER_B_GOVERNANCE_REPORT.md:43`): "admissibility of **new** quantities
  derived from P3 tail records (C6 Condition 10 …). A ruling is needed before any Stage-1 freeze (KG-U2)."
* **Primary text, C6 Condition 10** (`p5y_k5_tail_c6_evidence_recovery/evidence/adjudication/C6_ADJUDICATION.md:666`,
  read masked and ledgered): "**No P3 object may be adopted as new scientific evidence.** All four recovered records
  are P3 with `admissible_for_NEW_scientific_reuse: false`."
* **The standing of adopted inputs** (same file, lines 175–178): the four tail records' standing "belongs to the
  predecessors' adoption of those bytes (ADOPTED_TAIL_INPUTS, TCT_INPUTS, C2–C5 consumption)". Lines 420–422: the
  recovered bytes "are identical to what `ADOPTED_TAIL_INPUTS` names".
* **The committed examples of objects that need U2**:
  * SC: a **new statistic** recomputed from candidate payloads (`SC_SUPNORM.md:252`);
  * RSO: **regeneration** of payloads (`RSO.md:229`);
  * CR/COVER: **new K1 records** (`COVER.md:226`, `D309_SUMMARY_AND_NEGATIVES.md:266`);
  * R10 Corollary T: "it **tightens a recorded interval** with a new quantity derived from the record, so it needs the U2
    ruling" (`theory/PHASE1_RESULTS.md:169`; `ROUTE_MATRIX.md:69`; `ROUTE_SELECTION_RULE.md:29`).
* **Rule S C3** (`ROUTE_SELECTION_RULE.md:15`, fixed 2026-09-29 13:52, before any decoy comparison): "No candidate
  payloads, no new K1 or order-3 records, no replay host (U1), no new quantity derived from the P3 record (U2)."

So on committed evidence a quantity requires U2 authorization if it is one of these:
* **(Q1)** a new statistic or measurement of P3 records or payloads;
* **(Q2)** a regeneration or replay of P3 data;
* **(Q3)** a new K1/order-3 record;
* **(Q4)** a re-derived or tightened **record-level** field or interval (Corollary T);
* **(Q5)** adoption of a P3 object as new evidence beyond its existing adopted standing.

## 4. The corrected proposition

> **U2-CP.** P309 package 1's load-bearing path (Stage 1a, Stage 1b, Stage 2, as frozen) invokes no quantity of
> class Q1–Q5. Precisely:
> 1. **New evidence objects are operator-only.** Its only new evidence objects are the Stage-1a SRK certificates
>    (Γ̄_1..Γ̄_4) and the Stage-1b RLR certificates (A1_RLR, A2_RLR). They are computed from the CUSUM kernel
>    (h = 5, k = 1/2) at drifts in Ew, and from the frozen C2 partition of the cell interval. They read no P3 record,
>    measurement, adopted input or registry, and no Stage-1 module imports a consumer or record module.
> 2. **P3-provenance inputs enter only with their adopted standing.** Every P3-provenance value on the Stage-2 path is
>    an already-adopted input (`TCT_INPUTS_309`, `ADOPTED_TAIL_INPUTS`, the adopted K1 record and its auxiliary
>    evidence), read unchanged through the pinned loader and the frozen validation gates, in exactly the roles C2
>    consumed them. The post-grant, pre-marker historical control must reproduce C2's committed Γ_exact for 309
>    byte-identically before the marker. That shows the inputs are the adopted bytes.
> 3. **No record-level quantity is re-derived.** No record field or recorded interval (R2_interval, M_R2, R_interval,
>    D_interval, eps_cell_refined, C_upper, candidate_suprema, midpoint_eps) is recomputed, tightened or re-derived.
>    The direct clause reads them by subscript only. The adapter never reads them. This is the Corollary T boundary
>    (Q4).
> 4. **The one new formula forms no new function of adopted scalars.** S2 replaces rad_r by rad_r^SRK (THEOREM_SRK §3),
>    and this is a new consumer-level formula. But every sub-expression of adopted scalars in it is one the frozen TC-T
>    radius already forms:
>    * s_H, s_D, s_F, σ3 + ε3, σ4, s_D + ρs_H and s_F + ρs_D + ρ²s_H/2;
>    * f_H, and the Taylor terms p1 and p0.
>
>    SRK changes only the operator-side multipliers of those sub-expressions (A0·k_i → Γ̄_i), under a min with the frozen
>    value. rad_r^SRK ≤ rad_r is enforced as a refusal. This is an exact polynomial identity (§6, S1).
> 5. **The supply composition is a min.** S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)). The S_I1 components
>    (including Lemma G's, built from the adopted C_upper) come from the frozen `combine` unchanged, and they are only
>    min-composed with operator-only values.
>
> **Consequently** the new consumer-level outputs (rad_r^SRK, 𝓗_SRK, M, Γ) are the same category as C2's own TC-T
> enclosure and Γ: consumer-level quantities built from adopted inputs in their established roles. They are not P3
> objects adopted as new evidence (C6 Condition 10). **U2 is NOT_TRIGGERED on this premise.** The wording
> "uses no P3-derived quantity" is not relied on.

The reviewer judged the line between SRK (a consumer enclosure) and Corollary T (a record interval) "defensible, but
not self-evident". §6 makes the S2 part mechanical. Only the classification judgement itself (is a consumer-level
radius over adopted scalars a Q1–Q5 quantity?) remains the owner's. The owner's ruling adopts it on this premise.

## 5. Every potentially P3-derived quantity encountered, and its role

"Load-bearing" means Γ's value depends on it. "Gate-only" means it only passes or fails a check, and a failure is an
exception (EXECUTION_INDETERMINATE after the marker; STOP before it). "Present-only" means it is loaded or present in
an input file but never used on the 309 path. Field names come from the AST inventory (§6 S2) and from the key
structure of the two input files (types only; no value read).

| quantity (field) | source object (provenance) | role on the P309 path | how it enters | Q1–Q5? |
|---|---|---|---|---|
| sup F/D/H (s_F, s_D, s_H) per r | TCT_INPUTS_309 `r.<r>.sup.*` (Campaign B measurement of the tail record; P3, adopted) | load-bearing | frozen `tct_rule.tail_object`; `srk_adapter.fields_for_r`, after the exact-reproduction gate | no: unchanged, same sub-expressions (S1) |
| delta_F/D/H, eps_src[0..3] (f_F, f_D, f_H, ε3) | TCT_INPUTS_309 `r.<r>.*` | load-bearing | same | no |
| H_at_a (centres), W2 enclosures | TCT_INPUTS_309 `r.<r>.H_at_a`, `W2.<r:j>` | load-bearing | assembly with the frozen coefficient table, unchanged | no |
| rho, norms.k, norms.j, sup_S0 | TCT_INPUTS_309 | load-bearing | frozen `tct_rule` (f_G, Env4, σ3, σ4 towers); k1/k2 also in Lemma G | no: frozen roles |
| candidate_suprema, midpoint_eps (the adopted order-3 bounds) | adopted K1 record `auxiliary_evidence` | load-bearing | frozen `tct_rule.sigmas` → σ3; SRK reads σ3/σ4 from the frozen object | no |
| f_G, Env4, σ3, σ4, rad, half | frozen `tct_rule` object (consumer outputs from the rows above) | load-bearing (TC-T branch of the min; reproduction gate) | read by the adapter; re-derived and compared exactly | no |
| C_upper | adopted K1 record (P3, adopted) | load-bearing | Lemma G supply via the frozen `atom_constants_generic` and `combine` → S_I1 | no: frozen roles; only min-composed |
| R2_interval, M_R2 | ADOPTED_TAIL_INPUTS `cells.<309>.m.5` | load-bearing | frozen `direct`: intersection with 𝓗, M | no: subscript read only (S4) |
| R_interval.hi, D_interval.lo | ADOPTED_TAIL_INPUTS | load-bearing | frozen `direct`: g_hi | no: subscript read only |
| e0, rho, right (x_hi) | adopted cover (`cells.json` via the pinned loader) | load-bearing (structural cell geometry) | frozen `direct` | no: cell definition |
| A0/A1/A2 of C1, C2 | REGISTRY_C1/C2 (operator-only certified registries) | load-bearing | frozen `atom_constants_r2`, `combine` | not P3 |
| Γ̄_1..Γ̄_4 | new Stage-1a certificates (operator-only) | load-bearing | gate → adapter → B3/B4 | not P3 (S3) |
| A1_RLR, A2_RLR | new Stage-1b certificates (operator-only, C1B_R2) | load-bearing | min with S_I1 | not P3 (S3) |
| rad_r^SRK, 𝓗_SRK, M, Γ | new consumer-level outputs | the result | THEOREM_SRK §3 plus the frozen direct clause | not a P3 object (§4.4, S1) |
| identity_gate.identical, order3_fields_present, k1_record_sha256, cell | TCT_INPUTS_309 | gate-only | frozen validation (`c2_d5_forecast.main` pattern) | no |
| eps_cell_refined, R2_interval (rebuilt containment) | adopted K1 record | gate-only | frozen `tct_rule.derived_identity_gate` | no |
| record manifest hash, cells.json hash, record_sha256 | adopted state | gate-only | pinned loader bindings | no |
| TC-T crosscheck enclosure | frozen `tct_rule.tail_enclosure_crosscheck` | gate-only | equality with the primary TC-T enclosure | no |
| C2's committed Γ_exact for 309 | C2 evidence | gate-only (historical control; post-grant, pre-marker) | byte-identical equality; digest sealed | no: comparison only |
| R_interval.lo, D_interval.hi, other m entries, identity_gate.fields_compared, mode, schema, left, e0 (TCT copy) | input files | present-only | not read on the 309 path | no |
| records and objects of other cells (305–308 and the rest of the cover), text objects, Campaign-A cells | loaded by the pinned `adopted_state` | present-only | loaded and hash-checked, **never evaluated**. The P309 driver must not call `compose` or `direct` for any cell other than 309 (FC4 requirement; checked in QC and post-execution: "no other cell was evaluated") | no |
| Corollary T, SC, RSO, payloads, new K1 records, SRK-T's D_lo, TPT | — | **absent** | not on the path (rule S; SRK-T OUT) | (would be Q1–Q4) |

## 6. Mechanical evidence (committed with this document)

* `code/u2_structure_check.py` → `evidence/u2/U2_STRUCTURE_CHECK.json` (ok = true). This is a static analysis of the
  pinned source text. Nothing from the analysed files is executed.
  * **S1:** exact polynomial identities over Q, computed from the AST (no sampling):
    * new3[Γ̄_i := A0·k_i] = A0·f_G^TCT;
    * new4[Γ̄_i := A0·k_i] = A0·Env4^TCT at s_G = 0;
    * `p_terms` = `tc_rule.taylor_bounds`;
    * `rad_tct` = `tc_rule.radius`;
    * rad^SRK with the TC-T branches equals rad^TCT.

    The Γ̄-coefficients (3s_H, 3s_D, s_F; 6s_H, 4s_D + 4ρs_H, s_F + ρs_D + ρ²s_H/2) equal the k_i-coefficients of the
    frozen f_G and Env4.
  * **S2:** the field inventory (key names only) used in §5.
  * **S3:** Stage-1 isolation. The producer, gate, verifier, the RLR307 Stage-1 code and the C1B_R2 load-bearing files
    import no consumer or record module and name no record, measurement or adopted-input file. The RLR307 pinned
    loader loads only the C1B certifier files.
  * **S4:** the direct clause reads R2_interval, M_R2, R_interval and D_interval with no subscript assignment, and the
    adapter subscripts no record field.
  * **Pins:** every analysed file matches its sha256 in the rev. 2b candidate manifest.
* `tests/test_u2_structure_controls.py` → `evidence/u2/U2_CONTROLS.json` (all_pass = true). Eight planted defects each
  make the checker fail:
  * an extra adopted-scalar product;
  * a changed coefficient;
  * a multiplier moved to the wrong scalar;
  * a drifted frozen Env4;
  * a producer importing a consumer;
  * Stage 1b naming a record file;
  * the direct clause recomputing a record interval;
  * the adapter reading C_upper.
* Every read is ledgered (`ledger/EXPOSURE_LEDGER.jsonl`): code skeletons with numbers masked, JSON key structure with
  types only, and a masked grep of the C6 adjudication. No 305–309 value was displayed. `carried_309_numbers = false`
  on every line.

## 7. Conclusion and handling

* **U2-CP is established from committed evidence**: the documents in §3 and the pinned code in §6. U2 = NOT_TRIGGERED
  on that premise, as the owner ruled.
* The freeze documents and the proposed grant will carry U2-CP verbatim (§4), not the withdrawn wording, together with
  the review's NOT_TRIGGERED_WORDING_DISCREPANCY finding.
* **Freeze obligations derived from this document:**
  * (F-U2-1) The frozen pin set includes `code/u2_structure_check.py` and its controls. QC re-runs them on the frozen
    tree.
  * (F-U2-2) The Stage-2 driver evaluates the direct clause for cell 309 only, and never calls `compose` or `direct`
    for another cell.
  * (F-U2-3) The historical-control equality is a hard pre-marker gate.
* **Independent check.** Before the freeze relies on U2-CP, it is submitted to independent check (brief committed
  first; condition C5). If the check finds U2-CP not established, the campaign STOPs with **U2_UNRESOLVED**.
