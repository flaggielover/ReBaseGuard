# R3 infrastructure successor: certified C_o0 / C_e0, real graded wiring, He₆, first-cell strategies

**Non-scientific, additive.**
- R1 (`e69a0224` / `4a1b20a8`) and R2 (`a1dcf1e8` / `327e0e13`) are byte-identical and pinned file by file.
- No real CUSUM cell is evaluated and no `R'''` of any `(D,m)` is computed.
- The real-cell authorization registry is frozen **empty**.
- Results are in `RESULT.md`, written after the freeze commit.

## A. Certified σ-odd resolvent bound C_o0

**Setting.**
- `K_0 f(x) = ∫ f(q(x,z)) φ(z) dz` over the survival window.
- `R` is the reachable state set: `{p·m = 0, max ≤ 5} ∪ {p, m > 0, p + m ≤ 4}`. It is invariant under one step (both
  coordinates positive after a step forces `p' + m' = p + m − 1 ≤ 4`) and is the frozen reachable cover.
- The norm is the sup norm of bounded functions on `R`. This is the norm of every frozen operator constant and of
  the graded proof.

**A1. Prerequisites.**
1. **Commutation.** `q(σx, z) = σ q(x, −z)`, φ is even, and the window `[m − c, c − p]` maps to itself under
   `z → −z`. So `σ K_0 = K_0 σ`, the survival event is σ-symmetric, and `σR = R`. (The real Arb kernels are checked
   in gate R05.)
2. **Invariance.** `P_o = (I − σ)/2` commutes with `K_0`, hence with `A_0 = I − K_0` and with `A_0⁻¹ = Σ K_0^j`
   (the Neumann series converges since `sup_x E_x τ < ∞`). So the odd subspace is invariant, and
   `P_o A_0⁻¹ P_e = 0`.
3. **Projected equation = graded system.**
   - The graded derivative system (R2 `graded_dag`) uses exactly `‖P_x A_0⁻¹ P_x‖ ≤ C_x0` inside
     `A(e)⁻¹ = (I − A_0⁻¹Δ)⁻¹ A_0⁻¹`.
   - `C_o0` bounds `A_0⁻¹` on odd functions: `‖P_o A_0⁻¹ P_o g‖ = ‖A_0⁻¹ (P_o g)‖ ≤ C_o0 ‖P_o g‖`.
4. **Conventions.** `‖P_x‖ ≤ 1` in the sup norm (σ is an isometry). Both the graded proof and the certificate use
   the sup norm on `R`, so they are compatible.

**A2. Theorem (odd reduction).** Let `T_0 = min{t ≥ 1 : X_t = (0,0)}`. For every σ-odd bounded `f` and `x ∈ R`:
`|(A_0⁻¹ f)(x)| ≤ ‖f‖ · E_x[τ ∧ T_0]`.

*Proof.* `u = A_0⁻¹ f = E_x Σ_{t<τ} f(X_t)` is σ-odd, and `(0,0)` is σ-fixed, so `u(0,0) = 0`. The strong Markov
property at `T_0` gives `u(x) = E_x Σ_{t<τ∧T_0} f(X_t) + E_x[u(0,0); T_0 < τ]`, and the second term is 0. ∎

The reset state `(0,0)` is an atom: the frozen kernel's "origin" piece `∫_{m−1/2}^{1/2−p} φ`, positive for
`p + m < 1`.

**A3. Theorem (supersolution).** Let `K̂` be `K_0` with the origin piece removed (`(0,0)` absorbing). If a bounded
`w ≥ 0` on `R` satisfies `w ≥ 1 + K̂w`, then `E_x[τ ∧ T_0] = Σ_j K̂^j 1 ≤ w`.

*Proof.* By induction `Σ_{j<n} K̂^j 1 ≤ w`, since `K̂` is positive. ∎

So `C_o0 := sup_R w`. The same argument with `K_0` gives `C_e0 := sup_R w_e ≥ sup_x E_x[τ] = ‖A_0⁻¹‖`, a bound for
every function, in particular even ones.

**A4. Certification** (`code/resolvent_certificate.py`). No global inverse is built and no float is rounded into a
certificate.
- **Proposal.** `w` is an exact dyadic degree-12 Chebyshev polynomial, proposed from the float solution of
  `(I − K̂)g = 1` on the frozen grid and scaled `αg + β`.
- **Margin.** `L := w − 1 − (K̂w)_poly − allowance`, where:
  - `(K̂w)_poly` is the frozen Pair enclosure at `e = 0` minus the frozen origin piece;
  - the allowance is the frozen `Z_RANGE·sup|w|·ε_z`, charged twice for the odd case (Kw and the removed piece).
- **Certified quantities.** Bernstein coefficients on the frozen reachable cover with subdivision give
  `min_R L > 0`, `min_R w ≥ 0` and `C = max_R w`.
- **Artifacts** (`config/operator_certificates/*.json`) store the payload; `verify_artifact` recomputes every
  number from it.

| constant | (α, β, depth) | certified margin ≥ | min w ≥ | **certified bound** | float reference (not evidence) |
|---|---|---:|---:|---:|---:|
| `C_o0` | (13/10, 0, 2) | 0.0205 | 8.73 | **20.4322** | odd-resolvent norm ≈ 4.68; `E τ∧T_0` ≈ 16.6 |
| `C_e0` | (201/200, 2, 3) | 0.00409 | 252.9 | **469.7697** | ARL ≈ 465.4 (frozen `C_upper` 1232.8) |

Every attempt in the parameter scan is disclosed. α ∈ {1.05, 1.2} failed. α ∈ {1.3, 1.35, 1.4, 1.6, 2.0} certified,
at 20.43, 21.22, 22.00, 25.15 and 31.43; the smallest certified value was frozen. Any certified supersolution is a
valid bound, so the scan selects a certificate, not a result.

`C_o0` (20.4) exceeds the float odd-norm estimate (4.68) because `E_x[τ ∧ T_0]` is a coupling bound on the odd
resolvent, not its norm. That slack is quantified in section H.

## B. Certified C_e0 (diagnostic)

**C_e0 = 469.7697** certifies `‖A_0⁻¹‖` for every function, 2.62× sharper than the frozen cell-0 `C_upper`. Its
effect on the forecast is in section H.

## C. Real graded wiring (`code/graded_real.py`)

- **`GradedRealCertifier(R1 Order3Certifier)`.** The frozen `certify` is extended by explicit subclassing to capture
  each residual Pair.
- **Graded residual.** Reachable-set Bernstein ranges of `(res ± swap res)/2` plus the entry's **final** truncation
  allowance; t is the frozen certified `delta_mid`, exactly. Repair1 rewrites the r = 0 F/D/H allowances after
  `certify`, and the final entry is the one used.
- **Parity table at e = 0:**
  - `h` is even; `S_0`, `S_r`, `F_r`, `W_(r,j)` are odd. The n-th derivative flips parity n times.
  - `K_i(0)` has parity `(−1)^i` and `J_i(0)` has parity `(−1)^(i+1)`.
- **Envelopes.**
  - Operator residuals use `graded_env` on the graded candidate suprema, with the frozen residual-derivative term
    lists (candidates are constant in e).
  - Closed-form leaves use `graded_true_sup` with `sup|S_0^(n)|` (cell) and the next order (hull, times η).
- **Norms.** `k_0..k_6` and `j_0..j_6` on the cell and on the hull of {0} ∪ cell: frozen orders 0–4 plus section D.
- **Constants.** `C_o0` and `C_e0` are loaded only from the pinned certificate registry, with artifact sha256
  checked. A missing or altered entry makes the path **refuse**.
- **Scalar fallback.** `graded_dag` with `parity=False` is the R1 scalar cascade. When the Neumann condition fails,
  the resolvent block falls back to scalar `C` (R2 rule).
- **Entry point.** `certify_real_cell_r3` checks, in order: empty authorization registry, then certificates, then
  the K1 record. Authorized evaluation is out of R3 scope.

Qualification on the real Arb path uses synthetic candidates (`code/synthetic_real.py`; gates R05–R08, R12, R13).

## D. He₆ / j₅ extension (`code/hermite6_ext.py`)

**Need.** `j_5` enters the leakage of order-3 S envelopes and the R⁽⁵⁾ tower. It needs `∫_W |He_6| φ`.
`sup|S_0^(5)|` needs the extrema of `He_5 φ`, which are roots of He₆. The frozen table stops at He₅.

**Construction.** A separate artifact; the frozen table is unchanged.
- `He_6 = x⁶ − 15x⁴ + 45x² − 15`.
- Roots `±√t_i`, where `t_i` are the roots of `t³ − 15t² + 45t − 15`.
- Exact sign-change isolation, bisection to `2^−(bits+32)`, outward `sqrt` balls.
- A root ball that straddles a window endpoint refuses.
- Each bound is `min(drift-aware, reviewed)`; `j_6` and `sup|S_0^(6)|` use the reviewed whole-line bounds.

| cell 0 | drift-aware (R3) | reviewed |
|---|---:|---:|
| `j_5` | 13.81 | 35.46 |
| `sup|S_0^(5)|` | 4.61 | 9.49 |

## E. Qualification design (non-scientific)

Gates R01–R17 are in `config/PRE_RESULT_GATES_R3.json`; fixtures, seeds and mutations are in
`config/QUALIFICATION_PROTOCOL_R3.json`. Every part runs in a fresh process on vultr-02 at the freeze commit.

| part | what it checks | gates |
|---|---|---|
| `certificates` | exact replay of both artifacts; registry consistency | R02–R04, R13 |
| `certificate_mutations` | frozen verifier rejects the 4/5-scaled odd payload; each verifier mutant accepts it or fails the exact artifact replay | R12 |
| `parity` | σ-structure of the real Arb `K_i(0)`, `J_i(0)` | R05 |
| `synthetic_real` (+ replay) | synthetic parity-pure candidates through the frozen prepare / certify / Repair1 path: scalar equivalence with the frozen midpoint DAG, Aux3 and R1 rung (C1); float-quadrature residual parity parts inside graded mid / cell bounds (C2, C3); `K_i`, `J_i` parity identities (C4); graded ≤ scalar; wiring mutants RW01–RW12; payload hash | R06–R08, R12, R13 |
| `he6` | section D verification; orders 0–4 identical to the frozen table; extension ≤ reviewed; moment ≥ quadrature; straddle refusal | R09 |
| `first_cell` | FC1–FC5 manufactured odd systems: A, B and point enclosures, tower components, M5 against exact truth; evenness lemma with non-odd control; R⁽⁵⁾ mutants B01–B06 | R10–R12 |
| `forecast` (+ replay) | section H, deterministic hash | R13 |
| `r2_regression` | R2 graded soundness | R17 |
| `failclosed`, `fence` | refusals, import fences, no monkeypatch, registries, R1/R2 pins | R01, R14, R15 |

**DEV calibration** (seed-disjoint: fixture seeds + 900000, synthetic seed 9001, lemma seed 99001) was used only to
fix required-mutation flags and to find defects before the freeze. It found two:
- The R⁽⁵⁾ tower's `h_1` leaf used the CUSUM identity `h_1⁽ⁿ⁾ = −S_0⁽ⁿ⁻¹⁾`, which manufactured systems do not
  satisfy (tower violations on 4 of 5 DEV fixtures). The tower now takes explicit `h_1` leaf suprema when supplied.
  The CUSUM default, the frozen real-wiring convention, is unchanged.
- The certificate mutants CM01 and CM03 did not change acceptance of the control payload (CM01 moves bounds by
  ball radii only; CM03 acts on the low branch, where the control payload does not fail). Detection now also
  counts failing the exact artifact replay, which is the verifier's own check.
- The wiring mutants RW02 (F-envelope norm-order shift) and RW11 (candidate-sup parity swap) went undetected.
  - RW11 was masked by a cache: `graded_sup` cached the graded result on the certifier, so mutants read the
    unmutated value. The cache was removed; only the Bernstein range data stays cached.
  - Two checks were added: C6 (graded candidate sups dominate float even/odd parts at the reachable states, gate
    R07) and C7 (every operator-residual envelope term list equals the generic Leibniz rule, gate R06).
  - After this, DEV detected 12/12 wiring, 6/6 R⁽⁵⁾ and 3/3 certificate mutants, so every mutation is required.

## H. Cell-0 forecast (`code/cell0_forecast_r3.py`)

- **Inputs.** Only the committed Aux5 cell-0 record magnitudes, the certified `C_o0` and `C_e0`, the frozen and
  extended norms, and `sup|S_0⁽ⁿ⁾|`. No `R'''` value.
- **Strategy A.** The graded whole-cell radius.
- **Strategy B.** The point radius under assumption A1 (point-run residuals equal the committed e0 magnitudes), plus
  `(x_1²/2)·M5` from the anchored tower. A conservative proxy is also reported.
- **Classification.** The predeclared classes against `S*` (`config/FEASIBILITY_CRITERION_R3.json`).
- **Diagnostics** (attribution only, not certified where marked):
  - `C_o0` replaced by the non-certified float estimate 4.68;
  - `C_e0` replaced by `C_upper`;
  - no leakage;
  - residuals ×0.1;
  - midpoint vs cell;
  - unanchored vs anchored M5.
- **Next-step input.** The best case with the float `C_o0` is the only input to the
  REPAIR_GRADED_OPERATOR_CERTIFICATE branch of the next-step rule.

## F. First cell: two certified strategies

K5-B needs `L_1 ≤ inf_{[0,x_1]} R'''`, with `x_1 = 5083/10⁷` for CUSUM cell 0.

**Strategy A (generic graded).** `L_A = lo` of the graded whole-cell interval (R2 method, section C inputs).

**Strategy B (point + evenness transport).**
- **Lemma.** R is odd (P5-T3) and real-analytic (P5X L5, reviewed at `879792d0`), so `R'''` is even and
  `R''''(0) = 0`. Hence
  `R'''(e) = R'''(0) + ∫_0^e (e − t) R⁽⁵⁾(t) dt ≥ R'''(0) − (e²/2) sup_[0,e] |R⁽⁵⁾|`.
  So `L_B = lo(I_0) − (x_1²/2)·M5`, with `I_0 ∋ R'''(0)` from a degenerate-cell point run (`e0 = 0`, `ρ = 0`) and
  `M5 ≥ sup_[0,x_1] |R⁽⁵⁾|`.
- **Checks.**
  - Independent: exact odd polynomials, and a non-odd control with `R''''(0) < 0` where the bound must fail (gate R11).
  - Manufactured σ-systems are exactly odd: `σK(e)σ = K(−e)`, `σS_0(e) = −S_0(−e)`, so `F_r(−e)(x0) = −F_r(e)(x0)`.
- **M5 semantics** (`code/r5_majorant.py`). An absolute, unsigned majorant.
  - At the σ-fixed `x0` only even parts survive: `|R⁽⁵⁾_m(e)| ≤ Σ|c| sup ‖P_e X⁽⁵⁾(e)‖`.
  - A graded tower of true objects on the hull `[0, x_1]` uses the graded operator and resolvent rules with the
    certified constants.
  - Orders ≤ 3 can be anchored by (graded candidate sup + graded whole-cell error). This is valid componentwise.
- **Not supplied by Aux3.** Aux3/aux_refine towers stop at order 4 and are scalar. They are not used.

## G. R⁽⁵⁾ majorant source audit

| candidate source | usable? |
|---|---|
| existing frozen towers | no: order ≤ 4, scalar, `C`-based (unanchored graded tower at cell 0: 2.8·10¹³) |
| parity alone | reduces the tower but not enough without anchors |
| analytic Gaussian/Hermite bounds | supply the source leaves `S_0⁽ⁿ⁾` (sections D, F) but not the resolvent chain |
| norm-only operator recurrence | yes, as the graded tower (built here) |
| cheap non-signed bound | yes: the **anchored** graded tower. It needs only data a real point/cell run already produces (candidate suprema, graded whole-cell errors) plus the certified constants; no order-4/5 rung and no new solve |

`R5_MAJORANT_SOURCE = CHEAP_SUCCESSOR`. It is built and qualified in R3 on manufactured systems; its real inputs come
from a future authorized run.
