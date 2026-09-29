# Independent route review R2 of SRK (cell-309 research campaign r1)
ROUTE_REVIEW: FREEZE_READY_WITH_CONDITIONS

**Status.** Final, 2026-09-29.
* Phase A was reviewed at `a748ac49`…`daa7e885` (16:19–16:40Z). Phase B was reviewed at `bf5c87c4` (23:11–23:40Z),
  on a clean tree with no coordinator process running.
* I am not the R1 reviewer, and I have no stake in the outcome.
* Everything below was recomputed or re-run where possible; I did not rely on the coordinator's summaries. The
  Phase-A record (§§1–7 as first written) is kept below; the Phase-B updates (§PB) supersede it where they say so.

## Verdict

**FREEZE_READY_WITH_CONDITIONS.** P309 (package 1) is scientifically ready to be frozen into a formal, closure-only,
exactly-once campaign, subject to three conditions. The route is: the frozen direct clause, the SRK-0 whole-kernel
order-0 channel min construction, and the supply S = (A0_I1, min(A1_I1, A1_RLR), min(A2_I1, A2_RLR)).
* No mathematical, soundness, producer or evidence blocker remains.
* All three conditions are target-free and can be met inside the freeze package without new science.
* This classification authorizes nothing. See (ii) and the P0-1 statement.

Classes: A mathematical/soundness · B implementation · C verifier/control · D evidence completeness ·
E provenance/governance · F wording/documentation · G target-dependent or unrepairable without forbidden information.

### (i) Science / implementation: blockers none; conditions C1–C3

| id | class | condition (target-free; inside the freeze package) | evidence |
|---|---|---|---|
| **C1** | B | Fix the adapter's geometry to (5, 1/2). `srk_enclosure(..., geometry=REAL_GEOMETRY)` is a caller-overridable keyword. With `geometry={"h":"3/1",…}` the adapter ACCEPTS a synthetic-geometry GateResult (RD2-B2 probe b1‴). Remove the keyword, or refuse any value ≠ REAL_GEOMETRY, and add the probe to test_srk_adapter | srk_adapter.py:93–94, 72–73 |
| **C2** | D, F | Record the non-run of the A1 taboo family as a formal withdrawal for package 1 (erratum). The base declaration says "All declared decoys are run and reported", and A2's rerun rule names the A1 taboo family. a748ac49 said it "is still run as preparatory evidence", but PHASE3 (23:1xZ) now says "not run". It cannot affect P309 (SRK-T is OUT). The erratum must say that any package including SRK-T runs the full A1 family from its own locked code state | config/SRK_DECOY_DECLARATION.json "no_selection"; SRK_DECOY_DECLARATION_A2.json "rerun_rule"; PHASE3 readiness table |
| **C3** | C | Give the verifier battery's quarantine probe its intended reason. On **all 41 rerun real-kernel certificates** (25 whole + 16 cell), mutant `7q_quarantine_band_refused` is REFUSED for "weight_block does not contain block", **not** for the band. Only the 15 preliminary certificates (no `weight_block` key) exercised the band refusal. Fix the generator (verify/run_verify_all.py) to move `weight_block` with `block`, or assert the reason, and re-run the battery. The verifier file and its identity are untouched. Firewall control only; not load-bearing for validity | VERIFY_RESULTS.json `mutants.7q_*.reason` |

**No G-class item.** Nothing in this review needs 309 information to be decided.

### (ii) Owner governance decisions (block authorization, not the route class)

* **G1.** Accept SRK's motivation-provenance liability, **MEDIUM-HIGH**. Its sources:
  * 309R1-02 (an in-band estimate during ideation) and 309R1-01;
  * rule S's "BLOCKED-only" C4 threshold, set by the exposed coordinator;
  * every post-R1 rule was written by the same exposed coordinator. The rules written knowing decoy counts or ratios
    are disclosed (E-10, E-12), and they are decoy-only.
* **G2.** Authorize a separate closure-only, exactly-once campaign. It includes new in-band Stage-1 operator
  certificates over the **hull Ew** of cell 309, which are forbidden here.
* **G3.** Confirm RLR as the min-composed A1/A2 component. It needs its own 309 Stage-1 blocks by the frozen C2 rule and
  carries the 307 disclosures.
* **U2.** Rule, or confirm "not triggered": P309 claims no quantity derived from P3 records (rule S C3), and KG-U2
  requires a ruling before any Stage-1 freeze.
* **U3.** Decide on the floor extension for closure-only routes, or on explicit CLOSURE_ONLY. KG-U3 says: user-instructed,
  frozen and reviewed before Stage 1. Adoption needs U3; closure does not.
* **SRK-T under C5.** Should the exclusion be reconsidered? My finding (item 5) is that it is correct and safe.
  * Re-inclusion is optional. It would need a D_lo decoy certifier, the A1 taboo family from a locked state, a
    verifier taboo-mode qualification and a new review.
  * It must be decided **before** any 309 Stage-1 number exists (rule S).
  * Excluding it in an exactly-once campaign forgoes SRK-T for 309.
* **Efficacy is unknown by design.**
  * Real-kernel decoys stop at 33/32 and never bracket the band, and no decoy number may be extrapolated. So nothing
    here says whether SRK certifies at 309's drift.
  * Failure is safe: Γ̄_i = +∞, then TC-T. But it would spend the single evaluation on P309 without the SRK channel.
    The owner should decide knowing this.
* **Other recorded user items** (governance report §2): acknowledgement of the incident disclosures, the cell set, a
  separate grant after QUALIFICATION_ACCEPTED, any new real computation, and push/merge. R1 G4 (the unverifiable timing
  of an early out-of-band probe) is historical.

**P0-1 (does an actual protocol freeze itself need owner authorization?)** **Yes.**
* No protocol draft is inside my allowed reading: `protocol_prep/` is empty and untracked. So I cannot quote P0-1's
  text.
* Independently of that text, the recorded governance requires owner authorization before an actual freeze:
  * README: the campaign is research-only; "no exactly-once step, no grant, no marker… without explicit
    authorization"; `protocol_prep/` is "prepared only if … FREEZE_READY. Never executed";
  * governance report §2: U1–U3 "none decided"; KG-U2 requires a ruling "before any Stage-1 freeze"; KG-U3 requires
    the floor extension to be "user-instructed, frozen and reviewed before Stage 1";
  * R1 G2.
* This verdict classifies readiness only. It authorizes neither a freeze nor a campaign.

### (iii) Formal-campaign items (expected outstanding; not blockers of the route class)

* **FC1. Pin set.** It must cover:
  * producer `srk_kernel/srk_float/srk_envelope/srk_certify` + the imported `c1b_gauss` (fingerprint `377057be…`,
    lock `2a03e838`);
  * `srk_gate`, `srk_adapter` and `srk_assemble` at the post-`cfb88c69` state, plus C1;
  * the verifier `a32d5d39…` (or its grant-scoped successor, FC2), `run_verify_all.py`, SRK_CERT_SPEC, THEOREM_SRK
    §§1–3 and 9–12, and the configs;
  * the §12 constants, the verifier parameters (N = 8, max_depth = 24), and the Python version.
* **FC2. Grant-scoped band handling (necessary for SRK to have any effect).**
  * As qualified, the producer refuses the band through q309 (`guard_geometry_block`, `log_execution`). The
    verifier also refuses any real-geometry certificate whose block or weight block meets the band (hard-coded
    `QUARANTINE_BANDS`, srk_verify_indep.py:121, 254–259, 1448).
  * Unchanged, every 309 certificate would be refused and Γ̄ = None, so the route falls back to TC-T. That is safe
    but useless.
  * Replacing the verifier's band check changes its identity, so it must be re-qualified before the seal: self-tests,
    then batch re-verification of the 87 decoy certificates and battery (minutes).
  * The grant must cover **Ew**, not only C. Ew extends up to 2⁻¹⁰ beyond C, possibly into an adjacent quarantined
    cell's drift range; no evaluation of that cell is involved.
* **FC3. Stage-1 driver.**
  * Exact-rational cells from the pinned cells.json, then `cell_blocks`, then one `run_block` per sub-block with
    weight block = Ew. Deterministic output.
  * Failure semantics fixed in advance: Γ̄_i = +∞, no retry.
  * Optionally, decided in advance: emit every certified rung, not only the best one.
* **FC4. Stage-2 driver.**
  * Verdicts by `srk_gate.verdicts_from_verifier` with the pinned verifier in-process. `verifier_id` goes to the
    adapter. The pinned `tct_rule` is loaded by bytes. Reproduction gate, dominance, frozen direct clause.
  * A static driver check: no use of `srk_gate._TOKEN` or `object.__setattr__`, and no geometry override. RD2-B2 b7
    shows the module-private token can be forged, so immutability holds against accidents, not against an
    adversarial driver.
* **FC5.** RLR 309 Stage-1 blocks (G3).
* **FC6.** Exactly-once machinery: grant, marker/seal, sandbox qualification (the 307 anatomy, Q1–Q12), and independent
  qualification, execution and adjudication reviews.

---

## PB. Phase-B findings

### Item 3. B3 evidence integrity: PASS (no failure; C2 and C3 above)

Everything below was recomputed by me (RD2-B1, B4, B5, B5b, B6), mostly without trusting the manifest, the
self-audit or the summaries.

**Completeness.**
* The expected names, derived from `SRK_DECOY_DECLARATION.json` (real 5 + h3 3 + h4 3 blocks) and from
  `cell_blocks` on the 2 A2 cells (4 sub-blocks each), are exactly the 19 files present. **19/19; nothing missing,
  nothing extra.**
* Each file's geometry, block, kernel (`whole`), weight block (= the hull for cells, `null` for whole blocks), index
  set (0–4 whole, 1–4 cell) and ladder (8, 10, 12) are as declared.
* In all 57 rungs, W is CERTIFIED and every index has a V: every rung certified.
* The A1 taboo family was not run (C2). The A1 index-5 item is conditional on SRK-1, which is deferred.

**Single code state.**
* All 19 files carry `producer.combined = 377057bef1d1…` and `git_head_at_start = 2a03e838498a…`.
* I re-hashed the producer bytes **as committed at 2a03e838** (`git show 2a03e838:<path>` for the 4 producer files and
  `c1b_gauss.py`). They reproduce each file's per-file sha256 dict and the combined hash exactly. The current working
  tree gives the same fingerprint.
* `git diff 2a03e838 HEAD` is empty for all five files.

**Nothing dropped, re-run or overwritten.**
* After the lock (16:07:47Z), the exec ledger has **exactly one** `run_block` line for each of the 19 blocks.
* Each evidence file was committed once. The four earlier commits on the same paths are the pre-E-7 preliminary
  files, moved to `srk_decoys_prelim/` at 5f41d8a9.
* Across all 21 committed versions of VERIFY_RESULTS.json since fae64157:
  * the totals grow monotonically, 20 → 107 certificates and 415 → 2196 expectations;
  * no non-ACCEPT verdict and no failed mutant expectation was ever recorded;
  * no sha has two verdicts, and no (file, index) ever had two shas.
* The MC preview (dade1486, 50 rows) is identical, row for row, to the final (142fe64e, 55 rows).
* The E2E file was produced once.
* SRK_CERT_MUTANTS.json changed once, for the disclosed T1 repair (E-13).

**Certificates.**
* 87 = 11 × 5 + 8 × 4, all CERTIFIED.
* The canonical sha256 recomputes to the stored value for every certificate.
* The certificate fields match the file: geometry, block, `kernel` whole, index, `producer_sha256` = the lock
  fingerprint, and weight_block.
* Γ in each certificate equals the file's Γ_i, and that is the minimum over rungs at the arg-min degree.

**Independent verification.**
* Every certificate's sha256 has a VERIFY_RESULTS entry: **87/87 ACCEPT**, with **1781/1781** mutant expectations met
  (2196/2196 including the preliminary files).
* Settings: N = 8, max_depth = 24. The verifier file is unchanged since 2f026dbc (sha `a32d5d39…`, equal to the
  manifest).
* **My own re-run of `verify_cert` on all 87 certificates (RD2-B5/B5b): 87/87 ACCEPT, sha-matched.**
* The 32 genuine weight_block ⊋ block certificates are among them. This closes R1's verifier-coverage gap.

**MC controls.**
* `SRK_MC_CONTROL.json` has 55 rows, exactly (11 blocks × indices 0–4). Row Γ equals the evidence Γ, and all rows pass
  the 5-se criterion.
* **I reproduced all 55 rows bit-identically** with the committed seeds (RD2-B6).
* The worst row is (Γ − MC)/se = −2.23 (h4 [1, 33/32], i = 0). This is within the allowance, and the MC weight is a
  1/32-grid upper envelope, so it is conservative.
* Decoy-only tightness Γ/MC is 0.99–1.39.

**A2 end to end.** My re-run of `e2e_cell_family.run(10000)` (RD2-B4) gave PASS on both cells, 13/13 checks each.
* In-process verdicts equal the batch verdicts.
* The gate is bound to the cell and the verifier identity, and equals the max over sub-blocks.
* Γ̄ and the MC rows are identical to the committed file. The cell-level MC passes 8/8.
* The negatives on real certificates refuse for their own reasons:
  * `independent verifier verdict 'REJECT'`;
  * `kernel whole != requested taboo`;
  * `weight_block is not the cell's outward dyadic hull` (narrowed weight block; shifted cell);
  * the missing sub-block gives None.

**Manifest and self-audit.** My recomputation agrees with `SRK_EVIDENCE_MANIFEST.json` (complete, 19 jobs, 87
certificates, lock, verifier sha) and with self-audit A1–A9. I checked A7 (namespace-only since base b73b9449: 0 paths
outside NS) and A2/A1 (below) directly.

**Failures found:** none. Deviations: C2 (declaration bookkeeping) and C3 (control reason).

### Item 8. Classification: FREEZE_READY_WITH_CONDITIONS (see "Verdict" above)

* **Soundness (A).**
  * SRK-0 (R1), Lemma SV″ and the §12 D_lo argument (my Phase A) hold.
  * The Phase-B restatement of SC-SRK is also correct (PHASE1_RESULTS.md). If for every e ∈ C,
    (R_eκ̄_i)(a) < ‖κ̄_i‖E_a[τ_e], then with continuous sides on compact C, sup f < sup g. Hence Γ̄_i < A0·k_i, and
    B3 < A0·f_G when that index's coefficient is > 0.
  * Nothing in P309's validity depends on a decoy number or on any 309 quantity.
* **Implementation (B).**
  * The producer is qualified at a single locked code state.
  * The gate and adapter are repaired (P-1). One residual remains, C1.
  * Failure semantics are fail-safe: None → TC-T. Dominance is checked twice (the `rad_srk` refusal and the adapter).
* **Verifier and controls (C).**
  * The verifier is independent and re-verified by me on all certificates.
  * The controls have demonstrated power: T1 is now refuted at an explicit point, and T2, the FSM M1/M4/M5, the
    envelope corners, the assembly mutants, the gate and adapter probes, and MC all bite.
  * One control reason is wrong, C3.
* **Evidence (D).** It is complete for package 1 (item 3). The C2 bookkeeping item remains.
* **Provenance (E).** Temporal integrity passes: after fae64157 there are 403 exec-ledger lines, and the counters are
  0. The max real-kernel |drift| is 33/32, with no line at |e| ≥ 6/5, and the ledger is append-only. There are no
  producer changes after the lock, the static scan passes, and all changes stay inside NS. The G1 liability stays
  with the owner.
* **Wording (F).**
  * The B6 corrections are present; SC-SRK is fixed; E-12 through E-14 are recorded.
  * One remaining wording mismatch is covered by C2.
  * NOTE: the MC control's ledger lines carry no `drifts` field. `guard_drift` is still called before any real-kernel
    simulation, so this is only an audit-trail gap.

### Phase-B updates to Phase-A items

**Item 2 (B2 gate): PASS (supersedes P-1 "OPEN"), with residual C1.** I re-ran every RD2-2 probe against the repaired
code (RD2-B2). Each is now refused, for its own reason:
* an unrelated cell ("GateResult is for another cell"; if the driver also passes that cell: "cell half-width != meas
  rho");
* a synthetic geometry ("for another geometry");
* a hand-built GateResult (`TypeError`, foreign token);
* a mutated EMPTY gamma (mappingproxy has no `__setitem__`; attribute rebinding gives "immutable"; an
  `object.__setattr__` bypass gives "EMPTY GateResult with a non-None value");
* GATE_TABOO and GATE_MIN ("not admissible in package 1");
* a verdict-source mismatch or a missing `verifier_id`;
* the `allow_test_gamma` keyword (removed: `TypeError`);
* D_lo = 4 ("(0, 1]");
* a float cell endpoint;
* hermite_index 1.5 ("hermite_index is not an int");
* `combine` across cells.

Two residuals:
* (b1‴) a caller-overridden `geometry` keyword is ACCEPTED, hence C1;
* (b7) a forgery with the module-private `_TOKEN` is ACCEPTED. That is adversarial and inherent to Python; it is
  covered by FC4.

`verdict_source` is a caller string. Its binding comes from `verdicts_from_verifier` plus the adapter's `verifier_id`
equality, so the driver's use must be statically checked (FC4). Tests: test_srk_gate 33/33 and test_srk_adapter
17 × 20, both re-run and passing.

**Item 4 (controls): PASS (supersedes P-2), with C3.**
* test_srk_cert_mutants re-run (RD2-B3): T1 is the consistent quarter-weight mutant, **REJECT with `false: True`**
  ("C3 is FALSE at (3/16, 3/16, 17/64): certified upper bound −0.59 < 0").
* The legacy T1 row is report-only ("UNPROVEN", as I found).
* T2 is refuted; T8 and T10 pass.
* E-12 (the T8 tolerance disclosure) and E-13 (the T1 history) are recorded.

**Item 5 (SRK-T):** unchanged (PASS). The adapter now refuses taboo-derived results, and `_d_lo` enforces (0, 1].

**Item 6 (changed code): PASS, with residual C1.**
* **`srk_gate`.** Construction requires the module token. Values are held in `MappingProxyType` over private copies,
  and `__setattr__`/`__delattr__` raise. `_rat` refuses floats and bools. The G5 verdict check precedes the index
  type check. D_lo must be in (0, 1]. `combine` requires the same cell, geometry and verdict source.
* **`srk_adapter._bound_gamma`.** It checks the source ∈ {GATE, EMPTY}, the exact cell, the geometry, kernel = whole,
  ρ = half-width, indices = {1..4}, EMPTY ⇒ all None, `verdict_source == verifier_id`, and each Γ̄ ∈ Fraction ≥ 0.
  All of these are correct.
* No producer file was touched (`cfb88c69` changed only the gate, adapter, tests and text).
* NOTE: `verifier_identity` hashes the verifier file only, not N or max_depth. Pin those (FC1).

**Item 7:** re-checked at bf5c87c4 (403 ledger lines after fae64157; see Item 8 E). PASS.

---

## Phase-B disclosures

**Exposures.**
* Phase B added only NS files: the governance reader report §§1–3, PHASE3, ERRATA, theory, evidence JSON,
  VERIFY_RESULTS, and the new code and tests.
* **No 305–309 number was seen.** The only in-band values I met were the verifier battery's `7q` refusal-probe drift
  literals (in reason strings of preliminary entries). They are generic band points and carry no cell quantity.

**Executions (Phase B).** All executions were declared in §0B before running; RD2-B5b was declared by the amendment
before it ran.
* Ledgers: 91 lines in total across `scratchpad/r2/reviewer_exec_ledger*.jsonl` (Phase A + B). Max real-kernel
  |drift| is 33/32; all target counters are 0; no cell was touched.
* Runs:
  * the RD2-B1 integrity script;
  * the RD2-B2 probes;
  * RD2-B3: 5 tests via `run()`;
  * RD2-B4: e2e `run(10000)`;
  * RD2-B5/B5b: the verifier on 11, then all 87 certificates;
  * RD2-B6: all 55 MC rows.
* Scripts are in `scratchpad/r2/`.
* Nothing was written in the repository except this file. No git write. No process was started or stopped other than
  my own.

---

## Phase-A record (written 16:19–16:40Z; superseded where §PB says so)

### 0. Reviewer execution declaration (Phase A; verbatim)


Written 2026-09-29 ~16:20Z at HEAD `a748ac49`, while the coordinator's rerun (`srk_decoy_suite.py 2 whole`,
`2 cell`) is running. I do not start, stop or touch those processes, and I do not run `srk_decoy_suite.py`.

Every run below uses `PYTHONDONTWRITEBYTECODE=1`, calls only `run()` (never a `__main__` that writes evidence), and
redirects `q309_guard.EXEC_LEDGER` to `scratchpad/r2/reviewer_exec_ledger.jsonl`. Nothing is written in the repository
except this file.

| id | what | kernel / geometry / drift | certifier? |
|---|---|---|---|
| RD2-0 | static quarantine scan (`q309_guard.scan()`, read-only) | none | no |
| RD2-1 | `cell_blocks` arithmetic probe on non-dyadic, dyadic, negative and degenerate cell endpoints, against my own re-implementation (no kernel evaluated; no endpoint in [6/5, 13/5] or its mirror) | none | no |
| RD2-2 | `srk_gate.gate` / `combine` / adapter-binding probes on constructed certificate objects (no kernel), with refusal reasons printed | none | no |
| RD2-T | NS tests via `run()`: test_q309_guard, test_srk_gate, test_srk_adapter, test_srk_assembly_twosided, test_srk_envelope (real geometry envelope only, E = [1/4, 9/32]), test_srk_fsm_truth (synthetic FSM), test_srk_wrec_refusal and test_srk_cert_mutants (both: synthetic h = 3, k = 1/2, E = [1/4, 9/32], degree 8, whole and taboo kernel; the latter also runs the independent verifier) | h = 3 synthetic; real geometry only inside the envelope test at e ≤ 9/32 | yes (h = 3 only) |
| RD2-3 | T1 power probe. Synthetic h = 3, k = 1/2, E = [1/4, 9/32], degree 8, index 1, whole kernel: (a) genuine and `quarter_weight` weight certificates from the same W, reporting r_min and λ of both; (b) a *consistent* quarter-weight mutant (float proposal RHS also κ̄₁/4, exact check against κ̄₁/4, certificate claims κ̄₁), judged by `verify/srk_verify_indep.verify_cert` with the test's settings (N = 8, max_depth = 24). Expected: (b) REJECT with an explicit refutation | h = 3 synthetic only | yes (h = 3 only) |

No run touches the real kernel at a drift above 9/32, any cell 305–309, or any drift in [6/5, 13/5] or its mirror.

**Timing disclosure.**
* The declaration file was written at 16:19:56Z (file mtime).
* My first certifier call (test_srk_wrec_refusal, `certify_W`) is ledgered at 16:22:03Z in my scratch ledger.
* The coordinator's WIP commit `4a6a546b` (16:25:16Z) captured the declaration byte-identical, but only after
  RD2-T had started.

So git alone does not show declaration-before-run; the file time and my session do. This is the same situation as
R1's timing disclosure.


### Phase-A summary (historical; P-1 and P-2 were repaired, see §PB)

**Science blockers: none found.**
* I re-derived Lemma SV″ (A3) and the §12 SRK-T D_lo argument, and both are correct.
* The hull rule is target-free, and `cell_blocks` implements it exactly: 3 014 cells matched an independent
  implementation, including non-dyadic, negative and degenerate endpoints.

**Implementation findings: all target-free, and all fixable without new science.** I class them as candidate
conditions (Phase B decides between a condition and a blocker):

1. **P-1. The gate is not bound to the consumer (item 2).** `srk_gate.gate` itself is sound: every admission rule
   refuses for the right reason. But the adapter's "GateResult only" rule is a type check, not a binding. RD2-2 shows
   the adapter **accepts** each of these:
   * a GateResult built by gate() for a **different cell and a synthetic geometry**;
   * a **hand-built** `GateResult(..., "GATE")`;
   * an `EMPTY` GateResult whose `gamma` dict was **mutated to 0**;
   * `GATE_TABOO` / `GATE_MIN` results. These carry a caller-supplied D_lo; D_lo = 4 > 1 is accepted, although
     D_e ≤ 1 always. SRK-T is OUT of package 1.

   Also:
   * `allow_test_gamma=True` bypasses the gate entirely;
   * the `verdicts` map is caller-supplied.

   A frozen Stage-2 path must bind the GateResult to the consumer's cell, the geometry (5, 1/2), the whole kernel,
   source `GATE`, and verifier verdicts produced by the pinned verifier.
2. **P-2. T1 has no demonstrated power (item 4).**
   * The committed quarter-weight mutant uses the **full-weight float proposal**; only its λ is sized for κ̄/4. The
     verifier's REJECT is "UNPROVEN at depth limit, certified lower bound −1.6·10⁻⁸": the claim is not refuted and
     may be true. This is the RD-1 / SE-1 phenomenon again.
   * RD2-3(b) shows that a *consistent* quarter-weight mutant is **refuted** at an explicit point.
   * T1 should be replaced by that mutant. The intent of §8 test 1 is still covered: RD2-3(b) here, and spec
     mutant 5 in R1.
3. Smaller NOTEs:
   * gate `int(hermite_index)` accepts 1.5 as 1 (only G5 stops it);
   * `combine` does not check that both results are for the same cell or geometry;
   * the degenerate-cell hull convention is not in the §11 text;
   * the runner lock does not cover gate/adapter/assembly, the guard, the suite itself or the configs;
   * the T8 tolerance 2⁻⁴ was written knowing R1's "Γ₀/Ā_W slightly above 1" observation, and this is not
     disclosed.

**Temporal integrity: PASS.**
* 98 ledger lines after fae64157 at scan time; max |drift| on the real kernel 9/32; no line reaches |e| ≥ 6/5; the
  ledger is append-only across every commit.
* No impl/, config/ or verifier-code change after the rerun code state 2a03e838.
* The static scan passes.
* The SRK-T exclusion is target-free and conservative.


---

### 1. B1 / Lemma SV″ and the §12 D_lo argument: PASS (NOTE on one undocumented convention)

**Lemma SV″ (THEOREM_SRK.md:311–321), re-derived.**
* Fix e ∈ C. Since C ⊆ Ew = ∪_j b_j (closed, contiguous quarters), e ∈ b_j for some j.
* On b_j, the pair (W^{(j)}, V^{(j)}) satisfies Lemma SV′ with Ψ = κ̄_i^{Ew}. So R_e exists and is positive, and
  (R_e κ̄_i^{Ew})(a) ≤ V^{(j)}_e(a) ≤ max over the endpoints of b_j (V^{(j)}_e(a) is affine in e).
* κ̄_i^C ≤ κ̄_i^{Ew} pointwise, because it is a sup over a subset. Positivity then gives
  (R_e κ̄_i^C)(a) ≤ (R_e κ̄_i^{Ew})(a).
* Taking the sup over e ∈ C gives Γ̄_i. Sub-blocks that do not meet C only enlarge the max, so the result is
  conservative.

The claim "Theorem SRK holds verbatim" is right.
* Steps 4 and 5 need |φ‴(e₀)(x)| ≤ Ψ3(x) and sup_{s∈C}|φ⁗(s)(x)| ≤ Ψ4(x), with Ψ built from κ̄_i^C.
* Replacing κ̄_i^C by the larger κ̄_i^{Ew} keeps both majorants valid.
* Step 6 needs R_e ≥ 0 for e ∈ C (from W^{(j)}), A0 ≥ sup_{e∈C} E_a[τ] (the supply, unchanged), and
  Γ̄_i ≥ sup_{e∈C}(R_eκ̄_i^{Ew})(a) (above).

**§12 D_lo argument (THEOREM_SRK.md:357–363), re-derived.**
* By regeneration at the atom, (R_e f)(a) = (Ĝ_e f)(a)/D_e, where D_e ∈ (0, 1] is the killing-before-return
  probability (Lemma SM(c)).
* For e ∈ C ∩ b_j and |f| ≤ κ̄_i^C ≤ κ̄_i^{Ew}, Lemma SV-T gives
  |(R_e f)(a)| ≤ (Ĝ_e κ̄_i^{Ew})(a)/D_e ≤ v̂^{(j)}_e(a)/D_e.
* v̂^{(j)}_e(a) ≥ 0 on b_j, and it is affine, so it is ≤ its endpoint max, and that max is ≥ 0.
* With D_e ≥ D_lo > 0 on C, the ratio is ≤ max/D_lo. Only e ∈ C is used, so validity of D_lo on C (not on Ew) is
  enough, as claimed.
* The raw taboo value bounds Ĝ_e, not R_e (E-11), so the division is mandatory. The gate does it
  (srk_gate.py:124).
* NOTE: `_d_lo` (srk_gate.py:57–66) does not refuse D_lo > 1, which is impossible since D_e ≤ 1. test_srk_gate
  even uses D_lo = 4 as a positive case (test_srk_gate.py:105). Harmless while SRK-T is OUT; fix before any package
  that includes SRK-T.

**Is the hull rule target-free, and fixed before any 309-related number? Yes.**
* Ew = [⌊2¹⁰e_lo⌋/2¹⁰, ⌈2¹⁰e_hi⌉/2¹⁰] and four equal sub-blocks. It is a function of the cell endpoints only, with
  two constants (GRID_BITS = 10, N_SUB = 4).
* N_E = 4 dates from §7 (before any decoy). The 2⁻¹⁰ grid is new in A3 (5f41d8a9, 15:55:20Z). That is before the
  single-code-state rerun, and no 309 quantity has been computed in this campaign.
* Neither constant can affect validity. The grid affects tightness only, by widening C by < 2⁻¹⁰ on each side.
* A3 contains no reference to 309 (THEOREM_SRK.md:303–336).

**Does `cell_blocks` implement it exactly? Yes (RD2-1).**
* I compared `srk_certify.cell_blocks` (srk_certify.py:61–79) against my own integer-division hull on 3 014 cells.
  The cells were: 14 hand-picked (non-dyadic, e.g. [1/3, 20/51] and [1/2, 37/72]; negative, e.g. [−7/9, −5/9];
  straddling 0; on-grid; degenerate on-grid and off-grid; width 10⁻⁹) plus 3 000 random rational cells, none meeting
  the band or its mirror.
* Result: **0 mismatches**. Every hull contains the cell, lies on the 2⁻¹⁰ grid, and is the tightest such interval.
  The four sub-blocks are equal, contiguous and dyadic, and cover Ew exactly. An empty cell (e_hi < e_lo) is
  refused.
* Example: [1/3, 20/51] → Ew = [341/1024, 201/512], sub-blocks with endpoints 1425/4096, 743/2048, 1547/4096. This
  matches the rerun's ledgered sub-blocks.
* NOTE (convention): a degenerate on-grid cell [x, x] gets Ew = [x, x + 2⁻¹⁰] (srk_certify.py:73–74). The §11
  formula would give [x, x]. This is harmless: ρ = 0 is refused by `srk_assemble.validate` (rho must be > 0), and
  D3 says SRK = TC-T there. Document it in the freeze package.
* NOTE (inputs): `cell_blocks` and `gate` accept floats (`F(0.1)` is the binary value, so the hull is for the wrong
  cell). The Stage-2 driver must pass exact rationals (strings or Fractions).

### 2. B2 gate: PASS for the gate logic; binding to the consumer is OPEN (candidate condition P-1)

**Gate logic (srk_gate.py:69–130).** I re-ran test_srk_gate (23/23), and RD2-2 printed each refusal reason.
Every G-rule negative is refused alone, for its own reason:

| probe | reason returned |
|---|---|
| sha tamper | `sha256 mismatch` |
| status | `schema/status` |
| geometry | `geometry mismatch` |
| kernel mismatch | `kernel taboo != requested whole` |
| kernel absent | `kernel not in hashed body (pre-B5 certificate)` |
| weight block narrower by 2⁻¹² | `weight_block is not the cell's outward dyadic hull` |
| weight block wider by 2⁻¹⁰ | same (A3 requires = Ew exactly) |
| e_c wrong | `e_c is not the block midpoint` |
| verifier REJECT | `independent verifier verdict 'REJECT' != 'ACCEPT'` |
| verifier verdict missing | `... None != 'ACCEPT'` |
| negative Γ | `negative Γ` |
| Γ as a float | `malformed: rational fields must be strings` |

* A missing sub-block gives None, and the max of the mins is computed correctly.
* **So, inside gate():** no certificate is admitted without an ACCEPT keyed by its exact sha256. The sha covers
  geometry, kernel, block, weight_block, e_c, index, polynomials, Γ and producer sha.
* Also inside gate(): nothing with a weight block ≠ Ew or with a wrong kernel is admitted, and a missing sub-block
  yields None (TC-T fallback).
* NOTE: `int(c["hermite_index"])` (srk_gate.py:109) admits `1.5` as index 1 (RD2-2). This is safe only because the
  verifier refuses a non-integer index (srk_verify_indep.py:233–235), so a genuine ACCEPT can never exist for it.
  The gate should type-check it itself.

**Can any path deliver a Γ̄ to the adapter without those guarantees? Yes (RD2-2).** `srk_adapter.srk_enclosure`
(srk_adapter.py:203–210) checks only `isinstance(GateResult)` and `source`. `GateResult` is a public, mutable class,
and its `report` carries neither the cell nor the geometry (srk_gate.py:125–129). The adapter ACCEPTED and used each
of these:
1. a gate() result for an **unrelated cell and synthetic geometry h = 3**, applied to a consumer object with a
   different ρ (no cell or geometry binding);
2. a **hand-constructed** `GateResult({i: …}, {}, "GATE")`;
3. `GateResult.empty()` with its `gamma` dict **mutated to 0**, which changes the enclosure (an `EMPTY` source does
   not force all-None);
4. `GATE_TABOO` / `GATE_MIN` results. A taboo result needs only a caller-supplied D_lo, and D_lo = 4 was accepted.
   `combine` also accepted two results for different cells and geometries.

In addition:
* `allow_test_gamma=True` admits a raw dict (srk_adapter.py:207);
* `verdicts` is whatever map the caller passes.

This does not break the mathematics, which is valid given the right inputs. But R1's B2 asked that nothing reach the
consumer without the listed checks, and the checks are currently enforced only if the (not yet written) Stage-2
driver calls gate() correctly.

**Candidate condition P-1 (target-free, no new science).** The frozen package must do all of the following:
* have gate() record cell, geometry, kernel and the admitted shas in an immutable result;
* have the adapter or Stage-2 driver check, exactly: the cell equals the consumer's [e₀ − ρ, e₀ + ρ]; geometry =
  (5, 1/2); kernel = whole; source = `GATE` only in package 1; and `EMPTY` ⇒ all None;
* remove or refuse `allow_test_gamma` in the frozen path;
* produce `verdicts` with the pinned verifier inside the formal run, or load them from a sealed, hashed file;
* re-qualify the adapter with a real gate() output (today, test_srk_adapter exercises only `EMPTY` and the raw-dict
  path).

**e2e gate negatives on real certificates.** By code reading (tests/e2e_cell_family.py:110–130), the negatives act
on the loaded rerun certificates:
* the narrow-weight negative asserts the refusal reason ("hull");
* missing sub-block, REJECT, wrong kernel and shifted cell assert only a None result. Each is structurally
  single-cause: only that attribute changes, and the kernel-mismatch and hull reasons fire first;
* a wrong-geometry negative is not included on real certificates. It is covered on constructed certificates in
  test_srk_gate.

They have not yet run on the complete rerun evidence. **Deferred to Phase B**, where I will run e2e `run()` and print
the reasons.

### 4. B4 controls: PASS except T1 (NOTE/FAIL-for-power, candidate condition P-2)

| control | can it fail? | right reason? | evidence |
|---|---|---|---|
| Envelope sampling control (4 corner mutants) | yes | yes: a mutant is caught when the envelope falls below a rigorous lower bound of k_i at a sample of box × E | RD2-T: genuine dominates; p1-for-p0, e_lo-for-e_hi, m1-for-m0, e_hi-for-e_lo all caught; sandwich 240/240; κ bounds ok |
| FSM exit rule: M1 12/12, M4 on every applicable case, M5 ≥ 1 | yes | yes (premise level) | RD2-T reproduced M1 12/12, M4 6/6 applicable (6 inapplicable: σ3 = 0, reported), M5 12/12. M1 and M5 are caught at premise level only (radius truth never), which is the right level: Γ < the exact sup over the cell |
| Two-sided assembly and live dominance refusal | yes | yes | 10/10 mutants; 7/7 refusals, including `dominance_refusal_live_drop_min3/4` (srk_assemble.py:98–99, no longer an assert) |
| W-record refusal | yes | yes | test_srk_wrec_refusal 9/9. All refusals raise before any computation (srk_certify.py:232–236), and refused calls leave no ledger line |
| Per-call ledgering | — | — | certify_W / certify_weight lines appear per call (ledger lines 24–25 onward; my scratch ledger has 17 lines for RD2-T/RD2-3) |
| T2 taboo-as-whole | yes | yes | REJECT with **refutation** ("C2 is FALSE at (3/16, 3/16, 17/64)"); genuine taboo ACCEPT |
| T8 constant weight | yes | yes | all three criteria hold (h = 3 decoy: Γ₀ = 36.04, MC 31.92 ± 0.21, identity within 5σ, Γ₀/max W(a) = 0.977). See the disclosure NOTE below |
| T10 determinism | yes | yes | sha identical across two productions, V round trip, genuine ACCEPT. NOTE: the round trip checks the V polynomials only, not W or the whole certificate |
| **T1 quarter weight** | see below | **no** | RD2-3 |

**T1 (THEOREM_SRK.md:372–374; tests/test_srk_cert_mutants.py:75–77).**
* The `quarter_weight` mutant changes only the exact-check RHS (srk_certify.py:249–250). Its float proposal is
  still solved against the **full** κ̄₁ (srk_certify.py:247).
* RD2-3(a), same W, h = 3, E = [1/4, 9/32], d = 8, i = 1:

  | | r_min | λ | Γ |
  |---|---|---|---|
  | genuine | −0.01695 | 0.01695 | 27.8715 |
  | quarter mutant | +0.2945 | μ = 2⁻²⁰ | 27.2465 (0.978 × genuine) |

  The two polynomials are identical except for the λW term (checked exactly).
* So the "mutant" is the genuine proposal with a smaller repair. Against the true κ̄₁, the verifier (N = 8,
  depth 24) returns **"C3 UNPROVEN at depth limit: certified lower bound −1.62e−08"** on a depth-24 cell near
  (1/4, 5/32, 17/64).
* The claim is not refuted, and it may be TRUE: the producer's r_min is a loose box bound, not the true minimum. A
  stronger verifier could ACCEPT it, and T1 would then "fail" with nothing wrong. As a negative control, it has the
  RD-1 / SE-1 defect.
* RD2-3(b): the **consistent** quarter-weight mutant (proposal RHS κ̄₁/4 as well; Γ = 0.25 × genuine) is
  **REJECTED with a refutation**: "C3 is FALSE at (p, m, e) = (3/16, 3/16, 17/64): certified upper bound
  −0.59 < 0".
* The verifier therefore does detect too-small weights. The committed T1 just does not test that. This is not a
  soundness issue: spec mutant 5 (index+1) is refuted in 16/20 cases per R1, and RD2-3(b) now exists.
* Commit a6bc6a04 honestly says "[unprovable, not refuted]". But §12's description, "Ψ/4 certified, κ̄_i claimed",
  overstates what the mutant is.
* **Candidate condition P-2:** replace T1 by the consistent mutant and require a *refutation* (`false: True`), not
  just a non-ACCEPT.

**Disclosure of rules written with knowledge of counts (E-10).**
* The FSM M4 rule is disclosed in both the test (test_srk_fsm_truth.py:146–152) and E-10.
* M5 "≥ 1" is lenient relative to the 12/12 result, so no result-chasing benefit is possible. But git cannot show
  it preceded the M5 run: the rule and SRK_FSM_TRUTH.json both land in 61a65003 (16:11:12Z), after the FSM run
  ledgered at 16:08:29Z.
* **NOTE:** the T8 tolerance "Γ₀ ≤ max_E W(a)·(1 + 2⁻⁴)" (THEOREM_SRK.md:376–380; test file added in 5f41d8a9 before
  its first ledgered run at 15:55:34Z) was chosen after R1 reported "Γ₀/Ā_W slightly above 1" on one decoy. It should
  carry an E-10-style disclosure. This is decoy-only, target-free, and a sanity bound only.

### 5. B5 / SRK-T exclusion: PASS (correct and safe), with NOTEs

**Correct under C5?** Yes.
* There is no D_lo certifier anywhere in NS, so the Γ̂ = v̂/D_lo path cannot be qualified end to end on decoys.
* The exclusion (PHASE3_ROUTE_COMPARISON.md, a748ac49, 16:12:58Z) cites only C5. It uses no decoy gain and no 309
  quantity.
* Timing: the first taboo rerun (real kernel [0, 1/32]; ledger lines 52–65) was stopped before any output file
  existed (ledger line 71), and no taboo job is running now. So the decision was not informed by rerun taboo results.
  The only taboo outputs that exist are T2's synthetic h = 3 certificates, which are structural (ACCEPT / refuted),
  not gains.

**Safe?** Yes.
* SRK-T is min-composed, so omitting it can only leave Γ̄_i (hence rad^SRK) the same or larger. It can never
  invalidate the enclosure, and it cannot bias the route toward closure.

**NOTEs.**
* C5 reads "…or it will be, in the same freeze package". Declining to build a D_lo decoy certifier is therefore a
  discretionary, conservative reading. The user should know that in an exactly-once campaign this forgoes SRK-T for
  cell 309 permanently.
* The package-1 code still accepts `GATE_TABOO` / `GATE_MIN` in the adapter, and `_d_lo` accepts D_lo > 1. P-1
  removes the first; fix the second before SRK-T is ever IN.
* B5's certificate-format part is repaired: `kernel` and `producer_sha256` are in the hashed body, and `claim` follows
  the kernel (srk_certify.py:338–349). The verifier refuses a cert-level / file-level kernel conflict
  (srk_verify_indep.py:237–240). So R1's RD-2 ambiguity (same sha, opposite verdicts) cannot recur, and T2 confirms
  it.

### 6. Soundness spot-checks of changed code: PASS with NOTEs

| unit | verdict | evidence |
|---|---|---|
| `certify_weight` W-record checks | **PASS** | srk_certify.py:232–236 refuses a non-CERTIFIED W or a mismatch in geometry, check block, degree, e_c or kernel type, before any computation. `whole` is inherited from the W record, so V and W always use the same kernel. The V′ = V + λW′ repair is valid because W′ − K_eW′ ≥ 1 on the same check block and e_c (R1 item 1(i)); this is now enforced rather than assumed. The verifier re-checks everything independently |
| `cell_blocks` | **PASS** | item 1 (3 014 cases, 0 mismatches). NOTE: the degenerate convention |
| `srk_gate` (whole) | **PASS** | item 2 |
| `srk_gate` taboo | **PASS** (math), NOTE | it divides by D_lo, refuses a missing or non-positive D_lo, a domain not covering C, and extra keys. It does not refuse D_lo > 1 |
| `srk_gate.combine` | **PASS** (math), NOTE | the index-wise min is valid for two results for the same cell. It does not check that they are for the same cell or geometry, because the reports carry neither |
| adapter source check | **PASS as written; insufficient as a binding** | P-1 |
| `rad_srk` refusal | **PASS** | srk_assemble.py:98–99; live under mutation (test_srk_assembly_twosided) |
| certificate body (B5) | **PASS** | `kernel`, `producer_sha256` and the kernel-dependent `claim` are in the sha body (srk_certify.py:338–349) |
| runner lock | **PASS** for what it claims, NOTEs | See below |

**Runner lock (srk_decoy_suite.py:91–100, 28–39).**
* **What it does.**
  * `git status --porcelain` must be empty for the 4 producer files and the imported `c1b_gauss.py`, so the working
    tree equals HEAD for them.
  * It records HEAD and the combined sha256. Every job re-hashes the files at start and end (`run_block` embeds the
    fingerprint) and refuses on any change.
  * `c1b_gauss` is hashed at the path actually imported (`KX.G.__file__`), which closes R1's sys.path.append
    concern for evidence binding.
  * No impl/, verify/*.py, config/ or c1b file changed after 2a03e838. `git diff --name-only 2a03e838 HEAD` lists
    only: ERRATA, evidence (FSM truth and two rerun blocks), ledgers, PHASE3, the R2 brief and review, THEOREM_SRK,
    tests/e2e_cell_family.py, tests/test_srk_fsm_truth.py and VERIFY_RESULTS.json.
* **NOTEs.**
  * The fingerprint does not cover:
    * srk_gate.py, srk_adapter.py and srk_assemble.py (not producers of certificates, but part of the route);
    * code/q309_guard.py (guard and logging only);
    * srk_decoy_suite.py itself;
    * the declaration configs;
    * the verifier;
    * the Python version.

    The freeze package's pin set must cover all of them (R1 already listed most).
  * The hash is of the files on disk, not of the imported module objects. Together with the clean-tree check at
    start, that is adequate.
  * `.gitignore` ignores only `__pycache__/` and `*.pyc`, so the porcelain check cannot be blinded by an ignored
    producer file.

**NOTE (tightness only).** `certificate_json` emits only the best rung per (block, i) (srk_certify.py:326–333). If
the verifier rejected that rung, the gate would fall back to TC-T (None) instead of to another certified rung. This is
safe. Emitting every certified rung, fixed in advance, would keep "min over admitted rungs" meaningful without being a
retry.

### 7. Target independence and temporal integrity since fae64157: PASS

* **Band drift.**
  * I scanned every ZERO_TARGET_LEDGER line after fae64157 (98 lines at 16:2xZ, including the running rerun's
    uncommitted tail).
  * All three target counters are 0 on every line, and `cells_touched` is empty.
  * Classes: NONTARGET_DECOY 94, SYNTHETIC_VALIDATION 3, PROCESS_NOTE 1.
  * Max real-kernel |drift| is 9/32; **no line meets |e| ≥ 6/5**.
  * The ledger is **append-only** across every commit fae64157..HEAD and in the working tree (script
    `scratchpad/r2/ledger_scan.py`).
  * NOTE: synthetic-geometry lines carry their drift only in the `purpose` text (`drifts: []`), by design. The A2
    real-kernel cell [1/2, 37/72] (hull ≤ 527/1024) had not yet reached the ledger at scan time. I re-scan in
    Phase B.
* **Decisions fixed without reference to 309.**
  * A3 (5f41d8a9), A4 (61a65003), the FSM rule (5f41d8a9 / 61a65003) and the SRK-T exclusion (a748ac49) contain no
    309 quantity, and none is conditioned on one.
  * A4's constants are exactly those in the producer at 2a03e838. A4's text was committed at 16:11:12Z, after the
    rerun started (16:07:47Z), but it documents rather than changes the code state. No producer file changed after
    2a03e838.
  * The earlier rerun at 2f026dbc was stopped before any output (ledger line 71). Its per-certificate log went to an
    in-memory list (`log=logs.append`, srk_decoy_suite.py:36), so no Γ was printed.
* **Static scan: PASS** (RD2-0).
  * 28 files, 0 findings, and the planted control fires all 4 kinds.
  * I inspected all 22 `literal-ok` suppressions. All are benign: Gaussian moments E|He_i| (summarize_decoys.py:8),
    state coordinates (p, m), Gaussian special-function arguments, the verifier's band definition, and two
    refusal probes (run_verify_all.py:118–119, test_verify_selftests.py:442–443) that are REFUSED at parse time.
  * The 8 sanctioned findings are all in the refusal test test_q309_guard.py.
* **Route-selection application: still target-free.** Rule S (ROUTE_SELECTION_RULE.md) is unchanged since
  7f1eb363. The a748ac49 application removes SRK-T by C5 only, and removal can only weaken the route. P309 (package 1)
  is as stated in the brief.

### B6 text (spot check)

* E-5 corrections are present and marked (THEOREM_SRK §2, PHASE1 Theorem L restricted to the order-0 channel,
  SC-SRK reduced from "iff" to "if", O3-N with the full Δ_r). E-8 and E-9 are recorded.
* NOTE (non-load-bearing): SC-SRK keeps "for the maximizing e". R1 flagged this, because Γ̄_i are separate sups over
  e, so the maximizing e is per index. The proposition should say "for each i's maximizing e", or be stated per i.


### Reviewer disclosures (Phase A)

**Exposures.**
* I read only brief-sanctioned files: NS (not EXPOSURE_LEDGER or INCIDENT_*), git metadata and diffs of NS files,
  and the two D_309 modules as imported by the FSM test (not opened).
* I did **not** open THEOREM_TCT.md, tct_rule.py, tc_rule.py, THEOREM_TC.md, THEOREM_AD.md, OPERATOR_AUDIT.md or any
  forbidden file.
* **No 305–309 number was seen.**
* Class disclosure: I saw in-band *drift literals* of two parse-time refusal probes (in the static-scan output and in
  test_verify_selftests.py / run_verify_all.py). They are generic band points and carry no cell quantity.

**Executions** (scratch ledger `scratchpad/r2/reviewer_exec_ledger.jsonl`, 17 lines):
* RD2-0, RD2-1 and RD2-2: no kernel.
* RD2-T: 8 tests through `run()`. The real kernel appears only in the envelope test at E = [1/4, 9/32]; the
  certifier runs on h = 3 only.
* RD2-3: h = 3, degree 8, index 1. Three weight certificates and two verifier calls. The consistent mutant is ledgered
  as `mutant='quarter_weight'`; its proposal patch is not visible in the ledger line.

Nothing was written to the repository except this file. No git write. The coordinator's running processes were not
touched.

---

## 0B. Phase-B reviewer execution declaration (written before any Phase-B run)

Written 2026-09-29 at HEAD `bf5c87c4`, clean tree. No coordinator process is running. The rules are the same as in
§0: `PYTHONDONTWRITEBYTECODE=1`; only `run()` or library calls, never a `__main__` that writes evidence; the q309
exec ledger redirected to `scratchpad/r2/reviewer_exec_ledger.jsonl`; nothing written in the repository except this
file.

| id | what | kernel / geometry / drift | certifier or verifier? |
|---|---|---|---|
| RD2-B1 | evidence-integrity recomputation: JSON reads, sha256 recomputation, `git show <git_head_at_start>:<producer file>` byte hashes, completeness against the declarations, verdict matching by sha256, MC row coverage, re-derivation of the manifest and self-audit claims | none | no |
| RD2-B2 | my RD2-2 gate/adapter probes, re-run against the repaired `srk_gate` / `srk_adapter` (constructed certificates and manufactured consumer objects) | none | no |
| RD2-B3 | NS tests via `run()`: test_srk_gate, test_srk_adapter, test_q309_guard, test_srk_assembly_twosided, test_srk_cert_mutants (synthetic h = 3, k = 1/2, E = [1/4, 9/32], degree 8, including the new consistent-T1 and the verifier) | h = 3 only | yes (h = 3) |
| RD2-B4 | `tests/e2e_cell_family.run(10000)`: in-process verifier on the 32 A2 sub-block certificates (h = 3 cell [1/3, 20/51]; real-kernel cell [1/2, 37/72], hull [1/2, 527/1024]), gate, real-certificate negatives with reasons, and MC at drifts inside those cells | real kernel only at e ≤ 527/1024; h = 3 | verifier only |
| RD2-B5 | independent verifier `verify_cert` (N = 8, max_depth = 24, procs = 1) re-run on committed whole-block certificates: all 5 of real [1, 33/32], all 5 of h = 4 [1, 33/32], and real [0, 1/32] index 4, compared by sha256 with VERIFY_RESULTS.json (genuine certificates only) | real kernel only at e ≤ 33/32; h = 4 | verifier only |
| RD2-B6 | deterministic MC reproduction of a subset of SRK_MC_CONTROL.json rows via `srk_mc_control.simulate` / `he_abs_int`, with the committed seeds (crc32 of `file:i`) and n = 10 000: rows of real [1, 33/32] and h = 4 [1, 33/32] (as many as time allows), compared for exact equality | real kernel only at e ≤ 33/32; h = 4 | no |

No run touches the real kernel at a drift above 33/32, any cell 305–309, or any drift in [6/5, 13/5] or its mirror.

**Amendment to 0B (written before the run it declares).** RD2-B5b: the same verifier call (N = 8, max_depth = 24) on
**all 87** rerun certificates. These are all 11 whole blocks (real kernel e ≤ 33/32, h = 3, h = 4) and the 8 A2
sub-blocks (real-kernel hull ≤ 527/1024, h = 3). Genuine certificates only, compared by sha256 with VERIFY_RESULTS.json.
