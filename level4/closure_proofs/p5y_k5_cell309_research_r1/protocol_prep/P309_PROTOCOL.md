# P309 formal campaign: prospective protocol (CANDIDATE rev. 2; NOT frozen, NOT authorized, NOT executable)

**Status (2026-09-30).** The route class is FREEZE_READY, by independent review R2 (`reviews/REVIEW_SRK_R2.md`,
phases A–D). This file is a candidate protocol. Rev. 2 settles independent package review R3's notes N1–N4, N9, N10,
N12, N15–N17 and N19 (`reviews/REVIEW_P309_PACKAGE_R3.md`). Freezing the protocol is itself a step of the formal
campaign and requires the owner's explicit authorization (P0-1). The research campaign therefore stops at
**READY_TO_FREEZE_PENDING_OWNER_AUTHORIZATION**. **Nothing here authorizes any evaluation.** No exactly-once ref
exists and no grant exists.

A later formal campaign, separately authorized by the user, may adopt this protocol. It may do so only after its own
start-state verification, an incident audit with independent review, the freeze, qualification, an independent
qualification review, and a separate grant.

## 0. Preconditions (owner decisions, in this order; none taken)

| id | decision |
|---|---|
| P0-1 | An explicit owner instruction authorizing a formal, exactly-once, **closure-only** campaign for cell 309 on route P309, including new in-band Stage-1 computation over the drift hull Ew |
| P0-2 | The owner acknowledges the disclosed liabilities: overnight incidents 01–03 and their residues; research-campaign incidents 309R1-01, 309R1-02 and 309R1-03; the unverifiable ordering of the early real-kernel probe (ERRATA E-3); the unrecorded pre-commit verifier self-test runs (ERRATA E-17(a)); the ledgered necessary reads; the MEDIUM-HIGH motivation-provenance rating of SRK; and the MEDIUM rating of RLR, whose knockout is known |
| P0-3 | U3: either explicitly CLOSURE_ONLY (the default), or a floor extension naming P309, frozen and reviewed **before** any Stage 1 (C2 Condition 1; KG-U3). **The outcome table (§5) and the grant schema are written for CLOSURE_ONLY.** A U3 extension would require revising them before the freeze. With no decision: CLOSURE_ONLY |
| P0-4 | Permission to create the campaign namespace, branch and exactly-once refs, and a statement of the execution host. Cell 308's campaign must be finished or run on another machine. Stage 1 is operator-only stdlib, so no U1 host is needed. QC10 determinism is re-run on the named host |

## 1. Scope (fixed now)

* **Cell set.** {309} only.
  * 305: adopted under r1, not re-adjudicable.
  * 306: OUT (sealed adverse I2).
  * 307: already CLOSED_UNDER_RLR, no re-evaluation.
  * 308: its own campaign, untouchable.
* **Detector and object.** CUSUM, m = 5, the K5-B direct clause, consumed through C2's frozen consumer path with
  exactly two substitutions:
  * **S1.** The supply S = (A0 from S_I1; A1 = min(A1_I1, A1_RLR); A2 = min(A2_I1, A2_RLR)).
  * **S2.** The TC-T per-object half width rad_r is replaced by rad_r^SRK (THEOREM_SRK §3, §11, §12), through
    `srk_adapter.srk_enclosure`, with the exact reproduction gate.
* **Label.** CLOSURE_ONLY: never adoption, never a floor change, never r6, never a K5/P5Y status change.
* **Non-re-attribution (incident-02 lesson).** Everything computed for 309 in Stage 1a/1b is bound to cell 309. The
  gate and the adapter already enforce this binding by cell. Nothing computed for 309 is ever used for, or
  re-attributed to, another cell. The hull Ew may overlap a neighbouring quarantined cell's drift range, and that
  overlap confers no licence to reuse.

## 2. Stage 1a: SRK certificates (operator-only, exact stdlib)

1. **Cell and hull.** C = [e0 − ρ, e0 + ρ], from the pinned `cells.json` after filtering to CUSUM. The weight block Ew
   and the check sub-blocks b₁..b₄ come from `srk_certify.cell_blocks(C)`: the outward 2⁻¹⁰ dyadic hull split into
   N_E = 4 equal parts (THEOREM_SRK §11).
2. **Certificates.** For each b_j (via `srk_certify.run_block` with weight_block = Ew, as `run_cell` does), each rung
   d ∈ {8, 10, 12} and each index i ∈ {1, 2, 3, 4}, with the pinned constants of THEOREM_SRK §12:
   * `certify_W` on b_j (whole kernel);
   * `certify_weight(i, weight_block = Ew)`.
3. **Serialization (R3 N1).** Every rung of every (b_j, i) that the producer returns as CERTIFIED is serialized as its
   **own** certificate: the pinned per-rung serializer calls `srk_certify.certificate_json` on a block record holding
   that single rung. The best-rung-only form must not be used in Stage 1a. The serializer is pinned and is exercised
   in QC08 and QC10.
4. **Admission.** Admission goes only through the pinned gate `srk_gate.gate` (THEOREM_SRK §11, rules G1–G6). A
   certificate is admitted iff:
   * the producer status is CERTIFIED;
   * the pinned **grant-scoped** independent verifier (§7(b)) returns ACCEPT for exactly its sha256. Verdicts are
     produced in-process by `srk_gate.verdicts_from_verifier`, with the pinned N = 8 and max_depth = 24; the verdict
     source is that verifier's sha256;
   * its geometry, kernel, weight block (= Ew) and sub-block all match.

   Then:
   * Γ_{i,b} := min over admitted rungs;
   * Γ̄_i := max_b Γ_{i,b};
   * Γ̄_i := None (+∞) if some b has no admitted rung for i.

   **Genuine certificates only.** No mutant battery, and no shifted or widened probe, is run on in-band 309
   certificates (R2 FC2 extension, from incident 309R1-03).
5. **Failure mapping (R3 N2; fixed now).**

   | event in Stage 1a | effect |
   |---|---|
   | a producer status other than CERTIFIED (W_REPAIR_INAPPLICABLE, W_NEGATIVE) for a (b, rung) | no certificate for that (b, rung): **fallback**, no retry |
   | a verifier verdict other than ACCEPT (REJECT or REFUSE) for a certificate | not admitted: **fallback** for that (b, i, rung) |
   | jobs not started, or stopped by the budget mechanics below (**48 CPU-h total**; workers ≤ 4) | no certificate for those jobs: **fallback** for the affected indices. The budget is a pre-declared resource limit, not a malfunction. It is set at about 10× the qualified real-kernel decoy cell (about 4.5 CPU-h), a target-free basis |
   | **any exception**: producer, guard refusal, verifier, gate or driver | **post-marker failure → EXECUTION_INDETERMINATE** (target consumed; no rerun; no conclusion) |

   Here "fallback" means Γ̄_i = None for the affected index, and the min takes the TC-T term. Stage 2 still runs. The
   fallback is safe for validity, but it spends the single evaluation without that SRK index. Whether exceptions
   should instead fall back is an owner rule decision, to be taken before the freeze (P309_OWNER_DECISIONS).

   **Budget mechanics (R3 F2.2; fixed now).**
   * **Accounting.** CPU-h is the sum over worker processes of process CPU time (user + system), including in-process
     verification.
   * **Job.** One job is one (sub-block b_j, rung d) unit: `certify_W`, the four `certify_weight` calls, per-rung
     serialization and the in-process verification of those certificates.
   * **Fixed order.** Rung-major: every sub-block at d = 8, then every one at d = 10, then d = 12, with b₁..b₄ in
     order within each rung. A binding budget therefore removes the most expensive rungs first, and every sub-block
     gets its cheapest rung before any sub-block gets a costlier one.
   * **Stopping.** No job starts once the cumulative CPU reaches 48 CPU-h. A job that exceeds a per-job limit of
     12 CPU-h is terminated and its outputs are discarded. Stopping is only by not starting jobs and by discarding a
     terminated job's outputs; neither raises an exception.
   * **Host dependence (R3 F2.1).** When the budget binds, which certificates exist depends on timing, so the outcome
     can depend on the host's speed. The budget use and the list of started, finished and terminated jobs are
     recorded. Validity is unaffected, because missing certificates only fall back.
6. **Recording.** **All** serialized certificates, all verdicts (with reasons) and the full GateResult report
   (admitted and refused, with reasons) are sealed, not only the admitted ones.
7. **SRK-T.** SRK-T is **OUT of package 1** (rule S, C5). It is not computed.
8. **Determinism.** While the budget does not bind, every Stage-1a output is a pure function of the pinned bytes and
   the pinned interpreter/platform. When it binds, see the host-dependence caveat in §2.5.
   The research campaign showed byte-identical certificate reproduction for one decoy certificate (test T10). The
   formal campaign must show Stage-1a determinism in QC10, including a re-run on the execution host.

## 3. Stage 1b: RLR certificates

* **Rules.** The RLR307 Stage-1 rules verbatim: partition by the frozen C2 rule, degrees 4/6/8, D14 composition, and
  the 2⁻²⁰ hull. Applied to cell 309's blocks they give A1_RLR and A2_RLR (cell max over blocks, ladder min). The
  certifier is the pinned C1B_R2 bytes, with the RLR307 independent reconstruction.
* **Failure mapping (R3 N12; fixed now; flagged to the owner under G3).** RLR is a **min-composed** component of P309.
  Unlike 307, where RLR was the whole route, a Stage-1b CERTIFICATION_FAILED for a block therefore gives A1_RLR,
  A2_RLR := None (+∞) for the cell. The min then takes the S_I1 values, which is valid, and Stage 2 still runs.
* **Budget (R3 F2.3).** 21 600 s CPU, accounted as in §2.5 with jobs in the RLR307 order. Blocks not certified within
  the budget are CERTIFICATION_FAILED and fall back to the S_I1 values, as above. The stop is by not starting and by
  discarding, never by raising.
* **Exceptions.** Any exception in Stage 1b, or a mismatch between the producer and the independent reconstruction,
  is a post-marker failure and gives EXECUTION_INDETERMINATE.

## 4. Stage 2: the single sealed evaluation

1. Load the frozen inputs through the pinned loader: `TCT_INPUTS_309`, `ADOPTED_TAIL_INPUTS`, REGISTRY_C1/C2, the K1
   record manifest, and `cells.json`.
2. Compute S (§1 S1).
3. Call the pinned `tct_rule.tail_enclosure(R, meas, aux, S, 5)` → (lo, hi, obj).
4. Call `srk_adapter.srk_enclosure(meas, S, 5, C, gate_result, obj, (lo, hi), pinned tc_rule.coefficients,
   verifier_id = <sha256 of the pinned grant-scoped verifier>)` → 𝓗_SRK. Here C is the exact rational cell from the
   pinned `cells.json`. The adapter refuses on any of:
   * a reproduction mismatch;
   * a gate result for another cell, geometry, kernel or verifier;
   * a source other than GATE or EMPTY;
   * a rho/cell mismatch;
   * a float cell.

   An adapter refusal is an exception (§2.5), so it gives EXECUTION_INDETERMINATE.
5. Evaluate the pinned C2 direct clause **exactly as the pinned `c2_d5_forecast.direct` / `combine` compute it**, with
   𝓗_SRK substituted for the TC-T enclosure (reused as in the 307 single-cell driver). Γ is an exact rational.
6. **Pass criterion.** Γ < 0, exact and strict. Γ = 0, or an incomplete evaluation, is NOT a pass.

**Historical control** (post-grant, pre-marker; equality only; not a new evaluation). With Γ̄ ≡ None, S = S_I1 and
the EMPTY GateResult, the same pipeline must reproduce C2's committed Γ_exact for cell 309 **byte-identically**. On
any mismatch: CONTROL_FAILED, the target is not consumed, STOP. The control's digest is sealed with the result and
checked after execution (R3 N10).

## 5. Outcome table (applied verbatim by the adjudication; written for CLOSURE_ONLY)

The **in-run independent checks** (R3 N3) are:
* (i) Stage 1a: admission only via in-process verdicts of the pinned grant-scoped verifier (§2.4);
* (ii) Stage 1b: the RLR307 independent reconstruction equals the producer supplies (§3).

A mismatch in (ii) is a post-marker failure.

| sealed status | conclusion |
|---|---|
| TARGET_EVALUATED; Stage 1a and 1b per §§2–3, including any fallbacks; in-run independent checks passed; Γ < 0 exact | **CELL309_CLOSED_UNDER_P309** (scientific closure only) |
| TARGET_EVALUATED; Γ ≥ 0 (including Γ = 0) | NOT_CLOSED |
| any post-marker failure (exception, check mismatch, adapter refusal, lost information) | EXECUTION_INDETERMINATE (target consumed; no rerun; no conclusion) |
| post-seal: independent re-verification disagrees with the sealed admission of any Stage-1a certificate, or the historical-control digest is missing or unequal (§6 of the formal package) | EXECUTION_INDETERMINATE (the sealed closure is not confirmed; target consumed; no rerun) |
| CONTROL_FAILED | no conclusion; not consumed; STOP |

Fallbacks under §2.5 and §3 are not failures. Strictness, rounding, tolerance, margin, budget and adoption semantics
never change after the freeze.

## 6. Quarantine and ledgers (inherited; stricter only)

* The research campaign's `TARGET_QUARANTINE_309.json` stays in force until the grant.
* Before the grant there is no Γ309, no band quantity and no proxy.
* Decoys are declared and lie outside the band. The declared real-kernel decoy blocks lie at e ≤ 33/32. Verifier
  probes built from them reach at most 37/32 (and −1/3), and are ledgered (ERRATA E-17).
* Ledger classes follow 307: START_STATE_READ, HISTORICAL_READ, NONTARGET_DECOY, SYNTHETIC, GOVERNANCE and DISCLOSURE.
  TARGET_EXECUTION is appended after the seal. **Every execution is ledgered, including the verifier's.**

## 7. Band handling at 309 (R2 FC2; one lettering, used in both documents)

As qualified, the producer-side `q309_guard` and the independent verifier's quarantine refusal both refuse every
drift in the band. Stage 1a at 309 therefore needs:

* **(a) A grant-scoped guard.** It admits band drifts only inside the granted hull Ew, and only when
  marker = grant = HEAD and all pins verify. It refuses otherwise.
* **(b) A grant-scoped verifier variant.**
  * **Authorship.** It is written by the verifier's author (an agent or session separate from the producer side)
    from the spec.
  * **Order (R3 N4).** It is written and hashed **before the freeze**, and pinned by the freeze. Its sha256 is
    `verifier_id`.
  * **Re-qualification (QC16, before the grant) covers:**
    * genuine ACCEPT on the full decoy suite;
    * every v2 mutant expectation;
    * the 21 self-tests;
    * a grant-scoped counterpart of the 7q probe, which must refuse without a valid grant and refuse outside Ew;
    * a **sandbox positive-path test** of the admission logic. It uses a synthetic geometry, or a substituted test
      band and test hull, never the real band, and shows admission inside the hull under a valid test grant.
  * Every re-qualification execution is ledgered.
  * **Evidence of authorship (R3 N18).** Git cannot show who wrote the variant, so the evidence is:
    * the author session's identifier and its declaration of sources read;
    * a statement that no producer code was consulted;
    * the qualification review's assessment of independence.

    "Independent" is a procedural claim, for that review to assess.
* **(c) A probe-construction guard.** Any probe construction (in qualification only) is guarded by a band check that
  depends on **no** lifted band list: not the verifier's and not the grant-scoped guard's. In-band certificates are
  never probed (§2.4).
* **(d) The grant names Ew,** not only C, and states that Ew may overlap a neighbouring cell's drift range (§1).

Without (a)–(d) in place, every Stage-1a certificate at 309 would be refused. By §2.5 that is either a fallback
(REFUSE verdicts) or an exception (a guard refusal leads to EXECUTION_INDETERMINATE). So (a)–(d) are mandatory before
the grant.
