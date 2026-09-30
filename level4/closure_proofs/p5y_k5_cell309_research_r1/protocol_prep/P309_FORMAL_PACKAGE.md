# P309 formal-campaign package (CANDIDATE rev. 2b): qualification, exactly-once mechanics, reviews, adjudication

**Status (2026-09-30).** CANDIDATE. It is not frozen, not authorized and not executed. Route class: FREEZE_READY
(independent review R2). Rev. 2 settles independent package review R3's notes (`reviews/REVIEW_P309_PACKAGE_R3.md`).
Freezing needs the owner's explicit authorization (P0-1; `P309_OWNER_DECISIONS.md`). The anatomy follows the accepted
earlier formal-campaign pattern, as described in the sanitized `dossier/sources/READER_B_GOVERNANCE_REPORT.md` §3,
adapted to P309. `P309_PROTOCOL.md` (rev. 2b) governs wherever the two documents overlap.

## A. Frozen parameter specification (serialized as `protocol/P309_FREEZE.json` at a future, authorized freeze)

| key | value |
|---|---|
| cell | 309 (CUSUM, m = 5; `cells.json` filtered to detector == CUSUM FIRST) |
| route | P309 = the direct clause; S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)); the order-0 channel is the SRK min construction |
| scope | CLOSURE_ONLY. The outcome table and the grant schema are written for it (protocol P0-3) |
| SRK blocks | `srk_certify.cell_blocks`: the outward 2⁻¹⁰ hull Ew, and N_E = 4 equal check sub-blocks |
| SRK ladder | d ∈ {8, 10, 12}; indices {1, 2, 3, 4}; whole kernel only (SRK-T OUT, rule S C5) |
| SRK numerics | THEOREM_SRK §12 (A4) verbatim: μ = 2⁻²⁰; base cover 1/4; 4 extra levels (tightness rule), 3 for the W ≥ 0 check; KT = 10; float proposals at dyadic 2⁻⁹⁶; λ dyadic 2⁻⁴⁰; η dyadic 2⁻²⁴; root brackets 2⁻⁴⁰ |
| SRK serialization | **per rung**: one certificate per producer-CERTIFIED (b, i, rung), made by `certificate_json` on a single-rung block record. Never best-rung-only (protocol §2.3) |
| SRK admission | only through `srk_gate.gate` (G1–G6), with in-process verdicts of the pinned **grant-scoped** verifier at N = 8, max_depth = 24. The adapter accepts only a GateResult bound to C, (5, 1/2), the whole kernel and `verifier_id` |
| Stage-1a failure mapping | protocol §2.5: non-CERTIFIED statuses, non-ACCEPT verdicts and budget exhaustion fall back (Γ̄_i = None); **any exception gives EXECUTION_INDETERMINATE** |
| RLR (Stage 1b) | the RLR307 Stage-1 rules verbatim (C1B_R2 pins), with the independent reconstruction. A CERTIFICATION_FAILED falls back to S_I1 values (protocol §3). An exception or reconstruction mismatch gives EXECUTION_INDETERMINATE |
| pins | **All pins are listed in `P309_CANDIDATE_FREEZE_MANIFEST.json`, each with git blob AND sha256** (this table deliberately lists no prefixes, to avoid mixing notations). The freeze adds, pinned by the freeze commit: the grant-scoped guard and the grant-scoped verifier variant (protocol §7; its sha256 is `verifier_id`); the Stage-1 driver and its per-rung serializer; the interpreter and platform string of the execution host (QC10); the floor r2 record; the K1 record manifest |
| exactly-once names | marker `refs/p5y-k5-cell309-p309-r1/target-consumed`; pending ref `refs/p5y-k5-cell309-p309-r1/pending-result`; emergency file `<gitdir>/p309-cell309-emergency-result.json`. Refuse if any prior marker namespace of 307/308/309 designs exists for 309 |
| budgets | Stage 1a start threshold **48 CPU-h** total (running jobs may finish, up to 12 CPU-h each; target-free basis: about 10× the qualified real-kernel decoy cell of about 4.5 CPU-h), with a per-job limit of 12 CPU-h and rung-major job order. Stage 1b ≤ 21 600 s CPU (307 precedent). Workers ≤ 4. Accounting, stopping and host dependence follow protocol §2.5 and §3. Budget exhaustion is a fallback, not a failure |

## B. Qualification suite (all non-target; frozen before any run; no new quantity for cells 305–309; the real band is never used. QC16's positive-path test uses a substituted test band and hull, or a synthetic geometry)

| QC | test |
|---|---|
| QC01 | SRK port identity versus the pinned C1b (G-forms and box enclosures) |
| QC02 | Envelope sandwich (rigorous lower ≤ float ≤ rigorous upper) plus the point-sampled containment control (4 wrong-corner mutants caught) |
| QC03 | Exact-truth FSM, 12 declared seeds: radius truth, pointwise premises, premise-level truth of Γ̄ and B3/B4, dominance. Mutants: M1 (Γ/2) 12/12; M4 on every applicable case; M5 (centre drift only) ≥ 1 |
| QC04 | Two-sided assembly versus an independent recomputation. 10 textual mutants caught; malformed inputs refused; dominance refusal live under -O |
| QC05 | Adapter. Stub reproduction plus equality of its re-assembly with the **pinned** `tct_rule.tail_enclosure` on manufactured TC-T-shaped inputs (non-target). All binding refusals: other cell, geometry, verifier, source, float cell, rho mismatch, raw dict, hand-built result, geometry override |
| QC06 | Declared SRK decoy suite. The declared real-kernel blocks lie at e ≤ 33/32; synthetic h ∈ {3, 4}. Every certificate is independently verified, with harness-v2 batteries (single-defect mutants, reason-specific expectations). The research qualification gave 1868/1868. Verifier probes built from these blocks reach 37/32 and −1/3 (ERRATA E-17), all outside the band, and are ledgered. Includes the verifier self-tests, 21/21 |
| QC07 | Monte Carlo positive control on every QC06 certificate (5-σ) |
| QC08 | Decoy full Stage 1a through the driver's `decoy-stage1a` on declared non-target cells outside the band. It uses the A2 pattern: non-dyadic endpoints, hull weight block, 4 sub-blocks, **the per-rung serializer**, the in-process verifier, the gate, gate negatives on real certificates, and the cell-level MC control. Includes the gate battery, the W-record refusals and the certificate battery T1/T2/T8/T10 |
| QC09 | RLR Stage-1 decoy per the RLR307 pattern, including the independent reconstruction |
| QC10 | Determinism: serial and cross-run byte identity of Stage 1a on QC08, **including a re-run on the execution host**. The interpreter and platform string are recorded and pinned |
| QC11 | Exactly-once sandbox flows (≥ 39 flows in a `git clone --shared` sandbox with stubs), including every failure mapping of protocol §2.5, §3 and §5 (exception → EXECUTION_INDETERMINATE; fallbacks → Stage 2 runs) and the budget mechanics (job order, the per-job limit, stop without raising) |
| QC12 | Static structure. An AST check of the driver shows no path from qualification modes to the target. The FC4 static check covers: `srk_gate._TOKEN`, `object.__setattr__`, any `GateResult(` call, **rebinding `srk_adapter._REAL_GEOMETRY_ITEMS` or `REAL_GEOMETRY`**, any geometry or kernel override, and `verdicts_from_verifier` called without the pinned N and max_depth. Also a leak scan against the committed target-cell tokens |
| QC13 | Temporal and governance state: the ordering freeze → qualification → review → grant; r5 unchanged; no r6 |
| QC14 | `rehearse --cell 305`: historical reproduction of C2's committed 305 record with SRK disabled and S = S_I1, equality only (the accepted pattern) |
| QC15 | Self-audit A1–A10 (`code/self_audit.py`), including the verifier-probe envelope audit: no in-band probe was ever evaluated |
| QC16 | Re-qualification of FC2 (protocol §7): the grant-scoped verifier variant (hashed before the freeze) on the full decoy battery, with genuine ACCEPT, every v2 mutant expectation and the 21 self-tests. Also: the grant-scoped 7q counterpart, which must refuse without a valid grant and outside Ew; **a sandbox positive-path test of admission inside a test hull under a valid test grant** (synthetic geometry, or a substituted test band and hull; never the real band); and the probe-construction guard, which must be independent of any lifted list. **The verifier's review mode (§F) is also qualified in a sandbox** (R3 F2.4): it admits a certificate only when a test marker names a test grant and a test sealed result lists that sha256, and it refuses otherwise. Everything is ledgered |
| QC17 | S construction: S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)) on manufactured non-target supplies versus an independent recomputation, including the None → S_I1 fallback (the accepted pattern's S-construction case) |

**Gates.** Q01–Q17, one per QC item; none may be waived. The accepted earlier pattern had Q1–Q12, and this package
extends it. The verifier has an official mode (grant-scoped, for Stage 1a) and a review mode (§F).

## C. Exactly-once driver design (`code/p309_driver.py`)

**Modes.**
* `preflight`: read-only.
* `rehearse --cell 305`.
* `decoy-stage1a --cell <declared>`.
* `decoy-stage1b --cell <declared>`.
* `execute`: the qualified worktree plus the grant commit only.
* `seal-only`: never computes.

**Exit codes.**
* 0: sealed;
* 2: refused pre-marker;
* 3: CONTROL_FAILED (not consumed);
* 4: UNSEALED;
* 5: sealed failure status;
* 6: CONSUMED_UNRECORDED;
* 7: sealed but not materialized.

**`execute`, in order:**
1. `check_grant`: the chain HEAD^^^ = freeze → qualification → review → grant, each commit touching only its own
   files.
2. Verify all pins, including the interpreter and platform string.
3. Refuse if any guarded path exists (lstat), or if the namespace is unclean (ignored files included).
4. Historical control (protocol §4). CONTROL_FAILED ⇒ exit 3. Record its digest.
5. Arm the marker by CAS from the zero OID → grant. Ignore signals from here on.
6. Stage 1a (protocol §2): per-rung serialization, in-process verdicts, the gate, the §2.5 failure mapping and the
   48 CPU-h budget.
7. Stage 1b (protocol §3).
8. Stage 2 (protocol §4).
9. Serialize the result in memory; `hash-object -w`; set the pending ref by CAS (with the emergency O_EXCL file as a
   second channel); commit with a private index and `--cacheinfo`; materialize O_EXCL|O_NOFOLLOW; read back.

**Guard.** Workers re-verify the pins, and arm the grant-scoped band guard only when marker = grant = HEAD.

## D. Grant schema (`authorization/P309_GRANT.json`, committed alone as the child of the qualification review; a separate owner decision)

* **Scope fields:** `schema`, `cell`, `detector`, `m`, `route`, `closure_only` (true), `closure_criterion`
  ("Γ < 0 exact, strict").
* **Not-authorized fields:** `adoption`, `floor_change`, `r6`, `k5_or_p5y_closure` (each NOT AUTHORIZED).
* **Chain fields:** `freeze_commit`, `freeze_tree`, `qualification_commit`, `qualification_review_commit`,
  `input_manifest_path`, `input_manifest_sha256`, `driver_path`, `driver_sha256`, `evaluator`.
* **Execution fields:** `executions_authorized` (1), `exactly_once` (names), `consumed_marker`, `outcome_table`.
* **`disclosed_liabilities`:** overnight 01–03; 309R1-01, 309R1-02, **309R1-03** and **309R1-04**; ERRATA **E-3** and
  **E-17(a)**; the ledgered reads.
* **Review record fields:** `incident_review_conditions_verbatim`, `qualification_review_conditions_verbatim`,
  `qualification_review_notes_verbatim`, `issued_utc`, `granted_after`, `authority` (the owner instruction, verbatim
  reference).
* **Band and verification fields:**
  * `drift_hull_Ew`: the exact outward 2⁻¹⁰ hull of C. The grant-scoped guard admits band drifts only inside it. It
    may overlap a neighbouring cell's drift range, and that overlap confers no licence to reuse;
  * `verifier_id`: the sha256 of the pinned grant-scoped verifier variant;
  * `in_band_verification`: "genuine certificates only; no mutant battery; no shifted or widened probe";
  * `non_reattribution`: "Stage-1 material of 309 is bound to 309 and is never reused for another cell".

## E. Recording the result from memory

The accepted C12-R2 / RLR307 design. The result bytes are canonical JSON, containing:
* **all** Stage-1a certificates (per rung), **all** verifier verdicts with reasons, and the full GateResult report
  (admitted and refused, with reasons);
* the Stage-1b rung supplies and the reconstruction results;
* S, Γ̄, per-r rad^SRK with branch labels, 𝓗_SRK, M, g_hi, and Γ as an exact rational string;
* pass;
* the historical-control digest;
* budgets used;
* timings.

## F. Post-execution checks (`postexec/`)

* The result blob equals the pending ref, including its self-hash.
* The seal commit changes the result path only, and its parent is the grant.
* The marker names the grant, and there was exactly one execution.
* A second `execute` is refused before anything happens. Resolve the recorded E4 tension by running this probe only
  in the sandbox copy.
* `seal-only` is read-only.
* The worktree copy equals the sealed bytes.
* r5 is unchanged, and there is no r6.
* No other cell was evaluated.
* **The historical-control digest is present and equal to C2's committed record** (R3 N10).
* **Independent re-verification** of every sealed Stage-1a certificate uses the verifier's **review mode**. Review mode
  admits the band only when:
  * the marker names the grant; and
  * the sealed result exists and lists the certificate's sha256.

  It evaluates only those sealed certificates, genuine only, with no probes. If its verdict on any sealed certificate
  differs from the sealed admission, or the digest check fails, the outcome is EXECUTION_INDETERMINATE (protocol §5)
  (R3 N9).

## G. Review briefs

Four full briefs are in **`P309_REVIEW_BRIEFS.md`**: incident independence, qualification, execution and
adjudication. Each has allowed reading and running, a firewall and verdict tokens. They are issued in order, and each
review is preserved verbatim. REJECTED ⇒ STOP, with no same-round repair.

## H. Adjudication rule

Apply protocol §5 verbatim to the sealed status, with an exact-Fraction recomputation of Γ from the sealed components.
The label is one of: CELL309_CLOSED_UNDER_P309 (scientific closure only), NOT_CLOSED or EXECUTION_INDETERMINATE.

## I. Failure and recovery semantics

* Any REJECTED review ⇒ STOP.
* A consumed marker is never rerun.
* If result information is lost, there is no recomputation without a new, independent governance process.
* **STOP conditions (pre-marker):**
  * the start state differs;
  * the incident review rejects;
  * the target appears consumed;
  * inputs drift (a pin mismatch);
  * qualification touches the target;
  * the exactly-once infrastructure is unsafe;
  * the historical control fails.
* **Stage 1a (protocol §2.5):**
  * non-CERTIFIED statuses, non-ACCEPT verdicts and budget exhaustion fall back (Γ̄_i = None; no retry);
  * any exception gives EXECUTION_INDETERMINATE.
* **Stage 1b (protocol §3):**
  * CERTIFICATION_FAILED falls back to the S_I1 values;
  * an exception or reconstruction mismatch gives EXECUTION_INDETERMINATE.
* **Post-seal (§F):** a disagreeing re-verification or digest gives EXECUTION_INDETERMINATE.

## J. Formal-campaign items from independent review R2 (FC1–FC6)

* **FC1, the pin set.** `P309_CANDIDATE_FREEZE_MANIFEST.json`, plus the freeze additions of §A. The code files are
  pinned by git blob and sha256.
  * Producer: lock 2a03e838, fingerprint 377057be….
  * c1b_gauss.
  * The gate, adapter and assembly in their post-R2 state.
  * The verifier file and harness v2, the self-tests and the verifier settings.
  * THEOREM_SRK, SRK_CERT_SPEC, all decoy declarations (A0, A1, A2), `TARGET_QUARANTINE_309.json`, ROUTE_SELECTION_RULE.
  * The QC test files, including `tests/planted_control_q309.py` (needed by the static scan).
  * The self-audit and the envelope tool.
  * `ERRATA.md` and `registry/PHASE3_ROUTE_COMPARISON.md`.
  * The C1b kernel files used by Stage 1b (`c1b_kernel.py`, `c1b_float.py`, …) are covered by `C1B_R2_CODE_PINS.json`,
    which is itself pinned. The coordinator checked this by file names only.
* **FC2, band handling.** Protocol §7 **(a)–(d)**, with the same lettering: (a) the grant-scoped guard; (b) the
  grant-scoped verifier variant (authorship, order, QC16 re-qualification including the sandbox positive path, and
  evidence of authorship); (c) a probe-construction guard independent of **every** lifted list, including the
  grant-scoped guard's; (d) a grant naming Ew. The genuine-only / no-probe rule for in-band certificates is in protocol
  §2.4.
* **FC3, Stage-1 failure semantics.** Protocol §2.5 and §3 (fixed).
* **FC4, the Stage-2 driver.** In-process verdicts at the pinned N and max_depth; `verifier_id` from the pinned bytes;
  the cell from the pinned `cells.json` as exact rationals. The static check is part of QC12.
* **FC5, RLR Stage 1b.** The RLR307 rules verbatim on 309's blocks, with a fallback on CERTIFICATION_FAILED (protocol
  §3).
* **FC6, exactly-once machinery and reviews.** §§C–I and `P309_REVIEW_BRIEFS.md`.

## K. Owner decisions

See `P309_OWNER_DECISIONS.md`.
