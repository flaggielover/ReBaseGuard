# B_int — reuse of the frozen P1 derivative bound as the softplus Lagrange factor

Additive governance successor. Authorizes exactly
`P1_DERIVATIVE_BOUND_REUSE_FOR_SOFTPLUS_LAGRANGE_FACTOR`
(`config/P1_BOUND_REUSE_AUTHORIZATION.json`, verified by `code/verify_governance.py`).
Predecessors preserved unchanged: endpoint strips `b48973d6`, B_int audit `fa92afb`, and everything before them.
**T2 is not closed by this record.**

## Decision: A — equivalent rigorous enclosure repair, permitted

1. **Only a valid enclosure is required.** L-R3.1 (PROOF.md) claims the containment whenever
   `A_{d+1}` "is a ball containing `sp^{(d+1)}(xi)/(d+1)!` for every `xi in U`". The claim does not
   depend on how the ball is built.
2. **Interval-series evaluation is not declared binding.** The L-R3.1 proof paragraph, its status line,
   SR_DERIVATION §9 and the harness docstring describe the construction that discharged the hypothesis.
   None of them makes it a requirement. The same frozen file `sr_local.py`, hash-pinned by the
   protected-inputs and governed-inputs manifests, already contains `softplus_enclosure_absolute`
   ("L-R3.1 with the ABSOLUTE derivative bound"). The L-R3.1 remark states every derivative is bounded by an
   absolute constant independent of `u`. In the Task1R checkpoint, "representation family" means the
   candidate representation. No frozen invariant names the Lagrange-ball construction: not in
   TASK1R_ADJUDICATION, not in GATE2F (non-binding; its only semantic change was the P1 threshold pair),
   and not in the excluded-routes register.
3. **M/9! is a frozen, proved enclosure of the same quantity.**
   `softplus_derivative_bound_tight(9)` bounds `|sp^(9)(u)| = |sigma^(8)(u)|` for **all real u**. That
   domain is a superset of every panel interval `U`. The frozen P1 rule already uses this M to certify
   `E_d = M rho^9 / 9! <= 1e-9` for the same ninth-order Lagrange remainder.
4. **Every dependency is preserved.** Both balls enter as one constant factor of `(x ± z)^9`, expanded by
   the unchanged `harness.softplus_tm2`. Neither tracks a correlation of the unknown `xi` with `x` or `z`,
   so there is no dependency to lose. The new ball has midpoint 0 and radius at least `M/9! > 0`, so no
   uncertainty becomes zero (ERROR_ALGEBRA §1).
5. **No budget line moves.** The ball occupies the same coefficient slots and reaches the certificate
   through the same channel: `int` (Arb interval radius), charged to `B_int`.
6. **No frozen threshold or degree changes.** These all stay as they were: softplus degree 8 (Lagrange
   order 9), D = 11, Z = 20, 256 bits, candidate degree 16, the P1 rule and check, panel geometry,
   candidates and contracts, all allowances, the 1/250 gate and B_cover. ERROR_ALGEBRA §7 lists the
   forbidden relaxations; none of them occurs.

This decision does not rely on the fa92afb numbers.

## Equivalence proof (machine-checked in `evidence/A9_P1_PROOF.json`)

1. **Derivative identity.** `sp' = sigma` and `sigma' = sigma(1-sigma)`. So `sp^(9) = sigma^(8) = p_8(sigma)`,
   with `p_{k+1} = p_k' · s(1-s)` by the chain rule. The frozen `p_8` equals an independent recomputation.
2. **Bernstein form.** Writing `p_8(s) = sum_k b_k B_{k,9}(s)`, with the identity checked exactly in
   rationals: the `B_{k,9}` are non-negative and sum to 1 on [0, 1], and `sigma(u)` lies in (0, 1).
   Therefore `|sp^(9)(u)| <= max|b_k| = M_exact = 15619/126` for every real u.
3. **The certifier's ball.** The frozen arb `M` contains `M_exact`. The certifier's `A9_P1` has midpoint
   exactly 0 and radius at least `M_exact/9!` (≈ 3.416e-4).
4. **Conclusion.** `A9_P1` contains `sp^(9)(xi)/9!` for every `xi` in every `U`, so the L-R3.1 hypothesis
   holds and its conclusion follows verbatim.
5. **Sanity checks (not part of the proof).**
   - On a 2,001-point grid over [−40, 40] and at 7 points where sigma is rational, arb_series agrees with
     `p_8(sigma)/9!` and lies inside `A9_P1`. The sampled supremum is 6.58e-6, so the bound is about
     52× the sampled supremum.
   - At the Task1R reference patch, `|A9_P1| rho^9` equals the frozen P1 `E_d` (8.864e-10) to within
     8e-10 relative.

**What stays fixed.** The substitution leaves unchanged the Taylor polynomial (`a_0..a_8` are the frozen
function's own output), the degree, the expansion centre, the radius `rho = H + h`, the function `sp`, the
dependency structure (the harness and downstream modules are unchanged files, and the single consumer is
`harness.softplus_tm2`, per a static scan) and the B_int accounting line. Only the tightness of the
enclosure changes.

## Supersession

The historical interval-series construction remains immutable historical evidence. It is superseded for
future T2 execution only.

PRE_T2 A1–A6/B/C and the A5 amendment stay in force, unchanged, as conformance checks on the preserved
frozen-ball mode. The untouched predecessor verifiers re-run here to confirm this. The successor mode is
certified by L-R3.1 with `A9_P1`, and it differs from the frozen-ball mode only in `A_9`.
