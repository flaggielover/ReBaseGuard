# Graph B — K5 CUSUM m = 5 tail: operator-constant chain, and the cell-306 I1 / I2 disagreement

Read-only reconstruction. Worktree `/Users/suzhe/ReBaseGuard-k5ov`, read at HEAD `6735d945` (overnight research stage 0).
HEAD advanced to `cbff958a` during the read (af4365aa, cbff958a — not by this agent); the diff touches only
`p5y_k5_tail_overnight_research/{code,ledger,streams,validation}`, none of the files cited below.
All paths below are relative to `level4/closure_proofs/` unless stated. `file:N` = line N at that HEAD.

**Quarantine kept.** No Python or repository script was executed; only `cat/sed/grep/ls/wc/git log`. No Γ, margin,
enclosure radius, eff factor, critical constant or other derived number for cells 305–309 was computed. Every number
below is quoted verbatim from a committed file (rationals are cited by line rather than re-rendered when no committed
decimal exists). No I1 constant is combined with any I2 constant anywhere in this document.

---

## (a) The operator-constant chain

### a.0 Objects (theorem AD, `p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md`)

| object | definition | source |
|---|---|---|
| state space, atom | X = reachable closure, B(X) sup-norm, a = (0,0) = x0 | THEOREM_AD.md:4-5 |
| atom split (Lemma K) | K_e = K̂_e + k_{a,e} ⊗ δ_a, K̂_e ≥ 0; k_{a,e} + h_{1,e} + K̂_e 1 = 1, h_{1,e} = 1 − K_e 1 | THEOREM_AD.md:19-21 |
| atom window removed from K̂ | z ∈ [β, α] = [m − K, K − p] (non-empty iff p + m < 1); code skips that window / subtracts the "origin" piece | THEOREM_AD.md:26; `taboo_certify.py`:94-100, 148-155; `p5y_k5_tail_c11r_n9_statement_alignment/evidence/table/C11R_N9_STATEMENTS.json`:34-42 |
| κ_n | ‖∂_e^n K̂_e‖ ≤ κ_n := E|He_n(Y)|; κ₁ = √(2/π) < 0.7978846, κ₂ = 4φ(1) < 0.9678830 | THEOREM_AD.md:23-24 |
| κ in the consumer | `K1_BOUND = 7978846/10^7`, `K2_BOUND = 9678830/10^7` (whole-line, same for every supply) | `deflated_consume.py`:55-56; FLOOR_R2_SPECIFICATION.md:95-96 |
| Lemma T | if w ≥ 1 + K̂_e w on X for every e ∈ E: Ĝ_e = Σ K̂_e^j ≥ 0, ‖Ĝ_e‖ ≤ C_T := sup_X w, τ_a(e) := (Ĝ_e 1)(a) ≤ w(a), r(K̂_e) ≤ 1 − 1/C_T | THEOREM_AD.md:32-40 |
| Lemma SM | h_e = Ĝ_e k_{a,e}, ν_e(f) = (Ĝ_e f)(a), p_e = h_e(a), D_e = 1 − p_e = ν_e(h_{1,e}) > 0; (I − K_e)⁻¹f(a) = ν_e(f)/D_e, |ν_e(f)| ≤ τ_a‖f‖; (d) sup_{‖f‖≤1}|[(I−K_e)⁻¹f](a)| = τ_a/D_e = E_a[τ] | THEOREM_AD.md:44-56 |
| whole-kernel supersolution | W ≥ 1 + K_e W on X for every e ∈ E ⇒ E_a[τ] ≤ W(a) =: Ā | THEOREM_AD.md:91-93 |
| C8 reading of SM(d) | "A0 is admissible iff A0 >= sup_{e in cell} E_a[tau]"; a certified LOWER bound on E_a[τ] (Λ) is a floor on A0, never an input to Γ | `p5y_k5_tail_c8_operator_feasibility/config/DECISION_GATE_C8.json`:25; C8 README.md:32-41 |

### a.1 What each constant certifies (per theorem AD §8 and the certifier's own statements)

All six constants are **operator-only** (no source, no candidate of F/D/H, no R value): THEOREM_AD.md:175;
`taboo_certify.py`:1-10. All are **block-uniform** ("for every e in the block"), never pointwise in e.

| constant | exact statement | kernel | direction | how uniform on the block | producer (I1) |
|---|---|---|---|---|---|
| **C_T** | for every e in [e_lo, e_hi]: ‖Ĝ_e‖ ≤ C_T (induced sup-norm of the taboo resolvent), C_T = sup over the reachable cover of a K̂-supersolution w | K̂_e (atom removed) | upper | w ≥ 1 + K̂_e w checked with the affine-in-(e − ec) expansion at **both** block ends plus a κ₂δ²/2·sup w remainder | `taboo_certify.certify_block(full=False)` :200-239, statement :238-239; THEOREM_AD.md:165-166, 171-173 |
| **τ** | for every e in the block: (Ĝ_e 1)(a) ≤ τ, τ = w(a) of the **same** w | K̂_e | upper | same certificate as C_T | same; THEOREM_AD.md:165 |
| **Ā** | for every e in the block: w ≥ 1 + K_e w on X, hence E_a[τ] ≤ w(a) =: Ā | **K_e** (whole kernel) | upper | same affine check, `full=True` | `certify_block(full=True)` :203, :236-237; THEOREM_AD.md:164 |
| **D_lo** | for every e in [e0 − ρ, e0 + ρ]: D_e ≥ D_lo, where D_e = d(a), d = Ĝ_e h_1 = P_x(alarm before reaching the atom) — **conditional on** ‖Ĝ_e‖ ≤ C_T and (Ĝ_e 1)(a) ≤ τ on the same set | K̂_e | **lower** | candidate fixed at e0, residual at e0 (λ_mid), widened to the interval by ρ·env (λ_cell); D_lo = D_mid_lo − ρ·D1_cell | `certify_cell` :284-349; statement :348-349; THEOREM_AD.md:167 |
| **D1** | for every e in [e0 − ρ, e0 + ρ]: |D_e'| ≤ D1, d' = Ĝ(K̂' d + h_1'), same conditionality | K̂_e | upper | D1 = min(|d̃1(a)| + p1(cell), D1_mid + ρ·D2) | `certify_cell` :332-336; THEOREM_AD.md:168 |
| **D2** | for every e in [e0 − ρ, e0 + ρ]: |D_e''| ≤ D2, d'' = Ĝ(K̂'' d + 2K̂' d' + h_1''), same conditionality | K̂_e | upper | D2 = |d̃2(a)| + p2(cell) | `certify_cell` :333; THEOREM_AD.md:169 |
| C_upper (Lemma G only) | C ≥ sup_{e∈cell} ‖(I − K_e)⁻¹‖, the frozen K1 one-sided block bound (whole-kernel resolvent, not taboo) | K_e | upper | cell-uniform, from `cells.json` | THEOREM_TCT.md:22-23 |
| k_i (Lemma G, TC-T premises) | k_i = `cert.norms["k"][i]` ≥ sup_{e∈cell} ‖K_i(e)‖, frozen drift-aware norms | K_e derivatives | upper | cell-uniform | THEOREM_TCT.md:23; `p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_306.json`:61-67 |
| j_i | source-kernel norms in the σ_n Leibniz tower σ_n(r) = Σ C(n,i) j_i ‖h_r^(n−i)‖ — enter p0/p1/p2, **not** A | — | upper | cell-uniform | THEOREM_TCT.md:76-78; TCT_INPUTS_306.json:54-60 |

The I1 cell statement verbatim: "for every e in [e0 - rho, e0 + rho]: D_e >= D_lo, |D_e'| <= D1, |D_e''| <= D2 (given
||Ghat_e|| <= C_T and (Ghat_e 1)(a) <= tau on the same set)" (`taboo_certify.py`:348-349). The C11R statement table
records the resulting **dependency finding**: D_lo, D1, D2 are conditional on C_T and τ, so the six are not six
instances of one statement (C11R_N9_STATEMENTS.json:3-18).

### a.2 How the constants map into A0, A1, A2, and where A binds

**Lemma Dv (r1)** (THEOREM_AD.md:66-72; code `deflated_consume.atom_constants` :83-94), hypotheses on the drift set E:
τ_a ≤ τ, ‖Ĝ‖ ≤ C, D ≥ D_lo, |∂_e D| ≤ D1, |∂²_e D| ≤ D2, ‖∂^n K̂‖ ≤ κ_n:

    A0 = τ / D_lo
    A1 = τ κ₁ C / D_lo + τ D1 / D_lo²
    A2 = τ (2κ₁²C² + κ₂C) / D_lo + 2 τ κ₁ C D1 / D_lo² + τ (2 D1²/D_lo³ + D2/D_lo²)

**Lemma Dv′ (r2) — the rule actually consumed** (THEOREM_AD.md:81-89; `deflated_consume.atom_constants_r2` :97-109;
independent re-derivation `p5y_k5_tail_c2_closure/code/c2_d5_forecast.py`:60-67; quoted verbatim in
FLOOR_R2_SPECIFICATION.md:29):

    Ā_eff := min(Ā, τ / D_lo)              ("eff" in C8/C9)
    δ₁ := D1 / D_lo,   δ₂ := D2 / D_lo
    A0 = Ā_eff
    A1 = Ā_eff (κ₁ C + δ₁)
    A2 = Ā_eff (2κ₁²C² + κ₂C + 2κ₁Cδ₁ + 2δ₁² + δ₂)

with **C = C_T** (the cell's `"C": max C_T` in `deflated_consume.block_for` :166) and κ = the consumer's
K1_BOUND/K2_BOUND. Validation refuses unless τ ≥ 1, C ≥ τ, D_lo > 0, Ā ≥ 1 (`deflated_consume.py`:88-89, 100-101;
`c2_d5_forecast.py`:62-63; C12-R2 driver `validate_set` `p5y_k5_tail_c12r2_cell306_adoption/code/c12r2_cell306.py`:489-494).
C8/C9 state the consequence: "all three are PROPORTIONAL to eff" (`p5y_k5_tail_c8_operator_feasibility/code/c8_chain.py`:21-27;
`p5y_k5_tail_c9_e1_cell307/code/c9_chain.py`:12-15, 72-80).

**Lemma G (registry-free, TC-T)** (`p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md`:20-33; `tct_rule.atom_constants_generic`
`p5y_k5_m5_tail_closure/code/tct_rule.py`:65-76; re-derived in `c12r2_cell306.py`:458-460):

    A0 = C_upper,   A1 = k₁ C_upper²,   A2 = k₂ C_upper² + 2 k₁² C_upper³

(k_i drift-aware norms, not the consumer's κ). These equal the frozen generic K1 DAG rules (THEOREM_TCT.md:35-38).

**Aggregation to a cell.**
- Registry blocks meeting a cell: worst case — max τ, max C_T, min D_lo, max D1, max D2, max Ā (`deflated_consume.block_for` :146-171).
- C2's sub-block registry: the cell row is max C_T/τ/D1/D2 and min D_lo over its sub-blocks (`p5y_k5_tail_c2_closure/code/c2_refined_registry.py`:159-166). Each of the five fields is taken independently (possibly from different sub-blocks).
- Across supplies: `A_j := min over the VALID certified supplies of A_j, componentwise and independently for j = 0, 1, 2` (`p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json`:169; `c2_d5_forecast.combine` :70-76), with per-field provenance.
- S_I1 = min{G, C1, C2}; S_I2 = min{G, I2} (FLOOR_R2_SPECIFICATION.md:90-94; sealed labels `evidence/execution/C12R2_CELL306_RESULT.json`:36, :143 in the C12-R2 namespace).
- The D′ "operator-mixed" supply (componentwise best of the six constants across C1 and C2, then Lemma Dv′; `p5y_k5_tail_c2_closure/phase_d/D_PRIME_OPPORTUNITY.md`:11-29; `c9_chain.py`:83-96) is what C8/C9 call the "current eff" (e.g. 307: "current `eff` **5.597995510441** (binding on `τ/D_lo`)", `p5y_k5_tail_c9_e1_cell307/README.md`:84). It is explicitly **not** part of S_I under floor r2 (FLOOR_R2_SPECIFICATION.md:92-93).

**Where A enters the decision (TC-T → K5-B).**
- Per object r: `rad_r = A0 p2 + 2 A1 p1 + A2 p0`, `half_r = rad_r` (|Ĝ(a)| = 0), with
  `p0 = f_F + ρ f_D + ρ² f_H/2 + ρ³ f_G/6 + ρ⁴ Env4/24`, `p1 = f_D + ρ f_H + ρ² f_G/2 + ρ³ Env4/6`,
  `p2 = f_H + ρ f_G + ρ² Env4/2` (THEOREM_TCT.md:124-126; crosscheck path `tct_rule.py`:268 `halves[r] = rho*aG + Σ C(2,i) A_i p_{2−i}`; frozen path `tail_object` :154-177).
  So **A0 binds on p2 (the order-2 residual f_H + order-3/4 terms), A1 on 2·p1, A2 on p0 (the order-0 residual f_F).**
- Enclosure: R''_m ∈ Σ_{r<m}(1/m)[Ĥ_r(a) ∓ half_r] + Σ c(m)·W (THEOREM_TCT.md:127; `tct_rule.tail_enclosure` :180-210).
- Clause: `Gam = (R_interval.hi − e0·D_interval.lo) + rho·x_hi·M`, `M = M_R2 if a > b else min(M_R2, max(|a|,|b|))`, `[a,b] = [max(H_lo, lo), min(H_hi, hi)]`, pass iff Γ < 0 (`c2_d5_forecast.direct` :79-89; C8 restatement `c8_chain.py`:9-19, 111-129). A enters **only** through [lo, hi] (c8_chain.py:19).
- Committed C2 elasticities (D1 diagnosis, C1 constants): "A0 carries 0.63 of the magnitude response, A1 0.165, A2 0.022" (`p5y_k5_tail_c2_closure/phase_d/D_STAGE_DECISION.md`:47-49).
- On I1 supplies Ā is inert: "on all five tail cells τ/D_lo is the smaller" (C1: `p5y_k5_tail_operator_registry/theorem/C1_OPERATOR_EXTENSION.md`:41-45); C2 docstring "Abar_eff = tau/D_lo on all five cells" (`c2_refined_registry.py`:16-17); D_STAGE_DECISION.md:42 "A0 = τ/D_lo".

### a.3 Certification method (I1 = `taboo_certify.py`, sha `ced9422c…`)

Block certificate (C_T, τ, Ā) — `taboo_certify.py`:
- Float proposal (untrusted): solve (I − M)g = 1 on a tensor Chebyshev grid of the given degree, M = K̂ (taboo) or K (ARL, atom column added) at the block centre ec (:176-197, :82-112); candidate = exact-dyadic Chebyshev payload of α·g + β (`L1.dyadic_candidate`) (:197).
- Certification in Arb at **256 bits** (:56) with the frozen Pair kernel `_kernel_polynomials` (order-120 φ series, `ORDER = RA.TAYLOR_N`) (:52, :57, :136-160); truncation allowance 2·Z_RANGE·sup·(N+1)^i·eps_z doubled for the removed origin piece (:12-15, :157-160).
- Check: for s = ±1, L = w − K̂_ec w − s·δ·K̂'_ec w − (1 + allow) ≥ 0 via `R3C.min_max_on_reachable(…, depth)` (Bernstein range on the frozen reachable cover), allow = trunc terms + δ²/2·κ₂·sup w (:206-226); certified iff margin > 0 and w_min ≥ 0 (:227-228). C_T = upper(max w on reachable cover), τ (or Ā) = upper(w(0,0)) (:225-233).
- Registries: depth 2 (64 patches) (`p5y_k5_tail_operator_registry/evidence/registry_c1/taboo_block_306.json`:8, :15); taboo degree 20, ARL degree 12 (`c1_tail_registry.py`:50-51; `c2_refined_registry.py`:51-52); taboo α ladder (6/5, 13/10, 7/5, 3/2, 2, 3) β = 0; ARL ladder (5/4, 7/5, 3/2, 2, 3, 5) β = 2; first certifying rung taken (`c1_tail_registry.py`:54-61, :93-114; `c2_refined_registry.py`:53-54, :95-99, :126-128). Every tail cell certified at the first rung (C1_OPERATOR_EXTENSION.md:39; C2 306 sub-rows `"taboo_alpha": "6/5"`, REGISTRY_C2.json:214-342; ARL `"arl_alpha": "5/4"` :188).

Cell certificate (D_lo, D1, D2) — `taboo_certify.certify_cell` :284-349:
- Candidates d̃0, d̃1, d̃2: degree-20 **global** tensor-Chebyshev polynomials from a float solve at e0 (`taboo_proposals` :274-281), constant in e.
- Residuals r0, r1, r2 at **e0 only** (Ops(e0)), bounded by `max_abs_on_reachable_fast` at depth 0 plus truncation allowances → λ_mid (:300-315); λ_cell = λ_mid + ρ·env_k with env0 = κ₁S0 + sup|h_1'|, env1 = κ₁S1 + κ₂S0 + sup|h_1''|, env2 = κ₁S2 + 2κ₂S1 + κ₃S0 + sup|h_1'''| (:303-318) — a first-order-in-ρ Lipschitz widening.
- Propagation with the supplied (τ, C): n0 = Cλ0, p0 = τλ0, n1 = C(λ1 + κ₁n0), p1 = τ(λ1 + κ₁n0), p2 = τ(λ2 + 2κ₁n1 + κ₂n0) (:321-327).
- D_mid_lo = d̃0(a) − p0(mid); D2 = |d̃2(a)| + p2(cell); D1 = min(|d̃1(a)| + p1(cell), D1_mid + ρ·D2); **D_lo = D_mid_lo − ρ·D1** (:330-337).
- Audit restatement: `p5y_k5_tail_c11rd_d1d2_extension/docs/D1_D2_STATEMENT_AUDIT.md`:92-117; it also notes the original "used one global polynomial per object and absorbs these kinks [at p + m = 1, 2, 3, 4] in its residual bound" (:125-129).

Partition per registry:
- **REGISTRY_C1**: one block per cell = the cell's own interval, all six constants from one taboo block, one ARL block, one cell artifact at (e0, ρ) (`c1_tail_registry.py`:17-19, :87-134; C1_OPERATOR_EXTENSION.md:14-24).
- **REGISTRY_C2**: N_k = ceil(2ρ_k/(1/100)) equal sub-blocks; per sub-block a taboo block (C_T, τ) and a denominator artifact (D_lo, D1, D2) run **with that sub-block's own C_T and τ** at the sub-block centre/half-width; Ā once per cell (`c2_refined_registry.py`:7-18, :81-134; C11R_N9_STATEMENTS.json:403). Cell 306: 9 sub-blocks (REGISTRY_C2.json:200); 307: 10 (:369); 305: 9 (:31); 308, 309: 11 (:554, :755).
- Provenance defect: REGISTRY_C2 records `c2_refined_registry` sha `4ac24d9e…` (REGISTRY_C2.json:939-942) vs committed file `0d1d8021…` (C9 README.md:74-78; D1_D2_STATEMENT_AUDIT.md:13). N10 (no build host/toolchain/precision recorded) open (`p5y_k5_tail_c2_closure/phase_d/CELL_306_ADOPTION.md`:40-55).

C9 α ladder (cell 307 only): the ladder has no rung below 6/5; 307 certified at 6/5 on all ten sub-blocks with margin lower bounds 0.1608913749747931–0.1663373317598909; certification is affine in w so a block still certifies when c ≥ 1/(1+margin); admissible window α_min = 1.0336884448177213 … 1.2 (`p5y_k5_tail_c9_e1_cell307/evidence/phase4/C9_ALPHA_LEVER.json`:3-8, 24-39; README.md:29-51). Labelled "COUNTERFACTUAL_PROJECTION -- not certified evidence" (C9_ALPHA_LEVER.json:2). Nothing comparable was committed for 306.

C2 non-monotonicity (I1-internal): "C2's refinement improved D_lo, D1 and D2 but made **τ and C_T 1.9–2.9 % worse**, because the degree-20 candidate is anchored at its block's centre and the worst sub-block's centre sits further left" (D_PRIME_OPPORTUNITY.md:27-29; D_STAGE_DECISION.md:39-45).

### a.4 Committed values, cells 305–309

**REGISTRY_C1** (one block per cell; `C1_OPERATOR_EXTENSION.md`:31-37; exact rationals `p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json`:12-109):

| cell | e-interval | C_T | τ | Ā | D_lo | D1 | D2 | τ/D_lo | Ā_eff |
|---|---|---|---|---|---|---|---|---|---|
| 305 | [1.620881, 1.701923] | 6.028953 | 5.291155 | 8.290719 | 0.768609 | 1.618684 | 28.506538 | 6.884064 | 6.884064 |
| 306 | [1.701923, 1.788592] | 5.670984 | 5.070746 | 7.912417 | 0.790892 | 1.519245 | 25.787949 | 6.411423 | 6.411423 |
| 307 | [1.788592, 1.882413] | 5.331527 | 4.851873 | 7.555613 | 0.810385 | 1.448025 | 23.555402 | 5.987123 | 5.987123 |
| 308 | [1.882413, 1.983910] | 5.008961 | 4.633777 | 7.217875 | 0.828872 | 1.377221 | 21.469367 | 5.590460 | 5.590460 |
| 309 | [1.983910, 2.092283] | 4.705512 | 4.418493 | 6.900983 | 0.848046 | 1.284353 | 19.336006 | 5.210202 | 5.210202 |

**REGISTRY_C2** (sha `1b2b8349…`; cell rows `p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json`):
- 305: rationals :12-16, τ :178; committed decimals D_lo 0.821410, D1 0.520713, D2 6.2573, τ 5.391442, C_T 6.197599 (D_STAGE_DECISION.md:36).
- **306**: Ā :181, C_T :182, D1 :183, D2 :184, D_lo :185, τ :347; committed decimals C_T 5.829887954, τ 5.169819806, Ā 7.912416712, D_lo 0.844492286, D1 0.455295982, D2 5.416355434 (`p5y_k5_tail_c11r_n9_statement_alignment/adjudication/ADJUDICATION_C11R_N9.md`:27-32; REVIEW_C11R_COMPARISON.md:108-113).
- 307: :350-354, τ :532; committed decimals τ 4.9520562, Ā 7.5556132 (`p5y_k5_tail_c11_n9_independent_certifier/README.md`:65-68; `tau_worst_sub_block` 4.952056204691856, C9_ALPHA_LEVER.json:39).
- 308: :535-539, τ :733 (no committed decimal found).
- 309: :736-740, τ :934; committed decimals D_lo 0.907807, D1 0.274845, D2 3.1019, τ 4.517254, C_T 4.842907 (D_STAGE_DECISION.md:37).
- Read-off (string identity, no arithmetic): every 306 cell aggregate (C_T, D1, D2, D_lo, τ) equals sub-row 0's value, i.e. the leftmost sub-block [680769/400000, 154039721/90000000] (REGISTRY_C2.json:182-185, 347 vs 203-206, 216). Ā for 306 is the same string in C1 and C2 (REGISTRY_C1.json:32; REGISTRY_C2.json:181). C2 sub-row 4 (the centred sub-block) carries exactly C1's 306 C_T and τ (REGISTRY_C2.json:267, 280 vs REGISTRY_C1.json:33, 49).

**Atom constants per supply** (`C2_D5_FORECAST.json` `supplies`):

| cell | G (Lemma G) A0 / A1 / A2 | C1 (Dv′) | C2 (Dv′) | lines |
|---|---|---|---|---|
| 305 | 7.732565297046676 / 47.694682210498335 / 646.1865340198186 | 6.884064161921174 / 47.612938182348756 / 814.6298812805493 | 6.5636436163891805 / 36.61787494079209 / 456.7966052643967 | 273-285 |
| 306 | 7.230406258255243 / 41.697052649841126 / 531.4670671630953 | 6.411422920029179 / 41.326208144609154 / 665.5436573260256 | 6.121808203299506 / 31.776552901884617 / 372.98795136463804 | 290-302 |
| 307 | 6.6792892997618765 / 35.57778229811774 / 422.1285970238484 | 5.9871227639433435 / 36.16688750611022 / 550.8575787893827 | 5.713585470347228 / 27.578342293398137 / 303.38849424867556 | 307-319 |
| 308 | 6.174137363908812 / 30.393446012323317 / 336.052306022857 | 5.590460453801663 / 31.631571724871883 / 455.61048487373813 | 5.332021179343055 / 23.91517098849144 / 246.74977924152824 | 324-336 |
| 309 | 5.782414324348792 / 26.650741928068 / 277.9282709148853 | 5.210202027997067 / 27.452244760421934 / 372.56264240766563 | 4.976006984918255 / 20.734214118344813 / 201.47627865963835 | 341-353 |

Chosen S_I1 = C2 on all three fields for all five cells (provenance, C2_D5_FORECAST.json:29-32, 61-64, 93-96, 125-128, 157-160; D_STAGE_DECISION.md:51-54 "this registry dominates on 15 of 15 fields"). Cell 306 exact A: C2_D5_FORECAST.json:43-45.
Lemma G range: "A0 = 5.782–7.733, A1 = 26.65–47.69, A2 = 277.9–646.2 on cells 309…305" (THEOREM_TCT.md:39).
C_upper (Lemma G C): 305 `33211115065/4294967296`, 306 `31054358416/4294967296`, 307 `28687329103/4294967296`, 308 `26517718059/4294967296`, 309 `24835280415/4294967296` (`p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json`:4, 109, 214, 319, 424).
Drift-aware k: "k₀ 0.99978–0.99995, k₁ 0.79706–0.79767, k₂ 0.96498–0.96705, k₃ 1.50064–1.50699, k₄ 2.77345–2.79053" vs whole-line [1, 0.79788, 0.96788, 1.510, 2.801] (`measurement_r1/MEASUREMENT_NOTE.md`:60).

**Committed Γ on S_I1 (C2 clause)**: 305 −0.08802906884054082, 306 −0.030469257709306738, 307 0.033132953404317905, 308 0.10270008356594545, 309 0.16224941061997425 (C2_D5_FORECAST.json:15, 47, 79, 111, 143); margins 1.353× / 1.112× / 0.891× / 0.705× / 0.579× (D_STAGE_DECISION.md:14-18). C1-only Γ: 305 −0.065100, 306 −0.005719, 307 +0.061683, 308 +0.136195, 309 +0.198810 (C1_OPERATOR_EXTENSION.md:69-73). Lemma G alone closes only 305 (THEOREM_TCT.md:162-164). ×1.25 on S_I1: 306 +0.029163 (D_STAGE_DECISION.md:67-70). D′ mixed supply for 306: Γ −0.036198, uniform-A margin 1.1555 (`p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md`:497-498).

---

## (b) Cell 306: I1 vs I2

Drift block for 306, both sides: [680769/400000, 17885921/10000000] = [1.7019225, 1.7885921], e0 = 17452573/10000000,
ρ = 108337/2500000 (C11R_N9_STATEMENTS.json:243-262; REGISTRY_C2.json:195-199; C11RD `protocol/C11RD_FREEZE_R1.json`:58-66).

### b.1 The two implementations (floor r2 §6)

| | **I1** | **I2** |
|---|---|---|
| code | `taboo_certify.py` (Arb/FLINT supersolutions, numpy float proposals); REGISTRY_C2 (blob `1a3adfd3`) and REGISTRY_C1 | C11R certifier (C_T, τ, Ā, D_lo: `c11r_idrift.py`, `c11r_boxdata.py`, on C11's `c11_certifier` and C7's `c7_gaussian`) + C11RD (D1, D2); C11RD consumes C11R's F_H as a dependency |
| arithmetic | Arb 256-bit balls, numpy proposals (`taboo_certify.py`:42-56) | exact `fractions.Fraction`; C7 rational Gaussian enclosures (2^-320 outward rounding); C11RD Taylor models order 6 in (u_s, u_θ, u_e), 2^-160 integer scaling, 34 moment terms; CPython 3.14 stdlib only (C11RD_FREEZE_R1.json:156-166; D1_D2_DERIVATION.md:210-223; `c11r_idrift.py`:1-27) |
| source | FLOOR_R2_SPECIFICATION.md:137-141 | same |

### b.2 Per constant: statement, method, partition, value, class

Frozen comparison rule (before results): UPPER — STRONGER if independent ≤ original, AGREES if original < independent ≤ 2×original, else INSUFFICIENT; LOWER mirrored; "SAME STATEMENT BEFORE SAME NUMBER" (C11R_N9_STATEMENTS.json:44-58).

| constant | I1 statement & method | I2 statement & method | statement verdict | I1 value (C2 306) | I2 value | class, ratio I2/I1 |
|---|---|---|---|---|---|---|
| **C_T** | ‖Ĝ_e‖ ≤ C_T ∀e, K̂_e; sup over reachable cover of a degree-20 w; **max over 9 sub-blocks**, each with its own w (C11R_N9_STATEMENTS.json:83-112) | same proposition; F_H: w = A − B·m, A = 3429/500, B = 1113/1000, certified on K̂_e **as one whole-block interval-drift certificate**, depth 5, 32 panels, 363 boxes (C11R_RUNS.json:43-81, 122-126); C_T = `sup_cover_w` = max over cover boxes of the interval evaluation of w (`c11r_certificate.py`:84-85, 162-168) = "3429/500 + 99/2.67e101, outward rounding" (REVIEW_C11R_COMPARISON.md:85-86) | EQUIVALENT (domain EQUAL, premises SAME; aggregation max_over_sub_blocks vs single_certificate_whole_block) (C11R_COMPARISON.json:96-118) | 5.829887954 | 6.858 (+3.7e-97); exact C11R_RUNS.json:303 | AGREES, 1.176351939 (ADJUDICATION_C11R_N9.md:27) |
| **τ** | (Ĝ_e 1)(a) ≤ τ ∀e, K̂_e; w(a) of the same degree-20 w; max over 9 sub-blocks | same proposition; τ = w(a) = A of the same F_H weight (`c11r_certificate.py`:84-85) | EQUIVALENT (C11R_COMPARISON.json:168-190) | 5.169819806 | 3429/500 | AGREES, 1.326545268 (:28) |
| **Ā** | E_a[τ] ≤ Ā ∀e, **K_e**; degree-12 ARL supersolution, α = 5/4, β = 2; single whole-block certificate | same proposition; F_K: **the same weight** w = 3429/500 − (1113/1000)·m certified on K_e (atom not removed), whole block (C11R_RUNS.json:82-120) | EQUIVALENT (C11R_COMPARISON.json:72-95) | 7.912416712 | 3429/500 | STRONGER, 0.866738981 (:29) |
| **D_lo** | D_e ≥ D_lo ∀e, K̂_e, **conditional on (C_T, τ)** of each sub-block; midpoint candidate d̃0 minus τ·λ0 error, minus ρ·D1 mean-value widening; **min over 9 sub-blocks** | D_e ≥ D_lo ∀e, K̂_e, **unconditional**: F_D sub-solution u = α + β·m, α = 101/200, β = 21/250, u ≤ h_1 + K̂_e u on the cover, u ≥ 0, h_min > 0 (certified in the same pass), so u ≤ d and D_lo = u(a) = α; whole block, depth 5, 32 panels (C11R_RUNS.json:3-42; `c11r_boxdata.py`:26-41, 213-236; REVIEW_C11R_COMPARISON.md:82-84) | **STRONGER statement** (premises FEWER) (C11R_COMPARISON.json:144-166) | 0.844492286 | 101/200 | AGREES, 0.597992437 (:30) |
| **D1** | |D_e'| ≤ D1 ∀e, K̂_e, conditional on each sub-block's own (C_T, τ); e-constant degree-20 global candidates, residual at the sub-block centre + ρ·env; D1 = min(|d̃1(a)| + p1(cell), D1_mid + ρ·D2); max over 9 sub-blocks | same proposition, conditional on I2's own C_T = τ = 3429/500 (C11R F_H, exact sup, not C11R's rounded record); **4** sub-blocks; e-Taylor candidates D0(e) = D0 + hD1 + h²/2 D2 + h³/6 D3 about each sub-block centre, **band-piecewise** polynomials (bands p+m ∈ [k,k+1]), residuals enclosed by Taylor models uniformly in e; D1_j = |D1(a)| + |D2(a)|de + |D3(a)|de²/2 + τ(λ1 + κ₁n0) (C11RD_FREEZE_R1.json:68-90, 124-154; D1_D2_DERIVATION.md:164-191; `evidence/runs/C11RD_RUNS.json`:3815-3833, 3838-3890) | EQUIVALENT (domain EQUAL, premises SAME) (`evidence/comparison/C11RD_COMPARISON.json`:24-40) | 0.455295982 | exact C11RD_RUNS.json:16 / C11RD_COMPARISON.json:27 (no committed decimal) | STRONGER, ratio_float 0.45362884480385873 (C11RD_COMPARISON.json:32) |
| **D2** | |D_e''| ≤ D2 ∀e, as above; D2 = |d̃2(a)| + p2(cell) | same proposition; D2_j = |D2(a)| + |D3(a)|de + τ(λ2 + 2κ₁n1 + κ₂n0) | EQUIVALENT (C11RD_COMPARISON.json:41-57) | 5.416355434 | exact C11RD_RUNS.json:17 / C11RD_COMPARISON.json:44 | STRONGER, ratio_float 0.0557333083728129 (:49) |

Further facts:
- Argmax sub-block is the leftmost on both sides: I1 sub-row 0 for all five aggregated fields (a.4 read-off); I2 C11RD "The argmax is sub-block 0 for both" (`review/C11RD_COMPARISON_REVIEW.md`:108).
- F_H and F_K report **identical** `margin_lower_bound` and `w_min_lower_bound` (C11R_RUNS.json:55-56 vs 94-95; "1.293 = A − 5B", REVIEW_C11R_COMPARISON.md:71). Selector: minimise A over a grid of B (grid 1000, b_max 4) by exact ternary search on a convex A_req(B); F_D maximises α over β (grid 1000, β_max 1) (C11R_RUNS.json:200-230; `c11r_boxdata.py`:17-24, 114-140, 242-260).
- I2 kernel box bound partitions in u = z + e (32 panels) and bounds w piecewise per panel; it "over-counts mass by O(W) at the two ends" (`c11r_idrift.py`:275-294). Configuration D5/P32 was chosen by a frozen non-target calibration rule (`config/C11R_POLICY.json`:22-24, 255-258, 290-295).
- C11RD premise: "C_T": "3429/500", "tau": "3429/500", statement "w >= 1 + Khat_e w on R, w = A - B m; hence ||Ghat_e|| <= A and (Ghat_e 1)(a) <= A" (C11RD_RUNS.json:3815-3832); floor r2 residual N1: C11RD used the exact sup, "about 3.7e-97 below C11R's outward-rounded C_T record"; S_I2 uses the outward-rounded record (FLOOR_R2_SPECIFICATION.md:141, 144-145; C12R2_ADOPTION_ADJUDICATION.md:479-480).
- Kernel norms in C11RD: κ₁ = 2φ(0), κ₂ = 4φ(1), upper ends of C7 enclosures (C11RD_FREEZE_R1.json:143-146; exact rationals C11RD_RUNS.json:3810-3813). I1 uses `opnorms.kernel_norm(i)` (`taboo_certify.py`:291).

### b.3 Comparison artifacts and N9

- **C11R comparison** (`2c24a989`; `evidence/comparison/C11R_COMPARISON.json`): classes C_T AGREES, τ AGREES, Ā STRONGER, D_lo AGREES, D1/D2 INSUFFICIENT (NOT_IMPLEMENTED) → **AGREEMENT_INSUFFICIENT** (:27-48). COMPARISON_ACCEPTED `7375b9cd`.
- **C11R adjudication**: **N9_REMAINS_OPEN** (ADJUDICATION_C11R_N9.md:99-106); Q5 explains equal τ and Ā values: "the frozen selector chose the same grid weight … and that one function is a certified supersolution for both kernels" (:68-74).
- **C11RD comparison** (`8e2defab`; COMPARISON_ACCEPTED `90265349`): D1 STRONGER (0.45362884480385873), D2 STRONGER (0.0557333083728129); six-class reassembly (C_T/τ/Ā/D_lo read blob-bound from C11R, not recomputed) → `N9_VERDICT` N9_CLOSED (C11RD_COMPARISON.json:1-14, 23-57).
- **C11RD adjudication** `7d67989d`: **N9_CLOSED** (`adjudication/ADJUDICATION_C11RD_N9.md`:2, 124-139); review **ADJUDICATION_ACCEPTED** `fb237288` (`review/C11RD_ADJUDICATION_REVIEW.md`). N9 is "a trust condition on the constants, not a closure criterion for any cell" (:143-145).

### b.4 Floor r2 and F1′ (`p5y_k5_tail_floor_r2/FLOOR_R2_SPECIFICATION.md`, rule `a15d083b`, REPLACEMENT_FLOOR_ACCEPTED `3fadb422`)

- Old F1 (Γ < 0 under Lemma G) lapsed when N9 closed (:33-43; `p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md`:430-433).
- Rule: base (Γ < 0 on the chosen, single-implementation supply) AND (F1′ OR F2) (:54-72).
- **F1′**: (a) two independent implementations each certified the six constants on the whole drift block; (b) compared under the frozen N9 rule, all AGREES/STRONGER, statements EQUIVALENT/STRONGER, accepted comparison; (c) soundness evidence; **(d) Γ(5, k; S_I) < 0 for EACH of I1 and I2 separately** (:62-69).
- Supplies: S_I = componentwise min over {Lemma G} ∪ {Lemma Dv′ r2 on each six-constant set of implementation I}; S_I1 = C2's adopted {G, C1, C2}; no D′ recombination; κ common (:90-100). No mixing of implementations anywhere; "STRONGER … never substitutes" (:57-60, :79-83, :123-127).
- 306 criterion: control Γ(S_I1) must reproduce C2's `Gamma_exact`; Γ(S_I2) < 0 evaluated once and sealed (:216-231).

### b.5 C12-R2 sealed result (`p5y_k5_tail_c12r2_cell306_adoption/evidence/execution/C12R2_CELL306_RESULT.json`, seal `276f4d41`, EXECUTION_ACCEPTED `1173670f`)

Top-level field names: `cell, consumed_ref, control, cpu_seconds, driver_sha256, finished_utc, floor, floor_r2_table, governance_state_before, grant, identity, input_sha256, m, peak_rss_bytes, python, schema, seal_preconditions, sha256, started_utc, status, target, target_evaluated, target_evaluations, wall_seconds` (:2-147).
- `control` / `target` each hold `cell`, `evaluated{A_exact{A0,A1,A2}, Gamma, Gamma_exact, H_exact[lo,hi], M_after_exact, pass}`, `provenance{A0,A1,A2}`, `supply`; control also `field_matches{A_exact, Gamma_exact, H_exact, M_after_exact, pass, per_supply_records_G_C1_C2, provenance}` and `reproduces_C2_exactly` (:4-37, :121-144). `H_exact` is the TC-T enclosure [lo, hi] and `M_after_exact` the clause M (`c12r2_cell306.evaluate` :568-573).
- `floor_r2_table{F1_prime, F1_prime_a_to_c, F1_prime_d_both_supplies_lt_0, F2, base_clause_Gamma_S_I1_lt_0, floor_r2_satisfied_mechanically, note, scientific_closure{S_I1, S_I2}}` (:42-54).
- **Included:** only the *combined* (post-min) A0/A1/A2 of each supply as exact rationals, their provenance, Γ (float + exact), enclosure endpoints, M.
- **Not included:** the six operator constants of either implementation; the per-supply A tuples (G vs I2 separately); p0/p1/p2, f_F/f_D/f_H/f_G, Env4, rad_r/half_r, per-object or per-term values; magnitude; any degraded (×1.25) Γ.
- Committed values: control supply "S_I1 = min{G, C1, C2}", provenance C2/C2/C2, Γ −0.030469257709306738, pass true, reproduces C2 exactly (:8-12, 19, 30-36). Target supply "S_I2 = min{G, I2}", provenance I2/I2/I2, **A0 = "3429/500"** (:125), A1/A2 exact (:126-127), **Γ 0.005159101140006536**, pass false (:129-143); `target_evaluations` 1 (:146).
- Read-off: the committed target A0 string equals the committed I2 Ā (and τ) string 3429/500 (C11R_COMPARISON.json:75, 171); for I1, A0 is the τ/D_lo branch (a.2). No other decomposition is committed.

### b.6 C12-R2 adjudication and review

- `adjudication/C12R2_ADOPTION_ADJUDICATION.md` (`9c2cbf21`): **CELL306_NOT_ADOPTED** (:2-7). Base TRUE; F1′(a)–(c) HOLD; **F1′(d) FAILS** — Γ(S_I2) sign +1, float 0.005159101140006536 (:219-231, :360-371); a "closure disagreement" under floor r2 §8; F2 FAILS on historical evidence (Γ at ×1.25 on S_I1 = +0.029163; three unreconciled margins 1.1277 / 1.1555 / 1.171431) (:249-262, :492-496). No-mixing verified: "no field of either supply came from the other implementation, and none came from G" (:233-246). Reservation 3: "Non-certification is not non-closure … I2's supply does not reproduce it" (:497-500).
- `review/C12R2_ADJUDICATION_REVIEW.md` (`c5324a78`): **ADJUDICATION_ACCEPTED** (:2); re-verifies supplies/provenance (:180-181) and F1′ (a)/(b) (:153-159).

### b.7 Same statement or different? (per constant)

| constant | verdict | what is the same | what differs |
|---|---|---|---|
| C_T | **same statement** (EQUIVALENT) | K̂_e, sup-norm, ∀e on the identical block, state set R | I1: max over 9 sub-block certificates of degree-20 w; I2: one whole-block linear w. Two I2 renderings exist: outward-rounded record (used in S_I2) and exact 3429/500 (used as C11RD premise) |
| τ | **same statement** (EQUIVALENT) | K̂_e, point value at a, ∀e | I2's w is also a K_e supersolution; binding box outside the atom window ⇒ I2 τ "is exactly the K_e bound" (REVIEW_C11R_COMPARISON.md:214, note N6) |
| Ā | **same statement** (EQUIVALENT) | K_e, point value at a, ∀e, whole block both sides | I1 degree-12 ARL candidate; I2 same linear w as τ |
| D_lo | **different premises** (STRONGER) | lower bound on D_e = d(a), K̂_e, ∀e | I1 conditional on (C_T, τ) per sub-block and built from midpoint candidate + mean-value widening; I2 unconditional linear sub-solution over the whole block |
| D1, D2 | **same statement form** (EQUIVALENT, premises SAME in kind) | K̂_e, |D_e'|, |D_e''| at a, ∀e | the premise *values* differ (each implementation's own C_T, τ); I1 e-constant global degree-20 candidates with first-order ρ·env widening on 9 sub-blocks; I2 e-Taylor band-piecewise candidates with Taylor-model enclosures on 4 sub-blocks |
| Lemma G (C_upper, k_i), κ₁/κ₂, TC-T inputs | **common** to both supplies (FLOOR_R2_SPECIFICATION.md:95-100, 164-166) | — | — |

---

## (c) Committed evidence on WHY I2's constants differ from I1's

1. **Explicitly unattributed.** ROUTE_AUDIT_R1 lists as UNKNOWN: "Which constants drive the I1/I2 disagreement. It is not attributed in committed evidence." (`p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md`:225). The overnight quarantine forbids "per-constant attribution of the sealed 306 Gamma gap by partial substitution" (`p5y_k5_tail_overnight_research/config/TARGET_QUARANTINE.json`:20). Route 306-c ("tighten or repair I2 until Γ(S_I2) < 0") is classed RESULT_CHASING_RISK (ROUTE_AUDIT_R1.md:317).
2. **τ (and C_T) of I2 do not exercise the atom removal.** "the independent tau is only as tight as the K_e bound; the Khat_e structure was not exercised at the binding constraint" (REVIEW_C11R_COMPARISON.md:71); N6: "tau adds no information beyond Abar in value … the independent tau (1.3265× the original) is exactly the K_e bound" (:214). Pre-freeze: the u-panel skip "rarely fires … only boxes near the origin can skip anything. It is sound but nearly inert" (REVIEW_C11R_PREFREEZE.md:185-189); "the Khat_e bound removes only part of the atom mass near the origin … it may leave tau and C_T close to the K_e bound", origin-box removal fraction 0.2017 at D4/P128, 0.4276 at D5/P64 (REVIEW_C11R_PREFREEZE_R3.md:257-260, 407). (No committed fraction for the chosen D5/P32 was found.)
3. **Ansatz shape.** I2's supersolution family is linear, w = A − B·m, and the sub-solution family u = α + β·m is "the simplest non-negative, non-decreasing family … Richer families would give tighter lower bounds; that is out of scope here and recorded as such" (`p5y_k5_tail_c11r_n9_statement_alignment/code/c11r_boxdata.py`:34-41). Non-target evidence: the linear D_lo family's pointwise ceiling α ≤ 0.9748 vs float reference ≈ 0.98, so an earlier "loose" reading was box/panel loss at a coarse configuration, not the family (`evidence/errata/C11R_ERRATA.json`:25-30; REVIEW_C11R_PREFREEZE_R2.md:319-323). Non-target calibration of relative box loss at the chosen D5/P32: metric_float 0.22013017208875502 (normalised by 12 for w, 1/2 for u) on block [5/2, 5/2 + 108337/1250000] (C11R_POLICY.json:22-31). None of these is a target-cell attribution.
4. **Why the linear w shape is plausible at all (cell 307, scalar e = 1.8355, float, NOT LOAD-BEARING):** the true value function of v = 1 + K_e v is "~4.445 at the atom, essentially FLAT in p and decreasing in m … w = A - B*m is feasible at A ~ 4.885" (`p5y_k5_tail_c11_n9_independent_certifier/evidence/crosscheck/C11_CROSSCHECK.json`:2, 146-170; `code/c11_crosscheck.py`:31; README.md:99-100). Different cell and a point drift; no 306 analogue committed.
5. **D1/D2 structural differences (documented, not offered as a causal attribution):** the original "used one global polynomial per object and absorbs these kinks in its residual bound" (D1_D2_STATEMENT_AUDIT.md:125-129); I2's e-Taylor candidates make residuals vanish formally through order 3/2/1 in h "so the sub-block width costs little" (D1_D2_DERIVATION.md:184-191), versus I1's ρ·env first-order widening (`taboo_certify.py`:316-318). I1 itself is strongly partition-sensitive on D1/D2 (306: C1 D1 1.519245, D2 25.787949 vs C2 0.455295982, 5.416355434 — C1_OPERATOR_EXTENSION.md:34; ADJUDICATION_C11R_N9.md:31-32).
6. **STRONGER is not soundness evidence.** "an unsound independent certifier would also show up as STRONGER. D2's ratio of about 0.056 is a large gap" (C11RD_ADJUDICATION_REVIEW.md:261-265); floor r2 §5 (FLOOR_R2_SPECIFICATION.md:123-127).
7. **I1 has its own non-monotonicities.** τ/C_T got 1.9–2.9 % worse under C2's refinement because the degree-20 candidate is anchored at the block centre (D_PRIME_OPPORTUNITY.md:27-29); I1 τ for 307 carried ≈ 0.16 unused certification margin at the first ladder rung (C9 README.md:29-33).
8. **Disclosed residuals, both sides:** N10 open for I1 (no build host/toolchain/precision); I2 independence is implementation-level, not authorship; I2's author saw the original D1/D2 before C11RD's freeze; common-mode model/kernel/derivative-theory/consumer (FLOOR_R2_SPECIFICATION.md:141, 159-166; C12R2_ADOPTION_ADJUDICATION.md:469-483).

**Bottom line for (c):** the committed record documents the statement differences (b.7), the ansatz and configuration of I2, and review notes that I2's τ equals its K_e bound, but it contains **no** attribution of the 306 Γ sign disagreement to any constant or term; that attribution is explicitly recorded as UNKNOWN and is quarantine-forbidden by partial substitution.
