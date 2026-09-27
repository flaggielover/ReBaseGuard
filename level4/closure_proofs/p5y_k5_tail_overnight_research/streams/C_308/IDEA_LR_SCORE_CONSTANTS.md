# Idea note (timestamped before any evaluation): likelihood-ratio / score representation of the atom constants

Written 2026-09-28 (overnight), before any computation on any CUSUM cell. It is motivated by the structure of the
kernel and by an exact synthetic probe. No cell data is used.

## Synthetic probe (exact finite-state drift families, 8 seeds, e = 1/8)

The probe compared three quantities for the atom functionals of R, ∂R and ∂²R:
* Lemma G's scalar constants;
* the positive-kernel majorants that replace the signed K₁ by |K₁|;
* the true functional norms.

| quantity | positive majorant vs Lemma G | true functional norm vs positive majorant |
|---|---|---|
| A1 = ‖δ_a R K₁ R‖ | 1.2–2× smaller | **3–10× smaller** |
| A2 | 1.2–2× smaller | **10–20× smaller** |

A0 = ‖δ_a R‖ = (R1)(a) exactly, because R ≥ 0. It is the ARL at the atom, Λ, and Lemma G's C exceeds it by 1.00–1.25×.

**Conclusion.** The slack in A1 and A2 lives in the **sign cancellation of K₁ and K₂**. A positive majorant destroys
it. A route that bounds |K₁| cannot recover it.

## The structural identity

For the CUSUM kernel, the drift e enters only through the increment density, `z + e ~ N(0,1)`. The alarm window
`[ell, up]` and the update map `n(x, z)` do not depend on e. Therefore

    (K₁ g)(x) = ∫ g(n(x,z)) ∂_e φ(z+e) dz = E[ g(n(x,Z)) · S ],       S := −(Z + e) ~ N(0,1)  (the score),
    (K₂ g)(x) = E[ g(n(x,Z)) · (S² − 1) ].

By the likelihood-ratio derivative of `E_a^e[Σ_{n<τ} f(X_n)]`, where `{n < τ}` is determined by `Z_1..Z_n`:

    (∂R f)(a)  = E_a[ Σ_{n<τ} f(X_n) · M_n ],               M_n := Σ_{k≤n} S_k,
    (∂²R f)(a) = E_a[ Σ_{n<τ} f(X_n) · (M_n² − n) ].

Hence, for the functionals that TC / TC-T need:

    A1_true = ‖δ_a ∂R‖ ≤ A1^LR := E_a[ Σ_{n<τ} |M_n| ],
    A2_true = ‖δ_a ∂²R‖ ≤ A2^LR := E_a[ Σ_{n<τ} |M_n² − n| ],

and A1^LR ≤ the positive majorant (R|K₁|R1)(a), by the triangle inequality inside M_n.

## Certification (no Monte Carlo)

(X_n, M_n) is Markov on the augmented state (p, m, μ). Use quadratic-in-μ supersolutions
`w(x, μ) = a(x) + b(x) μ²`, with `|μ| ≤ (c + μ²/c)/2` and `|2μ c₁(x)| ≤ δ μ² + c₁(x)²/δ`.
* The inequality `w ≥ |μ| + E[w(X', μ+S) 1_surv]` reduces to **two linear supersolution inequalities on the original
  2-D state**, for b and then for a.
* Their kernel terms need only E[g(X')·S^j 1_surv] for polynomial g. These are Gaussian moments, the same exact
  machinery as the existing rational kernel_apply.
* Then `A1^LR ≤ a(atom)`.

A2 works the same way with a quartic-in-μ ansatz. Uniformity over a drift block `[e_lo, e_hi]` needs interval-drift
kernel evaluation, as in I1/I2.

## Status and governance

| item | status |
|---|---|
| status | THEORY_ONLY |
| cells potentially relevant | 307 (C3 knockout: blocker is (A1, A2)) and 308 (partial) |
| stream assignment | this note is filed under C_308 for the operator-level stream, but applies to every cell |
| r2 | **closure-only**: it is neither a Lemma G nor a Lemma Dv′ supply |
| quarantine | never to be evaluated on a tail drift block tonight; validation drifts must avoid [1.2, 2.6] |

## Erratum (after `reviews/REVIEW_GLOBAL_INTEGRITY_R1.md` F8)

The ratio ranges in the probe table above were hand-copied from console output and were inaccurate. The probe is now
a guarded producer, `pm_probe_synthetic.py`, which writes `validation/PM_PROBE_SYNTHETIC.json` with the same declared
set. Its exact-arithmetic ranges over the 8 seeds are:

| ratio | A1 | A2 |
|---|---|---|
| positive majorant / true functional norm | **2.43–9.20** (not "3–10×") | **7.34–23.6** (not "10–20×") |
| Lemma G / positive majorant | 1.22–2.07 | **1.53–2.45** (not "1.2–2×") |

The conclusion is unchanged: the slack lives in the sign cancellation of K₁ and K₂.
