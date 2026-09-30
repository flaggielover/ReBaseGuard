# P309 formal campaign: independent review briefs (CANDIDATE; issued only inside an authorized campaign)

The four reviews are issued in this order: incident independence, then qualification, then execution, then
adjudication. Each reviewer is independent and has not been a producer or coordinator of this campaign. Each review
is preserved verbatim. **REJECTED ⇒ STOP**, with no same-round repair.

## Common firewall (all four briefs)

* **Forbidden before the grant:**
  * any file that may carry numbers for CUSUM m = 5 cells 305–309, other than those a brief explicitly allows;
  * running anything on the real kernel (h = 5, k = 1/2) at drifts in [6/5, 13/5] or its mirror;
  * any evaluation for cells 305–309;
  * git writes;
  * modifying anything other than the review file.
* **Always excluded** (R1 G6): `p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md` lines 12 and 39. These carry the tail
  drift domain and atom-constant ranges for cells 305–309.
* **The cell-307 and cell-308 campaigns' own files** are forbidden, except the sanitized
  `dossier/sources/READER_B_GOVERNANCE_REPORT.md`.
* **Exposure:** if a number for cells 305–309 is seen anyway, disclose its class, not its value.
* **Executions:** every reviewer execution is ledgered (reviewer scratch ledger, transcribed by the coordinator).
* **Declaration:** every run beyond read-only checks and the pinned tests is declared in the review file before it
  runs.

## 1. Incident-independence review (before the freeze)

* **Allowed reading:**
  * the research namespace, including `ledger/EXPOSURE_LEDGER.jsonl` and `ledger/INCIDENT_*`, which this review must
    read;
  * the overnight-research incident files and their audit;
  * `reviews/`;
  * `ERRATA.md`;
  * the coordinator's audit and addendum.
* **Tasks:**
  1. For each incident: overnight 01–03 and residues; 309R1-01, 309R1-02, 309R1-03; E-3; E-17(a) (unrecorded
     pre-commit verifier self-test runs); the manifest-generator runs hashing two other campaigns' governance files (from 2026-09-29 23:11Z, before R2's final
     verdict; R3 N13/D1); and 309R1-04 (Phase-4 drafting in the uncommitted scratchpad from 2026-09-29 14:11Z, before
     any FREEZE_READY). Decide whether P309's design, parameters and route choice are temporally and parametrically independent
     of the exposed information.
  2. Rate result-chasing (the reviewer decides; the coordinator's MEDIUM-HIGH rating for SRK is an input, not a
     bound).
  3. Assess, explicitly, the target independence of the three rule choices made in candidate rev. 2 (R3 F2.8):
     * the Stage-1a failure mapping (protocol §2.5);
     * the 48 CPU-h budget and its mechanics;
     * the Stage-1b fallback to S_I1 (protocol §3).

     P0-2 records that RLR's knockout is known, and the Stage-1b fallback favours closure when Stage 1b fails.
  4. Check that every firewalled-reader brief is hashed or committed.
* **Verdict tokens:** `INCIDENT_AUDIT_ACCEPTED` (with conditions C…) or `INCIDENT_AUDIT_REJECTED`. The expected
  standard of wording is "temporal and parametric independence only".

## 2. Qualification review (after qualification, before the grant)

* **Allowed reading:** the frozen package, the qualification outputs, the pinned code, `reviews/`, and the research
  evidence.
* **Allowed running:** every QC test on decoys. The **QC16 sandbox positive-path test** uses a substituted test band
  and hull and never the real band.
* **Checklist** (each item PASS/FAIL with evidence):
  1. The freeze commit contains exactly the frozen files. Pins verify (blob and sha256), including the interpreter
     and platform string.
  2. The frozen protocol is byte-identical to the candidate reviewed by R3, apart from the documented freeze fields.
  3. QC01–QC17 all ran after the freeze, on the frozen code, with non-target inputs only (ledger check).
  4. Every gate Q01–Q17 passed; none was waived.
  5. The verifier variant: its independence (the authorship evidence of protocol §7(b)); that it was written and
     hashed before the freeze; that it re-qualified on the full decoy battery (genuine ACCEPT, the v2 mutant
     expectations, the 21 self-tests); the grant-scoped 7q refusals; and the sandbox positive path.
  6. The mutants are genuine: single defect and reason-specific. No control is vacuous (every negative control is
     refuted, not merely unproven, where the spec requires it).
  7. The per-rung serializer produces one certificate per certified rung, and the gate takes the min over admitted
     rungs (QC08).
  8. Determinism: byte identity cross-run and on the execution host (QC10).
  9. The adapter reproduction is against the **pinned** `tct_rule` (QC05). The S construction matches an independent
     recomputation (QC17).
  10. The exactly-once sandbox covers every failure mapping of protocol §2.5, §3 and §5 (QC11).
  11. The static AST check of the driver passes, including the FC4 forbidden constructs (QC12).
  12. The historical control is in the driver and runs pre-marker. `rehearse --cell 305` equality holds (QC14).
  13. Budgets are declared: Stage 1a 48 CPU-h, Stage 1b 21 600 s, ≤ 4 workers.
  14. The quarantine is intact: self-audit A1–A10 and the verifier-probe envelope (QC15).
  15. Temporal order: freeze → qualification → review, with r5 unchanged and no r6 (QC13).
  16. No qualification artifact touches the target or the real band. QC16 uses only a substituted test band and hull, or a synthetic geometry.
  17. The outcome table and grant schema are for CLOSURE_ONLY, consistent with the owner's U3 decision.
* **Verdict tokens:** `QUALIFICATION_ACCEPTED` (with conditions G… and notes E…) or `QUALIFICATION_REJECTED`.

## 3. Execution review (after the seal)

* **Allowed reading:** the sealed result, the post-execution checks, the frozen package, the pinned inputs and code,
  and the ledgers.
* **Allowed running:** re-verification of the **sealed Stage-1a certificates only**, with the verifier in review mode
  (formal package §F). **Genuine certificates only: no mutant battery, and no shifted or widened probe, on any in-band
  certificate** (protocol §2.4; incident 309R1-03). Recomputation of Γ from the sealed components in exact Fractions,
  with no new target evaluation beyond that recomputation.
* **Checks:**
  1. The frozen commit.
  2. The grant chain.
  3. The inputs equal the pins.
  4. Exactly-once, with the marker naming the grant.
  5. No duplicate execution.
  6. The recording is from memory, and the sealed bytes equal the pending ref.
  7. Exact arithmetic.
  8. Reconstruction without recomputation: re-derive rad^SRK, 𝓗_SRK, M and Γ from the sealed certificates, verdicts,
     GateResult report and pinned inputs.
  9. The historical-control digest.
  10. Closure-only scope, and the non-re-attribution statement.
  11. A mechanical outcome by protocol §5, including every fallback and failure mapping.
* **Verdict tokens:** `EXECUTION_REVIEW_ACCEPTED` or `EXECUTION_REVIEW_REJECTED`.

## 4. Adjudication review (after adjudication)

* **Allowed reading:** the adjudication, the sealed result, the frozen protocol §5, and the execution review.
* **Checks:**
  1. The frozen §5 table is applied verbatim to the correct sealed blob.
  2. The sign of Γ is recomputed exactly.
  3. No rule has changed since the freeze.
  4. The closure/adoption distinction holds.
  5. r5 is unchanged, and there is no r6.
  6. The other cells are untouched.
  7. The label is one of CELL309_CLOSED_UNDER_P309, NOT_CLOSED or EXECUTION_INDETERMINATE.
* **Verdict tokens:** `ADJUDICATION_ACCEPTED` or `ADJUDICATION_REJECTED`.
