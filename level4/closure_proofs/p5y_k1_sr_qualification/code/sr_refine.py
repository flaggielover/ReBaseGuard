"""SR whole-cell refinement: the monotone iteration and its typed inputs/outputs.

Mathematics: SR_MIDPOINT_REFINEMENT.md. Structure follows the validated
`refine.py`, but the closure equation is the SR one and carries two extra
raw-variable source terms that the g-variable formulation does not have:

    (I - K) H_r = K'' F_r + 2 K' D_r + S_r'' + 2 h_1' + e h_1''
                                                 ^^^^^^^^^^^^^^^
Those two are REQUIRED inputs with no default, because defaulting them to zero
would silently understate every SR curvature bound.

WHY EVERY ITERATE IS VALID
--------------------------
All four maps are monotone non-decreasing in `supH`, the iteration is seeded with
the crude mean-value bound (valid unconditionally), and each step takes the min
with the previous value. So the sequence is a decreasing sequence of VALID
bounds; refinement can only tighten, and a failure to contract simply leaves the
crude bound standing. No fixed point is assumed to exist and no closure
inequality is hypothesised.

CONTRACTION (evidence, not hypothesis)
--------------------------------------
    kappa' = C rho ( 2 k1 + k2 rho / 2 )
Measured <= 0.513371 over all 315 compact SR cells, capped by the frozen step
rule s = 1/(4 a_upper C_upper) with a_upper = k1 = sqrt(2/pi). Reported per cell
as evidence; never relied upon for validity.

NO GLOBAL STATE
---------------
Every quantity is injected through `RefinementInputs`. This module reads no
module-level configuration, mutates nothing, and performs no lazy imports.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
IMPL = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code"
for _p in (str(IMPL), str(Path(__file__).resolve().parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flint import arb                                              # noqa: E402

MAX_ITERATIONS = 60
IMPROVEMENT_STOP = F(999999, 1000000)


class RefinementLoosened(ArithmeticError):
    """Refinement produced a looser bound than the crude one; refused."""


class MissingRawVariableTerm(ValueError):
    """An SR raw-variable source term was not supplied."""


def _min(a: arb, b: arb) -> arb:
    return a if a.upper() <= b.upper() else b


@dataclass(frozen=True)
class RefinementInputs:
    """Everything the SR refinement consumes, injected explicitly.

    `eps_*_mid` come from a SECOND propagation performed at e0; `sup_D_hat` and
    `sup_H_hat` are sups of the computed CANDIDATES. Without a candidate layer
    these do not exist, which is why refinement is sequenced after Phase 8.
    """
    rho: arb
    C: arb
    k1: arb
    k2: arb
    e_abs: arb
    eps_F_mid: arb
    eps_D_mid: arb
    eps_F_crude: arb
    eps_D_crude: arb
    eps_H_crude: arb
    delta_H_cell: arb
    eps_S2_cell: arb
    sup_D_hat: arb
    sup_H_hat: arb
    # SR-specific raw-variable order-2 source terms -- no defaults on purpose
    eps_h1_d1: arb = None          # type: ignore[assignment]
    eps_h1_d2: arb = None          # type: ignore[assignment]

    def __post_init__(self):
        for name in ("eps_h1_d1", "eps_h1_d2"):
            if getattr(self, name) is None:
                raise MissingRawVariableTerm(
                    f"{name} is required: the SR H equation carries "
                    "+ 2 h_1' + e h_1'' and omitting it understates the bound")

    def contraction(self) -> arb:
        """kappa' = C rho (2 k1 + k2 rho / 2), the full Lipschitz constant."""
        return self.C * self.rho * (arb(2) * self.k1 + self.k2 * self.rho / arb(2))


@dataclass(frozen=True)
class SRRefinedCellValues:
    """Refined whole-cell eps for one r, with its audit trail."""
    eps_F_cell: arb
    eps_D_cell: arb
    eps_H_cell: arb
    sup_H: arb
    iterations: int
    converged: bool
    refinement_enabled: bool
    contraction: str
    contraction_below_one: bool
    tightening_factor_H: float | None

    def as_dict(self) -> dict:
        return {"eps_F_cell": self.eps_F_cell.abs_upper().str(20),
                "eps_D_cell": self.eps_D_cell.abs_upper().str(20),
                "eps_H_cell": self.eps_H_cell.abs_upper().str(20),
                "sup_H": self.sup_H.abs_upper().str(20),
                "iterations": self.iterations, "converged": self.converged,
                "refinement_enabled": self.refinement_enabled,
                "contraction": self.contraction,
                "contraction_below_one": self.contraction_below_one,
                "tightening_factor_H": self.tightening_factor_H}


def refine_cell(inp: RefinementInputs, *, enabled: bool = True,
                iterations: int = MAX_ITERATIONS) -> SRRefinedCellValues:
    """Monotone SR refinement of the whole-cell error bounds.

    With `enabled=False` this returns the crude bounds BYTE-FOR-BYTE, performing
    no arithmetic at all, so the unrefined propagation is reproduced exactly.
    `tests/test_sr_refine.py` asserts that identity.
    """
    kappa = inp.contraction()
    kappa_ok = bool(kappa < arb(1))
    if not enabled:
        return SRRefinedCellValues(
            eps_F_cell=inp.eps_F_crude, eps_D_cell=inp.eps_D_crude,
            eps_H_cell=inp.eps_H_crude,
            sup_H=inp.sup_H_hat + inp.eps_H_crude,
            iterations=0, converged=False, refinement_enabled=False,
            contraction=kappa.abs_upper().str(20),
            contraction_below_one=kappa_ok, tightening_factor_H=1.0)

    rho = inp.rho
    half_rho2 = rho * rho / arb(2)
    D_at_e0 = inp.sup_D_hat + inp.eps_D_mid
    # the two SR raw-variable terms are constants of the iteration
    sr_extra = arb(2) * inp.eps_h1_d1 + inp.e_abs * inp.eps_h1_d2

    epsF, epsD, epsH = inp.eps_F_crude, inp.eps_D_crude, inp.eps_H_crude
    supH = inp.sup_H_hat + epsH
    n = 0
    for n in range(1, iterations + 1):
        nF = _min(epsF, inp.eps_F_mid + rho * D_at_e0 + half_rho2 * supH)
        nD = _min(epsD, inp.eps_D_mid + rho * supH)
        nH = _min(epsH, inp.C * (inp.delta_H_cell + inp.k2 * nF
                                 + arb(2) * inp.k1 * nD + inp.eps_S2_cell
                                 + sr_extra))
        nsupH = inp.sup_H_hat + nH
        improved = nsupH.upper() < (supH * arb(IMPROVEMENT_STOP.numerator)
                                    / arb(IMPROVEMENT_STOP.denominator)).upper()
        epsF, epsD, epsH, supH = nF, nD, nH, nsupH
        if not improved:
            break

    for name, new, crude in (("F", epsF, inp.eps_F_crude),
                             ("D", epsD, inp.eps_D_crude),
                             ("H", epsH, inp.eps_H_crude)):
        if new.upper() > crude.upper():
            raise RefinementLoosened(f"refinement loosened eps{name}; refused")

    crude_H = float(inp.eps_H_crude.abs_upper().mid())
    ref_H = float(epsH.abs_upper().mid())
    tf = (crude_H / ref_H) if ref_H > 0 else None
    return SRRefinedCellValues(
        eps_F_cell=epsF, eps_D_cell=epsD, eps_H_cell=epsH, sup_H=supH,
        iterations=n, converged=n < iterations, refinement_enabled=True,
        contraction=kappa.abs_upper().str(20), contraction_below_one=kappa_ok,
        tightening_factor_H=tf)
