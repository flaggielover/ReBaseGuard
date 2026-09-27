# REVIEW_RLR_R2 — independent adversarial review of the RLR route (C_308/LR)

Reviewer: independent R2 reviewer (completes the stalled R1 review). Date 2026-09-28.
Scope: THEOREM_LR.md, lr_fsm.py + C1LR_*.json, cusum/ (c1b_*.py, C1B_ROUTE_SUMMARY.md) + C1B_*.json.
Prior input (untrusted, verified here): reviews/REVIEW_RLR_R1_INCOMPLETE.md and SCR/review_RLR/.
Scratch: SCR/review_RLR2/. Quarantine: no 305–309 quantity, drifts only in declared set, no git writes.

## 0. Status
COMPLETE. Sections 1–4 are the four tasks; §5 conditions; §6 verdict. Evidence: SCR/review_RLR2/ (PROGRESS.md with
declarations RV1, RV2 written before runs; rv2_fsm.py/_out.json; rv2_plant.py/_out.json/.log; rv2_fields.py).

## 1. Mathematics spot-check (task 1)

Reporting rule (QUARANTINE_AMENDMENT_2 R2.3): C1B artefacts carry validation-drift Λ/τ/C_T values (latent proxies).
This review quotes only pass/fail flags, counts and dimensionless synthetic-fixture ratios; no C1B value is quoted.

### 1.1 LR-1 (THEOREM_LR.md:53–91): VALID — agree with R1 §1.1
Re-derived by hand: (K^{k−1}K′K^{n−k}f)(x) = E_x[f(X_n)s(X_{k−1},Z_k); n<τ] needs only the Markov property at k−1, k
and an e-free survival set (so ∂_e K has no boundary term); summation over (n,k) is justified by the majorant identity
(R|K′|R|f|)(x) ≤ ‖W‖²m_1‖f‖ and Fubini; the second-order identity uses M_n²+N_n = Σ(s_k²+t_k) + 2Σ_{j<k}s_js_k and
‖|K″|‖ ≤ m_2 + m′_1 (|s²+t| ≤ s²+|t|). No differentiation under an infinite expectation. The Rao–Blackwell remark
(:86–90) is correct (given the X-path, the Z_k are conditionally independent with laws depending on (X_{k−1},X_k)).

### 1.2 Regenerative decomposition, quotient rule, k_{a,e}′ cancellation: VALID — agree with R1 §1.2
* Quotient terms (THEOREM_LR.md:244–248; THEOREM_AD.md:85): all five terms present; each bounded by Λ·(factor)
  with |ν(f)| ≤ τ_a‖f‖, |ν^{(j)}(f)| ≤ L_j‖f‖ ≤ τ_aρ_j‖f‖. `assemble` (c1b_certpw.py:294–311) implements
  A1 = q1 + Ā_eff δ1, A2 = q2 + 2q1δ1 + Ā_eff(2δ1²+δ2) with q_j = min(Ā_eff ρ_j, L_j/D_lo); the min is sound because
  L_j/D is below both alternatives, and the cross term 2|ν′||D′|/D² ≤ 2(L1/D)δ1 ≤ 2q1δ1.
* Cancellation: Ĝ(I−K̂)1 = 1 and K̂1 + k_a + h1 = 1 give (Ĝh1)(a) = 1 − (Ĝk_a)(a); differentiating the h1 form gives
  D′ = (ĜK̂′Ĝh1)(a) + (Ĝh1′)(a) with h1′ = −K̂′1 − k_a′, so k_a′ enters only through h1′. For CUSUM h1 = Φ(l4) + 1 − Φ(l1)
  (alarm mass, l4 = m−C+e, l1 = C−p+e), so h1′ = φ(l4) − φ(l1), h1″ = l1φ(l1) − l4φ(l4): matches R1 and the
  `residual_forms` d-chain (c1b_certpw.py:99–116; the d2 line uses K̂″ = K̂^(2) − K̂, correct since t = −1).
* **Independent exact check (my code, RV1: `SCR/review_RLR2/rv2_fsm.py` → `rv2_fsm_out.json`).** 9 synthetic exact
  fixtures declared by rule before running (3 two-state toys, 6 seeded random DAG-excursion 4-state chains). Checked in
  Fractions: (Ĝh1)(a) = 1 − (Ĝk_a)(a); D′ (h1 form) = −[(ĜK̂′Ĝk_a)(a) + (Ĝk_a′)(a)]; row a of ∂R and ∂²R equals the
  quotient-rule expansion exactly; Λ = (R1)(a); Σ_y|∂^jR(a,y)| ≤ A_j^RLR(exact ρ) ≤ A_j^Dv′(exact inputs), with L1, L2
  by exact path enumeration. **Result: every check exact/true on 9/9.** Negative controls through the same code:
  dropping h1′ from D′ → detected 6/6 seeds; dropping the 2ν′D′/D² term → detected 6/6 (class (a): the planted
  error breaks an exact identity).

### 1.3 LR-3 "dominance" on equal inputs — R1's nuance CONFIRMED; the headline claim is overstated for certified inputs
* Exact ρ: theorem (THEOREM_LR.md:238–242; L1 ≤ (Ĝ|K̂′|Ĝ1)(a) ≤ κ1C_Tτ_a, likewise L2). Confirmed exactly on 9/9 fixtures.
* Certified ρ: **not a theorem.** Counterexample (RV1, exact arithmetic): with the Cauchy–Schwarz form L1 ≤ √(τ_a Ŝ2)
  — one of the two L1 bounds c1b_certpw takes the min of (`L1_cs`, c1b_certpw.py:274; cusum/PROGRESS.md:83) — the
  certified ρ1 exceeds κ1C_T **with every input exact** on 6/9 fixtures. Two-state toy (a→b w.p. q, unit score):
  (ρ1^CS/κ1C_T)² = 1/(q(1+q)³) > 1 for q = 1/10, 1/4 (analytic and exact). The triangle form L2 ≤ Ŝ2 + T_N has the same
  exposure (per-step weight s²+|t| instead of Dv′'s ‖|K̂″|‖). So raw certified RLR can be worse than Dv′ on equal
  inputs; RLR < Dv′ at the 5 declared drifts and on the block is an **empirical** observation, not LR-3.
* The ρ-level min form (ρ_j := min(certified ρ_j, Dv′ factor), THEOREM_LR.md:241) is trivially ≤ Dv′ (and ≤ the
  constant-level componentwise min, since it can feed the smaller ρ1 into A2's cross term). **It is not implemented:**
  `assemble` returns raw RLR (c1b_certpw.py:297–301) and no code computes min(RLR, Dv′ r2, G); that min exists only as
  prose in the proposed acceptance rule (C1B_ROUTE_SUMMARY.md:259).
* Overstated wording: THEOREM_LR.md:223 heading "dominates Dv′" and C1LR_ROUTE_SUMMARY.md:28 "RLR dominates Dv′ when
  both use the same inputs" — true only for exact ρ (or the unimplemented ρ-level min). THEOREM_LR.md:241 is correctly
  qualified; THEOREM_LR.md:418 ("RLR beats exact-input Dv′ on 24/24 seeds", certified L1/L2) is correctly empirical.
* **Correct statement:** (i) exact excursion ratios ⇒ A_j^RLR ≤ A_j^Dv′ componentwise (theorem); (ii) certified ratios
  ⇒ only min(RLR_cert, Dv′ r2), at ρ level or constant level, is guaranteed never worse than Dv′ r2 (trivially); (iii)
  raw certified RLR carries no such guarantee; "never worse than Dv′" must not be claimed for it.

## 2. Re-verification of attack evidence (task 2)

Declaration RV2 (written in SCR/review_RLR2/PROGRESS.md before running): drift e = 3 only, rung d = 4 (declared set).
Files reviewed are byte-identical to R1's table (sha256 prefixes re-computed: gauss 3189208d6c4c, kernel dfdc871b18ff,
pw db51847c5b56, certpw c506907858a3, float 2a14067cd0c6, negctl aae8d3b4c7eb, THEOREM_LR 59cd350ca201).

### 2.1 My own reruns (`SCR/review_RLR2/rv2_plant.py`, `rv2_fields.py`; `nice python3 -B …`, 24 s + 22 s)
| check | result |
|---|---|
| regenerate e = 3, d = 4 with `CP.certify_degree` (TIGHT_CT as the author) | CERTIFIED |
| exact-field reproduction vs committed `C1B_PW9_POINT_e3.json` rung d = 4 (`CP.EXACT_KEYS`, Fraction equality) | **21/21 equal** (my first attempt reported 0/21 — a reviewer bug: the JSON stores `{exact, float}` dicts; fixed and rerun) |
| **new plant** (not one of R1's): w′ = (1−ε)w_T with ε = dyadic_up(r̄/(1+r̄)) + 2^-20, r̄ = exact upper end of the certified residual at the atom; exact witness `teval` of the w′ residual at (0,0) | witness upper end < 0 (**guaranteed invalid**); `CP.check_supersolution` **REJECTS**; `pointwise_refuted` flag set |
| positive control: unmodified w_T through the same call | accepted |
| **independent point evaluation of the accepted w_T**: residual w_T − 1 − K̂w_T at (0,0), (1/2,0), (0,3), (1/4,1/2) by my own float quadrature of the taboo kernel (window [m−C, C−p] minus atom window, split at kinks and strip crossings; w_T evaluated from its strip polynomials) vs the exact G-form interval | exact lower end ≥ 0 at 4/4; own quadrature ≥ 0 at 4/4; relative disagreement ≤ 1.1e-7 (midpoint-rule level) |

Limits: one drift, one rung, one plant type (supersolution); the quad_check (i′) and block checkers were not re-attacked
by me (R1 did; see 2.2). The point evaluation is float, not rigorous — it is an independent consistency check, not a proof.

### 2.2 Prior reviewer's evidence (read, not rerun except as above)
* `SCR/review_RLR/check_e3_d4.json`: status CERTIFIED; dense exact sampling 2237 points × 21 forms, 0 exact violations;
  float cross-check 205 points, 0 sign violations; plants P_A (A<0 at atom), P_B (tight discriminant, A, C ≥ 0 kept),
  P_C5 (C<0 only at the p-axis end), P_W, P_L: each `witness_valid: true` and `rejected: true`; `all_plants_rejected: true`.
* `check_e3_d8.json` (2237 pts) and `check_block_4.json` (621 pts × 5 drifts in [1/2, 17/32]): CERTIFIED, 0 exact
  violations, 0 float sign violations.
* `rv_assemble_out.json` (RD5, exact recomputation of RLR/Dv′ constants from JSON rationals) and `rv_kernel_out.json`
  (RD1: 21960 closed-form vs own-quadrature comparisons, 0 bad; wrong-ownership control detected) — consistent with R1 §2.
* **RD3b (block plant, `rv_blockplant.py`) has no output file in SCR/review_RLR/: NOT RUN / not completed.** No planted
  certificate has been pushed through the *block* (e_r > 0) checkers by any reviewer.
* R1 findings re-confirmed here: **F1** — `C1B_PW9_POINT_e3.json` rung d = 6 has S2-ladder checks FFF and L1-ladder TFF,
  so C1B_ROUTE_SUMMARY.md:91 "every (i′) checker passes" is false (sound: failed rungs fall back to the tame bound /
  other rungs in the ladder minima; all other rungs at all drifts and the block are TTT). **F2** — summary §8.1
  (C1B_ROUTE_SUMMARY.md:235) pins certpw prefix 0e1465d5, current file is c5069078; output JSONs carry no code hash and do
  not record the `--tight-ct` flag (my 21/21 reproduction needed TIGHT_CT = True).

## 3. Controls and coverage in C1b (task 3)

Read `c1b_negctl.py` (all of main, n2_score, n3_window) and `validation/C1B_NEGCTL.json` (flags only). Classes:
(a) planted input provably invalid (exact witness / exact identity) and pushed through the code under test;
(b) through the code but detection not guaranteed by construction; (d) cannot fail / does not test the code.

| control | through code under test? | class | note |
|---|---|---|---|
| N1 w_T(1−2^-6) (declared D4) | yes (`check_supersolution`) | **invalid control** | Not guaranteed invalid: w_T has residual slack, so the scaled w is a genuine supersolution and its acceptance is *correct* checker behaviour. Author's design error, disclosed and preserved (`logs/C1B_NEGCTL_run1_N1_design_error.json`, PROGRESS.md:141–144), excluded from `all_controls_detected` (c1b_negctl.py:187). Handled correctly. |
| N1′ f = 1/2 (D10, declared PROGRESS.md:145 before rerun) | yes | (a) conditionally | Invalid iff V = w_T − K̂w_T < 2 somewhere; V(atom) is recorded (c1b_negctl.py:153) but the `< 2` condition is **not asserted** in code or in `all_controls_detected`. |
| N1″ tight (D10) | yes | **(a)** | exact residual at x* asserted < 0 (`exact_violation_at_x_star`, c1b_negctl.py:156–158, 188). |
| N2 score sign (FD in e vs K^(1), K^(2)−K̂) | yes (kernel_gf_pw) | (a) for the true-sign bracket; (b) for flip detection | bracket uses interval midpoints (`iv_mid`) and a proved Taylor remainder; flips detected 6/6 points each. |
| N3a atom window not removed; N3b alarm window shifted 1/8 | yes (whole kernel / mutated `KX.ELL`, restored in `finally`) | (a) | mass balance K̂1 + k_a + h1 = 1 must fail by the displaced mass; quadrature reference is the float side. |
| N4 L1 (i′) certificate with a − κ | yes (`quad_check`) | (a) given C(atom) > 0 | κ = 2·C_hi(a)/(k_a+h1)_lo(a) makes C′(a) ≤ −C_hi(a) < 0; positivity of C_hi(a) not asserted. Plants only the C-conjunct. |
| N4b T_N certificate x̃T/2 | yes (`lin_check`) | (b) | no exact witness; large margin. |

**Coverage gaps on the author side** (filled only by reviewers, not by the stream's own committed controls):
1. No author control plants the discriminant conjunct B² ≤ 4AC or a violation confined to a boundary region; R1's
   P_B (tight discriminant, A and C kept ≥ 0) and P_C5 (axis-end only) supply this (§2.2).
2. **No control of any kind exercises the block (e_r > 0) checkers** — neither the author's (point e = 1/2 only) nor
   R1's (RD3b not completed). The block result rests on the same code paths with e as a Taylor variable; R1's dense
   exact sampling of the block certificate (0 violations) is positive evidence, not a negative control.
3. No control on `assemble` itself; covered instead by R1's independent exact recomputation (RD5, exact match) and,
   for the quotient-rule structure, by my FSM controls (§1.2).
4. Declared-before-run discipline is visible (D4, D10 in PROGRESS.md with reasons); the N1 failure was preserved, not
   rewritten. The coverage statement (C1B_ROUTE_SUMMARY.md:204–209: base cover of R, every x-region a box meets) matches
   the code (`quad_check` loops `regions_of_box`; `enclose_t` likewise, c1b_pw.py:120–157).

## 4. Claims vs evidence; route state; freeze binding (task 4)

### 4.1 Claims in C1B_ROUTE_SUMMARY.md / THEOREM_LR / C1LR summary
| claim (file:line) | evidence | verdict |
|---|---|---|
| S1–S4 statements and LR-3 / Dv′ r2 assembly from the same inputs (C1B:15–39) | c1b_certpw.py:179–311; 21/21 exact reproduction (§2.1); R1 RD5 exact recompute | **supported** |
| "All rungs … CERTIFIED … every (i′) checker passes" (C1B:90–92) | e = 3, d = 6: S2 ladder FFF, L1 ladder TFF (§2.2) | **false as worded** (sound: ladder minima use passing rungs/tame fallback). Must be corrected. |
| ρ and A ratios "from the same certified inputs" (C1B:116, :277 G10) | assemble output; R1 RD5 | supported **as empirical facts at the declared drifts**; not a consequence of LR-3 for certified ρ (§1.3) |
| "RLR dominates Dv′" (THEOREM_LR:223 heading; C1LR_ROUTE_SUMMARY:28) | §1.3 counterexample for the certified CS form | **overstated**; true only for exact ρ or the (unimplemented) ρ-level min |
| acceptance rule "combined componentwise with Dv′ r2 and Lemma G" (C1B:259) | no code computes it (c1b_certpw.py:294–311 returns raw RLR and Dv′ side by side) | **prose only**; must be code before a freeze |
| "K̂w is continuous in x … images on strip lines are null sets" (C1B:269, G2 row) | B-piece maps t>1 onto the whole line t′ = t−1 (positive mass); R1 §1.5 N1 | **false reasoning, correct code** (region J = ⌈t⌉ ownership + both adjacent forms checked) |
| code pin certpw 0e1465d5… (C1B:235) | current file c5069078… | **stale**; JSONs carry no code hash and no `--tight-ct`/`--block-light` flag |
| G4 "every JSON is regenerated by its CLI" (C1B:271) | e = 3 d = 4 regenerated exactly (with TIGHT_CT); PW e = 1/4, 1/2 were made by an earlier certpw revision (C1B:236–238) | **partially** supported; provenance gap disclosed by author |
| G5 "all replacement negative controls are detected" (C1B:272) | C1B_NEGCTL.json `all_controls_detected: true` | supported; but no control on the block path (§3) |
| G8 no leakage (C1B:275) | declared drifts only; no cell id in code | supported; **note**: C1B:60 and the tables at C1B:97–112 carry certified/float τ, C_T, Ā, Λ values at validation drifts — the R2.3 latent-proxy content class — yet the file is not on the R2.3/A3 latent-proxy list |

### 4.2 Route state
The author's own state, VALIDATED_NON_TARGET and not FREEZE_READY (C1B:13, :279), is **correct**. With R1 + R2 the
G-gates read: G1 PASS; G2 PASS (independently re-derived; LR-3 dominance restricted to exact ρ); G3 PASS; G4 PASS
with provenance/pin notes; G5 PASS at 5 point drifts + 1 block; **G6 PASS_WITH_NOTES** (two independent reviews;
independent code paths: R1 quadrature/MC/assembly, R2 exact FSM and point quadrature; no second implementation of the
checker; block path never negative-controlled); G7 PASS (D0–D11 declared before runs, per PROGRESS.md); G8 PASS
(with the R2.3 listing note); G9 possible but not yet (see 4.3); G10 empirical at the declared drifts only.
Governance: **CLOSURE-ONLY under floor r2**; no consumer tonight.

### 4.3 Is FREEZE_READY (closure-only certifier) justified now? **No.**
What a freeze would bind (C1B §8.1–8.8) is a reasonable list, but it is not yet bindable as stated:
1. the combined output (min with Dv′ r2 and Lemma G, ρ-level or constant-level) exists only as prose — the frozen
   code would emit raw RLR, for which "never worse than Dv′" is not a theorem;
2. the code pin is stale and outputs do not self-identify (no code hash, no CLI flags such as TIGHT_CT/BLOCK_LIGHT);
3. the statement type a closure would consume is **block-uniform**, yet the block candidate family (e-free vs
   e-affine) is undecided, only one block exists, and **no planted-invalid certificate has ever been pushed through the
   block checkers**;
4. evidence was produced by more than one certpw revision; a freeze needs a single regeneration with the pinned code.
None of these is a soundness defect of the certified numbers; all can be resolved on non-target drifts.

## 5. Blockers / conditions / notes

**Blockers (soundness):** none found. No certified number was shown invalid; every planted-invalid input tried by R1
(P_A, P_B, P_C5, P_W, P_L) and by me (shrink plant, §2.1) was rejected with an exact witness; exact reproduction 21/21.

**Conditions (must be met before the route is called FREEZE_READY or a freeze is prepared):**
* C1 (claims) — reword THEOREM_LR.md:223 and C1LR_ROUTE_SUMMARY.md:28 to the correct statement of §1.3 (dominance is a
  theorem for exact ρ only; for certified ρ only the min with Dv′ is guaranteed); correct C1B_ROUTE_SUMMARY.md:91 (e = 3,
  d = 6 (i′) ladder failures) and :269 (continuity / null-set reasoning).
* C2 (code) — implement the combined supply the acceptance rule describes (ρ-level min with the Dv′ factors, or at
  least the constant-level componentwise min with Dv′ r2 and Lemma G) in load-bearing code, with a test that can fail.
* C3 (block controls) — push class-(a) planted-invalid certificates (supersolution and (i′) quadratic, incl. a
  discriminant-only violation and a violation at an interior drift of the block with an exact witness) through the
  block (e_r > 0) checkers, plus a positive control; decide and declare the block candidate family.
* C4 (provenance) — re-pin all load-bearing hashes; make every output JSON record code hashes and CLI flags
  (TIGHT_CT, BLOCK_LIGHT); regenerate all evidence once with the pinned code.
* C5 (governance) — add C1B_ROUTE_SUMMARY.md (C1B:60 and the tables at C1B:97–112) to the R2.3 latent-proxy list or
  redact those values from anything used as handover text. CLOSURE-ONLY under floor r2 stays binding.

**Notes:** N1′ (c1b_negctl.py:153) and N4 do not assert the precondition that makes them guaranteed-invalid
(V(atom) < 2; C(atom) > 0) — assert it. The author's N1 design error is correctly preserved and excluded. The float
Monte Carlo and float-C_T fairness fields are NON-CERTIFIED context only (correctly labelled). My RV1 fixtures are
synthetic; they test the algebra of LR-3/quotient rule, not the CUSUM kernel.

**NOT RUN by me:** attacks on the (i′) quad_check path, block-path plants, dense sampling (relied on R1's logs,
read and confirmed), Monte Carlo (R1's RD4, read only).

**Quarantine statement for this review:** drifts used: e = 3 (C1b rerun) and synthetic fixtures only (nominal
e = 1/2 guard); `Q.guard_drift` called at every entry; `Q.LEDGER` redirected to SCR/review_RLR2/REVIEW_LEDGER.jsonl;
no cell id, no 305–309 quantity, no tail number read into code or placed next to any value here; no historical module
imported (only this route's `c1b_*` code under test and `NS/code/ov_quarantine.py`); no git writes; no remote hosts.
Only dimensionless ratios on synthetic fixtures, pass/fail flags and counts are quoted (R2.3).

## 6. Verdict

The RLR mathematics (LR-1, regenerative quotient rule, k_a′ cancellation, (i′) certificates, block uniformity) is
valid; the C1b implementation reproduces exactly, rejects every planted-invalid certificate tried, and agrees with
independent evaluations. The route is accepted at **VALIDATED_NON_TARGET, CLOSURE-ONLY (floor r2)**, with G6 now
PASS_WITH_NOTES. **FREEZE_READY is not justified yet**: the "never worse than Dv′" claim is a theorem only for exact
ρ, the combined min is prose not code, the block path has no negative controls, and the pins/provenance are stale.
Conditions C1–C5 (§5) must be met before freeze preparation. No target information is needed for any of them.

ROUTE_REVIEW: ACCEPTED_WITH_CONDITIONS
