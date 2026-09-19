# Prior art and method classification (§20)

Purpose: avoid re-deriving a known theorem incorrectly. No novelty is claimed.

| ingredient of theorem AD | standard source | status here |
|---|---|---|
| Rank-one atom split K = K̂ + k_a ⊗ δ_a and (I − K)⁻¹ = Ĝ + h ⊗ ν / D | first-entrance / last-exit (regenerative) decomposition with taboo probabilities (Chung); its resolvent form ("resolvent decomposition theorem"); Nummelin splitting, which *creates* an atom for general Harris chains. The CUSUM kernel has a genuine atom at (0,0), so no splitting is needed | STANDARD_TOOL (used as an algebraic Sherman–Morrison identity on B(X)) |
| Quasi-stationary / Perron mode = renewal root δ_a(z − K̂)⁻¹k_a = 1 | renewal theory for killed chains; Darroch–Seneta quasi-stationary distributions | STANDARD_TOOL (audit only; not load-bearing) |
| ‖(I − K)⁻¹‖∞ = sup_x E_x[τ] for positive K, certified by a supersolution w ≥ 1 + K w | Foster–Lyapunov drift / comparison principle for positive operators | STANDARD_TOOL (the adopted R3 C_e0, C_o0 certificates already use it) |
| CUSUM ARL as a Markov / integral-equation problem with regeneration at 0 | Page (1954); Brook & Evans (1972, Biometrika 59:539–549); two-sided extensions (Woodall 1984, Technometrics 26) | STANDARD_TOOL (the two-sided state (0,0) is the classical renewal state) |
| e-derivatives of a resolvent, ∂R = RK'R, quotient rule on ν/D | elementary analytic perturbation (Kato) | STANDARD_TOOL |
| Group inverse / fundamental matrix, reduced resolvent (Kemeny–Snell; Meyer) | not used: the atom route needs no spectral projection | — |
| Verified enclosure of a simple eigenpair (Krawczyk / Rump verifynlss, verifyeig) | not used: the finite-dimensional tools do not certify this infinite-dimensional operator without a discretisation-defect theory | — |
| Point-error propagation through the frozen K1 DAG with one channel division; e-uniform supersolutions by an affine expansion checked at both block ends; tightening recorded Arb enclosures by Δ | project-specific combination of the above with the frozen ERROR_ALGEBRA | STANDARD_TOOL_WITH_PROJECT_SPECIFIC_ADAPTATION |

**METHOD_CLASSIFICATION = STANDARD_TOOL_WITH_PROJECT_SPECIFIC_ADAPTATION.**

References located during the campaign (for orientation, not as evidence):
- Resolvent decomposition theorems (first-entrance/last-exit, taboo resolvent): https://link.springer.com/article/10.1007/s10959-019-00941-w
- Brook & Evans (1972): https://academic.oup.com/biomet/article/59/3/539/484836
- Two-sided CUSUM Markov-chain approach (Technometrics 26:1): https://www.tandfonline.com/doi/abs/10.1080/00401706.1984.10487920
- Rump, verified eigenpair bounds (not used): https://www.tuhh.de/ti3/paper/rump/Ru99c.pdf
