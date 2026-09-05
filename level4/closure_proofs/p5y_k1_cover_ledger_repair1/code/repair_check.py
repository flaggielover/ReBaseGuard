"""Accounting validator: the closed-form S0 remainder must be charged EXACTLY once.

The frozen ERROR_ALGEBRA permits representation A (residual against the fixed
candidate, plus a separate epsS) or representation B (complete residual against
the true source, epsS forced to zero) -- never a mixture, and never neither.

This module makes "exactly once" a checkable invariant rather than a claim. For
each derivative order k it locates the S0 remainder in the two places it could
appear and counts them:

    local     = truncation_allowance(F_0/dF_0/H_0) - corrected_extra
    dependency = delta(Sclosed_k), the epsS node the resolvent consumes

`corrected_extra` is the kernel-series truncation alone. A charge counts as
present when it is at least half the remainder, which is unambiguous: the two
candidate values are 0 and `reward_allow[k]`, and the arithmetic that produces
them is outward-rounded by at most a few ulps at 256 bits.
"""
from __future__ import annotations

from fractions import Fraction as F

import prior                                                    # noqa: F401

from intervals import mag_fraction, tight_upper                 # noqa: E402

from repair_layer2 import DUPLICATE_SITES, corrected_extra      # noqa: E402

ORDERS = {"F_0": 0, "dF_0": 1, "H_0": 2}


def charge_positions(*, truncation_allowance: F, corrected: F,
                     dependency: F, reward: F) -> dict:
    """Where the S0 remainder is charged, and how many times."""
    if reward <= 0:
        raise ValueError("reward_allow must be positive to be locatable")
    local = truncation_allowance - corrected
    if local < 0:
        local = F(0)
    half = reward / 2
    in_local = local >= half
    in_dependency = dependency >= half
    return {
        "local_residual_charge": str(local),
        "dependency_charge": str(dependency),
        "reward_allow": str(reward),
        "in_local_residual": in_local,
        "in_dependency_graph": in_dependency,
        "charge_count": int(in_local) + int(in_dependency),
    }


def audit_cert(cert, residuals: dict) -> dict:
    """Run the invariant over a real certifier's residual set."""
    out = {}
    for name in DUPLICATE_SITES:
        k = ORDERS[name]
        entry = residuals[name]
        out[name] = charge_positions(
            truncation_allowance=mag_fraction(entry["truncation_allowance"]),
            corrected=mag_fraction(tight_upper(corrected_extra(cert, name))),
            dependency=mag_fraction(residuals[f"Sclosed_{k}"]["delta_mid"]),
            reward=mag_fraction(tight_upper(cert.reward_allow[k])),
        )
    out["all_charged_exactly_once"] = all(
        out[n]["charge_count"] == 1 for n in DUPLICATE_SITES)
    out["representation"] = (
        "A: residual against fixed candidate + separate epsS"
        if all(out[n]["in_dependency_graph"] and not out[n]["in_local_residual"]
               for n in DUPLICATE_SITES) else "MIXED_OR_MISSING")
    return out


class ChargeAccountingError(RuntimeError):
    """The S0 remainder is charged zero times or more than once."""


def require_single_charge(cert, residuals: dict) -> dict:
    report = audit_cert(cert, residuals)
    for name in DUPLICATE_SITES:
        n = report[name]["charge_count"]
        if n != 1:
            raise ChargeAccountingError(
                f"{name}: S0 remainder charged {n} times (must be exactly 1); "
                f"local={report[name]['local_residual_charge']} "
                f"dependency={report[name]['dependency_charge']}")
    return report
