# P5Y K1 SR O9 — endpoint-strip successor (micropilot)

**Status: `ENDPOINT_STRIP_SUCCESSOR_MICROPILOT_PASS__INT_LINE_OPEN`.** Not a T2 closure.

The predecessor (`p5y-k1-sr-o9-t2-endpoint-not-closing`) bounds the two x-dependent
endpoint strips analytically (`H * candidate_sup * sup phi`), which fails the frozen
gate `C * delta_end <= 1/250` by up to 4e5x. Here the true operator is split
`M(a,b) = core[L_c,U_c] - I_L(b) - I_U(a)` and each strip is **contracted**: expanded with
the frozen PanelShared Taylor models about the strip centre, weighted by a certified
phi series times `(z_c+zeta)^s`, and integrated exactly in `zeta`. Only certified strip
errors (raised-degree truncation, Taylor-model error, weight remainder) enter `end`.
Strip IDs: `SRstrip:v3:task1r-span-p1+strip-contract-v3:64:{i}:{j}:{L|U}`.

Unchanged: theorem target, the 1/250 gate, `B_cover`, D=11, Z=20, 256 bits, degree 16,
46 candidates / 102 contracts, the core span panelisation, and the historical sliver
method (predecessor evidence).

Results (`config/ENDPOINT_STRIP_MANIFEST.json`): the endpoint gate passes in every run
(worst `C*delta_end/(1/250)` = 2.5e-7); strip polynomials match an independent
quadrature; the (17,11) and Task1R controls improve. **Open:** the frozen interval line
`B_int` still fails on 3 low-drift boundary pilot cases — present identically in the
predecessor and attributed (diagnostic) to the frozen softplus Lagrange interval
coefficient, not to the endpoint method.

Also superseded here (predecessor not edited): the T2 engine's `arb ** int` in the
raw-shift drift (NaN on zero-centred panels, radius-inflated elsewhere) is replaced by
exact repeated multiplication for both paths.

No T2, whole-cell, refinement, `B_cover` or obligation closure is claimed.
