# Campaign C2, Phase D1 — what actually blocks the tail

Diagnosis only. Machine-readable: `evidence/phase_d1/C2_D1_BLOCKER.json` (sha256 `62531bf5…`), produced from
committed evidence with stdlib Python alone, after the C2 gate was frozen at `87309610`.

## 1. The decomposition

The theorem-TC-T radius expands into twelve terms. Grouped by what a successor could attack, averaged over r with
the assembly weight 1/5, as a share of the total radius:

| cell | required uniform A-reduction | gap above 1 | **order-3 residual f_G** | **(P3) envelope Env4** | order-0 f_F | order-1 f_D | order-2 f_H |
|---|---|---|---|---|---|---|---|
| 305 | 1.000 (closes) | 0.000 | **80.11 %** | 18.80 % | 0.602 % | 0.320 % | 0.170 % |
| 306 | 1.000 (closes) | 0.000 | **78.49 %** | 20.44 % | 0.545 % | 0.340 % | 0.179 % |
| 307 | 1.262057 | 0.262 | **76.44 %** | 22.57 % | 0.475 % | 0.342 % | 0.177 % |
| 308 | 1.663451 | 0.663 | **74.67 %** | 24.47 % | 0.378 % | 0.322 % | 0.161 % |
| 309 | 2.101597 | 1.102 | **73.08 %** | 26.22 % | 0.285 % | 0.282 % | 0.135 % |

    DOMINANT_BLOCKER_1 = order-3 residual f_G        73-80 % of the radius, on every cell
    DOMINANT_BLOCKER_2 = (P3) envelope Env4          19-26 %
    DOMINANT_BLOCKER_3 = order-0 residual f_F        0.28-0.60 %, i.e. nothing

**Corrected after the pre-freeze review (note 30).** The three columns above previously read `order-2 f_H | order-1
f_D | order-0 f_F`, printed "~0" for f_D and f_F, and named **f_H** as `DOMINANT_BLOCKER_3`. That inverted the
ranking of the three negligible terms and contradicted this document's own machine-readable evidence, which has
always said `"DOMINANT_BLOCKER_3": {"term": "order0_residual_fF"}`. The true order is f_F > f_D > f_H on every
cell. No conclusion moves — all three are under 1 % and "everything but f_G and Env4 is negligible" is what the
diagnosis rests on — but a document that disagrees with its own evidence file should not be frozen, so it is fixed
here rather than explained away. The JSON was right; the prose was wrong.

Inside f_G (≈ 6.5–7.6): the candidate-supremum part 3k₁s_H + 3k₂s_D + k₃s_F is 3.91–4.82, σ₃ is 2.63–2.81, and the
adopted Aux3 source error `eps_src[3]` is 0.0027–0.0034. Inside Env4 (≈ 95): **σ₄ is 85.2–86.0**, the candidate part
only 9.0–11.1. Both σ's come from the frozen J/h Leibniz tower, for which no adopted order-4 evidence exists.

## 2. Sensitivity — which certified input is worth attacking

Relative gain in the whole-cell magnitude from a **10 % improvement in one input**, holding everything else fixed.

**The convention, which the first version of this table left unstated (pre-freeze review note 32).** "A 10 %
improvement" means *scale by 1.1 in the improving direction*: τ, C_T, D1, D2 and each A_j are **divided** by 1.1;
D_lo is **multiplied** by 1.1. That is the convention under which A0 = τ/D_lo responds symmetrically to its two
factors, which is why it was chosen. Under the other natural reading — upper bounds × 0.9, lower bound ÷ 0.9 —
every gain is about 10 % larger: at cell 305, D_lo +9.457 % and τ +8.820 % against the +8.603 % and +8.018 %
tabulated here. **The ordering does not change:** D_lo outranks τ under both conventions, on every cell.

The review suggested the ordering reverses, quoting τ +8.82 % against D_lo +8.60 %. Those two figures come from
*different* conventions — τ scaled by 0.9 against D_lo scaled by 1/1.1 — so they are not comparable. Within either
convention consistently applied, D_lo > τ. Recomputed here rather than accepted, because it is the finding the
whole section rests on.

An earlier version of this paragraph claimed a further reason to prefer the tabulated convention: that × 0.9
drives C_T below τ at cell 307 and so leaves the Lemma Dv′ hypotheses. **That was wrong, and the pre-freeze review
was right to call it (note 65).** ÷ 1.1 does exactly the same thing, on exactly the same three cells — see the ◆
note above. Neither convention is "uniformly applicable" in that sense, so this is not a reason to prefer either
one. The reason to prefer ÷ 1.1 is symmetry in A0 = τ/D_lo, and that reason alone.

| cell | D_lo | D2 | D1 | C_T | τ | A0 | A1 | A2 | all three A |
|---|---|---|---|---|---|---|---|---|---|
| 305 | **+8.60 %** | +0.07 % | +0.57 % | +1.36 % | **+8.02 %** | +6.15 % | +1.63 % | +0.23 % | +8.02 % |
| 307 | **+8.67 %** | +0.07 % | +0.56 % | +1.37 %◆ | **+8.10 %** | +6.23 % | +1.64 % | +0.23 % | +8.10 % |
| 309 | **+8.72 %** | +0.07 % | +0.54 % | **+0.93 %**◆ | **+8.17 %** | +6.30 % | +1.65 % | +0.22 % | +8.17 % |

◆ **A 10 % improvement in C_T alone is not available at these cells, and the first published version of this table
did not say so (pre-freeze review r2, notes 65/66).** Lemma Dv′ requires C ≥ τ. On cells 307, 308 and 309, C_T/1.1
falls *below* τ — 4.846842 < 4.851873, 4.553601 < 4.633777, 4.277739 < 4.418493 — so the perturbation leaves the
lemma's hypotheses. The pinned consumer `deflated_consume.atom_constants` refuses such a tuple; the local copy in
`c2_d1_blocker.py` had no such guard and returned a number anyway. The guard is now present, and the C_T column
reports the **admissible best, C_T = τ**, exactly as the D_lo column has always been capped at 1 because D is a
probability. The corrected figures are +1.3681 % (307), +1.1502 % (308), +0.9335 % (309), against the
inadmissible +1.3823 / +1.3945 / +1.3887 % published before — an overstatement of 0.01 / 0.24 / 0.46 percentage
points. Cells 305 and 306 are unaffected; C_T/1.1 stays above τ there. Nothing else in the table, and no Γ,
magnitude or blocker share anywhere in this campaign, changes. **The correction strengthens the section's
conclusion**: C_T's real lever at cell 309 is 0.93 %, not 1.39 %, against D_lo's 8.72 %.

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
