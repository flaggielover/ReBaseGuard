# Independent route review: SUCCESSOR_ROUTE_AUDIT_308.md (cell-308 successor route MB-S)
ROUTE_ACCEPTED

Reviewer: reviewROUTE (fresh, independent; wrote none of the reviewed material and reviewed none of it before).
Date: 2026-09-30. Mode: read-only (no mb308 driver mode run, no git write, GIT_OPTIONAL_LOCKS=0 for git reads, no
computation on CUSUM m=5 cells 305-309, no drift in [6/5, 13/5] or its mirror, no target-valued proxy, no estimate of
any route's effect on cell 308, nothing of cell 309 inspected). This file carries no tail figure.

Reviewed object: research branch `p5y-k5-cell308-research`, file
`level4/closure_proofs/p5y_k5_cell308_research/registry/SUCCESSOR_ROUTE_AUDIT_308.md` as of commit `bddd85f8`.

## Work log (incremental)

- Started; read the audit (94 lines), registry r2 (46 lines), the governance determination (131 lines), README,
  HISTORY_308 (sanctioned; figures not copied here).
- Read THEOREM_MB r1 (184 lines); the formal MB r1 protocol (frozen r3, 379 lines), the qualification review
  (QUALIFICATION_ACCEPTED, G1-G5, E1-E8, N1-N8), the driver/stage1 structure (read-only, no mode run), the
  qualification record's Q12 and QC04 entries (non-target: decoy runtimes and determinism booleans only).
- Read the verdict lines and conditions of REVIEW_THEOREM_MB_R1 (THEORY_ACCEPTED_WITH_CORRECTIONS),
  REVIEW_A0_CERTIFIER_R1 (CERTIFIER_ACCEPTED_WITH_CONDITIONS; its note N2 on platform float) and
  INCIDENT_INDEPENDENCE_REVIEW_MB308 (INCIDENT_AUDIT_ACCEPTED; conditions C1-C9).
- Host facts (target-free): python3.14 = 3.14.5 (framework binary mtime 2026-05-10), macOS 26.5.2 (25F84);
  InstallHistory shows no OS or Python install after 2026-09-20 other than XProtect data files.
- Read PRUNING_308 (sanctioned; figures not copied) for the certified vs evidenced status of P0/P1; checked that
  registry r2 (`8da57f89`) is an ancestor of the MB r1 freeze `a7fe3028` and unchanged at `bddd85f8`.
- Read the MB r1 freeze manifest keys, the guard's marker binding, `mb308_stage1.run_job` exception handling and the
  driver's Stage-1/Stage-2 orchestration (read-only).

## Checks

### 1. Route classification (registry r2 + completeness rows): PASS WITH NOTE

Every row of registry r2 (main table and the r2 completeness rows) appears in the audit's matrix, with the same
blocker or logical position: R4 and R9 (data + host), C9-E1 (toolchain/host, U1), RO3 (governance, guard DENY),
CHAIN (not a per-cell quantity; quarantined adjacent cells), X308 (zero closure leverage), TPT/C5-T/LR/B2c (special
cases or internal parts of R-MB). Registry r2 was committed at `8da57f89`, an ancestor of the MB r1 freeze
`a7fe3028`, and is byte-unchanged at `bddd85f8`, so every classification predates the lost run. No refuted or
blocked route is resurrected, and no live route is dismissed by a new estimate of its effect on 308. The audit
creates no new route quantity.

Label defects (none changes the selection):
* **P1 is labelled REFUTED, but only part of its stand-alone infeasibility is certified.** Registry r2 says
  "PRUNED as a stand-alone route (evidenced by committed Monte-Carlo)". PRUNING_308 §4 says the committed facts
  "license neither '308 is closable' nor 'not closable'", and its A0 condition is "certified-undecided". The audit's
  own parenthesis admits that the A0 part rests on an uncertified MC.
  * **The dismissal is still target-free.** It is pruning from committed facts (class PRUNING_FROM_COMMITTED; the
    quarantine allows it; incident review Q4 accepted it as disclosure I-b). It is not a new estimate.
  * **The label is wrong.** It should read "PRUNED as a stand-alone route (EVIDENCED from committed facts; certified
    part per PRUNING_308); its instruments are members of R-MB".
  * **"Subsumed" cannot be claimed in full either.** THEOREM_MB §7 (C2) states the dominance chain only for S_I1 with
    the consumed H_final. Dominance of R-MB over P1 run with a different uniform triple under the frozen consumer
    (whose M then changes) is plausible but not stated.
  * **Why the label matters.** P1 is the only family on C2's consumer path, which is floor r2's adoption path. No
    later reader should take it as certified-refuted.
* **R2 (C1b) is listed as a component, but in MB r1 it supplies no upper bound.** Its ladder is d ∈ {8, 10, 12}.
  Under D5, C1b upper rungs with d > 6 are NOT_INDEPENDENTLY_VERIFIED and are never admitted
  (`mb308_stage1.C1B_VERIFY_MAX_D = 6`; VERIFIER_REPORT D7). R2's role is the Λ_lo alarm and the other-implementation
  lower rung that D5(ii) requires before any C2b rung is admitted. That is a real role, but not a U supplier. The
  exclusion is target-free (verifier cost, fixed before the freeze) and fail-closed (incident review N3).
* **P0 REFUTED is correct.** P-D-a is certified (exact reproduction plus Lemma P0, no MC).
* The catch-all row ("sharper sup / operator norms, other A1/A2 improvements") has no status word. It should carry
  one (IDEA, no instrument) so that the matrix is a closed classification.

### 2. Dominance claim: PASS WITH NOTE

On the scope that matters, the claim is right. R-MB takes the componentwise minimum of every member that is
**implemented, reviewed and qualified at this cell's blocks**: S_I1, Dv′-M on REGISTRY_C1 and REGISTRY_C2, D14-M,
and Lemma G, with the Theorem-M envelope, D_lo′, the TPT-B consumer and the independent layers. P*_B is
nondecreasing in every block constant. Adding a member can therefore only lower Γ_MB (given completion), and
omitting one only forgoes an improvement. Nothing already present is weakened.

The sentence "R-MB is already the strongest host-free, data-free combination" (§2.1, echoing registry r2) is
**overstated as written**:
* By registry r2's own account, C11R-I2 is stdlib (host-free), was reviewed at cell 306, and has implementation
  scope as its only recorded blocker (no data blocker). Added as a further minimum member, it would give a
  combination at least as strong as R-MB. The same holds for COR-T on g_hi.
* The C1b upper rungs (R2) are sound and reviewed, but not admitted (above).

The accurate statement is the audit's own second sentence: R-MB is the strongest combination **among components
implemented, reviewed and qualified at this cell**. The rest is deferred on implementation scope or excluded by the
frozen admission rule. The dominance chain of THEOREM_MB §7 is stated for S_I1 and the consumed H_final; the audit
should not cite it more broadly than that.

### 3. Deferral of C11R-I2 and COR-T: PASS WITH NOTE

The deferral rests on target-free grounds that the record supports:
* C11R-I2 has never run at any block of this cell and is not wired into R-MB (registry r2, written before the
  freeze).
* COR-T would change g_hi, which THEOREM_MB §8 lists as an **unchanged** TC-T input. Including it needs a new theorem
  revision, not just a member.
* Both would need new code, reviews and qualification.
* Either one moves the successor onto the S4 "changed" branch.

**It is not a hidden judgement on effect in the chasing direction.** Both would enter as further minima (C11R-I2) or
as a tighter g_hi (COR-T), so given completion they could only lower Γ. A result-chaser would add them. Keeping the
science unchanged forgoes a monotone improvement in exchange for the determinism property. That is the conservative
direction.

Notes:
* "Breaks the determinism argument" is a reason to **prefer** the S4 unchanged branch, not a prohibition. S4 admits
  changed science with a prior non-target motivation. The audit should phrase it as a preference.
* "Not tonight" is a scheduling remark, not a scientific reason, and should be dropped or marked as such.
* Registry r2 called C11R-I2 "a successor-campaign item", and MB-S **is** a successor campaign. The audit should say
  that it re-defers the item on the S4 ground, not merely cite r2.
* **"Available for a later increment" is not a free option.** Once MB-S has sealed an outcome, adding C11R-I2 or
  COR-T for 308 is a variant selected after an observed result (grant `afa93072`; C4 ruling U6; the cell-306
  no-rerun precedent). Deferring now may foreclose them for 308. The audit must say so, so that the user ruling (S1)
  sees the trade.

### 4. Required elements: PASS WITH NOTE (two elements are incomplete as written; conditions RC1 and RC2)

| element | finding |
|---|---|
| closure mechanism | **present and correct.** Γ_dec = g_hi + max(P*_B, P_hi) < 0 strict and exact, with the member set of D7, as in protocol §2 and the driver's `decide` |
| theorem | **present.** THEOREM_MB r1, THEORY_ACCEPTED_WITH_CORRECTIONS; the corrections are applied, and the formal copy is byte-identical per the protocol |
| implementation plan | **incomplete.** See the first bullet below |
| independent verification path | **present.** F2, F3, `vd_pl`, `vd_verify` and `rlr307_independent`, as in protocol §6. The RLR block certificates remain single-implementation (disclosed) |
| non-target qualification | **incomplete.** See the second bullet below |
| no dependence on the lost result | **present.** No value exists. The runtime-only observations are excluded (S3). Q12's projection behind the audit's "about 4.9 h" is derived from the r3 decoy runtimes (the value implied by `eval_cap_required_s`), not from the target run |

**Implementation plan (RC1).** "Science byte-identical, only infrastructure changes" cannot be implemented as
written, because the boundary is not drawn and part of the science lives in files that must change:
* `mb308_driver.py` holds science logic:
  * D1/D2 geometry (`target_geometry`) and the admitted pairs;
  * the Stage-1 aggregation, which decides which results enter U_i;
  * the VER-job rule for C1b d ≤ 6;
  * the F2 Lemma-Lad check and the INCONSISTENT and INDEPENDENT_CHECK_FAILED raises;
  * `compose_and_consume`, `decide`, the C-A/C-B controls and `prepare_target`.
* `mb308_guard.py` hard-codes `CONSUMED_REF = "refs/p5y-k5-cell308-mb-r1/target-consumed"`. S2 and S7 (a new
  namespace and a new marker) force a change to a file bound in the MB r1 manifest's `helper_sha256`.

**Non-target qualification (RC2).** The determinism argument that S4 requires is **platform-conditional**, and the
audit states it unconditionally:
* REVIEW_A0_CERTIFIER_R1 N2 and R2: "U is reproducible bit-for-bit only on the same platform". The C2b/C1b float
  proposals use libm (`math.erfc`, `exp`) and a float LS/Jacobi step. The persisted certificate, not a re-run, is
  the record.
* QC04 established determinism within one host and interpreter: a ladder pair plus serial vs pooled. It says nothing
  across interpreters or OS builds.
* MB r1 recorded only `python 3.14.5`. It records no interpreter hash, no OS build and no architecture.

Today the platform appears unchanged: the same framework binary, and no OS or Python install since 2026-09-20 per
InstallHistory. The claim "the successor's value is the value the lost run would have produced" is therefore
**probably true now, on this host**. But nothing in the audit binds it, and a new launcher or host contract could
silently break it.

### 5. Known risks: PASS WITH NOTE

The four stated risks are present and accurate:
* **Incident-01 liability, with result-chasing MEDIUM–HIGH.** Matches the incident review Q4 and C3.
* **Single-implementation RLR.** Matches protocol §6.
* **Thin Q12 margins, "about 6 % and 9 %".** Matches qualification review N7: RLR d8 at twice the official max wall
  against its cap, and the projection against Q12's own EVAL_CAP threshold.
* **The runtime of about 4.9 h.** Derived from decoy runtimes (see 4).

Missing or understated:
* **(a) The platform dependence of the determinism argument** (RC2). This is the main missing risk, because S4's
  unchanged branch rests on it.
* **(b) Second consumption and "no retry".** Incident review C9 ("one sealed execution, with no retry") and
  qualification review E7 bind route R-MB itself. MB-S is a second consumption of cell 308 under the same route.
  The audit cites neither. MB-S is admissible only through the governance process (S1, S7), whose determination is
  still under review (REVIEW_SUCCESSOR_GOVERNANCE_308 has no verdict line yet).
* **(c) "The crash-exposure window Phases 5–7 address" overstates what S6 delivers.** S6 as written protects
  against:
  * the death of the hosting app or of the launcher's parent;
  * loss of the **final** result.

  It does not protect against a host reset, kernel panic, power loss or lid sleep in the middle of a multi-hour
  Stage 1. Under S7 any of these is again an INDETERMINATE-class outcome. Two remedies exist:
  * sealed per-job checkpoints with resume. These are deterministic per job, but they are target intermediates on
    disk, so they need a quarantine rule that forbids reading them before the seal, and a frozen resume semantics.
  * an explicit acceptance of the residual window.

  Either must be decided in advance and target-free.
* **(d) Launcher-induced runtime drift.** A new launcher (launchd, detached session, changed QoS or nice) can change
  scheduling and hence runtimes, and the margins are thin. Q12 must be re-measured on decoys **under the successor's
  launcher**, not inherited from MB r1's r3 numbers.
* **(e) The go/no-go decision.** The decision to consume 308 a second time is taken with the runtime-only
  observations of the lost run in view (governance §4.3). Fixing the science removes their influence on the route.
  It cannot remove their influence on whether to run, which is the user's decision. The ruling should see this.

### 6. Other matters, including missed routes: PASS WITH NOTE

* **Missed completeness row: R-MB's own parameters.** Nothing names the most obvious successor variants:
  * the partition N (D1);
  * the RLR/C2b/C1b ladders (D3/D4);
  * the verification budgets (D14), e.g. enough budget to admit C1b d ≥ 8;
  * the D5 admission rule;
  * extra pointwise drifts per block.

  These are the tuning levers of result-chasing. The matrix should carry them as **NOT SELECTED**, for these
  target-free reasons:
  * each is a science change after the loss;
  * S4's changed branch requires a non-target motivation fixed in advance, and none exists;
  * all were fixed by target-free rules before the MB r1 freeze (C2's partition rule, the 307 ladder, A0 rules
    R1–R6, VERIFIER_REPORT D7).

  That MB-S keeps them unchanged is implicit. It should be explicit.
* **Missed row: moving MB-S to another host.** For reliability this would be tempting, e.g. a node without app or lid
  hazards. It would break the determinism argument (RC2) unless cross-platform bit-identity is shown on decoys.
  Record it as EXCLUDED unless RC2 is discharged on that platform.
* **Caps and workers (D11) are unclassified.** They are execution parameters: they gate INDETERMINATE but never enter
  a value, and QC04 shows serial = pooled. The audit should classify them as infrastructure that may be re-derived,
  by the frozen §3.2 rule, from decoy runtimes only (S3).
* **No other legitimate host-free, data-free route family was found missing.** The families beyond the registry are
  covered by R4/R9/RO3 (data/governance), C9-E1 (toolchain) or CHAIN (quarantine).
* **Seal-only recovery of MB r1 is impossible.** Nothing was persisted. It is correctly absent as a route.

## CONDITIONS (binding on the successor; none changes the selected route)

* **RC1. Draw the science/infrastructure boundary before the successor freeze.**
  * List the "unchanged science" by path, sha256 and git blob:
    * THEOREM_MB r1;
    * `mb308_stage1`, `mb308_supply`, `mb308_consumer`, `mb308_a0core` and `mb308_pinned`;
    * the 25 `module_pins`, the 15 `consumer_and_input_pins`, and the F2, F3, `vd_pl` and `vd_verify` pins;
    * the rules D1–D10, D12–D14 and the §8 outcome mapping.
  * The science functions of `mb308_driver.py` (listed in check 4) are either carried text-identical, with a
    function-level source-equality check against the MB r1 driver at `c46434a3` that the qualification runs, or
    each change is listed with an equivalence argument and falls under RC2.
  * The guard changes only in its namespace and marker constants. That diff is independently reviewed.
  * D11 (workers, caps) is classified as infrastructure. It is re-derived only by the frozen §3.2 rule from decoy
    runtimes (S3).
* **RC2. Bind the determinism argument to the platform.**
  * Pin before the marker, refusing on any mismatch:
    * the interpreter path and sha256, the libpython sha256 and `sys.version`;
    * the OS build and the architecture.
  * No OS or Python update between the successor's qualification and its execution.
  * Add a qualification case that re-runs MB r1's committed non-target r3 cases through the successor's code and
    requires exact equality of every certified leaf, timing stripped, with the committed MB r1 r3 records. The cases
    are QC02 (decoy 297), QC03 (decoy 316, blocks 0–2) and the QC04 validation-drift ladder pair.
  * Any mismatch means the science is not "unchanged" in the S4 sense: STOP, and route through S4's changed branch.
  * Qualification review E8 applies. These records are never placed next to any cell-308 quantity.
* **RC3. Governance dependency.**
  * MB-S takes effect only if SUCCESSOR_GOVERNANCE_308 is accepted by its independent review. At the time of this
    review, that review had no verdict line.
  * The audit, by addendum, must cite:
    * incident review C9 ("one sealed execution, with no retry");
    * qualification review E7;
    * the fact that MB-S is a second consumption of cell 308, admissible only through S1 and S7 and disclosed in
      the successor's adjudication.
* **RC4. Audit addendum with corrections (the original kept).** It must:
  * relabel P1 as in check 1;
  * state R2's alarm-only role and the D5 exclusion of C1b upper rungs;
  * scope "strongest" to "implemented, reviewed and qualified at this cell";
  * make the determinism sentence conditional on RC2;
  * phrase the C11R-I2/COR-T deferral as a preference under S4, drop "not tonight", and state the foreclosure
    consequence (check 3);
  * give the catch-all row a status.
* **RC5. Completeness rows.** Add:
  * R-MB parameter variants (D1, D3, D4, D5, D14, extra drifts): NOT SELECTED, with the target-free reasons in
    check 6;
  * moving to another host: EXCLUDED unless RC2 is discharged on that platform.
* **RC6. Risk register.** Carry risks (a)–(e) of check 5 into the successor charter and grant alongside the four the
  audit already names. Decide in advance, target-free, one of:
  * sealed per-job checkpoints with a frozen resume semantics and a read-before-seal prohibition;
  * explicit acceptance of the residual host-reset window.

  Re-measure Q12 on decoys under the successor's own launcher.

## NOTES

* **N1.** Choosing the unchanged science is the conservative, anti-chasing direction. The deferred items could only
  lower Γ given completion, and they are forgone for integrity (check 3).
* **N2.** Registry r2's statuses for R2/R3 ("REVIEW_PENDING", "C3–C5 under review") are superseded by
  REVIEW_A0_CERTIFIER_R1 (CERTIFIER_ACCEPTED_WITH_CONDITIONS) and by MB r1's QC06. The audit's updated wording is
  consistent with the committed reviews.
* **N3.** I did not read the runtime-only observations of the MB r1 target run, any `postexec` content beyond file
  names, or any cell-309 material.
* **N4.** The successor inherits S5's liabilities verbatim. A short incident-independence delta at the successor's
  qualification review is advisable. It would confirm that no exposure beyond the disclosed runtime-only
  observations has arisen since `93058f3a`. It is not required by this review.
* **N5.** HISTORY_308 and PRUNING_308 were read in their sanctioned location. The latter was read with its figures
  masked, and no figure is reproduced here.

## Verdict and reason

**The selection of MB-S is accepted.** It keeps Theorem MB r1, the D7 member set, the ladders, the D5 admission rule,
the TPT-B consumer, F2/F3 and the strict exact criterion unchanged.
* Every alternative is classified on target-free grounds fixed before the MB r1 freeze.
* No refuted route is resurrected.
* No live route is dismissed by an estimated effect on 308.
* The deferrals run against result-chasing, not toward it.

The defects found are:
* overstated labels and wording (P1 "REFUTED", R2's role, "strongest", "not tonight");
* an unconditional determinism claim, which holds only on the same platform (A0 review N2);
* an undrawn science/infrastructure boundary, when the driver and guard hold science logic or MB r1 bindings;
* missing completeness rows and risks.

Each is discharged by RC1–RC6 without changing the route. RC2 and RC3 are load-bearing: without them, S4's
unchanged-science branch is not established, and MB-S has no standing.

Summary of checks: 1 PASS WITH NOTE; 2 PASS WITH NOTE; 3 PASS WITH NOTE; 4 PASS WITH NOTE (RC1, RC2); 5 PASS WITH
NOTE (RC6); 6 PASS WITH NOTE (RC5).

New cell-308 target evaluations by this review: 0. Target-valued proxies: 0. Drifts in the band or its mirror: 0.
Cells 305–309 computed: none. Cell 309 inspected: no.
