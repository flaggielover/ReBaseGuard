"""Monotone refinement of the whole-cell F / D / H error bounds.

WHY THIS EXISTS
---------------
The plain mean-value extension `delta_cell = delta_mid + rho * Env` is rigorous
but, fed through the resolvent chain three times, it is enormously lossy: each
level multiplies by `C * k1`, so a first-level slack of `rho * Env_F` reappears
at the curvature level multiplied by roughly `(C k1)^2`. On CUSUM cell 221 the
unrefined chain gives `M_R2 = 6.2e4` and `B_cover = 143% of .050` -- a FAIL that
is an artefact of the bound, not of the mathematics.

WHAT IS REFINED
---------------
The chain is re-derived using Taylor-in-`e` rather than a single mean value.
With `s = e - e0`, `|s| <= rho`, and the integral remainder form:

    F(x,e) = F(x,e0) + s D(x,e0) + int_{e0}^{e} (e-t) F''(x,t) dt
 => epsF_cell <= epsF_mid + rho * ||D(.,e0)|| + (rho^2/2) * supH
    epsD_cell <= epsD_mid + rho * supH                         (mean value on D)
    epsH_cell  = C (deltaH_cell + k2 epsF_cell + 2 k1 epsD_cell + epsS2_cell)
    supH      <= sup|Hhat| + epsH_cell
    ||D(.,e0)|| <= sup|Dhat| + epsD_mid

WHY EACH ITERATE IS RIGOROUS
----------------------------
All four maps are monotone NON-DECREASING in `supH`. So if `supH` is a valid
bound on `sup_cell ||F''||`, then every quantity computed from it is valid, and
in particular the new `supH` is valid too. The iteration is therefore a
decreasing sequence of VALID bounds, and it is seeded with the crude mean-value
chain, which is valid unconditionally. Each step also takes `min` with the crude
value, so refinement can only tighten.

No fixed point is asserted to exist and no closure inequality is assumed. If the
iteration fails to contract, the crude bound simply stands. In particular this
does NOT invoke the old R1 bootstrap condition, which the frozen CHECKPOINT
explicitly declines to use; the observed contraction factor is reported per cell
as evidence, not relied on as a hypothesis.
"""
from __future__ import annotations

from fractions import Fraction as F

from flint import arb

import propagate
from intervals import exact, mag_fraction, tight_upper

MAX_ITERATIONS = 60


def _min(a: arb, b: arb) -> arb:
    return a if a.upper() <= b.upper() else b


def refine(cert, mid, crude, *, rs=range(5),
           iterations: int = MAX_ITERATIONS) -> dict:
    """Refined whole-cell eps for F_r, D_r, H_r, plus a per-r audit trail."""
    rho = exact(cert.rho)
    half_rho2 = rho * rho / arb(2)
    C = exact(cert.C)
    k1, k2 = cert.norms["k"][1], cert.norms["k"][2]
    out, audit = {}, {}

    for r in rs:
        epsF_mid = mid.get(f"F:{r}")
        epsD_mid = mid.get(f"D:{r}")
        epsF_crude = crude.get(f"F:{r}")
        epsD_crude = crude.get(f"D:{r}")
        epsH_crude = crude.get(f"H:{r}")
        deltaH_cell = cert.residuals[f"H_{r}"]["delta_cell"]
        epsS2 = crude.get(propagate._source_node(r, 2))
        supD = cert.sup["D", r, 0]
        supH_hat = cert.sup["H", r, 0]
        D_at_e0 = supD + epsD_mid

        epsF, epsD, epsH = epsF_crude, epsD_crude, epsH_crude
        supH = tight_upper(supH_hat + epsH_crude)
        trail = []
        for step in range(iterations):
            nF = _min(epsF, tight_upper(epsF_mid + rho * D_at_e0 + half_rho2 * supH))
            nD = _min(epsD, tight_upper(epsD_mid + rho * supH))
            nH = _min(epsH, tight_upper(
                C * (deltaH_cell + k2 * nF + arb(2) * k1 * nD + epsS2)))
            nsupH = tight_upper(supH_hat + nH)
            trail.append({"step": step, "supH": str(mag_fraction(nsupH)),
                          "epsF_cell": str(mag_fraction(nF)),
                          "epsD_cell": str(mag_fraction(nD)),
                          "epsH_cell": str(mag_fraction(nH))})
            # Stop once another sweep buys less than one part in 10^6. The
            # sequence is geometric, so the remaining gap is negligible, and
            # every iterate already IS a valid bound.
            improved = nsupH.upper() < (supH * exact(F(999999, 1000000))).upper()
            epsF, epsD, epsH, supH = nF, nD, nH, nsupH
            if not improved:
                break

        # Reported only as evidence; the refinement never assumes it is < 1.
        contraction = F(mag_fraction(rho)) * F(mag_fraction(C)) * 2 * F(mag_fraction(k1))
        out[f"F:{r}"] = epsF
        out[f"D:{r}"] = epsD
        out[f"H:{r}"] = epsH
        audit[r] = {
            "iterations": len(trail),
            "converged": len(trail) < iterations,
            "observed_contraction_factor_rho_C_2k1": str(contraction),
            "contraction_below_one": contraction < 1,
            "crude": {"epsF_cell": str(mag_fraction(epsF_crude)),
                      "epsD_cell": str(mag_fraction(epsD_crude)),
                      "epsH_cell": str(mag_fraction(epsH_crude))},
            "refined": {"epsF_cell": str(mag_fraction(epsF)),
                        "epsD_cell": str(mag_fraction(epsD)),
                        "epsH_cell": str(mag_fraction(epsH))},
            "tightening_factor_H": (float(F(mag_fraction(epsH_crude))
                                          / F(mag_fraction(epsH)))
                                    if F(mag_fraction(epsH)) > 0 else None),
            "trail": trail[:4] + (["..."] if len(trail) > 8 else []) + trail[-4:]
            if len(trail) > 8 else trail,
        }
        for key in (f"F:{r}", f"D:{r}", f"H:{r}"):
            if out[key].upper() > crude.get(key).upper():
                raise ArithmeticError(
                    f"refinement produced a LOOSER bound for {key}; refuse")
    return {"eps": out, "audit": audit}
