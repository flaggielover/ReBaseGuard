# Digest: real order-3 theory, higher-order audit (structure), B_307 summary, Theorem TC-T (symbolic), order-3 producer and readiness READMEs

Firewalled digest. Sources:
* NS = `level4/closure_proofs/p5y_k5_tail_overnight_research/`: `streams/B_307/REAL_ORDER3_THEORY.md`,
  `streams/B_307/HIGHER_ORDER_AUDIT_307.md` (structure only), `streams/B_307/B_307_ROUTE_SUMMARY.md`.
* `level4/closure_proofs/p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md` (symbolic only).
* READMEs of `p5y_k5_cusum_order3_producer_design`, `_r2_repair`, `_r3_infrastructure`, `_r4_tightening`,
  `_real_producer`, and `p5y_k5_order3_readiness_audit`.
* For N1/N3/N5/N7 definitions: `p5y_k5_m5_tail_closure/CAMPAIGN_A_OPEN_NOTES_DISPOSITION.md` and
  `p5y_k5_tail_c2_closure/OPEN_NOTES_DISPOSITION_C2.md`.
Redaction tokens: `[TAIL-NUMBER REDACTED]`, `[TAIL-COMPARISON REDACTED]`, `[LATENT-PROXY REDACTED]`.
THEOREM_TCT, HIGHER_ORDER_AUDIT §0, B_307 summary per-cell §0, the readiness README §4 and the two notes files contain
committed tail numbers; none is reproduced. Kept numbers are synthetic fixtures (FX_A, FX_B), the declared Gaussian
drifts, lower-front cells 11–44 (e ≈ 0.006–0.025), or generic.

---

## 1. Theorem TC-T (THEOREM_TCT.md) — symbolic

Status: written from the measured adopted inputs of cells 305–309 and no new real scientific value. Theorem TC
(`p5y_k5_lower_front_order3/theorem/THEOREM_TC.md`, adopted at `3c1c6b9c`, module pin `tc_rule.py` `8d402d11…`) is
reused **verbatim**: its setting §1, premises (P1)–(P3), statement §3 and proof §4 are unchanged. TC-T replaces exactly
two premise supplies (because the tail drift domain [TAIL-NUMBER REDACTED] admits neither of the lower-front ones) and
sharpens a third from adopted evidence.

### 1.0 What changes vs the lower front
| theorem-TC premise | lower front (cells 11–44, e ∈ [0.0089, 0.0252]) | m = 5 tail (cells 305–309) |
|---|---|---|
| (P4) atom constants A0, A1, A2 | adopted certified operator registry r1 (`1b7f5da7…`) via Lemma Dv′ | registry r1 certifies only e ∈ [0, 0.1147] — no coverage. Replaced by **Lemma G** |
| Ĝ (order-3 candidate of F) | frozen order-3 producer's degree-12 candidate, one certified real evaluation per (cell, r) | **Ĝ := 0**, a legal fixed function; no real evaluation. Premise **(P2′)** |
| σ3, σ4 (true source derivative sups) | frozen J/h Leibniz tower | tower **intersected with adopted Aux3 order-3 source and h evidence**. Premise **(P3′)** |
Everything else (frozen K1 candidates, residuals and drift-aware norms, frozen W enclosures, assembly table, K5-B
consumption rule) is adopted machinery, unchanged.

### 1.1 Lemma G (registry-free atom constants) — verbatim-close
Let C := `cells.json[cell].C_upper` (frozen K1 one-sided block bound, C ≥ sup_{e ∈ C} ‖(I − K_e)⁻¹‖ on the cell) and
k_i := `cert.norms["k"][i]` ≥ sup_{e ∈ C} ‖K_i(e)‖ (frozen drift-aware norms, TC (P1)). Then for every e ∈ C, f ∈ B(X):

    |[R_e f](a)|    ≤ A0 ‖f‖,   A0 := C
    |[∂R_e f](a)|   ≤ A1 ‖f‖,   A1 := k₁ C²
    |[∂²R_e f](a)|  ≤ A2 ‖f‖,   A2 := k₂ C² + 2 k₁² C³

*Proof.* |[Rf](a)| ≤ ‖Rf‖ ≤ C‖f‖. With ∂R = RK₁R and ∂²R = 2RK₁RK₁R + RK₂R (theorem AD §4; R_e exists and is analytic on
C by (P1) and the invertibility asserted through C_upper), submultiplicativity gives ‖∂R‖ ≤ C k₁ C and ‖∂²R‖ ≤
2Ck₁Ck₁C + Ck₂C; evaluation at a is bounded by the sup norm. ∎
These are exactly the constants of the frozen generic K1 DAG rules `eps(F) = C f_F`, `eps(D) = C(f_D + k₁ eps(F))`,
`eps(H) = C(f_H + k₂ eps(F) + 2 k₁ eps(D))` rewritten as A0 f_H + 2A1 f_D + A2 f_F — Lemma G asserts nothing the adopted
K1 stack does not already assert. Lemma Dv′ is strictly sharper where a certified registry exists; Lemma G needs none.
(Numerical ranges of A0, A1, A2 on the tail: [TAIL-NUMBER REDACTED].) TC's proof uses (P4) at exactly one place (§4
step 3, `|E''(e)(a)| ≤ A0‖φ''(e)‖ + 2A1‖φ'(e)‖ + A2‖φ(e)‖`); Lemma G supplies it.

### 1.2 Premise (P2′) — the zero order-3 candidate (the Ĝ := 0 convention)
TC §1 lets F̂, D̂, Ĥ, Ĝ be four fixed functions; nothing requires Ĝ ≈ F_r'''. Take **Ĝ := 0**; the Taylor candidate is the
quadratic F̃(e) = F̂ + tD̂ + (t²/2)Ĥ. TC's (P2) identity at e0 reads

    φ'''(e0) = −[(I − K)·0 − K₃F̂ − 3K₂D̂ − 3K₁Ĥ − Ŝ'''] + (S''' − Ŝ''') = S'''(e0) + 3K₁Ĥ + 3K₂D̂ + K₃F̂

so with σ3 ≥ ‖S_r'''(e0)‖,

    f_G := 3 k₁ s_H + 3 k₂ s_D + k₃ s_F + σ3      satisfies  ‖φ'''(e0)‖ ≤ f_G,

and the two other order-3 inputs vanish exactly: **s_G = 0** (‖Ĝ‖ = 0; (P3)'s envelope loses every s_G term) and
**|Ĝ(a)| = 0** (the centre-motion half-width ρ|Ĝ(a)| is zero; the enclosure stays centred on the adopted order-2
candidate Ĥ_r(a)). The implementation adds the adopted `eps_src[3]` = ε_mid(src(r,3)) on top of f_G (valid extra
allowance; keeps the frozen `tc_rule` field semantics `fG = delta_G + eps_src[3]`).

**What is traded (symbolic).** A real Ĝ makes f_G small (residual of an accurate candidate) but pays ‖Ĝ‖ (in Env4) and
|Ĝ(a)| (centre motion); Ĝ := 0 makes those zero but pays the full surrogate f_G. On the lower front (ρ ≈ 2.7·10⁻⁴) the
ρ·f_G term is negligible and the real candidate is strictly better. [TAIL-COMPARISON REDACTED] The document
distinguishes the **break-even between the two enclosures** (a threshold on s_G/s_H at which the real-Ĝ enclosure
equals the Ĝ := 0 enclosure) from `evidence/forecast_r2/TAIL_FORECAST_R2.json` `critical_sup_G_over_sup_H_ratio` (a
different threshold: at which the real-Ĝ route still **closes** each cell; review r2 note M4). Both choices are valid
enclosures, so a campaign may compute both and intersect.

### 1.3 Premise (P3′) — σ3 and σ4 from adopted Aux3 evidence; the two towers
TC (P3) bounds the true source derivatives by the frozen J/h Leibniz tower:
`‖h_1‖ ≤ 1`, `‖h_1^{(n)}‖ ≤ sup‖S_0^{(n−1)}‖` (h_1' = −S_0 exactly), `‖h_j‖ ≤ 1`,
`‖h_j^{(n)}‖ ≤ Σ_i C(n,i) k_i ‖h_{j−1}^{(n−i)}‖`, and `σ_n(r) = Σ_i C(n,i) j_i ‖h_r^{(n−i)}‖` for r ≥ 1.
(On the tail the tower is loose at order 3 relative to adopted values: [TAIL-NUMBER REDACTED].)

Adopted Aux3 evidence carries certified order-3 quantities for the same objects
(`auxiliary_evidence.candidate_suprema['S:r:3'], ['Sclosed:0:3'], ['h:j:3']` and matching
`auxiliary_evidence.midpoint_eps`, all inside the frozen producer's identity gate). Since
‖S_r'''(e0)‖ ≤ ‖Ŝ_r'''(e0)‖ + ‖S_r'''(e0) − Ŝ_r'''(e0)‖ (likewise h_j):

    adopted3(r) := candidate_suprema['S:r:3'] + midpoint_eps['S:r:3']      bounds ‖S_r'''(e0)‖
    adoptedh(j) := candidate_suprema['h:j:3'] + midpoint_eps['h:j:3']      bounds ‖h_j'''(e0)‖

These are MIDPOINT bounds. σ3 enters only f_G ((P2), stated at e0) — midpoint is right. σ4 enters Env4 ((P3), must hold
for every e in the cell). Review r1 note N1 found (P3′) r1 substituted the midpoint bound into the order-3 slot and ran
the order-4 recursion on it — unsound. (P3′) r2 keeps **two** towers:

    midpoint tower   t_mid[j,3] = min( tower[j,3], adoptedh(j) )                 -> sigma3 only
    cell tower       t_cell[j,3] = min( tower[j,3], adoptedh(j) + rho * tower[j,4] )
                     t_cell[j,4] = min( sum_i C(4,i) k_i t_cell[j-1,4-i] , tower[j,4] )    -> sigma4 only

The cell tower's order-3 slot carries the mean-value correction ‖h_j'''(e)‖ ≤ ‖h_j'''(e0)‖ + ρ·sup_C‖h_j⁗‖ (h_j analytic
on the cell), with sup_C‖h_j⁗‖ from the **unrefined** (cell-uniform) tower; order-4 entries re-derived from corrected
lower orders (Leibniz recursion holds pointwise in e → cell-uniform inputs give cell-uniform output). Min of two valid
upper bounds is valid → (P3′) r2 sound by construction. The order-4 clamp `min(·, tower[j,4])` is defensive only and
never fires (cell tower ≤ pure tower componentwise; recursion monotone) (review r2 note M7). (Effect sizes at the tail
cells: [TAIL-NUMBER REDACTED].)

Which half is live (review r2 note M5): `h:1:3` loses to the frozen ‖h_1'''‖ ≤ sup_C‖S_0''‖; the r = 0 source refinement
loses to `sup_S0[3]` (`Sclosed:0:3` is the same closed-form quantity computed twice). Live half: `S:r:3` for r = 1…4 and
`h:j:3` for j = 2, 3, 4.

### 1.4 Statement and consumption — verbatim-close
With A from Lemma G, f_G from (P2′), σ3/σ4 from (P3′) and every other input the adopted K1/Aux3 value, TC §3 holds
unchanged: for every e in the cell

    p0 = f_F + ρ f_D + ρ² f_H/2 + ρ³ f_G/6 + ρ⁴ Env4/24,  p1 = f_D + ρ f_H + ρ² f_G/2 + ρ³ Env4/6,
    p2 = f_H + ρ f_G + ρ² Env4/2,   rad_r = A0 p2 + 2 A1 p1 + A2 p0,   half_r = rad_r   (|Ĝ(a)| = 0)
    R''_m(e) ∈ 𝓗_m := Σ_{r<m} (1/m)·[Ĥ_r(a) − half_r, Ĥ_r(a) + half_r] + Σ c(m)·𝒲_{(r,j)}

with Env4 = σ4 + 6k₂ s_H + 4k₃(s_D + ρ s_H) + k₄(s_F + ρ s_D + ρ² s_H/2) (the (P3) envelope at s_G = 0).
Consumption is TC §6 unchanged: H_k ← H_k ∩ 𝓗_m(k) (refuse if empty), M_k ← min(M_k, mag(H_k)), then the frozen
`k5b_literal`.

### 1.5 Identity of the replayed inputs (§5), sanitized
* Reproduction trap: frozen `cells.json` holds 642 entries (326 CUSUM, 316 SR); its `index` field collides across
  detectors, so a CUSUM tail index also exists for SR; keying on `index` alone silently loads the SR cell and gives a
  wrong Γ ([TAIL-NUMBER REDACTED]) while other quantities still match. Filter on `detector == "CUSUM"` first (the frozen
  loader does; review r2 note M6).
* `cert.norms`, `cert.sup[F|D|H, r, 0]`, `sup_S0`, `Ĥ_r(a)`, W enclosures are not stored in the adopted K1 record; they
  are recomputed by the frozen chain in replay mode (`code/tct_inputs.py`), where the frozen producer's identity gate
  compares 262 dependent fields (every `delta_mid`, `eps_mid`, `eps_cell`, Aux3 midpoint eps, Aux3 residuals and
  candidate suprema) against the sealed record exactly.
* **Derived identity gate** (`tct_rule.derived_identity_gate`): rebuilds the adopted `R2_interval` for every m from the
  replayed Ĥ_r(a) and W plus the record's `eps_cell_refined`; must be contained in the record interval with relative
  endpoint agreement ≤ 10⁻⁶ (measured gap: [TAIL-NUMBER REDACTED]); a wrong Ĥ_r(a) or W moves an endpoint by
  O(10⁻²–1).
* **Two independent rule paths**: `tct_rule.tail_enclosure` (through frozen `tc_rule`) and
  `tct_rule.tail_enclosure_crosscheck` (re-derived, shares **no function** with the first since review r1 note N15;
  re-derives both towers, both σ's, Taylor sums, (P3) envelope, assembly) must agree as exact rationals on every cell
  and m (20/20 pairs).

### 1.6 What is not claimed (§6)
No R, R′, R‴ values beyond the enclosure; no whole-function sup norm improved; no order-3 candidate of F proposed,
computed or recorded → guard stays DENY; Campaign A's note N5 trust surface not entered. The enclosure alone is **not**
sufficient for cells 306–309 and closes 305 ([TAIL-COMPARISON REDACTED]; see `phase_c/EXECUTION_DECISION.md`).
`tail_object` also accepts a non-zero order-3 supply (a real-Ĝ route is scored on the same (P3′) supply; (P3′) is a
statement about the source, independent of Ĝ; review r1 note N4).

---

## 2. REAL_ORDER3_THEORY.md (stream B_307)

Scope/quarantine: nothing evaluated on 305–309 or at drifts in [6/5, 13/5] (or mirror); **no order-3 result applied to
305–309**; tail facts quoted with file:line only. The accepted route audit rates the real order-3 route R4 at **HIGH**
scientific risk for 307 (`ROUTE_AUDIT_R1_REVIEW.md:105-124`); not lowered or used. Correction note (incident 01): a
pre-correction §4c set a committed tail break-even figure next to the structural ratios (α, β); removed on coordinator
instruction. Control classes (a)–(d): (a) through code, planted invalid, guaranteed to fire; (b) through code, not
guaranteed; (c) tautological/arithmetic; (d) tests only a comparison operator — (c)/(d) not evidence.

Notation: a = (0,0) atom; R_e = (I − K_e)⁻¹; K_i = ∂_e^iK_e; F_r = R_eS_r; Λ(e) = E_a[τ] = ‖δ_aR_e‖; ∂^jR = j-th
e-derivative of e ↦ R_e.

### 2.1 True order-3 objects and who needs what (§1)
* F_r'''(e) ∈ B(X) exists by (P1); F_r'''(e)(a) one signed real per (r, e); R'''_m(e) = (1/m)Σ_{r<m}F_r'''(e)(a) +
  Σ_t c(m,t)Σ_{r<t}W'''_(r,t−r−1)(e)(a) (same coefficients at every order).
* **TC needs** a fixed function Ĝ (any Ĝ admissible; only width changes), entering through three **midpoint** scalars:
  f_G ≥ ‖φ'''_Ĝ(e0)‖ with φ'''_Ĝ(e0) = S''' + 3K₁Ĥ + 3K₂D̂ + K₃F̂ − (I − K)Ĝ; |Ĝ(a)| (centre motion ρ|Ĝ(a)|); s_G ≥ ‖Ĝ‖
  (in Env4). "Real order-3" route: Ĝ ≈ F_r'''(e0); TC-T takes Ĝ := 0. TC is local and midpoint-only at order 3.
* **K5-B's chain needs** a certified whole-cell **signed** lower bound L_k ≤ inf_{e∈C_k} R'''_m(e) and an **unbroken**
  run from cell 0 (contiguity-dependent). So strictly more than TC: the sign; uniformity over the cell (pointwise
  order-4 bound at the atom: F'''(e)(a) ≥ F'''(e0)(a) − ρ·sup|F⁗(u)(a)|); contiguity. TC-T's whole-cell interval
  discards the sign (half_r = ρ|Ĝ(a)| + rad_r; HO-12).

### 2.2 Representations (§2)
* **2a Resolvent identity (exact):** F''' = R_e·[S''' + 3K₁F'' + 3K₂F' + K₃F] = Σ_{j=0..3} C(3,j)·∂^jR·S^(3−j);
  ∂^nR = Σ over compositions (i_1..i_p) of n of n!/(i_1!…i_p!)·RK_{i_1}RK_{i_2}R…K_{i_p}R; ∂³R = 6RK₁RK₁RK₁R + 3RK₂RK₁R +
  3RK₁RK₂R + RK₃R. Exact on 4 P1 cases; atom identity exact on all 320 fixture objects; class-(a) control (∂³R without
  3RK₂RK₁R) detected 4/4.
* **2b Hermite form (CUSUM):** (K_eg)(x) = ∫_{m−c}^{c−p} g(T(x,z))φ(z+e)dz, window and map e-free; ∂_e^iφ(z+e) =
  He_i(−(z+e))φ(z+e), so (K_i g)(x) = E[g(T(x,Z))·1{no alarm}·He_i(S)], S := −(Z+e) ~ N(0,1). Float check at declared
  drifts {0, 1/4, 1/2, 1, 3}: 240 cases, worst rel. error 1.6·10⁻¹⁵; control (b) sign dropped 112/120 odd-order (8
  vanish by symmetry). κ_n = E|He_n(Y)| = 0.797885, 0.967883, 1.510013, 2.800600 (n = 1..4) (generic constants).
* **2c Path (LR) form.** M_n := Σ_{k≤n} S_k. **Gaussian-location lemma:** ∂_e^j Π_{k≤n} φ(u_k) = H_j(M, n)·Πφ(u_k),
  H_j(M, n) := n^{j/2}He_j(M/√n): H_0 = 1, H_1 = M, H_2 = M² − n, H_3 = M³ − 3nM, H_4 = M⁴ − 6nM² + 3n² (proof: dependence
  only via Σu_k with variance n). Jets check worst 4.4·10⁻¹³; control (b) variance rescaling dropped 225/300.
  **Theorem RO3-LR (path representation).** Premises: P_x(τ > n) ≤ Ā·θ^n uniformly on a drift set E (from a whole-kernel
  supersolution W ≥ 1 + K_eW on E, θ = 1 − 1/‖W‖); g ∈ B(X) fixed. Claim: (∂^jR g)(a) = E_a[Σ_{n<τ} g(X_n)·H_j(M_n, n)]
  for every e ∈ E, j ≥ 0. Proof sketch: R g(a) = Σ_n E_a[g(X_n); τ > n]; differentiate summands; interchange justified by
  E|H_j(M_n,n)|² = j!·n^j and Cauchy–Schwarz: Σ_n E|g(X_n)H_j(M_n,n)|·1{τ>n} ≤ ‖g‖√(j!)Σ_n n^{j/2}√(Āθ^n) < ∞, uniformly on
  E. Consequence: Λ_j(e) := E_a[Σ_{n<τ}|H_j(M_n,n)|] ≥ ‖δ_a∂^jR_e‖, Λ_0 = Λ. **Caveat:** Cauchy–Schwarz proves finiteness
  only (order √Ā·(2C)^{1+j/2}, no better than Dv′ in Λ); sharp certification needs augmented-state supersolutions in
  (x, M) — the C_308 LR program (owns Λ_1, Λ_2), not implemented here.
* **2d Sources depend on e:** F_r^(k)(e)(a) = Σ_{j=0..k} C(k,j)·E_a[Σ_{n<τ} S_r^(k−j)(X_n; e)·H_j(M_n, n)] → **ADLR** bound
  |F_r^(k)(e)(a)| ≤ Σ_j C(k,j)·Λ_j(e)·σ_{k−j}(e), σ_i(e) ≥ ‖S_r^(i)(e)‖; any A_j ≥ ‖δ_a∂^jR‖ may replace Λ_j (true
  functional norm, positive majorant, Lemma-G-type `generic_dnR_bound`).
* **2e Hermite h-tower:** h_j(x) = P_x(τ = j); S_r(x) = E_x[raw_1·1{τ = r+1}], raw_1 = Z_1 + e (S_r = J_eh_r).
  h_j^(n)(x) = E_x[1{τ=j}·H_n(M_j, j)] ⇒ ‖h_j^(n)‖ ≤ κ_n·j^{n/2} (also ≤ √(n!·j^n·P_x(τ=j)));
  S_r^(n)(x) = E_x[1{τ=r+1}·(raw_1·H_n(M_{r+1}, r+1) + n·H_{n−1}(M_{r+1}, r+1))] ⇒ ‖S_r^(n)‖ ≤ √(n!·(r+1)^n) +
  n·κ_{n−1}·(r+1)^{(n−1)/2}. Universal constants, valid at every drift/cell; grow like j^{n/2} vs frozen tower (k₁j)^n.
  On exact FX_B score walks the frozen tower overstates truth 3–4× (j = 2), 9–12× (j = 3), 24–38× (j = 4), 47–77× on
  S_4'''. Control (b) binomial weights dropped 6/54 (weak). Valid alternative σ3/σ4 supply (min with frozen tower
  valid); keep frozen h_1^(n) = −S_0^(n−1) at j = 1. THEORY_ONLY; closure-only under floor r2.

### 2.3 Existence and finiteness (§3)
Kernel analytic (‖K_i(e)‖ ≤ κ_i, Lemma K; or drift-aware k_i); resolvent analytic if ‖R_e‖ ≤ C on the cell (Neumann
radius ≥ 1/(C·Σ_i κ_iρ^{i−1}/i!)), ‖∂^nR‖ ≤ generic_dnR_bound(n, k, C); sources analytic (S_0 closed form; S_r = J_eh_r,
h_r = K_e^{r−1}h_1); ‖F_r^(k)(e)‖ ≤ Σ_j C(k,j)‖∂^jR_e‖‖S_r^(k−j)(e)‖ < ∞; atom values finite, analytic; LR form finite under
a uniform geometric tail, Λ_j ≤ √(j!·Ā)·Σ_n n^{j/2}θ^{n/2}. Premise status on the tail (read only): a whole-kernel
supersolution Ā exists on the tail blocks (committed I1 registry `REGISTRY_C1.json:12-109`); no new tail quantity computed.

### 2.4 Propositions RO3-S / RO3-F / RO3-E (§4) — what they say
* **RO3-S (surrogate = norm-only resolvent bound on the true point value).** With Ĝ = 0, φ'''_0 := S''' + 3K₁Ĥ + 3K₂D̂ +
  K₃F̂ (at e0), E_X := X(e0) − X̂:
  `[R_{e0}φ'''_0](a) = F'''(e0)(a) − [R(3K₁E_H + 3K₂E_D + K₃E_F)](a)`, and `A0·f_G ≥ A0·‖φ'''_0‖ ≥ |[R_{e0}φ'''_0](a)|`.
  Proof: subtract the exact §2a identity. Reading: the dominant TC-T monomial A0·ρ·f_G is **exactly** a norm-only bound of
  ρ·|F'''(e0)(a)| up to candidate-error terms, built by a triangle split into four norms.
* **RO3-F (centre-motion floor).** For any fixed Ĝ, f_G(Ĝ) ≥ ‖φ'''_Ĝ(e0)‖, A0 ≥ ‖δ_aR_{e0}‖:
  `ρ|Ĝ(a)| + A0ρ·f_G(Ĝ) ≥ ρ·|[R_{e0}φ'''_0(e0)](a)| (≈ ρ|F'''(e0)(a)|)`.
  Proof: φ'''_Ĝ = φ'''_0 − (I − K)Ĝ ⇒ [Rφ'''_Ĝ](a) = [Rφ'''_0](a) − Ĝ(a); triangle. Reading: whatever order-3 candidate,
  the A0-level ρ-group of a **whole-cell** TC enclosure cannot fall below the true centre motion; a real Ĝ removes only
  the excess of the norm-only bound over that floor. Holds on 320 objects × 3 routes; class-(a) control (G = 0, f_G = 0,
  s_G = 0 through `route_groups`) flips `floor_ok` on 320/320 eligible.
* **RO3-E (order-4 envelope penalty of a real candidate).** A real Ĝ puts s_G into Env4; A0-level cost
  A0·(ρ²/2)·s_G·(4k₁ + 6k₂ρ + 2k₃ρ² + k₄ρ³/6); relative to A0ρf_G^surr:
  `β := ρ·s_G·(4k₁ + 6k₂ρ + 2k₃ρ² + k₄ρ³/6) / (2 f_G^surr)`. Since ‖F'''‖ ≤ C‖(I − K)F'''‖ ≤ C(f_G^surr + ε3),
  ε3 := 3k₁‖E_H‖ + 3k₂‖E_D‖ + k₃‖E_F‖, and s_G ≤ ‖F'''‖ + ‖Ĝ − F'''‖:
  `β ≤ ρ(4k₁ + 6k₂ρ + 2k₃ρ² + k₄ρ³/6)·(C(f_G^surr + ε3) + ‖Ĝ − F'''‖) / (2 f_G^surr)`.
  Under the frozen cover rule ρ ≤ 1/(4 a_up C_use), k₁ ≤ κ₁ ≤ a_up (`CHECKPOINT.md:91-97`), leading factor 2k₁ρC ≤ 1/2, so
  for an accurate candidate `β ≤ (1/2)·(1 + O(ρ) + ε3/f_G^surr + ‖Ĝ−F'''‖/(C f_G^surr))`.
  Consequence (ideal candidate): α := |F'''(e0)(a)|/(A0 f_G^surr); `Q_real/Q_surr ≈ α + β ≤ α + 1/2 (+ small)` — never
  much worse (≤ ≈ 1.5×); gain capped by 1/(α + β); large iff α ≪ 1 and F''' is **not Perron-amplified**
  (‖F'''‖ ≪ C‖(I − K)F'''‖; "Perron index" s_G/(C f_G^surr)). Envelope holds on 640 real-route objects; class-(a)
  control (inflated s_G through `route_groups`) flips 320/320. FX_A under cover rule β = 0.0025–0.09 vs envelope
  0.05–0.62; lower front β = 0.0033–0.0084, 2k₁ρC_upper = 0.49992–0.499999. No committed tail-cell figure placed next to
  α, β (incident-01 rule).
* **ADLR evaluated (§4d).** Enclosure F_r''(e)(a) ∈ Ĥ_r(a) ± [rad0 + s·B3 + (s²/2)·B4], rad0 = A0f_H + 2A1f_D + A2f_F at e0;
  B3 = Σ_{j≤3} C(3,j)A_j(e0)σ_{3−j}(e0); B4 = Σ_{j≤4} C(4,j) sup_u A_j(u) σ^cell_{4−j}. Validity: (i) A_j bound
  ‖δ_a∂^jR‖ at e0 (rad0, B3) and uniformly (B4); (ii) σ_i bound true source derivatives (at e0 / cell-uniform); (iii)
  Taylor with integral remainder for e ↦ F_r''(e)(a). s-coefficient B3 = Λσ3 + 3A1σ2 + 3A2σ1 + A3σ0 vs TC-T A0f_G; no
  A1/A2 cross terms in the ρ-group (removes rank 1 of the audit) but needs A3 (true order Λ^{5/2}, certified Λ⁴) and
  cell-uniform A4. Fixture half-width / TC-T surrogate half (medians): G (certified generic_dnR_bound) FX_A 18.3,
  FX_B 2.2·10⁴; PM (proxy) 2.67 / 2.4·10³; true (best case of any A_j supply) 0.46 / 2.9; oracle (shape floor) 0.050 /
  0.0016; 0 pointwise failures. Verdict: valid; incomparable with TC-T and regime-dependent (2.2× tighter on FX_A with
  best constants, 2.9× looser on large-Λ FX_B); with the only certified supply today 18× (FX_A) to 2·10⁴× (FX_B) looser;
  always looser than an accurate real-Ĝ route; shape excellent (oracle 20× tighter than surrogate on FX_A); gap entirely
  in A3, A4, which no stream certifies. Which regime the tail is in: not assessed (quarantine).

### 2.5 What "real order-3 / real Ĝ" requires (§5 + notes files)
| route | inputs | available? | blocker (committed) |
|---|---|---|---|
| **real Ĝ in TC (R4)** | K1 candidates F̂, D̂, Ĥ (degree-12 dyadic polynomials); a producer run of the order-3 solve (I − K)Ĝ = K₃F̂ + 3K₂D̂ + 3K₁Ĥ + Ŝ:3 with certified residual δ_G, sup s_G, value Ĝ(a) | **no** | candidates **never serialized** (0/326, C6 README:41-50); replay needs numpy/python-flint on a host (none in scope, C6-N1); order-3 producer real-cell registry **frozen empty** and its guard **DENY**; notes **N1, N3, N5, N7 open** (`p5y_k5_tail_c2_closure/OPEN_NOTES_DISPOSITION_C2.md:5-43, 72-75`) |
| ADLR | σ0..σ3 at e0 and σ0..σ4 cell-uniform; A_0..A_3 at e0, A_0..A_4 cell-uniform | partly | σ's committed ((P3′) Aux3, pure tower or Hermite bound); A_0 = Ā_eff; A_1, A_2 as Lemma G/Dv′ (LR sharpening THEORY_ONLY, C_308); **A_3, A_4 only generic, 18×–2·10⁴× too loose; no stream owns sharp A_3/A_4** |
| direct atom bound with Dv′-type constants | Lemma Dv″ with new operator constant D3 ≥ |D'''| | no | D3 certified nowhere; new operator constant, closure-only |
| K5-B chain L_k | cell-uniform order-4 atom bound + unbroken run from cell 0 | no | readiness audit: "chain problem" (`README.md:109-113`) |
Governance: every route closure-only (changes consumer / non-constant inputs / constants other than Lemma G / Dv′ r2);
adoption needs a user-decided floor extension frozen before any evaluation (`ROUTE_AUDIT_R1.md:42`; floor r2).

**N-notes a real-Ĝ (R-stage / continuation C2) route must discharge** (from the two notes files):
* **N1 / C7** — the order-3 producer's registry (`p5y_k5_cusum_order3_real_producer/config/REAL_CELL_AUTHORIZATION_REGISTRY.json`,
  FROZEN_EMPTY: "no real CUSUM cell may be evaluated by this producer") vs Campaign A's execution of that namespace's
  frozen `Order3Certifier` on lower-front cells 11–44 under its own authorization. Not load-bearing for Campaign B or C2
  (Ĝ := 0; no gated entry point `certify_real_cell` / `rung3_engine.certify_order3` executed; `rung3_residual.g_residual`
  never called; `NEW_REAL_ADDRESSES = 0` in C2). **Becomes load-bearing the moment the R stage runs:** the bridge must be
  owned by the successor that evaluates the first real order-3 cell, must not edit the historical registry, must state
  why that successor may use the qualified executor, and must bind executor identity, protocol identity, runtime
  identity, the allowed address set, output schema, precision, resource cap, seal policy and consumer — under independent
  review; it must name `p5y_k5_lower_front_order3/evidence/tc_r1/SEAL.json` `disclosure_C7_parallel_channel` and its own
  authorization before its freeze.
* **N3** — the manufactured oracle covers r = 0 and m = 1; the r ≥ 1 source tower and W assembly rest on cross-checks.
  Campaign B answered it without new fixtures via (P3′) intersection and the new derived identity gate. **If a real-Ĝ
  route is executed, N3 returns in full:** manufactured fixtures at the tail geometry (drift, ρ and atom-constant ranges
  [TAIL-NUMBER REDACTED]) must be added, since existing fixture families run at e₀ ∈ [−0.2, 0.2], ρ ≤ 0.02 and exercise
  neither the tail's ρ² regime nor its atom constants; still open (C2): tail-geometry fixtures and exact independent
  cross-checks for the source tower, W assembly, order-3 injection, whole-cell transport and consumer composition.
* **N5** — the four new order-3 fields `delta_G`, `eps_src[3]`, `sup.G`, `abs_G_at_a` have no identity gate. Retired
  for TCT0/C2 by construction (Ĝ := 0: `sup.G = abs_G_at_a = 0`; `delta_G` = closed form of identity-gated quantities;
  `eps_src[3]` adopted Aux3; C2 consumer passes `order3 = None`; mutant M09 detects an order-3 field at the wrong
  location). **For the R stage N5 must be closed properly** ("they can widen but not shift" is not enough): bound and
  verified field names, semantic roles, source hashes, expected signs and ranges, exact insertion point, and mutation
  detection for each. Pre-registered refusal-only invariants: `abs_G_at_a ≤ sup.G` and `delta_G > 0`.
* **N7** — the deterministic direction is not established as exhausted. [TAIL-COMPARISON REDACTED] **This blocks any
  R-stage authorization** and must be discharged by a successor D′ campaign, with its rule frozen first, before a real
  order-3 address is spent.
* Also from C2: N6 (frozen gate's `why_gap_and_not_ratio` directionally inverted; not amended; successor must not copy),
  N8 (cell 306 margin floor referred to adjudicator), N9 (Arb/FLINT supersolutions are one implementation; second
  independent certifier is the real answer), N10 (registry does not record its build host/toolchain/precision; successor
  must record at build time).
* New real addresses: a real-Ĝ route needs real order-3 producer evaluations on real cells (NEW_REAL addresses),
  authorization entries in the frozen-empty registry via a governed successor, a host (U1), and the guard to leave DENY.

### 2.6 Non-target evidence (§6), non-tail numbers only
* 6a exact fixtures, ladder of bounds on |F_r'''(e0)(a)| / truth (medians): FX_A — L_res_norm 4.9, L_split_true 13.5,
  L_surrogate (TC-T form) 18, L_atom_true 5.6, L_atom_PM 95, L_atom_G 203, **L_real (η = 10⁻³ / 10⁻²) 1.02 / 1.19**;
  FX_B (24/80 objects with F'''(e0)(a) ≠ 0) — 77, 538, 664, 2670, 7.2·10⁵, 2.2·10⁶, 1.10 / 2.1. All sound. FX_A
  factorization: 18× ≈ 5× (norm-only) × 2.7× (four-norm split) × 1.3× (candidate sups, cell norms, A0 ≥ Λ); a real
  candidate collapses it to 1.02–1.2. (Fixture Λ ranges omitted: [LATENT-PROXY REDACTED] — conservative.)
* 6b surrogate vs real vs ADLR (medians): FX_A cover rule Q ratio 0.088, α 0.058, β 0.018, half-width ratio 0.17; FX_A
  ρ/16: 0.075, 0.072, 0.0009, 0.081; FX_B cover rule 0.0020, α 0 (F''' ≡ 0 on 56/80), β 0.0010, half 0.24; FX_B ρ/16
  0.0010, 0, 0.00006, 0.83. On FX_B the A2·p0 monomial dominates (rank 1; P_0 share 0.51–0.995) — improving order 3
  alone cannot beat rank-1 atom-functional slack. Pointwise soundness 0 failures (320 × 17). Controls (b): sign-flipped
  motion 328/640; f_G := 0 146/320; (a) E'' identity without RK₂R 5439/5439.
* 6c lower-front (34 committed cells, 170 objects, real order-3 data): reproduction gate 136/136 exact; 2⁻⁶⁰ δ_G
  perturbation detected. Surrogate uses pure-tower σ3 (P3′ Aux3 not in these files; σ3 is 0.4–53 %, median 15 %, of
  f_G^surr). α 0.0091–0.027 (0.017); β 0.0033–0.0084 (0.0057); Q_real/Q_surr 0.012–0.035 (0.023); per-object half-width
  real/surrogate 0.107–0.294 (0.185); m-enclosure width real/surrogate m = 1 0.107–0.160, m = 2 0.153–0.222, m = 3
  0.157–0.226, m = 5 0.157–0.217; Perron index 0.0065–0.017; 2k₁ρC_upper 0.49992–0.499999. Reading: surrogate's order-3
  monomial overstates certified point motion 37–110×; β < 0.01; real route narrows m-enclosures 4.42–9.35× (baseline
  caveat: pure-tower σ3 favours the real route). **Transfer: none** to any tail cell (route audit E09/§8; Campaign B's T2
  is the committed counter-example).

### 2.7 Verdict (§7): does the real order-3 object contain more structural information?
Yes, in one precise sense, with three limitations:
1. **More information: the signed point value** F_r'''(e0)(a); surrogate replaces it by a norm-only bound (RO3-S);
   excess structural (norm-only factor; SM(d) sharp only for f ≡ 1; four-term split discards near-cancellation to
   (I − K)F'''); large on fixtures (FX_A median 18×) and real non-target cells (37–110×); unbounded in general (FX_B).
2. **Limitation A — whole-cell floor** (RO3-F): whole-cell interval charges ρ|F'''(e0)(a)| and discards the sign; sign
   usable only by a profile-/sign-aware consumer (TPT; K5-B chain with L_k).
3. **Limitation B — norm-only cost moves to order 4** (RO3-E): s_G re-enters via Env4; ≤ ≈ 1/2 of the surrogate's order-3
   monomial for an accurate candidate under the cover rule; gain capped by 1/(α + β); real route never worse than ≈ 1.5×;
   penalty small exactly when F''' is not Perron-amplified. **Which regime the tail is in has never been measured**
   (committed: "The tail's own s_G/s_H has never been measured", `R_STAGE_DESIGN.md:68-69`).
4. **Limitation C — order 4 and atom functionals remain:** after an order-3 fix the order-4 envelope dominates on FX_A
   (83–98.5 % of rad); with fixed order-3 candidate the A2·p0 monomial can dominate (FX_B); neither touched by a real Ĝ;
   no route has an order-4 point value; ADLR is the only candidate-free route (needs sharp A_3, A_4).
Negative results preserved: (N-a) Cauchy–Schwarz LR constants not sharper than Dv′ in Λ (finiteness only); (N-b) ADLR
with certified constants 18×–2·10⁴× looser; (N-c) best-case ADLR looser than surrogate on FX_B (2.9×) and than accurate
real Ĝ everywhere tested; (N-d) Hermite h-tower does not beat frozen closed form at j = 1; (N-e) FX_B has F'''(a) ≡ 0 on
most objects (F_0(a) ≡ 1, F_1(a) = 1 − p₀(e)) — α statistics degenerate. **Not applied to 305–309; no tail number
produced.**

---

## 3. HIGHER_ORDER_AUDIT_307.md — structure only

Quarantine: nothing computed for 305–309 or drifts in [6/5, 13/5] (or mirror); every tail number quoted with file:line;
new numbers only from synthetic fixtures, declared drifts {0, 1/4, 1/2, 1, 3}, and the 34 lower-front TC cells; no I1
constant combined with I2; no committed "x-eff" factor used to rank; validation sets declared first
(`VALIDATION_DECLARATION_B307.json`).

**§0 History table** — committed tail facts (C3/C4 knockout at 307, C5 radius-sum decomposition for 307/308/309, C2
elasticities, σ3 share at the tail, tail midpoint residual magnitudes): all values [TAIL-NUMBER REDACTED]. Also quoted
(generic): Lemma Dv′ r2 `A0 = Ā_eff, A1 = Ā_eff(κ₁C_T + δ₁), A2 = Ā_eff(2κ₁²C_T² + κ₂C_T + 2κ₁C_Tδ₁ + 2δ₁² + δ₂)`
(`THEOREM_AD.md:81-89`); Lemma G `A0 = C, A1 = k₁C², A2 = k₂C² + 2k₁²C³`; route audit rates R4 HIGH risk for 307 (review
N3 corrects r1's MEDIUM). "History only; no route factor combined with them."

**§1 Chain under audit:** (P1) analyticity; (P2) f_F, f_D, f_H; (P2′) f_G surrogate [HO-8]; (P3) Env4 [HO-9]; (P3′)
σ3/σ4 towers [HO-10] → Taylor with integral remainder → ‖φ^(j)(e)‖ ≤ p_j [HO-7]; (I−K_e)E = φ [HO-1] → E'' = Rφ'' +
2(∂R)φ' + (∂²R)φ [HO-2]; atom evaluation with A0, A1, A2 [HO-3…HO-6] → rad_r = A0p2 + 2A1p1 + A2p0; centre motion
half_r = ρ|Ĝ(a)| + rad_r [HO-11, HO-12]; assembly [HO-13]; H_k ∩ 𝓗_m, M_k = mag [HO-14] → K5-B direct clause / C5-T
[HO-15]; chain (ℓ_k, γ_k, L_k) [HO-16]. Exact bookkeeping (`b307_lib.radius_terms`):

    rad = A0·f_H + A0ρ·f_G + A0ρ²·Env4/2
        + 2A1·f_D + 2A1ρ·f_H + A1ρ²·f_G + A1ρ³·Env4/3
        + A2·f_F + A2ρ·f_D + A2ρ²·f_H/2 + A2ρ³·f_G/6 + A2ρ⁴·Env4/24.
"Higher-order contribution" = every monomial containing f_G or Env4 (seven of twelve). [TAIL-COMPARISON REDACTED]
(the audit's inference about which monomials carry the weight at 307 uses committed tail residual magnitudes).

**§2 Inequality list** (columns: exact? / relaxation / discarded / collapse / order):
* HO-1 (I − K_e)E = φ, E := F − F̃ — exact.
* HO-2 E'' = Rφ'' + 2(∂R)φ' + (∂²R)φ, ∂R = RK₁R, ∂²R = 2RK₁RK₁R + RK₂R — exact (also at the atom); five-way split
  P_H + P_G + P_4 + P_1 + P_0 = E''(e)(a) holds by construction (class (c), not evidence).
* HO-3 |E''(e)(a)| ≤ A0‖φ''‖ + 2A1‖φ'‖ + A2‖φ‖ — two relaxations (triangle over three atom terms; |δ_aTf| ≤ ‖δ_aT‖₁‖f‖∞
  with cell-uniform A_j); discards cancellation, residual shape (sharp only for f ≡ const, SM(d)), e-dependence;
  collapse to three scalars; residual-specific, no a-priori bound (C4 §7 item 1 escape).
* HO-4 A0 ≥ sup_C Λ(e) — Lemma G A0 = C_upper ≥ sup_{e,x}E_x[τ] ≥ Λ (discards start state, drift); Dv′ A0 = min(Ā, τ/D_lo)
  (SM(d)-sharp); order O(1).
* HO-5 A1 ≥ sup ‖δ_aRK₁R‖ — ladder true ≤ PM (R|K₁|R1)(a) ≤ Λk₁C ≤ k₁C² (G); Dv′ Λ_eff(κ₁C_T + δ₁) via taboo form; discards
  sign cancellation of K₁ (zero-mean score), quotient-rule cancellation, post-atom state; orders G O(k₁C²), Dv′
  O(Λ(κ₁C_T + δ₁)), heuristic LR O(Λ^{3/2}).
* HO-6 A2 ≥ sup ‖δ_a(2RK₁RK₁R + RK₂R)‖ — same ladder; G O(C³), Dv′ O(ΛC_T²), heuristic LR O(Λ²); certified supplies loose
  by O(C_T²/Λ) (Dv′) or O(C³/Λ²) (G).
* HO-7 Taylor remainders p0, p1, p2 — exact expansion, bound not; discards relative direction, sign of t, profile (→ TPT);
  under the cover rule k₁ρC ≤ 1/4 and A1ρ/A0 = k₁Cρ bounded ⇒ A1/A2 monomials never asymptotically suppressed.
* HO-8 f_G (P2′) = σ3 + 3k₁s_H + 3k₂s_D + k₃s_F (+ ε_src[3]) — four relaxations (triangle over nearly-cancelling vectors
  summing to (I−K)F''' up to candidate errors; ‖K_iX̂‖ ≤ k_i‖X̂‖ discarding derivative action; ‖X̂‖ ≤ s_X; σ3 from tower or
  Aux3); ε_src[3] pure slack (tiny); collapse; O(1) in Λ.
* HO-9 Env4 (P3) — relaxations of HO-8 at order 4 plus cell supremum and triangle over |t| ≤ ρ; true object ≈ (I−K)F⁗
  (Ĝ ≈ F''') or ≈ (I−K)F⁗ − 4K₁F''' + O(ρ) (Ĝ = 0).
* HO-10 (P3′) towers — triangle + collapse each step; discards Gaussian-location structure; tower ~ (k₁j)^n vs Hermite
  κ_n j^{n/2}; bounded gain for j ≤ 5; Aux3 already replaces tower at order 3 where it binds; order 4: cell tower only
  supply.
* HO-11 A0·ρ·f_G bounds P_G = t·[R_eφ'''(e0)](a) — composition HO-3(ii)∘HO-8; bounds ρ|F_r'''(e0)(a)| up to candidate
  errors; two slack factors (norm-only, split).
* HO-12 centre-motion floor half_r = ρ|Ĝ(a)| + rad_r — intrinsic to a whole-cell interval (RO3-F); discards the sign.
* HO-13 assembly 𝓗_m — valid Minkowski sum; per-object worst cases; discards cross-object correlation; W not audited.
* HO-14 H_k ∩ 𝓗_m, M_k = mag — exact intersection; magnitude discards sign. (Tail-specific binding-endpoint statement
  and its consequence for the clause: [TAIL-COMPARISON REDACTED].)
* HO-15 K5-B direct clause Γ = g_hi + ρ·x_hi·M and C5-T — MVT with sup|tR''| ≤ x_hi·M; discards sign, weight t, profile;
  C5-T restores weight, TPT restores profile (optimal in three-input family); not higher-order.
* HO-16 K5-B chain (ℓ_k, γ_k with L_k ≤ inf R''') — not used at the tail (needs signed whole-cell L_k and unbroken chain
  from cell 0; readiness audit "chain problem"); TC-T discards exactly the sign info the chain needs.

**§3 Orders table** (certified form vs truth): HO-4 O(1); HO-5 A1 avoidable Λ^{1/2} at zero drift (Λ^{0.63–0.77} at drift
1/4, 1/2 — FX_B synthetic); HO-6 A2 avoidable Λ¹ (Λ^{1.1–1.4}); A3 (ADLR) certified Λ⁴ vs true Λ^{5/2}; HO-8 constant
factor (fixtures 2.1–2.2 FX_A, 8.8 FX_B); HO-11 unbounded ratio (FX_B), lower front 37–110×; HO-9 constant (1.1–10);
HO-10 j^{n/2}; HO-7 profile factors 1/2, 1/3 (TPT); HO-13 constant (1.2–3.4). FX_B log-log slopes at zero drift: true
1.499, 2.005, 2.494 (= Λ^{1+j/2}); every certified rung and PM ~ Λ^{1+j} (PM 2.008, 3.006, 4.004; G 2.0, 2.99, 3.98; Dv′
1.91, 2.83). **Structural conclusion: the entire asymptotic slack of A1, A2 (and A3) is sign cancellation**; collapse
steps change only constants. At drift 1/4, 1/2 (FX_B synthetic): true exponents fall; C_T grows faster than Λ (slope
1.35) so Dv′ asymptotically worse than G there. Caveat: FX_B is a one-sided discrete walk sharing CUSUM's score structure,
not the CUSUM kernel — exponents are evidence of structure only. Cover-rule consequence: A1ρ/A0 and A2ρ²/A0 bounded by
cell-independent constants at every cell.

**§4 Fixture demonstrations T1–T5** (64 cells: FX_A 48, FX_B 16; 320 objects; 4 routes — surrogate, zero candidate with
exact residual, real Ĝ η = 10⁻³, real Ĝ η = 10⁻²; 17 grid points): T1 identities exact with class-(a) controls; T2
atom-constant ladders (biggest step true → PM, 3–400×; collapse and Λ → C 1–2×; Dv′ 2.4–680× above truth); T2b Λ-scaling
(class-(a) exponent-claim check fires on |K_i| mutant); T3 per-term looseness (FX_A cover-rule surrogate medians P_H 19,
P_G 18, P_4 19, P_1 627, P_0 2770; share of rad P_G 0.77, P_4 0.096, P_1 0.17, P_0 0.014 — synthetic, not compared with
any tail cell; P_G slack = norm-only 5.8 (Λ-only 4.9) × split 2.2; Env4/max‖φ⁗‖ 1.9); T4 assembly per-r/joint FX_A
1.42–3.22; T5 lower-front (same figures as §2.6; certain lower-front ratio rows that serve as the committed tail evidence
model are withheld: [LATENT-PROXY REDACTED]; lower-front C scale also withheld: [LATENT-PROXY REDACTED]).

**§5 Ranked looseness inventory** (slack classes P = larger asymptotic order, U = norm-only on pointwise signed object,
C = bounded constant; no tail-cell share used):
1. atom functionals of ∂R, ∂²R in the radius (2A1·p1, A2·p0) — P × U × C — sign cancellation (zero-mean score, path
   martingale M_n), residual shape, post-atom state — owner C_308 LR (not implemented here).
2. norm-only atom evaluation of A0·ρ·f_G (HO-11) — U × C — pointwise value/sign of F_r'''(e0)(a), four-term cancellation,
   K_i as derivative — owner real order-3 candidate (R4), ADLR or direct atom bound.
3. norm-only evaluation of order-4 remainder A0·ρ²·Env4/2 — U × C — pointwise F⁗(a), five-term cancellation, cell sup —
   **no route yet**.
4. (P3′) J/h tower — P in j (bounded for j ≤ 5) — Hermite h-tower (THEORY_ONLY).
5. split and collapse inside f_G, Env4 — C — joint residual certificate (needs payloads, C6).
6. assembly per-object radii — C — joint residual (data-blocked).
7. whole-cell time substitution |t| → ρ — C — TPT.
8. A0 — C — A0X / C_308.
9. clause magnitude/weight/profile — C — stream E.
— exact items: HO-1, HO-2, (P2)/(P2′) identities, SM(d), D = ν(h₁).
Remarks: ranks 1–3 are all norm-only evaluations of pointwise objects; rank 1 is the only item with a proven growing gap
(pure sign cancellation); rank 3 has no owner and dominates once rank 2 is improved (fixtures). Correction note
(incident 01): a pre-correction version placed route/synthetic gain factors (e.g. TPT-G profile factors, fixture share
patterns) next to committed tail-cell shares of S — a target-equivalent proxy; corrected.

**§6 Cell 307 (structural statements only):** (1) the committed knockout names (A1, A2) as 307's blocker under the
committed clause; A1, A2 multiply p1, p0 (content ρ²f_G/2 + ρ³Env4/6 and ρ³f_G/6 + ρ⁴Env4/24 up to measured-residual
terms) → the blocker is structurally rank 1 × (ranks 2–3 quantities); two multiplicative levers: sharper atom functionals
(C_308 LR) and sharper order-3/4 quantities (real Ĝ, ADLR, direct atom bound). (2) cover rule makes A1/A2 monomials
structural (k₁ρC ≤ 1/4 at every cell). (3) improving order 3 moves the problem to order 4 (rank 3, no owner). (4)
nothing is a 307 forecast; no fixture or lower-front ratio combined with any committed tail figure or transferred.

**§7 Reproduction:** `b307_run_fixtures.py` (T1–T4, ≈ 6 min exact), `b307_scaling.py`, `b307_tower_fixture.py`,
`b307_lower_front.py`, `b307_hermite_check.py`, `ov_quarantine.py --scan` (0 findings; planted control detected); ledger
classes SYNTHETIC_VALIDATION / NONTARGET_DRIFT_VALIDATION / NONTARGET_REAL_VALIDATION.

---

## 4. B_307_ROUTE_SUMMARY.md

Research only: no route and no cell CLOSED; nothing adopted or frozen. Quarantine 0/0/0; static scan 0 findings in 8
B_307 files, planted control detected.

Registry rows:
| id | route | mechanism | state | r2 status |
|---|---|---|---|---|
| B307-R1 | real order-3 candidate Ĝ ≈ F_r'''(e0) in TC (R4 restated) | replaces A0ρf_G by ρ|Ĝ(a)| + A0ρδ_G, cost s_G in Env4 | **BLOCKED**: candidates never serialized (C6); no host; producer registry empty and guard DENY; N1/N3/N5/N7 open | closure-only |
| B307-R2 | ADLR | Ĥ(a) ± [rad0 + sB3 + s²B4/2] from A_j and σ_i | **BLOCKED**: needs sharp cell-uniform A_3, A_4 (uncertified); fixtures only | closure-only |
| B307-R3 | Hermite h/S tower (‖h_j^(n)‖ ≤ κ_n j^{n/2}, ‖S_r^(n)‖ ≤ √(n!(r+1)^n) + nκ_{n−1}(r+1)^{(n−1)/2}) | alternative σ3/σ4 supply, min with frozen tower | **THEORY_ONLY** | closure-only |
| B307-R4 | joint (unsplit) order-3/4 residual across four kernel terms and across r | removes split factor (≈ 2.2×) and per-r triangle (≈ 2.4×) (fixtures) | **BLOCKED**: needs payloads (C6) | closure-only |
| B307-ref | (A1, A2) via LR/score constants | removes rank-1 sign-cancellation slack | DEFERRED to C_308 | closure-only |

Kill gates (R1 / R2 / R3 / R4): G1 P/P/P/P; G2 P/P/P/P; G3 P×4; G4 P on fixtures, F on real cells / P fixtures / — /
F; G5 P (fixtures + 34 lower-front cells, 136/136 exact reproduction, real/surrogate enclosure 0.11–0.22) / P fixtures,
— real / — / P fixtures; G6 partial (independent TC arithmetic reproduction; no second agent on RO3-E/F) / F / F / F; G7
P×4; G8 P×4; G9 F (data, host, governance N1/N3/N5/N7) / F (A_3, A_4) / F / F (payloads); G10 P on non-target (lower-front
m-enclosures 4.42–9.35× narrower; baseline caveat; capped by 1/(α+β); leaves ranks 1 and 3) / F with certified constants,
best case incomparable / undetermined / undetermined. States: R1 BLOCKED, R2 BLOCKED, R3 THEORY_ONLY, R4 BLOCKED.

Controls register: (a) ∂³R without 3RK₂RK₁R 4/4; E'' factor 2 fired; ∂²R without RK₂R 5439/5439; φ''' 2K₁Ĥ 2/2; ladder
plants 42/42, 42/42; Λ-exponent mutant fired; RO3-F plant 320/320; RO3-E inflated s_G 320/320; lower-front 2⁻⁶⁰ δ_G
perturbation fired; scan planted file detected. (b) pointwise soundness 328/640, 146/320; ADLR oracle B3 := 0 247/320;
Hermite 112/120, 225/300; tower binomial weights 6/54 (weak). (c)/(d) non-evidence: SM(d) "A0 := τ_a ≥ Λ"; linear slope
plant; five-way split.

Per-cell deliverable 307: §0 history (committed 307 radius-share decomposition and knockout: [TAIL-NUMBER REDACTED];
route audit R4 HIGH risk; tail s_G/s_H never measured). §1 structural decomposition (as audit §6). §2 order-3 findings
(RO3-S, RO3-F, RO3-E ≈ 1/(α+β), ADLR valid but incomparable and blocked; non-target measurements not transferred).
§3 strongest surviving route: largest proven asymptotic slack is rank 1 (C_308 LR); inside this stream **B307-R1** (only
demonstrated real non-target gain; BLOCKED; closure-only; leaves ranks 1 and 3). §4 remaining theorem gap: (i) no
certified sharp atom functionals A1, A2 (C_308), A3, A4 (unowned); (ii) no pointwise order-4 object; (iii) no sign-aware
consumer compatible with floor r2 (TPT and chain closure-only or contiguity-bound); (iv) R4's data/host/governance
prerequisites (N1/N3/N5/N7). §5 **FREEZE_READY: NO** (no route meets G9; all closure-only; floor extension needed,
`ROUTE_AUDIT_R1.md:42`).

---

## 5. Order-3 producer READMEs (lineage; none evaluates a real cell)

| namespace | what it is | key facts |
|---|---|---|
| `p5y_k5_cusum_order3_producer_design` | design + non-scientific qualification of a CUSUM signed order-3 producer | not a producer run / K5 probe / authorization; computes no R''' for any (D,m), reads no K1 record, uses no host; B1 (no certified order-3 producer) and B2 (no SR K1 inputs) open; B3 closed by `d7d3c08b` with scope limitation; `DESIGN.md` (objects, certified rules with proofs, export schema, qualification ladder L0–L5, owner decisions, risk); `QUALIFICATION_PROTOCOL.json` QN1–QN6 FROZEN_PRE_RESULT; exact-rational reference kernel `order3_algebra.py`; manufactured analytic systems; synthetic qualification PASS |
| `p5y_k5_cusum_order3_real_producer` | implementation + non-scientific qualification of the real producer | no real CUSUM cell evaluated, no R''' computed; K1/closure/K5-B/countersignature/premise-binding/design unchanged; SR out of scope (B2); `PRE_RESULT_GATES.json` G01–G16 + verdict rule; `REAL_CELL_AUTHORIZATION_REGISTRY.json` **frozen empty**, pinned in `cusum_order3.py`; `rung3_engine.py`, `rung3_residual.py` (Arb engine, new-rung residual); `cusum_order3.py` real front-end gated, never entered; `k1_inputs.py` fail-closed K1 record validation V01–V10 with target gate for every m; manufactured chains with exact truth; reference differential; independent rational-function whole-cell cross-check; real-operator integration on synthetic polynomials vs float quadrature; runs on `rebaseguard-vultr-02` venv at the freeze commit |
| `p5y_k5_cusum_order3_r2_repair` | R2 repair successor (non-scientific, additive; R1 immutable) | real-cell and operator-certificate registries frozen **empty**; R05 repair, cell-0 autopsy and exact budget, e = 0 structural audit; selected method σ-graded certified error propagation (orders 0–3, midpoint and whole cell) `graded_dag.py`; real graded range primitive with **wiring explicitly unbuilt**; NON-CERTIFIED float K₀ parity resolvent estimate (forecast input); cell-0 forecast from committed K1 magnitudes; frozen gates, feasibility criterion, protocol |
| `p5y_k5_cusum_order3_r3_infrastructure` | R3 infrastructure successor (R1, R2 immutable, pinned file by file) | real-cell authorization registry frozen empty; certified σ-odd (C_o0) and whole-space (C_e0) resolvent bounds at e = 0 (supersolution artifacts with recomputable certified numbers); He₆ extension (j_5, k_6, sup|S_0^(5)|); real CUSUM σ-graded wiring on the frozen Arb stack with fail-closed gated entry; strategies A/B for the first cell, R⁽⁵⁾ source audit; gates R01–R17 |
| `p5y_k5_cusum_order3_r4_tightening` | R4 tightening successor (R1–R3 immutable) | no real cell, no R''' or R⁽⁵⁾ computed; real-cell registry frozen empty; B01 test-power fixtures; exact odd-block C_o0 certificate + independent float cross-check; local first-cell R⁽⁵⁾ majorant and local anchoring lemma; Strategy B against exact truth; certified constant loading with fail-closed real entry; cell-0 forecast and sensitivity grid; gates G01–G17; `PROPOSAL_GOVERNED_FIRST_REAL_CELL.md` present (not read) |
Common: all non-scientific; registries frozen empty; guard DENY for real cells; host `rebaseguard-vultr-02`.

## 6. `p5y_k5_order3_readiness_audit/README.md`

**Verdict: `K5_FULL_CAMPAIGN_RECOMMENDATION = NOT_READY`.** Read-only, additive, non-certifying. Flags:
K5_BRIDGE_THEOREM = PASS (sufficient, not complete; countersignature recommended); K5_ORDER3_PRODUCER_EXISTS = NO (SR:
AUX3_SR_FEASIBILITY_FAIL; CUSUM: order-3 sources only, no F_r:3); K5_SR_K1_INPUTS_EXIST = NO; K5_CUSUM_K1_INPUTS_EXIST =
YES (326-cell composite closure, 2026-09-16); CUSUM_CELLS_PROVABLY_NOT_NEEDING_R3 = 156 of 310 (cells 149–304, every
m ∈ {1,2,3,5}); K5_ORDER3_PROBE = INCONCLUSIVE (not run; oracle precondition unmet); FULL_K5_PRODUCTION_AUTHORIZED = NO.

* Lineage: K2 CLOSED → K3 CLOSED → K1/K4 inputs → K5 bridge (Theorem K5-B) → certified order-3 evidence → K5 feasibility
  oracle (FROZEN_PRE_RESULT, `executed: false`) → adjudication → P5Z. CUSUM order-3 evidence (Aux3/4/5
  `auxiliary_third_derivative_evidence_v1`): magnitudes only; no F_r:3, no signed value.
* What K5 asks: R = R_{D,m}(e) odd, real-analytic, R''(0) = 0, R'(0) = 1 − Γ̃; s(e) := −R(e)/e on (0,2]; **H3a**: s
  continuous and strictly decreasing on (0,2], s(0+) = Γ̃ − 1, s(2) < 1. Numerical content is exactly s' < 0 on (0,2];
  with g(e) := R(e) − eR'(e): g(0) = 0, g' = −eR'', s'(e) = g(e)/e² → H3a reduces to **g < 0 on (0,2]**. Chain:
  certified L_k ≤ inf_{C_k} R''' (new) + K1 R(e0), R'(e0), R''(cell) → per-cell lower bounds l_k, μ_k for R'' (exact
  rational recurrence, MVT) → per-cell upper bounds γ_k, U_k, Γ_k for g → g < 0 → s' < 0 → H3a.
* Order 3 necessary only near zero: R'' odd, R''(0) = 0, every R'' enclosure over the first cell contains 0 (μ_1 ≤ 0),
  |g| = O(e³); a3 = R'''(0)/6 > 0 is the only generic way; a certified R'''(cell 0) < 0 would be a counterexample to H3a.
* Bridge audit PASS with caveats: (1) sufficient, not complete (degenerate cases not certifiable); (2) not independently
  countersigned; (3) **contiguity-dependent**: l_k = max(H_k.lo, l_{k−1} + 2ρ_kL_k) — an order-3 island buys nothing;
  only an unbroken run from cell 0 propagates. Cell 1 special case correct (g ≤ −L_1e³/3 < 0 when L_1 > 0).
* Minimality (K5-B recurrences on 326 certified records with L_k = −∞): cells needing order-3 — m = 1: 0–132; m = 2:
  0–144; m = 3: 0–145; m = 5: 0–148 **and 305–309**; union 0–148 ∪ 305–309 (154); 149–304 (156) discharged for every m.
  CUSUM 0–309 candidate = SUFFICIENT_BUT_NONMINIMAL; near-zero strip fallback (cells 0–221) would have been INSUFFICIENT
  (misses the m = 5 tail cells, which fail near the right end of (0,2]); Z2 never fires (no R2_interval.lo > 0 anywhere); tail carried by the
  direct bound Γ_k.
* **The m = 5 tail is a chain problem, not a local one:** failure Γ_k = g_mid_hi + ρ x M_R2 > 0 driven by curvature slack
  (per-cell example values [TAIL-NUMBER REDACTED]); μ_k improves only through the accumulated l chain. Closing via K5-B
  needs an **unbroken** order-3 run 0–309, or a tightened K1 R'' enclosure on those five cells, or acceptance of
  `K5_INCONCLUSIVE` for m = 5 on the tail drift range ([TAIL-NUMBER REDACTED]). Smallest defensible campaign: 0–148 (149
  cells) for m ∈ {1,2,3} plus a decision on the m = 5 tail.
* Reuse: SR NONE; CUSUM PARTIAL — Aux3/4/5 carry order-3 **source** objects (S_r:3, W_(r,j):3, h_j:3), residuals and
  midpoint error nodes (F:3, D:3, H:3), all `mag_fraction(...)` = unsigned magnitudes → no R''' sign or enclosure
  derivable; missing: F_r:3 (r = 0..4), all-m assembly at order 3, whole-cell fourth-order remainder ρ·T[R,4]; order 0–2
  payload in records is residual bounds, not signed candidate polynomials → an order-3 producer must redo the base
  per-cell solve (full cell cost).
* Producer status (hard blocker): oracle precondition = a governed certified identity-bound order-3 producer exists; SR
  AUX3 feasibility fail (norm-based fourth-order bounds; C·ρ amplification tied by RHO_CAP rule); CUSUM Aux4/5 sources
  only, no F_r:3, no signed export, no fourth-order tower.
* Probe design: frozen oracle sets SR {0, 207, 294}, CUSUM {0, 221, 309} (rule: first cell, last with left < 1/4, last
  meeting (0,2]); CUSUM 221 lies in the provably-unneeded region; better {0, 148, 305} but the frozen set must not be
  edited (new predeclared successor oracle needed).
* Cost model (CUSUM Aux5 production, all 326 cells): 2,069.5 CPU-s/cell (min 2,027, max 2,150), 248 MiB peak RSS,
  281 KiB/record, order-3 source work 172 CPU-s (8.3 %); CUSUM order-3 producer 0.75–1.10 CPU-h/cell → 110–165 CPU-h
  (149 cells) / 230–340 CPU-h (310); SR 16–26 CPU-h/cell → 4,700–7,700 CPU-h (295); host has 4 physical cores, runtime
  pins 4 workers; SR cross-host replay 0/24 bit-identical vs AWS → multi-host must re-qualify determinism.
* What would unblock K5: independent countersignature of K5-B; governed identity-bound certified order-3 producer gated by
  its own feasibility oracle; SR K1 inputs; new predeclared probe oracle. Then authorize 149 CUSUM cells plus an explicit
  m = 5 tail decision, not 310. `FULL_K5_PRODUCTION_LAUNCHED = NO`.
