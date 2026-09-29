# Independent route review R1 of SRK (cell-309 research campaign r1)
ROUTE_REVIEW: NOT_READY

**Reviewer:** an independent reviewer subagent with no stake in the outcome. Written 2026-09-29, 15:31–15:55Z, at HEAD
`733129d1`, with the decoy suite and the independent verifier still running.

**Bottom line.**
* **Soundness.** I re-derived the SRK-0 mathematics (whole kernel) and found no soundness defect: Lemmas SK, SV and
  SV′, the Theorem SRK proof, the coefficient-wise min, and dominance by TC-T.
* **Implementation.** It computes what the theorem needs, rigorously. The certificates verify independently (20/20),
  the MC control passes (20/20), and the two-sided assembly and adapter gates work.
* **Why NOT_READY.** The route cannot be frozen yet:
  * The cell-to-drift-block rule is not fixed (B1).
  * Nothing binds certificates to the cell-level Γ̄_i (B2).
  * Qualification evidence is 4 of 11 declared blocks, with no taboo run (B3).
  * Several planned controls are missing or have no power (B4).
  * The taboo certificate format does not bind its kernel (B5, blocking only if SRK-T is to be IN).
* **Scope of the fixes.** Every blocker is target-free and can be fixed without touching 309. A short delta review of
  B1–B4 (plus B5 if SRK-T is wanted) could then turn this into ACCEPTED or ACCEPTED_WITH_CONDITIONS.

---

## 0. Reviewer decoy declaration (verbatim from the first version of this file, written 15:39Z before the runs)

Under the brief's "Allowed running" clause, the reviewer declares exactly these two extra decoy runs. Both use:
* the declared synthetic geometry h = 3, k = 1/2;
* the declared block E = [1/4, 9/32];
* Hermite index 1, degree 8 only (no rung above 8);
* direct calls to `certify_W` / `certify_weight`.

Outputs go to the reviewer's scratchpad. The campaign exec-ledger path is redirected there.

| id | purpose (THEOREM_SRK §8) | run | expected |
|---|---|---|---|
| RD-1 | test 1, too-small weight | whole kernel, `certify_weight(..., mutant="shrink_window")`, JSON via `certificate_json`, then `verify/srk_verify_indep.py` (whole kernel) | REJECT (FALSE), or PROVED TRUE with the proof recorded |
| RD-2 | test 2, taboo instead of whole | taboo kernel (`certify_W(..., whole=False)`), certificate JSON as the producer writes it (no `kernel` key in the hashed body), verified as-is (whole) and with file-level `kernel: taboo` | REJECT as whole; ACCEPT as taboo |

**Timing disclosure.** The declaration was written at 15:39:19Z, and both runs started immediately after it. The
coordinator's commit `dac99268` (15:41:08Z) captured this file after RD-1 had started. The git history therefore does
not by itself show declaration-before-run; only the file-write time and my session do.

**Results.**
* **RD-1.** The shrink-window mutant certificate was **ACCEPTED** by the independent verifier against the *true* κ̄₁,
  so the mutated claim is TRUE there. §8 test 1 as written is therefore not a negative control at this decoy (the
  same phenomenon as erratum SE-1). See item 5.
* **RD-2.** `"kernel" in cert` is false. The same hashed body is **REJECTED** as a whole-kernel claim (C2 disproved
  at an explicit point) and **ACCEPTED** with the file-level `kernel: taboo` key. See B5.

---

## 1. Theorem (THEOREM_SRK §§1–3, §9 A1, §10 A2): PASS (with NOTEs on non-load-bearing text)

| check | verdict | evidence / derivation |
|---|---|---|
| Lemma SK, pointwise kernel bound, including the atom sub-window | **PASS** | See (a) below |
| Box monotonicity | **PASS** | See (b) below |
| Lemma SV: positivity and invertibility, W ≥ 0 premise | **PASS** + NOTE | See (c) below |
| V = R_e g and V − R_eΨ ≥ 0 | **PASS** | I − K_e invertible and V bounded. No sign check on V is needed (THEOREM_SRK.md:65) |
| Pointwise Taylor in B(X) (§3 step 3) | **PASS** | See (d) below |
| Order-3 identity (step 4) | **PASS** | See (e) below |
| Order-4 identity (step 5) | **PASS** | See (f) below |
| Coefficient-wise min (step 6) | **PASS** | See (g) below |
| SRK changes only the order-0 channel term; dominated by TC-T | **PASS** | Steps 1 and 7. p0 and p1 still carry f_G and Env4 unchanged. The adapter re-checks dominance at enclosure level (srk_adapter.py:76–77) |
| Lemma SV′ (e-affine families, A1) | **PASS** | See (h) below |
| Repairs (A1) | **PASS** | See (i) below |
| Refinement rule (A1) affects tightness only | **PASS** | Validity rests only on (a) the cover invariant (split children cover the parent ∩ X; `box_in_X_nonempty` drops only children with no point of X) and (b) rigorous per-box bounds. This matches C1b's rule (srk_certify.py:84–116) |
| Lemma SV-T (A2) | **PASS** | See (j) below |

**(a) Lemma SK.** (K_e f)(x) = ∫_{m−c}^{c−p} f(T(x,z)) φ(z+e) dz, where the window and T are e-free and the atom window
[m−k, k−p] sits inside the survival window. So K_i(e) f(x) = ∫ f(T) (−1)^i He_i(z+e) φ(z+e) dz and
|K_i(e) f(x)| ≤ ‖f‖ ∫_{m−c+e}^{c−p+e} |He_i| φ. The atom part is just the sub-window where T = a.

**(b) Box monotonicity.** The integrand is ≥ 0, and for x ∈ B and e ∈ E the window
[m−c+e, c−p+e] ⊆ [m₀−c+e_lo, c−p₀+e_hi]. The implementation has exactly these corners (srk_envelope.py:113–119).

**(c) Lemma SV.** W ≥ 0 ⇒ K W ≥ 0 ⇒ W ≥ 1 ⇒ K W ≤ θW with θ = 1 − 1/‖W‖. Then ‖K^j‖ = ‖K^j 1‖ ≤ θ^j‖W‖, and the
Neumann series converges to a positive R_e.
* **NOTE.** The W ≥ 0 premise (fix 23e66ba7) is redundant for any positive sub-Markov kernel (K1 ≤ 1), whole or
  taboo. If w_* = inf W < 0, then KW ≥ w_*·K1 ≥ w_*, so W ≥ 1 + w_* everywhere, which contradicts inf W = w_*. The
  premise and the spec check (C1) are harmless.

**(d) Pointwise Taylor.** φ: C → B(X) is analytic and δ_x is a bounded functional, so e ↦ φ(e)(x) is C⁴ with
derivatives δ_xφ^{(j)}. The integral remainder gives (t²/2)·sup_s|φ⁗(s)(x)|. All majorants are bounded and Borel:
κ̄_i^C(x) is a sup over a compact e-set of a function continuous in (x, e).

**(e) Order-3 identity.** φ‴(e₀) = S‴ + 3K₁Ĥ + 3K₂D̂ + K₃F̂ with Ĝ = 0. This follows from the Leibniz rule with
F̃‴ = 0 at t = 0, and matches TCT (P2′). So |φ‴(e₀)(x)| ≤ σ3 + 3s_Hk₁(x;e₀) + … ≤ Ψ3(x), because e₀ ∈ C.

**(f) Order-4 identity.** φ⁗(s) = S⁗ + 6K₂Ĥ + 4K₃(D̂+tĤ) + K₄(F̂+tD̂+t²Ĥ/2); the K₁ term vanishes since F̃‴ = Ĝ = 0.
Env4 with s_G = 0 is identical to `tc_rule.env4` (tc_rule.py:66–71).

**(g) Coefficient-wise min.** R_e is linear and positive, and |φ″(e)| ≤ |φ″(e₀)| + |t||φ‴(e₀)| + (t²/2)M4. Each of
the three nonnegative pieces is bounded separately by two valid bounds, and each bound uses (R_e1)(a) ≤ A0 (true for
any valid A0: take f ≡ 1) and Γ̄_i ≥ sup_{e∈C}(R_eκ̄_i^C)(a). So the min per piece is valid. The coefficients 3, 3, 1
and 6, 4, 1, and ρ²/2, check out.

**(h) Lemma SV′.** Apply SV at each fixed e. Ψ is e-independent, and V_e(a) is affine, so the sup over E is attained
at the endpoints. The implementation checks the residual over X × E with e as a Taylor-model variable; the kernel
G-form is exact in e (srk_certify.py:66–77).

**(i) Repairs (A1).**
* W′ = (1+η)W with η ≥ −r/(1+r) (rounded up) gives W′ − 1 − KW′ ≥ r + η(1+r) ≥ 0.
* V′ = V + λW′ with λ ≥ −r_min + μ·max(1, sup Ψ) (rounded up) gives V′ − KV′ − Ψ ≥ r_min + λ > 0.
* This is pure algebra on certified bounds, so no re-check is needed. The independent verifier re-checks anyway.

**(j) Lemma SV-T (A2).** It follows from Lemma T with K̂ and Lemma SM(c): |R_e f(a)| = |ν_e f|/D_e ≤ v̂(a)/D_lo for
|f| ≤ Ψ. The weight stays κ̄ (it majorizes φ‴, which involves whole-kernel derivatives), which is correct. D_lo must
be certified on every e in the block; see B5.

**NOTEs (text only; none is load-bearing for validity):**
* **N1.** THEOREM_SRK.md:72–73 says "strictly better exactly when the weight is non-constant on the occupation
  support". This is overstated in two ways:
  * Strictness can also come from A0 > sup_E E_a[τ] and from the frozen k_i > ‖κ̄_i‖.
  * "Non-constant" is the wording already repaired in the overnight RSO r1 (N14). The correct condition is Ψ ≠ ‖Ψ‖
    μ-a.e. (dossier/digests/RSO.md, collapse lemma).
* **N2.** §7 (THEOREM_SRK.md:196) justifies the sub-block max as "a max over a cover is valid". That is valid only for
  the *check* (resolvent-drift) variable. The *weight* must stay κ̄ over the whole cell, because B4 needs
  sup_{s∈C}k_i(x;s) and B3 needs k_i(x;e₀). The spec (SRK_CERT_SPEC.md:28, 43) and the code (srk_certify.py:181–189)
  already separate weight block from check block; the theorem text does not. See B1.
* **N3.** §8 (THEOREM_SRK.md:227–228) says real-kernel decoys "e ≤ 1", but the declaration uses [1, 33/32]. Both are
  below the band.

## 2. Phase-1 statements (PHASE1_RESULTS.md): PARTIAL (SRK-P and O3-X PASS; L, SC-SRK and O3-N overstated)

* **Theorem L (ladder, :77–84): FAIL as stated; PASS restricted to the order-0 channel.**
  * RSO-P replaces the derivative terms too: rad_RSO carries 2(N1[…]) + N2[…] from RSO-PM whole-kernel positive
    majorants (dossier/digests/RSO.md §4). The proof compares only the order-0 channels.
  * So "rad^SRK ≥ rad^{RSO-P∘SC}" is unproven when A1/A2 come from deflated supplies (Dv′/RLR). And
    "rad^{RSO-P∘SC} ≥ |exact order-0 image| + 2A1p1 + A2p0" is false in general.
  * Fix: state it for the order-0 channel with common derivative terms.
* **SC-SRK (:91–97): FAIL as an "iff"** (same issues as N1). The "for the maximizing e" clause also breaks, because
  Γ̄_i are separate sups over e. Restate relative to the Λ floor (Corollary RSO-G form).
* **O3-N (:50–52): NOTE.** The "iff" criterion leaves out the f_G and Env4 changes in p1 and p0 (the A1 and A2
  channels). The conclusion "no uniform dominance" still holds.
* **O3-X (:58–66): PASS.** The interpolation bound φ‴_λ = λφ‴_1 + (1−λ)φ‴_0 is exact.
* **SRK-P (:107): PASS**, with a typo: "s = |t − e0|" should read s = |e − e0|. Using ρ inside B4 for s ≤ ρ is valid.
* **Q1 / Q7 / Q8: NOTE.** Q1 is a symbolic restatement of committed records, which I could not verify behind the
  firewall. Q8's "SRK is the residual-specific route" is loose: SRK is structure-specific and candidate-norm-only (see
  item 3).

## 3. Scope claim: PASS (with caveats)

The only source I may read is the quotation as relayed:
* dossier §C row F1 (CELL309_DOSSIER.md:61);
* READER_A_309_HISTORY_REPORT.md:66;
* D309_SUMMARY_AND_NEGATIVES.md:22, which cites C4_ADJUDICATION.md:201–203.

It says F1 holds TC-T fixed and `does_not_cover` "residual-specific (non-norm-only) order-0 bounds; any change to
TC-T, the clause or the inputs; order-3 candidates". SRK replaces TC-T's order-0 channel term with a non-norm-only
bound, so it is outside F1 on two named clauses. The C3 knockout and F2 hold TC-T and the [H_lo, H_hi] input fixed,
so SRK is outside those too.

Caveats:
* I cannot check the quotation against C4 itself.
* Only the κ̄-weighted kernel-derivative parts of B3 and B4 leave F1. The terms A0·f_H, A0·(σ3+ε3) and A0·σ4 are
  still uniform-A0 terms, floored by Λ (degenerate case D2).
* With a constant weight, SRK collapses to an F1 member (the RSO collapse lemma).

## 4. Implementation: PASS for what exists; gaps listed as blockers

**Port (srk_kernel.py vs c1b_kernel.py): PASS.**
* The line-by-line diff shows the mathematics unchanged, with constants moved to `Geom`.
* `kd` now also covers the ELL constants. This is a no-op for all declared geometries, where c and k have dyadic
  exponent 1.
* `_BIN` was enlarged, an unused line in `_Gn` was dropped, and the Fraction path, H1 and KA were removed.
* `test_srk_port_identity` gives 84/84 identical.
* My added checks: `base_cover` for h ∈ {1/8, 1/4, 1/2}, `regions_of_box`, `split_box` and `box_in_X_nonempty` are
  identical to C1b (the identity test does not cover these).
* NOTE: `c1b_gauss` is imported by `sys.path.append` (srk_kernel.py:32). Pin it by hash in any freeze.

**Envelopes (srk_envelope.py): PASS.**
* The antiderivative −He_{i−1}φ is correct.
* Root brackets √3 and √(3±√6) are rigorous, via directed isqrt. The width is 2·2^-40, not the documented ≤ 2^-40;
  this is only a doc slip.
* The bracket bound width·sup|He_i|·φ(0) is valid, and the pieces between brackets have constant sign.
* The box corners are correct.

**Certifier (srk_certify.py): PASS on soundness**, covering:
* the e-affine G-form;
* both repairs (item 1(i));
* the cover invariant and refinement rule;
* Γ = max of the endpoint values V′(a), in exact arithmetic;
* min over rungs;
* the weight-block ⊇ check-block check (:187–188);
* guards on both blocks (:189–192).

Robustness gaps:
* `certify_weight` does not check that `Wrec` is CERTIFIED, or that it was certified on the same block, e_c and
  kernel (:181–205). This is safe only because the independent verifier re-checks W.
* Executions are logged only in `run_block` (:225); `certify_W` and `certify_weight` are unlogged. This is the cause
  of the retroactive ledger lines 10–12.
* `certificate_json` omits `kernel` and hard-codes "(whole kernel)" in `claim` (:258–280). See B5.
* Evidence files carry no producer code hash.

**Assembly and adapter: PASS.**
* `srk_assemble` equals the theorem exactly, and my own derivation agrees.
* The adapter reproduction gate requires `rad` = recomputed TC-T radius, `half` = rad, and an exact re-assembly
  equal to the frozen (lo, hi). Field mapping to `tct_rule.tail_object` has been checked: f_G includes eps_src[3],
  σ3 is the midpoint-tower value and σ4 the cell-tower value.
* NOTE: dominance in `rad_srk` is an `assert` (srk_assemble.py:98), which is stripped under `-O`. Make it a refusal.
* The adapter trusts `gamma` (srk_adapter.py:55–73). See B2.

## 5. Tests with power: PARTIAL

I ran all of these through a wrapper that calls `run()`, so no evidence files are written.

| test | result | power assessment |
|---|---|---|
| test_q309_guard | PASS | Refusals fire. **NOTE:** the static scan (q309_guard.py:187) matches only calls literally named `Fraction`. The codebase aliases it as `F` / `Fr`, so `F(9, 5)` is not detected (probe in scratchpad; srk_verify_indep.py:121 `Fr(6, 5)` passes unflagged, legitimately). The runtime guards are the load-bearing part |
| test_srk_port_identity | PASS 84/84 | Exact equality, so power is high; cover functions were added by me |
| test_srk_envelope | PASS 240/240 | The sandwich catches my 3 bracket and sign mutants. **Two box-corner mutants of `box_envelope` (p₁ for p₀; e_lo for e_hi) PASS undetected.** The "planted shrink" (:38–43) only checks shrunk < full, which is always true, so it is vacuous as a control |
| test_srk_assembly_twosided | PASS; 10/10 mutants; 5/5 refusals | Exact disagreement with the independent recomputation, and the battery includes raw > old. M2 is covered here, as the brief notes |
| test_srk_adapter | PASS 6×20 | Tamper, Ĝ ≠ 0 and wrong coefficients are refused for the right reason (reproduction gate) |
| test_srk_fsm_truth | PASS (genuine) | See the bullets below this table |
| srk_mc_control (n = 10⁴) | PASS 20/20 | See the bullets below this table |

**test_srk_fsm_truth.**
* Genuine checks and premise-level truth all hold, with Γ/truth between 1.002 and 1.037 on the FSM.
* **Mutants:**
  * M1 is caught 12/12, at premise level only: the right reason.
  * M2 is not applicable (0/12).
  * **M3 is caught 0/12**, so it is vacuous.
  * M4 is caught 6/12. The other 6 are inapplicable (σ3 = 0 for degree-2 sources), but this is not reported.
* **The exit status ignores mutants** (test_srk_fsm_truth.py:126–130).
* PHASE3:12 and the f0dbaa79 message ("premise-level controls with power") overstate this.

**srk_mc_control.**
* The worst z-score (Γ − MC)/se is +1.35 standard errors, so the control can fail.
* Γ/MC lies between 1.01 and 1.39 (decoy-only ratio).
* It uses a 1/32-grid envelope ≥ κ̄, so it is conservative.

**§8 planned tests.**
* **Test 1 (too-small weight).** Vacuous at RD-1: the mutant claim is TRUE. Its intent is covered by spec mutant 5
  (index+1), which is disproved in 16/20 cases (i ≥ 1). Amend §8 in the manner of SE-1.
* **Test 2.** Evidenced only by my RD-2.
* **Test 8 (constant weight vs Ā at the same rung).** Asserted nowhere. On one decoy, Γ₀/Ā_W is slightly above 1:
  Γ₀ is looser than the trivially valid V := W. This is a tightness matter, but a control that "can fail" needs a
  defined criterion.
* **Test 10 (byte-identical rerun, JSON round-trip).** Not tested, although the suite's resume relies on it
  (srk_decoy_suite.py:52–57).
* **SE-1.** Logically necessary: the verifier *proved* the ×(1−2⁻⁸) claims true, so this is not result-chasing. The
  ×3/4 replacement is coarse.

## 6. Decoy evidence and independent verification: PASS for what exists; incomplete

* **Declaration.** Committed in f0dbaa79 at 13:44:15Z, before the first ledgered real-geometry `run_block`
  (13:45:34Z). Caveat: a real-kernel direct-call probe at E = [1/2, 17/32] was ledgered only retroactively (lines 10–12).
  Its correction dates the declaration commit "13:3xZ", which contradicts git (13:44:15Z), so its order relative to
  the commit cannot be verified. Impact is low: it was a declared, out-of-band block.
* **Evidence present at review time.** 4 of 11 declared whole-kernel blocks:
  * real [1/8, 5/32], [1/4, 9/32] and [1/2, 17/32];
  * synthetic h = 3, [1/4, 9/32].

  All 3 rungs certified on each. The files predate the `weight_block` and `kernel` keys, which default to the block
  and to whole. There are no h = 4 blocks, no real [0, 1/32] or [1, 33/32], and **no taboo family**.
* **Independent verifier** (VERIFY_RESULTS.json; working tree and dac99268):
  * **20/20 ACCEPT**, with 415/415 mutant expectations met, 20/20 unit self-tests, and no REJECT or unproven result;
  * independence is claimed, and no producer import was found;
  * the method differs (prisms, order-8 Taylor models, e′-sampling with a C^{1,1} bound), and I find it sound.
* **Verifier coverage gaps.**
  * It does not cover Lemma SV′ or the assembly (by design; this review covers them).
  * No genuine certificate with weight_block ⊋ block has been verified (only the negative self-test).

## 7. Target independence and temporal integrity: PASS with NOTEs

**Git order.** The charter and quarantine (52e00290, 12:58Z) come first. Incidents 309R1-01 and 309R1-02
(13:02Z, 13:06Z) precede THEOREM_SRK (13:15Z). Both are disclosed in the theorem header, the dossier §G, the route
matrix R16 and Phase 3.

**Selection rule.** ROUTE_SELECTION_RULE (7f1eb363, 13:52Z) precedes Phase 3 (d627960b, 13:58Z). It is target-free
in form.
* NOTE: its C4 threshold ("BLOCKED" only) was set by the exposed coordinator after both liabilities were known. That
  threshold puts TPT OUT and SRK IN, so it is a user matter (G1).

**Band drift.** No band drift appears in ZERO_TARGET_LEDGER: every drift is ≤ 33/32. Line 17 is a parse-time refusal
probe in which nothing was evaluated. The static scan passes, with the blind spot noted in item 5.

**Parameters.**
* The ladder {8, 10, 12}, cover width 1/4 and 4 extra levels are inherited from C1b.
* μ = 2⁻²⁰ and N_E = 4 are fixed in §7. A1 is driven by synthetic profiling.
* None references 309, **but** the E = C versus 4-sub-block choice and the dyadic hull are not fixed (B1).
* Unlisted implementation constants (KT = 10, rounding bits 24/40/96, 3 extra levels in `poly_min_X`
  (srk_certify.py:123), which differs from §7's 4) are tightness-only and must be pinned.

**Push authorization.** README.md:9 says "not pushed unless the user authorizes", while checkpoint_push.py:1 pushes
under a "standing preservation authorization". Record that authorization in the charter (G5).

## 8. Readiness for a formal, closure-only, exactly-once 309 campaign

### Science and implementation blockers

**B1. Cell-to-block rule.** Fix it in THEOREM §7, target-free, before any 309-related number.
* The drift set: E = the dyadic outward hull of C on a fixed grid. The certifier refuses non-dyadic endpoints
  (srk_certify.py:221–222), and K1 cell endpoints need not be dyadic.
* One of: E alone, N_E = 4 sub-blocks, or the min of both (valid).
* For sub-blocks, weight_block = E for every sub-block (N2).

**B2. Γ-binding gate.** Nothing turns certificates into cell-level Γ̄_i with exact checks. It needs to check:
* geometry (5, 1/2) and hermite index;
* union of check blocks ⊇ C, and weight_block ⊇ C;
* the kernel;
* a **mandatory independent-verifier ACCEPT**, else Γ̄_i = +∞;
* max over sub-blocks and min over rungs.

Build it and qualify it on decoys, including a genuine weight_block ⊋ block certificate verified independently
(positive control) and a weight-too-narrow negative.

**B3. Qualification evidence.**
* Complete all 11 declared blocks, with verifier and MC on each.
* Record the producer code sha in every evidence file.
* Bind the evidence to the code that will be pinned. The present files come from pre- and post-464494e8 code states
  and a restarted suite.

**B4. Controls with power.**
* Add a point-sampled containment test for `box_envelope`.
* Make the FSM exit status require M1 = 12, M4 on every applicable case (with applicability reported), and M3
  replaced by a truth-catchable mutant.
* Implement §8 tests 2, 8 (with a stated criterion) and 10.
* Amend §8 test 1 as SE-1 was amended.
* Log executions at `certify_W` / `certify_weight`.
* Replace the `assert` in `rad_srk` with a refusal, and check `Wrec` block, e_c, kernel and status in `certify_weight`.

**B5 (only if SRK-T is to be IN).**
* Put `kernel` in the hashed certificate body and make the `claim` text follow it. RD-2 shows the same hash yields
  opposite verdicts under the unhashed key.
* Run the taboo decoy family.
* Fix a D_lo block rule (the registry's D_lo must be valid on the whole block E).

Otherwise SRK-T stays OUT, which is safe.

**B6 (text).** Fix N1–N3, Theorem L, SC-SRK and O3-N (item 2), and the PHASE3 "12/12 with power" wording.

### Governance (user decisions)

* **G1.** Explicitly accept SRK's motivation-provenance liability, **MEDIUM-HIGH**. It comes from 309R1-02 (an
  in-band estimate during ideation), 309R1-01, and programme-wide dominance knowledge. This includes rule S's
  "BLOCKED-only" C4 threshold.
* **G2.** Authorize a separate closure-only, exactly-once campaign. It includes new Stage-1 operator certificates at
  309's drift block, which are forbidden here by the quarantine.
* **G3.** Confirm RLR as the min-composed A1/A2 component. It needs its own 309 Stage-1 blocks by the frozen C2 rule
  and carries the 307 disclosures.
* **G4.** Accept the disclosed uncertainty about when the real-kernel probe ran (item 6).
* **G5.** Record the push authorization in the charter (item 7).
* **G6.** Ledger the reviewer exposures listed below. Future briefs should exclude THEOREM_TCT.md:39: the allowed range
  1–62 carries 305–309 atom-constant ranges.

### Formal-campaign items (not blockers of this review)

* **Freeze package.**
  * Pinned hashes: the srk_* modules, c1b_gauss, the verifier, the spec and the theorem.
  * A frozen parameter file: ladder, cover, levels, μ, KT, rounding, and the B1 rule.
* **Stage-1 driver.**
  * A grant-scoped band guard that replaces q309, whose import guard also blocks `tct_rule` / `tc_rule` by name.
  * Deterministic outputs.
  * Failure semantics fixed in advance: Γ̄_i = +∞, which falls back to TC-T, with no retry.
* **Stage 2.**
  * The pinned `tct_rule.tail_enclosure` loaded by bytes (load_frozen).
  * The adapter reproduction gate and dominance check, then the frozen direct clause.
* **Exactly-once machinery.** Grant, seal, sandbox qualification (307 precedent), and independent execution and
  adjudication reviews.

---

## Reviewer disclosures

**Exposures** (all brief-sanctioned reads; no 305–309 number is reproduced here):
* THEOREM_TCT.md lines 1–62: line 39 carries Lemma-G atom-constant ranges on cells 305–309, and line 12 the tail drift
  domain;
* the `tct_rule.py` docstrings: tail drift range, one endpoint magnitude;
* the content-class field of EXPOSURE_LEDGER.jsonl, read programmatically: one class names the tail drift range.

No Γ, margin, radius share or verdict value was seen. I did not open any other file outside the brief's list.

**Executions** (none on the real kernel at a drift above 33/32; nothing written to the repository except this file):
* all listed tests through `run()`, with PYTHONDONTWRITEBYTECODE;
* the read-only static scan;
* in-memory envelope mutants;
* a scan alias probe (scratch file);
* RD-1 and RD-2 (h = 3, degree 8).

The q309 exec-ledger was redirected to the scratchpad (`reviewer_exec_ledger.jsonl`), so these runs are not in
ZERO_TARGET_LEDGER. The coordinator may transcribe them.
