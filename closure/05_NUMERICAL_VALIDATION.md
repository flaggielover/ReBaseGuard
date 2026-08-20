# 05 — Numerical Validation Inventory

Every Level 1–3 computational result that is **not** rigorous proof. All of it
carries the label `NUMERICAL EVIDENCE`. Nothing here supports a `PROVED` or
`CERTIFIED` claim, and nothing here is required for the closure decision — it is
corroboration.

Where a field is genuinely absent from the artifacts, it is written
`NOT FOUND` rather than reconstructed or guessed.

---

## 1. Monte Carlo — the reference diagnostic

**Source script:** `rebaseguard-proof/scripts/run_diagnostics.py`
→ `src/rebaseguard_certify/diagnostics.py::simulate` (lockstep simulation, so
results are batch-size invariant)
**Output artifact:** `rebaseguard-proof/diagnostics/reference.json`
**Self-label in the artifact:** `"proof_role": "NON-RIGOROUS DIAGNOSTIC ONLY"`

| Field | Run 1 | Run 2 |
|---|---|---|
| Method | Direct path simulation of the frozen detector | same |
| Model | `k=0.5`, `h=5`, `Z_t ~ N(0,1)`, `S₀=(0,0)`, alarm `≥ h` | same |
| Parameters | `m=1`, single cycle | same |
| Sample size | `200 000` paths | `200 000` paths |
| Seed | `1729` | `20260818` |
| **`Γ` estimate** | **15.961901323226364** | **15.900990186311688** |
| Uncertainty (SE) | `0.08978145556625645` | `0.09024426859968229` |
| `E[Z_τ²]` | 4.051321303599967 | 4.050728751813283 |
| Cross term `E[Z_τT_{τ−1}]` | 11.910580019626394 | 11.850261434498407 |
| `E[τ]` (ARL₀) | 465.60712 | 462.539075 |
| `E[T_τ²]` | 463.8578273336159 | 463.2465185555655 |
| `E[Z_τ]` | −0.007454651595004509 | 0.004600951427371437 |
| `E[T_τ]` | 0.017791494647526086 | −0.008072713802986282 |
| `up_fraction` | 0.498475 | 0.501055 |
| Evidence label | NUMERICAL EVIDENCE | NUMERICAL EVIDENCE |
| Relation to the rigorous result | Both estimates lie **strictly inside** the certified interval `[3.9243, 27.8494]`, roughly `12` SE above the certified lower endpoint. Corroborates, does not prove. | same |

**Reproduction (this session, 2026-08-20).** `.venv/bin/python scripts/run_diagnostics.py`,
exit 0, ≈5 s. **Every stored numeric field reproduced bit-for-bit.** The current
code additionally emits five newer summary fields absent from the stored file
(`arl`, `down_fraction`, `gamma_se`, `alarm_symmetry_gap`, `wald_second_gap`) —
the stored artifact predates them. The historical artifact was restored
byte-for-byte after the check, so nothing in the repository was altered.

The SE values above are from the re-run; they are `NOT FOUND` in the stored
`reference.json`.

## 2. Consistency checks derived from the same runs

| Check | Theoretical statement | Run 1 | Run 2 | Verdict |
|---|---|---|---|---|
| Wald second identity `E[T_τ²] = E[τ]` (`C-M2`, PROVED) | equality | 463.86 vs 465.61 (gap −1.749) | 463.25 vs 462.54 (gap +0.707) | Consistent (gaps ≪ MC noise on `E[τ]`) |
| Reflection symmetry `E[Z_τ]=E[T_τ]=0` (`C-DEC`, PROVED) | both zero | −0.0075, +0.0178 | +0.0046, −0.0081 | Consistent |
| Alarm-direction balance | `up = 0.5` | 0.498475 (gap −0.00305) | 0.501055 (gap +0.00211) | Consistent |
| Decomposition `Γ = E[Z_τ²] + E[Z_τT_{τ−1}]` (`C-DEC`) | exact | 4.0513 + 11.9106 = 15.9619 ✓ | 4.0507 + 11.8503 = 15.9010 ✓ | Exact to displayed precision |

## 3. Independent implementations

| # | Implementation | Method | Result | Evidence | Relation to rigorous result |
|---|---|---|---|---|---|
| 1 | `src/rebaseguard_certify/bellman.py` → `proofs/bellman_crosscheck.json` | Finite cellwise **Arb** Bellman solve, 12 cells, 96 `z`-bins, 169 mass-balance rows, 192-bit balls | `18.7401484450398286287…` | NUMERICAL EVIDENCE (`"proof_role": "INDEPENDENT FINITE INTERVAL CROSS-CHECK ONLY"`, `"continuum_certificate": false`) | Shares neither the spectral candidate nor the symbolic residual path. The auditor **enforces** that it lies strictly inside the certified interval (`audit.py:96`). |
| 2 | `src/rebaseguard_certify/refined_bellman.py` (Phase-4 pre-gate) | Reachable-geometry solver with second-order extrapolation | `Γ ≈ 15.8868236` (point estimate) | NUMERICAL EVIDENCE | Agrees with `b̂(0,0) = 15.8868651640648…` to ~5×10⁻⁵ relative — strong corroboration of the candidate |
| 3 | `Mathematical_proof/blind_rederivation_report.md` | Independent blind human re-derivation of the operator core | Structural agreement | PROVED (derivation), not numerics | Confirms the equations the numerics implement |
| 4 | Phase-4D independent simulator (raw `R`-recursion, `n=3×10⁵`) | Monte Carlo | Level-4 SR quantities; also `ARL₀(CUSUM) ≈ 465.8` | NUMERICAL EVIDENCE | Independent ARL corroboration only |

## 4. Convergence / discretization sensitivity

| Study | What was varied | Finding | Artifact | Evidence |
|---|---|---|---|---|
| Finite-Bellman resolution | Cell count of the finite chain | The 12-cell chain's transition rule sends every off-grid next state to the componentwise **lower** grid point, biasing the state away from the alarm boundary; at that resolution the chain's ARL is `2099.53` instead of `≈465`, which fully explains the `18.7401` vs `15.87` gap. Refining converges toward `15.87`. | `proofs/ReBaseGuard_Phase4_Feasibility_PreGate_Report.md` §2; `diagnostics/phase4_pregate.json` | NUMERICAL EVIDENCE |
| Threshold sweep | `h ∈ {0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0}` at `k=0.5` | Monotone growth of `Γ`; at `h=5`: `Γ=15.8851`, `F₁'(0)=−14.8851`, `ρ_c=0.06718`, `ARL₀=465.4`. Internally consistent: `ρ_c = 1/(Γ−1)` holds to the tabulated precision at every row. | `Mathematical_proof/gamma_table.csv` | NUMERICAL EVIDENCE |
| Continuum-certificate mesh sensitivity | — | **NOT FOUND** as a stored artifact. This is by design: the certificate has no state grid (`"sampled_grid_used": false`), so there is no mesh to vary. The only discretization parameters (`phi_taylor_order`, `subdivision_depth`) enter through rigorous remainder bounds, not through a convergence argument. | — | — |
| Monte Carlo sample-size convergence study | — | **NOT FOUND**. Only two fixed-`n = 200 000` runs exist. | — | — |

## 5. Alternative numerical approaches

| Approach | Used for | Proof role |
|---|---|---|
| Degree-12 tensor Chebyshev collocation (`candidate.py`, `spectral_candidate.py`) | Constructing `â, b̂` | **Candidate only.** Leaves the proof path at dyadic rounding. NumPy/SciPy are explicitly outside the trusted base. |
| Symbolic integration + tensor Bernstein enclosure (`residual.py`, `polynomial.py`) | Certified residual | Inside the trusted base (this is the proof) |
| Monotone one-sided Bellman minorant (`contraction.py`) | Certified contraction | Inside the trusted base |
| Finite cellwise Arb Bellman (`bellman.py`) | Cross-check | Outside |
| Lockstep Monte Carlo (`diagnostics.py`) | Cross-check | Outside |
| Pathwise oracle replay (`pathwise.py`) | Convention verification | Outside |

## 6. Hostile audits and regression checks

| Item | Scope | Verdict | Artifact |
|---|---|---|---|
| Blind re-derivation | Full mathematical core, derived without reading the official algebra first | PASS | `Mathematical_proof/blind_rederivation_report.md` |
| Step-2 hostile mathematical audit | Official vs blind derivation, adversarial | **PASS with two nonfatal corrections** (both in auxiliary one-sided commentary of the blind report; neither touches the symmetric CUSUM theorem) | `Mathematical_proof/ReBaseGuard_Step2_Hostile_Mathematical_Audit.md` |
| Step-3 proof-to-code correspondence | 15-item hostile mismatch checklist (wrong recursion, pre/post-update alarm, strict vs inclusive threshold, terminal increment omitted, `Z_τT_{τ−1}` substitution, wrong continuation endpoints, wrong reflected sign, missing `K_z a`, missing `z²` absorption, candidate treated as proof, sampled-grid residual, wrong target, `Γ` taken from the cross-check, hash inconsistency, auditor trusting the stored interval) | **PASS — all 15 NOT FOUND**; declares `LEVEL-3 MATHEMATICAL BASELINE: FROZEN` | `Mathematical_proof/ReBaseGuard_Step3_Proof_to_Code_Correspondence_Audit.md` |
| Phase-4D adversarial audit | Level-4 SR route; explicitly does not touch the Level-3 certificate | Architecture sound, not executed | `rebaseguard_phase4d_audit.md` |
| Regression suite | 90 tests: Arb backend, mesh, model conventions, symmetry invariants, mass balance, certificate assembly, auditor, enclosure, residual, plus Level-4 groups | **PASS**, exit 0, 3.87 s (re-run this session) | `rebaseguard-proof/tests/` |

Test-group breakdown (collected this session): 90 total = 44 core + 20 `tests/phase4b` + 26 `tests/phase4c`.

## 7. Level-1 phenomenon evidence (multi-cycle — context only)

Recorded here for completeness because it is what motivated the Level 2–3 work.
**It is not part of the Level 1–3 closed claims** (see
`08_LIMITATIONS_AND_BOUNDARIES.md`): the multi-cycle recursion is Level-4 territory.

| Signature | Reuse | Fresh control | Source |
|---|---|---|---|
| Local slope `F'(0)` | `−4.51` (`m=5`), `−2.98` (`m=10`), `−0.71` (`m=50`) | — | `rebaseguard_phase15.md` |
| Alarm-direction alternation rate | 0.94 | 0.50 | `rebaseguard_phase15.md` |
| Reference-error ACF, lags 1–3 | `−0.56, +0.57, −0.47` | ≈ 0 at every lag | `rebaseguard_phase15.md` |
| In-control run length | 48% of matched-window fresh | baseline | `rebaseguard_phase15.md` |
| Invariant density | bimodal (0.38 at 0, ≈0.70 at the lobes) | unimodal | `rebaseguard_phase15.md` |

Sample sizes, seeds and uncertainties for these Phase-1.5 runs: **NOT FOUND** —
the memo reports point estimates without a machine-readable artifact. They are
therefore the weakest evidence in the project and are labelled accordingly.

## 8. Summary

* Every Monte Carlo estimate of `Γ` (≈ 15.90–15.96) sits comfortably inside the
  certified interval `[3.9243, 27.8494]`, ≈ 12 standard errors above the lower
  endpoint.
* Two structurally independent deterministic computations (finite Arb Bellman
  `18.7401`, refined reachable-geometry extrapolation `15.8868236`) also sit
  inside it, and the second matches the certificate's own candidate `b̂(0,0)` to
  ~5×10⁻⁵ relative.
* All proved consistency identities (`Wald`, reflection symmetry, the exact
  decomposition) check out numerically.
* No numerical result contradicts any rigorous result anywhere in the project.
* No numerical result is used to support a `PROVED` or `CERTIFIED` claim.
