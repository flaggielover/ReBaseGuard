# Campaign C2, Phase D1 — what actually blocks the tail

Diagnosis only. Machine-readable: `evidence/phase_d1/C2_D1_BLOCKER.json` (sha256 `e929e857…`), produced from
committed evidence with stdlib Python alone, after the C2 gate was frozen at `87309610`.

## 1. The decomposition

The theorem-TC-T radius expands into twelve terms. Grouped by what a successor could attack, averaged over r with
the assembly weight 1/5, as a share of the total radius:

| cell | required uniform A-reduction | gap above 1 | **order-3 residual f_G** | **(P3) envelope Env4** | order-2 f_H | order-1 f_D | order-0 f_F |
|---|---|---|---|---|---|---|---|
| 305 | 1.000 (closes) | 0.000 | **0.801** | 0.188 | 0.0017 | ~0 | ~0 |
| 306 | 1.000 (closes) | 0.000 | **0.785** | 0.204 | 0.0018 | ~0 | ~0 |
| 307 | 1.262057 | 0.262 | **0.764** | 0.226 | 0.0018 | ~0 | ~0 |
| 308 | 1.663451 | 0.663 | **0.747** | 0.245 | 0.0016 | ~0 | ~0 |
| 309 | 2.101597 | 1.102 | **0.731** | 0.262 | 0.0013 | ~0 | ~0 |

    DOMINANT_BLOCKER_1 = order-3 residual f_G        73-80 % of the radius, on every cell
    DOMINANT_BLOCKER_2 = (P3) envelope Env4          19-26 %
    DOMINANT_BLOCKER_3 = order-2 residual f_H        0.13-0.18 %, i.e. nothing

Inside f_G (≈ 6.5–7.6): the candidate-supremum part 3k₁s_H + 3k₂s_D + k₃s_F is 3.91–4.82, σ₃ is 2.63–2.81, and the
adopted Aux3 source error `eps_src[3]` is 0.0027–0.0034. Inside Env4 (≈ 95): **σ₄ is 85.2–86.0**, the candidate part
only 9.0–11.1. Both σ's come from the frozen J/h Leibniz tower, for which no adopted order-4 evidence exists.

## 2. Sensitivity — which certified input is worth attacking

Relative gain in the whole-cell magnitude from a **10 % improvement in one input**, holding everything else fixed:

| cell | D_lo | D2 | D1 | C_T | τ | A0 | A1 | A2 | all three A |
|---|---|---|---|---|---|---|---|---|---|
| 305 | **+8.60 %** | +0.07 % | +0.57 % | +1.36 % | **+8.02 %** | +6.15 % | +1.63 % | +0.23 % | +8.02 % |
| 307 | **+8.67 %** | +0.07 % | +0.56 % | +1.38 % | **+8.10 %** | +6.23 % | +1.64 % | +0.23 % | +8.10 % |
| 309 | **+8.72 %** | +0.07 % | +0.54 % | +1.39 % | **+8.17 %** | +6.30 % | +1.65 % | +0.22 % | +8.17 % |

Three findings, and one of them corrects the plan C1 handed forward:

1. **D_lo and τ are the only operator levers that matter.** They act through A0 = Ā_eff = τ/D_lo, which carries
   6.2–6.3 % of the 8.1 % that a uniform 10 % A-improvement buys.
2. **D2 is irrelevant.** A 10 % improvement in D2 moves the magnitude by **0.07 %**, because A2 itself contributes
   only 0.22–0.23 %. C1's finding that Lemma Dv′ *worsens* A2 by 1.25–1.36× is real, and it is also **immaterial** —
   C1's own continuation plan item "attack D_lo **and D2**" is half right, and C2 records the correction rather than
   inheriting it.
3. **No plausible operator tightening closes cell 309.** The magnitude responds to the atom constants with elasticity
   ≈ 0.82, and cell 309 needs a 2.102× uniform reduction, i.e. A must fall to 47.6 % of its certified value. Since
   A0 = τ/D_lo with τ ≥ 1 and D_lo ≤ 1, A0 ≥ τ, so reaching A0 = 2.48 requires τ ≤ 2.48 against a certified 4.42 —
   and τ bounds a genuine expected hitting time at drift e ≈ 2.04, which is not a slack quantity.

## 3. The R-stage attribution test, as the gate pre-registers it

Recompute each cell's magnitude with the order-3 residual f_G reduced to its `eps_src[3]` floor — a perfect order-3
candidate — and everything else unchanged:

| cell | magnitude now | with a perfect order-3 candidate | Γ | closes |
|---|---|---|---|---|
| 305 | 3.9476 | **1.1593** | −0.257390 | yes |
| 306 | 3.8313 | **1.1661** | −0.212293 | yes |
| 307 | 3.7747 | **1.2044** | −0.165287 | yes |
| 308 | 3.7851 | **1.2538** | −0.118666 | yes |
| 309 | 3.7234 | **1.2798** | −0.078229 | yes |

**The residual blocker is ORDER-3-ATTRIBUTABLE on all five cells**, which satisfies the gate's R-stage eligibility
condition (b). Condition (a) — that the D stage does not close all five — is decided in D5, not here.

This is a counterfactual with a *perfect* candidate and is the gate's attribution test, nothing more. A real order-3
candidate pays its own certified supremum and its value at the atom, which is exactly what invalidated Campaign B's
route T2; any R-stage forecast must model that and not this.

## 4. What D2 and D3 are therefore for

The pre-registered deterministic designs attack τ and D_lo, which §2 identifies as the only operator levers with
weight: a finer partition tightens the per-block sup that sets τ and C_T, and per-sub-block denominator
certification tightens D_lo on a narrower interval. They cannot reach cell 309 (§2.3), and C2 does not claim they
will. Their job is to close what is reachable and to tighten the rest by the margin the gate demands.
