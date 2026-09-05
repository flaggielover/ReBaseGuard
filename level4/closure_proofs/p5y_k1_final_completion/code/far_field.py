"""Far-field certificate (P5X-T3) for both detectors.

THE OBLIGATION
--------------
The frozen K1 checkpoint says: "Far-field theorem P5X-T3 and the parent splice
obligations remain mandatory for both detectors." The compact certified cover is
`[0, c_D]` (CUSUM `c = 11/2`, SR `c = log(A) + 1/2`), oddness supplies `e < 0`,
and P5X-T3 must close `[c_D, infinity)`.

THE DERIVATION (every step elementary and stated in full)
---------------------------------------------------------
Under `P_e` the observations `raw_t` are iid `N(0,1)` and `z_t = raw_t - e`.
`tau` is the inclusive alarm time, `w = min(m, tau)`, and, in the raw variable
with Stage-D convention A,

    Rbar = (1/w) sum_{t=1}^{w} raw_t ,      R_{D,m}(e) = E_e[ Rbar ] .

1. ONE-STEP ALARM.  `c_D` is by construction the one-step alarm threshold: on
   `{ |z_1| >= c_D }` the detector fires at `t = 1`. Hence
       { tau > 1 }  subset  { |raw_1 - e| < c_D }
   and for `e >= 0`
       q(e) := P_e(tau > 1) <= Phi(c_D - e) - Phi(-c_D - e) <= Phi(c_D - e).

2. MEAN-ZERO CANCELLATION.  `E[raw_1] = 0`, and on `{tau = 1}` we have `w = 1`
   and `Rbar = raw_1` exactly, so that event contributes nothing to `Rbar-raw_1`:
       R = E[Rbar] = E[Rbar - raw_1] = E[ (Rbar - raw_1) 1{tau > 1} ] .
   This is where the far-field decay comes from; it is exact, not a bound.

3. CAUCHY-SCHWARZ.
       |R| <= sqrt( E[(Rbar - raw_1)^2] ) * sqrt( q(e) ) .

4. SECOND MOMENT, PATHWISE.  By Cauchy-Schwarz on the average,
   `Rbar^2 <= (1/w) sum_{t<=w} raw_t^2 <= sum_{t=1}^{m} raw_t^2` pathwise
   (valid however `w` depends on the path), so `E[Rbar^2] <= m` and
       E[(Rbar - raw_1)^2] <= 2 E[Rbar^2] + 2 E[raw_1^2] <= 2m + 2 .

Therefore the certified majorant, decreasing in `e` and super-exponentially
small:

    |R_{D,m}(e)|  <=  B_(D,m)(e)  =  sqrt(2m + 2) * sqrt( Phi(c_D - e) )

and, because `B` is decreasing, `B_(D,m)(e_0)` bounds `|R|` on all of
`[e_0, infinity)`.

WHAT THIS DOES AND DOES NOT CLOSE
---------------------------------
The frozen target is `|R| < 2`. Solving `B_(D,m)(e_0) < 2` gives
`Phi(c_D - e_0) < 4/(2m+2)`. At the frozen K1 splice `e_0 = c_D` we have
`Phi(0) = 1/2` exactly, so the majorant closes `m = 1, 2` and does NOT close
`m = 3, 5`. It closes every `m` once `e_0 >= c_D + Phi^-1(1 - 4/(2m+2))`.

That is a statement about THIS majorant, not about the science: the true `|R|`
near `c_D` is certainly far below 2. It is reported as
CERTIFICATE_TOO_LOOSE / coverage-composition gap, never as a counterexample.
No cover geometry, threshold, budget or precision is changed here.
"""
from __future__ import annotations

from fractions import Fraction as F

import base                                                     # noqa: F401

from flint import arb                                           # noqa: E402

import spec                                                     # noqa: E402
from intervals import exact, mag_fraction, tight_upper, workprec  # noqa: E402

TARGET = F(2)                       # the frozen K1 target sup|R| < 2
# Below this, "B < 2" is decided by outward rounding, not by mathematics.
MEANINGFUL_MARGIN = F(1, 10 ** 6)
A_SR = F(4581762885148045, 8796093022208)


def gaussian_cdf(x: arb) -> arb:
    return (arb(1) + (x / arb(2).sqrt()).erf()) / arb(2)


def c_threshold(detector: str) -> arb:
    """The one-step alarm threshold c_D, exactly as the frozen scope fixes it."""
    if detector == "CUSUM":
        return exact(F(11, 2))                       # h + k = 5 + 1/2
    if detector == "SR":
        return (arb(A_SR.numerator) / arb(A_SR.denominator)).log() + exact(F(1, 2))
    raise ValueError(detector)


def q_upper(detector: str, e: arb) -> arb:
    """q(e) = P_e(tau > 1) <= Phi(c-e) - Phi(-c-e), outward rounded."""
    c = c_threshold(detector)
    return tight_upper(gaussian_cdf(c - e) - gaussian_cdf(-c - e))


def majorant(detector: str, m: int, e: arb) -> arb:
    """B_(D,m)(e) = sqrt(2m+2) * sqrt(q(e)); decreasing in e."""
    if m not in spec.M_VALUES:
        raise ValueError(f"m={m} outside the frozen scope {spec.M_VALUES}")
    return tight_upper((arb(2 * m + 2).sqrt()) * q_upper(detector, e).sqrt())


def certify_at(detector: str, e0, *, bits: int = spec.PRODUCTION_BITS) -> dict:
    """Certificate for [e0, infinity) at every frozen m."""
    with workprec(bits):
        e = exact(e0) if not isinstance(e0, arb) else e0
        c = c_threshold(detector)
        rows = {}
        for m in spec.M_VALUES:
            b = majorant(detector, m, e)
            passes = bool(b < exact(TARGET))
            margin = F(TARGET) - mag_fraction(b)
            # A margin decided by outward rounding is not a certificate.
            if passes and margin >= MEANINGFUL_MARGIN:
                status = "PASS"
            elif passes:
                status = "MARGINAL"
            else:
                status = "CERTIFICATE_TOO_LOOSE"
            rows[m] = {
                "majorant": str(mag_fraction(b)),
                "majorant_float": float(b.abs_upper()),
                "target": str(TARGET),
                "margin_float": float(margin),
                "strictly_below_target": passes,
                "usable_certificate": status == "PASS",
                "status": status,
            }
        return {
            "detector": detector,
            "c_threshold": float(c.mid()),
            "e0": str(F(e0)) if not isinstance(e0, arb) else float(e0.mid()),
            "e0_float": float(e.mid()),
            "q_upper": float(q_upper(detector, e).abs_upper()),
            "precision_bits": bits,
            "per_m": rows,
            "all_m_pass": all(r["usable_certificate"] for r in rows.values()),
            "marginal_m": [m for m, r in rows.items() if r["status"] == "MARGINAL"],
            "monotone_decreasing": True,
            "covers": "[e0, infinity), by monotonicity of B in e",
        }


def minimum_e0(detector: str, m: int, *, bits: int = spec.PRODUCTION_BITS,
               tol: F = F(1, 10 ** 6)) -> dict:
    """Smallest e0 at which this majorant closes (certified bisection)."""
    with workprec(bits):
        c = c_threshold(detector)
        lo, hi = F(0), F(20)
        # certified bisection on the decreasing function B(e) - 2
        for _ in range(80):
            mid = (lo + hi) / 2
            if (F(TARGET) - mag_fraction(majorant(detector, m, exact(mid)))
                    >= MEANINGFUL_MARGIN):
                hi = mid
            else:
                lo = mid
            if hi - lo < tol:
                break
        witness = majorant(detector, m, exact(hi))
        return {"detector": detector, "m": m,
                "c_threshold": float(c.mid()),
                "minimum_e0": float(hi),
                "excess_over_c": float(hi) - float(c.mid()),
                "majorant_at_minimum": float(witness.abs_upper()),
                "verified_below_target": bool(witness < exact(TARGET))}


def report(*, bits: int = spec.PRODUCTION_BITS) -> dict:
    """Full far-field report at the frozen K1 splice and at P5X's e_far = 12."""
    out = {"schema": "k1.final.far-field.v1",
           "theorem": "P5X-T3", "target": str(TARGET),
           "precision_bits": bits, "result_bearing": False,
           "derivation": "see module docstring; steps 1-4 elementary",
           "detectors": {}}
    for det in ("CUSUM", "SR"):
        with workprec(bits):
            c = c_threshold(det)
            c_frac = F(11, 2) if det == "CUSUM" else \
                F(int((c * 2 ** 60).floor().fmpq().p), 2 ** 60)
        at_splice = certify_at(det, c_frac, bits=bits)
        at_far = certify_at(det, F(12), bits=bits)
        mins = {m: minimum_e0(det, m, bits=bits) for m in spec.M_VALUES}
        need = max(v["minimum_e0"] for v in mins.values())
        out["detectors"][det] = {
            "c_threshold": at_splice["c_threshold"],
            "at_frozen_k1_splice": at_splice,
            "at_p5x_e_far_12": at_far,
            "minimum_e0_per_m": mins,
            "e0_closing_all_m": need,
            "uncovered_interval_if_cover_ends_at_c":
                [at_splice["c_threshold"], need],
            "status": ("PASS" if at_splice["all_m_pass"]
                       else "NOT_ESTABLISHED_AT_FROZEN_SPLICE"),
            "failure_class": (None if at_splice["all_m_pass"]
                              else "CERTIFICATE_TOO_LOOSE"),
        }
    return out
