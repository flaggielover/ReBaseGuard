# 06 — Claim Ledger

The authoritative statement of what ReBaseGuard Level 1–3 does and does not
claim, and of the exact wording that is defensible in public.

## Evidence labels — strict definitions

| Label | Meaning | Never confuse with |
|---|---|---|
| **MACHINE-CHECKED** | The mathematical statement is accepted by Lean's kernel **and** its Lean semantics correspond to the intended scientific model. Compilation alone is not sufficient. | CERTIFIED |
| **PROVED** | A complete human mathematical proof exists that is not fully represented in the Lean formalization. Where a claim is also Lean-verified, `MACHINE-CHECKED` takes precedence. | MACHINE-CHECKED |
| **CERTIFIED** | Rigorous computer-assisted numerical result resting on validated outward-rounded interval arithmetic. | MACHINE-CHECKED |
| **NUMERICAL EVIDENCE** | Monte Carlo, simulation, ordinary floating point, cross-checks, convergence studies, non-rigorous independent replication. | PROVED |
| **OPEN** | Unresolved research question. | NOT CLAIMED |
| **NOT CLAIMED** | The project deliberately makes no claim. | OPEN |

**`NUMERICAL EVIDENCE ≠ PROVED`. `CERTIFIED ≠ MACHINE-CHECKED`.**
No evidence is silently promoted anywhere in this package.

---

## The ledger

### L-01 — Analytic derivative identity (the Lean result)

| Field | Value |
|---|---|
| **Claim** | For the frozen two-sided CUSUM (`k=1/2`, `h=5`, alarm `max(S⁺,S⁻) ≥ 5`, `τ ≥ 1`) driven by i.i.d. `N(0,1)` scores: `d/de E[Z_τ·exp(−e·T_τ − (e²/2)·τ)]\|_{e=0} = −E[Z_τ·T_τ]` |
| **Scope** | The frozen single-cycle detector only. `m = 1`. Null model (`e = 0`). |
| **Evidence label** | **MACHINE-CHECKED** |
| **Primary artifact** | `rebaseguard-lean/RebaseguardLean/ReBaseGuardIdentity.lean:392`, `hasDerivAt_rebaseguard_cusum` |
| **Independent support** | Human derivation in `Mathematical_proof/ReBaseGuard_Step2_Hostile_Mathematical_Audit.md` (the "differentiation under expectation" row, PASS after explicit lemma closure); `rebaseguard_lemma_handoff.md` §1 regularity |
| **Assumptions** | `∀n, Measurable (X n)`; `iIndepFun X μ` (which itself forces `μ` to be a probability measure); `μ.map (X j) = gaussianReal 0 1` |
| **Publicly defensible?** | **Yes** |
| **Recommended wording** | *"The analytically delicate differentiation-under-the-expectation identity for the frozen two-sided Gaussian CUSUM model is machine-checked in Lean."* |
| **Forbidden overclaim** | ~~"The entire ReBaseGuard project is formally verified."~~ Also forbidden: "Lean verifies ReBaseGuard", "the ReBaseGuard theorem is formalized", "Γ is computed in Lean". |

### L-02 — `Γ_CUSUM > 2`

| Field | Value |
|---|---|
| **Claim** | `Γ_CUSUM = E₀[Z_τ T_τ] ∈ [3.9243482005828971282…, 27.8493821275467032805…]`, hence `Γ_CUSUM > 2` |
| **Scope** | `k = 0.5`, `h = 5`, Gaussian innovations, `m = 1`. No other parameters. |
| **Evidence label** | **CERTIFIED** |
| **Primary artifact** | `rebaseguard-proof/proofs/certificate.json` (`proof_status: CERTIFIED`), `proofs/audit_report.md` |
| **Independent support** | Full replay reproduced 2026-08-20 (exit 0, 129 s, bit-identical); finite Arb Bellman cross-check `18.7401…` inside the interval; Monte Carlo `≈15.90–15.96` inside the interval; Step-2 and Step-3 audits PASS |
| **Assumptions** | Correctness of FLINT/Arb outward-rounded arithmetic and transcendentals, python-flint bindings, CPython exact integer serialization, and the project's symbolic-polynomial / Bernstein / monotone-contraction / audit code |
| **Publicly defensible?** | **Yes** |
| **Recommended wording** | *"`Γ_CUSUM > 2` is certified by outward-rounded Arb interval arithmetic."* |
| **Forbidden overclaim** | ~~"Lean proves `Γ_CUSUM > 2`."~~ Also forbidden: "`Γ_CUSUM > 2` is formally verified", "machine-checked", "proved by Lean", and any statement that omits the parameter restriction `(k,h,m) = (0.5, 5, 1)`. |

### L-03 — Bellman/Fredholm reduction `Γ = b(0,0)`

| Field | Value |
|---|---|
| **Claim** | `E[Z_τT_τ \| S_t=(p,m), T_t=x] = a(p,m)x + b(p,m)` with `a = Ka+r_a`, `b = Kb+K_z a+r_b`, exact rewards `r_a = φ(u)−φ(ℓ)`, `r_b = uφ(u)+1−Φ(u)+Φ(ℓ)−ℓφ(ℓ)`, and `Γ = b(0,0)` |
| **Scope** | Frozen model; bounded solutions |
| **Evidence label** | **PROVED** |
| **Primary artifact** | `rebaseguard-proof/proofs/derivation.md` |
| **Independent support** | Blind re-derivation (`Mathematical_proof/blind_rederivation_report.md`) and Step-2 hostile audit, both PASS; symmetry identities `a(p,m)=−a(m,p)`, `b(p,m)=b(m,p)` verified by the test suite |
| **Assumptions** | Markov property of the state; regularity from `C-REG`; existence/uniqueness from the Neumann series (contraction constant Arb-certified) |
| **Publicly defensible?** | Yes |
| **Recommended wording** | *"The terminal functional admits an exact affine state reduction whose Fredholm system is derived and independently re-derived; `Γ = b(0,0)`."* |
| **Forbidden overclaim** | "The Fredholm reduction is machine-checked" — it is **not** in the Lean development. |

### L-04 — `F₁'(0) = 1 − Γ` and the `ρ_c` chain

| Field | Value |
|---|---|
| **Claim** | `F₁'(0) = 1 − Γ`; `F_ρ'(0) = ρF₁'(0)`; and if `F₁'(0) < −1` then `ρ_c = 1/\|F₁'(0)\| = 1/(Γ−1) ∈ (0,1)` |
| **Scope** | `m = 1` for the first identity; affine mixed reuse with a mean-zero, `e`-independent fresh component for the second |
| **Evidence label** | **PROVED** (the analytically delicate differentiation step within it is separately MACHINE-CHECKED as `L-01`) |
| **Primary artifact** | `rebaseguard_phase2c.md` §4, Prop. 2, Prop. 3; canonical theorem in `Mathematical_proof/ReBaseGuard_Step2_Hostile_Mathematical_Audit.md` |
| **Independent support** | `L-01`; reflection symmetry giving `F(0) = 0`; numerical corroboration `F₁'(0) ≈ −14.885` at `h=5` (`gamma_table.csv`) |
| **Assumptions** | Regularity (`C-REG`); reflection symmetry of the symmetric two-arm detector |
| **Publicly defensible?** | Yes |
| **Recommended wording** | *"The exact score identity `F₁'(0) = 1 − Γ` is proved, with its regularity conditions stated explicitly and its differentiation step machine-checked in Lean."* |
| **Forbidden overclaim** | Presenting `ρ_c ∈ (0,1)` as unconditional. It is conditional on `Γ > 2`, which is `CERTIFIED`, not proved analytically — so the composite result is at best CERTIFIED, never PROVED. |

### L-05 — Consequences `F₁'(0) < −1` and `ρ_c ∈ [0.0372, 0.3420]`

| Field | Value |
|---|---|
| **Claim** | `F₁'(0) ∈ [−26.8493821…, −2.9243482…] ⊂ (−∞,−1)`, and `ρ_c ∈ [0.03724480493627555…, 0.34195654258978959…] ⊂ (0,1)` |
| **Scope** | `k=0.5`, `h=5`, `m=1` |
| **Evidence label** | **CERTIFIED** (a proved implication applied to a certified input; the weakest link governs) |
| **Primary artifact** | `proofs/ReBaseGuard_Certified_Lemma_Proof_Report.md` §17–18 |
| **Independent support** | `gamma_table.csv` row `h=5.0`: `F₁'(0) = −14.8851`, `ρ_c = 0.06718` — inside both intervals |
| **Assumptions** | `L-02` + `L-04` |
| **Publicly defensible?** | Yes |
| **Recommended wording** | *"Combining the proved score identity with the Arb-certified bound gives a certified, strictly interior critical reuse fraction for the frozen configuration."* |
| **Forbidden overclaim** | "It is proved that the reference fixed point is unstable." The instability is *locally* certified for this one configuration; and it is CERTIFIED, not PROVED. |

### L-06 — Local instability of the mean-transition map

| Field | Value |
|---|---|
| **Claim** | `e = 0` is a locally repelling, orientation-reversing fixed point of the deterministic mean transition map, for the frozen configuration |
| **Scope** | **Local, linearized, deterministic-map only.** `k=0.5`, `h=5`, `m=1` |
| **Evidence label** | **CERTIFIED** |
| **Primary artifact** | Canonical Level-3 theorem, Step-2 hostile audit |
| **Independent support** | Phase-1.5 simulations (NUMERICAL EVIDENCE) |
| **Assumptions** | `L-04` + `L-02` |
| **Publicly defensible?** | Yes, with the local/linearized qualifier |
| **Recommended wording** | *"For the frozen configuration, the centered reference fixed point is locally linearly unstable under full stopping-selected reuse."* |
| **Forbidden overclaim** | ~~"period-2 orbit", "bifurcation theorem", "bimodal invariant law", "ARL degradation theorem"~~ — the canonical theorem states explicitly: *"No period-2, bifurcation, bimodality, invariant-law, or ARL theorem follows from this local result alone."* |

### L-07 — Numerical cross-validation

| Field | Value |
|---|---|
| **Claim** | Monte Carlo gives `Γ ≈ 15.96 / 15.90` (`n = 200 000`, seeds 1729 / 20260818); independent solvers give `18.7401` (finite Arb Bellman) and `≈ 15.8868236` (refined extrapolation); Wald, reflection and decomposition identities check out |
| **Scope** | Frozen model, single cycle |
| **Evidence label** | **NUMERICAL EVIDENCE** |
| **Primary artifact** | `diagnostics/reference.json`, `proofs/bellman_crosscheck.json`, `Mathematical_proof/gamma_table.csv` |
| **Independent support** | Two seeds; three independent implementations; 90-test regression suite; all reproduced this session |
| **Assumptions** | Floating-point arithmetic; finite sample |
| **Publicly defensible?** | Yes, as corroboration only |
| **Recommended wording** | *"Monte Carlo and two independent deterministic solvers agree with, and lie inside, the certified interval."* |
| **Forbidden overclaim** | ~~"`Γ ≈ 15.89` is proved"~~; ~~"simulation confirms `Γ > 2`"~~ (simulation cannot confirm a strict inequality rigorously); using any MC number as an input to a rigorous argument. |

### L-08 — Phase-1.5 phenomenon (multi-cycle)

| Field | Value |
|---|---|
| **Claim** | Under recursive reuse the reference-error chain shows alarm-direction alternation ≈0.94 vs 0.50, oscillatory ACF, bimodal invariant density, and in-control run length ≈48% of matched fresh |
| **Scope** | Multi-cycle simulation at `m ∈ {5,10,50}` — **outside** the frozen single-cycle model |
| **Evidence label** | **NUMERICAL EVIDENCE** |
| **Primary artifact** | `rebaseguard_phase15.md` |
| **Independent support** | None recorded; sample sizes, seeds and uncertainties **NOT FOUND** |
| **Assumptions** | Simulation only |
| **Publicly defensible?** | Only as motivating phenomenology, explicitly labelled |
| **Recommended wording** | *"Simulations of the recursive-reuse chain exhibit an oscillatory, bimodal regime; this is the phenomenon that motivated the analysis and is reported as numerical evidence."* |
| **Forbidden overclaim** | Any theorem-shaped statement about period-2 orbits, bimodality or ARL degradation; any suggestion that Level 1–3 closure covers it. |

### L-09 — Level-4 multi-cycle dynamics

| Field | Value |
|---|---|
| **Claim** | — |
| **Scope** | Multi-cycle recursive reference-state dynamics; second detector (symmetric two-chart Shiryaev–Roberts); `Γ_SR > 2` |
| **Evidence label** | **OPEN** |
| **Primary artifact** | `rebaseguard_phase4d_audit.md`; `rebaseguard-proof/proofs/phase4b/**`, `phase4c/**` |
| **Independent support** | Phase-4D audit verdict: *"Architecture SOUND; not yet executed. Nothing here is a proof of `Γ_SR>2`."* One genuine open risk recorded (ε_a achievability at continuum scale); `sup_y E_y[τ]` needs its own Arb certificate. |
| **Assumptions** | — |
| **Publicly defensible?** | Only as declared future work |
| **Recommended wording** | *"Level-4 multi-cycle dynamics and detector-independence remain open and are not part of this closure."* |
| **Forbidden overclaim** | Any leakage of Level-4 material into a Level 1–3 claim; any statement that the SR route is certified, proved, or complete. |

### L-10 — Global nonlinear theory

| Field | Value |
|---|---|
| **Claim** | — |
| **Scope** | Global bifurcation theorem, rigorous period-2 existence, invariant-law characterization, ARL-degradation mechanism, robustness across arbitrary `m`, `(k,h)`, or noise families, closed form for `Γ` |
| **Evidence label** | **NOT CLAIMED** |
| **Primary artifact** | Step-3 audit §19; Proof Report §19 |
| **Independent support** | — |
| **Publicly defensible?** | n/a — nothing is claimed |
| **Recommended wording** | *"No global nonlinear, bifurcation, invariant-law or ARL theorem is claimed."* |
| **Forbidden overclaim** | All of the above. |

### L-11 — Formal verification scope

| Field | Value |
|---|---|
| **Claim** | Exactly one theorem of the project is machine-checked: the derivative identity `L-01`, together with its supporting chain (`T-01`…`T-18` in `02_THEOREM_MAP.md`) |
| **Scope** | The Lean development, 9 modules, ~115 KB of source |
| **Evidence label** | **MACHINE-CHECKED** (about the scope itself) |
| **Primary artifact** | `closure/03_LEAN_VERIFICATION.md` |
| **Independent support** | Bypass scan clean; axiom audit `[propext, Classical.choice, Quot.sound]` |
| **Publicly defensible?** | Yes |
| **Recommended wording** | *"One analytically delicate step of the ReBaseGuard argument — differentiation under the expectation at the actual stopping time — is machine-checked in Lean against the real two-sided detector, with no `sorry` and no non-standard axiom."* |
| **Forbidden overclaim** | ~~"ReBaseGuard is formally verified."~~ ~~"The proof is in Lean."~~ |

---

## Overclaim audit

Each of the following was checked against every document in `closure/` and each
was found **absent**:

- [x] "the entire ReBaseGuard project is formally verified" — absent
- [x] "Lean proves `Γ_CUSUM > 2`" — absent; the opposite is stated repeatedly
- [x] `CERTIFIED` presented as `MACHINE-CHECKED` — absent
- [x] `NUMERICAL EVIDENCE` presented as `PROVED` — absent
- [x] `Γ > 2` stated without its parameter restriction — absent
- [x] Level-4 material inside a Level 1–3 claim — absent (isolated in `L-09`)
- [x] Unconditional `ρ_c ∈ (0,1)` — absent (conditionality stated in `L-04`, `L-05`)
- [x] Global/bifurcation/ARL theorems — absent (`L-10` = NOT CLAIMED)
- [x] Monte Carlo used as an input to a rigorous step — absent

**No known overclaim remains in this ledger.**
