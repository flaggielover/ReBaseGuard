# P309 formal-campaign package DRAFT: qualification, exactly-once mechanics, reviews, adjudication

Not frozen, not authorized. This mirrors the accepted p5y_k5_cell307_rlr_r1 anatomy
(`dossier/sources/READER_B_GOVERNANCE_REPORT.md` §3), adapted to P309.

## A. Frozen parameter specification (to be serialized as `protocol/P309_FREEZE.json` at the future freeze)

| key | value |
|---|---|
| cell | 309 (CUSUM, m = 5; `cells.json` filtered detector == CUSUM FIRST) |
| route | P309 = direct clause, S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)), order-0 channel = SRK min construction |
| scope | CLOSURE_ONLY (unless a prior frozen U3 extension exists) |
| SRK weight block | outward dyadic hull of C on the 2⁻¹⁰ grid |
| SRK check sub-blocks | N_E = 4 equal |
| SRK ladder | d ∈ {8, 10, 12}; indices {1, 2, 3, 4}; whole kernel only (SRK-T OUT of package 1, rule S C5) |
| SRK numerics | THEOREM_SRK §12 (A4) verbatim: μ = 2⁻²⁰, base cover 1/4, extra levels 4 (tightness rule; 3 for the W ≥ 0 check), KT = 10, float proposals at dyadic 2⁻⁹⁶, λ dyadic 2⁻⁴⁰, η dyadic 2⁻²⁴, root brackets 2⁻⁴⁰ |
| SRK acceptance | only through `srk_gate.gate` (G1–G6): producer CERTIFIED ∧ independent verifier ACCEPT for that sha256 ∧ geometry/kernel/weight block/sub-block match; the adapter accepts only a GateResult |
| RLR | RLR307 Stage-1 rules verbatim (C1B_R2 pins) |
| pins | sha256 + blob of: `srk_kernel.py`, `srk_float.py`, `srk_envelope.py`, `srk_certify.py`, `srk_assemble.py`, `srk_adapter.py`, `srk_gate.py`, `srk_decoy_suite.py`, `code/q309_guard.py` (or its grant-scoped successor), `verify/srk_verify_indep.py` (its sha256 is the adapter's `verifier_id`), the decoy declarations (`config/SRK_DECOY_DECLARATION*.json`), the Python version (`sys.version`), the pinned `c1b_gauss.py`, RLR certifier set (C1B_R2_CODE_PINS), `tct_rule.py` 98f6eee4, `tc_rule.py` (pin 8d402d11), `c2_d5_forecast.py` 18403dbe, `deflated_consume.py` a0a836fa, `tail_forecast_r2.py` edec817e (pin it, floor-r2 review N5), `TCT_INPUTS_309`, `ADOPTED_TAIL_INPUTS`, REGISTRY_C1, REGISTRY_C2, the K1 record manifest, `cells.json`, r5 f978eeb6, floor r2 |
| exactly-once names | marker `refs/p5y-k5-cell309-p309-r1/target-consumed`; pending `refs/p5y-k5-cell309-p309-r1/pending-result`; emergency `<gitdir>/p309-cell309-emergency-result.json`. Refuse if any prior marker namespace of 307/308/309 designs exists for 309 |
| caps | Stage 1a ≤ 6 CPU-h; Stage 1b ≤ 21 600 s (307 precedent); workers ≤ 4 |

## B. Qualification suite (all non-target; frozen before any run; no 305–309 new quantity; the band is forbidden)

| QC | test |
|---|---|
| QC01 | SRK port identity versus pinned C1b (G-forms and box enclosures) |
| QC02 | Envelope sandwich (rigorous lower ≤ float ≤ rigorous upper) plus the point-sampled containment control (4 wrong-corner mutants caught; the old planted shrink was vacuous, ERRATA E-6) |
| QC03 | Exact-truth FSM, 12 declared seeds: radius truth, pointwise premises, premise-level truth of Γ̄ and B3/B4, dominance; mutants M1 (Γ/2) 12/12, M4 on every applicable case, M5 (centre drift only) ≥ 1 |
| QC04 | Two-sided assembly versus an independent recomputation, with 10 textual mutants caught and malformed inputs refused |
| QC05 | Adapter: stub reproduction (manufactured), **plus** equality of the adapter's re-assembly with the **pinned** `tct_rule.tail_enclosure` on manufactured TC-T-shaped inputs (non-target), plus the refusals (tamper, Ĝ ≠ 0, wrong coefficients) |
| QC06 | Declared SRK decoy suite (real kernel e ≤ 33/32; synthetic h ∈ {3, 4}): all certificates independently verified; required rejections 1–7 (SRK_CERT_SPEC §5) |
| QC07 | Monte Carlo positive control on every QC06 certificate (5-σ) |
| QC08 | Decoy full Stage 1a on declared non-target cells outside the band (the A2 pattern: non-dyadic endpoints, hull weight block, 4 sub-blocks), through the driver's `decoy-stage1a`, verifier, gate and gate negatives on real certificates, plus the cell-level MC control |
| QC08b | Gate battery (`tests/test_srk_gate.py`), W-record refusals (`test_srk_wrec_refusal.py`) and the certificate battery T1/T2/T8/T10 (`test_srk_cert_mutants.py`) |
| QC09 | RLR Stage-1 decoy per RLR307 QC02/QC05/QC09, reused |
| QC10 | Determinism: serial and cross-run byte identity of Stage 1a on QC08 |
| QC11 | Exactly-once sandbox flows (the 307 QC10 pattern: ≥ 39 flows in a `git clone --shared` sandbox with stubs) |
| QC12 | Static structure: AST of the driver, with no path from qualification modes to the target. Leak scan against the committed target-cell tokens |
| QC13 | Temporal and governance state: freeze → qualification → review → grant ordering; r5 unchanged; no r6 |
| QC14 | `rehearse --cell 305`: historical reproduction of C2's committed 305 record with SRK disabled and S = S_I1, equality only |

Gates Q1–Q13 follow the 307 pattern. None may be waived. The verifier has an official mode and a review mode.

## C. Exactly-once driver design (`code/p309_driver.py`)

**Modes.**
* `preflight`: read-only.
* `rehearse --cell 305`.
* `decoy-stage1a --cell <declared>`.
* `decoy-stage1b --cell <declared>`.
* `execute`: qualified worktree plus the grant commit only.
* `seal-only`: never computes.

**Exit codes (307 set).**
* 0 sealed;
* 2 refused pre-marker;
* 3 CONTROL_FAILED (not consumed);
* 4 UNSEALED;
* 5 sealed failure status;
* 6 CONSUMED_UNRECORDED;
* 7 sealed but not materialized.

**`execute`, in order:**
1. `check_grant`: the chain HEAD^^^ = freeze → qualification → review → grant, each commit touching only its own
   files.
2. Verify all pins.
3. Refuse if any guarded path exists (lstat), or if the namespace is unclean, including ignored files.
4. Run the historical control (§4 of the protocol) → CONTROL_FAILED ⇒ exit 3.
5. Arm the marker by CAS from the zero OID → grant.
6. Ignore signals from here on.
7. Stage 1a.
8. Stage 1b.
9. Stage 2.
10. Serialize the result in memory; `hash-object -w`; set the pending ref by CAS (emergency O_EXCL file as a second
    channel); commit with a private index and `--cacheinfo`; materialize O_EXCL|O_NOFOLLOW; read back.

**Guard.** Workers re-verify pins and arm the band guard only when marker = grant = HEAD.

## D. Grant schema (`authorization/P309_GRANT.json`, committed alone as the child of the qualification review)

`schema`, `cell`, `detector`, `m`, `route`, `closure_only` (true), `closure_criterion` ("Γ < 0 exact, strict"),
`adoption` (NOT AUTHORIZED), `floor_change` (NOT AUTHORIZED), `r6` (NOT AUTHORIZED), `k5_or_p5y_closure`
(NOT AUTHORIZED), `freeze_commit`, `freeze_tree`, `qualification_commit`, `qualification_review_commit`,
`input_manifest_path`, `input_manifest_sha256`, `driver_path`, `driver_sha256`, `evaluator`,
`executions_authorized` (1), `exactly_once` (names), `consumed_marker`, `outcome_table`, `disclosed_liabilities`
(01–03, 309R1-01, 309R1-02, reads), `incident_review_conditions_verbatim`,
`qualification_review_conditions_verbatim`, `qualification_review_notes_verbatim`, `issued_utc`, `granted_after`,
`authority` (the user instruction, verbatim reference).

## E. Seal-from-memory

As C12-R2 / RLR307. The result bytes are canonical JSON. They contain:
* the Stage-1a certificates (the ACCEPTED ones and their verifier verdicts);
* the Stage-1b rung supplies;
* S, Γ̄, per-r rad^SRK and branch labels, 𝓗_SRK, M, g_hi, Γ as an exact rational string;
* pass;
* the historical-control digest;
* timings.

## F. Post-execution checks (`postexec/`)

* The result blob equals the pending ref, including its self-hash.
* The seal commit changes the result path only, and its parent is the grant.
* The marker names the grant. Exactly one execution.
* A second `execute` is refused before anything. (Resolve the RLR307 E4 tension by running this probe only in the
  sandbox copy, never on the real repository.)
* `seal-only` is read-only.
* The worktree copy equals the sealed bytes.
* r5 is unchanged; no r6.
* No other cell was evaluated.
* An independent re-verification of every sealed Stage-1a certificate (the verifier re-run on the sealed bytes)
  agrees.

## G. Review briefs (to be issued in order; each preserved verbatim; REJECTED ⇒ STOP, no same-round repair)

1. **Incident-independence review.** The coordinator audit and addendum cover overnight 01–03, residues and L-lines
   as they bear on 309, plus 309R1-01/02 and the research campaign's ledgered reads and briefs (hash or commit every
   firewalled-reader brief). The expected standard wording is "temporal and parametric independence only"; the
   result-chasing rating is to be decided by the reviewer.
2. **Qualification review.** The 17-item checklist of the 307 pattern, plus SRK specifics:
   * the verifier is genuinely independent;
   * the mutants are genuine;
   * there are no vacuous controls;
   * the adapter reproduction is against the pinned `tct_rule`.
3. **Execution review.** 11 checks: frozen commit, grant, inputs, exactly-once, marker, no duplicate, seal, exact
   arithmetic, reconstruction without recomputation (re-derive rad^SRK, 𝓗_SRK, M, Γ from the sealed certificates
   and pinned inputs), closure-only scope, mechanical outcome.
4. **Adjudication review.** The frozen §5 criterion is applied verbatim; the correct sealed blob is used; the sign is
   recomputed exactly; no rule changed since the freeze; the closure/adoption distinction holds; r5/r6 and the other
   cells are correct.

## H. Adjudication rule

Apply §5 of the protocol verbatim to the sealed status. Exact-Fraction recomputation of Γ from the sealed components.
Label as CELL309_CLOSED_UNDER_P309 (scientific closure only) or NOT_CLOSED / EXECUTION_INDETERMINATE.

## I. Failure and recovery semantics

* Any REJECTED review ⇒ STOP.
* A consumed marker is never rerun.
* Lost result information ⇒ no recomputation without a new independent governance process.
* STOP conditions:
  * the start state differs;
  * the incident review rejects;
  * the target appears consumed;
  * inputs drift (pin mismatch);
  * qualification touches the target;
  * the exactly-once infrastructure is unsafe;
  * the historical control fails.
* A Stage-1a certificate that fails the verifier is dropped by rule. It is not a failure and not a retry.
* A Stage-1b CERTIFICATION_FAILED ⇒ NOT_CLOSED (reason recorded).

## J. Items from independent review R2 (FC1–FC6), to be completed inside the formal campaign

* **FC1, pin set.** See `P309_CANDIDATE_FREEZE_MANIFEST.json` (code: git blob + sha256; data: blob only until the
  campaign's own freeze).
  * Producer: lock 2a03e838, fingerprint 377057be….
  * c1b_gauss; gate, adapter and assembly at the post-R2-C1 state.
  * The independent verifier file, its settings (Taylor order N = 8, max depth 24, initial cell width 1/4) and its
    harness.
  * THEOREM_SRK, SRK_CERT_SPEC, the decoy declarations, ROUTE_SELECTION_RULE.
  * The Python version used for qualification.
* **FC2, band handling (mandatory, before any freeze of the Stage-1 driver).** As qualified, both the producer-side
  `q309_guard` and the verifier's hard-coded quarantine refusal refuse every drift in [6/5, 13/5]. Stage 1a at 309
  therefore needs all of the following:
  * **(a)** A grant-scoped guard. It admits band drifts only inside the granted hull Ew, and only when
    marker = grant = HEAD, the grant pins the cell, Ew and the driver, and the pins verify. It refuses otherwise.
  * **(b)** A grant-scoped verifier variant, written by the verifier's author and not by the producer side. It is a
    new identity, so its sha256 becomes the adapter's `verifier_id`. It must be re-qualified on the full decoy
    battery (genuine ACCEPT, all mutant expectations, a reason-specific quarantine refusal without a grant) before
    the freeze.
  * **(c)** The grant must name Ew, not only C.

  Without FC2, SRK silently falls back to TC-T. That is safe, but the single evaluation would then be spent without
  the SRK channel.
* **FC3, Stage-1 failure semantics.** A sub-block without an admitted certificate gives Γ̄_i = None (+∞): the min falls
  back to TC-T, with no retry and no parameter change.
* **FC4, Stage-2 driver.**
  * Verdicts are produced in-process by the pinned verifier (`srk_gate.verdicts_from_verifier`), and `verifier_id`
    is computed from the pinned bytes.
  * The cell comes from the pinned `cells.json` (exact rationals).
  * A static (AST) check of the driver forbids `srk_gate._TOKEN`, `object.__setattr__`, any `GateResult(` call and any
    geometry or kernel override.
* **FC5, RLR Stage 1b.** The RLR307 Stage-1 rules verbatim on 309's blocks: the C1B_R2 pins, and the partition by the
  frozen C2 rule.
* **FC6, exactly-once machinery and reviews.** As sections C–I, in the 307 pattern.

## K. Owner decisions required before any freeze (none decided by this research campaign)

| id | decision | blocks |
|---|---|---|
| P0-1 / G2 | authorize a separate, closure-only, exactly-once formal campaign for 309 on P309, including in-band Stage-1 certificates over the hull Ew (FC2) and a grant | the freeze itself |
| G1 | accept the MEDIUM-HIGH motivation-provenance liability of SRK (309R1-01, 309R1-02, programme-wide dominance knowledge, rule S's C4 threshold) | authorization |
| G3 | confirm RLR as the min-composed A1/A2 component (307 disclosures carried) | authorization |
| U2 | rule on U2, or confirm it is not triggered by P309 (no P3-derived quantity is used) | any Stage-1 freeze |
| U3 | CLOSURE_ONLY (default), or a frozen floor extension naming P309, before Stage 1 | any Stage-1 freeze |
| SRK-T | optionally reconsider the C5 exclusion. Only before any 309 Stage-1 number exists, and only with the full taboo family run (ERRATA E-15) plus a D_lo path | optional |
| — | acknowledge that efficacy is unknown by design (decoys stop at 33/32); a TC-T fallback spends the single evaluation | authorization |
