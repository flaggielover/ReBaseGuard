# D2.3 / D1.4 — finite-difference and root-scan pre-commitment

**Written 2026-08-22, BEFORE any induced-map data was generated.**
`STAGE_D_PROTOCOL.md` (`925adecf…`) fixes the D2.3 criterion — central finite
difference of the actual induced map, agreement within 3 combined SE — but does
not fix the *step size*. Rather than pick a step after seeing the answer, the
choice is committed here first. This note only constrains; it loosens nothing
and changes no criterion.

## D2.3

* **Primary step: `h = 0.05`.** The D2.3 verdict is read off this step alone.
* **Pre-specified variants (adversarial "finite-difference step variation"):**
  `h ∈ {0.025, 0.10}`. Reported always, pass or fail.
* **Richardson extrapolation** from `h = 0.025` and `h = 0.05` is reported as a
  **truncation diagnostic only**, never as the primary estimate.
* Estimator: `F'(0) ≈ [F(+h) − F(−h)] / (2h)`, with `F(±h)` from **independent**
  seeds, so the SE is the quadrature sum. CRN pairing is not used for the
  primary; the unpaired estimator needs no coupling assumption.
* Comparison target: `1 − Gamma_m` with `Gamma_m` from the frozen convention A,
  its own SE propagated. Combined SE = quadrature of both.
* `N = 500,000` cycles per grid point, as the protocol requires.
* Every `m` in the frozen grid is reported. None may be dropped.

**Anticipated failure mode, recorded in advance so it cannot be reframed
later:** the map is steep at small `m` (`F'(0) ≈ −14.9` at `m = 1`), so the
`O(h²)` truncation error of the central difference may exceed 3 combined SE even
when the identity holds exactly. If the primary step fails while the step
sequence shows the discrepancy shrinking as `h → 0` at the expected `O(h²)`
rate, that is a **finite-difference truncation artifact, not a refutation** —
and it will be reported as a D2.3 failure *with* that diagnosis attached, not
silently converted into a pass.

## D1.4

Runs only if D1.2 passes with `Gamma_SR > 4` (it does: lower bound 17.26).

* Symmetric period-2 candidates satisfy `F(e) = −e`, i.e. a root of
  `H(e) = F(e) + e`, using the odd symmetry `F(−e) = −F(e)`.
* **Coarse scan committed now:** `e ∈ {0.4, 0.6, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4,
  1.8}`, `N = 500,000` each.
* A sign change of `H` is reported as a candidate **only if** both bracketing
  values differ from zero by more than 3 SE; otherwise `NO-CANDIDATE`.
* Refinement by bisection on the bracket, 6 steps, each on its own seed.
* The result is a **Monte Carlo candidate**. It is not a certificate, it does
  not transfer the Stage B certificate to SR, and the words "certified",
  "proved" and "detector-independent" may not be applied to it.
