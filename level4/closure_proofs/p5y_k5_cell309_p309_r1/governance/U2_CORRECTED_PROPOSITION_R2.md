# U2 corrected proposition, revision 2 (conditions U1–U6 of the independent U2 check; pre-freeze)

**Status.** This revision supersedes `governance/U2_CORRECTED_PROPOSITION.md` (revision 1, commit 46533afd), which
stays unchanged as the record. The independent check (`reviews/REVIEW_U2_CHECK_P309.md`, commit 73200812) found
**U2_CP_ESTABLISHED**, subject to conditions U1–U6. This revision implements U1 (text), U2 (inventory), U3 (checker),
U5 (freeze declarations) and U6 (record binding). U4 (the extended checker passing on the frozen drivers) is a
freeze-time gate, QC-U2 (rev. 2c A17). **If U4 fails on the frozen tree, U2 is UNRESOLVED and the campaign STOPs before
the freeze.**

## 1. Findings preserved verbatim

* Incident-independence review, line 3: `U2_FINDING: NOT_TRIGGERED_WORDING_DISCREPANCY`
* Independent U2 check, line 2: `U2_CP_ESTABLISHED`

## 2. The proposition (this is the text carried verbatim into the freeze and the grant)

> **U2-CP (rev. 2).** P309 package 1's load-bearing path (Stage 1a, Stage 1b, Stage 2, as frozen) invokes no quantity
> of class Q1–Q5 (§3). Precisely:
> 1. **New evidence objects are operator-only.** The only new evidence objects are the Stage-1a SRK certificates
>    (Γ̄_1..Γ̄_4) and the Stage-1b RLR certificates (A1_RLR, A2_RLR). They are computed from the CUSUM kernel
>    (h = 5, k = 1/2) at drifts in Ew, and from the frozen C2 partition of the cell interval. They read no P3 record,
>    measurement, adopted input or registry. No Stage-1 module, and no Stage-1 driver function, reads any of these or
>    passes a value derived from them into a producer.
> 2. **P3-provenance inputs are used only under their existing adopted standing.** Every P3-provenance value on the
>    Stage-2 path is an already-adopted input (`TCT_INPUTS` for the cell, `ADOPTED_TAIL_INPUTS`, the adopted K1 record
>    data carried in it). It is read unchanged, from byte-pinned files, through the frozen validation gates, in exactly
>    the roles C2 consumed it. This is declared **prospectively**, as C6 requires for any use under an
>    already-adopted standing (C6:175–178, C6:665). The post-grant, pre-marker historical control must reproduce C2's
>    committed record for the cell byte-identically before the marker.
> 3. **No record-level quantity is re-derived on the load-bearing path.** On that path no record field or recorded
>    interval (R2_interval, M_R2, R_interval, D_interval, eps_cell_refined, C_upper, candidate_suprema, midpoint_eps) is
>    recomputed, tightened or re-derived. The direct clause reads them by subscript only, and the SRK adapter never
>    reads them. Two gate-only operations exist, exactly as in C2, and neither is load-bearing, tightened or adopted:
>    * the frozen `derived_identity_gate` rebuilds an R2 interval (H_at_a ± eps_cell_refined, plus W2) for a pass/fail
>      containment and tolerance check;
>    * C_upper is copied from the adopted inputs into the measurement dict, as C2's `main` does.
> 4. **The one new formula forms no new form of adopted scalars.** S2 replaces rad_r by rad_r^SRK (THEOREM_SRK §3),
>    a new consumer-level formula. Adopted scalars enter it only through:
>    * the k_i-coefficients and k-free parts of the frozen f_G and Env4: s_H, s_D, s_F, σ3 + ε3, σ4, s_D + ρs_H and
>      s_F + ρs_D + ρ²s_H/2;
>    * the unchanged f_H, p1 and p0.
>
>    Only operator-side multipliers change (A0·k_i → Γ̄_i), under a min with the frozen value (None → the frozen
>    value). rad_r^SRK ≤ rad_r is enforced as a refusal. The combined expression (new products, piecewise min) is a new
>    *function* of adopted scalars and Γ̄. It is not a new *form* of the adopted scalars.
> 5. **The supply composition is a min.** S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)). S_I1 comes unchanged
>    from the frozen `combine` of Lemma G (built from the adopted C_upper) and the operator-only registries C1 and C2.
>    A Stage-1b CERTIFICATION_FAILED gives S = S_I1.
>
> **Consequently** the new consumer-level outputs (rad_r^SRK, 𝓗_SRK, M, Γ) are the same category as C2's own TC-T
> enclosure and Γ: consumer-level quantities built from adopted inputs in their established roles. They are not P3
> objects adopted as new scientific evidence (C6 Condition 10). **U2 = NOT_TRIGGERED on this premise.** This
> classification is a **governance reading adopted by the owner's ruling** (owner rulings 2, "OWNER RULING — U2"). It is
> grounded in committed text, and it is not a mechanical result. The mechanical results (§6) establish the facts the
> reading rests on. Governance anchors:
> * READER_B:25 and READER_B:140–145 place consumer changes on the U3 / closure-only axis;
> * U3 = CLOSURE_ONLY is decided;
> * C6 Condition 10 is at C6:666.
>
> The wording "uses no P3-derived quantity" is withdrawn and is not relied on.

## 3. The criterion (U1: stated as a reading)

Q1–Q5 are a **reading** of U2's committed definition. The definition is "admissibility of new quantities derived from
P3 tail records (C6 Condition 10)". The reading is anchored in:
* the committed examples: SC, a new statistic; RSO, regeneration; COVER/CR, new K1 records; R10 Corollary T, a
  tightened record-level interval;
* C6's standing clause (C6:175–178).

It is narrower than the literal phrase "new quantities derived from P3 records". That phrase, read literally, would
cover every consumer output including C2's own Γ, and the programme accepted C2's Γ. The owner adopted this reading in
ruling on the corrected premise.
* (Q1) a new statistic or measurement of P3 records or payloads;
* (Q2) a regeneration or replay of P3 data;
* (Q3) a new K1/order-3 record;
* (Q4) a re-derived or tightened **record-level** field or interval on the load-bearing path;
* (Q5) adoption of a P3 object as new evidence beyond its existing adopted standing.

## 4. Inventory (U2: revision 1 §5, completed)

Revision 1 §5 stands, with these corrections and additions from the check (§3 items 1–5):

| addition / correction | role |
|---|---|
| the order-3 bounds (candidate_suprema, midpoint_eps) feed **σ3 and σ4** (through the `h:j:3` entries and the cell tower in `sigmas`), not σ3 only | load-bearing, frozen roles |
| the P309 driver reads C_upper, the auxiliary evidence and eps_cell_refined from the **byte-pinned ADOPTED_TAIL_INPUTS** (the 307 pattern), bound by the record sha to the pinned K1 export manifest (U6). C2's `main` read the same bytes from the K1 records | load-bearing (C_upper, auxiliary evidence), gate-only (eps_cell_refined) |
| present-only duplicates: the TCT copy of `right`; in ADOPTED_TAIL_INPUTS the entries of other cells, `R_interval.lo`, `D_interval.hi` and the other `m` entries | present-only |
| the P309 driver does **not** call `tail_forecast_r2.adopted_state`. It never computes text objects, and never loads the records of any other cell (a change from revision 1's row, which assumed the C2 `main` loader) | absent |
| gate-only, added: the adapter's ρ-versus-cell-half-width refusal; the adapter's `sup_G = abs_G_at_a = 0` refusal; the copy of C_upper into the measurement dict | gate-only |
| **absent, and must not be computed** (the C2 `main` diagnostics): <br>• `requirement` (the required uniform atom-constant reduction) and the gap / material-tightening classification; <br>• the C2 feasibility gate's baseline gaps; <br>• `compose` (the replay gate over the cover); <br>• `critical_ratio`, `atom_constant_requirement`, `classify`, `main`; <br>• `adopted_state`, `tail_enclosures`, `order3_inputs`. <br>They are target-equivalent diagnostics, several in the quarantine's forbidden class. QC-U2 U4(ii) checks their absence in the frozen driver and rehearsal | absent (forbidden) |

## 5. Record binding (U6)

The target cell's inputs are accepted only if all of these hold (driver `cell_inputs`, the 307 pattern):
* the measurement's `k1_record_sha256`;
* equals the adopted inputs' `record_sha256`;
* equals the entry `k4_records/aux5_CUSUM_<cell>_256.json` of the pinned K1 export manifest (`COMPOSITE_EXPORT_MANIFEST.json`,
  a data pin);
* and the adopted inputs' `manifest_sha256` equals that manifest's pinned sha256.

Every input file is byte-pinned (sha256 and git blob) in the freeze manifest. The data pins of the rev. 2b candidate
manifest must match by blob, and `code/make_freeze_manifest.py` refuses otherwise. No other copy of a P3 record may
enter under another path, C6's recovered files included: the driver reads data only through `data_rel(role)` from the
frozen manifest.

## 6. Mechanical evidence (U3; version 2 of the checker)

`code/u2_structure_check.py` (version 2) → `evidence/u2/U2_STRUCTURE_CHECK_V2.json`. It adds:
* **U3a** — every `fields_for_r` entry is bound by AST to its frozen `tct_rule` role, with no extra key;
* **U3b** — `srk_coefficients` selects exactly min(old, new) (None → old), with old = A0·f_G / A0·Env4, and `rad_srk`
  uses the selected branches;
* **U3c** — Stage-1 isolation over every loaded C1B module (the load order, not only the "load_bearing" list) and the
  guard modules, under a role whitelist (the research guard's refusal-pattern list is excluded from the record-word
  scan). The RLR307 helpers are checked against the 307 driver's HELPER_SHA256, and the C1B files against
  C1B_R2_CODE_PINS;
* **U4** — on the driver, the rehearsal and the FC2 components:
  * `direct` is called unchanged through the shim, and the genuine crosscheck runs first;
  * none of the forbidden consumer calls occurs;
  * Stage-1 functions read no record or measurement;
  * record fields are touched only in `cell_inputs`, where the single store is the C_upper copy;
  * the target inputs are read only from the historical control, in execute mode;
  * the FC2 components are isolated.

`tests/test_u2_structure_controls.py` → `evidence/u2/U2_CONTROLS_V2.json`. The eight version-1 controls, plus:
* RV1, RV2 and RV3 (the reviewer's blind-spot demonstrations);
* a guard importing a consumer;
* five driver defects: `direct` not through the shim; a forbidden `compose` call; Stage 1 reading target inputs; a
  record interval rewritten; target inputs read from another function.

Every control fires. The genuine sources pass.

**U4 at the freeze.** QC-U2 re-runs both on the frozen tree. The pass above is on the current development drafts, not
yet on frozen bytes.
