# C11RD — independence audit

The C11RD D1/D2 certifier must be independent of the original load-bearing implementation (S1–S6
of `docs/D1_D2_STATEMENT_AUDIT.md`) at least as strongly as C11R's accepted certifier. This page
lists what was read, what is used, what differs, and the mechanical checks.

## 1. What the author read, and why

| source | read for | used by the C11RD certifier? |
|---|---|---|
| S1 `taboo_certify.py`, S2 `c2_refined_registry.py`, S3 `opnorms.py`, S4 `cusum_layer1.py`, S5 `cusum_layer2.py` (original chain) | the statement audit only (the instruction requires the meanings to be reconstructed from the original producer chain) | NO: not imported, not executed, no data read |
| S6 `REGISTRY_C2.json` | the audit's structural facts (9 sub-rows, their drift bounds, the artifact hashes); no D1/D2 field was used in any design decision | NO |
| C11R statement table (blob `58b4066f…`) | the frozen semantics and the factor-2 rule; the table declares itself magnitude-free and the loader refuses value fields | YES: cell-306 block, statement semantics, comparison rule |
| C11R sealed runs (blob `a5351603…`) | the ACCEPTED F_H certificate (the premise) | YES: `C_T = tau = 3429/500`, as a DEPENDENCY, not recomputed |
| C11R `c11r_schema.py` (blob `0526426c…`) | the statement wording and route rules | only by validation V19 (equality check) |
| C11R `c11r_equiv.py` | the equivalence semantics | only by validation V20 (in a subprocess, to show the mirror agrees) |
| C11 `c11_certifier.py` | an independent exact FULL-kernel reference | only by validation V03 |
| C7 `c7_gaussian.py` | rigorous rational `phi`, `Phi` enclosures (imports only `fractions`) | YES (point values) |

**Disclosure of the original values.** The two original values of cell 306 (D1 and D2) were
disclosed in C11R Phase 15 and repeated in the C11RD campaign instruction, so the author has seen
them. They appear in no file of this namespace (validation V18 scans every file for all their
renderings with 4–9 significant digits, by hash; the comparator repeats the check at the freeze
commit, U7). No design parameter was chosen with reference to them: every choice is recorded in
`evidence/calibration/C11RD_CALIBRATION.json` with its non-target (NT, LOW) evidence, and the
tolerances are tight (1e-5 to 5e-4 on the residuals), not loosened. The comparison rule is C11R's,
frozen before any C11R result.

## 2. What is different from the original route

| aspect | original (S1 `certify_cell`) | C11RD |
|---|---|---|
| candidates | degree-20 registry polynomials on the reachable cover | band-piecewise degree-8 Chebyshev fits per band (4 strips + 2 axis segments), exact dyadic power-basis, e-Taylor cubic about each sub-block centre |
| drift handling | point candidates at the sub-block midpoint plus an envelope term `rho * env` | the drift is a Taylor-model variable: every residual enclosure is uniform in `e` over the sub-block |
| enclosure arithmetic | `flint.arb` balls, `numpy`, `intervals`, range bounding over the reachable set by `fast_range` / `ra_certifier` / `resolvent_certificate` (S1 lines 40–53) | new Taylor models: Python integers at 2^-160, order 6 in `(u_s, u_theta, u_e)`; standard library only |
| kernel integrals | `rebaseguard_certify.residual._kernel_piece` / `_kernel_polynomials` (S1 line 52) | exact Taylor shifts + centred Gaussian moment series with a proved Lagrange remainder (Lemma 6), C7 point values |
| kink handling | the original's reachable-cover partition | a re-derived piece structure (Lemma 1) on band-aligned boxes; boxes never straddle a band line |
| premise | per-sub-block C_T and tau from the original's degree-20 supersolutions | C11R's independently certified whole-block F_H (`C_T = tau = 3429/500`) |
| sub-blocks | 9 | 4 |
| propagation | same inequalities (they are the mathematics of Theorem 5, re-proved in theory/D1_D2_DERIVATION.md) | Theorem 5 with kappa from C7 |

## 3. Mechanical checks (validation)

* V16: no C11RD module and no module they load (C7 included) imports any of `taboo_certify,
  resolvent_certificate, opnorms, ra_certifier, fast_range, intervals, rebaseguard_certify,
  rung3_engine, spec, cusum_layer1, cusum_layer2, ancestry5, numpy, flint, mpmath, scipy, sympy,
  gmpy2`; a fresh isolated interpreter that imports every certifier module has none of them in
  `sys.modules`; no certifier module names `REGISTRY_C2`, a quarantine, a C11R comparison, an
  adjudication or a review. A planted forbidden import is caught.
* V17: every numeric literal in the certifier modules is in a structural allowlist; no string
  literal carries a >= 3-decimal number or a >= 4-digit rational other than cell 306's block. A
  planted magnitude is caught.
* V18: no original value in any file (above).
* V19/V20: the statements and the comparison rule are C11R's frozen ones (equality and a 32-case
  battery run through C11R's own `c11r_equiv.compare`).

## 4. Dependency versus reproduction

`C_T` and `tau` are consumed from C11R's ACCEPTED F_H certificate as frozen inputs: a
DEPENDENCY, not an independent reproduction and not a recomputation. The records declare them as
`C_T_independent`, `tau_independent` (C11R's independent line), which is what C11R's frozen schema
requires of the route `independent_derivative_propagation`. D1 and D2 themselves are produced only
by the C11RD pipeline.
