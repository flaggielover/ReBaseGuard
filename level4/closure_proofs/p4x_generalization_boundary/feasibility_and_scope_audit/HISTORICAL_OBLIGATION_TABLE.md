# Historical P4 obligation table

Reconstructed by reading the frozen artifacts, not their summaries.  Every row
cites the file it was read from.  Nothing here is new science and nothing here
edits P4.

Source tree, by git object:

```text
git rev-parse HEAD:level4/closure_proofs/p4_theory_generalization
  = eede90383da44c250871b1bb97d12045c897c8d9
```

## 1. Theorem statement as frozen

From `p4_theory_generalization/THEOREM.md` §3 (G1), verbatim in content:

```text
Assume (A1)-(A7).  Then g_m is differentiable at 0,

    g_m'(0) = -Gamma_{D,m,f},   Gamma_{D,m,f} := E_0[ A_m S_tau^psi ]      (G1a)

and F_{rho,m} is differentiable at 0 with

    F'_{rho,m}(0) = rho (1 - Gamma_{D,m,f}).                               (G1b)

    psi = -f'/f,   S_tau^psi = sum_{t=1}^{tau} psi(Z_t),
    A_m = (1/w) sum_{r=0}^{w-1} Z_{tau-r},   w = min(m, tau),
    Z_t = eps_t - e,   f_e(z) = f(z+e),
    F_{rho,m}(e) = rho (e + g_m(e)),  g_m(e) = E_e[A_m].
```

Companions, same file:

| id | statement | section |
|---|---|---|
| `G1'` | the same identity at a general base point `e0`, score evaluated at the unshifted innovations `eps_t = Z_t + e0` | §4 |
| `G2` | deterministic `tau ≡ n` ⟹ `g_m(e) = -e`, `F_{rho,m} ≡ 0`, and `Gamma = 1` exactly for every regular location family, via `E[psi]=0`, `E[eps psi(eps)]=1` | §5 |
| `G3a` | pathwise `A_m S = B_m S + 1{tau<m}(1/tau - 1/m) T_tau S`; the **identity** is general, the Gaussian sign `Q_m >= 0` is **not** | §6 |
| `G4` | `f` even + reflection-equivariant detector ⟹ `E_0[A_m] = 0`, origin is a fixed point, P3 classification applies with `rho_c = 1/\|1-Gamma\|` | §7 |
| `F1` | moving support breaks (A3) and the identity is **false**: uniform on `[-a,a]`, memoryless `\|Z\|>=c`, exact defect `2` at `a=1, c=1/2` | §9 |
| `F2` | no first moment breaks the **map**: Cauchy, `E\|A_1\| = infinity` under the frozen CUSUM, so `g_m(e)` is undefined | §9 |

`G3`'s converse was **narrowed** by independent adjudication: Gaussian
sufficiency plus explicit non-Gaussian failure is claimed; an iff
characterisation is not (`INDEPENDENT_ADJUDICATION.md`, "Theorem narrowing").

## 2. Assumptions A1-A7 as frozen

Verbatim scope from `THEOREM.md` §2 and `CLOSURE_REPORT.md` §3.

| id | assumption | where used | discharged by |
|---|---|---|---|
| A1 | parameter-free path functional: `{tau=n} ∈ F_n`; `A_m`, `T_tau` Borel in the first `n` residuals; detector recursion, threshold, inclusivity and tie rule do not depend on `e` | `PROOF.md` §1.1 (change of measure restricted to `F_tau`) | property of the two frozen detectors |
| A2 | `tau < infinity` `Q_e`-a.s. for `\|e\| <= d0` | throughout | `L1` geometric stopping tail |
| A3 | local common support and absolute continuity: `f > 0` a.e. on a translation-invariant set; `f` locally absolutely continuous; `psi = -f'/f` defined a.e. | `PROOF.md` §1.1 | model class |
| A4 | `e -> L_tau(e)` differentiable **at zero** a.s. with derivative `-S_tau^psi` | `PROOF.md` §2 | `L5` |
| A5 | `A_m ∈ L^1(Q_0)` and `A_m S_tau^psi ∈ L^1(Q_0)` | `PROOF.md` §2 | `L2`+`L3` or `L2`+`L4` |
| A6 | locally Lipschitz stopped likelihood with integrable constant: `\|A_m\|·\|L_tau(e)-L_tau(e')\| <= G\|e-e'\|` on `[-d,d]`, `G ∈ L^1(Q_0)` | `PROOF.md` §2 | `L3` or `L4` |
| A7 | fresh reference `U` independent, `E[U] = mu`, entering affinely with coefficient `1-rho`; forces `E[eps] = 0` and `E\|eps\| < infinity` | `PROOF.md` §3 | model definition |

Discharge lemmas, `PROOF.md` §8: `L1` geometric stopping tail from a one-step
forcing event (`c_D = h+k` for CUSUM, `c_D = 1/2 + log A` for SR); `L2`
`E[\|A_m\|^r] <= E\|Z\|^r E[tau]`; `L3` bounded score + a `1+eta` moment;
`L4` at-most-linear score + an exponential moment; `L5` (A4) from
differentiability of `log f` at the finitely many residuals.

**No finite variance is required** (`CLOSURE_REPORT.md` §3).

## 3. Scope as frozen

| axis | frozen scope | source |
|---|---|---|
| detectors | exactly two: frozen two-sided CUSUM `k=1/2, h=5`; frozen symmetric two-chart SR `A=520.886133602749`, no headstart. Plus the memoryless validation rule `tau = inf{t: \|Z\|>=c}`, which is **not** a frozen detector | `THEOREM.md` §10; `configs/P4_PROTOCOL.json` |
| operating-point layers | `frozen` (`cusum@5`, `sr@520.886`) and `reduced` (`cusum@2`, `sr@20`) | protocol `layers` |
| windows | `m ∈ {1,2,3,5}` numerically; the **theorem** is stated for every `m >= 1` | protocol `m_grid`; `THEOREM.md` §3 |
| location families | 6 `THEOREM-SUPPORTED`: gaussian, laplace, logistic, skewnormal4, t1p5, t3.  2 `OUTSIDE-ASSUMPTIONS`: uniform (moving support), cauchy (no first moment) | protocol `families` |
| numerical correspondence | 4 routes kept apart: **A** score route, **B** Richardson finite difference, **Q** deterministic quadrature (memoryless detector only), **N** deterministic-stopping neutrality control | `NUMERICAL_CORRESPONDENCE.md`; `EVIDENCE_BOUNDARY.md` §3 |
| certification | 3 Arb objects at 160 bits (Laplace unbounded-horizon closed form; uniform exact rational defect; finite-support bounded-score tilt witness).  **No frozen CUSUM or SR gain is interval-certified** | `EVIDENCE_BOUNDARY.md` §4, §6 |
| Lean | 19 declarations, axioms exactly `propext`, `Classical.choice`, `Quot.sound`; no `sorry`, no project axiom.  Constructs no probability space, discharges no `L1`-`L5`, evaluates no `Gamma` | `LEAN_CORRESPONDENCE.md` §1, §3 |
| explicitly NOT claimed | distribution-free; detector-universal; global; nonlinear; valid for moving support; valid without a first moment; ARL-matched cross-family comparison; asymmetric classification at the origin; novelty | `THEOREM.md` §10; `CLOSURE_REPORT.md` §10-§11 |

## 4. Frozen gates and their literal statuses

From `results/closure_decision.json`, derived mechanically by `derive_closure.py`.

| # | gate | status |
|---|---|---|
| 1 | `protocol_hash_matches_manifest` | PASS |
| 2 | `witness_hash_matches_manifest` | PASS |
| 3 | `route_q_analytic_identity_holds` | PASS |
| 4 | `route_q_uniform_identity_fails_as_predicted` | PASS |
| 5 | `route_n_neutrality_holds` | PASS |
| 6 | `all_theorem_supported_cells_pass` | **FAIL** |
| 7 | `all_outside_assumption_cells_demonstrate_failure` | **FAIL** |
| 8 | `both_frozen_detectors_covered` | PASS |
| 9 | `at_least_five_theorem_supported_families` | PASS |
| 10 | `asymmetric_family_origin_not_a_fixed_point` | PASS |
| 11 | `gaussian_consistency_with_closed_core` | **FAIL** |
| 12 | `certificate_all_checks_pass` | PASS |
| 13 | `lean_compiles_with_clean_axioms` | PASS |
| 14 | `repository_verification_all_gates_pass` | PASS |

Six negative claims are asserted false and all six hold.

Numeric gate thresholds, `configs/P4_PROTOCOL.json` `gates`:

```text
correspondence_relative_limit = 0.03      (inherited unchanged from Track 3)
correspondence_z_limit        = 4.0
counterexample_min_relative   = 0.5
counterexample_min_z          = 10.0
consistency_z_limit           = 4.0       (frozen_reference_values)
```

## 5. Final P4 PARTIAL rationale

`CLOSURE_REPORT.md` §1, and `INDEPENDENT_ADJUDICATION.md`:

> the generalization is established as mathematics after one G3 prose
> narrowing, both named discrepancies are reconciled, and repository
> verification passes; but three frozen numerical gates remain literally false,
> so the mechanically consistent verdict is still PARTIAL.

Independent adjudication accepted the derivative theorem on re-derivation,
reconciled both named numerical discrepancies, replayed Lean and Arb, and
confirmed twelve protected trees byte-identical to `HEAD` — and still returned
`PARTIAL`, because **three literal frozen gates were not weakened or
regenerated**.

## 6. Downstream position

From `p9r_final_synthesis_repair/results/claim_ledger.json`:

| node | class | licensed strength | assumptions |
|---|---|---|---|
| `ASM-P4-A1A7` | `NOT_ESTABLISHED` | 0 | — |
| `P4-T1` | `CONDITIONAL_THEOREM` | 4 | `ASM-P4-A1A7` |
| `P4-T2N` | `CONDITIONAL_THEOREM` | 4 | — |
| `P4-L1` | `FORMALLY_VERIFIED` | 6 | — |
| `P4-F1` | `NEGATIVE_RESULT` | 2 | — |
| `P4-RESULT` | `PARTIAL_PRIORITY_RESULT` | 1 | — |
| `P4-STATUS` | status | — | `P4 = PARTIAL` |

Edges touching P4:

```text
P4-T1   <- ASM-P4-A1A7   ASSUMPTION
P4-T1   <- P4-STATUS     STATUS_PROPAGATION
P4-T2N  <- P4-T1         LOGICAL_PREMISE
P4-L1   <- P4-T1         FORMAL_SUPPORT
P4-F1   <- P4-STATUS     STATUS_PROPAGATION
P4-RESULT <- P4-T1       LOGICAL_PREMISE
P4-RESULT <- P4-F1       NEGATIVE_RESULT_CONSTRAINT
P4-RESULT <- P4-STATUS   STATUS_PROPAGATION
GLOBAL-CLOSURE <- P4-STATUS  STATUS_PROPAGATION
```

**No claim outside the P4 sub-graph takes P4 as a premise.**  P4 consumes P1,
P2, P3 and Track 3; nothing consumes P4 except the global-closure status node.
P4 is a scientific leaf.
