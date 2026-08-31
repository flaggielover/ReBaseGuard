# Assumption and dependency audit

Phase A of the Priority-4 charter: read the closed artifacts, reconstruct
exactly which steps depend on Gaussianity, and separate the layers.  No frozen
artifact is modified; each row cites the frozen text it audits.

## 1. Sources audited (read-only)

| artifact | status | what it fixes |
|---|---|---|
| `m_gt_1_priority1/THEOREM.md`, `PROOF.md` | CLOSED (P1) | truncated window `w=min(m,tau)`, abstract score-at-zero theorem, Gaussian stopped likelihood, random-denominator decomposition |
| `sr_derivative_priority2/THEOREM.md` | CLOSED (P2) | frozen SR recursion and threshold, same window and stopping conventions, its own discharge of the abstract hypotheses |
| `m_rho_stability_priority3/THEOREM.md` | CLOSED (P3) | `lambda = rho(1-Gamma)`, `rho_c = 1/\|1-Gamma\|`, admissible domain, interval-robustness rule |
| `location_family/THEOREM.md`, `FINAL_REPORT.md` | PARTIAL | regular location-family stopped-score identity for a *single terminal observation* |
| `location_family_track3ab/THEOREM.md`, `FINAL_REPORT.md` | CLOSED | replication of that `m = 1` result; Lean spine in which the derivative bridge is an **assumed hypothesis** |

## 2. The four layers

**(L-I) Detector-independent structure.**  Nothing here mentions a density or a
recursion.

* the state map `F_{rho,m}(e) = rho(e + E_e[A_m])` (needs only (A7));
* exact `rho` scaling of the derivative;
* the window algebra `w = min(m,tau)`, `A_m`, `B_m`, and the pathwise
  decomposition `A_m S = B_m S + 1{tau<m}(1/tau-1/m) T S`;
* the classification `|lambda|<1 / =1 / >1` and `rho_c = 1/|1-Gamma|`.

**(L-II) Location-family structure.**  Needs a density, not a Gaussian one.

* `f_e(z) = f(z+e)`, parameter score `s = f'/f = -psi`;
* the stopped change of measure `E_e[H] = E_0[H L_tau(e)]`;
* `d/de L_tau(e)|_0 = -sum_{t<=tau} psi(Z_t)`;
* the derivative identity `g_m'(0) = -E_0[A_m S_tau^psi]`;
* the integration-by-parts identities `E[psi] = 0`, `E[eps psi(eps)] = 1`, hence
  the neutrality corollary.

**(L-III) Gaussian-specific identities.**  Exactly three, and no more.

* `psi(z) = z`, i.e. the score sum *is* the residual total `T_tau`.  This is the
  single substitution that turns the general theorem into P1/P2.
* `L_tau(e) = exp(-e T_tau - (e^2/2) tau)` in closed form.  Generally there is
  no closed form, only the product `prod f(Z_t+e)/f(Z_t)`.
* `T_tau S_tau^psi = T_tau^2 >= 0`, which is what makes P1's short-window
  correction `Q_m` pathwise nonnegative.  Priority 4 proves this Gaussian
  sufficiency and gives explicit non-Gaussian negative witnesses; it does not
  claim the unproved converse that no other score could preserve the sign on
  every admissible path.

**(L-IV) Numerical and certification-only assumptions.**  Not part of any
theorem.

* frozen thresholds `h = 5` and `A = 520.886133602749`, and the reduced
  operating points `h = 2`, `A = 20` used for the primary correspondence grid;
* batch counts, path counts, seeds, and the `O(h^2)` Richardson step pair;
* the 3% relative correspondence limit, inherited unchanged from Track 3;
* the finite-support / closed-form objects used by the Arb layer.

## 3. Dependency table

Where each hypothesis actually enters, and what breaks without it.

| # | assumption | enters at | needed for | Gaussian-specific? | what fails without it |
|---|---|---|---|---|---|
| 1 | existence of a density `f` | change of measure, `PROOF.md` 1.1 | G1, G1' | no | no likelihood ratio; the derivative may still exist but has no score form |
| 2 | local common support / absolute continuity (A3) | `PROOF.md` 1.1 | G1, G1' | no | **provably false conclusion** -- the uniform counterexample, `PROOF.md` 9 |
| 3 | symmetry of `f` | G4 only | fixed point at `0`, P3 map at `0` | no | `0` is not a fixed point; the derivative identity is unaffected (skew-normal cell) |
| 4 | differentiability of `e -> log f(z+e)` at `0`, a.s. (A4) | `PROOF.md` 2 | G1 | no | no pointwise limit for the difference quotient |
| 5 | differentiability at *every* `e` in a neighbourhood | **not used** | -- | -- | this is the P1/P2 hypothesis; it is **false for Laplace** and is not needed |
| 6 | score regularity `psi` measurable, a.e. defined | (A3) | G1 | no | `Gamma` undefined |
| 7 | finite first moment of `eps` | (A5), (A7), L2 | the map itself | no | **provably false conclusion** -- the Cauchy failure, `PROOF.md` 10 |
| 8 | finite second moment of `eps` | **not needed** | -- | -- | Student-`t` with `nu = 1.5` is inside the theorem |
| 9 | exponential moments of `eps` | L4 only | domination for unbounded scores | *partly* -- P1/P2 need it because the Gaussian score is unbounded | bounded-score families replace it by a `1+eta` moment (L3) |
| 10 | bounded score `sup\|psi\| <= M` | L3 | the cheapest domination route | no (it excludes Gaussian) | fall back to L4 |
| 11 | dominated difference quotient (A6) | `PROOF.md` 2 | G1 | no | interchange unjustified |
| 12 | stopping-time integrability / geometric tail | L1, L2, L3, L4 | (A2), (A5), (A6) | no | domination integrals may diverge |
| 13 | detector path regularity: `{tau=n} ∈ F_n`, `e`-free recursion (A1) | `PROOF.md` 1.1 | G1 | no | the change of measure does not restrict to `F_tau` |
| 14 | reuse-window truncation `w = min(m,tau)` | window algebra | G1, G3 | no | this is P1's contribution and is carried over unchanged |
| 15 | random denominator `1/w` | `PROOF.md` 1.2 | G1 | no | nothing: `1/w ∈ [1/m, 1]` is bounded, `e`-free, and never separated from the numerator |
| 16 | `T_tau S_tau^psi >= 0` | G3 sign | `Q_m >= 0` | **yes** | the correction, and its expectation, can be strictly negative (certified) |
| 17 | interchange of differentiation and stopped expectation | `PROOF.md` 2 | G1 | no | -- |
| 18 | fresh reference unbiased (A7) | `PROOF.md` 3 | the map's affine form | no | an extra constant appears and `0` need not be fixed |

## 4. What the audit changes about the closed core's own statement

Two findings are about P1/P2 themselves, and neither weakens them.

1. **Row 5 -- their differentiation hypothesis is stronger than their proof
   needs.**  P1's hypothesis 6 and P2's hypothesis 5 ask for an integrable
   dominator of the pointwise `e`-derivative on a neighbourhood.  Their proofs
   use the derivative only at `e = 0`.  For the Gaussian family the distinction
   is invisible, because the Gaussian likelihood is smooth in `e` everywhere.
   It becomes visible the moment the family is allowed a kink.  P1 and P2
   remain correct as stated; Priority 4 records that the hypothesis can be
   weakened and proves the weaker version in Lean.

2. **Row 16 -- their nonnegativity result is a Gaussian result.**  P1's
   `Q_m >= 0` and the reading that "the random denominator cannot be replaced
   by `m`, because doing so deletes `Q_m`" are both correct for the Gaussian
   model.  The *direction* of the deletion is not general: for a bounded score
   the truncated-window gain can be strictly smaller than the
   fixed-denominator gain.

Neither finding is an integrity problem and neither frozen artifact is edited.

## 5. Assumptions Priority 4 audited and found *not* required

* finite variance (row 8) -- a `1 + eta` moment suffices;
* symmetry for the derivative identity (row 3) -- only the fixed point needs it;
* exponential moments in general (row 9) -- only for unbounded scores;
* smoothness of the log-density away from the base point (row 5);
* any relationship between the detector and the family's own likelihood.  The
  frozen SR chart is the Gaussian likelihood ratio; applied to Laplace or
  Student-`t` innovations it is simply a fixed path functional, and the theorem
  is indifferent.
