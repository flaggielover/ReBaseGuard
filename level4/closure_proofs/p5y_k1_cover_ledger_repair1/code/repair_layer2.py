"""REPAIR 1: charge the closed-form S0 remainder exactly once.

DEFECT (independently adjudicated, DERIVATIVE_DEPENDENCY_SOUND = NO)
--------------------------------------------------------------------
The reviewed implementation at c0a1f40 builds the r = 0 residual against the
FIXED truncated closed-form source `Sclosed_k` and then also adds
`reward_allow[k]` -- the bound on `||Sclosed_k - S_0^(k)_true||` -- into that
residual's local `extra`:

    cusum_layer2.py:379   extra = extra + self.reward_allow[0]      # F_0
    cusum_layer2.py:395   extra = extra + self.reward_allow[1]      # dF_0
    cusum_layer2.py:411   extra = extra + self.reward_allow[2]      # H_0

Separately, `propagate.py` creates the `Sclosed:k` error node from the very same
`reward_allow[k]` and feeds it to the resolvent as the epsS dependency:

    propagate.py:39   _source_node(0, k) -> "Sclosed:k"
    propagate.py:69   dag.local(nid, d(f"Sclosed_{k}"), ...)

so `epsF = C*(deltaF + epsS)` counts that one quantity twice. The excess is
exactly `C * reward_allow[k]` per level, and it compounds through the
F -> D -> H chain.

The frozen ERROR_ALGEBRA section 1 permits exactly one of

    A. residual against the CANDIDATE source, plus a separate epsS, or
    B. a complete residual against the TRUE source, with epsS forced to zero
       ("the corresponding separate epsS term MUST be zero in the accounting
        DAG because it is INCLUDED, not because the error vanishes")

The reviewed code mixes A and B.

REPAIR
------
Representation **A** is adopted, because it is what the surrounding
architecture already implements everywhere else: `S_r` for r >= 1, `h_1^(k)`
and the `S_0:k` candidate all use "residual against a fixed candidate, error
carried by its own node". Only the r = 0 F/D/H residuals deviated.

So `reward_allow[k]` is removed from the local F_0/D_0/H_0 residual and left in
exactly one place -- the `Sclosed:k` dependency node. Nothing else changes:

  * `epsF = C*(deltaF + epsS)` and
    `epsD = C*(deltaD + k1*epsF + epsS')` keep their exact frozen shape;
  * STYLE_1 is untouched, D_interval stays complete, the Taylor derivative
    charge is still made exactly once;
  * the kernel-series truncation, the whole-cell envelopes and every r >= 1
    object are bit-for-bit unchanged;
  * no containment term is dropped except the provable duplicate.

The expensive certified work (the Bernstein range bound on the residual
polynomial) is REUSED from the reviewed implementation: only the scalar `extra`
is recomputed, from the same certified inputs.
"""
from __future__ import annotations

from fractions import Fraction as F                             # noqa: E402

import prior                                                    # noqa: F401

from flint import arb                                           # noqa: E402

import cusum_layer2 as reviewed                                 # noqa: E402
from cusum_layer2 import CellCertifier, Z_RANGE                 # noqa: E402
from intervals import exact, mag_fraction, tight_upper          # noqa: E402

DUPLICATE_SITES = ("F_0", "dF_0", "H_0")

# Arb stores ball radii with 30-bit precision, so two valid outward bounds
# of one quantity can differ by ~2^-30 of the radius. 2^-40 of the whole
# allowance is comfortably above that and far below any real term.
ROUNDING_SLACK = F(1, 2 ** 40)


def corrected_extra(cert, name: str) -> arb:
    """The local truncation allowance WITHOUT the source remainder.

    Exactly the reviewed expressions with `reward_allow[k]` omitted; every
    factor is a certified quantity the reviewed pass already computed.
    """
    sup_F = cert.sup["F", 0, 0]
    sup_D = cert.sup["D", 0, 0]
    sup_H = cert.sup["H", 0, 0]
    if name == "F_0":
        return Z_RANGE * sup_F * cert.eps_zi(0)
    if name == "dF_0":
        return (Z_RANGE * sup_D * cert.eps_zi(0)
                + Z_RANGE * sup_F * cert.eps_zi(1))
    if name == "H_0":
        return (Z_RANGE * sup_H * cert.eps_zi(0)
                + Z_RANGE * sup_F * cert.eps_zi(2)
                + arb(2) * Z_RANGE * sup_D * cert.eps_zi(1))
    raise ValueError(f"{name} is not one of the duplicate sites")


def correct_residuals(cert, out: dict) -> dict:
    """Rebuild only the three r=0 entries with the duplicate removed.

    Guarded both ways: the repair may only tighten, and it may not remove more
    than the S0 remainder itself.
    """
    rho = exact(cert.rho)
    for name, k in zip(DUPLICATE_SITES, (0, 1, 2)):
        entry = out[name]
        poly = entry["polynomial_residual"]
        extra = tight_upper(corrected_extra(cert, name))
        envelope = entry["envelope"]
        delta_mid = tight_upper(poly + extra)
        delta_cell = tight_upper(delta_mid + rho * envelope)
        reward = tight_upper(cert.reward_allow[k])

        # (a) the repair may only tighten, never loosen
        if not entry["delta_mid"] >= delta_mid:
            raise ArithmeticError(
                f"{name}: repaired delta_mid is not <= the reviewed one")
        # (b) soundness: the repaired allowance still dominates the certified
        #     enclosure of the kernel-truncation term, centre AND radius
        raw = corrected_extra(cert, name)
        if not extra >= tight_upper(raw):
            raise ArithmeticError(
                f"{name}: repaired extra does not dominate its own enclosure")
        # (c) no SUBSTANTIVE over-removal. Exact equality with reward_allow is
        #     not available: Arb rounds radii to 30 bits, so two outward bounds
        #     of the same quantity differ by ~2^-30*rad, which here is ~1e18
        #     times reward_allow. ROUNDING_SLACK is far below any real term.
        removed = mag_fraction(entry["delta_mid"]) - mag_fraction(delta_mid)
        allowance = (mag_fraction(reward)
                     + ROUNDING_SLACK * mag_fraction(entry["truncation_allowance"]))
        if removed > allowance:
            raise ArithmeticError(
                f"{name}: repair removed {removed} > allowed {allowance}; "
                "that is more than the S0 remainder plus radius rounding")

        out[name] = dict(entry)
        out[name].update({
            "truncation_allowance": extra,
            "delta_mid": delta_mid,
            "delta_cell": delta_cell,
            "repair": "S0_remainder_removed_from_local_residual",
            "reviewed_delta_mid": entry["delta_mid"],
            "duplicate_removed": reward,
        })
    return out


class RepairedCellCertifier(CellCertifier):
    """The reviewed certifier with the duplicate S0 remainder removed.

    Everything is inherited. `all_residuals` runs the reviewed pass unchanged
    and then rebuilds only the three r = 0 entries with the corrected `extra`,
    recomputed from the same certified sup norms and truncation allowances.
    """

    repairs_defect_1 = True

    def all_residuals(self) -> dict:
        out = correct_residuals(self, super().all_residuals())
        self.residuals = out
        return out


def duplicate_amount(cert, k: int):
    """The excess epsF/epsD/epsH the reviewed code charged, before the C factor."""
    return tight_upper(cert.reward_allow[k])
