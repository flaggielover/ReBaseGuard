# Digest: Residual-specific order-0 (RSO) bounds and derivative extensions

Firewalled digest. Sources (NS = `level4/closure_proofs/p5y_k5_tail_overnight_research/`):
`streams/D_309/RESIDUAL_SPECIFIC_309.md`, `streams/D_309/code/d309_rso.py` (review findings from
`reviews/REVIEW_STREAM_D_R1.md` §3 are summarised in SC_SUPNORM.md §11).
Redaction tokens: `[TAIL-NUMBER REDACTED]`, `[TAIL-COMPARISON REDACTED]`, `[LATENT-PROXY REDACTED]`.
All numbers kept are synthetic FSM / discrete LR-family ratios. No CUSUM Λ, E_a[τ] or supersolution value appears in
the sources or here.

---

## 0. Status and route states (header), near-verbatim

Research, target-free. Nothing evaluated on CUSUM m = 5 cells 305–309 or on any drift in [1.2, 2.6]. Validation on
synthetic FSM families with exact truth (`code/d309_rso.py` → `validation/D309_RSO_FSM.json`). Rule S8: committed
history in §1 carries no route factor; route sections carry no tail number.

| route | state |
|---|---|
| RSO-0 (order 0) | **VALIDATED_NON_TARGET** |
| RSO-PM (derivatives, positive majorant) | **VALIDATED_NON_TARGET** |
| RSO-LR order 1 (score form) | **VALIDATED_NON_TARGET** (single drift) |
| RSO-LR order 2 | **THEORY_ONLY** |
| RSO-P (whole TC assembly) | **VALIDATED_NON_TARGET** |
| real use | **BLOCKED** (payloads, U1, U2, U3) |

## 1. History: original definition (quoted, no route factor)

* **C4 §7.1** (`p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md:256-259`): replace `A0‖φ_H‖` by
  `(Ĝ|φ_H|)(a)/D_e`, "a pointwise majorant of the actual residual rather than its sup-norm", which "escapes the floor
  entirely". Ranked first for costing by C4 Condition 7(a) (`:554-556`).
* **Route-audit narrowing** (`p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md:418-431`): the mechanism replaces "at most, the
  residual part `A0·f_H` of TC-T's `A0·p2`", because "`f_G` and `Env4` are norm-only".
* Repair r1 (review N18): the r0 pointer to a committed per-cell share of this term was removed from the document.

The document keeps the original as **RSO-C4** and adds two defined extensions:

| route | acts on | needs |
|---|---|---|
| RSO-C4 (as defined) | the `A0 f_H` term only | — |
| RSO-P | the whole TC radius, through the pointwise Taylor profile of the residual | the order-3 profile from the composite function of SUPNORM_THEOREM.md |
| RSO-PM / RSO-LR | the derivative terms `2A1 p1`, `A2 p0` | — |

The audit's narrowing is correct for RSO-C4 but does not bind RSO-P, which changes exactly the premise that made f_G
and Env4 norm-only.

## 2. Order 0

### 2.1 Theorem RSO-0 (verbatim-close)
**Setting.** X measurable state space; atom a ∈ X; `K_e` positive sub-Markov kernel for each e in a cell C,
`R_e = Σ_j K_e^j`; `φ_e ∈ B(X)` for each e ∈ C.

**Assumptions** (frozen; no sign assumption on any target quantity):
* (R1) ψ: X → [0, ∞) bounded, with `ψ ≥ |φ_e|` on X for every e ∈ C; ψ from a declared class, fixed before any
  evaluation.
* (R2) v: X → [0, ∞) bounded, with `v ≥ ψ + K_e v` on X for every e ∈ C.

**Conclusion.** For every e ∈ C: `|(R_e φ_e)(a)| ≤ (R_e ψ)(a) ≤ v(a)`.

*Proof.* (1) Positivity: `|R_e φ| ≤ R_e|φ| ≤ R_e ψ` pointwise. (2) Induction: `v ≥ Σ_{j<n} K^j ψ + K^n v ≥
Σ_{j<n} K^j ψ`, using v ≥ 0. (3) n → ∞, monotone convergence. (4) No convergence assumption beyond (R2). ∎
(Review: step 2 gives v ≥ R_eψ **pointwise on X**, which RSO-PM needs.)

### 2.2 Occupation-measure characterization
**Identity.** `(R_e ψ)(a) = E_a[τ]·μ_{a,e}(ψ)`, `μ_{a,e}(B) := E_a[Σ_{n<τ} 1_B(X_n)] / E_a[τ]` (normalized expected
occupation measure of the chain started at a, killed at alarm).

**Corollary RSO-G (repair r1, N15: drift explicit).** Against any uniform order-0 atom constant
`A0 ≥ Λ := sup_C E_a[τ]` (Lemma SM(d)), the exact RSO bound improves by

    A0‖ψ‖ / sup_e (R_e ψ)(a)  ≥  (A0/Λ) · (‖ψ‖ / sup_{e∈C} μ_{a,e}(ψ)),

since `sup_e (R_eψ)(a) = sup_e E_a[τ](e) μ_{a,e}(ψ) ≤ Λ · sup_e μ_{a,e}(ψ)`. The **shape factor**
`‖ψ‖ / sup_e μ_{a,e}(ψ) ≥ 1` is the RSO-specific part.

**Equality.** Shape factor = 1 **iff** `ψ = ‖ψ‖` μ_{a,e}-a.e. for some e approaching the sup (single drift: the
majorant equals its sup on everything the chain visits).

### 2.3 Collapse lemma
For `ψ ≡ c`, `v = c·W` with `W ≥ 1 + K_e W`, so `v(a) = c·Ā` — exactly the whole-kernel ARL supply Ā of Lemma Dv′
(`THEOREM_AD.md:91-93`), a member of the refuted uniform-A0 family F1. So RSO is **non-cosmetic iff `ψ ≠ ‖ψ‖` μ-a.e.**
(ψ below its sup on a set with positive expected occupation). (Repair r1, N14: r0's "non-constant on the support of μ"
missed ψ constant on supp μ but larger off it, which also gains.) Constant ψ → F1 again.

### 2.4 Deflated form
`(R_e ψ)(a) = ν_e(ψ)/D_e` (Lemma SM(c)) — this is C4's `(Ĝ_e|φ|)(a)/D_e`. The whole-kernel certificate (R2) needs no
`D_lo` and no taboo resolvent; taboo form is an equivalent alternative.

### 2.5 Declared ψ class for real use
ψ piecewise constant on the frozen reachable-cover boxes `B_j`, `c_j ≥ sup_{B_j} |φ|`. For TC's time-dependent
residual use the pointwise Taylor profile of §4. Box values from rigorous range bounds of the residual
`S − (I−K)F̂` on each box (kernel part via the Hermite closed form of SUPNORM §5). The frozen K1 certifier already
computes per-patch residual ranges ("reachable-set Bernstein range") and keeps only their maximum `δ_mid`; the
per-box values are exactly what it discards.

## 3. Derivative terms

TC's error: `E''(t)(a) = (Rφ'')(a) + 2((∂R)φ')(a) + ((∂²R)φ)(a)`, `∂R = RK₁R`, `∂²R = 2RK₁RK₁R + RK₂R`.

### 3.1 Theorem RSO-PM (positive majorant), verbatim-close
**Assumptions.** `|K_i|` a positive kernel dominating K_i in absolute value (entrywise absolute value on FSM; the
`|∂_e^i φ(z+e)|` weight on CUSUM). With v0 as in (R2) for ψ, on C:

    v1 ≥ |K1(e)| v0 + K_e v1,    v2 ≥ 2|K1(e)| v1 + |K2(e)| v0 + K_e v2,    v1, v2 ≥ 0.

**Conclusion.** For every e ∈ C and every f with `|f| ≤ ψ`: `|((∂R_e) f)(a)| ≤ v1(a)`, `|((∂²R_e) f)(a)| ≤ v2(a)`.

*Proof.* (1) `|(RK₁R f)(a)| ≤ (R|K₁|R|f|)(a) ≤ (R|K₁|v0)(a) ≤ v1(a)` (RSO-0 twice). (2) `|(∂²R f)(a)| ≤
(R[2|K₁|R|K₁|R|f| + |K₂|R|f|])(a) ≤ (R[2|K₁|v1 + |K₂|v0])(a) ≤ v2(a)`. ∎
With `ψ ≡ ‖f‖`, RSO-PM gives norm-type atom constants (members of F1); non-cosmetic only for non-constant ψ.

### 3.2 Theorem RSO-LR (score form)
**Setting.** Location family; drift only through the increment density. CUSUM: `z + e ~ N(0,1)`; score
`S = ∂_e log φ(z+e) = −(z+e)`; update map and window e-free.

**LR identities.** Differentiate `E_a[Σ_{n<τ} f(X_n)]` ({n < τ} measurable in Z_1..Z_n):

    ((∂R) f)(a)  = E_a[Σ_{n<τ} f(X_n) M_n],               M_n := Σ_{k=1}^{n} S_k,
    ((∂²R) f)(a) = E_a[Σ_{n<τ} f(X_n) (M_n² − n)]        (Gaussian: ∂_e S = −1)

(ψ-weighted generalization of `streams/C_308/IDEA_LR_SCORE_CONSTANTS.md`, which treats ψ ≡ 1; general family: Σ ∂_eS_k
in place of −n.)

**Pointwise bound (order 1).** `|((∂R) f)(a)| ≤ A1^ψ := E_a[Σ_{n<τ} ψ(X_n)|M_n|]` for |f| ≤ ψ.

**Certificate (order 1; proved).** Augmented chain `(X_n, M_n)`, ansatz `V(x, μ) = α(x) + β(x)μ²`; use
`|μ| ≤ (c + μ²/c)/2` and `2μq ≤ δμ² + q²/δ` (constants c, δ > 0). Then `V ≥ ψ|μ| + E[V(X', μ + S) 1_surv]` follows
from two **linear** supersolution inequalities on X:

    β ≥ K β + ψ/(2c) + δ,       α ≥ K α + ψ c/2 + K^{S²} β + (K^S β)²/δ,       α, β ≥ 0,

`(K^{S^j} g)(x) = E[g(X') S^j 1_surv]`; `K^S = K₁` and, for the Gaussian, `K^{S²} = K₂ + K`. Then `A1^ψ ≤ α(a)`.
*Proof of the reduction.* Substitute the ansatz; μ² coefficient and constant term are the two inequalities; cross
term absorbed by `2μK^Sβ ≤ δμ² + (K^Sβ)²/δ`; V ≥ 0 and the supersolution argument give `V ≥ E[Σ ψ|μ + M_n|]`; at μ = 0
`A1^ψ ≤ α(a)`. ∎ (Review: RHS = ψ|μ| + Kα + μ²Kβ + 2μK^Sβ + K^{S²}β; the two AM–GM inequalities give exactly the two
linear inequalities.)

**Order 2 (THEORY_ONLY).** Quartic ansatz `V = α + βμ² + γμ⁴` with `|μ² − n|` via an extra state component n. Not
implemented.

## 4. Theorem RSO-P (whole TC radius from pointwise profiles), verbatim-close

**Pointwise profile.** For `s = |t − e0| ≤ ρ`, Taylor pointwise in x, with Ĝ = 0:

    |φ''(t)(x)| ≤ a2(x) + s a3(x) + (s²/2) a4(x),
    a_j := |φ^(j)(e0)|  (j ≤ 3),     a4(x) := sup_{u∈C} |φ⁗(u)(x)|.

φ'(t), φ(t) bounded likewise one and two orders further. Let `N0[a], N1[a], N2[a]` be RSO-0 and RSO-PM certificate
values for a source vector a. By linearity of R,

    rad_RSO(s) = N0[a2] + s N0[a3] + (s²/2) N0[a4]
               + 2( N1[a1] + s N1[a2] + (s²/2) N1[a3] + (s³/6) N1[a4] )
               + N2[a0] + s N2[a1] + (s²/2) N2[a2] + (s³/6) N2[a3] + (s⁴/24) N2[a4],

and `|F_r''(t)(a) − Ĥ_r(a)| ≤ rad_RSO(|t − e0|)` for every t in the cell.
*Proof.* TC §4 steps 1–3 with Lemma G replaced by RSO-0 and RSO-PM applied to the pointwise profiles. ∎

**Variants** (implemented, `d309_rso.py` `r4`): **RSO-C4** only `A0 f_H → N0[a2]`, rest TC-T; **RSO-P-normonly34**
a3, a4 replaced by constants f_G^sur and Env4 (no SC); **RSO-P-box_g** profiles grouped into boxes of g states
(g = 1 pointwise; g = n constant per component = F1-type collapse combined with SC's composite norms). RSO-specific
gain in isolation = `box_1 / box_n`.

## 5. Machine-checkable certificate (§5)
**Record:** kernel spec and drift block `[e_lo, e_hi]`; box cover of X; ψ value per box with the range certificate
bounding |φ| on it; the supersolution v (polynomial on (p, m) or per-box values); per box a rigorous lower bound of
`min_{x∈box, e∈block} [v − ψ − K_e v]`; lower bound of `min v`. **Acceptance:** every margin ≥ 0 and v ≥ 0.
**Verifier:** re-evaluates every enclosure (for CUSUM: stdlib box/panel technique of the I2 certifier,
`c11_certifier.supersolution_margin` with source 1 replaced by ψ, plus interval drift). FSM implementation checks every
certificate twice (Taylor-form bisection lower bound; 256-point grid minimum minus (h/2)·sup|q'|) and accepts only when
both pass. Construction `v = λ R_{e0} b + η‖b‖ R_{e0} 1` on a declared (λ, η) ladder (tightness only, never validity).
No sign of any target quantity used (two-sided |·|).

## 6. Validation (target-free; `validation/D309_RSO_FSM.json`; declared rule `d309_rso.py:42-50`)

Certificates and soundness (48 cases = 12 families × 4 ψ classes): every N0, N1, N2 passes both checks; soundness vs
exact truth on a 17-point drift grid: `N0 ≥ max_e (R_e a)(a)`, `N1 ≥ max_e (R_e|K1|R_e a)(a)`, `N2 ≥` PM2 truth,
`N1, N2 ≥` signed |(∂R f)(a)|, |(∂²R f)(a)| for f = ±a — all hold. Certificate overhead N0 / max_e (R_e a)(a):
1.003–1.139.

Shape classes (synthetic):
| class | shape factor μ(ψ)/‖ψ‖ | N0/(Λ‖ψ‖) |
|---|---|---|
| generic TC residual |φ''(e0)| | 0.30–0.78 | 0.30–0.81 |
| favourable (mass on least-occupied states) | 0.20–0.36 | 0.20–0.37 |
| mass on most-occupied state | 0.37–0.52 | 0.39–0.53 |
| constant ψ (adversarial: no gain) | 1.00 | 1.003–1.017 (≥ 1, as collapse lemma requires) |

(These are dimensionless ratios on synthetic FSM families; no Λ value is reported.)

Derivative terms (RSO-PM vs Lemma G): N1/(A1‖ψ‖) 0.063–0.836; N2/(A2‖ψ‖) 0.068–0.736; signed truth / N1 0.015–0.64
(PM loose relative to the signed functional; LR form addresses this).

TC assembly (12 fixtures × 33 points × 6 variants = 2376 checks): 0 violations of |F''(t)(a) − Ĥ(a)| ≤ rad(|t − e0|);
genuine worst dev/rad 0.98 (RSO-P-box1); power against planted every-component-halved profile only 4/12 → weak
necessary condition; load-bearing evidence = truth-relative certificate checks. rad(ρ)/TCT_base (synthetic): RSO-C4
0.957–1.000; RSO-P-normonly34 0.798–1.002; RSO-P-box1 0.099–0.481; box2 0.122–0.556; boxn 0.145–0.739; RSO-specific
factor box1/boxn 0.29–0.78.

Structural reading (generic, not forecasts): RSO-C4 acts only on the order-0 residual term, small whenever premise
residuals are small relative to ρ f_G and ρ² Env4; without SC's pointwise composite RSO barely moves the radius
(normonly34); the route becomes material only as RSO-P ∘ SC.

LR order 1 (12 cases: L ∈ {4, 5, 6}, e ∈ {1/8, 1/4}, two ψ; exact rationals): kernel identity K^S = K₁ exact 12/12;
signed LR path sum (N = 60) matches (RK₁Rf)(a) within 2.1·10⁻⁸, surviving mass ≤ 10⁻⁸; ordering
`|(∂R f)(a)| ≤ truncated lower bound of A1^ψ ≤ certificate α(a)` 12/12. Ratios: exact LR lower bound / path-level PM
0.41–0.58 (triangle inside M_n costs ≈ 2×); LR certificate / entrywise PM 0.74–0.87; LR certificate / norm bound
k₁C²‖ψ‖ 0.015–0.28. Certificate recovers only part of the LR gap (constant c, δ); per-state c(x), δ(x) not implemented.

Controls through the code path (repair r1, review B1; r0 (a) and (c) withdrawn as arithmetic):
| control | planted into | checker | flagged |
|---|---|---|---|
| (a1) ψ := 0 at most-occupied state | `cert_chain` | N0 ≥ exact max_e (R_e a)(a) | 44/48 |
| (a1) same | `cert_chain` | N1 ≥ exact PM1 truth | 34/48 |
| (a2) ψ := a/2 | `cert_chain` | N0 ≥ exact truth | 48/48 |
| (a2) same | `cert_chain` | N1 ≥ exact PM1 truth | 48/48 |
| (b) v := (9/10) v_cert | `check_cert_taylor` | margin ≥ 0 | 48/48 |
| (c1) cross term (K^Sβ)²/δ dropped | `lr_certificate` | α(a) ≥ exact truncated lower bound of A1^ψ | 4/12 |
| (c2) K^{S²}β dropped | `lr_certificate` | same | 12/12 |
| (c3) ψc/2 dropped | `lr_certificate` | same | 12/12 |
| (d) wrong score S(z) := z | LR kernel builder | K^S = K₁ exactly | 12/12 |
| (e) every profile component halved | `rso_poly` → enclosure check | exact F''(t)(a) | 4/12 |
Misses are power limits: (a1) may still exceed truth when the most-occupied state carries little residual; (c1) AM–GM
slack covers truth; (e) radius loose.

## 7. Data blocker for real use (§7)
* ψ requires pointwise residual information: candidate payloads (never serialized, 0/326, C6 README:41-50); per-box
  residual ranges (computed and discarded by the frozen certifier); for RSO-P the SC composite function. None exists
  for any real cell (SUPNORM §8).
* Regeneration needs a replay host (**U1**); new quantity derives from P3 records → C6 Condition 10 (**U2**).
* The supersolution certificate is stdlib-computable like I2 but needs kernel evaluation at the cell's drift block —
  quarantined tonight.
* Governance: **CLOSURE-ONLY** under floor r2 (changes a consumer term, not a Lemma G / Dv′ supply) → **U3**.

## 8. Kill gates and verdict (§8)
| gate | RSO-0 / RSO-PM / RSO-P | RSO-LR |
|---|---|---|
| G1 | PASS: Lemma SM(d) sharp only at f = 1 (C4 :256-259); shape factor structural | PASS: sign cancellation of K₁, K₂ (C_308 note) |
| G2 | PASS: proofs §2–§4 | PASS order 1; order 2 THEORY_ONLY |
| G3 | PASS: (R1), (R2), declared ψ class | PASS: single drift; block uniformity not implemented |
| G4 | PASS | PASS |
| G5 | PASS on FSM incl. favourable/adversarial classes | PASS on discrete LR families |
| G6 | PASS for mathematics (review R1 re-derived RSO-0, RSO-PM, RSO-P); two independent certificate checks | PASS for order-1 reduction (review R1) |
| G7–G9 | PASS (certificate format freezable) | PASS |
| G10 | PASS **iff ψ ≠ ‖ψ‖ μ-a.e.** (N14); constant ψ → F1 | PASS (below PM and norm in every case) |

**Verdict.** RSO-C4 as originally defined is **valid but structurally narrow** (order-0 term only). RSO-P (with SC) is
the form with reach. FREEZE_READY: **no** (payloads, U1–U3).

---

## 9. `d309_rso.py` — functions, formulas, data needed

Target-free (no CUSUM cell, no committed tail value, no band drift); imports `d309_core` (FSM machinery); every drift
entry calls `guard_interval`/`Q.guard_drift` (added in `abs_sup_matrix`, `check_cert_taylor`, `check_cert_grid`,
`LRFamily.kernel`, `LRFamily.kernel_deriv` per review N8).

DECLARED_RULE (fixed before first run): R1–R4 generic seeds 1..12, n = 4 + seed%4, kernel degree 4, e0 = 1/8,
ρ = (1/64, 1/32, 1/16)[seed%3], pert = (1e-6, 1e-4, 1e-2)[(seed//3)%3], source degree (2, 5)[seed%2], one source,
Ĝ := 0. R3 classes: FAVOURABLE a = 1 on states with exact occupation at e0 below median, 1/100 elsewhere;
ADVERSARIAL-ATOM a = 1 on the most occupied state, 1/100 elsewhere; ADVERSARIAL-CONST a = 1. Ladder
λ ∈ {1, 1+2^-10, 1+2^-8, 1+2^-6, 1+2^-4, 1+2^-2, 2}, η/‖b‖ ∈ {2^-12, 2^-8, 2^-5, 2^-3, 2^-1, 1, 4}. Box classes g ∈
{1, 2, n}. Drift grid 17 points. R5: discrete LR families on states 0..L−1 (L ∈ {4,5,6}), z ∈ {−1, 0, 1},
p_e(z) = p0(z)(1 + e z + e² c (z² − m2)), p0 = (1/4, 1/2, 1/4), c = 1/2, e ∈ {1/8, 1/4}, e-independent killing 1/4,
x' = max(0, x + z), alarm iff x + z ≥ L; ψ = 1/100 + x/L and ψ = indicator of top state; c ∈ 2^{−4..4}, δ ∈ 2^{−8..2};
path enumeration N = 60.

Functions:
* `abs_sup_matrix(fam, i, lo, hi)`: entrywise rigorous sup |K_i(e)_{xy}| over the cell.
* `margin_poly(fam, v, x)`: v_x − Σ_y K_xy(e) v_y as a polynomial in e.
* `check_cert_taylor(fam, lo, hi, v, b)`: rigorous lower bound of min_x min_e [v_x − (K_e v)_x − b_x] (Taylor-form
  bisection `min_on`).
* `check_cert_grid(...)`: independent bound: 256-point grid minimum minus (h/2)·sup|q'| (crude coefficient bound).
* `certify(fam, e0, ρ, b)`: v = λ R_{e0} b + η‖b‖ R_{e0} 1 over the ladder, sorted by v(a); accept first pair with v ≥ 0
  and both margins ≥ 0 (`verified_twice`).
* `cert_chain(fam, e0, ρ, a, K1abs, K2abs)`: N0 = certify(a); b1 = |K1| v0 → N1; b2 = 2|K1| v1 + |K2| v0 → N2
  (RSO-PM).
* `truth_grid`: exact max over drifts of (R a)(a), PM1 = R|K1|R a, PM2 = R(2|K1|PM1 + |K2|Ra), signed |RK1Rf|,
  |2RK1RK1Rf + RK2Rf| for random-sign f = ±a, and Λ-grid max Σ R[0] (used only as a normalizer for synthetic ratios).
* `occupation(fam, e0)`: normalized occupation R[0]/ΣR[0].
* `r123(seed)`: R1–R3 plus controls (a1, a2, b).
* `r4(seed)`: TC assembly: a_j = |φ^(j)(e0)| (j ≤ 3), a4 = whole-cell sup |φ⁗|; base TCT radius (f_G^sur, E0);
  `rso_poly` builds rad(s) = [N0[a2], N0[a3], N0[a4]/2] + 2[N1[a1], N1[a2], N1[a3]/2, N1[a4]/6] + [N2[a0], N2[a1],
  N2[a2]/2, N2[a3]/6, N2[a4]/24]; variants RSO_C4 (base + N0[a2] − A0 f_H), RSO_P_normonly34, RSO_P_box{1,2,n}
  (`group_max`); enclosure check on 33 points; halved-profile mutant.
* `LRFamily(L, c, kappa)`: `pz(z, e, der)`, `score`, `nxt`, `kernel(e, weight)` (weighted kernel K^{S^j} when weight =
  S^j), `kernel_deriv(e, der)`.
* `lr_certificate(fam, e, ψ, defect)`: for each (c, δ) on the grid: β = R(ψ/(2c) + δ), α = R(ψc/2 + K^{S²}β +
  (K^Sβ)²/δ); best α(a); defects drop_cross, drop_KS2, drop_psi.
* `lr_paths(fam, e, ψ, f, N)`: exact truncated path sums E_a[Σ ψ(X_n)|M_n|] (lower bound) and E_a[Σ f(X_n) M_n].
* `r5()`: kernel identity K^S = K1, wrong-score control, exact signed functional, paths, certificate, PM entrywise and
  pathwise, norm bound k1 C² ‖ψ‖, controls (c).
* Data needed: synthetic only (ov_fixtures families; LR toy families). No CUSUM data.
