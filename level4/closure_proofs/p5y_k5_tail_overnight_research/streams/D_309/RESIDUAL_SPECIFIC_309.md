# Residual-specific order-0 (RSO) bounds and their derivative extensions

**Status.** Research, target-free. Nothing here was evaluated on CUSUM m = 5 cells 305–309, or on any drift in
[1.2, 2.6]. Validation is on synthetic FSM families with exact truth (`code/d309_rso.py` →
`validation/D309_RSO_FSM.json`). Rule S8: committed history in §1 carries no route factor, and route sections carry no
tail number.

**Route states.**
| route | state |
|---|---|
| RSO-0 (order 0) | **VALIDATED_NON_TARGET** |
| RSO-PM (derivatives, positive majorant) | **VALIDATED_NON_TARGET** |
| RSO-LR order 1 (score form) | **VALIDATED_NON_TARGET** (single drift) |
| RSO-LR order 2 | **THEORY_ONLY** |
| RSO-P (whole TC assembly) | **VALIDATED_NON_TARGET** |
| real use | **BLOCKED** (payloads, U1, U2, U3) |

## 1. History: how the route was originally defined (quoted, no route factor)

* **C4 §7.1** (`p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md:256-259`): replace `A0‖φ_H‖` by
  `(Ĝ|φ_H|)(a)/D_e`, "a pointwise majorant of the actual residual rather than its sup-norm", which "escapes the floor
  entirely". Ranked first for costing by C4 Condition 7(a) (`:554-556`).
* **Route-audit narrowing** (`p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md:418-431`): the mechanism replaces "at most, the
  residual part `A0·f_H` of TC-T's `A0·p2`", because "`f_G` and `Env4` are norm-only".
* (Repair r1, review N18: the r0 pointer to a committed per-cell share of this term was removed from this document,
  because the same document reports synthetic RSO-C4 ratios in §6 and a reader could combine the two.)

**This document keeps the original definition as RSO-C4.** It adds two extensions, which are defined, not
reinterpreted:

| route | acts on | needs |
|---|---|---|
| **RSO-C4** (as defined) | the `A0 f_H` term only | — |
| **RSO-P** | the whole TC radius, through the pointwise Taylor profile of the residual | the order-3 profile comes from the composite function of `SUPNORM_THEOREM.md` |
| **RSO-PM / RSO-LR** | the derivative terms `2A1 p1`, `A2 p0` | — |

The route audit's narrowing is **correct for RSO-C4**. It does not bind RSO-P, because RSO-P changes exactly the
premise that made `f_G` and Env4 norm-only.

## 2. Order 0

### 2.1 Theorem RSO-0

**Setting.**
* X is a measurable state space; the atom `a ∈ X`.
* `K_e` is a positive sub-Markov kernel for each e in a cell C, and `R_e = Σ_j K_e^j`.
* `φ_e ∈ B(X)` for each `e ∈ C`.

**Assumptions** (frozen; no sign assumption on any target quantity):
* (R1) ψ: X → [0, ∞) is bounded, with `ψ ≥ |φ_e|` on X for every `e ∈ C`. ψ is taken from a declared class, fixed
  before any evaluation.
* (R2) v: X → [0, ∞) is bounded, with `v ≥ ψ + K_e v` on X for every `e ∈ C`.

**Conclusion.** For every `e ∈ C`: `|(R_e φ_e)(a)| ≤ (R_e ψ)(a) ≤ v(a)`.

*Proof.*
1. Positivity gives `|R_e φ| ≤ R_e|φ| ≤ R_e ψ` pointwise.
2. By induction, `v ≥ Σ_{j<n} K^j ψ + K^n v ≥ Σ_{j<n} K^j ψ`, using `v ≥ 0`.
3. Let n → ∞; the series converges monotonically.
4. No convergence assumption beyond (R2) is needed. ∎

### 2.2 Occupation-measure characterization

**Identity.** `(R_e ψ)(a) = E_a[τ]·μ_{a,e}(ψ)`, where

    μ_{a,e}(B) := E_a[Σ_{n<τ} 1_B(X_n)] / E_a[τ]

is the normalized expected occupation measure of the chain started at a and killed at alarm.

**Corollary RSO-G (repair r1, review N15: the drift is now explicit).** Against any uniform order-0 atom constant
`A0 ≥ Λ := sup_C E_a[τ]` (Lemma SM(d)), the exact RSO bound improves by the factor

    A0‖ψ‖ / sup_e (R_e ψ)(a)  ≥  (A0/Λ) · (‖ψ‖ / sup_{e∈C} μ_{a,e}(ψ)),

because `sup_e (R_eψ)(a) = sup_e E_a[τ](e) μ_{a,e}(ψ) ≤ Λ · sup_e μ_{a,e}(ψ)`. The second factor, the **shape factor**
`‖ψ‖ / sup_e μ_{a,e}(ψ) ≥ 1`, is the RSO-specific part.

**Equality.** The shape factor is 1 **iff** `ψ = ‖ψ‖` `μ_{a,e}`-a.e. for some `e` approaching the sup. At a single
drift: the majorant equals its sup on everything the chain visits.

### 2.3 Collapse lemma

For `ψ ≡ c`, `v = c·W` with `W ≥ 1 + K_e W`, so `v(a) = c·Ā`. That is exactly the whole-kernel ARL supply `Ā` of
Lemma Dv′ (`THEOREM_AD.md:91-93`), a member of the refuted uniform-A0 family F1.

So RSO is **non-cosmetic iff `ψ ≠ ‖ψ‖` μ-a.e.**, i.e. iff ψ is below its sup on a set the chain visits with
positive expected occupation. (Repair r1, review N14: r0 said "non-constant on the support of μ", which misses ψ
constant on supp μ but larger off it; that case also gains.) With a constant ψ it is F1 again.

### 2.4 Deflated form

`(R_e ψ)(a) = ν_e(ψ)/D_e` (Lemma SM(c)). This is C4's `(Ĝ_e|φ|)(a)/D_e`. The whole-kernel certificate (R2) needs no
`D_lo` and no taboo resolvent; the taboo form is an equivalent alternative.

### 2.5 Declared ψ class for real use

ψ is piecewise constant on the frozen reachable-cover boxes `B_j`, with `c_j ≥ sup_{B_j} |φ|`.
* For TC's time-dependent residual, use the pointwise Taylor profile of §4.
* The box values come from rigorous range bounds of the residual on each box. The residual is `S − (I−K)F̂`, whose
  kernel part has the Hermite closed form of `SUPNORM_THEOREM.md` §5.
* The frozen K1 certifier already computes per-patch residual ranges ("reachable-set Bernstein range") and keeps only
  their maximum, `δ_mid`. The per-box values are exactly what it discards.

## 3. Derivative terms

TC's error is `E''(t)(a) = (Rφ'')(a) + 2((∂R)φ')(a) + ((∂²R)φ)(a)`, with `∂R = RK₁R` and `∂²R = 2RK₁RK₁R + RK₂R`.

### 3.1 Theorem RSO-PM (positive majorant)

**Assumptions.** Let `|K_i|` be a positive kernel dominating `K_i` in absolute value: the entrywise absolute value
(FSM), or the `|∂_e^i φ(z+e)|` weight (CUSUM). With v0 as in (R2) for ψ, suppose that on C

    v1 ≥ |K1(e)| v0 + K_e v1,    v2 ≥ 2|K1(e)| v1 + |K2(e)| v0 + K_e v2,    v1, v2 ≥ 0.

**Conclusion.** For every `e ∈ C` and every f with `|f| ≤ ψ`:

    |((∂R_e) f)(a)| ≤ v1(a),    |((∂²R_e) f)(a)| ≤ v2(a).

*Proof.*
1. `|(RK₁R f)(a)| ≤ (R|K₁|R|f|)(a) ≤ (R|K₁|v0)(a) ≤ v1(a)`, applying RSO-0 twice.
2. Likewise `|(∂²R f)(a)| ≤ (R[2|K₁|R|K₁|R|f| + |K₂|R|f|])(a) ≤ (R[2|K₁|v1 + |K₂|v0])(a) ≤ v2(a)`. ∎

With `ψ ≡ ‖f‖`, RSO-PM gives norm-type atom constants, i.e. members of F1. As at order 0, the route is non-cosmetic only
for non-constant ψ.

### 3.2 Theorem RSO-LR (score form)

**Setting.** For a location family, the drift enters only through the increment density:
* CUSUM: `z + e ~ N(0,1)`;
* score `S = ∂_e log φ(z+e) = −(z+e)`;
* the update map and the window are e-free.

**Likelihood-ratio identities.** Differentiate `E_a[Σ_{n<τ} f(X_n)]`, where `{n < τ}` is measurable in `Z_1..Z_n`:

    ((∂R) f)(a)  = E_a[Σ_{n<τ} f(X_n) M_n],               M_n := Σ_{k=1}^{n} S_k,
    ((∂²R) f)(a) = E_a[Σ_{n<τ} f(X_n) (M_n² − n)]        (Gaussian: ∂_e S = −1)

This is the ψ-weighted generalization of `streams/C_308/IDEA_LR_SCORE_CONSTANTS.md`, which treats ψ ≡ 1. For a general
parametric family the second identity has `Σ ∂_e S_k` in place of `−n`.

**Pointwise bound (order 1).** `|((∂R) f)(a)| ≤ A1^ψ := E_a[Σ_{n<τ} ψ(X_n)|M_n|]` for `|f| ≤ ψ`.

**Certificate (order 1; proved).**
* Take the augmented chain `(X_n, M_n)` and the ansatz `V(x, μ) = α(x) + β(x)μ²`.
* Use `|μ| ≤ (c + μ²/c)/2` and `2μ q ≤ δμ² + q²/δ`, for constants c, δ > 0.
* The inequality `V ≥ ψ|μ| + E[V(X', μ + S) 1_surv]` then follows from two **linear** supersolution inequalities on X:

      β ≥ K β + ψ/(2c) + δ,       α ≥ K α + ψ c/2 + K^{S²} β + (K^S β)²/δ,       α, β ≥ 0,

  where `(K^{S^j} g)(x) = E[g(X') S^j 1_surv]`. Note `K^S = K₁` and, for the Gaussian, `K^{S²} = K₂ + K`.
* Then `A1^ψ ≤ α(a)`.

*Proof of the reduction.* Substitute the ansatz. The μ² coefficient and the constant term are the two inequalities; the
cross term is absorbed by `2μ K^Sβ ≤ δμ² + (K^Sβ)²/δ`. `V ≥ 0` and the standard supersolution argument (as in RSO-0)
give `V ≥ E[Σ ψ|μ + M_n|]`. At μ = 0 this is `A1^ψ ≤ α(a)`. ∎

**Order 2 (THEORY_ONLY).** A quartic ansatz `V = α + βμ² + γμ⁴` with `|μ² − n|` handled through an extra state
component n. Not implemented tonight.

## 4. Theorem RSO-P (the whole TC radius from pointwise profiles)

**Pointwise profile.** For `s = |t − e0| ≤ ρ`, Taylor's theorem applied **pointwise in x** gives, with Ĝ = 0,

    |φ''(t)(x)| ≤ a2(x) + s a3(x) + (s²/2) a4(x),
    a_j := |φ^(j)(e0)|  (j ≤ 3),     a4(x) := sup_{u∈C} |φ⁗(u)(x)|.

`φ'(t)` and `φ(t)` are bounded likewise, one and two orders further. Let `N0[a]`, `N1[a]`, `N2[a]` be the RSO-0 and
RSO-PM certificate values for a source vector a. By linearity of R,

    rad_RSO(s) = N0[a2] + s N0[a3] + (s²/2) N0[a4]
               + 2( N1[a1] + s N1[a2] + (s²/2) N1[a3] + (s³/6) N1[a4] )
               + N2[a0] + s N2[a1] + (s²/2) N2[a2] + (s³/6) N2[a3] + (s⁴/24) N2[a4],

and `|F_r''(t)(a) − Ĥ_r(a)| ≤ rad_RSO(|t − e0|)` for every t in the cell.

*Proof.* Theorem TC §4 steps 1–3, with Lemma G replaced by RSO-0 and RSO-PM applied to the pointwise profiles
(`|φ^(j)(t)| ≤` the profile, pointwise). ∎

**Variants** (all implemented, `d309_rso.py:235-304`):
* **RSO-C4.** Only `A0 f_H → N0[a2]`; everything else stays TC-T (`:282`).
* **RSO-P-normonly34.** a3 and a4 replaced by the constants `f_G^sur` and Env4, i.e. without SC (`:284`).
* **RSO-P-box_g.** Pointwise profiles grouped into boxes of g states: g = 1 is pointwise; g = n is constant per
  component, which is the F1-type collapse combined with SC's composite norms (`:285-286`).

The RSO-specific gain in isolation is the ratio `box_1 / box_n`.

## 5. Machine-checkable certificate

**Record.**
* the kernel specification and drift block `[e_lo, e_hi]`;
* the box cover of X;
* the ψ value per box, with the range certificate that bounds `|φ|` on that box;
* the supersolution v (a polynomial on (p, m), or per-box values);
* for every box, a rigorous lower bound of `min_{x∈box, e∈block} [v − ψ − K_e v]`;
* the lower bound of `min v`.

**Acceptance.** Every margin ≥ 0 and `v ≥ 0`.

**Verifier.** Re-evaluates every enclosure. For CUSUM this is the stdlib-only box/panel technique of the I2 certifier
(`c11_certifier.supersolution_margin`, with source 1 replaced by ψ) plus interval drift.

**The FSM implementation checks every certificate twice** by two independent rigorous methods and accepts only when
both pass:
1. the Taylor-form bisection lower bound of the per-state polynomial margin in e (`code/d309_rso.py:75-77`);
2. a 256-point grid minimum minus `(h/2)·sup|q'|` (`:80-92`).

The construction is `v = λ R_{e0} b + η‖b‖ R_{e0} 1` on a declared (λ, η) ladder (`:95-117`). The ladder choice affects
tightness only, never validity.

**Sign.** No sign of any target quantity is used: every bound is two-sided in `|·|`.

## 6. Validation (target-free)

**Declared rule:** `code/d309_rso.py:42-50`. **Output:** `validation/D309_RSO_FSM.json`.

### Certificates and soundness (48 cases: 12 families × 4 ψ classes)

* **Certificates:** every one (N0, N1, N2) passes both independent checks.
* **Soundness against exact truth,** on a 17-point drift grid per cell:
  * `N0 ≥ max_e (R_e a)(a)`;
  * `N1 ≥ max_e (R_e|K1|R_e a)(a)`;
  * `N2 ≥` the PM2 truth;
  * `N1, N2 ≥` the **signed** `|(∂R f)(a)|`, `|(∂²R f)(a)|` for random-sign `f = ±a`.
  All hold in every case.
* **Certificate overhead** `N0 / max_e (R_e a)(a)` is 1.003–1.139.

### Shape classes (the structural claim of §2.2; synthetic)

| class | shape factor `μ(ψ)/‖ψ‖` | `N0/(Λ‖ψ‖)` |
|---|---|---|
| generic TC residual `|φ''(e0)|` | 0.30–0.78 | 0.30–0.81 |
| favourable (mass on the least-occupied states) | 0.20–0.36 | 0.20–0.37 |
| mass on the most-occupied state | 0.37–0.52 | 0.39–0.53 |
| **constant ψ (adversarial: no gain)** | **1.00** | **1.003–1.017** (≥ 1, as the collapse lemma requires) |

Concentrating ψ on the single most-occupied state still leaves a gain equal to that state's occupation share. Only a
ψ flat on the occupation support gives nothing.

### Derivative terms (RSO-PM vs Lemma G)

| ratio | range |
|---|---|
| `N1 / (A1‖ψ‖)` | 0.063–0.836 |
| `N2 / (A2‖ψ‖)` | 0.068–0.736 |
| signed truth `/ N1` | 0.015–0.64 (PM is loose relative to the signed functional; the LR form addresses this) |

### TC assembly (12 fixtures × 33 grid points × 6 variants = 2376 checks; `:235-304`)

* **Soundness:** 0 violations of `|F''(t)(a) − Ĥ(a)| ≤ rad(|t − e0|)`. The check has some power here (genuine worst
  deviation/radius 0.98 for RSO-P-box1). Its measured power against a planted profile with every component halved is
  only 4/12 (`R4_mutant_profile_half_detected`), so it is a weak necessary condition. The load-bearing RSO evidence is
  the truth-relative certificate checks of §6 (N0, N1, N2 ≥ the exact functionals).

`rad(ρ)` relative to TCT_base, synthetic:

| variant | range |
|---|---|
| RSO-C4 | 0.957–1.000 |
| RSO-P-normonly34 | 0.798–1.002 |
| RSO-P-box1 | 0.099–0.481 |
| RSO-P-box2 | 0.122–0.556 |
| RSO-P-boxn | 0.145–0.739 |
| **RSO-specific factor `box1/boxn`** | **0.29–0.78** |

**Structural reading.** These are generic statements, not forecasts:
* RSO-C4 acts only on the order-0 residual term, which is small whenever the premise residuals are small relative to
  `ρ f_G` and `ρ² Env4`.
* Without SC's pointwise composite, RSO barely moves the radius (normonly34).
* The route becomes material only as RSO-P ∘ SC.

### LR order 1 (12 cases: L ∈ {4, 5, 6}, e ∈ {1/8, 1/4}, two ψ; exact rationals; `:353-445`)

**Exact checks.**
* The kernel identity `K^S = K₁` holds exactly in 12/12.
* The signed LR path sum (N = 60) matches `(RK₁Rf)(a)` to within 2.1·10⁻⁸; the surviving mass is ≤ 10⁻⁸.
* The ordering holds in 12/12:

      |(∂R f)(a)|  ≤  truncated lower bound of A1^ψ  ≤  certificate α(a)

**Ratios.**

| ratio | range |
|---|---|
| exact LR lower bound / path-level PM | 0.41–0.58 (the triangle inside `M_n` costs about 2×) |
| LR certificate / entrywise PM | 0.74–0.87 |
| LR certificate / norm bound `k₁C²‖ψ‖` | 0.015–0.28 |

The certificate recovers only part of the LR gap: AM–GM with constant (c, δ). Per-state c(x), δ(x) is the obvious
tightening and is not implemented.

### Controls through the code path (repair r1, review B1)

The r0 controls (a) and (c) were arithmetic on constructed values and could not fail. They are **withdrawn**. The
controls below plant an invalid input **into the function under test** and require a truth-relative checker to flag it
(`d309_rso.py`, `r123` and `r5`):

| control | planted into | checker | flagged |
|---|---|---|---|
| (a1) ψ := 0 at the most-occupied state (invalid majorant) | `cert_chain` | N0 ≥ exact `max_e (R_e a)(a)` | 44/48 |
| (a1) same | `cert_chain` | N1 ≥ exact PM1 truth | 34/48 |
| (a2) ψ := a/2 | `cert_chain` | N0 ≥ exact truth | 48/48 |
| (a2) same | `cert_chain` | N1 ≥ exact PM1 truth | 48/48 |
| (b) v := (9/10) v_cert | `check_cert_taylor` | margin ≥ 0 | 48/48 |
| (c1) cross term `(K^Sβ)²/δ` dropped | `lr_certificate` | α(a) ≥ exact truncated lower bound of A1^ψ | 4/12 |
| (c2) `K^{S²}β` term dropped | `lr_certificate` | same | 12/12 |
| (c3) `ψc/2` term dropped | `lr_certificate` | same | 12/12 |
| (d) wrong score S(z) := z | LR kernel builder | `K^S = K₁` exactly | 12/12 |
| (e) every pointwise profile component halved | `rso_poly` → enclosure check | exact `F''(t)(a)` | 4/12 |

Misses are power limits, not failures:
* **(a1)** is invalid but can still produce a certificate above the truth when the most-occupied state carries little
  residual.
* **(c1)** removes only the cross term, and the remaining AM–GM slack can still cover the truth.
* **(e)** is weak because the radius is loose.

## 7. Data blocker for real use (honest)

* **ψ requires pointwise residual information.** That means:
  * the candidate payloads, which were never serialized (0/326 records, C6 README:41-50);
  * the per-box residual ranges, which the frozen certifier computes and discards;
  * for RSO-P, the SC composite function.

  None exists for any real cell, target or not (`SUPNORM_THEOREM.md` §8).
* **Regeneration** needs a replay host (U1).
* **The new quantity** derives from P3 records, so C6 Condition 10 applies (U2).
* **The supersolution certificate itself** is stdlib-computable, like I2. It needs kernel evaluation at the cell's drift
  block, which is quarantined tonight.
* **Governance: CLOSURE-ONLY under floor r2.** RSO changes a consumer term and is not a Lemma G / Lemma Dv′ supply, so it
  needs U3.

## 8. Kill gates

| gate | RSO-0 / RSO-PM / RSO-P | RSO-LR |
|---|---|---|
| G1 | PASS: Lemma SM(d) is sharp only at f = 1 (C4 :256-259); the shape factor is structural | PASS: sign cancellation of K₁, K₂ (C_308 note) |
| G2 | PASS: proofs in §2–§4 | PASS for order 1; order 2 is THEORY_ONLY |
| G3 | PASS: (R1), (R2), declared ψ class | PASS: single drift; uniformity over a block is not implemented |
| G4 | PASS | PASS |
| G5 | PASS on FSM: favourable and adversarial classes included | PASS on discrete LR families |
| G6 | PASS for the mathematics (independent review R1 re-derived RSO-0, RSO-PM and RSO-P); two independent certificate checks | PASS for the order-1 reduction (re-derived by review R1) |
| G7 | PASS | PASS |
| G8 | PASS | PASS |
| G9 | PASS: the certificate format is freezable | PASS |
| G10 | PASS **iff ψ ≠ ‖ψ‖ μ-a.e.** (N14); with constant ψ it is F1 (collapse lemma) | PASS (below PM and norm on every case) |

**Verdict.**
* RSO-C4 as originally defined is **valid but structurally narrow**: order-0 term only.
* RSO-P (with SC) is the form with reach.
* States as in the header. FREEZE_READY: **no** (payloads, U1–U3).
