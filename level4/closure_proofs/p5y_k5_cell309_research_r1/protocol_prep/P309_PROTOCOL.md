# P309 formal campaign: prospective protocol (CANDIDATE; NOT frozen, NOT authorized, NOT executable)

**Status (2026-09-30).** Route class FREEZE_READY by independent review R2 (`reviews/REVIEW_SRK_R2.md`, phases A–D).
This file is a CANDIDATE protocol. Freezing it is itself a step of the formal campaign and requires the owner's
explicit authorization (P0-1), so the research campaign stops at **READY_TO_FREEZE_PENDING_OWNER_AUTHORIZATION**.

This is prepared by the research campaign `p5y_k5_cell309_research_r1`. A later, separately user-authorized formal
campaign may adopt it, and only after its own start-state verification, incident audit plus independent review,
freeze, qualification, independent qualification review and grant. **Nothing here authorizes any evaluation.** No
exactly-once ref exists. No grant exists.

## 0. Preconditions (user decisions, in this order; none decided)

| id | decision |
|---|---|
| P0-1 | An explicit user instruction authorizing a formal, exactly-once, **closure-only** campaign for cell 309 on route P309 |
| P0-2 | The user acknowledges the disclosed liabilities: overnight incidents 01–03 (and their residues), research-campaign incidents 309R1-01 and 309R1-02, the ledgered necessary reads, and the MEDIUM-HIGH motivation-provenance rating of SRK. It also acknowledges the MEDIUM rating of RLR, whose knockout is known |
| P0-3 | U3: either explicitly CLOSURE_ONLY (default), or a floor extension naming P309, frozen and reviewed **before** any Stage 1 (C2 Condition 1; KG-U3). Absent a decision: CLOSURE_ONLY |
| P0-4 | Permission to create the campaign namespace, branch and exactly-once refs, and a statement of where the execution runs. Cell 308's campaign must be finished or on another machine. Stage 1 is operator-only stdlib; no U1 host is needed |

## 1. Scope (fixed now)

* **Cell set.** {309} only.
  * 305: adopted under r1, not re-adjudicable.
  * 306: OUT (sealed adverse I2; route audit 306-c/d/g).
  * 307: already CLOSED_UNDER_RLR; no re-evaluation.
  * 308: its own live campaign; untouchable.
* **Detector and object.** CUSUM, m = 5, the K5-B direct clause (the adoption-quantity form), consumed through C2's
  frozen consumer path with exactly two substitutions:
  * **S1:** the supply S = (A0 from S_I1; A1 = min(A1_I1, A1_RLR); A2 = min(A2_I1, A2_RLR)), as the 307 S_RLR
    construction (D14 with Lemma G and Dv′);
  * **S2:** the TC-T per-object half width rad_r is replaced by rad_r^SRK (THEOREM_SRK §3 / §9), through
    `srk_adapter.srk_enclosure`, with the exact reproduction gate.
* **Label.** CLOSURE_ONLY (unless P0-3 says otherwise). Never adoption, never floor, never r6, never K5/P5Y status.

## 2. Stage 1a: SRK certificates (operator-only, exact stdlib)

1. **Cell interval.** C = [e0 − ρ, e0 + ρ] from the pinned `cells.json`, CUSUM-filtered first. **Weight block**
   Ew = [⌊e_lo⌋₂₋₁₀, ⌈e_hi⌉₂₋₁₀], outward dyadic.
2. **Check sub-blocks.** Ew split into N_E = 4 equal sub-blocks b₁..b₄.
3. **Certificates.** For each b and each rung d ∈ {8, 10, 12}:
   * `certify_W(whole=True)` on b;
   * then `certify_weight(i, weight_block=Ew)` for i ∈ {1, 2, 3, 4}.
   * The parameters are the pinned constants of THEOREM_SRK §12 (amendment A4) and §11 (A3): μ = 2⁻²⁰, base cover
     step 1/4, ≤ 4 extra levels (≤ 3 for the W ≥ 0 check), KT = 10, rounding 96/24/40 bits, 2⁻¹⁰ hull, N_E = 4.
     The producer files are pinned by the fingerprint of the qualification rerun.
4. **Acceptance.** Only through the pinned gate `srk_gate.gate` (THEOREM_SRK §11, rules G1–G6). A certificate is
   admitted iff all of the following hold:
   * the producer status is CERTIFIED;
   * the pinned **grant-scoped** independent verifier (FC2) returns ACCEPT for exactly its sha256. The verdicts are
     produced in-process by `srk_gate.verdicts_from_verifier`, and the verdict source is that verifier's sha256;
   * its geometry, kernel, weight block (= Ew) and sub-block match.

   **Genuine certificates only.** No mutant battery, and no shifted or widened probe, is run on in-band 309
   certificates (review R2 FC2 extension, from incident 309R1-03). Negative-control power is established only on
   decoys, in qualification.
   * Γ_{i,b} := min over ACCEPTED rungs.
   * Γ̄_i := max_b Γ_{i,b}.
   * If some b has no ACCEPTED rung for index i, then Γ̄_i := None (+∞), and the corresponding min falls back to the
     TC-T term. This is not a failure and never triggers a retry.
5. **SRK-T.** **OUT of package 1** (rule S C5; registry/PHASE3_ROUTE_COMPARISON.md, recorded before any taboo
   rerun output). It is not computed. A later package could add it only by a new freeze before any 309 number.
6. **Determinism.** Every Stage-1a output is a pure function of pinned bytes. The rehearsal on decoys shows
   byte-identical reruns.

## 3. Stage 1b: RLR certificates

These are the RLR307 Stage-1 rules verbatim (partition by the frozen C2 rule, degrees 4/6/8, D14 composition, 2⁻²⁰
hull). They are applied to cell 309's blocks and give A1_RLR and A2_RLR (cell max over blocks, ladder min).
Certifier: the pinned C1B_R2 bytes.

## 4. Stage 2: the single sealed evaluation

1. Load the frozen inputs through the pinned loader: `TCT_INPUTS_309`, `ADOPTED_TAIL_INPUTS`, REGISTRY_C1/C2, the K1
   record manifest, `cells.json`.
2. Compute S (§1 S1).
3. Call the pinned `tct_rule.tail_enclosure(R, meas, aux, S, 5)` → (lo, hi, obj).
4. Call `srk_adapter.srk_enclosure(meas, S, 5, C, gate_result, obj, (lo, hi), pinned tc_rule.coefficients,
   verifier_id=<sha256 of the pinned grant-scoped verifier>)` → 𝓗_SRK. Here C is the exact rational cell from the
   pinned `cells.json`. The adapter refuses on any of the following:
   * a reproduction mismatch;
   * a gate result for another cell, geometry, kernel or verifier;
   * a source other than GATE or EMPTY;
   * a rho/cell mismatch;
   * a float cell.
5. Run the pinned C2 direct clause (`c2_d5_forecast.direct` / `combine`, reused as in 307's single-cell driver) with
   𝓗_SRK in place of the TC-T enclosure: M = min(M_R2, mag(H ∩ 𝓗_SRK)) (refuse if empty), Γ = g_hi + ρ·x_hi·M.
   Exact rational.
6. **Pass criterion.** Γ < 0, strict. Γ = 0 or an incomplete evaluation is NOT pass.

**Historical control (post-grant, pre-marker; equality only; not a new evaluation).** With Γ̄ ≡ None and S = S_I1,
the same pipeline must reproduce C2's committed Γ_exact for cell 309, **byte-identical**. On any mismatch:
CONTROL_FAILED, the target is not consumed, STOP.

## 5. Outcome table (frozen §8 analogue; applied verbatim by the adjudication)

| sealed status | conclusion |
|---|---|
| TARGET_EVALUATED; Stage 1a/1b per rules; independent checks equal; Γ < 0 exact | **CELL309_CLOSED_UNDER_P309** (scientific closure only) |
| TARGET_EVALUATED; Γ ≥ 0 (including Γ = 0) | NOT_CLOSED |
| TARGET_EVALUATED; Stage-1b CERTIFICATION_FAILED | NOT_CLOSED (reason recorded; no retry) |
| any post-marker failure | EXECUTION_INDETERMINATE (target consumed; no rerun) |
| CONTROL_FAILED | no conclusion; not consumed; STOP |

Stage-1a certificates that are not accepted are not a failure: the min falls back to TC-T by construction.
Strictness, rounding, tolerance, margin and adoption semantics never change after the freeze.

## 6. Quarantine and ledgers (inherited, stricter-only)

* The research campaign's `TARGET_QUARANTINE_309.json` stays in force until the grant.
* No Γ309, no band quantity and no proxy before the grant.
* Decoys are declared and lie outside the band. The real kernel is used only at e ≤ 33/32 for new decoys.
* Ledger classes follow 307: START_STATE_READ, HISTORICAL_READ, NONTARGET_DECOY, SYNTHETIC, GOVERNANCE, DISCLOSURE;
  TARGET_EXECUTION is appended after the seal.

## 7. Band handling at 309 (review R2 FC2, mandatory before the Stage-1 driver is frozen)

As qualified, both the producer-side `q309_guard` and the independent verifier's quarantine refusal refuse every drift
in the band. Stage 1a at 309 therefore needs all of the following:
* **(a)** A grant-scoped guard. It admits band drifts only inside the granted hull Ew, only when
  marker = grant = HEAD and all pins verify. It refuses otherwise.
* **(b)** A grant-scoped verifier variant, written by the verifier's author and not by the producer side. It is a new
  identity, whose sha256 becomes `verifier_id`. It must be re-qualified on the full decoy battery before the freeze:
  genuine ACCEPT; every v2 mutant expectation; the self-tests; and a grant-scoped counterpart of the 7q probe (refusal
  without a valid grant, and refusal outside Ew). All re-qualification executions are ledgered.
* **(c)** Probe construction guarded by a band check that does **not** depend on any lifted band list.
* **(d)** A grant that names Ew, not only C.

Without (a)–(d), SRK falls back to TC-T. That is safe, but the single evaluation would then be spent without the SRK
channel.
