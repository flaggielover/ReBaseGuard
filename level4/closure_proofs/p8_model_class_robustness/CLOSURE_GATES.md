# P8 closure gates — preregistered, literal

**No historical P8 gate exists.** The searches in `P8_DEFINITION_AUDIT.md` §1
find no P8 protocol, gate file, config or status entry anywhere in the
repository at the anchor commit. Every gate below is therefore `P8_ORIGINAL`.
Nothing historical was overwritten, weakened or reworded.

Frozen with `EXPERIMENT_PROTOCOL.md`, before any production cell was generated.
**These thresholds are not to be changed after results are seen.** If a gate
fails it stays failed and is reported as failed.

---

| gate | statement | threshold | verdict rule |
|---|---|---|---|
| **G1a** | P8 reproduces P3's `CLOSED` Gaussian `GammaTilde` for CUSUM and SR at `m in {1,2,3,5}` | combined-SE `\|z\| <= 3` in `>= 7` of 8 cells | PASS/FAIL |
| **G1b** | P8 reproduces P4's `m=1` CUSUM `Gamma_f` for the six families | combined-SE `\|z\| <= 3` in `>= 5` of 6 families | PASS/FAIL |
| **G1c** | measured `ARL_0` at the frozen Stage-D CUSUM thresholds matches the frozen target `465.50394` | relative error `<= 1%` in all 6 families | PASS/FAIL |
| **G1d** | exact regularity identities hold for all six families: `E[eps psi(eps)] = 1`, `E[psi(eps)] = 0`, and the Fisher information matches Stage-D's `E_psi_prime` | `\|E[eps psi] - 1\| <= 1e-4`, `\|E[psi]\| <= 1e-8`, `\|I - E_psi_prime\| <= 1e-6`, all 6 | PASS/FAIL |
| **G1e** | P8's independent family implementation agrees with P4's `route_a.py` `location_score` and `draw_innovations` | max abs score difference `<= 1e-12` on a fixed grid, all 6 | PASS/FAIL |
| **G2** | every P8-calibrated SR threshold `A_f` achieves the frozen target at the verification sample | relative `ARL_0` error `<= 0.5%` in all 5 non-Gaussian families | PASS/FAIL |
| **G3** | **regime survival.** In every `(D, f, m)` cell with `m in {1,2,3,5}` and `f` not `MOMENT_MARGINAL`, the lower 95% bound of `Gamma_A` exceeds `2`, i.e. `rho_c < 1` and full reuse is locally repelling | all 40 eligible cells | PASS/FAIL. The 8 `t3` cells are reported in full and **never counted** either way |
| **G4** | **PRIMARY. Window-separability law `H1`.** Relative spread of `K(D,f,m) = rho_c(D,f,m)/rho_c(D,f,1)` across the 10 eligible `(D,f)` cells | `max/min - 1 <= 0.10` for **every** `m in {2,3,5}` | PASS/FAIL |
| **G4-D** | sub-gate: detector invariance of `K` | `\|K(cusum,f,m)/K(sr,f,m) - 1\| <= 0.03` for all 5 eligible `f` and all `m in {2,3,5}` | PASS/FAIL |
| **G4-F** | sub-gate: distribution invariance of `K` | for each detector, spread of `K` across the 5 eligible families `<= 0.10`, all `m in {2,3,5}` | PASS/FAIL |
| **G4-X** | extrapolation report: the same three quantities at `m in {10,20}` | **reported, not gated** (`EXTRAPOLATION_BEYOND_P3`) | REPORT |
| **G5** | **decomposition identity.** `Gamma_A(m) - (1/m) sum_{r<m} gamma_r - R_m = 0` (`P8-L1(b)`) in every cell | `\|residual\| <= 4 x SE(residual)` in all `(D,f,m)` cells | PASS/FAIL |
| **G6** | **convention semantics.** The measured `Gamma_A - Gamma_B` equals the exact truncation remainder `R_m`, and `P(tau < m)` is reported per cell | `\|(Gamma_A - Gamma_B) - R_m\| <= 1e-12` (algebraic identity, exact in the implementation) and `P(tau<m)` present for all cells | PASS/FAIL |
| **G7** | **P7 boundary criterion, applied verbatim per family.** For each innovation family, run P7's test: "the rate across the bracket containing `rho/rho_c = 1` must be the maximum over all brackets, in at least half of the `(detector, m)` sub-families, for at least one pre-specified metric" | reported per family. PASS means "P7's `LOCAL-MATHEMATICAL, NOT OPERATIONAL` verdict **reproduces** in that family" | PASS/FAIL per family; gate PASS iff the verdict reproduces in `>= 5` of 6 families |
| **G8** | **operational degradation survives.** In every `(D, f, m in {1,5})` cell, chain `ARL_0` at `rho = 1` is below `50%` of the same-cell nominal `A_f(0)` | all 24 cells | PASS/FAIL |
| **G9** | **detector transfer, tested not assumed.** Report `Gamma_A(cusum,f,m)/Gamma_A(sr,f,m)` and the chain-metric ratios with intervals. **No threshold**: the gate is that the comparison is reported and that no transfer claim is made beyond what it supports | REPORT + no-overclaim audit | PASS/FAIL |
| **G10** | **seed sensitivity.** `E1` repeated on an independent batch family reproduces every `Gamma_A(D,f,m)` | combined-SE `\|z\| <= 3` in `>= 90%` of the 72 cells, and `>= 95%` of the 60 non-`t3` cells | PASS/FAIL |
| **G11** | **drift-pattern robustness.** Step and ramp delay metrics are reported for all six families at `rho in {0,1}`, `m in {1,5}`, both detectors, with tail metrics (`q50`, `q95`, `P(delay>100)`) and an explicit `INSUFFICIENT_TAIL_EVENTS` label wherever fewer than 200 tail events occur | reported and labelled for all declared cells | PASS/FAIL |
| **G12** | **protected-tree integrity.** No tracked file outside `level4/closure_proofs/p8_model_class_robustness/` differs from the pre-campaign manifest | zero differences | PASS/FAIL |
| **G13** | **CRN primitive identity.** Every P8 primitive value is a pure function of its address: identical under a changed live set, a changed execution order, a changed `rho`, a changed shift, a changed detector where the detector is not in the address, and past any block boundary | all identity tests pass, including at least one address beyond block index 3 | PASS/FAIL |
| **G14** | **no hidden recalibration.** No threshold, no constant and no grid used in any P8 production result was changed after that result existed; the frozen CUSUM thresholds are byte-identical to Stage D's | audit script passes | PASS/FAIL |
| **G15** | **focused test suite.** The P8 test suite passes in full | 0 failures | PASS/FAIL |

---

## Verdict rule (frozen)

* `P8 = CLOSED_CANDIDATE` iff **every** PASS/FAIL gate above passes.
* `P8 = PARTIAL_CANDIDATE` iff `G1a`–`G1e`, `G5`, `G6`, `G12`, `G13`, `G14`,
  `G15` all pass (the correctness, reproduction and integrity spine) but at
  least one scientific gate (`G2`, `G3`, `G4`, `G4-D`, `G4-F`, `G7`, `G8`, `G9`,
  `G10`, `G11`) fails.
* `P8 = FAIL_CANDIDATE` otherwise — in particular if any correctness,
  reproduction or integrity gate fails.

Claude's verdict is a **candidate**. It is not authoritative and must not be
promoted to `CLOSED` without independent adjudication.

## What a failed gate does NOT license

* No gate may be re-thresholded, re-scoped, split, or re-run at a different
  sample size in order to pass.
* A failed `G4` does not license reporting `H1` as "approximately holding". It
  licenses exactly the `NARROWED` or `REJECTED` wording preregistered in
  `EXPERIMENT_PROTOCOL.md` §10.
* A failed `G3` does not license dropping the cell; it licenses applying P3's
  regime audit table to it.
