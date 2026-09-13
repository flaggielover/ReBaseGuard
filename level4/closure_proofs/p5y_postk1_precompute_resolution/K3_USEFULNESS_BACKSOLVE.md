# K3: back-solving the "useful M₂" requirement (pre-compute; no M₂ value inspected)

## 1. Every frozen consumer of `M_2 = sup_e E_e[Rbar²]`

| consumer | frozen text | what it requires of `M_2` |
|---|---|---|
| P5X-T6 upper arm (CERTIFIED_THEOREM, primary target) | "`M_2 = sup_e E_e[Rbar^2] < infinity` … `E_π[e²] ≤ ρ²M_2 + (1−ρ)²/m`" | finiteness (any valid upper bound makes the inequality true) |
| P5X-T9 item 4 ("bounded stationary law") | "unique with all moments finite and `E_π[e²] ≤ ρ²M_2 + (1−ρ)²/m`" | finiteness |
| Gate G4 → `TWO_SIDED` | "`s_min > 0` and `M_2 < infinity` are certified" | finiteness, certified |
| Gate G9 via `EMPIRICAL_PLAN` E3 | measured `E_π[e²]` must lie inside `[ρ²s_min + …, ρ²M_2 + …]` | any valid upper bound contains the truth, so it imposes no tightness |
| Lean spine `X2` (`LEAN_COMPATIBILITY.md`) | consumes `g_max` as a hypothesis | finiteness |
| `THEOREM_CANDIDATES.md` Level B | "`M_2 < infinity` certified … consequently `RMS_π ≥ …`, a **lower** bound"; "The *lower* bound is the local-to-global bridge" | finiteness; the science is carried by the lower arm |
| `FEASIBILITY_AUDIT.md` §7 (design narrative, not a gate) | "Both ends are non-vacuous … Crucially the **lower** end is what carries the science" | none (descriptive) |
| K1 checkpoint §1 | "`K3` (finite / useful `M_2`)" | "useful" is not defined |
| THEOREM_ADJUDICATION (binding) | `K3_FINITE_BUT_TIGHT_BOUND_STILL_REQUIRED`, reasoning from design intent ("named the primary target precisely to deliver a quantitative sandwich") | quantitative, but **no consumer, inequality or threshold is cited** |

No frozen theorem, corollary, gate, Lean declaration or empirical test consumes a quantitative property of `M_2` beyond finiteness. The only quantitative downstream claim in the P5X chain (the "order of magnitude outside `r_lin`" dispersion) uses the **lower** arm (`s_min`), not `M_2`.

## 2. The weakest sufficient inequality

Every frozen P5X/P5Y statement that consumes `M_2` holds as soon as `M_2(D,m) < ∞`. That is discharged exactly: P5-T5 at `p = 1`, plus P5-T4, gives `M_2 ≤ C_D` (`C_CUSUM ≤ 9.8959e8`, `C_SR ≤ 1.4054e11`).

```text
K3_BINDING_USEFULNESS_CRITERION = M_2(D,m) < ∞   for each frozen (D,m)
                                  (already discharged: M_2 ≤ C_D, P5-T5 with P5-T4, EXACT)
K3_CRITERION_DERIVATION         = back-solve over all frozen consumers (table §1): P5X-T6 upper arm,
                                  P5X-T9(4), G4, G9/E3 and Lean X2 each need only a valid finite upper bound;
                                  no frozen consumer uses a quantitative M_2
K3_READY_TO_FREEZE              = YES   (as a governance record for independent adjudication; it supersedes the
                                         TA "tight bound" reading for lack of any consumer; no compute)
```

## 3. Why no numerical threshold is proposed

A threshold such as "`M_2` within a factor `f` of measured" or "`M_2 ≤ c`" has no frozen consumer. Adopting one would **create a new obligation**, which this pass is forbidden to do. The Monte-Carlo comparison in FEASIBILITY_AUDIT §7 ("upper end within a factor 2.2") is design narrative. Using it would anchor a criterion on uncertified data.

## 4. If the adjudicator upholds the binding TA reading anyway

The only theorem-native quantitative form found is the sandwich localisation factor. Its yardstick is taken from P5X's own "order of magnitude" language:

```text
sup_{ρ∈[0,1]} (ρ²M_2 + (1−ρ)²/m) / (ρ²s_min + (1−ρ)²/m) = max(1, M_2/s_min)   (exact: shared (1−ρ)²/m term)
"quantitative sandwich" ⇔ RMS localisation within one order of magnitude ⇔ M_2 ≤ 100 · s_min
```

This alternative **couples K3 to a numerical `s_min`**. With the analytic `κ_D/m²` of Lemma K2-A it is provably unattainable. By P5X-T3 plus P5-T5, `E_e[Rbar²] → 1` as `|e| → ∞` (`Rbar = raw_1` on `{τ = 1}`, and `P_e(τ > 1) → 0` with uniformly bounded fourth moments), so `M_2 ≥ 1`. Meanwhile `100·κ_D/m² ≤ 100·u(11) ≈ 0.79 < 1` for every `m`. It would therefore force certified C2 computation of **both** `s_min` and `M_2`. The recommendation is §2. §4 is recorded only so the adjudicator's choice is explicit and made before any C2 value exists.
